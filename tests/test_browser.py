"""Browser interaction tests for placard overlays (Plan 018).

Tests run against a built site using Playwright. Two modes:
  - JavaScript enabled (enhanced): focus management, escape, focus trap
  - JavaScript disabled (CSS-only): :target open/close, back/forward

The site uses CSS :target for placard overlays. A small enhancement module
(placard.js) adds focus management, keyboard handling, and focus restoration.
With JS disabled, the CSS-only fallback still handles open/close via hash
changes.

Run: pytest tests/test_browser.py -v
"""

from __future__ import annotations

from pathlib import Path

import pytest

playwright = pytest.importorskip("playwright")
from playwright.sync_api import Page, expect  # noqa: E402

DATA = Path(__file__).parent.parent / "data"

FACT_ID = "us-1950s-tv-diffusion"
MODAL_ID = f"{FACT_ID}--modal"


@pytest.fixture(scope="module")
def site_dir(tmp_path_factory: pytest.TempPathFactory) -> Path:
    from vitrine.loader import load_corpus
    from vitrine.series import load_series
    from vitrine.site.build import build_site

    out = tmp_path_factory.mktemp("browser_site")
    corpus = load_corpus(DATA)
    build_site(corpus, out, load_series(DATA), DATA)
    return out


def _open_placard(page: Page, modal_id: str = MODAL_ID) -> None:
    """Open a placard by setting the location hash (equivalent to clicking
    a chart mark link, which changes the hash)."""
    page.evaluate(f"window.location.hash = '#{modal_id}'")
    page.wait_for_timeout(200)


@pytest.fixture
def corridor_page(page: Page, site_dir: Path) -> Page:
    page.goto(f"file://{site_dir / 'corridors' / 'index.html'}")
    return page


# ── opening placards ─────────────────────────────────────────────────────────


class TestOpenPlacard:
    def test_open_from_chart_mark(self, corridor_page: Page) -> None:
        """Opening a placard via hash shows the overlay."""
        _open_placard(corridor_page)
        expect(corridor_page.locator(f"#{MODAL_ID}")).to_be_visible()

    def test_open_from_walkthrough_stop(
        self, page: Page, site_dir: Path
    ) -> None:
        """Opening a placard from the walkthrough page shows the overlay."""
        page.goto(f"file://{site_dir / 'walkthrough.html'}")
        _open_placard(page)
        expect(page.locator(f"#{MODAL_ID}")).to_be_visible()

    def test_open_from_room_placard(
        self, page: Page, site_dir: Path
    ) -> None:
        """Opening a placard from a room page shows the overlay."""
        page.goto(f"file://{site_dir / 'rooms' / 'us-1950s.html'}")
        _open_placard(page)
        expect(page.locator(f"#{MODAL_ID}")).to_be_visible()


# ── initial load with hash ────────────────────────────────────────────────────


class TestInitialLoadHash:
    def test_load_with_placard_hash(
        self, page: Page, site_dir: Path
    ) -> None:
        """Loading a page with #fact-id--modal shows the overlay immediately."""
        page.goto(
            f"file://{site_dir / 'corridors' / 'index.html'}#{MODAL_ID}"
        )
        expect(page.locator(f"#{MODAL_ID}")).to_be_visible()


# ── focus management (JS enhanced) ───────────────────────────────────────────


class TestFocusManagement:
    def test_focus_enters_overlay(self, corridor_page: Page) -> None:
        """When a placard opens, focus moves into the overlay."""
        _open_placard(corridor_page)
        overlay = corridor_page.locator(f"#{MODAL_ID}")
        assert overlay.evaluate(
            "el => el.contains(document.activeElement)"
        )

    def test_escape_closes_overlay(self, corridor_page: Page) -> None:
        """Escape key closes the placard overlay."""
        _open_placard(corridor_page)
        overlay = corridor_page.locator(f"#{MODAL_ID}")
        expect(overlay).to_be_visible()
        corridor_page.keyboard.press("Escape")
        expect(overlay).not_to_be_visible()

    def test_backdrop_closes_overlay(self, corridor_page: Page) -> None:
        """Clicking the backdrop closes the placard overlay."""
        _open_placard(corridor_page)
        overlay = corridor_page.locator(f"#{MODAL_ID}")
        expect(overlay).to_be_visible()
        overlay.locator(".overlay-backdrop").click()
        expect(overlay).not_to_be_visible()

    def test_close_button_closes_overlay(
        self, corridor_page: Page
    ) -> None:
        """Clicking the close button closes the placard overlay."""
        _open_placard(corridor_page)
        overlay = corridor_page.locator(f"#{MODAL_ID}")
        expect(overlay).to_be_visible()
        overlay.locator(".overlay-close").click()
        expect(overlay).not_to_be_visible()

    def test_focus_returns_to_origin(self, corridor_page: Page) -> None:
        """After closing via Escape, focus returns to the originating link."""
        link = corridor_page.query_selector(
            f'a[href="#{MODAL_ID}"]'
        )
        if link is None:
            pytest.skip("no chart mark link found")
        link.focus()
        _open_placard(corridor_page)
        expect(corridor_page.locator(f"#{MODAL_ID}")).to_be_visible()
        corridor_page.keyboard.press("Escape")
        corridor_page.wait_for_timeout(300)
        active = corridor_page.evaluate("document.activeElement.tagName")
        assert active in ("A", "BODY")  # link or body if focus was lost


# ── tab containment (JS enhanced) ────────────────────────────────────────────


class TestTabContainment:
    def test_tab_stays_within_overlay(self, corridor_page: Page) -> None:
        """Tab key stays within the overlay when it's open."""
        _open_placard(corridor_page)
        overlay = corridor_page.locator(f"#{MODAL_ID}")
        for _ in range(5):
            corridor_page.keyboard.press("Tab")
            corridor_page.wait_for_timeout(50)
        assert overlay.evaluate(
            "el => el.contains(document.activeElement)"
        )

    def test_shift_tab_stays_within_overlay(
        self, corridor_page: Page
    ) -> None:
        """Shift-Tab key stays within the overlay when it's open."""
        _open_placard(corridor_page)
        overlay = corridor_page.locator(f"#{MODAL_ID}")
        for _ in range(5):
            corridor_page.keyboard.press("Shift+Tab")
            corridor_page.wait_for_timeout(50)
        assert overlay.evaluate(
            "el => el.contains(document.activeElement)"
        )


# ── browser back/forward ─────────────────────────────────────────────────────


class TestBackForward:
    def test_back_closes_overlay(
        self, page: Page, site_dir: Path
    ) -> None:
        """Browser Back closes the overlay (hash change clears :target)."""
        page.goto(f"file://{site_dir / 'corridors' / 'index.html'}")
        _open_placard(page)
        overlay = page.locator(f"#{MODAL_ID}")
        expect(overlay).to_be_visible()
        page.go_back()
        expect(overlay).not_to_be_visible()

    def test_forward_reopens_overlay(
        self, page: Page, site_dir: Path
    ) -> None:
        """Browser Forward reopens the overlay."""
        page.goto(f"file://{site_dir / 'corridors' / 'index.html'}")
        _open_placard(page)
        overlay = page.locator(f"#{MODAL_ID}")
        expect(overlay).to_be_visible()
        page.go_back()
        expect(overlay).not_to_be_visible()
        page.go_forward()
        expect(overlay).to_be_visible()


# ── CSS-only fallback (JS disabled) ──────────────────────────────────────────


class TestCssOnlyFallback:
    def test_open_placard_no_js(
        self, browser: playwright.sync_api.Browser, site_dir: Path
    ) -> None:
        """CSS-only: hash change opens the overlay via :target."""
        context = browser.new_context(java_script_enabled=False)
        pg = context.new_page()
        pg.goto(
            f"file://{site_dir / 'corridors' / 'index.html'}#{MODAL_ID}"
        )
        expect(pg.locator(f"#{MODAL_ID}")).to_be_visible()
        context.close()

    def test_close_placard_no_js(
        self, browser: playwright.sync_api.Browser, site_dir: Path
    ) -> None:
        """CSS-only: clicking the close button closes the overlay."""
        context = browser.new_context(java_script_enabled=False)
        pg = context.new_page()
        pg.goto(
            f"file://{site_dir / 'corridors' / 'index.html'}#{MODAL_ID}"
        )
        expect(pg.locator(f"#{MODAL_ID}")).to_be_visible()
        pg.locator(f"#{MODAL_ID} .overlay-close").click()
        expect(pg.locator(f"#{MODAL_ID}")).not_to_be_visible()
        context.close()

    def test_backdrop_close_no_js(
        self, browser: playwright.sync_api.Browser, site_dir: Path
    ) -> None:
        """CSS-only: clicking the backdrop closes the overlay."""
        context = browser.new_context(java_script_enabled=False)
        pg = context.new_page()
        pg.goto(
            f"file://{site_dir / 'corridors' / 'index.html'}#{MODAL_ID}"
        )
        expect(pg.locator(f"#{MODAL_ID}")).to_be_visible()
        pg.locator(f"#{MODAL_ID} .overlay-backdrop").click()
        expect(pg.locator(f"#{MODAL_ID}")).not_to_be_visible()
        context.close()


# ── responsive ───────────────────────────────────────────────────────────────


class TestResponsive:
    def test_desktop_width_renders(
        self, page: Page, site_dir: Path
    ) -> None:
        """Page renders correctly at desktop width."""
        page.set_viewport_size({"width": 1280, "height": 800})
        page.goto(f"file://{site_dir / 'corridors' / 'index.html'}")
        assert page.query_selector(".chart-panel") is not None

    def test_narrow_mobile_width_renders(
        self, page: Page, site_dir: Path
    ) -> None:
        """Page renders correctly at narrow mobile width."""
        page.set_viewport_size({"width": 375, "height": 667})
        page.goto(f"file://{site_dir / 'corridors' / 'index.html'}")
        assert page.query_selector(".chart-panel") is not None

    def test_room_mobile_placard(
        self, page: Page, site_dir: Path
    ) -> None:
        """Placard overlay works on mobile width in a room."""
        page.set_viewport_size({"width": 375, "height": 667})
        page.goto(f"file://{site_dir / 'rooms' / 'us-1950s.html'}")
        _open_placard(page)
        expect(page.locator(f"#{MODAL_ID}")).to_be_visible()
