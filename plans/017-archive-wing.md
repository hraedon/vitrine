# Plan 017 — The archive wing: the collection about the collection

**Status:** draft
**Triggered by:** 2026-07-11 deep-dive over the evidence base. Provenance
under glass is the museum's distinguishing mechanic, but the provenance
itself has thin surfaces: one flat bibliography page for 80 sources, a gap
inventory that exists only as CLI output, and a fact base consumable only
as rendered HTML. The corpus is the product; it deserves a wing.

## The problem

1. **Sources are second-class exhibits.** A source card names the survey and
   its measured population — the museum's most load-bearing honesty device —
   but a visitor cannot ask "what else in this museum rests on the 1901 BLS
   survey?" The answer exists in the corpus; no page shows it.
2. **The shape of the record is invisible.** `vitrine gaps` computes, per
   room, the tier mix, rendered gaps, and empty panels — the museum's own
   epistemic floor plan. It renders nowhere. "The museum stops where the
   record does" is the charter's best line and a visitor cannot see it
   happen at a glance.
3. **The fact base is not reusable.** 446 facts with populations, tiers,
   assumptions, and citations is a dataset nothing else occupies (the niche
   scan that founded the project). Locked in TOML-behind-HTML it can't be
   cited, diffed by outsiders, or built on — and the corpus-of-engagement
   pillar wants exactly this kind of durable artifact.

## Design

Three surfaces, all pure projections of data that already exists. No new
truth enters the museum in this plan.

### WI-1: Map of the record

One page (`archive/map.html`, linked "The record" from the index): a
13-room × 6-panel grid. Each cell renders the panel's fact count and a tier
composition bar (the four tier colors, plus the gap/dash treatment for
rendered gaps); an empty panel renders as the same dashed "not yet curated"
vocabulary the rooms use. Row ends carry the room totals `gaps.py` already
computes. Cells link to the panel anchor in the room.

Implementation: extend `RoomGaps` (or a sibling in `gaps.py`) with per-panel
tier counts — the renderer projects it, consistent with the
generated-not-hand-maintained rule. The existing design tokens cover this;
the tier colors already hold ≥3:1 on `case`.

**Acceptance:** every cell's counts equal the corpus's (test computes both
ways); grid totals match `vitrine gaps` output; page passes the link
checker; no fact ids rendered without resolving (mark coverage).

### WI-2: Source collection pages

`archive/sources/<id>.html`, one per registry entry: full citation, the
verbatim `population` string given top billing, `measure` where declared,
access notes, and **every fact that cites this source**, grouped by room
with tier chips and placard links. The bibliography page's entries become
links into these. Where Plan 015 lands, the page also shows audit status
per fact (audited date from the ledger) — soft dependency, page degrades
to citation-only without it.

A registry entry cited by zero facts is listed with "registered, not yet
cited" (there are such entries — e.g. the 1890–91 Commissioner of Labor
survey awaiting the 1890s room); that too is the shape of the record.

**Acceptance:** page count equals registry count; the union of facts across
source pages equals the corpus (nothing dropped, nothing duplicated —
gate-tested); bibliography links resolve.

### WI-3: `vitrine export` — the corpus as citable dataset

A new CLI subcommand emitting, deterministically, into the build:

- `_site/data/corpus.json` — schema-versioned (`schema_version = 1`):
  rooms, facts (all fields including structured amounts, quantities,
  assumptions), derived facts (with computed values *and* their operand
  ids — the derivation stays visible), sources, assumption ledger.
- `_site/data/facts.csv` — the flat projection of quantified facts
  (id, decade, panel, label, value, quantity, unit, tier, source_id,
  short_cite) for spreadsheet users.
- A `data.html` landing page stating what the dataset is, the composite
  disclaimer, the tier taxonomy, and how to cite.
- `CITATION.cff` at the repo root.

Determinism matters: byte-identical output for an unchanged corpus, so
dataset diffs are corpus diffs. A round-trip test loads `corpus.json` and
asserts fact/source/assumption counts and every fact id match the corpus.

**Licensing note (owner decision, does not block implementation):** the
transcribed facts are US-government-work data plus curation; the curation
layer needs an explicit data license (CC BY 4.0 is the natural candidate)
before the already-gated public flip. The landing page ships with a
"license: pending" line until decided.

**Acceptance:** export runs in `vitrine build`; round-trip test green;
regenerating twice is byte-identical; `facts.csv` row count equals
quantified-fact count.

## Phasing

| Phase | WIs | Effort | Dependency |
|---|---|---|---|
| 1 | WI-3 (export) | Low — serialization of loaded model | None |
| 2 | WI-1 (map) | Low–medium — gaps.py extension + one template | None |
| 3 | WI-2 (source pages) | Medium — one template, N pages, gate tests | None (audit column arrives with Plan 015) |

Ordered by leverage-per-effort: the export is nearly free and makes the
corpus durable outside the site; the map is the cheapest new visitor
surface in the museum; source pages are the most templating work.

## Out of scope

- A "new acquisitions" changelog page generated from git history — cute,
  museum-appropriate, and deferred until someone actually wants it.
- Any external data catalog registration (Zenodo/DOI) — post-public-flip.
- Per-assumption pages (the ledger is small; the methodology page carries it).
- Search. Static, no-JS museum; the map and source pages *are* the finding
  aids.
