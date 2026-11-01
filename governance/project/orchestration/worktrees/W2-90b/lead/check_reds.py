#!/usr/bin/env python3
"""Print the non-green checks of gov check --json's result, with their details trimmed (no file contents)."""
import json
import sys

text = open(sys.argv[1], encoding="utf-8").read()
data = json.loads(text[text.find("{"):])
result = data.get("result") or {}
checks = result.get("checks") if isinstance(result, dict) else result
if isinstance(checks, dict):
    checks = [dict(name=k, **v) for k, v in checks.items()]
for c in checks or []:
    status = str(c.get("status", "")).upper()
    if status != "GREEN":
        print("==", c.get("name") or c.get("id"), status)
        print(json.dumps({k: v for k, v in c.items() if k not in ("name", "status")})[:1200])
