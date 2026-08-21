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
zipfile); PDFs are searched after unwrapping their FlateDecode content
streams (stdlib zlib) and collecting the strings their text operators
show. Formats that stay opaque — encrypted PDFs, image-only scans with no
text operators — fall back to resolve-only and say so.

Two further advisory checks are reported for OK URLs (neither changes the
exit code):

  - Content-type mismatch: a document URL (.pdf/.xlsx/.csv/...) that
    returns text/html is almost certainly an error or landing page served
    with HTTP 200 — a "wrong document" failure the status code alone hides.
  - Redirect destination: a URL whose final destination differs in host or
    path is surfaced so a human can confirm it still serves the described
    document and not a moved landing page.

Usage: python3 scripts/link_check.py [--verbose]
"""

from __future__ import annotations

import io
import re
import ssl
import sys
import tomllib
import urllib.error
import urllib.request
import zipfile
import zlib
from collections.abc import Sequence
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from pathlib import Path
from typing import Any, cast
from urllib.parse import urlsplit

REPO_ROOT = Path(__file__).resolve().parent.parent

# File extensions that imply a binary document, not an HTML page. A 200
# response with text/html for one of these URLs is a content-type mismatch
# (WI-023): the server is likely serving an error/landing page.
_DOCUMENT_EXTS = frozenset({".pdf", ".xlsx", ".xls", ".csv", ".zip", ".tif", ".tiff"})


def load_sources() -> list[dict[str, Any]]:
    with open(REPO_ROOT / "data/sources.toml", "rb") as f:
        data = tomllib.load(f)
    return cast("list[dict[str, Any]]", data.get("source", []))


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


# ── PDF text extraction (WI-023 remaining item a) ───────────────────────────
#
# A PDF's page text lives in content streams, usually compressed with
# FlateDecode — a raw substring search of the bytes sees only zlib noise.
# stdlib has no PDF parser, but it does have zlib: find each `stream...endstream`
# span, inflate the ones whose dictionary declares FlateDecode, and collect the
# byte strings shown by the text operators (Tj, TJ, ', "). What remains is an
# approximation of the rendered text — good enough to confirm a marker string
# ("Table F-8", a table title, a series name) is or is not in the document.

_STREAM_RE = re.compile(rb"stream\r?\n(.*?)endstream", re.DOTALL)
_SHOW_TOKEN_RE = re.compile(rb"[A-Za-z'\*\"]+")

# Streams larger than this are image/font binaries, not page text.
_MAX_SCANNED_STREAM = 2_000_000


def _inflate(data: bytes) -> bytes | None:
    """zlib-inflate with tolerance for trailing garbage after the stream."""
    try:
        return zlib.decompress(data)
    except zlib.error:
        pass
    try:
        return zlib.decompressobj().decompress(data)
    except zlib.error:
        return None


def _decode_pdf_string(raw: bytes) -> str:
    """Decode one PDF string per its own conventions.

    UTF-16BE strings carry a BOM; everything else is taken as PDFDocEncoding,
    which matches latin-1 for the ASCII range marker search cares about.
    """
    if raw.startswith(b"\xfe\xff"):
        return raw[2:].decode("utf-16-be", errors="replace")
    return raw.decode("latin-1")


def _unescape_pdf_literal(body: bytes) -> bytes:
    out = bytearray()
    i = 0
    while i < len(body):
        ch = body[i]
        if ch != 0x5C or i + 1 >= len(body):  # backslash
            out.append(ch)
            i += 1
            continue
        nxt = body[i + 1]
        simple = {0x6E: b"\n", 0x72: b"\r", 0x74: b"\t", 0x62: b"\b", 0x66: b"\f"}
        if nxt in simple:
            out += simple[nxt]
            i += 2
        elif nxt in (0x28, 0x29, 0x5C):  # ( ) \
            out.append(nxt)
            i += 2
        elif 0x30 <= nxt <= 0x37:  # octal escape, up to 3 digits
            j = i + 1
            digits = bytearray()
            while j < len(body) and len(digits) < 3 and 0x30 <= body[j] <= 0x37:
                digits.append(body[j])
                j += 1
            out.append(int(digits, 8) & 0xFF)
            i = j
        elif nxt in (0x0A, 0x0D):  # line continuation: escaped EOL vanishes
            i += 2 if nxt == 0x0D and body[i + 2 : i + 3] == b"\n" else 1
            i += 1
        else:
            out.append(nxt)
            i += 2
    return bytes(out)


def _scan_pdf_literal(content: bytes, i: int) -> tuple[bytes | None, int]:
    """Read one literal string starting at content[i] == '('.

    Returns (raw bytes between the outer parens, index past the closing
    paren) — escapes are kept verbatim for _unescape_pdf_literal — or
    (None, len(content)) when the string never terminates. Balanced nested
    parens are part of PDF string syntax and must not end the string.
    """
    depth = 1
    j = i + 1
    buf = bytearray()
    while j < len(content):
        c = content[j]
        if c == 0x5C:  # backslash: copy escape verbatim so \( \) stay escaped
            buf += content[j : j + 2]
            j += 2
            continue
        if c == 0x28:  # (
            depth += 1
        elif c == 0x29:  # )
            depth -= 1
            if depth == 0:
                return bytes(buf), j + 1
        buf.append(c)
        j += 1
    return None, len(content)


def _pdf_show_strings(content: bytes) -> list[str]:
    """The decoded strings shown by one content stream's text operators.

    A linear character scanner rather than a regex: content streams share
    the file with font-program binaries whose byte soup sends a
    backtracking regex into catastrophic runtimes (a real Census PDF hung
    on this). Strings accumulate as they appear; the show operators Tj,
    TJ, ' and " flush them. Any other operator outside a TJ array drops
    pending strings so operands of unrelated operators can't leak forward.
    """
    strings: list[str] = []
    pending: list[str] = []  # strings seen since the last operator/array close
    depth = 0  # nesting inside a [ ... ] TJ array
    i = 0
    n = len(content)
    while i < n:
        c = content[i]
        if c == 0x28:  # ( literal string
            raw, i = _scan_pdf_literal(content, i)
            if raw is not None:
                pending.append(_decode_pdf_string(_unescape_pdf_literal(raw)))
            continue
        if c == 0x3C:  # < hex string (but << is a dictionary)
            if content[i + 1 : i + 2] == b"<":
                i += 2
                continue
            end = content.find(b">", i + 1)
            if end == -1:
                break
            nibbles = re.sub(rb"[^0-9A-Fa-f]", b"", content[i + 1 : end])
            if len(nibbles) % 2:
                nibbles += b"0"
            pending.append(_decode_pdf_string(bytes.fromhex(nibbles.decode())))
            i = end + 1
            continue
        if c == 0x5B:  # [ open array
            depth += 1
            i += 1
            continue
        if c == 0x5D:  # ] close array
            depth = max(0, depth - 1)
            i += 1
            continue
        if 0x41 <= c <= 0x5A or 0x61 <= c <= 0x7A or c in (0x27, 0x22, 0x2A):
            m = _SHOW_TOKEN_RE.match(content, i)
            if m is None:  # unreachable: the branch condition guarantees a match
                i += 1
                continue
            token = m.group(0)
            i = m.end()
            if token in (b"Tj", b"'", b'"'):
                if pending:
                    strings.append(pending[-1])
                    pending.clear()
            elif token == b"TJ":
                strings.extend(pending)
                pending.clear()
            elif depth == 0:
                pending.clear()
            continue
        i += 1
    return strings


def _pdf_text(body: bytes) -> str | None:
    """The searchable text of a PDF, or None when extraction cannot run.

    None means "opaque to this extractor": not a PDF at all, unreadable
    streams (e.g. encrypted), no text operators anywhere (an image-only
    scan), or output dominated by non-printable bytes (embedded font
    programs are FlateDecode streams too, and subset-font encodings turn
    otherwise-real text into mojibake). Declared markers on such documents
    stay unverifiable rather than failing on a false positive.
    """
    if not body.startswith(b"%PDF"):
        return None
    variants: set[str] = set()
    for m in _STREAM_RE.finditer(body):
        stream = m.group(1)
        dict_start = max(0, m.start() - 400)
        if b"FlateDecode" not in body[dict_start : m.start()]:
            content = stream
        else:
            inflated = _inflate(stream.rstrip(b"\r\n"))
            if inflated is None:
                continue
            content = inflated
        if len(content) > _MAX_SCANNED_STREAM:
            # Image and font streams dwarf page text; scanning hundreds of
            # megabytes of binary buys nothing (and any real text lost this
            # way only demotes the document to resolve-only, never to a
            # false mismatch).
            continue
        if not (b"Tj" in content or b"TJ" in content):
            # Emission requires a show operator somewhere; image/font
            # binaries without one are skipped at C speed instead of
            # paying the Python scanner.
            continue
        strings = _pdf_show_strings(content)
        if not strings:
            continue
        # Words can be split across show operators ("(Medi)(an)" via TJ kerning)
        # and operators can each hold whole words; search both joins.
        joined_direct = "".join(strings)
        joined_spaced = " ".join(strings)
        for candidate in (joined_direct, joined_spaced):
            # A fragment too short to be page text (a stray operator in a
            # font binary) is noise: treating it as the document's text
            # would accuse markers of being missing. Say opaque instead.
            if len(candidate) < 16:
                continue
            printable = sum(
                1 for ch in candidate if ch.isprintable() or ch in " \t\n\r"
            )
            if printable / len(candidate) >= 0.9:
                variants.add(candidate)
    return "\n".join(sorted(variants)) or None


def searchable_text(url: str, body: bytes, content_type: str) -> str | None:
    """The text a marker search runs against, or None when the format is
    opaque to stdlib extraction (encrypted PDFs, image-only scans etc.) —
    those stay resolve-only."""
    path = url.lower().split("?")[0]
    if path.endswith(".pdf") or "pdf" in content_type:
        return _pdf_text(body)
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


# ── Advisory signals (WI-023) ───────────────────────────────────────────────


def content_type_mismatch(url: str, content_type: str) -> bool:
    """A document-extension URL returning text/html is a mismatch."""
    if not content_type:
        return False
    suffix = Path(url.split("?")[0]).suffix.lower()
    if suffix not in _DOCUMENT_EXTS:
        return False
    ct = content_type.split(";")[0].strip().lower()
    return ct.startswith("text/html")


def redirected_elsewhere(url: str, final_url: str) -> bool:
    """True when the final destination differs in host or path.

    Trailing slashes are ignored (canonical redirects); query strings are
    ignored (session parameters). Advisory only — the point is to surface
    destination drift for a human to confirm.
    """
    if not final_url or final_url == url:
        return False
    a, b = urlsplit(url), urlsplit(final_url)
    if (a.hostname or "") != (b.hostname or ""):
        return True
    return a.path.rstrip("/") != b.path.rstrip("/")


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
    content_type: str = ""
    final_url: str = ""


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
            head_type = resp.headers.get("Content-Type", "")
            final_url = resp.url
        if not markers:
            return Result(
                sid, url, status, "OK",
                content_type=head_type, final_url=final_url,
            )
    except urllib.error.HTTPError as e:
        return Result(sid, url, e.code, f"HTTP {e.reason}")
    except Exception:
        try:
            req = urllib.request.Request(url, method="GET", headers=headers)
            with urllib.request.urlopen(req, timeout=15, context=ctx) as resp:
                status = resp.status
                head_type = resp.headers.get("Content-Type", "")
                final_url = resp.url
            if not markers:
                return Result(
                    sid, url, status, "OK (GET)",
                    content_type=head_type, final_url=final_url,
                )
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
        return Result(
            sid, url, status, "OK (content check unsupported for this format)",
            content_type=content_type,
        )
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

    # WI-023 advisories (do not change the exit code): a document URL
    # serving text/html, or one whose redirect landed on a different host
    # or path, is surfaced for a human to verify.
    type_mismatch = [
        r for r in ok if content_type_mismatch(r.url, r.content_type)
    ]
    redirected = [
        r for r in ok if redirected_elsewhere(r.url, r.final_url)
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

    if type_mismatch:
        count = len(type_mismatch)
        print(f"=== CONTENT-TYPE MISMATCH ({count}) — advisory, verify ===")
        print("  Document URL returned text/html (likely an error/landing page)")
        for r in sorted(type_mismatch, key=lambda r: r.sid):
            ct = r.content_type.split(";")[0]
            print(f"  {r.sid}: {r.url[:80]}")
            print(f"    content-type: {ct}")
        print()

    if redirected:
        count = len(redirected)
        print(f"=== REDIRECTED ({count}) — advisory, verify ===")
        print("  Final destination differs in host or path from the registered URL")
        for r in sorted(redirected, key=lambda r: r.sid):
            print(f"  {r.sid}:")
            print(f"    registered: {r.url[:90]}")
            print(f"    final:      {r.final_url[:90]}")
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
    print(f"Content-type mismatch (advisory): {len(type_mismatch)}")
    print(f"Redirected elsewhere (advisory): {len(redirected)}")
    print(f"Content-verified: {n_verified}; content check unsupported: {n_unsupported}")
    return 1 if genuine_404 or mismatch else 0


if __name__ == "__main__":
    sys.exit(main())
