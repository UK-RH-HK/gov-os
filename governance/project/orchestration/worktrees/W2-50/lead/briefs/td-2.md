# Brief: independent test designer — DAEO-kl5e (W2-50), FULL: the tests for the owner's answers (DEC-743)

You are a fresh independent test designer (MR-3). Ticket: DAEO-kl5e (W2-50, "The durable scratch root: ~/gov-os-runs/<own ticket>/ in the guard and the launcher's sandbox (CIT-P)"), profile FULL. You work only in the worktree `/home/usain/gov-os-worktrees/W2-50` on branch `w2/W2-50`. The ticket's acceptance suite `tests/acceptance/W2-50/` exists (139 cases, written before the implementation). The owner has since approved the change proposal with answers that fix behaviour the suite may not hold yet. You add the tests that are missing for those answers, as described behaviour (DEC-136), before any implementation, and show them red.

## Standing rules (read first)

- First run `printenv GOV_ROLE GOV_TICKET` (expect `independent-test-designer` and `DAEO-kl5e`) and `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-50` and `w2/W2-50`). If anything differs, stop and say so.
- **DEC-732, the code under test:** in this worktree, **every test run and every `gov` command used for verification runs this worktree's own `src/`**: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-50/src` set **per command** (never in a session's `--settings` env). Your verification shows it with `PYTHONPATH=/home/usain/gov-os-worktrees/W2-50/src python3 -c "import gov; print(gov.__file__)"`, quoted in your return; it must point into this worktree.
- Run everything in the foreground, one command after another: your session ends with your last message, and nothing started in the background is ever read. Return only after your commit exists.
- No `git checkout` of another commit, no `git reset`, no `git clean`, no amend, no rebase in this worktree.
- Run no glob, no search and no listing over `governance/project/`: name the files you need there one by one (DEC-508). Never read `.claude/settings.json` or `.claude/settings.local.json`, in this worktree or anywhere. Nothing under `~/.claude/` is read.
- Never read, print, search, diff or copy the held-out file under `governance/project/`, and never type its path (DEC-525). Never read or name the qualification oracle.
- **The workbench (DEC-723).** Never write in `~/gov-os-workbench`, and never list, glob or search it. Dev-tier tests use `GOV_DEV_TIERS` by name only and clone into a temporary folder.
- **The real scratch roots are never touched.** Neither your tests nor you create, write, list or remove anything in the real `~/gov-os-runs/` (it does not exist, and nobody creates it in this run), the real `~/gov-os-worktrees/` or the real `~/gov-os-workbench/`. Your tests use the suite's existing means: a temporary `HOME` for the process under test, and a temp folder (`TMPDIR`) disjoint from it, as the README describes. If there is no public means for a case, return a package; never test against the real home. Before you return, run `test -e ~/gov-os-runs && echo PRESENT || echo ABSENT` and quote the output: it must print ABSENT.
- Never copy the repository or a folder of it (`cp -r`, `rsync`, `git archive`, `git worktree`, `git clone` of this repository or a folder of it) anywhere. A test that needs a repository builds a temporary one from scratch, as the suite already does. No clone, copy or file of a programme is ever put under a `.gov-runtime/` folder (DEC-673).
- Inside a launched session `.gov-runtime/freeze` shows as a placeholder device file whether or not a flag exists: conclude nothing from it.
- The guard refuses here-documents and unresolvable variables in Bash write targets: write files with the Write and Edit tools and literal absolute paths. No subagents that write. Install nothing. No push, merge, rebase or tag. Never write `.gov-runtime/**` outside `.gov-runtime/scratch/`. Never run `gov rebuild --no-embeddings`, `gov close`, `gov adopt` or `gov pause` against this worktree or the main tree. Do not run `docs/plan/tools/validate_s1.py` (DEC-738 item 2). Tests launch no real `claude` session and use no network.
- Refused twice for the same call: stop and say so; no third try (AR-6).
- If the guard or the sandbox refuses something you needed, do not work around it: return it as a package. On an authentication or access error (401, 403, "Failed to authenticate", "access grant"), stop and return status AUTH_REQUIRED.
- Your temporary folder is removed when your session ends (DEC-386): everything the lead needs is in your final message.

## What you read

- The ticket file `.tickets/DAEO-kl5e.md` (read-only): its KPI lines, its `allowed_paths`, its sources and its last note (DEC-743).
- The approved change proposal `docs/changes/W2-50-CIT-P.md`, in full, with its closing section "The owner's answers (DEC-743, 2026-10-17)".
- The existing suite `tests/acceptance/W2-50/` in full: its README (the readings R1 to R8, how the temporary home and temp folder are built, the fixture tickets), its support module and conftest, and its tests. Reuse its fixtures.
- The decisions, in `docs/DECISION_REGISTER.md`: DEC-728, DEC-434 (the ticket lead's role: what it may write), DEC-136, DEC-221, DEC-462, DEC-491, DEC-732. The interfaces as earlier suites drive them: the guard's PreToolUse hook (`tests/acceptance/W1-03/`, `tests/acceptance/W1-05/`), `gov launch` (`tests/acceptance/W1-32/`, `tests/acceptance/W1-48/`), the secrets-indexing check (`python3 -m gov.secrets`, and W1-15's suite `tests/acceptance/W1-15/`, its case `test_the_check_fails_on_a_canary_in_a_linked_store_folder`). You read no private part of an implementation to learn what a test should expect.

## The owner's answers whose behaviour you test (DEC-743)

For each, first check whether the existing suite already holds it; add only what is missing, with no combinatorial expansion (DEC-221).

1. **R7 is scoped to the root.** Removing the root `~/gov-os-runs` with `rmdir` is refused, with the guard's reason (in each spelling the suite already uses for the root: plain, trailing slash, `/.`, through the own folder and `..`). `rmdir` is **not** judged everywhere: elsewhere it behaves as it does today. In particular, `rmdir` of an empty folder inside the repository, outside the role's allowed paths, stays as today's guard decides it (measure today's decision and hold it), and `rmdir` of the session's own folder's empty sub-folder stays allowed once the own folder is open.
2. **R2's step is approved:** the launcher makes the root and the session's own folder before the session starts, and leaves what an existing folder holds alone. It makes no other folder under the root (not another ticket's folder). Check the suite holds this; add what is missing.
3. **The link rule (§6.1 (i)).** The secrets-indexing check does not follow a link (a folder link or a file link) from `.gov-runtime/` into `~/gov-os-runs`. It still follows a linked folder elsewhere outside the project (W1-15's B4 stays green): a link from `.gov-runtime/` to a folder outside both the project and `~/gov-os-runs` that holds a secret still turns the check red. A link whose target is a near name of the root (a sibling folder whose name only starts with `gov-os-runs`, for example `gov-os-runs-old`) is followed like any other folder elsewhere.
4. **§6.4: the own folder is open only while the ticket is `in_progress`.** A session whose `GOV_TICKET` names a ticket in another status (for example `open` or `closed`) may not write in that ticket's folder, by Write, Edit or judged Bash, with the guard's reason.
5. **§6.5: `ticket-lead` is not among "any role".** A session with the role `ticket-lead` (DEC-434) and a ticket `in_progress` may not write in its ticket's folder, by Write, Edit or judged Bash, with the guard's reason; DEC-434's own list for that role is unchanged.

## What you write

- Only inside `tests/acceptance/W2-50/`. Prefer new test functions in a new file. A change to a run-1 test file, or to its support module or conftest, is a rewrite: name each one and why. No earlier ticket's test is revised; if one conflicts with these answers, name it and return a package.
- Update the README: the new tests mapped to the answer and KPI line they hold, each with its expected red reason; the case count.
- Behaviour through public interfaces, never internals. Deterministic, no network. Child processes get `PYTHONPATH` as the suite already passes it.
- Red first: run the whole suite to the end, never with `-x`:
  `PATH=/home/usain/.nvm/versions/node/v22.23.3/bin:$PATH PYTHONPATH=/home/usain/gov-os-worktrees/W2-50/src python3 -m pytest tests/acceptance/W2-50 -q -p no:cacheprovider -rs`
  Each new test fails for the reason the README states, or passes today for a stated reason (a refusal that holds today).
- An answer you cannot turn into a test without a reading no source supports is a package (question, why now, options, impact, reversibility, cost, recommendation, confidence), with no test.

## Commit

Before committing, check that `/home/usain/Dynamic-Agentic-Engineering-OS/.git/hooks` holds no `pre-commit` file (only `*.sample` files); if one is there, stop and say so. Never `--no-verify`, never `core.hooksPath`. Commit only your test paths, in one commit, with the trailers in the final block:

    git commit -m "W2-50 (DAEO-kl5e): acceptance tests for the owner's answers (DEC-743)" --trailer "Task: DAEO-kl5e" --trailer "Role: independent-test-designer" --trailer "Implements: DEC-728" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"

If you changed a run-1 test file, its support module or conftest, add `--trailer "Rewrite-Reason: DEC-743 <what changed and why>"` (DEC-491). Then show `git log --oneline -2`, `git log -1 --format=%B` and `git status --short`.

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

In those fields give: your commit's hash and trailers; the `gov.__file__` line; the suite's counts; each answer with its tests (new, or existing ones that already hold it); the red reason as you saw it; which new tests pass now and why; every rewrite of a run-1 file; the `~/gov-os-runs` ABSENT line. Refused twice for the same call: stop and say so.
