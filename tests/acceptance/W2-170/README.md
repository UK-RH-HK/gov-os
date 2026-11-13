# W2-170 acceptance tests: the memory audit's set record (S1–S6, F1–F5)

Ticket `DAEO-61vm` (W2-170), profile FULL, class C2, run 1. An independent test designer (MR-3) wrote these
cases from the ticket's KPI lines and its `## Interface` section (sections 1–10, with section 10's four readings),
the three approved briefs (`governance/project/indep-briefs/memory-audit/`) and the ticket's sources. They were written
before the implementation; no code of `src/gov/memaudit/` existed or was read. Today's interfaces the tool uses or is
checked against were read at `w2/integrate` (`a3f1d5d2e32e`): `gov.util.parts.evaluation_sets`,
`gov.retrieval.measure`, `gov.retrieval.lexical.ids_in`/`whole_id`, `gov.store.loader.fingerprints`, the launch
script's stage B4 and its `SEEDS.log`/`AUDITS.log` lines, `gov.close.select.plan`, `gov.accept.runner.parse_map`.

**Batch 2 (run 2, the fix round after review round 1):** the same designer role, a fresh session, added
`test_w2_170_s1_s3_preflighted_set.py` for section 10's **reading 9** (review round 1's RV1, given as a described
behaviour, DEC-136): "the pre-flighted set is the set declared": `PREFLIGHT.json` records each delivered file's sha256
by id, and `DC-PREFLIGHT` also refuses when a kept file is not byte-equal to a pre-flighted one. No first-batch case was
changed. The implementation was not read (DEC-820); the new cases drive the same child process.

**179 cases from 101 test functions in eight files** (batch 1: 165 cases, 93 functions, seven files; batch 2: 14
cases, 8 functions, one file), with a support module (`w2_170_world.py`), a conftest and two child-process drivers
(`w2_170_open_log.py`, `w2_170_say_driver.py`). With the tool as it stands, the folder runs in under a minute.

## How the tests reach the code under test

- **The command line, as the callers run it:** `python3 -m gov.memaudit preflight|void|declare --sets-root <root>
  --audit memory-audit-20261111 ...` in a child process, judged by its exit code (Interface 5), its printed lines
  (sections 1, 3, 5) and the files it writes under `<root>/runs/<A>/`, `<root>/fixtures/evaluation/<A>/hidden/dropped/`
  and the sets root's own path map. `gov.memaudit` is never imported at collection, so the suite runs red by failing.
- **Python entry points (section 8), imported:** `gov.memaudit.say.say` (S5's refusal, by `w2_170_say_driver.py`)
  and the presence of `layout.paths`, `layout.is_used`, `preflight.run`, `drops.apply`, `declare.declare`,
  `say.say`, `ledger.append` (S6).
- **Code under test (DEC-732):** every child process gets this tree's `src/` first on its `PYTHONPATH`, taken from
  this folder's repository root (`w2_170_world.SRC`); a session fixture fails the run when a child would import `gov`
  from elsewhere. Today's modules used in-process: `gov.util.parts.evaluation_sets` (S4) and `gov.close.select`
  (S6's `plan`, F5's `match`).
- **Everything is planted under pytest's `tmp_path` (under `TMPDIR`)**, as section 9 lists it: a sets root whose own
  `governance/project/path-map.yaml` holds an `evaluation_sets` block among comments (with `memory-verdict-2`'s entry
  and another key after it); a git repository with three commits (`base`, the audit commit, and a `later` commit the
  working tree stands at, so that reading "at the commit" is told from reading the tree), its
  `governance/project/retrieval.yaml` (pool on; variants: pool off, absent, not a mapping), its path map with the
  `evaluation-sources` and `evaluation-fixtures` namespaces and an `evaluation_sets` entry, the walls'
  `tree-exclude.txt`, `.claude/` files and every source the planted questions cite; a launch-script folder with
  `indep/AUDITS.log` and `indep/SEEDS.log` (and, per case, a planted `selection.json`); a pool
  `fixtures/evaluation/memory-pool/hidden/`; a store file with a `fingerprints` row whose `head` is the audit commit;
  a `gov` link into a folder `pin-0123456789ab`; a clean 40-question set (and 36–39 variants) and `XCHECK-r<n>.md`
  notes. One template world per variant is built per session and copied whole into each test's `tmp_path`.
- **`HOME`** of every child process is a planted folder under `tmp_path`; `PYTHONUSERBASE` is kept as the test
  process has it, so the planted home changes no imported package. The true home's `~/gov-os-eval` and
  `~/gov-os-runs` are never opened (F3): `w2_170_world.TRUE_HOME` is used only to check the file-access log.
- **The file-access log (F3, S1's "no real ~/gov-os-eval is opened"):** `w2_170_open_log.py` installs
  `sys.addaudithook` for `open`, `os.*` and `subprocess.Popen` events, writes them to a file, then runs `gov.memaudit`
  with `runpy` as `__main__`. The case runs `preflight` (its default runs folder `~/gov-os-runs`, planted in the planted
  home), `void` and `declare` this way and fails on any logged path at or under the true home's `gov-os-eval` or
  `gov-os-runs`, and unless the log shows the planted questions and the planted home's runs folder opened. The
  repository under test's own root (the checkout this folder sits in, found from `w2_170_world.HERE`) is excluded
  from that judgement (W2-179, `DAEO-c9n8`): the nightly's clone lives at `~/gov-os-runs/W2-00/nightly/<run>/`, so its
  own source, tests and stores are not runs-folder opens; the root is compared with each logged path in the
  `realpath` form, and the case first asserts that it is not the true home, runs folder or sets root, nor an
  ancestor of one.
- **S4's measure:** `python3 -m gov.retrieval.measure memory-audit-20261111 --root <repo> --sets-root <root> --part
  hidden --kept <empty folder>` as the orchestrator (`GOV_ROLE=orchestrator`, a role no set measures): before
  `declare` it answers "not declared"; after, it declares the set accepted, covered and every question loaded, and
  stops only at the first call for want of a kept output (no retriever is ever started).
- **S6's selection:** a planted repository holding this tree's own `governance/project/test-map.yaml`, a stub for every
  target the map names, a planted `tests/unit/memaudit/` and one change `src/gov/memaudit/core.py`; its green nightly
  record names the base. `gov.close.select.plan` must answer `scoped` and name `tests/unit/memaudit/`.
- **F5:** judged **only on W2-170's own branch, `w2/W2-170`** (the checked-out branch of the repository this folder sits
  in, `w2_170_world.TREE`): there, `git diff --name-only <merge-base with w2/integrate>...HEAD`; allowed are the
  ticket's `allowed_paths` (matched by `gov.close.select.match`) and its own acceptance folder
  (`acceptance_tests.path`). On any other checkout (another ticket's branch, the merge queue's detached candidate merge,
  `w2/integrate`, a clone's checkout) it is **skipped with the reason named** (the branch found, or "detached HEAD"), as
  it is without the `w2/integrate` reference or the ticket file; never red, never passed silently. The judgement is one
  function, `judge_f5_paths(root)`, which the case calls with `TREE` and the planted cases call with each planted
  repository: in its own `git init` under `tmp_path`, `w2/integrate` holds a base commit and a copy of W2-170's ticket
  file, and one commit adds `docs/changes/W2-171-evidence.md` (outside W2-170's paths; W2-171's own file): on a branch
  `w2/W2-170` the judgement fails naming the path; on `w2/W2-171`, on a detached candidate merge of `w2/W2-171` into
  `w2/integrate` (`--no-ff`), and on `w2/integrate` itself it skips; a change inside `src/gov/memaudit/**` on
  `w2/W2-170` passes.
- No network, no GPU, no model, no store but the planted file. No case is marked `local_only`; no test, class,
  parameter id or file name holds `real`, `green_here` or `time_limit`.

Run from the ticket's worktree (with an empty `HOME` folder made first; `PYTHONUSERBASE` only where pytest is a user
install that the changed `HOME` would hide):

    env HOME=<empty folder> PYTHONUSERBASE=<the user base> PYTHONPATH=<worktree>/src TMPDIR=<tmp> \
      python3 -m pytest tests/acceptance/W2-170 -q -p no:cacheprovider -o tmp_path_retention_policy=failed \
      -m "not local_only" -k "not real and not green_here and not time_limit"

## Readings of the Interface these cases take (where its words leave a choice)

- **`say(...)`'s parameters** are not stated (section 8). The driver gives the line as the first argument and, when
  `say` has a parameter whose name holds `root`, the planted sets root by position under that name. Its refusal is
  judged by exit 4 and the exact line `REFUSED: a line that names a sets-root folder was not printed` on standard output
  or error.
- **`PREFLIGHT.json`'s keys** beyond `ok` are not named: the re-anchored and no-token counts are found as any key
  matching `re.?anchored` / `no.?token`, and each of the ten codes must appear in its text.
- **A code's printed block** is its line `PF-<NAME> ok|refused <n> ...` and any lines after it up to the next code or
  the closing line; ids are the `q<nn>` tokens in it; `PF-QUOTA` and `PF-SPREAD` name no id. PF-SPREAD's text holds
  `domain <name> <count>` / `subsystem <name> <count>` (section 3).
- **Not asserted** (left to the Interface's owner, named in the return): which other codes a `PF-FORM` or `PF-COUNT`
  defect also trips (whether a file refused by the form counts toward the quotas and the scale, and the quotas below
  36 files); how `preflight` answers a path map at the commit it cannot read (only that it answers with its codes or one
  `ERROR:` line and quotes nothing); whether `DC-DECISION` writes the map entry; whether a refused `void` makes the empty
  run folder (only "nothing moved" and no `DROPS.json`); `DROPS.json`'s `domains`/`subsystems` beyond the five domains'
  and seven subsystems' counts.
- **Ledger:** events `preflight`, `drop`, `void`, `declaration`, `used`, each line with `seq` (consecutive), `at` and
  `event`.

### Batch 2: reading 9 (section 10 item 9)

- **"Records each delivered file's sha256 by id"** names no key. Found key-agnostically, anywhere in `PREFLIGHT.json`:
  either (a) a JSON object whose keys are exactly the ids of the `q<nn>.yaml` files in `hidden/` (flat, not
  `dropped/`) at the pre-flight, each id's value that file's sha256 (lower-case hex of its bytes) or an object holding
  that digest as one of its values; or (b) a list of objects, one per delivered id, each pairing exactly one delivered
  id with exactly one 64-hex digest, the pairs exactly the expected ones. Checked on a clean 40, a clean 39, a refused
  pre-flight (`PF-COMMIT`) and a refused 35 (`PF-COUNT`): "each delivered file" is recorded whatever the verdict.
- **"Byte-equal"** is judged on bytes: a kept file whose YAML mapping is unchanged but whose bytes differ (a comment
  appended) is refused like a re-worded one; a whole set re-delivered with the same bytes and later file times goes on.
- **"A kept file"** is a `q<nn>.yaml` left in `hidden/` after `void`: a file round 2 replaced (or delivered new) that the
  checker's second pass then drops is not kept and need not match; a kept file whose id was never pre-flighted is
  refused.
- **"Writing nothing"** for this refusal is section 5's: exit 1, `DC-PREFLIGHT` printed, no `USED written` line, no
  `USED`, no `DECLARATION.json`, no `declaration` or `used` ledger line, no entry for the audit in the sets root's map
  (read with `gov.util.parts.evaluation_sets`), and every file under the sets root and the launch folder unchanged.
- **"Until it is pre-flighted again"**: the recovery case re-delivers a set that is valid as it stands; after
  `DC-PREFLIGHT`, `preflight` again exits 0 and records the new digests, and `declare` exits 0 and writes `USED`. (A
  replaced set that a pre-flight refuses is shown refused again, and `declare` still refuses; fixing its files would
  change `hidden/` after `DROPS.json`, which section 5 refuses as `DC-DROPS` while `void` refuses `DR-DONE`, so that path
  is not tested: named to the CTO as a gap.)

## KPI map

| KPI | tests | expected red reason |
|---|---|---|
| S1 | `test_w2_170_s1_preflight.py::test_s1_the_clean_set_passes_every_check_and_ends_with_the_exact_line`, `test_w2_170_s1_preflight.py::test_s1_a_refused_check_prints_one_line_per_code_in_the_kpi_order_and_writes_ok_false`, `test_w2_170_s1_preflight.py::test_s1_an_empty_dropped_folder_is_not_a_stray_folder`, `test_w2_170_s1_preflight.py::test_s1_an_absent_pool_folder_is_an_empty_pool`, `test_w2_170_s1_preflight.py::test_s1_pf_count_refuses_fewer_than_36_files`, `test_w2_170_s1_preflight.py::test_s1_pf_count_refuses_a_stray_file_or_folder_in_hidden`, `test_w2_170_s1_preflight.py::test_s1_pf_form_refuses_a_file_not_in_the_writer_brief_s_form`, `test_w2_170_s1_preflight.py::test_s1_the_optional_keyword_and_naive_answer_pass_the_form`, `test_w2_170_s1_preflight.py::test_s1_pf_commit_refuses_a_commit_other_than_the_audit_commit`, `test_w2_170_s1_preflight.py::test_s1_pf_quota_refuses_a_category_off_its_quota_and_names_no_id`, `test_w2_170_s1_preflight.py::test_s1_pf_quota_reads_at_most_for_36_to_39_files`, `test_w2_170_s1_preflight.py::test_s1_pf_quota_refuses_a_count_over_its_quota_at_38_files`, `test_w2_170_s1_preflight.py::test_s1_pf_spread_refuses_a_domain_under_4`, `test_w2_170_s1_preflight.py::test_s1_pf_spread_refuses_a_subsystem_over_10`, `test_w2_170_s1_preflight.py::test_s1_the_scale_lets_a_subsystem_hold_its_scaled_maximum`, `test_w2_170_s1_preflight.py::test_s1_the_scale_refuses_one_over_the_scaled_maximum`, `test_w2_170_s1_preflight.py::test_s1_the_scale_needs_4_of_a_domain_at_36_and_at_40`, `test_w2_170_s1_preflight.py::test_s1_the_domain_is_the_first_source_s_never_a_later_one`, `test_w2_170_s1_preflight.py::test_s1_a_charter_first_source_counts_for_the_contract_domain`, `test_w2_170_s1_preflight.py::test_s1_a_kernel_hook_first_source_counts_for_the_guard_subsystem`, `test_w2_170_s1_preflight.py::test_s1_pf_drawn_refuses_a_changed_question_whose_source_is_not_in_selection_json_s_changed`, `test_w2_170_s1_preflight.py::test_s1_pf_drawn_refuses_a_sample_question_whose_source_is_not_in_selection_json_s_sample`, `test_w2_170_s1_preflight.py::test_s1_pf_drawn_never_checks_a_drawn_none_question`, `test_w2_170_s1_preflight.py::test_s1_pf_drawn_derives_the_lists_from_the_launch_log_when_selection_json_is_absent`, `test_w2_170_s1_preflight.py::test_s1_pf_drawn_from_the_derived_lists_refuses_a_question_off_its_list`, `test_w2_170_s1_preflight.py::test_s1_selection_json_is_read_first_when_present`, `test_w2_170_s1_preflight.py::test_s1_pf_drawn_names_every_drawn_question_when_the_lists_cannot_be_had`, `test_w2_170_s1_preflight.py::test_s1_with_no_audits_log_nothing_is_changed_and_every_changed_question_is_named`, `test_w2_170_s1_preflight.py::test_s1_pf_source_refuses_a_source_not_found_at_the_audit_commit`, `test_w2_170_s1_preflight.py::test_s1_a_heading_not_found_with_lines_inside_passes_and_is_counted_re_anchored`, `test_w2_170_s1_preflight.py::test_s1_pf_evalns_refuses_a_source_in_an_evaluation_namespace`, `test_w2_170_s1_preflight.py::test_s1_pf_evalns_refuses_an_evaluation_source_given_as_an_alternative`, `test_w2_170_s1_preflight.py::test_s1_pf_duppool_refuses_a_gold_source_set_equal_to_a_pool_question_s`, `test_w2_170_s1_preflight.py::test_s1_pf_duppool_compares_sets_not_orders`, `test_w2_170_s1_preflight.py::test_s1_pf_duppool_lets_a_pool_question_with_other_lines_pass`, `test_w2_170_s1_preflight.py::test_s1_pf_idexists_refuses_a_nonexistent_id_question_whose_id_exists_at_the_commit`, `test_w2_170_s1_preflight.py::test_s1_pf_idexists_matches_whole_tokens_only`, `test_w2_170_s1_preflight.py::test_s1_pf_idexists_looks_at_the_audit_commit_not_the_tree`, `test_w2_170_s1_preflight.py::test_s1_a_nonexistent_id_question_with_no_id_token_is_counted_and_not_refused`, `test_w2_170_s4_map.py::test_f3_a_run_s_file_access_log_shows_no_open_of_the_true_sets_root_or_runs_folders`, `test_w2_170_s1_s3_preflighted_set.py::test_s1_preflight_json_records_each_delivered_file_s_sha256_by_id`, `test_w2_170_s1_s3_preflighted_set.py::test_s1_f1_the_digest_record_and_the_refusal_carry_ids_and_digests_only` | batch 1: `gov.memaudit` absent: the child exits 1 with "No module named gov.memaudit", no `PF-` line, no `PRE-FLIGHT:` line, no `PREFLIGHT.json`. Batch 2 (reading 9): `PREFLIGHT.json` records no sha256 by id (the record cases fail); the leak case passes |
| S2 | `test_w2_170_s2_void.py::test_s2_three_drops_go_on_with_37_kept_and_the_scales_recomputed`, `test_w2_170_s2_void.py::test_f4_five_drops_void_the_audit_with_no_used_and_no_declaration`, `test_w2_170_s2_void.py::test_s2_a_drop_that_leaves_a_domain_at_3_voids_the_audit`, `test_w2_170_s2_void.py::test_s2_void_count_is_reported_first_when_both_causes_hold`, `test_w2_170_s2_void.py::test_s2_a_subsystem_over_its_scaled_maximum_after_drops_is_recorded_and_does_not_void`, `test_w2_170_s2_void.py::test_s2_the_highest_notes_round_is_the_one_read`, `test_w2_170_s2_void.py::test_s2_the_highest_round_is_numeric_not_by_name`, `test_w2_170_s2_void.py::test_s2_a_line_that_does_not_fit_or_is_not_exactly_accept_is_dropped`, `test_w2_170_s2_void.py::test_s2_dr_notes_refuses_when_no_notes_exist_and_moves_nothing`, `test_w2_170_s2_void.py::test_s2_dr_notes_refuses_notes_without_a_questions_section`, `test_w2_170_s2_void.py::test_s2_dr_done_refuses_a_second_void`, `test_w2_170_s2_void.py::test_s2_void_writes_no_used_and_no_declaration_even_when_it_goes_on` | `gov.memaudit` absent: `void` exits 1 with no `DROPS:`/`VOID`/`DR-` line; nothing is moved and no `DROPS.json` is written |
| S3 | `test_w2_170_s3_declare.py::test_s3_declare_writes_every_key_of_the_declaration_with_its_value`, `test_w2_170_s3_declare.py::test_s3_the_bar_for_37_is_32_right_1_wrong_target_36`, `test_w2_170_s3_declare.py::test_s3_used_holds_one_line_naming_the_audit_and_the_declaration_s_sha256`, `test_w2_170_s3_declare.py::test_s3_a_planted_used_marker_alone_refuses_the_declaration`, `test_w2_170_s3_declare.py::test_s3_the_pool_off_without_a_decision_is_named_and_not_ok_and_writes_no_used`, `test_w2_170_s3_declare.py::test_s3_the_pool_off_with_a_decision_is_ok_and_writes_used`, `test_w2_170_s3_declare.py::test_s3_a_decision_with_the_standard_file_is_recorded_as_given`, `test_w2_170_s3_declare.py::test_s3_a_decision_not_of_the_form_dec_n_is_a_usage_refusal`, `test_w2_170_s3_declare.py::test_s3_the_commit_flag_is_resolved_to_40_hex_digits`, `test_w2_170_s3_declare.py::test_s3_preflight_makes_the_audit_s_run_folder_with_mode_700`, `test_w2_170_s3_declare.py::test_s3_each_dc_refusal_exits_1_with_its_code_and_writes_nothing`, `test_w2_170_s3_declare.py::test_s3_dc_preflight_refuses_a_preflight_that_was_not_ok`, `test_w2_170_s3_declare.py::test_s3_dc_drops_refuses_a_void_audit`, `test_w2_170_s3_declare.py::test_s3_dc_retrieval_refuses_a_missing_or_unmapped_retrieval_yaml`, `test_w2_170_s1_s3_preflighted_set.py::test_s3_rv1_files_replaced_after_a_clean_preflight_are_refused_by_dc_preflight_writing_nothing`, `test_w2_170_s1_s3_preflighted_set.py::test_s3_a_kept_file_rewritten_but_still_valid_is_refused_by_dc_preflight`, `test_w2_170_s1_s3_preflighted_set.py::test_s3_a_kept_file_whose_id_was_never_preflighted_is_refused_by_dc_preflight`, `test_w2_170_s1_s3_preflighted_set.py::test_s3_f2_a_replaced_set_preflighted_again_is_declared_and_marked_used`, `test_w2_170_s1_s3_preflighted_set.py::test_s3_f2_a_byte_identical_redelivery_after_the_preflight_goes_on`, `test_w2_170_s1_s3_preflighted_set.py::test_s3_f2_files_dropped_after_round_two_need_not_match_the_preflight` | batch 1: `gov.memaudit` absent: the flow's `preflight` exits 1 (not 0), so no `PREFLIGHT.json`, `DROPS.json`, `DECLARATION.json` or `USED` exists to judge. Batch 2 (reading 9): `declare` exits 0 and writes `USED` for kept files that differ from (or were never in) the pre-flight, where exit 1 and `DC-PREFLIGHT` are required; the byte-identical and dropped-file cases pass |
| S4 | `test_w2_170_s4_map.py::test_s4_the_sets_root_map_gains_exactly_one_entry_and_keeps_every_other_byte`, `test_w2_170_s4_map.py::test_s4_an_equal_entry_already_present_is_left_as_it_is`, `test_w2_170_s4_map.py::test_s4_dc_map_refuses_and_writes_nothing`, `test_w2_170_s4_map.py::test_s4_the_measure_accepts_the_declared_set_from_the_sets_root_s_map`, `test_w2_170_s4_map.py::test_f3_the_planted_repository_is_unwritten_after_every_subcommand` | `gov.memaudit` absent: no subcommand runs, the sets root's map gains no entry, and the measure keeps answering "not declared" |
| S5 | `test_w2_170_s5_counts_only.py::test_s5_preflight_json_holds_no_question_answer_path_or_heading`, `test_w2_170_s5_counts_only.py::test_s5_the_command_lines_name_only_the_sets_root`, `test_w2_170_s5_counts_only.py::test_s5_say_refuses_a_line_that_names_a_sets_root_folder`, `test_w2_170_s5_counts_only.py::test_s5_say_prints_a_line_of_ids_counts_and_codes`, `test_w2_170_s5_counts_only.py::test_s5_a_flag_naming_a_folder_under_the_sets_root_is_refused`, `test_w2_170_s5_counts_only.py::test_s5_a_sets_root_that_is_not_a_folder_is_refused`, `test_w2_170_s5_counts_only.py::test_s5_a_sets_root_inside_indep_walls_is_refused`, `test_w2_170_s5_counts_only.py::test_s5_an_audit_name_of_another_form_is_refused`, `test_w2_170_s5_counts_only.py::test_s5_an_unresolved_commit_is_refused`, `test_w2_170_s5_counts_only.py::test_f1_the_unique_words_reach_no_output_file_and_no_printed_line`, `test_w2_170_s1_s3_preflighted_set.py::test_s1_f1_the_digest_record_and_the_refusal_carry_ids_and_digests_only` | batch 1: `gov.memaudit` absent: exits 1 where 0 or 4 is required; `gov.memaudit.say` cannot be imported. Batch 2: passes (no word leaks today; it guards the new record) |
| S6 | `test_w2_170_s6_wiring.py::test_s6_each_subcommand_prints_its_usage_with_help_and_exits_0`, `test_w2_170_s6_wiring.py::test_s6_argparse_errors_exit_4`, `test_w2_170_s6_wiring.py::test_s6_the_scoped_selection_for_a_change_under_src_gov_memaudit_names_tests_unit_memaudit`, `test_w2_170_s6_wiring.py::test_s6_the_entry_points_for_w2_171_and_w2_172_exist` | `gov.memaudit` absent (`--help` and argparse exit 1; the entry points cannot be imported); today's test map places nothing under `src/gov/memaudit/`, so the selection is `full` with `UNPLACED` |
| F1 | `test_w2_170_s5_counts_only.py::test_f1_the_unique_words_reach_no_output_file_and_no_printed_line`, `test_w2_170_s5_counts_only.py::test_f1_the_words_of_a_dropped_question_reach_no_output`, `test_w2_170_s5_counts_only.py::test_f1_a_refused_malformed_question_s_text_is_never_quoted`, `test_w2_170_s5_counts_only.py::test_f1_an_unreadable_path_map_at_the_commit_is_never_quoted`, `test_w2_170_s4_map.py::test_s4_dc_map_refuses_and_writes_nothing`, `test_w2_170_s1_s3_preflighted_set.py::test_s1_f1_the_digest_record_and_the_refusal_carry_ids_and_digests_only` | batch 1: `gov.memaudit` absent: no subcommand answers (no `PF-`/`DC-`/`ERROR:` line), so no case reaches its grep. Batch 2: passes |
| F2 | `test_w2_170_s3_declare.py::test_f2_declaration_then_used_by_file_times_and_ledger_order`, `test_w2_170_s3_declare.py::test_f2_with_used_present_every_subcommand_exits_3_prints_used_and_writes_nothing`, `test_w2_170_s3_declare.py::test_s3_a_planted_used_marker_alone_refuses_the_declaration`, `test_w2_170_s1_s3_preflighted_set.py::test_s3_rv1_files_replaced_after_a_clean_preflight_are_refused_by_dc_preflight_writing_nothing`, `test_w2_170_s1_s3_preflighted_set.py::test_s3_a_kept_file_rewritten_but_still_valid_is_refused_by_dc_preflight`, `test_w2_170_s1_s3_preflighted_set.py::test_s3_a_kept_file_whose_id_was_never_preflighted_is_refused_by_dc_preflight`, `test_w2_170_s1_s3_preflighted_set.py::test_s3_f2_a_replaced_set_preflighted_again_is_declared_and_marked_used`, `test_w2_170_s1_s3_preflighted_set.py::test_s3_f2_a_byte_identical_redelivery_after_the_preflight_goes_on`, `test_w2_170_s1_s3_preflighted_set.py::test_s3_f2_files_dropped_after_round_two_need_not_match_the_preflight` | batch 1: `gov.memaudit` absent: no `DECLARATION.json`, `USED` or ledger line is written; nothing exits 3. Batch 2: `USED` is written for a set whose kept files were not the pre-flighted ones (as S3's row) |
| F3 | `test_w2_170_s4_map.py::test_f3_the_planted_repository_is_unwritten_after_every_subcommand`, `test_w2_170_s4_map.py::test_f3_a_refused_declaration_leaves_the_repository_unwritten`, `test_w2_170_s4_map.py::test_f3_a_run_s_file_access_log_shows_no_open_of_the_true_sets_root_or_runs_folders` | `gov.memaudit` absent: the subcommands exit 1 and the open-log runner's `runpy` raises `ImportError` (its exit 99). W2-179: the third case excludes the repository's own root (a clone under `~/gov-os-runs`), and any other open at or under the true sets root or runs folder still fails it |
| F4 | `test_w2_170_s2_void.py::test_f4_five_drops_void_the_audit_with_no_used_and_no_declaration`, `test_w2_170_s2_void.py::test_f4_no_dropped_question_is_deleted` | `gov.memaudit` absent: `void` exits 1, not 0 or 2, and nothing is moved to `hidden/dropped/` |
| F5 | `test_w2_170_f5_paths.py::test_f5_the_branch_changes_only_paths_the_ticket_allows`, `test_w2_170_f5_paths.py::test_f5_the_planted_paths_are_outside_and_inside_the_ticket_s_paths`, `test_w2_170_f5_paths.py::test_f5_planted_w2_170_branch_with_a_change_outside_its_paths_fails`, `test_w2_170_f5_paths.py::test_f5_planted_w2_170_branch_with_a_change_inside_its_paths_passes`, `test_w2_170_f5_paths.py::test_f5_planted_other_ticket_branch_with_the_same_change_is_skipped_with_its_reason`, `test_w2_170_f5_paths.py::test_f5_planted_candidate_merge_on_a_detached_head_is_skipped_with_its_reason`, `test_w2_170_f5_paths.py::test_f5_planted_integrate_branch_itself_is_skipped_with_its_reason` | the case judges only on `w2/W2-170` (there: passes while the branch changes only W2-170's paths and its folder) and is skipped, with the reason named, on any other checkout and without `w2/integrate`; the six planted cases pass today (they assert the judgement's fail or skip) |

## Revision (W2-180, DAEO-weh2)

`test_f5_the_branch_changes_only_paths_the_ticket_allows` diffed whatever branch the suite ran on against W2-170's own
`allowed_paths`, so it was red on any later ticket's branch (W2-171's, which adds `docs/changes/W2-171-evidence.md` and
its own acceptance folder) and would have been red on the merge queue's candidate merge of it, attributed to that
batch (PKG-W2-171-F5-1). A test designer revised it, with a Rewrite-Reason (DEC-866): the case now judges only on
`w2/W2-170` and skips with its reason elsewhere, and six planted cases (one a sanity check of the planted paths) guard
the judgement; no other case changed. The folder now holds 185 cases from 107 test functions (179 and 101 above, plus
these six).

## Expected red on today's integrated code

### Batch 2 (run 2, reading 9), on the merged implementation (`fcfe85cb1`)

Every batch-1 case passes (165, F5 included); 10 of batch 2's 14 cases fail, each for reading 9's reason only:

| case | cases | expected red reason |
|---|---|---|
| `test_w2_170_s1_s3_preflighted_set.py::test_s3_rv1_files_replaced_after_a_clean_preflight_are_refused_by_dc_preflight_writing_nothing` | 1 | `declare` exits 0 (`DECLARED: ...`, `USED written`) where exit 1 and `DC-PREFLIGHT` are required |
| `test_w2_170_s1_s3_preflighted_set.py::test_s3_a_kept_file_rewritten_but_still_valid_is_refused_by_dc_preflight` | 3 (re-worded, `keyword` marked, a comment appended) | the same: `declare` exits 0 and writes `USED` |
| `test_w2_170_s1_s3_preflighted_set.py::test_s3_a_kept_file_whose_id_was_never_preflighted_is_refused_by_dc_preflight` | 1 | the same |
| `test_w2_170_s1_s3_preflighted_set.py::test_s3_f2_a_replaced_set_preflighted_again_is_declared_and_marked_used` | 1 | its first `declare` (before the second pre-flight) exits 0 where `DC-PREFLIGHT` is required |
| `test_w2_170_s1_s3_preflighted_set.py::test_s1_preflight_json_records_each_delivered_file_s_sha256_by_id` | 4 (clean 40, clean 39, refused `PF-COMMIT`, refused 35) | `PREFLIGHT.json` holds no object or list pairing each delivered id with its file's sha256 |
| `test_w2_170_s1_s3_preflighted_set.py::test_s3_f2_a_byte_identical_redelivery_after_the_preflight_goes_on` | 1 | passes (guards against refusing an unchanged re-delivery) |
| `test_w2_170_s1_s3_preflighted_set.py::test_s3_f2_files_dropped_after_round_two_need_not_match_the_preflight` | 2 | passes (guards against checking files that are no longer kept) |
| `test_w2_170_s1_s3_preflighted_set.py::test_s1_f1_the_digest_record_and_the_refusal_carry_ids_and_digests_only` | 1 | passes (guards the new record and the new refusal against leaking a question, an answer, a path or a heading) |

### Batch 1 (run 1, before the implementation)

164 of the 165 cases fail and F5 passes. 163 fail because `gov.memaudit` does not exist: the child exits 1 with
"No module named gov.memaudit", or `gov.memaudit.say` and the entry points cannot be imported, or the open-log runner's
`runpy` raises `ImportError`. S6's selection case fails because today's `governance/project/test-map.yaml` places
nothing under `src/gov/memaudit/` (`full`, `UNPLACED`). F5 passes on this branch, which changes only this folder.
