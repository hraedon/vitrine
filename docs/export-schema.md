# The corpus export — consumer notes (schema version 1)

`vitrine export` (and every full `vitrine build`) writes a data surface:
`data/corpus.json`, `data/facts.csv`, and `data/facts-raw.csv`, introduced
by a `data.html` landing page. This document is the consumer contract for
those files. The authoring model — what a Fact, Source, Assumption, or Room
*is*, and the tier taxonomy — lives in `docs/fact-model.md`; this page only
describes the projection.

The exports are **projections of the gated corpus, not a second source of
truth**: they are rendered from the same TOML files the site renders from,
only after `vitrine check` (the provenance gate) passes. They contain
aggregates and citations only — never raw or micro-level source material —
so the archive's licensing posture (IPUMS compliance in particular, see
`docs/ipums-compliance.md`) carries over unchanged.

## Determinism

Repeated exports of the same corpus are byte-identical. Every collection is
sorted (rooms by country then decade; facts, sources, assumptions, and
series by id); series observations keep chronological order. Non-finite
floats are refused before anything is written. The JSON is UTF-8, indented
two spaces, trailing newline. If two exports differ, the corpus or the
exporter changed — never chance.

## `corpus.json`

Top level: `schema_version` (currently `1`), then four arrays.

### `rooms[]`

| Field | Meaning |
|-------|---------|
| `country`, `decade` | Room identity; `slug` is `<country>-<decade>` |
| `wage_anchor`, `income_anchor` | Fact ids the affordability axis uses, or `null` |
| `data_as_of` | Editorial recency marker for the room |
| `facts[]`, `derived[]` | The authored record, below |

### `rooms[].facts[]` — one authored fact

Every field of the authored model, with optional fields carried as `null`
rather than omitted: `id`, `panel`, `label`, `value` (display string),
`unit`, `source` (id resolving into `sources[]`), `tier`, `notes`,
`assumptions[]` (ids resolving into `assumptions[]`), `amount_minor`,
`currency`, `price_year`, `basis`, `quantity`.

Two conventions matter to consumers:

- **Money is minor units.** `amount_minor` is an integer-scaled amount in
  the currency's minor unit (pence, cents); yen has none, so a yen
  `amount_minor` is a whole yen count. The registry
  (`vitrine.money.CURRENCIES`, currently USD/GBP with 2 minor digits, JPY
  with 0) is the scale table. Divide by `10 ** minor_digits` for major
  units; never assume 100.
- **`quantity` is the chartable number and must appear verbatim inside
  `value`** — the build gate enforces it, so a consumer may quote `value`
  as the display form of `quantity` without re-checking.

### `rooms[].derived[]` — one computed fact

The authored derivation structure (`op`, `numerator`, `denominator`,
`precision`, `notes`, `assumptions`, and for `INFLATE`: `inflate_series`,
`inflate_from_year`, `inflate_to_year`) is kept **next to** the computed
result: `value` (display string), `computed_value` (float, in the displayed
unit), `computed_amount_minor` / `computed_currency` (for money results),
and `tier` — computed as the weakest operand tier, never authored. For
`INFLATE`, `inflation` carries the exact series id and the two observations
(base and target year, value as stored — minor units when the series is
monetary) used by the computation, so the arithmetic is reproducible from
this file alone.

### `sources[]`, `assumptions[]`, `series[]`

Sources serialize every registry field (`id`, `title`, `publisher`, `year`,
`url`, `population`, `notes`, `short_cite`, `measure`, `expect[]`).
Assumptions are `id` / `title` / `statement`. Series carry their full
annual observation set — `values`, and `values_minor` with `currency` when
the series is monetary — plus `label`, `source`, `tier`, `unit`,
`population`, `notes`, `splices_from`, `measure`.

## The CSV pair

`facts-raw.csv` and `facts.csv` are the same narrow projection of
**quantified authored facts only** (facts whose `quantity` is present;
facts without one are display-only and appear in JSON alone). Columns:
`id`, `decade`, `panel`, `label`, `value`, `quantity`, `unit`, `tier`,
`source_id`, `short_cite`.

- `facts.csv` prefixes any cell beginning with `=`, `+`, `-`, or `@` with
  an apostrophe so spreadsheet applications cannot reinterpret it as a
  formula. Canonical values are unchanged — nothing is rounded or
  reformatted.
- `facts-raw.csv` is byte-exact, for machine consumption.

JSON remains the canonical machine-readable record; the CSVs are a
convenience projection.

## Citing

For a number, cite the primary source its `source`/`source_id` names
(click through to its `url`), then cite the vitrine corpus for the
compilation and tier assignment — `CITATION.cff` in the repository root is
that corpus citation (content CC BY-SA 4.0; the exporter software is
separately MIT-licensed; see `LICENSE`). Underlying source material keeps
the terms stated on its source record.

## Versioning

`schema_version` is `1`. Within a version, changes are additive only (new
optional fields, new enum values are avoided for existing fields). A
breaking change — a field removed or retyped, a convention above altered —
bumps `schema_version` and gets a `docs/changelog.md` entry. Consumers
should read `schema_version` and stop on a version they do not know.
