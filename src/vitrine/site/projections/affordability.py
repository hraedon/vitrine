"""Affordability projections: per-room display, arc charts, dashboard.

Three concerns live here:
  * ``affordability_for_room`` — the hours/pct display dict a room's placards
    read (unchanged mechanics from the V0 renderer).
  * ``afford_arc_chart`` / ``afford_fact_ids`` — the hours-axis arc chart for a
    corridor affordability exhibit or pairwise comparison.
  * ``project_affordability_dashboard`` — the five stacked metric charts on the
    Plan 011 dashboard page.
"""

from __future__ import annotations

from markupsafe import Markup

from vitrine.affordability import afford
from vitrine.compare import Comparison
from vitrine.model import Basis, Corpus, Measure, Room, measure_label
from vitrine.series import Series
from vitrine.site import curation, svg
from vitrine.site.context import AffordabilityDashboardSection, AffordabilityPage
from vitrine.site.projections.facts import FactRef, placard_href
from vitrine.site.projections.metrics import metric_markers, resolve_metric


def afford_fact_ids(corpus: Corpus, pattern: str) -> dict[str, str]:
    """Every decade whose room holds the priced fact — structured or not.

    Unstructured facts can't compute an hours axis; they render as gap slots,
    which is the record's actual shape (Plan 003 structured only the rooms
    with verified anchors).
    """
    ids = {}
    for room in corpus.rooms:
        fid = pattern.format(decade=room.decade)
        if any(f.id == fid for f in room.facts):
            ids[room.decade] = fid
    return ids


def afford_arc_chart(
    comparison: Comparison,
    ids: dict[str, str],
    index: dict[str, FactRef],
    root: str,
) -> str:
    """Project an affordability comparison onto the arc chart (hours axis).

    Decades whose fact exists but can't compute hours (no structured amount,
    or no wage anchor in the room) render as gap slots.
    """
    computed = {
        p.decade: p for p in comparison.points if p.afford.hours_to_afford is not None
    }
    points = []
    for decade in sorted(ids):
        fid = ids[decade]
        ref = index[fid]
        p = computed.get(decade)
        if p is None:
            points.append(
                svg.ArcPoint(
                    decade=decade,
                    fact_id=fid,
                    href=placard_href(index, fid, root),
                    tier=ref.fact.tier.value,
                    label=ref.fact.label,
                    value=f"{ref.fact.value} — hours axis not computable (see the placard)",
                    quantity=None,
                )
            )
            continue
        hours = p.afford.hours_to_afford
        assert hours is not None
        points.append(
            svg.ArcPoint(
                decade=decade,
                fact_id=fid,
                href=placard_href(index, fid, root),
                tier=p.afford.tier.value,
                label=ref.fact.label,
                value=f"{p.price_display} ≈ {hours:,.0f} hours of work",
                quantity=round(hours, 1),
            )
        )
    return svg.arc_chart(tuple(points), "hours of work to afford", falling=False)


def _format_hours(hours: float) -> str:
    if hours < 100:
        return f"≈ {hours:.1f} hours of work"
    return f"≈ {hours:,.0f} hours of work"


def _format_pct(pct: float) -> str:
    return f"≈ {pct:.1f}% of annual income"


def affordability_for_room(corpus: Corpus, room: Room) -> dict[str, dict[str, str]]:
    """Compute affordability display for each TOTAL-basis fact in a room."""
    display: dict[str, dict[str, str]] = {}
    if not room.wage_anchor and not room.income_anchor:
        return display

    by_id = {f.id: f for f in room.facts}
    wage_fact = by_id.get(room.wage_anchor) if room.wage_anchor else None
    income_fact = by_id.get(room.income_anchor) if room.income_anchor else None

    wage_pop = ""
    income_pop = ""
    wage_measure: Measure | None = None
    income_measure: Measure | None = None
    if wage_fact is not None:
        src = corpus.sources.get(wage_fact.source)
        if src is not None:
            wage_pop = src.population
            wage_measure = src.measure
    if income_fact is not None:
        src = corpus.sources.get(income_fact.source)
        if src is not None:
            income_pop = src.population
            income_measure = src.measure

    for fact in room.facts:
        if fact.basis is not Basis.TOTAL or fact.amount_minor is None:
            continue
        aff = afford(
            fact,
            wage=wage_fact,
            income=income_fact,
            wage_population=wage_pop,
            income_population=income_pop,
            wage_measure=wage_measure,
            income_measure=income_measure,
        )

        hours_str = ""
        if aff.hours_to_afford is not None:
            hours_str = _format_hours(aff.hours_to_afford)
        pct_str = ""
        if aff.pct_of_income is not None:
            pct_str = _format_pct(aff.pct_of_income)

        measure_parts: list[str] = []
        if aff.hours_to_afford is not None and aff.hours_measure is not None:
            measure_parts.append(f"hours axis: {measure_label(aff.hours_measure)}")
        if aff.pct_of_income is not None and aff.pct_measure is not None:
            measure_parts.append(f"income axis: {measure_label(aff.pct_measure)}")

        display[fact.id] = {
            "hours": hours_str,
            "hours_large": "true"
            if aff.hours_to_afford is not None and aff.hours_to_afford > 2000
            else "",
            "pct": pct_str,
            "tier": aff.tier.value,
            "anchor_note": aff.anchor_note,
            "measures": "; ".join(measure_parts),
        }

    return display


def project_affordability_dashboard(
    series: dict[str, Series],
    recessions: tuple[svg.Recession, ...],
    index: dict[str, FactRef],
    recession_url: str,
) -> AffordabilityPage:
    """Project the /affordability/ dashboard — five stacked metric charts."""
    sections: list[AffordabilityDashboardSection] = []
    for metric in curation.AFFORDABILITY_METRICS:
        values, note = resolve_metric(metric, series)
        markers = metric_markers(metric, index, "../")
        # a section renders if it has annual values OR direct-mode markers
        if not values and not markers:
            sections.append(
                AffordabilityDashboardSection(
                    metric=metric, chart=Markup(""), note=note or "no data yet"
                )
            )
            continue
        chart = svg.affordability_chart(
            values,
            recessions,
            metric.unit,
            metric_slug=metric.slug,
            falling=metric.falling,
            markers=markers,
            zero_baseline=metric.zero_baseline,
        )
        sections.append(
            AffordabilityDashboardSection(metric=metric, chart=Markup(chart), note=note)
        )
    return AffordabilityPage(sections=tuple(sections), recession_url=recession_url)
