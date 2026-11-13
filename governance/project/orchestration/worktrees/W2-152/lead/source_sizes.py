"""Characters of each source entry of the ticket in the register, and the ticket's own sections."""
import re

REG = "/home/usain/gov-os-worktrees/W2-152/docs/DECISION_REGISTER.md"
TICKET = "/home/usain/gov-os-worktrees/W2-152/.tickets/DAEO-o5x1.md"
text = open(REG, encoding="utf-8").read()
heads = [(m.start(), m.group(1)) for m in re.finditer(r"^### (DEC-\d+)\b", text, re.M)]
size = {}
for i, (pos, dec) in enumerate(heads):
    end = heads[i + 1][0] if i + 1 < len(heads) else len(text)
    size[dec] = end - pos
for dec in ("DEC-1050", "DEC-1052", "DEC-1083", "DEC-1088", "DEC-1112", "DEC-1109"):
    print(dec, size.get(dec), "chars, about", (size.get(dec) or 0) // 4, "tokens")
t = open(TICKET, encoding="utf-8").read()
fm_end = t.index("\n---", 3)
print("ticket front matter", fm_end, "chars; body", len(t) - fm_end, "chars")
in_src = False
for line in t.splitlines():
    if line.startswith("sources:"):
        in_src = True
        continue
    if in_src:
        if line.startswith("- ") or line.startswith("  "):
            print("  src:", line[:160])
        else:
            in_src = False
