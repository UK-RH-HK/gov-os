"""short_hashes.py <file>...: every bare 40-hex commit hash in each file cut to its first 12 digits (row W2-L423's rule)."""
import re
import sys

FULL = re.compile(r"\b([0-9a-f]{12})[0-9a-f]{28}\b")
for path in sys.argv[1:]:
    text = open(path, encoding="utf-8").read()
    new, count = FULL.subn(r"\1", text)
    if count:
        open(path, "w", encoding="utf-8").write(new)
    print(path, count)
