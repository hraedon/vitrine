# Plan 020 — The Statistical Atlas: a presentation redesign

**Status:** delivered (branch `ui/statistical-atlas`, 2026-07-29)
**Scope:** presentation only — tokens, CSS, templates, the lobby projection,
and the docs that describe them. No change to the fact model, the loader, the
`check` gate, the derivation engine, curation registries, or a single datum.

## Why a redesign

The Plan 007/009/018/019 UI is a "night museum": dark gallery, brass
spotlights, ivory specimen labels, chart marks behind modal placards. It is
coherent and well-tested, but its priorities are theatrical: mood first,
evidence on request. The charter's claim is the opposite — *the exhibit is
the evidence*. This redesign asks what the data itself wants to look like.

## The take: the site should present as the document class it cites

vitrine's sources are statistical annuals, census reports, and survey
bulletins. Its natural dress is therefore the **statistical folio**: light
paper, hairline rules, tabular numerals, plate numbers, and color reserved
for epistemology. Three structural moves follow from that:

1. **Provenance becomes ambient, not on-demand.** Every fact row shows the
   value, the tier chip, *the population actually measured*, and the
   publisher·year in one scan-line — no click required. The expandable
   record keeps the deep drawer (notes, assumptions, affordability inputs);
   the `--modal` overlay placards remain for cross-page deep links from
   chart marks, with the same `:target` CSS fallback and JS state machine.

2. **The honest shape of the corpus is the landing page.** The index opens
   with a "record at a glance" matrix — decades × the six panels; every cell
   shows fact counts, the tier mix, and the gap count. "Render the gap"
   graduates from a placard style to the site's organizing geometry. All
   numbers in the matrix are build metadata (counts of corpus exhibits),
   computed in the projection layer — never authored, and the architecture
   is unchanged: core knows nothing of it.

3. **Gaps are structural, everywhere.** Gap facts, gap chart slots, and gap
   matrix cells share one vocabulary (dashed hairline, warm grey, the word
   "gap"), so absence reads as data at every zoom level.

What stays, deliberately, because it is evidentiary infrastructure and not
decoration: every `data-fact-id` mark and its `--modal` deep link; the
render- and mark-coverage gates; the composite-family disclaimer on every
room (still a visible block, higher in the reading order than before); the
placard overlay state machine (focus containment, inert background,
`:target` fallback); the six-panel skeleton; the era-graded stage (re-inked
for paper — the tint vocabulary survives as a faint plate wash); the house
cutaway, corridor wings, pairwise tables, transect, and affordability
dashboard.

## Design tokens

Light "folio" palette (full table lives in `docs/design-spec.md`; the
executable form is `src/vitrine/site/tokens.py`):

- `GROUND` — paper `#f2ecdd`; `CASE`/`CASE_2` — sheet and inset tints
- `EDGE` — hairline `#d5c9ab`
- `INK` `#29241b` body; `INK_SOFT` `#6e6450` secondary (≥ 4.5:1 on paper)
- accent ("brass" slot, re-inked): deep atlas petrol `#175d75` — editorial
  voice, rising series; `COPPER` `#b34a13` — falling series, cautions
- tiers on paper: A `#2f7a55`, B `#8f6512`, C `#7d4a63`, D `#6e6a5e`;
  white letters ≥ 4.5:1 on every chip; chips ≥ 3:1 on every sheet
- era wash for the stage: pale amber tints fading kerosene → LED
- composition bars move to a sheet-validated dark palette with white
  direct labels (mandatory; the validator result is recorded in the spec)

Contrast is enforced exactly as before — computed in `tests/test_design.py`
across every semantic color × every stage wash × every sheet, plus the new
chip-letter and segment-label constraints. No hex ships unvalidated.

## Deliverables

1. `tokens.py` rewritten; `docs/design-spec.md` rewritten to match (the
   spec/token drift test stays).
2. One stylesheet (`assets/museum.css.j2`) rewritten for the folio language.
3. All templates rewritten: index (corpus matrix), room (ledger rows),
   corridors (plates), pair, walkthrough, affordability, methodology
   (numbered ledger), bibliography (source register).
4. `LobbyPage` gains the atlas matrix (new typed views; lobby projection
   counts exhibits per room×panel; derived facts counted from `evaluate_room`,
   hoisted once in `build.py` and shared with the room loop).
5. `svg.py`: composition segments use the sheet palette; stage gradient
   reads as a paper wash; everything otherwise geometry-identical.
6. Tests: `test_design.py` extended (chip letters, segment labels, new
   surfaces); `test_site_contracts.py` re-baselined against the new
   structure with the same strength; `test_browser.py` keeps its full
   behavioral matrix (state machine, no-JS, responsive) on the new DOM;
   `test_visualization.py` updated only where visible copy changed —
   the mark/wing/story/provenance assertions stay.

## Acceptance

- `pytest -q`, `ruff check .`, `mypy src`, `vitrine check`,
  `vitrine check --against-build` all green — **done**: 214 passed
  (210 pre-redesign + 4 new design/matrix tests), both coverage gates green,
  cross-check 0 hard errors.
- Composite-family disclaimer visible on every room page — **done**:
  `test_render.py` passed unchanged; the plaque moved *up* in the reading
  order (immediately under the room title).
- Every fact row renders value + tier + measured population + source
  publisher/year inline — **done** (`fact_row` macro; the old
  `test_placards_lead_with_evidence_hierarchy` strings survive in the
  overlay body, and the row repeats the hierarchy unprompted).
- The index matrix's counts equal the corpus's own per-room/panel fact,
  derived, and gap counts — **done**:
  `test_index_matrix_counts_match_the_corpus`.
- Browser matrix passes with JS on and off at the three viewports —
  **done**: all 35 pre-existing browser tests pass against the new DOM
  without a single edit (the `.wrap`/`.placard-overlay`/`--modal` contract
  held).
- No change under `data/`, `src/vitrine/loader.py`, `src/vitrine/model.py`,
  `src/vitrine/check.py`, `src/vitrine/derive.py` — **done** (verified in
  the landed diff).

## Notable incident during implementation

An unclosed CSS rule brace (two, in fact) silently swallowed most of the
stylesheet — Chromium dropped everything after the first error, manifesting
as "overlay dismissal stopped working" in the browser suite. The suite
caught it before any human eyeballing would have. Lesson recorded: validate
the rendered stylesheet's brace balance in CI if hand-editing the template
ever resumes being a hazard; for now the browser suite is the tripwire.
