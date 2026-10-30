"""Writes the serial-route entries of tests/acceptance/serial-only.txt (the ones gov close runs in its serial phase), one per line."""
import sys

src, out = sys.argv[1], sys.argv[2]
entries = []
for line in open(src, encoding="utf-8"):
    if not line.strip() or line.lstrip().startswith("#"):
        continue
    entry, _, comment = line.partition(" #")
    if comment.strip().startswith("serial"):
        entries.append(entry.strip())
open(out, "w", encoding="utf-8").write("\n".join(entries) + "\n")
print(len(entries), "serial entries")
