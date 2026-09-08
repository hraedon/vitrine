"""Layout contracts at the boundaries shown in the owner's production screenshots."""

import pytest
import test_browser as browser_tests
from playwright.sync_api import Page, expect

from vitrine.site.curation.collections import HOUSE_ROOMS

browser_context_args = browser_tests.browser_context_args
nojs_page = browser_tests.nojs_page
server_url = browser_tests.server_url
site_dir = browser_tests.site_dir


@pytest.mark.parametrize("width", [375, 768, 1280, 1440])
def test_room_selector_stays_a_compact_horizontal_row(
    page: Page, server_url: str, width: int,
) -> None:
    page.set_viewport_size({"width": width, "height": 900})
    page.goto(server_url + "rooms/us-1900s.html")
    track = page.locator(".room-track")
    assert track.get_attribute("style") is None  # no CSP-sensitive inline column count
    boxes = page.locator(".room-track a").evaluate_all(
        "els => els.map(el => {const r=el.getBoundingClientRect(); "
        "return {top:r.top,height:r.height}})"
    )
    assert len(boxes) == 13
    assert max(b["top"] for b in boxes) - min(b["top"] for b in boxes) < 2
    assert track.bounding_box()["height"] < 90
    assert page.locator(".room-map").bounding_box()["height"] < 155
    # Native focus must reveal an offscreen decade inside the scrolling track.
    last = page.locator(".room-track a").last
    last.focus()
    box = last.bounding_box()
    bounds = track.bounding_box()
    assert box["x"] >= bounds["x"] - 1
    assert box["x"] + box["width"] <= bounds["x"] + bounds["width"] + 1


@pytest.mark.parametrize("width", [375, 768, 1280, 1440])
def test_each_decade_badge_fits_its_own_tile(page: Page, server_url: str, width: int) -> None:
    page.set_viewport_size({"width": width, "height": 900})
    page.goto(server_url + "index.html")
    bad = page.locator(".wing-decades a").evaluate_all("""els => els.flatMap(el => {
      const parent=el.getBoundingClientRect(); const issues=[];
      for (const child of el.querySelectorAll('small,span')) {
        const range=document.createRange(); range.selectNodeContents(child);
        for (const r of range.getClientRects()) {
          if (r.left < parent.left-1 || r.right > parent.right+1 ||
              r.top < parent.top-1 || r.bottom > parent.bottom+1) issues.push(el.textContent);
        }
      }
      return issues;
    })""")
    assert not bad


@pytest.mark.parametrize("width", [375, 1280, 1440])
def test_supported_house_is_visible_and_opens_a_source_without_js(
    nojs_page: Page, server_url: str, width: int,
) -> None:
    nojs_page.set_viewport_size({"width": width, "height": 900})
    nojs_page.goto(server_url + "rooms/us-1950s.html")
    house = nojs_page.locator(".house-experience .house")
    expect(house).to_be_visible()
    assert house.locator("xpath=ancestor::details").count() == 0
    for excluded in ("us-1950s-telephone-automobile", "us-1950s-food-basket"):
        assert house.locator(f'[data-fact-id="{excluded}"]').count() == 0
        assert nojs_page.locator(f'#{excluded}--modal').count() == 1
    assert nojs_page.locator(".room-disclaimer").inner_text().startswith("The composite family")
    nojs_page.locator('.house a[href="#us-1950s-tv-diffusion--modal"]').click()
    expect(nojs_page.locator("#us-1950s-tv-diffusion--modal")).to_be_visible()
    assert nojs_page.evaluate("document.documentElement.scrollWidth <= innerWidth")


@pytest.mark.parametrize("room", ["us-1910s", "us-1940s", "jp-1950s", "jp-2010s"])
def test_research_or_uneven_collections_do_not_get_an_empty_house(
    page: Page, server_url: str, room: str,
) -> None:
    page.goto(server_url + f"rooms/{room}.html")
    assert page.locator(".house-experience").count() == 0
    expect(page.locator(".room-disclaimer")).to_be_visible()
    expect(page.locator("#collection-records")).to_be_visible()


@pytest.mark.parametrize("width", [320, 375])
def test_mobile_objects_have_visible_finger_sized_source_links(
    nojs_page: Page, server_url: str, width: int,
) -> None:
    nojs_page.set_viewport_size({"width": width, "height": 900})
    nojs_page.goto(server_url + "rooms/us-1950s.html")
    links = nojs_page.locator(".house-object-links a")
    targets = set()
    for link in links.all():
        expect(link).to_be_visible()
        box = link.bounding_box()
        assert box["height"] >= 44 and box["width"] >= 44
        targets.add(link.get_attribute("href"))
    glyph_targets = nojs_page.locator(".house a:has(.hs)").evaluate_all(
        "els => els.map(el => el.getAttribute('href'))"
    )
    assert set(glyph_targets) <= targets
    nojs_page.locator('.house-object-links a[href="#us-1950s-tv-diffusion--modal"]').click()
    expect(nojs_page.locator("#us-1950s-tv-diffusion--modal")).to_be_visible()


def test_tablet_highlights_have_no_empty_grid_rows(page: Page, server_url: str) -> None:
    page.set_viewport_size({"width": 768, "height": 900})
    page.goto(server_url + "rooms/us-1950s.html")
    trail = page.locator(".house-highlights .story-trail").bounding_box()
    last = page.locator(".house-highlights .story-stop").last.bounding_box()
    assert abs(trail["y"] + trail["height"] - last["y"] - last["height"]) < 2


@pytest.mark.parametrize("width", [375, 768, 1280])
def test_house_objects_and_captions_clear_each_other_and_the_structure(
    page: Page, server_url: str, width: int,
) -> None:
    page.set_viewport_size({"width": width, "height": 900})
    for path in [*(f"rooms/{slug}.html" for slug in sorted(HOUSE_ROOMS)), "walkthrough.html"]:
        page.goto(server_url + path)
        problems = page.locator("svg.house").evaluate_all("""houses => houses.flatMap(svg => {
          const issues = [], scale = svg.getBoundingClientRect().width / 800;
          const point = (x,y) => new DOMPoint(x,y).matrixTransform(svg.getScreenCTM());
          const segments = [];
          for (const el of svg.querySelectorAll('.structure > *, .groundline')) {
            let points;
            if (el.tagName === 'polygon') points = Array.from(el.points, p => point(p.x,p.y));
            else if (el.tagName === 'rect') {
              const b = el.getBBox();
              points = [[b.x,b.y],[b.x+b.width,b.y],[b.x+b.width,b.y+b.height],
                [b.x,b.y+b.height]].map(([x,y]) => point(x,y));
            } else {
              segments.push([point(el.x1.baseVal.value,el.y1.baseVal.value),
                point(el.x2.baseVal.value,el.y2.baseVal.value)]); continue;
            }
            points.forEach((p,i) => segments.push([p,points[(i+1)%points.length]]));
          }
          const distance = (p,a,b) => {
            const dx=b.x-a.x, dy=b.y-a.y;
            const t=Math.max(0,Math.min(1,((p.x-a.x)*dx+(p.y-a.y)*dy)/(dx*dx+dy*dy)));
            return Math.hypot(p.x-a.x-t*dx,p.y-a.y-t*dy);
          };
          const overlaps = (a,b) => a.left < b.right && a.right > b.left &&
            a.top < b.bottom && a.bottom > b.top;
          const objects = [...svg.querySelectorAll('.hs')];
          const notes = [...svg.querySelectorAll('.znote,.zlabel')]
            .map(n=>n.getBoundingClientRect());
          objects.forEach((el,i) => {
            const id=el.dataset.factId, box=el.getBoundingClientRect();
            const ring=el.querySelector('.ring').getBoundingClientRect();
            const center={x:ring.x+ring.width/2,y:ring.y+ring.height/2};
            for (const [a,b] of segments) {
              if (distance(center,a,b)-ring.width/2 < 8*scale-0.2)
                issues.push(id+' circle near wall');
              const label=el.querySelector('.pct');
              if (label && getComputedStyle(label).display !== 'none') {
                const r=label.getBoundingClientRect();
                const corners=[[r.left,r.top],[r.right,r.top],[r.left,r.bottom],[r.right,r.bottom]];
                if (corners.some(([x,y]) => distance({x,y},a,b) < 8*scale-0.2))
                  issues.push(id+' caption near wall');
              }
            }
            for (const other of objects.slice(i+1))
              if (overlaps(box,other.getBoundingClientRect())) issues.push(id+' overlaps object');
            if (notes.some(note => overlaps(box,note))) issues.push(id+' overlaps annotation');
          });
          return issues;
        })""")
        assert not problems, (path, width, problems)
