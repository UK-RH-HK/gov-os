# Brief: independent test designer — DAEO-kl5e (W2-50), FULL: tests for one option reader in the guard's read rule (DEC-778)

You are a fresh independent test designer (MR-3). Ticket: DAEO-kl5e (W2-50, "The durable scratch root: ~/gov-os-runs/<own ticket>/ in the guard and the launcher's sandbox (CIT-P)"), profile FULL. You work only in the worktree `/home/usain/gov-os-worktrees/W2-50` on branch `w2/W2-50`, at head `b4172c59` or later. The ticket is implemented. Its acceptance suite `tests/acceptance/W2-50/` holds 446 cases; 58 of them (finding D, `test_w2_50_link_replaced.py`) are red today and wait for an engineer. The owner has widened this round with one more behaviour (DEC-778, 2026-10-18, staged for the owner's commit and not in this worktree's register; its text is below). You add acceptance tests for it, as described behaviour (DEC-136), and show them red.

## Standing rules (read first)

- First run `printenv GOV_ROLE GOV_TICKET` (expect `independent-test-designer` and `DAEO-kl5e`) and `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-50` and `w2/W2-50`). If anything differs, stop and say so.
- **DEC-732, the code under test:** in this worktree, **every test run and every `gov` command used for verification runs this worktree's own `src/`**: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-50/src` set **per command** (never in a session's `--settings` env). Your verification shows it with `PYTHONPATH=/home/usain/gov-os-worktrees/W2-50/src python3 -c "import gov; print(gov.__file__)"`, quoted in your return; it must point into this worktree.
- **The guard's hook in your own session runs this worktree's `src/`** (DEC-751 item 6), not the main tree's. You change no code, so this only means: the rules that confine you are the ones under test. It refuses Bash calls whose write path it cannot resolve (`mktemp -d`, `$VAR` paths): use literal paths, or put experiments in a script file.
- Run everything in the foreground, one command after another: your session ends with your last message, and nothing started in the background is ever read. Return only after your commit exists. A foreground command is killed after 10 minutes: run the suite's files in a few separate commands if the whole folder takes longer (the last designer needed five runs).
- No `git checkout` of another commit, no `git reset`, no `git clean`, no amend, no rebase in this worktree.
- Run no glob, no search and no listing over `governance/project/`: name the files you need there one by one (DEC-508). Never read `.claude/settings.json` or `.claude/settings.local.json` of this worktree or of any real repository (a fixture project's settings file that your test writes is yours). Nothing under `~/.claude/` is read.
- **Never read, print, search, diff, copy, move or link the held-out file under `governance/project/`, and never type its path, in a test, a fixture, a command or a message (DEC-525, DEC-778).** Never read or name the qualification oracle. Never run `mv`, `cp` or `ln` on any real repository's settings file or held-out file: your experiments run only on files in your temporary folder.
- **The workbench (DEC-723).** Never write in `~/gov-os-workbench`, and never list, glob or search it. Dev-tier tests use `GOV_DEV_TIERS` by name only and clone into a temporary folder.
- **The real scratch roots are never touched.** Neither your tests nor you create, write, list or remove anything in the real `~/gov-os-runs/` (it does not exist, and nobody creates it in this run), the real `~/gov-os-worktrees/` or the real `~/gov-os-workbench/`. Your tests use the suite's existing means: a temporary `HOME` for the process under test and a temp folder (`TMPDIR`) disjoint from it. Run no `local_only` live-launch case of another suite (W1-46, W1-50: they would make the real root). Before you return, run `test -e ~/gov-os-runs && echo PRESENT || echo ABSENT` and quote the output: it must print ABSENT.
- Every link or hard link a case needs is made by the test's own fixture, in its temporary tree, never in the repository.
- Never copy the repository or a folder of it (`cp -r`, `rsync`, `git archive`, `git worktree`, `git clone` of this repository or a folder of it) anywhere. A test that needs a repository builds a temporary one from scratch, as the suite already does. No clone, copy or file of a programme is ever put under a `.gov-runtime/` folder (DEC-673).
- Inside a launched session `.gov-runtime/freeze` shows as a placeholder device file whether or not a flag exists: conclude nothing from it.
- The guard refuses here-documents and unresolvable variables in Bash write targets: write files with the Write and Edit tools and literal absolute paths. No subagents that write. Install nothing. No push, merge, rebase or tag. Never write `.gov-runtime/**` outside `.gov-runtime/scratch/`. Never run `gov rebuild --no-embeddings`, `gov close`, `gov adopt` or `gov pause` against this worktree or the main tree. Do not run `docs/plan/tools/validate_s1.py` (DEC-738 item 2). Tests launch no real `claude` session and use no network. Never write under `src/`, `src/gov/close/**` or `tests/unit/close/**`.
- Refused twice for the same call: stop and say so; no third try (AR-6).
- If the guard or the sandbox refuses something you needed, do not work around it: return it as a package. On an authentication or access error (401, 403, "Failed to authenticate", "access grant"), stop and return status AUTH_REQUIRED.
- Your temporary folder is removed when your session ends (DEC-386): everything the lead needs is in your final message.

## What you read

- The ticket file `.tickets/DAEO-kl5e.md` (read-only), its last note in particular (the widening for this round); the record `docs/changes/W2-50-CIT-E.md`, its §10.
- The existing suite `tests/acceptance/W2-50/` (README, support module, conftest), `test_w2_50_short_round.py` and `test_w2_50_link_replaced.py` in particular: reuse their fixtures (the temporary `HOME`, the fixture project with its own `.claude/settings.json` written by the test, the guard's PreToolUse hook driven with the call on stdin).
- How the guard's refusal to read the protected pair (the settings file and the held-out file, DEC-508, DEC-525, DEC-548, DEC-553) is already tested through the public hook: W1-02's suite under `tests/acceptance/W1-02/` (its tests on copies and second names). Read only what you need; never copy a line of it that names the held-out file.
- The tools' own documentation, a public source for how each option reads: `cp --help`, `mv --help` (GNU coreutils 9.4 on this machine). Check by running the tool **inside your temporary folder only**, on files you made there.
- The decisions, in `docs/DECISION_REGISTER.md`: DEC-136, DEC-221, DEC-462, DEC-491, DEC-508, DEC-525, DEC-548, DEC-553, DEC-728, DEC-732. You read no private part of an implementation to learn what a test should expect.

## The owner's DEC-778 (2026-10-18)

- The guard refuses every role a call that reads the protected pair (the project's settings file and its held-out file), and it counts as a read a command that gives such a file, or a folder that holds one, a second name: the sources of `mv`, and of `cp -l` (`--link`) (DEC-548, DEC-553).
- **Today the guard reads the options of `mv` and `cp -l` for this rule with an older reader than the one it uses for writes** (the one DEC-765 replaced for `cp` and `install`): a `t` inside an option's value can be read as `-t`, and `--` is not honoured. The owner's ruling: **the guard reads every copy-like command one way, for writes and for reads.** `mv` and `cp -l` with value-taking options whose value holds a `t` (joined and separate), and with `--` before and after the source and the destination, are judged as the reads they are.
- Ordinary `mv` and `cp -l` of unprotected files still pass.
- **Tests never name, type, read or copy the real held-out file or its path.** They use a temporary project with its own stand-in protected file, or another public means. The fixture project's own settings file (`.claude/settings.json`, written by the test in its temporary project) is protected by the same rule and is such a means. If you find no public means, return a package with no test.
- A change to an earlier test is a rewrite with `Rewrite-Reason:` naming DEC-778 (DEC-491).

## The behaviours to test (described behaviour)

1. **A second name for a protected file is refused as a read, however the options are written.** In a fixture project with its own settings file, a call that gives that file (or the folder that holds it) a second name with `mv` or `cp -l`/`--link` is refused with the guard's read refusal (compare its reason with that of the plain form, `mv <settings file> <new name>`, which the guard refuses today; say in the README what you compared). Find first, through the hook, which forms the guard allows today, and for which role: a role whose write rules would let it write the file's new name and remove the old one is the one that shows the read rule alone; if every role is refused anyway by another rule, assert the read refusal's reason, and say so in the README. Representative forms, a few each, no combinatorial expansion (DEC-221):
   - every value-taking option of `mv` and `cp` that the tool's `--help` lists (short and long: for example `-S`/`--suffix`, `--backup=`, and for `cp` `--sparse=`, `--reflink=`, `--preserve=`, `--no-preserve=`), each with a value that holds a `t` (`.t`, `t`, `auto`, `timestamps`, as the tool accepts), joined to the letter, after `=`, and as the next word; in clusters (`-lS.t`, `-bS .t`);
   - `--` before the source, between the source and the destination, and after both (where the tool accepts it), with and without `-t`;
   - `-t <folder> <protected file>`, `--target-directory`, and `-T`;
   - the folder that holds the protected file as the source, with such options.
   Check each form with the tool in your temporary folder: it is a second name if, after it runs, the file's content is reachable at the new name.
2. **Controls (must pass now and after):**
   - ordinary `mv` and `cp -l` of unprotected files of the fixture project, with the same options (values holding a `t`, `--`, `-t`, `-T`), stay allowed where the role's write rules allow the destination;
   - the plain second names the guard refuses today stay refused (name the existing cases that hold this, in W1-02's suite or this one, instead of duplicating them);
   - a plain `cp` (no `-l`) of an unprotected file with such options is not refused as a read.
3. **Not this round's:** `ln` (rows W2-L354, W2-L350), the write rules of `cp`, `install` and `mv` (finding D's tests already hold them): write no new case for them.
4. If an earlier case of this suite or of another ticket's suite now conflicts with DEC-778, name it; rewrite it only in this suite and only where DEC-778's text decides it, with `Rewrite-Reason: DEC-778: …`; otherwise return a package. No earlier ticket's test is revised.

Test each through the public interface the suite already drives (the guard's PreToolUse hook with the call on stdin). FULL, thorough, but no combinatorial expansion (DEC-221). A test only checks the guard's answer; it runs no allowed command for real against anything outside its temporary folder.

## What you write

- Only inside `tests/acceptance/W2-50/`: the new cases in a new file; named rewrites of earlier files only as above.
- Update the README: the new tests mapped to the behaviour they hold, each with its expected red reason, stated as "tests added after implementation, for the owner's widening of the round (DEC-136, DEC-778)"; the stand-in you used for the protected file and why it is public; what each form does as you saw it with the tool; which role each case runs as and why; every rewritten case with its reason; the case count.
- Behaviour through public interfaces, never internals. Deterministic, no network. Child processes get `PYTHONPATH` as the suite already passes it.
- Red first: run the whole suite to the end, never with `-x`:
  `PATH=/home/usain/.nvm/versions/node/v22.23.3/bin:$PATH PYTHONPATH=/home/usain/gov-os-worktrees/W2-50/src python3 -m pytest tests/acceptance/W2-50 -q -p no:cacheprovider -rs`
  (in a few runs of separate files if it outlives one call). Each new test fails for the reason the README states, or passes today for a stated reason (a control, or a form already refused); every earlier case gives what it gave before (the 58 D cases of `test_w2_50_link_replaced.py` are red today, the rest green).
- A behaviour you cannot turn into a test without a reading no source supports is a package (question, why now, options, impact, reversibility, cost, recommendation, confidence), with no test.

## Commit

Before committing, check that `/home/usain/Dynamic-Agentic-Engineering-OS/.git/hooks` holds no `pre-commit` file (only `*.sample` files); if one is there, stop and say so. Never `--no-verify`, never `core.hooksPath`. Commit only your test paths, in one commit, with the trailers in the final block:

    git commit -m "W2-50 (DAEO-kl5e): acceptance tests for one option reader in the guard's read rule (DEC-136, DEC-778)" --trailer "Task: DAEO-kl5e" --trailer "Role: independent-test-designer" --trailer "Implements: DEC-728" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"

If you changed an existing test file, its support module or conftest, add `--trailer "Rewrite-Reason: DEC-778: <what changed and why>"` (DEC-491). Then show `git log --oneline -2`, `git log -1 --format=%B` and `git status --short`.

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

In those fields give: your commit's hash and trailers; the `gov.__file__` line; the suite's counts; each behaviour with its tests; the stand-in for the protected file; what each form does with the tool; the red reason as you saw it; which new tests pass now and why; every rewrite of an existing file; the `~/gov-os-runs` ABSENT line. Refused twice for the same call: stop and say so.
