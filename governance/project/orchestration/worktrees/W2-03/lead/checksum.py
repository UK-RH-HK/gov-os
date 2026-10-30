"""Summarise a gov check --json output: overall status, and each check that is not GREEN with its first finding."""

import json
import sys
from collections import Counter

document = json.load(open(sys.argv[1]))
result = document.get("result", document)
checks = result.get("checks") or result.get("results") or []
if isinstance(checks, dict):
    checks = [dict(value, id=key) for key, value in checks.items()]
print("ok:", document.get("ok"), "keys:", sorted(result)[:12])
print("overall:", result.get("status") or result.get("overall"))
print("statuses:", Counter(check.get("status") for check in checks))
for check in checks:
    if check.get("status") != "GREEN":
        findings = check.get("findings") or []
        first = findings[0] if findings else {}
        print("-", check.get("id"), check.get("status"), str(first.get("message", first))[:300])
