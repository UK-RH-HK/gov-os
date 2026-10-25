"""List the gov check results that are not GREEN, and rewrite the log with 12-digit hashes (row W2-L423's rule)."""
import json
import re
import sys

path = sys.argv[1]
raw = open(path, encoding="utf-8").read()
short = re.sub(r"\b([0-9a-f]{12})[0-9a-f]{28}\b", r"\1", raw)
if short != raw:
    open(path, "w", encoding="utf-8").write(short)
start = short.find("{")
data = json.loads(short[start:])


def walk(node):
    if isinstance(node, dict):
        if "id" in node and "status" in node:
            yield node
        for value in node.values():
            yield from walk(value)
    elif isinstance(node, list):
        for value in node:
            yield from walk(value)


seen = 0
for check in walk(data):
    seen += 1
    if check["status"] != "GREEN":
        codes = [f.get("code") or f.get("message") for f in check.get("findings", [])]
        print(check["id"], check["status"], check.get("severity"), codes[:5])
print("checks:", seen, "ok:", data.get("ok"))
