#!/usr/bin/env python3
"""``govbridge cite <identifier> [--commit C]`` (REPAIR_DAG.yaml node R1-RA, REPAIR_PLAN.md section 7):
resolve one named identifier to an exact citation -- ``(path, commit, lines, symbol if any)`` -- or report
``AMBIGUOUS`` with every candidate. Never ``NOT_FOUND`` treated as an error: an honest "does not resolve" is a
normal, disclosed result, matching every other query command's own conventions in this codebase.

**Four identifier kinds** (REPAIR_DAG.yaml node R1-RA, "REAL INPUT SHAPES"), dispatched by SHAPE alone, never by a
hard-coded name (OC-BR-02):

1. **Rust symbols** -- a bare ``fn_name`` or a ``mod::fn`` path. The code layer's own tree-sitter adapter
   (``govbridge.code.adapters.rust_treesitter``) stores a free or mod-nested function's ``qualified_name`` as its
   BARE name only (module nesting is never tracked; only an ``impl`` block's own ``Type::method`` qualification
   is) -- so a ``mod::fn``-shaped query needs **trailing-segment resolution**: the exact qualified string is tried
   first (catches a genuine ``Type::method`` hit), and only if that finds nothing does this module retry with just
   the trailing segment after the last ``::``. Either way, more than one surviving candidate is ``AMBIGUOUS``,
   listing all of them -- this module never guesses a "best" one (``govbridge.code.symbols`` itself already
   follows this discipline for ``HEURISTIC_AMBIGUOUS``; this is the same discipline for its own new fallback).
2. **Python test names** -- the persisted code layer indexes ``.rs`` only (``ARCHITECTURE.md`` section 4.6); a
   Python identifier is resolved through **the exact route** (``govbridge.core.exact.grep``, corpus-rule and
   task-exclusion aware, never the store) for a literal ``"def <name>("`` occurrence under ``*.py``, labelled
   ``PYTHON_DEF_EXACT_GREP`` -- a distinct heuristic, never confused with a Rust resolution label.
3. **id-grammar ids** -- resolved through the existing, already-tested ``govbridge.authority.lifecycle.
   find_definition``, which already covers a YAML top-level/list ``id:`` key (block OR flow style -- PyYAML parses
   both the same way once composed) and a Markdown heading/table definition (``config/id-grammar.yaml``).
4. **document section anchors** (``<doc> §N``) -- the document path is resolved through the exact route's own
   ``path_resolve`` (so an ambiguous suffix is reported exactly like every other exact-route lookup), then the
   requested numbered heading is located in ``govbridge.compile.sectionmap.markdown_sections`` (R1-RM's own
   section map, reused here rather than re-implemented).

Nothing here writes to the store: every code-route call goes through ``govbridge.code.symbols``'s own
``ensure_indexed_readonly`` path (BR-DAG-AMEND-R1-17), and every other lookup is a Git plumbing read
(``govbridge.core.gitobj``) or a pure-text parse (``govbridge.compile.sectionmap``).
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from typing import Optional

KIND_RUST = "rust_symbol"
KIND_PYTHON = "python_def"
KIND_ID = "id_grammar"
KIND_DOC = "doc_section"
KIND_CODE = "code"  # the classification BEFORE the rust/python cascade decides which of the two actually resolved

STATUS_RESOLVED = "RESOLVED"
STATUS_AMBIGUOUS = "AMBIGUOUS"
STATUS_NOT_FOUND = "NOT_FOUND"

LABEL_RUST_EXACT = "EXACT_QUALIFIED_MATCH"
LABEL_RUST_TRAILING = "HEURISTIC_TRAILING_SEGMENT"
LABEL_PYTHON = "PYTHON_DEF_EXACT_GREP"
LABEL_ID_GRAMMAR = "ID_GRAMMAR_DEFINITION"
LABEL_DOC_ANCHOR = "DOC_SECTION_ANCHOR"
LABEL_DOC_PATH_AMBIGUOUS = "DOC_PATH_AMBIGUOUS"

#: "<doc> §N[.N...]" -- a document section anchor (REPAIR_DAG.yaml node R1-RA REAL INPUT SHAPES item 4).
DOC_ANCHOR_RE = re.compile(r"^(?P<doc>\S+)\s+§\s*(?P<section>\d+(?:\.\d+)*)$")


def id_token_re():
    """The id-grammar's own generic id-token shape (``govbridge.authority.records.ID_TOKEN_RE``), re-exported here
    so both this module's :func:`classify_identifier` and ``govbridge.answers.lint``'s own identifier-candidate
    scan use the exact same pattern. Imported lazily so this module (a leaf, read-only lookup tool) never pays for
    ``govbridge.authority.records``'s own heavier imports (yaml, gitobj, ...) unless a caller actually asks for an
    id-grammar-shaped identifier."""
    from govbridge.authority import records as recordsmod
    return recordsmod.ID_TOKEN_RE


def classify_identifier(identifier: str) -> str:
    """Dispatch on SHAPE alone (OC-BR-02): a document section anchor, an id-grammar-shaped token, or a code
    identifier (Rust, tried first, falling back to Python -- see :func:`cite_identifier`)."""
    if DOC_ANCHOR_RE.match(identifier):
        return KIND_DOC
    if id_token_re().fullmatch(identifier):
        return KIND_ID
    return KIND_CODE


def _default_view_path() -> str:
    from govbridge import GOV_BRIDGE_DOMAIN
    return os.path.join(GOV_BRIDGE_DOMAIN, "config", "canonical-view.yaml")


def _default_product_commit(view_path: Optional[str], repo: Optional[str]) -> Optional[str]:
    """The canonical view's own ``role: product`` ref, resolved to a commit -- generically, by role, never by a
    hard-coded ref name (OC-BR-02). Falls back to ``role: primary`` when no ``product`` role is declared (a
    single-ref view collapses every role together, ARCHITECTURE.md section 1.2's "ordinary V8.3 operation" case)."""
    from govbridge.core import view as viewmod
    vp = view_path or _default_view_path()
    vc = viewmod.load_view(vp)
    resolved = viewmod.resolve_view(vc, repo=repo)
    for role in ("product", "primary"):
        for r in vc.refs:
            if r.role == role:
                ref = resolved.named.get(r.name)
                if ref is not None:
                    return ref.commit
    return None


def _rust_citation(hit: dict, commit_full: str) -> dict:
    return {"path": hit["path"], "commit": commit_full, "lines": [hit["start_line"], hit["end_line"]],
            "symbol": hit["qualified_name"]}


def _resolve_rust(identifier: str, commit: str, repo: Optional[str]) -> dict:
    from govbridge.code import symbols as codesymbols

    d = codesymbols.definitions(identifier, commit, repo=repo)
    hits = d["definitions"]
    commit_full = d["commit"]
    label = LABEL_RUST_EXACT
    if not hits and "::" in identifier:
        trailing = identifier.rsplit("::", 1)[-1]
        d = codesymbols.definitions(trailing, commit, repo=repo)
        hits = d["definitions"]
        commit_full = d["commit"]
        label = LABEL_RUST_TRAILING
    if not hits:
        return {"status": STATUS_NOT_FOUND, "candidates": []}
    candidates = [_rust_citation(h, commit_full) for h in hits]
    if len(candidates) > 1:
        return {"status": STATUS_AMBIGUOUS, "candidates": candidates, "label": label}
    return {"status": STATUS_RESOLVED, "citation": candidates[0], "label": label}


def _resolve_rust_safe(identifier: str, commit: Optional[str], repo: Optional[str]) -> dict:
    if commit is None:
        return {"status": STATUS_NOT_FOUND, "candidates": [], "note": "no product-role commit resolvable"}
    from govbridge.code import symbols as codesymbols
    try:
        return _resolve_rust(identifier, commit, repo)
    except codesymbols.StoreNeedsRebuild as e:
        # honest MISSING (the same discipline every other optional code-route caller in this codebase already
        # follows) -- never raised out of a read-only lookup tool.
        return {"status": STATUS_NOT_FOUND, "candidates": [], "note": f"code layer unavailable: {e}"}


def _resolve_python(identifier: str, commit: Optional[str], repo: Optional[str],
                     view_path: Optional[str] = None) -> dict:
    from govbridge.core import exact as exactmod

    literal = f"def {identifier}("
    r = exactmod.grep(literal, ref=commit, paths=["*.py"], view_path=view_path, repo=repo)
    hits = r.get("hits") or []
    if not hits:
        return {"status": STATUS_NOT_FOUND, "candidates": []}
    commit_full = r.get("commit", commit)
    candidates = [
        {"path": h["path"], "commit": commit_full, "lines": [h["line"], h["line"]], "symbol": identifier}
        for h in hits
    ]
    if len(candidates) > 1:
        return {"status": STATUS_AMBIGUOUS, "candidates": candidates, "label": LABEL_PYTHON}
    return {"status": STATUS_RESOLVED, "citation": candidates[0], "label": LABEL_PYTHON}


def _resolve_id_grammar(identifier: str, repo: Optional[str], view_path: Optional[str]) -> dict:
    from govbridge.authority import lifecycle as lifecyclemod

    found = lifecyclemod.find_definition(identifier, repo=repo, view_path=view_path)
    if found is None:
        return {"status": STATUS_NOT_FOUND, "candidates": []}
    path, commit, line_start, line_end = found
    citation = {"path": path, "commit": commit, "lines": [line_start, line_end], "symbol": None}
    return {"status": STATUS_RESOLVED, "citation": citation, "label": LABEL_ID_GRAMMAR}


def _resolve_doc_anchor(doc: str, section: str, commit: Optional[str], repo: Optional[str],
                         view_path: Optional[str]) -> dict:
    from govbridge.compile import sectionmap as sectionmapmod
    from govbridge.core import exact as exactmod
    from govbridge.core import gitobj

    pr = exactmod.path_resolve(doc, ref=commit, view_path=view_path, repo=repo)
    if pr.get("ambiguous"):
        candidates = [{"path": p} for p in (pr.get("candidates") or [])]
        if not candidates:
            return {"status": STATUS_NOT_FOUND, "candidates": []}
        return {"status": STATUS_AMBIGUOUS, "candidates": candidates, "label": LABEL_DOC_PATH_AMBIGUOUS}

    path = pr["resolved"]
    commit_full = pr["commit"]
    raw = gitobj.read_path(commit_full, path, repo=repo)
    if raw is None:
        return {"status": STATUS_NOT_FOUND, "candidates": []}
    text = raw.decode("utf-8", "replace")
    sections = sectionmapmod.markdown_sections(text)

    matches = []
    for s in sections:
        m = re.match(r"^(\d+(?:\.\d+)*)\b", s.name)
        if m and m.group(1) == section:
            matches.append(s)
    if not matches:
        return {"status": STATUS_NOT_FOUND, "candidates": []}
    candidates = [
        {"path": path, "commit": commit_full, "lines": [s.line_start, s.line_end], "symbol": None,
         "section_title": s.name}
        for s in matches
    ]
    if len(candidates) > 1:
        return {"status": STATUS_AMBIGUOUS, "candidates": candidates, "label": LABEL_DOC_ANCHOR}
    return {"status": STATUS_RESOLVED, "citation": candidates[0], "label": LABEL_DOC_ANCHOR}


def cite_identifier(identifier: str, *, commit: Optional[str] = None, view_path: Optional[str] = None,
                     repo: Optional[str] = None, registry_path: Optional[str] = None) -> dict:
    """Resolve ``identifier`` to ``{identifier, kind, status, citation|candidates, label}``. ``registry_path`` is
    accepted for CLI-signature symmetry with every other query command but unused: none of the four identifier
    kinds this module resolves needs an authority-registry lookup of its own."""
    del registry_path
    kind = classify_identifier(identifier)

    if kind == KIND_DOC:
        m = DOC_ANCHOR_RE.match(identifier)
        out = _resolve_doc_anchor(m.group("doc"), m.group("section"), commit, repo, view_path)
    elif kind == KIND_ID:
        out = _resolve_id_grammar(identifier, repo, view_path)
    else:
        rust_commit = commit if commit is not None else _default_product_commit(view_path, repo)
        out = _resolve_rust_safe(identifier, rust_commit, repo)
        if out["status"] == STATUS_NOT_FOUND and "::" not in identifier:
            py_out = _resolve_python(identifier, commit, repo, view_path=view_path)
            if py_out["status"] != STATUS_NOT_FOUND:
                out = py_out
            else:
                combined_note = "; ".join(n for n in (out.get("note"), py_out.get("note")) if n)
                out = {"status": STATUS_NOT_FOUND, "candidates": [],
                       "note": combined_note or "no Rust definition and no Python def(...) found"}

    return {"identifier": identifier, "kind": kind, **out}


def main(argv=None) -> int:
    p = argparse.ArgumentParser(prog="govbridge cite")
    p.add_argument("identifier")
    p.add_argument("--commit")
    p.add_argument("--view")
    p.add_argument("--repo")
    p.add_argument("--registry")
    args = p.parse_args(argv)

    result = cite_identifier(args.identifier, commit=args.commit, view_path=args.view, repo=args.repo,
                              registry_path=args.registry)
    print(json.dumps(result, indent=1, sort_keys=True))
    return 0 if result["status"] == STATUS_RESOLVED else 1


if __name__ == "__main__":
    sys.exit(main())
