# Gap Log — curator commentary

**The inventory itself is generated — run `vitrine gaps`.** It classifies,
mechanically, every rendered gap (value = "no reliable record…"), every Tier D
estimate (displayed value awaiting a primary-source upgrade), and every empty
panel, per room. This file carries only what a machine can't know: which source
would fill a gap, and which gaps are structural.

This file used to hand-maintain summary tables. Within a week they had drifted
badly out of sync with the corpus (5 of 13 rooms tracked, 101 of 203 facts
counted, filled gaps still listed as open, and one wrong number — "~55% lacked
complete plumbing in 1940" where the Census table says 45.3%). A hand-kept
summary table drifting from the data it summarizes is this project's founding
observation about everyone else's history content; it does not get to happen
here. Hence `vitrine gaps`.

## Structural gaps (likely permanent)

- **1910s–1930s income, housing, food basket, work-buys.** No consumer
  expenditure survey or Census of Housing before 1940. These are permanent
  rendered gaps — the museum shows them.
- **1940s expenditure and food basket.** No consumer expenditure survey exists
  for the 1940s, and wartime rationing (1942–46) makes what data exists
  non-representative. BLS Bulletin 1055 (1952) covers retail food *prices*
  1939–50 but not household baskets. The 1942 Wartime Consumption Survey is the
  only candidate; treat these as gaps the museum shows, not backlog.
- **Pre-1947 income.** No national family income survey before the CPS series
  (Census P-60, 1947→). The 1910s–1930s income gaps are filled only by proxy
  reconstructions (period cost-of-living surveys, Tier C) or scholarly
  estimates (Tier D) — never by an official median.
- **1990s Ramey home production.** Ramey excluded the 1992-94 survey; no
  benchmark exists for the decade.

## Upgrade paths for standing Tier D estimates

- **1950s new car price ($1,511).** Identified as the Ford Custom price, not
  the overall average. A primary upgrade needs period trade publications or
  NADA historical data.
- **1950s rooms/heating-fuel detail.** The 1950 Census of Housing collected
  rooms and heating fuel; volumes are scanned online, not yet transcribed.
- **1970s/1980s housing detail and TV/AC diffusion.** Census 1970 and AHS 1973+
  data available; not yet transcribed.

## Filled in the 2026-07-08 flagged-issues round

- **1990s cable TV:** Corrected from "~60%" (Tier C, unverified NCTA
  source) to "59.3% of TV households" (Tier A, FCC 97-423 Table B-1).
  The NCTA timeline does not contain year-by-year penetration percentages;
  the FCC report provides exact figures sourced from Nielsen and Kagan.
- **1970s AC:** Verified — the 23% central AC figure is confirmed via EIA
  Annual Energy Review Table 2.6, which republishes 1978 RECS data (Form
  EIA-84) with explicit source attribution. Tier A confirmed. Added total
  AC (56%) and no-AC (44%) breakdown to notes.
- **2000s housing share:** Corrected from 32.2% to 32.3% (rounding of
  32.27% from CEX 2005 Table 4).
- **MANIFEST.md:** Fixed mislabeling of RECS ASCII microdata files — they
  are RECS 1993 (7,111 records), not RECS 2001 (4,822). Confirmed by sample
  size and FUELHEAT coding.
- **nchs-nvss source title:** Updated to reflect coverage of both life
  tables and infant mortality.

- **Week-of-work arc (1940s–2020s):** 8 new derived facts computing weekly
  earnings as % of median family income. Arc shows the end of the single-earner
  era: 92% (1940s) → 95% (1960s) → 83% (1970s) → 60% (1980s) → 49% (2000s)
  → 60% (2020s). All Tier A, derived from existing earnings + income facts.
- **Vehicle ownership arc (1960s–2020s):** 5 new facts from BTS Figure 2-7
  (Census decennial + ACS). 78.5% (1960) → 87.1% (1980) → 88.5% (1990) →
  89.7% (2000) → 90.9% (2010). Joined existing 1970s (CEX) and 2020s (ACS)
  facts for a 7-decade arc.
- **Appliance ownership (1970s, 1980s):** 2 new facts from EIA Annual Energy
  Review Table 8.3. 1978: refrigerator 99.7%, washer 70.5%, dryer 45.0%,
  dishwasher 34.6%, microwave 7.8%. 1980: refrigerator 99.9%, color TV 82.1%,
  washer 71.6%, microwave 14.2%.
- **Median home size (1970s–2010s):** 5 new facts from Census C-25 annual
  reports. New-construction median sq ft: 1,525 (1973) → 1,595 (1980) →
  1,905 (1990) → 2,057 (2000) → 2,169 (2010). Joined existing AHS figure
  (1,500 sq ft existing stock, 2023).
- **Poverty rate arc (1960s–2020s):** 7 facts from Census API histpov2.
- **Food prices arc (1960s–2010s):** 6 facts from Statistical Abstract + BLS API.
- **Heating fuel arc (1940–2024):** Census Historical Housing + RECS + ACS.
- **Cable TV (1980s–2010s):** NCTA + FCC reports.
- **Vehicle ownership (1970s):** CEX 1972-73.
- **AC diffusion (1960s–2010s):** CEX + RECS.
- **CPI/purchasing power (1970s–2010s):** BLS CPI series.
- **Ramey home-production hours (1900s–2020s):** 28 facts, Plan 005 WI-2.
- **1960s diffusion split:** TV, telephone, AC, appliances as separate facts.
- **1900s estimates upgraded:** Women's wages → Tier A (1905 Census of
  Manufactures); car price → Tier C (manufacturer records).

## Naming note

A fact id ending in `-gap` does not make it a rendered gap; classification is
by value and tier, not by name. Several `-gap` ids carry Tier D estimates with
real displayed values and are counted as estimates by `vitrine gaps`.
