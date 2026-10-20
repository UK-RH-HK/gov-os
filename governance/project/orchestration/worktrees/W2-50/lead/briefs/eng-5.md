# Brief: engineer (one more short round, DEC-764 and DEC-765) — DAEO-kl5e (W2-50), FULL

You are a fresh engineer. Ticket: DAEO-kl5e (W2-50, "The durable scratch root: ~/gov-os-runs/<own ticket>/ in the guard and the launcher's sandbox (CIT-P)"), profile FULL. You work only in the worktree `/home/usain/gov-os-worktrees/W2-50` on branch `w2/W2-50`, at head `41aa00c0` or later. The ticket is implemented; the review of the last round found two behaviours missing (A and B), the owner decided them (DEC-764 and DEC-765, below), and new acceptance tests fail against the code. You repair the code until the whole acceptance suite passes, then add one section to the change-execution record.

## Standing rules (read first)

- First run `printenv GOV_ROLE GOV_TICKET` (expect `engineer` and `DAEO-kl5e`) and `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-50` and `w2/W2-50`). If anything differs, stop and say so.
- **DEC-732, the code under test:** in this worktree, **every test run and every `gov` command used for verification runs this worktree's own `src/`**: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-50/src` set **per command** (never in a session's `--settings` env). Your verification shows it with `PYTHONPATH=/home/usain/gov-os-worktrees/W2-50/src python3 -c "import gov; print(gov.__file__)"`, quoted in your return; it must point into this worktree.
- **Your own guard runs the code you change (DEC-751 item 6).** The guard's hook in your session runs **this worktree's** `src/`, not the main tree's. A change to `src/gov/guard/decide.py` therefore also confines you at once, and a broken file there breaks your own hook. So: make each edit leave the file importable and whole (prefer one complete edit over several half-steps); the very next command after any edit to it is `PYTHONPATH=/home/usain/gov-os-worktrees/W2-50/src python3 -m pytest tests/unit/guard -q -p no:cacheprovider`, and you do not end the step (or go on to other work) until it passes. If your tools start being refused after such an edit, do not work around it: stop and return a package with the exact refusal text. Note that after your change, your own `cp`/`install`/`mv` calls are judged by the new rules too.
- Run everything in the foreground, one command after another: your session ends with your last message, and nothing started in the background is ever read. Return only after your commits exist.
- No `git checkout` of another commit, no `git reset`, no `git clean`, no amend, no rebase in this worktree.
- Run no glob, no search and no listing over `governance/project/`: name the files you need there one by one (DEC-508). Never read `.claude/settings.json` or `.claude/settings.local.json`, in this worktree or anywhere. Nothing under `~/.claude/` is read.
- Never read, print, search, diff or copy the held-out file under `governance/project/`, and never type its path (DEC-525). Never read or name the qualification oracle.
- **The workbench (DEC-723).** Never write in `~/gov-os-workbench`, and never list, glob or search it. Dev-tier tests use `GOV_DEV_TIERS` by name only and clone into a temporary folder.
- **The real scratch roots are never touched.** Neither you, your code run by hand, nor your builder tests create, write, list or remove anything in the real `~/gov-os-runs/` (it does not exist, and nobody creates it in this run), the real `~/gov-os-worktrees/` or the real `~/gov-os-workbench/`. Every run of the code under test that could make or reach the root gets a temporary `HOME` (and a `TMPDIR` disjoint from it), as the acceptance suite does. Run no `local_only` live-launch case: use `-m "not local_only"` for W1-46 and W1-50. Before you return, run `test -e ~/gov-os-runs && echo PRESENT || echo ABSENT` and quote the output: it must print ABSENT.
- Never copy the repository or a folder of it (`cp -r`, `rsync`, `git archive`, `git worktree`, `git clone` of this repository or a folder of it) anywhere; copy single named files only, never `governance/project/`. A builder test that needs a repository builds a temporary one from scratch. No clone, copy or file of a programme is ever put under a `.gov-runtime/` folder (DEC-673).
- Inside a launched session `.gov-runtime/freeze` shows as a placeholder device file whether or not a flag exists: conclude nothing from it.
- The guard refuses here-documents and unresolvable variables in Bash write targets: write files with the Write and Edit tools and literal absolute paths. No subagents that write. Install nothing: a tool you need is returned as a package. No push, merge, rebase or tag. Never write `.gov-runtime/**` outside `.gov-runtime/scratch/`. Never run `gov rebuild --no-embeddings`, `gov close`, `gov adopt` or `gov pause` against this worktree or the main tree. Do not run `docs/plan/tools/validate_s1.py` (DEC-738 item 2). Never write under `src/gov/close/**` or `tests/unit/close/**`, nor `template/governance/kernel/checks/product-traceability-trailers.yaml`.
- Refused twice for the same call: stop and say so; no third try (AR-6).
- If the guard or the sandbox refuses something you needed for the ticket, do not work around it: return it as a package. On an authentication or access error (401, 403, "Failed to authenticate", "access grant"), stop and return status AUTH_REQUIRED.
- Your temporary folder is removed when your session ends (DEC-386): everything the lead needs is in your final message.

## The owner's DEC-764 and DEC-765 (2026-10-18; staged for the owner's commit, not in this worktree's register — apply them as written here)

- **DEC-764: one more short round, tests first.**
  - **A:** the guard refuses `cp --parents` (and every copy, install or move option that makes the landed path other than `<folder>/<name>`) **as doubt**, the way `ln -t` is refused today.
  - **The change record is corrected:** a new section of `docs/changes/W2-50-CIT-E.md` states what holds after this round and corrects §9's claim (that every copy into a folder is judged file by file and that W2-H056 is closed); §9 is not rewritten in place.
- **DEC-765: in the same round,** the guard reads option values as values and honours `--`: the short options that take a value (among them `-S`, `-o`, `-g`, `-m`, `-Z`, joined to the letter or separate, and their long forms) never read as `-t`; nothing after `--` is read as an option, and the destination is still judged. `cp -S.t`, `cp -bS.t`, `install -S.t`, `install -oroot`, `install -m+t` onto an acceptance test, and `cp -- -t F`, are judged as the files they write (B).
  - `ln -f`/`ln -sf` onto the own folder's marker is row W2-L354 and a FIFO in the marker's place is row W2-L350: **not this round's work.**
- **Note on `-Z`:** on this machine (GNU coreutils 9.4) `cp -Z`, `install -Z` and `mv -Z` take **no** value (`--context[=CTX]` takes one only after `=`). So `cp -Zt <folder> X` is a copy into `<folder>` and must stay judged as one; the acceptance suite holds this as a fail-closed control. Whatever the guard does with `-Z`, it must never make such a call less judged.
- **The fix is in `src/gov/guard/decide.py`.** If it needs a path outside this ticket's `allowed_paths`, stop and return PACKAGES naming the file.

## What you read

- The ticket file `.tickets/DAEO-kl5e.md` (read-only): its KPI lines, its `allowed_paths` and its body.
- The approved proposal `docs/changes/W2-50-CIT-P.md` and the record `docs/changes/W2-50-CIT-E.md` (its §9 in particular).
- The acceptance tests and their README (read-only): `tests/acceptance/W2-50/`, in particular the new file `test_w2_50_short_round.py` and the README's section on the tests from the review of the last round.
- **The failing output:** `/home/usain/gov-os-worktrees/W2-50/.gov-runtime/scratch/lead/log/red-6.txt` — the suite at `41aa00c0`.
- The decisions, in `docs/DECISION_REGISTER.md`: DEC-728, DEC-108, DEC-135, DEC-311, DEC-334. The code: `src/gov/guard/decide.py` (and `src/gov/guard/runs.py` for reading).

## What you write

- Only inside the ticket's `allowed_paths`: `src/gov/guard/decide.py` for the fix; `src/gov/guard/runs.py`, `src/gov/guard/runs.py`'s neighbours named in the ticket only if strictly needed; `tests/unit/guard/test_runs*` for builder tests; `docs/changes/W2-50-CIT-E.md`.
- Never the acceptance tests (MR-3). A test you think is wrong is returned as a package, never edited and never worked around.
- Builder tests in `tests/unit/guard/test_runs*`, as regression evidence only, with a temporary `HOME`.
- Proportion (DEC-135): no code for edge cases beyond what the failing tests, DEC-764, DEC-765 and the KPI lines ask. **Never make a guard decision fail open:** every case that refuses today must still refuse (the suite's earlier 305 cases, W1-46's and W1-03's copy forms among them), and any form whose landed path the guard cannot tell refuses. An ordinary copy, install or move into a folder the session may write must still be allowed. Keep the guard's decision fast: the latency cases `test_a_call_waits_under_100_ms_p95_for_the_hook` (W1-05) and `test_decision_p95_is_under_100_ms` (W1-02) must still pass (run such a file alone if it fails under machine load, and report it).
- Run, in the foreground, each suite to its end, never with `-x`:
  - `PATH=/home/usain/.nvm/versions/node/v22.23.3/bin:$PATH PYTHONPATH=/home/usain/gov-os-worktrees/W2-50/src python3 -m pytest tests/acceptance/W2-50 -q -p no:cacheprovider -rs` until all 358 pass;
  - the earlier suites of the code you touch, the same way: W1-02, W1-03, W1-04, W1-05, W1-28, W1-32, W1-38, W1-46 and W1-50 (these two with `-m "not local_only"`), W1-48, and any other you judge touched (name each);
  - the builder tests: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-50/src python3 -m pytest tests/unit -q -p no:cacheprovider`.
- **Then the record.** Add a new section (§10) at the end of `docs/changes/W2-50-CIT-E.md`, for this round: DEC-764 and DEC-765; what holds after this round (which copy, install and move forms are judged file by file, which are refused as doubt, how option values and `--` are read); **the correction of §9's claims**, stated as a correction (what §9 claimed, what did not hold at `8a310cb2`: `cp --parents` and the option parser; whether W2-H056 is closed now, and on what grounds); what stays open (W2-L354, W2-L350, and any form you know the guard still does not read); what the repair changed; the new commits; the lines added and removed. Do not rewrite §9 or any earlier section in place. Keep its frontmatter valid against `template/governance/kernel/schemas/change-execution-record.schema.json`; if the frontmatter lists commits or sections, bring it up to date. Say only what holds: each claim in §10 must be one the acceptance tests or your builder tests hold, or be marked as not tested.

## Commit

Before each commit, check that `/home/usain/Dynamic-Agentic-Engineering-OS/.git/hooks` holds no `pre-commit` file (only `*.sample` files); if one is there, stop and say so. Never `--no-verify`, never `core.hooksPath`. Two commits, only your paths, with the trailers in the final block:

    git commit -m "W2-50 (DAEO-kl5e): one more short round — cp --parents refused as doubt, option values read as values, -- honoured (DEC-764, DEC-765)" --trailer "Task: DAEO-kl5e" --trailer "Role: engineer" --trailer "Implements: DEC-728" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
    git commit -m "W2-50 (DAEO-kl5e): the CIT-E's §10 for the DEC-764/DEC-765 round, correcting §9's claims" --trailer "Task: DAEO-kl5e" --trailer "Role: engineer" --trailer "Implements: DEC-728" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"

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

In those fields give: both commits' hashes and trailers; the files changed; the lines added and removed (`git show --shortstat` of the repair commit); the interface as changed (which forms are refused as doubt, how values and `--` are read); every suite you ran with its counts; the `gov.__file__` line; the `~/gov-os-runs` ABSENT line; anything you were refused or could not settle, as a package (question, why now, options, impact, reversibility, cost, recommendation, confidence). Refused twice for the same call: stop and say so.
