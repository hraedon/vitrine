# vitrine

A decade-by-decade virtual museum of the median-income four-person family's
lifestyle — every fact behind glass, with its source card showing.

## What this is

vitrine renders "decade rooms": for each (country, decade), a composite
portrait of how the family at the median income lived — the home, the budget,
the table, the working day, what technologies had reached them, and what a
day's work bought. The distinguishing mechanic is **provenance under glass**:
every rendered fact carries a source citation and a confidence tier, and the
build fails mechanically if any fact lacks one.

- **v1 (US):** rooms from the 1900s through the 2020s, tier-badged (an 1890s
  room is planned; the 1890–91 Commissioner of Labor survey is already in the
  source registry). Official median family income exists only from 1947
  (Census P-60); the 1940s room leans on census microdata; the early rooms are
  reconstructed from period cost-of-living surveys; the museum stops where the
  record does, and says so.
- **v2 (world):** United Kingdom, Poland, Russia, China, India, Japan — each
  with its own honest data floor and country-specific caveats (consumption vs
  income in India, shortage economies in the PRL/USSR, urban/rural splits in
  China and India).

## Why it exists

Nothing occupies this niche: popular "life in the 1950s" content is
uncitable nostalgia, and the underlying economic data is published but never
assembled into a lifestyle portrait with the methodology on display. vitrine
is an experiment in whether rigorous sourcing and an approachable museum
format can coexist — the exhibit *is* the data model, rendered.

## The central honesty rule

The median-income family is a statistical composite, not a family. The family
at the median income did not have the median house, the median car, and the
median diet all at once. Every room displays this disclaimer, and every fact
declares the population actually measured. Where the record is silent, the
room shows the gap instead of inventing a number.

## Confidence tiers

| Tier | Meaning |
|------|---------|
| A | Official statistical series for the stated population (e.g. Census P-60 median family income, 1947→) |
| B | Official microdata; the statistic is computed by this project (e.g. IPUMS 1940 census) |
| C | Reconstructed from contemporaneous surveys of a proxy population (e.g. 1901 BLS cost-of-living survey of urban wage-earners) |
| D | Scholarly estimate or narrative; no contemporaneous survey exists |

## Scope

**In:** curated facts with citations; a deterministic static-site build; the
six-panel room skeleton (home / budget / table / day / diffusion / a-day's-
work-buys); methodology and assumption pages generated from the same data
files; schematic SVG illustration.

**Out (non-goals):** original econometrics beyond simple, documented
arithmetic (equivalization, deflation); real-time data feeds; user accounts or
any server-side state; photorealistic or AI-generated period imagery in v1;
being a general-purpose economic-history database.

**Boundary vs. siblings:** vitrine is a data-curation and presentation
project. It shares the portfolio's provenance temperament but does not depend
on regista/dossier/agent-notes; its provenance is editorial (source cards),
not cryptographic.

## Design principles

1. **The data files are the museum; the site is a projection.** Facts live in
   versioned TOML under `data/`, one file per (country, decade), plus a global
   source registry and an assumption ledger.
2. **No AI in the truth path.** Every number is hand-curated from a cited
   source. Narration, if ever added, is an optional layer that may not
   introduce numbers.
3. **The gate is mechanical.** `vitrine check` fails the build on any fact
   without a resolvable source, a tier, or a declared population — CI enforces
   what the charter promises.
4. **Render the gap.** "No reliable record exists" is a valid, first-class
   exhibit state.

## Status

US corpus curated: 13 decade rooms (1900s–2020s), 307 facts, 2 derived
facts, zero Tier D estimates; 18 rendered gaps are structural (pre-WWII
income/housing/food for 1910s–1930s, 1940s wartime bifurcation, 1990s/2010s
home-production data) and listed in `docs/resource-hunt.md`. The
visualization layer (Plan 007) is implemented: three static surfaces —
rooms (dark-gallery cutaway, era-graded light, CSS-only popup placards),
corridors (cross-decade arc charts plus the 78-page pairwise comparison
set), and the walkthrough (the three-stop transect) — all pre-rendered,
no JS, every chart mark carrying the fact id it projects (`data-fact-id`,
enforced by the mark-coverage gate in `vitrine check --against-build`).
Design tokens and the validated palette: `docs/design-spec.md` /
`src/vitrine/site/tokens.py`. Plan 009 (visitor experience pass) is in
progress: 9 of 23 items done, 2 partial, 11 pending. See
`docs/fact-model.md` (design spine) and `plans/` for the full series.

## Quick start

```bash
uv venv && uv pip install -e ".[dev]"
.venv/bin/vitrine check            # validate data/ against the fact model
.venv/bin/vitrine build            # render the static site to _site/
.venv/bin/vitrine gaps             # mechanical gap inventory (never hand-kept)
.venv/bin/pytest -q
```
