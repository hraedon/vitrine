# Design spec — the statistical atlas (Plan 020)

The production renderer's design language. Tokens are executable in
`src/vitrine/site/tokens.py`; **this document records the decisions and the
validation results.** A test suite asserts the two never drift and computes
every contrast constraint (`tests/test_design.py`).

Plan 020 replaced the dark "night gallery" of Plan 007/019 with a light
statistical folio. The reasoning and the information-design moves are recorded
in `plans/020-the-statistical-atlas.md`; this file is the normative palette.

## Principles

1. **Static truth, progressively enhanced interaction.** Unchanged from the
   dark atlas: everything works with JavaScript disabled; anchor + CSS
   `:target` keeps record cards deep-linkable; one dependency-free script adds
   focus containment, Escape dismissal, background inertness, and focus
   restoration.
2. **Paper is the surface; ink is the voice; color is epistemology.** Pages
   are folio sheets with hairline rules and tabular numerals. Hue does only
   epistemology (tier chips, provisional, gap) and series direction (petrol
   rising, ember falling). The overlay record card is the brightest object on
   the page, still printed on the old ivory.
3. **Provenance in the scan-line.** Every fact row carries value, tier chip,
   the measured population, and the source record (publisher · year · tier)
   without a click. Drawers and overlays add depth, never prerequisites.
4. **Every mark names its fact.** Unchanged: chart points, glyphs, meter
   segments and cutaway annotations carry `data-fact-id`; the mark-coverage
   gate fails the build if a mark's id doesn't resolve to a curated fact.

## Core tokens

| Token | Hex | Role |
|---|---|---|
| `ground` | `#f2ecdd` | page background — paper |
| `case` | `#fbf7ec` | sheet/panel background |
| `case-2` | `#f5efe0` | inset tint (summing rows, drawer fills) |
| `edge` | `#d5c9ab` | hairline rules |
| `ivory` | `#fffdf7` | the overlay record card (brightest object) |
| `ivory-2` | `#f8f2e2` | card gradient partner |
| `ink` | `#29241b` | body text (≥ 7:1 on every surface — checked) |
| `ink-soft` | `#6e6450` | secondary text (4.5:1 minimum on paper) |
| `brass` | `#175d75` | atlas petrol — editorial voice, rising series |
| `brass-dim` | `#61798a` | quiet petrol — structure strokes, idle rings |
| `brass-deep` | `#0f4253` | petrol on hover/pressed |
| `brass-lit` | `#1e7a9c` | petrol bright — focus rings, current marker |
| `copper` | `#b34a13` | ember — falling series, caution borders |
| `copper-deep` | `#933d0e` | ember for small caution text (4.5:1) |

**Type.** Display serif `"Iowan Old Style", "Palatino Linotype", Palatino,
"Book Antiqua", Georgia, serif`; letterspaced uppercase mono metadata
(`ui-monospace, "SFMono-Regular", Menlo, Consolas, monospace`); system sans
body. Numerals tabular in stat rows and matrix counts.

## The honesty vocabulary

Rendered identically on every page, never restyled per page:

| State | Color | Rendering |
|---|---|---|
| Tier A | `#2f7a55` | solid chip, white letter |
| Tier B | `#8f6512` | solid chip, white letter |
| Tier C | `#7d4a63` | solid chip, white letter |
| Tier D | `#6e6a5e` | solid chip, white letter |
| Provisional | `#a45a2b` | `prov.` chip; flag styling |
| Gap | dashed `#6e6a5e` ring / italic, ember `#933d0e` counts | "no reliable record" — never a confident guess |

A gap is content, not absence: chart slots, stage glyph rings, fact rows, and
corpus-matrix cells all render it as a first-class state at full size.

**Constraints (checked, not assumed):**

- every semantic color — the four tier colors, provisional, petrol, copper —
  holds **≥ 3:1** against every sheet and every era wash;
- white chip letters hold **≥ 4.5:1** against every chip color;
- body `ink` holds **≥ 7:1** against every sheet and wash;
- `ink-soft` captions hold **≥ 4.5:1** on the three untinted sheets and are
  never placed on the tinted stage.

`tests/test_design.py` computes the full cross-product; a new tint or
semantic color that breaks it is a red build.

## Era-graded stage wash

The one place mood color moves: the stage's radial glaze per decade, the same
editorial rendering of the sourced lighting-fuel / electrification family as
before, re-inked for paper — deep amber pools for the kerosene decades,
clearing toward the neutral sheet as the grid and LED arrive.

| Decades | Wash | Character |
|---|---|---|
| 1890s–1910s | `#e8d9b8` | kerosene amber; narrow, saturated pool |
| 1920s–1940s | `#ece0c4` | early electric; softer, wider |
| 1950s–1970s | `#efe7d2` | incandescent tan |
| 1980s–1990s | `#f0ead8` | fluorescent-warm |
| 2000s–2010s | `#f2edde` | CFL, cooler |
| 2020s | `#f4f0e4` | LED neutral; widest, clearest pool |

The pool's geometry (radius tokens) is unchanged; the gradient runs
wash → `case` → `ground`, so the wash stays a tint of the paper, not a
foreign overlay.

## Budget-composition categorical palette (sheet variant)

*Position* carries category identity inside the cutaway, so the cutaway stays
in the petrol/ink family. Categorical hue appears only in corridor composition
charts, which now sit on light sheets. Fixed assignment, never cycled; every
segment carries its mandatory **white** direct label.

| Category | Sheet hex |
|---|---|
| housing | `#38618f` |
| apparel | `#8f3f7d` |
| food | `#4f6b20` |
| health | `#11706a` |
| transport | `#a84c38` |
| other | `#6e6a5e` (neutral, outside the validated slots) |

Segments keep the 2px surface gaps. **Validator results** (computed by
`tests/test_design.py` at this writing, 2026-07-29): every slot holds
≥ 4.5:1 against its white label and ≥ 3:1 against the sheet `#fbf7ec`;
weakest pairs are `other` at 5.40:1 (label) and 4.58:1 (sheet).

## The lobby and corpus matrix

The index leads with country entrances, each offering a selected route into
its own evidence. The United States opens the illustrated equipment record,
the United Kingdom opens its housing and equipment records, and Japan opens
its thematic collection. Native disclosures beneath each entrance expose
every decade without JavaScript. The reading guide and whole-museum counts
are optional; the complete composite-family disclaimer remains visible.

The detailed matrix is a separate research inventory below the visitor routes:
curated rooms × the six cases, counted. Counts are **build metadata**, folded
from the corpus rather than authored: sourced records exclude documented gaps,
derived exhibits have their own count, and gaps are labelled separately. Each
cell links to the corresponding room panel. These counts describe holdings,
not historical prevalence or confidence. Country collections stay separate.

## The artifact symbol library

Unchanged: committed SVG symbols in `src/vitrine/site/symbols.py` per artifact
per era bucket, gated by the existence of a diffusion-family fact in the room;
diffusion percentage maps to glyph opacity (`0.16 + 0.84 × pct/100`,
floor 0.12). Strokes re-inked: glyphs and annotations in petrol `#175d75`,
structure in quiet `#61798a`, gaps dashed in `#6e6a5e`.

## Page dramaturgy

Plan 030 makes the exhibit the entrance and the inventory a second layer.
The US rooms explicitly selected in `HOUSE_ROOMS` open with a source-linked
house and four sourced highlights beside it. The house is an illustrated
index with fixed geometry, not a measured floor plan or reconstructed family.
Primary object exclusions apply to both the house and its labelled object
list; excluded records remain in the complete inventory and source cards.
Sparse collections use selected observations or a compact research entrance.
Japan's thematic collection remains its principal entrance.

The decade selector is one horizontal row, with contained scrolling on small
screens. Editorial status explains the selection in a disclosure; the full
composite-family disclaimer remains visible. Source-linked highlights still
resolve to exactly four distinct in-room facts where a route is curated.

Below the exhibit, three counters separate sourced records, derived
exhibits, and documented gaps. Counts describe collection entries, not people
or households, and gaps are never zero values. Six topic links lead to the
complete record panels, each folded behind a native topic summary. Opening a
topic reveals every row's value, evidence tier, measured population, and source.
The full drawer adds detail and the source card opens independently of the fold.
Record fragments reveal their topic natively without JavaScript; topic-map links
land at the summary, which can be opened normally. The enhancement opens the
chosen topic and provides expand/collapse controls for reading the whole room.
Closed records remain printable. Calculations identify their inputs and
weakest-input tier.

The sourced-record bucket includes records with a value calculated from
published source inputs. Such records carry an "Includes a calculated value"
badge; their row drawer, source card and source collection show the declared
method and rounding rule. That check covers its declared value, not every
number in a compound record. Derived exhibits form a separate structural
bucket combining curated records or series. Audit-calculated values are not
added to that bucket or counted twice.
The lobby's detailed curated inventory is likewise a second layer, with
explicit count labels in every cell and footer. Country collections stay separate.

Browser qualification uses production response headers and checks component
geometry at phone and desktop widths; see `production-layout-policy.md`.

Trend, affordability and essay charts offer native table disclosures as a
second reading path. Selected points keep their source-card links; annual
tables list the actual source years and population without filling missing
years. A record excluded from a plotting axis is labelled "Not plotted".
Calculated annual values cite their input series and disclose their display
rounding. Tables adapt to the page width while retaining column headings and
bounded vertical scrolling for long series. The plot itself keeps its scale
and contained horizontal scroll on narrow screens.

An arc's excluded record remains accessible but cannot supply geometry or a
shared-axis comparison elsewhere. The same exclusion applies to direct metric
markers, pair cells, walkthrough bars and stage annotations. Illustrative
mid-decade positions are labelled as such; table periods use the curated
decade or an explicitly declared record year, with the source date retained
in the record label.

Withdrawn composition shares retain their decade slot as a linked, labelled
gap rather than an empty bar or an omitted row. Both the main corridor and
pair views preserve this source access. Literal food-category expenses do
not become percentage-axis values when no comparable expenditure denominator
has been verified.

Docent tours (Plan 016) render as narrow reading columns: prose blocks with an
accent rule, every interpolated figure an inline chip (petrol value, tier
letter), chart blocks identical to their corridor renderings. No new tokens;
the disclaimer strip rides below the standfirst on every tour.
