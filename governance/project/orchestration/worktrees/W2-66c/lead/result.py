import json
import sys

text = open(sys.argv[1]).read()
dec = json.JSONDecoder()
last = None
i = 0
while True:
    j = text.find("{", i)
    if j < 0:
        break
    try:
        obj, end = dec.raw_decode(text, j)
    except ValueError:
        i = j + 1
        continue
    if isinstance(obj, dict) and "result" in obj:
        last = obj
    i = end
if last is None:
    print("no result object")
else:
    print("session_id:", last.get("session_id"), "cost:", last.get("total_cost_usd"))
    print(last["result"])
