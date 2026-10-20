---
id: W2-59-CIT-P
type: change-impact-proposal
status: PROPOSED
date: 2026-10-20
branch: w2/W2-59
base: w2/integrate @ 74d22909 (merged by 3eadca4c; the change started at c5100159)
author: engineer (W2-59, DAEO-kh9l, run 1; brought up to date in run 2)
scope_approved: owner, 2026-10-19 (DEC-835)
decisions_carried: [DEC-822, DEC-835, DEC-864, DEC-853, DEC-854, DEC-831, DEC-732, DEC-579, DEC-135, DEC-750, DEC-754, CAP-33]
state_class: EVIDENCE
---

# W2-59 — Change-impact proposal (CIT-P): the pinned judge

This change makes the judge judge with its own code. Under the bootstrap pin (DEC-822 step 1), `gov check` still ran
the declared checks and the guard's hook programs from the working tree's `src/`, so a ticket that edits a check
changes the check that judges it. It is a judge change, so it comes to the owner through CIT-P (CAP-33). The owner
approved its scope in DEC-835; this record states what changed, what stays, the owner acts it needs, the risks and
the rollback.

The change started on `w2/integrate` at `c5100159`; the line numbers and code cited "at `c5100159`" below are from
there. The branch now also holds `w2/integrate` at `74d22909`, by the merge `3eadca4c` (git's own merge of its two
parents, no conflict; its record corrected in `6d4925ab`, DEC-750). That merge brought W2-62's session-start hook
change (merged `6e4b2750`) and W2-50's secrets-scan fix (merged `98effadc`, DEC-853); it touched none of this
change's files.

The merge `3eadca4c` carries no `Task:` trailer (its subject names `DAEO-kl9l` by a typing error; `6d4925ab` records
this, unamended). Once it is in `w2/integrate`, `gov close`'s gate for work without a task reads its paths as nobody's
work. That gate, `_check_unmeasured` in `src/gov/close/command.py`, takes the commits of the closing ticket's range
(`<its first commit>..HEAD`, its own left out); for each commit whose `Task:` trailers name none of the project's
tickets, the paths it changes (for a merge, what it brings to its first parent: 543 paths for `3eadca4c`, among them
other tickets' ticket files, checkpoints and probe records) that are the closing ticket's work (its acceptance
tests, a path inside its allowed paths, its own ticket file) refuse the close with `WORK_WITHOUT_TASK`. Only a
FULL-profile ticket's probe gate leaves out the merges after its probed commit that are git's own merge on the
probed paths (DEC-754); a STANDARD or LITE close leaves out none. So another ticket whose work is among those paths
and whose range holds `3eadca4c` is refused. This is package P-W2-59-5, open with the orchestrator (§7).

## 1. The evidence

| # | Finding | Source |
|---|---|---|
| E1 | Under the bootstrap pin's `gov check` of 2026-10-19, `secrets-indexing` ran from `/home/usain/Dynamic-Agentic-Engineering-OS/src/gov/…`, not from the pin | The pin's dry run; plan §4.1; DEC-835 |
| E2 | `src/gov/check/runner.py` `_run_command` put the project's `src` first on `PYTHONPATH` and ran the declared command by `sh -c`, so `python3 -m gov.check.*` ran the first `python3` on `PATH` with the tree's package | Code at `c5100159`, lines 76–91 |
| E3 | The hook lines in `.rulesync/hooks.jsonc` ran `PYTHONPATH="$CLAUDE_PROJECT_DIR/src" python3 …` (three lines) or a bare `python3 …` (four lines): the first `python3` on `PATH`, and for three of them the tree's package | `.rulesync/hooks.jsonc` at `c5100159` |
| E4 | `gov/retrieval/canary.py:10` and `gov/retrieval/retrieve_check.py:16` found the repository from their own install path (`parents[3]`); from a wheel that is `site-packages/../..`, never the project | The pin's dry run; DEC-835 item 2 |
| E5 | `retrieve_baseline.yaml` was not in the wheel: the installed retrieval-regression check failed with `FileNotFoundError` before it read anything | The pin's dry run; W2-59's acceptance tests, red before this change |
| E6 | `gov --version` was a usage error (exit 2) | W2-59's acceptance tests, red before this change |

`src/gov/**` was searched for every use of `__file__`: only the two modules of E4 find the repository from it. The
others find the package's own files (the reranker worker, the close command's test-runner plugins, the command
modules), which is right for an installed package.

## 2. The three options (DEC-105)

| Option | What it means | Cost |
|---|---|---|
| **Apply now** (approved, DEC-835) | This change: 71 lines added, 21 removed in six files, plus builder tests | One ticket; after the merge the owner re-pins at the merge commit, then regenerates the settings file (§7) |
| Defer | Keep the pin as the `gov` on `PATH` while the checks and hooks still run from the tree | The judge fails open for every ticket that edits a check or a hook's package (E1) |
| Re-baseline | Rework the check declarations into a form the judge imports in-process | Rewrites every declaration and the runner; not needed to close the gap |

## 3. What changes

### 3.1 The judge runs the declared checks with its own interpreter and package (DEC-822 item 3)

`src/gov/check/runner.py`:

- a declared command that starts with `python3` runs as `<the judge's sys.executable> -P …`; one that starts with
  `gov` runs as `<the judge's sys.executable> -P -m gov.cli.main …`. Every other command (`openspec validate
  --strict`) is left as declared;
- the runner no longer puts `<root>/src` on the check's `PYTHONPATH`. The judge's own command line carries no
  `PYTHONPATH` naming the project;
- `-P` keeps the working folder, the project's root, off the check's import path, so a `gov/` package at the
  project's root is not imported either.

The project under check supplies only data: its declarations, its files, its git history. A check module edited in
the project's `src/` does not change an installed judge's verdict.

### 3.2 The hook lines start their program with the pin's interpreter (DEC-822 step 2)

Each of the seven lines in `.rulesync/hooks.jsonc` now finds the pin and starts its program with the pin's
interpreter. Only the interpreter part changes: the program path (`$CLAUDE_PROJECT_DIR/template/governance/kernel/
hooks/<name>.py`) stays, so `gov launch` still finds the guard by the text `hooks/pretooluse.py`. The form, in
`sh`:

    g="$HOME/.local/bin/gov"; [ -f "$g" ] || g="$(command -v gov)" || { echo "…no pinned gov…" >&2; exit 2; };
    read -r p < "$g"; p="${p#'#!'}"; [ -x "$p" ] || { echo "…names no interpreter that runs…" >&2; exit 2; };
    exec "$p" -E "$CLAUDE_PROJECT_DIR/template/governance/kernel/hooks/pretooluse.py"

- **No versioned path.** The line names the owner's stable link `~/.local/bin/gov` (→ `<pin env>/bin/gov`), else
  the `gov` on `PATH`. The interpreter is the first line of that console script, which pip writes as
  `#!<pin env>/bin/python`; it moves with each re-pin without any edit of the line.
- **The rollback is followed.** The owner's documented rollback replaces the link with an editable install's own
  `gov` script: its first line names that install's interpreter, and the line starts that one.
- **The project's `src` is not put on the import path** by the line: the program imports the pin's installed
  package.
- **An import path the session inherited is not used either (run 2).** Every worker session started by the
  committed launch form (`PYTHONPATH=<worktree>/src python3 -m gov.cli.main launch …`, `governance/project/briefs/
  LEAD-w2-common.md`) carries `PYTHONPATH=<worktree>/src`, because the launcher passes its own environment on
  (`src/gov/launch/launcher.py`, `env = {**os.environ, **settings["env"]}`), and Claude Code runs the hook lines with
  the session's environment. The pin's interpreter honoured that variable, so in a worker session the program
  imported the tree's `gov`: an edited guard in the tree decided the worker's calls. DEC-822 item 3 has the
  per-command `PYTHONPATH` choose only the code under test, never the judge, so each line now starts its program as
  `"$p" -E …`: the interpreter ignores every `PYTHON*` variable of the environment (`PYTHONPATH`, `PYTHONHOME`,
  `PYTHONUSERBASE` among them), so no folder the session names is put on the import path and no `sitecustomize`
  there runs. The interpreter's own `site` still runs, so an editable install, which finds its package through its
  own `site-packages` entry, still works after the owner's rollback. Seen in this run's own session, which carries
  `PYTHONPATH=/home/usain/gov-os-worktrees/W2-59/src`: the pin's interpreter imported
  `…/W2-59/src/gov/__init__.py`; with `-E`, `…/pin-fecb870c/lib/python3.12/site-packages/gov/__init__.py`.
- **Never fail open.** If neither the link nor `PATH` gives a `gov`, or its first line names nothing that runs, the
  line prints why on standard error and ends: with **exit 2** for `preToolUse` (Claude Code blocks the call) and
  for `postToolUse` and `postToolUseFailure` (the message reaches the session; it does not end silently), and with
  **exit 1** for `preCompact`, `sessionStart`, `stop` and `subagentStop` (a non-blocking error shown to the owner: an
  exit 2 there would block the compaction or keep a session from stopping, while the guard's line already blocks
  every tool call).

No new stable name was needed: the link `~/.local/bin/gov` exists and is the one the pin commands maintain.

### 3.3 The project under check, not the install path (DEC-835 item 2; DEC-579)

- `gov/retrieval/canary.py` reads the canary declarations of the project under check, in either layout of its
  kernel: `template/governance/kernel/canaries/` (this repository), else `governance/kernel/canaries/` (an adopted
  project). A project that declares none gets `FACET_UNAVAILABLE` ("unreadable canary declaration"); it is never
  given the install path's.
- `gov/retrieval/retrieve_check.py` adopts each dev tier with the path map and the gitleaks configuration of the
  project under check (the working folder, where the runner starts the check, DEC-285): the path map at
  `governance/project/path-map.yaml`; the gitleaks configuration at `template/.gitleaks.toml`, else `.gitleaks.toml`.
  The baseline stays the package's own file, read beside the module.

### 3.4 The baseline ships (DEC-835 item 2)

`pyproject.toml` declares `retrieve_baseline.yaml` as package data of `gov.retrieval`. A builder test fails if any
non-Python file under `src/gov/` is not declared as package data.

### 3.5 `gov --version`

`gov --version`, with no command and outside any project, prints `gov <version> (commit <sha>)` and exits 0. From a
source tree (a `src/gov` beside a `pyproject.toml`) the version is that `pyproject.toml`'s and the commit is the
`HEAD` of the repository whose top is that tree, never that of the working folder's repository. An installed
package names the version it was built with and `(commit unknown)`; it runs no git, so it can never name a wrong
commit. Whether a build should record its commit is decided: `gov --version` stays as built, and a release that
records its commit is row W2-L371, for W2-16 and W2-18 (DEC-864 item 3; §7, P2).

## 4. What stays

- **DEC-822 item 3:** DEC-732's per-command `PYTHONPATH=<worktree>/src` stays. It now chooses only the code under
  test: a judge started that way is the tree's code by intent, and its checks inherit that `PYTHONPATH` with it. A
  bare `gov` is the pinned judge only where the environment carries no `PYTHONPATH`.
- **DEC-822 item 3 in a worker session.** A bare `gov` in a session whose environment carries `PYTHONPATH` runs the
  code that variable names, because the pin's console script starts its interpreter without `-E` and the
  interpreter follows the variable. Seen in this run's own session (launched with
  `PYTHONPATH=/home/usain/gov-os-worktrees/W2-59/src`): a bare `gov --version` printed
  `gov 0.1.0 (commit 6e95cd41…)`, the tree's code naming the tree's `HEAD`; with that variable removed from its
  environment, the same `gov` is the pin built from `fecb870c`, which has no `--version` and answers with a usage
  error. The hook lines no longer do this (§3.2). Two questions stay open, both the orchestrator's to decide, not
  this change's:
  - **P-W2-59-6:** whether a bare `gov` with a per-command `PYTHONPATH` (or one inherited) should run the pin or
    the tree.
  - **P-W2-59-7:** the launcher carries `PYTHONPATH` into every session it starts (`src/gov/launch/launcher.py`
    passes its own environment on, and the committed launch form sets it). The launcher is outside this ticket's
    paths: a row for the launcher's ticket.
- The declarations, their format and their commands are unchanged; the runner's time limits, environment
  (`XDG_*`), working folder and verdict rules are unchanged.
- `template/governance/kernel/hooks/precompact.py` and `sessionstart.py` still put the project's `src` on their own
  import path when that folder exists (`sessionstart.py`'s `_add_src`, still there after W2-62's change came in by
  the merge `3eadca4c`). That is outside this ticket's paths: it is row W2-M389, for W2-10 (DEC-864 item 2).
- The generated settings file is not touched (§7).

## 5. The pin ladder's consequence

The judge is now the pin, so what the pin does not hold does not judge:

- a check new in the tree (a new module under `gov/check/`) runs only after a re-pin that holds it: before that,
  the pinned judge fails on a module it does not have (`No module named …`) and the check is RED (YELLOW for a
  warning);
- a ticket that changes a format the judge reads (declarations, path map, ticket files, registers) needs a release
  that accepts the new format first (DEC-822 item 5);
- a fix to a check reaches the judge only with the next re-pin.

## 6. The overlap with W2-05 (DEC-854)

W2-05's unmerged branch (`w2/W2-05` at `f19f156e`) changes the same two files. `git merge-tree` of this branch
with it gives two small conflicts, each resolved by keeping both sides (DEC-750, DEC-754). Re-checked in run 2 at
`fc8f8494`, after the merge `3eadca4c` (`git merge-tree --write-tree --name-only HEAD w2/W2-05`, read-only):
`w2/W2-05` is still at `f19f156e`, and the conflicts are the same two, in the same lines:

| File | This change | W2-05 | Resolution |
|---|---|---|---|
| `src/gov/check/runner.py`, `_run_command` | adds `command = _judged(command)`; removes the four lines that put `<root>/src` on `PYTHONPATH` | `env = dict(os.environ)` becomes `env = git_env(root)` | `command = _judged(command)`, then `env = git_env(root)`; the four `PYTHONPATH` lines stay removed. W2-05 also drops the `os` import, which this change no longer needs beyond that line |
| `src/gov/retrieval/retrieve_check.py`, top of the module | `REPO_ROOT` replaced by `GITLEAKS_CONFIGS` | adds `from gov.util.gitenv import git_env` beside `REPO_ROOT` | keep W2-05's import and `GITLEAKS_CONFIGS`; `REPO_ROOT` stays removed |

W2-05's block that clears the environment at the start of `main` does not conflict: this change adds one line
(`project = Path.cwd()`) further down. This change imports nothing from `gov.util.gitenv`.

## 7. Owner acts and packages

| # | Act | When |
|---|---|---|
| A1 | Re-run the pin commands at the merge commit of this ticket into `w2/integrate`, which must also hold W2-50's secrets fix (DEC-835 item 4, DEC-853 item 4). That fix is on `w2/integrate` (`98effadc`) and on this branch (`3eadca4c`), so this ticket's merge commit holds both | First, after the merge |
| A2 | Regenerate the settings file from `.rulesync/hooks.jsonc` (the generated files are the owner's). Until then the live hooks keep the old lines, and the adapter-portability check is RED with one finding, `GENERATED_DIFFERS` (DEC-835 item 3). The ticket lead's `gov check` of run 2 shows exactly that: `adapter-portability` RED with one finding, `GENERATED_DIFFERS` on the generated settings file (the lead's record) | After A1 |

The order is corrected from run 1's record, which had the regeneration first: re-pinning first means the live hook
programs (read from the tree) and the pin's package they import match from the first regenerated session.

| # | Package | Decided |
|---|---|---|
| P1 | `precompact.py` and `sessionstart.py` put the project's `src` on their own import path (§4) | P-W2-59-1 (b): row W2-M389, for W2-10 (DEC-864 item 2) |
| P2 | Whether `gov --version` should know its commit from an installed wheel (a build that records it) | P-W2-59-2 (a) now, (c) later: stays as built; row W2-L371, for W2-16 and W2-18 (DEC-864 item 3) |
| R1 | The residual: the hook programs are still read from the tree while the package they import comes from the pin, so a ticket that changes a hook program and that package together would block every tool call until a re-pin | Row W2-M390, for W2-18 (DEC-864 item 4) |
| R2 | A file under `.gov-runtime/` that vanishes during the secrets scan fails `secrets-indexing` with `FileNotFoundError` (seen in run 1) | Row W2-M388, for W2-45 (DEC-864 item 4) |
| P-W2-59-5 | The merge `3eadca4c` has no `Task:` trailer; once in `w2/integrate`, `_check_unmeasured` reads the paths it brings as work without a task and refuses the close of another ticket whose work is among them (§1) | Open, with the orchestrator |
| P-W2-59-6 | Whether a bare `gov` with a per-command or inherited `PYTHONPATH` runs the pin or the tree (§4) | Open, with the orchestrator |
| P-W2-59-7 | The launcher carries `PYTHONPATH` into every session (§4); outside this ticket's paths | Open, with the orchestrator: a row for the launcher's ticket |

## 8. The earlier tests revised (DEC-864 item 1)

Three earlier acceptance cases assumed what DEC-822 item 3 and DEC-835 remove (P-W2-59-4):

- `tests/acceptance/W1-26/test_w1_26_planted_defects.py::test_planted_authority_defect_decision_checker_exception_not_swallowed`
  planted a raising decision checker in the judged project's `src/gov/` and expected the judge to import it; the
  judge now runs its own package (§3.1).
- `tests/acceptance/W1-22/test_w1_22_canaries.py::TestCanaryRunner::test_lexical_canary_hits_after_reindex` and
  `::test_semantic_canary_hits_after_reindex` used a fixture project with no canary declarations and expected the
  canaries to be found from the install path; the canary runner now reads the project's own (§3.3).

A fresh independent test designer in this ticket's resume revised their setup only, in commit `45c6bfae`
(`Role: independent-test-designer`, `Rewrite-Reason: DEC-822 item 3, DEC-835 (DEC-864)`; six files under
`tests/acceptance/W1-22/` and `tests/acceptance/W1-26/`): W1-26's raising checker is planted in the judge's own
code, and W1-22's fixture carries the kernel's canary declarations, as an adopted project does through the copier
template (DEC-579). The behaviours they guard stay: an exception in the decision checker is never swallowed, and
canaries hit after a reindex. No KPI of W1-22 or W1-26 changed and no expectation was lowered (DEC-864 item 1).

## 9. Risks

| Risk | Effect | Mitigation |
|---|---|---|
| A pin whose console script pip wrote in the long-path form (`#!/bin/sh` and an `exec` line, used when the interpreter path is longer than 127 characters or holds a space) | The line would start the hook program with `sh`, which fails; for `preToolUse` the call is refused, not allowed | The owner's pin path (`~/.local/share/gov-os/pin-<sha>/bin/python`) is about 50 characters |
| A session whose `HOME` has no `~/.local/bin/gov` and whose `PATH` has no `gov` | Every tool call is refused with "no pinned gov" | Intended: the guard does not fail open. The message names both places looked at |
| A declared check that starts `python3` or `gov` again inside itself | That inner call would run what is first on `PATH` | None does today (`src/gov` searched) |
| `-P` takes the script's own folder off the import path of a declared `python3 <script>.py` | Such a script could not import its siblings | Every declaration today is `python3 -m …` or `gov …` |
| The merge with W2-05 | Two conflicts | §6 gives the resolution |
| The hook programs come from the tree, their package from the pin (§7, R1) | A ticket that changes both blocks every tool call until a re-pin | Row W2-M390 (W2-18): a hook program and its package move together on the pin ladder, or the program says what to re-pin |
| An import path the session inherited (every launched worker carries `PYTHONPATH=<worktree>/src`, §3.2) | Before run 2 the pin's interpreter followed it: the tree's `gov` decided the worker's calls, an edited guard failing open | Each line starts `"$p" -E …`: no `PYTHONPATH` (nor `PYTHONHOME`, `PYTHONUSERBASE`) of the session is used; W2-59's acceptance tests check it for all seven lines and for the rollback |
| `-E` drops every `PYTHON*` variable, not only `PYTHONPATH` | A setting the owner put in the environment (`PYTHONUTF8`, `PYTHONIOENCODING`, a user install under a non-default `PYTHONUSERBASE`) does not reach the hook program | None is used by the hook programs or the pin; an editable install in a venv or the default user site is still found |

Residuals the independent review named, proposed as rows for the Wave 3 hardening pass (one line each):

| Residual | Proposed |
|---|---|
| The `preToolUse` line checks only that the named interpreter is an executable file, not that it is a Python that runs the program | Row for the Wave 3 hardening pass |
| `gov --version` from a source tree follows a `GIT_DIR` set by hand | Row for the Wave 3 hardening pass |
| Only a declared command whose first word is exactly `python3` or `gov` is rewritten to the judge's interpreter (§3.1) | Row for the Wave 3 hardening pass |
| A project that holds both kernel layouts with different canary declarations uses the template's silently (§3.3) | Row for the Wave 3 hardening pass |

## 10. Rollback

Revert this ticket's merge commit. The hook lines return exactly to their form at `c5100159`: three lines
(`preToolUse`, `postToolUse`, `postToolUseFailure`) were `PYTHONPATH="$CLAUDE_PROJECT_DIR/src" python3 …` and four
(`preCompact`, `sessionStart`, `stop`, `subagentStop`) a bare `python3 …`, each the first `python3` on `PATH`, with
no check of their own that it runs. The runner returns to the tree's `src`, and the owner regenerates the
settings file again. The pin itself is not touched by this
change; the owner's pin rollback (the link `~/.local/bin/gov` back to an editable install's `gov`) is followed by
the new hook lines without an edit.

## 11. Verification

Run 1's figures, before the merge `3eadca4c` and the revision of §8:

- W2-59's acceptance tests (`tests/acceptance/W2-59`): 44 passed, from a stand-in pin built from this branch.
- W1-38's acceptance tests (the hook-source tests): 201 passed.
- Builder tests: `tests/unit/check/test_w2_59_judged_commands.py`, `tests/unit/cli/test_w2_59_version.py`,
  `tests/unit/retrieval/test_w2_59_project_root.py`; and the existing `tests/unit/validate/test_canary.py` unchanged
  and passing.

Run 2's verification, after the merge and the revision, is the ticket lead's and is recorded in the lead's return.

Run 2's engineer, after the change of §3.2 (`-E` on each line), every run with
`PYTHONPATH=/home/usain/gov-os-worktrees/W2-59/src` (`gov.__file__` = `/home/usain/gov-os-worktrees/W2-59/src/gov/__init__.py`):

- W2-59's acceptance tests (`tests/acceptance/W2-59`, revised in `6e95cd41`): 55 passed (the nine cases of a
  worker's inherited `PYTHONPATH`, red at `6e95cd41` by the lead's record, now pass).
- W1-38's acceptance tests (the hook-source tests): 201 passed.
- Builder tests: the three files above and `tests/unit/validate/test_canary.py`: 16 passed.
