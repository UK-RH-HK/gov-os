# Your assignment
You are a fresh orchestrator session. Your role's rules are in your system prompt (template `role-lead`); this brief gives this assignment's facts.
Ticket DAEO-6n5k (W2-37), profile FULL. Objective: gov impact. Card: `docs/plan/WAVE_2_WBS.md` §2 (W2-37), as approved (DEC-729). The list rows it takes in are in `list_rows` and in `docs/plan/WAVE_2_TRIAGE.md`; a row's state is re-checked against the code when the ticket picks it up (DEC-718).

## Where you work
| what | path |
|---|---|
| your tree (write here only) | /home/usain/gov-os-worktrees/W2-37 |
| branch | w2/W2-37 |
| allowed paths | src/gov/impact/**, src/gov/closure/**, tests/unit/impact/** |
| ticket file (read-only) | /home/usain/Dynamic-Agentic-Engineering-OS/.tickets/DAEO-6n5k.md |
| your scratch | /home/usain/gov-os-worktrees/W2-37/.gov-runtime/scratch/ |

## What must be true (KPI lines and how each is checked)
| id | line | verify |
|---|---|---|
| S1 | "What's the impact of X?" in plain language runs gov impact [CAP-33.g, DEC-167]. | a planted question "what is the impact of DEC-NNN?" given to the plain-language entry runs gov impact on DEC-NNN and prints its result [Verify clause added, DEC-1157 (12)] |
| S2 | It also takes the S0b2 glue G-16 (id mapping) and G-24 (deletable-class join). | planted records with mapped ids and a deletable-class row: gov impact resolves the mapped ids (G-16) and joins the deletable class (G-24) in its result [Verify clause added, DEC-1157 (12)] |
Non-goals (do not build, do not test): none
Done when: the DoD lines DOD-1, DOD-2, DOD-3, DOD-4, DOD-5, DOD-6 hold for your part.

## Inputs
- Sources: CAP-33.b, CAP-33.g, DEC-167, DEC-1083. Read each by id in /home/usain/Dynamic-Agentic-Engineering-OS/docs/DECISION_REGISTER.md, or ask memory (below).
- What the lead knows of the ground: This is a resume run of W2-37 (DAEO-6n5k), gov impact, FULL, run kind resume. It was held since 2026-10-31 at 'checkpoint before the final probe', stacked on W2-03 (DEC-786); W2-03 is closed, so the hold is gone (DEC-1157: nothing holds a lead but the machine's and the governance's protections). Read your CHECKPOINT.md and the ticket. (1) Merge w2/integrate (git merge --no-edit w2/integrate): 13 days behind; an engineer resolves conflicts in your paths and names any outside them; the CTO committed .claude/templates/role-lead.md on your branch (byte-identical to integrate's) so the launcher could start you: the merge brings the same bytes. (2) gov accept and lead_verify once on the merged head; fix within your paths (the base-red rule holds). (3) The final probe: the FULL review's next round (at most two rounds in all, DEC-1010: count the rounds already run in your probe record), committed as docs/probes/DAEO-6n5k/PR-DAEO-6n5k.md if that path is in the ticket's paths (else return it in full). Return DONE with the head to land, or PACKAGES for any decision outside the ticket's purpose (the owner's at any hour, DEC-1157 (1)).
Class C2 (RUBRIC-2): workers on Sonnet, high (claude-sonnet-5-5, --class C2); a reviewer on Opus, high. Every pytest, yours and every worker's, through bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh, with a TMPDIR outside the repository and outside ~/gov-os-runs, PYTHONUSERBASE=/home/usain/.local, -p no:cacheprovider -o tmp_path_retention_policy=failed. A path case of the form "the branch changes only the ticket's allowed_paths" judges only this ticket's branch (skip elsewhere, naming the branch found); a hygiene check compares paths with Path.is_relative_to, never a text search of a temporary path (DEC-1155). If another ticket's path case, or an older case asserting a behaviour the owner has since decided, turns red on this branch: name it in your return with file:line (the CTO fixes such cases under DEC-1156 (7)); do not fix it outside your paths. The base-red rule holds. A resource gate's refusal is a wait (DEC-1146); a runaway-brake refusal goes to the CTO. No new run starts after 03:00 (the night hold): reach a checkpoint before it if you cannot finish. Never open the evaluation sets' root or any hidden or memory-verdict folder. No new ticket and no widening: a gap comes back as a package (the owner answers at night, DEC-1156 (8)). A session refused twice for an action by the guard, the sandbox or a hook stops and says so (DEC-1142 (9)).
Keep contexts short; there is no token cap: use your model's full window; before compaction the hook writes your checkpoint and the summary opens with the read-first line. Return DONE with the head to land and the probe record, or PACKAGES.
none

## Commands (copy them as they are)
| name | command |
|---|---|
| identity | `printenv GOV_ROLE GOV_TICKET` |
| where | `git -C /home/usain/gov-os-worktrees/W2-37 rev-parse --show-toplevel --abbrev-ref HEAD` |
| retrieve | `gov retrieve --root /home/usain/gov-os-worktrees/W2-00-store "{QUESTION}"` |
| context | `gov context DAEO-6n5k --role {WORKER_ROLE}` |
| launch_worker | `bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/launch_worker.sh {WORKER_ROLE} {EFFORT} {BRIEF_FILE}` |
| wait_for | `bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/wait_for.sh {EXIT_FILE}` |
| tests_worktree | `git -C /home/usain/gov-os-worktrees/W2-37 worktree add /home/usain/gov-os-worktrees/W2-37-tests -b w2/W2-37-tests HEAD` |
| merge_tests | `git -C /home/usain/gov-os-worktrees/W2-37 merge --no-ff w2/W2-37-tests -F {MESSAGE_FILE}` |
| accept | `gov accept W2-37 --root /home/usain/gov-os-worktrees/W2-37` |
| rebuild | `env PYTHONPATH=/home/usain/gov-os-worktrees/W2-37/src bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/rebuild_slot.sh /home/usain/gov-os-worktrees/W2-37` |
| lead_verify | `bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/lead_verify.sh /home/usain/gov-os-worktrees/W2-37 W2-37 DAEO-6n5k` |
| tests_worktree_remove | `git -C /home/usain/gov-os-worktrees/W2-37 worktree remove /home/usain/gov-os-worktrees/W2-37-tests` |
| links | `gov links --since {BASE}` |
Ask memory first: outside the sandbox gov retrieve --root /home/usain/gov-os-worktrees/W2-00-store "{QUESTION}" "<which decision governs X | where is Y implemented>"; inside it, the Read and Grep tools [DEC-1065]; grep the register only by id.
Search again once: if the bundle does not answer, or your answer may be incomplete, ask once more in your own, different words; then answer from both bundles with path and lines, or say "not found". Two searches in all; never answer beyond what you read.
No `gov retrieve` in the sandbox, and no `gov context`: a launched worker searches with the Read and Grep tools, and searches again once the same way [DEC-1065].
Every whole-folder pytest run adds `-m "not local_only" -k "not real and not green_here and not time_limit"` and an empty `HOME`: run it as env HOME=/home/usain/gov-os-worktrees/W2-37/.gov-runtime/scratch/empty-home PYTHONPATH=/home/usain/gov-os-worktrees/W2-37/src python3 -m pytest {FOLDER} -q -p no:cacheprovider -o tmp_path_retention_policy=failed -m "not local_only" -k "not real and not green_here and not time_limit" [DEC-1065].
Wait for anything long with bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/wait_for.sh {EXIT_FILE}, one call per 9.5 min; never a hand-written sleep loop.
No merge inside the sandbox: the CTO or your lead merges into your branch outside it; a restore or conflict resolution in `tests/acceptance/` is a test designer's [DEC-1052].

## Forms that work (the guard and the harness accept these)
- Write and edit files with the Write and Edit tools and absolute paths.
- Anything longer than one line goes in a script file under /home/usain/gov-os-worktrees/W2-37/.gov-runtime/scratch/, run with `bash <file>` or `python3 <file>`.
- Use literal paths, never a shell variable or `$(…)` as a write target; name the folder a listing or search starts at.
- The harness allows these headless without asking: Bash, Read, Edit, Write, Grep, Glob. For anything else use a script file as above, or report it; never retry another form.

## Commit (your paths only)
```
git commit -m "{SUBJECT}" --trailer "Task: DAEO-6n5k" --trailer "Role: orchestrator" --trailer "Implements: CAP-33.b, CAP-33.g, DEC-167, DEC-1083" -- {COMMIT_PATHS}
```
- `Task:` is the ticket's id (DAEO-6n5k, a `DAEO-…` id), never a W2 id [DEC-182].
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
**resume**: read /home/usain/gov-os-worktrees/W2-37/.gov-runtime/scratch/lead/CHECKPOINT.md; do its NEXT line; then continue in the run kind it names.
