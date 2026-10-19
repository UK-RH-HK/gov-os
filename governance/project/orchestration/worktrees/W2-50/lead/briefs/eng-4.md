# Brief: engineer (the last round, DEC-758 item 1) — DAEO-kl5e (W2-50), FULL

You are a fresh engineer. Ticket: DAEO-kl5e (W2-50, "The durable scratch root: ~/gov-os-runs/<own ticket>/ in the guard and the launcher's sandbox (CIT-P)"), profile FULL. You work only in the worktree `/home/usain/gov-os-worktrees/W2-50` on branch `w2/W2-50`, at head `ef7c1835` or later. The ticket is implemented and repaired; an extra independent review found two more behaviours missing, the owner decided them (DEC-758, below), and new acceptance tests fail against the code. You repair the code until the whole acceptance suite passes, then bring the change-execution record up to date. This is the last round the owner allows.

## Standing rules (read first)

- First run `printenv GOV_ROLE GOV_TICKET` (expect `engineer` and `DAEO-kl5e`) and `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-50` and `w2/W2-50`). If anything differs, stop and say so.
- **DEC-732, the code under test:** in this worktree, **every test run and every `gov` command used for verification runs this worktree's own `src/`**: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-50/src` set **per command** (never in a session's `--settings` env). Your verification shows it with `PYTHONPATH=/home/usain/gov-os-worktrees/W2-50/src python3 -c "import gov; print(gov.__file__)"`, quoted in your return; it must point into this worktree.
- **Your own guard runs the code you change (DEC-751 item 6).** The guard's hook in your session runs **this worktree's** `src/`, not the main tree's. A change to `src/gov/guard/decide.py` or `src/gov/guard/runs.py` therefore also confines you at once, and a broken file there breaks your own hook. So: make each edit to those two files leave them importable and whole (prefer one complete edit over several half-steps); the very next command after any edit to either file is `PYTHONPATH=/home/usain/gov-os-worktrees/W2-50/src python3 -m pytest tests/unit/guard -q -p no:cacheprovider`, and you do not end the step (or go on to other work) until it passes. If your tools start being refused after such an edit, do not work around it: stop and return a package with the exact refusal text. Note that after your F1 change, your own `cp`/`install` into a folder is judged file by file too.
- Run everything in the foreground, one command after another: your session ends with your last message, and nothing started in the background is ever read. Return only after your commits exist.
- No `git checkout` of another commit, no `git reset`, no `git clean`, no amend, no rebase in this worktree.
- Run no glob, no search and no listing over `governance/project/`: name the files you need there one by one (DEC-508). Never read `.claude/settings.json` or `.claude/settings.local.json`, in this worktree or anywhere. Nothing under `~/.claude/` is read.
- Never read, print, search, diff or copy the held-out file under `governance/project/`, and never type its path (DEC-525). Never read or name the qualification oracle.
- **The workbench (DEC-723).** Never write in `~/gov-os-workbench`, and never list, glob or search it. Dev-tier tests use `GOV_DEV_TIERS` by name only and clone into a temporary folder.
- **The real scratch roots are never touched.** Neither you, your code run by hand, nor your builder tests create, write, list or remove anything in the real `~/gov-os-runs/` (it does not exist, and nobody creates it in this run), the real `~/gov-os-worktrees/` or the real `~/gov-os-workbench/`. Every run of the code under test that could make or reach the root gets a temporary `HOME` (and a `TMPDIR` disjoint from it), as the acceptance suite does. Run no `local_only` live-launch case (`tests/acceptance/W1-46/test_w1_46_live_sessions.py`, and the `local_only` cases of W1-50): use `-m "not local_only"` for W1-46 and W1-50. Before you return, run `test -e ~/gov-os-runs && echo PRESENT || echo ABSENT` and quote the output: it must print ABSENT.
- Never copy the repository or a folder of it (`cp -r`, `rsync`, `git archive`, `git worktree`, `git clone` of this repository or a folder of it) anywhere; copy single named files only, never `governance/project/`. A builder test that needs a repository builds a temporary one from scratch. No clone, copy or file of a programme is ever put under a `.gov-runtime/` folder (DEC-673).
- Inside a launched session `.gov-runtime/freeze` shows as a placeholder device file whether or not a flag exists: conclude nothing from it.
- The guard refuses here-documents and unresolvable variables in Bash write targets: write files with the Write and Edit tools and literal absolute paths. No subagents that write. Install nothing: a tool you need is returned as a package. No push, merge, rebase or tag. Never write `.gov-runtime/**` outside `.gov-runtime/scratch/`. Never run `gov rebuild --no-embeddings`, `gov close`, `gov adopt` or `gov pause` against this worktree or the main tree. Do not run `docs/plan/tools/validate_s1.py` (DEC-738 item 2). Never write under `src/gov/close/**` or `tests/unit/close/**` (W2-53's, running beside you in its own worktree), nor `template/governance/kernel/checks/product-traceability-trailers.yaml`.
- Refused twice for the same call: stop and say so; no third try (AR-6).
- If the guard or the sandbox refuses something you needed for the ticket, do not work around it: return it as a package. On an authentication or access error (401, 403, "Failed to authenticate", "access grant"), stop and return status AUTH_REQUIRED.
- Your temporary folder is removed when your session ends (DEC-386): everything the lead needs is in your final message.

## DEC-758 item 1 (owner, 2026-10-17; staged for the owner's commit, not in this worktree's register — apply it as written here)

- **F1:** every copy or install into a folder (`cp X d/`, `cp X d`, `install X d/`, `cp -r s/. d/`, with or without a trailing slash, with `-t`/`--target-directory` as now) is judged as **each file it writes, `<folder>/<name>`, under the same link and hard-link rule as a direct write**, and refused with the guard's reason. This closes the older hole for every ticket (row W2-H056, closed by W2-50), and the case where the destination is the own folder's marker (row W2-L349).
- **F2:** a project whose real root is inside `~/gov-os-runs` gets **no own folder**.
- A FIFO in the marker's place is row W2-L350, not this round's work.
- **If F1's fix needs a path outside this ticket's `allowed_paths`, stop and return PACKAGES naming the file.**

## What you read

- The ticket file `.tickets/DAEO-kl5e.md` (read-only): its KPI lines, its `allowed_paths` and its body.
- The approved proposal `docs/changes/W2-50-CIT-P.md` (with the owner's answers, DEC-743, in its closing section) and the record `docs/changes/W2-50-CIT-E.md`.
- The acceptance tests and their README (read-only): `tests/acceptance/W2-50/`, in particular the new file `test_w2_50_extra_review.py` and the README's section on the tests added from the extra review.
- **The failing output:** `/home/usain/gov-os-worktrees/W2-50/.gov-runtime/scratch/lead/log/red-5.txt` — the suite at `ef7c1835`: 38 failed, 267 passed, all failures in `test_w2_50_extra_review.py`.
- The decisions, in `docs/DECISION_REGISTER.md`: DEC-728, DEC-723, DEC-108, DEC-159, DEC-135. The code: `src/gov/guard/runs.py`, `src/gov/guard/decide.py`, `src/gov/launch/launcher.py`.

## What you write

- Only inside the ticket's `allowed_paths`: `src/gov/guard/runs.py`, `src/gov/guard/decide.py`, `src/gov/launch/launcher.py`, `src/gov/secrets/__init__.py` (the link rule only), `template/governance/kernel/checks/secrets-indexing.yaml`, `tests/unit/guard/test_runs*`, `tests/unit/launch/test_runs*`, `docs/changes/W2-50-CIT-E.md`.
- Never the acceptance tests (MR-3). A test you think is wrong is returned as a package, never edited and never worked around.
- Builder tests in `tests/unit/guard/test_runs*` and `tests/unit/launch/test_runs*`, as regression evidence only, with a temporary `HOME`.
- Proportion (DEC-135): no code for edge cases beyond what the failing tests, DEC-758 and the KPI lines ask. **Never make a guard decision fail open:** every case that refuses today must still refuse, and any error or doubt (a destination whose kind cannot be told, a project root that cannot be resolved) refuses. An ordinary copy or install into a folder the session may write must still be allowed. Keep the guard's decision fast: the latency cases `test_a_call_waits_under_100_ms_p95_for_the_hook` (W1-05) and `test_decision_p95_is_under_100_ms` (W1-02) must still pass (run such a file alone if it fails under machine load, and report it).
- Run, in the foreground, each suite to its end, never with `-x`:
  - `PATH=/home/usain/.nvm/versions/node/v22.23.3/bin:$PATH PYTHONPATH=/home/usain/gov-os-worktrees/W2-50/src python3 -m pytest tests/acceptance/W2-50 -q -p no:cacheprovider -rs` until all 305 pass;
  - the earlier suites of the code you touch, the same way: W1-02, W1-03, W1-04, W1-05, W1-15, W1-28, W1-32, W1-38, W1-46 and W1-50 (these two with `-m "not local_only"`), W1-48, and any other you judge touched (name each);
  - the builder tests: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-50/src python3 -m pytest tests/unit -q -p no:cacheprovider`.
- **Then the record.** Update `docs/changes/W2-50-CIT-E.md` in the same round, with a new section for this round: DEC-758 and the findings the new tests hold (F1 with rows W2-H056 and W2-L349 closed; F2), what the repair changed, file by file, any new difference from the CIT-P, the correction of difference 15's text if it no longer holds as written, the new commits, and the lines added and removed. Keep its frontmatter valid against `template/governance/kernel/schemas/change-execution-record.schema.json`.

## Commit

Before each commit, check that `/home/usain/Dynamic-Agentic-Engineering-OS/.git/hooks` holds no `pre-commit` file (only `*.sample` files); if one is there, stop and say so. Never `--no-verify`, never `core.hooksPath`. Two commits, only your paths, with the trailers in the final block:

    git commit -m "W2-50 (DAEO-kl5e): the last round — a copy into a folder judged file by file, no own folder for a project under the root (DEC-758)" --trailer "Task: DAEO-kl5e" --trailer "Role: engineer" --trailer "Implements: DEC-728" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
    git commit -m "W2-50 (DAEO-kl5e): the CIT-E brought up to date for the DEC-758 round" --trailer "Task: DAEO-kl5e" --trailer "Role: engineer" --trailer "Implements: DEC-728" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"

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

In those fields give: both commits' hashes and trailers; the files changed; the lines added and removed (`git show --shortstat` of the repair commit); the interface as changed (how a copy or install into a folder is judged now, the rule for a project under the root in the guard and in the launcher); every suite you ran with its counts; the `gov.__file__` line; the `~/gov-os-runs` ABSENT line; anything you were refused or could not settle, as a package (question, why now, options, impact, reversibility, cost, recommendation, confidence). Refused twice for the same call: stop and say so.
