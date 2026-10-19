# Brief: independent test designer — DAEO-kl5e (W2-50), FULL: tests for the last round (DEC-758 item 1)

You are a fresh independent test designer (MR-3). Ticket: DAEO-kl5e (W2-50, "The durable scratch root: ~/gov-os-runs/<own ticket>/ in the guard and the launcher's sandbox (CIT-P)"), profile FULL. You work only in the worktree `/home/usain/gov-os-worktrees/W2-50` on branch `w2/W2-50`, at head `19a4e9fd` or later. The ticket is implemented and repaired; its acceptance suite `tests/acceptance/W2-50/` (233 cases) passes. An extra independent review found two behaviours the suite misses; the owner has decided them (DEC-758, 2026-10-17, staged for the owner's commit and not in this worktree's register: its text is given below). You add acceptance tests for them, as described behaviour (DEC-136), and show them red.

## Standing rules (read first)

- First run `printenv GOV_ROLE GOV_TICKET` (expect `independent-test-designer` and `DAEO-kl5e`) and `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-50` and `w2/W2-50`). If anything differs, stop and say so.
- **DEC-732, the code under test:** in this worktree, **every test run and every `gov` command used for verification runs this worktree's own `src/`**: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-50/src` set **per command** (never in a session's `--settings` env). Your verification shows it with `PYTHONPATH=/home/usain/gov-os-worktrees/W2-50/src python3 -c "import gov; print(gov.__file__)"`, quoted in your return; it must point into this worktree.
- **The guard's hook in your own session runs this worktree's `src/`** (DEC-751 item 6), not the main tree's. You change no code, so this only means: the rules that confine you are the ones under test.
- Run everything in the foreground, one command after another: your session ends with your last message, and nothing started in the background is ever read. Return only after your commit exists.
- No `git checkout` of another commit, no `git reset`, no `git clean`, no amend, no rebase in this worktree.
- Run no glob, no search and no listing over `governance/project/`: name the files you need there one by one (DEC-508). Never read `.claude/settings.json` or `.claude/settings.local.json` of this worktree or of any real repository (a fixture project's settings file that your test writes is yours). Nothing under `~/.claude/` is read.
- Never read, print, search, diff or copy the held-out file under `governance/project/`, and never type its path (DEC-525). Never read or name the qualification oracle.
- **The workbench (DEC-723).** Never write in `~/gov-os-workbench`, and never list, glob or search it. Dev-tier tests use `GOV_DEV_TIERS` by name only and clone into a temporary folder.
- **The real scratch roots are never touched.** Neither your tests nor you create, write, list or remove anything in the real `~/gov-os-runs/` (it does not exist, and nobody creates it in this run), the real `~/gov-os-worktrees/` or the real `~/gov-os-workbench/`. Your tests use the suite's existing means: a temporary `HOME` for the process under test and a temp folder (`TMPDIR`) disjoint from it. Run no `local_only` live-launch case of another suite (W1-46, W1-50: they would make the real root). Before you return, run `test -e ~/gov-os-runs && echo PRESENT || echo ABSENT` and quote the output: it must print ABSENT.
- Never copy the repository or a folder of it (`cp -r`, `rsync`, `git archive`, `git worktree`, `git clone` of this repository or a folder of it) anywhere. A test that needs a repository builds a temporary one from scratch, as the suite already does; a `git clone` or `git worktree add` of such a temporary repository, inside the test's own temporary folder, is fine. No clone, copy or file of a programme is ever put under a `.gov-runtime/` folder (DEC-673).
- Inside a launched session `.gov-runtime/freeze` shows as a placeholder device file whether or not a flag exists: conclude nothing from it.
- The guard refuses here-documents and unresolvable variables in Bash write targets: write files with the Write and Edit tools and literal absolute paths. No subagents that write. Install nothing. No push, merge, rebase or tag. Never write `.gov-runtime/**` outside `.gov-runtime/scratch/`. Never run `gov rebuild --no-embeddings`, `gov close`, `gov adopt` or `gov pause` against this worktree or the main tree. Do not run `docs/plan/tools/validate_s1.py` (DEC-738 item 2). Tests launch no real `claude` session and use no network. Never write under `src/gov/close/**` or `tests/unit/close/**` (W2-53's, running beside you in its own worktree).
- Refused twice for the same call: stop and say so; no third try (AR-6).
- If the guard or the sandbox refuses something you needed, do not work around it: return it as a package. On an authentication or access error (401, 403, "Failed to authenticate", "access grant"), stop and return status AUTH_REQUIRED.
- Your temporary folder is removed when your session ends (DEC-386): everything the lead needs is in your final message.

## What you read

- The ticket file `.tickets/DAEO-kl5e.md` (read-only); the approved proposal `docs/changes/W2-50-CIT-P.md` with the owner's answers (DEC-743) in its closing section (R8, the link rule); the record `docs/changes/W2-50-CIT-E.md` (difference 15: the marker is protected by the guard).
- The existing suite `tests/acceptance/W2-50/` in full (README, support module, conftest, tests). Reuse its fixtures: the temporary `HOME`, the fixture project, the launch that opens the own folder, the stand-in CLI for `gov launch`, the guard's PreToolUse hook driven with the call on stdin.
- The decisions, in `docs/DECISION_REGISTER.md`: DEC-728, DEC-723, DEC-743 (staged; its text is the CIT-P's closing section), DEC-136, DEC-221, DEC-462, DEC-491, DEC-732. You read no private part of an implementation to learn what a test should expect.

## DEC-758 item 1 (owner, 2026-10-17): one more short round, tests first

- **F1:** every copy or install into a folder (`cp X d/`, `cp X d`, `install X d/`, `cp -r s/. d/`, with or without a trailing slash, with `-t`/`--target-directory` as now) is judged as **each file it writes, `<folder>/<name>`, under the same link and hard-link rule as a direct write**, and refused with the guard's reason. This closes the older hole for every ticket (row W2-H056), and with it the case where the destination is the own folder's marker (row W2-L349).
- **F2:** a project whose real root is inside `~/gov-os-runs` gets **no own folder**.
- A FIFO in the marker's place is another row (W2-L350), not this round's: write no test for it.
- A change to an earlier test is a rewrite with `Rewrite-Reason:` naming DEC-758 (DEC-491).

## The behaviours to test (from the review, as described behaviour)

1. **A copy or install into a folder is judged as each file it writes.** Today the guard judges such a call by the folder alone, so a file lands through an entry that already sits in that folder: the review reproduced it changing the project's acceptance test, overwriting another ticket's file, and (through a local clone's hard-linked objects) corrupting the source repository's object store. The same write named file by file is already refused. From now on the call is refused, with the guard's reason, whenever any file it would write, `<folder>/<name of that source>`, is refused as a direct write. Representative forms, a few each, no combinatorial expansion (DEC-221):
   - **In the own folder** (opened by the suite's launch), a folder `d` holding, at the name of the source:
     - a symbolic link to the project's acceptance test;
     - a symbolic link to a file in another ticket's folder under the root;
     - a hard link to a file outside the own folder (for example in the project);
     - with `cp X d/`, `cp X d` (no slash), `install X d/`, `cp -r s/. d/` (the entry under `s` named like the link), `cp a b d/` (several sources, only the second one landing on a link), and `cp -t d X` / `--target-directory=d X` as today's control (refused now; must stay refused).
   - **A link to a folder:** `cp -r s d/` where `d/s` is a symbolic link to a folder outside the own folder (another ticket's folder, or the project's acceptance-test folder): refused.
   - **Inside the repository, for every ticket** (W2-H056, the older hole): a folder the session may write, holding a symbolic link at the source's name to the project's acceptance test; `cp X <that folder>/`: refused with the guard's reason, as the direct write to the link is. One or two forms suffice.
   - **The own folder's marker** (W2-L349): a copy or install into the own folder of a file named like the marker (you learn the name only from a launch's result, never from code: list what the launch left in the own folder, as an existing case may already do; if there is no public way to know the name without reading code, write the case with the name taken from that listing and say so in the README) is refused, as the direct write onto the marker is. If you can add a `mv` of such a file into the own folder as a form and it is refused today, add it; if it is allowed today, add it as a red case, since the guard already refuses `mv` onto the marker named directly (difference 15).
   - **Controls (must pass now and after):** an ordinary `cp X d/`, `cp X d`, `install X d/`, `cp -r s/. d/` and `cp a b d/` into a folder of the own folder that holds no such entry are allowed; the same into an allowed folder inside the repository are allowed; a copy over an ordinary existing file of the same name in the own folder is allowed.
   - Test through the guard's hook with the call on stdin, as the suite does. Where a case shows the loss (an acceptance test changed), it is enough that the guard refuses the call; the test runs no allowed command for real against anything outside its temporary folder.
2. **A project whose real root lies inside `~/gov-os-runs` gets no own folder.** Today a project made inside the own folder (a `.git` file naming this repository's common directory, a forged `in_progress` ticket whose `external-ref` names another ticket's folder, and the guard's hook) gets that other ticket's folder from the guard (Write, `rm -rf`) and from `gov launch` (its sandbox write list). From now on, a project whose real root (links resolved) is under the root gets no folder under the root at all:
   - the guard refuses its Write, Edit and judged Bash (`rm -rf`, a redirect) in any folder under the root outside the project itself, with its reason, whatever ticket its session names, the folder of its own ticket's name included, marked or not;
   - `gov launch` from it adds no folder under the root to its sandbox write list, makes no folder there and writes no record (its temp folder stays).
   - Representative forms: (a) a project with a `.git` file naming the first project's common directory, made inside the first project's own folder; (b) a `git worktree add` of the temporary fixture repository into its own folder, with forged tickets; (c) a `git clone` of the fixture repository into its own folder, with a ticket of another folder's name; (d) a project outside the root reached by a path that is a symbolic link into the root, if the suite can build it simply.
   - **Controls:** the first project, outside the root, keeps its own folder (allowed writes there, its launch keeps the folder in the write list); writes the project under the root makes inside its own tree are judged as before (if an existing case already holds this, name it; add no reading no source supports).

Test each through the public interfaces the suite already drives (the guard's PreToolUse hook with the call on stdin; `gov launch` with the stand-in CLI). FULL, thorough, but no combinatorial expansion (DEC-221): a few representative forms per behaviour, the success control with each refusal.

## What you write

- Only inside `tests/acceptance/W2-50/`: the new cases in a new file; named rewrites of earlier files only if a new behaviour conflicts with an earlier case. No earlier ticket's test is revised; if one conflicts with these behaviours, name it and return a package.
- Update the README: the new tests mapped to the behaviour they hold, each with its expected red reason, stated as "tests added after implementation, from the extra review (DEC-136, DEC-758)"; every rewritten case with its reason; the case count.
- Behaviour through public interfaces, never internals. Deterministic, no network. Child processes get `PYTHONPATH` as the suite already passes it.
- Red first: run the whole suite to the end, never with `-x`:
  `PATH=/home/usain/.nvm/versions/node/v22.23.3/bin:$PATH PYTHONPATH=/home/usain/gov-os-worktrees/W2-50/src python3 -m pytest tests/acceptance/W2-50 -q -p no:cacheprovider -rs`
  Each new test fails for the reason the README states, or passes today for a stated reason (a control, or a `-t` form already refused); every earlier case still passes.
- A behaviour you cannot turn into a test without a reading no source supports is a package (question, why now, options, impact, reversibility, cost, recommendation, confidence), with no test.

## Commit

Before committing, check that `/home/usain/Dynamic-Agentic-Engineering-OS/.git/hooks` holds no `pre-commit` file (only `*.sample` files); if one is there, stop and say so. Never `--no-verify`, never `core.hooksPath`. Commit only your test paths, in one commit, with the trailers in the final block:

    git commit -m "W2-50 (DAEO-kl5e): acceptance tests for the extra review's findings F1 and F2 (DEC-136, DEC-758)" --trailer "Task: DAEO-kl5e" --trailer "Role: independent-test-designer" --trailer "Implements: DEC-728" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"

If you changed an existing test file, its support module or conftest, add `--trailer "Rewrite-Reason: DEC-758: <what changed and why>"` (DEC-491). Then show `git log --oneline -2`, `git log -1 --format=%B` and `git status --short`.

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

In those fields give: your commit's hash and trailers; the `gov.__file__` line; the suite's counts; each behaviour with its tests; the red reason as you saw it; which new tests pass now and why; every rewrite of an existing file; the `~/gov-os-runs` ABSENT line. Refused twice for the same call: stop and say so.
