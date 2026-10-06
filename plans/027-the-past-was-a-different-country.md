# Plan 027 — The past was a different country

**Status:** WI-1 through WI-9 implemented; WI-10 through WI-12 remain
research and editorial work. WI-7 added 2026-09-12; WI-8 and WI-9 added
2026-10-05. Scope revised after the 2026-09-07 claims review.

## Purpose and editorial correction

This US corridor brings together consumption, exposure, and food-supply
records. It should let a visitor investigate changes in specific measures.
It cannot reconstruct the behaviour of a median-income family from unrelated
population averages.

The original selection rule required every practice to have been "normal,
legal, and ubiquitous" and now virtually gone. That rule preselected a story
the evidence did not establish. Legal permission is not prevalence; a lower
rate is not disappearance; a statistical series ending is not a practice
ending. The wing now states those distinctions in its introduction, and its
food group is titled **Four foods in the national supply**. Existing URLs and
registry slugs remain stable.

The older plan is retained in Git history, not as an executable specification.
In particular, do not revive its unsupported claims that child labour ended
with the FLSA, that reference services or repair culture died, or that a CPI
index supplies a refrigerator price. See `docs/editorial-review.md` for the
source checks and the limits of this review.

## Evidence rules

- Admit a measure because its population, unit, source, and relevant change
  can be explained. Do not require a monotonic or emotionally striking trend.
- Transcribe from primary tables into the corpus. Illustrations and prose
  cannot introduce measurements absent from the facts.
- Treat legal events separately from behavioural frequency. Each legal claim
  needs a dated jurisdiction, coverage, exceptions, and primary citation.
- Explain every series start, end, and break from source documentation.
  Missing observations are neither zero nor evidence of no historical record.
- A national supply average is neither household ownership nor intake. A
  worker rate is not the risk experienced by a particular family breadwinner.
- Tier by the fact-model definitions. A federal publisher does not turn a
  republished trade survey into official microdata computed by this project.
  The produce-SKU cards are Tier C commercial period-survey proxies after
  their source/tier review; a federal host does not make them Tier B.
- Keep comparative curation US-only until another country's compatible
  curation is authored and the comparative registry gate is satisfied. A
  nation-prefixed identifier alone does not provide comparability.

## Delivered work, with actual boundaries

| Work item | Delivered record | Boundary to preserve |
|---|---|---|
| WI-1: wing | Fifth corridor wing, registry placement and source cards | No universal family or vanished-practice claim |
| WI-2: smoking | Cigarette-consumption and smoking-prevalence records | Consumption and prevalence differ; the archived consumption table ends in 1994, and later TTB records use another basis |
| WI-3: alcohol | NIAAA apparent-consumption record | Published Prohibition gap; age denominator changes at 1970; pre-1934 observations are ranges |
| WI-4: injury deaths | FHWA road rate and BLS CFOI hours-based work-injury rate | FHWA fatality window changes in 1976; CFOI starts in 1992, hours-based rates in 2006; earlier records are not claimed nonexistent |
| WI-5: teenage births | NCHS selected-year age-specific rates | Highest selected point is not the annual historical peak; rate does not establish marital status or sexual behaviour |
| WI-6: food supply | Four FADS arcs, commodity-count derivations, supermarket SKU cards, 1955 broccoli-use checkpoint | Availability, assortment, and household use are three different measures; a series start does not date an item's arrival |
| WI-7: lead exposure | Seven Childstats/NHANES median checkpoints for children ages 1–5, repeatable source audits and a discrete-period corridor | Separate national survey samples; full sampling windows, changing laboratory sensitivity and final pre-pandemic weighting remain explicit; no annual interpolation or causal claim |
| WI-8: children and work | The census's comparability-adjusted gainful-occupation share for children 10-15, 1870-1930, from Table XVIII of the 1943 Comparative Occupation Statistics monograph; day cards in the 1900s-1930s rooms and a 1940s gap card | The decennial gainful-worker concept is stated on the cards, not modernised; the series ends at 1930 by the source's own account of the 1940 labor-force break; the 1930s job collapse is recorded as the Bureau records it, with no statute's effect inferred from timing; no post-series zeros |
| WI-9: smoking restrictions | Five legal-record day cards — the 1973 CAB separation rule, the temporary 1987 two-hour flight ban, the permanent 1989 all-domestic ban, the 2000 statute covering foreign transportation, and California's 1994 workplace statute | Each card is one restriction with its scope, jurisdiction, effective date, and exceptions, verified against a fetched primary record; a permission or restriction does not measure how many people smoked; hospital policy is not represented — the accreditation standard is a private rule with no retrievable primary text and does not meet the statute-or-rule bar |

The verification log records source extraction and cross-checks for these
deliveries. It is not blanket qualification of all their interpretive notes.
Plan 015's audit ledger separately records which numeric fields have a current
repeatable transcription check.

WI-7's source choice, comparability boundaries, archived-file fingerprint and
qualification record are in [the evidence dossier](../docs/lead-exposure-evidence.md).
Contemporary interventions and reference thresholds remain separate facts
requiring their own dated primary sources; none are inferred from this chart.

WI-9's records were re-read from the Statutes at Large and the Federal
Register rather than from secondary summaries, which conflate the three
aviation laws of December 1987: the first ban was § 328 of the 1988 DOT
appropriations act (in Pub. L. 100-202) and was temporary by its own terms —
effective after four months, repealed after twenty-eight; the all-domestic
ban is § 335 of Pub. L. 101-164 with its own 96th-day effective date, and
over-six-hour segments to and from Alaska and Hawaii stayed outside it until
2000. The 1973 card is sourced to the 2000 rule's recitation because ER-800
itself was not separately retrieved. The archived records are pinned in the
samples archive (51-smoking-legal/); the verification log records the
corrections.

## Remaining work

### WI-10: Finding information and communicating

Investigate IMLS reference transactions, USPS First-Class Mail volume, and
newspaper circulation as separate, narrowly defined measures. Do not title
the result "the death of the reference desk" or "the death of the personal
letter" before assessing what the sources count.

[IMLS defines reference transactions](https://www.imls.gov/search-compare-definitions)
as information consultations, not exclusively physical visits. Its annual
documentation must determine which channels, estimates, and classification
changes apply in each year. A mail class is not automatically a measure of
personal correspondence. A publisher's print-edition cessation can be a
separate institutional event, with its own primary announcement.

**Acceptance:** record definitions and breaks before building arcs. Compare
with internet adoption only as juxtaposition, without claiming substitution
or causation. Preserve whichever direction the data actually show.

### WI-11: Appliances, prices, and repair

Assess whether available sources support an exhibit about acquisition and
repair. Candidate measures are appliance price indexes, repair-service price
indexes, and repair-establishment or employment counts. Verify coverage and
industry-classification boundaries before comparing them.

A CPI index measures price change, not the dollar cost of an appliance. It
cannot be divided by an hourly wage to obtain hours per refrigerator without
a separately sourced price level and defensible product definition. Repair
business counts do not directly measure household repair behaviour, product
durability, or a culture's disappearance. Relative price movements alone do
not identify why people repair or replace goods.

**Acceptance:** no promised collapse, crossover, or causal story. Present only
what the acquired evidence supports. Treat quality dispersion as an unanswered
research question, not as proven bimodality or a claim that no source exists.
Energy-use and regulatory material may be added with compatible product and
test-standard definitions; do not recall headline figures from familiar charts.

### WI-12: A source-led visitor route

Author a short route only after choosing mutually intelligible exhibits.
State the populations and meaning of each transition. A satisfying route need
not connect every topic or end with a progress/decline judgment.

**Acceptance:** existing provenance, registry, numeral, rendered-mark,
accessibility, and layout gates pass. Separately review the prose for causal
and typical-family claims; a green numeral gate cannot validate them.

## Scope limits

This plan authorizes no new mortality essay, currency conversion, live feed,
or cross-country comparative series. New facts require their own primary
source qualification. The 2026-09-07 review narrows current public framing and
future acceptance criteria; it does not claim to have audited every fact note,
every series value, or all of the remaining candidate sources.


Integration update: the two produce-SKU records are now Tier C commercial
period-survey proxies; their values and source links are unchanged.
