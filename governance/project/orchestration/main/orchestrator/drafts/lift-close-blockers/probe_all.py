"""Every finding the probe gate would give a FULL ticket, not only its first (`_check_probe` ends at its first).

A re-implementation of the loop's per-commit tests in `gov.close.command._check_probe` (read-only; prints).
Usage: PYTHONPATH=<main tree>/src python3 probe_all.py <root> <ticket>
It judges the record of the final round (the one no other record's probed commit descends from), as the gate does.
"""
from __future__ import annotations

import sys
from pathlib import Path

from gov.close import command as C, history as H
from gov.tasks.tickets import TICKETS_REL, frontmatter

root, ticket = Path(sys.argv[1]).resolve(), sys.argv[2]
front = frontmatter(root / TICKETS_REL / f"{ticket}.md")
wbs = front.get("wbs_id") or front.get("external-ref") or ticket
inside, own = C._work_of(front, ticket, wbs)
tickets = C._tickets_of_head(root)
commits = C._ticket_commits(root, ticket)
others = C._commits_since(root, commits)
print("reviewer-role commits in range:", [c["sha"][:12] for c in commits + others
                                           if C.REVIEWER_ROLE in c["trailers"].get("Role", [])])
records = {}
for path in sorted((root / "docs" / "probes" / ticket).glob("*.md")):
    pf = frontmatter(path)
    if pf and pf.get("type") == "probe" and pf.get("task") == ticket:
        records[path.name] = C._full_id(root, str(pf.get("probed_commit") or ""))
rounds = set(filter(None, records.values()))
final = [n for n, p in records.items() if p and not any(
    o != p and not C._git(root, "merge-base", "--is-ancestor", p, o, ok=(0, 1), code=True) for o in rounds)]
print("records:", records)
print("final-round records:", final)
for name in final:
    probed = records[name]
    after = {c["sha"]: c for c in C._read_commits(root, f"{probed}..HEAD")}
    print(f"-- {name}: probed {probed[:12]}, {len(after)} commits after it")
    for sha, c in after.items():
        if C.REVIEWER_ROLE in c["trailers"].get("Role", []):
            print("  reviewer role after probed:", sha[:12])
        holds = any(not C._git(root, "merge-base", "--is-ancestor", probed, p, ok=(0, 1), code=True)
                    for p in c["parents"]) if len(c["parents"]) > 1 else False
        if holds or (len(c["parents"]) > 1 and ticket in c["trailers"].get("Task", [])):
            expected = H.own_merge(root, c["parents"])
            dropped = [p for p in H.differing(root, expected or probed, sha) if own(p)]
            if dropped:
                print(f"  merge {sha[:12]} drops probed paths: {dropped}")
            continue
        judged = own if len(c["parents"]) < 2 else inside
        changed = [p for p in c["paths"] if judged(p)] if C._names_no_task(c, tickets) else []
        if changed:
            print(f"  stale: {sha[:12]} names no task, changes {changed}")
    ticket_file = f"{TICKETS_REL}/{ticket}.md"
    for c in commits:
        if c["sha"] not in after or len(c["parents"]) > 1:
            continue
        if c["paths"] == [ticket_file] and c["trailers"].get("Role") in (["orchestrator"], ["owner"]):
            continue
        for p in c["paths"]:
            if own(p):
                print(f"  ticket commit {c['sha'][:12]} (Role {c['trailers'].get('Role')}) changes {p} after probed")
