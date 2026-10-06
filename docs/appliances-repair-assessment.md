# WI-11 assessment — appliances, prices, and repair

**Status: assessment complete 2026-10-06. No measure entered.** This
document records what the candidate sources actually are, what each can and
cannot support, and what a full acquisition pass would need, so the next
pass starts from evidence rather than recollection. It follows the plan
027 acquisition-state pattern used for the WI-10 measures before they were
entered.

## What the work item asks

> Assess whether available sources support an exhibit about acquisition and
> repair. Candidate measures are appliance price indexes, repair-service
> price indexes, and repair-establishment or employment counts. Verify
> coverage and industry-classification boundaries before comparing them.

The acceptance bars: no promised collapse, crossover, or causal story;
present only what the acquired evidence supports; treat quality dispersion
as an unanswered research question; energy-use and regulatory material only
with compatible product and test-standard definitions; no headline figures
recalled from familiar charts.

## The acquired evidence

All series identities, bases, and coverage windows below were read from
BLS's own public catalogs (`download.bls.gov/pub/time.series/cu/cu.series`
and `.../wp/wp.series`, fetched 2026-10-06) and confirmed live through the
same BLS Public Data API this repository already uses for the CPI series
(`bls-api` source entry, Tier A, M13 annual averages, 10-year chunking).

### Appliance price indexes

- **PPI commodity: Household appliances (WPU124).** 1982=100, not
  seasonally adjusted, monthly coverage January **1947** through the
  present. The long appliance price record: producer (shipment) prices for
  the "Furniture and household durables — Household appliances" commodity
  group. Fetches cleanly through the existing pipeline (a probe returned
  current values at ~152 on the 1982 base). Its seasonally adjusted twin
  (WPS124) ends December 2008; subseries definitions shift inside the group
  (e.g. WPU124104 "Other major household appliances including room
  air-conditioners" exists only 1990-1996), so any entry must carry the
  group-level series and name the base.
- **CPI: Major appliances (CUUR0000SEHK01).** December **1997**=100,
  coverage December 1997 through the present — the retail record begins
  only with the 1997 CPI revision. There is no continuous retail
  major-appliance index before it in the current CPI.
- The familiar chart — appliances falling dramatically in price relative to
  all items — is exactly the window 1997→present in the CPI, or 1947→ in
  the producer index against the WPI/CPI all-items comparator. Either arc
  can be built from fetched values; none of its headline shape may be
  asserted from recollection, and the plan's boundary stands: a price
  *index* measures price change only. It cannot be divided by an hourly
  wage to obtain "hours per refrigerator" without a separately sourced
  price *level* and a defensible product definition, and the wing's
  existing wage series (production-worker earnings) is not such a level.

### Repair-service price indexes

- **CPI: Repair of household items (CUUR0000SEHP04).** December 1997=100,
  coverage December **1997** through October **2025** — the catalog's last
  printed month. The household-repair price record is short and, on the
  catalog's face, ending; any entry must state both.
- The long repair price record is a different object: **CPI: Motor vehicle
  maintenance and repair (CUUR0000SETD)**, 1982-84=100, annual averages
  from **1935**. It supports a vehicles-repair arc but not an
  appliance-repair one, and the two must not be spliced or silently
  compared.
- PPI has no household-appliance repair commodity series; its "Repair and
  maintenance services" indices begin 2017 and cover commercial and
  industrial machinery (a different population).

### Repair-establishment and employment counts

- The classification boundary sits exactly where the question lives: SIC
  76 (Miscellaneous repair services, including radio and television
  repair) governed through 1997; NAICS 811 (repair and maintenance), with
  8114 "Personal and household goods repair and maintenance" as the
  household subset, from 1998. County Business Patterns counts exist on
  both sides but the industries are not comparable across the 1997/98
  break — a count of SIC-76 shops and a count of NAICS-8114 shops answer
  different questions, and neither measures household repair *behaviour*.
- The Statistical Abstract's "Selected service industries" tables (the
  1985 edition's contents points one at its Domestic Trade section) are a
  lead for SIC-era counts and would need their own page-located,
  eye-transcribed pass — the same discipline as the WI-10 postal tables —
  before any pre-1998 count could be entered.

## What an exhibit could and could not say

Could say, on this evidence, with the boundaries carried on the cards:

- A producer-price arc for household appliances, 1947→, Tier A, from
  fetched WPU124 annual averages — presented as price change alone.
- A retail major-appliances arc from 1997 (CPI), clearly dated by its own
  base, so the visitor sees that the retail record is short rather than
  reading the short arc as the whole history.
- A household-item repair price arc, 1997→October 2025, with the
  record's end stated on the card.

Could not say, on this evidence:

- "Hours of work to afford a refrigerator" (no sourced price level; the
  plan forbids the computation without one).
- Any collapse/crossover/causal story about repair culture — the price
  indexes measure prices; the establishment counts measure industries; and
  the classification break at 1997/98 falls in the middle of the period the
  story would be about.
- Anything about quality dispersion — it stays an unanswered research
  question per the acceptance.

## Recommendation

A narrow exhibit is supportable: the WPU124 producer-price arc (1947→) as
its spine, with the 1997-based CPI arcs (appliances retail, household-item
repair) as clearly-dated short companions if the editorial review wants the
repair comparison at all. Before entry the next pass needs: (1) the full
BLS API acquisition (M13 annual averages, the `bls_cpi_components_extract.py`
convention), (2) a source note naming each series ID, base, and the
SEHP04 end-of-record, (3) the standing gap/absence discipline at 1997
where the two bases meet, and (4) the usual qualification chain. The
SIC-era establishment counts are a separate, larger acquisition (scan
tables) and should not gate the price exhibit.
