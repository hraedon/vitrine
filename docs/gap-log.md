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

## Current curation and source-definition gaps

- **Pre-1960 produce variety** (Plan 027 WI-6, 2026-09-01). ERS's Food
  Availability system has historical summary sheets as well as detailed
  commodity workbooks; the summary sheets can reach earlier years than the
  detailed commodity records. Those are different levels of detail and do not
  by themselves establish a continuous, comparable count of the selected
  produce items. The current room gaps mean that an earlier per-commodity
  series has not been qualified for this comparison; they do not establish
  that ERS published no earlier produce information. See the registered
  primary source `usda-ers-fads` and the selected workbook locators recorded in
  `middle-us-health-food-results.json`.
- **1910s–1930s income, housing, food basket, work-buys.** The current rooms do
  not present a continuous set of decade-specific observations with one
  population and comparable definitions. Historical records do exist: BLS
  Bulletin 49 covers selected wage-earner families; the BLS 1918–19 cost-of-
  living report covers selected locations; the 1935–36 Study of Consumer
  Purchases covers urban and rural families in selected areas; and the 1930
  Census asked about radio ownership. The Census of Housing's 1940 amenity
  series is a separate, later source. These source records do not automatically
  provide a national median, a complete household basket, or every housing
  measure used by the rooms. The gaps mark observations not yet curated and
  qualified for the room's comparison, not a claim that no relevant records
  exist. See registered sources `bls-bulletin-49-1903`,
  `bls-1918-cost-of-living`, `bls-1935-consumer-purchases`, and
  `census-decennial-pubs`.
- **1940s expenditure and food basket.** The current room has no verified full
  household expenditure-share table. BLS Bulletin 1055 covers retail food
  prices for 1939–50; price observations do not constitute a household budget.
  The reviewed record therefore describes a curation gap, not proof that no
  contemporary budget survey exists. See `us-1940s-expenditure-gap` in
  `root-reserved-results.json` and the registered BLS Bulletin 1055 source.
- **Pre-1947 family-income coverage in the current rooms.** The family-income
  series used by the rooms begins with the Census historical family-income
  table's 1947 coverage. Census P-60 No. 5 compares its 1947 family-income
  result with a 1944 figure, so the broader statement that no pre-1947 family-
  income estimate or survey existed is unsupported. Earlier selected surveys
  have their own populations and measures and are not automatically a national
  family median. The gap is that a suitable decade-specific median has not
  been curated and qualified for these rooms, not that pre-1947 income records
  do not exist. See the `us-1910s-income-gap`, `us-1920s-income-gap`, and
  `us-1930s-income-gap` reviews in `early_us-results.json` and registered
  sources `census-hist-income-families` and `census-p60-001`.
- **1990s Ramey home production.** Ramey excluded the 1992-94 survey; no
  benchmark exists for the decade.
- **UK affordability before the 1990s** (FWI-001, 2026-09-01). The current
  affordability view combines selected income, price, earnings, and hours
  inputs; their start dates describe those inputs, not the full record of UK
  statistics. The cited ONS household-income dataset begins in 1977; the
  selected ONS house-price Table 31 begins in 1991; and the selected ASHE median
  hourly-pay series begins in 1997. Other table definitions are not assumed to
  be interchangeable. ONS also publishes a long-run weekly-earnings series
  reaching back to 1938; its earlier years measure adult manual workers, while
  later sections use different surveys.
  Those weekly means are not interchangeable with the selected ASHE median
  hourly measure. Department of Employment year books provide separate hours
  observations. Accordingly, the existing room gaps mark where the current
  inputs have not been matched and qualified for the affordability calculation;
  they are not claims that UK income, wage, price, or hours records were absent.
  See registered sources `ons-etb-household-type`, `ons-hpi-annual-tables`,
  `ons-ashe-table1`, `ons-earnings-1938-2025`,
  `dep-labour-year-book-1969`, and `dep-labour-year-book-1976`.

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

- **Comparable workplace fatality rates before the selected 2006 series.** The
  current source card uses BLS's hours-based full-time-equivalent rate tables
  beginning in 2006. The reviewed CFOI description states that the federal
  program has covered all fifty states and D.C. since 1992, so the gap must not
  be read as absence of federal fatality counts before 2006. Earlier CFOI rate
  tables use an employment denominator, while this selected series uses hours
  worked; they are different measures and are not silently joined in the
  current arc. The rendered gap is for the current comparable rate series, not
  for workplace-death records. See `us-1990s-workplace-death-rate` in
  `recent_us-results.json`, the registered source
  `bls-cfoi-hours-based-rates`, and the archived BLS CFOI survey description
  cited in that review.
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
