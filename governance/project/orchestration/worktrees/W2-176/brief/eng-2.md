Step 0, before any work: the sandbox check in /home/usain/gov-os-worktrees/W2-176/.gov-runtime/scratch/brief/EMG-d4b-launched.md, reported first in your return (launch_worker.sh).

# W2-176 (DAEO-ktiw), engineer, run 2 batch: the CTO's decisions on run 1's packages

Read `briefs/EMG-common.md` beside this file first; its rules hold.

**Role:** engineer (fresh). **Worktree:** `/home/usain/gov-os-worktrees/W2-176`, branch `w2/W2-176`, head `d69eed1fc`
(tree clean). **Ticket:** `DAEO-ktiw` (W2-176), profile STANDARD, class C3. Your scratch:
`/home/usain/gov-os-worktrees/W2-176/.gov-runtime/scratch/engineer/`.

## The spec
Read `/home/usain/gov-os-worktrees/W2-176/.tickets/DAEO-ktiw.md` (S2 was amended; read the "Delegated" line at its end):
KPIs S1, S2, S3, F1 and F2 are your spec (S4, `docs/changes/W2-176-CIT-P.md`, is the lead's: do not touch it). The
governed context packet is `/home/usain/gov-os-worktrees/W2-176/.gov-runtime/scratch/lead/briefs/eng-context-2.md`.
Read decisions by id in `/home/usain/Dynamic-Agentic-Engineering-OS/docs/DECISION_REGISTER.md` (grep by id only:
DEC-1140 (4), DEC-1118 (A), DEC-264, DEC-259). Search with Read and Grep; search again once in other words if needed.

Run 1 built both hooks (`template/governance/kernel/hooks/precompact.py`, `.../context_watch.py`) and their unit tests
(`tests/unit/hooks/test_w2_176_precompact.py`, `tests/unit/hooks/test_w2_176_context_watch.py`); review round 1 was
READY with findings R1-R7 (`/home/usain/gov-os-worktrees/W2-176/.gov-runtime/scratch/lead/log/rev-1.result.md`). This
batch changes that code; it does not rewrite it.

**Allowed paths (nothing else):** `template/governance/kernel/hooks/precompact.py`,
`template/governance/kernel/hooks/context_watch.py`, `tests/unit/hooks/test_w2_176*`,
`tests/unit/hooks/test_resume_hooks.py` and `tests/unit/hooks/test_w29_hooks.py` (these two: assert-only updates, see
1). Never `.claude/`, a settings file, `sessionstart.py` or another hook. Keep the names `STAMP`, `checkpoint_rel` and
`split` in precompact.py (`sessionstart.py` imports them).

## What to change (tests first: red, commit, then the code, commit)
1. **P1 (a), the five older reds (assert-only).** `test_resume_hooks.py::test_an_unset_role_is_not_the_orchestrator`,
   `::test_precompact_appends_one_block_and_sessionstart_warns`, `::test_a_checkpoint_precompact_cannot_write_is_left_as_it_was`,
   `::test_a_write_that_fails_part_way_leaves_the_checkpoint_as_it_was`, and
   `test_w29_hooks.py::TestPreCompactCombined::test_checkpoint_failure_reports_systemmessage` expect the old stdout (empty,
   or one JSON object). Change only their assertions to S1's form: the read-first line first (starts with the
   instruction and `READ FIRST:`), and, where a systemMessage is expected, the JSON object on the last line (parse that
   line, assert what was asserted before). No other edit to those files: no setup, fixture or case added or removed.
2. **P2 (a), the CTO's report-state path** in `context_watch.py`'s wording: `<root>/.gov-runtime/scratch/orchestrator/log/report-state.json`
   (not `<root>/log/report-state.json`). A test asserts the path in the CTO's text.
3. **R7:** `newest()` in precompact.py catches `OSError` from the per-file stat too (a file deleted between the listing
   and the stat), returning the next newest or the folder; the line is always printed. A unit test plants it (import
   the module and patch, or a stat that raises).
4. **R2 (P3):** `context_watch.py` prints nothing and writes no state for an event that carries a non-empty `agent_id`
   (a subagent's tool call). Test: an `agent_id` event at 90 % gives no output and no state file; the next main event
   at 90 % gives the reminder.
5. **R1 (P3), re-arm:** the reminder fires once per context window: when the session's usage is below 50 % of its
   window (as after a compaction) and a state file exists for the session, remove it (silently; any error ignored), so
   the next 85 % reminds again. Between 50 % and 85 % nothing changes. Test: 90 % fires; 90 % again silent; 60 % silent
   and still armed-off; 4 % silent (re-arms); 92 % fires again. The state file stays the only write (F1).
6. **P4, the window per session:** the window is the model's window from the table for the **CTO's own session** only,
   and `min(model window, 200_000)` for every lead and worker (DEC-1118 (A); DEC-1140 (4)). The CTO's session is
   `GOV_ROLE=orchestrator` with `GOV_TICKET` naming a coordination ticket: `<project root>/.tickets/<GOV_TICKET>.md`
   whose front matter has `class: coordination` (today `DAEO-sdxk`, W2-00; read only the file's first 4 KiB; any error
   or no such file: not the CTO, so the 200,000 cap, the earlier reminder, applies). Use the same test for the role's
   wording (the CTO's files: its CHECKPOINT's RESUME HERE, DECIDED-NOT-DONE, report-state; a lead, orchestrator on any
   other ticket: its CHECKPOINT via `checkpoint_rel`; anyone else: its record). Tests: an Opus 5.5 transcript at 180k
   is silent for the CTO's session and reminds a lead and an engineer (90 % of 200k); at 850k the CTO's session is
   reminded (S2's "an Opus 5.5 transcript uses 1,000,000" now under the CTO's setup, with a planted `.tickets` file);
   an unknown model is 200,000 for both. Keep the table patchable as in run 1, so 50/84/85/99 % stay cheap.
   F1 holds: no `CLAUDE_CODE_AUTO_COMPACT_WINDOW`, `autocompact` or any threshold string in either source; no
   `decision` key; the cap is a constant of the reminder, not a compaction setting.

Keep S3 (last 256 KiB, under 100 ms median of 5 on 50 MB, fail-safe exit 0 and no stdout) and every run-1 case green;
update a run-1 W2-176 case only where these decisions change its expectation, and say which in `work_completed`.
Keep the code delta small (about 40 lines of hook code).

Run your unit tests (create the empty-home folder first):
`env HOME=/home/usain/gov-os-worktrees/W2-176/.gov-runtime/scratch/empty-home PYTHONUSERBASE=/home/usain/.local PYTHONPATH=/home/usain/gov-os-worktrees/W2-176/src python3 -m pytest tests/unit/hooks -q -p no:cacheprovider -o tmp_path_retention_policy=failed -m "not local_only" -k "not real and not green_here and not time_limit"`
It must be fully green (run 1 left 5 reds there; item 1 clears them). Then the regression, unchanged, through the gate:
`env HOME=/home/usain/gov-os-worktrees/W2-176/.gov-runtime/scratch/empty-home PYTHONUSERBASE=/home/usain/.local PYTHONPATH=/home/usain/gov-os-worktrees/W2-176/src bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh python3 -m pytest tests/acceptance/W1-29 tests/acceptance/W1-49 tests/acceptance/W2-62 -q -p no:cacheprovider -o tmp_path_retention_policy=failed -m "not local_only" -k "not real and not green_here and not time_limit"`
A red there: re-run that case alone once; if it still fails and your change did not cause it, name it with its output
in `risks`. Never edit those suites; never `git stash`.

## Commit (your paths only, after each green batch)
```
git commit -m "W2-176: <subject>" --trailer "Task: DAEO-ktiw" --trailer "Role: engineer" --trailer "Implements: DEC-1140, DEC-1118, DEC-264, DEC-259, DEC-838, DEC-901, DEC-445, DEC-208, DEC-250" -- <paths>
```
No push, no merge, no `.tickets/` edit.

## Return (your last message; nothing else is read)
The twelve fields, each a labelled line ("none" where nothing):
`task: / status: / work_completed: / files_changed: / evidence: / tests: / discoveries: / risks: / lessons: / proposed_decisions: / unresolved: / recommended_next_action:`
In `evidence`: each commit hash12 and subject; the new sha256 of both hook files at your last commit; the additionalContext
text in full for the CTO, a lead and an engineer. In `tests`: counts for the unit run and the regression run, and the
50 MB timing's median.
