# Plan 013 — Wage anchors for the early rooms (1900s–1930s)

**Status:** proposed
**Triggered by:** 2026-07-09 project evaluation. The 2026-07-09 session
added car-price facts for the 1910s–1930s but had to strip their
`amount_minor` because those rooms declare no wage or income anchor — the
affordability corridor renders a gap for decades where the price data
exists and the wage data *also* exists, unstructured, in the same rooms.
This plan structures what is already transcribed and wires it as anchors,
so the corridor's early decades light up with real ratios instead of gaps.

## The situation

The gaps report shows the 1900s–1930s rooms each rendering
income/housing/work-buys gaps. But the raw material is mostly present:

| Room | Wage data in room today | Anchor status |
|------|------------------------|---------------|
| 1900s | `us-1900s-mens-weekly-wages` — Series D 766 hourly earnings, $0.216/hr, unstructured | `income_anchor` already set ($827.19, BLS Bulletin 49); no wage anchor |
| 1910s | `us-1910s-manufacturing-wages` — Series D 765–767, $0.260/hr, unstructured | no anchors |
| 1920s | `us-1920s-manufacturing-wages` — Series D 802–804, $0.55/hr, unstructured | no anchors |
| 1930s | `us-1930s-manufacturing-wages` — hourly figures for 1930 and 1933 in one fact, unstructured | no anchors |

All from `hist-stats-colonial-1970`, already in the source registry and
already OCR-verified for other facts. No new sourcing is required for
wage anchors; this is structuring + wiring work.

**Income anchors are a different story and stay out of scope** for the
1910s–1930s: no national family income survey exists before 1947, and
the period surveys in the registry (`bls-1918-cost-of-living`,
`bls-1935-consumer-purchases`) cover selected wage-earner families, not
the general population. The 1900s income anchor (same class of survey)
is grandfathered with its population caveat; adding more of them is a
curation decision to take separately, not a mechanical follow-on.
Where there is no income anchor, the corridor computes hours-of-work
ratios from the wage anchor and renders income-based metrics as gaps —
which is the honest shape of the record.

## Design decisions

### D1 — Manufacturing wages as the early wage anchor, disclosed

The wage anchor for 1900s–1930s is average hourly earnings of
manufacturing production workers. That is not "the median worker" — it
skews urban, industrial, male. The 1950s room already anchors on
manufacturing earnings, so the series has precedent inside the museum;
what's new is stretching it to decades where it is the *only* option.
Add an assumption-ledger entry (`manufacturing-wage-proxy`) stating the
population skew, referenced by every early wage-anchor fact. The
existing measure guard will correctly flag manufacturing-vs-total-private
mismatches in cross-decade comparisons; do not suppress it.

### D2 — The sub-cent problem, resolved by decade choice, not model change

`amount_minor` is integer cents. The 1900 figure is $0.216/hr — 21.6
cents, not representable. Do **not** widen the model (a minor-unit scale
field is churn the whole corpus pays for one decade), and do not round
(21.6 → 22 is a 1.9% error that propagates into every hours-of-work
ratio).

Instead: the anchor fact for each room picks the in-decade year whose
published hourly figure is representable in integer cents, and says so.
Series D publishes annual values; 1910 is $0.260 exactly, 1920 is $0.55,
and the 1900s/1930s candidate years must be read from the table at
execution time (the trailing-digit pattern varies by year — transcribe,
don't assume). If no year in a decade lands on a cent boundary, fall
back to the weekly-earnings figure divided at render time — but only if
that becomes necessary; decide against the table, not in advance.
The room's representative-year note already explains which year each
fact speaks for; the anchor note gains one sentence on why that year.

### D3 — Restoring `amount_minor` to the early car-price facts

Once a room has a wage anchor, the gate's priced-fact-without-anchor
rule is satisfied and the 1910s–1930s car-price facts get their
`amount_minor` restored (the values are already in the fact notes from
the 2026-07-09 session — restore from the source table, verify against
notes). The corridor's "A new car" line then spans 1900s–2020s with
real points. The wholesale-price methodology caveat from Plan 011 WI-5
covers the interpretation.

## Work items

### WI-1: Assumption-ledger entry `manufacturing-wage-proxy`

States the population (manufacturing production workers), the skew
(urban, industrial, male), and why it stands in for "the median worker"
in decades with no broader wage series. Referenced by every 1900s–1930s
wage-anchor fact.

### WI-2: Structure and anchor the 1910s and 1920s wage facts

Split the composite wage facts (hourly + hours + weekly in one `value`
string) so the anchor fact carries one structured quantity: `basis =
"hourly"`, `amount_minor`, `currency`, `price_year`, quantity verbatim
in `value` per the gate. The hours-per-week and weekly-earnings numbers
stay in the room (day panel or notes) — they are good exhibits, they
just can't be the anchor's payload. Wire `wage_anchor` in each `[room]`.

### WI-3: Structure and anchor the 1930s wage fact

Same treatment; the existing fact holds 1930 and 1933 values in one
label. Pick the representative year per D2, split accordingly. The
Depression-era collapse ($0.55 → $0.44) is exactly the kind of thing
the room's prose should keep even though the anchor carries one number.

### WI-4: 1900s wage anchor per D2

Resolve the sub-cent question against the Series D table, structure
`us-1900s-mens-weekly-wages` (or a new fact if splitting is cleaner),
wire `wage_anchor`. The room keeps its existing income anchor; having
both makes the 1900s the only early room with the full affordability
treatment.

### WI-5: Restore car-price `amount_minor` (1910s–1930s)

Per D3. Re-run the gate; the corridor and the rooms' work-buys panels
pick the points up. Extend the week-of-work derived facts
(Plan 006 machinery, commit d09d994 precedent) to the newly anchored
decades where an income anchor also exists (1900s only, for now).

### WI-6: Verification and tests

- Verification-log entries for every transcribed value (Plan 008
  convention) — Series D page scans are in the samples archive.
- Gate run: no priced-fact-without-anchor failures; anchor basis and
  amount_minor rules satisfied.
- Test: the affordability corridor "A new car" line renders points for
  1910s–1930s; the early rooms' work-buys panels render ratios where an
  anchor supports them and gaps where none does (income-based metrics in
  1910s–1930s stay gapped).

## Out of scope

- Income anchors for 1910s–1930s (see above — separate curation
  decision with real population-skew questions).
- The 1890s room (its own effort; the 1890–91 Commissioner of Labor
  survey is registered but the room doesn't exist yet).
- Any change to the fact model or tier vocabulary.
- Annual wage series before 1939 (Plan 010's manufacturing series
  starts at the FRED CES boundary; extending it backward from Historical
  Statistics is possible but belongs to a future series-expansion pass).
