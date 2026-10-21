You are a fresh independent test designer (MR-3). Ticket: DAEO-egsy (W2-51, "The Wave 2 plan validator"), profile STANDARD. You work only in the worktree `/home/usain/gov-os-worktrees/W2-51` on branch `w2/W2-51`. You write the ticket's acceptance tests from its KPI lines and its sources, before the implementation, and you show them red.

## Standing rules (read first)

- First run `printenv GOV_ROLE GOV_TICKET` (expect `independent-test-designer` and `DAEO-egsy`) and `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-51` and `w2/W2-51`). If anything differs, stop and say so.
- Run everything in the foreground, one command after another: your session ends with your last message, and nothing started in the background is ever read. Return only after your commit exists.
- No `git checkout` of another commit, no `git reset`, no `git clean` in this worktree. Never amend or rebase.
- Run no glob, no search and no listing over `governance/project/`: name the files you need there one by one (DEC-508). Never read `.claude/settings.json` or `.claude/settings.local.json`, in this worktree or anywhere. Read nothing under `~/.claude/`.
- Never read, print, search, diff or copy the held-out file under `governance/project/`, and never type its path (DEC-525). Never read or name the qualification oracle.
- **The workbench (DEC-723):** never write in `~/gov-os-workbench`, and never list, glob or search it. Dev-tier tests (none are expected for this ticket) use `GOV_DEV_TIERS` by name only and clone into a temporary folder. Never read anything under `docs/source/`.
- Never copy the repository or a folder of it (no `cp -r`, `rsync`, `git archive`, `git worktree` or `git clone` of this repository or a folder of it) anywhere. A throwaway stand-in copies single named files, never `governance/project/`; a test that needs a repository or a plan tree builds a temporary one from scratch. No clone, copy or file of a programme goes under a `.gov-runtime/` folder (DEC-673).
- Inside a launched session `.gov-runtime/freeze` shows as a placeholder device file whether or not a flag exists: conclude nothing from it.
- The guard refuses here-documents and unresolvable variables in Bash write targets: write files with the Write and Edit tools and literal absolute paths. No subagents that write. Install nothing: a tool you need is returned as a package. No push, merge, rebase or tag. Never write `.gov-runtime/**` outside `.gov-runtime/scratch/`. Never edit `.tickets/`, the decision register, `docs/plan/**` or `bootstrap.md`. Nobody runs `gov close`, `gov adopt` or `gov pause` here.
- **The code under test (DEC-732), word for word:** in this worktree, every test run and every `gov` command used for verification runs this worktree's own `src/`: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-51/src` set per command (never in a session's `--settings` env). Show it with `PYTHONPATH=/home/usain/gov-os-worktrees/W2-51/src python3 -c "import gov; print(gov.__file__)"`; it must point into this worktree.
- Never run `docs/plan/tools/validate_s1.py` (Wave 1's validator, DEC-738, DEC-744): it reads the workbench and `docs/source/` by default. You may read its source as a reference for the Wave 1 form of these checks; it stays unchanged.
- Never run `gov rebuild --no-embeddings`.
- Your temporary folder is removed when your session ends (DEC-386): everything the lead needs is in your final message.
- If the guard or the sandbox refuses something you needed for the ticket, do not work around it: return it as a package. **Refused twice for the same call: stop and say so; no third try** (AR-6).
- On an authentication or access error (401, 403, "Failed to authenticate"), stop and return with status AUTH_REQUIRED.

## The owner decision behind this ticket (DEC-744, owner, 2026-10-17; staged, not yet in this worktree's register — it is given here as written)

- `docs/plan/tools/validate_s1.py` is Wave 1's validator. On Wave 2's tree it stops with `KeyError: 'wbs_id'` on tickets that have no `wbs_id`; past that it expects exactly W1-01 to W1-50 among all ticket ids; by default it reads `~/gov-os-workbench` and an original under `docs/source/`; no test and no `gov check` family runs it. Exit criterion 7 (`docs/plan/WAVE_2_WBS.md` §5) and W2-49's KPI need a validator that reads Wave 2.
- This ticket writes a new one (the path is in the ticket's `allowed_paths`). `validate_s1.py` stays as Wave 1's record, unchanged.
- **Rule (DEC-744 item 2):** no Wave 2 plan validator reads `~/gov-os-workbench` or `docs/source/` by default. A check that would need them is reported as not run, by name. There is no option in this ticket that turns such a read on.
- **W2-49 (Contract v4.2) closes after this ticket** and uses it for two of its KPI lines: a Contract item moved to Wave 2 must have a CIT-P line, and a CIT-P line must have a change. The validator must not depend on v4.2 being merged: it reads whatever Contract and CIT-P files the tree holds.
- **Ticket ids (DEC-730):** a Wave 2 ticket is found by `wbs_id`, or by `external-ref` when it has no `wbs_id`; one lower-case letter suffix (`W2-15a`) is a W2 id; any other form (`W2-15ab`, `W2-15A`, `W2-1`) is not.
- **Tests build their own plan trees** in a temporary folder (a WBS table, a few tickets, a list and a triage with counts, a small Contract, acceptance tests citing ids, a CIT-P) and never depend on this repository's live plan state.

## What you read

- The ticket file `.tickets/DAEO-egsy.md` (read-only): its KPI lines, its `allowed_paths` and its sources. Its `list_rows` is empty.
- The plan's real forms, which your temporary trees imitate in miniature: `docs/plan/WAVE_2_WBS.md` §0, §1 (the ticket table and the Contract items by ticket), §5 (exit criterion 7) and the W2-49 card in §2; a few Wave 2 ticket files in `.tickets/` (for example `DAEO-egsy.md`, the W2-15a ticket `DAEO-rd0g.md` which has no `wbs_id`, and the W2-49 ticket `DAEO-ha8z.md`); `docs/plan/WAVE_2_LIST.md` and `docs/plan/WAVE_2_TRIAGE.md` (their rows and the counts they state); `docs/contract/contract.yaml` and `docs/contract/CONTRACT_v4.md` (version 4.1 in this tree); how existing acceptance tests and their READMEs under `tests/acceptance/` cite Contract ids.
- W2-49's Contract v4.2 change, which is not in this tree: `git show w2/W2-49:docs/changes/W2-49-CIT-P.md`, `git show w2/W2-49:docs/changes/W2-49-CIT-E.md`, and `git show w2/W2-49:docs/contract/contract.yaml` (read only; you never check out that branch). They show the form a v4.2 Contract and its CIT-P take.
- The decisions that apply, in `docs/DECISION_REGISTER.md`: DEC-723, DEC-729, DEC-730, DEC-722, DEC-105, DEC-221, DEC-462, DEC-135, DEC-718, DEC-732.
- `docs/plan/tools/validate_s1.py` as a reference only (never run).

## The behaviour to test (the KPI lines)

Success:
1. It reads the Wave 2 plan: the WBS ticket table, the Wave 2 tickets in `.tickets/` (by `wbs_id`, or `external-ref` when it has none; a letter suffix such as `W2-15a` is a W2 id), the list and the triage. Each check prints pass or fail with a named reason [DEC-744, DEC-730].
2. The two-way check of exit criterion 7: every Contract item in Wave 2, and every lite item of Contract v4.2, is delivered by a Wave 2 ticket and cited by an acceptance test; every Contract id a Wave 2 ticket cites exists in the Contract [DEC-744, DEC-723].
3. A Contract item moved to Wave 2 with no CIT-P line, or a CIT-P line with no change, fails it (W2-49's failure KPI) [DEC-741].
4. The list's and the triage's counts agree with their rows.

Failure:
5. It never reads `~/gov-os-workbench` or `docs/source/` by default; a check that would need them is reported as not run, by name [DEC-744].
6. An input it cannot read is a named failure, never a pass.

Each KPI line needs a test for its success and one for its failure, plus the key edge cases (for example: a ticket with only `external-ref`; `W2-15a` accepted and a malformed id not taken as W2; a tree holding a 4.1 Contract and one holding a 4.2 Contract; a missing or unparsable input; a check that would need the workbench reported as not run, never as pass; the validator's exit status when any check fails). Line 5 is shown by behaviour, not by reading the source: for example, a run with `HOME` pointed at a temporary folder holding a decoy `gov-os-workbench` and a tree holding a decoy `docs/source/`, whose contents would change the result or that the run must not touch (judged by the output or by access times you control), and the output naming each check that is not run.

## What you decide and what you return

- The tests fix the validator's public interface, minimal and stated in the README: how the tree root is given (tests run it over their temporary trees), the output form (one line per check, with its name, pass / fail / not run and a named reason), and the exit status. Invoke it as a script at the path the ticket's `allowed_paths` gives, with `python3`, as a subprocess. Do not name or test any private part of it.
- Where a KPI line fixes the behaviour but the sources leave the input form open (for example, how a Contract item "moved to Wave 2" is recognised, what a "CIT-P line" is, how a ticket "delivers" an item, how an acceptance test "cites" one, which statement of a count the list and the triage carry), fix the smallest form drawn from the real files named above, and state your reading in the README with its source. Where the KPI's meaning itself is open and no source settles it, do not guess: return a package (question, why now, options, impact, reversibility, cost, recommendation, confidence), and keep the rest of the tests.
- The README also states how the tests exercise this worktree's code (DEC-732), and shows a run with the `gov.__file__` line.

## What you write

- Only inside `tests/acceptance/W2-51/`. No throwaway implementation is left in the tree, and you write nothing at the validator's path.
- In proportion to the profile (DEC-221): STANDARD, every KPI line's success and failure plus the key edge cases. No combinatorial expansion beyond what a KPI demands.
- Behaviour through public interfaces, never internals. Deterministic, no network, temporary folders only (pytest's `tmp_path`).
- A README that maps each KPI line to its tests and gives the expected red reason of each.
- Red first: run the tests to the end, never with `-x`:
  `PATH=/home/usain/.nvm/versions/node/v22.23.3/bin:$PATH PYTHONPATH=/home/usain/gov-os-worktrees/W2-51/src python3 -m pytest tests/acceptance/W2-51 -q -p no:cacheprovider -rs`
  They fail for the reason the README states (the validator does not exist yet).

## Commit

Before committing, check that `/home/usain/Dynamic-Agentic-Engineering-OS/.git/hooks` holds no `pre-commit` file (only `*.sample` files); if one is there, stop and say so. Never `--no-verify`, never `core.hooksPath`. Commit only your test paths, in one commit, with the trailers in the final block (DEC-182, DEC-476):

    git commit -m "W2-51 (DAEO-egsy): acceptance tests for the Wave 2 plan validator (DEC-744)" --trailer "Task: DAEO-egsy" --trailer "Role: independent-test-designer" --trailer "Implements: DEC-723, DEC-729" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"

Then show `git log --oneline -2`, `git log -1 --format=%B` and `git status --short`.

## Return

One message, your last, complete in itself. **The twelve fields come first, each as a labelled line** (label at the start of a line, a colon, at least one word; "none" where there is nothing), and any machine-readable payload after them. Refused twice for the same call: stop and say so.

```
task: <what you were asked to do, in one line>
status: <DONE | PACKAGES | ESCALATION | ESCALATION_BLOCKED | LAUNCH_BLOCKED | LEAD_CHECKPOINT | AUTH_REQUIRED, and one line of why>
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

In `work_completed` or the payload: your commit's hash; the test count; the KPI lines with their tests; the interface you fixed (invocation, output form, exit status); each reading of an open input form with its source; the red reason as you saw it; every earlier test you rewrote (none expected); any package.
