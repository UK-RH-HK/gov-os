"""W1-49 -- the SessionStart hook's injection.

KPI success 2 [CAP-37.g]: "A SessionStart hook on compact, clear and resume
injects, within the hook's size cap, the prompt path and the checkpoint's RESUME
HERE section, with the instruction to read both now (DEC-248)".
KPI failure 3: "SessionStart injects more than the hook's size cap, or leaves out
the prompt path or the RESUME HERE section".
KPI success 5 [CAP-37.g], second half: "the SessionStart injection warns when
the checkpoint's written part is older than that block, and tells the session to
re-derive state from git and the tickets before acting (DEC-264)".
KPI failure 2: "The checkpoint's written part is older than the generated state
block, and the SessionStart injection does not say so".
KPI success 6 [CAP-37.g]: "The SessionStart injection is role-specific ...
(DEC-263)".

**The cap** is 10,000 characters for each string Claude Code 2.1.288 puts into
the context (``additionalContext``, plain stdout); over it the text is replaced
by a file path and a 2,000-character preview that nobody tells the model to
open. See the README for the source.

**The RESUME HERE section** is the heading whose text begins with ``RESUME
HERE`` and everything up to the next heading of the same or a higher level.
A line inside a fenced code block (three backticks) is not a heading. The
section is taken from the written part: the generated state block is never part
of it, and nothing of the block is injected.

The worker tests follow DEC-259 (the hooks act for the orchestrator role only).
One test stands on a recommendation: decision package DP-4, what "older than the
block" is measured against.
"""

from __future__ import annotations

import os

import pytest

import w1_49_support as support

ORCH = support.ORCHESTRATOR_CHECKPOINT_REL
LEAD = support.LEAD_CHECKPOINT_REL
SOURCES = ("compact", "clear", "resume")
EARLIER = "## Earlier log\n\n- EARLIER-LOG-MARKER merged ZQ-12\n\n"
LATER = "## History\n\n- HISTORY-MARKER closed ZQ-09\n"


def _lines(text):
    return [line.strip() for line in text.splitlines() if line.strip()]


def _assert_whole_section(injection, body):
    missing = [line for line in _lines(body) if line not in injection]
    assert not missing, f"the injection leaves out {len(missing)} line(s) of the RESUME HERE section, first: {missing[0]!r}"


@pytest.mark.parametrize("source", SOURCES)
def test_the_injection_carries_the_prompt_path_and_the_whole_resume_here_section(run, project, source):
    """Success 2, failure 2 [CAP-37.g]: both paths, the section with its sub-heading, "read both now", inside the cap."""
    body = support.resume_section("ZQ")
    support.write_checkpoint(project, ORCH, support.checkpoint_text(body, before=EARLIER, after=LATER))
    result = run.sessionstart(project, source)
    assert result.returncode == 0, f"the hook failed on source {source}: {result.describe()}"
    support.assert_reads_both_now(result.injection, support.PROMPT_REL, ORCH)
    _assert_whole_section(result.injection, body)
    support.assert_within_cap(result)


def test_a_long_checkpoint_does_not_push_the_section_out_of_the_cap(run, project):
    """Success 2: the section is what is injected; 30,000 characters of history around it change nothing."""
    body = support.resume_section("ZQ")
    history = "## History\n\n" + "".join(f"- HISTORY-MARKER entry {n:04d} of the invented log\n" for n in range(700))
    support.write_checkpoint(project, ORCH, support.checkpoint_text(body, before=EARLIER, after=history))
    result = run.sessionstart(project, "compact")
    support.assert_within_cap(result)
    _assert_whole_section(result.injection, body)
    assert support.TRUNCATED not in result.injection.lower(), "a section that fits the cap is reported as cut"


def test_a_resume_here_section_larger_than_the_cap_is_cut_and_said_so(run, project):
    """Failure 2, "within the hook's size cap": the head is kept, the cut is named, the paths and the instruction stay."""
    head = support.resume_section("ZQ")
    body = head + "".join(f"- note {n:04d}: an invented line that fills the section\n" for n in range(500))
    assert len(body) > 2 * support.SIZE_CAP_CHARS
    support.write_checkpoint(project, ORCH, support.checkpoint_text(body, after=LATER))
    result = run.sessionstart(project, "compact")
    assert result.returncode == 0, result.describe()
    support.assert_within_cap(result)
    support.assert_reads_both_now(result.injection, support.PROMPT_REL, ORCH)
    _assert_whole_section(result.injection, head)
    assert support.TRUNCATED in result.injection.lower(), (
        f"the section was cut to fit the cap and the injection does not say `{support.TRUNCATED}`"
    )


def test_a_resume_here_heading_with_more_text_and_no_later_heading(run, project):
    """The heading begins with RESUME HERE; the section runs to the end of the file."""
    body = support.resume_section("ZQ")
    support.write_checkpoint(project, ORCH, support.checkpoint_text(body, heading="# RESUME HERE (read this first)"))
    result = run.sessionstart(project, "resume")
    _assert_whole_section(result.injection, body)
    support.assert_within_cap(result)


def test_a_checkpoint_without_a_resume_here_section_still_gives_both_paths(run, project):
    """There is no section to inject; the session is still sent to the prompt and the checkpoint."""
    support.write_checkpoint(project, ORCH, "# Checkpoint (stand-in)\n\n## Notes\n\n- nothing under the expected heading\n")
    result = run.sessionstart(project, "compact")
    assert result.returncode == 0, result.describe()
    support.assert_reads_both_now(result.injection, support.PROMPT_REL, ORCH)
    support.assert_within_cap(result)


@pytest.mark.parametrize("source", SOURCES)
def test_a_missing_checkpoint_does_not_fail_the_hook(run, project, source):
    """A session without a checkpoint starts as it did before this ticket."""
    result = run.sessionstart(project, source)
    assert result.returncode == 0, f"the hook failed without a checkpoint: {result.describe()}"
    support.assert_within_cap(result)


def test_a_plain_startup_does_not_fail_the_hook(run, project):
    """Startup is not required to inject. If the hook is run for it, it ends with 0 and stays inside the cap."""
    support.write_checkpoint(project, ORCH, support.checkpoint_text(support.resume_section("ZQ")))
    result = run.sessionstart(project, "startup")
    assert result.returncode == 0, result.describe()
    support.assert_within_cap(result)


def test_a_hook_that_cannot_read_its_input_does_not_end_with_a_blocking_code(run, project):
    result = run.sessionstart(project, "resume", stdin="this is not JSON")
    assert result.returncode is not None and result.returncode != 2, result.describe()
    support.assert_within_cap(result)


# --------------------------------------------------------------------------
# A line inside a fenced code block is not a heading (second batch, DEC-136)
# --------------------------------------------------------------------------

FENCE = "```"


def test_a_code_block_inside_the_section_does_not_end_it(run, project):
    """Failure 2: a shell comment in a fenced block is not a heading; the block and the bullets after it are injected."""
    body = (
        "- Active tickets: ZQ-71 (engineer implementing)\n"
        "\n"
        "Run this first:\n"
        "\n"
        f"{FENCE}sh\n"
        "# FENCED-COMMENT-MARKER rebuild the invented index before anything else\n"
        "zephyr index --rebuild ZQ-71\n"
        f"{FENCE}\n"
        "\n"
        "- AFTER-BLOCK-MARKER next ticket: ZQ-88 (waiting for its audit)\n"
        "- ZQ-71 review-repair loop: 17\n"
    )
    support.write_checkpoint(project, ORCH, support.checkpoint_text(body, before=EARLIER, after=LATER))
    result = run.sessionstart(project, "compact")
    assert result.returncode == 0, result.describe()
    _assert_whole_section(result.injection, body)
    assert support.TRUNCATED not in result.injection.lower(), "a section that fits the cap is reported as cut"
    assert "HISTORY-MARKER" not in result.injection, "the injection runs past the real heading that ends the section"
    support.assert_within_cap(result)


def test_a_heading_inside_a_code_block_in_the_section_does_not_end_it(run, project):
    """Failure 2: a fenced line that looks like a heading of the section's own level does not end the section."""
    body = (
        "- Active tickets: ZQ-71 (engineer implementing)\n"
        "\n"
        f"{FENCE}\n"
        "## FENCED-HEADING-MARKER a heading of the invented report, quoted\n"
        f"{FENCE}\n"
        "\n"
        "- AFTER-BLOCK-MARKER ZQ-88 test-fix loop: 23\n"
    )
    support.write_checkpoint(project, ORCH, support.checkpoint_text(body, after=LATER))
    result = run.sessionstart(project, "resume")
    assert result.returncode == 0, result.describe()
    _assert_whole_section(result.injection, body)
    assert "HISTORY-MARKER" not in result.injection, "the injection runs past the real heading that ends the section"
    support.assert_within_cap(result)


def test_a_resume_here_heading_inside_a_code_block_is_not_the_section(run, project):
    """Failure 2: an example of the heading in a fenced block before the real section is not taken for the section."""
    template = (
        "## How this file is written\n"
        "\n"
        "The section the hook injects looks like this:\n"
        "\n"
        f"{FENCE}\n"
        "## RESUME HERE\n"
        "\n"
        "- EXAMPLE-MARKER active tickets: <ticket> (<state>)\n"
        f"{FENCE}\n"
        "\n"
    )
    body = support.resume_section("ZQ")
    support.write_checkpoint(project, ORCH, support.checkpoint_text(body, before=template, after=LATER))
    result = run.sessionstart(project, "compact")
    assert result.returncode == 0, result.describe()
    _assert_whole_section(result.injection, body)
    assert "EXAMPLE-MARKER" not in result.injection, "the example in the code block was injected as the RESUME HERE section"
    assert "HISTORY-MARKER" not in result.injection, "the injection runs past the real heading that ends the section"
    support.assert_within_cap(result)


# --------------------------------------------------------------------------
# In a worktree: the lead's checkpoint, never the orchestrator's
# --------------------------------------------------------------------------

@pytest.mark.parametrize("source", SOURCES)
def test_in_a_worktree_the_leads_section_is_injected(run, project, worktree, source):
    """Success 2 with DEC-237: a fresh lead in the same worktree resumes from the lead's checkpoint."""
    support.write_checkpoint(project, ORCH, support.checkpoint_text(support.resume_section("ZQ")))
    body = support.resume_section("LD")
    support.write_checkpoint(worktree, LEAD, support.checkpoint_text(body, after=LATER))
    result = run.sessionstart(worktree, source)
    assert result.returncode == 0, result.describe()
    assert LEAD in result.injection, f"the injection does not carry the lead checkpoint's path: {result.injection[:300]!r}"
    _assert_whole_section(result.injection, body)
    assert "ZQ-71" not in result.injection, "the lead's injection carries the orchestrator's checkpoint"
    support.assert_within_cap(result)


def test_a_worktree_without_a_lead_checkpoint_gets_nothing_of_the_orchestrators(run, project, worktree):
    """The orchestrator's checkpoint holds every ticket's loop count (loop policy, DEC-096): it stays in the main tree."""
    support.write_checkpoint(project, ORCH, support.checkpoint_text(support.resume_section("ZQ")))
    result = run.sessionstart(worktree, "resume")
    assert result.returncode == 0, result.describe()
    assert "ZQ-71" not in result.stdout, "a worktree session was given the orchestrator's RESUME HERE section"


# --------------------------------------------------------------------------
# DEC-263: the injection is role-specific
# --------------------------------------------------------------------------

LEAD_TICKET = "LD-4242"


def test_in_the_main_tree_the_injection_is_the_orchestrators(run, project, worktree):
    """Success 6 [CAP-37.g]: the orchestrator prompt, the orchestrator's checkpoint and its section; no lead's brief."""
    body = support.resume_section("ZQ")
    support.write_checkpoint(project, ORCH, support.checkpoint_text(body, after=LATER))
    support.write_checkpoint(worktree, LEAD, support.checkpoint_text(support.resume_section("LD")))
    result = run.sessionstart(project, "compact")
    assert result.returncode == 0, result.describe()
    support.assert_reads_both_now(result.injection, support.PROMPT_REL, ORCH)
    _assert_whole_section(result.injection, body)
    lowered = result.injection.lower()
    assert "ticket lead" not in lowered and "appendix a5" not in lowered and LEAD not in result.injection, (
        f"the main tree's injection speaks to a ticket lead: {result.injection[:400]!r}"
    )
    assert "LD-71" not in result.injection, "the main tree's injection carries a lead's checkpoint"
    support.assert_within_cap(result)


def test_in_a_worktree_the_injection_tells_the_session_it_is_the_ticket_lead(run, project, worktree):
    """Success 6 [CAP-37.g]: the lead sentence with the ticket, appendix A5 of the prompt, the lead's checkpoint and section."""
    support.write_checkpoint(project, ORCH, support.checkpoint_text(support.resume_section("ZQ")))
    body = support.resume_section("LD")
    support.write_checkpoint(worktree, LEAD, support.checkpoint_text(body, after=LATER))
    result = run.sessionstart(worktree, "resume", ticket=LEAD_TICKET)
    assert result.returncode == 0, result.describe()
    injection = result.injection
    assert f"ticket lead for {LEAD_TICKET}".lower() in injection.lower(), (
        f"the injection does not say `you are the ticket lead for {LEAD_TICKET}`: {injection[:400]!r}"
    )
    assert "appendix a5" in injection.lower(), f"the injection does not send the lead to appendix A5: {injection[:400]!r}"
    support.assert_reads_both_now(injection, support.PROMPT_REL, LEAD)
    _assert_whole_section(injection, body)
    assert "ZQ-71" not in injection and ORCH not in injection, (
        "the lead's injection carries the orchestrator's checkpoint or its path"
    )
    support.assert_within_cap(result)


def test_in_a_worktree_without_gov_ticket_the_injection_says_the_ticket_is_not_set(run, project, worktree):
    """The hook knows the ticket from GOV_TICKET only. Unset, it says so and still gives the lead everything else."""
    body = support.resume_section("LD")
    support.write_checkpoint(worktree, LEAD, support.checkpoint_text(body))
    result = run.sessionstart(worktree, "resume")
    assert result.returncode == 0, result.describe()
    injection = result.injection
    assert "ticket lead" in injection.lower() and "GOV_TICKET" in injection, (
        f"without GOV_TICKET the injection does not say it is a ticket lead whose GOV_TICKET is not set: {injection[:400]!r}"
    )
    assert "appendix a5" in injection.lower(), f"the injection does not send the lead to appendix A5: {injection[:400]!r}"
    support.assert_reads_both_now(injection, support.PROMPT_REL, LEAD)
    _assert_whole_section(injection, body)
    support.assert_within_cap(result)


# --------------------------------------------------------------------------
# DEC-264: the warning when the written part is older than the generated state block
# --------------------------------------------------------------------------

def _compacted(run, tree, rel, prefix, age_s, trigger="auto", **kwargs):
    """A checkpoint written ``age_s`` seconds ago and one compaction over it; returns ``(path, written text, body)``."""
    body = support.resume_section(prefix)
    text = support.checkpoint_text(body, before=EARLIER, after=LATER)
    path = support.write_checkpoint(tree, rel, text, age_s)
    before = run.precompact(tree, trigger, **kwargs)
    support.assert_not_blocked(before, f"the {trigger} compaction")
    support.read_block(path, text)
    return path, text, body


def test_after_a_compaction_over_an_old_checkpoint_the_injection_warns(run, project):
    """Success 5, failure 2 [CAP-37.g]: the warning, the path, "re-derive state from git and the tickets before acting"."""
    _, _, body = _compacted(run, project, ORCH, "ZQ", support.STALE_AGE_S)
    after = run.sessionstart(project, "compact")
    assert after.returncode == 0, after.describe()
    support.assert_warns_older(after.injection, ORCH)
    support.assert_reads_both_now(after.injection, support.PROMPT_REL, ORCH)
    _assert_whole_section(after.injection, body)
    support.assert_within_cap(after)


def test_a_second_compaction_does_not_make_an_old_written_part_look_fresh(run, project):
    """Failure 2: the first append is not a write of the session's; after the second the warning is still there."""
    _compacted(run, project, ORCH, "ZQ", support.STALE_AGE_S)
    support.assert_not_blocked(run.precompact(project, "manual"), "the second compaction")
    after = run.sessionstart(project, "resume")
    support.assert_warns_older(after.injection, ORCH)


def test_a_written_part_rewritten_after_the_block_is_not_warned_about(run, project):
    """Success 5, "when ... older": the session rewrote its part after the compaction; the block is the older one now."""
    path, text, _ = _compacted(run, project, ORCH, "ZQ", support.STALE_AGE_S)
    block = path.read_text(encoding="utf-8")[len(text):]
    body = support.resume_section("ZR")
    support.write_checkpoint(project, ORCH, support.checkpoint_text(body, after=LATER) + block, age_s=-5.0)
    after = run.sessionstart(project, "resume")
    assert after.returncode == 0, after.describe()
    assert support.OLDER not in after.injection, (
        f"the written part is newer than the state block and the injection warns: {after.injection[:400]!r}"
    )
    _assert_whole_section(after.injection, body)


def test_a_checkpoint_without_a_state_block_is_not_warned_about(run, project):
    """No compaction has run over this checkpoint: there is no block for it to be older than."""
    support.write_checkpoint(project, ORCH, support.checkpoint_text(support.resume_section("ZQ")),
                             age_s=support.STALE_AGE_S)
    after = run.sessionstart(project, "clear")
    assert after.returncode == 0, after.describe()
    assert support.OLDER not in after.injection, f"the injection warns about a block that does not exist: {after.injection[:400]!r}"


def test_a_checkpoint_written_minutes_before_the_compaction_is_warned_about(run, project):
    """DP-4 (a). "Older than the block" is the written part's time against the block's: any age counts, no tolerance."""
    _compacted(run, project, ORCH, "ZQ", support.RECENT_AGE_S)
    after = run.sessionstart(project, "compact")
    support.assert_warns_older(after.injection, ORCH)


def test_in_a_worktree_the_warning_is_about_the_leads_checkpoint(run, project, worktree):
    """Success 5 and 6: the lead is warned about its own checkpoint, and is still told who it is."""
    _, _, body = _compacted(run, worktree, LEAD, "LD", support.STALE_AGE_S, ticket=LEAD_TICKET)
    after = run.sessionstart(worktree, "compact", ticket=LEAD_TICKET)
    support.assert_warns_older(after.injection, LEAD)
    assert f"ticket lead for {LEAD_TICKET}".lower() in after.injection.lower(), (
        f"the warned lead is not told it is the ticket lead for {LEAD_TICKET}: {after.injection[:400]!r}"
    )
    _assert_whole_section(after.injection, body)
    support.assert_within_cap(after)


def _assert_nothing_of_the_block(injection):
    carried = [mark for mark in (support.BLOCK_BEGIN, support.BLOCK_END, *support.TK_LINES) if mark in injection]
    assert not carried, f"the injection carries the generated state block, first: {carried[0]!r}"


def test_the_state_block_is_not_injected_as_the_end_of_the_resume_here_section(run, project):
    """RESUME HERE is the file's last section, so the block follows it with no heading between: the section ends first."""
    body = support.resume_section("ZQ")
    text = support.checkpoint_text(body, before=EARLIER)
    path = support.write_checkpoint(project, ORCH, text, age_s=support.STALE_AGE_S)
    support.assert_not_blocked(run.precompact(project, "auto"), "the compaction")
    support.read_block(path, text)
    after = run.sessionstart(project, "compact")
    _assert_whole_section(after.injection, body)
    _assert_nothing_of_the_block(after.injection)
    support.assert_warns_older(after.injection, ORCH)
    support.assert_within_cap(after)


def test_the_state_block_is_not_injected_instead_of_a_missing_resume_here_section(run, project):
    """The written part has no RESUME HERE section: both paths, the warning, and nothing of the block in its place."""
    text = "# Checkpoint (stand-in)\n\n## Notes\n\n- NOTES-MARKER nothing under the expected heading\n"
    path = support.write_checkpoint(project, ORCH, text, age_s=support.STALE_AGE_S)
    support.assert_not_blocked(run.precompact(project, "auto"), "the compaction")
    support.read_block(path, text)
    after = run.sessionstart(project, "compact")
    assert after.returncode == 0, after.describe()
    support.assert_reads_both_now(after.injection, support.PROMPT_REL, ORCH)
    _assert_nothing_of_the_block(after.injection)
    support.assert_warns_older(after.injection, ORCH)


def test_the_markers_quoted_inside_the_section_do_not_cut_it(run, project):
    """The section quotes both markers in a code block: it is injected whole before and after a compaction."""
    body = (
        "- Active tickets: ZQ-71 (engineer implementing)\n"
        "\n"
        f"{FENCE}\n"
        f"{support.BLOCK_BEGIN}\n"
        "git head: QUOTED-EXAMPLE-MARKER\n"
        f"{support.BLOCK_END}\n"
        f"{FENCE}\n"
        "\n"
        "- AFTER-QUOTE-MARKER ZQ-88 test-fix loop: 23\n"
    )
    text = support.checkpoint_text(body, before=EARLIER)
    path = support.write_checkpoint(project, ORCH, text, age_s=support.STALE_AGE_S)
    before = run.sessionstart(project, "resume")
    _assert_whole_section(before.injection, body)
    assert support.OLDER not in before.injection, "a quoted marker was taken for a generated block"
    support.assert_not_blocked(run.precompact(project, "auto"), "the compaction")
    support.read_block(path, text)
    after = run.sessionstart(project, "compact")
    _assert_whole_section(after.injection, body)
    assert not [line for line in support.TK_LINES if line in after.injection], "the injection carries the generated block"
    support.assert_warns_older(after.injection, ORCH)
    support.assert_within_cap(after)


def test_a_section_over_the_cap_with_the_warning_stays_inside_the_cap(run, project):
    """Failure 3: the warning and both paths are kept, the section is cut from its end and said so."""
    head = support.resume_section("ZQ")
    body = head + "".join(f"- note {n:04d}: an invented line that fills the section\n" for n in range(500))
    text = support.checkpoint_text(body, after=LATER)
    path = support.write_checkpoint(project, ORCH, text, age_s=support.STALE_AGE_S)
    support.assert_not_blocked(run.precompact(project, "auto"), "the compaction")
    support.read_block(path, text)
    after = run.sessionstart(project, "compact")
    assert after.returncode == 0, after.describe()
    support.assert_within_cap(after)
    support.assert_warns_older(after.injection, ORCH)
    support.assert_reads_both_now(after.injection, support.PROMPT_REL, ORCH)
    _assert_whole_section(after.injection, head)
    assert support.TRUNCATED in after.injection.lower(), "the section was cut to fit the cap and the injection does not say so"


# --------------------------------------------------------------------------
# A hook that cannot read the checkpoint does not stop the session start
# --------------------------------------------------------------------------

@pytest.mark.parametrize("what", ("a directory", "an unreadable file"))
def test_a_checkpoint_that_cannot_be_read_does_not_fail_the_hook(run, project, what):
    """Exit 0, inside the cap, and the session is still sent to the prompt and told which checkpoint it could not read."""
    if what == "a directory":
        support.write(project, f"{ORCH}/kept.txt", "an invented file inside the directory\n")
    else:
        if os.geteuid() == 0:
            pytest.skip("root reads unreadable files")
        support.write_checkpoint(project, ORCH, support.checkpoint_text(support.resume_section("ZQ"))).chmod(0o000)
    try:
        result = run.sessionstart(project, "compact")
    finally:
        if what != "a directory":
            (project / ORCH).chmod(0o644)
    assert result.returncode == 0, f"{what} in place of the checkpoint failed the hook: {result.describe()}"
    support.assert_reads_both_now(result.injection, support.PROMPT_REL, ORCH)
    support.assert_within_cap(result)


# --------------------------------------------------------------------------
# DEC-259: a worker session is given no checkpoint
# --------------------------------------------------------------------------

@pytest.mark.parametrize("role", support.WORKER_ROLES)
def test_a_worker_session_is_not_given_the_leads_checkpoint(run, project, worktree, role):
    """DEC-259. The loop count is never disclosed to the sessions inside the loop (WBS, loop policy)."""
    support.write_checkpoint(worktree, LEAD, support.checkpoint_text(support.resume_section("LD")))
    result = run.sessionstart(worktree, "resume", role=role)
    assert result.returncode == 0, result.describe()
    assert "LD-71" not in result.stdout and "loop" not in result.stdout.lower(), (
        f"a {role} session was given the lead's RESUME HERE section with its loop counts"
    )
