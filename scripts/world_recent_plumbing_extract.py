"""Extract 2000 Census H048 counts for an occupied-unit plumbing percentage."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

SHA = "f688cad57d0e974a3dd3b8d5e39140ac93124c01d5dcb24d4349cd3d09aa4bb5"


def extract(path: Path) -> dict[str, object]:
    blob = path.read_bytes()
    if hashlib.sha256(blob).hexdigest() != SHA:
        raise ValueError("Census source response changed")
    headers, row = json.loads(blob)
    data = dict(zip(headers, row, strict=True))
    if data["NAME"] != "United States" or data["us"] != "1":
        raise ValueError("Census geography changed")
    total = int(data["H048001"])
    complete = int(data["H048003"]) + int(data["H048006"])
    lacking = int(data["H048004"]) + int(data["H048007"])
    if (total, complete, lacking) != (105480101, 104809115, 670986) or total != complete + lacking:
        raise ValueError("Census H048 population or categories changed")
    return {
        "provenance": "Curator sum from pinned Census 2000 SF3 H048 API response",
        "population": "United States occupied housing units",
        "total": total,
        "complete": complete,
        "lacking": lacking,
    }


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("source", type=Path)
    p.add_argument("output", type=Path)
    args = p.parse_args()
    args.output.write_text(
        json.dumps(extract(args.source), indent=2) + "\n", encoding="utf-8", newline="\n"
    )


if __name__ == "__main__":
    main()
