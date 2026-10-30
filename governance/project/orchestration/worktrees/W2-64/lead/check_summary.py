"""Summarise gov check --json: each check's id, status and first findings (lead's scratch)."""
import json
import sys
from pathlib import Path

text = Path(sys.argv[1]).read_text(encoding="utf-8")
data = json.loads(text[text.find("{"):])
result = data.get("result", data)
checks = result.get("checks") or result.get("results") or []
print("top keys:", list(result)[:12], "ok:", data.get("ok"))
for check in checks:
    status = check.get("status")
    line = f"{check.get('id')}: {status}"
    if status != "GREEN":
        for finding in (check.get("findings") or [])[:4]:
            line += "\n    " + json.dumps(finding)[:300]
    print(line)
