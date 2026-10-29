# Remaining-record source audit — 2026-10-28

The audit covers the **561 records without field bindings at `f58b808`**:
92 early U.S., 190 mid-century U.S., 193 recent U.S., and 86 UK/Japan records.
Terra and Luna agents read the primary archive, acquired additional originals,
and independently revisited the records that initially had limited checks.
The existing data methodology, source populations and composite disclaimer
remain the governing rules.

Every queued ID has a disposition. The final inventory has **no pending,
unresolved or partial review status**. It distinguishes 502 source-reviewed
records, 42 reviewed curation gaps, 13 records now computed in code, and four
records needing specific evidence. These are review dispositions, not a claim
that every source or statistical method has been independently validated.

The committed [record inventory](audits/20261028-remaining-records.json) retains
baseline membership, review scopes, source paths and hashes, table/cell/page
locators, historical findings and current fingerprints. Earlier findings are
history; they are not automatically defects remaining in the current corpus.
Its offline check is now part of CI:

```sh
python scripts/record_review_report.py --check
```

This command needs no private source archive or reviewer handoff files. It
checks the exact baseline ID set, retained scopes and current model bindings;
it does not reread the original documents or certify their meaning.

## Corrections that affect interpretation

- **Prices and wages:** factory sales and aggregate wholesale values are not
  retail car prices. Unsupported early per-car amounts were removed, including
  hidden fields that could still feed affordability. The retained Oldsmobile
  observation now uses the source's “cost” wording and actual model year.
  Six later car-price observations use the total current-dollar column of
  ORNL Edition 39, with its exclusion of pickups, vans and SUVs.
- **Manufacturing reconstruction:** Historical Statistics D765–766 combines
  union scales and selected payroll occupations, with backward extrapolation
  and an upward-bias warning. Its four early records now disclose those limits
  and use Tier D. Affordability inherits that weaker input tier.
- **Household equipment and housing:** telephone instruments per population
  cannot supply household adoption percentages. Private bath/toilet measures
  cannot silently become modern complete plumbing. Vehicle complements now
  express access rather than absence on the access axis. The national new-home
  air-conditioning figure is distinguished from a neighboring regional column.
- **Energy:** the RECS table distinguishes households from buildings. The
  household expenditure record no longer uses a per-building amount or count.
  Heating and cooling comparisons retain table-specific populations and
  equipment definitions.
- **Health:** historical female life-expectancy cells, teen birth-rate columns
  and mortality vintages were corrected. A per-100,000 infant-mortality measure
  is excluded from the per-1,000 axis. Relative cancer survival is distinguished
  from observed survival and from changing registry populations. Unsupported
  treatment explanations, historical percentage comparisons and peak claims
  were removed from mortality notes.
- **Budgets and food:** the CMS qualifier reproduces whole compound placards,
  uses the actual endpoints of its GDP comparison, and preserves a publisher
  dash rather than inventing zero. CEX observations retain consumer-unit size,
  survey population and denominator; withdrawn shares remain linked gaps.
  Food prices retain their item definitions, package units, month and declared
  cent rounding. The Census poverty records distinguish people in families
  from family units.
- **Media and surveys:** FCC source cards distinguish TV-household penetration,
  MVPD subscribers and Nielsen DVR estimates. A conflicting publisher percentage
  is identified separately from its subscriber table, without inventing a
  reconciliation. ALA analysis of NHIS microdata is attributed to ALA and tiered
  accordingly. The unsupported “first below” smoking milestone was removed.
- **UK and Japan:** rental categories, worker populations, survey dates,
  durable-goods ownership versus unit growth, and licence counts versus
  household penetration retain their actual definitions. Newly located reports
  are described as curation opportunities rather than proof that older gap
  statements were historically true.

Chart exclusions propagate to corridor comparisons, direct metrics, pairs,
walkthroughs and room stages. Their records remain accessible. Room openings
now select source records where a former authored ratio has become a derived
exhibit. Gap banners and the gap log describe what is unverified or uncurated,
rather than claiming that no historical survey exists. Undated publications
render as “undated” on citation surfaces.

## Reproducible arithmetic and coverage

The ledger now has **390 current field bindings: 290 literal extractions and
100 calculation replays**, up from 221. All previous bound IDs remain present;
unchanged entries retain their audit dates. These counts describe specific
numeric fields, not whole-record certification. Compound qualifiers separately
check additional amounts, percentages, units and source headings.

The audit adds exact ratio and rounding operations. The sub-cent historical
wage remains visible at source precision; its existing cent-based affordability
anchor now has an explicit replayed rounding method. The build also rejects a
hidden monetary amount unless its currency-marked amount is displayed, or a
valid rounding audit supplies the displayed original operand. This prevents
an unrelated year from satisfying monetary visibility. It remains an editorial
responsibility to establish that a visible amount has the claimed economic
meaning.

The annual food-availability generator was also reconciled with its two pinned
publisher workbooks: **2,810 selected cells in 54 series**, comprising 2,790
formula/cache replays and 20 published literal values. Every series retains
its selected year window, source-cell precision and population definition.
Marketing periods and population reference dates remain explicit. These are
availability estimates, not intake or a matched household basket.

The existing inclusive one-pound count rule now uses the printed estimates,
not hidden cached digits. Raspberries in 2020 print as 1.0 at the source's
one-decimal precision; the old extra-precision value was 0.97. Consequently
the computed count becomes **42 of 52**, while the other decade counts stay
unchanged. The assumption explains near-threshold rounding and the selected
source-year windows. No number was adjusted by feel.

The final corpus retains **798 exhibit IDs**: 770 Facts and 28 DerivedFacts,
across 27 rooms. It has 169 source registrations, 30 assumptions, 78 series
and three essays. There are 75 explicit gaps and ten non-gap Tier D estimates.
See the [generated field-coverage report](transcription-audit-coverage.md).

## Acquisitions and remaining evidence

Additional originals include the full Federal Reserve release, ORNL car-price
tables, Census API responses, BLS published responses, CEX tables, RECS/AHS
tables, public-library and USPS releases, the ACS cancer report and the cable
history timeline. The Fed release restores the previously unavailable 1950
aggregate net-worth observation; selected quarter-end rows reproduce assets
less liabilities. These are household-plus-nonprofit sector stocks, not median
family wealth.

The primary archive remains under `/projects/vitrine/samples` on `mvmcc02`.
New review material is indexed by the committed inventory's samples-relative
paths, mostly under `remaining-audit-20261028/`. Raw documents, microdata and
credentials are excluded from Git. Hash checks establish byte identity, not
source interpretation. Some hashes were first observed during consolidation;
the inventory does not misrepresent those as original reviewer pins.

The [byte-check snapshot](audits/20261028-evidence-byte-checks.json) records
209 distinct local files across 1,009 check instances: 880 matched a reported
pin and 129 had their hash observed at consolidation without a reported pin.
There were no missing files or hash mismatches. The one URL-only item is
identified below.

Two requests could resolve the four remaining evidence needs:

1. **The original IPUMS family-income analysis code and aggregate outputs.**
   The owner's lead located extract 00001 metadata in
   `/home/itadmin/vitrine/samples` on `mvmhermes01`, outside the general research
   folder. Only its XML/codebook/setup metadata was copied; no raw records were
   opened or copied. The extract contains personal income but not FTOTINC or
   SLWT. Its census observation concerns prior-calendar-year income, and its
   geography codes do not substantiate the former metro/suburban selections.
   No original aggregation code or aggregate output was found. The three
   medians and their dependent difference remain gaps. A new income method
   would require a separate documented design and authorized extract; it would
   not retrospectively prove the withdrawn estimates.
2. **The actual BLS report/table behind the former housing-budget claim.**
   The 1950s “11%” assertion lacks a traceable survey cell, sample, housing
   definition and expenditure denominator. The secondary guide does not
   establish it, so the record remains a gap.

One archival limitation remains separate from those needs: the BLS rate-method
page was read through the official web source, but raw download is blocked
without a contact-address User-Agent. No contact address was supplied. Its
URL-only evidence and the link check's limitation remain explicit.

## Validation

The integrated candidate passed:

- Linux Python 3.13 and 3.14: **1,101 tests and 67 subtests on each**, including
  the browser/layout suite; four Windows-only cases skip on Linux.
- Native Windows Python 3.13: **964 tests and 53 subtests**, with 65 optional
  archive/platform skips; the browser/layout files are covered by Linux.
- Native Windows Python 3.14 core/publication matrix: **241 tests**, nine
  optional archive skips.
- All 390 original-source field replays, the 54-series source replay,
  strict mypy, full Ruff, offline inventory checks, standalone export,
  corpus validation, and actual rendered-row/mark coverage. All **798 exhibits**
  match the build; every chart mark resolves to a curated fact.
- All **292 generated files are byte-identical on Windows and Linux**.
- The canonical private identifier scan passes on the complete staged tree.
  Source-topic checks report no hard errors; the reviewed advisories concern
  source lineage/comparison mentions, brief F-8 notes and disclosed Tier D inputs.

The XLSX parser reports the publisher workbook's missing default style; it
does not affect values or replay. No deployment, publication change or
microdata redistribution is part of this work. The original main checkout
remains unchanged; the isolated review branch holds the implementation.
