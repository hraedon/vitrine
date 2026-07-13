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

## WP2 — environment, templates, and static assets (landed)

Extracted the ten inline Jinja template constants from `render.py` into
package-resource template files and centralized Jinja environment construction
in a new `environment.py`, per Plan 019 §"Template and asset loading".

| template file | source constant | render.py lines |
|---------------|-----------------|-----------------|
| `templates/index.html` | `_INDEX` (+ folded `_TIER_LEGEND`) | 63–97 |
| `templates/macros.html` | `_PLACARD` (the `room_map` macro) | 99–211 |
| `templates/room.html` | `_ROOM` | 213–261 |
| `templates/methodology.html` | `_METHODOLOGY` | 263–279 |
| `templates/bibliography.html` | `_BIBLIOGRAPHY` | 281–300 |
| `templates/affordability.html` | `_AFFORDABILITY` | 302–328 |
| `templates/corridors.html` | `_CORRIDORS` | 330–436 |
| `templates/pair.html` | `_PAIR` | 438–489 |
| `templates/walkthrough.html` | `_WALKTHROUGH` | 491–572 |
| `environment.py` (new) | globals block from `render_site` | ~1296–1314 |

`render.py` shrank from 1732 → 1170 lines (−562). The `DictLoader({...})`
construction was replaced by `build_environment(disclaimer, disclaimer_title)`
from `environment.py`, which uses `PackageLoader("vitrine.site", "templates")`.
Template references updated from loader keys (`"base"`, `"macros"`, `"index"`)
to filenames (`"base.html"`, `"macros.html"`, `"index.html"`) — these are
loader-resolution directives that emit no output, so rendered HTML is
unchanged.

**Ownership honored:** only `environment.py`, the new template files, and
`render.py` changed. `build.py` was not touched (doesn't exist yet — WP4
territory); `curation/`, assets, `tests/`, and `pyproject.toml` untouched
(the existing `templates/*.html` package-data glob already covers the new
files).

**Scope deferred to later WPs:** the plan's eventual `templates/macros/
{placards,navigation,charts}.html` split is not done here — `macros.html`
stays one flat file. The placard-overlay macro split (into `placard_card` and
`placard_overlay`) is WP5.

**Correctness proof:** `diff -r /tmp/vitrine-wp1-baseline /tmp/vitrine-wp2-result`
is empty — byte-for-byte identical to the WP1 build. Full suite 162 green,
ruff + mypy --strict clean (22 source files), provenance and mark-coverage
gates green, ancestry gate PASS.

## WP3 + WP4 — typed contexts, surface projections, build orchestration (landed)

Split the 1170-line `render.py` into the Plan 019 target presentation
architecture: typed page contexts (`context.py`), one projection module per
surface (`projections/*.py`), a thin build orchestrator (`build.py`), and a
compatibility-only `render.py`. Per §"Typed page boundary", every template now
receives a single typed `page` object produced by a `project_*` function;
templates format and branch only, never resolving fact IDs or computing ratios.

| module | lines | role |
|--------|-------|------|
| `context.py` | 342 | 8 page contexts + 9 intermediate view types (all `frozen=True, slots=True`) |
| `build.py` | 188 | orchestration: env, dirs, assets, render+write loop, manifest, registry gates |
| `render.py` | 107 | compatibility re-exports only (`render_site` + private names tests pin) |
| `projections/rooms.py` | 93 | `project_lobby`, `project_room`, `room_story`, `panels_for` |
| `projections/corridors.py` | 202 | `project_corridor` + wing-validation `ValueError` |
| `projections/pairs.py` | 156 | `project_pair`, `pair_families`, `pair_afford` |
| `projections/walkthrough.py` | 231 | `project_walkthrough` + `_FIGS` decoration primitives |
| `projections/affordability.py` | 195 | `project_affordability_dashboard`, `affordability_for_room`, afford-arc chart |
| `projections/references.py` | 20 | `project_methodology`, `project_bibliography` |
| `projections/stage.py` | 94 | `build_stage` |
| `projections/arcs.py` | 143 | arc/group chart + coverage projections |
| `projections/metrics.py` | 133 | annual metric/recession projections |
| `projections/facts.py` | 43 | `FactRef` (re-export), `index_facts`, `placard_href`, `GAP_PREFIX` |

**Size budgets met:** `build.py` 188 ≤ 250; `render.py` 107 ≤ 120; largest
projection module 231 < 600.

**Ownership honored:** only `build.py`, `context.py`, `render.py`,
`projections/` (new), the 9 templates (rewritten to `page.X`), and one
`pyproject.toml` per-file-ignore line (the `_FIGS` SVG literals carry the same
E501 carve-out they had in the original `render.py`) changed. `environment.py`,
`curation/`, `assets/`, `svg.py`, `symbols.py`, `tokens.py`, and
`tests/test_site_contracts.py` untouched.

**Decision points:**
- `FactRef` lives in `context.py` (the boundary leaf) and is re-exported from
  `projections/facts.py` — placing it in facts.py created a circular import
  (context → projections.facts → package `__init__` → projections.affordability
  → context). The current DAG is clean: context is the leaf every projection
  reads from.
- `CorridorWingView.arcs` typed as `tuple[ArcSection, ...]` — one uniform shape
  whether the section is a lone arc or a collapsed group.
- The wing-validation `ValueError` lives in `projections/corridors.py`
  (`_build_wings`), not `build.py` — it is mechanically inseparable from arc
  assembly (it validates rendered-arc slugs against wing membership, which only
  `project_corridor` computes). The room-story-registry `ValueError` stays in
  `build.py` (a decades-vs-registry check build.py owns).
- `_render_page(env, template, out, *, root, surface, page)` helper in
  `build.py` standardizes the render+write loop.
- `evaluate_room` / `affordability_for_room` run twice (once in `build.py` for
  the manifest + merged affordability, once inside `project_room` for
  self-contained page assembly) — acceptable double-compute for 13 rooms; keeps
  `project_room`'s signature clean.
- `comp_caveats` typed as `tuple[str, ...]` (it was already a 1-tuple in the
  original — the template iterates it).

**Wheel verification:** built a wheel, installed in a clean venv, rendered the
site from `/tmp` — byte-for-byte identical to the WP2 baseline.

**Correctness proof:** `diff -r /tmp/vitrine-wp2-baseline /tmp/vitrine-wp34-result`
is empty — byte-for-byte identical to the WP2 build. Full suite 162 green,
ruff + mypy --strict clean (35 source files), provenance and mark-coverage
gates green, ancestry gate PASS, `tests/test_site_contracts.py` unchanged and
passing (9 tests).

## WP5 — placard macro split, browser suite, enhancements.js fix (landed)

Split the combined `placard` macro into `placard_card` (inline specimen card)
and `placard_overlay` (page-level overlay deck) per Plan 019 §"Placard DOM and
enhancement contract", added a 34-test Playwright browser suite covering the
plan's enhanced / no-JS / responsive matrix, wired Playwright into CI on both
Python versions, and fixed a real `:target` dismissal bug the new tests
surfaced in `enhancements.js`.

### Macro split (byte-identical)

`macros.html`: `_placard_body` unchanged; `placard` replaced by
`placard_card(fact, room, sources, assumptions, affordability, root)` and
`placard_overlay(fact, room, sources, assumptions, affordability, root)`.
Call sites in `room.html`, `corridors.html`, `pair.html`, `walkthrough.html`
updated: inline exhibits call both macros (card then overlay, matching the
prior combined output); overlay-deck loops call `placard_overlay` only. The
generated HTML is byte-for-byte identical to the WP3+WP4 baseline — a pure
macro-organization refactor.

### Browser suite (tests/test_browser.py, 34 tests)

Serves the built site over local HTTP (`http.server` in a module-scoped
fixture — the plan requires this, not `file://`). Covers the plan's full
matrix:

- **Enhanced (17 tests):** open from room-story trigger, SVG chart mark, and
  direct hash; focus enters overlay; `.wrap` inert + active `aria-modal=true`;
  Tab / Shift-Tab containment; dismissal via Escape, close button, backdrop,
  browser Back; focus returns to the exact originating trigger (element
  identity, not tag name); open-close-reopen lifecycle; A→B state transfer;
  Forward restores enhanced state; dense deck cycles on the 41-overlay room
  and 249-overlay corridor page.
- **JavaScript-disabled (6 tests):** `:target` deep link visible; close
  control, backdrop, Back, and Forward work; no false `aria-modal="true"`;
  fact marks and navigation present without client execution.
- **Responsive (11 parametrized tests):** no document-level horizontal
  overflow at 1280×800, 768×1024, 375×667 (corridor + room pages); decade
  navigation exposes the current room at 375×667; placard card fits the mobile
  viewport; focused control stays within viewport at every breakpoint.

### enhancements.js dismissal bug (fixed)

The browser suite uncovered a real defect: `dismissOverlay()` used
`history.pushState(null, "", "...#dismissed")`, which updates the URL but
does **not** recalculate CSS `:target` in Chromium. After Escape / close /
backdrop dismissal, the enhanced state was cleaned up correctly (aria-modal
removed, `.wrap` de-inerted, focus restored to origin) but the overlay stayed
visually `display:flex` because `:target` still matched the old hash. Browser
Back dismissal and A→B transfer already worked (they use real fragment
navigations).

Fix: `dismissOverlay()` now calls `closeOverlay()` first, then
`location.hash = "#dismissed"` — a same-document fragment navigation that
updates `:target` and fires `hashchange`. The `hashchange` handler
(`syncWithHash`) no-ops because `active` is already null by then. This is the
only byte difference from the WP3+WP4 baseline (one asset file). All five
previously-xfailed dismissal/reopen/dense-deck tests now pass green.

### CI

Both Python 3.13 and 3.14 now install the pinned Chromium browser
(`.venv/bin/python -m playwright install --with-deps chromium`) and run the
browser suite (`pytest tests/test_browser.py -v`) after the existing build
step. A skipped browser module is no longer a green browser gate.

### Scope deferred

The plan's §"DOM placement" prefers overlays rendered outside `.wrap` as
siblings near the end of `<body>`. The current architecture renders overlays
inline (inside `.wrap`) and `enhancements.js` moves the active overlay to
`document.body` at runtime via a comment-placeholder swap. This meets the
functional requirement (the active overlay is outside the inert `.wrap`
subtree whenever a placard is open — now verified by the `.wrap` inert + aria
+ visibility tests). Restructuring the static HTML would break byte-identity
and require simplifying the JS's move logic; it is a clean follow-up, not a
correctness gap. The macro split here is the structural prerequisite for that
future move (templates already call `placard_overlay` separately).

**Correctness proof:** `diff -r` against the WP2 baseline shows exactly one
changed file (`assets/enhancements.js`, the bug fix) — all HTML is
byte-identical. Full suite **196 green** (162 existing + 34 browser),
ruff + mypy --strict clean, provenance + mark-coverage green, ancestry PASS,
`tests/test_site_contracts.py` unchanged and passing.

### Adversarial-review follow-ups

A cross-lineage adversarial review of WP2–WP5 found no critical or major
defects (byte-identity verified by `git worktree` rebuild + `diff -r`; all 8
page contexts + 14 view types constructed and consumed — no dead types;
mypy --strict clean; wheel-install loads all templates and assets). Four
minor findings addressed in this follow-up:

- **Dead `modal` parameter** in `_placard_body` (`macros.html`): declared and
  passed at both call sites but never read inside the body — a leftover from
  the placard macro split. Removed from the signature and both call sites.
- **`.gitignore` + ruff `build/` exclusion**: setuptools' ephemeral `build/`
  dir (created on first `pip install -e` when no wheel is cached) mirrors
  `src/` and surfaced 21 spurious E501s under `build/lib/...` on first CI
  runs (the per-file-ignore paths didn't match the duplicated tree). Added
  `build/` to `.gitignore` and `exclude = ["build"]` to `[tool.ruff]`.
  Verified: a simulated `build/lib/` no longer affects `ruff check`.
- **Recovery-log test-count drift**: corrected "10 contract tests" → 9 (the
  parametrized `EXPECTED` dict has 9 entries) and "23 enhanced" → 17
  (34 total − 6 no-JS − 11 responsive).
- **Post-dismissal Forward coverage gap**: added
  `test_dismiss_then_back_forward` proving Escape creates a real history
  entry (Back reopens, Forward returns to the dismissed state). Full browser
  suite now 35 tests.

Borderline finding noted but not acted on: `projections/metrics.py:load_recessions`
reads `data/recessions.toml` directly — a projection module doing file I/O on
a non-corpus, non-curation data file. Functionally correct (build.py calls
it and threads the result through); the cleaner home would be build.py-owned
ingestion passed in as a parameter (the way `series` is). Left as-is because
moving it risks a signature change across the byte-identical window for
marginal abstraction benefit; flagged for a future cleanup pass.

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
