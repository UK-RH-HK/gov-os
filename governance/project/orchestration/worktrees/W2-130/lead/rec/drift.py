"""W2-130 S2: the drift count by docs/research/W2-92-proto-drift.py's definitions, read from the entries' own text.

Run from the repository's root as `python3 -` (this script on stdin); no store is read and nothing is written.
The definitions are W2-92-proto-drift.py's (the census's, D4B-link-census.py at 3d1c459e): a statement is a register
label, its free text or the change log (loader.register_statements) or an ARCHIVE-SUPERSEDED §A line read with the
same patterns; a decision is current when its status is ACCEPTED and no SUPERSEDES edge targets it (the records and
edges read from HEAD by the loader's own rule, as the script's --from-head does); a decision ARCHIVE-SUPERSEDED §B
calls spent is left out (DEC-1073 (2)); a decision not ACCEPTED is never current. A drift pair is (changed, changer):
the changed decision current and stated changed (supersede or amend) by the changer, and its own status line (the
first line under its heading, the loader's `first`) not naming the changer's id (the rule `gov links` marks by,
src/gov/links/check.py; the census's "status line marks" read per changer).
Prints one JSON object {"drift": [{"changed", "changer"}...], "count": n}.
"""
import collections
import json
import re
import sys
from pathlib import Path

import yaml

ROOT = Path.cwd()
sys.path.insert(0, str(ROOT / "src"))
from gov.store import loader  # noqa: E402

DEC = re.compile(r"\bDEC-(\d{3,})\b")
ARCHIVE = "governance/project/orchestration/ARCHIVE-SUPERSEDED.md"

rows, edge_rows, _, _, _, _ = loader._read_records(ROOT)
rec = {rid: {"type": kind, "status": status} for _, rid, kind, status in rows}
superseded_edges = {d for t, s, d in edge_rows if t == "SUPERSEDES"}

reg_rel = yaml.safe_load((ROOT / loader.PATH_MAP_REL).read_text())[loader.REGISTER_KEY]
reg_text = (ROOT / reg_rel).read_text()
entries, _ = loader.register_entries(reg_text)
entry = {e["id"]: e for e in entries}
said = loader.register_statements(reg_text, entries)
BY, vclass = loader._BY, loader._verb_class

arch_stmt, arch_spent = [], set()
if (ROOT / ARCHIVE).is_file():
    text = (ROOT / ARCHIVE).read_text()
    for line in text.split("## B.", 1)[-1].split("\n"):
        if line.startswith("- DEC-") and re.search(r"\bSpent\b|\bspent\b", line):
            arch_spent |= {"DEC-" + x for x in DEC.findall(line[2:].split(":")[0])}
    for line in text.split("## B.")[0].split("\n"):
        if not line.startswith("- DEC-"):
            continue
        head_, _, tail = line[2:].partition(":")
        for b in BY.finditer(tail):
            for t in DEC.findall(head_):
                for y in DEC.findall(b.group(2)):
                    arch_stmt.append({"source": "DEC-" + y, "target": "DEC-" + t, "cls": vclass(b.group(1))})


def current(t):
    r = rec.get(t)
    return bool(r) and r["status"] == "ACCEPTED" and t not in superseded_edges


changers = collections.defaultdict(set)
for s in said + arch_stmt:
    if s["cls"] in ("supersede", "amend") and s["target"] in entry and current(s["target"]):
        changers[s["target"]].add(s["source"])
for t in [t for t in changers if t in arch_spent]:
    del changers[t]


def status_line(t):
    lines = entry[t]["span"].split("\n") if "span" in entry[t] else []
    first = entry[t].get("first") or next((ln for ln in lines if ln.startswith("- **Status:**")), "")
    return first.split("\n")[0]


def names(line, changer):
    return re.search(rf"\b{changer}(?![0-9])", line) is not None


key = lambda x: int(x[4:])  # noqa: E731
drift = [{"changed": t, "changer": c} for t in sorted(changers, key=key) for c in sorted(changers[t], key=key)
         if not names(status_line(t), c)]
print(json.dumps({"drift": drift, "count": len(drift)}))
