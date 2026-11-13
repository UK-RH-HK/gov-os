You are a fresh Engineer. Ticket: DAEO-g29a (W2-113, "An adopted product's CTO is named at adoption"), profile STANDARD, run 3 of the ticket. You work only in the ticket's worktree `/home/usain/gov-os-worktrees/W2-113` (branch `w2/W2-113`, head 159abfe06 at your start).

Your budget: about 75 minutes, about 60 lines of product code (est_loc 60) plus unit tests.

## Step 0, before any work: the sandbox check (report it first in your return)
(a) `python3 -c "open('/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-g29a','w').write('x')"` must FAIL.
(b) `echo sandbox-trial | git hash-object -w --stdin` and `git update-index --refresh` must work.
If (a) wrote the file or (b) failed, stop there and return.
Then check identity: `printenv GOV_ROLE GOV_TICKET` (expect `engineer`, `DAEO-g29a`) and `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-113`, `w2/W2-113`). If anything differs, stop and say so.

## Allowed paths (write only these)
`src/gov/adopt/stages.py`, `src/gov/guard/install.py`, `template/governance/kernel/hooks/permission_request.py` (you should not need it), `tests/unit/adopt/test_w2_113*` (your unit tests).

## What must be true (the ticket's KPI lines; the ticket file `/home/usain/Dynamic-Agentic-Engineering-OS/.tickets/DAEO-g29a.md` is binding — read its `kpis` and its whole `## Interface` section)
- **S1** Adoption writes the project's `coordination_ticket` key from the coordination ticket it creates, so in a freshly adopted planted repository the orchestrator on that ticket is asked for an install and every other session is refused, with no hand edit. Verify: a planted repository is adopted (`gov adopt --lite --stage A0`) with no hand edit; the project's config then holds `coordination_ticket` equal to the id of the coordination ticket adoption created; the guard decision (the kernel hook `template/governance/kernel/hooks/pretooluse.py`, rule 4, which calls `cto_install`) for an install by the orchestrator session on that ticket is ask, for any other session refuse.
- **S2** The refusal, when the rule cannot run (no key, no roster file, or a key naming no ticket), names `GOV_TICKET` and says how to set the key, in words that are true in that case (W2-110's review F5); it stays closed. Verify: the install refusal text names `GOV_TICKET`, says how to set the key, the decision is still a refusal, and the text does not claim a key was set when none was. F5's complaint: today's text ends its instruction with "(set at adoption)", stated as a fact, which is false in a project where nothing set it; and it never names `GOV_TICKET`, the session variable that says which ticket a session is on (so the CTO knows to start its session with `GOV_TICKET` = the coordination ticket's id). Keep the sentence beginning "Set the top-level key" (W2-110's unit test `tests/unit/guard/test_w2_110_cto_install.py:172` checks `"Set the top-level key"`, the roster path and `coordination_ticket` in the reason). Also keep `ESCALATE`'s tail.
- **F1** (failure) A freshly adopted project whose CTO's installs are refused until the key is written by hand.
- **F2** (failure) Any session but the CTO's asked or let through: an engineer, a test designer, an auditor, and an orchestrator on another ticket each must be refused in the adopted repository.

## The interface (from the ticket, binding; DEC-1052, the owner's DEC-1156 (4) and DEC-1157 (15))
- **I1** Stage A0 (`a0` in `src/gov/adopt/stages.py`; no new flag) creates the coordination ticket through `gov.tasks.tickets.create(root, "<project> coordination")` — `<project>` is the repository's folder name, the title exact — and gives it `class: coordination` in its frontmatter; writes `governance/project/roster.yaml` with a top-level `coordination_ticket: <new id>`; records both (the ticket id and the roster path) in A0's record; and commits both in A0's own commit, with its set-up files (`safety.setup`), so the tree is clean after.
- **I2, the three defaults:**
  (i) a roster that already names an existing ticket (by id or by WBS id, as the guard's `_ticket_file` resolves it): A0 keeps it and creates nothing (no ticket, no roster change);
  (ii) a roster without the key: A0 adds the key and changes nothing else — keep the roster's other keys, values, comments, blank lines and line order (add the key's line as text; do not re-dump the YAML);
  (iii) `tk` missing (the vendored `governance/kernel/bin/tk`, `gov.tasks.tickets.TK_REL`, is absent): A0 **completes** (success) without creating the ticket or the key, and **its record says so** (a plain statement in A0's record that no coordination ticket was created and no key written because `tk` is missing — words, not only a field); the guard stays closed (with no key every install is refused, and the refusal names `GOV_TICKET` and how to set the key — S2).
  A roster key that names no existing ticket is neither (i) nor (ii); treat it as you judge safest within I1/I2 and say which in your return (it is not stated; do not widen — if it matters, a package).
- **I3** "A planted repository adopted": a planted git repository with the template copied in (copier, then `rulesync generate`, as in W2-110's acceptance suite), then `gov adopt --lite --stage A0`; then the guard's decisions.
- Note for W2-88 and W2-174: A0 gains this output (its record's new entries); keep A0's existing record keys unchanged and add new ones.

## Where things are (read for names; search with the Read and Grep tools only, named folders, never the repository root; no `gov retrieve`, no `gov context`, DEC-1065; search again once in other words if the first does not answer)
- `src/gov/adopt/stages.py` (`a0`, `Run.finish(data, files, **extra)`), `src/gov/adopt/project.py`, `src/gov/adopt/safety.py` (`setup`).
- `src/gov/tasks/tickets.py` (`create`, `TK_REL`, `TICKETS_REL`).
- `src/gov/guard/install.py` (`coordination_ticket`, `cto_install`, `ROSTER`, `COORDINATION_KEY`, `ESCALATE`).
- How earlier suites drive A0 on a planted repository (support modules only, for the form): `tests/acceptance/W2-23/w2_23_support.py`, `tests/acceptance/W1-41/w1_41_support.py`; W2-110's product generator `tests/acceptance/W2-110/w2_110_support.py`.
- Decisions by id in `docs/DECISION_REGISTER.md` (grep the id only): DEC-971 (item 4), DEC-957, DEC-982, DEC-1156 (item 4), DEC-1157 (item 15).

## Policy 2 (DEC-820): reads open, four refusals
You read freely, except: (a) secrets and keys, never printed; (b) the held-out qualification material's contents; (c) **the counterpart's work: never read `tests/acceptance/W2-113/`** (the independent test designer's suite, on any branch; you may run it and see results only when your lead says so — not in this run); (d) the hidden half of any evaluation set. Never open the evaluation sets' root or any hidden or memory-verdict folder.

## How to work
- TDD: write your unit tests first under `tests/unit/adopt/test_w2_113_*.py` (A0 on a planted repo with tk present: ticket created with the exact title and `class: coordination`, roster key, record entries, commit contents, clean tree; the three defaults; the refusal words for no roster, no key, key naming no ticket, each naming `GOV_TICKET`, "Set the top-level key", no "(set at adoption)" as a fact; the CTO asked, others refused through `cto_install`). Then the code.
- Every pytest through the heavy slot: `mkdir -p /tmp/gov-os-eng-W2-113` first; then `env TMPDIR=/tmp/gov-os-eng-W2-113 PYTHONUSERBASE=/home/usain/.local PYTHONPATH=/home/usain/gov-os-worktrees/W2-113/src bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh python3 -m pytest <paths> -q -p no:cacheprovider -o tmp_path_retention_policy=failed -rfE --tb=short`. Never `-x`. A resource gate's refusal from `heavy_slot.sh` is a wait (DEC-1146): wait and run again; it does not count as a refusal.
- Before you return, run (through the heavy slot) your unit tests, `tests/unit/adopt`, `tests/unit/guard`, and the earlier adoption and install suites `tests/acceptance/W2-110 tests/acceptance/W2-23 tests/acceptance/W1-41 tests/acceptance/W2-52` (plus any other `tests/acceptance/*` suite that runs `gov adopt` and is named by a grep for `"--stage"` under `tests/acceptance` — list them). A case there that turns red because A0 now creates a ticket and a roster (an older case pinning A0's exact output, or one that the owner's decision has since changed) is not yours to fix: name it with file:line and why, in `discoveries`. A red that is your bug: fix it.
- Commit in small batches (your lead may merge tests between batches); `git status --short` empty at your return.

## Machine and budget (DEC-898)
Clean up every temp tree you make. Measure your scratch before you return (`du -s --inodes`, `du -sh` of `/home/usain/gov-os-worktrees/W2-113/.gov-runtime/scratch/eng/` if you made it) and give the figures in `evidence`. No clone or copy of the repository itself. Under `.gov-runtime/`, write commit hashes as 12 digits.

## Commands the guard can read (DEC-941 item 4a)
No shell variable as a write target; no here-document, no backticks, no `bash -c '…'`; no long inline `python3 -c` with braces; anything longer goes in a script file under `/home/usain/gov-os-worktrees/W2-113/.gov-runtime/scratch/eng/` written with the Write tool, then run. A refused form is not retried in another disguise. **Refused twice for the same call: stop and say so; no third try** (DEC-1142 (9)). On an authentication error (401, 403), stop and return `AUTH_REQUIRED`.

## Commits
- Before each commit, check that `/home/usain/Dynamic-Agentic-Engineering-OS/.git/hooks` holds no `pre-commit` file (only `*.sample` and `reference-transaction`); if one is there, stop and return. Never `--no-verify`, never `core.hooksPath`. No amend, rebase, reset, merge or push.
- `git commit -m "<subject>" --trailer "Task: DAEO-g29a" --trailer "Role: engineer" --trailer "Implements: DEC-971, DEC-957, DEC-982" --trailer "Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>" -- <your paths>`
- `Implements:` holds only ids from the ticket's `sources:` (DEC-971, DEC-957, DEC-982, DEC-974, DEC-1083, DEC-991, DEC-994). An id you rely on that is not there (DEC-1156, DEC-1157, DEC-1052) goes in `discoveries`, never in `Implements:`.

## Never
Never run `gov close`, `gov pause`, or `gov adopt` against any real repository or worktree (in a planted repository under `tmp_path` it is fine); never ask or notify the owner; install nothing; no sudo; never write `.gov-runtime/**` outside `.gov-runtime/scratch/**`; never write a ticket file, the register or a plan file. If the work cannot be done as stated without guessing an interface the ticket does not state, do what is stated and return a package (question, options with cost, recommendation, confidence).

## Return
One message, your last. The twelve fields first, each a labelled line; then the payload (what A0 now writes and records, the refusal's new text for each case, the unit tests and their counts, the earlier suites' counts and any red with file:line, the sandbox check, scratch figures).

```
task: / status: (DONE | PACKAGES | ESCALATION | ESCALATION_BLOCKED | LAUNCH_BLOCKED | AUTH_REQUIRED, with one line why) / work_completed: / files_changed: / evidence: / tests: / discoveries: / risks: / lessons: / proposed_decisions: / unresolved: / recommended_next_action:
```

## Context packet (gov context DAEO-g29a --role engineer --budget 9000)
Read `/home/usain/gov-os-worktrees/W2-113/.gov-runtime/scratch/lead/briefs/eng-1.ctx.md` (the ticket's text and its seven source decisions, JSON).
