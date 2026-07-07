# Gap Log — Vitrine US Rooms

Tracking unsourced facts (Tier D "no reliable record") and thin panels across all
US decade rooms. Updated when gaps are filled or new gaps identified.

## How to read this

- **Gap (rendered):** Fact is Tier D with value "no reliable record accessible
  online" — the visitor sees the gap, not a fabricated number.
- **Gap (placeholder):** Fact is Tier D with a note like "data available via X —
  not yet transcribed" — we know the source exists but haven't extracted the data.
- **Estimate (Tier D with value):** Fact has a value from a scholarly estimate or
  secondary source. Lower confidence but not a gap.
- **Thin panel:** Panel has fewer facts than typical for the room type.

Status: 🔴 open · 🟡 in progress · 🟢 filled

---

## 1900s (19 facts, 0 rendered gaps)

| # | Panel | Fact | Type | Source needed | Status |
|---|-------|------|------|---------------|--------|
| 1 | budget | Women's weekly earnings, 1905 ($6.17) | Estimate (D) | Could upgrade to Tier A via BLS Bulletin No. 49 or 18th Annual Report | 🟡 |
| 2 | work-buys | New automobile price, 1904 ($750–$1,500) | Estimate (D) | Could upgrade via contemporary auto industry records | 🔴 |

**Notes:** 1900s is well-sourced (17 of 19 Tier A). The two Tier D estimates have
values but could be upgraded with primary sources. No rendered gaps.

---

## 1940s (16 facts, 3 rendered gaps)

| # | Panel | Fact | Type | Source needed | Status |
|---|-------|------|------|---------------|--------|
| 1 | budget | Expenditure shares, 1940s | Rendered gap | No CEX for 1940s. BLS Bulletin 1055 (1952) has food prices 1939-50 but not full expenditure shares. Would need 1942 Wartime Consumption Survey. | 🔴 |
| 2 | home | Rooms, plumbing, electricity, heating fuel | Rendered gap | 1940 Census of Housing Vol 2 (General Characteristics) has the data but full tabulations not transcribed. Census reported ~55% lacked complete plumbing in 1940. | 🔴 |
| 3 | table | Food basket, 1940s | Rendered gap | Wartime rationing (1942-46) makes 1940s food patterns non-comparable. BLS Bulletin 1055 has retail food prices 1939-50 but not household basket. | 🔴 |

**Notes:** 11 of 16 Tier A. The three gaps are structural — the 1940s had no
consumer expenditure survey, and wartime controls make expenditure data
non-representative. These may remain permanent gaps.

---

## 1950s (30 facts, 1 rendered gap, 1 estimate)

| # | Panel | Fact | Type | Source needed | Status |
|---|-------|------|------|---------------|--------|
| 1 | home | Rooms, plumbing, electricity, heating fuel | Rendered gap | 1950 Census of Housing has this data. Could also use AHS historical tables. | 🔴 |
| 2 | work-buys | Average new car price, 1950 (~$1,511) | Estimate (D) | Could upgrade via NADA historical data or BLS new-car price series. | 🟡 |

**Notes:** 28 of 30 Tier A/B. Strongest room. The housing characteristics gap
and car price estimate are the only weaknesses.

---

## 1960s (10 facts, 3 rendered gaps)

| # | Panel | Fact | Type | Source needed | Status |
|---|-------|------|------|---------------|--------|
| 1 | home | Home value, rooms, plumbing | Placeholder | Census 1960 housing data + AHS historical. Data exists, needs transcription. | 🔴 |
| 2 | day | Average hourly earnings and weekly hours | Placeholder | FRED series (AHETPI, AWHMAN). Data exists, needs pull. | 🔴 |
| 3 | work-buys | Consumer Price Index and affordability | Placeholder | FRED CPIAUCNS. Data exists, needs pull. | 🔴 |

**Notes:** 7 of 10 Tier A. Thinnest room. All three gaps are "data exists but not
transcribed" — these are the easiest to fill since the sources are already
registered (FRED, Census). **Priority target for gap-filling.**

---

## 2020s (26 facts, 0 rendered gaps)

All Tier A. No gaps. Enriched 2025-07-07 with life expectancy, vehicle ownership, and poverty rate.

| # | Panel | Fact | Source | Status |
|---|-------|------|--------|--------|
| 1 | day | Life expectancy at birth, 2023 (75.8M/81.1F) | NCHS Data Brief No. 521 | 🟢 Filled |
| 2 | diffusion | Vehicle ownership 91.5% (8.5% no vehicle) | Census ACS B25045 | 🟢 Filled |
| 3 | budget | Official poverty rate 10.6% (2024) | Census P-60-287 | 🟢 Filled |

Remaining enrichment areas (lower priority):

| # | Panel | Potential fact | Source | Priority |
|---|-------|---------------|--------|----------|
| 1 | day | Commute time / mode | ACS S0802 | Medium |
| 2 | budget | Income distribution / Gini coefficient | Census P-60 / ACS | Low |
| 3 | home | Homeownership by age/race | Census AHS | Low — already have headline rate |
| 4 | diffusion | Smartphone ownership | Pew Research | Low — have internet/broadband |

**Notes:** 2020s is now the most complete room (26 Tier A facts). Life expectancy closes the last cross-decade comparability gap — every room now has this fact.

---

## Summary

| Room | Facts | Tier A | Gaps (rendered) | Gaps (placeholder) | Estimates (D) |
|------|-------|--------|-----------------|--------------------|---------------| 
| 1900s | 19 | 17 | 0 | 0 | 2 |
| 1940s | 16 | 11 | 3 | 0 | 0 |
| 1950s | 30 | 25 | 1 | 0 | 1 |
| 1960s | 10 | 7 | 0 | 3 | 0 |
| 2020s | 26 | 26 | 0 | 0 | 0 |
| **Total** | **101** | **86** | **4** | **3** | **3** |

**Total gaps: 7** (4 rendered + 3 placeholder)
**Total estimates: 3** (Tier D with values)

### Priority order for gap-filling:
1. **1960s placeholders** — sources already registered, data exists on FRED/Census, just needs transcription. Highest ROI.
2. **2020s life expectancy** — NCHS data available online, every other room has this fact.
3. **1950s housing characteristics** — 1950 Census Housing data available via IPUMS/Census pubs.
4. **1940s gaps** — may be permanent (wartime economy, no CEX). Lowest priority.
5. **1900s/1950s estimates** — could upgrade Tier D→A with primary sources, but values are already displayed.
