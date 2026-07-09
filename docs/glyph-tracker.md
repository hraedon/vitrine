# Glyph Tracker

This tracker documents all artifact stage glyphs (Plan 007 and Plan 009 WI-20) and their era variants, showing which are fully implemented or pending.

## Stage Artifact Glyphs

| Artifact | Variant Key | Era / Year | Description | Status |
| :--- | :--- | :--- | :--- | :--- |
| **tenure** | `deed` | 0+ | Document deed rect and text lines | Done |
| **rooms** | `floor-plan` | 0+ | Basic rooms floor plan outline | Done |
| **electricity** | `drop-cord-bulb` | 0+ | Drop-cord light bulb | Done |
| | `bulb` | 1940+ | Standard wall/ceiling light bulb | Done |
| **radio** | `cathedral-console` | 0+ | Classic cathedral dome wooden cabinet | Done |
| | `tabletop-set` | 1940+ | Tabletop bakelite dial set | Done |
| **television** | `rabbit-ear-set` | 0+ | Box set with rabbit-ear antennas | Done |
| | `crt-color` | 1990+ | Deep CRT color television frame with controls | Done (WI-20) |
| | `flat-panel` | 2000+ | Slim flat-panel TV on stand | Done |
| **telephone** | `candlestick` | 0+ | Standup candlestick frame + receiver cup | Done |
| | `rotary-desk` | 1940+ | Classic desktop rotary dial console | Done |
| | `push-button` | 1970+ | Desktop button dial console | Done (WI-20) |
| | `handset` | 1980+ | Slim push-button wall/desk handset | Done |
| | `smartphone` | 2010+ | Flat smartphone face and home button | Done |
| **refrigerator** | `icebox` | 0+ | Heavy latch-hinge wooden icebox cabinet | Done |
| | `round-top` | 1940+ | Mid-century rounded top cabinet with horizontal handle | Done |
| | `two-door` | 1970+ | Modern double-door unit with handles | Done |
| **food** | `bowl` | 0+ | Basic wide bowl base and rim | Done |
| | `still-life` | dynamic | Gated still life showing named basket items | Done (WI-20) |
| **plumbing** | `hand-pump` | 0+ | Mechanical well hand pump | Done |
| | `tap` | 1940+ | Kitchen sink faucet tap and water droplet | Done |
| **heating** | `potbelly-stove` | 0+ | Parlor wood-burn stove with chimney duct | Done |
| | `radiator` | 1940+ | Wall metal steam radiator fins | Done |
| **automobile** | `horseless-carriage` | 0+ | High-wheel wagon automobile | Done |
| | `sedan` | 1920+ | Three-box boxy early sedan carriage | Done |
| | `modern-car` | 2000+ | Aerodynamic sedan contour | Done |
| **air-conditioning** | `window-unit` | 0+ | Boxy window-mounted cooler fan grill | Done |
| | `split-unit` | 2000+ | Sleek ductless mini-split wall panel | Done |
| **cable** | `coax-screen` | 0+ | Coaxial cable and box hookup | Done |
| **computer** | `desktop-crt` | 0+ | Classic beige desktop CRT unit and keyboard | Done |
| | `laptop` | 2000+ | Clamshell laptop body | Done |
| **internet** | `router` | 0+ | Router box with vertical antenna & signals | Done |
| **washing-machine** | `wringer` | 0+ | Tub on legs with top rollers and crank | Library-ready (WI-20) |
| | `top-loader` | 1950+ | Cabinet with top lid and dial dashboard | Library-ready (WI-20) |
| | `front-loader` | 2000+ | Front-loader cabinet with window door | Library-ready (WI-20) |
| **stove** | `wood-coal` | 0+ | Iron stove range with legs and chimney pipe | Library-ready (WI-20) |
| | `cabinet-range` | 1950+ | Classic stove range with dials backsplash | Library-ready (WI-20) |
| | `smooth-top` | 2000+ | Flat-top slide-in stove range with front window | Library-ready (WI-20) |

"Library-ready" means the glyph is drawn and era-keyed but not wired into the
rendering pipeline: `STAGE_POS` (svg.py) and `STAGE_DIFFUSION`/`STAGE_STATS`
(curation.py) do not yet include these artifacts, and no room has a dedicated
appliance-ownership fact for them. They will render once positions, fact
mappings, and data curation are added.

## Individual Food Items (WI-20 Still Life Elements)

These symbols are dynamically combined when named in the room's food-basket fact value:

- **bread** (`loaf`): A rounded loaf of bread with diagonal slash lines.
- **milk** (`bottle`): A tall milk bottle with a neck contour and fill level line.
- **meat** (`steak`): A classic T-bone steak outline with internal bone lines.
- **eggs** (`eggs`): Two overlapping egg ovals lying at different angles.
- **potatoes** (`tubers`): Two small organic potato ovals.
