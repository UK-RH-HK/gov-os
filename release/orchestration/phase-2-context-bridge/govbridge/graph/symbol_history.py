#!/usr/bin/env python3
"""Symbol-introduction history (ARCHITECTURE.md section 4.6 "Symbol history (C6 temporal)"; REPAIR_PLAN.md section
4, R1-RL: "a 'why was it created' facet can reach the introducing commit"). ``govbridge.code.history.diff`` already
answers INTRODUCED_IN/DELETED_IN as a set difference between two COMMITS a caller already knows; the gap this
module closes is finding that commit automatically, from ONE known reference point, by walking the (``--follow``)
Git history of the symbol's own defining path(s) -- bounded by configuration (``max_commits``, never an unbounded
walk of the whole repository history).

This module is exact about the parse tables, exactly like ``govbridge.code.history``: a symbol either has a
definition (by ``(kind, qualified_name)``) at a commit's view or it does not. It reuses ``govbridge.code.symbols``'s
existing lazy, per-blob cache -- a commit visited more than once (by ``introduced_in`` and later by a caller's own
``history diff``) is never re-parsed.
"""
from __future__ import annotations

import argparse
import json
import sys
from typing import Optional

from govbridge.core import gitobj, store as corestore
from govbridge.code import store as codestore, symbols as symbolsmod

DEFAULT_MAX_COMMITS = 500


def _resolve_commit(commit: str, repo: Optional[str]) -> str:
    full = gitobj.resolve_commit(commit, repo=repo)
    if full is None:
        raise ValueError(f"commit {commit!r} does not resolve")
    return full


def _log_commits_for_path(path: str, start_commit: str, repo: Optional[str], max_commits: int) -> list:
    """Newest-first commit ids reachable from ``start_commit`` that touched ``path`` (``--follow``: a rename is
    followed, the same way ``govbridge.core.gitobj.blame_last_change`` already follows history for one path),
    bounded to the ``max_commits`` most recent -- the "bounded by configuration" the DAG node names. A plain
    ``gitobj.run_git`` call (a generic wrapper this module is allowed to call without editing ``gitobj.py``, which
    is outside this node's mutation scope)."""
    r = gitobj.run_git(
        ["log", "--follow", f"--max-count={max_commits}", "--format=%H", start_commit, "--", path],
        repo=repo, check=False,
    )
    if r.returncode != 0:
        return []
    out = r.stdout.decode("utf-8", "replace").split()
    return out


def _definition_present(conn, commit: str, repo: Optional[str], qualified_name: str) -> bool:
    entries = symbolsmod.ensure_indexed(conn, commit, repo=repo)
    blob_ids = [b for _, b in entries]
    rows = codestore.symbols_for_blobs(conn, blob_ids)
    return any(r["qualified_name"] == qualified_name for r in rows)


def introduced_in(qualified_name: str, commit: str, repo: Optional[str] = None,
                   max_commits: int = DEFAULT_MAX_COMMITS) -> dict:
    """For every path that currently defines ``qualified_name`` at ``commit``, walk that path's own history
    (newest-first, bounded to ``max_commits``) to find the commit at which the symbol FIRST appears -- the closest
    commit, walking backward, whose immediate (still-examined) predecessor does not yet have it. When the walk
    reaches its bound without finding an absence, the oldest EXAMINED commit is reported as an honest LOWER bound
    (``bounded_incomplete: true``), never claimed as the true origin -- the same "honest MISSING, not a guess"
    discipline ``govbridge.graph.derive``'s own module docstring already documents."""
    commit_full = _resolve_commit(commit, repo)
    conn = corestore.open_db()
    codestore.ensure_schema(conn)

    current = symbolsmod.definitions(qualified_name, commit_full, repo=repo)["definitions"]
    if not current:
        return {"symbol": qualified_name, "commit": commit_full, "found": False, "max_commits": max_commits,
                "results": [], "reason": "no current definition to trace back from"}

    results = []
    for d in current:
        path = d["path"]
        history = _log_commits_for_path(path, commit_full, repo, max_commits)
        if not history:
            continue
        introduced_commit = history[-1]  # default: oldest examined -- an honest lower bound if never falsified
        bounded_incomplete = len(history) >= max_commits
        last_present = history[0]
        for older in history[1:]:
            if _definition_present(conn, older, repo, qualified_name):
                last_present = older
                continue
            introduced_commit = last_present
            bounded_incomplete = False
            break
        results.append({
            "path": path, "qualified_name": qualified_name, "introduced_commit": introduced_commit,
            "bounded_incomplete": bounded_incomplete, "commits_examined": len(history),
        })

    results.sort(key=lambda r: (r["bounded_incomplete"], r["path"]))
    return {"symbol": qualified_name, "commit": commit_full, "found": bool(results), "max_commits": max_commits,
            "results": results}


def deleted_in(qualified_name: str, since_commit: str, until_ref: str = "HEAD", repo: Optional[str] = None,
                max_commits: int = DEFAULT_MAX_COMMITS) -> dict:
    """The inverse question: ``qualified_name`` is known present at ``since_commit`` (typically a caller's own
    earlier ``introduced_in``/``definitions`` result); walk FORWARD (oldest-first, ``since_commit`` EXCLUDED) along
    ``until_ref``'s own history to find the first commit at which it is gone. Unlike ``introduced_in`` (which walks
    one known path's own history backward), this walks the whole ref's ancestry-path history forward, because the
    defining path itself might be deleted, renamed away, or replaced -- the SAME kind of bounded, configuration-
    limited walk (``max_commits``), never a whole-repository history sweep."""
    since_full = _resolve_commit(since_commit, repo)
    until_full = _resolve_commit(until_ref, repo)
    conn = corestore.open_db()
    codestore.ensure_schema(conn)

    if not _definition_present(conn, since_full, repo, qualified_name):
        return {"symbol": qualified_name, "since": since_full, "until": until_full, "found": False,
                "max_commits": max_commits, "reason": "symbol not present at since_commit"}

    r = gitobj.run_git(
        ["log", "--reverse", "--ancestry-path", f"--max-count={max_commits}", "--format=%H",
         f"{since_full}..{until_full}"],
        repo=repo, check=False,
    )
    if r.returncode != 0:
        return {"symbol": qualified_name, "since": since_full, "until": until_full, "found": False,
                "max_commits": max_commits, "reason": f"git log failed: {r.stderr.decode('utf-8', 'replace')}"}
    forward = r.stdout.decode("utf-8", "replace").split()
    if not forward:
        return {"symbol": qualified_name, "since": since_full, "until": until_full, "found": False,
                "max_commits": max_commits, "reason": "still present at until_ref (or until_ref is not a descendant)"}

    for c in forward:
        if not _definition_present(conn, c, repo, qualified_name):
            return {"symbol": qualified_name, "since": since_full, "until": until_full, "found": True,
                    "deleted_commit": c, "max_commits": max_commits, "bounded_incomplete": False}
    return {"symbol": qualified_name, "since": since_full, "until": until_full, "found": False,
            "max_commits": max_commits, "bounded_incomplete": len(forward) >= max_commits,
            "reason": "still present through every examined commit"}


def main(argv=None) -> int:
    p = argparse.ArgumentParser(prog="govbridge.graph.symbol_history")
    sub = p.add_subparsers(dest="cmd", required=True)

    i = sub.add_parser("introduced-in")
    i.add_argument("name")
    i.add_argument("--commit", required=True)
    i.add_argument("--max-commits", type=int, default=DEFAULT_MAX_COMMITS)
    i.add_argument("--json", action="store_true")

    d = sub.add_parser("deleted-in")
    d.add_argument("name")
    d.add_argument("--since", required=True)
    d.add_argument("--until", default="HEAD")
    d.add_argument("--max-commits", type=int, default=DEFAULT_MAX_COMMITS)
    d.add_argument("--json", action="store_true")

    args = p.parse_args(argv)
    try:
        if args.cmd == "introduced-in":
            result = introduced_in(args.name, args.commit, max_commits=args.max_commits)
        elif args.cmd == "deleted-in":
            result = deleted_in(args.name, args.since, args.until, max_commits=args.max_commits)
        else:
            return 2
    except ValueError as e:
        print(json.dumps({"error": str(e)}))
        return 1

    print(json.dumps(result, sort_keys=True) if args.json else json.dumps(result, indent=1, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
