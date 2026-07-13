"""The normalized fact model — see docs/fact-model.md, the design spine.

Everything the site displays is a projection of these types. ``Tier`` and
``Panel`` are closed sets: every dispatch over them must end in
``typing.assert_never`` so that adding a variant breaks the build at each
unhandled site.
"""

from __future__ import annotations

import enum
from dataclasses import dataclass, field
from typing import assert_never


class Tier(enum.Enum):
    """Confidence tier for a fact."""

    A = "A"  # official statistical series for the stated population
    B = "B"  # official microdata; statistic computed by this project
    C = "C"  # reconstructed from contemporaneous surveys of a proxy population
    D = "D"  # scholarly estimate or narrative; no contemporaneous survey


class Panel(enum.Enum):
    """The six-panel room skeleton, identical in every room."""

    HOME = "home"
    BUDGET = "budget"
    TABLE = "table"
    DAY = "day"
    DIFFUSION = "diffusion"
    WORK_BUYS = "work-buys"


class Basis(enum.Enum):
    """What a structured amount is measured against — closed set."""

    TOTAL = "total"      # a one-time price ($1,511 for a car)
    HOURLY = "hourly"    # a wage rate ($1.32/hr)
    WEEKLY = "weekly"    # a weekly figure ($53.29/wk)
    ANNUAL = "annual"    # an annual figure ($3,319/yr)


class Measure(enum.Enum):
    """What economic quantity an affordability *anchor* measures — closed set.

    Same ``Basis`` (hourly vs annual) is necessary but *not sufficient* to chain
    two anchors into one cross-decade series. Dividing a price by wages-and-
    salaries in one decade and by total money income in another and calling both
    "share of income" is a lie by juxtaposition even though both are annual. The
    comparator refuses to present a series as comparable unless every point
    shares a Measure. See docs/fact-model.md "Comparability".
    """

    # ── income-axis denominators (share-of-income; Basis.ANNUAL) ──
    MONEY_INCOME = "money_income"  # total money income (CPS: Census F-8/P-60/FRED-MEFAIN)
    WAGES_SALARIES = "wages_salaries"  # wages and salaries only — narrower than money income
    SURVEY_FAMILY_INCOME = "survey_family_income"  # family income from a period survey (pre-CPS)
    CONSUMPTION = "consumption"  # consumption expenditure as an income proxy (v2 rooms)
    # ── wage-axis denominator (hours-to-afford; Basis.HOURLY) ──
    HOURLY_EARNINGS = "hourly_earnings"  # avg hourly earnings, production/nonsupervisory workers


class DerivedOp(enum.Enum):
    """How a derived fact combines its operands — closed set.

    Derivations are code (fact-model.md): a curator authors the *structure*
    (operand fact ids and an op), never the resulting number. Both operands
    must be structured facts in the same room with the same currency.
    """

    RATIO = "ratio"    # numerator / denominator
    PCT_OF = "pct_of"  # numerator / denominator * 100
    INFLATE = "inflate"  # numerator x series[to_year] / series[from_year] (Plan 012)
    PRODUCT = "product"  # numerator.amount_minor * denominator.quantity -> minor units (WI-5)
    QUANTITY_RATIO = "quantity_ratio"  # numerator.quantity / denominator.quantity (WI-5)


def weakest_tier(*tiers: Tier) -> Tier:
    """The weakest (least confident) of the given tiers — A < B < C < D."""
    return max(tiers, key=lambda t: t.value)


def tier_label(tier: Tier) -> str:
    """Visitor-facing description of a confidence tier."""
    match tier:
        case Tier.A:
            return "Official series"
        case Tier.B:
            return "Official microdata (computed)"
        case Tier.C:
            return "Reconstructed from period surveys"
        case Tier.D:
            return "Scholarly estimate"
        case _:
            assert_never(tier)


def panel_title(panel: Panel) -> str:
    """Visitor-facing title of a room panel."""
    match panel:
        case Panel.HOME:
            return "The home"
        case Panel.BUDGET:
            return "The budget"
        case Panel.TABLE:
            return "The table"
        case Panel.DAY:
            return "The day"
        case Panel.DIFFUSION:
            return "What had arrived"
        case Panel.WORK_BUYS:
            return "A day's work buys"
        case _:
            assert_never(panel)


def measure_label(measure: Measure) -> str:
    """Visitor-facing description of what an anchor denominator measures."""
    match measure:
        case Measure.MONEY_INCOME:
            return "total money income"
        case Measure.WAGES_SALARIES:
            return "wages and salaries only"
        case Measure.SURVEY_FAMILY_INCOME:
            return "family income (period cost-of-living survey)"
        case Measure.CONSUMPTION:
            return "consumption expenditure"
        case Measure.HOURLY_EARNINGS:
            return "average hourly earnings"
        case _:
            assert_never(measure)


def measure_axis(measure: Measure) -> Basis:
    """The anchor ``Basis`` a Measure belongs to — closed dispatch.

    Income measures denominate the share-of-income axis (an ANNUAL anchor);
    HOURLY_EARNINGS denominates the hours-to-afford axis (an HOURLY anchor).
    Adding a Measure variant breaks the build here until its axis is declared.
    """
    match measure:
        case (
            Measure.MONEY_INCOME
            | Measure.WAGES_SALARIES
            | Measure.SURVEY_FAMILY_INCOME
            | Measure.CONSUMPTION
        ):
            return Basis.ANNUAL
        case Measure.HOURLY_EARNINGS:
            return Basis.HOURLY
        case _:
            assert_never(measure)


def basis_label(basis: Basis) -> str:
    """Visitor-facing description of a structured amount's basis."""
    match basis:
        case Basis.TOTAL:
            return "One-time price"
        case Basis.HOURLY:
            return "Hourly rate"
        case Basis.WEEKLY:
            return "Weekly figure"
        case Basis.ANNUAL:
            return "Annual figure"
        case _:
            assert_never(basis)


@dataclass(frozen=True, slots=True)
class Source:
    """An entry in the global source registry (data/sources.toml)."""

    id: str
    title: str
    publisher: str
    year: int
    url: str
    population: str  # who was actually measured — the anti-composite field
    notes: str = ""
    short_cite: str = ""  # brief inline citation for footnote display
    measure: Measure | None = None  # what it measures, iff used as an affordability anchor


@dataclass(frozen=True, slots=True)
class Assumption:
    """An entry in the assumption ledger (data/assumptions.toml)."""

    id: str
    title: str
    statement: str


@dataclass(frozen=True, slots=True)
class Fact:
    """One claim, one source, one tier — the atomic exhibit unit."""

    id: str
    panel: Panel
    label: str
    value: str  # display value as authored; see fact-model.md on structured numerics
    unit: str
    source: str  # Source.id
    tier: Tier
    notes: str = ""
    assumptions: tuple[str, ...] = field(default=())
    amount_minor: int | None = None  # integer minor units (cents) — no float drift
    currency: str = ""  # "USD"; required iff amount_minor is set
    price_year: int | None = None  # year the amount is quoted in
    basis: Basis | None = None  # required iff amount_minor is set
    quantity: float | None = None  # headline numeric for chart projection; must
    # appear verbatim in ``value`` (gate-enforced) — a transcription of the
    # displayed datum, never a new number. Unit semantics stay in ``unit``.


@dataclass(frozen=True, slots=True)
class DerivedFact:
    """A fact whose displayed value is computed by repo code, never authored.

    The tier is computed too (weakest operand tier) — a curator cannot badge
    a derivation stronger than its inputs. See plan 006.
    """

    id: str
    panel: Panel
    label: str
    unit: str
    op: DerivedOp
    numerator: str  # Fact.id in the same room; must be structured
    denominator: str  # Fact.id in the same room; must be structured, non-zero
    precision: int = 1  # decimal places in the rendered value
    notes: str = ""
    assumptions: tuple[str, ...] = field(default=())
    # INFLATE op (Plan 012): inflate numerator by a series ratio across years.
    # denominator is unused for INFLATE; the series provides the second input.
    inflate_series: str = ""  # series id whose values carry the CPI ratio
    inflate_from_year: int = 0  # base year in the series
    inflate_to_year: int = 0  # target year in the series


@dataclass(frozen=True, slots=True)
class Room:
    """One (country, decade) exhibit room."""

    country: str  # lowercase slug: us, uk, pl, ru, cn, in, jp
    decade: str  # "1890s" … "2020s"
    facts: tuple[Fact, ...]
    derived: tuple[DerivedFact, ...] = field(default=())
    wage_anchor: str = ""  # fact id → a HOURLY basis fact in this room
    income_anchor: str = ""  # fact id → an ANNUAL basis fact in this room
    data_as_of: str = ""  # "data as of" year for the current (ongoing) decade

    @property
    def slug(self) -> str:
        return f"{self.country}-{self.decade}"


@dataclass(frozen=True, slots=True)
class Corpus:
    """Everything under data/: the museum, before projection."""

    sources: dict[str, Source]
    assumptions: dict[str, Assumption]
    rooms: tuple[Room, ...]
