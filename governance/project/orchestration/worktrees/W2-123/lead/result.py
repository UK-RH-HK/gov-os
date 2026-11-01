"""Print a launched worker's last JSON object's session id, turns, cost and result: result.py <log.json>."""
import json
import sys

text = open(sys.argv[1]).read()
decoder, found, at = json.JSONDecoder(), None, 0
while True:
    at = text.find("{", at)
    if at < 0:
        break
    try:
        obj, end = decoder.raw_decode(text, at)
    except ValueError:
        at += 1
        continue
    if isinstance(obj, dict) and "result" in obj:
        found = obj
    at = end
if found is None:
    print(text[-3000:])
    sys.exit(1)
print("session_id:", found.get("session_id"), "| turns:", found.get("num_turns"), "| cost:",
      found.get("total_cost_usd"), "| is_error:", found.get("is_error"))
print(found["result"])
