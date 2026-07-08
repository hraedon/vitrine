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

## Filled in the wi-1/us-source-survey merge (2026-07-08)

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
