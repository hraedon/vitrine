# Plan 027 — The past was a different country

**Status:** WI-1 through WI-6 implemented and verified; WI-7 through WI-12 remain open (reconciled 2026-09-07)
**Triggered by:** owner request for a more evocative retrospective wing — the
class of fact where ordinary, legal, ubiquitous behaviour of the recent past is
now unthinkable (you could smoke on a domestic flight in 1985; a child's blood
lead that was *median* in 1978 would trigger intervention today). The US corpus
already carries lived-texture facts in the `day` panel (infant mortality,
married-women LFPR, age at first marriage); this plan gathers a deliberate set
of them into a themed corridor wing with the arcs and series to back it.

**Numbering note.** This is a Pillar II exhibit (Plan 021 — "curated epoch
comparisons / chosen confrontations that carry meaning"), a *sibling* of the
budget-basket cutaway that Plan 021 penciled in as 024, not a replacement for
it. It is buildable on the US corpus alone and does **not** depend on Plan 023
(the UK) — so it can run in parallel with the world wing. Numbered 027 to avoid
colliding with 021's reserved 023–026 slots; renumber freely if you'd rather it
sit earlier in the queue.

## The idea

The US wing measures the median family's *material* life — what it earned, what
it owned, what a car cost in hours of work. This wing measures the median
family's *behavioural and environmental* life, and it does so to make one point
that the affordability corridors cannot: **the recent past was morally and
physically a different country.** Not poorer — different. The father smoked in
the hospital waiting room while the mother was in labour; the children rode
unbelted in a car with leaded exhaust; a fourteen-year-old down the street had a
full-time job and nobody thought it remarkable.

### The selection principle (the thing that keeps this from being a morality play)

A fact earns a place in this wing only if it was, in its time, **normal, legal,
and ubiquitous**, and is now **unthinkable, illegal, or vanishingly rare**. That
is a stricter and more interesting test than "things got better":

- Infant mortality *falling* is expected progress and already lives in the
  general corridors. It does **not** belong here.
- Smoking permitted in a *maternity ward* is a different moral universe. It
  belongs here.

The distinction is the whole editorial spine. It keeps the wing from becoming a
Whig-history "look how far we've come" victory lap, and it admits facts that cut
*against* progress-as-direction (the teen-birthrate peak is the golden-age
1950s, not the "backward" past). The curatorial voice stays flat: these facts
are shocking **unadorned**. No adjectives on the cards. The evocation lives in
the wing's title and arrangement — fields the curation registry already provides
(`CorridorWing.title` / `.question` / `.introduction`) — never in a fact
`value` or `notes`. The permanent no-narration-in-the-truth-path rule holds.

### Why it fits the machine as-is

Nothing here needs a model change:

- Continuous annual measures (cigarettes per capita, ethanol per capita,
  vehicle-death rate) become `Series` in `data/series/`, exactly like CPI.
- Decade checkpoints (child-labour share, blood-lead median, a 1955 household's
  food-use rates) become `day`/`diffusion` facts in the rooms.
- Each measure becomes an `Arc` in `curation/corridors.py`, most with
  `falling=True` (copper), backed by its series where one exists.
- The set is placed in one new `CorridorWing`. The existing
  registry-consistency gate — *every rendered arc lives in exactly one wing* —
  means an arc and its wing placement land in the same work item, or the build
  reddens. That gate is a feature here: it makes "I added a chart but forgot to
  file it" impossible.

## Design decisions

### D1 — Rising *and* falling arcs share the wing, on purpose

Most measures fall (smoking, vehicle deaths, workplace deaths, blood lead, child
labour) and render copper via `falling=True`. Two do not: **diet variety rises**
(more commodities cross the "actually eaten" threshold each decade) and the
**teen birthrate is non-monotonic** (rises to a 1957 peak, then falls). Keeping
both directions in one wing is deliberate — a wing where every line falls *is* a
progress narrative. The mixed shape enforces the selection principle visually.

### D2 — Gaps that are themselves the exhibit

Three measures have honest gaps that carry more meaning than any number would:

- **Alcohol across Prohibition (1920–1933).** The NIAAA per-capita ethanol
  surveillance series is built from legal sales; during Prohibition legal sales
  collapse and the series with them. Render the gap. Do **not** backfill with
  Warburton-style consumption estimates unless they are entered as a separate,
  clearly-tiered (C/D) fact with the methodology on the card. The gap says
  "the state stopped being able to measure this" — which is the point.
- **Child labour, after it ends.** The decennial share of 10–15-year-olds in the
  labour force runs high early-century and then the series *ends* because the
  measured thing ended (Fair Labor Standards Act, 1938). A terminating series is
  the honest display of an abolished practice.
- **Vehicle deaths in the 1900s.** Cars barely existed; there is no rate.
  `plot_gaps` (or simple absence) renders the early gap rather than a
  manufactured zero.

`falling=True` + honest gaps are both already supported by the `Arc` dataclass
(`falling`, `caveats`, `plot_gaps`). No new mechanism.

### D3 — Tier honestly; the famous-headline numbers are the dangerous ones

The recurring finding across Plans 006/015/020 is that obscure table cells
transcribe clean and *famous* numbers arrive wearing a fake citation. This wing
is *made of* famous numbers. Discipline is non-negotiable:

- Every value transcribed from the **primary table**, not from the chart
  everyone reprints (the 1964 Surgeon General smoking curve, the "1 in 5 kids
  worked" statistic, the leaded-gas decline — all have canonical
  reproductions that are one citation removed from the source).
- The specific figures floated in the triggering discussion — ~100→400 produce
  SKUs, teen birthrate ~96/1,000 at the 1957 peak, workplace deaths ~61→~3.5 per
  100k, vehicle deaths ~24→~1.2 per 100M VMT, child blood lead ~15→~3.5 µg/dL —
  are **leads to verify, not data to enter.** They came from web search and
  model recall. Nothing is committed until it is read off the cited source and
  logged (Plan 008 verification-log convention; `/ocr` for scanned tables).
- Trade-survey and estimate-based measures are **Tier B or lower**, disclosed:
  the produce-SKU count is a Progressive Grocer / FMI trade survey relayed
  through USDA publications (B); the pre-registration NSC workplace and vehicle
  fatality figures are *estimates*, not registrations (B, with an assumption-
  ledger entry naming the estimation basis).

### D4 — Name series nation-scoped now, so the wing goes comparative for free

Every measure here has a UK analogue (smoking prevalence, drink-driving deaths,
leaded-petrol phase-out to 2000, per-capita alcohol). When Plan 023 lands the
UK, this wing should become a cross-nation confrontation with no refactor. So
follow the existing `us-`-prefixed convention strictly for both series ids and
fact ids, and keep each `Arc.fact_ids` map US-only for now. The arc/series
machinery already keys on the id; a future `uk-` sibling series drops in beside
it. (No cross-currency or FX concern arises — none of these measures is
monetary except the produce-SKU *count*, which is dimensionless.)

### D5 — Qualitative regulatory-moment facts are first-class, and Tier A

The most visceral items are not rates but *permissions*: smoking was legal on US
domestic flights until the 1988 (short-haul) / 1990 (all-domestic) bans, in most
hospitals into the early 1990s, in restaurants nationwide for a decade after.
These have no `quantity`; they are compound `value` strings — precedent:
`us-1980s-food-prices` already carries a multi-item string value. Their sources
are *better* than most statistics: public laws and Federal Register / DOT
rulemakings are primary sources par excellence, so a well-cited permission fact
is **Tier A**. They live in the `day` panel of the decade the permission ended.

## Work items

Phased so the pattern is proven on the flagship before the long transcription
tail. Each WI is independently green (tests + `vitrine check` +
`--against-build` + mypy --strict + ruff) and leaves prior rooms' existing
output unchanged.

### Phase A — the wing skeleton and the flagship

#### WI-1: The "different country" corridor wing

Add one `CorridorWing` in `curation/corridors.py` (title, question,
introduction, `arc_slugs`) and register it in `CORRIDOR_WINGS`. It starts
holding only the WI-2 arc(s); every later WI appends its arc slug here in the
same commit that adds the arc, satisfying the one-arc-one-wing gate. The
introduction states the selection principle (D1) in the museum's voice.

**Acceptance:** the corridors index renders a fifth wing; the registry-
consistency gate passes (no arc unplaced, no arc double-placed); a test asserts
the new wing's `arc_slugs` are all resolvable arcs.

#### WI-2: Smoking — the flagship (series + prevalence + arc)

- **Series** `us-cigarettes-per-capita` — annual per-capita cigarette
  consumption, adults 18+, ~1900–present. Source: USDA/ERS tobacco series as
  reproduced in the CDC century-retrospective MMWR (transcribe the table, per
  D3), with the 1964 Surgeon General report as a cross-check, not the source.
- **Series** `us-smoking-prevalence` — % of adults who smoke, NHIS, 1965→
  present (the survey starts 1965; earlier decades render as gap on this arc).
- **Arc(s)** placed in the WI-1 wing, `falling=True`.
- A `day` fact per room for the decade checkpoints so the room placards link.

**Acceptance:** both series pass the series gate (source resolves, values
non-empty, keys parse); the arc renders full-coverage for consumption and
gapped-before-1965 for prevalence; verification-log entries for every
transcribed value; the pre-1965 prevalence gap renders as a gap, not a zero.

### Phase B — the mortal-risk cluster

#### WI-3: Alcohol per capita, with the Prohibition gap (D2)

- **Series** `us-ethanol-per-capita` — gallons of pure ethanol per capita 14+,
  NIAAA Surveillance Report series (reaches back to the 19th c.). Render the
  1920–1933 gap; do not backfill.
- Arc in the wing, `falling` left `False` (the modern trend is roughly flat/
  declining but the story is the Prohibition discontinuity, not a monotone).

**Acceptance:** the Prohibition years render as an explicit gap with a caveat
naming why; a test asserts no value is present for 1920–1933; any estimate fact
for those years (if the owner chooses to add one) is Tier C/D with a methodology
card.

#### WI-4: The two death-rates — road and workplace

Two separate arcs (different exposure denominators, so **not** an ArcGroup —
they cannot share an axis honestly):

- **Series** `us-traffic-death-rate` — deaths per 100 million vehicle-miles
  travelled, FHWA/NHTSA (FARS from 1975; NSC estimates before). ~1921→present.
- **Series** `us-workplace-death-rate` — occupational fatalities per 100,000
  workers, NSC estimates (1913→1992) spliced to BLS CFOI (1992→present). This
  one ties directly to the family portrait: it is the *breadwinner's daily
  risk*, not an abstract public-health stat.
- Assumption-ledger entry `nsc-fatality-estimate` (D3): the pre-CFOI /
  pre-FARS figures are estimates, population and method disclosed. The existing
  splice-caveat mechanism (`splices_from`) marks the estimate→registration
  boundary.

**Acceptance:** both arcs `falling=True`/copper; the splice markers render at the
estimate→registration year with a placard explaining the method change; the
1900s road-death gap renders (cars barely existed); Tier B on the estimate
segments, A on the registered segments.

#### WI-5: Teen birthrate — the mid-century-peak twist (D1)

- **Series** `us-teen-birth-rate` — births per 1,000 women 15–19, NCHS, 1940→
  present. Non-monotonic: the peak is ~1957, and the placard notes that most
  1950s teen mothers were *married* — which is what makes it "different country"
  rather than "social decline."

**Acceptance:** the arc renders the mid-century peak (not forced monotone
`falling`); the married-vs-unmarried context rides in the arc caveat and the
decade placards, sourced, never as unsourced narration.

### Phase C — the diet-variety exhibit

#### WI-6: Diet variety (FADS arcs + produce-SKU count + a 1955 checkpoint)

The richest sub-exhibit; three complementary apparatuses (see the sources note
below), each carded for what it actually measures:

- **FADS commodity arcs** — from the USDA/ERS Food Availability (Per Capita)
  Data System, continuous from 1909, per-commodity spreadsheets. Pick a handful
  of "exotic-turned-ordinary" commodities (broccoli, avocados, fresh grapes,
  bell peppers) as individual series `us-availability-<commodity>`, and render
  them as an **ArcGroup** on one shared lb-per-capita axis — the visual of
  near-zero-then-liftoff is the exhibit. Tier A (federal food-supply
  disappearance series); the card discloses it measures *availability*, not
  intake. 1900s renders as a partial gap (series starts 1909).
- **A derived "variety" fact** (Plan 006 machinery): count of fresh
  fruit/vegetable commodities above a stated lb-per-capita threshold, per
  decade — a derived count over Tier A inputs under a documented rule.
- **Produce-SKU count** — the headline confrontation number: ~100 items in a
  1980 produce aisle → ~400 by 1997 (Progressive Grocer / FMI trade survey via
  ERS AIB-758 / AER-825). **Tier B**, trade-survey basis disclosed. `day`/
  `diffusion` facts in the 1980s/1990s rooms.
- **A 1955 household-use checkpoint** — from the 1955 USDA Household Food
  Consumption Survey: the fraction of households serving a given item in a
  week. The human-scale version of "variety" ("almost no household served
  broccoli in a given week in 1955"). A `day` fact in the 1950s room.

**Acceptance:** the FADS ArcGroup renders liftoff on a shared honest axis with
each commodity's card naming availability-not-intake; the derived variety-count
fact passes the derivation gate and names its rule; the SKU count is Tier B with
its survey basis on the card; the 1955 checkpoint cites the survey volume/table;
every transcribed value logged.

### Phase D — the tail (checkpoint facts, no series)

#### WI-7: Lead exposure (decade `day` facts, not a series)

Blood-lead is a checkpoint measure (NHANES median child blood lead begins
1976–80), too sparse for a corridor arc. Enter as `day` facts from the 1970s
room onward: the 1976–80 median (~mid-teens µg/dL — *verify*) against today's
much lower level and the current intervention threshold. Optionally one
`diffusion`-style fact on leaded-gasoline phase-out (Clean Air Act schedule,
final 1996) as the environmental mechanism.

**Acceptance:** Tier A (NHANES); values verified off the NHANES tables, not
recalled; rendered as room facts, not forced into an arc; the leaded-gas
phase-out fact cites the regulatory schedule.

#### WI-8: Child labour (decennial series + terminating gap, D2)

- **Series** `us-child-labor-share` — % of 10–15-year-olds in the labour force,
  decennial census, ~1900 (~high-teens %, *verify*) declining to near-zero and
  **ending** post-FLSA (1938). Sparse decennial values, terminating series.
- Arc in the wing, `falling=True`; the terminating series *is* the exhibit.

**Acceptance:** the arc renders the decline and then the honest end (no
manufactured post-1940 zeros beyond what the census reports); Tier A (decennial
census); the FLSA context in the caveat, sourced.

#### WI-9: The regulatory-moment permission facts (D5)

Compound-string `day` facts, one per permission that ended, in the decade it
ended: smoking on US domestic flights (1988/1990/2000 phase-out), in hospitals
(early 1990s), in restaurants/workplaces (state-by-state, cite representative
statutes). Sourced to public law / Federal Register / DOT rulemaking → Tier A.

**Acceptance:** each fact's `value` string states the permission and its end;
each `source` resolves to a primary legal citation in the registry; Tier A;
`vitrine check` clean (no `quantity` required for a string-value fact, per the
existing food-prices precedent).

#### WI-10: The vanishing reference desk — how you got an answer before the web

The evocative "information availability" comparison, rendered *rigorously* by
refusing to invent a number for it. "Information availability" is a lived
condition, not a measured quantity; a composite "information-access index" would
be a synthesized figure the data does not support — exactly the class of number
the museum refuses. Instead this WI renders a **constellation of narrow proxies,
each carding precisely what it measures**, arranged so the *crossover* is the
exhibit. The distinction from the corpus's existing `internet` diffusion arc is
the whole point: that arc measures the **new conduit arriving** (an adoption
S-curve, reads as neutral progress); this WI measures the **old behaviour
dying** — which is what passes the D1 selection principle.

- **Series** `us-library-reference-transactions-per-capita` — the flagship
  proxy, and almost exactly the owner's scenario made countable: a "reference
  transaction" *is* a person going to ask a librarian a question they could not
  answer themselves. IMLS Public Libraries Survey, annual, Tier A, ~1988/1990→
  present, with a clean peak-and-collapse as the web arrived. It is *obscure*
  (not a famous headline chart), so it transcribes clean — the inverse of the
  D3 famous-number risk. `falling=True` from its peak.
- **Series** `us-first-class-mail-per-capita` — USPS Revenue, Pieces & Weight
  reports, Tier A, peaks ~2001 then falls: the death of the personal letter, the
  "you had to know someone and write to them" channel quantified.
- **Series** `us-newspaper-circulation-per-capita` — daily circulation per
  capita (News Media Alliance / Pew); **Tier B** (industry association,
  disclosed). The distribution side.
- **Reuse** the existing `internet` arc as the rising counter-line; do **not**
  duplicate it. The exhibit is the *scissors*: reference transactions (or mail)
  falling in copper as internet-at-home rises, on adjacent panels.
- **A D5-style institutional-death fact**, not a sales series: Encyclopædia
  Britannica ceased its print edition in 2012 (cite Britannica's own
  announcement / the news of record). A compound-string `day` fact in the 2010s
  room — the encyclopedia set in the living room, ended on a date. Chasing
  proprietary encyclopedia *sales* figures is out (unsourceable); the datable
  cessation is Tier A as a cited event.

Coverage discipline (the honest limits, on every card): these series begin only
where the federal/industry record begins (~1988–2001) — there is **no** number
for "how a 1930 family got an answer," so the pre-series decades render as gap,
not zero. This is a *change-within-living-memory* arc by nature, and that is the
point, not a defect. Definitional revisions (IMLS in-person vs. virtual
reference; mail-class changes) get the `splices_from` marker and a caveat, same
discipline as WI-4. And each card names the **behaviour** it counts
("reference transactions per capita"), never "information availability" — the
evocation lives in the wing framing, never in a fact.

**Acceptance:** the reference-transaction and mail arcs render `falling`/copper
with their peaks; the internet arc is reused (grep proves no second internet
series/arc is added); the pre-series decades render as explicit gaps, not zeros;
splice markers render at each definitional break with an explaining placard;
the Britannica-2012 fact is a cited Tier A string-value `day` fact; Tier B on
newspaper circulation is disclosed on its card; every transcribed value logged.

#### WI-11: The death of the repair-and-keep household

The D1-passing appliance exhibit — and a deliberate *reframe* away from the two
angles that don't earn a place. Appliance **efficiency** (the refrigerator's
energy collapse) is a things-got-better story, not a different-country one, so it
rides here only as a subordinate support thread, never the headline. The
**K-shaped quality thesis** (the durable middle hollowing into cheap-disposable
vs. premium-expensive) is emotionally real but **not in the public record as a
series** — there is no primary source for within-category price/quality
dispersion over time; the only thing close is proprietary retail scanner data
(recent, un-sourceable, and still wouldn't cleanly show the hollowing). So this
WI does *not* assert it. What it renders is the **death of the repair-and-keep
household**: repairing a broken appliance was ordinary household competence
backed by a whole category of local business, and now you bin the thing. That
passes D1 and structurally rhymes with WI-10 — another vanished household skill,
another vanished class of neighbourhood shop.

- **Series** `us-major-appliance-price-real` — BLS CPI for major appliances, one
  of the great real-terms *deflation* categories (like TVs): roughly flat
  nominal while the cost of living doubled, so sharply falling in real terms.
  Run through the affordability machinery → **hours of work per refrigerator**,
  collapsing across the century. This is the *mechanism* of disposability: when
  a new one is cheap, you don't repair the old one. Tier A (BLS).
- **Series** `us-appliance-repair-establishments` — count (or employment) of
  appliance-repair businesses, Census County Business Patterns (NAICS 811412;
  SIC codes before the 1997/98 NAICS switch — a `splices_from` marker at the
  changeover, per the WI-4 discipline). The repair shop as a vanishing local
  business, the direct parallel to the vanishing reference desk. Tier B.
- **The repair-vs-replace scissors** — the falling appliance-price arc against a
  *rising* repair-labour-cost arc (CPI/PPI repair services). The crossover is
  the exhibit and the explanation of why the fix-it culture died; each series is
  carded separately, and the "scissors" is presented as two sourced lines, not a
  single manufactured ratio.
- **Efficiency, as the subordinate transformation thread** — the refrigerator's
  ~1,700→~390 kWh/yr fall (AHAM data via LBNL/ASAP — the famous "refrigerator
  graph": energy down, box up, real price down) and the DOE minimum-efficiency
  standards (SEER/HSPF, refrigerator NAECA) as datable Tier A regulatory facts
  (CFR / Federal Register). Placed and labelled as support so the exhibit does
  not curdle into a progress narrative.
- **The hollow-middle rendered as a known-unknown** — an explicit placard: here
  are the measurable mechanisms; the bimodal cheap-vs-premium quality claim is
  *not* in the public record as a series, and the museum will not manufacture
  one. This refusal is the exhibit's signature — the discipline on display, not
  a hole apologised for.

**Acceptance:** the real-price arc renders the decline / hours-per-fridge, Tier
A; the repair-establishment arc renders the collapse with the SIC→NAICS splice
marked and Tier B disclosed on its card; the efficiency material renders as a
labelled *support* thread subordinate to the repair-culture spine (its placement
proves it is not the headline); the hollow-middle placard renders as an explicit
known-unknown, and a grep/test proves no price-dispersion or K-shape figure is
entered as a fact; every transcribed value logged.

#### WI-12: Wing polish, docent route, gate, and tests

- A walkthrough/docent route (Plan 009/016 machinery) through the wing that
  states the selection principle and lets a visitor walk the confrontations.
- Full test pass: series-gate coverage for every new series; arc mark-coverage
  (gaps render, don't crash); wing registry-consistency; string-value facts
  pass; derived variety-count agrees with its inputs.
- Verification-log completeness check: every transcribed value has an entry.
- `--against-build`: rooms and corridors that existed before this plan render
  byte-identical except for the intended new arcs/facts/wing.

## Sourcing note (leads, to be verified at execution — D3)

| Measure | Candidate primary source | Tier |
|---|---|---|
| Cigarettes per capita | USDA/ERS tobacco series via CDC MMWR century-retrospective; 1964 Surgeon General report as cross-check | A |
| Smoking prevalence (1965→) | NHIS (National Health Interview Survey) | A |
| Ethanol per capita | NIAAA Surveillance Report per-capita ethanol series (19th c.→) | A |
| Traffic death rate | FHWA/NHTSA FARS (1975→) + NSC estimates before | A / B |
| Workplace death rate | BLS CFOI (1992→) spliced to NSC estimates (1913→) | A / B |
| Teen birthrate | NCHS natality (1940→) | A |
| Diet variety (commodities) | USDA/ERS Food Availability (Per Capita) Data System (1909→) | A |
| Produce-aisle SKU count | Progressive Grocer / FMI trade survey via ERS AIB-758, AER-825 | B |
| 1955 household food use | USDA 1955 Household Food Consumption Survey | A |
| Blood lead (child, median) | NHANES (1976–80→) | A |
| Child-labour share | Decennial census, labour force 10–15 | A |
| Smoking-ban permissions | Public Law / Federal Register / DOT rulemaking | A |
| Library reference transactions/capita | IMLS Public Libraries Survey (~1988→) | A |
| First-class mail per capita | USPS Revenue, Pieces & Weight reports | A |
| Newspaper circulation per capita | News Media Alliance / Pew | B |
| Britannica print cessation (2012) | Encyclopædia Britannica announcement / news of record | A |
| Major appliance price (real) | BLS CPI, major appliances | A |
| Appliance-repair establishments | Census County Business Patterns (NAICS 811412 / prior SIC) | B |
| Repair-labour cost | BLS CPI/PPI repair services | A |
| Refrigerator energy use | AHAM data via LBNL / ASAP "refrigerator graph"; DOE standards (CFR/FR) | A / B |

None of the figures in the triggering discussion are entered until read off the
cited source and logged. `/ocr` for scanned tables; script-assisted extraction
for the FADS/NHANES spreadsheets (Plan 010 precedent), then spot-verify by eye.

## Out of scope

- Any world-wing (UK etc.) data — D4 makes this wing *ready* to go comparative,
  but the foreign data is Plan 023+ and its own primary-source transcription.
- FX/PPP or any monetary conversion — the one count here (produce SKUs) is
  dimensionless; nothing on these axes is a currency magnitude.
- New fact-model or tier-vocabulary fields — this plan is pure curation + data +
  one new corridor wing on existing machinery.
- Narration/LLM text anywhere in the truth path (permanent charter rule); the
  wing's editorial voice lives only in the curation registry's wing fields, as
  the existing wings' do.
- Maternal mortality and other "progress" arcs — they fail the D1 selection
  principle (better, not *different*) and belong in the general corridors if
  anywhere.
- **Car reliability (considered, declined).** The evocative, D1-passing
  automotive material — unbelted children, no airbags, leaded exhaust — is
  already carried by WI-4's safety death-rates; a second car exhibit would
  over-weight automobiles in a wing meant to range widely. Reliability itself is
  a *progress* story, not a different-country one, and its strongest metric
  (average vehicle age, BTS / S&P Global Mobility, ~5→12.8 yrs) is heavily
  confounded by new-car affordability, financing, and recession — it would need
  so much carding that the emotional signal drains out; J.D. Power PP100 starts
  only 1987 with definition drift. Excluded to protect the wing's signal. If
  wanted, the average-vehicle-age datum can live as a supporting note in the
  *affordability* corridors, not as a different-country exhibit.
- **The appliance K-shape / quality-hollowing thesis as a sourced claim** — see
  WI-11: rendered as an explicit known-unknown, never asserted, because no
  primary-source series for within-category price/quality dispersion exists.
