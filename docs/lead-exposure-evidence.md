# Childhood blood lead: evidence and display contract

Plan 027 WI-7. Source review: 2026-09-12. Baseline: `cc10b444`.

## Selected observation

The exhibit transcribes the **50th percentile (median)** row in the official
[Childstats PHY4.A table](https://www.childstats.gov/americaschildren/tables/phy4a.asp).
The publisher is the Federal Interagency Forum on Child and Family Statistics;
the data source is NCHS's National Health and Nutrition Examination Survey
(NHANES). These are published national estimates for US civilian
noninstitutionalized children ages 1-5, not household records, clinical-screening
samples, or measurements of the same children followed over time.

| Complete sampling period | Published median, micrograms per deciliter |
|---|---:|
| 1976-1980 | 15.0 |
| 1988-1994 | 3.0 |
| 1999-2002 | 1.9 |
| 2003-2006 | 1.6 |
| 2007-2010 | 1.3 |
| 2013-2016 | 0.7 |
| 2017-March 2020 | 0.6 |

The table belongs to [America's Children 2025](https://www.childstats.gov/americaschildren/),
but supplies no separate table publication date. `Source.year = 2025` denotes
that edition. It is not the observation year or a claim about present exposure.
Two independent source reviews checked the statistic, age group, and full
sampling windows. A third integration check read the live official table.

## Measurement boundaries

The [EPA methods document, July 2023](https://www.epa.gov/system/files/documents/2023-07/Biomonitoring-Methods-Lead.1976-2020.pdf)
describes sampling weights, nonresponse, missing measurements, and changing
laboratory detection limits. Its table does **not report** the NHANES II limit;
that is not evidence that no limit existed. Below-detection values and missing
measurements are different conditions. We copy the published percentile estimates
without applying a correction, reconstructing weights, or averaging medians.

The [EPA indicator report](https://www.epa.gov/system/files/documents/2022-04/ace3-lead-updates.pdf),
printed page 5, explains that improved sensitivity does not prevent comparing
medians and upper percentiles because most measurements were detectable. This
supports a descriptive comparison; it does not establish unchanged methods or
statistical significance between adjacent rounded estimates. EPA's separately
published individual-cycle values must not replace this table's pooled periods.

The [NCHS pre-pandemic guidance](https://wwwn.cdc.gov/nchs/nhanes/continuousnhanes/overviewbrief.aspx?Cycle=2017-2020)
explains the last period: incomplete 2019-2020 collection was combined with
2017-2018 using special weights. The endpoint is **2017-March 2020**, not the
whole 2020 cycle. The [youth file documentation](https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2017/DataFiles/P_PBY_R.htm)
also describes harmonized detection limits after a laboratory-method change.
Recent youth microdata require Research Data Center access. This exhibit proves
transcription of a public aggregate table, not independent recomputation of
those microdata.

The selected table has no 2011-2012 column. That omission does not say that
NHANES collected no data during those years. These checkpoints are not annual
observations or decade averages. A national median does not identify an
individual child's exposure, subgroup equality, a clinical outcome, or the
causal effect of a particular regulation. No threshold, intervention chronology,
percentage reduction, or statistical-significance claim is added.

## Repeatable transcription

The existing source archive is
`samples/48-blood-lead/childstats-phy4a-lead-table.html` (untracked).
The archived file and the live response checked on the review date are
byte-identical: 15,293 bytes, SHA-256
`ba0e2353890de464464255873a38e84f833be091bed6e558da6469670d2bf4af`.

Each fact's `text-regex` audit extracts one column of the median row from the
original HTML. Guards bind the complete title/age group, statistic and unit,
source agency, and column header **at the same ordinal position** as the number.
The content fingerprint also binds the authored fact, source population and
notes, and assumptions. Reordering columns, changing the statistic or ages, or
moving a number to a different meaning must fail rather than silently repin.
The source HTML is never committed; neither is a reconstructed table substituted
for the archived evidence.

The archive filename `egan-2021-nhanes-blood-lead-1976-2016.pdf` is misleading:
its bytes are a [CDC LEPAC presentation](https://stacks.cdc.gov/view/cdc/113073/cdc_113073_DS1.pdf),
not the journal article. It reports geometric means and contains inconsistent
endpoint labeling between its prose and figure. It supplies no exhibit values.

## Display contract

All seven facts are retained, including multiple periods in the same archive
decade. Room placement uses the sampling period's starting decade as an
organizational choice; the full period remains in every fact label.

The corridor uses discrete sampling-period marks on an explicitly categorical
axis. Values come only from the facts. There is no connected annual line,
synthetic midpoint year, interpolated period, or zero assigned to unselected
years. The zero baseline and printed precision remain visible. Each mark opens
the actual fact's population, source, notes, and audit status.

The new checkpoint path is separate from annual `Series` and one-fact-per-decade
`Arc` declarations. It still participates in the US comparative-country gate,
fact overlay deck, and rendered-mark validation.

## Verification record

Before editing, the isolated Linux checkout passed Ruff, strict typing, the
provenance gate, and **604 tests with 2 skips**. Implementation qualification
used Linux and Python 3.14.4 on 2026-09-12:

| Check | Result |
|---|---|
| Complete test suite | 651 passed |
| Browser and layout suite after the final CSS adjustment | 75 passed |
| Ruff and configured strict mypy checks | Passed; 47 typed source files |
| Provenance and render coverage | 745 facts, 15 derived facts; all 760 exhibits match the build and every rendered mark resolves |
| Standalone export | Passed with a separate `_export` destination |
| Source audit against the actual archive | 104 passed: 65 literal checks and 39 calculations, including all seven new values |
| Identifier gate | Passed with the configured canonical denylist and no tracked raw source files |
| Source-topic cross-check | No hard errors; the same 75 nonblocking findings as the baseline, with none added or removed |

Browser checks cover desktop (1280), tablet (768) and phone (375) widths under
the production response policy, full-period bounds and nonoverlap, actual
rendered label size, first/last placard clicks and the JavaScript-free route.
Manual inspection of the locally served Linux build checked the same three
widths. The chart scrolls inside its panel when space is limited; the microgram
unit retains its case. Restoring unrelated checkout line endings reproduced
all 237 build files byte for byte. Independent numeric, statistical-meaning and code
reviews found no remaining actionable issue in this slice.

These are branch and artifact checks, not a claim of deployment or hosted CI.
Python 3.13's hosted matrix was not run. The existing Windows CLI import of
`fcntl` prevents a full native Windows build, so no Windows build qualification
is claimed. The old checkouts and production deployment were left in place.
