#!/usr/bin/env python3
"""Derives code-route seed symbols and bare occurrences from a task SEED that names a record (or a record-local
section), not a code symbol directly -- ARCHITECTURE.md section 7.2's G row, BR-HO-0015 (repair for the defect the
orchestrator's pre-dispatch run found: section G came out empty because "nothing derives seed symbols from record
seeds": ``govbridge.compile.packet``'s seed pass handed the code route a record id such as ``P2-AR-0097#F2``, and
the code route only ever resolves symbol NAMES).

A record's own text cites code in exactly the four shapes BR-HO-0015 names: ``path:N``, ``path:N-M``, a
path-qualified symbol (``module::fn``, ``Type::fn``), or a bare symbol in backticks. This module resolves each of
them at the view's CANONICAL PRODUCT ref (never the citing record's own ref -- G's job, ARCHITECTURE.md section
7.2, is "the code route at the canonical product ref"), using only the public entry points of
``govbridge.code.symbols`` (``definitions``, ``ensure_indexed_readonly``) and B5's own ``govbridge.graph.derive``
(``cites_edges_in_text``) -- neither module is edited here.

BR-DAG-AMEND-R1-17 item 5 reopening: this module is a QUERY at compile time, always against the canonical product
commit (an eager ref by default -- ``govbridge.code.build.eager_ref_names``). It reads via
``codesymbols._open_conn_readonly()``/``codesymbols.ensure_indexed_readonly()`` (never the BUILD-only
``_open_conn()``/``ensure_indexed``, which this module used to call, writing to the store on any commit the eager
builder had not already reached). A commit whose ``.rs`` blobs the eager builder has not indexed raises the typed
``codesymbols.StoreNeedsRebuild``, propagated to this module's own caller (``govbridge.compile.packet.Compiler.
code_seeds_for``, out of this node's mutation scope) unchanged.

Generic (OC-BR-02): every function takes a seed id, a commit and a grammar as DATA. Nothing here names Review 8,
Phase 2 or a particular file; the acceptance control for this module is D-0006, deliberately unrelated.
"""
from __future__ import annotations

import dataclasses
import re
from typing import Optional

from govbridge.authority import records as recordsmod
from govbridge.code import store as codestore
from govbridge.code import symbols as codesymbols
from govbridge.core import gitobj, pathrules
from govbridge.graph import derive as derivemod
from govbridge.graph import edges as edgesmod

# "module::fn" / "Type::fn" -- the SAME symbol-shaped-token pattern govbridge.route.router._SYMBOL_TOKEN_RE anchors
# on for its "::"-qualified half; kept as its own, smaller regex here (this module never scans for the bare
# `name()`-call shape that pattern also matches -- ARCHITECTURE.md section 6.1's SYMBOL_MENTION row names only
# "file.rs::name or Type::name" and "a bare backticked name", not a call-shaped token).
_QUALIFIED_TOKEN_RE = re.compile(r"\b[A-Za-z_][A-Za-z0-9_]*(?:::[A-Za-z_][A-Za-z0-9_]*)+\b")
# a bare identifier inside single backticks; the character class excludes ':', so this never also matches a
# qualified token (those are read by _QUALIFIED_TOKEN_RE instead, even when the prose backtick-quotes them).
_BACKTICK_BARE_RE = re.compile(r"`([A-Za-z_][A-Za-z0-9_]*)`")

EXACT_QUALIFIED = "EXACT_QUALIFIED"
HEURISTIC_NAME = "HEURISTIC_NAME"
HEURISTIC_AMBIGUOUS = "HEURISTIC_AMBIGUOUS"


@dataclasses.dataclass(frozen=True)
class CitedSymbol:
    """One code symbol a seed record's own text cites, resolved at the canonical product ref. ``label`` is how the
    citation itself was matched (never blurred with how a later CALLS/TESTS/READS_KEY expansion resolves -- those
    keep their own derive.py labels)."""
    name: str  # qualified_name at the product ref
    kind: str
    label: str
    path: str
    start_line: int
    end_line: int
    cite_path: str
    cite_line: int


@dataclasses.dataclass(frozen=True)
class CitedOccurrence:
    """A cited ``path:line`` that resolves to a real line at the product ref, but no parsed symbol encloses it
    (BR-HO-0015: "Where a cited line has no enclosing symbol, keep an occurrence-level G item for that line") --
    this is also how a cited evidence probe (a non-code path, e.g. under ``probes/``) surfaces, generically, with
    no special-casing of that directory name."""
    path: str
    line: int
    label: str
    cite_path: str
    cite_line: int


def _extract_definitions(decoded: str, path: str, grammar: "recordsmod.Grammar") -> list:
    if path.endswith((".yaml", ".yml")):
        return recordsmod.extract_definitions_yaml(decoded, path, grammar)
    if path.endswith(".md"):
        return recordsmod.extract_definitions_markdown(decoded, path, grammar)
    return []


def _whole_record_definition(record_id: str, records_commit: str, grammar: "recordsmod.Grammar",
                              repo: Optional[str] = None) -> Optional[tuple]:
    """(path, line_start, line_end, decoded_text) for the NON-local definition of ``record_id`` at
    ``records_commit`` -- the same git-grep-then-extract walk ``govbridge.graph.derive.defines_edges_for_id``
    performs (mirrored here, not imported, because that frozen function's ``Edge`` keeps only ``line_start``, never
    the ``line_end`` BR-HO-0015 needs to bound a citation scan to the record's own section -- ARCHITECTURE.md
    section 5.2 rule 1, "the file-level class never flows into a section")."""
    hits = gitobj.git_grep(record_id, records_commit, repo=repo)
    seen: set = set()
    for path, _line, _text in hits:
        if path in seen or pathrules.glob_match(path, grammar.fixtures_glob):
            continue
        seen.add(path)
        raw = gitobj.read_path(records_commit, path, repo=repo)
        if raw is None:
            continue
        try:
            decoded = raw.decode("utf-8")
        except UnicodeDecodeError:
            continue
        defs = _extract_definitions(decoded, path, grammar)
        defs += recordsmod.extract_definitions_file_stem(path, grammar, decoded.count("\n") + 1)
        for d in defs:
            if not d.local and d.id == record_id:
                return path, d.line_start, d.line_end, decoded
    return None


def record_span(seed_id: str, records_commit: str, grammar: "recordsmod.Grammar",
                 repo: Optional[str] = None) -> Optional[tuple]:
    """(path, line_start, line_end, decoded_text) for ``seed_id``'s own heading-delimited section at
    ``records_commit``. ``seed_id`` may be a bare record id, or ``RECORD#LOCAL`` (a record-local finding, e.g.
    ``P2-AR-0097#F2``) -- the id-grammar's own MP-BARE-LOCAL/DR-MD-HEADING-LOCAL convention: a local id is defined
    only inside the section of the record that names it (``config/id-grammar.yaml``), so this first finds the
    RECORD's own file, then re-scans that SAME file's text for the LOCAL heading. Returns None when ``seed_id`` is
    not itself a record/section definition at all -- the seed is presumably already a code symbol or bare path,
    left to the existing direct code-route path in ``govbridge.compile.packet``."""
    record_id, sep, local_id = seed_id.partition("#")
    found = _whole_record_definition(record_id, records_commit, grammar, repo=repo)
    if found is None:
        return None
    path, line_start, line_end, decoded = found
    if not sep:
        return path, line_start, line_end, decoded
    for d in _extract_definitions(decoded, path, grammar):
        if d.local and d.id == local_id:
            return path, d.line_start, d.line_end, decoded
    return None  # the local id is not defined inside its own record's file -- honest MISSING, never a guess


def _section_text(decoded: str, line_start: int, line_end: int) -> str:
    lines = decoded.splitlines(keepends=True)
    return "".join(lines[max(line_start - 1, 0):line_end])


def _path_to_blob(conn, product_commit: str, repo: Optional[str]) -> dict:
    """path -> blob_id for every ``.rs`` blob reachable at ``product_commit`` -- computed ONCE per
    ``cited_code_units`` call (the underlying read is cheap per blob, but it still walks the whole ``.rs`` tree, so
    this is looked up once per seed here, never once per citation). BR-DAG-AMEND-R1-17 item 5 reopening: reads via
    ``ensure_indexed_readonly`` -- raises ``StoreNeedsRebuild`` rather than classifying/parsing/persisting a
    not-yet-eager-indexed blob."""
    return {p: blob_id for p, blob_id in codesymbols.ensure_indexed_readonly(conn, product_commit, repo=repo)}


def _enclosing_symbol(conn, blob_id: str, line: int) -> Optional[dict]:
    """The SMALLEST ``code_symbol`` span at ``blob_id`` containing ``line`` -- a direct containment lookup over
    B3's own parsed span table, never a new resolution heuristic (the span itself IS the parse fact, so this is
    exact by construction whenever a symbol contains the line at all)."""
    best = None
    for r in codestore.symbols_for_blobs(conn, [blob_id]):
        if r["start_line"] <= line <= r["end_line"]:
            if best is None or (r["end_line"] - r["start_line"]) < (best["end_line"] - best["start_line"]):
                best = r
    return best


def _symbol_name_index(conn, path_to_blob: dict) -> tuple:
    """``(by_name, by_qualname)`` over EVERY symbol at the whole commit, built ONCE per ``cited_code_units`` call
    from the blobs ``_path_to_blob`` already enumerated -- the same ``(name, qualified_name)`` fields
    ``govbridge.code.symbols.definitions`` matches on, just precomputed as dicts instead of re-walking the whole
    ``.rs`` tree (``ensure_indexed``) for every single backticked/qualified token a record's text happens to
    mention. This adapter's ``qualified_name`` is at most ``ImplType::name`` (never a full module path -- see
    ``rust_treesitter._walk``), so an exact match on ``name`` or ``qualified_name`` covers exactly what
    ``definitions()`` itself would find; there is no third, suffix-only case this adapter can produce."""
    blob_to_path = {v: k for k, v in path_to_blob.items()}
    by_name: dict = {}
    by_qualname: dict = {}
    for r in codestore.symbols_for_blobs(conn, list(path_to_blob.values())):
        row = {"path": blob_to_path.get(r["blob_id"], ""), "qualified_name": r["qualified_name"], "kind": r["kind"],
               "start_line": r["start_line"], "end_line": r["end_line"]}
        by_name.setdefault(r["name"], []).append(row)
        by_qualname.setdefault(r["qualified_name"], []).append(row)
    return by_name, by_qualname


def _resolve_symbol_name(name: str, by_name: dict, by_qualname: dict, qualified: bool,
                          cite_path: str, cite_line: int, out: list, seen: set) -> None:
    """Looks ``name`` up against the precomputed whole-commit symbol index (the same ``(name, qualified_name)``
    match ``govbridge.code.symbols.definitions`` performs -- no new resolution logic, just no repeated
    ``ensure_indexed`` tree-walk per token). A qualified (``::``-bearing) token is EXACT_QUALIFIED only when it
    resolves to exactly one definition (ARCHITECTURE.md section 6.1's SYMBOL_MENTION row); a bare backticked token
    is always HEURISTIC_NAME (never promoted to exact, whatever the match count). Several surviving candidates are
    listed under HEURISTIC_AMBIGUOUS, never collapsed to one -- the same discipline section 4.6 requires of the
    code route's own call resolution."""
    hits = by_qualname.get(name) or by_name.get(name) or []
    if not hits:
        return
    if qualified and len(hits) == 1:
        label = EXACT_QUALIFIED
    elif qualified:
        label = HEURISTIC_AMBIGUOUS
    else:
        label = HEURISTIC_NAME
    for d in hits:
        key = d["qualified_name"]
        if key in seen:
            continue
        seen.add(key)
        out.append(CitedSymbol(name=key, kind=d["kind"], label=label, path=d["path"],
                                start_line=d["start_line"], end_line=d["end_line"],
                                cite_path=cite_path, cite_line=cite_line))


def cited_code_units(seed_id: str, product_commit: str, records_commit: str, grammar: "recordsmod.Grammar",
                      repo: Optional[str] = None) -> tuple:
    """Every code/test unit ``seed_id``'s own record text cites, resolved at the canonical product ref:
    ``(symbols, occurrences)`` -- ``symbols``: ``tuple[CitedSymbol]`` (an enclosing definition was found for a
    ``path:line`` citation, or a ``::``-qualified/backticked token resolved directly to a definition);
    ``occurrences``: ``tuple[CitedOccurrence]`` (the CITED LINE ITSELF, for every ``path:line``/``path:line-line``
    citation -- ALWAYS emitted, whether or not an enclosing symbol was also found; this is also how a cited
    evidence probe surfaces, generically, since it never resolves to a symbol). Returns ``((), ())`` when
    ``seed_id`` is not itself a record (nothing to derive; the seed is presumably already a code symbol or path)."""
    span = record_span(seed_id, records_commit, grammar, repo=repo)
    if span is None:
        return (), ()
    cite_path, line_start, line_end, decoded = span
    text = _section_text(decoded, line_start, line_end)

    conn = codesymbols._open_conn_readonly()
    path_to_blob = _path_to_blob(conn, product_commit, repo)
    by_name, by_qualname = _symbol_name_index(conn, path_to_blob)
    symbols_out: list = []
    occ_out: list = []
    seen_syms: set = set()
    seen_occs: set = set()

    # path[:N[-M]] citations -- resolved directly against the PRODUCT tree; a bare CITES_PATH (no line) names no
    # single location to resolve a symbol from and is left to the record's own graph/B/C-section representation.
    fake_view = None  # cites_edges_in_text accepts it but never dereferences it (derive.py's own function body).
    for edge in derivemod.cites_edges_in_text(text, cite_path, product_commit, fake_view, repo=repo):
        if edge.type != edgesmod.CITES_LINE:
            continue
        target_path, _, rng = edge.dst.partition(":")
        line = int(rng.split("-", 1)[0])
        # cites_edges_in_text already confirmed target_path exists in the product tree (it resolves the path via
        # git ls-tree before ever emitting an edge) -- a non-.rs path (an evidence probe, a config file, ...) has
        # no blob_id here (ensure_indexed only enumerates .rs blobs), which correctly falls through to the
        # occurrence-level branch below, exactly like a .rs line no symbol happens to enclose. Neither case is a
        # reason to drop the citation.
        # BR-AR-0015 reopening, defect 3: a path:line citation yields BOTH (a) the cited line's own occurrence and
        # (b) its enclosing definition, when one is found -- never either/or. A CALLS/TESTS/READS_KEY edge that
        # happens to land on this same line (T2 expansion, below) is never the citation's own resolution.
        occ_key = (target_path, line)
        if occ_key not in seen_occs:
            seen_occs.add(occ_key)
            occ_out.append(CitedOccurrence(path=target_path, line=line, label=edge.derivation,
                                            cite_path=cite_path, cite_line=edge.evidence_line))
        blob_id = path_to_blob.get(target_path)
        sym = _enclosing_symbol(conn, blob_id, line) if blob_id is not None else None
        if sym is None:
            continue
        sym_key = sym["qualified_name"]
        if sym_key not in seen_syms:
            seen_syms.add(sym_key)
            symbols_out.append(CitedSymbol(name=sym_key, kind=sym["kind"], label=edge.derivation, path=target_path,
                                            start_line=sym["start_line"], end_line=sym["end_line"],
                                            cite_path=cite_path, cite_line=edge.evidence_line))

    # path-qualified symbol mentions ("module::fn", "Type::fn") and bare backticked symbols.
    for lineno, line_text in enumerate(text.splitlines(), start=line_start):
        for m in _QUALIFIED_TOKEN_RE.finditer(line_text):
            _resolve_symbol_name(m.group(0), by_name, by_qualname, True, cite_path, lineno, symbols_out, seen_syms)
        for m in _BACKTICK_BARE_RE.finditer(line_text):
            _resolve_symbol_name(m.group(1), by_name, by_qualname, False, cite_path, lineno, symbols_out, seen_syms)

    return tuple(symbols_out), tuple(occ_out)
