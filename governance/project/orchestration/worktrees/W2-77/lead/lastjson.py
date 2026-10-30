"""Print the last JSON object's result (and session id, cost, turns) of a worker log."""
import json
import sys

text = open(sys.argv[1], encoding="utf-8", errors="replace").read()
decoder = json.JSONDecoder()
last = None
i = 0
while True:
    j = text.find("{", i)
    if j < 0:
        break
    try:
        obj, end = decoder.raw_decode(text, j)
    except ValueError:
        i = j + 1
        continue
    if isinstance(obj, dict) and "result" in obj:
        last = obj
    i = end
if last is None:
    print(text[-4000:])
    sys.exit(1)
print("session_id:", last.get("session_id"), "turns:", last.get("num_turns"), "cost:", last.get("total_cost_usd"),
      "is_error:", last.get("is_error"), "duration_ms:", last.get("duration_ms"))
print(last.get("result"))
