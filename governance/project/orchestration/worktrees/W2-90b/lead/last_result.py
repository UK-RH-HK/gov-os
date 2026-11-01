#!/usr/bin/env python3
"""Print the `result` (and session id, cost) of the last JSON object in a launch log."""
import json
import sys

text = open(sys.argv[1], encoding="utf-8", errors="replace").read()
obj = {}
for start in [i for i, ch in enumerate(text) if ch == "{" and (i == 0 or text[i - 1] == "\n")][::-1]:
    try:
        obj = json.loads(text[start:])
        break
    except ValueError:
        continue
print("session_id:", obj.get("session_id"), "| is_error:", obj.get("is_error"), "| cost:", obj.get("total_cost_usd"),
      "| turns:", obj.get("num_turns"), "| duration_s:", (obj.get("duration_ms") or 0) / 1000)
print(obj.get("result", "<no result>"))
