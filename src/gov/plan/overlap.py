"""Whether two path patterns can name one path, decided one way only (W2-136 S3, DEC-1088 (1)).

The patterns are read as the guard reads a ticket's ``allowed_paths`` (``gov.guard.decide._match_pattern``): ``*``
stays inside one folder, ``**`` crosses folders. A path the guard would let two writers both touch is a path both
patterns match, so:

- a literal path against a pattern is the guard's own matcher, called on it;
- two patterns are compared pattern to pattern, for the paths not yet created as for the tracked ones: there is an
  overlap exactly when some path matches both, which this module decides on the guard's own reading of the two
  patterns (each ``**`` part's ``*`` is ``[^/]*``, the parts joined by ``.*``). A tracked file that matches both is
  one such path, and names the overlap when there is one.
- It errs toward overlap: a literal path is also read as the folder of that name (``src/x`` overlaps ``src/x/**``),
  so a plan can make tickets wait but never lets two writers collide.
"""

from __future__ import annotations

import subprocess
from functools import lru_cache
from pathlib import Path

from gov.guard import decide

_STAR, _DSTAR = object(), object()


@lru_cache(maxsize=None)
def _tokens(pattern: str) -> tuple:
    """The guard's reading of a pattern: characters, ``*`` (no ``/``) and ``**`` (anything)."""
    out: list = []
    for number, part in enumerate(pattern.split("**")):
        if number:
            out.append(_DSTAR)
        out.extend(_STAR if char == "*" else char for char in part)
    return tuple(out)


def _accepts(token, char: str) -> bool:
    return token is _DSTAR or (token is _STAR and char != "/") or token == char


@lru_cache(maxsize=None)
def _intersect(a: str, b: str) -> bool:
    """True when some path matches both patterns (neither literal): a search over the pairs of positions."""
    ta, tb = _tokens(a), _tokens(b)
    seen, todo = set(), [(0, 0)]
    while todo:
        i, j = todo.pop()
        if (i, j) in seen:
            continue
        seen.add((i, j))
        if i == len(ta) and j == len(tb):
            return True
        x = ta[i] if i < len(ta) else None
        y = tb[j] if j < len(tb) else None
        if x is _STAR or x is _DSTAR:
            todo.append((i + 1, j))  # the wildcard matches nothing more
        if y is _STAR or y is _DSTAR:
            todo.append((i, j + 1))
        if isinstance(x, str) and y is not None:  # x's character, taken by y (a wildcard stays where it is)
            if _accepts(y, x):
                todo.append((i + 1, j if y is _STAR or y is _DSTAR else j + 1))
        elif isinstance(y, str) and x is not None:  # y's character, taken by the wildcard x
            if _accepts(x, y):
                todo.append((i, j + 1))
    return False


def _literal(pattern: str) -> bool:
    return "*" not in pattern


def _prefix(pattern: str) -> str:
    return pattern.split("*", 1)[0]


def _readings(pattern: str) -> tuple[str, ...]:
    """The pattern, and for a literal path also the folder of that name (erring toward overlap)."""
    pattern = pattern.strip()
    if _literal(pattern):
        return (pattern, pattern.rstrip("/") + "/**")
    return (pattern,)


def _one(a: str, b: str) -> bool:
    pa, pb = _prefix(a), _prefix(b)
    if not (pa.startswith(pb) or pb.startswith(pa)):
        return False  # the literal heads differ: no path can match both
    if _literal(a) and _literal(b):
        return a == b
    if _literal(a):
        return decide._match_pattern(a, b)
    if _literal(b):
        return decide._match_pattern(b, a)
    return _intersect(a, b)


@lru_cache(maxsize=None)
def patterns_overlap(a: str, b: str) -> bool:
    """True when the guard could let a writer of ``a`` and a writer of ``b`` both touch one path."""
    if not a.strip() or not b.strip():
        return False
    return any(_one(x, y) for x in _readings(a) for y in _readings(b))


class Tracked:
    """The repository's tracked files, listed once per plan and only when an overlap needs naming."""

    def __init__(self, root: Path):
        self.root, self._files = Path(root), None

    @property
    def files(self) -> list[str]:
        if self._files is None:
            self._files = _ls_files(self.root)
        return self._files

    def witness(self, a: str, b: str) -> str:
        """The path that names an overlap of ``a`` and ``b``: a literal one of the two, else the first tracked file
        both match (the guard's matcher), else the narrower pattern."""
        for pattern in (a, b):
            if _literal(pattern):
                return pattern
        for path in self.files:
            if decide._match_pattern(path, a) and decide._match_pattern(path, b):
                return path
        return min((a, b), key=lambda p: (-len(_prefix(p)), p))


def _ls_files(root: Path) -> list[str]:
    from gov.util.gitenv import git_binary, git_env
    git = git_binary()
    if git is None or not (root / ".git").exists():
        return []
    try:
        done = subprocess.run([git, "-C", str(root), "ls-files", "-z"], capture_output=True,
                              env=git_env(root), timeout=60)
    except (OSError, subprocess.SubprocessError):
        return []
    if done.returncode != 0:
        return []
    return sorted(name for name in done.stdout.decode("utf-8", "replace").split("\0") if name)
