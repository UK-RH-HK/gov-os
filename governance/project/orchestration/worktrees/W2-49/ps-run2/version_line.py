"""Throwaway (W2-49, DEC-741 K (1)): the version line in every capability record, 4.1 -> 4.2. Not committed."""

import sys
from pathlib import Path

OLD = "(Contract v4, version 4.1)"
NEW = "(Contract v4, version 4.2)"

folder = Path(sys.argv[1])
changed = 0
for path in sorted(folder.glob("*.md")):
    text = path.read_text(encoding="utf-8")
    if text.count(OLD) != 1:
        sys.exit(f"{path.name}: {text.count(OLD)} occurrences of the version line, expected 1")
    path.write_text(text.replace(OLD, NEW), encoding="utf-8")
    changed += 1
print(f"{changed} records changed")
