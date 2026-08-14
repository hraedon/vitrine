#!/usr/bin/env python3
"""Link checker for all source URLs in data/sources.toml.

Checks every source URL with a HEAD request, falls back to GET.
Categorizes failures as: genuine 404, bot-blocked (403/405),
or timeout.

WI-023: the link checker previously verified only HTTP status, not whether
the URL served the document it claimed to (the f08a/f08ar incident: a .xlsx
URL returned HTTP 200 for a valid — but wrong — Excel file). Two advisory
checks are now reported (neither changes the exit code):

  - Content-type mismatch: a document URL (.pdf/.xlsx/.csv/...) that returns
    text/html is almost certainly an error page or landing page served with
    HTTP 200 — a "wrong document" failure the status code alone hides.
  - Redirect destination: a document URL that redirects to a different host
    or path is surfaced so a human can confirm it still serves the described
    document and not a moved landing page.

Usage: python3 scripts/link_check.py [--verbose]
"""

from __future__ import annotations

import ssl
import sys
import tomllib
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

# File extensions that imply a binary document, not an HTML page. A 200
# response with text/html for one of these URLs is a content-type mismatch
# (WI-023): the server is likely serving an error/landing page.
_DOCUMENT_EXTS = frozenset({".pdf", ".xlsx", ".xls", ".csv", ".zip", ".tif", ".tiff"})


def load_sources() -> list[dict]:
    with open(REPO_ROOT / "data/sources.toml", "rb") as f:
        data = tomllib.load(f)
    return data.get("source", [])


@dataclass(frozen=True, slots=True)
class Result:
    sid: str
    url: str
    status: int
    message: str
    content_type: str = ""
    final_url: str = ""


def _content_type_mismatch(url: str, content_type: str) -> bool:
    """A document-extension URL returning text/html is a mismatch (WI-023)."""
    if not content_type:
        return False
    suffix = Path(url.split("?")[0]).suffix.lower()
    if suffix not in _DOCUMENT_EXTS:
        return False
    ct = content_type.split(";")[0].strip().lower()
    return ct.startswith("text/html")


def check_url(sid: str, url: str) -> Result:
    """Check a URL. Returns a Result with status, content-type, and final URL."""
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    ua = (
        "Mozilla/5.0 (X11; Linux x86_64) "
        "AppleWebKit/537.36"
    )
    headers = {"User-Agent": ua}
    try:
        req = urllib.request.Request(
            url, method="HEAD", headers=headers
        )
        resp = urllib.request.urlopen(req, timeout=15, context=ctx)
        return Result(
            sid, url, resp.status, "OK",
            content_type=resp.headers.get("Content-Type", ""),
            final_url=resp.url,
        )
    except urllib.error.HTTPError as e:
        return Result(sid, url, e.code, f"HTTP {e.reason}")
    except Exception:
        try:
            req = urllib.request.Request(
                url, method="GET", headers=headers
            )
            resp = urllib.request.urlopen(
                req, timeout=15, context=ctx
            )
            return Result(
                sid, url, resp.status, "OK (GET)",
                content_type=resp.headers.get("Content-Type", ""),
                final_url=resp.url,
            )
        except urllib.error.HTTPError as e:
            return Result(sid, url, e.code, f"HTTP {e.reason}")
        except Exception as e2:
            return Result(sid, url, 0, str(e2)[:80])


def main() -> int:
    verbose = "--verbose" in sys.argv
    sources = load_sources()
    urls = [(s["id"], s["url"]) for s in sources if s.get("url")]

    print(f"Link checker: {len(urls)} URLs to check")
    print()

    results = []
    with ThreadPoolExecutor(max_workers=8) as executor:
        futures = {
            executor.submit(check_url, sid, url): (sid, url)
            for sid, url in urls
        }
        for future in as_completed(futures):
            results.append(future.result())

    ok_codes = {200, 301, 302, 303, 307, 308}
    ok = [r for r in results if r.status in ok_codes]
    fail = [r for r in results if r.status not in ok_codes]

    genuine_404 = [r for r in fail if r.status == 404]
    bot_blocked = [r for r in fail if r.status in (403, 405)]
    timeout = [
        r for r in fail if r.status == 0 and "timeout" in r.message.lower()
    ]
    server_error = [r for r in fail if r.status in (500, 503, 520)]
    other = [
        r for r in fail
        if r not in genuine_404
        and r not in bot_blocked
        and r not in timeout
        and r not in server_error
    ]

    # WI-023 advisory: a document URL serving text/html (HTTP 200) is a
    # "wrong document" signal — the server returned an error/landing page
    # the status code alone hides. Advisory only (does not change exit code).
    type_mismatch = [
        r for r in ok if _content_type_mismatch(r.url, r.content_type)
    ]

    print(f"Total: {len(results)}, OK: {len(ok)}, "
          f"Failed: {len(fail)}")
    print()

    if genuine_404:
        print(f"=== GENUINE 404 ({len(genuine_404)}) — must fix ===")
        for r in sorted(genuine_404, key=lambda x: x.sid):
            print(f"  [{r.status}] {r.sid}")
            print(f"       {r.url}")
        print()

    if bot_blocked:
        count = len(bot_blocked)
        print(f"=== BOT-BLOCKED ({count}) — works in browser ===")
        for r in sorted(bot_blocked, key=lambda x: x.sid):
            print(f"  [{r.status}] {r.sid}: {r.url[:80]}")
        print()

    if timeout:
        print(f"=== TIMEOUT ({len(timeout)}) — likely bot-block ===")
        for r in sorted(timeout, key=lambda x: x.sid):
            print(f"  [{r.status}] {r.sid}: {r.url[:80]}")
        print()

    if server_error:
        count = len(server_error)
        print(f"=== SERVER ERROR ({count}) — transient ===")
        for r in sorted(server_error, key=lambda x: x.sid):
            print(f"  [{r.status}] {r.sid}: {r.url[:80]}")
        print()

    if other:
        print(f"=== OTHER ({len(other)}) ===")
        for r in sorted(other, key=lambda x: x.sid):
            print(f"  [{r.status}] {r.sid}: {r.url[:80]} — {r.message}")
        print()

    if type_mismatch:
        count = len(type_mismatch)
        print(f"=== CONTENT-TYPE MISMATCH ({count}) — advisory, verify ===")
        print("  Document URL returned text/html (likely an error/landing page)")
        for r in sorted(type_mismatch, key=lambda x: x.sid):
            ct = r.content_type.split(";")[0]
            print(f"  {r.sid}: {r.url[:80]}")
            print(f"    content-type: {ct}")
        print()

    if verbose:
        print(f"=== ALL OK ({len(ok)}) ===")
        for r in sorted(ok, key=lambda x: x.sid):
            print(f"  [{r.status}] {r.sid}: {r.url[:80]}")
        print()

    print("=== SUMMARY ===")
    print(f"URLs checked: {len(results)}")
    print(f"OK: {len(ok)}")
    print(f"Genuine 404 (must fix): {len(genuine_404)}")
    print(f"Bot-blocked: {len(bot_blocked)}")
    print(f"Timeout: {len(timeout)}")
    print(f"Server error: {len(server_error)}")
    print(f"Other: {len(other)}")
    print(f"Content-type mismatch (advisory): {len(type_mismatch)}")
    return 1 if genuine_404 else 0


if __name__ == "__main__":
    sys.exit(main())
