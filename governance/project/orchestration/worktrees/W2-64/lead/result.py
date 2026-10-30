"""Print a worker log's last JSON object's result, session id and cost (lead's scratch)."""
import json
import sys
from pathlib import Path

lines = Path(sys.argv[1]).read_text(encoding="utf-8", errors="replace").splitlines()
objs = [(n, line) for n, line in enumerate(lines) if line.startswith("{")]
if not objs:
    print("NO JSON; tail:")
    print("\n".join(lines[-40:]))
    sys.exit(1)
n, line = objs[-1]
obj = json.loads(line)
print("launcher lines before:", "\n".join(lines[:n])[-1500:])
print("session_id:", obj.get("session_id"), "is_error:", obj.get("is_error"), "turns:", obj.get("num_turns"),
      "cost:", obj.get("total_cost_usd"), "duration_s:", (obj.get("duration_ms") or 0) / 1000)
print(obj.get("result"))
