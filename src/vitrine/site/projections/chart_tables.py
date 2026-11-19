"""Text alternatives from the same point objects and series as the charts."""

from __future__ import annotations

from vitrine.series import Series, representation_problems
from vitrine.site import svg
from vitrine.site.context import ChartTable, ChartTableRow
from vitrine.site.curation.models import Metric


def point_table(
    points: tuple[svg.ArcPoint, ...], unit: str, title: str = "Selected chart records",
) -> ChartTable:
    return ChartTable(
        title=title,
        unit=unit,
        note=(
            "Values use the plotted axis. A record excluded from that axis is marked "
            "not plotted; this does not assert a zero or historical absence. "
            "Open a record for its full value, population and source."
        ),
        rows=tuple(ChartTableRow(
            period=point.decade,
            value=str(point.quantity) if point.quantity is not None else "Not plotted",
            label=point.label,
            href=f"#{point.fact_id}--modal",
            tier=point.tier,
            plotted=point.quantity is not None,
        ) for point in points),
    )


def annual_table(series: Series, root: str) -> ChartTable:
    """The annual line's observations; never fill omitted calendar years."""
    if problems := representation_problems(series):
        raise ValueError(f"annual chart table {series.id!r}: {'; '.join(problems)}")
    if series.values_minor:
        raise ValueError(
            f"annual chart table {series.id!r}: monetary minor-unit amounts are not "
            "supported by the annual arc renderer"
        )
    return ChartTable(
        title="Annual series values",
        unit=series.unit,
        note="Only published observations are listed. Missing years are not zero values.",
        population=series.population,
        rows=tuple(ChartTableRow(
            period=str(year),
            value=str(value),
            label=series.label,
            href=f"{root}archive/sources/{series.source}.html",
            tier=series.tier.value,
        ) for year, value in sorted(series.values.items())),
    )


def metric_tables(
    metric: Metric, values: dict[int, float], markers: tuple[svg.MetricMarker, ...],
    series: dict[str, Series], root: str,
) -> tuple[ChartTable, ...]:
    if values:
        return (ChartTable(
            title="Calculated chart values", unit=metric.unit,
            note=(
                "Calculated from the same source series as the chart. Only years with "
                "a result are listed; omitted years are not zero. Source populations "
                "and calculation limits remain those stated above the chart. "
                "Calculated values are displayed to six significant digits; this "
                "formatting does not increase the precision of the source inputs."
            ),
            sources=tuple(
                (series[sid].label, f"{root}archive/sources/{series[sid].source}.html")
                for sid in dict.fromkeys((*metric.numerator, *metric.denominator))
            ),
            rows=tuple(ChartTableRow(
                period=str(year), value=f"{value:g}",
                label="Computed from the cited source series", href="", tier="",
            ) for year, value in sorted(values.items())),
        ),)
    if markers:
        return (ChartTable(
            title="Selected chart records", unit=metric.unit,
            note=(
                "Periods identify the curated decade or an explicit record year. "
                "Read each record label for its observation date and population. "
                "Where no exact year field is declared, the plot uses an illustrative "
                "decade midpoint, not an observed year."
            ),
            rows=tuple(ChartTableRow(
                period=marker.period or str(marker.year),
                value=str(marker.quantity) if marker.quantity is not None else "Not plotted",
                label=marker.label, href=marker.href, tier=marker.tier,
                plotted=marker.quantity is not None,
            ) for marker in markers),
        ),)
    return ()
