# Changelog

## 2026-07-08 — Plan 008 Phase 1-2 (verification and gap filling)

### Corrections (4 facts fixed)

1. **`us-1920s-home-production-components`** (WI-1): Value had 1965 AHTUS column values instead of 1920s Wilson Study values. Fixed: food prep 16.5→19.9, house cleaning 9.5→9.3, clothing care 6.9→11.5, childcare 8.5→7.2, purchasing 4.4 (was 10.4). Total 51.8→52.4. Notes updated with explicit 1965 comparison values.

2. **`us-1970s-food-prices`** (WI-4): Round steak 134¢→133¢ (table value 133.3, rounds to 133 not 134). Milk 66.5¢→65.5¢ (off by 1¢). Notes updated: round steak +27%→+26%, milk +156%→+152%.

3. **`us-1980s-cable-tv`** (WI-6): "53 million households (≈57%)" → "More than 52 million cable customers (50.5% penetration, 1988)". NCTA source says "more than 52 million" and "50.5 percent," not 53M/57%. Label changed from "Cable TV, 1989" to "Cable TV, 1988-1989" to reflect mixed-year data.

4. **`us-1970s-vehicle-ownership`** (WI-6): Income breakdown in notes corrected. Under $3,000: 47.3%→38.3% (was row-confusion error). $15,000+: 94.3%→~96.6% (composite of three top income brackets). Source reference corrected from "Table 1, p.31" to "Bulletin 1992, Table 1, p.31".

### Notes updates (3 facts)

5. **`us-1990s-cable-tv`** (WI-6): Notes updated to acknowledge that the 60% penetration figure for 1992 could not be directly verified against the NCTA Cable History Timeline PDF. The figure is consistent with the trend but is not stated in the cited primary source.

6. **`us-1970s-infant-mortality`** (WI-7, adversarial review fix): Decline percentage corrected from 35% to 37% (actual: (20.0-12.6)/20.0 = 37%).

7. **Source registry `ncts-nvss`**: Notes updated to include infant mortality data from Health, United States, 2016, Table 11, with URL.

8. **Source registry `ncta-cable-history`**: Notes corrected. "1989: 53M" → "1989: more than 52M, 9,050 systems". "1997: 66.7M" → "1999: 66.7M". Added "1992: ~60% (not directly stated in NCTA timeline)".

### New facts (7 added)

9. **Infant mortality arc** (WI-7): Added `us-{1950s,1960s,1970s,1980s,1990s,2000s,2010s}-infant-mortality` facts. Source: nchs-nvss, Tier A. Values from NCHS Health, United States, 2016, Table 11. Completes the infant mortality arc from ~100 (1900s) through 5.6 (2020s).

### Verification summary

- **WI-1** (Ramey): 27 of 28 verified, 1 corrected (1920s components column swap)
- **WI-2** (Heating fuel): All 7 verified against Census/RECS/EIA sources
- **WI-3** (AC diffusion): 6 of 7 verified, 1 unable to verify (1978 RECS not accessible)
- **WI-4** (Food prices): All 5 items for 1960s verified, 2 of 5 for 1970s corrected
- **WI-5** (CEX shares): All 10 verified, 0 corrected
- **WI-6** (Cable/vehicle): 3 of 6 verified, 2 corrected, 1 unable to verify
- **WI-7** (Infant mortality): All 7 new facts verified against NCHS Table 11
- **WI-9** (1950s car price): Upgraded from Tier D to Tier C. Found primary-source wholesale value in Statistical Abstract 1953, Table 615: 6.666M passenger cars at $8.633B wholesale = ~$1,295/car. Source changed from umizzou-prices-wages to statab-food-prices. Zero Tier D estimates remain in the corpus.

Total: 278 facts (271 existing + 7 new), 56 sources, 2 derived. Build gate, tests, ruff, mypy all pass.

### MANIFEST.md note

`samples/10-recs/file2_asc.txt` through `file12_asc.txt` are RECS **1993** microdata (7,111 sample), not RECS 2001 as labeled. The sample size matches the RECS 1993 survey, not RECS 2001 (4,822 households).
