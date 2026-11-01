"""Prints the result of the last JSON object in a worker's launch log (the launcher may write lines before it)."""
import json
import sys

text = open(sys.argv[1], encoding="utf-8").read()
dec = json.JSONDecoder()
last = None
i = 0
while i < len(text):
    j = text.find("{", i)
    if j < 0:
        break
    try:
        obj, end = dec.raw_decode(text, j)
        last = obj
        i = end
    except ValueError:
        i = j + 1
if last is None:
    sys.exit("no JSON object")
print("session:", last.get("session_id"), "turns:", last.get("num_turns"), "error:", last.get("is_error"),
      "cost:", last.get("total_cost_usd"))
print(last.get("result"))
