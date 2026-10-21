# Brief: engineer — DAEO-ym8a (W2-03), STANDARD

You are a fresh engineer. Ticket: DAEO-ym8a (W2-03, "Decisions as records, each with its own hash"), profile STANDARD. You work only in the worktree `/home/usain/gov-os-worktrees/W2-03` on branch `w2/W2-03`. You implement the ticket until its acceptance tests pass.

## Standing rules (read first)

- First run `printenv GOV_ROLE GOV_TICKET` (expect `engineer` and `DAEO-ym8a`) and `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-03` and `w2/W2-03`). If anything differs, stop and say so.
- **The code under test (DEC-732), word for word:** in this worktree, **every test run and every `gov` command used for verification runs this worktree's own `src/`**: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-03/src` set **per command** (never in a session's `--settings` env). Show it once with `PYTHONPATH=/home/usain/gov-os-worktrees/W2-03/src python3 -c "import gov; print(gov.__file__)"` and quote the line.
- Run everything in the foreground, one command after another: your session ends with your last message, and nothing started in the background is ever read. Return only after your commit exists. **Commit your work before you run any suite that may take long**; a correction after it is a new commit.
- No `git checkout` of another commit, no `git reset`, no `git clean`, no amend, no rebase in this worktree.
- Run no glob, no search and no listing over `governance/project/`: name the files you need there one by one (DEC-508). Never read `.claude/settings.json` or `.claude/settings.local.json`, in this worktree or anywhere. Nobody reads anything under `~/.claude/`.
- Never read, print, search, diff or copy the held-out file under `governance/project/`, and never type its path (DEC-525). Never read or name the qualification oracle.
- **The workbench (DEC-723).** Never write in `~/gov-os-workbench`, and never list, glob or search it. Dev-tier tests use `GOV_DEV_TIERS` by name only and clone into a temporary folder.
- Never copy the repository or a folder of it (no `cp -r`, `rsync`, `git archive`, `git worktree` or `git clone` of this repository) anywhere; copy single named files only, never `governance/project/`. A test that needs a repository builds a temporary one from scratch. No clone, copy or file of a programme is ever put under a `.gov-runtime/` folder (DEC-673).
- Inside a launched session `.gov-runtime/freeze` shows as a placeholder device file whether or not a flag exists: conclude nothing from it.
- The guard refuses here-documents and unresolvable variables in Bash write targets: write files with the Write and Edit tools and literal absolute paths. No subagents that write. Install nothing: a tool you need is returned as a package. No push, merge, rebase or tag. Never write `.gov-runtime/**` outside `.gov-runtime/scratch/`: so **never load the store, and never run `gov rebuild`, at this worktree's root** (it writes `.gov-runtime/store.db`); the lead does that. Load stores only in temporary repositories. Never run `gov rebuild --no-embeddings` anywhere. Never run `gov close`, `gov adopt` or `gov pause`.
- The decision register `docs/DECISION_REGISTER.md` is the real one and read-only: never edit it.
- Your temporary folder is removed when your session ends (DEC-386): everything the lead needs is in your final message.
- If the guard or the sandbox refuses something you needed for the ticket, do not work around it: return it as a package. **Refused twice for the same call: stop and say so; no third try** (AR-6).
- On an authentication or access error (401, 403, "Failed to authenticate"), stop and return at once.

## What you read

- The ticket file `.tickets/DAEO-ym8a.md` (read-only): its KPI lines and its `allowed_paths`.
- The ticket's acceptance tests and their README (read-only): `tests/acceptance/W2-03/`. **The README's readings R1 to R7 are the readings you build to.**
- The card in `docs/plan/WAVE_2_WBS.md` §2 (W2-03) and §0.
- The list rows it takes in, in `docs/plan/WAVE_2_LIST.md` and `docs/plan/WAVE_2_TRIAGE.md`: W2-L031, W2-L069, W2-L221, W2-M039, W2-M106, W2-M145, W2-M267 (W2-M055 and W2-M141 are not yours here: see below). Their origin is in `governance/project/bootstrap.md` (name it by that path).
- The decisions that apply, in `docs/DECISION_REGISTER.md`: DEC-012, DEC-135, DEC-182, DEC-274, DEC-276, DEC-277, DEC-463, DEC-473, DEC-476, DEC-479, DEC-485, DEC-521, DEC-579, DEC-718 (AR-1), DEC-729, DEC-746 (item 5), DEC-732.
- **DEC-752 (owner, 2026-10-17; not yet in this worktree's register):** this branch carries W2-02's held branch (record types, the decision entry's schema `template/governance/kernel/schemas/register-entry.schema.json`, the `decision_id` grammar in `common.schema.json`). **W2-02's files are not yours:** you never write a path in W2-02's `allowed_paths` (`template/governance/kernel/schemas/**`, `schemas/**`, `template/governance/kernel/templates/decision-record.md`, `src/gov/check/schema.py`, `tests/unit/check/test_schema*`, `tests/unit/check/test_check.py`). If this ticket cannot be built without changing W2-02's work, stop and return a package saying exactly what.
- **W2-01's paths are not yours either:** never write under `src/gov/close/**`, `tests/unit/close/**` or `template/governance/kernel/checks/product-traceability-trailers.yaml`. If the ticket needs a change there, stop and return a package saying exactly which part needs it.
- The code the ticket touches, and the code outside your paths that reads what you change (the store's other readers: `gov close`, `gov context`, `gov status`, the READY rule, retrieval, `gov rebuild`'s check).

## Settled readings for this round

- **Folders (open package P-3):** no folder rule is added. A decision file counts by what it is (reading R5), wherever it lies.
- **How far a register entry is held to its schema (open package P-4):** only as KPI line 4 words it, the `decision_id` grammar and the canonical status. The store's record of an entry keeps the type it has today; `owner` and `date` are not required to load it.
- **Two earlier W1-26 cases contradict this ticket's KPI lines** and are expected to turn red when it is built; they are with the orchestrator as packages and are not yours to change or to keep green:
  - `tests/acceptance/W1-26/test_w1_26_decision_register_and_base.py::test_a_heading_after_a_closed_fence_records_its_id` (a heading without a status line, W2-L221);
  - `tests/acceptance/W1-26/test_w1_26_decision_citations.py::test_a_decision_file_records_its_id[no-type-id-in-grammar]` (an id-only file, W2-M267).
  Report their output. **Every other case of every earlier suite must stay as it was.**
- **List rows outside this round:** W2-M055 (the READY rule reads `deps` only) lies in `src/gov/tasks/`, outside your paths: no work. W2-M141 (core-graph) is already green on this tree: no work. **W2-M039** (dangling edges from WBS ids and trailer values): take it only where it falls out of decisions becoming records; anything more, report as a residual. **W2-L031** (the digest and a `content_hash` over body and all frontmatter): take it for the register entries as the KPI lines demand; extend it to file records only if W1-10's suite (its pinned digests included) stays green unchanged, otherwise report it as a residual.

## What you write

- Only inside the ticket's `allowed_paths`: `src/gov/store/**`, `src/gov/records/**`, `src/gov/decisions/**`, `src/gov/check/citations.py`, `tests/unit/store/**`, `tests/unit/records/**`, `tests/unit/decisions/**`.
- Never the acceptance tests (MR-3). A test you think is wrong is returned as a package, never edited and never worked around.
- Builder tests go in `tests/unit/store/`, `tests/unit/records/` or `tests/unit/decisions/`, as regression evidence only.
- Proportion (DEC-135): no code for edge cases beyond the KPI lines and the rows above. The estimate is about 160 lines. Never make a guard or gate decision fail open: each failure KPI must still refuse, and what the citations check and the decision checker refuse today they still refuse.
- Code outside your paths that reads the store, the record queries or the decision checker must keep working unchanged. If the ticket cannot be built without changing it, return a package.
- No new `gov` command is expected. If you add one, say so: it must be recorded in two lists, one of which is outside your paths.
- Run, in the foreground, each suite to its end (never `-x`), with `PATH=/home/usain/.nvm/versions/node/v22.23.3/bin:$PATH PYTHONPATH=/home/usain/gov-os-worktrees/W2-03/src python3 -m pytest <suite> -q -p no:cacheprovider -rs`:
  - `tests/acceptance/W2-03` until it passes;
  - then the earlier suites nearest your change: `tests/acceptance/W1-10`, `tests/acceptance/W1-11`, `tests/acceptance/W1-26`, `tests/acceptance/W2-02`, `tests/acceptance/W1-09`, `tests/acceptance/W1-13`, `tests/acceptance/W1-24`;
  - then `tests/unit/store tests/unit/records tests/unit/decisions tests/unit/check`.

## Commit

Before each commit, check that `/home/usain/Dynamic-Agentic-Engineering-OS/.git/hooks` holds no `pre-commit` file (only `*.sample` files); if one is there, stop and say so. Never `--no-verify`, never `core.hooksPath`. Commit only your paths, with the trailers in the final block (DEC-182, DEC-476):

    git commit -m "W2-03 (DAEO-ym8a): <subject>" --trailer "Task: DAEO-ym8a" --trailer "Role: engineer" --trailer "Implements: DEC-729" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"

After each commit, run `git log --oneline -2` and `git status --short`, and quote them.

## Return

Your final message is the only thing read. The twelve fields come first, each as a labelled line (label at the start of a line, a colon, at least one word; "none" where there is nothing), and any machine-readable payload after them. Put in them: your commits' hashes; the files changed; the lines added and removed (`git diff --stat 857a428c..HEAD -- src tests/unit`); each suite you ran with its counts; the output of the two W1-26 cases named above; the interface as built (what a record of a register entry carries, what a duplicate's refusal says, what findings the decision checker and the citations check add); the state of each list row (W2-L031, W2-L069, W2-L221, W2-M039, W2-M106, W2-M145, W2-M267); anything you were refused or could not settle, as a package (question, why now, options, impact, reversibility, cost, recommendation, confidence). Refused twice for the same call: stop and say so.

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
