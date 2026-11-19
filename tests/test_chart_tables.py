"""Chart alternatives project the same observations without inventing years."""

from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

import pytest

from vitrine.loader import load_corpus
from vitrine.model import Tier
from vitrine.series import Series, load_series
from vitrine.site.build import build_site
from vitrine.site.curation.models import Metric
from vitrine.site.projections.chart_tables import annual_table, metric_tables, point_table
from vitrine.site.svg import ArcPoint


def test_table_preserves_excluded_record_without_plotting_its_quantity() -> None:
    points = (
        ArcPoint("1950s", "us-1950s-a", "#a", "A", "Included", "31%", 31.0),
        ArcPoint("1960s", "us-1960s-b", "#b", "C", "Different measure", "42%", None),
    )
    table = point_table(points, "% of measured population")
    assert table.rows[0].value == "31.0"
    excluded = table.rows[1]
    assert excluded.value == "Not plotted" and not excluded.plotted
    assert excluded.href == "#us-1960s-b--modal"
    assert excluded.label == "Different measure" and excluded.tier == "C"


def test_annual_table_retains_only_actual_series_years_and_population() -> None:
    series = Series(
        id="test", label="Observed series", source="source", tier=Tier.A,
        unit="test units", population="A specified survey population",
        values={1950: 0.0, 1952: 12.125},
    )
    table = annual_table(series, "../")
    assert [row.period for row in table.rows] == ["1950", "1952"]
    assert [row.value for row in table.rows] == ["0.0", "12.125"]
    assert table.population == series.population
    assert all(row.href == "../archive/sources/source.html" for row in table.rows)


def test_annual_table_rejects_unsupported_minor_unit_amounts() -> None:
    amount = Series(
        id="money", label="Money", source="source", tier=Tier.A, unit="USD",
        population="Specified population", currency="USD", values_minor={1950: 234},
    )
    with pytest.raises(ValueError, match="monetary minor-unit amounts"):
        annual_table(amount, "../")


def test_calculated_table_preserves_coverage_and_discloses_display_rounding() -> None:
    table, = metric_tables(
        Metric("test", "Test", "ratio", "Test caption"),
        {1950: 1.23456789, 1952: 9.0}, (), {}, "../",
    )
    assert [row.period for row in table.rows] == ["1950", "1952"]
    assert table.rows[0].value == "1.23457"
    assert "six significant digits" in table.note
    assert all(row.tier == "" for row in table.rows)  # No invented confidence badge.


def test_every_chart_table_evidence_link_resolves_in_the_static_build(tmp_path: Path) -> None:
    class TableLinks(HTMLParser):
        def __init__(self) -> None:
            super().__init__()
            self.ids: set[str] = set()
            self.links: list[str] = []
            self.in_table = False

        def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
            values = dict(attrs)
            if identifier := values.get("id"):
                self.ids.add(identifier)
            if tag == "table" and values.get("class") == "chart-value-table":
                self.in_table = True
            if self.in_table and tag == "a" and (href := values.get("href")):
                self.links.append(href)

        def handle_endtag(self, tag: str) -> None:
            if tag == "table":
                self.in_table = False

    data = Path(__file__).parent.parent / "data"
    build_site(load_corpus(data), tmp_path, load_series(data), data)
    pages: dict[Path, TableLinks] = {}
    for page in tmp_path.rglob("*.html"):
        parser = TableLinks()
        parser.feed(page.read_text(encoding="utf-8"))
        pages[page.resolve()] = parser
    assert any(parser.links for parser in pages.values())
    for page, parser in pages.items():
        for href in parser.links:
            parts = urlsplit(href)
            assert not parts.scheme and not parts.netloc, (page.name, href)
            target = (page.parent / unquote(parts.path)).resolve() if parts.path else page
            assert target in pages, (page.name, href)
            if parts.fragment:
                assert unquote(parts.fragment) in pages[target].ids, (page.name, href)
