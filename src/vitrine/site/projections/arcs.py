"""Arc and arc-group projections: cross-decade chart geometry + coverage cues.

Pure projection: takes a fact index (+ optional annual series) and returns
ready-to-render ``Markup`` charts and the compact coverage strings the atlas
directory shows. No file I/O, no corpus mutation.
"""

from __future__ import annotations

from vitrine.model import Fact
from vitrine.series import Series
from vitrine.site import curation, svg, tokens
from vitrine.site.projections.facts import FactRef, placard_href


def arc_points(
    index: dict[str, FactRef], arc: curation.Arc, root: str
) -> tuple[svg.ArcPoint, ...]:
    points = []
    for decade in sorted(arc.fact_ids):
        fid = arc.fact_ids[decade]
        ref = index[fid]
        # Marker year: the fact's own price_year when it states one, else the
        # mid-decade year (1950s → 1955). A fact that pins a year sits at that
        # year on the annual axis; a decade-level fact sits at mid-decade while
        # the annual series line carries the year-by-year detail.
        year = ref.fact.price_year if ref.fact.price_year else int(decade[:4]) + 5
        points.append(
            svg.ArcPoint(
                decade=decade,
                fact_id=fid,
                href=placard_href(index, fid, root),
                tier=ref.fact.tier.value,
                label=ref.fact.label,
                value=ref.fact.value,
                quantity=(None if decade in arc.plot_gaps else ref.fact.quantity),
                year=year,
            )
        )
    return tuple(points)


def arc_chart_for(
    arc: curation.Arc,
    index: dict[str, FactRef],
    series: dict[str, Series],
    root: str,
) -> str:
    """The arc chart for ``arc`` — annual series where one backs it, else decades."""
    points = arc_points(index, arc, root)
    if arc.series_id and arc.series_id in series:
        s = series[arc.series_id]
        return svg.arc_chart_series(
            s.values, points, arc.unit, series_id=arc.series_id, falling=arc.falling
        )
    return svg.arc_chart(points, arc.unit, falling=arc.falling)


def arc_group_chart_for(
    group: curation.ArcGroup,
    index: dict[str, FactRef],
    root: str,
) -> str:
    """Render a curated group of related arcs on one honest shared scale."""
    colors = {
        "copper": tokens.COPPER,
        "brass": tokens.BRASS,
        "brass-deep": tokens.BRASS_DEEP,
    }
    chart_series = tuple(
        svg.ArcSeries(
            label=label,
            color=colors[color_role],
            points=arc_points(index, curation.ARC_BY_SLUG[arc_slug], root),
        )
        for arc_slug, label, color_role in group.members
    )
    return svg.multi_arc_chart(chart_series, group.unit)


def arc_coverage(
    arc: curation.Arc,
    index: dict[str, FactRef],
    series: dict[str, Series],
    room_count: int,
) -> str:
    """A compact, mechanically derived coverage cue for the atlas directory."""
    if arc.series_id and arc.series_id in series:
        annual = series[arc.series_id]
        observations = len(annual.values) + len(annual.values_minor)
        return f"{observations} annual observations"
    plotted = sum(
        1
        for decade, fact_id in arc.fact_ids.items()
        if decade not in arc.plot_gaps and index[fact_id].fact.quantity is not None
    )
    return f"{plotted} of {room_count} rooms charted"


def arc_group_coverage(
    group: curation.ArcGroup,
    index: dict[str, FactRef],
    room_count: int,
) -> str:
    plotted_decades = {
        decade
        for arc_slug, _label, _color_role in group.members
        for decade, fact_id in curation.ARC_BY_SLUG[arc_slug].fact_ids.items()
        if decade not in curation.ARC_BY_SLUG[arc_slug].plot_gaps
        and index[fact_id].fact.quantity is not None
    }
    return f"{len(plotted_decades)} of {room_count} rooms charted"


def fold_shares(
    fact: Fact, index: dict[str, FactRef], root: str
) -> tuple[svg.ShareSegment, ...]:
    """Parse a composition fact and fold categories into the fixed palette slots."""
    parsed = svg.parse_shares(fact.value)
    href = placard_href(index, fact.id, root)
    by_slot: dict[str, list[tuple[str, float]]] = {}
    for category, pct in parsed:
        slot = tokens.CATEGORY_SLOT.get(category, "other")
        by_slot.setdefault(slot, []).append((category, pct))
    segments = []
    for slot in tokens.COMPOSITION_ORDER:
        if slot not in by_slot:
            continue
        breakdown = by_slot[slot]
        names = [name for name, _pct in breakdown]
        total = sum(pct for _name, pct in breakdown)
        label = "other" if slot == "other" else " + ".join(names)
        segments.append(
            svg.ShareSegment(
                slot=slot,
                category=label,
                pct=round(total, 2),
                fact_id=fact.id,
                href=href,
                breakdown=tuple(breakdown),
            )
        )
    return tuple(segments)
