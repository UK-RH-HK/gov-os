"""Assemble the R4/R5 narrow check's auditor brief a8: head, JUDGEMENT.md word for word, tail, the context packet."""
import re
import subprocess
B = "/home/usain/gov-os-worktrees/W2-42a/.gov-runtime/scratch/lead/"
J = "/home/usain/gov-os-worktrees/W2-42a/governance/project/briefs/JUDGEMENT.md"
head = subprocess.run(["git", "-C", "/home/usain/gov-os-worktrees/W2-42a", "rev-parse", "HEAD"],
                      capture_output=True, text=True, check=True).stdout.strip()
scoped = ("gov accept exit 0, every KPI line passed; the scoped run with GOV_TESTS_OPTIN=lifted,breadth: 6 failed, "
          "4431 passed, 2 xfailed, the 6 being W2-33's copy_folder cases in W1-50 and W1-28, red on d9e7dc859 too "
          "(log/r4-base-reds.log: 6 failed); lead_verify: 1 failed of 8250 "
          "(tests/unit/retrieval/test_w2_112_shared_reranker.py, passes alone: log/r4-rerank-alone.log)")
h = open(B + "r7/a8-head.md").read().replace("HEAD_FULL", head).replace("SCOPED_LINE", scoped)
tail = open(B + "briefs/a3-tail.md").read()
tail = tail.replace("Then the fenced verdict block, one entry per line S1-S11, F1, F2:",
                    "Then the fenced verdict block, one entry per line R4, R5, F3:")
tail = tail.replace('{"kpi": "S1"', '{"kpi": "R4"')
tail = tail.replace("(gov context DAEO-03ub --role independent-auditor)",
                    "(gov context DAEO-03ub --role independent-auditor --budget 20000, from the integration store's root)")
parts = [h, open(J).read(), "\n", tail, "\n```json\n", open(B + "r7/ctx-independent-auditor.md").read(), "\n```\n"]
text = "".join(parts)
open(B + "r7/a8.md", "w").write(text)
print(head, text.count("\n"), "lines; slots:", re.findall(r"\b(HEAD_FULL|SCOPED_LINE)\b", text),
      re.findall(r"\{[A-Z_]{3,}\}", text), "verdict ids ok:", "R4, R5, F3" in text, "JUDGEMENT in:", open(J).read() in text)
