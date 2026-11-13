# AR-2: the sweep of every git call of the Gov OS source

**Ticket:** W2-05 (DAEO-0z8c). **Closes:** AR-2. **Sources:** DEC-710, DEC-711, DEC-712, DEC-777, DEC-783,
DEC-804, DEC-807; the list rows W2-M105, W2-M113, W2-M161, W2-L160. **Swept:** `src/gov/**/*.py` on `w2/W2-05` at
`134d765a40c0`, before any call was changed. **Re-swept:** at `55586fded9de` (the resume's batch 2, after
`w2/integrate` at `04bd5e11b01b`), every call that starts git or a program that starts git, `subprocess` calls
through other names included.

## Why

In a linked worktree a pre-commit hook inherits `GIT_DIR` (the worktree's git directory) and an absolute
`GIT_INDEX_FILE`. The retrieval-regression check ran `git clone`, `git add -A` and `git commit` in a temporary
clone with them, and wrote two foreign commits onto `w1/W1-42` (DEC-710, DEC-711). Every git call that inherits
the caller's environment can act on a repository other than its own the same way, or write a trace file, or
fetch behind the reader's back.

## The helper

`src/gov/util/gitenv.py` (module `gov.util.gitenv`). It has five forms.

**`git_env(root=None, *, pinned=False, base=None) -> dict`**, for a git call in the repository at `root`:

- It starts from `base` (default `os.environ`) and removes every `GIT_*` variable. This covers the location
  variables (`GIT_DIR`, `GIT_INDEX_FILE`, `GIT_WORK_TREE`, `GIT_COMMON_DIR`, `GIT_OBJECT_DIRECTORY` and the
  others), the trace variables (`GIT_TRACE*`, W2-M105) and the configuration variables (`GIT_CONFIG_*`).
- It keeps the person's own variables, which name no repository, trace, configuration or fetch:
  - the identity (`GIT_AUTHOR_NAME`, `_EMAIL`, `_DATE`, `GIT_COMMITTER_NAME`, `_EMAIL`, `_DATE`). Without it,
    `gov ci push`'s `git notes add` refused with "Author identity unknown" (W1-40's acceptance tests, 11 failed
    and 21 errors on a first draft that cleared them).
  - how a push reaches its remote (`GIT_SSH`, `GIT_SSH_COMMAND`, `GIT_SSH_VARIANT`, `GIT_ASKPASS`,
    `GIT_TERMINAL_PROMPT`).
- It sets `GIT_NO_LAZY_FETCH=1`: no call fetches a missing object in a partial clone (W2-M105).
- With `pinned=True` it also sets `GIT_CONFIG_NOSYSTEM=1` and `GIT_CONFIG_GLOBAL=/dev/null`. The system file and
  the person's own configuration (`~/.gitconfig`, `$XDG_CONFIG_HOME/git/config`) are then not read (W2-M113).
  A call that only reads is pinned. A call that commits is not, where the identity comes from that configuration.
- **P-1, accepted (DEC-804 item 3):** an inherited `GIT_INDEX_FILE` is honoured only for git calls in the project
  root. The one value kept is a `GIT_INDEX_FILE` that names a file directly in the git directory of `root`. Such
  a value is git's own for the call's repository. It is kept as an absolute path:
  - `index.lock` for `git commit -a`;
  - `next-index-*.lock` for `git commit -- <path>`;
  - the relative `.git/index` of the main tree, read from the caller's folder.

  Any other value is cleared. That includes a linked worktree's index seen from the main tree: it lies deeper,
  under `.git/worktrees/<name>/`. A `GIT_DIR` that names the git directory of `root` is the one git finds from
  `root` by itself, so clearing it changes nothing. The git directory of `root` is asked of git with every `GIT_*`
  variable cleared and the configuration pinned. This happens only when a `GIT_INDEX_FILE` was inherited. With
  no `root`, nothing is kept.

**`program_env(*, pinned=False, base=None) -> dict`**, for a program that may start git outside the project root
(P-1): `git_env`'s, with no index kept whatever `base` holds. Its git in a folder of its own acts on that folder's
repository only. Its git in the root finds the root's own index by itself (F-A, DEC-807 item 2).

**`runner_env(*, base=None)`**, a context manager (package I (b), DEC-970), for a process that runs the tests:
`program_env(pinned=True, base=base)`, with `GIT_CONFIG_GLOBAL` naming a file generated for the run instead of
`/dev/null`; `GIT_CONFIG_NOSYSTEM=1` stays.

- The file holds the person's `user.name`, `user.email` and `init.defaultBranch`, each only when set, and nothing
  else: no `trace2.*`, no `core.*`, no include, no alias, no hook path. With none set it is empty, which is what
  `/dev/null` was; no identity is invented.
- The values come from the person's global files as `base`'s `HOME` and `XDG_CONFIG_HOME` name them, in git's
  order: `$XDG_CONFIG_HOME/git/config` (or `$HOME/.config/git/config`), then `~/.gitconfig`, the later winning.
  Each is read as data, `git config --file <path> --null --get-regexp`, by git from `GIT_DIRS`, under the pinned
  environment, in the generated file's own folder with `GIT_CEILING_DIRECTORIES` above it (no repository read): no include is followed and no
  setting of the file acts (a `trace2.eventTarget` there writes nothing while it is read).
- The file is at git's global level, so a test's own `git config user.name` in its repository wins.
- It lives in a folder of this process's temporary folder (`gov-gitconfig-*`), made on entering the `with` and
  removed on leaving it: one file per run, never in the project.

Why: the pinning of batch 2 hid the person's identity and default branch from the tests too. A test that commits
in a repository of its own without naming an identity, or relies on `init.defaultBranch`, failed under `gov
close` and the nightly for no fault of the change judged (three cases of `tests/unit/containment/
test_dec_572_lift.py`).

**`foreign_index(root, *, base=None) -> str | None`** answers from the same rule: the inherited `GIT_INDEX_FILE` as
given when `git_env(root)` would not keep it, else None. The staged-secrets gate asks it and refuses on such an
index, naming it: the index being committed is never replaced by the default one (review F1, row 13).

**`git_binary(dirs=None) -> str | None`** (batch 2) is git by absolute path from the system's own folders
(`GIT_DIRS`: `/usr/bin`, `/bin`, `/usr/local/bin`, `/opt/homebrew/bin`), never the first on the inherited `PATH`
(W2-L160). None when no folder holds it; the caller then refuses (DEC-580). The guard's freeze look-up (row 42) and
the containment check (rows 19 to 21) take it.

## How a program is read against P-1

A call that starts a program other than `git -C <root> …` gets `program_env` if the program may start git outside
the project root, and stays as it is if it starts git only in the root.

| Row | Program | Where it starts git | Reading |
|---|---|---|---|
| 9 | a declared check (`sh -c`) | anywhere: a check may clone into a temporary folder (DEC-710) | `program_env()`: no index (batch 1) |
| 13 | `gitleaks git --pre-commit --staged` | only the root (`git diff --staged`) | stays: git's own index of the commit is kept |
| 30, 38 | the vendored `tk` | only the root (`git config user.name`) | stays: `git_env(root)` with `TICKETS_DIR` |
| 36, 51 | the close's test runs and probes (`_started`) | anywhere: the tests start git in folders of their own | `runner_env` from a base without any `GIT_*` variable: no index, nothing of the caller's, configuration pinned, the person's three settings only (batch 2; package I (b), DEC-970) |
| 55 | `git bisect run <step>` in the nightly's clone | the clone (another folder), and the tests the step starts | `runner_env` from a base without any `GIT_*` variable, as row 36 (package I (b), DEC-970; batch 2 had `program_env` unpinned); the step's tests get that environment as handed to the step, not what `git bisect run` adds to it (R4-1) |
| 43 to 45 | `codebase-memory-mcp` | only the root (it indexes the project) | stays; W2-56 holds the file: recorded only |

## The calls

"Inherited" says whether the call passed the caller's whole environment, `GIT_*` variables included, to git
before this ticket. "Change" says what W2-05 did. A call in a file another ticket holds is listed, marked
"after <W2 id> merges", and left unchanged (DEC-777). Rows 1 to 45 keep their numbers from the first sweep.

| # | File | Call | Folder it acts on | Inherited | Change |
|---|---|---|---|---|---|
| 1 | `src/gov/adopt/project.py` | `_run`: `git -C <root> -c core.quotePath=false <args>` (every git call of `gov adopt`) | the project being adopted | yes | `env=git_env(root)` |
| 2 | `src/gov/check/audit_validator.py` | `_git_repo_root`: `git rev-parse --show-toplevel` | the caller's folder | yes | `env=git_env(".")`. Batch 2: pinned: it only reads, and a close reaches it (W2-M161) |
| 3 | `src/gov/check/audit_validator.py` | `_commit_resolves`: `git rev-parse --verify <c>^{commit}` | the repository root | yes | `env=git_env(repo_root)`. Batch 2: pinned: it only reads, and a close reaches it (W2-M161) |
| 4 | `src/gov/check/audit_validator.py` | `_path_exists_at_commit`: `git cat-file -e <c>:<path>` | the repository root | yes | `env=git_env(repo_root)`. Batch 2: pinned: it only reads, and a close reaches it (W2-M161) |
| 5 | `src/gov/check/claims.py` | `_check_taxonomy_change`: `git log --oneline -1 -- <dims>` | the project root | yes | `env=git_env(root)`. Batch 2: pinned: it only reads, and a close reaches it (W2-M161) |
| 6 | `src/gov/check/claims.py` | `_check_taxonomy_change`: `git diff HEAD~1 -- <dims>` | the project root | yes | `env=git_env(root)`. Batch 2: pinned: it only reads, and a close reaches it (W2-M161) |
| 7 | `src/gov/check/pathmap.py` | `_git_ls_files`: `git ls-files -z` | the project root | yes | `env=git_env(root)`. Batch 2: pinned: it only reads, and a close reaches it (W2-M161) |
| 8 | `src/gov/check/runner.py` | `_head`: `git rev-parse HEAD` (also `gov ci`'s head) | the project root | yes | `env=git_env(root)`. Batch 2: pinned: it only reads, and a close reaches it (W2-M161) |
| 9 | `src/gov/check/runner.py` | `_run_command`: `sh -c <declared check>` (each declared check, which starts git itself) | the project root; the check's git may act anywhere | yes | `program_env()`: no inherited `GIT_*` variable and no index (P-1, F-A; batch 1, `8b8a3baa347a`) |
| 10 | `src/gov/check/runner.py` | `_check_skill_version`: `git diff HEAD~1 --name-only -- <vendor>` | the project root | yes | `env=git_env(root)`. Batch 2: pinned: it only reads, and a close reaches it (W2-M161) |
| 11 | `src/gov/check/runner.py` | `_check_skill_version`: `git show HEAD~1:<rel>` | the project root | yes | `env=git_env(root)`. Batch 2: pinned: it only reads, and a close reaches it (W2-M161) |
| 12 | `src/gov/checkpoint/record.py` | `_git`: `git -C <root> <args>` | the project root | yes | `env=git_env(root)`. Batch 2: pinned: it only reads, and a close reaches it (W2-M161) |
| 13 | `src/gov/ci/command.py` | `_staged_secrets`: `gitleaks git --pre-commit --staged` (gitleaks starts `git diff --staged`), twice | the project root | yes (less `GITLEAKS_CONFIG`) | `git_env(root)`, less `GITLEAKS_CONFIG`: git's own index of the commit is kept. An inherited `GIT_INDEX_FILE` that is not git's own (`foreign_index(root)`) is refused, naming it, before gitleaks starts (review F1). P-1: starts git only in the root, unchanged in batch 2 |
| 14 | `src/gov/ci/command.py` | `_git`: `git notes`, `git push` (`gov ci push`, `gov ci record`) | the project root | yes | `env=git_env(root)` |
| 15 | `src/gov/closure/__init__.py` | `closure`: `git --no-optional-locks status --porcelain` | the project root | yes | `env=git_env(root)`. Batch 2: pinned: it only reads, and a close reaches it (W2-M161) |
| 16 | `src/gov/codeintel/__init__.py` | `_checked`: `git rev-parse --show-toplevel` | the project root | yes | `env=git_env(root)`. W2-56 holds the file now: unchanged in batch 2 |
| 17 | `src/gov/codeintel/__init__.py` | `index`: `git ls-files -z --cached --others --exclude-standard` | the project root | yes | `env=git_env(root)`. W2-56 holds the file now: unchanged in batch 2 |
| 18 | `src/gov/doctor/command.py` | `_git`: `git ls-files`, `log`, `grep`, `rev-parse --show-toplevel` | the project root | yes | `env=git_env(root)` |
| 19 | `src/gov/guard/containment.py` | `_git`: `<git> --no-replace-objects -c core.commitGraph=false -C <root> <args>` (every git call of the containment check, W1-03's PostToolUse hook, and of `judge_commits`) | the project root | no: it cleared 7 location variables; trace, configuration and lazy fetch were inherited; git was the first on `PATH` | `_git_env(root)` is `git_env(root, pinned=True)` with the graft and shallow files off (W2-M113). Batch 2: git by absolute path, `git_binary()` through `_git_command`. With no git resolved, `_GitError`: the post-command check reports it as a finding and `judge_commits` raises, so the change is not passed (DEC-580). The environment is unchanged |
| 20 | `src/gov/guard/containment.py` | `_is_ancestor`: `git merge-base --is-ancestor` | the project root | as row 19 | as row 19 |
| 21 | `src/gov/guard/containment_merge.py` | `_run` -> `containment._git`: `rev-list`, `diff-tree`, `merge-base` (`read_merge`) | the repository of the merge | as row 19 | through row 19: trace variables cleared, `GIT_NO_LAZY_FETCH` set, configuration pinned (W2-M105), git by absolute path. The file starts no process of its own |
| 22 | `src/gov/pause/command.py` | `_git`: `git -C <root> <args>` (`gov pause`) | the project root | yes | `env=git_env(root)` |
| 23 | `src/gov/pause/command.py` | `_mirror_path`: `git rev-parse --git-common-dir` | the project root | yes | `env=git_env(root)` |
| 24 | `src/gov/retrieval/lexical.py` | `_git`: `git -C <root> <args>` (the lexical index: `_tracked`'s `ls-files -z` and `hash-object --stdin-paths`; W2-108's freshness key, `_tree`'s `rev-parse HEAD --git-path index` and `ls-files -z`, which every `gov check`, `gov retrieve` and `gov close` works out) | the project root, or the check's temporary clone | yes | `env=git_env(root)`. W2-87 holds the file now: unchanged in batch 2. After W2-108 merged (`d1533bf30a10`): `git_env(root, pinned=True)`: every call only reads, and a close reaches them (W2-M161). A person's `trace2.eventTarget` took 20 events from them (review R6-2) and three of the close's (W2-05's planted case). `hash-object` has no `-w`; pinned, its blob id still follows the repository's own attributes and configuration, and is the same for an ordinary project; a person's global `core.autocrlf` no longer changes it (a store built under one sees such a file stale once). An inherited index of the root's own git directory is kept |
| 25 | `src/gov/retrieval/retrieve_check.py` | `main`: `git clone -q --no-hardlinks <tier> <dest>` | a temporary folder (**another folder**) | yes: **the DEC-710 cause** | `env=git_env(None, pinned=True)` |
| 26 | `src/gov/retrieval/retrieve_check.py` | `main`: `git -C <dest> add -A` | the temporary clone (**another folder**) | yes: **the DEC-710 cause** | `env=git_env(dest, pinned=True)` |
| 27 | `src/gov/retrieval/retrieve_check.py` | `main`: `git -C <dest> commit -q --allow-empty -m adopted` | the temporary clone (**another folder**) | yes: **the DEC-710 cause** (the foreign commits) | `env=git_env(dest, pinned=True)` |
| 28 | `src/gov/retrieval/retrieve_check.py` | `main`: the git calls of `lexical.refresh`, `semantic.refresh` and `store.load` on the clone | the temporary clone (**another folder**) | yes | the check clears its own process environment with `git_env(None, pinned=True)` first. Its every git call, the store's included, inherits no `GIT_*` variable. W2-87 holds the file now: unchanged in batch 2 |
| 29 | `src/gov/status/command.py` | `_store_fault`: `git rev-parse HEAD` | the project root | yes | `env=git_env(root)`. Batch 2: pinned: it only reads, and a close reaches it (W2-M161) |
| 30 | `src/gov/tasks/tickets.py` | `create`: the vendored `tk create` (it runs `git config user.name`) | the project root | yes | `env=git_env(root)` with `TICKETS_DIR`. P-1: starts git only in the root, unchanged in batch 2 |
| 31 | `src/gov/telemetry/counter.py` | `_commits`: `git log HEAD --topo-order --reverse` | the project root | yes (with `GIT_CEILING_DIRECTORIES`) | `env=git_env(root)` with `GIT_CEILING_DIRECTORIES`. Batch 2: pinned: it only reads, and a close reaches it (W2-M161) |
| 32 | `src/gov/close/repo.py` | `git`: `git -C <root> --no-replace-objects <args>` (every git call of `gov close` through `gov.close.repo`: rows 33 and 46 to 54) | the project root | no: it cleared every `GIT_*` variable; configuration not pinned (W2-M161) | batch 2: `git_env(root, pinned=pinned)` from a base without any `GIT_*` variable, so nothing of the caller's speaks to git, the identity included (DEC-500). `pinned=True` by default: every read is pinned. The close's commits pass `pinned=False` (rows 46, 47) |
| 33 | `src/gov/close/history.py` | through row 32 (`rev-parse`, `merge-base`, `rev-list`, `merge-tree --write-tree`, `commit-tree`, `diff-tree`, `log`, `show`) | the project root | as row 32 | through row 32, pinned. `commit-tree` carries its identity explicitly (`-c user.name=gov -c user.email=gov@localhost`), so pinning changes no author; its merges are objects for a comparison |
| 34 | `src/gov/close/traceability.py` | `_read_trailers`: `git log -1 --format=%(trailers)` | the project root | yes | batch 2: `env=git_env(root, pinned=True)` |
| 35 | `src/gov/close/traceability.py` | `_commits_for_ticket`: `git log HEAD --format=%H ...` | the project root | yes | batch 2: `env=git_env(root, pinned=True)` |
| 36 | `src/gov/close/command.py` | `_started`: the ticket's acceptance tests, the parallel-runner probe and the timeout-plugin probe (the **test helper**: the tests start git) | the project root; the tests' git acts in their own temporary repositories | yes (W2-M161) | batch 2: `program_env(pinned=True)` from `env` without any `GIT_*` variable. No `GIT_*` variable of the caller reaches a test run, the location, index, trace and identity variables among them (P-1, DEC-500); `GIT_NO_LAZY_FETCH=1` is the helper's. The configuration is pinned (W2-M161): a test's git reads neither the system's nor the person's configuration. Package I (b) (DEC-970): `runner_env` instead of `program_env(pinned=True)`, so `GIT_CONFIG_GLOBAL` names the file made for the run with the person's `user.name`, `user.email` and `init.defaultBranch` only, removed when the run ends: a test that commits without naming an identity commits as the person, and nothing else of the person's configuration (trace, `core.*`, include, alias, hook path) reaches it. The close's own `PYTHONPATH`, plugin variables and check result are kept |
| 37 | `src/gov/close/command.py` | `judge_commits` (through row 19); the close's reads through row 32 (`rev-parse`, `merge-base`, `ls-tree` and the others) | the project root | as rows 19 and 32 | through rows 19 and 32; the file's one change is row 36 |
| 38 | `src/gov/close/tool.py` | `tk`: the ticket tool (it runs `git config user.name`) | the project root | yes | batch 2: `env=git_env(root)` with `TICKETS_DIR`, as row 30 |
| 39 | `src/gov/decisions/checker.py` | `_git`: `git --no-replace-objects ... -C <root> <args>` | the project root | no: it cleared every `GIT_*` variable and set `GIT_NO_LAZY_FETCH`; configuration not pinned | batch 2: `_environment(root)` is `git_env(root, pinned=True)` from a base without any `GIT_*` variable, with the graft and shallow files off. What the clearing protected is kept: no inherited variable names another repository |
| 40 | `src/gov/decisions/checker.py` | the `cat-file --batch` process of its batch reader (`_Objects.__init__`) | the project root | as row 39 | as row 39 |
| 41 | `src/gov/store/loader.py` | `_git`: `git -C <root> <args>` (the record store: `ls-tree`, `cat-file`, `log`, `rev-parse`) | the project root, or the check's temporary clone | yes | batch 2: `env=git_env(root, pinned=True)`. In the retrieval check it is also reached through row 28 |
| 42 | `src/gov/guard/decide.py` | `_mirror_path`: `<git> -C <root> rev-parse --git-common-dir` (the guard hook's freeze look-up) | the project root | yes: git by name, no limit of its own (W2-L160) | batch 1: git by absolute path from the system's folders, `git_env(None, pinned=True)`, its own limit of 15 s (DEC-783 item 2). On a time-out or with no git resolved, `FreezeLookupUnavailable`: the guard refuses, never allows. Batch 2: the resolver is the helper's `git_binary` (`_GIT_DIRS` is `GIT_DIRS`); the behaviour is unchanged |
| 43 | `src/gov/codeintel/__init__.py` | `_env`: `codebase-memory-mcp config set ui_enabled false` (the tool starts git in the project) | the project root | yes | `_env` builds on `git_env(root)` with `CBM_CACHE_DIR` and `CBM_RUNTIME_DIR` (review F2). P-1: starts git only in the root. W2-56 holds the file now: recorded only |
| 44 | `src/gov/codeintel/__init__.py` | `_tool`: `codebase-memory-mcp cli --quiet --json <tool> <args>` (`index_repository` among them) | the project root | yes | through row 43: `env=_env(root, tool)`. W2-56 holds the file now: recorded only |
| 45 | `src/gov/codeintel/__init__.py` | `_Session.tool`: the `codebase-memory-mcp` server (`Popen`) | the project root | yes | through row 43: `env=_env(root, tool)`. W2-56 holds the file now: recorded only |
| 46 | `src/gov/close/batch.py` | `_commit`: `git config user.email`, `git add --all`, `git commit` (the batch's run record and closes); its reads (`rev-parse`, `rev-list`) through row 32 | the project root | as row 32 | batch 2: the three commit calls pass `pinned=False`: the commit carries the configured identity (the person's `~/.gitconfig`), else `gov@localhost`, as before. The reads are pinned |
| 47 | `src/gov/close/tool.py` | `_commit_alone`: `git config user.email`, `git add`, `git commit` (the repair ticket) | the project root | as row 32 | batch 2: `pinned=False`, as row 46 |
| 48 | `src/gov/close/select.py` | through row 32: `merge-base --is-ancestor`, `rev-parse`, `rev-list --count`, `diff`, `ls-tree`, `show` | the project root | as row 32 | through row 32, pinned |
| 49 | `src/gov/close/fingerprint.py` | through row 32: `ls-tree -r --full-tree`, `cat-file blob` | the project root | as row 32 | through row 32, pinned |
| 50 | `src/gov/close/state.py`, `src/gov/close/ratchet.py` | through row 32: `ls-tree`, `cat-file blob`, `merge-base --is-ancestor`, `show`, `rev-list`, `log` | the project root | as row 32 | through row 32, pinned |
| 51 | `src/gov/close/gates.py` | the collection run (`pytest --collect-only`) through `_started`; `ls-tree`, `log -1`, `ls-files --others` through row 32 | the project root; the collected tests may start git anywhere | as rows 32 and 36 | through rows 32 (pinned) and 36 (`runner_env`) |
| 52 | `src/gov/close/nightly.py` | the run alone of a red (`_alone`) through `_started` | the nightly's clone (**another folder**) | yes (as row 36) | through row 36: `runner_env` |
| 53 | `src/gov/close/nightly.py` | through row 32: `rev-parse --git-common-dir`, `rev-parse --verify`, `rev-parse <head>^{tree}`, `rev-parse refs/bisect/bad` | the project root, or the nightly's clone | as row 32 | through row 32, pinned |
| 54 | `src/gov/close/nightly.py` | `night`: `git worktree add --detach --force <clone> <head>` through row 32 | the project root (it writes the clone) | as row 32 | batch 2: `pinned=False` (a write, not a read). Arguments, paths and order as W2-77 left them |
| 55 | `src/gov/close/nightly.py` | `_bisect`: `git bisect start`, `git bisect run <step>` (the step starts pytest, whose tests start git), `git bisect reset` | the nightly's clone (**another folder**) | no: it cleared every `GIT_*` variable of the run's environment | batch 2: `program_env` from the run's environment without any `GIT_*` variable, as it cleared them; `GIT_NO_LAZY_FETCH=1` added; not pinned. Package I (b) (DEC-970): `runner_env` from the same base, as row 36, for `bisect start`, `run` and `reset` alike: each commit is judged in the environment of the run that found the red, the file made for the run included and removed when the bisect ends. Review finding R4-1 (DEC-970): `git bisect run` itself exports `GIT_DIR` (the clone's git directory), `GIT_EXEC_PATH` and `GIT_PREFIX` to the step and puts its own folder first on `PATH`, so a test's `git init` in a folder of its own re-initialised the clone and its commits and branches reached the project (`main` moved, a foreign branch, a first bad commit outside the project's history). The step's tests now get that environment handed to the step whole (`GOV_NIGHTLY_STEP_ENV`, given to `bisect run` only), never the step's own: no `GIT_*` variable but `GIT_CONFIG_GLOBAL`, `GIT_CONFIG_NOSYSTEM` and `GIT_NO_LAZY_FETCH`, exactly what `_alone` gives the same test. A step that cannot read it exits 125 (untestable), never good (DEC-580). `bisect start`, `run` and `reset` keep `runner_env`'s. Arguments, paths and order unchanged |
| 56 | `src/gov/close/nightly.py` | `_remove_clone`: `git worktree remove --force <clone>` (never a prune, DEC-939 item 5) | the project root | yes | batch 2: `env=git_env(root)` (a write: unpinned) |
| 57 | `src/gov/cli/main.py` | `_version`: `git -C <tree> rev-parse --show-toplevel HEAD` (`gov --version`) | the source tree of the running code | yes | batch 2: `env=git_env(tree, pinned=True)` |
| 58 | `src/gov/check/citations.py` | through rows 39 and 40 (`checker._git`, `checker._Objects`) | the project root | as row 39 | through rows 39 and 40 |
| 59 | `src/gov/adopt/stages.py`, `src/gov/adopt/legacy.py` | through row 1 (`project.git`) | the project being adopted | as row 1 | through row 1 |
| 60 | `src/gov/tasks/bridge.py`, `src/gov/readiness/checker.py` | through row 30 (`tickets.create`) | the project root | as row 30 | through row 30 |
| 61 | `src/gov/guard/reads.py` | `_git` (line 194): `git -C <folder> <args>` (the guard's read policy), for: `_changed`'s `rev-parse --verify --quiet w2/integrate^{commit}`, `merge-base`, `diff --name-only` (lines 208, 211, 214); `_worktrees`' `worktree list --porcelain -z` (line 256); `base_version`'s `rev-parse <rev>:<rel> <base>:<rel>` (line 1698); and `ask` (line 1664, git at line 1671): git with words taken from the judged command (its `--git-dir`/`--work-tree` options, `addr`, lines 1491 to 1498) before a fixed read-only question (`rev-parse --end-of-options <rev>^{commit}`, the `log`/`diff` of names filtered by the hidden globs, `ls-tree -r --full-tree --name-only`, `ls-files --cached`; lines 1637, 1639, 1653, 1658, from `patched` and `stored`) | the project root; for `_worktrees` also a run clone's common git directory named by its marker (`_clone_trees`, line 281); for `ask` the judged command's folder (after its own `-C`) and the repository its words address | no: it clears every `GIT_*` variable; configuration not pinned; git by name | open: W2-84 has merged, and `_git` (line 194), which every call of the row goes through, still builds its own environment (every `GIT_*` variable cleared, no `GIT_NO_LAZY_FETCH`), unpinned, git by name on the inherited `PATH`. No decision exempts it. Left unchanged as the guard's own policy file, outside this ticket's paths: open for the CTO |
| 62 | `src/gov/secrets/__init__.py` | `_partial`: `git config --list -z`; `_commits`: `git cat-file --batch-check` (which matches name a commit) | the project root | no: it clears every `GIT_*` variable, sets `GIT_CEILING_DIRECTORIES`, `GIT_NO_REPLACE_OBJECTS` and `GIT_NO_LAZY_FETCH`; configuration not pinned (it reads the person's on purpose, for a partial-clone setting) | after W2-107 merges |
| 63 | `src/gov/retrieval/measure.py` | `main`: `git -C <root> rev-parse HEAD`; `_retriever` and `_ask`: `gov --version` and `gov retrieve` (rows 57 and 24) | the project root | yes | after W2-87 merges (W2-61 too) |
| 64 | `src/gov/rebuild/**` | through rows 24, 41 and 43 to 45 (`lexical.refresh`, `store.load`, `codeintel.index`) | the project root | as those rows | after W2-76 merges; it started no process of its own when swept. As merged, `command.py` and `integration.py` start git themselves: rows 68 and 69 |
| 65 | `src/gov/launch/launcher.py` | the session (`Popen` of the harness), whose hooks are the rows above | the worktree of the session | yes | after W2-60a merges |
| 66 | `src/gov/release/__init__.py` | `_git`: `git -C <repo> <args>` (`rev-parse`, `status --porcelain`, `ls-tree`, `log --all`, `for-each-ref`, `show`); `_blobs`: `cat-file --batch`; `_wheel`: `archive`; `build`: `merge-base --is-ancestor` (`gov release`) | the repository being released | yes | open: W2-16's file, merged into `w2/W2-05` at `2359f6d79e3e` after batch 2's sweep; outside package I (b)'s paths, a package of this round (P-W2-05-RELEASE) |
| 67 | `src/gov/links/command.py` | `_toplevel`: `git -C <root> rev-parse --show-toplevel` (`gov links`; line 53); `_commit`: `loader._git(root, "rev-parse", "--verify", "--quiet", <rev>^{commit})` (line 64) through row 41 | the project root | no: new since the sweep, written with the helper | scrubbed: `env=git_env(root, pinned=True)` (line 54); `_commit` through row 41, `git_env(root, pinned=True)` (`src/gov/store/loader.py` line 114). Both only read, both pinned; nothing to change. Recorded only |
| 68 | `src/gov/rebuild/command.py` | `_commit_of`: `<git> -C <where> <args>` (`rev-parse --verify`, `rev-list --count`: `gov rebuild --seed`'s relation of the base's head to the tree's, `_behind`, lines 118 to 124; call at lines 85 to 86) | the project root, or the seed's base tree | no: new since the sweep, written with the helper | scrubbed: `env=git_env(where)` (line 86), git by `git_binary()` with `git` as the fall-back (line 85). Reads only, left unpinned; a close does not reach it (it runs from `gov rebuild`), so no W2-M161 reason to pin. Nothing to change. Recorded only |
| 69 | `src/gov/rebuild/integration.py` | `_git`: `<git> -C <where> <args>` (`gov rebuild --integration`; lines 52 to 60): `worktree add --force --detach` (lines 139, 152) and `checkout -q --force --detach` (line 147) write the store's half; `rev-parse --git-common-dir`, `rev-parse --verify -q` (lines 64, 71, 247) read | the project root, and the two halves (`<link>-a`, `<link>-b`: **other worktrees** of the repository) | no: new since the sweep, written with the helper | scrubbed: `env=git_env(where)` (line 56), git by `git_binary()` with `git` as the fall-back (line 55). Unpinned for reads and writes alike: the writes are right so (as row 56); the reads only read, and no close reaches them (`gov rebuild --integration` is the merge queue's and a hook's). Nothing to change. Recorded only |
| 70 | `src/gov/util/gitrun.py` | `git`: `git -C <root> --no-replace-objects <args>` (lines 22 to 45): the runner moved whole from `gov.close.repo` (W2-150 S6); `gov.close.repo.git` and `gov.store.loader._commit_git` are this function | the project root | no: it clears every `GIT_*` variable of the base (lines 32 to 33) | scrubbed: `env=git_env(root, pinned=pinned, base=<os.environ without any GIT_* variable>)` (lines 32 to 33), `pinned=True` by default. This is row 32's code at its new place: rows 32 to 38, 46 to 50 and 53 to 54 reach git through it; the row 32 text holds. Recorded only |
| 71 | `src/gov/util/role_paths.py` | `main_tree` (line 119, `rev-parse --path-format=absolute --git-common-dir`), `linked_tests` (line 178, `rev-parse`, `log --all`, `rev-list`), `changed` (line 256, `merge-base`, `diff --name-only`, `ls-files --others`), `engineer_side` (line 275, `merge-base`, `rev-parse`, `log`); the file moved whole from `gov.guard.role_paths` (W2-150), which is this module (`gov.guard.role_paths` re-exports it); `gov retrieve`'s role filter and `gov context`'s supplementary block reach it. The guard's read hook does not: `.claude/hooks/role_reads.py` imports `gov.guard.reads` alone (lines 152, 182, 846: `_read_text`, `_Part`, `_ticket`), never this module, and runs its own copies of `linked_tests`, `changed` and `engineer_side` (git at lines 243, 337, 378), each in an environment of its own (lines 240, 334, 375: every `GIT_*` variable cleared, no `GIT_NO_LAZY_FETCH`), unpinned, git by name on `PATH`. The hook and the retrieve filter so ask git the same three questions in different environments (`changed`'s `ls-files --others` answer can differ as measured in the last cell); the hook is outside this ticket's paths, open with row 61's question | the project root, the main tree, or the searched tree | no: all four go through `_git` (lines 56 to 65), `env=git_env(<the folder given to -C>, pinned=True)`: no inherited location, index, trace or configuration variable, `GIT_NO_LAZY_FETCH=1`, the system's and the person's configuration unread. Before this round its own `_git_env()` cleared every `GIT_*` variable but set none of that | scrubbed (round r7): `_git_env` removed; each call (`main_tree` line 122, `linked_tests` line 184, `changed` line 262, `engineer_side` line 279) takes `git_env(<its -C folder>, pinned=True)` and starts git by `git_binary()`. A `None` from `git_binary()` raises `OSError`, the file's "git cannot say" route; never a git from `PATH`. `main_tree` then gives the folder it was given (line 127). `linked_tests` gives None, and only the ticket's own `tests/acceptance/<WBS>/` is judged (`Linked.names_rel`, line 350, names nothing outside it). `changed` and `engineer_side` give None, and nothing in that tree is withheld for the ticket's paths (`Denied.names`, line 334, is false on None): let through by design, as `changed`'s docstring says. The guard's containment check calls none of the four. `changed`'s `ls-files --others --exclude-standard` is pinned too, measured (git 2.43.0, a HOME of the test's own): with `core.excludesFile` named in `~/.gitconfig`, unpinned lists `b.xdg c.txt`, pinned `a.secret c.txt`; the ignore file the person names is unread, so an untracked file it alone hides is now counted as changed (withheld from the designer, never handed out: the strict side), and git's default `$XDG_CONFIG_HOME/git/ignore` (or `~/.config/git/ignore`) is read in its place, as it is with no `core.excludesFile` (so `b.xdg`, which that default file alone hides, drops out: the one way the answer can shrink, and only for a person who has both files); the repository's `.gitignore` and `info/exclude` apply as before. Unit cases: `tests/unit/gitenv/test_role_paths_env.py` |
| 72 | `src/gov/memaudit/common.py` | `git` (lines 39 to 44) and `git_code` (lines 47 to 49): `git -C <repo> <args>` (W2-170's memory audit). Its own: `toplevel`'s `rev-parse --show-toplevel` (line 54), `resolve_commit`'s `rev-parse --verify --quiet <rev>^{commit}` (line 65), `blob_at`'s `cat-file -e`, `cat-file -t` and `cat-file blob` of `<commit>:<path>` (lines 75, 77, 79). Its callers in `src/gov/memaudit/` reach git only through it: `preflight.py` (`ls-tree -r --name-only -z <commit>` line 169, `diff --name-only --no-renames -z <last> <commit>` line 179, `grep -l -F -z -e <name> <commit> --` line 267; `blob_at` lines 170, 209, 242; `toplevel` line 302; `resolve_commit` line 312) and `declare.py` (`blob_at` line 153, `toplevel` line 223, `resolve_commit` line 233); `layout.py`, `drops.py`, `ledger.py` and `__main__.py` import other names from it and start no git | the repository given (`-C repo`), else the caller's folder's top level | no: new since the sweep; `_env()` (lines 32 to 36) clears every `GIT_*` variable itself | open: its own filter, not the helper. `_env()` clears every `GIT_*` variable and sets `GIT_OPTIONAL_LOCKS=0` and `LC_ALL=C`; it sets no `GIT_NO_LAZY_FETCH`, does not pin the configuration, and starts `git` by name on the inherited `PATH` (no `git_binary()`). Every call only reads. Outside this round's change: W2-170's file, merged into `w2/W2-05` after round r7 (at `1f2a38a71`); no code changed there: open for the CTO |
| 73 | `src/gov/plan/overlap.py` | `_ls_files`: `<git> -C <root> ls-files -z` (lines 130 to 142, call at lines 136 to 137), reached from `Tracked.files` (line 115) when `gov plan` names the file of an overlap (`Tracked.witness`; `src/gov/plan/derive.py` line 98) | the project root | no: new since the sweep (W2-136), written with the helper | scrubbed: `env=git_env(root)` (line 137), unpinned; git by `git_binary()` (line 132); with no git resolved, or no `.git`, or git failing, no tracked file is listed and the overlap is named by its patterns (lines 133 to 141), never a git from `PATH`. Reads only; no close reaches it, so no W2-M161 reason to pin. Nothing to change. Recorded only |
| 74 | `src/gov/context/context_check.py` | `stale_store` (line 41): `loader._git(root, "rev-parse", "--verify", "HEAD^{commit}")` (line 51) through row 41; called by the context-reproducibility check's `main` (line 84) | the project root | as row 41 | through row 41: `git_env(root, pinned=True)`. The file starts no git of its own. Recorded only |
| 75 | `src/gov/accept/runner.py` | `_run` (line 511): `gov accept`'s pytest run of a ticket's acceptance cases (`subprocess.Popen`, lines 555 to 556; the **test helper**: the tests start git) | the project root; the tests' git acts in their own temporary repositories | yes: its environment (lines 539 to 543) is the caller's less every `PYTEST_*` and `PYTHON*` variable, with `PYTHONPATH`, `PYTHONDONTWRITEBYTECODE`, `TMPDIR` and the opt-in variable set; no `GIT_*` variable is cleared | open: W2-96's file; not changed here. Not ordinary work: `gov accept` is not started from a git hook here (`lefthook.yml` runs only `gov ci`), and `tests/conftest.py` strips git's repository-local variables in every test process (below), so an inherited location or index variable does not reach a test's own git; trace and configuration variables would. Open for the CTO |
| 76 | `src/gov/resources/slots.py` | `run` (line 311): the resource gate's heavy job, `gov resources --slot KIND -- CMD...` (`subprocess.Popen` of the given command, lines 375 to 376; a test run or rebuild that starts git) | the folder of the caller; the job's git acts wherever the job puts it | yes: `env = dict(os.environ ...)` (line 332), the caller's whole environment, with the thread budget and slot added by `job_env` (lines 82 to 88); no `GIT_*` variable is cleared | open: W2-20's file; not changed here. Not ordinary work, as row 75: it is not started from a git hook here (`lefthook.yml` runs only `gov ci`), and a pytest job's test processes strip the repository-local variables through `tests/conftest.py`. Open for the CTO |

Files that name git or start a program and start no git:

- `src/gov/guard/protected.py` reads `git diff` and `git status` in a Bash command it judges, and starts nothing.
- `src/gov/secrets/__init__.py` (W2-107's) starts `gitleaks stdin`, which starts no git; its git calls are row 62.
- `src/gov/doctor/command.py` starts `codebase-memory-mcp`, `gitleaks`, `lefthook` and `rulesync` only to ask their
  versions (`_probe`); the code index's starts of the tool are rows 43 to 45.
- `src/gov/adapters/portability.py` starts `rulesync generate` in an empty temporary folder and `rulesync
  --version`. Measured in batch 2: `rulesync generate` over this repository's sources started no git through `PATH`
  (44 files compared, no call to a logging `git` placed first on `PATH`). `src/gov/adopt/legacy.py` starts
  `rulesync import`, the same program.
- `src/gov/telemetry/counter.py` starts `ccusage`, which reads the harness's logs.
- `src/gov/retrieval/ollama.py` starts `ollama serve` and `src/gov/retrieval/rerank.py` its Python worker
  (W2-87's): neither starts git.
- `src/gov/impact/**` (W2-37), `src/gov/lock/**` (W2-16), `src/gov/launch/gate*` (W2-20) and the rest of
  `src/gov/launch/**` (W2-56) start no process. `src/gov/release/**` (W2-16) did not when first swept; as merged it
  starts git (row 66). `src/gov/resources/**` (W2-20) did not when first swept; since W2-20 merged,
  `src/gov/resources/slots.py` starts the heavy job it is given (row 76).

**Counts:** 76 rows (rows 67 to 71 added at `f2c228681`, rows 72 to 76 in round r8, after the files they name were
merged: see below). 61 changed by W2-05, directly or through a changed row: rows 1 to 60 and 71 (round r7). Of rows 1 to 60, 40 changed in
batch 2: rows 2 to 8, 10 to 12, 15, 29 and 31 (pinned: reads a close reaches), 19 to 21, 32 to 42 and 46 to 58. Rows 16, 17 and 43 to 45 (W2-56's file now) and 24 and 28 (W2-87's)
were changed in the first runs and are recorded only since. 4 marked "after <W2 id> merges": rows 62
(W2-107), 63 (W2-87), 64 (W2-76) and 65 (W2-60a). Row 61 (W2-84's, merged) is open, below. No row is open for W2-50,
W2-53 or W2-03: those have merged.
Package I (b) (DEC-970) changed rows 36 and 55, and through row 36 rows 51 and 52; its review's finding R4-1
changed row 55 again (the step's tests). The round after W2-108's merge changed row 24 again (pinned, W2-M161,
R6-2). 5 open: row 66 (W2-16's
`gov release`, merged after batch 2), recorded in package I (b)'s round and unchanged; row 61 (the guard's
`src/gov/guard/reads.py`, W2-84's, merged: its `_git` builds its own environment, unpinned, git by name; open for the
CTO); row 72 (W2-170's `src/gov/memaudit/common.py`, merged after round r7: its own filter, not the helper); and rows
75 and 76 (W2-96's `gov accept` runner and W2-20's heavy-job runner: each passes the caller's `GIT_*` variables to
what it starts). Rows 67 to 70, 73 and 74 are files that started git after the sweep and were written with the helper
(`git_env`, or `gitrun.git` or `loader._git` through it): recorded only, no change needed. Row 71
(`src/gov/util/role_paths.py`) was changed in round r7: its four calls take `git_env(<folder>, pinned=True)` and
`git_binary()`.

The test helpers outside `src/` (`tests/**/*support*.py`) build their own environments and are not Gov OS calls.
`tests/conftest.py` strips git's repository-local variables from `os.environ` at import in every test process
(`drop_git_local_env`, D-10, DEC-1074 (8)): its one git call, `git rev-parse --local-env-vars` from `/`, asks git for
the names, joined with a fixed list (git 2.43's 15) used alone when git cannot answer, and every
`GIT_CONFIG_KEY_<n>`/`VALUE_<n>`. It does not use the helper: the conftest must load without `gov`; `git_env` and
`program_env` would also drop `runner_env`'s generated `GIT_CONFIG_GLOBAL` (and `GIT_CONFIG_NOSYSTEM`), which a run
the Gov OS starts must keep; and it asks git which names are repository-local rather than clearing every `GIT_*`.
The test runs the Gov OS starts for `gov close` and the nightly are rows 36, 51, 52 and 55, all in `runner_env`;
`gov accept`'s run (row 75) and a heavy job of the resource gate (row 76) take the caller's environment, open.

## Not settled here

- **F-B and D-1** (`staged-secrets` on inherited object, alternate or common-dir variables; gitleaks with replace
  refs ignored) are Wave 3 rows W2-M375 and W2-M376 (DEC-807 item 1).
- **The settings re-sort** (KPI success 3) cannot be fixed in `lefthook.yml`. `lefthook uninstall` (2.1.15) always
  rewrites `.claude/settings.json`: in `internal/command/uninstall_ai.go`, `uninstallAIHooks` ->
  `removeAIHookEntries` -> `writeJSONFile`, with no check of the configuration or of a change. The rewrite is
  Go's `json.MarshalIndent` of a map: keys sorted, `&`, `<` and `>` escaped. DEC-783 item 1 re-baselined it:
  `install` leaves the file byte-identical; `uninstall` is the owner's act, followed by restoring it.
- **The rows marked "after <W2 id> merges"** (62 to 65) are changed by the ticket that holds each file, or by a
  later W2-05 round after it merges.
- **Row 61** (`src/gov/guard/reads.py`, the guard's read policy; W2-84 merged): `_git` still clears every `GIT_*`
  variable itself, sets no `GIT_NO_LAZY_FETCH`, reads the person's configuration and starts git by name. No decision
  exempts it; no code was changed there. It is left as the guard's own policy file, open for the CTO.
- **Row 66** (`gov release`, W2-16's, merged): its git calls inherit the caller's whole environment. They take
  `git_env(repo)` (pinned for the reads) once a round's paths hold the file (P-W2-05-RELEASE).

- **Row 72** (`src/gov/memaudit/common.py`, W2-170's memory audit, merged after round r7): `_env()` clears every
  `GIT_*` variable itself and sets `GIT_OPTIONAL_LOCKS=0` and `LC_ALL=C`, but sets no `GIT_NO_LAZY_FETCH`, reads the
  person's configuration and starts git by name. No decision exempts it; no code was changed there. Outside this
  round's change: open for the CTO.
- **Rows 75 and 76** (`gov accept`'s runner, W2-96's; the resource gate's job runner, W2-20's): each starts its run
  with the caller's `GIT_*` variables. Neither is started from a git hook here (`lefthook.yml` runs only `gov ci`) and
  `tests/conftest.py` strips the repository-local names in every test process, so this is not ordinary work; no code
  was changed there. Open for the CTO.

- **Row 71** (`src/gov/util/role_paths.py`, W2-150's move of the guard's file) is settled in round r7: its four
  calls take `git_env(<folder>, pinned=True)` and `git_binary()`, and a missing system git is "git cannot say"
  (`changed`'s `ls-files` pinned too, its measured change in the row). The guard's read hook
  (`.claude/hooks/role_reads.py`) does not use it: its own copies of three of the calls clear every `GIT_*` variable,
  unpinned, git by name, open with row 61's question.

W2-L160 (rows 19 to 21 and 42) and W2-M161 (rows 32 to 38 and 46 to 56) are settled in this record.
