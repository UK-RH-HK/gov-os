"""Write the scoped run's argument files from select-3.json: the pytest options, and the selected serial-only entries."""
import json
from pathlib import Path

LEAD = Path("/home/usain/gov-os-worktrees/W2-95/.gov-runtime/scratch/lead")
ROOT = Path("/home/usain/gov-os-worktrees/W2-95")
sel = json.loads((LEAD / "log/select-3.json").read_text())
(LEAD / "verify-opts.txt").write_text("\n".join(sel["pytest_options"]) + "\n")

targets = [s["target"] for s in sel["selected"]]
deselected = set(sel.get("deselect") or [])
serial = []
for line in (ROOT / "tests/acceptance/serial-only.txt").read_text().splitlines():
    entry = line.split(" #", 1)[0].strip()
    if not entry or entry.startswith("#"):
        continue
    file_part = entry.split("::", 1)[0]
    chosen = any(entry.startswith(t) or file_part == t.split("::", 1)[0] and ("::" not in t or t == entry)
                 or (t.endswith("/") and file_part.startswith(t)) for t in targets)
    if chosen and entry not in deselected and (ROOT / file_part).exists():
        serial.append(entry)
(LEAD / "verify-serial.txt").write_text("\n".join(serial) + ("\n" if serial else ""))
print("scope:", sel.get("scope"), "core_changed:", sel.get("core_changed"), "unplaced:", sel.get("unplaced"))
print("options:", len(sel["pytest_options"]), "selected targets:", len(targets), "serial entries selected:", len(serial))
for entry in serial:
    print(" ", entry)
