"""KPI success 2: what ``gov status --json`` reports.

"gov status --json reports ready/blocked/claimed tickets, open decision
packages, readiness per specification, governance share, pause state and
doctor summary."

Each part is compared with the source the README settles on, read on the same
temporary project through that source's own public interface: ``gov.tasks``
(the READY rule and the claim lock, W1-09), the record store's decision
packages (DEC-308), ``gov readiness`` (W1-13), ``gov telemetry`` (W1-31) and
``gov doctor`` (W1-27). The pause state has a file of its own.
"""

from __future__ import annotations

import pytest

import w1_32_support as support

spec_support = support.spec_support
tasks_support = support.tasks_support


def test_the_answer_has_the_six_parts(status, interface):
    answer = support.answered(status(), interface)
    assert set(support.PARTS) <= set(answer)


def test_an_empty_project_is_answered_too(empty_project, sandbox, interface):
    """No ticket, no package, no specification: every list was read and is empty, and says so by being a list."""
    answer = support.answered(support.status(empty_project, sandbox), interface)
    for name in support.TICKET_LISTS:
        assert support.ids(answer[support.TICKETS][name]) == [], f"an empty project has {name} tickets"
    assert support.ids(answer[support.PACKAGES]) == []
    assert support.ids(answer[support.READINESS]) == []


# --------------------------------------------------------------------------
# Tickets
# --------------------------------------------------------------------------

def test_the_ready_tickets_are_those_of_the_ready_rule(project, status, interface):
    ready, _ = project.queue()
    assert ready == [support.T_READY, support.T_OTHER_READY], f"the fixture's READY tickets are {ready}"
    answer = support.answered(status(), interface)
    assert support.ids(answer[support.TICKETS][support.READY]) == ready


def test_the_blocked_tickets_are_listed_each_with_its_reasons(project, status, interface):
    _, blocked = project.queue()
    assert blocked[support.T_WAITS] == ["DECISION_OPEN"] and blocked[support.T_DEPENDS] == ["DEPENDENCY_OPEN"], \
        f"the fixture's blocked tickets are {blocked}"
    listed = support.answered(status(), interface)[support.TICKETS][support.BLOCKED]
    missing = sorted(set(blocked) - set(support.ids(listed)) - {support.T_IN_PROGRESS, support.T_CLAIMED})
    assert not missing, f"blocked tickets left out: {missing}; listed: {support.ids(listed)}"
    for ticket in (support.T_WAITS, support.T_DEPENDS):
        said = support.text_of(support.entry(listed, ticket))
        for reason in blocked[ticket]:
            assert reason in said, f"{ticket} is listed as blocked without its reason {reason}: {said}"


def test_a_ready_ticket_is_not_listed_as_blocked_and_a_closed_ticket_nowhere(status, interface):
    tickets = support.answered(status(), interface)[support.TICKETS]
    assert support.T_READY not in support.ids(tickets[support.BLOCKED])
    for name in support.TICKET_LISTS:
        assert support.T_CLOSED not in support.ids(tickets[name]), f"a closed ticket is listed as {name}"


def test_a_claimed_ticket_is_listed_with_its_holder(status, interface):
    """The claim lock of W1-09 (DEC-292): the ticket and who holds it."""
    claimed = support.answered(status(), interface)[support.TICKETS][support.CLAIMED]
    assert support.T_CLAIMED in support.ids(claimed), f"the claimed ticket is not listed: {support.ids(claimed)}"
    assert support.HOLDER in support.text_of(support.entry(claimed, support.T_CLAIMED)), \
        f"the claim is listed without its holder {support.HOLDER}: {support.text_of(claimed)}"


def test_a_ticket_in_progress_is_listed_as_claimed(status, interface):
    """The READY rule's own reading: ``CLAIMED`` holds a ticket that is in progress as it holds a locked one."""
    tickets = support.answered(status(), interface)[support.TICKETS]
    assert support.T_IN_PROGRESS in support.ids(tickets[support.CLAIMED]), \
        f"the ticket in progress is not listed as claimed: {support.ids(tickets[support.CLAIMED])}"
    assert support.T_READY not in support.ids(tickets[support.CLAIMED])


def test_every_ticket_that_is_not_closed_is_in_a_list(project, status, interface):
    """Nothing falls between the lists."""
    tickets = support.answered(status(), interface)[support.TICKETS]
    listed = {ticket for name in support.TICKET_LISTS for ticket in support.ids(tickets[name])}
    assert listed == set(project.tickets()) - {support.T_CLOSED}


# --------------------------------------------------------------------------
# Open decision packages
# --------------------------------------------------------------------------

def test_the_open_decision_packages_are_listed(status, interface):
    """Open is ``PROPOSED`` (DEC-308); a package nobody waits on is open too."""
    packages = support.answered(status(), interface)[support.PACKAGES]
    assert support.ids(packages) == [support.DP_OPEN, support.DP_OTHER_OPEN]


def test_an_answered_package_is_not_listed_as_open(status, interface):
    packages = support.answered(status(), interface)[support.PACKAGES]
    assert support.DP_ANSWERED not in support.ids(packages)


def test_an_open_package_names_the_tickets_that_wait_on_it(status, interface):
    packages = support.answered(status(), interface)[support.PACKAGES]
    assert support.T_WAITS in support.text_of(support.entry(packages, support.DP_OPEN)), \
        f"{support.DP_OPEN} is listed without the ticket that waits on it: {support.text_of(packages)}"


# --------------------------------------------------------------------------
# Readiness per specification
# --------------------------------------------------------------------------

def test_every_specification_is_listed_with_its_verdict(status, interface):
    readiness = support.answered(status(), interface)[support.READINESS]
    assert support.ids(readiness) == [support.SPEC_CLOSED, support.SPEC_OPEN]
    assert support.entry(readiness, support.SPEC_CLOSED)[spec_support.KEY_CLOSED] is True
    assert support.entry(readiness, support.SPEC_OPEN)[spec_support.KEY_CLOSED] is False


def test_the_verdict_is_the_readiness_checkers(project, sandbox, status, interface):
    """Specification by specification, the same verdict, profile and open rows as ``gov readiness`` gives."""
    readiness = support.answered(status(), interface)[support.READINESS]
    for spec_id in (support.SPEC_CLOSED, support.SPEC_OPEN):
        run = support.gov(project, sandbox, *spec_support.select(spec_id))
        report = spec_support.report_of(run, interface)
        said = support.entry(readiness, spec_id)
        assert said[spec_support.KEY_CLOSED] is report[spec_support.KEY_CLOSED]
        assert said.get(spec_support.KEY_REPORT_PROFILE) == report[spec_support.KEY_REPORT_PROFILE], \
            f"{spec_id}: the profile it was judged at is not shown: {support.text_of(said)}"
        for row in report[spec_support.KEY_OPEN]:
            assert row[spec_support.ROW_KEY] in support.text_of(said), \
                f"{spec_id}: the open row {row[spec_support.ROW_KEY]} is not shown: {support.text_of(said)}"


# --------------------------------------------------------------------------
# Governance share
# --------------------------------------------------------------------------

def test_the_governance_share_is_not_measured_and_says_why(project, sandbox, status, interface):
    """No session of a ticket is recorded anywhere (DEC-491), so the counter measures nothing: the status says
    "not measured" with the counter's own reason, and gives no figure."""
    counter = support.gov(project, sandbox, "telemetry", support.T_IN_PROGRESS, "--json")
    reason = counter.envelope()["error"]["message"]
    assert support.NOT_MEASURED in reason, f"the counter measured a ticket no session is named for\n{counter.describe()}"
    share = support.answered(status(), interface)[support.SHARE]
    said = support.text_of(share)
    assert support.NOT_MEASURED in said, f"the governance share does not say {support.NOT_MEASURED!r}: {said}"
    assert reason in said, f"the governance share does not give the counter's reason ({reason!r}): {said}"
    assert support.numbers_in(share) == [], f"a share that was not measured carries a figure: {said}"


# --------------------------------------------------------------------------
# Doctor summary
# --------------------------------------------------------------------------

def _doctor(project, sandbox):
    """``gov doctor --json`` on the same project: ``(healthy, section -> status)``."""
    envelope = support.gov(project, sandbox, "doctor", "--json").envelope()
    report = envelope["result"] if envelope["ok"] else envelope["error"]["details"]
    return report["healthy"], {name: section["status"] for name, section in report.items()
                               if isinstance(section, dict) and "status" in section}


def test_the_doctor_summary_gives_doctors_verdict(project, sandbox, status, interface):
    healthy, _ = _doctor(project, sandbox)
    summary = support.answered(status(), interface)[support.DOCTOR]
    assert isinstance(summary, dict) and summary.get("healthy") is healthy, \
        f"the doctor summary does not give doctor's verdict (healthy: {healthy}): {support.text_of(summary)}"


def test_the_doctor_summary_names_every_part_that_did_not_pass(project, sandbox, status, interface):
    """A part doctor could not measure is named with that word: a summary of "healthy" alone would hide it."""
    _, sections = _doctor(project, sandbox)
    not_passed = {name: state for name, state in sections.items() if state != "pass"}
    assert "unmeasured" in not_passed.values(), f"the fixture has no unmeasured doctor part: {sections}"
    summary = support.answered(status(), interface)[support.DOCTOR]
    said = support.text_of(summary)
    for name, state in not_passed.items():
        assert name in said, f"the doctor summary leaves out {name} ({state}): {said}"
    for state in set(not_passed.values()):
        assert state in said, f"the doctor summary does not say {state!r}: {said}"


def test_an_unhealthy_doctor_is_shown_with_the_part_that_failed(project, sandbox, interface):
    """A path-map that classifies no tracked file fails doctor's ``path_map`` part (W1-27)."""
    tasks_support.write(project.root, "governance/project/path-map.yaml",
                        "namespaces:\n  core:\n    paths:\n    - no-such-folder/**\n")
    support.settle(project)
    healthy, sections = _doctor(project, sandbox)
    assert healthy is False and sections["path_map"] == "fail", f"the fixture's doctor is not unhealthy: {sections}"
    answer = support.parts(support.status(project, sandbox), interface)
    summary = answer[support.DOCTOR]
    assert isinstance(summary, dict) and summary.get("healthy") is False, \
        f"doctor is unhealthy and the summary does not say so: {support.text_of(summary)}"
    assert "path_map" in support.text_of(summary), f"the failed part is not named: {support.text_of(summary)}"
    assert support.ids(answer[support.TICKETS][support.READY]), "an unhealthy doctor emptied the ticket lists"


# --------------------------------------------------------------------------
# The plain form
# --------------------------------------------------------------------------

@pytest.mark.parametrize("name", support.PARTS)
def test_the_plain_form_shows_the_same_parts(project, sandbox, name):
    """``gov status`` without ``--json``: the same answer for a reader (CAP-28)."""
    run = support.gov(project, sandbox, support.COMMAND)
    assert run.returncode == 0, run.describe()
    assert name in run.stdout, f"plain gov status does not show the part {name}\n{run.describe()}"
