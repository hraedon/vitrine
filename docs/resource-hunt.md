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
- **Week-of-Work Comparison** — Facts in 10 decades (1900s, 1940s–2020s).
  Derived from existing Tier A earnings and Census F-8 median family income
  facts. Arc: 92% (1940s) → 83% (1950s) → 95% (1960s) → 83% (1970s) → 60%
  (1980s) → 51% (1990s) → 49% (2000s) → 55% (2010s) → 60% (2020s). The
  single-earner era ended in the 1970s; the two-earner era began in the
  1980s. See verification-log WI-9.

## Priority 1 — Closes gaps / completes arcs

### 1. Vehicle Ownership — More Decades

**Why:** 2020s room has vehicle ownership (91.5% with at least one vehicle,
2023) and 1970s has it (80.1%, CEX 1972-73). Adding 1960s, 1980s, 1990s,
2000s, and 2010s would show the shift to a car-dependent society.

**What I need:** % of households with at least one vehicle, by decade.

**Where to look:**
- Census Historical Housing Tables: check `https://www2.census.gov/programs-surveys/decennial/tables/time-series/`
  for any vehicle-related tables (I checked coh-vehicles, coh-auto — both 404)
- Census 1990/2000 decennial: the 1990 and 2000 Census asked about vehicles
  available; data might be in `coh-ownerchar/` or a separate vehicle table
- Census Reporter API: try `https://api.censusreporter.org/1.0/data/show/acs2011_1yr?table_ids=B25045&geo_ids=01000US`
  (ACS 2011 1-year — adjust release name for different years)
- Census Statistical Abstract: `https://www2.census.gov/prod2/statcomp/`
  — check various editions for "vehicles available" tables

**Expected values:** 1960: ~70-75%, 1970: ~80%, 1980: ~85%, 1990: ~88%,
2000: ~90%. The 2020s room shows 91.5% (2023).

---

### 2. CEX Durable Goods Ownership — 1970s and 1980s

**Why:** 1960s room has detailed appliance ownership data (TV 91.4%,
refrigerator 84.7%, washing machine 70.0%, etc. from CEX 1960-61 p.15).
1970s and 1980s rooms lack this data. Would enrich the diffusion panel.

**What I need:** % of households/families with TV, refrigerator, washing
machine, AC, clothes dryer, dishwasher, etc. from CEX 1972-73 and CEX 1985.

**Where to look:**
- CEX 1972-73 Bulletin 1992: Already accessed via FRASER for expenditure
  data. Check later pages (likely p.15-20) for a "durable goods ownership"
  or "home equipment" table.
- CEX 1985 tables: Already accessed via Wayback Machine for expenditure
  data. Check for a separate durable goods table.

**FRASER URLs:**
- `https://fraser.stlouisfed.org/title/consumer-expenditure-survey-3643`
  — look for 1972-73 bulletin
- Wayback: `https://web.archive.org/web/2024/https://www.bls.gov/cex/1985/Standard/`
  — check for durable goods tables

## Priority 2 — Room enrichment

### 4. Median Home Size (Square Footage)

**Why:** Would add a living-space metric to the home panel. Currently the
home panel tracks homeownership, home value, plumbing, and heating fuel but
not how much space families actually had. The 2020s room has "Median 1,500
sq ft" from AHS 2023.

**What I need:** Median square footage of new single-family homes (or all
homes) by decade.

**Where to look:**
- Census Construction Reports: `https://www.census.gov/construction/chars/`
  — "Annual Characteristics of New Housing" — has median sq ft of new homes
  going back to 1973
- AHS (American Housing Survey): historical data on home size
- Historical Statistics Vol 2: check for room-count data (pre-1970)
- Census Historical Housing Tables: `coh-crowding/` might have persons-per-room

**Note:** New-construction size ≠ existing housing stock. The AHS measures
the entire stock; Census construction reports measure only new homes. Flag
the distinction in fact notes.

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
