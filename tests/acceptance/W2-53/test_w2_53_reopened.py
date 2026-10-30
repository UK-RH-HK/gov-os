"""KPI 3: a reopened FULL ticket whose earlier round was merged back before its final probe.

KPI 3 [DEC-754]: "A reopened FULL ticket whose earlier round was merged back before its final probe closes when the
probed code at the closed head is the final probed code." Round 4's finding 3
(``docs/probes/DAEO-g0ip/PR-DAEO-g0ip-round-4.md``): such a ticket cannot close; the earlier merge-back is judged
against the final probed commit (fails closed).

The project: FULL ticket ``PROJ-ropn`` is created on ``main`` and worked on ``work``. Round one's head is probed;
its record is committed on the branch, and the branch is merged back. The ticket is reopened for a second round on
the same branch; round two's head is probed (the final probe) and merged back; its record and the checkpoint are
committed on ``main``, where the close runs. Round one's record is an earlier round's (its probed commit is an
ancestor of the final one): it neither passes nor refuses (W2-01's KPI 5).
"""

import pytest

import w2_53_support as support

TICKET, WBS = "PROJ-ropn", "W1-ropn"
BRANCH = "work"
FEATURE = "src/example/feature.py"
ROUND_ONE = "# the feature, round one\n"
ROUND_TWO = "# the feature, round two\n"
MERGE_TRAILERS = support.trailers_of(TICKET, role="orchestrator")

FINAL_MERGE_BACKS = ("brings the final probed code", "keeps round one's code")


@pytest.mark.parametrize("final", FINAL_MERGE_BACKS)
def test_a_reopened_ticket_whose_first_round_was_merged_back_is_judged_by_the_final_probed_code(
        final, project, sandbox, interface):
    support.create_ticket(project, TICKET, WBS, profile="FULL")
    project.checkout(BRANCH, create=True)
    first = support.engineer_commit(project, TICKET, {FEATURE: ROUND_ONE})
    support.probe_recorded(project, TICKET, first, name=f"PR-{TICKET}-round-1")
    project.checkout("main")
    first_back = project.merge(BRANCH, MERGE_TRAILERS, message="merge the ticket's branch, round one")

    project.checkout(BRANCH)
    probed = support.engineer_commit(project, TICKET, {FEATURE: ROUND_TWO}, message="round two")
    project.checkout("main")
    edit = {FEATURE: ROUND_ONE} if final == FINAL_MERGE_BACKS[1] else None
    final_back = project.merge(BRANCH, MERGE_TRAILERS, edit=edit, message="merge the ticket's branch, round two")
    support.probe_recorded(project, TICKET, probed)
    support.checkpointed(project, TICKET)
    assert support.holds(project, first, first_back) and not support.holds(project, probed, first_back), \
        "the fixture is wrong: round one's merge-back does not hold round one's probe alone"
    assert support.holds(project, first, probed), "the fixture is wrong: round two does not follow round one"

    run = support.run_close(project, sandbox, TICKET)

    if final == FINAL_MERGE_BACKS[0]:
        assert support.content_at(project, "HEAD", FEATURE) == support.content_at(project, probed, FEATURE), \
            "the fixture is wrong: the closed head does not hold the final probed code"
        assert not support.probe_statements(run.envelope().get("error") or {}), \
            f"the probe gate refuses the reopened ticket: round one's merge-back {first_back[:12]} is judged " \
            f"against the final probed commit {probed[:12]}\n{run.describe()}"
        support.closed(run, interface)
    else:
        error = support.refused(run, interface)
        assert support.probe_gate_names(error, final_back), \
            f"the probe gate does not refuse the final merge-back {final_back[:12]}, which keeps round one's code " \
            f"at the closed head\n{run.describe()}"
        support.base.assert_not_closed(project, TICKET)
