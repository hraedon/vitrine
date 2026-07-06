#!/usr/bin/env python3
"""
IPUMS USA data extraction client for vitrine.

Rate-limited to 50 requests/minute (half the 100/min limit) to be a good citizen.

Usage:
    IPUMS_API_KEY=... python ipums_extract.py --submit  # submit an extract
    IPUMS_API_KEY=... python ipums_extract.py --status   # check extract status
    IPUMS_API_KEY=... python ipums_extract.py --download # download completed extract

Raw microdata is saved to samples/ (gitignored). Only aggregate statistics
computed from the microdata are published as Facts in data/.

See docs/ipums-compliance.md for compliance details.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path

import requests

# ── Configuration ───────────────────────────────────────────────────────────

API_BASE = "https://api.ipums.org"
RATE_LIMIT_DELAY = 1.2  # seconds between requests (50/min, half the 100/min limit)
SAMPLES_DIR = Path(__file__).parent.parent / "samples"

# ── Rate-limited HTTP client ───────────────────────────────────────────────


class IpumsClient:
    """Rate-limited IPUMS API client."""

    def __init__(self, api_key: str, collection: str = "usa"):
        self.api_key = api_key
        self.collection = collection
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": api_key,
            "Content-Type": "application/json",
        })
        self._last_request = 0.0

    def _throttle(self) -> None:
        """Enforce rate limit: wait at least RATE_LIMIT_DELAY between requests."""
        elapsed = time.monotonic() - self._last_request
        if elapsed < RATE_LIMIT_DELAY:
            time.sleep(RATE_LIMIT_DELAY - elapsed)
        self._last_request = time.monotonic()

    def _request(self, method: str, path: str, **kwargs) -> requests.Response:
        self._throttle()
        url = f"{API_BASE}{path}"
        r = self.session.request(method, url, timeout=30, **kwargs)
        if r.status_code == 429:
            retry_after = int(r.headers.get("Retry-After", 60))
            print(f"  Rate limited — waiting {retry_after}s...")
            time.sleep(retry_after)
            self._throttle()
            r = self.session.request(method, url, timeout=30, **kwargs)
        return r

    # ── Extract lifecycle ───────────────────────────────────────────────

    def list_extracts(self, limit: int = 10) -> list[dict]:
        """List previous extract requests."""
        r = self._request("GET", f"/extracts?collection={self.collection}&limit={limit}")
        r.raise_for_status()
        return r.json()

    def submit_extract(self, sample_ids: list[str], variables: list[str],
                       description: str = "", data_format: str = "csv") -> dict:
        """Submit a new extract request.

        Args:
            sample_ids: IPUMS sample IDs (e.g., ["us1950a"]).
            variables: IPUMS variable names (e.g., ["METRO", "INCTOT", "FAMSIZE"]).
            description: Human-readable description.
            data_format: "csv" or "fixed" or "stata" or "spss" or "sas".

        Returns:
            Extract definition dict with extractId.
        """
        body = {
            "dataStructure": {"rectangular": {"on": "P"}},
            "samples": {sid: {} for sid in sample_ids},
            "variables": {var: {} for var in variables},
            "description": description or f"vitrine extract: {', '.join(sample_ids)}",
            "dataFormat": data_format,
        }
        r = self._request(
            "POST",
            f"/extracts?collection={self.collection}",
            json=body,
        )
        if r.status_code not in (200, 201):
            raise RuntimeError(f"Submit failed ({r.status_code}): {r.text}")
        return r.json()

    def get_status(self, extract_id: int) -> dict:
        """Check the status of an extract."""
        r = self._request("GET", f"/extracts/{extract_id}?collection={self.collection}")
        r.raise_for_status()
        return r.json()

    def wait_for_completion(self, extract_id: int, poll_interval: int = 60,
                            max_wait: int = 3600) -> dict:
        """Poll until extract is complete or timeout.

        Args:
            extract_id: The extract ID to poll.
            poll_interval: Seconds between status checks.
            max_wait: Maximum seconds to wait.

        Returns:
            Final extract status dict.
        """
        elapsed = 0
        while elapsed < max_wait:
            status = self.get_status(extract_id)
            state = status.get("status", "unknown")
            print(f"  [{elapsed}s] Status: {state}")
            if state in ("completed", "complete"):
                return status
            if state in ("failed", "error", "canceled"):
                raise RuntimeError(f"Extract {extract_id} {state}: {status}")
            time.sleep(poll_interval)
            elapsed += poll_interval
        raise TimeoutError(f"Extract {extract_id} not completed after {max_wait}s")

    def download_extract(self, extract_id: int, dest_dir: Path | None = None) -> list[Path]:
        """Download all files from a completed extract.

        Returns:
            List of downloaded file paths.
        """
        if dest_dir is None:
            dest_dir = SAMPLES_DIR
        dest_dir.mkdir(parents=True, exist_ok=True)

        status = self.get_status(extract_id)
        if status.get("status") not in ("completed", "complete"):
            raise RuntimeError(f"Extract {extract_id} not completed: {status.get('status')}")

        downloaded = []
        for link in status.get("downloadLinks", []):
            url = link.get("url") if isinstance(link, dict) else link
            if not url:
                continue
            if isinstance(link, dict):
                filename = link.get("fileName", url.split("/")[-1])
            else:
                filename = url.split("/")[-1]
            dest = dest_dir / filename
            print(f"  Downloading {filename}...")
            self._throttle()
            r = self.session.get(url, timeout=300, stream=True)
            r.raise_for_status()
            with open(dest, "wb") as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
            downloaded.append(dest)
            print(f"    Saved to {dest} ({dest.stat().st_size:,} bytes)")
        return downloaded


# ── Vitrine extract definitions ────────────────────────────────────────────

# Variables needed for vitrine's locale split analysis
VITRINE_VARIABLES = {
    "income": ["INCTOT", "INCWAGE"],        # Total income, wage income
    "family": ["FAMSIZE", "RELATE", "NCHILD"],  # Family composition
    "geography": ["METRO", "URBAN", "REGION"],  # Locale classification
    "housing": ["OWNERSHP", "ROOMS", "PLUMBING", "ELECTRIC", "RADIO",
                "TV", "REFRIG", "PHONE", "AUTOS"],  # Housing/diffusion
    "work": ["HOURS", "WKSWORK1", "LABFORCE", "OCC"],  # Work hours/occupation
}

# Sample IDs by decade (IPUMS sample codes)
VITRINE_SAMPLES = {
    "1940": ["us1940a"],  # Full count
    "1950": ["us1950a"],  # Full count
    "1960": ["us1960a"],  # 1% sample
    "1970": ["us1970a"],  # 1% sample (Form 1)
    "1980": ["us1980a"],  # 5% sample
    "1990": ["us1990a"],  # 5% sample
    "2000": ["us2000a"],  # 5% sample
}


def build_vitrine_extract(decade: str, variables: list[str] | None = None) -> dict:
    """Build an extract request for a specific decade."""
    if decade not in VITRINE_SAMPLES:
        raise ValueError(f"Unknown decade: {decade}. Available: {list(VITRINE_SAMPLES.keys())}")
    sample_ids = VITRINE_SAMPLES[decade]
    if variables is None:
        # Flatten all variable groups
        variables = [v for group in VITRINE_VARIABLES.values() for v in group]
    return {"sample_ids": sample_ids, "variables": variables}


# ── CLI ────────────────────────────────────────────────────────────────────


def main():
    parser = argparse.ArgumentParser(description="IPUMS USA extraction client for vitrine")
    parser.add_argument("--submit", metavar="DECADE", help="Submit extract for decade (e.g., 1950)")
    parser.add_argument(
        "--status", type=int, metavar="EXTRACT_ID",
        help="Check extract status")
    parser.add_argument(
        "--download", type=int, metavar="EXTRACT_ID",
        help="Download completed extract")
    parser.add_argument("--list", action="store_true", help="List previous extracts")
    parser.add_argument("--test", action="store_true", help="Test API key validity")
    args = parser.parse_args()

    api_key = os.environ.get("IPUMS_API_KEY")
    if not api_key:
        # Try reading from .env
        env_path = Path.home() / ".hermes" / ".env"
        if env_path.exists():
            for line in env_path.read_text().splitlines():
                if line.startswith("IPUMS_API_KEY="):
                    api_key = line.split("=", 1)[1].strip()
                    break
    if not api_key:
        print("ERROR: IPUMS_API_KEY not found in environment or ~/.hermes/.env")
        sys.exit(1)

    client = IpumsClient(api_key)

    if args.test:
        print("Testing API key...")
        try:
            extracts = client.list_extracts(limit=1)
            print(f"✅ API key valid! Previous extracts: {len(extracts)}")
        except Exception as e:
            print(f"❌ API key invalid: {e}")
            sys.exit(1)

    elif args.list:
        print("Listing previous extracts...")
        extracts = client.list_extracts(limit=10)
        for ext in extracts:
            print(f"  ID: {ext.get('extractId', '?')}, Status: {ext.get('status', '?')}, "
                  f"Description: {ext.get('description', '?')[:60]}")

    elif args.submit:
        decade = args.submit
        print(f"Building extract for {decade}...")
        spec = build_vitrine_extract(decade)
        print(f"  Samples: {spec['sample_ids']}")
        print(f"  Variables: {', '.join(spec['variables'])}")
        print(f"  Rate limit: {RATE_LIMIT_DELAY}s between requests (50/min)")
        result = client.submit_extract(
            spec["sample_ids"], spec["variables"],
            description=f"vitrine: {decade} locale split + diffusion"
        )
        extract_id = result.get("extractId", result.get("id"))
        print(f"\n✅ Extract submitted! ID: {extract_id}")
        print(f"   Poll with: python {sys.argv[0]} --status {extract_id}")
        print(f"   Download with: python {sys.argv[0]} --download {extract_id}")

    elif args.status:
        print(f"Checking status of extract {args.status}...")
        status = client.get_status(args.status)
        print(f"  Status: {status.get('status', 'unknown')}")
        print(f"  Info: {json.dumps(status, indent=2)[:500]}")

    elif args.download:
        print(f"Downloading extract {args.download}...")
        files = client.download_extract(args.download)
        print(f"\n✅ Downloaded {len(files)} files:")
        for f in files:
            print(f"  {f} ({f.stat().st_size:,} bytes)")
        print(f"\nRaw data saved to {SAMPLES_DIR}/ (gitignored)")
        print("Compute aggregate statistics and publish as Tier B Facts.")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
