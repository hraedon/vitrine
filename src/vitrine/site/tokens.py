"""Design tokens — the executable half of docs/design-spec.md.

The "statistical atlas" palette (Plan 020): light paper surfaces, ink text,
hairline rules, and color reserved for epistemology (tiers, gap, provisional)
and editorial voice (the petrol accent for rising series, ember copper for
falling ones). Tokens live here; the spec records the decisions and the
validation results. tests/test_design.py asserts the two never drift and
computes every contrast constraint (spec: "checked, not assumed").
"""

from __future__ import annotations

# ── core surfaces & voice ────────────────────────────────────────────────────

GROUND = "#f2ecdd"  # paper — the page background
CASE = "#fbf7ec"  # sheet — panels, cards, chart windows
CASE_2 = "#f5efe0"  # inset — recessed areas, summary rows
EDGE = "#d5c9ab"  # hairline rules
IVORY = "#fffdf7"  # raised card — the overlay placard (brightest object)
IVORY_2 = "#f8f2e2"  # card gradient partner
INK = "#29241b"  # body text
INK_SOFT = "#6e6450"  # secondary text (4.5:1 minimum on paper/sheets)
BRASS = "#175d75"  # atlas accent ink — editorial voice, rising series
BRASS_DIM = "#61798a"  # quiet accent — structure strokes, idle rings
BRASS_DEEP = "#0f4253"  # accent on hover/pressed
BRASS_LIT = "#1e7a9c"  # accent bright — focus rings, current marker
COPPER = "#b34a13"  # ember — falling series, caution borders
COPPER_DEEP = "#933d0e"  # ember for small text (4.5:1 minimum)

SERIF = '"Iowan Old Style","Palatino Linotype",Palatino,"Book Antiqua",Georgia,serif'
SANS = 'ui-sans-serif,system-ui,"Segoe UI",Helvetica,Arial,sans-serif'
MONO = 'ui-monospace,"SFMono-Regular",Menlo,Consolas,monospace'

# ── the honesty vocabulary ───────────────────────────────────────────────────

TIER_COLORS = {
    "A": "#2f7a55",
    "B": "#8f6512",
    "C": "#7d4a63",
    "D": "#6e6a5e",
}
PROVISIONAL = "#a45a2b"
GAP = "#6e6a5e"  # dashed hairline / gap chip — shares Tier D's neutral

# Semantic colors that render on the tinted stage and sheets; every one must
# hold >= 3:1 against every era wash and every sheet surface
# (design-spec: "Era-graded stage wash — Constraint").
SEMANTIC_ON_STAGE = {
    "tier-A": TIER_COLORS["A"],
    "tier-B": TIER_COLORS["B"],
    "tier-C": TIER_COLORS["C"],
    "tier-D": TIER_COLORS["D"],
    "provisional": PROVISIONAL,
    "brass": BRASS,
    "copper": COPPER,
}

# Chip letters (and only those) may be white; each chip color must hold
# >= 4.5:1 against white text. The gap ring color is held to the chip rule
# too, since it labels small italic gap text on sheets.
CHIP_COLORS = SEMANTIC_ON_STAGE | {"copper-deep": COPPER_DEEP}

# Caption text on untinted paper surfaces only — never placed on the stage
# wash (the renderer keeps it to paper/sheets; the test holds 4.5:1 there).
CAPTION_ON_SHEET = {"ink-soft": INK_SOFT}

# ── era-graded stage wash (inner glaze stop of the stage gradient) ───────────
# Editorial rendering of the sourced lighting-fuel / electrification family:
# deep amber pools for the kerosene decades, clearing toward LED's neutral
# sheet.

ERA_GLOW = {
    "1890s": "#e8d9b8",
    "1900s": "#e8d9b8",
    "1910s": "#e8d9b8",
    "1920s": "#ece0c4",
    "1930s": "#ece0c4",
    "1940s": "#ece0c4",
    "1950s": "#efe7d2",
    "1960s": "#efe7d2",
    "1970s": "#efe7d2",
    "1980s": "#f0ead8",
    "1990s": "#f0ead8",
    "2000s": "#f2edde",
    "2010s": "#f2edde",
    "2020s": "#f4f0e4",
}
ERA_GLOW_DEFAULT = "#efe7d2"  # a decade outside the table gets the mid stop

# Pool geometry: (radius-x %, radius-y %) of the wash — dim/narrow for
# kerosene, wide/clear for LED. Mood only; carries no data.
ERA_POOL = {
    "1890s": (95, 74),
    "1900s": (95, 74),
    "1910s": (95, 74),
    "1920s": (105, 82),
    "1930s": (105, 82),
    "1940s": (105, 82),
    "1950s": (120, 92),
    "1960s": (120, 92),
    "1970s": (120, 92),
    "1980s": (125, 96),
    "1990s": (125, 96),
    "2000s": (130, 100),
    "2010s": (130, 100),
    "2020s": (140, 106),
}
ERA_POOL_DEFAULT = (120, 92)

# ── budget-composition categorical palette (design-spec, validated) ──────────
# Fixed assignment, never cycled. Composition bars sit on sheets; every slot
# holds >= 4.5:1 against its mandatory white direct label and >= 3:1 against
# the sheet itself.

COMPOSITION_ORDER = ("housing", "apparel", "food", "health", "transport", "other")

COMPOSITION_SHEET = {
    "housing": "#38618f",
    "apparel": "#8f3f7d",
    "food": "#4f6b20",
    "health": "#11706a",
    "transport": "#a84c38",
    "other": "#6e6a5e",
}

# CEX category labels → palette slot. Anything unlisted folds into "other".
CATEGORY_SLOT = {
    "housing": "housing",
    "rent": "housing",
    "apparel": "apparel",
    "clothing": "apparel",
    "food": "food",
    "healthcare": "health",
    "health": "health",
    "transportation": "transport",
    "transport": "transport",
}


def glyph_opacity(pct: float | None) -> float:
    """Diffusion percentage → glyph opacity, carried from the demo unchanged."""
    if pct is None:
        return 0.55
    return max(0.12, min(1.0, 0.16 + 0.84 * (pct / 100.0)))


# ── WCAG contrast (used by the viewer-facing constraint tests and nowhere
# else at render time — the shipped colors are static) ────────────────────────


def _channel(v: int) -> float:
    c = v / 255.0
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def relative_luminance(hex_color: str) -> float:
    h = hex_color.lstrip("#")
    r, g, b = (int(h[i : i + 2], 16) for i in (0, 2, 4))
    return 0.2126 * _channel(r) + 0.7152 * _channel(g) + 0.0722 * _channel(b)


def contrast_ratio(fg: str, bg: str) -> float:
    lighter, darker = sorted((relative_luminance(fg), relative_luminance(bg)), reverse=True)
    return (lighter + 0.05) / (darker + 0.05)
