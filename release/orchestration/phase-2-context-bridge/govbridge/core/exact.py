#!/usr/bin/env python3
"""The exact route (ARCHITECTURE.md section 4.2): a thin, deterministic wrapper over Git, authoritative about Git
content. ``show``/``grep``/``path`` are fully generic Git wrappers. ``id`` is a bounded placeholder: true
definition-site resolution needs the id-grammar (``config/id-grammar.yaml``, node B5, not yet built); until then
``id`` reports every literal mention it can find via Git and says so, rather than guessing at a definition.

Every subcommand honours the corpus rules (``config/corpus-rules.yaml``): for a path whose corpus_effect is
EXCLUDE, only metadata and the rule id are returned, never the content.

BR-DAG-AMEND-R1-23 (ONE RESOLVED VIEW PER OPERATION): every function below took a bare ``view_path`` and called
``viewmod.load_view``/``resolve_view`` internally, on EVERY call -- fine for a single, standalone ``govbridge
exact ...`` CLI invocation (that IS the whole operation), but wrong when a caller that is itself already inside
a longer-running operation (a gather round, a search) invokes one of these repeatedly: the ``records`` role's
``follow: tip`` ref could resolve to a different commit on each call, mid-operation (confirmed empirically:
AGENT_RUNS/BR-AR-0024.check-ca-why-wall-time-defaults.out, four different "records" commits inside one ~1031s
gather). Every function now also accepts an optional ``resolved_view`` (a ``govbridge.core.view.ResolvedView``
the CALLER already resolved once); when given, it is used directly and no fresh ``load_view``/``resolve_view``
call happens. ``resolved_view=None`` (the default) preserves the exact pre-existing behaviour for a genuinely
standalone call -- this module's own ``main()``/CLI dispatch never passes one, by design.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from typing import Optional

from govbridge.core import corpus, gitobj, view as viewmod
from govbridge.core import taskctx as taskctxmod
from govbridge.core.yamlutil import sha256_text

REF_PATH_RE = re.compile(r"^(?P<ref>[^:]+):(?P<path>.+?)(?::(?P<l1>\d+)(?:-(?P<l2>\d+))?)?$")


def parse_ref_path_spec(spec: str) -> tuple[str, str, Optional[int], Optional[int]]:
    """Parse "<ref>:<path>[:L1-L2]" -- greedy on the ref (first colon), then an optional trailing line range."""
    if ":" not in spec:
        raise ValueError(f"expected <ref>:<path>[:L1-L2], got {spec!r}")
    ref, rest = spec.split(":", 1)
    m = re.search(r":(\d+)(?:-(\d+))?$", rest)
    if m:
        path = rest[: m.start()]
        l1 = int(m.group(1))
        l2 = int(m.group(2)) if m.group(2) else l1
        return ref, path, l1, l2
    return ref, rest, None, None


def _default_paths(repo: Optional[str] = None) -> tuple[str, str]:
    from govbridge import GOV_BRIDGE_DOMAIN
    import os
    view_path = os.path.join(GOV_BRIDGE_DOMAIN, "config", "canonical-view.yaml")
    rules_path = os.path.join(GOV_BRIDGE_DOMAIN, "config", "corpus-rules.yaml")
    return view_path, rules_path


def _classify_path(commit: str, path: str, rules_path: str, repo: Optional[str]) -> corpus.Verdict:
    entry = gitobj.ls_tree_path(commit, path, repo=repo)
    if entry is None:
        raise FileNotFoundError(f"{commit}:{path} does not exist")
    rules = corpus.load_rules(rules_path)
    with gitobj.CatFileBatch(repo=repo) as cat:
        sniffer = corpus.ContentSniffer(cat)
        return corpus.classify_entry(entry, rules, sniffer)


def show(spec: str, view_path: Optional[str] = None, rules_path: Optional[str] = None,
          repo: Optional[str] = None, task: Optional[taskctxmod.TaskContext] = None,
          resolved_view: Optional["viewmod.ResolvedView"] = None) -> dict:
    task = task or taskctxmod.current()
    default_view, default_rules = _default_paths(repo)
    view_path = view_path or default_view
    rules_path = rules_path or default_rules

    ref, path, l1, l2 = parse_ref_path_spec(spec)
    commit = gitobj.resolve_commit(ref, repo=repo)
    if commit is None:
        return {"error": "REF_NOT_FOUND", "ref": ref}
    entry = gitobj.ls_tree_path(commit, path, repo=repo)
    if entry is None:
        return {"error": "PATH_NOT_FOUND", "ref": ref, "commit": commit, "path": path}

    # R1-RX (OBS-BR-08): the task's own retrieval_exclusions, generically -- checked separately from (and
    # disclosed separately from) corpus-rules.yaml's own, pre-existing EXCLUDE effect below; either one withholds
    # content the same way.
    task_excluded = task.is_excluded(path)

    rules = corpus.load_rules(rules_path)
    with gitobj.CatFileBatch(repo=repo) as cat:
        sniffer = corpus.ContentSniffer(cat)
        verdict = corpus.classify_entry(entry, rules, sniffer)

        result = {
            "ref": ref, "commit": commit, "path": path, "blob": entry.oid, "size": entry.size,
            "corpus_rule": verdict.rule_id, "corpus_effect": verdict.effect,
            "excluded_hits": 1 if task_excluded else 0,
        }

        if resolved_view is not None:
            resolved = resolved_view
        else:
            resolved = viewmod.resolve_view(viewmod.load_view(view_path), repo=repo)
        classification = resolved.classify_occurrence(path, commit, queried_blob=entry.oid)
        result["version_status"] = classification.status
        result["canonical_ref"] = classification.canonical_ref
        result["canonical_commit"] = classification.canonical_commit

        if verdict.effect == "EXCLUDE" or task_excluded:
            result["excluded"] = True
            return result

        is_binary, text = sniffer.get(entry.oid)
        if is_binary:
            result["excluded"] = False
            result["binary"] = True
            return result
        lines = text.splitlines(keepends=True)
        if l1 is not None:
            l2 = l2 or l1
            selected = "".join(lines[l1 - 1:l2])
            result["line_start"] = l1
            result["line_end"] = l2
        else:
            selected = text
        result["excluded"] = False
        result["text"] = selected
        result["text_sha256"] = sha256_text(selected)
        return result


def grep(literal: str, ref: Optional[str] = None, paths: Optional[list[str]] = None,
          view_path: Optional[str] = None, rules_path: Optional[str] = None, repo: Optional[str] = None,
          task: Optional[taskctxmod.TaskContext] = None,
          resolved_view: Optional["viewmod.ResolvedView"] = None) -> dict:
    task = task or taskctxmod.current()
    default_view, default_rules = _default_paths(repo)
    view_path = view_path or default_view
    rules_path = rules_path or default_rules
    if ref is None:
        # BR-DAG-AMEND-R1-23: the view is only ever needed here, to find the primary ref's OWN pinned commit --
        # resolved ONCE per call to this branch, reusing the caller's own resolved_view when given (never a
        # fresh, independent resolution mid-operation) rather than unconditionally resolving it even when an
        # explicit `ref` makes it unnecessary (the `ref is not None` branch below never reads it at all).
        if resolved_view is not None:
            resolved = resolved_view
        else:
            resolved = viewmod.resolve_view(viewmod.load_view(view_path), repo=repo)
        primary = next(r for r in resolved.config.refs if r.role == "primary")
        commit = resolved.named[primary.name].commit
        ref = primary.name
    else:
        commit = gitobj.resolve_commit(ref, repo=repo) or ref

    hits = gitobj.git_grep(literal, commit, paths=paths, repo=repo)
    rules = corpus.load_rules(rules_path)
    out = []
    skipped = 0
    task_excluded = 0
    verdict_cache: dict[str, str] = {}
    with gitobj.CatFileBatch(repo=repo) as cat:
        sniffer = corpus.ContentSniffer(cat)
        for path, lineno, text in hits:
            # R1-RX (OBS-BR-08): the task's own retrieval_exclusions, checked (and counted) separately from
            # corpus-rules.yaml's pre-existing EXCLUDE effect below -- excluded_skipped keeps its original meaning.
            if task.is_excluded(path):
                task_excluded += 1
                continue
            if path not in verdict_cache:
                entry = gitobj.ls_tree_path(commit, path, repo=repo)
                v = corpus.classify_entry(entry, rules, sniffer) if entry else None
                verdict_cache[path] = v.effect if v else "EXCLUDE"
            if verdict_cache[path] == "EXCLUDE":
                skipped += 1
                continue
            out.append({"path": path, "line": lineno, "text": text})
    return {"ref": ref, "commit": commit, "query": literal, "hits": out, "excluded_skipped": skipped,
            "excluded_hits": task_excluded}


def path_resolve(suffix: str, ref: Optional[str] = None, view_path: Optional[str] = None,
                   repo: Optional[str] = None, resolved_view: Optional["viewmod.ResolvedView"] = None) -> dict:
    if resolved_view is not None:
        resolved = resolved_view
    else:
        default_view, _ = _default_paths(repo)
        view_path = view_path or default_view
        resolved = viewmod.resolve_view(viewmod.load_view(view_path), repo=repo)
    if ref is None:
        primary = next(r for r in resolved.config.refs if r.role == "primary")
        commit = resolved.named[primary.name].commit
        ref = primary.name
    else:
        commit = resolved.named[ref].commit if ref in resolved.named else (
            gitobj.resolve_commit(ref, repo=repo) or ref)

    all_paths = gitobj.ls_tree_paths(commit, repo=repo)
    matches = [p for p in all_paths if p == suffix or p.endswith("/" + suffix)]
    if len(matches) == 1:
        return {"ref": ref, "commit": commit, "suffix": suffix, "resolved": matches[0], "ambiguous": False}
    return {"ref": ref, "commit": commit, "suffix": suffix, "candidates": matches, "ambiguous": len(matches) != 1}


def id_lookup(token: str, ref: Optional[str] = None, view_path: Optional[str] = None,
               repo: Optional[str] = None, task: Optional[taskctxmod.TaskContext] = None,
               resolved_view: Optional["viewmod.ResolvedView"] = None) -> dict:
    """Every literal mention of ``token`` (found generically via Git), plus its definition site if one resolves
    through the id grammar (B1 OI-2, closed by I1/BR-AR-0009: node B5's ``config/id-grammar.yaml`` interpreter,
    reused here via ``govbridge.authority.lifecycle.find_definition`` -- a bounded, git-grep-based lookup, never a
    whole-corpus scan). ``definition_sites`` is empty, with an explanatory note, when the token is not an
    id-grammar-shaped record id (e.g. a bare code symbol) or the lookup is unavailable in this environment: a
    mention is never mistaken for a definition either way.

    ``resolved_view`` (BR-DAG-AMEND-R1-23) is threaded straight through to both :func:`grep` (so ``mention_sites``
    never causes a second, independent tip resolution) and ``govbridge.authority.lifecycle.find_definition`` (pass
    5: that module now accepts it too, so ``definition_sites`` uses the SAME pinned "records" commit as
    ``mention_sites`` -- closing the residual gap pass 4's own docstring here used to document). When the caller
    gives no ``resolved_view`` (a standalone ``govbridge exact id`` invocation), THIS function resolves exactly
    ONCE, itself, right here -- never leaving `grep`/`find_definition` to each resolve independently on their own
    ``None`` fallback (a second re-audit, pass 5, found this was still happening: two separate resolutions for
    one `id_lookup` call, mention_sites and definition_sites each potentially seeing a different "records" tip)."""
    default_view, _ = _default_paths(repo)
    view_path = view_path or default_view
    if resolved_view is None:
        resolved_view = viewmod.resolve_view(viewmod.load_view(view_path), repo=repo)
    r = grep(token, ref=ref, view_path=view_path, repo=repo, task=task, resolved_view=resolved_view)
    r["mention_sites"] = r.pop("hits")
    definition_sites: list = []
    try:
        from govbridge.authority import lifecycle as lifecyclemod
        found = lifecyclemod.find_definition(token, repo=repo, view_path=view_path, resolved_view=resolved_view)
        if found is not None:
            def_path, def_commit, line_start, line_end = found
            definition_sites.append({
                "path": def_path, "commit": def_commit, "line_start": line_start, "line_end": line_end,
            })
    except Exception:
        pass  # id-grammar config/registry unavailable in this environment; mentions are still returned honestly
    r["definition_sites"] = definition_sites
    r["note"] = ("definition site resolved via config/id-grammar.yaml (govbridge.authority)" if definition_sites
                 else "no definition site resolved via config/id-grammar.yaml for this token")
    return r


def main(argv=None) -> int:
    p = argparse.ArgumentParser(prog="govbridge.core.exact")
    sub = p.add_subparsers(dest="cmd", required=True)

    sp_show = sub.add_parser("show")
    sp_show.add_argument("spec")
    sp_show.add_argument("--view")
    sp_show.add_argument("--rules")
    taskctxmod.add_cli_arg(sp_show)

    sp_grep = sub.add_parser("grep")
    sp_grep.add_argument("-F", dest="literal", required=True)
    sp_grep.add_argument("--ref")
    sp_grep.add_argument("--paths", nargs="*")
    sp_grep.add_argument("--view")
    sp_grep.add_argument("--rules")
    taskctxmod.add_cli_arg(sp_grep)

    sp_id = sub.add_parser("id")
    sp_id.add_argument("token")
    sp_id.add_argument("--ref")
    sp_id.add_argument("--view")
    taskctxmod.add_cli_arg(sp_id)

    sp_path = sub.add_parser("path")
    sp_path.add_argument("suffix")
    sp_path.add_argument("--ref")
    sp_path.add_argument("--view")

    args = p.parse_args(argv)
    ctx = taskctxmod.from_args(args)
    if args.cmd == "show":
        result = show(args.spec, view_path=args.view, rules_path=args.rules, task=ctx)
    elif args.cmd == "grep":
        result = grep(args.literal, ref=args.ref, paths=args.paths, view_path=args.view, rules_path=args.rules,
                       task=ctx)
    elif args.cmd == "id":
        result = id_lookup(args.token, ref=args.ref, view_path=args.view, task=ctx)
    elif args.cmd == "path":
        result = path_resolve(args.suffix, ref=args.ref, view_path=args.view)
    else:
        return 2
    print(json.dumps(result, indent=1, sort_keys=True))
    return 0 if "error" not in result else 1


if __name__ == "__main__":
    sys.exit(main())
