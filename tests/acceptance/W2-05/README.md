# W2-05 acceptance tests (DAEO-0z8c)

**Ticket:** W2-05, "The git environment of every check, hook and helper; the settings re-sort". Profile FULL.
**Closes:** AR-2. **Sources:** DEC-710 (with DEC-711 and DEC-712).
**Author:** the independent test designer (MR-3). The tests were written from the ticket's KPI lines and its
sources before the implementation, and shown red on `c94e1507`. The four S3 cases (`test_w2_05_settings.py`)
were rewritten after the implementation began by a later independent test designer, as the owner re-baselined
the S3 line (DEC-783, option (b) of P-W2-33). Each rewrite carries a `Rewrite-Reason:` trailer (DEC-491).
An independent review of `0983be4c` found two behaviours the cases missed (F1 and F2, DEC-413 round 1; passed as
behaviours under DEC-136). A further independent test designer wrote their cases on top of `0983be4c` and rewrote
the three F1 cases F1 contradicts, each with a `Rewrite-Reason:` trailer (see "The review's F1 and F2").

## Running them

```
PATH=/home/usain/.nvm/versions/node/v22.23.3/bin:$PATH PYTHONPATH=/home/usain/gov-os-worktrees/W2-05/src \
  python3 -m pytest tests/acceptance/W2-05 -q -p no:cacheprovider -rs
```

The suite has 35 cases. The whole run takes about 60 s on this machine.

- On `c94e1507`, with the S3 cases as first written, it gave 23 failed, 6 passed and 0 skipped.
- On `aa676b9f`, with the S3 cases rewritten (DEC-783), it gave 5 failed, 24 passed and 0 skipped (49 s).
  The 5 red cases are the ones listed under "Red until another ticket merges".
- On `0983be4c`, with the F1 and F2 cases (29 cases became 35), it gives 14 failed, 21 passed and 0 skipped
  (59 to 66 s, in a launched session). The 14 red cases are the 5 under "Red until another ticket merges" and the
  9 of "The review's F1 and F2".
- **Run `test_w2_05_code_index_tool.py` outside a launched session.** The code index keeps its tool's daemon
  files in a folder of its own under `/tmp` (`/tmp/gov-cbm-<uid>/…`, W1-16, DEC-338). A launched session cannot
  write there, so `gov rebuild` reports the code index `not_recreated` (`Read-only file system`) and starts no
  tool. The case then fails with "gov rebuild started no codebase-memory-mcp", not with its own reason.

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
  - W1-38's template files, which its own support copies one by one;
  - the path map that W1-16's public support (`path_map_text`) builds for its temporary repositories, for the
    code-index case's project.
- **The code index's tool is a recording stand-in** (`recording_stand_in`), a script in the case's `tmp_path`
  first on `PATH`. It records the arguments, the folder and the environment of each start, prints nothing and
  exits 0. The real tool is never started by these cases.
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
| **S1**: every check, test helper and command that runs git in another folder clears the inherited `GIT_*` variables; one helper does it; the sweep record lists every call [AR-2, W2-M105, W2-M113, W2-M161, W2-L160] | `test_w2_05_sweep.py`: all 4 cases (the record, every git-starting file named, the code index's tool as a call that starts git (F2), the helper). The behaviour half is in `test_w2_05_planted.py`, listed under the covers ids below, and in `test_w2_05_code_index_tool.py::test_the_code_index_tool_started_by_gov_rebuild_gets_no_inherited_git_variable` (F2: a program the Gov OS starts that starts git itself). |
| **S2**: a hooked commit in a linked worktree leaves its branch, index and reflog as the commit made them (DEC-710) | `test_w2_05_linked_worktree.py`: `test_a_hooked_commit_that_runs_the_retrieval_check_leaves_the_branch_as_the_commit_made_it[a linked worktree]` (success); `[the main tree]` (guard); `test_a_refusing_hook_in_a_linked_worktree_leaves_the_branch_the_reflog_and_the_staged_change` (the refusing side); `test_a_commit_in_a_linked_worktree_through_lefthook_and_the_project_hooks_file` (through lefthook and `gov ci checks G1 G2`) |
| **S3**, as DEC-783 (b) re-baselined it: `lefthook install` leaves `.claude/settings.json` byte-identical to the committed file, and adapter-portability stays green; `uninstall` is an owner act, followed by restoring the committed file (DEC-712) | `test_w2_05_settings.py`: `test_install_leaves_the_settings_byte_identical_before_and_after_the_owner_s_uninstall_and_restore[lefthook.yml]`, `[the template's hooks file]`; `test_install_from_a_linked_worktree_leaves_both_settings_byte_identical_and_the_owner_s_act_both_clean`; `test_adapter_portability_stays_green_through_install_and_the_owner_s_uninstall_and_restore`. What `uninstall` alone does to the file is lefthook's own behaviour and is not asserted. The state after the owner's act is: `lefthook uninstall`, then `git restore -- .claude/settings.json` in each tree whose file changed. |
| **F1**: a planted `GIT_DIR` or `GIT_INDEX_FILE` in a hook's environment reaches no child git call; and (review F1) the staged-secrets gate never passes on an index other than the one being committed | `test_w2_05_planted.py`: `test_the_retrieval_check_under_a_planted_git_dir_measures_and_leaves_the_decoy[the check's declared command]`, `[gov ci checks G1]`; `test_a_staged_secret_under_a_planted_decoy_index_is_refused_naming_the_index[GIT_INDEX_FILE]`, `[GIT_DIR and GIT_INDEX_FILE]` (rewritten); `test_a_clean_index_is_not_refused_for_a_decoy_s_staged_secret[GIT_DIR]`; `test_a_clean_index_under_a_planted_decoy_index_is_refused_naming_the_index` (rewritten); `test_staged_secrets_refuses_an_inherited_index_outside_the_git_directory_naming_it[a secret in that index, the project's index clean]`, `[nothing secret in that index, the project's index clean]`, `[nothing secret in that index, a secret in the project's index]` (new); `test_a_hooked_commit_with_its_index_outside_the_git_directory_and_a_secret_there_does_not_land` (new, through lefthook); `test_read_merge_under_a_planted_git_dir_reads_its_own_repository`; `test_the_containment_check_catches_the_change_whatever_its_environment_holds[a decoy GIT_DIR and GIT_INDEX_FILE]`; and the S2 linked-worktree cases, where git itself plants both variables |
| Edge: a caller that set `GIT_*` on purpose for its own folder | `test_w2_05_planted.py::test_a_hooked_commit_in_a_linked_worktree_scans_the_index_git_gives_it` with `[git commit -a, a secret in a tracked file]`, `[git commit -- <path>, a secret in that file]` and `[git commit -a, nothing secret]` |
| Edge: a check in a linked worktree | the S2 cases; `test_install_from_a_linked_worktree_...`; `test_the_guard_hook_refuses_within_its_own_limit_...` |
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
- **W2-M281** (adapter-portability goes red on a planted drift in the template's hooks source) has no case in
  this suite. DEC-783 accepted reading P-4: the source is `template/.rulesync/hooks.jsonc`. The lead returns
  the row as a package.

## Each test's expected red reason on `c94e1507` (the rewritten S3 cases: what was seen on `aa676b9f`)

| Test | Red now because |
|---|---|
| `test_the_sweep_record_lists_the_calls_in_a_table` | `docs/research/AR-2-git-sweep.md` is absent |
| `test_every_file_of_the_source_that_starts_git_is_named_in_the_sweep` | the same |
| `test_the_one_helper_is_there_and_the_sweep_names_it` | `No module named 'gov.util'` |
| `..._leaves_the_branch_as_the_commit_made_it[a linked worktree]` | the check's `git commit -m adopted` in its temporary clone used the inherited `GIT_DIR` and ran the repository's pre-commit hook again ("nested" mark) |
| `..._leaves_the_branch_as_the_commit_made_it[the main tree]` | **green** (guard: no `GIT_DIR` is exported in the main tree) |
| `test_a_refusing_hook_in_a_linked_worktree_...` | the same nested hook run |
| `test_a_commit_in_a_linked_worktree_through_lefthook_...` | the DEC-710 symptom: the check's foreign commit moved the worktree's HEAD, and the real commit failed with `fatal: cannot lock ref 'HEAD': is at <x> but expected <y>` |
| the four S3 cases, as first written (`test_install_and_uninstall_leave_the_settings_byte_identical[...]` ×2, `..._from_a_linked_worktree_...`, `test_adapter_portability_stays_green_through_install_and_uninstall`) | `lefthook uninstall` re-sorted `.claude/settings.json` (its keys, alphabetically). The same happened on rulesync's generated settings. `install` alone left the file identical. These cases were replaced by the rewritten ones below (DEC-783). |
| `test_install_leaves_the_settings_byte_identical_before_and_after_the_owner_s_uninstall_and_restore[lefthook.yml]`, `[the template's hooks file]` | not run on `c94e1507` (written later). On `aa676b9f`: **green**. `lefthook` is not part of the code under test and neither hooks file was changed. |
| `test_install_from_a_linked_worktree_leaves_both_settings_byte_identical_and_the_owner_s_act_both_clean` | the same: **green** on `aa676b9f` |
| `test_adapter_portability_stays_green_through_install_and_the_owner_s_uninstall_and_restore` | the same: **green** on `aa676b9f` |
| `test_the_retrieval_check_under_a_planted_git_dir_...[the check's declared command]` | the decoy changed: the check committed into it (`COMMIT_EDITMSG`, index, reflogs, objects) |
| `...[gov ci checks G1]` | the same |
| `test_a_staged_secret_is_found_under_a_planted_decoy_index[GIT_INDEX_FILE]` | exit 0: `gov ci staged-secrets` scanned the decoy's clean index and missed the staged secret (fail-open). Rewritten after `0983be4c` as `test_a_staged_secret_under_a_planted_decoy_index_is_refused_naming_the_index` (review F1). |
| `...[GIT_DIR and GIT_INDEX_FILE]` | the same; rewritten the same way |
| `test_a_clean_index_is_not_refused_for_a_decoy_s_staged_secret[GIT_DIR]` | exit 3: it scanned the decoy's index |
| `...[GIT_DIR and GIT_INDEX_FILE]` | the same. Rewritten after `0983be4c` as `test_a_clean_index_under_a_planted_decoy_index_is_refused_naming_the_index` (review F1). |
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

## The review's F1 and F2 (DEC-413 round 1): the cases, and their red reason on `0983be4c`

**F1. The staged-secrets gate never passes on an index other than the one being committed.** It holds under
either answer to P-1. When `gov ci staged-secrets` inherits a `GIT_INDEX_FILE` that is not git's own index of the
project, it refuses: a non-zero exit, with a refusal that names that index. This holds whatever that index or the
project's own index holds. It never answers pass. The assertion is `assert_index_refused`.

What stays as before: a planted index still reaches no child git call (the decoy is untouched, asserted in every
rewritten case). A planted `GIT_DIR` alone is still cleared, and the project's clean index still passes
(`[GIT_DIR]`, unchanged). git's own index is still scanned (`_on_purpose`, the S2 cases, unchanged).

**F2. The code index's tool gets no inherited `GIT_*` variable.** The code index starts `codebase-memory-mcp`
(W1-16's README), which starts git in the project. Every start of it by `gov rebuild --no-embeddings` (the public
command that builds the code index) receives none of the planted `GIT_DIR`, `GIT_INDEX_FILE`, `GIT_TRACE`,
`GIT_TRACE2_EVENT`, `GIT_CONFIG_COUNT`, `GIT_CONFIG_KEY_0` and `GIT_CONFIG_VALUE_0`. The sweep record lists the
tool's starts in a row that names the tool and the file that starts it. The lower bound of those files is every
file of the code index's package (`src/gov/codeintel/`, W1-16's public interface) that holds the literal
`"codebase-memory-mcp"`, as for git. `src/gov/doctor/command.py` also names the tool, but it does not build the
code index, so it is not counted.

| Case | Kind | Red on `0983be4c` because (seen) |
|---|---|---|
| `test_w2_05_planted.py::test_a_staged_secret_under_a_planted_decoy_index_is_refused_naming_the_index[GIT_INDEX_FILE]` | rewritten | refused with the staged-secret refusal (`SECRET_STAGED`, the project's default index scanned); the refusal does not name the planted index |
| `...[GIT_DIR and GIT_INDEX_FILE]` | rewritten | the same |
| `test_w2_05_planted.py::test_a_clean_index_under_a_planted_decoy_index_is_refused_naming_the_index` | rewritten | exit 0: the gate passed (it scanned the project's default index in place of the planted one) |
| `test_w2_05_planted.py::test_staged_secrets_refuses_an_inherited_index_outside_the_git_directory_naming_it[a secret in that index, the project's index clean]` | new | exit 0: the gate passed, and the secret staged in the commit's index was not seen |
| `...[nothing secret in that index, the project's index clean]` | new | exit 0: the gate passed |
| `...[nothing secret in that index, a secret in the project's index]` | new | refused with `SECRET_STAGED` (the default index); the refusal does not name the commit's index |
| `test_w2_05_planted.py::test_a_hooked_commit_with_its_index_outside_the_git_directory_and_a_secret_there_does_not_land` | new | the commit landed (exit 0; lefthook's `staged-secrets` answered `"scans": 2, "secrets": 0`) |
| `test_w2_05_sweep.py::test_the_sweep_lists_the_starts_of_the_code_index_tool_as_calls_that_start_git` | new | the sweep has no row naming `codebase-memory-mcp` and `src/gov/codeintel/__init__.py` (its rows 16 and 17 name the file's own git calls only) |
| `test_w2_05_code_index_tool.py::test_the_code_index_tool_started_by_gov_rebuild_gets_no_inherited_git_variable` | new | **in a launched session, not its own reason:** "gov rebuild started no codebase-memory-mcp", because the code index was `not_recreated` (`Read-only file system: '/tmp/gov-cbm-1000/…'`). Its expected reason, outside a session (by the review, not seen here): the stand-in received the planted variables. |

## Red until another ticket merges (DEC-777)

These cases depend on files of other unmerged tickets, which this run does not change:

| Case | Red until | File |
|---|---|---|
| `test_w2_05_planted.py::test_gov_close_runs_its_subprocesses_and_the_ticket_tests_with_a_sanitised_environment` | **W2-53** merges | `src/gov/close/**` (the close's test run and its git calls) |
| `test_w2_05_planted.py::test_the_guard_hook_does_not_run_the_git_first_on_path` | **W2-50** merges | `src/gov/guard/decide.py` (the guard's `git rev-parse --git-common-dir`) |
| `test_w2_05_planted.py::test_the_guard_hook_refuses_within_its_own_limit_when_the_freeze_look_up_hangs` | **W2-50** merges | `src/gov/guard/decide.py` (the freeze look-up) |
| `test_w2_05_planted.py::test_the_containment_check_catches_the_change_whatever_its_environment_holds[trace variables]` | **W2-50** merges | `src/gov/guard/decide.py` (its mirror-path git call) |
| `test_w2_05_planted.py::test_the_containment_check_catches_the_change_whatever_its_environment_holds[a trace setting in the person's git configuration]` | **W2-50** merges | the same |

That makes 4 cases red until W2-50 merges and 1 until W2-53 merges. On `aa676b9f` these were the run's only 5
red cases. On `0983be4c` they are still red, beside the 9 cases of the review's F1 and F2. The lead found the two containment parametrizations in the earlier verification. This run agrees with
that finding from outside: in both cases the only git calls that wrote the planted trace targets were
`git -C <root> rev-parse --git-common-dir`, twice. The `[trace variables]` case shows it in `GIT_TRACE`, and the
configuration case in the `trace2.eventTarget` events. The guard-hook case reports the same call as the guard's.

No case depends on the files of W2-54, W2-03, W2-16 or W2-20.

## Skips

A case that needs an absent tool skips with the reason stated (`skip_without`). On this machine nothing is
absent, and nothing skips.

| Tool | Cases that skip without it |
|---|---|
| `git` | every case that uses the box |
| `lefthook` | the S3 cases; the lefthook case of S2; the lefthook case of F1 (an index outside the git directory) |
| `gitleaks` | the staged-secrets cases; the lefthook cases of S2 and F1 |
| `rulesync` | `test_adapter_portability_stays_green_through_install_and_the_owner_s_uninstall_and_restore` |
| `sqlite_vec` | the retrieval-regression cases (the `tiers` fixture) |

## Readings the tests rest on

P-1 and P-2 were returned as packages. DEC-783 accepted P-3 and P-4 and answered P-A.

- **P-1: an honoured versus a planted `GIT_INDEX_FILE`.** A `GIT_*` value that names the call's own
  repository's git directory, or a file inside it, is git's own. Examples are `index.lock` for `commit -a`,
  `next-index-*.lock` for `commit -- <path>`, and the relative `.git/index` in the main tree. Such a value is
  honoured. Any other value is cleared. The F1 cases and `_on_purpose` are written against this reading.
  **P-1 stays returned to the owner.** The staged-secrets gate is held to a stricter behaviour that holds under
  either answer (review F1). An inherited `GIT_INDEX_FILE` that is not git's own index of the project is refused,
  and the refusal names it; it is never cleared in favour of the default index. Clearing it is right for every
  other git call. For the gate it would mean answering on an index other than the one being committed: the
  secret staged in the commit's index passes, and the commit lands.
- **P-2: the freeze look-up's own limit.** The ticket gives no value. The case takes "below the hook's 20 s
  deadline" and asserts an answer within 18 s. The answer is `deny` (DEC-580: the guard answers refuse).
- **P-3: the template's hooks file. Accepted by the owner (DEC-783).** The ticket's allowed path is
  `template/lefthook.yml`, but the tree holds `template/lefthook.yml.jinja`. The template's hooks file is
  `template/lefthook.yml.jinja`, which stays untouched. The template case takes that file.
- **P-4: W2-M281. Accepted by the owner (DEC-783).** "A planted drift in the template hooks source" is read as
  the Claude Code hooks source `template/.rulesync/hooks.jsonc`. W2-M281 has no case in this suite. The lead
  returns it as a package.
- **P-A: the S3 line as first written. Answered by DEC-783 (b).** lefthook 2.1.15 rewrites a Claude Code
  settings file on every `uninstall`, whatever the project's files hold. The owner re-baselined the line:
  - `lefthook install` leaves the file byte-identical to the committed one;
  - `uninstall` is an owner act, followed by restoring the committed file (DEC-712).

  The S3 cases were rewritten to match. Every install keeps its byte-identical expectation. Each case also
  asserts that `install` really installed a pre-commit hook, so that an unchanged file cannot come from an
  install that did nothing.

## What was measured (git 2.43.0, lefthook 2.1.15, gitleaks 8.30.1)

- **What git exports to a pre-commit hook:**
  - In a linked worktree: `GIT_DIR=<main>/.git/worktrees/<wt>` and an absolute `GIT_INDEX_FILE`. The index is
    `.../index`, or `index.lock` for `commit -a`, or `next-index-*.lock` for `commit -- <path>`.
  - In the main tree: `GIT_INDEX_FILE=.git/index` (relative) and no `GIT_DIR`.
- **lefthook 2.1.15:** `install` leaves a Claude Code settings file byte-identical; `uninstall` re-sorts its
  keys. Run from a linked worktree, `install` left both trees' files identical, and `uninstall` rewrote only
  the worktree's file, not the main tree's (measured on 2026-10-18).
