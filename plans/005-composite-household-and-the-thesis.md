# Plan 005 — The composite household: people, home-production hours, and true scale

**Status:** proposed
**Triggered by:** the walkthrough concept demo + a stated purpose for the exhibit.

## The thesis (the exhibit's purpose)

vitrine is not a neutral catalogue; it argues against a specific, widespread
historical amnesia — *"the world was always basically like this."* Two claims
the data supports, made in sourced facts rather than narration:

1. **Technology transformed domestic labour — and the dividend was spent on
   higher standards, not leisure.** (Revised 2026-07-07; see "What Ramey
   actually shows" below.) Running water, the washing machine, the
   refrigerator, and central heat removed the physically grinding chores —
   hauling water, boiling laundry, tending fires — that fell overwhelmingly on
   women. But home-production *hours* fell far less before ~1965 than the
   appliance narrative predicts: the freed time was reallocated into cleaner
   clothes, more elaborate meals, more shopping, and far more childcare. This
   mirrors the market economy exactly — vastly improved productivity did not
   shorten the workweek proportionally either; the surplus went into
   consumption and standards. Progress is real in both cases, and it looks
   like *transformation and enrichment of the work*, not its disappearance.
   The steep per-woman hours decline comes after 1965, coinciding with women's
   move into market work.
2. **The single-earner mid-century family lived small and spartan.** The
   "one income used to be enough" nostalgia quietly assumes the 1950s family
   lived like we do, minus a paycheck. They did not: a small house, one
   bathroom (and more than a third of homes lacked complete plumbing), half
   without central heat, a modest food-heavy budget, few possessions, one car
   or none.

The amnesia is about *our own baseline*, so the exhibit's most important
comparison is the **long transect to the 2020s**, not any single decade.

### What Ramey actually shows (read before designing the exhibit)

Ramey (2009) — this plan's spine source — is a **revisionist** paper: its
headline argument is *against* the "engines of liberation" story (Greenwood,
Seshadri & Yorukoglu 2005) this plan's first draft assumed. Her estimates
show prime-age women's home-production hours roughly flat-to-modestly-falling
from 1900 to the mid-1960s while appliances diffused massively; the sharp
decline is post-1965. The adjacent literature agrees on the reallocation
(Vanek 1974's near-constant housewife hours; Ruth Schwartz Cowan, *More Work
for Mother*: mechanization raised standards rather than freeing time).

Consequences:

- The exhibit **argues the revised claim #1**, which Ramey supports, not the
  "hours collapsed" claim, which she rebuts.
- The **chore-composition breakdown is the centerpiece**, not the total-hours
  meter: laundry hours collapse (a full day per week pre-machine), while
  shopping and childcare hours rise. The composition shift *is* the
  higher-standards story, made visible.
- The owner's judgment, stated for the record and fair game to render as an
  editorial caption outside the truth path: shopping is less unpleasant than
  pre-mechanized laundry. The data shows the swap; the visitor can weigh it.

## The honesty guardrail (the counterweight)

An argument-driven exhibit is more tempting to overclaim. The discipline that
keeps it clean is the one already running, made explicit here:

- Every thesis-bearing figure carries its **tier** and the **population
  actually measured**; where the evidence is thin (historical time-use is a
  reconstruction, Tier C/D) the card says so.
- **Emphasis is allowed only on sourced facts.** Foregrounding a fact (a big
  meter, a scaled house) is editorial; asserting a *number* or a *cause* the
  sources don't carry is not. No narrator claims causation beyond what the
  juxtaposition of sourced facts shows.
- The composite-person disclaimer is persistent: each figure is a stack of
  separate medians, never one coherent individual.
- The comparability guard (Plan 004 `Measure`) extends to the new axes:
  women's home-production hours (Ramey) vs all-adult ATUS hours is a **concept
  splice** and must caveat; new-construction floor area vs occupied-stock area
  is another. Same-axis is necessary but not sufficient.

## Data-model additions (WI-1)

Minimal, additive, projection-only — decisions flagged for the owner:

- **`actor` dimension.** An optional closed field attributing a fact to a
  composite household member: `{father, mother, child, household}`. Lets the
  walkthrough bind a fact to a figure. Open question: a new `actor` field on
  `Fact`, or a new `household` panel plus actor — leaning `actor` field so
  existing panels (day/budget) still apply.
- **Home-production hours.** Represented as a fact with `basis = weekly`,
  `actor = mother|father|household`, plus a `Measure`-style tag distinguishing
  **unpaid home production** from **paid work** (both are "weekly hours" but
  are not the same concept — the splitting reason is the whole thesis). Open
  question: extend `Measure` with `home_production` / `paid_hours`, or a
  separate `hours_kind` enum. Leaning a small `hours_kind` enum, since
  `Measure` is scoped to affordability denominators.
- **Floor area.** A structured `area_sqft: int | None` (with a companion
  `area_basis` noting *new-construction* vs *occupied-stock* — they are not
  comparable and the gate should know). Drives true-scale rendering.

## Extraction targets for Hermes — Ramey (2009)

Source: **Valerie A. Ramey, "Time Spent in Home Production in the Twentieth-
Century United States: New Estimates from Old Data," *Journal of Economic
History* 69(1), 2009.** Register in `sources.toml` with full cite. Pull, per
benchmark year Ramey reports:

1. **Women's weekly hours of home production** — the thesis spine. Record the
   exact age range Ramey uses (e.g. prime-age 25–54, or 14+) as the
   **population** string; do not blur it. Extract the series *as published* —
   its shape (roughly level to the mid-1960s, falling after) is itself the
   finding; do not assume a pre-1965 fall.
2. **Men's weekly hours of home production** — the honest counterpoint (men's
   rose); needed so the household total is not misread.
3. **Total / per-capita household home-production hours** — Ramey stresses the
   per-woman decline is larger than the per-household decline (household size
   fell, men picked some up). Capture both so the exhibit cannot overstate.
4. **Component breakdown if present** (cooking, cleaning, laundry, care) — for
   the chore-breakdown card. Laundry is the headline (a full day/week pre-
   machine).
5. **Tier & caveat.** This is a rigorous reconstruction from disparate period
   studies → **Tier C** (period-survey reconstruction), not A. Note the
   splice from Ramey's series to modern ATUS (already in the 2020s room:
   `us-2020s-time-use`, household activities 1.78 hr/day, all adults 15+) — a
   concept change (women-specific vs all-adult), flagged, not smoothed.

Deliverable from Hermes: one `[[source]]` for Ramey + home-production `[[fact]]`
entries across the decade rooms we cover, `actor`-tagged, tiered, with the
age-range population verbatim.

## Reordered curation backlog (thesis-first)

1. **Ramey home-production hours** — the thesis spine. *Hermes, now.*
2. **Infant & child mortality** and **maternal mortality** series (Historical
   Statistics / NCHS) — the children's and mother's mortality cards; steep
   declines that carry claim #1's human stakes.
3. **Floor area by decade** (Census/AHS new-construction; Census room counts
   for the early rooms) — powers true-scale house size for claim #2. Flag the
   new-vs-stock basis.
4. **Conditional life expectancy** (e₁₀ / e₂₀) to sit beside life-expectancy-
   at-birth — the infant-mortality-controlled figure the owner asked for; same
   life tables, not yet pulled.
5. **Median height & weight** by decade, per adult member (and children where
   sourced) — a vivid living-standards signal: Americans grew markedly taller
   across the early century (better childhood nutrition and disease
   environment) and markedly heavier in the late century (the obesity
   transition). Two different stories on one body. Sourcing: **NHANES** for the
   modern era (Tier A, height and weight/BMI, by sex); historical height from
   **anthropometric history** — military-enlistment and skeletal records
   reconstructed by Fogel / Steckel / Komlos (Tier C, reconstruction, with the
   measured population — often *native-born white males of military age* —
   stated verbatim, since the early samples are narrow). Height doubles as a
   subtle figure cue (the family silhouettes can grow slightly over the
   transect); weight stays a card stat, never caricatured.
6. **Median education** + **compulsory-schooling years** (Census; Goldin–Katz,
   state-level, caveated) — secondary.

## Design work (WI-4, prototyped in the concept demo)

- **Labour-hours meter + chore composition.** The mother's weekly unpaid-labour
  hours rendered as a bar across decades beside the appliance-diffusion glow —
  drawn to whatever shape Ramey's series actually delivers (likely: hours
  roughly level while diffusion soars, then falling post-1965), NOT presupposed
  to move in inverse lockstep. A meter engineered so "one glance = the claim"
  is a causal assertion moved from prose into design, and the first draft of
  this plan made exactly that mistake. The composition sub-bars (laundry /
  cooking / cleaning / childcare / shopping) carry the real story: segments
  swap while the total resists. Historical points are Tier-C (Ramey pending);
  the modern point anchors on ATUS.
- **True-scale house size.** The cutaway scales with sourced floor area while
  the family stays constant — the 1950s home reads visibly cramped beside the
  2020s. Powers claim #2 spatially.

## Work items

- **WI-1** model: `actor` field, `hours_kind` (or `Measure` extension),
  `area_sqft` + `area_basis`; loader + `assert_never` dispatch; gate invariants
  (an `actor`-tagged hours fact must declare its `hours_kind`).
- **WI-2** curation: Ramey source + women's/men's/total home-production hours,
  tiered, `actor`-tagged, across covered rooms. *(Hermes)*
- **WI-3** curation: infant/child + maternal mortality series. *(Hermes)*
- **WI-3b** curation: median height & weight by decade and sex (NHANES modern,
  anthropometric-history reconstruction pre-war), population stated verbatim.
  *(Hermes)*
- **WI-4** curation: floor area by decade (+ basis). *(Hermes)*
- **WI-5** render: labour-hours meter + true-scale house size in the walkthrough
  projection; comparability caveats on hours (Ramey↔ATUS) and area
  (new↔stock).
- **WI-6** gate/tests: walkthrough-coverage (every rendered element resolves to
  a curated fact) + the new comparability caveats.

## Acceptance criteria

1. The mother's home-production hours render across the transect **in the
   shape the source delivers** (no presupposed fall pre-1965), every point
   tier-badged, the Ramey↔ATUS splice caveated, the chore-composition
   breakdown present. ✅ when WI-2/WI-4/WI-5 land.
2. The 1950s house renders visibly smaller than the 2020s, driven by sourced
   floor area with the new-vs-stock basis stated. ✅
3. No thesis figure appears without a tier and a population; provisional/unsourced
   values are visibly marked and never presented as fact.
4. `vitrine check`, ruff, mypy, pytest green; walkthrough-coverage gate green.

## Not in scope

- Narration or an authored "argument" text in the truth path (charter: no AI in
  the truth path; the facts argue, emphasis is the only editorial lever).
- Causal modelling (we juxtapose appliance diffusion and falling hours; we do
  not compute or assert a causal coefficient).
