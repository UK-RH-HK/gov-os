"""Shorten every exact 40-digit hexadecimal run in the files of one folder to its first 12 digits (row W2-L423's rule).

Run: shorten_ids.py <folder>. Prints each file changed and how many runs it shortened.
"""

import re
import sys
from pathlib import Path

RUN = re.compile(r"(?<![0-9a-f])([0-9a-f]{12})[0-9a-f]{28}(?![0-9a-f])")

for path in sorted(Path(sys.argv[1]).rglob("*")):
    if not path.is_file():
        continue
    text = path.read_text(encoding="utf-8", errors="surrogateescape")
    new, count = RUN.subn(r"\1", text)
    if count:
        path.write_text(new, encoding="utf-8", errors="surrogateescape")
        print(path.name, count)
