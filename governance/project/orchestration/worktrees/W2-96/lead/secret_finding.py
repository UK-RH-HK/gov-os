"""Print the secrets-indexing finding's keys and short non-secret fields (paths, codes, rule ids); never a matched value."""
import json
import sys

text = open(sys.argv[1], encoding="utf-8").read()
envelope = json.loads(text[text.index('{"ok"'):].splitlines()[0])
error = envelope.get("error") or {}
checks = (error.get("details") or {}).get("checks") or (envelope.get("result") or {}).get("checks") or []
SAFE = {"code", "message", "path", "file", "rule", "rule_id", "RuleID", "File", "StartLine", "line", "store", "source", "count"}
for item in checks:
    if "secret" in str(item.get("name") or item.get("id")):
        print("check keys:", sorted(item.keys()))
        for f in item.get("findings") or []:
            if isinstance(f, dict):
                print("finding keys:", sorted(f.keys()))
                print({k: str(v)[:160] for k, v in f.items() if k in SAFE})
                for k, v in f.items():
                    if isinstance(v, dict):
                        print(" sub", k, {kk: str(vv)[:160] for kk, vv in v.items() if kk in SAFE}, "keys:", sorted(v.keys()))
                    if isinstance(v, list):
                        for e in v[:20]:
                            if isinstance(e, dict):
                                print(" item", k, {kk: str(vv)[:160] for kk, vv in e.items() if kk in SAFE}, "keys:", sorted(e.keys()))
