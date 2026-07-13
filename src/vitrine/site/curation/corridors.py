"""Corridor atlas curation: cross-decade arcs, shared-axis groups, wings.

Also holds the affordability-corridor items (median home, new car) projected
across decades. Authors structure only; the corpus supplies every value.
"""

from __future__ import annotations

from vitrine.site.curation.models import Arc, ArcGroup, CorridorWing


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
        "family-size",
        "Average family size",
        "persons per family",
        {
            "1900s": "us-1900s-family-size",
            "1940s": "us-1940s-average-family-size",
            "1950s": "us-1950s-average-family-size",
            "1960s": "us-1960s-average-family-size",
            "1970s": "us-1970s-average-family-size",
            "1980s": "us-1980s-average-family-size",
            "1990s": "us-1990s-average-family-size",
            "2000s": "us-2000s-average-family-size",
            "2010s": "us-2010s-average-family-size",
            "2020s": "us-2020s-average-family-size",
        },
        falling=True,
        caveats=(
            "The 1900s datum (5.31) is from the 1901 BLS wage-earner survey — "
            "0.7 persons above the Census 1900 national average of 4.61; the "
            "survey over-sampled larger families, not by design.",
            "The 1940s point is 1947 (first postwar CPS tabulation), not 1940. "
            "The 1960s uptick (3.7 vs 3.54 in 1950) reflects the baby boom's "
            "peak family-composition effect.",
        ),
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
            "2020s": "us-2020s-median-home-size",
        },
        caveats=(
            "1970s–2020s: median square feet of new single-family houses completed "
            "(Census C-25/H-150 / Characteristics of New Housing). The 2020s point "
            "is 2024; the series is conceptually consistent across the whole span.",
        ),
    ),
    Arc(
        "number-of-families",
        "Number of families",
        "families in the United States",
        _ids("us-{decade}-number-of-families", "194 195 196 197 198 199 200 201 202"),
        caveats=(
            "CPS/F-8 counts all families (related persons living together). "
            "The 1940s point is 1947 — the first postwar CPS tabulation.",
        ),
    ),
    # ── Plan 014: corridor expansion arcs ──────────────────────────────────
    Arc(
        "heart-disease-mortality",
        "Heart disease mortality",
        "age-adjusted deaths per 100,000",
        _ids(
            "us-{decade}-heart-disease-mortality",
            "194 195 196 197 198 199 200 201 202",
        ),
        falling=True,
    ),
    Arc(
        "cancer-mortality",
        "Cancer mortality",
        "age-adjusted deaths per 100,000",
        _ids(
            "us-{decade}-cancer-mortality",
            "194 195 197 199 201 202",
        ),
        caveats=(
            "Six points across nine decades — 1960s, 1980s, and 2000s are "
            "missing from the NCHS series and render as gaps.",
        ),
    ),
    Arc(
        "stroke-mortality",
        "Stroke mortality",
        "age-adjusted deaths per 100,000",
        _ids("us-{decade}-stroke-mortality", "195 197 202"),
        falling=True,
        caveats=(
            "Only three points span the 70-year window — the decline is "
            "dramatic but sparsely sampled. Additional decades are available "
            "from the same NCHS source for a future curation pass.",
        ),
    ),
    Arc(
        "cancer-survival",
        "Cancer 5-year relative survival",
        "% surviving 5 years after diagnosis (SEER)",
        _ids(
            "us-{decade}-cancer-survival",
            "196 197 198 199 200 201 202",
        ),
        caveats=(
            "Different source family (SEER/NCI, not CDC NCHS) and different "
            "unit (% surviving, not deaths per 100,000) — not grouped with "
            "the mortality arcs.",
        ),
    ),
    Arc(
        "nhe-gdp-share",
        "Healthcare spending as share of GDP",
        "% of GDP (national health expenditures)",
        _ids("us-{decade}-nhe-total", "196 197 198 199 200 201 202"),
    ),
    Arc(
        "out-of-pocket-share",
        "Out-of-pocket share of health spending",
        "% of total NHE paid out of pocket",
        _ids(
            "us-{decade}-nhe-out-of-pocket-share",
            "196 197 198 199 200 201 202",
        ),
        falling=True,
    ),
    Arc(
        "cex-healthcare-share",
        "Healthcare share of household budget",
        "% of total expenditures (CEX, consumer units)",
        _ids(
            "us-{decade}-cex-healthcare-share",
            "198 199 200 201 202",
        ),
        caveats=(
            "Different population from the NHE arcs (consumer units, not "
            "national health spending) and different concept (family budget "
            "share, not GDP share). The trend is the same direction.",
        ),
    ),
    Arc(
        "median-gross-rent",
        "Median gross rent",
        "USD/month, nominal (specified renter-occupied units)",
        _ids("us-{decade}-median-gross-rent", "194 195 196 197 198 199 200"),
        caveats=(
            "Nominal dollars — the CPI arc and affordability dashboard "
            "provide deflation context. No 2010s or 2020s point: Census "
            "Historical Housing Tables end at 2000; ACS rent data (Table "
            "B25064) would extend the arc in a future curation pass.",
        ),
    ),
    Arc(
        "expenditure-income-ratio",
        "Expenditure-to-income ratio",
        "% (total expenditures ÷ income before taxes, all CUs)",
        _ids(
            "us-{decade}-cex-expenditure-income-ratio",
            "198 199 200 201 202",
        ),
        falling=True,
        caveats=(
            "The aggregate ratio hides inequality — the bottom quintile "
            "spent 221.8% of income in 2012 (see us-2010s-cex-quintile-q1-ratio). "
            "The falling aggregate reflects high-income households pulling "
            "the ratio down, not broad-based affordability improvement.",
        ),
    ),
    Arc(
        "apparel-share",
        "Apparel's share of spending",
        "% of total expenditures",
        _ids(
            "us-{decade}-cex-apparel-share",
            "197 198 199 200 201 202",
        ),
        falling=True,
        caveats=(
            "Population changes mid-series: 1970s–1990s are 4-person CUs "
            "(CEX Table 4), 2000s–2020s are all consumer units (multi-year "
            "tables). Every placard names the measured population.",
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
    ArcGroup(
        "mortality-revolution",
        "The mortality revolution: heart disease, cancer, stroke",
        "age-adjusted deaths per 100,000 population",
        (
            ("heart-disease-mortality", "Heart disease", "copper"),
            ("cancer-mortality", "Cancer", "brass"),
            ("stroke-mortality", "Stroke", "brass-deep"),
        ),
        caveats=(
            "Three trajectories on one axis: heart disease peaked early and "
            "fell steadily; cancer rose for decades before turning; stroke "
            "fell dramatically throughout. Cancer survival is charted "
            "separately (different unit and source family).",
        ),
    ),
    ArcGroup(
        "healthcare-cost",
        "Healthcare cost transformation: spending rose, direct payment fell",
        "% (share of GDP / share of NHE)",
        (
            ("nhe-gdp-share", "NHE as % of GDP", "brass"),
            ("out-of-pocket-share", "Out-of-pocket % of NHE", "copper"),
        ),
        caveats=(
            "Two complementary halves of one story: national healthcare "
            "spending rose from 5% to 18% of GDP while the out-of-pocket "
            "share fell from 47% to 10.5%. Insurance and public programs "
            "shifted costs from direct payment to third-party payment.",
        ),
    ),
)

ARC_GROUP_BY_MEMBER: dict[str, ArcGroup] = {
    member_slug: group
    for group in ARC_GROUPS
    for member_slug, _label, _color in group.members
}


# The corridor page is an atlas, not a registry dump. These four questions
# provide an editorial route through every rendered chart while leaving the
# underlying arc registry—and therefore every provenance invariant—unchanged.
CORRIDOR_WINGS: tuple[CorridorWing, ...] = (
    CorridorWing(
        slug="household",
        number="I",
        title="The household",
        question="Who made up the family, and how long did life last?",
        introduction=(
            "Population records describe the household from the outside: its "
            "size, its prevalence, and the health conditions surrounding it. "
            "The gaps show where the national series had not yet learned to count."
        ),
        arc_slugs=(
            "life-expectancy",
            "infant-mortality",
            "mortality-revolution",
            "cancer-survival",
            "poverty-rate",
            "family-size",
            "number-of-families",
        ),
    ),
    CorridorWing(
        slug="shelter",
        number="II",
        title="The threshold",
        question="When did shelter become infrastructure?",
        introduction=(
            "Tenure, plumbing, cooling, mobility, and floor area entered the "
            "record on different clocks. Read together, they show a house becoming "
            "a bundle of systems rather than a single possession."
        ),
        arc_slugs=(
            "homeownership",
            "plumbing",
            "air-conditioning",
            "vehicle",
            "home-size",
            "median-gross-rent",
        ),
    ),
    CorridorWing(
        slug="signals",
        number="III",
        title="Signals into the home",
        question="How did the outside world cross the walls?",
        introduction=(
            "Broadcast, voice, cable, computing, and networks arrived in waves. "
            "Short series remain short: an absent line is not filled from a later "
            "technology with a similar name."
        ),
        arc_slugs=(
            "radio",
            "television",
            "telephone",
            "cable-tv",
            "computer",
            "internet",
        ),
    ),
    CorridorWing(
        slug="economy",
        number="IV",
        title="The household economy",
        question="Where did the family's time and money go?",
        introduction=(
            "Paid hours, unpaid production, prices, and the food budget expose the "
            "work behind the room. This wing also holds the computed affordability "
            "exhibits: ratios made at build time, never authored as facts."
        ),
        arc_slugs=(
            "home-production-by-sex",
            "weekly-hours",
            "food-share",
            "apparel-share",
            "expenditure-income-ratio",
            "healthcare-cost",
            "cex-healthcare-share",
            "cpi",
        ),
    ),
)


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
