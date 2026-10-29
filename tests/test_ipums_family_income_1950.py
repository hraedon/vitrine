"""Synthetic tests for the aggregate-only 1950 IPUMS curator."""

from __future__ import annotations

import csv
import hashlib
import io
import json
import xml.etree.ElementTree as ET
from decimal import Decimal
from pathlib import Path

import ipums_family_income_1950 as curator
import pytest


def ddi() -> bytes:
    root = ET.Element("codeBook")
    ET.SubElement(root, "timePrd", date="1950")
    ET.SubElement(
        root, "notes"
    ).text = "Additional notes on a sample that is part of this study:  1950 1%"
    ET.SubElement(root, "fileName").text = "usa_00042.dat"
    for name in sorted(curator.REQUIRED):
        var = ET.SubElement(root, "var", name=name, dcml="2" if name == "SLWT" else "0")
        categories = {
            "SAMPLE": {195001: "1950 1%"},
            "METRO": curator.METRO_CODES,
            "GQ": curator.GQ_CODES,
            "RELATE": {1: curator.HEAD_LABEL},
        }.get(name, {})
        for code, label in categories.items():
            cat = ET.SubElement(var, "catgry")
            ET.SubElement(cat, "catValu").text = str(code)
            ET.SubElement(cat, "labl").text = label
        if name == "FTOTINC":
            ET.SubElement(var, "codInstr").text = (
                "-000001 = Net loss (1950) 0000000 = No income "
                "9999998 = Not ascertained (1950) 9999999 = N/A"
            )
    return ET.tostring(root, encoding="utf-8")


def row(serial: int, *, metro: int = 1, income: int = 2000, weight: str = "330.00", **kw):
    result = {
        "YEAR": "1950",
        "SAMPLE": "195001",
        "SERIAL": str(serial),
        "PERNUM": "1",
        "GQ": "1",
        "FAMUNIT": "1",
        "FAMSIZE": "4",
        "RELATE": "1",
        "METRO": str(metro),
        "FTOTINC": str(income),
        "SLWT": weight,
    }
    result.update({k: str(v) for k, v in kw.items()})
    return result


def reader(rows, *, header=None):
    names = sorted(curator.REQUIRED) if header is None else header
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=names, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    stream.seek(0)
    return csv.DictReader(stream, strict=True)


def rows_for_release():
    # Each released count meets the disclosure threshold. Data are synthetic.
    rows = []
    for metro in (1, 2, 3, 4, 5):
        rows += [row(len(rows) + i + 1, metro=metro) for i in range(30)]
    rows += [row(len(rows) + i + 1, weight="0", income=9999999) for i in range(30)]
    rows += [row(len(rows) + i + 1, metro=1, income=9999998) for i in range(30)]
    rows += [row(len(rows) + i + 1, metro=1, income=9999999) for i in range(30)]
    companions = []
    for head in rows:
        for pernum in (2, 3, 4):
            companions.append({**head, "PERNUM": str(pernum), "RELATE": "2"})
    return rows + companions


def test_ddi_requires_actual_sample_variable_metadata_and_codes() -> None:
    blob = ddi()
    result = curator.validate_ddi(blob)
    assert result["extract_id"] == "usa_00042"
    assert result["slwt_decimals"] == 2
    with pytest.raises(curator.ReviewError, match="metropolitan"):
        curator.validate_ddi(blob.replace(b"Not in metropolitan area", b"Central city"))
    with pytest.raises(curator.ReviewError, match="sample"):
        curator.validate_ddi(blob.replace(b"1950 1%", b"1950 full count"))
    with pytest.raises(curator.ReviewError, match="income special"):
        curator.validate_ddi(blob.replace(b"9999998", b"9999997"))
    with pytest.raises(curator.ReviewError, match="required"):
        curator.validate_ddi(blob.replace(b'name="SLWT"', b'name="OTHER"'))


def test_weighted_inverse_cdf_ties_net_loss_and_decimal_weights() -> None:
    data = [
        curator.Observation(-1, Decimal("330.00")),
        curator.Observation(1000, Decimal("330.00")),
    ]
    median = curator.weighted_median(data)
    assert median["median_code"] == -1
    assert median["bottom_code_is_net_loss"] is True
    assert median["half_rank_exact_boundary"] is True
    assert median["weight_at_or_below"] == "330.00"
    result = curator.weighted_median([curator.Observation(10000, Decimal("330"))])
    assert result["top_code_reached"] is True
    assert curator._weight("330.00") == Decimal("330.00")
    with pytest.raises(curator.ReviewError):
        curator._weight("1.234")


def test_selection_geography_and_missingness_are_aggregate_only() -> None:
    rows = rows_for_release()
    rows += [
        row(9000, metro=3, FAMUNIT=2),
        row(9001, metro=3, GQ=3),
        row(9002, metro=3, FAMSIZE=1),
        row(9003, metro=3, RELATE=2),
    ]
    result = curator.aggregate(reader(rows), tuple(sorted(curator.REQUIRED)))
    assert result["groups"]["metro"]["unweighted_count"] == 90
    assert result["groups"]["nonmetro"]["unweighted_count"] == 30
    assert result["groups"]["outside_central_identified"]["unweighted_count"] == 30
    assert result["counts"]["geography_metro_indeterminate"] == 30
    assert result["counts"]["income_not_ascertained"] == 30
    assert result["counts"]["income_not_applicable"] == 30
    assert result["counts"]["not_sample_line"] == 30
    assert result["groups"]["nonmetro"]["total_weight"] == "9900.00"
    assert "9000" not in json.dumps(result)


def test_duplicate_head_records_and_wrong_sample_fail_closed() -> None:
    rows = rows_for_release()
    duplicate = row(1, PERNUM=5)
    # Add a replacement family so the nonmetro release group remains large enough.
    replacement = [row(9000, PERNUM=n, RELATE=1 if n == 1 else 2) for n in (1, 2, 3, 4)]
    result = curator.aggregate(
        reader([*rows, duplicate, *replacement]), tuple(sorted(curator.REQUIRED))
    )
    assert result["groups"]["nonmetro"]["unweighted_count"] == 30
    assert result["counts"]["ambiguous_household_heads"] is None
    assert "ambiguous_household_heads" in result["suppressed_counts"]
    with pytest.raises(curator.ReviewError, match="duplicated person"):
        curator.aggregate(reader([*rows, rows[0]]), tuple(sorted(curator.REQUIRED)))
    bad = rows_for_release()
    bad[0]["SAMPLE"] = "195002"
    with pytest.raises(curator.ReviewError, match="1950 1%"):
        curator.aggregate(reader(bad), tuple(sorted(curator.REQUIRED)))
    with pytest.raises(curator.ReviewError, match="disclosure"):
        curator.aggregate(reader(rows[:3]), tuple(sorted(curator.REQUIRED)))


def test_full_synthetic_extract_checks_doc_pins_and_outputs_no_rows(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    csv_path = tmp_path / "usa_00042.csv"
    names = sorted(curator.REQUIRED)
    with csv_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=names)
        writer.writeheader()
        writer.writerows(rows_for_release())
    ddi_path = tmp_path / "usa_00042.xml"
    ddi_path.write_bytes(ddi())
    docs = {key: tmp_path / f"{key}.html" for key in curator.DOC_PINS}
    for key, path in docs.items():
        path.write_bytes((key + " test documentation").encode())
    monkeypatch.setattr(
        curator,
        "DOC_PINS",
        {key: hashlib.sha256(path.read_bytes()).hexdigest() for key, path in docs.items()},
    )
    result = curator.run(csv_path, ddi_path, docs)
    assert result["income_reference_year"] == 1949
    assert result["extract_id"] == "usa_00042"
    assert "SERIAL" not in json.dumps(result)
    assert result["documentation_sha256"] == curator.DOC_PINS
    docs["slwt"].write_text("changed", encoding="utf-8")
    with pytest.raises(curator.ReviewError, match="documentation pin"):
        curator.run(csv_path, ddi_path, docs)


def test_gzipped_synthetic_source_has_same_aggregates(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    import gzip

    plain = tmp_path / "usa_00042.csv"
    with plain.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=sorted(curator.REQUIRED))
        writer.writeheader()
        writer.writerows(rows_for_release())
    compressed = tmp_path / "usa_00042.csv.gz"
    compressed.write_bytes(gzip.compress(plain.read_bytes(), mtime=0))
    metadata = tmp_path / "usa_00042.xml"
    metadata.write_bytes(ddi())
    docs = {key: tmp_path / f"{key}.html" for key in curator.DOC_PINS}
    for key, path in docs.items():
        path.write_bytes(key.encode())
    monkeypatch.setattr(
        curator,
        "DOC_PINS",
        {key: hashlib.sha256(path.read_bytes()).hexdigest() for key, path in docs.items()},
    )
    uncompressed_result = curator.run(plain, metadata, docs)
    compressed_result = curator.run(compressed, metadata, docs)
    assert compressed_result["groups"] == uncompressed_result["groups"]
    assert compressed_result["data_sha256"] == hashlib.sha256(compressed.read_bytes()).hexdigest()
    assert compressed_result["data_sha256"] != uncompressed_result["data_sha256"]


def test_family_roster_and_rare_ancillary_cells_are_guarded() -> None:
    rows = rows_for_release()
    # One reported four-person family has only three primary-unit records.
    rows = [r for r in rows if not (r["SERIAL"] == "1" and r["PERNUM"] == "4")]
    # A quasi-household cannot enter the period household universe.
    for r in rows:
        if r["SERIAL"] == "2":
            r["GQ"] = "2"
    # Add two matching nonmetro units to keep headline counts above threshold.
    for serial in (10001, 10002):
        for pernum in (1, 2, 3, 4):
            rows.append(row(serial, PERNUM=pernum, RELATE=1 if pernum == 1 else 2))
    result = curator.aggregate(reader(rows), tuple(sorted(curator.REQUIRED)))
    assert result["groups"]["nonmetro"]["unweighted_count"] == 30
    assert result["counts"]["primary_unit_size_mismatch"] is None
    assert "primary_unit_size_mismatch" in result["suppressed_counts"]
    assert result["counts"]["top_code"] == 0
