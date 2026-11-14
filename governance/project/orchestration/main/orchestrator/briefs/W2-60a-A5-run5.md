# Your assignment
You are a fresh orchestrator session. Your role's rules are in your system prompt (template `role-lead`); this brief gives this assignment's facts.
Ticket DAEO-cv58 (W2-60a), profile FULL. Objective: The role, its skills and its model and effort loaded at launch; the launch record. Card: the draft card `W2-60` (W2-60a part), from the accepted plan (`docs/plan/WAVE_2_REVISED_PLAN.md` §4.3, §2 row 5 and the CAP-35.c and CAP-36.a lite rows; DEC-826 Q1 and Q5, DEC-838, DEC-839); keystone 3, agents know what to do. Started now by the re-plan the owner accepted on 2026-10-29 (DEC-941), beside the memory work.

## Where you work
| what | path |
|---|---|
| your tree (write here only) | /home/usain/gov-os-worktrees/W2-60a |
| branch | w2/W2-60a |
| allowed paths | src/gov/launch/launcher.py, src/gov/launch/role.py, src/gov/launch/record.py, src/gov/launch/criticality.py, governance/project/criticality.yaml, tests/unit/launch/test_role*, tests/unit/launch/test_launch_record*, tests/unit/launch/test_runs.py, tests/unit/launch/test_w1_28.py, tests/unit/launch/test_w1_32.py, docs/changes/W2-60a-CIT-E.md, docs/research/W2-60-rules-probe.md, tests/acceptance/W2-50/w2_50_support.py, tests/acceptance/W2-58/README.md, tests/acceptance/W2-58/test_w2_58_launched_sessions.py, tests/acceptance/W2-58/w2_58_support.py, tests/unit/launch/test_w2_136_plan_check.py, tests/unit/launch/test_w2_153_template.py, tests/unit/launch/test_w2_56.py, tests/acceptance/W2-153/test_w2_153_launch.py, tests/acceptance/W2-56/test_w2_56_environment.py, tests/acceptance/W2-56/test_w2_56_endings.py, tests/acceptance/W2-56/test_w2_56_refused_arguments.py |
| ticket file (read-only) | /home/usain/Dynamic-Agentic-Engineering-OS/.tickets/DAEO-cv58.md |
| your scratch | /home/usain/gov-os-worktrees/W2-60a/.gov-runtime/scratch/ |

## What must be true (KPI lines and how each is checked)
| id | line | verify |
|---|---|---|
| S1 | gov launch <role> <ticket> starts the session as its role: the role's text (its generated agent, or the role file's text appended) is in the session's context at its start, shown by a launched session's log; the launch record holds the role file's path, version and content hash. | a planted role file and a launch of that role: the session's first context names the role's text, and the launch record holds the file's path, version and sha256 [DEC-826 Q1, lens E F2] [Verify clause added, DEC-1157 (12)] |
| S2 | The skills the session can load are in the launch record, each with its name, version and content hash, taken from the copy the session loads; a role file that names its skills gets those, so the engineer's skill packs load with no code change once W2-33 writes them; a named skill that is missing refuses the launch. | a planted role file naming two skills: the launch record lists each with its name, version and sha256 from the loaded copy; the same file naming a missing skill: the launch is refused naming it [DEC-826 Q1, DEC-832 item 1, lens E F15] [Verify clause added, DEC-1157 (12)] |
| S3 | The role's default model and effort, read from its role file's `Launch default` line, are applied on the launch line (--model, --effort) and recorded with `model_source` (role default, or after --); a missing or malformed default line refuses the launch; an effort given after -- is applied and recorded as the launch's own. | a planted role file's default line is applied and recorded; a missing or malformed line is refused naming the file; an effort after -- is recorded as the launch's own (tests/acceptance/W2-60a/test_w2_60a_model_and_effort.py) [DEC-839 items 1, 2 and 5, CAP-35.c lite, lens F R1] (folds W2-21 S4) [restored by P1-W2-60a-P5 (B), DEC-1167; RUBRIC-2's form moved to W2-184] |
| S4 | A model given after -- that is not the role's is refused, naming both; the subagent model is set to the session's model (CLAUDE_CODE_SUBAGENT_MODEL in the settings' env) and recorded. | a model after -- that is not the role's is refused naming both; the planted launch's settings carry CLAUDE_CODE_SUBAGENT_MODEL equal to its model, recorded (tests/acceptance/W2-60a/test_w2_60a_model_and_effort.py) [DEC-839 items 1 and 3, lens E F14] (folds W2-21 S4) [restored by P1-W2-60a-P5 (B), DEC-1167; the trial moved to W2-184] |
| S5 | No launch sets a compaction threshold: no --autocompact on the line, no CLAUDE_CODE_AUTO_COMPACT_WINDOW in the settings or the session's environment, one given after -- refused; the launch record states the threshold as none. | the launch line and settings of a planted launch hold no --autocompact and no CLAUDE_CODE_AUTO_COMPACT_WINDOW; one given after -- is refused; the record says none [DEC-838 items 1 and 2] [Verify clause added, DEC-1157 (12)] |
| S6 | A launched session loads no connectors, no user-level agents or skills and no model-side memory: a test home planted with one of each shows none in the session's start; what the CLI gives no switch for is a package naming it, never passed silently. | a test home planted with one connector, one user-level agent, one user-level skill and model-side memory: a launched session's start shows none of them [DEC-826 Q5, lens E R6] (folds W2-21 S4) [Verify clause added, DEC-1157 (12)] |
| S7 | The arguments the launcher now sets itself are refused after --: --agent, --append-system-prompt and its file form, --session-id. | a launch with each of these after --: each is refused, naming the argument [lens E R6, DEC-826 Q5] [Verify clause added, DEC-1157 (12)] |
| S8 | Every launch writes one launch record, keyed by the session id the launcher gives with --session-id, before the session starts: role, ticket, the ticket's class, model, effort, subagent model, threshold none, the role text's and each skill's version and hash, the CLI's version and the start time; in one folder every worktree of the repository shares, stated in the CIT-E; a record that cannot be written refuses the launch. | a planted launch writes exactly one record under its --session-id holding every field named here, before the session starts; with the record folder unwritable the launch is refused (tests/acceptance/W2-60a/test_w2_60a_launch_record.py) [DEC-826 Q1, CAP-36.a lite, lens F R6] (folds W2-21 S3, its launch record) [restored by P1-W2-60a-P5 (B), DEC-1167; tier, criticality, trial and promotion fields moved to W2-184] |
| S9 | Research first, by the lead before the engineer starts: whether a paths:-scoped .claude/rules/ file loads in a headless worker started by gov launch, its token cost, and whether the worker can change it; recorded in docs/research/W2-60-rules-probe.md. | the research record exists and answers the three questions, each with its evidence [lens G Q4] [Verify clause added, DEC-1157 (12)] |
| S10 | On a FULL ticket that could fail open, the second review is launched with a different model or effort setting from the first, taken from the role defaults; the launch record shows both, and the same setting twice is refused unless the owner named it. | a planted FULL ticket's two review launches record different settings; the same setting twice is refused unless an owner-named decision is given [DEC-1014 item 1, SMART-WORK-5 A, DEC-1015 item 3] [restored by P1-W2-60a-P5 (B), DEC-1167; RUBRIC-2's Opus high then max moved to W2-184] |
| S11 | Routed from W2-33 (its S2, DEC-1156 (3)): the launcher's plan for a planted ticket prints the model and effort of the role file's `- **Launch default:**` line (W2-33's line form). | a planted ticket whose role file says `model claude-sonnet-5-5, effort high`: the plan prints that model and effort; a role file without the line fails the plan naming the file [DEC-954, DEC-957, DEC-1156 (3)] |
| F1 | A launch that starts with no role text, an unrecorded skill, a model not the role's, a compaction threshold, a user-level agent, skill or connector, or model-side memory. | S1, S2, S3, S5 and S6's planted cases: none of these launches starts [Verify clause added, DEC-1157 (12)] |
| F2 | A role file without its default line that still launches; a launch with no record, or a record naming another session. | a planted role file without its Launch default line is refused; every planted launch has its record, keyed by its own session id [Verify clause added, DEC-1157 (12)] |
| F3 | A refusal the launcher makes today that no longer refuses. | the launcher's existing refusal cases under tests/unit/launch/ pass unchanged on the branch [Verify clause added, DEC-1157 (12)] |
Non-goals (do not build, do not test): none
Done when: the DoD lines DOD-1, DOD-2, DOD-3, DOD-4, DOD-5, DOD-6 hold for your part.

## Inputs
- Sources: DEC-826, DEC-838, DEC-839, DEC-832, DEC-801, DEC-786, DEC-941, CAP-35.c, CAP-36.a, DEC-1014, DEC-1015, DEC-1119, DEC-1120, DEC-1126. Read each by id in /home/usain/Dynamic-Agentic-Engineering-OS/docs/DECISION_REGISTER.md, or ask memory (below).
- What the lead knows of the ground: This is run 5 of W2-60a (DAEO-cv58), FULL, class C3, after your run 4e's LAUNCH_BLOCKED (14:41). Both open questions are answered. Read your lead checkpoint first, then the ticket again (changed by 81d16e088).

**The answers:**
- **P-5: the owner chose (B)** (DEC-1167 (2)). W2-60a lands its reviewed scope. S3, S4, S8 and S10 are back to their DEC-839 forms, each with a Verify, and S11 and F4 are out of the ticket. RUBRIC-2's lines move to W2-184 (`DAEO-6f0s`), filed, which starts after you merge. Build no RUBRIC-2 line here. S12's interface reads "the role file's `- **Launch default:**` line" only; the by-criticality read is W2-184's.
- **P-LB-1: the CTO chose (1).** Start every worker with `LAUNCH_CODE_ROOT=/home/usain/Dynamic-Agentic-Engineering-OS` in launch_worker.sh's environment, e.g. `LAUNCH_CODE_ROOT=/home/usain/Dynamic-Agentic-Engineering-OS LAUNCH_TICKET=DAEO-cv58 bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/launch_worker.sh --class C3 --model claude-opus-5-5 <role> high <brief>`. `gov launch` and its dry run then come from integrate's code; the sandbox root, the ticket and every check stay your tree. Your own launcher is judged by gov accept and the scoped run.

**The order:**
1. b12, a fresh independent test designer, resolves the five conflict markers in the four acceptance files committed in 5b7941b66, on its sides `5b7941b66^1` and `^2`, with its own commit (Task, Role, Implements, Rewrite-Reason). It also plants the templates and the open gate in W2-60a's fixtures. In parallel, b13, a test designer in the tests worktree, writes:
   - the S12 test as a new self-contained file;
   - P-3's older fixtures;
   - a case for a skill copy that carries its version only under `metadata: version:`.
2. An engineer (C3):
   - first, S2's defect: `role.py:212` reads a skill's `version`, else `metadata.version`, so a launch on integrate's generated copies is not refused. This is in S2 and F3's scope: today's copies must not be refused.
   - then S12's `gov launch --plan`.
3. `gov accept W2-60a`, the rebuild, and the scoped run once (DEC-968). `git grep -n '^<<<<<<<'` must be empty.
4. A narrow independent check of W2-60a's own diff since e1a3e2214266 (review rounds are spent, DEC-1010). It covers S2's version-reader fix, S12, and the restored DEC-839 lines against the reviewed code. Its probe record has the schema's `implementer_session` field and is validated against probe.schema.json; the old record moves to `-round-3.md`.
5. Return DONE with the head to land.

W2-60a gates W2-27 (EXAMIN's copy): a package that stops you goes to the CTO at once. Workers launched by `gov launch` write only their sandbox's own `$TMPDIR`. Every pytest, yours and every worker's, through bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh with a TMPDIR outside the repository and outside ~/gov-os-runs (a launched worker: its sandbox's `$TMPDIR`), PYTHONUSERBASE=/home/usain/.local, -p no:cacheprovider -o tmp_path_retention_policy=failed. Waits and stops by pid only (`/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/proc.sh wait --max <s> <pid>`). A resource gate's refusal is a wait (DEC-1146). A session refused twice for the same action stops and says so, and never works around a refusal by another tool or form (DEC-1142 (9)). Never open the evaluation sets' root or any hidden or memory-verdict folder. No new ticket. There is no token cap.
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

## Your run: build (only this section is in your brief)
**build**: implement and verify.
1. Run the *tests* steps 1 to 3 and, in parallel, the implementer (engineer) from its brief.
2. Merge the tests when the implementer is between batches; write TESTS-READY.
3. Verify: env PYTHONPATH=/home/usain/gov-os-worktrees/W2-60a/src bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/rebuild_slot.sh /home/usain/gov-os-worktrees/W2-60a, then bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/lead_verify.sh /home/usain/gov-os-worktrees/W2-60a W2-60a DAEO-cv58, then wait. Name a red as known only from /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/skip_known.json; re-run a load-sensitive case alone once.
4. Red: a fresh implementer given the failing output only. Three iterations that do not converge: return ESCALATION [DEC-096].
