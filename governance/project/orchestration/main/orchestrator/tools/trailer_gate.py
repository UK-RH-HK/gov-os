"""Gate (e) as the close reads it (`gov close`'s `_check_trailers`): every commit of the ticket after the trailers
base and outside the accepted history carries `Implements:` and `Role:`; a merge that adds nothing of its own needs
no `Implements:` (DEC-436). Prints each lacking commit; exits 1 if any.

    PYTHONPATH=<main tree>/src python3 trailer_gate.py <ticket id>
"""
import sys
from pathlib import Path

from gov.close import history as _history
from gov.close.repo import ticket_commits

root = Path("/home/usain/Dynamic-Agentic-Engineering-OS")
ticket = sys.argv[1]
import yaml  # noqa: E402

settings = yaml.safe_load((root / "governance/project/path-map.yaml").read_text())
hist = _history.judged_history(root, settings)
commits = ticket_commits(root, ticket)
judged = [c for c in commits if (hist["after"] is None or c["sha"] in hist["after"]) and c["sha"] not in hist["accepted"]]
lacking = [(c["sha"][:12], key, c.get("subject", "")) for c in judged for key in ("Implements", "Role")
           if not c["trailers"].get(key)
           and not (key == "Implements" and len(c["parents"]) > 1 and _history.adds_nothing(root, c["sha"]))]
print(f"{ticket}: {len(commits)} commits, {len(judged)} judged, {len(lacking)} lacking")
for sha, key, subject in lacking:
    print(f"  {sha} lacks {key}: {subject[:90]}")
sys.exit(1 if lacking else 0)
