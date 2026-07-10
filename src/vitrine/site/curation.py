"""Editorial curation for the three surfaces (Plan 007).

This module authors *structure only*: which fact ids form a cross-decade arc,
which artifact glyph maps to which fact in which room, which facts carry a
parseable expenditure composition. Values, tiers and geometry all come from
the corpus at build time; a registry entry whose fact lacks a structured
quantity renders as a gap, and an entry naming a fact the corpus doesn't have
is a red build (mark coverage).
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True, slots=True)
class Arc:
    """One cross-decade fact family, charted in the corridors."""

    slug: str
    label: str
    unit: str
    fact_ids: dict[str, str]  # decade → fact id
    falling: bool = False  # falling metrics render in copper
    caveats: tuple[str, ...] = field(default=())
    series_id: str = ""  # plan 010: annual series backing this arc, if any
    # A fact may have an honest quantity that is not comparable on this arc's
    # axis.  Keep the fact in the registry (and render a linked gap mark), but
    # never turn that quantity into geometry.  This is distinct from a fact
    # whose quantity is absent: the source has a number; the chart refuses the
    # splice.
    plot_gaps: frozenset[str] = field(default_factory=frozenset)


@dataclass(frozen=True, slots=True)
class ArcGroup:
    """Several related arcs rendered on one shared axis."""

    slug: str
    label: str
    unit: str
    members: tuple[tuple[str, str, str], ...]  # (arc slug, legend label, color role)
    caveats: tuple[str, ...] = field(default=())


def _ids(pattern: str, decades: str) -> dict[str, str]:
    return {d + "0s": pattern.format(decade=d + "0s") for d in decades.split()}


ARCS: tuple[Arc, ...] = (
    Arc(
        "life-expectancy",
        "Life expectancy at birth",
        "years (all races, both sexes)",
        _ids("us-{decade}-life-expectancy", "190 191 192 193 194 196 197 198 199 200 201 202"),
        caveats=(
            "Decades before the 1960s published white-only male/female life tables "
            "with no all-races total — the placard carries the sexed figures and "
            "the chart renders the gap rather than a spliced concept.",
        ),
    ),
    Arc(
        "infant-mortality",
        "Infant mortality",
        "deaths under age 1 per 1,000 live births",
        _ids("us-{decade}-infant-mortality", "190 195 196 197 198 199 200 201 202"),
        falling=True,
    ),
    Arc(
        "poverty-rate",
        "People in poverty",
        "% below the official poverty line",
        _ids("us-{decade}-poverty-rate", "196 197 198 199 200 201 202"),
        falling=True,
        caveats=("The official poverty series begins in 1959 — earlier decades have no line.",),
    ),
    Arc(
        "homeownership",
        "Homeownership",
        "% of occupied housing units owner-occupied",
        {
            "1900s": "us-1900s-homeownership-gap",
            "1910s": "us-1910s-homeownership",
            "1920s": "us-1920s-homeownership",
            "1930s": "us-1930s-homeownership",
            "1940s": "us-1940s-homeownership-rate",
            "1950s": "us-1950s-homeownership-rate",
            "1960s": "us-1960s-homeownership-rate",
            "1970s": "us-1970s-homeownership",
            "1980s": "us-1980s-homeownership",
            "1990s": "us-1990s-homeownership",
            "2000s": "us-2000s-homeownership",
            "2010s": "us-2010s-homeownership",
            "2020s": "us-2020s-homeownership-rate",
        },
    ),
    Arc(
        "plumbing",
        "Complete plumbing",
        "% of homes with complete plumbing",
        _ids("us-{decade}-plumbing", "194 195 196 197 198 199 200"),
    ),
    Arc(
        "television",
        "Television",
        "% of households",
        {
            "1940s": "us-1940s-no-television",
            "1950s": "us-1950s-tv-diffusion",
            "1960s": "us-1960s-television",
        },
    ),
    Arc(
        "telephone",
        "Household landline telephone",
        "% of households",
        {
            "1900s": "us-1900s-diffusion",
            "1910s": "us-1910s-telephone",
            "1920s": "us-1920s-telephone",
            "1930s": "us-1930s-telephone",
            "1940s": "us-1940s-telephone",
            "1950s": "us-1950s-telephone-automobile",
            "1960s": "us-1960s-telephone",
            "1970s": "us-1970s-telephone",
            "1980s": "us-1980s-telephone",
            "1990s": "us-1990s-telephone",
            "2020s": "us-2020s-phone-vehicle-diffusion",
        },
        caveats=(
            "The 1900s source combines several technologies in one headline "
            "percentage, so its 5% is not plotted as a telephone datum.",
            "1910s–1930s sources counted telephones per 1,000 population, not "
            "households — those decades render as gaps rather than a unit splice.",
            "The 2020s fact leads with cell-phone adoption (92.7%), while the "
            "landline share is 20.1%; neither is spliced into the historical "
            "landline line.",
        ),
        plot_gaps=frozenset({"1900s", "2020s"}),
    ),
    Arc(
        "air-conditioning",
        "Air conditioning",
        "% of households with AC",
        _ids("us-{decade}-air-conditioning", "196 197 198 199 200 201 202"),
        caveats=(
            "The 1980s source bridges 1978 central-AC and 1993 total-AC figures — "
            "no single-decade datum, so the decade renders as a gap.",
        ),
    ),
    Arc(
        "cable-tv",
        "Cable television",
        "% of households with TV",
        _ids("us-{decade}-cable-tv", "198 199 200 201"),
        caveats=("The 2010s source reports subscriber counts amid cord-cutting, not a share.",),
    ),
    Arc(
        "computer",
        "Home computer",
        "% of households",
        _ids("us-{decade}-computer", "198 199"),
    ),
    Arc(
        "internet",
        "Internet at home",
        "% of households",
        {
            "1990s": "us-1990s-internet-households",
            "2000s": "us-2000s-internet",
            "2010s": "us-2010s-internet",
            "2020s": "us-2020s-internet-diffusion",
        },
        caveats=(
            "1990s–2010s sources report within-decade ranges; the placards carry "
            "them and the chart renders the gaps.",
        ),
    ),
    Arc(
        "radio",
        "Radio",
        "% of households",
        {
            "1920s": "us-1920s-radio-automobile",
            "1930s": "us-1930s-radio-automobile",
            "1950s": "us-1950s-radio-diffusion",
        },
    ),
    Arc(
        "vehicle",
        "Vehicle at home",
        "% of households with a vehicle",
        {
            "1960s": "us-1960s-vehicle-ownership",
            "1970s": "us-1970s-vehicle-ownership",
            "1980s": "us-1980s-vehicle-ownership",
            "1990s": "us-1990s-vehicle-ownership",
            "2000s": "us-2000s-vehicle-ownership",
            "2010s": "us-2010s-vehicle-ownership",
            "2020s": "us-2020s-vehicle-ownership",
        },
    ),
    Arc(
        "home-production-women",
        "Women's unpaid home production",
        "hours per week, prime-age women",
        _ids(
            "us-{decade}-home-production-women",
            "190 191 192 193 194 195 196 197 198 199 200 201",
        )
        | {"2020s": "us-2020s-home-production-splice"},
        falling=True,
        caveats=(
            "From 2010s onward the source is ATUS (all adults 15+, hrs/day, "
            "narrower 'household activities'), not Ramey (prime-age women 18-64, "
            "hrs/week, broader 'home production') — a concept splice. ATUS facts "
            "remain available in their rooms, but render as linked gaps on this "
            "weekly axis rather than as a false decline.",
        ),
        plot_gaps=frozenset({"2010s", "2020s"}),
    ),
    Arc(
        "home-production-men",
        "Men's unpaid home production",
        "hours per week, prime-age men",
        _ids(
            "us-{decade}-home-production-men",
            "190 191 192 193 194 195 196 197 198 199 200 201",
        )
        | {"2020s": "us-2020s-home-production-splice"},
        caveats=(
            "From 2010s onward the source is ATUS (all adults 15+, hrs/day, "
            "narrower 'household activities'), not Ramey (prime-age men 18-64, "
            "hrs/week, broader 'home production') — a concept splice. ATUS facts "
            "remain available in their rooms, but render as linked gaps on this "
            "weekly axis rather than as a false rise or decline.",
        ),
        plot_gaps=frozenset({"2010s", "2020s"}),
    ),
    Arc(
        "food-share",
        "Food's share of spending",
        "% of household expenditure",
        {
            "1900s": "us-1900s-food-share",
            "1950s": "us-1950s-food-basket",
            "1960s": "us-1960s-food-basket",
            "1970s": "us-1970s-food-basket",
            "1980s": "us-1980s-food-basket",
            "1990s": "us-1990s-food-basket",
            "2000s": "us-2000s-food-basket",
            "2010s": "us-2010s-food-basket",
            "2020s": "us-2020s-food-expenditure-share",
        },
        falling=True,
        caveats=(
            "Populations differ across the century — 1901 wage-earner families vs "
            "modern consumer units; every placard names who was measured.",
            "The 1950s point is the nearest available survey (CEX 1960–61), stated "
            "plainly rather than back-cast.",
        ),
    ),
    Arc(
        "weekly-hours",
        "Weekly hours, manufacturing",
        "hours per week, production workers",
        {
            "1900s": "us-1900s-weekly-hours",
            "1950s": "us-1950s-weekly-hours-manufacturing",
            "2020s": "us-2020s-weekly-hours-manufacturing",
        },
        falling=True,
    ),
    Arc(
        "cpi",
        "Consumer Price Index",
        "CPI-U level, 1982–84 = 100",
        _ids("us-{decade}-cpi", "195 197 198 199 200 201 202"),
        series_id="cpi-u",
    ),
    Arc(
        "home-size",
        "Median home size",
        "median sq ft, new single-family houses completed",
        {
            "1970s": "us-1970s-median-home-size",
            "1980s": "us-1980s-median-home-size",
            "1990s": "us-1990s-median-home-size",
            "2000s": "us-2000s-median-home-size",
            "2010s": "us-2010s-median-home-size",
            "2020s": "us-2020s-housing-characteristics",
        },
        caveats=(
            "1970s–2010s: new single-family houses completed (Census C-25/H-150). "
            "2020s: American Housing Survey, all housing stock — the median drops "
            "because the existing stock is older and smaller. The two series are "
            "not directly comparable; the placard names who was measured.",
        ),
    ),
)

ARC_BY_SLUG: dict[str, Arc] = {a.slug: a for a in ARCS}


# These two series answer one question and must share one scale.  Separate
# charts made the smaller men's series look visually comparable in magnitude
# to the women's series and hid the convergence that is the actual story.
ARC_GROUPS: tuple[ArcGroup, ...] = (
    ArcGroup(
        "home-production-by-sex",
        "Unpaid home production, women and men",
        "hours per week, prime-age adults (Ramey series)",
        (
            ("home-production-women", "Women", "copper"),
            ("home-production-men", "Men", "brass"),
        ),
        caveats=ARC_BY_SLUG["home-production-women"].caveats,
    ),
)

ARC_GROUP_BY_MEMBER: dict[str, ArcGroup] = {
    member_slug: group
    for group in ARC_GROUPS
    for member_slug, _label, _color in group.members
}


# ── budget composition (parseable "Category N.N%" facts) ─────────────────────

COMPOSITIONS: dict[str, str] = {
    "1900s": "us-1900s-expenditure-breakdown",
    "1970s": "us-1970s-expenditure-shares",
    "1980s": "us-1980s-expenditure-shares",
    "1990s": "us-1990s-expenditure-shares",
    "2000s": "us-2000s-expenditure-shares",
    "2010s": "us-2010s-expenditure-shares",
    "2020s": "us-2020s-expenditure-breakdown-4p",
}

# ── the room stage: artifact → decade → fact id ──────────────────────────────
# "diffusion" glyphs read their percentage from quantity (gap ring when the
# fact carries none); "stat" glyphs mark an amenity/fixture whose fact is not
# a share — drawn at full presence with no percentage.

STAGE_DIFFUSION: dict[str, dict[str, str]] = {
    "electricity": {
        "1910s": "us-1910s-electricity-gap",
        "1950s": "us-1950s-electricity-diffusion",
    },
    "radio": ARC_BY_SLUG["radio"].fact_ids,
    "television": ARC_BY_SLUG["television"].fact_ids,
    "telephone": ARC_BY_SLUG["telephone"].fact_ids,
    "refrigerator": {"1950s": "us-1950s-refrigerator-diffusion"},
    "plumbing": ARC_BY_SLUG["plumbing"].fact_ids,
    "air-conditioning": ARC_BY_SLUG["air-conditioning"].fact_ids,
    "cable": ARC_BY_SLUG["cable-tv"].fact_ids,
    "computer": ARC_BY_SLUG["computer"].fact_ids,
    "internet": ARC_BY_SLUG["internet"].fact_ids,
    "automobile": ARC_BY_SLUG["vehicle"].fact_ids,
    "heating": {"1950s": "us-1950s-central-heating-diffusion"},
}

STAGE_STATS: dict[str, dict[str, str]] = {
    "tenure": ARC_BY_SLUG["homeownership"].fact_ids,
    "rooms": {
        "1900s": "us-1900s-housing-rooms-rent",
        "2020s": "us-2020s-housing-characteristics",
    },
    "food": {
        "1900s": "us-1900s-food-basket",
        "1950s": "us-1950s-food-basket",
        "1960s": "us-1960s-food-basket",
        "1970s": "us-1970s-food-basket",
        "1980s": "us-1980s-food-basket",
        "1990s": "us-1990s-food-basket",
        "2000s": "us-2000s-food-basket",
        "2010s": "us-2010s-food-basket",
        "2020s": "us-2020s-food-prices",
    },
    "heating": {
        "1940s": "us-1940s-heating-fuel",
        "1950s": "us-1950s-heating-fuel",
        "1960s": "us-1960s-heating-fuel",
        "1970s": "us-1970s-heating-fuel",
        "1980s": "us-1980s-heating-fuel",
        "1990s": "us-1990s-heating-fuel",
        "2000s": "us-2000s-heating-fuel",
        "2010s": "us-2010s-heating-fuel",
        "2020s": "us-2020s-heating-fuel",
    },
    "refrigerator": {
        "1960s": "us-1960s-household-appliances",
        "1970s": "us-1970s-appliance-ownership",
        "1980s": "us-1980s-appliance-ownership",
    },
    "washing-machine": {
        "1960s": "us-1960s-household-appliances",
        "1970s": "us-1970s-appliance-ownership",
        "1980s": "us-1980s-appliance-ownership",
    },
}

# Median home size facts → decade → fact id; used for the home-scale stage
# and the floor-area annotation. Scales the house outline proportionally.
HOME_SIZE_FACTS: dict[str, str] = {
    "1970s": "us-1970s-median-home-size",
    "1980s": "us-1980s-median-home-size",
    "1990s": "us-1990s-median-home-size",
    "2000s": "us-2000s-median-home-size",
    "2010s": "us-2010s-median-home-size",
    "2020s": "us-2020s-housing-characteristics",
}

# Structural gaps that change how a whole room should be read deserve notice
# before the visitor reaches the individual gap placards. These are editorial
# summaries of committed gap facts, not new historical claims.
ROOM_GAP_BANNERS: dict[str, str] = {
    "1910s": (
        "Four core exhibits — income, housing, the food basket, and work-buys — "
        "lack a reliable national record for this room. Their gaps are shown, "
        "not reconstructed from neighboring decades."
    ),
    "1920s": (
        "Four core exhibits — income, housing, the food basket, and work-buys — "
        "lack a reliable national record for this room. Their gaps are shown, "
        "not reconstructed from neighboring decades."
    ),
    "1930s": (
        "Four core exhibits — income, housing, the food basket, and work-buys — "
        "lack a reliable national record for this room. Their gaps are shown, "
        "not reconstructed from neighboring decades."
    ),
    "1940s": (
        "The wartime record is structurally different: no Consumer Expenditure "
        "Survey covered the decade, while rationing and price controls make a "
        "peacetime-style food basket misleading. Both exhibits remain gaps."
    ),
}

# zone-note anchor positions on the cutaway, per palette slot
ZONE_NOTE_POS: dict[str, tuple[int, int]] = {
    "housing": (172, 218),
    # End before the air-conditioning ring at x=600.
    "apparel": (440, 218),
    "food": (172, 342),
    # Start to the right of the plumbing ring at x=460.
    "health": (520, 342),
    # The automobile sits at (700, 405); keep its budget annotation above the
    # mark rather than running through its ring and percentage label.
    "transport": (700, 360),
}

# ── affordability corridors (structured amounts + room anchors) ──────────────
# decade lists resolved against the corpus at build time; a decade whose fact
# is missing simply isn't a point (render the gap).

AFFORD_ITEMS: tuple[tuple[str, str, str], ...] = (
    # (slug, label, fact id pattern)
    ("median-home", "A median home", "us-{decade}-median-home-value"),
    ("new-car", "A new car", "us-{decade}-car-price"),
)

# Static caveats the dynamic measure-guard can't detect (Plan 011 WI-5). The
# car-price line mixes wholesale (pre-1970) and transaction (1970+) price
# methodologies — a step between points that the comparator sees as a price
# change is partly a concept change. Surfaced, not smoothed.
AFFORD_ITEM_CAVEATS: dict[str, tuple[str, ...]] = {
    "new-car": (
        "Pre-1970 car prices are wholesale averages; 1970+ are BEA transaction "
        "prices — the jump at 1970 partly reflects the methodology change, not "
        "only real price change.",
    ),
}

# ── the walkthrough (Plan 005's transect, on this plan's primitives) ─────────

WALKTHROUGH_STOPS: tuple[str, ...] = ("1900s", "1950s", "2020s")

# figure → decade → fact ids rendered as that figure's stat rows
WALKTHROUGH_PEOPLE: dict[str, dict[str, tuple[str, ...]]] = {
    "father": {
        "1900s": (
            "us-1900s-weekly-hours",
            "us-1900s-mens-weekly-wages",
            "us-1900s-life-expectancy",
        ),
        "1950s": (
            "us-1950s-weekly-hours-manufacturing",
            "us-1950s-hourly-earnings-manufacturing",
            "us-1950s-annual-earnings",
        ),
        "2020s": (
            "us-2020s-weekly-hours-manufacturing",
            "us-2020s-hourly-earnings",
            "us-2020s-life-expectancy",
        ),
    },
    "mother": {
        "1900s": (
            "us-1900s-home-production-women",
            "us-1900s-womens-weekly-wages",
        ),
        "1950s": (
            "us-1950s-home-production-women",
            "us-1950s-home-production-men",
        ),
        "2020s": (
            "us-2020s-home-production-splice",
            "us-2020s-time-use",
        ),
    },
    "children": {
        "1900s": ("us-1900s-infant-mortality",),
        "1950s": ("us-1950s-infant-mortality",),
        "2020s": ("us-2020s-infant-mortality",),
    },
}

# the walkthrough metric band: arcs projected onto the three stops
WALKTHROUGH_METRICS: tuple[str, ...] = (
    "home-production-women",
    "food-share",
    "weekly-hours",
    "life-expectancy",
    "infant-mortality",
)

# floor-area facts for the true-scale house; a stop without one renders the
# dashed reference outline and the words
WALKTHROUGH_FLOOR_AREA: dict[str, str] = {
    "1900s": "us-1900s-housing-rooms-rent",  # rooms counted, area not — a gap
    "2020s": "us-2020s-housing-characteristics",  # median 1,500 sq ft (AHS)
}


# ── affordability dashboard metrics (Plan 011) ───────────────────────────────
# Every metric is a ratio of two series (or a direct arc projection), computed
# by the renderer — never authored. A metric's coverage is the intersection of
# its numerator and denominator years; years missing on either side render as
# gaps (the "render the gap" ethos, extended to cross-decade metrics).

@dataclass(frozen=True, slots=True)
class Metric:
    """One affordability metric on the dashboard — a computed ratio over time.

    Ratio mode: ``numerator`` / ``denominator`` (each a tuple of series ids
    whose values merge; monetary series convert cents→dollars uniformly). A
    ``base_year`` re-scales the ratio so that year = 100 (an index).
    Direct mode: ``source_arc`` names an arc whose decade quantities plot
    as-is (for metrics with no annual series, e.g. food share).
    """

    slug: str
    label: str
    unit: str
    caption: str
    caveats: tuple[str, ...] = field(default=())
    numerator: tuple[str, ...] = field(default=())  # series ids (ratio mode)
    denominator: tuple[str, ...] = field(default=())  # series ids (ratio mode)
    numerator_scale: float = 1.0  # e.g. 52 for weekly→annual
    base_year: int | None = None  # if set, ratio normalized to 100 at this year
    percent: bool = False  # if True, ratio x 100 (share-of metrics)
    source_arc: str = ""  # arc slug whose decade quantities plot directly
    falling: bool = False  # falling metrics render in copper
    zero_baseline: bool = True  # False only for indices where zero has no meaning


AFFORDABILITY_METRICS: tuple[Metric, ...] = (
    Metric(
        "home-as-income-years",
        "A median home, in years of median income",
        "years of 4-person median family income",
        "Home values are decennial (1940–2000) then ACS (2005+); the line "
        "is sparse because that is the honest shape of the record before ACS.",
        numerator=("median-home-value-decennial", "median-home-value-acs"),
        denominator=("median-family-income-4p",),
        caveats=(
            "Pre-2005 home values are decennial census points only — the gaps "
            "between them are unknown, not interpolated.",
        ),
    ),
    Metric(
        "car-as-hours-of-work",
        "A new car, in hours of work",
        "hours of average hourly earnings (total private)",
        "The price line has only six transcribed points (the BEA transaction "
        "series' decade years); early-decade gaps render as gaps.",
        numerator=("new-car-price",),
        denominator=("hourly-earnings-total-private",),
        caveats=(
            "Pre-1970 car prices are wholesale averages; 1970+ are transaction "
            "prices — the jump at 1970 partly reflects methodology, not only "
            "real price change.",
        ),
    ),
    Metric(
        "single-earner-wage-coverage",
        "One manufacturing wage, as share of family income",
        "% of median (all) family income",
        "Weekly manufacturing earnings x 52 / median family income. The fall "
        "from near-parity in the 1950s traces the death of the single-earner "
        "family norm — one production wage stopped covering the median.",
        numerator=("weekly-earnings-manufacturing",),
        denominator=("median-family-income-all",),
        numerator_scale=52.0,
        percent=True,
        falling=True,
        caveats=(
            "Manufacturing wages skew urban, industrial, male — they stand in "
            "for 'the worker' where no broader wage series exists (see the "
            "manufacturing-wage-proxy assumption).",
        ),
    ),
    Metric(
        "food-share",
        "Food's share of spending",
        "% of household expenditure",
        "No annual series exists for food share — the line is the decade "
        "survey points, and the gaps between surveys are unknown.",
        source_arc="food-share",
        falling=True,
    ),
    Metric(
        "real-wage-index",
        "An hour of work's real purchasing power",
        "index, 2024 = 100",
        "Nominal hourly earnings / CPI-U, normalized so 2024 = 100. The line "
        "shows how much an hour of work in each year could buy compared with "
        "an hour in 2024.",
        numerator=("hourly-earnings-total-private",),
        denominator=("cpi-u",),
        base_year=2024,
        zero_baseline=False,
    ),
)

METRIC_BY_SLUG: dict[str, Metric] = {m.slug: m for m in AFFORDABILITY_METRICS}
