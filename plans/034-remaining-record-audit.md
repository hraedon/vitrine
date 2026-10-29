# Plan 034 — Audit the remaining records

**Status:** complete — source review, corrections and integration validation,
2026-10-28. Four specific evidence needs remain disclosed as gaps.
Starts at `f58b808`; no deployment or publication change.

## Request and scope

The owner requested an audit of the records without a current field binding,
using Luna and Terra agents as appropriate, plus continued implementation and
specific requests for sources that require the owner's help to acquire.

The initial queue has 561 records: 92 early US, 190 mid-century US, 193 recent
US and 86 UK/Japan. It includes 69 documented gaps. The existing 221 bindings
remain a baseline, not proof that all companions or notes were verified.

## Method

- Read actual publisher files first, preserving source vintage, population,
  units and observation dates. Existing curator qualifiers can be replayed;
  locating a file or matching a headline alone is not verification.
- Record a disposition for every queue item and exact evidence paths,
  SHA-256 pins, table/cell/page locators, inspected fields and unresolved claims.
- Distinguish verified records, partially checked records, reviewed gaps,
  demonstrated corrections and exact acquisition needs. An uninspected file
  remains pending; it is not a request for a missing source.
- Add numeric field bindings where the model permits them and reproducible
  compound qualifiers where one binding cannot cover the record. Review prose
  independently and remove unsupported causal or comparative claims.
- Preserve the fact methodology, source licensing and composite disclaimer.
  No raw third-party data, credentials or bulk datasets enter Git.

## Integration

Agents own distinct source-review scripts/tests and assessment artifacts.
The integrating agent owns shared data, source and assumption registries and
the combined audit ledger. Re-read proposed corrections before applying them;
refresh changed bindings honestly and preserve unchanged dates.

Run original-file replay, relevant tests, strict lint/types, the full corpus
gate and rendered-row/mark coverage after integration. Document unresolved
records and precise source acquisition requests without overstating coverage.

## Outcome

All 561 baseline IDs have a disposition. Re-reading the initially partial
records resolved their remaining field-level findings; four specific evidence
needs remain as disclosed gaps. The original IPUMS extract metadata was found
on the owner's research host, but the original analysis and aggregate output
were not recovered. No raw microdata was opened or copied.

The ledger now has 390 current bindings. The source review also reconciles
54 existing annual availability series, preserves their curated year windows,
and documents the source-precision effect on one derived threshold count.
An independent core review checked the new monetary-visibility rule against
unrelated numeric tokens and an incorrectly displayed rounded source operand.

Details and evidence boundaries are in
[the audit report](../docs/remaining-record-audit-20261028.md) and
[the committed inventory](../docs/audits/20261028-remaining-records.json).
