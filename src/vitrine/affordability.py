"""The affordability derivation — the one place cross-fact division happens.

See plan 003: hours-to-afford (price / hourly wage) is the inflation-free
primary axis; share-of-income (price / annual income) is the secondary axis.
Both are computed here from structured minor-unit amounts, never hand-authored.
The result carries the weakest input tier so comparisons never overstate their
confidence.
"""

from __future__ import annotations

from dataclasses import dataclass

from vitrine.model import Basis, Fact, Measure, Tier


@dataclass(frozen=True, slots=True)
class Affordability:
    """Derived affordability figures for a priced fact."""

    hours_to_afford: float | None  # price / hourly wage
    pct_of_income: float | None  # price / annual income * 100
    tier: Tier  # weakest of the inputs used
    anchor_note: str  # population(s) behind the anchors, verbatim
    hours_measure: Measure | None = None  # what the wage denominator measures (iff hours computed)
    pct_measure: Measure | None = None  # what the income denominator measures (iff pct computed)
    year_gap: int | None = None  # largest |price_year - anchor_year| among used anchors


def _weakest(*tiers: Tier) -> Tier:
    return max(tiers, key=lambda t: t.value)


def _year_gap(price: Fact, anchor: Fact) -> int | None:
    if price.price_year is None or anchor.price_year is None:
        return None
    return abs(price.price_year - anchor.price_year)


def afford(
    price: Fact,
    wage: Fact | None = None,
    income: Fact | None = None,
    wage_population: str = "",
    income_population: str = "",
    wage_measure: Measure | None = None,
    income_measure: Measure | None = None,
) -> Affordability:
    """Compute affordability figures from a priced fact and its anchors.

    Pure: the caller passes anchor population strings and measures so this
    function needs no Source registry lookup.  Returns ``None`` for any figure
    whose inputs are absent or have the wrong basis.  ``year_gap`` carries the
    largest gap between the price year and an anchor year actually used, so a
    within-"decade" but temporally distant division (e.g. a 1947 price against a
    1939 wage in the bifurcated 1940s) can be surfaced rather than hidden.
    """
    hours_to_afford: float | None = None
    pct_of_income: float | None = None
    hours_measure: Measure | None = None
    pct_measure: Measure | None = None
    used_tiers: list[Tier] = [price.tier]
    anchor_parts: list[str] = []
    gaps: list[int] = []

    if (
        price.amount_minor is not None
        and wage is not None
        and wage.amount_minor is not None
        and wage.basis is Basis.HOURLY
    ):
        hours_to_afford = price.amount_minor / wage.amount_minor
        hours_measure = wage_measure
        used_tiers.append(wage.tier)
        if wage_population:
            anchor_parts.append(wage_population)
        gap = _year_gap(price, wage)
        if gap is not None:
            gaps.append(gap)

    if (
        price.amount_minor is not None
        and income is not None
        and income.amount_minor is not None
        and income.basis is Basis.ANNUAL
    ):
        pct_of_income = price.amount_minor / income.amount_minor * 100
        pct_measure = income_measure
        used_tiers.append(income.tier)
        if income_population:
            anchor_parts.append(income_population)
        gap = _year_gap(price, income)
        if gap is not None:
            gaps.append(gap)

    return Affordability(
        hours_to_afford=hours_to_afford,
        pct_of_income=pct_of_income,
        tier=_weakest(*used_tiers),
        anchor_note="; ".join(anchor_parts),
        hours_measure=hours_measure,
        pct_measure=pct_measure,
        year_gap=max(gaps) if gaps else None,
    )
