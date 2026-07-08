# Plan 007 — The visualization layer: the museum gets its architecture

**Status:** proposed
**Triggered by:** owner direction 2026-07-08. The walkthrough concept demo is
adopted as the design reference (`docs/concept-demo/walkthrough.html`,
non-truth-path); this plan turns its design language into the production
renderer.

## What this plan builds

The current renderer is the deliberate V0 schematic. This plan replaces it
with three surfaces, all pre-rendered, all drawing exclusively from fact ids:

1. **Rooms** (one decade) — the gallery proper: dark stage, house cutaway
   with era-specific artifact glyphs, ivory specimen-label cards, the budget
   basket rendered spatially (food at the table, clothing at the closet…).
   Texture and concreteness; few charts.
2. **Corridors** (cross-decade arcs) — where charts live: diffusion,
   affordability-in-hours, budget composition, life expectancy. Curated epoch
   comparisons (1900s ↔ 1950s ↔ 2020s) featured; the full pairwise set
   generated behind them, each page showing only fact families the measure
   guard certifies comparable for that pair — everything else renders as the
   gap it is.
3. **The walkthrough** (Plan 005's transect) — the one editorial path:
   figures, true-scale house, labour-hours meter beside the diffusion glow.
   Lands on this plan's primitives (Plan 005 WI-5/WI-6 close here).

## Design decisions

### D1 — Static, no JS. The demo's interactions translate:

| Demo (JS)                          | Production (static)                       |
|------------------------------------|-------------------------------------------|
| decade buttons swap state          | pre-rendered page per decade, same button row as links |
| click glyph/person → specimen card | anchor + CSS `:target` — every placard is a deep-linkable URL |
| animated house rescale             | static per-page scale (animation dropped)  |
| JS-inlined data objects            | fact-id lookups at build time              |

The `:target` placard is an upgrade, not a concession: every object's
provenance card becomes a citable address.

### D2 — Build-time SVG from fact ids; the mark-coverage gate.
Charts and stages are Python functions (facts → inline SVG) in the `[site]`
extra. **Every mark carries the fact id it projects** (`data-fact-id`), the
facts-manifest includes chart marks, and a gate asserts every rendered mark
resolves to a corpus fact or derived fact. A mark that can't name its fact
doesn't render. This subsumes Plan 005 WI-6 (walkthrough coverage).

### D3 — Design tokens inherited from the demo, recorded in
`docs/design-spec.md`: ground `#1b1815`, case `#242019`/`#2c261e`, edge
`#413728`; ivory label `#ece2cf`/`#e3d7bf`, ink `#2a2317`; brass voice
`#cf9f4c` (dim `#7d663a`, deep `#a97f34`, lit `#f0c778`); tier colors
A `#7aa38c` · B `#c79a44` · C `#c5763e` · D `#948a78`; provisional `#b07a52`.
Iowan/Palatino serif display, letterspaced mono labels, system sans body.
The three-way honesty vocabulary (tiered / provisional / gap) renders exactly
as the demo drew it, including "not yet curated · would source from".

### D4 — Color strategy: light is the mood channel, hue is the meaning channel.
The demo's restraint is load-bearing — hue currently *does epistemology*
(tier chips, provisional, gap) and editorial voice (brass; copper for falling
metrics). Decorative colorization of objects or interiors would spend that
channel. Color is added in exactly two places, where it carries meaning:

- **Era-graded stage light.** The spotlight gradient and vignette tint per
  decade: kerosene amber and a narrow, dim pool (1900s) → incandescent gold
  (mid-century) → cool bright LED white (2020s). This is the "scenes pop"
  lever: each room reads differently at a glance, and the tint is an
  editorial rendering of a sourced fact family (lighting fuel /
  electrification), not decoration. Constraint: every semantic color must
  keep ≥ 3:1 contrast on every tinted stage — checked per tint, not assumed.
- **Budget-composition categorical palette.** In the cutaway, *position*
  carries category identity (that's the metaphor), so the cutaway stays in
  the brass ramp. Only the corridor composition charts need categorical hue.
  Palette (validated 2026-07-08 with the six-checks validator; all checks
  pass on the dark stage; ivory variant passes with a contrast WARN relieved
  by mandatory direct labels):
  - dark stage `#1b1815`: blue `#5b8fd6`, plum `#c06fae`, olive `#8d983a`,
    teal `#1ca69e`, brick `#d16a55`
  - ivory card `#ece2cf`: blue `#4d7fc4`, plum `#b05f9e`, olive `#7f8a2f`,
    teal `#0f948c`, brick `#c05a46`
  Fixed assignment (never cycled): housing=blue, apparel=plum, food=olive,
  health=teal, transport=brick; "other" = neutral `#9a938a`, outside the
  validated slots. Direct labels on all segments; 2px surface gaps.

Explicitly rejected: era-authentic interior palettes (wallpaper greens,
upholstery reds). Pretty, but it turns the museum into a dollhouse and buries
the tier vocabulary in confetti. The ivory specimen label stays the brightest
object on every page.

### D5 — The artifact symbol library.
The demo's glyphs are 2–4 stroke primitives and identical across eras. Ship a
committed SVG symbol library, one symbol per artifact **per era** (icebox →
round-top refrigerator → french-door; wringer → top-loader → front-loader;
console radio → rabbit-ear set → flat panel; …), drawn in the demo's stroke
language (thin brass line work, sparing fills). Acceptance bar: recognizable
at 48px without a label. Symbols are decoration (non-truth-path) but their
*appearance is gated*: a symbol renders only if a diffusion fact for that
artifact exists in that room — absent technology isn't drawn, gaps keep the
dashed ring, diffusion-as-opacity carries over unchanged.

## Work items

- **WI-1** prerequisite: merge `wi-1/us-source-survey` (CEX shares 1970s–2010s,
  BLS CES wages, Ramey hours), reconcile with the post-Plan-006 gap-log
  (generated inventory wins), full gate green.
- **WI-2** `docs/design-spec.md`: tokens, honesty vocabulary, color strategy,
  palette + validator results, symbol-library stroke rules.
- **WI-3** SVG primitives in the `[site]` extra + `data-fact-id` on every
  mark + mark-coverage gate; import-boundary test still holds.
- **WI-4** artifact symbol library, era-keyed; test: symbol set ⊆ artifacts
  with diffusion facts, per room.
- **WI-5** room redesign: dark gallery, `:target` specimen cards, cutaway
  with spatial budget shares, era-graded light with the contrast check.
- **WI-6** corridors: the three epoch pages (curated) + generated pairwise
  set, measure-guard-filtered; every point deep-links to its room placard.
- **WI-7** walkthrough on the primitives: labour-hours meter (drawn to the
  data's shape) + true-scale house — closes Plan 005 WI-5/WI-6.

## Acceptance criteria

1. `_site/` contains rooms, corridors, and the walkthrough, all static, no
   `<script>` in truth-path pages; every interactive affordance works with
   JS disabled.
2. The mark-coverage gate is red if any rendered mark (chart point, glyph,
   meter segment, cutaway annotation) fails to resolve to a fact id.
3. Every semantic color passes ≥ 3:1 on every era tint; the budget palette's
   recorded validation matches the shipped hexes.
4. A symbol never appears in a room lacking its diffusion fact; absent
   technology is not drawn.
5. Ruff, `mypy --strict`, pytest, `vitrine check`, build + `check
   --against-build` green; render-coverage includes all three surfaces.

## Not in scope

- JS charting libraries, client-side rendering, animated transitions.
- Narration or authored argument text (charter).
- Non-US rooms (v2 floors) and new curation beyond WI-1's merge.
- Deployment (nginx container on the homelab cluster when ready — a
  directory of static files; no plan needed).
