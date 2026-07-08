# Resource Hunt — Sources to Track Down

Prioritized list of documents, data, and primary sources that would close
gaps or create new cross-decade comparison arcs. Items are sorted by impact.

## Priority 1 — Closes gaps / completes arcs

### 1. RECS 1993 Heating Fuel Breakdown

**Why:** Completes the heating fuel arc (1940→2024). Currently missing for
1990s — EIA restructured their website and the 1993 RECS data returns 503.
Only sourced figure: "more than 10% of homes heated with fuel oil" (from
RECS 2009 overview comparison).

**What I need:** Full breakdown — % of homes using natural gas, electricity,
fuel oil, propane, and other for main space heating, 1993 RECS.

**Where to look:**
- Wayback Machine: `https://web.archive.org/web/2010*/https://www.eia.doe.gov/emeu/recs/`
- FRASER: `https://fraser.stlouisfed.org/` — search "RECS 1993" or "Residential Energy Consumption Survey"
- EIA RECS 1993 page with a browser (may be JS-rendered): `https://www.eia.gov/consumption/residential/data/1993/`
- Printed report: DOE/EIA-0310/3 (Housing Characteristics 1993)

**Expected values** (for verification): Natural gas ~53-57%, electricity ~25-29%,
fuel oil ~10-12%, propane ~5%, other ~5%. These are inferred from the trend
between 1980 Census (gas 55%, electric 18%) and 2009 RECS (gas 49%, electric 34%).

---

### 2. 1950s Average New Car Price ($1,511) — Primary Source

**Why:** Last non-permanent Tier D gap. The $1,511 figure is widely cited
across multiple secondary sources but the primary document hasn't been
verified. Would upgrade from Tier D to Tier A.

**What I need:** Official average new car price for 1950, from a primary
government source.

**Where to look:**
- FRASER: `https://fraser.stlouisfed.org/` — search "BLS Bulletin 1097" or
  "Consumer Expenditure Survey 1950"
- Census Statistical Abstract 1953: `https://www2.census.gov/prod2/statcomp/`
  — look for the 1953 edition PDF, check "Motor vehicles" table
- NADA (National Automobile Dealers Association) historical data
- BLS Bulletin 1097 (1950 Consumer Expenditure Survey) — may have vehicle
  purchase price data

**Note:** Do NOT "correct" $1,511 to $2,200. The $2,200 figure is the 1959
price, not 1950. The $1,511 figure is consistent with era evidence (Henry J
budget car was $1,299 in 1950).

---

### 3. Cable TV Penetration — 2000s and 2010s

**Why:** Cable TV arc currently covers 1980s (53M households, 1989) and 1990s
(60%, 1992). Missing for 2000s and 2010s — the peak and cord-cutting decline.

**What I need:** % of US households with cable/satellite TV subscription,
circa 2005 and circa 2015.

**Where to look:**
- NCTA/Syndeo Institute: `https://syndeoinstitute.org/` — their Cable History
  Timeline PDF only covers up to 1997; check for updated versions
- FCC Annual Video Competition Reports: `https://www.fcc.gov/reports-research/`
  — search "video competition report" — these report pay-TV penetration
- Pew Research Center: `https://www.pewresearch.org/` — search "cable TV"
  or "cord cutting" — Pew has tracked pay-TV penetration
- Nielsen: `https://www.nielsen.com/` — may have historical penetration data

**Expected values:** ~65-70% peak (mid-2000s), declining to ~55-60% by 2015
as streaming (Netflix, Hulu) accelerated cord-cutting.

## Priority 2 — New cross-decade arcs

### 4. Historical Poverty Rates

**Why:** 2020s room has poverty rate (10.6%, 2024). Adding to other decades
would create a century-long poverty comparison. The official poverty measure
starts in 1959.

**What I need:** Official poverty rate (% of population below poverty
threshold) for: 1959/60, 1970, 1980, 1990, 2000, 2010.

**Where to look:**
- Census.gov: `https://www.census.gov/data/tables/time-series/demo/income-poverty/historical-poverty-people.html`
  — this page may be JS-rendered; try with a browser
- Census P-60 series: `https://www2.census.gov/programs-surveys/cps/tables/time-series/historical-poverty/`
  — directory listing, look for `pov` tables
- Census Historical Statistics: `https://www2.census.gov/programs-surveys/cps/tables/time-series/historical-income/`
  — related income/poverty tables
- FRED: `https://fred.stlouisfed.org/series/PPAAACUSA720A` — but may need API key
  for CSV download; the chart page shows the data visually

**Expected values:** 1959: ~22%, 1970: ~12.6%, 1980: ~13.0%, 1990: ~13.5%,
2000: ~11.3%, 2010: ~15.1% (Great Recession impact).

---

### 5. Vehicle Ownership — More Decades

**Why:** 2020s room has vehicle ownership (91.5% with at least one vehicle,
2023). Adding to other decades would show the shift to a car-dependent society.

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

### 6. Retail Food Prices — More Decades

**Why:** 1950s room has detailed retail food prices (bread 14.3¢/lb, milk
20.6¢/qt, etc. from BLS Bulletin 1055). 2020s room has December 2024 prices
(BLS API). Adding food prices to 1960s-2010s would show the cost of living
across the century in concrete terms.

**What I need:** Retail prices of common foods (bread, milk, eggs, beef,
flour, coffee, potatoes) for: 1960, 1970, 1980, 1990, 2000, 2010.

**Where to look:**
- BLS API: series IDs like APU0000712211 (bread), APU0000704111 (milk) —
  the API should return historical data; I can pull this if you find the
  correct series IDs and the API supports the years needed
- Census Statistical Abstract: `https://www2.census.gov/prod2/statcomp/`
  — various editions have "retail prices of foods" tables
- BLS historical publications at FRASER: `https://fraser.stlouisfed.org/`
  — search "retail prices food" for annual bulletins

**Note:** The BLS API series (APUxxxx) may have limited historical coverage.
The Census Statistical Abstract is the best bet for pre-1980 data.

## Priority 3 — Room enrichment

### 7. CEX Durable Goods Ownership — 1970s and 1980s

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

---

### 8. Week-of-Work Comparison — More Decades

**Why:** 1950s room has "what a week of work bought" ($53.29/week = 1.6% of
median family income). Adding this to other decades would show purchasing
power in concrete terms (how many loaves of bread, gallons of milk, etc.
a week of manufacturing work could buy).

**What I need:** Average weekly earnings (already have for most decades) +
retail food prices (see #6 above). The computation is mine — just need the
input data.

**Where to look:** Same as #6 (food prices) — this fact is a derivative of
the food price data.

## Priority 4 — Plan 005 future work items

### 9. Infant Mortality Rate

**Why:** Would add a health-improvement metric to the day panel, complementing
life expectancy.

**What I need:** Infant mortality rate (deaths per 1,000 live births) by
decade, 1900-2020.

**Where to look:**
- Historical Statistics Vol 1 (already OCR'd): check Series B 1-4 for
  infant mortality
- NCHS: `https://www.cdc.gov/nchs/nvss/mortality-tables.htm`
- Census Statistical Abstract: various editions

**Expected values:** 1900: ~100+, 1950: ~29.2, 2000: ~6.9, 2020: ~5.4.

---

### 10. Median Home Size (Square Footage)

**Why:** Would add a living-space metric to the home panel. Currently the
home panel tracks homeownership, home value, plumbing, and heating fuel but
not how much space families actually had.

**What I need:** Median square footage of new single-family homes (or all
homes) by decade. The 2020s room has "Median 1,500 sq ft" from AHS 2023.

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

### 11. Median Height and Weight

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
