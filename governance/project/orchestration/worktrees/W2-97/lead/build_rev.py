"""Fills the reviewer brief: the head to probe (argv[1], full id) and JUDGEMENT.md word for word."""
import sys

LEAD = "/home/usain/gov-os-worktrees/W2-97/.gov-runtime/scratch/lead"
judgement = open("/home/usain/gov-os-worktrees/W2-97/governance/project/briefs/JUDGEMENT.md", encoding="utf-8").read()
text = open(LEAD + "/briefs/rev-1.tmpl.md", encoding="utf-8").read()
text = text.replace("@HEAD@", sys.argv[1]).replace("@JUDGEMENT@", judgement.strip())
open(LEAD + "/briefs/rev-1.md", "w", encoding="utf-8").write(text)
print("rev-1.md", len(text.splitlines()), "lines; placeholders left:", text.count("@HEAD@") + text.count("@JUDGEMENT@"))
