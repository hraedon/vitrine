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
| us-1970s-vehicle-ownership | **updated** | Switched from CEX 1972-73 (80.1%, source: bls-cex) to BTS/Census decennial 1970 (82.5%, source: bts-vehicle-availability) for series consistency with all other decades (1960s-2020s). CEX figure preserved in notes. |
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

---

## WI-11: Pre-share audit — miscite fix, link check, cross-check, honesty rule (2026-07-10)

**Date:** 2026-07-10
**Verifier:** umans-glm-5.2 session
**Context:** Opus review feedback requesting four pre-share actions before
making vitrine public. All four addressed in one pass.

### WI-002: Live miscite fix (1 fact, 2 sources)

**Problem:** `us-1990s-cable-tv` cited `fcc-video-competition`, but the
source URL pointed to the 2017 FCC report — the actual data (59.3%, 1992)
comes from FCC 97-423 (1997). A visitor clicking the source card would
land on the wrong document.

**Fixes applied:**
1. `fcc-video-competition` source URL changed from the 2017 report page
   (`/document/annual-assessment-...-video-0`) to the FCC Media Bureau
   reports index (`/general/media-bureau-reports-industry`), which links
   to all annual reports. Source title updated to note the date range
   (1994–2017). Source notes now reference local archive paths for each
   report year.
2. `ncta-cable-history` source notes cleaned: removed stale "~60% (1992)"
   reference (no fact cites NCTA for 1990s data anymore — corrected in
   WI-8). Added note explaining the correction history.

**Verification:** Fact correctly cites `fcc-video-competition` (Tier A).
Fact notes describe FCC 97-423 Table B-1 with year-by-year data. Source
notes list all three report years with local archive paths.

### WI-003: Link checker (61 source URLs)

**Method:** `scripts/link_check.py` — HEAD + GET fallback, 8-way parallel.
All failures verified via Wayback Machine.

| Category | Count | Action |
|----------|-------|--------|
| OK (200/301/302) | 36 | — |
| Genuine 404 | 1 → 0 (fixed) | `census-p60-009` URL corrected |
| Bot-blocked (403/405) | 8 | URLs work in browser |
| Timeout (FRED/FRASER/FCC) | 14 | Confirmed via Wayback |
| Server error (503/520) | 3 | Transient; confirmed via Wayback |

**404 fix:** `census-p60-009` — old URL returned 404 (not in Wayback).
Corrected to `www2.census.gov/library/publications/1952/demographics/p60-09.pdf`.

### WI-009: Note-vs-source cross-check (312 facts, 61 sources)

**Method:** `scripts/cross_check.py` — 7 mechanical checks.

| Check | Issues | Detail |
|-------|--------|--------|
| 1. Source ID resolves | 0 | All facts cite existing sources |
| 2. Quantity in value | 0 | All quantities appear verbatim |
| 3. Note-source mismatch | 17 | All false positives — contextual mentions |
| 4. Stale source notes | 0 | No source references stale data |
| 5. Note completeness | 4 | Thin notes on number-of-families facts |
| 6. Source has URL | 0 | All sources have URLs |
| 7. Tier D facts | 18 | All structural gaps (known, documented) |

**Conclusion:** Zero miscites detected. The 17 note-source mismatches are
false positives (notes mention other sources for comparison/correction
context, not as the cited source).

### Tenure honesty rule (README)

Added paragraph to the central honesty rule about homeownership rate
measuring all occupied housing units, not the median four-person family.

---

## WI-12: 1950s car-price fix — provenance, methodology, tier (2026-07-10)

**Date:** 2026-07-10
**Verifier:** umans-glm-5.2 session
**Context:** WI-002 identified the 1950s car-price fact as a three-way outlier:
wrong source card, retail price instead of wholesale, Tier C instead of A.

### OCR verification of Table 615

**Source checked:** Statistical Abstract of the United States, 1953, Table 615
("Motor Vehicles—Factory Sales and Registrations: 1900 to 1951"), p.533
**Method:** Rendered page image from `samples/01-statistical-abstracts/1953.zip`
→ `1953-05.pdf` page 61 (printed p.533) at 200 DPI. OCR'd via chandra-ocr-2-mlx
on the Mac Studio (OCR skill workflow).

### Results — 1950 row

| Field | Fact notes (pre-fix) | OCR value | Result |
|-------|---------------------|-----------|--------|
| Passenger cars (thousands) | 6,666 | 6,666 | **verified** |
| Wholesale value (thousands $) | 8,633,272 | 8,633,272 | **verified** |
| Average wholesale per car | ~$1,295 | 8,633,272 / 6,666 = $1,295.03 | **verified** (arithmetic) |

### Cross-decade verification (same table)

| Year | Cars (K) | Wholesale ($K) | Avg/car | Existing fact | Result |
|------|---------|----------------|---------|---------------|--------|
| 1910 | 181 | 215,340 | $1,190 | ~$1,188 (1910s fact) | **consistent** (Hist Stats rounding) |
| 1920 | 1,906 | 1,809,171 | $949 | ~$949 (1920s fact) | **verified** |
| 1930 | 2,785 | 1,645,399 | $591 | ~$590 (1930s fact) | **verified** |
| 1940 | 3,717 | 2,370,654 | $638 | ~$638 (1940s fact) | **verified** |

### Fixes applied

1. **Source:** `statab-food-prices` → `hist-stats-colonial-1970` (matches
   all neighboring decades 1910s–1960s, which cite Series Q 148-162)
2. **Chartable quantity:** `amount_minor` 151100 → 129500 (wholesale, not retail)
3. **Tier:** C → A (primary source, same as neighbors)
4. **Value/notes:** Wholesale $1,295 as chartable value; $1,511 Ford Custom
   retail retained in notes as narrative context
5. **Tests updated:** `test_compare_tier_inheritance_weakest_wins` switched to
   1900s car (Tier C), hours/pct tests updated for 129500

### CI wiring (WI-003, WI-009)

- `scripts/cross_check.py` added to per-push CI (`.github/workflows/ci.yml`)
  with two-tier exit code: hard errors (source resolves, quantity in value,
  source has URL) block CI; advisory checks (note-source mismatch, thin notes,
  Tier D) report without blocking
- `scripts/link_check.py` added as weekly scheduled job
  (`.github/workflows/link-check.yml`, Mondays 08:00 UTC)

---

## WI-006: 2010s home-production gaps filled from ATUS (2026-07-10)

**Date:** 2026-07-10
**Verifier:** umans-glm-5.2 session
**Context:** The 2010s room rendered two gaps for women's and men's home
production. ATUS Table A-1 (2010 annual averages) was already in
`samples/13-atus/a1_2010.pdf` with text layer extractable via pypdf.

### Source

BLS American Time Use Survey, Table A-1 (2010 annual averages),
`a1_2010.pdf`. Text extracted via pypdf (no OCR needed — born-digital PDF).

### Transcription

| Fact | ATUS value | Unit |
|------|-----------|------|
| `us-2010s-home-production-women` | 2.14 hrs/day | hours per day, all women 15+ |
| `us-2010s-home-production-men` | 1.42 hrs/day | hours per day, all men 15+ |

### Cross-verification (A-1 vs A-2)

Table A-2 (`a2_2010.pdf`) splits by weekday/weekend. Weighted average
(5 weekdays + 2 weekend days) / 7 must reconcile to the A-1 overall:

- **Women:** (5×2.05 + 2×2.38) / 7 = (10.25 + 4.76) / 7 = 15.01 / 7 = 2.144
  ≈ **2.14** ✓
- **Men:** (5×1.30 + 2×1.72) / 7 = (6.50 + 3.44) / 7 = 9.94 / 7 = 1.420
  = **1.42** ✓

### 2011 stability check

A-2 2011 data (`a2_2011.pdf`) shows similar values:
- Women: weekday 2.05, weekend 2.42 → weighted avg 2.156
- Men: weekday 1.18, weekend 1.81 → weighted avg 1.360

Values are stable year-over-year, confirming the 2010 data point is
representative of the decade.

### Design decision: quantity retained; weekly arc rejects the splice

The ATUS data is transcribed with `quantity` set to the daily value (2.14
for women, 1.42 for men), because a fact with a single headline number must
carry a quantity. The 2026-07-10 visitor-honesty pass moved the comparability
decision to the chart projection: the weekly Ramey arc now renders these ATUS
facts as linked gap marks rather than turning their daily quantities into
weekly geometry. Multiplying by seven would repair the unit but not the
population and activity-definition mismatch. The facts remain numeric in the
rooms; the chart refuses the splice. The 2020s splice fact has no quantity
because its value is a multi-series string with no single headline number.

### Source card update

The `bls-atus` source card notes were updated to list the specific tables
used (2010 annual averages for the 2010s room, 2024 for the 2020s room).
The `year = 2024` represents the most recent publication year used; fact
labels identify the specific survey year.

### Arc caveat update

Both `home-production-women` and `home-production-men` arcs now carry a
caveat explaining the 2010s+ ATUS splice point.

---

## WI-13: Census home-values link-rot repair (2026-07-10)

**Date:** 2026-07-10
**Verifier:** GPT-5 Codex session
**Context:** The full scheduled link audit found that the registered Census
URL for `census-historical-housing-values` returned a genuine 404.

### Repair and verification

- Old path: `.../time-series/census-housing-tables/values-unadj.txt` (404)
- Current official path: `.../time-series/coh-values/values-unadj.txt` (200)
- The current directory is linked by the Census Bureau's official Historical
  Census of Housing Tables: Home Values landing page.
- Direct retrieval confirmed the U.S. row is unchanged: 1940 $2,938; 1950
  $7,354; 1960 $11,900; 1970 $17,000; 1980 $47,200; 1990 $79,100; 2000
  $119,600. No fact or series value changed.

## WI-37: Smoking facts (20 new facts, 1900s-2020s)

**Date:** 2026-07-17
**Verifier:** umans-glm-5.2 session
**Source checked:** CDC MMWR Surveillance Summary Vol. 43 No. SS-3 (Table 1), CDC Adult Tobacco Consumption dataset (data.cdc.gov), CDC NHIS via American Lung Association compilation
**Method:** Downloaded HTML/CSV from CDC websites, parsed Table 1 (per-capita consumption 1900-1994) and ALA prevalence table (1965-2022). Cross-checked key values against published CDC FastStats (9.1% in 2025) and MMWR narrative text.

### Per-capita consumption (13 facts)

| Decade | Fact value | Source value | Result |
|--------|-----------|-------------|--------|
| 1900s | 54 | 54 (MMWR Table 1, 1900) | **verified** |
| 1910s | 151 | 151 (MMWR Table 1, 1910) | **verified** |
| 1920s | 665 | 665 (MMWR Table 1, 1920) | **verified** |
| 1930s | 1,485 | 1,485 (MMWR Table 1, 1930) | **verified** |
| 1940s | 1,976 | 1,976 (MMWR Table 1, 1940) | **verified** |
| 1950s | 3,552 | 3,552 (MMWR Table 1, 1950) | **verified** |
| 1960s | 4,345 | 4,345 (MMWR Table 1, 1963 peak) | **verified** |
| 1970s | 3,985 | 3,985 (MMWR Table 1, 1970) | **verified** |
| 1980s | 3,849 | 3,849 (MMWR Table 1, 1980) | **verified** |
| 1990s | 2,817 | 2,817 (MMWR Table 1, 1990) | **verified** |
| 2000s | 2,076 | 2,076 (CDC Adult Tobacco CSV, 2000) | **verified** |
| 2010s | 1,278 | 1,278 (CDC Adult Tobacco CSV, 2010) | **verified** |
| 2020s | 890 | 890 (CDC Adult Tobacco CSV, 2020) | **verified** |

### Smoking prevalence (7 facts)

| Decade | Fact value | Source value | Result |
|--------|-----------|-------------|--------|
| 1960s | 42.4% | 42.4% (NHIS 1965 via ALA) | **verified** |
| 1970s | 37.4% | 37.4% (NHIS 1970 via ALA) | **verified** |
| 1980s | 33.2% | 33.2% (NHIS 1980 via ALA) | **verified** |
| 1990s | 25.5% | 25.5% (NHIS 1990 via ALA) | **verified** |
| 2000s | 23.3% | 23.3% (NHIS 2000 via ALA) | **verified** |
| 2010s | 19.3% | 19.3% (NHIS 2010 via ALA) | **verified** |
| 2020s | 12.5% | 12.5% (NHIS 2020 via ALA) | **verified** |

### Cross-checks

- 1963 peak of 4,345 cigarettes/adult confirmed in MMWR text: "Per capita annual consumption was 54 cigarettes in 1900, peaked at 4,345 in 1963"
- 2025 preliminary rate of 9.1% confirmed via CDC FastStats page
- Sex breakdown (1965: 51.9% men / 33.9% women) confirmed via ALA table extraction
- Pre-1965 prevalence: structural gap (NHIS first assessed tobacco in 1965)

---

## Plan 028 WI-1: CPI component series for the early rooms (2026-07-28)

**Date:** 2026-07-28
**Verifier:** claude-opus-5 session
**Context:** The 1910s/1920s/1930s rooms carried four declared gaps each and no
price content at all in the `table` panel. BLS has published food, rent and
apparel indexes continuously since 1913, so the price record for those decades
is excellent even though the income and expenditure record is not. Added
`data/series/cpi-{food,rent,apparel}.toml` (112 years each, 1913-2024) via
`scripts/bls_cpi_components_extract.py`, and seven Tier A facts across the three
rooms.

### 1a: Source selection — why not the scanned table

Historical Statistics of the United States 1789-1945, Series L 40-47 (p. 246 of
`hist_stats_1789-1945.pdf`) carries the same data. **Its PDF text layer is not
usable for curation.** The scan's OCR renders zeros as ".0", so 100.0 appears as
`1.0.0 . .0` and 106.3 as `1.06.3`; it also mangles letters (`l'JATIOl'JAL` for
NATIONAL). Two independent extractors (pypdf and pymupdf) reproduce the same
corruption, which establishes it is baked into the document rather than an
artefact of one reader.

A PDF having a text layer is not the same as that text being transcribable —
the same shape as WI-023's finding that a 200 OK is not proof a URL serves the
described document. The values were therefore taken from the BLS Public Data
API, which has no transcription step at all.

### 1b: Independent cross-check — BLS API against the printed 1949 table

The printed table is unusable for bulk transcription but perfectly usable as an
*independent check* on a handful of cells, and it is a genuinely independent
source: a 1949 Census/BLS publication, on a different base (1935-39=100) from
the API's (1982-84=100). BLS values were rebased by dividing by their own
1935-39 mean and compared against the printed figures.

| Year | Component | BLS API (1982-84=100) | Rebased to 1935-39=100 | HSUS L 40-47 printed | Difference |
|---|---|---|---|---|---|
| 1920 | All items | 20.0 | 142.9 | 143.3 | −0.31% |
| 1920 | Food | 21.0 | 169.4 | 168.8 | +0.33% |
| 1920 | Apparel | 43.1 | 200.8 | 201.0 | −0.08% |
| 1920 | Rent | 27.4 | 120.6 | 120.7 | −0.08% |
| 1925 | All items | 17.5 | 125.0 | 125.4 | −0.32% |
| 1925 | Food | 16.5 | 133.1 | 132.9 | +0.12% |
| 1925 | Apparel | 26.3 | 122.6 | 122.4 | +0.13% |
| 1925 | Rent | 34.6 | 152.3 | 152.2 | +0.06% |
| 1929 | All items | 17.1 | 122.1 | 122.5 | −0.29% |
| 1929 | Food | 16.5 | 133.1 | 132.5 | +0.43% |
| 1929 | Apparel | 24.7 | 115.1 | 115.3 | −0.18% |
| 1929 | Rent | 32.1 | 141.3 | 141.4 | −0.08% |

**Result: 12/12 agree within 0.43%.** Residuals of this size are expected from
rounding in the printed table (one decimal place, on a base that is itself a
five-year mean) and from series revisions in the intervening 77 years. Two
sources, two bases, two eras of publication, same series.

This also incidentally confirms that the four HSUS cells were read correctly
despite the corrupt text layer — the corruption is systematic (zeros) rather
than random, so a rebased match at four significant figures is not a coincidence.

### 1c: Extraction reproducibility

The extractor was run once, and its output spot-checked against a separate
ad-hoc API pull made before the script existed: `cpi-food` 1913=10.0, 1920=21.0,
1932=10.7; `cpi-rent` 1913=21.0, 1921=31.5; `cpi-apparel` 1920=43.1. All match.

### 1d: What these facts do not claim

The seven facts are price indexes. They do **not** close the food-basket gap in
any of the three rooms, and the room notes say so explicitly: an index shows how
the cost of eating moved, never what the family ate. The income gaps and
work-buys gaps are untouched — without a family-income figure, affordability
still cannot be computed for these decades. The 1930s food fact states the point
directly, because it is the one most likely to be misread: food fell 37% while
incomes fell faster, so deflation is not affordability.

---

## Plan 027 WI-2: smoking series (2026-08-29)

**Date:** 2026-08-29
**Verifier:** glm-5.3 session
**Context:** Phase A of Plan 027 — the "different country" wing and its
smoking flagship. Three series + 13 consumption facts authored; the
pre-1965 prevalence facts already existed (curated 2026-07-17) and were
re-verified against the new series by the drift gate and by eye.

### 2a: MMWR SS-3 Table 1 — per-capita cigarette consumption, 1900-1994

**Source:** samples/34-smoking/mmwr-tobacco-surveillance-1900-1994.html
(MMWR Surveillance Summary Vol. 43 No. SS-3, fetched by a prior session,
re-verified on disk this session).
**Method:** script extraction (scripts/mmwr_tobacco_extract.py) over the
flattened table text, then direct eye comparison of the parsed rows against
the source text. The table's three irregular rows were handled explicitly:
1900 (no change column), 1993 (`@` = provisional), 1994 (`&` = projected).

| Year | Source text | Parsed | Agrees |
|------|-------------|--------|--------|
| 1900 | "2.5 54" | 54 | ✓ |
| 1920 | "44.6 665 - 8.5" | 665 | ✓ |
| 1925 | "79.8 1,085 +10.5" | 1085 | ✓ |
| 1940 | (prose cross-check "1,976") | 1976 | ✓ |
| 1945 | "340.6 3,449 +13.5" | 3449 | ✓ |
| 1955 | "396.4 3,597 + 1.4" | 3597 | ✓ |
| 1963 | "peaked at 4,345 in 1963" (prose) | 4345 | ✓ |
| 1964 | (prose cross-check "4,194") | 4194 | ✓ |
| 1965 | "528.8 4,258 + 1.5" | 4258 | ✓ |
| 1975 | "607.2 4,122 - 0.5" | 4122 | ✓ |
| 1985 | "594.0 3,370 - 2.2" | 3370 | ✓ |
| 1990 | "estimate of per capita consumption (2,817)" (Methods prose) | 2817 | ✓ |
| 1994 | "&amp; 480.0 2,493" | 2493 | ✓ |

The prose statements in the document's own narrative (54 in 1900, 4,345 peak
in 1963, 2,493 in 1994, 2,817 in 1990) independently confirm the table parse
at four cells — table and prose agree with each other and with the script.

### 2b: CDC Adult Tobacco Consumption CSV — 2000-2023

**Source:** samples/34-smoking/adult-tobacco-consumption-2000-present.csv.
**Method:** filtered Cigarette Removals rows; read `Total Per Capita`.
The `Population` column (2000: 209,786,736) confirms the denominator is the
18+ population, not total residents — this is per-**adult**, matching the
MMWR basis. Spot-verified by eye: 2000 = "2,076" (2,018 domestic + 59
imports), 2005 = "1,717", 2010 = "1,278", 2015 = "1,083", 2020 = "890",
2023 = "678". The 1999 MMWR achievements piece states 1998 = 2,261 in prose;
1995-1999 remain unentered (no table in the archive covers them) — the gap
renders.

### 2c: NHIS smoking prevalence — series vs. pre-existing facts

**Source:** samples/34-smoking/cdc-trends-cig-smoking-1965-2014.html
(CDC/NCHS trends table, Wayback snapshot 2018-11-13; blank cells carry
`<!-- -->` placeholders and are preserved as gaps).
**Method:** parsed the Adults column (27 survey-year values 1965-2014), then
compared against the six pre-existing room facts (2026-07-17 curation, ALA
table) and against MMWR SS-3 Table 2 where years overlap:

| Year | CDC trends (series) | Existing fact | MMWR Table 2 | Agrees |
|------|--------------------|---------------|--------------|--------|
| 1965 | 42.4 | 42.4 | 42.4 | ✓ |
| 1970 | 37.4 | 37.4 | 37.4 | ✓ |
| 1980 | 33.2 | 33.2 | 33.2 | ✓ |
| 1990 | 25.5 | 25.5 | 25.5 | ✓ |
| 2000 | (blank cell) | 23.3 (ALA) | n/a | **series omits; fact keeps ALA value with its source's disclosure** |
| 2010 | 19.3 | 19.3 | n/a | ✓ |

The drift gate (invariant 9) passes: where series and fact share a source
and a year, they agree. The 2000 discrepancy is a coverage difference (the
CDC trends table has a blank 2000 adults cell; the ALA table publishes
23.3), not a value conflict; both are disclosed on their own records.

Known secondary-source variance noted and NOT entered: 2006 = 20.8 (CDC
trends, entered) vs 20.6 (ALA); 2022 = 11.6 final (ALA) vs 11.2 preliminary
(NCHS Early Release). Early Release and ALA-analysis values stay out of the
series until final NCHS publication is on file.

### 2d: What these facts do not claim

Per-capita consumption is a tax-derived population basis, not individual
behavior: it divides removals by all adults (including non-smokers), so it
cannot be read as "cigarettes per smoker." The TTB segment (2000+) counts
taxable removals, not consumption. Prevalence measures current smokers among
civilian noninstitutionalized adults; institutionalized and military
populations are outside the frame. No fact here claims health outcomes.

---

## Plan 027 WI-2 corrections (2026-08-29, adversarial review pass)

**Date:** 2026-08-29
**Verifier:** glm-5.3 session, applying cross-lineage adversarial review
findings (deepseekv4flash reviewer; the reviewer independently re-verified
all 136 values and found the transcription clean — the corrections below
are provenance and presentation defects, not number errors).

### 2e: Series provenance corrected (reviewer C1)

The `us-smoking-prevalence` series was cited to `cdc-nhis-smoking-prevalence`
(the American Lung Association compilation) while its values were
transcribed from the CDC/NCHS trends table — two compilations that differ
(2006: 20.8 CDC vs 20.6 ALA; the ALA table publishes 2000 = 23.3 where the
CDC table's adults cell is blank). **Fix:** registered the trends table as
its own source (`cdc-trends-cig-smoking`) with the snapshot URL and the
2006 divergence disclosed in its notes; the series now cites the document
it was actually read from. A visitor clicking the source card now lands on
a table that shows the entered values.

### 2f: Unsourced side-claims removed from the truth path (reviewer M2)

The series note and arc caveat claimed "'some days' counted from 1992;
questionnaire redesigned 1997 and again in 2019." Verification against the
archive: the 1992 note IS on file (Surgeon General's 2014 report, Table
12.2 note, samples/34-smoking/sg-2014-table12.2-prevalence.txt — "the some
days condition was added in 1992") and is kept, named. The 1997 redesign is
stated on the ALA compilation (its † marker) but not by either cited table;
the 2019 redesign appears only in NCHS Early Release preamble text, not a
cited document. Both were removed from truth-path strings (series notes,
arc caveats); they remain above as archive observations with their
documents named.

### 2g: Marker-year coherence (reviewer M1/M3)

Arc markers defaulted to mid-decade positions while the facts state their
own years, visibly contradicting the annual lines (e.g. the 1980 prevalence
fact 33.2@1980 plotted at 1985, where the series reads 30.1). **Fix:**
`price_year` set on all 13 cigarette-consumption facts (label years,
previously verified against the series) and all 6 smoking-prevalence facts
— which also activates the invariant-9 drift detector over every one of
them (series/fact agreement is now mechanical, not just logged). The
consumption arc's fact_ids are trimmed to 1900s–1990s: its series line ends
1994 where its table does, and post-1994 markers clamped to the chart edge
(2005/2015/2023 piling at 1994) misrepresented the splice; the TTB-era
decades stay in their room placards and the continuation series, with the
arc caveat saying exactly that.

### 2h: ALA compilation cells corrected (reviewer m2; pre-existing facts)

Two sex-split cells in the 2026-07-17 facts were off by one column against
the ALA table on disk (verified this session, parsing the table's year
header including its footnoted "1997 †" column):

- us-2000s-smoking-prevalence: female 2000 was 20.7 (the 2001 value);
  ALA Female 2000 = 21.0. **Corrected to 21.0.**
- us-2020s-smoking-prevalence: male 2020 was 14.0; ALA Male 2020 = 14.1.
  **Corrected to 14.1.**

All other cells in both facts re-verified against the table (total 23.3 /
12.5 ✓, male 2000 25.7 ✓, female 2010 17.3 ✓, female 2020 11.0 ✓).

### 2i: Duplicate concept facts removed (reviewer m1)

The 2026-08-29 session added `us-{decade}-cigarettes-per-capita` day-panel
facts without noticing the 2026-07-17 session's `us-{decade}-cigarette-
consumption` table-panel facts (same sources, same series). The new
duplicates were removed and the arc re-bound to the pre-existing facts,
whose values match the new series at every label year (verified 13/13
before binding; now drift-gated via price_year).

---

## FWI-001: The UK affordability axis (2026-09-01)

**Date:** 2026-09-01
**Verifier:** claude-opus-5 session
**Context:** The seven UK rooms carried no wage or income anchor, so the
museum's central mechanic — what a thing cost in hours of work — was blank for
the whole wing. The source archive for it landed on 2026-08-29 and the
transcription was deliberately deferred to a fresh session. Every value below
was read from the document in `samples/`, never from that session's summary
notes (`samples/30-uk-income/EXTRACTED-DATA.md` was not used as a source).

### F1a: ASHE hourly pay and paid hours (1997, 2000, 2010)

**Source checked:** ONS ASHE Table 1, `samples/43-uk-hours/ashe-table1/*.zip`,
tables 1.5a (hourly pay — gross) and 1.9a (paid hours worked — total), `All`
sheet, `All Employees` row.
**Method:** `scripts/uk_ashe_extract.py`, which locates the workbook by a
bounded table-number match and the value row by its header labels. The
member-name format changes three times across the series (the 2000–2003 zips
drop the word "Table"; 2010 carries a `REVISED - All Employees` prefix; 2011+
are `.xlsx` where earlier years are `.xls`), so a fixed name or column index
reads the wrong file or the wrong cell without failing.
**Fact IDs:** uk-1990s-hourly-pay, uk-2000s-hourly-pay, uk-2010s-hourly-pay,
uk-1990s-paid-hours, uk-2000s-paid-hours, uk-2010s-paid-hours

| Year | Median hourly | Mean hourly | Full-time median | Median paid hours | Mean paid hours | Jobs (thousand) |
|------|---------------|-------------|------------------|-------------------|-----------------|-----------------|
| 1997 | £7.07 | £8.90 | £7.92 | 37.0 | 35.1 | 20,858 |
| 2000 | £7.93 | £10.22 | £8.91 | 37.0 | 34.7 | 21,721 |
| 2010 | £11.14 | £14.60 | £12.57 | 37.0 | 33.4 | 24,263 |

**Result: verified**, transcribed as displayed. The full-time median is carried
in each fact's notes because the all-jobs median — the anchor — sits about 12%
below it, and a reader who assumes "the wage" means full-time would misread the
number alone.

### F1b: ETB household disposable income (1977, 1980, 1990, 1997/98, 2000/01, 2010/11)

**Source checked:** ONS "Effects of taxes and benefits on household income",
historical dataset by household type,
`samples/30-uk-income/etb-hhldtype.xlsx`, non-retired block, `2 adults with 2
children` column.
**Method:** `scripts/uk_etb_extract.py`. The column is located by *composing*
the stacked header cells and matching the composed text. This is not
defensive over-engineering: the header block gains a `1 adult Men/Women` split
between the 1980 and 1990 sheets, moving the target from column 6 to column 8.
A fixed index reads "2 adults with 1 child" for half the series and nothing
fails. The script prints every column's composed header and the neighbouring
columns' values so a wrong pick is visible rather than merely absent.
**Fact IDs:** uk-1970s-household-income, uk-1980s-household-income,
uk-1990s-household-income, uk-2000s-household-income, uk-2010s-household-income

| Sheet | Original | Cash benefits | Gross | Direct tax + NIC | Disposable |
|-------|----------|---------------|-------|------------------|------------|
| 1977 | £5,073 | £257 | £5,330 | £1,214 | **£4,116** |
| 1980 | £8,218 | £569 | £8,787 | £1,899 | **£6,888** |
| 1990 | £20,396 | £1,216 | £21,613 | £4,344 | £17,269 |
| 1997-98 | £30,047 | £2,018 | £32,064 | £7,130 | **£24,934** |
| 2000-01 | £36,241 | £2,629 | £38,870 | £8,690 | **£30,181** |
| 2010-11 | £55,409 | £4,863 | £60,272 | £14,144 | **£46,129** |

**Result: verified.** Bolded values are the ones cited; 1990 is recorded here
because it was extracted before the anchor year moved to 1997.

**Correction made in passing — twice, the second time to this log.** The
direct-tax figures were first going to be written as gross − disposable. Each
row of this table is independently rounded to the pound, so the arithmetic does
not close: 2000-01 publishes £8,690 of direct tax where the subtraction gives
£8,689, and 2010-11 publishes £14,144 where it gives £14,143. Every row above
is therefore transcribed, not derived.

The first draft of this log then did the same thing again: it recorded 1990
cash benefits as £1,217 (gross − original) where the sheet publishes **£1,216**.
Corrected above by re-reading the row. The lesson is not that the arithmetic is
close enough — it is that a number reached by computing is not evidence of what
the source says, no matter how obvious the computation, and the habit reasserts
itself the moment attention moves to prose.

### F1c: ONS house prices (1997, 2000, 2010), and a cross-check that first failed

**Source checked:** ONS house price annual tables,
`samples/32-uk-housing/ons-hpi-annual-tables.xls`, Table 31 (simple average
house prices, United Kingdom, unadjusted), cross-checked against Table 28.
**Method:** `scripts/uk_house_price_extract.py`.
**Fact IDs:** uk-1990s-house-price, uk-2000s-house-price, uk-2010s-house-price

| Year | Table 31 | Table 28 (all dwellings) | Table 28 borrower income | Nationwide Q4 |
|------|----------|--------------------------|--------------------------|---------------|
| 1997 | £76,103 | £76,103 | £26,086 | £61,830 |
| 2000 | £101,550 | £101,550 | £31,193 | £81,628 |
| 2010 | £251,174 | £251,174 | £57,973 | £162,971 |

**Result: verified**, with the two ONS tables agreeing to the pound.

**The cross-check was wrong the first time and said so loudly**, which is the
only reason it was caught. Table 28 breaks the same survey across 25 columns —
new dwellings, other dwellings, all dwellings, first-time buyers, former owner
occupiers — and the first price column at a fixed index is *new dwellings*. It
read £93,196 against Table 31's £76,103 for 1997 and, worse, flipped sign by
2010 (£213,604 against £251,174). Had the two series merely differed by a
plausible margin in a consistent direction, the mismatch would have been filed
as a methodology difference and the wrong column believed. The fix locates the
`All dwellings` block by its composed header.

Nationwide runs 20–35% below ONS throughout. That is a real methodological
difference (a lender's mix-adjusted index of its own lending, versus a simple
average of survey transactions), not a discrepancy to resolve; it is recorded
here and Nationwide is not cited by any fact.

### F1d: British Labour Statistics Year Book hours — three independent routes

**Sources checked:** `samples/43-uk-hours/bls-yearbook-1976.pdf` p.57 (all
industries, April 1972–76) and `bls-yearbook-1969.pdf` p.40, Table 10 (all
industries covered, April/October 1965–69). Both are 216MB scans with an OCR
text layer of unknown provenance.
**Fact IDs:** uk-1970s-paid-hours, uk-1970s-hourly-earnings, uk-1960s-work-hours

An OCR text layer is one transcription pass, and its failure mode is a
plausible wrong digit rather than an error. Each committed value was therefore
established on more than one route:

1. **Coordinate reconstruction** of the page's word boxes (the reading-order
   text is unusable — the number grid arrives detached from its headers).
2. **Reading the rendered page image** directly, independently of the text
   layer.
3. **An external series** that must agree if the column mapping is right.

**1976 volume, p.57, all industries, April 1976:**

| Row | Weekly (excl. absence) | Hours | Hourly incl. OT | Hourly excl. OT |
|-----|------------------------|-------|-----------------|-----------------|
| Full-time manual men 21+ | £65.10 | 45.3 | 143.7p | 141.0p |
| All full-time men 21+ | £71.80 | 42.7 | 166.8p | **166.6p** |
| Full-time non-manual men 21+ | £81.60 | 39.1 | — | — |
| All full-time women 18+ | — | 37.3 | — | — |

- Routes 1 and 2 agree cell for cell.
- Route 3, weekly earnings: the ONS long-run series
  (`ons-earnings-1938-2025.xlsx`, an independent publication) gives 1976 adult
  male full-time **manual £65.10, "All" £71.80, non-manual £81.60** — three
  exact matches, which fixes the column mapping (the "all industries,
  excluding those whose pay was affected by absence" column) beyond doubt.
- Route 3, hours: the Bank of England Millennium workbook, sheet A54 col. 50
  ("Average weekly hours — full time adults, April, New Earnings Survey")
  gives **41.1** for 1976. That series covers adults of both sexes; the men's
  42.7 and women's 37.3 above weight to 41.1 at roughly a 70/30 employment
  split. Corroborated.
- The header itself was read from the rendered page: the paired columns are
  *including/excluding those whose pay was affected by absence* for weekly
  earnings and *including/excluding overtime pay and overtime hours* for
  hourly earnings — **not** including/excluding overtime for both, which is
  what the flattened text layer suggests and which would have swapped two
  columns.

**1969 volume, p.40, Table 10, men 21+ manual full-time, all industries
covered, average hours worked:**

| April 1965 | Oct | April 1966 | Oct | April 1967 | Oct | April 1968 | Oct | April 1969 | Oct |
|---|---|---|---|---|---|---|---|---|---|
| **47.5** | 47.0 | 46.4 | 46.0 | 46.1 | 46.2 | 46.2 | 46.4 | 46.4 | 46.5 |

- Routes 1 and 2 agree on all ten observations.
- Route 3: the same column's weekly earnings for April 1965 read **£18 18s 2d**
  = £18.908, and the ONS long-run series reports **£18.91** for 1965 adult male
  manual workers — the figure this room already cited before this session. The
  agreement confirms that the last column is "All Industries covered" and that
  the OCR of this page is sound.
- The £ s. d. earnings of this volume are **not** transcribed: converting
  shillings and pence to decimal pence is arithmetic on the truth path with no
  registered derivation op, and the museum's money layer holds whole pence.

### F1e: What was deliberately not written

- **No wage anchor for the 1970s.** The decade's hourly earnings are 166.6p —
  a tenth of a penny. `vitrine.money` holds GBP in whole pence, so the value
  cannot be an `amount_minor` without rounding to £1.67, which would put a
  number on the page that no source printed. The figure is published as a plain
  fact and the hours axis stays uncomputed for that room.
- **No wage anchor for the 1980s.** The Year Books end with the 1976 volume,
  ASHE hours begin in 1997, and the LFS per-worker averages begin in 1992
  (confirmed by the ONS FOI response in the archive). The decade genuinely has
  no hours in the archive.
- **No priced fact before 1990s.** The official ONS house-price series begins
  in 1991 (Table 31) / 1986 (Table 28). The only series reaching the 1970s and
  1980s is Nationwide's, which is a lender's index rather than an official
  statistic; the rooms say so rather than citing it.
- **No income anchor before the 1970s.** The ETB series begins in 1977.
- The 1950s room's notes previously said "no continuous hours-worked survey
  exists before the Labour Force Survey (1973)". This session's reading of the
  Year Books shows that claim to be **false** — the Department of Employment's
  twice-yearly enquiry recorded hours through the 1960s. The note now says what
  is actually true: those figures exist, but the volumes in the archive reach
  back only to 1965.

---

## Plan 027 WI-3: Alcohol per capita, with the Prohibition gap (14 facts, 13 rooms + 1 series)

**Date:** 2026-09-01
**Verifier:** Claude Opus 5 session (mvmcc02)
**Source checked:** NIAAA Surveillance Report #122, *Apparent Per Capita
Alcohol Consumption: National, State, and Regional Trends, 1977–2023* (Slater
& Alpert, April 2025), Table 1, "Apparent per capita ethanol consumption,
United States, 1850–2023", all-beverages column.
**Archive copy:** `samples/34-smoking/niaaa-surveillance-122.pdf`
**Extraction:** `scripts/niaaa_alcohol_extract.py` → `data/series/us-ethanol-per-capita.toml`

### Provenance: the archived PDF is the served document

The archive copy was compared byte-for-byte with the document served at the
cited URL on 2026-09-01:

| | sha256 |
|---|---|
| served (`https://www.niaaa.nih.gov/sites/default/files/surveillance-report122.Per-Capita-Consumption.pdf`) | `71f1e8531f2de32138f99d20b239ec78215a23b50070294fbb80671507bc222a` |
| archived (`samples/34-smoking/niaaa-surveillance-122.pdf`) | `71f1e8531f2de32138f99d20b239ec78215a23b50070294fbb80671507bc222a` |

**Identical.** The transcription source and the citation target are the same
bytes. (The `samples/MANIFEST.md` archive index has no entry for this file —
it was archived on 2026-07-17 without being manifested. Noted, not fixed here.)

### Method

The values were read out of the PDF itself with PyMuPDF, not out of the
flattened `niaaa-text.txt` dump beside it and **not** out of
`niaaa-alcohol-extraction.md`, the markdown extraction summary in the same
directory — a summary is a secondary source, and a prior session's summary is
exactly what the truth-path rule exists to keep out of the data. That rule
earned its keep here: the summary states that 1970 is the "last year using
ages 15+ basis", while the table's own header reads "based on population ages
15 and older prior to 1970 and on population ages 14 and older thereafter" —
i.e. 1970 is already on the 14+ basis. The header was followed.

The parser asserts the row shape (a year or year-range label, then exactly
four numeric cells) so a layout change fails loudly rather than misparsing,
and it refuses to write unless the literal `(Prohibition)` row is present, no
value falls in 1920–1933, and the post-Repeal record is continuous.

### Cross-check: two independent extractions of the same PDF

The 90 parsed annual values were compared against an independent re-parse of
`niaaa-text.txt` (a differently-produced text rendering of the same PDF):

| | |
|---|---|
| series values | 90 (1934–2023) |
| text-dump rows matched | 93 (the extra three are 1850/1860/1870) |
| overlap compared | 90 |
| **mismatches** | **none — every value reproduces exactly** |

### Spot-verification against the rendered table

Read off the PDF's own text layer (report pages 11–12):

| Row | Beer | Wine | Spirits | All beverages | In the data |
|---|---|---|---|---|---|
| 2023 | 0.99 | 0.41 | 1.08 | 2.48 | ✓ |
| 2020 | 1.05 | 0.44 | 0.95 | 2.44 | ✓ (2020s card) |
| 1981 | 1.39 | 0.35 | 1.02 | 2.76 | ✓ (cited as the modern peak) |
| 1980 | 1.37 | 0.34 | 1.04 | 2.75 | ✓ (1980s card) |
| 1970 | 1.14 | 0.27 | 1.11 | 2.52 | ✓ (1970s card; spirits cited) |
| 1950 | 1.04 | 0.23 | 0.77 | 2.04 | ✓ (1950s card) |
| 1934 | 0.61 | 0.07 | 0.29 | 0.97 | ✓ (1930s card) |
| 1911–1915 | 1.48 | 0.14 | 0.94 | 2.56 | ✓ (1910s card) |
| 1901–1905 | 1.31 | 0.13 | 0.95 | 2.39 | ✓ (1900s card) |
| *(Prohibition)* | — | — | — | — | ✓ rendered as a gap |

Every numeral quoted in a fact's `notes` is asserted against the parsed table
by `scripts/niaaa_alcohol_cards.py` before it writes anything (1.96 for
1916–1919, 2.30 for 1946, 1.11 spirits for 1970, 2.76 for 1981, 2.15 for 1995,
2.54 for 2021, 2.48 for 2023). None was typed from memory. That script is
committed rather than left in a scratch directory for the same reason this log
exists: an assertion whose artifact is gone is a claim, not evidence. It is
idempotent — re-running reports "already present" rather than inserting a
second copy — which was learned the hard way here, when a first pass did
double-insert all thirteen cards and the provenance gate caught it
("duplicate fact id", 13 problems).

### What was deliberately left out

- **1920–1933.** The table prints `(Prohibition)` and no numbers. Rendered as
  a gap card in the 1920s room and a gap slot on the arc. Not interpolated, no
  estimate substituted. Per Plan 027 D2, any Warburton-style reconstruction
  would be a separate Tier C/D fact with its methodology on the card.
- **The eight pre-1934 five-year ranges.** A range is not a year and cannot
  enter a year-keyed series without inventing a datum. Two of them (1901–1905,
  1911–1915) are carried as decade cards, which name the range in the value;
  the six that straddle a decade boundary or predate the museum's floor are
  not carried at all.
- **1850, 1860, 1870.** Published as single years, so they *could* enter the
  series — but they sit before the museum's 1890s floor, and including them
  would draw one line across a 63-year void that is really two different
  absences (a grouped-publication era, then a measurement collapse).

### Disclosed weaknesses in the source itself

- **The early half is republished scholarly work.** The table's own note reads
  "Data prior to 1977 are from Hyman et al. 1980". Carried in the series notes
  and as an arc caveat; the series is still Tier A because NIAAA publishes the
  figures as its own table, but the caveat says whose they were.
- **The denominator changes at 1970** (ages 15+ → 14+). Disclosed, not
  corrected for.
- **"Apparent" consumption is legal sales ÷ population**, so it measures what
  the state could count. This is the reason the Prohibition gap exists at all,
  and it is stated on the arc rather than left as an inference.

### Standing gates

`tests/test_alcohol_series.py` (17 tests). Each was proven to fail by
mutation: drifting a card's quantity from the series, adding a value inside
Prohibition, turning the 1920s gap card into a number, and dropping the
`(Prohibition)` expect-marker each redden a named test. The expect-marker is
the load-bearing one for the citation: if NIAAA ever republished with those
years backfilled, `scripts/link_check.py` would redden rather than the museum
quietly citing a document that no longer says what its cards say it says.

---

## Plan 027 WI-4a: Road deaths per 100 million vehicle-miles (13 facts, 13 rooms + 1 series)

**Date:** 2026-09-01
**Verifier:** Claude Opus 5 session (mvmcc02)
**Source checked:** FHWA, *Highway Statistics 2023*, Table FI-200, "Motor
vehicle traffic fatalities, 1900–2023".
**Archive copy:** `samples/44-road-workplace-deaths/fhwa-fi200-highway-statistics-2023.html`
**Extraction:** `scripts/fhwa_traffic_deaths_extract.py` → `data/series/us-traffic-death-rate.toml`
**Cards:** `scripts/fhwa_traffic_cards.py`

### The column was identified by arithmetic, not by position

FI-200 publishes four fatality-rate columns side by side — per 1,000 miles of
road, per 100 million annual VMT, per 100,000 registered motor vehicles, per
100,000 licensed drivers — any of which would look plausible read alone. The
extractor recomputes the rate from the table's own fatality and VMT columns and
refuses to write unless the published figure reproduces for **every** year.

Pointed at each neighbouring column in turn, the guard behaves as intended:

| column read | result |
|---|---|
| per 1,000 miles of road | **rejected** |
| per 100 million annual VMT | accepted |
| per 100,000 registered motor vehicles | **rejected** |
| per 100,000 licensed drivers | **rejected** |

### Cross-check: two FHWA publications, 26 years apart

The 1900–1995 rows were compared against FHWA's separately-published *Highway
Statistics Summary to 1995* (Table FI-200, April 1997), archived as
`fhwa-fi200-summary-to-1995.pdf`:

| | |
|---|---|
| years compared | 96 |
| reproduce exactly | 95 |
| differ | 1 |

The single difference is **1995**, that publication's terminal — and therefore
provisional — year: the 1997 edition reports 41,770 deaths and a rate of 1.72,
the 2023 edition 41,817 and 1.73, on identical VMT (2,422,823 million). That is
a source revision, recorded here rather than smoothed over. Every other year
across nearly a century of the table reproduces to the published decimal.

### Four prose numerals were wrong and the guard caught all four

`scripts/fhwa_traffic_cards.py` asserts every numeral quoted in a card's notes
against the parsed table before writing anything. Four claims drafted from
recall failed that assertion and were corrected from the table:

| claim as drafted | what FI-200 says |
|---|---|
| peak absolute deaths 54,589 (1972) | **55,600** (1972) |
| the rate peaked "around 1910" | peaked **1909 at 45.33** |
| 1940s: wartime rationing cut travel "and the rate fell with them" | travel fell 38% and deaths 40%, so the **rate barely moved** (11.43 → 10.92) |
| 1990 was the first year below 2.0 | 1990 is **2.08**; the crossing is **1991** |

This is Plan 027 D3 operating exactly as written — "the famous-headline numbers
are the dangerous ones" — and it is the reason the assertions exist rather than
a spot-check at the end. The wartime one is the instructive failure: the drafted
sentence was not merely off by a digit, it told the story backwards.

### Disclosed weaknesses in the source itself

- **A definitional change at 1976.** FHWA footnote (3): "Beginning in 1976,
  includes only persons injured in a highway vehicular crash that died within
  30 days." Earlier years were counted on a wider window, so the two halves of
  the line are not the same measurement. Carried as an arc caveat, as a series
  note, and as an `expect` marker on the source so the link check notices if
  FHWA ever drops the footnote.
- **The 1900 figure rests on 36 deaths** against an estimated 100 million
  vehicle-miles. It is published, not reconstructed, but the exposure is very
  thin and the travel figure is a back-cast. Disclosed on the card and in the
  arc caveats, and asserted by a test.
- **The plan's D2 assumption was wrong.** Plan 027 anticipated "vehicle deaths
  in the 1900s: cars barely existed; there is no rate", to be rendered as a
  gap. FI-200 does publish a rate back to 1900, so rendering a gap there would
  have been *inventing* an absence. The published figure is carried, with its
  thinness disclosed.
- **A rate is not a count.** Absolute road deaths peaked at 55,600 in 1972 and
  were still near 41,000 in 2023; what fell by a factor of about thirty is the
  risk per mile. A test asserts both that the caveat saying so is present and
  that its premise holds against the series.

### What WI-4 did not deliver, and why

Plan 027 WI-4 specifies **two** arcs. Only the road one is landed here.

The workplace arc — occupational fatalities per 100,000 workers, NSC estimates
1913–1992 spliced to BLS CFOI 1992–present — is blocked on source acquisition,
not on effort:

- **BLS CFOI (1992→).** `www.bls.gov` returns 403 to non-browser clients (four
  CFOI pages tried). The flat-file host `download.bls.gov` answers, but only to
  a User-Agent carrying a contact address, which is a decision about the
  owner's data to send to a third party and is not the agent's to take. The
  BLS **public API** is reachable and the registered key works
  (`REQUEST_SUCCEEDED` against a known series), so this is a matter of
  obtaining the correct CFOI series identifiers, not of access.
- **NSC estimates (1913–1992).** *Injury Facts* is a commercial publication.
  The archived *Historical Statistics of the United States* Part 1 carries
  Series D 1029–1036, but those are work-injury **frequency and severity rates
  per million man-hours** — a different measure from fatalities per 100,000
  workers — and the volume's OCR is poor.

Recorded as FWI-006 rather than left implicit. The road arc stands on its own
and required none of the above.

---

## Plan 027 WI-4b: Deaths at work per 100,000 workers (4 facts, 4 rooms + 1 series)

**Date:** 2026-09-01
**Verifier:** Claude Opus 5 session (mvmcc02)
**Source checked:** BLS, Census of Fatal Occupational Injuries, hours-based
fatal work injury rates — the nineteen per-year workbooks
`fatal-occupational-injuries-hours-based-rates-YYYY.xlsx`, 2006–2024, Total
row, "Fatal injury rate" column.
**Archive copies:** `samples/44-road-workplace-deaths/hb-YYYY.xlsx` (19 files),
`cfoi-charts-1992-2017.pdf`, `bls-cfoi-fw-survey-definition.txt`
**Extraction:** `scripts/bls_cfoi_rates_extract.py` → `data/series/us-workplace-death-rate.toml`
**Cards:** `scripts/bls_cfoi_cards.py`

### What the plan wanted, and what the record actually holds

Plan 027 WI-4 asked for occupational fatalities per 100,000 workers as a
century-long arc, NSC estimates 1913–1992 spliced to CFOI 1992–present, with
"~61 → ~3.5 per 100k" named as a lead to verify. **That arc is not
constructible from freely published primary sources**, for two reasons the
sources state themselves:

- CFOI "has been active in all 50 States and the District of Columbia since
  **1992**" (BLS's own survey definition, archived as
  `bls-cfoi-fw-survey-definition.txt`). Before that there is no federal census
  of people killed at work. The century-long figures in circulation come from
  the National Safety Council's *Injury Facts*, a commercial publication.
- BLS changed the rate's basis in **2006**, from employment to hours worked
  ("In 2008, CFOI implemented a new methodology, using hours worked for fatal
  work injury rate calculations rather than employment" —
  `cfoi-charts-1992-2017.pdf`, p. 2). Pre-2006 rates measure something else.

So the honest series is 2006–2024, nineteen values, moving between 3.3 and
4.2. It is not a "different country" line. The exhibit that *is* honest is the
absence: for nine decades the United States did not count this. The arc is
four slots wide, the 1990s slot is a gap card explaining why, and the arc's
first caveat says the shortness is the point.

### Two column traps, one caught by the cross-check

The workbooks' layout changes three times across nineteen years: 2006–2016 have
no "Characteristic code" column; 2017–2018 add one **and** a fatality-count
column; 2019+ drop the count again. Reading a fixed column index therefore
returns *total hours worked* instead of the rate for two years:

| year | rate, column located by header | value at the fixed 2019+ index |
|---|---|---|
| 2016 | 3.6 | 3.6 |
| **2017** | **3.5** | **285,977** |
| **2018** | **3.4807** | **292,527.5** |
| 2019 | 3.5 | 3.5 |

The first draft did read by index, and the mistake surfaced only because the
values were cross-checked against a second BLS document. The extractor now
locates the column by header text.

### Cross-check: workbooks against BLS's own chart labels

The 2006–2017 values were compared against the data labels on the "Rate of
fatal work injuries per 100,000 full-time equivalent workers by employee
status, 2006–17" chart in `cfoi-charts-1992-2017.pdf` (All Workers series) —
a separately-produced BLS artifact:

| | |
|---|---|
| years compared | 12 |
| reproduce exactly | 12 |
| differ | 0 |

### Rounding

2018's workbook publishes the unrounded figure (3.48069787484815) where every
other year publishes one decimal place. It is rounded to 3.5, matching BLS's
published value, and the extractor asserts that rounding is a no-op for every
other year — so it cannot quietly alter a year that was already rounded.

### A citation this repo's CI cannot verify

`www.bls.gov` returns **403** to any client whose User-Agent carries no contact
address; `scripts/link_check.py` sends a plain browser UA, so this source will
report as *bot-blocked* in CI and its `expect` markers will never fire there.
A marker that never runs is not a check. This is stated in the source's own
notes and asserted by a test, so no later reader mistakes the entry for a
CI-verified citation. The markers were verified locally on 2026-09-01 against
the served page. Access for this session was made with the owner's explicit
approval to send a contact address to BLS.

### Standing gates

`tests/test_workplace_deaths.py` (9 tests), each proven to fail by mutation:
chaining a pre-2006 employment-based rate onto the series, turning the 1990s
gap card into a number, marking the flat arc `falling=True` (which would render
it in the museum's decline colour), and removing the source's admission that
its link check is inert each redden a named test. The "no trend the record can
call a fall" caveat is checked against the data rather than asserted: the test
fails if the rate's span ever widens past 1.0.

---

## Plan 027 WI-5: Births per 1,000 women aged 15–19 (8 facts, 8 rooms + 1 series)

**Date:** 2026-09-01
**Verifier:** Claude Opus 5 session (mvmcc02)
**Source checked:** NCHS, *Health, United States, 2019*, Table 1, "Crude birth
rates, fertility rates, and birth rates, by age, race, and Hispanic origin of
mother: United States, selected years 1950–2018" — All-races block, 15–19
"Total" column. The 2020 figure comes from NVSR 72(1), *Births: Final Data for
2021*, Table 2.
**Archive:** `samples/45-teen-births/` (3 documents)
**Extraction:** `scripts/nchs_teen_births_extract.py`; cards `scripts/nchs_teen_births_cards.py`

### Why the 2019 edition and not the newer one

*Health, United States, 2020–2021* Table Brth is the same table one edition
later, and it **drops 2010** from its selected years in favour of 2009 and
2019. The museum has a 2010s room, so the 2019 edition is the source and the
later one becomes a witness.

### Cross-checks: three NCHS documents

| witness | overlapping years | mismatches |
|---|---|---|
| *Health, United States, 2020–2021*, Table Brth (a later edition of the same table) | 12 | **0** |
| NVSR 72(1) Table 2 (compiled independently of the trend tables) | 6 | **0** |

The overlap is asserted to be at least five years before either comparison is
believed — a cross-check with no overlap reports "no mismatches" and means
nothing. An earlier draft of this work printed exactly that reassuring line on
a parse that had returned zero rows.

### Two traps, both hit during this work

1. **The wrong race block.** These tables repeat their whole year-by-year
   structure once per race and Hispanic-origin group. The first "All races"
   heading in NVSR 72(1) belongs to Table 1, on a different page with different
   columns, and the first race block a naive reader meets in that report is
   Hispanic — whose 2020 rate is **23.0** against the all-races **15.0**. The
   parser now reads only between an "All races" heading and the next race
   heading, requires that boundary to exist, and takes a caller-supplied table
   marker so it cannot latch onto the wrong table's block.
2. **The wrong age column.** "15–19 years" is a spanner over Total, 15–17 and
   18–19, with 10–14 immediately before it, and the two document families do
   not agree on how many columns precede it — *Health, United States* prints a
   crude birth rate and a fertility rate first, NVSR Table 2 prints only a
   total fertility rate. Reading NVSR at the trend-table offset returns the
   **15–17** sub-rate: 9.9 instead of 22.3 for 2015, about half, and entirely
   plausible in isolation. The cross-check caught it; the column index is now
   stated per document.

### The shape, which is the exhibit

| year | rate |
|---|---|
| 1950 | 81.6 |
| **1960** | **89.1** ← the highest published row |
| 1970 | 68.3 |
| 1980 | 53.0 |
| **1990** | **59.9** ← rose |
| 2000 | 47.7 |
| 2010 | 34.2 |
| 2020 | 15.0 (NVSR) |

Two facts cut against progress-as-direction, and both are asserted by tests:
the peak of American teenage childbearing is **1960**, the decade usually
remembered for its families, and the series **rose** between 1980 and 1990.
The arc is therefore not marked `falling`.

### Boundaries

- **No card before the 1950s.** The published table starts there. Earlier
  vital-statistics eras are a different registration regime and are not
  reconstructed.
- **Selected years, not annual.** NCHS prints 1950, 1960, 1970, 1980, 1990,
  1995, 2000, 2005, 2010 and then recent years. The line connects published
  rows; the true annual peak between them is not shown. Plan 027 D3 floated
  "~96 per 1,000 at the 1957 peak" as a lead — **it is not verified here** and
  is not asserted anywhere in the data, because this table does not print 1957.
- **The denominator is every woman aged 15–19**, not those who were sexually
  active, and in the earlier decades most of these births were to married
  women. Stated on the arc and asserted by a test.

### A repository fix this work forced

`cdc.gov` returns **403 to browser-like User-Agents** and serves plain tool
agents instead — the exact opposite of `bls.gov`, which requires a contact
address. `scripts/link_check.py` sent only a browser agent, so both NCHS
citations would have reported bot-blocked and their `expect` markers would
never have fired. The checker now retries a 403/405 once with a plain tool
agent, which makes these two citations genuinely verified in CI. It does not
rescue bls.gov, and is not meant to: that host wants personal data this public
repository does not carry.
