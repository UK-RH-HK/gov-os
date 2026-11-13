import re, sys
sys.path.insert(0, "/home/usain/gov-os-worktrees/W2-146/src")
from gov.accept.runner import parse_map
text = open("/home/usain/gov-os-worktrees/W2-146/tests/acceptance/W2-146/README.md").read()
print("as is:", parse_map(text))
out = []
for line in text.splitlines():
    if line.startswith("| ") and "test_w2_146_" in line:
        cells = line.split("|")
        cells[2] = " " + ", ".join("`%s`" % t.strip() for t in cells[2].split(",")) + " "
        line = "|".join(cells)
    out.append(line)
m = parse_map("\n".join(out))
for k in sorted(m):
    print(k, len(m[k]))
