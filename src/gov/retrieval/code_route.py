"""The code route of a plain question: the symbols it names, their callers and callees (W2-92; DEC-957, CAP-12).

``route`` asks the code index for each word of the question that names a function, method or class: a word shaped
as code (``_CODE_SHAPED``: in backticks, called, or with an underscore or a capital inside it), or a plain word that
a code file of the store, no test, defines (``def`` or ``class``). It asks with the code-graph tool's own traversal
(DEC-859): ``search_graph`` for the definitions, then for each a targeted ``query_graph`` of the CALLS edges into
and out of that one qualified name, which gives the callers' and callees' files and lines in one answer. Every
answer is a small page (``PAGE`` rows, far under the tool's cap), followed by its continuation; nothing loads the
whole graph. A span is a file of the index's staged copy, given back as the repository's path, and joins the fusion
as the store's lexical chunks that cover it. As the tool's ``trace_path`` does by default, test files are left out.

A question whose plain words no code file defines asks nothing of the index, and its daemon is not started: no
route and no facet, today's bundle. A missing or unreadable code index gives the facet unavailable with its reason,
and no hit, for a question that names a symbol. The other routes still answer (DEC-957, DEC-860).
Everything is sorted. It only reads: it builds no index.
"""

from __future__ import annotations

import re
from pathlib import Path

from gov import codeintel

FACET = "code"
PAGE = 50  # rows of one answer of the tool: a small page, far under its cap of 500 (search) and 5000 (query)
_SYMBOLS = {"Function", "Method", "Class"}
_TRACED = {"Function", "Method"}
_WORD = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")
# A word that names a symbol by its form: in backticks, called, or with an underscore or a capital inside it.
_CODE_SHAPED = re.compile(r"`[^`\s]+`|\b[A-Za-z_]\w*\(|\b\w*_\w+|\b\w*[a-z0-9][A-Z]\w*")
_CODE_FILES = (".py",)
_NEIGHBOURS = ("MATCH (a)-[:CALLS]->(b) WHERE {near}.qualified_name = '{qualified}' "
               "RETURN {far}.qualified_name, {far}.label, {far}.file_path, {far}.start_line, {far}.end_line")


def _test_file(path: str) -> bool:
    parts = path.split("/")
    return any(part in ("tests", "test") for part in parts[:-1]) or parts[-1].startswith("test_")


def _repo_path(root: Path, file: str) -> str:
    """A file of the index, as the repository's path: the tool's paths are under the staged copy, or relative to it."""
    staged = str(Path(root) / codeintel.BASE_REL / "files") + "/"
    return file[len(staged):] if file.startswith(staged) else file


def _defined(root: Path, words: set[str], chunks: dict[str, dict]) -> set[str]:
    """The ``words`` that a code file of the store, no test, defines as a function, method or class."""
    if not words:
        return set()
    pattern = re.compile(rf"^[ \t]*(?:async[ \t]+)?(?:def|class)[ \t]+({'|'.join(sorted(words))})\b", re.M)
    defined = set()
    for path in sorted({chunk["path"] for chunk in chunks.values()}):
        if path.endswith(_CODE_FILES) and not _test_file(path):
            try:
                defined |= set(pattern.findall((Path(root) / path).read_text(encoding="utf-8", errors="replace")))
            except OSError:
                continue
    return defined


def _search(session, **args) -> list[tuple[str, str, str, str]]:
    """``(qualified name, name, label, file and lines)`` of every row ``search_graph`` finds, page by page."""
    rows, offset = [], 0
    while True:
        page = session.tool("search_graph", project=codeintel.PROJECT, format="json", limit=PAGE, offset=offset,
                            **args)
        for group in page.get("groups", []):
            prefix = group.get("qn_prefix", "")
            for name, label, lines, *_ in group["rows"]:
                rows.append((f"{prefix}.{name}" if prefix else name, name, label, group.get("file", ""), lines))
        if not page.get("has_more") or page.get("next_offset", offset) <= offset:
            return rows
        offset = page["next_offset"]


def _near(session, qualified: str) -> set[tuple[str, str, str, str]]:
    """``(qualified name, label, file, first-last)`` of the callers and callees of ``qualified``, page by page."""
    near = set()
    for side, far in (("b", "a"), ("a", "b")):  # the edges into it: its callers; out of it: its callees
        query, offset = _NEIGHBOURS.format(near=side, far=far, qualified=qualified), 0
        while True:
            page = session.tool("query_graph", project=codeintel.PROJECT, format="json", query=query, max_rows=PAGE,
                                offset=offset)
            near |= {(name, label, file, f"{first}-{last}") for name, label, file, first, last in page["rows"]}
            offset += len(page["rows"])
            if not page.get("has_more") or not page["rows"]:
                break
    return near


def _spans(root: Path, words: list[str]) -> list[tuple[str, int, int]]:
    """The spans of the symbols named ``words``, then of their callers and callees, sorted within each."""
    with codeintel._Session(Path(root).resolve()) as session:
        found = _search(session, name_pattern=f"^({'|'.join(words)})$")
        named = sorted({row for row in found if row[1] in words and row[2] in _SYMBOLS and not _test_file(row[3])})
        near = set()
        for qualified, _, label, _, _ in named:
            if label in _TRACED:
                near |= _near(session, qualified)
    named_keys = {row[0] for row in named}
    others = sorted(row for row in near if row[0] not in named_keys and row[1] in _SYMBOLS and not _test_file(row[2]))
    spans = []
    for file, lines in [(row[3], row[4]) for row in named] + [(row[2], row[3]) for row in others]:
        first, _, last = str(lines).partition("-")
        if first.isdigit() and int(first) > 0:
            spans.append((_repo_path(root, file), int(first), int(last or first)))
    return list(dict.fromkeys(spans))


def route(root: Path, query: str, chunks: dict[str, dict]) -> tuple[list[dict], dict] | None:
    """The code route's hits (chunks of ``chunks``) and its facet, or None when ``query`` names no symbol."""
    shaped = {word for form in _CODE_SHAPED.findall(query) for word in _WORD.findall(form)}
    words = sorted(shaped | _defined(root, set(_WORD.findall(query)) - shaped, chunks))
    if not words:  # no word names a symbol: the index is not asked, today's bundle
        return None
    index, spans, reason = Path(root) / codeintel.BASE_REL, [], None
    if not (index / "home").is_dir() or not (index / "files").is_dir():
        reason = f"the code index is missing: no {codeintel.BASE_REL}/home and {codeintel.BASE_REL}/files to ask"
    else:
        try:
            spans = _spans(root, words)
        except (RuntimeError, OSError, LookupError, TypeError, ValueError) as error:
            reason = f"the code index is unreadable: {codeintel.TOOL} did not answer ({error})"
    if reason is not None:
        return [], {"available": False, "reason": reason}
    if not spans:
        return None
    by_path: dict[str, list[dict]] = {}
    for chunk in chunks.values():
        by_path.setdefault(chunk["path"], []).append(chunk)
    hits = {}
    for path, first, last in spans:
        for chunk in sorted(by_path.get(path, []), key=lambda chunk: (chunk["start_line"], chunk["end_line"])):
            if chunk["start_line"] <= last and chunk["end_line"] >= first:
                hits.setdefault(chunk["chunk_id"], chunk)
    return list(hits.values()), {"available": True, "reason": None}
