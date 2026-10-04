"""W1-49 -- the PreCompact hook: it never blocks, and it appends a generated state block.

KPI success 1 [CAP-37.g]: "A PreCompact hook ensures the orchestrator's checkpoint
is current, and in a worktree the lead's (DEC-248)".
KPI success 5 [CAP-37.g]: "The PreCompact hook never blocks a compaction: it
appends a generated state block to the checkpoint (the git head, the tickets in
progress from tk, the worktree list, the pending owner decisions) ... (DEC-264)".
KPI failure 1: "A compaction is blocked by the PreCompact hook".

DEC-264 amends DEC-258: no compaction is blocked, and "current" is no longer a
30-minute age. The tests of this file that asserted a blocked manual compaction,
the age or ``CHECKPOINT NOT CURRENT`` were rewritten after the implementation
(reason "owner decision, DEC-264"); the README lists each one.

**The fixtures.** A *current* checkpoint was written this minute, an *old* one
three days ago, a *missing* one is not there. The hook's ``tk`` is a stand-in
that prints invented tickets in progress (``GEN-...``); its ``git`` is the real
one in the temporary repository, unless a test replaces it by one that fails.

**The written part** is what the session wrote: everything before the block.
**The block** runs from the last line that is ``<!-- GENERATED STATE BLOCK BEGIN
-->`` to the line ``<!-- GENERATED STATE BLOCK END -->`` that ends the file.

One test stands on a recommendation: the last of the block's four items
(decision package DP-5, where the pending owner decisions come from).
"""

from __future__ import annotations

import os

import pytest

import w1_49_support as support

ORCH = support.ORCHESTRATOR_CHECKPOINT_REL
LEAD = support.LEAD_CHECKPOINT_REL
TRIGGERS = ("manual", "auto")
AGES = {"current": 0.0, "old": support.STALE_AGE_S}
FENCE = "```"


def _checkpoint(tree, rel, prefix, age_s=0.0):
    """A stand-in checkpoint; returns ``(path, its text)``."""
    text = support.checkpoint_text(support.resume_section(prefix), after="## History\n\n- closed ZQ-09\n")
    return support.write_checkpoint(tree, rel, text, age_s), text


# --------------------------------------------------------------------------
# No compaction is blocked (DEC-264, failure 1)
# --------------------------------------------------------------------------

@pytest.mark.parametrize("trigger", TRIGGERS)
@pytest.mark.parametrize("state", ("current", "old", "missing"))
def test_no_compaction_is_blocked(run, project, trigger, state):
    """Failure 1: exit code 0 and no blocking decision, whatever the checkpoint's age, and without one."""
    if state != "missing":
        _checkpoint(project, ORCH, "ZQ", age_s=AGES[state])
    result = run.precompact(project, trigger, transcript_age_s=0.0)
    support.assert_not_blocked(result, f"a {trigger} compaction over a {state} checkpoint")


@pytest.mark.parametrize("trigger", TRIGGERS)
def test_a_hook_that_cannot_read_its_input_does_not_block_the_compaction(run, project, trigger):
    """A failure of the hook itself: only exit code 2 blocks, and it must not be used here."""
    _checkpoint(project, ORCH, "ZQ")
    result = run.precompact(project, trigger, stdin="this is not JSON")
    assert result.returncode is not None and result.returncode != 2, (
        f"the hook blocked the compaction on input it could not read: {result.describe()}"
    )


# --------------------------------------------------------------------------
# The generated state block (DEC-264, success 5)
# --------------------------------------------------------------------------

@pytest.mark.parametrize("trigger", TRIGGERS)
def test_the_state_block_is_appended_and_the_written_part_is_unchanged_and_first(run, project, trigger):
    """Success 5: the written part stays byte for byte and comes first; one block follows and ends the file."""
    path, text = _checkpoint(project, ORCH, "ZQ", age_s=support.STALE_AGE_S)
    result = run.precompact(project, trigger)
    support.assert_not_blocked(result, f"a {trigger} compaction")
    support.read_block(path, text)
    assert support.marker_lines(path.read_text(encoding="utf-8")) == 1


def test_the_state_block_holds_the_git_head(run, project):
    """Success 5: the full hash of the tree's HEAD commit."""
    path, text = _checkpoint(project, ORCH, "ZQ")
    run.precompact(project, "auto")
    head = support.git(project, "rev-parse", "HEAD").strip()
    block = support.read_block(path, text)
    assert head in block, f"the state block does not hold the git head {head}: {block[:500]!r}"


def test_the_state_block_holds_the_tickets_in_progress_as_tk_gives_them(run, project):
    """Success 5: every line `tk ls --status=in_progress` printed, and no ticket of the hook's own."""
    path, text = _checkpoint(project, ORCH, "ZQ")
    run.precompact(project, "auto")
    block = support.read_block(path, text)
    missing = [line for line in support.TK_LINES if line not in block]
    assert not missing, f"the state block leaves out what tk gave, first: {missing[0]!r}; the block: {block[:500]!r}"


def test_the_state_block_holds_the_worktree_list(run, project, worktree):
    """Success 5: the main tree and the linked worktree, as `git worktree list` gives them."""
    path, text = _checkpoint(project, ORCH, "ZQ")
    run.precompact(project, "auto")
    block = support.read_block(path, text)
    for tree in (project, worktree):
        assert os.path.realpath(tree) in block, f"the state block's worktree list leaves out {tree}: {block[:600]!r}"
    assert "w1/lead-fixture" in block, f"the worktree list does not show the worktree's branch: {block[:600]!r}"


def test_the_state_block_has_a_line_for_the_pending_owner_decisions(run, project):
    """Success 5: the fourth item is there under its own name, whatever DP-5 ends in."""
    path, text = _checkpoint(project, ORCH, "ZQ")
    run.precompact(project, "auto")
    block = support.read_block(path, text)
    assert support.DECISIONS_LABEL in block.lower(), (
        f"the state block has no line `{support.DECISIONS_LABEL}`: {block[:500]!r}"
    )


def test_the_state_block_does_not_invent_the_pending_owner_decisions(run, project):
    """DP-5 (a). A hook is a command: it does not know them, says so, and copies none from the written part."""
    path, text = _checkpoint(project, ORCH, "ZQ")
    run.precompact(project, "auto")
    block = support.read_block(path, text)
    line = next((line for line in block.splitlines() if support.DECISIONS_LABEL in line.lower()), "")
    assert "not known to the hook" in line.lower(), (
        f"the line `{support.DECISIONS_LABEL}` does not say `not known to the hook`: {line!r}"
    )
    assert "OD-ZQ-913" not in block, "the state block copies an owner decision from the written part as generated state"


def test_a_second_compaction_replaces_the_block(run, project, sandbox):
    """Success 5: one block, the newest. The written part and what separates it from the block stay as they were."""
    path, text = _checkpoint(project, ORCH, "ZQ", age_s=support.STALE_AGE_S)
    run.precompact(project, "auto")
    first = path.read_text(encoding="utf-8")
    support.read_block(path, text)
    later = ("GEN-77 [in_progress] - Invented generated ticket gamma",)
    sandbox.tk_gives(later)
    for trigger in ("manual", "auto"):
        support.assert_not_blocked(run.precompact(project, trigger), f"a later {trigger} compaction")
    block = support.read_block(path, text)
    final = path.read_text(encoding="utf-8")
    assert support.marker_lines(final) == 1 and support.marker_lines(final, support.BLOCK_END) == 1, (
        f"after three compactions the checkpoint holds {support.marker_lines(final)} state blocks, not one"
    )
    assert later[0] in block and support.TK_LINES[0] not in block, (
        f"the block is not the newest one (it should hold GEN-77 and no GEN-41): {block[:500]!r}"
    )
    gap = lambda whole: whole[len(text):whole.index(support.BLOCK_BEGIN)]  # noqa: E731
    assert gap(final) == gap(first), "each compaction adds to what separates the written part from the block"


def test_the_append_leaves_the_checkpoints_modification_time(run, project):
    """The file's time stays the time of its written part: the hook sets it back after the append (README, section 1)."""
    path, text = _checkpoint(project, ORCH, "ZQ", age_s=support.STALE_AGE_S)
    before = path.stat().st_mtime
    for _ in range(2):
        run.precompact(project, "auto")
    support.read_block(path, text)
    assert abs(path.stat().st_mtime - before) < 1.0, (
        f"appending the block moved the checkpoint's modification time by {path.stat().st_mtime - before:.0f} s: "
        "a written part three days old now looks fresh"
    )


def test_the_marker_text_in_the_written_part_is_not_taken_for_the_block(run, project):
    """The markers quoted in a sentence and, as whole lines, in a code block: nothing written is lost, cut or moved."""
    body = (
        support.resume_section("ZQ")
        + f"\nThe hook appends a block that starts with `{support.BLOCK_BEGIN}` (quoted in a sentence).\n\n"
        + f"{FENCE}\n{support.BLOCK_BEGIN}\ngit head: QUOTED-EXAMPLE-MARKER\n{support.BLOCK_END}\n{FENCE}\n\n"
        + "- AFTER-QUOTE-MARKER ZQ-88 test-fix loop: 23\n"
    )
    text = support.checkpoint_text(body, after="## History\n\n- closed ZQ-09\n")
    path = support.write_checkpoint(project, ORCH, text, age_s=support.STALE_AGE_S)
    for trigger in ("auto", "manual"):
        support.assert_not_blocked(run.precompact(project, trigger), f"a {trigger} compaction")
        block = support.read_block(path, text)
        assert "QUOTED-EXAMPLE-MARKER" not in block and support.TK_LINES[0] in block, (
            f"the quoted example was taken for the generated block: {block[:400]!r}"
        )
    assert support.marker_lines(path.read_text(encoding="utf-8")) == 2, (
        "the checkpoint should hold the quoted begin marker and one generated block"
    )


# --------------------------------------------------------------------------
# In a worktree: the lead's checkpoint (success 1)
# --------------------------------------------------------------------------

def test_in_a_worktree_the_block_is_appended_to_the_leads_checkpoint(run, project, worktree):
    """Success 1, "in a worktree the lead's": the block holds the worktree's head; the orchestrator's file is untouched."""
    orchestrator, orchestrator_text = _checkpoint(project, ORCH, "ZQ", age_s=support.STALE_AGE_S)
    support.write(worktree, "lead-note.txt", "an invented commit of the lead's branch\n")
    support.git(worktree, "add", "lead-note.txt")
    support.git(worktree, "commit", "-q", "-m", "lead fixture commit")
    lead, lead_text = _checkpoint(worktree, LEAD, "LD", age_s=support.STALE_AGE_S)
    result = run.precompact(worktree, "manual", ticket="LD-4242")
    support.assert_not_blocked(result, "a manual compaction in a worktree")
    block = support.read_block(lead, lead_text)
    head = support.git(worktree, "rev-parse", "HEAD").strip()
    assert head in block, f"the lead's state block does not hold the worktree's git head {head}: {block[:500]!r}"
    assert orchestrator.read_text(encoding="utf-8") == orchestrator_text, (
        "a compaction in a worktree changed the orchestrator's checkpoint in the main tree"
    )
    assert not (worktree / ORCH).exists(), "a compaction in a worktree created an orchestrator checkpoint there"


def test_a_worktree_without_a_lead_checkpoint_is_said_so_and_nothing_is_written(run, project, worktree):
    """The hook names the lead's checkpoint it could not append to; it writes neither that file nor the orchestrator's."""
    orchestrator, orchestrator_text = _checkpoint(project, ORCH, "ZQ")
    result = run.precompact(worktree, "auto", ticket="LD-4242")
    support.assert_not_blocked(result, "a compaction in a worktree without a lead checkpoint")
    assert LEAD in result.said, f"the hook did not say it could not append to {LEAD}: {result.describe()}"
    assert not (worktree / LEAD).exists(), "the hook created a lead checkpoint that holds no written part"
    assert orchestrator.read_text(encoding="utf-8") == orchestrator_text, (
        "a compaction in a worktree changed the orchestrator's checkpoint in the main tree"
    )


# --------------------------------------------------------------------------
# A hook that cannot do its work stops nothing and loses nothing
# --------------------------------------------------------------------------

@pytest.mark.parametrize("trigger", TRIGGERS)
def test_a_missing_checkpoint_is_said_so_and_none_is_created(run, project, trigger):
    """A file with a block and no written part would pass for a checkpoint: the hook says what it could not do."""
    result = run.precompact(project, trigger)
    support.assert_not_blocked(result, f"a {trigger} compaction without a checkpoint")
    assert ORCH in result.said, f"the hook did not say it could not append to {ORCH}: {result.describe()}"
    assert not (project / ORCH).exists(), "the hook created a checkpoint that holds no written part"


def test_a_read_only_checkpoint_is_left_as_it_is_and_said_so(run, project):
    """The file and its directory can't be written: exit 0, the file byte for byte as it was, the path named."""
    path, text = _checkpoint(project, ORCH, "ZQ", age_s=support.STALE_AGE_S)
    if os.geteuid() == 0:
        pytest.skip("root writes read-only files")
    path.chmod(0o444)
    path.parent.chmod(0o555)
    try:
        result = run.precompact(project, "manual")
    finally:
        path.parent.chmod(0o755)
        path.chmod(0o644)
    support.assert_not_blocked(result, "a compaction over a read-only checkpoint")
    assert path.read_text(encoding="utf-8") == text, "a read-only checkpoint was changed"
    assert ORCH in result.said, f"the hook did not say it could not append to {ORCH}: {result.describe()}"


def test_a_directory_in_place_of_the_checkpoint_is_left_alone_and_said_so(run, project):
    inside = support.write(project, f"{ORCH}/kept.txt", "an invented file inside the directory\n")
    result = run.precompact(project, "auto")
    support.assert_not_blocked(result, "a compaction with a directory in place of the checkpoint")
    assert (project / ORCH).is_dir() and inside.read_text(encoding="utf-8") == "an invented file inside the directory\n", (
        "the directory in place of the checkpoint was replaced or emptied"
    )
    assert ORCH in result.said, f"the hook did not say it could not append to {ORCH}: {result.describe()}"


@pytest.mark.parametrize("how", ("not on PATH", "fails"))
def test_without_tk_the_block_says_so_and_holds_the_rest(run, project, sandbox, how):
    """The block is still appended: the git head is there, and the tickets line says `unavailable`."""
    path, text = _checkpoint(project, ORCH, "ZQ")
    if how == "fails":
        sandbox.tk_fails()
    result = run.precompact(project, "auto", path=sandbox.path_without_tk if how == "not on PATH" else None)
    support.assert_not_blocked(result, f"a compaction while tk is {how}")
    block = support.read_block(path, text)
    assert support.git(project, "rev-parse", "HEAD").strip() in block, f"the block lost the git head: {block[:500]!r}"
    tickets = [line for line in block.splitlines() if "tickets in progress" in line.lower()]
    assert tickets and support.UNAVAILABLE in tickets[0].lower(), (
        f"tk is {how} and the block's `tickets in progress` line does not say `{support.UNAVAILABLE}`: {block[:500]!r}"
    )


def test_without_git_the_block_says_so_and_holds_the_rest(run, project, sandbox):
    """The hook chooses the checkpoint without git (README, section 1); the block holds what tk gave."""
    path, text = _checkpoint(project, ORCH, "ZQ")
    sandbox.git_fails()
    result = run.precompact(project, "auto")
    support.assert_not_blocked(result, "a compaction while git fails")
    block = support.read_block(path, text)
    assert support.TK_LINES[0] in block, f"the block lost the tickets in progress: {block[:500]!r}"
    for label in ("git head", "worktrees"):
        lines = [line for line in block.splitlines() if line.lower().startswith(label)]
        assert lines and support.UNAVAILABLE in lines[0].lower(), (
            f"git fails and the block's `{label}` line does not say `{support.UNAVAILABLE}`: {block[:500]!r}"
        )


# --------------------------------------------------------------------------
# DEC-259: a worker session is left alone
# --------------------------------------------------------------------------

@pytest.mark.parametrize("role", support.WORKER_ROLES)
def test_a_workers_compaction_is_not_blocked_and_appends_nothing(run, project, worktree, role):
    """DEC-259. A worker shares the lead's worktree; the lead's checkpoint is not the worker's to write."""
    lead, lead_text = _checkpoint(worktree, LEAD, "LD", age_s=support.STALE_AGE_S)
    orchestrator, orchestrator_text = _checkpoint(project, ORCH, "ZQ", age_s=support.STALE_AGE_S)
    result = run.precompact(worktree, "manual", role=role, ticket="LD-4242", transcript_age_s=0.0)
    support.assert_not_blocked(result, f"a {role} session's compaction")
    assert lead.read_text(encoding="utf-8") == lead_text, f"a {role} session's compaction wrote to the lead's checkpoint"
    assert orchestrator.read_text(encoding="utf-8") == orchestrator_text, (
        f"a {role} session's compaction wrote to the orchestrator's checkpoint"
    )
