"""Support code for the eighth batch of the W1-50 acceptance tests: DEC-403, the symmetric rule.

DEC-403 (delegated; packages DP-20 option (a) and DP-19 option (a)) widens "against its first parent" in
DEC-394 and DEC-398: the one helper reads every parent of a merge commit the way it reads the first.

**The rule, for one path of a merge commit with the parents P1..Pn.** For each parent Pi whose content of the
path differs from the merge commit's, the path is the merge commit's *own* change unless some other parent Pj
*brought* the merge commit's content: Pj's content of the path is the merge commit's, and it differs from the
one merge base of Pi and Pj. A merge that takes each side's change is silent in both directions; a merge that
keeps one parent's content where only another parent changed the path has changed that path itself.

**Fail closed.** When another parent has several merge bases with the first parent, or none, nothing is
brought: every path where the merge commit differs from any parent is its own change (DP-19: an octopus merge
fails closed as a whole).

This module builds the histories of that batch. Every history is a real one, made in the throw-away project
with commits, ``git merge`` and, where a shape needs it, ``git commit-tree``. A tree a merge commit made by
plumbing is to hold is prepared before the call, as the tree of a commit on the branch ``prepared``; that
commit is never an ancestor of ``HEAD``, so it is no commit of the move.

``own_by_the_words`` works the rule out from git's own answers. It is a guard for the fixtures only: it shows
that the history a test built is the one its literal expectation describes.
"""

from __future__ import annotations

import shlex
from dataclasses import dataclass

import w1_50_support as support

check_support = support.check_support

AS_DESIGNER = support.AS_DESIGNER
AS_ENGINEER = support.AS_ENGINEER
AS_ORCHESTRATOR = support.AS_ORCHESTRATOR
NO_TRAILERS = support.NO_TRAILERS
ORCHESTRATOR_ON_MAIN = support.ORCHESTRATOR_ON_MAIN

TICKET_BRANCH = support.TICKET_BRANCH
SECOND_BRANCH = support.SECOND_BRANCH
CROSSING = support.CROSSING
ISLAND = support.ISLAND
PREPARED = "prepared"              # its head's tree is the tree a merge commit made by plumbing is to hold
SIDE = "side"                      # a branch that forked before the changes a merge commit drops
TEMPORARY = "tmp"                  # the branch of the plain porcelain shape

NARROWED_TICKET = check_support.AUDITOR_TICKET_ID            # DAEO-zz94: an orchestrator commit narrows its paths
CLOSED_TICKET = check_support.NEW_DIRECTORY_TICKET_ID        # DAEO-zz96: an orchestrator commit closes it
NARROWED_FILE = support.ticket_file(NARROWED_TICKET)
CLOSED_FILE = support.ticket_file(CLOSED_TICKET)
ACCEPTANCE_README = f"{support.ACCEPTANCE}/{support.WBS}/README.md"   # in the fixture project from the start


# --------------------------------------------------------------------------
# The two changes a merge commit drops: a test designer's tests, or an orchestrator's ticket files
# --------------------------------------------------------------------------

@dataclass(frozen=True)
class Dropped:
    """Two commits on ``main``, the second on top of the first, that a merge commit of the batch drops."""
    name: str
    work: str                 # shell: makes the two commits
    first: str                # the path of the first commit: a file that exists already
    second: str               # the path of the second commit
    trailers: tuple | None    # the dropping merge commit's trailers where a test does not vary them
    what: str

    @property
    def paths(self):
        return (self.first, self.second)


# A test designer edits an existing acceptance test, then adds a new one. No trailers of a merge commit of this
# batch allow a path under tests/acceptance/**: not the orchestrator's, not the engineer's, not the caller's.
TESTS = Dropped(
    name="a-test-designer-s-tests",
    work=support.commits((support.ACCEPTANCE_FILE, AS_DESIGNER), (support.NEW_TEST, AS_DESIGNER)),
    first=support.ACCEPTANCE_FILE, second=support.NEW_TEST, trailers=AS_ORCHESTRATOR,
    what=f"a test designer's commits of {support.ACCEPTANCE_FILE} (edited) and {support.NEW_TEST} (added)",
)

# The orchestrator narrows one ticket's allowed paths, then closes another ticket. The dropping merge commit
# carries an engineer's trailers: a change under .tickets/** in a commit with a worker's Role trailer is a
# finding (DEC-390, DP-16). With the orchestrator's trailers, or none, the orchestrator may write a ticket file
# (DEC-156, DEC-359); that form is not pinned (README, package DP-21).
TICKETS = Dropped(
    name="an-orchestrator-s-ticket-files",
    work=(f"sed -i 's|^- docs/audit/\\*\\*$|- docs/audit/reports/**|' {NARROWED_FILE} && "
          + support.commit_paths([NARROWED_FILE], ORCHESTRATOR_ON_MAIN, subject=f"{NARROWED_TICKET} narrowed")
          + " && " + support.set_status_in_the_working_tree(CLOSED_TICKET, "closed") + " && "
          + support.commit_paths([CLOSED_FILE], (support.ORCHESTRATOR, CLOSED_TICKET),
                                 subject=f"{CLOSED_TICKET} closed")),
    first=NARROWED_FILE, second=CLOSED_FILE, trailers=AS_ENGINEER,
    what=f"an orchestrator's commits of {NARROWED_FILE} (allowed paths narrowed) and {CLOSED_FILE} (closed)",
)

DROPPED = {TESTS.name: TESTS, TICKETS.name: TICKETS}


def do_the_work(project, sandbox, dropped):
    """Make the two commits of ``dropped`` on the branch checked out, with no hook around them."""
    before = check_support.git(project, "rev-parse", "HEAD").strip()
    support.run(project, sandbox, dropped.work)
    assert check_support.git(project, "rev-parse", "HEAD~2").strip() == before, (
        f"the fixture is wrong: {dropped.what} are not two commits on top of {before[:12]}"
    )
    for revision, path in (("HEAD~1", dropped.first), ("HEAD", dropped.second)):
        assert support.changed_paths(project, revision) == [path], (
            f"the fixture is wrong: {revision} changes {support.changed_paths(project, revision)}, not {path}"
        )


def prepare_tree(project, sandbox, change, start="HEAD"):
    """Commit ``change`` (shell) on a new branch ``prepared`` cut from ``start``; ``main`` is checked out again.

    ``prepared^{tree}`` is then the tree a merge commit made with ``git commit-tree`` is to hold.
    """
    support.run(project, sandbox,
                f"git checkout -q -b {PREPARED} {shlex.quote(start)} && {change} "
                f"&& git commit -q --allow-empty -m 'the tree to hold' && git checkout -q main")
    assert not support.is_ancestor(project, PREPARED, "main"), (
        f"the fixture is wrong: the commit on {PREPARED} is in main's history"
    )


def _porcelain_merge(branch, trailers, strategy=""):
    """Shell: ``git merge`` of ``branch`` as porcelain makes it. Without trailers it is the plain one command."""
    if trailers is None:
        return f"git merge -q --no-ff {strategy}-m {shlex.quote('Merge ' + branch)} {shlex.quote(branch)}"
    return (f"git merge -q --no-ff --no-commit {strategy}{shlex.quote(branch)} "
            f"&& git commit -q -m {shlex.quote('Merge ' + branch)}" + support._trailer_options(trailers))


def _move_to(merge_commit):
    """Shell: move the branch forward to a commit object made by plumbing; the working tree follows."""
    return f"git merge -q --ff-only {merge_commit}"


# --------------------------------------------------------------------------
# The rule, worked out from git's own answers (a guard for the fixtures)
# --------------------------------------------------------------------------

def differing(project, commit_id, parent):
    """The paths where ``commit_id`` holds other content than ``parent``; a rename is two paths."""
    return check_support.git(project, "diff", "--no-renames", "--name-only", parent, commit_id).split()


def differing_from_any_parent(project, commit_id="HEAD"):
    """The sorted paths where the commit holds other content than at least one of its parents."""
    paths = set()
    for parent in support.parents_of(project, commit_id):
        paths.update(differing(project, commit_id, parent))
    return sorted(paths)


def tree_paths(project, commit_id="HEAD"):
    """Every path the commit's tree holds, sorted."""
    return sorted(check_support.git(project, "ls-tree", "-r", "--name-only", commit_id).split())


def fails_closed(project, commit_id="HEAD"):
    """True when another parent has several merge bases with the first parent, or none (DEC-398, DEC-403)."""
    first, *others = support.parents_of(project, commit_id)
    return any(len(support.merge_bases(project, first, other)) != 1 for other in others)


def own_by_the_words(project, commit_id="HEAD"):
    """The merge commit's own changes by the words of DEC-403, sorted. A guard for the fixtures only.

    It refuses a history in which two parents other than the first cross each other while the merge does not
    fail closed as a whole: DEC-403 leaves that shape "as built", and no expectation of this suite rests on it.
    """
    parents = support.parents_of(project, commit_id)
    assert len(parents) > 1, f"the fixture is wrong: {commit_id} is no merge commit"
    if fails_closed(project, commit_id):
        return differing_from_any_parent(project, commit_id)
    own = set()
    for parent in parents:
        for path in differing(project, commit_id, parent):
            held = support.content_at(project, commit_id, path)
            brought = False
            for other in parents:
                if other == parent:
                    continue
                bases = support.merge_bases(project, parent, other)
                assert len(bases) == 1, (
                    f"the fixture is wrong: the parents {parent[:12]} and {other[:12]} have the merge bases "
                    f"{bases}; this guard reads no such history"
                )
                if support.content_at(project, other, path) == held and held != support.content_at(
                        project, bases[0], path):
                    brought = True
            if not brought:
                own.add(path)
    return sorted(own)


def assert_own(project, commit_id, own, what):
    """Guard against an empty test: by the words of DEC-403 the merge commit's own changes are ``own``."""
    found = own_by_the_words(project, commit_id)
    assert found == sorted(own), (
        f"the fixture is wrong: by the words of DEC-403 the own changes of {what} are {found}, not {sorted(own)}"
    )


def assert_silent_by_the_first_parent(project, commit_id, paths, what):
    """Guard: read against its first parent alone (DEC-394 as built), none of ``paths`` is the merge commit's
    own change. Either the first parent holds the merge commit's content of it, or another parent brought it."""
    first, *others = support.parents_of(project, commit_id)
    several = fails_closed(project, commit_id)
    changed = set(differing(project, commit_id, first))
    for path in paths:
        if path not in changed:
            continue
        held = support.content_at(project, commit_id, path)
        assert not several and any(
            support.content_at(project, other, path) == held
            and held != support.content_at(project, support.merge_bases(project, first, other)[0], path)
            for other in others), (
            f"the fixture is wrong: read against its first parent alone, {path} is already the own change of {what}"
        )


# --------------------------------------------------------------------------
# The shapes: a merge commit that keeps one parent's content and so drops what another parent changed
# --------------------------------------------------------------------------

@dataclass(frozen=True)
class DroppingMerge:
    """A history that ends with a move of ``main`` made by ``command``; one merge commit of the move drops
    changes."""
    command: str              # shell: the call
    dropping: str             # the revision of the dropping merge commit once the command has run
    own: tuple                # the dropping merge commit's own changes by DEC-403, all of them
    named: tuple              # the paths a finding is to name
    kept: tuple               # paths another parent brought into the dropping merge commit: no finding names them
    what: str


def parents_turned_round(project, sandbox, dropped, trailers):
    """Shape B. The merge commit's first parent is ``HEAD~2``, its second parent ``HEAD``, its tree ``HEAD~2``'s."""
    do_the_work(project, sandbox, dropped)
    merge_commit = support.commit_object("HEAD~2^{tree}", ["HEAD~2", "HEAD"], trailers)
    return DroppingMerge(_move_to(merge_commit), "HEAD", own=dropped.paths, named=dropped.paths, kept=(),
                         what=f"a merge commit with trailers {trailers}, the parents HEAD~2 and HEAD in that order "
                              f"and the tree of HEAD~2: it drops {dropped.what}")


def turned_round_through_a_new_empty_commit(project, sandbox, dropped, trailers):
    """Shape C. As B; the first parent is a new empty commit made on top of ``HEAD~2``."""
    do_the_work(project, sandbox, dropped)
    empty = support.commit_object("HEAD~2^{tree}", ["HEAD~2"], AS_ORCHESTRATOR, subject="An empty commit")
    merge_commit = support.commit_object("HEAD~2^{tree}", ["$empty", "HEAD"], trailers)
    return DroppingMerge(f"empty={empty} && " + _move_to(merge_commit), "HEAD", own=dropped.paths,
                         named=dropped.paths, kept=(),
                         what=f"a merge commit with trailers {trailers} whose first parent is a new empty commit on "
                              f"top of HEAD~2, whose second parent is HEAD and whose tree is that of HEAD~2: it "
                              f"drops {dropped.what}")


def plain_porcelain(project, sandbox, dropped, trailers):
    """Shape D. ``git checkout -b tmp HEAD~2``, an orchestrator's commit of ``README.md``, ``git merge -s ours
    main``, and ``main`` fast-forwarded to the result."""
    do_the_work(project, sandbox, dropped)
    command = (f"git checkout -q -b {TEMPORARY} HEAD~2 && "
               + support.commit(support.README, AS_ORCHESTRATOR, subject="outside the judged paths")
               + " && " + _porcelain_merge("main", trailers, strategy="-s ours ")
               + f" && git checkout -q main && git merge -q --ff-only {TEMPORARY}")
    return DroppingMerge(command, "HEAD", own=dropped.paths, named=dropped.paths, kept=(support.README,),
                         what=f"`git checkout -b {TEMPORARY} HEAD~2`, an orchestrator's commit of {support.README}, "
                              f"`git merge -s ours main` (trailers {trailers}) and main fast-forwarded to it: the "
                              f"merge commit drops {dropped.what}")


def turned_round_setting_one_back(project, sandbox, dropped, trailers):
    """Shape E. As B, but the merge commit sets back only the first of the two changes and keeps the second."""
    do_the_work(project, sandbox, dropped)
    prepare_tree(project, sandbox, f"git checkout -q HEAD~2 -- {shlex.quote(dropped.first)}")
    merge_commit = support.commit_object(PREPARED + "^{tree}", ["HEAD~2", "HEAD"], trailers)
    return DroppingMerge(_move_to(merge_commit), "HEAD", own=(dropped.first,), named=(dropped.first,),
                         kept=(dropped.second,),
                         what=f"a merge commit with trailers {trailers} and the parents HEAD~2 and HEAD in that "
                              f"order, which holds HEAD's tree with {dropped.first} set back to HEAD~2's content "
                              f"(of {dropped.what})")


def octopus_turned_round(project, sandbox, dropped, trailers):
    """Shape J2. A branch ``side`` forked before the changes and got an orchestrator's commit of ``README.md``.
    The merge commit has the parents ``side``, ``HEAD`` and ``HEAD~1`` and the tree of ``side``."""
    support.run(project, sandbox,
                f"git checkout -q -b {SIDE} && "
                + support.commit(support.README, AS_ORCHESTRATOR, subject="the side's own commit")
                + " && git checkout -q main")
    do_the_work(project, sandbox, dropped)
    merge_commit = support.commit_object(SIDE + "^{tree}", [SIDE, "HEAD", "HEAD~1"], trailers)
    return DroppingMerge(_move_to(merge_commit), "HEAD", own=dropped.paths, named=dropped.paths,
                         kept=(support.README,),
                         what=f"a merge commit with trailers {trailers}, the parents {SIDE}, HEAD and HEAD~1 and "
                              f"the tree of {SIDE}, which forked before the changes: it drops {dropped.what}")


def unrelated_first_parent(project, sandbox, dropped, trailers):
    """Shape NB2. The first parent is a new commit without a parent and with an empty tree; the second parent is
    ``HEAD``. The merge commit's tree is ``HEAD``'s without ``tests/acceptance/`` (the tests) or without the two
    ticket files (the tickets). No merge base."""
    do_the_work(project, sandbox, dropped)
    if dropped is TESTS:
        removed = (ACCEPTANCE_README, *dropped.paths)
        prepare_tree(project, sandbox, f"git rm -rq -- {shlex.quote(support.ACCEPTANCE)}")
    else:
        removed = dropped.paths
        prepare_tree(project, sandbox, "git rm -q -- " + " ".join(shlex.quote(path) for path in removed))
    kept = tuple(check_support.git(project, "ls-tree", "-r", "--name-only", PREPARED).split())
    assert kept and not set(kept) & set(removed), f"the fixture is wrong: the prepared tree holds {kept}"
    root = support.commit_object("$nothing", [], AS_ORCHESTRATOR, subject="A commit without a parent")
    merge_commit = support.commit_object(PREPARED + "^{tree}", ["$root", "HEAD"], trailers)
    return DroppingMerge(f"nothing=$(git mktree < /dev/null) && root={root} && " + _move_to(merge_commit), "HEAD",
                         own=(*kept, *removed), named=dropped.paths, kept=(),
                         what=f"a merge commit with trailers {trailers} whose first parent is a new commit without "
                              f"a parent and with an empty tree, whose second parent is HEAD and whose tree is "
                              f"HEAD's without {', '.join(removed)} (after {dropped.what})")


def branch_that_took_main_with_ours(project, sandbox, dropped, trailers, take_in_the_call):
    """Shape N. A ticket branch got an engineer's commit; ``main`` then got the two changes. The branch takes
    ``main`` with ``git merge -s ours`` (the dropping merge commit, with ``trailers``), and an ordinary
    ``git merge --no-ff`` with the orchestrator's trailers merges the branch into ``main``.

    With ``take_in_the_call`` both merges are the call's (N1); without it the branch took ``main`` before the
    call and the call makes only the final merge (N2). Either way the dropping merge commit is new to ``HEAD``
    in the move: it is the final merge commit's second parent.
    """
    support.ticket_branch(project, sandbox, (support.SOURCE, AS_ENGINEER), main_moves_on=False)
    do_the_work(project, sandbox, dropped)
    take = (f"git checkout -q {shlex.quote(TICKET_BRANCH)} && "
            + _porcelain_merge("main", trailers, strategy="-s ours ") + " && git checkout -q main")
    final = support.merge(trailers=AS_ORCHESTRATOR)
    if take_in_the_call:
        command = take + " && " + final
    else:
        support.run(project, sandbox, take)
        command = final
    when = "in the same call" if take_in_the_call else "before the call"
    return DroppingMerge(command, "HEAD^2", own=dropped.paths, named=dropped.paths, kept=(support.SOURCE,),
                         what=f"{TICKET_BRANCH} (an engineer's {support.SOURCE}) takes main with `git merge -s ours` "
                              f"(trailers {trailers}) {when}, dropping {dropped.what}; then an ordinary "
                              f"`git merge --no-ff` of the branch into main")


def turned_round_then_one_restored(project, sandbox):
    """The follow-on. A turned-round merge commit (shape B) undoes both tests; a second merge commit on top of
    it, with ``HEAD`` for its second parent, holds ``HEAD``'s content of the second test again. Both are made in
    the one call, with the orchestrator's trailers. The first test stays undone."""
    dropped = TESTS
    do_the_work(project, sandbox, dropped)
    prepare_tree(project, sandbox, f"git checkout -q HEAD~2 -- {shlex.quote(dropped.first)}")
    first = support.commit_object("HEAD~2^{tree}", ["HEAD~2", "HEAD"], AS_ORCHESTRATOR)
    second = support.commit_object(PREPARED + "^{tree}", ["$first", "HEAD"], AS_ORCHESTRATOR,
                                   subject="Merge again")
    return DroppingMerge(f"first={first} && " + _move_to(second), "HEAD^1", own=dropped.paths,
                         named=(dropped.first,), kept=(),
                         what=f"a turned-round merge commit that undoes {dropped.what}, and on top of it a second "
                              f"merge commit that holds {dropped.second} again; {dropped.first} stays undone")


def assert_dropping(project, shape, before):
    """Guard against an empty test, from git's own answers.

    ``HEAD`` moved forward from ``before``; the dropping merge commit is new in the move and, by the words of
    DEC-403, its own changes are ``shape.own``; read against its first parent alone, none of the paths a
    finding is to name is its own change; and no other merge commit of the move has an own change among them.
    """
    assert support.is_ancestor(project, before, "HEAD"), "the fixture is wrong: the move is not forward"
    dropping = check_support.git(project, "rev-parse", shape.dropping).strip()
    assert support.is_merge(project, dropping), f"the fixture is wrong: {shape.dropping} is no merge commit"
    assert not support.is_ancestor(project, dropping, before), (
        "the fixture is wrong: the dropping merge commit was in HEAD's history before the call"
    )
    assert_own(project, dropping, shape.own, shape.what)
    assert_silent_by_the_first_parent(project, dropping, shape.named, shape.what)
    for path in shape.named:
        assert support.content_at(project, "HEAD", path) != support.content_at(project, before, path), (
            f"the fixture is wrong: after the call HEAD holds for {path} what it held before"
        )
    return dropping


# --------------------------------------------------------------------------
# Silent: a merge that takes each side's change
# --------------------------------------------------------------------------

@dataclass(frozen=True)
class TakingMerge:
    """A history that ends with a merge commit, made by ``command``, that takes what each of its parents changed."""
    command: str
    differs: tuple            # the paths where the merge commit differs from at least one parent
    what: str


# name: (the branch's commit, main's commit since the fork). One of the two is a test designer's.
EACH_SIDE_ITS_OWN_PATH = {
    "the-test-designer-s-commit-on-main": ((support.SOURCE, AS_ENGINEER), (support.ACCEPTANCE_FILE, AS_DESIGNER)),
    "the-test-designer-s-commit-on-the-branch": ((support.NEW_TEST, AS_DESIGNER),
                                                 (support.BOOTSTRAP, ORCHESTRATOR_ON_MAIN)),
}


def each_side_changed_its_own_path(project, sandbox, sides, turned_round, trailers=AS_ORCHESTRATOR):
    """The ticket branch made one commit and ``main`` another, of different paths; the merge commit holds both.

    Ordinary: ``git merge --no-ff`` of the branch. Turned round: a merge commit with the same tree whose first
    parent is the branch and whose second parent is ``HEAD``, and ``main`` moved forward to it.
    """
    on_the_branch, on_main = EACH_SIDE_ITS_OWN_PATH[sides]
    support.ticket_branch(project, sandbox, on_the_branch, main_moves_on=False)
    support.run(project, sandbox, support.commit(*on_main, subject="main's own commit"))
    differs = (on_the_branch[0], on_main[0])
    if not turned_round:
        return TakingMerge(support.merge(trailers=trailers), differs,
                           what=f"an ordinary --no-ff merge of {TICKET_BRANCH} ({on_the_branch}) into main, which "
                                f"got {on_main} since the fork")
    prepare_tree(project, sandbox, f"git merge -q --no-ff -m merged {shlex.quote(TICKET_BRANCH)}")
    merge_commit = support.commit_object(PREPARED + "^{tree}", [TICKET_BRANCH, "HEAD"], trailers)
    return TakingMerge(_move_to(merge_commit), differs,
                       what=f"a merge commit with the parents {TICKET_BRANCH} ({on_the_branch}) and HEAD (main, "
                            f"which got {on_main} since the fork) in that order, holding both changes")


def both_sides_made_the_same_change(project, sandbox, trailers=AS_ORCHESTRATOR):
    """A test designer made the same change of an acceptance test on the ticket branch and on ``main``; the
    branch also got an engineer's commit. An ordinary ``git merge --no-ff``."""
    path = support.ACCEPTANCE_FILE
    support.ticket_branch(project, sandbox, (path, AS_DESIGNER), (support.SOURCE, AS_ENGINEER), main_moves_on=False)
    support.run(project, sandbox, support.commit(path, AS_DESIGNER, subject="the same change on main"))
    fork = support.merge_bases(project, "HEAD", TICKET_BRANCH)
    held = support.content_at(project, "HEAD", path)
    assert len(fork) == 1 and held == support.content_at(project, TICKET_BRANCH, path) and (
        held != support.content_at(project, fork[0], path)), (
        f"the fixture is wrong: the two sides did not make the same change of {path}"
    )
    return TakingMerge(support.merge(trailers=trailers), (support.SOURCE,),
                       what=f"an ordinary --no-ff merge of {TICKET_BRANCH} into main after a test designer made the "
                            f"same change of {path} on both; the branch also brings an engineer's {support.SOURCE}")


def assert_taking(project, shape):
    """Guard: ``HEAD`` is a merge commit that differs from its parents in exactly ``shape.differs``, and by the
    words of DEC-403 none of those paths is its own change."""
    assert support.is_merge(project), f"the fixture is wrong: HEAD is no merge commit after {shape.what}"
    assert differing_from_any_parent(project) == sorted(shape.differs), (
        f"the fixture is wrong: the merge commit differs from its parents in {differing_from_any_parent(project)}"
    )
    assert_own(project, "HEAD", (), shape.what)


# --------------------------------------------------------------------------
# Several merge bases, or none; octopus merges (DP-19)
# --------------------------------------------------------------------------

@dataclass(frozen=True)
class ReadMerge:
    """A history that ends with a merge commit made by ``command``, for the helper's cases."""
    command: str
    what: str


def criss_cross_turned_round(project, sandbox):
    """Several merge bases with a dropped change. ``main`` and ``crossing`` cross (two merge bases);
    ``crossing`` then gets an engineer's commit and ``main`` a test designer's. The merge commit has the parents
    ``crossing`` and ``HEAD`` in that order and the tree of ``crossing``: it drops the test designer's change."""
    support.criss_cross_merge(project, sandbox, (support.SOURCE, AS_ENGINEER), AS_ORCHESTRATOR)
    support.run(project, sandbox, support.commit(support.ACCEPTANCE_FILE, AS_DESIGNER, subject="after the crossing"))
    merge_commit = support.commit_object(CROSSING + "^{tree}", [CROSSING, "HEAD"], AS_ORCHESTRATOR)
    return ReadMerge(_move_to(merge_commit),
                     what=f"a merge commit with the parents {CROSSING} and HEAD in that order (two merge bases) and "
                          f"the tree of {CROSSING}: it drops main's test designer commit of "
                          f"{support.ACCEPTANCE_FILE}")


def octopus_with_a_crossing_parent(project, sandbox):
    """An octopus merge: ``HEAD``, a branch that crosses it (two merge bases with the first parent) and an
    ordinary ticket branch (one merge base). The tree holds every side's changes."""
    support.ticket_branch(project, sandbox, (support.NEW_TEST, AS_DESIGNER), main_moves_on=False)
    support.criss_cross_merge(project, sandbox, (support.SOURCE, AS_ENGINEER), AS_ORCHESTRATOR)
    prepare_tree(project, sandbox, f"git merge -q --no-ff -m one {shlex.quote(CROSSING)} "
                                   f"&& git merge -q --no-ff -m two {shlex.quote(TICKET_BRANCH)}")
    merge_commit = support.commit_object(PREPARED + "^{tree}", ["HEAD", CROSSING, TICKET_BRANCH], AS_ORCHESTRATOR)
    return ReadMerge(_move_to(merge_commit),
                     what=f"an octopus merge of HEAD, {CROSSING} (two merge bases with HEAD; an engineer's "
                          f"{support.SOURCE}) and {TICKET_BRANCH} (one merge base; a test designer's "
                          f"{support.NEW_TEST})")


def octopus_with_an_unrelated_parent(project, sandbox):
    """An octopus merge: ``HEAD``, an ordinary ticket branch (one merge base) and a history with nothing in
    common with ``HEAD``'s (no merge base). The tree holds every side's files."""
    support.ticket_branch(project, sandbox, (support.NEW_TEST, AS_DESIGNER))
    support.unrelated_merge(project, sandbox, (support.ISLAND_NOTES, AS_ORCHESTRATOR), AS_ORCHESTRATOR)
    prepare_tree(project, sandbox, f"git merge -q --no-ff -m one {shlex.quote(TICKET_BRANCH)} "
                                   f"&& git merge -q --no-ff --allow-unrelated-histories -m two {ISLAND}")
    merge_commit = support.commit_object(PREPARED + "^{tree}", ["HEAD", TICKET_BRANCH, ISLAND], AS_ORCHESTRATOR)
    return ReadMerge(_move_to(merge_commit),
                     what=f"an octopus merge of HEAD, {TICKET_BRANCH} (one merge base; a test designer's "
                          f"{support.NEW_TEST}) and {ISLAND} (no merge base; one commit that adds "
                          f"{support.ISLAND_NOTES})")


def octopus_whose_other_parents_cross_each_other(project, sandbox):
    """An octopus merge of ``HEAD`` and two branches that each have one merge base with ``HEAD`` and cross each
    other (two merge bases between them).

    One branch got a test designer's new test, the other an engineer's source file; each merged the other's
    commit; the second branch then got one more engineer's commit; ``main`` moved on. The tree holds it all.
    """
    for branch, step in ((TICKET_BRANCH, (support.NEW_TEST, AS_DESIGNER)),
                         (SECOND_BRANCH, (support.SOURCE, AS_ENGINEER))):
        check_support.git(project, "checkout", "-q", "-b", branch, "main")
        support.run(project, sandbox, support.commit(*step))
    first_tip = check_support.git(project, "rev-parse", TICKET_BRANCH).strip()
    second_tip = check_support.git(project, "rev-parse", SECOND_BRANCH).strip()
    check_support.git(project, "checkout", "-q", TICKET_BRANCH)
    support.run(project, sandbox, support.merge(branch=second_tip, trailers=AS_ORCHESTRATOR))
    check_support.git(project, "checkout", "-q", SECOND_BRANCH)
    support.run(project, sandbox, support.merge(branch=first_tip, trailers=AS_ORCHESTRATOR))
    support.run(project, sandbox, support.commit(support.SECOND_SOURCE, AS_ENGINEER, subject="after the crossing"))
    check_support.git(project, "checkout", "-q", "main")
    support.run(project, sandbox, support.commit(support.BOOTSTRAP, ORCHESTRATOR_ON_MAIN, subject="main moves on"))
    prepare_tree(project, sandbox, f"git merge -q --no-ff -m one {shlex.quote(TICKET_BRANCH)} "
                                   f"&& git merge -q --no-ff -m two {shlex.quote(SECOND_BRANCH)}")
    merge_commit = support.commit_object(PREPARED + "^{tree}", ["HEAD", TICKET_BRANCH, SECOND_BRANCH],
                                         AS_ORCHESTRATOR)
    return ReadMerge(_move_to(merge_commit),
                     what=f"an octopus merge of HEAD, {TICKET_BRANCH} and {SECOND_BRANCH}; the two branches each "
                          f"have one merge base with HEAD and cross each other")
