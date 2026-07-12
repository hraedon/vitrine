"""Affordability dashboard metric resolution and recession loading."""

from __future__ import annotations

import tomllib
from pathlib import Path

from vitrine.series import Series
from vitrine.site import curation, svg
from vitrine.site.projections.facts import FactRef, placard_href


def series_numeric(s: Series) -> dict[int, float]:
    """A series's values in canonical units: dollars for monetary series
    (values_minor cents → dollars), raw floats otherwise (CPI index, hours)."""
    if s.values_minor:
        return {y: v / 100.0 for y, v in s.values_minor.items()}
    return dict(s.values)


def resolve_metric(
    metric: curation.Metric,
    series: dict[str, Series],
) -> tuple[dict[int, float], str]:
    """Compute a metric's year→value map, or report why it can't render."""
    if metric.source_arc:
        return {}, ""
    if not metric.numerator or not metric.denominator:
        return {}, "metric declares no numerator/denominator"
    if metric.base_year is not None and metric.percent:
        return {}, "metric sets both base_year and percent (mutually exclusive)"

    num: dict[int, float] = {}
    for sid in metric.numerator:
        if sid not in series:
            return {}, f"numerator series {sid!r} not found"
        new_vals = series_numeric(series[sid])
        overlap = set(num) & set(new_vals)
        if overlap:
            return {}, (
                f"numerator series {sid!r} overlaps {sorted(overlap)} with an "
                f"earlier numerator series — merge is ambiguous"
            )
        num.update(new_vals)
    den: dict[int, float] = {}
    for sid in metric.denominator:
        if sid not in series:
            return {}, f"denominator series {sid!r} not found"
        den.update(series_numeric(series[sid]))

    years = sorted(set(num) & set(den))
    if not years:
        return {}, "numerator and denominator share no years"
    ratios: dict[int, float] = {}
    for y in years:
        d = den[y]
        if d == 0:
            continue
        ratios[y] = (num[y] * metric.numerator_scale) / d
    if not ratios:
        return {}, "denominator is zero for every coverage year"
    if metric.base_year is not None:
        if metric.base_year not in ratios:
            return {}, f"base_year {metric.base_year} not in coverage"
        base = ratios[metric.base_year]
        if base == 0:
            return {}, f"base_year {metric.base_year} ratio is zero — cannot index"
        ratios = {y: v / base * 100.0 for y, v in ratios.items()}
    elif metric.percent:
        ratios = {y: v * 100.0 for y, v in ratios.items()}
    return ratios, ""


def metric_markers(
    metric: curation.Metric,
    index: dict[str, FactRef],
    root: str,
) -> tuple[svg.MetricMarker, ...]:
    """Decade-fact markers for a direct-mode metric (e.g. food share)."""
    if not metric.source_arc:
        return ()
    arc = curation.ARC_BY_SLUG.get(metric.source_arc)
    if arc is None:
        return ()
    markers: list[svg.MetricMarker] = []
    for decade, fid in arc.fact_ids.items():
        if fid not in index:
            continue
        fact = index[fid].fact
        year = fact.price_year if fact.price_year else int(decade[:4]) + 5
        markers.append(
            svg.MetricMarker(
                year=year,
                fact_id=fid,
                href=placard_href(index, fid, root),
                tier=fact.tier.value,
                label=fact.label,
                value=fact.value,
                quantity=fact.quantity,
            )
        )
    return tuple(markers)


def ym_to_year(ym: str) -> float:
    """'1973-11' → 1973 + (11-1)/12 ≈ 1973.83 (fractional year for band edges)."""
    year_s, month_s = ym.split("-")
    return int(year_s) + (int(month_s) - 1) / 12.0


def load_recessions(path: Path) -> tuple[tuple[svg.Recession, ...], str]:
    """Load NBER recession bands + the source url from data/recessions.toml."""
    if not path.is_file():
        return (), ""
    with path.open("rb") as fh:
        data = tomllib.load(fh)
    bands: list[svg.Recession] = []
    for entry in data.get("recession", []):
        bands.append(
            svg.Recession(
                peak=ym_to_year(entry["peak"]),
                trough=ym_to_year(entry["trough"]),
            )
        )
    return tuple(bands), str(data.get("url", ""))
