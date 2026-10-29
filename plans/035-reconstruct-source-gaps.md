# Plan 035 — Recover or reconstruct the remaining evidence

**Status:** complete, 2026-10-29. Four-host recovery search, source acquisition,
independent reconstruction and integration qualification passed. See
`docs/reconstruction-20261029.md` and
`docs/reconstruction-qualification-20261029.md`.

## Authorization and boundaries

The owner requested a search on the current Windows machine, mvmcc02,
mvmcc03 and mvmhermes01, followed by the best supported reconstruction when
original material cannot be recovered. This authorizes a new research extract
using the existing IPUMS account and a documented aggregate calculation.
It does not turn the former unsupported estimates into evidence.

Preserve the data methodology, the measured population, source licensing,
and the composite-family disclaimer. Raw microdata stays in ignored samples;
only aggregate results may enter the museum. Do not print keys, download
tokens, account responses or individual records.

## Recovery findings

Search project/research folders, relevant histories and Git objects on all
four hosts. Record actual search boundaries, inaccessible paths and evidence
found; a bounded search is not proof of universal absence. The original
1950 extract and its metadata are on mvmhermes01. Available extract definitions
have INCTOT but lack FTOTINC and SLWT. Git records the former household-income
summation and HHWT method; no recoverable aggregation program/output has been
located in the searched locations. That method is not a valid demonstrated
1950 family-income calculation.

The 1950 urban expenditure survey is available. A primary BLS publication,
*How American Buying Habits Change* (1959), prints a suitably scoped housing
share in Table 6. It supplies a replacement, not retroactive proof of the
former curator's citation.

## New family-income reconstruction

- Use the 1950 1% sample (`us1950a`) and its FTOTINC family-income variable,
  not a sum of available personal incomes. The income reference year is 1949.
- Obtain and pin the matching DDI and data, sample identity and source
  documentation. Apply the actual CSV weight representation, verified against
  DDI/setup metadata; do not apply implied decimals twice.
- Select one household head (`RELATE=1`), primary family (`FAMUNIT=1`), with
  four own-family members (`FAMSIZE=4`) and four primary-unit person records.
  Restrict to `GQ=1` under the period household definition. Quasi/group quarters
  and incompatible family-unit cases are outside this estimand.
- Use positive sample-line weights (`SLWT`). Retain valid zero income;
  distinguish the net-loss category from a literal negative-dollar observation;
  exclude documented missing codes. Report eligibility, missingness, geography
  coverage and top-code limitations as aggregate diagnostics.
- Define metro by the actual DDI codes for metropolitan residence, including
  central-city status unknown; nonmetro uses its explicit code. The identifiable
  outside-central-city subset must not be labelled all suburban families.
  Unknown metropolitan status is excluded and its extent disclosed.
- Compute the inverse weighted empirical CDF median without interpolation.
  Document half-rank ties and income-category midpoint coding. Do not force
  agreement with the withdrawn medians or the separate CPS family-income anchor.
- Use conservative minimum group sizes for released medians. Small ancillary
  diagnostic counts must not invalidate a well-supported median; suppress them
  explicitly where appropriate. No new legal threshold is inferred.

Primary definitions: [FTOTINC](https://usa.ipums.org/usa-action/variables/FTOTINC),
[SLWT](https://usa.ipums.org/usa-action/variables/SLWT),
[FAMUNIT](https://usa.ipums.org/usa-action/variables/FAMUNIT),
[FAMSIZE](https://usa.ipums.org/usa-action/variables/FAMSIZE),
[GQ](https://usa.ipums.org/usa-action/variables/GQ), and
[METRO](https://usa.ipums.org/usa-action/variables/METRO).

## Housing reconstruction

Read Table 6's original image and population/definition notes independently.
Use the publisher-printed all-income housing percentage, current-consumption
denominator and worker-family population. Fuel, household operations and
furnishings are separate categories. Do not relabel this as modern total housing
or a four-person median family's budget. Expose visual transcription honestly
where the source text layer is unreliable.

## Acceptance

Independent source/method review; synthetic selection, weighting, missingness,
duplicate and median tests; deterministic original-file aggregate replay;
source-bound published fields; updated audit history with changes distinguished
from the prior review; corpus/build/render coverage, lint and strict types.
Complete the appropriate supported-Python and Windows checks. Preserve original
main checkouts and the owner's pending note files. No deployment is included.
