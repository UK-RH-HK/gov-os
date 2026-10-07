"""Containment at close, place by place (KPI S1 "runs the containment check"; DEC-453).

DEC-453: ``gov close`` calls W1-50's public judgement for the ticket's commits and refuses on any finding; it
has no rule set of its own, so it exempts no place. ``tests/acceptance/W1-50/README.md`` ("What the suite takes
as given") says where a commit with ``Role: engineer`` and the ticket's ``Task`` may write: the ticket's
``allowed_paths``, and never a ticket file.

Each case builds a ticket that is clean and green, then adds one commit of the ticket, made by the engineer,
that changes one file in one place outside ``allowed_paths``. The case first asks W1-50's public function and
holds its answer (the commit, with that path): so the finding is W1-50's own, not this suite's reading of the
rules. Then ``gov close`` must refuse and name the commit and the path, the ticket stays in progress, and no
close record is written.
"""

import w1_30_support as support

TICKET = "PROJ-cont"
WBS = "W1-cont"
OTHER = "PROJ-othr"
OTHER_WBS = "W1-othr"


def _refused_for(project, sandbox, interface, rel, text="planted\n", before=None):
    """Add the engineer's commit of ``rel`` to a clean green ticket and hold the refusal."""
    trailers = support.build_ticket(project, TICKET, WBS)
    if before is not None:
        before(project)
    project.write(rel, text)
    planted = project.commit(f"the engineer changes {rel}", who=support.IMPLEMENTER, trailers=trailers, exact=True)
    project.add_checkpoint(TICKET)
    project.commit("checkpoint", who=support.ORCHESTRATOR)

    findings = support.judged_by_w1_50(project, sandbox, support.ticket_commits(project.root, TICKET))
    assert [(f["commit"], f["paths"]) for f in findings] == [(planted, [rel])], \
        f"the fixture is wrong: W1-50's judgement of the ticket's commits is {findings}"

    run = support.run_close(project, sandbox, TICKET)
    error = support.refused(run, interface, support.EXIT_CHECK_FAILED)
    text = support.error_text(error)
    assert rel in text, f"the refusal does not name the path {rel}\n{run.describe()}"
    assert planted[:7] in text, f"the refusal does not name the commit {planted[:7]}\n{run.describe()}"
    support.assert_not_closed(project, TICKET)


def test_an_engineer_commit_under_the_projects_governance_folder_refuses(project, sandbox, interface):
    """A file under ``governance/project/``."""
    _refused_for(project, sandbox, interface, "governance/project/notes.md", "# planted\n")


def test_an_engineer_commit_of_a_kernel_file_under_template_refuses(project, sandbox, interface):
    """A kernel file under ``template/``."""
    _refused_for(project, sandbox, interface, "template/governance/kernel/roles/planted.md", "# planted\n")


def test_an_engineer_commit_of_a_test_outside_its_acceptance_folder_and_paths_refuses(project, sandbox, interface):
    """A test under ``tests/`` that is neither in the ticket's acceptance folder nor in its paths. It passes, so
    the regression run finds nothing: only the containment judgement can refuse."""
    _refused_for(project, sandbox, interface, "tests/unit/test_planted.py",
                 "def test_planted():\n    assert True\n")


def test_an_engineer_commit_of_a_file_at_the_projects_root_refuses(project, sandbox, interface):
    """A file at the project's root."""
    _refused_for(project, sandbox, interface, "NOTES.md", "# planted\n")


def _another_ticket(project):
    project.write(support.ticket_path(OTHER), support.ticket_text(OTHER, OTHER_WBS, allowed_paths=["src/other/**"]))
    project.commit("the other ticket", who=support.ORCHESTRATOR)


def test_an_engineer_commit_of_another_tickets_file_refuses(project, sandbox, interface):
    """The file of another ticket under ``.tickets/`` (W1-50 README, "Ticket files": a finding whatever the
    ticket's paths say)."""
    text = support.ticket_text(OTHER, OTHER_WBS, allowed_paths=["src/other/**", "src/example/**"])
    _refused_for(project, sandbox, interface, support.ticket_path(OTHER), text, before=_another_ticket)


def test_an_engineer_commit_inside_another_tickets_paths_refuses(project, sandbox, interface):
    """A source file inside the paths of another ticket in progress, outside its own."""
    _refused_for(project, sandbox, interface, "src/other/planted.py", "# planted\n", before=_another_ticket)


def test_a_clean_ticket_has_no_finding_and_closes(project, sandbox, interface):
    """The other side: the commits of the ticket this file builds pass W1-50's judgement, and the ticket closes.
    A close that refuses whatever the commits hold fails here."""
    support.build_ticket(project, TICKET, WBS)
    assert support.judged_by_w1_50(project, sandbox, support.ticket_commits(project.root, TICKET)) == []
    run = support.run_close(project, sandbox, TICKET)
    support.result_of(run, interface)
    assert support.ticket_status(project.root, TICKET) == "closed"
