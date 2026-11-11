"""Extract the reviewer's final result from its launch log, save it as a draft, and compute READY with verdict.ready."""
import json
import sys

sys.path.insert(0, "/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools")
import verdict  # noqa: E402

LOG = "/home/usain/gov-os-worktrees/W2-40/.gov-runtime/scratch/lead/log/rev-1.json"
OUT = "/home/usain/gov-os-worktrees/W2-40/.gov-runtime/scratch/lead/probes/rev-1-result.md"

text = open(LOG, encoding="utf-8").read()
last = None
dec = json.JSONDecoder()
i = 0
while True:
    j = text.find("{", i)
    if j < 0:
        break
    try:
        obj, end = dec.raw_decode(text, j)
    except ValueError:
        i = j + 1
        continue
    if isinstance(obj, dict) and "result" in obj:
        last = obj
    i = end
if last is None:
    sys.exit("no result object in the log")
result = last["result"]
with open(OUT, "w", encoding="utf-8") as f:
    f.write(result)
print("session_id", last.get("session_id"), "chars", len(result))
print("ready", verdict.ready(result))
