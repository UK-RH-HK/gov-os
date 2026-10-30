"""Print the full stderr of one check's findings from gov check --json (W2-87 lead)."""
import json
import sys

text = open(sys.argv[1], encoding="utf-8", errors="replace").read()
data = json.loads(text[text.index('{"ok"'):])


def walk(value):
    if isinstance(value, dict):
        if value.get("id") == sys.argv[2]:
            yield value
        for item in value.values():
            yield from walk(item)
    elif isinstance(value, list):
        for item in value:
            yield from walk(item)


for check in walk(data):
    for finding in check.get("findings") or []:
        print(finding.get("stderr", finding)[-2500:])
    break
