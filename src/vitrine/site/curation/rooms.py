"""Room curation: opening-route stories, stage artifacts, gap banners, notes."""

from __future__ import annotations

from vitrine.site.curation.corridors import ARC_BY_SLUG
from vitrine.site.curation.models import RoomStory

# Four sourced exhibits per room form its opening route. These selections do
# not replace the complete six-panel collection; they give a first-time
# visitor a way into it. Questions are deliberately interpretive rather than
# declarative: the fact cards below them carry every historical claim.
ROOM_STORIES: tuple[RoomStory, ...] = (
    RoomStory(
        "1900s",
        "The work behind the household",
        "What did it take to keep one family housed, fed, and running?",
        (
            "us-1900s-annual-family-income",
            "us-1900s-food-share",
            "us-1900s-weekly-hours",
            "us-1900s-home-production-household",
        ),
    ),
    RoomStory(
        "1910s",
        "The record goes quiet",
        "What can a room reveal when the national household books are missing?",
        (
            "us-1910s-housing-gap",
            "us-1910s-income-gap",
            "us-1910s-manufacturing-wages",
            "us-1910s-electricity-gap",
        ),
    ),
    RoomStory(
        "1920s",
        "Signals at the walls",
        "Which parts of modern life appear before the household is fully measured?",
        (
            "us-1920s-radio-automobile",
            "us-1920s-home-production-components",
            "us-1920s-manufacturing-wages",
            "us-1920s-housing-gap",
        ),
    ),
    RoomStory(
        "1930s",
        "A modern room with missing books",
        "What survives in the record when wages contract and household surveys fail us?",
        (
            "us-1930s-manufacturing-wages",
            "us-1930s-radio-automobile",
            "us-1930s-homeownership",
            "us-1930s-work-buys-gap",
        ),
    ),
    RoomStory(
        "1940s",
        "Between prewar and postwar",
        "Can one room honestly hold a decade split by mobilization and reconversion?",
        (
            "us-1940s-prewar-wages",
            "us-1940s-median-family-income",
            "us-1940s-plumbing",
            "us-1940s-no-television",
        ),
    ),
    RoomStory(
        "1950s",
        "The equipped home arrives",
        "Which conveniences became ordinary, and which work remained?",
        (
            "us-1950s-electricity-diffusion",
            "us-1950s-refrigerator-diffusion",
            "us-1950s-tv-diffusion",
            "us-1950s-home-production-women",
        ),
    ),
    RoomStory(
        "1960s",
        "Comfort becomes common",
        "How evenly did the new baseline of domestic comfort arrive?",
        (
            "us-1960s-plumbing",
            "us-1960s-television",
            "us-1960s-air-conditioning",
            "us-1960s-poverty-rate",
        ),
    ),
    RoomStory(
        "1970s",
        "The budget changes shape",
        "What happens when the house grows while time and spending are redistributed?",
        (
            "us-1970s-expenditure-shares",
            "us-1970s-median-home-size",
            "us-1970s-home-production-women",
            "us-1970s-food-basket",
        ),
    ),
    RoomStory(
        "1980s",
        "More house, more systems",
        "How did space, media, computing, and price accumulate under one roof?",
        (
            "us-1980s-median-home-size",
            "us-1980s-cable-tv",
            "us-1980s-computer",
            "us-1980s-home-as-income-years",
        ),
    ),
    RoomStory(
        "1990s",
        "The connected threshold",
        "When does a household become part of a network?",
        (
            "us-1990s-computer",
            "us-1990s-internet-households",
            "us-1990s-median-home-value",
            "us-1990s-expenditure-shares",
        ),
    ),
    RoomStory(
        "2000s",
        "The networked day",
        "What changed when connection became infrastructure and time became measurable?",
        (
            "us-2000s-internet",
            "us-2000s-atus-time-use",
            "us-2000s-home-production-household",
            "us-2000s-home-as-income-years",
        ),
    ),
    RoomStory(
        "2010s",
        "Comfort under pressure",
        "How can a well-equipped household still carry a strained budget?",
        (
            "us-2010s-internet",
            "us-2010s-expenditure-shares",
            "us-2010s-cex-quintile-q1-ratio",
            "us-2010s-home-as-income-years",
        ),
    ),
    RoomStory(
        "2020s",
        "The expensive connected present",
        "What does the current room reveal when housing, time, and connection move together?",
        (
            "us-2020s-housing-surge",
            "us-2020s-expenditure-breakdown-4p",
            "us-2020s-time-use",
            "us-2020s-internet-diffusion",
        ),
    ),
)

ROOM_STORY_BY_DECADE: dict[str, RoomStory] = {
    story.decade: story for story in ROOM_STORIES
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
    "2020s": "us-2020s-median-home-size",
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
    # The automobile sits at (620, 405); keep its budget annotation above the
    # mark rather than running through its ring and percentage label.
    "transport": (620, 360),
}
