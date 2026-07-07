# Plan 004 — The concept-comparability guard (the measure axis)

**Status:** implemented (branch `plan-004/concept-comparability`)
**Triggered by:** review of the shipped affordability axis. Plan 003's closing
principles promised **splice flagging** — "where the underlying wage/income
series changes population, the comparability ledger shows it instead of
smoothing it over" — but only **weakest-tier inheritance** actually shipped.
The splice guard stayed prose. This plan makes it mechanical.

## The problem this plan solves

`afford()` and `compare_item` guard **basis** (a price is only divided by an
`hourly` wage or an `annual` income) and **tier** (a comparison inherits its
weakest input). They do **not** guard **concept**. `Source.population` — the
"anti-composite" field — is free text that nothing compares. So:

- An `income_anchor` measuring **wages and salaries only** (the 1940s room's
  documented 1939 figure) and one measuring **total money income** (CPS) are
  both `Basis.ANNUAL`; both pass every gate; both land on one "share of income"
  axis. The step between them is an artifact of the concept change — a **lie by
  juxtaposition**, with no fabricated number anywhere.
- The **already-shipped** V0 anchors prove this is live, not hypothetical: the
  1900s income anchor is `bls-bulletin-49-1903` (a 1901 cost-of-living survey of
  2,567 wage-earner families under an income ceiling), while 1950s/2020s use CPS
  money income. A 1900s-inclusive share-of-income series would silently mix two
  income concepts. (It is not *rendered* today only because the 1900s room has
  no priced total-basis fact to divide — the trap is armed, not yet stepped on.)
- `afford()` divides a price by an anchor with **no check that their years are
  close**; the bifurcated 1940s (1939 wartime vs 1947 postwar, near-doubling
  wages) is exactly where a within-"decade" gap distorts the inflation-free axis.

## Design decisions

1. **`Measure` is a new closed set on `Source`** (`money_income`,
   `wages_salaries`, `survey_family_income`, `consumption`, `hourly_earnings`),
   with `assert_never` dispatch (`measure_label`, `measure_axis`) like every
   other closed set. It promotes the free-text "what was measured" into the
   machine-checkable discipline the model already uses for Tier/Panel/Basis.
2. **Required only where it bites: on anchors.** A source needs no `measure`
   unless it is used as a `wage_anchor` or `income_anchor`. `vitrine check`
   fails a declared anchor whose source has no measure, or whose measure sits on
   the wrong axis (a wage anchor measuring an income concept).
3. **Comparability is surfaced, never forbidden** — the render-the-gap ethos
   applied to comparison. A mixed-`Measure` series still renders; it carries a
   **caveat** banner. We do not drop points or fail the build on heterogeneity,
   because a decade legitimately measured differently should be shown *with the
   seam visible*, not hidden.
4. **Sub-concept nuance stays in `population`.** *Manufacturing* vs *all-private*
   hourly earnings are both `hourly_earnings`; the difference rides the verbatim
   population string in the anchor note, not a caveat. (Takes a position on Plan
   003 open question #2: one canonical anchor per room; concept-level splices
   flag, industry-scope splices are disclosed in the note.) Splitting the enum
   finer is a one-line follow-up if we later want industry scope to flag too.
5. **Temporal proximity is a caveat, not a hard fail.** `afford()` records the
   largest price-vs-anchor year gap used; `compare_item` flags gaps beyond
   `_MAX_ANCHOR_YEAR_GAP` (3y). Within-decade small gaps are normal.

## Work items

- **WI-1 — `Measure` closed set + `Source.measure`.** Enum + `measure_label` +
  `measure_axis` (both `assert_never`), field on `Source`, loader parsing.
  *(model.py, loader.py)* ✅
- **WI-2 — anchor-measure invariant.** `check_corpus`: a declared anchor's
  source must declare a `measure` whose axis matches the anchor kind.
  *(check.py)* ✅
- **WI-3 — thread measures + year-gap through the derivation.** `afford()` gains
  `wage_measure`/`income_measure` params and `hours_measure`/`pct_measure`/
  `year_gap` outputs; `compare_item` looks them up and computes `Comparison.
  caveats`; renderer shows a caveat banner. *(affordability.py, compare.py,
  site/render.py)* ✅
- **WI-4 — classify anchor sources.** `measure` added to the anchor + money-
  income sources in `data/sources.toml`. *(data)* ✅
- **WI-5 — tests + spine doc.** Gate tests (no-measure fails, wrong-axis fails);
  comparator tests (mixed income concept flags, shared concept clean, wide year
  gap flags); `afford()` measure/year-gap passthrough; `measure_label`/
  `measure_axis` dispatch. `docs/fact-model.md` gains the Measure closed set,
  a Comparability section, and invariant #8. *(tests, docs)* ✅

## Acceptance criteria

1. `vitrine check` fails on a declared anchor whose source has no `measure` or a
   wrong-axis measure. ✅ (test_gate)
2. A cross-decade series mixing income concepts (survey vs money income) carries
   a caveat; a shared-concept series carries none. ✅ (test_compare)
3. The committed corpus stays green: 13 rooms, all anchors classified. ✅
4. `ruff` / `mypy --strict` / full pytest green. ✅

## Not in scope

- Splitting `hourly_earnings` by industry scope (deferred; population string
  carries it for now).
- CPI/deflator reconciliation of the price series itself (the hours axis is
  inflation-free by construction; share-of-income is nominal-over-nominal
  within a year, already correct).
- Any v2/world-room measures beyond seeding `consumption` in the enum.
