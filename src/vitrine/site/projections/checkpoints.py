"""Resolve comparable sample-period facts without inventing dated coordinates."""

from __future__ import annotations

import math

from markupsafe import Markup

from vitrine.model import Corpus
from vitrine.site import svg
from vitrine.site.context import ArcSection
from vitrine.site.curation.checkpoints import CHECKPOINT_ARCS, CheckpointArc
from vitrine.site.curation.rooms import CURATED_COUNTRIES
from vitrine.site.projections.facts import GAP_PREFIX, FactRef


def checkpoint_points(
    corpus: Corpus, index: dict[str, FactRef], arc: CheckpointArc,
) -> tuple[svg.CheckpointPoint, ...]:
    """Refuse a comparison whose stated population, statistic or period drifts.

    All observations resolve the same registered source population. The exact
    fact unit binds the statistic and ages as well as the physical unit; the
    authored label must also make those meanings and its sampling period visible.
    """
    if not arc.checkpoints:
        raise ValueError(f"checkpoint arc {arc.slug}: no sampling periods")
    if not all((arc.population, arc.source_population, arc.statistic, arc.unit, arc.axis_unit)):
        raise ValueError(f"checkpoint arc {arc.slug}: comparison meaning must be explicit")
    source = corpus.sources.get(arc.source)
    if source is None or (
        " ".join(source.population.split()).casefold()
        != " ".join(arc.source_population.split()).casefold()
    ):
        raise ValueError(f"checkpoint arc {arc.slug}: source population does not match")
    seen_ids: set[str] = set()
    seen_periods: set[str] = set()
    points = []
    for checkpoint in arc.checkpoints:
        fact_id, period = checkpoint.fact_id, checkpoint.period
        if fact_id in seen_ids or period in seen_periods:
            raise ValueError(f"checkpoint arc {arc.slug}: duplicate fact or sampling period")
        seen_ids.add(fact_id)
        seen_periods.add(period)
        ref = index.get(fact_id)
        if ref is None or ref.room.country not in CURATED_COUNTRIES:
            raise ValueError(f"checkpoint arc {arc.slug}: unknown or foreign fact {fact_id}")
        fact = ref.fact
        if fact.source != arc.source or fact.unit != arc.unit:
            raise ValueError(f"checkpoint fact {fact_id}: source or unit does not match")
        if (
            not period or fact.label.rsplit(", ", 1)[-1] != period
            or arc.population.casefold() not in fact.label.casefold()
            or arc.statistic.casefold() not in fact.label.casefold()
        ):
            raise ValueError(f"checkpoint fact {fact_id}: period, population or statistic missing")
        quantity = fact.quantity
        is_gap = fact.value.strip().lower().startswith(GAP_PREFIX)
        if quantity is None and not is_gap:
            raise ValueError(f"checkpoint fact {fact_id}: no quantity or documented gap")
        if quantity is not None and (is_gap or not math.isfinite(quantity) or quantity < 0):
            raise ValueError(f"checkpoint fact {fact_id}: invalid concentration quantity")
        points.append(svg.CheckpointPoint(
            fact_id=fact_id,
            period=period,
            label=fact.label,
            value=fact.value,
            quantity=quantity,
            tier=fact.tier.value,
        ))
    return tuple(points)


def checkpoint_sections(
    corpus: Corpus, index: dict[str, FactRef],
    arcs: tuple[CheckpointArc, ...] = CHECKPOINT_ARCS,
) -> tuple[ArcSection, ...]:
    sections = []
    for arc in arcs:
        points = checkpoint_points(corpus, index, arc)
        observed = sum(point.quantity is not None for point in points)
        gaps = len(points) - observed
        coverage = f"{observed} sampling period{'s' if observed != 1 else ''}"
        if gaps:
            coverage += f"; {gaps} documented gap{'s' if gaps != 1 else ''}"
        sections.append(ArcSection(
            slug=arc.slug,
            label=arc.label,
            unit=arc.unit,
            caveats=arc.caveats,
            coverage=coverage,
            chart=Markup(svg.checkpoint_chart(points, arc.axis_unit, arc.label, arc.falling)),
        ))
    return tuple(sections)
