"""Print the `result` text of a headless session's JSON log: python3 show-result.py <log name> [from marker] [chars]."""
import json
import sys

L = "/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/log/"
d = json.load(open(L + sys.argv[1], encoding="utf-8"))
r = d.get("result", "")
i = r.find(sys.argv[2]) if len(sys.argv) > 2 else 0
n = int(sys.argv[3]) if len(sys.argv) > 3 else 100000
print("session:", d.get("session_id"), "| is_error:", d.get("is_error"), "| chars:", len(r))
print(r[max(i, 0):max(i, 0) + n])
