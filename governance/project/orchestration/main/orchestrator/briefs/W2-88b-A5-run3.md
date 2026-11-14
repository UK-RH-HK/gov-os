# Your assignment
You are a fresh orchestrator session. Your role's rules are in your system prompt (template `role-lead`); this brief gives this assignment's facts.
Ticket DAEO-aks1 (W2-88b), profile STANDARD. Objective: W2-88b gov adopt's smoke run on copies of two real public repositories, grafana (large) and redis (smaller): where it completes and where it fails; no questions, no measure, no validation. Filed by the owner's decision (DEC-1150 (1), package 1 (a), 2026-11-12), under DEC-996 (1)'s split list: W2-88 mixed three roles (DEC-995). This child holds the research half. It starts after W2-88 lands; it is not on W2-27's dependency chain (W2-27 needs W2-88's tools). If the research wall refuses the copies' folder under ~/gov-os-runs/W2-88b/, that comes back as a package.

## Where you work
| what | path |
|---|---|
| your tree (write here only) | /home/usain/gov-os-worktrees/W2-88b |
| branch | w2/W2-88b |
| allowed paths | experiments/W2-88/** |
| ticket file (read-only) | /home/usain/Dynamic-Agentic-Engineering-OS/.tickets/DAEO-aks1.md |
| your scratch | /home/usain/gov-os-worktrees/W2-88b/.gov-runtime/scratch/ |

## What must be true (KPI lines and how each is checked)
| id | line | verify |
|---|---|---|
| S1 | S1 The copies: grafana/grafana (large: Go and TypeScript, of the order of 10^4 tracked files) and redis/redis (smaller: C, with its vendored deps/), each cloned by the lead or the CTO (network) under ~/gov-os-runs/W2-88b/<name>/, pinned to a commit, its licence recorded, never committed to this repository and never pushed anywhere. | experiments/W2-88/smoke-run.md has one section per repository naming its clone path under ~/gov-os-runs/W2-88b/, its commit (40 hex), its tracked-file count and its licence; `git -C ~/gov-os-runs/W2-88b/<name> rev-parse HEAD` prints the recorded commit; a search of this repository's tracked files and history for the clones' paths finds nothing [DEC-1176 (2), DEC-1150 (1)] [changed, DEC-1176 (2)] |
| S2 | S2 gov adopt run on each copy, every stage recorded: `gov adopt --lite --stage MA` (the memory assessment and the refactoring plan), then A0 to A9 in `project.STAGES` order (A0, A1, A2, A3, A4, A5, A6, A8, A9), A9 being the memory build (the full index, the embeddings, the record, lexical, vector and code-graph stores), run with no `--questions`. For each repository and each stage the record names the exact command, its exit code, its wall-clock time (start and end) and the peak RSS where gov prints it, and the outcome: completed, or failed. | each repository's section holds one row per stage MA, A0, A1, A2, A3, A4, A5, A6, A8 and A9, each with its command, exit code, start and end time and outcome (completed, failed or not reached); each recorded exit code equals the one in that stage's log under ~/gov-os-runs/W2-88b/<name>-logs/; no recorded command carries `--questions` [DEC-1176 (2)] [changed, DEC-1176 (2)] |
| S3 | S3 Where and how it fails: a stage that fails is recorded with the stage, the command, its exit code, the refusal code gov printed, the error's text (its first lines, with any secret value left out), the time it ran for, and the file or path the error names when it names one; the stages after it on that copy are marked not reached, naming the failing stage. A failure is a finding to record, never a reason to stop the other repository: the other copy's run starts and goes on. A wait by the resource gate or the rebuild lock is a wait, recorded with its length, not a failure. Each failure is returned in the lead's return as a finding for the owner (a candidate row or package), never fixed in this ticket. | every stage row whose exit code is not 0 has a findings entry naming the stage, the command, the exit code, the refusal code and the error text; every stage after it on that copy is marked not reached with the failing stage named; both sections hold an MA row whatever the other repository's outcome; `git diff --name-only` of the ticket's branch lists no path outside experiments/W2-88/ [DEC-1176 (2)] [changed, DEC-1176 (2)] |
| S4 | S4 A5 on a copy: A5's verdict on each copy's path map is given by a fresh independent-auditor session started by the lead or the CTO, committed in that copy with its Role trailer, as the product's own gate requires; it judges the path map only, never memory, and it is part of running gov adopt, not a validation of the result. | each copy's A5 row names the verdict file, its commit in the copy and the auditor session id, which differs from every session that ran a stage; a copy with no verdict has A5 recorded as failed with its refusal code (NO_VERDICT) and A6 to A9 as not reached [DEC-1176 (3)] [added, DEC-1176 (3)] |
| S5 | S5 No questions, no measure, no validation: the record states that the smoke run tests only whether gov adopt works on repositories different from this one, small and large, and where it fails; it holds no question set and no quality figure, and draws no conclusion on memory's quality. A9's own `measure` block (which says that no question set was given) and its `scale` block stay in A9's record in the copy and are not copied into the record as results. | the record holds the sentence "No questions, no measure, no validation."; a case-insensitive grep of the record for `hit@5`, `hit_at_5`, `right_e2e`, `right end to end`, `wrong claim`, `wrong_claims`, `MRR`, `recall`, `accuracy`, `query_ms` and `vector_scan_ms` finds nothing [DEC-1176 (1), (2)] [changed, DEC-1176 (2)] |
| F1 | A clone of a GitHub repository, or any of its files, in this repository or in a commit of it; a clone outside ~/gov-os-runs/W2-88b/; any clone, read or write of the workbench (~/gov-os-workbench), ~/workspace, EXAMIN's real repository or the held-out qualification material. | `git ls-files` and the branch's history hold no path of a clone; each clone's folder is under ~/gov-os-runs/W2-88b/; no recorded command and no log under ~/gov-os-runs/W2-88b/ names a path under ~/gov-os-workbench/, ~/workspace or ~/EXAMIN APP [DEC-1176 (2), DEC-1150 (1), DEC-728] [changed, DEC-1176 (2)] |
| F2 | Anything written outside the copies and the record: every stage works on the copies only, never on an original. | every path the run wrote is under ~/gov-os-runs/W2-88b/ or experiments/W2-88/; `git status` of this repository after the run lists changes under experiments/W2-88/ only [DEC-1150 (1), DEC-1176 (2)] [changed, DEC-1176 (2)] |
| F3 | A secret's value in the record, a log quoted in it or the lead's return; a question set, a quality figure or a claim that memory works, is measured or is proven on either repository. | the record names the assessment's secrets by path and rule id only, and a secrets scan (gitleaks, `--no-git`) of experiments/W2-88/smoke-run.md finds nothing; S5's grep finds nothing [DEC-1176 (1), (2)] [added, DEC-1176 (2)] |
Non-goals (do not build, do not test): any question set, measure, bar or validation of memory's quality on these repositories: memory is built and measured per repository in its own Wave 0, on its own hidden questions (DEC-1176 (1)); clones or reads of the workbench (ORION, ARGUS, ARGUS's stress tier, EXAMIN's copy) and of ~/workspace (DEC-1176 (2)); fixing a failure the smoke run finds: each is a finding for the owner; the code (W2-88), the skill text (W2-88a), the synthetic repositories (W2-88's proof (a)), EXAMIN's copy (W2-27)
Done when: the DoD lines DOD-1, DOD-2, DOD-3, DOD-4, DOD-5, DOD-6 hold for your part.

## Inputs
- Sources: DEC-1176, DEC-1150, DEC-996, DEC-954, DEC-1099, DEC-728. Read each by id in /home/usain/Dynamic-Agentic-Engineering-OS/docs/DECISION_REGISTER.md, or ask memory (below).
- What the lead knows of the ground: This is W2-88b (DAEO-aks1), run 3: the smoke run. Your earlier run was stopped by the CTO on the owner's scope change. DEC-1176 is now recorded (e3c94cd77), and the ticket is re-scoped. Read the ticket in full: its new KPI lines S1 to S5 and F1 to F3, the Verify clauses, the lines "Removed by DEC-1176 (2)", and the non-goals. Read DEC-1176 in docs/DECISION_REGISTER.md. Your earlier scratch work stands where it fits, including the GitHub clones if they are still under `~/gov-os-runs/W2-88b/`.

**The purpose, in the owner's words:** "its only purpose is to test whether gov adopt works on repositories different from ours, small and large, and where it fails. No measuring and no validation."

**The order:**
1. **A research worker** runs `gov adopt` on copies of grafana (large) and redis (smaller) under `~/gov-os-runs/W2-88b/`.
   - It takes them through the stages MA, A0 to A6, A8 and A9, with A9 run without `--questions`.
   - The work is the assessment, the index, the embeddings and the stores.
   - Indexing and embeddings take a heavy slot; a resource gate's refusal is a wait, never a failure.
2. **A5 on each copy (DEC-1176 (3) (a)):**
   - When a copy reaches A5, launch a fresh independent auditor on it (Opus, high, read-only, a session that ran no stage).
   - It judges that copy's path map only, never memory, and commits its verdict there with `Role: independent-auditor` alone.
   - The gate needs that trailer (`src/gov/adopt/stages.py:432-461`).
3. **The record:** `experiments/W2-88/smoke-run.md`.
   - For each repository and each stage, it says whether the stage completed, or where and how it failed: the command, exit code, refusal code, error and time.
   - A failure is a finding to record and return. It never stops the other repository and is never fixed here.
   - No questions, no measure, no validation of quality.
   - `~/workspace`, the workbench and the owner's repositories are neither cloned, read nor written.
4. **A narrow independent check** that the record holds every stage's outcome for both repositories and claims no measure:
   - a fresh independent auditor, Opus, high, read-only, carrying JUDGEMENT.md word for word, ending with the verdict block;
   - its record goes under `docs/probes/DAEO-aks1/`, with `implementer_session` and `probed_commit` in full; quote any front-matter value that holds `: `.
5. Return DONE with the head and the list of failures found, or PACKAGES.

Every commit's trailers go in one final paragraph. Never commit a merge with conflict markers (DEC-1175 (4)). Workers use the sandbox's own `$TMPDIR`. Every pytest through bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh, PYTHONUSERBASE=/home/usain/.local. Waits and stops by pid only (`/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/proc.sh wait --max <s> <pid>`); never the Monitor tool, never a name match. Never open the evaluation sets' root, the workbench, EXAMIN's real repository, or any hidden or memory-verdict folder. No new ticket: a gap comes back as a package. A session refused twice for the same action by the guard, the sandbox or a hook stops and says so, and never works around a refusal (DEC-1142 (9)). If an API error ends a worker, relaunch it once from its checkpoint; if it ends again, return PACKAGES naming it. There is no token cap.
none

## Commands (copy them as they are)
| name | command |
|---|---|
| identity | `printenv GOV_ROLE GOV_TICKET` |
| where | `git -C /home/usain/gov-os-worktrees/W2-88b rev-parse --show-toplevel --abbrev-ref HEAD` |
| retrieve | `gov retrieve --root /home/usain/gov-os-worktrees/W2-00-store "{QUESTION}"` |
| context | `gov context DAEO-aks1 --role {WORKER_ROLE}` |
| launch_worker | `bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/launch_worker.sh {WORKER_ROLE} {EFFORT} {BRIEF_FILE}` |
| wait_for | `bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/wait_for.sh {EXIT_FILE}` |
| tests_worktree | `git -C /home/usain/gov-os-worktrees/W2-88b worktree add /home/usain/gov-os-worktrees/W2-88b-tests -b w2/W2-88b-tests HEAD` |
| merge_tests | `git -C /home/usain/gov-os-worktrees/W2-88b merge --no-ff w2/W2-88b-tests -F {MESSAGE_FILE}` |
| accept | `gov accept W2-88b --root /home/usain/gov-os-worktrees/W2-88b` |
| rebuild | `env PYTHONPATH=/home/usain/gov-os-worktrees/W2-88b/src bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/rebuild_slot.sh /home/usain/gov-os-worktrees/W2-88b` |
| lead_verify | `bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/lead_verify.sh /home/usain/gov-os-worktrees/W2-88b W2-88b DAEO-aks1` |
| tests_worktree_remove | `git -C /home/usain/gov-os-worktrees/W2-88b worktree remove /home/usain/gov-os-worktrees/W2-88b-tests` |
| links | `gov links --since {BASE}` |
Ask memory first: outside the sandbox gov retrieve --root /home/usain/gov-os-worktrees/W2-00-store "{QUESTION}" "<which decision governs X | where is Y implemented>"; inside it, the Read and Grep tools [DEC-1065]; grep the register only by id.
Search again once: if the bundle does not answer, or your answer may be incomplete, ask once more in your own, different words; then answer from both bundles with path and lines, or say "not found". Two searches in all; never answer beyond what you read.
No `gov retrieve` in the sandbox, and no `gov context`: a launched worker searches with the Read and Grep tools, and searches again once the same way [DEC-1065].
Every whole-folder pytest run adds `-m "not local_only" -k "not real and not green_here and not time_limit"` and an empty `HOME`: run it as env HOME=/home/usain/gov-os-worktrees/W2-88b/.gov-runtime/scratch/empty-home PYTHONPATH=/home/usain/gov-os-worktrees/W2-88b/src python3 -m pytest {FOLDER} -q -p no:cacheprovider -o tmp_path_retention_policy=failed -m "not local_only" -k "not real and not green_here and not time_limit" [DEC-1065].
Wait for anything long with bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/wait_for.sh {EXIT_FILE}, one call per 9.5 min; never a hand-written sleep loop.
No merge inside the sandbox: the CTO or your lead merges into your branch outside it; a restore or conflict resolution in `tests/acceptance/` is a test designer's [DEC-1052].

## Forms that work (the guard and the harness accept these)
- Write and edit files with the Write and Edit tools and absolute paths.
- Anything longer than one line goes in a script file under /home/usain/gov-os-worktrees/W2-88b/.gov-runtime/scratch/, run with `bash <file>` or `python3 <file>`.
- Use literal paths, never a shell variable or `$(…)` as a write target; name the folder a listing or search starts at.
- The harness allows these headless without asking: Bash, Read, Edit, Write, Grep, Glob. For anything else use a script file as above, or report it; never retry another form.

## Commit (your paths only)
```
git commit -m "{SUBJECT}" --trailer "Task: DAEO-aks1" --trailer "Role: orchestrator" --trailer "Implements: DEC-1176, DEC-1150, DEC-996, DEC-954, DEC-1099, DEC-728" -- {COMMIT_PATHS}
```
- `Task:` is the ticket's id (DAEO-aks1, a `DAEO-…` id), never a W2 id [DEC-182].
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
1. Run the *tests* steps 1 to 3 and, in parallel, the implementer (research) from its brief.
2. Merge the tests when the implementer is between batches; write TESTS-READY.
3. Verify: env PYTHONPATH=/home/usain/gov-os-worktrees/W2-88b/src bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/rebuild_slot.sh /home/usain/gov-os-worktrees/W2-88b, then bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/lead_verify.sh /home/usain/gov-os-worktrees/W2-88b W2-88b DAEO-aks1, then wait. Name a red as known only from /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/skip_known.json; re-run a load-sensitive case alone once.
4. Red: a fresh implementer given the failing output only. Three iterations that do not converge: return ESCALATION [DEC-096].
