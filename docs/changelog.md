# Changelog

## 2026-09-01 — Exotic turned ordinary (Plan 027 WI-6a)

Four commodities on one shared pounds-per-person axis, from the USDA/ERS Food
Availability data system: broccoli 0.40 → 5.24, bell peppers 2.08 → 11.06,
avocados 0.45 → 8.06, grapes 2.92 → 8.50. Twenty-five cards across seven
rooms, and the wing's first shared-axis arc group. The exhibit is the liftoff
from near-nothing — things that were not in the shop becoming things nobody
remarks on.

Every card says what the number is not. This is **availability, not intake**: a
disappearance estimate, production plus imports less exports and non-food use,
over population. It says what the food supply made available per person, not
what anyone ate. ERS publishes a separate loss-adjusted series for
consumption-like figures and this is not it.

The two workbooks do not share a layout — the fruit sheets carry an extra
"Shipments to U.S. Territories" column and print the "Farm" sub-header a row
lower — so a fixed column index is right for one and wrong for the other. The
first draft was, and failed on the first fruit sheet. Columns are now found by
their printed labels, the availability column by the spanner above it (the
header row prints two columns beginning "Total"), and the result is then
checked arithmetically: farm per-capita must equal availability ÷ population
for every year. Pointed one column right, at the retail figures, that check
rejects all four commodities.

A caveat was wrong until a test caught it. It read "avocados fall through the
1990s"; they rose, 1.42 in 1990 to 1.94 in 1999. Rewritten from the data — the
real irregularity is the 1980s swing (2.37 in 1986, 1.08 in 1989) and broccoli
sitting lower in 2022 than in 2000. That is the fifth prose numeral this plan's
guards have caught today.

The design system gained a fourth arc-group colour role: `copper-deep` was
already a token but was not wired into the group renderer, and four
commodities need four colours. A test asserts no two members share one.

**WI-6 is not finished.** The plan specifies four apparatuses; this is the
first. The derived variety-count, the produce-SKU confrontation number and the
1955 Household Food Consumption Survey checkpoint are tracked as FWI-007.

## 2026-09-01 — The peak is 1960 (Plan 027 WI-5)

The wing's sixth arc: births per 1,000 women aged 15–19, selected years
1950–2020, in eight rooms. It earns its place because it refuses to be a story
about progress. **The highest figure NCHS publishes is 1960 — 89.1 — the decade
usually remembered for its families**, not some more distant past; and the rate
**rose** between 1980 and 1990, from 53.0 to 59.9, before resuming its fall to
15.0 in 2020. The arc is deliberately not marked falling, and two tests assert
that shape so it cannot be flattened later.

The card notes say what the number is, because it is routinely misread: it is a
rate over *every* woman aged 15 to 19, not over those who were sexually active,
and in the earlier decades most of these births were to married women. It
measures teenage childbearing, which is not the same subject as teenage sex.

Plan 027 floated "~96 per 1,000 at the 1957 peak" as a lead to verify. **It is
not verified and appears nowhere in the data**: NCHS publishes selected years,
not annual ones, and this table does not print 1957. The line connects
published rows and says so.

Three NCHS documents were compared. A later edition of the same trend table
agrees on all twelve overlapping years; NVSR 72(1), compiled independently,
agrees on all six. Both traps this table sets were hit during the work and both
were caught. The reports repeat their whole structure once per race group — the
first "All races" heading in NVSR belongs to a different table, and the first
race block a naive read meets there is Hispanic, whose 2020 rate is 23.0
against the all-races 15.0. And "15–19" is a spanner over three columns whose
offset differs between the two document families: reading NVSR at the trend
table's offset returns the 15–17 sub-rate, 9.9 instead of 22.3 for 2015, about
half and entirely plausible alone.

One repository fix came out of it. `cdc.gov` returns 403 to browser-like
User-Agents and serves plain tool agents instead — the exact opposite of
`bls.gov`, which demands a contact address. The link checker sent only a
browser agent, so both new citations would have reported bot-blocked and their
content markers would never have fired. It now retries a 403 once with a plain
agent, which makes these citations genuinely verified in CI. It does not rescue
bls.gov, and should not: that host wants personal data this public repository
does not carry.

## 2026-09-01 — Nobody counted: the workplace-death arc (Plan 027 WI-4b)

The wing's fifth arc is four slots wide where the others are thirteen, and the
shortness is the exhibit. **The United States kept no federal census of the
people killed at work until 1992.** The Census of Fatal Occupational Injuries
has covered all fifty states only since then, and BLS changed the rate's basis
in 2006 from employment to hours worked, so the one continuous single-measure
stretch the record supports runs 2006–2024. It moves between 3.3 and 4.2 with
no trend the record can call a fall, and the arc is deliberately not marked
falling — a flat line must not be dressed in the museum's decline colour.

Plan 027 asked for this as a century-long arc, NSC estimates spliced to CFOI,
with "~61 → ~3.5 per 100,000" named as a lead to verify. **That arc is not
constructible from freely published primary sources.** The century-long figures
in circulation come from the National Safety Council's *Injury Facts*, a
commercial publication, not a government census. Rather than build a weak
version to fill the slot, the absence is rendered: the 1990s room carries a gap
card naming 1992 and the 2006 basis change, and the arc says plainly that for
nine decades nobody counted.

The workbooks' column layout changes three times across nineteen years, and the
first draft read by fixed index — which silently returns *total hours worked*
instead of the rate for 2017 (285,977) and 2018 (292,527.5). That surfaced only
because the values were cross-checked against a second BLS document, the data
labels on its own rate chart. The extractor now locates the column by header
text, and all twelve overlapping years reproduce exactly.

One honesty note is carried in the data itself: `www.bls.gov` returns 403 to
any client without a contact address in its User-Agent, and this repo's link
checker sends a plain browser agent. So this citation reports as bot-blocked in
CI and its `expect` markers never fire there. A marker that never runs is not a
check, so the source entry says so and a test asserts that it keeps saying so.
The markers were verified locally against the served page.

## 2026-09-01 — Road deaths: a rate is not a count (Plan 027 WI-4a)

The "different country" wing gains its fourth arc: motor-vehicle deaths per
100 million vehicle-miles travelled, 1900–2023, from FHWA Table FI-200, with a
card in every US room. The line falls from 36.00 to 1.11 — about thirtyfold —
and the arc's first caveat exists to stop that being misread. **Absolute road
deaths peaked at 55,600 in 1972 and were still near 41,000 in 2023.** What
collapsed is the risk per mile, because the miles grew far faster than the
toll. The 1940s card makes the same point from the other direction: wartime
rationing cut travel by 38 percent and deaths by 40 percent, and the rate
barely moved. Fewer people died because less driving happened.

FI-200 publishes four rate columns side by side, and reading the wrong one
would produce a plausible, wrong chart. The extractor therefore identifies its
column by **arithmetic rather than position** — it recomputes the rate from the
table's own fatality and VMT columns and refuses to write unless the published
figure reproduces for every year. Aimed at each neighbouring column in turn,
the guard rejects all three and accepts only the right one.

The 1900–1995 rows were cross-checked against a second, separately-published
FHWA edition (Summary to 1995, April 1997): **95 of 96 years reproduce
exactly.** The one difference is 1995, that edition's terminal provisional
year, since revised from 41,770 deaths to 41,817. Recorded, not smoothed.

Four numerals drafted for the card prose from recall were wrong, and the
card generator's assertions caught all four before anything was written: the
1972 peak (55,600, not 54,589), the year the rate peaked (1909, not "around
1910"), the first year below 2.0 (1991, not 1990), and — the instructive one —
the wartime story, which as drafted said the rate fell when in fact it barely
moved. That is Plan 027 D3 working as designed: the famous numbers are the
dangerous ones.

Two of the plan's own assumptions did not survive contact with the source, and
the source won. It anticipated splicing NSC estimates to FARS at 1975; FHWA
publishes the whole span in one table, so there is no splice — what there *is*
is a definitional change at 1976, when the count narrowed to deaths within 30
days of the crash, now carried as a caveat, a series note and an `expect`
marker. And it anticipated an empty 1900s ("cars barely existed; there is no
rate"); FI-200 does publish one, so rendering a gap would have been inventing
an absence. The figure is carried with its thinness disclosed: it rests on 36
recorded deaths against a back-cast travel estimate.

**WI-4's second arc is not here.** Workplace fatalities per 100,000 workers is
blocked on acquisition — bls.gov 403s non-browser clients, its flat-file host
wants a contact address in the User-Agent, and the NSC's historical estimates
are a commercial publication. Tracked as FWI-006 with the specific decision
that would unblock it, rather than left as a silent half-delivery.

## 2026-09-01 — Alcohol per capita, and the gap that is the exhibit (Plan 027 WI-3)

The "different country" wing gains its third arc: apparent per capita ethanol
consumption, 1934–2023, plus a card in every US room. The point of the exhibit
is not the line but the hole in it. **National Prohibition renders as a gap**,
because the source table renders it as a gap — NIAAA's series is built from
legal beverage sales, so when legal sales ended in January 1920 the
measurement ended with them, and Table 1 prints the single word
"(Prohibition)" where fourteen years of numbers would be. Drinking did not
stop; the state's ability to count it did. Nothing is interpolated across those
years and no reconstruction is substituted for them.

Two other shapes of the record survive into the data rather than being
smoothed away. The pre-1934 figures are published as five-year ranges, not
single years, so the 1900s and 1910s cards carry ranges and say so on their
face (2.39 for 1901–1905; 2.56 for 1911–1915) while the annual series begins
at 1934 — a range cannot be keyed to a year without inventing a datum. And the
1930s card opens at **1934, not 1930**, because its decade begins inside
Prohibition: the first year the table can report again is the year after
Repeal, at 0.97 gallons, well under half the 1911–1915 level.

The arc is deliberately **not** marked falling. It is a discontinuity, not a
trend: the 1911–1915 level is not reached again until the 1970s, and the modern
peak (2.76 in 1981) sits above every year since.

Provenance was established rather than assumed. The archived PDF was compared
byte-for-byte with the document served at the cited URL — **sha256-identical**
— so the transcription source and the citation target are the same bytes. The
values were read out of the PDF itself, not out of the flattened text dump
beside it and not out of the markdown extraction summary a prior session left
in the same directory. That distinction earned its keep: the summary states
that 1970 was the last year on the ages-15+ denominator, while the table's own
header puts 1970 already on the 14+ basis. The header was followed. Two
independent extractions of the PDF were then compared value by value — all 90
reproduce exactly.

The source registry entry declares `(Prohibition)` as a content marker, so if
NIAAA ever republishes with those years backfilled the link check reddens
rather than the museum quietly citing a document that no longer says what its
cards say it says. `tests/test_alcohol_series.py` holds the two committed
surfaces — the cards and the series — against each other, and each of its
gates was proven to fail by mutation.

## 2026-09-01 — The comparative layer stops reaching outside its wing (FWI-004, FWI-005)

Every room whose work-buys panel held any fact rendered "See this metric across
all decades →", pointing at `affordability/index.html`. That page is projected
over `CURATED_COUNTRIES`, which is US-only, so the link fired on all seven UK
rooms and all seven JP rooms and landed the visitor on a page holding no fact
of their country — zero `uk-` ids, zero `£`. It was pre-existing rather than
introduced by the UK affordability work; that work only made it visible, by
putting a real priced exhibit where three "no reliable record" cards had been.
The link now renders only for a room whose country the comparative layer
actually covers: **13 US rooms, zero UK, zero JP**.

The underlying fault was larger than one link, and is the second half of this
entry. Three surfaces compare rooms across decades — the corridor atlas, the
pair matrix and the affordability arcs — and all three are keyed by decade
alone while holding US fact ids. A second country's "1950s" is a different
room, so the key is only well-defined inside one wing. The stage layer solved
this in August by keying on country; the comparative registries still held
their side of it by discipline, and nothing reddened if that stopped being
true. Two mechanisms replace the discipline:

- `validate_comparative_registries` runs at build time beside the essay
  registry gate. It walks every decade-keyed fact-id registry — `COMPOSITIONS`,
  `HOME_SIZE_FACTS`, `WALKTHROUGH_FLOOR_AREA`, `WALKTHROUGH_PEOPLE` and every
  arc's `fact_ids` — and reddens the build if any entry resolves to a room
  outside `CURATED_COUNTRIES`, or to no room at all.
- `afford_fact_ids` skips non-curated rooms and raises on a decade collision
  inside the curated set rather than taking the dict's last-wins overwrite,
  which would have put one country's price on another country's hours axis.

Neither mechanism changes a single rendered value today: the guard passes over
the committed corpus unchanged, because the invariant does currently hold. They
exist so that the next country to join the story layer without its own
comparative curation is a red build rather than a borrowed exhibit. Each is
covered by a test proven to fail when its fix is reverted.

## 2026-09-01 — The UK affordability axis (FWI-001)

The seven UK rooms rendered facts but could not answer the museum's central
question — what a thing cost in hours of work — because no UK room carried a
wage or income anchor. Five now do, and three compute both axes end to end:
the average UK house took **10,764 hours of work in 1997, 12,806 in 2000 and
22,547 in 2010**, or 305%, 337% and 545% of a two-adult-two-child household's
annual disposable income. Every input is Tier A and every ratio is computed by
`affordability.py` at build time from structured amounts.

Thirteen rendered gaps closed (35 → 22 across the wing), all with official
sources: ASHE median gross hourly pay and total paid hours (1997, 2000, 2010);
ONS effects-of-taxes-and-benefits disposable income for non-retired two-adult,
two-child households (1977, 1980, 1997/98, 2000/01, 2010/11); ONS simple
average house prices (1997, 2000, 2010); and weekly hours from the Department
of Employment's Year Books for the 1960s (47.5, April 1965) and 1970s (42.7,
April 1976, with the 166.6p hourly earnings beside it).

Two new `Measure` variants keep the UK denominators from being chained to the
US ones: `disposable_household_income` (post-tax, per household) is not
`money_income` (gross, per family), and `median_hourly_pay` is not
`hourly_earnings` (a mean of a narrower population). The comparator refuses
the chain mechanically rather than by convention.

Three rooms are honestly still blank and say why in their own notes: the 1970s
hourly wage is 166.6p and cannot be an anchor while GBP is held in whole pence;
the 1980s has no hours in the record between the last Year Book (1976) and
ASHE (1997); the 1950s has none of the three ingredients. One standing claim
was **retracted**: the 1950s and 1960s rooms asserted that "no continuous
hours-worked survey exists before the Labour Force Survey (1973)", which the
Year Books disprove.

Three extraction scripts land with the data — `uk_ashe_extract.py`,
`uk_etb_extract.py`, `uk_house_price_extract.py` — each locating its column by
composed header rather than by index, because in all three workbooks the
column moves. The house-price cross-check caught itself reading the wrong
column, and the ETB direct-tax rows do not reconcile to gross − disposable
(each row is independently rounded), so every row is transcribed. Full evidence
in `docs/verification-log.md`, section FWI-001.

## 2026-08-29 — Adversarial-review corrections (Plan 027 Phase A + Plan 024 docs)

A cross-lineage adversarial review re-verified every landed number against
the archived documents (136/136 transcription values clean) and found
provenance/presentation defects, all fixed: the smoking-prevalence series
now cites the CDC/NCHS trends table it was actually transcribed from
(registered as its own source; the ALA compilation it was mis-cited to
reads 2006 as 20.6 where the trends table says 20.8, and supplies the 2000
value where the trends table is blank — both divergences disclosed on the
cards); unsourced definitional side-claims (1997/2019 redesigns) came out
of truth-path strings, keeping the on-file 1992 some-days note named to the
Surgeon General's report; arc markers now sit at their facts' own years via
`price_year`, which also turns on the drift detector for all 19 bound
facts; the consumption arc stops at 1994 where its table does instead of
piling post-1994 markers on the chart edge; two ALA sex-split cells
(female 2000, male 2020) corrected against the table on disk; and thirteen
duplicate day-panel consumption facts were removed in favor of the
pre-existing table-panel facts they unknowingly duplicated. Also from the
review: `facts.csv` now carries a UTF-8 BOM (spreadsheets were mojibaking
¥/£ cells), the export schema doc states the real quantity-containment
rule and the empty-string anchor convention, the stage home-scale math
rejects non-positive quantities, the walkthrough projection makes a
decade collision a red build instead of silent dict last-wins, the
architecture test lists the core modules explicitly, and StageCuration
registries are mechanically checked (position keys, country-decade fact
prefixes, home-size baseline presence) — verified 383 tests green.

## 2026-08-29 — Plan 027 Phase A (the "different country" wing + the smoking flagship)

Wing V, "The past was a different country," opens with the smoking flagship:
two arcs backed by three new Tier A series, all transcribed from primary
tables on disk (`samples/34-smoking/`, verification log 2a–2c). Cigarette
consumption per adult runs 1900–1994 from MMWR SS-3 Table 1 (USDA/ERS basis;
script-extracted then eye-verified, including the three irregular rows — 1900
has no change column, 1993/94 carry provisional/projected footnote markers),
with a TTB-removals continuation 2000–2023 spliced at the basis change and
the 1995–99 gap left as the exhibit. Smoking prevalence (NHIS survey years
1965–2014, CDC/NCHS trends table) renders pre-1965 as gaps, never zeros; the
2015+ cells that exist only as Early Release preliminary or secondary
analysis stay out of the series. Thirteen consumption facts join the day
panels (mid-decade checkpoints, each label naming its year); the prevalence
facts already existed from the 2026-07-17 curation and agreed with the new
series at every overlapping year — the drift gate and a three-way cross-check
(MMWR Table 2 / CDC trends / the facts) confirm it. The wing's introduction
states the selection principle: normal, legal, ubiquitous then;
unthinkable, illegal, or vanishingly rare now. Falling lines are not
presented as progress.

## 2026-08-29 — Locale-configurable stage layouts (country-keyed stages)

The stage curation is country-keyed: `STAGE_BY_COUNTRY` maps each country to
a `StageCuration` (diffusion/stat bindings, composition and food-share zone
notes, home-scale facts with the country's own baseline, and optional
per-artifact layout overrides over the shared `svg.STAGE_POS`). The UK and
Japan now draw stages from their own facts — GHS diffusion and tenure, the
1950s/60s TV-licence counts as stat glyphs (never on the percentage axis),
NSFIE durables, FIES food-share zone notes, and a Japan-specific floor-area
baseline in m² (the US baseline stays square feet). A country without stage
curation keeps the bare stage. The renderer now enforces room membership
for every stage-bound fact id, so a binding naming another room's fact —
the borrowed-exhibit failure the split exists to prevent — is a red build
even when the id resolves globally. The stage-geometry audit and the
absent-technology test now run over every room's own curation.

## 2026-08-29 — Plan 024 follow-ups (CI export run, README, export schema doc)

The new export surface is now discoverable and CI-exercised: CI runs
`vitrine export --out _export` after the render-coverage gate (the
standalone CLI path — the same "not silent in CI" lesson WI-024 taught),
the README documents the archive wing, `vitrine export`, and `CITATION.cff`,
and `docs/export-schema.md` is the consumer contract for `corpus.json`
schema version 1 and the CSV pair — field semantics, the minor-units
convention (divide by the currency registry's digits, never assume 100),
the quantity-in-value guarantee, citation guidance, and the versioning
promise.

## 2026-08-28 — Plan 024 (corpus exports and the data surface)

The corpus is now a citable dataset. `vitrine export` runs the full
provenance gate first, then writes a standalone archive-wing surface:
`data.html` plus `data/corpus.json` (schema version 1), `data/facts.csv`,
and `data/facts-raw.csv`. The JSON export is the canonical machine record —
rooms and metadata, every authored fact with all structured fields, the
source register, the assumption ledger, and the complete series with their
annual observations, so an `INFLATE` derivation is reproducible from the
export alone; derived facts keep the authored derivation structure next to
the computed result and the weakest-operand tier. The CSVs are deliberately
narrower: quantified authored facts only, with `facts.csv` apostrophe-
prefixing formula-like text so spreadsheets cannot reinterpret a value and
`facts-raw.csv` preserving machine values exactly. The exports are
projections of the gated corpus, never a second source of truth, and the
IPUMS posture is unchanged: aggregates and citations only — no raw source
material leaves the archive. The composite-family disclaimer renders on the
data surface too.

Both `vitrine build` and `vitrine export` now publish through staged
same-filesystem swaps (`publish.py`): builders render into a sibling
staging directory and the destination is never written file-by-file, so a
render failure leaves the previous tree untouched and a successful handoff
publishes one coherent build. Rollback and cleanup failures have explicitly
documented partial states, and recovery fails closed — a destination plus a
rollback artifact, or several artifacts, is an error rather than a guess.
Advisory locks serialize cooperating local writers per logical output root
(a nested data surface reuses the full site's lock); path overlap with the
corpus and symlinked destinations or trees are rejected.

Landing this surfaced a real display bug: `INFLATE` and `AMOUNT_PRODUCT`
divided minor units by a hardcoded `100` on their way to a display string,
which would have made a yen result a hundredth of its true amount.
`ComputedFact` now carries `numeric_value`, `amount_minor`, and
`currency`, and money display scales through the currency registry's minor
digits (mirroring the plan-023 fix in `series_numeric`). `CITATION.cff`
lands with the corpus citation — CC BY-SA 4.0 for corpus and site, MIT for
the software — scoped by a contract test against the dual `LICENSE`.

## 2026-08-21 — WI-023 remaining item a (PDF expect-marker verification)

The link checker could verify markers in HTML and .xlsx bodies but had to
trust PDFs on status code alone — most of the corpus's primary documents
are PDFs. Content streams are now inflated (`zlib`) and the strings shown
by the text operators (`Tj`, `TJ`, `'`, `"`) become searchable text, so a
200 that serves the wrong PDF fails the way the f08a/f08ar incident taught
us to fail. Encrypted PDFs, image-only scans and subset-font encodings
stay honestly opaque.

The extraction is a linear character scanner rather than a regex, and that
choice is load-bearing: a backtracking pattern over embedded font binaries
had catastrophic runtime and hung indefinitely on a real 1950 Census PDF
(hc-5-02). Streams over 2 MB, streams without a show operator, and
fragments too short to be page text are skipped or treated as opaque —
every shortcut demotes toward resolve-only, never toward a false
mismatch. Three sources gained verified `expect` markers (ramey-2009,
goldsmith-balance-sheet against `samples/` archive copies;
seer-csr-1975-2017 against the live document); the other eight cited PDFs
are scans or cipher-encoded and remain resolve-only by design. Live run:
95 URLs, content-verified 6 → 9, 0 must-fix. `scripts/link_check.py` is
now inside strict mypy (it runs as its own CI job and has a test suite);
the one-off extract scripts are not held to strict yet.

## 2026-08-14 — Plan 023 WI-3 (cross-currency non-comparison gate)

Un-deferred: the guard was waiting "until a second currency's data exists" —
the UK (£) and Japan (¥) rooms are in the corpus, so it is now mechanical.
`Series` gains a `currency` field, required iff `values_minor` and forbidden
on dimensionless series; `vitrine check` rejects an unregistered series
currency, a `splices_from` chain across currencies (an exchange rate laundered
in through the back door), and an `INFLATE` derivation pointed at a monetary
series (the ratio must be an index, not an amount). `series_numeric` scales
minor units by the registry's per-currency digits — the hardcoded `/100`
would have divided a yen series by a hundred. Room-level currency mixing and
`ratio`/`pct_of` operand mixing were already gated by the multi-currency
foundation; this closes the series-layer remainder. Fact-model invariant 11.

## 2026-07-29 — Plan 016 (the docent layer, WI-1–4)

The museum gets a voice, within one constraint: the docent may interpret but
may not quote from memory. Essays are data (`data/essays/*.toml`): prose
blocks whose every number is a `{fact:<id>}` binding interpolated at build
into a deep-linked tier chip, and chart blocks that reuse the corridor
builders verbatim. After stripping bindings, the numeral gate
(`check_essays`, part of `vitrine check`) fails the build on any remaining
numeric token except years and decade words — the failure mode the project
was built around (hand-authored numbers in prose) is closed *mechanically*,
not socially. Unknown fact ids and unknown chart slugs fail too — the latter
at build time, since core may not import the site's registries.

Shipped surfaces: a `Tours` section (`essays/` + nav) with one page per tour
(disclaimer strip, per-chart caveats, rooms-cited footer), computed
room↔tour backlinks, tours listed on the lobby, and two essays written from
the placards: **"One paycheck"** (single-earner-wage-coverage metric + the
1950/2024 income, wage and LFPR exhibits, with the manufacturing-wage-proxy
caveat stated in prose) and **"The work that moved"** (the home-production
flat-then-cliff arc, the appliance arrival, and the ATUS/Ramey concept
splice rendered as the honest stop it is). WI-5 ("How death changed") is
unblocked and pending an editorial pass.

Tests: `tests/test_essays.py` covers the gate's failure modes token by
token, interpolation rendering, deck/mark coverage, and room backlinks —
plus a DOM-level assertion that rendered docent cards carry no digit outside
a chip or an allowed year form.

## 2026-07-29 — Plan 020 (the statistical atlas)

A presentation redesign with a single question: what does the data itself
want to look like? Answer: the document class the museum cites — statistical
annuals and census atlases. The dark night-gallery becomes a light folio:
paper surfaces, hairline rules, tabular numerals, hue reserved for
epistemology. Three structural moves, all projection/template-layer:

- **Provenance in the scan-line.** Room panels are now ledgers of fact rows:
  value, tier chip, measured population, and source record (publisher ·
  year · tier) on every line without a click. The full drawer is one
  disclosure; the overlay record card keeps its `--modal` deep links, its
  `:target` CSS fallback, and its JS state machine unchanged (the entire
  35-test browser battery pins the new DOM without a single edit).
- **The index is the record at a glance.** A corpus matrix — 13 rooms × the
  six cases — leads the landing page: exhibit counts (`N` sourced `+M`
  computed), tier-mix slivers, and ember gap counts. Every number is build
  metadata folded from the corpus in the projection layer; a test proves the
  matrix equals the corpus's own per-room/panel counts.
- **Gaps are structural everywhere.** The gap vocabulary (dashed, warm grey,
  ember counts) now runs consistently through rows, chart slots, stage
  rings, and matrix cells.

No change to the fact model, loader, `check` gate, derivation engine,
curation registries, SVG geometry, or any datum. The fact-mark hashes,
overlay decks, corridor/pair/walkthrough/affordability structures, and both
coverage gates are byte-identical to the pre-redesign build — the redesign
is confined to tokens, one stylesheet, templates, the lobby projection,
and their contract tests. New design-test disciplines: white chip letters
≥ 4.5:1 on every chip, composition segments ≥ 4.5:1 against their mandatory
white labels, body ink ≥ 7:1 on every sheet and era wash.

Tests: 213 (was 210). ruff + mypy --strict clean. `vitrine check` and
`check --against-build` green; cross-check 0 hard errors.

See `plans/020-the-statistical-atlas.md` for the rationale and acceptance
criteria and `docs/design-spec.md` for the validated palette.

## 2026-07-14 — Plan 022 WI-1/WI-2 (the multi-currency foundation)

The money layer the world wing (plan 021) stands on. New `vitrine.money`: a
closed currency registry (USD, GBP seeded) with per-currency formatting and an
`UnknownCurrency` guard. `vitrine check` now rejects a priced fact whose
`currency` isn't registered. Derivation threads the operand's currency through
`_op_value`, so `INFLATE`/`PRODUCT` render in the fact's own currency
(closing WI-021: the hardcoded `$` is gone) — a GBP derived fact renders `£`,
not `$`. No FX anywhere: the museum never converts between currencies as a
truth-path number.

**Foundation-only invariant held:** the entire US corpus rebuilds
**byte-identical** (108 files, identical checksums) — USD formatting is
provably unchanged. 220 tests pass (10 new), mypy --strict + ruff clean.

WI-3 (site-layer money-formatting audit + cross-currency non-comparison gate)
is deferred to plan 023: the render path was already clean — it renders
authored `value` and derived `value`, never re-formatting money — so there is
nothing to reroute until a second currency's data exists to guard against.

*(Adopted onto the atlas line 2026-08-14 from `plan-022-multi-currency`
79e34fe, alongside JPY in the registry — the Japan rooms price facts in
`JPY`, whose minor unit is the yen itself, so amounts carry no decimals.)*

## 2026-07-13 — Plan 019 (presentation architecture recovery)

A controlled recovery of the museum UI onto a maintainable presentation
architecture. Plan 018 split the presentation code off the pre-museum-UI
baseline; Plan 019 transplants that split onto the content-complete `9953a0e`
baseline (the museum lobby, atlas-wing corridors, room opening routes,
visitor navigation, evidence-first placards, and walkthrough that Plan 018
had omitted) without losing a single rendered byte.

**What landed (six work packages, all byte-identical except one intentional
asset fix):**

- **WP0/WP1** — recovery baseline + ancestry gate; `curation.py` (1096 lines)
  split into the `site/curation/` package (`models`, `corridors`, `rooms`,
  `affordability`, `walkthrough`, re-exporting `__init__`).
- **WP2** — ten inline Jinja template strings extracted from `render.py` into
  `templates/*.html`; `environment.py` centralizes the `PackageLoader` +
  globals. `render.py` 1732→1170 lines.
- **WP3+WP4** — `render.py` (1170 lines) split into `context.py` (8 typed
  page contexts + 14 intermediate view types, all `frozen=True, slots=True`),
  `projections/*.py` (11 surface modules, one `project_*` per page), and
  `build.py` (188 lines, orchestration only). All 9 templates rewritten to
  receive a single typed `page` object. `render.py` reduced to a 107-line
  compatibility re-export.
- **WP5** — `placard` macro split into `placard_card` + `placard_overlay`;
  35-test Playwright browser suite covering the enhanced / no-JS / responsive
  matrix; wired Playwright into CI on both Python versions. Surfaced and
  fixed a real `:target` dismissal bug in `enhancements.js`
  (`pushState("#dismissed")` did not recalculate CSS `:target`; replaced with
  a real fragment navigation). This is the only byte difference from the
  baseline.
- **WP6** — adversarial review (no critical/major defects), follow-up fixes
  (dead macro parameter, ruff `build/` exclusion, test-count drift,
  post-dismissal Forward coverage), and this report.

**Size budgets met:** `build.py` 191 ≤ 250; `render.py` 107 ≤ 120; largest
projection module 231 < 600. **Wheel verification:** an installed wheel
builds the site byte-identically from outside the repository. **Tests:**
197 (162 existing + 35 browser). ruff + mypy --strict clean across 35 files.
Ancestry gate PASS (`9953a0e` is an ancestor of HEAD). Contracts unchanged.

See `plans/019-recovery-log-output.md` for the per-work-package landing notes and
`plans/019-ui-recovery-and-presentation-architecture.md` for the full plan.

## 2026-07-08 — Plan 007 (the visualization layer)

The production renderer replaces the V0 schematic with three static surfaces
on the concept demo's design language: rooms (dark-gallery house cutaway,
era-graded stage light, ivory `:target` specimen placards), corridors (17
cross-decade arc charts, affordability-in-hours, budget composition, and the
78-page measure-guard-filtered pairwise set), and the walkthrough (the
1900s→1950s→2020s transect with the labour-hours meter and true-scale house).
One progressive-enhancement asset; every interactive affordance still works
with scripts disabled.

Model change: facts gained an optional structured `quantity` — the one number
a chart mark may project — gate-enforced to appear verbatim in the display
value. 118 quantities added across all 13 rooms; multi-number ranges got none
and render as gaps. New gate: **mark coverage** — the built HTML is scanned
for `data-fact-id` and any mark that doesn't resolve to a curated fact is a
red build (`vitrine check --against-build`). Design tokens + validated
palette recorded in `docs/design-spec.md`, executable in
`src/vitrine/site/tokens.py`, with a contrast test over every era light tint
(it caught `ink-soft` at 2.7:1 on the glow tints during development). 89
tests; ruff/mypy/check/build all green.

## 2026-07-08 — Plan 008 Phase 1-2 (verification and gap filling)

### Corrections (4 facts fixed)

1. **`us-1920s-home-production-components`** (WI-1): Value had 1965 AHTUS column values instead of 1920s Wilson Study values. Fixed: food prep 16.5→19.9, house cleaning 9.5→9.3, clothing care 6.9→11.5, childcare 8.5→7.2, purchasing 4.4 (was 10.4). Total 51.8→52.4. Notes updated with explicit 1965 comparison values.

2. **`us-1970s-food-prices`** (WI-4): Round steak 134¢→133¢ (table value 133.3, rounds to 133 not 134). Milk 66.5¢→65.5¢ (off by 1¢). Notes updated: round steak +27%→+26%, milk +156%→+152%.

3. **`us-1980s-cable-tv`** (WI-6): "53 million households (≈57%)" → "More than 52 million cable customers (50.5% penetration, 1988)". NCTA source says "more than 52 million" and "50.5 percent," not 53M/57%. Label changed from "Cable TV, 1989" to "Cable TV, 1988-1989" to reflect mixed-year data.

4. **`us-1970s-vehicle-ownership`** (WI-6): Income breakdown in notes corrected. Under $3,000: 47.3%→38.3% (was row-confusion error). $15,000+: 94.3%→~96.6% (composite of three top income brackets). Source reference corrected from "Table 1, p.31" to "Bulletin 1992, Table 1, p.31".

### Notes updates (3 facts)

5. **`us-1990s-cable-tv`** (WI-6): Notes updated to acknowledge that the 60% penetration figure for 1992 could not be directly verified against the NCTA Cable History Timeline PDF. The figure is consistent with the trend but is not stated in the cited primary source.

6. **`us-1970s-infant-mortality`** (WI-7, adversarial review fix): Decline percentage corrected from 35% to 37% (actual: (20.0-12.6)/20.0 = 37%).

7. **Source registry `ncts-nvss`**: Notes updated to include infant mortality data from Health, United States, 2016, Table 11, with URL.

8. **Source registry `ncta-cable-history`**: Notes corrected. "1989: 53M" → "1989: more than 52M, 9,050 systems". "1997: 66.7M" → "1999: 66.7M". Added "1992: ~60% (not directly stated in NCTA timeline)".

### New facts (7 added)

9. **Infant mortality arc** (WI-7): Added `us-{1950s,1960s,1970s,1980s,1990s,2000s,2010s}-infant-mortality` facts. Source: nchs-nvss, Tier A. Values from NCHS Health, United States, 2016, Table 11. Completes the infant mortality arc from ~100 (1900s) through 5.6 (2020s).

### Verification summary

- **WI-1** (Ramey): 27 of 28 verified, 1 corrected (1920s components column swap)
- **WI-2** (Heating fuel): All 7 verified against Census/RECS/EIA sources
- **WI-3** (AC diffusion): 6 of 7 verified, 1 unable to verify (1978 RECS not accessible)
- **WI-4** (Food prices): All 5 items for 1960s verified, 2 of 5 for 1970s corrected
- **WI-5** (CEX shares): All 10 verified, 0 corrected
- **WI-6** (Cable/vehicle): 3 of 6 verified, 2 corrected, 1 unable to verify
- **WI-7** (Infant mortality): All 7 new facts verified against NCHS Table 11
- **WI-9** (1950s car price): Upgraded from Tier D to Tier C. Found primary-source wholesale value in Statistical Abstract 1953, Table 615: 6.666M passenger cars at $8.633B wholesale = ~$1,295/car. Source changed from umizzou-prices-wages to statab-food-prices. Zero Tier D estimates remain in the corpus.

Total: 278 facts (271 existing + 7 new), 56 sources, 2 derived. Build gate, tests, ruff, mypy all pass.

### MANIFEST.md note

`samples/10-recs/file2_asc.txt` through `file12_asc.txt` are RECS **1993** microdata (7,111 sample), not RECS 2001 as labeled. The sample size matches the RECS 1993 survey, not RECS 2001 (4,822 households).
