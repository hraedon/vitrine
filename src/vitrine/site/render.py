"""Compatibility re-exports for the presentation layer.

Historically this 1170-line module held the renderer, projections, and typed
views together. Plan 019 split it into:
  * ``build.py``      — output orchestration (``build_site``)
  * ``context.py``    — frozen typed page/view models
  * ``projections/``  — one module per surface, each exposing a ``project_*``

This file now exists only so legacy imports keep resolving. New code should
import from the split modules directly. The private underscore-prefixed names
are re-exported so the characterization tests (which pin the projections)
continue to pass unchanged.
"""

from __future__ import annotations

from vitrine.site.build import build_site as render_site
from vitrine.site.projections.affordability import (
    afford_arc_chart as _afford_arc_chart,
)
from vitrine.site.projections.affordability import (
    afford_fact_ids as _afford_fact_ids,
)
from vitrine.site.projections.affordability import (
    affordability_for_room as _affordability_for_room,
)
from vitrine.site.projections.arcs import (
    arc_chart_for as _arc_chart_for,
)
from vitrine.site.projections.arcs import (
    arc_coverage as _arc_coverage,
)
from vitrine.site.projections.arcs import (
    arc_group_chart_for as _arc_group_chart_for,
)
from vitrine.site.projections.arcs import (
    arc_group_coverage as _arc_group_coverage,
)
from vitrine.site.projections.arcs import (
    arc_points as _arc_points,
)
from vitrine.site.projections.arcs import (
    fold_shares as _fold_shares,
)
from vitrine.site.projections.facts import (
    GAP_PREFIX as _GAP_PREFIX,
)
from vitrine.site.projections.facts import (
    FactRef as _FactRef,
)
from vitrine.site.projections.facts import (
    index_facts as _index_facts,
)
from vitrine.site.projections.facts import (
    placard_href as _placard_href,
)
from vitrine.site.projections.metrics import (
    load_recessions as _load_recessions,
)
from vitrine.site.projections.metrics import (
    metric_markers as _metric_markers,
)
from vitrine.site.projections.metrics import (
    resolve_metric as _resolve_metric,
)
from vitrine.site.projections.metrics import (
    series_numeric as _series_numeric,
)
from vitrine.site.projections.metrics import (
    ym_to_year as _ym_to_year,
)
from vitrine.site.projections.rooms import (
    panels_for as _panels_for,
)
from vitrine.site.projections.rooms import (
    project_room,
)
from vitrine.site.projections.rooms import (
    room_story as _room_story,
)
from vitrine.site.projections.stage import build_stage as _build_stage

__all__ = [
    "_GAP_PREFIX",
    "_FactRef",
    "_afford_arc_chart",
    "_afford_fact_ids",
    "_affordability_for_room",
    "_arc_chart_for",
    "_arc_coverage",
    "_arc_group_chart_for",
    "_arc_group_coverage",
    "_arc_points",
    "_build_stage",
    "_fold_shares",
    "_index_facts",
    "_load_recessions",
    "_metric_markers",
    "_panels_for",
    "_placard_href",
    "_resolve_metric",
    "_room_story",
    "_series_numeric",
    "_ym_to_year",
    "project_room",
    "render_site",
]
