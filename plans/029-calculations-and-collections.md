# Plan 029 — Calculations, collections and interpretive restraint

**Status:** implemented and locally qualified, 2026-09-07. Publication uses
the tested-commit CI/deployment workflow.

## Intended outcome

Make the prominent calculations reproducible from saved publisher inputs,
organize Japan around supported subjects, and remove household and historical
interpretations that the cited measurements cannot establish. This supersedes
Plan 028's automatic density rule; existing decisions are open to revision.

## Work items

1. Extend the audit with same-file source operands, exact arithmetic, explicit
   rounding and a recorded method. Support means and percentage ratios only;
   JSON pointers select original API response values and context. Save every
   operand in the ledger so the offline gate can replay the calculation.
2. Qualify selected CES/CEX observations against real source files. Save new
   publisher responses as a new input vintage. Do not imply they recreate an
   unavailable historical download. Separate compound wage claims and keep
   incompatible consumer-unit populations visible. Unverified tables produce
   gaps rather than an invented reconstruction from rounded aggregate shares.
3. Replace room-density inference with an explicit editorial registry and
   rationale. Build a Japan thematic entrance with source-separated household,
   workplace and equipment observations; retain all decade archive links.
   Polish the US 1950s room as a contrasting guided presentation.
4. Review the existing essays, thematic corridors and strongest room notes.
   Arithmetic does not demonstrate family behaviour, causality, prevalence,
   or the disappearance of a practice when a statistical series ends.

## Acceptance

- Every newly audited field reproduces from pinned publisher bytes, and guards
  detect wrong populations, years and monthly periods. A failed audit preserves
  the ledger; the offline gate detects method/operand/semantic drift.
- Arithmetic uses an explicit rounding rule, checks denominator validity, and
  never uses the museum's own generated series as independent evidence.
- Existing fact links remain valid after splitting compound records or
  identifying unsupported claims; additional observations have their own IDs.
- Japan's theme selections show actual observation dates and populations;
  no cross-country chart enrollment or implied continuous national household.
- Editorial statuses are inspectable choices, not evidence/confidence scores.
- Source cards work without JavaScript; Japan and US examples fit phone and
  desktop screens. All rendered records and source links remain covered.
- Full tests, typing, lint, provenance/build/export gates, identifier check,
  remote CI and exact deployed-byte comparison pass before completion.

## Explicit limits

This tranche does not audit the entire corpus or establish source authority.
Food-price baskets and other unqualified compound records remain a backlog.
Additional countries and the mortality essay remain deferred. Absence from
an accessible archive is not proof that a historical record never existed.

## Delivered scope

The corpus now has 738 authored records and 15 derived exhibits. Thirteen
single-measure observations were added; four unsupported four-person CEX
comparisons became explicit gaps. All 97 archive checks passed (58 literals
and 39 calculations). See `docs/calculation-audit-evidence.md`,
`docs/editorial-review.md` and `docs/japan-exhibit-curation.md` for evidence
and remaining limits.

## Qualification

581 tests passed on Python 3.14 with the source archive available, including
phone/desktop and no-JavaScript source-card checks. Ruff and strict typing
passed. The build covered all 753 exhibits, and standalone export passed.
All 97 archive checks matched. Source-topic checks reported zero hard errors
and 75 advisory findings; these are not claimed resolved. The staged
identifier gate passed using the operator's shared denylist.
