"""Gate (d) as the close reads it: every path where the working tree is not HEAD (gov.close.repo.tree_differences),
less a refused close's repair ticket. Prints one path per line; exits 1 if any."""
import sys
from pathlib import Path

from gov.close.repo import tree_differences
from gov.tasks.tickets import TICKETS_REL, frontmatter

root = Path("/home/usain/Dynamic-Agentic-Engineering-OS")
ticket = sys.argv[1] if len(sys.argv) > 1 else ""


def repair_ticket(state: str, path: str) -> bool:
    if not ticket or state != "??" or not path.endswith(".md") or path.rsplit("/", 1)[0] != TICKETS_REL:
        return False
    return (frontmatter(root / path) or {}).get("parent") == ticket


paths = sorted({path for state, path in tree_differences(root) if not repair_ticket(state, path)})
for path in paths:
    print(path)
sys.exit(1 if paths else 0)
