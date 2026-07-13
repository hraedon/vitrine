"""Editorial curation for the site's rendered surfaces (Plan 007 onward).

This package authors *structure only*: which fact ids form a cross-decade arc,
which artifact glyph maps to which fact in which room, which four exhibits open
a room. Values, tiers and geometry all come from the corpus at build time; a
registry entry whose fact lacks a structured quantity renders as a gap, and an
entry naming a fact the corpus doesn't have is a red build (mark coverage).

The declarations live in domain submodules; this module is the deliberate
public surface that renders and tests import as ``curation``.
"""

from __future__ import annotations

from vitrine.site.curation.affordability import (
    AFFORDABILITY_METRICS,
    METRIC_BY_SLUG,
)
from vitrine.site.curation.corridors import (
    AFFORD_ITEM_CAVEATS,
    AFFORD_ITEMS,
    ARC_BY_SLUG,
    ARC_GROUP_BY_MEMBER,
    ARC_GROUPS,
    ARCS,
    CORRIDOR_WINGS,
)
from vitrine.site.curation.models import (
    Arc,
    ArcGroup,
    CorridorWing,
    Metric,
    RoomStory,
)
from vitrine.site.curation.rooms import (
    COMPOSITIONS,
    HOME_SIZE_FACTS,
    ROOM_GAP_BANNERS,
    ROOM_STORIES,
    ROOM_STORY_BY_DECADE,
    STAGE_DIFFUSION,
    STAGE_STATS,
    ZONE_NOTE_POS,
)
from vitrine.site.curation.walkthrough import (
    WALKTHROUGH_FLOOR_AREA,
    WALKTHROUGH_METRICS,
    WALKTHROUGH_PEOPLE,
    WALKTHROUGH_STOPS,
)

__all__ = [
    "AFFORDABILITY_METRICS",
    "AFFORD_ITEMS",
    "AFFORD_ITEM_CAVEATS",
    "ARCS",
    "ARC_BY_SLUG",
    "ARC_GROUPS",
    "ARC_GROUP_BY_MEMBER",
    "COMPOSITIONS",
    "CORRIDOR_WINGS",
    "HOME_SIZE_FACTS",
    "METRIC_BY_SLUG",
    "ROOM_GAP_BANNERS",
    "ROOM_STORIES",
    "ROOM_STORY_BY_DECADE",
    "STAGE_DIFFUSION",
    "STAGE_STATS",
    "WALKTHROUGH_FLOOR_AREA",
    "WALKTHROUGH_METRICS",
    "WALKTHROUGH_PEOPLE",
    "WALKTHROUGH_STOPS",
    "ZONE_NOTE_POS",
    "Arc",
    "ArcGroup",
    "CorridorWing",
    "Metric",
    "RoomStory",
]
