# Plan 019 — Recover the museum UI on the split presentation architecture

**Status:** proposed
**Starting point:** `9953a0e` (`feat: integrate the museum UI with progressive enhancement`)
**Reference implementation:** `e4ef903` contains useful presentation-module,
package-resource, and Playwright work, but it was based on `081328f` and must
not be treated as the recovery baseline.

## Why this plan exists

Plan 018 produced a useful mechanical split, but it was implemented on the
pre-revamp `main` rather than on the integrated museum UI. The resulting
`main` is green while omitting the visitor-route lobby, museum-map navigation,
room timelines and curator routes, corridor atlas wings, evidence-first
placards, and their structural contracts.

The recovery must preserve two things simultaneously:

1. the complete visitor experience and provenance-bound editorial registries
   present at `9953a0e`; and
2. the maintainable package-resource, projection, curation, typed-context, and
   browser-test architecture that Plan 018 intended.

This is not another visual redesign. It is a controlled transplant of the
presentation architecture onto the correct output baseline, followed by a
repair of the placard interaction contract.

## Non-negotiable recovery strategy

Create the implementation branch from `9953a0e`, not from current `main`:

```bash
git switch --detach 9953a0e
git switch -c plan-019/ui-recovery
```

Do **not** cherry-pick `e4ef903` wholesale. Use its modules and tests as donor
material, porting them surface by surface. Its old templates, CSS, curation
registries, and output snapshots are not authoritative.

The branch must retain `9953a0e` as an ancestor. This is a mechanical
acceptance check:

```bash
git merge-base --is-ancestor 9953a0e HEAD
```

The only later `main` change that may be applied directly is the Playwright CI
browser-install adjustment from `e7355d4`, after verifying the workflow diff.

## Output baseline that must survive

Before moving code, build `9953a0e` and preserve its normalized structural
contracts. At minimum, the final site must still contain:

- the lobby's Browse / Compare / Tour visitor routes;
- the global museum map with Visit and Research groupings;
- a skip link and named main landmark;
- complete decade-room timelines with previous/next context;
- exactly one `RoomStory` per built room and exactly four distinct local facts
  per story;
- the six-case room collection and sticky case navigation;
- all four corridor atlas wings, with every rendered arc placed exactly once;
- evidence-first sourced placards and computed-exhibit placards;
- the composite-family disclaimer in every room;
- all pairwise pages, affordability, walkthrough, methodology, and
  bibliography paths; and
- every fact mark and popup deep link present at `9953a0e`, plus any deliberate
  corpus additions made afterward.

Restore `tests/test_site_contracts.py` from `9953a0e` at the beginning of the
work. Snapshot changes require an explicit explanation in the migration
report; deleting the contracts is not an acceptable way to make the refactor
green.

## Target presentation split

```text
src/vitrine/site/
  build.py                       # output orchestration only
  environment.py                 # PackageLoader, globals, render helper
  context.py                     # frozen typed page/view models
  render.py                      # temporary compatibility re-exports only
  projections/
    __init__.py
    facts.py                     # FactRef, indexing, placard hrefs
    rooms.py                     # project_room -> RoomPage
    corridors.py                 # project_corridor -> CorridorPage
    pairs.py                     # project_pair -> PairPage
    affordability.py             # room + dashboard affordability projections
    walkthrough.py               # project_walkthrough -> WalkthroughPage
    references.py                # methodology + bibliography contexts
    stage.py                     # stage and composition projection helpers
    arcs.py                      # arc/group chart projections
    metrics.py                   # annual metric/recession projections
  curation/
    __init__.py                  # deliberate public registry surface
    models.py                    # Arc, ArcGroup, CorridorWing, RoomStory, Metric
    rooms.py                     # room stories, stage positions, gaps, compositions
    corridors.py                 # arcs, groups, wings, corridor caveats
    affordability.py             # dashboard declarations
    walkthrough.py               # stops, people, metrics, floor-area selections
  templates/
    base.html
    index.html
    room.html
    corridors.html
    pair.html
    affordability.html
    walkthrough.html
    methodology.html
    bibliography.html
    legend.html
    macros/
      placards.html
      navigation.html
      charts.html
  assets/
    museum.css
    placards.js
  svg.py
  symbols.py
  tokens.py
```

### Ownership rules

- `build.py` creates directories, copies package assets, asks projection
  functions for page contexts, renders templates, and writes manifests. It
  does not build individual page dictionaries or perform chart calculations.
- Each public `project_*` function returns one typed page context.
- Templates receive a single `page` object plus documented environment
  globals. They do not receive an open-ended collection of keyword arguments.
- Templates format and branch only. They do not resolve fact IDs, compute
  ratios, determine comparability, or select editorial facts.
- Curation modules declare editorial choices but perform no SVG geometry or
  filesystem work.
- Projection modules turn the corpus plus curation into complete display
  values. They do not write files.
- Core modules outside `site/` continue to have no dependency on presentation
  code.

`render.py` remains a compatibility layer for one migration cycle. New code
imports from `build`, `projections`, or `curation` directly.

## Typed page boundary

The page dataclasses must be used, not merely declared. The intended pattern
is:

```python
page = project_room(corpus, room, index, series)
render_page(env, "room.html", output_path, page=page)
```

and in Jinja:

```jinja2
{{ page.room.decade }}
{% for section in page.panels %}...{% endfor %}
```

Required page contexts:

- `LobbyPage`
- `RoomPage`
- `CorridorPage`
- `PairPage`
- `AffordabilityPage`
- `WalkthroughPage`
- `MethodologyPage`
- `BibliographyPage`

Required intermediate contexts include `RoomStoryView`, `PanelSection`,
`PlacardView`, `ArcSection`, `CorridorWingView`, `CompositionRow`,
`PairFamilyView`, `WalkthroughStop`, and `AffordabilitySection`.

Use tuples for ordered collections and `Mapping[...]` for lookup-only fields.
Do not put mutable `list` or `dict` annotations into dataclasses advertised as
immutable. Convert mutable construction state at the projection boundary.

Represent affordability display data with a typed value rather than nested
`dict[str, dict[str, str]]`. Mypy must be able to catch a tuple/string mismatch
such as the previous `comp_caveats` defect before Jinja sees it.

Add tests proving every page context is constructed and is the object passed
to its template. A context type with zero references outside `context.py` is a
failed migration.

## Curation registries and validation

Move declarations without weakening their validators:

### Rooms

- `RoomStory` names exactly four distinct fact IDs.
- Every ID resolves to the same room decade.
- Every built room has exactly one story; no unknown story decade exists.
- Story prose may frame evidence but may not introduce unsourced numbers.

### Corridors

- Every rendered arc or arc group appears in exactly one `CorridorWing`.
- No wing names an unknown arc.
- New arcs make the registry validator fail until deliberately placed.
- Grouped arcs share scales only when their units and measures permit it.

### Other surfaces

- Walkthrough, affordability, stage, and composition registries retain their
  fact-resolution and comparability checks.
- No editorial selection may silently skip an unresolved fact ID.

## Template and asset loading

Use `PackageLoader` for templates and `importlib.resources.files()` for static
assets. Do not rely on repository-relative paths or `Path(__file__).parent`
when copying packaged resources.

The installed wheel must build the same URLs and assets from a working
directory outside the repository.

All pages link one shared stylesheet and one deferred enhancement module.
There is no inline CSS or inline JavaScript. Facts, marks, navigation, and
placard content remain fully rendered without JavaScript.

## Placard DOM and enhancement contract

### DOM placement

Render overlay decks outside `.wrap`, as siblings near the end of `<body>`.
This lets the enhancement make `.wrap` inert without also making the active
dialog inert. Split the current combined placard macro into:

- `placard_card(...)` for the inline specimen card; and
- `placard_overlay(...)` for the page-level overlay deck.

The CSS-only `:target` fallback must continue to work at the same deep-link
URLs.

### Semantics

- Generated fallback HTML uses `role="dialog"` but does not claim
  `aria-modal="true"` while the background remains interactive.
- JavaScript adds `aria-modal="true"` only to the active enhanced overlay.
- JavaScript applies real `inert` state to `.wrap` while a placard is open and
  removes it on every close path.
- The active overlay remains outside the inert subtree.

### State machine

Keep explicit module state:

```text
active overlay | originating trigger | previous focus
```

Do not rediscover the closing overlay with `:target` after the hash has already
changed. All close paths operate on stored active state, then clear it.

Required transitions:

```text
closed -> trigger click/hash -> open
open -> Escape/close/backdrop/hash-away -> closed
closed -> browser Forward/direct hash -> open
open(A) -> hash to B -> close(A), open(B)
```

Opening must focus the close control or dialog. Tab and Shift-Tab remain inside
the active overlay. Closing restores the exact originating element when it
still exists. Direct-hash visits without an origin focus the main landmark on
close. Repeated open/close cycles must behave identically to the first.

JavaScript remains interaction-only: no fact lookup, chart construction,
geometry, data fetch, analytics, or client-rendered content.

## Browser-test requirements

Run browser tests against a local HTTP server, not only `file://` URLs.

### Enhanced mode

Tests must:

1. click an actual room-story trigger;
2. click an actual SVG chart mark;
3. load an initial modal hash;
4. assert focus enters the overlay;
5. assert `.wrap.inert is True` and active `aria-modal` is `true`;
6. assert Tab and Shift-Tab containment across a complete cycle;
7. dismiss through Escape, close control, backdrop, and browser Back;
8. assert inertness and modal state are removed after every close path;
9. assert focus returns to the exact trigger—not merely any anchor or `BODY`;
10. open, close, and reopen the same overlay;
11. open overlay A, navigate to overlay B, and verify clean state transfer;
12. verify browser Forward restores enhanced state; and
13. exercise both dense room and corridor overlay decks.

### JavaScript-disabled mode

Tests must assert:

- a deep-linked overlay is visible through CSS `:target`;
- close control, backdrop, Back, and Forward work;
- the page contains no false `aria-modal="true"` claim;
- all normal navigation and disclosures remain usable; and
- every displayed fact and mark is present without client execution.

### Responsive checks

At 1280x800, 768x1024, and 375x667, assert more than element existence:

- no unintended document-level horizontal overflow;
- intended scroll containers remain keyboard reachable;
- the active placard fits the viewport or scrolls internally;
- sticky case navigation does not cover an anchored case heading;
- decade navigation exposes the current room;
- corridor atlas summaries and coverage labels do not overlap; and
- focused controls remain within the viewport.

Screenshots may supplement these assertions but may not replace them.

## Work packages and sequencing

### WP0 — Recovery baseline and contracts (integration owner, lands first)

1. Branch from `9953a0e`.
2. Build and record page count, generated size, URLs, fact marks, and registry
   coverage.
3. Restore and run structural page contracts.
4. Add the ancestry assertion to the migration checklist.

No other work package lands before WP0.

### WP1 — Curation split

Owns only `site/curation/` and curation validator tests. Move models,
room stories, atlas wings, arcs, stage registries, affordability declarations,
and walkthrough declarations without altering selections or copy.

### WP2 — Environment, templates, and static assets

Owns `environment.py`, `templates/`, package-data configuration, and stylesheet
resource handling. Extract the revamp templates verbatim before making any
semantic or accessibility changes.

WP1 and WP2 may proceed in parallel after WP0 because their file ownership is
separate.

### WP3 — Typed contexts and surface projections

Split by surface after WP1's public curation interface is stable:

- owner A: lobby, methodology, bibliography;
- owner B: rooms, room stories, panels, placards;
- owner C: corridor atlas and pairwise pages;
- owner D: affordability and walkthrough.

Each owner creates its projection module, typed contexts, focused unit tests,
and template adaptation. Owners do not edit `build.py`; the integration owner
wires completed projection APIs in WP4.

### WP4 — Build orchestration and compatibility layer

The integration owner wires one `project_*` call per page family, copies assets
through `importlib.resources`, preserves manifests, and reduces `render.py` to
re-exports. Delete superseded code in the same change; do not retain parallel
old and new renderers.

### WP5 — Placard state machine and browser suite

Owns the overlay macro split, `placards.js`, and browser tests. Start only after
room and corridor templates are stable. Fix the state model before expanding
test counts.

### WP6 — Accessibility, responsive audit, and report

Run the required viewport and keyboard matrix, update documentation, and write
the final migration report. Every intentional output difference names its
reason and affected contract.

## Size and complexity budgets

These are review thresholds, not incentives to hide code:

- `render.py`: at most 120 lines, compatibility exports only;
- `build.py`: target at most 250 lines;
- no new presentation module above 600 lines;
- no inline stylesheet or script in generated HTML;
- generated site no larger than the `9953a0e` baseline by more than 5% without
  an explained content increase; and
- one shared CSS asset and one shared enhancement asset.

If `build.py` exceeds the target because it assembles page-specific contexts,
that assembly belongs in the corresponding projection module.

## Required validation

```bash
.venv/bin/pytest -q
.venv/bin/ruff check .
.venv/bin/mypy src
.venv/bin/vitrine check
rm -rf /tmp/vitrine-plan019-site
.venv/bin/vitrine build --out /tmp/vitrine-plan019-site
.venv/bin/vitrine check --against-build /tmp/vitrine-plan019-site
```

Also build a wheel, install it with the `[site]` extra into a clean environment,
change to a directory outside the repository, and successfully run `vitrine
build` against the corpus.

CI must install the pinned Playwright browser and run the browser suite on all
supported Python versions. A skipped browser module is not a green browser
gate.

## Acceptance criteria

- `9953a0e` is an ancestor of the final branch.
- Structural contracts demonstrate that the complete museum UI survived.
- All 13 rooms have one validated four-fact opening route.
- Every rendered corridor arc is assigned to exactly one atlas wing.
- Every template receives a typed page object produced by a `project_*`
  function.
- No page context is dead code; no page boundary uses open-ended dictionaries.
- Templates and assets build from an installed wheel outside the repository.
- `build.py` is orchestration, not a replacement renderer monolith.
- Placard modal semantics, inertness, focus containment, restoration, and
  repeated lifecycle behavior pass with JavaScript enabled.
- CSS-only deep links and dismissal pass with JavaScript disabled.
- Desktop, tablet, and mobile geometry assertions pass.
- Public URLs, fact manifests, render coverage, and mark coverage remain exact.
- Ruff, strict mypy, all unit/contract/browser tests, provenance check, build,
  cross-check, and identifier gate are green.
- The final migration report records module sizes, generated-site size, wheel
  verification, browser matrix, and every intentional output change.

## Stop conditions

Stop and request review rather than improvising if:

- preserving a current `main` change would require dropping a `9953a0e` visitor
  feature;
- a template needs to perform fact lookup, arithmetic, or comparability logic;
- a client framework appears necessary;
- a public URL must change;
- a structural contract differs for a reason other than a reviewed intentional
  change; or
- the no-JavaScript visit loses content, evidence, navigation, or deep links.

The next review should happen only after the acceptance criteria are met or a
stop condition is reached with a concrete minimal reproduction.
