#!/usr/bin/env python3
"""Historical lesson/failure retrieval: a PROFILE, not a store (ARCHITECTURE.md section 6.3). "Failed approaches"
are units that already exist -- sections of review records that define findings, ledger entries, WITHDRAWN/
SUPERSEDED records, DELETED_IN symbols/records, lessons/, and rank-5 research records with RETRACTED/WITHDRAWN
sections. ``govbridge history <seed>`` returns them through MENTIONS, SYMBOL_MENTION, CITES_LINE and DELETED_IN,
ordered by commit time, and labelled. No separate lesson store and no LLM extraction.
"""
from __future__ import annotations

import argparse
import json
import sys
from typing import Optional

from govbridge.authority import lifecycle as lifecyclemod
from govbridge.authority import records as recordsmod
from govbridge.authority import registry as registrymod
from govbridge.core import gitobj, view as viewmod
from govbridge.core import taskctx as taskctxmod
from govbridge.graph import derive as D

LESSON_DIRS = ("spec/research", "spec/reports", "lessons")


def _resolved_view(view_path: Optional[str] = None, repo: Optional[str] = None) -> "viewmod.ResolvedView":
    from govbridge import GOV_BRIDGE_DOMAIN
    import os
    view_path = view_path or os.path.join(GOV_BRIDGE_DOMAIN, "config", "canonical-view.yaml")
    vc = viewmod.load_view(view_path)
    return viewmod.resolve_view(vc, repo=repo)


def history(seed: str, repo: Optional[str] = None, view_path: Optional[str] = None,
            registry_path: Optional[str] = None, deleted_from: Optional[str] = None,
            task: Optional[taskctxmod.TaskContext] = None) -> dict:
    resolved_view = _resolved_view(view_path, repo=repo)
    commit = resolved_view.ref_commit("records")
    grammar = recordsmod.load_grammar(recordsmod._default_grammar_path())
    reg = registrymod.load(registry_path or registrymod._default_registry_path(), verify_commit="records",
                            view_path=view_path, repo=repo)

    # R1-RX (OBS-BR-08): the same generic path-exclusion predicate every route/command uses.
    task = task or taskctxmod.current()
    mentions, excluded_hits = taskctxmod.filter_edges(
        D.mentions_edges_for_id(seed, commit, repo=repo, grammar=grammar), task)

    entries: list = []
    for e in mentions:
        path = e.evidence_occurrence.split("@")[0]
        rule = reg.class_for_path(path)
        cls = rule.cls if rule else None
        blame = gitobj.blame_last_change(path, e.evidence_line, e.evidence_line, commit=commit, repo=repo) \
            if e.evidence_line else None
        commit_time = None
        if blame:
            _sha, date = blame
            commit_time = date
        entries.append({
            "edge": e.to_dict(), "path_class": cls,
            "kind": "lesson" if any(path.startswith(d) for d in LESSON_DIRS) else (
                "withdrawn_or_superseded" if cls in ("EVIDENCE_WITHDRAWN",) else "mention"),
            "commit_time": commit_time,
        })

    deleted: list = []
    if deleted_from:
        raw_deleted = [e for e in D.deleted_in_edges(deleted_from, commit, repo=repo, grammar=grammar)
                       if e.src == seed or seed in e.src]
        kept_deleted, dropped = taskctxmod.filter_edges(raw_deleted, task)
        excluded_hits += dropped
        deleted = [e.to_dict() for e in kept_deleted]

    seed_classification = lifecyclemod.classify(seed, reg=reg, repo=repo, view_path=view_path)
    if seed_classification.lifecycle in ("WITHDRAWN", "SUPERSEDED"):
        entries.append({
            "edge": None, "path_class": seed_classification.cls, "kind": "withdrawn_or_superseded",
            "commit_time": None,
            "note": f"the seed's own current lifecycle is {seed_classification.lifecycle} "
                    f"({seed_classification.derivation})",
        })

    entries.sort(key=lambda x: x["commit_time"] or "")
    return {"seed": seed, "entries": entries, "deleted_in": deleted, "excluded_hits": excluded_hits}


def main(argv=None) -> int:
    p = argparse.ArgumentParser(prog="govbridge.graph.history")
    p.add_argument("seed")
    p.add_argument("--deleted-from", help="an earlier commit to diff record definitions against for DELETED_IN")
    p.add_argument("--json", action="store_true", help="present regardless (output is always JSON)")
    taskctxmod.add_cli_arg(p)
    args = p.parse_args(argv)

    ctx = taskctxmod.from_args(args)
    result = history(args.seed, deleted_from=args.deleted_from, task=ctx)
    print(json.dumps(result, indent=1, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
