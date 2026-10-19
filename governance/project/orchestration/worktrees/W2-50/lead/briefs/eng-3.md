# Brief: engineer (repair after the last review, DEC-751) — DAEO-kl5e (W2-50), FULL

You are a fresh engineer. Ticket: DAEO-kl5e (W2-50, "The durable scratch root: ~/gov-os-runs/<own ticket>/ in the guard and the launcher's sandbox (CIT-P)"), profile FULL. You work only in the worktree `/home/usain/gov-os-worktrees/W2-50` on branch `w2/W2-50`, at head `3df9d396` or later. The ticket is implemented; the last review found two behaviours missing, the orchestrator decided them (DEC-751, below), and new acceptance tests fail against the code. You repair the code until the whole acceptance suite passes, then bring the change-execution record up to date.

## Standing rules (read first)

- First run `printenv GOV_ROLE GOV_TICKET` (expect `engineer` and `DAEO-kl5e`) and `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-50` and `w2/W2-50`). If anything differs, stop and say so.
- **DEC-732, the code under test:** in this worktree, **every test run and every `gov` command used for verification runs this worktree's own `src/`**: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-50/src` set **per command** (never in a session's `--settings` env). Your verification shows it with `PYTHONPATH=/home/usain/gov-os-worktrees/W2-50/src python3 -c "import gov; print(gov.__file__)"`, quoted in your return; it must point into this worktree.
- **Your own guard runs the code you change (DEC-751 item 6).** The guard's hook in your session runs **this worktree's** `src/`, not the main tree's. A change to `src/gov/guard/decide.py` or `src/gov/guard/runs.py` therefore also confines you at once, and a broken file there breaks your own hook. So: make each edit to those two files leave them importable and whole (prefer one complete edit over several half-steps); the very next command after any edit to either file is `PYTHONPATH=/home/usain/gov-os-worktrees/W2-50/src python3 -m pytest tests/unit/guard -q -p no:cacheprovider`, and you do not end the step (or go on to other work) until it passes. If your tools start being refused after such an edit, do not work around it: stop and return a package with the exact refusal text.
- Run everything in the foreground, one command after another: your session ends with your last message, and nothing started in the background is ever read. Return only after your commits exist.
- No `git checkout` of another commit, no `git reset`, no `git clean`, no amend, no rebase in this worktree.
- Run no glob, no search and no listing over `governance/project/`: name the files you need there one by one (DEC-508). Never read `.claude/settings.json` or `.claude/settings.local.json`, in this worktree or anywhere. Nothing under `~/.claude/` is read.
- Never read, print, search, diff or copy the held-out file under `governance/project/`, and never type its path (DEC-525). Never read or name the qualification oracle.
- **The workbench (DEC-723).** Never write in `~/gov-os-workbench`, and never list, glob or search it. Dev-tier tests use `GOV_DEV_TIERS` by name only and clone into a temporary folder.
- **The real scratch roots are never touched.** Neither you, your code run by hand, nor your builder tests create, write, list or remove anything in the real `~/gov-os-runs/` (it does not exist, and nobody creates it in this run), the real `~/gov-os-worktrees/` or the real `~/gov-os-workbench/`. Every run of the code under test that could make or reach the root gets a temporary `HOME` (and a `TMPDIR` disjoint from it), as the acceptance suite does. Run no `local_only` live-launch case (`tests/acceptance/W1-46/test_w1_46_live_sessions.py`, and the `local_only` cases of W1-50): they launch real sessions with the real HOME and would make the real root; use `-m "not local_only"` for W1-46 and W1-50. Before you return, run `test -e ~/gov-os-runs && echo PRESENT || echo ABSENT` and quote the output: it must print ABSENT.
- Never copy the repository or a folder of it (`cp -r`, `rsync`, `git archive`, `git worktree`, `git clone` of this repository or a folder of it) anywhere; copy single named files only, never `governance/project/`. A builder test that needs a repository builds a temporary one from scratch. No clone, copy or file of a programme is ever put under a `.gov-runtime/` folder (DEC-673).
- Inside a launched session `.gov-runtime/freeze` shows as a placeholder device file whether or not a flag exists: conclude nothing from it. Code that reads a flag is tried in a temporary repository.
- The guard refuses here-documents and unresolvable variables in Bash write targets: write files with the Write and Edit tools and literal absolute paths. No subagents that write. Install nothing: a tool you need is returned as a package. No push, merge, rebase or tag. Never write `.gov-runtime/**` outside `.gov-runtime/scratch/`. Never run `gov rebuild --no-embeddings`, `gov close`, `gov adopt` or `gov pause` against this worktree or the main tree. Do not run `docs/plan/tools/validate_s1.py` (DEC-738 item 2). Never write under `src/gov/close/**`, `tests/unit/close/**` or `template/governance/kernel/checks/product-traceability-trailers.yaml` (W2-01's).
- Refused twice for the same call: stop and say so; no third try (AR-6).
- If the guard or the sandbox refuses something you needed for the ticket, do not work around it: return it as a package. On an authentication or access error (401, 403, "Failed to authenticate", "access grant"), stop and return status AUTH_REQUIRED.
- Your temporary folder is removed when your session ends (DEC-386): everything the lead needs is in your final message.

## DEC-751 (orchestrator, delegated, 2026-10-17; staged for the owner's commit, not in this worktree's register — apply it as written here)

1. **P-A (a), stricter only.** The launcher writes a marker in the own folder naming this repository's git common directory. The guard and the launcher refuse a folder whose marker is missing or names another repository. About 40 to 60 lines in `runs.py` and `launcher.py`, within DEC-728.
2. **P-B (a), stricter only.** The secrets walk follows links whose target stays inside the repository being scanned, even under the root. About 5 to 10 lines in `src/gov/secrets/__init__.py`, within DEC-743 item 3's link rule; W1-15's B4 stays green.
3. These are fixes after the last review that DEC-413 allows.

## What you read

- The ticket file `.tickets/DAEO-kl5e.md` (read-only): its KPI lines, its `allowed_paths` and its body.
- The approved proposal `docs/changes/W2-50-CIT-P.md` (with the owner's answers, DEC-743, in its closing section) and the record `docs/changes/W2-50-CIT-E.md`.
- The acceptance tests and their README (read-only): `tests/acceptance/W2-50/`, in particular the new file `test_w2_50_last_review.py` and the README's section on the tests added from the last review.
- **The failing output:** `/home/usain/gov-os-worktrees/W2-50/.gov-runtime/scratch/lead/log/red-4.txt` — the suite at `e58081be`: 15 failed, 218 passed. The failures are all in `tests/acceptance/W2-50/test_w2_50_last_review.py`: `test_another_repositorys_session_gets_nothing_in_a_folder_the_first_made` (3), `test_a_launch_in_another_repository_neither_adds_nor_changes_the_folder` (3), `test_a_folder_made_by_hand_gives_no_session_anything` (2), `test_a_folder_that_does_not_exist_yet_gives_no_session_anything` (2), `test_a_launch_neither_adds_nor_records_a_folder_that_exists_without_a_record` (2), `test_a_projects_own_check_follows_a_link_that_stays_inside_the_project` (3, the clone under the root).
- The decisions, in `docs/DECISION_REGISTER.md`: DEC-728, DEC-723, DEC-108, DEC-159, DEC-135. The code: `src/gov/guard/runs.py`, `src/gov/guard/decide.py`, `src/gov/launch/launcher.py`, `src/gov/secrets/__init__.py`.

## What you write

- Only inside the ticket's `allowed_paths`: `src/gov/guard/runs.py`, `src/gov/guard/decide.py`, `src/gov/launch/launcher.py`, `src/gov/secrets/__init__.py` (the link rule only), `template/governance/kernel/checks/secrets-indexing.yaml`, `tests/unit/guard/test_runs*`, `tests/unit/launch/test_runs*`, `docs/changes/W2-50-CIT-E.md`.
- Never the acceptance tests (MR-3). A test you think is wrong is returned as a package, never edited and never worked around.
- Builder tests in `tests/unit/guard/test_runs*` and `tests/unit/launch/test_runs*`, as regression evidence only, with a temporary `HOME`.
- Proportion (DEC-135): no code for edge cases beyond what the failing tests, DEC-751 and the KPI lines ask; the estimate is about 50 to 70 lines in all. The launcher writes the marker only into a folder it has just made itself; it never writes one into a folder that already exists without it, and never rewrites one. **Never make a guard decision fail open:** every case that refuses today must still refuse, and any error or doubt (a marker missing, unreadable, not a regular file, or naming another repository; a common directory that cannot be found) gives no own folder (deny). Keep the guard's decision fast: the latency cases `test_a_call_waits_under_100_ms_p95_for_the_hook` (W1-05) and `test_decision_p95_is_under_100_ms` (W1-02) must still pass (run such a file alone if it fails under machine load, and report it).
- Run, in the foreground, each suite to its end, never with `-x`:
  - `PATH=/home/usain/.nvm/versions/node/v22.23.3/bin:$PATH PYTHONPATH=/home/usain/gov-os-worktrees/W2-50/src python3 -m pytest tests/acceptance/W2-50 -q -p no:cacheprovider -rs` until all 233 pass;
  - the earlier suites of the code you touch, the same way: W1-02, W1-03, W1-04, W1-05, W1-15, W1-28, W1-32, W1-38, W1-46 and W1-50 (these two with `-m "not local_only"`), W1-48, and any other you judge touched (name each);
  - the builder tests: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-50/src python3 -m pytest tests/unit -q -p no:cacheprovider`.
- **Then the record.** Update `docs/changes/W2-50-CIT-E.md` in the same round, with a new section for this round: DEC-751 and the findings the new tests hold (read them from the README's section on the last review), what the repair changed, file by file, any new difference from the CIT-P (for one: a session can now write in its own folder only after a launch of its ticket has made it, so R2's "first write makes the folder" is gone; and CIT-E difference 10 is closed), the new commits, and the lines added and removed. Keep its frontmatter valid against `template/governance/kernel/schemas/change-execution-record.schema.json`.

## Commit

Before each commit, check that `/home/usain/Dynamic-Agentic-Engineering-OS/.git/hooks` holds no `pre-commit` file (only `*.sample` files); if one is there, stop and say so. Never `--no-verify`, never `core.hooksPath`. Two commits, only your paths, with the trailers in the final block:

    git commit -m "W2-50 (DAEO-kl5e): repair after the last review — the own folder's repository marker, links inside the scanned project (DEC-751)" --trailer "Task: DAEO-kl5e" --trailer "Role: engineer" --trailer "Implements: DEC-728" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
    git commit -m "W2-50 (DAEO-kl5e): the CIT-E brought up to date for the DEC-751 repair round" --trailer "Task: DAEO-kl5e" --trailer "Role: engineer" --trailer "Implements: DEC-728" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"

Then show `git log --oneline -3`, `git log -2 --format=%B`, `git show --stat HEAD~1 HEAD` and `git status --short`.

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

In those fields give: both commits' hashes and trailers; the files changed; the lines added and removed (`git show --shortstat` of the repair commit); the interface as changed (the marker's place and content, the rule in the guard and in the launcher, the secrets link rule); every suite you ran with its counts; the `gov.__file__` line; the `~/gov-os-runs` ABSENT line; anything you were refused or could not settle, as a package (question, why now, options, impact, reversibility, cost, recommendation, confidence). Refused twice for the same call: stop and say so.
