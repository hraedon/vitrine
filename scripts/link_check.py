#!/usr/bin/env python3
"""Link checker for all source URLs in data/sources.toml.

Checks every source URL with a HEAD request, falls back to GET.
Categorizes failures as: genuine 404, bot-blocked (403/405),
or timeout.

Usage: python3 scripts/link_check.py [--verbose]
"""

from __future__ import annotations

import ssl
import sys
import tomllib
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


def load_sources() -> list[dict]:
    with open(REPO_ROOT / "data/sources.toml", "rb") as f:
        data = tomllib.load(f)
    return data.get("source", [])


def check_url(sid: str, url: str) -> tuple[str, str, int, str]:
    """Check a URL. Returns (source_id, url, status_code, message)."""
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
        return (sid, url, resp.status, "OK")
    except urllib.error.HTTPError as e:
        return (sid, url, e.code, f"HTTP {e.reason}")
    except Exception:
        try:
            req = urllib.request.Request(
                url, method="GET", headers=headers
            )
            resp = urllib.request.urlopen(
                req, timeout=15, context=ctx
            )
            return (sid, url, resp.status, "OK (GET)")
        except urllib.error.HTTPError as e:
            return (sid, url, e.code, f"HTTP {e.reason}")
        except Exception as e2:
            return (sid, url, 0, str(e2)[:80])


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
    ok = [r for r in results if r[2] in ok_codes]
    fail = [r for r in results if r[2] not in ok_codes]

    genuine_404 = [r for r in fail if r[2] == 404]
    bot_blocked = [r for r in fail if r[2] in (403, 405)]
    timeout = [
        r for r in fail if r[2] == 0 and "timeout" in r[3].lower()
    ]
    server_error = [r for r in fail if r[2] in (500, 503, 520)]
    other = [
        r for r in fail
        if r not in genuine_404
        and r not in bot_blocked
        and r not in timeout
        and r not in server_error
    ]

    print(f"Total: {len(results)}, OK: {len(ok)}, "
          f"Failed: {len(fail)}")
    print()

    if genuine_404:
        print(f"=== GENUINE 404 ({len(genuine_404)}) — must fix ===")
        for sid, url, status, _msg in sorted(genuine_404):
            print(f"  [{status}] {sid}")
            print(f"       {url}")
        print()

    if bot_blocked:
        count = len(bot_blocked)
        print(f"=== BOT-BLOCKED ({count}) — works in browser ===")
        for sid, url, status, _msg in sorted(bot_blocked):
            print(f"  [{status}] {sid}: {url[:80]}")
        print()

    if timeout:
        print(f"=== TIMEOUT ({len(timeout)}) — likely bot-block ===")
        for sid, url, status, _msg in sorted(timeout):
            print(f"  [{status}] {sid}: {url[:80]}")
        print()

    if server_error:
        count = len(server_error)
        print(f"=== SERVER ERROR ({count}) — transient ===")
        for sid, url, status, _msg in sorted(server_error):
            print(f"  [{status}] {sid}: {url[:80]}")
        print()

    if other:
        print(f"=== OTHER ({len(other)}) ===")
        for sid, url, status, msg in sorted(other):
            print(f"  [{status}] {sid}: {url[:80]} — {msg}")
        print()

    if verbose:
        print(f"=== ALL OK ({len(ok)}) ===")
        for sid, url, status, _msg in sorted(ok):
            print(f"  [{status}] {sid}: {url[:80]}")
        print()

    print("=== SUMMARY ===")
    print(f"URLs checked: {len(results)}")
    print(f"OK: {len(ok)}")
    print(f"Genuine 404 (must fix): {len(genuine_404)}")
    print(f"Bot-blocked: {len(bot_blocked)}")
    print(f"Timeout: {len(timeout)}")
    print(f"Server error: {len(server_error)}")
    print(f"Other: {len(other)}")
    return 1 if genuine_404 else 0


if __name__ == "__main__":
    sys.exit(main())
