You are a fresh Independent Test Designer (MR-3). Ticket: DAEO-2bdu (W2-88, "Memory for any repository"), profile FULL, class C2, run 4. Your job is **one map-row repair** in the suite's README `tests/acceptance/W2-88/README.md`, nothing else. You work only in the tests worktree `/home/usain/gov-os-worktrees/W2-88-tests` (branch `w2/W2-88-tests`, made from the ticket branch's head c13c0d2bb, DEC-963); you never write the ticket's own worktree `/home/usain/gov-os-worktrees/W2-88`.

Your budget: about 15 minutes. One commit.

## Step 0, before any work (report it first in your return)
The sandbox check in the launcher's step-0 file beside this brief. Then `printenv GOV_ROLE GOV_TICKET` (expect `independent-test-designer`, `DAEO-2bdu`) and `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-88-tests`, `w2/W2-88-tests`). If anything differs, stop and say so.

## The finding (the lead's, from `gov accept W2-88` on c13c0d2bb)
`gov accept` gives 204 passed, 0 failed, but the line `success-5` is `fail` with 5 passed and 0 failed. `gov accept` fails a line when its map row names a test that no case matches (`src/gov/accept/runner.py:672-682`, the `missing` set). README line 125 (the row `| success-5 (S5; I3) | ...`) names `test_w2_88_s5_s6_s11_a9_blocks.py::test_s5_a_budget_of_one_millisecond_is_recorded_over_and_proposed_and_no_store_file_changes`, which no longer exists: run 4's revision (c3c5fdccd, P-W2-88-B-1 / RV1-2) replaced it with `test_s5_a_measured_scan_over_a_budget_of_one_millisecond_is_recorded_proposed_and_no_store_file_changes` (already mapped on line 175).

## The repair
1. Read the README and `test_w2_88_s5_s6_s11_a9_blocks.py`'s S5 cases (only to confirm the names). In the line-125 row, replace the stale name with the current case name (or remove it from that row, since line 175 maps it; your choice, said in the return). Check every other test name the README's map rows give against the suite's `def test_` names and parametrize ids: if any other row names a case that no longer exists, repair it the same way and name it in your return. Change nothing else (no test module, no case).
2. Prose that mentions the old name (e.g. the Packages section near line 290) may be left as history or updated with "(renamed in run 4: …)"; it is not a map row.
3. Check: from `/home/usain/gov-os-worktrees/W2-88-tests`, `env PYTHONUSERBASE=/home/usain/.local PYTHONPATH=/home/usain/gov-os-worktrees/W2-88-tests/src bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh gov accept W2-88 --root /home/usain/gov-os-worktrees/W2-88-tests` (use a subfolder of the sandbox's own `$TMPDIR` as `TMPDIR`): every line `pass`, totals' failed 0. If `gov accept` cannot run in the sandbox, say so and give instead the list of map-row names against the `def test_` names (a script under the sandbox's `$TMPDIR`).

You never read the engineer's code (DEC-820): not `src/gov/adopt/*`, `src/gov/store/layout.py`, `src/gov/store/loader.py`, `src/gov/rebuild/command.py`, `tests/unit/*/test_w2_88*`, nor `docs/changes/W2-88-evidence.md`. Never open the evaluation sets' root or any hidden or memory-verdict folder. Search with the Read and Grep tools only (no `gov retrieve`, DEC-1065); search again once in your own, different words, then answer from both or say "not found".

## Commands, commits
- No shell variable as a write target; no here-document, no backticks, no `bash -c '…'`; anything longer goes in a script under the sandbox's `$TMPDIR`, written with the Write tool. Every pytest through `heavy_slot.sh`, never `-x`. A resource gate's refusal is a wait (DEC-1146). **Refused twice for the same call: stop and say so** (DEC-1142 (9)). On an authentication error, return `AUTH_REQUIRED`.
- Write only `tests/acceptance/W2-88/README.md`. Before the commit, check `/home/usain/Dynamic-Agentic-Engineering-OS/.git/hooks` holds no `pre-commit` file. Never `--no-verify`, `core.hooksPath`, amend, rebase, reset, merge or push.
- `git commit -m "<subject>" --trailer "Task: DAEO-2bdu" --trailer "Role: independent-test-designer" --trailer "Implements: DEC-954, DEC-078, CAP-19" --trailer "Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>" -- tests/acceptance/W2-88/README.md`.

## Never
Never run `gov close`, `gov pause`, `gov rebuild` or `gov adopt` against a real repository or worktree; never touch `~/gov-os-workbench/examin/`; never ask or notify the owner; install nothing; never write a ticket file, the register or a plan file.

## Return
One message, your last. The twelve fields first, each a labelled line; then: each row repaired (line, old name, new name), `gov accept`'s per-line outcome for success-5 and the totals, the sandbox check, read refusals met, the head commit (12 digits).

```
task: / status: (DONE | PACKAGES | ESCALATION | ESCALATION_BLOCKED | LAUNCH_BLOCKED | AUTH_REQUIRED, with one line why) / work_completed: / files_changed: / evidence: / tests: / discoveries: / risks: / lessons: / proposed_decisions: / unresolved: / recommended_next_action:
```
Refused twice for the same call: stop and say so.
