"""S5: a missing mandatory input makes gov context refuse with an explicit BLOCKED state; a superseded record
cannot satisfy a current requirement; conflicting mandatory inputs raise a contradiction (decision package or
repair ticket) [CAP-15.c].

Red reason: ``gov.context`` does not exist (``src/gov/context/`` is not built).
"""

from __future__ import annotations

import w1_24_support as S


def test_a_missing_mandatory_input_refuses_with_blocked(api, project):
    """The ticket TK_BLOCKED declares a source that does not exist in the store; the call raises BLOCKED."""
    outcome = api.context_outcome(project, S.TK_BLOCKED)
    error = outcome.error()
    assert error is not None, "the call did not raise — a missing mandatory input must refuse"
    assert error["code"] == S.BLOCKED, \
        f"expected error code {S.BLOCKED!r}, got {error['code']!r}: {error['message']}"
    assert S.GONE_ID in error["message"] or S.GONE_ID in str(error.get("details", "")), \
        f"the error does not name the missing id {S.GONE_ID!r}: {error['message']}"


def test_a_superseded_record_cannot_satisfy_a_requirement(api, project):
    """The ticket TK_SUPERSEDED declares a source whose status is SUPERSEDED; it cannot satisfy."""
    outcome = api.context_outcome(project, S.TK_SUPERSEDED)
    error = outcome.error()
    assert error is not None, "the call did not raise — a superseded record cannot satisfy a current requirement"
    assert error["code"] == S.BLOCKED, \
        f"expected error code {S.BLOCKED!r}, got {error['code']!r}: {error['message']}"


def test_conflicting_inputs_at_the_same_level_raise_a_contradiction(api, project):
    """The ticket TK_CONFLICT declares two decisions where one supersedes the other. ADR_CONFLICT_2
    supersedes ADR_CONFLICT_1, so ADR_CONFLICT_1 is superseded — the call raises BLOCKED (not CONTRADICTION,
    because the supersession edge resolves which record is stale)."""
    outcome = api.context_outcome(project, S.TK_CONFLICT)
    error = outcome.error()
    assert error is not None, "the call did not raise — a superseded mandatory input must refuse"
    assert error["code"] == S.BLOCKED, \
        f"expected {S.BLOCKED!r} (superseded record), got {error['code']!r}: {error['message']}"


def test_the_blocked_error_names_the_superseded_record(api, project):
    """When a mandatory input is superseded, the BLOCKED error names the id of the record that could not
    satisfy the requirement."""
    outcome = api.context_outcome(project, S.TK_SUPERSEDED)
    error = outcome.error()
    assert error is not None, "the call did not raise for a superseded record"
    combined = error["message"] + " " + str(error.get("details", ""))
    assert S.ADR_SUPERSEDED in combined, \
        f"the BLOCKED error does not name the superseded record {S.ADR_SUPERSEDED!r}: {error['message']}"


def test_a_record_superseded_by_several_records_cannot_satisfy(api, project):
    """A record that has been superseded by more than one successor is still SUPERSEDED; requiring it raises
    BLOCKED. This tests multi-superseder depth (ADR_MULTI_OLD is superseded by both ADR_A and ADR_B)."""
    outcome = api.context_outcome(project, S.TK_MULTI_SUP)
    error = outcome.error()
    assert error is not None, "the call did not raise — a record superseded by multiple successors must refuse"
    assert error["code"] == S.BLOCKED, \
        f"expected {S.BLOCKED!r}, got {error['code']!r}: {error['message']}"


def test_two_active_records_at_the_same_level_without_supersession_raise_contradiction(api, project):
    """Two ACTIVE decisions at the same level with no supersession edge between them are a genuine
    contradiction — the call raises CONTRADICTION (not BLOCKED)."""
    outcome = api.context_outcome(project, S.TK_PURE_CONFLICT)
    error = outcome.error()
    assert error is not None, "the call did not raise — two active records at the same level must raise"
    assert error["code"] == S.CONTRADICTION, \
        f"expected {S.CONTRADICTION!r} (pure contradiction), got {error['code']!r}: {error['message']}"
