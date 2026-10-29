# Reconstruction of the remaining source gaps

Follow-up to the [remaining-record audit](remaining-record-audit-20261028.md),
2026-10-29. The earlier unsupported figures remain withdrawn. The four source
gaps now have independently checked replacements with explicit populations and
methods; their dependent income difference is calculated by the core.

## Recovery search

The owner identified four relevant machines and authorized reconstruction if
the original analysis could not be recovered. Searches covered:

| Machine | Searched locations and evidence |
|---|---|
| Current Windows workspace | Project files, relevant local research copies, candidate download names, filtered shell history and relevant Git history. No original aggregation program or output found. |
| mvmcc02 | Project/review copies, shared worktrees, relevant Git stores and unreachable commits, and filtered histories. Extract metadata and client copies found; no original aggregation program/output found. |
| mvmcc03 | `/home/itadmin/projects/personal/vitrine`, relevant project/home paths, Git refs/objects and history. An original commit documents the old household-sum/household-weight method; no saved program/output found. |
| mvmhermes01 | `/home/itadmin/vitrine`, `/home/itadmin/vitrine-research`, relevant histories and candidate filenames, Git refs and unreachable commits. Original extracts and codebooks recovered; no original aggregation program/output found. |

These were bounded searches of relevant accessible locations, not a claim that
no copy can exist anywhere. Ignored search reports remain with the research
archive. The original 1950 extract, `usa_00001`, selected the 1% sample and
included INCTOT, but lacked FTOTINC and SLWT. The recovered Git description
summed available personal income by household and used HHWT. That does not
establish 1950 total family income: personal income questions were restricted
to sample-line persons. Its METRO selection also omitted the central-city
category. Matching those old numbers would not validate them.

## New primary-family income estimates

An authorized new IPUMS request produced extract `usa_00003`, using `us1950a`
(1950 1% sample). The matching DDI identifies SAMPLE=195001 and all required
variables. The provider's byte counts and SHA-256 values were checked on all
four downloaded files. Raw files remain in ignored `samples/` on the research
hosts and workspace; no person records or identifiers are published.

| Geography | Valid sampled heads | Weighted median of coded 1949 income |
|---|---:|---:|
| Metropolitan, METRO=3/4/5 | 13,734 | $3,650 |
| Nonmetropolitan, METRO=1 | 9,062 | $2,650 |
| Identifiable outside central city, METRO=3 | 11,788 | $3,750 |

The last row is a subset of the first. It excludes metropolitan cases whose
central-city status is undetermined and must not be labelled all suburbs.
The core computes the difference between the first two medians as $1,000.
This difference describes two populations; it is not a causal estimate.

The calculation selects a unique household head (RELATE=1), FAMUNIT=1,
head FAMSIZE=4 and exactly four FAMUNIT=1 person records, in period-defined
GQ=1 households. Ambiguous heads and mismatched family-unit counts are
excluded. GQ=2 is excluded: its harmonized modern label must not be read as
ordinary households under the period definition. Use SLWT>0 and valid FTOTINC.
This is a primary-family-unit population, not every household or every CPS
family. No equivalence adjustment or calibration to the room's CPS median is
performed. Census observation year is 1950; income refers to 1949.

The new CSV supplies SLWT as decimal weights of 330.0 for sample-line
observations. DDI/setup metadata's two implied decimal places describe the
fixed-width representation; the CSV is not divided again. The median is the
smallest ordered coded income whose cumulative SLWT reaches half the total,
without interpolation. None of the three medians reaches a top/bottom code or
lands on an exact half-weight boundary. FTOTINC uses income-category midpoints;
these are medians of coded values, not exact-dollar income measurements or
confidence intervals. Income of children below age fourteen is outside this
income definition. No valid selected head has missing income or unknown metro
status in this extract. Small ancillary diagnostics receive complementary
suppression; thirty records per released median is the project's conservative
choice, not a claimed IPUMS legal threshold.

Primary definitions: [FTOTINC](https://usa.ipums.org/usa-action/variables/FTOTINC),
[SLWT](https://usa.ipums.org/usa-action/variables/SLWT),
[FAMUNIT](https://usa.ipums.org/usa-action/variables/FAMUNIT),
[FAMSIZE](https://usa.ipums.org/usa-action/variables/FAMSIZE),
[GQ](https://usa.ipums.org/usa-action/variables/GQ), and
[METRO](https://usa.ipums.org/usa-action/variables/METRO).
The [published aggregate artifact](audits/20261029-family-income.json) records
the file/document hashes, selection, median rule and weighted rank endpoints.
The public calculation is `scripts/ipums_family_income_1950.py`; independent
implementation and original-file replays are part of qualification.
The [acquisition integrity record](audits/20261029-acquisition-integrity.json)
retains only safe file metadata and the provider-hash comparisons.

Data citation: Steven Ruggles, Sarah Flood, Matthew Sobek, Daniel Backman,
Grace Cooper, Julia A. Rivera Drew, Stephanie Richards, Renae Rodgers,
Jonathan Schroeder, and Kari C.W. Williams. *IPUMS USA: Version 16.0 [dataset].*
Minneapolis, MN: IPUMS, 2025. [DOI](https://doi.org/10.18128/D010.V16.0).
The new Source carries the full citation on pages rendering these observations.

## Recovered housing observation

BLS, [*How American Buying Habits Change* (1959), Table 6](https://fraser.stlouisfed.org/docs/publications/dol/dol_americanBuyingHabits_1959.pdf),
printed pp. 46–47 (PDF pp. 60–61), reports an all-income-classes housing
share of **10.6%** for urban wage-earner and clerical-worker families of two or
more, including owners and renters. The survey covers cities of at least
2,500 people. The table reports 7,007 sampled families, mean current consumption
of $3,925 and mean housing spending of $415.

Use the publisher-printed percentage; do not recalculate it from rounded
dollar means. Fuel/light/refrigeration, household operation and furnishings
are separately reported categories. This is not modern total housing,
a percentage of income, an all-household estimate, or a four-person family's
budget. The original Bulletin 1097 has city-specific tables but did not
establish the former national claim.

The table image was independently inspected. Its unreliable numeric text
layer makes this an explicit visual transcription, recorded in the
[housing artifact](audits/20261029-housing-transcription.json).
`scripts/bls_1950_housing_review.py` checks the original PDF hash and page-text
sentinels before returning that reviewed transcription. It does not claim
to extract numeric cells automatically.

## Verification boundary

The dated 561-record review retains the earlier findings and adds a later
review for these four replacements. Numeric bindings check artifact bytes and
fields; original-file replay and independent source/method review supply
separate evidence for interpretation. Unchanged audit dates remain unchanged.
Other rendered gaps remain curation boundaries, not proof of historical absence.
The existing census-income anchor, source populations, composite disclaimer and
raw-data publication restrictions remain in force. No deployment is included.

The [qualification record](reconstruction-qualification-20261029.md) gives
the completed checks. Five newly cited evidence files also passed the
[byte-identity check](audits/20261029-reconstruction-byte-checks.json);
the preceding dated archive check remains historical.
