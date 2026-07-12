# Plan 018 — Presentation Architecture

**Status:** in progress
**Started:** 2026-07-12

## Goal

Split the monolithic `render.py` (~1,650 lines) and `curation.py` (~820 lines)
into a well-separated presentation layer: package-resource templates, typed
page contexts, projection helpers, and curation split by surface.

## Target structure

```
site/
  __init__.py
  build.py            # orchestration — build_site()
  context.py          # frozen, slotted page-context dataclasses
  svg.py              # SVG primitives (unchanged)
  tokens.py           # design tokens (unchanged)
  symbols.py          # artifact symbols (unchanged)
  projections/
    __init__.py
    facts.py           # FactRef, index_facts, placard_href
    stage.py           # build_stage, fold_shares
    arcs.py            # arc chart projections
    pairs.py           # pairwise corridor projections
    affordability.py   # affordability projections + formatting
    metrics.py         # dashboard metric resolution + recession loading
  curation/
    __init__.py        # re-exports for backward compat
    room.py            # stage, compositions, gap banners, zone notes
    corridor.py        # arcs, arc groups, afford items
    affordability.py   # dashboard metrics
    walkthrough.py     # walkthrough stops, people, metrics, floor area
  templates/
    base.html
    macros.html
    index.html
    room.html
    methodology.html
    bibliography.html
    corridors.html
    pair.html
    walkthrough.html
    affordability.html
    legend.html
  assets/
    vitrine.css
```

## Phases

1. Extract inline CSS into `assets/vitrine.css` (resolve Jinja vars to static values)
2. Extract all templates into `templates/` package resources
3. Replace `DictLoader` with `PackageLoader`
4. Split `curation.py` into `curation/` package
5. Create `context.py` with typed page contexts
6. Split `render.py` into `build.py` + `projections/`
7. Update `pyproject.toml` for package data
8. Update tests for new import paths
9. Add Playwright browser tests
10. Accessibility audit

## Constraints

- No inline CSS or JS in generated HTML
- No public URL changes
- No facts or computations in templates
- Installed-wheel builds must work
- Existing test suite must pass
