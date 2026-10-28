"""Reproduce two published EHS 2011 observations from pinned original PDFs.

Run with --download to acquire the small official report, errata and annex
workbooks into gitignored samples/. No microdata is downloaded. The dump is
an extraction artifact, not an independent publisher source; its header pins
both PDFs, and archive-backed tests re-extract the original bytes.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import urllib.request
from pathlib import Path

from link_check import _pdf_text

REPO = Path(__file__).resolve().parent.parent
DEFAULT_ARCHIVE = REPO / "samples" / "58-uk-housing-review"
PUBLICATION = "https://www.gov.uk/government/statistics/english-housing-survey-2011-homes-report"
HOST = "https://assets.publishing.service.gov.uk/media/"
FILES = {
    "ehs-homes-2011.pdf": (
        HOST + "5a7c381eed915d76e2ebbe26/EHS_HOMES_REPORT_2011.pdf",
        "1908c15dbb29196e53f2a5b91c9c9020f9df94a36aa7c702ae56c010f0055f5b",
    ),
    "ehs-homes-2011-errata.pdf": (
        HOST + "5a7d9c13ed915d497af70732/EHS_2011_Homes_Report_errata.pdf",
        "2418fab7b73e928ba574f70e77928c7404c4efb2de0af9a1c2040b9e3864022a",
    ),
    "ehs-homes-2011-chapter1.xls": (
        HOST + "5a7b7b70ed915d131105f87f/Chapter_1_Tables__Figures_and_Annex_Tables.xls",
        "848b10acf76bd24d905f45f2ef005838ffd8add2fa126a94f51fc9d70d808006",
    ),
    "ehs-homes-2011-chapter4.xls": (
        HOST + "5a7c1661e5274a1f5cc75b5a/Chapter_4_Tables__Figures_and_Annex_Tables.xls",
        "cbfdefdee34d2235634c58b1683cf617908f6e35f03f477e18c94961ce6bb1e3",
    ),
}


def _pinned(blob: bytes, name: str) -> str:
    digest = hashlib.sha256(blob).hexdigest()
    if digest != FILES[name][1]:
        raise ValueError(f"{name}: publisher bytes differ from the inspected vintage")
    return digest


def _observation(text: str, pattern: str) -> str:
    # PDF streams may repeat the same passage. Repeated agreeing readings are
    # acceptable; a conflicting value is an error, never an arbitrary first hit.
    readings = set(re.findall(pattern, text))
    if len(readings) != 1:
        raise ValueError(f"expected one unambiguous source value, got {sorted(readings)}")
    return readings.pop()


def extract(report: bytes, errata: bytes) -> str:
    report_hash = _pinned(report, "ehs-homes-2011.pdf")
    errata_hash = _pinned(errata, "ehs-homes-2011-errata.pdf")
    text = re.sub(r"\s+", " ", _pdf_text(report))
    corrected = re.sub(r"\s+", " ", _pdf_text(errata))
    if "Integral garages and integral balconies are included as usable floor area" not in corrected:
        raise ValueError("the inspected floor-area correction is missing")
    if "central heating is defined as a system with a boiler that feeds radiators" not in text:
        raise ValueError("the inspected heating definition is missing")
    area = _observation(
        text, r"In 2011, the average dwelling had a total usable floor area of (\d+)m²",
    )
    heating = _observation(
        text, r"rose from \d+% in 2001 to (\d+)% in 2011, Annex Table 4\.2",
    )
    return (
        "# EHS Homes 2011: extraction from original publisher PDFs\n"
        f"# report sha256: {report_hash}\n"
        f"# errata sha256: {errata_hash}\n"
        "# population: all dwellings in England, occupied or vacant\n"
        "# observation: 2011; fieldwork April 2010 to March 2012\n"
        f"mean-usable-floor-area-m2 = {area}\n"
        f"central-heating-percent = {heating}\n"
    )


def acquire(archive: Path) -> None:
    archive.mkdir(parents=True, exist_ok=True)
    manifest: list[dict[str, str | int]] = []
    for name, (url, _) in FILES.items():
        path = archive / name
        if path.exists():
            blob = path.read_bytes()
        else:
            request = urllib.request.Request(url, headers={"User-Agent": "vitrine-research/1.0"})
            with urllib.request.urlopen(request, timeout=60) as response:
                blob = response.read()
            _pinned(blob, name)  # refuse changed bytes before installing them
            path.write_bytes(blob)
        digest = _pinned(blob, name)
        manifest.append({"file": name, "url": url, "sha256": digest, "bytes": len(blob)})
    (archive / "acquisition-manifest.json").write_text(
        json.dumps({"publication": PUBLICATION, "files": manifest}, indent=2) + "\n",
        encoding="utf-8",
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archive", type=Path, default=DEFAULT_ARCHIVE)
    parser.add_argument("--download", action="store_true")
    args = parser.parse_args()
    if args.download:
        acquire(args.archive)
    dump = extract(
        (args.archive / "ehs-homes-2011.pdf").read_bytes(),
        (args.archive / "ehs-homes-2011-errata.pdf").read_bytes(),
    )
    destination = args.archive / "ehs-homes-2011-observations.txt"
    destination.write_text(dump, encoding="utf-8")
    print(f"Extracted two published observations to {destination}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
