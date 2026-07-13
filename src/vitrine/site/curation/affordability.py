"""Affordability dashboard curation: computed ratio metrics over time."""

from __future__ import annotations

from vitrine.site.curation.models import Metric

# ── affordability dashboard metrics (Plan 011) ───────────────────────────────
# Every metric is a ratio of two series (or a direct arc projection), computed
# by the renderer — never authored. A metric's coverage is the intersection of
# its numerator and denominator years; years missing on either side render as
# gaps (the "render the gap" ethos, extended to cross-decade metrics).
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
