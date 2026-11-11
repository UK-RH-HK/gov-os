import sys
from pathlib import Path
sys.path.insert(0, "/home/usain/Dynamic-Agentic-Engineering-OS/src")
from gov.accept.runner import parse_map, Unreadable, Unlisted
text = Path("/home/usain/gov-os-worktrees/W2-81/tests/acceptance/W2-81/README.md").read_text(encoding="utf-8")
try:
    parse_map(text); print("as is: reads")
except Unlisted as e: print("as is: Unlisted", e.args[0], e.args[1][:60])
except Unreadable: print("as is: Unreadable")
new = {
 "**Review (batch 4)** Items 1 to 10": "**S3, S4, S5, S6, S7, S9, F1, F2, F3, F4** Review batch 4, items 1 to 10",
 "**Round 3 (DEC-1005)** Items 1 and 2": "**S7, S10, F4, F5** Round 3 (DEC-1005), items 1 and 2",
 "**Round 2b (DEC-997)** Items 1 to 7": "**S4, S5, S6, S7, S10, F2, F3, F4, F5** Round 2b (DEC-997), items 1 to 7",
 "**Round 2 (DEC-993)** Items 1 to 7": "**S3, S5, S6, S7, S9, S10, F1, F4, F5** Round 2 (DEC-993), items 1 to 7",
}
out = []
for l in text.splitlines():
    for k, v in new.items():
        if l.startswith("| " + k):
            rest = l[len("| " + k):]
            # keep the remainder of the cell
            l = "| " + v + rest
            print("ROW:", l[:200])
    out.append(l)
m = parse_map("\n".join(out))
print("after: reads;", {k: len(v) for k, v in m.items()})
