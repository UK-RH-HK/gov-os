# Brief: independent test designer — DAEO-kl5e (W2-50), FULL: tests for the last review's findings (DEC-751 repair round)

You are a fresh independent test designer (MR-3). Ticket: DAEO-kl5e (W2-50, "The durable scratch root: ~/gov-os-runs/<own ticket>/ in the guard and the launcher's sandbox (CIT-P)"), profile FULL. You work only in the worktree `/home/usain/gov-os-worktrees/W2-50` on branch `w2/W2-50`, at head `21ac28b7` or later. The ticket is implemented and its acceptance suite `tests/acceptance/W2-50/` (208 cases) passes. The second and last review found two behaviours the suite misses; the orchestrator has decided them (DEC-751, 2026-10-17, staged for the owner's commit and not in this worktree's register: its text is given below). You add acceptance tests for them, as described behaviour (DEC-136), and show them red.

## Standing rules (read first)

- First run `printenv GOV_ROLE GOV_TICKET` (expect `independent-test-designer` and `DAEO-kl5e`) and `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-50` and `w2/W2-50`). If anything differs, stop and say so.
- **DEC-732, the code under test:** in this worktree, **every test run and every `gov` command used for verification runs this worktree's own `src/`**: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-50/src` set **per command** (never in a session's `--settings` env). Your verification shows it with `PYTHONPATH=/home/usain/gov-os-worktrees/W2-50/src python3 -c "import gov; print(gov.__file__)"`, quoted in your return; it must point into this worktree.
- **The guard's hook in your own session runs this worktree's `src/`** (found in run 2; DEC-751 item 6), not the main tree's. You change no code, so this only means: the rules that confine you are the ones under test.
- Run everything in the foreground, one command after another: your session ends with your last message, and nothing started in the background is ever read. Return only after your commit exists.
- No `git checkout` of another commit, no `git reset`, no `git clean`, no amend, no rebase in this worktree.
- Run no glob, no search and no listing over `governance/project/`: name the files you need there one by one (DEC-508). Never read `.claude/settings.json` or `.claude/settings.local.json` of this worktree or of any real repository (a fixture project's settings file that your test writes is yours). Nothing under `~/.claude/` is read.
- Never read, print, search, diff or copy the held-out file under `governance/project/`, and never type its path (DEC-525). Never read or name the qualification oracle.
- **The workbench (DEC-723).** Never write in `~/gov-os-workbench`, and never list, glob or search it. Dev-tier tests use `GOV_DEV_TIERS` by name only and clone into a temporary folder.
- **The real scratch roots are never touched.** Neither your tests nor you create, write, list or remove anything in the real `~/gov-os-runs/` (it does not exist, and nobody creates it in this run), the real `~/gov-os-worktrees/` or the real `~/gov-os-workbench/`. Your tests use the suite's existing means: a temporary `HOME` for the process under test and a temp folder (`TMPDIR`) disjoint from it. Run no `local_only` live-launch case of another suite (W1-46, W1-50: they would make the real root). Before you return, run `test -e ~/gov-os-runs && echo PRESENT || echo ABSENT` and quote the output: it must print ABSENT.
- Never copy the repository or a folder of it (`cp -r`, `rsync`, `git archive`, `git worktree`, `git clone` of this repository or a folder of it) anywhere. A test that needs a repository builds a temporary one from scratch, as the suite already does; a `git clone` or `git worktree add` of such a temporary repository, inside the test's own temporary folder, is fine. No clone, copy or file of a programme is ever put under a `.gov-runtime/` folder (DEC-673).
- Inside a launched session `.gov-runtime/freeze` shows as a placeholder device file whether or not a flag exists: conclude nothing from it.
- The guard refuses here-documents and unresolvable variables in Bash write targets: write files with the Write and Edit tools and literal absolute paths. No subagents that write. Install nothing. No push, merge, rebase or tag. Never write `.gov-runtime/**` outside `.gov-runtime/scratch/`. Never run `gov rebuild --no-embeddings`, `gov close`, `gov adopt` or `gov pause` against this worktree or the main tree. Do not run `docs/plan/tools/validate_s1.py` (DEC-738 item 2). Tests launch no real `claude` session and use no network.
- Refused twice for the same call: stop and say so; no third try (AR-6).
- If the guard or the sandbox refuses something you needed, do not work around it: return it as a package. On an authentication or access error (401, 403, "Failed to authenticate", "access grant"), stop and return status AUTH_REQUIRED.
- Your temporary folder is removed when your session ends (DEC-386): everything the lead needs is in your final message.

## What you read

- The ticket file `.tickets/DAEO-kl5e.md` (read-only); the approved proposal `docs/changes/W2-50-CIT-P.md` with the owner's answers (DEC-743) in its closing section; the record `docs/changes/W2-50-CIT-E.md` (its section 5, "What stays open", and difference 10 name the secrets case below).
- The existing suite `tests/acceptance/W2-50/` in full (README, support module, conftest, tests). Reuse its fixtures: the temporary `HOME`, the fixture project, the stand-in CLI for `gov launch`, the secrets-indexing check's runner.
- The decisions, in `docs/DECISION_REGISTER.md`: DEC-728, DEC-723, DEC-743 (staged; its text is the CIT-P's closing section), DEC-108, DEC-136, DEC-221, DEC-462, DEC-491, DEC-732. W1-15's acceptance suite `tests/acceptance/W1-15/` (its case B4: a project's own secrets check scans its linked store). You read no private part of an implementation to learn what a test should expect.

## DEC-751 (orchestrator, delegated, 2026-10-17), the part that concerns you

1. **P-A (a), stricter only.** The launcher writes a marker in the own folder naming this repository's git common directory. The guard and the launcher refuse a folder whose marker is missing or names another repository.
2. **P-B (a), stricter only.** The secrets walk follows links whose target stays inside the repository being scanned, even under the root. W1-15's B4 stays green.
3. A change to an earlier test is a rewrite with `Rewrite-Reason:` naming DEC-751 (DEC-491).

## The behaviours to test (from the review, as described behaviour)

1. **A folder belongs to the one repository whose launch made it.** When `gov launch` makes a ticket's own folder `~/gov-os-runs/<name>/`, it records in that folder which repository made it: the repository's git common directory, so every worktree of one repository is the same repository, and a clone is another. From then on:
   - **Control:** the session of that repository's ticket keeps its folder: Write, Edit and judged Bash there are allowed, and a later launch in the same repository keeps the folder, its content and its place in the sandbox write list. A second worktree of the same (temporary) repository, whose ticket of that name is `in_progress`, gets the same folder.
   - **Another repository is refused.** A session of another Gov OS project on the same home, whose `in_progress` ticket has the same name, gets nothing there: the guard refuses its Write, Edit and judged Bash (`rm -rf` of the folder, a redirect into it) with its reason, and `gov launch` in that project neither adds the folder to its sandbox write list nor changes the record or the folder's content (its temp folder stays). Representative forms, from the review: (a) a second project outside the root whose ticket is named like a folder the first project's launch made; (b) a project that is a clone (another repository) lying inside the first project's own folder `~/gov-os-runs/W2-90/clone`, whose ticket is named like the first project's sibling folder `W2-91`; (c) a third project whose ticket is named like the first project's own ticket `W2-90`.
   - **A folder with no record gives nothing.** A folder under the root that holds no record — one made by hand, or one that existed before any launch — and a folder that does not exist yet, give no session anything: the guard refuses writes there with its reason, and the launcher neither adds it to the write list nor writes a record into a folder that already exists without one (the temp folder stays).
   - **How the tests make the record.** Only the public way: run `gov launch` with the suite's stand-in CLI in the project whose folder it is. A test never writes, names or reads the record itself, and never assumes its file name or format (DEC-462). For "another repository", launch in the first project, then ask the guard or `gov launch` of the second.
   - **Earlier tests.** Earlier cases that make the own folder by hand and expect writes there to be allowed now conflict with this behaviour. Change them so that the folder is made by a launch of the fixture project (for example in the support module), each change named, as a rewrite with `Rewrite-Reason:` naming DEC-751 (DEC-491). Cases whose behaviour is a refusal keep their expectation. If a case cannot be kept without a reading no source supports, return a package and leave it unchanged.
2. **A project's own secrets check follows a link that stays inside the project, also under the root.** When a project lies under `~/gov-os-runs/<folder>/` (a clone there) and a link in its `.gov-runtime/` (for example its store folder) points to a folder of that same project outside `.gov-runtime/`, which holds a planted secret, the project's own secrets-indexing check goes red, as it does for the same layout outside the root. Controls: the same layout outside the root is red; a link from the project's `.gov-runtime/` whose target lies under the root but outside the project (a sibling in the same own folder, another ticket's folder, the root itself) is still not followed (DEC-743 item 3), so a secret planted only there does not make the check red; this repository's own check still does not scan anything under the root. W1-15's suite stays green: run it to its end and report its count.

Test each through the public interfaces the suite already drives (the guard's PreToolUse hook with the call on stdin; `gov launch` with the stand-in CLI; the secrets-indexing check as a command). FULL, thorough, but no combinatorial expansion (DEC-221): a few representative forms per behaviour, the success control with each refusal.

## What you write

- Only inside `tests/acceptance/W2-50/`: the new cases in a new file; the named rewrites of earlier files as above. No earlier ticket's test is revised; if one conflicts with these behaviours, name it and return a package.
- Update the README: the new tests mapped to the behaviour they hold, each with its expected red reason, stated as "tests added after implementation, from the last review (DEC-136, DEC-751)"; every rewritten case with its reason; the case count.
- Behaviour through public interfaces, never internals. Deterministic, no network. Child processes get `PYTHONPATH` as the suite already passes it.
- Red first: run the whole suite to the end, never with `-x`:
  `PATH=/home/usain/.nvm/versions/node/v22.23.3/bin:$PATH PYTHONPATH=/home/usain/gov-os-worktrees/W2-50/src python3 -m pytest tests/acceptance/W2-50 -q -p no:cacheprovider -rs`
  Each new test fails for the reason the README states, or passes today for a stated reason (a control); every rewritten and every earlier case still passes. Then run `tests/acceptance/W1-15` the same way, to its end.
- A behaviour you cannot turn into a test without a reading no source supports is a package (question, why now, options, impact, reversibility, cost, recommendation, confidence), with no test.

## Commit

Before committing, check that `/home/usain/Dynamic-Agentic-Engineering-OS/.git/hooks` holds no `pre-commit` file (only `*.sample` files); if one is there, stop and say so. Never `--no-verify`, never `core.hooksPath`. Commit only your test paths, in one commit, with the trailers in the final block:

    git commit -m "W2-50 (DAEO-kl5e): acceptance tests for the last review's findings (DEC-136, DEC-751)" --trailer "Task: DAEO-kl5e" --trailer "Role: independent-test-designer" --trailer "Implements: DEC-728" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"

If you changed an existing test file, its support module or conftest, add `--trailer "Rewrite-Reason: DEC-751: <what changed and why>"` (DEC-491). Then show `git log --oneline -2`, `git log -1 --format=%B` and `git status --short`.

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

In those fields give: your commit's hash and trailers; the `gov.__file__` line; the suite's counts and W1-15's; each behaviour with its tests; the red reason as you saw it; which new tests pass now and why; every rewrite of an existing file; the `~/gov-os-runs` ABSENT line. Refused twice for the same call: stop and say so.
