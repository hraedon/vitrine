# Plan 024 — Corpus exports and the data surface (archive wing)

**Status:** delivered 2026-08-28. *Backfilled at landing time*: the work was
developed directly in the working tree without a plan file and found
complete-but-uncommitted at session start (all gates already green); this
document reconstructs scope and acceptance from the code, the test suites,
and a live `vitrine export` run. Plan numbering skips 024–026 in the tree
only because no files existed; this claim takes 024.

**Triggered by:** the publication-side counterpart of the provenance gate.
Once every fact is gated and the site renders from the corpus, the corpus
itself is the citable artifact — the archive wing's download surface.
`docs/ipums-compliance.md` shapes what it may contain: aggregates and
citations only, never raw source material.

## Scope

- **`vitrine export` CLI**: runs the full `vitrine check` gate first, then
  writes a standalone data surface — `data.html` landing page with assets,
  plus the `data/` exports — without rendering the rest of the museum. The
  page works standalone (no museum nav) and integrates into full builds
  (nav "Data" entry, active-state link).
- **`corpus.json` (schema version 1)**: rooms with metadata, every authored
  fact with all structured fields (`amount_minor`, `currency`, `price_year`,
  `basis`, `quantity`), the source register, the assumption ledger, and the
  complete series including annual observations — so an `INFLATE` derivation
  is reproducible from the export alone. Derived facts carry the authored
  derivation structure next to the computed result (`value`,
  `computed_value`, `computed_amount_minor`, `computed_currency`,
  weakest-operand tier) and the exact inflation observations used.
- **CSV pair**: `facts.csv` (public, spreadsheet-safe — cells that could be
  read as formulas are apostrophe-prefixed) and `facts-raw.csv` (exact
  machine values). Both are quantified authored facts only; JSON remains
  canonical.
- **`publish.py` (stdlib-only core)**: staged same-filesystem publication
  for both `build` and `export`. Builders render into a sibling staging
  directory and publish with `os.replace`; the destination is never written
  file-by-file. Advisory locks serialize cooperating local writers per
  logical output root (a nested data surface reuses the full site's lock);
  orphan staging directories are cleaned by the next cooperating run;
  path overlap with the corpus and symlinked destinations or trees are
  rejected. Rollback/cleanup failures have documented partial states;
  recovery fails closed (destination absent + exactly one valid artifact,
  else error).
- **`derive.py`**: `ComputedFact` gains `numeric_value`, `amount_minor`,
  `currency`. Fixes a display bug: `INFLATE` and `AMOUNT_PRODUCT` divided
  minor units by a hardcoded `100`, which would have mis-scaled a
  zero-minor-digit currency (JPY) a hundredfold; money display now scales
  through the currency registry (mirroring the plan-023 `series_numeric`
  fix).
- **`CITATION.cff`**: the corpus citation — dataset, CC-BY-SA-4.0 content,
  MIT software — scoped by a contract test against the dual `LICENSE`.
- **Charter invariants carried onto the new surface**: the
  composite-family disclaimer renders on `data.html`; non-finite floats are
  rejected before entering a machine-readable export; exports are
  projections of the gated corpus, not a second source of truth.

**Acceptance (met 2026-08-28):** full suite green (377 tests, including
publication failure modes: rollback, swap failure, umask variance, symlink
rejection, lock serialization, orphan cleanup, fail-closed recovery);
ruff + `mypy --strict` clean; `vitrine check`, `vitrine build`, and
`check --against-build` green (render + mark coverage verified); live
`vitrine export` run inspected by hand (schema 1, 27 rooms, sorted
collections, formula-safe CSV).
