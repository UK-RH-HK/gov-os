Step 0, before any work: the sandbox check in /home/usain/gov-os-worktrees/W2-182-tests/.gov-runtime/scratch/brief/EMG-d4b-launched.md, reported first in your return (launch_worker.sh).

# Brief: independent test designer, W2-182 (DAEO-5y8d), run 1 — revise six drift-red cases (DEC-1163 (6), route (a))

You are a fresh independent test designer (role independent-test-designer), ticket DAEO-5y8d (W2-182), profile LITE, class C1.
Headless: only your last message is read.

## Where you work
| what | path |
|---|---|
| your tree (write here only) | /home/usain/gov-os-worktrees/W2-182-tests |
| branch | w2/W2-182-tests |
| your scratch | /home/usain/gov-os-worktrees/W2-182-tests/.gov-runtime/scratch/ |
| your context packet (gov context output, JSON: the ticket, KPIs, sources) | /home/usain/gov-os-worktrees/W2-182-tests/.gov-runtime/scratch/brief/td-context.md |
| the analysis (each case's failure text, the merge that changed the behaviour, the smallest fix) | /home/usain/gov-os-worktrees/W2-182-tests/.gov-runtime/scratch/brief/nightly-20261113-analysis.md |
| the ticket (read-only) | /home/usain/Dynamic-Agentic-Engineering-OS/.tickets/DAEO-5y8d.md |
| the decision register (grep by id only) | /home/usain/gov-os-worktrees/W2-182-tests/docs/DECISION_REGISTER.md |

Your allowed paths (write nothing else; in particular NOT `tests/acceptance/W1-07/**`, NOT `src/**`, NOT `template/**`):
- tests/acceptance/W1-32/test_w1_32_command_set.py, tests/acceptance/W1-32/README.md
- tests/acceptance/W1-18/test_w1_18_on_demand_start.py, tests/acceptance/W1-18/README.md
- tests/acceptance/W2-123/test_w2_123_retry.py, tests/acceptance/W2-123/README.md
- tests/acceptance/W2-121/test_s1_lock_off_status.py, tests/acceptance/W2-121/README.md
- tests/acceptance/W2-136/test_w2_136_never_a_gate.py, tests/acceptance/W2-136/README.md
- tests/acceptance/W2-23/test_w2_23_space.py, tests/acceptance/W2-23/README.md

`template/.rulesync/hooks.jsonc` is in the ticket's paths but is a product-spec worker's line, not yours: do not touch it.

## The work
Each of the cases below records a behaviour the owner already decided and that has landed (product code is right; no `src/gov/**` change). Revise each case to that behaviour, keeping its point. Lower nothing; remove, skip, xfail or mark nothing; no flaky/rerun mark. Each revised case must still fail on a planted break of what it guards.

| id | case (file::test) | KPI line (the ticket's) |
|---|---|---|
| B | tests/acceptance/W1-32/test_w1_32_command_set.py::test_the_command_set_is_the_twelve_and_the_three_recorded_ones | W1-32's recorded command list holds the four approved commands gov --help shows (dispatch W2-121, adapters W2-23, session-watch W2-159, wait W2-160), and nothing else changes in it [DEC-1163 (6), DEC-1156 (7)]. Verify: passes; a planted unrecorded command name added to gov --help in a stand-in makes it fail. |
| C | tests/acceptance/W1-18/test_w1_18_on_demand_start.py::test_with_the_server_not_answering_a_retrieval_answers_by_keywords_and_starts_nothing and tests/acceptance/W2-123/test_w2_123_retry.py::test_after_the_last_failed_try_the_rebuild_states_the_tries_and_waits_and_no_partial_store_is_reported_built | expect REBUILD_FAILED where a rebuild's asked-for semantic store is not recreated (W2-124, DEC-1150 (3)), each keeping its point (the keyword answer and no start for W1-18; the last failed try's record for W2-123). Verify: both pass; each still fails on a planted break (W1-18: a retrieval that starts the server; W2-123: a retry record that is not written). |
| R | tests/acceptance/W2-121/test_s1_lock_off_status.py::test_s1_status_runs_no_pass_and_writes_nothing | takes its second snapshot only after the fake launched job's .exit file exists, so `gov dispatch status` is judged on what it writes, not on the job's late write. Verify: passes 20 runs in a row under load; still fails when a stand-in status writes a file. Prefer waiting for the `.exit` file before the first snapshot (bounded wait, a clear failure message on timeout) over excluding `logs/*.exit` from the snapshot, so nothing status could write is hidden. |
| D | tests/acceptance/W2-136/test_w2_136_never_a_gate.py::test_s10_no_module_of_gov_outside_plan_and_launch_imports_or_calls_gov_plan | the scan allows `src/gov/session_watch` to call gov plan (W2-159's S5: session-watch reads the dispatcher's ready list by `gov plan --ready`); every other module outside plan/ and launch/ is still refused [DEC-1163 (6) D (a), DEC-105]. Verify: passes; a planted module outside plan/, launch/ and session_watch/ calling gov plan fails it. Allow exactly the folder `src/gov/session_watch` (compare with Path.is_relative_to, DEC-1155), not a prefix string match. |
| E | tests/acceptance/W2-23/test_w2_23_space.py::test_s6_every_kernel_hook_exits_alike_with_a_space_in_the_project_dir | expects the seven kernel hooks (W2-176's `context_watch.py`). Verify: passes once the template is wired; a planted eighth hook script with no wiring fails it. Note: the template's wiring of `context_watch.py` (template/.rulesync/hooks.jsonc) is NOT on your branch yet (a product-spec worker adds it); so on your branch this case is expected red with exactly the message naming `context_watch.py` as unreached. Say so in your return; do not work around it. |

For B: `RECORDED` comes from W1-07's support (`tests/acceptance/W1-07/w1_07_support.py`), which is NOT in your paths. Record the four approved commands in W1-32's own file (a named tuple beside the existing `EXCUSED_UNTIL_RECORDED`, one comment line each citing its ticket and approval), keep the first assert's pinned set exact for W1-07's list, and count the four as recorded in the `extra` and `gone` checks. Any other unrecorded command must still fail it; a recorded command gone from gov --help must still fail it. If you find the point cannot be kept within your paths, stop and say so (the lead returns PACKAGES).

Each revised test's docstring gets a "Revised for DEC-1163 (6) (W2-182, DAEO-5y8d) …" paragraph in the form of the earlier revision paragraphs in these files: the reason, the decided behaviour and the landing merge it follows (the analysis names each), and what the case still catches. Update each folder's README map line only where the case's description changes.

## Planted breaks (prove each, then remove)
For each S line, plant the break in a throwaway copy (scratch, or an uncommitted edit you revert), run the case, and record in your return: the plant, the command, the failing assertion line. Then remove the plant. Nothing planted is committed. Forms: B a stand-in gov whose --help adds an unrecorded command name; C W1-18 a retrieval that starts the server, W2-123 a retry record not written; R a stand-in status that writes a file; D a planted module outside plan/, launch/, session_watch/ calling gov plan; E a planted eighth hook script with no wiring (it must fail on that name, distinct from the context_watch.py red).

## How you run tests
Every pytest through the heavy slot, TMPDIR outside the repository and outside ~/gov-os-runs:
```
env TMPDIR=/tmp/w2-182-td PYTHONUSERBASE=/home/usain/.local HOME=/home/usain/gov-os-worktrees/W2-182-tests/.gov-runtime/scratch/empty-home PYTHONPATH=/home/usain/gov-os-worktrees/W2-182-tests/src bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh python3 -m pytest <file>::<test> -q -p no:cacheprovider -o tmp_path_retention_policy=failed
```
(make /tmp/w2-182-td first with `mkdir -p /tmp/w2-182-td`). PYTHONPATH must be absolute (a relative one breaks W2-123's child process). A whole-folder run adds `-m "not local_only" -k "not real and not green_here and not time_limit"`. Run each revised case alone, then its whole folder once. For R, also 5 runs in a row alone (the lead does the 20-under-load run). If another ticket's case turns red, name it with file:line and leave it. A resource gate's refusal is a wait, not a refusal: wait and retry. Never a hand-written sleep loop beyond a single bounded wait.

## Searching
No `gov retrieve` and no `gov context` in the sandbox: use the Read and Grep tools; if the first search does not answer, search again once in different words; then answer from both with path and lines, or say "not found". Reads are open, except: secrets, the held-out qualification material's contents, the evaluation sets' root and any hidden or memory-verdict folder (never open them).

## Forms that work
Write and edit with the Write and Edit tools and absolute paths. Anything longer than one line goes in a script under /home/usain/gov-os-worktrees/W2-182-tests/.gov-runtime/scratch/, run with `bash <file>` or `python3 <file>`. Literal paths only as write targets. Refused twice for the same call by the guard, sandbox or a hook: stop and say so; never work around a refusal. No merge, no push.

## Commit (your paths only; one or more commits)
```
git -C /home/usain/gov-os-worktrees/W2-182-tests commit -m "W2-182: <subject>" --trailer "Task: DAEO-5y8d" --trailer "Role: independent-test-designer" --trailer "Implements: DEC-1163, DEC-1156, DEC-1150, DEC-105" --trailer "Rewrite-Reason: DEC-1163 (6)" -- <paths>
```
`Implements:` only ids from the ticket's sources (DEC-1163, DEC-1156, DEC-1150, DEC-1159, DEC-105, DEC-781), each the ones your change applies. Never `Role: owner` or `Decided-by:`. Before you return, `git -C /home/usain/gov-os-worktrees/W2-182-tests status --short` must be empty for tracked files, and `git -C /home/usain/gov-os-worktrees/W2-182-tests diff 2bf4430f4 --stat` must name only your allowed paths; `git diff 2bf4430f4 | grep -nE "skip|xfail|flaky|rerun"` on added lines must show nothing new.

## Return (your last message; the twelve fields, each a labelled line, "none" where nothing)
task: / status: (DONE or PACKAGES or ESCALATION) / work_completed: / files_changed: / evidence: (each case's alone result and folder result with counts; each planted break: plant, command, failing line) / tests: / discoveries: / risks: / lessons: / proposed_decisions: / unresolved: / recommended_next_action:
Then: commits: <hash12> <subject> | trailers as committed; guard_refusals: none or a line each.
