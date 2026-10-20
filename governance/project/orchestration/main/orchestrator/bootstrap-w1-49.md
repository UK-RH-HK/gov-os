
## W1-49 residuals (light auto-resume hooks, 2026-10-04)

Recorded at W1-49's close, from the ticket lead's summaries and two reviews. None is a defect of the ticket; W1-29
replaces the checkpoint file and settles most of them.

- **An in-place save during the hook's read–write window can be lost** (DEC-306, accepted by the owner). If the
  session saves its checkpoint in place between the PreCompact hook's read and its write, the new text is cut or
  overwritten. A save by rename, or a save while `tk` runs, is safe. PreCompact runs while the session is idle, and
  the reviewer reached the window only by wrapping the hook's file object. Until W1-29.
- **The warning shows after every compaction** until the session rewrites its checkpoint (DEC-283, confirmed by
  DEC-323). W1-29 may refine it. A write in the same second as the compaction gets no warning, and a file time in the
  future never warns.
- **"Pending owner decisions" is not known to the hook** (DEC-284): the block points to the written part.
- **Not proved:** that a compaction really starts near 300k tokens; the `auto` trigger was never run live. The
  auto-compact setting takes effect only in sessions started after the merge (`840f1e37`).
- **A half-written block** after a kill or a double write failure stays as written text and is injected with the last
  section. Eight compactions at once gave this in about 1 of 40 to 1 of 80 rounds.
- **The modification time is not set back** after a kill, or when the user does not own the file, so the warning is
  missing then.
- **File kinds.** A checkpoint that is a symbolic link is written through to its target. A FIFO hangs both hooks
  until Claude Code's hook timeout. An empty checkpoint gets a block with no written part.
- **Text written after the block** freezes the old block into the written part. Whitespace-only lines after the block
  are dropped.
- **Headings and fences.** Heading variants (lower case, bold, indented, after a byte-order mark) are not found; with
  two RESUME HERE sections the first wins; tilde fences, indented fences and an unclosed fence are not handled; a
  form feed or U+2028 before a heading-like line cuts the section.
- **Sizes.** The 10,000 cap is counted in code points, not UTF-16 units. The block has no size limit. A very long or
  multi-line `GOV_TICKET` breaks the cap's promises and is injected verbatim.
- **Process edges.** A timed-out `tk` leaves its children running; there is no fsync; the message is wrong after a
  failed truncate; the hooks exit 120, not 0, when stdout cannot be written (nothing is blocked).
- **Neither hook reads stdin**, so SessionStart would also inject on `startup` if that source were registered. A
  missing or broken `precompact.py` makes SessionStart inject nothing, silently. A `CLAUDE_PROJECT_DIR` at a
  subdirectory only reports the checkpoint missing.
- **Two stale git-ignored `.pyc` files** remain in `template/governance/kernel/hooks/__pycache__/` in the ticket's
  worktree; they went with the worktree.
- **A guard observation.** The batch 4 engineer wrote its two allowed files with `python3 - <<'EOF'` scripts and the
  guard did not refuse them. Same observation as under W1-15; for W1-46's residual list.
