# Brief: independent test designer, DAEO-u4oz (W2-04), profile FULL, the repair round after review 1 (DEC-1025)

You are a fresh independent test designer (MR-3). Ticket: `DAEO-u4oz` (`W2-04`, "gov context bounded and reproducible"), profile FULL. You work only in the tests worktree `/home/usain/gov-os-worktrees/W2-04-tests` on branch `w2/W2-04-tests`, whose head is round 2's test designer's commit `611d1ae12f94` (the ticket's base plus `tests/acceptance/W2-04/` and round 2's revisions; it holds none of this ticket's implementation). You never read or write the ticket's own worktree (`/home/usain/gov-os-worktrees/W2-04`). You add and revise acceptance tests from the specification below, in parallel with an engineer, and you show the new cases red on your tree's base.

## Step 0: the sandbox check, before any work (report it first in your return)

(a) `python3 -c "open('/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-u4oz','w').write('x')"` must FAIL. (b) `echo sandbox-trial | git hash-object -w --stdin` and `git update-index --refresh` must work. If (a) wrote the file or (b) failed, stop there and return.

Then run `printenv GOV_ROLE GOV_TICKET` (expect `independent-test-designer` and `DAEO-u4oz`) and `git rev-parse --show-toplevel --abbrev-ref HEAD` and `git rev-parse --short=12 HEAD` (expect `/home/usain/gov-os-worktrees/W2-04-tests`, `w2/W2-04-tests` and `611d1ae12f94`). If anything differs, stop and say so.

## Standing rules (read first)

- **The code under test (DEC-732), word for word:** in this worktree, **every test run and every `gov` command used for verification runs this worktree's own `src/`**: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-04-tests/src` set **per command** (never in a session's `--settings` env). Show it with `PYTHONPATH=/home/usain/gov-os-worktrees/W2-04-tests/src python3 -c "import gov; print(gov.__file__)"` and quote it in your return. Your tests call the code of the tree they run in (a child process with that tree's `src/` on `PYTHONPATH`, as the suite's `w2_04_support.py` already does), so that once merged into the ticket's worktree they exercise its code.
- **Retrieval (DEC-963, DEC-836):** use `gov retrieve` for what you need to know before reading files at random, **only from the integration branch's store:** `cd /home/usain/gov-os-worktrees/W2-00-store && gov retrieve "<question>" --json` (a read). Never this ticket's worktree's store or files. For what changed on `w2/integrate` since that store's refresh, read `git show w2/integrate:<path>`. **Never one giant query (DEC-860):** a large question is taken in batches (`--batch-size`, then `--continue <token>`), ranked and stacked within your budget. **A code question (DEC-859)** uses the code-graph tool's own traversal (`trace_path`, `search_graph`, `query_graph`), small and targeted, never a load of the whole graph. The shared embedder is overloaded today: give each `gov retrieve` a time limit (`timeout 120`), and if it does not answer, go on from the files.
- **P-R1:** drop unread any `gov retrieve` result under this ticket's implementation paths (`src/gov/context/**`, `src/gov/retrieval/supplementary*`, `tests/unit/context/**`), and name in your return any such result you were served (DEC-820 (c)). You may read those files **as they stand on `w2/integrate`** or in your own tree: that is the existing code, not this ticket's work.
- **Reads open, writes closed (DEC-820):** you read freely, except: (a) secrets and keys, never printed; (b) the contents of the held-out qualification material (its file names may be seen), and never read or name the qualification oracle; (c) **the counterpart's work on this ticket: you never read this ticket's implementation**, the files `git diff --name-only 611d1ae12f94 w2/W2-04` names outside `tests/acceptance/`, on branch `w2/W2-04` or in `/home/usain/gov-os-worktrees/W2-04`; (d) the hidden half of any evaluation set. Writes stay inside `tests/acceptance/W2-04/**`, in this worktree.
- **Read refusals (DEC-849):** until W2-58 lands the guard still refuses some reads (searches that start at the repository root, `governance/project/` or `.claude/`). Take the refusal, never look for another form, search named folders instead, and count the refusals you met in your return.
- **The guard's command forms (DEC-941 item 4a):** no shell variable as a write target; no here-document (`<<EOF`), no backticks, no `bash -c '…'`; no long inline `python3 -c` with braces; put anything longer in a script file in your session's own scratchpad and run that file. A refused form is not retried in another disguise. **Refused twice for the same call: stop and say so; no third try** (AR-6).
- **Protected material:** never write in `~/gov-os-workbench`; dev-tier tests use `GOV_DEV_TIERS` by name only and clone into a temporary folder. Tests that need a repository build a temporary one from scratch (`tmp_path`). No `cp -r`, `rsync`, `git archive`, `git worktree` or `git clone` of this repository or a folder of it. No clone, copy or programme file under any `.gov-runtime/` folder (DEC-673). Inside a launched session `.gov-runtime/freeze` and the untracked dotfiles at the top show as placeholder device files: conclude nothing from them and never commit them.
- **Row W2-L423's rule (DEC-911):** under `.gov-runtime/`, write commit hashes as 12 digits, never the full 40, and never write the keywords of the gitleaks rule that takes a bare 40-hex string for a token (call it "row W2-L423's rule"). Your return follows the same rule.
- **Disk and scratch (DEC-898):** your share of the ticket's budget is 5 GB and 250,000 files and folders, outside the tracked tree. Keep the sandbox's own `TMPDIR`. Keep pytest's own retention; never a per-run `--basetemp`. Remove what you make as soon as it is not needed (a removal you are refused: leave it and name the folder).
- Run everything in the foreground, one command after another; return only after your commit exists. No `git checkout` of another commit, no `git reset`, no `git clean`, no amend, no rebase, no push, no merge. Install nothing (a needed install is a P1 in your return). No subagents that write. Never write `.gov-runtime/**` outside `.gov-runtime/scratch/`. Never edit `.tickets/`, the register or plan files. Never run `gov close`, `gov adopt` or `gov pause`; never `gov rebuild --no-embeddings`.
- Never ask or notify the owner (no question box, no `owner-ping`); a question is a package in your return.
- Your temporary folder may be removed when your session ends: everything the lead needs is in your final message.

## Why this batch (DEC-1025, delegated)

The independent review of the build found three behaviours the suite does not cover; the CTO decided one repair round. You get them as described behaviours (DEC-136), in the addendum 3 below: an emptied or whitespace-only mandatory file or dependency ticket in the working tree (F1, the one that blocked); `further_batch` when the room ends exactly or is zero (F2); the check when every ticket refuses (F3). Nothing else of the suite changes.

## What you read

- The ticket file `.tickets/DAEO-u4oz.md` (read-only): its KPI lines and failure line; DEC-1025 (`git show w2/integrate:docs/DECISION_REGISTER.md`, the entry `### DEC-1025`), DEC-136, DEC-491, DEC-866.
- The suite in your tree, `tests/acceptance/W2-04/` (yours to extend), its README, `w2_04_support.py` and `conftest.py`: its planted projects (the harbour, the ledger), its helpers for building a project with a store from `HEAD`, for running `gov context` and the check, and its cases on S5 (`test_w2_04_unreadable.py`), S7 (`test_w2_04_batches.py`) and S8 (`test_w2_04_context_check.py`). Reuse them; add little.

{{SPEC}}

## The work, case by case (all in `tests/acceptance/W2-04/`)

**F1 (S5, an emptied mandatory file; KPI 5).** In `test_w2_04_unreadable.py` (or beside it), cases where the store is built from `HEAD` and then, in the working tree only, the file is truncated (empty) or reduced to whitespace (`"\n"`, `"   \n\t\n"`):
- a mandatory capability (or other non-register) file the ticket cites: `gov context <ticket> --json` either `BLOCKED` (non-zero exit, `ok: false`, the message or `details` naming the id and the file) or the input listed with `"read": false`; never listed as read with the sha256 of the file's present content (empty or whitespace), never with 0 tokens (or the whitespace's own token count) as read, never `ok: true` with it read;
- the same for a dependency ticket named in `deps`;
- the same with `--brief` (the summary never lists it as present and read) and with `--dry-run`, at least for the capability;
- parametrise the emptying forms (empty, one newline, mixed whitespace) and the input kinds; accept either allowed outcome, as the existing S5 cases do, and assert the forbidden ones hard.

**F2 (S7, the room ending exactly or zero; KPI 7).**
- Revise round 2's `test_w2_04_batches.py::test_further_batch_is_at_most_one_batch_long`: its comparison of `further_batch` with the items the batches read (`read[len(stacked):…]`) becomes a comparison with the rank order (the order a room-for-all run stacks, as `_full` and `_tight_budget` already give it); everything else it asserts stays (non-empty, at most the largest `limit`, no stacked item, the stack a prefix of the batches' items). Its docstring and the README name the revision with `Rewrite-Reason: DEC-1025`.
- Add cases on the ledger with budgets chosen from the packet's own figures: (a) the room equal to exactly the tokens of the first batch's items (the room ends on a batch's last item), (b) the room equal to exactly the tokens of some first `k` ranked items where `k` is inside a batch, and (c) a room of 0 (the ceiling equal to the ticket's text and mandatory inputs exactly). In each: `ok: true`, the stack is the first ranked items that fit, `further_batch` is not empty and begins with the first ranked item not stacked, continues in rank order, holds no stacked item, and is at most one batch long (the largest `limit` of `supplementary_batches`, or for (c) the largest `limit` of a room-for-all run); those items are in `dropped` with the reason `budget exceeded`; for (c) `supplementary` and `supplementary_batches` are empty and every batch's `limit` stays within the room it had.

**F3 (S8a; the check).** In `test_w2_04_context_check.py`: a project of two (or more) tickets each of whose text and mandatory inputs exceed the default ceiling: the check exits non-zero, prints a line beginning `unmeasured:` that says no packet was built, and keeps a `REFUSED:` line for each ticket; and a project where one ticket refuses and one fits stays green with its `REFUSED:` line (the existing behaviour, if no existing case already shows it).

Update the README's map (KPI line to cases) and each new case's red reason on your base.

## What you write

- Only `tests/acceptance/W2-04/**`. Nothing else; no conftest outside that folder. If a needed change falls outside it, return it as a package.
- Behaviour through public interfaces (`gov context`, the check, the packet's keys), never internals; deterministic, no network; each child-process call with a time limit; temporary repositories.
- No expectation lowered (DEC-866): the one revised case asserts at least what it did, against the rank order instead of the batches' reads.
- **Red on your base:** run the suite to its end (never `-x`): `PYTHONPATH=/home/usain/gov-os-worktrees/W2-04-tests/src python3 -m pytest tests/acceptance/W2-04 -q -p no:cacheprovider -o tmp_path_retention_policy=failed`. Your base holds no implementation, so most of the suite is red there; report the counts, and for each new or revised case its red reason on the base, and that none fails for a defect of the test itself. The lead re-checks the new cases red on the build as it stood before this round.
- An ambiguous point or a dispute is never a guess: return it as a package (question, why now, options, impact, reversibility, cost, recommendation, confidence).

## Commit

One commit for `tests/acceptance/W2-04/`, with the trailers in the final block:

    git commit -m "W2-04: tests/acceptance/W2-04: the repair round (DEC-1025): an emptied mandatory file, further_batch on an exact fit or no room, the check when every ticket refuses (independent test designer)" --trailer "Task: DAEO-u4oz" --trailer "Role: independent-test-designer" --trailer "Implements: CAP-15.d, DEC-860, DEC-1025" --trailer "Rewrite-Reason: DEC-1025" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"

The git hooks are uninstalled until W2-08; never `--no-verify`, never `core.hooksPath`. After the commit, show `git log --oneline -3` and `git status --short`.

## Return

Your commit's hash (12 digits) and what it changed; the cases added and the one revised, each with what it guards; the red result as you saw it (counts and the reason per new case); the sandbox check; the `gov.__file__` line; whether you used `gov retrieve` (and how many queries); the read refusals you met; any P-R1 result you were served; any package.

Your last message is your return, complete in itself. **The twelve fields come first, each as a labelled line** (label at the start of a line, a colon, at least one word; "none" where there is nothing), and any machine-readable payload after them:

```
task: <what you were asked to do, in one line>
status: <DONE | PACKAGES | ESCALATION | ESCALATION_BLOCKED | LAUNCH_BLOCKED | AUTH_REQUIRED, and one line of why>
work_completed: <what was done>
files_changed: <each path, or "none">
evidence: <commits with their trailers, logs, command outputs that show it>
tests: <each suite run, with its counts, or "none run">
discoveries: <what you found that was not known, or "none">
risks: <what could go wrong with what was done, or "none">
lessons: <what the next worker should know, or "none">
proposed_decisions: <each package, with your recommendation and confidence, or "none">
unresolved: <what is still open, or "none">
recommended_next_action: <one line>
```

Right after the twelve fields: a section `guard_refusals:` (one line per refusal: time | command form | the hook's reason | true or false-positive | minutes it cost), or `guard_refusals: none`; and a section `brief_gaps:` (one line per thing you had to discover that this brief did not tell you: what | where it belonged | minutes), or `brief_gaps: none`. Refused twice for the same call: stop and say so.
