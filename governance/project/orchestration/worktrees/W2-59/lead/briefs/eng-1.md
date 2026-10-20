# Brief: engineer — W2-59 (DAEO-kh9l), run 1

You are a fresh engineer. Ticket: `DAEO-kh9l` (`W2-59`, "The pinned judge: the declared checks and the hook lines run from the pin; the packaging gaps"), profile STANDARD. You work only in the worktree `/home/usain/gov-os-worktrees/W2-59` on branch `w2/W2-59`. You implement the ticket until its acceptance tests pass, and you write its CIT-P.

## Step 0, before any work: the sandbox check (report it first in your return)

(a) `python3 -c "open('/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-kh9l','w').write('x')"` must FAIL.
(b) `echo sandbox-trial | git hash-object -w --stdin` and `git update-index --refresh` must WORK.
If (a) wrote the file or (b) failed, stop there and return, saying which.

Then run `printenv GOV_ROLE GOV_TICKET` (expect `engineer` and `DAEO-kh9l`) and `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-59` and `w2/W2-59`). If anything differs, stop and say so.

## Standing rules (read first)

- **DEC-732, the code under test:** in this worktree, **every test run and every `gov` command used for verification runs this worktree's own `src/`**: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-59/src` set **per command** (never in a session's `--settings` env). Show it with `PYTHONPATH=/home/usain/gov-os-worktrees/W2-59/src python3 -c "import gov; print(gov.__file__)"`; it must point into this worktree. Once the bootstrap pin is on PATH (DEC-822), a bare `gov` is the pinned judge; `PYTHONPATH` chooses only the code under test.
- **Memory first (DEC-836):** use `gov retrieve` for what you need to know before reading files at random: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-59/src python3 -m gov.cli.main retrieve "<question>" --json`. Say in your return which questions you asked it and whether the answers helped.
- **Reads are open, writes are closed (DEC-820, Policy 2).** You read freely: the repository, git history, other worktrees. Four things are refused: (a) secrets and keys, never printed; (b) the contents of the held-out qualification material (its file names may be seen); (c) **the counterpart's work on this ticket: you never read `tests/acceptance/W2-59/`** — no file there, by any tool (its README included); you may run those tests and read their names, results and failure messages; (d) the hidden half of any evaluation set, by whoever is measured by it. Never read or name the qualification oracle.
- **DEC-849, read refusals until W2-58 lands:** the guard still refuses some reads Policy 2 opened (searches that start at the repository root, `governance/project/` or `.claude/`). Take the refusal, never look for another form, and search named folders instead. **Count every read refusal you meet and give the count in your return.** Never read `.claude/settings.json` (the generated settings file), in this worktree or anywhere.
- **Refused twice for the same call: stop and say so; no third try** (AR-6). If the guard or the sandbox refuses something you need for the ticket, do not work around it: return it as a package.
- Run everything in the foreground, one command after another; give long commands the tool's longest timeout. **Commit your work before you run any long suite.** Return only after your commit exists.
- No `git checkout` of another commit, no `git reset`, no `git clean`, no amend, no rebase, no push, no merge, no tag. Install nothing; never `sudo`.
- **No copy of the repository:** no `cp -r`, `rsync`, `git archive`, `git worktree` or `git clone` of this repository or a folder of it. A throwaway stand-in imports the installed package or copies single named files, never `governance/project/`. A test that needs a repository builds a temporary one.
- Nothing goes under a `.gov-runtime/` folder (DEC-673), in `~/.local` (never touch the owner's pin under `~/.local/share/gov-os/` or the link `~/.local/bin/gov`), or in `~/gov-os-workbench`. Dev-tier tests use `GOV_DEV_TIERS` by name only and clone into a temporary folder.
- Inside a launched session `.gov-runtime/freeze` shows as a placeholder device file whether or not a flag exists: conclude nothing from it.
- The guard refuses here-documents and unresolvable variables in Bash write targets: write files with the Write and Edit tools, with literal absolute paths. No subagents that write. Never write `.gov-runtime/**` outside `.gov-runtime/scratch/`. Never touch `tests/acceptance/**`.
- Never ask the owner anything and never notify anyone (DEC-850): a question is a package in your return.
- You use your model's full window; nobody asks you to stop or compact early (DEC-838).
- Your temporary folder is removed when your session ends: everything the lead needs is in your final message.

## What you read

- The ticket file `.tickets/DAEO-kh9l.md` (read-only): its KPI lines and its `allowed_paths`.
- The decisions in `docs/DECISION_REGISTER.md`: DEC-822 (item 3: the per-command `PYTHONPATH` chooses only the code under test, not the judge; step 2: the hook lines), DEC-835 (this scope and the two packaging gaps), DEC-831, DEC-732, DEC-579 (the kernel's two layouts), DEC-135 (proportion), CAP-33 (a judge change goes through CIT-P). The plan's text of the ticket: `docs/plan/WAVE_2_REVISED_PLAN.md` section 4.1.
- The code the ticket touches, and anything else you need.

## What the ticket must do (behaviour)

1. When a judge runs `gov check`, every declared check runs with that judge's own interpreter and its own installed package; the project under check supplies only data. A declared command that starts with `python3` or with `gov` must not run whatever comes first on `PATH`, and a check module edited in the project's `src/` must not change the verdict of an installed judge. The judge's own command line carries no `PYTHONPATH` naming the project (DEC-822 item 3).
2. The hook command lines in `.rulesync/hooks.jsonc` that start a governance program start it with the pin's interpreter and package, not with the project's `src` on the import path. **The pin's path names a version and moves with each re-pin:** no versioned path may be written in the lines. The owner's pin keeps a stable link, `~/.local/bin/gov` → `<pin env>/bin/gov` (the pin environment is a `--system-site-packages` venv; its `bin/gov` console script's first line names its interpreter); the owner's documented rollback replaces that link with an editable install's own `gov` script. **Never fail open:** if the pin cannot be found, the preToolUse line must block the call (Claude Code treats a hook's exit code 2 as blocking and any other non-zero exit as a non-blocking error that lets the call proceed). `gov launch` recognises the guard by the text `hooks/pretooluse.py` in the preToolUse command: keep it. Change only the lines' interpreter part (the ticket's path rule). **If you find that a stable name for the pin's interpreter is needed that does not exist yet (for example a link the owner's pin script would maintain), do not invent one: return a package naming the exact owner command, and finish everything else.** The generated settings file is the owner's to regenerate: never read or write it. A hook line runs in the session's own environment: on this machine `~/.local/bin` is on `PATH` today, but nothing guarantees it in every session; choose a form that finds the pin through the stable link or through `PATH`, and that blocks when neither gives it. The acceptance tests make the stand-in pin reachable both ways, the link at `$HOME/.local/bin/gov` and that folder on `PATH`. Changing `.rulesync/hooks.jsonc` is expected to leave the adapter-portability check RED until the owner regenerates the settings (DEC-835 item 3): report it, do not touch the generated files, and name the owner act in the CIT-P.
3. Every module that finds the repository from its own install path finds it from the project under check instead (today known: the canary declarations, and the path map and gitleaks configuration of the retrieval-regression check; DEC-835 asks for every such module). The kernel has two layouts (DEC-579): `template/governance/kernel/` here, `governance/kernel/` in an adopted project.
4. `retrieve_baseline.yaml` ships as package data in the wheel.
5. `gov --version` prints the version and the commit, and exits 0, with no command and outside any project. Run from a source tree, the commit is the `HEAD` of the repository that holds the code (never the commit of whatever repository the working folder is in). An installed wheel built from a `git archive` export has no git metadata: it names its version and never a wrong commit (saying plainly that the commit is unknown is acceptable for now; whether a build should record it is an open package for the owner, not your work).
6. Two hook programs outside your paths (`template/governance/kernel/hooks/precompact.py` and `sessionstart.py`) put the project's `src` on their own import path when that folder exists. That is known and with the owner as a package; leave them as they are.

Proven from an installed wheel: build one **without writing into this worktree** (a plain `pip wheel` leaves `build/` and `src/*.egg-info` in the source tree, and a stale `build/` leaks old files into later wheels). One clean form: set `DIST_EXTRA_CONFIG` to a `.cfg` file in a temporary folder holding `[build]` `build_base=<tmp>/bb` and `[egg_info]` `egg_base=<tmp>/eb`, then `python3 -m pip wheel --no-deps --no-build-isolation --no-index -w <tmp>/dist /home/usain/gov-os-worktrees/W2-59`; install it with `<venv>/bin/python -m pip install --no-deps --no-index <wheel>` into `python3 -m venv --system-site-packages <tmp>/venv`.

## The overlap with W2-05 (DEC-854: you start beside it)

Another ticket's branch, unmerged, changes the same two files. In the check runner, it changes the line that builds the environment of a declared check's command (today a copy of the process's environment) into a call to a git-environment helper that exists only on its branch, removes the runner's now-unused import of the standard `os` module, and passes that helper's environment to the runner's three git calls. In the retrieval-regression check's main function, it adds an import of the same helper and a block that clears the process's environment and fills it from the helper before any work. That ticket's resume takes the merge conflict, keeping both sides (DEC-750, DEC-754). So: **keep your edits of those lines small and composable** (do not restructure the environment-building line or the start of that main function more than this ticket needs); **never import the git-environment helper module (`gov.util.gitenv`)**, which does not exist on this branch; and your CIT-P names the overlap.

## What you write

- Only inside the ticket's `allowed_paths`: `src/gov/check/runner.py`, `src/gov/retrieval/canary.py`, `src/gov/retrieval/retrieve_check.py`, `src/gov/cli/main.py` (the version only), `pyproject.toml` (package data only), `.rulesync/hooks.jsonc` (the hook lines' interpreter only), `tests/unit/check/**`, `tests/unit/cli/**`, `tests/unit/retrieval/**` (the canary and baseline cases only), `docs/changes/W2-59-CIT-P.md`. A file outside them that you need is a package.
- Never the acceptance tests (MR-3). A test you think is wrong is returned as a package, never edited and never worked around.
- Builder tests in the unit-test paths above, as regression evidence only.
- Proportion (DEC-135): no code for edge cases beyond the KPI lines. Never make a guard or gate decision fail open: each failure KPI must still refuse.
- **`docs/changes/W2-59-CIT-P.md`:** the change proposal under CAP-33 (follow the form of an existing `docs/changes/*-CIT-P.md`): the evidence (the pin's dry run: `secrets-indexing` ran from the working tree's `src`), what changes in the judge and the hook lines and why, what stays (DEC-822 item 3), the pin ladder's consequence (a check new in the tree runs only after a re-pin that holds it; a ticket that changes a format the judge reads needs a release that accepts it first, DEC-822 item 5), the overlap with W2-05 (DEC-854), any owner act needed (the owner regenerates the settings file and re-pins after the merge, DEC-835 item 4), risks and rollback.
- Run the ticket's acceptance tests, to the end, never `-x`, until they pass:
  `PATH=/home/usain/.nvm/versions/node/v22.23.3/bin:$PATH PYTHONPATH=/home/usain/gov-os-worktrees/W2-59/src python3 -m pytest tests/acceptance/W2-59 -q -p no:cacheprovider -rs`
  then W1-38's suite (the hook-line change touches it; report every red by name):
  `PATH=/home/usain/.nvm/versions/node/v22.23.3/bin:$PATH PYTHONPATH=/home/usain/gov-os-worktrees/W2-59/src python3 -m pytest tests/acceptance/W1-38 -q -p no:cacheprovider -rs`
  then the builder tests: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-59/src python3 -m pytest tests/unit -q -p no:cacheprovider`
  Inside your sandbox the code graph's folder `/tmp/gov-cbm-<uid>` is read-only (until W2-56): a builder test that fails only on it is reported by name as sandbox-caused, and the lead re-runs it outside. Known reds you did not cause: W1-42's two accepted reds; `secrets-indexing` RED in `gov check` (a time-out on the store, another ticket's fix). Do not run `gov rebuild` (the lead does), and run no full acceptance regression (the lead does).

## Commit

Commit only your paths, with the trailers in the final block, after checking that `/home/usain/Dynamic-Agentic-Engineering-OS/.git/hooks` holds no `pre-commit` file (if one is there, stop and return; never `--no-verify`, never `core.hooksPath`):

    git commit -m "W2-59 (DAEO-kh9l): <subject>" --trailer "Task: DAEO-kh9l" --trailer "Role: engineer" --trailer "Implements: DEC-822, DEC-835" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>" -- <your paths>

Check `git log --oneline -2` and `git status --short` after each commit.

## Return

Your last message, complete in itself. In `evidence`: the sandbox check's result (first), your commit hashes, the `gov.__file__` line, the lines added and removed (`git diff --stat w2/integrate...HEAD -- src pyproject.toml .rulesync tests/unit docs/changes`). In `tests`: each suite you ran with its counts and every red by name. Also give: the number of guard read refusals you met, and the `gov retrieve` questions you asked.

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
