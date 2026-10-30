"""Print the non-green checks of run3-check.json, with long hex strings masked."""
import json
import re

PATH = "/home/usain/gov-os-worktrees/W2-26/.gov-runtime/scratch/lead/log/run3-check.json"
result = json.load(open(PATH))["result"]
for check in result["checks"]:
    status = check.get("status") or check.get("state")
    if status != "GREEN":
        text = json.dumps(check, indent=1)
        text = re.sub(r"[0-9a-f]{32,}", "<hex>", text)
        print(text[:3000])
        print("--")
