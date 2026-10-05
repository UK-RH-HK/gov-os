"""W1-50 — the repository's ``.git/info/grafts`` does not change which commits the check judges.

Added after implementation; reason: review finding (DEC-136, DEC-137).
DEC-390: "`.git/info/grafts` is closed off for the check's git calls; this
needs no decision, only tests and a fix."

The behaviour, as it was passed to the test designer:

    A repository-local file `.git/info/grafts` can tell git that a commit has
    other parents than its object holds. The check judges a move's commits as
    git reads the real objects, whatever `.git/info/grafts` holds.

It is the behaviour of ``test_w1_50_repository_settings.py`` (local settings
and replacement refs) for one more repository-local file, and it is held by
the same KPIs:

KPI success 1 [CAP-58.h]: a forward HEAD move "is judged commit by commit".

KPI success 5 [CAP-58.h]: "A commit carrying a Role: owner trailer that is made
during any agent session's call is a finding (DEC-360)".

KPI failure 2: "A commit that changes a path outside the allowed paths of its
own Role and Task trailers raises no finding, whoever the caller is".

**The graft.** One call makes two commits, A and then B, and then writes one
line into ``.git/info/grafts``: ``<B> <HEAD before the call>``. Git's history
walk then goes from B straight to the old ``HEAD``: A is not among the commits
it lists for the move, and B seems to change everything A and B change
together. The objects are untouched: B's parent is A, and A is what a clone, a
push or a merge carries.

Every flagged case has a twin without the graft file (``without-a-graft``),
which is flagged already: the graft alone is what the check must not follow.

What the commits really are is read by the tests with ``GIT_GRAFT_FILE`` set
to an empty file and replacement refs off.

No test writes a grafts file anywhere but in its throw-away project.
"""

from __future__ import annotations

import pytest

import w1_50_support as support

check_support = support.check_support

ORCHESTRATOR = support.ORCHESTRATOR
ENGINEER = support.ENGINEER
TICKET = support.TICKET
AS_DESIGNER = support.AS_DESIGNER
AS_ENGINEER = support.AS_ENGINEER
AS_ORCHESTRATOR = support.AS_ORCHESTRATOR

ROLE_OWNER = f"Role: {support.OWNER}"
TASK = f"Task: {TICKET}"

GRAFTED = (True, False)
GRAFT_IDS = ("with-the-graft", "without-a-graft")


def _two_commits(project, call, first, second, role, grafted):
    """One call: the commit ``first``, the commit ``second`` and, with ``grafted``, the graft that hides ``first``.

    Returns (result, state after, the id of the hidden commit).
    """
    before = check_support.git(project, "rev-parse", "HEAD").strip()
    command = "old=$(git rev-parse HEAD) && " + first + " && " + second
    if grafted:
        command += " && " + support.graft_newest_onto("$old")
    result, left = call(project, command, role, TICKET)
    real = support.new_commits(project, before)
    assert len(real) == 2 and real[0] == left[0][0], (
        f"the fixture is wrong: the move really holds the commits {real}"
    )
    parents = support.ungrafted(project, "rev-list", "--parents", "-n", "1", "HEAD").split()[1:]
    assert parents == [real[1]], f"the fixture is wrong: the newest commit's real parents are {parents}"
    if grafted:
        assert support.grafts(project) == [f"{real[0]} {before}"], (
            f"the fixture is wrong: {support.GRAFTS} holds {support.grafts(project)}"
        )
        assert support.new_commits(project, before, real=False) == [real[0]], (
            "the fixture is wrong: with the graft git still lists the first commit among the commits of the move"
        )
    else:
        assert support.grafts(project) == [], f"the fixture is wrong: {support.GRAFTS} exists"
    return result, left, real[1]


# --------------------------------------------------------------------------
# (i) A hidden commit that carries Role: owner
# --------------------------------------------------------------------------

@pytest.mark.parametrize("grafted", GRAFTED, ids=GRAFT_IDS)
def test_a_graft_does_not_hide_a_role_owner_commit(project, call, grafted):
    """KPI success 5. The orchestrator's own call makes a ``Role: owner`` commit of README.md, then an
    orchestrator's commit of docs/notes.md. The orchestrator may write both paths itself, so only the trailer
    makes the first commit a finding."""
    first = support.commit_with(support.README, *support.trailer_arguments(TASK, ROLE_OWNER))
    second = support.commit(support.NOTES, AS_ORCHESTRATOR)
    result, left, hidden = _two_commits(project, call, first, second, ORCHESTRATOR, grafted)
    assert support.final_block(project, hidden) == [TASK.encode(), ROLE_OWNER.encode()], (
        f"the fixture is wrong: the first commit's final block is {support.final_block(project, hidden)}"
    )
    what = (f"a commit of {support.README} with the trailers {(TASK, ROLE_OWNER)} and then a commit of "
            f"{support.NOTES} with trailers {AS_ORCHESTRATOR}, in the orchestrator's own call on {TICKET}"
            + (f", which then grafts the second commit onto the HEAD it began with ({support.GRAFTS})"
               if grafted else ""))
    check_support.assert_caught(result, support.README, what=what, action=check_support.FLAGGED)
    check_support.assert_left_as_the_call_left_it(project, left, what)


# --------------------------------------------------------------------------
# (ii) A hidden commit with engineer trailers that changes an acceptance test
# --------------------------------------------------------------------------

@pytest.mark.parametrize("grafted", GRAFTED, ids=GRAFT_IDS)
def test_a_graft_does_not_put_an_engineer_s_change_of_an_acceptance_test_under_a_test_designer_s_trailers(
        project, call, grafted):
    """KPI failure 2, in the orchestrator's own call. An engineer's commit changes an existing acceptance test;
    a test designer's commit then adds another. With the graft the second commit seems to change both, and its
    trailers would allow both."""
    first = support.commit(support.ACCEPTANCE_FILE, AS_ENGINEER)
    second = support.commit(support.NEW_TEST, AS_DESIGNER)
    result, left, hidden = _two_commits(project, call, first, second, ORCHESTRATOR, grafted)
    assert support.changed_paths(project, hidden) == [support.ACCEPTANCE_FILE], (
        f"the fixture is wrong: the first commit changes {support.changed_paths(project, hidden)}"
    )
    what = (f"a commit of {support.ACCEPTANCE_FILE} with trailers {AS_ENGINEER} and then a commit of "
            f"{support.NEW_TEST} with trailers {AS_DESIGNER}, in the orchestrator's own call on {TICKET}"
            + (", which then grafts the second commit onto the HEAD it began with" if grafted else ""))
    check_support.assert_caught(result, support.ACCEPTANCE_FILE, what=what, action=check_support.FLAGGED)
    check_support.assert_not_recorded(result, support.NEW_TEST, what=what)
    check_support.assert_left_as_the_call_left_it(project, left, what)


@pytest.mark.parametrize("grafted", GRAFTED, ids=GRAFT_IDS)
def test_a_graft_does_not_hide_an_engineer_s_undone_change_of_an_acceptance_test_in_its_own_call(project, call,
                                                                                               grafted):
    """KPI failure 2 and DEC-327, in an engineer's call. The engineer's first commit changes an existing
    acceptance test; its second puts the test back and changes its own source file. With the graft the second
    commit seems to change the source file alone, and nothing seems to have touched the test."""
    path = support.ACCEPTANCE_FILE
    first = support.commit(path, AS_ENGINEER, subject="outside")
    second = (f"git checkout -q HEAD~1 -- {path} && " + support.change(support.SOURCE) + " && "
              + support.commit_paths([path, support.SOURCE], AS_ENGINEER, subject="undo, and work"))
    result, left, hidden = _two_commits(project, call, first, second, ENGINEER, grafted)
    assert support.changed_paths(project, hidden) == [path], (
        f"the fixture is wrong: the first commit changes {support.changed_paths(project, hidden)}"
    )
    assert support.ungrafted(project, "diff", "--name-only", "HEAD~2", "HEAD").split() == [support.SOURCE], (
        "the fixture is wrong: the two commits together change something else than the source file"
    )
    what = (f"an engineer's commit of {path} and then one that puts it back and changes {support.SOURCE}, in a "
            f"call of the engineer on {TICKET}"
            + (", which then grafts the second commit onto the HEAD it began with" if grafted else ""))
    check_support.assert_caught(result, path, what=what, action=check_support.FLAGGED)
    check_support.assert_not_recorded(result, support.SOURCE, what=what)
    check_support.assert_left_as_the_call_left_it(project, left, what)


# --------------------------------------------------------------------------
# (iii) The other side: a graft takes nothing from commits inside their own paths
# --------------------------------------------------------------------------

# name: (GOV_ROLE, the first commit: path and trailers, the second commit: path and trailers)
INSIDE = {
    # With the graft the engineer's commit seems to add the acceptance test as well.
    "orchestrator-call-test-designer-commit-then-engineer-commit": (
        ORCHESTRATOR, (support.NEW_TEST, AS_DESIGNER), (support.SOURCE, AS_ENGINEER)),
    "engineer-call-two-commits-inside-its-ticket-s-paths": (
        ENGINEER, (support.SOURCE, AS_ENGINEER), (support.SECOND_SOURCE, AS_ENGINEER)),
}


@pytest.mark.parametrize("case", sorted(INSIDE), ids=sorted(INSIDE))
def test_commits_inside_their_own_paths_stay_silent_with_a_graft_written_in_the_call(project, call, case):
    """KPI success 1. Each of the two commits stays inside the paths of its own trailers; the call then grafts
    the second onto the ``HEAD`` it began with. A graft gives a commit no path it does not change either."""
    role, (first_path, first_trailers), (second_path, second_trailers) = INSIDE[case]
    first = support.commit(first_path, first_trailers)
    second = support.commit(second_path, second_trailers)
    result, left, hidden = _two_commits(project, call, first, second, role, True)
    assert support.changed_paths(project, hidden) == [first_path], (
        f"the fixture is wrong: the first commit changes {support.changed_paths(project, hidden)}"
    )
    assert support.ungrafted(project, "diff-tree", "-r", "--no-commit-id", "--name-only", "HEAD").split() == [
        second_path], "the fixture is wrong: the second commit really changes other paths"
    what = (f"a commit of {first_path} with trailers {first_trailers} and then a commit of {second_path} with "
            f"trailers {second_trailers}, in a call with GOV_ROLE={role!r} on {TICKET}, which then grafts the "
            f"second commit onto the HEAD it began with")
    check_support.assert_silent(result, what)
    check_support.assert_left_as_the_call_left_it(project, left, what)


def test_commits_inside_their_own_paths_stay_silent_with_a_graft_from_before_the_call(project, sandbox, call):
    """KPI success 1. Before the call the history got two commits and a graft that puts the newer of them onto
    the fixture's first commit. The orchestrator's own call then makes a test designer's commit and an
    engineer's, each inside its own paths."""
    support.run(project, sandbox,
                "old=$(git rev-parse HEAD) && "
                + support.commits((support.BOOTSTRAP, (ORCHESTRATOR, support.ORCHESTRATOR_TICKET)),
                                  (support.NOTES, AS_ORCHESTRATOR))
                + " && " + support.graft_newest_onto("$old"))
    before = check_support.git(project, "rev-parse", "HEAD").strip()
    written = support.grafts(project)
    assert len(written) == 1 and written[0].startswith(before + " "), (
        f"the fixture is wrong: {support.GRAFTS} holds {written}"
    )
    command = support.commits((support.NEW_TEST, AS_DESIGNER), (support.SOURCE, AS_ENGINEER))
    result, left = call(project, command, ORCHESTRATOR, TICKET)
    assert support.grafts(project) == written, "the fixture is wrong: the call changed the grafts file"
    assert len(support.new_commits(project, before)) == 2, "the fixture is wrong: the move does not hold two commits"
    what = f"`{command}` in the orchestrator's own call on {TICKET}, with a graft on an earlier commit"
    check_support.assert_silent(result, what)
    check_support.assert_left_as_the_call_left_it(project, left, what)
