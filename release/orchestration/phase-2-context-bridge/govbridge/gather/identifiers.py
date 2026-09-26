#!/usr/bin/env python3
"""Identifier extraction (REPAIR_PLAN.md section 2.5; REPAIR_DAG.yaml node R1-GA2; OD-BR-05 section 3). Given a
round's merged evidence (``govbridge.route.router.RouteHit`` objects), find every NEW identifier that evidence
exposes -- an id-grammar record id, a symbol-shaped token, a Rust ``mod::fn`` test path, a repository path literal
or a joined path fragment, a commit hash, or a ``<doc> section N`` / ``<doc> §N`` requirement citation -- so
``govbridge.gather.followup`` can issue a triggered round for each one.

Generic, not bespoke (OC-BR-02): every pattern here is reused, never re-invented, from the SAME regexes/grammars
the rest of this domain already uses for the identical shape --

* id-grammar mention patterns: ``govbridge.authority.records.load_grammar`` (the SAME grammar
  ``govbridge.core.exact.id_lookup``/``govbridge.graph.derive`` already interpret);
* symbol-shaped tokens and Rust qualified paths: ``govbridge.route.router._SYMBOL_TOKEN_RE`` (the exact pattern
  ``govbridge.route.router.select_routes``/``govbridge.route.real_routes._extract_symbol_names`` already use to
  decide "this text names a symbol");
* path literals, joined path fragments, commit hashes and requirement citations:
  ``govbridge.graph.derive``'s own ``PATH_CITE_RE``/``STRING_LITERAL_RE``/``HEX_COMMIT_RE``/``SECTION_CITE_RE`` and
  ``_looks_like_comment`` -- the SAME grammar ``govbridge.graph.derive.depends_on_data_edges``/
  ``cites_requirement_edges_in_text`` already used to derive ``DEPENDS_ON_DATA``/``CITES_REQUIREMENT`` edges into
  ``govbridge.code.lineage_layer``'s persisted ``lineage_edge`` table at build time.

:func:`extract_from_lineage` is the OTHER half of extraction, and the one this node's brief calls out by name:
rather than re-deriving a citation/dependency from a hit's own text a second time, it reads the ALREADY-COMPUTED
``lineage_edge`` rows for that hit's own occurrence straight out of the store (a read-only ``SELECT``, never a
write -- BR-DAG-AMEND-R1-15) -- the single source of truth R1-RL built for exactly this purpose.
"""
from __future__ import annotations

import dataclasses
import sqlite3
from typing import Optional

from govbridge.authority import records as recordsmod
from govbridge.graph import derive as derivemod
from govbridge.graph import edges as edgesmod
from govbridge.route import router as routermod

KIND_RECORD_ID = "record_id"
KIND_SYMBOL = "symbol"
KIND_RUST_TEST_PATH = "rust_test_path"
KIND_PATH_LITERAL = "path_literal"
KIND_JOINED_PATH_LITERAL = "joined_path_literal"
KIND_COMMIT = "commit"
KIND_REQUIREMENT_CITATION = "requirement_citation"
KIND_TESTS_OF = "tests_of"  # a dst discovered directly from a persisted lineage_edge TESTS row

ALL_KINDS = (KIND_RECORD_ID, KIND_SYMBOL, KIND_RUST_TEST_PATH, KIND_PATH_LITERAL, KIND_JOINED_PATH_LITERAL,
             KIND_COMMIT, KIND_REQUIREMENT_CITATION, KIND_TESTS_OF)

#: a candidate is dropped if its value alone would make it indistinguishable from ordinary prose -- generic bounds,
#: never a name/id from a particular corpus (OC-BR-02).
_MIN_PATH_LITERAL_LEN = 3


@dataclasses.dataclass(frozen=True)
class Identifier:
    """One candidate identifier discovered in a round's evidence. ``source_*`` is the occurrence it was found IN
    (never confused with the identifier's own, not-yet-resolved location); ``note`` carries a human-readable reason
    (e.g. which lineage_edge row/derivation produced it) for telemetry/debugging, never used for matching.
    ``mention_count``: how many hits, across every extractor and every batch this identifier has been merged from
    (the BR-AR-0024 reopening), mentioned this exact ``(kind, value)`` -- :func:`_dedupe_identifiers` SUMS this
    across duplicates rather than discarding them, so a caller merging identifiers across rounds
    (:mod:`govbridge.gather.followup`'s own priority queue) can use it as a relevance signal ("how many frontier
    items mention them") without re-scanning anything."""
    kind: str
    value: str
    source_unit_id: Optional[str] = None
    source_route: Optional[str] = None
    source_path: Optional[str] = None
    source_commit: Optional[str] = None
    source_ref: Optional[str] = None
    note: Optional[str] = None
    mention_count: int = 1

    def key(self) -> tuple:
        """The visited-set key (REPAIR_PLAN.md section 2.5: "a visited set prevents loops") -- kind+value only,
        deliberately never the source, so the SAME identifier discovered from two different hits is chased once."""
        return (self.kind, self.value)

    def to_dict(self) -> dict:
        return dataclasses.asdict(self)


def _hit_text(hit) -> str:
    return getattr(hit, "text", None) or ""


def _hit_occurrence(hit):
    occs = getattr(hit, "occurrences", None) or ()
    return occs[0] if occs else None


def _default_grammar():
    try:
        return recordsmod.load_grammar(recordsmod._default_grammar_path())
    except Exception:
        return None


def extract_record_ids(hits: list, grammar=None) -> list:
    """id-grammar-shaped tokens mentioned in a hit's text (REAL INPUT SHAPES: "id-grammar ids in Markdown heading
    titles and in YAML (block and flow style)") -- a heading title or a YAML scalar that itself CITES another id is
    ordinary retrieved TEXT by the time it reaches here, so the SAME mention-pattern scan that finds an id anywhere
    else finds it. A record-LOCAL id (``local: true``, e.g. a bare ``A2``-shaped token) is never resolvable as a
    global definition on its own (config/id-grammar.yaml's own documented rule), so it is skipped here, not
    chased as a dead end."""
    grammar = grammar if grammar is not None else _default_grammar()
    if grammar is None:
        return []
    out: list = []
    for h in hits:
        text = _hit_text(h)
        if not text:
            continue
        occ = _hit_occurrence(h)
        seen_here: set = set()
        for pat in grammar.mention_patterns:
            if pat.get("local"):
                continue
            for m in pat["regex"].finditer(text):
                token = m.group(0)
                if token in seen_here:
                    continue
                seen_here.add(token)
                out.append(Identifier(
                    kind=KIND_RECORD_ID, value=token, source_unit_id=getattr(h, "unit_id", None),
                    source_route=getattr(h, "route", None), source_path=getattr(occ, "path", None),
                    source_commit=getattr(occ, "commit", None), source_ref=getattr(occ, "ref", None),
                    note=f"id-grammar mention pattern {pat['id']}",
                ))
    return out


def extract_symbols_and_rust_paths(hits: list) -> list:
    """Symbol-shaped tokens (``routermod._SYMBOL_TOKEN_RE``, the SAME shape ``select_routes``/
    ``_extract_symbol_names`` already use). A token with ``::`` in it is a Rust qualified path -- REAL INPUT SHAPES
    item 2, ``mod::fn`` -- kept as its own kind so :mod:`govbridge.gather.followup` can apply the trailing-segment
    fallback the code layer's own module-free ``qualified_name`` convention requires; anything else is a bare
    symbol/function-call token."""
    out: list = []
    for h in hits:
        text = _hit_text(h)
        if not text:
            continue
        occ = _hit_occurrence(h)
        seen_here: set = set()
        for m in routermod._SYMBOL_TOKEN_RE.finditer(text):
            tok = m.group(0).rstrip("()")
            if not tok or tok in seen_here:
                continue
            seen_here.add(tok)
            kind = KIND_RUST_TEST_PATH if "::" in tok else KIND_SYMBOL
            out.append(Identifier(
                kind=kind, value=tok, source_unit_id=getattr(h, "unit_id", None),
                source_route=getattr(h, "route", None), source_path=getattr(occ, "path", None),
                source_commit=getattr(occ, "commit", None), source_ref=getattr(occ, "ref", None),
            ))
    return out


def extract_commit_hashes(hits: list) -> list:
    """40-hex and short (7+) commit hashes (REAL INPUT SHAPES item 5), reusing
    ``govbridge.graph.derive.HEX_COMMIT_RE`` verbatim (never a second commit-hash grammar)."""
    out: list = []
    for h in hits:
        text = _hit_text(h)
        if not text:
            continue
        occ = _hit_occurrence(h)
        seen_here: set = set()
        for m in derivemod.HEX_COMMIT_RE.finditer(text):
            tok = m.group(0)
            if tok in seen_here:
                continue
            seen_here.add(tok)
            out.append(Identifier(
                kind=KIND_COMMIT, value=tok, source_unit_id=getattr(h, "unit_id", None),
                source_route=getattr(h, "route", None), source_path=getattr(occ, "path", None),
                source_commit=getattr(occ, "commit", None), source_ref=getattr(occ, "ref", None),
            ))
    return out


def extract_path_literals(hits: list, repo: Optional[str] = None) -> list:
    """Repository path literals (``routermod._PATH_TOKEN_RE``) and JOINED path literals (two to four adjacent
    quoted string fragments, joined with '/' -- the exact heuristic
    ``govbridge.graph.derive.depends_on_data_edges`` already uses to build ``DEPENDS_ON_DATA`` edges at index time,
    reused here rather than re-invented) -- REAL INPUT SHAPES item 4: "joined path literals". A joined candidate is
    kept even when it cannot be resolved against ``repo`` right here (resolution, including the unique-suffix
    fallback, is :mod:`govbridge.gather.followup`'s job, against the ACTUAL commit/ref the hit came from, which
    this function -- text-only -- does not itself decide)."""
    out: list = []
    for h in hits:
        text = _hit_text(h)
        if not text:
            continue
        occ = _hit_occurrence(h)
        seen_here: set = set()
        for m in routermod._PATH_TOKEN_RE.finditer(text):
            tok = m.group(0)
            if len(tok) < _MIN_PATH_LITERAL_LEN or tok in seen_here:
                continue
            seen_here.add(tok)
            out.append(Identifier(
                kind=KIND_PATH_LITERAL, value=tok, source_unit_id=getattr(h, "unit_id", None),
                source_route=getattr(h, "route", None), source_path=getattr(occ, "path", None),
                source_commit=getattr(occ, "commit", None), source_ref=getattr(occ, "ref", None),
            ))
        for line in text.splitlines():
            literals = [mm.group(1) for mm in derivemod.STRING_LITERAL_RE.finditer(line) if mm.group(1)]
            for j in range(len(literals)):
                for n in range(2, 5):
                    if j + n > len(literals):
                        break
                    joined = "/".join(literals[j:j + n])
                    if not joined or joined in seen_here:
                        continue
                    seen_here.add(joined)
                    out.append(Identifier(
                        kind=KIND_JOINED_PATH_LITERAL, value=joined, source_unit_id=getattr(h, "unit_id", None),
                        source_route=getattr(h, "route", None), source_path=getattr(occ, "path", None),
                        source_commit=getattr(occ, "commit", None), source_ref=getattr(occ, "ref", None),
                        note="two-to-four adjacent quoted literals, joined with '/' (derive.depends_on_data_edges shape)",
                    ))
    return out


def extract_requirement_citations(hits: list) -> list:
    """``<doc> §N`` / ``<doc> section N`` / ``<doc>:<line>`` citations inside a ``///``/``//!``/``#`` comment line
    (REAL INPUT SHAPES item 3), reusing ``derivemod.PATH_CITE_RE``/``SECTION_CITE_RE``/``_looks_like_comment``
    verbatim -- the exact grammar ``cites_requirement_edges_in_text`` already uses to build ``CITES_REQUIREMENT``
    edges at index time. A ``§N-M``/``§N–M`` range keeps both bounds in ``note`` so
    :mod:`govbridge.gather.followup` can resolve the whole range, not just its start."""
    out: list = []
    for h in hits:
        text = _hit_text(h)
        if not text:
            continue
        occ = _hit_occurrence(h)
        seen_here: set = set()
        for line in text.splitlines():
            if not derivemod._looks_like_comment(line):
                continue
            for m in derivemod.PATH_CITE_RE.finditer(line):
                candidate, l1, l2 = m.group("path"), m.group("l1"), m.group("l2")
                if l1 is None or ("/" not in candidate and "." not in candidate):
                    continue
                key = ("path_line", candidate, l1, l2)
                if key in seen_here:
                    continue
                seen_here.add(key)
                out.append(Identifier(
                    kind=KIND_REQUIREMENT_CITATION, value=candidate, source_unit_id=getattr(h, "unit_id", None),
                    source_route=getattr(h, "route", None), source_path=getattr(occ, "path", None),
                    source_commit=getattr(occ, "commit", None), source_ref=getattr(occ, "ref", None),
                    note=f"path:line l1={l1} l2={l2 or l1}",
                ))
            for m in derivemod.SECTION_CITE_RE.finditer(line):
                candidate, sec, sec2 = m.group("path"), m.group("sec"), m.group("sec2")
                key = ("section", candidate, sec, sec2)
                if key in seen_here:
                    continue
                seen_here.add(key)
                out.append(Identifier(
                    kind=KIND_REQUIREMENT_CITATION, value=candidate, source_unit_id=getattr(h, "unit_id", None),
                    source_route=getattr(h, "route", None), source_path=getattr(occ, "path", None),
                    source_commit=getattr(occ, "commit", None), source_ref=getattr(occ, "ref", None),
                    note=f"section sec={sec} sec2={sec2 or ''}",
                ))
    return out


def _dedupe_identifiers(idents: list) -> list:
    """First occurrence wins for ``source_*``/``note``; ``mention_count`` is SUMMED across every duplicate
    (the BR-AR-0024 reopening) -- correct whether the duplicates being merged already carry a summed count
    themselves (this function is applied in two stages: once per extractor, then again over the combined list in
    :func:`extract_all`) or a fresh count of 1 each."""
    seen: dict = {}
    order: list = []
    for i in idents:
        key = i.key()
        if key not in seen:
            seen[key] = i
            order.append(key)
        else:
            existing = seen[key]
            seen[key] = dataclasses.replace(existing, mention_count=existing.mention_count + i.mention_count)
    return [seen[k] for k in order]


def extract_from_text(hits: list, grammar=None, repo: Optional[str] = None) -> list:
    """Every text-based extractor, combined and de-duplicated by ``(kind, value)`` (first occurrence wins, so
    ``source_*`` records where the identifier was FIRST seen this round)."""
    out: list = []
    out.extend(extract_record_ids(hits, grammar=grammar))
    out.extend(extract_symbols_and_rust_paths(hits))
    out.extend(extract_commit_hashes(hits))
    out.extend(extract_path_literals(hits, repo=repo))
    out.extend(extract_requirement_citations(hits))
    return _dedupe_identifiers(out)


# ---------------------------------------------------------------------------------------------------------------
# The OTHER extraction path: read ALREADY-DERIVED edges straight out of R1-RL's persisted ``lineage_edge`` table,
# for the exact occurrence a hit came from -- never a second derivation of the same fact (this node's brief:
# "Your resolvers must USE it"). A read-only SELECT only (BR-DAG-AMEND-R1-15): the caller is responsible for
# passing a connection opened ``store.open_db_readonly()`` when the read-only property must hold.
# ---------------------------------------------------------------------------------------------------------------

_LINEAGE_TABLE_CACHE: dict = {}


def _lineage_table_exists(conn: sqlite3.Connection) -> bool:
    """``lineage_edge`` may not exist at all on a bare/isolated connection (a unit test's own in-memory store that
    never ran ``govbridge.code.lineage_layer_builder``) -- an honest empty result in that case, the same
    "code-route-optional... honest MISSING, never a crash" discipline ``govbridge.graph.derive`` already documents
    (module docstring), never a raised exception."""
    key = id(conn)
    cached = _LINEAGE_TABLE_CACHE.get(key)
    if cached is not None:
        return cached
    try:
        conn.execute("SELECT 1 FROM lineage_edge LIMIT 1")
        ok = True
    except sqlite3.OperationalError:
        ok = False
    _LINEAGE_TABLE_CACHE[key] = ok
    return ok


def extract_from_lineage(conn: Optional[sqlite3.Connection], hits: list) -> list:
    """For every hit whose occurrence names a ``(ref, commit, path)`` with a known line span, every persisted
    ``lineage_edge`` row whose ``evidence_occurrence``/``evidence_line`` falls inside that span becomes an
    :class:`Identifier` naming its ``dst`` -- ``TESTS`` (direct calls, CLI dispatch, test-registry rows, at ANY
    derivation label -- ``KIND_TESTS_OF``), ``DEPENDS_ON_DATA`` (``KIND_JOINED_PATH_LITERAL``/``KIND_PATH_LITERAL``
    depending on the derivation) and ``CITES_REQUIREMENT`` (``KIND_REQUIREMENT_CITATION``, including the
    document-only ``HEURISTIC_SECTION_UNRESOLVED`` label -- never dropped just because the section heading itself
    did not resolve at INDEX time; :mod:`govbridge.gather.followup` still retrieves the document). Every row's own
    ``ref_name``/``commit_id``/``version_status`` is carried through in ``note`` (this node's brief: "per-row ref,
    commit and version_status")."""
    if conn is None or not hits:
        return []
    if not _lineage_table_exists(conn):
        return []
    out: list = []
    for h in hits:
        occ = _hit_occurrence(h)
        if occ is None or not getattr(occ, "path", None) or not getattr(occ, "commit", None):
            continue
        ref_name = getattr(occ, "ref", None)
        path, commit = occ.path, occ.commit
        line_start = occ.line_start if occ.line_start is not None else 1
        line_end = occ.line_end if occ.line_end is not None else line_start
        prefix = f"{path}@{commit}"
        try:
            rows = conn.execute(
                "SELECT ref_name, commit_id, src, type, dst, derivation, evidence_line, version_status "
                "FROM lineage_edge WHERE commit_id = ? AND evidence_occurrence = ? "
                "AND (evidence_line IS NULL OR (evidence_line >= ? AND evidence_line <= ?))",
                (commit, prefix, line_start, line_end),
            ).fetchall()
        except sqlite3.OperationalError:
            continue
        for row_ref, row_commit, src, etype, dst, derivation, evidence_line, version_status in rows:
            if ref_name is not None and row_ref != ref_name:
                continue
            note = (f"lineage_edge type={etype} derivation={derivation} ref={row_ref} commit={row_commit} "
                    f"version_status={version_status} src={src}")
            if etype == edgesmod.TESTS:
                kind = KIND_TESTS_OF
            elif etype == edgesmod.DEPENDS_ON_DATA:
                kind = (KIND_JOINED_PATH_LITERAL if derivation == edgesmod.HEURISTIC_JOINED_PATH
                        else KIND_PATH_LITERAL)
            elif etype == edgesmod.CITES_REQUIREMENT:
                kind = KIND_REQUIREMENT_CITATION
            else:
                continue
            out.append(Identifier(
                kind=kind, value=dst, source_unit_id=getattr(h, "unit_id", None),
                source_route=getattr(h, "route", None), source_path=path, source_commit=commit,
                source_ref=row_ref, note=note,
            ))
    return _dedupe_identifiers(out)


def extract_all(hits: list, grammar=None, conn: Optional[sqlite3.Connection] = None,
                 repo: Optional[str] = None) -> list:
    """Every extractor, combined: text-based (always available) plus lineage-edge-based (when ``conn`` is given).
    De-duplicated by ``(kind, value)``, first occurrence wins."""
    out = extract_from_text(hits, grammar=grammar, repo=repo)
    out.extend(extract_from_lineage(conn, hits))
    return _dedupe_identifiers(out)
