"""Gate (e) as the close reads it (`gov close`'s `_check_trailers`): every commit of the ticket after the trailers
base and outside the accepted history carries `Implements:` and `Role:`; a merge that adds nothing of its own needs
no `Implements:` (DEC-436). Since DEC-927 (owner, standing) also: every item of every `Implements:` is a decision id
that the register holds (a role, a row or any other word is caught here, within the ticket, not at close time by
product traceability). Prints each lacking or unresolved commit; exits 1 if any.

    PYTHONPATH=<tree>/src python3 trailer_gate.py <ticket id> [<tree: the main tree (default) or a ticket worktree>]

A lead runs it on its own worktree before it returns (LEAD-w2-common, DEC-927); the queue runs it on the main tree.
"""
import re
import sys
from pathlib import Path

import yaml

from gov.close import history as _history
from gov.close.repo import ticket_commits

root = Path(sys.argv[2] if len(sys.argv) > 2 else "/home/usain/Dynamic-Agentic-Engineering-OS")
ticket = sys.argv[1]
DECISION = re.compile(r"DEC-\d+")

settings = yaml.safe_load((root / "governance/project/path-map.yaml").read_text())
register = _history.register_entries(root, settings.get(_history.REGISTER_KEY)) or {}
hist = _history.judged_history(root, settings)
commits = ticket_commits(root, ticket)
judged = [c for c in commits if (hist["after"] is None or c["sha"] in hist["after"]) and c["sha"] not in hist["accepted"]]
lacking = [(c["sha"][:12], key, c.get("subject", "")) for c in judged for key in ("Implements", "Role")
           if not c["trailers"].get(key)
           and not (key == "Implements" and len(c["parents"]) > 1 and _history.adds_nothing(root, c["sha"]))]
# DEC-927's reading: a decision id the register holds, or a Contract id (CAP-n) the record store holds, as the judge
# resolves them (`gov.close.traceability`); a role, a row or any other word is refused.
CONTRACT = re.compile(r"CAP-[0-9][0-9A-Za-z.]*")
try:
    from gov.close.traceability import _record_ids
    stored = _record_ids(root)
except Exception:  # no readable store: Contract ids cannot be confirmed, so they are refused (fails closed)
    stored = set()
unresolved = []
for c in judged:
    for value in c["trailers"].get("Implements", []):
        for item in value.replace(",", " ").split():
            ok = (DECISION.fullmatch(item) and item in register) or (CONTRACT.fullmatch(item) and item in stored)
            if not ok:
                unresolved.append((c["sha"][:12], item, c.get("subject", "")))
print(f"{ticket}: {len(commits)} commits, {len(judged)} judged, {len(lacking)} lacking, "
      f"{len(unresolved)} Implements item(s) not a decision or Contract id that resolves")
for sha, key, subject in lacking:
    print(f"  {sha} lacks {key}: {subject[:90]}")
for sha, item, subject in unresolved:
    print(f"  {sha} Implements: {item} does not resolve as a decision or Contract id: {subject[:70]}")
sys.exit(1 if lacking or unresolved else 0)
