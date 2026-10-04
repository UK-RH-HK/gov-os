"""W1-49 -- the SessionStart hook's injection.

KPI success 2 [CAP-37.g]: "A SessionStart hook on compact, clear and resume
injects, within the hook's size cap, the prompt path and the checkpoint's RESUME
HERE section, with the instruction to read both now (DEC-248)".
KPI failure 2: "SessionStart injects more than the hook's size cap, or leaves out
the prompt path or the RESUME HERE section".

**The cap** is 10,000 characters for each string Claude Code 2.1.288 puts into
the context (``additionalContext``, plain stdout); over it the text is replaced
by a file path and a 2,000-character preview that nobody tells the model to
open. See the README for the source.

**The RESUME HERE section** is the heading whose text begins with ``RESUME
HERE`` and everything up to the next heading of the same or a higher level.
A line inside a fenced code block (three backticks) is not a heading.

The last tests stand on the recommendation of DP-2 (the hooks act for the
orchestrator role only); the worktree tests assert no prompt path (DP-3).
"""

from __future__ import annotations

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
# On the recommendation of DP-2: a worker session is given no checkpoint
# --------------------------------------------------------------------------

@pytest.mark.parametrize("role", support.WORKER_ROLES)
def test_a_worker_session_is_not_given_the_leads_checkpoint(run, project, worktree, role):
    """DP-2 (a). The loop count is never disclosed to the sessions inside the loop (WBS, loop policy)."""
    support.write_checkpoint(worktree, LEAD, support.checkpoint_text(support.resume_section("LD")))
    result = run.sessionstart(worktree, "resume", role=role)
    assert result.returncode == 0, result.describe()
    assert "LD-71" not in result.stdout and "loop" not in result.stdout.lower(), (
        f"a {role} session was given the lead's RESUME HERE section with its loop counts"
    )
