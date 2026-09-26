#!/usr/bin/env python3
"""The system-purpose chain (ARCHITECTURE.md section 6.2): ``govbridge why <seed>``, a deterministic traversal in
the owner's order:

    product purpose -> requirement -> owner decision -> architecture -> dependency -> implementation -> tests
    -> findings -> lessons -> current status

Every hop is printed with its edge label and citation; a missing link is printed as ``MISSING: <stage>`` and is
never filled by retrieval (W8). This module names no particular seed, review or phase (OC-BR-02): the stage
functions are generic operations over whatever the registry's class_rules and the id-grammar's mentions surface for
the GIVEN seed -- the acceptance subject is D-0006 precisely because it is unrelated to Review 8.
"""
from __future__ import annotations

import argparse
import json
import sys
from typing import Optional

from govbridge.authority import lifecycle as lifecyclemod
from govbridge.authority import records as recordsmod
from govbridge.authority import registry as registrymod
from govbridge.core import taskctx as taskctxmod
from govbridge.core import view as viewmod
from govbridge.graph import derive as D
from govbridge.graph import edges as E

STAGES = ("purpose", "requirement", "owner_decision", "architecture", "dependency", "implementation", "tests",
          "findings", "lessons", "current_status")

GOVERNING_DOCS = (
    "spec/product",
)
CONTRACT_PATHS = (
    "Governance_OS_Capability_Acceptance_Contract_v3.md",
    "framework/contracts",
)
LESSON_DIRS = ("spec/research", "spec/reports", "lessons")
EVIDENCE_DIRS = ("probes", "telemetry")


def _resolved_view(view_path: Optional[str] = None, repo: Optional[str] = None) -> "viewmod.ResolvedView":
    from govbridge import GOV_BRIDGE_DOMAIN
    import os
    view_path = view_path or os.path.join(GOV_BRIDGE_DOMAIN, "config", "canonical-view.yaml")
    vc = viewmod.load_view(view_path)
    return viewmod.resolve_view(vc, repo=repo)


def _mentions_from_dirs(seed: str, commit: str, dirs: tuple, repo: Optional[str],
                         grammar: recordsmod.Grammar) -> list:
    edges = D.mentions_edges_for_id(seed, commit, repo=repo, grammar=grammar)
    return [e for e in edges if any(e.evidence_occurrence.split("@")[0].startswith(d) for d in dirs)]


def _class_of_path(path: str, reg: registrymod.Registry) -> Optional[str]:
    rule = reg.class_for_path(path)
    return rule.cls if rule else None


def why(seed: str, repo: Optional[str] = None, view_path: Optional[str] = None,
        registry_path: Optional[str] = None, code_conn=None,
        task: Optional[taskctxmod.TaskContext] = None) -> dict:
    resolved_view = _resolved_view(view_path, repo=repo)
    commit = resolved_view.ref_commit("records")
    grammar = recordsmod.load_grammar(recordsmod._default_grammar_path())
    reg = registrymod.load(registry_path or registrymod._default_registry_path(), verify_commit="records",
                            view_path=view_path, repo=repo)
    mandatory_items = lifecyclemod._load_mandatory_items(repo=repo, view_path=view_path)

    seed_classification = lifecyclemod.classify(seed, reg=reg, mandatory_items=mandatory_items, repo=repo,
                                                  view_path=view_path)
    all_mentions = D.mentions_edges_for_id(seed, commit, repo=repo, grammar=grammar,
                                            exclude_paths=(seed_classification.path,) if seed_classification.path else ())
    defines = D.defines_edges_for_id(seed, commit, repo=repo, grammar=grammar)

    chain: dict = {}

    # 1. purpose: the governing documents' purpose sections / product records that mention the seed.
    chain["purpose"] = _mentions_from_dirs(seed, commit, GOVERNING_DOCS, repo, grammar)

    # 2. requirement: Contract v3 (canonical import + compiled) mentioning the seed.
    chain["requirement"] = [e for e in all_mentions
                             if any(e.evidence_occurrence.split("@")[0].startswith(p) for p in CONTRACT_PATHS)]

    # 3/4. owner decision / architecture: the seed's own definition, if it IS one of these classes; otherwise every
    # ACTIVE mention from a file the registry classifies that way.
    owner_hops, arch_hops = [], []
    if seed_classification.cls == "OWNER_DECISION":
        owner_hops = list(defines)
    if seed_classification.cls == "ARCHITECTURE_DECISION":
        arch_hops = list(defines)
    for e in all_mentions:
        path = e.evidence_occurrence.split("@")[0]
        cls = _class_of_path(path, reg)
        if cls == "OWNER_DECISION":
            owner_hops.append(e)
        elif cls == "ARCHITECTURE_DECISION":
            arch_hops.append(e)
    chain["owner_decision"] = owner_hops
    chain["architecture"] = arch_hops

    # 5. dependency: CALLS in both directions at the canonical product ref (B3's tables; MISSING until I1 wires them).
    chain["dependency"] = D.callers_of(code_conn, seed) + D.callees_of(code_conn, seed)

    # 6. implementation: CODE_CITES -- an id token inside a code file's doc/body comment.
    chain["implementation"] = D.code_cites_edges_for_id(seed, commit, repo=repo)

    # 7. tests: TESTS (B3, MISSING until I1) + EVIDENCE_MAP.
    chain["tests"] = D.tests_of(code_conn, seed) + D.evidence_map_edges_for_id(seed, commit, repo=repo)

    # 8. findings: mentions from evidence-classed paths (probes/, telemetry/, review/finding material).
    chain["findings"] = _mentions_from_dirs(seed, commit, EVIDENCE_DIRS, repo, grammar)

    # 9. lessons: mentions from research/report/lesson material, with a RELATION_CUE reading where a cue word
    # appears on the same line as the mention.
    lesson_hops = _mentions_from_dirs(seed, commit, LESSON_DIRS, repo, grammar)
    sentence_by_line = {}
    for e in lesson_hops:
        path = e.evidence_occurrence.split("@")[0]
        raw = None
        try:
            from govbridge.core import gitobj
            raw = gitobj.read_path(commit, path, repo=repo)
        except Exception:
            raw = None
        if raw is not None:
            lines = raw.decode("utf-8", "replace").splitlines()
            if e.evidence_line and 1 <= e.evidence_line <= len(lines):
                sentence_by_line[e.evidence_line] = lines[e.evidence_line - 1]
    chain["lessons"] = lesson_hops + D.relation_cue_edges(lesson_hops, sentence_by_line)

    # 10. current status: structured lifecycle of the seed itself (and, if any findings/lessons hop landed on a
    # record id, its lifecycle too).
    status_hop = E.Edge(src=seed, type="CURRENT_STATUS", dst=seed_classification.lifecycle,
                         derivation=seed_classification.derivation,
                         evidence_occurrence=f"{seed_classification.path}@{seed_classification.commit}"
                         if seed_classification.path else None,
                         note=f"class={seed_classification.cls}")
    chain["current_status"] = [status_hop]

    # R1-RX (OBS-BR-08): the task context (explicit, or the ambient one -- GOVBRIDGE_TASK/--task) applies here too:
    # a hop whose evidence occurrence falls under an excluded path is dropped, generically, the same way it would
    # be dropped from a route's own hits -- never a special case per stage.
    task = task or taskctxmod.current()
    excluded_hits = 0
    for stage in list(chain.keys()):
        kept, dropped = taskctxmod.filter_edges(chain[stage], task)
        chain[stage] = kept
        excluded_hits += dropped

    result = {"seed": seed, "stages": {}, "excluded_hits": excluded_hits}
    for stage in STAGES:
        hops = chain.get(stage, [])
        if hops:
            result["stages"][stage] = {"status": "PRESENT", "hops": [h.to_dict() for h in hops]}
        else:
            result["stages"][stage] = {"status": f"MISSING: {stage}", "hops": []}
    return result


def main(argv=None) -> int:
    p = argparse.ArgumentParser(prog="govbridge.graph.why")
    p.add_argument("seed")
    p.add_argument("--json", action="store_true", help="present regardless (output is always JSON)")
    taskctxmod.add_cli_arg(p)
    args = p.parse_args(argv)

    ctx = taskctxmod.from_args(args)
    result = why(args.seed, task=ctx)
    print(json.dumps(result, indent=1, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
