"""From select_tests.py's JSON: writes the pytest options file and the selected serial-only entries.

Outputs (under /tmp/gov-os-lead-W2-107/): options.txt (one option per line), serial.txt (the selected serial-only entries,
one per line). An entry is selected when it lies under a selected target, under no --ignore path, and is not deselected.
"""
import json
from pathlib import Path

ROOT = Path("/home/usain/gov-os-worktrees/W2-107")
OUT = Path("/tmp/gov-os-lead-W2-107")
plan = json.loads((OUT / "select.json").read_text())
(OUT / "options.txt").write_text("\n".join(plan["pytest_options"]) + "\n")
targets = [item["target"] for item in plan["selected"]]
ignores = [str(Path(p).relative_to(ROOT)) if p.startswith("/") else p for p in plan["ignore"]]
deselects = set(plan["deselect"])


def under(entry: str, prefix: str) -> bool:
    prefix = prefix.rstrip("/")
    return entry == prefix or entry.startswith(prefix + "/") or entry.startswith(prefix + "::")


entries = []
for line in (ROOT / "tests/acceptance/serial-only.txt").read_text().splitlines():
    entry = line.split(" #")[0].strip()
    if not entry or entry.startswith("#"):
        continue
    if not any(under(entry, target) or under(target, entry) for target in targets):
        continue
    if any(under(entry, ignore) for ignore in ignores) or entry in deselects:
        continue
    entries.append(entry)
(OUT / "serial.txt").write_text("".join(f"{entry}\n" for entry in entries))
print(len(plan["pytest_options"]), "options;", len(entries), "serial entries")
for entry in entries:
    print(" ", entry)
