"""Affordability projections — hours/pct formatting and room affordability."""

from __future__ import annotations

from vitrine.affordability import afford
from vitrine.compare import Comparison
from vitrine.derive import ComputedFact
from vitrine.model import Basis, Corpus, Fact, Measure, Panel, Room, measure_label
from vitrine.site import svg
from vitrine.site.projections.facts import FactRef, placard_href


def format_hours(hours: float) -> str:
    if hours < 100:
        return f"≈ {hours:.1f} hours of work"
    return f"≈ {hours:,.0f} hours of work"


def format_pct(pct: float) -> str:
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
            hours_str = format_hours(aff.hours_to_afford)
        pct_str = ""
        if aff.pct_of_income is not None:
            pct_str = format_pct(aff.pct_of_income)

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


def panels_for(
    room: Room, computed: tuple[ComputedFact, ...]
) -> list[tuple[Panel, list[Fact], list[ComputedFact]]]:
    return [
        (
            panel,
            [f for f in room.facts if f.panel is panel],
            [c for c in computed if c.panel is panel],
        )
        for panel in Panel
    ]


def afford_fact_ids(corpus: Corpus, pattern: str) -> dict[str, str]:
    """Every decade whose room holds the priced fact — structured or not."""
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
    """Project an affordability comparison onto the arc chart (hours axis)."""
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
