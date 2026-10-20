"""Reduce a specimen session log (DEC-495): keep whole the lines the counter must learn from, and reduce every
other line to its type and length. Usage: reduce.py <log.jsonl> <out.jsonl>"""
import json
import sys

KEEP_TYPES = {"assistant", "user", "cost-state", "system"}
out = []
for line in open(sys.argv[1], encoding="utf-8"):
    if not line.strip():
        continue
    d = json.loads(line)
    att = d.get("attachment") if isinstance(d.get("attachment"), dict) else None
    att_type = att.get("type", "") if att else ""
    if d.get("type") in KEEP_TYPES or att_type.startswith("hook"):
        out.append(d)
    else:
        out.append({"type": d.get("type"), "sessionId": d.get("sessionId"),
                    "attachment": {"type": att_type} if att else None,
                    "_reduced": True, "_original_chars": len(line)})
with open(sys.argv[2], "w", encoding="utf-8") as f:
    for d in out:
        f.write(json.dumps(d) + "\n")
kinds = {}
for d in out:
    k = (d.get("type"), (d.get("attachment") or {}).get("type", "") if isinstance(d.get("attachment"), dict) else "",
         (d.get("attachment") or {}).get("hookEvent", "") if isinstance(d.get("attachment"), dict) else "")
    kinds[k] = kinds.get(k, 0) + 1
for k, n in sorted(kinds.items(), key=str):
    print(n, k)
