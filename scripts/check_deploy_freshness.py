"""Compare the deployed museum against the corpus it should be serving.

The site is built into a container image on every push to main, but a running
Deployment does not re-pull a mutable tag on its own: ``imagePullPolicy:
Always`` governs the pull when a pod is *created*, not for pods already
running. Between 2026-07-13 and 2026-07-28 that left the public site serving a
build that was fifteen days and twenty facts behind main, with every CI signal
green — the image was built and pushed correctly, and nothing ever rolled it
out.

This check closes that blind spot the same way ``link_check.py`` closes the
citation one: by comparing the claim against the artifact. ``facts-manifest.txt``
is the site's own list of every fact id it rendered, so a diff between the
manifest built from the corpus and the manifest the live site serves is an
exact, order-insensitive answer to "is what visitors see what we curated?"

Usage:
    python3 scripts/check_deploy_freshness.py _site/facts-manifest.txt
    python3 scripts/check_deploy_freshness.py _site/facts-manifest.txt \
        --url https://vitrine.hraedon.com

Exit codes:
    0  live site matches the built corpus
    1  live site is stale or ahead (a real drift — deploy, or investigate)
    2  live site could not be read (unreachable, non-200, or empty)

Unreachable is deliberately a *different* exit code from stale: "the museum is
down" and "the museum is showing last fortnight's exhibit" are different
problems with different responses, and collapsing them costs a diagnosis.
"""

from __future__ import annotations

import argparse
import sys
import urllib.error
import urllib.request
from pathlib import Path

DEFAULT_URL = "https://vitrine.hraedon.com"
MANIFEST_PATH = "/facts-manifest.txt"
TIMEOUT_SECONDS = 30


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
        help="facts-manifest.txt from a local `vitrine build` of the current corpus",
    )
    parser.add_argument(
        "--url",
        default=DEFAULT_URL,
        help=f"deployed site (default: {DEFAULT_URL})",
    )
    args = parser.parse_args()

    try:
        built = _read_ids(args.built_manifest.read_text(encoding="utf-8"))
    except OSError as error:
        print(f"cannot read built manifest: {error}", file=sys.stderr)
        return 2
    if not built:
        print("built manifest is empty — did `vitrine build` run?", file=sys.stderr)
        return 2

    try:
        live = _read_ids(fetch_live_manifest(args.url))
    except (OSError, urllib.error.URLError) as error:
        print(f"UNREACHABLE: could not read the live manifest from {args.url}: {error}")
        return 2
    if not live:
        print(f"UNREACHABLE: {args.url} served an empty manifest")
        return 2

    missing = sorted(built - live)  # curated but not deployed
    extra = sorted(live - built)  # deployed but no longer in the corpus

    print(f"built: {len(built)} fact(s); live: {len(live)} fact(s)")

    if not missing and not extra:
        print(f"FRESH: {args.url} serves exactly the current corpus")
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
