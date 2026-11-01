"""Summarises a tripwire compare's JSON (from a file) for the trees named, and counts the rest by tree."""
import collections
import json
import sys

data = json.load(open(sys.argv[1], encoding="utf-8"))
mine = sys.argv[2:]
other = collections.Counter()
for c in data.get("changes", []):
    tree = c.get("tree", "")
    if any(tree == m for m in mine):
        print(json.dumps(c))
    else:
        other[tree] += 1
print("other trees:", dict(other))
