# Brief: independent test designer — DAEO-kl5e (W2-50), FULL: tests for one more short round (DEC-774, finding D)

You are a fresh independent test designer (MR-3). Ticket: DAEO-kl5e (W2-50, "The durable scratch root: ~/gov-os-runs/<own ticket>/ in the guard and the launcher's sandbox (CIT-P)"), profile FULL. You work only in the worktree `/home/usain/gov-os-worktrees/W2-50` on branch `w2/W2-50`, at head `2d60cdd3` or later. The ticket is implemented and its acceptance suite `tests/acceptance/W2-50/` (358 cases) passes. The review of the last round found one behaviour the suite misses (finding D below); the owner has decided it (DEC-774, 2026-10-18, staged for the owner's commit and not in this worktree's register: its text is given below). You add acceptance tests for it, as described behaviour (DEC-136), and show them red.

## Standing rules (read first)

- First run `printenv GOV_ROLE GOV_TICKET` (expect `independent-test-designer` and `DAEO-kl5e`) and `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-50` and `w2/W2-50`). If anything differs, stop and say so.
- **DEC-732, the code under test:** in this worktree, **every test run and every `gov` command used for verification runs this worktree's own `src/`**: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-50/src` set **per command** (never in a session's `--settings` env). Your verification shows it with `PYTHONPATH=/home/usain/gov-os-worktrees/W2-50/src python3 -c "import gov; print(gov.__file__)"`, quoted in your return; it must point into this worktree.
- **The guard's hook in your own session runs this worktree's `src/`** (DEC-751 item 6), not the main tree's. You change no code, so this only means: the rules that confine you are the ones under test. It refuses Bash calls whose write path it cannot resolve (`mktemp -d`, `$VAR` paths): use literal paths, or put experiments in a script file.
- Run everything in the foreground, one command after another: your session ends with your last message, and nothing started in the background is ever read. Return only after your commit exists.
- No `git checkout` of another commit, no `git reset`, no `git clean`, no amend, no rebase in this worktree.
- Run no glob, no search and no listing over `governance/project/`: name the files you need there one by one (DEC-508). Never read `.claude/settings.json` or `.claude/settings.local.json` of this worktree or of any real repository (a fixture project's settings file that your test writes is yours). Nothing under `~/.claude/` is read.
- Never read, print, search, diff or copy the held-out file under `governance/project/`, and never type its path (DEC-525). Never read or name the qualification oracle.
- **The workbench (DEC-723).** Never write in `~/gov-os-workbench`, and never list, glob or search it. Dev-tier tests use `GOV_DEV_TIERS` by name only and clone into a temporary folder.
- **The real scratch roots are never touched.** Neither your tests nor you create, write, list or remove anything in the real `~/gov-os-runs/` (it does not exist, and nobody creates it in this run), the real `~/gov-os-worktrees/` or the real `~/gov-os-workbench/`. Your tests use the suite's existing means: a temporary `HOME` for the process under test and a temp folder (`TMPDIR`) disjoint from it. Run no `local_only` live-launch case of another suite (W1-46, W1-50: they would make the real root). Before you return, run `test -e ~/gov-os-runs && echo PRESENT || echo ABSENT` and quote the output: it must print ABSENT.
- **Every symbolic link a case needs is made by the test's own fixture, in its temporary tree, never in the repository** (not in this worktree's `tests/acceptance/`, not anywhere under the worktree). A link "at a protected name" means a link in the fixture project's acceptance folder or in another ticket's folder under the fixture's temporary root.
- Never copy the repository or a folder of it (`cp -r`, `rsync`, `git archive`, `git worktree`, `git clone` of this repository or a folder of it) anywhere. A test that needs a repository builds a temporary one from scratch, as the suite already does. No clone, copy or file of a programme is ever put under a `.gov-runtime/` folder (DEC-673).
- Inside a launched session `.gov-runtime/freeze` shows as a placeholder device file whether or not a flag exists: conclude nothing from it.
- The guard refuses here-documents and unresolvable variables in Bash write targets: write files with the Write and Edit tools and literal absolute paths. No subagents that write. Install nothing. No push, merge, rebase or tag. Never write `.gov-runtime/**` outside `.gov-runtime/scratch/`. Never run `gov rebuild --no-embeddings`, `gov close`, `gov adopt` or `gov pause` against this worktree or the main tree. Do not run `docs/plan/tools/validate_s1.py` (DEC-738 item 2). Tests launch no real `claude` session and use no network. Never write under `src/gov/close/**` or `tests/unit/close/**`. Never touch `src/gov/guard/protected.py`.
- Refused twice for the same call: stop and say so; no third try (AR-6).
- If the guard or the sandbox refuses something you needed, do not work around it: return it as a package. On an authentication or access error (401, 403, "Failed to authenticate", "access grant"), stop and return status AUTH_REQUIRED.
- Your temporary folder is removed when your session ends (DEC-386): everything the lead needs is in your final message.

## What you read

- The ticket file `.tickets/DAEO-kl5e.md` (read-only); the approved proposal `docs/changes/W2-50-CIT-P.md` with the owner's answers (DEC-743); the record `docs/changes/W2-50-CIT-E.md`, its §10 in particular (the claims this round corrects).
- The existing suite `tests/acceptance/W2-50/` in full (README, support module, conftest, tests), `test_w2_50_short_round.py` and `test_w2_50_extra_review.py` in particular: reuse their fixtures (the temporary `HOME`, the fixture project, the launch that opens the own folder, another ticket's folder, the guard's PreToolUse hook driven with the call on stdin, the folders holding a link at `<folder>/<name>`).
- The tools' own documentation, a public source for how each form writes: `cp --help`, `install --help`, `mv --help` (GNU coreutils 9.4 on this machine). Find what each form does to a link by running the tool **inside your temporary folder only**.
- The decisions, in `docs/DECISION_REGISTER.md`: DEC-728, DEC-136, DEC-221, DEC-462, DEC-491, DEC-732. You read no private part of an implementation to learn what a test should expect.

## The owner's DEC-774 (2026-10-18)

- **Finding D:** `cp -b` (`--backup`), `install`, `mv` and `cp --remove-destination` onto a symbolic link replace the link with a new file at the link's own path, while the guard judges the link's target. So where such a link already sits at a protected name (an acceptance test, another ticket's file or folder), a session puts a file there.
- **One more short round, tests first.**
  - **The guard refuses as doubt a write that replaces a link rather than following it.** This covers the four forms above and any other form of `cp`, `install` or `mv` whose write replaces the link at its own path.
  - Ordinary writes through a link to an allowed target, and every copy, install and move run 6 allows into allowed folders, still pass.
- `ln -f`/`ln -sf` onto the own folder's marker is row W2-L354, a FIFO in the marker's place row W2-L350: write no test for either. `ln` is not this round's.
- A change to an earlier test is a rewrite with `Rewrite-Reason:` naming DEC-774 (DEC-491).

## The behaviours to test (from the review, as described behaviour)

The review saw, on coreutils 9.4: with the acceptance folder holding a link `test_link.py` that points to an allowed file of the project, and another ticket's folder holding a link `mylink` that points into the session's own folder, `cp -b X <link>`, `cp -S.t X <link>`, `cp --backup X <link>`, `cp --backup=simple X <link>` and `cp -b -t <other ticket's folder> mylink` were all allowed; the tool renamed the link to `<link><suffix>` and made a new regular file at the link's own path. `install X <link>`, `mv X <link>` and `cp --remove-destination X <link>` were allowed too and replace the link itself.

1. **D: a call whose write replaces a symbolic link at its own path is refused, as a form the guard cannot read ("doubt").** For each form, first find by running the tool in your temporary folder whether it replaces the link (the link's own path then holds a regular file, or the link is gone) or follows it (the link stays, its target changes), and name that in the README. Every form that replaces is refused; compare the refusal's reason with that of an existing refusal as doubt in the suite (for example `ln -t` or `cp --parents`), as far as the public result lets you, and say in the README what you compared. Representative forms, a few each, no combinatorial expansion (DEC-221), each with the link **at a protected name** (in the acceptance folder, and in another ticket's folder pointing into the own folder) and, for a few, **in an allowed folder** pointing to an allowed file (the rule is for the form, not the place):
   - `cp` with a backup: `-b`, `--backup`, `--backup=numbered`, `-S.t`, `--suffix=.bak`; joined and separate (`-bS .t`, `-b -S .t`); with `-f`; with `-t <folder> <name>` where `<folder>/<name>` is the link; with `-T`; with `--` before the operands;
   - `cp --remove-destination` (and an abbreviation the tool accepts, checked with the tool), alone and with `-t`;
   - `cp -f` (and `--force`) onto a link whose target the tool cannot open for writing (a dangling link; a link to a file without write permission), where the tool replaces the link: find by running it which cases replace; the guard cannot know this ahead, so `cp -f` onto a link is a form that may replace;
   - `install X <link>`, `install -m 644 X <link>`, `install -b X <link>`, `install -t <folder> X` where `<folder>/X` is the link, `install -T X <link>`;
   - `mv X <link>`, `mv -f X <link>`, `mv -b X <link>`, `mv -T X <link>`, `mv -t <folder> X` where `<folder>/X` is the link, `mv -- X <link>`;
   - **a link moved away:** `mv <link at a protected name> <own folder>/x` removes the link from its protected place; check whether the guard refuses it today, and if it does not, write a case (the call writes at the link's own path).
   - any other option of `cp`, `install` or `mv` in `--help` that replaces the destination rather than writing through it: if you find one, write a case; if you find none, say so in the README.
2. **Controls (must pass now and after):**
   - a plain `cp X <link>` (no backup, no `-f`, no `--remove-destination`), where `<link>` is in an allowed folder and points to an allowed, writable file: the tool writes through the link; allowed. The same with `cp -t <folder> X` where `<folder>/X` is such a link;
   - a link at a middle level or a link to a folder used as the destination folder, pointing to an allowed folder: `cp X <link to folder>/`, `install X <link to folder>/`, `install -m 644 X <link to folder>/`, `mv X <link to folder>/`: the tool writes through the link into the allowed folder; allowed. (If the tool turns out to replace the link in any of these, say so and treat it under D.)
   - every copy, install and move run 6's suite allows into allowed folders still passes: name the existing cases that hold this instead of duplicating them; backups (`-b`, `-S.bak`) onto ordinary files that are not links: allowed.
   - existing refusals stay refused (the suite already holds them; name them).
   - If an earlier case of this suite now conflicts with D (it asserts that a form which replaces a link is allowed), rewrite it only where DEC-774's text decides it, with `Rewrite-Reason: DEC-774: …`; otherwise return it as a package. No earlier ticket's test is revised; if one conflicts, name it and return a package.

Test each through the public interface the suite already drives (the guard's PreToolUse hook with the call on stdin). FULL, thorough, but no combinatorial expansion (DEC-221): a few representative forms per behaviour, the control with each refusal. A test that shows the loss only checks that the guard refuses the call; it runs no allowed command for real against anything outside its temporary folder.

## What you write

- Only inside `tests/acceptance/W2-50/`: the new cases in a new file; named rewrites of earlier files only as above.
- Update the README: the new tests mapped to the behaviour they hold (D, controls), each with its expected red reason, stated as "tests added after implementation, from the review of the last round (DEC-136, DEC-774)"; what each form does to a link as you saw it; every rewritten case with its reason; the case count.
- Behaviour through public interfaces, never internals. Deterministic, no network. Child processes get `PYTHONPATH` as the suite already passes it.
- Red first: run the whole suite to the end, never with `-x`:
  `PATH=/home/usain/.nvm/versions/node/v22.23.3/bin:$PATH PYTHONPATH=/home/usain/gov-os-worktrees/W2-50/src python3 -m pytest tests/acceptance/W2-50 -q -p no:cacheprovider -rs`
  Each new test fails for the reason the README states, or passes today for a stated reason (a control, or a form already refused); every earlier case still passes.
- A behaviour you cannot turn into a test without a reading no source supports is a package (question, why now, options, impact, reversibility, cost, recommendation, confidence), with no test.

## Commit

Before committing, check that `/home/usain/Dynamic-Agentic-Engineering-OS/.git/hooks` holds no `pre-commit` file (only `*.sample` files); if one is there, stop and say so. Never `--no-verify`, never `core.hooksPath`. Commit only your test paths, in one commit, with the trailers in the final block:

    git commit -m "W2-50 (DAEO-kl5e): acceptance tests for the review's finding D, a write that replaces a link (DEC-136, DEC-774)" --trailer "Task: DAEO-kl5e" --trailer "Role: independent-test-designer" --trailer "Implements: DEC-728" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"

If you changed an existing test file, its support module or conftest, add `--trailer "Rewrite-Reason: DEC-774: <what changed and why>"` (DEC-491). Then show `git log --oneline -2`, `git log -1 --format=%B` and `git status --short`.

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

In those fields give: your commit's hash and trailers; the `gov.__file__` line; the suite's counts; each behaviour with its tests; what each form does to a link; the red reason as you saw it; which new tests pass now and why; every rewrite of an existing file; the `~/gov-os-runs` ABSENT line. Refused twice for the same call: stop and say so.
