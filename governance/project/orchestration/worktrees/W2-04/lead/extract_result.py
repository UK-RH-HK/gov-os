import json, sys
text = open(sys.argv[1], encoding="utf-8", errors="replace").read()
last = None
dec = json.JSONDecoder()
i = 0
while True:
    j = text.find("{", i)
    if j < 0:
        break
    try:
        obj, end = dec.raw_decode(text, j)
        if isinstance(obj, dict) and "result" in obj:
            last = obj
        i = end
    except ValueError:
        i = j + 1
if last is None:
    sys.exit("no result object")
open(sys.argv[2], "w", encoding="utf-8").write(str(last.get("result", "")))
print("session", last.get("session_id"), "cost", last.get("total_cost_usd"), "chars", len(str(last.get("result", ""))))
