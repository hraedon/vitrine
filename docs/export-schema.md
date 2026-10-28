# The corpus export — consumer notes (schema version 2)

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

Top level: `schema_version` (currently `2`), then four arrays.

### `rooms[]`

| Field | Meaning |
|-------|---------|
| `country`, `decade` | Room identity; `slug` is `<country>-<decade>` |
| `wage_anchor`, `income_anchor` | Fact ids the affordability axis uses; an empty string when the room has no anchor |
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
- **`quantity` is the chartable number, and the gate enforces that one of
  its canonical renderings (plain, thousands-comma, or trailing-zero
  forms) occurs as a complete numeric token inside `value`**. Consumers
  should read `quantity` instead of parsing display prose. Token presence
  does not establish which of several independent numbers is the headline,
  or verify the cited source; those remain editorial checks.

### `rooms[].derived[]` — one computed fact

The authored derivation structure (`op`, `numerator`, `denominator`,
`precision`, `notes`, `assumptions`, and for `INFLATE`: `inflate_series`,
`inflate_from_year`, `inflate_to_year`, and for `COUNT_ABOVE`:
`count_series[]`, `threshold`, `at_year`) is kept **next to** the computed
result: `value` (display string), `computed_value` (float, in the displayed
unit), `computed_amount_minor` / `computed_currency` (for money results),
and `tier` — computed as the weakest operand tier, never authored. For
`INFLATE`, `inflation` carries the exact series id and the two observations
(base and target year, value as stored by the series — the gate only
permits `INFLATE` over a dimensionless index series, so these are index
points) used by the computation, so the arithmetic is reproducible from
this file alone. For `COUNT_ABOVE`, `numerator`/`denominator` are empty and
`computed_value` is the count; the series observations it counts over are
in `series[]` under the ids in `count_series[]`, so that arithmetic is
reproducible from this file alone too.

### `sources[]`, `assumptions[]`, `series[]`

Sources serialize every registry field (`id`, `title`, `publisher`, `year`,
`url`, `population`, `notes`, `short_cite`, `measure`, `expect[]`).
Assumptions are `id` / `title` / `statement`. Series carry their full annual
observation set, plus `label`, `source`, `tier`, `unit`, `population`, `notes`,
`splices_from`, `measure`, `kind`, `currency` and nullable `rate_basis`.
Exactly one observation map is nonempty:

| `kind` | Storage and interpretation | `currency` | `rate_basis` |
|---|---|---|---|
| `quantity` | `values`: index points, shares, hours or other stated units | Empty | `null` |
| `monetary_amount` | `values_minor`: integer minor currency units | Required | `null` |
| `monetary_rate` | `values`: major currency units per stated time basis | Required | `hourly`, `weekly`, `monthly` or `annual` |

Rates are already in major currency units: **do not divide rate observations
by the currency's minor-unit scale**. Their annual observations may be means
of monthly published rates; four-decimal subcent precision is retained.
`rate_basis` states the denominator of each rate, not the frequency of the
annual observation map. It does not establish a complete year of employment.
Rates and amounts can form same-currency affordability ratios. An inflation
index or threshold-count input must be a non-monetary quantity; a monetary
rate cannot stand in for one.

## The CSV pair

`facts-raw.csv` and `facts.csv` are the same narrow projection of
**quantified authored facts only** (facts whose `quantity` is present;
facts without one are display-only and appear in JSON alone). Columns:
`id`, `decade`, `panel`, `label`, `value`, `quantity`, `unit`, `tier`,
`source_id`, `short_cite`.

- `facts.csv` prefixes any cell whose text begins (after whitespace) with
  `=`, `+`, `-`, or `@` with an apostrophe so spreadsheet applications
  cannot reinterpret it as a formula, and carries a UTF-8 BOM so
  spreadsheets decode non-ASCII (¥, £) correctly. Canonical values are
  unchanged — nothing is rounded or reformatted.
- `facts-raw.csv` is byte-exact (BOM-less UTF-8), for machine consumption.

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

`schema_version` is `2`. Within a version, changes are additive only (new
optional fields, new enum values are avoided for existing fields). A
breaking change — a field removed or retyped, a convention above altered —
bumps `schema_version` and gets a `docs/changelog.md` entry. Consumers
should read `schema_version` and stop on a version they do not know.

Version 2 adds explicit series `kind` and `rate_basis` and permits `currency`
beside `values` only for monetary rates. Version 1 described every float
series as non-monetary, although three earnings series actually held major
USD rates with currency only in their prose units. Their numeric observations
are unchanged in version 2. A version-1 client must not interpret the newly
declared currency as a request to scale those float values. Other record
fields and both CSV projections retain their previous semantics. Previous
exports can be reproduced from the corresponding repository revision;
the current exporter emits version 2 only.
