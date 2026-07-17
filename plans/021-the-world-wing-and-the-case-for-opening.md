# Plan 021 — The world wing, and the case for opening the doors

*A north-star roadmap. This plan does not itself land code; it names the
promise, argues what "living up to it" means, and sequences the plans
(022–026) that get there. Phase 0 (the keystone) is detailed enough to
execute directly.*

## Where we are, honestly

The US wing is finished and good: 13 decade rooms (1900s–2020s), 456 facts,
zero Tier D estimates, 16 structural gaps rendered as gaps rather than
papered over. The site renders three surfaces — rooms, corridors, walkthrough
— every chart mark carrying the fact id it projects, a mechanical gate that
reddens the build if a number can't name its source. The provenance
discipline has been stress-tested in anger: the recurring finding across
Plans 006/015/020 is that transcription of obscure table cells is clean and
the *famous headline numbers* are the ones that arrive wearing a fake
citation. The machine that catches that is real and working.

And yet the README promises a museum of **seven nations**, and one is built.
It promises something you can *visit*, and it is private. It promises
"provenance under glass," and today the glass shows the source *card* but not
the *chain* — a visitor is asked to trust that the number came from the cited
table; they cannot yet watch it do so. The plan queue is empty. This is the
moment to say what the finished museum is, and build toward it on purpose.

## What would make it compelling — the four pillars

### Pillar I — The world wing is the whole point

"The median-income four-person family" is not an American object. Its power
as a lens is comparative: a 1955 family in the United States mid-boom, a 1955
family in the People's Poland queuing in a shortage economy, a 1955 family in
Japan at the start of the miracle — same abstraction, radically different
lived texture, each measured by a different statistical apparatus with its own
honest floor. The US wing alone is a good exhibit. The world wing is the
*thesis*: that ordinary life across the 20th century can be assembled from the
public record, rigorously, and made comparable without flattening the
differences the data itself insists on (consumption vs. income in India,
suppressed prices and queue-time in the command economies, urban/rural bifurcation
in China and India). This is the pillar that turns rooms into an argument.

The honesty rule gets *harder* and therefore more valuable abroad: nominal
incomes in incomparable currencies, official statistics that measured
different populations, decades where the record simply does not exist for a
median family (and must render as a gap). Building this wing well is the
strongest possible demonstration of what the whole project claims.

### Pillar II — The comparison instruments (owner-endorsed, still unbuilt)

Two experiential surfaces the owner endorsed back in the Plan 007 era and we
never built:

- **Curated epoch comparisons** — deliberate side-by-side decades (and, once
  Pillar I lands, side-by-side *nations*), not the exhaustive pairwise grid we
  already generate, but a small set of chosen confrontations that carry
  meaning (1900s vs 2020s US; 1950s US vs 1950s UK).
- **The budget-basket cutaway** — the household budget rendered as a physical
  cutaway you zoom into: food, shelter, clothing, transport as chambers whose
  proportions are the actual expenditure shares, with the sourced number
  behind each. The budget panel is the emotional core of the family portrait;
  right now it is a list. Made a cutaway, it becomes the thing people remember.

These are what separate "a well-sourced dataset with a renderer" from "a
museum a stranger wants to walk through."

### Pillar III — Provenance you can audit *as a visitor*

vitrine's differentiator is not that it has sources; every dataset has
sources. It is that the sourcing is *on display and mechanically enforced*.
The maximal version makes the chain itself an exhibit: from any rendered
number, a visitor can walk back to the specific table/row in the cited
primary source, see the tier reasoning, and see the gaps as deliberate rather
than missing. WI-023 names the deepest version of the discipline — link-check
proves a URL *resolves*, not that it *serves the described document* (the
f08a/f08ar incident: a real file at a valid URL that was the wrong table). A
"provenance drawer" the visitor can open, backed by a stronger verification
gate, converts vitrine's central claim from *asserted* to *demonstrable*. This
is the pillar most aligned with the portfolio's temperament and with the
owner's own reason for building things this way.

### Pillar IV — Open the doors

A museum nobody can enter has not met its promise. The public flip is
mechanically unblocked — the identifier gate and its CI secret are both in
place. What remains is a written sanitization/publication review, an entrance
that states the thesis and the honesty rule before the first room, and the
deploy (ghcr + k8s already wired). Opening is not a victory lap; it is the
acceptance test for every other pillar, because a stranger's eye is the only
one that has never seen the data before.

## Sequencing — Plans 022–026

The pillars are not strictly ordered, but there is a keystone and a natural
critical path:

- **Plan 022 — Multi-currency foundation** (Phase 0, detailed below). The
  keystone. v2 is blocked on the code assuming USD. Small, typed,
  gate-enforced. Nothing in Pillar I can be honest until this lands.
- **Plan 023 — The United Kingdom** (Pillar I, first nation). Owner's pick for
  v2-first: richest data outside the US, long official series (ONS/BoE
  historical), a currency that shares the money-family reasoning. Proves the
  country-generalization of the fact model, the per-nation caveat ledger, and
  the world-comparison surface end to end on one nation before we scale to six.
- **Plan 024 — The budget-basket cutaway + curated confrontations** (Pillar
  II). Buildable independently of Pillar I on the US corpus; gains a second
  dimension once the UK exists.
- **Plan 025 — The provenance drawer + document-fidelity gate** (Pillar III).
  Absorbs WI-023. Independent of the others; can run in parallel.
- **Plan 026 — Opening** (Pillar IV): publication review, entrance experience,
  public flip, deploy verification. Gated on 023 (at least one world room) and
  025 (the audit surface is the thing worth showing a stranger).

Then the remaining nations (Poland, Russia, China, India, Japan) each become a
Plan-023-shaped unit, cheaper each time as the country-generalization hardens.

## Phase 0 / Plan 022 — The multi-currency foundation (the keystone)

**The problem.** The fact schema already carries `currency`, `amount_minor`,
`price_year`, and `basis` on monetary facts, but the *code* still assumes
dollars. Concretely, `derive._op_value` hard-codes `$` for the `INFLATE` and
`PRODUCT` operations (WI-021), so the first GBP derived fact would render
`≈ $12.50`. `affordability` and the chart/placard renderers make the same
assumption in subtler places. A world room cannot state an honest number
until the money layer knows what currency it is in.

This phase is deliberately *only* the money-representation layer — no UK data,
no new rooms. It is the typed spine everything in Pillar I stands on.

### WI-1: A first-class `Currency` in the core

A small, closed registry (stdlib-only, in `model.py` or a new
`src/vitrine/money.py`): ISO 4217 code → `{symbol, symbol_placement,
minor_unit_digits, decimal/group separators}`. Seed it with USD and GBP; adding
a currency is one registry entry. `assert_never`-dispatched where a closed set
is switched on, per the correctness-by-construction rule. Facts already
declaring `currency` validate against the registry; a `currency` the registry
doesn't know is a red `vitrine check`.

**Acceptance:** `vitrine check` rejects an unknown currency code with a clear
message; USD and GBP both format a known amount correctly (`$1,234.50` /
`£1,234.50`); mypy --strict clean; a test asserts every registry entry
round-trips minor-units ↔ display.

### WI-2: Thread currency through derivation

`_op_value` takes the operand currency (derived from the source facts, not a
literal) and formats via the registry. `INFLATE`/`PRODUCT` render in the
operand's currency; `RATIO`/`PCT_OF`/`QUANTITY_RATIO` stay unit-free. This
also lets WI-022's unit-comparability guard key off currency: a QUANTITY_RATIO
mixing GBP and hours is a red build, not silent nonsense.

**Acceptance:** a synthetic GBP `INFLATE`/`PRODUCT` derived fact renders `£`,
not `$`; the existing US derived facts render byte-identically to today
(regression-locked); a mixed-currency derived op fails the gate with a
message naming both operands.

### WI-3: Currency-aware rendering + a cross-currency non-comparison invariant

Audit the site layer (`affordability`, `projections/*`, placards, charts) for
hard-coded `$`/USD assumptions; route money formatting through the registry.
Establish and gate the invariant that **cross-currency magnitudes are never
placed on a shared axis or arithmetic** without an explicit, sourced
conversion fact — the museum compares *lived texture and shares*, not raw
exchange-rate-converted incomes (that would be a number we can't source and a
comparison the data doesn't support). Cross-nation comparison is by
affordability, time-cost, and expenditure share, never by naive FX.

**Acceptance:** grep-level and test-level proof that no money is formatted
outside the registry; a test that a corridor/arc chart refuses to co-plot two
currencies; the US site output is unchanged (the whole US corpus is USD, so
Phase 0 is a pure refactor there — the regression gate is the safety net).

> **Status (2026-07-14):** WI-1 and WI-2 landed; the US site is byte-identical.
> WI-3's *audit* found the render path already clean — the site renders
> authored `value` and derived `value` and never re-formats money (the one hit,
> a `"USD/month"` axis *label* in `corridors.py`, is US-specific data, not a
> format path). So WI-3's remaining substance — the cross-currency
> non-comparison invariant and its gate — is genuinely testable only against a
> second currency, and moves to **Plan 023** where the UK data makes it real.

### Phasing

WI-1 → WI-2 → WI-3, each independently green (tests + `vitrine check` +
`--against-build` + mypy --strict). The entire phase must leave the US site
byte-identical; a `_site` diff against `main`'s build is the acceptance gate
for "foundation only, no behavior change."

## Out of scope (this roadmap)

- Any actual foreign-currency *data* (that is Plan 023+, and it is real
  primary-source transcription — no model-recalled numbers, ever).
- FX/PPP conversion as a truth-path number. If cross-nation money comparison
  is ever shown, the conversion factor is itself a sourced, tiered Fact with
  its methodology on the card — not a hard-coded rate.
- Narration/LLM text anywhere in the truth path (permanent charter rule).
- Photorealistic period imagery (v1 non-goal, unchanged).
