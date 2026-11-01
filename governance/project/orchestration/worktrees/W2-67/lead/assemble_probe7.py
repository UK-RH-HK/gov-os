"""Assemble the run-7 probe record: the lead's head (probes/run7-head.md, its verification lines from
probes/run7-verify.md, the probed commit's full id resolved by git), then rev-7's full return (its saved first line,
the session line, left out). Writes docs/probes/DAEO-9nys/PR-DAEO-9nys-run7.md."""
import subprocess
from pathlib import Path

W = Path("/home/usain/gov-os-worktrees/W2-67")
LEAD = W / ".gov-runtime/scratch/lead"
OUT = W / "docs/probes/DAEO-9nys/PR-DAEO-9nys-run7.md"

full = subprocess.run(["git", "-C", str(W), "rev-parse", "aa4a4a9ef53e"], capture_output=True, text=True,
                      check=True).stdout.strip()
head = (LEAD / "probes/run7-head.md").read_text(encoding="utf-8")
verify = (LEAD / "probes/run7-verify.md").read_text(encoding="utf-8").rstrip("\n")
review = "\n".join((LEAD / "probes/rev-7.raw.md").read_text(encoding="utf-8").splitlines()[1:]).strip() + "\n"
text = head.replace("@@PROBED@@", full).replace("@@VERIFY@@", verify) + review
OUT.write_text(text, encoding="utf-8")
print(OUT, len(text.splitlines()))
