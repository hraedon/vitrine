"""Arc chart projections — cross-decade fact families onto SVG charts."""

from __future__ import annotations

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
        year = ref.fact.price_year if ref.fact.price_year else int(decade[:4]) + 5
        points.append(
            svg.ArcPoint(
                decade=decade,
                fact_id=fid,
                href=placard_href(index, fid, root),
                tier=ref.fact.tier.value,
                label=ref.fact.label,
                value=ref.fact.value,
                quantity=(
                    None if decade in arc.plot_gaps else ref.fact.quantity
                ),
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
    colors = {"copper": tokens.COPPER, "brass": tokens.BRASS, "brass-deep": tokens.BRASS_DEEP}
    chart_series = tuple(
        svg.ArcSeries(
            label=label,
            color=colors[color_role],
            points=arc_points(index, curation.ARC_BY_SLUG[arc_slug], root),
        )
        for arc_slug, label, color_role in group.members
    )
    return svg.multi_arc_chart(chart_series, group.unit)
