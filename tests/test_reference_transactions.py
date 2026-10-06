"""Plan 027 WI-10 — finding information: public-library reference transactions.

The series is the Public Libraries Survey's national reference-transaction
total, FY1992-FY2019 (a census of public libraries via the state library
agencies — NCES reports through FY2006, IMLS from FY2007 — Tier A). The
national tables print exact thousands-precision rows through FY2010 and only
prose/S1 millions afterwards; fiscal 2013 and 2016 have no printed national
total and are absent, not zero. The dump lives in the gitignored archive, so
the dump-reading checks skip when it is absent (CI checkouts have no
samples/).
"""

from __future__ import annotations

import re
from itertools import pairwise
from pathlib import Path

import pytest

from vitrine.loader import load_corpus
from vitrine.series import load_series

DATA = Path(__file__).parent.parent / "data"
ARCHIVE_DIR = DATA.parent / "samples" / "53-library-reference"
DUMP = ARCHIVE_DIR / "reference-transactions-dump.txt"
SOURCE_ID = "imls-public-libraries-survey"
SERIES_ID = "us-public-library-reference-transactions"

MARKERS = {
    "1990s": {"quantity": 227.997, "year": 1992},
    "2000s": {"quantity": 309.839, "year": 2009},
    "2010s": {"quantity": 308.629, "year": 2010},
}

# Years no retrieved document prints a national total for.
ABSENT = (2013, 2016)


def _facts() -> dict[str, object]:
    corpus = load_corpus(DATA)
    out: dict[str, object] = {}
    for room in corpus.rooms:
        if room.country != "us":
            continue
        for fact in room.facts:
            if fact.id.endswith("-public-library-reference-transactions"):
                out[room.decade] = fact
    return out


def test_the_marker_years_have_table_cards() -> None:
    facts = _facts()
    assert set(facts) >= set(MARKERS)
    for decade, spec in MARKERS.items():
        fact = facts[decade]
        assert fact.tier.value == "A"
        assert fact.panel.value == "table"
        assert fact.quantity == spec["quantity"]
        assert fact.price_year == spec["year"]
        assert fact.source == SOURCE_ID
        assert str(spec["quantity"]) in fact.value


def test_quantities_match_the_series_values() -> None:
    series = load_series(DATA)[SERIES_ID]
    facts = _facts()
    for decade, spec in MARKERS.items():
        assert series.values[spec["year"]] == facts[decade].quantity


def test_the_series_spans_1992_to_2019_and_stops() -> None:
    series = load_series(DATA)[SERIES_ID]
    assert series.source == SOURCE_ID
    assert series.tier.value == "A"
    assert min(series.values) == 1992
    assert max(series.values) == 2019
    for absent in ABSENT:
        assert absent not in series.values
    assert not any(y > 2019 for y in series.values)


def test_the_shape_rises_to_a_2009_peak_then_falls_every_printed_year() -> None:
    series = load_series(DATA)[SERIES_ID]
    peak_year = max(series.values, key=lambda y: series.values[y])
    assert peak_year == 2009
    after = [(y, series.values[y]) for y in sorted(series.values) if y > 2009]
    for (_, prev), (year, value) in pairwise(after):
        assert value < prev, (year, value)
    assert series.values[2019] < series.values[1992]


def test_absent_years_are_recorded_in_the_dump() -> None:
    if not DUMP.exists():
        pytest.skip("gitignored archive not present on this machine")
    dump = DUMP.read_text(encoding="utf-8")
    for year in ABSENT:
        assert not any(
            line.startswith(f"{year} ") for line in dump.splitlines()
        ), year
    assert "2013" in dump  # the header explains why the year is absent
    assert "2016" in dump


def test_the_revision_signal_is_recorded_not_smoothed() -> None:
    if not DUMP.exists():
        pytest.skip("gitignored archive not present on this machine")
    dump = DUMP.read_text(encoding="utf-8")
    assert "295.8" in dump  # the revised FY2011 base the FY2012 report implies
    assert "272.5" in dump  # the FY2013 level the FY2014 report implies
    series = load_series(DATA)[SERIES_ID]
    assert series.values[2011] == 293.1  # the FY2011 report's own print


def test_the_print_precision_is_kept_per_year() -> None:
    series = load_series(DATA)[SERIES_ID]
    # Thousands-precision table rows convert without rounding; prose and S1
    # prints keep the source's decimals.
    assert series.values[1992] == 227.997
    assert series.values[2004] == 304.39
    assert series.values[2011] == 293.1
    assert series.values[2015] == 255.88
    assert series.values[2019] == 219.7


def test_source_registry_entry_states_the_tier_rationale() -> None:
    corpus = load_corpus(DATA)
    source = corpus.sources[SOURCE_ID]
    assert "census of public libraries" in source.notes
    assert "Tier A" in source.notes
    assert source.population is not None
    assert "typical-week-in-October" in source.population


def test_the_arc_names_the_span_and_the_gap() -> None:
    from vitrine.site import curation

    arc = curation.ARC_BY_SLUG["public-library-reference-transactions"]
    assert arc.series_id == SERIES_ID
    assert set(arc.fact_ids) == {"1990s", "2000s", "2010s", "2020s"}
    assert any("gap" in c.lower() for c in arc.caveats)


def test_audit_dump_is_pinned_to_the_archived_bytes() -> None:
    if not DUMP.exists():
        pytest.skip("gitignored archive not present on this machine")
    text = DUMP.read_text(encoding="utf-8")
    pins = dict(
        re.findall(r"^# source pdf (\S+) sha256: ([0-9a-f]{64})$", text, re.M)
    )
    assert len(pins) == 32
    # Every archived document in the directory must still hash to its pin.
    import hashlib

    for name, digest in pins.items():
        path = ARCHIVE_DIR / f"{name}.pdf"
        assert path.exists(), path
        actual = hashlib.sha256(path.read_bytes()).hexdigest()
        assert actual == digest, name
