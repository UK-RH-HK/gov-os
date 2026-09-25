"""Generic path-glob matching shared by corpus classification (corpus.py) and canonical-view partitioning
(view.py). Repository path names are always the SUBJECT of a match; they are never interpolated into a pattern
(ARCHITECTURE.md section 1.1)."""
from __future__ import annotations

import fnmatch
import re
from typing import Iterable

_BRACE_RE = re.compile(r"^(?P<pre>[^{}]*)\{(?P<alts>[^{}]+)\}(?P<post>[^{}]*)$")


def expand_braces(pattern: str) -> list[str]:
    """Expand one shell-style ``{a,b,c}`` alternation group in ``pattern`` into a list of plain glob patterns, one
    per alternative. A pattern with no ``{...}`` group is returned unchanged as a single-element list. Handles at
    most one group (nested/multiple groups are not a seeded need anywhere in this domain's config); a pattern with
    more than one group is returned unchanged (its first group is left literal) rather than mis-expanded. This is
    the central fix for the gap B5 (BR-AR-0007) found and worked around locally in
    ``govbridge.authority.registry.expand_braces``: any glob consumer -- corpus rules, canonical-view partitions,
    the authority registry -- gets brace alternation through this one function now."""
    m = _BRACE_RE.match(pattern)
    if not m:
        return [pattern]
    pre, alts, post = m.group("pre"), m.group("alts"), m.group("post")
    return [f"{pre}{alt}{post}" for alt in alts.split(",")]


def glob_match(path: str, pattern: str) -> bool:
    """True if ``path`` matches ``pattern``. A leading ``**/`` also matches at the top level (so ``**/target/**``
    matches ``target/foo`` as well as ``a/target/foo``), the same convention the architect's spike used. ``pattern``
    may contain one shell-style ``{a,b,c}`` alternation group (expanded via ``expand_braces``); any match among the
    alternatives matches."""
    for alt in expand_braces(pattern):
        if fnmatch.fnmatchcase(path, alt):
            return True
        if alt.startswith("**/") and fnmatch.fnmatchcase(path, alt[3:]):
            return True
    return False


def any_glob_match(path: str, patterns: Iterable[str]) -> str | None:
    """The first pattern in ``patterns`` that matches ``path``, or None."""
    for p in patterns:
        if glob_match(path, p):
            return p
    return None


def top_level_dir_match(path: str, names: Iterable[str]) -> str | None:
    """The first name in ``names`` such that ``path`` is that exact root-level file, or lies under that top-level
    directory. Used for the product-code partition (a list of directory/file names, not globs)."""
    for name in names:
        if path == name or path.startswith(name + "/"):
            return name
    return None
