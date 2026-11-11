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
        if isinstance(obj, dict) and "result" in obj:
            last = obj
        i = end
    except ValueError:
        i = j + 1
if last is None:
    print("no result object")
    sys.exit(1)
r = last["result"]
lim = int(sys.argv[2]) if len(sys.argv) > 2 else 4000
print("session_id:", last.get("session_id"))
print(r[:lim])
