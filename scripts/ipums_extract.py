"""IPUMS extract API v2 client; raw downloads belong in ignored samples/.

This tool does not submit a request unless explicitly invoked with --submit.
Read docs/ipums-compliance.md before using IPUMS material.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import tempfile
import time
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import unquote, urlencode, urlsplit
from urllib.request import HTTPRedirectHandler, Request, build_opener

API_BASE = "https://api.ipums.org"
RATE_LIMIT_DELAY = 1.2
SAMPLES_DIR = Path(__file__).parent.parent / "samples"


class _NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):  # type: ignore[no-untyped-def]
        return None


def _open(request: Request):  # type: ignore[no-untyped-def]
    try:
        return build_opener(_NoRedirect).open(request, timeout=30)
    except HTTPError as exc:
        raise RuntimeError(f"HTTP request failed (status {exc.code})") from None
    except (URLError, OSError, ValueError):
        raise RuntimeError("HTTP request failed") from None


def _safe_download(url: str, collection: str, number: int) -> str:
    parts = urlsplit(url)
    host = (parts.hostname or "").lower()
    try:
        port = parts.port
    except ValueError:
        raise ValueError("Invalid download location") from None
    if (
        parts.scheme != "https"
        or not (host == "ipums.org" or host.endswith(".ipums.org"))
        or parts.username is not None
        or parts.password is not None
        or port not in (None, 443)
    ):
        raise ValueError("Invalid download location")
    path = unquote(parts.path)
    if "\\" in path or any(p in (".", "..") for p in path.split("/")):
        raise ValueError("Invalid download path")
    name = path.rsplit("/", 1)[-1]
    stem = re.escape(f"{collection}_{number:05d}")
    if not re.fullmatch(stem + r"\.(?:csv\.gz|dat\.gz|csv|dat|xml|cbk|do|sas|sps|sts|R|txt)", name):
        raise ValueError("Invalid extract filename")
    return name


def _safe_directory(path: Path) -> Path:
    absolute = path.absolute()
    for part in (absolute, *absolute.parents):
        if part.is_symlink():
            raise ValueError("Destination must not contain symbolic links")
    absolute.mkdir(parents=True, exist_ok=True)
    return absolute


class IpumsClient:
    """Rate-limited client with origin- and path-restricted download authentication."""

    def __init__(self, api_key: str, collection: str = "usa"):
        if not re.fullmatch(r"[a-z0-9]+", collection):
            raise ValueError("Invalid collection")
        self.api_key = api_key
        self.collection = collection
        self._last_request = 0.0

    def _throttle(self) -> None:
        remaining = RATE_LIMIT_DELAY - (time.monotonic() - self._last_request)
        if remaining > 0:
            time.sleep(remaining)
        self._last_request = time.monotonic()

    def _request(self, method: str, path: str, *, body: dict | None = None) -> object:
        self._throttle()
        query = {"collection": self.collection, "version": "2"}
        path, _, extra = path.partition("?")
        if extra:
            from urllib.parse import parse_qsl

            query.update(dict(parse_qsl(extra)))
        request = Request(
            API_BASE + path + "?" + urlencode(query),
            data=None if body is None else json.dumps(body).encode("utf-8"),
            headers={"Authorization": self.api_key, "Content-Type": "application/json"},
            method=method,
        )
        try:
            with _open(request) as response:
                return json.load(response)
        except (json.JSONDecodeError, UnicodeDecodeError, OSError):
            raise RuntimeError("Invalid API response") from None

    def list_extracts(self, limit: int = 10) -> list[dict]:
        if limit < 1 or limit > 100:
            raise ValueError("Invalid page size")
        result = self._request("GET", f"/extracts?pageSize={limit}")
        if isinstance(result, dict):
            result = result.get("data")
        if not isinstance(result, list) or not all(isinstance(item, dict) for item in result):
            raise RuntimeError("Invalid API response")
        return result

    def submit_extract(
        self,
        sample_ids: list[str],
        variables: list[str],
        description: str = "",
        data_format: str = "csv",
    ) -> dict:
        body = {
            "dataStructure": {"rectangular": {"on": "P"}},
            "samples": {sid: {} for sid in sample_ids},
            "variables": {var: {} for var in variables},
            "description": description or "vitrine extract",
            "dataFormat": data_format,
        }
        result = self._request("POST", "/extracts", body=body)
        if not isinstance(result, dict):
            raise RuntimeError("Invalid API response")
        return result

    def get_status(self, extract_id: int) -> dict:
        if extract_id < 1:
            raise ValueError("Invalid extract number")
        result = self._request("GET", f"/extracts/{extract_id}")
        if not isinstance(result, dict):
            raise RuntimeError("Invalid API response")
        return result

    def wait_for_completion(
        self, extract_id: int, poll_interval: int = 60, max_wait: int = 3600
    ) -> dict:
        if not 1 <= poll_interval <= 60 or max_wait < 0:
            raise ValueError("Invalid polling interval")
        deadline = time.monotonic() + max_wait
        while time.monotonic() < deadline:
            result = self.get_status(extract_id)
            state = result.get("status")
            if state in ("completed", "complete"):
                return result
            if state in ("failed", "error", "canceled"):
                raise RuntimeError("Extract failed")
            time.sleep(min(poll_interval, max(0, deadline - time.monotonic())))
        raise TimeoutError("Extract did not complete before the deadline")

    def download_extract(self, extract_id: int, dest_dir: Path | None = None) -> list[Path]:
        status = self.get_status(extract_id)
        if status.get("status") not in ("completed", "complete"):
            raise RuntimeError("Extract is not complete")
        definition = status.get("extractDefinition", {})
        links = status.get(
            "downloadLinks",
            definition.get("downloadLinks") if isinstance(definition, dict) else None,
        )
        if not isinstance(links, dict) or not links:
            raise RuntimeError("Invalid download metadata")
        directory = _safe_directory(dest_dir or SAMPLES_DIR)
        downloaded = []
        for item in links.values():
            if not isinstance(item, dict) or not isinstance(item.get("url"), str):
                raise RuntimeError("Invalid download metadata")
            name = _safe_download(item["url"], self.collection, extract_id)
            size, digest = item.get("bytes"), item.get("sha256")
            if size is not None and (
                not isinstance(size, int) or isinstance(size, bool) or size < 0
            ):
                raise RuntimeError("Invalid download metadata")
            if digest is not None and (
                not isinstance(digest, str) or not re.fullmatch(r"[a-fA-F0-9]{64}", digest)
            ):
                raise RuntimeError("Invalid download metadata")
            dest = directory / name
            if dest.exists() or dest.is_symlink():
                raise FileExistsError("Download destination already exists")
            self._throttle()
            parts = urlsplit(item["url"])
            protected_path = (
                rf"/downloads/{re.escape(self.collection)}/api/v1/extracts/"
                rf"[0-9]+/{re.escape(name)}"
            )
            headers = {}
            if f"{parts.scheme}://{parts.netloc}" == API_BASE and re.fullmatch(
                protected_path, parts.path
            ):
                headers["Authorization"] = self.api_key
            request = Request(item["url"], headers=headers, method="GET")
            tmp = None
            try:
                with (
                    _open(request) as response,
                    tempfile.NamedTemporaryFile(dir=directory, delete=False) as out,
                ):
                    tmp = Path(out.name)
                    hasher = hashlib.sha256()
                    count = 0
                    while chunk := response.read(65536):
                        count += len(chunk)
                        if size is not None and count > size:
                            raise RuntimeError("Download size mismatch")
                        hasher.update(chunk)
                        out.write(chunk)
                if size is not None and count != size:
                    raise RuntimeError("Download size mismatch")
                if digest is not None and hasher.hexdigest() != digest.lower():
                    raise RuntimeError("Download digest mismatch")
                os.link(tmp, dest)
                downloaded.append(dest)
            except FileExistsError:
                raise FileExistsError("Download destination already exists") from None
            except OSError:
                raise RuntimeError("Download failed") from None
            finally:
                if tmp is not None:
                    tmp.unlink(missing_ok=True)
        return downloaded


VITRINE_VARIABLES = {
    "income": ["INCTOT", "INCWAGE"],
    "family": ["FAMSIZE", "RELATE", "NCHILD"],
    "geography": ["METRO", "URBAN", "REGION"],
    "housing": [
        "OWNERSHP",
        "ROOMS",
        "PLUMBING",
        "ELECTRIC",
        "RADIO",
        "TV",
        "REFRIG",
        "PHONE",
        "AUTOS",
    ],
    "work": ["HOURS", "WKSWORK1", "LABFORCE", "OCC"],
}
VITRINE_SAMPLES = {str(y): [f"us{y}a"] for y in (1940, 1950, 1960, 1970, 1980, 1990, 2000)}


def build_1950_family_income_extract() -> dict:
    """1950 sample-line family income, referring to income in 1949."""
    return {
        "sample_ids": ["us1950a"],
        "variables": [
            "YEAR",
            "SAMPLE",
            "SERIAL",
            "PERNUM",
            "GQ",
            "FAMUNIT",
            "FAMSIZE",
            "RELATE",
            "METRO",
            "FTOTINC",
            "SLWT",
        ],
    }


def build_vitrine_extract(decade: str, variables: list[str] | None = None) -> dict:
    if decade not in VITRINE_SAMPLES:
        raise ValueError("Unknown decade")
    if decade == "1950" and variables is None:
        raise ValueError("Choose explicit 1950 variables or the 1950-family-income extract")
    return {
        "sample_ids": VITRINE_SAMPLES[decade],
        "variables": variables
        if variables is not None
        else [v for group in VITRINE_VARIABLES.values() for v in group],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="IPUMS USA API v2 client")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--submit", metavar="DECADE_OR_1950-family-income")
    group.add_argument("--status", type=int)
    group.add_argument("--download", type=int)
    group.add_argument("--list", action="store_true")
    group.add_argument("--test", action="store_true")
    args = parser.parse_args()
    if not any((args.submit, args.status, args.download, args.list, args.test)):
        parser.print_help()
        return
    key = os.environ.get("IPUMS_API_KEY")
    if not key:
        parser.exit(1, "IPUMS_API_KEY is required\n")
    client = IpumsClient(key)
    try:
        if args.submit:
            spec = (
                build_1950_family_income_extract()
                if args.submit == "1950-family-income"
                else build_vitrine_extract(args.submit)
            )
            result = client.submit_extract(
                **spec,
                description="vitrine: 1949 family income"
                if args.submit == "1950-family-income"
                else "vitrine extract",
            )
            number = result.get("number")
            if not isinstance(number, int) or isinstance(number, bool) or number < 1:
                raise RuntimeError("Invalid API response")
            print(f"Extract submitted: {number}")
        elif args.status:
            status = client.get_status(args.status).get("status")
            print(
                "Status:",
                status
                if status
                in ("completed", "complete", "started", "queued", "failed", "error", "canceled")
                else "unknown",
            )
        elif args.download:
            print(f"Downloaded {len(client.download_extract(args.download))} files")
        else:
            print(f"Extracts returned: {len(client.list_extracts(limit=1 if args.test else 10))}")
    except (RuntimeError, ValueError, OSError, TimeoutError) as exc:
        parser.exit(1, f"{exc}\n")


if __name__ == "__main__":
    main()
