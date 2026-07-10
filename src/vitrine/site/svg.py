"""Build-time SVG primitives — facts in, inline SVG out (Plan 007 WI-3).

Every mark that projects a fact carries ``data-fact-id`` and deep-links to the
fact's room placard; the mark-coverage gate fails the build on any mark whose
id doesn't resolve. A fact present in a chart's registry but carrying no
structured ``quantity`` renders as the gap it is — dashed slot, no invented
geometry.

Charts sit on ``ground``-colored panels: the categorical palette was validated
against that exact surface (docs/design-spec.md).
"""

from __future__ import annotations

import math
import re
from dataclasses import dataclass, field
from itertools import pairwise
from xml.sax.saxutils import escape, quoteattr

from vitrine.site import tokens


@dataclass(frozen=True, slots=True)
class ArcPoint:
    """One decade slot of a cross-decade arc."""

    decade: str
    fact_id: str
    href: str  # deep link to the room placard
    tier: str  # "A".."D"
    label: str
    value: str  # authored display value (for the native tooltip)
    quantity: float | None  # None → render the gap
    year: int = 0  # representative year (plan 010 series charts); 0 = unknown


@dataclass(frozen=True, slots=True)
class ArcSeries:
    """One named line in a shared-axis cross-decade chart."""

    label: str
    color: str
    points: tuple[ArcPoint, ...]


@dataclass(frozen=True, slots=True)
class ShareSegment:
    """One labeled segment of a composition bar."""

    slot: str  # palette slot: housing/apparel/food/health/transport/other
    category: str  # the source's own category word
    pct: float
    fact_id: str
    href: str


@dataclass(frozen=True, slots=True)
class StageArtifact:
    """One artifact glyph on the room stage."""

    artifact: str
    glyph_svg: str  # symbol fragment (local ±14 box)
    x: float
    y: float
    fact_id: str
    href: str
    label: str
    value: str
    quantity: float | None  # diffusion pct → opacity; None → dashed gap ring
    kind: str = "diffusion"  # "diffusion" (pct drives opacity) or "stat" (present, no pct)


@dataclass(frozen=True, slots=True)
class MeterBar:
    """One decade slot of the labour-hours meter."""

    decade: str
    fact_id: str
    href: str
    tier: str
    label: str
    value: str
    quantity: float | None
    note: str = ""


# parses "Housing 31.3%, transportation 17.9%, …" — applied only to facts a
# registry declares as compositions; segment labels come from the same parse,
# so a misparse is visible on the page, never silent.
_SHARE_RE = re.compile(r"([A-Za-z][A-Za-z /&'’-]*?)\s+(\d+(?:\.\d+)?)%")


def parse_shares(value: str) -> tuple[tuple[str, float], ...]:
    """Extract ``(category, pct)`` pairs from a composition display value."""
    return tuple((m.group(1).strip().lower(), float(m.group(2))) for m in _SHARE_RE.finditer(value))


def _fmt(q: float) -> str:
    return f"{q:g}"


def _nice_axis_top(q_max: float) -> float:
    """Round a chart maximum up to a clean, human-readable increment.

    Select a 1/2/5 tick step for roughly five intervals, then round the top
    above the data. Choosing the whole axis as a single 1/2/5 magnitude makes
    46.8 jump to 100 and visually flattens the series; tick-first rounding
    keeps the same clean labels without throwing away half the plot.
    """
    if q_max <= 0 or math.isnan(q_max):
        return 1.0
    raw_step = q_max / 5
    magnitude: float = 10.0 ** math.floor(math.log10(raw_step))
    normalized = raw_step / magnitude
    if normalized <= 1:
        step = 1.0
    elif normalized <= 2:
        step = 2.0
    elif normalized <= 5:
        step = 5.0
    else:
        step = 10.0
    increment = step * magnitude
    return math.ceil((q_max * 1.02) / increment) * increment


def _nice_step(raw: float) -> float:
    """Return a 1/2/5 step at least as large as ``raw``."""
    if raw <= 0 or math.isnan(raw):
        return 1.0
    magnitude = 10.0 ** math.floor(math.log10(raw))
    normalized = raw / magnitude
    if normalized <= 1:
        step = 1.0
    elif normalized <= 2:
        step = 2.0
    elif normalized <= 5:
        step = 5.0
    else:
        step = 10.0
    return step * magnitude


def _axis_bounds(values: list[float], zero_baseline: bool) -> tuple[float, float]:
    """Choose readable bounds, retaining zero unless the metric is an index."""
    if not values:
        return 0.0, 1.0
    q_min, q_max = min(values), max(values)
    if zero_baseline or q_min <= 0:
        return 0.0, _nice_axis_top(q_max)
    spread = q_max - q_min
    if spread == 0:
        spread = max(abs(q_max) * 0.1, 1.0)
    padding = spread * 0.08
    step = _nice_step((spread + 2 * padding) / 5)
    bottom = math.floor((q_min - padding) / step) * step
    top = math.ceil((q_max + padding) / step) * step
    if top <= bottom:
        top = bottom + step
    return bottom, top


def _tick(decade: str) -> str:
    return f"’{decade[2:4]}s"


def _decade_labels(points: tuple[ArcPoint, ...]) -> tuple[str, ...]:
    """Return x-axis labels for the given points.

    Use the short “’50s” form unless the arc spans both the 1900s and 2000s,
    in which case render full “1900s” / “2020s” labels to avoid ambiguity.
    """
    has_19 = any(p.decade.startswith("19") for p in points)
    has_20 = any(p.decade.startswith("20") for p in points)
    if has_19 and has_20:
        return tuple(f"{p.decade}" for p in points)
    return tuple(_tick(p.decade) for p in points)


def arc_chart(
    points: tuple[ArcPoint, ...],
    unit: str,
    falling: bool = False,
    width: int = 880,
    height: int = 230,
) -> str:
    """A cross-decade arc: dots for sourced quantities, dashed slots for gaps.

    The x axis carries every registry decade; y spans zero to just above the
    maximum. Dots deep-link to their placards and carry native ``<title>``
    tooltips; tier letters ride under the axis in the honesty colors.
    """
    stroke = tokens.COPPER if falling else tokens.BRASS
    pad_l, pad_r, pad_t, pad_b = 52, 18, 16, 44
    plot_w, plot_h = width - pad_l - pad_r, height - pad_t - pad_b
    n = len(points)
    if n == 0:
        return ""
    step = plot_w / max(n - 1, 1)
    quantities = [p.quantity for p in points if p.quantity is not None]
    q_max = max(quantities) if quantities else 1.0
    q_top = _nice_axis_top(q_max)

    def x_of(i: int) -> float:
        return pad_l + (i * step if n > 1 else plot_w / 2)

    def y_of(q: float) -> float:
        return pad_t + plot_h * (1 - q / q_top)

    svg_open = (
        f'<svg class="arc" viewBox="0 0 {width} {height}" role="img" '
        f'aria-label={quoteattr(f"Cross-decade arc, {unit}")}>'
    )
    out: list[str] = [svg_open]
    # recessive gridlines + y captions
    for frac in (0.0, 0.5, 1.0):
        gy = pad_t + plot_h * (1 - frac)
        out.append(
            f'<line class="grid" x1="{pad_l}" y1="{gy:.1f}" x2="{width - pad_r}" y2="{gy:.1f}"/\u003e'
        )
        out.append(
            f'<text class="ylab" x="{pad_l - 8}" y="{gy + 3:.1f}">{_fmt(q_top * frac)}</text>'
        )
    out.append(f'<text class="unit" x="{pad_l}" y="{pad_t - 4}">{escape(unit)}</text>')
    # reserve the bottom 22px of plot area for x-axis labels; don't place a
    # value label below this band when it would overlap.
    x_label_ceiling = height - pad_b + 4  # just above the decade label row

    # connecting line: solid between adjacent sourced points, dashed across gaps
    prev: tuple[int, ArcPoint] | None = None
    for i, p in enumerate(points):
        if p.quantity is None:
            continue
        if prev is not None:
            j, q = prev
            index_gap = i - j > 1
            year_gap = abs((p.year or 0) - (q.year or 0)) > 20 if (p.year and q.year) else False
            if year_gap and not index_gap:
                # large temporal gap between adjacent points — render a visual
                # break: wide dash, lower opacity, "no data" label in the gap
                mid_x = (x_of(j) + x_of(i)) / 2
                mid_y = (y_of(q.quantity or 0) + y_of(p.quantity)) / 2
                out.append(
                    f'<line class="join" x1="{x_of(j):.1f}" y1="{y_of(q.quantity or 0):.1f}" '
                    f'x2="{x_of(i):.1f}" y2="{y_of(p.quantity):.1f}" '
                    f'stroke="{stroke}" stroke-dasharray="2 6" opacity="0.4"/>'
                )
                out.append(
                    f'<text class="gaplab" x="{mid_x:.1f}" y="{mid_y:.1f}" '
                    f'style="fill:{tokens.GAP}">no data</text>'
                )
            elif index_gap:
                out.append(
                    f'<line class="join" x1="{x_of(j):.1f}" y1="{y_of(q.quantity or 0):.1f}" '
                    f'x2="{x_of(i):.1f}" y2="{y_of(p.quantity):.1f}" '
                    f'stroke="{stroke}" stroke-dasharray="4 5"/>'
                )
            else:
                out.append(
                    f'<line class="join" x1="{x_of(j):.1f}" y1="{y_of(q.quantity or 0):.1f}" '
                    f'x2="{x_of(i):.1f}" y2="{y_of(p.quantity):.1f}" stroke="{stroke}"/>'
                )
        prev = (i, p)

    label_all = len(quantities) <= 8
    extremes = {q_max, min(quantities)} if quantities else set()
    x_labels = _decade_labels(points)
    for i, p in enumerate(points):
        cx = x_of(i)
        out.append(f'<text class="xlab" x="{cx:.1f}" y="{height - 26}">{x_labels[i]}</text>')
        if p.quantity is None:
            gy = pad_t + plot_h
            out.append(
                f'<a href={quoteattr(f"#{p.fact_id}--modal")}><g data-fact-id={quoteattr(p.fact_id)}>'
                f'<title>{escape(p.label)}: {escape(p.value)} — see the placard</title>'
                f'<circle class="gapdot" cx="{cx:.1f}" cy="{gy:.1f}" r="5"/>'
                f'<text class="gaplab" x="{cx:.1f}" y="{height - 12}">gap</text></g></a>'
            )
            continue
        cy = y_of(p.quantity)
        tier_color = tokens.TIER_COLORS.get(p.tier, tokens.GAP)
        show_label = label_all or (p.quantity in extremes) or i in (0, n - 1)
        # label above the dot by default; if there's no room, place it below
        label_y = cy - 9
        if show_label and label_y < x_label_ceiling:
            label_y = cy + 18
        out.append(
            f'<a href={quoteattr(f"#{p.fact_id}--modal")}><g data-fact-id={quoteattr(p.fact_id)}>'
            f"<title>{escape(p.label)}: {escape(p.value)} — Tier {p.tier}</title>"
            f'<circle class="dot" cx="{cx:.1f}" cy="{cy:.1f}" r="4.5" fill="{stroke}"/>'
            + (
                f'<text class="vlab" x="{cx:.1f}" y="{label_y:.1f}">{_fmt(p.quantity)}</text>'
                if show_label
                else ""
            )
            + f'<text class="tlet" x="{cx:.1f}" y="{height - 12}" '
            f'fill="{tier_color}">{p.tier}</text></g></a>'
        )
    out.append("</svg>")
    return "".join(out)


def multi_arc_chart(
    series: tuple[ArcSeries, ...],
    unit: str,
    width: int = 880,
    height: int = 250,
) -> str:
    """Related decade arcs on one scale, with linked gaps and a legend.

    A shared scale prevents a smaller series from acquiring the same apparent
    amplitude as a larger one through independent y-axes. Every point remains
    a fact-backed mark.
    """
    if not series:
        return ""
    decades = sorted({p.decade for item in series for p in item.points})
    if not decades:
        return ""
    by_series = [{p.decade: p for p in item.points} for item in series]
    quantities = [
        p.quantity
        for item in series
        for p in item.points
        if p.quantity is not None
    ]
    q_top = _nice_axis_top(max(quantities) if quantities else 1.0)
    pad_l, pad_r, pad_t, pad_b = 52, 18, 34, 44
    plot_w, plot_h = width - pad_l - pad_r, height - pad_t - pad_b
    step = plot_w / max(len(decades) - 1, 1)
    decade_index = {decade: i for i, decade in enumerate(decades)}

    def x_of(decade: str) -> float:
        i = decade_index[decade]
        return pad_l + (i * step if len(decades) > 1 else plot_w / 2)

    def y_of(q: float) -> float:
        return pad_t + plot_h * (1 - q / q_top)

    out: list[str] = [
        f'<svg class="arc multi-arc" viewBox="0 0 {width} {height}" role="img" '
        f'aria-label={quoteattr(f"Shared-axis cross-decade arc, {unit}")}>'
    ]
    legend_x = pad_l
    for item in series:
        out.append(
            f'<line x1="{legend_x}" y1="12" x2="{legend_x + 20}" y2="12" '
            f'stroke="{item.color}" stroke-width="2.5"/>'
            f'<text class="unit" x="{legend_x + 26}" y="15">{escape(item.label)}</text>'
        )
        legend_x += 112
    out.append(f'<text class="unit" x="{pad_l + 250}" y="15">{escape(unit)}</text>')
    for frac in (0.0, 0.5, 1.0):
        gy = pad_t + plot_h * (1 - frac)
        out.append(
            f'<line class="grid" x1="{pad_l}" y1="{gy:.1f}" '
            f'x2="{width - pad_r}" y2="{gy:.1f}"/>'
            f'<text class="ylab" x="{pad_l - 8}" y="{gy + 3:.1f}">'
            f'{_fmt(q_top * frac)}</text>'
        )

    # Lines first, marks second. A missing/non-comparable decade breaks the
    # line; the next comparable point reconnects with a dashed segment.
    for item, point_map in zip(series, by_series, strict=True):
        previous: tuple[int, ArcPoint] | None = None
        for i, decade in enumerate(decades):
            point = point_map.get(decade)
            if point is None or point.quantity is None:
                continue
            if previous is not None:
                j, prior = previous
                dash = ' stroke-dasharray="4 5"' if i - j > 1 else ""
                out.append(
                    f'<line class="join" x1="{x_of(prior.decade):.1f}" '
                    f'y1="{y_of(prior.quantity or 0):.1f}" x2="{x_of(decade):.1f}" '
                    f'y2="{y_of(point.quantity):.1f}" stroke="{item.color}"{dash}/>'
                )
            previous = (i, point)

    label_points = tuple(
        ArcPoint(d, "", "", "", "", "", None) for d in decades
    )
    x_labels = _decade_labels(label_points)
    for i, decade in enumerate(decades):
        cx = x_of(decade)
        out.append(f'<text class="xlab" x="{cx:.1f}" y="{height - 26}">{x_labels[i]}</text>')
        for series_i, (item, point_map) in enumerate(
            zip(series, by_series, strict=True)
        ):
            point = point_map.get(decade)
            if point is None:
                continue
            offset = (series_i - (len(series) - 1) / 2) * 8
            tier_color = tokens.TIER_COLORS.get(point.tier, tokens.GAP)
            if point.quantity is None:
                gy = pad_t + plot_h
                out.append(
                    f'<a href={quoteattr(f"#{point.fact_id}--modal")}>'
                    f'<g data-fact-id={quoteattr(point.fact_id)}>'
                    f'<title>{escape(point.label)}: not comparable on this axis; '
                    f'{escape(point.value)}</title>'
                    f'<circle class="gapdot" cx="{cx + offset:.1f}" cy="{gy:.1f}" '
                    f'r="4" style="stroke:{item.color}"/>'
                    f'<text class="tlet" x="{cx + offset:.1f}" y="{height - 12}" '
                    f'fill="{tier_color}">{point.tier}</text></g></a>'
                )
                continue
            cy = y_of(point.quantity)
            show_label = decade in (decades[0], decades[-1])
            out.append(
                f'<a href={quoteattr(f"#{point.fact_id}--modal")}>'
                f'<g data-fact-id={quoteattr(point.fact_id)}>'
                f'<title>{escape(point.label)}: {escape(point.value)} — Tier {point.tier}</title>'
                f'<circle class="dot" cx="{cx:.1f}" cy="{cy:.1f}" r="4.5" '
                f'fill="{item.color}"/>'
                + (
                    f'<text class="vlab" x="{cx:.1f}" y="{cy - 9:.1f}">'
                    f'{_fmt(point.quantity)}</text>'
                    if show_label
                    else ""
                )
                + f'<text class="tlet" x="{cx + offset:.1f}" y="{height - 12}" '
                f'fill="{tier_color}">{point.tier}</text></g></a>'
            )
    out.append("</svg>")
    return "".join(out)


def arc_chart_series(
    series_values: dict[int, float],
    markers: tuple[ArcPoint, ...],
    unit: str,
    series_id: str = "",
    falling: bool = False,
    width: int = 880,
    height: int = 230,
) -> str:
    """A year-axis arc backed by an annual series — plan 010 WI-4.

    The x axis is calendar years (decade-boundary ticks); the annual series
    draws as a faint line of small dots, and the curated decade facts render
    as larger labeled brass markers on top — the same ``data-fact-id``/
    placard-link contract as the decade arc. Series points are the series's
    voice, not curated facts, so they carry ``data-series-id`` (provenance
    via the series source, named in the tooltip) and never ``data-fact-id``.

    Years without a series value are simply absent (render the gap).
    """
    stroke = tokens.COPPER if falling else tokens.BRASS
    pad_l, pad_r, pad_t, pad_b = 52, 18, 16, 44
    plot_w, plot_h = width - pad_l - pad_r, height - pad_t - pad_b

    years = sorted(series_values)
    if not years:
        return ""
    # The x domain spans the annual series; decade markers whose year falls
    # outside it clamp to the nearest edge so they remain visible.
    y_min, y_max = years[0], years[-1]
    all_vals = list(series_values.values()) + [
        m.quantity for m in markers if m.quantity is not None
    ]
    q_max = max(all_vals) if all_vals else 1.0
    q_top = _nice_axis_top(q_max)
    domain = max(y_max - y_min, 1)

    def x_of(year: int) -> float:
        clamped = min(max(year, y_min), y_max)
        return pad_l + plot_w * (clamped - y_min) / domain

    def y_of(q: float) -> float:
        return pad_t + plot_h * (1 - q / q_top)

    out: list[str] = [
        f'<svg class="arc arc-series" viewBox="0 0 {width} {height}" role="img" '
        f'aria-label={quoteattr(f"Annual arc, {unit}")}>'
    ]
    # gridlines + y captions
    for frac in (0.0, 0.5, 1.0):
        gy = pad_t + plot_h * (1 - frac)
        out.append(
            f'<line class="grid" x1="{pad_l}" y1="{gy:.1f}" x2="{width - pad_r}" y2="{gy:.1f}"/\u003e'
        )
        out.append(
            f'<text class="ylab" x="{pad_l - 8}" y="{gy + 3:.1f}">{_fmt(q_top * frac)}</text>'
        )
    out.append(f'<text class="unit" x="{pad_l}" y="{pad_t - 4}">{escape(unit)}</text>')

    # decade-boundary x ticks
    tick_start = (y_min // 10) * 10 + 10
    for tick_year in range(tick_start, y_max + 1, 10):
        tx = x_of(tick_year)
        out.append(f'<text class="xlab" x="{tx:.1f}" y="{height - 26}">{tick_year}</text>')

    # One polyline per contiguous run. A missing year is a real gap, not
    # permission to draw an interpolating bridge.
    line_pts = [(x_of(yr), y_of(series_values[yr])) for yr in years]
    run: list[int] = []
    for year in years:
        if run and year != run[-1] + 1:
            if len(run) > 1:
                path = " ".join(
                    f"{x_of(yr):.1f},{y_of(series_values[yr]):.1f}" for yr in run
                )
                out.append(
                    f'<polyline class="series-line" points="{path}" fill="none" '
                    f'stroke="{stroke}" stroke-opacity="0.35" stroke-width="1.5"/>'
                )
            run = []
        run.append(year)
    if len(run) > 1:
        path = " ".join(
            f"{x_of(yr):.1f},{y_of(series_values[yr]):.1f}" for yr in run
        )
        out.append(
            f'<polyline class="series-line" points="{path}" fill="none" '
            f'stroke="{stroke}" stroke-opacity="0.35" stroke-width="1.5"/>'
        )
    for x, yy in line_pts:
        out.append(
            f'<circle data-series-id={quoteattr(series_id)} '
            f'cx="{x:.1f}" cy="{yy:.1f}" r="1.6" fill="{stroke}" fill-opacity="0.5"/>'
        )

    # decade-fact markers on top (data-fact-id → mark-coverage gate)
    for m in markers:
        mx = x_of(m.year) if m.year else pad_l + plot_w / 2
        if m.quantity is None:
            gy = pad_t + plot_h
            out.append(
                f'<a href={quoteattr(f"#{m.fact_id}--modal")}><g data-fact-id={quoteattr(m.fact_id)}>'
                f'<title>{escape(m.label)}: {escape(m.value)} — see the placard</title>'
                f'<circle class="gapdot" cx="{mx:.1f}" cy="{gy:.1f}" r="5"/></g></a>'
            )
            continue
        my = y_of(m.quantity)
        tier_color = tokens.TIER_COLORS.get(m.tier, tokens.GAP)
        out.append(
            f'<a href={quoteattr(f"#{m.fact_id}--modal")}><g data-fact-id={quoteattr(m.fact_id)}>'
            f"<title>{escape(m.label)}: {escape(m.value)} — Tier {m.tier}</title>"
            f'<circle class="dot" cx="{mx:.1f}" cy="{my:.1f}" r="4.5" '
            f'fill="ivory" stroke="{stroke}" stroke-width="2"/>'
            f'<text class="vlab" x="{mx:.1f}" y="{my - 9:.1f}">{_fmt(m.quantity)}</text>'
            f'<text class="tlet" x="{mx:.1f}" y="{height - 12}" fill="{tier_color}">{m.tier}</text>'
            f"</g></a>"
        )
    out.append("</svg>")
    return "".join(out)


@dataclass(frozen=True, slots=True)
class Recession:
    """One NBER recession band, in fractional years (1973.92 = Dec 1973)."""

    peak: float
    trough: float


@dataclass(frozen=True, slots=True)
class MetricMarker:
    """A decade fact drawn as a labeled marker on an affordability chart."""

    year: int
    fact_id: str
    href: str
    tier: str
    label: str
    value: str
    quantity: float | None


def affordability_chart(
    values: dict[int, float],
    recessions: tuple[Recession, ...],
    unit: str,
    metric_slug: str = "",
    falling: bool = False,
    markers: tuple[MetricMarker, ...] = (),
    zero_baseline: bool = True,
    width: int = 880,
    height: int = 260,
) -> str:
    """A year-axis affordability metric — Plan 011 WI-2.

    The ratio line draws as connected dots (one per year both series cover);
    NBER recessions render as copper-tinted bands behind the line
    (annotation, no ``data-fact-id`` — their provenance is the dashboard
    footer citation). Direct-mode decade facts (e.g. food share) render as
    labeled markers carrying ``data-fact-id`` (mark-coverage gate). Years
    without data are absent — render the gap.
    """
    stroke = tokens.COPPER if falling else tokens.BRASS
    pad_l, pad_r, pad_t, pad_b = 52, 18, 18, 44
    plot_w, plot_h = width - pad_l - pad_r, height - pad_t - pad_b

    all_pts = list(values.items()) + [
        (m.year, m.quantity) for m in markers if m.quantity is not None
    ]
    if not all_pts:
        return ""
    all_years = set(values) | {m.year for m in markers}
    y_min = min(all_years)
    y_max = max(all_years)
    domain = max(y_max - y_min, 1)
    q_vals = [v for _, v in all_pts]
    q_bottom, q_top = _axis_bounds(q_vals, zero_baseline)
    years = sorted(values)

    def x_of(year: float) -> float:
        return pad_l + plot_w * (min(max(year, y_min), y_max) - y_min) / domain

    def y_of(q: float) -> float:
        return pad_t + plot_h * (1 - (q - q_bottom) / (q_top - q_bottom))

    out: list[str] = [
        f'<svg class="arc afford-chart" id="metric-{escape(metric_slug)}" '
        f'viewBox="0 0 {width} {height}" role="img" '
        f'aria-label={quoteattr(f"Affordability metric, {unit}")}>'
    ]
    # recession bands (annotation — no data-fact-id)
    for rec in recessions:
        if rec.trough < y_min or rec.peak > y_max:
            continue
        x1 = x_of(max(rec.peak, y_min))
        x2 = x_of(min(rec.trough, y_max))
        out.append(
            f'<rect class="recession" x="{x1:.1f}" y="{pad_t}" '
            f'width="{x2 - x1:.1f}" height="{plot_h}" fill="{tokens.COPPER}" '
            f'fill-opacity="0.10"/>'
        )
    # gridlines + y captions
    for frac in (0.0, 0.5, 1.0):
        gy = pad_t + plot_h * (1 - frac)
        out.append(
            f'<line class="grid" x1="{pad_l}" y1="{gy:.1f}" x2="{width - pad_r}" y2="{gy:.1f}"/\u003e'
        )
        out.append(
            f'<text class="ylab" x="{pad_l - 8}" y="{gy + 3:.1f}">'
            f'{_fmt(q_bottom + (q_top - q_bottom) * frac)}</text>'
        )
    out.append(f'<text class="unit" x="{pad_l}" y="{pad_t - 5}">{escape(unit)}</text>')
    # decade-boundary x ticks
    for tick_year in range((y_min // 10) * 10 + 10, y_max + 1, 10):
        tx = x_of(tick_year)
        out.append(f'<text class="xlab" x="{tx:.1f}" y="{height - 26}">{tick_year}</text>')

    # the ratio line + dots (computed — data-metric-id, never data-fact-id)
    if len(years) > 1:
        path = " ".join(f"{x_of(yr):.1f},{y_of(values[yr]):.1f}" for yr in years)
        out.append(
            f'<polyline class="series-line" points="{path}" fill="none" '
            f'stroke="{stroke}" stroke-width="2"/>'
        )
    for yr in years:
        out.append(
            f'<circle data-metric-id={quoteattr(metric_slug)} cx="{x_of(yr):.1f}" '
            f'cy="{y_of(values[yr]):.1f}" r="2.5" fill="{stroke}">'
            f"<title>{yr}: {_fmt(values[yr])} {escape(unit)}</title></circle>"
        )

    # Direct-mode facts have no annual line. Connect adjacent survey points
    # so the trajectory is legible, using a subdued dashed bridge across a
    # multi-decade hole rather than implying annual observations.
    direct = sorted(
        (m for m in markers if m.quantity is not None), key=lambda m: m.year
    )
    for prior, current in pairwise(direct):
        dash = (
            ' stroke-dasharray="4 5" opacity="0.6"'
            if current.year - prior.year > 15
            else ""
        )
        out.append(
            f'<line class="join direct-series" x1="{x_of(prior.year):.1f}" '
            f'y1="{y_of(prior.quantity or 0):.1f}" x2="{x_of(current.year):.1f}" '
            f'y2="{y_of(current.quantity or 0):.1f}" stroke="{stroke}"{dash}/>'
        )

    # direct-mode decade markers (facts — data-fact-id → mark-coverage gate)
    label_all = len(markers) <= 8
    for m in markers:
        mx = x_of(m.year)
        tier_color = tokens.TIER_COLORS.get(m.tier, tokens.GAP)
        if m.quantity is None:
            gy = pad_t + plot_h
            out.append(
                f'<a href={quoteattr(m.href)}><g data-fact-id={quoteattr(m.fact_id)}>'
                f'<title>{escape(m.label)}: {escape(m.value)} — see the placard</title>'
                f'<circle class="gapdot" cx="{mx:.1f}" cy="{gy:.1f}" r="5"/>'
                f'<text class="gaplab" x="{mx:.1f}" y="{height - 12}">gap</text></g></a>'
            )
            continue
        my = y_of(m.quantity)
        out.append(
            f'<a href={quoteattr(m.href)}><g data-fact-id={quoteattr(m.fact_id)}>'
            f"<title>{escape(m.label)}: {escape(m.value)} — Tier {m.tier}</title>"
            f'<circle class="dot" cx="{mx:.1f}" cy="{my:.1f}" r="4.5" '
            f'fill="ivory" stroke="{stroke}" stroke-width="2"/>'
            + (f'<text class="vlab" x="{mx:.1f}" y="{my - 9:.1f}">{_fmt(m.quantity)}</text>'
               if label_all else "")
            + f'<text class="tlet" x="{mx:.1f}" y="{height - 12}" fill="{tier_color}">{m.tier}</text>'
            f"</g></a>"
        )
    out.append("</svg>")
    return "".join(out)


def composition_bar(
    decade: str,
    segments: tuple[ShareSegment, ...],
    width: int = 880,
    bar_h: int = 26,
) -> str:
    """One decade's stacked expenditure bar, fixed palette, 2px surface gaps.

    Direct labels are mandatory (the ivory-variant WARN's relief): every
    segment is named with its percentage in the caption row; segments wide
    enough also carry the number inline.
    """
    pad_l = 52
    plot_w = width - pad_l - 16
    height = bar_h + 26
    out = [
        f'<svg class="comp" viewBox="0 0 {width} {height}" role="img" '
        f"aria-label={quoteattr(f'Expenditure composition, {decade}')}>"
    ]
    out.append(f'<text class="xlab" x="{pad_l - 8}" y="{bar_h / 2 + 4}" '
               f'style="text-anchor:end">{_tick(decade)}</text>')
    x = float(pad_l)
    total = sum(s.pct for s in segments)
    scale = plot_w / max(total, 100.0)
    for s in segments:
        w = max(s.pct * scale - 2, 1.5)  # 2px surface gap
        color = tokens.COMPOSITION_DARK[s.slot]
        out.append(
            f'<a href={quoteattr(f"#{s.fact_id}--modal")}><g data-fact-id={quoteattr(s.fact_id)}>'
            f"<title>{escape(s.category)}: {s.pct:g}% — {decade}</title>"
            f'<rect x="{x:.1f}" y="0" width="{w:.1f}" height="{bar_h}" rx="2" fill="{color}"/>'
            + (
                f'<text class="seglab" x="{x + w / 2:.1f}" y="{bar_h / 2 + 3.5}">{s.pct:g}</text>'
                if w > 34
                else ""
            )
            + "</g></a>"
        )
        x += s.pct * scale
    # caption row: the mandatory direct labels
    caption = " · ".join(f"{s.category} {s.pct:g}%" for s in segments)
    out.append(f'<text class="caplab" x="{pad_l}" y="{bar_h + 17}">{escape(caption)}</text>')
    out.append("</svg>")
    return "".join(out)


def hours_meter(
    bars: tuple[MeterBar, ...], unit: str, width: int = 880, overlay_links: bool = False
) -> str:
    """The labour-hours meter — horizontal bars drawn to the data's shape.

    Falling metric → copper. A decade whose fact carries no single honest
    quantity (the 1990s/2010s Ramey gap, the 2020s concept splice) renders a
    dashed empty track with the words, at full row height. When
    ``overlay_links`` is true, click targets open the CSS-only popup layer.
    """
    row_h, pad_l, pad_r = 30, 52, 170
    plot_w = width - pad_l - pad_r
    height = len(bars) * row_h + 24
    quantities = [b.quantity for b in bars if b.quantity is not None]
    q_max = max(quantities) if quantities else 1.0
    out = [
        f'<svg class="meter" viewBox="0 0 {width} {height}" role="img" '
        f"aria-label={quoteattr(f'Labour-hours meter, {unit}')}>"
    ]
    out.append(f'<text class="unit" x="{pad_l}" y="12">{escape(unit)}</text>')
    y = 18.0
    for b in bars:
        cy = y + row_h / 2
        out.append(
            f'<text class="xlab" x="{pad_l - 8}" y="{cy + 3:.1f}" '
            f'style="text-anchor:end">{_tick(b.decade)}</text>'
        )
        href = f"#{b.fact_id}--modal" if overlay_links else b.href
        if b.quantity is None:
            out.append(
                f'<a href={quoteattr(href)}><g data-fact-id={quoteattr(b.fact_id)}>'
                f"<title>{escape(b.label)}: {escape(b.value)}</title>"
                f'<rect class="gaptrack" x="{pad_l}" y="{cy - 7:.1f}" width="{plot_w}" '
                f'height="14" rx="4"/>'
                f'<text class="gaplab" x="{pad_l + plot_w + 10}" y="{cy + 3:.1f}" '
                f'style="text-anchor:start">{escape(b.note or "no reliable record")}</text></g></a>'
            )
        else:
            w = plot_w * b.quantity / (q_max * 1.02)
            tier_color = tokens.TIER_COLORS.get(b.tier, tokens.GAP)
            out.append(
                f'<a href={quoteattr(href)}><g data-fact-id={quoteattr(b.fact_id)}>'
                f"<title>{escape(b.label)}: {escape(b.value)} — Tier {b.tier}</title>"
                f'<rect x="{pad_l}" y="{cy - 7:.1f}" width="{w:.1f}" height="14" rx="4" '
                f'fill="{tokens.COPPER}"/>'
                f'<text class="vlab" x="{pad_l + w + 8:.1f}" y="{cy + 3:.1f}" '
                f'style="text-anchor:start">{_fmt(b.quantity)} '
                f'<tspan fill="{tier_color}">{b.tier}</tspan></text></g></a>'
            )
        y += row_h
    out.append("</svg>")
    return "".join(out)


# ── the room stage ────────────────────────────────────────────────────────────

# artifact → cutaway position, carried from the demo's composition
# positions map to the four house zones: parlor (upper-left), rooms (upper-right),
# kitchen (lower-left), bath & heat (lower-right). Each glyph sits in its
# semantic zone, spaced on a loose grid to avoid overlap.
STAGE_POS: dict[str, tuple[int, int]] = {
    "tenure": (400, 140),
    "rooms": (490, 250),
    "electricity": (240, 215),
    "radio": (200, 275),
    "television": (300, 275),
    "telephone": (350, 240),
    "refrigerator": (200, 360),
    "food": (300, 395),
    "plumbing": (460, 365),
    "heating": (560, 395),
    "air-conditioning": (600, 210),
    "cable": (490, 330),
    "computer": (530, 275),
    "internet": (600, 290),
    "automobile": (700, 405),
    "washing-machine": (350, 365),
    "stove": (350, 395),
}


@dataclass(frozen=True, slots=True)
class ZoneNote:
    """A budget share rendered spatially — an annotation on a cutaway zone."""

    text: str
    x: int
    y: int
    fact_id: str
    href: str


@dataclass(frozen=True, slots=True)
class Stage:
    """Everything the stage draws for one room."""

    decade: str
    artifacts: tuple[StageArtifact, ...]
    zone_notes: tuple[ZoneNote, ...] = field(default=())
    home_scale: float = 1.0  # scale factor for the house outline (floor-area datum)


def stage_svg(stage: Stage, overlay_links: bool = False) -> str:
    """The dark-gallery house cutaway with era-graded light.

    The spotlight tint per decade is the mood channel (design-spec); glyph
    opacity is the diffusion datum; a fact with no quantity keeps the dashed
    gap ring. Every glyph links to its placard. When ``overlay_links`` is true
    the click target is the CSS-only popup layer (``#fact-id--modal``) rather
    than the room placard.

    ``stage.home_scale`` proportionally scales the house outline (structure,
    zone labels, zone notes, artifact positions) so the visitor sees the home
    grow across decades — anchored to the sourced floor-area datum.
    """
    glow = tokens.ERA_GLOW.get(stage.decade, tokens.ERA_GLOW_DEFAULT)
    rx, ry = tokens.ERA_POOL.get(stage.decade, tokens.ERA_POOL_DEFAULT)
    s = stage.home_scale
    # scale house geometry around its center (x=400, y=306 — mid-body)
    cx, cy = 400, 306

    def sx(x: float) -> float:
        return cx + (x - cx) * s

    def sy(y: float) -> float:
        return cy + (y - cy) * s

    out = [
        '<svg class="house" viewBox="0 0 800 560" role="img" '
        f"aria-label={quoteattr(f'Schematic cutaway of the composite home, {stage.decade}')}>"
        "<defs>"
        f'<radialGradient id="stagelight" cx="50%" cy="16%" r="{max(rx, ry)}%">'
        f'<stop offset="0%" stop-color="{glow}"/>'
        f'<stop offset="44%" stop-color="{tokens.CASE}"/>'
        f'<stop offset="100%" stop-color="{tokens.GROUND}"/>'
        "</radialGradient></defs>"
        '<rect x="0" y="0" width="800" height="560" fill="url(#stagelight)"/>'
        '<g class="structure">'
        f'<polygon points="{sx(120):.0f},{sy(182):.0f} {sx(400):.0f},{sy(90):.0f} {sx(680):.0f},{sy(182):.0f}"/>'
        f'<rect x="{sx(150):.0f}" y="{sy(182):.0f}" width="{500*s:.0f}" height="{248*s:.0f}"/>'
        f'<line x1="{sx(400):.0f}" y1="{sy(182):.0f}" x2="{sx(400):.0f}" y2="{sy(430):.0f}"/>'
        f'<line x1="{sx(150):.0f}" y1="{sy(306):.0f}" x2="{sx(650):.0f}" y2="{sy(306):.0f}"/>'
        f'<rect x="{sx(452):.0f}" y="{sy(122):.0f}" width="{34*s:.0f}" height="{60*s:.0f}"/>'
        "</g>"
        f'<line class="groundline" x1="{sx(80):.0f}" y1="{sy(430):.0f}" x2="{sx(720):.0f}" y2="{sy(430):.0f}"/>'
        f'<text class="zlabel" x="{sx(172):.0f}" y="{sy(202):.0f}">parlor</text>'
        f'<text class="zlabel" x="{sx(470):.0f}" y="{sy(202):.0f}">rooms</text>'
        f'<text class="zlabel" x="{sx(172):.0f}" y="{sy(326):.0f}">kitchen</text>'
        f'<text class="zlabel" x="{sx(470):.0f}" y="{sy(326):.0f}">bath &amp; heat</text>'
    ]
    for note in stage.zone_notes:
        nx, ny = sx(note.x), sy(note.y)
        anchor = ' style="text-anchor:end"' if note.x > 620 else ""
        out.append(
            f'<a href={quoteattr(note.href)}>'
            f'<text class="znote" x="{nx:.0f}" y="{ny:.0f}"{anchor} '
            f"data-fact-id={quoteattr(note.fact_id)}>{escape(note.text)}</text></a>"
        )
    for a in stage.artifacts:
        ax, ay = sx(a.x), sy(a.y)
        if a.kind == "stat":
            opacity, ring = 0.95, '<circle class="ring" r="17"/>'
            pct = ""
        elif a.quantity is None:
            opacity, ring = 0.5, '<circle class="ring gapring" r="17"/>'
            pct = '<text class="pct gap">gap</text>'
        else:
            opacity = tokens.glyph_opacity(a.quantity)
            ring = '<circle class="ring" r="17"/>'
            pct = f'<text class="pct">{_fmt(a.quantity)}%</text>'
        # invisible hitbox covers the ring and the glyph bounding box so the
        # whole artifact area is clickable, not just the drawn strokes
        hitbox = (
            '<rect x="-18" y="-18" width="36" height="36" fill="transparent" '
            'stroke="none"/>'
        )
        href = f"#{a.fact_id}--modal" if overlay_links else a.href
        out.append(
            f"<a href={quoteattr(href)}>"
            f'<g class="hs" transform="translate({ax:.0f},{ay:.0f})" '
            f"data-fact-id={quoteattr(a.fact_id)}>"
            f"<title>{escape(a.label)}: {escape(a.value)}</title>"
            f"{hitbox}{ring}"
            f'<g class="glyphwrap" style="opacity:{opacity:.2f}">{a.glyph_svg}</g>'
            f'<g transform="translate(0,30)">{pct}</g>'
            "</g></a>"
        )
    out.append("</svg>")
    return "".join(out)
