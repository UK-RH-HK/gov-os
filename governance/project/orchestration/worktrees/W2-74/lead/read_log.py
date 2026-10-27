"""Print the last JSON object's session id and result from a worker log (launcher lines may come first)."""
import json
import sys

text = open(sys.argv[1], encoding="utf-8").read()
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
    print("no result object")
    sys.exit(1)
print("session_id:", last.get("session_id"), "is_error:", last.get("is_error"), "turns:", last.get("num_turns"),
      "duration_ms:", last.get("duration_ms"))
print(last["result"])
