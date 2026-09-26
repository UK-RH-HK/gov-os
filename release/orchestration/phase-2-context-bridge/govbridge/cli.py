#!/usr/bin/env python3
"""``python -m govbridge <command> ...`` -- node I1's integration CLI (ARCHITECTURE.md, DAG node I1 deliverable):

    index update|rebuild, coverage, freshness, exact, state, search, gather, why, impact, history, resolve, compile,
    packet verify, receipt check, renew, bootstrap, notes validate|build, demo grade|validate-oracle|extract-reads

Every subcommand is a thin dispatcher onto the module that already owns that capability (B1-B6's own CLIs, where
one exists) -- this file adds no retrieval or classification logic of its own. What it DOES add, because no other
node owns it:

* discovering and importing every ``govbridge.*`` layer package before ANY command runs (B2/B4 open issue OI-1:
  "a bare `freshness rebuild --layer X` raises KeyError" -- ``govbridge.core.freshness.
  ensure_all_layer_packages_imported`` does the actual work; this is the CLI's own half of that fix);
* ``freshness`` (bare, no subcommand): an incremental check against the committed build manifest, matching the
  DAG's own acceptance line ("NOOP, wall < 2 s, llm_invocations 0");
* ``search``: a multi-route query, fused, over the REAL routes (``govbridge.route.real_routes``);
* ``gather``: the OD-BR-05 multi-facet, multi-round retrieval loop (``govbridge.gather``, REPAIR_DAG.yaml node
  R1-GA1) -- facet decomposition, deterministic parallel retrieval, paging with a configurable batch size, and a
  recorded stopping reason, for one instantiated task-spec query;
* ``notes`` (``govbridge.notes.cli``, REPAIR_DAG.yaml node R1-RN): hierarchical evidence note build/validate --
  dispatched here, owned there;
* ``compile --out DIR`` / ``packet verify DIR`` / ``receipt check --packet DIR``: a small, stable on-disk packet
  format (``manifest.json``, ``packet.md``, ``task_spec.yaml``, ``meta.json``) so a packet compiled once can be
  independently re-verified and receipt-checked later, exactly as the I1 acceptance checks require
  ("compile ... --out /tmp/p && ... packet verify /tmp/p");
* ``demo``: the grader, the oracle validator and the transcript read-extractor (``govbridge.demo``, this node's
  own new package).
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Optional

import yaml

from govbridge.core import taskctx as taskctxmod
from govbridge.core.yamlutil import load_yaml_file


def _load_receipt(path: str):
    if path.endswith((".yaml", ".yml")):
        return load_yaml_file(path)
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def cmd_freshness(argv) -> int:
    p = argparse.ArgumentParser(prog="govbridge freshness")
    p.add_argument("--view")
    p.add_argument("--rules")
    args = p.parse_args(argv)

    from govbridge.core import freshness as freshnessmod
    result = freshnessmod.run(view_path=args.view, rules_path=args.rules, from_clean=False)
    print(json.dumps(result, indent=1, sort_keys=True))
    return 0


def cmd_search(argv) -> int:
    p = argparse.ArgumentParser(prog="govbridge search")
    p.add_argument("text")
    p.add_argument("--route", action="append", choices=("exact", "lexical", "semantic", "code"),
                    help="repeatable; default is the same generic, text-shape-based selection "
                         "govbridge.route.router.select_routes uses for a packet query")
    p.add_argument("--k", type=int, default=8)
    p.add_argument("--exclude", action="append", metavar="GLOB")
    p.add_argument("--view")
    p.add_argument("--registry")
    p.add_argument("--repo", help="the repository to read Git objects from; defaults to the repository containing "
                                   "the current working directory (govbridge.core.gitobj.repo_root's own default). "
                                   "Pass this explicitly rather than relying on cwd: repo_root() is process-cached "
                                   "(functools.lru_cache, keyed only on the argument actually passed) the first "
                                   "time it is called bare, so a caller who changes cwd afterwards would otherwise "
                                   "see a stale resolution shared with any other bare caller in the same process.")
    taskctxmod.add_cli_arg(p)
    args = p.parse_args(argv)

    from govbridge.authority import records as recordsmod
    from govbridge.route import real_routes as real_routesmod
    from govbridge.route import router as routermod

    # R1-RX (OBS-BR-08): --task/GOVBRIDGE_TASK's retrieval_exclusions are merged with any explicit --exclude,
    # applied to every route this command runs, and disclosed as excluded_hits -- never left to the caller to
    # remember on its own (real_routes.py's own routes also apply the ambient context; this merge is belt-and-
    # braces so a --exclude-only caller sees its own globs counted too).
    ctx = taskctxmod.from_args(args)
    merged_exclude = ctx.merge_exclude(args.exclude)
    counter = taskctxmod.ExclusionCounter()

    routes = real_routesmod.build_real_routes(view_path=args.view, registry_path=args.registry, repo=args.repo)
    if args.route:
        route_names = tuple(args.route)
    else:
        grammar = recordsmod.load_grammar(recordsmod._default_grammar_path())
        route_names = tuple(rn for rn in routermod.select_routes({"text": args.text}, grammar=grammar)
                             if rn != "graph")

    hits_by_route = {rn: routes.run(rn, text=args.text, k=args.k, exclude=merged_exclude, exclude_counter=counter)
                      for rn in route_names}
    fused = routermod.fuse(hits_by_route)
    result = {
        "text": args.text,
        "routes": list(route_names),
        "hits_by_route": {rn: [h.to_dict() for h in hits] for rn, hits in hits_by_route.items()},
        "fused": [
            {"unit_id": f.hit.unit_id, "unit_kind": f.hit.unit_kind, "route": f.hit.route,
             "fused_score": f.fused_score, "authority_class": f.hit.authority_class, "lifecycle": f.hit.lifecycle}
            for f in fused
        ],
        "excluded_hits": counter.count,
    }
    print(json.dumps(result, indent=1, sort_keys=True))
    return 0


def cmd_gather(argv) -> int:
    p = argparse.ArgumentParser(prog="govbridge gather")
    p.add_argument("--task", required=True, help="a task-spec YAML (schemas/task-spec.yaml): its own `queries` "
                                                   "field is the query set `--query <id>` resolves against, and "
                                                   "its `retrieval_exclusions`/`seeds`/`budget_profile`/`view` are "
                                                   "honoured the same way every other query command honours them")
    p.add_argument("--query", required=True, help="a query id from the task's own query set, or literal ad hoc "
                                                    "query text (REPAIR_PLAN.md section 2.1)")
    p.add_argument("--batch-size", type=int, default=None, help="default: config/facets.yaml's default_batch_size")
    p.add_argument("--max-rounds", type=int, default=None, help="default: config/facets.yaml's default_max_rounds")
    p.add_argument("--threads", type=int, default=None, help="default: config/facets.yaml's default_threads")
    p.add_argument("--facets", action="append", metavar="NAME",
                    help="repeatable; overrides the query's own facet selection (config/facets.yaml)")
    p.add_argument("--gather-budget-profile", default=None,
                    help="OPT IN to stopping this gather once a named config/budgets.yaml compile profile's own "
                         "total_kb is reached, instead of gather's own, separate config/budgets.yaml gather."
                         "max_bytes_per_query default; never the task spec's own budget_profile automatically "
                         "(that field bounds the FINAL COMPILED packet, not raw gathered evidence)")
    p.add_argument("--exclude", action="append", metavar="GLOB")
    p.add_argument("--view")
    p.add_argument("--registry")
    p.add_argument("--json", action="store_true", help="print the full JSON result (default: a short summary)")
    args = p.parse_args(argv)

    from govbridge import GOV_BRIDGE_DOMAIN
    from govbridge.gather import engine as enginemod
    from govbridge.gather import instantiate as instmod
    from govbridge.route import real_routes as real_routesmod

    def _abs_path(maybe_rel: str) -> str:
        # The SAME resolution govbridge.compile.packet._abs_path already uses for a task spec's own `view`/`queries`
        # paths (relative to the process cwd if that already exists, else relative to GOV_BRIDGE_DOMAIN) -- never a
        # second, diverging convention for the one command that also reads a task spec.
        if os.path.isabs(maybe_rel):
            return maybe_rel
        if os.path.exists(maybe_rel):
            return maybe_rel
        return os.path.join(GOV_BRIDGE_DOMAIN, maybe_rel)

    task_spec = load_yaml_file(args.task)
    ctx = taskctxmod.load(args.task)
    raw_queries = task_spec.get("queries")
    doc = instmod.load_query_set(_abs_path(raw_queries) if isinstance(raw_queries, str) else raw_queries)
    try:
        query = instmod.resolve_query(doc, args.query)
    except instmod.QueryNotExecutable as exc:
        print(json.dumps(exc.to_dict(), indent=1, sort_keys=True), file=sys.stderr)
        return 1

    view_path = args.view or (_abs_path(task_spec["view"]) if task_spec.get("view") else None)
    routes = real_routesmod.build_real_routes(view_path=view_path, registry_path=args.registry)

    result = enginemod.gather(
        query, routes, task=ctx, seeds=task_spec.get("seeds"), facet_names=args.facets,
        batch_size=args.batch_size, max_rounds=args.max_rounds, threads=args.threads, exclude=args.exclude,
        budget_profile=args.gather_budget_profile,
    )
    if args.json:
        print(json.dumps(result, indent=1, sort_keys=True))
    else:
        t = result["telemetry"]
        print(f"query={result['query']['id']!r} facets={result['facets']} rounds={t['rounds']} "
              f"stop_reason={result['stop_reason']} merged_items={len(result['merged'])} "
              f"excluded_hits={result['excluded_hits']} merged_sha256={result['merged_sha256']}")
    return 0


def cmd_compile(argv) -> int:
    p = argparse.ArgumentParser(prog="govbridge compile")
    p.add_argument("task_spec")
    p.add_argument("--out", help="directory to write packet.md/manifest.json/task_spec.yaml/meta.json into, so "
                                  "the packet can be independently re-verified/receipt-checked later")
    p.add_argument("--fake-routes", action="store_true",
                    help="use the all-empty RouteSet; the DEFAULT is the real B2/B3/B4 routes")
    p.add_argument("--registry")
    p.add_argument("--budgets")
    p.add_argument("--json", action="store_true", help="print the manifest instead of the rendered packet")
    args = p.parse_args(argv)

    from govbridge.compile import packet as packetmod

    task_spec = load_yaml_file(args.task_spec)
    routes = packetmod.FAKE_ROUTES if args.fake_routes else packetmod.real_routes_for(
        task_spec, registry_path=args.registry)
    result = packetmod.compile_packet(task_spec, routes=routes, registry_path=args.registry,
                                       budgets_path=args.budgets)

    if args.out:
        out_dir = Path(args.out)
        out_dir.mkdir(parents=True, exist_ok=True)
        (out_dir / "packet.md").write_text(result["rendered"], encoding="utf-8")
        (out_dir / "manifest.json").write_text(
            json.dumps(result["manifest"], indent=1, sort_keys=True), encoding="utf-8")
        (out_dir / "task_spec.yaml").write_text(yaml.safe_dump(task_spec, sort_keys=False), encoding="utf-8")
        meta = {
            "status": result["status"], "packet_id": result.get("packet_id"),
            "packet_sha256": result.get("packet_sha256"), "manifest_sha256": result.get("manifest_sha256"),
            "registry_path": result.get("registry_path"),
            # R1-RX (OBS-BR-08): disclosed here too, so a caller of `compile --out` sees it without parsing
            # manifest.json's notices.
            "excluded_hits": result.get("excluded_hits"),
        }
        (out_dir / "meta.json").write_text(json.dumps(meta, indent=1, sort_keys=True), encoding="utf-8")
        print(json.dumps({"out": str(out_dir), **meta}, indent=1, sort_keys=True))
    elif args.json:
        print(json.dumps(result["manifest"], indent=1, sort_keys=True))
    else:
        sys.stdout.write(result["rendered"])
    return 0 if result["status"] == packetmod.STATUS_OK else 1


def cmd_packet(argv) -> int:
    p = argparse.ArgumentParser(prog="govbridge packet")
    sub = p.add_subparsers(dest="cmd", required=True)
    v = sub.add_parser("verify")
    v.add_argument("path", help="a directory written by `govbridge compile --out DIR`")
    v.add_argument("--registry")
    args = p.parse_args(argv)

    if args.cmd != "verify":
        return 2

    from govbridge.compile import validate as validatemod

    d = Path(args.path)
    manifest = json.loads((d / "manifest.json").read_text(encoding="utf-8"))
    task_spec = load_yaml_file(str(d / "task_spec.yaml"))
    meta = {}
    meta_path = d / "meta.json"
    if meta_path.exists():
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
    problems = validatemod.verify_packet(manifest, task_spec, registry_path=args.registry or meta.get("registry_path"))
    result = {"status": meta.get("status", "?"), "verify": "PASS" if not problems else "FAIL", "problems": problems}
    print(json.dumps(result, indent=1, sort_keys=True))
    return 0 if not problems else 1


def cmd_receipt(argv) -> int:
    p = argparse.ArgumentParser(prog="govbridge receipt")
    sub = p.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("check")
    c.add_argument("--packet", required=True, help="a directory written by `govbridge compile --out DIR`")
    c.add_argument("--receipt", required=True)
    c.add_argument("--registry")
    args = p.parse_args(argv)

    if args.cmd != "check":
        return 2

    from govbridge.compile import receipt as receiptmod

    d = Path(args.packet)
    manifest = json.loads((d / "manifest.json").read_text(encoding="utf-8"))
    task_spec = load_yaml_file(str(d / "task_spec.yaml"))
    meta = {}
    meta_path = d / "meta.json"
    if meta_path.exists():
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
    receipt = _load_receipt(args.receipt)
    result = receiptmod.check(manifest, receipt, task_spec, registry_path=args.registry or meta.get("registry_path"))
    print(json.dumps(result, indent=1, sort_keys=True))
    return 0 if result["status"] == "PASS" else 1


_DISPATCH = {
    # command -> (module path, submodule main() gets the REST of argv verbatim)
    "index": "govbridge.core.freshness",
    "exact": "govbridge.core.exact",
    "state": "govbridge.authority.state",
    "why": "govbridge.graph.why",
    "impact": "govbridge.graph.impact",
    "history": "govbridge.graph.history",
    "resolve": "govbridge.authority.resolver",
    "renew": "govbridge.compile.renewal",
    "bootstrap": "govbridge.compile.bootstrap",
}


def main(argv: Optional[list] = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)

    # B2/B4 OI-1 ("the CLI, and core freshness, discover and import every layer package deterministically"):
    # every govbridge command that touches the store needs every layer package's own register_layer_builder/
    # register_layer call to have run first. freshness.run() does this itself too (belt and braces -- a caller
    # of the library function directly, not through this CLI, still gets it); doing it here as well means even a
    # command that never calls freshness.run() (search, why, impact, ...) still sees every layer registered.
    from govbridge.core import freshness as freshnessmod
    freshnessmod.ensure_all_layer_packages_imported()

    if not argv:
        print(__doc__)
        return 2

    cmd, rest = argv[0], argv[1:]

    if cmd == "coverage":
        from govbridge.core import corpus as corpusmod
        return corpusmod.main(["coverage", *rest])
    if cmd == "freshness":
        return cmd_freshness(rest)
    if cmd == "search":
        return cmd_search(rest)
    if cmd == "gather":
        return cmd_gather(rest)
    if cmd == "notes":
        # REPAIR_DAG.yaml node R1-RN (BR-AR-0017); the dispatch line R1-GA1 (BR-AR-0023) adds, exactly as
        # govbridge/notes/cli.py's own module docstring names it -- govbridge.notes.cli.main is unchanged by it.
        from govbridge.notes import cli as notescli
        return notescli.main(rest)
    if cmd == "compile":
        return cmd_compile(rest)
    if cmd == "packet":
        return cmd_packet(rest)
    if cmd == "receipt":
        return cmd_receipt(rest)
    if cmd == "demo":
        from govbridge.demo import cli as democli
        return democli.main(rest)

    mod_path = _DISPATCH.get(cmd)
    if mod_path is None:
        print(f"govbridge: unknown command {cmd!r}. {__doc__}", file=sys.stderr)
        return 2
    import importlib
    mod = importlib.import_module(mod_path)
    return mod.main(rest)


if __name__ == "__main__":
    sys.exit(main())
