# Plan 031 — The United Kingdom joins the curated collection

**Status:** mechanism tranche implemented 2026-10-12 (locally qualified on
the Linux build host; publication via the tested-commit CI/deployment
workflow). The story tranche — the seven UK room stories and editorial
selections that flip enrollment — lands with this plan as its acceptance.

## Intended outcome

Enroll the United Kingdom as the second curated country — authored room
stories, curated wing badge, lobby-matrix membership — without letting an
enrolled room reach into an analysis that holds none of its facts. The
round answers the two standing owner questions: enrollment is a content
decision (author the editorial layer), and the country-keyed stage
registries stay exactly as they are.

## Delivered design (mechanism tranche)

- Curation now has two named layers. `CURATED_COUNTRIES` stays the derived
  enrollment set (a country joins when its room stories are authored);
  `COMPARATIVE_COUNTRIES` names the countries whose own comparative
  curation is written and is projected over by the corridor atlas, the
  pairwise set, the walkthrough and the affordability view. It is US-only
  today and must stay a subset of the curated set (a red build otherwise).
- The pairwise loop, the corridor atlas and the guided walkthrough take
  the comparative rooms, so a second curated "1950s" no longer collides in
  the walkthrough guard or double-writes pair pages. The build derives its
  curated set from the published constant instead of re-deriving it from
  the story registry.
- The room-level "See this metric across all decades" link and the
  affordability-page citation gate move to the comparative layer, so an
  enrolled-but-not-comparative room (the UK, on enrollment day) cannot link
  itself onto a US-only page — the FWI-005 guard now covers exactly the
  case it was written for.
- The lobby inventory becomes the curated collection: matrix rows label
  their country (`UK 1970s` beside a bare `1970s`), and the section's
  captions say "curated collection" instead of naming the US wing.
- `tests/test_enrollment_layers.py` simulates the UK's enrollment by
  widening the curated set alone and renders the whole site: the build
  must succeed, the pairwise set must stay US-sized, UK rooms must join
  the matrix without the comparative link, and every room must still
  render. The comparative-gate tests were retargeted to the new layer.

## Story tranche (the enrollment itself)

One `RoomStory` per UK room (1950s–2010s): digit-free framing, exactly four
distinct facts of that room, gaps permitted where the record is a silence
(the 1950s room must include one). Each room gets an explicit
`ROOM_EDITORIAL` selection; guided status requires its story. The stories
are editorial prose — the owner reviews wording as PR review.

## Acceptance

- Baseline gates before changes; lint, typing, tests, provenance, build,
  export checks and `check --against-build` afterwards on the Linux host.
- The simulated-enrollment test passes both before the stories land (the
  mechanism proof) and after (now merely descriptive of the built site).
- The committed UK stories pass the story gate on build: no digits in the
  framing, four distinct in-room facts, no borrowed exhibit.
- No source values, audit coverage or stage registries change in this
  round; the UK_STAGE bindings and their room-membership enforcement stay
  exactly as committed.

## Scope limits

- The comparative layer stays US-only: UK corridors, affordability arcs
  and walkthrough stops are a later round that authors UK comparative
  curation and then widens `COMPARATIVE_COUNTRIES` with its registries.
- The house-experience entrance (`HOUSE_ROOMS`) stays the nine US rooms;
  whether UK rooms join it is a presentation decision for a later round.
- `ROOM_GAP_BANNERS` stays US-keyed (no decade overlap with the UK wing
  today); re-keying it per country is deferred with that note on record.
- No new UK data series in this round; the missing-for-parity families
  (expenditure compositions, food share, home size) are catalogued for a
  follow-up sourcing round.
