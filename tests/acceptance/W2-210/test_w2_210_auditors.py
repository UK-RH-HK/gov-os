"""V4: the verdict is computed by code alone; the independence is carried by the three Independent Auditor records the
stage depends on (A5's, A7's, A10's), which the stage re-reads by code and lists under ``auditors`` [CAP-44.h
("from a fresh Independent Auditor"); lite_gates.AUDITOR].

The cases that plant a failure stand the live tools in (``compute``'s seam) so that exactly one condition is the
planted one. The restoring plants put an auditor record back byte for byte: its content is what the stage recorded,
only the commit that last touched it differs.
"""

from __future__ import annotations

import pytest

import w2_210_support as d1

support = d1.support

AUDITOR_CONDITION = {"A5": d1.A5_REVIEW, "A7": d1.LITE_A7, "A10": d1.LITE_A10}
SESSIONS = {"A5": support.AUDITOR_SESSION, "A7": d1.gates.GATE_SESSION["A7"], "A10": d1.gates.GATE_SESSION["A10"]}


def test_the_record_lists_the_three_auditors(adopted):
    """V4: ``auditors`` lists A5's, A7's and A10's records: path, sha256 (as it stands), commit (the one that last
    touched it), session (its own ``auditor_session``) and role (``independent-auditor``)."""
    result = d1.compute(adopted.project, tools=d1.healthy_tools())
    listed = {item["path"]: item for item in result["auditors"]}
    assert set(listed) == set(d1.AUDITOR.values()) and len(result["auditors"]) == 3, result["auditors"]
    for stage, rel in d1.AUDITOR.items():
        item = listed[rel]
        assert item["sha256"] == d1.sha256_at_head(adopted.project, rel)
        assert item["commit"] == d1.last_commit(adopted.project, rel)
        assert item["session"] == SESSIONS[stage]
        assert item["role"] == d1.AUDITOR_ROLE


def test_the_committed_record_lists_the_three_auditors(cli_plain):
    d1.taken(cli_plain)
    front, _ = d1.record_at_head(cli_plain.project)
    assert sorted(item["path"] for item in front["auditors"]) == sorted(d1.AUDITOR.values())


ROLES = {"engineer": ("engineer",), "no-role": (), "auditor-and-engineer": ("independent-auditor", "engineer"),
         "orchestrator": ("orchestrator",)}


@pytest.mark.parametrize("roles", sorted(ROLES))
@pytest.mark.parametrize("stage", sorted(AUDITOR_CONDITION))
def test_an_auditor_record_brought_by_a_commit_with_another_role_makes_its_stage_not_met(adopted, stage, roles):
    """V4: the commit that last touched the auditor's record carries a Role other than ``independent-auditor``
    alone (or none): that stage's condition is ``not met``, the others as they were, the verdict
    NOT_ADOPTED_HEALTHY. The content is restored, so nothing but the role differs."""
    d1.restore_by(adopted.project, d1.AUDITOR[stage], ROLES[roles])
    result = d1.compute(adopted.project, tools=d1.healthy_tools())
    assert d1.not_met(result) == [AUDITOR_CONDITION[stage]], d1.states(result)
    assert result["verdict"] == "NOT_ADOPTED_HEALTHY"


@pytest.mark.parametrize("stage", sorted(AUDITOR_CONDITION))
def test_an_auditor_commit_that_also_wrote_the_adoptions_folder_makes_its_stage_not_met(adopted, stage):
    """V4: the commit carries ``Role: independent-auditor`` alone but wrote a file of ``governance/adoption/``:
    not independent (the A5 rule): that stage's condition is ``not met``."""
    d1.restore_by(adopted.project, d1.AUDITOR[stage], ("independent-auditor",), also=f"{d1.FOLDER}/notes-of-the-auditor.md")
    result = d1.compute(adopted.project, tools=d1.healthy_tools())
    assert d1.not_met(result) == [AUDITOR_CONDITION[stage]], d1.states(result)


@pytest.mark.parametrize("stage", sorted(AUDITOR_CONDITION))
def test_an_auditor_whose_session_is_this_stages_session_makes_its_stage_not_met(adopted, stage):
    """V4: ``auditor_session`` must differ from the session that runs the stage: the stage run with the auditor's own
    session as its ``--session`` finds that stage's condition ``not met`` (the others as they were)."""
    result = d1.compute(adopted.project, SESSIONS[stage], tools=d1.healthy_tools())
    assert d1.not_met(result) == [AUDITOR_CONDITION[stage]], d1.states(result)
    assert result["verdict"] == "NOT_ADOPTED_HEALTHY"


def _auditor_session_changed(project, stage, session):
    """The auditor's record carries ``session`` (None: the key removed), committed by the auditor; the gate's record
    that recorded the auditor is brought along (ordinary commit), so that only the session rule can fail."""
    rel = d1.AUDITOR[stage]

    def mutate(front):
        if session is None:
            front.pop("auditor_session", None)
        else:
            front["auditor_session"] = session
    d1.write_front(project, rel, mutate, f"the auditor's session in {rel}", f"Task: {d1.TICKET}",
                   f"Role: {d1.AUDITOR_ROLE}")

    def record(front):
        front["auditor"].update({"sha256": d1.sha256_at_head(project, rel), "commit": d1.last_commit(project, rel),
                                 "session": session})
    d1.write_front(project, d1.RECORD[stage], record, f"{stage}'s record names the auditor's record as it is",
                   f"Task: {d1.TICKET}")


@pytest.mark.parametrize("session", ["adopter-001", None], ids=["a-stages-session", "no-session"])
@pytest.mark.parametrize("stage", ["A7", "A10"])
def test_an_auditor_session_that_equals_a_stages_or_is_not_named_makes_its_stage_not_met(adopted, stage, session):
    """V4: an ``auditor_session`` equal to the session that ran the stages (the adopter's), or not named, fails the
    re-read: that gate's condition is ``not met`` and no other."""
    _auditor_session_changed(adopted.project, stage, session)
    result = d1.compute(adopted.project, tools=d1.healthy_tools())
    assert d1.not_met(result) == [AUDITOR_CONDITION[stage]], d1.states(result)
    assert result["verdict"] == "NOT_ADOPTED_HEALTHY"


def test_an_a7_auditor_record_by_another_role_gives_not_adopted_through_the_command_line(adopted):
    """V4 through the command line: A7's auditor record brought by an engineer's commit: NOT_ADOPTED_HEALTHY, the
    lite A7 gate named."""
    d1.restore_by(adopted.project, d1.AUDITOR["A7"], ("engineer",))
    outcome = d1.taken(d1.run_stage(adopted))
    error = d1.assert_refused(outcome, "ADOPT_NOT_ADOPTED")
    front, _ = d1.record_at_head(outcome.project)
    assert front["verdict"] == "NOT_ADOPTED_HEALTHY"
    assert d1.states_of(front)[d1.LITE_A7] == "not met" and d1.LITE_A7 in d1.json.dumps(error)
