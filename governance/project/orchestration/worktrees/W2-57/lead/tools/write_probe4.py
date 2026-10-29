"""Writes run 4's probe record: the lead's front matter and note, then the reviewer's record as returned."""
import subprocess
import sys
from pathlib import Path

ROOT = Path("/home/usain/gov-os-worktrees/W2-57")
SRC = ROOT / ".gov-runtime/scratch/lead/log/rev-4.result.md"
HEAD = ROOT / ".gov-runtime/scratch/lead/probes/PR-head-4.md"
OUT = ROOT / "docs/probes/DAEO-cy5o/PR-DAEO-cy5o-reprobe-2.md"

probed = subprocess.run(["git", "-C", str(ROOT), "rev-parse", sys.argv[1]], capture_output=True, text=True,
                        check=True).stdout.strip()
returned = SRC.read_text(encoding="utf-8")
body = returned[returned.index("Verdict: pass"):].rstrip() + "\n"
OUT.write_text(HEAD.read_text(encoding="utf-8").replace("@@PROBED@@", probed) + body, encoding="utf-8")
print(OUT, len(OUT.read_text(encoding="utf-8").splitlines()))
