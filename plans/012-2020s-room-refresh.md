# Plan 012 — The 2020s room refresh: current data, pandemic-era facts

**Status:** proposed
**Triggered by:** 2026-07-09 owner discussion. The 2020s room is the
"current" room — it already uses 2024 data for income, wages, CPI, home
values, expenditure, and poverty. But several facts are stale (car prices
from 2020, time-use from 2019, AC from 2020), and the room doesn't capture
the defining events of 2020–2024: the pandemic, the inflation surge, the
housing explosion, the remote-work shift. This plan refreshes the room to
2024 data throughout and adds facts that make the 2020s read like the 2020s,
not like a generic "latest data" page.

## Why not a separate 2024 room

A separate "2024" room was considered and rejected:

1. **The decade room is the museum's unit.** Breaking it with a year-level
   room creates an awkward overlap (2020s room + 2024 room covering the
   same period) and a maintenance question (when does the 2024 room get
   frozen? when the 2020s decade room is complete?).
2. **The 2020s room is already the "current" room.** It uses 2024 data
   for its most important facts. The fix is to make it consistently
   current, not to split it.
3. **The year-by-year drama belongs in charts, not rooms.** The pandemic
   spike, the inflation surge, the housing bubble — these are time-series
   events that a single room can't show. Plan 010 (series layer) and
   Plan 011 (affordability dashboard) handle the temporal detail. The
   room's job is the snapshot.
4. **When the decade is complete (2030), the 2020s room freezes.** If a
   new "current" room is needed, it becomes the 2030s room. No
   special-case room type needed.

The 2020s room header already says "This decade is ongoing — each fact
states its data year." This plan makes that promise true by ensuring
every fact uses the latest available data, and by adding a "data as of"
indicator in the room header.

## Data year audit

Current state of the 2020s room (31 facts):

| Data year | Facts | Action |
|-----------|-------|--------|
| 2024 | Income, wages, CPI, home value, expenditure, food prices, poverty, family count/size, weekly hours/earnings | Already current — verify |
| 2023 | Life expectancy, infant mortality, vehicle ownership | Update to 2024 provisional if available |
| 2020 | Car price (BEA ends 2020), air conditioning (RECS 2020) | Car price: find 2024 source. AC: 2020 RECS is the latest — note it. |
| 2019 | Time use (ATUS 2019), home production splice (ATUS 2019) | Update to ATUS 2024 if available; otherwise note "latest published" |

## Work items

### WI-1: Car price — close the 2020 gap

**Problem:** The BEA Average Transaction Price series (ORNL TEDB
Table 11.13) ends in 2020. The 2020s room uses $27,366 (2020), but by
2024 average new car prices exceeded $47,000 (industry sources). The
4-year gap makes the affordability corridor misleading (2020 car price
against 2024 wages).

**Options (in priority order):**

1. **BLS CPI for New Vehicles** (CUUR0000SETA01, FRED): a price index,
   not an absolute price. Could inflate the 2020 BEA base ($27,366) to
   2024: $27,366 × (CPI_new_vehicles_2024 / CPI_new_vehicles_2020). This
   is permitted arithmetic (deflation/inflation) documented in the
   assumption ledger. Tier A (BLS official series). The resulting 2024
   price would be an estimate, not a transcription — but it's a
   code-computed estimate from two Tier A sources, not a hand-quoted
   number.

2. **BLS Average Price data (APU series):** BLS publishes average prices
   for specific items but not "new car" as a single price. The CPI new
   vehicle index is the closest official series.

3. **NADA (National Automobile Dealers Association):** Industry source,
   not government. Reports average new vehicle transaction prices
   annually. **Not usable:** the closed tier set has no slot for
   industry self-reported data (Tier C is period-survey reconstruction,
   which this is not), and the charter's tier vocabulary is not being
   amended to accommodate a convenience source. Also not comparable —
   NADA includes SUVs/trucks, the BEA series does not.

**Recommendation:** Option 1 (CPI inflation of BEA base). Create a
`[[derived]]` fact with numerator = `us-2020s-car-price` (the BEA 2020
base) and op = a new `inflate` op that applies a CPI ratio — the
computation lives in `derive.py` (code, never an authored number), the
tier computes as weakest-operand per the existing machinery, and the
assumption ledger gets a new entry: `cpi-inflation-of-base-price`. Do
not author the inflated number as a plain fact; that would be exactly
the hand-computed value the derived-fact machinery exists to prevent.

**The CPI ratio:** use **annual-average** CPI new vehicles for 2020 and
2024, not January values — the BEA base is an annual figure, and mixing
an annual base with point-in-time index values is a quiet methodology
mismatch. Pull both index values from the BLS API (CUUR0000SETA01) at
execution time; the index values in earlier drafts of this plan are
recalled approximations and must not be transcribed. Expect a result
in the low $30,000s — well below industry all-vehicle figures (~$47,000)
because the BEA series excludes SUVs/trucks. The derived fact's note
explains this.

### WI-2: Update life expectancy and infant mortality to 2024

**Current:** Life expectancy 2023 (78.4 total), infant mortality 2023 (5.6).

**Available:** NCHS Data Brief No. 548 (Jan 2026) has provisional 2024
life expectancy: male 76.5, female 81.4 (provisional). The source
registry's `nchs-nvss` entry already notes this.

**Action:** Update the 2020s life expectancy fact to 2024 provisional,
transcribing the total figure from the data brief itself (the ~79.0 here
is a recalled approximation — verify). Update notes to cite the
provisional data brief and mark the value provisional. Tier stays A
(NCHS official provisional data). Update infant mortality to 2024
provisional (5.34 per 1,000 if confirmed by the data brief — verify).

### WI-3: Update time-use to 2024

**Current:** ATUS 2019 data (sleeping 8.84 hrs, working 3.26 hrs). The
`us-2020s-time-use` fact and `us-2020s-home-production-splice` fact both
reference 2019 data.

**Available:** ATUS 2024 data (Table A-1, `samples/13-atus/a1-2024.pdf`
is in the archive). The 2024 data should be transcribed and the fact
updated. The home-production splice fact should reference ATUS 2024
instead of 2019.

**Action:** Read `samples/13-atus/a1-2024.pdf`, extract the 2024
time-use averages, update the fact. `a1-2025.pdf` also exists in the
archive, but **use the 2024 table**: the room's income and wage anchors
are 2024, and a 2025 time-use fact would sit ahead of every comparison
denominator and the room's `data_as_of` (WI-6). Rule: facts in the
current room use the latest data **up to the anchor year**; note the
newer release's existence in the fact notes so the next refresh (when
anchors move to 2025) picks it up.

### WI-4: Add pandemic-era event facts

The 2020s room currently reads like a generic "latest data" page. These
facts would make it read like the 2020s.

> **Every number below is a recalled illustration of the fact's shape,
> not a value to transcribe.** The executing agent transcribes from the
> named source, never from this plan. (One of the drafted figures below
> was arithmetically wrong — a 50% change written as 53% — which is the
> demonstration of why.)

1. **Remote work rate:** shape: "N% of workers worked from home at least
   one day per week (2023)." Source: ACS or BLS/ATUS — pick one and
   transcribe its figure with its own population definition. Captures
   the permanent shift in work location.

2. **Inflation surge:** shape: "CPI rose N% in 2021 and N% in 2022."
   Source: BLS CPI. The fact **must state its basis** — December-to-
   December and annual-average changes differ materially for 2022
   (roughly 6.5% vs 8.0%), and any "highest since 19XX" claim is only
   true relative to a stated basis. Transcribe both the figures and the
   comparison year from BLS, don't reconstruct them.

3. **Housing price surge:** state the two endpoints only — median home
   value in 2019 and in 2024 (ACS B25077), each transcribed. If the
   percentage change is worth showing, it is a `[[derived]]` fact over
   the two endpoint facts, not an authored number: an authored
   percentage over two other facts is exactly the cross-fact arithmetic
   the charter forbids.

4. **Used car price spike:** source is the **BLS CPI used cars & trucks
   index (CUUR0000SETA02)** — Tier A. The Manheim index was considered
   and rejected: the closed tier set has no slot for industry
   self-reported data and the charter is not being amended for it. The
   CPI index shows the same supply-chain story with official provenance;
   as an index it states percentage change directly, no cross-fact
   arithmetic needed.

5. **Broadband adoption:** Already a fact (78%). Enrich with the
   pandemic-era jump only as two transcribed endpoints (same rule as
   item 3); verify the earlier year's figure from the same ACS table,
   same population, or don't pair them.

Each fact needs a source, tier, and population. All are Tier A (BLS,
Census).

### WI-5: Vehicle ownership update

**Current:** 91.5% (2023 ACS B25045).

**Available:** ACS 2024 data may be available (ACS 1-year estimates for
2024 were released in late 2025). Check Census Reporter for B25045 2024.

**Action:** If 2024 data is available, update the fact. If not, note
"latest available: 2023" in the fact notes.

### WI-6: "Data as of" indicator

Add a room-level metadata field `data_as_of` to the `[room]` table:

```toml
[room]
country = "us"
decade = "2020s"
data_as_of = "2024"
wage_anchor = "us-2020s-hourly-earnings"
income_anchor = "us-2020s-median-income-four-person"
```

The renderer displays this in the room header: "Data as of 2024 (decade
ongoing)." Other rooms don't need this field — only the current decade.

### WI-7: Verify updated facts against sources

Every updated fact gets a verification-log entry, same as Plan 008.
Priority: car price (CPI inflation computation), life expectancy (2024
provisional), time use (ATUS 2024).

## Dependencies

- **No hard dependency on Plans 010/011.** This plan can execute
  independently. The series layer and affordability dashboard add the
  temporal context; this plan makes the snapshot current.
- **Plan 010 (series layer)** would make WI-1 (car price) easier: instead
  of a CPI-inflated estimate, a series could include 2021–2024 values if
  a source is found. But Plan 010 is not blocking.

## Out of scope

- Adding a "current snapshot" page type (the 2020s room IS the current
  room).
- Real-time data updates (the room is a committed TOML file, not a live
  feed).
- 2025 data (most 2025 data won't be published until 2026 — the room
  uses the latest available at time of curation).
