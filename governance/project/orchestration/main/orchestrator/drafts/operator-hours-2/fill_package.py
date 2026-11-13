#!/usr/bin/env python3
"""ACT-OPERATOR-HOURS-2 round 2: fill package.template.md's {{tokens}} from the finalized bundle and write ACT-OPERATOR-HOURS-2.md.
Run after `build_act.py all` (or build, rehearse, finalize). Read only on the bundle; writes only this folder's ACT-OPERATOR-HOURS-2.md."""
import hashlib
import json
import re
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
BUNDLE = Path("/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/acts/ACT-OPERATOR-HOURS-2")
CLONE = Path("/home/usain/gov-os-runs/W2-00/operator-hours-2-r2/clone")


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


log = (BUNDLE / "rehearsal.log").read_text()
assert log.rstrip().endswith("failures: 0"), "the rehearsal did not end with failures: 0"
cases = int(re.search(r"^cases: (\d+)$", log, re.M).group(1))
nums = {int(m.group(1)): m.group(2) for m in re.finditer(r"^ok (\d+): (.*)$", log, re.M)}
p7 = [n for n, t in nums.items() if "the package holds the operator's three blocks" in t]
p7_to = max(n for n, t in nums.items() if "[chain map]" in t or "[live map]" in t)
green = re.search(r"W1-01 before the ACT's commit: green \((.*?)\)", log).group(1)
red = re.search(r"CONTROL, W1-01 after the first commit and before the entry: red, the one failure names the first commit and no other \((.*?)\)", log).group(1)
m = json.loads((BUNDLE / "manifest.json").read_text())
msha = sha(BUNDLE / "manifest.json")
head = subprocess.run(["git", "-C", str(CLONE), "rev-parse", "--short=12", "HEAD"], capture_output=True, text=True).stdout.strip()
tok = {"CASES": cases, "P7_FROM": p7[0], "P7_TO": p7_to, "LIVE_FROM": p7_to + 1, "LIVE_TO": cases, "W101_GREEN": green, "W101_RED": red,
       "SHA8": msha[:8], "MANIFEST": msha, "APPLY_SHA": sha(BUNDLE / "apply.sh"), "REHEARSAL_SHA": sha(BUNDLE / "rehearsal.log"),
       "NFILES": len(m["files"]), "HEAD12": head}
text = (HERE / "package.template.md").read_text()
for k, v in tok.items():
    text = text.replace("{{" + k + "}}", str(v))
assert "{{" not in text, re.findall(r"\{\{[A-Z0-9_]+\}\}", text)
(HERE / "ACT-OPERATOR-HOURS-2.md").write_text(text)
print(json.dumps(tok, indent=1))
