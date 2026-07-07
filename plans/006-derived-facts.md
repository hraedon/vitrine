# Plan 006 — Derived facts: derivations move out of the data files

**Status:** WI-1..4 implemented; WI-5 (quantity generalization) open
**Triggered by:** the 2026-07-07 external review.

## The finding

The fact model has always said: *"No cross-fact arithmetic in data files (no
derived values authored by hand). Derivations are code."* The rooms violated
it — roughly nine facts carried hand-authored arithmetic (`weekly-earnings`,
`annual-earnings`, `purchasing-power`, `week-of-work-buys`,
`home-as-income-years` ×2, `real-income-growth`, the 1901-vs-2024 share
comparisons) — and the review found that **every defect in the corpus lived in
that class, and none in primary transcriptions**:

- `us-2020s-food-expenditure-share` displayed 17.8%, a misread of CEX Table
  1400's aggregate-share column, flatly contradicting its sibling fact (13.5%)
  in the same room. Tier A badge on a wrong number.
- `us-2020s-real-income-growth` displayed "3.1x ($25,633 → $79,490)" — figures
  traceable to no source in the registry, contradicting its own note (2.4x or
  3.0x depending on deflator).
- `us-1950s-home-as-income-years` quoted the 2020s ratio as "~3.0 years" after
  the 2020s room had computed 2.58 — a cross-room echo that rotted silently.

Spot-checks of primary transcriptions against live sources (FRED CES3000000008,
AHETPI, CPIAUCNS; the Census plumbing time-series file) found zero errors. The
charter rule predicted exactly where the bodies were. This plan enforces it.

## Design

A **derived fact** is authored as structure, never as a number. The value the
visitor sees is computed at load/build time by repo code.

```toml
[[derived]]
id = "us-1950s-home-as-income-years"
panel = "work-buys"
label = "Median home value as years of median family income, 1950"
op = "ratio"
numerator = "us-1950s-median-home-value"
denominator = "us-1950s-median-income-four-person"
unit = "years of four-person median family income"
precision = 1
notes = "..."
assumptions = ["composite-family", "affordability-normalization"]
```

- **Ops (closed set, `assert_never` dispatch):** `ratio` (numerator ÷
  denominator), `pct_of` (× 100). Both operands must be structured facts
  (`amount_minor` set) in the **same room**, same currency.
- **Tier is computed, never authored:** the weakest of the operand tiers. A
  curator cannot badge a derivation stronger than its inputs.
- **Value is computed, never authored:** formatted from `precision`; `unit`
  carries the semantics. There is no `value` key to typo.
- **Provenance drawer shows the derivation:** both operand facts with their
  own values, tiers, and sources — the visitor can redo the arithmetic.
- **Gate invariants:** operands resolve in-room and are structured; same
  currency; denominator ≠ 0; id prefix and uniqueness rules shared with facts;
  assumptions resolve; render coverage counts derived ids.

### Deliberately out of scope (v1)

- **Cross-room operands** (`real-income-growth` divides a 2020s income by a
  1950s income). Cross-decade division needs the comparability machinery
  (Measure homogeneity, year-gap caveats) wired into the drawer; defer.
- **Non-monetary quantities.** `weekly-earnings` = $/hr × hours; hours and CPI
  index points have no structured representation (`amount_minor` is monetary
  minor units). Needs a `quantity` generalization — WI-5.
- **Scaled ops** (× 52 weeks, × 50 weeks). With scale factors in TOML the data
  file is programming again; when a real need accumulates, add a named op with
  the convention documented (e.g. `annualize_weekly`), not a free constant.

Until then the remaining authored-arithmetic facts stay, with their inputs and
method named in `notes` — visible debt, listed by this plan, not hidden.

## Work items

- **WI-1** model + loader: `DerivedOp`, `DerivedFact`, `Room.derived`;
  `[[derived]]` parsing. ✅
- **WI-2** derive + gate: `derive.py` evaluation (`ComputedFact`), checker
  invariants, render-coverage includes derived ids. ✅
- **WI-3** render: computed facts render in their panel with tier badge and a
  derivation drawer (operands, op, sources); manifest includes them. ✅
- **WI-4** migration: `home-as-income-years` (1950s, 2020s) converted from
  authored `[[fact]]` to `[[derived]]`; tests. ✅
- **WI-5** quantity generalization: structured non-monetary amounts (hours,
  index points), `deflate` op (CPI-adjusted cross-room ratios), then migrate
  `weekly-earnings`, `purchasing-power`, `real-income-growth`. Open.

## Acceptance criteria

1. The two migrated ratios render with computed values and weakest-input tiers;
   no `value` key exists in their TOML. ✅
2. Breaking an operand (wrong id, unstructured fact, currency mismatch) turns
   the gate red with a message naming the derived id. ✅
3. Full local gate green: ruff, mypy --strict, pytest, `vitrine check`,
   build + `check --against-build`. ✅
4. The remaining authored-arithmetic facts are enumerated here (see v1 scope)
   and nowhere claim to be transcriptions. ✅
