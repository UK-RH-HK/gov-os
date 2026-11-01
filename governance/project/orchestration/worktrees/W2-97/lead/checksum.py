"""Summarises a failing gov check --json envelope (argv[1]): every check that is not GREEN, with its findings."""
import json
import sys

text = open(sys.argv[1], encoding="utf-8").read()
d = json.loads(text[text.find("{"):])
print("ok:", d.get("ok"), "|", (d.get("error") or {}).get("message"))
det = (d.get("error") or {}).get("details") or {}
print("detail keys:", list(det))
for c in det.get("checks") or []:
    if c.get("status") != "GREEN":
        print("-", c.get("id"), c.get("family"), c.get("status"), c.get("severity"), "|",
              json.dumps(c.get("findings"))[:700])
