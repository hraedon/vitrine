# Plan 002 — Locale split (urban/suburban/rural) + artifact objects

**Status:** proposed (feasibility assessment)
**Triggered by:** user request to evaluate (a) three visualizations per
decade for urban/suburban/rural, and (b) clickable amenity objects with
composite cost, lifespan, and modern-era comparisons.

## What this plan evaluates

1. **Locale split:** Can the museum show three rooms per decade — urban,
   suburban, rural — instead of one national-median room?
2. **Artifact objects:** Can the museum show clickable objects (refrigerator,
   automobile, radio, telephone) that display composite cost, average
   lifespan, diffusion rate, and inline comparison to the modern equivalent?

The short answer: **both are feasible, but on different timelines.** The
locale split is a data-model extension that can follow WI-2. The artifact
objects are a deeper model extension that should follow the structured-
numerics planned extension to the fact model. Both have honest data floors
that the museum must render, not paper over.

---

## Part 1: Locale split (urban / suburban / rural)

### The "suburban" problem

The U.S. Census Bureau has never had a "suburban" category. The Census
classifies residence as:

- **Urban** — places with 2,500+ population (definition has changed over
  time; "urbanized areas" introduced 1950; "urban clusters" added 2000)
- **Rural** — everything not urban
- **Metropolitan** — core county (50k+ pop) + adjacent counties with
  economic ties (MSAs introduced 1949, standardized through OMB)
- Within metropolitan: **inside central city** and **outside central city**

The closest Census proxy for "suburban" is **metropolitan, outside central
city**. The museum would define:

| Museum locale | Census proxy | Notes |
|---|---|---|
| Urban | Inside central city, metropolitan | Principal city of a metro area |
| Suburban | Outside central city, metropolitan | The "suburban" derivation |
| Rural | Nonmetropolitan | Outside any MSA |

This derivation is a methodological choice that must be an assumption in the
ledger. The Census itself says "non-metropolitan" is not the same as "rural"
(many metro counties contain rural territory), so the mapping is approximate.

**New assumption needed:** `suburban-locale-definition` — "Suburban" is
defined as metropolitan, outside central city. This is a derived concept, not
an official Census category. The Census's metropolitan classification has
changed over time (MSAs introduced 1949, OMB standards revised 1980, 2000,
2010, 2020). Earlier decades use the urban/rural binary only.

### Data availability by era

| Era | Urban | Suburban | Rural | Anchor source | Tier |
|---|---|---|---|---|---|
| 1890s–1920s | ✅ | ❌ | ❌ | Commissioner of Labor surveys (urban only) | C |
| 1930s | ✅ | ✅† | ✅ | 1935–36 Study of Consumer Purchases (51 cities / 140 villages / 66 farm counties) | C |
| 1940s | ✅ | ⚠️ | ✅ | IPUMS 1940 census (URBAN + METRO variables) | B |
| 1950s–1960s | ✅ | ⚠️ | ✅ | Census of Housing (urban/rural); IPUMS for metro split | A/B |
| 1970s–2000s | ✅ | ✅ | ✅ | CPS + AHS (metro/nonmetro, inside/outside central city) | A |
| 2010s–2020s | ✅ | ✅ | ✅ | ACS + AHS + CPS | A |

† Villages in the 1935–36 survey are the closest proxy for "suburban" in the
pre-metro-classification era.

**Key finding:** The Census Historical Income Tables (F-1 through F-23) do
**not** include a metro/nonmetro or urban/rural income table. The tables
break out by quintile, race, region, state, family type, size, age, earners,
and education — but **not by residence**. Income by locale must be computed
from IPUMS microdata (Tier B) or extracted from individual P-60 reports that
included metro/nonmetro tables (inconsistent across years).

### Pre-1930s: the honest gap

Before the 1930s, the surveys were explicitly urban/industrial. The 1890-91
Commissioner of Labor survey covered "industrial workers in selected
industries." The 1903 survey covered "wage-earner families in selected
industrial centers." The 1918-19 survey covered "shipbuilding centers + 13
large cities."

There is no rural or suburban data for these decades. This is not a gap in
the museum's sourcing — it is a gap in the historical record. The museum
should show the urban room only, with an explicit "no reliable record exists
for rural or suburban families in this decade" statement for the other two
locales. This is the "render the gap" principle applied to locale.

### Impact on the fact model

**Room entity changes:**

```python
@dataclass(frozen=True, slots=True)
class Room:
    country: str
    decade: str
    locale: str  # NEW: "national" | "urban" | "suburban" | "rural"
    facts: tuple[Fact, ...]

    @property
    def slug(self) -> str:
        if self.locale == "national":
            return f"{self.country}-{self.decade}"
        return f"{self.country}-{self.decade}-{self.locale}"
```

**File layout changes:**

- National rooms (backward compatible): `data/us/1950s.toml` with
  `locale = "national"` (default)
- Locale rooms: `data/us/1950s-urban.toml`, `data/us/1950s-suburban.toml`,
  `data/us/1950s-rural.toml`
- The loader detects locale from the `[room]` table; the check validates
  that locale facts use sources whose `population` field matches the locale

**Assumption ledger additions:**

- `suburban-locale-definition` — defining suburban as metro, outside central city
- Update `urban-rural-split` — currently scoped to V2 countries; now applies
  to V1 US as well, with the pre-1930s caveat

**Room count impact:**

Assuming locale rooms for decades 1930s–2020s (where data exists) and
national rooms for 1890s–1920s (urban-only, with gaps for suburban/rural):

- 1890s–1920s: 4 decades × 1 national room = 4 rooms (with gap statements)
- 1930s–2020s: 10 decades × 3 locale rooms = 30 rooms
- Total: 34 rooms (up from 14 national rooms)

Not all panels will have data for all three locales in every decade — the
"render the gap" rule applies. The national room may remain as a fallback
or be dropped in favor of locale rooms only.

### Source registry additions

New sources needed for locale-split rooms:

| Source | Coverage | Tier | URL |
|---|---|---|---|
| 1935–36 Study of Consumer Purchases — Urban Series | City families | C | FRASER (search-confirmed) |
| 1935–36 Study of Consumer Purchases — Village Series | Village families | C | FRASER (needs verification) |
| 1935–36 Study of Consumer Purchases — Farm Series | Farm families | C | FRASER (needs verification) |
| IPUMS METRO variable | 1940–present | B | usa.ipums.org ✅ |
| Census of Housing — urban/rural tables | 1940–present | A | census.gov ✅ |
| AHS metro/nonmetro tables | 1973–present | A | census.gov ✅ |
| ACS income by metro status | 2005–present | A | data.census.gov ✅ |

---

## Part 2: Artifact objects (clickable amenities)

### What the user wants

When a visitor views a room, they see schematic objects (a refrigerator, a
car, a radio, a telephone, a stove). Clicking an object opens a drawer
showing:

1. **Composite cost** — what the item cost in period money, and as a share
   of median annual family income
2. **Average lifespan** — how long the item typically lasted before
   replacement
3. **Diffusion** — what percentage of families in this locale/decade had one
4. **Modern comparison** — the equivalent item today: cost, lifespan,
   diffusion, with inline comparison ("a 1950 refrigerator cost 3.2% of
   annual income; a 2024 refrigerator costs 1.1%")

### Data availability

**Pricing (strong):**

- **Sears, Roebuck catalogs** — available on Internet Archive (1897, 1900s,
  1910s) and HathiTrust (1922, 1923). Duke University holds a collection
  spanning 1902–1994. These are the primary source for period prices of
  consumer goods across all decades.
- **BLS Consumer Expenditure Survey (CEX)** — expenditure shares by category
  (food, housing, transportation, etc.) from 1960 onward, continuous from
  1980. Good for budget-context pricing but not individual-item prices.
- **BLS CPI detailed commodity data** — price indices for specific goods
  (refrigerators, automobiles, televisions) from the CPI database.

**Lifespan (weak for historical, strong for modern):**

- **AHAM** (Association of Home Appliance Manufacturers) — publishes average
  lifespan estimates for major appliances. Modern data only.
- **NAHB Study of Life Expectancy of Home Components** — estimates lifespan
  for appliances, building components. Available at
  `pointofviewhomeinspection.com/NAHB-Lifetimes.pdf`. Modern data.
- **DOE Energy Saver** — mentions 10–20 year lifespans for appliances.
  Modern data.
- **Consumer Reports** — reliability and longevity data. Modern, subscription.
- **Historical lifespan** — NO systematic source exists for how long a 1950
  refrigerator or a 1920 radio actually lasted. This would need to be
  reconstructed from:
  - Period consumer reports / magazine articles (Consumer Reports started
    1936; earlier from Good Housekeeping, etc.)
  - Scholarly work on consumer durables
  - Industry historical data
  - The honest fallback: Tier D ("scholarly estimate; no contemporaneous
    survey") with a note that the estimate is derived, not measured

**Diffusion (strong):**

- **Census of Housing** (1940→) — asked about radio, refrigerator, telephone,
  automobile, TV, washing machine, plumbing, electricity. By urban/rural.
  Tier A.
- **Historical Statistics** — aggregate diffusion series for automobiles,
  telephones, radios, TVs. Tier C.
- **AHS** (1973→) — appliance ownership questions (varies by year). Tier A.
- **CPS/NTIA/Pew** — computer, internet, smartphone adoption. Tier A.

**Modern comparison (feasible):**

- Current prices from BLS CPI data, retail data, or Sears modern equivalent
- Current lifespan from AHAM/NAHB
- Current diffusion from CPS/Pew/AHS
- The comparison arithmetic (cost as % of income, then vs. now) is computed
  by code, not authored by hand — consistent with the nominal-values assumption

### Model impact

The current Fact model is "one claim, one source, one tier." An artifact is
a bundle of related claims (price, lifespan, diffusion, modern comparison)
that each need their own source. Two approaches:

**Option A: Artifact as a new entity (recommended)**

```python
@dataclass(frozen=True, slots=True)
class Artifact:
    id: str  # "us-1950s-suburban-refrigerator"
    name: str  # "Refrigerator"
    category: str  # "appliance" | "vehicle" | "communication" | "utility"
    facts: tuple[Fact, ...]  # price, lifespan, diffusion — each sourced
```

Each attribute of the artifact (price, lifespan, diffusion) is a Fact with
its own `source`, `tier`, and `population`. The artifact groups them. The
Room gains an `artifacts: tuple[Artifact, ...]` field. The renderer presents
artifacts as clickable objects.

**Option B: New panel + structured numerics (simpler, less clean)**

Add `Panel.ARTIFACTS` and use the planned structured-numeric fields to store
price/lifespan/diffusion. Facts are grouped by an `artifact_id` field.
This stays within the existing entity model but pushes more complexity into
the Fact dataclass.

**Recommendation:** Option A. It keeps the Fact model pure (one claim, one
source, one tier) while adding a composing entity that groups related facts
into a visitor-facing object. The structured-numerics extension to Fact
(mentioned in the fact model as "planned") supports both options; Option A
uses it without coupling artifact presentation to the Fact's display value.

**New Panel:** Not needed if Option A is used. The Artifact entity replaces
what would otherwise be a panel. The existing `DIFFUSION` panel continues
to hold aggregate diffusion facts ("% of families with a telephone"); the
Artifact entity holds item-level detail ("telephone: cost $X, lifespan Y
years, diffusion Z%, modern equivalent: $W, V years, U%").

**New assumption:** `artifact-pricing-source` — Sears catalog prices represent
mail-order retail, not local prices or actual transaction prices. They are
the best available proxy for what a median family would have paid.

### Visualization feasibility

The current plan (WI-3) specifies "schematic HTML/CSS" with "no external
assets (self-contained static output)." Interactive clickable objects require
JavaScript but do NOT require server-side state — the data is baked into the
static HTML at build time, and JavaScript handles the click → drawer
interaction client-side.

**Technical approach:**

1. The SVG room illustration contains clickable regions (one per artifact)
2. Each region has a `data-artifact-id` attribute
3. A small JavaScript module reads a JSON blob (embedded in the page at build
   time) mapping artifact IDs to their data
4. Clicking a region opens a drawer/modal (same pattern as the existing
   provenance drawer) showing the artifact's facts

**No external dependencies.** The JavaScript is vanilla, the data is baked
in, the output remains a self-contained static site. This is consistent with
the "deterministic static-site generator" design principle.

**Scope:** This is a rendering-layer feature, not a data-model change. Once
the Artifact entity exists in the data model and the data files are curated,
the renderer extension is straightforward. The hard part is curating the
artifact data (especially historical lifespans), not building the UI.

---

## Note: dwelling-size metric (rooms vs. square feet)

House/apartment size belongs in the existing `home` panel, not the artifact
model — but it carries a data floor worth stating before curation so a curator
doesn't reach for a number the record never held. The **durable cross-decade
size axis is number of rooms** (Census of Housing 1940→; IPUMS; the pre-1940
cost-of-living surveys recorded rooms too). **Square footage is late:** it
exists only for *new construction* from 1973 (Census SOC / Characteristics of
New Housing) and for existing stock from roughly 1985 (AHS unit square
footage). So rooms is the comparable metric across the whole span; sq ft is
shown only where the record has it, never back-filled. This is captured as the
`dwelling-size-metric` assumption in Plan 003 (WI-3). The affordability axis
from Plan 003 also applies here — median home value and rent become
hours-of-work-to-afford / years-of-income figures on the same consistent basis
as every other priced item.

---

## Phased rollout

### Phase 1 — Current plan (WI-1, WI-2, WI-3, WI-4)

Complete the US V0 with national-median rooms. The source survey (WI-1) is
done. Three rooms curated (WI-2). Renderer with provenance drawers (WI-3).
Gate hardened (WI-4). **No locale split, no artifact objects.**

### Phase 2 — Locale split

- Add `locale` field to Room entity
- Add `suburban-locale-definition` and updated `urban-rural-split` assumptions
- Curate locale rooms for 1950s first (strongest data: Census of Housing +
  IPUMS + P-60 for income; Sears for pricing; Historical Statistics for
  diffusion)
- Then expand to 1930s (Study of Consumer Purchases city/village/farm) and
  1940s (IPUMS metro computation)
- Pre-1930s: national rooms only, with gap statements for suburban/rural
- **Estimated effort:** Model change (small) + assumption updates (small) +
  curation of ~30 locale rooms (the bulk of the work — same transcribing-
  from-sources discipline as WI-2, ×3 locales per decade where data exists)

### Phase 3 — Artifact objects

- Add Artifact entity to the fact model (or structured numerics + artifact_id)
- Add `artifact-pricing-source` assumption
- Curate artifacts for high-impact items first:
  - 1950s: refrigerator, automobile, telephone, television, radio
  - 1920s: radio, automobile, telephone
  - 2020s: smartphone, computer, internet service, automobile
- Extend renderer with clickable SVG regions + artifact drawer
- **Estimated effort:** Model extension (medium) + curation (high — each
  artifact has 4+ facts with separate sources) + rendering extension (medium)

### Phase 4 — Interactivity polish

- Cross-decade comparison views (slider through decades, see how the same
  artifact changed)
- Cross-locale comparison (urban vs. rural side-by-side)
- These are rendering-layer features; the data model doesn't change

---

## Open questions

1. **P-60 metro/nonmetro income data:** Do individual P-60 reports (1947–1980s)
   include income by metro/nonmetro or inside/outside central city? Some do,
   some don't — which years have this breakdown? If inconsistent, IPUMS
   microdata (Tier B) is the reliable path.

2. **1935–36 Study of Consumer Purchases separate series:** FRASER lists an
   "Urban Series" volume. Are the Village and Farm series also on FRASER?
   The study covered "51 Cities, 140 Villages, and 66 Farm Counties" — are
   these three separate publications or one?

3. **Historical appliance lifespan data:** Is there any scholarly work
   estimating how long consumer durables lasted in past decades? (e.g.,
   "the average 1950 refrigerator lasted 18 years"). If not, the museum
   uses Tier D with a disclaimer, or omits the lifespan field for historical
   artifacts.

4. **Sears catalog coverage gaps:** Internet Archive has strong coverage for
   1890s–1910s but the search showed fewer catalogs for later decades.
   HathiTrust and Duke University may fill gaps. What's the actual coverage
   map by decade?

5. **National room disposition:** When locale rooms exist, does the national
   room remain (as a "see all locales" overview) or is it replaced by the
   three locale rooms? This affects room count and the lobby/index page.

6. **Suburban pre-1949:** Metropolitan statistical areas were introduced in
   1949. For the 1930s, "village" is the proxy for suburban. For the 1940s,
   IPUMS has a METRO variable but the 1940 census predates MSAs. How is
   "suburban" defined for 1930s–1940s? The `suburban-locale-definition`
   assumption must address this.
