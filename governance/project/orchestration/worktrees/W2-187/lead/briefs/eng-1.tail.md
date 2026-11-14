
----

## Rules
- **One judged path, two modes** (the ticket's rabbit holes): the standing mode reuses `driver._Cycle`, `_refusal`,
  `_history`, `_finish`, `declare.declare`, `measure.run`, `judge.run` / `_Judge.one`, `prompts`, `matcher` and
  `figures.build` with a `week=` argument; never copy the reader path into a second module; `prompts.py` is unchanged
  (`tests/unit/memaudit/test_prompts.py` passes unchanged). The new modules are `standing.py` (I3, I4's week rule, I7,
  I8) and `maintain.py` (I10). `maintain` is never a gate: exit 0 always (4 for usage), each item bounded by its timeout.
- **Counts only (S4, F1):** a standing run writes no `misses.jsonl`, starts no `classes`, auditor, `pool` or writer;
  nothing of a standing set's questions is written outside `<sets root>/runs/<set>/` (mode 0700); `say` stays the only
  printer; no question id, question, gold, answer, citation or path of a standing set in stdout, stderr, any HISTORY,
  STANDING, MAINTAIN, COUNTS, DIGEST or log line.
- **The bar (I5):** `declare.bar` and `declare.ROUNDING` as I5 gives them, for both modes. The existing acceptance
  cases that pin 85 % (W2-170, W2-171, W2-172) are being revised in parallel by the independent test designer; they turn
  green when the designer's suite is merged. Never edit `tests/acceptance/` (it is not yours; a restore or conflict there
  is the test designer's). Update `tests/unit/memaudit/` cases that pin the old bar.
- **State per repository (I2):** `schedule.state_dir(runs, repo)` replaces `schedule.folder(runs)` everywhere; the
  driver passes `GOV_INDEP_RUNS_DIR=<key folder>` to every child.
- **G6:** show in `docs/changes/W2-187-evidence.md` (by a unit test or a planted run) what `maintain` does with a store
  at the main line's head whose layout is stale (one rebuild by the same command, else `stale kept`).
- Work test first: unit tests under `tests/unit/memaudit/` (and `tests/unit/adopt/test_w2_187*` for `walls_act`) for
  each Interface item, small and fast, planted under `tmp_path` only.
- **Size:** the ticket estimates about 700 lines (G1+G2 300-450, G3 100-150, G5 150-250, S11 about 20). If S10 and S11
  split off as W2-187b (pre-approved, DEC-1179 O8 (a)), your lead tells you; build S1-S9 first (I1-I9, I12's standing
  lines), then S10 (I10) and S11 (I11), committing between them, so a split leaves a clean S1-S9.
- **The acceptance suite and your batches:** the independent test designer writes `tests/acceptance/W2-187/` in
  parallel; your lead merges it into this worktree only while you are between batches. Commit your code and unit tests
  in batches as you go. **When `/home/usain/gov-os-worktrees/W2-187/.gov-runtime/scratch/lead/TESTS-READY` exists**
  (check after each committed batch), read `tests/acceptance/W2-187/README.md` and its helpers, and make the suite pass.
  If it does not exist once your S1-S11 code and unit tests are committed, stop and return (status DONE, with
  "acceptance suite not yet merged" in `unresolved`); your lead resumes you.
- Never stage or commit while `git status` shows a merge in progress; if your tree changes under you unexpectedly, stop
  and return saying so.
- **Every pytest through the heavy-slot gate**, TMPDIR the sandbox's own `$TMPDIR` (outside the repository and outside
  ~/gov-os-runs); make the empty HOME first with `mkdir -p /home/usain/gov-os-worktrees/W2-187/.gov-runtime/scratch/empty-home`:
  `bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh env HOME=/home/usain/gov-os-worktrees/W2-187/.gov-runtime/scratch/empty-home PYTHONUSERBASE=/home/usain/.local PYTHONPATH=/home/usain/gov-os-worktrees/W2-187/src python3 -m pytest tests/unit/memaudit -q -p no:cacheprovider -o tmp_path_retention_policy=failed -m "not local_only" -k "not real and not green_here and not time_limit"`
  and the same for `tests/acceptance/W2-170`, `W2-171`, `W2-172`, `W2-173`, `W2-88` and (once merged) `W2-187`, one
  folder per run. A single case: append `::<name>`. A heavy-slot or resource gate refusal is a wait: run again when it
  opens; it never counts as a refusal.
- The base-red rule: a case red on the base (5336a6fca) for a reason outside this ticket is reported, not fixed.
- Write `docs/changes/W2-187-evidence.md`: what was built, per KPI line the cases that show it and their result, the
  pytest summary lines, G6, the size in lines (`git diff --stat 5336a6fca`), and any reading of the Interface you had to
  make (with the item number).
- Anything longer than one line goes in a script under /home/usain/gov-os-worktrees/W2-187/.gov-runtime/scratch/eng/,
  run with `bash <file>` or `python3 <file>`. Literal paths only as write targets.
- **Commit** your paths only, in batches, the trailers in ONE final paragraph (a blank line between them hides `Task:`):
  `git commit -m "W2-187: <subject>" --trailer "Task: DAEO-0cd2" --trailer "Role: engineer" --trailer "Implements: DEC-1179, DEC-1176, DEC-1101, DEC-1125, DEC-1098, DEC-1097, DEC-1092, DEC-1074, DEC-1072" --trailer "Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>" -- <your paths>`
  Never `Role: owner` or `Decided-by:`. No merge, no push, no edit of `.tickets/`, the register or `tests/acceptance/`.
- Refused twice for the same call by the guard, the sandbox or a hook: stop and say so; never reach the same effect by
  another command, form or file (DEC-1142 (9)).

## Return (your last message; nothing else is read)
The twelve fields, each a labelled line ("none" where nothing): task / status (DONE, PACKAGES or ESCALATION) /
work_completed / files_changed / evidence (the pytest summary lines of each folder above) / tests / discoveries / risks
/ lessons / proposed_decisions / unresolved / recommended_next_action. Then `commits:` (hash12, subject, trailers) and
`guard_refusals:` (none, or each: time | form | the hook's reason | true or false-positive).
