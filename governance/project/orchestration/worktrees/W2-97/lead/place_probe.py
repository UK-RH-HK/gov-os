"""Writes the passing probe record to docs/probes/DAEO-wq2b/PR-DAEO-wq2b.md, the probed commit's full id
(argv[1], read from git by the caller) put in for the placeholder (DEC-733; the full id only in the committed record)."""
import os
import sys

LEAD = "/home/usain/gov-os-worktrees/W2-97/.gov-runtime/scratch/lead"
full = sys.argv[1].strip()
assert len(full) == 40 and full.startswith("287047f23ab8"), "not the probed head"
text = open(LEAD + "/probes/PR-DAEO-wq2b.draft.md", encoding="utf-8").read().replace("@PROBED@", full)
os.makedirs("/home/usain/gov-os-worktrees/W2-97/docs/probes/DAEO-wq2b", exist_ok=True)
open("/home/usain/gov-os-worktrees/W2-97/docs/probes/DAEO-wq2b/PR-DAEO-wq2b.md", "w", encoding="utf-8").write(text)
print("written; placeholders left:", text.count("@PROBED@"))
