"""Round 13, piece 1: a merge that brings exactly the probed code is not "after" the probed commit (DEC-505).

DEC-498: "The fresh reviewer probes the ticket's final code before the orchestrator merges it." So the probed
commit is the head of the ticket's branch, and the orchestrator's merge commit follows it. DEC-505: "The probe
gate is changed [...] so that a merge bringing exactly the probed code no longer counts as 'after' the probed
commit."

**What "exactly the probed code" means here (README, round 13, settlement 24), the stricter reading.** A commit
of the ticket that follows the probed commit does not count as "after" it when all of this holds:

- it is a merge commit, and the probed commit itself is one of its parents other than the first (the head that
  was merged is the probed commit, not a later one);
- every path the merge brings to its first parent, outside ``tests/`` and ``docs/probes/``, is at the merge
  byte for byte what it is at the probed commit (a path the probed commit does not hold is not there at the
  merge either).

Which other commits of the ticket after the probed one refuse is DEC-581's rule since round 14
(``test_w1_30_r14_probe_later_commits.py``): those that change a file inside the ticket's allowed paths or in
its acceptance tests, a merge that is not that merge among them. The second condition above is read with
that rule's paths since then (README, round 14, settlement 34). One case of this file was rewritten to it
(``test_a_commit_of_the_ticket_after_the_merge_outside_its_code_does_not_refuse``); the others stand.

The projects: the ticket's work is made on a branch (``work``), probed at its head, and merged into ``main`` by
the orchestrator with a merge commit that carries the ticket's trailers. The probe record is committed after the
merge, by the orchestrator, as in this repository.
"""

import pytest

import w1_30_support as support

TICKET = "PROJ-prmg"
WBS = "W1-prmg"
FEATURE = "src/example/feature.py"
BRANCH = "work"
MERGE_TRAILERS = support.trailers_of(TICKET, role="orchestrator")
# A file of the orchestrator's outside the ticket's paths, as this repository's residual notes are; no governance file,
# so that the governance checks of a close are not run for it.
NOTES = "docs/residuals.md"


def _work_on_a_branch(project):
    """The ticket's work on its branch, by the roles that may do it; ``main`` stays where it was. Returns the
    head of the branch."""
    support.git(project.root, "checkout", "-q", "-b", BRANCH)
    project.add_ticket(TICKET, WBS, profile="FULL")
    project.add_passing_test(WBS)
    project.write(FEATURE, "# feature\n")
    return project.commit("implement", who=support.IMPLEMENTER, trailers=support.trailers_of(TICKET))


def _main_goes_on(project):
    """A commit of the owner on ``main`` outside the ticket's work, so that the merge is no fast-forward in
    any sense: its first parent holds what the branch never saw."""
    support.git(project.root, "checkout", "-q", "main")
    project.write("docs/elsewhere.md", "# Something else\n")
    project.commit("something else", who=support.OWNER)
    support.git(project.root, "checkout", "-q", BRANCH)


def _merge(project, head=BRANCH, edit=None):
    """The orchestrator merges ``head`` into ``main`` with a merge commit that carries the ticket's trailers.
    ``edit`` (``{path: text}``) is written into the merge itself, before it is committed. Returns the merge."""
    support.git(project.root, "checkout", "-q", "main")
    message = "merge the ticket's branch\n\n" + "\n".join(MERGE_TRAILERS) + "\n"
    if edit is None:
        support.git(project.root, "merge", "-q", "--no-ff", "--no-gpg-sign", "-m", message, head,
                    who=support.ORCHESTRATOR)
    else:
        support.git(project.root, "merge", "-q", "--no-ff", "--no-commit", head, who=support.ORCHESTRATOR)
        for rel, text in edit.items():
            project.write(rel, text)
        support.git(project.root, "add", "-A", who=support.ORCHESTRATOR)
        support.git(project.root, "commit", "-q", "--no-gpg-sign", "-m", message, who=support.ORCHESTRATOR)
    merge = support.head_of(project)
    parents = support.git(project.root, "rev-list", "--parents", "-n", "1", merge).split()
    assert len(parents) == 3, "the fixture is wrong: HEAD is not a merge commit"
    assert merge in support.ticket_commits(project.root, TICKET), \
        "the fixture is wrong: the merge commit does not carry the ticket's trailers"
    return merge


def _recorded_and_checkpointed(project, probed):
    """The orchestrator's probe record of ``probed`` and its checkpoint, committed after everything else."""
    project.add_probe(TICKET, probed_commit=probed)
    project.commit("the probe record", who=support.ORCHESTRATOR)
    support.checkpointed(project, TICKET)


def _refused_by_the_probe_gate(project, sandbox, interface, *one_of):
    """Refused with a finding (exit code 3) that says "probe" and names one of the commits ``one_of``."""
    run = support.run_close(project, sandbox, TICKET)
    text = support.error_text(support.refused(run, interface, support.EXIT_CHECK_FAILED))
    assert "probe" in text.lower(), f"the refusal is not the probe gate's\n{run.describe()}"
    assert any(commit[:7] in text for commit in one_of), \
        f"the refusal names none of {[commit[:7] for commit in one_of]}\n{run.describe()}"
    support.assert_not_closed(project, TICKET)


# --------------------------------------------------------------------------
# New: the merge of exactly the probed code
# --------------------------------------------------------------------------

@pytest.mark.parametrize("main_went_on", [False, True], ids=["main stayed", "main went on"])
def test_a_merge_that_brings_exactly_the_probed_code_does_not_refuse(main_went_on, project, sandbox, interface):
    """The branch is probed at its head and merged as it is; the probe record follows the merge."""
    probed = _work_on_a_branch(project)
    if main_went_on:
        _main_goes_on(project)
    merge = _merge(project)
    _recorded_and_checkpointed(project, probed)
    assert support.git(project.root, "diff", "--name-only", probed, merge, "--", "src").strip() == "", \
        "the fixture is wrong: the merge's code is not the probed code"

    run = support.run_close(project, sandbox, TICKET)

    support.result_of(run, interface)
    assert support.ticket_status(project.root, TICKET) == "closed"
    record = support.the_close_record(project, TICKET)
    assert merge in [entry["commit"] for entry in record["commits"]], \
        "the close record does not list the merge commit among the ticket's commits"


# --------------------------------------------------------------------------
# As today: what still refuses
# --------------------------------------------------------------------------

def test_a_commit_after_the_merge_that_changes_the_tickets_code_refuses(project, sandbox, interface):
    """The merge is the merge of the probed code; the engineer's commit after it is not probed."""
    probed = _work_on_a_branch(project)
    _merge(project)
    later = support.engineer_commit(project, TICKET, {FEATURE: "# rewritten after the merge\n"})
    _recorded_and_checkpointed(project, probed)
    _refused_by_the_probe_gate(project, sandbox, interface, later)


@pytest.mark.parametrize("edit", [{FEATURE: "# changed in the merge\n"},
                                  {"src/example/added.py": "# added in the merge\n"}],
                         ids=["a probed file changed in the merge", "a file added in the merge"])
def test_a_merge_whose_result_is_not_the_probed_code_refuses(edit, project, sandbox, interface):
    """What a conflict resolution or an edit made in the merge leaves: the head merged is the probed commit,
    and the merge holds, on the ticket's paths, what the probed commit does not."""
    probed = _work_on_a_branch(project)
    merge = _merge(project, edit=edit)
    _recorded_and_checkpointed(project, probed)
    assert support.git(project.root, "diff", "--name-only", probed, merge, "--", "src").strip() != "", \
        "the fixture is wrong: the merge's code is the probed code"
    _refused_by_the_probe_gate(project, sandbox, interface, merge)


def test_a_merge_of_a_later_head_that_changed_the_code_refuses(project, sandbox, interface):
    """The engineer goes on after the probe; the orchestrator merges that later head."""
    probed = _work_on_a_branch(project)
    later = support.engineer_commit(project, TICKET, {FEATURE: "# rewritten after the probe\n"})
    merge = _merge(project)
    _recorded_and_checkpointed(project, probed)
    _refused_by_the_probe_gate(project, sandbox, interface, later, merge)


def test_a_merge_of_a_later_head_that_changed_only_tests_refuses(project, sandbox, interface):
    """Settlement 24, the stricter reading: the head that was merged is not the probed commit, so the merge is
    not the merge of the probed commit, although the code it brings is the probed code."""
    probed = _work_on_a_branch(project)
    project.add_passing_test(WBS, name="test_more")
    project.commit("one more acceptance test", who=support.TEST_DESIGNER,
                   trailers=support.trailers_of(TICKET, role="independent-test-designer"))
    merge = _merge(project)
    _recorded_and_checkpointed(project, probed)
    assert support.git(project.root, "diff", "--name-only", probed, merge, "--", "src").strip() == ""
    _refused_by_the_probe_gate(project, sandbox, interface, merge)


def test_a_commit_of_the_ticket_after_the_merge_outside_its_code_does_not_refuse(project, sandbox, interface):
    """Package P-1 of round 13, answered by the owner (DEC-581): the orchestrator's notes, committed after the
    merge with the ticket named, change a file outside the ticket's allowed paths and outside its acceptance
    tests. The gate does not refuse for it; the ticket closes, and the close record lists the commit.

    Until round 14 this case held the stricter reading meanwhile (the same commit refused) under the name
    ``test_a_commit_of_the_ticket_after_the_merge_outside_its_code_refuses``."""
    probed = _work_on_a_branch(project)
    _merge(project)
    project.write(NOTES, "# Residuals of the ticket\n")
    notes = project.commit("residual notes", who=support.ORCHESTRATOR, trailers=MERGE_TRAILERS, exact=True)
    _recorded_and_checkpointed(project, probed)
    assert notes in support.ticket_commits(project.root, TICKET)

    run = support.run_close(project, sandbox, TICKET)

    support.result_of(run, interface)
    assert support.ticket_status(project.root, TICKET) == "closed"
    record = support.the_close_record(project, TICKET)
    assert notes in [entry["commit"] for entry in record["commits"]], \
        "the close record does not list the notes commit among the ticket's commits"


def test_the_orchestrators_notes_after_the_merge_that_name_no_ticket_do_not_refuse(project, sandbox, interface):
    """As today: the same notes in a commit that names no ticket are no commit of the ticket and change nothing
    inside its paths. With the merge of the probed code no longer "after", such a project closes."""
    probed = _work_on_a_branch(project)
    _merge(project)
    project.write(NOTES, "# Residuals of the ticket\n")
    project.commit("residual notes", who=support.ORCHESTRATOR)
    _recorded_and_checkpointed(project, probed)

    run = support.run_close(project, sandbox, TICKET)

    support.result_of(run, interface)
    assert support.ticket_status(project.root, TICKET) == "closed"
