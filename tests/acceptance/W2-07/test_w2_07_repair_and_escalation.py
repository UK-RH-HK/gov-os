"""KPI 8, KPI 10 and KPI 11: complete, tracked repair tickets; what counts toward escalation; an interrupted close.

KPI 8: "A refused close writes a complete repair ticket (role, allowed paths, KPIs) that stays tracked in .tickets/
[F-m8, W2-L209, W2-L236, AR-9]." W2-L209: "A refused close's repair ticket is schema-valid with a role, and its
tracking state is decided and tested." W2-L236: the orchestrator had to move untracked repair tickets out of
``.tickets/``.

KPI 10: "Adoption-gap and baseline refusals do not count toward the escalation counter; a repeated identical refusal
reuses its repair ticket [W2-H038, W2-M249, W2-M252]." W2-M249: "A refusal for adoption gaps alone leaves the
escalation counter unchanged, and a case shows it." DEC-492 names the adoption gaps; the first of them is a commit
without ``Implements:``, which is now a commit-gate refusal (KPI 4) and spends no attempt (README, the reading of
KPI 10).

KPI 11: "An interrupted close leaves nothing that blocks the next close [W2-M158]." W2-M158: "Interrupted ticket-tool
close leaves a record and checkpoint that block the next close."

A refusal "for a finding about the ticket's work" here is a failing acceptance test (DEC-455): counted, with a repair
ticket, exit code 3.
"""

import w2_07_support as support

TICKET, WBS = "PROJ-rpar", "W9-rpar"
FAILING = "test_w207_fails"


def _ticket_with_a_failing_test(project):
    support.create_ticket(project, TICKET, WBS)
    project.write(f"tests/acceptance/{WBS}/{FAILING}.py", f"def {FAILING}():\n    assert False, 'not yet'\n")
    project.commit("a failing acceptance test", who=support.TEST_DESIGNER,
                   trailers=support.trailers_of(TICKET, role="independent-test-designer"), exact=True)
    support.work(project, TICKET, {"src/example/feature.py": "# feature\n"})
    support.checkpointed(project, TICKET)


def _refused_for_the_test(project, sandbox, interface):
    run = support.run_close(project, sandbox, TICKET)
    error = support.refused(run, interface)
    assert run.returncode == support.EXIT_CHECK_FAILED and support.names(error, FAILING), \
        f"the close was not refused for the failing acceptance test\n{run.describe()}"
    return run, error


def _the_repair_ticket(project, run):
    repairs = support.other_tickets(project.root, TICKET)
    assert len(repairs) == 1, f"one repair ticket is expected, found {[p.name for p in repairs]}\n{run.describe()}"
    return repairs[0]


# --------------------------------------------------------------------------
# KPI 8: complete and tracked
# --------------------------------------------------------------------------

def test_a_refused_close_writes_a_complete_schema_valid_repair_ticket(project, sandbox, interface):
    _ticket_with_a_failing_test(project)
    run, _ = _refused_for_the_test(project, sandbox, interface)
    repair = _the_repair_ticket(project, run)
    front = support.frontmatter_of(repair)
    assert isinstance(front.get("role"), str) and front["role"].strip(), f"the repair ticket has no role: {front}"
    paths = front.get("allowed_paths")
    assert isinstance(paths, list) and paths and all(isinstance(p, str) and p for p in paths), \
        f"the repair ticket has no allowed paths: {front}"
    kpis = front.get("kpis") or {}
    assert isinstance(kpis, dict) and kpis.get("success") and "failure" in kpis, f"the repair ticket has no KPIs: {front}"
    errors = support.ticket_schema_errors(front)
    assert not errors, f"the repair ticket is not valid against the ticket schema: {errors}\n{repair.read_text()}"


def test_the_repair_ticket_stays_tracked_and_blocks_no_later_close(project, sandbox, interface):
    _ticket_with_a_failing_test(project)
    run, _ = _refused_for_the_test(project, sandbox, interface)
    repair = _the_repair_ticket(project, run)
    rel = repair.relative_to(project.root).as_posix()
    assert rel.startswith(".tickets/"), f"the repair ticket is not in .tickets/: {rel}"
    assert support.tracked(project, rel), f"git does not track the repair ticket {rel}\n{run.describe()}"

    # The repair: the test designer corrects the test. The next close is not refused for the repair ticket.
    project.write(f"tests/acceptance/{WBS}/{FAILING}.py", f"def {FAILING}():\n    assert True\n")
    project.commit("the test corrected", who=support.TEST_DESIGNER,
                   trailers=support.trailers_of(TICKET, role="independent-test-designer"), exact=True)
    support.checkpointed(project, TICKET)
    again = support.run_close(project, sandbox, TICKET)
    support.closed(again, interface)
    assert repair.is_file() and support.tracked(project, rel), "the repair ticket did not stay tracked in .tickets/"


# --------------------------------------------------------------------------
# KPI 10: what counts toward escalation; one repair ticket for one cause
# --------------------------------------------------------------------------

def test_adoption_gap_refusals_do_not_count_toward_escalation(project, sandbox, interface):
    """Four closes, each refused for a commit without ``Implements:`` alone (DEC-492's first adoption gap): the count
    stays 0, no escalation is written, and the fourth is not blocked (exit code 4)."""
    support.create_ticket(project, TICKET, WBS)
    support.work(project, TICKET, {"src/example/feature.py": "# feature\n"},
                 trailers=(f"Task: {TICKET}", "Role: engineer"))
    support.checkpointed(project, TICKET)
    for attempt in range(4):
        run = support.run_close(project, sandbox, TICKET)
        error = support.refused(run, interface)
        assert run.returncode != support.EXIT_BLOCKED, \
            f"attempt {attempt + 1} is blocked: adoption-gap refusals reached an escalation\n{run.describe()}"
        assert support.names(error, "Implements"), f"attempt {attempt + 1} was refused for something else\n{run.describe()}"
        support.assert_no_attempt_spent(project, TICKET, run)
        support.commit_what_a_refusal_left(project)


def test_a_repeated_identical_refusal_reuses_its_repair_ticket(project, sandbox, interface):
    _ticket_with_a_failing_test(project)
    first, first_error = _refused_for_the_test(project, sandbox, interface)
    repair = _the_repair_ticket(project, first)
    support.commit_what_a_refusal_left(project)

    second, second_error = _refused_for_the_test(project, sandbox, interface)

    assert _the_repair_ticket(project, second) == repair, "the second refusal did not reuse the repair ticket"
    assert support.names(second_error, repair.stem), \
        f"the second refusal does not name the repair ticket it reuses ({repair.stem})\n{second.describe()}"
    assert support.iteration_count(project.root, TICKET) == 2, "a refusal for a failing test is still counted"


# --------------------------------------------------------------------------
# KPI 11: an interrupted close
# --------------------------------------------------------------------------

def test_an_interrupted_close_leaves_nothing_that_blocks_the_next_close(project, sandbox, interface, tmp_path):
    """The ticket tool kills the close that called it while it closes the ticket: the close ends with SIGKILL after
    it wrote its records. With the real tool back (only the tool's file committed, so whatever the interrupted close
    left stays where it left it), the next close closes the ticket."""
    support.ready_ticket(project, TICKET, WBS)
    keep = tmp_path / "real-tool" / "tk"
    support.install_interrupting_tool(project, TICKET, keep)

    interrupted = support.run_close(project, sandbox, TICKET)
    assert interrupted.returncode not in (support.EXIT_OK, support.EXIT_GOV_ERROR, support.EXIT_CHECK_FAILED), \
        f"the fixture is wrong: the close was not interrupted\n{interrupted.describe()}"
    assert support.ticket_status(project.root, TICKET) == "in_progress", "the fixture is wrong: the ticket closed"

    support.restore_tool(project, keep)

    run = support.run_close(project, sandbox, TICKET)

    support.closed(run, interface)
    assert support.ticket_status(project.root, TICKET) == "closed"
    assert len(support.base.close_records(project.root, TICKET)) == 1, "the ticket has more than one close record"
