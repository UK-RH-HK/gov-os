# Your assignment
You are a fresh orchestrator session. Your role's rules are in your system prompt (template `role-lead`); this brief gives this assignment's facts.
Ticket DAEO-f58b (W2-116), profile STANDARD. Objective: The designers' store in the product: a double-buffered store of the integration branch, refreshed after the nightly and once more a day, that a test designer's retrieval reads (SMART-WORK-1). The owner's SMART-WORK-1 decision 2 (DEC-983): the designers' store (DEC-963, DEC-966 item 3) becomes the product's, not only the CTO's `refresh_integration_store.sh` and `store_refresh_daily.sh`.

## Where you work
| what | path |
|---|---|
| your tree (write here only) | /home/usain/gov-os-worktrees/W2-116 |
| branch | w2/W2-116 |
| allowed paths | src/gov/status/**, docs/probes/DAEO-f58b/**, src/gov/rebuild/integration.py, src/gov/rebuild/command.py, src/gov/launch/store.py, src/gov/launch/launcher.py, src/gov/retrieve/command.py, docs/changes/W2-116-evidence.md, tests/unit/rebuild/test_w2_116*, tests/unit/launch/test_w2_116*, governance/project/rebuild.yaml, src/gov/retrieval/retrieve.py, tests/unit/status/test_w2_116*, tests/unit/retrieval/test_w2_116* |
| ticket file (read-only) | /home/usain/Dynamic-Agentic-Engineering-OS/.tickets/DAEO-f58b.md |
| your scratch | /home/usain/gov-os-worktrees/W2-116/.gov-runtime/scratch/ |

## What must be true (KPI lines and how each is checked)
| id | line | verify |
|---|---|---|
| S1 | `gov rebuild --integration <branch>` keeps a store of that branch's head in two detached worktrees outside the project, building into the one not in use and switching a link to it only when the build succeeded; a search during a build is answered from the ready one [DEC-963, DEC-983, DEC-982] | the success-1 cases in tests/acceptance/W2-116/test_w2_116_double_buffer.py (the build in a detached worktree behind the link, the two halves alternating, a search during a build and a killed build answered from the ready half) pass [Verify clause added, DEC-1157 (12)] |
| S2 | It is refreshed after the nightly's verdict and at a set second time each day (both in the project's configuration), and its status (head, age) is in `gov status` [DEC-966 item 3, DEC-983, DEC-982] | pass 2's cases: a planted configuration's two refresh times are read and the refresh runs after the nightly's verdict and at the second time; `gov status` names the integration store's head and age, and a stale store is named; a missing or invalid time refuses by name [Verify clause added, DEC-1157 (12)] |
| S3 | `gov launch independent-test-designer` points the session's retrieval at it; a designer's retrieval never reads a ticket worktree's store [DEC-963, DEC-983, DEC-982] | the success-3 cases in tests/acceptance/W2-116/test_w2_116_launch.py pass: each launched worker role's plain search reads the integration store from a worktree with none, and the session keeps its role and ticket [Verify clause added, DEC-1157 (12)] |
| S4 | The store is also refreshed after every landing on the integration branch, and it is the warm base `gov rebuild --seed` (W2-122) reads; a seed taken from a store behind the integration head is named, and only what changed since is re-embedded [DEC-1014 items 4 and 6, SMART-WORK-5 D, DEC-1015 item 3] (folds W2-06 S1, S2) | the success-4 cases in tests/acceptance/W2-116/test_w2_116_refresh.py pass: after a merge the refresh brings the store to the new head re-embedding only what changed, an unchanged head does nothing, `gov rebuild --seed` reads it and a seed behind the head is named [Verify clause added, DEC-1157 (12)] |
| S5 | A re-index never empties the semantic index; a model-less re-index reports the semantic facet unavailable instead [DEC-719]. [moved from W2-06 S5, DEC-1083] | the success-5 cases in tests/acceptance/W2-116/test_w2_116_reindex.py pass: a model-less re-index of the integration store keeps its index and says the semantic facet is unavailable [Verify clause added, DEC-1157 (12)] |
| S6 | `gov launch` points every worker session's retrieval at the integration store (the `GOV_STORE` of a launched session), not only a designer's; a designer's retrieval never reads a ticket worktree's store. | a launcher unit test per worker role: the session environment names the integration store; a designer's never names a worktree's store [DEC-1087 (3), DEC-963] [added, the CTO's note of 2026-11-06 in the body (S3 widened), DEC-1087 (3)] |
| F1 | A designer's retrieval answered from a ticket worktree's store. | tests/acceptance/W2-116/test_w2_116_launch.py::test_s3_failure1_a_designer_never_reads_the_ticket_worktree_s_own_store passes [Verify clause added, DEC-1157 (12)] |
| F2 | The link switched to a store whose build failed, or a search answered from a half-built store. | the failure-2 cases in test_w2_116_double_buffer.py and test_w2_116_reindex.py pass: a search during a build and through the link while the other half rebuilds is answered from the ready half, never stale; a build killed half way leaves the link [Verify clause added, DEC-1157 (12)] |
| F3 | A re-index that fails leaves the previous index and reports the failure; it never leaves no index [W2-M088]. [moved from W2-06 F1, DEC-1083] | the failure-3 cases in test_w2_116_double_buffer.py and test_w2_116_reindex.py pass: a killed build or a failed re-index leaves the previous index and reports the failure [Verify clause added, DEC-1157 (12)] |
Non-goals (do not build, do not test): none
Done when: the DoD lines DOD-1, DOD-2, DOD-3, DOD-4, DOD-5, DOD-6 hold for your part.

## Inputs
- Sources: DEC-1109, DEC-1112, DEC-983, DEC-982, DEC-963, DEC-966, DEC-1014, DEC-1015, DEC-1083, DEC-1087, DEC-719, DAEO-kia7. Read each by id in /home/usain/Dynamic-Agentic-Engineering-OS/docs/DECISION_REGISTER.md, or ask memory (below).
- What the lead knows of the ground: This is W2-116 (DAEO-f58b) pass 2b, FULL: S2, then the build. Your pass 2 returned PACKAGES (P-W2-116-S2-INTERFACE). The CTO decided all three questions under DEC-1157 (12), committed as 8801ffd17 on w2/integrate:
- **Q1 (a):** your interface, written into the ticket's notes ("S2's interface (pass 2b)").
- **Q2 (b), not (a):** the ticket is widened by `governance/project/rebuild.yaml`. Your engineer adds this repository's `integration_refresh` line with the code that reads it, so no reader meets the key before its code exists.
- **Q3 (a):** the ticket is widened by `src/gov/retrieval/retrieve.py` for R2-F3, plus `tests/unit/status/test_w2_116*` and `tests/unit/retrieval/test_w2_116*`.

Read your lead checkpoint `.gov-runtime/scratch/lead/CHECKPOINT.md` first, then the package `.gov-runtime/scratch/lead/PACKAGE-W2-116-S2-INTERFACE.md` and the ticket.

**The order:**
1. Merge `w2/integrate` into `w2/W2-116`: one command, `--no-ff`, with `Task: DAEO-f58b` and `Role: orchestrator`. Delete pass 1's leftover `w2/W2-116-tests` branch and folder only if they hold nothing unmerged (check with `git branch --no-merged`); otherwise name them in your return.
2. **An independent test designer** (a fresh tests worktree) writes S2's acceptance cases under `tests/acceptance/W2-116/` from the KPI line and the stated interface:
   - a planted config's two times are read;
   - a refresh runs after a newer verdict file, when `latest` passes without one, and at `second`; otherwise it says `not_due`;
   - `gov status`'s `integration_store` part has head, age and a named stale reason;
   - a missing or invalid time refuses `REBUILD_CONFIG_INVALID` naming the key;
   - R2-F3: a continuation token from the other half is refused.
   The clock is planted with `GOV_NOW`. Check red for the stated reasons.
3. **An engineer** builds S2 and R2-F3 inside the paths, and adds `rebuild.yaml`'s `integration_refresh` line with this repository's values, as the ticket states.
4. `gov accept W2-116` on the final head; the scoped run once (DEC-968).
5. **A narrow independent check** (a fresh independent auditor, Opus, high, read-only, carrying JUDGEMENT.md word for word): only pass 2b's change, against S2's line, the stated interface and R2-F3, ending with the verdict block. Commit its record under `docs/probes/DAEO-f58b/`, with `implementer_session`.
6. Return DONE with the head to land and the record, or PACKAGES.

Every pytest, yours and every worker's, through bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh with a TMPDIR outside the repository and outside ~/gov-os-runs, PYTHONUSERBASE=/home/usain/.local, -p no:cacheprovider -o tmp_path_retention_policy=failed. Waits and stops by pid only (`/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/proc.sh wait --max <s> <pid>`); never the Monitor tool, never a name match. A path case of the form "the branch changes only the ticket's allowed_paths" judges only this ticket's branch. If another ticket's case turns red on this branch, name it with file:line; the CTO fixes it under DEC-1156 (7). The three `test_cto_safety_nets.py` live-inbox cases and `test_w2_23_space.py:94` are known reds: name them, never fix them here. A resource gate's refusal is a wait (DEC-1146). Never open the evaluation sets' root or any hidden or memory-verdict folder. No new ticket: a gap comes back as a package. A session refused twice for the same action by the guard, the sandbox or a hook stops and says so, and never works around a refusal (DEC-1142 (9)). If an API error ends a worker, relaunch it once from its checkpoint; if it ends again, return PACKAGES naming it. There is no token cap.
none

## Commands (copy them as they are)
| name | command |
|---|---|
| identity | `printenv GOV_ROLE GOV_TICKET` |
| where | `git -C /home/usain/gov-os-worktrees/W2-116 rev-parse --show-toplevel --abbrev-ref HEAD` |
| retrieve | `gov retrieve --root /home/usain/gov-os-worktrees/W2-00-store "{QUESTION}"` |
| context | `gov context DAEO-f58b --role {WORKER_ROLE}` |
| launch_worker | `bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/launch_worker.sh {WORKER_ROLE} {EFFORT} {BRIEF_FILE}` |
| wait_for | `bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/wait_for.sh {EXIT_FILE}` |
| tests_worktree | `git -C /home/usain/gov-os-worktrees/W2-116 worktree add /home/usain/gov-os-worktrees/W2-116-tests -b w2/W2-116-tests HEAD` |
| merge_tests | `git -C /home/usain/gov-os-worktrees/W2-116 merge --no-ff w2/W2-116-tests -F {MESSAGE_FILE}` |
| accept | `gov accept W2-116 --root /home/usain/gov-os-worktrees/W2-116` |
| rebuild | `env PYTHONPATH=/home/usain/gov-os-worktrees/W2-116/src bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/rebuild_slot.sh /home/usain/gov-os-worktrees/W2-116` |
| lead_verify | `bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/lead_verify.sh /home/usain/gov-os-worktrees/W2-116 W2-116 DAEO-f58b` |
| tests_worktree_remove | `git -C /home/usain/gov-os-worktrees/W2-116 worktree remove /home/usain/gov-os-worktrees/W2-116-tests` |
| links | `gov links --since {BASE}` |
Ask memory first: outside the sandbox gov retrieve --root /home/usain/gov-os-worktrees/W2-00-store "{QUESTION}" "<which decision governs X | where is Y implemented>"; inside it, the Read and Grep tools [DEC-1065]; grep the register only by id.
Search again once: if the bundle does not answer, or your answer may be incomplete, ask once more in your own, different words; then answer from both bundles with path and lines, or say "not found". Two searches in all; never answer beyond what you read.
No `gov retrieve` in the sandbox, and no `gov context`: a launched worker searches with the Read and Grep tools, and searches again once the same way [DEC-1065].
Every whole-folder pytest run adds `-m "not local_only" -k "not real and not green_here and not time_limit"` and an empty `HOME`: run it as env HOME=/home/usain/gov-os-worktrees/W2-116/.gov-runtime/scratch/empty-home PYTHONPATH=/home/usain/gov-os-worktrees/W2-116/src python3 -m pytest {FOLDER} -q -p no:cacheprovider -o tmp_path_retention_policy=failed -m "not local_only" -k "not real and not green_here and not time_limit" [DEC-1065].
Wait for anything long with bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/wait_for.sh {EXIT_FILE}, one call per 9.5 min; never a hand-written sleep loop.
No merge inside the sandbox: the CTO or your lead merges into your branch outside it; a restore or conflict resolution in `tests/acceptance/` is a test designer's [DEC-1052].

## Forms that work (the guard and the harness accept these)
- Write and edit files with the Write and Edit tools and absolute paths.
- Anything longer than one line goes in a script file under /home/usain/gov-os-worktrees/W2-116/.gov-runtime/scratch/, run with `bash <file>` or `python3 <file>`.
- Use literal paths, never a shell variable or `$(…)` as a write target; name the folder a listing or search starts at.
- The harness allows these headless without asking: Bash, Read, Edit, Write, Grep, Glob. For anything else use a script file as above, or report it; never retry another form.

## Commit (your paths only)
```
git commit -m "{SUBJECT}" --trailer "Task: DAEO-f58b" --trailer "Role: orchestrator" --trailer "Implements: DEC-1109, DEC-1112, DEC-983, DEC-982, DEC-963, DEC-966, DEC-1014, DEC-1015, DEC-1083, DEC-1087, DEC-719, DAEO-kia7" -- {COMMIT_PATHS}
```
- `Task:` is the ticket's id (DAEO-f58b, a `DAEO-…` id), never a W2 id [DEC-182].
- `Implements:` lists only ids from the ticket's `sources:`, each ACCEPTED [DEC-927].
- Put an id you need that is not in `sources:` in `discoveries`, never into `Implements:` alone [DEC-1073].
- Cite only ACCEPTED decisions as rules; name a PROPOSED one "proposed", never as the rule [DEC-1073].

## Return (your last message; nothing else is read)
The twelve fields first, each a labelled line ("none" where nothing), then each section below, always present:
```
task: / status: / work_completed: / files_changed: / evidence: / tests: / discoveries: / risks: / lessons: / proposed_decisions: / unresolved: / recommended_next_action:
template: role-lead@1.0.1
commits: <hash12> <subject> | Task/Role/Implements as committed
brief_gaps: none | - <what was missing> | <where it belonged: template, facts, ticket, tool> | <minutes, est.>
guard_refusals: none | - <time> | <the command's form, one line> | <the rule's reason as the hook gave it> | true or false-positive [DEC-958]
```
Refused twice for the same call: stop and say so. Never work around a refusal: report it.

## Your run: build (only this section is in your brief)
**build**: implement and verify.
1. Run the *tests* steps 1 to 3 and, in parallel, the implementer (engineer) from its brief.
2. Merge the tests when the implementer is between batches; write TESTS-READY.
3. Verify: env PYTHONPATH=/home/usain/gov-os-worktrees/W2-116/src bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/rebuild_slot.sh /home/usain/gov-os-worktrees/W2-116, then bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/lead_verify.sh /home/usain/gov-os-worktrees/W2-116 W2-116 DAEO-f58b, then wait. Name a red as known only from /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/skip_known.json; re-run a load-sensitive case alone once.
4. Red: a fresh implementer given the failing output only. Three iterations that do not converge: return ESCALATION [DEC-096].
