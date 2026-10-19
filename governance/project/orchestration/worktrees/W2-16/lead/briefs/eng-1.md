# Brief: engineer

You are a fresh engineer. Ticket: `DAEO-49o5` (`W2-16`, "Immutable, hash-pinned releases (CAP-43.b lite)"), profile FULL. You work only in the worktree `/home/usain/gov-os-worktrees/W2-16` on branch `w2/W2-16`. You implement the ticket until its acceptance tests pass.

## Standing rules (read first)

- First run `printenv GOV_ROLE GOV_TICKET` (expect `engineer` and `DAEO-49o5`) and `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-16` and `w2/W2-16`). If anything differs, stop and say so.
- **The code under test (DEC-732):** in this worktree, **every test run and every `gov` command used for verification runs this worktree's own `src/`**: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-16/src` set **per command** (never in a session's `--settings` env). Your verification shows it with `PYTHONPATH=/home/usain/gov-os-worktrees/W2-16/src python3 -c "import gov; print(gov.__file__)"`, quoted in your return; it must point into this worktree.
- Run everything in the foreground, one command after another: your session ends with your last message, and nothing started in the background is ever read. Return only after your commit exists. A single tool call is cut off at 10 minutes: if a suite takes longer, run it file by file.
- No `git checkout` of another commit, no `git reset`, no `git clean`, no amend, no rebase in this worktree. A correction is a new commit.
- Run no glob, no search and no listing over `governance/project/`: name the files you need there one by one (DEC-508). Never read `.claude/settings.json` or `.claude/settings.local.json`, in this worktree or anywhere. Nobody reads anything under `~/.claude/`.
- Never read, print, search, diff or copy the held-out file under `governance/project/`, and never type its path (DEC-525). Never read or name the qualification oracle.
- **The workbench (DEC-723):** never write in `~/gov-os-workbench`, and never list, glob or search it. Dev-tier tests use `GOV_DEV_TIERS` by name only and clone into a temporary folder.
- **Never copy the repository or a folder of it** (no `cp -r`, `rsync`, `git archive`, `git worktree` or `git clone` of this repository or a folder of it) anywhere; copy single named files only, never `governance/project/`. A try-out that needs a repository builds a temporary one from scratch. No clone, copy or file of a programme is ever put under a `.gov-runtime/` folder (DEC-673).
- Inside a launched session `.gov-runtime/freeze` shows as a placeholder device file whether or not a flag exists: conclude nothing from it.
- The guard refuses here-documents and unresolvable variables in Bash write targets: write files with the Write and Edit tools and literal absolute paths. No subagents that write. **Install nothing** (no `pip install`, no download, no network): a tool you need is returned as a package. No push, merge, rebase or tag.
- **Nobody tags and nobody signs.** You never create a git tag in this repository, and your code never creates one or signs anything. You never run `gov release` against this repository's real history, and you write nothing into this worktree's `docs/releases/` except, if you judge it useful, one short README or format note there. Try-outs build releases in temporary repositories.
- Never write `.gov-runtime/**` outside `.gov-runtime/scratch/`. Never touch `tests/acceptance/**` (MR-3). Never run `gov rebuild --no-embeddings`. Never run `gov close`, `gov adopt` or `gov pause`.
- Your temporary folder is removed when your session ends (DEC-386): everything the lead needs is in your final message.
- If the guard or the sandbox refuses something you needed for the ticket, do not work around it: return it as a package. **Refused twice for the same call: stop and say so; no third try** (AR-6).
- On an authentication or access error (401, 403, "Failed to authenticate"), stop and return status `AUTH_REQUIRED`.

## What you read

- The ticket file `.tickets/DAEO-49o5.md` (read-only): its KPI lines and its `allowed_paths`.
- The ticket's acceptance tests and their README (read-only): `tests/acceptance/W2-16/` (commit `4422f93c`). The README states the interface the tests assume and the readings the test designer made (the manifest's own hash, the lock task, the schema versions).
- The sources: CAP-43 and its covers, and CAP-02 (CAP-02.a, CAP-02.c) in `docs/contract/contract.yaml` (Contract v4.2). The list rows the ticket takes in, in `docs/plan/WAVE_2_LIST.md`: W2-H029, W2-L002, W2-L014, W2-L227, W2-M174, W2-M175.
- The decisions that apply, in `docs/DECISION_REGISTER.md`: DEC-722, DEC-023, DEC-488, DEC-493, DEC-499, DEC-542, DEC-194, DEC-244, DEC-654, DEC-135. Two staged decisions not yet in this tree's register, applied as written here:
  - **DEC-752:** this branch carries W2-49's held work (Contract v4.2 and its records). W2-49's files are not this ticket's: you write none of them.
  - **DEC-753 (delegated):** `gov release` is a new `gov` command. It is recorded in the two command lists (W1-07's tests' list and `RECORDED_GOV_COMMANDS` in `src/gov/check/commands.py`) only in this ticket's resume round, after W2-20 closes. **You do not touch `src/gov/check/commands.py` in this round.** The W1-07 and W1-26 cases that find `release` unrecorded are expected reds, with DEC-753 as their reason.
- The code the ticket touches: `src/gov/lock/` (the lock and the one comparison, DEC-488), `copier.yml` (the Copier task), how `gov` finds a command (`src/gov/cli/main.py`: a package `src/gov/<name>/` with a `command.py` is a command), and how `gov doctor` reads the comparison (`src/gov/doctor/command.py`, read-only).

## What you write

- Only inside the ticket's `allowed_paths`, minus the one file DEC-753 holds back: `src/gov/lock/**`, `src/gov/release/**`, `copier.yml`, `template/framework.lock*`, `tests/unit/lock/**`, `tests/unit/release/**`, `docs/releases/**`. **Not** `src/gov/check/commands.py` (DEC-753), and never `src/gov/close/**`, `tests/unit/close/**` or `template/governance/kernel/checks/product-traceability-trailers.yaml` (W2-01's).
- **If a KPI needs a change outside those paths** (for example in `src/gov/doctor/`, a new `src/gov/install/` or W2-17's `src/gov/update/`), do not make it: return a package naming the file and the line of the KPI it serves, and build the rest. The tests take "refused by `gov install` and `gov update`" through `copier copy` and `copier update` of the template and through `gov doctor`, because those two commands do not exist yet (W2-18 and W2-17 build them after this ticket); your verification of a release must therefore be a public function they can call.
- Never the acceptance tests (MR-3). A test you think is wrong is returned as a package, never edited and never worked around.
- Constraints from the earlier suites, which must stay green: W1-39 (the template and the lock), W1-27 (doctor; a project never installed from the template stays "unmeasured", and `gov doctor` stays green on this repository, Wave 2 exit criterion 3), W1-07 (`gov lock` stays a usage error, DEC-542; `python3 -m gov.lock` stays the module command, and in a folder that is no installed project it refuses with exit 1, names `framework.lock` and writes nothing), W1-26, W1-32. W2-M175 is met with a `gov` subcommand that adds no top-level command other than `release`.
- **One known conflict, not yours to settle:** `tests/acceptance/W1-39/test_w1_39_drift.py::test_a_project_with_neither_lock_nor_answers_file_stays_unmeasured` expects what W2-H029 (a KPI line of this ticket) forbids: an installed project with both its lock and its answers file deleted answering "unmeasured" with exit 0. Build the KPI as the W2-16 tests hold it; that one W1-39 case is expected to go red, and the lead returns it as a package. Do not try to make both pass, and report it.
- Builder tests go in `tests/unit/lock/` and `tests/unit/release/`, as regression evidence only (MR-3).
- Proportion (DEC-135): no code for edge cases beyond the KPI lines and the rows. The estimate is about 150 lines. **Never make a guard or gate decision fail open:** each failure case must still refuse; a release, lock or manifest that cannot be read or hashed is a refusal, never a pass.
- **Commit your work before you run any long suite.** Then run, each to its end, never with `-x`:
  - `PATH=/home/usain/.nvm/versions/node/v22.23.3/bin:$PATH PYTHONPATH=/home/usain/gov-os-worktrees/W2-16/src python3 -m pytest tests/acceptance/W2-16 -q -p no:cacheprovider -rs`
  - the same for `tests/acceptance/W1-39`, `tests/acceptance/W1-27`, `tests/acceptance/W1-07`, `tests/acceptance/W1-26`, `tests/acceptance/W1-32`;
  - `PYTHONPATH=/home/usain/gov-os-worktrees/W2-16/src python3 -m pytest tests/unit -q -p no:cacheprovider`
  A repair after a run is a new commit.

## Commit

Before each commit, check that `/home/usain/Dynamic-Agentic-Engineering-OS/.git/hooks` holds no `pre-commit` file (only `*.sample` files); if one is there, do not commit: stop and say so. Never `--no-verify`, never `core.hooksPath`. Commit only your paths, with the trailers in the final block (DEC-182, DEC-476):

    git commit -m "<subject>" --trailer "Task: DAEO-49o5" --trailer "Role: engineer" --trailer "Implements: DEC-722" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"

After each commit show `git log --oneline -2`, `git log -1 --format=%B` and `git status --short`.

## Return

Your last message, complete in itself: your commits' hashes; the files changed; the interface as built (the `gov release` command line, where the record goes and what it holds, what the lock records, the Copier task's command, the public verification function); each suite you ran with its counts and each red case by name with its reason; the `gov.__file__` line; the lines added and removed (`git diff --stat 4422f93c..HEAD`); anything you were refused or could not settle, as a package (question, why now, options, impact, reversibility, cost, recommendation, confidence).

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

The twelve fields come first, each as a labelled line (label at the start of a line, a colon, at least one word; "none" where there is nothing), and any machine-readable payload after them. Refused twice for the same call: stop and say so.
