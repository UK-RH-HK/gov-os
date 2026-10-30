"""Print the last JSON object's session id, turns, cost and result from a worker log."""
import json
import sys

text = open(sys.argv[1], encoding="utf-8").read()
decoder = json.JSONDecoder()
found, position = None, 0
while True:
    start = text.find("{", position)
    if start < 0:
        break
    try:
        value, end = decoder.raw_decode(text, start)
    except ValueError:
        position = start + 1
        continue
    if isinstance(value, dict) and "result" in value:
        found = value
    position = end
if found is None:
    print("no result object")
else:
    print(found.get("session_id"), found.get("num_turns"), found.get("total_cost_usd"), found.get("is_error"))
    print(found.get("result"))
