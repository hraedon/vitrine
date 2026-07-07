# Gap Log — Vitrine US Rooms

Tracking unsourced facts (Tier D) across all US decade rooms.

## Current state (after 2026-07-07 session, Ramey ingestion)

**20 gaps remaining** (18 prior + 2 new Ramey gap facts: 1990s + 2010s home production)

| Room | Gaps | Type |
|------|------|------|
| 1900s | 2 | Estimates with values (could upgrade to Tier A) |
| 1910s | 4 | Structural permanent (no surveys before 1947) |
| 1920s | 4 | Structural permanent |
| 1930s | 4 | Structural permanent |
| 1940s | 2 | Wartime permanent (no CEX, wartime controls) |
| 1950s | 1 | Estimate with value (car price) |
| 1990s | 2 | 1 RECS AC (fillable) + 1 Ramey (1992-94 survey excluded by author) |
| 2010s | 1 | Ramey series ends 2005; ATUS is a concept splice |
| 2020s | 0 | — |

### Ramey (2009) home-production hours ingested

28 facts added across 13 rooms (Plan 005 WI-2). Source: Valerie A. Ramey,
"Time Spent in Home Production in the Twentieth-Century United States,"
*J. Econ. History* 69(1), 2009. Tier C (period-survey reconstruction).

- Women's + men's weekly unpaid home-production hours (Tables 6A & 7)
  for benchmark years 1900–2005 across 10 decade rooms.
- Per-household total: 78→49 hrs/week (1900→2005, -37%).
- Component breakdown: 1920s housewife's week (Table 3).
- 1990s: gap rendered (Ramey excludes 1992-94 survey; no benchmark).
- 2010s: gap rendered (series ends 2005; ATUS is a concept splice).
- 2020s: splice-note fact connecting Ramey endpoint to existing ATUS fact.
- Draft (NBER w13985) ingested for comparison; data tables numerically
  identical to published version.

## Filled this session (19 gaps)

### CEX expenditure shares + food baskets (10 gaps, 1970s-2010s)
- 1970s: 1972-73 CEX Bulletin 1992 (FRASER + GLM-OCR)
- 1980s: 1985 CEX Table 4 (Wayback Machine)
- 1990s: 1996 CEX Table 4 (Wayback Machine)
- 2000s: 2005 CEX Table 4 (Wayback Machine)
- 2010s: 2013 CEX Table 1400 (cu-size-2013.xlsx)

### Housing characteristics (8 gaps)
- Heating fuel 1940-1980 (5 gaps) — Census Historical Housing Tables: Fuels
- Telephone diffusion 1970 + 1980 (2 gaps) — Census Historical Housing Tables: Telephones
- Median home value 2010 (1 gap) — ACS B25077 via Census Reporter API

### Affordability (1 gap)
- 2010s home-as-income-years (computed from ACS home value + Census F-8 income)

## Remaining gaps detail

### 1900s (2 estimates — could upgrade to Tier A)
1. Women's weekly earnings, 1905 ($6.17) — BLS Bulletin 49
2. New automobile price, 1904 ($750-$1,500) — contemporary auto records

### 1910s/1920s/1930s (12 structural permanent)
No consumer expenditure survey existed before 1947. No Census of Housing
before 1940. Income, housing, and food basket gaps are permanent rendered
gaps. Each decade has: income (budget), housing (home), food basket (table).

### 1940s (2 wartime permanent)
No CEX for 1940s. Wartime rationing (1942-46) makes expenditure data
non-representative. Expenditure shares and food basket are permanent gaps.

### 1950s (1 estimate)
Average new car price, 1950 (~$1,511) — could upgrade via NADA or BLS.

### 1990s (1 fillable — needs RECS PDF OCR)
Cell phone, AC, cable TV, computer. RECS 1993/2001 data available as PDFs
on EIA.gov but not in HTML table format (only 2015 RECS has HTML tables).
AC data found in 2015 RECS: 86.9% of homes. Need 1990s equivalent.
New OCR tools (parser2 pro, flash) would help extract from RECS PDFs.

## Data sources discovered this session

- **Census.gov is accessible** (unlike BLS which 403-blocks)
- **Wayback Machine** serves BLS PDFs that BLS blocks
- **FRASER** (fraser.stlouisfed.org) has historical BLS bulletins
- **EIA.gov** is accessible — RECS data for all years (1978-2024)
- **Census Reporter API** works for ACS data (no key needed)
- Census Historical Housing Tables at www2.census.gov:
  - coh-fuels/ (heating fuel 1940-1980)
  - coh-phone/ (telephone 1960-1990)
  - coh-plumbing/ (plumbing 1940-1990)
  - coh-values/ (home values 1940-2000)
  - coh-ownerchar/ (owner characteristics 1950-1990)
