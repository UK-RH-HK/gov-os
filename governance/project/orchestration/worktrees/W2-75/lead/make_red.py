"""Write a copy of a gov check --json envelope with the context-reproducibility check set to RED."""
import json
import sys

source, target = sys.argv[1], sys.argv[2]
with open(source, encoding="utf-8") as f:
    envelope = json.load(f)
where = envelope.get("result") if envelope.get("ok") else (envelope.get("error") or {}).get("details")
hit = 0
for check in where["checks"]:
    if check.get("id") == "context-reproducibility":
        check["status"] = "RED"
        hit += 1
with open(target, "w", encoding="utf-8") as f:
    json.dump(envelope, f)
print(f"planted RED on {hit} check(s) into {target}")
sys.exit(0 if hit == 1 else 1)
