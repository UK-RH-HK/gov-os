"""Run 6: the serial-only cases (tests/acceptance/serial-only.txt) that the scoped selection (select-6.json) reaches:
an entry under a selected target, not under an ignored path, not deselected. Prints one entry per line."""
import json
import sys

W = "/home/usain/gov-os-worktrees/W2-67"
sel = json.load(open(W + "/.gov-runtime/scratch/lead/log/select-6.json"))
targets = [s["target"] for s in sel["selected"]]
ignore = sel["ignore"]
deselect = set(sel["deselect"])


def under(entry, prefix):
    if prefix.endswith("/"):
        return entry.startswith(prefix)
    return entry == prefix or entry.startswith(prefix + "::") or entry.startswith(prefix + "/")


out = []
for line in open(W + "/tests/acceptance/serial-only.txt"):
    entry, _, comment = line.partition(" #")
    entry = entry.strip()
    if not entry or entry.startswith("#") or not comment.strip().startswith("serial"):
        continue  # the "nightly" route runs in neither of the close's phases
    path = entry.split("::", 1)[0]
    if not any(under(entry, t) or under(path, t.split("::", 1)[0]) and "::" not in t for t in targets):
        continue
    if any(under(path, i) for i in ignore):
        continue
    if entry in deselect:
        continue
    out.append(entry)
sys.stdout.write("\n".join(out) + ("\n" if out else ""))
