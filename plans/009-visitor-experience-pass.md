# Plan 009 — The visitor experience pass: interaction, charts, rooms, and surfaces

**Status:** proposed
**Triggered by:** 2026-07-08 owner review of the live site at vitrine.hraedon.com.
Twenty-three items of structured feedback across rooms (10), corridors (10),
walkthrough (1), and general (4). This plan organizes them into six phases by
shared mechanics, not by surface — many items (popup placards, axis rounding)
touch more than one surface and should be fixed once, correctly.

## Design constraint: the no-JS rule and this plan

The charter says "Static, no JS" (Plan 007 D1; design-spec principle 1). Every
interactive affordance currently works via CSS `:target`, which causes the page
to jump. Several feedback items ask for popup/overlay behavior instead. **This
plan holds the line:** every new interaction is pure CSS, no `<script>`. The
key insight is that `:target` + `position: fixed` gives us overlays without
scroll — the hash still changes (deep links still work), but the page doesn't
move. A JS-dependent item (corridor budget hover breakdown, #C8) gets a
CSS-only fallback or is deferred to a future JS plan.

## Phase 1 — Interaction model (the highest-impact UX changes)

### WI-1: Popup placards instead of page-jump (Room #2, Corridor #1)

**Problem:** Clicking a stage glyph or chart point navigates to the placard's
anchor, scrolling the page mid-view. Disruptive in rooms; jarring in corridors
(it flashes to the room page).

**Solution:** Pure-CSS overlay modal via `:target` + `position: fixed`.

Currently placards are inline `<div class="placard" id="...">` that the browser
scrolls to on `:target`. The change:

1. Room placards: keep them inline in the DOM (for no-JS fallback and
   print), but add a CSS overlay layer. Each glyph/link gets
   `href="#fact-id--modal"` and a hidden overlay placard
   `<div class="placard-overlay" id="fact-id--modal">` is rendered once per
   room (reusing the placard macro). CSS: `.placard-overlay{display:none;
   position:fixed; inset:5vh 10vw; z-index:100; overflow:auto}` and
   `.placard-overlay:target{display:block}`. A close affordance
   `<a href="#" class="overlay-close">×</a>` dismisses via hash clear. The
   inline placards remain for deep-link sharing and `:target`-without-overlay
   (e.g. if someone links to `#us-1950s-median-income` directly, it still
   scrolls+highlights as today — the overlay is the *click* path, the inline
   is the *link* path).
2. Corridor chart points: same overlay mechanism. The chart point's `href`
   currently goes to `../rooms/us-1950s.html#fact-id` (cross-page). Change to
   `#fact-id--modal` and render an overlay placard *on the corridor page*
   containing the fact's data. This requires the corridor page to carry the
   fact data it references — the render already has the `index` (fact→room
   mapping), so the overlay placard can be generated inline. No cross-page
   navigation on click; the deep-link path (right-click → copy link) still
   points to the room placard.

**Acceptance:** clicking a glyph/chart point surfaces the placard as an
overlay without scroll; the URL hash changes (deep-linkable); closing the
overlay returns to the prior scroll position; works with JS disabled.

### WI-2: Larger clickable hit area for appliance glyphs (Room #4)

**Problem:** Appliance glyphs are only clickable on their drawn stroke
elements — the circle ring and the glyph paths. The space inside the ring
isn't clickable (it's a `<g>` with no fill on the ring).

**Solution:** Add an invisible `<rect>` or `<circle>` hitbox inside each
artifact group, sized to the glyph's bounding box (±18 from center, covering
the ring and the glyph). `fill="transparent"` (not `none`) so it captures
clicks. One line per artifact in `svg.stage_svg()`.

**Acceptance:** clicking anywhere within the ring or the glyph's bounding
box opens the placard overlay; the hit area is visually imperceptible.

### WI-3: Collapsible room panel sections (Room #6)

**Problem:** All six panels render fully expanded; long rooms are a wall of
cards.

**Solution:** Wrap each panel section in `<details open><summary>` with the
panel title as the summary. CSS styles the summary as the existing
`case-title` heading. All panels default `open` (current behavior preserved);
visitors can collapse the ones they don't need. The `<details>` element is
no-JS, keyboard accessible, and semantic.

**Acceptance:** each of the six panel sections is independently
collapsible; default state is open (no regression); keyboard
`Enter`/`Space` toggles; works with JS disabled.

### WI-4: Corridor budget-composition hover breakdown (Corridor #8)

**Problem:** Mousing over a category segment in the budget composition bar
should show a breakdown — most important for "other," which is opaque.

**Solution:** CSS-only tooltip via `:hover`. Each composition segment
already carries a `<title>` (native tooltip). Enhance: add a CSS
`:hover`-visible breakdown `<div>` positioned above the segment, showing
the categories folded into that slot and their individual shares. The
breakdown data is already parsed by `_fold_shares()` (it has the original
category names before folding). For "other," list the subcategories. No JS.

**Acceptance:** hovering a segment shows its subcategory breakdown; "other"
is the priority — it names every category folded into the neutral slot;
works with JS disabled.

## Phase 2 — Chart rendering fixes (corridors)

### WI-5: Y-axis rounding (Corridor #3)

**Problem:** Y-axis labels show raw computed values (35.748, 71.496, 102.384)
instead of rounded increments.

**Solution:** In `svg.arc_chart()`, round `q_top` up to the nearest multiple
of 5 (or a "nice" number — 1/2/5/10/20/50/100 depending on magnitude). The
three gridlines (0, 0.5×q_top, q_top) then read as clean numbers. Implement a
`_nice_axis_top(q_max)` helper that picks the smallest "nice" number ≥ q_max
× 1.08.

**Acceptance:** every arc chart's y-axis labels are multiples of 5 (or a
nice increment); the top label is ≥ the max data point; no decimal-only
labels.

### WI-6: Telephone arc: >100% fix and cell/landline split (Corridor #4, #5)

**Problem:** The telephone arc tops out at 102.384% — the 1900s fact
(`us-1900s-diffusion`) has `quantity = 5` (a composite "5% of families had
[a telephone]") that doesn't belong on the telephone arc cleanly. The 2020s
point counts cell phones (92.7%) while earlier points count landlines — a
concept splice rendered as a single line.

**Solution:**

1. **Fix the >100%:** audit the 1900s diffusion fact — if its `quantity` is
   not telephone-specific, exclude it from the telephone arc (render the
   1900s as a gap) or correct the quantity. The arc's caveats already note
   "1910s–1930s sources counted telephones per 1,000 population" — those
   decades already render as gaps. The 1900s entry needs the same treatment
   if it's not a household telephone percentage.
2. **Split cell/landline:** add a second arc variant — `telephone-cell` and
   `telephone-landline` — where the chart draws two lines (brass for landline
   adoption rising then falling, copper for cell phone adoption rising).
   This needs:
   - New facts or restructured existing facts: the 2020s fact already has
     both values in its `value` string ("Cell phone 92.7%, landline 20.1%").
     The landline arc needs facts for earlier decades (landline was the only
     phone; the existing telephone facts *are* landline facts through the
     1990s). The cell arc needs a 2020s fact with `quantity = 92.7`.
   - A new chart function `svg.dual_arc_chart()` that draws two series on
     shared axes, or extend `arc_chart()` to accept multiple series.

**Acceptance:** no value exceeds 100% on the telephone chart; cell and
landline render as separate lines on the same chart with a legend;
landline peaks and declines, cell phone rises.

### WI-7: Label collision with x-axis (Corridor #2)

**Problem:** The 1960s data-point label for several charts (poverty, women's
home production, food share, weekly hours) collides with the top of the
x-axis area. This happens when a data point sits near the top of the chart
(its `vlab` text at `cy - 9` overlaps with the x-axis label row at
`height - 26`).

**Solution:** In `arc_chart()`, clamp the value label y-position to
`min(cy - 9, pad_t + 8)` — labels for high data points render *below* the
dot instead of above it when there's no room above. Also ensure the x-axis
label row (`height - 26`) and the value label row never overlap by checking
`cy - 9 < height - 30` before placing above.

**Acceptance:** no value label overlaps any x-axis decade label; high-value
points place their labels below the dot when above would collide.

### WI-8: Y-axis gap rendering for sparse arcs (Corridor #9)

**Problem:** Infant mortality and food share charts have y-axes that appear
to jump from '00s to '50s — the gridlines are computed from the max quantity
but the x-axis shows all decades, making it look like the y-axis skips.

**Solution:** The issue is that the chart plots decades at even x-spacings
but only some have data. The connecting line is dashed across gaps (already
implemented), but the y-axis gridlines are continuous (0/0.5/1.0 of q_top).
The fix: add explicit gap markers on the x-axis for decades with no data
(small `·` or a faded tick), so the visitor sees "no data here" rather than
"the axis jumped." Alternatively, only render x-axis labels for decades that
have data points, with the gap decades shown in a faded style. The existing
`gapdot` + `gaplab` mechanism at the bottom of the chart already handles this
for facts that exist but have no quantity — extend it to decades that have
no fact at all in the arc.

**Acceptance:** the visitor can distinguish "no data for this decade" from
"the axis skipped a value"; gap decades are visibly marked on the x-axis.

### WI-9: Men's home production on the same chart as women's (Corridor #10)

**Problem:** Men's and women's home production are separate arcs with
separate y-axes, making visual comparison misleading (men's bars look
comparable in height but represent fewer hours on a different scale).

**Solution:** Render both series on the same chart — either:
- A dual-series arc chart (like the telephone split in WI-6), or
- A grouped bar chart (women's and men's hours side by side per decade).

The dual-series approach is more consistent with the existing chart language.
Women's hours in copper (falling), men's in brass (rising). Shared y-axis.
The existing `home-production-women` and `home-production-men` arcs provide
the data; the chart function from WI-6 can be reused.

**Acceptance:** women's and men's weekly hours render on the same chart
with a shared y-axis; the visual comparison is honest; both series carry
tier labels and deep-link to their placards.

### WI-10: Cable TV label wording (Corridor #6)

**Problem:** "% of TV households" reads awkwardly; "% of households with TV"
is clearer.

**Solution:** One-line change in `curation.py`: the `cable-tv` arc's `unit`
field from `"% of TV households"` to `"% of households with TV"`. Also update
the arc label if needed. Gate-verified (no fact values change).

**Acceptance:** the cable TV chart's unit caption reads "% of households
with TV."

### WI-11: "Featured" → "Detailed" epoch comparisons (Corridor #7)

**Problem:** "Featured Epoch Comparisons" suggests clicking one regenerates
the landing-page charts for that period; instead it takes you to a page with
the pairwise comparison (no landing-page charts).

**Solution:** Rename the section heading to "Detailed epoch comparisons" in
the corridors index template. Consider adding a one-line sub-caption:
"Side-by-side fact families for each pair — the charts above cover the full
century."

**Acceptance:** the heading reads "Detailed epoch comparisons"; the
sub-caption sets expectations.

## Phase 3 — Room enhancements

### WI-12: The composite family in the room (Room #1)

**Problem:** Rooms show the house cutaway but not the people. The walkthrough
has figures (father, mother, children) but rooms don't.

**Solution:** Add family figures to the room stage SVG, standing in the
cutaway. The `_FIGS` dict in `render.py` already has the SVG primitives.

**Labels — era-evolving, less heteronormative:**
The user is "open to different, less heteronormative labels, especially as
we get more modern and gender roles become less rigid." Approach:
- 1900s–1940s: "The earner" / "The homemaker" / "The children" — period-
  accurate role labels (the 1900s family at the median had one earner and one
  homemaker by the gendered division of the era; labeling them by *role*
  not *gender* is both accurate and less jarring than "father/mother").
- 1950s–1970s: "The earner" / "The homemaker" / "The children" — still
  accurate for the median family (single-earner era), and the role label
  avoids assuming gender.
- 1980s–2020s: "Parent A" / "Parent B" / "The children" — the median family
  shifted to two earners; gender-neutral and reflects the modern family
  structure. The "Parent A/B" labeling also avoids implying a primary/
  secondary earner hierarchy.

This requires no data-model change — the labels are editorial (which
figure SVG goes where) and live in the renderer. The figures themselves
are decorative (non-truth-path), like the stage glyphs.

**Note:** Plan 005 proposed an `actor` field for binding facts to figures.
That model change is *not* needed for this WI — the figures are decoration;
the stat rows already live in the placards. If per-figure stats on the
room page are wanted later, that's Plan 005's scope.

**Acceptance:** the room stage shows four figures in the cutaway; labels
are era-appropriate and less heteronormative; figures don't overlap the
artifact glyphs or zone notes.

### WI-13: House size scaling in rooms (General #2)

**Problem:** The room stage's house cutaway is the same size in every room
— a 1900s 4-room home and a 2020s 7-room home render identically.

**Solution:** Scale the house outline (the `<polygon>`/`<rect>`/`<line>` in
`svg.stage_svg()`'s `structure` group) by the room's floor-area datum. The
walkthrough already computes a `scale` from `area_fact.quantity /
sourced_area` (render.py:1136). Apply the same logic to the room stage:
- If the room has a floor-area fact with a `quantity`, scale the structure
  outline by `sqrt(quantity / max_area_across_corpus)`.
- If no floor-area fact, use a default scale (the current size).
- The artifact positions (`STAGE_POS`) need to scale with the house, or
  stay fixed while the house shrinks (the house shrinks around them,
  showing that the artifacts fill more of the space — the 1900s home is
  cramped). The latter is more visually honest.

**Data dependency:** Floor-area facts are sparse (only 1900s and 2020s have
them in the walkthrough registry). This WI should also extend
`curation.STAGE_STATS` or a new `FLOOR_AREA` registry to cover more
decades. Plan 008 WI-4 (floor area by decade) is the curation dependency;
this WI renders what exists and gaps the rest.

**Acceptance:** rooms with sourced floor area render a visibly scaled house;
rooms without it render the reference outline with a gap note; the
artifact glyphs don't overlap the scaled structure.

### WI-14: Data-gap prominence banner (Room #10)

**Problem:** Rooms with significant unsolvable data gaps (e.g. war periods,
the 1940s bifurcation) don't surface this prominently — the visitor has to
scroll to discover the gaps.

**Solution:** Add a "data-gap banner" at the top of the room page (below the
decade selector, above the stage) when the room has an above-threshold gap
density. The banner is a styled `<div class="gap-banner">` in brass/copper
that names the structural gap. The threshold and text are editorial:
- The 1940s room: "The 1940s are bifurcated — pre-war and post-war figures
  are from different surveys and different economies; the gap is structural."
- Rooms with >40% gap facts: "Many measures for this decade have no reliable
  record — the gaps are shown, not guessed."

Computed at build from the gap inventory (`vitrine gaps` / `room_gaps()`),
which already counts missing panels and structural gaps. The banner is
gated: it only renders when the gap count exceeds a threshold.

**Acceptance:** the 1940s room shows its structural-gap banner without
scrolling; rooms with no significant gaps show no banner; the banner text
names the specific gap reason (not generic).

### WI-15: "Reading the Museum" legend — color the color words (Room #9)

**Problem:** The legend says "Falling metrics render in copper, rising in
brass" but doesn't color the words "copper" and "brass" — they're similar
tones and the visitor can't tell which is which.

**Solution:** In the `_TIER_LEGEND` template, wrap "copper" and "brass" in
`<b style="color:{copper}">copper</b>` and `<b style="color:{brass}">brass</b>`.
Bold + colored. One-line template change.

**Acceptance:** "copper" renders in copper (#c98a6a), bold; "brass" renders
in brass (#cf9f4c), bold; the two are visually distinguishable.

### WI-16: Small visualizations in placards (Room #5)

**Problem:** "The Table" panel shows the food basket as a contextless list;
a small chart (bar, donut, or pictogram) would make it easier to ingest.

**Solution:** Add an optional `placard_chart` field to the placard macro
that renders a small inline SVG when the fact's `value` contains parseable
structured data (percentages, prices, quantities). Chart types by panel:
- **Table (food basket):** a mini horizontal bar chart of food item prices
  (parsed from `value` if it contains "$X, $Y, $Z" patterns) or a pictogram
  of food categories.
- **Budget (expenditure shares):** a mini donut chart of the composition
  (reusing the `parse_shares()` logic already in `svg.py`).
- **Diffusion:** a mini progress-ring showing the adoption percentage.

The chart is small (80–120px), sits below the value/unit, above the
provenance drawer. It's decoration-of-the-data (the value text is the truth
path; the chart is a projection of it). The mark-coverage gate applies: the
chart's marks carry `data-fact-id`.

**Scope:** start with the food basket (the named pain point); extend to
other panels as the parse patterns are validated. A registry in
`curation.py` maps fact ids → chart type.

**Acceptance:** "The Table" placards in rooms with food-basket facts show a
mini chart; the chart's data matches the fact's `value` (gate-enforced via
quantity-verbatim); the chart deep-links to the same placard.

### WI-17: Work-buys panel — hours-to-afford in the display (Room #8)

**Problem:** "A day's work buys" placards show "$650 Oldsmobile" with a
generic "A day's work buys" header repeated for each item. The user wants
hours-to-afford computed and displayed: "Oldsmobile Curved Dash consumed
51 weeks of work."

**Solution:** The affordability engine already computes `hours_to_afford`
for structured `TOTAL`-basis facts. The work-buys panel placards should
surface this in the *display value area* (not just the provenance drawer):
- If the fact has `basis = TOTAL` and the room has a wage anchor, the
  placard renders a prominent "≈ N hours / N weeks of work" line in the
  value area (not the drawer).
- The header for each work-buys placard should be the item name, not
  "A day's work buys" — e.g. "New car (Oldsmobile Curved Dash)" with the
  hours/weeks figure below.
- For items where the hours figure is very large (>2000 hours), convert to
  weeks (÷ weekly hours) or years (÷ annual hours) for readability.

This is a rendering change in the placard macro — the affordability data is
already computed and passed to the template (`affordability[fact.id]`).

**Acceptance:** work-buys placards show hours/weeks-to-afford prominently;
the header names the item, not the panel; the figure is computed (not
authored) and gated by the affordability engine.

### WI-18: Explanation for "impossible" results (Room #7)

**Problem:** The 1900s work-buys fact says "60 weeks to cover annual
expenses" — impossible (a year has 52 weeks). The explanation ("year-round
work by multiple family earners") is in the curator note, hidden in the
provenance drawer.

**Solution:** Two-part fix:
1. **Data:** the `value` string should carry the explanation inline —
   "60 weeks of a single earner's wages to cover annual expenses (multiple
   earners worked year-round)." The `notes` field is for the curator; the
   `value` is for the visitor.
2. **Rendering:** when a work-buys or affordability figure exceeds a
   threshold (e.g. >52 weeks, >2000 hours), the placard renders a visible
   caveat note below the value: "This exceeds a single year — see the
   placard for why." This is a rendering rule, not a data fix for every
   fact.

The 1900s fact's `value` needs editing to surface the multi-earner
explanation; other "impossible" results get the rendering caveat
automatically.

**Acceptance:** the 1900s work-buys placard explains the 60-week figure
visibly (not hidden in the drawer); any future affordability figure that
exceeds a single year shows a caveat.

## Phase 4 — New surfaces

### WI-19: Bibliography page (Room #3)

**Problem:** No bibliography page. `docs/citations.md` exists but is
hand-written and not rendered; `data/sources.toml` has 56 fully-cited
sources.

**Solution:** Render a `bibliography.html` page from `data/sources.toml`,
sorted by publisher (Census Bureau, BLS, IPUMS, …) then year. Each entry
renders the full citation: title, publisher, year, URL (linked),
population (who was measured), and notes. Tier usage is not on the source
(it's on the facts) — show a count of facts citing each source, with a link
to the first room that uses it.

Add to the top nav: `vitrine | corridors | walkthrough | methodology |
bibliography`.

The page is a projection of the source registry (like methodology is a
projection of the assumption ledger). No new data needed.

**Acceptance:** `bibliography.html` lists all 56 sources with full
citations; each links to its URL; the source count matches the registry;
the page is in the top nav; `vitrine check` render-coverage includes it.

## Phase 5 — Glyphs, overlap, and the vision pass

### WI-20: Expand the artifact symbol library (General #1)

**Problem:** Glyphs are minimal (2–4 stroke primitives) and identical for
many artifacts within a panel. The food basket glyph is a single bowl;
the user wants individual food items rendered.

**Solution:** Extend `symbols.py` with:
- **Food items:** bread, milk, eggs, potatoes, meat — each a 2–3 stroke
  glyph, arranged in the food zone of the stage as a small still-life.
  The items that render are gated by the food-basket fact's content
  (parse the `value` for item names).
- **More era variants:** the existing library has 1–3 variants per
  artifact; add intermediate forms (e.g. 1970s push-button phone between
  rotary and handset; 1990s CRT TV between rabbit-ear and flat-panel).
- **New artifacts:** washing machine, stove/range (separate from heating),
  and the food-basket items above.

Add a glyph tracker section to `docs/resource-hunt.md` (or a new
`docs/glyph-tracker.md`) listing every artifact and its era variants,
marked done/pending, so the next agent knows what's left.

**Acceptance:** the food zone shows individual food item glyphs when the
basket fact names them; the glyph tracker lists all artifacts and their
status; the symbol-gate test still passes (symbols only render for
rooms with the diffusion fact).

### WI-21: Vision-model overlap and placement audit (General #3)

**Problem:** Lots of item overlap and odd placement in the room stages.
Artifact positions (`STAGE_POS`) were carried from the demo's layout and
haven't been checked against the scaled house or the new figures.

**Solution:** A per-room audit using a vision-capable model. For each of
the 13 rooms:
1. Build the room page.
2. Screenshot the stage SVG.
3. Send to a vision model with the prompt: "Identify overlapping elements,
   off-position labels, and glyphs that don't fit the house outline."
4. Fix the positions in `STAGE_POS` / `ZONE_NOTE_POS`.
5. Re-screenshot and verify.

This is a WI-per-room or a plan-phase-per-room. Given 13 rooms, a single
agent session can do 3–4 rooms; the plan should track which rooms are
done. The `STAGE_POS` dict is the single source of truth — fixes there
propagate to all rooms.

**Acceptance:** a vision-model pass confirms no overlaps in audited rooms;
`STAGE_POS` positions are adjusted; the stage-gate test still passes.

## Phase 6 — Walkthrough

### WI-22: Walkthrough flow polish (Walkthrough #1)

**Problem:** The walkthrough "could flow more smoothly" but the feedback is
not well-considered.

**Solution:** Defer. After Phases 1–5 land, the owner reviews the
walkthrough again with specific feedback. The popup-placard interaction
(WI-1) and the chart fixes (WI-5–9) may resolve the flow issues without
targeted walkthrough work. Log as a placeholder; revisit after Phase 5.

## Phase 7 — General fixes

### WI-23: Decade label disambiguation (General #4)

**Problem:** "'00s" means 1900s, but "2000s" is also "00s" — confusing in
charts that span both centuries.

**Solution:** In `svg._tick()`, change the label format:
- 1890s–1990s: `'{decade[2:4]}s` → `'{decade[:4]}s` (e.g. "1900s", "1950s")
  only when the chart contains both 1900s and 2000s; otherwise keep the
  short form.
- The function can check: if `any(p.decade.startswith("20") for p in points)
  and any(p.decade.startswith("19") for p in points)`, use full decade
  labels; else short.

Also apply to the pairwise comparison table headers and the budget
composition bar labels.

**Acceptance:** in charts spanning 1900s–2020s, all decade labels are
fully written ("1900s", "2020s"); in charts spanning only one century,
short labels are fine.

## Dependencies and ordering

```
WI-1 (popup placards)          ← no deps; do first (everything else builds on it)
WI-2 (hit areas)               ← no deps
WI-3 (collapsible sections)    ← no deps
WI-5 (axis rounding)            ← no deps
WI-7 (label collision)         ← no deps
WI-10 (cable TV wording)       ← no deps
WI-11 (featured→detailed)      ← no deps
WI-15 (legend colors)          ← no deps
WI-18 (impossible results)     ← data edit + rendering
WI-19 (bibliography)           ← no deps
WI-23 (decade labels)           ← no deps

WI-6 (telephone split)         ← WI-5 (axis rounding) for the new chart
WI-9 (men's home prod chart)   ← WI-6 (dual-series chart function)
WI-4 (budget hover)            ← WI-1 (overlay mechanism may inform tooltip style)

WI-12 (family figures)         ← WI-13 (house scaling) for positioning
WI-13 (house scaling)           ← data: floor-area facts (Plan 008 WI-4)
WI-14 (gap banner)             ← no deps; uses existing gap inventory
WI-16 (placard charts)          ← WI-1 (overlay placards may change layout)
WI-17 (work-buys display)       ← no deps; affordability engine exists

WI-20 (glyph expansion)        ← no deps; additive to symbols.py
WI-21 (vision audit)           ← WI-12, WI-13, WI-20 (after layout changes)
```

## Acceptance criteria

1. Clicking any glyph or chart point surfaces the placard as an overlay —
   no page scroll, no cross-page navigation. Works with JS disabled.
2. Every arc chart's y-axis labels are rounded to nice numbers; no value
   exceeds 100% where 100% is the conceptual maximum; cell and landline
   telephone render as separate lines.
3. The composite family renders in every room stage, with era-appropriate
   labels; the house scales by floor area where sourced.
4. Rooms with significant data gaps show a prominent banner without
   scrolling; "impossible" affordability figures are explained visibly.
5. A bibliography page lists every source with full citations, linked
   from the top nav.
6. Work-buys placards show hours/weeks-to-afford prominently, with the
   item name as the header.
7. Decade labels are unambiguous in any chart spanning both centuries.
8. A vision-model audit confirms no overlap/placement issues in the
   room stages; the glyph tracker records the symbol library status.
9. Ruff, `mypy --strict`, pytest, `vitrine check`, build + `check
   --against-build` green; render-coverage includes the bibliography page.

## Not in scope

- JavaScript (the charter's no-JS rule holds; all interactions are CSS).
- Plan 005's `actor` field (the figures are decoration; per-figure stats on
  the room page are a future enhancement if the owner wants them).
- New data curation beyond the floor-area facts needed for WI-13 (Plan 008
  covers the curation backlog; this plan is about rendering what exists).
- The 1890s room or v2 world rooms (Plan 008 WI-11).
- Narration or authored argument text (charter).