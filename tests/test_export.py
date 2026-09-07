"""Plan 017 WI-3: deterministic, citable corpus exports."""

import csv
import json
import math
from dataclasses import replace
from pathlib import Path

import pytest

from vitrine.export import (
    CSV_FIELDS,
    RAW_CSV_FILENAME,
    SAFE_CSV_FILENAME,
    export_corpus,
    quantified_fact_count,
)
from vitrine.loader import load_corpus
from vitrine.series import load_series
from vitrine.site.build import build_data_page

DATA = Path(__file__).parent.parent / "data"


def test_json_round_trip_preserves_corpus_shape(tmp_path: Path) -> None:
    corpus = load_corpus(DATA)
    series = load_series(DATA)
    export_corpus(corpus, tmp_path, series)

    payload = json.loads((tmp_path / "data" / "corpus.json").read_text())
    assert set(payload) == {"assumptions", "rooms", "schema_version", "series", "sources"}
    assert payload["schema_version"] == 1
    assert len(payload["rooms"]) == len(corpus.rooms)
    assert len(payload["sources"]) == len(corpus.sources)
    assert len(payload["assumptions"]) == len(corpus.assumptions)
    assert len(payload["series"]) == len(series)

    fact_fields = {
        "amount_minor", "assumptions", "basis", "currency", "id", "label", "notes",
        "panel", "price_year", "quantity", "source", "tier", "unit", "value",
    }
    derived_fields = {
        "at_year", "computed_amount_minor", "computed_currency", "computed_value",
        "count_series", "denominator", "id", "inflate_from_year", "inflate_series",
        "inflate_to_year", "inflation", "label", "notes", "op", "panel", "precision",
        "assumptions", "threshold", "tier", "unit", "value", "numerator",
    }
    source_fields = {
        "expect", "id", "measure", "notes", "population", "publisher", "short_cite",
        "title", "url", "year",
    }
    series_fields = {
        "currency", "id", "label", "measure", "notes", "population", "source",
        "splices_from", "tier", "unit", "values", "values_minor",
    }
    assert all(set(source) == source_fields for source in payload["sources"])
    assert all(set(item) == series_fields for item in payload["series"])
    assert all(
        set(room) == {
            "country", "data_as_of", "decade", "derived", "facts", "income_anchor",
            "slug", "wage_anchor",
        }
        for room in payload["rooms"]
    )
    assert all(
        set(fact) == fact_fields
        for room in payload["rooms"]
        for fact in room["facts"]
    )
    assert all(
        set(derived) == derived_fields
        for room in payload["rooms"]
        for derived in room["derived"]
    )

    exported_facts = [fact for room in payload["rooms"] for fact in room["facts"]]
    expected_facts = [fact for room in corpus.rooms for fact in room.facts]
    assert len(exported_facts) == len(expected_facts)
    assert {fact["id"] for fact in exported_facts} == {
        fact.id for fact in expected_facts
    }

    exported_derived = [derived for room in payload["rooms"] for derived in room["derived"]]
    assert all("value" in derived and "numerator" in derived for derived in exported_derived)
    ratio = next(
        item for item in exported_derived if item["id"] == "us-1950s-home-as-income-years"
    )
    assert ratio["numerator"] == "us-1950s-median-home-value"
    assert ratio["denominator"] == "us-1950s-median-income-four-person"
    assert ratio["value"] == "≈ 2.0"
    assert ratio["computed_value"] == pytest.approx(735400 / 367500)

    inflation = next(
        item
        for room in payload["rooms"]
        for item in room["derived"]
        if item["op"] == "inflate"
    )
    cpi = series[inflation["inflate_series"]]
    assert inflation["inflation"] == {
        "series_id": cpi.id,
        "from": {
            "year": inflation["inflate_from_year"],
            "value": cpi.values[inflation["inflate_from_year"]],
        },
        "to": {
            "year": inflation["inflate_to_year"],
            "value": cpi.values[inflation["inflate_to_year"]],
        },
    }
    assert inflation["computed_value"] == pytest.approx(
        2736600 * cpi.values[2024] / cpi.values[2020] / 100
    )
    exported_cpi = next(item for item in payload["series"] if item["id"] == cpi.id)
    assert exported_cpi["values"]["2020"] == cpi.values[2020]
    assert exported_cpi["values"]["2024"] == cpi.values[2024]


def test_exports_are_byte_identical_and_csv_is_quantified_only(tmp_path: Path) -> None:
    corpus = load_corpus(DATA)
    series = load_series(DATA)
    first = tmp_path / "first"
    second = tmp_path / "second"
    export_corpus(corpus, first, series)
    export_corpus(corpus, second, series)
    build_data_page(corpus, first)
    build_data_page(corpus, second)

    for name in (
        "corpus.json",
        RAW_CSV_FILENAME,
        SAFE_CSV_FILENAME,
    ):
        assert (first / "data" / name).read_bytes() == (second / "data" / name).read_bytes()
    for name in ("data.html", "assets/enhancements.js", "assets/museum.css"):
        assert (first / name).read_bytes() == (second / name).read_bytes()
    assert not list(first.rglob("*.publish.lock"))
    assert not list(second.rglob("*.publish.lock"))

    with (first / "data" / SAFE_CSV_FILENAME).open(
        encoding="utf-8-sig", newline=""
    ) as handle:
        reader = csv.DictReader(handle)
        assert reader.fieldnames == list(CSV_FIELDS)
        rows = list(reader)
    assert len(rows) == quantified_fact_count(corpus)
    assert all(row["quantity"] for row in rows)
    # the safe CSV carries a BOM for spreadsheet decoding; the raw one does not
    assert (first / "data" / SAFE_CSV_FILENAME).read_bytes().startswith(b"\xef\xbb\xbf")
    assert not (first / "data" / RAW_CSV_FILENAME).read_bytes().startswith(b"\xef\xbb\xbf")


def test_formula_safe_csv_keeps_canonical_values_unchanged(tmp_path: Path) -> None:
    corpus = load_corpus(DATA)
    series = load_series(DATA)
    room_index = next(
        index
        for index, room in enumerate(corpus.rooms)
        if any(fact.quantity is not None for fact in room.facts)
    )
    room = corpus.rooms[room_index]
    fact_index = next(index for index, fact in enumerate(room.facts) if fact.quantity is not None)
    fact = room.facts[fact_index]
    dangerous = replace(fact, label="=SUM(A1)", value="+cmd|'/C calc'!A0")
    facts = (*room.facts[:fact_index], dangerous, *room.facts[fact_index + 1 :])
    altered_room = replace(room, facts=facts)
    altered = replace(
        corpus,
        rooms=(*corpus.rooms[:room_index], altered_room, *corpus.rooms[room_index + 1 :]),
    )

    export_corpus(altered, tmp_path, series)
    raw = (tmp_path / "data" / RAW_CSV_FILENAME).read_text()
    safe = (tmp_path / "data" / SAFE_CSV_FILENAME).read_text()
    assert "=SUM(A1)" in raw
    assert "'=SUM(A1)" in safe
    assert "'+cmd|'/C calc'!A0" in safe
    payload = json.loads((tmp_path / "data" / "corpus.json").read_text())
    exported = next(
        fact
        for room in payload["rooms"]
        for fact in room["facts"]
        if fact["id"] == dangerous.id
    )
    assert exported["label"] == "=SUM(A1)"
    assert exported["value"] == "+cmd|'/C calc'!A0"


def test_export_file_failure_rolls_back_existing_data_directory(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    corpus = load_corpus(DATA)
    series = load_series(DATA)
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    for name in ("corpus.json", RAW_CSV_FILENAME, SAFE_CSV_FILENAME):
        (data_dir / name).write_text("old")

    import vitrine.export as export_module

    def fail(_: object) -> str:
        raise RuntimeError("CSV serialization failed")

    monkeypatch.setattr(export_module, "_safe_csv_text", fail)
    with pytest.raises(RuntimeError, match="CSV serialization failed"):
        export_corpus(corpus, tmp_path, series)

    assert all(
        (data_dir / name).read_text() == "old"
        for name in ("corpus.json", RAW_CSV_FILENAME, SAFE_CSV_FILENAME)
    )
    assert not list(tmp_path.glob(".data.staging-*"))


def test_export_rejects_nonfinite_float_before_writing_json(tmp_path: Path) -> None:
    corpus = load_corpus(DATA)
    room_index = next(
        index
        for index, room in enumerate(corpus.rooms)
        if room.facts
    )
    room = corpus.rooms[room_index]
    fact = replace(room.facts[0], quantity=math.nan)
    altered = replace(
        corpus,
        rooms=(
            *corpus.rooms[:room_index],
            replace(room, facts=(fact, *room.facts[1:])),
            *corpus.rooms[room_index + 1 :],
        ),
    )

    with pytest.raises(ValueError, match="non-finite float"):
        export_corpus(altered, tmp_path, load_series(DATA))
    assert not (tmp_path / "data").exists()
