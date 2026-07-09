# Plan 010 — Series layer: year-by-year data for chart density

**Status:** proposed
**Triggered by:** 2026-07-09 owner discussion. The affordability view
(Plan 011) needs annual resolution to show recessions, bubbles, and policy
shocks that decade points flatten. The underlying data is already annual
(F-8 Excel, FRED monthly, BLS API, Census API) — the decade rooms
transcribe one representative year and call it "the decade." This plan
adds a series entity so charts can draw from the full annual record
without multiplying the curation burden.

## The problem

Every arc chart in the corridors has at most 13 points (one per decade).
The housing bubble (2002–2006 inflating, 2008–2012 crashing), the Volcker
recession (1980–82), the 1973 oil shock, and the pandemic distortion
(2020–2022) are all invisible at decade granularity. The data to show them
exists — F-8 has every year 1947–2024, FRED has monthly wages, the BLS API
gives monthly food prices — but the fact model has no way to express "this
source publishes a time series; here are the values."

Creating one fact per year (78 facts for F-8 income alone) would work
mechanically but is absurd curation: 78 TOML blocks, each with the same
source, tier, and population, differing only in `value` and `price_year`.
The gate would validate 78 near-identical entries. The rooms would
balloon. And the curator's intent — "this is one series" — would be lost.

## The design

A **series** is a named time series with one source, one tier, one
population, and a year→value table. It is not a fact — it does not appear
in rooms or carry a `panel`. It exists to feed charts.

```toml
# data/series/median-family-income.toml
[[series]]
id = "median-family-income-all"
label = "Median family income, all families"
source = "census-f08-allraces"
tier = "A"
unit = "USD per year, nominal"
population = "All US families, CPS money income"

[series.values_minor]
1947 = 303100
1948 = 317200
1949 = 313000
# ... one line per year through 2024
```

Note the sub-table form, not an inline table: TOML 1.0 inline tables
cannot span lines, and 78 year/value pairs on one line is unreviewable.
`[series.values_minor]` after a `[[series]]` element binds to that
element. TOML keys are always strings — the loader parses `"1947"` to
`int` and fails on any key that doesn't parse.

### Properties

- **One source, one tier, one population.** The series inherits its
  provenance from the source registry, exactly as facts do. The tier is
  uniform across all years — if a series changes methodology mid-run
  (e.g. F-8 revised vs. unrevised), it is two series with a splice caveat.
- **`values` / `values_minor` is a TOML sub-table** mapping year → numeric
  value. No strings, no display formatting — the raw number. The renderer
  formats.
- **Exactly one of `values` or `values_minor` per series.** Monetary series
  use `values_minor` in integer cents, consistent with the fact model's
  no-float-drift convention. Non-monetary series (CPI, hours, percentages)
  use `values` with floats. Declaring both, or neither, is a gate failure.
- **No `panel`, no `label` on rooms.** Series do not render in rooms.
  They render in corridors and the affordability dashboard (Plan 011).
- **Stdlib-only core.** Series loading is in the core package, alongside
  fact loading. The renderer (site extra) imports it. Architecture test
  holds: core never imports site.

### Gate invariants (new)

The gate (`vitrine check`) gains:

1. A series whose `source` does not resolve in the registry → fail.
2. A series with empty `values` / `values_minor` → fail.
3. A series whose `values` table has non-integer keys or non-numeric
   values → fail.
4. A series with a `tier` outside the closed set → fail (parse-time, like
   facts).
5. A series id that collides with a fact id → fail (shared namespace).
6. A series whose source lacks a `measure` when the series is declared as
   an affordability axis (income/wage) → fail, same rule as anchors.
7. Render coverage: every series referenced by a chart must resolve —
   a chart mark projecting a series value for year Y must find Y in the
   series's values table, or render as the gap.
8. Exactly one of `values` / `values_minor` per series → fail otherwise.
9. **Series/fact agreement:** where a decade fact and a series share the
   same source and the fact's `price_year` (or data year) appears in the
   series, the values must agree. This is the new failure mode the series
   entity introduces — the same number living in two places and drifting —
   and the gate closes it.

### Splice caveats

When two series with different measures or methodologies are plotted on
the same axis, the comparison code's existing measure-mismatch guard
fires — no new mechanism needed. A series can declare an optional
`splices_from` field naming another series id and a splice year; the
renderer draws a vertical marker at the splice point and the placard
explains the concept change. Example: Ramey women's home production
(1900–2005) splices to ATUS all-adult household activities (2003→).

## Work items

### WI-1: Series entity + loader (stdlib only)

`src/vitrine/series.py` — `Series` dataclass, `load_series(path)` that
reads `data/series/*.toml`. Returns `dict[str, Series]`. Pure stdlib
(`tomllib`, `dataclasses`). Architecture test: `series.py` must not import
anything from `site/`.

### WI-2: Gate invariants

Extend `vitrine check` to load and validate series alongside facts.
New invariant: every chart mark that references a series must resolve
(mark-coverage gate, extended). The existing `--against-build` flag now
also checks series mark coverage.

### WI-3: Populate first series (8 series)

The highest-impact series, all Tier A, all with existing or verifiable
sources:

| Series | Source | Coverage | Values |
|--------|--------|----------|--------|
| `median-family-income-all` | `census-f08-allraces` | 1947–2024 | 78 annual medians, all families |
| `median-family-income-4p` | `census-f08-allraces` | 1947–2024 | 78 annual medians, 4-person families |
| `cpi-u` | `fred-cpiaucns` | 1913–2024 | 112 annual averages |
| `hourly-earnings-total-private` | `fred-ahetpi` | 1964–2024 | 61 annual averages |
| `hourly-earnings-manufacturing` | `fred-ces-manuf-earnings` | 1939–2024 | 86 annual averages |
| `weekly-earnings-manufacturing` | new source: CES weekly earnings, mfg production & nonsupervisory | 1939–2024 (verify start) | ~86 annual averages |
| `new-car-price` | `bea-new-car-price` (ORNL TEDB Table 11.13) | 1970–2020 | 51 annual transaction prices |

The `weekly-earnings-manufacturing` series exists because Plan 011's
wage-coverage metric needs annual earnings: weekly × 52 is clean, but
hourly × hours × 52 would smuggle in a weekly-hours assumption (40 hrs
in 1950, ~34 today). Verify the CES weekly series' actual start year
before committing; if it starts later than 1939, the metric's coverage
shrinks accordingly — render the gap, don't backfill from hourly.

The `new-car-price` series exists because Plan 011's car-as-hours metric
needs an annual numerator; without it the metric renders decade points
only. The TEDB table is already the source for the 1970s–2020s decade
facts, so the series/fact agreement invariant (gate invariant 9) applies.

Plus (Tier A, decennial/annual mix):
| `median-home-value` | `census-homeownership-historical` / `census-acs-homevalue` | 1940–2024 | Decennial 1940–2000 + ACS annual 2005–2024 |

The home-value series is a splice: decennial census (1940–2000, every
10 years) then ACS (2005–2024, annual). **Decision: one series with
sparse values and a note.** Plan 011's `Metric` registry names a single
numerator id, both segments measure the same thing (self-reported owner
value), and sparse years render as the gap — which is itself the honest
display of "we only know this decennially before 2005."

**Data source:** F-8 values are in `samples/06-acs-csv/f08ar.xlsx`. CPI
values can be pulled from the BLS API (key in `samples/api.env`). FRED
wage values are in `samples/08-fred/AHETPI.xlsx`. All verifiable.

**Transcription discipline:** this WI transcribes ~500 values. Hand-typing
that many numbers is where transcription errors breed. Use script-assisted
extraction from the xlsx/API (precedent: `scripts/ipums_extract.py`) to
generate the TOML, then spot-verify a sample of each series against the
source by eye, and record a verification-log entry per series (Plan 008
convention). The script generates; a human-readable diff and the gate
verify; nothing is recalled.

### WI-4: Corridor renderer integration

The arc chart function (`render.py`) currently takes a `dict[str, str]`
(decade → fact id) and resolves each fact's `quantity` at build time.
Extend it to optionally take a series id: when a series is available, the
chart draws annual points (50–78 per arc) instead of decade points
(7–13). The decade facts remain as labeled markers on the same chart
(so the room placards still link). Facts without a corresponding series
render as before.

### WI-5: Tests

- Series loader: loads a test series, validates fields, parses year keys
  to int and rejects non-parseable keys.
- Gate: rejects series with unresolved source, empty values, bad tier,
  both/neither of `values`/`values_minor`.
- Gate: rejects a series whose value for year Y disagrees with a decade
  fact from the same source (invariant 9).
- Mark coverage: a chart referencing a series value for a year not in
  the table renders as a gap, not a crash.
- Architecture: `series.py` does not import `site/`.

## Out of scope

- Series for survey-based data (CEX, RECS, ATUS) — these don't have
  annual data; they stay as decade facts.
- Series for diffusion metrics (vehicle ownership, telephone, etc.) —
  decennial census or sporadic ACS; not annual.
- Real-time data feeds — series are committed TOML, not live API calls.
- Cross-country series — v2 world rooms are not yet built.
