# W2-05 acceptance tests (DAEO-0z8c)

**Ticket:** W2-05, "The git environment of every check, hook and helper; the settings re-sort". Profile FULL.
**Closes:** AR-2. **Sources:** DEC-710 (with DEC-711 and DEC-712).
**Author:** the independent test designer (MR-3). The tests were written from the ticket's KPI lines and its
sources before the implementation, and shown red on `c94e1507`.

## Running them

```
PATH=/home/usain/.nvm/versions/node/v22.23.3/bin:$PATH PYTHONPATH=/home/usain/gov-os-worktrees/W2-05/src \
  python3 -m pytest tests/acceptance/W2-05 -q -p no:cacheprovider -rs
```

The suite has 29 cases. The whole run takes about 50 s on this machine. On `c94e1507` it gives 23 failed, 6
passed and 0 skipped.

## How the tests run this worktree's `src/` (DEC-732)

- **`SRC` is derived from the test file's own location.** `w2_05_support.py` sets `REPO_ROOT =
  Path(__file__).resolve().parents[2]` and `SRC = REPO_ROOT / "src"`. No main-tree path is written anywhere.
  The earlier supports these cases reuse derive theirs the same way (`parents[3]` from their own files).
- **Every process a case starts that imports or runs `gov` gets `SRC` first:**
  - The box's `bin/gov` is a launcher. It is the console script that `pyproject.toml`'s `[project.scripts]`
    names, with `sys.path.insert(0, SRC)`.
  - `Box.env()` puts `SRC` first on `PYTHONPATH`, followed by a folder that links `sqlite_vec` alone (as
    W1-21's `Api` does). Its `PATH` is the box's `bin` folder, then `/usr/bin:/bin`.
  - The guard, containment and close cases use the environments of W1-02, W1-03 and W1-30. These put the same
    `src/` on `PYTHONPATH`, derived from their own files.
- **Every repository is temporary and built from scratch** under pytest's `tmp_path`. This covers the
  repository with its linked worktree, the decoy, the bare server and partial clone, and the stand-in dev tier
  (W1-21's fixture). No folder of this repository is copied. A case receives single named files only:
  - `lefthook.yml`;
  - the template's hooks file;
  - `template/.gitleaks.toml`;
  - the retrieval-regression declaration;
  - W1-38's template files, which its own support copies one by one.
- **lefthook only ever runs in a temporary repository.** Its working folder is set there and its environment is
  built from nothing, with no `GIT_*` variable of the caller. Nothing runs `lefthook install` or `uninstall`
  in this repository. The hooks stay uninstalled until W2-08.
- **This repository's own `.claude/settings.json` is never read.** The settings cases either write a stand-in
  (`stand_in_settings()`) or take the file that `rulesync generate` writes in W1-38's temporary project.
- **The dev tier is a stand-in built in `tmp_path`**, named by `GOV_DEV_TIERS` (DEC-723). The workbench is
  never touched.
- **No network and no model.** Embeddings come from W1-21's stand-in endpoint on a loopback port. The box's
  Python sees no installed package other than `sqlite_vec`, so no reranker loads.

## Safety: the nested hook, and processes left behind

On the code before this ticket, a hooked commit in a linked worktree passes its `GIT_DIR` to the check. The
check's own `git commit` in its temporary clone then runs the same repository's pre-commit hook again, which
runs the check again, without end. A first draft of these cases started more than 1500 processes this way
before they were stopped. The suite now bounds this in three ways:

- **The plain hook detects its own re-entry.** It refuses at once when it starts inside its own run (marked by
  the variable `W2_05_IN_THE_HOOK`), and leaves a line in `marks/nested`. The cases report this as their red
  reason ("ran its pre-commit hook again").
- **Every command of a box runs in a process group of its own.** A run that does not end within its limit is
  stopped with its whole group. The limit is 90 s for a hooked commit (one takes about 5 s) and 300 s for any
  other call.
- **Nothing is left running after a case.** An autouse fixture stops every process left under the case's
  `tmp_path`, matched by its command line or its working folder. Nothing outside that folder is touched.

## The KPI lines and their tests

| KPI | Test (file::case) |
|---|---|
| **S1**: every check, test helper and command that runs git in another folder clears the inherited `GIT_*` variables; one helper does it; the sweep record lists every call [AR-2, W2-M105, W2-M113, W2-M161, W2-L160] | `test_w2_05_sweep.py`: all 3 cases (the record, every git-starting file named, the helper). The behaviour half is in `test_w2_05_planted.py`, listed under the covers ids below. |
| **S2**: a hooked commit in a linked worktree leaves its branch, index and reflog as the commit made them (DEC-710) | `test_w2_05_linked_worktree.py`: `test_a_hooked_commit_that_runs_the_retrieval_check_leaves_the_branch_as_the_commit_made_it[a linked worktree]` (success); `[the main tree]` (guard); `test_a_refusing_hook_in_a_linked_worktree_leaves_the_branch_the_reflog_and_the_staged_change` (the refusing side); `test_a_commit_in_a_linked_worktree_through_lefthook_and_the_project_hooks_file` (through lefthook and `gov ci checks G1 G2`) |
| **S3**: lefthook install and uninstall leave `.claude/settings.json` byte-identical, and adapter-portability stays green | `test_w2_05_settings.py`: `test_install_and_uninstall_leave_the_settings_byte_identical[lefthook.yml]`, `[the template's hooks file]`; `test_install_and_uninstall_from_a_linked_worktree_leave_both_settings_byte_identical`; `test_adapter_portability_stays_green_through_install_and_uninstall` |
| **F1**: a planted `GIT_DIR` or `GIT_INDEX_FILE` in a hook's environment reaches no child git call | `test_w2_05_planted.py`: `test_the_retrieval_check_under_a_planted_git_dir_measures_and_leaves_the_decoy[the check's declared command]`, `[gov ci checks G1]`; `test_a_staged_secret_is_found_under_a_planted_decoy_index[GIT_INDEX_FILE]`, `[GIT_DIR and GIT_INDEX_FILE]`; `test_a_clean_index_is_not_refused_for_a_decoy_s_staged_secret[GIT_DIR]`, `[GIT_DIR and GIT_INDEX_FILE]`; `test_read_merge_under_a_planted_git_dir_reads_its_own_repository`; `test_the_containment_check_catches_the_change_whatever_its_environment_holds[a decoy GIT_DIR and GIT_INDEX_FILE]`; and the S2 linked-worktree cases, where git itself plants both variables |
| Edge: a caller that set `GIT_*` on purpose for its own folder | `test_w2_05_planted.py::test_a_hooked_commit_in_a_linked_worktree_scans_the_index_git_gives_it` with `[git commit -a, a secret in a tracked file]`, `[git commit -- <path>, a secret in that file]` and `[git commit -a, nothing secret]` |
| Edge: a check in a linked worktree | the S2 cases; `test_install_and_uninstall_from_a_linked_worktree_...`; `test_the_guard_hook_refuses_within_its_own_limit_...` |
| Edge: a call in a command, a check and a test helper | command: `gov ci staged-secrets`, `gov ci checks G1`, `gov close`; check: retrieval-regression, containment (W1-03's PostToolUse hook); test helper: the ticket's acceptance test that `gov close` runs (`test_gov_close_runs_...`) |

## The covers ids and their tests

| Id | Test |
|---|---|
| **AR-2** | every case of the suite (its four "closes when" lines are S1 to S3, plus the sweep) |
| **W2-M105**: `gov.guard.containment_merge` sets `GIT_NO_LAZY_FETCH` and clears `GIT_TRACE` | `test_read_merge_under_planted_trace_variables_writes_no_trace`; `test_read_merge_in_a_partial_clone_fetches_nothing`; `test_read_merge_under_a_planted_git_dir_reads_its_own_repository` (guard) |
| **W2-M113**: all governance git calls run with pinned configuration and a cleared environment | `test_the_containment_check_catches_the_change_whatever_its_environment_holds[a decoy GIT_DIR and GIT_INDEX_FILE]`, `[trace variables]`, `[a trace setting in the person's git configuration]` |
| **W2-M161**: all subprocesses of close run with a sanitised environment and pinned git configuration | `test_gov_close_runs_its_subprocesses_and_the_ticket_tests_with_a_sanitised_environment` |
| **W2-L160**: git is resolved by absolute path, and the freeze look-up has its own limit | `test_the_guard_hook_does_not_run_the_git_first_on_path`; `test_the_guard_hook_refuses_within_its_own_limit_when_the_freeze_look_up_hangs` |

Not written:

- **W2-L109** (findings grouped by cause) and **W2-M231** (the check and the hand-run generator use the same
  root) state no form these tests could hold them to. They are returned to the lead.
- **W2-M012** is an owner act.
- **W2-M281** (adapter-portability goes red on a planted drift in the template's hooks source) is package P-4.

## Each test's expected red reason on `c94e1507`

| Test | Red now because |
|---|---|
| `test_the_sweep_record_lists_the_calls_in_a_table` | `docs/research/AR-2-git-sweep.md` is absent |
| `test_every_file_of_the_source_that_starts_git_is_named_in_the_sweep` | the same |
| `test_the_one_helper_is_there_and_the_sweep_names_it` | `No module named 'gov.util'` |
| `..._leaves_the_branch_as_the_commit_made_it[a linked worktree]` | the check's `git commit -m adopted` in its temporary clone used the inherited `GIT_DIR` and ran the repository's pre-commit hook again ("nested" mark) |
| `..._leaves_the_branch_as_the_commit_made_it[the main tree]` | **green** (guard: no `GIT_DIR` is exported in the main tree) |
| `test_a_refusing_hook_in_a_linked_worktree_...` | the same nested hook run |
| `test_a_commit_in_a_linked_worktree_through_lefthook_...` | the DEC-710 symptom: the check's foreign commit moved the worktree's HEAD, and the real commit failed with `fatal: cannot lock ref 'HEAD': is at <x> but expected <y>` |
| `test_install_and_uninstall_leave_the_settings_byte_identical[lefthook.yml]` | `lefthook uninstall` re-sorts `.claude/settings.json` (its keys, alphabetically) |
| `...[the template's hooks file]` | the same |
| `test_install_and_uninstall_from_a_linked_worktree_...` | the same, in the worktree |
| `test_adapter_portability_stays_green_through_install_and_uninstall` | the same, on rulesync's generated settings (`install` alone leaves them identical) |
| `test_the_retrieval_check_under_a_planted_git_dir_...[the check's declared command]` | the decoy changed: the check committed into it (`COMMIT_EDITMSG`, index, reflogs, objects) |
| `...[gov ci checks G1]` | the same |
| `test_a_staged_secret_is_found_under_a_planted_decoy_index[GIT_INDEX_FILE]` | exit 0: `gov ci staged-secrets` scanned the decoy's clean index and missed the staged secret (fail-open) |
| `...[GIT_DIR and GIT_INDEX_FILE]` | the same |
| `test_a_clean_index_is_not_refused_for_a_decoy_s_staged_secret[GIT_DIR]` | exit 3: it scanned the decoy's index |
| `...[GIT_DIR and GIT_INDEX_FILE]` | the same |
| `test_a_hooked_commit_in_a_linked_worktree_scans_the_index_git_gives_it[...]` (3 cases) | **green** (guard: git's own index for `commit -a` and `commit -- <path>` is honoured) |
| `test_read_merge_under_planted_trace_variables_writes_no_trace` | `GIT_TRACE`, `GIT_TRACE2`, `GIT_TRACE2_EVENT` and `GIT_TRACE_SETUP` were written |
| `test_read_merge_under_a_planted_git_dir_reads_its_own_repository` | **green** (guard) |
| `test_read_merge_in_a_partial_clone_fetches_nothing` | 4 lazy fetches from `origin`, and an answer given from the fetched trees |
| `test_the_containment_check_..._holds[a decoy GIT_DIR and GIT_INDEX_FILE]` | **green** (guard) |
| `...[trace variables]` | the planted trace files were written |
| `...[a trace setting in the person's git configuration]` | `~/.gitconfig`'s `trace2.eventTarget` was written: the configuration is not pinned |
| `test_gov_close_runs_its_subprocesses_and_the_ticket_tests_with_a_sanitised_environment` | every planted variable (`GIT_DIR`, `GIT_INDEX_FILE`, `GIT_TRACE*`) reached the ticket's test run. The close itself answered `ok: true`. |
| `test_the_guard_hook_does_not_run_the_git_first_on_path` | the guard ran the git first on `PATH` (`-C <root> rev-parse --git-common-dir`) |
| `test_the_guard_hook_refuses_within_its_own_limit_when_the_freeze_look_up_hangs` | decision `timeout` after 20 s: the freeze look-up has no limit of its own |

## Red until another ticket merges (DEC-777)

These cases depend on files of other unmerged tickets, which this run does not change:

| Case | Red until | File |
|---|---|---|
| `test_w2_05_planted.py::test_gov_close_runs_its_subprocesses_and_the_ticket_tests_with_a_sanitised_environment` | **W2-53** merges | `src/gov/close/**` (the close's test run and its git calls) |
| `test_w2_05_planted.py::test_the_guard_hook_does_not_run_the_git_first_on_path` | **W2-50** merges | `src/gov/guard/decide.py` (the guard's `git rev-parse --git-common-dir`) |
| `test_w2_05_planted.py::test_the_guard_hook_refuses_within_its_own_limit_when_the_freeze_look_up_hangs` | **W2-50** merges | `src/gov/guard/decide.py` (the freeze look-up) |

No case depends on the files of W2-54, W2-03, W2-16 or W2-20.

## Skips

A case that needs an absent tool skips with the reason stated (`skip_without`). On this machine nothing is
absent, and nothing skips.

| Tool | Cases that skip without it |
|---|---|
| `git` | every case that uses the box |
| `lefthook` | the S3 cases; the lefthook case of S2 |
| `gitleaks` | the staged-secrets cases; the lefthook case of S2 |
| `rulesync` | `test_adapter_portability_stays_green_through_install_and_uninstall` |
| `sqlite_vec` | the retrieval-regression cases (the `tiers` fixture) |

## Readings the tests rest on (returned as packages)

- **P-1: an honoured versus a planted `GIT_INDEX_FILE`.** A `GIT_*` value that names the call's own
  repository's git directory, or a file inside it, is git's own. Examples are `index.lock` for `commit -a`,
  `next-index-*.lock` for `commit -- <path>`, and the relative `.git/index` in the main tree. Such a value is
  honoured. Any other value is cleared. The F1 cases and `_on_purpose` are written against this reading.
- **P-2: the freeze look-up's own limit.** The ticket gives no value. The case takes "below the hook's 20 s
  deadline" and asserts an answer within 18 s. The answer is `deny` (DEC-580: the guard answers refuse).
- **P-3: the template's hooks file.** The ticket's allowed path is `template/lefthook.yml`, but the tree holds
  `template/lefthook.yml.jinja`. The template case takes `template/lefthook.yml` if it exists, and the `.jinja`
  file otherwise.
- **P-4: W2-M281.** "A planted drift in the template hooks source" has two readings: `lefthook.yml.jinja`, or
  the Claude Code hooks source `template/.rulesync/hooks.jsonc` compared with the kernel's `settings.json`. No
  case is written for it.

## What was measured (git 2.43.0, lefthook 2.1.15, gitleaks 8.30.1)

- **What git exports to a pre-commit hook:**
  - In a linked worktree: `GIT_DIR=<main>/.git/worktrees/<wt>` and an absolute `GIT_INDEX_FILE`. The index is
    `.../index`, or `index.lock` for `commit -a`, or `next-index-*.lock` for `commit -- <path>`.
  - In the main tree: `GIT_INDEX_FILE=.git/index` (relative) and no `GIT_DIR`.
- **lefthook 2.1.15:** `install` leaves a Claude Code settings file byte-identical; `uninstall` re-sorts its
  keys.
