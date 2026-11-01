"""Summarise a tripwire compare: changes in the W2-96 trees in full, others counted per tree."""
import collections
import json
import sys

data = json.load(open(sys.argv[1], encoding="utf-8"))
mine = ("/home/usain/gov-os-worktrees/W2-96", "/home/usain/gov-os-worktrees/W2-96-tests")
others = collections.Counter()
for change in data.get("changes", []):
    tree = change.get("tree", "")
    if tree in mine:
        print(json.dumps(change))
    else:
        others[(tree, change.get("change"))] += 1
for (tree, kind), count in sorted(others.items()):
    print(f"other: {tree} | {kind} | {count}")
