"""Compatibility layer — re-exports from the split presentation modules.

The presentation code is now split into:
  build.py          — orchestration (build_site)
  context.py        — typed page contexts
  projections/      — fact-to-SVG projection helpers
  curation/          — editorial registries split by surface
  templates/        — Jinja2 templates as package resources
  assets/            — external CSS stylesheet

This module preserves the old import paths (render_site, _build_stage, etc.)
so existing tests and the CLI continue to work during the migration.
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
from vitrine.site.projections.affordability import (
    format_hours as _format_hours,
)
from vitrine.site.projections.affordability import (
    format_pct as _format_pct,
)
from vitrine.site.projections.affordability import (
    panels_for as _panels_for,
)
from vitrine.site.projections.arcs import (
    arc_chart_for as _arc_chart_for,
)
from vitrine.site.projections.arcs import (
    arc_group_chart_for as _arc_group_chart_for,
)
from vitrine.site.projections.arcs import (
    arc_points as _arc_points,
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
from vitrine.site.projections.stage import (
    build_stage as _build_stage,
)
from vitrine.site.projections.stage import (
    fold_shares as _fold_shares,
)

__all__ = [
    "_FactRef",
    "_afford_arc_chart",
    "_afford_fact_ids",
    "_affordability_for_room",
    "_arc_chart_for",
    "_arc_group_chart_for",
    "_arc_points",
    "_build_stage",
    "_fold_shares",
    "_format_hours",
    "_format_pct",
    "_index_facts",
    "_load_recessions",
    "_metric_markers",
    "_panels_for",
    "_placard_href",
    "_resolve_metric",
    "_series_numeric",
    "_ym_to_year",
    "render_site",
]
