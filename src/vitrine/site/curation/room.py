"""Room curation: stage artifacts, compositions, gap banners, zone notes."""

from __future__ import annotations

from vitrine.site.curation.corridor import ARC_BY_SLUG

COMPOSITIONS: dict[str, str] = {
    "1900s": "us-1900s-expenditure-breakdown",
    "1970s": "us-1970s-expenditure-shares",
    "1980s": "us-1980s-expenditure-shares",
    "1990s": "us-1990s-expenditure-shares",
    "2000s": "us-2000s-expenditure-shares",
    "2010s": "us-2010s-expenditure-shares",
    "2020s": "us-2020s-expenditure-breakdown-4p",
}

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

HOME_SIZE_FACTS: dict[str, str] = {
    "1970s": "us-1970s-median-home-size",
    "1980s": "us-1980s-median-home-size",
    "1990s": "us-1990s-median-home-size",
    "2000s": "us-2000s-median-home-size",
    "2010s": "us-2010s-median-home-size",
    "2020s": "us-2020s-median-home-size",
}

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

ZONE_NOTE_POS: dict[str, tuple[int, int]] = {
    "housing": (172, 218),
    "apparel": (440, 218),
    "food": (172, 342),
    "health": (520, 342),
    "transport": (620, 360),
}
