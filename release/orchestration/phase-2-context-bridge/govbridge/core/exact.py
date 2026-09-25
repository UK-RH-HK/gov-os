#!/usr/bin/env python3
"""The exact route (ARCHITECTURE.md section 4.2): a thin, deterministic wrapper over Git, authoritative about Git
content. ``show``/``grep``/``path`` are fully generic Git wrappers. ``id`` is a bounded placeholder: true
definition-site resolution needs the id-grammar (``config/id-grammar.yaml``, node B5, not yet built); until then
``id`` reports every literal mention it can find via Git and says so, rather than guessing at a definition.

Every subcommand honours the corpus rules (``config/corpus-rules.yaml``): for a path whose corpus_effect is
EXCLUDE, only metadata and the rule id are returned, never the content.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from typing import Optional

from govbridge.core import corpus, gitobj, view as viewmod
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
          repo: Optional[str] = None) -> dict:
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

    rules = corpus.load_rules(rules_path)
    with gitobj.CatFileBatch(repo=repo) as cat:
        sniffer = corpus.ContentSniffer(cat)
        verdict = corpus.classify_entry(entry, rules, sniffer)

        result = {
            "ref": ref, "commit": commit, "path": path, "blob": entry.oid, "size": entry.size,
            "corpus_rule": verdict.rule_id, "corpus_effect": verdict.effect,
        }

        vc = viewmod.load_view(view_path)
        resolved = viewmod.resolve_view(vc, repo=repo)
        classification = resolved.classify_occurrence(path, commit, queried_blob=entry.oid)
        result["version_status"] = classification.status
        result["canonical_ref"] = classification.canonical_ref
        result["canonical_commit"] = classification.canonical_commit

        if verdict.effect == "EXCLUDE":
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
          view_path: Optional[str] = None, rules_path: Optional[str] = None, repo: Optional[str] = None) -> dict:
    default_view, default_rules = _default_paths(repo)
    view_path = view_path or default_view
    rules_path = rules_path or default_rules
    vc = viewmod.load_view(view_path)
    resolved = viewmod.resolve_view(vc, repo=repo)
    if ref is None:
        primary = next(r for r in vc.refs if r.role == "primary")
        commit = resolved.named[primary.name].commit
        ref = primary.name
    else:
        commit = gitobj.resolve_commit(ref, repo=repo) or ref

    hits = gitobj.git_grep(literal, commit, paths=paths, repo=repo)
    rules = corpus.load_rules(rules_path)
    out = []
    skipped = 0
    verdict_cache: dict[str, str] = {}
    with gitobj.CatFileBatch(repo=repo) as cat:
        sniffer = corpus.ContentSniffer(cat)
        for path, lineno, text in hits:
            if path not in verdict_cache:
                entry = gitobj.ls_tree_path(commit, path, repo=repo)
                v = corpus.classify_entry(entry, rules, sniffer) if entry else None
                verdict_cache[path] = v.effect if v else "EXCLUDE"
            if verdict_cache[path] == "EXCLUDE":
                skipped += 1
                continue
            out.append({"path": path, "line": lineno, "text": text})
    return {"ref": ref, "commit": commit, "query": literal, "hits": out, "excluded_skipped": skipped}


def path_resolve(suffix: str, ref: Optional[str] = None, view_path: Optional[str] = None,
                   repo: Optional[str] = None) -> dict:
    default_view, _ = _default_paths(repo)
    view_path = view_path or default_view
    vc = viewmod.load_view(view_path)
    resolved = viewmod.resolve_view(vc, repo=repo)
    if ref is None:
        primary = next(r for r in vc.refs if r.role == "primary")
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
               repo: Optional[str] = None) -> dict:
    """A bounded placeholder for id resolution: every literal mention of ``token``, found generically via Git.
    Definition-site classification (which mention is THE definition) needs the id-grammar rules that node B5 owns;
    until B5 lands, every hit is reported as a mention, none as a definition, and the result says so explicitly so
    nothing downstream mistakes an unclassified mention for authority."""
    r = grep(token, ref=ref, view_path=view_path, repo=repo)
    r["definition_sites"] = []
    r["mention_sites"] = r.pop("hits")
    r["note"] = "definition-site resolution requires config/id-grammar.yaml (node B5); not yet available"
    return r


def main(argv=None) -> int:
    p = argparse.ArgumentParser(prog="govbridge.core.exact")
    sub = p.add_subparsers(dest="cmd", required=True)

    sp_show = sub.add_parser("show")
    sp_show.add_argument("spec")
    sp_show.add_argument("--view")
    sp_show.add_argument("--rules")

    sp_grep = sub.add_parser("grep")
    sp_grep.add_argument("-F", dest="literal", required=True)
    sp_grep.add_argument("--ref")
    sp_grep.add_argument("--paths", nargs="*")
    sp_grep.add_argument("--view")
    sp_grep.add_argument("--rules")

    sp_id = sub.add_parser("id")
    sp_id.add_argument("token")
    sp_id.add_argument("--ref")
    sp_id.add_argument("--view")

    sp_path = sub.add_parser("path")
    sp_path.add_argument("suffix")
    sp_path.add_argument("--ref")
    sp_path.add_argument("--view")

    args = p.parse_args(argv)
    if args.cmd == "show":
        result = show(args.spec, view_path=args.view, rules_path=args.rules)
    elif args.cmd == "grep":
        result = grep(args.literal, ref=args.ref, paths=args.paths, view_path=args.view, rules_path=args.rules)
    elif args.cmd == "id":
        result = id_lookup(args.token, ref=args.ref, view_path=args.view)
    elif args.cmd == "path":
        result = path_resolve(args.suffix, ref=args.ref, view_path=args.view)
    else:
        return 2
    print(json.dumps(result, indent=1, sort_keys=True))
    return 0 if "error" not in result else 1


if __name__ == "__main__":
    sys.exit(main())
