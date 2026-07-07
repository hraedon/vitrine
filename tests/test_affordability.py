"""Tests for the affordability derivation module."""

from __future__ import annotations

import pytest

from vitrine.affordability import afford
from vitrine.model import Basis, Fact, Panel, Tier, basis_label


def _fact(
    fact_id: str = "us-1950s-x",
    tier: Tier = Tier.A,
    amount_minor: int | None = None,
    currency: str = "",
    price_year: int | None = None,
    basis: Basis | None = None,
) -> Fact:
    return Fact(
        id=fact_id,
        panel=Panel.TABLE,
        label="L",
        value="V",
        unit="U",
        source="src-1",
        tier=tier,
        amount_minor=amount_minor,
        currency=currency,
        price_year=price_year,
        basis=basis,
    )


def test_cents_arithmetic_exactness() -> None:
    price = _fact(
        amount_minor=151100,
        currency="USD",
        price_year=1950,
        basis=Basis.TOTAL,
    )
    wage = _fact(
        fact_id="us-1950s-wage",
        amount_minor=132,
        currency="USD",
        price_year=1950,
        basis=Basis.HOURLY,
    )
    result = afford(price, wage=wage, wage_population="production workers")
    assert result.hours_to_afford is not None
    assert result.hours_to_afford == 151100 / 132
    assert result.hours_to_afford == pytest.approx(1144.6969, rel=1e-4)


def test_tier_inheritance_weakest_wins() -> None:
    price = _fact(
        tier=Tier.A,
        amount_minor=151100,
        currency="USD",
        price_year=1950,
        basis=Basis.TOTAL,
    )
    wage = _fact(
        fact_id="us-1950s-wage",
        tier=Tier.C,
        amount_minor=132,
        currency="USD",
        price_year=1950,
        basis=Basis.HOURLY,
    )
    result = afford(price, wage=wage)
    assert result.tier == Tier.C


def test_none_safe_price_only() -> None:
    price = _fact(tier=Tier.B)
    result = afford(price)
    assert result.hours_to_afford is None
    assert result.pct_of_income is None
    assert result.tier == Tier.B
    assert result.anchor_note == ""


def test_afford_with_wage_produces_hours_not_pct() -> None:
    price = _fact(
        amount_minor=151100,
        currency="USD",
        price_year=1950,
        basis=Basis.TOTAL,
    )
    wage = _fact(
        fact_id="us-1950s-wage",
        amount_minor=132,
        currency="USD",
        price_year=1950,
        basis=Basis.HOURLY,
    )
    result = afford(price, wage=wage, wage_population="production workers")
    assert result.hours_to_afford is not None
    assert result.pct_of_income is None
    assert result.anchor_note == "production workers"


def test_afford_with_income_produces_pct_not_hours() -> None:
    price = _fact(
        amount_minor=151100,
        currency="USD",
        price_year=1950,
        basis=Basis.TOTAL,
    )
    income = _fact(
        fact_id="us-1950s-income",
        amount_minor=331900,
        currency="USD",
        price_year=1950,
        basis=Basis.ANNUAL,
    )
    result = afford(price, income=income, income_population="all families")
    assert result.hours_to_afford is None
    assert result.pct_of_income is not None
    assert result.pct_of_income == pytest.approx(151100 / 331900 * 100)
    assert result.anchor_note == "all families"


def test_afford_with_both_anchors_produces_both() -> None:
    price = _fact(
        amount_minor=151100,
        currency="USD",
        price_year=1950,
        basis=Basis.TOTAL,
    )
    wage = _fact(
        fact_id="us-1950s-wage",
        amount_minor=132,
        currency="USD",
        price_year=1950,
        basis=Basis.HOURLY,
    )
    income = _fact(
        fact_id="us-1950s-income",
        amount_minor=331900,
        currency="USD",
        price_year=1950,
        basis=Basis.ANNUAL,
    )
    result = afford(
        price,
        wage=wage,
        income=income,
        wage_population="production workers",
        income_population="all families",
    )
    assert result.hours_to_afford is not None
    assert result.pct_of_income is not None
    assert result.tier == Tier.A
    assert "production workers" in result.anchor_note
    assert "all families" in result.anchor_note


def test_total_price_with_annual_wage_does_not_produce_hours() -> None:
    price = _fact(
        amount_minor=151100,
        currency="USD",
        price_year=1950,
        basis=Basis.TOTAL,
    )
    annual_wage = _fact(
        fact_id="us-1950s-annual",
        amount_minor=266500,
        currency="USD",
        price_year=1950,
        basis=Basis.ANNUAL,
    )
    result = afford(price, wage=annual_wage)
    assert result.hours_to_afford is None
    assert result.pct_of_income is None


def test_tier_weakest_of_three() -> None:
    price = _fact(
        tier=Tier.A,
        amount_minor=151100,
        currency="USD",
        price_year=1950,
        basis=Basis.TOTAL,
    )
    wage = _fact(
        fact_id="us-1950s-wage",
        tier=Tier.B,
        amount_minor=132,
        currency="USD",
        price_year=1950,
        basis=Basis.HOURLY,
    )
    income = _fact(
        fact_id="us-1950s-income",
        tier=Tier.D,
        amount_minor=331900,
        currency="USD",
        price_year=1950,
        basis=Basis.ANNUAL,
    )
    result = afford(price, wage=wage, income=income)
    assert result.tier == Tier.D


def test_affordability_is_frozen() -> None:
    result = afford(_fact())
    with pytest.raises((AttributeError, TypeError)):
        result.hours_to_afford = 1.0  # type: ignore[misc]


def test_basis_label_assert_never_reachable() -> None:
    class FakeBasis:
        pass

    with pytest.raises(AssertionError):
        basis_label(FakeBasis())  # type: ignore[arg-type]


def test_basis_label_returns_labels() -> None:
    assert basis_label(Basis.TOTAL) == "One-time price"
    assert basis_label(Basis.HOURLY) == "Hourly rate"
    assert basis_label(Basis.WEEKLY) == "Weekly figure"
    assert basis_label(Basis.ANNUAL) == "Annual figure"
