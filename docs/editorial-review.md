# Editorial review — 2026-09-07

This pass reviews the two published essays, the strongest framing in the
corridor registry, the single-earner comparison caption, and Plan 027's
remaining research instructions. It narrows interpretation without changing
numbers in those surfaces. The parallel calculation pass separately corrects
the 2024 earnings operands and selected room notes.

## Findings and changes

| Earlier claim | Change | Evidence and reasoning |
|---|---|---|
| One production wage almost carried the median household; its decline explains a move to two earners | Essay and metric describe an annualized earnings-to-income benchmark, not household needs or earner counts | BLS manufacturing series measures average worker earnings; Census F-8 measures median family money income. Multiplying a weekly average by 52 assumes a full year's pay. Neither is an expenditure requirement or a joint household observation. |
| The 2024 room calculation is the chart's endpoint | Essay identifies it as a separate total-private-sector calculation | Chart registry uses `weekly-earnings-manufacturing`; the corrected room calculation uses total-private production/nonsupervisory earnings and hours. These are different worker populations. |
| Married women's participation demonstrates a dual-earner transition caused by wage shortfall | Removed causal and family-composition inference | The registered sources measure participation, not joint spousal employment. Participation includes unemployment. Separate time series cannot identify the proposed cause. |
| A woman in the median household spent the Ramey average on housework | Essay identifies the reconstruction and population averages | Archived Ramey working paper, final column of Table 6 and section IV.A, weights employed and nonemployed prime-age women; it does not select a median-income family. |
| Appliances and changed standards explain where the unpaid-work hours went | Removed the destination and causal story | Ramey's discussion on printed pp. 23–24 raises multiple possible explanations and calls for further research. The museum's adoption and time-use facts do not link the same households. |
| Before CFOI, nobody counted workplace deaths | Explicitly acknowledges earlier estimates and other records | The registered BLS source bounds CFOI's national start at 1992 and the hours-based rates at 2006; neither boundary establishes an absence of earlier records. |
| A small workplace-rate range proves no falling trend | Caption now describes a presentation choice, without claiming a statistical test | The previous test checked only `max-min < 1`, which says nothing about time ordering. That assertion has been removed. |
| NCHS's highest teenage-birth rate is 1960, with an unsupported marital-status explanation | Caption says highest selected point, not annual peak, and does not infer marital status | `nchs-hus-2019-table1` publishes selected years and an age-specific rate; the registration specifies neither a full annual peak nor a marital-status distribution. |
| Four foods were absent from shops before their lines start | Group retitled **Four foods in the national supply** | ERS availability sheets measure supply-side averages. Their first observations do not establish historical absence, distribution across shops, or household intake. |
| Prohibition ended sales and their measurement | Caption reports the source's published gap without asserting zero sales or consumption | NIAAA Report 122 Table 1 prints a Prohibition gap in an apparent-consumption series. |
| Every Wing V topic represents a formerly universal practice now gone | Replaced the selection rule in the public introduction and Plan 027 | Prevalence, legal status, exposure rates, and source coverage are different kinds of evidence. The delivered measures do not meet the original universal claim. |

Other narrowed corridor text removes the unsupported attribution of the
family-size change to a specific cause, distinguishes absent curated cancer
points from absent NCHS records, and labels road deaths per mile as an
aggregate rate rather than individual risk.

## Source checks

- Ramey, *Time Spent in Home Production in the Twentieth-Century United
  States*, [NBER working paper w13985](https://www.nber.org/system/files/working_papers/w13985/w13985.pdf):
  inspected the existing archived text at `samples/14-ramey/w13985.txt`,
  especially the Table 6 discussion, pp. 23–24 discussion of possible causes,
  and summary of women's, men's, and population-weighted estimates. No new
  time-use values were transcribed.
- BLS/Census/NCHS/NIAAA/ERS: checked the existing corpus's registered source
  populations, linked fact definitions, series metadata, and their recorded
  extraction boundaries. This is a semantic comparison of those contracts,
  not a fresh numeric audit of every table.
- [Department of Labor agricultural employment guidance](https://www.dol.gov/general/topic/youthlabor/agriculturalemployment),
  consulted 2026-09-07: age-dependent rules and statutory exemptions contradict
  Plan 027's claim that the FLSA ended all child employment. No legal chronology
  or prevalence fact was added to the museum.
- [IMLS reference-transaction definition](https://www.imls.gov/search-compare-definitions)
  and [2021 Public Libraries Survey documentation](https://www.imls.gov/sites/default/files/2023-06/2021_pls_data_file_documentation.pdf),
  consulted 2026-09-07: the measure counts information consultations, including
  assistance with information sources, rather than exclusively people arriving
  at a physical desk. Plan 027 now requires checking definitions by year before
  constructing a series.

## Revised research boundaries

Plan 027 now records the delivered WI-1 through WI-6 as they actually exist,
and rewrites WI-7 through WI-12 as source-led questions. It no longer promises
that repair establishments collapse, that letters or reference services die,
or that appliance price indexes can directly become hours per refrigerator.
Its child-work item requires census-definition and legal-coverage research;
its smoking-restriction item requires jurisdiction, effective date and scope.

The produce-SKU trade-survey cards have also been moved from Tier B to C,
with source notes explaining that they are commercial period-survey proxies
reported by ERS. Federal republication does not make the underlying survey
official microdata computed by this project. Values and record IDs remain.

## Validation and limits

The focused Linux run passed all 29 existing essay and workplace-death tests.
It checks essay interpolation, source-card coverage, chart inclusion, room
backlinks, and measurement-boundary caveats. Ruff passed on the changed Python
files. Windows pytest cannot collect the site tests because existing
publication code imports Linux `fcntl`; qualification ran in an isolated
Linux checkout. Final whole-project checks cover integration with the parallel
data and presentation edits.

This is not a complete review of every room note, every interpretation in
other registries, or the historical candidate sources for the open work items.
Passing a numeral gate or transcription audit does not validate causation,
representativeness, legal scope, or the social meaning of a measurement.
