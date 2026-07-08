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

import re
from dataclasses import dataclass, field
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


def _tick(decade: str) -> str:
    return f"’{decade[2:4]}s"


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
    q_top = q_max * 1.08 if q_max > 0 else 1.0

    def x_of(i: int) -> float:
        return pad_l + (i * step if n > 1 else plot_w / 2)

    def y_of(q: float) -> float:
        return pad_t + plot_h * (1 - q / q_top)

    out: list[str] = [
        f'<svg class="arc" viewBox="0 0 {width} {height}" role="img" '
        f"aria-label={quoteattr(f'Cross-decade arc, {unit}')}>"
    ]
    # recessive gridlines + y captions
    for frac in (0.0, 0.5, 1.0):
        gy = pad_t + plot_h * (1 - frac)
        out.append(
            f'<line class="grid" x1="{pad_l}" y1="{gy:.1f}" x2="{width - pad_r}" y2="{gy:.1f}"/>'
        )
        out.append(
            f'<text class="ylab" x="{pad_l - 8}" y="{gy + 3:.1f}">{_fmt(q_top * frac)}</text>'
        )
    out.append(f'<text class="unit" x="{pad_l}" y="{pad_t - 4}">{escape(unit)}</text>')

    # connecting line: solid between adjacent sourced points, dashed across gaps
    prev: tuple[int, ArcPoint] | None = None
    for i, p in enumerate(points):
        if p.quantity is None:
            continue
        if prev is not None:
            j, q = prev
            dashed = ' stroke-dasharray="4 5"' if i - j > 1 else ""
            out.append(
                f'<line class="join" x1="{x_of(j):.1f}" y1="{y_of(q.quantity or 0):.1f}" '
                f'x2="{x_of(i):.1f}" y2="{y_of(p.quantity):.1f}" stroke="{stroke}"{dashed}/>'
            )
        prev = (i, p)

    label_all = len(quantities) <= 8
    extremes = {q_max, min(quantities)} if quantities else set()
    for i, p in enumerate(points):
        cx = x_of(i)
        out.append(f'<text class="xlab" x="{cx:.1f}" y="{height - 26}">{_tick(p.decade)}</text>')
        if p.quantity is None:
            gy = pad_t + plot_h
            out.append(
                f'<a href={quoteattr(p.href)}><g data-fact-id={quoteattr(p.fact_id)}>'
                f'<title>{escape(p.label)}: {escape(p.value)} — see the placard</title>'
                f'<circle class="gapdot" cx="{cx:.1f}" cy="{gy:.1f}" r="5"/>'
                f'<text class="gaplab" x="{cx:.1f}" y="{height - 12}">gap</text></g></a>'
            )
            continue
        cy = y_of(p.quantity)
        tier_color = tokens.TIER_COLORS.get(p.tier, tokens.GAP)
        show_label = label_all or (p.quantity in extremes) or i in (0, n - 1)
        out.append(
            f'<a href={quoteattr(p.href)}><g data-fact-id={quoteattr(p.fact_id)}>'
            f"<title>{escape(p.label)}: {escape(p.value)} — Tier {p.tier}</title>"
            f'<circle class="dot" cx="{cx:.1f}" cy="{cy:.1f}" r="4.5" fill="{stroke}"/>'
            + (
                f'<text class="vlab" x="{cx:.1f}" y="{cy - 9:.1f}">{_fmt(p.quantity)}</text>'
                if show_label
                else ""
            )
            + f'<text class="tlet" x="{cx:.1f}" y="{height - 12}" '
            f'fill="{tier_color}">{p.tier}</text></g></a>'
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
            f'<a href={quoteattr(s.href)}><g data-fact-id={quoteattr(s.fact_id)}>'
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


def hours_meter(bars: tuple[MeterBar, ...], unit: str, width: int = 880) -> str:
    """The labour-hours meter — horizontal bars drawn to the data's shape.

    Falling metric → copper. A decade whose fact carries no single honest
    quantity (the 1990s/2010s Ramey gap, the 2020s concept splice) renders a
    dashed empty track with the words, at full row height.
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
        if b.quantity is None:
            out.append(
                f'<a href={quoteattr(b.href)}><g data-fact-id={quoteattr(b.fact_id)}>'
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
                f'<a href={quoteattr(b.href)}><g data-fact-id={quoteattr(b.fact_id)}>'
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
STAGE_POS: dict[str, tuple[int, int]] = {
    "tenure": (400, 142),
    "rooms": (500, 252),
    "electricity": (250, 220),
    "radio": (214, 286),
    "television": (322, 286),
    "telephone": (366, 244),
    "refrigerator": (214, 378),
    "food": (304, 402),
    "plumbing": (458, 378),
    "heating": (556, 398),
    "air-conditioning": (612, 244),
    "cable": (322, 330),
    "computer": (556, 252),
    "internet": (612, 296),
    "automobile": (712, 404),
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


def stage_svg(stage: Stage) -> str:
    """The dark-gallery house cutaway with era-graded light.

    The spotlight tint per decade is the mood channel (design-spec); glyph
    opacity is the diffusion datum; a fact with no quantity keeps the dashed
    gap ring. Every glyph links to its placard.
    """
    glow = tokens.ERA_GLOW.get(stage.decade, tokens.ERA_GLOW_DEFAULT)
    rx, ry = tokens.ERA_POOL.get(stage.decade, tokens.ERA_POOL_DEFAULT)
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
        '<polygon points="120,182 400,90 680,182"/>'
        '<rect x="150" y="182" width="500" height="248"/>'
        '<line x1="400" y1="182" x2="400" y2="430"/>'
        '<line x1="150" y1="306" x2="650" y2="306"/>'
        '<rect x="452" y="122" width="34" height="60"/>'
        "</g>"
        '<line class="groundline" x1="80" y1="430" x2="720" y2="430"/>'
        '<text class="zlabel" x="172" y="202">parlor</text>'
        '<text class="zlabel" x="470" y="202">rooms</text>'
        '<text class="zlabel" x="172" y="326">kitchen</text>'
        '<text class="zlabel" x="470" y="326">bath &amp; heat</text>'
    ]
    for note in stage.zone_notes:
        anchor = ' style="text-anchor:end"' if note.x > 620 else ""
        out.append(
            f'<a href={quoteattr(note.href)}>'
            f'<text class="znote" x="{note.x}" y="{note.y}"{anchor} '
            f"data-fact-id={quoteattr(note.fact_id)}>{escape(note.text)}</text></a>"
        )
    for a in stage.artifacts:
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
        out.append(
            f"<a href={quoteattr(a.href)}>"
            f'<g class="hs" transform="translate({a.x},{a.y})" '
            f"data-fact-id={quoteattr(a.fact_id)}>"
            f"<title>{escape(a.label)}: {escape(a.value)}</title>"
            f"{ring}"
            f'<g class="glyphwrap" style="opacity:{opacity:.2f}">{a.glyph_svg}</g>'
            f'<g transform="translate(0,30)">{pct}</g>'
            "</g></a>"
        )
    out.append("</svg>")
    return "".join(out)
