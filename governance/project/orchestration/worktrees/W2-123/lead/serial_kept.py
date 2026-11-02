"""Print the serial-only entries the selection keeps (read-only): serial_kept.py <select.json> <serial-only.txt>."""
import json
import sys
from pathlib import Path

select = json.loads(Path(sys.argv[1]).read_text())
ignored = [p.rstrip("/") for p in select["ignore"]]
deselected = set(select["deselect"])
for raw in Path(sys.argv[2]).read_text().splitlines():
    entry = raw.split("#", 1)[0].strip()
    if not entry:
        continue
    path = entry.split("::", 1)[0]
    if any(path == p or path.startswith(p + "/") for p in ignored) or entry in deselected:
        continue
    print(entry)
