"""Print the findings of every check of gov check --json that is not GREEN (lead's scratch)."""
import json
import sys
from pathlib import Path


def walk(node):
    if isinstance(node, dict):
        if "id" in node and "status" in node and "findings" in node:
            yield node
        for value in node.values():
            yield from walk(value)
    elif isinstance(node, list):
        for value in node:
            yield from walk(value)


data = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
seen = set()
for check in walk(data):
    if check["status"] == "GREEN" or check["id"] in seen:
        continue
    seen.add(check["id"])
    print(check["id"], check["status"], check.get("reason", ""))
    for finding in check["findings"][:6]:
        print("   ", json.dumps(finding)[:400])
