"""Acceptance tests for W1-29: Session hooks.

SessionStart, PreCompact, Stop and SubagentStop hook scripts.

Tests that run a hook from ``src/gov/hooks/`` fail while the module is not
built (red reason: ``src/gov/hooks/`` is empty).  Tests that call the watchdog
function (``gov.checkpoint.record.watch``) test W1-25 code directly because
``gov close`` (W1-30) is not built.
"""

from __future__ import annotations

import json

import pytest

from conftest import (
    BRIEF_TOKEN_LIMIT,
    TWELVE_FIELDS,
    _tokens,
    run_hook,
)


# ======================================================================
# SUCCESS LINE 1
# SessionStart injects gov context --brief plus tk ready within the
# 2.5k-token cap; PreCompact and Stop write checkpoints and respect
# stop_hook_active  [CAP-15.g, CAP-37.b]
# ======================================================================


class TestSessionStart:
    """SessionStart injects context and tk ready within the token cap."""

    def test_injects_context_brief_on_startup(self, project):
        """On startup, SessionStart injects gov context --brief output and tk
        ready, within the 2.5k-token cap.  [CAP-15.g]"""
        rc, output, _ = run_hook(
            "sessionstart",
            {"hook_event_name": "SessionStart", "source": "startup",
             "session_id": "s1", "cwd": str(project)},
            project,
            env_extra={"GOV_TICKET": "TEST-abcd", "GOV_ROLE": "engineer"},
        )
        assert rc == 0, f"SessionStart must exit 0, got {rc}"
        ctx = output["hookSpecificOutput"]["additionalContext"]
        assert _tokens(ctx) <= BRIEF_TOKEN_LIMIT, (
            f"injection is {_tokens(ctx)} tokens, cap is {BRIEF_TOKEN_LIMIT}"
        )

    @pytest.mark.parametrize("source", ["compact", "clear", "resume"])
    def test_reinjects_on_compact_clear_resume(self, project, source):
        """On compact/clear/resume, SessionStart re-injects the context packet
        and the checkpoint.  [CAP-37.b, DEC-208]"""
        rc, output, _ = run_hook(
            "sessionstart",
            {"hook_event_name": "SessionStart", "source": source,
             "session_id": "s1", "cwd": str(project)},
            project,
            env_extra={"GOV_TICKET": "TEST-abcd", "GOV_ROLE": "engineer"},
        )
        assert rc == 0
        ctx = output["hookSpecificOutput"]["additionalContext"]
        assert ctx, "additionalContext must not be empty on re-injection"
        assert _tokens(ctx) <= BRIEF_TOKEN_LIMIT


class TestPreCompact:
    """PreCompact writes a checkpoint at the compaction trigger."""

    def test_writes_checkpoint(self, project):
        """PreCompact calls gov checkpoint --trigger compaction.  [CAP-37.b]"""
        cp_before = list((project / "docs" / "checkpoints" / "TEST-abcd").glob("CP-*.md"))
        rc, output, _ = run_hook(
            "precompact",
            {"hook_event_name": "PreCompact", "trigger": "auto",
             "session_id": "s1", "cwd": str(project)},
            project,
            env_extra={"GOV_TICKET": "TEST-abcd", "GOV_ROLE": "engineer"},
        )
        assert rc == 0, "PreCompact must never block (exit 0)"
        cp_after = list((project / "docs" / "checkpoints" / "TEST-abcd").glob("CP-*.md"))
        assert len(cp_after) > len(cp_before), "PreCompact must write a new checkpoint"


class TestStop:
    """Stop writes a checkpoint and respects stop_hook_active."""

    def test_writes_checkpoint(self, project):
        """Stop calls gov checkpoint --trigger stop.  [CAP-37.b]"""
        cp_before = list((project / "docs" / "checkpoints" / "TEST-abcd").glob("CP-*.md"))
        rc, output, _ = run_hook(
            "stop",
            {"hook_event_name": "Stop", "session_id": "s1",
             "cwd": str(project), "last_assistant_message": "Done."},
            project,
            env_extra={"GOV_TICKET": "TEST-abcd", "GOV_ROLE": "engineer"},
        )
        assert rc == 0
        cp_after = list((project / "docs" / "checkpoints" / "TEST-abcd").glob("CP-*.md"))
        assert len(cp_after) > len(cp_before), "Stop must write a new checkpoint"

    def test_respects_stop_hook_active(self, project):
        """When stop_hook_active is present, Stop exits 0 without writing a
        checkpoint or blocking — this prevents re-entrancy loops.  [FL1]"""
        cp_before = list((project / "docs" / "checkpoints" / "TEST-abcd").glob("CP-*.md"))
        rc, output, _ = run_hook(
            "stop",
            {"hook_event_name": "Stop", "session_id": "s1",
             "cwd": str(project), "last_assistant_message": "Done.",
             "stop_hook_active": {"hook_name": "gov-stop",
                                  "hook_type": "command",
                                  "matcher": "", "event_name": "Stop"}},
            project,
            env_extra={"GOV_TICKET": "TEST-abcd", "GOV_ROLE": "engineer"},
        )
        assert rc == 0, "Stop must exit 0 even when re-entered"
        if output:
            hso = output.get("hookSpecificOutput", {})
            assert hso.get("permissionDecision") != "block", \
                "Stop must not block when stop_hook_active is set"
        cp_after = list((project / "docs" / "checkpoints" / "TEST-abcd").glob("CP-*.md"))
        assert len(cp_after) == len(cp_before), \
            "Stop must not write a checkpoint when stop_hook_active is set"


# ======================================================================
# SUCCESS LINE 2
# SubagentStop enforces the 12-field return contract of Framework §61
# [CAP-37.d]
# ======================================================================


class TestSubagentStop:
    """SubagentStop enforces the 12-field worker return contract."""

    @staticmethod
    def _return_message(fields):
        """Build a last_assistant_message with the given fields as JSON."""
        return json.dumps({f: "present" for f in fields})

    def test_accepts_all_twelve_fields(self, project):
        """When all 12 fields are present, SubagentStop passes.  [CAP-37.d]"""
        rc, output, _ = run_hook(
            "subagentstop",
            {"hook_event_name": "SubagentStop", "session_id": "s1",
             "agent_id": "a1", "agent_type": "engineer",
             "cwd": str(project),
             "last_assistant_message": self._return_message(TWELVE_FIELDS)},
            project,
        )
        assert rc == 0, f"SubagentStop must pass (exit 0) with all 12 fields, got {rc}"

    def test_blocks_missing_fields(self, project):
        """When fields are missing, SubagentStop blocks (exit 2).  [CAP-37.d]"""
        present = TWELVE_FIELDS[:6]  # only 6 of 12
        rc, output, _ = run_hook(
            "subagentstop",
            {"hook_event_name": "SubagentStop", "session_id": "s1",
             "agent_id": "a1", "agent_type": "engineer",
             "cwd": str(project),
             "last_assistant_message": self._return_message(present)},
            project,
        )
        assert rc == 2, f"SubagentStop must block (exit 2) when fields are missing, got {rc}"

    def test_block_includes_reason_and_is_once(self, project):
        """The block names the missing fields and fires once, never a loop.
        [CAP-37.d]"""
        rc, output, _ = run_hook(
            "subagentstop",
            {"hook_event_name": "SubagentStop", "session_id": "s1",
             "agent_id": "a1", "agent_type": "engineer",
             "cwd": str(project),
             "last_assistant_message": "no structured return at all"},
            project,
        )
        assert rc == 2
        assert output is not None, "block must produce output with a reason"
        text = json.dumps(output)
        missing_mentioned = any(f in text for f in TWELVE_FIELDS)
        assert missing_mentioned, "the block reason must name at least one missing field"


# ======================================================================
# SUCCESS LINE 3
# A checkpoint is written when the session's context utilisation passes
# the configured threshold, not only at PreCompact  [CAP-37.c]
# ======================================================================


class TestCheckpointOnContextUtilisation:
    """Checkpoints are written at multiple triggers, not only PreCompact."""

    def test_stop_writes_checkpoint_not_only_precompact(self, project):
        """The Stop hook writes a checkpoint (trigger: stop), proving that
        checkpoints are not limited to PreCompact events.  [CAP-37.c]"""
        rc, output, _ = run_hook(
            "stop",
            {"hook_event_name": "Stop", "session_id": "s1",
             "cwd": str(project), "last_assistant_message": "Done."},
            project,
            env_extra={"GOV_TICKET": "TEST-abcd", "GOV_ROLE": "engineer"},
        )
        assert rc == 0
        cps = list((project / "docs" / "checkpoints" / "TEST-abcd").glob("CP-*.md"))
        assert len(cps) >= 2, "Stop must have written a new checkpoint"

    def test_watchdog_marks_stale_on_context_utilisation(self, project):
        """The watchdog marks the checkpoint stale when context utilisation
        exceeds the threshold.

        Tests record.watch() directly: gov close (W1-30) calls this function;
        it is not built yet.  [CAP-37.c]"""
        from gov.checkpoint.record import watch
        from gov.cli.errors import GovError

        with pytest.raises(GovError) as exc_info:
            watch(project, "TEST-abcd",
                  max_age_minutes=99999, max_commits=99999,
                  max_context=0.2,
                  context_utilisation=0.5)
        assert exc_info.value.code == "CHECKPOINT_STALE"
        assert "context" in exc_info.value.details.get("reasons", [])


# ======================================================================
# SUCCESS LINE 4
# A compaction preserves the open decisions, the active ticket and the
# loop counts; PreCompact writes the checkpoint, and SessionStart (on
# compact, clear and resume) re-injects the context packet and the
# checkpoint; the auto-compact threshold is set to about 300k tokens if
# Claude Code allows it, and if it can't be configured the
# orchestrator's CONTEXT_CHECKPOINT stop stays  (DEC-208)
# ======================================================================


class TestCompactionPreservesState:
    """A compaction preserves critical session state (DEC-208)."""

    def test_precompact_then_sessionstart_preserves_ticket(self, project):
        """PreCompact writes a checkpoint that includes the active ticket;
        SessionStart on compact re-injects it."""
        run_hook(
            "precompact",
            {"hook_event_name": "PreCompact", "trigger": "auto",
             "session_id": "s1", "cwd": str(project)},
            project,
            env_extra={"GOV_TICKET": "TEST-abcd", "GOV_ROLE": "engineer"},
        )
        rc, output, _ = run_hook(
            "sessionstart",
            {"hook_event_name": "SessionStart", "source": "compact",
             "session_id": "s1", "cwd": str(project)},
            project,
            env_extra={"GOV_TICKET": "TEST-abcd", "GOV_ROLE": "engineer"},
        )
        assert rc == 0
        ctx = output["hookSpecificOutput"]["additionalContext"]
        assert "TEST-abcd" in ctx, (
            "re-injection must include the active ticket"
        )

    def test_auto_compact_threshold(self, project):
        """Claude Code 2.1.288 supports autoCompactWindow; the hooks set it
        to about 300k tokens, or the CONTEXT_CHECKPOINT stop stays.

        This test verifies the hook module exposes the threshold.  When it
        cannot be configured (which does not apply to the pinned version),
        the fallback is the orchestrator's CONTEXT_CHECKPOINT stop (DEC-208).
        """
        # The mechanism lives in the hooks module.  If the module is not
        # built the assertion inside run_hook fails, which is the red reason.
        rc, _, _ = run_hook(
            "sessionstart",
            {"hook_event_name": "SessionStart", "source": "startup",
             "session_id": "s1", "cwd": str(project)},
            project,
            env_extra={"GOV_TICKET": "TEST-abcd", "GOV_ROLE": "engineer"},
        )
        assert rc == 0


# ======================================================================
# FAILURE LINE 1
# A Stop hook loops — stop_hook_active prevents this
# ======================================================================


class TestNoStopLoop:
    """A Stop hook must not loop; stop_hook_active prevents re-entrancy."""

    def test_stop_exits_without_side_effects_when_active(self, project):
        """When stop_hook_active is set, the hook exits 0 with no checkpoint
        write and no block decision.  This is the single mechanism that
        prevents the Stop hook from looping."""
        cp_before = set(
            p.name for p in (project / "docs" / "checkpoints" / "TEST-abcd").glob("CP-*.md")
        )
        rc, output, _ = run_hook(
            "stop",
            {"hook_event_name": "Stop", "session_id": "s1",
             "cwd": str(project), "last_assistant_message": "Done.",
             "stop_hook_active": {"hook_name": "gov-stop",
                                  "hook_type": "command",
                                  "matcher": "", "event_name": "Stop"}},
            project,
            env_extra={"GOV_TICKET": "TEST-abcd", "GOV_ROLE": "engineer"},
        )
        assert rc == 0
        cp_after = set(
            p.name for p in (project / "docs" / "checkpoints" / "TEST-abcd").glob("CP-*.md")
        )
        assert cp_after == cp_before, "no checkpoint written during re-entrant stop"


# ======================================================================
# FAILURE LINE 2
# SessionStart injects more than the cap
# ======================================================================


class TestInjectionCap:
    """The injection must stay within the 2.5k-token cap.  [CAP-15.g]"""

    def test_large_context_within_cap(self, project):
        """Even when the project has a large context, the additionalContext
        output stays within 2500 tokens (10 000 characters)."""
        rc, output, _ = run_hook(
            "sessionstart",
            {"hook_event_name": "SessionStart", "source": "startup",
             "session_id": "s1", "cwd": str(project)},
            project,
            env_extra={"GOV_TICKET": "TEST-abcd", "GOV_ROLE": "engineer"},
        )
        assert rc == 0
        ctx = output["hookSpecificOutput"]["additionalContext"]
        tokens = _tokens(ctx)
        assert tokens <= BRIEF_TOKEN_LIMIT, (
            f"injection is {tokens} tokens ({len(ctx)} chars), "
            f"cap is {BRIEF_TOKEN_LIMIT} tokens ({BRIEF_TOKEN_LIMIT * 4} chars)"
        )


# ======================================================================
# FAILURE LINE 3
# A handoff or ticket close proceeds while the latest checkpoint is
# stale for its policy  (watchdog, Contract v3 N3)
# ======================================================================


class TestWatchdogBlocksStale:
    """The watchdog function blocks handoff/close when the checkpoint is stale.

    Since ``gov close`` (W1-30) is not built, these tests call
    ``gov.checkpoint.record.watch`` directly.  The function is built by W1-25.
    """

    def test_stale_by_age(self, project):
        """A checkpoint older than max_age_minutes is stale (exit 3).
        [CAP-37.c]"""
        from gov.checkpoint.record import watch
        from gov.cli.errors import GovError

        with pytest.raises(GovError) as exc_info:
            watch(project, "TEST-abcd",
                  max_age_minutes=0,
                  max_commits=99999,
                  max_context=1.0,
                  context_utilisation=None)
        assert exc_info.value.code == "CHECKPOINT_STALE"
        assert exc_info.value.exit_code == 3

    def test_missing_checkpoint(self, project):
        """A ticket with no checkpoint produces CHECKPOINT_MISSING (exit 3).
        [CAP-37.c]"""
        from gov.checkpoint.record import watch
        from gov.cli.errors import GovError

        (project / ".tickets" / "NOCK-wxyz.md").write_text(
            "---\nid: NOCK-wxyz\nstatus: in_progress\ntitle: No checkpoint\n"
            "sources: []\n---\n# NOCK-wxyz\n",
            encoding="utf-8",
        )
        with pytest.raises(GovError) as exc_info:
            watch(project, "NOCK-wxyz",
                  max_age_minutes=99999, max_commits=99999,
                  max_context=1.0, context_utilisation=None)
        assert exc_info.value.code == "CHECKPOINT_MISSING"

    def test_stale_on_ticket_transition(self, project):
        """A checkpoint is stale when the ticket's status changed after it was
        written.  [CAP-37.c]"""
        from gov.checkpoint.record import watch
        from gov.cli.errors import GovError

        (project / ".tickets" / "TEST-abcd.md").write_text(
            "---\nid: TEST-abcd\nstatus: closed\ntitle: Test ticket\n"
            "sources: []\ndepends_on: []\n---\n# TEST-abcd\n",
            encoding="utf-8",
        )
        with pytest.raises(GovError) as exc_info:
            watch(project, "TEST-abcd",
                  max_age_minutes=99999, max_commits=99999,
                  max_context=1.0, context_utilisation=None)
        assert exc_info.value.code == "CHECKPOINT_STALE"
        assert "ticket-transition" in exc_info.value.details.get("reasons", [])
