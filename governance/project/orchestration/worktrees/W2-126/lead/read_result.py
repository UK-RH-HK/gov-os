"""Print the last JSON object's session_id, error flag and result from a worker log."""
import json
import sys

text = open(sys.argv[1]).read()
decoder = json.JSONDecoder()
last = None
i = 0
while True:
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
    print("NO RESULT OBJECT")
    print(text[:3000])
else:
    print("session_id:", last.get("session_id"))
    print("is_error:", last.get("is_error"), "turns:", last.get("num_turns"), "cost:", last.get("total_cost_usd"))
    print(last.get("result"))
