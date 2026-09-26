#!/usr/bin/env python3
"""BR-AR-0016: self-check that no committed BR-AR-0016 file carries oracle content. Reads the quarantined oracle at
runtime; prints ONLY file:line locations and a category for each overlap, never the overlapping text.
Categories: LINE (a committed line of >= 40 chars occurs verbatim in the oracle), STRING (an oracle string of >= 20
chars occurs in a committed file), IDENT (an oracle symbol, record id or section title occurs in a committed file),
PATH (an oracle anchor path occurs in a committed file). Structural strings shared with PUBLIC design files (the
domain path, the three view commits, stage names, query ids, gate names) are listed in ALLOW and ignored."""
import os
import re
import subprocess
import sys

import yaml

DOM = "release/orchestration/phase-2-context-bridge"
root = subprocess.run(["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True).stdout.strip()
oracle_txt = subprocess.run(["git", "show", f"bridge/grade-0012:{DOM}/DEMONSTRATION/oracle/oracle.yaml"],
                            capture_output=True, text=True, cwd=root).stdout
oracle = yaml.safe_load(oracle_txt)
strings, idents, paths = set(), set(), set()


def walk(x, key=None):
    if isinstance(x, dict):
        for k, v in x.items():
            walk(v, k)
    elif isinstance(x, list):
        for v in x:
            walk(v, key)
    elif isinstance(x, str):
        s = x.strip()
        if key in ("symbol", "record_id", "section", "item"):
            idents.add(s)
            if "::" in s:
                idents.add(s.split("::")[-1])
        elif key == "path":
            paths.add(s)
        elif len(s) >= 20:
            strings.add(s)


walk(oracle)
ALLOW = {DOM, "3c880d80f81475f5306bdd5f680f2e004df49391", "6e7a2a3495a8d3619759a95b7ed055da9c848618",
         "58219d5628683d6f462aa67bf25dbc2641933bce"}
idents = {i for i in idents if len(i) >= 6 and i not in ALLOW}
# PUBLIC corpus: what builders and the demonstration agent legitimately hold (the run-1 packet, the bridge state, the
# public design and query files). An overlap whose token also occurs there is public metadata (a mandatory item id, a
# class name, a mandatory input path), not oracle content; it is reported as PUBLIC. Only SUBSTANTIVE overlaps fail.
PUBLIC_FILES = [f"{DOM}/DEMONSTRATION/run-1/packet/packet.md", f"{DOM}/ORCHESTRATOR_STATE.yaml",
                f"{DOM}/ARCHITECTURE/DEMONSTRATION_DESIGN.md", f"{DOM}/ARCHITECTURE/ARCHITECTURE.md",
                f"{DOM}/ARCHITECTURE/demonstration-queries.yaml", f"{DOM}/ARCHITECTURE/demonstration-task.yaml"]
public = "\n".join(open(os.path.join(root, f), encoding="utf-8").read() for f in PUBLIC_FILES)
# the bridge domain's own tracked file paths are builder-visible by design (a repair plan for the bridge must name them)
public += "\n" + subprocess.run(["git", "ls-files", DOM], capture_output=True, text=True, cwd=root).stdout
files = sys.argv[1:]
hits = []
for f in files:
    for n, line in enumerate(open(f, encoding="utf-8", errors="replace"), start=1):
        s = line.strip()
        found = []
        if len(s) >= 40 and s in oracle_txt:
            found.append(("LINE", s))
        found += [("STRING", o) for o in strings if len(o) >= 20 and o in line]
        found += [("IDENT", i) for i in idents if re.search(r"(?<![\w-])" + re.escape(i) + r"(?![\w-])", line)]
        found += [("PATH", p) for p in paths if p in line]
        for cat, tok in found:
            hits.append((f, n, cat, "PUBLIC" if tok in public else "SUBSTANTIVE"))
subst = [h for h in hits if h[3] == "SUBSTANTIVE"]
for f, n, c, k in hits:
    print(f"{os.path.relpath(f, root)}:{n}: {c} {k}")
print(f"files_checked={len(files)} overlaps={len(hits)} public={len(hits) - len(subst)} substantive={len(subst)}")
sys.exit(1 if subst else 0)
