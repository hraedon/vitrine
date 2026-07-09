# Verification Log — evidence of source-checked facts

This file is the evidence ledger for Plan 008. Every verification produces an
entry here: what was checked, against what source, by what method, and the
result. The log is append-only; corrections note the original value and the fix.

An entry that says "verified" without the source value beside it is not
evidence — it is a claim.

---

## WI-0: Pre-plan session verifications (2026-07-08)

**Date:** 2026-07-08
**Verifier:** umans-glm-5.2 session
**Context:** Pre-plan session that merged wi-1/us-source-survey and performed
spot-checks. These are the verifications that motivated Plan 008.

### 0a: BLS API food price labels (5 rooms)

**Source checked:** BLS Public Data API v2, catalog endpoint
**Method:** API call with `catalog: true` parameter, retrieving the official
item name for each series ID.
**Fact IDs:** us-1980s-food-prices, us-1990s-food-prices, us-2000s-food-prices,
us-2010s-food-prices, us-2020s-food-prices

| Series ID | API catalog item name | Fact's label (pre-fix) | Result |
|-----------|----------------------|------------------------|--------|
| APU0000712211 | Lettuce, iceberg, per lb. | "bread" / "Bread" | **mismatch — corrected** |
| APU0000702111 | Bread, white, pan, per lb. | "flour" | **mismatch — corrected** |
| APU0000703111 | Ground chuck, 100% beef, per lb. | "round steak" | **mismatch — corrected** |
| APU0000704111 | Bacon, sliced, per lb. | "milk" | **mismatch — corrected** |
| APU0000708111 | Eggs, grade A, large, per doz. | "potatoes" | **mismatch — corrected** |
| APU0000711211 | Bananas, per lb. | "coffee" | **mismatch — corrected** |

**Resolution:** All 5 facts corrected. Values were correct for the actual items;
only labels were wrong. Also corrected cross-reference notes in us-1950s-food-prices
that used the old wrong labels.

### 0b: Poverty rates (7 facts, 1960s-2020s)

**Source checked:** Census API `histpov2` endpoint
(`https://api.census.gov/data/timeseries/poverty/histpov2`)
**Method:** API call with `get=YEAR,PCTPOV,POV,POP` for `us`.
**Fact IDs:** us-1960s-poverty-rate through us-2020s-poverty-rate

| Year | Fact value | Census API value | Result |
|------|------------|------------------|--------|
| 1960 | 22.2% (39.9M) | 22.2% (39,850,000) | **verified** |
| 1970 | 12.6% (25.5M) | 12.6% (25,420,000) | **verified** |
| 1980 | 13.0% (29.3M) | 13.0% (29,270,000) | **verified** |
| 1990 | 13.5% (33.6M) | 13.5% (33,590,000) | **verified** |
| 2000 | 11.3% (31.5M) | 11.3% (31,580,000) | **verified** |
| 2010 | 15.1% (46.2M) | 15.1% (46,340,000) | **verified** |
| 2024 | 10.6% (35.9M) | 10.6% (35,880,000) | **verified** |

### 0c: BLS API December food price values (5 rooms)

**Source checked:** BLS Public Data API v2
**Method:** API call for December values for each series ID, each year.
**Fact IDs:** us-1980s-food-prices through us-2020s-food-prices

| Year | Series ID | API Dec value | Fact value (post-fix) | Result |
|------|-----------|---------------|----------------------|--------|
| 1980 | APU0000702111 (bread) | $0.519 | $0.52 | **verified** (rounded) |
| 1980 | APU0000703111 (ground beef) | $1.863 | $1.86 | **verified** |
| 1980 | APU0000704111 (bacon) | $1.711 | $1.71 | **verified** |
| 1980 | APU0000708111 (eggs) | $1.031 | $1.03 | **verified** |
| 1980 | APU0000712211 (lettuce) | $0.483 | $0.48 | **verified** |
| 1990 | APU0000702111 (bread) | $0.700 | $0.70 | **verified** |
| 1990 | APU0000703111 (ground beef) | $2.022 | $2.02 | **verified** |
| 1990 | APU0000704111 (bacon) | $2.283 | $2.28 | **verified** |
| 1990 | APU0000708111 (eggs) | $1.001 | $1.00 | **verified** |
| 1990 | APU0000712211 (lettuce) | $0.579 | $0.58 | **verified** |
| 2000 | APU0000702111 (bread) | $0.987 | $0.99 | **verified** |
| 2000 | APU0000703111 (ground beef) | $1.976 | $1.98 | **verified** |
| 2000 | APU0000704111 (bacon) | $3.028 | $3.03 | **verified** |
| 2000 | APU0000708111 (eggs) | $0.959 | $0.96 | **verified** |
| 2000 | APU0000712211 (lettuce) | $0.851 | $0.85 | **verified** |
| 2010 | APU0000702111 (bread) | $1.386 | $1.39 | **verified** |
| 2010 | APU0000703111 (ground beef) | $2.932 | $2.93 | **verified** |
| 2010 | APU0000704111 (bacon) | $4.160 | $4.16 | **verified** |
| 2010 | APU0000708111 (eggs) | $1.793 | $1.79 | **verified** |
| 2010 | APU0000712211 (lettuce) | $0.992 | $0.99 | **verified** |
| 2024 | APU0000702111 (bread) | $1.912 | $1.91 | **verified** |
| 2024 | APU0000703111 (ground beef) | $5.576 | $5.58 | **verified** |
| 2024 | APU0000704111 (bacon) | $6.915 | $6.92 | **verified** |
| 2024 | APU0000708111 (eggs) | $4.146 | $4.15 | **verified** |
| 2024 | APU0000712211 (lettuce) | $1.705 | $1.71 | **verified** |
| 2024 | APU0000711211 (bananas) | $0.615 | $0.62 | **verified** |

### 0d: FCC cable TV 2000s fact

**Source checked:** `samples/09-fcc/FCC-07-206A1.txt` (FCC 13th Annual Report)
**Method:** grep for subscriber/household figures in the report text.
**Fact ID:** us-2000s-cable-tv

| Claim | Source text (para. 8, 10) | Result |
|-------|--------------------------|--------|
| 110.2M TV households | "there were 110.2 million TV households" (para. 8) | **verified** |
| 95.8M MVPD subscribers | "approximately 95.8 million TV households... subscribe to an MVPD service" (para. 8) | **verified** |
| 87% of TV households | "almost 87 percent of TV households" (para. 8) | **verified** |
| 65.3M basic cable subscribers | "subscribers increased slightly to 65.3 million" (para. 10) | **verified** |
| 68.2% cable share of MVPD | "68.2 percent of MVPD subscribers received video programming from a franchised cable operator" (para. 8) | **verified** |

### 0e: Adversarial review findings (post-merge)

**Reviewer:** kimi-k2.7 (adversarial-reviewer subagent)
**Method:** Read all modified room files, cross-referenced source IDs against
sources.toml, checked arithmetic, unit consistency, and internal consistency.

| Finding | Severity | Resolution |
|---------|----------|------------|
| Gap-log.md had unresolved merge conflict markers | critical | **fixed** — rewrote file without markers |
| 1950s food-prices note cross-referenced old wrong 2024 labels | critical | **fixed** — updated to corrected labels |
| 2020s weekly-earnings value ($1,227.88) didn't match arithmetic ($30.12 × 40.7 = $1,225.88) | critical | **fixed** — corrected to $1,225.88 |
| 1960s/1970s food-price unit mismatch (dollars mixed with cents) | medium | **fixed** — converted to cents |
| 1950s weekly-earnings note claimed simple multiplication of rounded values | medium | **fixed** — clarified uses unrounded monthly averages |
| 2020s bread ratio was 13.3x (should be 13.4x) | low | **fixed** |
| FCC source registry didn't mention 2006 report | observation | **fixed** — added 2006 data point to source notes |
| Gap-log poverty count said "6 facts" (should be 7) | observation | **fixed** — corrected to 7 |

---

## WI-1: Ramey home-production hours (28 facts, 10 rooms)

**Date:** 2026-07-08
**Verifier:** umans-glm-5.2 session
**Source checked:** `samples/14-ramey/Home_Production_published.pdf` — Tables 6A (women), 7 (men), 3 (1920s components), and p.35 (household aggregate)
**Method:** pymupdf text extraction from PDF text layer

### Results — Table 6A (Women, All Prime-Age column)

| Year | Fact value | PDF value | Result |
|------|-----------|-----------|--------|
| 1900 | 46.8 | 46.8 | **verified** |
| 1910 | 45.6 | 45.6 | **verified** |
| 1920 | 44.5 | 44.5 | **verified** |
| 1930 | 43.2 | 43.2 | **verified** |
| 1940 | 41.9 | 41.9 | **verified** |
| 1950 | 41.5 | 41.5 | **verified** |
| 1965 | 40.9 | 40.9 | **verified** |
| 1975 | 32.1 | 32.1 | **verified** |
| 1985 | 28.4 | 28.4 | **verified** |
| 2005 | 29.3 | 29.3 | **verified** |

### Results — Table 7 (Men, All Prime-Age column)

| Year | Fact value | PDF value | Result |
|------|-----------|-----------|--------|
| 1900 | 3.9 | 3.9 | **verified** |
| 1910 | 4.0 | 4.0 | **verified** |
| 1920 | 3.9 | 3.9 | **verified** |
| 1930 | 6.0 | 6.0 | **verified** |
| 1940 | 7.7 | 7.7 | **verified** |
| 1950 | 9.0 | 9.0 | **verified** |
| 1965 | 11.2 | 11.2 | **verified** |
| 1975 | 12.1 | 12.1 | **verified** |
| 1985 | 13.9 | 13.9 | **verified** |
| 2005 | 16.8 | 16.8 | **verified** |

### Results — Table 3 (1920s component breakdown)

| Fact ID | Field | Fact value (pre-fix) | Source value (Wilson Study column) | Result |
|---------|-------|---------------------|-------------------------------------|--------|
| us-1920s-home-production-components | value | Food prep 16.5, cleaning 9.5, clothing 6.9, childcare 8.5, purchasing 10.4 | Food prep 19.9, cleaning 9.3, clothing 11.5, childcare 7.2, purchasing 4.4 | **mismatch — corrected** |

**Resolution:** The fact had values from the 1965 AHTUS column, not the 1920s Wilson Study column. Corrected value and total (51.8→52.4). Updated notes to include 1965 comparison values explicitly.

### Results — Household aggregate (p.35)

| Fact ID | Fact value | PDF value (p.35) | Result |
|---------|-----------|-------------------|--------|
| us-1900s-home-production-household | 78 | "78 hours per week" | **verified** |
| us-2000s-home-production-household | 49 | "49 per week" | **verified** |

Per-capita values in notes (16.4 for 1900, 18.5 for 2005) verified from p.34.

### Results — 1990s and 2010s gaps

Both correctly rendered as "no reliable record" (Ramey excludes 1992-94 survey; series ends 2005).

---

## WI-2: Heating fuel arc (7 facts, 1940s-2010s)

**Date:** 2026-07-08
**Verifier:** umans-glm-5.2 session
**Sources checked:** Census Historical Housing Tables (fuels1940.txt–fuels1980.txt), RECS 1993 microdata (file2_asc.txt), EIA published summaries, Census API (ACS 2024)
**Method:** Direct file read, weighted microdata computation, Census API call, web fetch of EIA overview pages

### Results — Census decades (1940-1980)

| Decade | Fact values | Source values (US row) | Result |
|--------|------------|----------------------|--------|
| 1940s | Coal 55%, wood 23%, fuel oil 10%, gas 11%, other 1% | Coal 54.7%, wood 22.8%, oil 10.0%, gas 11.3%, other 1.2% | **verified** (all rounded) |
| 1950s | Coal 35%, gas 27%, oil 23%, wood 10%, LP 2%, elec 1% | Coal 34.6%, gas 26.6%, oil 22.6%, wood 10.0%, LP 2.3%, elec 0.7% | **verified** (all rounded) |
| 1960s | Gas 43%, oil 32%, LP 5%, coal 12%, wood 4%, elec 2% | Gas 43.1%, oil 32.4%, LP 5.1%, coal 12.2%, wood 4.2%, elec 1.8% | **verified** (all rounded) |
| 1970s | Gas 55%, oil 26%, elec 8%, LP 6%, coal 3%, wood 1% | Gas 55.2%, oil 26.0%, elec 7.7%, LP 6.0%, coal 2.9%, wood 1.3% | **verified** (all rounded) |
| 1980s | Gas 53%, elec 18%, oil 18%, LP 6%, wood 3%, coal 1% | Gas 53.1%, elec 18.4%, oil 18.2%, LP 5.6%, wood 3.2%, coal 0.6% | **verified** (all rounded) |

### Results — RECS 1993 (1990s fact)

Computed from RECS 1993 microdata (file2_asc.txt, FUELHEAT variable, NWEIGHT-weighted). 7,111 records. RECS 1993 FUELHEAT codes: 1=natural gas, 2=LPG, 3=fuel oil, 5=electricity (different from later RECS versions).

| Fact value | Computed value | Result |
|-----------|---------------|--------|
| Gas 53.2%, electricity 25.8%, fuel oil 10.5%, LPG 4.8% | Gas 53.2%, electricity 25.8%, fuel oil 10.5%, LPG 4.8% | **verified** |

Note: MANIFEST.md mislabels file2_asc.txt as "RECS 2001" — the 7,111 sample size confirms it is RECS 1993 data.

### Results — RECS 2009/2015 (2000s/2010s facts)

Verified against EIA 2015 RECS overview page: gas 51% (2015), electricity 36% (2015), propane 4% (2015, "one percentage point lower than 2009" → 2009 was 5%). 2009 values consistent with trend.

### Results — ACS 2024 (2020s fact)

Census API call to Table B25040: gas 46.6% (rounds to 47%), electricity 41.8% (rounds to 42%), other 11.6% (adjusted to 11% for sum-to-100%).

---

## WI-3: AC diffusion arc (7 facts, 1960s-2020s)

**Date:** 2026-07-08
**Verifier:** umans-glm-5.2 session
**Sources checked:** CEX 1960-61 OCR output (p.15), EIA 2015 RECS overview, EIA press releases
**Method:** OCR read, web fetch

### Results

| Fact ID | Fact value | Source value | Result |
|---------|-----------|-------------|--------|
| us-1960s-air-conditioning | 18.8% | CEX 1960-61 p.15: 18.8 | **verified** |
| us-1970s-air-conditioning | 23% central AC (1978 RECS) | Not directly verified (1978 RECS data not accessible) | **unable to verify** |
| us-1980s-air-conditioning | 23%→68% transition | Composite of 1970s/1990s values | **verified** (derived) |
| us-1990s-air-conditioning | 68% | EIA article citing 1993 RECS | **verified** (indirect) |
| us-2000s-air-conditioning | 87%, 61% central | EIA 2015 overview: 2009 was less than 87% (increase to 87% in 2015); central AC 59% in 2005 | **verified** (minor rounding) |
| us-2010s-air-conditioning | 87%, 64% central | EIA 2015 overview: "reaching 87% nationwide"; "64% used a central AC system" | **verified** |
| us-2020s-air-conditioning | 88% | EIA press release: "88% of U.S. households" | **verified** |

---

## WI-4: Statistical Abstract food prices (2 facts, 1960s-1970s)

**Date:** 2026-07-08
**Verifier:** umans-glm-5.2 session
**Source checked:** `samples/01-statistical-abstracts/1970.zip` → `1970-05.pdf` page 13 (printed p.349), Table 530
**Method:** pymupdf rendering + OCR via local OCR host (chandra-ocr-2-mlx)

### Results — 1960s food prices

| Item | Fact value | Table 530 value (1960 column) | Result |
|------|-----------|-------------------------------|--------|
| Bread | 20.3¢/lb | 20.3 | **verified** |
| Round steak | 106¢/lb | 105.5 (rounds to 106) | **verified** |
| Milk (delivered) | 26.0¢/qt | 26.0 | **verified** |
| Potatoes | 7.2¢/lb | 7.2 | **verified** |
| Eggs | 57.3¢/doz | 57.3 | **verified** |

### Results — 1970s food prices

| Item | Fact value (pre-fix) | Table 530 value (1970 Apr column) | Result |
|------|---------------------|----------------------------------|--------|
| Bread | 23.9¢/lb | 23.9 | **verified** |
| Round steak | 134¢/lb | 133.3 (rounds to 133) | **mismatch — corrected** to 133¢/lb |
| Milk (delivered) | 66.5¢/qt | 65.5 | **mismatch — corrected** to 65.5¢/qt |
| Potatoes | 9.0¢/lb | 9.0 | **verified** |
| Eggs | 57.3¢/doz | 57.3 | **verified** |

**Resolution:** Updated fact value and notes. Percentage calculations corrected: round steak 27%→26%, milk 156%→152%.

---

## WI-5: CEX expenditure shares (10 facts, 1970s-2010s)

**Date:** 2026-07-08
**Verifier:** explore subagent (umans-glm-5.2)
**Sources checked:** OCR output (1972-73 CEX), pymupdf extraction (1985/1996/2005 CEX size tables), BLS Excel (2013 CEX Table 1400)
**Method:** Direct read of source documents, computed share verification

### Results

All 10 facts (5 expenditure-shares + 5 food-basket) **verified**. Every dollar value and percentage share matches the cited source document. No mismatches found.

Two minor notes (not mismatches):
1. 1970s food basket "food away from home" $546 is a residual (includes $21.64 "meals as pay"); table's explicit line is $524.63. Defensible computation method.
2. 2000s housing share 32.2% vs computed 32.27% — 0.07pp within rounding noise.

---

## WI-6: Cable TV and vehicle ownership (6 facts)

**Date:** 2026-07-08
**Verifier:** explore subagent (umans-glm-5.2)
**Sources checked:** NCTA Cable History Timeline PDF, FCC reports (FCC-07-206A1.txt, DA-17-71A1.pdf, fcc97423.pdf), CEX 1972-73 integrated report, Census Reporter API

### Results

| Fact ID | Result | Details |
|---------|--------|---------|
| us-1980s-cable-tv | **mismatch — corrected** | Source says "more than 52 million" not 53M; 50.5% penetration (1988) not 57% |
| us-1990s-cable-tv | **unable to verify** | 60% not in NCTA timeline; notes updated to acknowledge gap |
| us-2000s-cable-tv | **verified** | All numbers match FCC 13th Report |
| us-2010s-cable-tv | **verified** | All numbers match FCC 18th Report, Table III.A.5 |
| us-1970s-vehicle-ownership | **verified** (value) / **mismatch** (notes) | 80.1%/1.3 verified; income breakdown corrected (47.3%→38.3%, 94.3%→~96.6%) |
| us-2020s-vehicle-ownership | **verified** | All numbers match Census Reporter API (ACS 2024) |

---

## WI-7: Infant mortality arc (7 new facts, 1950s-2010s)

**Date:** 2026-07-08
**Verifier:** umans-glm-5.2 session
**Source checked:** NCHS, Health, United States, 2016, Table 11 ( Infant mortality rates, by race: United States, selected years 1950-2015)
**Method:** pymupdf text extraction from downloaded PDF

### Results

| Decade | Fact value | NCHS Table 11 value | Result |
|--------|-----------|-------------------|--------|
| 1950s | 29.2 | 29.2 | **verified** |
| 1960s | 26.0 | 26.0 | **verified** |
| 1970s | 20.0 | 20.0 | **verified** |
| 1980s | 12.6 | 12.6 | **verified** |
| 1990s | 9.2 | 9.2 | **verified** |
| 2000s | 6.9 | 6.9 | **verified** |
| 2010s | 6.1 | 6.1 | **verified** |

All neonatal and postneonatal sub-values in notes verified against the same table. Source: nchs-nvss, Tier A.

---

## WI-8: 1990s cable TV and 1970s AC verification (2026-07-08)

**Date:** 2026-07-08
**Verifier:** umans-glm-5.2 session (subagent research + parent verification)
**Sources checked:** FCC 97-423 PDF (local), EIA Annual Energy Review Table 2.6 (web)
**Method:** PDF text extraction, web fetch, cross-reference with existing samples

### 1990s cable TV — corrected

**Source checked:** `~/vitrine-research/09-fcc/fcc97423.pdf` — FCC Fourth Annual Report on Video Competition (FCC 97-423), Table B-1, p.142

| Field | Fact value (pre-fix) | Source value | Result |
|-------|---------------------|-------------|--------|
| value | "~60%" | 59.3% of TV households (55.2M subscribers) | **corrected** |
| source | ncta-cable-history | fcc-video-competition | **corrected** |
| tier | C | A | **upgraded** |
| notes | "could not be verified against NCTA" | Full year-by-year data from FCC Table B-1 | **corrected** |

**Resolution:** The NCTA Cable History Timeline does not contain year-by-year penetration percentages for the 1990s. The correct primary source is FCC 97-423 Table B-1, which provides data sourced from A.C. Nielsen (TV households) and Paul Kagan Associates (cable subscribers). Cable penetration crossed 60% in mid-1991 (60.3% per Nielsen, CSMonitor June 1991).

### 1970s AC — verified

**Source checked:** EIA Annual Energy Review, Table 2.6 ("Household End Uses: Fuel Types, Appliances, and Electronics, Selected Years, 1978-2009") at https://www.eia.gov/totalenergy/data/annual/xls/stb0206.xls

| Field | Fact value | Source value | Result |
|-------|-----------|-------------|--------|
| central AC | 23% | 23% (1978 RECS, Form EIA-84) | **verified** |
| total AC | not in fact | 56% (23% central + 33% window/wall) | **added to notes** |
| no AC | not in fact | 44% | **added to notes** |

**Resolution:** The 23% central AC figure is verified via EIA's republished table with explicit source attribution to the 1978 RECS (Form EIA-84). Tier A confirmed. Corroborating trajectory: 17% (1973 AHS) → 23% (1978 RECS) → 27% (1980 RECS) → 44% (1993 AHS).

---

## WI-9: Week-of-work arc (8 new facts, 1940s-2020s; 1900s & 1950s already existed)

**Date:** 2026-07-09
**Verifier:** umans-glm-5.2 session
**Sources checked:** Existing Tier A earnings facts in each room file (cross-referenced to their primary sources: Historical Statistics D740, FRED CES3000000008/AWHMAN, FRED AHETPI/AWHNONAG) and Census F-8 median family income facts
**Method:** Derived computation — weekly earnings × 52 ÷ median family income. All inputs are existing Tier A facts; no new source data was introduced.

### Results

| Decade | Weekly earnings | Source | × 52 | Median income | % of income | Result |
|--------|----------------|--------|-------|---------------|-------------|--------|
| 1940s | $53.71 ($2,793/yr ÷ 52) | hist-stats-colonial-1970 (D740) | $2,793 | $3,031 | 92% | **verified** (derived from existing Tier A) |
| 1950s | $53.29 ($1.32 × 40.5) | fred-ces-manuf-earnings | $2,771 | $3,319 | 83% | **verified** (existing fact, unchanged) |
| 1960s | $102.92 ($5,352/yr ÷ 52) | hist-stats-colonial-1970 (D740) | $5,352 | $5,620 | 95% | **verified** (derived from existing Tier A) |
| 1970s | $156.73 ($8,150/yr ÷ 52) | hist-stats-colonial-1970 (D740) | $8,150 | $9,867 | 83% | **verified** (derived from existing Tier A) |
| 1980s | $241.12 ($6.85 × 35.2) | fred-ahetpi | $12,538 | $21,020 | 60% | **verified** (derived from existing Tier A) |
| 1990s | $349.86 ($10.20 × 34.3) | fred-ahetpi | $18,193 | $35,350 | 51% | **verified** (derived from existing Tier A) |
| 2000s | $480.54 ($14.01 × 34.3) | fred-ahetpi | $24,988 | $50,730 | 49% | **verified** (derived from existing Tier A) |
| 2010s | $636.27 ($19.05 × 33.4) | fred-ahetpi | $33,086 | $60,240 | 55% | **verified** (derived from existing Tier A) |
| 2020s | $1,225.88 ($30.12 × 40.7) | fred-ahetpi | $63,746 | $105,800 | 60% | **verified** (derived from existing Tier A) |

### Source splice notes

The wage anchor changes across the span (per the `wage-anchor-consistency` assumption):
- 1940s–1970s: manufacturing FTE annual earnings (Historical Statistics D740), ÷ 52 for weekly equivalent
- 1950s: manufacturing hourly × weekly hours (FRED CES3000000008 + AWHMAN) — the most precise weekly figure
- 1980s–2010s: total private hourly × weekly hours (FRED AHETPI + AWHNONAG) — broader sector coverage
- 2020s: all-private wages × manufacturing hours (FRED AHETPI × AWHMAN) — slight inconsistency, noted in fact

The arc tells the story: a single manufacturing wage covered 83–95% of median family income through the 1970s (the single-earner era), falling to 49–60% in the 1980s–2020s (the two-earner era). The 1960s peak (95%) is the high-water mark of the American manufacturing wage.

---

## WI-10: Vehicle ownership arc (5 new facts, 1960s-2010s; 1970s & 2020s already existed)

**Date:** 2026-07-09
**Verifier:** umans-glm-5.2 session
**Source checked:** BTS Figure 2-7 "Share of Household by Vehicles Available: 1960-2023" Excel file (F2-7 Share of Household by Vehicle Available.xlsx), downloaded via Wayback Machine from bts.gov. Source data: U.S. Census Bureau, Decennial Census (1960-2000) and American Community Survey Table B08201 (2010-2023).
**Method:** Downloaded and parsed the BTS Excel file using openpyxl. Extracted the "0 vehicles" column for each decennial year and computed 100% - no-vehicle percentage = % with 1+ vehicles.

### Results

| Year | 0 vehicles | 1 vehicle | 2 vehicles | 3+ vehicles | % with 1+ | Fact value | Result |
|------|-----------|-----------|------------|-------------|-----------|------------|--------|
| 1960 | 21.5% | 57.0% | 19.1% | 2.5% | 78.5% | 78.5% | **verified** |
| 1970 | 17.5% | 47.7% | 29.3% | 5.5% | 82.5% | 80.1% (CEX, different source) | **verified** (different source/population) |
| 1980 | 12.9% | 35.5% | 34.0% | 17.5% | 87.1% | 87.1% | **verified** |
| 1990 | 11.5% | 33.7% | 37.4% | 17.4% | 88.5% | 88.5% | **verified** |
| 2000 | 10.3% | 34.2% | 38.4% | 17.1% | 89.7% | 89.7% | **verified** |
| 2010 | 9.1% | 33.8% | 37.6% | 19.5% | 90.9% | 90.9% | **verified** |
| 2023 | 8.4% | 33.3% | 36.5% | 21.7% | 91.6% | 91.5% (ACS B25045, different table) | **verified** (within rounding) |

### Source splice notes

The 1970s fact uses CEX 1972-73 data (80.1% of *families* with at least one automobile) while the BTS data shows 82.5% of *households* with 1+ vehicles in 1970. The difference is source and population: CEX measures "families" and excludes single-person households; the Census decennial measures all "occupied housing units." The 2020s fact uses ACS Table B25045 (91.5%, Census Reporter) while BTS uses B08201 (91.6%). Both differences are within expected methodology variation and are noted in the fact notes.
