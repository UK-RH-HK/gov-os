# Your assignment
You are a fresh orchestrator session. Your role's rules are in your system prompt (template `role-lead`); this brief gives this assignment's facts.
Ticket DAEO-6y0x (W2-93), profile STANDARD. Objective: W2-81's held-out half: hidden questions and planted-problem variants per synthetic repository, by an independent session. Card: the WBS's proposed companion "W2-81's held-out half" (§2), filed as MEMORY-SPEC-MAP gap 6, resolved by the owner in DEC-957. Without it W2-81's and W2-88's question figures stand on the visible half only.

## Where you work
| what | path |
|---|---|
| your tree (write here only) | /home/usain/gov-os-worktrees/W2-93 |
| branch | w2/W2-93 |
| allowed paths | tests/acceptance/W2-93/**, docs/probes/DAEO-6y0x/**, fixtures/evaluation/adoption-proving-ground/validate_hidden.py, fixtures/evaluation/adoption-proving-ground/hidden/**, tests/acceptance/W2-81/w2_81_run.py, tests/acceptance/W2-81/test_w2_81_runner.py |
| ticket file (read-only) | /home/usain/Dynamic-Agentic-Engineering-OS/.tickets/DAEO-6y0x.md |
| your scratch | /home/usain/gov-os-worktrees/W2-93/.gov-runtime/scratch/ |

## What must be true (KPI lines and how each is checked)
| id | line | verify |
|---|---|---|
| S1 | At least 10 hidden questions per synthetic repository, each with its gold answer, gold sources and forbidden citations, in the form W2-81's README states | `validate_hidden.py` on a planted stand-in hidden folder prints, for each repository, a question count of 10 or more and exits 0; a planted folder with 9 for one repository is refused; each planted question holds the fields the README states [DEC-957, DEC-941, DEC-828] |
| S2 | At least one hidden planted-problem variant per kind that the visible builders do not produce, so an adoption tuned to the visible generator is caught | `validate_hidden.py` on a planted stand-in set prints, for each kind of planted problem the visible builders do not produce, the number of hidden variants per repository; a planted set missing one kind is refused [DEC-941] |
| S3 | Written by a session independent of the sessions it measures; nothing hidden written outside the hidden folder; no question or answer quoted in a commit message, a return, a log or a ticket note | the delivery's run record names the walled writer's run (`20261112T185824Z-adoption-proving-ground-r1`) and its launch log the approved brief's sha256 (the sets root is outside git, so no commit carries it); `validate_hidden.py --sets-root` finds the hidden files only under the hidden folder; a grep of commit messages, return, log and ticket notes for a planted unique question word finds 0 hits [DEC-820 (d), DEC-845, DEC-873] |
| S4 | Every gold answer is held by the repository the builder builds, checked on a built copy | `validate_hidden.py` on a built copy of a planted stand-in repository: every gold answer is found in it; a planted answer the built copy does not hold is refused naming its id [DEC-828] |
| S5 | The hidden half proves its own data valid with an automatic check, `validate_hidden.py`, written by the ticket's independent test designer (never the walled writer), run by the CTO on the delivered hidden half before it is used, printing counts and ids only, and recorded: every forbidden ("must not cite") file names a file of the repository the builder builds, checked on a built copy; every kind of planted problem the visible generator does not produce has at least one hidden variant per repository; anything it cannot read refuses (fail closed); W2-81's files are not touched | planted stand-in cases: a must-not-cite file absent from the built copy refuses, a kind with no variant refuses, an unreadable file refuses (non-zero exit); `git diff` shows W2-81's files untouched except the two paths DEC-1144 (6) gives this ticket (`--sets-root`); the delivered hidden half has a recorded run of the check (counts and ids only) [DEC-1010 item 4] |
| S6 | The W2-81 runner (`tests/acceptance/W2-81/w2_81_run.py`) and `validate_hidden.py` each take `--sets-root <root>` and find the hidden half under it, so neither the CTO nor a session names the hidden folder on a command line; the runner's `--hidden <folder>` stays for a direct call; both written by the independent test designer | a planted stand-in sets root holding a stand-in hidden half: the runner and `validate_hidden.py` given only `--sets-root` find and read it, and a root without one exits non-zero naming the missing folder [DEC-1144 (6), DEC-1143 (4)] |
| F1 | A hidden question or answer readable by a measured session by a route an honest agent takes in ordinary work. | a planted stand-in hidden file: a read, a grep and a `git log` from a measured session's sandbox (the guard's path map) are refused or find it 0 times |
| F2 | A question whose gold answer the built repository does not hold. | `validate_hidden.py` on a planted stand-in question whose gold answer the built copy does not hold exits non-zero and names the question id |
Non-goals (do not build, do not test): none
Done when: the DoD lines DOD-1, DOD-2, DOD-3, DOD-4, DOD-5, DOD-6 hold for your part.

## Inputs
- Sources: DEC-957, DEC-941, DEC-828, DEC-820, DEC-845, DEC-873, DEC-1010. Read each by id in /home/usain/Dynamic-Agentic-Engineering-OS/docs/DECISION_REGISTER.md, or ask memory (below).
- What the lead knows of the ground: This is W2-93 (DAEO-6y0x), STANDARD, class C2, run "close": W2-81's held-out half. The owner's DEC-1167 (3): its walled writer delivered on 2026-11-12 (run `20261112T185824Z-adoption-proving-ground-r1`, 60 questions in the evaluation sets' root, outside git); close it in parallel with W2-94. The ticket's Verify lines were fitted to the walled route by the CTO (S3, S5) and its paths gained `tests/acceptance/W2-93/**` and its probe folder.

**What is missing, and what you deliver** (an independent test designer, C2; you never read the hidden half's contents):
1. `fixtures/evaluation/adoption-proving-ground/validate_hidden.py`, as S5 states. It reads the hidden half under `--sets-root <root>` (S6) and checks:
   - every must-not-cite file names a file of the repository the builder builds, checked on a built copy;
   - at least one hidden variant per kind the visible generator does not produce, per repository;
   - anything it cannot read refuses (fail closed).

   It prints counts and ids only, never a question or an answer.
2. `--sets-root <root>` on `tests/acceptance/W2-81/w2_81_run.py`, with its case in `test_w2_81_runner.py` (DEC-1144 (6)). The runner finds the hidden half under the root given, never a named hidden path.
3. `tests/acceptance/W2-93/`: form-only cases on planted stand-in sets (counts, fields, sources exist). They cover each S line's Verify and both F lines: a planted unreadable file, a planted must-not-cite file absent from the built copy, and a planted kind with no variant each refuse (non-zero exit); and a read, a grep and a `git log` from a measured session's role cannot reach a planted stand-in hidden file.
4. `gov accept W2-93` on stand-ins, and the scoped run once (DEC-968). A narrow independent check of the change: a fresh read-only auditor carrying JUDGEMENT.md word for word, with the verdict block; the probe record with the schema's `implementer_session`.
5. Return DONE with the head to land.

The CTO runs `validate_hidden.py --sets-root` on the real delivery himself, records the counts, then lands and closes.

**Walls (hard):** never open, list, grep or print anything under the evaluation sets' root or any hidden folder; your cases use planted stand-ins under your sandbox's `$TMPDIR` only. Never quote a question or an answer anywhere.

Workers launched by `gov launch` write only their sandbox's own `$TMPDIR`. Every pytest through bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh with a TMPDIR outside the repository and outside ~/gov-os-runs (a launched worker: its sandbox's `$TMPDIR`), PYTHONUSERBASE=/home/usain/.local, -p no:cacheprovider -o tmp_path_retention_policy=failed. Waits by pid only. A resource gate's refusal is a wait (DEC-1146). A session refused twice for the same action stops and says so, and never works around a refusal by another tool or form (DEC-1142 (9)). No new ticket. There is no token cap.
none

## Commands (copy them as they are)
| name | command |
|---|---|
| identity | `printenv GOV_ROLE GOV_TICKET` |
| where | `git -C /home/usain/gov-os-worktrees/W2-93 rev-parse --show-toplevel --abbrev-ref HEAD` |
| retrieve | `gov retrieve --root /home/usain/gov-os-worktrees/W2-00-store "{QUESTION}"` |
| context | `gov context DAEO-6y0x --role {WORKER_ROLE}` |
| launch_worker | `bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/launch_worker.sh {WORKER_ROLE} {EFFORT} {BRIEF_FILE}` |
| wait_for | `bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/wait_for.sh {EXIT_FILE}` |
| tests_worktree | `git -C /home/usain/gov-os-worktrees/W2-93 worktree add /home/usain/gov-os-worktrees/W2-93-tests -b w2/W2-93-tests HEAD` |
| merge_tests | `git -C /home/usain/gov-os-worktrees/W2-93 merge --no-ff w2/W2-93-tests -F {MESSAGE_FILE}` |
| accept | `gov accept W2-93 --root /home/usain/gov-os-worktrees/W2-93` |
| rebuild | `env PYTHONPATH=/home/usain/gov-os-worktrees/W2-93/src bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/rebuild_slot.sh /home/usain/gov-os-worktrees/W2-93` |
| lead_verify | `bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/lead_verify.sh /home/usain/gov-os-worktrees/W2-93 W2-93 DAEO-6y0x` |
| tests_worktree_remove | `git -C /home/usain/gov-os-worktrees/W2-93 worktree remove /home/usain/gov-os-worktrees/W2-93-tests` |
| links | `gov links --since {BASE}` |
Ask memory first: outside the sandbox gov retrieve --root /home/usain/gov-os-worktrees/W2-00-store "{QUESTION}" "<which decision governs X | where is Y implemented>"; inside it, the Read and Grep tools [DEC-1065]; grep the register only by id.
Search again once: if the bundle does not answer, or your answer may be incomplete, ask once more in your own, different words; then answer from both bundles with path and lines, or say "not found". Two searches in all; never answer beyond what you read.
No `gov retrieve` in the sandbox, and no `gov context`: a launched worker searches with the Read and Grep tools, and searches again once the same way [DEC-1065].
Every whole-folder pytest run adds `-m "not local_only" -k "not real and not green_here and not time_limit"` and an empty `HOME`: run it as env HOME=/home/usain/gov-os-worktrees/W2-93/.gov-runtime/scratch/empty-home PYTHONPATH=/home/usain/gov-os-worktrees/W2-93/src python3 -m pytest {FOLDER} -q -p no:cacheprovider -o tmp_path_retention_policy=failed -m "not local_only" -k "not real and not green_here and not time_limit" [DEC-1065].
Wait for anything long with bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/wait_for.sh {EXIT_FILE}, one call per 9.5 min; never a hand-written sleep loop.
No merge inside the sandbox: the CTO or your lead merges into your branch outside it; a restore or conflict resolution in `tests/acceptance/` is a test designer's [DEC-1052].

## Forms that work (the guard and the harness accept these)
- Write and edit files with the Write and Edit tools and absolute paths.
- Anything longer than one line goes in a script file under /home/usain/gov-os-worktrees/W2-93/.gov-runtime/scratch/, run with `bash <file>` or `python3 <file>`.
- Use literal paths, never a shell variable or `$(…)` as a write target; name the folder a listing or search starts at.
- The harness allows these headless without asking: Bash, Read, Edit, Write, Grep, Glob. For anything else use a script file as above, or report it; never retry another form.

## Commit (your paths only)
```
git commit -m "{SUBJECT}" --trailer "Task: DAEO-6y0x" --trailer "Role: orchestrator" --trailer "Implements: DEC-957, DEC-941, DEC-828, DEC-820, DEC-845, DEC-873, DEC-1010" -- {COMMIT_PATHS}
```
- `Task:` is the ticket's id (DAEO-6y0x, a `DAEO-…` id), never a W2 id [DEC-182].
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
1. Run the *tests* steps 1 to 3 and, in parallel, the implementer (independent-test-designer) from its brief.
2. Merge the tests when the implementer is between batches; write TESTS-READY.
3. Verify: env PYTHONPATH=/home/usain/gov-os-worktrees/W2-93/src bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/rebuild_slot.sh /home/usain/gov-os-worktrees/W2-93, then bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/lead_verify.sh /home/usain/gov-os-worktrees/W2-93 W2-93 DAEO-6y0x, then wait. Name a red as known only from /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/skip_known.json; re-run a load-sensitive case alone once.
4. Red: a fresh implementer given the failing output only. Three iterations that do not converge: return ESCALATION [DEC-096].
