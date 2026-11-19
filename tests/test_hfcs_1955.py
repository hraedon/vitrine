"""Plan 027 WI-6, the 1955 checkpoint — households using fresh broccoli.

The primary is the survey's own national report (HFCS 1955 Report No. 1,
Table 14, All-urbanizations section, printed p. 111 of the scan). The scan
is a negative microfilm; its text layer garbles some digits, so every curated
value is closed against the document's own arithmetic: the All-households
row is, by construction, the household-count-weighted mean of its 1-person
and 2+-person rows, with the weights published in the report's Table 1
(1-person households: 369 of 4,556 weighted). This file re-runs that
closure, so a mistyped digit in the fact breaks here even if it looks
plausible.

The transcribed triplets below (all / 1-person / 2-or-more) are the
verification record from the table's percentage block.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

from vitrine.loader import load_corpus

DATA = Path(__file__).parent.parent / "data"
ARCHIVE = (
    DATA.parent / "samples" / "47-produce-sku"
    / "hfcs-1955-report1-united-states.pdf"
)

FACT_ID = "us-1950s-households-using-broccoli"

# Table 1, "Distribution of households interviewed": weighted,
# includes one-quarter farm — 1-person households 369 of 4,556.
W1 = 369 / 4556

# Table 14 (FRESH VEGETABLES), All urbanizations, PERCENTAGE OF
# HOUSEHOLDS USING block: (all households, 1-person, 2-or-more)
TRIPLETS = {
    "broccoli (col 6, all sources)": (4.6, 2.8, 4.8),
    "carrots (col 7, all sources)": (51.5, 36.2, 52.9),
    "green peppers (col 8, all sources)": (21.0, 10.9, 21.9),
    "dark green & deep yellow total (col 2, all sources)": (69.4, 52.0, 71.0),
}


def _fact():
    corpus = load_corpus(DATA)
    for room in corpus.rooms:
        if room.slug == "us-1950s":
            for fact in room.facts:
                if fact.id == FACT_ID:
                    return fact
    raise AssertionError(f"{FACT_ID} not found")


def test_fact_shape() -> None:
    fact = _fact()
    assert fact.panel.value == "day"
    assert fact.tier.value == "A"
    assert fact.quantity == 4.6
    assert "4.6" in fact.value
    assert fact.price_year == 1955
    assert fact.source == "usda-hfcs-1955-report1"


def test_every_triplet_reconciles_at_the_printed_weight() -> None:
    """The document's own arithmetic: All = W1*(1-person) + (1-W1)*(2+).
    Each printed row is rounded to one decimal, so the closure holds to
    within that rounding (|residual| <= 0.1); a misread digit in any cell
    of a column breaks it outright."""
    for name, (all_v, one_p, two_p) in TRIPLETS.items():
        computed = W1 * one_p + (1 - W1) * two_p
        assert abs(computed - all_v) <= 0.1 + 1e-9, (
            f"{name}: computed {computed:.3f} vs printed {all_v}"
        )


def test_fact_value_is_the_verified_broccoli_cell() -> None:
    fact = _fact()
    assert fact.quantity == TRIPLETS["broccoli (col 6, all sources)"][0]


def test_record_names_use_period_and_both_population_denominators() -> None:
    """A household-use measure is not food intake or one matched family."""
    fact = _fact()
    assert "households using" in fact.label.lower()
    assert "4.6% of households" in fact.value
    assert "2.8% of one-person households" in fact.value
    for disclosure in ("all sources", "one survey week", "April–June", "housekeeping"):
        assert disclosure in fact.notes


def test_source_registry_entry() -> None:
    corpus = load_corpus(DATA)
    source = corpus.sources["usda-hfcs-1955-report1"]
    assert source.year == 1956
    assert set(source.expect) == {"FRESH VEGETABLES", "Broccoli",
                                  "PERCENTAGE OF HOUSEHOLDS USING"}
    assert "April-June 1955" in source.population


@pytest.mark.skipif(not ARCHIVE.is_file(), reason="samples/ archive not present")
def test_archived_report_carries_the_table() -> None:
    """Where the archive exists: the document's text layer still carries the
    table header and its explicit item column labels."""
    sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
    import link_check

    text = link_check._pdf_text(ARCHIVE.read_bytes())
    assert text is not None
    assert "FRESH VEGETABLES" in text
    assert "Broccoli" in text
    assert "PERCENTAGE OF HOUSEHOLDS USING" in text.upper()
