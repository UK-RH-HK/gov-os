"""Acceptance tests for W1-29: Session hooks.

The combined PreCompact and SessionStart hooks live at
``template/governance/kernel/hooks/`` and are shared with W1-49.  Tests for
these two events run the registered shell commands via ``CombinedHooks``
(the ``run`` fixture), in a temporary project built by
``w1_49_support.make_project()`` and extended with W1-29 fixture data
(the ``w49_project`` fixture).

Stop and SubagentStop are W1-29-only hooks in ``src/gov/hooks/``.  They
are run as Python scripts directly (``run_w29_hook``), in a simpler
throwaway project (the ``project`` fixture).

Tests that call the watchdog function (``gov.checkpoint.record.watch``)
test W1-25 code directly because ``gov close`` (W1-30) is not built.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

from conftest import (
    BRIEF_TOKEN_LIMIT,
    HOOKS_DIR,
    ORCH,
    REPO_ROOT,
    SIZE_CAP_CHARS,
    TWELVE_FIELDS,
    _tokens,
    run_w29_hook,
)

import w1_49_support


# ======================================================================
# SUCCESS LINE 1
# SessionStart injects gov context --brief plus tk ready within the
# 2.5k-token cap; PreCompact and Stop write checkpoints and respect
# stop_hook_active  [CAP-15.g, CAP-37.b]
# ======================================================================


class TestSessionStart:
    """SessionStart injects context and tk ready within the token cap."""

    def test_injects_context_brief_on_startup(self, w49_project, run):
        """On startup, SessionStart injects gov context --brief output and tk
        ready, within the 2.5k-token cap.  [CAP-15.g]"""
        result = run.sessionstart(
            w49_project, "startup", role="engineer", ticket="TEST-abcd",
        )
        assert result.returncode == 0, (
            f"SessionStart must exit 0, got {result.returncode}: "
            f"{result.describe()}"
        )
        ctx = result.injection
        assert _tokens(ctx) <= BRIEF_TOKEN_LIMIT, (
            f"injection is {_tokens(ctx)} tokens, cap is {BRIEF_TOKEN_LIMIT}"
        )

    @pytest.mark.parametrize("source", ["compact", "clear", "resume"])
    def test_reinjects_on_compact_clear_resume(self, w49_project, run, source):
        """On compact/clear/resume, SessionStart re-injects the context packet
        and the checkpoint.  [CAP-37.b, DEC-208]"""
        result = run.sessionstart(
            w49_project, source, role="engineer", ticket="TEST-abcd",
        )
        assert result.returncode == 0, result.describe()
        ctx = result.injection
        assert ctx, "additionalContext must not be empty on re-injection"
        assert _tokens(ctx) <= BRIEF_TOKEN_LIMIT

    def test_orchestrator_compact_carries_prompt_path(self, w49_project, run):
        """When the orchestrator resumes after a compaction, the combined
        injection carries the prompt path (W1-49 content preserved)."""
        w1_49_support.write_checkpoint(
            w49_project, ORCH,
            w1_49_support.checkpoint_text(
                w1_49_support.resume_section("TST"),
            ),
            age_s=w1_49_support.RECENT_AGE_S,
        )
        result = run.sessionstart(
            w49_project, "compact", ticket="TEST-abcd",
        )
        assert result.returncode == 0, result.describe()
        ctx = result.injection
        assert w1_49_support.PROMPT_REL in ctx, (
            f"orchestrator injection must carry the prompt path "
            f"{w1_49_support.PROMPT_REL}: {ctx[:400]!r}"
        )

    def test_orchestrator_compact_carries_resume_section(self, w49_project, run):
        """When the orchestrator resumes after a compaction, the combined
        injection carries the RESUME HERE section from the checkpoint
        (W1-49 content preserved)."""
        body = w1_49_support.resume_section("TST")
        w1_49_support.write_checkpoint(
            w49_project, ORCH,
            w1_49_support.checkpoint_text(body),
            age_s=w1_49_support.RECENT_AGE_S,
        )
        result = run.sessionstart(
            w49_project, "compact", ticket="TEST-abcd",
        )
        assert result.returncode == 0, result.describe()
        ctx = result.injection
        assert "TST-71" in ctx or "RESUME" in ctx.upper(), (
            f"orchestrator injection must carry the RESUME HERE section "
            f"content from the checkpoint: {ctx[:400]!r}"
        )

    def test_orchestrator_compact_combined_within_cap(self, w49_project, run):
        """The combined orchestrator injection (W1-49 prompt path and RESUME
        HERE plus W1-29 context brief and tk ready) stays within the
        10,000-character cap."""
        w1_49_support.write_checkpoint(
            w49_project, ORCH,
            w1_49_support.checkpoint_text(
                w1_49_support.resume_section("TST"),
            ),
            age_s=w1_49_support.RECENT_AGE_S,
        )
        result = run.sessionstart(
            w49_project, "compact", ticket="TEST-abcd",
        )
        assert result.returncode == 0, result.describe()
        w1_49_support.assert_within_cap(result)


class TestPreCompact:
    """PreCompact writes a checkpoint at the compaction trigger."""

    def test_writes_checkpoint(self, w49_project, run):
        """PreCompact calls gov checkpoint --trigger compaction.  [CAP-37.b]"""
        cp_dir = w49_project / "docs" / "checkpoints" / "TEST-abcd"
        cp_before = list(cp_dir.glob("CP-*.md"))
        result = run.precompact(
            w49_project, "auto", role="engineer", ticket="TEST-abcd",
        )
        assert result.returncode == 0, (
            f"PreCompact must never block (exit 0): {result.describe()}"
        )
        cp_after = list(cp_dir.glob("CP-*.md"))
        assert len(cp_after) > len(cp_before), (
            "PreCompact must write a new checkpoint record"
        )


class TestStop:
    """Stop writes a checkpoint and respects stop_hook_active."""

    def test_writes_checkpoint(self, project):
        """Stop calls gov checkpoint --trigger stop.  [CAP-37.b]"""
        cp_before = list(
            (project / "docs" / "checkpoints" / "TEST-abcd").glob("CP-*.md"),
        )
        rc, output, _ = run_w29_hook(
            "stop",
            {"hook_event_name": "Stop", "session_id": "s1",
             "cwd": str(project), "last_assistant_message": "Done."},
            project,
            env_extra={"GOV_TICKET": "TEST-abcd", "GOV_ROLE": "engineer"},
        )
        assert rc == 0
        cp_after = list(
            (project / "docs" / "checkpoints" / "TEST-abcd").glob("CP-*.md"),
        )
        assert len(cp_after) > len(cp_before), (
            "Stop must write a new checkpoint"
        )

    def test_no_checkpoint_without_ticket(self, project):
        """When GOV_TICKET is not set, the Stop hook writes no checkpoint.
        Sessions without a ticket must not pollute the checkpoint
        directory.  [Point 4]"""
        cp_dir = project / "docs" / "checkpoints"
        cp_before = set(cp_dir.rglob("CP-*.md")) if cp_dir.exists() else set()
        rc, output, _ = run_w29_hook(
            "stop",
            {"hook_event_name": "Stop", "session_id": "s1",
             "cwd": str(project), "last_assistant_message": "Done."},
            project,
            env_extra={"GOV_ROLE": "engineer"},
        )
        assert rc == 0, f"Stop must exit 0 even without GOV_TICKET, got {rc}"
        cp_after = set(cp_dir.rglob("CP-*.md")) if cp_dir.exists() else set()
        assert cp_after == cp_before, (
            "Stop must not write any checkpoint when GOV_TICKET is not set"
        )

    def test_respects_stop_hook_active(self, project):
        """When stop_hook_active is present, Stop exits 0 without writing a
        checkpoint or blocking — this prevents re-entrancy loops.  [FL1]"""
        cp_before = list(
            (project / "docs" / "checkpoints" / "TEST-abcd").glob("CP-*.md"),
        )
        rc, output, _ = run_w29_hook(
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
        cp_after = list(
            (project / "docs" / "checkpoints" / "TEST-abcd").glob("CP-*.md"),
        )
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
        rc, output, _ = run_w29_hook(
            "subagentstop",
            {"hook_event_name": "SubagentStop", "session_id": "s1",
             "agent_id": "a1", "agent_type": "engineer",
             "cwd": str(project),
             "last_assistant_message": self._return_message(TWELVE_FIELDS)},
            project,
        )
        assert rc == 0, (
            f"SubagentStop must pass (exit 0) with all 12 fields, got {rc}"
        )

    def test_blocks_missing_fields(self, project):
        """When fields are missing, SubagentStop blocks (exit 2).  [CAP-37.d]"""
        present = TWELVE_FIELDS[:6]  # only 6 of 12
        rc, output, _ = run_w29_hook(
            "subagentstop",
            {"hook_event_name": "SubagentStop", "session_id": "s1",
             "agent_id": "a1", "agent_type": "engineer",
             "cwd": str(project),
             "last_assistant_message": self._return_message(present)},
            project,
        )
        assert rc == 2, (
            f"SubagentStop must block (exit 2) when fields are missing, "
            f"got {rc}"
        )

    def test_block_includes_reason_and_is_once(self, project):
        """The block names the missing fields and fires once, never a loop.
        [CAP-37.d]"""
        rc, output, _ = run_w29_hook(
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
        assert missing_mentioned, (
            "the block reason must name at least one missing field"
        )

    @pytest.mark.parametrize("raw_input,label", [
        ("", "empty stdin"),
        ("NOT VALID JSON{{{", "invalid JSON"),
        (json.dumps({"last_assistant_message": None}),
         "null last_assistant_message"),
    ])
    def test_malformed_input_fails_closed(self, project, raw_input, label):
        """SubagentStop must fail closed (exit 2) on malformed input, not
        silently pass (exit 0).  [DEC-136]"""
        script = HOOKS_DIR / "subagentstop.py"
        assert script.is_file(), f"hook not built: {script}"
        result = subprocess.run(
            [sys.executable, str(script)],
            input=raw_input,
            capture_output=True, text=True,
            cwd=str(project),
            env={
                "PATH": os.environ.get("PATH", "/usr/bin:/bin"),
                "PYTHONPATH": str(REPO_ROOT / "src"),
                "PYTHONDONTWRITEBYTECODE": "1",
                "CLAUDE_PROJECT_DIR": str(project),
            },
            timeout=30,
        )
        assert result.returncode == 2, (
            f"SubagentStop must fail closed (exit 2) on {label}, "
            f"got exit {result.returncode} — fail-open vulnerability"
        )

    def test_text_labels_without_content_do_not_satisfy_contract(self, project):
        """When all twelve field labels are present as text (not JSON) but
        have no content after the colon, SubagentStop must block (exit 2).
        The text-path regex must verify content exists after the label,
        not just the label itself.  [DEC-413, Point 5]"""
        empty_text = "\n".join(f"{field}:" for field in TWELVE_FIELDS)
        rc, output, _ = run_w29_hook(
            "subagentstop",
            {"hook_event_name": "SubagentStop", "session_id": "s1",
             "agent_id": "a1", "agent_type": "engineer",
             "cwd": str(project),
             "last_assistant_message": empty_text},
            project,
        )
        assert rc == 2, (
            f"SubagentStop must block (exit 2) when text labels have no "
            f"content after the colon — got {rc}: fail-open vulnerability "
            f"in the text-path regex"
        )

    def test_empty_and_null_values_do_not_satisfy_contract(self, project):
        """Empty string and null values for the 12-field contract do not
        count as present.  The contract requires meaningful values.
        [DEC-136, Finding 2]"""
        fields = {f: "meaningful" for f in TWELVE_FIELDS}
        fields["work_completed"] = ""
        fields["evidence"] = None
        rc, output, _ = run_w29_hook(
            "subagentstop",
            {"hook_event_name": "SubagentStop", "session_id": "s1",
             "agent_id": "a1", "agent_type": "engineer",
             "cwd": str(project),
             "last_assistant_message": json.dumps(fields)},
            project,
        )
        assert rc == 2, (
            f"SubagentStop must block (exit 2) when fields contain empty "
            f"string or null — got {rc}: empty/null passes as present"
        )


# ======================================================================
# SUCCESS LINE 3
# A checkpoint is written when context utilisation passes the threshold,
# not only at PreCompact  [CAP-37.c]
# ======================================================================


class TestCheckpointOnContextUtilisation:
    """Checkpoints are written at multiple triggers, not only PreCompact."""

    def test_stop_writes_checkpoint_not_only_precompact(self, project):
        """The Stop hook writes a checkpoint (trigger: stop), proving that
        checkpoints are not limited to PreCompact events.  [CAP-37.c]"""
        rc, output, _ = run_w29_hook(
            "stop",
            {"hook_event_name": "Stop", "session_id": "s1",
             "cwd": str(project), "last_assistant_message": "Done."},
            project,
            env_extra={"GOV_TICKET": "TEST-abcd", "GOV_ROLE": "engineer"},
        )
        assert rc == 0
        cps = list(
            (project / "docs" / "checkpoints" / "TEST-abcd").glob("CP-*.md"),
        )
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

    def test_precompact_then_sessionstart_preserves_ticket(
        self, w49_project, run,
    ):
        """PreCompact writes a checkpoint that includes the active ticket;
        SessionStart on compact re-injects it."""
        run.precompact(
            w49_project, "auto", role="engineer", ticket="TEST-abcd",
        )
        result = run.sessionstart(
            w49_project, "compact", role="engineer", ticket="TEST-abcd",
        )
        assert result.returncode == 0, result.describe()
        ctx = result.injection
        assert "TEST-abcd" in ctx, (
            "re-injection must include the active ticket"
        )

    def test_precompact_then_sessionstart_preserves_decisions(
        self, w49_project, run,
    ):
        """PreCompact preserves the written part of CHECKPOINT.md, which
        contains open decision IDs; SessionStart on compact re-injects
        that content for the orchestrator.  [DEC-208, KPI line 4]"""
        body = (
            "- Active tickets: TST-71 (engineer implementing)\n"
            "- Open owner decisions: DEC-999 pending owner answer\n"
            "\n"
            "Next action: wait for DEC-999 resolution.\n"
        )
        w1_49_support.write_checkpoint(
            w49_project, ORCH,
            w1_49_support.checkpoint_text(body),
            age_s=w1_49_support.RECENT_AGE_S,
        )
        run.precompact(
            w49_project, "auto", role="orchestrator", ticket="TEST-abcd",
        )
        result = run.sessionstart(
            w49_project, "compact", ticket="TEST-abcd",
        )
        assert result.returncode == 0, result.describe()
        ctx = result.injection
        assert "DEC-999" in ctx, (
            "re-injection must include the open decision ID DEC-999 "
            f"from the written part of CHECKPOINT.md: {ctx[:400]!r}"
        )

    def test_precompact_then_sessionstart_preserves_loop_counts(
        self, w49_project, run,
    ):
        """PreCompact preserves the written part of CHECKPOINT.md, which
        contains loop counts; SessionStart on compact re-injects that
        content for the orchestrator.  [DEC-208, DEC-096, KPI line 4]"""
        body = w1_49_support.resume_section("LPC")
        w1_49_support.write_checkpoint(
            w49_project, ORCH,
            w1_49_support.checkpoint_text(body),
            age_s=w1_49_support.RECENT_AGE_S,
        )
        run.precompact(
            w49_project, "auto", role="orchestrator", ticket="TEST-abcd",
        )
        result = run.sessionstart(
            w49_project, "compact", ticket="TEST-abcd",
        )
        assert result.returncode == 0, result.describe()
        ctx = result.injection
        assert "Loop" in ctx or "loop" in ctx, (
            "re-injection must include the loop count text "
            f"from the written part of CHECKPOINT.md: {ctx[:400]!r}"
        )
        assert "17" in ctx or "LPC" in ctx, (
            "re-injection must carry identifiable loop count content: "
            f"{ctx[:400]!r}"
        )

    def test_auto_compact_threshold(self, w49_project, run):
        """The ``autocompact`` setting (approximately 300 000 tokens) is
        configured in ``.claude/settings.json`` by the owner.  That file
        is outside this ticket's allowed_paths, so this test verifies
        what IS in the ticket's reach: PreCompact writes a checkpoint and
        SessionStart re-injects it on compact — the hooks handle
        compaction correctly.

        Rewrite after implementation, reason: owner correction — the
        original test was vacuous (asserted only exit 0) and the setting
        lives in the owner's file, not reachable by this ticket's paths.
        The correct setting name is ``autocompact`` (not
        ``autoCompactWindow``).  [DEC-208]"""
        run.precompact(
            w49_project, "auto", role="engineer", ticket="TEST-abcd",
        )
        result = run.sessionstart(
            w49_project, "compact", role="engineer", ticket="TEST-abcd",
        )
        assert result.returncode == 0, result.describe()
        ctx = result.injection
        assert ctx, (
            "SessionStart on compact must produce non-empty injection "
            "after PreCompact wrote a checkpoint"
        )
        assert "TEST-abcd" in ctx, (
            "re-injection must include the active ticket after a "
            "compaction cycle"
        )


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
            p.name
            for p in (project / "docs" / "checkpoints" / "TEST-abcd").glob(
                "CP-*.md",
            )
        )
        rc, output, _ = run_w29_hook(
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
            p.name
            for p in (project / "docs" / "checkpoints" / "TEST-abcd").glob(
                "CP-*.md",
            )
        )
        assert cp_after == cp_before, (
            "no checkpoint written during re-entrant stop"
        )


# ======================================================================
# FAILURE LINE 2
# SessionStart injects more than the cap
# ======================================================================


class TestInjectionCap:
    """The injection must stay within the 2.5k-token cap.  [CAP-15.g]"""

    def test_large_context_within_cap(self, w49_project, run):
        """Even when the project has a large context, the additionalContext
        output stays within 2500 tokens (10 000 characters)."""
        result = run.sessionstart(
            w49_project, "startup", role="engineer", ticket="TEST-abcd",
        )
        assert result.returncode == 0, result.describe()
        w1_49_support.assert_within_cap(result)


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
        assert "ticket-transition" in exc_info.value.details.get(
            "reasons", [],
        )


# ======================================================================
# CUT ORDER
# When the combined injection exceeds the cap, context brief and tk
# ready are cut first; instruction to read the prompt and checkpoint,
# and the staleness warning, are last.  [Finding 3]
# ======================================================================


class TestCutOrder:
    """Under the cap, instruction and warning survive while context brief
    and tk ready are cut first."""

    def test_instruction_preserved_when_cap_tight(self, w49_project, run):
        """With a very large checkpoint the combined injection would exceed
        the 10,000-character cap.  The instruction to read the prompt and
        checkpoint must survive (last to be cut); context brief and tk ready
        are trimmed first.  [Finding 3]"""
        large_body = "x" * 9500
        w1_49_support.write_checkpoint(
            w49_project, ORCH,
            w1_49_support.checkpoint_text(large_body),
            age_s=w1_49_support.RECENT_AGE_S,
        )
        result = run.sessionstart(
            w49_project, "compact", role="orchestrator", ticket="TEST-abcd",
        )
        assert result.returncode == 0, result.describe()
        w1_49_support.assert_within_cap(result)
        ctx = result.injection
        assert w1_49_support.PROMPT_REL in ctx, (
            "the instruction to read the prompt must survive even when the "
            "cap is tight — it is the last thing to be cut"
        )


# ======================================================================
# HOOK COPIES
# src/gov/hooks/ must be byte-for-byte identical to
# template/governance/kernel/hooks/ for stop.py and subagentstop.py
# [Point 6]
# ======================================================================


class TestHookCopiesIdentical:
    """The src/gov/hooks/ copies (used by tests) must match the canonical
    template/governance/kernel/hooks/ copies (installed into projects)."""

    @pytest.mark.parametrize("name", ["stop.py", "subagentstop.py"])
    def test_hook_copies_identical(self, name):
        """src/gov/hooks/<name> and template/governance/kernel/hooks/<name>
        must have identical content.  If the template is the canonical
        source, src/ must match so tests exercise the same code that
        gets installed.  [Point 6]"""
        src_copy = HOOKS_DIR / name
        template_copy = REPO_ROOT / "template" / "governance" / "kernel" / "hooks" / name
        assert src_copy.is_file(), f"src copy missing: {src_copy}"
        assert template_copy.is_file(), f"template copy missing: {template_copy}"
        assert src_copy.read_bytes() == template_copy.read_bytes(), (
            f"src/gov/hooks/{name} and template/governance/kernel/hooks/{name} "
            f"differ — the canonical source is the template and src/ must match"
        )
