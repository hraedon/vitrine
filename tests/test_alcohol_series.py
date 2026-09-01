"""Plan 027 WI-3 — the alcohol arc, and the gap that is the exhibit.

The room cards and the annual series are two committed surfaces transcribed
from one table (NIAAA Surveillance Report #122, Table 1). The PDF itself lives
in the gitignored ``samples/`` archive, so CI cannot re-derive either from the
primary; what CI *can* do is hold the two committed surfaces against each
other, which catches the realistic drift — a card edited without its series,
or a series regenerated against a revised report.

The pre-1934 cards are deliberately outside that cross-check: the table
publishes those years as five-year ranges, so they are not in the year-keyed
series by construction. That exemption is asserted rather than assumed, so it
cannot quietly widen to cover a card that *should* have been checked.
"""

from __future__ import annotations

import tomllib
from pathlib import Path

import pytest

from vitrine.loader import load_corpus
from vitrine.series import load_series
from vitrine.site import curation

DATA = Path(__file__).parent.parent / "data"
SERIES_ID = "us-ethanol-per-capita"
FACT = "us-{decade}-ethanol-per-capita"

PROHIBITION = range(1920, 1934)  # 1920-1933 inclusive
RANGE_ANCHORED = {"1900s", "1910s"}  # published as five-year ranges
GAP_DECADES = {"1920s"}


def _facts() -> dict[str, object]:
    corpus = load_corpus(DATA)
    out = {}
    for room in corpus.rooms:
        for fact in room.facts:
            if fact.id == FACT.format(decade=room.decade) and room.country == "us":
                out[room.decade] = fact
    return out


def test_the_arc_covers_every_us_decade() -> None:
    arc = curation.ARC_BY_SLUG["ethanol-per-capita"]
    assert set(arc.fact_ids) == set(_facts())
    # every decade lands in exactly one bucket: cross-checked, range-anchored,
    # or the gap. A decade added to the arc cannot fall through unchecked.
    assert set(_CHECKED) | RANGE_ANCHORED | GAP_DECADES == set(arc.fact_ids)
    assert not (set(_CHECKED) & (RANGE_ANCHORED | GAP_DECADES))
    assert arc.slug in dict(
        (w.slug, w) for w in curation.CORRIDOR_WINGS
    )["different-country"].arc_slugs


def test_series_has_no_value_across_prohibition() -> None:
    """The gap is in the data, not only in the prose describing it."""
    series = load_series(DATA)[SERIES_ID]
    present = sorted(y for y in series.values if y in PROHIBITION)
    assert present == [], f"Prohibition years carry values: {present}"


def test_series_is_continuous_after_repeal() -> None:
    series = load_series(DATA)[SERIES_ID]
    years = sorted(series.values)
    assert years[0] == 1934, "the post-Repeal record starts the year the table resumes"
    assert years == list(range(years[0], years[-1] + 1)), "the series has holes"


def test_prohibition_decade_is_a_gap_card() -> None:
    from vitrine.site.projections.facts import GAP_PREFIX

    for decade in GAP_DECADES:
        fact = _facts()[decade]
        assert fact.value.startswith(GAP_PREFIX)  # type: ignore[attr-defined]
        assert fact.quantity is None  # type: ignore[attr-defined]
        assert "Prohibition" in fact.value  # type: ignore[attr-defined]


# the decades the cross-check covers, derived from the arc registry rather
# than restated, so a decade added to the arc is checked without a test edit
_ARC_DECADES = frozenset(curation.ARC_BY_SLUG["ethanol-per-capita"].fact_ids)
_CHECKED = sorted(_ARC_DECADES - RANGE_ANCHORED - GAP_DECADES)


@pytest.mark.parametrize("decade", _CHECKED)
def test_card_value_matches_the_series(decade: str) -> None:
    """Each single-year card carries exactly the series value for its year."""
    fact = _facts()[decade]
    series = load_series(DATA)[SERIES_ID]
    year = fact.price_year  # type: ignore[attr-defined]
    assert year is not None, f"{decade}: a single-year card must name its year"
    assert year in series.values, f"{decade}: year {year} is not in the series"
    assert fact.quantity == pytest.approx(series.values[year]), (  # type: ignore[attr-defined]
        f"{decade}: card says {fact.quantity}, series says {series.values[year]}"  # type: ignore[attr-defined]
    )


@pytest.mark.parametrize("decade", sorted(RANGE_ANCHORED))
def test_range_anchored_cards_are_exempt_for_a_stated_reason(decade: str) -> None:
    """The exemption is asserted, so it cannot quietly widen.

    A range card names its range in the value and carries no ``price_year``;
    if one ever grew a ``price_year`` it would belong in the cross-check above
    instead of here.
    """
    fact = _facts()[decade]
    assert fact.price_year is None  # type: ignore[attr-defined]
    assert fact.quantity is not None  # type: ignore[attr-defined]
    assert "average)" in fact.value  # type: ignore[attr-defined]
    series = load_series(DATA)[SERIES_ID]
    assert not any(
        y for y in series.values if str(y)[:3] == decade[:3]
    ), f"{decade}: the series now covers this decade — the exemption is stale"


def test_the_source_declares_content_markers() -> None:
    """A 200 OK is not proof the URL still serves the table (WI-023).

    The '(Prohibition)' marker is the load-bearing one: if NIAAA ever
    republished with those years backfilled, the link check would redden
    rather than the museum quietly citing a document that no longer says what
    the cards say it says.
    """
    raw = tomllib.loads((DATA / "sources.toml").read_text())
    source = next(s for s in raw["source"] if s["id"] == "niaaa-surveillance-122")
    assert "(Prohibition)" in source["expect"]
    assert "Apparent per capita ethanol consumption" in source["expect"]
