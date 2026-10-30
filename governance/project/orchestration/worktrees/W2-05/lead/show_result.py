"""Print the `result` of the last JSON object in a worker's log (the launcher may print lines before it)."""
import json
import sys

text = open(sys.argv[1], encoding="utf-8").read()
start = text.rfind('{"')
while start >= 0:
    try:
        obj = json.loads(text[start:])
        break
    except json.JSONDecodeError:
        start = text.rfind('{"', 0, start)
else:
    print("no JSON object found")
    sys.exit(1)
print("session_id:", obj.get("session_id"), "| is_error:", obj.get("is_error"), "| turns:", obj.get("num_turns"),
      "| cost:", obj.get("total_cost_usd"), "| denials:", len(obj.get("permission_denials") or []))
for d in obj.get("permission_denials") or []:
    print("DENIAL:", json.dumps(d)[:400])
print(obj.get("result"))
