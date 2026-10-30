"""W2-62 -- the RESUME HERE section reaches the resumed session whole (W2-M372, DEC-837 item 1).

KPI success 1: "The whole RESUME HERE section reaches the resumed session, however long:
never a cut of its first 9,000 characters, and no "[truncated]" line in its place".
KPI success 2 (the route): the hook's injection stays within the bound of about 10,000
characters that a SessionStart hook's context arrives whole in (measured on Claude Code
2.1.292), and carries the instruction to read the section in full before anything else,
with the checkpoint's path, the section's exact line range and its size.
KPI success 3: "The overall cap never cuts the RESUME HERE section or the instruction to
read it; the optional parts (context packet, ready list, checkpoint brief) are the ones
trimmed."
KPI failure: "A RESUME HERE section of 50,000 characters reaches the resumed session with
no character lost; a checkpoint with no such section still says so; unreadable input still
exits 0 and never blocks the session; a role other than orchestrator still gets no RESUME
HERE injection."

The form of the instruction is this ticket's public interface: ``lines <first>-<last>``
(1-based, inclusive, line numbers of the checkpoint file, from the heading to the section's
last line that is not empty) and ``<n> characters`` (the length of those lines joined by
newlines; thousands separators allowed). Numbers in the README map the tests to its items.
"""

from __future__ import annotations

import os

import pytest

import w2_62_support as support

ORCH = support.ORCH
LEAD = support.LEAD
SOURCES = ("startup", "resume", "compact", "clear")
FENCE = "```"


def _big(token="TOKEN-50K"):
    return support.checkpoint(support.section_text(50_000, token))


# --------------------------------------------------------------------------
# Items 2 and 3: the instruction, always; the whole section when it fits
# --------------------------------------------------------------------------

@pytest.mark.parametrize("source", SOURCES)
def test_a_section_that_fits_is_injected_whole_with_the_instruction(project, sandbox, source):
    """Items 2 and 3 (success 1, 2): the path, `lines a-b`, `n characters`, read in full first; the section whole."""
    cp = support.checkpoint(support.section_text(3_000, "TOKEN-FITS"))
    support.write_checkpoint(project, ORCH, cp)
    run = support.run_sessionstart(project, sandbox, source)
    support.assert_well_formed(run)
    support.assert_instruction(run.injection, cp, ORCH)
    support.assert_whole(run.injection, cp)
    support.assert_no_old_cut(run.injection, cp)


def test_a_section_that_ends_at_the_end_of_the_file(project, sandbox):
    """Item 2 edge: no later heading; the trailing empty lines of the file are not part of the range."""
    cp = support.checkpoint(support.section_text(2_000, "TOKEN-EOF"), after="", trailing="\n\n")
    support.write_checkpoint(project, ORCH, cp)
    run = support.run_sessionstart(project, sandbox, "resume")
    support.assert_well_formed(run)
    support.assert_instruction(run.injection, cp, ORCH)
    support.assert_whole(run.injection, cp)


def test_a_section_with_empty_lines_before_the_next_heading(project, sandbox):
    """Item 2 edge: the range ends at the section's last line that is not empty, not at the next heading."""
    cp = support.checkpoint(support.section_text(2_000, "TOKEN-GAP"), trailing="\n\n\n")
    support.write_checkpoint(project, ORCH, cp)
    run = support.run_sessionstart(project, sandbox, "compact")
    support.assert_well_formed(run)
    support.assert_instruction(run.injection, cp, ORCH)
    support.assert_whole(run.injection, cp)
    assert "HISTORY-MARKER" not in run.injection, "the injection runs past the heading that ends the section"


def test_a_heading_with_more_text_at_the_top_level(project, sandbox):
    """Item 2 edge: a level-1 heading that begins with RESUME HERE runs to the end of the written part."""
    section = support.section_text(2_500, "TOKEN-H1", heading="# RESUME HERE (read this first)")
    cp = support.checkpoint(section, before="Notes before any heading.\n\n", after="")
    support.write_checkpoint(project, ORCH, cp)
    run = support.run_sessionstart(project, sandbox, "resume")
    support.assert_well_formed(run)
    support.assert_instruction(run.injection, cp, ORCH)
    support.assert_whole(run.injection, cp)


def test_a_fenced_hash_line_does_not_end_the_section_or_its_range(project, sandbox):
    """Item 2 edge: `#` lines inside a fenced code block are not headings; the range runs past the block."""
    head = support.section_text(1_500, "TOKEN-BEFORE-FENCE")
    section = (head + "\n\nRun this first:\n\n" + FENCE + "sh\n# FENCED-COMMENT-MARKER rebuild the index\n"
               "## FENCED-HEADING-MARKER quoted heading of the same level\nzephyr index --rebuild ZQ-71\n"
               + FENCE + "\n\n- AFTER-BLOCK-MARKER the section's real last line: TOKEN-FENCE")
    cp = support.checkpoint(section)
    support.write_checkpoint(project, ORCH, cp)
    run = support.run_sessionstart(project, sandbox, "resume")
    support.assert_well_formed(run)
    support.assert_instruction(run.injection, cp, ORCH)
    support.assert_whole(run.injection, cp)


def test_a_section_followed_by_a_generated_state_block(project, sandbox):
    """Item 2 edge, item 5: the section is the written part's last; the block is not in its range or its size."""
    cp = support.checkpoint(support.section_text(2_000, "TOKEN-BLOCK"), after="", trailing="\n")
    path = support.write_checkpoint(project, ORCH, cp, age_s=support.STALE_AGE_S)
    support.compact(project, sandbox)
    assert support.BLOCK_BEGIN in path.read_text(encoding="utf-8"), "precompact.py appended no state block"
    run = support.run_sessionstart(project, sandbox, "compact")
    support.assert_well_formed(run)
    support.assert_instruction(run.injection, cp, ORCH)
    support.assert_whole(run.injection, cp)
    support.assert_warns_older(run.injection, ORCH)
    assert support.BLOCK_BEGIN not in run.injection, "the generated state block was injected as part of the section"


def test_in_a_worktree_the_leads_section_is_named_by_its_lines(project, worktree, sandbox):
    """Items 2 and 3 in a linked worktree: the lead checkpoint, its range and size, its section whole."""
    support.write_checkpoint(project, ORCH, support.checkpoint(support.section_text(2_000, "TOKEN-ORCH")))
    cp = support.checkpoint(support.section_text(2_400, "TOKEN-LEAD"), before="# Lead checkpoint\n\n")
    support.write_checkpoint(worktree, LEAD, cp)
    run = support.run_sessionstart(worktree, sandbox, "resume", ticket="LD-4242")
    support.assert_well_formed(run)
    support.assert_instruction(run.injection, cp, LEAD)
    support.assert_whole(run.injection, cp)
    assert "TOKEN-ORCH" not in run.injection and ORCH not in run.injection, (
        "the lead's injection carries the orchestrator's checkpoint")


# --------------------------------------------------------------------------
# Items 3 and 4 at the edge: fits exactly, one character over
# --------------------------------------------------------------------------

def test_the_fit_edge_whole_at_the_bound_and_never_cut_one_character_over(project, sandbox):
    """Items 1, 3, 4. The edge is measured from the hook's own answer: a 2,500-character section of 60 lines gives
    the length of everything else; a section of 60 lines at the same place that brings the injection to exactly
    10,000 characters fits and is injected whole; one character more does not fit and is never cut."""
    lines = 60

    def at(size, token):
        cp = support.checkpoint(support.section_text(size, token, lines=lines))
        support.write_checkpoint(project, ORCH, cp)
        return cp, support.run_sessionstart(project, sandbox, "resume")

    small, run = at(2_500, "TOKEN-SMALL")
    support.assert_well_formed(run)
    support.assert_instruction(run.injection, small, ORCH)
    support.assert_whole(run.injection, small)
    rest = len(run.injection) - len(small.section)
    edge = support.BOUND - rest
    assert 2_500 < edge < 10_000, f"everything but the section takes {rest:,} characters; no 4-digit edge to test"

    fits, run = at(edge, "TOKEN-EDGE")
    support.assert_well_formed(run)
    support.assert_instruction(run.injection, fits, ORCH)
    support.assert_whole(run.injection, fits)

    over, run = at(edge + 1, "TOKEN-OVER")
    support.assert_well_formed(run)
    support.assert_instruction(run.injection, over, ORCH)
    support.assert_no_old_cut(run.injection, over)


# --------------------------------------------------------------------------
# Item 4 and the failure line: 50,000 characters, never a cut
# --------------------------------------------------------------------------

@pytest.mark.parametrize("source", ("resume", "compact"))
def test_a_section_of_50000_characters_is_named_by_its_lines_never_cut(project, sandbox, source):
    """Failure line, items 1, 2, 4: within the bound, the instruction whole with the exact range and size, no
    9,000-character cut, no `truncated`. Taking exactly the stated lines gives the whole section."""
    cp = _big()
    support.write_checkpoint(project, ORCH, cp)
    run = support.run_sessionstart(project, sandbox, source)
    support.assert_well_formed(run)
    support.assert_instruction(run.injection, cp, ORCH)
    support.assert_no_old_cut(run.injection, cp)
    lines = (project / ORCH).read_text(encoding="utf-8").split("\n")
    assert "\n".join(lines[cp.first - 1:cp.last]) == cp.section  # what a reader of the stated lines gets


def test_a_section_of_50000_characters_in_a_worktree(project, worktree, sandbox):
    """Failure line in a linked worktree: the lead checkpoint's range and size, no cut."""
    cp = _big("TOKEN-LEAD-50K")
    support.write_checkpoint(worktree, LEAD, cp)
    run = support.run_sessionstart(worktree, sandbox, "compact", ticket="LD-4242")
    support.assert_well_formed(run)
    support.assert_instruction(run.injection, cp, LEAD)
    support.assert_no_old_cut(run.injection, cp)


def test_a_section_of_50000_characters_after_a_compaction(project, sandbox):
    """Failure line, items 4 and 5: with the staleness warning, the warning and the instruction are both whole."""
    cp = support.checkpoint(support.section_text(50_000, "TOKEN-STALE-50K"), after="", trailing="\n")
    support.write_checkpoint(project, ORCH, cp, age_s=support.STALE_AGE_S)
    support.compact(project, sandbox)
    run = support.run_sessionstart(project, sandbox, "compact")
    support.assert_well_formed(run)
    support.assert_warns_older(run.injection, ORCH)
    support.assert_instruction(run.injection, cp, ORCH)
    support.assert_no_old_cut(run.injection, cp)


# --------------------------------------------------------------------------
# Items 1 and 5: the bound; the optional parts are the ones trimmed
# --------------------------------------------------------------------------

def test_a_long_ready_list_is_trimmed_not_the_section_or_the_warning(project, sandbox):
    """Items 1, 3, 5 (success 3): section that fits + warning + a 30,000-character ready list + a ticket."""
    cp = support.checkpoint(support.section_text(5_000, "TOKEN-OPTIONAL"), trailing="")
    support.write_checkpoint(project, ORCH, cp, age_s=support.STALE_AGE_S)
    support.compact(project, sandbox)
    sandbox.tk_ready(support.long_ready_list())
    run = support.run_sessionstart(project, sandbox, "compact", ticket="ZQ-71")
    support.assert_well_formed(run)
    support.assert_warns_older(run.injection, ORCH)
    support.assert_instruction(run.injection, cp, ORCH)
    support.assert_whole(run.injection, cp)


def test_a_long_ready_list_with_a_50000_character_section_stays_within_the_bound(project, sandbox):
    """Items 1, 4, 5: everything long at once; the instruction and the warning stay whole, inside the bound."""
    cp = support.checkpoint(support.section_text(50_000, "TOKEN-ALL-LONG"), after="", trailing="\n")
    support.write_checkpoint(project, ORCH, cp, age_s=support.STALE_AGE_S)
    support.compact(project, sandbox)
    sandbox.tk_ready(support.long_ready_list())
    run = support.run_sessionstart(project, sandbox, "resume", ticket="ZQ-71")
    support.assert_well_formed(run)
    support.assert_warns_older(run.injection, ORCH)
    support.assert_instruction(run.injection, cp, ORCH)
    support.assert_no_old_cut(run.injection, cp)


# --------------------------------------------------------------------------
# Item 6 and the failure line: no section still says so
# --------------------------------------------------------------------------

SAYS_SO = support.SAYS_SO


def _says_so(run, rel):
    support.assert_well_formed(run)
    lowered = run.injection.lower()
    assert rel in run.injection and any(phrase in lowered for phrase in SAYS_SO), (
        f"the injection does not name {rel} and say it is missing, can't be read or has no RESUME HERE section: "
        f"{run.injection[:400]!r}")
    assert not support.ranges(run.injection), f"a line range is given for a section that is not there: {run.injection[:400]!r}"


@pytest.mark.parametrize("what", ("no checkpoint", "no RESUME HERE section", "a directory", "an unreadable file",
                                  "a fenced RESUME HERE only"))
def test_no_section_still_says_so(project, sandbox, what):
    """Failure line, item 6: exit 0, the path, and what is wrong; no line range."""
    if what == "no RESUME HERE section":
        support.write_checkpoint(project, ORCH, "# Checkpoint (stand-in)\n\n## Notes\n\n- NOTES-MARKER nothing here\n")
    elif what == "a directory":
        support.write(project, f"{ORCH}/kept.txt", "an invented file inside the directory\n")
    elif what == "an unreadable file":
        if os.geteuid() == 0:
            pytest.skip("root reads unreadable files")
        support.write_checkpoint(project, ORCH, _big()).chmod(0o000)
    elif what == "a fenced RESUME HERE only":
        support.write_checkpoint(project, ORCH, "# Checkpoint\n\n" + FENCE + "\n## RESUME HERE\n\n- EXAMPLE-MARKER\n"
                                 + FENCE + "\n")
    try:
        run = support.run_sessionstart(project, sandbox, "resume")
    finally:
        if what == "an unreadable file":
            (project / ORCH).chmod(0o644)
    _says_so(run, ORCH)


def test_in_a_worktree_without_a_lead_checkpoint_the_lead_path_is_named(project, worktree, sandbox):
    """Failure line, item 6 in a linked worktree; the orchestrator's checkpoint is never used in its place."""
    support.write_checkpoint(project, ORCH, support.checkpoint(support.section_text(2_000, "TOKEN-ORCH")))
    run = support.run_sessionstart(worktree, sandbox, "resume", ticket="LD-4242")
    _says_so(run, LEAD)
    assert "TOKEN-ORCH" not in run.injection


# --------------------------------------------------------------------------
# Item 8 and the failure line: unreadable input, exit 0, never blocks
# --------------------------------------------------------------------------

BAD_STDIN = {"empty": "", "not JSON": "this is not JSON {", "a JSON array": "[1, 2, 3]",
             "a JSON string": '"resume"'}


@pytest.mark.parametrize("role", (support.ORCHESTRATOR, "engineer"))
@pytest.mark.parametrize("kind", tuple(BAD_STDIN))
def test_unreadable_input_exits_0(project, sandbox, kind, role):
    """Failure line, item 8: exit 0, nothing or one SessionStart JSON object, quickly."""
    support.write_checkpoint(project, ORCH, _big())
    run = support.run_sessionstart(project, sandbox, role=role, ticket="ZQ-71", stdin=BAD_STDIN[kind])
    support.assert_well_formed(run, f"the hook given {kind} on stdin")


def test_a_checkpoint_that_cannot_be_decoded_exits_0(project, sandbox):
    """Failure line, item 8: bytes that are not UTF-8 in the checkpoint, around its section."""
    data = b"# Checkpoint\n\n\xff\xfe\xc3(\n\n## RESUME HERE\n\n- DECODE-MARKER \x80\x81 invented\n\n## History\n"
    support.write_checkpoint(project, ORCH, data)
    run = support.run_sessionstart(project, sandbox, "resume")
    support.assert_well_formed(run, "the hook given a checkpoint that is not UTF-8")


# --------------------------------------------------------------------------
# Item 9 and the failure line: other roles get no RESUME HERE injection
# --------------------------------------------------------------------------

@pytest.mark.parametrize("tree", ("main tree", "worktree"))
@pytest.mark.parametrize("role", ("engineer", "independent-test-designer", None))
def test_another_role_gets_no_resume_here_injection(project, worktree, sandbox, role, tree):
    """Failure line, item 9: none of the section, no instruction to read it, no line range."""
    support.write_checkpoint(project, ORCH, support.checkpoint(support.section_text(3_000, "TOKEN-ROLE")))
    support.write_checkpoint(worktree, LEAD, support.checkpoint(support.section_text(3_000, "TOKEN-ROLE")))
    target = project if tree == "main tree" else worktree
    run = support.run_sessionstart(target, sandbox, "resume", role=role, ticket="ZQ-71")
    support.assert_well_formed(run, f"the hook for role {role!r}")
    assert "TOKEN-ROLE" not in run.stdout and "LAST-LINE-MARKER" not in run.stdout and "ZQ-88" not in run.stdout, (
        f"a {role!r} session was given the RESUME HERE section: {run.injection[:300]!r}")
    assert "RESUME HERE" not in run.injection.upper() and not support.ranges(run.injection), (
        f"a {role!r} session was told to read a RESUME HERE section: {run.injection[:300]!r}")
