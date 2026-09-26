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
* ``why``/``impact``/``history``/``exact``/``state``: every one of these query commands (like ``search``/
  ``gather`` already did) additionally accepts ``--out DIR`` (REPAIR_DAG.yaml node R1-RS) to write a budgeted,
  deduplicated SUPPLEMENTARY packet in that same on-disk shape, instead of dumping raw JSON by default;
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


# ---------------------------------------------------------------------------------------------------------------
# REPAIR_DAG.yaml node R1-RS: supplementary packets for every query command (search/why/impact/history/exact/
# state/gather). One shared --out/--raw/--dedup-against surface, used by every cmd_* below, so the flags and
# their meaning never drift between commands.
# ---------------------------------------------------------------------------------------------------------------

def _add_supplementary_args(p) -> None:
    p.add_argument("--out", help="write a supplementary packet directory here (manifest.json/packet.md/"
                                  "task_spec.yaml/meta.json -- the same shape `govbridge compile --out` writes, "
                                  "so `packet verify`/`receipt check` need no special case for it). Without "
                                  "--out, this command's output is unchanged (REPAIR_PLAN.md section 2.9)")
    p.add_argument("--raw", action="store_true",
                    help="with --out, ALSO print the full raw JSON result (default: a short packet summary "
                          "only -- REPAIR_PLAN.md section 2.9: \"raw JSON is available only behind --raw\")")
    p.add_argument("--dedup-against", action="append", metavar="DIR",
                    help="repeatable: an earlier packet directory (the main packet, or an earlier supplementary "
                         "packet from this same run) whose item ids this one must not duplicate -- a duplicate is "
                         "still listed, but delivered by reference only, never a second full copy")


def _packet_item_ids(packet_dir: str) -> set:
    """Every ``"{unit_kind}:{unit_id}"`` already present in a packet directory's own ``manifest.json`` -- used to
    build ``dedup_ids`` for a LATER supplementary packet (``--dedup-against``)."""
    manifest_path = Path(packet_dir) / "manifest.json"
    if not manifest_path.exists():
        return set()
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    ids = set()
    for letter, sec in (manifest.get("sections") or {}).items():
        rows = sec.get("items") or []
        if letter == "D":
            rows = [r for sub in (sec.get("subblocks") or {}).values() for r in (sub.get("items") or [])]
        for row in rows:
            unit = row.get("unit") or {}
            ids.add(f"{unit.get('kind')}:{unit.get('id')}")
    return ids


def _load_task_spec_for_supplementary(args) -> dict:
    """The real task spec when ``--task`` was given (every query command already accepts it --
    ``taskctxmod.add_cli_arg``); otherwise a minimal, honest placeholder -- a supplementary packet always needs
    SOME ``task_spec.yaml`` companion file (``packet verify``/``receipt check`` read one unconditionally), and a
    query command run without ``--task`` genuinely has no task spec of its own to report."""
    task_path = getattr(args, "task", None)
    if task_path:
        return load_yaml_file(task_path)
    return {"schema": "govbridge-task-spec/1", "task_id": "adhoc", "view": getattr(args, "view", None)}


def _handle_query_output(command: str, result: dict, args, subcmd: Optional[str] = None) -> None:
    """Common ``--out``/``--raw``/``--dedup-against`` handling for every query command. Without ``--out``, prints
    ``result`` exactly as every command already did (no behaviour change). With ``--out``, builds and writes a
    supplementary packet (``govbridge.compile.supplementary``) and prints its short summary; the full raw JSON is
    printed too only when ``--raw`` is also given."""
    out_dir = getattr(args, "out", None)
    if not out_dir:
        print(json.dumps(result, indent=1, sort_keys=True, default=str))
        return

    from govbridge.compile import supplementary as suppmod

    task_spec = _load_task_spec_for_supplementary(args)
    dedup_ids: set = set()
    for d in (getattr(args, "dedup_against", None) or []):
        dedup_ids |= _packet_item_ids(d)
    built = suppmod.build_supplementary_packet(command, result, task_spec, subcmd=subcmd, dedup_ids=dedup_ids)
    meta = suppmod.write_supplementary_packet(out_dir, built, task_spec)
    print(json.dumps({"out": out_dir, **meta}, indent=1, sort_keys=True))
    if getattr(args, "raw", False):
        print(json.dumps(result, indent=1, sort_keys=True, default=str))


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
    _add_supplementary_args(p)
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
    _handle_query_output("search", result, args)
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
    _add_supplementary_args(p)
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
    if args.out:
        _handle_query_output("gather", result, args)
    elif args.json:
        print(json.dumps(result, indent=1, sort_keys=True))
    else:
        t = result["telemetry"]
        print(f"query={result['query']['id']!r} facets={result['facets']} rounds={t['rounds']} "
              f"stop_reason={result['stop_reason']} merged_items={len(result['merged'])} "
              f"excluded_hits={result['excluded_hits']} merged_sha256={result['merged_sha256']}")
    return 0


def cmd_why(argv) -> int:
    """Was a bare ``_DISPATCH`` forward onto ``govbridge.graph.why.main`` before this node -- now calls
    ``why.why(...)`` directly (mirroring ``cmd_search``/``cmd_gather``'s own existing pattern) so ``--out`` can
    packetise the result. Every pre-existing flag/behaviour (no ``--out``) is unchanged."""
    p = argparse.ArgumentParser(prog="govbridge why")
    p.add_argument("seed")
    p.add_argument("--json", action="store_true", help="present regardless (output is always JSON)")
    taskctxmod.add_cli_arg(p)
    _add_supplementary_args(p)
    args = p.parse_args(argv)

    from govbridge.graph import why as whymod
    ctx = taskctxmod.from_args(args)
    result = whymod.why(args.seed, task=ctx)
    _handle_query_output("why", result, args)
    return 0


def cmd_impact(argv) -> int:
    p = argparse.ArgumentParser(prog="govbridge impact")
    p.add_argument("seed")
    p.add_argument("--depth", type=int, default=2)
    p.add_argument("--view")
    p.add_argument("--json", action="store_true", help="present regardless (output is always JSON)")
    taskctxmod.add_cli_arg(p)
    _add_supplementary_args(p)
    args = p.parse_args(argv)

    from govbridge.graph import impact as impactmod
    ctx = taskctxmod.from_args(args)
    result = impactmod.impact(args.seed, view_path=args.view, max_depth=args.depth, task=ctx)
    _handle_query_output("impact", result, args)
    return 0


def cmd_history(argv) -> int:
    p = argparse.ArgumentParser(prog="govbridge history")
    p.add_argument("seed")
    p.add_argument("--deleted-from", help="an earlier commit to diff record definitions against for DELETED_IN")
    p.add_argument("--json", action="store_true", help="present regardless (output is always JSON)")
    taskctxmod.add_cli_arg(p)
    _add_supplementary_args(p)
    args = p.parse_args(argv)

    from govbridge.graph import history as historymod
    ctx = taskctxmod.from_args(args)
    result = historymod.history(args.seed, deleted_from=args.deleted_from, task=ctx)
    _handle_query_output("history", result, args)
    return 0


def cmd_exact(argv) -> int:
    p = argparse.ArgumentParser(prog="govbridge exact")
    sub = p.add_subparsers(dest="cmd", required=True)

    sp_show = sub.add_parser("show")
    sp_show.add_argument("spec")
    sp_show.add_argument("--view")
    sp_show.add_argument("--rules")
    taskctxmod.add_cli_arg(sp_show)
    _add_supplementary_args(sp_show)

    sp_grep = sub.add_parser("grep")
    sp_grep.add_argument("-F", dest="literal", required=True)
    sp_grep.add_argument("--ref")
    sp_grep.add_argument("--paths", nargs="*")
    sp_grep.add_argument("--view")
    sp_grep.add_argument("--rules")
    taskctxmod.add_cli_arg(sp_grep)
    _add_supplementary_args(sp_grep)

    sp_id = sub.add_parser("id")
    sp_id.add_argument("token")
    sp_id.add_argument("--ref")
    sp_id.add_argument("--view")
    taskctxmod.add_cli_arg(sp_id)
    _add_supplementary_args(sp_id)

    sp_path = sub.add_parser("path")
    sp_path.add_argument("suffix")
    sp_path.add_argument("--ref")
    sp_path.add_argument("--view")
    _add_supplementary_args(sp_path)  # note: `path` never took --task upstream either (path_resolve has no task=)

    args = p.parse_args(argv)
    ctx = taskctxmod.from_args(args)
    from govbridge.core import exact as exactmod
    if args.cmd == "show":
        result = exactmod.show(args.spec, view_path=args.view, rules_path=args.rules, task=ctx)
    elif args.cmd == "grep":
        result = exactmod.grep(args.literal, ref=args.ref, paths=args.paths, view_path=args.view,
                                rules_path=args.rules, task=ctx)
    elif args.cmd == "id":
        result = exactmod.id_lookup(args.token, ref=args.ref, view_path=args.view, task=ctx)
    elif args.cmd == "path":
        result = exactmod.path_resolve(args.suffix, ref=args.ref, view_path=args.view)
    else:
        return 2
    _handle_query_output("exact", result, args, subcmd=args.cmd)
    return 0 if "error" not in result else 1


def cmd_state(argv) -> int:
    p = argparse.ArgumentParser(prog="govbridge state")
    sub = p.add_subparsers(dest="cmd", required=True)
    g = sub.add_parser("get")
    g.add_argument("alias")
    g.add_argument("key_path")
    g.add_argument("--view")
    g.add_argument("--repo", help="the repository to read Git objects from; defaults to the repository containing "
                                   "the current working directory (see cmd_search's own --repo).")
    g.add_argument("--json", action="store_true", help="present regardless (output is always JSON)")
    taskctxmod.add_cli_arg(g)
    _add_supplementary_args(g)
    args = p.parse_args(argv)

    ctx = taskctxmod.from_args(args)
    from govbridge.authority import state as statemod
    if args.cmd == "get":
        try:
            result = statemod.get(args.alias, args.key_path, repo=args.repo, view_path=args.view, task=ctx)
        except (KeyError, ValueError, FileNotFoundError) as e:
            print(json.dumps({"error": str(e)}, indent=1))
            return 1
        _handle_query_output("state", result.to_dict(), args)
        return 0
    return 2


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
    from govbridge.compile import section_i as section_i_mod

    task_spec = load_yaml_file(args.task_spec)
    routes = packetmod.FAKE_ROUTES if args.fake_routes else packetmod.real_routes_for(
        task_spec, registry_path=args.registry)
    result = packetmod.compile_packet(task_spec, routes=routes, registry_path=args.registry,
                                       budgets_path=args.budgets)
    # OBS-BR-07 (RC-9, node R1-RS): section I additionally carries the task's instantiated query set and the
    # answers/receipt schemas, verbatim and by hash -- re-finalises manifest_sha256/packet_sha256 around the
    # exact same sections/queries_log/drops compile_packet already computed (govbridge.compile.packet, this
    # function's own caller of it, is untouched).
    result = section_i_mod.with_task_inputs_in_section_i(result, task_spec)

    if args.out:
        out_dir = Path(args.out)
        out_dir.mkdir(parents=True, exist_ok=True)
        (out_dir / "packet.md").write_text(result["rendered"], encoding="utf-8")
        (out_dir / "manifest.json").write_text(
            json.dumps(result["manifest"], indent=1, sort_keys=True), encoding="utf-8")
        (out_dir / "task_spec.yaml").write_text(yaml.safe_dump(task_spec, sort_keys=False), encoding="utf-8")
        meta = {
            "packet_kind": "main", "status": result["status"], "packet_id": result.get("packet_id"),
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
    v.add_argument("--repo", help="the repository to read Git objects from; defaults to the repository containing "
                                   "the current working directory (see cmd_search's own --repo for why this is "
                                   "worth passing explicitly -- a fixture-repo caller MUST pass it, since cwd-based "
                                   "resolution would otherwise look for its commits in the wrong repository).")
    args = p.parse_args(argv)

    if args.cmd != "verify":
        return 2

    from govbridge.compile import validate as validatemod

    d = Path(args.path)
    manifest = json.loads((d / "manifest.json").read_text(encoding="utf-8"))
    meta = {}
    meta_path = d / "meta.json"
    if meta_path.exists():
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
    # BR-DAG-AMEND-R1-10: read the RENDERED packet too (never just the manifest), so `packet verify` can
    # re-extract each A item's delivered body from the actual bytes and independently recompute its hash.
    packet_md_path = d / "packet.md"
    rendered = packet_md_path.read_text(encoding="utf-8") if packet_md_path.exists() else None

    # node R1-RS: a supplementary packet (meta.json's own `packet_kind`, absent == "main" for back-compat with
    # every packet `compile --out` wrote before this node) has no section A of its own to re-derive a resolver
    # against -- verify_supplementary_packet checks placement/banners/ordering and refuses any MANDATORY/PINNED
    # item instead.
    if meta.get("packet_kind") == "supplementary":
        problems = validatemod.verify_supplementary_packet(manifest)
    else:
        task_spec = load_yaml_file(str(d / "task_spec.yaml"))
        problems = validatemod.verify_packet(manifest, task_spec, repo=args.repo,
                                              registry_path=args.registry or meta.get("registry_path"),
                                              rendered=rendered)
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
    c.add_argument("--repo", help="the repository to read Git objects from; defaults to the repository containing "
                                   "the current working directory (see cmd_packet verify's own --repo).")
    c.add_argument("--supplementary", action="append", metavar="DIR",
                    help="repeatable: a supplementary packet directory this run also wrote (REPAIR_PLAN.md "
                         "section 2.9: \"receipt check covers... every supplementary packet\") -- its own "
                         "packet_sha256/manifest_sha256 must also be acknowledged in the receipt, or this fails")
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
    # BR-DAG-AMEND-R1-10: the same rendered-body re-extraction `packet verify` now runs.
    packet_md_path = d / "packet.md"
    rendered = packet_md_path.read_text(encoding="utf-8") if packet_md_path.exists() else None

    supplementary = []
    for supp_dir in (args.supplementary or []):
        sd = Path(supp_dir)
        supp_manifest = json.loads((sd / "manifest.json").read_text(encoding="utf-8"))
        supplementary.append({"label": supp_dir, "manifest": supp_manifest})

    receipt = _load_receipt(args.receipt)
    result = receiptmod.check(manifest, receipt, task_spec, repo=args.repo,
                               registry_path=args.registry or meta.get("registry_path"),
                               rendered=rendered, supplementary=supplementary)
    print(json.dumps(result, indent=1, sort_keys=True))
    return 0 if result["status"] == "PASS" else 1


_DISPATCH = {
    # command -> (module path, submodule main() gets the REST of argv verbatim). why/impact/history/exact/state
    # moved OUT of this table at node R1-RS -- each now has its own cmd_* function above (calling the library
    # function directly, like cmd_search/cmd_gather already did) so `--out` can packetise the result; every other
    # flag and behaviour is unchanged.
    "index": "govbridge.core.freshness",
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
    if cmd == "why":
        return cmd_why(rest)
    if cmd == "impact":
        return cmd_impact(rest)
    if cmd == "history":
        return cmd_history(rest)
    if cmd == "exact":
        return cmd_exact(rest)
    if cmd == "state":
        return cmd_state(rest)
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
