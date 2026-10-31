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
| 24 | `src/gov/retrieval/lexical.py` | `_git`: `git -C <root> <args>` (the lexical index) | the project root, or the check's temporary clone | yes | `env=git_env(root)`. W2-87 holds the file now: unchanged in batch 2 |
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
| 61 | `src/gov/guard/reads.py` | `_git`: `git -C <root> rev-parse`, `merge-base`, `diff --name-only` (the guard's read policy) | the project root | no: it clears every `GIT_*` variable; configuration not pinned; git by name | after W2-84 merges |
| 62 | `src/gov/secrets/__init__.py` | `_partial`: `git config --list -z`; `_commits`: `git cat-file --batch-check` (which matches name a commit) | the project root | no: it clears every `GIT_*` variable, sets `GIT_CEILING_DIRECTORIES`, `GIT_NO_REPLACE_OBJECTS` and `GIT_NO_LAZY_FETCH`; configuration not pinned (it reads the person's on purpose, for a partial-clone setting) | after W2-107 merges |
| 63 | `src/gov/retrieval/measure.py` | `main`: `git -C <root> rev-parse HEAD`; `_retriever` and `_ask`: `gov --version` and `gov retrieve` (rows 57 and 24) | the project root | yes | after W2-87 merges (W2-61 too) |
| 64 | `src/gov/rebuild/**` | through rows 24, 41 and 43 to 45 (`lexical.refresh`, `store.load`, `codeintel.index`) | the project root | as those rows | after W2-76 merges; it starts no process of its own |
| 65 | `src/gov/launch/launcher.py` | the session (`Popen` of the harness), whose hooks are the rows above | the worktree of the session | yes | after W2-60a merges |
| 66 | `src/gov/release/__init__.py` | `_git`: `git -C <repo> <args>` (`rev-parse`, `status --porcelain`, `ls-tree`, `log --all`, `for-each-ref`, `show`); `_blobs`: `cat-file --batch`; `_wheel`: `archive`; `build`: `merge-base --is-ancestor` (`gov release`) | the repository being released | yes | open: W2-16's file, merged into `w2/W2-05` at `2359f6d79e3e` after batch 2's sweep; outside package I (b)'s paths, a package of this round (P-W2-05-RELEASE) |

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
- `src/gov/impact/**` (W2-37), `src/gov/lock/**` (W2-16), `src/gov/launch/gate*` and `src/gov/resources/**`
  (W2-20), and the rest of `src/gov/launch/**` (W2-56) start no process. `src/gov/release/**` (W2-16) did not when
  first swept; as merged it starts git (row 66).

**Counts:** 66 rows. 60 changed by W2-05, directly or through a changed row: rows 1 to 60. Of them, 40 changed in
batch 2: rows 2 to 8, 10 to 12, 15, 29 and 31 (pinned: reads a close reaches), 19 to 21, 32 to 42 and 46 to 58. Rows 16, 17 and 43 to 45 (W2-56's file now) and 24 and 28 (W2-87's)
were changed in the first runs and are recorded only since. 5 marked "after <W2 id> merges": rows 61 (W2-84), 62
(W2-107), 63 (W2-87), 64 (W2-76) and 65 (W2-60a). No row is open for W2-50, W2-53 or W2-03: those have merged.
Package I (b) (DEC-970) changed rows 36 and 55, and through row 36 rows 51 and 52; its review's finding R4-1
changed row 55 again (the step's tests). 1 open: row 66 (W2-16's
`gov release`, merged after batch 2), recorded in package I (b)'s round and unchanged.

The test helpers outside `src/` (`tests/**/*support*.py`) build their own environments and are not Gov OS calls.
The test runs the Gov OS starts are rows 36, 51, 52 and 55, all in `runner_env`.

## Not settled here

- **F-B and D-1** (`staged-secrets` on inherited object, alternate or common-dir variables; gitleaks with replace
  refs ignored) are Wave 3 rows W2-M375 and W2-M376 (DEC-807 item 1).
- **The settings re-sort** (KPI success 3) cannot be fixed in `lefthook.yml`. `lefthook uninstall` (2.1.15) always
  rewrites `.claude/settings.json`: in `internal/command/uninstall_ai.go`, `uninstallAIHooks` ->
  `removeAIHookEntries` -> `writeJSONFile`, with no check of the configuration or of a change. The rewrite is
  Go's `json.MarshalIndent` of a map: keys sorted, `&`, `<` and `>` escaped. DEC-783 item 1 re-baselined it:
  `install` leaves the file byte-identical; `uninstall` is the owner's act, followed by restoring it.
- **The rows marked "after <W2 id> merges"** (61 to 65) are changed by the ticket that holds each file, or by a
  later W2-05 round after it merges.
- **Row 66** (`gov release`, W2-16's, merged): its git calls inherit the caller's whole environment. They take
  `git_env(repo)` (pinned for the reads) once a round's paths hold the file (P-W2-05-RELEASE).

W2-L160 (rows 19 to 21 and 42) and W2-M161 (rows 32 to 38 and 46 to 56) are settled in this record.
