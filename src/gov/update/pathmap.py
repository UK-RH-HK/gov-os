"""The path map line for the update records (W2-17 fix F6, G3 run of 2026-11-22).

``gov update`` writes ``governance/updates/<version>.json`` (and ``governance/updates/<version>/release/...``). The path
map of an adopted repository, ``governance/project/path-map.yaml``, is the project's own file (the update never writes
an existing file under ``governance/project/``), and one adopted by an earlier kit does not classify those paths, so
``gov doctor``'s ``path_map`` part failed after the update. ``merge`` adds the line ``governance/updates/**`` to such a
path map as a merge: textually, so that every other line, comment and blank line stays as it is, in its order. It never
refuses and never conflicts: a path map it cannot read, or whose edit it cannot verify, is left as it is.
"""

from __future__ import annotations

import re

import yaml

from gov.util.patterns import _match_pattern

REL = "governance/project/path-map.yaml"
PATTERN = "governance/updates/**"
# The two kinds of path the update writes: the record, and the aside copies of the release's files.
SAMPLES = ("governance/updates/0.0.0.json", "governance/updates/0.0.0/release/x")
ANCHOR = re.compile(r"^(?P<indent>[ \t]*)-[ \t]+(?P<quote>[\"']?)governance/project/\*\*(?P=quote)[ \t]*(#.*)?$")
NAMESPACES = re.compile(r"^namespaces[ \t]*:[ \t]*(#.*)?$")


def _patterns(text: str) -> list[str] | None:
    """Every path pattern of every namespace; ``None`` where the text is not a path map with a namespaces map."""
    try:
        data = yaml.safe_load(text)
    except yaml.YAMLError:
        return None
    spaces = data.get("namespaces") if isinstance(data, dict) else None
    if not isinstance(spaces, dict):
        return None
    return [path for space in spaces.values() if isinstance(space, dict) and isinstance(space.get("paths"), list)
            for path in space["paths"] if isinstance(path, str)]


def classified(text: str) -> bool:
    """True where a pattern of the path map holds both kinds of update path."""
    found = _patterns(text) or []
    return all(any(_match_pattern(sample, pattern) for pattern in found) for sample in SAMPLES)


def _eol(lines: list[str]) -> str:
    return "\r\n" if lines and lines[0].endswith("\r\n") else "\n"


def _insert(lines: list[str], at: int, new: list[str]) -> list[str]:
    before = list(lines)
    if at and not before[at - 1].endswith("\n"):
        before[at - 1] += _eol(lines)
    return before[:at] + new + before[at:]


def _after_anchor(lines: list[str]) -> list[str] | None:
    eol = _eol(lines)
    for index, line in enumerate(lines):
        found = ANCHOR.match(line.rstrip("\r\n"))
        if found:
            item = f"{found['indent']}- {found['quote']}{PATTERN}{found['quote']}{eol}"
            return _insert(lines, index + 1, [item])
    return None


def _as_namespace(lines: list[str]) -> list[str] | None:
    """A namespace of its own at the end of the ``namespaces`` map, where no ``governance/project/**`` line anchors."""
    eol = _eol(lines)
    start = next((i for i, line in enumerate(lines) if NAMESPACES.match(line.rstrip("\r\n"))), None)
    if start is None:
        return None
    indent, end = None, start + 1
    for index in range(start + 1, len(lines)):
        text = lines[index].rstrip("\r\n")
        if not text.strip() or text.lstrip().startswith("#"):
            continue
        width = len(text) - len(text.lstrip())
        if width == 0:
            break
        indent = indent if indent is not None else text[:width]
        end = index + 1
    if indent is None:
        return None
    block = [f"{indent}updates:{eol}", f"{indent}{indent}paths:{eol}", f"{indent}{indent}{indent}- {PATTERN}{eol}"]
    return _insert(lines, end, block)


def merge(text: str) -> str | None:
    """The path map's text with ``governance/updates/**`` added, every other line as it was; ``None`` where there is
    nothing to add (the update paths are classified already) or no safe edit (the text is not a path map)."""
    if _patterns(text) is None or classified(text):
        return None
    lines = text.splitlines(keepends=True)
    for edit in (_after_anchor, _as_namespace):
        merged = edit(lines)
        if merged is None:
            continue
        result = "".join(merged)
        found = _patterns(result)
        if found is not None and found.count(PATTERN) == 1 and classified(result) and all(
                line in merged for line in lines if line.endswith("\n")):
            return result
    return None
