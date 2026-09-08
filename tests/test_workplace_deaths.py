"""Plan 027 WI-4b — the workplace-death arc, four slots wide on purpose.

The exhibit here is an absence: the United States kept no federal census of
people killed at work until 1992, and the rate BLS publishes has only been on
one consistent basis since 2006. The tests below exist mostly to stop that
absence being quietly filled — by chaining the pre-2006 employment-based
rates onto the hours-based ones, or by turning the 1990s gap into a number.
"""

from __future__ import annotations

import tomllib
from pathlib import Path

import pytest

from vitrine.loader import load_corpus
from vitrine.series import load_series
from vitrine.site import curation
from vitrine.site.projections.facts import GAP_PREFIX

DATA = Path(__file__).parent.parent / "data"
SERIES_ID = "us-workplace-death-rate"
FACT = "us-{decade}-workplace-death-rate"

CFOI_BEGINS = 1992
HOURS_BASIS_BEGINS = 2006
GAP_DECADE = "1990s"
PLOTTED = {"2000s": 2006, "2010s": 2010, "2020s": 2020}


def _facts() -> dict[str, object]:
    corpus = load_corpus(DATA)
    return {
        room.decade: fact
        for room in corpus.rooms
        if room.country == "us"
        for fact in room.facts
        if fact.id == FACT.format(decade=room.decade)
    }


def test_the_arc_is_exactly_the_four_decades_the_record_supports() -> None:
    arc = curation.ARC_BY_SLUG["workplace-death-rate"]
    assert set(arc.fact_ids) == {GAP_DECADE, *PLOTTED}
    wing = {w.slug: w for w in curation.CORRIDOR_WINGS}["different-country"]
    assert arc.slug in wing.arc_slugs


def test_the_series_starts_where_the_basis_starts() -> None:
    """Nothing before 2006 may appear: earlier rates are a different measure."""
    years = sorted(load_series(DATA)[SERIES_ID].values)
    assert years[0] == HOURS_BASIS_BEGINS, (
        "a value before 2006 means employment-based rates were chained onto "
        "hours-based ones — BLS says they are not the same measure"
    )
    assert years == list(range(years[0], years[-1] + 1)), "the series has holes"


def test_the_1990s_slot_is_a_gap_and_says_why() -> None:
    fact = _facts()[GAP_DECADE]
    assert fact.value.startswith(GAP_PREFIX)  # type: ignore[attr-defined]
    assert fact.quantity is None  # type: ignore[attr-defined]
    assert str(CFOI_BEGINS) in fact.value  # type: ignore[attr-defined]
    assert "absence of the counting" in fact.notes  # type: ignore[attr-defined]


@pytest.mark.parametrize("decade,year", sorted(PLOTTED.items()))
def test_card_value_matches_the_series(decade: str, year: int) -> None:
    fact = _facts()[decade]
    series = load_series(DATA)[SERIES_ID]
    assert fact.price_year == year  # type: ignore[attr-defined]
    assert fact.quantity == pytest.approx(series.values[year])  # type: ignore[attr-defined]


def test_the_arc_does_not_claim_a_fall() -> None:
    """The presentation choice must not masquerade as a statistical test.

    A narrow range cannot establish the absence of a trend. Keep the arc
    neutral and explain the limits of that editorial choice.
    """
    arc = curation.ARC_BY_SLUG["workplace-death-rate"]
    assert arc.falling is False
    assert "no statistical trend test" in " ".join(arc.caveats)


def test_the_shortness_is_explained_on_the_arc() -> None:
    joined = " ".join(curation.ARC_BY_SLUG["workplace-death-rate"].caveats)
    assert str(CFOI_BEGINS) in joined
    assert str(HOURS_BASIS_BEGINS) in joined
    assert "Earlier estimates and other records exist" in joined
    assert "nobody counted" not in joined


def test_the_source_admits_its_link_check_is_inert() -> None:
    """bls.gov 403s CI, so the expect-markers cannot fire there.

    A marker that never runs is not a check. The source notes must say so,
    rather than leaving a reader to assume CI is verifying this citation.
    """
    raw = tomllib.loads((DATA / "sources.toml").read_text())
    source = next(s for s in raw["source"] if s["id"] == "bls-cfoi-hours-based-rates")
    assert "403" in source["notes"] and "NOT verified" in source["notes"]
