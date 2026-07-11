"""Plan 007 acceptance criteria over the built site.

Builds once per session from the committed corpus and asserts on the actual
HTML: static (no script), marks resolve, symbols gated per room, deep links
land, gaps render as gaps.
"""

import re
from html.parser import HTMLParser
from itertools import combinations
from pathlib import Path

import pytest

from vitrine.check import check_mark_coverage
from vitrine.loader import load_corpus
from vitrine.model import Corpus
from vitrine.series import load_series
from vitrine.site import curation, symbols
from vitrine.site.render import _build_stage, _index_facts, render_site

DATA = Path(__file__).parent.parent / "data"


@pytest.fixture(scope="module")
def corpus() -> Corpus:
    return load_corpus(DATA)


@pytest.fixture(scope="module")
def site(corpus: Corpus, tmp_path_factory: pytest.TempPathFactory) -> Path:
    out = tmp_path_factory.mktemp("site")
    render_site(corpus, out, load_series(DATA), DATA)
    return out


class _Scanner(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.tags: list[str] = []
        self.mark_ids: list[str] = []
        self.hrefs: list[str] = []
        self.anchor_ids: set[str] = set()

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.tags.append(tag)
        for name, value in attrs:
            if name == "data-fact-id" and value:
                self.mark_ids.append(value)
            if name == "href" and value:
                self.hrefs.append(value)
            if name == "id" and value:
                self.anchor_ids.add(value)


def _scan(page: Path) -> _Scanner:
    scanner = _Scanner()
    scanner.feed(page.read_text())
    return scanner


def test_no_script_anywhere(site: Path) -> None:
    """AC 1: all static — no <script> in any truth-path page."""
    for page in site.rglob("*.html"):
        assert "script" not in _scan(page).tags, f"<script> in {page.name}"


def test_all_three_surfaces_render(site: Path, corpus: Corpus) -> None:
    """AC 1/5: rooms, corridors, and the walkthrough all exist."""
    assert (site / "walkthrough.html").is_file()
    assert (site / "corridors" / "index.html").is_file()
    n = len(corpus.rooms)
    assert len(list((site / "rooms").glob("*.html"))) == n
    assert len(list((site / "corridors").glob("*--*.html"))) == n * (n - 1) // 2


def test_museum_map_is_semantic_and_surface_aware(site: Path) -> None:
    """The global museum map identifies location without JavaScript."""
    pages = {
        site / "index.html": "Rooms",
        site / "corridors" / "index.html": "Trends",
        site / "affordability" / "index.html": "Affordability",
        site / "walkthrough.html": "Guided tour",
        site / "methodology.html": "Method",
        site / "bibliography.html": "Sources",
    }
    for page, active_label in pages.items():
        html = page.read_text()
        assert '<a class="skip-link" href="#content">' in html
        assert '<nav class="museum-map" aria-label="Museum map">' in html
        assert '<main id="content" tabindex="-1">' in html
        assert re.search(
            rf'<a class="here" aria-current="page"[^>]*>{re.escape(active_label)}</a>',
            html,
        ), page


def test_room_map_has_context_and_complete_timeline(site: Path, corpus: Corpus) -> None:
    rooms = sorted(corpus.rooms, key=lambda room: room.decade)
    first = (site / "rooms" / f"{rooms[0].slug}.html").read_text()
    middle_position = len(rooms) // 2
    middle_room = rooms[middle_position]
    middle = (site / "rooms" / f"{middle_room.slug}.html").read_text()
    last = (site / "rooms" / f"{rooms[-1].slug}.html").read_text()

    for html in (first, middle, last):
        assert '<nav class="room-map" aria-label="Decade rooms">' in html
        assert html.count('<i aria-hidden="true"></i>') == len(rooms)

    assert 'rel="prev"' not in first
    assert 'rel="next"' in first
    assert 'rel="prev"' in middle and 'rel="next"' in middle
    assert f"Room {middle_position + 1} of {len(rooms)}" in middle
    assert (
        f'class="on" aria-current="page" href="{middle_room.slug}.html"'
        in middle
    )
    assert 'rel="prev"' in last
    assert 'rel="next"' not in last


def test_mark_coverage_green_on_build(site: Path, corpus: Corpus) -> None:
    assert check_mark_coverage(corpus, site) == []


def test_mark_coverage_red_on_unresolvable_mark(site: Path, corpus: Corpus, tmp_path: Path) -> None:
    """AC 2: a mark that names a fact the corpus doesn't have is a red build."""
    bad = tmp_path / "bad"
    bad.mkdir()
    (bad / "page.html").write_text('<div data-fact-id="us-1950s-ghost">x</div>')
    problems = check_mark_coverage(corpus, bad)
    assert any("us-1950s-ghost" in p for p in problems)


def test_room_marks_stay_in_room(site: Path) -> None:
    """AC 4 (and honesty): every mark on a room page projects that room's facts —
    a symbol can't borrow another decade's diffusion fact."""
    for page in (site / "rooms").glob("*.html"):
        prefix = page.stem + "-"  # us-1950s-
        for mark_id in _scan(page).mark_ids:
            assert mark_id.startswith(prefix), f"{page.name}: foreign mark {mark_id}"


def test_absent_technology_is_not_drawn(site: Path, corpus: Corpus) -> None:
    """AC 4: a stage artifact appears only when its registry fact exists in the room."""
    for room in corpus.rooms:
        page = site / "rooms" / f"{room.slug}.html"
        room_ids = {f.id for f in room.facts}
        html = page.read_text()
        for artifact in ("television", "internet", "air-conditioning", "cable", "computer"):
            fid = curation.STAGE_DIFFUSION.get(artifact, {}).get(room.decade)
            sym = symbols.symbol(artifact, room.decade)
            assert sym is not None
            drawn = sym.svg[:60] in html
            if fid is None:
                assert not drawn, f"{room.slug}: {artifact} drawn without a fact"
            else:
                assert fid in room_ids
                assert drawn, f"{room.slug}: {artifact} has a fact but wasn't drawn"


def test_era_keyed_symbols() -> None:
    """The icebox precedes the round-top precedes the two-door."""
    assert symbols.symbol("refrigerator", "1900s").variant == "icebox"  # type: ignore[union-attr]
    assert symbols.symbol("refrigerator", "1950s").variant == "round-top"  # type: ignore[union-attr]
    assert symbols.symbol("refrigerator", "2020s").variant == "two-door"  # type: ignore[union-attr]
    assert symbols.symbol("telephone", "1900s").variant == "candlestick"  # type: ignore[union-attr]
    assert symbols.symbol("telephone", "1970s").variant == "push-button"  # type: ignore[union-attr]
    assert symbols.symbol("telephone", "1980s").variant == "handset"  # type: ignore[union-attr]
    assert symbols.symbol("telephone", "2020s").variant == "smartphone"  # type: ignore[union-attr]
    assert symbols.symbol("television", "1900s").variant == "rabbit-ear-set"  # type: ignore[union-attr]
    assert symbols.symbol("television", "1990s").variant == "crt-color"  # type: ignore[union-attr]
    assert symbols.symbol("television", "2000s").variant == "flat-panel"  # type: ignore[union-attr]
    assert symbols.symbol("no-such-artifact", "1950s") is None

    # New artifacts
    assert symbols.symbol("washing-machine", "1900s").variant == "wringer"  # type: ignore[union-attr]
    assert symbols.symbol("washing-machine", "1950s").variant == "top-loader"  # type: ignore[union-attr]
    assert symbols.symbol("washing-machine", "2000s").variant == "front-loader"  # type: ignore[union-attr]
    assert symbols.symbol("stove", "1900s").variant == "wood-coal"  # type: ignore[union-attr]
    assert symbols.symbol("stove", "1950s").variant == "cabinet-range"  # type: ignore[union-attr]
    assert symbols.symbol("stove", "2000s").variant == "smooth-top"  # type: ignore[union-attr]

    # Food items
    assert symbols.symbol("bread", "1900s").variant == "loaf"  # type: ignore[union-attr]
    assert symbols.symbol("milk", "1900s").variant == "bottle"  # type: ignore[union-attr]

    # Dynamic food still-life
    bowl_sym = symbols.symbol("food", "1900s")
    assert bowl_sym.variant == "bowl"  # type: ignore[union-attr]
    assert "ellipse" in bowl_sym.svg  # type: ignore[union-attr]

    still_life_sym = symbols.symbol("food", "1900s", "We had beef, eggs, and milk")
    assert still_life_sym.variant == "still-life"  # type: ignore[union-attr]
    assert 'd="-3 -3' in still_life_sym.svg or 'd="M-3 -3' in still_life_sym.svg  # type: ignore[union-attr]
    assert 'cx="1"' in still_life_sym.svg  # type: ignore[union-attr]
    assert 'd="M5.5 -4' in still_life_sym.svg  # type: ignore[union-attr]
    assert 'd="M-12 -2' not in still_life_sym.svg  # type: ignore[union-attr]


def test_chart_deep_links_resolve(site: Path) -> None:
    """WI-6 / Plan 009: every corridor mark links to a resolvable placard.

    Click targets are now in-page overlays (``#fact-id--modal``); the deep link
    to the room placard is preserved as the fallback path when a path is given.
    """
    for page in [site / "corridors" / "index.html", site / "walkthrough.html"]:
        base = page.parent
        for href in _scan(page).hrefs:
            if (
                "#" not in href
                or href.startswith("http")
                or href in {"#", "#dismissed"}
            ):
                continue
            path, _, anchor = href.partition("#")
            if not path:
                # in-page CSS-only overlay anchor; must exist on the same page
                assert anchor in _scan(page).anchor_ids, f"{page.name}: dead overlay anchor {href}"
                continue
            target = (base / path).resolve()
            assert target.is_file(), f"{page.name}: dead link {href}"
            assert anchor in _scan(target).anchor_ids, f"{page.name}: dead anchor {href}"


def test_modal_close_target_preserves_position(site: Path) -> None:
    """Dismissal targets no element, so browsers clear :target without scrolling."""
    for page in (site / "rooms" / "us-1950s.html", site / "corridors" / "index.html"):
        html = page.read_text()
        assert 'href="#dismissed" class="overlay-backdrop"' in html
        assert 'href="#dismissed" class="overlay-close"' in html
        assert 'id="dismissed"' not in html


def test_walkthrough_uses_in_page_placards(site: Path) -> None:
    html = (site / "walkthrough.html").read_text()
    assert 'href="#us-1950s-hourly-earnings-manufacturing--modal"' in html
    assert 'id="us-1950s-hourly-earnings-manufacturing--modal"' in html
    assert 'role="dialog"' in html
    assert "The paid-work record" in html
    assert "The unpaid-work record" in html
    assert "The father" not in html
    assert "The mother" not in html


def test_gaps_render_as_gaps_not_numbers(site: Path, corpus: Corpus) -> None:
    """A fact without a structured quantity never becomes chart geometry."""
    corridor = (site / "corridors" / "index.html").read_text()
    # the 1990s Ramey gap: its mark exists (a gap slot), but never as a dot with a value
    assert 'data-fact-id="us-1990s-home-production-women"' in corridor
    gap_mark = re.search(
        r'<g data-fact-id="us-1990s-home-production-women">.*?</g>', corridor, re.S
    )
    assert gap_mark is not None
    assert 'class="gapdot"' in gap_mark.group(0)
    assert 'class="dot"' not in gap_mark.group(0)


def test_home_production_shares_an_axis_and_rejects_atus_unit_splice(site: Path) -> None:
    """Women/men render together; daily ATUS quantities are linked gaps."""
    corridor = (site / "corridors" / "index.html").read_text()
    assert corridor.count("Unpaid home production, women and men") == 1
    assert "Women's unpaid home production</h2>" not in corridor
    assert "Men's unpaid home production</h2>" not in corridor
    assert 'class="arc multi-arc"' in corridor
    for fid in (
        "us-2010s-home-production-women",
        "us-2010s-home-production-men",
    ):
        mark = re.search(rf'<g data-fact-id="{fid}">.*?</g>', corridor, re.S)
        assert mark is not None
        assert 'class="gapdot"' in mark.group(0)
        assert 'class="dot"' not in mark.group(0)


def test_telephone_arc_does_not_splice_composite_or_cell_phone_values(site: Path) -> None:
    corridor = (site / "corridors" / "index.html").read_text()
    for fid in ("us-1900s-diffusion", "us-2020s-phone-vehicle-diffusion"):
        mark = re.search(rf'<g data-fact-id="{fid}">.*?</g>', corridor, re.S)
        assert mark is not None
        assert 'class="gapdot"' in mark.group(0)


def test_walkthrough_meter_and_house_are_honest(site: Path) -> None:
    """The 2020s meter row is the concept-splice gap; only sourced floor area scales."""
    html = (site / "walkthrough.html").read_text()
    assert "concept splice" in html
    atus_mark = re.search(
        r'<g data-fact-id="us-2010s-home-production-women">.*?</g>', html, re.S
    )
    assert atus_mark is not None
    assert 'class="gaptrack"' in atus_mark.group(0)
    assert "1,500 sq ft (sourced)" in html
    assert "floor area not yet curated" in html


def test_structural_room_gaps_are_visible_before_the_stage(site: Path) -> None:
    for decade in ("1910s", "1920s", "1930s", "1940s"):
        html = (site / "rooms" / f"us-{decade}.html").read_text()
        assert 'class="gap-banner"' in html
        assert html.index('class="gap-banner"') < html.index('class="stage"')
    assert 'class="gap-banner"' not in (site / "rooms" / "us-1950s.html").read_text()


def test_stage_artifacts_and_budget_notes_do_not_collide(corpus: Corpus) -> None:
    """WI-21: hold the audited ring/label clearances across all room scales."""
    index = _index_facts(corpus)
    for room in corpus.rooms:
        stage = _build_stage(room, index, "")
        scale = stage.home_scale

        # Rings are 34px across and their percentage labels extend below them.
        for left, right in combinations(stage.artifacts, 2):
            left_x = 400 + (left.x - 400) * scale
            left_y = 306 + (left.y - 306) * scale
            right_x = 400 + (right.x - 400) * scale
            right_y = 306 + (right.y - 306) * scale
            distance = ((left_x - right_x) ** 2 + (left_y - right_y) ** 2) ** 0.5
            assert distance >= 44, (
                f"{room.decade}: {left.artifact} and {right.artifact} "
                f"are only {distance:.1f}px apart"
            )

        for artifact in stage.artifacts:
            ax = 400 + (artifact.x - 400) * scale
            ay = 306 + (artifact.y - 306) * scale
            artifact_box = (ax - 20, ay - 20, ax + 20, ay + 38)
            for note in stage.zone_notes:
                nx = 400 + (note.x - 400) * scale
                ny = 306 + (note.y - 306) * scale
                text_width = len(note.text) * 5.5
                note_box = (
                    nx - text_width if note.x > 620 else nx,
                    ny - 11,
                    nx if note.x > 620 else nx + text_width,
                    ny + 3,
                )
                overlaps = not (
                    artifact_box[2] < note_box[0]
                    or note_box[2] < artifact_box[0]
                    or artifact_box[3] < note_box[1]
                    or note_box[3] < artifact_box[1]
                )
                assert not overlaps, (
                    f"{room.decade}: {artifact.artifact} overlaps {note.text!r}"
                )

        note_boxes: list[tuple[str, tuple[float, float, float, float]]] = []
        for note in stage.zone_notes:
            nx = 400 + (note.x - 400) * scale
            ny = 306 + (note.y - 306) * scale
            text_width = len(note.text) * 5.5
            note_boxes.append(
                (
                    note.text,
                    (
                        nx - text_width if note.x > 620 else nx,
                        ny - 11,
                        nx if note.x > 620 else nx + text_width,
                        ny + 3,
                    ),
                )
            )
        for (left_text, left), (right_text, right) in combinations(note_boxes, 2):
            overlaps = not (
                left[2] < right[0]
                or right[2] < left[0]
                or left[3] < right[1]
                or right[3] < left[1]
            )
            assert not overlaps, (
                f"{room.decade}: note {left_text!r} overlaps {right_text!r}"
            )


def test_budget_composition_exposes_folded_categories(site: Path) -> None:
    corridor = (site / "corridors" / "index.html").read_text()
    assert 'class="composition-key"' in corridor
    assert "Inspect the folded categories" in corridor
    assert "fuel &amp; light 5.25%" in corridor
    assert "liquor/sickness/amusements 14.51%" in corridor
    # The same breakdown rides in the SVG's native hover/focus tooltip.
    assert "other: 30.47% — 1900s (fuel &amp; light 5.25%" in corridor


def test_impossible_work_week_explains_multiple_earners(site: Path) -> None:
    html = (site / "rooms" / "us-1900s.html").read_text()
    assert "60 weeks of one earner&#39;s wages" in html
    assert "the family budget depended on income beyond this one manufacturing wage" in html


def test_large_affordability_ratios_are_prominent_and_caveated(site: Path) -> None:
    html = (site / "rooms" / "us-1900s.html").read_text()
    assert "Computed affordability" in html
    assert 'class="afford-box"' in html
    assert "Large ratio: inspect the wage population and anchor years" in html


def test_era_graded_light_varies(site: Path) -> None:
    """The stage glow tint differs between the 1900s and 2020s rooms."""
    page_1900s = (site / "rooms" / "us-1900s.html").read_text()
    page_2020s = (site / "rooms" / "us-2020s.html").read_text()
    from vitrine.site import tokens

    assert tokens.ERA_GLOW["1900s"] in page_1900s
    assert tokens.ERA_GLOW["2020s"] in page_2020s
    assert tokens.ERA_GLOW["2020s"] not in page_1900s


def test_vehicle_arc_has_seven_points() -> None:
    """WI-005: the vehicle-ownership arc spans 7 decades (1960s–2020s)."""
    arc = curation.ARC_BY_SLUG["vehicle"]
    assert len(arc.fact_ids) == 7
    expected_decades = {"1960s", "1970s", "1980s", "1990s", "2000s", "2010s", "2020s"}
    assert set(arc.fact_ids) == expected_decades
    for decade, fid in arc.fact_ids.items():
        assert fid == f"us-{decade}-vehicle-ownership"


def test_vehicle_arc_renders_dots_not_gaps(site: Path) -> None:
    """WI-005: the corridor chart shows 7 sourced dots (not gap markers) for
    the vehicle-ownership arc, each carrying a data-fact-id."""
    corridor = (site / "corridors" / "index.html").read_text()
    arc = curation.ARC_BY_SLUG["vehicle"]
    for fid in arc.fact_ids.values():
        assert f'data-fact-id="{fid}"' in corridor, f"missing vehicle arc mark: {fid}"
        # each mark should be a dot (sourced), not a gapdot
        mark = re.search(
            rf'<g data-fact-id="{re.escape(fid)}">.*?</g>', corridor, re.S
        )
        assert mark is not None, f"no mark group for {fid}"
        assert 'class="dot"' in mark.group(0), f"{fid} rendered as gap, not dot"
        assert 'class="gapdot"' not in mark.group(0), f"{fid} rendered as gapdot"


def test_automobile_glyph_drawn_for_vehicle_decades(site: Path, corpus: Corpus) -> None:
    """WI-005: the automobile stage glyph renders for every decade that has a
    vehicle-ownership fact (1960s–2020s)."""
    arc = curation.ARC_BY_SLUG["vehicle"]
    for decade in arc.fact_ids:
        page = site / "rooms" / f"us-{decade}.html"
        html = page.read_text()
        sym = symbols.symbol("automobile", decade)
        assert sym is not None, f"no automobile symbol for {decade}"
        assert sym.svg[:60] in html, f"automobile glyph not drawn in {decade} room"


def test_automobile_glyph_absent_before_1960s(site: Path) -> None:
    """WI-005: the automobile stage glyph is absent from decades before the
    vehicle-ownership arc begins (1900s–1950s)."""
    early_decades = ["1900s", "1910s", "1920s", "1930s", "1940s", "1950s"]
    for decade in early_decades:
        page = site / "rooms" / f"us-{decade}.html"
        html = page.read_text()
        sym = symbols.symbol("automobile", decade)
        if sym is not None:
            assert sym.svg[:60] not in html, f"automobile glyph unexpectedly drawn in {decade}"
