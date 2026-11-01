"""Summarise a tripwire compare output (JSON on stdin): our trees in full, other trees counted by kind."""
import collections
import json
import sys

OURS = ("/home/usain/gov-os-worktrees/W2-11", "/home/usain/gov-os-worktrees/W2-11-tests",
        "/home/usain/Dynamic-Agentic-Engineering-OS")
data = json.load(sys.stdin)
others = collections.Counter()
for change in data.get("changes", []):
    tree = change.get("tree", "")
    if tree in OURS:
        print(json.dumps(change))
    else:
        others[(tree, change.get("change"))] += 1
for (tree, kind), n in sorted(others.items()):
    print(f"other: {tree} | {kind} x{n}")
