import json
import sys

text = open(sys.argv[1], encoding="utf-8").read()
start = text.rfind('{"type"')
if start < 0:
    start = text.find("{")
pre = text[:start].strip()
if pre:
    print("PRE-JSON LINES:\n" + pre[-2000:] + "\n---")
try:
    doc = json.loads(text[start:])
except ValueError as exc:
    print("not JSON:", exc)
    print(text[-3000:])
    sys.exit(0)
for key in ("subtype", "is_error", "num_turns", "duration_ms", "session_id", "total_cost_usd"):
    print(key, "=", doc.get(key))
print("RESULT:\n" + str(doc.get("result")))
