"""Counts of the whole approval queue by form (read only)."""
import collections
import json
import re
import sys

rows = [json.loads(line) for line in open(sys.argv[1])]
count, example = collections.Counter(), {}
for r in rows:
    w, t = str(r["what"]), r["tool"]
    if t in ("Write", "Read", "Edit"):
        m = re.match(r"(/[^/]+/[^/]+)", w)
        key = (t, m.group(1) if m else w[:30])
    elif t == "Bash":
        key = (t, " ".join(w.split()[:2])[:40])
    else:
        key = (t, "")
    count[(key, r["outcome"])] += 1
    example.setdefault(key, w[:110])
for (key, outcome), n in sorted(count.items(), key=lambda x: -x[1])[:45]:
    print(n, key, outcome, "|", example[key].replace("\n", " "))
print(collections.Counter(r["at"][:10] for r in rows))
