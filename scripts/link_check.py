#!/usr/bin/env python3
"""Link checker for all source URLs in data/sources.toml.

Checks every source URL with a HEAD request, falls back to GET.
Categorizes failures as: genuine 404, bot-blocked (403/405),
or timeout.

Sources may declare `expect = ["marker", ...]` (WI-023): the checker then
also downloads the document and verifies each marker appears in it — a
200 OK is not proof the URL serves the described document (the
census-f08-allraces f08a/f08ar incident, where the URL served the wrong
table variant with a 200). Text/HTML bodies are searched as decoded text;
.xlsx files are searched in their shared strings and sheet names (stdlib
zipfile). Formats opaque to stdlib extraction (PDFs, compressed streams)
stay resolve-only and say so.

Usage: python3 scripts/link_check.py [--verbose]
"""

from __future__ import annotations

import io
import ssl
import sys
import tomllib
import urllib.error
import urllib.request
import zipfile
from collections.abc import Sequence
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


def load_sources() -> list[dict]:
    with open(REPO_ROOT / "data/sources.toml", "rb") as f:
        data = tomllib.load(f)
    return data.get("source", [])


# ── Content verification (WI-023) ───────────────────────────────────────────


def _xlsx_text(body: bytes) -> str | None:
    """The searchable text inside an .xlsx: shared strings + sheet names."""
    try:
        with zipfile.ZipFile(io.BytesIO(body)) as zf:
            parts = []
            for name in ("xl/sharedStrings.xml", "xl/workbook.xml"):
                try:
                    parts.append(zf.read(name).decode("utf-8", errors="replace"))
                except KeyError:
                    continue
    except zipfile.BadZipFile:
        return None
    return "\n".join(parts) if parts else None


def searchable_text(url: str, body: bytes, content_type: str) -> str | None:
    """The text a marker search runs against, or None when the format is
    opaque to stdlib extraction (PDFs etc.) — those stay resolve-only."""
    path = url.lower().split("?")[0]
    if path.endswith(".xlsx") or "spreadsheetml" in content_type:
        return _xlsx_text(body)
    if (
        any(t in content_type for t in ("text/", "json", "xml", "html"))
        or path.endswith((".html", ".htm", ".txt", ".csv", ".xml", ".json"))
    ):
        return body.decode("utf-8", errors="replace")
    return None


def _normalize(text: str) -> str:
    """Markers match case/whitespace-insensitively."""
    return " ".join(text.split()).casefold()


def missing_markers(text: str, markers: Sequence[str]) -> list[str]:
    """The markers that do not appear in the served document's text."""
    haystack = _normalize(text)
    return [m for m in markers if _normalize(m) not in haystack]


# ── URL checking ─────────────────────────────────────────────────────────────

_UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"
_OK_CODES = {200, 301, 302, 303, 307, 308}


@dataclass
class Result:
    sid: str
    url: str
    status: int
    message: str
    missing: tuple[str, ...] = ()  # expect-markers absent from the served body


def _ssl_ctx() -> ssl.SSLContext:
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    return ctx


def _get(url: str, ctx: ssl.SSLContext) -> tuple[int, bytes, str]:
    req = urllib.request.Request(url, headers={"User-Agent": _UA})
    with urllib.request.urlopen(req, timeout=30, context=ctx) as resp:
        content_type = resp.headers.get("Content-Type", "")
        return resp.status, resp.read(), content_type


def check_url(sid: str, url: str, markers: Sequence[str] = ()) -> Result:
    """Check a URL, and its content when markers are declared."""
    ctx = _ssl_ctx()
    headers = {"User-Agent": _UA}
    try:
        req = urllib.request.Request(url, method="HEAD", headers=headers)
        with urllib.request.urlopen(req, timeout=15, context=ctx) as resp:
            status = resp.status
        if not markers:
            return Result(sid, url, status, "OK")
    except urllib.error.HTTPError as e:
        return Result(sid, url, e.code, f"HTTP {e.reason}")
    except Exception:
        try:
            req = urllib.request.Request(url, method="GET", headers=headers)
            with urllib.request.urlopen(req, timeout=15, context=ctx) as resp:
                status = resp.status
            if not markers:
                return Result(sid, url, status, "OK (GET)")
        except urllib.error.HTTPError as e:
            return Result(sid, url, e.code, f"HTTP {e.reason}")
        except Exception as e2:
            return Result(sid, url, 0, str(e2)[:80])

    if status not in _OK_CODES:
        return Result(sid, url, status, "unexpected status")
    try:
        _status, body, content_type = _get(url, ctx)
    except Exception as e:
        return Result(sid, url, 0, f"content fetch failed: {str(e)[:60]}")
    text = searchable_text(url, body, content_type)
    if text is None:
        return Result(sid, url, status, "OK (content check unsupported for this format)")
    missing = tuple(missing_markers(text, markers))
    if missing:
        return Result(sid, url, status, "content mismatch", missing)
    return Result(sid, url, status, "OK (content verified)")


def main() -> int:
    verbose = "--verbose" in sys.argv
    sources = load_sources()
    checks = [
        (s["id"], s["url"], tuple(s.get("expect", [])))
        for s in sources
        if s.get("url")
    ]

    print(f"Link checker: {len(checks)} URLs to check")
    print()

    results: list[Result] = []
    with ThreadPoolExecutor(max_workers=8) as executor:
        futures = {
            executor.submit(check_url, sid, url, markers): (sid, url)
            for sid, url, markers in checks
        }
        for future in as_completed(futures):
            results.append(future.result())

    ok = [r for r in results if r.status in _OK_CODES and not r.missing]
    mismatch = [r for r in results if r.missing]
    fail = [r for r in results if r.status not in _OK_CODES]

    genuine_404 = [r for r in fail if r.status == 404]
    bot_blocked = [r for r in fail if r.status in (403, 405)]
    timeout = [
        r
        for r in fail
        if r.status == 0
        and ("timeout" in r.message.lower() or "timed out" in r.message.lower())
    ]
    server_error = [r for r in fail if r.status in (500, 503, 520)]
    other = [
        r
        for r in fail
        if r not in genuine_404
        and r not in bot_blocked
        and r not in timeout
        and r not in server_error
    ]

    print(f"Total: {len(results)}, OK: {len(ok)}, Failed: {len(fail) + len(mismatch)}")
    print()

    if mismatch:
        print(f"=== CONTENT MISMATCH ({len(mismatch)}) — serves the wrong document? ===")
        for r in sorted(mismatch, key=lambda r: r.sid):
            print(f"  [{r.status}] {r.sid}: missing {list(r.missing)}")
            print(f"       {r.url}")
        print()

    if genuine_404:
        print(f"=== GENUINE 404 ({len(genuine_404)}) — must fix ===")
        for r in sorted(genuine_404, key=lambda r: r.sid):
            print(f"  [{r.status}] {r.sid}")
            print(f"       {r.url}")
        print()

    if bot_blocked:
        count = len(bot_blocked)
        print(f"=== BOT-BLOCKED ({count}) — works in browser ===")
        for r in sorted(bot_blocked, key=lambda r: r.sid):
            print(f"  [{r.status}] {r.sid}: {r.url[:80]}")
        print()

    if timeout:
        print(f"=== TIMEOUT ({len(timeout)}) — likely bot-block ===")
        for r in sorted(timeout, key=lambda r: r.sid):
            print(f"  [{r.status}] {r.sid}: {r.url[:80]}")
        print()

    if server_error:
        count = len(server_error)
        print(f"=== SERVER ERROR ({count}) — transient ===")
        for r in sorted(server_error, key=lambda r: r.sid):
            print(f"  [{r.status}] {r.sid}: {r.url[:80]}")
        print()

    if other:
        print(f"=== OTHER ({len(other)}) ===")
        for r in sorted(other, key=lambda r: r.sid):
            print(f"  [{r.status}] {r.sid}: {r.url[:80]} — {r.message}")
        print()

    if verbose:
        print(f"=== ALL OK ({len(ok)}) ===")
        for r in sorted(ok, key=lambda r: r.sid):
            print(f"  [{r.status}] {r.sid}: {r.url[:80]} — {r.message}")
        print()

    n_verified = sum(1 for r in ok if "content verified" in r.message)
    n_unsupported = sum(1 for r in results if "unsupported" in r.message)
    print("=== SUMMARY ===")
    print(f"URLs checked: {len(results)}")
    print(f"OK: {len(ok)}")
    print(f"Content mismatch (must fix): {len(mismatch)}")
    print(f"Genuine 404 (must fix): {len(genuine_404)}")
    print(f"Bot-blocked: {len(bot_blocked)}")
    print(f"Timeout: {len(timeout)}")
    print(f"Server error: {len(server_error)}")
    print(f"Other: {len(other)}")
    print(f"Content-verified: {n_verified}; content check unsupported: {n_unsupported}")
    return 1 if genuine_404 or mismatch else 0


if __name__ == "__main__":
    sys.exit(main())
