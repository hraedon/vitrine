# Source audit coverage — 2026-10-28

Generated from the current corpus and version-two ledger with
`vitrine audit --coverage`. Independent original-archive replay passed all
221 checks: 169 literal extractions and 52 documented calculations. The
previous September snapshot recorded 97 checks; the first review tranche
recorded 161. No raw third-party data are committed.

These counts describe declared field bindings, not the fraction of the museum
proven true. A compound record can contain additional unaudited numbers or
interpretive claims. Separate compound-food checks are documented in
`docs/provenance-review-20261028.md`; their fields are not added to the counts
below. Records without a locator remain unclassified, including documented
gaps. The offline report validates bindings and saved calculation operands;
it does not itself re-read source documents.

```text
Transcription audit coverage (current ledger bindings; archive not re-read)
room / tier: facts | locators | current | unaudited-or-stale
jp-1950s / A: 2 | 1 | 1 | 1
jp-1950s / D: 5 | 0 | 0 | 5
jp-1960s / A: 4 | 3 | 3 | 1
jp-1960s / D: 4 | 0 | 0 | 4
jp-1970s / A: 5 | 5 | 5 | 0
jp-1970s / D: 3 | 0 | 0 | 3
jp-1980s / A: 8 | 5 | 5 | 3
jp-1980s / D: 3 | 0 | 0 | 3
jp-1990s / A: 12 | 5 | 5 | 7
jp-1990s / D: 2 | 0 | 0 | 2
jp-2000s / A: 17 | 5 | 5 | 12
jp-2000s / D: 2 | 0 | 0 | 2
jp-2010s / A: 18 | 5 | 5 | 13
jp-2010s / D: 3 | 0 | 0 | 3
uk-1950s / A: 3 | 2 | 2 | 1
uk-1950s / D: 5 | 0 | 0 | 5
uk-1960s / A: 4 | 2 | 2 | 2
uk-1960s / D: 4 | 0 | 0 | 4
uk-1970s / A: 8 | 6 | 6 | 2
uk-1970s / D: 3 | 0 | 0 | 3
uk-1980s / A: 8 | 8 | 8 | 0
uk-1980s / D: 4 | 0 | 0 | 4
uk-1990s / A: 10 | 10 | 10 | 0
uk-1990s / D: 2 | 0 | 0 | 2
uk-2000s / A: 10 | 10 | 10 | 0
uk-2000s / D: 2 | 0 | 0 | 2
uk-2010s / A: 12 | 12 | 12 | 0
uk-2010s / D: 2 | 0 | 0 | 2
us-1900s / A: 26 | 2 | 2 | 24
us-1900s / C: 5 | 0 | 0 | 5
us-1900s / D: 2 | 0 | 0 | 2
us-1910s / A: 15 | 2 | 2 | 13
us-1910s / C: 3 | 0 | 0 | 3
us-1910s / D: 4 | 0 | 0 | 4
us-1920s / A: 15 | 2 | 2 | 13
us-1920s / C: 3 | 0 | 0 | 3
us-1920s / D: 5 | 0 | 0 | 5
us-1930s / A: 15 | 2 | 2 | 13
us-1930s / C: 2 | 0 | 0 | 2
us-1930s / D: 5 | 0 | 0 | 5
us-1940s / A: 28 | 8 | 8 | 20
us-1940s / C: 3 | 0 | 0 | 3
us-1940s / D: 3 | 0 | 0 | 3
us-1950s / A: 39 | 12 | 12 | 27
us-1950s / B: 3 | 0 | 0 | 3
us-1950s / C: 4 | 1 | 1 | 3
us-1960s / A: 44 | 6 | 6 | 38
us-1960s / C: 4 | 1 | 1 | 3
us-1960s / D: 1 | 0 | 0 | 1
us-1970s / A: 51 | 10 | 10 | 41
us-1970s / C: 4 | 1 | 1 | 3
us-1970s / D: 2 | 0 | 0 | 2
us-1980s / A: 57 | 19 | 19 | 38
us-1980s / C: 6 | 1 | 1 | 5
us-1990s / A: 66 | 20 | 20 | 46
us-1990s / C: 4 | 1 | 1 | 3
us-1990s / D: 2 | 0 | 0 | 2
us-2000s / A: 62 | 21 | 21 | 41
us-2000s / B: 1 | 0 | 0 | 1
us-2000s / C: 5 | 1 | 1 | 4
us-2010s / A: 62 | 21 | 21 | 41
us-2010s / B: 1 | 0 | 0 | 1
us-2010s / C: 2 | 0 | 0 | 2
us-2020s / A: 58 | 11 | 11 | 47
us-2020s / C: 1 | 0 | 0 | 1
us-2020s / D: 4 | 0 | 0 | 4
total: 782 facts | 221 locators | 221 current | 561 unaudited-or-stale
No locator means unclassified: it does not imply missing or PDF-only evidence.
```
