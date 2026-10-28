"""Print the last JSON object's result (and session id, cost) from a launch log."""
import json
import sys

text = open(sys.argv[1], encoding="utf-8").read()
last = None
for line in text.splitlines():
    line = line.strip()
    if line.startswith("{"):
        try:
            last = json.loads(line)
        except ValueError:
            pass
if last is None:
    print(text[-3000:])
    sys.exit(1)
print("session_id:", last.get("session_id"), "| is_error:", last.get("is_error"), "| turns:", last.get("num_turns"),
      "| duration_s:", (last.get("duration_ms") or 0) // 1000)
print(last.get("result"))
