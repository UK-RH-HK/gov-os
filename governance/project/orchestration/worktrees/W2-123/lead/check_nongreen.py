"""Print gov check --json's checks that are not GREEN, with their findings' codes and messages: check_nongreen.py <json>."""
import json
import sys

data = json.load(open(sys.argv[1]))


def walk(node):
    if isinstance(node, dict):
        if "status" in node and isinstance(node.get("status"), str) and node["status"] in ("RED", "YELLOW"):
            yield node
        for value in node.values():
            yield from walk(value)
    elif isinstance(node, list):
        for value in node:
            yield from walk(value)


for check in walk(data):
    name = check.get("id") or check.get("family") or check.get("name")
    findings = check.get("findings") or []
    print(f"{check['status']}: {name}: {len(findings)} finding(s)")
    for finding in findings[:6]:
        text = finding if isinstance(finding, str) else json.dumps(finding)
        print("   ", text[:300])
