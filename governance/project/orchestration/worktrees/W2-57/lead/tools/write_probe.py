"""Writes the probe record of review 1: the lead's front matter and note, then the reviewer's record as returned."""
from pathlib import Path

SRC = Path("/home/usain/gov-os-worktrees/W2-57/.gov-runtime/scratch/lead/log/rev-1.result.md")
HEAD = Path("/home/usain/gov-os-worktrees/W2-57/.gov-runtime/scratch/lead/probes/PR-head.md")
OUT = Path("/home/usain/gov-os-worktrees/W2-57/docs/probes/DAEO-cy5o/PR-DAEO-cy5o.md")

returned = SRC.read_text(encoding="utf-8")
body = returned[returned.index("Verdict: pass"):].rstrip() + "\n"
OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(HEAD.read_text(encoding="utf-8") + body, encoding="utf-8")
print(OUT, len(OUT.read_text(encoding="utf-8").splitlines()))
