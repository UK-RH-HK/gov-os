"""Prints the `result` (and session id, turns, duration) of the last JSON object in a worker log."""
import json
import sys

text = open(sys.argv[1], encoding="utf-8", errors="replace").read()
obj, pre = None, ""
lines = text.splitlines()
for i in range(len(lines) - 1, -1, -1):
    line = lines[i].strip()
    if line.startswith("{"):
        try:
            obj = json.loads(line)
            pre = "\n".join(lines[:i])
            break
        except ValueError:
            continue
if not obj:
    print(text[-3000:])
    sys.exit(1)
print("session_id:", obj.get("session_id"), "| is_error:", obj.get("is_error"), "| turns:", obj.get("num_turns"),
      "| duration_s:", round((obj.get("duration_ms") or 0) / 1000), "| subtype:", obj.get("subtype"))
print(obj.get("result"))
if pre.strip():
    print("--- launcher lines ---")
    print(pre.strip()[-1500:])
