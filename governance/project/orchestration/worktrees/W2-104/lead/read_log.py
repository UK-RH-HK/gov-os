"""Print the result of the last JSON object in a worker log: python3 read_log.py <log>."""
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
    except ValueError:
        i = j + 1
        continue
    if isinstance(obj, dict) and "result" in obj:
        last = obj
    i = end
print("session:", last.get("session_id"), "is_error:", last.get("is_error"), "cost:", last.get("total_cost_usd"))
print(last["result"])
