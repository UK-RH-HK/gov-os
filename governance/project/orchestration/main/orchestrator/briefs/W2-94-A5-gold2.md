# Your assignment
You are a fresh orchestrator session. Your role's rules are in your system prompt (template `role-lead`); this brief gives this assignment's facts.
Ticket DAEO-g87r (W2-94), profile STANDARD. Objective: EXAMIN's question set: memory questions with gold sources about the owner's copy, a visible and a hidden half, by a session independent of the adopting team, before W2-27. Card: MEMORY-SPEC-MAP gap 7, resolved by the owner in DEC-957; W2-61's KPI 6 moves here. The set measures memory on EXAMIN's copy at W2-27 (with W2-88's tools) and W2-15b.

## Where you work
| what | path |
|---|---|
| your tree (write here only) | /home/usain/gov-os-worktrees/W2-94 |
| branch | w2/W2-94 |
| allowed paths | tests/acceptance/W2-94/**, fixtures/evaluation/examin/check_gold.py, docs/probes/DAEO-g87r/**, fixtures/evaluation/examin/visible/**, fixtures/evaluation/examin/hidden/** |
| ticket file (read-only) | /home/usain/Dynamic-Agentic-Engineering-OS/.tickets/DAEO-g87r.md |
| your scratch | /home/usain/gov-os-worktrees/W2-94/.gov-runtime/scratch/ |

## What must be true (KPI lines and how each is checked)
| id | line | verify |
|---|---|---|
| S1 | Between 10 and 20 questions about EXAMIN's code and governance, each with its gold answer and the source or sources an answer must cite (file and section or line), in the form W2-61's visible half takes; after writing, a recorded seeded draw, stratified by category, splits the set into a development half (`hidden/visible/`) and a hidden half, both written by the walled writer inside the hidden folder; the owner's release step (`release_visible.sh`) then copies the development half into `visible/` | a planted stand-in set: a count outside 10 to 20 is refused; the record holds the seed and the draw; the two halves each hold half (within one) with each category in both halves; the release step copies exactly the development half into `visible/` and refuses a second release [DEC-957, DEC-828 items 3 and 4, DEC-954 Q9f] |
| S2 | Written by the walled writer from the wall's tree, `git archive` of the CTO's launch clone of the owner's copy, made by exact path under ~/gov-os-runs/W2-94/examin/ with one scaffold commit (the walls' template files, `COPY-HEAD.txt`, a path map holding only `sets_root_hidden`, the brief); the copy is only read by that clone; nothing written in the workbench or in EXAMIN's real repository | the record names the clone's path under `~/gov-os-runs/W2-94/examin/` and `COPY-HEAD.txt` names the copy's commit; after the run `git status` in the workbench and in EXAMIN's real repository shows no change, and the owner's copy's file times are unchanged [DEC-723, DEC-728] |
| S3 | Written by the walled writer session (the approved brief `governance/project/indep-briefs/examin-sets/EXAMIN-writer.md`; no shell or network; counts only returned), independent of the adopting team: no session of W2-26, W2-27, W2-88 or a retrieval ticket writes or reads the hidden half; nothing hidden quoted in a commit message, a return, a log or a ticket note | the walls' launch log names the approved brief's sha256; the guard's log shows no session of W2-26, W2-27, W2-88 or a retrieval ticket opened the hidden folder; a grep of commit messages, return, log and ticket notes for a planted unique question word finds 0 hits [DEC-820 (d), DEC-845] |
| S4 | Every gold source exists at the copy's recorded commit and holds the answer | a counts-only script, written by the ticket's independent test designer and run by the CTO with `--sets-root` (the writer has no shell), prints only counts and ids: for each question, its gold source exists at the copy's recorded commit and holds the answer ("n of n hold"); a planted source that is absent or does not hold its answer is reported by id [DEC-828 item 4] |
| S5 | W2-61's KPI 6 ("the same split for EXAMIN's set") is met by this ticket; W2-61's close record names it as moved here | a grep of W2-61's close record finds KPI 6 named as moved to W2-94; this ticket's visible and hidden folders hold the split of S1 [DEC-954, DEC-957] |
| F1 | A hidden question or answer readable by a measured session by a route an honest agent takes in ordinary work. | a planted stand-in hidden file: a read, a grep and a `git log` from a measured session's sandbox (the guard's path map) are refused or find it 0 times |
| F2 | A write in the workbench, the owner's copy or EXAMIN's real repository; a clone outside ~/gov-os-runs/W2-94/. | `git status` in the workbench, the owner's copy and EXAMIN's real repository shows no change after the run; a `find` for a clone of the copy outside `~/gov-os-runs/W2-94/` finds none |
| F3 | A gold source that does not hold its answer. | the S4 script on a planted source that does not hold its answer reports that question's id as failing |
Non-goals (do not build, do not test): none
Done when: the DoD lines DOD-1, DOD-2, DOD-3, DOD-4, DOD-5, DOD-6 hold for your part.

## Inputs
- Sources: DEC-957, DEC-954, DEC-828, DEC-820, DEC-845, DEC-723, DEC-728. Read each by id in /home/usain/Dynamic-Agentic-Engineering-OS/docs/DECISION_REGISTER.md, or ask memory (below).
- What the lead knows of the ground: This is W2-94 (DAEO-g87r), the GOLD change, resumed after your PACKAGES (P-W2-94-GOLD-2). Read your lead checkpoint first. td-3's 34 cases and the guard case (133b79626, merged 95ac3ec04) stand: 29 red against the unchanged check, the guards green.

**The CTO's answer: P-W2-94-GOLD-2 (A).** The ticket's role is now `engineer` (db09788ff on w2/integrate; it was `independent-auditor`, for the walled writers' delivery, which is done). The launcher therefore lets you launch the engineer the owner's GOLD (a) names.

**The order:**
1. Merge `w2/integrate` into `w2/W2-94` to bring the ticket: one command, `--no-ff`, with `Task: DAEO-g87r` and `Role: orchestrator`. Never commit a merge with conflict markers.
2. **A fresh engineer** from your ready brief `briefs/en-1.md`: `fixtures/evaluation/examin/check_gold.py` only, to turn td-3's 29 cases green with the guard cases still green. Nothing else changes.
3. `gov accept W2-94`, then the scoped run once (DEC-968).
4. **A narrow independent check** (a fresh independent auditor, Opus, high, read-only, carrying JUDGEMENT.md word for word):
   - It checks only the check's change, against the GOLD brief's (i) to (iii) and the guard cases.
   - It ends with the verdict block.
   - Its record goes under `docs/probes/DAEO-g87r/`, with `implementer_session` and `probed_commit` in full; any front-matter value holding `: ` is quoted.
   - Every commit's trailers go in one final paragraph.
5. Return DONE with the head. The owner's operator then re-runs `check_gold.py` on the real delivery (expected 19 of 20, draw ok, q02 the only FAIL).

Never open the evaluation sets' root or any hidden folder. Workers use the sandbox's own `$TMPDIR`. Every pytest, yours and every worker's, through bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh, PYTHONUSERBASE=/home/usain/.local, -p no:cacheprovider -o tmp_path_retention_policy=failed. Waits and stops by pid only (`/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/proc.sh wait --max <s> <pid>`); never the Monitor tool, never a name match. If another ticket's case turns red on this branch, name it with file:line; the CTO fixes it under DEC-1156 (7). Known reds: `test_w2_23_space.py:94` and the three `test_cto_safety_nets.py` live-inbox cases. A resource gate's refusal is a wait (DEC-1146). No new ticket: a gap comes back as a package. A session refused twice for the same action by the guard, the sandbox or a hook stops and says so, and never works around a refusal (DEC-1142 (9)). If an API error ends a worker, relaunch it once from its checkpoint; if it ends again, return PACKAGES naming it. There is no token cap.
none

## Commands (copy them as they are)
| name | command |
|---|---|
| identity | `printenv GOV_ROLE GOV_TICKET` |
| where | `git -C /home/usain/gov-os-worktrees/W2-94 rev-parse --show-toplevel --abbrev-ref HEAD` |
| retrieve | `gov retrieve --root /home/usain/gov-os-worktrees/W2-00-store "{QUESTION}"` |
| context | `gov context DAEO-g87r --role {WORKER_ROLE}` |
| launch_worker | `bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/launch_worker.sh {WORKER_ROLE} {EFFORT} {BRIEF_FILE}` |
| wait_for | `bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/wait_for.sh {EXIT_FILE}` |
| tests_worktree | `git -C /home/usain/gov-os-worktrees/W2-94 worktree add /home/usain/gov-os-worktrees/W2-94-tests -b w2/W2-94-tests HEAD` |
| merge_tests | `git -C /home/usain/gov-os-worktrees/W2-94 merge --no-ff w2/W2-94-tests -F {MESSAGE_FILE}` |
| accept | `gov accept W2-94 --root /home/usain/gov-os-worktrees/W2-94` |
| rebuild | `env PYTHONPATH=/home/usain/gov-os-worktrees/W2-94/src bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/rebuild_slot.sh /home/usain/gov-os-worktrees/W2-94` |
| lead_verify | `bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/lead_verify.sh /home/usain/gov-os-worktrees/W2-94 W2-94 DAEO-g87r` |
| tests_worktree_remove | `git -C /home/usain/gov-os-worktrees/W2-94 worktree remove /home/usain/gov-os-worktrees/W2-94-tests` |
| links | `gov links --since {BASE}` |
Ask memory first: outside the sandbox gov retrieve --root /home/usain/gov-os-worktrees/W2-00-store "{QUESTION}" "<which decision governs X | where is Y implemented>"; inside it, the Read and Grep tools [DEC-1065]; grep the register only by id.
Search again once: if the bundle does not answer, or your answer may be incomplete, ask once more in your own, different words; then answer from both bundles with path and lines, or say "not found". Two searches in all; never answer beyond what you read.
No `gov retrieve` in the sandbox, and no `gov context`: a launched worker searches with the Read and Grep tools, and searches again once the same way [DEC-1065].
Every whole-folder pytest run adds `-m "not local_only" -k "not real and not green_here and not time_limit"` and an empty `HOME`: run it as env HOME=/home/usain/gov-os-worktrees/W2-94/.gov-runtime/scratch/empty-home PYTHONPATH=/home/usain/gov-os-worktrees/W2-94/src python3 -m pytest {FOLDER} -q -p no:cacheprovider -o tmp_path_retention_policy=failed -m "not local_only" -k "not real and not green_here and not time_limit" [DEC-1065].
Wait for anything long with bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/wait_for.sh {EXIT_FILE}, one call per 9.5 min; never a hand-written sleep loop.
No merge inside the sandbox: the CTO or your lead merges into your branch outside it; a restore or conflict resolution in `tests/acceptance/` is a test designer's [DEC-1052].

## Forms that work (the guard and the harness accept these)
- Write and edit files with the Write and Edit tools and absolute paths.
- Anything longer than one line goes in a script file under /home/usain/gov-os-worktrees/W2-94/.gov-runtime/scratch/, run with `bash <file>` or `python3 <file>`.
- Use literal paths, never a shell variable or `$(…)` as a write target; name the folder a listing or search starts at.
- The harness allows these headless without asking: Bash, Read, Edit, Write, Grep, Glob. For anything else use a script file as above, or report it; never retry another form.

## Commit (your paths only)
```
git commit -m "{SUBJECT}" --trailer "Task: DAEO-g87r" --trailer "Role: orchestrator" --trailer "Implements: DEC-957, DEC-954, DEC-828, DEC-820, DEC-845, DEC-723, DEC-728" -- {COMMIT_PATHS}
```
- `Task:` is the ticket's id (DAEO-g87r, a `DAEO-…` id), never a W2 id [DEC-182].
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
3. Verify: env PYTHONPATH=/home/usain/gov-os-worktrees/W2-94/src bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/rebuild_slot.sh /home/usain/gov-os-worktrees/W2-94, then bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/lead_verify.sh /home/usain/gov-os-worktrees/W2-94 W2-94 DAEO-g87r, then wait. Name a red as known only from /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/skip_known.json; re-run a load-sensitive case alone once.
4. Red: a fresh implementer given the failing output only. Three iterations that do not converge: return ESCALATION [DEC-096].
