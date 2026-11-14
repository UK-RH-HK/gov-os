# Brief: independent test designer, W2-182 (DAEO-5y8d), run 1 batch 2: revise W2-128's row-8 case (line F, DEC-1163 (1))

You are a fresh independent test designer (role independent-test-designer), ticket DAEO-5y8d (W2-182), profile LITE, class C1.
Headless: only your last message is read. A first batch (commit 6e3697785 on this branch) revised six other cases;
leave those files alone.

## Where you work
| what | path |
|---|---|
| your tree (write here only) | /home/usain/gov-os-worktrees/W2-182-tests |
| branch | w2/W2-182-tests (head 6e3697785) |
| the ticket (read-only; the CTO widened it by line F in 775b430cd) | /home/usain/Dynamic-Agentic-Engineering-OS/.tickets/DAEO-5y8d.md |
| the decision register (grep by id only) | /home/usain/gov-os-worktrees/W2-182-tests/docs/DECISION_REGISTER.md |
| scratch for scripts, temp folders and plant copies | your sandbox's own `$TMPDIR` (the tree's .gov-runtime/scratch/ is not writable for you) |

Your allowed paths for this batch (write nothing else): `tests/acceptance/W2-128/test_w2_128_rows.py`, `tests/acceptance/W2-128/README.md`.

## The line (the ticket's F)
F: W2-128's row 8 records that the line "Run `gov accept` for a ticket whose suites need the code index outside the sandbox, until W2-56" is gone from both kernel templates (W2-56 closed; the owner's DEC-1163 (1), b88a76172), so W2-128 and W2-152 S10 (which runs gov accept W2-128) are green [DEC-1163 (1), DEC-1156 (7)]. Verify: tests/acceptance/W2-128/test_w2_128_rows.py passes on w2/integrate; the row-8 case fails when the line is planted back into template/governance/kernel/templates/role-lead.md.

The case: `tests/acceptance/W2-128/test_w2_128_rows.py::test_row_8_gov_accept_runs_outside_the_sandbox_until_w2_56[role-lead]` and `[role-cto]`. It requires a line with "gov accept", "outside", "sandbox", "W2-56"; b88a76172 (on this branch) deleted that line from `template/governance/kernel/templates/role-lead.md` and `role-cto.md` (and `template/.rulesync/subagents/orchestrator.md`), so the case is red. Read DEC-1163 (1) by id.

Revise row 8 so it records the decided state: no unit of either template (role-lead, role-cto) carries the "gov accept … outside … sandbox … until W2-56" instruction (use the support's own `units_with` / matching so the same line form the case used to find is what it now refuses; match it as robustly as the old case found it). Keep the parametrisation over both stems. The case may be renamed only if the README map line changes with it (full node ids, both stems); prefer keeping the name stable unless it now states the opposite, in which case rename it and update the README map (W2-128 README lines ~204-205) to the new full node ids. Add a docstring paragraph "Revised for DEC-1163 (1) (W2-182, DAEO-5y8d; a recorded rewrite by a fresh test designer, DEC-491; routed by DEC-1156 (7), widened by DEC-1157 (12)) …": the reason, the decided behaviour (W2-56 closed; b88a76172), what it still catches. Lower nothing; remove, skip, xfail or mark nothing else.

## Planted break (prove, then remove)
In a throwaway copy of the tree under `$TMPDIR` (never in the worktree), plant the line "Run `gov accept` for a ticket whose suites need the code index outside the sandbox, until W2-56 [DEC-1052]." back into the copy's `template/governance/kernel/templates/role-lead.md`; the `[role-lead]` case must fail naming it. Do the same for role-cto. Record plant, command and failing line.

## How you run tests
Every pytest through the heavy slot, TMPDIR the sandbox's own `$TMPDIR` (outside the repository and outside ~/gov-os-runs):
```
env PYTHONUSERBASE=/home/usain/.local HOME=/home/usain/gov-os-worktrees/W2-182-tests/.gov-runtime/scratch/empty-home PYTHONPATH=/home/usain/gov-os-worktrees/W2-182-tests/src bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh python3 -m pytest <file>::<test> -q -p no:cacheprovider -o tmp_path_retention_policy=failed
```
Run the case alone, then the whole W2-128 folder once with `-m "not local_only" -k "not real and not green_here and not time_limit"`. Also run `tests/acceptance/W2-152` once (W2-152 S10 runs gov accept W2-128); if it cannot run in the sandbox (it needs the code index or gov accept outside the sandbox), say so and leave it to the lead. If another ticket's case turns red, name it with file:line and leave it. A resource gate's refusal is a wait.

## Searching and forms
No `gov retrieve` and no `gov context` in the sandbox: Read and Grep; search again once in different words if needed. Never open the evaluation sets' root, held-out material or any hidden or memory-verdict folder. Write and edit with the Write and Edit tools and absolute paths; scripts longer than one line go in `$TMPDIR`. Refused twice for the same call: stop and say so; never work around a refusal. No merge, no push.

## Commit (your paths only)
```
git -C /home/usain/gov-os-worktrees/W2-182-tests commit -m "W2-182: W2-128 row 8 records the gone 'until W2-56' line (F)" --trailer "Task: DAEO-5y8d" --trailer "Role: independent-test-designer" --trailer "Implements: DEC-1163, DEC-1156" --trailer "Rewrite-Reason: DEC-1163 (1)" -- <paths>
```
Never `Role: owner` or `Decided-by:`. Before you return: tracked `git status --short` empty; `git diff 6e3697785 --stat` names only your two paths; no added skip/xfail/flaky/rerun.

## Return (your last message; the twelve fields, each a labelled line, "none" where nothing)
task: / status: / work_completed: / files_changed: / evidence: (alone and folder results with counts; each plant, command, failing line) / tests: / discoveries: / risks: / lessons: / proposed_decisions: / unresolved: / recommended_next_action:
Then: commits: <hash12> <subject> | trailers as committed; guard_refusals: none or a line each.
