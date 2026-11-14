"""What this tree's launcher does with each worker role (read_role, then the DEC-839 item 1 model check); no launch."""
from pathlib import Path
from gov.cli.errors import GovError
from gov.launch import role as roles
root = Path("/home/usain/gov-os-worktrees/W2-60a")
for r in ("independent-test-designer", "engineer", "independent-auditor", "research", "product-spec"):
    try:
        loaded = roles.read_role(root, r)
    except GovError as e:
        print(f"{r}: REFUSED at read_role: {e}")
        continue
    ok = loaded["model"] == "claude-opus-5-5"
    print(f"{r}: role-file model {loaded['model']}; --model claude-opus-5-5 {'accepted' if ok else 'REFUSED (not the role model)'}")
