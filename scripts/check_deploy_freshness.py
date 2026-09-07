"""Compare the deployed museum against the corpus it should be serving.

The site is built into a container image on every push to main, but a running
Deployment does not re-pull a mutable tag on its own: ``imagePullPolicy:
Always`` governs the pull when a pod is *created*, not for pods already
running. Between 2026-07-13 and 2026-07-28 that left the public site serving a
build that was fifteen days and twenty facts behind main, with every CI signal
green — the image was built and pushed correctly, and nothing ever rolled it
out.

Pass the local build directory to compare the actual bytes of every page,
asset, and export with the live site. A fact-ID list alone cannot detect a
corrected value, changed citation, stale stylesheet, or mixed rollout.

Usage:
    python3 scripts/check_deploy_freshness.py _site
    python3 scripts/check_deploy_freshness.py _site --url https://vitrine.hraedon.com

The legacy facts-manifest.txt argument compares identifiers only and reports
ID MATCH, never a claim that the content is current.

Exit codes:
    0  all expected artifacts match (or IDs match in legacy mode)
    1  readable live artifacts differ from the local build
    2  local build or a live artifact could not be read

This is a read-time check of the expected artifacts, not an atomic snapshot
of the server or proof that no extra remote paths exist. A mixed rollout is
reported as a mismatch and should be checked again once deployment settles.

Unreachable is deliberately a *different* exit code from stale: "the museum is
down" and "the museum is showing last fortnight's exhibit" are different
problems with different responses, and collapsing them costs a diagnosis.
"""

from __future__ import annotations

import argparse
import sys
import urllib.error
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

DEFAULT_URL = "https://vitrine.hraedon.com"
MANIFEST_PATH = "/facts-manifest.txt"
TIMEOUT_SECONDS = 30


def compare_site(site: Path, base_url: str) -> int:
    """Verify every local build artifact against the bytes served to visitors.

    Paths come from the local build, never a remote file listing. Requests are
    bounded by the expected file size plus one byte, enough to detect larger
    responses without downloading arbitrary error pages in full.
    """
    if not (site / "index.html").is_file() or not (site / "facts-manifest.txt").is_file():
        print("built site needs index.html and facts-manifest.txt", file=sys.stderr)
        return 2
    paths = sorted(path for path in site.rglob("*") if path.is_file())

    def compare(path: Path) -> tuple[str, str]:
        relative = path.relative_to(site).as_posix()
        try:
            expected = path.read_bytes()
            url = base_url.rstrip("/") + "/" + urllib.parse.quote(relative, safe="/")
            request = urllib.request.Request(url, headers={
                "User-Agent": "vitrine-freshness-check",
                "Cache-Control": "no-cache",
                "Accept-Encoding": "identity",
            })
            with urllib.request.urlopen(request, timeout=TIMEOUT_SECONDS) as response:
                if response.status != 200:
                    return relative, f"UNAVAILABLE: HTTP {response.status}"
                actual = response.read(len(expected) + 1)
            return relative, "MATCH" if actual == expected else "DIFFERENT"
        except (OSError, urllib.error.URLError) as error:
            return relative, f"UNAVAILABLE: {error}"

    with ThreadPoolExecutor(max_workers=6) as pool:
        results = list(pool.map(compare, paths))
    failures = [(path, status) for path, status in results if status != "MATCH"]
    for path, status in failures:
        print(f"{status}: {path}")
    if failures:
        print(f"NOT VERIFIED: {len(failures)} of {len(paths)} build artifacts did not match")
        return 2 if any(status.startswith("UNAVAILABLE") for _, status in failures) else 1
    print(f"FRESH: {base_url} serves matching bytes for all {len(paths)} build artifacts")
    return 0


def _read_ids(text: str) -> set[str]:
    return {line.strip() for line in text.splitlines() if line.strip()}


def fetch_live_manifest(base_url: str) -> str:
    url = base_url.rstrip("/") + MANIFEST_PATH
    request = urllib.request.Request(url, headers={"User-Agent": "vitrine-freshness-check"})
    with urllib.request.urlopen(request, timeout=TIMEOUT_SECONDS) as response:
        if response.status != 200:
            raise OSError(f"{url} returned HTTP {response.status}")
        return response.read().decode("utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "built_manifest",
        type=Path,
        help="local build directory (exact bytes), or facts-manifest.txt (IDs only)",
    )
    parser.add_argument(
        "--url",
        default=DEFAULT_URL,
        help=f"deployed site (default: {DEFAULT_URL})",
    )
    args = parser.parse_args()

    if args.built_manifest.is_dir():
        return compare_site(args.built_manifest, args.url)

    try:
        built = _read_ids(args.built_manifest.read_text(encoding="utf-8"))
    except (OSError, UnicodeError) as error:
        print(f"cannot read built manifest: {error}", file=sys.stderr)
        return 2
    if not built:
        print("built manifest is empty — did `vitrine build` run?", file=sys.stderr)
        return 2

    try:
        live = _read_ids(fetch_live_manifest(args.url))
    except (OSError, urllib.error.URLError, UnicodeError) as error:
        print(f"UNREACHABLE: could not read the live manifest from {args.url}: {error}")
        return 2
    if not live:
        print(f"UNREACHABLE: {args.url} served an empty manifest")
        return 2

    missing = sorted(built - live)  # curated but not deployed
    extra = sorted(live - built)  # deployed but no longer in the corpus

    print(f"built: {len(built)} fact(s); live: {len(live)} fact(s)")

    if not missing and not extra:
        print(f"ID MATCH: {args.url} serves the expected exhibit identifiers")
        print("Values, citations and presentation were not checked. Pass the build directory.")
        return 0

    if missing:
        print(f"\n=== STALE ({len(missing)}) — curated but not deployed ===")
        for fact_id in missing[:40]:
            print(f"  {fact_id}")
        if len(missing) > 40:
            print(f"  … and {len(missing) - 40} more")
    if extra:
        print(f"\n=== ORPHANED ({len(extra)}) — deployed but absent from the corpus ===")
        for fact_id in extra[:40]:
            print(f"  {fact_id}")
        if len(extra) > 40:
            print(f"  … and {len(extra) - 40} more")

    print(
        "\nThe deployed site disagrees with the corpus. If main has moved, "
        "deploy it (scripts/deploy.sh). A running Deployment does not re-pull "
        "a mutable tag by itself."
    )
    return 1


if __name__ == "__main__":
    sys.exit(main())
