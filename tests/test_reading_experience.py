"""Dense evidence stays readable, linkable and printable without a framework."""

import pytest
import test_browser as browser_tests
from playwright.sync_api import Page, expect

from vitrine.loader import load_corpus
from vitrine.site.svg import ArcPoint, arc_chart

browser_context_args = browser_tests.browser_context_args
nojs_page = browser_tests.nojs_page
server_url = browser_tests.server_url
site_dir = browser_tests.site_dir


@pytest.mark.parametrize("fact_id", [
    "us-1950s-tv-diffusion", "us-2020s-internet-diffusion",
    "uk-1980s-telephone", "jp-1990s-pc",
])
def test_record_fragment_reveals_its_native_topic_without_javascript(
    nojs_page: Page, server_url: str, fact_id: str,
) -> None:
    room = "-".join(fact_id.split("-")[:2])
    nojs_page.set_viewport_size({"width": 375, "height": 812})
    nojs_page.goto(f"{server_url}rooms/{room}.html#{fact_id}")
    record = nojs_page.locator(f"#{fact_id}")
    expect(record).to_be_visible()
    expect(record.locator("xpath=ancestor::details[@class='record-panel']")).to_have_attribute(
        "open", "",
    )
    record.locator(".f-open").click()
    expect(nojs_page.locator(f"#{fact_id}--modal")).to_be_visible()


def test_topics_fold_without_losing_record_links(page: Page, server_url: str) -> None:
    page.goto(server_url + "rooms/us-2020s.html")
    assert page.locator(".record-panel[open]").count() == 0
    expect(page.locator(".record-reading-controls")).to_be_visible()
    total = page.locator(".record-panel").count()
    page.get_by_role("button", name="Expand all topics").click()
    assert page.locator(".record-panel[open]").count() == total
    collapse = page.get_by_role("button", name="Collapse all topics")
    collapse.click()
    assert page.locator(".record-panel[open]").count() == 0
    expect(collapse).to_be_focused()
    topic = page.locator('.exhibit-map a[href="#panel-diffusion"]')
    topic.click()
    expect(page.locator("#panel-diffusion .record-panel")).to_have_attribute("open", "")
    expect(page.locator("#panel-diffusion .panel-head")).to_be_focused()
    page.get_by_role("button", name="Collapse all topics").click()
    topic.click()  # The hash is unchanged; clicking the topic must still reveal it.
    expect(page.locator("#panel-diffusion .record-panel")).to_have_attribute("open", "")


def test_selected_record_has_a_keyboard_reading_start(page: Page, server_url: str) -> None:
    page.goto(server_url + "rooms/us-1950s.html#us-1950s-tv-diffusion")
    record = page.locator("#us-1950s-tv-diffusion")
    expect(record).to_be_focused()
    page.keyboard.press("Tab")
    expect(record.locator(".f-drawer summary")).to_be_focused()
    page.keyboard.press("Enter")
    expect(record.locator(".f-drawer")).to_have_attribute("open", "")


def test_calculation_fragment_reveals_its_topic_without_javascript(
    nojs_page: Page, server_url: str,
) -> None:
    nojs_page.goto(server_url + "rooms/us-2020s.html#us-2020s-home-as-income-years")
    record = nojs_page.locator("#us-2020s-home-as-income-years")
    expect(record).to_be_visible()
    record.locator("summary").click()
    expect(record.locator(".drawer")).to_be_visible()


def test_print_reveals_closed_records_without_javascript(
    nojs_page: Page, server_url: str,
) -> None:
    nojs_page.goto(server_url + "rooms/us-1950s.html")
    expect(nojs_page.locator("#us-1950s-tv-diffusion")).not_to_be_visible()
    nojs_page.emulate_media(media="print")
    expect(nojs_page.locator("#us-1950s-tv-diffusion")).to_be_visible()


def test_bad_fragment_does_not_break_source_cards(page: Page, server_url: str) -> None:
    errors: list[str] = []
    page.on("pageerror", lambda error: errors.append(str(error)))
    page.goto(server_url + "rooms/us-1950s.html#%E0%A4%A")
    page.locator('.house a[href="#us-1950s-tv-diffusion--modal"]').click()
    overlay = page.locator("#us-1950s-tv-diffusion--modal")
    expect(overlay).to_have_attribute("aria-modal", "true")
    page.keyboard.press("Escape")
    expect(overlay).not_to_be_visible()
    assert not errors


def test_source_calculation_method_is_visible_without_javascript(
    nojs_page: Page, server_url: str,
) -> None:
    fact_id = "us-2020s-cex-healthcare-share"
    corpus = load_corpus(browser_tests.DATA)
    fact = next(fact for room in corpus.rooms for fact in room.facts if fact.id == fact_id)
    assert fact.audit is not None and fact.audit.calculation is not None
    method = fact.audit.calculation.method
    nojs_page.goto(server_url + f"rooms/us-2020s.html#{fact_id}")
    record = nojs_page.locator(f"#{fact_id}")
    expect(record).to_contain_text("Includes a calculated value")
    record.locator(".f-drawer summary").click()
    expect(record.locator(".source-calculation")).to_contain_text(method)
    expect(record.locator(".source-calculation")).to_contain_text("decimal places")
    expect(record.locator(".source-calculation")).to_contain_text(
        "do not validate every other number or claim",
    )
    record.locator(".f-open").click()
    overlay = nojs_page.locator(f"#{fact_id}--modal")
    overlay.locator("details > summary").click()
    expect(overlay.locator(".source-calculation")).to_contain_text(method)
    nojs_page.goto(server_url + f"archive/sources/{fact.source}.html")
    source = nojs_page.locator(f'[data-source-fact-id="{fact_id}"]')
    source.locator(".audit-method summary").click()
    expect(source.locator(".source-calculation")).to_contain_text(method)


@pytest.mark.parametrize("width", [375, 1280])
def test_withdrawn_composition_stays_a_linked_gap_without_javascript(
    nojs_page: Page, server_url: str, width: int,
) -> None:
    nojs_page.set_viewport_size({"width": width, "height": 900})
    nojs_page.goto(server_url + "corridors/index.html")
    composition = nojs_page.locator("#budget-composition")
    if composition.get_attribute("open") is None:
        composition.locator(":scope > summary").click()
    fact_id = "us-1970s-expenditure-shares"
    gap = composition.locator(f'a.composition-gap[href="#{fact_id}--modal"]')
    expect(gap).to_be_visible()
    expect(gap).to_contain_text("1970s")
    expect(gap).to_contain_text("no reliable record")
    assert gap.locator("svg").count() == 0
    gap.click()
    expect(nojs_page.locator(f"#{fact_id}--modal")).to_be_visible()
    assert nojs_page.evaluate("document.documentElement.scrollWidth <= innerWidth")


@pytest.mark.parametrize("width", [320, 375, 1280])
def test_chart_table_opens_a_source_record_without_javascript(
    nojs_page: Page, server_url: str, width: int,
) -> None:
    nojs_page.set_viewport_size({"width": width, "height": 900})
    nojs_page.goto(server_url + "corridors/index.html")
    exhibit = nojs_page.locator("#homeownership")
    if exhibit.get_attribute("open") is None:
        exhibit.locator(":scope > summary").click()
    data = exhibit.locator(".chart-data").first
    data.locator("summary").click()
    table = data.locator("table")
    expect(table).to_be_visible()
    box = table.bounding_box()
    assert box is not None and box["x"] >= 0 and box["x"] + box["width"] <= width
    link = table.locator('a[href="#us-1950s-homeownership-rate--modal"]')
    link.click()
    expect(nojs_page.locator("#us-1950s-homeownership-rate--modal")).to_be_visible()


def test_arc_labels_clear_the_decade_axis_at_zero(page: Page) -> None:
    points = tuple(ArcPoint(
        decade=decade, fact_id=f"us-{decade}-sample", href="#sample",
        tier="A", label="Test observation", value=str(value), quantity=value,
    ) for decade, value in [("1950s", 0.0), ("1960s", 0.1), ("1970s", 100.0)])
    page.set_content('<style>svg{width:880px}.vlab,.xlab{font:10px monospace}</style>'
                     + arc_chart(points, "test units"))
    collisions = page.locator(".vlab").evaluate_all("""labels => {
      const axes=[...document.querySelectorAll('.xlab')].map(el=>el.getBoundingClientRect());
      return labels.flatMap(el=>{
        const b=el.getBoundingClientRect();
        return axes.filter(a=>b.left<a.right && b.right>a.left && b.top<a.bottom && b.bottom>a.top)
                   .map(()=>el.textContent);
      });
    }""")
    assert not collisions


@pytest.mark.parametrize("width", [320, 375, 900, 1440])
def test_navigation_targets_fit_and_remain_readable(
    page: Page, server_url: str, width: int,
) -> None:
    page.set_viewport_size({"width": width, "height": 900})
    page.goto(server_url + "index.html")
    sizes = page.locator(".museum-map a").evaluate_all("""links => links.map(el => ({
      height:el.getBoundingClientRect().height, width:el.getBoundingClientRect().width,
      size:parseFloat(getComputedStyle(el).fontSize)
    }))""")
    assert all(item["size"] >= 11 for item in sizes)
    assert all(item["width"] >= 44 for item in sizes)
    assert all(item["height"] >= (44 if width <= 560 else 36) for item in sizes)
    assert page.evaluate("document.documentElement.scrollWidth <= innerWidth")
