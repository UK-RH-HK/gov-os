# AR-2: the sweep of every git call of the Gov OS source

**Ticket:** W2-05 (DAEO-0z8c). **Closes:** AR-2. **Sources:** DEC-710, DEC-711, DEC-712; the list rows W2-M105,
W2-M113, W2-M161, W2-L160. **Swept:** `src/gov/**/*.py` on `w2/W2-05` at `134d765a`, before any call was changed.

## Why

In a linked worktree a pre-commit hook inherits `GIT_DIR` (the worktree's git directory) and an absolute
`GIT_INDEX_FILE`. The retrieval-regression check ran `git clone`, `git add -A` and `git commit` in a temporary
clone with them, and wrote two foreign commits onto `w1/W1-42` (DEC-710, DEC-711). Every git call that inherits
the caller's environment can act on a repository other than its own the same way, or write a trace file, or
fetch behind the reader's back.

## The helper

`src/gov/util/gitenv.py`, `git_env(root=None, *, pinned=False, base=None) -> dict` (module `gov.util.gitenv`):

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
- **The one value kept** (the acceptance tests' reading P-1) is a `GIT_INDEX_FILE` that names a file directly in
  the git directory of `root`. Such a value is git's own for the call's repository. It is kept as an absolute path:
  - `index.lock` for `git commit -a`;
  - `next-index-*.lock` for `git commit -- <path>`;
  - the relative `.git/index` of the main tree, read from the caller's folder.

  Any other value is cleared. That includes a linked worktree's index seen from the main tree: it lies deeper,
  under `.git/worktrees/<name>/`. A `GIT_DIR` that names the git directory of `root` is the one git finds from `root`
  by itself, so clearing it changes nothing. The git directory of `root` is asked of git with every `GIT_*`
  variable cleared and the configuration pinned. This happens only when a `GIT_INDEX_FILE` was inherited. With
  no `root`, nothing is kept.

## The calls

"Inherited" says whether the call passed the caller's whole environment, `GIT_*` variables included, to git
before this ticket. "Change" says what W2-05 did. A call in a file of another unmerged ticket is listed, marked
"after <W2 id> merges", and left unchanged in this run (DEC-777).

| # | File | Call | Folder it acts on | Inherited | Change |
|---|---|---|---|---|---|
| 1 | `src/gov/adopt/project.py` | `_run`: `git -C <root> -c core.quotePath=false <args>` (every git call of `gov adopt`) | the project being adopted | yes | `env=git_env(root)` |
| 2 | `src/gov/check/audit_validator.py` | `_git_repo_root`: `git rev-parse --show-toplevel` | the caller's folder | yes | `env=git_env(".")` |
| 3 | `src/gov/check/audit_validator.py` | `_commit_resolves`: `git rev-parse --verify <c>^{commit}` | the repository root | yes | `env=git_env(repo_root)` |
| 4 | `src/gov/check/audit_validator.py` | `_path_exists_at_commit`: `git cat-file -e <c>:<path>` | the repository root | yes | `env=git_env(repo_root)` |
| 5 | `src/gov/check/claims.py` | `_check_taxonomy_change`: `git log --oneline -1 -- <dims>` | the project root | yes | `env=git_env(root)` |
| 6 | `src/gov/check/claims.py` | `_check_taxonomy_change`: `git diff HEAD~1 -- <dims>` | the project root | yes | `env=git_env(root)` |
| 7 | `src/gov/check/pathmap.py` | `_git_ls_files`: `git ls-files -z` | the project root | yes | `env=git_env(root)` |
| 8 | `src/gov/check/runner.py` | `_head`: `git rev-parse HEAD` (also `gov ci`'s head) | the project root | yes | `env=git_env(root)` |
| 9 | `src/gov/check/runner.py` | `_run_command`: `sh -c <declared check>` (each declared check, which starts git itself) | the project root | yes | the check's environment is `git_env(root, base=...)` |
| 10 | `src/gov/check/runner.py` | `_check_skill_version`: `git diff HEAD~1 --name-only -- <vendor>` | the project root | yes | `env=git_env(root)` |
| 11 | `src/gov/check/runner.py` | `_check_skill_version`: `git show HEAD~1:<rel>` | the project root | yes | `env=git_env(root)` |
| 12 | `src/gov/checkpoint/record.py` | `_git`: `git -C <root> <args>` | the project root | yes | `env=git_env(root)` |
| 13 | `src/gov/ci/command.py` | `_staged_secrets`: `gitleaks git --pre-commit --staged` (gitleaks starts `git diff --staged`), twice | the project root | yes (less `GITLEAKS_CONFIG`) | `git_env(root)`, less `GITLEAKS_CONFIG`: a planted index is cleared, git's own index of the commit is kept |
| 14 | `src/gov/ci/command.py` | `_git`: `git notes`, `git push` (`gov ci push`, `gov ci record`) | the project root | yes | `env=git_env(root)` |
| 15 | `src/gov/closure/__init__.py` | `closure`: `git --no-optional-locks status --porcelain` | the project root | yes | `env=git_env(root)` |
| 16 | `src/gov/codeintel/__init__.py` | `_checked`: `git rev-parse --show-toplevel` | the project root | yes | `env=git_env(root)` |
| 17 | `src/gov/codeintel/__init__.py` | `index`: `git ls-files -z --cached --others --exclude-standard` | the project root | yes | `env=git_env(root)` |
| 18 | `src/gov/doctor/command.py` | `_git`: `git ls-files`, `log`, `grep`, `rev-parse --show-toplevel` | the project root | yes | `env=git_env(root)` |
| 19 | `src/gov/guard/containment.py` | `_git`: `git --no-replace-objects -c core.commitGraph=false -C <root> <args>` (every git call of the containment check, W1-03's PostToolUse hook, and of `judge_commits`) | the project root | no: it cleared 7 location variables; trace, configuration and lazy fetch were inherited | `_git_env(root)` is `git_env(root, pinned=True)` with the graft and shallow files off (W2-M113) |
| 20 | `src/gov/guard/containment.py` | `_is_ancestor`: `git merge-base --is-ancestor` | the project root | as row 19 | as row 19 |
| 21 | `src/gov/guard/containment_merge.py` | `_run` -> `containment._git`: `rev-list`, `diff-tree`, `merge-base` (`read_merge`) | the repository of the merge | as row 19 | through row 19: trace variables cleared, `GIT_NO_LAZY_FETCH` set, configuration pinned (W2-M105) |
| 22 | `src/gov/pause/command.py` | `_git`: `git -C <root> <args>` (`gov pause`) | the project root | yes | `env=git_env(root)` |
| 23 | `src/gov/pause/command.py` | `_mirror_path`: `git rev-parse --git-common-dir` | the project root | yes | `env=git_env(root)` |
| 24 | `src/gov/retrieval/lexical.py` | `_git`: `git -C <root> <args>` (the lexical index) | the project root, or the check's temporary clone | yes | `env=git_env(root)` |
| 25 | `src/gov/retrieval/retrieve_check.py` | `main`: `git clone -q --no-hardlinks <tier> <dest>` | a temporary folder (**another folder**) | yes: **the DEC-710 cause** | `env=git_env(None, pinned=True)` |
| 26 | `src/gov/retrieval/retrieve_check.py` | `main`: `git -C <dest> add -A` | the temporary clone (**another folder**) | yes: **the DEC-710 cause** | `env=git_env(dest, pinned=True)` |
| 27 | `src/gov/retrieval/retrieve_check.py` | `main`: `git -C <dest> commit -q --allow-empty -m adopted` | the temporary clone (**another folder**) | yes: **the DEC-710 cause** (the foreign commits) | `env=git_env(dest, pinned=True)` |
| 28 | `src/gov/retrieval/retrieve_check.py` | `main`: the git calls of `lexical.refresh`, `semantic.refresh` and `store.load` on the clone | the temporary clone (**another folder**) | yes | the check clears its own process environment with `git_env(None, pinned=True)` first. Its every git call, the store's included, inherits no `GIT_*` variable. |
| 29 | `src/gov/status/command.py` | `_store_fault`: `git rev-parse HEAD` | the project root | yes | `env=git_env(root)` |
| 30 | `src/gov/tasks/tickets.py` | `create`: the vendored `tk create` (it runs `git config user.name`) | the project root | yes | `env=git_env(root)` with `TICKETS_DIR` |
| 31 | `src/gov/telemetry/counter.py` | `_commits`: `git log HEAD --topo-order --reverse` | the project root | yes (with `GIT_CEILING_DIRECTORIES`) | `env=git_env(root)` with `GIT_CEILING_DIRECTORIES` |
| 32 | `src/gov/close/repo.py` | `git`: `git -C <root> --no-replace-objects <args>` (every git call of `gov close` through `gov.close.repo`, `gov.close.history` included) | the project root | no: it cleared every `GIT_*` variable; configuration not pinned (W2-M161) | after W2-53 merges |
| 33 | `src/gov/close/history.py` | through `gov.close.repo.git` (`rev-parse`, `merge-base`, `commit-tree`) | the project root | as row 32 | after W2-53 merges |
| 34 | `src/gov/close/traceability.py` | `_read_trailers`: `git log -1 --format=%(trailers)` | the project root | yes | after W2-53 merges |
| 35 | `src/gov/close/traceability.py` | `_commits_for_ticket`: `git log HEAD --format=%H ...` | the project root | yes | after W2-53 merges |
| 36 | `src/gov/close/command.py` | `_started`: the ticket's acceptance tests and the parallel-runner probe (the **test helper**: the tests start git) | the project root | yes (W2-M161) | after W2-53 merges |
| 37 | `src/gov/close/command.py` | `judge_commits` (through row 19) | the project root | as row 19 | changed through row 19; the file itself is unchanged |
| 38 | `src/gov/close/tool.py` | `tk`: the ticket tool (it runs `git config user.name`) | the project root | yes | after W2-53 merges |
| 39 | `src/gov/decisions/checker.py` | `_git`: `git --no-replace-objects ... -C <root> <args>` | the project root | no: it cleared every `GIT_*` variable and set `GIT_NO_LAZY_FETCH`; configuration not pinned | after W2-03 merges |
| 40 | `src/gov/decisions/checker.py` | the `cat-file --batch` process of its batch reader (`__init__`) | the project root | as row 39 | after W2-03 merges |
| 41 | `src/gov/store/loader.py` | `_git`: `git -C <root> <args>` (the record store) | the project root, or the check's temporary clone | yes | after W2-03 merges. In the retrieval check it is reached through row 28. |
| 42 | `src/gov/guard/decide.py` | `_mirror_path`: `git -C <root> rev-parse --git-common-dir` (the guard hook's freeze look-up), by name, with no limit of its own (W2-L160) | the project root | yes | after W2-50 merges |

Files that name git and start none: `src/gov/guard/protected.py` reads `git diff` and `git status` in a Bash
command it judges, and starts nothing. `src/gov/secrets/__init__.py` (W2-50's) starts `gitleaks stdin`, which
starts no git. `src/gov/launch/launcher.py` (W2-50's) starts the session, whose hooks are the rows above.

**Counts:** 42 calls listed. 31 changed by W2-05 (rows 1 to 31; row 37 changes through row 19 with its file
untouched). 10 marked "after <W2 id> merges": rows 32 to 36 and 38 (W2-53), 39 to 41 (W2-03) and 42 (W2-50).

The test helpers outside `src/` (`tests/**/*support*.py`) build their own environments and are not Gov OS calls.
The one test run the Gov OS starts is row 36.

## Not settled here

- **W2-L160** (the guard's git by absolute path, and the freeze look-up's own limit) is in row 42, W2-50's
  `src/gov/guard/decide.py`. The helper does not pick git's path. The guard's fix belongs to W2-50's file.
- **W2-M161** (every subprocess of close, with a sanitised environment and pinned configuration) is in rows 32 to
  38, W2-53's `src/gov/close/**`. After W2-53 merges, the fix is `env=git_env(root, pinned=True)` in
  `gov.close.repo.git`, and `git_env(root, base=env)` for `_started`.
- **The settings re-sort** (KPI success 3) cannot be fixed in `lefthook.yml`; see the ticket's return.
  `lefthook uninstall` (2.1.15) always rewrites `.claude/settings.json`: in
  `internal/command/uninstall_ai.go`, `uninstallAIHooks` -> `removeAIHookEntries` -> `writeJSONFile`, with no
  check of the configuration or of a change. The rewrite is Go's `json.MarshalIndent` of a map: keys sorted,
  `&`, `<` and `>` escaped.
