# Brief: independent test designer, W2-111 (ticket DAEO-qvff), run 1 (tests)

You are a fresh independent test designer (MR-3). One ticket: DAEO-qvff (W2-111), profile LITE, class C1, a test revision under the owner's named decision (DEC-979 item 1 D2 (a), P-LATENCY-1; DEC-906 item 1). Headless: only your last message is read.

## Objective
Revise the hook-latency cases of W1-02, W1-05 and W2-57 so each judges the hook's own work, not the machine's load, at the same bound of 100 ms at p95. Lower nothing. Remove, skip, xfail or mark flaky nothing.

## Where you work
| what | path |
|---|---|
| your tree (write here only) | /home/usain/gov-os-worktrees/W2-111-tests |
| branch | w2/W2-111-tests (commit here; never merge, never push) |
| allowed paths (write only these) | tests/acceptance/W1-02/test_w1_02_guard_hook.py, tests/acceptance/W1-02/README.md, tests/acceptance/W1-05/test_w1_05_live_hooks.py, tests/acceptance/W1-05/README.md, tests/acceptance/W2-57/test_w2_57_designer_read_p95.py, tests/acceptance/W2-57/README.md |
| your scratch (uncommitted scripts, logs) | /home/usain/gov-os-worktrees/W2-111-tests/.gov-runtime/scratch/td/ |
| ticket (read it first, read-only) | /home/usain/Dynamic-Agentic-Engineering-OS/.tickets/DAEO-qvff.md |
| decisions (read by id) | /home/usain/gov-os-worktrees/W2-111-tests/docs/DECISION_REGISTER.md: DEC-979 (line ~12282, item 1 D2), DEC-906 (~10585), DEC-968 (~12129), DEC-958 |
| the owner's package | /home/usain/gov-os-worktrees/W2-111-tests/governance/project/orchestration/packages/CAPACITY-1.md, section "D2. P-LATENCY-1" |

The support modules (`w1_02_support.py`, `w1_05_support.py`, `w2_57_list_support.py`, the conftests) are NOT in your paths: read them, do not edit them. Everything you need is reachable from the test files.

## The cases (collect-only finds 15 ids, not the ticket's "11")
- `tests/acceptance/W1-02/test_w1_02_guard_hook.py::test_decision_p95_is_under_100_ms` — 5 parameters
- `tests/acceptance/W1-05/test_w1_05_live_hooks.py::test_a_call_waits_under_100_ms_p95_for_the_hook` — 9 parameters
- `tests/acceptance/W2-57/test_w2_57_designer_read_p95.py::test_a_test_designer_s_read_on_a_branch_with_changes_is_decided_under_100_ms_at_p95` — 1

The ticket names the two parametrized functions "in its parameters": every parameter is in scope. Revise all 15. Keep all 15 ids exactly as they are now (same function names, same parameter ids). Name the 15-versus-11 count in `discoveries`.

## What must be true (the ticket's KPI lines)
- S1: each case measures the hook's own work at 100 ms p95, not raised. The measure is open in the ticket between (i) the CPU time (user + system) of the hook's process and its children over each call, and (ii) wall time against a quiet reference measured beside it in the same run. **The lead's choice (DEC-1052): use (i), the CPU-time form.** It sees the children: `resource.getrusage(resource.RUSAGE_CHILDREN)` read before and after one synchronous hook call counts the hook and every process it waited for (its forked decision process, the git it runs). Already present: `w1_02_support.children_cpu_seconds()` and `HookResult.cpu_seconds`, filled by `run_hook_raw` (check that the path `run_hook` takes fills it; one Popen path at w1_02_support.py:~465 returns no cpu_seconds). W1-05's `support.timed_pre_tool_use` returns only wall seconds: take the RUSAGE_CHILDREN difference around the call in the test file itself (it waits for every registered command before it returns, so the difference is the sum of all of them: that is the call's hook work, and summing is stricter than wall, never looser). If you find the CPU-time form cannot see some of a hook's work (a process not waited for), stop and say so in your return with the evidence; do not switch measure silently.
- Keep the warm-up, the 40 samples, the p95 by nearest rank and the bound `LATENCY_BOUND_S = 0.100`. Decide whether the "repeat up to three rounds" stays; it may stay (it lowers nothing), but say in the README why.
- The assertion messages report the CPU p95 per round in ms and, for information, the wall p95 beside it.
- S2/F3: the verdict does not change with load (see Verify below).
- S3/F2: a planted hook that does 150 ms of its own work per call fails every revised case (see Verify below).
- S4: each of the three READMEs gets a section (headed for W2-111, with the line `Rewrite-Reason: DEC-979`) that states what its case measures, why wall time under load is not the measure (the 2026-10-31 traces: red 8, 0, 1 of 11 with W2-106 and 0, 0, 5 without, at loads 15 to 30; the cases pass alone on a quiet machine; a wall clock under load times the scheduler's queue, not the hook), the measured figures (below), and the planted-hook result. Each case's docstring says the same in a line or two. Keep the existing README content; add, do not rewrite others' sections.
- F1: no raised bound, no case removed, no `skip`/`xfail`/`flaky` mark added. `git diff` will be read for it.

Not here: the hook itself (a slow hook is a product ticket); the guard's decisions; any other case.

## Verify (your evidence)
Every pytest through the heavy slot, with a TMPDIR outside the repository and outside ~/gov-os-runs:
```
env TMPDIR=/tmp/w2-111-td-tmp PYTHONUSERBASE=/home/usain/.local HOME=/home/usain/gov-os-worktrees/W2-111-tests/.gov-runtime/scratch/empty-home PYTHONPATH=/home/usain/gov-os-worktrees/W2-111-tests/src bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh python3 -m pytest <the 3 case node ids> -q -p no:cacheprovider -o tmp_path_retention_policy=failed
```
(mkdir the TMPDIR and empty-home first, in a script file.) Put anything longer than one line in a script under your scratch and run it with `bash <file>` or `python3 <file>`.

1. **Green on the real hook, at the ambient load.** Run the 15 cases; record `cat /proc/loadavg` before and after, each case's CPU p95 and wall p95 (ms). Tonight's ambient load is about 12 to 25. Run it at least twice at different moments and record both loads.
2. **The quiet reference.** A run on an idle machine is not available tonight. Record, in the same runs, each case's figures; the lead names the quiet-machine run and the load-50 run (the CTO's benchmark, in a window with few leads) as pending. **Never generate load yourself** (no stress tools, no busy loops beside the run).
3. **The planted 150 ms hook.** Put a hook that does 150 ms of its own CPU work per call in place of the real one, for each of the three files, and run every case: each of the 15 must FAIL, on the latency assertion (not on a decision assertion or a setup error). "150 ms of its own work" means a busy loop until the process's own CPU time (`time.process_time()`) reaches 0.150 s, then the real hook's decision (so the decision assertions still pass and only latency fails). Do it with a scratch harness only (for example a pytest plugin under your scratch passed with `-p`, with `PYTHONPATH` including the scratch folder, that wraps or monkeypatches the hook entry / `subprocess` call in the fixture's project copy, or a copy of the template hook prefixed with the busy loop) — nothing in the committed tests may carry a switch, environment variable or hook for planting. Run the planted set at the ambient load; record the load and the figures.
4. **Collect-only** on the three files' cases names the same 15 ids as before.
5. Hygiene: `git -C /home/usain/gov-os-worktrees/W2-111-tests diff --stat 085b4391c` shows only your allowed paths; grep the diff for `skip`, `xfail`, `flaky` and for the bound.

Record the commands, loads and figures in the READMEs (the measured figures, short) and in full in your scratch (log files), and name the log paths in your return.

## Commit (your paths only, on w2/W2-111-tests)
```
git -C /home/usain/gov-os-worktrees/W2-111-tests commit -m "W2-111: the hook-latency cases time the hook's own work (CPU time of the hook and its children), at the same 100 ms p95" --trailer "Task: DAEO-qvff" --trailer "Role: independent-test-designer" --trailer "Implements: DEC-979, DEC-906, DEC-968" --trailer "Rewrite-Reason: DEC-979" -- <your changed allowed paths>
```
One or more commits; every commit carries all four trailers. `Task:` is DAEO-qvff, never W2-111. Never `Role: owner` or `Decided-by:`.

## Rules
- Reads are open (the whole repository, history). Refused: secrets and keys; the held-out qualification material's contents; the hidden half of any evaluation set; never open the evaluation sets' root or any hidden or memory-verdict folder.
- No `gov retrieve`, no `gov context` (you are in the sandbox): search with the Read and Grep tools, and search again once in other words if the first does not answer.
- No merge, no push, no install. Write only inside your allowed paths and your scratch.
- If another ticket's case, or an older case asserting a behaviour the owner has since decided, is red on your branch: name it with file:line in your return; do not fix it.
- A resource gate's refusal (heavy slot, memory, disk) is a wait, not a refusal: wait and run again. Refused twice for the same action by the guard, the sandbox or a hook: stop and say so in your return. Never work around a refusal.
- If a KPI line cannot be met inside your paths, stop and return with the question, its options and cost, and your recommendation.

## Return (your last message; nothing else is read)
The twelve fields, each a labelled line ("none" where nothing):
task: / status: (DONE or BLOCKED) / work_completed: / files_changed: / evidence: (loads, per-case CPU and wall p95, the planted run's 15 failures, log paths) / tests: (the commands and counts) / discoveries: / risks: / lessons: / proposed_decisions: / unresolved: / recommended_next_action:
Then: `commits: <hash12> <subject> | trailers` per commit, and `guard_refusals: none | - <time> | <command form> | <the reason given> | true or false-positive`.
