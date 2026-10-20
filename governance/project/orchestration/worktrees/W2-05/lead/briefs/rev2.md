You are a fresh reviewer (the second and last review, DEC-413). Ticket DAEO-0z8c (W2-05, "The git environment of every check, hook and helper; the settings re-sort"), profile FULL, is implemented in the worktree `/home/usain/gov-os-worktrees/W2-05` on branch `w2/W2-05`, at the head `f19f156ed606eb9997cefce07e32d601b4ce3b7b`, and its acceptance tests pass except five cases that wait on other tickets' merges (named below). You probe that head for behaviour the tests miss. You write nothing in the repository.

## Step 0, before any work: the sandbox check (owner, DEC-789)

You were started through `gov launch`, sandboxed. Before anything else, run these and report their exact output first in your return (in `evidence`, and say in `status` whether the check passed):

- (a) `python3 -c "open('/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-0z8c','w').write('x')"` — a write outside your worktree. It **must fail**. If it wrote the file, do not delete it: stop there and return, naming the file.
- (b) `echo sandbox-trial | git hash-object -w --stdin` and then `git update-index --refresh` — git's own writes. They **must work** (`update-index --refresh` prints nothing or only paths that need an update, with exit 0). If either fails, stop there and return with the exact error.

These two writes of step (b) are the only writes you make; they change no file of the repository and no branch.

## Standing rules (read first)

- First run `printenv GOV_ROLE GOV_TICKET` (expect `independent-auditor` and `DAEO-0z8c`) and `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-05` and `w2/W2-05`), and `git rev-parse HEAD` (expect `f19f156ed606eb9997cefce07e32d601b4ce3b7b`). If anything differs, stop and say so.
- **DEC-732, the code under test:** in this worktree, **every test run and every `gov` command used for verification runs this worktree's own `src/`**: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-05/src` set **per command** (never in a session's `--settings` env). Your verification shows it with `PYTHONPATH=/home/usain/gov-os-worktrees/W2-05/src python3 -c "import gov; print(gov.__file__)"`, quoted in your return; it must point into this worktree.
- Run everything in the foreground, one command after another: your session ends with your last message, and nothing started in the background is ever read. A foreground command is killed after 10 minutes: keep each run within that (the W2-05 suite takes about a minute). You write nothing, so no commit of yours will exist: return when your findings are complete.
- No `git checkout` of another commit, no `git reset`, no `git clean`, no `git stash`, no commit, no amend, no rebase, no merge, no push, no tag in this worktree.
- Write no file of the repository. Your probes run in a temporary folder of your own (`mktemp -d`), and every temporary repository you need is built there from scratch with `git init`.
- Run no glob, no search and no listing over `governance/project/`: name the files you need there one by one (DEC-508). Never read `.claude/settings.json` or `.claude/settings.local.json`, in this worktree or anywhere. Nobody reads anything under `~/.claude/`.
- Never read, print, search, diff or copy the held-out file under `governance/project/`, and never type its path (DEC-525). Never read or name the qualification oracle.
- **The workbench (DEC-723).** Never write in `~/gov-os-workbench`, and never list, glob or search it. Dev-tier tests use `GOV_DEV_TIERS` by name only and clone into a temporary folder.
- Never copy the repository or a folder of it (no `cp -r`, `rsync`, `git archive`, `git worktree` or `git clone` of this repository or a folder of it) anywhere. A throwaway stand-in imports the package (with the `PYTHONPATH` above) or copies single named files, never `governance/project/`. No clone, copy or file of a programme is ever put under a `.gov-runtime/` folder (DEC-673).
- **The git hooks stay uninstalled until W2-08.** Never run `lefthook install` or `lefthook uninstall` in this repository or any of its worktrees: they share `.git/hooks` with the main tree. Run lefthook only inside a temporary repository of your own, with its working directory set to it and an environment with no `GIT_*` variable, and with a stand-in `.claude/settings.json` that you write there yourself.
- Inside a launched session `.gov-runtime/freeze` shows as a placeholder device file whether or not a flag exists: conclude nothing from it.
- Never run `gov close`, `gov adopt`, `gov pause`, `gov rebuild` or `gov checkpoint` against this worktree or the main tree. Install nothing. No subagents.
- Your temporary folder is removed when your session ends (DEC-386): every finding is in your final message.
- If the guard or the sandbox refuses something you needed for the probe, do not work around it: say so in your return. **Refused twice for the same call: stop and say so; no third try** (AR-6).

## What you read

- The ticket file `.tickets/DAEO-0z8c.md` (read-only): its KPI lines and its `allowed_paths` (`src/gov/**/*.py`, `src/gov/util/gitenv.py`, `lefthook.yml`, `template/lefthook.yml`, `tests/unit/gitenv/**`, `docs/research/AR-2-git-sweep.md`).
- The source: DEC-710, and AR-2 under `docs/research/`.
- The decisions that apply, in `docs/DECISION_REGISTER.md`: DEC-710, DEC-712, DEC-136, DEC-137, DEC-413, DEC-498, DEC-580, DEC-737.
- **The owner's DEC-783 (2026-10-18; staged for the owner's commit, not yet in this worktree's register; apply it as written here):** the third success KPI line is re-baselined: `lefthook install` leaves `.claude/settings.json` byte-identical to the committed file; `uninstall` is an owner act, followed by restoring the committed file (DEC-712). The template's hooks file is `template/lefthook.yml.jinja`, which stays untouched. The freeze look-up's own time limit (15 s, in `src/gov/guard/decide.py`) is set at a later resume, after W2-50 merges: it is not in this head.
- **DEC-777 (delegated, stricter-only):** this ticket changes no file in another unmerged or unclosed ticket's allowed paths. These files must be unchanged against the base `c94e1507`: `src/gov/guard/runs.py`, `src/gov/guard/decide.py`, `src/gov/launch/launcher.py`, `src/gov/secrets/__init__.py` (W2-50); `src/gov/context/**`, `src/gov/check/schema.py`, `src/gov/retrieval/semantic.py` (W2-54); `src/gov/close/**` (W2-53); `src/gov/store/**`, `src/gov/records/**`, `src/gov/decisions/**`, `src/gov/check/citations.py` (W2-03); `src/gov/lock/**`, `src/gov/release/**`, `src/gov/check/commands.py` (W2-16); `src/gov/resources/**`, `src/gov/launch/gate*` (W2-20). Their git calls are listed in the sweep record, marked "after <ticket> merges".
- The ticket's whole change: `git diff c94e1507..f19f156ed606eb9997cefce07e32d601b4ce3b7b` (the helper `src/gov/util/gitenv.py`, the git calls of the changed `src/gov/` files, the sweep record `docs/research/AR-2-git-sweep.md`, the unit tests under `tests/unit/gitenv/`, the acceptance tests under `tests/acceptance/W2-05/` with their README).

## The five cases that stay red at this head (expected; not findings)

- After W2-50 merges (`src/gov/guard/decide.py`): `test_the_guard_hook_does_not_run_the_git_first_on_path`, `test_the_guard_hook_refuses_within_its_own_limit_when_the_freeze_look_up_hangs`, `test_the_containment_check_catches_the_change_whatever_its_environment_holds[trace variables]` and `[a trace setting in the person's git configuration]`.
- After W2-53 merges (`src/gov/close/**`): `test_gov_close_runs_its_subprocesses_and_the_ticket_tests_with_a_sanitised_environment`.
- Inside a launched session only: `test_the_code_index_tool_started_by_gov_rebuild_gets_no_inherited_git_variable` cannot reach its assertion (the code index's daemon folder under `/tmp/gov-cbm-<uid>` is read-only in the sandbox); the lead ran it outside the sandbox at this head, and it passed. Likewise most of `tests/acceptance/W1-16` errors in the sandbox for its `/tmp` folders; outside, it passed (167).

## What the first review found, and what was done (round 1, head `0983be4c`)

The first review failed on F1. Its findings, as described behaviours:

- F1 (fixed in this round): a commit whose index lies outside the git directory, with a secret staged in that index, passed the staged-secrets gate (it scanned the default index); the base refused it. Now `gov ci staged-secrets` refuses whenever the inherited `GIT_INDEX_FILE` is not git's own index of the project, naming it, whatever is staged. The test designer wrote this as cases (3 rewritten, stricter, with `Rewrite-Reason:`, and 4 new) in `68055fa3`; the engineer's change is `2e108d85`. The question which index a hook may honour (the reading P-1 in the README) stays with the owner: the refusal holds under either answer.
- F2 (fixed in this round): the code-index tool started by the code index got every inherited `GIT_*` variable; it starts git itself. Now its environment comes from the helper, and the sweep record lists its three starts.
- F6 (fixed): sweep row 9's wording.
- F3 (residual, fails closed): `gov ci push`'s own push loses push settings given with `git -c` (`GIT_CONFIG_PARAMETERS`). F4 (residual): a work tree whose git directory is named only by `GIT_DIR`/`GIT_WORK_TREE` breaks every gov git call. F5 (residual): the containment check's pinned configuration ignores a global `core.excludesFile`. These are known; report them again only if you find they can lose work or make the guard or a gate fail open in a way the first review did not describe.

Probe this round's change above all: that the refusal of F1 cannot be passed around (an index given relatively, through a symbolic link, a path that names the git directory by another route, a linked worktree's index given from the main tree, an index under the git directory but not directly in it, an empty value), that git's own indexes are still scanned (a secret there still refused, clean content still passing), that nothing else now refuses that passed before (a hooked commit of the main tree, `commit -a`, `commit -- <path>`, a linked worktree), and that the code index still works with the environment it now gets.

## What you probe for

Behaviour the acceptance tests miss, above all a case that could:

- lose work;
- let a role write outside its scope;
- let an implementer change the acceptance tests;
- make the guard or a gate fail open.

For this ticket in particular:

- a git call in a check, hook, helper or command (in this ticket's changed files) that still inherits `GIT_DIR`, `GIT_INDEX_FILE`, `GIT_WORK_TREE`, `GIT_OBJECT_DIRECTORY`, `GIT_COMMON_DIR`, `GIT_CEILING_DIRECTORIES`, a `GIT_TRACE*` variable or another `GIT_*` variable from its caller;
- a git call anywhere under `src/gov/` that the sweep record misses (count them yourself), or a row of the record that does not match the code;
- the helper clearing a variable the call needs, such as one the caller set on purpose for that call, the person's identity, or the push transport;
- a hooked commit in a linked worktree (of a temporary repository) that moves another branch, index or reflog, or leaves its own branch, index or reflog other than as the commit made them;
- `.claude/settings.json` changed in any byte by `lefthook install` in a temporary repository (with the project's `lefthook.yml` and with the template's `template/lefthook.yml.jinja`); and after `uninstall` followed by `git restore -- .claude/settings.json`, any difference left;
- a planted `GIT_DIR` or `GIT_INDEX_FILE` in a hook's environment that reaches a child git call of the changed code;
- a guard or gate decision of the changed code that now answers "allow" or "pass" where it refused before (for example a containment check that misses a change because of the environment it was given);
- any file of another unmerged ticket changed (the DEC-777 list above).

Run the code; do not judge it by reading alone. A finding you could not reproduce is marked as such. Run the acceptance suite and the unit tests of the helper once, to the end, never with `-x`:

    PATH=/home/usain/.nvm/versions/node/v22.23.3/bin:$PATH PYTHONPATH=/home/usain/gov-os-worktrees/W2-05/src python3 -m pytest tests/acceptance/W2-05 -q -p no:cacheprovider -rs
    PYTHONPATH=/home/usain/gov-os-worktrees/W2-05/src python3 -m pytest tests/unit/gitenv -q -p no:cacheprovider

Before you return, run `git status --short` and `git log --oneline -1` and quote them: the status must be empty and the head `f19f156ed606eb9997cefce07e32d601b4ce3b7b`.

## Return

The head you probed; your session's own judgement, `pass` or `fail` (fail if any finding could lose work, let a role write outside its scope, let an implementer change the acceptance tests, or make the guard or a gate fail open); and each finding as a described behaviour, never as code (DEC-136): what was done, what happened, what should have happened, its severity, and whether it loses work or fails open. Say also what you probed and found sound. You repair nothing (MR-4). The lead writes the probe record from your return.

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

Put the sandbox check's result (a) and (b) first in `evidence`, and your judgement (`judgement: pass` or `judgement: fail`) and your findings in `work_completed` and `discoveries`.

Refused twice for the same call: stop and say so.
