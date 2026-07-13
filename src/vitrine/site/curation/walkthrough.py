"""Walkthrough curation: the three-stop transect (people, metrics, floor area)."""

from __future__ import annotations

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
