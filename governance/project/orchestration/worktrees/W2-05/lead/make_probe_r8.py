"""Write docs/probes/DAEO-0z8c/PR-DAEO-0z8c-r8.md: the header, then the reviewer's record as returned."""
from pathlib import Path

S = Path("/home/usain/gov-os-worktrees/W2-05/.gov-runtime/scratch/lead")
head = (S / "probe_head_r8.md").read_text(encoding="utf-8")
record = (S / "probes-rev-2.txt").read_text(encoding="utf-8").split("\n", 1)[1]  # drop result_of.py's own first line
out = Path("/home/usain/gov-os-worktrees/W2-05/docs/probes/DAEO-0z8c/PR-DAEO-0z8c-r8.md")
out.write_text(head + record.rstrip("\n") + "\n", encoding="utf-8")
print(out, len(out.read_text(encoding="utf-8").splitlines()), "lines")
