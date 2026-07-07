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
| `currency` | str | e.g. `"USD"`; required iff `amount_minor` is set |
| `price_year` | int? | Year the amount is quoted in |
| `basis` | Basis? | What the amount is measured against (closed set, below); required iff `amount_minor` is set |

`value` is always the as-authored display string: the museum shows what the
source said, in the source's own terms. The structured fields
(`amount_minor`/`currency`/`price_year`/`basis`) are *additional*, never a
replacement — they are optional, and when present they feed the affordability
axis (see `src/vitrine/affordability.py`) and cross-decade comparators. A fact
with no structured amount still renders; it just carries no derived
affordability figure.

A fact whose honest value is "the record is silent" is written with
`value = "no reliable record"` and tiered `D` with a note explaining why.
Rendering the gap is a feature; inventing a number is a charter violation.

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

### Room

One file per (country, decade): `data/<country>/<decade>.toml`, e.g.
`data/us/1950s.toml`. A room is `[room]` metadata plus a list of `[[fact]]`
tables. The `[room]` table carries `country` and `decade` and, optionally,
the affordability anchors `wage_anchor` (a fact id whose `basis` is `hourly`)
and `income_anchor` (a fact id whose `basis` is `annual`); the affordability
axis divides each priced fact by these. Country codes are lowercase ISO-ish
slugs (`us`, `uk`, `pl`, `ru`, `cn`, `in`, `jp`); decades are
`"1890s"`…`"2020s"`.

## Closed sets

Both are Python enums; every dispatch over them ends in
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
| `annual` | An annual figure | $3,319/yr |

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

CI runs `vitrine check` alongside ruff/mypy/pytest; a red gate blocks merge.

## What this model deliberately does not do

- No cross-fact arithmetic in data files (no derived values authored by
  hand). Derivations are code, in the repo, with the assumption ledger entry
  named.
- No cryptographic provenance — source cards are editorial provenance;
  regista integration would be scope creep for a static museum.
- No live data feeds. Sources are published documents; updates are commits.
