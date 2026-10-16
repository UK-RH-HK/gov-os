"""KPI 2 and failure KPI 8: a merge of the integration branch into a ticket branch, in DEC-436's merge form.

KPI 2 [W2-M165]: "A merge of the integration branch into a ticket branch in DEC-436's merge form (Task: and Role:)
passes the trailer gate." DEC-436: "A lead merges ``w1/integrate`` into its branch in one command that commits."
W1-42's case (DEC-717): seven such merges, each carrying ``Task:`` and ``Role:`` only, each refused the close
with ``TRAILER_MISSING``.

Failure KPI 8: "A merge that adds its own change outside the merged side still refuses."

The project: ``main`` is the integration branch. ``PROJ-mrge`` is created there and worked on its branch
``work``; meanwhile another ticket, ``PROJ-othr``, lands its own work on ``main`` (outside this ticket's paths,
every trailer present). The lead merges ``main`` into ``work`` with one command that commits, the merge
carrying the merge form; the close runs at the head of ``work``.
"""

import pytest

import w2_01_support as support

TICKET, WBS = "PROJ-mrge", "W1-mrge"
OTHER, OTHER_WBS = "PROJ-othr", "W1-othr"
FEATURE = "src/example/feature.py"
BRANCH = "work"


def _branch_with_work(project):
    support.create_ticket(project, TICKET, WBS)
    project.checkout(BRANCH, create=True)
    support.engineer_commit(project, TICKET, {FEATURE: "# feature\n"})


def _integration_goes_on(project, number):
    """Another ticket's work lands on ``main`` (its own ticket, tests and code, outside this ticket's paths)."""
    project.checkout("main")
    if number == 1:
        support.create_ticket(project, OTHER, OTHER_WBS, allowed_paths=("src/other/**",))
    support.engineer_commit(project, OTHER, {f"src/other/part{number}.py": f"# part {number}\n"},
                            trailers=support.trailers_of(OTHER))
    project.checkout(BRANCH)


def _merged_in(project, edit=None):
    return project.merge("main", support.merge_form(TICKET), edit=edit, message="merge w1/integrate into the branch")


@pytest.mark.parametrize("merges", (1, 2), ids=("one merge", "two merges"))
def test_a_merge_of_the_integration_branch_in_the_merge_form_passes_the_trailer_gate(merges, project, sandbox,
                                                                                     interface):
    _branch_with_work(project)
    made = []
    for number in range(1, merges + 1):
        _integration_goes_on(project, number)
        made.append(_merged_in(project))
    support.checkpointed(project, TICKET)

    run = support.run_close(project, sandbox, TICKET)

    error = run.envelope().get("error") or {}
    for merge in made:
        assert not support.statements_naming(error, merge), \
            f"the merge {merge[:12]} in the merge form is judged\n{run.describe()}"
    support.closed(run, interface)
    record = support.base.the_close_record(project, TICKET)
    listed = [entry.get("commit") for entry in record.get("commits", [])]
    assert all(merge in listed for merge in made), \
        f"the close record does not list the merges among the ticket's commits: {listed}"


def test_the_merge_form_after_more_work_on_the_branch_still_passes(project, sandbox, interface):
    """The branch goes on after the merge, every commit of its own carrying every trailer."""
    _branch_with_work(project)
    _integration_goes_on(project, 1)
    merge = _merged_in(project)
    support.engineer_commit(project, TICKET, {FEATURE: "# feature, after the merge\n"})
    support.checkpointed(project, TICKET)

    run = support.run_close(project, sandbox, TICKET)

    assert not support.statements_naming(run.envelope().get("error") or {}, merge), \
        f"the merge {merge[:12]} in the merge form is judged\n{run.describe()}"
    support.closed(run, interface)


# --------------------------------------------------------------------------
# Failure KPI 8: a merge that adds its own change still refuses
# --------------------------------------------------------------------------

OWN_CHANGES = {
    "a file added inside the ticket's paths": {"src/example/extra.py": "# added in the merge\n"},
    "a file changed outside both sides": {"README.md": "# A project, changed in the merge\n"},
    "a file of the integration side changed": {"src/other/part1.py": "# part 1, changed in the merge\n"},
}


@pytest.mark.parametrize("own", tuple(OWN_CHANGES))
def test_a_merge_in_the_merge_form_that_adds_its_own_change_still_refuses(own, project, sandbox, interface):
    _branch_with_work(project)
    _integration_goes_on(project, 1)
    merge = _merged_in(project, edit=OWN_CHANGES[own])
    assert support.git(project, "diff", "--name-only", f"{merge}^1", merge).strip(), "the fixture is wrong"
    support.checkpointed(project, TICKET)

    run = support.run_close(project, sandbox, TICKET)

    error = support.refused(run, interface)
    assert support.statements_naming(error, merge), \
        f"the merge {merge[:12]} with its own change ({own}) is not named in the refusal\n{run.describe()}"
    support.base.assert_not_closed(project, TICKET)
