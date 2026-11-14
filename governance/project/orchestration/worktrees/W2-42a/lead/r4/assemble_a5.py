"""Assemble the narrow check's auditor brief: head, JUDGEMENT.md word for word, tail, the context packet."""
import re, subprocess, sys
B = "/home/usain/gov-os-worktrees/W2-42a/.gov-runtime/scratch/lead/"
J = "/home/usain/gov-os-worktrees/W2-42a/governance/project/briefs/JUDGEMENT.md"
head = subprocess.run(["git", "-C", "/home/usain/gov-os-worktrees/W2-42a", "rev-parse", "HEAD"],
                      capture_output=True, text=True, check=True).stdout.strip()
scoped = sys.argv[1]
h = open(B + "r4/a5-head.md").read().replace("HEAD_FULL", head).replace("SCOPED_LINE", scoped)
tail = open(B + "briefs/a3-tail.md").read()
tail = tail.replace("Then the fenced verdict block, one entry per line S1-S11, F1, F2:",
                    "Then the fenced verdict block, one entry per line HASH, HSTR, DEP1, DEC409, FC:")
tail = tail.replace('{"kpi": "S1"', '{"kpi": "HASH"')
tail = tail.replace("(gov context DAEO-03ub --role independent-auditor)",
                    "(gov context DAEO-03ub --role independent-auditor --budget 12000)")
parts = [h, open(J).read(), tail, "\n```json\n", open(B + "r4/ctx-aud.md").read(), "\n```\n"]
text = "".join(parts)
open(B + "r4/a5.md", "w").write(text)
print(head, text.count("\n"), "lines; slots:", re.findall(r"\b(HEAD_FULL|SCOPED_LINE)\b", text),
      "verdict ids ok:", "HASH, HSTR, DEP1, DEC409, FC" in text, "JUDGEMENT in:", open(J).read() in text)
