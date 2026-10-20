"""W2-50 run 8: the close's probe gate and unmeasured-commit gate asked read-only at this head (no close is run).

Also asked at the outward merge's tree as `git merge-tree` computes it is not possible without a commit; this
asks the gate at HEAD, as a close of this branch would, and reports what it finds.
"""
from pathlib import Path

from gov.close import command as c
from gov.tasks.tickets import TICKETS_REL, frontmatter

root = Path("/home/usain/gov-os-worktrees/W2-50")
ticket = "DAEO-kl5e"
front = frontmatter(root / TICKETS_REL / f"{ticket}.md")
wbs = front.get("wbs_id") or front.get("external-ref") or ticket
commits = c._ticket_commits(root, ticket)
others = c._commits_since(root, commits)
tickets = c._tickets_of_head(root)
inside, own = c._work_of(front, ticket, wbs)
try:
    brought = c._check_probe(root, ticket, commits, others, inside, own, tickets) or frozenset()
    print("probe gate: passes; merges measured:", sorted(b[:12] for b in brought))
except c._Finding as f:
    print("probe gate: REFUSES:", f.args)
    brought = frozenset()
try:
    c._check_unmeasured(ticket, [x for x in others if x["sha"] not in brought], own, tickets)
    print("unmeasured gate: passes")
except c._Finding as f:
    print("unmeasured gate: REFUSES:", f.args)
