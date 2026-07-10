# Design spec — the visualization layer (Plan 007 WI-2)

The production renderer's design language, inherited from the concept demo
(`docs/concept-demo/walkthrough.html`, non-truth-path) and made executable in
`src/vitrine/site/tokens.py`. **Tokens live in code; this document records the
decisions and the validation results.** A test asserts the two never drift
(`tests/test_design.py`).

## Principles

1. **Static, no JS.** Every page is pre-rendered; every interactive affordance
   works with JS disabled. The demo's click-to-inspect becomes anchor +
   CSS `:target`: every placard is a deep-linkable, citable URL.
2. **Light is the mood channel; hue is the meaning channel.** Hue does
   epistemology (tier chips, provisional, gap) and editorial voice (brass;
   copper for falling metrics). Decorative colorization is rejected — no
   era wallpaper, no upholstery reds. The ivory specimen label stays the
   brightest object on every page.
3. **Every mark names its fact.** Chart points, glyphs, meter segments and
   cutaway annotations carry `data-fact-id`; the mark-coverage gate fails the
   build if a mark's id doesn't resolve to a corpus fact or derived fact.

## Core tokens

| Token | Hex | Role |
|---|---|---|
| `ground` | `#1b1815` | page background — the dark gallery |
| `case` | `#242019` | display-case panel background |
| `case-2` | `#2c261e` | raised case surface / gradient partner |
| `edge` | `#413728` | case borders and hairlines |
| `ivory` | `#ece2cf` | specimen label card (brightest object) |
| `ivory-2` | `#e3d7bf` | label gradient partner |
| `ink` | `#2a2317` | text on ivory |
| `ink-soft` | `#998b70` | secondary text on dark surfaces (4.5:1 minimum) |
| `brass` | `#cf9f4c` | editorial voice: rising metrics, highlights, glyph strokes |
| `brass-dim` | `#7d663a` | quiet brass: structure lines, idle rings |
| `brass-deep` | `#a97f34` | brass on ivory (pressed/accent) |
| `brass-lit` | `#f0c778` | brass at full glow (hover/`:target`) |
| `copper` | `#c98a6a` | falling-metric bars (labour hours, food share) |

**Type.** Display serif `"Iowan Old Style", "Palatino Linotype", Palatino,
"Book Antiqua", Georgia, serif`; letterspaced uppercase mono labels
(`ui-monospace, "SFMono-Regular", Menlo, Consolas, monospace`); system sans
body. Numerals tabular in stat rows.

## The honesty vocabulary

Three states, rendered exactly as the demo drew them — never restyled per page:

| State | Color | Rendering |
|---|---|---|
| Tier A | `#7aa38c` | solid chip, white letter |
| Tier B | `#c79a44` | solid chip, white letter |
| Tier C | `#c5763e` | solid chip, white letter |
| Tier D | `#948a78` | solid chip, white letter |
| Provisional | `#b07a52` | `prov.` chip; value in copper-brown on ivory |
| Gap | dashed `#948a78` ring / italic | "not yet curated · would source from …" — never a confident guess |

A gap is content, not absence: chart slots and stage glyphs for gap facts render
a dashed outline and the words, at the same size as a sourced value.

## Era-graded stage light

The one place mood color moves: the stage spotlight tints per decade, an
editorial rendering of the sourced lighting-fuel / electrification fact family
(kerosene → incandescent → fluorescent → LED). Tints are the *inner glow* stop
of the stage's radial gradient (outer stops stay `case` → `ground`):

| Decades | Glow | Character |
|---|---|---|
| 1890s–1910s | `#3a2c17` | kerosene amber; narrow, dim pool |
| 1920s–1940s | `#392e1c` | early electric; warmer, wider |
| 1950s–1970s | `#322a20` | incandescent gold (the demo's stop) |
| 1980s–1990s | `#2f2b22` | fluorescent-warm white |
| 2000s–2010s | `#2c2b24` | CFL, cooler |
| 2020s | `#2d2e29` | LED white; brightest, widest pool |

**Constraint (checked, not assumed):** every semantic color that renders on
the stage — the four tier colors, provisional, brass, copper — holds **≥ 3:1
WCAG contrast against every era glow tint** and against `case`/`ground`.
`ink-soft` caption text never sits on the tinted stage; it is held to 4.5:1 on
`case`/`ground` where it does render. `tests/test_design.py` computes the full
cross-product; a new tint or semantic color that breaks it is a red build.

## Budget-composition categorical palette

*Position* carries category identity inside the cutaway (food at the table,
clothing at the closet), so the cutaway stays in the brass ramp. Categorical
hue appears only in corridor composition charts. Fixed assignment, never
cycled:

| Category | Dark stage `#1b1815` | Ivory card `#ece2cf` |
|---|---|---|
| housing | `#5b8fd6` | `#4d7fc4` |
| apparel | `#c06fae` | `#b05f9e` |
| food | `#8d983a` | `#7f8a2f` |
| health | `#1ca69e` | `#0f948c` |
| transport | `#d16a55` | `#c05a46` |
| other | `#9a938a` (neutral, outside the validated slots) | `#8a8378` |

Segments get **mandatory direct labels** and 2px surface gaps.

**Validator results** (six-checks validator, re-run 2026-07-08 against these
exact hexes):

- Dark stage, surface `#1b1815`: lightness band PASS (all 5 in L 0.48–0.67);
  chroma floor PASS (all ≥ 0.10); CVD separation PASS (worst adjacent
  `#c06fae`↔`#5b8fd6` ΔE 14.7 protan); contrast vs surface PASS (all ≥ 3:1).
- Ivory card, surface `#ece2cf`: lightness band PASS (all 5 in L 0.43–0.77);
  chroma floor PASS; CVD separation PASS (worst adjacent ΔE 14.0 protan);
  contrast **WARN** — `#7f8a2f` 2.93:1 and `#0f948c` 2.90:1 sit just under
  3:1. The WARN's mandated relief is the direct labels, which are therefore
  not optional on ivory.

## The artifact symbol library

Committed SVG symbols in `src/vitrine/site/symbols.py`, drawn in the demo's
stroke language: thin brass line work (`stroke-width` ≈ 1.7, round caps/joins),
sparing fills, 2–4 stroke primitives. One symbol per artifact **per era
bucket** (icebox → round-top refrigerator → french-door; console radio →
tabletop set; aerial TV → flat panel …). Acceptance bar: recognizable at 48px
without a label.

Symbols are decoration (non-truth-path) but their **appearance is gated**: a
symbol renders in a room only if a diffusion-family fact for that artifact
exists in that room. Absent technology isn't drawn. A fact with no `quantity`
keeps the dashed gap ring; diffusion percentage maps to glyph opacity
(`0.16 + 0.84 × pct/100`, floor 0.12), carried over from the demo unchanged.
