"""Tests for the cross-decade comparator (Plan 003 WI-4)."""

from __future__ import annotations

from pathlib import Path

import pytest

from vitrine.compare import compare_item
from vitrine.loader import load_corpus
from vitrine.model import (
    Basis,
    Corpus,
    Fact,
    Measure,
    Panel,
    Room,
    Source,
    Tier,
)

DATA = Path(__file__).parent.parent / "data"


def _income_room(decade: str, source_id: str, price_year: int = 0) -> Room:
    """A room with a priced fact + an income anchor, for caveat tests."""
    yr = price_year or int(decade[:4])
    price = Fact(
        id=f"us-{decade}-thing", panel=Panel.WORK_BUYS, label="A thing",
        value="$100", unit="USD", source=source_id, tier=Tier.A,
        amount_minor=10000, currency="USD", price_year=int(decade[:4]), basis=Basis.TOTAL,
    )
    income = Fact(
        id=f"us-{decade}-income", panel=Panel.BUDGET, label="Income",
        value="$1000", unit="USD/yr", source=source_id, tier=Tier.A,
        amount_minor=100000, currency="USD", price_year=yr, basis=Basis.ANNUAL,
    )
    return Room(
        country="us", decade=decade, facts=(price, income),
        income_anchor=income.id,
    )


def _corpus(rooms: tuple[Room, ...], sources: dict[str, Source]) -> Corpus:
    return Corpus(sources=sources, assumptions={}, rooms=rooms)


_MONEY = Source(
    id="money", title="T", publisher="P", year=2000, url="u",
    population="families, money income", measure=Measure.MONEY_INCOME,
)
_SURVEY = Source(
    id="survey", title="T", publisher="P", year=1901, url="u",
    population="wage-earner families, survey", measure=Measure.SURVEY_FAMILY_INCOME,
)


def test_compare_flags_mixed_income_concept() -> None:
    corpus = _corpus(
        (_income_room("1900s", "survey"), _income_room("1950s", "money")),
        {"survey": _SURVEY, "money": _MONEY},
    )
    comparison = compare_item(
        corpus, "A thing, share of income",
        {"1900s": "us-1900s-thing", "1950s": "us-1950s-thing"},
    )
    assert len(comparison.points) == 2
    assert any("income concept" in c.lower() for c in comparison.caveats)


def test_compare_no_caveat_when_income_concept_shared() -> None:
    corpus = _corpus(
        (_income_room("1950s", "money"), _income_room("2020s", "money")),
        {"money": _MONEY},
    )
    comparison = compare_item(
        corpus, "A thing, share of income",
        {"1950s": "us-1950s-thing", "2020s": "us-2020s-thing"},
    )
    assert comparison.caveats == ()


def test_compare_flags_wide_year_gap() -> None:
    corpus = _corpus(
        (_income_room("1940s", "money", price_year=1932),),  # 1940 price vs 1932 anchor
        {"money": _MONEY},
    )
    comparison = compare_item(
        corpus, "A thing", {"1940s": "us-1940s-thing"},
    )
    assert any("years" in c.lower() for c in comparison.caveats)


def test_compare_median_home_across_decades() -> None:
    corpus = load_corpus(DATA)
    comparison = compare_item(
        corpus,
        "A median home, in hours of work",
        {
            "1950s": "us-1950s-median-home-value",
            "2020s": "us-2020s-median-home-value",
        },
    )
    assert comparison.label == "A median home, in hours of work"
    decades = [p.decade for p in comparison.points]
    assert "1950s" in decades
    assert "2020s" in decades
    assert "1900s" not in decades


def test_compare_skips_missing_fact() -> None:
    corpus = load_corpus(DATA)
    comparison = compare_item(
        corpus,
        "A new car, in hours of work",
        {"1970s": "us-1970s-car-price", "2020s": "us-2020s-no-such-fact"},
    )
    decades = [p.decade for p in comparison.points]
    assert "1970s" in decades
    assert "2020s" not in decades


def test_compare_includes_verified_price_and_skips_factory_totals() -> None:
    """A factory count and wholesale total are not a source-bound retail price."""
    corpus = load_corpus(DATA)
    comparison = compare_item(
        corpus,
        "A new car, in hours of work",
        {"1910s": "us-1910s-car-price", "1970s": "us-1970s-car-price"},
    )
    decades = [p.decade for p in comparison.points]
    assert "1910s" not in decades
    assert "1970s" in decades


def test_compare_withdrawn_1950_car_price_keeps_archival_fact_without_point() -> None:
    """Factory sales counts and wholesale values do not establish a car price."""
    corpus = load_corpus(DATA)
    room = next(r for r in corpus.rooms if r.slug == "us-1950s")
    fact = next(f for f in room.facts if f.id == "us-1950s-car-price")
    assert fact.amount_minor is None
    assert fact.source == "statab-1953-car-factory-sales"
    assert fact.source in corpus.sources
    assert "wholesale" in fact.value.lower()
    comparison = compare_item(
        corpus,
        "A new car, in hours of work",
        {"1950s": fact.id, "1970s": "us-1970s-car-price"},
    )
    assert [point.decade for point in comparison.points] == ["1970s"]


def test_compare_1900s_has_both_anchors() -> None:
    """Plan 013: the 1900s now has both wage_anchor and income_anchor, so
    both hours_to_afford and pct_of_income are computed."""
    corpus = load_corpus(DATA)
    comparison = compare_item(
        corpus,
        "Annual income, as share of income",
        {"1900s": "us-1900s-annual-family-income"},
    )
    assert len(comparison.points) == 1
    point = comparison.points[0]
    assert point.decade == "1900s"
    assert point.afford.hours_to_afford is not None  # wage anchor now present
    assert point.afford.pct_of_income is not None


def test_compare_tier_inheritance_weakest_wins() -> None:
    """The historical wage reconstruction limits this affordability estimate."""
    corpus = load_corpus(DATA)
    comparison = compare_item(
        corpus,
        "A new car, in hours of work",
        {"1900s": "us-1900s-car-price"},
    )
    assert len(comparison.points) == 1
    point = comparison.points[0]
    assert point.afford.tier == Tier.D


def test_compare_2020s_home_tier_a() -> None:
    """2020s home: price Tier A, wage Tier A, income Tier A → weakest is A."""
    corpus = load_corpus(DATA)
    comparison = compare_item(
        corpus,
        "A median home, in hours of work",
        {"2020s": "us-2020s-median-home-value"},
    )
    assert len(comparison.points) == 1
    point = comparison.points[0]
    assert point.afford.tier == Tier.A


def test_compare_1970s_car_hours() -> None:
    """The verified $3,543 ORNL car price uses the $3.23 hourly wage anchor."""
    corpus = load_corpus(DATA)
    comparison = compare_item(
        corpus,
        "A new car, in hours of work",
        {"1970s": "us-1970s-car-price"},
    )
    assert len(comparison.points) == 1
    point = comparison.points[0]
    assert point.afford.hours_to_afford is not None
    assert point.afford.hours_to_afford == pytest.approx(354300 / 323, rel=1e-6)
    assert point.afford.hours_to_afford == pytest.approx(1096.9, abs=0.1)


def test_compare_1970s_car_pct_of_income() -> None:
    """The $3,543 price uses the $11,170 four-person median income anchor."""
    corpus = load_corpus(DATA)
    comparison = compare_item(
        corpus,
        "A new car, in hours of work",
        {"1970s": "us-1970s-car-price"},
    )
    assert len(comparison.points) == 1
    point = comparison.points[0]
    assert point.afford.pct_of_income is not None
    assert point.afford.pct_of_income == pytest.approx(354300 / 1117000 * 100, rel=1e-6)
    assert point.afford.pct_of_income == pytest.approx(31.7, abs=0.1)


def test_compare_1950s_home_values() -> None:
    """$7,354 / $1.32/hr ≈ 5,571 hours; $7,354 / $3,675 ≈ 200.1%."""
    corpus = load_corpus(DATA)
    comparison = compare_item(
        corpus,
        "A median home, in hours of work",
        {"1950s": "us-1950s-median-home-value"},
    )
    assert len(comparison.points) == 1
    point = comparison.points[0]
    assert point.afford.hours_to_afford is not None
    assert point.afford.hours_to_afford == pytest.approx(735400 / 132, rel=1e-6)
    assert point.afford.pct_of_income is not None
    assert point.afford.pct_of_income == pytest.approx(735400 / 367500 * 100, rel=1e-6)
    assert point.afford.pct_of_income == pytest.approx(200.1, abs=0.1)


def test_compare_2020s_home_values() -> None:
    """$360,600 / $30.12/hr ≈ 11,972 hours; $360,600 / $139,900 ≈ 257.8%."""
    corpus = load_corpus(DATA)
    comparison = compare_item(
        corpus,
        "A median home, in hours of work",
        {"2020s": "us-2020s-median-home-value"},
    )
    assert len(comparison.points) == 1
    point = comparison.points[0]
    assert point.afford.hours_to_afford is not None
    assert point.afford.hours_to_afford == pytest.approx(36060000 / 3012, rel=1e-6)
    assert point.afford.pct_of_income is not None
    assert point.afford.pct_of_income == pytest.approx(36060000 / 13990000 * 100, rel=1e-6)
    assert point.afford.pct_of_income == pytest.approx(257.8, abs=0.1)


def test_compare_points_ordered_by_decade() -> None:
    corpus = load_corpus(DATA)
    comparison = compare_item(
        corpus,
        "A median home, in hours of work",
        {
            "2020s": "us-2020s-median-home-value",
            "1950s": "us-1950s-median-home-value",
        },
    )
    decades = [p.decade for p in comparison.points]
    assert decades == sorted(decades)


def test_compare_anchor_note_carries_populations() -> None:
    corpus = load_corpus(DATA)
    comparison = compare_item(
        corpus,
        "A median home, in hours of work",
        {"1950s": "us-1950s-median-home-value"},
    )
    assert len(comparison.points) == 1
    point = comparison.points[0]
    assert "manufacturing" in point.afford.anchor_note.lower()
    assert "families" in point.afford.anchor_note.lower()


def test_compare_empty_fact_ids() -> None:
    corpus = load_corpus(DATA)
    comparison = compare_item(corpus, "Nothing", {})
    assert comparison.points == ()


def test_comparison_point_is_frozen() -> None:
    corpus = load_corpus(DATA)
    comparison = compare_item(
        corpus,
        "A new car, in hours of work",
        {"1970s": "us-1970s-car-price"},
    )
    point = comparison.points[0]
    with pytest.raises((AttributeError, TypeError)):
        point.decade = "1800s"  # type: ignore[misc]


def test_comparison_is_frozen() -> None:
    corpus = load_corpus(DATA)
    comparison = compare_item(corpus, "X", {})
    with pytest.raises((AttributeError, TypeError)):
        comparison.label = "Y"  # type: ignore[misc]
