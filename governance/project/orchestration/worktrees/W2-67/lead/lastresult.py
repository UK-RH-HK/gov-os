"""Print the last JSON object's result (and session id) from a launched worker's log (launcher lines may come first)."""
import json
import sys

text = open(sys.argv[1], encoding="utf-8").read()
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
    print("NO RESULT OBJECT")
    sys.exit(1)
print("session_id:", last.get("session_id"), "is_error:", last.get("is_error"), "turns:", last.get("num_turns"))
print(last["result"])
