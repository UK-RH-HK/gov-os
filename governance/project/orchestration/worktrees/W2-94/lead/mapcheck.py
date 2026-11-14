import sys
sys.path.insert(0, "/home/usain/gov-os-worktrees/W2-94/src")
from gov.accept.runner import line_names, Unlisted, _cells
text = open(sys.argv[1], encoding="utf-8").read().splitlines()
for n, raw in enumerate(text, 1):
    if raw.strip().startswith("|"):
        c = _cells(raw.strip())
        if c:
            try:
                print(n, "OK", line_names(c[0]))
            except Unlisted:
                print(n, "UNLISTED")
