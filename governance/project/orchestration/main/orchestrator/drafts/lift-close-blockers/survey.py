"""Read-only survey of the pre-measure gates of `gov close` (the commit gates, DEC-868 (3)) for given tickets.

Usage: PYTHONPATH=<main tree>/src python3 survey.py [--ignore-reviewer-role] <root> <ticket> [<ticket> ...]   (root: a clone, never the main tree)

It calls the close command's own gate functions, in the order `run` calls them, and writes nothing (it prints).
It is the part of `gov.close.command.run` before `_scope`: _check_probe (FULL profile), _check_trailers,
_check_accepted_history, decision_records + _check_unmeasured, check_ratchet_lists for both lists.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import yaml

from gov.close import command as C, gates as G, history as H, ratchet as R
from gov.tasks.tickets import TICKETS_REL, frontmatter


def survey(root: Path, ticket: str) -> list[dict]:
    path_map = yaml.safe_load((root / H.PATH_MAP_REL).read_text(encoding="utf-8")) or {}
    front = frontmatter(root / TICKETS_REL / f"{ticket}.md")
    if front is None:
        return [{"gate": "TICKET_UNKNOWN", "what": ticket, "why": "no ticket file"}]
    profile = str(front.get("profile", "STANDARD")).upper()
    wbs = front.get("wbs_id") or front.get("external-ref") or ticket
    history = H.judged_history(root, path_map)
    commits = C._ticket_commits(root, ticket)
    others = C._commits_since(root, commits)
    tickets = C._tickets_of_head(root)
    inside, own = C._work_of(front, ticket, wbs)
    out: list[dict] = []

    def gate(name, check, *a, **kw):
        try:
            return check(*a, **kw)
        except C._Finding as f:
            for line in f.findings:
                out.append({"gate": f"{name}:{f.code}", "what": line, "why": f.message if len(f.findings) == 1 else ""})
        return None

    brought = frozenset()
    if profile == "FULL":
        brought = gate("probe", C._check_probe, root, ticket, commits, others, inside, own, tickets,
                       accepted={}) or frozenset()
    gate("trailers", C._check_trailers, root, commits, ticket, history)
    gate("accepted_history", C._check_accepted_history, history["refused"])
    recorded = G.decision_records(root, others, path_map)
    gate("unmeasured", C._check_unmeasured, ticket, [c for c in others if c["sha"] not in brought | recorded], own,
         tickets)
    for key in (R.ACCEPTED_REDS, R.LOAD_SENSITIVE):
        gate(f"ratchet:{key}", G.check_ratchet_lists, root, key)
    out.append({"gate": "_info", "what": f"{ticket} profile={profile} ticket_commits={len(commits)} "
                                         f"range_others={len(others)} brought={len(brought)} recorded={len(recorded)}",
                "why": ""})
    return out


if __name__ == "__main__":
    args = sys.argv[1:]
    if args and args[0] == "--ignore-reviewer-role":  # show what the probe gate asks after its first finding
        C.REVIEWER_ROLE = "__none__"
        args = args[1:]
    root = Path(args[0]).resolve()
    result = {t: survey(root, t) for t in args[1:]}
    print(json.dumps(result, indent=1))
