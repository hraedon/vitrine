# Plan 008 — Post-merge verification and gap filling

**Status:** proposed
**Triggered by:** 2026-07-08 session. The `wi-1/us-source-survey` merge brought
in 67 new facts and 13 new sources. A spot-check found that every BLS API food
price fact (5 rooms) had mismatched item labels — values correct, labels wrong.
Poverty rates were verified against the Census API and matched exactly. This
plan systematically verifies the rest and fills standing gaps.

## The lesson (again)

The AGENTS.md verification lesson says: *"hours and obscure table cells
transcribe clean; famous headline numbers are the ones that arrive from model
memory wearing a fake citation."* The food price label swap confirmed it — the
values were correct (pulled from the API), but the labels were assigned by
pattern-matching, not by reading the BLS catalog. The poverty rates were
verified and matched. Everything in between is unverified.

## Companion file

`docs/verification-log.md` is the evidence ledger. Every WI below produces an
entry there: what was checked, against what source, by what method, and the
result (verified / mismatch / corrected). The log is append-only; corrections
note the original value and the fix. The log is the proof that verification
happened — "trust me" is not a verification result.

---

## Phase 1 — Verify merged data (urgent)

Every fact that arrived in the merge gets checked against its cited source.
Priority order is by blast radius (most facts at risk first).

### WI-1: Ramey home-production hours (28 facts, 10 rooms)

**Scope:** `us-*-home-production-*` facts in every room except 1990s (gap) and
2010s (gap). Also the 1920s component breakdown and the 2020s splice note.

**Check against:** `samples/14-ramey/Home_Production_published.pdf` — Tables 6A
(women's weekly hours) and 7 (men's weekly hours), and Table 3 (1920s component
breakdown). Extract via pymupdf (the PDF has a text layer).

**Method:** Open the PDF, locate each table, compare every benchmark-year value
to the fact's `value` field. Record in verification-log with the table number,
row, and column.

**Risk:** Ramey's values are obscure table cells — the verification lesson
predicts these transcribe clean. But 28 facts is a large surface area, and the
values were OCR'd by a prior session.

### WI-2: Heating fuel arc (7 facts, 1940s-2010s)

**Scope:** `us-*-heating-fuel` and `us-*-heating-fuel-gap` facts across
1940s, 1950s, 1960s, 1970s, 1980s, 2000s, 2010s, 2020s rooms.

**Check against:** `samples/05-census-housing/fuels1940.txt` through
`fuels1980.txt` (Census Historical Housing Tables). RECS data for 2000s/2010s
(verify against EIA published tables, not the samples PDFs — those were
OCR'd and could carry OCR errors).

**Method:** Read each `fuels*.txt` file, locate the US row, compare coal/gas/
electric/oil percentages to the fact values. For RECS years, cross-check
against EIA's published summary tables (accessible via web).

### WI-3: AC diffusion arc (7 facts, 1960s-2020s)

**Scope:** `us-*-air-conditioning` and `us-*-ac-*` facts.

**Check against:** CEX 1960-61 (p.15, already OCR'd in
`samples/15-ocr-output/ocr_cex_1960_tables/`) for the 1960s value. RECS 1978,
1993, 2001, 2009, 2015, 2020 for the others — check against EIA published
summary tables, not the OCR'd PDFs.

**Method:** For 1960s: read the OCR output, find the AC line, compare. For
RECS years: fetch EIA summary tables from the web (EIA.gov is accessible). The
2020s room already cites RECS 2020 — verify the 88% figure.

### WI-4: Statistical Abstract food prices (2 facts, 1960s-1970s)

**Scope:** `us-1960s-food-prices` and `us-1970s-food-prices`.

**Check against:** `samples/01-statistical-abstracts/1970.zip` — unzip, find
Table 530 ("Average Retail Prices of Selected Foods"), compare bread, round
steak, milk, potatoes, eggs values.

**Method:** Unzip the Statistical Abstract, extract the table (may need OCR if
scanned), compare each price to the fact's `value` field. These are the only
food price facts not sourced from the BLS API — they came from a printed
compendium, so transcription errors are possible.

### WI-5: CEX expenditure shares (5 facts, 1970s-2010s)

**Scope:** `us-*-expenditure-shares` and `us-*-food-basket` facts that cite CEX
data.

**Check against:**
- 1970s: `samples/02-cex/cex-1972-73-integrated.pdf` (Bulletin 1992, Table 2)
- 1980s: Wayback Machine CEX 1985 tables (URL in fact notes)
- 1990s: Wayback Machine CEX 1996 tables
- 2000s: Wayback Machine CEX 2005 tables
- 2010s: `samples/19-cpi-tables/cu-size-2013.xlsx` or CEX Table 1400

**Method:** For the 1970s, use pymupdf to extract Table 2 from the PDF. For
1980s-2000s, fetch the Wayback URLs cited in the fact notes. For 2010s, open
the Excel file. Compare expenditure shares and food basket amounts.

**Risk:** The 2020s room had a famous error here (17.8% vs 13.5% — a misread of
the aggregate-share column). The 1970s-2010s facts from the merge may carry
similar column-misread errors.

### WI-6: Cable TV and vehicle ownership (5 facts)

**Scope:** `us-*-cable-tv` (1980s, 1990s, 2000s, 2010s) and
`us-1970s-vehicle-ownership`.

**Check against:**
- 1980s cable: NCTA Cable History Timeline (cite in fact notes)
- 1990s cable: NCTA (same)
- 2000s cable: `samples/09-fcc/FCC-07-206A1.txt` (already read this session —
  verify the 65.3M figure against para. 10 and Table B-1)
- 2010s cable: `samples/09-fcc/DA-17-71A1.pdf` (FCC 2017 report)
- 1970s vehicle: `samples/02-cex/cex-1972-73-interview-v1.pdf` (Bulletin 1997,
  automobile ownership line, p.669)

**Method:** Read each source, locate the cited figure, compare. The FCC 2006
data was already verified this session; the others need checking.

---

## Phase 2 — Fill remaining gaps

### WI-7: Infant mortality arc (1950s-2010s)

**Scope:** Add `us-*-infant-mortality` facts for 1950s, 1960s, 1970s, 1980s,
1990s, 2000s, 2010s. Currently only 1900s (~100) and 2020s (5.6) have facts.

**Source priority:**
1. Historical Statistics Bicentennial Edition, Series B 1-4 (scanned images —
   needs OCR via the local OCR host; install pymupdf or pdftoppm first)
2. NCHS National Vital Statistics Reports (fetch specific reports from
   cdc.gov — these have historical tables with decade-representative values)
3. CDC WONDER system (may have an API for historical mortality data)

**Method:** Find a primary source with year-by-year infant mortality rates.
Transcribe the value for a representative year in each decade. Tier A (NCHS
official series). If the Historical Statistics is the only source for early
decades, tier down to A with a note (it's an official compendium, not a
calculated estimate).

**Blocker:** pymupdf/pdftoppm not installed on this machine. The OCR host is
available but needs page images rendered from the PDF.

### WI-8: Vehicle ownership arc (1960s, 1980s-2000s)

**Scope:** Add `us-*-vehicle-ownership` facts for 1960s, 1980s, 1990s, 2000s.
Currently only 1970s (80.1%, CEX) and 2020s (91.5%, ACS) have facts.

**Source:** Census decennial housing tables — the 1960, 1980, 1990, 2000
censuses all asked about vehicles available. Check:
- `www2.census.gov/programs-surveys/decennial/tables/time-series/` for vehicle
  tables (the resource-hunt notes coh-vehicles and coh-auto returned 404 — try
  coh-ownerchar which exists in samples)
- Statistical Abstract various editions for "vehicles available" tables
- Census 1990/2000 long-form data via Census API or Census Reporter

### WI-9: Upgrade 1950s car price (last Tier D)

**Scope:** `us-1950s-car-price` — currently Tier D, value ~$1,511, identified
as the Ford Custom price (not the overall average).

**Source leads (from resource-hunt):**
- BLS Bulletin 1097 (1950 Consumer Expenditure Survey) — may have vehicle
  purchase price data. On FRASER.
- Census Statistical Abstract 1953 — check "Motor vehicles" table.
  `samples/01-statistical-abstracts/1953.zip`
- NADA historical data (not in samples — would need to find online)

**Goal:** Either find a primary source confirming $1,511 as the average new car
price (upgrade to Tier A), or correct the value and re-tier. If no primary
source is findable, keep Tier D but update the note to say "Ford Custom price,
not overall average" (which Hermes already did).

**On completion:** Zero Tier D estimates remain in the corpus.

---

## Phase 3 — Build-out (after verification is clean)

### WI-10: Visualization layer (Plan 007)

The data is now rich enough: 271+ facts, multiple complete cross-decade arcs
(poverty, food prices, heating fuel, AC, cable TV, CPI, home-production, life
expectancy, infant mortality endpoints). Plan 007 has the design; this WI is
the trigger to start implementation once Phase 1-2 are verified.

### WI-11: 1890s room or v2 world rooms

The 1890s room has its source already registered
(`commissioner-labor-6th-1890`). v2 world rooms (UK, PL, RU, CN, IN, JP) are a
much larger scope expansion. Owner decides priority.

---

## Verification log format

Each WI produces entries in `docs/verification-log.md`:

```
## WI-N: Title

**Date:** YYYY-MM-DD
**Verifier:** agent/session identifier
**Source checked:** file path or URL
**Method:** API call / PDF read / OCR / web fetch

### Results

| Fact ID | Field | Fact value | Source value | Result |
|---------|-------|-------------|--------------|--------|
| us-XXXX-YYYY | value | "$X" | "$X" | verified |
| us-XXXX-ZZZZ | value | "$Y" | "$Z" | mismatch — corrected |
```

The log is the evidence. An entry that says "verified" without the source value
beside it is not evidence — it is a claim.
