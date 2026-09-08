"""Browser interaction tests for the placard state machine (Plan 019 WP5).

Tests run against a built site served over local HTTP using Playwright.
Two execution modes are covered:

- **JavaScript enabled** (enhanced): focus management, tab containment,
  Escape / backdrop / close dismissal, ``.wrap`` inertness, focus
  restoration, A→B state transfer, and browser back/forward.
- **JavaScript disabled** (CSS-only): ``:target`` open/close, back/forward,
  no false ``aria-modal``, and content present without client execution.

Responsive checks verify no horizontal overflow and placard fit at three
viewports (1280x800, 768x1024, 375x667).

Run: ``pytest tests/test_browser.py -v``
"""

from __future__ import annotations

import functools
import http.server
import re
import socketserver
import threading
from collections.abc import Iterator
from pathlib import Path
from typing import Any

import pytest

playwright = pytest.importorskip("playwright")
from playwright.sync_api import Browser, Page, expect  # noqa: E402

DATA = Path(__file__).parent.parent / "data"
DEPLOY_CONFIG = DATA.parent / "deploy" / "nginx.conf"


def _production_headers() -> dict[str, str]:
    """Use the deployed literal headers, so local rendering exercises its CSP."""
    declarations = re.findall(
        r'^\s*add_header\s+([\w-]+)\s+"([^"\n]*)"\s+always;',
        DEPLOY_CONFIG.read_text(),
        re.MULTILINE,
    )
    headers = dict(declarations)
    assert "Content-Security-Policy" in headers
    assert len(headers) == len(declarations), "duplicate server headers need explicit handling"
    return headers

# Fact IDs verified present in the built site.
FACT_TV = "us-1950s-tv-diffusion"
FACT_RADIO = "us-1950s-radio-diffusion"
FACT_1910S_WAGES = "us-1910s-manufacturing-wages"

MODAL_TV = f"{FACT_TV}--modal"
MODAL_RADIO = f"{FACT_RADIO}--modal"
MODAL_1910S = f"{FACT_1910S_WAGES}--modal"

ROOM_1950S = "rooms/us-1950s.html"
CORRIDORS = "corridors/index.html"
LOBBY = "index.html"

VIEWPORTS = [
    pytest.param(1280, 800, id="desktop-1280"),
    pytest.param(768, 1024, id="tablet-768"),
    pytest.param(375, 667, id="mobile-375"),
]


# ── Fixtures ─────────────────────────────────────────────────────────────────


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args: dict[str, Any]) -> dict[str, Any]:
    """The browser must enforce the same policy visitors receive."""
    return {**browser_context_args, "bypass_csp": False}


@pytest.fixture(scope="module")
def site_dir(tmp_path_factory: pytest.TempPathFactory) -> Path:
    from vitrine.loader import load_corpus
    from vitrine.series import load_series
    from vitrine.site.build import build_site

    out = tmp_path_factory.mktemp("browser_site")
    build_site(load_corpus(DATA), out, load_series(DATA), DATA)
    return out


@pytest.fixture(scope="module")
def server_url(site_dir: Path) -> Iterator[str]:
    """Serve the built site with the exact production response headers."""
    production_headers = _production_headers()

    class ProductionHandler(http.server.SimpleHTTPRequestHandler):
        def end_headers(self) -> None:
            for name, value in production_headers.items():
                self.send_header(name, value)
            super().end_headers()

    handler = functools.partial(
        ProductionHandler, directory=str(site_dir)
    )
    with socketserver.TCPServer(("127.0.0.1", 0), handler) as httpd:
        port = httpd.server_address[1]
        thread = threading.Thread(target=httpd.serve_forever, daemon=True)
        thread.start()
        yield f"http://127.0.0.1:{port}/"
        httpd.shutdown()


@pytest.fixture
def nojs_page(browser: Browser) -> Iterator[Page]:
    """A fresh page with JavaScript disabled (CSS-only :target fallback)."""
    context = browser.new_context(java_script_enabled=False, bypass_csp=False)
    page = context.new_page()
    yield page
    context.close()


# ── Helpers ──────────────────────────────────────────────────────────────────


def test_deployed_policy_keeps_generated_styles_legible(page: Page, server_url: str) -> None:
    """Tier colors and SVG alignment must work under the served policy."""
    response = page.goto(server_url + "rooms/us-1980s.html")
    assert response is not None
    assert response.headers["content-security-policy"] == _production_headers()[
        "Content-Security-Policy"
    ]
    chip = page.locator('.tchip[style]').first
    assert chip.count() == 1
    assert chip.evaluate("el => getComputedStyle(el).backgroundColor") == chip.evaluate(
        "el => el.style.backgroundColor"
    )
    assert chip.evaluate("el => getComputedStyle(el).backgroundColor") != "rgba(0, 0, 0, 0)"
    right_aligned_note = page.locator('svg .znote[style*="text-anchor:end"]').first
    assert right_aligned_note.count() == 1
    assert right_aligned_note.evaluate("el => getComputedStyle(el).textAnchor") == "end"


def test_deployed_policy_allows_attributes_without_inline_elements(
    page: Page, server_url: str,
) -> None:
    """The style-attribute exception must not become an inline-code exception."""
    page.goto(server_url + LOBBY)
    result = page.evaluate("""() => {
        const probe = document.createElement('span');
        probe.id = 'policy-probe';
        probe.textContent = 'Policy rendering check';
        probe.setAttribute('style', 'color: rgb(1, 2, 3)');
        document.body.append(probe);
        const sheet = document.createElement('style');
        sheet.textContent = '#policy-probe { color: rgb(4, 5, 6) !important; }';
        document.head.append(sheet);
        const script = document.createElement('script');
        script.textContent = "document.documentElement.dataset.policyProbe = 'ran'";
        document.head.append(script);
        const result = {
            color: getComputedStyle(probe).color,
            scriptRan: document.documentElement.dataset.policyProbe === 'ran'
        };
        probe.remove();
        sheet.remove();
        script.remove();
        return result;
    }""")
    assert result == {"color": "rgb(1, 2, 3)", "scriptRan": False}


@pytest.mark.parametrize("width,height", VIEWPORTS)
def test_country_directory_without_javascript(
    nojs_page: Page, server_url: str, width: int, height: int,
) -> None:
    """Every country's decades remain reachable on small screens without JS."""
    nojs_page.set_viewport_size({"width": width, "height": height})
    nojs_page.goto(f"{server_url}{LOBBY}")
    nojs_page.get_by_role("link", name="Choose a room", exact=True).click()
    assert nojs_page.url.endswith("#choose-room")
    links = nojs_page.locator(".wing-decades a")
    assert links.count() == 27
    for link in links.all():
        box = link.bounding_box()
        assert box is not None
        assert box["x"] >= 0 and box["x"] + box["width"] <= width
        assert box["height"] >= 44
    nojs_page.get_by_role("link", name="Japan, 1980s", exact=True).click()
    assert nojs_page.url.endswith("rooms/jp-1980s.html")
    expect(nojs_page.locator(".room-disclaimer")).to_be_visible()


def _open(page: Page, modal_id: str = MODAL_TV) -> None:
    """Open a placard by setting the location hash (triggers hashchange)."""
    page.evaluate(f"location.hash = '#{modal_id}'")
    page.wait_for_timeout(100)


def _expect_open(page: Page, modal_id: str = MODAL_TV) -> None:
    overlay = page.locator(f"#{modal_id}")
    expect(overlay).to_be_visible()
    expect(overlay).to_have_attribute("aria-modal", "true")


def _expect_closed(page: Page, modal_id: str = MODAL_TV) -> None:
    overlay = page.locator(f"#{modal_id}")
    expect(overlay).not_to_be_visible()
    assert overlay.evaluate("el => !el.hasAttribute('aria-modal')")
    assert page.locator(".wrap").evaluate("el => !el.hasAttribute('inert')")


def _focus_inside(page: Page, modal_id: str = MODAL_TV) -> bool:
    return page.locator(f"#{modal_id}").evaluate(
        "el => el.contains(document.activeElement)"
    )


# ── Opening placards ─────────────────────────────────────────────────────────


class TestOpenPlacard:
    def test_open_from_story_stop(self, page: Page, server_url: str) -> None:
        """Clicking a room-story trigger opens the overlay enhanced."""
        page.goto(f"{server_url}{ROOM_1950S}")
        page.locator(f'a.story-stop[href="#{MODAL_TV}"]').click()
        page.wait_for_timeout(100)
        _expect_open(page, MODAL_TV)

    def test_open_from_svg_chart_mark(self, page: Page, server_url: str) -> None:
        """Activating an SVG chart point (in an open exhibit) opens the overlay."""
        page.goto(f"{server_url}{CORRIDORS}")
        page.wait_for_timeout(100)
        # The radio exhibit is open by default. SVG <a> elements are SVGElement
        # (no .click()) and their bounding box is intercepted by the parent
        # <svg> for Playwright's hit-testing, so dispatch a click event + hash
        # navigation via evaluate — the same effect a real click has.
        page.evaluate(
            """(sel) => {
                const el = document.querySelector(sel);
                if (!el) return;
                el.dispatchEvent(new MouseEvent('click', {bubbles: true}));
                location.hash = el.getAttribute('href');
            }""",
            f'a[href="#{MODAL_RADIO}"]',
        )
        page.wait_for_timeout(100)
        _expect_open(page, MODAL_RADIO)

    def test_load_with_initial_hash(self, page: Page, server_url: str) -> None:
        """Loading a page with #fact-id--modal opens the overlay immediately."""
        page.goto(f"{server_url}{CORRIDORS}#{MODAL_TV}")
        _expect_open(page, MODAL_TV)


# ── Focus and inert state ────────────────────────────────────────────────────


class TestFocusAndInert:
    def test_focus_enters_overlay(self, page: Page, server_url: str) -> None:
        """When a placard opens, focus moves inside the overlay."""
        page.goto(f"{server_url}{CORRIDORS}")
        _open(page, MODAL_TV)
        assert _focus_inside(page, MODAL_TV)

    def test_wrap_inert_and_aria_modal(self, page: Page, server_url: str) -> None:
        """While open, .wrap is inert and the overlay carries aria-modal."""
        page.goto(f"{server_url}{CORRIDORS}")
        _open(page, MODAL_TV)
        assert page.locator(".wrap").evaluate("el => el.hasAttribute('inert')")
        assert page.locator(f"#{MODAL_TV}").get_attribute("aria-modal") == "true"


# ── Tab containment ──────────────────────────────────────────────────────────


class TestTabContainment:
    def test_tab_stays_within_overlay(self, page: Page, server_url: str) -> None:
        """Tab cycles focus inside the overlay (wraps at boundaries)."""
        page.goto(f"{server_url}{CORRIDORS}")
        _open(page, MODAL_TV)
        for _ in range(6):
            page.keyboard.press("Tab")
            page.wait_for_timeout(40)
        assert _focus_inside(page, MODAL_TV)

    def test_shift_tab_stays_within_overlay(
        self, page: Page, server_url: str
    ) -> None:
        """Shift-Tab cycles focus inside the overlay (wraps at boundaries)."""
        page.goto(f"{server_url}{CORRIDORS}")
        _open(page, MODAL_TV)
        for _ in range(6):
            page.keyboard.press("Shift+Tab")
            page.wait_for_timeout(40)
        assert _focus_inside(page, MODAL_TV)


# ── Dismissal paths ──────────────────────────────────────────────────────────


class TestDismissal:
    def test_escape_dismissal(self, page: Page, server_url: str) -> None:
        page.goto(f"{server_url}{CORRIDORS}")
        _open(page, MODAL_TV)
        _expect_open(page, MODAL_TV)
        page.keyboard.press("Escape")
        _expect_closed(page, MODAL_TV)

    def test_close_button_dismissal(self, page: Page, server_url: str) -> None:
        page.goto(f"{server_url}{CORRIDORS}")
        _open(page, MODAL_TV)
        _expect_open(page, MODAL_TV)
        page.locator(f"#{MODAL_TV} .overlay-close").click()
        _expect_closed(page, MODAL_TV)

    def test_backdrop_dismissal(self, page: Page, server_url: str) -> None:
        page.goto(f"{server_url}{CORRIDORS}")
        _open(page, MODAL_TV)
        _expect_open(page, MODAL_TV)
        # Click top-left corner of the backdrop (outside the centered card).
        page.locator(f"#{MODAL_TV} .overlay-backdrop").click(
            position={"x": 5, "y": 5}
        )
        _expect_closed(page, MODAL_TV)

    def test_browser_back_dismissal(self, page: Page, server_url: str) -> None:
        """Browser Back closes the overlay (real navigation updates :target)."""
        page.goto(f"{server_url}{CORRIDORS}")
        _open(page, MODAL_TV)
        _expect_open(page, MODAL_TV)
        page.go_back()
        _expect_closed(page, MODAL_TV)


# ── Focus restoration ────────────────────────────────────────────────────────


class TestFocusRestoration:
    def test_focus_returns_to_origin(self, page: Page, server_url: str) -> None:
        """After Escape, focus returns to the exact originating trigger."""
        page.goto(f"{server_url}{ROOM_1950S}")
        selector = f'a.story-stop[href="#{MODAL_TV}"]'
        page.locator(selector).click()
        _expect_open(page, MODAL_TV)
        page.keyboard.press("Escape")
        page.wait_for_timeout(150)
        # Enhanced cleanup ran.
        assert page.locator(f"#{MODAL_TV}").evaluate(
            "el => !el.hasAttribute('aria-modal')"
        )
        assert page.locator(".wrap").evaluate("el => !el.hasAttribute('inert')")
        # Focus returned to the exact origin (not just any anchor or BODY).
        is_origin = page.evaluate(
            "(sel) => document.activeElement === document.querySelector(sel)",
            selector,
        )
        assert is_origin, "Focus did not return to the originating story-stop trigger"


# ── Reopen ───────────────────────────────────────────────────────────────────


class TestReopen:
    def test_open_close_reopen(self, page: Page, server_url: str) -> None:
        """Closing and reopening the same overlay works identically."""
        page.goto(f"{server_url}{CORRIDORS}")
        _open(page, MODAL_TV)
        _expect_open(page, MODAL_TV)
        page.keyboard.press("Escape")
        _expect_closed(page, MODAL_TV)
        _open(page, MODAL_TV)
        _expect_open(page, MODAL_TV)
        assert _focus_inside(page, MODAL_TV)


# ── State transfer and history ───────────────────────────────────────────────


class TestStateTransfer:
    def test_a_to_b_transfer(self, page: Page, server_url: str) -> None:
        """Opening B while A is active closes A and opens B."""
        page.goto(f"{server_url}{CORRIDORS}")
        _open(page, MODAL_TV)
        _expect_open(page, MODAL_TV)
        page.evaluate(f"location.hash = '#{MODAL_RADIO}'")
        page.wait_for_timeout(150)
        # A is closed.
        assert page.locator(f"#{MODAL_TV}").evaluate(
            "el => !el.hasAttribute('aria-modal')"
        )
        # B is open with focus inside.
        _expect_open(page, MODAL_RADIO)
        assert _focus_inside(page, MODAL_RADIO)

    def test_forward_restores_enhanced_state(
        self, page: Page, server_url: str
    ) -> None:
        """Back then Forward reopens the overlay with enhanced state."""
        page.goto(f"{server_url}{CORRIDORS}")
        _open(page, MODAL_TV)
        _expect_open(page, MODAL_TV)
        page.go_back()
        _expect_closed(page, MODAL_TV)
        page.go_forward()
        page.wait_for_timeout(150)
        # Enhanced state restored.
        overlay = page.locator(f"#{MODAL_TV}")
        expect(overlay).to_be_visible()
        expect(overlay).to_have_attribute("aria-modal", "true")
        assert page.locator(".wrap").evaluate("el => el.hasAttribute('inert')")
        # Chromium's session-history focus restoration moves activeElement to
        # BODY after go_forward; Tab twice (past the skip-link) to confirm focus
        # enters the overlay (possible because .wrap is inert).
        page.keyboard.press("Tab")
        page.wait_for_timeout(40)
        page.keyboard.press("Tab")
        page.wait_for_timeout(40)
        assert _focus_inside(page, MODAL_TV)

    def test_dismiss_then_back_forward(
        self, page: Page, server_url: str
    ) -> None:
        """Escape dismissal creates a real history entry: Back reopens the
        overlay and Forward returns to the dismissed state."""
        page.goto(f"{server_url}{CORRIDORS}")
        _open(page, MODAL_TV)
        _expect_open(page, MODAL_TV)
        page.keyboard.press("Escape")  # dismisses → hash #dismissed (new entry)
        _expect_closed(page, MODAL_TV)
        page.go_back()  # back to #tv--modal → reopens enhanced
        _expect_open(page, MODAL_TV)
        page.go_forward()  # forward to #dismissed → closes again
        _expect_closed(page, MODAL_TV)


# ── Dense decks ──────────────────────────────────────────────────────────────


class TestDenseDecks:
    def test_room_deck_open_close(self, page: Page, server_url: str) -> None:
        """A room page with many overlays opens and closes cleanly."""
        page.goto(f"{server_url}{ROOM_1950S}")
        _open(page, MODAL_TV)
        _expect_open(page, MODAL_TV)
        page.keyboard.press("Escape")
        _expect_closed(page, MODAL_TV)

    def test_corridor_deck_open_close(self, page: Page, server_url: str) -> None:
        """The densest corridor page (249 overlays) opens and closes cleanly."""
        page.goto(f"{server_url}{CORRIDORS}")
        _open(page, MODAL_TV)
        _expect_open(page, MODAL_TV)
        page.go_back()
        _expect_closed(page, MODAL_TV)


# ── JavaScript disabled (CSS-only :target fallback) ──────────────────────────


class TestJavaScriptDisabled:
    def test_deep_link_visible_via_target(
        self, nojs_page: Page, server_url: str
    ) -> None:
        """CSS :target makes the overlay visible on deep-link load without JS."""
        nojs_page.goto(f"{server_url}{CORRIDORS}#{MODAL_TV}")
        expect(nojs_page.locator(f"#{MODAL_TV}")).to_be_visible()

    def test_close_button_no_js(self, nojs_page: Page, server_url: str) -> None:
        """Clicking .overlay-close (href='#dismissed') hides the overlay."""
        nojs_page.goto(f"{server_url}{CORRIDORS}#{MODAL_TV}")
        expect(nojs_page.locator(f"#{MODAL_TV}")).to_be_visible()
        nojs_page.locator(f"#{MODAL_TV} .overlay-close").click()
        expect(nojs_page.locator(f"#{MODAL_TV}")).not_to_be_visible()

    def test_backdrop_no_js(self, nojs_page: Page, server_url: str) -> None:
        """Clicking .overlay-backdrop hides the overlay without JS."""
        nojs_page.goto(f"{server_url}{CORRIDORS}#{MODAL_TV}")
        expect(nojs_page.locator(f"#{MODAL_TV}")).to_be_visible()
        nojs_page.locator(f"#{MODAL_TV} .overlay-backdrop").click(
            position={"x": 5, "y": 5}
        )
        expect(nojs_page.locator(f"#{MODAL_TV}")).not_to_be_visible()

    def test_back_forward_no_js(self, nojs_page: Page, server_url: str) -> None:
        """Browser back/forward tracks :target visibility without JS."""
        nojs_page.goto(f"{server_url}{CORRIDORS}")
        nojs_page.goto(f"{server_url}{CORRIDORS}#{MODAL_TV}")
        expect(nojs_page.locator(f"#{MODAL_TV}")).to_be_visible()
        nojs_page.go_back()
        expect(nojs_page.locator(f"#{MODAL_TV}")).not_to_be_visible()
        nojs_page.go_forward()
        expect(nojs_page.locator(f"#{MODAL_TV}")).to_be_visible()

    def test_no_false_aria_modal(self, nojs_page: Page, server_url: str) -> None:
        """No element carries aria-modal in the no-JS HTML."""
        nojs_page.goto(f"{server_url}{CORRIDORS}#{MODAL_TV}")
        count = nojs_page.evaluate(
            "document.querySelectorAll('[aria-modal=\"true\"]').length"
        )
        assert count == 0

    def test_content_present_without_js(
        self, nojs_page: Page, server_url: str
    ) -> None:
        """Fact marks and navigation links are present in the DOM without JS."""
        nojs_page.goto(f"{server_url}{CORRIDORS}")
        assert nojs_page.locator("[data-fact-id]").count() > 0
        assert nojs_page.locator(".museum-map a").count() > 0


# ── Responsive checks ────────────────────────────────────────────────────────


class TestResponsive:
    @pytest.mark.parametrize("width,height", VIEWPORTS)
    def test_no_horizontal_overflow_corridor(
        self, page: Page, server_url: str, width: int, height: int
    ) -> None:
        """Densest page (corridors) has no horizontal overflow at each viewport."""
        page.set_viewport_size({"width": width, "height": height})
        page.goto(f"{server_url}{CORRIDORS}")
        assert page.evaluate(
            "document.documentElement.scrollWidth <= "
            "document.documentElement.clientWidth + 1"
        )
        page.locator("details.pair-archive").evaluate("el => el.open = true")
        assert page.evaluate(
            "document.documentElement.scrollWidth <= "
            "document.documentElement.clientWidth + 1"
        )
        page.locator("details.pair-archive").evaluate("el => el.open = true")
        assert page.evaluate(
            "document.documentElement.scrollWidth <= "
            "document.documentElement.clientWidth + 1"
        )
        page.locator("details.pair-archive").evaluate("el => el.open = true")
        assert page.evaluate(
            "document.documentElement.scrollWidth <= "
            "document.documentElement.clientWidth + 1"
        )

    @pytest.mark.parametrize("width,height", VIEWPORTS)
    def test_no_horizontal_overflow_room(
        self, page: Page, server_url: str, width: int, height: int
    ) -> None:
        """Room page has no horizontal overflow at each viewport."""
        page.set_viewport_size({"width": width, "height": height})
        page.goto(f"{server_url}{ROOM_1950S}")
        assert page.evaluate(
            "document.documentElement.scrollWidth <= "
            "document.documentElement.clientWidth + 1"
        )

    def test_decade_nav_visible_mobile(self, page: Page, server_url: str) -> None:
        """Current decade is exposed in the room-map at mobile width."""
        page.set_viewport_size({"width": 375, "height": 667})
        page.goto(f"{server_url}{ROOM_1950S}")
        current = page.locator(".room-map a.on")
        expect(current).to_be_visible()

    def test_placard_fits_mobile(self, page: Page, server_url: str) -> None:
        """An open placard card fits within the mobile viewport."""
        page.set_viewport_size({"width": 375, "height": 667})
        page.goto(f"{server_url}{ROOM_1950S}")
        _open(page, MODAL_TV)
        expect(page.locator(f"#{MODAL_TV}")).to_be_visible()
        box = page.locator(f"#{MODAL_TV} .placard-card").bounding_box()
        assert box is not None
        assert box["x"] >= -1
        assert box["x"] + box["width"] <= 376

    @pytest.mark.parametrize("width,height", VIEWPORTS)
    def test_focused_control_within_viewport(
        self, page: Page, server_url: str, width: int, height: int
    ) -> None:
        """Tabbing through the lobby keeps focus within viewport width."""
        page.set_viewport_size({"width": width, "height": height})
        page.goto(f"{server_url}{LOBBY}")
        page.wait_for_timeout(100)
        for _ in range(5):
            page.keyboard.press("Tab")
            page.wait_for_timeout(30)
            box = page.evaluate(
                """() => {
                    const el = document.activeElement;
                    if (!el || el === document.body) return null;
                    const r = el.getBoundingClientRect();
                    return {left: r.left, right: r.right};
                }"""
            )
            if box is not None:
                assert box["left"] >= -1, f"focused element left={box['left']} < 0"
                assert box["right"] <= width + 1, (
                    f"focused element right={box['right']} > {width}"
                )


@pytest.mark.parametrize("width", [375, 1280])
@pytest.mark.parametrize("relative", ["rooms/jp-1950s.html", "rooms/jp-2010s.html",
                                     "collections/japan.html",
                                     "archive/sources/census-f08-allraces.html"])
def test_research_collections_fit_viewport(page: Page, server_url: str,
                                          width: int, relative: str) -> None:
    page.set_viewport_size({"width": width, "height": 812})
    page.goto(server_url + relative)
    assert page.evaluate("document.documentElement.scrollWidth <= window.innerWidth")


def test_artifact_card_opens_source_without_javascript(nojs_page: Page, server_url: str) -> None:
    nojs_page.goto(server_url + ROOM_1950S)
    nojs_page.locator(".object-catalogue > summary").click()
    nojs_page.locator(f'.artifact-card[href="#{MODAL_TV}"]').click()
    expect(nojs_page.locator(f'#{MODAL_TV}')).to_be_visible()


def test_japan_collection_observations_work_without_javascript(
    nojs_page: Page, server_url: str,
) -> None:
    nojs_page.set_viewport_size({"width": 375, "height": 812})
    nojs_page.goto(server_url + "collections/japan.html")
    lens = nojs_page.locator("#televisions")
    lens.locator("summary").click()
    fact_id = "jp-2010s-flat-tv"
    record = nojs_page.locator(f"#selection-{fact_id}")
    expect(record).to_contain_text("Observed 2009")
    expect(record).to_contain_text("Filed in the 2010s archive")
    record.locator(".observation-link").click()
    expect(nojs_page.locator(f"#{fact_id}--modal")).to_be_visible()
    assert nojs_page.evaluate("document.documentElement.scrollWidth <= window.innerWidth")
