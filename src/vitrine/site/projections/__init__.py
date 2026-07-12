"""Projection helpers — transform corpus facts into chart-ready values."""

from __future__ import annotations

from vitrine.site.projections.affordability import (
    afford_arc_chart,
    afford_fact_ids,
    affordability_for_room,
    format_hours,
    format_pct,
    panels_for,
)
from vitrine.site.projections.arcs import (
    arc_chart_for,
    arc_group_chart_for,
    arc_points,
)
from vitrine.site.projections.facts import FactRef, index_facts, placard_href
from vitrine.site.projections.metrics import (
    load_recessions,
    metric_markers,
    resolve_metric,
    series_numeric,
    ym_to_year,
)
from vitrine.site.projections.pairs import (
    PairAffordSection,
    PairCell,
    PairFamily,
    pair_afford,
    pair_families,
)
from vitrine.site.projections.stage import build_stage, fold_shares

__all__ = [
    "FactRef",
    "PairAffordSection",
    "PairCell",
    "PairFamily",
    "afford_arc_chart",
    "afford_fact_ids",
    "affordability_for_room",
    "arc_chart_for",
    "arc_group_chart_for",
    "arc_points",
    "build_stage",
    "fold_shares",
    "format_hours",
    "format_pct",
    "index_facts",
    "load_recessions",
    "metric_markers",
    "pair_afford",
    "pair_families",
    "panels_for",
    "placard_href",
    "resolve_metric",
    "series_numeric",
    "ym_to_year",
]
