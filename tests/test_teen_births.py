"""Plan 027 WI-5 — the teen-birthrate arc, which does not only fall.

The editorial point of this exhibit is that it cuts against progress-as-
direction: the peak is 1960, not some more distant past, and the rate rose
between 1980 and 1990. The tests below mostly exist to stop that shape being
flattened — by marking the arc as falling, by dropping the reversal, or by
extending the series before the year NCHS actually publishes.
"""

from __future__ import annotations

import tomllib
from pathlib import Path

import pytest

from vitrine.loader import load_corpus
from vitrine.series import load_series
from vitrine.site import curation

DATA = Path(__file__).parent.parent / "data"
SERIES_ID = "us-teen-birth-rate"
FACT = "us-{decade}-teen-birth-rate"
SERIES_FLOOR = 1950
HUS_SOURCE = "nchs-hus-2019-table1"
NVSR_SOURCE = "nchs-nvsr-72-1"


def _facts() -> dict[str, object]:
    corpus = load_corpus(DATA)
    return {
        room.decade: fact
        for room in corpus.rooms
        if room.country == "us"
        for fact in room.facts
        if fact.id == FACT.format(decade=room.decade)
    }


_ARC_DECADES = frozenset(curation.ARC_BY_SLUG["teen-birth-rate"].fact_ids)


def test_the_arc_sits_in_the_wing_and_matches_its_cards() -> None:
    arc = curation.ARC_BY_SLUG["teen-birth-rate"]
    assert set(arc.fact_ids) == set(_facts())
    wing = {w.slug: w for w in curation.CORRIDOR_WINGS}["different-country"]
    assert arc.slug in wing.arc_slugs


def test_the_series_starts_where_the_published_table_starts() -> None:
    years = sorted(load_series(DATA)[SERIES_ID].values)
    assert years[0] == SERIES_FLOOR, (
        "a value before 1950 means the series reached outside the published "
        "table — NCHS starts there"
    )


def test_the_peak_is_1960_not_the_distant_past() -> None:
    """The whole editorial point. If this ever fails, the exhibit is wrong."""
    values = load_series(DATA)[SERIES_ID].values
    peak = max(values, key=lambda y: values[y])
    assert peak == 1960, f"the published peak is now {peak}, not 1960"
    assert values[1960] > values[min(values)], "1960 does not exceed the first row"


def test_the_1980s_to_1990s_reversal_survives() -> None:
    """The one rise in the series, and the reason the arc is not 'falling'."""
    values = load_series(DATA)[SERIES_ID].values
    assert values[1990] > values[1980], "the reversal has been flattened"
    rises = [
        b for a, b in zip(sorted(values), sorted(values)[1:], strict=False)
        if values[b] > values[a]
    ]
    assert rises == [1960, 1990], f"the shape changed: rises are {rises}"


def test_the_arc_is_not_dressed_as_a_falling_line() -> None:
    arc = curation.ARC_BY_SLUG["teen-birth-rate"]
    assert arc.falling is False
    joined = " ".join(arc.caveats)
    assert "1960" in joined and "1980" in joined and "1990" in joined


def test_the_arc_says_what_the_denominator_is() -> None:
    """A rate over all women 15-19, not over the sexually active."""
    joined = " ".join(curation.ARC_BY_SLUG["teen-birth-rate"].caveats).lower()
    assert "not over those who were" in joined
    assert "selected-year" in joined  # selected points do not establish an annual peak


@pytest.mark.parametrize("decade", sorted(_ARC_DECADES))
def test_each_card_matches_its_declared_source(decade: str) -> None:
    """Seven cards come from the trend table; the 2020s one cannot.

    Health, United States 2019 stops at 2018, so the 2020s card is read from
    NVSR 72-1 instead and must say so. A card silently attributed to the trend
    table would be citing a document that does not contain it.
    """
    fact = _facts()[decade]
    series = load_series(DATA)[SERIES_ID]
    year = fact.price_year  # type: ignore[attr-defined]
    assert year is not None
    if year in series.values:
        assert fact.source == HUS_SOURCE  # type: ignore[attr-defined]
        assert fact.quantity == pytest.approx(series.values[year])  # type: ignore[attr-defined]
    else:
        assert fact.source == NVSR_SOURCE, (
            f"{decade} cites {fact.source!r} for {year}, which is not in the "  # type: ignore[attr-defined]
            "trend-table series"
        )


def test_both_nchs_sources_declare_content_markers() -> None:
    raw = tomllib.loads((DATA / "sources.toml").read_text())
    by_id = {s["id"]: s for s in raw["source"]}
    assert "Health, United States, 2019" in by_id[HUS_SOURCE]["expect"]
    assert "Births: Final Data for 2021" in by_id[NVSR_SOURCE]["expect"]
