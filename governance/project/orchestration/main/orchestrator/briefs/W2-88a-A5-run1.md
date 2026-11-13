# Your assignment
You are a fresh orchestrator session. Your role's rules are in your system prompt (template `role-lead`); this brief gives this assignment's facts.
Ticket DAEO-pg6i (W2-88a), profile STANDARD. Objective: W2-88a The adopt skill states Wave 0's memory practice in order, and the Verify pass (W2-88's and W2-174's kernel skill text). Filed by the owner's decision (DEC-1150 (1), package 1 (a), 2026-11-12), under DEC-996 (1)'s split list: W2-88 mixed three roles (DEC-995). This child holds the kernel skill text: W2-88's S17 (moved word for word) and W2-174's skill line (its S5, moved word for word, so the adopt skill is written once under one CIT-P). The two `test_w2_174_skill.py` and S17 string tests named in the moved lines are this ticket's acceptance tests, written by its test designer under `tests/acceptance/W2-88a/`. It can start now; the owner approves the skill's bytes before the merge (CAP-33).

## Where you work
| what | path |
|---|---|
| your tree (write here only) | /home/usain/gov-os-worktrees/W2-88a |
| branch | w2/W2-88a |
| allowed paths | template/governance/kernel/skills/adopt/SKILL.md, template/.rulesync/skills/adopt/SKILL.md, .rulesync/skills/adopt/SKILL.md, docs/changes/W2-88a-CIT-P.md, docs/research/W2-88-memory-practice.md |
| ticket file (read-only) | /home/usain/Dynamic-Agentic-Engineering-OS/.tickets/DAEO-pg6i.md |
| your scratch | /home/usain/gov-os-worktrees/W2-88a/.gov-runtime/scratch/ |

## What must be true (KPI lines and how each is checked)
| id | line | verify |
|---|---|---|
| S1 | S17 The Wave 0 order in the adopt skill: A9's step in template/governance/kernel/skills/adopt/SKILL.md states the practice in order and points to the practice record. The order: assess and plan; census the stated links and build the graph from them; build the store with the standard (S10) and its refresh (S11); have the verdict set and the tuning set written (S13, S12); measure the tuning set and fix only the structure, never a named question, until its halves agree within 5 points; declare and measure the verdict set once (S14); record every method and figure. | a string test on the skill for the steps in that order, and the skills check [DEC-1098 (1), DEC-1072 (2), DEC-1071 (1)-(3), DEC-1074 (4), CAP-33] [added, DEC-1099 (2); DEC-1098 (1)] |
| S2 | The adopt skill, in the kernel copy and the two generated-source copies, states the pass: when it runs (for a ticket about to launch, not for the whole tracker), who writes the clauses (a product-spec session), what checks them (the tool, the ticket's test designer, the auditor's sample), and that the owner approves the rule once [DEC-1130, DEC-1083] | tests/unit/adopt/test_w2_174_skill.py: the three files carry the section `Verify clauses for adopted tickets` with the four statements, and the three copies are equal in that section |
| S3 | The CIT-P record (docs/changes/W2-88a-CIT-P.md) gives the kernel skill's sha256 before and after, the lines added or removed, the independent review and the owner's approval of the bytes before the merge; the two .rulesync copies equal the kernel copy in the changed sections | the record holds both hashes and the review's verdict; a diff of the three files shows the same changed sections [CAP-33, DEC-1116] |
Non-goals (do not build, do not test): the adopt code (W2-88, W2-174) and the proofs (W2-88b); the .claude/ copy (the copies ACT)
Done when: the DoD lines DOD-1, DOD-2, DOD-3, DOD-4, DOD-5, DOD-6 hold for your part.

## Inputs
- Sources: DEC-1150, DEC-996, DEC-995, DEC-1098, DEC-1130, CAP-33. Read each by id in /home/usain/Dynamic-Agentic-Engineering-OS/docs/DECISION_REGISTER.md, or ask memory (below).
- What the lead knows of the ground: This is run 1 of W2-88a (DAEO-pg6i), a child of W2-88 filed by the owner (DEC-1150 (1)): the adopt skill's kernel text. Read the ticket first: it holds W2-88's S17 (the Wave 0 order in the adopt skill) and W2-174's skill line (the Verify pass), moved word for word, and the CIT-P line. Role product-spec (one role per ticket, DEC-995): the product-spec worker writes the three adopt-skill files (`template/governance/kernel/skills/adopt/SKILL.md`, `template/.rulesync/skills/adopt/SKILL.md`, `.rulesync/skills/adopt/SKILL.md`), the practice record `docs/research/W2-88-memory-practice.md` refreshed to S17's order, and the CIT-P `docs/changes/W2-88a-CIT-P.md` (sha256 before and after, the lines added or removed, the review). STANDARD profile: first an independent test designer writes the acceptance tests under `tests/acceptance/W2-88a/` (the string tests the two moved lines name, and the three copies equal in the changed sections); then the product-spec worker; then one independent review (Opus, high); then the probe record (docs/probes/DAEO-pg6i/: if its folder is not in allowed_paths, say so). The kernel bytes go to the owner for approval before any merge (CAP-33): return DONE with the head and the CIT-P's hashes; nothing lands before the owner's approval line. The `.claude/skills/adopt/SKILL.md` copy is the CTO's copies ACT after the approval, not this run's.
Class C2 (RUBRIC-2): the test designer and the product-spec worker on Sonnet, high (claude-sonnet-5-5, --class C2); the reviewer on Opus, high. Every pytest, yours and every worker's, through bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh, with a TMPDIR outside the repository and outside ~/gov-os-runs, PYTHONUSERBASE=/home/usain/.local, -p no:cacheprovider -o tmp_path_retention_policy=failed. A resource gate's refusal is a wait (DEC-1146). A reviewer's read-only probes are allowed at any hour, by Bash into its own TMPDIR (DEC-1144 (7)). No new ticket and no widening: a gap comes back as a package. A session refused twice for an action by the guard, the sandbox or a hook stops and says so (DEC-1142 (9)).
Keep contexts short; there is no token cap: use your model's full window; before compaction the hook writes your checkpoint and the summary opens with the read-first line. Return DONE with the head and the CIT-P's hashes, or PACKAGES.
none

## Commands (copy them as they are)
| name | command |
|---|---|
| identity | `printenv GOV_ROLE GOV_TICKET` |
| where | `git -C /home/usain/gov-os-worktrees/W2-88a rev-parse --show-toplevel --abbrev-ref HEAD` |
| retrieve | `gov retrieve --root /home/usain/gov-os-worktrees/W2-00-store "{QUESTION}"` |
| context | `gov context DAEO-pg6i --role {WORKER_ROLE}` |
| launch_worker | `bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/launch_worker.sh {WORKER_ROLE} {EFFORT} {BRIEF_FILE}` |
| wait_for | `bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/wait_for.sh {EXIT_FILE}` |
| tests_worktree | `git -C /home/usain/gov-os-worktrees/W2-88a worktree add /home/usain/gov-os-worktrees/W2-88a-tests -b w2/W2-88a-tests HEAD` |
| merge_tests | `git -C /home/usain/gov-os-worktrees/W2-88a merge --no-ff w2/W2-88a-tests -F {MESSAGE_FILE}` |
| accept | `gov accept W2-88a --root /home/usain/gov-os-worktrees/W2-88a` |
| rebuild | `env PYTHONPATH=/home/usain/gov-os-worktrees/W2-88a/src bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/rebuild_slot.sh /home/usain/gov-os-worktrees/W2-88a` |
| lead_verify | `bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/lead_verify.sh /home/usain/gov-os-worktrees/W2-88a W2-88a DAEO-pg6i` |
| tests_worktree_remove | `git -C /home/usain/gov-os-worktrees/W2-88a worktree remove /home/usain/gov-os-worktrees/W2-88a-tests` |
| links | `gov links --since {BASE}` |
Ask memory first: outside the sandbox gov retrieve --root /home/usain/gov-os-worktrees/W2-00-store "{QUESTION}" "<which decision governs X | where is Y implemented>"; inside it, the Read and Grep tools [DEC-1065]; grep the register only by id.
Search again once: if the bundle does not answer, or your answer may be incomplete, ask once more in your own, different words; then answer from both bundles with path and lines, or say "not found". Two searches in all; never answer beyond what you read.
No `gov retrieve` in the sandbox, and no `gov context`: a launched worker searches with the Read and Grep tools, and searches again once the same way [DEC-1065].
Every whole-folder pytest run adds `-m "not local_only" -k "not real and not green_here and not time_limit"` and an empty `HOME`: run it as env HOME=/home/usain/gov-os-worktrees/W2-88a/.gov-runtime/scratch/empty-home PYTHONPATH=/home/usain/gov-os-worktrees/W2-88a/src python3 -m pytest {FOLDER} -q -p no:cacheprovider -o tmp_path_retention_policy=failed -m "not local_only" -k "not real and not green_here and not time_limit" [DEC-1065].
Wait for anything long with bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/wait_for.sh {EXIT_FILE}, one call per 9.5 min; never a hand-written sleep loop.
No merge inside the sandbox: the CTO or your lead merges into your branch outside it; a restore or conflict resolution in `tests/acceptance/` is a test designer's [DEC-1052].

## Forms that work (the guard and the harness accept these)
- Write and edit files with the Write and Edit tools and absolute paths.
- Anything longer than one line goes in a script file under /home/usain/gov-os-worktrees/W2-88a/.gov-runtime/scratch/, run with `bash <file>` or `python3 <file>`.
- Use literal paths, never a shell variable or `$(…)` as a write target; name the folder a listing or search starts at.
- The harness allows these headless without asking: Bash, Read, Edit, Write, Grep, Glob. For anything else use a script file as above, or report it; never retry another form.

## Commit (your paths only)
```
git commit -m "{SUBJECT}" --trailer "Task: DAEO-pg6i" --trailer "Role: orchestrator" --trailer "Implements: DEC-1150, DEC-996, DEC-995, DEC-1098, DEC-1130, CAP-33" -- {COMMIT_PATHS}
```
- `Task:` is the ticket's id (DAEO-pg6i, a `DAEO-…` id), never a W2 id [DEC-182].
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

## Your run: tests (only this section is in your brief)
**tests**: the tests only.
1. git -C /home/usain/gov-os-worktrees/W2-88a worktree add /home/usain/gov-os-worktrees/W2-88a-tests -b w2/W2-88a-tests HEAD
2. Build the test designer's brief (above) into /home/usain/gov-os-worktrees/W2-88a/.gov-runtime/scratch/lead/briefs/td-<n>.md.
3. Launch it (role independent-test-designer), then wait.
4. Check the return (below); merge the tests (git -C /home/usain/gov-os-worktrees/W2-88a merge --no-ff w2/W2-88a-tests -F {MESSAGE_FILE}); check red (gov accept W2-88a --root /home/usain/gov-os-worktrees/W2-88a); write /home/usain/gov-os-worktrees/W2-88a/.gov-runtime/scratch/lead/TESTS-READY naming the merge commit.
