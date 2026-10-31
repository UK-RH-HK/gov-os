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
For the resume, after `w2/integrate` (with W2-50 and W2-53) was merged into the branch (`1814315f106e`), a fourth
independent test designer wrote the cases of the three behaviours the owner decided: F-A with reading P-1 (DEC-804
items 1 and 3, DEC-807 item 2), W2-M281 (DEC-805), and the freeze look-up's own 15 s limit (DEC-783 item 2). The one
case those contradict, the freeze look-up case, was rewritten with a `Rewrite-Reason:` trailer (see "The resume's
three behaviours").

## Running them

```
PATH=/home/usain/.nvm/versions/node/v22.23.3/bin:$PATH PYTHONPATH=/home/usain/gov-os-worktrees/W2-05/src \
  python3 -m pytest tests/acceptance/W2-05 -q -p no:cacheprovider -rs
```

The suite has 48 cases. The whole run takes about 100 s to 200 s on this machine, in a launched session.

- On `c94e1507`, with the S3 cases as first written, it gave 23 failed, 6 passed and 0 skipped.
- On `aa676b9f`, with the S3 cases rewritten (DEC-783), it gave 5 failed, 24 passed and 0 skipped (49 s).
  The 5 red cases are the ones listed under "Red until another ticket merges".
- On `0983be4c`, with the F1 and F2 cases (29 cases became 35), it gave 14 failed, 21 passed and 0 skipped
  (59 to 66 s, in a launched session). The 14 red cases are the 5 under "Red until another ticket merges" and the
  9 of "The review's F1 and F2".
- On `1814315f106e` (`w2/integrate` merged in, W2-50 and W2-53 with it), before this batch: 35 cases, 12 failed,
  23 passed and 0 skipped (173 s and 197 s, two runs, in a launched session). The 12 red cases:
  - the 5 of "Red until another ticket merges" (both tickets have merged; this ticket's own change to their files
    is not made yet);
  - the 5 cases that run the retrieval-regression check: `test_w2_05_linked_worktree.py`'s
    `..._leaves_the_branch_as_the_commit_made_it[a linked worktree]`, `[the main tree]` and
    `test_a_commit_in_a_linked_worktree_through_lefthook_and_the_project_hooks_file`, and `test_w2_05_planted.py`'s
    `test_the_retrieval_check_under_a_planted_git_dir_...[the check's declared command]`, `[gov ci checks G1]`. Each
    fails on the check's own result, not on a git environment: "Ollama is unavailable: semantic retrieval is skipped
    and results are FTS-only. hit@5: 0.0 (baseline: 80.0)", exit 1 (through lefthook: `CHECK_FAILED: hard-block
    checks failed: retrieval-regression`). The decoys were untouched and no nested hook ran. They passed on
    `0983be4c`. The test designer did not find the cause: it may be the merge (the merge commit names
    `retrieve_check.py`, which the designer may not read) or this session's sandbox. It is returned to the lead;
  - `test_w2_05_sweep.py::test_every_file_of_the_source_that_starts_git_is_named_in_the_sweep`: 3 of the 27 files
    of `src/gov` that start git are not named in the sweep at this head: `src/gov/cli/main.py`,
    `src/gov/close/nightly.py`, `src/gov/guard/reads.py`;
  - `test_w2_05_code_index_tool.py`, for the launched-session reason below.
- On `1814315f106e`, with this batch (35 cases became 48): 21 failed, 27 passed and 0 skipped (99 s, in a launched
  session). The 21 red cases are the 12 above (the freeze look-up case rewritten, still red) and the 9 new red
  cases of "The resume's three behaviours". Its 4 "not drift" cases are green.
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
  - The hooks-source cases (W2-M281) run adapter-portability's declared command through W1-38's
    `run_portability_check`, which sets `PYTHONPATH` to the same `src/`, derived from its own file (`parents[3]`).
  - The declared-check cases (F-A) run the hooked commit with the box's environment; `gov ci checks` and
    `gov ci staged-secrets` are the box's `gov`. The declared check itself is a Python script of the temporary
    project, started by the interpreter's absolute path, that imports nothing of `gov`. It does not depend on which
    package a declared check runs on (since W2-59, the judge's own, DEC-822 item 3).
- **Every repository is temporary and built from scratch** under pytest's `tmp_path`. This covers the
  repository with its linked worktree, the decoy, the bare server and partial clone, and the stand-in dev tier
  (W1-21's fixture). No folder of this repository is copied. A case receives single named files only:
  - `lefthook.yml`;
  - the template's hooks file;
  - `template/.gitleaks.toml`;
  - the retrieval-regression declaration;
  - W1-38's template files, which its own support copies one by one (the hooks-source cases then move that
    temporary project's kernel to `template/governance/kernel`, inside the temporary project, so that it has this
    repository's shape);
  - the two hooks sources `.rulesync/hooks.jsonc` and `template/.rulesync/hooks.jsonc`, read in place. The
    not-drift cases and the case over this repository's two sources write their texts, or a variant of them, into
    the temporary project; the drift cases write a pair built from one source written in the case (`BASE_HOOKS`,
    DEC-970) and read neither file;
  - the path map that W1-16's public support (`path_map_text`) builds for its temporary repositories, for the
    code-index case's project.
- **The code index's tool is a recording stand-in** (`recording_stand_in`), a script in the case's `tmp_path`
  first on `PATH`. It records the arguments, the folder and the environment of each start, prints nothing and
  exits 0. The real tool is never started by these cases.
- **lefthook only ever runs in a temporary repository.** Its working folder is set there and its environment is
  built from nothing, with no `GIT_*` variable of the caller. Nothing runs `lefthook install` or `uninstall`
  in this repository. The hooks stay uninstalled until W2-08.
- **The declared check's own repository is made outside the project,** in a folder under the case's `tmp_path`
  (`the-check-s-own/own-*`). Its records (the environment it was started with, its git calls) go to the box's
  `marks` folder.
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
| **S1**: every check, test helper and command that runs git in another folder clears the inherited `GIT_*` variables; one helper does it; the sweep record lists every call [AR-2, W2-M105, W2-M113, W2-M161, W2-L160] | `test_w2_05_sweep.py`: all 4 cases (the record, every git-starting file named, the code index's tool as a call that starts git (F2), the helper). The behaviour half is in `test_w2_05_planted.py`, listed under the covers ids below, and in `test_w2_05_code_index_tool.py::test_the_code_index_tool_started_by_gov_rebuild_gets_no_inherited_git_variable` (F2: a program the Gov OS starts that starts git itself). The nightly's `git bisect run` step, a test helper that runs git in another folder (review R4-1, DEC-970): `test_w2_05_bisect_step.py`, all 3 cases (see "The review's R4-1" below). |
| **S2**: a hooked commit in a linked worktree leaves its branch, index and reflog as the commit made them (DEC-710) | `test_w2_05_linked_worktree.py`: `test_a_hooked_commit_that_runs_the_retrieval_check_leaves_the_branch_as_the_commit_made_it[a linked worktree]` (success); `[the main tree]` (guard); `test_a_refusing_hook_in_a_linked_worktree_leaves_the_branch_the_reflog_and_the_staged_change` (the refusing side); `test_a_commit_in_a_linked_worktree_through_lefthook_and_the_project_hooks_file` (through lefthook and `gov ci checks G1 G2`); and, for a check the project declares that runs git in a repository of its own (F-A, DEC-804, DEC-807), `test_w2_05_declared_check.py::test_a_declared_check_that_runs_git_in_a_repository_of_its_own_gets_no_index_and_the_commit_lands_as_staged[a linked worktree, a plain commit]`, `[the main tree, a plain commit]`, `[the main tree, git commit -a]` (new): the commit lands with exactly the staged tree, the index matches it and names no missing object |
| **S3**, as DEC-783 (b) re-baselined it: `lefthook install` leaves `.claude/settings.json` byte-identical to the committed file, and adapter-portability stays green; `uninstall` is an owner act, followed by restoring the committed file (DEC-712) | `test_w2_05_settings.py`: `test_install_leaves_the_settings_byte_identical_before_and_after_the_owner_s_uninstall_and_restore[lefthook.yml]`, `[the template's hooks file]`; `test_install_from_a_linked_worktree_leaves_both_settings_byte_identical_and_the_owner_s_act_both_clean`; `test_adapter_portability_stays_green_through_install_and_the_owner_s_uninstall_and_restore`. What `uninstall` alone does to the file is lefthook's own behaviour and is not asserted. The state after the owner's act is: `lefthook uninstall`, then `git restore -- .claude/settings.json` in each tree whose file changed. "adapter-portability stays green" also covers the hooks sources it now compares (W2-M281, DEC-805): `test_w2_05_hooks_source.py`, all 10 cases (new; listed under W2-M281 below) |
| **F1**: a planted `GIT_DIR` or `GIT_INDEX_FILE` in a hook's environment reaches no child git call; and (review F1) the staged-secrets gate never passes on an index other than the one being committed | `test_w2_05_planted.py`: `test_the_retrieval_check_under_a_planted_git_dir_measures_and_leaves_the_decoy[the check's declared command]`, `[gov ci checks G1]`; `test_a_staged_secret_under_a_planted_decoy_index_is_refused_naming_the_index[GIT_INDEX_FILE]`, `[GIT_DIR and GIT_INDEX_FILE]` (rewritten); `test_a_clean_index_is_not_refused_for_a_decoy_s_staged_secret[GIT_DIR]`; `test_a_clean_index_under_a_planted_decoy_index_is_refused_naming_the_index` (rewritten); `test_staged_secrets_refuses_an_inherited_index_outside_the_git_directory_naming_it[a secret in that index, the project's index clean]`, `[nothing secret in that index, the project's index clean]`, `[nothing secret in that index, a secret in the project's index]` (new); `test_a_hooked_commit_with_its_index_outside_the_git_directory_and_a_secret_there_does_not_land` (new, through lefthook); `test_read_merge_under_a_planted_git_dir_reads_its_own_repository`; `test_the_containment_check_catches_the_change_whatever_its_environment_holds[a decoy GIT_DIR and GIT_INDEX_FILE]`; the S2 linked-worktree cases, where git itself plants both variables; and (F-A with P-1, DEC-804 items 1 and 3, DEC-807 item 2) the three cases of `test_w2_05_declared_check.py` (new): the `GIT_INDEX_FILE` git exports to the pre-commit hook (relative in the main tree, absolute on `commit -a` and in a linked worktree) reaches no declared check, and no location variable does |
| Edge: a caller that set `GIT_*` on purpose for its own folder | `test_w2_05_planted.py::test_a_hooked_commit_in_a_linked_worktree_scans_the_index_git_gives_it` with `[git commit -a, a secret in a tracked file]`, `[git commit -- <path>, a secret in that file]` and `[git commit -a, nothing secret]` |
| Edge: a check in a linked worktree | the S2 cases; `test_a_declared_check_..._lands_as_staged[a linked worktree, a plain commit]`; `test_install_from_a_linked_worktree_...`; `test_the_guard_hook_refuses_within_its_own_limit_...` |
| Edge: a call in a command, a check and a test helper | command: `gov ci staged-secrets`, `gov ci checks G1`, `gov close`; check: retrieval-regression, containment (W1-03's PostToolUse hook), a check the project declares (`test_w2_05_declared_check.py`); test helper: the ticket's acceptance test that `gov close` runs (`test_gov_close_runs_...`) |

## The covers ids and their tests

| Id | Test |
|---|---|
| **AR-2** | every case of the suite (its four "closes when" lines are S1 to S3, plus the sweep) |
| **W2-M105**: `gov.guard.containment_merge` sets `GIT_NO_LAZY_FETCH` and clears `GIT_TRACE` | `test_read_merge_under_planted_trace_variables_writes_no_trace`; `test_read_merge_in_a_partial_clone_fetches_nothing`; `test_read_merge_under_a_planted_git_dir_reads_its_own_repository` (guard) |
| **W2-M113**: all governance git calls run with pinned configuration and a cleared environment | `test_the_containment_check_catches_the_change_whatever_its_environment_holds[a decoy GIT_DIR and GIT_INDEX_FILE]`, `[trace variables]`, `[a trace setting in the person's git configuration]` |
| **W2-M161**: all subprocesses of close run with a sanitised environment and pinned git configuration | `test_gov_close_runs_its_subprocesses_and_the_ticket_tests_with_a_sanitised_environment` |
| **W2-L160**: git is resolved by absolute path, and the freeze look-up has its own limit, 15 s (DEC-783 item 2) | `test_the_guard_hook_does_not_run_the_git_first_on_path`; `test_the_guard_hook_refuses_within_its_own_limit_when_the_freeze_look_up_hangs` (rewritten for the 15 s limit: a `deny` not before 14.5 s and by 18 s) |
| **W2-M281**: adapter-portability goes red on a planted drift in the template's hooks source (`template/.rulesync/hooks.jsonc`, DEC-783 item 3), compared with the repository's by hook events and matchers, paths normalised (DEC-805) | `test_w2_05_hooks_source.py`: `test_a_drift_in_the_template_s_hooks_source_turns_adapter_portability_red_naming_the_source_and_the_event` with `[an event in the template's source only]`, `[an event in the repository's source only]`, `[an event whose matcher differs]`, `[a matcher in the repository's source only]`, `[a matcher in the template's source only]` (their base pair built from one source and checked green before the plant, DEC-970); `test_a_difference_that_is_not_drift_leaves_adapter_portability_green` with `[only the paths]`, `[only the order of the events]`, `[only the order of the hooks of an event]`, `[only the command wrapper]`; `test_adapter_portability_is_green_over_this_repository_s_two_hooks_sources` |

Not written:

- **W2-L109** (findings grouped by cause) and **W2-M231** (the check and the hand-run generator use the same
  root) state no form these tests could hold them to. They are returned to the lead.
- **W2-M012** is an owner act.
- **F-B** (objects in a folder named by `GIT_OBJECT_DIRECTORY` or by alternates; a git error inside gitleaks) and
  **D-1** (replace refs) are Wave 3 rows W2-M375 and W2-M376 (DEC-807): no case.

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

## The resume's three behaviours (DEC-804, DEC-807, DEC-805, DEC-783 item 2): the cases, and their state on `1814315f106e`

**B1. F-A with P-1: a check the project declares gets no inherited `GIT_INDEX_FILE` (DEC-804 items 1 and 3, DEC-807
item 2).** A hooked commit through lefthook and the project's own `lefthook.yml` in a temporary repository, in three
shapes: the main tree with a plain commit (git exports `GIT_INDEX_FILE=.git/index`, relative), the main tree with
`git commit -a` (`.git/index.lock`, absolute), and a linked worktree with a plain commit (absolute, under
`.git/worktrees/<name>/`). The project declares a G1 check that records the environment it was started with, then
makes a git repository of its own outside the project (`git init`, `git add -A`, `git commit` there). Each case
asserts, in this order:

- the check ran and received no `GIT_INDEX_FILE`, and none of `GIT_DIR`, `GIT_WORK_TREE`, `GIT_COMMON_DIR`;
- the commit landed: one new commit on the branch, its parent the old head, its message the one given;
- its tree is the staged tree (for `commit -a`, the index with `git add -u`, worked out on a copy of the index),
  so there is no deletion and no addition nobody staged;
- no other ref moved and no other commit became reachable;
- the index matches the commit (`git diff-index --cached HEAD` is empty) and names no object the repository does
  not hold (`git ls-files --stage`, then `git cat-file -e` on each object); in a linked worktree, the main tree's
  index is unchanged;
- the check's own repository has its own git directory and holds the check's one commit and one file.

**B2. W2-M281 as DEC-805 decides it.** adapter-portability compares `template/.rulesync/hooks.jsonc` with
`.rulesync/hooks.jsonc` by hook events and matchers, paths normalised. The temporary project is W1-38's adopted
project with its kernel moved to `template/governance/kernel` (this repository's shape), the two hooks sources
written by the case, adapters generated by the installed rulesync from `.rulesync/`, and everything committed. The
check runs through its declared command, as `gov check` runs it. The base pair of the drift cases is built from
one source written in the case (`BASE_HOOKS`, since DEC-970's P-W2-05-DRIFT-BASE; see "P-W2-05-DRIFT-BASE" below),
whatever this repository's live sources hold: the template's events and matchers as DEC-805 item 2 leaves them
(`preToolUse`; `postToolUse` and `postToolUseFailure`, `Bash`; `sessionStart`, `compact|clear|resume`; `stop`;
`preCompact`; `subagentStop`), each with the kernel's hook of that name. The repository's side has the repository's
path form with the pinned interpreter around each hook; the template's side has the template's path form with
`python3`. The two differ in paths and in the wrapper, never in events, matchers or order. Each case first requires
the check green over that pair alone (the control), then plants its drift in the template's source and commits it:

- **Drift is red,** with a finding that names `hooks.jsonc` and the event (matched without regard to case in the
  printed finding):
  - an event only in the template's source (`userPromptSubmit`);
  - an event only in the repository's (`subagentStop`);
  - a matcher that differs (`postToolUseFailure`, `Bash|Edit` against `Bash`);
  - a matcher only in the repository's (`sessionStart`);
  - a matcher only in the template's (`preToolUse`, `Bash`).
- **Not drift is green** (exit 0, no finding). Each case varies one thing alone, from the repository's source:
  - only the paths (the template's form, `governance/kernel/hooks/`);
  - only the order of the events (reversed);
  - only the order of the hooks of an event (two `postToolUse` hooks, `Bash` and `Edit|Write`, the other way round;
    the repository's source holds both, and the adapters are generated from it). Since ACT 1 the two hooks are
    written in the case, not taken from the live source (see "ACT 1 and the hooks sources" below);
  - only the command wrapper (the template's `python3` commands, with the repository's paths, in the repository's
    events, order and matchers).
- **This repository's two sources,** byte for byte, are green. As its own step, the case reads the template's
  `sessionStart` matcher and requires the repository's, `"compact|clear|resume"` (DEC-805 item 2). The same project
  with that matcher taken out of the template's source must then be red, naming `hooks.jsonc` and `sessionStart`,
  so the green comes from the comparison, not from the absence of one.

**B3. DEC-783 item 2: the freeze look-up's own limit is 15 s.** The rewritten case keeps its setup: the worktree's
`HEAD` in its git directory is a fifo, so the guard's `git rev-parse --git-common-dir` waits. The hook, started as
W1-02's support starts it (cut off at 20 s), must answer `deny` not before 14.5 s and by 18 s. The tolerance:

- the lower bound is the 15 s limit less 0.5 s for the clocks: an answer before it did not wait for the look-up up
  to its limit;
- the upper bound gives the hook's start and its answer after the limit 3 s. It is 1 s before 19 s, the earliest
  the hook deadline's answer comes in W1-02's deadline cases, and 2 s before the hook's 20 s deadline (DEC-580).

An answer after 18 s is the hook deadline's, not the look-up's.

| Case | Kind | State on `1814315f106e` (seen) |
|---|---|---|
| `test_w2_05_declared_check.py::test_a_declared_check_that_runs_git_in_a_repository_of_its_own_gets_no_index_and_the_commit_lands_as_staged[the main tree, a plain commit]` | new | **red:** the declared check received `GIT_INDEX_FILE=<repo>/.git/index`, made absolute |
| `...[the main tree, git commit -a]` | new | **red:** it received `GIT_INDEX_FILE=<repo>/.git/index.lock` |
| `...[a linked worktree, a plain commit]` | new | **red:** it received `GIT_INDEX_FILE=<repo>/.git/worktrees/wt/index` |
| `test_w2_05_hooks_source.py::test_a_drift_in_the_template_s_hooks_source_turns_adapter_portability_red_naming_the_source_and_the_event[an event in the template's source only]` | new | **red:** adapter-portability stayed green (exit 0, no finding): it does not compare the hooks sources |
| `...[an event in the repository's source only]` | new | **red:** the same |
| `...[an event whose matcher differs]` | new | **red:** the same |
| `...[a matcher in the repository's source only]` | new | **red:** the same |
| `...[a matcher in the template's source only]` | new | **red:** the same |
| `test_w2_05_hooks_source.py::test_a_difference_that_is_not_drift_leaves_adapter_portability_green[only the paths]`, `[only the order of the events]`, `[only the order of the hooks of an event]`, `[only the command wrapper]` | new | **green:** the check compares no hooks source today, so nothing in them can turn it red. These cases hold the comparison to come against an over-strict reading |
| `test_w2_05_hooks_source.py::test_adapter_portability_is_green_over_this_repository_s_two_hooks_sources` | new | **red, for the missing matcher:** the check is green over the two files (it does not compare them), then `template/.rulesync/hooks.jsonc`'s `sessionStart` matchers are `[None]`, not `["compact\|clear\|resume"]`. After the comparison alone it would be red at its first step (a finding for `sessionStart`); after the matcher line alone, at its last (the drift not seen) |
| `test_w2_05_planted.py::test_the_guard_hook_refuses_within_its_own_limit_when_the_freeze_look_up_hangs` | rewritten | **red:** decision `timeout` after 20.0 s: the look-up has no limit of its own |

Checked by the designer outside the suite, with a scratch stand-in that was not committed: the B1 assertions after
the first two pass in all three shapes when the declared check drops every `GIT_*` variable before its git calls.
When it hides the variables from its record but its git calls keep them, the commit does not land: `error: invalid
object ... for 'own.txt'`, `Error building trees`. In that run gitleaks, inside `gov ci staged-secrets`, also printed
`fatal: unable to read <object>` and still answered `"secrets": 0`. That is F-B's second half, a Wave 3 row (DEC-807).

## Red until another ticket merges (DEC-777): both tickets have merged

These cases depend on files of W2-50 and W2-53. Both have merged into this branch (`1814315f106e`), but this
ticket's own change to those files is not made yet: the resume makes it. On `1814315f106e` all 5 are red:

| Case | Was red until | File | Seen on `1814315f106e` |
|---|---|---|---|
| `test_w2_05_planted.py::test_gov_close_runs_its_subprocesses_and_the_ticket_tests_with_a_sanitised_environment` | **W2-53** merges | `src/gov/close/**` (the close's test run and its git calls) | **red:** the planted `GIT_DIR`, `GIT_INDEX_FILE`, `GIT_TRACE`, `GIT_TRACE2`, `GIT_TRACE2_EVENT`, `GIT_TRACE_PACKET` and `GIT_TRACE_SETUP` reached the ticket's test run; the close itself answered `ok: true` |
| `test_w2_05_planted.py::test_the_guard_hook_does_not_run_the_git_first_on_path` | **W2-50** merges | `src/gov/guard/decide.py` (the guard's `git rev-parse --git-common-dir`) | **red:** the guard ran the git first on `PATH`: `-C <project> rev-parse --git-common-dir` |
| `test_w2_05_planted.py::test_the_guard_hook_refuses_within_its_own_limit_when_the_freeze_look_up_hangs` (rewritten, B3) | **W2-50** merges | `src/gov/guard/decide.py` (the freeze look-up) | **red:** decision `timeout` after 20.0 s (seen before and after the rewrite) |
| `test_w2_05_planted.py::test_the_containment_check_catches_the_change_whatever_its_environment_holds[trace variables]` | **W2-50** merges | `src/gov/guard/decide.py` (its mirror-path git call) | **red:** the planted `git_trace`, `git_trace2` and `git_trace2_event` were written |
| `test_w2_05_planted.py::test_the_containment_check_catches_the_change_whatever_its_environment_holds[a trace setting in the person's git configuration]` | **W2-50** merges | the same | **red:** `~/.gitconfig`'s `trace2.eventTarget` (`user-config-trace2`) was written |

On `aa676b9f` these were the run's only 5 red cases. On `0983be4c` they were still red, beside the 9 cases of the
review's F1 and F2. The lead found the two containment parametrizations in the earlier verification. Two runs
agree with that finding from outside, on `0983be4c` and again on `1814315f106e`:

- in both cases the only git calls that wrote the planted trace targets were `git -C <root> rev-parse
  --git-common-dir`, twice;
- the `[trace variables]` case shows them in `GIT_TRACE`, and the configuration case in the `trace2.eventTarget`
  events;
- the guard-hook case reports the same call as the guard's.

No case depends on the files of W2-54, W2-03, W2-16 or W2-20.

## Skips

A case that needs an absent tool skips with the reason stated (`skip_without`). On this machine nothing is
absent, and nothing skips.

| Tool | Cases that skip without it |
|---|---|
| `git` | every case that uses the box |
| `lefthook` | the S3 cases; the lefthook case of S2; the lefthook case of F1 (an index outside the git directory); the 3 declared-check cases (F-A) |
| `gitleaks` | the staged-secrets cases; the lefthook cases of S2 and F1; the 3 declared-check cases (F-A) |
| `rulesync` | `test_adapter_portability_stays_green_through_install_and_the_owner_s_uninstall_and_restore`; the 10 hooks-source cases (W2-M281), with the same rule (`skip_without("rulesync")`, then W1-38's `rulesync_version()`) |
| `sqlite_vec` | the retrieval-regression cases (the `tiers` fixture) |

## Readings the tests rest on

P-1 and P-2 were returned as packages. DEC-783 accepted P-3 and P-4, answered P-A and gave P-2's value
(item 2). DEC-804 item 3 accepted P-1.

- **P-1: an honoured versus a planted `GIT_INDEX_FILE`. Accepted by the owner (DEC-804 item 3):** an inherited
  `GIT_INDEX_FILE` is honoured only for git calls in the project root; a program that may start git elsewhere gets
  no index.
  - A value that is git's own index of the project is honoured for git calls in the project root. Examples are
    `index.lock` for `commit -a`, `next-index-*.lock` for `commit -- <path>`, the relative `.git/index` in the main
    tree, and the worktree's own index in a linked worktree.
  - Any other value is cleared.
  - A check the project declares may start git anywhere, so it gets no `GIT_INDEX_FILE` at all, in every shape
    (`test_w2_05_declared_check.py`, F-A).

  What stays as it is:
  - git's own index is the one the staged-secrets gate scans on such a commit (`_on_purpose`, the S2 cases);
  - an inherited index that is not git's own index of the project is refused by the gate, and the refusal names it
    (the review-F1 cases). The gate never answers on an index other than the one being committed: clearing the
    index there would let the secret staged in the commit's index pass and the commit land;
  - a planted `GIT_DIR` or `GIT_INDEX_FILE` reaches no child git call (the decoy cases).
- **P-2: the freeze look-up's own limit. Decided by the owner (DEC-783 item 2): 15 s.** The rewritten case
  asserts the guard's `deny` (DEC-580: the guard answers refuse) not before 14.5 s and by 18 s. That makes it the
  look-up's own refusal, not the hook deadline's at 20 s (the tolerance is under "The resume's three behaviours").
  Before the decision the case took "below the hook's 20 s deadline" and asserted an answer within 18 s.
- **P-3: the template's hooks file. Accepted by the owner (DEC-783).** The ticket's allowed path is
  `template/lefthook.yml`, but the tree holds `template/lefthook.yml.jinja`. The template's hooks file is
  `template/lefthook.yml.jinja`, which stays untouched. The template case takes that file.
- **P-4: W2-M281. Accepted by the owner (DEC-783).** "A planted drift in the template hooks source" is read as
  the Claude Code hooks source `template/.rulesync/hooks.jsonc`. DEC-805 then defined the drift: hook events and
  matchers, compared with `.rulesync/hooks.jsonc`, with paths normalised. Its cases are in
  `test_w2_05_hooks_source.py`.
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

## ACT 1 and the hooks sources (2026-10-31): the order case built from hooks of its own

`Rewrite-Reason: DEC-953 item 2 (ACT 1): the repository's hooks source has no postToolUse; the case's construction,
not its expectation`. Ticket `DAEO-0z8c`, written by its independent test designer on `w2/W2-05-tests` from the
ticket's head `f217353e59fa`, under DEC-906's repair batch.

- **Why.** The owner's ACT 1 (`6c36c7b5`, DEC-953 item 2) took `postToolUse` and `postToolUseFailure` out of the
  repository's `.rulesync/hooks.jsonc`; the template's source keeps both. `[only the order of the hooks of an
  event]` built its two hooks from the repository's first `postToolUse` hook, and failed in its own construction
  (`KeyError: 'postToolUse'`) before the check ran.
- **Now.** The case's two hooks are written in the case (`ORDER_HOOKS`: `Bash` with `posttooluse.py`, then
  `Edit|Write` with `precompact.py`, both in the repository's path form), and `ORDER_EVENT` (`postToolUse`) is set
  in both sources alike: the repository's holds them in that order, the template's the other way round. Every other
  event is the live repository source's, the same in both. Held as before: exit 0 and no finding; the two sources
  are written differently (the case's own guard against a pair written the same). The id is unchanged.
- **The other cases of the file that read the live source** do not fail in their construction for this reason, and
  are unchanged: `[only the paths]`, `[only the order of the events]` and `[only the command wrapper]` vary the live
  repository source alone (the wrapper case takes the template's commands only for the repository's events), and
  the five drift cases plant into the template's source events it still carries. What the drift cases reach now
  that their base pair differs in two events is returned to the lead as a package (P-W2-05-DRIFT-BASE): green, but
  `[an event whose matcher differs]` is green through the event `postToolUseFailure` being in the template's source
  only, not through its matcher. DEC-970 decided it; the drift cases' base pair is now built from one source (see
  "P-W2-05-DRIFT-BASE" below).
- **`test_adapter_portability_is_green_over_this_repository_s_two_hooks_sources` is red, and stays red until the
  orchestrator's decision (package H).** It compares this repository's two files byte for byte, and since ACT 1 they
  differ in two events: `HOOKS_EVENT_DIFFERS` for `postToolUse` and `postToolUseFailure`, "only in
  template/.rulesync/hooks.jsonc". That is a decision about the sources, not about the case, and the case is not
  changed.

| Case | At `f217353e59fa`, before | After |
|---|---|---|
| `test_w2_05_hooks_source.py::test_a_difference_that_is_not_drift_leaves_adapter_portability_green[only the order of the hooks of an event]` | **red:** `KeyError: 'postToolUse'`, in the case's construction | **green** |
| `test_w2_05_hooks_source.py::test_adapter_portability_is_green_over_this_repository_s_two_hooks_sources` | **red:** two `HOOKS_EVENT_DIFFERS` findings (ACT 1) | **red, the same** (package H) |
| the other 8 cases of the file | green | green |

## P-W2-05-DRIFT-BASE (2026-10-31): the drift cases' base pair from one source

`Rewrite-Reason: DEC-970 (P-W2-05-DRIFT-BASE); DEC-953 item 2 (ACT 1): the base pair differed by events, so a drift
case passed without its plant; the construction, not the expectation`. Ticket `DAEO-0z8c`, written by a fresh
independent test designer on `w2/W2-05-tests` from the ticket's head `0cfa8684f720`.

- **Why.** The five drift cases built their base pair from this repository's two live sources. Since ACT 1
  (`6c36c7b5c7fa`, DEC-953 item 2) these differ in two events: `postToolUse` and `postToolUseFailure` are in the
  template's source only. So the check was red on the base pair before anything was planted. With every plant made
  to do nothing (a scratch plugin, not committed), at `0cfa8684f720`: `[an event whose matcher differs]` **passed**
  (its event, `postToolUseFailure`, was already named by a finding), and the other four went red at their naming
  step only, after the check had already gone red on the base pair. The cases did not show what they claimed.
- **Now.** The pair is built from one source written in the case (`BASE_HOOKS`, see B2 above), and neither live
  file is read. The repository's side has the repository's path form and the pinned interpreter; the template's
  side has the template's path form and `python3`. The events, matchers and order are the same on both sides.
  Each case:
  1. builds the project on that pair and requires the check green (exit 0, no finding): the control;
  2. plants its drift in the template's source and commits it;
  3. requires the check red, with a finding that names `hooks.jsonc` and the event, as before.

  The plants, the five ids and the expectation are unchanged. Each plant changes exactly the one event its case
  names (checked by a scratch script): `userPromptSubmit`, `subagentStop`, `postToolUseFailure`, `sessionStart`,
  `preToolUse`.
- **The mutation check, after the change.** With every plant made to do nothing, all five cases pass their control
  and fail at their last step: "adapter-portability stayed green on ... it did not see the drift". Each case is now
  red only because of its own plant.
- **Unchanged:** the four not-drift cases, and `test_adapter_portability_is_green_over_this_repository_s_two_hooks_sources`.
  The last is still red (two `HOOKS_EVENT_DIFFERS` findings, ACT 1). That is a decision about the sources, held by
  the owner (package H), and the case stays as it is.

| Case | At `0cfa8684f720`, before | After |
|---|---|---|
| `test_w2_05_hooks_source.py::test_a_drift_in_the_template_s_hooks_source_turns_adapter_portability_red_naming_the_source_and_the_event[an event in the template's source only]`, `[an event in the repository's source only]`, `[an event whose matcher differs]`, `[a matcher in the repository's source only]`, `[a matcher in the template's source only]` | green; with nothing planted, `[an event whose matcher differs]` still green and the other four red only at the naming step | green, the control green first; with nothing planted, all five red: "stayed green" |
| `test_w2_05_hooks_source.py::test_a_difference_that_is_not_drift_leaves_adapter_portability_green` (4 cases) | green | green |
| `test_w2_05_hooks_source.py::test_adapter_portability_is_green_over_this_repository_s_two_hooks_sources` | **red:** two `HOOKS_EVENT_DIFFERS` findings (ACT 1) | **red, the same** (package H) |

W2-05 whole, after the change, in a launched session: 48 cases, 40 passed and 8 failed. Of the 8:

- the hooks-source case above (package H);
- six that fail for a reason of the session, not their own:
  - five retrieval-regression cases, with no embedder (`Ollama is unavailable`, hit@5 0.0): `[a linked worktree]`,
    `[the main tree]`, `test_a_commit_in_a_linked_worktree_through_lefthook_and_the_project_hooks_file`, and
    `test_w2_05_planted.py`'s two `[the check's declared command]`, `[gov ci checks G1]`;
  - the code-index case, where `gov rebuild` started no code-index tool;
- `test_w2_05_sweep.py::test_every_file_of_the_source_that_starts_git_is_named_in_the_sweep`. The sweep record
  does not name `src/gov/release/__init__.py`, which came into the branch with `0cfa8684f720`'s merge of
  `w2/integrate` (W2-16). This change does not reach it, and it is returned to the lead.

## The review's R4-1 (2026-10-31): the nightly's bisect step gets the environment of the run that found the red

Ticket `DAEO-0z8c`. Written by a fresh independent test designer on `w2/W2-05-tests` from the ticket's head
`ba807a032603`, before the fix (DEC-136: the review found a behaviour the cases missed). Sources: KPI success 1 (a
test helper that runs git in another folder clears the inherited `GIT_*`; W2-M161), the failure KPI, P-1 (DEC-804
item 3), DEC-970's W2-05 line (the nightly's bisect pinned as the close's test runs are). No implementation file of
the ticket was read; the nightly's mechanics were read on `w2/integrate` (`git show w2/integrate:src/gov/close/nightly.py`).

- **What git does (measured, git 2.43.0):** `git bisect run <cmd>` puts `GIT_DIR` (the git directory of the tree it
  runs in: the night clone's, under the project's `.git/worktrees/`), `GIT_EXEC_PATH` and `GIT_PREFIX` into the
  environment of `<cmd>`, whatever the caller cleared. A test that runs git in a folder of its own with the
  environment it inherits then acts on the clone and, through its common git directory, on the project.
- **The project, built from scratch** in the case's temporary folder: the main tree on `work`; `main` checked out
  nowhere, holding the person's own commit; on `work` the tool's test (green), a committed green night's record
  naming it, `harmless one`, `the culprit` (the test's data says `BROKEN`), `harmless two` (the head). The tool's test
  makes a repository of its own in its `tmp_path` (`git init -b main`, a commit, `checkout -b side`, a commit,
  `checkout main`, `merge side`), requires its two commits there, then reads the data. At each run it adds the commit
  it runs at (`stage.txt`) and the names of the `GIT_*` variables it sees (never a value) to a file outside every
  repository.
- **The night, as the product runs it:** `python3 -m gov.close.nightly work --root <project> --json`, this worktree's
  `src/`, W1-30's sandbox environment (no `GIT_*` of the caller); a real `git bisect run`, no stand-in. It runs once
  for the three cases (a module fixture), with the project's state read before and after it by the suite's clean git.
  A bisect over the four commits after the green night needs at most three steps: the night is stopped, with every
  process it started, once the tool's test has run more than 20 times (its bisect does not converge), or at 240 s.
- **Each case first requires that a bisect step ran the tool's test,** so that none is green for want of a bisect.

| Case (`test_w2_05_bisect_step.py::`) | Requires | Red on `ba807a032603` because (seen; 3 failed, 29 s and 47 s, two runs) |
|---|---|---|
| `test_the_night_s_bisect_leaves_every_branch_head_and_reflog_of_the_project_as_it_was` | every ref, the reflog of every branch and of HEAD, HEAD (its branch and commit), the main tree's index, the commits reachable from refs and reflogs, and `.git/config` as before the night | the project's refs moved: `refs/heads/main` moved onto a foreign merge commit (its reflog 2 -> 3 entries), a foreign branch `refs/heads/side` appeared, 20 commits outside the project's history became reachable, and `.git/config` went from `bare = false` to `bare = true` (the step's `git init` re-initialised the project's git directory). The night was stopped after 21 runs of the test |
| `test_the_night_s_bisect_names_the_commit_that_made_the_test_red` | the night ends, red (exit 3, `NIGHTLY_RED`), and its bisect package for the tool's test names the culprit as the first bad commit | the night did not end: the bisect did not converge (each step's test made new commits in the range it bisects), stopped after the tool's test had run 21 times. Without the stop it ran 554 steps in 300 s (a first draft's limit). No first bad commit was named |
| `test_each_bisect_step_s_test_sees_only_the_git_variables_of_the_run_that_found_the_red` | each step's `GIT_*` names are among `GIT_CONFIG_GLOBAL`, `GIT_CONFIG_NOSYSTEM`, `GIT_NO_LAZY_FETCH` and the same as the run that found the red | the run that found the red (and the run alone) saw exactly the three; every one of the 19 steps saw `GIT_DIR`, `GIT_EXEC_PATH` and `GIT_PREFIX` beside them |

**Can they go green?** Checked by the designer outside the suite, with a scratch script that was not committed and
touched no product file: the same project, a real `git bisect run` driven as `w2/integrate`'s nightly drives it (a
detached worktree of the head, `bisect start <head> <green>`, `bisect run` of the step script), with the step taking
every `GIT_*` but the three out of its environment before pytest. Then: no change to the project's state; the culprit
named as the first bad commit; the two steps (at `harmless one` and at the culprit) saw the three names only; four
runs of the test in all.

W2-05 has 51 cases with these three.
