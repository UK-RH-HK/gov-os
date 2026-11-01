"""Pick the serial-only entries the scoped selection keeps: not under an --ignore path, not --deselect-ed.
Writes one entry per line to the output file (the GOV_CLOSE_SERIAL_ONLY_GIVEN value and the run's arguments)."""
import sys
from pathlib import Path

root = Path("/home/usain/gov-os-worktrees/W2-04")
opts = Path(sys.argv[1]).read_text(encoding="utf-8").split("\n")
ignores = [o.split("=", 1)[1] for o in opts if o.startswith("--ignore=")]
deselects = {o.split("=", 1)[1] for o in opts if o.startswith("--deselect=")}
ignores_rel = [str(Path(p).relative_to(root)) if p.startswith(str(root)) else p for p in ignores]
deselects_rel = {str(Path(p.split("::")[0]).relative_to(root)) + ("::" + p.split("::", 1)[1] if "::" in p else "")
                 if p.startswith(str(root)) else p for p in deselects}
kept = []
for line in (root / "tests/acceptance/serial-only.txt").read_text(encoding="utf-8").splitlines():
    entry = line.split("#", 1)[0].strip()
    if not entry:
        continue
    path = entry.split("::")[0]
    if any(path == ig or path.startswith(ig.rstrip("/") + "/") for ig in ignores_rel):
        continue
    if entry in deselects_rel or path in deselects_rel:
        continue
    kept.append(entry)
Path(sys.argv[2]).write_text("\n".join(kept) + ("\n" if kept else ""), encoding="utf-8")
print(len(kept), "serial-only entries kept")
for k in kept:
    print(" ", k)
