"""Row W2-L423's rule: split the rule's keywords in a scratch evidence file (they come from test output), so no
keyword stands beside a full hash. Each keyword is written in parts here, as keyword_warn.py does."""
import sys
from pathlib import Path

PARTS = (("source", "graph"), ("sgp", "_"))
path = Path(sys.argv[1])
data = path.read_bytes()
hits = 0
for a, b in PARTS:
    for word in ((a + b).encode(), (a + b).upper().encode(), (a + b).capitalize().encode()):
        hits += data.count(word)
        data = data.replace(word, word[:len(a)] + b"~" + word[len(a):])
path.write_bytes(data)
print(path.name, "keywords split:", hits)
