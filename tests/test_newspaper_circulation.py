"""Plan 027 WI-10 — finding information: daily newspaper circulation.

The series is the Statistical Abstract's newspapers tables (Editor &
Publisher yearbook data as republished by the Census Bureau — Tier C per the
source/tier review). The archive's editions are scans, so the tables were
eye-transcribed and are held honest here by cross-edition reconciliation on
every overlapping year (the 1960/1965 revision recorded, not smoothed), and
— where the gitignored archive is present — by the pinned document bytes.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from vitrine.loader import load_corpus
from vitrine.series import load_series

DATA = Path(__file__).parent.parent / "data"
ARCHIVE_DIR = DATA.parent / "samples" / "52-newspapers"
DUMP = ARCHIVE_DIR / "daily-newspaper-circulation-dump.txt"
SOURCE_ID = "statistical-abstract-newspapers"
SERIES_ID = "us-daily-newspaper-circulation"

MARKERS = {
    "1950s": {"quantity": 53.8, "year": 1950},
    "1960s": {"quantity": 58.9, "year": 1960},
    "1970s": {"quantity": 62.1, "year": 1970},
    "1980s": {"quantity": 62.2, "year": 1980},
    "1990s": {"quantity": 62.3, "year": 1990},
    "2000s": {"quantity": 55.8, "year": 2000},
}

# The revisions: the 1970 edition's prints for 1960 and 1965, superseded by
# the 1985 edition. Recorded in the dump and the series notes, not smoothed.
SUPERSEDED_PRINTS = {1960: 60.882, 1965: 63.03}


def _facts() -> dict[str, object]:
    corpus = load_corpus(DATA)
    out: dict[str, object] = {}
    for room in corpus.rooms:
        if room.country != "us":
            continue
        for fact in room.facts:
            if fact.id.endswith("-daily-newspaper-circulation"):
                out[room.decade] = fact
    return out


def test_the_marker_years_have_table_cards() -> None:
    facts = _facts()
    assert set(facts) >= set(MARKERS)
    for decade, spec in MARKERS.items():
        fact = facts[decade]
        assert fact.tier.value == "C"
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


def test_the_series_spans_1950_to_2009_and_stops() -> None:
    series = load_series(DATA)[SERIES_ID]
    assert series.source == SOURCE_ID
    assert series.tier.value == "C"
    assert min(series.values) == 1950
    assert max(series.values) == 2009
    # Years no archived edition reprints are absent, not zero — and no
    # post-series value is chained on.
    for absent in (1951, 1953, 1957, 1959, 1961, 1963, 1966, 1971, 1989, 1993, 2001):
        assert absent not in series.values
    assert not any(y > 2009 for y in series.values)


def test_the_1960_and_1965_revision_is_recorded_not_smoothed() -> None:
    dump = DUMP.read_text(encoding="utf-8")
    for year, superseded in SUPERSEDED_PRINTS.items():
        # The dump line carries both prints: the revised value first, the
        # superseded thousands-precision print tagged to the 1970 edition.
        line = next(ln for ln in dump.splitlines() if ln.startswith(f"{year} "))
        assert f"sa1970-no765:{round(superseded * 1000)}" in line
    series = load_series(DATA)[SERIES_ID]
    assert series.values[1960] == 58.9
    assert series.values[1965] == 60.4
    assert SUPERSEDED_PRINTS[1960] not in series.values
    assert SUPERSEDED_PRINTS[1965] not in series.values


def test_overlapping_editions_reconcile() -> None:
    """Every year printed by more than one edition agrees to the later
    edition's precision — the dump's reconciliation claim, checked."""
    prints: dict[int, list[float]] = {}
    for line in DUMP.read_text(encoding="utf-8").splitlines():
        if not line or line.startswith("#"):
            continue
        parts = line.split()
        year = parts[0]
        if not year.isdigit():
            continue
        if int(year) in SUPERSEDED_PRINTS:
            continue  # the two revision years, checked separately above
        values = [float(parts[1])]
        for tag in parts[2:]:
            if ":" in tag:
                values.append(float(tag.split(":")[1]) / 1000)
        prints.setdefault(int(year), []).extend(values)
    overlapping = {y: v for y, v in prints.items() if len(v) > 1}
    assert set(overlapping) >= {1950, 1970, 1975, 1977, 1978, 1979, 2000}
    for year, values in overlapping.items():
        spread = max(values) - min(values)
        assert spread <= 0.05, (year, values)


def test_the_peak_is_1973_and_the_series_falls_from_1990() -> None:
    series = load_series(DATA)[SERIES_ID]
    peak_year = max(series.values, key=lambda y: series.values[y])
    assert peak_year == 1973
    nineties = [series.values[y] for y in range(1994, 2000)]
    assert nineties == sorted(nineties, reverse=True)


def test_the_2010s_marker_is_a_documented_gap() -> None:
    facts = _facts()
    gap = facts["2010s"]
    assert gap.quantity is None
    assert gap.value.strip().lower().startswith("no reliable record")
    assert gap.source == SOURCE_ID
    assert set(facts) & {"2020s"} == set()


def test_source_registry_entry_states_the_tier_rationale() -> None:
    corpus = load_corpus(DATA)
    source = corpus.sources[SOURCE_ID]
    assert "Editor & Publisher" in source.notes
    assert "Tier C" in source.notes
    assert source.population is not None and "September 30" in source.population


def test_the_arc_names_the_span_and_the_gap() -> None:
    from vitrine.site import curation

    arc = curation.ARC_BY_SLUG["daily-newspaper-circulation"]
    assert arc.series_id == SERIES_ID
    assert set(arc.fact_ids) == {
        "1950s", "1960s", "1970s", "1980s", "1990s", "2000s", "2010s",
    }
    assert any("gap" in c.lower() for c in arc.caveats)


def test_audit_dump_is_pinned_to_the_archived_bytes() -> None:
    import hashlib
    import re

    if not DUMP.exists():
        pytest.skip("gitignored archive not present on this machine")
    text = DUMP.read_text(encoding="utf-8")
    pins = re.findall(r"^# source .* sha256: ([0-9a-f]{64})$", text, re.M)
    assert len(pins) == 7
    # The two section PDFs archived in this directory must still hash to
    # their pins; the scan editions live in samples/01-statistical-abstracts
    # (zip pins, likewise asserted by the dump header lines).
    for name in ("sa-2001-ed-inforcomm.pdf", "sa-2012-ed-infocomm.pdf"):
        path = ARCHIVE_DIR / name
        if path.exists():
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
            assert digest in pins
