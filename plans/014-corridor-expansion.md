# Plan 014 — Corridor expansion: eight data-supported journeys

**Status:** draft
**Triggered by:** 2026-07-11 verification pass. The three recent data commits
(`836648e`, `dd21822`, `f52a182`) added ~60 facts across mortality, healthcare
costs, CEX expenditure shares, RECS energy, ATUS time use, rent, and FCC video
competition. Verification against source files confirmed all `value`/`quantity`
fields. Review of the existing 21 corridor arcs and 5 affordability metrics
revealed eight compelling cross-decade narratives the data supports but the
exhibit doesn't chart.

## The problem

The corridors currently chart diffusion (TV, telephone, internet, etc.),
demographics (family size, life expectancy, infant mortality), housing
(homeownership, plumbing, home size), labor (weekly hours, home production,
food share, wages), and CPI. The new data opens four narrative territories
the corridors don't enter:

1. **Public health** — mortality rates and cancer survival span 9 decades
   and tell the story of how medical innovation transformed American death.
2. **Healthcare economics** — NHE, out-of-pocket share, and CEX healthcare
   share together show the cost transformation from both the macro and
   family-budget perspective.
3. **Housing costs** — median gross rent has a clean 7-decade Tier A series
   with no arc.
4. **Budget composition** — apparel collapse, energy expenditures, and the
   expenditure-to-income ratio are untold stories in the existing
   composition charts.

The existing curation.py `Arc` structure and the corridor renderer need no
new machinery — each journey is a new `Arc` entry pointing at existing fact
ids. The only design question is grouping: which journeys share a chart,
and which stand alone.

## Design

### Arc readiness classification

| # | Journey | Decades | Facts exist? | Additional curation needed? | Priority |
|---|---------|---------|-------------|----------------------------|----------|
| 1 | Heart disease mortality | 9 (1940s–2020s) | Yes — 9 facts, all Tier A | None | High |
| 2 | Cancer mortality + survival | 9 / 6 | Yes — 6 mortality + 6 survival | None | High |
| 3 | Stroke mortality | 3 (1950s, 1970s, 2020s) | Yes — 3 facts, all Tier A | Sparse; could add 1960s, 1980s, 1990s, 2000s from NCHS | Medium |
| 4 | NHE as % of GDP | 7 (1960s–2020s) | Yes — 7 facts, all Tier A | None | High |
| 5 | Out-of-pocket share | 7 (1960s–2020s) | Yes — 7 facts, all Tier A | None | High |
| 6 | CEX healthcare share | 5 (1980s–2020s) | Yes — 5 facts, all Tier A | None | Medium |
| 7 | Median gross rent | 7 (1940s–2000s) | Yes — 7 facts, all Tier A | None | High |
| 8 | Heating fuel transition | 9 (1940s–2020s) | Yes — 9 facts, but no `quantity` | Needs `quantity` on each fact, or render as stage-only | Low |

### Grouping decisions

**ArcGroup: Mortality revolution.** Heart disease, cancer, and stroke share
one axis (age-adjusted deaths per 100,000) and one source family (CDC NCHS
+ NCHS Data Brief 548). Charting them together shows the three different
trajectories: heart disease peaked early and fell steadily; cancer rose for
decades before turning; stroke fell dramatically throughout. A grouped chart
with three lines is more compelling than three separate arcs. Cancer
survival is a separate arc (different unit: % surviving, different source:
SEER).

**ArcGroup: Healthcare cost transformation.** NHE as % of GDP and
out-of-pocket share share the same source (CMS NHE) and tell complementary
halves of one story: spending rose while direct payments fell. A grouped
chart with two lines — one rising, one falling — is visually striking. The
CEX healthcare share is a third line on a different axis (family budget %
vs national economy %); it stays as a standalone arc with a caveat noting
the different population.

**Standalone arcs.** Rent, heating fuel, apparel, and the video
entertainment journey are standalone. Rent is a simple dollar arc.
Heating fuel and apparel need `quantity` fields added to existing facts
before they can be charted.

### What doesn't need new machinery

The `Arc` dataclass, the corridor renderer, and the chart functions all
work with decade → fact-id mappings resolved at build time. Adding an arc
is adding an entry to the `ARCS` tuple in `curation.py`. The renderer
already handles sparse decades (renders gaps), falling metrics (copper
color), and caveats. No new code paths.

### What does need work

1. **Arc entries** in `curation.py` for each new journey.
2. **`quantity` fields** on heating fuel facts (currently multi-value
   strings with no single headline number — the gate requires `quantity`
   to appear verbatim in `value` for chart projection).
3. **Additional stroke mortality facts** for 1960s, 1980s, 1990s, 2000s
   if we want a denser arc (the NCHS data is available).
4. **Apparel share facts** for intermediate decades (only 1980s and 2020s
   currently have the anchor points; 1990s, 2000s, 2010s CEX data exists
   in `samples/19-cpi-tables/` and could be transcribed).
5. **One note correction**: `us-2000s-atus-time-use` notes field says
   "Percent working fell from 46.2% (2003) to 28.9% (2024)." The 28.9%
   appears to be the socializing-and-communicating percent in the 2024
   ATUS, not the working percent (which is ~37.3%). Fix the note.

## Work items

### WI-1: Mortality revolution arcs (data ready)

Add to `curation.py`:

- `Arc("heart-disease-mortality", ...)` — 9 decades, falling, quantity
  = age-adjusted deaths per 100,000. Facts: `us-{decade}-heart-disease-mortality`
  for 1940s–2010s, `us-2020s-heart-disease-mortality` for 2020s.
- `Arc("cancer-mortality", ...)` — 6 decades with data (1940s, 1950s,
  1970s, 1990s, 2010s, 2020s). The arc rises then falls; do not mark
  `falling=True`.
- `Arc("stroke-mortality", ...)` — 3 decades (1950s, 1970s, 2020s),
  falling. Sparse but honest.
- `Arc("cancer-survival", ...)` — 6 points across 6 decades (1960s,
  1970s, 1980s, 1990s, 2000s, 2010s, 2020s). Rising. Different unit
  (% surviving) and different source family (SEER/ACS) — standalone,
  not in the mortality group.
- `ArcGroup("mortality-revolution", ...)` grouping heart disease, cancer,
  and stroke on one chart.

**Acceptance:** `vitrine check` passes. `vitrine build` produces corridor
charts with the new arcs. Each arc's decade points resolve to the correct
fact. Gaps render for decades without a fact (e.g., cancer mortality in
1960s, 1980s, 2000s).

**Data gap note:** Heart disease has all 9 decades. Cancer mortality has
6 (missing 1960s, 1980s, 2000s). Stroke has only 3. All missing values
are available from the same CDC NCHS source and could be transcribed in
a follow-up WI. For now, the arcs render with gaps — which is the honest
display of what's curated.

### WI-2: Healthcare cost transformation arcs (data ready)

Add to `curation.py`:

- `Arc("nhe-gdp-share", ...)` — 7 decades (1960s–2020s), rising,
  quantity = % of GDP. Facts: `us-{decade}-nhe-total`.
- `Arc("out-of-pocket-share", ...)` — 7 decades (1960s–2020s), falling,
  quantity = % of total NHE. Facts: `us-{decade}-nhe-out-of-pocket-share`.
- `Arc("cex-healthcare-share", ...)` — 5 decades (1980s–2020s), rising,
  quantity = % of total expenditures. Facts: `us-{decade}-cex-healthcare-share`.
  Caveat: different population (consumer units vs national health spending)
  and different concept (budget share vs GDP share).
- `ArcGroup("healthcare-cost", ...)` grouping NHE-GDP and out-of-pocket
  on one chart (shared % axis, different concepts — caveat required).

**Acceptance:** Same as WI-1. The grouped chart shows two lines crossing:
GDP share rising from 5% to 18%, out-of-pocket falling from 47% to 10.5%.

### WI-3: Median gross rent arc (data ready)

Add to `curation.py`:

- `Arc("median-gross-rent", ...)` — 7 decades (1940s–2000s), rising,
  quantity = USD/month nominal. Facts: `us-{decade}-median-gross-rent`.
  Caveat: nominal dollars; the CPI arc and the affordability dashboard
  provide the deflation context.

**Acceptance:** Same as WI-1. The arc shows $27 → $602 across 60 years.
No 2010s or 2020s point (Census Historical Housing Tables end at 2000;
ACS rent data would need a new fact — deferred to a follow-up).

**Future data:** 2010s and 2020s median gross rent are available from
ACS Table B25064. Adding them would extend the arc to 9 decades. This
is a curation task, not a design task.

### WI-4: Note correction (trivial fix)

Fix the `notes` field of `us-2000s-atus-time-use` in `data/us/2000s.toml`:

- Change "Percent working fell from 46.2% (2003) to 28.9% (2024)" to
  "Percent working fell from 46.2% (2003) to 37.3% (2024)" — the 37.3%
  is the 2024 "Working and work-related activities" percent from ATUS
  Table A-1. The 28.9% was the "Socializing and communicating" percent,
  misidentified in the curator note.

**Acceptance:** `vitrine check` passes. The `value` and `quantity` fields
are unchanged (they were correct). Only the `notes` field changes.

### WI-5: Heating fuel transition arc (needs `quantity`)

The heating fuel facts exist for 9 decades (1940s–2020s) but their `value`
fields are multi-component strings like "Coal 55%, wood 23%, fuel oil
10%, utility gas 11%, other 1%" — no single headline number for the chart
to project. Two options:

**Option A (recommended):** Add a `quantity` to each fact representing the
dominant fuel's share (e.g., 55 for coal in 1940s, 35 for coal in 1950s,
55.2 for natural gas in 2000s, 47 for natural gas in 2020s). The arc
would show the rise and fall of leading fuels. But the "dominant fuel"
changes mid-series (coal → gas → electricity), so a single arc of
"dominant fuel share" would be conceptually incoherent.

**Option B:** Create three separate arcs — coal share, gas share,
electricity share — each tracking one fuel across decades. This is cleaner
but requires extracting each fuel's percentage as a separate `quantity`
on each fact, or creating new dedicated facts.

**Option C (deferred):** Leave as stage stats only. The heating fuel
transition is already visible in the room stage (the cutaway house shows
the heating fuel mix per decade). A corridor arc adds a cross-decade
view but the data structure doesn't fit the `Arc` model cleanly.

**Recommendation:** Defer to a follow-up plan. The heating fuel story is
better told as a stacked-area chart (new chart type) than as a line arc.

### WI-6: Apparel share arc (needs intermediate facts)

Only two anchor points exist: 1980s (6.0%, from `us-1980s-cex-total-expenditures`
notes) and 2020s (2.5%, from `us-2020s-cex-apparel-share`). The CEX data
for 1990s, 2000s, and 2010s exists in `samples/19-cpi-tables/cu-all-multi-year-*.xlsx`
and could be transcribed as apparel-share facts.

**Work:** Transcribe apparel expenditure and total expenditure from the
multi-year CEX tables for 1990s (1996), 2000s (2000), and 2010s (2012).
Compute the share. Create facts with `quantity` = apparel share %. Then
add `Arc("apparel-share", ...)` with 5 decades.

**Acceptance:** 3 new facts transcribed and verified against the Excel
source. Arc renders 5 points showing the decline from 6.0% to 2.5%.

### WI-7: Video entertainment journey (design needed)

The existing diffusion arcs (television, cable-tv, internet) chart
adoption percentages. But the video entertainment story is about the
*succession* of technologies — broadcast → cable → satellite → DVR →
streaming — and the ATUS data shows the behavioral consequence (TV
watching declining from 78.8% to 72.8% of the population).

This doesn't fit the existing `Arc` model well. It's more of a narrative
timeline than a single-metric arc. Options:

- **Standalone page:** A new "video entertainment" corridor section that
  combines existing arc points with a timeline annotation.
- **Extended arc:** Add an "hours of TV watching" arc using ATUS data
  (2003: 2.58, 2010: 2.73, 2024: 2.60) — sparse but interesting.

**Recommendation:** Defer to a design discussion. The data exists but the
narrative structure doesn't fit the current corridor model cleanly.

### WI-8: Expenditure-to-income ratio + bottom quintile (design needed)

The CEX expenditure-to-income ratio is available for 5 decades (93.5% →
75.4%), and the bottom quintile ratio (221.8%) is a powerful single
point. But the aggregate ratio hides the inequality story.

This would need either:
- A new arc for the aggregate ratio (5 decades, falling).
- A companion "bottom quintile" arc (only 1 data point — not enough for
  a line).
- A combined metric on the affordability dashboard showing the ratio
  with the bottom-quintile point as an annotation.

**Recommendation:** Add the aggregate ratio as a standalone arc (5
decades). Annotate the 2010s point with the bottom-quintile figure in
the arc's caveat. This is honest: the aggregate is a real trend, and the
bottom-quintile outlier is surfaced rather than smoothed.

## Phasing

| Phase | WIs | Effort | Dependency |
|-------|-----|--------|------------|
| 1 | WI-4 (note fix) | Trivial | None |
| 2 | WI-1 (mortality arcs) | Low — curation.py entries only | None |
| 3 | WI-2 (healthcare cost arcs) | Low — curation.py entries only | None |
| 4 | WI-3 (rent arc) | Low — curation.py entry only | None |
| 5 | WI-8 (expenditure-to-income arc) | Low — curation.py entry only | None |
| 6 | WI-6 (apparel arc) | Medium — 3 new facts + curation.py | Transcribe from Excel |
| 7 | WI-5 (heating fuel) | Deferred — needs new chart type | Design decision |
| 8 | WI-7 (video entertainment) | Deferred — needs new narrative structure | Design decision |

Phases 1–5 are pure curation.py edits plus one note fix — no new facts, no
new code, no new chart types. They could land in a single commit. The
data is verified and the arc machinery exists.

Phase 6 requires transcribing 3 new facts from existing Excel files. Phase
7–8 need design work beyond the current Arc model.

## Out of scope

- New chart types (stacked area for heating fuels, timeline for video).
- Additional decade facts for stroke mortality (available but not yet
  transcribed; arcs render with gaps until then).
- 2010s/2020s rent facts from ACS (available but not yet transcribed).
- Cross-country comparisons (v2 world rooms not yet built).
- Annual series for healthcare or mortality (the decade facts are
  sufficient for the corridor arcs; annual resolution would be a
  Plan 010 series-layer extension).
