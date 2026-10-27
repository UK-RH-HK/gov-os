"""Writes the probe record of review 2: the lead's front matter and note, then the reviewer's record as returned."""
import subprocess
from pathlib import Path

ROOT = Path("/home/usain/gov-os-worktrees/W2-57")
SRC = ROOT / ".gov-runtime/scratch/lead/log/rev-2.result.md"
HEAD = ROOT / ".gov-runtime/scratch/lead/probes/PR-head-2.md"
OUT = ROOT / "docs/probes/DAEO-cy5o/PR-DAEO-cy5o-review-2.md"

probed = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "8f61bda0eb5c"], capture_output=True, text=True,
                        check=True).stdout.strip()
returned = SRC.read_text(encoding="utf-8")
body = returned[returned.index("Verdict: pass"):].rstrip() + "\n"
OUT.write_text(HEAD.read_text(encoding="utf-8").replace("@@PROBED@@", probed) + body, encoding="utf-8")
print(OUT, len(OUT.read_text(encoding="utf-8").splitlines()))
