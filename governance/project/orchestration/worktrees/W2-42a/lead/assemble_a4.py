"""Assemble the narrow check's auditor brief: head, JUDGEMENT.md word for word, tail, the context packet."""
import re, subprocess
B = "/home/usain/gov-os-worktrees/W2-42a/.gov-runtime/scratch/lead/briefs/"
J = "/home/usain/gov-os-worktrees/W2-42a/governance/project/briefs/JUDGEMENT.md"
head = subprocess.run(["git", "-C", "/home/usain/gov-os-worktrees/W2-42a", "rev-parse", "HEAD"],
                      capture_output=True, text=True, check=True).stdout.strip()
scoped = ("`gov accept W2-42a` 803 passed, 0 failed, 2 skipped (the strict xfails); the scoped set (tests/unit/guard, "
          "tests/acceptance/W2-42a, tests/unit/hooks, tests/unit/pause, tests/unit/containment/test_w1_50_freeze_flag.py, "
          "tests/acceptance/W1-50, W1-28, W2-16) 1809 passed, 2 xfailed, 0 failed, 1835 deselected (the opt-in tiers; "
          "the lead runs them with GOV_TESTS_OPTIN=lifted,breadth into apos-scoped-optin.log)")
h = open(B + "a4-head.md").read().replace("HEAD_FULL", head).replace("SCOPED_LINE", scoped)
tail = open(B + "a3-tail.md").read()
tail = tail.replace("Then the fenced verdict block, one entry per line S1-S11, F1, F2:",
                    "Then the fenced verdict block, one entry per line A, B, C, D, SCOPE, DEC409, FC:")
tail = tail.replace('{"kpi": "S1"', '{"kpi": "A"')
tail = tail.replace("(gov context DAEO-03ub --role independent-auditor)",
                    "(gov context DAEO-03ub --role independent-auditor --budget 12000)")
parts = [h, open(J).read(), tail, "\n```json\n", open(B + "a4-ctx.md").read(), "\n```\n"]
text = "".join(parts)
open(B + "a4.md", "w").write(text)
print(head, text.count("\n"), "lines; slots:", re.findall(r"\b(HEAD_FULL|SCOPED_LINE)\b", text))
