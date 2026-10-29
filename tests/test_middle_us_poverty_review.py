"""Poverty population columns, duplicate filters and rounding cannot silently drift."""

import json
from pathlib import Path

import pytest
from middle_us_poverty_review import HEADERS, parse, qualify


def test_all_person_count_is_not_family_count_and_rounds_once() -> None:
    rows = [HEADERS, ["United States", "12.6", "25420000", "202200000", "10.9",
                     "20330000", "186700000", "1970", "1", "1", "1970", "1"]]
    assert parse(json.dumps(rows).encode(), 1970) == ("12.6", "25.4")
    rows[0] = HEADERS.copy()
    rows[0][1] = "PCTFAMPOV"
    with pytest.raises(ValueError, match="source fields"):
        parse(json.dumps(rows).encode(), 1970)
    rows[0] = HEADERS
    rows[1][9] = "2"
    with pytest.raises(ValueError, match="all-race"):
        parse(json.dumps(rows).encode(), 1970)


def test_published_source_responses_reproduce_current_records() -> None:
    root = Path(__file__).parent.parent
    if not (root / "samples/remaining-audit-20261028/census-poverty-1960.json").is_file():
        pytest.skip("pinned Census API responses required")
    qualify(root / "samples", root / "data")
