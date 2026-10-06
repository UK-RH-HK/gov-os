"""Support code for the eleventh batch of the W1-50 acceptance tests: a move of very many merge commits.

Review finding, DEC-410. DP-28 bounds one merge commit: the helper refuses a merge commit with more than 24
distinct parents, so one merge commit cannot stop the post-command hook. Nothing bounds the move as a whole.
This module builds the three histories of that batch:

- a chain of very many merge commits with 24 parents each, the most DP-28 lets the helper read, one of which
  drops a test designer's change under ``tests/acceptance/**``;
- an ordinary move of 60 two-parent ``--no-ff`` merge commits, each bringing one commit that is inside the
  paths of its own trailers;
- an ordinary move of three octopus merges of eight branches each, made with ``git merge``.

Every history is a real one, made in the throw-away project. The commits a shape needs in large numbers are
made by plumbing (``git commit-tree``, ``git hash-object``, a temporary index), so that a fixture takes a few
seconds. Each ``assert_*`` guard shows, from git's own answers and in a handful of git calls, that the history
a test built is the one its expectation describes. No guard reads the check or the helper.
"""

from __future__ import annotations

import shlex
from dataclasses import dataclass

import w1_50_support as support
import w1_50_symmetric_support as symmetric

check_support = support.check_support

AS_DESIGNER = support.AS_DESIGNER
AS_ENGINEER = support.AS_ENGINEER
AS_ORCHESTRATOR = support.AS_ORCHESTRATOR
ORCHESTRATOR_ON_MAIN = support.ORCHESTRATOR_ON_MAIN
AS_DOCS_ENGINEER = (support.ENGINEER, support.DOCS_TICKET)


def _trailer_paragraph(trailers):
    """Shell: one word that is the final trailer block of a commit with ``trailers`` (two lines)."""
    role, task = trailers
    return f"\"$(printf 'Task: {task}\\nRole: {role}')\""


def _message_options(subject, trailers):
    """Shell: ``-m`` options for ``git commit-tree`` and ``git merge``; the trailers are the final paragraph
    (DEC-182). ``subject`` is shell text inside double quotes, so it may hold a shell variable."""
    options = f"-m \"{subject}\""
    if trailers is not None:
        options += f" -m {_trailer_paragraph(trailers)}"
    return options


# --------------------------------------------------------------------------
# A chain of very many merge commits with 24 parents each; one drops a test designer's change
# --------------------------------------------------------------------------

PARENTS = 24                       # the most DEC-410 (DP-28) lets the helper read: the first parent and 23 others
FORK_POINTS = PARENTS - 1
VERY_MANY_MERGES = 95              # No test pins a number at which anything changes; see the README for the choice


@dataclass(frozen=True)
class ManyMerges:
    """A history that ends with a move of ``main`` along a chain of ``merges`` merge commits, made by
    ``command``; the merge commit number ``dropping`` (1 is the oldest) undoes a test designer's change of
    ``undone``."""
    command: str
    merges: int
    dropping: int
    undone: str
    what: str


def chain_of_merge_commits_with_24_parents(project, sandbox, trailers, dropping, merges=VERY_MANY_MERGES):
    """Before the call ``main`` gets 23 empty commits (plumbing; the orchestrator's trailers) and then a test
    designer's change of an existing acceptance test.

    The command makes ``merges`` merge commits with ``git commit-tree``. Each has 24 parents: the merge commit
    before it (the first: ``HEAD``) and 23 new side commits, one on top of each of the 23 empty commits. Every
    side commit carries the orchestrator's trailers and holds the tree from before the test designer's change,
    so it changes nothing. The merge commits before number ``dropping`` hold ``HEAD``'s tree; number
    ``dropping`` and those after it hold the tree from before the test designer's change. ``main`` is moved
    forward to the last. The merge commits carry ``trailers``.
    """
    assert 1 <= dropping <= merges
    path = support.ACCEPTANCE_FILE
    support.run(project, sandbox,
                "tip=$(git rev-parse HEAD) && tree=$(git rev-parse 'HEAD^{tree}') && "
                f"for n in $(seq 1 {FORK_POINTS}); do "
                f"tip=$(git commit-tree -p \"$tip\" {_message_options('Fork point $n', ORCHESTRATOR_ON_MAIN)} "
                "\"$tree\") || exit 1; done && git merge -q --ff-only \"$tip\"")
    support.run(project, sandbox, support.commit(path, AS_DESIGNER, subject="a test designer's change"))
    assert support.changed_paths(project, "HEAD") == [path], (
        f"the fixture is wrong: the test designer's commit changes {support.changed_paths(project, 'HEAD')}"
    )
    command = (
        "tip=$(git rev-parse HEAD) && tree=$(git rev-parse 'HEAD^{tree}') && "
        "earlier=$(git rev-parse 'HEAD~1^{tree}') && "
        f"forks=$(git rev-list -n {FORK_POINTS} HEAD~1) && "
        f"for k in $(seq 1 {merges}); do "
        f"if [ \"$k\" -eq {dropping} ]; then tree=$earlier; fi; "
        "parents=\"-p $tip\"; n=0; "
        "for fork in $forks; do n=$((n + 1)); "
        f"side=$(git commit-tree -p \"$fork\" {_message_options('Side $k.$n', AS_ORCHESTRATOR)} \"$earlier\") "
        "|| exit 1; parents=\"$parents -p $side\"; done; "
        f"tip=$(git commit-tree $parents {_message_options('Merge $k', trailers)} \"$tree\") || exit 1; "
        "done && " + symmetric._move_to('"$tip"')
    )
    return ManyMerges(command, merges=merges, dropping=dropping, undone=path,
                      what=f"a chain of {merges} merge commits with trailers {trailers} and {PARENTS} parents each "
                           f"(the merge commit before it and {FORK_POINTS} side commits made with `git commit-tree` "
                           f"on {FORK_POINTS} different fork points, each changing nothing), of which number "
                           f"{dropping}, counted from the oldest, holds the tree from before a test designer's "
                           f"change of {path} and so undoes it")


def assert_chain(project, shape, before):
    """Guard against an empty test, from git's own answers and in a handful of git calls.

    The move ``before..HEAD`` holds ``shape.merges`` merge commits and 23 side commits for each, and nothing
    else. Followed by first parents from ``HEAD``, the merge commits lead to ``before``. Each has 24 distinct
    parents; every parent but the first is a commit whose only parent is one of the 23 commits before the test
    designer's change, a different one for each, and whose tree is the tree from before that change. So every
    pair of parents has one merge base, and every side commit holds its merge base's content of every path.

    The merge commits before number ``shape.dropping`` hold ``before``'s tree: they differ from their side
    commits in the test designer's path alone, and the first parent brought it. Number ``shape.dropping`` holds
    the earlier tree and its first parent ``before``'s: it differs from its first parent in the undone path,
    which no other parent brought. By the words of DEC-403 that path is its own change, and its only one. The
    merge commits after it hold the tree all their parents hold. Returns the dropping merge commit's id.
    """
    earlier = check_support.git(project, "rev-parse", f"{before}~1").strip()
    forks = check_support.git(project, "log", f"-n{FORK_POINTS}", "--format=%H %T", earlier).splitlines()
    tree = check_support.git(project, "rev-parse", f"{earlier}^{{tree}}").strip()
    changed = check_support.git(project, "rev-parse", f"{before}^{{tree}}").strip()
    assert len(forks) == FORK_POINTS and all(line.split()[1] == tree for line in forks) and tree != changed, (
        f"the fixture is wrong: the {FORK_POINTS} commits before the test designer's change do not all hold "
        f"one tree other than the tree after it"
    )
    fork_ids = {line.split()[0] for line in forks}
    assert symmetric.differing(project, earlier, before) == [shape.undone], (
        f"the fixture is wrong: the test designer's commit changes "
        f"{symmetric.differing(project, earlier, before)}, not {shape.undone} alone"
    )
    new = {}
    for line in check_support.git(project, "log", "--format=%H %T %P", f"{before}..HEAD").splitlines():
        commit_id, held, *parents = line.split()
        new[commit_id] = (held, parents)
    assert len(new) == shape.merges * PARENTS, (
        f"the fixture is wrong: the move holds {len(new)} new commits, not {shape.merges} merge commits and "
        f"{FORK_POINTS} side commits for each"
    )
    chain = []
    commit_id = check_support.git(project, "rev-parse", "HEAD").strip()
    while commit_id != before:
        assert commit_id in new, f"the fixture is wrong: the first parents of HEAD do not lead to {before}"
        chain.append(commit_id)
        commit_id = new[commit_id][1][0]
    chain.reverse()
    assert len(chain) == shape.merges, (
        f"the fixture is wrong: the chain holds {len(chain)} merge commits, not {shape.merges}"
    )
    sides = set()
    for number, merge_commit in enumerate(chain, 1):
        held, parents = new[merge_commit]
        assert len(parents) == len(set(parents)) == PARENTS, (
            f"the fixture is wrong: merge commit {number} has {len(parents)} parents, {len(set(parents))} distinct"
        )
        expected = changed if number < shape.dropping else tree
        assert held == expected, f"the fixture is wrong: merge commit {number} holds the tree {held}, not {expected}"
        on = set()
        for side in parents[1:]:
            assert side in new and new[side][0] == tree and len(new[side][1]) == 1, (
                f"the fixture is wrong: the parent {side[:12]} of merge commit {number} is no new commit with one "
                f"parent and the tree from before the test designer's change"
            )
            on.add(new[side][1][0])
        assert on == fork_ids, (
            f"the fixture is wrong: the side commits of merge commit {number} are on {len(on)} fork points, not "
            f"on each of the {FORK_POINTS} commits before the test designer's change"
        )
        sides.update(parents[1:])
    assert len(sides) == shape.merges * FORK_POINTS and not sides & set(chain), (
        f"the fixture is wrong: the merge commits share side commits: {len(sides)} distinct"
    )
    assert symmetric.differing(project, "HEAD", before) == [shape.undone], (
        f"the fixture is wrong: HEAD differs from where the branch was in "
        f"{symmetric.differing(project, 'HEAD', before)}, not in {shape.undone} alone"
    )
    return chain[shape.dropping - 1]


# --------------------------------------------------------------------------
# The other side: large ordinary integrations
# --------------------------------------------------------------------------

SIXTY = 60
OCTOPUSES = 3
BRANCHES_IN_AN_OCTOPUS = 8


@dataclass(frozen=True)
class Brought:
    """One branch with one commit, which adds one new file inside the allowed paths of its own trailers."""
    branch: str
    path: str
    trailers: tuple


def _branches(tag, count):
    """``count`` branches. Every third brings a test designer's new acceptance test; the others an engineer's
    new source file or, on the docs ticket, a new document. No two share a path."""
    kinds = (
        (f"{support.ACCEPTANCE}/{support.WBS}/test_{tag}_%02d.py", AS_DESIGNER),
        (f"src/gov/guard/{tag}_%02d.py", AS_ENGINEER),
        (f"docs/{tag}/%02d.md", AS_DOCS_ENGINEER),
    )
    made = []
    for number in range(1, count + 1):
        path, trailers = kinds[(number - 1) % len(kinds)]
        made.append(Brought(f"w1/{tag}-{number:02d}", path % number, trailers))
    return tuple(made)


def _cut_branches(project, sandbox, branches):
    """Make every branch from ``HEAD`` by plumbing: a new blob, ``HEAD``'s tree with that one file added (in a
    temporary index outside the working tree), a commit with the branch's trailers, and the branch. Then
    ``main`` gets a commit of its own, so that no merge of a branch is a fast-forward of the fork."""
    steps = ["base=$(git rev-parse HEAD)", "export GIT_INDEX_FILE=\"$TMPDIR/w1-50-many-merges.index\""]
    for brought in branches:
        path, branch = shlex.quote(brought.path), shlex.quote(brought.branch)
        steps.append(
            f"blob=$(echo {branch} | git hash-object -w --stdin) && git read-tree \"$base\" "
            f"&& git update-index --add --cacheinfo 100644,\"$blob\",{path} "
            f"&& git branch {branch} \"$(git commit-tree -p \"$base\" "
            f"{_message_options('work on ' + brought.branch, brought.trailers)} \"$(git write-tree)\")\""
        )
    support.run(project, sandbox, " && ".join(steps))
    support.run(project, sandbox, support.commit(support.BOOTSTRAP, ORCHESTRATOR_ON_MAIN, subject="main moves on"))


@dataclass(frozen=True)
class ManyOrdinaryMerges:
    """A history that ends with a move of ``main`` along ordinary merge commits made with ``git merge`` by
    ``command``; ``groups`` holds, oldest first, the branches each merge commit merges."""
    command: str
    groups: tuple
    what: str


def _ordinary_merges(groups, trailers):
    return " && ".join(
        f"git merge -q --no-ff {_message_options(f'Merge {number}', trailers)} "
        + " ".join(shlex.quote(brought.branch) for brought in group)
        for number, group in enumerate(groups, 1)
    )


def sixty_two_parent_merges(project, sandbox, trailers=AS_ORCHESTRATOR):
    """60 branches cut from the same commit, one commit each, each inside its own trailers' paths; ``main``
    moved on. The command merges them one after the other, each with ``git merge --no-ff``."""
    branches = _branches("sixty", SIXTY)
    _cut_branches(project, sandbox, branches)
    groups = tuple((brought,) for brought in branches)
    return ManyOrdinaryMerges(_ordinary_merges(groups, trailers), groups,
                              what=f"{SIXTY} ordinary two-parent --no-ff merges (`git merge`, trailers {trailers}) "
                                   f"of {SIXTY} branches, one commit each, each a new file inside its own trailers' "
                                   f"paths; {len([b for b in branches if b.trailers == AS_DESIGNER])} are a test "
                                   f"designer's new acceptance tests")


def three_octopus_merges_of_eight(project, sandbox, trailers=AS_ORCHESTRATOR):
    """24 branches cut from the same commit, one commit each, each inside its own trailers' paths; ``main``
    moved on. The command makes three ``git merge`` calls of eight branches each: three merge commits with
    nine parents."""
    branches = _branches("octopus", OCTOPUSES * BRANCHES_IN_AN_OCTOPUS)
    _cut_branches(project, sandbox, branches)
    groups = tuple(branches[start:start + BRANCHES_IN_AN_OCTOPUS]
                   for start in range(0, len(branches), BRANCHES_IN_AN_OCTOPUS))
    return ManyOrdinaryMerges(_ordinary_merges(groups, trailers), groups,
                              what=f"{OCTOPUSES} ordinary octopus merges (`git merge`, trailers {trailers}) of "
                                   f"{BRANCHES_IN_AN_OCTOPUS} branches each, one commit a branch, each a new file "
                                   f"inside its own trailers' paths")


def assert_ordinary_merges(project, shape, before):
    """Guard against an empty test, from git's own answers and in a handful of git calls.

    Every branch's commit is on top of the one fork, the commit before ``before``, and against it adds its one
    path and nothing else. Followed by first parents from ``HEAD``, the merge commits lead to ``before``, one
    for each group; a merge commit's other parents are its group's branches, in order, and against its first
    parent it adds exactly their paths. ``HEAD`` holds each path as its branch does.

    So every pair of parents of a merge commit has the one merge base, the fork; where a merge commit differs
    from a parent, it holds what exactly one other parent changed against the fork. By the words of DEC-403 and
    DEC-410 no merge commit has an own change, and no path is changed on more than one side.
    """
    branches = [brought for group in shape.groups for brought in group]
    fork = check_support.git(project, "rev-parse", f"{before}~1").strip()
    tips = check_support.git(project, "rev-parse", *(brought.branch for brought in branches)).split()
    added = {}
    listing = check_support.git(project, "log", "--no-walk=unsorted", "--format=%x00%H %P", "--name-status",
                                "--no-renames", *tips)
    for entry in listing.split("\0")[1:]:
        head, *changes = [line for line in entry.splitlines() if line.strip()]
        commit_id, *parents = head.split()
        assert parents == [fork], f"the fixture is wrong: the branch commit {commit_id[:12]} is not on the fork"
        added[commit_id] = changes
    for brought, tip in zip(branches, tips):
        assert added[tip] == [f"A\t{brought.path}"], (
            f"the fixture is wrong: the commit of {brought.branch} changes {added[tip]}, not {brought.path} alone"
        )
    assert symmetric.differing(project, before, fork) == [support.BOOTSTRAP], (
        "the fixture is wrong: main did not move on by one commit of its own before the call"
    )
    merges = check_support.git(project, "log", "--first-parent", "--reverse", "-m", "--format=%x00%H %P",
                               "--name-status", "--no-renames", f"{before}..HEAD").split("\0")[1:]
    assert len(merges) == len(shape.groups), (
        f"the fixture is wrong: the move holds {len(merges)} merge commits along its first parents, not "
        f"{len(shape.groups)}"
    )
    tip_of = dict(zip((brought.branch for brought in branches), tips))
    first = before
    for entry, group in zip(merges, shape.groups):
        head, *changes = [line for line in entry.splitlines() if line.strip()]
        commit_id, *parents = head.split()
        assert parents == [first, *(tip_of[brought.branch] for brought in group)], (
            f"the fixture is wrong: the merge commit {commit_id[:12]} has the parents {parents}"
        )
        assert sorted(changes) == sorted(f"A\t{brought.path}" for brought in group), (
            f"the fixture is wrong: against its first parent the merge commit {commit_id[:12]} changes {changes}"
        )
        first = commit_id
    assert first == check_support.git(project, "rev-parse", "HEAD").strip()
    new = check_support.git(project, "rev-list", f"{before}..HEAD").split()
    assert len(new) == len(merges) + len(branches), (
        f"the fixture is wrong: the move holds {len(new)} new commits, not {len(merges)} merge commits and "
        f"{len(branches)} branch commits"
    )
    held = check_support.git(project, "rev-parse", *(f"HEAD:{brought.path}" for brought in branches)).split()
    theirs = check_support.git(project, "rev-parse",
                               *(f"{brought.branch}:{brought.path}" for brought in branches)).split()
    assert held == theirs and len(set(held)) == len(branches), (
        "the fixture is wrong: HEAD does not hold every branch's file as the branch has it"
    )
