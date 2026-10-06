"""Plan 027 WI-10 — communicating by mail: pieces of mail handled.

The series is the Post Office Department's / U.S. Postal Service's national
count of pieces of mail handled, FY1900-FY2019 — official federal statistics
(Tier A) read through the Statistical Abstract's postal tables (four archived
scan editions plus the 2012 edition's clean-text Transportation section) and
the USPS Form 10-K volume tables for the tail. The archive is gitignored, so
the dump-reading checks skip when samples/ is absent (CI checkouts have no
samples/).
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from vitrine.loader import load_corpus
from vitrine.series import load_series

DATA = Path(__file__).parent.parent / "data"
ARCHIVE_DIR = DATA.parent / "samples" / "54-mail"
ABSTRACTS_DIR = DATA.parent / "samples" / "01-statistical-abstracts"
DUMP = ARCHIVE_DIR / "mail-pieces-dump.txt"
SOURCE_ID = "us-postal-mail-volume"
SERIES_ID = "us-mail-pieces-handled"

# Decade marker -> the year its card shows and the value it carries.
MARKERS = {
    "1900s": {"year": 1900, "quantity": 7130},
    "1910s": {"year": 1910, "quantity": 14850},
    "1920s": {"year": 1925, "quantity": 25835},
    "1930s": {"year": 1930, "quantity": 27888},
    "1940s": {"year": 1940, "quantity": 27749},
    "1950s": {"year": 1950, "quantity": 45064},
    "1960s": {"year": 1960, "quantity": 63675},
    "1970s": {"year": 1970, "quantity": 84882},
    "1980s": {"year": 1980, "quantity": 106311},
    "1990s": {"year": 1990, "quantity": 166301},
    "2000s": {"year": 2005, "quantity": 211743},
    "2010s": {"year": 2010, "quantity": 170574},
}

# Years the archived documents do not print on the measure used here.
ABSENT = (
    1915, 1920,
    1984, 1986, 1989,
    1991, 1992, 1993, 1994, 1996, 1997, 1998, 1999,
    2001, 2002, 2003, 2004, 2006, 2007,
)

# The 1970s revision: the 1976 edition's prints, superseded by the 1985
# edition (which the 1990 edition confirms at 1970).
SUPERSEDED_1976_PRINTS = {
    1970: 82005, 1971: 84882, 1972: 86983, 1973: 87156, 1974: 89683,
    1975: 90098, 1976: 89266,
}

# The 10-K reclassification revisions (year -> superseded prints).
SUPERSEDED_10K_PRINTS = {
    2015: (154157, 154035),
    2016: (153941,),
    2017: (149491,),
}


def _facts() -> dict[str, object]:
    corpus = load_corpus(DATA)
    out: dict[str, object] = {}
    for room in corpus.rooms:
        if room.country != "us":
            continue
        for fact in room.facts:
            if fact.id.endswith("-mail-pieces-handled"):
                out[room.decade] = fact
    return out


def test_every_decade_has_a_marker_and_the_2020s_is_a_gap() -> None:
    facts = _facts()
    assert set(facts) >= set(MARKERS)
    for decade, spec in MARKERS.items():
        fact = facts[decade]
        assert fact.tier.value == "A"
        assert fact.panel.value == "table"
        assert fact.quantity == spec["quantity"]
        assert fact.price_year == spec["year"]
        assert fact.source == SOURCE_ID
    gap = facts["2020s"]
    assert gap.quantity is None
    assert gap.value.strip().lower().startswith("no chained value")


def test_quantities_match_the_series_values() -> None:
    series = load_series(DATA)[SERIES_ID]
    facts = _facts()
    for decade, spec in MARKERS.items():
        assert series.values[spec["year"]] == facts[decade].quantity


def test_the_series_spans_1900_to_2019_and_stops() -> None:
    series = load_series(DATA)[SERIES_ID]
    assert series.source == SOURCE_ID
    assert series.tier.value == "A"
    assert min(series.values) == 1900
    assert max(series.values) == 2019
    for absent in ABSENT:
        assert absent not in series.values
    assert not any(y > 2019 for y in series.values)


def test_the_shape_peaks_in_2005_and_ends_a_third_below() -> None:
    series = load_series(DATA)[SERIES_ID]
    peak_year = max(series.values, key=lambda y: series.values[y])
    assert peak_year == 2005
    # Every print after the peak is below the peak itself; one reclassified
    # print (2016) sits a hair above its predecessor, and the record keeps it.
    for year, value in series.values.items():
        if year > 2005:
            assert value < series.values[2005], (year, value)
    assert series.values[2016] > series.values[2015]
    assert series.values[2019] < series.values[2015]
    assert series.values[2019] > series.values[1900]


def test_the_1970s_revision_is_recorded_not_smoothed() -> None:
    series = load_series(DATA)[SERIES_ID]
    assert series.values[1970] == 84882  # the 1990 edition's exact print
    if not DUMP.exists():
        pytest.skip("gitignored archive not present on this machine")
    dump = DUMP.read_text(encoding="utf-8")
    for year, superseded in SUPERSEDED_1976_PRINTS.items():
        line = next(ln for ln in dump.splitlines() if ln.startswith(f"{year} "))
        assert f"sa1976-no868:{superseded}" in line, year


def test_the_10k_reclassifications_are_recorded_not_smoothed() -> None:
    series = load_series(DATA)[SERIES_ID]
    assert series.values[2015] == 154321
    assert series.values[2016] == 154342
    assert series.values[2017] == 149590
    if not DUMP.exists():
        pytest.skip("gitignored archive not present on this machine")
    dump = DUMP.read_text(encoding="utf-8")
    for year, superseded in SUPERSEDED_10K_PRINTS.items():
        line = next(ln for ln in dump.splitlines() if ln.startswith(f"{year} "))
        for old in superseded:
            assert f":{old}" in line, (year, old)


def test_the_2010_splice_prints_both_bases() -> None:
    if not DUMP.exists():
        pytest.skip("gitignored archive not present on this machine")
    dump = DUMP.read_text(encoding="utf-8")
    line = next(ln for ln in dump.splitlines() if ln.startswith("2010 "))
    assert "sa2012-t1127:170574" in line
    assert "usps-10k-fy2012:170859" in line
    series = load_series(DATA)[SERIES_ID]
    assert series.values[2010] == 170574  # the compilation's print is carried


def test_overlapping_editions_reconcile() -> None:
    """Every year printed by more than one edition agrees to the later
    edition's precision — except the recorded 1970s revision and the 2010
    splice, which are checked separately above."""
    if not DUMP.exists():
        pytest.skip("gitignored archive not present on this machine")
    prints: dict[int, list[float]] = {}
    for line in DUMP.read_text(encoding="utf-8").splitlines():
        if not line or line.startswith("#"):
            continue
        parts = line.split()
        if not parts[0].isdigit():
            continue
        year = int(parts[0])
        if year in SUPERSEDED_1976_PRINTS or year in SUPERSEDED_10K_PRINTS:
            continue  # revision years, checked separately above
        if year == 2010:
            continue  # the splice year, checked separately above
        for tag in parts[2:]:
            value = float(tag.split(":")[1])
            # billions prints are scaled by the dump header's conversion
            if value < 1000:
                value *= 1000
            prints.setdefault(year, []).append(value)
    overlapping = {y: v for y, v in prints.items() if len(v) > 1}
    assert set(overlapping) >= {1900, 1910, 1930, 1940, 1950, 1955, 1960,
                                1965, 1980, 2014, 2018}
    for year, values in overlapping.items():
        spread = max(values) - min(values)
        assert spread <= 100, (year, values)


def test_the_transition_quarter_is_not_summed() -> None:
    if not DUMP.exists():
        pytest.skip("gitignored archive not present on this machine")
    flat = " ".join(DUMP.read_text(encoding="utf-8").replace("#", " ").split())
    assert "1976 transition quarter" in flat
    assert "not summed into any year" in flat.lower()
    # No dump line carries 21.5 as a fiscal-year value.
    for line in DUMP.read_text(encoding="utf-8").splitlines():
        if line and not line.startswith("#") and line[0].isdigit():
            assert " 21.5 " not in line


def test_source_registry_entry_states_the_tier_rationale() -> None:
    corpus = load_corpus(DATA)
    source = corpus.sources[SOURCE_ID]
    assert "annual-report statistics" in source.notes
    assert "Tier A" in source.notes
    assert source.population is not None
    assert "transition quarter" in source.population


def test_the_arc_names_the_span_and_the_gap() -> None:
    from vitrine.site import curation

    arc = curation.ARC_BY_SLUG["mail-pieces-handled"]
    assert arc.series_id == SERIES_ID
    assert set(arc.fact_ids) == set(MARKERS) | {"2020s"}
    assert any("gap" in c.lower() for c in arc.caveats)


def test_audit_dump_is_pinned_to_the_archived_bytes() -> None:
    if not DUMP.exists():
        pytest.skip("gitignored archive not present on this machine")
    text = DUMP.read_text(encoding="utf-8")
    pins = dict(
        re.findall(r"^# source (?:pdf|zip) (\S+) sha256: ([0-9a-f]{64})$", text, re.M)
    )
    assert len(pins) == 11
    import hashlib

    zip_names = {"sa1960", "sa1976", "sa1985", "sa1990"}
    for name, digest in pins.items():
        if name in zip_names:
            path = ABSTRACTS_DIR / f"{name[2:]}.zip"
        else:
            path = ARCHIVE_DIR / f"{name}.pdf"
        assert path.exists(), path
        actual = hashlib.sha256(path.read_bytes()).hexdigest()
        assert actual == digest, name
