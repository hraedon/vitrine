"""Plan 027 WI-4a — the road-death arc, and the rate that is not a count.

Same shape as ``test_alcohol_series.py``: the room cards and the annual series
are two committed surfaces transcribed from one table (FHWA Highway Statistics
2023, Table FI-200), and CI holds them against each other because the source
document lives in the gitignored ``samples/`` archive.

FI-200 publishes four rate columns side by side, any of which would look
plausible alone. The extraction script defends against reading the wrong one
by recomputing the rate from the table's own fatality and VMT columns; the
test here defends the *committed* result the same way, from the one figure the
series carries plus what the cards say.
"""

from __future__ import annotations

import tomllib
from pathlib import Path

import pytest

from vitrine.loader import load_corpus
from vitrine.series import load_series
from vitrine.site import curation

DATA = Path(__file__).parent.parent / "data"
SERIES_ID = "us-traffic-death-rate"
FACT = "us-{decade}-traffic-death-rate"
DEFINITION_CHANGE = 1976  # FHWA footnote (3): 30-day death window from here


def _facts() -> dict[str, object]:
    corpus = load_corpus(DATA)
    return {
        room.decade: fact
        for room in corpus.rooms
        if room.country == "us"
        for fact in room.facts
        if fact.id == FACT.format(decade=room.decade)
    }


_ARC_DECADES = frozenset(curation.ARC_BY_SLUG["traffic-death-rate"].fact_ids)


def test_the_arc_covers_every_us_decade_and_sits_in_the_wing() -> None:
    arc = curation.ARC_BY_SLUG["traffic-death-rate"]
    assert set(arc.fact_ids) == set(_facts())
    wing = {w.slug: w for w in curation.CORRIDOR_WINGS}["different-country"]
    assert arc.slug in wing.arc_slugs


def test_series_is_continuous_from_1900() -> None:
    years = sorted(load_series(DATA)[SERIES_ID].values)
    assert years[0] == 1900
    assert years == list(range(years[0], years[-1] + 1)), "the series has holes"


@pytest.mark.parametrize("decade", sorted(_ARC_DECADES))
def test_card_value_matches_the_series(decade: str) -> None:
    fact = _facts()[decade]
    series = load_series(DATA)[SERIES_ID]
    year = fact.price_year  # type: ignore[attr-defined]
    assert year is not None and year in series.values
    assert fact.quantity == pytest.approx(series.values[year])  # type: ignore[attr-defined]


def test_the_definitional_change_is_disclosed_somewhere_visible() -> None:
    """The 30-day window change is not a footnote we may quietly drop.

    Before 1976 a death was counted on a wider window, so the two halves of
    the line are not the same measurement. If that caveat disappears from the
    arc, the chart starts asserting a continuity the source does not.
    """
    arc = curation.ARC_BY_SLUG["traffic-death-rate"]
    joined = " ".join(arc.caveats)
    assert "30 days" in joined
    assert str(DEFINITION_CHANGE) in joined

    raw = tomllib.loads((DATA / "sources.toml").read_text())
    source = next(s for s in raw["source"] if s["id"] == "fhwa-fi200-2023")
    assert "died within 30 days" in source["expect"], (
        "the expect-marker is what notices if FHWA ever drops the footnote"
    )


def test_the_arc_says_the_rate_is_not_a_count() -> None:
    """The falling line is a denominator story and must say so.

    Absolute deaths are higher today than in 1930; only the risk per mile
    collapsed. An arc that renders the fall without that sentence invites
    exactly the misreading the museum exists to prevent.
    """
    joined = " ".join(curation.ARC_BY_SLUG["traffic-death-rate"].caveats).lower()
    assert "rate, not a count" in joined


def test_absolute_deaths_really_did_not_fall_like_the_rate() -> None:
    """The premise of the caveat above, checked rather than asserted.

    If this ever failed, the caveat would be the thing that is wrong.
    """
    series = load_series(DATA)[SERIES_ID]
    assert series.values[1930] > 10 * series.values[2023], (
        "the rate did not fall by anything like the factor the caveat claims"
    )


def test_the_thin_1900_exposure_is_disclosed() -> None:
    """A rate resting on 36 deaths must not be presented like the rest."""
    card = _facts()["1900s"]
    assert "36" in card.notes  # type: ignore[attr-defined]
    assert "back-cast" in card.notes or "estimate" in card.notes  # type: ignore[attr-defined]
