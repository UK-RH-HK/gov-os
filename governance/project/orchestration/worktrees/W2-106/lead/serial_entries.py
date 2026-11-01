"""Print the serial-only entries that the selection keeps (not under an --ignore, not --deselect-ed), and the
pytest options as one argument per line, so the run scripts read them without shell quoting."""
import json
import sys

ROOT = "/home/usain/gov-os-worktrees/W2-106/"
sel = json.load(open(sys.argv[1]))
ignores = [o.split("=", 1)[1] for o in sel["pytest_options"] if o.startswith("--ignore=")]
deselects = [o.split("=", 1)[1] for o in sel["pytest_options"] if o.startswith("--deselect=")]
opts_out = open(sys.argv[2], "w")
for o in sel["pytest_options"]:
    opts_out.write(o + "\n")
kept = []
for line in open(ROOT + "tests/acceptance/serial-only.txt"):
    entry = line.strip()
    if not entry or entry.startswith("#"):
        continue
    path = ROOT + entry.split("::")[0]
    if any(path == i or path.startswith(i.rstrip("/") + "/") for i in ignores):
        continue
    if any(entry == d or entry == d.replace(ROOT, "") or (ROOT + entry) == d for d in deselects):
        continue
    kept.append(entry)
open(sys.argv[3], "w").write("\n".join(kept) + ("\n" if kept else ""))
print(len(kept), "serial-only entries kept;", len(ignores), "ignores;", len(deselects), "deselects")
print("W1-39 ignored:", any("/W1-39" in i for i in ignores))
for k in kept:
    print("  ", k)
