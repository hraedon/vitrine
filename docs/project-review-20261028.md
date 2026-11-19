# Project review — 28 October 2026

Vitrine's strongest asset is its explicit separation of evidence, population,
calculation and presentation. Preserve that architecture. The most useful
next investment is improving the evidence behind existing exhibits and making
those exhibits easier to enter, before adding more countries or illustrated
households. The review found actual transcription and interpretation errors
despite a green baseline gate; attractive framing needs the same scrutiny as
numeric fields.

## Scope

The initial tranche was saved at `a306998`. The subsequent owner request to
continue prompted another source, reading and architecture pass. Historical
counts below describe that first tranche; the continuation section records
their disposition and the combined qualification.

Three independent agents reviewed source provenance, visitor experience and
architecture, followed by implementation and integration review. The local
Windows checkout and `/projects/vitrine` on `mvmcc02` both started at
`f487ecf`. The latter holds the approximately 4.7 GB primary-source archive.
Qualification used an isolated Linux checkout at
`/projects/vitrine-review-20261028`, with the existing archive available.
The original main checkout's tracked files were preserved.

This is a risk-based review, not a claim that every source, number, historical
assertion or browser state was independently checked. Evidence details are in
[the source review](provenance-review-20261028.md) and
[the experience review](experience-review-20261028.md).

## Findings and delivered changes

| Priority | Finding | Delivered response |
|---|---|---|
| High | The UK 1953 tenure record used the 1939 private/social rental split; owner-occupation was identical in both years, concealing the error from a headline-only check. | Corrected private/social renting to the source's 50/18 percent and corrected the subsequent comparison. Added year, heading and companion-column guards to all seven UK tenure audits. |
| High | The render-coverage gate trusted an orchestrator-written manifest even when a template omitted a record. | Independently parse canonical room rows and require every authored/derived record exactly once in its own room. Missing pages, borrowed rows and duplicates fail. Restoring the old function makes all six new regressions fail. This checks row presence, not complete semantic or visual equivalence. |
| Medium | Annual affordability polylines bridged unobserved years while captions said those gaps were not interpolated. | Split lines into consecutive-year runs. Retain observed dots, including isolated checkpoints. Tests cover synthetic gaps and the actual home/car series. |
| Medium | The numeric transcription gate accepted a quantity as a substring of a different displayed number. | Included the independently reviewed complete-token fix from draft PR 28, preserving its deliberately narrow spelling vocabulary. No data changed to accommodate the gate. |
| Medium | Japan notes confused growth in appliance units with growth in household ownership; broadband availability had the wrong observation date and survey attribution. | Corrected the equipment explanations and March 2014 availability date against the original publisher PDFs. Kept the existing headline quantities. |
| Medium | A US TV note called 2.58 to 2.60 hours a decline and attributed participation change to streaming. | State the distinct observed participation and whole-population duration measures; remove unsupported causation and a claimed historical maximum. |
| Medium | UK story questions implied a matched national household, near-universal television access from licence counts, and a reversed home-versus-telephone comparison. | Rewrote all seven openings around their actual records and populations. Licence records no longer claim ownership percentages or causal take-up histories. |
| Medium | Series admitted nonfinite values; annual metrics silently accepted conflicting declared currencies and overwrote overlapping denominator years. | Reject NaN/infinity at load and validation; fail conflicting currency metadata; return an explicit ambiguity diagnostic for overlapping denominator chains. |
| Medium | UK facts had no current field-audit bindings, despite the wing's enrollment. | Added thirty bindings to original ONS income, equipment and tenure files. CSV extraction now handles the original tenure file's CR-only line endings, with a regression test. |
| Medium | Visitors met a long methods/count preamble before any country entrance; the newly curated UK wing still had a developing-collection introduction. | Compact country entrance cards, a featured UK room, native decade disclosures and an optional reading guide. The complete composite disclaimer, inventory, source access and no-JavaScript route remain. |
| Low | Country-enrollment documentation contradicted the implemented curated/comparative split. | Included the guidance correction from draft PR 27. Comparative surfaces remain US-only; Japan's separate pilot PR was not included in this tranche. |

The baseline full suite passed **794 tests and 67 subtests** with the archive
available. Its success did not establish the source correctness of every
compound value or note. The findings above are why that distinction matters.

## New acquisition and bounded corpus expansion

The review acquired the official
[English Housing Survey Homes 2011](https://www.gov.uk/government/statistics/english-housing-survey-2011-homes-report),
its errata and chapter one/four annex workbooks. Two separately reviewed
observations now describe mean dwelling floor area and boiler-fed radiator
central heating. Their population is all dwellings in England, including
vacancies; neither is a UK-wide household or median-family estimate.

The floor-area definition follows the errata, including integral garages and
balconies. The record states its mean, observation period and limited
comparability with other measures. The heating definition explicitly excludes
other heating-system types. The existing housing-gap id remains available
and now names the untranscribed room-count and bath/WC fields.

`python scripts/uk_housing_extract.py --download` is the repeatable acquisition
and extraction path. Original report bytes are pinned; a source change requires
inspection instead of silent replacement. Raw PDFs/XLS files and extraction
artifacts stay in gitignored `samples/`. No IPUMS microdata or API credentials
were needed. The two new bindings target an explicitly identified extraction
artifact; archive-backed testing reproduces it from both original PDFs.

The corpus now has **780 authored facts and 16 derived exhibits**, with
**161 current field-audit bindings** versus 129 before this work. The thirty
new ONS bindings read publisher files directly; the two EHS bindings read the
reproducible extraction artifact. All original audit dates are preserved for
unchanged entries. **619 authored records still lack a current field binding**;
that is unclassified verification coverage, not a count of incorrect records.

UK food reports for the seventies and eighties were already in the archive.
Their gap notes now acknowledge an uncompleted transcription task, and the
source-review document gives precise consumption/expenditure/price table
locations. The presence of a report alone does not justify filling a basket.

## Design judgment

Keep the folio identity and provenance in each record's reading line. The
problem was entry hierarchy and explanatory claims, not a need for a different
framework or a decorative reconstruction. A country should present an
interesting, defensible route before asking visitors to examine its inventory.
Research depth can remain available behind native disclosures without making
methodological distinctions optional inside the exhibits themselves.

The country directory moved from 1,517 to approximately 471 pixels down a
375-pixel mobile viewport, and from 824 to 346 pixels on desktop. These are
local Chromium layout measurements, not usability-study results. The next UI
experiment should address long room inventories and mobile chart reading,
preserving stable record links and complete source access.

## First-tranche leads and their continuation

| Initial lead | Continuation result |
|---|---|
| Compound food baskets, interpretive notes, Japanese budgets and UK earnings/house prices needed deeper source review. | Re-read original PDFs/workbooks and acquired pinned publisher responses. Corrected product rows, package units, population labels, missing cells and unsupported budget arithmetic; added bindings and repeatable compound checks. |
| Float earnings rates lacked explicit monetary dimensions. | Added typed currency/rate-basis representation and schema two while preserving all annual values. Splices and derivations refuse incompatible dimensions. |
| Room inventories and phone charts were difficult to enter. | Native topic disclosures preserve direct record links and no-script reading/printing; source-linked tables accompany charts. Calculated source records disclose their method and field-coverage limit. |
| A label appeared to collide with the decade axis. | Reproduced and corrected the zero-value label placement, with browser regression coverage. |
| Publication was POSIX-only. | Implemented native Windows locking, permission semantics, junction refusal, interrupted-writer recovery and legacy-console handling. Local native checks supplement the new CI matrix. |

## Continued evidence review

The deeper review found errors that a valid citation and matching headline
could conceal. Historical potato and sugar prices had been read from different
product rows; milk's package unit changed within the published table. Modern
food prices now identify the actual ground-chuck series rather than implying
comparability with historical round steak. Original workbook footnotes qualify
Japan's long-run household-budget population.

The US seventies food record now retains the publisher's cents-precision
amounts, including a separate meals-as-pay category. Its previous food-share
and budget-composition denominator could not be established from that table.
Those comparisons now render as linked gaps. Likewise, a blank away-food cell
in the nineteen-eighties table is no longer filled by subtracting other means.
An earlier room's later-period food survey remains readable but is excluded
from earlier-period comparison graphics. These are corrections to what the
sources support, not attempts to smooth the historical series.

Two additional British food-at-home acquisition records retain the NFS report's
original units, geography and diary definition. They measure food entering
households, not ingestion or a constructed four-person family's basket.
Historical mortality fields were also replayed against the publisher's original
aggregate CSV and bound to year, cause and rate-heading guards.

Details and reproducible source paths are in the provenance and architecture
reviews. Raw documents remain in gitignored `samples/`; no raw microdata or
credentials were added to the repository.

## Continued presentation and portability review

Reading controls keep the full source and population beside each record.
Chart tables preserve excluded records as explicit non-plotted entries instead
of silently treating missing values as zero. Shared plot exclusions now reach
pair comparisons, metrics, walkthroughs and room-stage graphics, not just the
corridor plot. Counts distinguish sourced records, derived exhibits and gaps;
an audit-calculation badge identifies a calculated field without claiming that
every numeral in a compound record has been re-extracted.

Publication writes explicit UTF-8/LF output on Windows and Linux. Native process
tests exercise cooperating writers, abrupt process exit and a legacy console
codec. Windows preserves parent ACLs and rejects directory junctions rather
than promising POSIX permission behavior. See
[the platform contract](cross-platform-builds.md) and
[the reading review](experience-review-20261028.md) for evidence boundaries.

## Existing work and publication boundary

This branch incorporates the already-authored guidance patch from
[PR 27](https://github.com/hraedon/vitrine/pull/27) and corrected quantity-token
patch from [PR 28](https://github.com/hraedon/vitrine/pull/28), after inspecting
their exact diffs and independently exercising relevant tests. Their existing
work items remain in review; no formal cross-family or human acceptance is
claimed. The separate Japan pilot in
[PR 29](https://github.com/hraedon/vitrine/pull/29) was considered to avoid
duplicating work and is not included here.

The changes are a qualified local review branch. No pull request was merged,
no main branch was pushed, and no public site was deployed by this review.
Hosted CI and exact deployed-byte verification belong to publication.

## First-tranche qualification

The complete Linux suite passed **903 tests and 67 subtests**, with the source
archive available and no skipped tests. Lint, strict typing, all 161 archive
checks, provenance, the full build, all 796 rendered-record checks, chart-mark
resolution and standalone export passed. The source-topic
check reported zero hard errors and 76 advisories; those advisories are not
claimed resolved. Configured tracked and staged identifier scans passed, and
the local and Linux staged trees matched. The final citation-only correction was followed by another
27 housing/source-contract tests and full source replay. See Plan 032 for
qualification details. Source review establishes the specific transcriptions
described here; tests and render coverage establish their narrower contracts.

The continuation's publication check found that the first local checkpoint's
author email was outside `publication.toml`'s allowed identities. That checkpoint
remains on `codex/project-review-20261028`. The combined result is recorded on
`codex/comprehensive-review-20261028`, based on the original `f487ecf`, with
the declared repository identity. No publication policy was broadened to
accommodate the accidental identity.

## Combined qualification and stopping point

The complete source-backed suite passed on both Linux Python 3.13.13 and
3.14.4: **1,015 tests and 67 subtests per version**, with four Windows-only
skips. The original workbook's missing default-style warning is non-numeric;
its published cells still reproduce. Native Windows Python 3.14.6 passed
238 core/publication tests with nine platform/filename skips. The broader
native Windows Python 3.13 run passed 826 tests and 53 subtests, with 52 skips
for unavailable archives/readers and platform/privilege cases; browser modules
were excluded from that run and covered by the Linux suites.

Independent archive replay reproduced **221 current field bindings**:
169 literals and 52 calculations. The corpus has 782 authored records and
16 derived exhibits. All 798 rendered exhibits pass actual-room-row coverage,
and all chart marks resolve. Full build/export, Ruff and strict mypy pass.
All **253 generated files are byte-identical** between native Windows and
Linux builds. The topic-consistency script reports zero hard errors and
35 contextual advisories; those advisories are not source-value verification.

The final independent architecture and experience passes found and resolved
additional undefined-inflation, currency-mismatch and withdrawn-comparison
presentation defects. Their subsequent scoped reviews found no remaining
concrete blocker. This is the stopping point for the authorized improvement
passes, not a claim that no future improvement is possible. In particular,
561 authored records still lack a current field binding, and visitor testing,
other browser engines and exact deployed-byte checks remain outside this work.
