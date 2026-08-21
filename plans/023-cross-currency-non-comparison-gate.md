# Plan 023 — Cross-currency non-comparison gate (series layer)

**Status:** delivered 2026-08-14 (`f5ef98f`, plan-022-multi-currency line,
adopted to main via the ui/statistical-atlas merge). *This document was
backfilled 2026-08-21*: like plan 022, the work shipped without a plan file;
it reconstructs scope and acceptance from `docs/changelog.md` (2026-08-14
entry) and the commit.

**Triggered by:** plan 022 WI-3, deferred there because "the guard is only
testable once a second currency's data exists" — the UK (£) and Japan (¥)
rooms are now in the corpus, so it became mechanical.

## Scope

The series-layer remainder of multi-currency safety:

- `Series` gains a `currency` field — required iff the series carries
  `values_minor`, forbidden on dimensionless series.
- `vitrine check` rejects: an unregistered series currency; a
  `splices_from` chain that crosses currencies (an exchange rate laundered
  in through the back door); an `INFLATE` derivation pointed at a monetary
  series (the deflator must be an index, not an amount).
- `series_numeric` scales minor units by the registry's per-currency
  digits — replacing a hardcoded `/100` that would have divided a yen
  series by a hundred.
- Fact-model invariant 11 records the rule.

Room-level currency mixing and `ratio`/`pct_of` operand mixing were
already gated by the plan 022 foundation; this closes what the foundation
left at the series layer. The museum still never converts between
currencies as a truth-path number.

**Acceptance (met at `f5ef98f`):** registered-currency,
splice-currency and INFLATE-on-monetary gates each fail on a crafted
corpus and pass on the real one; per-currency minor scaling covered by
tests; mypy --strict + ruff clean; provenance and against-build gates
green.
