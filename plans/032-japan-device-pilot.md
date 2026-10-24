# Plan 032 — A focused Japan equipment route

**Status:** draft implementation. Independent technical/editorial review,
formal workflow gates and human acceptance are pending. This plan does not
authorize site publication or deployment.

## Intended behavior

The Japan thematic entrance links to a focused opening route in `jp-1990s`.
The route asks what the existing personal-computer, mobile-phone, facsimile
and standalone word-processor records measure about surveyed households.
All four records are existing NSFIIE 1999 observations; their source values,
populations, dates, tiers, notes and audit state remain unchanged.

The room is explicitly a **Focused exhibit**, not a Guided room or a complete
household portrait. Separate marginal ownership shares do not establish that
the same household owned the devices together, how devices were used, or a
matched household. The framing introduces no number, calculation, device
replacement story, trend or causal claim.

The exact route is:

- `jp-1990s-pc`
- `jp-1990s-mobile-phone`
- `jp-1990s-fax`
- `jp-1990s-word-processor`

## Country enrollment is broader than room status

`CURATED_COUNTRIES` derives countries from authored `ROOM_STORIES`. Adding
this Japan story enrolls the country: **all seven Japan rooms join the lobby
inventory and the country badge**, even though only the equipment room has
an opening route. This is an intentional country-level effect, not a claim
that all rooms have reviewed stories or shared editorial status.

The existing `jp-1950s` RESEARCH status and rationale remain verbatim. The
other five Japan rooms retain their research defaults; no hidden stories are
added to them. New room status is never inferred from record counts. The
Japan thematic entrance remains a Focused exhibit and preserves all existing
measurement lenses and selected values.

`COMPARATIVE_COUNTRIES` stays US-only. Japan does not enter the corridor atlas,
pairwise pages, walkthrough or affordability analyses. Its rooms gain no
country-specific comparative links or illustrated house entrance. Existing
global museum navigation remains available, as it is for other research rooms.
`HOUSE_ROOMS` and every country-specific stage binding remain unchanged.

## Isolation and scope

The feature branch `feat/japan-device-pilot-20261024` is stacked on guidance
commit `5c373e874e76366fa3335190d7bb5affabcaa6a9`. Its eventual draft PR targets
`fix/enrollment-guidance-20261024`, not main or the independent quantity-token
work. The shared checkout and the guidance and quantity branches stay untouched.

The predeclared working set is `AGENTS.md`, `README.md`,
`docs/japan-exhibit-curation.md`, this plan,
`src/vitrine/site/curation/rooms.py`,
`src/vitrine/site/curation/collections.py`,
`src/vitrine/site/templates/japan.html`,
`tests/test_japan_device_pilot.py`, `tests/test_browser.py`,
`tests/test_site_contracts.py` and `tests/test_visualization.py`. The final two
paths were added to WI-034 before edits when the first full runs exposed the
intentional structural snapshot and fully enrolled inventory consequences.

No data, source registrations, audit records, assumptions, stage bindings,
comparative/house registries, public formats, dependencies or deployment files
are in scope. Source cards remain editorial provenance; no new source
transcription or raw-archive verification is claimed.

## Acceptance and evidence

Visitor contracts must fail on the guidance baseline and pass on the feature:
one visible focused route, exactly four distinct same-room facts with their
citations, a discovery link from Japan's existing entrance, all seven Japan
lobby rows enrolled, and the six remaining research statuses preserved.
All Japan rooms must retain their comparative/house exclusions.

Run locked isolated Python 3.13 and 3.14 dev environments with normal lint,
strict typing, complete non-browser tests, provenance, real build, standalone
export, render/mark coverage and cross-check commands. Compare committed data,
thematic selections and stage representations to a baseline snapshot; compare
export payloads without changing source values. Do not use raw archives or keys.

Browser checks exercise discovery and all route source cards at phone, tablet
and desktop widths, plus the no-JavaScript path. Inspect readable screenshots
of the entrance, route and source card. Formal/human acceptance and any later
publication remain separate from these technical checks.

Baseline and final command results will be recorded with the immutable
candidate handoff and the authoritative work item WI-034.

## Local verification of the draft

- The guidance baseline passed the existing collection/enrollment checks. The
  new visitor contracts failed in the intended four places, with seven scope
  controls already green; all four new browser cases failed on the missing
  discovery link before implementation.
- Final locked Python 3.13.13 and 3.14.8 lanes each passed 715 non-browser tests
  and 67 subtests, with 16 existing archive/dump skips. Raw archives and keys
  were not used. Each Chromium/layout lane passed 79 cases.
- Ruff and strict mypy passed on both interpreters. Provenance, real build,
  standalone export, render/mark coverage and source-topic cross-check passed;
  the latter reported zero hard errors and 76 existing soft review issues.
- The two intentionally changed structural snapshots cover the new Japan
  entrance section/link and the seven additional lobby rows. The inventory
  contract explicitly tests both fully enrolled and Japan-directory-only
  inputs, including strict exclusion of the non-enrolled wing's facts.
- All 112 committed corpus/audit/assumption files, thematic selections, country
  stage bindings, house/comparative scopes, the early Japan editorial choice
  and the US/UK stories match baseline. Six export files are byte-identical.
  Of 246 generated site files, only the lobby, Japan entrance and focused room
  changed; the other 243 are byte-identical.
- Phone, tablet, desktop and no-JavaScript previews were inspected under the
  production response headers, including the source cards. Twelve component
  screenshots and viewport checks are retained in the local evidence bundle.

The evidence bundle uses the prefix `/tmp/vitrine-japan-device-pilot-`; the
final candidate handoff binds the exact commit. These local checks do not
constitute independent technical/editorial review, hosted CI, formal workflow
acceptance or human approval, and no site was published or deployed.
