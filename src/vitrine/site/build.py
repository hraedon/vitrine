"""Build orchestrator — output assembly only.

``build_site`` (re-exported as ``render_site`` for backward compatibility) owns
the environment, output directories, asset copy, the per-surface render+write
loop, the fact manifest, and the two registry-consistency gates. It does NOT do
fact-id resolution, SVG geometry, or ratio computation — every page is prepared
by a ``projections.project_*`` function that hands back a typed ``context.*Page``.
"""

from __future__ import annotations

import tomllib
from importlib.resources import files
from pathlib import Path

from jinja2 import Environment

from vitrine.derive import evaluate_room
from vitrine.model import Corpus
from vitrine.series import Series
from vitrine.site import curation, svg, tokens
from vitrine.site.context import (
    AffordabilityPage,
    BibliographyPage,
    CorridorPage,
    LobbyPage,
    MethodologyPage,
    PairPage,
    RoomPage,
    WalkthroughPage,
)
from vitrine.site.environment import build_environment
from vitrine.site.projections import (
    project_bibliography,
    project_corridor,
    project_methodology,
    project_pair,
    project_walkthrough,
)
from vitrine.site.projections.affordability import (
    affordability_for_room,
    project_affordability_dashboard,
)
from vitrine.site.projections.facts import index_facts
from vitrine.site.projections.rooms import project_lobby, project_room


def _render_page(
    env: Environment,
    template_name: str,
    out_path: Path,
    *,
    root: str,
    surface: str,
    page: (
        AffordabilityPage
        | BibliographyPage
        | CorridorPage
        | LobbyPage
        | MethodologyPage
        | PairPage
        | RoomPage
        | WalkthroughPage
    ),
) -> None:
    """Render ``template_name`` with ``page`` and write it to ``out_path``."""
    out_path.write_text(
        env.get_template(template_name).render(root=root, surface=surface, page=page)
    )


def _ym_to_year(ym: str) -> float:
    """'1973-11' → 1973 + (11-1)/12 ≈ 1973.83 (fractional year for band edges)."""
    year_s, month_s = ym.split("-")
    return int(year_s) + (int(month_s) - 1) / 12.0


def load_recessions(path: Path) -> tuple[tuple[svg.Recession, ...], str]:
    """Load NBER recession bands + the source url from data/recessions.toml."""
    if not path.is_file():
        return (), ""
    with path.open("rb") as fh:
        data = tomllib.load(fh)
    bands: list[svg.Recession] = []
    for entry in data.get("recession", []):
        bands.append(
            svg.Recession(peak=_ym_to_year(entry["peak"]), trough=_ym_to_year(entry["trough"]))
        )
    return tuple(bands), str(data.get("url", ""))


def _write_assets(out_dir: Path) -> None:
    """Copy the enhancement script and render the token-driven stylesheet."""
    assets_dir = out_dir / "assets"
    assets_dir.mkdir(exist_ok=True)
    enhancements = files("vitrine.site").joinpath("assets/enhancements.js").read_text()
    (assets_dir / "enhancements.js").write_text(enhancements)
    css_source = files("vitrine.site").joinpath("assets/museum.css.j2").read_text()
    # The stylesheet renders in its own non-autoescaping env on purpose: the
    # CSS uses {{ T.COPPER }} etc. and would be mangled by HTML autoescape.
    # build_environment() is for HTML templates only.
    museum_css = Environment(autoescape=False).from_string(css_source).render(T=tokens)
    (assets_dir / "museum.css").write_text(museum_css)


def build_site(
    corpus: Corpus,
    out_dir: Path,
    series: dict[str, Series] | None = None,
    data_dir: Path | None = None,
) -> None:
    """Render the full static site into ``out_dir``.

    The provenance gate runs before this in the CLI; this function assembles
    the typed page contexts via ``projections.project_*`` and renders each
    template against its page. Output is byte-for-byte stable across the split.
    """
    if series is None:
        series = {}
    disclaimer_entry = corpus.assumptions.get("composite-family")
    if disclaimer_entry is None:
        raise ValueError(
            "assumption ledger must contain 'composite-family' — "
            "the disclaimer renders on every room (charter rule)"
        )
    env = build_environment(disclaimer_entry.statement, disclaimer_entry.title)

    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "rooms").mkdir(exist_ok=True)
    (out_dir / "corridors").mkdir(exist_ok=True)
    (out_dir / "affordability").mkdir(exist_ok=True)
    _write_assets(out_dir)

    index = index_facts(corpus)
    rooms = sorted(corpus.rooms, key=lambda r: r.decade)
    decades = [room.decade for room in rooms]

    # room-story registry must cover the built rooms exactly (charter gate)
    story_decades = set(curation.ROOM_STORY_BY_DECADE)
    if (
        len(curation.ROOM_STORIES) != len(curation.ROOM_STORY_BY_DECADE)
        or story_decades != set(decades)
    ):
        raise ValueError(
            "room story registry must cover the built rooms exactly; "
            f"missing={sorted(set(decades) - story_decades)}, "
            f"unknown={sorted(story_decades - set(decades))}"
        )

    # lobby + methodology + bibliography
    _render_page(
        env, "index.html", out_dir / "index.html", root="", surface="rooms",
        page=project_lobby(rooms),
    )
    _render_page(
        env, "methodology.html", out_dir / "methodology.html",
        root="", surface="methodology", page=project_methodology(corpus),
    )
    _render_page(
        env, "bibliography.html", out_dir / "bibliography.html",
        root="", surface="bibliography", page=project_bibliography(corpus),
    )

    # rooms — accumulate the render-coverage manifest and merged affordability
    rendered_ids: list[str] = []
    all_affordability: dict[str, dict[str, str]] = {}
    for room_position, room in enumerate(rooms, start=1):
        computed = evaluate_room(room, series)
        rendered_ids.extend(fact.id for fact in room.facts)
        rendered_ids.extend(cf.id for cf in computed)
        all_affordability.update(affordability_for_room(corpus, room))
        _render_page(
            env, "room.html", out_dir / "rooms" / f"{room.slug}.html",
            root="../", surface="rooms",
            page=project_room(corpus, room, rooms, room_position, index, series),
        )

    # corridors index (wing validation happens inside project_corridor)
    _render_page(
        env, "corridors.html", out_dir / "corridors" / "index.html",
        root="../", surface="corridors",
        page=project_corridor(corpus, index, series, rooms, all_affordability),
    )

    # the pairwise set (the three epoch pages are the featured pairs)
    for i, a in enumerate(decades):
        for b in decades[i + 1 :]:
            _render_page(
                env, "pair.html", out_dir / "corridors" / f"{a}--{b}.html",
                root="../", surface="corridors",
                page=project_pair(corpus, index, a, b, all_affordability),
            )

    # the walkthrough
    _render_page(
        env, "walkthrough.html", out_dir / "walkthrough.html",
        root="", surface="walkthrough",
        page=project_walkthrough(corpus, index, rooms, all_affordability),
    )

    # the affordability dashboard (Plan 011)
    recessions, recession_url = load_recessions(
        (data_dir or Path("data")) / "recessions.toml"
    )
    _render_page(
        env, "affordability.html", out_dir / "affordability" / "index.html",
        root="../", surface="affordability",
        page=project_affordability_dashboard(series, recessions, index, recession_url),
    )

    (out_dir / "facts-manifest.txt").write_text("\n".join(rendered_ids) + "\n")
