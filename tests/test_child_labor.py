"""Plan 027 WI-8 — children and work: the decennial child-labor series.

The curated series is the Census Bureau's own comparability-adjusted
reconstruction (Comparative Occupation Statistics, 1870-1940, Table XVIII,
printed p. 97): the share of children 10-15 reported as gainful workers at
each census from 1870 to 1930. The archived scan's OCR text layer is
defective for most table cells (see scripts/census_child_labor_extract.py),
so the table was transcribed from page renders and is held honest here by
the table's own arithmetic, by the decade primaries, and — where the
gitignored archive is present — by the pinned document bytes.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

from vitrine.loader import load_corpus
from vitrine.series import load_series

DATA = Path(__file__).parent.parent / "data"
ARCHIVE_DIR = DATA.parent / "samples" / "49-child-labor"
ARCHIVE = ARCHIVE_DIR / "census-1940-comparative-occupation-statistics-ch2.pdf"
DUMP = ARCHIVE_DIR / "census-1943-ch2-p97.txt"
SOURCE_ID = "census-1943-comparative-occupations"
SERIES_ID = "us-child-labor-share"

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
import census_child_labor_extract as extract  # noqa: E402

DECADES = ("1900s", "1910s", "1920s", "1930s")
EXPECTED = {
    "1900s": {"quantity": 18.2, "year": 1900},
    "1910s": {"quantity": 15.0, "year": 1910},
    "1920s": {"quantity": 11.3, "year": 1920},
    "1930s": {"quantity": 4.7, "year": 1930},
}


def _facts() -> dict[str, object]:
    corpus = load_corpus(DATA)
    out: dict[str, object] = {}
    for room in corpus.rooms:
        if room.country != "us":
            continue
        for fact in room.facts:
            if fact.id.endswith("-child-labor-share"):
                out[room.decade] = fact
    return out


def test_the_four_census_years_have_day_cards() -> None:
    facts = _facts()
    assert set(facts) >= set(EXPECTED)
    for decade, spec in EXPECTED.items():
        fact = facts[decade]
        assert fact.tier.value == "A"
        assert fact.panel.value == "day"
        assert fact.quantity == spec["quantity"]
        assert fact.price_year == spec["year"]
        assert fact.source == SOURCE_ID


def test_quantities_match_the_series_values() -> None:
    series = load_series(DATA)[SERIES_ID]
    facts = _facts()
    for decade, spec in EXPECTED.items():
        assert series.values[spec["year"]] == facts[decade].quantity


def test_the_series_spans_the_census_years_and_stops() -> None:
    series = load_series(DATA)[SERIES_ID]
    assert series.source == SOURCE_ID
    assert series.tier.value == "A"
    assert sorted(series.values) == [1870, 1880, 1890, 1900, 1910, 1920, 1930]


def test_no_post_series_zeros_anywhere() -> None:
    """The 1940s slot is a stated gap; later decades carry no card at all."""
    facts = _facts()
    gap = facts["1940s"]
    assert "no comparable record" in gap.value
    assert not hasattr(gap, "quantity") or gap.quantity is None
    for later in ("1950s", "1960s", "1970s", "1980s", "1990s", "2000s", "2010s", "2020s"):
        assert later not in facts, f"{later} must not carry a child-labor card"


def test_the_table_closes_against_its_own_arithmetic() -> None:
    """Every printed percent must equal 100 x number / total at the table's
    one-decimal rounding, pursuits must sum, and the sex blocks must sum to
    the Total block — the closure that pins the eye transcription."""
    extract._check_closures()


def test_the_1910_adjustment_reconciles_with_the_raw_decade_primary() -> None:
    """Vol IV Table 28 (printed p. 70) publishes 1,990,225 child workers for
    1910; the monograph deducts 368,499 (165,557 males + 202,942 females)
    and prints 1,621,726. The words on the cards cannot drift from this."""
    raw_1910 = 1_990_225
    deducted = 165_557 + 202_942
    adjusted = dict((row[0], row[2]) for row in extract.TOTAL_BLOCK)[1910]
    assert adjusted == raw_1910 - deducted


def test_the_1900_row_matches_the_twelfth_census_report() -> None:
    """The 1900 occupation report (printed p. cxlvii) publishes the same
    counts the monograph carries for 1900; the series cannot drift from
    either without breaking the other."""
    report = {"total": 9_613_252, "workers": 1_750_178, "percent": 18.2}
    row = dict((r[0], r) for r in extract.TOTAL_BLOCK)[1900]
    assert row[1] == report["total"]
    assert row[2] == report["workers"]
    assert row[3] == report["percent"]


def test_source_registry_entry_carries_the_comparability_record() -> None:
    corpus = load_corpus(DATA)
    source = corpus.sources[SOURCE_ID]
    assert source.publisher == "U.S. Census Bureau"
    assert source.year == 1943
    assert "fraser.stlouisfed.org" in source.url
    notes = source.notes
    for marker in ("Table XVIII", "not exactly comparable", "overcount", "undercount"):
        assert marker in notes, marker


def test_the_arc_covers_the_five_rooms_and_names_the_gap() -> None:
    from vitrine.site.curation.corridors import ARCS

    arc = next(a for a in ARCS if a.series_id == SERIES_ID)
    assert set(arc.fact_ids.values()) == {f"us-{d}-child-labor-share" for d in (*DECADES, "1940s")}
    assert any("gap, not a zero" in c for c in arc.caveats)


@pytest.mark.skipif(not ARCHIVE.is_file(), reason="samples/ archive not present")
def test_archived_document_still_carries_the_anchors() -> None:
    """The D3 guard: the archived scan must still be the document the table
    was transcribed from (its clean text-layer anchors and, via the extract
    script's own assertions, its table arithmetic)."""
    import link_check

    text = link_check._pdf_text(ARCHIVE.read_bytes())
    assert text is not None, "archived monograph has no extractable text layer"
    flat = text.replace("\n", " ")
    for anchor in extract.RAW_ANCHORS:
        assert anchor in flat, anchor


@pytest.mark.skipif(not DUMP.is_file(), reason="audit dump not generated")
def test_audit_dump_is_pinned_to_the_archived_bytes() -> None:
    import hashlib

    header_sha = DUMP.read_text(encoding="utf-8").split("source pdf sha256: ")[1].split("\n")[0]
    assert header_sha == hashlib.sha256(ARCHIVE.read_bytes()).hexdigest()
