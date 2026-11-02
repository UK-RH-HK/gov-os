"""tw_own.py <compare.json> <tree>: the tripwire changes of one tree, one per line."""
import json
import sys

data = json.load(open(sys.argv[1]))
items = data.get("changes", data) if isinstance(data, dict) else data
for item in items:
    if isinstance(item, dict) and item.get("tree") == sys.argv[2]:
        print({k: v for k, v in item.items() if k != "tree"})
