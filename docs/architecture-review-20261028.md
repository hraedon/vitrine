# Architecture and source review handoff — 28 October 2026

This records implementation evidence and a bounded peer review. It is not
formal workflow acceptance or a claim that the whole corpus is correct.
The second architecture tranche started at `a306998`; the original main
checkout was preserved. Qualification used the isolated Linux candidate
and native Windows Python, with explicit candidate import paths on Linux.

## Monetary rates: representation changes, observations preserved

The three earnings series already stored annual means in major USD with
four-decimal precision. Currency appeared only in their prose units because
the earlier model prohibited currency metadata beside float observations.
Rounding those means into integer cents would change the evidence.

The delivered model distinguishes quantities, integer minor-unit monetary
amounts and major-unit monetary rates through the closed `SeriesKind` set.
Rate authoring explicitly declares `kind = "monetary_rate"`, a registered
currency and an hourly, weekly, monthly or annual basis. `total` is invalid.
The normalized kind derives from storage and rate metadata; representation
validation refuses empty or mixed maps and contradictory metadata before
numeric projection or export. It also refuses nonfinite observations and
numeric-year aliases that would overwrite the same annual observation.

The following before/after proof compared each current `values` table with
the corresponding table at `a306998`, requiring exact numeric-map equality.
Hashes use UTF-8 JSON with sorted keys and compact separators.

| Series | Annual observations | Unchanged numeric-map SHA256 |
|---|---:|---|
| Manufacturing hourly earnings | 86 | `fcd316602440d0c5bbf4418d00902c3ee362f67dd68f63ed82f594c99d3a23fe` |
| Total-private hourly earnings | 61 | `7169af1414fac0b3fe403fe9a365b719804032fcf15a50750ec9c9631c8c2a39` |
| Manufacturing weekly earnings | 86 | `e3f13b8e830031476e0a42c16304a43958cb713281a71c2729db8940555de663` |

All five dashboard metric result maps also compared exactly equal to the
pre-tranche arithmetic. Re-running the FRED extractor against the archived
original workbook reproduced every existing annual mean. That extractor now
requires distinct January–December observations rather than counting rows;
a duplicate month cannot stand in for a missing month. Both earnings
generators preserve the rate declarations and subcent precision.

Metric chains and splices reject currency or time-basis conflicts. Inflation
and threshold-count derivations reject monetary rates, including direct
evaluator calls. Rate/fact drift comparison requires matching currency and
time basis, uses the currency registry's minor-unit scale, and allows only
display-rounding tolerance. Tests include GBP and JPY, rather than assuming
every minor-unit scale is one hundred.

JSON export schema 2 exposes `kind` and nullable `rate_basis`. Rates remain
major-unit values and must not acquire a second minor-unit scaling step.
This changes the version-1 convention, so the schema was bumped explicitly;
fact and CSV projections retain their prior semantics. See
[the consumer contract](export-schema.md) for migration details.

Targeted qualification at this handoff passed 158 Linux tests, strict mypy
over all source modules, scoped Ruff, and the provenance gate. A native
Windows selection covering rates, series, derivations, exports and both
earnings generators passed 120 tests. These are scoped results; the primary
reviewer owns the combined final suite and publication checks.

## Independent review of the source tranche

The review inspected the original FIES and ASHE workbooks, the extraction
code, its pinned artifact and its archive-backed tests. The selected FIES
income, consumption and food columns match their original headings, years
and yen units. The agricultural, forestry and fisheries exclusion applies
to the archived long-run tables: their English notes at rows 81/82 confirm
it. The review did not infer population coverage from the modern survey's
general scope.

Original ASHE tables for the selected years confirm the all-employee median
column in hourly-pay table 1.5a and total-hours table 1.9a. The XLS reader
checks BIFF formula records before accepting xlrd's cached numeric result.
Its union of formula coordinates across sheets is deliberately conservative:
it may refuse an unrelated coordinate but cannot silently accept that cache.
Tests also refuse a real formula coordinate in the original FIES workbook.

The modern BLS food-price qualification binds item identity and units to
pinned BLS-sourced FRED metadata, and numbers to original BLS response bytes.
It requires the intended December and year, rejects duplicate or missing
series, and applies explicit half-up rounding to cents. Its 26-price check
does not pretend to add 26 single-field audit bindings to compound placards.

Historical package-unit corrections remove false per-pound and per-quart
comparisons. This review found one remaining contradiction: the corrected
April 1970 milk value said half-gallon while its unit still said quart.
The source reviewer corrected the unit and added a regression. Round steak
and ground chuck are now treated as different products.

The NFS extractor uses the inspected annual consumption cells rather than
damaged quarterly or purchases readings. Records retain the report's
food-entering-the-home definition, geographical exclusions and original
units. The primary reviewer separately inspected the page image. This
review inspected the extraction/guard logic and reproduced the artifact
from the original PDF; it did not substitute OCR for that visual check.

Twenty source-tranche tests passed on Linux, including original workbook
and PDF reproduction and modern compound-price qualification. No further
blocker was found in these scoped changes and selected facts. Interpretive
claims elsewhere in these documents were not exhaustively re-researched.

## Additional mortality verification and direct audit bindings

The existing historical heart disease, cancer and stroke quantities were
checked against the publisher's original aggregate CSV. All fifteen matched.
The source has only `Year`, `Cause` and `Age Adjusted Death Rate` columns;
there are no sex/race columns to guard. The new direct CSV-cell audit
references bind the row's year and cause and all three header cells. The
provenance reviewer owns the combined ledger replay; this reviewer did not
write or replace the audit ledger.

Representative independent checks are CSV row 52, heart disease in 1950
at 588.8; row 211, cancer in 1990 at 216.0; and row 429, stroke in 1970 at
147.7. The primary reviewer independently read those same original rows.
Five focused tests reproduce all fifteen rates and show that changing a
year, cause or rate heading fails while the numerical value stays fixed.

Original bytes are retained in gitignored `samples/60-mortality-review/`:

| Original publisher response | SHA256 |
|---|---|
| Aggregate CSV, 13,738 bytes and 595 published annual observations | `867d39e039b9ecb9843be3e8b3473250fec03050dc62d7d4409c1f737b731160` |
| Dataset metadata JSON | `0dbffadc05f79f0b431578c8deb1e7e378349b58b9bfe3eaa24d13aeb6680942` |
| HIST293 historical definitions HTML | `cb2d94ee7fcb5ab92a0f5f7ea55ad0c66014e355a3ab0da2fc065a83b03c1e04` |

The [dataset CSV](https://data.cdc.gov/api/views/6rkc-nb2q/rows.csv?accessType=DOWNLOAD)
contains published aggregates, not individual death records. Its
[metadata](https://data.cdc.gov/api/views/6rkc-nb2q.json) links the historical
definitions. [HIST293](https://www.cdc.gov/nchs/nvss/mortality/hist293.htm)
explains that the historical tables were calculated using the year 2000
standard population too. Do not invent a change of standard at the 1999
boundary in these particular historical values. ICD revisions can create
comparability breaks. Coverage before 1933 was a changing set of Death
Registration States; the selected room facts all start after that boundary.

This sample also found an incorrect comparison in the 2024 life-expectancy
note. [Data Brief 548, Table 1](https://www.cdc.gov/nchs/products/databriefs/db548.htm)
gives 78.4 in 2023 and 79.0 in 2024, an increase of 0.6; the note had said
78.6 and 0.4. The source reviewer corrected the note against the archived
original. The headline and sex-specific values already matched.

Field audits do not establish every medical explanation, causal account or
historical superlative in nearby prose. This review verified the stated
source fields and corrected the demonstrated note error; that is the scope
of its no-further-blocker conclusion.

## Final continuation pass

A fresh core review found two additional gate inconsistencies. A zero base
in an inflation index passed the provenance gate even though evaluation
correctly refused division by zero. The gate now rejects it; a zero target
remains a defined ratio. Monetary-amount drift checks also now reject a
fact/series currency mismatch even when the two minor-unit numerals happen
to be equal. Neither change modifies a source observation.

The 1972–73 CEX review independently followed the original four-person
column on the archived page. A damaged OCR token in an unrelated later
column initially caused the strict extractor to stop. The source reviewer
limited selection to the validated all-family through four-person prefix.
This pass then demonstrated that searching for the first well-formed decimal
could skip a damaged leading cell and shift that prefix. The final extractor
anchors the first numeric/currency character before validating the tokens;
its full-row regression rejects that demonstrated shift. The original
selected food categories reproduce, while an unverified budget denominator
remains withdrawn rather than spliced into a comparison.

Final scoped Linux results were 125 passing tests covering the core rate,
series, derivation, export, architecture and CEX paths, plus two passing real
publication-process tests. Four Windows-only publication cases were skipped
on Linux. Full Ruff and strict mypy over all source modules passed. The
legacy-console whole-build test awaits the primary reviewer's combined
ledger/full-suite run. No further concrete blocker was found in this scoped
pass; the core files were declared stable for integration testing.
