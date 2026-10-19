---
id: W2-59-CIT-P
type: change-impact-proposal
status: PROPOSED
date: 2026-10-20
branch: w2/W2-59
base: w2/integrate @ c5100159
author: engineer (W2-59, DAEO-kh9l, run 1)
scope_approved: owner, 2026-10-19 (DEC-835)
decisions_carried: [DEC-822, DEC-835, DEC-854, DEC-831, DEC-732, DEC-579, DEC-135, CAP-33]
state_class: EVIDENCE
---

# W2-59 — Change-impact proposal (CIT-P): the pinned judge

This change makes the judge judge with its own code. Under the bootstrap pin (DEC-822 step 1), `gov check` still ran
the declared checks and the guard's hook programs from the working tree's `src/`, so a ticket that edits a check
changes the check that judges it. It is a judge change, so it comes to the owner through CIT-P (CAP-33). The owner
approved its scope in DEC-835; this record states what changed, what stays, the owner acts it needs, the risks and
the rollback.

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
| **Apply now** (approved, DEC-835) | This change: 71 lines added, 21 removed in six files, plus builder tests | One ticket; the owner regenerates the settings file and re-pins after the merge (§7) |
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
    exec "$p" "$CLAUDE_PROJECT_DIR/template/governance/kernel/hooks/pretooluse.py"

- **No versioned path.** The line names the owner's stable link `~/.local/bin/gov` (→ `<pin env>/bin/gov`), else
  the `gov` on `PATH`. The interpreter is the first line of that console script, which pip writes as
  `#!<pin env>/bin/python`; it moves with each re-pin without any edit of the line.
- **The rollback is followed.** The owner's documented rollback replaces the link with an editable install's own
  `gov` script: its first line names that install's interpreter, and the line starts that one.
- **The project's `src` is not put on the import path** by the line: the program imports the pin's installed
  package.
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
commit. Whether a build should record its commit is an open question for the owner (§7, P3).

## 4. What stays

- **DEC-822 item 3:** DEC-732's per-command `PYTHONPATH=<worktree>/src` stays. It now chooses only the code under
  test: a judge started that way is the tree's code by intent, and its checks inherit that `PYTHONPATH` with it. A
  bare `gov` is the pinned judge.
- The declarations, their format and their commands are unchanged; the runner's time limits, environment
  (`XDG_*`), working folder and verdict rules are unchanged.
- `template/governance/kernel/hooks/precompact.py` and `sessionstart.py` still put the project's `src` on their own
  import path when that folder exists. That is outside this ticket's paths and is with the owner as a package.
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
with it gives two small conflicts, each resolved by keeping both sides (DEC-750, DEC-754):

| File | This change | W2-05 | Resolution |
|---|---|---|---|
| `src/gov/check/runner.py`, `_run_command` | adds `command = _judged(command)`; removes the four lines that put `<root>/src` on `PYTHONPATH` | `env = dict(os.environ)` becomes `env = git_env(root)` | `command = _judged(command)`, then `env = git_env(root)`; the four `PYTHONPATH` lines stay removed. W2-05 also drops the `os` import, which this change no longer needs beyond that line |
| `src/gov/retrieval/retrieve_check.py`, top of the module | `REPO_ROOT` replaced by `GITLEAKS_CONFIGS` | adds `from gov.util.gitenv import git_env` beside `REPO_ROOT` | keep W2-05's import and `GITLEAKS_CONFIGS`; `REPO_ROOT` stays removed |

W2-05's block that clears the environment at the start of `main` does not conflict: this change adds one line
(`project = Path.cwd()`) further down. This change imports nothing from `gov.util.gitenv`.

## 7. Owner acts and open packages

| # | Act | When |
|---|---|---|
| A1 | Regenerate the settings file from `.rulesync/hooks.jsonc` (the generated files are the owner's). Until then the live hooks keep the old lines, and the adapter-portability check is RED with one finding, `GENERATED_DIFFERS` (DEC-835 item 3) | After the merge |
| A2 | Re-run the pin commands at the merge commit, which must also hold W2-50's secrets fix (DEC-835 item 4, DEC-853 item 4) | After the merge, after A1 |
| P1 | `precompact.py` and `sessionstart.py` put the project's `src` on their own import path (§4) | Already with the owner |
| P2 | Whether `gov --version` should know its commit from an installed wheel (a build that records it) | Open |

## 8. Risks

| Risk | Effect | Mitigation |
|---|---|---|
| A pin whose console script pip wrote in the long-path form (`#!/bin/sh` and an `exec` line, used when the interpreter path is longer than 127 characters or holds a space) | The line would start the hook program with `sh`, which fails; for `preToolUse` the call is refused, not allowed | The owner's pin path (`~/.local/share/gov-os/pin-<sha>/bin/python`) is about 50 characters |
| A session whose `HOME` has no `~/.local/bin/gov` and whose `PATH` has no `gov` | Every tool call is refused with "no pinned gov" | Intended: the guard does not fail open. The message names both places looked at |
| A declared check that starts `python3` or `gov` again inside itself | That inner call would run what is first on `PATH` | None does today (`src/gov` searched) |
| `-P` takes the script's own folder off the import path of a declared `python3 <script>.py` | Such a script could not import its siblings | Every declaration today is `python3 -m …` or `gov …` |
| The merge with W2-05 | Two conflicts | §6 gives the resolution |

## 9. Rollback

Revert this ticket's merge commit. The hook lines return to `PYTHONPATH="$CLAUDE_PROJECT_DIR/src" python3 …`, the
runner to the tree's `src`, and the owner regenerates the settings file again. The pin itself is not touched by this
change; the owner's pin rollback (the link `~/.local/bin/gov` back to an editable install's `gov`) is followed by
the new hook lines without an edit.

## 10. Verification

- W2-59's acceptance tests (`tests/acceptance/W2-59`): 44 passed, from a stand-in pin built from this branch.
- W1-38's acceptance tests (the hook-source tests): 201 passed.
- Builder tests: `tests/unit/check/test_w2_59_judged_commands.py`, `tests/unit/cli/test_w2_59_version.py`,
  `tests/unit/retrieval/test_w2_59_project_root.py`; and the existing `tests/unit/validate/test_canary.py` unchanged
  and passing.
