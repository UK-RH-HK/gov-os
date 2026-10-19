# Brief: engineer (the last round, DEC-774 and DEC-778) — DAEO-kl5e (W2-50), FULL

You are a fresh engineer. Ticket: DAEO-kl5e (W2-50, "The durable scratch root: ~/gov-os-runs/<own ticket>/ in the guard and the launcher's sandbox (CIT-P)"), profile FULL. You work only in the worktree `/home/usain/gov-os-worktrees/W2-50` on branch `w2/W2-50`, at head `397a80de` or later. The ticket is implemented; the review of the last round found one behaviour missing (finding D), the owner decided it (DEC-774), and widened the round with one more (DEC-778). New acceptance tests fail against the code. You repair the code until the whole acceptance suite passes, then add one section to the change-execution record.

## Standing rules (read first)

- First run `printenv GOV_ROLE GOV_TICKET` (expect `engineer` and `DAEO-kl5e`) and `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-50` and `w2/W2-50`). If anything differs, stop and say so.
- **DEC-732, the code under test:** in this worktree, **every test run and every `gov` command used for verification runs this worktree's own `src/`**: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-50/src` set **per command** (never in a session's `--settings` env). Your verification shows it with `PYTHONPATH=/home/usain/gov-os-worktrees/W2-50/src python3 -c "import gov; print(gov.__file__)"`, quoted in your return; it must point into this worktree.
- **Your own guard runs the code you change (DEC-751 item 6).** The guard's hook in your session runs **this worktree's** `src/`, not the main tree's. A change to `src/gov/guard/decide.py` or `src/gov/guard/protected.py` therefore also confines you at once, and a broken file there breaks your own hook. So: make each edit leave the file importable and whole (prefer one complete edit over several half-steps); the very next command after any edit to either is `PYTHONPATH=/home/usain/gov-os-worktrees/W2-50/src python3 -m pytest tests/unit/guard -q -p no:cacheprovider`, and you do not end the step (or go on to other work) until it passes. If your tools start being refused after such an edit, do not work around it: stop and return a package with the exact refusal text. After your change, your own `cp`/`install`/`mv` calls are judged by the new rules too.
- Run everything in the foreground, one command after another: your session ends with your last message, and nothing started in the background is ever read. Return only after your commits exist. A foreground command is killed after 10 minutes: run a long suite's files in a few separate commands.
- No `git checkout` of another commit, no `git reset`, no `git clean`, no amend, no rebase in this worktree.
- Run no glob, no search and no listing over `governance/project/`: name the files you need there one by one (DEC-508). Never read `.claude/settings.json` or `.claude/settings.local.json`, in this worktree or anywhere. Nothing under `~/.claude/` is read.
- **Never read, print, search, diff, copy, move or link the held-out file under `governance/project/`, and never type its path (DEC-525), in code, a builder test, a command or a message. Builder tests for the read rule never name the held-out file or its path: they use a temporary project with its own settings file as the stand-in, as the acceptance tests do (DEC-778).** Never read or name the qualification oracle. Never run `mv`, `cp` or `ln` on any real repository's settings file or held-out file.
- **The workbench (DEC-723).** Never write in `~/gov-os-workbench`, and never list, glob or search it. Dev-tier tests use `GOV_DEV_TIERS` by name only and clone into a temporary folder.
- **The real scratch roots are never touched.** Neither you, your code run by hand, nor your builder tests create, write, list or remove anything in the real `~/gov-os-runs/` (it does not exist, and nobody creates it in this run), the real `~/gov-os-worktrees/` or the real `~/gov-os-workbench/`. Every run of the code under test that could make or reach the root gets a temporary `HOME` (and a `TMPDIR` disjoint from it), as the acceptance suite does. Run no `local_only` live-launch case: use `-m "not local_only"` for W1-46 and W1-50. Before you return, run `test -e ~/gov-os-runs && echo PRESENT || echo ABSENT` and quote the output: it must print ABSENT.
- Never copy the repository or a folder of it (`cp -r`, `rsync`, `git archive`, `git worktree`, `git clone` of this repository or a folder of it) anywhere; copy single named files only, never `governance/project/`. A builder test that needs a repository builds a temporary one from scratch. Links a builder test needs are made in its temporary folder, never in the repository. No clone, copy or file of a programme is ever put under a `.gov-runtime/` folder (DEC-673).
- Inside a launched session `.gov-runtime/freeze` shows as a placeholder device file whether or not a flag exists: conclude nothing from it.
- The guard refuses here-documents and unresolvable variables in Bash write targets: write files with the Write and Edit tools and literal absolute paths. No subagents that write. Install nothing: a tool you need is returned as a package. No push, merge, rebase or tag. Never write `.gov-runtime/**` outside `.gov-runtime/scratch/`. Never run `gov rebuild --no-embeddings`, `gov close`, `gov adopt` or `gov pause` against this worktree or the main tree. Do not run `docs/plan/tools/validate_s1.py` (DEC-738 item 2). Never write under `src/gov/close/**` or `tests/unit/close/**`, nor `template/governance/kernel/checks/product-traceability-trailers.yaml`.
- Refused twice for the same call: stop and say so; no third try (AR-6).
- If the guard or the sandbox refuses something you needed for the ticket, do not work around it: return it as a package. On an authentication or access error (401, 403, "Failed to authenticate", "access grant"), stop and return status AUTH_REQUIRED.
- Your temporary folder is removed when your session ends (DEC-386): everything the lead needs is in your final message.

## The owner's DEC-774 and DEC-778 (2026-10-18; staged for the owner's commit, not in this worktree's register — apply them as written here)

- **DEC-774, finding D:** `cp -b` (`--backup`), `install`, `mv` and `cp --remove-destination` onto a symbolic link replace the link with a new file at the link's own path, while the guard judges the link's target. So where such a link already sits at a protected name (an acceptance test, another ticket's file or folder), a session puts a file there.
  - **The guard refuses as doubt a write that replaces a link rather than following it.** This covers the four forms above and any other form of `cp`, `install` or `mv` whose write replaces the link at its own path.
  - Ordinary writes through a link to an allowed target, and every copy, install and move run 6 allows into allowed folders, still pass.
  - The fix for D is in `src/gov/guard/decide.py`.
- **DEC-778, one option reader:** `src/gov/guard/protected.py` still reads `mv` and `cp -l` with the old option reader, the one DEC-765 replaced for `cp` and `install` (a `t` inside an option's value read as `-t`; `--` ignored). That file holds the guard's refusal to read protected material. **It stops using its old option reader for `mv` and `cp -l` and uses the reader this ticket built for `cp` and `install`, so the guard reads every copy-like command one way, for writes and for reads.** This ticket's `allowed_paths` now hold `src/gov/guard/protected.py` and `tests/unit/guard/test_protected*` (committed in the ticket file, `b4172c59`).
- `ln -f`/`ln -sf` onto the own folder's marker is row W2-L354, a FIFO in the marker's place row W2-L350: **not this round's work.**
- **If a fix needs a path outside this ticket's `allowed_paths`, stop and return PACKAGES naming the file.**

## What you read

- The ticket file `.tickets/DAEO-kl5e.md` (read-only): its KPI lines, its `allowed_paths` and its body.
- The approved proposal `docs/changes/W2-50-CIT-P.md` and the record `docs/changes/W2-50-CIT-E.md` (its §10 in particular).
- The acceptance tests and their README (read-only): `tests/acceptance/W2-50/`, in particular `test_w2_50_link_replaced.py` (D), `test_w2_50_one_reader.py` (DEC-778) and the README's sections on them.
- **The failing output:** `/home/usain/gov-os-worktrees/W2-50/.gov-runtime/scratch/lead/log/red-8.txt` — the suite at `397a80de`: 104 failed, 509 passed (58 D cases allowed; 38 second names of the stand-in protected file allowed for the orchestrator; 8 refused for the engineer by the write rule instead of as reads).
- The decisions, in `docs/DECISION_REGISTER.md`: DEC-728, DEC-108, DEC-135, DEC-311, DEC-334, DEC-548, DEC-553. The code: `src/gov/guard/decide.py`, `src/gov/guard/protected.py` (and `src/gov/guard/runs.py` for reading).

## What you write

- Only inside the ticket's `allowed_paths`: `src/gov/guard/decide.py` (D) and `src/gov/guard/protected.py` (DEC-778) for the fix; `tests/unit/guard/test_runs*` and `tests/unit/guard/test_protected*` for builder tests; `docs/changes/W2-50-CIT-E.md`.
- Never the acceptance tests (MR-3). A test you think is wrong is returned as a package, never edited and never worked around.
- Builder tests as regression evidence only, with a temporary `HOME` and a temporary project.
- Proportion (DEC-135): no code for edge cases beyond what the failing tests, DEC-774, DEC-778 and the KPI lines ask. **Never make a guard decision fail open:** every case that refuses today must still refuse (the suite's earlier cases, W1-02's, W1-03's and W1-46's among them), and a form whose effect on a link the guard cannot tell refuses. An ordinary copy, install or move into a folder the session may write, and an ordinary `mv` or `cp -l` of an unprotected file, must still be allowed. Keep the guard's decision fast: the latency cases `test_a_call_waits_under_100_ms_p95_for_the_hook` (W1-05) and `test_decision_p95_is_under_100_ms` (W1-02) must still pass (run such a file alone if it fails under machine load, and report it).
- Run, in the foreground, each suite to its end, never with `-x`:
  - `PATH=/home/usain/.nvm/versions/node/v22.23.3/bin:$PATH PYTHONPATH=/home/usain/gov-os-worktrees/W2-50/src python3 -m pytest tests/acceptance/W2-50 -q -p no:cacheprovider -rs` until all pass (in separate runs of its files if the folder outlives one call);
  - the earlier suites of the code you touch, the same way: W1-02, W1-03, W1-04, W1-05, W1-28, W1-32, W1-38, W1-46 and W1-50 (these two with `-m "not local_only"`), W1-48, and any other you judge touched (name each);
  - the builder tests: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-50/src python3 -m pytest tests/unit -q -p no:cacheprovider`.
- **Then the record.** Add a new section (§11) at the end of `docs/changes/W2-50-CIT-E.md`, for this round: DEC-774 and DEC-778; what holds after this round for both (which forms that replace a link are refused as doubt, which writes through a link still pass; how the read rule now reads `mv` and `cp -l`, and that it is the same reader as the write rule's); **the correction of §10's claims**, stated as a correction (what §10 claimed about backups and W2-H056, and what did not hold at `2d60cdd3`: a link destination replaced by `cp -b`/`--backup`/`-S`, `install`, `mv`, `cp --remove-destination`; and that §10 did not name the read rule's older reader); what stays open (W2-L354, W2-L350, and any form you know the guard still does not read); what the repair changed; the new commits; the lines added and removed. Do not rewrite §10 or any earlier section in place. Keep its frontmatter valid against `template/governance/kernel/schemas/change-execution-record.schema.json`; if the frontmatter lists commits or sections, bring it up to date. Say only what holds: each claim in §11 must be one the acceptance tests or your builder tests hold, or be marked as not tested.

## Commit

Before each commit, check that `/home/usain/Dynamic-Agentic-Engineering-OS/.git/hooks` holds no `pre-commit` file (only `*.sample` files); if one is there, stop and say so. Never `--no-verify`, never `core.hooksPath`. Two commits, only your paths, with the trailers in the final block:

    git commit -m "W2-50 (DAEO-kl5e): the last round — a write that replaces a link refused as doubt, one option reader for reads and writes (DEC-774, DEC-778)" --trailer "Task: DAEO-kl5e" --trailer "Role: engineer" --trailer "Implements: DEC-728" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
    git commit -m "W2-50 (DAEO-kl5e): the CIT-E's §11 for the DEC-774/DEC-778 round, correcting §10's claims" --trailer "Task: DAEO-kl5e" --trailer "Role: engineer" --trailer "Implements: DEC-728" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"

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

In those fields give: both commits' hashes and trailers; the files changed; the lines added and removed (`git show --shortstat` of the repair commit); the interface as changed (which forms are refused as doubt, how the read rule reads `mv` and `cp -l`); every suite you ran with its counts; the `gov.__file__` line; the `~/gov-os-runs` ABSENT line; anything you were refused or could not settle, as a package (question, why now, options, impact, reversibility, cost, recommendation, confidence). Refused twice for the same call: stop and say so.
