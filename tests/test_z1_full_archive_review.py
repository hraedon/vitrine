"""Verify Federal Reserve CSV row guards and complete selected balance sheets."""

import csv
import hashlib
import io
import json
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

import pytest
import z1_full_archive_review as review


def row(code: str, date: str, value: str) -> list[str]:
    return [
        "Z1/Z1/" + code,
        "Households and nonprofit organizations; selected account",
        "Long description, with comma",
        "United States / United States Dollar",
        "Quarterly",
        "instrument",
        "prefix",
        "Households and nonprofit organizations",
        "type",
        "Currency",
        "Millions",
        date,
        value,
    ]


def csv_line(values: list[str]) -> bytes:
    stream = io.StringIO(newline="")
    csv.writer(stream, lineterminator="\n").writerow(values)
    return stream.getvalue().encode("utf-8")


def test_selected_rows_require_complete_csv_and_exact_metadata() -> None:
    cells = row(review.SERIES[0], "1950-12-31", "1171530")
    assert review.parse_selected(csv_line(cells))["value"] == "1171530"
    for col, replacement in [
        (1, "Banks"),
        (3, "Euro"),
        (4, "Annual"),
        (9, "Percent"),
        (10, "Billions"),
        (12, "NA"),
    ]:
        bad = cells.copy()
        bad[col] = replacement
        with pytest.raises(ValueError):
            review.parse_selected(csv_line(bad))
    with pytest.raises((ValueError, csv.Error)):
        review.parse_selected(csv_line(cells[:-1]))
    multiline = cells.copy()
    multiline[2] = "line one\nline two"
    with pytest.raises((ValueError, csv.Error)):
        review.parse_selected(csv_line(multiline).splitlines(keepends=True)[0])


def archive(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, rows: list[list[str]]) -> Path:
    path = tmp_path / "source.zip"
    with ZipFile(path, "w", ZIP_DEFLATED) as out:
        out.writestr("Z1.csv", csv_line(review.HEADERS) + b"".join(csv_line(r) for r in rows))
    monkeypatch.setattr(review, "SHA256", hashlib.sha256(path.read_bytes()).hexdigest())
    return path


def complete_rows() -> list[list[str]]:
    return [
        row(code, f"{year}-12-31", value)
        for year in (1950, 1960, 1970)
        for code, value in zip(review.SERIES, ("100", "120", "20"), strict=True)
    ]


def test_stream_requires_all_quarters_unique_and_balanced(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    rows = complete_rows()
    result = review.extract(archive(tmp_path, monkeypatch, rows))
    assert result["observations"]["1950"][review.SERIES[0]]["value"] == "100"
    with pytest.raises(ValueError, match="missing source balance sheet"):
        review.extract(archive(tmp_path, monkeypatch, rows[:-1]))
    with pytest.raises(ValueError, match="duplicate"):
        review.extract(archive(tmp_path, monkeypatch, [*rows, rows[0]]))
    bad = [r.copy() for r in rows]
    bad[1][-1] = "121"
    with pytest.raises(ValueError, match="identity"):
        review.extract(archive(tmp_path, monkeypatch, bad))


def test_inspected_federal_reserve_archive_reproduces_selected_artifact() -> None:
    root = Path(__file__).resolve().parents[1]
    source = root / "samples" / review.FILE
    artifact = root / "samples/remaining-audit-20261028/z1-full-selected.json"
    if not source.is_file() or not artifact.is_file():
        pytest.skip("inspected Federal Reserve archive and selected artifact required")
    extracted = review.extract(source)
    assert extracted == json.loads(artifact.read_text(encoding="utf-8"))
    assert extracted["observations"]["1950"][review.SERIES[0]]["value"] == "1171530"
