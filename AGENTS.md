# AGENTS.md

Conventions and quick reference for agents (and humans) working on vitrine.

## What this is

A decade-by-decade virtual museum of the median-income four-person family's
lifestyle, built as a deterministic static-site generator over hand-curated,
fully-cited data files. The exhibit mechanic is provenance: every rendered
fact carries a source card and a confidence tier, enforced by a mechanical
build gate. See `README.md` for the full charter.

## Orient

1. **Read the fact model.** `docs/fact-model.md` is the design spine: the
   entities (Fact / Source / Assumption / Room), the tier taxonomy, the file
   layout under `data/`, and the invariants `vitrine check` enforces. It
   dictates what the site is allowed to display.
2. **Read the current plan.** `plans/` holds numbered plans; work items and
   acceptance criteria live there.
3. **Facts come from sources, full stop.** Curating a room means reading the
   primary source and transcribing, not recalling. Model memory is a lead
   generator for finding sources, never a source.

## Hard rules

- **No AI in the truth path.** Every number in `data/` is transcribed from a
  cited source a human can follow. LLM narration, if ever added, is an
  optional layer that imports the core, never the reverse (architecture
  test), and may not introduce numbers.
- **No unsourced facts.** Every fact carries `source` (resolving to the
  registry), `tier`, and the source's surveyed population. `vitrine check`
  fails the build otherwise; CI runs it. If a fact can't be sourced, it
  doesn't ship — **render the gap** ("no reliable record") instead.
- **The composite-family disclaimer always renders.** Every room states that
  the portrait is a statistical composite assembled from separate
  distributions. Removing or hiding it is a charter violation.
- **Numbers are never invented or "adjusted by feel."** Permitted arithmetic
  (deflation, equivalization) is documented in the assumption ledger and
  applied by code in the repo, not by hand in the data files.
- **Respect source licensing.** Cite and extract facts; link to the source.
  Do not commit bulk third-party datasets. Downloaded raw source material
  lives in gitignored `samples/` and is never committed.
- **IPUMS compliance.** IPUMS USA data is used under a legally binding
  agreement. Read `docs/ipums-compliance.md` before using IPUMS data. Key
  rules: (1) raw microdata is never committed — it lives in gitignored
  `samples/`; (2) only aggregate statistics (medians, percentages, counts)
  are published as Facts; (3) Full Count data (1850-1950) will not be
  republished — only derived statistics computed from it; (4) cite IPUMS
  properly; (5) add vitrine to the IPUMS bibliography when published.
- **Stdlib-only core.** The fact model, loader, and `check` use stdlib only
  (`tomllib`, `dataclasses`, `argparse`). Rendering is the `[site]` extra
  (jinja2) and imports the core, never the reverse.
- **Correctness by construction.** `mypy --strict` in CI;
  `typing.assert_never()` in the default branch of every dispatch over a
  closed set (`Tier`, `Panel`). When a new variant is added, the type checker
  finds every site that must handle it.
- **No work-domain identifiers in committed files.** Enforced by the
  identifier gate (pre-commit hook + CI job). Homelab identifiers
  (`hraedon`, `mvm*`) are allowed; the work-domain set is not.

## Build / test / lint

```bash
uv venv && uv pip install -e ".[dev]"
.venv/bin/pytest -q
.venv/bin/ruff check .
.venv/bin/mypy src
.venv/bin/vitrine check          # the provenance gate, same as CI runs
.venv/bin/vitrine build          # static site → _site/ (gitignored)
.venv/bin/vitrine check --against-build _site  # + render & mark coverage
```

The site (Plan 007) is three static surfaces — rooms, corridors, walkthrough —
with no JS; design tokens live in `docs/design-spec.md` +
`src/vitrine/site/tokens.py`, editorial chart/stage registries in
`src/vitrine/site/curation.py`. Chart marks carry `data-fact-id`; a mark that
can't name a curated fact is a red build. A fact's chartable number is its
structured `quantity` (must appear verbatim in `value` — gate-enforced);
facts without one render as gaps.

## Data authoring

- One room file per (country, decade): `data/<country>/<decade>.toml`.
- Global registries: `data/sources.toml`, `data/assumptions.toml`.
- Fact ids are globally unique: `<country>-<decade>-<slug>`.
- Tiers: A official series / B official microdata (computed) / C period-survey
  reconstruction / D scholarly estimate. When in doubt, tier *down* and note why.

## Research materials & API keys (gitignored `samples/`)

- `samples/` holds the organized primary-source archive (19 topic dirs +
  `MANIFEST.md`, cross-referenced to `sources.toml`). **Verify transcriptions
  against these documents first** — bls.gov 403s non-browser clients from
  this environment; Wayback `…/web/<yyyy>id_/<url>` fetches work.
- `samples/api.env` (KEY=VALUE): `BLS_API_KEY`, `CENSUS_API_KEY`,
  `IPUMS_API_KEY`. Load with `set -a; . samples/api.env; set +a`. The
  registered BLS key permits multi-decade series pulls in one request.
  IPUMS use is governed by `docs/ipums-compliance.md` — read it first.
- Nothing under `samples/` is ever committed (raw third-party data, secrets).
- Verification lesson (2026-07-08, wage facts): hours and obscure table cells
  transcribe clean; *famous* headline numbers are the ones that arrive from
  model memory wearing a fake citation. Verify earnings-class values against
  the actually-cited series before trusting them.

## Repo hygiene

- Private until a written sanitization review (`docs/publication-review.md`).
- Breadcrumbs live in the agent-notes DB (`agent-notes` CLI), not in-repo dirs.
- Plans in `plans/NNN-*.md`; keep headers honest or trust git log over them.
