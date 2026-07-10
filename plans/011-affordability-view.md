# Plan 011 — The affordability view: how much life cost, over time

**Status:** implemented 2026-07-09; chart-honesty and readability refinements
landed 2026-07-10
**Triggered by:** 2026-07-09 owner discussion. The corpus has structured
amounts (home values, car prices, hourly wages, median income) and anchors
for 1940s–2020s, but affordability is scattered across pairwise corridor
pages, hand-computed `home-as-income-years` facts, and `week-of-work-buys`
narratives. There is no single surface where a visitor can see "when did
housing stop being affordable?" or "how many hours did a car cost in 1973?"
This plan builds that surface, drawing on Plan 010's series layer for
annual resolution where the data supports it.

## What this plan builds

A fourth surface alongside rooms, corridors, and walkthrough: the
**affordability dashboard**. A single page (not 78 pairwise pages) showing
multiple affordability metrics as time-series charts, each with full
provenance and the same tier/measure/gap vocabulary as the rest of the
museum.

The dashboard answers questions the decade rooms can't:
- *When did the single-earner family die?* (Wage coverage chart: 95% in
  1960s → 49% in 2000s.)
- *How bad was the housing bubble?* (Home-as-income-years chart: 1.9 in
  2000 → 4.5 at peak 2006 → 3.0 by 2012.)
- *Did cars actually get less affordable?* (Car-as-hours-of-work chart:
  surprisingly flat at ~1,100 hours for most of the postwar era.)
- *When did food stop being the main expense?* (Food-share chart: 42.5%
  in 1901 → 13.5% in 2024, with the steepest drop in the 1950s.)

## Design

### D1 — Metrics are computed, never authored

Every metric on the dashboard is a ratio of two structured quantities
from the corpus or series layer. The renderer computes the ratio; no
curator writes a number. This is the same principle as Plan 006's derived
facts, extended to cross-decade series.

A metric is declared in `curation.py` as:

```python
AFFORDABILITY_METRICS: tuple[Metric, ...] = (
    Metric(
        slug="home-as-income-years",
        label="A median home, in years of median family income",
        numerator="median-home-value",       # series id or fact-id pattern
        denominator="median-family-income-4p",
        unit="years",
        caveats=("Pre-2005 home values are decennial only.",),
    ),
    Metric(
        slug="car-as-hours-of-work",
        label="A new car, in hours of work",
        numerator="car-price",                # series id or fact-id pattern
        denominator="hourly-earnings-total-private",
        unit="hours",
    ),
    ...
)
```

The renderer resolves each metric for every year where both numerator and
denominator have values. Years with only one side render as gaps — the
same "render the gap" ethos.

### D2 — Five launch metrics

| Metric | Numerator | Denominator | Coverage | Source of annual data |
|--------|-----------|-------------|----------|----------------------|
| Home as years of income | Median home value | Median 4-person family income | 1947–2024 annual denominator; numerator decennial 1940–2000, annual 2005–2024 | Plan 010 series |
| Car as hours of work | New car price | Hourly earnings (total private) | 1970–2020 annual (car series starts 1970, AHETPI starts 1964, BEA ends 2020); earlier decades as decade-fact markers only | Plan 010 series (`new-car-price`) + decade facts |
| Single-earner wage coverage | Weekly manufacturing earnings × 52 | Median family income (all) | 1947–2024 (both series must cover the year) | Plan 010 series (`weekly-earnings-manufacturing`) |
| Food share of expenditure | Food expenditure | Total expenditure | Decade points only | Decade facts (no annual series) |
| Real wage index | Hourly earnings (nominal) | CPI-U | 1964–2024 (AHETPI start) | Plan 010 series |

Coverage windows are set by the *intersection* of numerator and
denominator series — a metric never extends past the shorter side; the
chart's x-axis still runs 1900–2024 so the missing early decades read as
the gap they are.

Metric 3 uses **weekly** earnings × 52, not hourly × hours × 52: the
weekly series (Plan 010 WI-3) avoids smuggling in a weekly-hours
assumption that changed from ~40 to ~34 over the century. If annualizing
weekly pay (×52, no unpaid-weeks adjustment) needs stating, it goes in
the assumption ledger, not in code comments.

Metric 5 (real wage index) requires a **base-year decision**: nominal
wage ÷ CPI is only an index after normalization. The base year is
declared on the `Metric` in `curation.py` (proposed: 2024 = 100, so the
chart reads "a 1970 hour of work bought X% of what a 2024 hour buys")
with the rationale in the metric's caption. This is an editorial choice
and lives in the curation registry like every other editorial choice.

Metrics 1–3 and 5 use Plan 010 series for annual resolution. Metric 4
(food share) has no annual series — CEX is conducted continuously from
1980 but the size-of-CU tables we use are annual and could be a future
series. For launch, it renders as decade points (the existing `food-share`
arc data).

### D3 — Chart mechanics

Each metric renders as a **time-series arc chart** — an extension of the
existing `arc_chart` function, but with:

- **X-axis is years, not decades.** Range: 1900–2024 (or the metric's
  coverage window). Ticks at decade boundaries (1900, 1910, ..., 2020)
  with minor ticks at mid-decade.
- **Points, not bars.** Small circles (r=2) at each year with data. Decade
  facts that also exist (e.g. the 1950s room's `$7,354` home value) are
  drawn as larger labeled markers (r=4, brass) with `data-fact-id` — the
  mark-coverage gate covers them.
- **Recession bands.** NBER recession dates are drawn as vertical
  copper-tinted bands behind the chart. This is structural context, not
  a fact — the recession dates are from NBER (a well-known public-domain
  series, cited in the page footer). No `data-fact-id` on the bands
  themselves; they're annotation, not data. But annotation is still
  data entering the museum: the dates are **transcribed from
  nber.org/research/business-cycle-dating, never recalled**, and this is
  the first data to bypass the fact gate, so its provenance requirements
  are spelled out in WI-4 rather than left implicit.
- **Gap rendering.** Years without data for either numerator or
  denominator are simply absent — no line, no marker. The viewer sees the
  gap. This is how 1940–2005 home values (decennial only) render: 7
  points connected by implied trend, not a false interpolation.
- **Measure-mismatch caveat.** If a metric's numerator or denominator
  series changes `measure` mid-run (e.g. manufacturing wages → total
  private wages in 1980), a caveat banner renders at the splice point.

### D4 — Layout

The dashboard is a single page at `/affordability/`. Layout:

1. **Header:** "Affordability over time" + one-paragraph framing
   (composite-family disclaimer, nominal values, methodology link).
2. **Five charts, stacked vertically**, each ~300px tall. Full width.
3. **Each chart has:**
   - Title (metric label)
   - The chart (SVG, inline, same design tokens as corridors)
   - A one-sentence "what this shows" caption (curated, in `curation.py`)
   - Placard links: clicking a point opens the provenance overlay (same
     `:target` mechanism as rooms/corrids)
4. **Footer:** recession date source (NBER), methodology notes, links to
   the decade rooms for context.

No JS. No server-side state. Same static-site model as everything else.

### D5 — Navigation

- The corridors page gets a new link: "Affordability over time →"
- Each room's work-buys panel gets a link: "See this metric across all
  decades →" pointing to the dashboard with `#metric-slug` anchor.
- The walkthrough's final stop (2020s) gets a link: "How did we get
  here? →" pointing to the dashboard.

## Work items

### WI-1: `Metric` dataclass + `AFFORDABILITY_METRICS` registry

In `curation.py`: `Metric` dataclass (slug, label, numerator, denominator,
unit, caveats, caption). The `AFFORDABILITY_METRICS` tuple declares the
five launch metrics. Numerator/denominator are strings that resolve to
either a series id (Plan 010) or a fact-id pattern (decade facts). The
renderer tries series first, falls back to decade facts.

### WI-2: Time-series arc chart function

`render.py` — new `_affordability_chart(metric, corpus, series, root)`
function. Takes a metric, resolves numerator/denominator to series or
facts, computes ratios per year, renders SVG. Extends the existing
`arc_chart` with year-axis ticks, recession bands, and decade-fact
markers. Must pass the mark-coverage gate for any decade-fact markers.

### WI-3: Affordability dashboard page

`render.py` — `_render_affordability(corpus, series, root)` builds
`_site/affordability/index.html`. Stacks the five charts. Includes the
composite-family disclaimer, methodology footer, recession band source
citation. Adds to the main navigation (the corridor index page gets a
link; the room nav bar gets a link).

### WI-4: NBER recession dates

A small data file `data/recessions.toml` with NBER recession start/end
dates. These are annotation, not facts — they don't go through the fact
gate. But they don't escape provenance either:

- The dates are **transcribed** from the NBER business-cycle chronology
  page, never recalled. Verification-log entry like any transcription.
- `recessions.toml` carries a top-level `url` field naming the source
  page, and the CI link checker that covers `data/sources.toml` URLs is
  **extended to also check this file** — otherwise it becomes the one
  citable URL nothing watches.
- The file lives in `data/`, not inline in `curation.py`: data is data,
  even annotation data. (The inline option is rejected.)

The dashboard footer cites it: "Recession dates: NBER Business Cycle
Dating Committee." No `data-fact-id` on recession bands.

### WI-5: Measure-mismatch caveats for series splices

Extend `compare.py`'s existing measure-guard to work with series. When a
metric's denominator series changes `measure` (e.g. manufacturing wages
1939–1963 → total private 1964→), the renderer draws a vertical splice
marker and a caveat. The existing `caveats` tuple on `Metric` handles
static caveats; this handles dynamic ones.

The dynamic guard only sees series `measure` changes — it does **not**
cover methodology changes inside a numerator assembled from decade
facts. The known case is the car-price line: wholesale averages
(1910s–1960s), transaction prices (1970s–2020s), list price (1900s).
The car-as-hours metric therefore ships with a **static caveat** naming
the methodology change at the 1960s→1970s boundary ("the jump partly
reflects a change from wholesale to transaction prices, not only real
price change"). The same caveat belongs on the existing corridor
"A new car" line (`curation.py` AFFORD_ITEMS) — this WI adds it there
too, closing the gap flagged in the 2026-07-09 reflection.

### WI-6: Tests

- Dashboard renders without errors.
- Each metric chart has at least one data point (no empty charts).
- Decade-fact markers resolve via `data-fact-id` (mark-coverage gate).
- Recession bands don't carry `data-fact-id` (annotation, not data).
- Dashboard page is linked from corridors and at least one room.
- Dashboard renders with no series data (falls back to decade facts only).

## Dependencies

- **Plan 010 (series layer)** is a hard dependency for annual resolution.
  Without it, the dashboard still works but renders decade points only —
  which is what the existing corridors already do. The dashboard's value
  proposition is annual resolution.
- **Plan 006 (derived facts)** established the "computed, never authored"
  principle. This plan extends it to cross-decade metrics. No changes to
  Plan 006 needed.

## Out of scope

- Per-decade affordability breakdowns (the pairwise corridor pages already
  do this).
- Rent affordability (no structured rent data yet — future curation).
- Healthcare/education affordability (no structured price data yet).
- Interactive controls (date range, metric toggle) — no JS rule holds.
- International affordability (v2 world rooms not yet built).
