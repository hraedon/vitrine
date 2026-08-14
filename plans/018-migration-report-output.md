# Migration Report — Plan 018 Presentation Architecture

## Module sizes before and after

### Before (2 files, 2,476 lines)

| File | Lines |
|------|-------|
| `src/vitrine/site/render.py` | 1,653 |
| `src/vitrine/site/curation.py` | 823 |
| **Total** | **2,476** |

### After (20 files, 3,002 lines)

| File | Lines | Role |
|------|-------|------|
| `site/build.py` | 526 | Orchestration |
| `site/context.py` | 206 | Typed page contexts |
| `site/render.py` | 97 | Backward-compat re-exports |
| `site/projections/__init__.py` | 60 | Re-exports |
| `site/projections/facts.py` | 22 | Fact indexing |
| `site/projections/stage.py` | 115 | Stage cutaway |
| `site/projections/arcs.py` | 66 | Arc charts |
| `site/projections/affordability.py` | 152 | Affordability projections |
| `site/projections/pairs.py` | 122 | Pairwise corridor |
| `site/projections/metrics.py` | 125 | Dashboard metrics |
| `site/curation/__init__.py` | 60 | Re-exports |
| `site/curation/corridor.py` | 512 | Arcs, groups, afford items |
| `site/curation/room.py` | 113 | Stage, compositions, banners |
| `site/curation/affordability.py` | 103 | Dashboard metrics |
| `site/curation/walkthrough.py` | 57 | Walkthrough config |
| `site/templates/*.html` (11 files) | 402 | Jinja2 templates |
| `site/assets/vitrine.css` | 154 | External stylesheet |
| `site/assets/placard.js` | 110 | Focus enhancement module |
| **Total** | **3,002** |

The ~20% increase reflects the added context types, template files (vs. inline
strings), and the new browser test infrastructure.

## Generated-site size

`_site/` is 13 MB (unchanged from before — same HTML content, CSS now external).

## Browser-test matrix

| Scenario | JS enabled | JS disabled |
|----------|-----------|-------------|
| Open from chart mark | ✅ | ✅ (hash) |
| Open from walkthrough stop | ✅ | — |
| Open from room placard | ✅ | — |
| Initial load with hash | ✅ | — |
| Focus enters overlay | ✅ | — |
| Escape dismissal | ✅ | — |
| Backdrop dismissal | ✅ | ✅ |
| Close button dismissal | ✅ | ✅ |
| Focus returns to origin | ✅ | — |
| Tab containment | ✅ | — |
| Shift-Tab containment | ✅ | — |
| Browser Back | ✅ | — |
| Browser Forward | ✅ | — |
| Desktop (1280px) | ✅ | — |
| Mobile (375px) | ✅ | — |
| Room mobile placard | ✅ | — |

19 tests total, all passing.

## Intentional output changes

1. **Inline CSS → external stylesheet**: All `<style>` blocks replaced with
   `<link rel="stylesheet" href="assets/vitrine.css">`. Token values resolved
   to static hex (verified against `tokens.py`).

2. **Placard JS enhancement**: `<script src="assets/placard.js" defer>` added
   to `base.html`. Provides focus management, escape key, tab containment,
   and focus restoration. CSS `:target` fallback works without JS.

3. **Heading hierarchy fixes**: `<summary class="case-title">` now wraps an
   `<h2>`; legend `<h4>` → `<h2>`; walkthrough person cards `<h5>` → `<h3>`.

4. **Landmark improvements**: `<main>` wraps body content; topnav has
   `aria-label="Primary"`.

5. **Focus visibility**: Added `:focus-visible` CSS rule using brass-lit
   (#f0c778) on dark surfaces and brass-deep (#a97f34) on ivory cards.

6. **Stagehint contrast**: `#5c5240` → `#998b70` (2.3:1 → 5.3:1).

7. **Pairtable mobile overflow**: Wrapped in `overflow-x:auto` container.

8. **Provenance disclosure labels**: Added `aria-label` for screen-reader
   distinguishability.

9. **Scroll padding**: Added `scroll-padding-top:80px` defensively.

## Proposed framework use cases

No framework needed. The placard overlay pattern (CSS `:target` + small JS
enhancement) handles all current interactions. If future requirements need:
- Complex multi-step wizards or form state → consider a framework
- Real-time data updates → would require a runtime API (currently prohibited)
- Client-side filtering/sorting of facts → would violate "no client-rendered facts"

None of these apply today.
