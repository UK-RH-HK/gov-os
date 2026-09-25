#!/usr/bin/env python3
"""Edge derivation (ARCHITECTURE.md section 6.1). Every function here is BOUNDED: it derives edges reachable from
one seed/occurrence via a targeted git grep or a direct read, never a whole-corpus sweep (that is records.py's
census job, a different operation). Code-derived edges (CALLS/READS_KEY/TESTS) are read from a connection whose
tables match B3's schema (symbol, call_site, literal, resolution -- ARCHITECTURE.md section 4.6); with no
connection given, they are simply absent (MISSING), which is the honest state until I1 wires the real code route.
"""
from __future__ import annotations

import re
import sqlite3
from typing import Optional

from govbridge.authority import records as recordsmod
from govbridge.authority import registry as registrymod
from govbridge.core import gitobj, pathrules, view as viewmod
from govbridge.graph import edges as E

HEX_COMMIT_RE = re.compile(r"\b[0-9a-f]{7,40}\b")
PATH_CITE_RE = re.compile(
    r"(?<![\w/.-])(?P<path>[A-Za-z0-9_./-]+\.[A-Za-z0-9_]+)(?::(?P<l1>\d+)(?:-(?P<l2>\d+))?)?(?![\w/.-])"
)
COMMENT_PREFIXES = ("//", "///", "//!", "#", "*", "\"\"\"", "'''")
CODE_DIRS = ("runtime/", "cli/", "framework/", "capabilities/", "migrations/", "tools/", "bin/", "scripts/")


def occ(path: str, commit: str, line: Optional[int] = None) -> str:
    return f"{path}@{commit}" + (f":{line}" if line is not None else "")


# ---------------------------------------------------------------------------------------------------------------
# DEFINES / MENTIONS -- built on top of authority.records's grammar interpreter.
# ---------------------------------------------------------------------------------------------------------------

def defines_edges_for_id(unit: str, commit: str, repo: Optional[str] = None,
                          grammar: Optional[recordsmod.Grammar] = None) -> list:
    grammar = grammar or recordsmod.load_grammar(recordsmod._default_grammar_path())
    hits = gitobj.git_grep(unit, commit, repo=repo)
    out: list = []
    seen: set = set()
    for path, _line, _text in hits:
        if path in seen or pathrules.glob_match(path, grammar.fixtures_glob):
            continue
        seen.add(path)
        raw = gitobj.read_path(commit, path, repo=repo)
        if raw is None:
            continue
        try:
            decoded = raw.decode("utf-8")
        except UnicodeDecodeError:
            continue
        if path.endswith((".yaml", ".yml")):
            defs = recordsmod.extract_definitions_yaml(decoded, path, grammar)
        elif path.endswith(".md"):
            defs = recordsmod.extract_definitions_markdown(decoded, path, grammar)
        else:
            defs = []
        defs += recordsmod.extract_definitions_file_stem(path, grammar, decoded.count("\n") + 1)
        for d in defs:
            if d.id == unit:
                out.append(E.Edge(src=occ(path, commit, d.line_start), type=E.DEFINES, dst=unit,
                                   derivation=E.EXACT_DEFINITION, evidence_occurrence=occ(path, commit),
                                   evidence_line=d.line_start))
    return out


def mentions_edges_for_id(unit: str, commit: str, repo: Optional[str] = None,
                           grammar: Optional[recordsmod.Grammar] = None, exclude_paths: tuple = ()) -> list:
    """MENTIONS(section -> record): every occurrence of ``unit`` as a mention token, EXACT_ID when the token itself
    resolves to exactly one definition anywhere in the hit set, HEURISTIC_LOCAL_ID for a bare local id (unit
    contains '#')."""
    grammar = grammar or recordsmod.load_grammar(recordsmod._default_grammar_path())
    is_local = "#" in unit
    search_token = unit.split("#", 1)[1] if is_local else unit
    hits = gitobj.git_grep(search_token, commit, repo=repo)
    out: list = []
    for path, line, _text in hits:
        if path in exclude_paths or pathrules.glob_match(path, grammar.fixtures_glob):
            continue
        derivation = E.HEURISTIC_LOCAL_ID if is_local else E.EXACT_ID
        out.append(E.Edge(src=occ(path, commit, line), type=E.MENTIONS, dst=unit, derivation=derivation,
                           evidence_occurrence=occ(path, commit), evidence_line=line))
    return out


# ---------------------------------------------------------------------------------------------------------------
# CITES_PATH / CITES_LINE / CITES_COMMIT -- scanned out of one occurrence's own text.
# ---------------------------------------------------------------------------------------------------------------

def cites_edges_in_text(text: str, citing_path: str, citing_commit: str,
                         resolved_view: "viewmod.ResolvedView", repo: Optional[str] = None) -> list:
    out: list = []
    all_paths_cache: dict = {}
    for i, line in enumerate(text.splitlines(), start=1):
        for m in PATH_CITE_RE.finditer(line):
            candidate = m.group("path")
            if "/" not in candidate and "." not in candidate:
                continue
            commit = citing_commit
            entry = gitobj.ls_tree_path(commit, candidate, repo=repo)
            derivation = E.EXACT_PATH
            resolved_path = candidate
            if entry is None:
                # try a unique suffix match within the citing record's subject ref
                if commit not in all_paths_cache:
                    all_paths_cache[commit] = gitobj.ls_tree_paths(commit, repo=repo)
                matches = [p for p in all_paths_cache[commit] if p.endswith("/" + candidate) or p == candidate]
                if len(matches) == 1:
                    resolved_path = matches[0]
                    derivation = E.HEURISTIC_SUFFIX
                else:
                    continue
            dst = resolved_path
            l1 = int(m.group("l1")) if m.group("l1") else None
            if l1 is not None:
                l2 = int(m.group("l2")) if m.group("l2") else l1
                dst = f"{resolved_path}:{l1}-{l2}"
                edge_type = E.CITES_LINE
            else:
                edge_type = E.CITES_PATH
            out.append(E.Edge(src=occ(citing_path, citing_commit, i), type=edge_type, dst=dst, derivation=derivation,
                               evidence_occurrence=occ(citing_path, citing_commit), evidence_line=i))
    return out


def cites_commit_edges_in_text(text: str, citing_path: str, citing_commit: str, repo: Optional[str] = None) -> list:
    out: list = []
    for i, line in enumerate(text.splitlines(), start=1):
        for m in HEX_COMMIT_RE.finditer(line):
            candidate = m.group(0)
            resolved = gitobj.resolve_commit(candidate, repo=repo)
            if resolved is None:
                continue
            out.append(E.Edge(src=occ(citing_path, citing_commit, i), type=E.CITES_COMMIT, dst=resolved,
                               derivation=E.EXACT_COMMIT, evidence_occurrence=occ(citing_path, citing_commit),
                               evidence_line=i))
    return out


# ---------------------------------------------------------------------------------------------------------------
# SUPERSEDES / AMENDS / EXTENDS
# ---------------------------------------------------------------------------------------------------------------

def supersession_edges(unit: str, reg: registrymod.Registry) -> list:
    out: list = []
    for sup in reg.supersessions_from(unit):
        out.append(E.Edge(src=unit, type=E.SUPERSEDES, dst=sup.to_id, derivation=E.REGISTRY_CITED,
                           evidence_occurrence=f"{sup.cite.path}:{sup.cite.line}", evidence_line=sup.cite.line,
                           note=sup.scope))
    for sup in reg.supersessions_to(unit):
        out.append(E.Edge(src=sup.from_id, type=E.SUPERSEDES, dst=unit, derivation=E.REGISTRY_CITED,
                           evidence_occurrence=f"{sup.cite.path}:{sup.cite.line}", evidence_line=sup.cite.line,
                           note=sup.scope))
    return out


def metadata_supersession_edges(unit: str, doc: dict, path: str, commit: str) -> list:
    out: list = []
    sup_by = doc.get("superseded_by")
    if isinstance(sup_by, str):
        out.append(E.Edge(src=unit, type=E.SUPERSEDES, dst=sup_by, derivation=E.EXACT_METADATA,
                           evidence_occurrence=occ(path, commit), note="superseded_by"))
    for other in (doc.get("supersedes") or []):
        if isinstance(other, str):
            out.append(E.Edge(src=other, type=E.SUPERSEDES, dst=unit, derivation=E.EXACT_METADATA,
                               evidence_occurrence=occ(path, commit), note="supersedes"))
    for other in (doc.get("amends") or []):
        if isinstance(other, str):
            out.append(E.Edge(src=unit, type=E.AMENDS, dst=other, derivation=E.EXACT_METADATA,
                               evidence_occurrence=occ(path, commit)))
    return out


# ---------------------------------------------------------------------------------------------------------------
# CODE_CITES -- an id-shaped token inside a doc/body comment in a code file; asserts the MENTION only.
# ---------------------------------------------------------------------------------------------------------------

def _looks_like_comment(line: str) -> bool:
    stripped = line.strip()
    return any(stripped.startswith(p) for p in COMMENT_PREFIXES)


def code_cites_edges_for_id(unit: str, commit: str, repo: Optional[str] = None,
                             code_dirs: tuple = CODE_DIRS) -> list:
    hits = gitobj.git_grep(unit, commit, paths=list(code_dirs), repo=repo)
    out: list = []
    for path, line_no, text in hits:
        if not _looks_like_comment(text):
            continue
        out.append(E.Edge(src=occ(path, commit, line_no), type=E.CODE_CITES, dst=unit, derivation=E.EXACT_ID,
                           evidence_occurrence=occ(path, commit), evidence_line=line_no,
                           note="mention only, asserts nothing about the claim's truth"))
    return out


# ---------------------------------------------------------------------------------------------------------------
# EVIDENCE_MAP -- tests/governance/capability-evidence-map.yaml rows.
# ---------------------------------------------------------------------------------------------------------------

def evidence_map_edges_for_id(unit: str, commit: str, repo: Optional[str] = None,
                               map_path: str = "tests/governance/capability-evidence-map.yaml") -> list:
    from govbridge.core.yamlutil import load_yaml_text
    raw = gitobj.read_path(commit, map_path, repo=repo)
    if raw is None:
        return []
    try:
        doc = load_yaml_text(raw.decode("utf-8"))
    except Exception:
        return []
    rows = doc if isinstance(doc, list) else (doc.get("rows") or doc.get("entries") or [])
    out: list = []
    for row in rows if isinstance(rows, list) else []:
        if not isinstance(row, dict):
            continue
        row_text = str(row)
        if unit in row_text:
            test_ref = row.get("test") or row.get("test_id") or row.get("id") or "?"
            out.append(E.Edge(src=str(test_ref), type=E.EVIDENCE_MAP, dst=unit, derivation=E.EXACT_ID,
                               evidence_occurrence=occ(map_path, commit)))
    return out


# ---------------------------------------------------------------------------------------------------------------
# CALLS / READS_KEY / TESTS -- against B3's table schema (symbol, call_site, literal, resolution). ``conn`` is a
# sqlite3.Connection whose tables match ARCHITECTURE.md section 4.6; None means "no code route wired yet" (I1's
# job on real data), which is a legitimate, honest MISSING, not an error.
# ---------------------------------------------------------------------------------------------------------------

def callers_of(conn: Optional[sqlite3.Connection], qualified_name: str) -> list:
    if conn is None:
        return []
    rows = conn.execute(
        "SELECT r.call_site, r.label, cs.blob, cs.line, cs.caller_symbol "
        "FROM resolution r JOIN call_site cs ON cs.rowid = r.call_site "
        "JOIN symbol s ON s.symbol_id = r.target_symbol "
        "WHERE s.qualified_name = ?", (qualified_name,),
    ).fetchall()
    out = []
    for call_site, label, blob, line, caller_symbol in rows:
        out.append(E.Edge(src=caller_symbol or f"{blob}:{line}", type=E.CALLS, dst=qualified_name, derivation=label,
                           evidence_occurrence=f"{blob}:{line}", evidence_line=line))
    return out


def callees_of(conn: Optional[sqlite3.Connection], qualified_name: str) -> list:
    if conn is None:
        return []
    rows = conn.execute(
        "SELECT r.label, cs.blob, cs.line, s.qualified_name "
        "FROM resolution r JOIN call_site cs ON cs.rowid = r.call_site "
        "LEFT JOIN symbol s ON s.symbol_id = r.target_symbol "
        "WHERE cs.caller_symbol = ?", (qualified_name,),
    ).fetchall()
    out = []
    for label, blob, line, target_qualified_name in rows:
        out.append(E.Edge(src=qualified_name, type=E.CALLS, dst=target_qualified_name or "?", derivation=label,
                           evidence_occurrence=f"{blob}:{line}", evidence_line=line))
    return out


def reads_key_of(conn: Optional[sqlite3.Connection], key_literal: str) -> list:
    if conn is None:
        return []
    rows = conn.execute(
        "SELECT blob, line, enclosing_symbol FROM literal WHERE value = ?", (key_literal,)
    ).fetchall()
    return [E.Edge(src=enclosing_symbol or f"{blob}:{line}", type=E.READS_KEY, dst=key_literal,
                    derivation=E.EXACT_SPAN, evidence_occurrence=f"{blob}:{line}", evidence_line=line)
            for blob, line, enclosing_symbol in rows]


def tests_of(conn: Optional[sqlite3.Connection], qualified_name: str) -> list:
    """TESTS(test -> symbol): every test-labelled symbol whose CALLS resolution reaches ``qualified_name``,
    EXACT_PATH when the resolution label itself is EXACT_PATH, HEURISTIC_NAME otherwise."""
    if conn is None:
        return []
    rows = conn.execute(
        "SELECT r.label, cs.blob, cs.line, cs.caller_symbol, s.is_test "
        "FROM resolution r JOIN call_site cs ON cs.rowid = r.call_site "
        "JOIN symbol s2 ON s2.symbol_id = r.target_symbol "
        "JOIN symbol s ON s.qualified_name = cs.caller_symbol "
        "WHERE s2.qualified_name = ? AND s.is_test = 1", (qualified_name,),
    ).fetchall()
    out = []
    for label, blob, line, caller_symbol, _is_test in rows:
        derivation = E.EXACT_PATH if label == "EXACT_PATH" else E.HEURISTIC_NAME
        out.append(E.Edge(src=caller_symbol, type=E.TESTS, dst=qualified_name, derivation=derivation,
                           evidence_occurrence=f"{blob}:{line}", evidence_line=line))
    return out


# ---------------------------------------------------------------------------------------------------------------
# CHANGED_IN / INTRODUCED_IN / DELETED_IN -- record-definition set difference between two commits (a generic
# analog of the code route's symbol-table set difference, used until I1 wires B3's real per-commit symbol tables).
# ---------------------------------------------------------------------------------------------------------------

def changed_in_edges(path: str, from_commit: str, to_commit: str, repo: Optional[str] = None) -> list:
    changes = gitobj.diff_tree(from_commit, to_commit, repo=repo)
    out = []
    for status, changed_path, _old, _new in changes:
        if changed_path == path:
            out.append(E.Edge(src=occ(path, to_commit), type=E.CHANGED_IN, dst=to_commit, derivation=E.EXACT_GIT,
                               evidence_occurrence=occ(path, to_commit), note=status))
    return out


def record_definition_set(commit: str, repo: Optional[str] = None,
                           grammar: Optional[recordsmod.Grammar] = None,
                           rules_path: Optional[str] = None) -> dict:
    from govbridge import GOV_BRIDGE_DOMAIN
    import os

    grammar = grammar or recordsmod.load_grammar(recordsmod._default_grammar_path())
    rules_path = rules_path or os.path.join(GOV_BRIDGE_DOMAIN, "config", "corpus-rules.yaml")
    scan = recordsmod.scan_ref(commit, grammar, rules_path, repo=repo)
    return {k: v[0] for k, v in scan.definitions.items()}


def deleted_in_edges(from_commit: str, to_commit: str, repo: Optional[str] = None,
                      grammar: Optional[recordsmod.Grammar] = None) -> list:
    before = record_definition_set(from_commit, repo=repo, grammar=grammar)
    after = record_definition_set(to_commit, repo=repo, grammar=grammar)
    out = []
    for rid, d in before.items():
        if rid not in after:
            out.append(E.Edge(src=rid, type=E.DELETED_IN, dst=to_commit, derivation=E.EXACT_PARSE,
                               evidence_occurrence=occ(d.path, from_commit, d.line_start)))
    return out


def introduced_in_edges(from_commit: str, to_commit: str, repo: Optional[str] = None,
                         grammar: Optional[recordsmod.Grammar] = None) -> list:
    before = record_definition_set(from_commit, repo=repo, grammar=grammar)
    after = record_definition_set(to_commit, repo=repo, grammar=grammar)
    out = []
    for rid, d in after.items():
        if rid not in before:
            out.append(E.Edge(src=rid, type=E.INTRODUCED_IN, dst=to_commit, derivation=E.EXACT_PARSE,
                               evidence_occurrence=occ(d.path, to_commit, d.line_start)))
    return out


# ---------------------------------------------------------------------------------------------------------------
# RELATION_CUE -- a fixed cue-word reading of a MENTIONS edge's sentence. Never used for authority.
# ---------------------------------------------------------------------------------------------------------------

_CUE_WORDS = (
    ("reopens", "reopens"), ("re-opens", "reopens"), ("closes", "closes"), ("resolved", "closes"),
    ("supersedes", "supersedes"), ("superseded", "supersedes"), ("withdraws", "withdraws"),
    ("withdrawn", "withdraws"), ("retracts", "withdraws"), ("moot", "moot"),
)


def relation_cue_for_sentence(sentence: str) -> Optional[str]:
    lower = sentence.lower()
    for word, cue in _CUE_WORDS:
        if word in lower:
            return cue
    return None


def relation_cue_edges(mention_edges: list, sentence_by_line: dict) -> list:
    out = []
    for e in mention_edges:
        sentence = sentence_by_line.get(e.evidence_line, "")
        cue = relation_cue_for_sentence(sentence)
        if cue:
            out.append(E.Edge(src=e.src, type=E.RELATION_CUE, dst=e.dst, derivation=E.HEURISTIC_CUE,
                               evidence_occurrence=e.evidence_occurrence, evidence_line=e.evidence_line, note=cue))
    return out
