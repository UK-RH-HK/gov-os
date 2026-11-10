"""ACT-SETS-GLOBS-1's rehearsal: lines in the live guard call log that came from the rehearsal's own checks.

  python3 livelog_count.py <call log folder> <start, UTC ISO>

Counts the lines since <start> whose session is one of the rehearsal's fixed names, or whose tree is a run clone (the
rehearsal's clone is one). Reads the log's fields only (it holds hashes, never an action).
"""
import glob
import json
import os
import sys

MINE = {"sets-globs-check", "sets-globs-deliver", "sets-globs-latency", "seal-replay", "walls-check", "w2-149-guard"}
n = 0
for f in glob.glob(os.path.join(sys.argv[1], "*.jsonl")):
    for line in open(f, errors="replace"):
        try:
            d = json.loads(line)
        except ValueError:
            continue
        if d.get("time", "") >= sys.argv[2] and (d.get("session") in MINE or d.get("tree") == "run"):
            n += 1
print("the live call log: lines from this rehearsal's checks (their session names, or a run clone) since its start:", n)
