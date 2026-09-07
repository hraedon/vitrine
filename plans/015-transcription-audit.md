# Plan 015 — Repeatable transcription audits

**Status:** WI-1 and WI-2 implemented; WI-3 partially implemented; initial WI-4
sweep delivered, with 57 audited records. Reconciled 2026-09-07.

## Outcome

`vitrine audit` re-reads pinned files from the operator's `samples/` archive,
checks a declared numeric field and source-context guards, and atomically
writes `data/audit-ledger.toml`. `vitrine check` checks those bindings without
needing the archive or openpyxl. An audited fact, source, population, unit,
label, assumption, or locator changing makes the gate fail until re-audited.

The previous draft remains in Git history. The implementation revises it:

- The target can be `quantity` or `amount_minor`. Earnings and home values
  frequently have only a structured monetary amount; adding a redundant
  quantity would create a second number to maintain.
- Scaling uses decimal arithmetic. There is no approximate comparison or
  guessed rounding rule. An average or ratio is not a cell transcription.
- The fingerprint covers the entire authored fact, its source registration,
  referenced assumptions, and every extraction option, using versioned,
  canonical JSON. The draft omitted the extractor, unit, and source meaning.
- Optional guards pin column headings, year labels and population selectors.
  A number in the wrong column is not sufficient evidence.
- `csv-cell`, `xlsx-cell`, and `text-regex` are the closed extractor set.
  CSV/text default to UTF-8; an explicit CP932 setting reads Japan's original
  CSV bytes. Text regexes see normalized line endings, require one capture
  group and exactly one match. Spreadsheet formulas are rejected.
- The ledger contains file hashes directly. There is no second checksum file
  under gitignored `samples/` that could drift or publish independently.
  One atomic replacement publishes all successful checks or none.
- An audit-bearing fact without its ledger entry fails the gate. Removing
  a locator or fact cannot silently delete its old audit through the command.
- A changed sample hash fails the audit even if the target cell is unchanged.
  After inspecting the replacement evidence, `--pin` allows a new hash, but
  all values and guards still have to pass.

## Use

```sh
uv sync --extra dev                 # includes the optional audit dependency
vitrine audit --samples samples     # extract, compare and update the ledger
vitrine audit --coverage            # read-only; does not need the archive
vitrine gaps                        # gap inventory followed by audit coverage
vitrine check                       # checks ledger bindings in CI
```

Example (the actual four-person income cell, not the draft's incorrect B column):

```toml
audit = { file = "06-acs-csv/f08ar.xlsx", extractor = "xlsx-cell", locator = "f08ar!C335", guards = [{ locator = "f08ar!A335", value = "1950" }, { locator = "f08ar!A256", value = "Families with Four People" }] }
```

A ledger record contains the fact ID, fingerprint, sample path and SHA-256,
extracted numeral, and audit date. Unchanged input on the same audit date
produces identical bytes. Raw source material stays uncommitted.

## Work items and evidence

| Item | Result |
|---|---|
| WI-1 model and gate | Implemented: typed references, loader validation, target requirements, fingerprints, deletion and missing-ledger checks |
| WI-2 extractors and command | Implemented: CSV, XLSX, text, decimal scaling, context guards, atomic output, pin refresh, per-room/tier coverage |
| WI-3 historically troublesome families | Partial: four CEX expenditure totals. Manufacturing annual means, expenditure-share calculations, and food-price evidence are not declared audited |
| WI-4 additional Tier A sweep | 36 Census F-8 records, seven historical home values, ten Japan MLS wage/hour records |

All 57 checks passed against the archive on the operator host. No numeric
corrections were needed in this selected set. This is **57 of 725 authored
records**, including gaps in the denominator; it is not whole-corpus verification.

### Why WI-3 remains open

The CES extraction script calculates annual means from monthly API results;
those facts need a replayable aggregation audit and the saved input vintage,
not a locator pointing back into the museum's generated series. CEX percentage
shares are often rounded ratios of expenditure cells. The archived 1985,
1996 and 2005 tables also change their household-size column layout. The new
context guards help prevent column swaps, but do not make the ratios literal
source cells. Food-price locators still need source-by-source qualification.

Do not manufacture a CSV from the curated facts to increase coverage. The
next extension should audit source operands and declared transformations,
or move authored arithmetic into the existing derived-fact model.

## Limits and next work

The audit checks a **declared numeric field**, not every numeral in a compound
placard or the source's authority, statistical validity, completeness, or
fitness for comparison. A source guard is curator-authored and still needs
review. Hashes bind reviewed bytes; they do not prove publisher authenticity.

The coverage report does not guess that a record without a locator has no
sample, is API-only, or is PDF-only. Those remain unclassified until inspected.
The operator archive is still required for re-extraction. CI detects binding
drift; it does not re-download sources or attest that the archive remains online.

Source collection pages (Plan 017) make the audit date and these limits visible.
See `docs/transcription-audit-coverage.md` for the generated closing snapshot
and Plan 028 for the next priorities.
