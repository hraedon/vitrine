# Plan 003 — The affordability axis + cross-decade comparability

**Status:** proposed
**Triggered by:** user request to (a) show median appliances/amenities and
dwelling size, and (b) put every priced item on **one consistent
affordability axis** so decades compare rigorously — "hours of median work to
afford" and/or "share of budget" — without the museum silently forging the
number.

## The problem this plan solves

Today `Fact.value` is a **display string** (`"$1,511"`, `"~11%"`). The only
affordability normalization that exists is **hand-authored** into `work-buys`
facts — e.g. `us-1950s-week-of-work-buys` types the literal string
`"$53.29 = 1.6% of median family income"`, and `us-1950s-home-as-income-years`
types `"2.2 years"`. That bends the charter's own rule ("derivations are
code, not authored by hand") and, worse, it is **not uniform**: nothing makes
every priced item carry a comparable figure, and nothing lets a visitor line
a 1920 radio up against a 2024 smartphone on a single axis. The fact-model
doc flags "structured numeric values (for charts and cross-decade
comparators)" as a *planned extension* — this plan is that extension.

This plan is a **prerequisite** for Plan 002: both the locale split and the
artifact-object drawers want to consume a shared, code-computed affordability
figure. Land this first.

## Design decisions (the rigor spine)

1. **Hours of median work to afford is the primary axis; share of annual
   income is secondary.** Hours-worked is *inflation-free* — it needs no CPI
   splice to compare 1900 to 2024 — and reads intuitively ("a 1950
   refrigerator ≈ 230 hours; a 2024 one ≈ 40"). It is also computable across
   the **entire** US span at an honest tier (see wage-anchor floor below),
   which "% of budget" is not.

2. **"% of budget" is offered as "% of annual income", and we say so.** True
   *expenditure share* (a good as a fraction of what the family actually
   spent) needs CEX weights, which are continuous only from 1980. Share of
   **income** is the honest denominator available 1940/1947→. We compute and
   label share-of-income; we surface true expenditure-share only where CEX
   exists, never mislabelled as "budget". This is a new assumption, not a
   footnote.

3. **Derivation is code; the display string stays.** Structured numerics are
   *additive* optional fields. The as-authored `value` string is never
   replaced (charter rule). `affordability.py` is the one place the division
   happens.

4. **A comparison inherits the weaker of its inputs' tiers, and anchor-
   population splices are shown, not hidden.** Cross-decade rigor is not
   "make the numbers line up" — it is *making the seams visible*. If the
   1900s wage anchor is a Tier-C reconstructed wage and the 1950s anchor is
   Tier-A manufacturing earnings, a comparison across them is Tier C and says
   why. Where no clean anchor exists, we render the gap.

### Wage-anchor data floor (why hours-worked is computable everywhere)

| Era | Hourly-wage anchor | Tier |
|---|---|---|
| 1964→ | AHETPI (FRED, total private) | A |
| 1909→ | BLS manufacturing production-worker hourly earnings | A |
| 1890s–1900s | MeasuringWorth / Historical Statistics production/unskilled wage series | C |
| pre-1890 | (outside the US museum's floor) | — |

Annual-income anchor = the median family income already curated per room
(P-60 1947→ Tier A; IPUMS 1940 Tier B; cost-of-living surveys 1890s–1930s
Tier C). Both anchors already exist as facts in the V0 rooms — this plan just
makes them *machine-identified* and *structured*.

---

## Model changes (concrete)

### New closed set: `Basis`

```python
class Basis(enum.Enum):
    """What a structured amount is measured against — closed set."""
    TOTAL = "total"      # a one-time price ($1,511 for a car)
    HOURLY = "hourly"    # a wage rate ($1.32/hr)
    WEEKLY = "weekly"    # a weekly figure ($53.29/wk)
    ANNUAL = "annual"    # an annual figure ($3,319/yr)
```

Every dispatch over `Basis` ends in `assert_never`, same discipline as `Tier`
and `Panel`.

### `Fact` gains optional structured fields (additive, backward compatible)

```python
@dataclass(frozen=True, slots=True)
class Fact:
    ...                              # all existing fields unchanged
    amount_minor: int | None = None  # integer minor units (cents) — no float drift
    currency: str = ""               # "USD"; required iff amount_minor is set
    price_year: int | None = None    # year the amount is quoted in
    basis: Basis | None = None       # required iff amount_minor is set
```

`amount_minor` is an **integer of minor units** (cents) on purpose: historical
prices are exact in period money and integer cents avoid float rounding in the
derivation. A fact with `amount_minor is None` is a pure display fact exactly
as today — the whole V0 corpus keeps loading unchanged.

TOML shape:

```toml
[[fact]]
id = "us-1950s-car-price"
panel = "table"
label = "Average new car price, 1950"
value = "~$1,511"          # unchanged display string
unit = "USD, nominal"
amount_minor = 151100      # NEW
currency = "USD"           # NEW
price_year = 1950          # NEW
basis = "total"            # NEW
source = "umizzou-prices-wages"
tier = "D"
```

### Room gains anchor pointers

```toml
[room]
country = "us"
decade  = "1950s"
wage_anchor   = "us-1950s-hourly-earnings-manufacturing"  # NEW → a HOURLY fact
income_anchor = "us-1950s-median-income-four-person"      # NEW → an ANNUAL fact
```

Both optional at the model level, but **required by the gate for any room that
contains a `basis = "total"` priced fact** (you can't normalize without an
anchor).

### The derivation module `src/vitrine/affordability.py`

```python
@dataclass(frozen=True, slots=True)
class Affordability:
    hours_to_afford: float | None    # price / hourly wage
    pct_of_income: float | None      # price / annual income
    tier: Tier                       # weakest of the inputs used
    anchor_note: str                 # population(s) behind the anchors, verbatim

def afford(price: Fact, wage: Fact | None, income: Fact | None) -> Affordability:
    ...  # pure; the ONLY place the division happens
```

Tier is the weakest (highest-letter) of {price.tier, wage.tier, income.tier}
for whichever outputs are produced. `anchor_note` carries the anchors'
`Source.population` strings verbatim so the seam is always legible.

---

## Work items

### WI-1 — Structured price model + affordability derivation

Add the `Basis` enum (with `basis_label` + `assert_never` dispatch), the four
optional `Fact` fields, and `affordability.py` with `afford()` and the
`Affordability` result. Loader reads the new optional fields (integer/enum
validation in the loader, same pattern as `_get_int`/`_parse_enum`). Unit
tests: cents arithmetic exactness, tier-inheritance (weakest wins), None-safe
when an anchor is absent, `assert_never` reachability.

**AC:** existing V0 corpus loads and `vitrine check` stays green with **zero**
data changes (fields are optional); `afford()` unit-tested including the
tier-inheritance and missing-anchor paths; mypy strict clean.

### WI-2 — Room anchors + gate invariants

`[room].wage_anchor` / `income_anchor` in the loader. New `check.py`
invariants:

- a fact with `amount_minor` set must also have non-empty `currency`, a
  `price_year`, and a `basis`;
- any room containing a `basis = "total"` fact must declare `wage_anchor`
  and/or `income_anchor`;
- each declared anchor must resolve to a fact **in that room** whose `basis`
  is `hourly` (wage) or `annual` (income) respectively, and that carries a
  structured `amount_minor`;
- `currency` values are consistent within a room.

**AC:** a room with a priced fact but no anchor fails the gate with a clear
message; a mis-typed anchor (e.g. pointing at a `total` fact) fails; the V0
corpus, once WI-5 tags its anchors, passes.

### WI-3 — Assumptions (the honesty ledger) + dwelling-size floor

Add to `data/assumptions.toml`:

- `affordability-normalization` — "hours to afford" = item price ÷ that
  decade's representative hourly wage; "% of income" = item price ÷ median
  annual family income; both computed by repo code, never hand-authored;
  named anchors shown in the drawer.
- `hours-vs-income-denominator` — why the primary axis is inflation-free
  hours-worked, why the secondary is share of **income** (not true
  expenditure-share), and that true "% of budget" is offered **only** where
  CEX expenditure weights exist (1980→), clearly labelled.
- `wage-anchor-consistency` — the hourly-wage anchor's measured population
  changes across the span (production/unskilled wage reconstructions pre-1909;
  manufacturing 1909→; total-private AHETPI 1964→); cross-decade comparisons
  therefore carry the weaker tier and flag the splice rather than pretending
  one continuous series.
- `dwelling-size-metric` — the durable cross-decade dwelling-size axis is
  **number of rooms** (Census of Housing 1940→, IPUMS); **square footage**
  exists only for new construction 1973→ (Census SOC/Characteristics of New
  Housing) and for existing stock ~1985→ (AHS). The `home` panel uses rooms
  as the comparable size metric and shows sq ft only where the record has it.

**AC:** all four assumptions render on the methodology page; each is
referenced by at least one fact after WI-5.

### WI-4 — Cross-decade comparator + renderer surface

The payoff. A `Comparator` projection (`src/vitrine/compare.py`): for a given
anchor or item, `afford()` across every decade that has it, producing an
ordered hours-to-afford series **plus a comparability ledger** listing each
decade's anchor tier and anchor population so splices are visible. Renderer:

- show hours-to-afford (and % of income) inline on every priced fact, computed
  at build time, never read from a data string;
- a cross-decade strip for at least one worked example (e.g. "a new car, in
  hours of work, 1900s → 2020s") with the comparability ledger beneath it;
- render-coverage invariant still holds (every rendered derived figure traces
  to a checked priced fact + its named anchors).

This is the surface Plan 002's artifact drawers reuse — the drawer's "3.2% of
annual income" line becomes an `afford()` call, not authored text.

**AC:** `vitrine build` shows a computed hours-to-afford figure on every
priced fact; the cross-decade example renders with its ledger; changing a
price in TOML changes the rendered hours with no other edit.

### WI-5 — Retrofit V0: delete hand-authored arithmetic

Tag the existing anchors and priced facts in the three V0 rooms with
structured amounts + basis; point `[room]` anchors at them; **replace** the
hand-authored arithmetic strings (`us-1950s-week-of-work-buys`,
`us-1950s-home-as-income-years`, the "computed:" weekly/annual earnings facts)
with values derived by `afford()`/the derivation module. The `value` display
string stays human-readable; the *number behind it* now comes from code. This
closes the charter-rule bend and proves the mechanism on real data.

**AC:** no `work-buys`/derived fact in the corpus contains hand-typed
cross-fact arithmetic in its `value`; the rendered figures match the
pre-retrofit ones (within rounding); `vitrine check` green; a spot diff shows
the 1950s "week of work" and "home as years of income" numbers reproduced by
code.

---

## Rigor vs. usefulness (the balance the user named)

The tool stays useful by always offering the comparison on the intuitive,
inflation-free hours axis. It stays rigorous by three mechanical guards, not
by editorial willpower:

1. **Weakest-tier inheritance** — a comparison is never more confident than
   its shakiest input, and says which input that was.
2. **Splice flagging** — where the underlying wage/income series changes
   population, the comparability ledger shows it instead of smoothing it over.
3. **Render the gap** — a decade with no honest anchor gets no forged number;
   it shows as absent on the comparator, consistent with the charter.

Comparisons are encouraged; their seams are always in view.

## Sequencing

Plan 003 lands **before** Plan 002's Phase 2/3 curation, because locale rooms
and artifact drawers both consume `afford()`. WI-1→WI-2→WI-3 are model/gate
foundation (small, mechanical); WI-4 is the visible payoff; WI-5 proves it on
the V0 corpus and removes the hand-authored arithmetic.

## Open questions

1. **Weekly basis** — the V0 corpus has a weekly-earnings fact. Keep `WEEKLY`
   in `Basis` for display fidelity, or derive weekly from hourly×hours in
   code? (Leaning: keep `WEEKLY` for authored source values, derive only the
   affordability figures.)
2. **Multiple candidate wage anchors** — some decades have both a
   manufacturing series and an all-private series. Does the room pick one
   canonical `wage_anchor`, or does the comparator show a band? (Leaning: one
   canonical anchor per room for the headline number; band is a Phase-4
   polish.)
3. **Currency across countries (V2)** — hours-worked is currency-free and
   travels to the UK/PL/RU/CN/IN/JP rooms cleanly; "% of income" needs each
   country's own income anchor. Confirm the anchor model is per-room (it is)
   so V2 inherits it without change.
4. **Rounding display** — hours to the nearest hour? nearest 5 for large
   items? Decide a single rounding rule in the renderer, not per fact.
