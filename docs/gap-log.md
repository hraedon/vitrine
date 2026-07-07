# Gap Log — Vitrine US Rooms

Tracking unsourced facts (Tier D) across all US decade rooms.

## Current state (after 2026-07-07 enrichment round)

**14 gaps remaining** (unchanged — all permanent)

**19 new facts added this session** (236 → 255)

### New facts added (2026-07-07)

**AC diffusion arc completed (6 facts):**
- 1960s: 18.8% (CEX 1960-61) — split from combined diffusion fact
- 1970s: 23% central AC (1978 RECS, first survey)
- 1980s: arc 1978→1993 (23% central → 68% total)
- 2000s: 87% (2009 RECS, 61% central)
- 2010s: 87% (2015 RECS, 64% central)
- (1990s and 2020s already had AC facts)

**Heating fuel arc extended to 2020s (2 facts):**
- 2000s: RECS 2009 (gas 49%, electric 34%)
- 2010s: RECS 2015 (gas 51%, electric 36%)
- 1990s: RECS 1993 data inaccessible (EIA 503 on old URLs)

**CPI/purchasing power arc (5 facts):**
- 1970s-2010s: CPI + purchasing power for work-buys panel
- 1970: $1=$8.09, real income +1.33x
- 1980: $1=$3.81, real income +1.32x
- 1990: $1=$2.40, real income +1.25x
- 2000: $1=$1.82, real income +1.14x
- 2010: $1=$1.44, real income +1.22x

**1980s diffusion enrichment (3 facts):**
- Cable TV (1989: 53M households, NCTA)
- Computer (1984: 8.2% → 1989: 15.0%, Census CPS)
- AC arc (1978→1993)

**1960s room enrichment (5 facts):**
- Median home value ($11,900, Census Historical Housing Tables)
- Number of families (45,540,000, F-8)
- Average family size (3.7, F-8)
- Split combined diffusion into 4 separate facts (TV, telephone, AC, appliances)

| Room | Gaps | Type |
|------|------|------|
| 1910s | 4 | Structural permanent (no surveys before 1947) |
| 1920s | 4 | Structural permanent |
| 1930s | 4 | Structural permanent |
| 1940s | 2 | Wartime permanent (no CEX, wartime controls) |
| 1950s | 1 | Estimate with value (car price) — subagent searching |
| 1990s | 1 | 1 Ramey (permanent, 1992-94 survey excluded by author) |
| 2010s | 1 | Ramey series ends 2005; ATUS is a concept splice (permanent) |
| 2020s | 0 | — |

### Filled this round

- **1900s women's wages**: Tier D → **Tier A**. Source: 1905 Census of Manufactures,
  Part I, page lxxxix. Women $6.17/week, men $11.16/week (55% gap).
- **1900s car price**: Tier D → **Tier C**. Oldsmobile Curved Dash $650 (best-selling
  1901–1904), Ford Model A $750 (1903). Manufacturer list prices.
- **1990s AC**: Tier D placeholder → **Tier A**. RECS 1993: 68% of households had AC.
- **1990s telephone**: Tier D placeholder → **Tier A**. Census 1990: 94.8% of housing
  units had telephone.
- **1990s diffusion split**: 1 combined placeholder → 5 individual facts (AC, telephone,
  cell phone, cable TV, computer). Cell phone/cable/computer remain Tier D with
  sourcing leads in notes.

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

### ~~1900s (2 estimates — could upgrade to Tier A)~~ ✅ FILLED
1. ~~Women's weekly earnings, 1905 ($6.17)~~ → Tier A (1905 Census of Manufactures)
2. ~~New automobile price, 1904 ($750-$1,500)~~ → Tier C (manufacturer records)

### 1910s/1920s/1930s (12 structural permanent)
No consumer expenditure survey existed before 1947. No Census of Housing
before 1940. Income, housing, and food basket gaps are permanent rendered
gaps. Each decade has: income (budget), housing (home), food basket (table).

### 1940s (2 wartime permanent)
No CEX for 1940s. Wartime rationing (1942-46) makes expenditure data
non-representative. Expenditure shares and food basket are permanent gaps.

### 1950s (1 estimate)
Average new car price, 1950 (~$1,511) — could upgrade via NADA or BLS.

### 1990s (1 permanent)
- **Computer**: ✅ Tier A — Census P20-522: 36.6% of households had computers (1997)
- **Internet**: ✅ Tier C — NTIA: ~18% (1997) → ~26% (1998) of households
- **Ramey home production**: permanent (author excluded 1992-94 survey)

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

## Session: 2026-07-07 (continued)

**Added 34 facts, 3 sources** (236→270 facts, 51→54 sources):

### New cross-decade arcs:
- **Poverty rate (1959-2024)**: 6 facts, Census API histpov2. 22.2% (1960) → 12.6% (1970) → 13.0% (1980) → 13.5% (1990) → 11.3% (2000) → 15.1% (2010) → 10.6% (2020)
- **Food prices (1950-2024)**: 6 new facts (1960s-2010s) + 2 existing (1950s, 2020s) = 8 data points. 1960/1970 from 1970 Statistical Abstract Table 530 (OCR'd with Mac Studio parser2). 1980-2010 from BLS API.
- **Heating fuel (1940-2024)**: Filled 1990s gap using RECS 2001 (closest accessible survey). Arc now complete: coal→gas→electric transition across 84 years.
- **Cable TV (1980s-2010s)**: Added 2010s FCC data (53.2M cable subscribers, cord-cutting era)
- **Vehicle ownership**: Added 1970s data point (80.1% had auto, CEX 1972-73)
- **CPI/purchasing power**: Added to 1970s-2010s rooms

### Source registrations:
- `census-poverty-historical`: Census API histpov2 endpoint
- `fcc-video-competition`: FCC Annual Video Competition Report (DA 17-71)
- `statab-food-prices`: 1970 Statistical Abstract Table 530 (BLS retail food prices)

### Gaps closed:
- 1990s heating fuel: filled with RECS 2001 (was inaccessible, now using closest accessible survey)
- Food prices: now have data for every decade 1950-2024

### Remaining gaps (14, all permanent):
- 12 structural pre-1940s (no Census/RECS surveys)
- 2 wartime 1940s (WWII data disruptions)
- These are permanent — data was never collected
