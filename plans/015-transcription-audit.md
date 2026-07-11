# Plan 015 — Mechanical transcription audit: the archive becomes an instrument

**Status:** draft
**Triggered by:** 2026-07-11 deep-dive over the evidence base. Every defect
this project has ever found lived in the transcription layer, never in the
sources: the 2026-07-07 external review (food-share column misread, ACS data
filed under AHS, plumbing percentages off), the BLS food-price label
mismatches (six series labeled with the wrong item), and the famous-figures
incident (1980/1990 manufacturing earnings "corrected" to the well-known
SIC-era published values instead of the cited CES series). Meanwhile
`samples/` holds ~400 fetched source files (2.3 GB, 27 directories,
manifest cross-referenced against the source registry) that **no fact
references machine-readably**. The archive is a filing cabinet; it should
be an instrument.

## The problem

Verification today is manual and non-repeatable. A session fetches the
source, compares by eye, and appends prose to `docs/verification-log.md`.
That log is honest evidence of past checks — but it protects nothing going
forward:

1. **Verified facts can drift after verification.** An edit, a merge
   resolution, or a well-meaning "correction" to a famous figure silently
   invalidates a logged check. The hermes earnings incident is exactly this
   mode, and nothing structural prevents its recurrence.
2. **Verification doesn't scale with the corpus.** 446 facts and growing;
   each manual pass covers a slice, and coverage is invisible — nobody can
   ask "which Tier A facts have never been checked against their pulled
   source?"
3. **The archive is unpinned.** `samples/` is gitignored (2.3 GB) and lives
   on one box. If it rots, the museum's ability to re-verify rots with it,
   and nothing would notice.

## Design

Three pieces: a locator on the fact, an extractor that re-reads the sample,
and a committed ledger that makes past audits CI-checkable without shipping
2.3 GB.

### The locator

A fact may carry an optional inline `audit` table:

```toml
[[fact]]
id = "us-1950s-median-income-four-person"
# ...existing fields...
audit = { file = "06-acs-csv/f08ar.xlsx", extractor = "xlsx-cell", locator = "All Races!B335", scale = 1.0 }
```

| Field | Type | Meaning |
|---|---|---|
| `file` | str | Path relative to the samples root |
| `extractor` | Extractor | Closed set, below |
| `locator` | str | Extractor-specific address of the datum |
| `scale` | float | Source-units → fact-units multiplier (default 1.0; e.g. 1000 when the source publishes thousands). A declared transform, never a hidden one. |

The audited value is the fact's `quantity` (required on any audit-bearing
fact — it is already gate-enforced to appear verbatim in `value`, so
auditing the quantity audits the placard). Comparison is exact after
canonicalization (strip `$ , %` and whitespace from the extracted cell,
parse as float, multiply by `scale`, compare to `quantity`). No tolerance:
transcription means exact.

### Extractors (closed set, `assert_never`-dispatched)

| Extractor | Locator syntax | Dependency |
|---|---|---|
| `csv-cell` | `R<row>:C<col>` (1-indexed, post-parse) | stdlib `csv` |
| `xlsx-cell` | `<Sheet>!<Cell>` | `openpyxl` under a new `[audit]` extra |
| `text-regex` | A regex with exactly one capture group, applied to the file as UTF-8 text | stdlib `re` |

The `[audit]` extra mirrors the `[site]` pattern: stdlib-only core stays
stdlib-only, and an import-boundary test asserts `vitrine.audit` is the only
module that imports `openpyxl`. Zip members, PDFs, and API replay are out
of scope for v1 (see below).

### `vitrine audit` and the committed ledger

`vitrine audit` runs on the operator box (where `samples/` lives):

- For each audit-bearing fact: extract, compare, report
  `ok / MISMATCH / missing-file / parse-error`. Any mismatch is a nonzero
  exit — a mismatch means either the fact or the locator is wrong, and
  both are red-build defects.
- On success it rewrites `data/audit-ledger.toml`: one entry per audited
  fact — `fact_id`, `fingerprint` (sha256 over the fact's
  `value|quantity|scale|file|locator`), `sample_sha256`, `audited` date.
  Deterministic ordering; the ledger is generated, never hand-edited
  (the gap-log lesson applied to verification).

CI cannot see `samples/`, but it can see the ledger. `vitrine check` gains
one invariant: **for every ledger entry, the referenced fact exists and its
current fingerprint matches the ledger.** Editing an audited fact's value
without re-running the audit locally is now a red build — this is the
structural fix for the famous-figures failure mode. (A fact with no ledger
entry is merely unaudited, reported as coverage, not an error.)

### Coverage as a first-class report

`vitrine audit --coverage` (and a line in `vitrine gaps`) reports, per room:
facts with locators / audited-and-current / unaudited, split by tier. The
retro-fit priority is the empirically bitten families first: earnings-type
facts, CEX shares, food prices — then remaining Tier A, then B. 100%
coverage is not the goal; coverage *visibility* is. Some sources are
verified via API (BLS/FRED) rather than a file — those keep manual
verification-log entries, and the coverage report says so
(`audit = "api"` marker considered, deferred).

### Pinning the archive

`samples/SHA256SUMS` — committed, regenerated by `vitrine audit --pin` —
records the digest of every file the ledger references (not all 2.3 GB of
the archive, just the evidence actually load-bearing for audits). Ledger
`sample_sha256` entries must match SHA256SUMS (CI-checkable), and the
operator box can detect archive rot with `sha256sum -c`. MANIFEST.md
remains prose; the checksums are the mechanical layer under it.

## Work items

### WI-1: Model + gate

`AuditRef` on `Fact` (optional), `Extractor` enum, loader parsing, and the
check invariants: audit-bearing fact must have `quantity`; extractor/locator
syntax validated at parse; ledger↔corpus fingerprint consistency; ledger
entries must reference existing facts; ledger sample hashes must appear in
`SHA256SUMS`.

**Acceptance:** `vitrine check` green on current corpus (no locators yet =
no ledger = vacuously consistent). Malformed locator, missing `quantity`,
and stale fingerprint each produce a named red-build error in tests.

### WI-2: Extractors + `vitrine audit`

The three extractors, canonicalization, `scale`, the CLI subcommand, ledger
generation, `--coverage`, `--pin`. `[audit]` extra + import-boundary test.

**Acceptance:** unit tests per extractor against fixture files (a tiny csv,
xlsx, and text file under `tests/fixtures/` — fixtures are test data, not
samples). A deliberate fixture mismatch exits nonzero naming the fact id.
Ledger output is byte-deterministic across runs.

### WI-3: Retro-fit locators — the bitten families

Locators for: manufacturing hourly/weekly earnings facts (all decades with
an xlsx/csv sample), CEX expenditure-share facts, food-price facts. Run the
audit; every mismatch found is fixed fact-side or locator-side with a
verification-log entry explaining which.

**Acceptance:** `vitrine audit` exits 0 on the operator box; ledger + 
SHA256SUMS committed; coverage report shows the three families at 100% of
sample-backed facts.

### WI-4: Retro-fit locators — remaining Tier A sweep

Best-effort pass over remaining Tier A facts whose sample file exists and
whose format an extractor can address. Facts whose evidence is API-only or
PDF-only are enumerated in the coverage report, not forced.

**Acceptance:** coverage report committed to the plan's closing note with
the honest number, whatever it is.

## Phasing

| Phase | WIs | Effort |
|---|---|---|
| 1 | WI-1, WI-2 | Medium — model, gate, extractors, CLI |
| 2 | WI-3 | Medium — curation, operator box required |
| 3 | WI-4 | Low intensity, incremental — can trail indefinitely |

## Out of scope

- PDF extraction (page-image sources go through /ocr + manual log, as today).
- Zip-member locators (Statistical Abstract zips) — v1 requires the table
  extracted to a flat file first; the extraction step is recorded in
  MANIFEST.md as today.
- API replay audits (BLS/FRED live re-fetch) — deliberate: audits must be
  reproducible offline against pinned evidence, not dependent on a remote
  serving the same vintage.
- Backfilling `samples/` into git/LFS. The archive stays local; the ledger
  and checksums are the committed truth.
