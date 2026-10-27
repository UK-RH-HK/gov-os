"""Splits the serial-only list by route into serial-entries.txt and nightly-entries.txt (verify2), as the list's
header gives the form: the entry before ` #`, the route the first word of the comment. An unreadable route is
kept serial (fail closed)."""
from pathlib import Path

ROOT = Path("/home/usain/gov-os-worktrees/W2-57")
OUT = ROOT / ".gov-runtime/scratch/lead/log/verify2"
serial, nightly, seen = [], [], set()
for line in (ROOT / "tests/acceptance/serial-only.txt").read_text(encoding="utf-8").splitlines():
    entry, _, comment = (" " + line).partition(" #")
    entry = entry.strip()
    if not entry or entry in seen:
        continue
    seen.add(entry)
    route = comment.strip().split(":", 1)[0].strip()
    (nightly if route == "nightly" else serial).append(entry)
(OUT / "serial-entries.txt").write_text("\n".join(serial) + "\n", encoding="utf-8")
(OUT / "nightly-entries.txt").write_text("\n".join(nightly) + "\n", encoding="utf-8")
print("serial", len(serial), "nightly", len(nightly))
