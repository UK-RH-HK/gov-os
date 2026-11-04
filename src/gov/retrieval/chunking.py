"""Line-aligned chunking and the parent of each chunk (W1-17; DEC-091, DEC-343).

``chunk_text`` is carried from ``cli/govbridge/core/chunking.py``: a chunk never
splits a line, and the overlap is whole lines. ``parents`` is new: the spans a
file's chunks belong to. A file is chunked parent by parent, so every chunk
lies inside the one parent it names.

- Markdown: a section, from a heading line to the line before the next heading.
- Python: an outermost function (read with ``ast``), from its ``def`` line to its
  last line; every other line belongs to the module, which is the whole file.
- Anything else: the module, which is the whole file.

``CHUNKER_VERSION`` is part of every chunk id and parent id.
"""

from __future__ import annotations

import ast
import hashlib
import re

CHUNKER_VERSION = "gov-chunker/1"
MAX_CHARS = 1200
OVERLAP_CHARS = 120
# Above every chunk the chunker makes (W2-32 S7): a chunk holds at most MAX_CHARS, or one longer line; this
# repository's longest such line is 24,575 characters. The models read less: the embedder up to
# ``semantic.EMBED_LIMIT_CHARS`` (its server's 4,096-token context), the reranker up to ``fusion.RERANK_LIMIT_CHARS``
# (one request's size bound, ``rerank.MAX_REQUEST_CHARS``, DEC-1067 (f)).
READ_CHARS = 32768
# DEC-1068's M5: a decision register entry is one chunk up to this many characters (the embedder's read,
# ``semantic.EMBED_LIMIT_CHARS``, so an entry is embedded whole); a longer entry is split within it at this size.
REGISTER_ENTRY_CHARS = 10_000
_ENTRY = re.compile(r"### DEC-")
_FENCE = re.compile(r"\s*(```|~~~)")
_TOP_HEADING = re.compile(r"#{1,3}\s")  # a register section: an entry ends at the next heading of level 1 to 3
_INNER = re.compile(r"(?:[-*+]|\d+[.)])\s|#{4,6}\s")  # an entry's own boundaries: a top-level item, a sub-heading


def _unfenced(lines: list[str]) -> list[bool]:
    """For each line, whether it stands outside a fenced block (``` or ~~~): a ``#`` line inside one is no heading."""
    out, fence = [], None
    for line in lines:
        mark = _FENCE.match(line)
        if fence is None:
            out.append(not mark)
            if mark:
                fence = mark.group(1)
        else:
            out.append(False)
            if mark and mark.group(1) == fence:
                fence = None
    return out


def register_sections(text: str) -> list[tuple[str, int, int, list[tuple[int, int]]]]:
    """The decision register's parents under M5: its sections at the headings of level 1 to 3 outside fenced blocks,
    so an entry runs from its ``### DEC-`` line to the next such heading and a fenced ``#`` line does not cut it."""
    lines = text.splitlines()
    if not lines:
        return []
    outside = _unfenced(lines)
    starts = sorted({1} | {n for n, line in enumerate(lines, 1) if outside[n - 1] and _TOP_HEADING.match(line)})
    ends = [s - 1 for s in starts[1:]] + [len(lines)]
    return [("section", start, end, [(start, end)]) for start, end in zip(starts, ends)]


def entry_parts(lines: list[str], first: int, last: int, limit: int = REGISTER_ENTRY_CHARS) -> list[tuple[int, int]]:
    """An entry's lines ``first`` to ``last`` (1-based) as its chunks: the whole entry when it holds at most ``limit``
    characters; else parts cut at its own boundaries (a top-level list item, a sub-heading, outside fenced blocks),
    packed in order, each at most ``limit``, no overlap; a piece still above it is cut by lines at that size."""
    body = lines[first - 1:last]
    if sum(map(len, body)) <= limit:
        return [(first, last)]
    outside = _unfenced(body)
    cuts = [first] + [first + i for i, line in enumerate(body) if i and outside[i] and _INNER.match(line)]
    pieces = [(a, b - 1) for a, b in zip(cuts, cuts[1:] + [last + 1])]
    parts, start, size = [], None, 0
    for a, b in pieces:
        chars = sum(len(line) for line in lines[a - 1:b])
        if chars > limit:  # one piece above the limit: by lines, at the limit
            if start is not None:
                parts.append((start, a - 1))
                start, size = None, 0
            parts += [(a + f - 1, a + l - 1) for f, l, _ in
                      chunk_text("".join(lines[a - 1:b]), max_chars=limit, overlap_chars=0)]
            continue
        if start is not None and size + chars > limit:
            parts.append((start, a - 1))
            start, size = None, 0
        if start is None:
            start = a
        size += chars
    if start is not None:
        parts.append((start, last))
    return parts
_HEADING = re.compile(r"#{1,6}\s")


def chunk_text(text: str, max_chars: int = MAX_CHARS, overlap_chars: int = OVERLAP_CHARS) -> list[tuple[int, int, str]]:
    """``(start_line, end_line, text)`` of each chunk of ``text``; lines are 1-based and inclusive.

    A chunk holds at most ``max_chars`` characters, but never less than one line; ``overlap_chars`` of trailing
    context are carried into the next chunk, in whole lines.
    """
    lines = text.splitlines(keepends=True)
    chunks, start = [], 0
    while start < len(lines):
        chars, end = 0, start
        while end < len(lines) and (end == start or chars + len(lines[end]) <= max_chars):
            chars += len(lines[end])
            end += 1
        chunks.append((start + 1, end, "".join(lines[start:end])))
        if end >= len(lines):
            break
        back_chars, back = 0, end
        while back > start and back_chars < overlap_chars:
            back -= 1
            back_chars += len(lines[back])
        start = back if back > start else end  # always forward, even when one line is longer than the overlap
    return chunks


def make_id(*parts) -> str:
    """The id of a chunk or a parent: the same parts give the same id in every build."""
    return hashlib.sha256("\0".join(str(part) for part in (CHUNKER_VERSION, *parts)).encode("utf-8")).hexdigest()[:24]


def _functions(text: str) -> list[tuple[int, int]]:
    """``(def line, last line)`` of every outermost function of the Python source ``text``."""
    try:
        tree = ast.parse(text)
    except (SyntaxError, ValueError):
        return []
    spans = sorted((node.lineno, node.end_lineno) for node in ast.walk(tree)
                   if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)))
    outer: list[tuple[int, int]] = []
    for start, end in spans:
        if not outer or start > outer[-1][1]:
            outer.append((start, end))
    return outer


def parents(path: str, text: str) -> list[tuple[str, int, int, list[tuple[int, int]]]]:
    """``(kind, start_line, end_line, runs)`` of each parent of the file; ``runs`` are the line spans chunked under it."""
    lines = text.splitlines()
    count = len(lines)
    if count == 0:
        return []
    if path.endswith((".md", ".markdown")):
        starts = sorted({1} | {number for number, line in enumerate(lines, 1) if _HEADING.match(line)})
        return [("section", start, end, [(start, end)]) for start, end in zip(starts, [s - 1 for s in starts[1:]] + [count])]
    functions = _functions(text) if path.endswith(".py") else []
    runs, at = [], 1
    for start, end in functions:
        if start > at:
            runs.append((at, start - 1))
        at = end + 1
    if at <= count:
        runs.append((at, count))
    return [("module", 1, count, runs)] + [("function", start, end, [(start, end)]) for start, end in functions]


def definitions(text: str) -> list[int]:
    """The ``def`` or ``class`` line of each top-level function and class of the Python source ``text``, and of each
    method of a top-level class, in order (DEC-1068's M2); none when it does not parse."""
    try:
        tree = ast.parse(text)
    except (SyntaxError, ValueError):
        return []
    kinds = (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)
    starts = {node.lineno for node in tree.body if isinstance(node, kinds)}
    for node in tree.body:
        if isinstance(node, ast.ClassDef):
            starts |= {item.lineno for item in node.body if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef))}
    return sorted(starts)


def cut_at(runs: list[tuple[int, int]], starts: list[int]) -> list[tuple[int, int]]:
    """``runs`` cut before each line of ``starts`` inside one, so no run holds the start of two definitions."""
    out = []
    for first, last in runs:
        at = first
        for start in starts:
            if at < start <= last:
                out.append((at, start - 1))
                at = start
        out.append((at, last))
    return out


_DEF = re.compile(r"\s*(?:async\s+)?def\s+(\w+)")


def _heading(line: str) -> tuple[int, str] | None:
    """A Markdown heading line's level and text (its marks and a closing run of ``#`` taken off), or None."""
    if not _HEADING.match(line):
        return None
    marks = len(line) - len(line.lstrip("#"))
    return marks, re.sub(r"\s+#+\s*$", "", line[marks:]).strip()


def headers(path: str, firsts: list[tuple[str, str, int, str]]) -> dict[str, str]:
    """The contextual header of each parent of the file at ``path`` (DEC-1067 order (5), index-time method 1), from
    ``(parent_id, kind, start_line, first line)`` of its parents, the first line read from the parent's first chunk.

    - Markdown: ``[path: <path>]`` and ``[section: <title> > <heading> > ...]``, the headings that contain the section,
      outermost first, by their levels, the section's own last; a part before the first heading has none.
    - Python: ``[path: <path>]`` and, for a function the chunker made a parent of, ``[function: <name>]``. The chunker
      knows no class, so a method is named as its function; the module's own lines have the path alone.
    - Anything else, and a parent not given: the path alone. Each line ends in a newline, so the header is followed
      by the chunk's text as it stands."""
    trail: list[tuple[int, str]] = []
    named: dict[str, str] = {}
    for parent_id, kind, _, line in sorted(firsts, key=lambda row: row[2]):
        extra = ""
        if kind == "section":
            found = _heading(line)
            if found:
                while trail and trail[-1][0] >= found[0]:
                    trail.pop()
                trail.append(found)
            extra = f"[section: {' > '.join(text for _, text in trail)}]\n" if trail else ""
        elif kind == "function" and (match := _DEF.match(line)):
            extra = f"[function: {match.group(1)}]\n"
        named[parent_id] = header(path) + extra
    return named


def header(path: str) -> str:
    """The header's first line, all a parent without headings gets."""
    return f"[path: {path}]\n"


def chunk_file(path: str, blob: str, text: str, recipe: dict | None = None, register: str | None = None):
    """``(parent rows, chunk rows)`` of one file.

    A parent row is ``(parent_id, path, kind, start_line, end_line)``; a chunk row is
    ``(chunk_id, path, start_line, end_line, parent_id, text)``.

    ``recipe`` holds DEC-1068's index-time methods that are on (absent or all off: today's chunks, byte for byte).
    ``chunk_code_by_definition`` (M2): a Python file's runs are also cut at each top-level def/class and method
    (``definitions``), so no chunk holds the start of two definitions; the parents are kept as they are.
    ``chunk_register_by_entry`` (M5, P-W2-32-11): in the decision register (``register``, the path map's
    ``decision_register``), the parents are ``register_sections`` (headings outside fenced blocks), and each
    ``### DEC-`` entry is one chunk when it and its contextual header (``headers``, as the embedder adds it) hold at
    most ``REGISTER_ENTRY_CHARS``, else split at its own boundaries (``entry_parts``) into parts that each fit with the
    header (review S7-F1), never across two entries; the same chunks whether ``embed_headers`` is on or off; the
    register's other sections are chunked as before; every other file as before.
    """
    recipe = recipe or {}
    lines = text.splitlines(keepends=True)
    starts = definitions(text) if recipe.get("chunk_code_by_definition") and path.endswith(".py") else []
    by_entry = bool(recipe.get("chunk_register_by_entry")) and register is not None and path == register
    parent_rows, chunk_rows = [], []
    sections = register_sections(text) if by_entry else parents(path, text)
    room = {}
    if by_entry:  # review S7-F1: an entry and its contextual header fit the embedder's read together
        ids = [make_id("parent", path, blob, kind, start, end) for kind, start, end, _ in sections]
        named = headers(path, [(pid, kind, start, lines[start - 1]) for pid, (kind, start, _, _) in zip(ids, sections)])
        room = {pid: REGISTER_ENTRY_CHARS - len(named.get(pid, header(path))) for pid in ids}
    for kind, start, end, runs in sections:
        runs = cut_at(runs, starts) if starts else runs
        parent_id = make_id("parent", path, blob, kind, start, end)
        parent_rows.append((parent_id, path, kind, start, end))
        if by_entry and _ENTRY.match(lines[start - 1]):  # an entry: one chunk, or its parts at its own boundaries
            for first, last in entry_parts(lines, start, end, room[parent_id]):
                chunk = "".join(lines[first - 1:last])
                chunk_rows.append((make_id("chunk", path, blob, first, last), path, first, last, parent_id, chunk))
            continue
        for run_start, run_end in runs:
            for first, last, chunk in chunk_text("".join(lines[run_start - 1:run_end])):
                first, last = first + run_start - 1, last + run_start - 1
                chunk_rows.append((make_id("chunk", path, blob, first, last), path, first, last, parent_id, chunk))
    return parent_rows, chunk_rows
