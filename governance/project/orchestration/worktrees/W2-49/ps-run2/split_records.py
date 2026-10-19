"""Throwaway (W2-49, DEC-741 K (2)): rewrite the records of the split and moved items from contract.yaml.

Usage: split_records.py <repo root> check|write
  check: render every covers record that is not one of the six and compare it with the file (the form check)
  write: write the six covers records and the Covers lines of CAP-43 and CAP-44
Not committed.
"""

import re
import sys
from pathlib import Path

import yaml

SIX = ("CAP-43.b", "CAP-43.d", "CAP-44.f", "CAP-44.h", "CAP-44.k", "CAP-44.l")
CAPS = ("CAP-43", "CAP-44")

root = Path(sys.argv[1])
mode = sys.argv[2]
folder = root / "docs/contract/capabilities"
data = yaml.safe_load((root / "docs/contract/contract.yaml").read_text(encoding="utf-8"))
version = data["version"]


def render(cap, item):
    meta = {
        "id": item["id"],
        "type": "capability",
        "status": "PROPOSED",
        "state_class": "DERIVED",
        "title": item["item"],
        "depends_on": [cap["id"]],
    }
    front = yaml.safe_dump(meta, sort_keys=False, allow_unicode=True, width=float("inf"))
    return (
        f"---\n{front}---\n\n# {item['id']}: {item['item']}\n\n"
        f"A covers item of {cap['id']} ({cap['title']}). Generated from `docs/contract/contract.yaml` "
        f"(Contract v4, version {version}), which is the authority (DEC-614).\n\n"
        f"- **Item:** {item['item']}\n- **Wave:** {item['wave']}\n"
    )


if mode == "check":
    same = differ = 0
    for cap in data["capabilities"]:
        for item in cap.get("covers") or []:
            if item["id"] in SIX:
                continue
            path = folder / f"{item['id']}.md"
            if path.read_text(encoding="utf-8") == render(cap, item):
                same += 1
            else:
                differ += 1
                print("differs:", item["id"])
    print(f"form check: {same} covers records reproduced exactly, {differ} differ")
elif mode == "write":
    for cap in data["capabilities"]:
        for item in cap.get("covers") or []:
            if item["id"] in SIX:
                (folder / f"{item['id']}.md").write_text(render(cap, item), encoding="utf-8")
                print("wrote", item["id"])
        if cap["id"] in CAPS:
            path = folder / f"{cap['id']}.md"
            text = path.read_text(encoding="utf-8")
            line = "- **Covers:** " + ", ".join(i["id"] for i in cap["covers"])
            new, n = re.subn(r"^- \*\*Covers:\*\* .*$", line, text, flags=re.MULTILINE)
            if n != 1:
                sys.exit(f"{cap['id']}.md: {n} Covers lines")
            path.write_text(new, encoding="utf-8")
            print("covers", cap["id"], "->", line)
