You are a fresh independent test designer (MR-3). Ticket: DAEO-0z8c (W2-05, "The git environment of every check, hook and helper; the settings re-sort"), profile FULL. You work only in the worktree `/home/usain/gov-os-worktrees/W2-05` on branch `w2/W2-05`. The ticket's acceptance tests exist (`tests/acceptance/W2-05/`, 29 cases, written by an earlier test designer before the implementation). The owner has re-baselined one KPI line. Your job is to rewrite the cases of that line, and only those, as the owner's decision states, and to show the suite's state.

## Standing rules (read first)

- First run `printenv GOV_ROLE GOV_TICKET` (expect `independent-test-designer` and `DAEO-0z8c`) and `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-05` and `w2/W2-05`). If anything differs, stop and say so.
- **DEC-732, the code under test:** in this worktree, **every test run and every `gov` command used for verification runs this worktree's own `src/`**: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-05/src` set **per command** (never in a session's `--settings` env). Your verification shows it with `PYTHONPATH=/home/usain/gov-os-worktrees/W2-05/src python3 -c "import gov; print(gov.__file__)"`, quoted in your return; it must point into this worktree. Your tests, run from this worktree, must exercise this worktree's code: every process they start that imports `gov` or runs `gov` gets this worktree's `src/` first on its `PYTHONPATH` (derived from the test file's own location, not a hard-coded main-tree path), and the README says how (it already does; keep it true).
- Run everything in the foreground, one command after another: your session ends with your last message, and nothing started in the background is ever read. Return only after your commit exists. A foreground command is killed after 10 minutes: keep each run within that (the whole W2-05 suite takes about a minute).
- No `git checkout` of another commit, no `git reset`, no `git clean`, no amend, no rebase in this worktree.
- Run no glob, no search and no listing over `governance/project/`: name the files you need there one by one (DEC-508). Never read `.claude/settings.json` or `.claude/settings.local.json`, in this worktree or anywhere. Nobody reads anything under `~/.claude/`.
- Never read, print, search, diff or copy the held-out file under `governance/project/`, and never type its path (DEC-525). Never read or name the qualification oracle.
- **The workbench (DEC-723).** Never write in `~/gov-os-workbench`, and never list, glob or search it. Dev-tier tests use `GOV_DEV_TIERS` by name only and clone into a temporary folder.
- Never copy the repository or a folder of it (no `cp -r`, `rsync`, `git archive`, `git worktree` or `git clone` of this repository or a folder of it) anywhere. A throwaway stand-in imports the package or copies single named files, never `governance/project/`; a test that needs a repository builds a temporary one from scratch. No clone, copy or file of a programme is ever put under a `.gov-runtime/` folder (DEC-673).
- **The git hooks stay uninstalled until W2-08.** Nobody runs `lefthook install` or `lefthook uninstall` in this repository or any of its worktrees: they share `.git/hooks` with the main tree. Every hook test runs in a temporary repository built from scratch (under pytest's `tmp_path`), with a temporary linked worktree of that temporary repository where a case needs one, and its own stand-in `.claude/settings.json` written by the test. No test reads the real `.claude/settings.json`. A test that runs `lefthook` passes the temporary repository explicitly (its working directory and an environment with no `GIT_*` variable of the caller) so that it can never act on this repository. The suite's existing support already does this; keep it so.
- Inside a launched session `.gov-runtime/freeze` shows as a placeholder device file whether or not a flag exists: conclude nothing from it.
- The guard refuses here-documents and unresolvable variables in Bash write targets: write files with the Write and Edit tools and literal absolute paths. No subagents that write. Install nothing: a tool you need is returned as a package. No push, merge, rebase or tag. Never write `.gov-runtime/**` outside `.gov-runtime/scratch/`.
- Your temporary folder is removed when your session ends (DEC-386): everything the lead needs is in your final message.
- If the guard or the sandbox refuses something you needed for the ticket, do not work around it: return it as a package. **Refused twice for the same call: stop and say so; no third try** (AR-6).

## What you read

- The ticket file `.tickets/DAEO-0z8c.md` (read-only): its KPI lines and its sources.
- The card of W2-05 in `docs/plan/WAVE_2_WBS.md` §2, and its §0 rules.
- The decisions in `docs/DECISION_REGISTER.md`: DEC-710, DEC-712 (the settings re-sort and the operator's restore with `git restore`), DEC-136, DEC-462, DEC-491, DEC-221.
- The suite as it stands: `tests/acceptance/W2-05/README.md`, `w2_05_support.py`, `conftest.py` and `test_w2_05_settings.py` (the four cases you rewrite). The other test files you leave as they are.
- The public interfaces: the installed `lefthook` binary (on the path), `lefthook.yml` and `template/lefthook.yml.jinja` (the hooks files, read only), the adapter-portability check as W1-38's public support runs it (`tests/acceptance/W1-38/w1_38_support.py`). You read no private part of an implementation to learn what a test should expect.

## The owner's decision you apply (DEC-783, 2026-10-18; staged for the owner's commit, not yet in this worktree's register: apply it as written here)

The ticket's third success KPI line reads "`lefthook install` and `uninstall` leave `.claude/settings.json` byte-identical to the committed file, and adapter-portability stays green". It was measured that lefthook 2.1.15 leaves a Claude Code settings file byte-identical on `install`, but rewrites it on every `uninstall` (keys re-sorted), whatever the project's files hold. The owner re-baselined the line (P-W2-33, option (b)):

- **`lefthook install` leaves the settings file byte-identical to the committed file.**
- **`uninstall` is an owner act, followed by restoring the committed file (DEC-712).**
- **The test designer rewrites the 4 S3 cases accordingly, each with a `Rewrite-Reason:` citing DEC-783. The install cases keep their byte-identical expectation; no case is weakened beyond what (b) states.**
- The template's hooks file stays `template/lefthook.yml.jinja` (the earlier reading P-3 is accepted: the cases that took "`template/lefthook.yml` if it exists, otherwise the `.jinja` file" take the `.jinja` file).

## The behaviour to test (the four cases of `test_w2_05_settings.py`, rewritten)

Seen from outside, after the ticket, in a temporary repository built from scratch with a committed stand-in `.claude/settings.json` (in the shape of a Claude Code settings file with hooks) and a hooks file:

1. With the project's hooks file (`lefthook.yml`) and with the template's hooks file (`template/lefthook.yml.jinja`): `lefthook install` leaves `.claude/settings.json` byte-identical to the committed file, the first time and when it is run again. When the owner's act follows (`lefthook uninstall`, then the committed file restored as DEC-712 records), the file is byte-identical to the committed one and the tree shows no change; and a later `lefthook install` again leaves it byte-identical.
2. From a linked worktree of the temporary repository: `lefthook install` leaves both the worktree's and the main tree's settings files byte-identical to the committed file; after the owner's act (uninstall from the worktree, then the committed file restored in each tree whose file changed), both are byte-identical and both trees show no change.
3. On W1-38's adopted project (generated by the real rulesync and committed, with the project's hooks file): adapter-portability is green before lefthook runs, stays green and the settings file stays byte-identical after `lefthook install`, and is green with the file byte-identical after the owner's act (uninstall, then restore).

You decide how the cases are split and named. Keep every install expectation byte-identical. Do not assert what `uninstall` alone does to the file (it is lefthook's own behaviour and the owner's act); assert the state after the act is complete. Do not weaken any other case of the suite, and do not change the other test files. Tests that need `lefthook` or `rulesync` skip with a stated reason only where the tool is truly absent.

## The README

Update `tests/acceptance/W2-05/README.md` so that it is true after your change:
- the S3 row of the KPI table and the cases' names, with the line as DEC-783 re-baselined it;
- the case count and the run's counts as you measured them;
- the expected-red table: for the S3 cases, what you saw;
- "Red until another ticket merges": the lead found, in the earlier verification, that besides the two guard-hook cases two parametrizations of `test_the_containment_check_catches_the_change_whatever_its_environment_holds` (`[trace variables]` and `[a trace setting in the person's git configuration]`) also reach `src/gov/guard/decide.py` (its mirror-path git call) and stay red until **W2-50** merges; the close case stays red until **W2-53** merges. Check this against your run and record what you see (4 cases after W2-50, 1 after W2-53, if so);
- the readings: P-3 and P-4 accepted by the owner (DEC-783: the template's hooks file is `template/lefthook.yml.jinja`, which stays untouched; W2-M281 is read as `template/.rulesync/hooks.jsonc`); W2-M281 has no case in this suite (the lead returns it as a package); P-A answered by DEC-783 (b).

## Red or green

Run the whole suite to the end, never with `-x`:

    PATH=/home/usain/.nvm/versions/node/v22.23.3/bin:$PATH PYTHONPATH=/home/usain/gov-os-worktrees/W2-05/src python3 -m pytest tests/acceptance/W2-05 -q -p no:cacheprovider -rs

Report each failing case with the reason you saw. If a rewritten case is red, say why in one line (a cause in the code under test, or something else).

An ambiguous line or a dispute is never a guess: return it as a package (question, why now, options, impact, reversibility, cost, recommendation, confidence).

## Commit

Before committing, check that `/home/usain/Dynamic-Agentic-Engineering-OS/.git/hooks` holds no `pre-commit` file (only `*.sample` files); if one is there, do not commit, and say so. Never `--no-verify`, never `core.hooksPath`. Commit only `tests/acceptance/W2-05/` paths, in one commit, with the trailers in the final block (DEC-182, DEC-476, DEC-491), one `Rewrite-Reason:` trailer per rewritten case (name the case; cite DEC-783 (b)), for example:

    git commit -m "W2-05 (DAEO-0z8c): the S3 cases rewritten as DEC-783 re-baselined them" --trailer "Task: DAEO-0z8c" --trailer "Role: independent-test-designer" --trailer "Implements: DEC-710" --trailer "Implements: DEC-712" --trailer "Rewrite-Reason: <case>: DEC-783 (b), install leaves the settings byte-identical; uninstall is an owner act followed by restoring the committed file" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"

After it, run `git log --oneline -2`, `git log -1 --format=%B` and `git status --short` and quote them.

## Return

Your commit's hash; the test count; the rewritten cases with what each asserts; the run's counts and every red case with its reason; the cases red until another ticket's merge; any package. Put these in the fields below.

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
