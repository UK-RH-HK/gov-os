#!/usr/bin/env python3
"""Edge derivation (ARCHITECTURE.md section 6.1). Every function here is BOUNDED: it derives edges reachable from
one seed/occurrence via a targeted git grep or a direct read, never a whole-corpus sweep (that is records.py's
census job, a different operation). Code-derived edges (CALLS/READS_KEY/TESTS) are read from a connection whose
tables match B3's schema (symbol, call_site, literal, resolution -- ARCHITECTURE.md section 4.6); with no
connection given, they are simply absent (MISSING), which is the honest state until I1 wires the real code route.
"""
from __future__ import annotations

import ast
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
SECTION_CITE_RE = re.compile(
    r"(?P<path>[A-Za-z0-9_./-]+\.[A-Za-z0-9_]+)\s+(?:section|§)\s*(?P<sec>\d+(?:\.\d+)*)", re.IGNORECASE
)
STRING_LITERAL_RE = re.compile(r'"((?:[^"\\]|\\.)*)"')
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
# DEPENDS_ON_DATA -- a code file's own string literal(s) that name a tracked repository path (REPAIR_PLAN.md
# section 4, RC-7: "no code-to-data edges"). Takes one already-read file's text (never a corpus scan): the caller
# (a route, a gather loop) already has the occurrence's text for the line it is looking at.
# ---------------------------------------------------------------------------------------------------------------

def depends_on_data_edges(text: str, path: str, commit: str, repo: Optional[str] = None,
                           code_dirs: tuple = CODE_DIRS) -> list:
    """A double-quoted string literal on a code line, generic across languages (the shape is "...", never a
    language-specific string-literal grammar): (1) the literal itself is a tracked path at ``commit``
    (EXACT_LITERAL_PATH); or (2) two to four of the line's literals, taken adjacent and IN ORDER and joined with
    '/', resolve -- directly, or (like ``cites_edges_in_text``'s own HEURISTIC_SUFFIX) as a UNIQUE path suffix --
    to a tracked path (HEURISTIC_JOINED_PATH; covers ``os.path.join("config", "id-grammar.yaml")``-shaped calls,
    generically, never one function name in particular)."""
    if not any(path.startswith(d) for d in code_dirs):
        return []
    out: list = []
    all_paths_cache: Optional[list] = None
    for i, line in enumerate(text.splitlines(), start=1):
        literals = [m.group(1) for m in STRING_LITERAL_RE.finditer(line) if m.group(1)]
        seen_on_line: set = set()

        for lit in literals:
            if lit in seen_on_line or ("/" not in lit and "." not in lit):
                continue
            if gitobj.ls_tree_path(commit, lit, repo=repo) is not None:
                seen_on_line.add(lit)
                out.append(E.Edge(src=occ(path, commit, i), type=E.DEPENDS_ON_DATA, dst=lit,
                                   derivation=E.EXACT_LITERAL_PATH, evidence_occurrence=occ(path, commit),
                                   evidence_line=i))

        for j in range(len(literals)):
            for n in range(2, 5):
                if j + n > len(literals):
                    break
                joined = "/".join(literals[j:j + n])
                if joined in seen_on_line or not joined:
                    continue
                resolved = joined
                derivation = E.HEURISTIC_JOINED_PATH
                if gitobj.ls_tree_path(commit, joined, repo=repo) is None:
                    if all_paths_cache is None:
                        all_paths_cache = gitobj.ls_tree_paths(commit, repo=repo)
                    matches = [p for p in all_paths_cache if p == joined or p.endswith("/" + joined)]
                    if len(matches) != 1:
                        continue
                    resolved = matches[0]
                seen_on_line.add(joined)
                out.append(E.Edge(src=occ(path, commit, i), type=E.DEPENDS_ON_DATA, dst=resolved,
                                   derivation=derivation, evidence_occurrence=occ(path, commit), evidence_line=i))
    return out


# ---------------------------------------------------------------------------------------------------------------
# CITES_REQUIREMENT -- a requirement citation inside a CODE FILE's own comment (RC-7: "no code-to-requirement
# edges"): "<doc>:<line>" (exact, or a unique suffix), or "<doc> section N" / "<doc> §N" (resolved to the
# first markdown heading at <doc> whose own leading numbering starts with N).
# ---------------------------------------------------------------------------------------------------------------

def _resolve_cited_path(candidate: str, commit: str, repo: Optional[str],
                         all_paths_cache: list) -> Optional[str]:
    if gitobj.ls_tree_path(commit, candidate, repo=repo) is not None:
        return candidate
    matches = [p for p in all_paths_cache if p == candidate or p.endswith("/" + candidate)]
    return matches[0] if len(matches) == 1 else None


def _first_heading_for_section(text: str, section_no: str) -> Optional[int]:
    for i, line in enumerate(text.splitlines(), start=1):
        m = re.match(r"^#{1,6}\s+(\d+(?:\.\d+)*)\b", line)
        if m and (m.group(1) == section_no or m.group(1).startswith(section_no + ".")):
            return i
    return None


def cites_requirement_edges_in_text(text: str, citing_path: str, citing_commit: str,
                                     repo: Optional[str] = None, code_dirs: tuple = CODE_DIRS) -> list:
    if not any(citing_path.startswith(d) for d in code_dirs):
        return []
    out: list = []
    all_paths_cache: Optional[list] = None
    heading_cache: dict = {}

    def _all_paths() -> list:
        nonlocal all_paths_cache
        if all_paths_cache is None:
            all_paths_cache = gitobj.ls_tree_paths(citing_commit, repo=repo)
        return all_paths_cache

    for i, line in enumerate(text.splitlines(), start=1):
        if not _looks_like_comment(line):
            continue
        for m in PATH_CITE_RE.finditer(line):
            candidate = m.group("path")
            l1 = m.group("l1")
            if l1 is None or ("/" not in candidate and "." not in candidate):
                continue  # a bare path mention with no line, in a comment, is not a requirement citation
            resolved_path = _resolve_cited_path(candidate, citing_commit, repo, _all_paths())
            if resolved_path is None:
                continue
            derivation = E.EXACT_COMMENT_CITATION if resolved_path == candidate else E.HEURISTIC_SUFFIX
            l2 = int(m.group("l2")) if m.group("l2") else int(l1)
            dst = f"{resolved_path}:{l1}-{l2}"
            out.append(E.Edge(src=occ(citing_path, citing_commit, i), type=E.CITES_REQUIREMENT, dst=dst,
                               derivation=derivation, evidence_occurrence=occ(citing_path, citing_commit),
                               evidence_line=i))
        for m in SECTION_CITE_RE.finditer(line):
            candidate, section_no = m.group("path"), m.group("sec")
            resolved_path = _resolve_cited_path(candidate, citing_commit, repo, _all_paths())
            if resolved_path is None:
                continue
            if resolved_path not in heading_cache:
                raw = gitobj.read_path(citing_commit, resolved_path, repo=repo)
                decoded = None
                if raw is not None:
                    try:
                        decoded = raw.decode("utf-8")
                    except UnicodeDecodeError:
                        decoded = None
                heading_cache[resolved_path] = decoded
            decoded = heading_cache[resolved_path]
            if decoded is None:
                continue
            found_line = _first_heading_for_section(decoded, section_no)
            if found_line is None:
                continue
            out.append(E.Edge(src=occ(citing_path, citing_commit, i), type=E.CITES_REQUIREMENT,
                               dst=f"{resolved_path}:{found_line}", derivation=E.HEURISTIC_COMMENT_SECTION,
                               evidence_occurrence=occ(citing_path, citing_commit), evidence_line=i,
                               note=f"section {section_no}"))
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


def _paginate(items: list, page_size: Optional[int], cursor: Optional[str]) -> tuple:
    """A simple, deterministic offset cursor (an ASCII integer string): ``items`` is already the full, sorted
    result; a caller with no ``page_size`` gets it back untouched (every EXISTING caller of ``tests_of``/
    ``reads_key_of`` -- a plain list -- keeps working unchanged). Otherwise a ``(page, next_cursor)`` pair, with
    ``next_cursor`` ``None`` once the union has been exhausted -- following it to exhaustion returns exactly
    ``items`` again, one page at a time (the paging acceptance check)."""
    if page_size is None:
        return items, None
    offset = int(cursor) if cursor else 0
    page = items[offset:offset + page_size]
    next_cursor = str(offset + page_size) if offset + page_size < len(items) else None
    return page, next_cursor


def reads_key_of(conn: Optional[sqlite3.Connection], key_literal: str, page_size: Optional[int] = None,
                  cursor: Optional[str] = None):
    if conn is None:
        return [] if page_size is None else {"items": [], "next_cursor": None, "total": 0}
    rows = conn.execute(
        "SELECT blob, line, enclosing_symbol FROM literal WHERE value = ? ORDER BY blob, line", (key_literal,)
    ).fetchall()
    out = [E.Edge(src=enclosing_symbol or f"{blob}:{line}", type=E.READS_KEY, dst=key_literal,
                   derivation=E.EXACT_SPAN, evidence_occurrence=f"{blob}:{line}", evidence_line=line)
           for blob, line, enclosing_symbol in rows]
    page, next_cursor = _paginate(out, page_size, cursor)
    if page_size is None:
        return page
    return {"items": page, "next_cursor": next_cursor, "total": len(out)}


def tests_of(conn: Optional[sqlite3.Connection], qualified_name: str, page_size: Optional[int] = None,
             cursor: Optional[str] = None):
    """TESTS(test -> symbol): every test-labelled symbol whose CALLS resolution reaches ``qualified_name``,
    EXACT_PATH when the resolution label itself is EXACT_PATH, HEURISTIC_NAME otherwise. ``page_size``/``cursor``
    (R1-RL paging): omitted, this returns the plain list exactly as before; given, a ``{"items", "next_cursor",
    "total"}`` page over the SAME sorted union."""
    if conn is None:
        return [] if page_size is None else {"items": [], "next_cursor": None, "total": 0}
    rows = conn.execute(
        "SELECT r.label, cs.blob, cs.line, cs.caller_symbol, s.is_test "
        "FROM resolution r JOIN call_site cs ON cs.rowid = r.call_site "
        "JOIN symbol s2 ON s2.symbol_id = r.target_symbol "
        "JOIN symbol s ON s.qualified_name = cs.caller_symbol "
        "WHERE s2.qualified_name = ? AND s.is_test = 1 ORDER BY cs.blob, cs.line", (qualified_name,),
    ).fetchall()
    out = []
    for label, blob, line, caller_symbol, _is_test in rows:
        derivation = E.EXACT_PATH if label == "EXACT_PATH" else E.HEURISTIC_NAME
        out.append(E.Edge(src=caller_symbol, type=E.TESTS, dst=qualified_name, derivation=derivation,
                           evidence_occurrence=f"{blob}:{line}", evidence_line=line))
    page, next_cursor = _paginate(out, page_size, cursor)
    if page_size is None:
        return page
    return {"items": page, "next_cursor": next_cursor, "total": len(out)}


# ---------------------------------------------------------------------------------------------------------------
# TESTS, beyond a direct in-test call: (b) a test that drives the product through its command-line binary, mapped
# generically -- by parsing the invoked module's OWN argparse dispatch structure at the same commit, never a
# hard-coded subcommand table of our own (OC-BR-02) -- through to its handler; (c) a test registry: a YAML file,
# anywhere, recognised by SHAPE (a row with a `tests:` list field) rather than by name.
# ---------------------------------------------------------------------------------------------------------------

def test_registry_edges_in_doc(doc, path: str, commit: str, unit: Optional[str] = None) -> list:
    """Every TESTS edge in an ALREADY-PARSED YAML document recognised as a test registry by SHAPE -- a top-level
    list (or a `rows`/`entries` key holding one) of mapping rows, each with a `tests` key that is itself a list of
    test paths/ids -- rather than by a specific file name (OC-BR-02; contrast ``evidence_map_edges_for_id``'s own
    fixed default path, an EXISTING, narrower capability this one generalises). ``unit``, if given, filters to rows
    mentioning it (``test_registry_edges_for_id``'s bounded, per-id use); omitted, every row's edges are returned
    (a whole-corpus layer builder's use, which already has the doc in hand and wants every row in one pass)."""
    rows = doc if isinstance(doc, list) else ((doc.get("rows") or doc.get("entries")) if isinstance(doc, dict)
                                                else None)
    if not isinstance(rows, list):
        return []
    out: list = []
    for row in rows:
        if not isinstance(row, dict) or not isinstance(row.get("tests"), list):
            continue
        if unit is not None and unit not in str(row):
            continue
        dst = unit if unit is not None else str(
            row.get("capability") or row.get("id") or row.get("requirement") or "?")
        for t in row["tests"]:
            out.append(E.Edge(src=str(t), type=E.TESTS, dst=dst, derivation=E.EXACT_TEST_REGISTRY_ROW,
                               evidence_occurrence=occ(path, commit)))
    return out


def test_registry_edges_for_id(unit: str, commit: str, repo: Optional[str] = None) -> list:
    """Bounded exactly like every other function here: a targeted git-grep for ``unit`` under ``tests/``, then each
    hit path is read once and checked for the registry shape (``test_registry_edges_in_doc``)."""
    from govbridge.core.yamlutil import load_yaml_text

    hits = gitobj.git_grep(unit, commit, paths=["tests/"], repo=repo)
    out: list = []
    seen_paths: set = set()
    for path, _line, _text in hits:
        if path in seen_paths or not path.endswith((".yaml", ".yml")):
            continue
        seen_paths.add(path)
        raw = gitobj.read_path(commit, path, repo=repo)
        if raw is None:
            continue
        try:
            doc = load_yaml_text(raw.decode("utf-8"))
        except Exception:
            continue
        out += test_registry_edges_in_doc(doc, path, commit, unit=unit)
    return out


def _argv_list_literal(call: ast.Call) -> Optional[list]:
    """The LITERAL PREFIX of ``call``'s first positional argument, IF it is a list literal: every leading element
    that is a string constant, or a bare ``sys.executable``/``<name>.executable`` attribute (represented here as
    the placeholder ``"<python>"``, since it is always the interpreter, never a subcommand). Stops at the first
    element this function cannot read generically (a variable such as a commit hash computed earlier in the test,
    an f-string, ...) and returns whatever literal prefix it already collected -- module path and subcommand are
    always among a real invocation's FIRST few tokens, so a trailing variable (a positional argument's value) never
    needs to be read to resolve the handler. ``None`` only when the argument is not a list literal at all."""
    if not call.args or not isinstance(call.args[0], ast.List):
        return None
    out = []
    for elt in call.args[0].elts:
        if isinstance(elt, ast.Constant) and isinstance(elt.value, str):
            out.append(elt.value)
        elif isinstance(elt, ast.Attribute) and elt.attr == "executable":
            out.append("<python>")
        else:
            break
    return out


def _module_path_to_domain_relpath(module_path: str) -> str:
    if module_path in ("govbridge", "govbridge.__main__"):
        # `python -m govbridge` runs govbridge/__main__.py, which only imports and calls govbridge.cli.main() (no
        # dispatch logic of its own to parse) -- a well-known, generic Python packaging convention (`-m <pkg>` runs
        # `<pkg>/__main__.py`), not a hard-coded subcommand of ours, so the real dispatch source to read is cli.py.
        return "govbridge/cli.py"
    return module_path.replace(".", "/") + ".py"


def _resolve_import_alias(tree: ast.AST, alias: str) -> Optional[str]:
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module:
            for a in node.names:
                if (a.asname or a.name) == alias:
                    return f"{node.module}.{a.name}"
        elif isinstance(node, ast.Import):
            for a in node.names:
                if (a.asname or a.name.split(".")[-1]) == alias:
                    return a.name
    return None


def _first_call_in_stmts(stmts: list) -> Optional[ast.Call]:
    for stmt in stmts:
        for node in ast.walk(stmt):
            if isinstance(node, ast.Call):
                return node
    return None


def _if_branch_for_subcommand(tree: ast.AST, subcommand: str) -> Optional[ast.Call]:
    """The first ``ast.Call`` inside the body of an ``if <name>.cmd == "<subcommand>":`` / ``if <name> ==
    "<subcommand>":`` branch, anywhere in ``tree`` (an if/elif chain is nested ``If.orelse`` in the AST, which
    ``ast.walk`` already descends into, so every branch of a chain is reached the same way). Generic over the
    comparison's left-hand variable name (``cmd``, ``args.cmd``, ...) -- this repository's own CLIs use both
    shapes (govbridge/cli.py: a bare ``cmd``; govbridge.code.symbols/.demo.cli and others: ``args.cmd``)."""
    for node in ast.walk(tree):
        if not isinstance(node, ast.If) or not isinstance(node.test, ast.Compare):
            continue
        cmp = node.test
        if len(cmp.ops) != 1 or not isinstance(cmp.ops[0], ast.Eq) or len(cmp.comparators) != 1:
            continue
        left = cmp.left
        left_is_cmd = isinstance(left, ast.Name) or (isinstance(left, ast.Attribute) and left.attr == "cmd")
        right = cmp.comparators[0]
        if left_is_cmd and isinstance(right, ast.Constant) and right.value == subcommand:
            call = _first_call_in_stmts(node.body)
            if call is not None:
                return call
    return None


def _dispatch_dict_target(tree: ast.AST, subcommand: str) -> Optional[str]:
    """A bare module-level ``{"<cmd>": "<module.path>", ...}`` dispatch table (govbridge/cli.py's own
    ``_DISPATCH``), found generically by shape (every key and value a string constant), not by the variable's
    name."""
    for node in ast.walk(tree):
        if not (isinstance(node, ast.Assign) and isinstance(node.value, ast.Dict)):
            continue
        keys, values = node.value.keys, node.value.values
        if not keys or not all(isinstance(k, ast.Constant) and isinstance(k.value, str) for k in keys):
            continue
        if not all(isinstance(v, ast.Constant) and isinstance(v.value, str) for v in values):
            continue
        mapping = {k.value: v.value for k, v in zip(keys, values)}
        if subcommand in mapping:
            return mapping[subcommand]
    return None


def _has_subparser_named(tree: ast.AST, subcommand: str) -> bool:
    for node in ast.walk(tree):
        if (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr == "add_parser"
                and node.args and isinstance(node.args[0], ast.Constant) and node.args[0].value == subcommand):
            return True
    return False


def resolve_cli_handler(module_path: str, argv_tail: list, commit: str, repo: Optional[str] = None,
                         _depth: int = 0) -> Optional[tuple]:
    """Resolve ``module_path``'s ``argv_tail[0]`` subcommand to its dispatch handler, purely by parsing that
    module's own source AT ``commit`` (never a table of our own) -- returns ``(qualified_target, derivation)`` or
    ``None``. Two hops deep at most (a top ``govbridge`` dispatch, then one submodule's own dispatch, matching the
    two-level ``govbridge <top> <sub>`` shapes this repository's own CLIs use, e.g. ``demo grade``)."""
    if not argv_tail or _depth > 2:
        return None
    subcommand = argv_tail[0]
    if subcommand.startswith("-"):
        return None
    # `-m govbridge` reads govbridge/cli.py (see _module_path_to_domain_relpath); its OWN dispatch functions
    # (cmd_search, cmd_compile, ...) live in that module, "govbridge.cli", not bare "govbridge" -- track the two
    # separately so a resolved LOCAL function is qualified correctly.
    read_module = "govbridge.cli" if module_path in ("govbridge", "govbridge.__main__") else module_path
    rel = _module_path_to_domain_relpath(module_path)
    from govbridge import GOV_BRIDGE_DOMAIN
    import os
    # GOV_BRIDGE_DOMAIN is an absolute filesystem path; a git tree path (what gitobj.read_path needs) is relative
    # to the REPO ROOT -- the same os.path.relpath(GOV_BRIDGE_DOMAIN, root) conversion
    # govbridge.core.manifest.bridge_code_tree already uses for exactly this reason.
    root = repo or gitobj.repo_root()
    domain_rel = os.path.relpath(GOV_BRIDGE_DOMAIN, root).replace(os.sep, "/")
    full_path = f"{domain_rel}/{rel}" if domain_rel != "." else rel
    raw = gitobj.read_path(commit, full_path, repo=repo)
    if raw is None:
        return None
    try:
        tree = ast.parse(raw.decode("utf-8"))
    except Exception:
        return None

    call = _if_branch_for_subcommand(tree, subcommand)
    if call is not None:
        func = call.func
        if isinstance(func, ast.Name):
            return f"{read_module}.{func.id}", E.EXACT_CLI_DISPATCH
        if isinstance(func, ast.Attribute) and isinstance(func.value, ast.Name):
            real_module = _resolve_import_alias(tree, func.value.id)
            if real_module:
                if len(argv_tail) > 1 and func.attr == "main":
                    nested = resolve_cli_handler(real_module, argv_tail[1:], commit, repo=repo, _depth=_depth + 1)
                    if nested:
                        return nested
                return f"{real_module}.{func.attr}", E.EXACT_CLI_DISPATCH

    target_module = _dispatch_dict_target(tree, subcommand)
    if target_module:
        if len(argv_tail) > 1:
            nested = resolve_cli_handler(target_module, argv_tail[1:], commit, repo=repo, _depth=_depth + 1)
            if nested:
                return nested
        return f"{target_module}.main", E.HEURISTIC_CLI_DISPATCH

    if _has_subparser_named(tree, subcommand):
        return f"{module_path}::{subcommand}", E.HEURISTIC_CLI_DISPATCH
    return None


def cli_dispatch_tests_edges(text: str, path: str, commit: str, repo: Optional[str] = None) -> list:
    """TESTS edges of derivation kind (b): a test that drives the product through its command-line binary
    (``subprocess.run([sys.executable, "-m", "<module>", "<subcommand>", ...])``), mapped generically -- via
    ``resolve_cli_handler`` -- to its dispatch handler. ``text``/``path`` are the ALREADY-READ test file (a Python
    source file); parsed once, here, with ``ast`` (never a regex over Python source)."""
    try:
        tree = ast.parse(text)
    except SyntaxError:
        return []
    out: list = []
    test_stack: list = []

    class _Visitor(ast.NodeVisitor):
        def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
            is_test = node.name.startswith("test_")
            if is_test:
                test_stack.append(node.name)
            self.generic_visit(node)
            if is_test:
                test_stack.pop()

        def visit_Call(self, node: ast.Call) -> None:
            if (isinstance(node.func, ast.Attribute) and node.func.attr == "run"
                    and isinstance(node.func.value, ast.Name) and node.func.value.id == "subprocess"):
                argv = _argv_list_literal(node)
                if argv and len(argv) >= 4 and argv[0] == "<python>" and argv[1] == "-m":
                    module_path = argv[2]
                    resolved = resolve_cli_handler(module_path, argv[3:], commit, repo=repo)
                    if resolved is not None:
                        target, derivation = resolved
                        test_name = test_stack[-1] if test_stack else "<module>"
                        out.append(E.Edge(src=test_name, type=E.TESTS, dst=target, derivation=derivation,
                                           evidence_occurrence=occ(path, commit, node.lineno),
                                           evidence_line=node.lineno,
                                           note=f"subprocess -m {module_path} {argv[3]}"))
            self.generic_visit(node)

    _Visitor().visit(tree)
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
