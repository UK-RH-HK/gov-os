import re
import sys

path = "/home/usain/gov-os-worktrees/W2-55/docs/DECISION_REGISTER.md"
want = set(sys.argv[1:])
lines = open(path, encoding="utf-8").read().split("\n")
out = []
cur = None
for line in lines:
    m = re.match(r"^#{2,4} (DEC-\d+)\b", line)
    if m:
        cur = m.group(1)
    elif re.match(r"^#{1,3} ", line):
        cur = None
    if cur in want:
        out.append(line)
print("\n".join(out))
