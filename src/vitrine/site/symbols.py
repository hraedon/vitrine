"""The artifact symbol library — era-keyed stage glyphs (Plan 007 WI-4).

Symbols are decoration (non-truth-path) but their appearance is gated: the
renderer draws a symbol only for artifacts whose registry fact exists in the
room, and a test enforces it. Drawn in the demo's stroke language: thin brass
line work, round caps and joins, sparing fills, 2–6 primitives, recognizable
at 48px without a label.

Each fragment is inline SVG in a local ±14 coordinate box, centered at the
origin; strokes carry ``class="glyph"`` (fills ``class="glyph fill"``) so the
stage stylesheet colors them. Era keying picks the latest variant whose
``from_year`` is at or before the room's decade — icebox before the round-top
refrigerator before the two-door, candlestick before rotary before handset.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Symbol:
    """One era-resolved artifact glyph."""

    artifact: str
    variant: str
    svg: str  # inline fragment, local ±14 box, class="glyph" strokes


def _year(decade: str) -> int:
    return int(decade[:4])


# ── the library: artifact → ((from_year, variant, svg), …) ascending ─────────

_VARIANTS: dict[str, tuple[tuple[int, str, str], ...]] = {
    "tenure": (
        (
            0,
            "deed",
            '<rect class="glyph" x="-10" y="-9" width="20" height="16" rx="1"/>'
            '<line class="glyph" x1="-6" y1="-4" x2="6" y2="-4"/>'
            '<line class="glyph" x1="-6" y1="0" x2="6" y2="0"/>'
            '<line class="glyph" x1="-6" y1="4" x2="2" y2="4"/>',
        ),
    ),
    "rooms": (
        (
            0,
            "floor-plan",
            '<rect class="glyph" x="-11" y="-9" width="22" height="18"/>'
            '<line class="glyph" x1="0" y1="-9" x2="0" y2="9"/>'
            '<line class="glyph" x1="-11" y1="1" x2="0" y2="1"/>',
        ),
    ),
    "electricity": (
        (
            0,
            "drop-cord-bulb",
            '<line class="glyph" x1="0" y1="-14" x2="0" y2="-6"/>'
            '<path class="glyph" d="M-5 -1 a5 6 0 1 1 10 0 q0 4 -2 6 h-6 q-2 -2 -2 -6z"/>'
            '<line class="glyph" x1="-3" y1="8" x2="3" y2="8"/>',
        ),
        (
            1940,
            "bulb",
            '<circle class="glyph" cx="0" cy="-3" r="8"/>'
            '<line class="glyph" x1="-4" y1="7" x2="4" y2="7"/>'
            '<line class="glyph" x1="-3" y1="10" x2="3" y2="10"/>',
        ),
    ),
    "radio": (
        (
            0,
            "cathedral-console",
            '<path class="glyph" d="M-9 10 v-12 a9 9 0 0 1 18 0 v12 z"/>'
            '<circle class="glyph" cx="0" cy="-3" r="3"/>'
            '<line class="glyph" x1="-5" y1="5" x2="5" y2="5"/>',
        ),
        (
            1940,
            "tabletop-set",
            '<rect class="glyph" x="-12" y="-8" width="24" height="16" rx="2"/>'
            '<circle class="glyph" cx="5" cy="0" r="3.4"/>'
            '<line class="glyph" x1="-8" y1="-3" x2="-2" y2="-3"/>'
            '<line class="glyph" x1="-8" y1="2" x2="-2" y2="2"/>',
        ),
    ),
    "television": (
        (
            0,
            "rabbit-ear-set",
            '<rect class="glyph" x="-11" y="-6" width="22" height="15" rx="2"/>'
            '<line class="glyph" x1="-3" y1="-6" x2="-7" y2="-13"/>'
            '<line class="glyph" x1="3" y1="-6" x2="7" y2="-13"/>',
        ),
        (
            1990,
            "crt-color",
            '<rect class="glyph" x="-12" y="-9" width="24" height="18" rx="1"/>'
            '<rect class="glyph" x="-10" y="-7" width="16" height="14" rx="2"/>'
            '<line class="glyph" x1="8" y1="-7" x2="8" y2="7"/>'
            '<circle class="glyph fill" cx="10" cy="-4" r="0.8"/>'
            '<circle class="glyph fill" cx="10" cy="-1" r="0.8"/>'
            '<circle class="glyph fill" cx="10" cy="2" r="0.8"/>',
        ),
        (
            2000,
            "flat-panel",
            '<rect class="glyph" x="-13" y="-9" width="26" height="15" rx="1"/>'
            '<line class="glyph" x1="0" y1="6" x2="0" y2="10"/>'
            '<line class="glyph" x1="-6" y1="10" x2="6" y2="10"/>',
        ),
    ),
    "telephone": (
        (
            0,
            "candlestick",
            '<line class="glyph" x1="0" y1="-11" x2="0" y2="7"/>'
            '<ellipse class="glyph" cx="0" cy="9" rx="6" ry="2.2"/>'
            '<circle class="glyph fill" cx="0" cy="-12" r="2.6"/>',
        ),
        (
            1940,
            "rotary-desk",
            '<path class="glyph" d="M-10 8 h20 l-3 -9 h-14 z"/>'
            '<path class="glyph" d="M-9 -4 a9 5 0 0 1 18 0"/>'
            '<circle class="glyph" cx="0" cy="3" r="3.2"/>',
        ),
        (
            1970,
            "push-button",
            '<path class="glyph" d="M-9 7 h18 l-2 -8 h-14 z"/>'
            '<path class="glyph" d="M-11 -5 h22 v3 M-11 -4 v-2 h2 M9 -6 h2 v2"/>'
            '<rect class="glyph" x="-3.5" y="-2" width="7" height="6" rx="0.5"/>'
            '<line class="glyph" x1="-1.2" y1="-2" x2="-1.2" y2="4"/>'
            '<line class="glyph" x1="1.2" y1="-2" x2="1.2" y2="4"/>'
            '<line class="glyph" x1="-3.5" y1="0" x2="3.5" y2="0"/>'
            '<line class="glyph" x1="-3.5" y1="2" x2="3.5" y2="2"/>',
        ),
        (
            1980,
            "handset",
            '<rect class="glyph" x="-4" y="-12" width="8" height="24" rx="3"/>'
            '<line class="glyph" x1="-2" y1="-7" x2="2" y2="-7"/>'
            '<line class="glyph" x1="-2" y1="7" x2="2" y2="7"/>',
        ),
        (
            2010,
            "smartphone",
            '<rect class="glyph" x="-6" y="-11" width="12" height="22" rx="2"/>'
            '<line class="glyph" x1="-2" y1="8" x2="2" y2="8"/>',
        ),
    ),
    "refrigerator": (
        (
            0,
            "icebox",
            '<rect class="glyph" x="-9" y="-13" width="18" height="26" rx="1"/>'
            '<line class="glyph" x1="-9" y1="-4" x2="9" y2="-4"/>'
            '<line class="glyph" x1="5" y1="-10" x2="5" y2="-7"/>'
            '<line class="glyph" x1="5" y1="0" x2="5" y2="3"/>'
            '<line class="glyph" x1="-5" y1="9" x2="5" y2="9"/>',
        ),
        (
            1940,
            "round-top",
            '<path class="glyph" d="M-8 13 v-19 a8 7 0 0 1 16 0 v19 z"/>'
            '<line class="glyph" x1="4" y1="-4" x2="4" y2="2"/>',
        ),
        (
            1970,
            "two-door",
            '<rect class="glyph" x="-8" y="-13" width="16" height="26" rx="2"/>'
            '<line class="glyph" x1="-8" y1="-1" x2="8" y2="-1"/>'
            '<line class="glyph" x1="4" y1="-9" x2="4" y2="-5"/>'
            '<line class="glyph" x1="4" y1="3" x2="4" y2="8"/>',
        ),
    ),
    "food": (
        (
            0,
            "bowl",
            '<ellipse class="glyph" cx="0" cy="5" rx="11" ry="3.4"/>'
            '<path class="glyph" d="M-9 5 a9 6 0 0 1 18 0"/>',
        ),
    ),
    "plumbing": (
        (
            0,
            "hand-pump",
            '<line class="glyph" x1="-3" y1="12" x2="-3" y2="-6"/>'
            '<path class="glyph" d="M-3 -6 h8 v5"/>'
            '<line class="glyph" x1="-10" y1="-9" x2="1" y2="-4"/>'
            '<path class="glyph fill" d="M5 3 q3.5 5 0 8 q-3.5 -3 0 -8z"/>',
        ),
        (
            1940,
            "tap",
            '<path class="glyph" d="M-9 -7 v5 h9 a4 4 0 0 1 4 4 v2"/>'
            '<path class="glyph fill" d="M4 8 q3.5 5 0 8 q-3.5 -3 0 -8z"/>',
        ),
    ),
    "heating": (
        (
            0,
            "potbelly-stove",
            '<circle class="glyph" cx="0" cy="2" r="8"/>'
            '<line class="glyph" x1="0" y1="-6" x2="0" y2="-13"/>'
            '<line class="glyph" x1="-5" y1="12" x2="-5" y2="10"/>'
            '<line class="glyph" x1="5" y1="12" x2="5" y2="10"/>'
            '<line class="glyph" x1="-3" y1="2" x2="3" y2="2"/>',
        ),
        (
            1940,
            "radiator",
            '<rect class="glyph" x="-11" y="-8" width="22" height="16" rx="1"/>'
            '<line class="glyph" x1="-6" y1="-8" x2="-6" y2="8"/>'
            '<line class="glyph" x1="0" y1="-8" x2="0" y2="8"/>'
            '<line class="glyph" x1="6" y1="-8" x2="6" y2="8"/>',
        ),
    ),
    "automobile": (
        (
            0,
            "horseless-carriage",
            '<line class="glyph" x1="-10" y1="0" x2="10" y2="0"/>'
            '<path class="glyph" d="M-6 0 v-7 h7 v7"/>'
            '<circle class="glyph" cx="-8" cy="5" r="4"/>'
            '<circle class="glyph" cx="8" cy="5" r="4"/>',
        ),
        (
            1920,
            "sedan",
            '<path class="glyph" d="M-14 5 h28 v-4 l-5 -7 h-13 l-5 7 z"/>'
            '<circle class="glyph" cx="-7" cy="7" r="3"/>'
            '<circle class="glyph" cx="7" cy="7" r="3"/>',
        ),
        (
            2000,
            "modern-car",
            '<path class="glyph" d="M-13 5 h26 v-3 a4 4 0 0 0 -4 -4 l-4 -4 h-9 l-5 6 a5 5 0 0 0 -4 5z"/>'
            '<circle class="glyph" cx="-7" cy="7" r="3"/>'
            '<circle class="glyph" cx="7" cy="7" r="3"/>',
        ),
    ),
    "air-conditioning": (
        (
            0,
            "window-unit",
            '<rect class="glyph" x="-11" y="-7" width="22" height="14" rx="1"/>'
            '<line class="glyph" x1="-8" y1="-2" x2="4" y2="-2"/>'
            '<line class="glyph" x1="-8" y1="2" x2="4" y2="2"/>'
            '<circle class="glyph" cx="7.5" cy="0" r="2.4"/>',
        ),
        (
            2000,
            "split-unit",
            '<rect class="glyph" x="-12" y="-6" width="24" height="10" rx="3"/>'
            '<line class="glyph" x1="-8" y1="1" x2="8" y2="1"/>'
            '<path class="glyph" d="M-5 8 q1 2 0 4 M0 8 q1 2 0 4 M5 8 q1 2 0 4"/>',
        ),
    ),
    "cable": (
        (
            0,
            "coax-screen",
            '<rect class="glyph" x="-11" y="-8" width="22" height="14" rx="2"/>'
            '<path class="glyph" d="M-11 6 q-3 4 1 6 h6"/>'
            '<circle class="glyph fill" cx="-3" cy="12" r="1.6"/>',
        ),
    ),
    "computer": (
        (
            0,
            "desktop-crt",
            '<rect class="glyph" x="-9" y="-11" width="18" height="13" rx="1"/>'
            '<line class="glyph" x1="0" y1="2" x2="0" y2="5"/>'
            '<rect class="glyph" x="-11" y="5" width="22" height="4" rx="1"/>',
        ),
        (
            2000,
            "laptop",
            '<path class="glyph" d="M-9 -9 h18 v11 h-18 z"/>'
            '<path class="glyph" d="M-12 6 h24 l-2 3 h-20 z"/>',
        ),
    ),
    "internet": (
        (
            0,
            "router",
            '<rect class="glyph" x="-11" y="3" width="22" height="7" rx="2"/>'
            '<line class="glyph" x1="7" y1="3" x2="7" y2="-4"/>'
            '<path class="glyph" d="M-6 -2 a7 7 0 0 1 8 0 M-8.5 -6 a11 11 0 0 1 13 0"/>',
        ),
    ),
    "washing-machine": (
        (
            0,
            "wringer",
            '<ellipse class="glyph" cx="0" cy="2" rx="7" ry="2"/>'
            '<path class="glyph" d="M-7 2 v7 c0 2 14 2 14 0 v-7"/>'
            '<line class="glyph" x1="-5" y1="9" x2="-7" y2="13"/>'
            '<line class="glyph" x1="5" y1="9" x2="7" y2="13"/>'
            '<path class="glyph" d="M-5 2 v-7 h10 v7"/>'
            '<rect class="glyph" x="-4.5" y="-4" width="9" height="3" rx="0.5"/>'
            '<path class="glyph" d="M5 -2.5 h3 v3"/>',
        ),
        (
            1950,
            "top-loader",
            '<rect class="glyph" x="-8" y="-6" width="16" height="18" rx="1"/>'
            '<rect class="glyph" x="-8" y="-11" width="16" height="5"/>'
            '<ellipse class="glyph" cx="0" cy="-6" rx="5" ry="1.2"/>'
            '<circle class="glyph fill" cx="-4" cy="-8.5" r="0.8"/>'
            '<circle class="glyph fill" cx="4" cy="-8.5" r="0.8"/>',
        ),
        (
            2000,
            "front-loader",
            '<rect class="glyph" x="-8" y="-11" width="16" height="23" rx="1.5"/>'
            '<line class="glyph" x1="-8" y1="-6" x2="8" y2="-6"/>'
            '<circle class="glyph fill" cx="-4" cy="-8.5" r="1"/>'
            '<rect class="glyph" x="2.5" y="-9.5" width="3" height="2"/>'
            '<circle class="glyph" cx="0" cy="3" r="5.5"/>'
            '<circle class="glyph" cx="0" cy="3" r="3.5"/>',
        ),
    ),
    "stove": (
        (
            0,
            "wood-coal",
            '<rect class="glyph" x="-8" y="-4" width="16" height="12"/>'
            '<line class="glyph" x1="-8" y1="2" x2="8" y2="2"/>'
            '<line class="glyph" x1="0" y1="-4" x2="0" y2="8"/>'
            '<path class="glyph" d="M4 -4 v-9 h2 v9"/>'
            '<path class="glyph" d="M-6 8 Q-8 11 -7 13 M6 8 Q8 11 7 13"/>'
            '<ellipse class="glyph" cx="-4" cy="-4" rx="2.5" ry="0.8"/>'
            '<ellipse class="glyph" cx="1" cy="-4" rx="2.5" ry="0.8"/>',
        ),
        (
            1950,
            "cabinet-range",
            '<rect class="glyph" x="-8" y="-5" width="16" height="17" rx="1"/>'
            '<rect class="glyph" x="-8" y="-11" width="16" height="6"/>'
            '<line class="glyph" x1="-8" y1="-5" x2="8" y2="-5"/>'
            '<circle class="glyph fill" cx="-4" cy="-8" r="0.8"/>'
            '<circle class="glyph fill" cx="0" cy="-8" r="0.8"/>'
            '<circle class="glyph fill" cx="4" cy="-8" r="0.8"/>'
            '<ellipse class="glyph" cx="-4" cy="-5" rx="2.2" ry="0.6"/>'
            '<ellipse class="glyph" cx="4" cy="-5" rx="2.2" ry="0.6"/>'
            '<rect class="glyph" x="-5" y="4" width="10" height="5" rx="0.5"/>'
            '<line class="glyph" x1="-4" y1="1" x2="4" y2="1"/>',
        ),
        (
            2000,
            "smooth-top",
            '<rect class="glyph" x="-8" y="-11" width="16" height="23" rx="1"/>'
            '<line class="glyph" x1="-8" y1="-8" x2="8" y2="-8"/>'
            '<ellipse class="glyph" cx="-3.5" cy="-11" rx="2.2" ry="0.5"/>'
            '<ellipse class="glyph" cx="3.5" cy="-11" rx="2.2" ry="0.5"/>'
            '<line class="glyph" x1="-8" y1="-10" x2="8" y2="-10"/>'
            '<rect class="glyph" x="-6.5" y="-3" width="13" height="9" rx="0.5"/>'
            '<line class="glyph" x1="-5" y1="-6" x2="5" y2="-6"/>',
        ),
    ),
    "bread": (
        (
            0,
            "loaf",
            '<path class="glyph" d="M-12 -2 C-12 -8, -2 -8, -2 -2 Z"/>'
            '<line class="glyph" x1="-12" y1="-2" x2="-2" y2="-2"/>'
            '<line class="glyph" x1="-9" y1="-7" x2="-7" y2="-3"/>'
            '<line class="glyph" x1="-6" y1="-7" x2="-4" y2="-3"/>',
        ),
    ),
    "milk": (
        (
            0,
            "bottle",
            '<path class="glyph" d="M5.5 -4 L5.5 7 A1.5 1.5 0 0 0 7 8.5 H8 A1.5 1.5 0 0 0 9.5 7 L9.5 -4 L8.3 -7 V-9 H6.7 V-7 Z"/>'
            '<line class="glyph" x1="5.5" y1="1" x2="9.5" y2="1"/>',
        ),
    ),
    "meat": (
        (
            0,
            "steak",
            '<path class="glyph" d="M-3 -3 C-7 -3, -8 1, -6 3 C-4 5, 1 5, 2 3 C3 1, 1 -3, -3 -3 Z"/>'
            '<line class="glyph" x1="-2" y1="-3" x2="-2" y2="1"/>'
            '<path class="glyph" d="M-2 0 C0 1, 1 1, 2 1"/>',
        ),
    ),
    "eggs": (
        (
            0,
            "eggs",
            '<ellipse class="glyph" cx="1" cy="6" rx="2.5" ry="3.5" transform="rotate(45 1 6)"/>'
            '<ellipse class="glyph" cx="-3" cy="7" rx="2.5" ry="3.5" transform="rotate(-30 -3 7)"/>',
        ),
    ),
    "potatoes": (
        (
            0,
            "tubers",
            '<path class="glyph" d="M-9 5 C-11 5, -11 9, -8 9 C-6 9, -7 5, -9 5 Z"/>'
            '<path class="glyph" d="M-5 6 C-7 6, -6 10, -4 10 C-2 10, -3 6, -5 6 Z"/>',
        ),
    ),
}

ARTIFACTS = frozenset(_VARIANTS)


def _food_still_life(value: str | None) -> str:
    if not value:
        return (
            '<ellipse class="glyph" cx="0" cy="5" rx="11" ry="3.4"/>'
            '<path class="glyph" d="M-9 5 a9 6 0 0 1 18 0"/>'
        )
    val_lower = value.lower()
    has_bread = "bread" in val_lower or "bakery" in val_lower or "flour" in val_lower or "cereals" in val_lower
    has_milk = "milk" in val_lower or "dairy" in val_lower or "butter" in val_lower
    has_eggs = "eggs" in val_lower
    has_potatoes = "potatoes" in val_lower or "vegetables" in val_lower
    has_meat = any(w in val_lower for w in ["meat", "beef", "hog", "pork", "steak", "roast", "chops", "bacon", "poultry", "fish", "chicken"])
    
    parts = []
    if has_bread:
        parts.append(_VARIANTS["bread"][0][2])
    if has_milk:
        parts.append(_VARIANTS["milk"][0][2])
    if has_meat:
        parts.append(_VARIANTS["meat"][0][2])
    if has_eggs:
        parts.append(_VARIANTS["eggs"][0][2])
    if has_potatoes:
        parts.append(_VARIANTS["potatoes"][0][2])
        
    if not parts:
        return (
            '<ellipse class="glyph" cx="0" cy="5" rx="11" ry="3.4"/>'
            '<path class="glyph" d="M-9 5 a9 6 0 0 1 18 0"/>'
        )
    return "".join(parts)


def symbol(artifact: str, decade: str, value: str | None = None) -> Symbol | None:
    """The era-resolved glyph for *artifact* in *decade*; None if unknown."""
    if artifact == "food":
        svg_content = _food_still_life(value)
        if value:
            val_lower = value.lower()
            has_any = (
                "bread" in val_lower or "bakery" in val_lower or "flour" in val_lower or "cereals" in val_lower or
                "milk" in val_lower or "dairy" in val_lower or "butter" in val_lower or
                "eggs" in val_lower or
                "potatoes" in val_lower or "vegetables" in val_lower or
                any(w in val_lower for w in ["meat", "beef", "hog", "pork", "steak", "roast", "chops", "bacon", "poultry", "fish", "chicken"])
            )
            if has_any:
                return Symbol(artifact="food", variant="still-life", svg=svg_content)
        return Symbol(artifact="food", variant="bowl", svg=svg_content)

    variants = _VARIANTS.get(artifact)
    if variants is None:
        return None
    year = _year(decade)
    chosen = None
    for from_year, variant, svg in variants:
        if from_year <= year:
            chosen = (variant, svg)
    if chosen is None:
        return None
    return Symbol(artifact=artifact, variant=chosen[0], svg=chosen[1])
