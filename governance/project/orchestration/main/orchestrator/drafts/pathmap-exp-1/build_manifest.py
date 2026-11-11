"""Builds ACT-PATHMAP-EXP-1/manifest.json (same schema as ACT-ACCEPTED-REDS-1's). Run from the drafts folder:
python3 build_manifest.py   (rehearsal.log must exist in the bundle for the full manifest)."""
import hashlib, json, sys
from pathlib import Path
B = Path(__file__).resolve().parent / "ACT-PATHMAP-EXP-1"
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
MAP = "governance/project/path-map.yaml"
before = sha(B / "before/repo" / MAP); after = sha(B / "after/repo" / MAP)
check2 = open("/tmp/claude-1000/c2.txt").read().strip() if len(sys.argv) < 2 else Path(sys.argv[1]).read_text().strip()
files = {f"before/repo/{MAP}": before, f"after/repo/{MAP}": after, "apply.sh": sha(B / "apply.sh"), "list.txt": sha(B / "list.txt")}
reh = None
if (B / "rehearsal.log").exists():
    reh = sha(B / "rehearsal.log"); files["rehearsal.log"] = reh
m = {"act": "ACT-PATHMAP-EXP-1", "dec": "DEC-333, DEC-273, DEC-1066, DEC-957", "author": "cto", "claimed_class": "b",
     "touched": [{"root": "repo", "path": MAP, "before": before, "after": after}],
     "files": files,
     "checks": [{"cmd": "PYTHONPATH=src python3 -m gov.check.pathmap", "exit": 0, "count": None},
                {"cmd": check2, "exit": 0, "count": None}],
     "commands": [], "rehearsal": {"log": "rehearsal.log", "sha256": reh}}
(B / "manifest.json").write_text(json.dumps(m, indent=1) + "\n")
print(sha(B / "manifest.json"))
