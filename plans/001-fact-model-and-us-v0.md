# Plan 001 — Fact model + US V0 (three rooms, full mechanic)

**Status:** proposed
**Goal:** prove the museum mechanic end-to-end at minimum scale: the fact
model and provenance gate from `docs/fact-model.md`, a renderer with the
six-panel skeleton and provenance drawers, and three fully curated US rooms
spanning the tier range. If the mechanic works at 3 rooms it works at 80.

## Work items

### WI-1 — US source registry and decade survey

Catalog the primary sources for US 1890s–2020s before curating anything:
which source anchors each decade, at which tier, with URL and surveyed
population. Deliverables: `data/sources.toml` populated for the US;
`docs/us-sources.md` — one section per decade stating the anchor source,
tier, and known caveats (e.g. 1940 census income is wage/salary only).

Anchor map to verify and pin down (from the planning discussion):
- 1947→: Census P-60 / Historical Income Tables (Table F-8 has family-of-four
  medians by size — check its actual coverage window). Tier A.
- 1940s: IPUMS 1940 decennial microdata (wage/salary income only). Tier B.
- 1890s–1930s: 1890–91 Commissioner of Labor survey, 1901 BLS cost-of-living
  survey, 1918–19 BLS survey, 1935–36 Study of Consumer Purchases; Historical
  Statistics of the US (Millennial Edition); MeasuringWorth series. Tier C.
- Housing amenities: Census of Housing 1940→; earlier from the surveys above.
- Diffusion series: Historical Statistics + HUD/AHS + Pew/Census for internet.

**AC:** every US decade 1890s–2020s has a named anchor source in the registry
with a working URL and a stated population; `vitrine check` green.

### WI-2 — Three V0 rooms curated

`data/us/1900s.toml` (Tier C), `data/us/1950s.toml` (Tier A),
`data/us/2020s.toml` (Tier A) — all six panels populated in each room, every
fact transcribed from its source (not from model memory), assumption ids
attached where they apply. Gaps rendered honestly.

**AC:** ≥4 facts per panel per room or an explicit gap fact; `vitrine check`
green; spot-check by following 5 random source URLs to the cited table.

### WI-3 — Renderer: rooms, drawers, methodology

`vitrine build` renders to `_site/`: an index (the museum lobby: decade
strip per country), one page per room with the six-panel skeleton, a
provenance drawer per fact (source card: title, publisher, year, population,
tier badge, URL, notes), the composite-family disclaimer on every room, and a
methodology page generated from `data/assumptions.toml`. Schematic styling;
no external assets (self-contained static output).

**AC:** `vitrine build` produces a browsable site from the V0 data; disclaimer
present on every room page; every rendered fact's drawer shows source +
population + tier; site passes a link-lint for internal hrefs.

### WI-4 — Gate hardening + render coverage

Implement invariant 7 from the fact model: the renderer records which fact
ids it displayed; `vitrine check --against-build _site/` (or equivalent
manifest comparison) fails if rendered ≠ curated. Wire the full gate into CI.

**AC:** deleting a fact's source entry breaks CI; rendering a fact not in
`data/` (or dropping one) breaks CI.

### WI-5 (stretch) — Lab deployment

nginx container serving `_site/`; deployed in the lab. Static output means
this is trivial; do it only after WI-1..4 are green.

## Decisions taken at planning time

- Name: **vitrine** (overload scan 2026-07-06: PyPI squatted by inactive
  0.1.0 package — irrelevant, not publishing to PyPI; no GitHub collision in
  this space).
- `value` stays a display string in V0; structured numerics are a later,
  additive extension (see fact model).
- Illustration ambition deferred: schematic HTML/CSS in V0; SVG room
  illustrations are a later plan; no AI-generated imagery in v1.
- v2 country set fixed: UK (over Germany, on data depth), Poland, Russia
  (over a current-sphere satellite, on data quality), China, India, Japan.
  Not in scope for this plan.

## Risks

- **Sourcing is the schedule.** WI-1/WI-2 are reading-and-transcribing work;
  agent memory *will* offer plausible numbers — the hard rule is transcribe
  from the fetched source only.
- **Table F-8 coverage window** (family-of-four medians) may start later than
  1947; if so the four-person normalization assumption does more work in
  early Tier-A decades and must say so.
- **Scope creep on visuals** — held off by WI-3's schematic-only AC.
