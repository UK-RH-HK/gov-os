"""``gov close`` refuses wherever ``gov check`` blocks (KPI S4, CAP-38.d; DEC-480).

DEC-480: for a governance-changing ticket, ``gov close`` refuses on "the same condition on which ``gov check``
blocks a merge". ``gov check`` blocks on the status of its families, and one family is red while no single
hard-block check is red: the family of a declared check that is none of the runner's families (W1-26, DEC-436:
such a declaration "is reported by name and makes the result not green"). The check itself runs and passes.

Every project here declares its own checks (``project_with_checks``; README, "Round 6"). Every case first
runs ``gov check`` in the project as it stands at the commit being closed and holds what it is about: that
the command blocks (or does not), and that no hard-block check is red. What blocks is read from the runner's
answer, not written into the case.
"""

import pytest

import w1_30_support as support

TICKET = "PROJ-gvb1"
WBS = "W1-checkblocks"

NOTES = "governance/project/notes.yaml"

# A family that is none of the runner's, and one that is.
OTHER_FAMILY = "licence hygiene"
KNOWN_FAMILY = "graph integrity"
assert OTHER_FAMILY not in support.FAMILIES and KNOWN_FAMILY in support.FAMILIES

README_PRESENT = support.declared_check("readme-present", "test -s README.md")


def _feature_check(family, severity=support.HARD_BLOCK):
    """A check that passes once the ticket's work is there, declared in ``family``."""
    return support.declared_check("feature-present", "test -s src/example/feature.py", severity=severity,
                                  family=family)


def _ready(project):
    """The ticket's work with a governance file changed, and the checkpoint: returns ``HEAD``."""
    support.start_ticket(project, TICKET, WBS)
    support.engineer_commit(project, TICKET, {"src/example/feature.py": "# feature\n", NOTES: "note: one\n"})
    return support.checkpointed(project, TICKET)


def _gov_check(project, sandbox):
    """``gov check --json`` in the project as it stands: its run, and the body that names families and checks
    (``result`` when it passes, ``error.details`` when it blocks)."""
    run = support.run_check(project, sandbox)
    envelope = run.envelope()
    body = envelope.get("result") if envelope.get("ok") else (envelope.get("error") or {}).get("details")
    assert isinstance(body, dict) and body.get("checks"), f"gov check named no check\n{run.describe()}"
    return run, body


def _red_hard_blocks(body):
    return support.red_hard_blocks({entry["id"]: entry for entry in body["checks"]})


def _red_families(body):
    families = body.get("families") or {}
    return sorted(name for name in families if support.family_status(body, name) == support.RED)


def _blocks_without_a_red_check(project, sandbox):
    """The fixture: ``gov check`` itself blocks at the commit being closed, no hard-block check is red, and
    the declared check passed. Returns the families the runner reports red."""
    run, body = _gov_check(project, sandbox)
    assert run.returncode == support.EXIT_CHECK_FAILED and run.envelope().get("ok") is False, \
        f"the fixture is wrong: gov check does not block\n{run.describe()}"
    assert _red_hard_blocks(body) == [], \
        f"the fixture is wrong: hard-block checks are red: {_red_hard_blocks(body)}"
    statuses = {entry["id"]: entry["status"] for entry in body["checks"]}
    assert statuses.get("feature-present") == support.GREEN, \
        f"the fixture is wrong: the declared check did not pass: {statuses}"
    red = _red_families(body)
    assert red == [OTHER_FAMILY], f"the fixture is wrong: the runner reports the families {red} red"
    return red


def _refused_naming_what_blocks(run, interface, families):
    error = support.refused(run, interface, support.EXIT_CHECK_FAILED)
    text = support.error_text(error)
    for family in families:
        assert family in text, \
            f"the answer does not name the family {family!r} that gov check reports as blocking\n{run.describe()}"
    return error


# --------------------------------------------------------------------------
# 1. gov check blocks, no hard-block check is red: the close is refused
# --------------------------------------------------------------------------

@pytest.mark.parametrize("severity", [support.HARD_BLOCK, support.WARNING])
def test_a_close_is_refused_where_gov_check_blocks_and_no_hard_block_check_is_red(
        severity, project_with_checks, sandbox, interface):
    """The family is red whatever the severity of the passing check declared in it."""
    project = project_with_checks(README_PRESENT, _feature_check(OTHER_FAMILY, severity))
    _ready(project)
    blocking = _blocks_without_a_red_check(project, sandbox)

    run = support.run_close(project, sandbox, TICKET)

    _refused_naming_what_blocks(run, interface, blocking)
    support.assert_not_closed(project, TICKET)


def test_a_refusal_where_gov_check_blocks_is_counted(project_with_checks, sandbox, interface):
    project = project_with_checks(README_PRESENT, _feature_check(OTHER_FAMILY))
    _ready(project)
    blocking = _blocks_without_a_red_check(project, sandbox)

    run = support.run_close(project, sandbox, TICKET)

    _refused_naming_what_blocks(run, interface, blocking)
    assert support.iteration_count(project.root, TICKET) == 1, \
        f"the close refused where gov check blocks is not counted as one iteration\n{run.describe()}"


def test_a_refusal_where_gov_check_blocks_opens_a_dependent_repair_ticket(project_with_checks, sandbox, interface):
    project = project_with_checks(README_PRESENT, _feature_check(OTHER_FAMILY))
    _ready(project)
    blocking = _blocks_without_a_red_check(project, sandbox)

    run = support.run_close(project, sandbox, TICKET)

    _refused_naming_what_blocks(run, interface, blocking)
    support.assert_dependent_repair_ticket(project, TICKET, run)


# --------------------------------------------------------------------------
# 2. The converse: gov check does not block, the same ticket closes
# --------------------------------------------------------------------------

def test_the_same_ticket_closes_where_gov_check_does_not_block(project_with_checks, sandbox, interface):
    """The same project, ticket and check; the check is declared in one of the runner's families."""
    project = project_with_checks(README_PRESENT, _feature_check(KNOWN_FAMILY))
    _ready(project)
    check, body = _gov_check(project, sandbox)
    assert check.returncode == support.EXIT_OK and check.envelope().get("ok") is True, \
        f"the fixture is wrong: gov check blocks\n{check.describe()}"
    assert _red_hard_blocks(body) == [] and _red_families(body) == [], \
        f"the fixture is wrong: red checks {_red_hard_blocks(body)}, red families {_red_families(body)}"

    run = support.run_close(project, sandbox, TICKET)

    support.result_of(run, interface)
    assert support.ticket_status(project.root, TICKET) == "closed"
