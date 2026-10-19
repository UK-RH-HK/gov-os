# Brief: engineer — DAEO-ym8a (W2-03), STANDARD, the builder tests' fixtures (DEC-755 item 3)

You are a fresh engineer. Ticket: DAEO-ym8a (W2-03, "Decisions as records, each with its own hash"), profile STANDARD. You work only in the worktree `/home/usain/gov-os-worktrees/W2-03` on branch `w2/W2-03`. The ticket is built. Under it, a register entry counts only when a status line sits under its heading (KPI line 3, list row W2-L221). Nine builder cases in `tests/unit/check/test_citations.py` still write headings with no status line under them, so they are red. You fix their fixtures and nothing else.

## Standing rules (read first)

- First run `printenv GOV_ROLE GOV_TICKET` (expect `engineer` and `DAEO-ym8a`) and `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-03` and `w2/W2-03`), and `git log --oneline -1` (expect `db002376`). If anything differs, stop and say so.
- **The code under test (DEC-732), word for word:** in this worktree, **every test run and every `gov` command used for verification runs this worktree's own `src/`**: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-03/src` set **per command** (never in a session's `--settings` env). Show it once with `PYTHONPATH=/home/usain/gov-os-worktrees/W2-03/src python3 -c "import gov; print(gov.__file__)"` and quote the line.
- Run everything in the foreground, one command after another: your session ends with your last message, and nothing started in the background is ever read. Return only after your commit exists. **Commit your work before you run any suite that may take long**. A correction after it is a new commit.
- No `git checkout` of another commit, no `git reset`, no `git clean`, no amend, no rebase in this worktree.
- Run no glob, no search and no listing over `governance/project/`: name the files you need there one by one (DEC-508). Never read `.claude/settings.json` or `.claude/settings.local.json`, in this worktree or anywhere. Nobody reads anything under `~/.claude/`.
- Never read, print, search, diff or copy the held-out file under `governance/project/`, and never type its path (DEC-525). Never read or name the qualification oracle.
- **The workbench (DEC-723).** Never write in `~/gov-os-workbench`, and never list, glob or search it. Dev-tier tests use `GOV_DEV_TIERS` by name only and clone into a temporary folder. This work needs none.
- Never copy the repository or a folder of it (no `cp -r`, `rsync`, `git archive`, `git worktree` or `git clone` of this repository) anywhere. No clone, copy or file of a programme is ever put under a `.gov-runtime/` folder (DEC-673).
- Inside a launched session `.gov-runtime/freeze` shows as a placeholder device file whether or not a flag exists: conclude nothing from it.
- The guard refuses here-documents and unresolvable variables in Bash write targets: write files with the Write and Edit tools and literal absolute paths. No subagents. Install nothing. No push, merge, rebase or tag. Never write `.gov-runtime/**` outside `.gov-runtime/scratch/`. Never run `gov rebuild` (with or without `--no-embeddings`), `gov close`, `gov adopt` or `gov pause`.
- The decision register `docs/DECISION_REGISTER.md` is the real one and read-only.
- If the guard or the sandbox refuses something you needed, do not work around it: return a package. **Refused twice for the same call: stop and say so; no third try** (AR-6).
- On an authentication or access error (401, 403, "Failed to authenticate"), stop and return at once.

## The decision you apply: DEC-755 item 3 (orchestrator, delegated, 2026-10-17; staged for the owner's commit, not in this worktree's register — apply it as written here)

`tests/unit/check/test_citations.py` is now in this ticket's `allowed_paths` (`.tickets/DAEO-ym8a.md`), **for its fixtures only**. Add a status line (`- **Status:** ACCEPTED`) under each entry heading in the fixtures of the nine red cases. **No expectation changes:** every `assert` keeps the same expected value, and no case is removed, skipped or renamed. These are the nine red cases:

- `test_an_entry_heading_records_its_id` (its six parameters, which share one fixture body);
- `test_a_longer_id_is_recorded_as_itself`;
- `test_a_heading_in_a_fence_does_not_count_and_the_fence_ends_where_it_is_closed` (put the status line under each heading, inside and outside fences, so the case still tests the fence and not the missing status line);
- `test_the_register_is_read_from_the_tree_of_the_citing_commit`.

Write nothing else: not `src/`, no other test file, and no other case in this file. If a case cannot be made green by a fixture's status line alone, report it with its output and change nothing more.

## Check

Run, in the foreground, to its end (never `-x`):

- `PYTHONPATH=/home/usain/gov-os-worktrees/W2-03/src python3 -m pytest tests/unit/check/test_citations.py -q -p no:cacheprovider` (before and after your edit; quote both counts);
- after your commit: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-03/src python3 -m pytest tests/unit/check -q -p no:cacheprovider`.

## Commit

Before committing, check that `/home/usain/Dynamic-Agentic-Engineering-OS/.git/hooks` holds no `pre-commit` file (only `*.sample` files); if one is there, stop and say so. Never `--no-verify`, never `core.hooksPath`. Commit only `tests/unit/check/test_citations.py`, in one commit, with the trailers in the final block (DEC-182, DEC-476):

    git commit -m "W2-03 (DAEO-ym8a): the citations builder tests' entries carry a status line (DEC-755 item 3)" --trailer "Task: DAEO-ym8a" --trailer "Role: engineer" --trailer "Implements: DEC-729" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"

After it, run `git log --oneline -2`, `git show --stat HEAD` and `git status --short`, and quote them.

## Return

Your final message is the only thing read. The twelve fields come first, each as a labelled line (label at the start of a line, a colon, at least one word; "none" where there is nothing), and any machine-readable payload after them. Put in them: your commit's hash and trailers; the diff (short); the counts before and after; the `gov.__file__` line; any refusal or package (question, why now, options, impact, reversibility, cost, recommendation, confidence). Refused twice for the same call: stop and say so.

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
