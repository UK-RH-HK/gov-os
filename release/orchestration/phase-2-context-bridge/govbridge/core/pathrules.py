"""Generic path-glob matching shared by corpus classification (corpus.py) and canonical-view partitioning
(view.py). Repository path names are always the SUBJECT of a match; they are never interpolated into a pattern
(ARCHITECTURE.md section 1.1)."""
from __future__ import annotations

import fnmatch
from typing import Iterable


def glob_match(path: str, pattern: str) -> bool:
    """True if ``path`` matches ``pattern``. A leading ``**/`` also matches at the top level (so ``**/target/**``
    matches ``target/foo`` as well as ``a/target/foo``), the same convention the architect's spike used."""
    if fnmatch.fnmatchcase(path, pattern):
        return True
    if pattern.startswith("**/") and fnmatch.fnmatchcase(path, pattern[3:]):
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
