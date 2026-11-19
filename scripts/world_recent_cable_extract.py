"""Extract FCC June 2006 cable and TV-household counts for a curator ratio."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

SHA = "1f8edaae47143a65f7a9bc50e54195f810610f7362130cc8582ebd41ee3e518e"


def extract(path: Path) -> dict[str, object]:
    if hashlib.sha256(path.read_bytes()).hexdigest() != SHA:
        raise ValueError("FCC report changed")
    from pypdf import PdfReader

    pdf = PdfReader(path)
    page5 = " ".join(pdf.pages[4].extract_text().split())
    page6 = " ".join(pdf.pages[5].extract_text().split())
    households = re.search(r"As of June 2006, there were (\d+\.\d+) million TV households", page5)
    cable = re.search(
        r"June 2006, the number of basic cable subscribers increased "
        r"slightly to (\d+\.\d+) million",
        page6,
    )
    if not households or not cable or (households.group(1), cable.group(1)) != ("110.2", "65.3"):
        raise ValueError("FCC context or observed counts changed")
    return {
        "provenance": "Curator extraction from pinned FCC 07-206",
        "population": "June 2006 TV households and basic cable subscribers",
        "tv_households_millions": households.group(1),
        "basic_cable_millions": cable.group(1),
    }


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("report", type=Path)
    p.add_argument("output", type=Path)
    args = p.parse_args()
    args.output.write_text(
        json.dumps(extract(args.report), indent=2) + "\n", encoding="utf-8", newline="\n"
    )


if __name__ == "__main__":
    main()
