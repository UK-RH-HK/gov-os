"""W1-49 -- the PreCompact hook and the checkpoint's currency.

KPI success 1 [CAP-37.g]: "A PreCompact hook ensures the orchestrator's checkpoint
is current, and in a worktree the lead's (DEC-248)".
KPI failure 1: "A compaction proceeds while the checkpoint is not current, and
nothing says so".

**The two fixtures.** A *current* checkpoint was written this minute: after the
last commit (an hour ago) and after the transcript's last write (ten minutes
ago). A *stale* one is three days old: older than the last commit and older than
the transcript. Whatever "current" is measured against (decision package DP-1),
the first is current and the second is not. A missing checkpoint is not current.

**What stands on what.** The first part needs no decision. The second part
stands on the recommendation of DP-1 (a manual compaction is blocked, an
automatic one is not blocked and the session is told afterwards), the third on
the recommendation of DP-2 (the hooks act for the orchestrator role only).
"""

from __future__ import annotations

import pytest

import w1_49_support as support

ORCH = support.ORCHESTRATOR_CHECKPOINT_REL
LEAD = support.LEAD_CHECKPOINT_REL
TRIGGERS = ("manual", "auto")


def _checkpoint(tree, rel, prefix, age_s=0.0):
    return support.write_checkpoint(tree, rel, support.checkpoint_text(support.resume_section(prefix)), age_s)


# --------------------------------------------------------------------------
# Independent of the decision packages
# --------------------------------------------------------------------------

@pytest.mark.parametrize("trigger", TRIGGERS)
def test_a_current_orchestrator_checkpoint_lets_the_compaction_proceed(run, project, trigger):
    """Success 1 [CAP-37.g]: exit code 0, and nothing calls the checkpoint stale."""
    _checkpoint(project, ORCH, "ZQ")
    result = run.precompact(project, trigger)
    assert result.returncode == 0, f"a current checkpoint did not let the {trigger} compaction proceed: {result.describe()}"
    assert support.NOT_CURRENT not in result.said, f"a current checkpoint is reported as not current: {result.describe()}"


@pytest.mark.parametrize("trigger", TRIGGERS)
@pytest.mark.parametrize("state", ("stale", "missing"))
def test_a_checkpoint_that_is_not_current_is_said_so(run, project, trigger, state):
    """Failure 1: the hook names the checkpoint and says it is not current, whether or not it blocks."""
    if state == "stale":
        _checkpoint(project, ORCH, "ZQ", age_s=support.STALE_AGE_S)
    result = run.precompact(project, trigger, transcript_age_s=0.0)
    assert support.NOT_CURRENT in result.said and ORCH in result.said, (
        f"the orchestrator's checkpoint is {state} and the hook did not say `{support.NOT_CURRENT}` with its path "
        f"on a {trigger} compaction: {result.describe()}"
    )


def test_in_a_worktree_the_leads_checkpoint_is_the_one_checked(run, project, worktree):
    """Success 1: "in a worktree the lead's". The main tree's orchestrator checkpoint is current; the lead's is stale."""
    _checkpoint(project, ORCH, "ZQ")
    _checkpoint(worktree, LEAD, "LD", age_s=support.STALE_AGE_S)
    result = run.precompact(worktree, "manual", transcript_age_s=0.0)
    assert support.NOT_CURRENT in result.said and LEAD in result.said, (
        f"the lead's stale checkpoint was not reported in its worktree: {result.describe()}"
    )


def test_in_a_worktree_a_current_lead_checkpoint_is_enough(run, project, worktree):
    """Success 1: the orchestrator's checkpoint in the main tree is stale, and that is not the lead's business."""
    _checkpoint(project, ORCH, "ZQ", age_s=support.STALE_AGE_S)
    _checkpoint(worktree, LEAD, "LD")
    result = run.precompact(worktree, "auto")
    assert result.returncode == 0 and support.NOT_CURRENT not in result.said, (
        f"a current lead checkpoint did not let the compaction proceed in the worktree: {result.describe()}"
    )


def test_a_worktree_without_a_lead_checkpoint_is_not_current(run, project, worktree):
    _checkpoint(project, ORCH, "ZQ")
    result = run.precompact(worktree, "auto", transcript_age_s=0.0)
    assert support.NOT_CURRENT in result.said and LEAD in result.said, (
        f"a worktree with no lead checkpoint was not reported: {result.describe()}"
    )


@pytest.mark.parametrize("trigger", TRIGGERS)
def test_a_hook_that_cannot_read_its_input_does_not_block_the_compaction(run, project, trigger):
    """A failure of the hook itself is not a stale checkpoint: only exit code 2 blocks, and it must not be used here."""
    _checkpoint(project, ORCH, "ZQ")
    result = run.precompact(project, trigger, stdin="this is not JSON")
    assert result.returncode is not None and result.returncode != 2, (
        f"the hook blocked the compaction on input it could not read: {result.describe()}"
    )


# --------------------------------------------------------------------------
# On the recommendation of DP-1: block a manual compaction, tell the session after an automatic one
# --------------------------------------------------------------------------

@pytest.mark.parametrize("state", ("stale", "missing"))
def test_a_manual_compaction_is_blocked_while_the_checkpoint_is_not_current(run, project, state):
    """DP-1 (a). Exit code 2 blocks the compaction and stderr is shown to whoever typed /compact."""
    if state == "stale":
        _checkpoint(project, ORCH, "ZQ", age_s=support.STALE_AGE_S)
    result = run.precompact(project, "manual", transcript_age_s=0.0)
    assert result.returncode == 2, f"the manual compaction was not blocked ({state} checkpoint): {result.describe()}"
    assert support.NOT_CURRENT in result.stderr and ORCH in result.stderr, (
        f"the blocking reason on stderr does not name the checkpoint: {result.describe()}"
    )


def test_an_automatic_compaction_is_not_blocked_and_the_session_is_told_afterwards(run, project):
    """DP-1 (a). Nobody can update the checkpoint from inside a PreCompact hook, so the model is told at SessionStart."""
    _checkpoint(project, ORCH, "ZQ", age_s=support.STALE_AGE_S)
    before = run.precompact(project, "auto", transcript_age_s=0.0)
    assert before.returncode == 0, f"the automatic compaction was blocked: {before.describe()}"
    after = run.sessionstart(project, "compact")
    assert support.NOT_CURRENT in after.injection and ORCH in after.injection, (
        f"after a compaction over a stale checkpoint the injection does not say so: {after.injection[:400]!r}"
    )
    support.assert_within_cap(after)


def test_after_a_compaction_over_a_current_checkpoint_the_session_is_not_warned(run, project):
    _checkpoint(project, ORCH, "ZQ")
    assert run.precompact(project, "auto").returncode == 0
    after = run.sessionstart(project, "compact")
    assert support.NOT_CURRENT not in after.injection, (
        f"the injection calls a current checkpoint not current: {after.injection[:400]!r}"
    )


# --------------------------------------------------------------------------
# On the recommendation of DP-2: a worker session is left alone
# --------------------------------------------------------------------------

@pytest.mark.parametrize("role", support.WORKER_ROLES)
def test_a_workers_compaction_is_not_blocked_by_the_leads_checkpoint(run, project, worktree, role):
    """DP-2 (a). A worker shares the lead's worktree; the lead's stale checkpoint is not the worker's to repair."""
    _checkpoint(worktree, LEAD, "LD", age_s=support.STALE_AGE_S)
    result = run.precompact(worktree, "manual", role=role, transcript_age_s=0.0)
    assert result.returncode == 0, f"a {role} session's compaction was blocked: {result.describe()}"
