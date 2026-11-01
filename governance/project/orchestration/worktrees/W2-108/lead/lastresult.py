"""Print the last JSON object's result (and session id, cost, turns) from a worker's log. usage: lastresult.py <log>"""
import json
import sys

text = open(sys.argv[1], encoding="utf-8", errors="replace").read()
last = None
decoder = json.JSONDecoder()
i = 0
while i < len(text):
    j = text.find("{", i)
    if j < 0:
        break
    try:
        obj, end = decoder.raw_decode(text, j)
        if isinstance(obj, dict) and "result" in obj:
            last = obj
        i = end
    except ValueError:
        i = j + 1
if last is None:
    print("no result object; head of log:")
    print(text[:2000])
    sys.exit(1)
print("session_id:", last.get("session_id"), "| is_error:", last.get("is_error"), "| turns:", last.get("num_turns"),
      "| cost:", last.get("total_cost_usd"), "| duration_s:", (last.get("duration_ms") or 0) / 1000)
print(last.get("result"))
