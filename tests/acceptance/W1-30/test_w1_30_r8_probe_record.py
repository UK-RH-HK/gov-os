"""The probe record is evidence only if the implementer could not have written it (DEC-487, fourth behaviour).

"It is committed, by a commit with the orchestrator's role; its judgement says the probe passed (a failing
judgement refuses); the probed commit is a commit id, not a name that moves; a commit with the reviewer's role
refuses wherever it lies in the ticket's range."

Every refusal by the probe gate is a finding: exit code 3 (DEC-470). The project of each case is the one of
``test_full_ticket_closes_with_valid_probe`` but for the one thing the case names.

**The words of a judgement (DEC-490).** "The judgement of a probe record is ``pass`` or ``passed`` to be
accepted; ``fail``, ``failed`` or any other value refuses." The cases hold the two accepted words, the two
named refusing words and one word that is neither (``inconclusive``). The suite's fixtures write ``pass``
(``support.probe_record``).
"""

import pytest

import w1_30_support as support

TICKET = "PROJ-prbr"
WBS = "W1-prbr"
FEATURE = "src/example/feature.py"
PROBE = f"docs/probes/{TICKET}/PR-{TICKET}.md"
REVIEWER_ROLE = "Role: independent-auditor"


def _refused_by_the_probe_gate(project, sandbox, interface, *named):
    run = support.run_close(project, sandbox, TICKET)
    text = support.error_text(support.refused(run, interface, support.EXIT_CHECK_FAILED))
    for name in named:
        assert name in text, f"the refusal does not name {name}\n{run.describe()}"
    support.assert_not_closed(project, TICKET)
    return text


@pytest.mark.parametrize("judgement", ["fail", "failed", "inconclusive"])
def test_a_judgement_that_is_neither_pass_nor_passed_refuses(judgement, project, sandbox, interface):
    support.build_ticket(project, TICKET, WBS, profile="FULL")
    project.add_probe(TICKET, judgement=judgement)
    project.commit("the probe record", who=support.ORCHESTRATOR)
    text = _refused_by_the_probe_gate(project, sandbox, interface)
    assert "judgement" in text.lower(), f"the refusal does not name the judgement: {text}"


@pytest.mark.parametrize("judgement", ["pass", "passed"])
def test_a_judgement_of_pass_or_passed_is_accepted(judgement, project, sandbox, interface):
    support.build_ticket(project, TICKET, WBS, profile="FULL")
    project.add_probe(TICKET, judgement=judgement)
    project.commit("the probe record", who=support.ORCHESTRATOR)

    run = support.run_close(project, sandbox, TICKET)

    support.result_of(run, interface)
    assert support.ticket_status(project.root, TICKET) == "closed"


def test_a_probe_record_that_is_written_and_not_committed_refuses(project, sandbox, interface):
    """The record is a file of the working tree only. Whether the close refuses for the tree or for the record,
    it names the file and closes nothing."""
    support.build_ticket(project, TICKET, WBS, profile="FULL")
    assert project.add_probe(TICKET) == PROBE and project.waiting_paths() == [PROBE]

    run = support.run_close(project, sandbox, TICKET)

    envelope = support.envelope_of(run, interface)
    assert envelope["ok"] is False and run.returncode != support.EXIT_OK, \
        f"the ticket closed on a probe record no commit holds\n{run.describe()}"
    assert PROBE in support.error_text(envelope["error"]), f"the refusal does not name {PROBE}\n{run.describe()}"
    support.assert_not_closed(project, TICKET)


def test_a_probe_record_committed_without_the_orchestrators_role_refuses(project, sandbox, interface):
    """The ticket's paths hold the folder of probe records, so W1-50's judgement passes the engineer's commit
    of the record: the only thing wrong is who committed it."""
    support.build_ticket(project, TICKET, WBS, profile="FULL", allowed_paths=["src/example/**", "docs/probes/**"])
    project.add_probe(TICKET)
    commit = project.commit("the probe record", who=support.IMPLEMENTER, trailers=support.trailers_of(TICKET))
    support.checkpointed(project, TICKET)
    assert support.judged_by_w1_50(project, sandbox, [commit]) == [], \
        "the fixture is wrong: W1-50's judgement has a finding, so the probe gate is not the only reason"
    text = _refused_by_the_probe_gate(project, sandbox, interface)
    assert "orchestrator" in text.lower(), f"the refusal does not say who must commit the record: {text}"


@pytest.mark.parametrize("name", ["HEAD", "main"])
def test_a_probed_commit_given_as_a_name_that_moves_refuses(name, project, sandbox, interface):
    """The record names the head by name; the engineer's commit that follows moves the name with it."""
    support.build_ticket(project, TICKET, WBS, profile="FULL")
    project.add_probe(TICKET, probed_commit=name)
    project.commit("the probe record", who=support.ORCHESTRATOR)
    support.engineer_commit(project, TICKET, {FEATURE: "# rewritten after the probe\n"})
    support.checkpointed(project, TICKET)
    _refused_by_the_probe_gate(project, sandbox, interface)


def test_a_commit_with_the_reviewers_role_and_no_task_before_the_probed_commit_refuses(project, sandbox, interface):
    """The reviewer's commit names no ticket and adds a source file; the probe record names a later commit."""
    support.build_ticket(project, TICKET, WBS, profile="FULL")
    project.write("src/example/reviewed.py", "# written by the reviewer\n")
    commit = project.commit("a fix found while probing", who=support.REVIEWER, trailers=(REVIEWER_ROLE,), exact=True)
    support.checkpointed(project, TICKET)
    project.add_probe(TICKET)
    project.commit("the probe record", who=support.ORCHESTRATOR)
    assert commit not in support.ticket_commits(project.root, TICKET)
    _refused_by_the_probe_gate(project, sandbox, interface, commit[:7])
