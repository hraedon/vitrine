"""Design tokens — the executable half of docs/design-spec.md.

Tokens live here; the spec records the decisions and validation results.
tests/test_design.py asserts the two never drift and computes the era-tint
contrast constraint (spec: "checked, not assumed").
"""

from __future__ import annotations

# ── core surfaces & voice ────────────────────────────────────────────────────

GROUND = "#1b1815"
CASE = "#242019"
CASE_2 = "#2c261e"
EDGE = "#413728"
IVORY = "#ece2cf"
IVORY_2 = "#e3d7bf"
INK = "#2a2317"
INK_SOFT = "#7c6f57"
BRASS = "#cf9f4c"
BRASS_DIM = "#7d663a"
BRASS_DEEP = "#a97f34"
BRASS_LIT = "#f0c778"
COPPER = "#c98a6a"  # falling-metric bars

SERIF = '"Iowan Old Style","Palatino Linotype",Palatino,"Book Antiqua",Georgia,serif'
SANS = 'ui-sans-serif,system-ui,"Segoe UI",Helvetica,Arial,sans-serif'
MONO = 'ui-monospace,"SFMono-Regular",Menlo,Consolas,monospace'

# ── the honesty vocabulary ───────────────────────────────────────────────────

TIER_COLORS = {
    "A": "#7aa38c",
    "B": "#c79a44",
    "C": "#c5763e",
    "D": "#948a78",
}
PROVISIONAL = "#b07a52"
GAP = "#948a78"  # dashed ring / gap chip — shares Tier D's neutral

# Semantic colors that render on the tinted stage and must hold >= 3:1 on
# every era glow (design-spec: "Era-graded stage light — Constraint").
SEMANTIC_ON_STAGE = {
    "tier-A": TIER_COLORS["A"],
    "tier-B": TIER_COLORS["B"],
    "tier-C": TIER_COLORS["C"],
    "tier-D": TIER_COLORS["D"],
    "provisional": PROVISIONAL,
    "brass": BRASS,
    "copper": COPPER,
}

# Caption text on untinted dark surfaces only — never placed on the stage
# (the renderer keeps it to case/ground; the test holds it to 3:1 there).
CAPTION_ON_DARK = {"ink-soft": INK_SOFT}

# ── era-graded stage light (inner glow stop of the stage gradient) ───────────
# Editorial rendering of the sourced lighting-fuel / electrification family.

ERA_GLOW = {
    "1890s": "#3a2c17",
    "1900s": "#3a2c17",
    "1910s": "#3a2c17",
    "1920s": "#392e1c",
    "1930s": "#392e1c",
    "1940s": "#392e1c",
    "1950s": "#322a20",
    "1960s": "#322a20",
    "1970s": "#322a20",
    "1980s": "#2f2b22",
    "1990s": "#2f2b22",
    "2000s": "#2c2b24",
    "2010s": "#2c2b24",
    "2020s": "#2d2e29",
}
ERA_GLOW_DEFAULT = "#322a20"  # a decade outside the table gets the demo stop

# Pool geometry: (radius-x %, radius-y %) of the spotlight — dim/narrow for
# kerosene, wide/bright for LED. Mood only; carries no data.
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
# Fixed assignment, never cycled. "other" is neutral, outside validated slots.

COMPOSITION_ORDER = ("housing", "apparel", "food", "health", "transport", "other")

COMPOSITION_DARK = {
    "housing": "#5b8fd6",
    "apparel": "#c06fae",
    "food": "#8d983a",
    "health": "#1ca69e",
    "transport": "#d16a55",
    "other": "#9a938a",
}
COMPOSITION_IVORY = {
    "housing": "#4d7fc4",
    "apparel": "#b05f9e",
    "food": "#7f8a2f",
    "health": "#0f948c",
    "transport": "#c05a46",
    "other": "#8a8378",
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


# ── WCAG contrast (used by the era-tint constraint test and nowhere else
# at render time — the shipped colors are static) ────────────────────────────


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
