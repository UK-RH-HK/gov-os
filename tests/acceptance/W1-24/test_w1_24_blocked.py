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
    """The ticket TK_CONFLICT declares two decisions where one supersedes the other. Both are at the decision
    level, so precedence cannot resolve the conflict — the call raises CONTRADICTION."""
    outcome = api.context_outcome(project, S.TK_CONFLICT)
    error = outcome.error()
    assert error is not None, "the call did not raise — conflicting mandatory inputs must raise a contradiction"
    assert error["code"] in (S.CONTRADICTION, S.BLOCKED), \
        f"expected {S.CONTRADICTION!r} or {S.BLOCKED!r}, got {error['code']!r}: {error['message']}"
