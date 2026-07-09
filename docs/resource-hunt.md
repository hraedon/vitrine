# Resource Hunt — Sources to Track Down

Prioritized list of documents, data, and primary sources that would close
gaps or create new cross-decade comparison arcs. Items are sorted by impact.

## Closed (kept for reference)

- **RECS 1993 Heating Fuel** — `us-1990s-heating-fuel`; computed from RECS
  1993 microdata (file2_asc.txt, FUELHEAT, weighted with NWEIGHT).
- **1950s Average New Car Price** — `us-1950s-car-price`; upgraded from
  Tier D to Tier C. Primary source: Statistical Abstract 1953 Table 615
  (wholesale ~$1,295); $1,511 Ford Custom retail confirmed by multiple
  secondary sources.
- **Cable TV Penetration** — Facts in 1980s (NCTA, 50.5%), 1990s (FCC,
  59.3%), 2000s (FCC 13th Report, ~59%), 2010s (FCC, 53.2M declining).
- **Historical Poverty Rates** — Facts in 7 decades (1960s–2020s) from
  Census Historical Poverty Tables (API: histpov2). Official measure
  starts 1959; 1960s is the earliest possible decade.
- **Retail Food Prices** — Facts in 8 decades (1950s–2020s). 1950s from
  BLS Bulletin 1055; 1960s/1970s from Statistical Abstract; 1980s–2020s
  from BLS API (series APU0000702xxx).
- **Infant Mortality Rate** — Facts in 9 decades (1900s, 1950s–2020s)
  from CDC MMWR / NCHS / NVSS.
- **Vehicle Ownership** — Facts in 7 decades (1960s–2020s) from BTS
  Figure 2-7 (Census decennial 1960-2000 + ACS 2010-2023). 1960: 78.5% →
  1970: 82.5% → 1980: 87.1% → 1990: 88.5% → 2000: 89.7% → 2010: 90.9% →
  2023: 91.6%.
- **Week-of-Work Comparison** — Facts in 10 decades (1900s, 1940s–2020s).
  Derived from existing Tier A earnings and Census F-8 median family income
  facts. Arc: 92% (1940s) → 83% (1950s) → 95% (1960s) → 83% (1970s) → 60%
  (1980s) → 51% (1990s) → 49% (2000s) → 55% (2010s) → 60% (2020s). The
  single-earner era ended in the 1970s; the two-earner era began in the
  1980s. See verification-log WI-9.

## Priority 1 — Closes gaps / completes arcs

### 1. CEX Durable Goods Ownership — 1970s and 1980s

**Status:** Closed. Found appliance ownership data in the EIA Annual Energy
Review 1988 (Table 8.3), republished in the Census Bureau's USSR/USA
Statistical Abstract 1990. Covers 1978 and 1980 (RECS data). Added
`us-1970s-appliance-ownership` (1978) and `us-1980s-appliance-ownership`
(1980) as Tier A facts. Source: `eia-aer-appliances`.

## Priority 2 — Room enrichment

### 4. Median Home Size (Square Footage)

**Status:** Closed. Extract median square footage of new single-family homes
from the Census Bureau's C-25 annual reports (c25ann2003.pdf through
c25ann2017.pdf in vitrine-research). Data covers 1973-2017. Added facts for
1970s (1,525), 1980s (1,595), 1990s (1,905), 2000s (2,057), 2010s (2,169).
The 2020s room already had the AHS existing-stock figure (1,500 sq ft).
Source: `census-soc-new-housing`. Note: new construction ≠ existing stock.

---

### 5. Median Height and Weight

**Why:** Would add a physical well-being metric to the day panel, showing
how nutrition and health changed over the century.

**What I need:** Average/median height and weight of US adults by decade.

**Where to look:**
- NHANES (National Health and Nutrition Examination Survey): `https://www.cdc.gov/nchs/nhanes/`
  — modern data from 1960-present
- Anthropometric history: Historical Statistics Vol 1 (Series D 7-12) has
  height data for earlier periods
- CDC: `https://www.cdc.gov/nchs/data/series/sr_03/` — various reports
- Robert Fogel "The Escape from Hunger and Premature Death" — anthropometric
  history for the 19th and early 20th century

**Expected values:** Men's height increased ~2-3 inches over the century;
weight increased significantly in the late 20th century.

---

## Candidates from the 2026-07-09 completeness survey

Domains the corpus does not cover at all, ranked by effort. All "expected"
figures below are recalled orientation, never transcription material.

### 6. Median rent — the renter half of the housing story

**Why:** Homeownership facts show 35–55% of families rented for the first
half of the century — the museum prices the home the median family often
did NOT own, and prices nothing it rented. The biggest single coverage
hole. Priority 1.

**Where to look:** Census of Housing decennial median gross rent (1940→)
and contract rent (1930→) — same publication family as the home-value
facts already curated; ACS B25064 annual 2005→; BLS cost-of-living
surveys (1901, 1918-19) already in the source registry carry rent for
wage-earner families. Tier A throughout the census years.

### 7. Married women's labor force participation — who earns

**Why:** The week-of-work arc implies the single-earner era's end but the
corpus never states the direct fact. LFPR of married women is THE
composite-family story across the century. Priority 1.

**Where to look:** Historical Statistics Vol 1 (Series D 49–62,
decennial 1890→); BLS/CPS annual tables for the postwar era. Tier A.
**Expected shape (verify):** single digits ~1900 → majority by the 1980s.

### 8. Median age at first marriage — when the family forms

**Why:** Frames the four-person composite itself; also the 2020s room's
"the median household is no longer this family" caveat gets a number.
Cheapest addition on this list — one Census table covers 1890→present.

**Where to look:** Census Historical Marital Status Table MS-2. Tier A.

### 9. Educational attainment — the parents' schooling

**Why:** Nothing in the corpus touches education. Attainment of adults
25+ (median school years / % high-school graduates) is a one-table
Tier A arc 1940→present and changes how every room's family reads.

**Where to look:** Census Historical Educational Attainment Table A-1/A-2
(CPS, 1940→); pre-1940 only via IPUMS computation (Tier B, defer).

### 10. Healthcare — coverage and cost

**Why:** The defining budget transformation the expenditure shares only
hint at. Two candidate arcs: health-insurance coverage (% insured) and
per-capita national health expenditure.

**Where to look:** CMS National Health Expenditure Accounts historical
tables (1960→, annual, Tier A); NHIS/CPS coverage series (methodology
breaks across redesigns — needs a splice caveat). Moderate effort.

### 11. Mortgage debt — the financing half of affordability

**Why:** Home-as-income-years prices the house, not the loan. The share
of owner-occupied homes carrying a mortgage is a diffusion-style Tier A
fact back to 1890 ("encumbered homes" in early censuses); mortgage
rates (FHA series, then Freddie Mac PMMS 1971→) would enable a
payment-based metric later. Involved end of the list; the encumbrance
share alone is cheap.

### Known holes that likely stay honest gaps

- **Taxes:** the median family's effective tax rate went from ~0 to a
  major budget line, but official family-level series are scarce; most
  published series are think-tank computed (Tier D — excluded). CBO
  household tax tables (1979→) might support late decades only.
- **Childcare:** no official series before SIPP 1985. Late-century facts
  possible; earlier decades render the gap.
