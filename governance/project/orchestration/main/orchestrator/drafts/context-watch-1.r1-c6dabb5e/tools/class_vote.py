"""The operator's own classifier (act_class.py, read only) on a copy of a bundle that holds only the first N listed files.
   python3 class_vote.py <bundle dir> <N> <scratch dir>     prints the class letter."""
import hashlib
import json
import os
import shutil
import subprocess
import sys

B, N, S = sys.argv[1], int(sys.argv[2]), sys.argv[3]
shutil.rmtree(S, ignore_errors=True)
shutil.copytree(B, S)
rows = [r.split("|") for r in open(os.path.join(S, "list.txt")).read().split("\n") if r][:N]
m = {"act": "VOTE", "dec": "x", "author": "cto", "claimed_class": "b",
     "touched": [{"root": r[0], "path": r[1], "before": r[2], "after": r[3]} for r in rows], "files": {}, "checks": [],
     "commands": [], "rehearsal": {}}
for _, rel, b, a in rows:
    m["files"][f"before/repo/{rel}"], m["files"][f"after/repo/{rel}"] = b, a
json.dump(m, open(os.path.join(S, "manifest.json"), "w"), indent=1)
out = subprocess.run([sys.executable, "/home/usain/Dynamic-Agentic-Engineering-OS/governance/project/operator/act_class.py", S],
                     capture_output=True, text=True).stdout
print(json.loads(out)["class"])
shutil.rmtree(S, ignore_errors=True)
