"""The serial-only entries that fall inside the scoped selection, one per line (for GOV_CLOSE_SERIAL_ONLY_GIVEN)."""
import json
import sys

root = "/home/usain/gov-os-worktrees/W2-55"
sel = json.load(open(sys.argv[1], encoding="utf-8"))
targets = [s["target"] for s in sel["selected"]]
ignored = [i.replace(root + "/", "") for i in sel.get("ignore", [])]
deselected = [d.replace(root + "/", "") for d in sel.get("deselect", [])]
entries = []
for line in open(root + "/tests/acceptance/serial-only.txt", encoding="utf-8"):
    entry = line.split("#", 1)[0].strip()
    if not entry:
        continue
    path = entry.split("::", 1)[0]
    inside = any(entry == t or entry.startswith(t.rstrip("/") + "/") or entry.startswith(t + "::")
                 or path == t.split("::", 1)[0] and ("::" not in t or entry.startswith(t))
                 for t in targets)
    out = any(path == i or path.startswith(i.rstrip("/") + "/") for i in ignored) or entry in deselected
    if inside and not out:
        entries.append(entry)
open(sys.argv[2], "w", encoding="utf-8").write("\n".join(entries) + ("\n" if entries else ""))
print(len(entries), "serial entries in the selection")
for e in entries:
    print(" ", e)
