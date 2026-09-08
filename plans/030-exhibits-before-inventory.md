# Plan 030 — Exhibits before inventory

**Status:** implemented and locally qualified, 2026-09-07. Publication uses
the tested-commit CI/deployment workflow.

## Intended outcome

Restore an engaging visual entrance to the collections without implying a
complete household where the evidence cannot support one. Respond to the
production screenshots: overflowing editorial badges, a vertical decade
selector, and ambiguous facts/gaps totals.

## Delivered design

- Selected US rooms open with the house and four source-linked highlights.
  The explicit selection covers 1900 and 1950–2020; the uneven 1910–1940
  collections retain focused exhibits or research entrances. Japan keeps its
  thematic entrance and complete decade archive.
- Room houses use fixed illustrative geometry. Labels describe measurements;
  they do not claim that separate source populations lived together. Compound
  records excluded from primary illustration remain available in the records.
- Horizontal decade navigation stays compact and scrolls within its own
  boundary on phones. Lobby tiles reserve a separate row for editorial status.
- Observations exclude gaps. Calculated exhibits and documented gaps have
  separate, explicit labels; counts refer to collection entries. The lobby
  matrix moves into an expandable inventory beneath the entrances.
- The complete disclaimer, six record panels, source cards and stable links
  remain available. All interactions retain a JavaScript-free path.

## Production defect and remedy

Production CSP blocked inline style attributes that local browser tests had
allowed. The selector's blocked custom property invalidated its grid layout.
The new selector has no inline dependency; the response policy permits authored
style attributes for existing visual encodings while continuing to block inline
scripts and style elements. Browser fixtures now send nginx's actual headers.
See `docs/production-layout-policy.md` for scope and evidence.

## Acceptance

- Baseline gates before changes; full lint, typing, tests, provenance, build
  and export checks afterwards, then exact-commit CI and deployment comparison.
- Geometry checks at phone, tablet and desktop widths inspect each badge's
  text bounds and the selector's row/height, including keyboard scrolling.
- Source cards open from the restored house with JavaScript disabled.
- Production CSP preserves tier colors and SVG alignment; allowing style
  attributes does not enable inline scripts or style elements.
- No source values or audit coverage change in this presentation tranche.

## Qualification

The unchanged baseline passed 581 tests. The completed tranche passed 603
tests on Python 3.14 with the source archive available, including 70 browser
checks under production CSP. Coverage includes 320px mobile object links,
tablet highlight geometry, horizontal keyboard navigation and badge bounds.
Independent review identified and resolved small mobile targets and empty
tablet grid rows. Desktop house and inventory views were inspected visually.

Ruff, strict typing, provenance, all 753 rendered-exhibit checks, and standalone
export passed. The source data and existing 97-field archive audit remain
unchanged. The staged identifier gate passed with the operator's shared list.

## Follow-up — circle and boundary spacing

Enlarged the house circles from radius 17 to 26, retaining the existing glyph
size to add internal padding. Click targets grow with the circles. Object rows,
caption offsets and the lower floor now reserve space for the complete mark,
including its label, rather than just its centre. Geometry regression checks
cover all nine house rooms and the walkthrough at 375, 768 and 1280px widths:
circles and captions clear structural lines, and objects do not overlap each
other or their annotations. The 1950s and denser 1980s layouts were visually
reviewed; data and source bindings are unchanged.
