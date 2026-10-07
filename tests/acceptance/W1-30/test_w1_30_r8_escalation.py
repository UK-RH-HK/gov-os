"""What lifts an escalation, and what cannot reset it (DEC-487, fifth and sixth behaviours).

"The owner's decision lifts an escalation only if W1-11's checker confirms it as the owner's and in force, it
is committed, it was recorded after the escalation began, and it has not lifted an escalation before."

"The escalation state cannot be reset by its absence: an escalation in force with its counter missing, or a
counter that is not a count from zero up, blocks and says so. The counter, the ticket files and the records
are written whole or not at all."

The escalation of every case is made the same way (``support.escalate``): three closes refused for the
ticket's failing acceptance test and a fourth that is blocked. Between closes the orchestrator commits what
the refusal left (the repair ticket), so each close finds its tree committed.

How a case holds "the escalation was not lifted": the close given the decision stays blocked, with the blocked
exit code 4 (DEC-490), and the close after it, given none, is blocked with exit code 4 too. Had the escalation
been lifted, that close would have run the tests and ended with exit code 3. What the case planted in the
working tree is removed before it.

A counter that is not a count, or that cannot be read, is "could not measure" (DEC-490): exit code 1, the
counter's file named in the answer, the counter as it was, no repair ticket. An escalation in force whose
counter is missing blocks (exit code 4, DEC-487).

Written whole, as far as a case can hold it without timing: after a refusal the folders of the counter and of
the escalation hold the ticket's one file each, readable, and nothing beside it. DEC-490: "held by the unit
tests and by reading; no acceptance case with timing."
"""

import json

import pytest

import w1_30_support as support

TICKET = "PROJ-escl"
WBS = "W1-escl"
COUNTER = f"{support.ITERATION_DIR}/{TICKET}.json"


def _escalated(project, sandbox, interface):
    support.build_ticket(project, TICKET, WBS, failing=True)
    support.escalate(project, sandbox, interface, TICKET)


def _not_lifted_by(project, sandbox, interface, decision, why, codes=(support.EXIT_BLOCKED,)):
    """The close given ``decision`` stays blocked, with the blocked exit code (DEC-490: "an owner's decision
    that does not qualify lifts nothing"); the ticket is not closed."""
    run = support.run_close(project, sandbox, TICKET, "--owner-decision", decision)
    envelope = support.envelope_of(run, interface)
    assert envelope["ok"] is False and run.returncode in codes, \
        f"{why}: the close does not end with exit code {' or '.join(map(str, codes))}\n{run.describe()}"
    support.assert_not_closed(project, TICKET)
    return run


# --------------------------------------------------------------------------
# The owner's decision
# --------------------------------------------------------------------------

def test_a_file_no_commit_holds_lifts_no_escalation(project, sandbox, interface):
    """The decision is the name of an untracked file that holds an active status line and nothing else. The
    file also makes the tree another than its commit, and no source states which of the two the close answers
    first: blocked (exit code 4) or "could not measure" for the tree (exit code 1). The case accepts both."""
    _escalated(project, sandbox, interface)
    planted = project.write("docs/adr/DEC-planted.md", "---\nstatus: ACTIVE\n---\n")
    _not_lifted_by(project, sandbox, interface, "DEC-planted", "a file no commit holds was taken as the owner's decision",
                   codes=(support.EXIT_BLOCKED, support.EXIT_GOV_ERROR))
    planted.unlink()
    support.commit_what_a_refusal_left(project)
    support.assert_escalation_in_force(project, sandbox, interface, TICKET, "a file no commit holds")


def test_a_path_to_a_file_outside_the_project_lifts_no_escalation(project, sandbox, interface):
    _escalated(project, sandbox, interface)
    outside = project.root.parent / "outside" / "DEC-outside.md"
    outside.parent.mkdir()
    outside.write_text(support.decision("DEC-outside", "ACTIVE", title="Continue"), encoding="utf-8")
    for start in ("docs/adr", "governance/decisions", "docs", "."):
        name = "/".join([".."] * len([part for part in start.split("/") if part != "."]) + ["..", "outside", "DEC-outside"])
        assert (project.root / start / f"{name}.md").resolve() == outside.resolve()
        _not_lifted_by(project, sandbox, interface, name, f"a path that leaves the project ({name}) was taken as the owner's decision")
        support.commit_what_a_refusal_left(project)
    support.assert_escalation_in_force(project, sandbox, interface, TICKET, "a file outside the project")


def test_the_tickets_own_checkpoint_lifts_no_escalation(project, sandbox, interface):
    _escalated(project, sandbox, interface)
    checkpoints = sorted((project.root / "docs" / "checkpoints").rglob("*.md"))
    assert checkpoints and support.frontmatter_of(checkpoints[-1]).get("task") == TICKET, \
        f"the fixture is wrong: no checkpoint of the ticket under docs/checkpoints: {checkpoints}"
    _not_lifted_by(project, sandbox, interface, checkpoints[-1].stem, "the ticket's own checkpoint was taken as the owner's decision")
    support.commit_what_a_refusal_left(project)
    support.assert_escalation_in_force(project, sandbox, interface, TICKET, "the ticket's own checkpoint")


def test_a_decision_recorded_before_the_escalation_began_lifts_none(project, sandbox, interface):
    """The owner's decision, active and committed by the owner, is older than the ticket's first refusal."""
    project.add_decision("DEC-earlier", "ACTIVE", title="An earlier decision of the owner")
    project.commit("the owner's decision", who=support.OWNER)
    _escalated(project, sandbox, interface)
    codes = [finding.get("code") for finding in support.decision_check(project, sandbox).get("findings", [])
             if "DEC-earlier" in json.dumps(finding)]
    assert not codes, f"the fixture is wrong: W1-11's checker has findings about the decision: {codes}"
    _not_lifted_by(project, sandbox, interface, "DEC-earlier", "a decision older than the escalation lifted it")
    support.commit_what_a_refusal_left(project)
    support.assert_escalation_in_force(project, sandbox, interface, TICKET, "a decision older than the escalation")


def test_a_decision_that_lifted_one_escalation_lifts_no_second(project, sandbox, interface):
    """The decision is recorded after the first escalation began and lifts it: the close runs and is refused
    for the failing test. Two more refusals bring the second escalation; the same decision is given again."""
    _escalated(project, sandbox, interface)
    project.add_decision("DEC-once", "ACTIVE", title="Continue")
    project.commit("the owner's decision", who=support.OWNER)
    first = support.run_close(project, sandbox, TICKET, "--owner-decision", "DEC-once")
    support.refused(first, interface, support.EXIT_CHECK_FAILED)   # lifted: the tests ran and failed
    support.commit_what_a_refusal_left(project)
    for _ in range(2):
        support.refused(support.run_close(project, sandbox, TICKET), interface, support.EXIT_CHECK_FAILED)
        support.commit_what_a_refusal_left(project)
    support.refused(support.run_close(project, sandbox, TICKET), interface, support.EXIT_BLOCKED)

    _not_lifted_by(project, sandbox, interface, "DEC-once", "a decision lifted a second escalation")
    support.commit_what_a_refusal_left(project)
    support.assert_escalation_in_force(project, sandbox, interface, TICKET, "a decision used before")


# --------------------------------------------------------------------------
# The escalation state
# --------------------------------------------------------------------------

def test_an_escalation_in_force_whose_counter_is_missing_blocks_and_says_so(project, sandbox, interface):
    _escalated(project, sandbox, interface)
    assert (project.root / support.ESCALATION_DIR / f"{TICKET}.json").is_file(), \
        "the fixture is wrong: the escalation left no file"
    (project.root / COUNTER).unlink()

    run = support.run_close(project, sandbox, TICKET)

    error = support.refused(run, interface, support.EXIT_BLOCKED)
    assert COUNTER in support.error_text(error), f"the answer does not name the missing counter {COUNTER}\n{run.describe()}"
    support.assert_not_closed(project, TICKET)


@pytest.mark.parametrize("count", [-5, 1.5], ids=["below zero", "not a whole number"])
def test_a_counter_that_is_not_a_count_from_zero_up_blocks_and_says_so(count, project, sandbox, interface):
    """The counter is preset before the first close. Nothing runs: exit code 1, the counter's file named, no
    repair ticket, the counter as it was."""
    support.build_ticket(project, TICKET, WBS, failing=True)
    preset = {"count": count, "last_failures": [], "outcomes": []}
    support.write_iteration_file(project.root, TICKET, preset)

    run = support.run_close(project, sandbox, TICKET)

    error = support.refused_without_a_finding(run, interface)
    assert COUNTER in support.error_text(error), f"the answer does not name the counter {COUNTER}\n{run.describe()}"
    assert support.read_iteration_file(project.root, TICKET) == preset, "the close rewrote the counter it could not read"
    support.assert_no_repair_ticket(project, run, TICKET)
    support.assert_not_closed(project, TICKET)


def test_a_counter_that_cannot_be_read_blocks_and_names_its_file(project, sandbox, interface):
    support.build_ticket(project, TICKET, WBS, failing=True)
    support.corrupt_iteration_file(project.root, TICKET, content='{"count": ')

    run = support.run_close(project, sandbox, TICKET)

    error = support.refused_without_a_finding(run, interface)
    assert COUNTER in support.error_text(error), f"the answer does not name the counter {COUNTER}\n{run.describe()}"
    support.assert_no_repair_ticket(project, run, TICKET)
    support.assert_not_closed(project, TICKET)


def test_a_refusal_leaves_the_counter_and_the_escalation_whole_and_nothing_beside_them(project, sandbox, interface):
    support.build_ticket(project, TICKET, WBS, failing=True)
    for number in (1, 2, 3):
        support.refused(support.run_close(project, sandbox, TICKET), interface, support.EXIT_CHECK_FAILED)
        support.commit_what_a_refusal_left(project)
        beside = sorted(path.name for path in (project.root / support.ITERATION_DIR).iterdir())
        assert beside == [f"{TICKET}.json"], f"after refusal {number} the counter's folder holds {beside}"
        assert support.iteration_count(project.root, TICKET) == number
    folder = project.root / support.ESCALATION_DIR
    beside = sorted(path.name for path in folder.iterdir())
    assert beside == [f"{TICKET}.json"], f"the escalation's folder holds {beside}"
    assert isinstance(json.loads((folder / f"{TICKET}.json").read_text(encoding="utf-8")), dict)
