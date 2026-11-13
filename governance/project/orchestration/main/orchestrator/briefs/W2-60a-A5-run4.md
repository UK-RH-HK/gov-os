# Your assignment
You are a fresh orchestrator session. Your role's rules are in your system prompt (template `role-lead`); this brief gives this assignment's facts.
Ticket DAEO-cv58 (W2-60a), profile FULL. Objective: The role, its skills and its model and effort loaded at launch; the launch record. Card: the draft card `W2-60` (W2-60a part), from the accepted plan (`docs/plan/WAVE_2_REVISED_PLAN.md` §4.3, §2 row 5 and the CAP-35.c and CAP-36.a lite rows; DEC-826 Q1 and Q5, DEC-838, DEC-839); keystone 3, agents know what to do. Started now by the re-plan the owner accepted on 2026-10-29 (DEC-941), beside the memory work.

## Where you work
| what | path |
|---|---|
| your tree (write here only) | /home/usain/gov-os-worktrees/W2-60a |
| branch | w2/W2-60a |
| allowed paths | src/gov/launch/launcher.py, src/gov/launch/role.py, src/gov/launch/record.py, src/gov/launch/criticality.py, governance/project/criticality.yaml, tests/unit/launch/test_role*, tests/unit/launch/test_launch_record*, tests/unit/launch/test_runs.py, tests/unit/launch/test_w1_28.py, tests/unit/launch/test_w1_32.py, docs/changes/W2-60a-CIT-E.md, docs/research/W2-60-rules-probe.md |
| ticket file (read-only) | /home/usain/Dynamic-Agentic-Engineering-OS/.tickets/DAEO-cv58.md |
| your scratch | /home/usain/gov-os-worktrees/W2-60a/.gov-runtime/scratch/ |

## What must be true (KPI lines and how each is checked)
| id | line | verify |
|---|---|---|
| S1 | gov launch <role> <ticket> starts the session as its role: the role's text (its generated agent, or the role file's text appended) is in the session's context at its start, shown by a launched session's log; the launch record holds the role file's path, version and content hash. | a planted role file and a launch of that role: the session's first context names the role's text, and the launch record holds the file's path, version and sha256 [DEC-826 Q1, lens E F2] [Verify clause added, DEC-1157 (12)] |
| S2 | The skills the session can load are in the launch record, each with its name, version and content hash, taken from the copy the session loads; a role file that names its skills gets those, so the engineer's skill packs load with no code change once W2-33 writes them; a named skill that is missing refuses the launch. | a planted role file naming two skills: the launch record lists each with its name, version and sha256 from the loaded copy; the same file naming a missing skill: the launch is refused naming it [DEC-826 Q1, DEC-832 item 1, lens E F15] [Verify clause added, DEC-1157 (12)] |
| S3 | The session's model and effort are RUBRIC-2's for its role and criticality: read from the role file's `Launch default` line and its `Launch by criticality` line (C3, C2, C1, C0), the ticket's criticality derived from its profile and `allowed_paths` by `governance/project/criticality.yaml` (never from the ticket's `class`, which is its kind); applied on the launch line (--model, --effort) and recorded with `tier`, `criticality` and `model_source` (role default, by criticality, after --, trial, promotion); a missing or malformed line refuses the launch; an effort below high for a judgement role, or max with no `--reason`, is refused. | a case per role and criticality on fixture role files [DEC-1120 (2)-(3), CAP-35.c lite, lens F R1] (folds W2-21 S4) [changed, DEC-1120 (5), DEC-1126 (3)] |
| S4 | A model after -- that is not the resolved tier's is refused, naming both, unless `--trial <id>` names a recorded trial (role, criticality, model and effort, two or more tickets that include this one, its Opus reviewer) and the launch records the trial id. The subagent model is the session's tier model (CLAUDE_CODE_SUBAGENT_MODEL in the settings' env), as the default for spawns that name none, recorded; a spawn that names its own wins (CLI above 2.1.251). | a planted trial record: the launch is accepted and records the id; a model after -- with no trial: refused naming both [DEC-1120 (3), lens E F14] (folds W2-21 S4) [changed, DEC-1120 (5), DEC-1126 (3)] |
| S5 | No launch sets a compaction threshold: no --autocompact on the line, no CLAUDE_CODE_AUTO_COMPACT_WINDOW in the settings or the session's environment, one given after -- refused; the launch record states the threshold as none. | the launch line and settings of a planted launch hold no --autocompact and no CLAUDE_CODE_AUTO_COMPACT_WINDOW; one given after -- is refused; the record says none [DEC-838 items 1 and 2] [Verify clause added, DEC-1157 (12)] |
| S6 | A launched session loads no connectors, no user-level agents or skills and no model-side memory: a test home planted with one of each shows none in the session's start; what the CLI gives no switch for is a package naming it, never passed silently. | a test home planted with one connector, one user-level agent, one user-level skill and model-side memory: a launched session's start shows none of them [DEC-826 Q5, lens E R6] (folds W2-21 S4) [Verify clause added, DEC-1157 (12)] |
| S7 | The arguments the launcher now sets itself are refused after --: --agent, --append-system-prompt and its file form, --session-id. | a launch with each of these after --: each is refused, naming the argument [lens E R6, DEC-826 Q5] [Verify clause added, DEC-1157 (12)] |
| S8 | Every launch writes one launch record, keyed by the session id the launcher gives with --session-id, before the session starts: role, ticket, the ticket's class, model, effort, subagent model, threshold none, the role text's and each skill's version and hash, the CLI's version and the start time, and `tier`, `criticality`, `model_source`, the trial id and the promotion reason (each null when not given); in one folder every worktree of the repository shares, stated in the CIT-E; a record that cannot be written refuses the launch. | a planted launch writes exactly one record under its --session-id holding every field named here, before the session starts; with the record folder unwritable the launch is refused [DEC-826 Q1, CAP-36.a lite, lens F R6, DEC-1120 (3)] (folds W2-21 S3, its launch record) [changed, DEC-1120 (5), DEC-1126 (3)] |
| S9 | Research first, by the lead before the engineer starts: whether a paths:-scoped .claude/rules/ file loads in a headless worker started by gov launch, its token cost, and whether the worker can change it; recorded in docs/research/W2-60-rules-probe.md. | the research record exists and answers the three questions, each with its evidence [lens G Q4] [Verify clause added, DEC-1157 (12)] |
| S10 | On a FULL ticket the second review is the probe, Opus max, and the first is Opus high; the record shows both; the same setting twice is refused unless the owner named it; max on any other review needs `--reason`. | a planted FULL ticket: the two launch records differ as stated; the same setting twice is refused [DEC-1014 item 1, SMART-WORK-5 A, DEC-1015 item 3, DEC-1120 (2)] [changed, DEC-1120 (5), DEC-1126 (3)] |
| S11 | A ticket whose review records show two failed reviews or a fail-open finding launches its next round on Opus at the table's effort, recorded as `promotion` with the reason and the record's path; a lower model is refused. | planted review records: one with two failed reviews, one with a fail-open finding, one with neither [DEC-1120 (3)] [changed, DEC-1120 (5), DEC-1126 (3)] |
| S12 | Routed from W2-33 (its S2, DEC-1156 (3)): the launcher's plan for a planted ticket prints the model and effort of the role file's `- **Launch default:**` line (W2-33's line form). | a planted ticket whose role file says `model claude-sonnet-5-5, effort high`: the plan prints that model and effort; a role file without the line fails the plan naming the file [DEC-954, DEC-957, DEC-1156 (3)] |
| F1 | A launch that starts with no role text, an unrecorded skill, a model not the role's, a compaction threshold, a user-level agent, skill or connector, or model-side memory. | S1, S2, S3, S5 and S6's planted cases: none of these launches starts [Verify clause added, DEC-1157 (12)] |
| F2 | A role file without its default line that still launches; a launch with no record, or a record naming another session. | a planted role file without its Launch default line is refused; every planted launch has its record, keyed by its own session id [Verify clause added, DEC-1157 (12)] |
| F3 | A refusal the launcher makes today that no longer refuses. | the launcher's existing refusal cases under tests/unit/launch/ pass unchanged on the branch [Verify clause added, DEC-1157 (12)] |
| F4 | A model below its tier with no trial; a promotion not applied; an effort below the floor. | S3 and S4's planted cases: a model below its tier with no trial is refused; a promotion is recorded and applied; an effort below high for a judgement role is refused [changed, DEC-1120 (5), DEC-1126 (3)] [Verify clause added, DEC-1157 (12)] |
Non-goals (do not build, do not test): none
Done when: the DoD lines DOD-1, DOD-2, DOD-3, DOD-4, DOD-5, DOD-6 hold for your part.

## Inputs
- Sources: DEC-826, DEC-838, DEC-839, DEC-832, DEC-801, DEC-786, DEC-941, CAP-35.c, CAP-36.a, DEC-1014, DEC-1015, DEC-1119, DEC-1120, DEC-1126. Read each by id in /home/usain/Dynamic-Agentic-Engineering-OS/docs/DECISION_REGISTER.md, or ask memory (below).
- What the lead knows of the ground: This is run 4 of W2-60a (DAEO-cv58), run kind resume (build), FULL profile; its merge is HELD until W2-33 lands (DEC-957 Q10; DEC-1157 (15)). Run 3 returned DONE on 2026-10-31 (review round 3 PASS, probe record docs/probes/DAEO-cv58/PR-DAEO-cv58.md at e1a3e2214266); read your CHECKPOINT.md. Since then: (1) w2/integrate moved a long way: merge it first (git merge --no-edit w2/integrate); it stops at one conflict, tests/unit/launch/test_w1_32.py (in your paths): an engineer resolves it (keep both sides' cases; integrate's changes came from W2-153 and W2-56), then commit the merge with your trailers; (2) one success line was added tonight, routed from W2-33 (DEC-1156 (3)): the launcher's plan for a planted ticket prints the model and effort of the role file's '- **Launch default:**' line (W2-33's line form, stated in DAEO-lrre's Interface); a role file without the line fails the plan naming the file. Work order: one independent test designer writes that line's acceptance case (tests/acceptance/W2-60a/), then one engineer builds it in src/gov/launch/role.py or launcher.py; then gov accept, lead_verify once (scoped, the close's form). Review rounds are spent (DEC-1010): instead a narrow independent check (Opus high, read-only, DEC-1154) of exactly the diff since e1a3e2214266 that is W2-60a's own (the new line, its case, and any conflict resolution), committed as the probe record (the older renamed -round-3.md). Return DONE with the head; the CTO lands it after W2-33. If integrate's changes break W2-60a's earlier KPI lines, name each with file:line; fix only within its paths.
Class C3 (RUBRIC-2, FULL): workers on Opus, high (claude-opus-5-5, --class C3). Every pytest, yours and every worker's, through bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh, with a TMPDIR outside the repository and outside ~/gov-os-runs, PYTHONUSERBASE=/home/usain/.local, -p no:cacheprovider -o tmp_path_retention_policy=failed. A path case of the form "the branch changes only the ticket's allowed_paths" judges only this ticket's branch (skip elsewhere, naming the branch found); a hygiene check compares paths with Path.is_relative_to, never a text search of a temporary path (DEC-1155). If another ticket's path case, or an older case asserting a behaviour the owner has since decided, turns red on this branch: name it in your return with file:line (the CTO fixes such cases under DEC-1156 (7)); do not fix it outside your paths. The base-red rule holds. A resource gate's refusal is a wait (DEC-1146); a runaway-brake refusal goes to the CTO. No new run starts after 03:00 (the night hold): reach a checkpoint before it if you cannot finish. Never open the evaluation sets' root or any hidden or memory-verdict folder. No new ticket and no widening: a gap comes back as a package (the owner answers at night, DEC-1156 (8)). A session refused twice for an action by the guard, the sandbox or a hook stops and says so (DEC-1142 (9)).
Keep contexts short; there is no token cap: use your model's full window; before compaction the hook writes your checkpoint and the summary opens with the read-first line. Return DONE with the head to land and the probe record, or PACKAGES.
none

## Commands (copy them as they are)
| name | command |
|---|---|
| identity | `printenv GOV_ROLE GOV_TICKET` |
| where | `git -C /home/usain/gov-os-worktrees/W2-60a rev-parse --show-toplevel --abbrev-ref HEAD` |
| retrieve | `gov retrieve --root /home/usain/gov-os-worktrees/W2-00-store "{QUESTION}"` |
| context | `gov context DAEO-cv58 --role {WORKER_ROLE}` |
| launch_worker | `bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/launch_worker.sh {WORKER_ROLE} {EFFORT} {BRIEF_FILE}` |
| wait_for | `bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/wait_for.sh {EXIT_FILE}` |
| tests_worktree | `git -C /home/usain/gov-os-worktrees/W2-60a worktree add /home/usain/gov-os-worktrees/W2-60a-tests -b w2/W2-60a-tests HEAD` |
| merge_tests | `git -C /home/usain/gov-os-worktrees/W2-60a merge --no-ff w2/W2-60a-tests -F {MESSAGE_FILE}` |
| accept | `gov accept W2-60a --root /home/usain/gov-os-worktrees/W2-60a` |
| rebuild | `env PYTHONPATH=/home/usain/gov-os-worktrees/W2-60a/src bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/rebuild_slot.sh /home/usain/gov-os-worktrees/W2-60a` |
| lead_verify | `bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/lead_verify.sh /home/usain/gov-os-worktrees/W2-60a W2-60a DAEO-cv58` |
| tests_worktree_remove | `git -C /home/usain/gov-os-worktrees/W2-60a worktree remove /home/usain/gov-os-worktrees/W2-60a-tests` |
| links | `gov links --since {BASE}` |
Ask memory first: outside the sandbox gov retrieve --root /home/usain/gov-os-worktrees/W2-00-store "{QUESTION}" "<which decision governs X | where is Y implemented>"; inside it, the Read and Grep tools [DEC-1065]; grep the register only by id.
Search again once: if the bundle does not answer, or your answer may be incomplete, ask once more in your own, different words; then answer from both bundles with path and lines, or say "not found". Two searches in all; never answer beyond what you read.
No `gov retrieve` in the sandbox, and no `gov context`: a launched worker searches with the Read and Grep tools, and searches again once the same way [DEC-1065].
Every whole-folder pytest run adds `-m "not local_only" -k "not real and not green_here and not time_limit"` and an empty `HOME`: run it as env HOME=/home/usain/gov-os-worktrees/W2-60a/.gov-runtime/scratch/empty-home PYTHONPATH=/home/usain/gov-os-worktrees/W2-60a/src python3 -m pytest {FOLDER} -q -p no:cacheprovider -o tmp_path_retention_policy=failed -m "not local_only" -k "not real and not green_here and not time_limit" [DEC-1065].
Wait for anything long with bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/wait_for.sh {EXIT_FILE}, one call per 9.5 min; never a hand-written sleep loop.
No merge inside the sandbox: the CTO or your lead merges into your branch outside it; a restore or conflict resolution in `tests/acceptance/` is a test designer's [DEC-1052].

## Forms that work (the guard and the harness accept these)
- Write and edit files with the Write and Edit tools and absolute paths.
- Anything longer than one line goes in a script file under /home/usain/gov-os-worktrees/W2-60a/.gov-runtime/scratch/, run with `bash <file>` or `python3 <file>`.
- Use literal paths, never a shell variable or `$(…)` as a write target; name the folder a listing or search starts at.
- The harness allows these headless without asking: Bash, Read, Edit, Write, Grep, Glob. For anything else use a script file as above, or report it; never retry another form.

## Commit (your paths only)
```
git commit -m "{SUBJECT}" --trailer "Task: DAEO-cv58" --trailer "Role: orchestrator" --trailer "Implements: DEC-826, DEC-838, DEC-839, DEC-832, DEC-801, DEC-786, DEC-941, CAP-35.c, CAP-36.a, DEC-1014, DEC-1015, DEC-1119, DEC-1120, DEC-1126" -- {COMMIT_PATHS}
```
- `Task:` is the ticket's id (DAEO-cv58, a `DAEO-…` id), never a W2 id [DEC-182].
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

## Your run: resume (only this section is in your brief)
**resume**: read /home/usain/gov-os-worktrees/W2-60a/.gov-runtime/scratch/lead/CHECKPOINT.md; do its NEXT line; then continue in the run kind it names.
