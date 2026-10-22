"""Summarise the five trial runs' JUnit files: per run the reds (failure/error) with the first line of each message,
the reruns (rerunfailures), and the reds unique to a run against b1 (the plain --dist load run)."""
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

out = Path(sys.argv[1])
RUNS = ["b1-load", "b2-worksteal", "a-cost-timeout", "d1-rerunfailures", "d2-randomly"]
reds, reruns = {}, {}
for run in RUNS:
    path = out / f"{run}.xml"
    reds[run], reruns[run] = {}, []
    for case in ET.parse(path).iter("testcase"):
        node = f"{case.get('classname')}::{case.get('name')}"
        for tag in ("failure", "error"):
            el = case.find(tag)
            if el is not None:
                msg = (el.get("message") or el.text or "").strip().splitlines()
                reds[run][node] = f"{tag}: {msg[0][:150] if msg else ''}"
        if case.find("rerun") is not None or any(c.tag.endswith("rerun") for c in case):
            reruns[run].append(node)
    total = sum(float(c.get("time") or 0) for c in ET.parse(path).iter("testcase"))
    print(f"== {run}: {len(reds[run])} reds, {len(reruns[run])} reruns, summed case time {total:.0f} s")
    for node, msg in sorted(reds[run].items()):
        print(f"   {node[:140]}\n      {msg}")
    for node in reruns[run]:
        print(f"   rerun: {node[:140]}")
base = set(reds["b1-load"])
for run in RUNS[1:]:
    extra = sorted(set(reds[run]) - base)
    print(f"-- reds in {run} not in b1: {len(extra)}")
    for node in extra:
        print("   ", node[:150])
