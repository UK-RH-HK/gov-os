"""Print the last JSON object's result, session id and usage from a worker log (the launcher may write lines first)."""
import json
import sys

text = open(sys.argv[1], encoding="utf-8", errors="replace").read()
start = text.rfind('\n{"type"')
start = 0 if start < 0 and text.startswith('{') else start + 1
obj = json.loads(text[start:])
print("session_id:", obj.get("session_id"), "is_error:", obj.get("is_error"), "turns:", obj.get("num_turns"),
      "duration_s:", round((obj.get("duration_ms") or 0) / 1000))
print(obj.get("result"))
