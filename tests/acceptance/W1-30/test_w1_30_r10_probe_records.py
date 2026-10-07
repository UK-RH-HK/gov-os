"""Every probe record of the ticket is read (DEC-500, first behaviour; finding 3 of the last review).

"A record that says the probe of the final code failed refuses the close, whatever another record says; a close
needs a passing record of the final code and no failing one. Ordinary shape: a ticket with two reviews has two
records."

The project of each case is the one of ``test_full_ticket_closes_with_valid_probe``: a FULL ticket, green, its
probe record committed by the orchestrator and naming the commit being probed. The ticket's folder of probe
records (``docs/probes/<ticket>/``) holds one record or two. The two records differ in their id, their file
and their judgement and in nothing else: both name the ticket and the same probed commit, both are committed
by the orchestrator's one commit.

Which of the two says "fail" is each of them in turn, so that neither the first file read nor the last one
decides. The refusal is the probe gate's: a finding, exit code 3 (DEC-470); it says "judgement", as the
refusal of one failing record does. Which record the answer names is held nowhere: no source says it.

One passing record alone closes, under either of the two file names: a record of the ticket is a record
whatever its file is called in the ticket's folder.

Not held (DEC-500, residuals): a record of an earlier round beside a passing one.
"""

import pytest

import w1_30_support as support

TICKET = "PROJ-prbs"
WBS = "W1-prbs"
FIRST = f"PR-{TICKET}"
SECOND = f"PR-{TICKET}-2"


def _record(project, record_id, judgement, probed):
    """One probe record of the ticket in the ticket's folder, written and not yet committed."""
    text = support.probe_record(TICKET, judgement=judgement, probed_commit=probed)
    assert text.count(FIRST) == 2, "the fixture is wrong: the record names its id elsewhere than in id and title"
    rel = f"docs/probes/{TICKET}/{record_id}.md"
    project.write(rel, text.replace(FIRST, record_id))
    assert support.frontmatter_of(project.root / rel).get("id") == record_id
    return rel


@pytest.mark.parametrize("failing, passing", [(SECOND, FIRST), (FIRST, SECOND)],
                         ids=["the second record fails", "the first record fails"])
def test_a_failing_probe_record_beside_a_passing_one_refuses(failing, passing, project, sandbox, interface):
    support.build_ticket(project, TICKET, WBS, profile="FULL")
    probed = support.head_of(project)
    _record(project, passing, "pass", probed)
    _record(project, failing, "fail", probed)
    project.commit("the two probe records", who=support.ORCHESTRATOR)

    run = support.run_close(project, sandbox, TICKET)

    text = support.error_text(support.refused(run, interface, support.EXIT_CHECK_FAILED))
    assert "judgement" in text.lower(), f"the refusal does not name the judgement\n{run.describe()}"
    support.assert_not_closed(project, TICKET)


@pytest.mark.parametrize("record_id", [FIRST, SECOND], ids=["under the first name", "under the second name"])
def test_one_passing_probe_record_alone_closes(record_id, project, sandbox, interface):
    support.build_ticket(project, TICKET, WBS, profile="FULL")
    _record(project, record_id, "pass", support.head_of(project))
    project.commit("the probe record", who=support.ORCHESTRATOR)

    run = support.run_close(project, sandbox, TICKET)

    support.result_of(run, interface)
    assert support.ticket_status(project.root, TICKET) == "closed"
