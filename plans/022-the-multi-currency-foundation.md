# Plan 022 — The multi-currency foundation

**Status:** WI-1/WI-2 landed 2026-07-14 in commit `79e34fe`; WI-3 deferred to
plan 023. *This document was backfilled 2026-07-28* (the work shipped without
a plan file, found in the 2026-07-28 review); it reconstructs scope and
acceptance from the commit, `docs/changelog.md` (2026-07-14 entry), and
`src/vitrine/money.py`.

**Triggered by:** plan 021 (the world wing). A second country's rooms mean a
second currency, and the pre-022 derivation layer formatted every monetary
result with a hardcoded `$` (tracked as WI-021) — acceptable for a USD-only
corpus, a silent lie the moment a GBP derived fact rendered.

## Scope

### WI-1: the money layer

`vitrine.money`: a closed currency registry (`CURRENCIES`, seeded USD + GBP)
with per-currency formatting and an `UnknownCurrency` guard. The museum
**never converts** between currencies as a truth-path number — this layer
represents and formats amounts within a single currency; FX/PPP is out of
scope by charter.

### WI-2: currency-aware derivation and the gate

- Derivation threads the operand's currency through `_op_value`, so
  `INFLATE`/`PRODUCT` render in the fact's own currency (a GBP derived fact
  renders `£`, closing WI-021).
- `vitrine check` rejects a priced fact whose `currency` is not registered in
  `vitrine.money.CURRENCIES`.

**Acceptance (met at `79e34fe`):** the US corpus rebuilds byte-identical
(108 files, identical checksums) — USD formatting provably unchanged; 220
tests green (10 new: money layer, GBP INFLATE/PRODUCT, unknown-currency
gate); mypy --strict + ruff clean; provenance and against-build gates green.

### WI-3 (deferred to plan 023)

Site-layer money-formatting audit + a cross-currency non-comparison gate.
Deferred because the render path already renders authored `value` / derived
`value` strings and never re-formats money — the guard is only testable once
a second currency's data exists to guard against.

## Design notes

- Adding a currency is one entry in `CURRENCIES` — the registry is the
  schema, same pattern as the `Tier`/`Panel` closed sets.
- The foundation-only invariant (byte-identical rebuild) is the same
  equivalence discipline plans 018/019 used for UI recovery: land the
  abstraction, prove nothing moved, then build on it.
