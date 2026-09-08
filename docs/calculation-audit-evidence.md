# Calculation evidence — 2026-09-07

The integrated archive replay checks **97 declared numeric fields: 58 literal
extractions and 39 calculations**. This is selected-field qualification, not
whole-corpus verification or endorsement of every statement in a record.

## Newly qualified families

- CES annual earnings and hours: original BLS response bytes are archived in
  `samples/50-calculation-inputs/`. Each mean names its monthly operands and
  guards the series ID, year and each January–December period. These are newly
  retrieved source vintages; the old extraction script did not preserve its
  input responses. Existing rounded headline figures reproduced.
- CEX budget shares: ratios use the numerator and denominator cells from the
  same archived table, with population/year/header guards and an explicit
  rounding rule. The 1985 and 1996 apparel records remain four-person consumer
  units and now say so. Their source operands were corrected without changing
  the rounded headline shares. The 1996 all-unit expenditure total also gained
  a literal check.
- Four compound wage records now have separate hourly-pay and weekly-hours
  observations for manufacturing and total-private production workers. Existing
  anchor IDs remain stable. Thirteen single-measure records were added.

## Corrections that change the visitor's conclusion

The 2024 weekly-earnings product now uses total-private production and
nonsupervisory hourly earnings and hours from the same worker population:
$30.12 multiplied by 33.7 hours gives $1,015.04 after currency rounding. Under
the explicit fifty-two-paid-week assumption, the family-income benchmark is
49.9 percent. It does not establish household spending needs or earner counts.
The separate manufacturing trend chart retains its own population.

The archived 2024 four-person CEX workbook contains shares of annual national
aggregate expenditures by consumer-unit size, rather than the annual-means
budget table. Its printed income mean also differs from the previous record.
Four unsupported comparisons now retain their stable IDs as verification gaps.
The direct official annual-means download returned HTTP 403; no missing number
was reconstructed from rounded aggregate shares. All-consumer-unit 2024
expenditure evidence remains available and audited.

The AWHMAN registration now identifies CES3000000007 (production-worker hours);
the previously named datatype 06 is an employment-count series. Source notes
and methodological assumptions now distinguish average/proxy worker pay from
median family income. Commercial produce-SKU survey records were down-tiered
from B to C; their recorded values did not change.

## Replay and refresh

`vitrine audit` checks the original bytes and declared operands before replacing
the ledger. The offline gate recomputes ledger calculations and rejects stale
record/source/assumption/method bindings. Calculation details appear on source
collection pages. A failed run leaves the previous ledger intact.

The CES refresh script now retains successful response bytes under filenames
containing their content hashes, validates distinct monthly periods, and emits
only complete calendar years. Request bodies and registration keys are not
saved. This tranche does not repull or replace the whole historical series.

Food-price baskets, other compound records, remaining unclassified audit
coverage, and retrieval of the correct four-person annual-means table remain
research work. Archive absence does not establish historical absence.
