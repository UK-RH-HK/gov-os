"""Classify run1c's reds against the known-red lists: classify_reds.py <tag>."""
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

LOG = Path("/home/usain/gov-os-worktrees/W2-84/.gov-runtime/scratch/lead/log")
tag = sys.argv[1]
known = set()
for line in Path("/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/briefs/"
                 "W2-90-cases.txt").read_text().splitlines():
    line = line.strip()
    if line and not line.startswith("#"):
        known.add(line.split()[0])
tot = {}
failing = []
for name in (f"parallel-{tag}.xml", f"serial-{tag}.xml"):
    p = LOG / name
    if not p.exists():
        continue
    root = ET.parse(p).getroot()
    for s in root.iter("testsuite"):
        for k in ("tests", "failures", "errors", "skipped"):
            tot[(name, k)] = tot.get((name, k), 0) + int(s.get(k, 0))
    for tc in root.iter("testcase"):
        if tc.find("failure") is not None or tc.find("error") is not None:
            f = tc.get("file") or tc.get("classname", "").replace(".", "/") + ".py"
            failing.append(f"{f}::{tc.get('name')}")
print(tot)
alone = (LOG / f"scoped-{tag}.out").read_text()
print("known entries:", len(known), "failing:", len(failing))
for node in failing:
    in_known = node in known or any(node.startswith(k.rstrip("/") + "::") or node.startswith(k.rstrip("/") + "/")
                                    for k in known if "::" not in k)
    state = "ALONE PASS" if f"ALONE PASS (flaky candidate): {node}" in alone else "ALONE RED"
    print(("KNOWN-W2-90 " if in_known else "OTHER       ") + state + " " + node)
