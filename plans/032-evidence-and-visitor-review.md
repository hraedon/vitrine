# Plan 032 — Evidence review and collection entrances

**Status:** implemented and locally qualified, 2026-10-28.
Not published or deployed.

## Outcome

Respond to the owner's broad review request while preserving the data
methodology. Make existing records more trustworthy, move collection
entrances earlier, and acquire only source material needed for a defensible
bounded expansion. See [the review](../docs/project-review-20261028.md) for
findings, implemented fixes and remaining design decisions.

## Delivered scope

- Independent source, experience and architecture reviews of `f487ecf`.
- Corrections to the UK 1953 tenure split and associated comparison, Japan
  equipment/availability notes and date, US TV interpretation and UK stories.
- Thirty direct ONS audit bindings and two reproducible EHS extraction
  bindings; all previous ledger dates preserved for unchanged entries.
- Two England dwelling observations from newly acquired EHS 2011 originals
  and errata; the remaining housing gap is retained with narrower wording.
- Compact country entrances, featured UK route, native decade disclosures,
  optional methods guide, complete visible disclaimer and record access.
- Honest line gaps, nonfinite-series refusal, declared-currency boundaries,
  ambiguous denominator refusal and HTML-backed render coverage.
- Reviewed incorporation of draft PRs 27/28; separate Japan pilot excluded.

## Acceptance and evidence boundaries

- Full Linux tests with the real source archive, lint and strict typing.
- Provenance, source-field replay, full build, rendered-record/mark coverage,
  standalone export, source-topic check and configured identifier gate.
- Browser checks under production CSP, phone/tablet/desktop geometry and
  no-JavaScript country entrances and source cards.
- Original source documents remain gitignored. No raw microdata, credentials
  or generated site is committed. A green audit covers declared fields, not
  the entire corpus or every number in a compound note.
- Publication remains a separate tested-commit/hosted-CI/deployed-byte step.

## Qualification

Baseline: 794 tests and 67 subtests passed with the archive. Final integrated
suite on Python 3.13: **903 tests and 67 subtests passed**, including browser
checks under production CSP and all archive prerequisites (no skips). Ruff and
strict mypy passed. After the final printed-page citation correction, the 27
housing/source-page contract checks passed again and all 161 source-field
checks replayed with current fingerprints. Unchanged ledger dates were retained.

Provenance passed for 27 rooms, 780 authored facts, 16 derived exhibits,
124 sources, 19 assumptions, 78 series and three essays. The build, all 796
canonical rendered records and chart-mark resolution passed. Standalone
export and publication plumbing passed. The source-topic cross-check examined
617 US facts and 124 sources: zero hard errors, 76 advisories (the advisories
are not claimed resolved). The configured tracked and staged identifier scans
both passed using the operator's shared denylist. Local and Linux staged trees
were identical; source documents, generated output and pre-existing untracked
handoff files were excluded.

Independent mutation review restoring the old manifest-only coverage function
failed all six new HTML coverage regressions. A separate final technical pass
passed 65 focused tests covering core import isolation, annual integrity,
coverage, CSV line endings and original housing-PDF extraction. Existing draft
PRs 27/28 were technically reviewed without claiming formal acceptance.

Browser evidence and before/after geometry are in
`docs/experience-review-20261028.md`. A local preview of the qualified output
is available while the operator's HTTP server is running. No hosted CI or
deployed-byte verification is claimed for this unpublished branch.
