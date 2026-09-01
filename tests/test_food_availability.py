"""Plan 027 WI-6a — the availability arc group, which is not a smooth rise.

Four commodities on one shared pounds-per-person axis. The exhibit's honesty
depends on three things this file holds: that the cards and their series agree,
that the group keeps saying availability is not intake, and that the lines are
not extended past the years their sheets publish.
"""

from __future__ import annotations

import tomllib
from pathlib import Path

import pytest

from vitrine.loader import load_corpus
from vitrine.series import load_series
from vitrine.site import curation

DATA = Path(__file__).parent.parent / "data"
GROUP = "exotic-turned-ordinary"
COMMODITIES = ("broccoli", "bell-peppers", "avocados", "grapes")

# where each published sheet begins; a card before this would be invented
FIRST_YEAR = {"broccoli": 1960, "bell-peppers": 1960, "avocados": 1970, "grapes": 1970}


def _facts() -> dict[str, dict[str, object]]:
    corpus = load_corpus(DATA)
    out: dict[str, dict[str, object]] = {c: {} for c in COMMODITIES}
    for room in corpus.rooms:
        if room.country != "us":
            continue
        for fact in room.facts:
            for c in COMMODITIES:
                if fact.id == f"us-{room.decade}-availability-{c}":
                    out[c][room.decade] = fact
    return out


def test_the_group_is_placed_and_names_four_commodities() -> None:
    group = curation.ARC_GROUP_BY_SLUG[GROUP]
    assert len(group.members) == len(COMMODITIES)
    slugs = {slug for slug, _label, _colour in group.members}
    assert slugs == {f"availability-{c}" for c in COMMODITIES}
    wing = {w.slug: w for w in curation.CORRIDOR_WINGS}["different-country"]
    assert GROUP in wing.arc_slugs


def test_every_member_colour_role_resolves() -> None:
    """A fourth commodity needed a fourth role; unknown roles crash the render."""
    from vitrine.site import tokens

    known = {"copper", "copper-deep", "brass", "brass-deep"}
    roles = [colour for _s, _l, colour in curation.ARC_GROUP_BY_SLUG[GROUP].members]
    assert set(roles) <= known
    assert len(set(roles)) == len(roles), "two commodities share a colour"
    assert tokens.COPPER_DEEP and tokens.BRASS_DEEP


@pytest.mark.parametrize("commodity", COMMODITIES)
def test_cards_match_their_series(commodity: str) -> None:
    series = load_series(DATA)[f"us-availability-{commodity}"]
    cards = _facts()[commodity]
    assert cards, f"{commodity} has no cards"
    for decade, fact in cards.items():
        year = fact.price_year  # type: ignore[attr-defined]
        assert year is not None, f"{decade}: no year on the card"
        assert year in series.values, f"{decade}: {year} is not in the series"
        assert fact.quantity == pytest.approx(series.values[year])  # type: ignore[attr-defined]


@pytest.mark.parametrize("commodity", COMMODITIES)
def test_no_card_before_the_published_sheet(commodity: str) -> None:
    """The line starts where ERS starts, not where the commodity did."""
    series = load_series(DATA)[f"us-availability-{commodity}"]
    assert min(series.values) == FIRST_YEAR[commodity]
    years = [f.price_year for f in _facts()[commodity].values()]  # type: ignore[attr-defined]
    assert min(years) >= FIRST_YEAR[commodity]


def test_the_group_says_availability_is_not_intake() -> None:
    """The single most important caveat on this exhibit."""
    joined = " ".join(curation.ARC_GROUP_BY_SLUG[GROUP].caveats).lower()
    assert "availability, not intake" in joined
    assert "not what anyone ate" in joined
    assert "farm weight" in joined


def test_the_group_admits_the_shape_is_not_a_smooth_rise() -> None:
    """Checked against the data, not merely asserted in prose."""
    joined = " ".join(curation.ARC_GROUP_BY_SLUG[GROUP].caveats).lower()
    assert "not a smooth rise" in joined
    avocados = load_series(DATA)["us-availability-avocados"].values
    broccoli = load_series(DATA)["us-availability-broccoli"].values
    assert avocados[1986] == 2.37 and avocados[1989] == 1.08, (
        "the caveat's 1980s avocado swing no longer matches the series"
    )
    assert broccoli[max(broccoli)] < broccoli[2000], (
        "broccoli is no longer below its 2000 level — the caveat's example is stale"
    )


def test_the_source_declares_a_content_marker() -> None:
    raw = tomllib.loads((DATA / "sources.toml").read_text())
    source = next(s for s in raw["source"] if s["id"] == "usda-ers-fads")
    assert "Food Availability (Per Capita) Data System" in source["expect"]
