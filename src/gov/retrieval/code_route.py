"""The code route of a plain question: the symbols it names, their callers and callees (W2-92; DEC-957, CAP-12).

``route`` asks the code index for each word of the question shaped as code (``_CODE_SHAPED``: in backticks, called,
or with an underscore or a capital inside it) that is the name of a function, method or class there, with the
code-graph tool's own traversal (DEC-859): ``search_graph`` for the definitions, ``trace_path`` one hop both
ways for the callers and callees, ``search_graph`` by qualified name for their spans. Every answer is a small page
(``PAGE`` rows, far under the tool's cap), followed by its continuation; nothing loads the whole graph. A span is a
file of the index's staged copy, given back as the repository's path, and joins the fusion as the store's lexical
chunks that cover it. As the tool's ``trace_path`` does by default, test files are left out.

A question of plain words asks nothing of the index: a plain word that happens to name a symbol (``close``, ``load``)
is no question about code, and a search for every word is no targeted answer. A question that names no symbol gives
no route and no facet: today's bundle. A missing or unreadable code index gives the facet unavailable with its
reason, and no hit, for a question with a word shaped as code. The other routes still answer (DEC-957, DEC-860).
Everything is sorted. It only reads: it builds no index.
"""

from __future__ import annotations

import re
from pathlib import Path

from gov import codeintel

FACET = "code"
PAGE = 50  # rows of one answer of the tool: a small page, far under its cap of 500 (search) and 5000 (trace)
_SYMBOLS = {"Function", "Method", "Class"}
_TRACED = {"Function", "Method"}
_WORD = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")
# A word that names a symbol by its form: in backticks, called, or with an underscore or a capital inside it.
_CODE_SHAPED = re.compile(r"`[^`\s]+`|\b[A-Za-z_]\w*\(|\b\w*_\w+|\b\w*[a-z0-9][A-Z]\w*")
_QNS = 20  # qualified names asked of search_graph at once


def _test_file(path: str) -> bool:
    parts = path.split("/")
    return any(part in ("tests", "test") for part in parts[:-1]) or parts[-1].startswith("test_")


def _repo_path(root: Path, file: str) -> str:
    """A file of the index, as the repository's path: the tool's paths are under the staged copy, or relative to it."""
    staged = str(Path(root) / codeintel.BASE_REL / "files") + "/"
    return file[len(staged):] if file.startswith(staged) else file


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


def _near(session, qualified: str) -> set[str]:
    """The qualified names of the callers and callees of ``qualified``, one hop, page by page."""
    near, cursor = set(), None
    while True:
        page = session.tool("trace_path", project=codeintel.PROJECT, function_name=qualified, direction="both",
                            depth=1, format="json", limit=PAGE, **({"cursor": cursor} if cursor else {}))
        for side in ("callers", "callees"):
            for group in (page.get(side) or {}).get("groups", []):
                prefix = group.get("qn_prefix", "")
                near |= {f"{prefix}.{row[0]}" if prefix else row[0] for row in group["rows"]}
        cursor = page.get("next_cursor")
        if not page.get("has_more") or not cursor:
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
        near -= {row[0] for row in named}
        listed, others = sorted(near), []
        for start in range(0, len(listed), _QNS):
            batch = [name.replace(".", r"\.") for name in listed[start:start + _QNS]]
            others += [row for row in _search(session, qn_pattern=f"^({'|'.join(batch)})$")
                       if row[0] in near and not _test_file(row[3])]
    spans = []
    for rows in (named, sorted(set(others))):
        for _, _, _, file, lines in rows:
            first, _, last = str(lines).partition("-")
            if first.isdigit():
                spans.append((_repo_path(root, file), int(first), int(last or first)))
    return list(dict.fromkeys(spans))


def route(root: Path, query: str, chunks: dict[str, dict]) -> tuple[list[dict], dict] | None:
    """The code route's hits (chunks of ``chunks``) and its facet, or None when ``query`` names no symbol."""
    words = sorted({word for shaped in _CODE_SHAPED.findall(query) for word in _WORD.findall(shaped)})
    if not words:  # a question of plain words asks nothing of the index: today's bundle
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
