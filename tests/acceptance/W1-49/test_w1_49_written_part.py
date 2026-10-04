"""W1-49 -- the written part is the session's work: the hooks never lose, cut or reorder it (batch 4).

KPI success 5 [CAP-37.g]: "The PreCompact hook never blocks a compaction: it
appends a generated state block to the checkpoint ... (DEC-264)". The block is
appended; the written part is never the price of it.

Written after the implementation, from a review's findings (DEC-136). Four
behaviours, as the README's section 1 fixes them:

1. The hook replaces only a block it generated: both marker lines exactly, the
   ``generated:`` line straight after the begin marker, and every line between
   the markers as the hook wrote it. Anything else is written text: it stays,
   byte for byte, and the new block is appended after it.
2. What ``tk`` or git prints is indented in the block, so a marker line in a
   command's output is never a marker line of the checkpoint.
3. A checkpoint saved while the hook gathers its state is not put back to what
   the hook read before.
4. The hook writes and removes no file but the checkpoint.

**The fixtures** are those of the other files: stand-in checkpoints in a
temporary git repository, a stand-in ``tk`` first on the hook's ``PATH``.
"""

from __future__ import annotations

import os

import pytest

import w1_49_support as support

ORCH = support.ORCHESTRATOR_CHECKPOINT_REL
BEGIN, END = support.BLOCK_BEGIN, support.BLOCK_END
EARLIER = "## Earlier log\n\n- EARLIER-LOG-MARKER merged ZQ-12\n\n"
HISTORY = "## History\n\n- HISTORY-MARKER closed ZQ-09\n"
QUOTED = "generated: 2026-10-01T08:00:00Z\ngit head: QUOTED-EXAMPLE-MARKER\n"
NOTE = "- BETWEEN-MARKERS-NOTE ZQ-88 test-fix loop: 23, the audit starts after the merge\n"


def _lines(text):
    return [line.strip() for line in text.splitlines() if line.strip()]


def _assert_whole_section(injection, body):
    missing = [line for line in _lines(body) if line not in injection]
    assert not missing, f"the injection leaves out {len(missing)} line(s) of the RESUME HERE section, first: {missing[0]!r}"


def _assert_nothing_generated(injection):
    carried = [mark for mark in support.TK_LINES if mark in injection]
    carried += [line for line in injection.splitlines() if line.startswith(("git head:", "generated:"))]
    assert not carried, f"the injection carries generated state as part of the RESUME HERE section, first: {carried[0]!r}"


def _compact(run, tree, times=1):
    for number in range(times):
        support.assert_not_blocked(run.precompact(tree, ("auto", "manual")[number % 2]), f"compaction {number + 1}")


# --------------------------------------------------------------------------
# 1. Text the session wrote between marker lines is not deleted
# --------------------------------------------------------------------------

def test_session_text_between_a_begin_marker_near_the_top_and_an_end_marker_at_the_end_is_kept(run, project):
    """The file ends with the end marker and the begin marker is far above it: no `generated:` line follows it, so
    this is no block of the hook's. The RESUME HERE section between them stays; the block is appended after it."""
    text = (
        "# Checkpoint (stand-in, invented)\n\n"
        f"{BEGIN}\n\n"
        f"## RESUME HERE\n\n{support.resume_section('ZQ')}\n{HISTORY}\n"
        f"{END}\n"
    )
    path = support.write_checkpoint(project, ORCH, text, age_s=support.STALE_AGE_S)
    _compact(run, project, 2)
    block = support.one_block_after(path, text)
    assert support.TK_LINES[0] in block, f"the appended block is not the generated one: {block[:400]!r}"


@pytest.mark.parametrize("shape", ("indented", "trailing spaces", "trailing tab"))
def test_marker_lines_that_are_not_exact_do_not_make_a_block_of_the_text_between_them(run, project, shape):
    """A marker line is the marker and nothing else on the line. Indented, or with a space or a tab after it, it is
    text the session wrote, and so is what stands between two such lines at the end of the file."""
    before, after = {"indented": ("    ", ""), "trailing spaces": ("", "  "), "trailing tab": ("", "\t")}[shape]
    quoted = "".join(f"{before}{line}\n" for line in (QUOTED + NOTE).splitlines())
    text = support.checkpoint_text(support.resume_section("ZQ"), before=EARLIER, after=HISTORY) + (
        f"\n{before}{BEGIN}{after}\n{quoted}{before}{END}{after}\n"
    )
    path = support.write_checkpoint(project, ORCH, text, age_s=support.STALE_AGE_S)
    _compact(run, project, 2)
    block = support.one_block_after(path, text)
    assert "QUOTED-EXAMPLE-MARKER" not in block and support.TK_LINES[0] in block, (
        f"the appended block is not the generated one: {block[:400]!r}"
    )


@pytest.mark.parametrize("line", (
    "- INSIDE-BLOCK-NOTE the audit of ZQ-88 starts after the merge",
    "  INSIDE-BLOCK-NOTE ZQ-93 [in_progress] - added by hand under the tickets",
), ids=("at the start of the line", "indented as the tickets are"))
def test_a_line_the_session_wrote_inside_the_block_is_not_deleted(run, project, line):
    """A block with a line the hook did not write is no longer the hook's: it is written text and stays whole, the
    session's line with it. The new block is appended after it, and that one is replaced as any generated block."""
    start = support.checkpoint_text(support.resume_section("ZQ"), after=HISTORY)
    path = support.write_checkpoint(project, ORCH, start, age_s=support.STALE_AGE_S)
    _compact(run, project)
    generated = support.one_block_after(path, start)
    whole = path.read_text(encoding="utf-8")
    last_ticket = next(row for row in generated.split("\n") if support.TK_LINES[-1] in row)
    text = whole.replace(f"{last_ticket}\n", f"{last_ticket}\n{line}\n", 1)
    assert text != whole and line in text
    support.write_checkpoint(project, ORCH, text, age_s=support.RECENT_AGE_S)
    _compact(run, project)
    support.one_block_after(path, text)
    _compact(run, project)
    block = support.one_block_after(path, text)
    assert "INSIDE-BLOCK-NOTE" not in block, f"the hook copied the session's line into its own block: {block[:400]!r}"


def test_session_text_between_marker_lines_at_the_end_of_the_section_is_injected(run, project):
    """At a session start, with no compaction: RESUME HERE is the last section and ends with text between two marker
    lines. No block was generated, so the section is injected whole and nothing is warned about. After a compaction
    the text is still in the file and in the injection, and the generated block is not."""
    body = support.resume_section("ZQ") + f"\n{BEGIN}\n{NOTE}- BETWEEN-MARKERS-NEXT read the review of ZQ-71\n{END}\n"
    text = support.checkpoint_text(body, before=EARLIER)
    assert text.endswith(f"{END}\n")
    path = support.write_checkpoint(project, ORCH, text, age_s=support.STALE_AGE_S)
    before = run.sessionstart(project, "resume")
    assert before.returncode == 0, before.describe()
    _assert_whole_section(before.injection, body)
    assert support.OLDER not in before.injection, (
        f"text the session wrote between marker lines was taken for a generated block: {before.injection[:400]!r}"
    )
    _compact(run, project)
    support.one_block_after(path, text)
    after = run.sessionstart(project, "compact")
    _assert_whole_section(after.injection, body)
    _assert_nothing_generated(after.injection)
    support.assert_warns_older(after.injection, ORCH)
    support.assert_within_cap(after)


# --------------------------------------------------------------------------
# 2. A marker line in what tk prints does not break the block
# --------------------------------------------------------------------------

@pytest.mark.parametrize("marker", (BEGIN, END), ids=("begin", "end"))
def test_a_marker_line_in_what_tk_prints_does_not_break_the_block(run, project, sandbox, marker):
    """`tk` prints a line that is exactly a marker (a ticket's title could be one). After two and three compactions
    there is one block, the written part is what it was, the file has not grown, the section is injected without
    anything generated, and the old written part is still warned about."""
    body = support.resume_section("ZQ")
    text = support.checkpoint_text(body, before=EARLIER)
    path = support.write_checkpoint(project, ORCH, text, age_s=support.STALE_AGE_S)
    sandbox.tk_gives((support.TK_LINES[0], marker, support.TK_LINES[1]))
    _compact(run, project)
    first = support.one_block_after(path, text)
    assert marker in first[len(BEGIN):-len(END)] and support.TK_LINES[1] in first, (
        f"the block does not hold every line tk printed: {first[:500]!r}"
    )
    size = len(path.read_text(encoding="utf-8").split("\n"))
    for number in (2, 3):
        _compact(run, project)
        support.one_block_after(path, text)
        now = len(path.read_text(encoding="utf-8").split("\n"))
        assert now == size, (
            f"after compaction {number} the checkpoint holds {now} lines, not the {size} it held after the first: "
            "an earlier block was left in the file"
        )
    after = run.sessionstart(project, "compact")
    assert after.returncode == 0, after.describe()
    _assert_whole_section(after.injection, body)
    _assert_nothing_generated(after.injection)
    support.assert_warns_older(after.injection, ORCH)
    support.assert_within_cap(after)


# --------------------------------------------------------------------------
# 3. A checkpoint saved while the hook gathers its state is not put back
# --------------------------------------------------------------------------

def test_a_checkpoint_saved_while_the_hook_gathers_its_state_keeps_the_new_text(run, project, sandbox):
    """While `tk` runs, the session saves its checkpoint with new text. When the hook ends the new text is in the
    file, whole and first. Either one block follows it, or the hook appended nothing and says so with the path."""
    old = support.checkpoint_text(support.resume_section("ZQ"), after=HISTORY)
    new = support.checkpoint_text(support.resume_section("ZR"), before=EARLIER, after=HISTORY)
    path = support.write_checkpoint(project, ORCH, old, age_s=support.STALE_AGE_S)
    pending = sandbox.tk_saves_the_checkpoint(path, new)
    result = run.precompact(project, "auto")
    support.assert_not_blocked(result, "a compaction during which the checkpoint was saved")
    assert not pending.exists(), "the hook did not run tk: the checkpoint was not saved during the compaction"
    data = path.read_text(encoding="utf-8")
    assert data.startswith(new), (
        "the checkpoint was saved while the hook gathered its state, and the hook put back what it had read before: "
        f"the new text is gone, the file begins {data[:160]!r}"
    )
    if data[len(new):].strip():
        support.one_block_after(path, new)
    else:
        assert ORCH in result.said, (
            f"the hook appended nothing to the checkpoint saved under it and did not say so with {ORCH}: "
            f"{result.describe()}"
        )


# --------------------------------------------------------------------------
# 4. The hook writes and removes no file but the checkpoint
# --------------------------------------------------------------------------

NEIGHBOURS = tuple(name for stem in ("CHECKPOINT.md", ".CHECKPOINT.md", "CHECKPOINT")
                   for name in (f"{stem}.precompact", f"{stem}.tmp", f"{stem}.new", f"{stem}.bak", f"{stem}.swp", f"{stem}.lock",
                                f"{stem}.part", f"{stem}.orig", f"{stem}~"))


def _assert_only_the_checkpoint_changed(path, text, before):
    after = support.directory_state(path.parent)
    name = path.name
    removed = sorted(set(before) - set(after))
    assert not removed, f"the hook removed {len(removed)} file(s) beside the checkpoint, first: {removed[0]}"
    changed = sorted(entry for entry in before if entry != name and after[entry] != before[entry])
    assert not changed, (
        f"the hook changed {len(changed)} file(s) beside the checkpoint, first: {changed[0]} "
        f"(was a {before[changed[0]][0]}, is a {after[changed[0]][0]})"
    )
    added = sorted(set(after) - set(before))
    assert not added, f"the hook left {len(added)} file(s) of its own beside the checkpoint, first: {added[0]}"
    assert after[name][0] == "file", f"the checkpoint is no longer a regular file: it is a {after[name][0]}"
    support.one_block_after(path, text)


def test_a_file_beside_the_checkpoint_is_neither_changed_nor_removed(run, project):
    """Files of the session's own beside the checkpoint, under the names a hook might take for its work: each is
    there after two compactions with its content, and the hook leaves no file of its own."""
    text = support.checkpoint_text(support.resume_section("ZQ"), after=HISTORY)
    path = support.write_checkpoint(project, ORCH, text, age_s=support.STALE_AGE_S)
    for name in NEIGHBOURS:
        (path.parent / name).write_text(f"NEIGHBOUR-MARKER an invented draft the session keeps as {name}\n", encoding="utf-8")
    before = support.directory_state(path.parent)
    _compact(run, project, 2)
    _assert_only_the_checkpoint_changed(path, text, before)


def test_a_link_beside_the_checkpoint_is_not_written_through_and_does_not_become_the_checkpoint(run, project, tmp_path):
    """Symbolic links beside the checkpoint, each to a file elsewhere: after two compactions every target holds what
    it held, every link is the link it was, and the checkpoint is a regular file with the written part first."""
    text = support.checkpoint_text(support.resume_section("ZQ"), after=HISTORY)
    path = support.write_checkpoint(project, ORCH, text, age_s=support.STALE_AGE_S)
    elsewhere = tmp_path / "elsewhere"
    elsewhere.mkdir()
    for number, name in enumerate(NEIGHBOURS):
        target = elsewhere / f"target-{number:02d}.txt"
        target.write_text(f"TARGET-MARKER an invented file elsewhere, linked as {name}\n", encoding="utf-8")
        os.symlink(target, path.parent / name)
    before, targets = support.directory_state(path.parent), support.directory_state(elsewhere)
    _compact(run, project, 2)
    now = support.directory_state(elsewhere)
    written = sorted(name for name in targets if now.get(name) != targets[name])
    assert not written and set(now) == set(targets), (
        f"the hook wrote through a link beside the checkpoint: {written[0] if written else sorted(set(now) ^ set(targets))[0]} "
        "elsewhere no longer holds what it held"
    )
    assert not path.is_symlink(), "the checkpoint is now a symbolic link to a file elsewhere"
    _assert_only_the_checkpoint_changed(path, text, before)
