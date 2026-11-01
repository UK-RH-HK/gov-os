"""lastjson.py <log>: the last JSON object of a launched session's log: its result, and its cost, time and ids."""
import json
import sys

text = open(sys.argv[1], encoding="utf-8", errors="replace").read()
start = text.rfind('{"type"')
if start < 0:
    start = text.find("{")
data = json.loads(text[start:])
for key in ("session_id", "total_cost_usd", "duration_ms", "num_turns", "is_error", "subtype"):
    print(f"{key}: {data.get(key)}")
print("----- result")
print(data.get("result"))
