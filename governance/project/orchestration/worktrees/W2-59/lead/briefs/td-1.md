# Brief: independent test designer — W2-59 (DAEO-kh9l), run 1

You are a fresh independent test designer (MR-3). Ticket: `DAEO-kh9l` (`W2-59`, "The pinned judge: the declared checks and the hook lines run from the pin; the packaging gaps"), profile STANDARD. You work only in the worktree `/home/usain/gov-os-worktrees/W2-59` on branch `w2/W2-59`. You write the ticket's acceptance tests from its KPI lines and its sources, before the implementation, and you show them red.

## Step 0, before any work: the sandbox check (report it first in your return)

(a) `python3 -c "open('/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-kh9l','w').write('x')"` must FAIL.
(b) `echo sandbox-trial | git hash-object -w --stdin` and `git update-index --refresh` must WORK.
If (a) wrote the file or (b) failed, stop there and return, saying which.

Then run `printenv GOV_ROLE GOV_TICKET` (expect `independent-test-designer` and `DAEO-kh9l`) and `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-59` and `w2/W2-59`). If anything differs, stop and say so.

## Standing rules (read first)

- **DEC-732, the code under test:** in this worktree, **every test run and every `gov` command used for verification runs this worktree's own `src/`**: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-59/src` set **per command** (never in a session's `--settings` env). Show it with `PYTHONPATH=/home/usain/gov-os-worktrees/W2-59/src python3 -c "import gov; print(gov.__file__)"`; it must point into this worktree. Once the bootstrap pin is on PATH (DEC-822), a bare `gov` is the pinned judge; `PYTHONPATH` chooses only the code under test.
- **Memory first (DEC-836):** use `gov retrieve` for what you need to know before reading files at random: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-59/src python3 -m gov.cli.main retrieve "<question>" --json`. Say in your return which questions you asked it and whether the answers helped.
- **Reads are open, writes are closed (DEC-820, Policy 2).** You read freely: the repository, git history, other worktrees. Four things are refused: (a) secrets and keys, never printed; (b) the contents of the held-out qualification material (its file names may be seen); (c) **the counterpart's work on this ticket: you never read this ticket's implementation**, that is any file `git diff --name-only w2/integrate...HEAD` names other than your own tests (read the code as it stands on the base with `git show w2/integrate:<path>`); (d) the hidden half of any evaluation set, by whoever is measured by it. Never read or name the qualification oracle.
- **DEC-849, read refusals until W2-58 lands:** the guard still refuses some reads Policy 2 opened (searches that start at the repository root, `governance/project/` or `.claude/`). Take the refusal, never look for another form, and search named folders instead. **Count every read refusal you meet and give the count in your return.** Never read `.claude/settings.json` (the generated settings file), in this worktree or anywhere.
- **Refused twice for the same call: stop and say so; no third try** (AR-6). If the guard or the sandbox refuses something you need for the ticket, do not work around it: return it as a package.
- Run everything in the foreground, one command after another; give long commands the tool's longest timeout. Return only after your commit exists.
- No `git checkout` of another commit, no `git reset`, no `git clean`, no amend, no rebase, no push, no merge, no tag. Install nothing (a temporary virtual environment made by a test, under the test's own temporary folder, with `--no-index`, is not an install). Never `sudo`.
- **No copy of the repository:** no `cp -r`, `rsync`, `git archive`, `git worktree` or `git clone` of this repository or a folder of it. A throwaway stand-in imports the installed package or copies single named files, never `governance/project/`. A test that needs a repository builds a temporary one from scratch (`git init` in pytest's temporary folder, single named files copied in) or from the dev tiers.
- Nothing of a test goes under a `.gov-runtime/` folder (DEC-673), in `~/.local`, or in `~/gov-os-workbench`. Dev-tier tests use `GOV_DEV_TIERS` by name only, clone into a temporary folder, and are marked `local_only`; never list, glob, search or write in `~/gov-os-workbench` yourself (DEC-723).
- Inside a launched session `.gov-runtime/freeze` shows as a placeholder device file whether or not a flag exists: conclude nothing from it.
- The guard refuses here-documents and unresolvable variables in Bash write targets: write files with the Write and Edit tools, with literal absolute paths. No subagents that write. Never write `.gov-runtime/**` outside `.gov-runtime/scratch/`.
- Never ask the owner anything and never notify anyone (DEC-850): a question is a package in your return.
- You use your model's full window; nobody asks you to stop or compact early (DEC-838).
- Your temporary folder is removed when your session ends: everything the lead needs is in your final message.

## What you read

- The ticket file `.tickets/DAEO-kh9l.md` (read-only): its KPI lines, its `allowed_paths`, its sources.
- The decisions: in `docs/DECISION_REGISTER.md`, DEC-822 (the pinned release in two steps; item 3: the per-command `PYTHONPATH` chooses only the code under test, not the judge), DEC-835 (this ticket's scope and the two packaging gaps), DEC-831, DEC-732, DEC-579 (the kernel's two layouts), DEC-221 (proportional tests), DEC-462. DEC-854 is staged, not yet in the register: the ticket starts beside another unmerged ticket; nothing in it changes what you test.
- The plan's text of the ticket: `docs/plan/WAVE_2_REVISED_PLAN.md` section 4.1 (the WBS has no W2-59 card in this worktree).
- The public interfaces, as they stand on `w2/integrate`: `gov check --json` and the declared checks under `template/governance/kernel/checks/*.yaml` (their `command` lines); `gov doctor --json`; `gov --version`; the hook command lines in `.rulesync/hooks.jsonc` and the hook programs they start under `template/governance/kernel/hooks/`; `pyproject.toml`. W1-38's acceptance tests under `tests/acceptance/W1-38/` (you check them against the hook-line change, below).
- The owner's pin, as installed on 2026-10-19 (facts, read-only; never write there): `~/.local/bin/gov` is a link to `~/.local/share/gov-os/pin-fecb870c/bin/gov`; that environment is a `python3 -m venv --system-site-packages` with a non-editable install of a wheel built from a `git archive` export of commit `fecb870c` (so the installed package carries no git metadata), by `SOURCE_DATE_EPOCH=… python3 -m pip wheel --no-deps --no-build-isolation --no-index`. The system `python3` has no importable `gov`. **The pin's path names a version and moves with each re-pin (the pin ladder):** nothing may depend on `pin-fecb870c` by name. The owner's documented rollback replaces the link by an editable install's own `gov` script.

## The behaviour to test (STANDARD: every KPI line's success and failure, plus the key edge cases)

Two installs exist in every test that needs a judge: **a stand-in pin**, which your test makes by building a wheel of this worktree's code and installing it, non-editable, into a virtual environment in the test's temporary folder (this is how the "proven from an installed wheel" lines exercise this worktree's code, DEC-732); and **a project under check**, a temporary git repository whose files are data for the judge. Build the wheel once per session (a session-scoped fixture), and build it **without writing anything into this worktree**: a plain `pip wheel <worktree>` leaves `build/` and `src/*.egg-info` in the source tree, and a stale `build/` can leak old files into a later wheel. The lead checked one form that keeps the source tree clean: set `DIST_EXTRA_CONFIG` to a `.cfg` file in your temporary folder holding `[build]` `build_base=<tmp>/bb` and `[egg_info]` `egg_base=<tmp>/eb`, then `python3 -m pip wheel --no-deps --no-build-isolation --no-index -w <tmp>/dist /home/usain/gov-os-worktrees/W2-59`. Install with `<venv>/bin/python -m pip install --no-deps --no-index <wheel>` into `python3 -m venv --system-site-packages <tmp>/venv`. No network.

1. **The judge's checks (KPI success 1, DEC-822 item 3; failure: "a check edited in the tree does not change the verdict of the pinned judge").** When the stand-in pin's `gov check` judges a project, every declared check runs with the judge's own interpreter and its own installed package; the project supplies only data. Observable, for example: the project holds a `src/gov/...` in which a declared check's module is edited (to give the opposite verdict, or to leave a marker when imported): the pin's verdict for that check is the one the installed check gives, and no marker appears. Key edges: a declared command that starts with `python3` must not run whatever `python3` comes first on `PATH` (a decoy `python3` earlier on `PATH` is not used), and a declared command that starts with `gov` (one exists today) must not run whatever `gov` comes first on `PATH`. The judge's own command line carries no `PYTHONPATH` naming the project (DEC-822 item 3: that variable chooses the code under test). A declaration names the check; its code comes from the judge.
2. **The hook lines (KPI success 2, DEC-822 step 2).** Every hook command line in `.rulesync/hooks.jsonc` that starts a governance program starts it with the pin's interpreter and package: not with the project's `src` on the import path, not with whichever `python3` is first on `PATH`, and with no versioned pin path written in the line. Make your stand-in pin reachable the way the owner's pin is: a link at `<HOME>/.local/bin/gov` to the stand-in's `bin/gov`, and that `.local/bin` folder also first on `PATH`, with `HOME` set to a temporary folder in the subprocess's environment (so the test does not fix which of the two the line uses). Run each line through `sh -c`, with `CLAUDE_PROJECT_DIR` set to the temporary project, and show which install's governance code ran. Key edge (never fail open): **if the pin cannot be found, the preToolUse line must not let the call through** — Claude Code treats a hook's exit code 2 as blocking and any other non-zero exit as a non-blocking error that lets the call proceed; a deny decision on standard output also blocks. Judge proportionately what the other lines must do when the pin is missing.
   **W1-38's hook-source tests:** before you write, check every test under `tests/acceptance/W1-38/` that reads or runs the hook command lines (its README explains P-7 and DEC-608, the `PYTHONPATH` prefix) against this change, and name, in your return and your README, each W1-38 test the change would make red, with the reason and the revision it would need. **Do not edit W1-38's tests in this run:** a needed revision is returned as a package (DEC-822 step 2, MR-3).
3. **The repository from the project root (KPI success 3, DEC-835; failure: "a module that still reads the repository from its install path fails a test").** From the stand-in pin, run in a project: every behaviour that reads repository files (today known: the zero-result canary declarations that `gov doctor` reads, and the path map and gitleaks configuration that the retrieval-regression check reads) reads them from the project under check, never from a place found from the installed package's own location. Cover every such module by behaviour (DEC-835 item 2); you may find them by reading the code as it stands on `w2/integrate`. A decoy at the place the install path leads to (with content that would change the result) is one way to make a lookup from the install path visible. The kernel has two layouts (DEC-579): `template/governance/kernel/` in this repository, `governance/kernel/` in an adopted project. The retrieval-regression check needs the dev tiers: `GOV_DEV_TIERS` by name, clone into a temporary folder, `local_only`.
4. **The baseline as package data (KPI success 4; failure: "a wheel without the data file fails the build or its test").** The wheel built from this worktree contains `retrieve_baseline.yaml` in the retrieval package, and the installed retrieval-regression check reads its thresholds from the installed package, not from the project. A wheel without the file fails your test.
5. **`gov --version` (KPI success 5).** It prints the package's version (as `pyproject.toml` states it) and the commit of the code that runs, and exits 0, with no command and outside any project. From this worktree's code in a git repository, the commit is that repository's `HEAD`. Note for proportion: unlike lines 3 and 4, this KPI line does not say "proven from an installed wheel", and the pin's wheel is built from an export with no git metadata. Decide what the line requires of an installed wheel; whatever you require, never accept a wrong commit. If you read the line as requiring the commit from an installed wheel and you judge that it cannot be met inside the ticket's `allowed_paths`, return a package (with your recommendation and confidence), and still write the tests you can.

Each test runs this worktree's code: either through the stand-in pin built from this worktree, or with `PYTHONPATH=/home/usain/gov-os-worktrees/W2-59/src` set in the subprocess. Your README says how, and gives the `gov.__file__` line as you ran it.

## What you write

- Only under `tests/acceptance/W2-59/`. No throwaway implementation in the tree. No edit of any other ticket's tests (see W1-38 above).
- STANDARD proportion (DEC-221): every KPI line's success and failure, plus the key edge cases above; no combinatorial expansion. Behaviour through public interfaces, never internals; deterministic; no network. Keep the whole suite's run time modest (one wheel build per session).
- A `README.md` mapping each KPI line to its tests and its expected red reason, how the tests exercise this worktree's code, the W1-38 check, and the run command:
  `PATH=/home/usain/.nvm/versions/node/v22.23.3/bin:$PATH PYTHONPATH=/home/usain/gov-os-worktrees/W2-59/src python3 -m pytest tests/acceptance/W2-59 -q -p no:cacheprovider -rs`
- **Red first:** run the suite to its end (never `-x`); every test fails for the reason your README states, or is named as already green with why.
- An ambiguous KPI line or a dispute is never a guess: return it as a package (context; what happened; why it matters; options with consequence, cost and risk; recommendation and confidence; what it blocks).

## Commit

Commit only `tests/acceptance/W2-59/`, in one commit, with the trailers in the final block:

    git commit -m "W2-59 (DAEO-kh9l): acceptance tests, the pinned judge and the packaging gaps" --trailer "Task: DAEO-kh9l" --trailer "Role: independent-test-designer" --trailer "Implements: DEC-822, DEC-835" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>" -- tests/acceptance/W2-59

Check `git log --oneline -2` and `git status --short` after it.

## Return

Your last message, complete in itself. In `evidence`: the sandbox check's result (first), your commit hash, the `gov.__file__` line, the test count and the red run's counts. In `tests`: each KPI line with its tests and the red reason you saw. In `discoveries`: the W1-38 check (each test the change would make red, with reason and needed revision), anything that exists only in the installed wheel. Also give: the number of guard read refusals you met, and the `gov retrieve` questions you asked.

**The twelve fields come first, each as a labelled line** (label at the start of a line, a colon, at least one word; "none" where there is nothing), and any machine-readable payload after them. Refused twice for the same call: stop and say so.

```
task: <what you were asked to do, in one line>
status: <DONE | PACKAGES | ESCALATION | ESCALATION_BLOCKED | LAUNCH_BLOCKED | AUTH_REQUIRED, and one line of why>
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
