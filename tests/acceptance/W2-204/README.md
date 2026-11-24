# W2-204 acceptance tests: the memory measure on any adopted repository, by product commands (DAEO-ma4q, FULL)

Written by the independent test designer (MR-3, DEC-963) from the ticket's KPI lines (S1 to S12, F1 to F4) and its
Interface (I1 to I6), on the base `a3accf8c4` (the ticket commit on `bfde928f5`), before any implementation. The
module's code as it stands on the base was read to learn today's lines and files (`PREFLIGHT.json`, `DROPS.json`,
`DECLARATION.json`, `FIGURES.json`, the ledger); nothing here is built on a guess of the new code.

## How the suite runs

- **Public interfaces only:** `python3 -m gov.cli.main memaudit <step>` (`gov memaudit`) and `python3 -m gov.memaudit
  <step>` as child processes, their lines and exit codes, the files they write; `gov.memaudit.config.load` and
  `gov.memaudit.EXIT` (named by I2 and I3) in process; the two files `governance/project/memory-audit.yaml` and
  `template/governance/kernel/schemas/memory-audit.schema.json`, read and validated with `jsonschema`.
- **Everything is planted** under pytest's temporary folder: a second repository ("Second Harbour", `git init`), a sets
  root, a planted `HOME`, a transcripts folder, a runs folder. No real writer, checker, reader or grader; no measure of a
  true store; nothing under `~/gov-os-eval` or `~/gov-os-runs` is opened (F1 has its own cases).
- **The fakes are W2-171's**, loaded by path and never edited: `tests/acceptance/W2-171/fake_gov.py` (the pinned `gov`),
  `fake_claude.py` (the reader and the graders), `w2_171_world.py` (`child_env`, `git`, `install_script`, `snapshot`,
  the planted register, the Gov OS-shaped world of S6, S9 and S11) and `w2_171_scenario.py` (`calls_for`, the `clean`
  scenario); W2-170's `w2_170_open_log.py` logs a step's file accesses (F1). `rebuild_stub.py` (this folder) is the
  `--rebuild-cmd`: it writes the clone's `.gov-runtime/store.db` (a fingerprints row at the clone's HEAD) and logs where
  it ran.
- **`MEMAUDIT_CONFIG`** is removed for every case of this folder (`conftest.py`): a repository is judged by its own
  file. The trial form is tested where a case passes the variable to the child itself (S3, S6, S9, S11); `World.run`
  drops it from every other child's environment.
- **The planted runs are built once per session** (`w2_204_stages.py`: a file lock in pytest's shared base folder, one
  build between xdist's workers) and then only read: `right`, `misses`, `void`, `round2`, `stopped-thin`,
  `stopped-heavy`, `govos`. A build asserts nothing of the product: it records each call (exit code, output) by a label,
  and the cases assert on the record.
- **Counts only (F3):** every planted question, gold answer, answer and note sentence holds a word found nowhere else
  (`quorblat…`, `gildenfrum…`, `brindlewex…`, `snarkelwump…`, each with the half's letter).
- No network, no model, deterministic. Run: `TMPDIR=$(mktemp -d) PYTHONPATH=<tree>/src python3 -m pytest
  tests/acceptance/W2-204 -q -p no:cacheprovider -n auto` (through the heavy slot), or `gov accept W2-204`.

## The second repository

`governance/project/memory-audit.yaml` at its audit commit: `repository: Second Harbour`, `half_size: 40`; categories
decision 6, harbour-task 4, berth-spec 4, tide-scenario 3, pilot-report 3, exact-string 4, callers 4, code-paraphrase 4,
multi-file 3, failure-memory 3, history 1, nonexistent-id 1; domains decisions (`records/decisions.md`), harbour-tasks
(`records/tasks/**`), berth-specs (`records/specs/**`), pilot-reports (`records/reports/**`), code (`app/**`);
subsystems `capture-flow` (`record_key: feature`, `values: [F01]`), `review-flow` (`feature`, `[F02]`), `tide-engine`
(`paths: [app/engine/**]`); `spread: {domain_min: 4, subsystem_max: 10}`; `exclude: [archive/**]`; `control: {set:
second-control, part: visible, size: 24, baseline: first, spread: 2}`. The names are its own on purpose (no `task`,
`spec`, `report`): a word of ordinary prose would make "holds no name of another repository" untestable.

A record carries its feature as YAML front matter (`---`, `feature: F01`, `---`); the clean 40 give decisions 8,
harbour-tasks 4, berth-specs 7, pilot-reports 6, code 15 and capture-flow 4, review-flow 4, tide-engine 4, none 28
(one report carries `feature: F09`, in no row). Three commits (base, audit, later); the working tree stands at `later`
with a staged file, a modified file and its own `.gov-runtime/store.db` (ignored), which nothing may touch (S8).

## Readings chosen where the ticket leaves a detail open

1. **The adopter's order (S7, S8).** `fresh` runs first, with nothing delivered: it names the two halves, prints the
   plan line and `WAITING <audit> writer-1`, exit 5. Then `brief` per half, then the halves are delivered, then `fresh`
   again. A tag whose audit names already exist in the sets root without the tag's run folder is `FR-NAME` (S8), so
   delivering before the first `fresh` is refused; the tests plant every delivery after it.
2. **The scan's window (S12).** Every planted run calls `brief --kind writer` for each half before delivering, so each
   half's ledger holds a `brief` event before any step; `fresh` is never given `--since` (reading 12).
3. **Which half waits or stops first is not fixed.** Where both halves are in the same state the tests accept either
   audit's name in `WAITING` / `STOPPED` / `MEASURE VOID`; where only the hidden half is behind they ask for its line
   among the run's lines. Both halves' question ids are `q01` to `q40`, so a transcript naming `q07` may void either.
4. **The verdict lines** are the run's last two lines, in either order, each fitting its whole form; the percentage is
   a decimal number (`100.0`, `92.5`).
5. **`MA-CONFIG-KEY <dotted key path>` inside a list row:** the path starts with the list's key and ends with the
   unknown key (`domains…colour`); how the row is named between them is the engineer's. `control.colour` and
   `control.baseline` are exact. An unreadable YAML's line is `MA-CONFIG-FORM <path, may be empty>: <reason>`.
6. **`config.load`'s tables** are read as rows that are mappings or objects with the Interface's key names (`name`,
   `paths`, `count`, `set`, `baseline`, …), or `(name, value)` pairs (a mapping by name is read as its items).
7. **`deliver --from <dir>`: `<dir>` is the session's `out/` folder itself** (confirmed by the lead) (it holds `result.json` and `set/`, or
   `notes.md`), as S10 words it ("takes a session's `out/` folder").
8. **`brief --since <rev>`** gives `selection.json`'s `last_audit` (the resolved commit) and `changed` (the tracked
   paths that differ between it and the commit, less `exclude`); with fewer than 300 other paths `sample` holds all of
   them. `seed_sha256` is accepted as the sha256 of `seed.txt`'s bytes, of `<seed>\n` or of `<seed>`.
9. **A quota in a brief** is the category's name with its count on one line, or a table whose header row holds the names
   and one of the next two rows the counts. A name "of another repository" is looked for as a whole lower-case word.
   `by_area`'s domains are looked for from the first `by_area` to the next `## ` heading.
10. **A step's control line** keeps today's form (`CONTROL control-1: hit@5 <h> of <n>; last <l>; in range|control out
    of range`), as S6 keeps Gov OS's figures unchanged.
11. **S7 (c), the lead's ruling.** A half still thin in a domain after round 2 ends at `void` itself (today's
    `VOID-DOMAIN`, exit 2): `STOPPED <audit> void [<code>]`, exit 2, no `USED`, one pre-flight in its ledger
    (`stopped-thin`). `STOPPED <audit> preflight-final` is for a refusal only the final pre-flight sees: a subsystem
    over its maximum (`stopped-heavy`, two pre-flights in the ledger).
12. **`--since`, the lead's ruling.** `fresh --since` is an ISO-8601 time (the scan window's start), `brief --since` a
    revision. `fresh --since` is not tested beyond that: every planted run opens its window by a `brief` event.

## Gaps (said, not weakened)

- **Closed: I6's variable is `MEMAUDIT_CONFIG` (the lead's decision).** As first written (`GOV_MEMAUDIT_CONFIG`) it
  did not reach the children of `tests/acceptance/W2-171`, `W2-172` and `W2-187`, whose planted worlds drop every
  `GOV_` variable from a child's environment and copy the rest. Without the prefix the variable passes through them,
  so their planted repositories get Gov OS's file with their test files unchanged. The ticket's I2 and I6 name it so.
- **S1's "every existing memaudit folder passes unchanged"** is the lead's run, not a case here.
- **S9's "differences listed in `docs/changes/W2-204-evidence.md`"** is a record, not tested.
- **S8:** a malformed tag's exit code is not stated closely enough to test; `fresh --since` is not tested (reading 12); `--gate-cmd` is not a
  KPI line. A run folder inside the sets root is asked only to be refused (exit 1 or 4) and not made.
- **F3 "a source":** a first-source path is looked for in every printed line; in files it is not (a repository path is
  legitimately in `selection.json` and the clone).
- **F1** is checked on the commands' own file accesses (`check`, `brief`, the first `fresh`) and on every recorded
  argument of a whole run; a grandchild's opens are covered by the planted `HOME` only.

## Kinds and cost

Acceptance, except `test_s1_check_reads_gov_os_s_own_file_and_prints_its_counts`, the four `test_s1_the_file_...` cases
and `test_f2_...`/`test_f3_say_stays_the_only_printer`, which are **repository-state** (they read this tree's own two
files, three pinned blobs and the module's sources). The cases that read a planted run are past the 5 s acceptance
limit by design once the commands exist (a whole fresh 80 with fakes is about 200 child processes per half, as in
W2-171 and W2-172; about 10 s per judged half on this machine); each run is built once. On the base the folder runs
in about 12 s (every command ends at once).

## The fix under the closed ticket: S13 to S16 (EXAMIN's F-033, 2026-11-20)

Written by the independent test designer from the ticket's last section (`## Fix: the transcript scan's id match`),
its terms and its lines S13 (M1) to S16 (M4), on the base `d42b1d833`, before any implementation. Public interface only:
`gov memaudit scan` as a child process (`python3 -m gov.cli.main memaudit scan --set ... --since ... [--until ...]
--projects <planted> [--json]`), its lines (`MEASURE VOID: <n> finding(s), <k> transcripts read`, one line per finding
`<file>:<line> session=.. role=.. kind=.. match=..`, `no transcript in the window names the set: <k> transcripts read,
<n> ids`, `SCAN INCOMPLETE`), its exit codes (0, 1, 3) and the `--json` envelope's `result.findings` and
`result.transcripts_read`; and `fresh`'s close (`SCAN <audit> clean`) on a new planted run, `busy`.

- **Planted** (`w2_204_scan_support.py`): a home under `tmp_path`; the set at `<home>/eval/fixtures/evaluation/
  memory-audit-20261107` (tag `20261107`), its `hidden/q<nn>.yaml` written with `yaml.safe_dump` in a delivered half's
  fields (a long question folded over two lines by the dumper), or empty (a dummy); transcripts in Claude Code's JSONL
  form under a planted projects folder (chat, text, Bash `tool_use`, `tool_result`, a Read tool's numbered output, a
  line of `\u` escapes, a sub-agent's transcript), with planted timestamps and mtimes. Every question and gold answer
  holds a word found nowhere else (`Velloran`, `Zephranel`, ...), checked absent from stdout and stderr.
- **The `busy` stage** (`w2_204_stages.py`): `misses`'s run with every answer right and three more transcripts in the
  window (bare `q01`..`q40`, a numbered list, another set's name and path beside `q07`), none naming either half.
- **Readings where the fix leaves a detail open** (tested no further than stated):
  1. A key is looked for in each decoded text value of a line, normalised; a line that holds the key across two text
     values is not tested. The question files' text is read as YAML (`question` field).
  2. The 48-character cut: a line ending right after the first 48 characters of a question holds its key; one
     holding the first 47 and then another character does not. Every planted key ends in a letter, so a key's
     trailing space never decides a case.
  3. An unreadable question file with no finding: exit 3 and the output names the file (`q01.yaml`), as an unreadable
     transcript is named today. An empty file is no problem (exit 0).
  4. A set whose path holds no audit or standing name: its own folder's name (the parent's when `--set` is the
     `hidden` folder), at least 8 characters, is its name; a shorter one gives no name, so its ids are never a finding
     (the path forms still are).
  5. A line holding both a bare id and a question's text gives `kind=text` (the bare id is no evidence); a line with
     the set's path gives `kind=path` (the most specific form) whatever else it holds. A line holding a key and the
     name beside an id is not planted (which kind wins is not stated).
  6. `--id` with the text match: not tested (the ticket does not say whether `--id` narrows the keys); W2-198's F2
     no-finding case no longer uses `--id` for that reason.
- **Rewritten existing cases** (a separate commit, trailer `Rewrite-Reason`): the cases that planted a bare id as the
  evidence now plant the tag or the audit name beside it, findings unchanged: W2-198 S3 (lines 6 and 8 of
  `sess-main`, the sub-agent's line, `--id h7`'s line; the names-only case renamed `..._even_when_the_files_cannot_be_read`),
  W2-198 F2 (the finding beside an unreadable transcript; the no-finding case plants a bare id and the gold answer,
  without `--id`), `tests/unit/memaudit/test_w2_198_scan.py` (the id cases through `scan.scan` with the tag; the
  bare-id assertion of the path-form case removed; "never opened" becomes "never changed, text never in the result")
  and this folder's S12 `void` and `right` stages (the leak line names the hidden half's audit name beside `q07`).
  Red on the base after the rewrite: only W2-198 F2's two no-finding cases (a bare `q01` is still a finding there).

## KPI map

| KPI id | tests | expected red reason |
|---|---|---|
| success-1 (S1) | `test_w2_204_s1_config.py::test_s1_the_file_holds_todays_domain_and_subsystem_tables_in_order`, `test_w2_204_s1_config.py::test_s1_the_file_holds_the_twelve_categories_with_their_quotas_in_order`, `test_w2_204_s1_config.py::test_s1_the_file_holds_the_control_set_and_the_spread_rule`, `test_w2_204_s1_config.py::test_s1_load_returns_exactly_the_old_tables_for_gov_os_s_repository`, `test_w2_204_s1_config.py::test_s1_load_returns_the_control_figures_and_the_spread_numbers`, `test_w2_204_s1_config.py::test_s1_the_file_validates_against_the_schema`, `test_w2_204_s1_config.py::test_s1_the_schema_takes_the_second_repository_s_file_and_refuses_an_unknown_key`, `test_w2_204_s1_config.py::test_s1_check_reads_gov_os_s_own_file_and_prints_its_counts` | `governance/project/memory-audit.yaml does not exist`; `cannot import name 'config' from 'gov.memaudit'`; the schema file does not exist; `check` is no step (`ERROR: UsageError`, exit 4; on the CLI `invalid choice: 'check'`, exit 2) |
| success-2 (S2) | `test_w2_204_s2_s3_refusals.py::test_s2_a_repository_without_the_file_is_refused_at_every_step` | no step knows the file: the old steps answer as before (`PF-...`, `DC-PREFLIGHT`, exit 1 without the line, or exit 4), the new ones are no steps; on the CLI `invalid choice` |
| success-3 (S3) | `test_w2_204_s2_s3_refusals.py::test_s3_check_names_the_one_fault_of_the_repository_s_own_file`, `test_w2_204_s2_s3_refusals.py::test_s3_a_step_names_the_same_fault_and_writes_nothing`, `test_w2_204_s2_s3_refusals.py::test_s3_every_step_refuses_a_faulty_file_with_exit_1`, `test_w2_204_s2_s3_refusals.py::test_s3_only_the_first_fault_is_named`, `test_w2_204_s2_s3_refusals.py::test_s3_a_file_without_a_fault_is_ok_and_check_prints_its_counts` | no `MA-CONFIG` line is printed: `check` is no step, the file is not read by any step |
| success-4 (S4) | `test_w2_204_s4_s6_second_repo.py::test_s4_two_delivered_halves_run_to_a_judged_figure_that_passes`, `test_w2_204_s4_s6_second_repo.py::test_s4_both_halves_figures_are_keyed_by_the_repository_s_categories`, `test_w2_204_s4_s6_second_repo.py::test_s4_three_wrong_answers_of_forty_say_misses`, `test_w2_204_s4_s6_second_repo.py::test_s4_the_verdict_s_n_is_the_kept_hidden_questions` | `gov memaudit fresh` does not exist (`invalid choice: 'fresh'`, exit 2): no verdict line, no `FIGURES.json` |
| success-5 (S5) | `test_w2_204_s4_s6_second_repo.py::test_s5_questions_are_counted_per_feature_by_their_first_source_s_front_matter`, `test_w2_204_s4_s6_second_repo.py::test_s5_a_feature_no_row_holds_and_a_file_without_front_matter_count_none`, `test_w2_204_s4_s6_second_repo.py::test_s5_void_counts_the_kept_questions_per_feature_in_drops_json`, `test_w2_204_s4_s6_second_repo.py::test_s5_eleven_of_forty_in_one_feature_are_refused_pf_spread` | `gov memaudit preflight` is not on the CLI (exit 2); no `PREFLIGHT.json` |
| success-6 (S6) | `test_w2_204_s4_s6_second_repo.py::test_s6_a_control_at_the_file_s_baseline_is_in_range`, `test_w2_204_s4_s6_second_repo.py::test_s6_a_control_outside_the_file_s_spread_stops_the_audit`, `test_w2_204_s4_s6_second_repo.py::test_s6_baseline_first_passes_and_its_figure_is_the_next_audit_s_last`, `test_w2_204_s4_s6_second_repo.py::test_s6_control_none_makes_no_control_search_and_the_figures_hold_null`, `test_w2_204_s4_s6_second_repo.py::test_s6_gov_os_s_own_control_is_still_34_within_2`, `test_w2_204_s4_s6_second_repo.py::test_s6_gov_os_s_control_three_away_is_out_of_range` | "the clean half's pre-flight did not pass" (the step is not on the CLI); `fresh` does not exist; the Gov OS cases: `void` takes no `--repo` (`ERROR: UsageError`) |
| success-7 (S7) | `test_w2_204_s7_s8_s12_fresh.py::test_s7a_a_refused_first_pre_flight_is_recorded_and_the_run_waits_for_the_checker`, `test_w2_204_s7_s8_s12_fresh.py::test_s7a_after_the_notes_the_writer_s_round_2_is_asked_though_every_line_accepts`, `test_w2_204_s7_s8_s12_fresh.py::test_s7a_after_a_repaired_round_2_the_checker_s_round_2_is_asked`, `test_w2_204_s7_s8_s12_fresh.py::test_s7a_with_the_second_notes_the_run_goes_on_to_the_judged_figure`, `test_w2_204_s7_s8_s12_fresh.py::test_s7a_the_first_pre_flight_ran_once_for_the_half`, `test_w2_204_s7_s8_s12_fresh.py::test_s7b_nothing_delivered_waits_for_the_writer_s_round_1`, `test_w2_204_s7_s8_s12_fresh.py::test_s7b_a_delivered_half_without_notes_waits_for_the_checker`, `test_w2_204_s7_s8_s12_fresh.py::test_s7b_no_round_2_is_asked_when_every_line_accepts_and_the_first_pre_flight_is_ok`, `test_w2_204_s7_s8_s12_fresh.py::test_s7c_a_refused_first_pre_flight_asks_round_2`, `test_w2_204_s7_s8_s12_fresh.py::test_s7c_a_round_2_that_cannot_go_on_stops_the_run_with_exit_2_at_its_step`, `test_w2_204_s7_s8_s12_fresh.py::test_s7c_nothing_is_spent_at_a_stop_no_used_no_measure`, `test_w2_204_s7_s8_s12_fresh.py::test_s7d_a_second_call_after_a_stop_repeats_no_recorded_step`, `test_w2_204_s4_s6_second_repo.py::test_s4_the_verdict_s_n_is_the_kept_hidden_questions` | `fresh` does not exist: exit 2 with no `WAITING` / `STOPPED` line |
| success-8 (S8) | `test_w2_204_s7_s8_s12_fresh.py::test_s8_the_two_halves_are_named_from_the_tag`, `test_w2_204_s7_s8_s12_fresh.py::test_s8_a_letter_of_the_tag_names_the_next_pair`, `test_w2_204_s7_s8_s12_fresh.py::test_s8_the_repository_s_store_tree_and_index_are_not_touched`, `test_w2_204_s7_s8_s12_fresh.py::test_s8_the_snapshot_is_a_detached_clean_clone_at_the_commit_without_hard_links`, `test_w2_204_s7_s8_s12_fresh.py::test_s8_the_rebuild_command_ran_once_in_the_clone_only`, `test_w2_204_s7_s8_s12_fresh.py::test_s8_each_half_is_declared_on_the_clone_s_own_store`, `test_w2_204_s7_s8_s12_fresh.py::test_s8_the_visible_half_is_released_after_its_measure_and_the_hidden_half_is_not`, `test_w2_204_s7_s8_s12_fresh.py::test_s8_the_run_s_state_is_counts_json_in_its_folder`, `test_w2_204_s7_s8_s12_fresh.py::test_s8_a_tag_whose_run_folder_holds_another_commit_is_refused`, `test_w2_204_s7_s8_s12_fresh.py::test_s8_a_tag_whose_audit_names_exist_without_its_run_folder_is_refused`, `test_w2_204_s7_s8_s12_fresh.py::test_s8_a_run_folder_inside_the_sets_root_is_refused` | `fresh` does not exist: no plan line, no clone, no rebuild, no `COUNTS.json`, no `FR-NAME` |
| success-9 (S9) | `test_w2_204_s9_s10_brief_deliver.py::test_s9_brief_prints_one_line_with_the_brief_s_sha256_and_no_path`, `test_w2_204_s9_s10_brief_deliver.py::test_s9_the_second_repository_s_writer_brief_is_filled_from_its_file`, `test_w2_204_s9_s10_brief_deliver.py::test_s9_the_second_repository_s_briefs_hold_no_name_of_gov_os_s_tables`, `test_w2_204_s9_s10_brief_deliver.py::test_s9_by_area_is_counted_in_the_file_s_domains_and_none`, `test_w2_204_s9_s10_brief_deliver.py::test_s9_gov_os_s_brief_is_filled_from_gov_os_s_file_and_holds_nothing_of_the_second_repository`, `test_w2_204_s9_s10_brief_deliver.py::test_s9_the_selection_lists_the_commit_s_tracked_paths_less_the_excluded`, `test_w2_204_s9_s10_brief_deliver.py::test_s9_the_seed_is_written_beside_the_brief_and_the_selection_holds_its_sha256`, `test_w2_204_s9_s10_brief_deliver.py::test_s9_the_set_s_selection_json_in_the_sets_root_equals_the_folder_s`, `test_w2_204_s9_s10_brief_deliver.py::test_s9_a_round_2_writer_folder_holds_the_delivered_set_and_the_round_1_notes`, `test_w2_204_s9_s10_brief_deliver.py::test_s9_a_checker_folder_holds_the_delivered_set`, `test_w2_204_s9_s10_brief_deliver.py::test_s9_each_brief_is_an_event_of_the_audit_s_ledger` | `brief` does not exist: "no brief.md in the ... folder", no `selection.json`, no `seed.txt`, no `brief` event |
| success-10 (S10) | `test_w2_204_s9_s10_brief_deliver.py::test_s10_a_good_writer_delivery_lands_forty_files_and_prints_counts_only`, `test_w2_204_s9_s10_brief_deliver.py::test_s10_a_delivery_that_fails_its_form_is_refused_and_nothing_is_copied`, `test_w2_204_s9_s10_brief_deliver.py::test_s10_a_second_round_1_delivery_is_refused_dl_exists`, `test_w2_204_s9_s10_brief_deliver.py::test_s10_round_2_moves_round_1_aside_and_leaves_only_the_new_files`, `test_w2_204_s9_s10_brief_deliver.py::test_s10_a_checker_s_notes_land_as_the_round_s_xcheck_file`, `test_w2_204_s9_s10_brief_deliver.py::test_s10_notes_without_the_questions_section_are_refused_dl_notes` | `deliver` does not exist (`invalid choice: 'deliver'`, exit 2; `ERROR: UsageError`, exit 4): no `DELIVER` line, no `DL-` code |
| success-11 (S11) | `test_w2_204_s11_cli.py::test_s11_both_entries_end_a_step_with_the_same_exit_code_and_lines`, `test_w2_204_s11_cli.py::test_s11_the_lines_are_the_steps_own`, `test_w2_204_s11_cli.py::test_s11_help_lists_the_steps`, `test_w2_204_s11_cli.py::test_s11_the_exit_words_gain_waiting_5_and_keep_the_others` | `gov memaudit` has `scan` only: every step is `invalid choice`, exit 2, no line; `--help` lists `scan` alone; `EXIT` has no `waiting` |
| success-12 (S12) | `test_w2_204_s7_s8_s12_fresh.py::test_s12_transcripts_that_name_no_id_give_two_clean_lines_and_the_verdict`, `test_w2_204_s7_s8_s12_fresh.py::test_s12_a_transcript_that_names_a_question_id_voids_the_measure`, `test_w2_204_s7_s8_s12_fresh.py::test_s12_the_same_transcript_allowed_by_its_session_is_clean`, `test_w2_204_s7_s8_s12_fresh.py::test_s12_the_window_opens_at_the_half_s_first_brief_event` | `fresh` does not exist: no `SCAN` and no `MEASURE VOID` line |
| failure-1 (F1) | `test_w2_204_f_guards.py::test_f1_a_new_step_opens_nothing_under_the_true_home_s_sets_or_runs`, `test_w2_204_f_guards.py::test_f1_no_call_of_a_whole_planted_run_names_the_true_sets_or_runs` | the new steps do not exist ("check ended 4, not 0"); the whole run did not end 0 |
| failure-2 (F2) | `test_w2_204_f_guards.py::test_f2_the_prompts_the_model_calls_and_their_test_are_the_base_s_bytes` | **Green on the base by design (a guard):** `prompts.py`, `claude.py` and `tests/unit/memaudit/test_prompts.py` are the base's blobs; red if the ticket touches one |
| failure-3 (F3) | `test_w2_204_f_guards.py::test_f3_no_line_of_a_whole_run_holds_a_question_an_answer_or_a_source`, `test_w2_204_f_guards.py::test_f3_the_figures_the_ledger_and_the_records_hold_counts_only`, `test_w2_204_f_guards.py::test_f3_no_file_outside_the_sets_and_the_run_folders_holds_a_planted_word`, `test_w2_204_f_guards.py::test_f3_say_stays_the_only_printer`, `test_w2_204_s9_s10_brief_deliver.py::test_s10_a_good_writer_delivery_lands_forty_files_and_prints_counts_only`, `test_w2_204_s9_s10_brief_deliver.py::test_s9_each_brief_is_an_event_of_the_audit_s_ledger` | the whole run did not end 0 (`fresh` does not exist). **Green on the base by design (a guard):** `test_f3_say_stays_the_only_printer` (no module but `say.py` and `command.py` prints today) |
| failure-4 (F4) | `test_w2_204_s4_s6_second_repo.py::test_f4_a_question_labelled_with_a_gov_os_category_is_pf_form`, `test_w2_204_s4_s6_second_repo.py::test_f4_a_half_with_no_register_question_is_not_thin_for_a_gov_os_domain`, `test_w2_204_s4_s6_second_repo.py::test_f4_void_never_calls_a_gov_os_domain_thin` | `gov memaudit preflight` is not on the CLI (exit 2); no `PREFLIGHT.json`, no `DROPS.json` |
| success-13 (S13) | `test_w2_204_s13_s16_scan_id_match.py::test_s13_bare_ids_in_many_transcripts_and_a_dummy_set_are_no_finding`, `test_w2_204_s13_s16_scan_id_match.py::test_s13_an_id_beside_the_tag_or_the_audit_name_is_a_finding_naming_its_transcript`, `test_w2_204_s13_s16_scan_id_match.py::test_s13_the_name_and_the_tag_count_only_as_whole_tokens`, `test_w2_204_s13_s16_scan_id_match.py::test_s13_the_set_s_names_come_from_its_real_path`, `test_w2_204_s13_s16_scan_id_match.py::test_s13_a_set_folder_name_under_8_characters_names_nothing_so_its_ids_are_no_finding`, `test_w2_204_s13_s16_scan_id_match.py::test_s13_guard_every_transcript_of_the_window_is_read` | the scan matches every bare `q<nn>` as a whole token: the busy window gives `MEASURE VOID: <n> finding(s)` (exit 1) where exit 0 is due, and the tagged and named lines come among many bare-id findings, not alone. **Green on the base by design (a guard):** `test_s13_guard_every_transcript_of_the_window_is_read` (A-12: `transcripts_read` counts every transcript of the window, the ones with no finding and a sub-agent's included); red if the fix narrows which transcripts are read |
| success-14 (S14) | `test_w2_204_s13_s16_scan_id_match.py::test_s14_a_question_s_text_read_is_a_text_finding_whose_match_is_its_id`, `test_w2_204_s13_s16_scan_id_match.py::test_s14_the_key_is_the_first_48_normalised_characters_and_text_of_no_question_is_clean`, `test_w2_204_s13_s16_scan_id_match.py::test_s14_two_questions_each_read_are_two_findings_each_matching_its_own_id`, `test_w2_204_s13_s16_scan_id_match.py::test_s14_a_question_under_24_normalised_characters_gives_no_text_finding`, `test_w2_204_s13_s16_scan_id_match.py::test_s14_an_unreadable_question_file_is_a_problem_an_empty_one_is_not`, `test_w2_204_s13_s16_scan_id_match.py::test_s15_a_question_and_its_gold_answer_read_from_a_file_are_printed_nowhere` | the scan never reads a question's text: a transcript holding it is clean (`no transcript in the window names the set`, exit 0) or gives only `kind=id` findings from a bare id beside it, never `kind=text`; an unreadable question file is not opened, so no `SCAN INCOMPLETE` (exit 0, not 3) |
| success-15 (S15) | `test_w2_204_s13_s16_scan_id_match.py::test_s15_guard_each_path_form_and_a_question_file_path_is_a_path_finding`, `test_w2_204_s13_s16_scan_id_match.py::test_s15_a_question_and_its_gold_answer_read_from_a_file_are_printed_nowhere` | the read file's line gives `kind=id match=q02` (the bare `id: q02` in it) and the quoted question none: `MEASURE VOID: 2 finding(s)` where 3 (path, text, text) are due. **Green on the base by design (a guard):** `test_s15_guard_each_path_form_and_a_question_file_path_is_a_path_finding`; red if a path form stops counting. S15's other verify, W2-198's path cases and the rewritten bare-id cases (W2-198 S3 and F2, `tests/unit/memaudit/test_w2_198_scan.py`), runs in those folders, not under `gov accept W2-204` |
| success-16 (S16) | `test_w2_204_s13_s16_scan_id_match.py::test_s16_examin_s_case_the_one_typed_path_is_the_only_finding_and_without_it_the_window_is_clean`, `test_w2_204_s13_s16_scan_id_match.py::test_s16_the_fresh_close_agrees_a_busy_window_without_the_path_is_clean` | EXAMIN's case as found: the busy window gives the typed path among many `kind=id` findings (`MEASURE VOID: <n> finding(s)`, n above 1) and without the path line still exit 1; `fresh` on the `busy` stage prints `MEASURE VOID <audit>` for both halves, exit 2, no `SCAN <audit> clean` and no verdict |
| success-17 (S17, F15 stamp) | `test_w2_204_fix_figure_stamp.py::test_s17_figures_json_carries_the_six_stamp_keys`, `test_w2_204_fix_figure_stamp.py::test_s17_the_stamp_values_are_the_runs_own`, `test_w2_204_fix_figure_stamp.py::test_s17_the_printed_verdict_says_the_stamp` | FIGURES.json and the printed verdict lack `release`, `commit`, `reader_model`, `grader_models`, `forbidden_rule`, `questions_with_forbidden`. The planted run sets `forbidden` lists, so it needs D5 (`e2/d5-memaudit-strict`) merged; on a base without D5 it stops earlier at PF-FORM |
| success-18 (S18, F15 declare) | `test_w2_204_fix_figure_stamp.py::test_s18_declare_notices_and_goes_on_when_no_question_carries_a_list`, `test_w2_204_fix_figure_stamp.py::test_s18_declare_goes_on_when_one_question_carries_a_list` | declare with no `forbidden` list prints the one NOTICE DC-FORBIDDEN-NONE line, exits 0 and records `forbidden_lists` 0 (red: refused); with one list no notice and `forbidden_lists` 1 (red: the count is missing) |
| success-19 (S19, F15 comparison) | `test_w2_204_fix_figure_stamp.py::test_s19_a_figure_without_the_stamp_is_not_compared_with_one_that_has_it`, `test_w2_204_fix_figure_stamp.py::test_s19_guard_two_stamped_figures_are_compared_as_before` | `standing.drift` compares a stamped figure with an unstamped one (drift word STANDING_STALE, no `comparable: false`, no `missing`). The second case is a guard, green today |

### The one change to existing test files (I6)

`tests/conftest.py`: the session-wide autouse fixture `_gov_os_memaudit_config` sets `MEMAUDIT_CONFIG` to
`<tree>/governance/project/memory-audit.yaml` (commit trailer `Rewrite-Reason`). Unused by the base's code;
`tests/unit/memaudit` and the existing memaudit acceptance folders are green with it on the base.

## The fix under the closed ticket: the strict forbidden-citation rule (DEC-1227 D5 (a)), S1 to S4 of the fix

Written by the independent test designer from the ticket's last section (`## Fix: the strict forbidden-citation rule in
the product's own grading`), its lines S1 to S4 and the interface the lead named, on the base `c03de39f2`, before any
implementation. The fix's lines are numbered S1 to S4 in the ticket and **share the ids `success-1` to `success-4`**
with the ticket's own lines in the map below (each row says `(S<n> of the fix)`): the ticket's own tests under those
ids stay green, and `gov accept` passes a line when every test it names was found and none failed. All the new cases
are in `test_w2_204_fix_forbidden.py`.

- **The rule** is W2-81's (`tests/acceptance/W2-81/w2_81_score.py`, loaded by path in the parity cases, never edited):
  a citation is right when a cited place holds a gold line and no cited path is one of the question's forbidden paths
  (equality); an answer is right when the grade is `correct` and the citation is right.
- **Public interface only:** `gov memaudit preflight`, `brief` and `fresh` as child processes; the files of a planted
  run (`FIGURES.json`, `misses.jsonl`, the reader's rows `reader/<id>.json` in the run folder); in process, the
  interface the lead named: `preflight.form_ok`, `matcher.questions` (the key `forbidden`), `matcher.forbidden_cited`
  and `matcher.citation_right`. The reader and the graders are W2-171's fakes (the planted `claude_plan.json` is
  edited after `install_plans`: each question's cited places and grade).
- **The planted run `forbidden`** (`ST.BUILDS`, built once per session like the folder's other stages): both halves
  delivered with `forbidden` on some questions, then `fresh`. Hidden: q05 gold and a forbidden path cited, grade
  correct (wrong); q06 a list never cited (right); q08 gold cited, grade wrong (wrong); q09 gold and an unlisted path
  (right); the hidden half therefore holds exactly **one** forbidden-cited answer. Visible: q05 the forbidden path
  alone (wrong); q06 gold and forbidden, grade wrong (wrong, forbidden cited); q07 the list's second path cited
  before the gold, grade correct (wrong); q08 right; q10 no `forbidden` key, a path other questions list cited (right,
  as before); q40 the apart question, not found, a listed path cited (right, `forbidden_cited` false). Strict
  figures: hidden 38 of 40 (misses `{q05: incomplete, q08: wrong}`, `forbidden_cited` 1); visible 37 of 40 (misses
  q05, q07 `incomplete` and q06 `wrong`, `forbidden_cited` 3).
- **Readings where the fix leaves a detail open** (tested no further than stated):
  1. A malformed `forbidden` is tested with ten variants (a string, a mapping, a number, a bool, an empty item alone
     or after a path, a number item, a null item, a list item, a mapping item). An explicit `forbidden: null`, a
     whitespace-only item, a path that does not exist in the repository, and a forbidden path that is also a gold
     path are not tested (the lead's text does not say).
  2. `misses.forbidden_cited` counts the misses whose row says a forbidden path was cited, whatever the grade (visible
     q06 is a wrong-grade miss and is counted); an apart question's row says `false` even when its reader cited a
     listed path.
  3. W2-81's `judge_question` has no apart concept (it reads a `not_found` reader as a miss), so the parity cases
     leave the apart question out; for the others the product's verdict is "not among `misses.jsonl`".
  4. The brief cases read text, not wording: a fenced `yaml` block with a `forbidden:` line, a rule that ties
     `forbidden` to the stale, superseded or legacy source and to naming it, a sentence that says a forbidden source
     is never also a gold one; the checker's input-form sentence names `forbidden` within 300 characters of
     `naive_answer`.
- **Existing cases rewritten** (a separate commit, trailer `Rewrite-Reason`: DEC-1227 D5; red on the base after the
  rewrite): they pin the old key sets of `FIGURES.json` and of a judge row. `tests/unit/memaudit/test_judge.py`
  (`FIGURE_KEYS` gains `forbidden_rule`); `tests/acceptance/W2-171/test_w2_171_s3_judge.py` (`ROW_KEYS` gains
  `forbidden_cited`); `tests/acceptance/W2-171/test_w2_171_s6_figures.py` (`TOP` gains `forbidden_rule`, `MISSES` gains
  `forbidden_cited`) and its expected figures in `w2_171_scenario.py` (`"forbidden_rule": "strict"`, `forbidden_cited`
  0: no planted question there lists a forbidden path).
- **Green on the base by design (guards):** `test_fix_s1_form_ok_refuses_a_malformed_field[...]` and
  `test_fix_s1_form_ok_accepts_the_field_and_its_absence[absent]` and the pre-flight case with the field absent (the
  base refuses an unknown key and accepts a set without it); `test_fix_s3_guard_kernel_template_prompts_and_claude_are_the_merge_base_s_files`
  (rescoped under DEC-1227 D5 and DEC-1232 (6): it pins the sha256 of `src/gov/memaudit/prompts.py` and `src/gov/memaudit/claude.py`, found through their modules, and no longer compares the whole `template/` tree with the merge base, which other fixes change; the `tests/unit/memaudit/test_prompts.py` hash pin and F2 stand too).
- **Red on the base, and why:** every case of the planted run `forbidden` stops at `STOPPED`/`WAITING ... writer-2`
  (exit 5): the base's pre-flight refuses a question file with the unknown key `forbidden` (`PF-FORM`), so no judge
  runs. Without the key (probed on the base) the rule is missing: q05 of the hidden half is right, `forbidden_cited`
  is absent from every row and `FIGURES.json`. The matcher cases: `matcher` has no `forbidden_cited`,
  `citation_right` or key `forbidden`. The brief cases: no `forbidden:` line, no rule.

### KPI map of the fix

| KPI id | tests | expected red reason |
|---|---|---|
| success-1 (S1 of the fix) | `test_w2_204_fix_forbidden.py::test_fix_s1_form_ok_accepts_the_field_and_its_absence`, `test_w2_204_fix_forbidden.py::test_fix_s1_form_ok_refuses_a_malformed_field`, `test_w2_204_fix_forbidden.py::test_fix_s1_a_set_with_or_without_the_field_passes_the_pre_flight`, `test_w2_204_fix_forbidden.py::test_fix_s1_a_malformed_field_is_pf_form_naming_the_question`, `test_w2_204_fix_forbidden.py::test_fix_s1_two_malformed_fields_name_both_questions`, `test_w2_204_fix_forbidden.py::test_fix_s1_the_loaded_question_holds_its_forbidden_paths`, `test_w2_204_fix_forbidden.py::test_fix_s1_a_question_without_the_field_loads_an_empty_list` | `form_ok` and the pre-flight refuse the unknown key `forbidden` (`PF-FORM refused` naming the good questions too: 3 where 2 or 1 are due); `matcher.questions` gives no key `forbidden` (`KeyError`). **Green on the base by design:** the `absent` cases and `form_ok`'s refusals of a malformed field |
| success-2 (S2 of the fix) | `test_w2_204_fix_forbidden.py::test_fix_s2_matcher_forbidden_cited_is_path_equality`, `test_w2_204_fix_forbidden.py::test_fix_s2_matcher_citation_right_is_gold_cited_and_no_forbidden_cited`, `test_w2_204_fix_forbidden.py::test_fix_s2_matcher_citation_right_is_the_old_gold_test_less_a_forbidden_citation`, `test_w2_204_fix_forbidden.py::test_fix_s2_planted_correct_and_gold_cited_is_right`, `test_w2_204_fix_forbidden.py::test_fix_s2_planted_correct_and_forbidden_cited_alone_is_wrong`, `test_w2_204_fix_forbidden.py::test_fix_s2_planted_correct_with_gold_and_forbidden_cited_is_wrong`, `test_w2_204_fix_forbidden.py::test_fix_s2_planted_wrong_grade_with_gold_cited_is_wrong_and_forbidden_cited_is_what_was_cited`, `test_w2_204_fix_forbidden.py::test_fix_s2_planted_a_question_without_a_list_is_graded_as_before`, `test_w2_204_fix_forbidden.py::test_fix_s2_planted_an_apart_question_is_unchanged`, `test_w2_204_fix_forbidden.py::test_fix_s2_the_planted_misses_are_exactly_the_cases_that_cite_a_forbidden_path_or_are_graded_wrong`, `test_w2_204_fix_forbidden.py::test_fix_s2_parity_the_product_and_w2_81_agree_on_every_planted_question`, `test_w2_204_fix_forbidden.py::test_fix_s2_parity_matcher_citation_right_agrees_with_w2_81_over_citations_and_grades` | `matcher` has no `forbidden_cited` or `citation_right` (`AttributeError`); the planted run stops at the pre-flight (`PF-FORM`, exit 5, no `misses.jsonl`, no rows); the rule itself is absent on the base (q05 right, no `forbidden_cited` in a row) |
| success-3 (S3 of the fix) | `test_w2_204_fix_forbidden.py::test_fix_s3_the_writer_brief_s_question_form_shows_the_optional_forbidden_field`, `test_w2_204_fix_forbidden.py::test_fix_s3_the_writer_brief_tells_the_writer_to_name_the_stale_sources`, `test_w2_204_fix_forbidden.py::test_fix_s3_the_writer_brief_says_a_forbidden_source_is_never_also_a_gold_source`, `test_w2_204_fix_forbidden.py::test_fix_s3_the_checker_brief_names_the_optional_forbidden_field_in_its_input_form`, `test_w2_204_fix_forbidden.py::test_fix_s3_guard_kernel_template_prompts_and_claude_are_the_merge_base_s_files` | the generated briefs hold no `forbidden:` line, no rule and no word `forbidden` in the checker's input form. **Green on the base by design:** the kernel guard |
| success-4 (S4 of the fix) | `test_w2_204_fix_forbidden.py::test_fix_s4_a_run_with_one_forbidden_cited_answer_counts_one_and_names_the_rule`, `test_w2_204_fix_forbidden.py::test_fix_s4_the_forbidden_cited_misses_are_counted_apart_from_the_others`, `test_w2_204_fix_forbidden.py::test_fix_s4_a_run_with_none_gives_zero_and_the_key_is_there`, `test_w2_204_fix_forbidden.py::test_fix_s4_the_run_s_printed_verdict_lines_count_the_strict_rule_in_their_old_form`, `test_w2_204_fix_forbidden.py::test_fix_s4_counts_only_no_text_path_or_answer_reaches_a_line_or_the_figures` | `FIGURES.json` holds no `forbidden_rule` and no `misses.forbidden_cited` (`KeyError`); the planted run `forbidden` stops at the pre-flight (exit 5) |

### P0-2 (plan item 0-2): the pre-flight refuses a store behind HEAD

Tests for the fix `P0-2` of DAEO-ma4q, in `test_w2_204_p0_2_store_behind.py`. The planted store is the one W2-116 keeps:
`integration_store` of the repository's `governance/project/rebuild.yaml` is a link to a detached worktree of the
repository, and the worktree's `.gov-runtime/store.db` has a `fingerprints` row for the commit the worktree is at (both
name one commit, so the engineer may read either). The repository commits the file (HEAD is that commit). A repository
that names no `integration_store` is not checked (the existing cases, green on the base, hold that). The refusal is any
non-zero exit with `STORE_BEHIND` and the first 12 hex digits of both commits in the output.

| KPI line | tests | expected red reason |
|---|---|---|
| P0-2 | `test_w2_204_p0_2_store_behind.py::test_p0_2_preflight_refuses_store_behind_naming_both_commits_and_writes_no_declaration` | the pre-flight does not read the store: exit 0, `PRE-FLIGHT: every check as expected`, no `STORE_BEHIND` |
| P0-2 | `test_w2_204_p0_2_store_behind.py::test_p0_2_a_store_at_head_passes_and_the_next_commit_makes_it_behind` | the store at HEAD passes (as before), then after a new commit the pre-flight still exits 0 with no `STORE_BEHIND` |
