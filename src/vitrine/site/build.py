"""Build orchestrator — output assembly only.

``build_site`` (re-exported as ``render_site`` for backward compatibility) owns
the environment, output directories, asset copy, the per-surface render+write
loop, the fact manifest, and the two registry-consistency gates. It does NOT do
fact-id resolution, SVG geometry, or ratio computation — every page is prepared
by a ``projections.project_*`` function that hands back a typed ``context.*Page``.
"""

from __future__ import annotations

import re
import tomllib
from importlib.resources import files
from pathlib import Path

from jinja2 import Environment, StrictUndefined

from vitrine.derive import evaluate_room
from vitrine.export import export_corpus
from vitrine.model import Corpus
from vitrine.publish import (
    ensure_publishable_directory,
    ensure_publishable_tree,
    staged_directory,
    validate_destination,
)
from vitrine.series import Series
from vitrine.site import curation, svg, tokens
from vitrine.site.context import (
    AffordabilityPage,
    BibliographyPage,
    CorridorPage,
    DataPage,
    EssayPage,
    EssaysIndexPage,
    LobbyPage,
    MethodologyPage,
    PairPage,
    RoomPage,
    SourceCollectionPage,
    WalkthroughPage,
)
from vitrine.site.environment import build_environment
from vitrine.site.projections import (
    project_bibliography,
    project_corridor,
    project_data,
    project_methodology,
    project_pair,
    project_walkthrough,
    validate_comparative_registries,
)
from vitrine.site.projections.affordability import (
    affordability_for_room,
    project_affordability_dashboard,
)
from vitrine.site.projections.essays import (
    essay_entry_views,
    essays_by_room,
    project_essay,
    project_essays_index,
    validate_essay_registries,
)
from vitrine.site.projections.facts import index_facts
from vitrine.site.projections.references import project_source
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
        | DataPage
        | EssayPage
        | EssaysIndexPage
        | LobbyPage
        | MethodologyPage
        | PairPage
        | RoomPage
        | SourceCollectionPage
        | WalkthroughPage
    ),
    standalone: bool = False,
) -> None:
    """Render ``template_name`` with ``page`` and write it to ``out_path``."""
    out_path.write_text(
        env.get_template(template_name).render(
            root=root, surface=surface, page=page, standalone=standalone
        )
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
    assets_dir.mkdir(mode=0o755, exist_ok=True)
    ensure_publishable_directory(assets_dir)
    enhancements = files("vitrine.site").joinpath("assets/enhancements.js").read_text()
    (assets_dir / "enhancements.js").write_text(enhancements)
    css_source = files("vitrine.site").joinpath("assets/museum.css.j2").read_text()
    # The stylesheet renders in its own non-autoescaping env on purpose: the
    # CSS uses {{ T.COPPER }} etc. and would be mangled by HTML autoescape.
    # build_environment() is for HTML templates only.
    museum_css = Environment(autoescape=False, undefined=StrictUndefined).from_string(
        css_source
    ).render(T=tokens)
    (assets_dir / "museum.css").write_text(museum_css)


def _environment_for(corpus: Corpus) -> Environment:
    """Build the template environment after resolving the charter disclaimer."""
    disclaimer_entry = corpus.assumptions.get("composite-family")
    if disclaimer_entry is None:
        raise ValueError(
            "assumption ledger must contain 'composite-family' — "
            "the disclaimer renders on every room (charter rule)"
        )
    env = build_environment(disclaimer_entry.statement, disclaimer_entry.title)
    env.globals["essays_available"] = bool(corpus.essays)
    return env


def build_data_page(
    corpus: Corpus, out_dir: Path, standalone: bool | None = None
) -> None:
    """Render the archive landing page and its presentation assets.

    ``vitrine export`` uses this small site-layer surface without rendering the
    museum's other pages.  The JSON/CSV files themselves are written by the
    stdlib-only :func:`vitrine.export.export_corpus` function.
    """
    validate_destination(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    validate_destination(out_dir)
    ensure_publishable_tree(out_dir)
    if standalone is None:
        required_core_pages = (
            "index.html",
            "corridors/index.html",
            "affordability/index.html",
            "walkthrough.html",
            "methodology.html",
            "bibliography.html",
        )
        # Essays are optional: an essay-free full build still has every core
        # surface, while a standalone export has none of those destinations.
        standalone = not all(
            (out_dir / page).is_file() for page in required_core_pages
        )
    _write_assets(out_dir)
    ensure_publishable_tree(out_dir)
    _render_page(
        _environment_for(corpus),
        "data.html",
        out_dir / "data.html",
        root="",
        surface="data",
        page=project_data(corpus),
        standalone=standalone,
    )
    ensure_publishable_tree(out_dir)


def _build_site_contents(
    corpus: Corpus,
    out_dir: Path,
    series: dict[str, Series] | None = None,
    data_dir: Path | None = None,
    publication_root: Path | None = None,
) -> None:
    """Render the full static site contents into a prepared directory.

    The provenance gate runs before this in the CLI; this function assembles
    the typed page contexts via ``projections.project_*`` and renders each
    template against its page. Output is byte-for-byte stable across the split.
    """
    if series is None:
        series = {}
    env = _environment_for(corpus)

    out_dir.mkdir(parents=True, exist_ok=True)
    for directory in (
        out_dir / "rooms",
        out_dir / "corridors",
        out_dir / "affordability",
        out_dir / "data",
    ):
        directory.mkdir(mode=0o755, exist_ok=True)
        ensure_publishable_directory(directory)
    _write_assets(out_dir)

    index = index_facts(corpus)
    fact_index = {fid: ref.fact for fid, ref in index.items()}
    rooms = sorted(corpus.rooms, key=lambda r: (r.country, r.decade))

    # Curation is still single-country. A second country's rooms are built and
    # navigable, but the comparative surfaces below -- the pair matrix, the
    # corridors, the walkthrough -- are US analyses keyed by decade alone, and a
    # second "1950s" collides with the first. Until those are country-aware they
    # are projected over the curated rooms only; the rest render as bare stages.
    curated_countries = {story.country for story in curation.ROOM_STORIES}
    curated_rooms = [room for room in rooms if room.country in curated_countries]
    decades = [room.decade for room in curated_rooms]

    # Every curated story must name a room that exists, and the registry must not
    # collapse two stories onto one key. The converse is deliberately NOT
    # required: a room may exist with no story yet (see room_story).
    story_slugs = set(curation.ROOM_STORY_BY_SLUG)
    room_slugs = {room.slug for room in rooms}
    if (
        len(curation.ROOM_STORIES) != len(curation.ROOM_STORY_BY_SLUG)
        or not story_slugs <= room_slugs
    ):
        raise ValueError(
            "every room story must name a built room, and story slugs must be "
            f"unique; unknown={sorted(story_slugs - room_slugs)}, "
            f"stories={len(curation.ROOM_STORIES)}, keys={len(story_slugs)}"
        )

    # derived facts evaluated once, shared by the room loop, the lobby's
    # record-at-a-glance matrix, and the essay interpolation layer
    computed_by_room = {
        room.slug: evaluate_room(room, series, fact_index) for room in rooms
    }
    export_corpus(
        corpus,
        out_dir,
        series,
        computed_by_room,
        source_dir=data_dir,
        lock_root=publication_root if publication_root is not None else out_dir,
    )

    # the comparative layer is decade-keyed US curation; it must never resolve
    # a room outside the curated set (FWI-004)
    validate_comparative_registries(corpus)

    # docent tours: chart slugs resolve or nothing renders (registry gate)
    validate_essay_registries(corpus)
    tour_links = essays_by_room(corpus, index)

    # lobby + methodology + bibliography
    _render_page(
        env, "index.html", out_dir / "index.html", root="", surface="rooms",
        page=project_lobby(
            corpus, curated_rooms, computed_by_room,
            essay_entry_views(corpus, index, computed_by_room, ""),
            all_rooms=tuple(rooms), curated_countries=curated_countries,
        ),
    )
    _render_page(
        env, "methodology.html", out_dir / "methodology.html",
        root="", surface="methodology", page=project_methodology(corpus),
    )
    _render_page(
        env, "bibliography.html", out_dir / "bibliography.html",
        root="", surface="bibliography", page=project_bibliography(corpus),
    )
    _render_page(
        env, "data.html", out_dir / "data.html",
        root="", surface="data", page=project_data(corpus),
    )

    # rooms — accumulate the render-coverage manifest and merged affordability
    rendered_ids: list[str] = []
    all_affordability: dict[str, dict[str, str]] = {}
    # Each country is its own wing: previous/next and the room map stay inside
    # it, so the last US room does not link to the first UK one as though the
    # timeline continued. Tours are US-authored and keyed by decade, so they
    # attach only to curated rooms -- otherwise a UK room would inherit the
    # backlinks of the US room sharing its decade.
    for country in sorted({room.country for room in rooms}):
        wing = [room for room in rooms if room.country == country]
        for room_position, room in enumerate(wing, start=1):
            computed = computed_by_room[room.slug]
            rendered_ids.extend(fact.id for fact in room.facts)
            rendered_ids.extend(cf.id for cf in computed)
            all_affordability.update(affordability_for_room(corpus, room))
            _render_page(
                env, "room.html", out_dir / "rooms" / f"{room.slug}.html",
                root="../", surface="rooms",
                page=project_room(
                    corpus,
                    room,
                    wing,
                    room_position,
                    index,
                    series,
                    computed,
                    tour_links.get(room.slug, ())
                    if room.country in curated_countries
                    else (),
                ),
            )

    # corridors index (wing validation happens inside project_corridor)
    _render_page(
        env, "corridors.html", out_dir / "corridors" / "index.html",
        root="../", surface="corridors",
        page=project_corridor(
            corpus, index, series, curated_rooms, all_affordability
        ),
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
        page=project_walkthrough(corpus, index, curated_rooms, all_affordability),
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

    # docent tours (Plan 016): index + one page per essay
    if corpus.essays:
        essays_dir = out_dir / "essays"
        essays_dir.mkdir(mode=0o755, exist_ok=True)
        ensure_publishable_directory(essays_dir)
        _render_page(
            env, "essays.html", out_dir / "essays" / "index.html",
            root="../", surface="essays",
            page=project_essays_index(
                corpus, index, computed_by_room, all_affordability, "../"
            ),
        )
        for essay in corpus.essays:
            _render_page(
                env, "essay.html", out_dir / "essays" / f"{essay.slug}.html",
                root="../", surface="essays",
                page=project_essay(
                    corpus,
                    essay,
                    index,
                    series,
                    computed_by_room,
                    all_affordability,
                    recessions,
                    "../",
                ),
            )

    source_dir = out_dir / "archive" / "sources"
    source_dir.mkdir(mode=0o755, parents=True, exist_ok=True)
    for source in corpus.sources.values():
        if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", source.id):
            raise ValueError(f"source id is not a portable source-page slug: {source.id!r}")
        _render_page(
            env, "source.html", source_dir / f"{source.id}.html",
            root="../../", surface="bibliography", page=project_source(corpus, source),
        )

    (out_dir / "facts-manifest.txt").write_text("\n".join(rendered_ids) + "\n")


def build_site(
    corpus: Corpus,
    out_dir: Path,
    series: dict[str, Series] | None = None,
    data_dir: Path | None = None,
) -> None:
    """Render the full static site via staged same-filesystem publication.

    All pages, assets, and corpus exports are built in a sibling staging
    directory. A successful handoff publishes one coherent build; replacing an
    existing non-empty directory has the brief absence window documented by
    :mod:`vitrine.publish`. Render failures leave the prior destination
    untouched; publication rollback and backup-cleanup failures have the
    explicit partial states documented by :mod:`vitrine.publish` instead of a
    blanket unchanged-destination guarantee.
    """
    with staged_directory(
        out_dir,
        forbidden_paths=(data_dir,) if data_dir is not None else (),
        cleanup_roots=(out_dir, out_dir / "data"),
    ) as staging:
        _build_site_contents(corpus, staging, series, data_dir, out_dir)
