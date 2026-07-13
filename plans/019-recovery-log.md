# Plan 019 — recovery log & migration checklist

Living record for the UI recovery. WP0 opens it; each later work package
appends its landing note. The migration checklist at the bottom is the set of
mechanical gates every subsequent commit on this branch must keep green.

## WP0 — recovery baseline and contracts (landed)

**Branch:** `plan-019/ui-recovery`, created from `9953a0e`
(`feat: integrate the museum UI with progressive enhancement`).

### Ancestry gate (the invariant the whole recovery hangs on)

```bash
git merge-base --is-ancestor 9953a0e HEAD   # must exit 0
```

Result at WP0: **PASS** — `9953a0e` is an ancestor of HEAD. Every future commit
on this branch must keep this true. If it ever fails, the recovery has drifted
off the content-complete baseline and must stop (see Plan 019 stop conditions).

### Root cause, confirmed mechanically

The Plan 018 refactor did not regress by editing the UI — it branched from
`081328f`, *before* the museum UI was integrated at `9953a0e`, and main followed
that branch. The reason CI stayed green while the visitor experience vanished:

| baseline | `tests/test_site_contracts.py` |
|----------|-------------------------------|
| `9953a0e` (this branch) | **present** — 8 page contracts |
| `main` (`144d2a9`)      | **absent** — dropped in the refactor |

The one test that pins page landmarks, disclosure state, local destinations,
provenance overlays, and the fact-mark set was removed, so nothing failed when
the pages it guarded lost their content.

### Baseline build metrics

```
vitrine build  →  13 rooms, 456 facts, 3 derived, 80 sources, 13 assumptions, 10 series
```

| metric | main (`144d2a9`) | baseline (`9953a0e`) |
|--------|------------------|----------------------|
| HTML pages | 97 | 97 |
| generated size | 8.2 MB | 9.0 MB |
| corpus facts | 456 | 456 |
| `test_site_contracts.py` | absent | **present, 162 tests green** |

The page **set** is identical (same 97 URLs); the loss is entirely *within*
pages. `9953a0e` contains no fewer facts than main — main added no corpus data
after `081328f` — so `9953a0e` is the strictly-richer content baseline.

### Exactly what main is missing

Running the baseline's own `PageContract` scanner against main's build, **all 8
contracted pages diverge**. The pattern is systematic, not incidental:

- **`<header>` landmark: 1 → 0 on every page.** The museum header is gone
  site-wide.
- **Navigation stripped:** index nav 2 → 1; every room nav 3 → 1; corridors
  nav 2 → 1. The visitor-route and in-room navigation is absent.
- **Rooms lost their opening-route structure:** each room's `<section>`
  landmark 1 → 0, and fact marks drop (`us-1950s` 10 → 9, `us-1910s` 6 → 3 —
  half its marks). The `RoomStory` four-fact opening route is not being
  rendered.
- **Corridor atlas wings are gone:** `corridors/index.html` loses 5 `<header>`s,
  5 `<section>`s, all 4 open disclosures, and 31 `<details>` — the four-wing
  atlas collapsed to an ungrouped list.
- **Every page's `local_links_hash` differs** and link counts drop — the
  visitor routes, atlas links, and opening-route deep links are simply not
  present in main's output.

This is the surface WP1–WP6 must restore. It is also the exact set the restored
contracts will re-pin, so a future refactor cannot silently drop it again.

### Handoff

- WP1 and WP2 fork from the **pushed** `origin/plan-019/ui-recovery` tip, not
  from `main`, `9953a0e`, or a local baseline.
- Only the integration owner (WP0/WP4) touches `build.py`.
- No work package lands before it re-runs the migration checklist below.

## WP1 — curation split (landed)

Decomposed the monolithic `src/vitrine/site/curation.py` (1096 lines) into the
`site/curation/` package specified by the Plan 019 target layout:

| module | holds |
|--------|-------|
| `models.py` | the 5 frozen dataclasses (Arc, ArcGroup, CorridorWing, RoomStory, Metric) |
| `corridors.py` | `_ids`, ARCS, ARC_BY_SLUG, ARC_GROUPS, ARC_GROUP_BY_MEMBER, CORRIDOR_WINGS, AFFORD_ITEMS/_CAVEATS |
| `rooms.py` | ROOM_STORIES, ROOM_STORY_BY_DECADE, COMPOSITIONS, STAGE_DIFFUSION/STATS, HOME_SIZE_FACTS, ROOM_GAP_BANNERS, ZONE_NOTE_POS |
| `affordability.py` | AFFORDABILITY_METRICS, METRIC_BY_SLUG |
| `walkthrough.py` | WALKTHROUGH_STOPS/PEOPLE/METRICS/FLOOR_AREA |
| `__init__.py` | deliberate public surface — re-exports all 26 names as `curation.*` |

**Ownership honored:** only `site/curation/` changed. `render.py` is untouched
— it still does `from vitrine.site import curation` and reads `curation.X`, which
the re-exporting `__init__` preserves exactly.

**Corrected-donor notes:** unlike the donor (`e4ef903`, pre-museum-UI), this
split adds a `models.py` home for the museum models `CorridorWing`/`RoomStory`
the donor never had; `rooms.py` imports `ARC_BY_SLUG` from `corridors.py`
(the stage registries key off it); `AFFORD_ITEMS` stays with corridors per the
donor's grouping. No selection or copy was altered — declarations were sliced
verbatim from the original, not retyped.

**Correctness proof:** the generated site is **byte-for-byte identical** to the
WP0 baseline build (`diff -r` clean) — a pure structural refactor. Full suite
162 green (incl. contracts), ruff + mypy --strict clean, provenance and
mark-coverage gates green, ancestry gate PASS.

## Migration checklist (every commit on this branch)

1. `git merge-base --is-ancestor 9953a0e HEAD` exits 0 (ancestry gate).
2. `tests/test_site_contracts.py` is present and green; snapshot changes carry a
   written reason here, and deleting a contract is never how a refactor goes
   green.
3. `.venv/bin/pytest -q` — full suite green.
4. `.venv/bin/ruff check .` and `.venv/bin/mypy src` clean.
5. `.venv/bin/vitrine check` — provenance gate green.
6. Build, then `.venv/bin/vitrine check --against-build <out>` — mark coverage
   exact.
7. Generated site within 5% of the `9953a0e` size (9.0 MB) unless an increase
   is explained here.
