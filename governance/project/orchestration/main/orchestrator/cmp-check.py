"""Compare two saved `gov check --json` outputs: python3 cmp-check.py <old name> <new name> (files under log/)."""
import json
import sys

L = "/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/log/"


def checks(name):
    found = {}

    def walk(o):
        if isinstance(o, dict):
            if "id" in o and "status" in o:
                found[o["id"]] = (o["status"], len(o.get("findings") or []), o.get("findings") or [])
            for v in o.values():
                walk(v)
        elif isinstance(o, list):
            for v in o:
                walk(v)
    walk(json.load(open(L + name)))
    return found


old, new = checks(sys.argv[1]), checks(sys.argv[2])
for key in sorted(set(old) | set(new)):
    a, b = old.get(key), new.get(key)
    if a is None or b is None or a[:2] != b[:2]:
        print(key, "|", a and a[:2], "->", b and b[:2])
        for finding in (b[2] if b else [])[:6]:
            print("     ", json.dumps(finding)[:260])
print("not green now:", sorted((k, v[0], v[1]) for k, v in new.items() if v[0] != "GREEN"))
