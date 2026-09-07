"""Plan 027 WI-6 (FWI-007 item 2) — the produce-department SKU count.

The remembered "~100 items in 1980 rising to ~400 by 1997" pair is wrong on
both ends and both years; the record (ERS AIB-758 p.3, relaying Litwak's
Supermarket Business surveys of 1988 and 1998) publishes 173 SKUs in 1987
and 335 in 1997. This file holds the committed pair, the source's own
arithmetic, and — where the gitignored archive is present — the archived
document itself, so the figures cannot drift back toward the famous ones.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

from vitrine.loader import load_corpus

DATA = Path(__file__).parent.parent / "data"
ARCHIVE = (
    DATA.parent / "samples" / "47-produce-sku"
    / "aib758-understanding-dynamics-produce-markets.pdf"
)

EXPECTED = {
    "1980s": {"id": "us-1980s-produce-department-skus", "quantity": 173, "year": 1987},
    "1990s": {"id": "us-1990s-produce-department-skus", "quantity": 335, "year": 1997},
}


def _sku_facts() -> dict[str, object]:
    corpus = load_corpus(DATA)
    out: dict[str, object] = {}
    for room in corpus.rooms:
        if room.country != "us":
            continue
        for fact in room.facts:
            if fact.id.endswith("-produce-department-skus"):
                out[room.decade] = fact
    return out


def test_sku_cards_exist_with_trade_survey_tier() -> None:
    facts = _sku_facts()
    assert set(facts) == set(EXPECTED)
    for decade, spec in EXPECTED.items():
        fact = facts[decade]
        assert fact.id == spec["id"]
        assert fact.tier.value == "B"  # trade survey relayed by a federal bulletin
        assert fact.panel.value == "diffusion"
        assert fact.quantity == spec["quantity"]
        assert str(spec["quantity"]) in fact.value
        assert fact.price_year == spec["year"]
        assert fact.source == "usda-ers-aib758"


def test_the_pairs_own_arithmetic_holds() -> None:
    """ERS states a 94-percent increase; the committed pair must reproduce
    it, so the words on the card can never drift from the numbers."""
    facts = _sku_facts()
    increase = (facts["1990s"].quantity - facts["1980s"].quantity) / facts["1980s"].quantity * 100
    assert round(increase) == 94


def test_the_floor_area_contrast_stays_qualitative() -> None:
    """The card states the area contrast in words (under seven percent);
    the precise figures stay in the source notes, not on the card face."""
    facts = _sku_facts()
    assert "4,817" not in facts["1990s"].notes
    assert "5,140" not in facts["1990s"].notes


def test_source_registry_names_the_trade_survey_basis() -> None:
    corpus = load_corpus(DATA)
    source = corpus.sources["usda-ers-aib758"]
    assert "Supermarket Business" in source.population
    assert set(source.expect) == {"173", "335", "Litwak"}
    assert source.year == 2000


@pytest.mark.skipif(not ARCHIVE.is_file(), reason="samples/ archive not present")
def test_archived_document_publishes_the_pair() -> None:
    """Where the archive exists, the committed pair is checked against the
    document's own text layer — the D3 guard against the famous number."""
    sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
    import link_check

    text = link_check._pdf_text(ARCHIVE.read_bytes())
    assert text is not None, "archived AIB-758 has no extractable text layer"
    for marker in ("173", "335", "Litwak"):
        assert marker in text
    # the remembered pair must not masquerade as the record
    assert "~400" not in text.replace("\n", "")
