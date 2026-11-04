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
# What the reranker reads of a chunk (W2-32 S7, DEC-1066 G1, DEC-1067): above every chunk the chunker makes, so each
# is read whole. A chunk holds at most MAX_CHARS, or one longer line; this repository's longest such line is 24,575
# characters. The embedder reads less, ``semantic.EMBED_LIMIT_CHARS``, its server's context being 4,096 tokens.
READ_CHARS = 32768
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


def chunk_file(path: str, blob: str, text: str):
    """``(parent rows, chunk rows)`` of one file.

    A parent row is ``(parent_id, path, kind, start_line, end_line)``; a chunk row is
    ``(chunk_id, path, start_line, end_line, parent_id, text)``.
    """
    lines = text.splitlines(keepends=True)
    parent_rows, chunk_rows = [], []
    for kind, start, end, runs in parents(path, text):
        parent_id = make_id("parent", path, blob, kind, start, end)
        parent_rows.append((parent_id, path, kind, start, end))
        for run_start, run_end in runs:
            for first, last, chunk in chunk_text("".join(lines[run_start - 1:run_end])):
                first, last = first + run_start - 1, last + run_start - 1
                chunk_rows.append((make_id("chunk", path, blob, first, last), path, first, last, parent_id, chunk))
    return parent_rows, chunk_rows
