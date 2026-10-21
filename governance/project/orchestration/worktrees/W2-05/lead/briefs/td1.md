You are a fresh independent test designer (MR-3). Ticket: DAEO-0z8c (W2-05, "The git environment of every check, hook and helper; the settings re-sort"), profile FULL. You work only in the worktree `/home/usain/gov-os-worktrees/W2-05` on branch `w2/W2-05`. You write the ticket's acceptance tests from its KPI lines and its sources, before the implementation, and you show them red.

## Standing rules (read first)

- First run `printenv GOV_ROLE GOV_TICKET` (expect `independent-test-designer` and `DAEO-0z8c`) and `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-05` and `w2/W2-05`). If anything differs, stop and say so.
- **DEC-732, the code under test:** in this worktree, **every test run and every `gov` command used for verification runs this worktree's own `src/`**: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-05/src` set **per command** (never in a session's `--settings` env). Your verification shows it with `PYTHONPATH=/home/usain/gov-os-worktrees/W2-05/src python3 -c "import gov; print(gov.__file__)"`, quoted in your return; it must point into this worktree. Your tests, run from this worktree, must exercise this worktree's code: every process they start that imports `gov` or runs `gov` gets this worktree's `src/` first on its `PYTHONPATH` (derived from the test file's own location, not a hard-coded main-tree path), and your README says how.
- Run everything in the foreground, one command after another: your session ends with your last message, and nothing started in the background is ever read. Return only after your commit exists. A foreground command is killed after 10 minutes: keep each run within that.
- No `git checkout` of another commit, no `git reset`, no `git clean`, no amend, no rebase in this worktree.
- Run no glob, no search and no listing over `governance/project/`: name the files you need there one by one (DEC-508). Never read `.claude/settings.json` or `.claude/settings.local.json`, in this worktree or anywhere. Nobody reads anything under `~/.claude/`.
- Never read, print, search, diff or copy the held-out file under `governance/project/`, and never type its path (DEC-525). Never read or name the qualification oracle.
- **The workbench (DEC-723).** Never write in `~/gov-os-workbench`, and never list, glob or search it. Dev-tier tests use `GOV_DEV_TIERS` by name only and clone into a temporary folder.
- Never copy the repository or a folder of it (no `cp -r`, `rsync`, `git archive`, `git worktree` or `git clone` of this repository or a folder of it) anywhere. A throwaway stand-in imports the package or copies single named files, never `governance/project/`; a test that needs a repository builds a temporary one from scratch. No clone, copy or file of a programme is ever put under a `.gov-runtime/` folder (DEC-673).
- **The git hooks stay uninstalled until W2-08.** Nobody runs `lefthook install` or `lefthook uninstall` in this repository or any of its worktrees: they share `.git/hooks` with the main tree. Every hook test runs in a temporary repository built from scratch (under pytest's `tmp_path`), with a temporary linked worktree of that temporary repository and its own stand-in `.claude/settings.json` written by the test. No test reads the real `.claude/settings.json`. A test that runs `lefthook` passes the temporary repository explicitly (its working directory and a cleared `GIT_*` environment) so that it can never act on this repository.
- Inside a launched session `.gov-runtime/freeze` shows as a placeholder device file whether or not a flag exists: conclude nothing from it.
- The guard refuses here-documents and unresolvable variables in Bash write targets: write files with the Write and Edit tools and literal absolute paths. No subagents that write. Install nothing: a tool you need is returned as a package. No push, merge, rebase or tag. Never write `.gov-runtime/**` outside `.gov-runtime/scratch/`.
- Your temporary folder is removed when your session ends (DEC-386): everything the lead needs is in your final message.
- If the guard or the sandbox refuses something you needed for the ticket, do not work around it: return it as a package. **Refused twice for the same call: stop and say so; no third try** (AR-6).

## What you read

- The ticket file `.tickets/DAEO-0z8c.md` (read-only): its KPI lines, its `allowed_paths`, its `list_rows` and its sources.
- The card of W2-05 in `docs/plan/WAVE_2_WBS.md` §2, and its §0 rules.
- AR-2 in `docs/plan/WAVE_2_LIST.md` ("### AR-2: the hook's git environment"), and the list rows W2-L109, W2-L160, W2-M012, W2-M105, W2-M113, W2-M161, W2-M231, W2-M281 in `docs/plan/WAVE_2_LIST.md` and `docs/plan/WAVE_2_TRIAGE.md`.
- The decisions in `docs/DECISION_REGISTER.md`: DEC-710, DEC-711, DEC-712 (the case and AR-2's origin), DEC-719, DEC-221, DEC-462, DEC-136, DEC-723, DEC-732, DEC-737.
- The public interfaces the ticket must work with: the `gov` command line (`python3 -m gov.cli.main --help` and its subcommands, `gov check`, `gov ci checks`, `gov ci staged-secrets`), the hooks file `lefthook.yml`, the installed `lefthook` binary (`~/.local/bin/lefthook`, as a tool on the path), the adapter-portability check as `gov check` reports it, and earlier acceptance suites under `tests/acceptance/` for how temporary projects are built (W2-01's and W1-40's supports, for example). You read no private part of an implementation to learn what a test should expect.

## The behaviour to test

Seen from outside, after this ticket:

1. **Every check, test helper and command of the Gov OS that runs git in another folder (a temporary clone, a dev-tier clone, a temporary repository, another worktree or project root) runs it with the inherited `GIT_*` variables cleared**, so that git acts on the folder it was pointed at and never on the repository whose hook or session started it. One shared helper does it, used by every such call. A sweep record, `docs/research/AR-2-git-sweep.md`, lists every call that starts git in the Gov OS source (file, call, the folder it acts on, whether it inherits the caller's environment, how it was changed); it is the ticket's first deliverable. The list rows add: the merge helper of containment (DEC-500) gets no lazy fetch and no `GIT_TRACE`-style trace variables (W2-M105); governance git calls run with pinned configuration (no user or system git configuration leaking in) and a cleared environment (W2-M113, W2-M161); the hook starts git by an absolute path and the freeze look-up has a time limit of its own (W2-L160). Sources: AR-2, DEC-712, W2-M105, W2-M113, W2-M161, W2-L160.
2. **A hooked commit in a linked worktree leaves its branch, index and reflog as the commit made them** (the DEC-710 case). The case: a temporary repository with a linked worktree; a pre-commit hook in the hook environment git gives (with `GIT_DIR`, `GIT_INDEX_FILE` and the other variables git exports to a hook) runs a Gov OS check that clones into a temporary folder and runs `git add` and `git commit` there (the G1 retrieval-regression check did this on dev-tier clones, DEC-712). After the commit, the worktree's branch points at the commit just made and nothing else, its reflog has only that entry added, its index matches that commit, and no other branch, index or reflog of the temporary repository changed. Sources: AR-2, DEC-710, DEC-711, DEC-712.
3. **`lefthook install` and `lefthook uninstall` leave `.claude/settings.json` byte-identical to the committed file**, and the adapter-portability check stays green. The case DEC-712 records: `lefthook uninstall` rewrote `.claude/settings.json`, sorting the hook events and each hook's fields alphabetically, and adapter-portability compares that file byte for byte with what the generator writes. Test it in a temporary repository with a committed stand-in `.claude/settings.json` (in the shape of a Claude Code settings file with hooks) and the project's hooks file, run `lefthook install` then `lefthook uninstall` there, and compare bytes after each. Whether the project's own hooks file and settings would hold this is part of the behaviour; how it is achieved is not yours to choose. Sources: AR-2, DEC-712, W2-M012, W2-M281.
4. **Failure KPI: a planted `GIT_DIR` or `GIT_INDEX_FILE` in a hook's environment reaches no child git call.** Plant them (pointing at a decoy repository or index), run the Gov OS hook commands and the checks that run git in another folder under that environment, and show that the decoy is untouched and that each child git acted on its own folder. Sources: AR-2, DEC-712.

The ticket's code paths are limited to calls that start git. Several files that start git belong to other unmerged tickets and will not be changed in this run (DEC-777): W2-50's `src/gov/guard/runs.py`, `src/gov/guard/decide.py`, `src/gov/launch/launcher.py`, `src/gov/secrets/__init__.py`; W2-54's `src/gov/context/**`, `src/gov/check/schema.py`, `src/gov/retrieval/semantic.py`; W2-53's `src/gov/close/**`; W2-03's `src/gov/store/**`, `src/gov/records/**`, `src/gov/decisions/**`, `src/gov/check/citations.py`; W2-16's `src/gov/lock/**`, `src/gov/release/**`, `src/gov/check/commands.py`; W2-20's `src/gov/resources/**`, `src/gov/launch/gate*`. Your tests may name behaviour that lives in those files; if so, mark each such case in the README as "red until <ticket> merges" with the file, so the lead can list it. Do not leave them out to make the suite green.

## What you write

- Only inside `tests/acceptance/W2-05/`. You revise no earlier ticket's test unless a KPI line requires it; if one does, name it and return it as a package instead of editing it. No throwaway implementation is left in the tree.
- In proportion to the profile (DEC-221): FULL, thorough: every KPI line's success and failure, and the key edge cases the rows name (a caller that set a `GIT_*` variable on purpose for its own folder; a check in a linked worktree; a call in a command, a check and a test helper). No combinatorial expansion beyond what a KPI demands. Every covers id (AR-2, W2-M105, W2-M113, W2-M161, W2-L160) gets at least one test.
- Behaviour through public interfaces, never internals. Deterministic, no network. Tests that need `lefthook`, `rulesync` or another tool that may be absent skip with a stated reason only where the tool is truly absent, and the README names them.
- A README that maps each KPI line and covers id to its tests, gives the expected red reason of each, says how the tests run this worktree's `src/` (DEC-732), and lists every case that stays red until another ticket's merge.
- Red first: run the tests to the end, never with `-x`: `PATH=/home/usain/.nvm/versions/node/v22.23.3/bin:$PATH PYTHONPATH=/home/usain/gov-os-worktrees/W2-05/src python3 -m pytest tests/acceptance/W2-05 -q -p no:cacheprovider -rs`. They fail for the reason the README states.
- An ambiguous KPI line or a dispute is never a guess: return it as a package (question, why now, options, impact, reversibility, cost, recommendation, confidence).

## Commit

Before committing, check that `/home/usain/Dynamic-Agentic-Engineering-OS/.git/hooks` holds no `pre-commit` file (only `*.sample` files); if one is there, do not commit, and say so. Never `--no-verify`, never `core.hooksPath`. Commit only your test paths, in one commit, with the trailers in the final block (DEC-182, DEC-476):

    git commit -m "W2-05 (DAEO-0z8c): acceptance tests" --trailer "Task: DAEO-0z8c" --trailer "Role: independent-test-designer" --trailer "Implements: DEC-710" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"

After it, run `git log --oneline -2` and `git status --short` and quote them.

## Return

Your commit's hash; the test count; the KPI lines and covers ids with their tests; the red reason as you saw it; the cases red until another ticket's merge; every earlier test you would rewrite, with its reason; any package. Put these in the fields below.

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

Refused twice for the same call: stop and say so.
