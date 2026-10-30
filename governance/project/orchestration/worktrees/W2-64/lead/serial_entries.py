"""Print the entries of tests/acceptance/serial-only.txt, one per line, comments and blanks dropped (lead's scratch)."""
import sys
from pathlib import Path

for line in Path(sys.argv[1]).read_text(encoding="utf-8").splitlines():
    entry = line.split(" #", 1)[0].strip()
    if entry and not entry.startswith("#"):
        print(entry)
