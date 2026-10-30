"""Print the last JSON object's result (and session id, cost, turns) from a worker's launch log."""
import json
import sys

lines = open(sys.argv[1], encoding="utf-8", errors="replace").read().splitlines()
data = None
for line in reversed(lines):
    line = line.strip()
    if line.startswith("{"):
        try:
            data = json.loads(line)
            break
        except ValueError:
            continue
if data is None:
    print("\n".join(lines[-40:]))
    raise SystemExit(1)
print("session_id:", data.get("session_id"), "| turns:", data.get("num_turns"), "| cost:", data.get("total_cost_usd"),
      "| is_error:", data.get("is_error"), "| duration_s:", (data.get("duration_ms") or 0) / 1000)
print(data.get("result"))
