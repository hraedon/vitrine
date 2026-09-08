# Plan 028 — Let the evidence determine the presentation

**Status:** first implementation delivered 2026-09-07; next priorities below.

## Decisions implemented

1. Sparse rooms become research collections. Fewer than eight non-gap records
   or observations spanning fewer than three panels triggers compact treatment.
   This is an editorial layout rule, not a confidence score. It applies equally
   to every country. Observed panels lead; gap-only panels follow. All existing
   record IDs, source cards and panel links remain available.
2. The 1950s Japan collection explicitly distinguishes its two observations
   from five gaps. Its household-income and workplace-wage series describe
   different populations; neither establishes a four-person median family.
   The empty illustrated house is removed. Later Japan collections retain
   their own sourced objects, with actual observation years in every label.
3. Labelled object cards replace the tiny cutaway as the primary room view.
   Larger SVG drawings use silhouettes, inset details and restrained shading.
   General telephone data does not become smartphone data because of the decade;
   an internet symbol does not assert Wi-Fi, and complete plumbing is not a
   hand-pump statistic. Illustrations identify subjects, not exact appliance
   models or a culturally universal house. The US schematic remains optional.
4. Counts distinguish observations from documented gaps. “The complete room”
   and claims that missing icons prove historical absence are retired.
5. Sources become navigable collections, completing Plan 017's remaining
   substantial surface. Current audit bindings and their limits appear there.

## Next priorities, in order

- **Audit calculations before adding more decorative data.** Extend Plan 015
  with explicit source operands, annual aggregation, population/year guards,
  and a documented rounding rule. Start with CES earnings and CEX shares.
  Do not validate generated series against themselves.
- **Review compound records.** A single `quantity` cannot qualify all claims
  in a multi-number food basket or telephone/automobile paragraph. Separate
  atomic observations before giving them independent visual emphasis.
- **Write a Japan route only when the comparison is earned.** Earlier decades
  need source retrieval, not a US-shaped household set. Later decades can
  support a tightly scoped tour, provided the household/workplace distinction,
  2009 observations filed in the 2010s room, and the pre/post-1963 FIES coverage
  change remain explicit. Do not imply a continuous national median series.
- **Plan 016 WI-5 remains editorial work.** The mortality-tour dependencies
  exist, but source populations and time-series breaks need a fresh reading
  before connective prose is written. More prose is not the immediate priority.
- **Separate curation status from country.** Keep any future layout and route
  thresholds inspectable. A room earns visual treatment through its records;
  membership in a US or world wing is not a proxy for evidential quality.

## Validation

Regression coverage checks sample drift, semantic drift, missing ledgers,
context mismatches, formula cells, decimal scaling, encodings and preservation
of the last ledger on failure. Presentation checks preserve every record and
link, enumerate every source's records, and exercise sparse/dense collections
at phone and desktop widths, including source-card access without JavaScript.

Qualification: 557 tests passed on the operator host with Python 3.14 and the
source archive present. Lint and strict typing passed; all 740 rendered
exhibits passed coverage gates, and 57 audit extractions matched. The standalone
export passed. Browser checks include phone/desktop layouts and no-JavaScript
record-card access. Source-topic cross-checks reported zero hard errors; their
existing advisory findings remain a separate research backlog.

## Superseded by Plan 029

The first implementation's automatic record/panel-density rule has been
replaced by explicit editorial status and rationale. Japan now has a thematic
entrance that does not require each decade to sustain an identical household
portrait. Plan 029 also implements calculation replay, selected atomic-record
corrections and a review of the strongest interpretive claims. The mortality
essay and further countries remain deferred.
