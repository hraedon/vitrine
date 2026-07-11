# Plan 016 — The docent layer: prose that cannot misquote its own museum

**Status:** draft
**Triggered by:** 2026-07-11 deep-dive over the evidence base. The corpus now
*proves* several century-scale stories — the single-earner wage falling from
near-parity with median family income, women's home production flat for
seven decades then falling off a cliff (the Plan 005 revised thesis), food's
budget share collapsing, the mortality revolution (Plan 014's arcs), the
healthcare cost transformation. No surface tells them. Rooms show placards;
corridors show lines; the connective narrative a real museum's docent
provides is absent — and it is absent for a good reason: every defect in
this project's history was a hand-authored number in prose or notes.
This plan adds narrative without re-admitting that failure mode.

## The problem

1. **The museum has evidence but no voice.** A visitor in the corridors sees
   that the single-earner-wage-coverage line falls; nothing tells them this
   traces the death of a social norm, or connects it to the home-production
   cliff two charts away. The thesis work (Plan 005) has no rendered home.
2. **Free prose is the proven defect vector.** The 2026-07-07 review found
   zero transcription errors and five hand-authored-arithmetic/prose errors.
   Writing essays with numbers typed into markdown would reintroduce exactly
   the drift the fact model was built to kill.
3. **Notes fields are already straining to carry narrative** (cross-room
   comparisons hand-quoted in `notes`, which the model explicitly forbids
   for derived facts). The pressure needs a sanctioned outlet.

## Design

Essays are data: curated files whose prose interpolates facts by id, with a
gate that makes an unbound numeral a red build. The docent may interpret;
the docent may not quote from memory.

### The essay file

`data/essays/<slug>.toml`:

```toml
[essay]
slug = "one-paycheck"
title = "One paycheck"
standfirst = "How a single manufacturing wage stopped covering the median family."

[[block]]
kind = "prose"
text = """
In 1950 the median four-person family reported {fact:us-1950s-median-income-four-person}
a year, and fifty-two weeks at manufacturing weekly earnings came within a
few percent of covering it..."""

[[block]]
kind = "chart"
metric = "single-earner-wage-coverage"

[[block]]
kind = "prose"
text = """..."""
```

| Block kind | Fields | Renders as |
|---|---|---|
| `prose` | `text` | Ivory docent card |
| `chart` | exactly one of `arc`, `group`, `metric` | The existing build-time SVG for that arc / arc-group / affordability metric, reused verbatim |

Block kinds are a closed enum, `assert_never`-dispatched. Chart references
resolve against `curation.py` registries at build; an unknown slug is a red
build (mark coverage extended to essays).

### The interpolation

`{fact:<id>}` renders the fact's as-authored `value` plus its tier chip,
hyperlinked to the placard in its room — provenance visible *inside the
sentence*. `{fact:<id>:label}` renders the label instead (for referring to
a fact without quoting it). Derived facts interpolate identically (shared
id namespace). Unknown id: red build.

### The numeral gate

After stripping interpolations, `vitrine check` scans every prose block for
numeric tokens. Allowed bare: four-digit years 1850–2035, decade words
(`1950s`), and ordinals written as words. **Any other numeral fails the
build** — percentages, dollars, hours, counts, "nearly 40" — with an error
naming the essay, block, and token. The curator's only way to put a number
in prose is to bind it to a fact.

Two honest limits, stated here rather than discovered later:

- **Verbal arithmetic** ("tripled", "nearly half") is words, so the gate
  cannot catch it. House rule: prefer a derived fact or the chart; where a
  verbal comparison is genuinely editorial, it is the docent's judgment on
  display, same status as an arc's `caveats`. The gate closes the numeral
  channel; the review process (and Plan 006's derived facts) covers ratios.
- **Selection is editorial.** Which facts an essay cites is a choice; the
  essay page carries the composite-family disclaimer strip and a standing
  "docent's interpretation — every figure links to its placard" notice.

### The surface

A new top-level `essays/` section ("Docent tours" in the index nav): one
page per essay — standfirst, prose cards interleaved with the charts they
discuss, same tokens/type as the rest of the museum (design-spec applies;
no new colors; no JS). Essays index page lists tours with standfirsts.
The three curated-epoch stops (1900s/1950s/2020s walkthrough) link to
relevant tours; rooms link to tours that cite them (computed, not
hand-maintained).

### Seed essays (curation WIs, written with sources on screen)

1. **One paycheck** — single-earner-wage-coverage metric + median-income
   facts + the manufacturing-wage-proxy assumption made narratively legible.
2. **The work that moved** — the Plan 005 revised thesis: home-production
   by sex (Ramey arcs), the flat-then-cliff shape, productivity dividend
   into standards not leisure; the concept-splice caveat carried honestly.
3. **How death changed** — Plan 014's mortality-revolution and
   healthcare-cost arc groups, once landed (dependency noted below).

## Work items

### WI-1: Model + loader + numeral gate

`Essay`/`Block` types, loader for `data/essays/`, interpolation resolution,
the numeral gate with its allowlist, mark-coverage extension.

**Acceptance:** fixture essay with a bound numeral passes; the same essay
with one bare `$3,675` fails naming block and token; unknown fact id and
unknown arc slug each fail. `vitrine check` green with zero essays present.

### WI-2: Renderer

Essay pages + index section, chart-block reuse of existing SVG builders,
tier chips inline in prose, disclaimer strip, room↔tour backlinks.

**Acceptance:** `vitrine build` renders a fixture essay; every interpolated
figure in the HTML carries `data-fact-id`; link-checker passes; no new
design tokens introduced.

### WI-3: Essay 1 — "One paycheck"

**Acceptance:** gate green; every numeral interpolated; prose reviewed
against each cited placard in one sitting (the adversarial-review pass this
suite already practices).

### WI-4: Essay 2 — "The work that moved"

**Acceptance:** as WI-3; the ATUS/Ramey concept splice appears in the prose
as a stated limit, not smoothed over.

### WI-5: Essay 3 — "How death changed"

Depends on Plan 014 WI-1/WI-2 (mortality + healthcare arcs) landing first.

**Acceptance:** as WI-3.

## Phasing

| Phase | WIs | Effort | Dependency |
|---|---|---|---|
| 1 | WI-1 | Medium | None |
| 2 | WI-2 | Medium | WI-1 |
| 3 | WI-3, WI-4 | Editorial — low code, high care | WI-2 |
| 4 | WI-5 | Editorial | Plan 014 arcs |

## Out of scope

- Audio/long-form "exhibition catalog" formats.
- Per-room auto-generated summaries (generation is the enemy; essays are
  curated or they don't exist).
- Any model-written historical claims. Essays are authored in-session with
  the cited sources open, like facts — the interpolation gate checks the
  numbers, the adversarial-review pass checks the words.
- Cross-room derived facts to support essay ratios (tracked as Plan 006
  WI-5; essays work without them).
