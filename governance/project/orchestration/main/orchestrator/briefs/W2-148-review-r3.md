# W2-148 — the narrow review of DEC-1106's points (DAEO-xafn), the exception round

You are a fresh, read-only independent reviewer. **Narrow scope:** review only the owner's DEC-1106 (1) and (3) in
W2-148's operator agent (`.tickets/DAEO-xafn.md`: read it, with its DEC-1106 note and fifteenth failure line; DEC-1106's
text is in your worktree at `.gov-runtime/scratch/ref/DEC-1106.md`; the finding it answers, F15, at
`.gov-runtime/scratch/ref/review-r2-F15.md`). Every other point was judged in rounds 1 and 2 and is not re-opened here.
The owner allowed this one exception round to DEC-1010: READY is computed by `verdict.py` from your block.

## The rule under review (DEC-1106 (1), with the CTO's confirmed reading)
- A live file whose bytes equal the frozen `after/` copy is the agent's own change, and is restored (after the G8 dry
  run: to its pre-dry-run bytes; in an undo: the ACT's own touched files undone).
- **Any other changed file** (a control file, a file created or removed, a touched file at bytes that are neither its
  before- nor its after-copy, including one where the agent's change and someone else's are mixed) **is left exactly
  as written: the agent writes nothing to it.**
- **Whenever any such other change is seen, the agent also refuses, holds the lock and sends the owner a P1 naming each
  file, even after restoring its own files. It never reports success in that case.**
- The same rule in the (a) after-check's undo.
- **DEC-1106 (3):** the commit freeze is `<operator root>/install/act-in-progress.txt`, the `freeze` setting's default;
  never in either `log/`; not counted by the APPROVED check nor the install's control hash; a stale one holds G9 and
  is never removed by a run that did not write it. (The CTO's tools, the landing hook and the guard's deny for it come
  with ACT-OPERATOR-1: not in scope.)

## What to review
- **The branch:** `w2/W2-148` in `/home/usain/gov-os-worktrees/W2-148`, head `1af33c535`. The round's change:
  `git diff 85a5cf655..1af33c535` (the designer's DEC-1106 cases merged at `5053a0407`; the engineer's `1ac0c1716`,
  `1af33c535`). Code: `Run.g8`, `Run.live_changed`, `undo_live`, `foreign_differences`, the `fail` path (`St.fail`),
  `after_checks`, the owner's undo step, the journal recovery, the hook points `in-G8` and `in-apply-checks`,
  `claim_freeze`/`release_freeze` and their callers, the APPROVED check's exception; the unit tests
  `tests/unit/operator/test_w2_148_round3.py`; the designer's cases `tests/acceptance/W2-148/test_w2_148_restore_freeze.py`
  and the revised S14/S15 cases in `test_w2_148_apply.py`; the evidence record's "Round 3 (DEC-1106)" section.
- **The runs:** the CTO's outside the sandbox at `1af33c535` with a planted HOME: `gov accept W2-148` **pass, all 39
  lines, 0 failed, 0 skipped** (166 cases); the trial: 57 ACT files (6 a, 19 b, 32 O), the 8 replays and 7 faults as
  before, `live_unchanged: true`; the CTO's own live hashes (operator folder, `~/.claude` settings, crontab, hooks,
  pin) unchanged. The engineer's unit tests: 175/175.

## Check
1. **No foreign write, at any write-back site.** Is there any path left in the code (G8, the after-check, the
   `unlisted` path, a red check, a failed commit, an error mid-apply, the owner's undo, the journal recovery, `apply.sh
   undo` itself) that can write, restore, delete or `git checkout` a live file that is not shown to be the agent's own
   by the after-copy test? The engineer skips `apply.sh undo` when any touched file is at third bytes: is that
   complete (what if a touched file is at its after-copy but a file `apply.sh undo` also writes is foreign)?
2. **Never success when a foreign change is seen.** The run path returns a non-zero exit with a P1 and the lock held.
   **The CTO noticed the owner's undo step and the journal recovery return `result: "undone"` with exit 0 even when
   files were left (`operator_run.py` around lines 1515-1528 and 1590-1592), with a P1 and the lock held.** Judge
   whether that is "reports success" under the rule above, and whether it fails open (the next ACT runs? the digest
   or the CTO reads it as done?).
3. **The P1 names every file**, with no truncation that drops a name; the lock really stops the next run and launch.
4. **A concurrent commit stays in history and the tree** (the undo commit holds only the ACT's own files; nothing
   resets, checks out or amends).
5. **The hook points** run where the README says, wait, and hold no git lock; they cannot be reached from the walled
   session's clean environment.
6. **The freeze:** claimed only after G9 passes and only if free; released only by its writer (token); out of
   APPROVED and the control hash; a stale freeze holds G9; the owner's undo while a freeze is held writes nothing.
   Can a crash leave the freeze so that nothing ever runs again without the owner (acceptable, if it is named), or so
   that a run proceeds without one?
7. **The wider reach the engineer reports** (the rule now also governs the `unlisted` path: a live unlisted file the
   apply wrote is left as written with a P1 and the lock): consistent with DEC-1106, or a gap?

## Judgement
`governance/project/briefs/JUDGEMENT.md`, word for word. Every finding carries `Ordinary work: yes|no, because …` and
`Consequence: fails open|loses work|other`, and `scope: in` only if it concerns DEC-1106's points above.

## Write and return
- **You write nothing** in any tree. You may run the tests read-only (`-p no:cacheprovider`) through
  `bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh`, with
  `PYTHONPATH=/home/usain/gov-os-worktrees/W2-148/src` and an empty scratch HOME. Never run anything against the real
  `~/gov-os-operator/`, `~/.claude/`, the crontab or a real `claude` session. No GPU. Single simple Bash commands
  (DEC-1080). The hidden-half rule holds: never open anything under `~/gov-os-eval/`, `~/gov-os-runs/`, or any
  `hidden`, `memory-verdict` or `memory-verdict-2` folder.
- **Search again once (DEC-1092 (1))** if a search does not answer.
- **Your record is your session's final message**, in full: the twelve labelled fields of `EMG-common.md` (sandbox and
  `ps` checks first), your answer to each check 1-7, every finding with its two lines and scope, and at the end the
  fenced `verdict` block over the lines DEC-1106 touches:
  `{"kpis": [{"kpi": "S12", ...}, {"kpi": "S13", ...}, {"kpi": "S14", ...}, {"kpi": "S15", ...}, {"kpi": "S22", ...}, {"kpi": "F15", ...}]}`
  with each `{"kpi", "verdict": "pass|fail", "findings": [{"id", "scope", "ordinary_work", "consequence"}]}`.
