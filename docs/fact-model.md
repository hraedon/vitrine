# The fact model

This is vitrine's design spine. It defines what a displayed fact *is*, where
it lives, and the invariants the build gate enforces. The site is a pure
projection of this model; anything the site shows that this model can't
express is a design bug.

## Entities

### Fact

The atomic exhibit unit. One claim, one source, one tier.

| Field | Type | Meaning |
|---|---|---|
| `id` | str | Globally unique, `<country>-<decade>-<slug>` |
| `panel` | Panel | Which room panel it belongs to (closed set, below) |
| `label` | str | Visitor-facing caption ("Median family income, 1950") |
| `value` | str | Display value as authored ("$3,319", "9%", "no record") |
| `unit` | str | Unit / basis ("USD per year, nominal", "% of households") |
| `source` | str | Id resolving into `data/sources.toml` |
| `tier` | Tier | Confidence tier (closed set, below) |
| `notes` | str | Optional curator note shown in the provenance drawer |
| `assumptions` | list[str] | Ids resolving into `data/assumptions.toml` |
| `amount_minor` | int? | Structured value in integer minor units (cents) — no float drift |
| `currency` | str | ISO 4217 code, e.g. `"USD"`; required iff `amount_minor` is set. Must be registered in `vitrine.money.CURRENCIES` — an unknown code is a red `vitrine check`. `vitrine.money` also formats amounts per-currency; **no FX** — the museum never converts between currencies as a truth-path number. |
| `price_year` | int? | Year the amount is quoted in |
| `basis` | Basis? | What the amount is measured against (closed set, below); required iff `amount_minor` is set |
| `quantity` | float? | Headline non-monetary numeric for chart projection (a percentage, hours, a rate); must appear verbatim in `value` — gate-enforced |

`value` is always the as-authored display string: the museum shows what the
source said, in the source's own terms. The structured fields
(`amount_minor`/`currency`/`price_year`/`basis`) are *additional*, never a
replacement — they are optional, and when present they feed the affordability
axis (see `src/vitrine/affordability.py`) and cross-decade comparators. A fact
with no structured amount still renders; it just carries no derived
affordability figure.

`quantity` (Plan 007) extends the same additional-never-a-replacement pattern
to non-monetary numerics: it is the one number a chart mark may project from
this fact (a diffusion percentage, weekly hours, a mortality rate). The gate
enforces that the quantity appears verbatim in `value` — it is a transcription
of the displayed datum, so the chart cannot drift from the placard. A fact
whose `value` carries no single honest headline number (a multi-series string,
a range) simply has no `quantity`, and charts render it as the gap it is.

A fact whose honest value is "the record is silent" is written with
`value = "no reliable record"` (or the longer form `"no reliable record
accessible online"` used by v2 world rooms where the gap is an archive-
access limitation rather than a missing survey) and normally tiered `D` with a
note explaining why. When an authoritative source explicitly prints an absent
period or documents an incompatible series boundary, the gap may carry that
source's stronger tier: the tier then measures the evidence for the absence,
not a value that was estimated. The gap detector matches any `value` that starts with
`"no reliable record"`. Rendering the gap is a feature; inventing a number
is a charter violation.

### Source

An entry in the global registry `data/sources.toml`.

| Field | Type | Meaning |
|---|---|---|
| `id` | str | Stable slug, e.g. `census-p60-hist-f8` |
| `title` | str | Full citation title |
| `publisher` | str | Census Bureau / BLS / GUS / NBS / IPUMS / scholar |
| `year` | int | Publication year of the source document |
| `url` | str | Where a visitor can verify (stable/archival link preferred) |
| `population` | str | **Who was actually measured** — the anti-composite field |
| `notes` | str | Access date, edition, table number, caveats |
| `short_cite` | str | Brief inline citation for footnote display on visualizations |
| `measure` | Measure? | What economic quantity an affordability anchor measures; optional in general but **required on any source used as a `wage_anchor` or `income_anchor`** (see Measure, below) |
| `expect` | list[str]? | Content markers `scripts/link_check.py` verifies against the served document — a 200 OK is not proof the URL serves the described document (the f08a/f08ar wrong-variant incident). Text/HTML and `.xlsx` (shared strings) are searchable; opaque formats (PDF) stay resolve-only. |

`population` is mandatory and load-bearing: "all US families, CPS money
income" vs "urban wage-earner families with a male head" is the difference
between an official median and a proxy reconstruction, and the visitor sees it.

### Assumption

An entry in the ledger `data/assumptions.toml`. Assumptions are the
methodological choices that would mislead if left implicit — each is written
once and referenced by every fact it touches.

| Field | Type | Meaning |
|---|---|---|
| `id` | str | Slug, e.g. `income-vs-consumption` |
| `title` | str | Short name |
| `statement` | str | The full plain-language statement |

Seed ledger (grows as rooms are curated):

- `composite-family` — rooms are statistical composites; no real family held
  the median position in every distribution at once. Rendered on every room.
- `four-person-normalization` — how "family of four" is derived when the
  source publishes all-family or household medians (equivalence scale, or the
  by-size table where one exists, e.g. Census Historical Income Table F-8).
- `income-vs-consumption` — some countries/eras measure consumption, not
  income (India's NSS; pre-1940 US expenditure surveys).
- `nominal-values` — values display in nominal period units; any deflation is
  computed by repo code with the CPI series named.
- `shortage-economy` — in rationed/shortage economies (USSR, PRL-era Poland)
  money income overstates lifestyle; availability facts accompany income facts.
- `urban-rural-split` — where the split dominates (China, India), rooms carry
  separate facts rather than a misleading national blend.

### Derived fact (plan 006)

A `[[derived]]` entry in a room file authors **structure, never a number**:
two operand fact ids and an op. The displayed value and the tier are computed
at build (tier = weakest operand tier — a curator cannot badge a derivation
stronger than its inputs). Operands must be structured facts in the same
room with the same currency.

| Field | Type | Meaning |
|---|---|---|
| `id` | str | Same rules as fact ids (prefix, uniqueness — shared namespace) |
| `panel` | Panel | Which room panel it renders in |
| `label` | str | Visitor-facing caption |
| `unit` | str | Carries the semantics ("years of four-person median family income") |
| `op` | DerivedOp | `ratio`, `pct_of`, `inflate`, `product`, or `quantity_ratio` (closed set) |
| `numerator` | str | Fact id in this room or another room (cross-room, WI-5); must have `amount_minor` (for ratio/pct_of/product/inflate) or `quantity` (for quantity_ratio) |
| `denominator` | str | Fact id in this room or another room (cross-room, WI-5); must have `amount_minor` (for ratio/pct_of), `quantity` (for product/quantity_ratio), or empty (for inflate) |
| `precision` | int | Decimal places in the rendered value (0–4, default 1) |
| `notes` | str | Curator note — **must not hand-quote numbers**; the drawer shows operands |
| `assumptions` | list[str] | Ids resolving into the ledger |

Cross-room operands, non-monetary quantities (hours, index points), and
scaled ops are deliberately out of v1 scope — see plan 006. Until they land,
the remaining authored-arithmetic facts are enumerated there as visible debt.

### Room

One file per (country, decade): `data/<country>/<decade>.toml`, e.g.
`data/us/1950s.toml`. A room is `[room]` metadata plus a list of `[[fact]]`
tables. The `[room]` table carries `country` and `decade` and, optionally,
the affordability anchors `wage_anchor` (a fact id whose `basis` is `hourly`)
and `income_anchor` (a fact id whose `basis` is `annual`); the affordability
axis divides each priced fact by these. A room for the current (ongoing)
decade may also declare `data_as_of` (e.g. `"2024"`) — the year the room's
most recent facts were drawn from, shown so the visitor knows how stale the
"current" decade is. Country codes are lowercase ISO-ish slugs
(`us`, `uk`, `pl`, `ru`, `cn`, `in`, `jp`); decades are
`"1890s"`…`"2020s"`.

### Essay (plan 016)

The docent layer: curated connective prose — "tours" — for the century-scale
stories the corpus proves but no chart tells. One file per tour,
`data/essays/<slug>.toml`: an `[essay]` table (`slug`, `title`, `standfirst`)
and `[[block]]` entries of kind `prose` (copy) or `chart` (exactly one of
`arc` / `group` / `metric`, resolved against the site's registries at build).

The defining rule: **the docent may interpret; the docent may not quote from
memory.** A number enters prose only by binding to a fact — `{fact:<id>}`
renders the fact's as-authored `value` with its tier chip, deep-linked;
`{fact:<id>:label}` renders the label; derived facts interpolate identically
(linking to their room row). After stripping these bindings, the numeral gate
(`vitrine check`) fails the build on any remaining numeric token except
four-digit years (1850–2035), decade words, and ranges of the two. The gate
checks numbers; the adversarial-review pass checks words. Honest limits
(recorded in plan 016): verbal arithmetic is words, and fact selection is
editorial — every essay page carries the composite-family disclaimer strip.

> **Country scope.** The interpolation regex in `model.py`
> (`INTERPOLATION_RE`) matches any `<country>-<decade>-<slug>` fact id, so
> essays may bind to `uk-`/`jp-` facts exactly as to `us-` ones. The two
> shipped essays bind exclusively to US facts; non-US bindings are covered
> by tests (`tests/test_essays.py`).

## Closed sets

Each is a Python enum; every dispatch over them ends in
`typing.assert_never()` so adding a variant breaks the build at every
unhandled site.

**Tier** — confidence taxonomy:

| Tier | Meaning | Example |
|---|---|---|
| `A` | Official statistical series for the stated population | Census P-60 median family income, 1947→ |
| `B` | Official microdata; statistic computed by this project | IPUMS 1940 census extract |
| `C` | Reconstruction from contemporaneous surveys of a proxy population | 1901 BLS cost-of-living survey |
| `D` | Scholarly estimate or narrative; no contemporaneous survey | Soviet-era living-standards reconstructions |

Tiering rule: when in doubt, tier down and say why in `notes`.

**Panel** — the six-panel room skeleton, identical in every room so decades
and countries compare at a glance:

| Panel | Contents |
|---|---|
| `home` | Tenure, rooms, floor area, amenities (water, flush toilet, electricity, heat) |
| `budget` | Income and expenditure shares |
| `table` | The food basket |
| `day` | Work hours, earners per family, commute |
| `diffusion` | % of families with car / phone / radio / TV / fridge / internet at that date |
| `work-buys` | What an hour/day/week of the median family's work buys, in local terms |

**Basis** — what a fact's structured `amount_minor` is measured against; the
affordability axis dispatches on it:

| Basis | Meaning | Example |
|---|---|---|
| `total` | A one-time price | $1,511 for a car |
| `hourly` | A wage rate | $1.32/hr |
| `weekly` | A weekly figure | $53.29/wk |
| `monthly` | A monthly figure | ¥29,169/mo (Japan rooms) |
| `annual` | An annual figure | $3,319/yr |

**Measure** — what an affordability *anchor* denominator measures. Set on the
`Source`, optional in general but **required on any source used as a
`wage_anchor` or `income_anchor`**. Same `Basis` is necessary but not
sufficient to chain two anchors into one series (see Comparability):

| Measure | Axis | Meaning |
|---|---|---|
| `money_income` | annual | Total money income (CPS: Census F-8/P-60/FRED-MEFAIN) |
| `wages_salaries` | annual | Wages and salaries only — narrower than money income |
| `survey_family_income` | annual | Family income reconstructed from a period cost-of-living survey (pre-CPS) |
| `consumption` | annual | Consumption expenditure used as an income proxy (v2 world rooms) |
| `hourly_earnings` | hourly | Average hourly earnings of production/nonsupervisory workers |

## Comparability

The affordability axes invite cross-decade comparison, which is where an honest
museum can still lie *by juxtaposition* — with no fabricated number anywhere.
Two guards, both surfaced rather than hidden (the "render the gap" ethos applied
to comparison):

- **Concept homogeneity.** The comparator (`compare_item`) attaches a **caveat**
  to any series whose points do not share a `Measure` on a given axis — e.g. a
  "share of income" line that divides by *wages-and-salaries* in one decade and
  *total money income* in another. It flags; it does not drop the point.
- **Temporal proximity.** Within one decade room a price and its anchor should be
  near-contemporaneous; a gap wider than a few years (e.g. a 1947 price against a
  1939 wage in the bifurcated 1940s) folds a real-wage change into an axis
  presented as inflation-free, and earns a caveat.

Sub-concept nuance below the `Measure` level (e.g. *manufacturing* vs
*all-private* hourly earnings, both `hourly_earnings`) is carried by the source's
verbatim `population` string in the anchor note, not by a caveat.

## Invariants (`vitrine check`)

The gate loads everything under `data/` and fails on any of:

1. A fact whose `source` does not resolve in the registry.
2. A fact referencing an assumption id not in the ledger.
3. Duplicate fact ids anywhere in the corpus, or a fact id whose
   `<country>-<decade>` prefix disagrees with the room file it lives in.
4. Empty `label`, `value`, `unit`, or (on sources) `population`.
5. A source registered but with an empty `url` (facts must be verifiable).
6. Malformed tier/panel values (rejected at parse — the enums are the schema).
7. (Once the renderer lands) render coverage: the set of facts rendered must
   equal the set of facts checked — nothing displayed that wasn't gated,
   nothing curated that silently vanished.
8. A declared `wage_anchor`/`income_anchor` whose source declares no `measure`,
   or whose measure sits on the wrong axis (a wage anchor measuring an income
   concept, or vice versa). You cannot divide by a denominator without saying
   what it measures.
9. A `[[derived]]` entry whose operands don't resolve in-room or cross-room,
   aren't structured (amount_minor for monetary ops, quantity for
   quantity-based ops), mix currencies (for ratio/pct_of), mismatch `unit`
   (for quantity_ratio — a ratio of unlike quantities is not meaningful;
   comparison is case/whitespace-insensitive, and quantities that share a
   dimension should harmonize their unit strings and carry the distinction
   in label/notes), or divide by zero (plan 006, WI-5; unit guard WI-022).
   Derived ids obey the same prefix/uniqueness rules as fact ids.
10. An essay whose prose carries a numeral not bound to a fact (after the
    year/decade allowance), cites an unknown fact id, duplicates slugs, or
    fails the block-shape rules (plan 016's numeral gate). Chart-block slugs
    resolve against the site's arc/group/metric registries at build time —
    same as the wing and room-story registry gates — or the build fails.
11. A currency boundary crossed anywhere the truth path divides or chains
    (plan 023 WI-3): a room whose structured facts mix currencies; a
    `ratio`/`pct_of` derivation over operands of different currencies; a
    monetary series (`values_minor`) without a registered `currency` (or a
    dimensionless series with one); a `splices_from` chain across currencies;
    or an `INFLATE` pointed at a monetary series — the ratio must be an
    index, not an amount. Within-currency structure only: the museum never
    converts between currencies. Cross-nation comparison travels on the
    currency-free axes (hours-to-afford, shares), never on amounts.

CI runs `vitrine check` alongside ruff/mypy/pytest; a red gate blocks merge.

## What this model deliberately does not do

- No cross-fact arithmetic in data files (no derived values authored by
  hand). Derivations are code, in the repo, with the assumption ledger entry
  named.
- No cryptographic provenance — source cards are editorial provenance;
  regista integration would be scope creep for a static museum.
- No live data feeds. Sources are published documents; updates are commits.


### Transcription audit bindings (Plan 015)

A fact may declare an `audit` table naming a samples-relative file, extractor,
locator, target (`quantity` or `amount_minor`), decimal scale, optional source
context guards, and text encoding. It then requires a current entry in
`data/audit-ledger.toml`. The gate compares a versioned fingerprint of the
whole fact, source registration and referenced assumptions. The operator
command re-extracts the declared field and guards from the pinned file bytes.
A checked field does not validate every other numeral in a compound record.
See Plan 015 for the command, schema decisions and coverage limits.

Room presentation is allowed to adapt to the available evidence. The six
panels and stable record links remain the data organization; sparse rooms
lead with observations and identify gap-only panels separately. A documented
gap is not an observation, and an omitted illustration is not evidence that
an object was historically absent.

### Calculation audits (Plan 029)

An audit may add `calculation = { op, operands, precision, rounding, method }`.
The main `locator` is the first operand; `operands` lists subsequent addresses
in the same pinned source file. `mean` computes their arithmetic mean;
`pct_of` computes the first divided by the second, multiplied by one hundred.
Only a positive percentage denominator is accepted. `precision` is the number
of decimal places (zero through eight), and `rounding` is explicitly
`half_even` or `half_up`. `method` records the population, aggregation and
rounding rationale. The rounded result is scaled into the target unit last.

Calculation uses exact rational arithmetic over decimal source numerals.
The `json-pointer` extractor selects scalar values in original publisher
responses; numeric JSON tokens retain decimal precision. Guards can bind a
series identifier, each observation year and each monthly period. Counting
twelve rows alone is insufficient to demonstrate a complete calendar year.

Ledger version two records every raw calculation operand as well as its
result, source-byte hash and semantic fingerprint. The offline gate replays
the operands and compares the declared target. A version-one ledger can be
read for migration, but its bindings must be regenerated against the real
archive. Changes in methods, source meaning or record interpretation also
require re-audit. Source republication and statistical revision remain
editorial questions; a newly retrieved vintage is not an old download.

Editorial status belongs to the presentation registry, with a rationale.
Research holdings, focused exhibits and guided rooms express a curation
choice. A record count does not grant confidence or imply a matched household.
The Japan thematic collection selects dated observations while keeping their
source populations separate and all decade records accessible.
