"""From select_tests.py's JSON, write the scoped run's argument files (DEC-952, DEC-968).

argv: <selection json> <worktree> <out folder>
Writes: parallel.args (targets + pytest_options, one per line), serial.args (the serial-route entries of
tests/acceptance/serial-only.txt that the selection reaches, one per line), serial.given (the same entries).
"""
import json
import sys
from pathlib import Path

sel_path, tree, out = sys.argv[1], Path(sys.argv[2]), Path(sys.argv[3])
d = json.loads(Path(sel_path).read_text(encoding="utf-8"))
assert d["scope"] == "scoped", d["scope"]
targets = [s["target"] for s in d["selected"]]
opts = list(d["pytest_options"])
ignored = [o.split("=", 1)[1] for o in opts if o.startswith("--ignore=")]
deselected = [o.split("=", 1)[1] for o in opts if o.startswith("--deselect=")]


def rel(p):
    p = str(p)
    root = str(tree) + "/"
    return p[len(root):] if p.startswith(root) else p


ignored = [rel(p) for p in ignored]
deselected = [rel(p) for p in deselected]

serial = []
for line in (tree / "tests/acceptance/serial-only.txt").read_text(encoding="utf-8").splitlines():
    if not line.strip() or line.lstrip().startswith("#"):
        continue
    entry, _, comment = line.partition(" #")
    entry, comment = entry.strip(), comment.strip()
    if not comment.startswith("serial"):
        continue
    file_part = entry.split("::", 1)[0]
    reached = any(file_part == t.rstrip("/") or file_part.startswith(t.rstrip("/") + "/") or entry.startswith(t)
                  or t.startswith(entry) for t in targets)
    if not reached:
        continue
    if any(file_part == i or file_part.startswith(i.rstrip("/") + "/") for i in ignored):
        continue
    if any(entry == x or entry.startswith(x + "::") or entry.startswith(x + "[") for x in deselected):
        continue
    serial.append(entry)

(out / "parallel.args").write_text("\n".join(targets + opts) + "\n", encoding="utf-8")
(out / "serial.args").write_text("\n".join(serial) + ("\n" if serial else ""), encoding="utf-8")
(out / "serial.given").write_text("\n".join(serial) + ("\n" if serial else ""), encoding="utf-8")
print("targets", len(targets), "options", len(opts), "serial", len(serial))
for s in serial:
    print("serial:", s)
