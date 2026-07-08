# Verification Log — evidence of source-checked facts

This file is the evidence ledger for Plan 008. Every verification produces an
entry here: what was checked, against what source, by what method, and the
result. The log is append-only; corrections note the original value and the fix.

An entry that says "verified" without the source value beside it is not
evidence — it is a claim.

---

## WI-0: Pre-plan session verifications (2026-07-08)

**Date:** 2026-07-08
**Verifier:** umans-glm-5.2 session
**Context:** Pre-plan session that merged wi-1/us-source-survey and performed
spot-checks. These are the verifications that motivated Plan 008.

### 0a: BLS API food price labels (5 rooms)

**Source checked:** BLS Public Data API v2, catalog endpoint
**Method:** API call with `catalog: true` parameter, retrieving the official
item name for each series ID.
**Fact IDs:** us-1980s-food-prices, us-1990s-food-prices, us-2000s-food-prices,
us-2010s-food-prices, us-2020s-food-prices

| Series ID | API catalog item name | Fact's label (pre-fix) | Result |
|-----------|----------------------|------------------------|--------|
| APU0000712211 | Lettuce, iceberg, per lb. | "bread" / "Bread" | **mismatch — corrected** |
| APU0000702111 | Bread, white, pan, per lb. | "flour" | **mismatch — corrected** |
| APU0000703111 | Ground chuck, 100% beef, per lb. | "round steak" | **mismatch — corrected** |
| APU0000704111 | Bacon, sliced, per lb. | "milk" | **mismatch — corrected** |
| APU0000708111 | Eggs, grade A, large, per doz. | "potatoes" | **mismatch — corrected** |
| APU0000711211 | Bananas, per lb. | "coffee" | **mismatch — corrected** |

**Resolution:** All 5 facts corrected. Values were correct for the actual items;
only labels were wrong. Also corrected cross-reference notes in us-1950s-food-prices
that used the old wrong labels.

### 0b: Poverty rates (7 facts, 1960s-2020s)

**Source checked:** Census API `histpov2` endpoint
(`https://api.census.gov/data/timeseries/poverty/histpov2`)
**Method:** API call with `get=YEAR,PCTPOV,POV,POP` for `us`.
**Fact IDs:** us-1960s-poverty-rate through us-2020s-poverty-rate

| Year | Fact value | Census API value | Result |
|------|------------|------------------|--------|
| 1960 | 22.2% (39.9M) | 22.2% (39,850,000) | **verified** |
| 1970 | 12.6% (25.5M) | 12.6% (25,420,000) | **verified** |
| 1980 | 13.0% (29.3M) | 13.0% (29,270,000) | **verified** |
| 1990 | 13.5% (33.6M) | 13.5% (33,590,000) | **verified** |
| 2000 | 11.3% (31.5M) | 11.3% (31,580,000) | **verified** |
| 2010 | 15.1% (46.2M) | 15.1% (46,340,000) | **verified** |
| 2024 | 10.6% (35.9M) | 10.6% (35,880,000) | **verified** |

### 0c: BLS API December food price values (5 rooms)

**Source checked:** BLS Public Data API v2
**Method:** API call for December values for each series ID, each year.
**Fact IDs:** us-1980s-food-prices through us-2020s-food-prices

| Year | Series ID | API Dec value | Fact value (post-fix) | Result |
|------|-----------|---------------|----------------------|--------|
| 1980 | APU0000702111 (bread) | $0.519 | $0.52 | **verified** (rounded) |
| 1980 | APU0000703111 (ground beef) | $1.863 | $1.86 | **verified** |
| 1980 | APU0000704111 (bacon) | $1.711 | $1.71 | **verified** |
| 1980 | APU0000708111 (eggs) | $1.031 | $1.03 | **verified** |
| 1980 | APU0000712211 (lettuce) | $0.483 | $0.48 | **verified** |
| 1990 | APU0000702111 (bread) | $0.700 | $0.70 | **verified** |
| 1990 | APU0000703111 (ground beef) | $2.022 | $2.02 | **verified** |
| 1990 | APU0000704111 (bacon) | $2.283 | $2.28 | **verified** |
| 1990 | APU0000708111 (eggs) | $1.001 | $1.00 | **verified** |
| 1990 | APU0000712211 (lettuce) | $0.579 | $0.58 | **verified** |
| 2000 | APU0000702111 (bread) | $0.987 | $0.99 | **verified** |
| 2000 | APU0000703111 (ground beef) | $1.976 | $1.98 | **verified** |
| 2000 | APU0000704111 (bacon) | $3.028 | $3.03 | **verified** |
| 2000 | APU0000708111 (eggs) | $0.959 | $0.96 | **verified** |
| 2000 | APU0000712211 (lettuce) | $0.851 | $0.85 | **verified** |
| 2010 | APU0000702111 (bread) | $1.386 | $1.39 | **verified** |
| 2010 | APU0000703111 (ground beef) | $2.932 | $2.93 | **verified** |
| 2010 | APU0000704111 (bacon) | $4.160 | $4.16 | **verified** |
| 2010 | APU0000708111 (eggs) | $1.793 | $1.79 | **verified** |
| 2010 | APU0000712211 (lettuce) | $0.992 | $0.99 | **verified** |
| 2024 | APU0000702111 (bread) | $1.912 | $1.91 | **verified** |
| 2024 | APU0000703111 (ground beef) | $5.576 | $5.58 | **verified** |
| 2024 | APU0000704111 (bacon) | $6.915 | $6.92 | **verified** |
| 2024 | APU0000708111 (eggs) | $4.146 | $4.15 | **verified** |
| 2024 | APU0000712211 (lettuce) | $1.705 | $1.71 | **verified** |
| 2024 | APU0000711211 (bananas) | $0.615 | $0.62 | **verified** |

### 0d: FCC cable TV 2000s fact

**Source checked:** `samples/09-fcc/FCC-07-206A1.txt` (FCC 13th Annual Report)
**Method:** grep for subscriber/household figures in the report text.
**Fact ID:** us-2000s-cable-tv

| Claim | Source text (para. 8, 10) | Result |
|-------|--------------------------|--------|
| 110.2M TV households | "there were 110.2 million TV households" (para. 8) | **verified** |
| 95.8M MVPD subscribers | "approximately 95.8 million TV households... subscribe to an MVPD service" (para. 8) | **verified** |
| 87% of TV households | "almost 87 percent of TV households" (para. 8) | **verified** |
| 65.3M basic cable subscribers | "subscribers increased slightly to 65.3 million" (para. 10) | **verified** |
| 68.2% cable share of MVPD | "68.2 percent of MVPD subscribers received video programming from a franchised cable operator" (para. 8) | **verified** |

### 0e: Adversarial review findings (post-merge)

**Reviewer:** kimi-k2.7 (adversarial-reviewer subagent)
**Method:** Read all modified room files, cross-referenced source IDs against
sources.toml, checked arithmetic, unit consistency, and internal consistency.

| Finding | Severity | Resolution |
|---------|----------|------------|
| Gap-log.md had unresolved merge conflict markers | critical | **fixed** — rewrote file without markers |
| 1950s food-prices note cross-referenced old wrong 2024 labels | critical | **fixed** — updated to corrected labels |
| 2020s weekly-earnings value ($1,227.88) didn't match arithmetic ($30.12 × 40.7 = $1,225.88) | critical | **fixed** — corrected to $1,225.88 |
| 1960s/1970s food-price unit mismatch (dollars mixed with cents) | medium | **fixed** — converted to cents |
| 1950s weekly-earnings note claimed simple multiplication of rounded values | medium | **fixed** — clarified uses unrounded monthly averages |
| 2020s bread ratio was 13.3x (should be 13.4x) | low | **fixed** |
| FCC source registry didn't mention 2006 report | observation | **fixed** — added 2006 data point to source notes |
| Gap-log poverty count said "6 facts" (should be 7) | observation | **fixed** — corrected to 7 |

---

## WI-1 through WI-9

*(Pending — see `plans/008-verification-and-gap-filling.md` for scope and method.
Entries will be added here as each WI is completed.)*
