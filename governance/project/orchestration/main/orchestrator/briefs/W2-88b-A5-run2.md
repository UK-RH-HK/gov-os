# Your assignment
You are a fresh orchestrator session. Your role's rules are in your system prompt (template `role-lead`); this brief gives this assignment's facts.
Ticket DAEO-aks1 (W2-88b), profile STANDARD. Objective: W2-88b W2-88's proofs on real repositories: two public GitHub repositories and the register's test repositories, on copies only. Filed by the owner's decision (DEC-1150 (1), package 1 (a), 2026-11-12), under DEC-996 (1)'s split list: W2-88 mixed three roles (DEC-995). This child holds the research half: proofs (b) and (c) moved word for word, the proof record (its path moved to `experiments/W2-88/any-repository.md`, the one folder a research worker writes), and the scale and measure lines for the real repositories. The owner added: proof (c) works on copies only; nothing is written in ~/workspace or in any of the owner's own repositories. It starts after W2-88 lands; it is not on W2-27's dependency chain (W2-27 needs W2-88's tools). If the research wall refuses the clones' folder under ~/gov-os-runs/W2-88/, that comes back as a package.

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
| S1 | The proofs, recorded in experiments/W2-88/any-repository.md, each with its commit, size, the assessment, the plan's proposals (count and kinds), the per-store figures and the measure: | experiments/W2-88/any-repository.md holds one section per proof, (b) and (c), and each names its commit, size, the assessment, the plan's proposals (count and kinds), the per-store figures and the measure; a grep for any of those fields missing from a section finds none |
| S2 | (b) two real, messy, public GitHub repositories of different languages and sizes. Candidates for the test designer or the owner to confirm, each pinned to a commit: a large polyglot monorepo with generated code and large fixtures (for example grafana/grafana, Go and TypeScript, of the order of 10^4 files), and a mid-size repository of another language with vendored dependencies in its tree (for example redis/redis, C, with deps/). They are cloned by the lead or the CTO (network) under ~/gov-os-runs/W2-88/github/<name>/, with their licence recorded, never committed and never pushed anywhere. They report data under "Memory works there" and neither runs the full practice: the practice's first full run (S12 to S14) is EXAMIN's copy at W2-27, with no separate proof repository; what goes wrong there is fixed in the practice, and the repositories adopted after EXAMIN follow the practice as fixed. | the proof record has a section for each of two public repositories of different languages, each pinned to a commit with its licence recorded and its data under "Memory works there"; the clones are under ~/gov-os-runs/W2-88/github/<name>/ and a search of this repository's tracked files and history for the clones' paths finds nothing; the record states that neither runs the full practice (S12 to S14) [DEC-954 Q9f, DEC-1099 (2)] [changed, DEC-1099 (2)] |
| S3 | (c) the test repositories the register names, each read through a clone under ~/gov-os-runs/W2-88/: ~/workspace (DEC-078, DEC-718: 77,346 nodes and 270,647 edges, 2.2 GB peak, the envelope's top); the dev tiers ~/gov-os-workbench/synthetic/a-dev (ORION) and b-dev (ARGUS) (DEC-071, DEC-630); ARGUS's stress tier (DEC-071: 5,355 files, 57,777 chunks) only if it lies outside the held-out qualification material; the assessment step only, never an adoption, on a clone of EXAMIN's copy ~/gov-os-workbench/examin/ (DEC-723), to feed W2-27. | the proof record has a section for each named test repository it used, each read through a clone under ~/gov-os-runs/W2-88/; the EXAMIN copy's section holds the assessment record only and no adoption record; a grep of the record for ARGUS's stress tier finds it only with its location outside the held-out qualification material stated [DEC-954 Q9f] |
| S4 | Scale: on each real proof repository ((b) and (c)) the stage records the query time of one plain question on each route, and the vector scan's time against the retrieve budget. A figure over the budget or over DEC-078's envelope is recorded with the measure, and returned as a proposal (a CIT-P or a ticket) for the owner, never a silent change of the store. | on each proof repository the record holds the query time of one plain question on each route and the vector scan's time against the retrieve budget; a planted figure over the budget is recorded with the measure and a proposal file (a CIT-P or a ticket) is written for the owner, and the store's files are byte-identical before and after [DEC-954 Q9f, DEC-078, CAP-19] |
| S5 | Memory works there, measured: on each real proof repository ((b) and (c)) after A9, its questions are run end to end with the standard (S10, S15) and with W2-61's measure, and right end to end, wrong claims and hit@5 are reported. W2-81's per-repository sets apply to the synthetic repositories, and 10 questions written under the rubric by the independent writer and checker (S12) apply to each real repository; these figures are data, set no bar, and a shortfall is a named residual with its cause (DEC-954 Q9e). No proof repository here runs the full practice (S12 to S14): its first full run is EXAMIN's copy at W2-27 (proof (d)), with no separate proof repository. | on each proof repository after A9 the record holds the right-end-to-end, wrong-claim and hit@5 figures from the run with the standard (S10, S15) and W2-61's measure; each real repository has its 10 questions with the writer's and checker's records; a planted low figure does not make the stage not ok (no bar) and appears as a named residual with its cause; the record names no proof repository as having run S12 to S14 [DEC-1099 (2), DEC-1098 (1), DEC-1097 (1)(d), DEC-833, DEC-860, CAP-10] [changed, DEC-1099 (2)] |
| F1 | A clone of a GitHub repository, or any of its files, in this repository or in a commit; a clone outside ~/gov-os-runs/W2-88/; a write in the workbench, EXAMIN's real repository or the held-out qualification material. | `git ls-files` and the branch's history hold no path of a clone; each clone's folder is under ~/gov-os-runs/W2-88/; the modification times of the workbench, EXAMIN's real repository and the qualification material are unchanged after the run |
| F2 | Anything written in ~/workspace or in any of the owner's own repositories: every proof works on copies only (clones under ~/gov-os-runs/W2-88/), never on the original | the modification times and `git status` of ~/workspace and of each original the proofs read are unchanged after the run; every path the run wrote is under ~/gov-os-runs/W2-88/ or experiments/W2-88/ [DEC-1150 (1), DEC-723] |
Non-goals (do not build, do not test): the code (W2-88), the skill text (W2-88a), the synthetic repositories (W2-88's proof (a)), EXAMIN's copy (W2-27, proof (d))
Done when: the DoD lines DOD-1, DOD-2, DOD-3, DOD-4, DOD-5, DOD-6 hold for your part.

## Inputs
- Sources: DEC-1150, DEC-996, DEC-954, DEC-1099, DEC-078, DEC-718, DEC-723. Read each by id in /home/usain/Dynamic-Agentic-Engineering-OS/docs/DECISION_REGISTER.md, or ask memory (below).
- What the lead knows of the ground: This is W2-88b (DAEO-aks1), run 2, resumed after your LAUNCH_BLOCKED return. Read your lead checkpoint first; its NEXT line launches rs-1.

**The CTO's answers:**
- **P1 (a):** done (c0cfe3099). The ticket's list items carry no inline comment, so `allowed_paths` is exactly `experiments/W2-88/**` and the launcher's experiment-folder rule (DEC-242) holds.
- **P2 (a)** (the CTO under DEC-1156 (7)): the clones go under `~/gov-os-runs/W2-88b/{github,workspace,workbench}/<name>/`. Where S2, S3, F1 and F2 name `~/gov-os-runs/W2-88/`, read `~/gov-os-runs/W2-88b/`. The record states the path and the reason (the ticket's body says so).
- **P3 and P4 go to the owner** (the operator's workbench clones; the independent writer's and checker's questions for each real repository). Do not wait for them. Run every part that needs neither, and leave a clear, named gap for the rest. The CTO tells you when the operator's clones and questions arrive.

**The order:**
1. Launch **rs-1** (the research worker, `--class C2`, its model as the ticket class sets it).
   - It clones the two GitHub repositories and `~/workspace` (`--no-hardlinks`) into `~/gov-os-runs/W2-88b/`, keeping the F2 snapshot rule for `~/workspace` (reads only, no writes there).
   - It runs MA (the assessment), with its time estimate first.
   - It then runs A9 with the real embedder, without questions for now: S5's measure stays named as waiting on P4.
   - Indexing and embedding take a heavy slot like a test run (DEC-1001 (d)).
2. The record goes into `experiments/W2-88/` with the data each KPI line asks for. S3's workbench repositories and S5's measures are marked as waiting on P3 and P4.
3. **A narrow independent check** of what is done:
   - A fresh independent auditor (Opus, high, read-only, carrying JUDGEMENT.md word for word) checks it against the KPI lines it covers and ends with the verdict block.
   - Its record goes under `docs/probes/DAEO-aks1/`, with `implementer_session` and `probed_commit` in full; quote any front-matter value that holds `: `.
4. Return PACKAGES with the head, and the record so far, while P3 or P4 are open, or DONE if the owner has accepted them as residuals by then.

Every commit's trailers go in one final paragraph. Never commit a merge with conflict markers (DEC-1173 (1)). Workers use the sandbox's own `$TMPDIR`. Every pytest through bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh, PYTHONUSERBASE=/home/usain/.local. Waits and stops by pid only (`/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/proc.sh wait --max <s> <pid>`); never the Monitor tool, never a name match. A resource gate's refusal is a wait (DEC-1146). Never open the evaluation sets' root, the workbench, EXAMIN's real repository, or any hidden or memory-verdict folder. No new ticket: a gap comes back as a package. A session refused twice for the same action by the guard, the sandbox or a hook stops and says so, and never works around a refusal (DEC-1142 (9)). If an API error ends a worker, relaunch it once from its checkpoint; if it ends again, return PACKAGES naming it. There is no token cap.
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
git commit -m "{SUBJECT}" --trailer "Task: DAEO-aks1" --trailer "Role: orchestrator" --trailer "Implements: DEC-1150, DEC-996, DEC-954, DEC-1099, DEC-078, DEC-718, DEC-723" -- {COMMIT_PATHS}
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
