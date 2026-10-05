"""The one place that reads a merge commit (W1-50; DEC-394, DEC-398).

The containment check uses ``read_merge`` for a merge commit's own
change, and the approval check reads merges the same way.
"""

from __future__ import annotations

from typing import NamedTuple

from gov.guard.containment import _git


class MergeReading(NamedTuple):
    own: list      # paths the merge commit changed itself, sorted
    brought: list  # paths another parent brought, sorted


def _changed(root: str, a: str, b: str) -> set:
    """The paths whose content, mode or presence differs between two
    commits' trees, without rename detection."""
    return {p for p in _git(
        root, "diff-tree", "-r", "-z", "--name-only", "--no-renames",
        "--ignore-submodules=none", a, b).split("\0") if p}


def read_merge(root: str, commit: str) -> MergeReading:
    """Which paths the merge commit *commit* of the repository at *root*
    changed itself, and which another parent brought.

    ``own`` and ``brought`` are sorted lists of repository-relative
    paths.  They are disjoint and together are exactly the paths the
    merge commit changes against its first parent, without rename
    detection: both ends of a rename are two paths, and a deleted path
    is a path.

    The rule (DEC-394 DP-18, as amended by DEC-398): a path is brought
    by another parent only when the merge commit holds that parent's
    content of the path and that parent's content of the path differs
    from the merge base of the first parent and that parent.  Content
    includes the mode, and absence.  Every other path is the merge
    commit's own change.

    Fail closed: when the first parent and any one of the other parents
    have several merge bases (a criss-cross history) or none (unrelated
    histories), nothing counts as brought by any parent: every path the
    merge commit changes against its first parent is its own, whatever
    the parents hold.

    A commit that is not a merge commit raises ``ValueError``.  Where a
    parent, a merge base or a tree cannot be read, the git call raises.

    The answer depends on the repository's real objects only: no caller,
    role or ticket, and no replacement ref, graft, shallow file,
    commit-graph or inherited ``GIT_DIR`` (the check's own git calls).
    Two git processes for the merge commit and three for each parent
    after the first, whatever the number of paths.
    """
    ids = _git(root, "rev-list", "--no-walk", "--parents", commit).split()
    if len(ids) < 3:
        raise ValueError(f"{commit} is not a merge commit")
    first, others = ids[1], ids[2:]
    changed = _changed(root, first, ids[0])
    brought: set = set()
    for other in others:
        # Exit code 1 with no output: no merge base.
        bases = _git(root, "merge-base", "--all", first, other,
                     ok=(0, 1)).split()
        if len(bases) != 1:
            return MergeReading(sorted(changed), [])
        brought |= (_changed(root, bases[0], other)
                    - _changed(root, other, ids[0]))
    return MergeReading(sorted(changed - brought), sorted(changed & brought))
