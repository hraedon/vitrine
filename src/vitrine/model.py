"""The normalized fact model — see docs/fact-model.md, the design spine.

Everything the site displays is a projection of these types. ``Tier`` and
``Panel`` are closed sets: every dispatch over them must end in
``typing.assert_never`` so that adding a variant breaks the build at each
unhandled site.
"""

from __future__ import annotations

import enum
import re
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
    MONTHLY = "monthly"  # a monthly figure (¥29,169/mo)
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
    # income *after* cash benefits and direct tax, per household (UK ETB tables).
    # Deliberately distinct from MONEY_INCOME, which is gross: dividing a price by
    # a post-tax denominator in one room and a pre-tax one in another and calling
    # both "share of income" is the exact juxtaposition this enum exists to refuse.
    DISPOSABLE_HOUSEHOLD_INCOME = "disposable_household_income"
    # ── wage-axis denominators (hours-to-afford; Basis.HOURLY) ──
    HOURLY_EARNINGS = "hourly_earnings"  # avg hourly earnings, production/nonsupervisory workers
    # the *median* hourly pay of all employee jobs (UK ASHE). A median and a mean
    # of the same population are different statistics; keeping them apart stops an
    # hours axis being chained across the two without the splice being visible.
    MEDIAN_HOURLY_PAY = "median_hourly_pay"


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
    # Count of series at or above a threshold in a stated year (Plan 027
    # WI-6). Operands are *series*, not facts: the count is taken over the
    # listed series' values at ``at_year``, and the displayed value carries
    # both the count and how many listed series were tracked that year
    # ("12 of 18") so a changing record breadth cannot masquerade as a
    # changing count. numerator/denominator are unused for this op.
    COUNT_ABOVE = "count_above"


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
        case Measure.DISPOSABLE_HOUSEHOLD_INCOME:
            return "household disposable income (after cash benefits and direct tax)"
        case Measure.HOURLY_EARNINGS:
            return "average hourly earnings"
        case Measure.MEDIAN_HOURLY_PAY:
            return "median gross hourly pay"
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
            | Measure.DISPOSABLE_HOUSEHOLD_INCOME
        ):
            return Basis.ANNUAL
        case Measure.HOURLY_EARNINGS | Measure.MEDIAN_HOURLY_PAY:
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
        case Basis.MONTHLY:
            return "Monthly figure"
        case Basis.ANNUAL:
            return "Annual figure"
        case _:
            assert_never(basis)


def normalized_unit(unit: str) -> str:
    """A fact's ``unit`` string canonicalized for comparability checks.

    QUANTITY_RATIO derivations divide two quantities, which is only
    meaningful when both measure the same dimension; the gate compares
    normalized unit strings so trivial formatting differences (letter case,
    whitespace runs) are not treated as a dimension difference, while a real
    mismatch (hours per week ÷ CPI index points) is a red build.
    """
    return " ".join(unit.split()).casefold()


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
    expect: tuple[str, ...] = ()  # content markers scripts/link_check.py verifies
    # against the served document (WI-023: a 200 OK is not proof the URL
    # serves the described document — see the f08a/f08ar incident)


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
    numerator: str = ""  # Fact.id in this room or another room (cross-room, WI-5);
    # empty for COUNT_ABOVE, whose operands are series
    denominator: str = ""  # Fact.id in this room or another room (cross-room, WI-5);
    # empty for INFLATE (unused) and COUNT_ABOVE (series operands)
    precision: int = 1  # decimal places in the rendered value
    notes: str = ""
    assumptions: tuple[str, ...] = field(default=())
    # INFLATE op (Plan 012): inflate numerator by a series ratio across years.
    # denominator is unused for INFLATE; the series provides the second input.
    inflate_series: str = ""  # series id whose values carry the CPI ratio
    inflate_from_year: int = 0  # base year in the series
    inflate_to_year: int = 0  # target year in the series
    # COUNT_ABOVE op (Plan 027 WI-6): count of listed series whose value at
    # ``at_year`` is >= ``threshold``. The candidate set is enumerated
    # explicitly — never a prefix convention — so a later series can only
    # enter the count through a visible diff. Series without a published
    # value at ``at_year`` are outside the count (and outside the tracked
    # total the value displays).
    count_series: tuple[str, ...] = ()  # candidate series ids, resolved by the gate
    threshold: float = 0.0  # inclusive lower bound, in the series' shared unit
    at_year: int = 0  # the year the count is taken at


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


# ── the docent layer (plan 016) ───────────────────────────────────────────────

# In essay prose, a number may appear only by binding to a fact:
# ``{fact:<id>}`` renders the fact's as-authored value plus its tier chip;
# ``{fact:<id>:label}`` renders the label. The numeral gate in ``check``
# strips these before scanning — a bare numeral in prose is a red build.
INTERPOLATION_RE = re.compile(r"\{fact:([a-z]+-[a-z0-9]+-[a-z0-9-]+)(?::(label))?\}")


class BlockKind(enum.Enum):
    """The shape of one essay block — closed set."""

    PROSE = "prose"  # docent copy; every numeral bound to a fact
    CHART = "chart"  # exactly one of arc / group / metric, resolved at build


@dataclass(frozen=True, slots=True)
class EssayBlock:
    """One block of a docent essay: prose, or a referenced exhibit chart."""

    kind: BlockKind
    text: str = ""  # prose copy (PROSE blocks only)
    arc: str = ""  # corridor arc slug (CHART: exactly one of arc/group/metric)
    group: str = ""  # arc-group slug
    metric: str = ""  # affordability metric slug


@dataclass(frozen=True, slots=True)
class Essay:
    """A curated docent tour: titled prose blocks interleaved with charts."""

    slug: str
    title: str
    standfirst: str
    blocks: tuple[EssayBlock, ...]


@dataclass(frozen=True, slots=True)
class Corpus:
    """Everything under data/: the museum, before projection."""

    sources: dict[str, Source]
    assumptions: dict[str, Assumption]
    rooms: tuple[Room, ...]
    essays: tuple[Essay, ...] = field(default=())
