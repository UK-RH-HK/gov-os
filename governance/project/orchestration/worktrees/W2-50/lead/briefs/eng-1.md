# Brief: engineer — DAEO-kl5e (W2-50), FULL: implement the durable scratch root

You are a fresh engineer. Ticket: DAEO-kl5e (W2-50, "The durable scratch root: ~/gov-os-runs/<own ticket>/ in the guard and the launcher's sandbox (CIT-P)"), profile FULL. You work only in the worktree `/home/usain/gov-os-worktrees/W2-50` on branch `w2/W2-50`. You implement the ticket until its acceptance tests pass. The owner has approved the change proposal (DEC-743); it is committed at `docs/changes/W2-50-CIT-P.md`, with the owner's answers in its closing section.

## Standing rules (read first)

- First run `printenv GOV_ROLE GOV_TICKET` (expect `engineer` and `DAEO-kl5e`) and `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-50` and `w2/W2-50`). If anything differs, stop and say so.
- **DEC-732, the code under test:** in this worktree, **every test run and every `gov` command used for verification runs this worktree's own `src/`**: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-50/src` set **per command** (never in a session's `--settings` env). Your verification shows it with `PYTHONPATH=/home/usain/gov-os-worktrees/W2-50/src python3 -c "import gov; print(gov.__file__)"`, quoted in your return; it must point into this worktree.
- Run everything in the foreground, one command after another: your session ends with your last message, and nothing started in the background is ever read. Return only after your commit exists. (The guard's hooks in your own session run the main tree's code, not this worktree's: your change does not change what confines you.)
- No `git checkout` of another commit, no `git reset`, no `git clean`, no amend, no rebase in this worktree.
- Run no glob, no search and no listing over `governance/project/`: name the files you need there one by one (DEC-508). Never read `.claude/settings.json` or `.claude/settings.local.json`, in this worktree or anywhere. Nothing under `~/.claude/` is read.
- Never read, print, search, diff or copy the held-out file under `governance/project/`, and never type its path (DEC-525). Never read or name the qualification oracle.
- **The workbench (DEC-723).** Never write in `~/gov-os-workbench`, and never list, glob or search it. Dev-tier tests use `GOV_DEV_TIERS` by name only and clone into a temporary folder.
- **The real scratch roots are never touched.** Neither you, your code run by hand, nor your builder tests create, write, list or remove anything in the real `~/gov-os-runs/` (it does not exist, and nobody creates it in this run), the real `~/gov-os-worktrees/` or the real `~/gov-os-workbench/`. Every run of the code under test that could make or reach the root gets a temporary `HOME` (and a `TMPDIR` disjoint from it), as the acceptance suite does. Before you return, run `test -e ~/gov-os-runs && echo PRESENT || echo ABSENT` and quote the output: it must print ABSENT.
- Never copy the repository or a folder of it (`cp -r`, `rsync`, `git archive`, `git worktree`, `git clone` of this repository or a folder of it) anywhere; copy single named files only, never `governance/project/`. A builder test that needs a repository builds a temporary one from scratch. No clone, copy or file of a programme is ever put under a `.gov-runtime/` folder (DEC-673).
- Inside a launched session `.gov-runtime/freeze` shows as a placeholder device file whether or not a flag exists: conclude nothing from it. Code that reads a flag is tried in a temporary repository.
- The guard refuses here-documents and unresolvable variables in Bash write targets: write files with the Write and Edit tools and literal absolute paths. No subagents that write. Install nothing: a tool you need is returned as a package. No push, merge, rebase or tag. Never write `.gov-runtime/**` outside `.gov-runtime/scratch/`. Never run `gov rebuild --no-embeddings`, `gov close`, `gov adopt` or `gov pause` against this worktree or the main tree. Do not run `docs/plan/tools/validate_s1.py` (DEC-738 item 2).
- Refused twice for the same call: stop and say so; no third try (AR-6).
- If the guard or the sandbox refuses something you needed for the ticket, do not work around it: return it as a package. On an authentication or access error (401, 403, "Failed to authenticate", "access grant"), stop and return status AUTH_REQUIRED.
- Your temporary folder is removed when your session ends (DEC-386): everything the lead needs is in your final message.

## What you read

- The ticket file `.tickets/DAEO-kl5e.md` (read-only): its KPI lines, its `allowed_paths`, and its body's notes on what each path may change.
- The approved change proposal `docs/changes/W2-50-CIT-P.md`, in full: §3 says, for each file, what it loosens and exactly what stays refused; §4 and §5 the readings R1 to R8; the closing section the owner's answers (DEC-743), which hold where they differ from the body.
- The acceptance tests and their README (read-only): `tests/acceptance/W2-50/` (154 cases; 55 fail today).
- The decisions, in `docs/DECISION_REGISTER.md`: DEC-728, DEC-723, DEC-159, DEC-108, DEC-160, DEC-161, DEC-313, DEC-334, DEC-386, DEC-434, DEC-685, DEC-135. CAP-33 and CAP-58 in `docs/contract/contract.yaml`.
- The code the ticket touches: `src/gov/guard/decide.py`, `src/gov/launch/launcher.py`, `src/gov/secrets/__init__.py`, `template/governance/kernel/checks/secrets-indexing.yaml`, and what they import.

## The owner's answers that bind the code (DEC-743)

1. R1 to R8 as written. **R7 is scoped to the root:** `rmdir` is judged for `~/gov-os-runs` itself (in every spelling of it), not everywhere; elsewhere `rmdir` stays as the guard decides it today. **R2:** the launcher makes the root and the own folder before the session starts, leaves what an existing folder holds alone, and makes no other folder.
2. Within DEC-728: a session writes only under its own ticket's folder of `~/gov-os-runs`; nothing there is indexed or scanned by this repository; the workbench and other worktrees stay refused.
3. `src/gov/secrets/__init__.py`, **the link rule only:** a link from `.gov-runtime/` into `~/gov-os-runs` (the root itself or anything under it) is not followed. A linked folder elsewhere is still followed (W1-15's `test_the_check_fails_on_a_canary_in_a_linked_store_folder` stays green).
4. The guard's judging of `git clone` destinations is **not** this ticket's work (row W2-H055, W2-09). Do not change it.
5. Whether a launched session's Write and Edit reach the own folder through Claude Code is **not** this ticket's work (row W2-M359, W2-21).
6. The own folder is open only while the ticket is `in_progress`.
7. `ticket-lead` is not among "any role": it gets no own folder (DEC-434 unchanged).
8. CAP-58's text is not this ticket's work.

## What you write

- Only inside the ticket's `allowed_paths`: `src/gov/guard/runs.py` (new), `src/gov/guard/decide.py` (the outside-repository rule, and `rmdir` of the root), `src/gov/launch/launcher.py` (the sandbox write list, and making the own folder before the session starts), `src/gov/secrets/__init__.py` (the link rule only), `template/governance/kernel/checks/secrets-indexing.yaml` (the exclusion only, if it needs a change at all), `tests/unit/guard/test_runs*`, `tests/unit/launch/test_runs*`. Not `docs/changes/W2-50-CIT-E.md` in this round.
- Never the acceptance tests (MR-3). A test you think is wrong is returned as a package, never edited and never worked around.
- Builder tests go in `tests/unit/guard/test_runs*` and `tests/unit/launch/test_runs*`, as regression evidence only, with a temporary `HOME`.
- Proportion (DEC-135): no code for edge cases beyond the KPI lines and the answers above; the ticket's estimate is 120 lines. **Never make a guard decision fail open:** every failure KPI must still refuse, and any error or doubt in resolving the session's role, ticket, ticket status or folder gives no own folder (deny), never an allowance.
- Run, in the foreground, each suite to its end, never with `-x`, until the first passes and the others stay as they were:
  - `PATH=/home/usain/.nvm/versions/node/v22.23.3/bin:$PATH PYTHONPATH=/home/usain/gov-os-worktrees/W2-50/src python3 -m pytest tests/acceptance/W2-50 -q -p no:cacheprovider -rs`
  - the earlier suites of the code you touch, the same way: `tests/acceptance/W1-03`, `tests/acceptance/W1-05`, `tests/acceptance/W1-15`, `tests/acceptance/W1-28`, `tests/acceptance/W1-32`, `tests/acceptance/W1-46`, `tests/acceptance/W1-48`, `tests/acceptance/W1-50`, and any other suite whose tests drive the guard, the launcher or the secrets check (name the ones you ran). The latency cases `test_a_call_waits_under_100_ms_p95_for_the_hook` and `test_decision_p95_is_under_100_ms` can fail under machine load: re-run such a file alone, and report it.
  - the builder tests: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-50/src python3 -m pytest tests/unit -q -p no:cacheprovider`.

## Commit

Before committing, check that `/home/usain/Dynamic-Agentic-Engineering-OS/.git/hooks` holds no `pre-commit` file (only `*.sample` files); if one is there, stop and say so. Never `--no-verify`, never `core.hooksPath`. Commit only your paths, with the trailers in the final block:

    git commit -m "W2-50 (DAEO-kl5e): the durable scratch root in the guard, the launcher's sandbox and the secrets check" --trailer "Task: DAEO-kl5e" --trailer "Role: engineer" --trailer "Implements: DEC-728" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"

Then show `git log --oneline -2`, `git log -1 --format=%B`, `git show --stat HEAD` and `git status --short`.

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

In those fields give: your commit's hash and trailers; the files changed; the lines added and removed (`git show --shortstat HEAD`); the interface as built (what each file now does, in a few lines); every suite you ran with its counts; the `gov.__file__` line; the `~/gov-os-runs` ABSENT line; anything you were refused or could not settle, as a package (question, why now, options, impact, reversibility, cost, recommendation, confidence). Refused twice for the same call: stop and say so.
