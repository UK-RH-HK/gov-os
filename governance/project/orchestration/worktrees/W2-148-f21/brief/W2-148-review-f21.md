Step 0, before any work: the sandbox check in /home/usain/gov-os-worktrees/W2-148-f21/.gov-runtime/scratch/brief/EMG-d4b-launched.md, reported first in your return (launch_worker.sh).

# W2-148 — the narrow review of DEC-1107 (F21) (DAEO-xafn)

You are a fresh, read-only independent reviewer. **Narrow scope: one point.** The owner's DEC-1107 (its text in your
worktree at `.gov-runtime/scratch/ref/DEC-1107.md`; the finding it answers, F21, at
`.gov-runtime/scratch/ref/review-r3-F21.md`): **the operator agent's owner-undo path and crash-recovery path exit
non-zero and say `refused` whenever they leave another's file untouched, with the P1 naming each file and the lock
held as before (DEC-1106 (1)); the ACT's own touched files (at their after-copy) are still undone.** Everything else in
W2-148 (`.tickets/DAEO-xafn.md`) was reviewed READY and merged (`511a4a17`); it is not re-opened here. READY is
computed by `verdict.py` from your block.

## What to review
- **The branch:** `w2/W2-148-f21` in `/home/usain/gov-os-worktrees/W2-148-f21`, head `0fe71aa8b`, from `w2/integrate`
  at `b134a760b`: `git diff b134a760b..0fe71aa8b`. The designer's cases (`tests/acceptance/W2-148/test_w2_148_undo_refused.py`,
  the README's changed interface line and N-10; merged at `68af526af`); the engineer's change `0e43fac2e`
  (`governance/project/operator/operator_run.py`: the owner's undo step and the journal recovery) with its unit cases
  `tests/unit/operator/test_w2_148_f21.py`, and the evidence record's "F21 (DEC-1107)" section (`0fe71aa8b`).
- **The runs:** the CTO's outside the sandbox at `0fe71aa8b` with a planted HOME: `gov accept W2-148` **pass, all 39
  lines, 0 failed, 0 skipped (169 cases)**; the trial: 58 ACT files (6 a, 20 b, 32 O; the new one ACT-GATE-CONFIG-2 at
  (b); none lower than the table; 22 rises), the 8 replays and 7 faults as before, `live_unchanged: true`; the CTO's
  own live hashes unchanged. The engineer's unit tests: 184/184.

## Check
1. **Never `undone` or exit 0 when anything is left,** on both paths and every branch into them (the owner's undo with
   a foreign control difference; with a touched file at third bytes; the recovery with either; the "already undone"
   branch; a second undo after the lock is cleared). Read the code paths, not only the tests.
2. **The owner's undo at third bytes** now goes through the same `undo_live` / `foreign_differences` rule as the run
   path: the ACT's own files at their after-copy undone (from the frozen `before/` copies, never by an `apply.sh undo`
   that could write the third-bytes file), the third-bytes file left exactly as written, the undo commit holding only
   the ACT's own files. Can this new branch write a file that is not the ACT's own?
3. **The P1 and the lock:** the P1 says refused and names each file; the lock is held; the next run and launch stop at
   it; nothing on the launcher's stdout carries `undone` in the left case.
4. **Unchanged behaviour:** with nothing left, `undone` and exit 0 (owner's undo) / `undone` (recovery); an undo after
   the next ACT on the same files a plain refusal; the run path's undo untouched.
5. **The "already undone" change** (a later log line with `undo: "done"` counts): can it make a genuine first undo be
   skipped, or let an undo run twice?

## Judgement
`governance/project/briefs/JUDGEMENT.md`, word for word. Every finding carries `Ordinary work: yes|no, because …` and
`Consequence: fails open|loses work|other`, and `scope: in` only if it concerns DEC-1107's point above.

## Write and return
- **You write nothing** in any tree. You may run the tests read-only (`-p no:cacheprovider`) through
  `bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh`, with
  `PYTHONPATH=/home/usain/gov-os-worktrees/W2-148-f21/src` and an empty scratch HOME (`PYTHONUSERBASE=/home/usain/.local`
  so pytest is found). Never run anything against the real `~/gov-os-operator/`, `~/.claude/`, the crontab or a real
  `claude` session. No GPU. Single simple Bash commands (DEC-1080). The hidden-half rule holds: never open anything
  under `~/gov-os-eval/`, `~/gov-os-runs/`, or any `hidden`, `memory-verdict` or `memory-verdict-2` folder.
- **Search again once (DEC-1092 (1))** if a search does not answer.
- **Your record is your session's final message**, in full: the twelve labelled fields of `EMG-common.md` (sandbox and
  `ps` checks first), your answer to checks 1-5, every finding with its two lines and scope, and at the end the fenced
  `verdict` block over the lines DEC-1107 touches:
  `{"kpis": [{"kpi": "S22", "verdict": "pass|fail", "findings": [...]}, {"kpi": "F15", "verdict": "pass|fail", "findings": [...]}]}`
  with each finding `{"id", "scope", "ordinary_work", "consequence"}` (ids from F28).
