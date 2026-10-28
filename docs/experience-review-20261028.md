# Experience review — 2026-10-28

## Scope and evidence

Reviewed the lobby, US and UK rooms, Japan collection, trends, affordability,
record cards and progressive enhancement against the methodology charter.
The baseline was `f487ecf`. The source archive and qualified runtime were on
the Linux host; Windows could not import the CLI because `publish.py`
unconditionally imported `fcntl`. That platform limitation is separate from
the presentation findings.

Chromium screenshots and document geometry covered six representative page
types at 375px and 1440px. This is local rendering evidence, not verification
of a deployed release or a claim that every record was visually inspected.
Screenshots are operator evidence in gitignored
`samples/review-20261028/`: `index-375.png`, `index-1440.png` and their
`candidate-` counterparts. The baseline and candidate outputs were built from
their respective source trees; no historical source values were edited for
this presentation change.

## Delivered: a shorter path into the evidence

The previous opening explained the methodology, counted the corpus and
displayed the disclaimer before offering a country entrance. On a phone,
visitors passed almost two screenfuls before reaching the country directory.

The lobby now opens with a compact invitation and country feature cards.
Each has a direct entrance and a native disclosure for every decade. The UK
gets a reviewed room entrance instead of the stale description of a
developing collection. Japan retains its thematic entrance. The full
disclaimer remains visible, the reading guide is optional, and the complete
research inventory remains available below the visitor routes.

| Local Chromium measurement | Baseline | Candidate |
|---|---:|---:|
| Country directory top, 375px viewport | 1517px | 471px |
| Country directory top, 1440px viewport | 824px | 346px |
| Lobby document height, 375px viewport | 6282px | 4773px |
| Lobby document height, 1440px viewport | 3388px | 2560px |

These positions measure layout, not visitor comprehension. The candidate
showed no document-wide horizontal overflow on the six inspected page types
at either width. New browser coverage exercises first-viewport access to a
country entrance, expansion of the decade archives, and entry into the UK
room without JavaScript. Existing badge geometry checks now open the native
disclosures before inspecting their contents, avoiding a vacuous hidden-state
check.

## Editorial corrections in the UK routes

Questions can imply facts as strongly as declarative captions. The seven UK
openings were rewritten around what the selected records actually measure.
This review checked their framing against the authored records; independent
primary-source transcription verification is a separate data-review task.

| Room | Previous implication and evidential limit |
|---|---|
| 1950s | A nationally rented majority: the tenure record covers England and Wales, while pay and licences use other populations. The new question names the separate records. |
| 1960s | Unchanged hours and a television in nearly every home: the selected hours figure is a single observation; licences are counts without a household denominator. Neither supports that framing. |
| 1970s | Possessions counted before household income: the selected household-income record exists. The new opening asks who the surveys measured. |
| 1980s | Home ownership outpaced telephone ownership: the selected figures are 58% and 75%, respectively, and their geographies differ. The new question avoids the reversed comparison. |
| 1990s | Ownership peaked and computing began: the tenure observations rise from 68% in 1991 to 69% in 2001; a computer-ownership observation does not establish its beginning. |
| 2000s | Connection left the household budget unrecorded: an uncurated food basket is a collection gap, not evidence of an absent survey or an effect of connection. |
| 2010s | One connected household met a housing-market reversal: the selected housing, equipment and employee-job observations do not follow a matched household. |

The replacement titles and questions retain the original selected fact IDs.
They add no historical quantities or inferred household biography.

## Second tranche: reading controls and chart tables

The continuation addressed the concrete design leads above. Native topic
disclosures shorten the room's initial reading surface without removing a
record, source card, calculation or stable ID. Each summary keeps its topic
heading and mechanically computed counts. Enhanced expand/collapse controls
offer a continuous reading mode; without JavaScript, each topic opens normally.
Direct record fragments reveal their topic natively. A no-script topic-map
link lands on the visible summary, which still needs its normal activation;
the enhancement opens that topic and places keyboard focus at the summary.
Selected record links start keyboard reading at the record. Print styles
reveal closed topics without requiring JavaScript.

Local Chromium measurements against `a306998`, with topics initially folded:

| Room | Phone height before | Phone height after | Desktop height before | Desktop height after |
|---|---:|---:|---:|---:|
| US 1950s | 18149px | 4145px | 11103px | 2683px |
| US 2020s | 23684px | 4383px | 14325px | 2934px |
| UK 1980s | 6339px | 3994px | 4087px | 2515px |
| Japan 1990s | 7695px | 3802px | 4877px | 2562px |

The phone viewport was 375px wide; desktop was 1440px. The candidate also
includes parallel corpus curation: these measurements compare complete builds,
not an isolated CSS benchmark. The evidence remains present when unfolded.
These reductions describe initial
page length, not reduced corpus size or proof of a better visitor outcome.

Charts now have native table alternatives in the trends, affordability and
essay surfaces. The same point objects supply selected values; source series
supply actual annual observations. Missing years stay absent, excluded points
say "Not plotted", and source links remain operable without JavaScript.
Annual tables state the measured population. Computed annual values cite the
input source series and disclose their six-significant-digit display rounding.
Unsupported monetary minor-unit series are rejected by the annual-table
projection rather than silently producing an empty table.

The label-placement lead was confirmed: with a zero observation, the old
condition placed the value label on the same baseline as its decade tick.
The corrected test uses the upper plot boundary when deciding whether to
move a label below its point. A rendered geometry regression covers zero,
near-zero and high observations; no numeric geometry or source value changed.

Navigation targets are larger and labels are less letterspaced on phones.
Re-audit caught a wrapping regression that displaced the first country
entrance, and corrected it while preserving target height. Further regression
checks cover width, readable type and overflow at 320, 375, 900 and 1440px.
Malformed URL fragments also no longer abort the source-card enhancement.

Screenshots use the deployed CSP and response headers. Additional operator
evidence is `reading-before-375.png`, `reading-after-375.png`, their `1440`
counterparts, and `chart-table-375.png` / `chart-table-1440.png` in the same
gitignored review directory. The source-linked table was visually inspected
at phone and desktop widths. Browser tests exercise no-script source access,
native fragment revelation, calculated-record revelation, print visibility,
keyboard entry, collapse focus and repeated topic-link activation.

## Remaining evidence limits

A further data-presentation review corrected the food-share record archived
in the 1950s room: its label identifies CEX 1960–61. It remains inspectable,
but the source quantity is excluded from the earlier decade's chart, direct
metric, pair comparison, walkthrough bar and house annotation. The same
projection rule now propagates every declared arc exclusion, including daily
ATUS values excluded from weekly unpaid-work axes. Midpoint plot coordinates
also no longer become invented observation years in the text alternatives:
the table shows a curated decade or explicit record year and retains the
actual survey date in the record label.

Count copy now distinguishes **sourced records**, **derived exhibits** and
**documented gaps**. These are the same numeric buckets as before; a sourced
record need not reproduce a single published table cell. Records with an
audit calculation identify the calculated value and expose its method,
rounding and limited field coverage. The badge does not claim every number
in a compound record has been replayed. Source calculations are not added to
the separate derived-exhibit count.

The later withdrawal of the 1970s expenditure/apparel shares was checked
across all consumers. Budget-composition views now keep an explicit linked
gap instead of silently omitting an unparseable or withdrawn row. Pair
views also refuse to print a nominal food-expense paragraph as the value
of a percentage axis. The 1970s opening acknowledges the unfinished budget
denominator. Exact page contracts were refreshed only after inspecting
landmark/disclosure differences and the actual sets of changed source links
and fact marks; the independent skeleton and source-target checks remain.

The chart plot still uses contained horizontal scrolling on a phone; the
table is its alternative rather than a squeezed replacement axis. This review
does not establish that every small plotted mark is easy to select by touch.
It also does not substitute for visitor testing or qualification across all
browser engines. Further structural changes should follow an observed usability
problem rather than repeatedly rebuilding the presentation on speculation.

Further countries or richer household illustrations should follow evidence
acquisition and editorial selection. Record density alone does not establish
a shared population, a continuous trend, or a reconstructed household.
