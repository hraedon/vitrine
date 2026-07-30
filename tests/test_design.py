"""Design-token invariants for the statistical-atlas palette (Plan 020).

The spec says every contrast constraint is *checked, not assumed*, and that
the palette recorded in docs/design-spec.md matches the shipped hexes. Both
live here. Three color disciplines are computed:

1. every semantic color that renders on stage washes or sheets holds 3:1
   against every one of those surfaces;
2. white chip letters hold 4.5:1 against every chip color;
3. composition segments hold 3:1 against the sheet and 4.5:1 against their
   mandatory white direct labels.
"""

import re
from pathlib import Path

from vitrine.site import tokens

SPEC = Path(__file__).parent.parent / "docs" / "design-spec.md"

WHITE = "#ffffff"


def _every_surface() -> dict[str, str]:
    surfaces = {"ground": tokens.GROUND, "case": tokens.CASE, "case-2": tokens.CASE_2}
    surfaces |= {f"wash-{d}": g for d, g in tokens.ERA_GLOW.items()}
    surfaces["wash-default"] = tokens.ERA_GLOW_DEFAULT
    return surfaces


def test_semantic_colors_hold_contrast_on_every_stage_surface() -> None:
    """Every stage-semantic color >= 3:1 against every wash and every sheet."""
    failures = [
        f"{name} on {sname} ({surface}): {tokens.contrast_ratio(color, surface):.2f}"
        for name, color in tokens.SEMANTIC_ON_STAGE.items()
        for sname, surface in _every_surface().items()
        if tokens.contrast_ratio(color, surface) < 3.0
    ]
    assert not failures, "semantic colors below 3:1 on a surface:\n" + "\n".join(failures)


def test_chip_letters_are_legible_on_every_chip() -> None:
    """White chip letters >= 4.5:1 against every chip color (small bold text)."""
    failures = [
        f"white on {name} ({color}): {tokens.contrast_ratio(WHITE, color):.2f}"
        for name, color in tokens.CHIP_COLORS.items()
        if tokens.contrast_ratio(WHITE, color) < 4.5
    ]
    assert not failures, "chip colors too light for white letters:\n" + "\n".join(failures)


def test_caption_text_holds_contrast_on_untinted_surfaces() -> None:
    """Small secondary text must hold WCAG AA's 4.5:1 on paper surfaces."""
    for name, color in tokens.CAPTION_ON_SHEET.items():
        for surface in (tokens.GROUND, tokens.CASE, tokens.CASE_2):
            assert tokens.contrast_ratio(color, surface) >= 4.5, f"{name} on {surface}"


def test_body_ink_holds_contrast_on_every_surface() -> None:
    """Body ink is long-form text: hold 7:1 on every wash and sheet."""
    failures = [
        f"ink on {sname} ({surface}): {tokens.contrast_ratio(tokens.INK, surface):.2f}"
        for sname, surface in _every_surface().items()
        if tokens.contrast_ratio(tokens.INK, surface) < 7.0
    ]
    assert not failures, "ink below 7:1 on a surface:\n" + "\n".join(failures)


def test_every_decade_has_a_wash_and_pool() -> None:
    assert set(tokens.ERA_GLOW) == set(tokens.ERA_POOL)
    for decade in tokens.ERA_GLOW:
        assert re.fullmatch(r"1[89]\d0s|20\d0s", decade)


def test_composition_palette_matches_recorded_validation() -> None:
    """The sheet palette's recorded validation matches the shipped hexes."""
    spec_text = SPEC.read_text()
    for slot in tokens.COMPOSITION_ORDER:
        color = tokens.COMPOSITION_SHEET[slot]
        assert color in spec_text, f"{slot} ({color}) not in spec"
        assert tokens.contrast_ratio(WHITE, color) >= 4.5, (
            f"{slot} segment can't carry its mandatory white label: "
            f"{tokens.contrast_ratio(WHITE, color):.2f}"
        )
        assert tokens.contrast_ratio(color, tokens.CASE) >= 3.0, (
            f"{slot} segment doesn't separate from the sheet: "
            f"{tokens.contrast_ratio(color, tokens.CASE):.2f}"
        )
    # the fixed order is part of the validation — never cycled
    expected = ("housing", "apparel", "food", "health", "transport", "other")
    assert expected == tokens.COMPOSITION_ORDER


def test_tier_colors_match_spec() -> None:
    spec_text = SPEC.read_text()
    for tier, color in tokens.TIER_COLORS.items():
        assert color in spec_text, f"tier {tier} color {color} not recorded in spec"
    assert tokens.PROVISIONAL in spec_text


def test_core_palette_matches_spec() -> None:
    """The folio's core surfaces and voices are recorded in the spec, not just in code."""
    spec_text = SPEC.read_text()
    core = {
        "ground": tokens.GROUND,
        "case": tokens.CASE,
        "case-2": tokens.CASE_2,
        "edge": tokens.EDGE,
        "ivory": tokens.IVORY,
        "ink": tokens.INK,
        "ink-soft": tokens.INK_SOFT,
        "brass": tokens.BRASS,
        "brass-deep": tokens.BRASS_DEEP,
        "copper": tokens.COPPER,
        "copper-deep": tokens.COPPER_DEEP,
        "gap": tokens.GAP,
    }
    for name, color in core.items():
        assert color in spec_text, f"{name} ({color}) not recorded in spec"


def test_glyph_opacity_bounds() -> None:
    assert tokens.glyph_opacity(None) == 0.55
    assert tokens.glyph_opacity(0) == 0.16
    assert tokens.glyph_opacity(100) == 1.0
    assert tokens.glyph_opacity(-5) >= 0.12
