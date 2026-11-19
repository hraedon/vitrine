"""Extract Census 1990 plumbing and phone counts from pinned source tables."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

PINS = {
    "plumbing-tab.txt": "56dcbdabfcdb340ccf23b988779725a3165b0e150d62795848a9ddd4b767132b",
    "phone-tab.txt": "f0029b5ad7a1974e90d69e24f19584548a23c6343efdd033dee3f872f31e1a27",
}


def extract(root: Path) -> dict[str, object]:
    rows = {}
    expected = {"plumbing-tab.txt": (101161982, 1101696), "phone-tab.txt": (87129953, 4817457)}
    for name, sha in PINS.items():
        data = (root / name).read_bytes()
        if hashlib.sha256(data).hexdigest() != sha:
            raise ValueError("Census table changed: " + name)
        text = data.decode("utf-8-sig")
        if "1990" not in text or "1980" not in text:
            raise ValueError("Census year headings changed")
        row = re.search(r"(?m)^\s*US\s+([\d,]+)\s+([\d,]+)\s+([\d.]+%)", text)
        if row is None:
            raise ValueError("Census national row missing")
        yes, no = (int(x.replace(",", "")) for x in row.group(1, 2))
        if (yes, no) != expected[name]:
            raise ValueError("Unexpected 1990 national counts")
        rows[name] = {"yes": yes, "no": no, "total": yes + no, "printed_no_percent": row.group(3)}
    return {
        "provenance": "Curator extraction from pinned Census 1990 historical tables",
        "plumbing": {**rows["plumbing-tab.txt"], "population": "all housing units"},
        "telephone": {**rows["phone-tab.txt"], "population": "occupied housing units"},
    }


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("source_dir", type=Path)
    p.add_argument("output", type=Path)
    args = p.parse_args()
    args.output.write_text(
        json.dumps(extract(args.source_dir), indent=2) + "\n", encoding="utf-8", newline="\n"
    )


if __name__ == "__main__":
    main()
