# W2-23 acceptance tests: adoption safety on a planted repository

Ticket `DAEO-kmcr` (W2-23), profile FULL. Written by an independent test designer (MR-3) before the implementation,
from the ticket's KPI lines (S1-S7, F1) and its `## Interface` (items 1-7, DEC-1052; the CTO's delegated decision,
DEC-1112 (3)), without reading the implementation (DEC-820, DEC-963). Sources: DEC-729, DEC-1052, DEC-954, DEC-315,
DEC-1112; the rows behind the KPIs in `governance/project/bootstrap.md` (lines 2344-2347, 2352-2357, 2362, 2393)
and `docs/plan/WAVE_2_LIST.md` (W2-H035, W2-H036, W2-H050, W2-M216-W2-M226, W2-M229, W2-M232, W2-M307, W2-M312).

## What the tests reach

Every case plants its own git repository under pytest's `tmp_path` (`w2_23_support.plant_project`): the programme's
own `CLAUDE.md`, `AGENTS.md` and `.claude/settings.json` (each with lines of its own), tracked files, ignored
untracked files (`local/scratch.md`, `settings.local`), a path map in the kernel schema's shape (one namespace;
`vault/` held by none), the template's `.gitleaks.toml` and a `.gitignore` naming `.gov-runtime/` unless a case
leaves them out; and, for S6, the same repository in a folder named `EXAMIN APP` and at a path without a space. Each
case has a planted empty `HOME` and `TMPDIR` (`w2_23_support.make_box`).

The tool is driven as its callers drive it: `python -m gov.cli.main adopt --lite --stage A<n> ... --json` and
`python -m gov.cli.main adapters generate --json`, as child processes, judged by exit code, the API-0002 envelope
(refusal code, message, details) and the repository afterwards (HEAD, index, files, refs). The A5 verdict is a
record the case commits with `Role: independent-auditor`, as W1-41's tests do. Nothing of the implementation is
imported, so the suite collects while `gov.adopt.safety` and `gov.adapters.command` do not exist.

How a case plants a condition:

- **A failed stage or batch:** a pre-commit hook in the planted repository (`w2_23_support.install_hook`) refuses
  the commit that stages a given path (stage A1's record; a batch's target or deleted file).
- **The owner's untracked material met by a restore:** a stage starts on a clean tree, so the owner's untracked
  files a restore can meet are made while the run is under way. The same hook writes them at one of the run's
  commits: `drafts/user-draft.md`, `user-dir/sketch.txt` (an untracked directory) and `user-clone/` (a nested git
  repository with a file: git lists it as one untracked directory).
- **A killed batch (S4):** the hook sends SIGKILL to git's parent, the process running the stage, at batch 2's
  commit and refuses that commit: the batch is staged and not committed, between its steps. The case asserts the
  kill happened (exit -9, the batch staged) before judging the resume.
- **A target no namespace holds (S7, A6):** the path map is narrowed and committed after A5.
- **S3's citations:** one file per listed form (see below), all citing the store `legacy/memory/` (ids LEG-001,
  LEG-002), which the proposal retires as a memory store.

## How to run

```
env HOME=<an empty folder> PYTHONPATH=<worktree>/src TMPDIR=<a writable temporary folder> \
  python3 -m pytest tests/acceptance/W2-23 -q -p no:cacheprovider -o tmp_path_retention_policy=failed \
  -m "not local_only" -k "not real and not green_here and not time_limit"
```

- **The code under test is the worktree's own `src/` (DEC-732):** every child gets the `src/` of the repository this
  folder stands in (from the support file's own location) first on its `PYTHONPATH`; no worktree path is written.
- **`rulesync` 24.0.0 on PATH** for S2 (the user's `~/.local/bin` is added to the children's PATH).
- No network, no model (the embedder's address is a dead port, no `ollama` program), no GPU. About 80 s here.
- Nothing is serial-only by kind of this folder's own; the move cases ask the codebase-memory daemon (see below).

### Known limit: the move cases cannot run in a launched session

"A3 with a move needs `/tmp/gov-cbm-<uid>` writable, so the move cases cannot run in a launched session"
(bootstrap.md 2396, W2-M226). These cases are written normally (no skip, no `local_only`) and fail in the launch
sandbox at stage A3 with `ADOPT_CODE_GRAPH_UNREADABLE`, whatever the code; run `gov accept` outside the sandbox:

- `test_w2_23_rollback.py::test_s1_a_failed_move_batch_keeps_the_owners_untracked_files_and_removes_its_target`
- `test_w2_23_setup.py::test_s5_after_the_set_up_a3_with_a_move_and_a8_do_not_refuse_for_either`
- `test_w2_23_unheld.py::test_s7_a6_refuses_a_target_the_path_map_no_longer_holds_before_any_batch`
- `test_w2_23_unheld.py::test_s7_a3_refuses_moves_to_unheld_targets_naming_each_before_its_record` (in the sandbox
  only if the implementation checks targets after the code graph; Interface item 4 does not fix the order)

They ask the codebase-memory daemon: the lead may list them as `serial: daemon` in `tests/acceptance/serial-only.txt`.

### Cases out of CI

- `test_w2_23_space.py::test_s6_retrieve_and_context_exit_alike_at_a_path_with_a_space` is marked `local_only`:
  no `gov retrieve` or `gov context` runs in the launch sandbox (DEC-1065). It needs no model (planted `HOME`, dead
  embedder address) and runs anywhere else.

## The interface the tests rely on (the ticket's `## Interface`, as written)

| What | Value | Item |
|---|---|---|
| The rollback | the restore a failed stage or batch runs; only paths the tool wrote are deleted; an untracked directory does not raise | 1 |
| The resume | `gov adopt --lite --stage A6` again; the A6 record at HEAD with `status: failed`, `failed_batch: <n>`, `batches` (each with `batch`, `commit`, `artefacts` with a `disposition` for a deleted file); refs `refs/gov/adoption/rollback/<run-id>/batch-<n>`; refusal `ADOPT_BATCH_FAILED` | 2 |
| The set-up | A0's record commit adds `.gitleaks.toml` (the bytes of `template/.gitleaks.toml`) and `.gov-runtime/` to `.gitignore`; an existing `.gitleaks.toml` untouched | 3 |
| The unheld target | refusal `ADOPT_TARGET_UNHELD` naming each target, from A3 before its record and from A6 before any batch | 4 |
| Adapter generation | `gov adapters generate`; one block `<!-- gov:generated begin -->` ... `<!-- gov:generated end -->` after the programme's lines; settings merged key by key, programme first; the programme's `env` entry first and **no** `env` key matching `AUTO_?COMPACT` (DEC-838; P-W2-23-4 (b)) | 5 |
| The citation forms | bootstrap.md 2362's list; found = named by the A8 refusal's message or its `citers` | 6 |
| A path with a space | every `COMMANDS` name and discovered command module with `--help`; status, doctor, adopt A0 (retrieve, context: `local_only`); the hooks of `template/.rulesync/hooks.jsonc` run by `/bin/sh -c` with `CLAUDE_PROJECT_DIR` holding the space | 7 |

S3's planted forms (`w2_23_support.LISTED_FORMS`): `rule-LEG-001` (a `-` before the id); `legacy\memory\...`
(backslashes); `legacy%2Fmemory%2F...` (URL-encoding); `Legacy/Memory/Decisions/Leg-001.md` (another letter case);
`legacy/memory/` + newline + `decisions/leg-001.md` (split across lines); `legacy/memory/` (the store's folder only);
`legacy/memory/**/*.md` (a glob); `../decisions/leg-001.md` (`../` and only the tail); `LEG-001` in the prose of
record DEC-401 (an id in a record's prose). **The unlisted form, the test designer's choice: the store's path written
in base64** (`.rulesync/rules/cite-base64.md`): it must be the only one not found.

Untested and named (Interface gaps, in the return's `proposed_decisions`): (the auto-compact entry gap is closed:
P-W2-23-4 (b), no compaction threshold, DEC-838); whether S3's "folder or glob" means both forms
(both are planted); what an S4 resume record says once done.

## The map

| KPI | Tests | Expected red reason (today's code) |
|---|---|---|
| S1: rollback never deletes an untracked file it did not create | `test_w2_23_rollback.py::test_s1_a_failed_stage_commit_keeps_the_owners_untracked_files_and_removes_its_record`, `test_w2_23_rollback.py::test_s1_a_failed_move_batch_keeps_the_owners_untracked_files_and_removes_its_target` | the restore deletes the owner's untracked files and the nested clone; the move case fails at A3 in the sandbox (known limit) |
| S2: adapter generation merges the programme's three files in order | `test_w2_23_adapters.py::test_s2_claude_and_agents_keep_every_programme_line_in_order_then_one_generated_block`, `test_w2_23_adapters.py::test_s2_a_second_generation_replaces_the_block_in_place_and_leaves_the_programme_lines`, `test_w2_23_adapters.py::test_s2_settings_keep_the_programmes_keys_and_entries_in_order_with_generated_ones_after`, `test_w2_23_adapters.py::test_s2_no_instruction_file_is_the_generated_file_alone` | `gov adapters` is no command: usage error, exit 2 (invalid choice) |
| S3: the A8 proof finds every listed citation form | `test_w2_23_citations.py::test_s3_the_a8_proof_finds_every_listed_form_and_only_the_unlisted_one_is_not_found`, `test_w2_23_citations.py::test_s3_with_only_the_unlisted_form_planted_the_proof_finds_no_citer` | the proof finds none of the nine planted citations and A8 retires the store; the control passes today |
| S4: a failed or killed batch leaves a resumable record, nothing staged | `test_w2_23_resume.py::test_s4_a_batch_failing_at_its_third_step_commits_a_record_and_the_stage_resumes_there`, `test_w2_23_resume.py::test_s4_a_batch_killed_between_its_steps_is_unstaged_and_the_stage_continues_there`, `test_w2_23_resume.py::test_s4_after_a_killed_batch_anything_else_staged_is_refused_by_name_and_left_as_it_is` | no A6 record is committed after the failed batch; after the kill the next A6 refuses `ADOPT_TREE_NOT_CLEAN`; the third case passes today (a guard: never reset) |
| S5: a project without the gitleaks file or the ignore line is set up at A0 | `test_w2_23_setup.py::test_s5_a0_writes_the_template_gitleaks_and_the_ignore_line_in_its_record_commit`, `test_w2_23_setup.py::test_s5_an_existing_gitleaks_is_never_touched_while_the_ignore_line_is_added`, `test_w2_23_setup.py::test_s5_after_the_set_up_a3_with_a_move_and_a8_do_not_refuse_for_either` | A0 writes neither `.gitleaks.toml` nor the ignore line; the move case fails at A3 in the sandbox (known limit) |
| S6: every command and hook works at a path with a space | `test_w2_23_space.py::test_s6_every_command_answers_help_alike_at_a_path_with_a_space`, `test_w2_23_space.py::test_s6_the_read_invocations_exit_alike_at_a_path_with_a_space`, `test_w2_23_space.py::test_s6_retrieve_and_context_exit_alike_at_a_path_with_a_space`, `test_w2_23_space.py::test_s6_every_kernel_hook_exits_alike_with_a_space_in_the_project_dir` | none seen: these pass on today's code here (a pin; the retrieve and context case is `local_only`, not run here) |
| S7: a move to an unheld target is refused before it runs | `test_w2_23_unheld.py::test_s7_a3_refuses_moves_to_unheld_targets_naming_each_before_its_record`, `test_w2_23_unheld.py::test_s7_a6_refuses_a_target_the_path_map_no_longer_holds_before_any_batch` | no `ADOPT_TARGET_UNHELD`: A3 goes on to the code graph (here `ADOPT_CODE_GRAPH_UNREADABLE`; outside, the move is accepted) and A6 runs the batch |
| F1: instruction files and untracked files survive an adoption and its rollback | `test_w2_23_rollback.py::test_f1_instruction_and_untracked_files_survive_an_adoption_ending_in_a_rollback` | the rollback of the failed batch deletes the owner's files made during the run (their sha256 becomes None) |
