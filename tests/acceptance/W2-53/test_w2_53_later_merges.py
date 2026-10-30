"""KPI 1, 2 and 4, failure KPI 1 and 2: every later merge that holds the probed commit is measured against git's
own merge of its parents, on the probed paths.

KPI 1 [DEC-750, DEC-754]: "After a FULL ticket's probed commit, every later merge that holds it refuses, naming
the merge, whatever task it names (or none), when a probed path (the ticket's allowed paths, its acceptance
folder, its ticket file) at the merge is not what git's own merge of its parents gives, a removal or a return to
a version from before the ticket included; on the integration branch, inward on the ticket's branch, and for an
octopus merge."

KPI 2 [DEC-754, P-5 (c)]: "A later merge that takes another ticket's whole version of a probed file is measured
the same way, against git's own merge of its parents."

KPI 4 [W2-H047, W2-M202]: "A merge whose probed paths are what git's own merge of its parents gives, and another
ticket's merge holding the probed commit on neither side, pass as before; W2-01's acceptance cases stay green."

Failure KPI 1: "An acceptance test added on the ticket's branch before the probe and removed or changed by a later
merge refuses the close." Failure KPI 2: "A merge whose own merge git cannot compute, or cannot read, is judged
against the probed code and never passes by default."

The layout is round 4's (``docs/probes/DAEO-g0ip/PR-DAEO-g0ip-round-4.md``, finding 1): ``main`` holds the
ticket's files as they were before it (``src/example/feature.py``, ``src/example/shared.py``). Another ticket,
``PROJ-othr``, is created there and worked on its own branch ``other`` before the ticket's merge-back. FULL ticket
``PROJ-lmrg`` is created on ``main`` and worked on ``work``: the test designer adds an acceptance case, the
engineer changes the two files and adds ``src/example/added.py``; that head is probed. The ticket is merged back
with the probed code unchanged; a later merge then brings ``other``. The probe record and the checkpoint follow;
the close runs on the branch the case names.

Every merge here that is not a plain ``git merge`` carries every trailer, so that the probe gate is the only gate
with a reason (W2-01's KPI 2 holds the merge form on its own).
"""

import pytest

import w2_53_support as support

TICKET, WBS = "PROJ-lmrg", "W1-lmrg"
OTHER, OTHER_WBS = "PROJ-othr", "W1-othr"
THIRD, THIRD_WBS = "PROJ-thrd", "W1-thrd"
BRANCH, OTHER_BRANCH, THIRD_BRANCH = "work", "other", "third"

FEATURE = "src/example/feature.py"
FEATURE_BEFORE = "# the feature before the ticket\n"
FEATURE_TICKET = "# the feature, as the ticket made it\n"
ADDED = "src/example/added.py"
SHARED = "src/example/shared.py"
SHARED_BEFORE = "one\ntwo\nthree\n"
SHARED_TICKET = "ONE (the ticket)\ntwo\nthree\n"
SHARED_OTHER_LINE_THREE = "one\ntwo\nTHREE (the other ticket)\n"
SHARED_BOTH = "ONE (the ticket)\ntwo\nTHREE (the other ticket)\n"
SHARED_OTHER_LINE_ONE = "ONE (the other ticket)\ntwo\nthree\n"
MORE_TEST = f"tests/acceptance/{WBS}/test_more.py"
MORE_TEXT = "def test_more():\n    assert 1 + 1 == 2\n"

MERGE_TRAILERS = support.trailers_of(TICKET, role="orchestrator")
OTHERS_TRAILERS = support.trailers_of(OTHER, role="orchestrator")
PLAIN_MESSAGE = f"Merge branch '{OTHER_BRANCH}'"
OTHERS_PATHS = ("src/other/**", "src/example/**")


def _before_the_ticket(project):
    """``main`` holds two of the ticket's files as they are before it."""
    project.write(FEATURE, FEATURE_BEFORE)
    project.write(SHARED, SHARED_BEFORE)
    support.setup_commit(project, "the code before the ticket")


def _other_ticket(project, files=None, ticket=OTHER, wbs=OTHER_WBS, branch=OTHER_BRANCH):
    """Another ticket created on ``main`` and worked on its own branch, cut from ``main`` as it is now. Ends on
    ``main``."""
    project.checkout("main")
    support.create_ticket_named(project, ticket, wbs, OTHERS_PATHS, f"test_{branch}_ticket")
    project.checkout(branch, create=True)
    support.engineer_commit(project, ticket, files or {f"src/other/{branch}.py": f"# {branch}\n"},
                            trailers=support.trailers_of(ticket))
    project.checkout("main")


def _probed(project):
    """The ticket created on ``main``; on its branch the test designer adds a case and the engineer does the work.
    Returns the probed commit; ends on the ticket's branch."""
    project.checkout("main")
    support.create_ticket(project, TICKET, WBS, profile="FULL")
    project.checkout(BRANCH, create=True)
    project.write(MORE_TEST, MORE_TEXT)
    project.commit("another acceptance case", who=support.TEST_DESIGNER,
                   trailers=support.trailers_of(TICKET, role="independent-test-designer"), exact=True)
    return support.engineer_commit(project, TICKET, {FEATURE: FEATURE_TICKET, SHARED: SHARED_TICKET,
                                                     ADDED: "# added by the ticket\n"})


def _merged_back(project):
    project.checkout("main")
    return project.merge(BRANCH, MERGE_TRAILERS, message="merge the ticket's branch")


def _recorded(project, probed):
    support.probe_recorded(project, TICKET, probed)
    support.checkpointed(project, TICKET)


def _refused_naming(project, sandbox, interface, merge, what):
    run = support.run_close(project, sandbox, TICKET)
    error = support.refused(run, interface)
    assert support.probe_gate_names(error, merge), \
        f"the probe gate does not refuse the merge {merge[:12]} ({what})\n{run.describe()}"
    support.base.assert_not_closed(project, TICKET)


def _closes(project, sandbox, interface, what):
    run = support.run_close(project, sandbox, TICKET)
    assert not support.probe_statements(run.envelope().get("error") or {}), \
        f"the probe gate refuses {what}\n{run.describe()}"
    support.closed(run, interface)


def _not_gits_own_merge(project, merge, rel):
    first, second = support.parents_of(project, merge)
    assert support.content_at(project, merge, rel) != support.own_merge_content(project, first, second, rel), \
        f"the fixture is wrong: {rel} at the merge is what git's own merge of its parents gives"


# --------------------------------------------------------------------------
# KPI 1 and failure KPI 1: round 4's finding 1 and 2, on the integration branch
# --------------------------------------------------------------------------

WAYS = {
    "a probed file the ticket added removed": (dict(remove=(ADDED,)), ADDED),
    "a probed file set back to its text from before the ticket": (dict(edit={FEATURE: FEATURE_BEFORE}), FEATURE),
    "an acceptance test added on the branch removed": (dict(remove=(MORE_TEST,)), MORE_TEST),
    "an acceptance test added on the branch changed": (dict(edit={MORE_TEST: "def test_more():\n    pass\n"}),
                                                       MORE_TEST),
}
NAMES = {"another ticket's task": OTHERS_TRAILERS, "no task": ()}
ON_MAIN = ([(way, "another ticket's task") for way in WAYS]
           + [("a probed file set back to its text from before the ticket", "no task")])


@pytest.mark.parametrize("way, names", ON_MAIN, ids=[f"{names}-{way}" for way, names in ON_MAIN])
def test_a_later_merge_on_the_integration_branch_that_is_not_gits_own_merge_refuses_and_names_it(
        way, names, project, sandbox, interface):
    """After the merge-back, the other ticket's branch (cut before it) is merged into ``main``; the merge holds the
    probed commit on its first side and drops or reverts a probed path to the other side's version."""
    _before_the_ticket(project)
    _other_ticket(project)
    probed = _probed(project)
    _merged_back(project)
    project.checkout("main")
    how, rel = WAYS[way]
    later = support.merge_by_hand(project, OTHER_BRANCH, NAMES[names],
                                  message=PLAIN_MESSAGE if names == "no task" else "merge the other ticket's branch",
                                  **how)
    _recorded(project, probed)
    first, second = support.parents_of(project, later)
    assert support.holds(project, probed, first) and not support.holds(project, probed, second), \
        "the fixture is wrong: the later merge does not hold the probed commit on its first side only"
    _not_gits_own_merge(project, later, rel)

    _refused_naming(project, sandbox, interface, later, f"{way}, naming {names}")


# --------------------------------------------------------------------------
# KPI 1: inward on the ticket's branch
# --------------------------------------------------------------------------

INWARD = ("a probed file the ticket added removed", "an acceptance test added on the branch removed")


@pytest.mark.parametrize("way", INWARD)
def test_a_later_merge_into_the_tickets_branch_that_is_not_gits_own_merge_refuses_and_names_it(
        way, project, sandbox, interface):
    """After the probe, the other ticket's branch is merged into the ticket's branch, naming that ticket's task;
    the close runs at the head of the ticket's branch."""
    _before_the_ticket(project)
    _other_ticket(project)
    probed = _probed(project)
    how, rel = WAYS[way]
    inward = support.merge_by_hand(project, OTHER_BRANCH, OTHERS_TRAILERS,
                                   message="merge the other ticket's branch into the ticket's", **how)
    _recorded(project, probed)
    assert support.parents_of(project, inward)[0] == probed, "the fixture is wrong: the merge is not on the probe"
    _not_gits_own_merge(project, inward, rel)

    _refused_naming(project, sandbox, interface, inward, f"{way}, inward")


# --------------------------------------------------------------------------
# KPI 1: an octopus merge
# --------------------------------------------------------------------------

OCTOPUSES = ("a later merge of two other branches", "the merge-back with another branch")


@pytest.mark.parametrize("which", OCTOPUSES)
def test_an_octopus_merge_that_is_not_gits_own_merge_refuses_and_names_it(which, project, sandbox, interface):
    _before_the_ticket(project)
    _other_ticket(project)
    if which == OCTOPUSES[0]:
        _other_ticket(project, ticket=THIRD, wbs=THIRD_WBS, branch=THIRD_BRANCH)
    probed = _probed(project)
    project.checkout("main")
    if which == OCTOPUSES[0]:
        _merged_back(project)
        merge = support.octopus(project, [OTHER_BRANCH, THIRD_BRANCH], OTHERS_TRAILERS,
                                edit={FEATURE: FEATURE_BEFORE}, message="merge two other branches")
    else:
        merge = support.octopus(project, [BRANCH, OTHER_BRANCH], OTHERS_TRAILERS, remove=(ADDED,),
                                message="merge the ticket's branch and the other ticket's")
    _recorded(project, probed)
    assert support.holds(project, probed, merge), "the fixture is wrong: the octopus does not hold the probed commit"

    _refused_naming(project, sandbox, interface, merge, which)


# --------------------------------------------------------------------------
# KPI 4: a later merge that is git's own merge of its parents passes
# --------------------------------------------------------------------------

PASSES = ("on the integration branch", "into the ticket's branch", "an octopus on the integration branch",
          "on the integration branch, both sides having changed one probed file")


@pytest.mark.parametrize("layout", PASSES)
def test_a_later_merge_that_is_gits_own_merge_of_its_parents_closes(layout, project, sandbox, interface):
    """The twins of the refused cases: the same later merges, made by git without a hand change. The other side
    holds the ticket's files as they were before it; git's own merge keeps the ticket's."""
    _before_the_ticket(project)
    both = layout == PASSES[3]
    _other_ticket(project, files={SHARED: SHARED_OTHER_LINE_THREE} if both else None)
    if layout == PASSES[2]:
        _other_ticket(project, ticket=THIRD, wbs=THIRD_WBS, branch=THIRD_BRANCH)
    probed = _probed(project)
    if layout == PASSES[1]:
        later = support.merge_by_hand(project, OTHER_BRANCH, OTHERS_TRAILERS,
                                      message="merge the other ticket's branch into the ticket's")
    else:
        _merged_back(project)
        project.checkout("main")
        if layout == PASSES[2]:
            later = support.octopus(project, [OTHER_BRANCH, THIRD_BRANCH], OTHERS_TRAILERS,
                                    message="merge two other branches")
        else:
            later = support.merge_by_hand(project, OTHER_BRANCH, OTHERS_TRAILERS,
                                          message="merge the other ticket's branch")
    _recorded(project, probed)
    assert support.holds(project, probed, later), "the fixture is wrong: the later merge does not hold the probe"
    expected = SHARED_BOTH if both else SHARED_TICKET
    assert support.content_at(project, later, SHARED) == expected, "the fixture is wrong: git's merge differs"
    for rel in (FEATURE, ADDED, MORE_TEST):
        assert support.content_at(project, later, rel) == support.content_at(project, probed, rel), \
            f"the fixture is wrong: {rel} changed in the later merge"

    _closes(project, sandbox, interface, f"the later merge {later[:12]} that is git's own merge ({layout})")


# --------------------------------------------------------------------------
# KPI 2 (P-5 (c)): another ticket's whole version of a probed file
# --------------------------------------------------------------------------

def test_a_later_merge_taking_another_tickets_whole_version_refuses_where_gits_merge_gives_other_text(
        project, sandbox, interface):
    """The other ticket (cut before the merge-back) changed line three of the shared file; the ticket changed line
    one. Git's own merge holds both lines; the later merge takes the other ticket's whole file."""
    _before_the_ticket(project)
    _other_ticket(project, files={SHARED: SHARED_OTHER_LINE_THREE})
    probed = _probed(project)
    _merged_back(project)
    project.checkout("main")
    later = support.merge_by_hand(project, OTHER_BRANCH, OTHERS_TRAILERS, edit={SHARED: SHARED_OTHER_LINE_THREE},
                                  message="merge the other ticket's branch, its version of the shared file")
    _recorded(project, probed)
    first, second = support.parents_of(project, later)
    assert support.own_merge_content(project, first, second, SHARED) == SHARED_BOTH, \
        "the fixture is wrong: git's own merge does not hold both lines"

    _refused_naming(project, sandbox, interface, later, "another ticket's whole version of a probed file")


def test_a_merge_into_the_tickets_branch_taking_another_tickets_whole_version_refuses(project, sandbox, interface):
    """The same, from the other side: the other ticket's branch is merged into the ticket's after the probe."""
    _before_the_ticket(project)
    _other_ticket(project, files={SHARED: SHARED_OTHER_LINE_THREE})
    probed = _probed(project)
    inward = support.merge_by_hand(project, OTHER_BRANCH, OTHERS_TRAILERS, edit={SHARED: SHARED_OTHER_LINE_THREE},
                                   message="merge the other ticket's branch into the ticket's, its version")
    _recorded(project, probed)
    _not_gits_own_merge(project, inward, SHARED)

    _refused_naming(project, sandbox, interface, inward, "another ticket's whole version, inward")


def test_a_later_merge_taking_another_tickets_whole_version_closes_where_gits_merge_gives_the_same(
        project, sandbox, interface):
    """The other ticket is cut from ``main`` after the merge-back, so it holds the ticket's line one; it changes
    line three, and its whole version is what git's own merge gives. The other ticket's own commit is that
    ticket's (DEC-490)."""
    _before_the_ticket(project)
    probed = _probed(project)
    _merged_back(project)
    _other_ticket(project, files={SHARED: SHARED_BOTH})
    later = support.merge_by_hand(project, OTHER_BRANCH, OTHERS_TRAILERS, message="merge the other ticket's branch")
    _recorded(project, probed)
    first, second = support.parents_of(project, later)
    assert support.content_at(project, later, SHARED) == support.content_at(project, second, SHARED) == \
        support.own_merge_content(project, first, second, SHARED) == SHARED_BOTH, \
        "the fixture is wrong: the merge does not take the other ticket's whole version, or git's merge differs"

    _closes(project, sandbox, interface, f"the later merge {later[:12]} whose shared file is git's own merge")


# --------------------------------------------------------------------------
# Failure KPI 2: a merge git cannot compute, or cannot read
# --------------------------------------------------------------------------

RESOLUTIONS = {"to the other ticket's version": SHARED_OTHER_LINE_ONE, "to the probed version": SHARED_TICKET}


@pytest.mark.parametrize("resolution", tuple(RESOLUTIONS))
def test_a_later_merge_whose_parents_conflict_on_a_probed_file_is_judged_against_the_probed_code(
        resolution, project, sandbox, interface):
    """Both the ticket and the other ticket (cut before the merge-back) changed line one of the shared file: git's
    own merge has a conflict, so the merge is judged against the probed code. Resolved to the other side, it
    refuses; resolved to the probed text, it is the probed code and closes."""
    _before_the_ticket(project)
    _other_ticket(project, files={SHARED: SHARED_OTHER_LINE_ONE})
    probed = _probed(project)
    _merged_back(project)
    project.checkout("main")
    later = support.merge_resolving(project, OTHER_BRANCH, OTHERS_TRAILERS, {SHARED: RESOLUTIONS[resolution]},
                                    message="merge the other ticket's branch, a conflict resolved")
    _recorded(project, probed)

    if resolution == "to the other ticket's version":
        _refused_naming(project, sandbox, interface, later, "a conflict resolved to the other side")
    else:
        _closes(project, sandbox, interface, f"the merge {later[:12]} resolved to the probed code")


def test_a_later_merge_whose_parents_git_cannot_read_never_passes(project, sandbox, interface):
    """Git's own merge of the later merge's parents needs the other side's version of the shared file, and that
    object is gone from the repository: the merge is judged against the probed code (it is not), and the close
    does not pass."""
    _before_the_ticket(project)
    _other_ticket(project, files={SHARED: SHARED_OTHER_LINE_THREE})
    probed = _probed(project)
    _merged_back(project)
    project.checkout("main")
    later = support.merge_by_hand(project, OTHER_BRANCH, OTHERS_TRAILERS, message="merge the other ticket's branch")
    _recorded(project, probed)
    assert support.content_at(project, later, SHARED) == SHARED_BOTH, "the fixture is wrong: git's merge differs"
    blob = support.git(project, "rev-parse", f"{OTHER_BRANCH}:{SHARED}").strip()
    loose = project.root / ".git" / "objects" / blob[:2] / blob[2:]
    assert loose.is_file(), "the fixture is wrong: the object is not a loose object"
    loose.unlink()
    assert support.own_merge_unreadable(project, *support.parents_of(project, later)), \
        "the fixture is wrong: git can still compute its own merge of the parents"

    run = support.run_close(project, sandbox, TICKET)

    envelope = support.base.envelope_of(run, interface)
    assert envelope["ok"] is False and run.returncode != support.EXIT_OK, \
        f"the close passes a merge whose parents git cannot read\n{run.describe()}"
    support.base.assert_not_closed(project, TICKET)
