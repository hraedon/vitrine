"""Surface projections — pure functions that turn the corpus into typed pages.

Each ``project_*`` function performs all fact-id resolution, SVG generation,
ratio computation, and comparability logic for one surface and returns a
frozen ``context.*Page`` object ready for the orchestrator to render. No
projection writes files; that is the build orchestrator's sole job.
"""

from __future__ import annotations

from vitrine.site.projections.affordability import project_affordability_dashboard
from vitrine.site.projections.corridors import project_corridor
from vitrine.site.projections.pairs import project_pair
from vitrine.site.projections.references import project_bibliography, project_methodology
from vitrine.site.projections.rooms import project_lobby, project_room
from vitrine.site.projections.walkthrough import project_walkthrough

__all__ = [
    "project_affordability_dashboard",
    "project_bibliography",
    "project_corridor",
    "project_lobby",
    "project_methodology",
    "project_pair",
    "project_room",
    "project_walkthrough",
]
