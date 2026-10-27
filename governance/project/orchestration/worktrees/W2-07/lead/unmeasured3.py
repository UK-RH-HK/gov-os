"""The lead's check (run 4): the judge's work-without-a-task gate, run from this worktree's src, for three tickets,
as the orchestrator's tools/unmeasured_gate.py does, but subtracting what this worktree's close subtracts before
_check_unmeasured (gate (h)'s line in command.py).

    PYTHONPATH=/home/usain/gov-os-worktrees/W2-07/src python3 unmeasured3.py <root> <ticket> [<ticket> ...]
"""
import inspect
import re
import sys
from pathlib import Path

import yaml

import gov
from gov.close import command as close
from gov.close import gates as _gates
from gov.close.repo import commits_since, names_no_task, ticket_commits, tickets_of_head
from gov.tasks.tickets import frontmatter

root = Path(sys.argv[1])
print("gov from:", gov.__file__)
print("root:", root)
# Gate (h)'s line as this worktree's close has it: the expression subtracted from the others.
source = inspect.getsource(close)
line = [l.strip() for l in source.splitlines() if "_check_unmeasured" in l and "gate(" in l]
print("gate (h) line:", line)
settings = yaml.safe_load((root / "governance" / "project" / "path-map.yaml").read_text(encoding="utf-8")) or {}
status = 0
for ticket in sys.argv[2:]:
    front = frontmatter(root / ".tickets" / (ticket + ".md")) or {}
    wbs = front.get("wbs_id") or ""
    commits = ticket_commits(root, ticket)
    others = commits_since(root, commits)
    tickets = tickets_of_head(root)
    inside, own = close._work_of(front, ticket, wbs)
    recorded = _gates.decision_records(root, others, settings)
    rest = [c for c in others if c["sha"] not in recorded]
    found = []
    for c in rest:
        changed = [p for p in c["paths"] if own(p)] if names_no_task(c, tickets) else []
        if changed:
            found.append((c["sha"][:12], changed))
    for sha, paths in found:
        print("  WORK WITHOUT A TASK:", sha, ", ".join(paths[:5]))
    print(ticket, "(" + wbs + "):", len(commits), "own commits,", len(others), "others in range,",
          len(recorded), "measured by the decision-record rule,", len(found), "unmeasured")
    if found:
        status = 1
sys.exit(status)
