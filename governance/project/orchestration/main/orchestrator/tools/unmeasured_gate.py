"""Gate (h) of the close queue: the close's work-without-a-task gate (`_check_unmeasured`, DEC-490, DEC-500), run with
the pinned judge's own code before a close spends its full run (W2-58's refused close of 2026-10-22).

    <the current pin's interpreter, the first line of ~/.local/bin/gov> -E unmeasured_gate.py <ticket id>

Prints each commit of the ticket's range that names no task and changes the ticket's work, with the paths; exits 1
if any. (Merges that are git's own merge on a FULL ticket's probed paths, which the probe gate exempts, are not
subtracted here: the check is the stricter one.)
"""
import sys
from pathlib import Path

from gov.close import command as close
from gov.close.repo import commits_since, names_no_task, ticket_commits, tickets_of_head
from gov.tasks.tickets import frontmatter

root = Path("/home/usain/Dynamic-Agentic-Engineering-OS")
ticket = sys.argv[1]
front = frontmatter(root / ".tickets" / f"{ticket}.md") or {}
wbs = front.get("wbs_id") or ""
commits = ticket_commits(root, ticket)
others = commits_since(root, commits)
tickets = tickets_of_head(root)
inside, own = close._work_of(front, ticket, wbs)
# As the pinned close does since W2-07 (DEC-896 item 1): decision-record commits of governance records only, naming
# an ACCEPTED owner decision, are measured by that decision (`gates.decision_records`, the judge's own function).
try:
    import yaml
    from gov.close import gates as _gates
    settings = yaml.safe_load((root / "governance" / "project" / "path-map.yaml").read_text(encoding="utf-8")) or {}
    recorded = _gates.decision_records(root, others, settings)
except ImportError:  # a judge before W2-07 has no such rule: nothing is subtracted
    recorded = set()
others = [c for c in others if c["sha"] not in recorded]
found = []
for c in others:
    changed = [p for p in c["paths"] if own(p)] if names_no_task(c, tickets) else []
    if changed:
        found.append((c["sha"][:12], changed))
for sha, paths in found:
    print(f"WORK WITHOUT A TASK: commit {sha} changes {', '.join(paths[:5])}")
print(f"{ticket} ({wbs}): {len(commits)} own commits, {len(others)} others in range, {len(found)} unmeasured")
sys.exit(1 if found else 0)
