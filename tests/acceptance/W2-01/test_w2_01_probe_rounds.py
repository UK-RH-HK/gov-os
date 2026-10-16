"""KPI 5: a reopened FULL ticket with an earlier-round probe record and a passing later one passes the probe gate.

KPI 5 [W2-M209, W2-L111]. W2-M209: "The gate judges only the latest probe record, or each record against its own
round." W2-L111: "Only the probe record of the closing commit is judged." DEC-500 listed the residual: "a record
of an earlier round refuses beside a passing one, so the orchestrator keeps only the record of the final code".
This repository keeps both rounds' records of W1-41 (``docs/probes/DAEO-cdoi/PR-DAEO-cdoi.md``, probed at
``920229dc``, and ``PR-DAEO-cdoi-round-DEC-694.md``, probed at ``dc14bf4e``).

Each case holds what both readings of W2-M209 share: the record of the final code (its probed commit is the
latest, and nothing of the ticket's code changed after it) decides; an earlier round's record, whose probed
commit is an ancestor of the later one, neither passes nor refuses the close. Both orders of the two files'
names are held, so the order in which records are read does not decide.

The other side, held as today: a reopened ticket whose only record is the earlier round's refuses (its code
changed after that probe), and a later record that fails refuses beside an earlier passing one. W1-30's
``test_a_failing_probe_record_beside_a_passing_one_refuses`` (two records of the same, final code, one failing)
is not reversed by this line and stands.

The project: FULL ticket ``PROJ-rond``. Round one: its work, probed, recorded, and the ticket closed by
``gov close`` itself. Then the ticket is reopened by the orchestrator, round two changes its code, and the
second round is probed and recorded.
"""

import pytest

import w2_01_support as support

TICKET, WBS = "PROJ-rond", "W1-rond"
FEATURE = "src/example/feature.py"
TICKET_TRAILERS = support.trailers_of(TICKET, role="orchestrator")

NAMES = {
    "the later record under a round name": (f"PR-{TICKET}", f"PR-{TICKET}-round-2"),
    "the earlier record under a round name": (f"PR-{TICKET}-round-1", f"PR-{TICKET}"),
}


def _round_one_closed(project, sandbox, interface, name):
    """Round one, closed by ``gov close``; what the close left is committed by the orchestrator. Returns the
    probed commit of round one."""
    support.create_ticket(project, TICKET, WBS, profile="FULL")
    probed = support.engineer_commit(project, TICKET, {FEATURE: "# feature, round one\n"})
    support.probe_recorded(project, TICKET, probed, name=name)
    support.checkpointed(project, TICKET)
    support.closed(support.run_close(project, sandbox, TICKET), interface)
    assert support.base.ticket_status(project.root, TICKET) == "closed", "the fixture is wrong: round one is open"
    if project.waiting_paths():
        project.commit("what the close of round one left", who=support.ORCHESTRATOR, trailers=TICKET_TRAILERS,
                       exact=True)
    return probed


def _round_one_record(project):
    """The close record of round one, as committed."""
    return support.git(project, "show", f"HEAD:docs/close/{TICKET}/CL-{TICKET}.md")


def _round_two_not_closed(project, record):
    """Nothing of round two's close happened: the ticket is in progress and round one's close record stands."""
    assert support.base.ticket_status(project.root, TICKET) == "in_progress", \
        f"the ticket's status is {support.base.ticket_status(project.root, TICKET)!r} after a refused close"
    now = (project.root / f"docs/close/{TICKET}/CL-{TICKET}.md").read_text(encoding="utf-8")
    assert now == record, "a refused close of round two rewrote round one's close record"


def _reopened_and_round_two(project):
    """The orchestrator reopens the ticket (a commit of the ticket); round two changes its code. Returns the
    head of round two, the commit its probe probes."""
    support.set_status(project, TICKET, "in_progress", trailers=TICKET_TRAILERS)
    return support.engineer_commit(project, TICKET, {FEATURE: "# feature, round two\n"})


@pytest.mark.parametrize("names", tuple(NAMES))
def test_a_reopened_ticket_with_an_earlier_record_and_a_passing_later_one_closes(names, project, sandbox,
                                                                                interface):
    earlier, later = NAMES[names]
    _round_one_closed(project, sandbox, interface, earlier)
    probed = _reopened_and_round_two(project)
    support.probe_recorded(project, TICKET, probed, name=later)
    support.checkpointed(project, TICKET)

    run = support.run_close(project, sandbox, TICKET)

    support.closed(run, interface)
    assert support.base.ticket_status(project.root, TICKET) == "closed"


def test_a_fix_round_after_a_failing_probe_closes_on_the_passing_record_of_the_fix(project, sandbox, interface):
    """Round one's probe failed, so the ticket was not closed; the fix round is probed and passes. The failing
    record is of round one's code, not of the final code (DEC-500: "a record that says the probe of the final
    code failed refuses")."""
    support.create_ticket(project, TICKET, WBS, profile="FULL")
    first = support.engineer_commit(project, TICKET, {FEATURE: "# feature, round one\n"})
    support.probe_recorded(project, TICKET, first, judgement="fail", name=f"PR-{TICKET}")
    fixed = support.engineer_commit(project, TICKET, {FEATURE: "# feature, fixed\n"})
    support.probe_recorded(project, TICKET, fixed, name=f"PR-{TICKET}-round-2")
    support.checkpointed(project, TICKET)

    run = support.run_close(project, sandbox, TICKET)

    support.closed(run, interface)


# --------------------------------------------------------------------------
# The other side, as today
# --------------------------------------------------------------------------

def test_a_reopened_ticket_with_only_the_earlier_record_still_refuses(project, sandbox, interface):
    _round_one_closed(project, sandbox, interface, f"PR-{TICKET}")
    record = _round_one_record(project)
    later = _reopened_and_round_two(project)
    support.checkpointed(project, TICKET)

    run = support.run_close(project, sandbox, TICKET)

    error = support.refused(run, interface)
    said = [text for text in support.strings_of(error) if "probe" in text.lower() and later[:7] in text]
    assert said, f"the probe gate does not refuse round two's commit {later[:12]}, never probed\n{run.describe()}"
    _round_two_not_closed(project, record)


@pytest.mark.parametrize("names", tuple(NAMES))
def test_a_failing_later_record_beside_a_passing_earlier_one_refuses(names, project, sandbox, interface):
    """Refused today too, but by round one's record (the gate stops at its first finding); the refusal must be the
    later record's judgement."""
    earlier, later = NAMES[names]
    _round_one_closed(project, sandbox, interface, earlier)
    record = _round_one_record(project)
    probed = _reopened_and_round_two(project)
    support.probe_recorded(project, TICKET, probed, judgement="fail", name=later)
    support.checkpointed(project, TICKET)

    run = support.run_close(project, sandbox, TICKET)

    error = support.refused(run, interface)
    assert "judgement" in support.text_of(error).lower(), \
        f"the failing record of the final code does not refuse by its judgement\n{run.describe()}"
    _round_two_not_closed(project, record)
