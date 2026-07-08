# Gap Log — curator commentary

**The inventory itself is generated — run `vitrine gaps`.** It classifies,
mechanically, every rendered gap (value = "no reliable record…"), every Tier D
estimate (displayed value awaiting a primary-source upgrade), and every empty
panel, per room. This file carries only what a machine can't know: which source
would fill a gap, and which gaps are structural.

This file used to hand-maintain summary tables. Within a week they had drifted
badly out of sync with the corpus (5 of 13 rooms tracked, 101 of 203 facts
counted, filled gaps still listed as open, and one wrong number — "~55% lacked
complete plumbing in 1940" where the Census table says 45.3%). A hand-kept
summary table drifting from the data it summarizes is this project's founding
observation about everyone else's history content; it does not get to happen
here. Hence `vitrine gaps`.

## Structural gaps (likely permanent)

- **1940s expenditure and food basket.** No consumer expenditure survey exists
  for the 1940s, and wartime rationing (1942–46) makes what data exists
  non-representative. BLS Bulletin 1055 (1952) covers retail food *prices*
  1939–50 but not household baskets. The 1942 Wartime Consumption Survey is the
  only candidate; treat these as gaps the museum shows, not backlog.
- **Pre-1947 income.** No national family income survey before the CPS series
  (Census P-60, 1947→). The 1910s–1930s income gaps are filled only by proxy
  reconstructions (period cost-of-living surveys, Tier C) or scholarly
  estimates (Tier D) — never by an official median.

## Upgrade paths for standing Tier D estimates

- **New car prices (1900s, 1950s).** Widely-cited secondary figures; a primary
  upgrade needs period trade publications or NADA historical data.
- **1970s–2010s expenditure, food baskets, wages — FILLED** (2026-07-08 merge
  of `wi-1/us-source-survey`): CEX expenditure shares + food baskets
  (1970s–2010s) and BLS CES wages/hours (1980s–2010s) transcribed at Tier A;
  the `-gap` placeholder ids were renamed to real fact ids. What remains in
  those decades: housing detail (1960s–1980s `-housing-gap`), diffusion
  detail (1970s–1990s), and the 2010s home-value pair — see `vitrine gaps`
  and `docs/resource-hunt.md` for prioritized upgrade paths.
- **1950s rooms/heating-fuel detail.** The 1950 Census of Housing collected
  rooms and heating fuel; volumes are scanned online, not yet transcribed.

## Naming note

A fact id ending in `-gap` does not make it a rendered gap; classification is
by value and tier, not by name. Several `-gap` ids carry Tier D estimates with
real displayed values and are counted as estimates by `vitrine gaps`.
