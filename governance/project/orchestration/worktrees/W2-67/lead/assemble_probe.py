"""Assemble the run-6 probe record: the lead's head, then each reviewer's full return (the first line of each saved
result is the session line, left out)."""
from pathlib import Path

LEAD = Path("/home/usain/gov-os-worktrees/W2-67/.gov-runtime/scratch/lead")
OUT = Path("/home/usain/gov-os-worktrees/W2-67/docs/probes/DAEO-9nys/PR-DAEO-9nys-run6.md")


def body(name):
    return "\n".join((LEAD / "log" / name).read_text(encoding="utf-8").splitlines()[1:]).strip() + "\n"


text = (LEAD / "probes" / "run6-head.md").read_text(encoding="utf-8")
text += body("rev-5.result.md") + "\n## rev-6's record\n\n" + body("rev-6.result.md")
OUT.write_text(text, encoding="utf-8")
print(OUT, len(text.splitlines()))
