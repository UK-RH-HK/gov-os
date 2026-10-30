"""Print the last JSON object's result (and session id) of a worker log: lastresult.py <log>."""
import json
import sys

text = open(sys.argv[1], encoding="utf-8", errors="replace").read()
dec = json.JSONDecoder()
last = None
i = 0
while True:
    j = text.find("{", i)
    if j < 0:
        break
    try:
        obj, end = dec.raw_decode(text, j)
        if isinstance(obj, dict) and ("result" in obj or "session_id" in obj):
            last = obj
        i = end
    except ValueError:
        i = j + 1
if last is None:
    print("no JSON result found; head of log:")
    print(text[:2000])
else:
    print("session_id:", last.get("session_id"), "| is_error:", last.get("is_error"),
          "| turns:", last.get("num_turns"), "| cost:", last.get("total_cost_usd"))
    print(last.get("result"))
