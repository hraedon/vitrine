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
- **UK affordability before the 1990s** (FWI-001, 2026-09-01). The UK axis is
  built from three ingredients, and each has a hard start date in the record:
  household income begins with the ONS taxes-and-benefits series in **1977**;
  official house prices begin in **1986** (Table 28) / **1991** (Table 31); and
  an hourly wage in whole pence begins with **ASHE in 1997**. Hours are the
  exception, reaching back to 1965 in the Department of Employment's Year Books.
  So: the 1990s–2010s rooms compute both axes; the 1970s and 1980s carry an
  income anchor with nothing yet priced against it; the 1960s has hours only;
  and the 1950s has none of the three. These are boundaries in what the UK
  published, not a transcription backlog — with two exceptions worth naming as
  backlog rather than structure: (a) the 1970s hourly wage *exists* (166.6p,
  April 1976) but cannot be an anchor while the money layer holds whole pence
  only; (b) a pre-1986 UK house price exists in the Nationwide lender index,
  which would let the 1970s and 1980s rooms compute a share-of-income axis at
  the cost of citing a non-official series. Both are decisions, not absences.

- **Alcohol consumption, 1920–1933.** National Prohibition. The NIAAA
  surveillance series is built from legal beverage sales, so when legal sales
  ended the measurement ended with them — the source table prints the word
  "(Prohibition)" where fourteen years of numbers would be. This is not an
  archive-access limitation and has no upgrade path within the series: it is
  the record's actual shape, and it is the exhibit. A consumption
  *reconstruction* for those years (Warburton and successors) exists in the
  scholarly literature and could be entered, but only as a separate Tier C/D
  fact carrying its estimation method on the card — never as a value on this
  series (Plan 027 D2).
- **Alcohol consumption before 1934.** The same table publishes the pre-
  Prohibition record as five-year ranges (1871–1880, …, 1916–1919), not single
  years, plus three isolated single years 1850/1860/1870. The 1900s and 1910s
  rooms carry the two ranges that fall wholly inside them and name the range on
  the card; the annual series begins at 1934 because a range cannot be keyed to
  a year without inventing a datum. Not fillable from this source at any tier.

- **Workplace deaths before 2006.** Structural, and now rendered. The Census
  of Fatal Occupational Injuries has covered all fifty states only since 1992,
  so for the nine decades before that no federal count of people killed at work
  exists; and the rates CFOI published from 1992 to 2005 were computed against
  employment rather than hours worked, a basis BLS replaced in 2006, so they
  measure something else and are not chained on. The 1990s room carries the gap
  card. The century-long figures usually quoted for this measure come from the
  National Safety Council's *Injury Facts*, a commercial publication rather
  than a government census; buying it would fill the arc but at Tier B or
  lower, and with an estimation method that would need its own card.
- **Road deaths before 1976 are counted differently.** FHWA footnote (3): from
  1976 the count includes only people who died within 30 days of the crash.
  Earlier years used a wider window. Not fillable and not correctable; it is
  disclosed on the arc instead.

- **Teen birth rates before 1950, and between NCHS's printed rows.** The
  published trend table starts at 1950 and prints selected years, not annual
  ones, so the museum carries no card before the 1950s and the arc connects
  published rows. The commonly-quoted 1957 peak (~96 per 1,000) is not in this
  table and is not carried anywhere; filling it would need the annual natality
  volumes, which are not in the archive.

## Upgrade paths for standing Tier D estimates

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
