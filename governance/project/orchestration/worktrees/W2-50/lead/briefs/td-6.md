# Brief: independent test designer — DAEO-kl5e (W2-50), FULL: tests for one more short round (DEC-764, DEC-765)

You are a fresh independent test designer (MR-3). Ticket: DAEO-kl5e (W2-50, "The durable scratch root: ~/gov-os-runs/<own ticket>/ in the guard and the launcher's sandbox (CIT-P)"), profile FULL. You work only in the worktree `/home/usain/gov-os-worktrees/W2-50` on branch `w2/W2-50`, at head `8a310cb2` or later. The ticket is implemented and its acceptance suite `tests/acceptance/W2-50/` (305 cases) passes. The review of the last round found two behaviours the suite misses (A and B below); the owner has decided them (DEC-764 and DEC-765, 2026-10-18, staged for the owner's commit and not in this worktree's register: their text is given below). You add acceptance tests for them, as described behaviour (DEC-136), and show them red.

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
- Never copy the repository or a folder of it (`cp -r`, `rsync`, `git archive`, `git worktree`, `git clone` of this repository or a folder of it) anywhere. A test that needs a repository builds a temporary one from scratch, as the suite already does. No clone, copy or file of a programme is ever put under a `.gov-runtime/` folder (DEC-673).
- Inside a launched session `.gov-runtime/freeze` shows as a placeholder device file whether or not a flag exists: conclude nothing from it.
- The guard refuses here-documents and unresolvable variables in Bash write targets: write files with the Write and Edit tools and literal absolute paths. No subagents that write. Install nothing. No push, merge, rebase or tag. Never write `.gov-runtime/**` outside `.gov-runtime/scratch/`. Never run `gov rebuild --no-embeddings`, `gov close`, `gov adopt` or `gov pause` against this worktree or the main tree. Do not run `docs/plan/tools/validate_s1.py` (DEC-738 item 2). Tests launch no real `claude` session and use no network. Never write under `src/gov/close/**` or `tests/unit/close/**`.
- Refused twice for the same call: stop and say so; no third try (AR-6).
- If the guard or the sandbox refuses something you needed, do not work around it: return it as a package. On an authentication or access error (401, 403, "Failed to authenticate", "access grant"), stop and return status AUTH_REQUIRED.
- Your temporary folder is removed when your session ends (DEC-386): everything the lead needs is in your final message.

## What you read

- The ticket file `.tickets/DAEO-kl5e.md` (read-only); the approved proposal `docs/changes/W2-50-CIT-P.md` with the owner's answers (DEC-743) in its closing section; the record `docs/changes/W2-50-CIT-E.md`, its §9 in particular (the claims this round corrects).
- The existing suite `tests/acceptance/W2-50/` in full (README, support module, conftest, tests), `test_w2_50_extra_review.py` in particular: reuse its fixtures (the temporary `HOME`, the fixture project, the launch that opens the own folder, the guard's PreToolUse hook driven with the call on stdin, the folders holding a link or hard link at `<folder>/<name>`).
- The tools' own documentation, a public source for how each form writes: `cp --help`, `install --help`, `mv --help` (GNU coreutils 9.4 on this machine).
- The decisions, in `docs/DECISION_REGISTER.md`: DEC-728, DEC-136, DEC-221, DEC-462, DEC-491, DEC-732. You read no private part of an implementation to learn what a test should expect.

## The owner's DEC-764 and DEC-765 (2026-10-18)

- **DEC-764: one more short round, tests first.**
  - **A:** the guard refuses `cp --parents` (and every copy, install or move option that makes the landed path other than `<folder>/<name>`) **as doubt**, the way `ln -t` is refused today.
- **DEC-765: in the same round,** the guard reads option values as values and honours `--`: the short options that take a value (among them `-S`, `-o`, `-g`, `-m`, `-Z`, joined to the letter or separate, and their long forms) never read as `-t`; nothing after `--` is read as an option, and the destination is still judged. `cp -S.t`, `cp -bS.t`, `install -S.t`, `install -oroot`, `install -m+t` onto an acceptance test, and `cp -- -t F`, are judged as the files they write (B).
  - `ln -f`/`ln -sf` onto the own folder's marker is another row (W2-L354), and a FIFO in the marker's place is row W2-L350: write no test for either.
- A change to an earlier test is a rewrite with `Rewrite-Reason:` naming DEC-764 or DEC-765 (DEC-491).

## The behaviours to test (from the review, as described behaviour)

1. **A: a copy whose landed path is not `<folder>/<name>` is refused, as a form the guard cannot read.** Today `cp --parents <source> <folder>` writes `<folder>/<source path as written>`; with `..` in the source, or through a link at a middle level of that path, it reached the project's acceptance test (`cp --parents ../../tests/acceptance/<suite>/test_a.py -t <project>/src/app`) and another ticket's folder under the root (`cp --parents ../<other ticket>/work.txt ~/gov-os-runs/<own ticket>/`), and the guard allowed both. From now on every such call is refused, whatever its source, the way the guard refuses `ln -t` today (compare the refusal's reason with that of an `ln -t` call, as far as the public result lets you, and say in the README what you compared). Representative forms, a few each, no combinatorial expansion (DEC-221):
   - `cp --parents` into a folder of the repository the session may write and into the own folder: with `..` in the source; with a harmless source that would land inside the allowed folder (it is still refused: the refusal is for the form, not the result); with a trailing slash, without one, with `-t <folder>` and `--target-directory=<folder>`; combined with `-r`/`-a`.
   - Abbreviated spellings of the long option that the tool accepts (check with `cp --help` and by running the tool inside your temporary folder only), for example `--parent` and `--par`.
   - For `install` and `mv`: read `install --help` and `mv --help` for any option that makes the landed path other than `<folder>/<name>` or the named destination; if you find one, write a case for it; if you find none, say so in the README and write no case for it.
2. **B: an option's value is read as a value, and nothing after `--` is read as an option.** Today the guard reads a `t` inside an option's value as `-t`, so it judges the wrong path, and `cp -- -t F` judges nothing; `cp -S.t` and `cp -- -t` each overwrote an acceptance test when run for real. From now on each call is judged as the files it actually writes (for each form, find what the tool writes by running it inside your temporary folder, and name that in the README), and refused with the guard's reason when one of them is refused as a direct write:
   - `cp -S.t X <acceptance test>`, `cp -bS.t X <acceptance test>`, `cp -S .t X <acceptance test>` (separate value), `cp --suffix=.t X <acceptance test>`, `cp --suffix .t X <acceptance test>`;
   - a separate value that looks like `-t`: `cp -S -t F <acceptance test>` and `cp --suffix -t F <acceptance test>` (the suffix is `-t`; the destination is the last operand);
   - `install -S.t X <acceptance test>`, `install -oroot X <acceptance test>`, `install -o root X <acceptance test>`, `install -m+t X <acceptance test>`, `install --mode=+t X <acceptance test>`, `install -gstaff X <acceptance test>` (a group whose name has a `t`); and `mv -S.t X <acceptance test>`;
   - `--`: `cp -- -t <acceptance test>` (copies the file named `-t` onto the acceptance test); `cp -t <protected folder> -- X` and `cp -- X <protected folder>/` (`--` before the destination, after `-t`); `cp X -- <acceptance test>` (`--` after an operand); `mv -- -t <acceptance test>`; each judged as the file it writes, and refused.
   - **`-Z`:** on this machine `cp -Z`, `install -Z` and `mv -Z` take no value (check with `--help`). So `cp -Zt <protected folder> X` is a copy into `<protected folder>`: it must stay judged, and refused, whatever reading the guard makes of `-Z`. Write this case; it is a fail-closed control.
3. **Controls (must pass now and after, from the review's "nothing earlier now refuses that should pass"):**
   - ordinary `cp X d/`, `cp X d`, `install X d/`, `mv X d/` and `cp -r s/. d/` into an allowed folder of the own folder and into an allowed folder inside the repository, holding no link: allowed;
   - `cp -t <folder> X` and `install -m 644 X <folder>/` stay judged as before: allowed into an allowed folder, refused into a protected one;
   - `cp -S.bak X <allowed file>`, `install -m 0644 -o root X <allowed file>` and `cp -- X <allowed file>` (a value with no `t`, and a `--`, onto an allowed destination): allowed;
   - where an existing case already holds a control, name it in the README instead of writing a duplicate.

Test each through the public interface the suite already drives (the guard's PreToolUse hook with the call on stdin). FULL, thorough, but no combinatorial expansion (DEC-221): a few representative forms per behaviour, the success control with each refusal. A test that shows the loss (an acceptance test changed) only checks that the guard refuses the call; it runs no allowed command for real against anything outside its temporary folder.

## What you write

- Only inside `tests/acceptance/W2-50/`: the new cases in a new file; named rewrites of earlier files only if a new behaviour conflicts with an earlier case. No earlier ticket's test is revised; if one conflicts with these behaviours, name it and return a package.
- Update the README: the new tests mapped to the behaviour they hold (A, B, controls), each with its expected red reason, stated as "tests added after implementation, from the review of the last round (DEC-136, DEC-764, DEC-765)"; every rewritten case with its reason; the case count.
- Behaviour through public interfaces, never internals. Deterministic, no network. Child processes get `PYTHONPATH` as the suite already passes it.
- Red first: run the whole suite to the end, never with `-x`:
  `PATH=/home/usain/.nvm/versions/node/v22.23.3/bin:$PATH PYTHONPATH=/home/usain/gov-os-worktrees/W2-50/src python3 -m pytest tests/acceptance/W2-50 -q -p no:cacheprovider -rs`
  Each new test fails for the reason the README states, or passes today for a stated reason (a control, or a form already refused); every earlier case still passes.
- A behaviour you cannot turn into a test without a reading no source supports is a package (question, why now, options, impact, reversibility, cost, recommendation, confidence), with no test.

## Commit

Before committing, check that `/home/usain/Dynamic-Agentic-Engineering-OS/.git/hooks` holds no `pre-commit` file (only `*.sample` files); if one is there, stop and say so. Never `--no-verify`, never `core.hooksPath`. Commit only your test paths, in one commit, with the trailers in the final block:

    git commit -m "W2-50 (DAEO-kl5e): acceptance tests for the review's findings A and B (DEC-136, DEC-764, DEC-765)" --trailer "Task: DAEO-kl5e" --trailer "Role: independent-test-designer" --trailer "Implements: DEC-728" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"

If you changed an existing test file, its support module or conftest, add `--trailer "Rewrite-Reason: DEC-764/DEC-765: <what changed and why>"` (DEC-491). Then show `git log --oneline -2`, `git log -1 --format=%B` and `git status --short`.

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
