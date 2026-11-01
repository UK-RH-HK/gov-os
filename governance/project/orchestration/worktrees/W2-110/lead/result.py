"""Print the last JSON object's result (and session id, cost fields) from a worker's launch log."""
import json
import sys

text = open(sys.argv[1], encoding="utf-8", errors="replace").read()
last = None
for line in text.splitlines():
    line = line.strip()
    if line.startswith("{"):
        try:
            last = json.loads(line)
        except ValueError:
            pass
if last is None:
    print("NO JSON OBJECT; head of log:")
    print(text[:3000])
    sys.exit(1)
print("session_id:", last.get("session_id"), "| is_error:", last.get("is_error"), "| turns:", last.get("num_turns"),
      "| duration_ms:", last.get("duration_ms"))
print(last.get("result"))
