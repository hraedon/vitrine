# Plan 027 — The past was a different country

**Status:** WI-1 through WI-6 delivered; WI-7 through WI-12 remain research
and editorial work. Scope revised after the 2026-09-07 claims review.

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
  The existing SKU cards' Tier B classification needs a separate source/tier
  review; this editorial pass does not silently retier the facts.
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

The verification log records source extraction and cross-checks for these
deliveries. It is not blanket qualification of all their interpretive notes.
Plan 015's audit ledger separately records which numeric fields have a current
repeatable transcription check.

## Remaining work

### WI-7: Lead exposure

Research age-specific NHANES blood-lead checkpoints. Preserve the actual
statistic (median or geometric mean), ages, sampling years, and measurement
limits. A contemporary intervention or reference threshold is a different
kind of fact and must have its own dated primary source. Do not infer a causal
contribution from a regulation's timing alone.

**Acceptance:** source-verified checkpoint facts and explicit population and
statistic labels. Add a corridor only if comparable observations justify it.

### WI-8: Children and work

Research the historical census definitions behind any proposed child-work
series: ages, employment/gainful-occupation concept, reference period, and
agricultural coverage. Historical definitions cannot be assumed equivalent to
modern labour-force measures. Research the FLSA separately as a legal event.

The [Department of Labor's agricultural employment guidance](https://www.dol.gov/general/topic/youthlabor/agriculturalemployment)
documents age-dependent rules and statutory exemptions. It rules out the
original plan's blanket assertion of abolition, but is not a source for
historical prevalence.

**Acceptance:** documented comparability boundaries and no post-series zeros.
The source must establish why each series ends. No claim that the FLSA ended
all child employment or that observed work was universally accepted.

### WI-9: Smoking restrictions

Choose a small number of primary legal records. Each fact should describe one
restriction, its effective date, scope, jurisdiction, and exceptions. Re-read
the original flight-ban and hospital leads before entering them; the draft's
broad chronology is not evidence.

**Acceptance:** statute or rule verifies each claim. A permission or
restriction does not establish how many people smoked in that location.
Hospital policy, federal law, and state law must not be collapsed into one
national event.

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
