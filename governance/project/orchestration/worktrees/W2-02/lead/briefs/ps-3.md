You are a fresh product-spec worker. Ticket: DAEO-zflj (W2-02), profile STANDARD, ticket mode. You work only in the worktree `/home/usain/gov-os-worktrees/W2-02` on branch `w2/W2-02`. You are a headless session: nobody answers questions while you work, and only your final message is read. Your task is one small, decided change to one builder test.

## Standing rules (read first)

- First run `printenv GOV_ROLE GOV_TICKET` (expect `product-spec` and `DAEO-zflj`) and `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-02` and `w2/W2-02`). If anything differs, stop and say so.
- Run everything in the foreground, one command after another: your session ends with your last message, and nothing started in the background is ever read. Return only after your commit exists. Your session has a hard limit of two hours: commit before you run the full builder suite.
- **The code under test (DEC-732, owner):** in this worktree, **every test run and every `gov` command used for verification runs this worktree's own `src/`**: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-02/src` set **per command** (never in a session's `--settings` env). Your verification shows it with `PYTHONPATH=/home/usain/gov-os-worktrees/W2-02/src python3 -c "import gov; print(gov.__file__)"`, quoted in your return; it must point into this worktree.
- No `git checkout` of another commit, no `git reset`, no `git clean`, no `git stash`, no amend, no rebase in this worktree. A correction is a new commit.
- Run no glob, no search and no listing over `governance/project/`: name the files you need there one by one (DEC-508). Never read `.claude/settings.json` or `.claude/settings.local.json`, in this worktree or anywhere. Nobody reads anything under `~/.claude/`.
- Never read, print, search, diff or copy the held-out file under `governance/project/`, and never type its path (DEC-525). Never read or name the qualification oracle.
- **The workbench (DEC-723):** never write in `~/gov-os-workbench`, and never list, glob or search it. Dev-tier tests use `GOV_DEV_TIERS` by name only and clone into a temporary folder.
- Never copy the repository or a folder of it (no `cp -r`, `rsync`, `git archive`, `git worktree`, `git clone` of this repository or a folder of it) anywhere; copy single named files only, never `governance/project/`. A test that needs a repository builds a temporary one. No clone, copy or file of a programme is ever put under a `.gov-runtime/` folder.
- Inside a launched session `.gov-runtime/freeze` shows as a placeholder device file whether or not a flag exists: conclude nothing from it.
- The guard refuses here-documents and unresolvable variables in Bash write targets: write files with the Write and Edit tools and literal absolute paths. No subagents that write. Install nothing. No push, merge, rebase or tag. Never write `.gov-runtime/**` outside `.gov-runtime/scratch/`.
- Never run `gov rebuild --no-embeddings`, `gov close`, `gov adopt` or `gov pause` against this worktree or the main tree.
- Never write under `src/gov/close/**`, `tests/unit/close/**` or `template/governance/kernel/checks/product-traceability-trailers.yaml` (another ticket's, W2-01).
- Never edit `tests/acceptance/**` (MR-3).
- **Refused twice for the same call: stop and say so; no third try** (AR-6).
- On an authentication or access error (401, 403, "Failed to authenticate", "access grant"), stop and return status `AUTH_REQUIRED`.
- Your temporary folder is removed when your session ends (DEC-386): everything the lead needs is in your final message.
- If the guard or the sandbox refuses something you needed, do not work around it: return it as a package.

## What you read

- The ticket file `.tickets/DAEO-zflj.md` (read-only): its KPI line 3 ("A type with no schema file is reported unmeasured, not green") and its DEC-746 paragraph.
- `tests/unit/check/test_check.py`, the test `test_schema_clean_record`, and the helpers of that file it uses.
- `src/gov/check/schema.py` (read only for you): where core-schema looks for a type's schema files (the layouts it reads), so that the test's project carries them.
- The kernel schema folder `template/governance/kernel/schemas/` (the task type's schema file and `common.schema.json`).

## The decision (DEC-746 item 1, delegated by the orchestrator, 2026-10-17; staged for the owner's commit)

P-A (a): `tests/unit/check/test_check.py` is now in this ticket's `allowed_paths`, **for `test_schema_clean_record` only**. Since W2-02, a record whose type has no schema file is reported unmeasured (`SCHEMA_UNREADABLE`), not green, so this test's project, which carries no schema file, now fails. Make its project carry the kernel's schema files it needs (copy the named single files from `template/governance/kernel/schemas/` into the project's temporary folder, at the layout core-schema reads), so that the test holds what it held before: a clean task record gives no finding. Its assertion stays `check(root) == []`. **Nothing else in that file changes**: no other test, no shared helper another test uses (a new small helper used only by this test is fine), and no other file.

## Runs, in the foreground, to their end, never with `-x`

1. `PYTHONPATH=/home/usain/gov-os-worktrees/W2-02/src python3 -m pytest tests/unit/check -q -p no:cacheprovider` (all of `tests/unit/check` green).
2. Commit (below).
3. After the commit: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-02/src timeout 1800 python3 -m pytest tests/unit -q -p no:cacheprovider`, and report its counts.

## Commit

Before committing, check that `/home/usain/Dynamic-Agentic-Engineering-OS/.git/hooks` holds no `pre-commit` file (only `*.sample` files); if one is there, do not commit, and say so. Never `--no-verify`, never `core.hooksPath`.

Commit only `tests/unit/check/test_check.py`, in one commit, with the trailers in the final block (DEC-182, DEC-476):

    git commit -m "W2-02 (DAEO-zflj): test_schema_clean_record carries the kernel's schema files" --trailer "Task: DAEO-zflj" --trailer "Implements: DEC-441" --trailer "Role: product-spec" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"

A commit message cites a decision id only if the decision register records it (DEC-463): DEC-746 is not yet in this worktree's register, so name it in neither the subject nor a trailer. After the commit run `git log --oneline -2`, `git log -1 --format=%B`, `git show --stat HEAD` and `git status --short`, and quote them.

## Return

One message, your last, complete in itself. **The twelve fields come first, each as a labelled line** (label at the start of a line, a colon, at least one word; "none" where there is nothing), and any machine-readable payload after them:

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

In those fields: your commit's hash and trailers; the lines added and removed; the result of each run with counts; the `gov.__file__` line. Refused twice for the same call: stop and say so.
