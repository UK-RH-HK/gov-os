"""Assemble round 2's auditor brief: head, JUDGEMENT.md word for word, tail, the context packet."""
import subprocess
B = "/home/usain/gov-os-worktrees/W2-42a/.gov-runtime/scratch/lead/briefs/"
J = "/home/usain/gov-os-worktrees/W2-42a/governance/project/briefs/JUDGEMENT.md"
head = subprocess.run(["git", "-C", "/home/usain/gov-os-worktrees/W2-42a", "rev-parse", "HEAD"],
                      capture_output=True, text=True, check=True).stdout.strip()
h = open(B + "a3-2-head.md").read().replace("HEAD_FULL", head)
parts = [h, open(J).read(), open(B + "a3-tail.md").read(), open(B + "a3-ctx.md").read()]
open(B + "a3-2.md", "w").write("".join(parts))
print(head, sum(p.count("\n") for p in parts), "lines")
