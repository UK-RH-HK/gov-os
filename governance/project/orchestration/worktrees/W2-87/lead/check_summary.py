"""Summarise gov check --json: every check that is not green, and the retrieval-regression check, with findings."""
import json
import sys

text = open(sys.argv[1], encoding="utf-8", errors="replace").read()
data = json.loads(text[text.index('{"ok"'):])
details = data.get("error", {}).get("details") or data.get("result") or {}


def walk(value):
    if isinstance(value, dict):
        if "id" in value and "status" in value and "family" in value:
            yield value
        for item in value.values():
            yield from walk(item)
    elif isinstance(value, list):
        for item in value:
            yield from walk(item)


for check in walk(details):
    if check["status"] != "GREEN" or check["family"] == "retrieval regression":
        print(f"- {check['family']} / {check['id']}: {check['status']} ({check.get('severity')})")
        for finding in (check.get("findings") or [])[:4]:
            print("    ", json.dumps(finding)[:400])
