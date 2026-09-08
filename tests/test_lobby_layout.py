"""The lobby's inventory separates measured values from documented absences."""

import re
from html import unescape
from pathlib import Path

import pytest

from vitrine.derive import evaluate_room
from vitrine.loader import load_corpus
from vitrine.series import load_series
from vitrine.site import curation
from vitrine.site.build import build_site
from vitrine.site.projections.rooms import atlas_matrix

DATA = Path(__file__).parent.parent / "data"


@pytest.fixture(scope="module")
def lobby(tmp_path_factory: pytest.TempPathFactory) -> str:
    out = tmp_path_factory.mktemp("lobby_layout")
    build_site(load_corpus(DATA), out, load_series(DATA), DATA)
    return (out / "index.html").read_text(encoding="utf-8")


def _words(html: str) -> str:
    return " ".join(unescape(re.sub(r"<[^>]*>", " ", html)).split())


def test_inventory_is_optional_with_visible_separate_totals(lobby: str) -> None:
    """A visitor can understand collection coverage without opening the matrix."""
    before, inventory = lobby.split('<details class="inventory-disclosure">', 1)
    assert 'aria-label="US collection totals"' in before
    assert "Sourced observations" in before
    assert "Calculations from sourced inputs" in before
    assert "Documented gaps" in before
    assert "they are counted separately and never mean zero" in before
    assert inventory.index('class="record-matrix"') < inventory.index("</details>")
    assert "Observation counts exclude documented gaps" in inventory
    assert "US wing ·" not in lobby


def test_matrix_labels_each_count_without_including_gaps_as_observations(lobby: str) -> None:
    """Check rendered cells, including gap-only cells, against their source records."""
    corpus = load_corpus(DATA)
    rooms = tuple(sorted(
        (room for room in corpus.rooms if room.country in curation.CURATED_COUNTRIES),
        key=lambda room: (room.country, room.decade),
    ))
    facts = {fact.id: fact for room in corpus.rooms for fact in room.facts}
    series = load_series(DATA)
    computed = {room.slug: evaluate_room(room, series, facts) for room in rooms}
    matrix, totals = atlas_matrix(rooms, computed)
    table = lobby.split('<table class="record-matrix">', 1)[1].split("</table>", 1)[0]
    body = table.split("<tbody>", 1)[1].split("</tbody>", 1)[0]
    rendered_rows = re.findall(r"<tr>(.*?)</tr>", body, re.DOTALL)
    assert len(rendered_rows) == len(matrix)
    for row, rendered in zip(matrix, rendered_rows, strict=True):
        cells = re.findall(r"<td>(.*?)</td>", rendered, re.DOTALL)
        for cell, html in zip((*row.cells, row.totals), cells, strict=True):
            text = _words(html)
            if not cell.exhibits:
                assert text == "No records"
                continue
            observations = cell.facts - cell.gaps
            expected = f"{observations} observation{'s' if observations != 1 else ''}"
            if cell.computed:
                expected += f" {cell.computed} calculation{'s' if cell.computed != 1 else ''}"
            if cell.gaps:
                expected += f" {cell.gaps} documented gap{'s' if cell.gaps != 1 else ''}"
            assert text == expected, (row.slug, text, expected)
    footer = table.split("<tfoot>", 1)[1]
    assert f"{totals.facts - totals.gaps}</b> observations" in footer
    assert f"{totals.computed} calculations" in footer
    assert f"{totals.gaps} documented gaps" in footer
