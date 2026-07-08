"""Design-token invariants (Plan 007 WI-2 / acceptance criterion 3).

The spec says the era-tint contrast constraint is *checked, not assumed*, and
that the palette recorded in docs/design-spec.md matches the shipped hexes.
Both live here.
"""

import re
from pathlib import Path

from vitrine.site import tokens

SPEC = Path(__file__).parent.parent / "docs" / "design-spec.md"


def test_semantic_colors_hold_contrast_on_every_stage_surface() -> None:
    """Every stage semantic color >= 3:1 against every era glow tint and both cases."""
    surfaces = {"ground": tokens.GROUND, "case": tokens.CASE, "case-2": tokens.CASE_2}
    surfaces |= {f"glow-{d}": g for d, g in tokens.ERA_GLOW.items()}
    surfaces["glow-default"] = tokens.ERA_GLOW_DEFAULT

    failures = [
        f"{name} on {sname} ({surface}): {tokens.contrast_ratio(color, surface):.2f}"
        for name, color in tokens.SEMANTIC_ON_STAGE.items()
        for sname, surface in surfaces.items()
        if tokens.contrast_ratio(color, surface) < 3.0
    ]
    assert not failures, "semantic colors below 3:1 on a stage surface:\n" + "\n".join(failures)


def test_caption_text_holds_contrast_on_untinted_surfaces() -> None:
    """ink-soft captions case/ground only; it must hold 3:1 there."""
    for name, color in tokens.CAPTION_ON_DARK.items():
        for surface in (tokens.GROUND, tokens.CASE):
            assert tokens.contrast_ratio(color, surface) >= 3.0, f"{name} on {surface}"


def test_every_decade_has_a_glow_and_pool() -> None:
    assert set(tokens.ERA_GLOW) == set(tokens.ERA_POOL)
    for decade in tokens.ERA_GLOW:
        assert re.fullmatch(r"1[89]\d0s|20\d0s", decade)


def test_composition_palette_matches_recorded_validation() -> None:
    """AC 3: the palette validation recorded in the spec matches shipped hexes."""
    spec_text = SPEC.read_text()
    for slot in tokens.COMPOSITION_ORDER:
        assert tokens.COMPOSITION_DARK[slot] in spec_text, f"{slot} (dark) not in spec"
        assert tokens.COMPOSITION_IVORY[slot] in spec_text, f"{slot} (ivory) not in spec"
    # the fixed order is part of the validation — never cycled
    expected = ("housing", "apparel", "food", "health", "transport", "other")
    assert expected == tokens.COMPOSITION_ORDER


def test_tier_colors_match_spec() -> None:
    spec_text = SPEC.read_text()
    for tier, color in tokens.TIER_COLORS.items():
        assert color in spec_text, f"tier {tier} color {color} not recorded in spec"
    assert tokens.PROVISIONAL in spec_text


def test_glyph_opacity_bounds() -> None:
    assert tokens.glyph_opacity(None) == 0.55
    assert tokens.glyph_opacity(0) == 0.16
    assert tokens.glyph_opacity(100) == 1.0
    assert tokens.glyph_opacity(-5) >= 0.12
