"""KPI 3 and failure KPI 3: decision records measured by their decision [DEC-896 item 1].

KPI 3: "A decision-record commit that changes only governance records (the register, the plan files, the prompts,
the briefs, governance/project/orchestration/, the path map) and names an ACCEPTED decision counts as measured for
the work-without-a-task gate; a decision-record commit that names no ACCEPTED decision, or changes code, tests or
the kernel, still counts as unmeasured."

Failure KPI 3: "A decision-record commit outside an ACCEPTED decision counted as measured."

The shape is W2-58's refused close (I2 F13): its allowed paths name the path map, and decision-record commits
(``Task: decision-record``, a ``Task:`` that names no ticket, DEC-500) changed the path map in its range, so the
close refused ``WORK_WITHOUT_TASK`` (DEC-490). A decision-record commit here is written as this repository writes
them: its subject names the decision ("Decision record DEC-…"), with ``Implements: DEC-…`` in its final trailer
block beside ``Task: decision-record`` and ``Role: owner``; it adds the decision's entry to the register.
"""

import pytest

import w2_07_support as support

TICKET, WBS = "PROJ-dcrd", "W9-dcrd"
WORK_WITHOUT_TASK = "WORK_WITHOUT_TASK"
ALLOWED = ("src/example/**", support.PATH_MAP_REL)


def _ticket_naming_the_path_map(project):
    support.create_ticket(project, TICKET, WBS, allowed_paths=ALLOWED)
    support.work(project, TICKET, {"src/example/feature.py": "# feature\n"})


def _decision_record(project, decision=None, status=support.OWNER_ACCEPTED, also=None):
    """The owner's decision-record commit in the ticket's range: the path map gains the close's time limit (a
    path of the ticket), and with ``decision`` the register gains its entry (``status``) and the commit names it.
    ``also`` (``{path: text}``) is written in the same commit. Returns the commit."""
    project.settings["close_timeout"] = 900
    project.write(support.PATH_MAP_REL, support.path_map_text(project.settings))
    if decision is not None:
        project.register_entry(decision, status, "The close's time limit is 900 seconds in this project.")
    for rel, text in (also or {}).items():
        project.write(rel, text)
    trailers = ["Task: decision-record", "Role: owner"]
    if decision is not None:
        trailers.append(f"Implements: {decision}")
        subject = f"Decision record {decision}: the close's time limit"
    else:
        subject = "Register tidy: the close's time limit"
    return project.commit(subject, who=support.OWNER, trailers=tuple(trailers), exact=True)


def _refused_as_unmeasured(project, sandbox, interface, commit):
    run = support.run_close(project, sandbox, TICKET)
    error = support.refused(run, interface)
    assert WORK_WITHOUT_TASK in support.codes_of(error) or support.names(error, WORK_WITHOUT_TASK), \
        f"the close was not refused for work without a task\n{run.describe()}"
    assert support.names(error, commit[:12]), f"the refusal does not name the decision-record commit\n{run.describe()}"
    support.base.assert_not_closed(project, TICKET)


def test_a_decision_record_of_governance_records_under_an_accepted_decision_counts_as_measured(project, sandbox,
                                                                                              interface):
    _ticket_naming_the_path_map(project)
    record = _decision_record(project, "DEC-501")
    changed = sorted(support.git(project, "show", "--name-only", "--format=", record).split())
    assert changed == sorted([support.PATH_MAP_REL, support.REGISTER]), f"the fixture is wrong: {changed}"
    support.checkpointed(project, TICKET)

    run = support.run_close(project, sandbox, TICKET)

    support.closed(run, interface)
    assert support.ticket_status(project.root, TICKET) == "closed"


def test_a_decision_record_naming_a_decision_that_is_not_accepted_counts_as_unmeasured(project, sandbox, interface):
    """Failure KPI 3: the decision it names is PROPOSED, not ACCEPTED."""
    _ticket_naming_the_path_map(project)
    record = _decision_record(project, "DEC-502", status=support.PROPOSED)
    support.checkpointed(project, TICKET)
    _refused_as_unmeasured(project, sandbox, interface, record)


def test_a_decision_record_naming_no_decision_counts_as_unmeasured(project, sandbox, interface):
    """Failure KPI 3: ``Task: decision-record``, and no decision named anywhere in the commit."""
    _ticket_naming_the_path_map(project)
    record = _decision_record(project, None)
    support.checkpointed(project, TICKET)
    _refused_as_unmeasured(project, sandbox, interface, record)


@pytest.mark.parametrize("rel, text", [
    ("src/example/feature.py", "# feature, changed by a decision record\n"),
    ("tests/unit/test_w207_by_a_record.py", "def test_w207_by_a_record():\n    assert True\n"),
    ("template/governance/kernel/skills/w207/SKILL.md", "---\nname: w207\nversion: \"1.0.0\"\n---\n# w207\n"),
], ids=["code", "tests", "kernel"])
def test_a_decision_record_that_also_changes_code_tests_or_the_kernel_counts_as_unmeasured(rel, text, project, sandbox,
                                                                                          interface):
    _ticket_naming_the_path_map(project)
    record = _decision_record(project, "DEC-503", also={rel: text})
    support.checkpointed(project, TICKET)
    _refused_as_unmeasured(project, sandbox, interface, record)
