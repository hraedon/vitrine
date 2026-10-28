# Primary-source review — 2026-10-28

This review used the source archive at `/projects/vitrine/samples` on
`mvmcc02`, against the corpus at `f487ecf`. It sampled prominent observations
and the newly enrolled UK wing. It does not certify the entire corpus.
Existing source inputs, structured headline quantities, confidence tiers and
survey populations were retained. The UK 1953 compound rental split and Japan
broadband observation date were corrected. Two new England dwelling records
were then added from a newly acquired official report, as described below.

## Archive replay and added coverage

Before changes, all **129 declared source-field checks** reproduced from the
saved bytes, using `run_audit` without writing a ledger. Coverage was 129 of
778 authored facts, with no UK bindings. Missing locators are unclassified
evidence, not proof that a source is missing or a datum is wrong.

The review added **30 direct-source bindings**: five UK disposable-income
anchors, eighteen UK durable-goods ownership observations and seven tenure
records. All **159 source checks** then passed (120 literal extractions and 39 calculations),
and `vitrine check` passed. The ledger was generated in the isolated
`/projects/vitrine-review-20261028` checkout with its own source tree on
`PYTHONPATH`; the authoritative main checkout was not modified. Existing
bindings were also replayed on this review date. Unchanged prior ledger entries
retain their original audit dates; the review date is recorded here.

The new checks use the publisher's original XLSX and CSV files. They do not
use the museum's derived series or an extraction dump as independent evidence.

### ONS disposable household income

Source registration: `ons-etb-household-type`. Archive:
`samples/30-uk-income/etb-hhldtype.xlsx`.

| Fact | Original worksheet and cell | Published GBP per year |
|---|---|---:|
| `uk-1970s-household-income` | `1977!G38` | 4,116 |
| `uk-1980s-household-income` | `1980!G38` | 6,888 |
| `uk-1990s-household-income` | `1997-98!I33` | 24,934 |
| `uk-2000s-household-income` | `2000-01!I33` | 30,181 |
| `uk-2010s-household-income` | `2010-11!I33` | 46,129 |

Each audit guards the worksheet's full year title, the non-retired block,
all three stacked cells defining two adults with two children, and the
disposable-income row label. Scaling to pence is explicit. The changing
column position is preserved rather than assumed constant. These remain
means for a household type, not medians or gross US-style family income.

### ONS household durable goods

Source registration: `ons-ghs-40yr`. Archive:
`samples/33-uk-diffusion/ghs-data-chart3.csv`, Figure 40.2.

The eighteen facts bind directly to rows 8 (1972), 10 (1978), 11 (1981),
14 (1990), 18 (2002), and 21 (2011). Columns 2–5 are colour television,
home computer, telephone, and car or van. Each binding guards the figure
title, unweighted-data note, percentage unit, column heading and year.
Only the selected headline field is audited; ancillary numbers and
interpretation in notes are not thereby validated.

### Manually re-read ASHE anchors

The saved ASHE Table 1 ZIPs for 1997, 2000 and revised 2010 were re-read with
`scripts/uk_ashe_extract.py`. All-employee median gross hourly pay was GBP
7.07, 7.93 and 11.14 respectively; median paid hours was 37.0 in each.
The workbook titles and `All` sheets identify employee jobs, with full-time
results printed separately. These match the six room facts. They have no
new audit bindings: the original XLS workbooks inside ZIPs are unsupported
by the present audit extractors. A conversion would require its own
documented provenance, rather than silently treating a converted file as
publisher bytes.

### ONS tenure: a compound-record error

Source registration: `ons-century-homeownership`. Archive:
`samples/32-uk-housing/ons-century-homeownership.csv`, rows 4–10 (1953–2011).

`uk-1950s-tenure` had attached the 1939 rental shares (58 percent private,
10 percent social) to a 1953 observation. The original CSV gives 1953 as
32 percent owned, **50 percent private rented and 18 percent socially
rented**. The owner-occupation headline is 32 in both years, so a check of
that number alone would have missed the error. The compound value and
notes were corrected, as was the 1960s note's comparison with the mistaken
social-rental starting point.

The seven new tenure audits check ownership, guard the actual year and
all column headers, and also guard both companion rental-share cells.
The original publisher CSV uses carriage-return-only record separators;
the CSV reader now accepts those without altering the archive bytes.
Regression tests cover LF, CRLF and CR separators and verify the original
byte hash. All 36 audit tests passed.

The GHS colour-TV notes also contained launch dates not established by the
cited ownership table. Those dates were removed from the 1960s–1980s notes;
the source-backed ownership observations remain. The recorded starting
point of an overview table is not proof that a survey never asked earlier.

## Corrections established by the primary documents

### Japan: equipment stocks and household ownership

Archive: `samples/37-jp-diffusion/nsfiie-2009-results4.pdf`, PDF page 1,
sections I.1.A–C. Publisher document:
[NSFIIE 2009 durable-goods summary](https://www.stat.go.jp/english/data/zensho/2009/pdf/results4.pdf).

- `jp-2010s-flat-tv`: the 652.2 percent increase concerns sets per thousand
  households, from 115 to 865. The household ownership rate is 61.9 percent.
  The note's claim that flat-screen TVs were a new survey item in 2009 was
  contradicted by the source's own 2004 comparison and was removed.
- `jp-2010s-pc-nsfiie`: the 15.8 percent increase concerns computers per
  thousand households, from 999 to 1,157. Ownership rates are 69.3 percent
  and 75.9 percent; the note now distinguishes those two measures.

The same page confirms the selected 2009 mobile-phone, car, washing-machine
and refrigerator ownership rates. This is a manual source reading, not new
machine-audit coverage for those records.

### Japan: broadband availability date

Archive: `samples/37-jp-diffusion/icwp-2015-chapter5.pdf`, printed pages
63–64 (PDF pages 16–17), Figure 7-2-2-2.

`jp-2010s-broadband` correctly transcribed 99.9 percent availability, but
dated it to the end of 2014 / FY 2014. The text and figure identify
**the end of March 2014**. The record now uses that date and separates
availability from the later fixed-line subscription count. The device
ownership survey named in the old note does not supply this infrastructure
availability measure.

Printed page 58 (PDF page 11), Figure 7-2-1-1, separately confirms the
end-2014 mobile/PHS, smartphone and PC household ownership figures of
94.6, 64.2 and 78.0 percent. These are distinct measures and dates.

### United States: watching television

Archives: `samples/13-atus/a1_2003.pdf` PDF page 2,
`a1_2009.pdf` PDF page 2, and `a1-2024.pdf` PDF page 3, all Table A-1.

`us-2020s-tv-watching-decline` correctly transcribed average-day TV
participation of 78.8 percent in 2003 and 72.8 percent in 2024. Its note
incorrectly described 2.58 to 2.60 daily hours as a decline. The note now
states the verified observations, including 2.82 hours in 2009, without
claiming that this intermediate observation was the series maximum.
The unsupported causal attribution to streaming/cord-cutting and an
unrelated mobile-subscription statistic were removed. These time-use tables
measure activity and participation; they do not identify causes.

## Evidence pins

SHA-256 of the bytes read during this review:

| Samples-relative file | SHA-256 |
|---|---|
| `30-uk-income/etb-hhldtype.xlsx` | `d1c870524ba5339120b5f94e732b3a9347b7e01cb79e9449e7825c0cd84cc323` |
| `33-uk-diffusion/ghs-data-chart3.csv` | `4582cf46618e0ad82a19b15509f9e45511533bd6ab3122a6a58e9038f520bc7e` |
| `37-jp-diffusion/nsfiie-2009-results4.pdf` | `418c398dd0076012b5061ef3bde50d86602287b86aaac81f30b20f15088d8c5e` |
| `37-jp-diffusion/icwp-2015-chapter5.pdf` | `feb30e0a64ba1cafd7f81faf335cab858647fc48e7a0aec58b2e58fa33d9168e` |
| `13-atus/a1_2003.pdf` | `a82614e1138727e9ca43c00ab6a8d8163057b3a0e03e5e1272cfa775f9779ca2` |
| `13-atus/a1_2009.pdf` | `cb2cd2e826430196c984edf8793c210a407a8db46b199257d3902929323000a3` |
| `13-atus/a1-2024.pdf` | `0778b8b3517d93e6eb2fc8ab901c10604904ff62ab4e2daab2e711bafc18686a` |

## Limits and next useful research

After the UK bindings and housing additions, 619 authored records remain without current field-audit
bindings. Confidence tiers describe evidence type, not verification coverage.
No whole-corpus accuracy claim follows from a green gate or this sample.

The highest-value remaining work is direct-source binding for UK earnings
and house prices, Japanese FIES budget observations and their calculated
food shares, and US compound food-price records. Interpretive and ancillary
numeric notes need review in addition to headline transcription checks.
Historical UK food reports already present in the archive should be read
before treating the room's food gaps as an acquisition problem: the saved
1974, 1979 and 1984 NFS reports contradict notes saying those decades are
absent from the archive. Their existence alone does not establish which
population or table can replace a gap.

The reviewed tables of contents supply a concrete research map:

| Report | Consumption | Expenditure | Prices | Methodology |
|---|---|---|---|---|
| 1974 | Table 9, printed p. 50 | Table 10, p. 53 | Table 11, p. 57 | Part IV appendices |
| 1979 | Table 7, printed p. 30 | Table 8, p. 33 | Table 9, p. 37 | Appendix A, p. 143 |
| 1984 | Table 8, printed p. 28 | Table 9, p. 33 | Table 10, p. 38 | Appendix A, p. 145 |

The reports are Ministry of Agriculture, Fisheries and Food publications,
with national tables for Great Britain. Their food-at-home quantities must
not become a complete diet or a median four-person family's basket. The
1974 preface also discloses interruptions around two general elections and
interpolation around those breaks. The 1970s and 1980s gap records now say
that these archived sources await transcription, rather than asserting that
the reports are unavailable.

## Independent check of the proposed English housing additions

The newly acquired `samples/58-uk-housing-review/ehs-homes-2011.pdf` and
its separate errata were independently read before new facts were selected.
The acquisition and any new fact bindings are recorded by their author.

The main report's printed p. 6 (PDF p. 8) defines the dwelling estimates as
physical inspections carried out April 2010–March 2012, with an April 2011
midpoint. The sample includes occupied **and vacant** dwellings in England;
it is distinct from the household interview sample labelled 2011–12.

Printed p. 10 (PDF p. 12) publishes mean total usable floor area of 91 m².
Printed p. 90 (PDF p. 92), paragraph 4.6, publishes 90 percent central
heating; Figure 4.2 on the next page explicitly uses all dwellings as its base.
Its footnote defines central heating as a boiler feeding radiators, excluding
warm-air, underfloor, ceiling and electric-storage systems. Availability of
this particular system is not equivalent to prevalence of any heating.

The errata's PDF p. 3 corrects the floor-area definition: integral garages
and integral balconies are included. Habitable lofts require fixed stairs;
external and partition walls and staircase footprints are excluded. The
errata do not correct either proposed numerical observation. The source is
suitable for two separate England dwelling facts with these definitions,
not a UK-wide household estimate or a matched household portrait.

## Housing acquisition delivered

The reviewed observations are now `uk-2010s-mean-dwelling-floor-area` and
`uk-2010s-dwelling-central-heating`, both Tier A. The existing amenity-gap
record keeps its stable id and now specifies the remaining untranscribed
room-count and bath/WC fields. An England dwelling observation does not
silently fill a UK household field.

`scripts/uk_housing_extract.py --download` acquires the official report,
errata and chapter one/four XLS annexes into gitignored
`samples/58-uk-housing-review/`. It rejects publisher bytes differing from
the inspected SHA-256 vintage. Its stdlib PDF reader extracts the two printed
observations into a deterministic dump, guarding the corrected size and
heating definitions. Two ledger bindings use that dump and guard both
original PDF hashes, observation period and dwelling population. The
archive-backed test independently regenerates the dump from the original
PDFs. This is a reproducible extraction artifact, not independent publisher
evidence, and remains distinguishable from the thirty direct UK bindings.

All **161 source-field checks** reproduce (122 literals, 39 calculations).
There are now **780 authored facts** and **16 derived exhibits**. The source
archive replay validates declared fields, not every number in a compound note.

## Continued source review — 2026-10-28, after `a306998`

The preceding sections record the first review and its **161-check** baseline;
those historical totals are unchanged. This continuation inspected selected
US food/expenditure records, Japanese FIES budget tables, UK earnings/house
prices, and the primary mortality tables. It also read the archived NFS report
before curating two observations. It does not certify every ancillary number
or interpretation in the museum.

The current archive replay passes **221 source-field checks**: **169 literal
extractions and 52 documented calculations**. All 161 prior entries remain;
136 retain their previous audit date because their fingerprint, source hash,
extracted value and operands are unchanged. Twenty-five prior entries receive
the new date following revised source/population/context text. Sixty bindings
are new: nineteen FIES, sixteen UK earnings/house prices, two NFS, eight US
compound-expenditure headline fields, and fifteen historical cause-of-death
rates. The replay date is **2026-10-28**, independently of retained entry dates.

| Country | Authored facts | Current field bindings | Without a field binding |
|---|---:|---:|---:|
| US | 617 | 142 | 475 |
| UK | 77 | 50 | 27 |
| Japan | 88 | 29 | 59 |
| Total | 782 | 221 | 561 |

There are also sixteen derived exhibits, 130 registered sources and twenty-two
assumptions. A binding covers its declared field and guards; a full compound
placard qualifier, described below, supplies additional evidence without
inflating this field count. An unbound fact is not thereby an incorrect fact.

### Japanese FIES: literal tables and population boundaries

`scripts/workbook_review_extract.py` reads the original archived XLS bytes.
It records cell coordinates, title, year, item/unit headings and original file
hash for every selected observation. Nineteen bindings cover seven workers'
household income means (including the earlier 1955 all-cities series), six
consumption means and six food shares. The shares are computed by the audit
engine from literal Food and Consumption expenditure cells in the same source
row, with one decimal place and half-up rounding; `jp-fies-food-share` states
the method. Existing quantities reproduce unchanged.

The original English exclusion footnotes apply to the entire long-run table,
not just pre-2000 observations:

- `36-jp-income/fies-a18-1.xls`, sheet `二人以上の世帯`, A2 titles the
  1963–2017 table; C82 reads: “＊ The data is not including agricultural,
  forestry and fisheries households.”
- `36-jp-income/fies-a18-2.xls`, sheet `勤労者世帯`, A2 titles the
  1963–2017 workers' household table; C81 carries the same exclusion.

The guards preserve these original readings (whitespace normalized), including
for 2005 and 2015 selected cells. The `jp-fies` source, selected notes and the
1962 seam assumption now respect that scope. The 1955 all-cities income table
is separate; the later exclusion is not projected backwards onto it. Workers'
household income and all-type two-or-more-person consumption remain separate
measured populations. The publisher's Food heading is retained; an unsupported
narrower “food and nonalcoholic beverages” gloss and causal explanations were
removed.

Formula rejection is independent of `xlrd`'s cached cell type. The extractor
reads the original OLE Workbook/Book BIFF stream and records FORMULA opcodes
0x0006/0x0206/0x0406. A selected coordinate is rejected if it appears as a
formula anywhere in the workbook. This conservative cross-sheet union can
reject an unrelated formula at the same coordinate, but cannot accept a
selected cached formula as a literal. A regression rejects a real formula in
the original income workbook at first-sheet row 52, column 13 (one-based).

### UK earnings, housing prices and food at home

Sixteen new bindings use guarded original source fields: seven mean male
full-time weekly earnings observations from the 1938–2025 XLSX, six hourly
pay/paid-hours fields from the original ASHE ZIP/XLS releases, and three house
price fields from the ONS annual XLS. Weekly earnings distinguish manual from
all-occupation columns, Great Britain, April survey timing and mean statistic.
No level changed. The 2010s “longest real-wage squeeze since the 1860s” claim
was removed: the cited nominal earnings table cannot establish it. The all-
employee wage-anchor assumption now describes sample coverage without an
unsupported numerical adjustment. Causal smartphone/car/tenure interpretations
were removed from the selected 2010s GHS notes.

Two new Tier A facts use NFS 1984 Table 8, printed p. 28/PDF p. 40:
`uk-1980s-full-price-whole-milk` is **3.53 British imperial pints per person
per week** and `uk-1980s-eggs-at-home` is **3.21 eggs per person per week**.
These are the Consumption yearly-average column, distinct from the nearby
Purchases values of 3.47 and 3.10. Root independently inspected the page image.
Appendix A, printed pp. 145–146/PDF pp. 157–158, defines consumption as food
entering the home, not actual ingestion. The survey covers private households
in mainland Great Britain and the Isle of Wight, excluding the Isles of Scilly
and Scottish islands, using one-week diaries. Meals out, pet food,
confectionery and alcohol are excluded; soft drinks are separate from the main
tables. These observations are not a complete diet or a four-person family.

The original PDF is
`31-uk-expenditure/Domestic_Food_Consumption_and_Expenditure_1984.pdf`, SHA-256
`b462e25868b77ba74e17eabeac4679837d5b0fe4382a977861886bbba04a72b2`.
`scripts/nfs_1984_extract.py` checks the original hash, table text, selected
rows and method, then emits a reproducible artifact. Both numeric bindings
guard that original hash and source context. The stable food-gap record is
narrowed to remaining basket/expenditure work and now cites `maff-nfs-1984`.
The 1974/1979 research map above remains a candidate, not new observations.

### US food prices and expenditure definitions

The historical price review read the actual row and footnotes, retaining the
original package sizes:

- BLS Bulletin 1055 Table 4, printed p. 9/PDF p. 14: 1950 sugar is 48.7 cents
  per five-pound package and potatoes 69.2 cents per fifteen-pound package.
- Statistical Abstract 1970 Table 530, printed p. 349 (`1970.zip`, member
  `1970-05.pdf`, PDF p. 13): round steak is 105.5 cents/lb in 1960 and 133.3
  in April 1970. Delivered milk is 65.5 cents per **half-gallon** in April
  1970; footnote four says quart through 1960 and half-gallon thereafter.

These replace mixed-row values, rounding errors and an incorrect quart unit.
The unsupported milk growth and comparisons between different meat cuts were
removed. Root independently inspected the 1970 table. Regression tests check
package units as well as numbers.

Five compound modern price placards (1980, 1990, 2000, 2010 and December 2024)
reproduce all **twenty-six prices** from newly retrieved public BLS API
responses saved on 2026-10-28. No key or contact address was sent. The script
pins those response bytes and six BLS-sourced FRED metadata pages, checks
unique series IDs, categories/units, requested year and December period, and
formats nearest-cent half-up values. Ground chuck is explicitly named rather
than silently generalized to all ground beef. This is a newly retrieved vintage,
not a recreation of an earlier download or a constant-quality price index.
These five compound qualifiers add no single-field audit coverage.

For 1985/1996/2005/2013 CEX, `scripts/cex_food_review.py` reproduces the entire
four-person food placard and **thirty-six category shares** across four budget
placards from original PDF/XLSX cells. The older three budget vectors and four
food shares use ratios of annual means, not mean household shares. The 2013
budget Share cells are publisher-printed literals. Eight headline fields have
audit bindings; three older artifact bindings also guard the full generated
placard string. The direct 2013 XLSX binding remains distinguishable from the
curator artifact. The workbook's erroneous A1 dimension does not prevent
original targeted cell access, so the core reader was not changed.

The 1985 food-away amount is blank in the source. Its inferred value and
home/away percentages were removed rather than filling that blank. Unneeded
hand-computed home/away percentages were removed in the other years too.
Published amounts remain literal, and population labels consistently say
four-person consumer units. Separately sourced all-consumer-unit records keep
their own scope. New source entries identify the actual historical table,
while digital-posting dates are explicitly distinguished from survey years.

The earlier 1960–61 B11 budget observation is explicitly an urban consumer-
unit observation, including when presented as a later checkpoint in the 1950s
room. The separate B20 appliance table (PDF p. 15/printed p. 108) uses the
publisher's term CES urban families. It is not forcibly harmonized to Census
families or to four-person consumer units. Refrigerator ownership is **82.7%**,
not 84.7%. Other selected CES values match the actual row. False cross-checks
using different Consumer Buying Intentions rows were removed. The three
appliance facts use a separate population-specific source, and root independently
inspected this page image.

For 1972–73, Bulletin 1992 Table 2 printed p. 37/PDF p. 44 gives food
$2,088.85, food at home $1,542.58, food away $524.63 and meals as pay $21.64
for four-person units. The previous $546 away amount silently combined meals
as pay. `scripts/cex_1972_review.py` now reproduces all thirteen displayed
food-category amounts at literal cents precision. Root inspected the original
page. The original PDF hash is
`448844ea53f0c7700c8fd43ce278c91ccd3fafedafcb36aca6f9129f0e062cc3`.
A damaged non-selected five-person bakery OCR token is ignored without repair;
the selected and preceding columns must each remain complete literal decimals.
Mutation tests reject a damaged first cell, preventing a silent column shift.

The previously displayed 1972 share and budget vector used an undocumented
constructed $12,226 total. The report prints current consumption separately
from insurance/pensions and gifts. The unsupported food share quantity was
removed; the stable expenditure-share and apparel-share records now render
verification gaps. No modern denominator was imposed to preserve a chart.
A repository scan found no surviving $12,226/17.1% budget or $16,155 wrong-
column income echoes in current data, curation, essays or documentation.
An unrelated 17.1% vehicle-distribution value remains untouched.

### Mortality and the final bounded interpretation check

The independent architecture reviewer verified fifteen historical heart,
cancer and stroke observations against the official NCHS CSV and added
bindings with year/cause/header guards. Its original hash is
`867d39e039b9ecb9843be3e8b3473250fec03050dc62d7d4409c1f737b731160`;
bytes and the HIST293 definitions are archived under `60-mortality-review/`.
All selected years are after national coverage began in 1933. HIST293 states
that historical rates also use the 2000 standard population; there is no
invented pre/post-1999 standard-population seam. ICD and population-denominator
revision caveats remain explicit.

The actual NCHS Data Brief 548 HTML confirms 2024 life expectancy 79.0 and
2023 78.4, an increase of 0.6. The old ancillary 78.6/+0.4 statement was
corrected without changing the 2024 headline. Archived HTML hash:
`dc96f7a1635477ab63123b064a274ab8af47dd01d55f4e360e75bee92d9d6be1`.

A final bounded read removed unsupported causal attribution from the 1970
poverty note, the three 1910s price-index notes and the 1947 family-size note.
It also removed an unqualified 1972 CEX division offered as a new-car-price
cross-check. These descriptive sources do not identify causal effects. This
editorial cleanup is not additional numerical verification of those domains. The
1940s expenditure gap now states an unverified room comparison rather than
claiming online absence, and its later-survey chronology includes 1972–73.

### Reproduction and remaining limits

The original XLS/PDF bytes remain in their topic directories; new responses,
metadata and extraction artifacts are in gitignored `59-workbook-review/`.
The archive MANIFEST records all artifact hashes and **xlrd 2.0.2, pypdf
6.14.2 and openpyxl 3.1.5**. These optional curator readers do not enter the
stdlib core. Different extraction versions can alter PDF/OCR text despite
identical source bytes; guards fail closed and should be inspected before
repinning. Scripts contain original hash pins and exact extraction locators.

From the isolated checkout, with the absolute candidate `PYTHONPATH`:

```sh
export PYTHONPATH=/projects/vitrine-review-20261028/src
.venv/bin/python scripts/workbook_review_extract.py
.venv/bin/python scripts/nfs_1984_extract.py
.venv/bin/python scripts/food_price_review.py
.venv/bin/python scripts/cex_food_review.py
.venv/bin/python scripts/cex_1972_review.py
.venv/bin/python -m pytest -q tests/test_workbook_review.py tests/test_nfs_1984.py tests/test_food_price_review.py tests/test_cex_food_review.py tests/test_cex_1972_review.py tests/test_mortality_audit.py
.venv/bin/python -m vitrine.cli audit
.venv/bin/python -m vitrine.cli check
```

The focused suite passes **33 tests**, including complete archive re-extraction,
changed-byte rejection, real XLS formula rejection, category/period/unit
mutations and the 1972 column-boundary regression. The complete 221-field
replay and provenance gate pass in the isolated checkout. Full integration
checks and independent product review are reported by the integrating agent.
The 561 records without bindings, other unreviewed compound notes, unresolved
historical definition seams and untranscribed NFS tables remain outside this
verification claim.
