import sys
from pathlib import Path
from gov.launch import role
root = Path("/home/usain/gov-os-worktrees/W2-60a")
for r in ["engineer","independent-test-designer","independent-auditor","research","product-spec","orchestrator","qa-engineer","senior-engineer","ticket-lead"]:
    try:
        d = role.read_role(root, r)
        print(r, "OK", d["model"], d["effort"])
    except Exception as e:
        print(r, "REFUSED", str(e)[:200])
