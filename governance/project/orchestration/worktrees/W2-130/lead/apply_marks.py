"""Appends the auditor's commit_as texts (aud-marks-1-2's verdict block) to the two entries' status lines."""
import json, re
from pathlib import Path

ret = Path("/home/usain/gov-os-worktrees/W2-130/.gov-runtime/scratch/lead/aud-marks-1-return.md").read_text()
block = re.search(r"```verdict\n(.*?)\n```", ret, re.S).group(1)
verdict = json.loads(block)
reg = Path("/home/usain/gov-os-worktrees/W2-130/docs/DECISION_REGISTER.md")
lines = reg.read_text(encoding="utf-8").split("\n")
for m in verdict["marks"]:
    assert m["verdict"] == "right", m
    head = f"### {m['changed']} "
    i = next(n for n, l in enumerate(lines) if l.startswith(head))
    j = next(n for n in range(i + 1, i + 40) if lines[n].startswith("- **Status:**"))
    assert m["changer"] not in lines[j], (m, lines[j])
    lines[j] = lines[j] + m["commit_as"]
    print(m["changed"], "line", j + 1, "+", m["commit_as"])
reg.write_text("\n".join(lines), encoding="utf-8")
