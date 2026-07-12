"""Editorial curation for the three surfaces (Plan 007).

Re-exports from the split submodules for backward compatibility.
"""

from __future__ import annotations

from vitrine.site.curation.affordability import (
    AFFORDABILITY_METRICS,
    METRIC_BY_SLUG,
    Metric,
)
from vitrine.site.curation.corridor import (
    AFFORD_ITEM_CAVEATS,
    AFFORD_ITEMS,
    ARC_BY_SLUG,
    ARC_GROUP_BY_MEMBER,
    ARC_GROUPS,
    ARCS,
    Arc,
    ArcGroup,
)
from vitrine.site.curation.room import (
    COMPOSITIONS,
    HOME_SIZE_FACTS,
    ROOM_GAP_BANNERS,
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
    "HOME_SIZE_FACTS",
    "METRIC_BY_SLUG",
    "ROOM_GAP_BANNERS",
    "STAGE_DIFFUSION",
    "STAGE_STATS",
    "WALKTHROUGH_FLOOR_AREA",
    "WALKTHROUGH_METRICS",
    "WALKTHROUGH_PEOPLE",
    "WALKTHROUGH_STOPS",
    "ZONE_NOTE_POS",
    "Arc",
    "ArcGroup",
    "Metric",
]
