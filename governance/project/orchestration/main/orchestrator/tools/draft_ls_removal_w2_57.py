"""Empties the path map's load_sensitive list: all 30 entries are fixed by W2-57 (merged 57e363c5, 2026-10-28).

W1-46's 23 and W1-19's warm p95 leave the close by W2-57's route (nightly); W1-38 x3, W1-07 [doctor], W1-30 r13 and
the unit close follow-up were fixed in its run 1. Applies to the working copy only; the orchestrator saves the diff
to scratch for the owner's Role: owner commit and restores the file.
"""
import pathlib
import sys

PM = pathlib.Path("/home/usain/Dynamic-Agentic-Engineering-OS/governance/project/path-map.yaml")
lines = PM.read_text(encoding="utf-8").split("\n")
start = lines.index("load_sensitive:")
end = start + 1
while end < len(lines) and (lines[end].startswith("  ") or lines[end] == ""):
    end += 1
entries = sum(1 for x in lines[start + 1:end] if x.startswith("  - test:"))
if entries != 30:
    sys.exit("expected 30 entries, found %d" % entries)
lines[start:end] = ["load_sensitive: []"]
PM.write_text("\n".join(lines), encoding="utf-8")
print("removed %d entries (lines %d to %d)" % (entries, start + 1, end))
