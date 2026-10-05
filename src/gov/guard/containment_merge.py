"""The one place that reads a merge commit (W1-50; DEC-394, DEC-398,
DEC-403).

The containment check uses ``read_merge`` for a merge commit's own
change, and the approval check reads merges the same way.  What cannot
be read raises ``MergeReadError``.
"""

from __future__ import annotations

import re
from itertools import combinations
from typing import NamedTuple

from gov.guard.containment import _GitError, _NotARepo, _git

_COMMIT_ID = re.compile(r"[0-9a-f]{40}|[0-9a-f]{64}")


class MergeReadError(ValueError):
    """``read_merge`` cannot read the merge: the ``commit`` argument is
    not a full commit id, the commit is not a merge commit, or the
    repository, a parent, a merge base or a tree cannot be read."""


class MergeReading(NamedTuple):
    own: list      # paths the merge commit changed itself, sorted
    brought: list  # paths another parent brought, sorted


def _run(root: str, *args: str, ok: tuple = (0,)) -> str:
    try:
        return _git(root, *args, ok=ok)
    except (_GitError, _NotARepo) as e:
        raise MergeReadError(str(e) or "git failed") from e


def _changed(root: str, a: str, b: str) -> set:
    """The paths whose content, mode or presence differs between two
    commits' trees, without rename detection."""
    return {p for p in _run(
        root, "diff-tree", "-r", "-z", "--name-only", "--no-renames",
        "--ignore-submodules=none", a, b).split("\0") if p}


def read_merge(root: str, commit: str) -> MergeReading:
    """Which paths the merge commit *commit* of the repository at *root*
    changed itself, and which another parent brought.

    *commit* is a full commit id in lower-case hexadecimal.  ``own`` and
    ``brought`` are sorted lists of repository-relative paths, without
    rename detection: both ends of a rename are two paths, and a deleted
    path is a path.  They are disjoint.

    The rule (DEC-394 DP-18, as amended by DEC-398 and widened to every
    parent by DEC-403): a parent brings a path against another parent
    only when the merge commit holds its content of the path and that
    content differs from the one merge base of the two parents.  Content
    includes the mode, and absence.

    ``own`` holds every path where the merge commit's content differs
    from a parent's, the first or any other, and no other parent brought
    it against that parent.  So it holds what the merge commit changes
    beyond its parents and also the paths where it drops a parent's
    change.

    ``brought`` holds the paths where the merge commit's content differs
    from its first parent's and another parent brought it against the
    first parent, less the paths in ``own``.  It does not hold what the
    first parent brought against another parent.

    Fail closed: when the first parent and any one of the other parents
    have several merge bases (a criss-cross history) or none (unrelated
    histories), nothing counts as brought by any parent: ``own`` is
    every path where the merge commit differs from any parent and
    ``brought`` is empty.  Two parents other than the first that have
    several merge bases, or none, bring nothing against each other; the
    rest of such an octopus merge is read parent by parent.

    Raises ``MergeReadError`` (a ``ValueError``), before git is started,
    for a *commit* that is not a full commit id, so no argument is ever
    read by git as an option; and for a commit that is not a merge
    commit, and where the repository, a parent, a merge base or a tree
    cannot be read.

    The answer depends on the repository's real objects only: no caller,
    role or ticket, and no replacement ref, graft, shallow file,
    commit-graph or inherited ``GIT_DIR`` (the check's own git calls).
    For a merge commit with n parents at most 1 + n + 3n(n-1)/2 git
    processes (six for two parents), whatever the number of paths.
    """
    if not isinstance(commit, str) or not _COMMIT_ID.fullmatch(commit):
        raise MergeReadError(f"{commit!r} is not a commit id")
    ids = _run(root, "rev-list", "--no-walk", "--parents", commit).split()
    if len(ids) < 3:
        raise MergeReadError(f"{commit} is not a merge commit")
    parents = list(dict.fromkeys(ids[1:]))
    first = parents[0]
    differs = {p: _changed(root, p, ids[0]) for p in parents}
    # For each parent, the paths another parent brought against it.
    brought = {p: set() for p in parents}
    # The pairs with the first parent come first.
    for a, b in combinations(parents, 2):
        # Exit code 1 with no output: no merge base.
        bases = _run(root, "merge-base", "--all", a, b, ok=(0, 1)).split()
        if len(bases) == 1:
            brought[a] |= _changed(root, bases[0], b) - differs[b]
            brought[b] |= _changed(root, bases[0], a) - differs[a]
        elif a == first:
            return MergeReading(sorted(set().union(*differs.values())), [])
    own = set().union(*(differs[p] - brought[p] for p in parents))
    return MergeReading(
        sorted(own), sorted(differs[first] & brought[first] - own))
