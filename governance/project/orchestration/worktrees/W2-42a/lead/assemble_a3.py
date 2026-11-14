"""Assemble the auditor's brief: head, JUDGEMENT.md word for word, tail, the context packet."""
B = "/home/usain/gov-os-worktrees/W2-42a/.gov-runtime/scratch/lead/briefs/"
J = "/home/usain/gov-os-worktrees/W2-42a/governance/project/briefs/JUDGEMENT.md"
parts = [open(B + "a3-head.md").read(), open(J).read(), open(B + "a3-tail.md").read(), open(B + "a3-ctx.md").read()]
open(B + "a3-1.md", "w").write("".join(parts))
print(sum(p.count("\n") for p in parts), "lines")
