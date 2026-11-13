# W2-88 acceptance tests: memory for any repository (the assessment, the plan, A9 lite, the store layout)

Ticket `DAEO-2bdu` (W2-88), profile FULL, class C2. **Run 4 (td-3, one narrow revision, 2026-11-13)** on the base `b1fe858ac` (the ticket
branch's head with P-W2-88-B-1 decided, DEC-1157 (3), (12), after review round 1 failed): B-1.1 + B-1.3 (A9's copy step, S16), B-1.2 (the reranker
and the bundle are the pin's constants, S11/F7), B-1.4 (the pool is the whole shipped block), B-1.5 (the secrets scan not run, S2), RV1-2 (a vector scan
that did not run, S5), RV1-4 (binaries a store holds, S3), RV1-5 (the code graph, unit seam), RV1-6 (a load does not make a stale store current, S10),
RV1-8 (the no-route rule, S1); the case list is in "Run 4 revisions" below; every other case stands as runs 2 and 3 wrote it. The suite is run on the
engineer's code now on the base (its files were never read, DEC-820). The guard refused the designer's read of the review record
(`docs/probes/DAEO-2bdu/**`, once; not worked round): the cases are written from the lead's statement of review round 1's behaviours and the ticket's
`## Interface additions (P-W2-88-B-1)`. **Run 3 (td-2, one narrow revision, 2026-11-13)** on the base `b482fc5bf` (the
ticket branch's head with P-W2-88-TD-1 decided, DEC-1157 (3), (12)): R1 (b) (A3), P-4 (the lock and `fabric.check_coverage`), P-10 (the
`retrieval.yaml` keys of the plant), P-1 (the planted over-budget S5 case and the planted low-measure S6 case), and the residuals
P-3, P-8, P-9 named; every other case stands as run 2 wrote it. Run 2 (run 1 stopped at the interface check; the CTO decided the
Interface, P-W2-88-IF-1 (a), DEC-1112 (3)): an independent test designer (MR-3) wrote these cases from the ticket's 23 success and 9 failure
lines, its `## Interface` (items cited below as **I1 to I7**) and its sources, before any implementation, on the ticket branch's head
`32d10098b0b7` (the base). Nothing of the ticket's implementation was read (`assess.py`, `refactor_plan.py`, `fabric.py`,
`memory_sets.py`, `store/layout.py` and the changes to `command.py`, `project.py`, `stages.py`, `rebuild/command.py`, `loader.py`
and `tests/unit/*/test_w2_88*` do not exist on the base; no other branch was read). The four refusals of DEC-820 were kept: no secret
printed (the planted secret is W2-81's `Held` object, which never prints), no held-out qualification material, no counterpart's work, no
hidden half of an evaluation set (W2-81's README was read for "What W2-88 and W2-93 amy read" only; no hidden question was opened).

## Run

```
mkdir -p $TMPDIR/td88 .gov-runtime/scratch/empty-home
env HOME=$PWD/.gov-runtime/scratch/empty-home TMPDIR=$TMPDIR/td88 PYTHONUSERBASE=$HOME_REAL/.local PYTHONPATH=$PWD/src \
  bash <heavy_slot.sh> python3 -m pytest tests/acceptance/W2-88 -q -p no:cacheprovider -o tmp_path_retention_policy=failed -rfE --tb=line
```

`-k "not real and not green_here and not time_limit"` selects nothing out: no case has those words in its name. No case is marked
`local_only` (no case needs this machine: the real code-graph tool and the real `HOME` are never used; the cases that need the code
graph use its absence, see "The code graph"). About 6 minutes with the heavy slot free (an A9 world is 15 to 20 s; four are shared
by module).

**Which code runs (DEC-732).** The support module finds the repository from its own location (`tests/acceptance/W2-88` -> the worktree's
`src/`), puts that `src/` first on `sys.path` and on every child's `PYTHONPATH`. Every `gov` the cases start is
`python -m gov.cli.main ...` (or `python -m gov.memaudit ...`) on a repository planted in `tmp_path`. No network (the embedder is
W2-124's stand-in on a loopback port, healthy), no real clone, never this repository's store or `.gov-runtime/store.db`, `HOME` is an empty
folder, the rebuild lock is the case's own. Every temp tree is removed after its case or module (`box` fixture, `Worlds.close`), the
largest being F4's 6,000-file tree (about 94 MiB, under the file budget of DEC-898).

**Reused read-only from other suites (never edited):** W2-124's `Embedder`/`make_box`/`environment`/`plant` and its adoption driver
(`w2_124_support`); W2-81's planted-secret builder (`w2_81_secret.make_secret("cloud-access-key", ...)`, gitleaks rule
`aws-access-token`) and its builders (`w2_81_build.build_all`, run into the case's folder); W2-170's planted sets world
(`w2_170_world`); W2-76's lock holder; W2-116's project builders (`make_project`, `land_h2`, `integration_build`); W2-172's `status_repo`.

## The interface the cases hold (I1 to I7), and the readings this suite makes

- **I1** `gov adopt --lite --stage MA --out <folder>`: the record's fields (`commit`, `tracked_files`, `tracked_bytes`, `languages`,
  `commits`, `largest[]`, `binary[]`, `generated[]`, `minified[]`, `vendored[]` as `{path, by}`, `secrets[]` as `{path, rule}`,
  `no_route[]` as `{path, reason}`, `estimate{...}`, `peak_rss_bytes`); `refactor-plan/RP-<nn>-<kind>.md`, `PLAN.md`,
  `NOTHING-TO-REFACTOR.md`; `OUT_INSIDE_PROJECT`; the seven kinds. Readings: (a) a category item may name a file or a folder it lies in
  (`holds`); (b) the triggers the Interface leaves open are pinned by the plants: a vendored folder is `vendor/`; a generated file is
  found by the header `# Code generated by tablegen. DO NOT EDIT.` (by `header`); a minified file by the name `*.min.js` (by `name`);
  a vendored file with no folder of its own by the header `# Vendored from github.com/acme/lib ...`; a binary by NUL bytes; an unsupported
  language by `.cob`; over the limit by size (`assess.FILE_LIMIT_BYTES` + 4,096, read from the module, 1 MiB where the module is absent
  so a case still plants) or a line of `chunking.READ_CHARS + 100`; the secret's rule id is `aws-access-token` (gitleaks' default rule for
  W2-81's `cloud-access-key` form); (c) a vendored or generated folder that holds its code in a folder of its own is no blocker
  (the plan's controls); (d) the namespace case is a namespace whose `embedding_policy` is `summary only`; (e) every proposal's
  `allowed_paths` reaches the file it is about (the path map for `namespace-policy`).
- **I2** A3's `--assessment <folder>`, `ASSESSMENT_MISSING`, A3's record cites the assessment's sha256. Readings: the assessment is
  "for HEAD's commit" when it was made at HEAD: MA is run after A2 (the chain driver's order), and an assessment of an earlier commit is
  `ASSESSMENT_MISSING`. **R1 (b), decided (P-W2-88-TD-1, DEC-1157 (3); Rewrite-Reason DEC-1156 (7)):** A3 refuses with
  `ASSESSMENT_MISSING` only when `--assessment` is given and holds no `memory-assessment.json` for HEAD's commit; a bare A3 (no
  `--assessment`) runs as today and its committed record says `assessment: none` (the case reads the record's text for that line).
  "MA before A3" is carried by the adopt skill's order (W2-88a's S17), not by a refusal. (Run 2 had read a bare A3 as a refusal:
  risk R1, five suites call A3 bare; decided away.)
- **I3** `gov adopt --lite --stage A9 --out <folder> [--decision DEC-n]...`: the record's blocks (`stores`, `digests`, `standard`, `scale`,
  `measure`, `refresh`, read from the committed record's frontmatter), `FABRIC_INCOMPLETE`, `STANDARD_DEPARTURE`, `SCALE-PROPOSAL.md`,
  `memory-audit/` (`AUDIT-RECORD.json`, `briefs/`, `ACT-WALLS/`, the cost block). A9 follows A8: the chain driver runs A0..A8 with W2-124's
  planted harbour (one move batch is a `DELETE_FROM_ACTIVE_TREE`; nothing to retire at A8; the chain reaches A8 on the base). Readings:
  `stores.<s>.indexed` is a count or a list (both accepted: `judged == count(indexed) + len(refused)`); the departure keys of a planted
  `retrieval.yaml` are the engineer's (P-10, run 3): pool off is `pool: {meaning_uncut: false, ...}` (the shipped block's other keys
  kept), a second reranker is `rerank: {service: private}`, another bundle budget is `bundle: {tokens: 4000}`; the departure is named in
  `standard.departures[].setting` by `fabric.STANDARD`'s name (the cases look for the word `pool`, `reranker` or `bundle`, each contained
  in `pool`, `reranker_service`, `bundle_tokens`) and, for the two with a value, carries `private` / `4000` in `value`; a
  `--decision DEC-n` is cited in `standard.departures[].decision`. **P-1 (run 3):** `--budget-ms <N>` plants the retrieve budget
  (over is `vector_scan_ms > budget_ms`; it writes `<out>/SCALE-PROPOSAL.md`); `--questions <file>` (`form: w2-88-questions/1`,
  `questions: [{id, question, gold, forbidden?}]`) plants A9's question set; without it `measure` is null with the residual `questions`.
  **P-4 (run 3):** S3's lock reads "never two at once" (a second rebuild waits, serialised); F2's "a file in neither list" is the unit
  seam `fabric.check_coverage(record, tracked)` raising `FABRIC_INCOMPLETE` with `details["missing"]` the sorted paths (the lexical store
  judges every tracked file; the refused reasons add `not-indexed`).
- **I4** modules: `assess.assess`, `assess.FILE_LIMIT_BYTES`, `refactor_plan.plan`, `fabric.a9`, `fabric.STANDARD`,
  `fabric.check_digests` (called with `{"digests": {...}}`), `memory_sets.audit_record|variants|walls_act|cost|launch_check`
  (`launch_check(variant, approved) -> 0|10`, and `python -m gov.adopt.memory_sets launch-check <variant> <approved>`, positional).
- **I5** `store/layout.py` and the open path: a loaded store is stamped (`LAYOUT_VERSION = 2`); an older (1) and a newer (3) stamp are
  `STORE_LAYOUT_STALE` with `details {found, expected}` and both numbers in the message, never `STORE_MISSING`; a store from before
  W2-03's `register_entries.span` (hand-built, unstamped) is stale with `found: 0`; **an unstamped store with complete tables is
  current** (the guard of the 35 hand-built stores); `gov rebuild` replaces each and reports `layout: {found, expected, rebuilt: true}`.
  The stamp's columns are not stated, so the planted stamps are made by rewriting every column of `store_layout` that holds the
  current version (`plant_store.py`), checked afterwards through `layout.version_of`.
- **I6** `digests: {record, lexical, vectors, codegraph_bytes}`; `digest` unchanged and equal to `digests.record`;
  `fabric.check_digests` refuses `DIGESTS_INCOMPLETE`.
- **I7** not this ticket's code: the guard's refusal of a measured role's read (existing: judged through `gov.guard.reads.parts`),
  S15's skill and T-0 text (judged on the template sources adoption copies, and on the copy a planted adoption holds), `retrieve.py`.
- **The three proposals** (`FILE_LIMIT_BYTES`, the retrieve budget's source, the code graph's language list) are never pinned: the limit
  is read from `assess.FILE_LIMIT_BYTES` / `chunking.READ_CHARS`, the per-session figure from `gov.resources.config` (`working_size_bytes`:
  the machine's `gate.json`, else the template's), and no case asserts a budget or a language list.

**The code graph.** `tests/conftest.py` takes the real code-graph tool off `PATH` for every suite not in its `_CBM_SUITES`, and the
child environments here do the same (the real tool is put on `PATH` only by `env(code_graph=True)`, which no case uses). So the planted
adoptions have code intelligence disabled (the path map's `capabilities.code_intelligence.enabled` false), and the case "a store the path
map calls for and not built" enables it with no tool: W2-124's way of planting an unbuilt store (the code index is `not_built`). The
code graph's nodes, edges and bytes are therefore not asserted beyond their presence (`codegraph_bytes` reported, not compared). If the
engineer needs the real tool in a case, `W2-88` joins `_CBM_SUITES` in `tests/conftest.py` (outside this ticket's paths: package P-3).

## KPI map

The ticket's success lines in file order are `success-1` to `success-23` as `gov accept` counts them (the two indented proof lines (a) and
(d) are `success-8` and `success-9`); the S-ids follow the brief's table by position, so the ticket's older inner labels do not shift them:
S1 assessment (1), S2 plan (2), S3 A9 lite (3), S4 structure (4), S5 scale (5), S6 measure (6), S7 proofs record (7), S8 proof (a) (8),
S9 proof (d) (9), S10 layout stale (10), S11 the standard (11; the ticket's text calls it "S10"), S12 the refresh (12; "S11"), S13 the
tuning set (13; "S12"), S14 the verdict set (14; "S13"), S15 the bar (15; "S14"), S16 search again once (16; "S15"), S17 a miss is a result
(17; "S16"), S18 audit schedule (18), S19 variants (19), S20 one core (20), S21 first audit (21), S22 walls ACT (22), S23 cost (23);
`failure-1` to `failure-9` are F1 to F9. The `moved:` line is W2-124's and is not tested.
"Red on the base" is `32d10098b0b7`. Cases marked **GUARD** are green on the base **by design** (the core exists and the KPI is the
adopted repository's use of it, or the case guards a behaviour that must stay); each is named here with its reason.

| KPI id | tests | expected red reason on the base |
|---|---|---|
| success-1 (S1; I1, I2, I4) | `test_w2_88_s1_assessment.py::test_the_assess_module_states_its_limit_and_its_entry_point`, `test_w2_88_s1_assessment.py::test_s1_the_record_holds_every_field_i1_names`, `test_w2_88_s1_assessment.py::test_s1_the_counts_are_the_repositorys`, `test_w2_88_s1_assessment.py::test_s1_each_planted_item_is_under_its_category`, `test_w2_88_s1_assessment.py::test_s1_the_secret_is_named_by_rule_id_only`, `test_w2_88_s1_assessment.py::test_s1_the_assessment_writes_only_under_out`, `test_w2_88_s1_assessment.py::test_s1_out_inside_the_project_is_refused`, `test_w2_88_s1_assessment.py::test_s1_f1_the_repository_is_byte_identical_before_and_after`, `test_w2_88_s1_assessment.py::test_s1_f5_no_output_holds_the_secrets_value`, `test_w2_88_s1_assessment.py::test_i2_a3_without_an_assessment_for_head_refuses`, `test_w2_88_s1_assessment.py::test_i2_a_bare_a3_is_no_refusal_and_its_record_says_assessment_none`, `test_w2_88_s1_assessment.py::test_i2_an_assessment_of_an_earlier_commit_is_not_one_for_head`, `test_w2_88_s1_assessment.py::test_i2_a3_with_the_assessment_cites_its_sha256_and_copies_no_proposal`, `test_w2_88_s1_assessment.py::test_s1_peak_rss_on_every_synthetic_proof_repository_is_under_the_per_session_figure`, `test_w2_88_s7_s9_proofs.py::test_s1_the_largest_proof_repositorys_peak_rss_is_recorded_and_under_the_per_session_figure` | no `MA` stage ("invalid choice 'MA'"); no `gov.adopt.assess`; A3 has no `--assessment` (usage error, no `ASSESSMENT_MISSING`: `test_i2_a3_without_an_assessment_for_head_refuses`); a bare A3 runs ok on the base but its record does not say `assessment: none` (`test_i2_a_bare_a3_is_no_refusal_and_its_record_says_assessment_none`, R1 (b): red for the line, not for the run); the evidence record `docs/changes/W2-88-evidence.md` is not written |
| success-2 (S2; I1, I4) | `test_w2_88_s2_plan.py::test_the_plan_module_states_its_entry_point`, `test_w2_88_s2_plan.py::test_s2_one_proposed_ticket_per_blocker_of_the_seven_kinds`, `test_w2_88_s2_plan.py::test_s2_every_proposal_is_in_the_kernel_ticket_form_citing_the_assessment`, `test_w2_88_s2_plan.py::test_s2_each_proposal_reaches_the_file_it_is_about`, `test_w2_88_s2_plan.py::test_s2_plan_md_lists_every_proposal_and_a_vendored_folder_is_no_blocker`, `test_w2_88_s2_plan.py::test_s2_f1_no_tk_call_and_the_repository_is_unchanged`, `test_w2_88_s2_plan.py::test_s2_a_clean_repository_says_there_is_nothing_to_refactor` | no `MA` stage; no `gov.adopt.refactor_plan` |
| success-3 (S3; I3) | `test_w2_88_s3_a9_stores.py::test_s3_the_stage_ends_ok_and_commits_its_record_under_governance_adoption`, `test_w2_88_s3_a9_stores.py::test_s3_the_record_holds_per_store_every_field`, `test_w2_88_s3_a9_stores.py::test_s3_every_store_judges_what_it_indexed_or_refused_with_a_reason`, `test_w2_88_s3_a9_stores.py::test_s3_the_planted_refusals_carry_their_reasons`, `test_w2_88_s3_a9_stores.py::test_s3_f2_check_coverage_passes_a_record_that_leaves_no_tracked_path_out`, `test_w2_88_s3_a9_stores.py::test_s3_f2_check_coverage_names_a_tracked_path_that_no_list_of_the_lexical_store_holds`, `test_w2_88_s3_a9_stores.py::test_s3_f2_check_coverage_lists_every_missing_path_sorted`, `test_w2_88_s3_a9_stores.py::test_s3_f2_a_path_named_in_the_refused_list_alone_is_covered`, `test_w2_88_s3_a9_stores.py::test_s3_f2_check_coverage_raises_for_a_store_that_was_not_built`, `test_w2_88_s3_a9_stores.py::test_s3_a_second_rebuild_waits_for_the_first_under_w2_76s_lock` | no `A9` stage (the planted adoption reaches A8 on the base: "invalid choice 'A9'"); the lock case (P-4 (a): never two at once, a wait, not a refusal): A9 ends at once (usage error) instead of waiting; the six `check_coverage` cases (run 3): no `gov.adopt.fabric` on the base (ModuleNotFoundError inside the case) |
| success-4 (S4; I5, I6) | `test_w2_88_s10_layout.py::test_s4_layout_py_states_the_version_and_each_store_with_its_tables`, `test_w2_88_s10_layout.py::test_s4_every_table_the_layout_names_for_the_record_store_exists_in_a_loaded_store`, `test_w2_88_s10_layout.py::test_f3_a_rebuild_digest_set_has_four_digests`, `test_w2_88_s3_a9_stores.py::test_s4_the_record_holds_the_four_digests`, `test_w2_88_s3_a9_stores.py::test_s4_f3_check_digests_refuses_a_record_with_only_the_record_graphs_digest`, `test_w2_88_s3_a9_stores.py::test_s4_two_a9_runs_on_one_commit_give_equal_first_three_digests` | no `src/gov/store/layout.py`; the load stamps nothing; the rebuild result has no `digests`; no `gov.adopt.fabric`; no A9 |
| success-5 (S5; I3) | `test_w2_88_s5_s6_s11_a9_blocks.py::test_s5_the_record_holds_a_query_time_per_route_and_the_vector_scan_against_the_budget`, `test_w2_88_s5_s6_s11_a9_blocks.py::test_s5_a_proposal_exists_exactly_when_a_figure_is_over_the_budget`, `test_w2_88_s5_s6_s11_a9_blocks.py::test_s5_a_budget_of_one_millisecond_is_recorded_over_and_proposed_and_no_store_file_changes` | no A9 (the planted case, P-1 (a): A9 with `--budget-ms 1` on an adoption of 150+ embedded notes: `scale.budget_ms` 1, `vector_scan_ms` over it, `SCALE-PROPOSAL.md` a CIT-P form holding the figure, the stage ok, the store files unchanged: sha256 of `.gov-runtime/store.db` and every file under `.gov-runtime/codeintel/` taken when `gov.rebuild.command.run` returns and again when the process ends, SQLite side files left out) |
| success-6 (S6; I3) | `test_w2_88_s5_s6_s11_a9_blocks.py::test_s6_the_record_holds_the_measure_and_a_residual_is_named_with_its_cause`, `test_w2_88_s5_s6_s11_a9_blocks.py::test_s6_the_record_names_no_proof_repository_as_having_run_the_full_practice`, `test_w2_88_s5_s6_s11_a9_blocks.py::test_s6_a_question_set_whose_gold_is_never_retrieved_is_a_named_residual_and_no_failure` | no A9 (the planted case, P-1 (b): A9 with `--questions <file outside the project>` whose gold paths are tracked nowhere: ok, `hit_at_5` and `right_e2e` 0, `wrong_claims` 0, a residual with a cause naming the retrieval shortfall, none of the planted questions' unique word in any committed record or file under `--out`) |
| success-7 (S7) | `test_w2_88_s7_s9_proofs.py::test_s7_the_record_holds_a_section_for_proof_a_and_one_for_d`, `test_w2_88_s7_s9_proofs.py::test_s7_proof_a_names_each_field`, `test_w2_88_s7_s9_proofs.py::test_s7_the_plans_proposals_are_counted_and_their_kinds_named` | `docs/changes/W2-88-evidence.md` is not written (the engineer writes it last) |
| success-8 (S8, proof (a)) | `test_w2_88_s7_s9_proofs.py::test_s8_proof_a_has_a_section_for_each_synthetic_repository_with_its_commit`, `test_w2_88_s7_s9_proofs.py::test_s8_the_builders_output_path_is_under_the_proving_ground_and_none_of_it_is_in_the_repository` | the evidence record is not written; the proving-ground path is a string in it (no test builds there) |
| success-9 (S9, proof (d)) | `test_w2_88_s7_s9_proofs.py::test_s9_the_record_has_no_adoption_run_on_examins_copy_and_names_w2_27_for_it`, `test_w2_88_s7_s9_proofs.py::test_s9_a_planted_run_of_the_adoption_tools_against_examins_copy_is_found`, `test_w2_88_s7_s9_proofs.py::test_s9_a_planted_branch_without_such_a_run_has_none`, `test_w2_88_s7_s9_proofs.py::test_s9_this_branch_holds_no_adoption_run_against_examins_copy` | the record case is red (record not written). The two planted cases are the judge's own bite checks (**GUARD**, green); the branch case judges only `w2/W2-88` and is skipped elsewhere, naming the branch found |
| success-10 (S10; I5) | `test_w2_88_s10_layout.py::test_s10_a_current_store_opens_with_no_refusal`, `test_w2_88_s10_layout.py::test_s10_f3_an_older_or_newer_stamp_is_refused_naming_both_versions`, `test_w2_88_s10_layout.py::test_s10_a_store_from_before_w2_03s_span_column_is_stale_never_missing`, `test_w2_88_s10_layout.py::test_s10_gov_rebuild_replaces_a_stale_store_and_reports_the_layout`, `test_w2_88_s10_layout.py::test_s10_an_unstamped_store_whose_tables_are_complete_opens_as_current`, `test_w2_88_s10_layout.py::test_s10_no_store_at_all_is_still_store_missing` | no `gov.store.layout` (a store cannot be stamped or planted at another version); a pre-span store opens as current; the rebuild reports no `layout`. **GUARD (green on the base, must stay):** the unstamped-complete store opens as current (I5: the 35 hand-built stores), and no store at all is still `STORE_MISSING` |
| success-11 (S11, the standard; I3, I4) | `test_w2_88_s5_s6_s11_a9_blocks.py::test_s11_fabric_states_the_standard`, `test_w2_88_s5_s6_s11_a9_blocks.py::test_s11_the_record_names_the_four_settings_the_pin_the_embedder_the_reranker_and_the_digest`, `test_w2_88_s5_s6_s11_a9_blocks.py::test_s11_f7_a_departure_is_named_and_the_stage_is_not_ok_without_a_decision`, `test_w2_88_s5_s6_s11_a9_blocks.py::test_s11_f7_a_departure_with_the_owners_decision_is_ok_and_cites_it` | no `gov.adopt.fabric`; no A9. The departure cases now plant the pool only (run 4: `pool-off`, `pool-depth`); the `rerank`/`bundle` keys and the pin's constants are the run 4 cases (no reason red for package P-W2-88-B-1 remains). W2-145 (no private reranker, in progress, not in `waits_on`): the `reranker_service: shared` value is asserted on the record only |
| success-12 (S12, the refresh; I3) | `test_w2_88_s12_refresh.py::test_s12_the_record_names_the_refresh_command_and_its_hook`, `test_w2_88_s12_refresh.py::test_s12_the_act_package_installs_the_refresh_and_adoption_installs_nothing_itself`, `test_w2_88_s12_refresh.py::test_s12_a_merge_followed_by_a_query_returns_the_new_commit`, `test_w2_88_s12_refresh.py::test_s12_a_failing_build_keeps_the_old_store_and_reports_the_failure` | the first two: no A9. **GUARD (green on the base):** the last two hold W2-116's `gov rebuild --integration` behaviour on a planted repository (its code is on this head; they go red for W2-116, `waits_on` DAEO-f58b, if it is not) |
| success-13 (S13, the tuning set; I4) | `test_w2_88_practice.py::test_s13_the_proof_record_holds_the_sets_checks`, `test_w2_88_practice.py::test_s13_guard_a_planted_clean_set_passes_every_check_with_the_quota_met`, `test_w2_88_practice.py::test_s13_guard_a_planted_set_with_a_path_missing_is_refused_on_that_check` | the record case: the evidence record is not written. **GUARD (green):** the two planted-set cases hold `gov.memaudit preflight`'s checks on stand-in questions (the KPI is the adopted repository's use of the existing core, W2-170) |
| success-14 (S14, the verdict set; I4, I7) | `test_w2_88_practice.py::test_s14_guard_the_declaration_is_written_before_the_used_marker`, `test_w2_88_practice.py::test_s14_f6_guard_a_planted_used_marker_makes_the_runner_refuse`, `test_w2_88_practice.py::test_s14_f6_guard_a_measured_role_is_refused_a_read_of_the_set_and_the_orchestrator_is_not` | none red: all **GUARD (green)**, the core and the existing guard (ACT-GUARD-SETS-1) carry the line; they hold it for the adopted repository's use (S20 forbids a second copy) |
| success-15 (S15, the bar; I4) | `test_w2_88_practice.py::test_s15_guard_the_declared_bar_is_ceil_085_n_right_and_floor_005_n_wrong`, `test_w2_88_practice.py::test_s15_the_figures_printer_states_the_verdict_and_the_side_table` | **GUARD (green):** `declare`'s bar is ceil(0.85 n) / floor(0.05 n) (n = 40, 37) and `figures.verdict_lines` states the verdict and the side table; the result record `docs/research/W2-88-any-repository.md` is W2-88b's (no case: package P-2) |
| success-16 (S16, search again once; I7) | `test_w2_88_s16_search_again.py::test_s16_guard_the_source_adoption_copies_holds_the_four_phrases`, and the run 4 cases (see "Run 4 revisions") | the run-2 case `test_s16_a_planted_adoption_holds_the_retrieval_skill_unchanged` is replaced (B-1.1: the copy step is A9's; "red for package P-6" is removed). **GUARD (green):** the retrieval skill, `templates/brief.md` (T-0's carrier) and `templates/role-cto.md` (T-8's) already hold the four phrases on this head (W2-142 and W2-128 `waits_on`: red for them if the lines leave) |
| success-17 (S17, a miss is a result) | `test_w2_88_practice.py::test_s17_guard_the_runner_refuses_a_set_marked_used_and_changes_nothing` | **GUARD (green):** a set marked USED is refused (exit 3) and nothing is written. The result record's miss section needs the reader run (W2-171's scenario world): no W2-88 case, named in `unresolved` |
| success-18 (S18; I3) | `test_w2_88_s18_s23_memory_sets.py::test_s18_the_audit_record_holds_its_sets_root_names_mode_variants_and_first_date`, `test_w2_88_s18_s23_memory_sets.py::test_s18_the_variant_hashes_of_the_record_are_the_files_hashes`, `test_w2_88_s18_s23_memory_sets.py::test_s18_f9_adoption_starts_no_audit_installs_no_schedule_and_changes_no_sets_root` | no A9 |
| success-19 (S19; I3, I4) | `test_w2_88_s18_s23_memory_sets.py::test_s19_a_variant_differs_from_the_gov_os_brief_only_in_the_domain_table_and_the_blind_list`, `test_w2_88_s18_s23_memory_sets.py::test_s19_a_launch_under_a_variant_not_on_the_approved_list_exits_10` | no A9; no `gov.adopt.memory_sets` |
| success-20 (S20; I4) | `test_w2_88_s18_s23_memory_sets.py::test_s20_memory_sets_imports_from_gov_memaudit`, `test_w2_88_s18_s23_memory_sets.py::test_s20_f9_no_file_of_src_gov_adopt_defines_a_pre_flight_a_use_once_marker_or_figures` | the first: no `memory_sets.py`. **GUARD (green, must stay):** the AST scan of `src/gov/adopt/*.py` (names holding `preflight`, `used` or `figure`, outside an import) finds none today |
| success-21 (S21; I4) | `test_w2_88_s18_s23_memory_sets.py::test_s21_before_the_verdict_set_is_used_the_adoption_says_no_audit_is_due`, `test_w2_88_s18_s23_memory_sets.py::test_s21_the_baseline_line_holds_the_verdict_commit` | the first: no A9 (the line is read from the A9 files: package P-5). **GUARD (green):** `gov.memaudit baseline` takes the verdict commit (W2-172's code, unchanged) |
| success-22 (S22; I3) | `test_w2_88_s18_s23_memory_sets.py::test_s22_the_act_package_holds_the_walls_the_sets_root_the_approved_list_and_the_hidden_globs`, `test_w2_88_s18_s23_memory_sets.py::test_s22_adoption_never_applies_the_act_and_changes_nothing_of_the_sets_root_or_the_path_map` | no A9 |
| success-23 (S23; I3, I4) | `test_w2_88_s18_s23_memory_sets.py::test_s23_the_record_states_the_four_figures_and_the_figure_to_replace`, `test_w2_88_s18_s23_memory_sets.py::test_s23_cost_is_from_the_audit_packages_section_7_and_scales_with_the_set` | no A9; no `memory_sets.cost` |
| failure-1 (F1; I1) | `test_w2_88_s1_assessment.py::test_s1_f1_the_repository_is_byte_identical_before_and_after`, `test_w2_88_s2_plan.py::test_s2_f1_no_tk_call_and_the_repository_is_unchanged`, `test_w2_88_s1_assessment.py::test_s1_out_inside_the_project_is_refused` | no `MA` stage |
| failure-2 (F2; I3) | `test_w2_88_s3_a9_stores.py::test_s3_f2_check_coverage_passes_a_record_that_leaves_no_tracked_path_out`, `test_w2_88_s3_a9_stores.py::test_s3_f2_check_coverage_names_a_tracked_path_that_no_list_of_the_lexical_store_holds`, `test_w2_88_s3_a9_stores.py::test_s3_f2_check_coverage_lists_every_missing_path_sorted`, `test_w2_88_s3_a9_stores.py::test_s3_f2_a_path_named_in_the_refused_list_alone_is_covered`, `test_w2_88_s3_a9_stores.py::test_s3_f2_check_coverage_raises_for_a_store_that_was_not_built`, `test_w2_88_s3_a9_stores.py::test_s3_a_store_the_path_map_calls_for_and_not_built_is_never_ok` | the `check_coverage` cases (run 3, P-4 (a)): no `gov.adopt.fabric` on the base. They replace the run-2 case that deleted store rows after a rebuild (`a9_drop_file.py`, removed): no stage-level "file in neither list" case is kept, since none can be planted without deleting store rows. The unbuilt store at the stage level is the code graph called for with no tool: no A9 on the base |
| failure-3 (F3; I5, I6) | `test_w2_88_s10_layout.py::test_s10_f3_an_older_or_newer_stamp_is_refused_naming_both_versions`, `test_w2_88_s10_layout.py::test_s10_a_store_from_before_w2_03s_span_column_is_stale_never_missing`, `test_w2_88_s3_a9_stores.py::test_s4_f3_check_digests_refuses_a_record_with_only_the_record_graphs_digest`, `test_w2_88_s10_layout.py::test_f3_a_rebuild_digest_set_has_four_digests` | no `gov.store.layout`; no `gov.adopt.fabric`; no `digests` |
| failure-4 (F4; I1) | `test_w2_88_s1_assessment.py::test_f4_the_memory_grows_with_the_largest_file_not_with_the_tree_size`, `test_w2_88_s1_assessment.py::test_s1_peak_rss_on_every_synthetic_proof_repository_is_under_the_per_session_figure`, `test_w2_88_s7_s9_proofs.py::test_s1_the_largest_proof_repositorys_peak_rss_is_recorded_and_under_the_per_session_figure` | no `MA` stage. Margin: tree M (6,000 files of 16 KiB, about 94 MiB tracked) against tree S (10 files, the same largest file): M's recorded peak RSS may exceed S's by at most 40 MiB (under half the 90 MiB the tree is larger). Only the upper bound is asserted: a chunked implementation whose RSS does not grow with the largest file at all passes (package P-7) |
| failure-5 (F5; I1) | `test_w2_88_s1_assessment.py::test_s1_f5_no_output_holds_the_secrets_value`, `test_w2_88_s1_assessment.py::test_s1_f5_no_hidden_question_is_read_or_printed`, `test_w2_88_s1_assessment.py::test_s1_the_secret_is_named_by_rule_id_only`, `test_w2_88_s2_plan.py::test_s2_no_proposal_holds_the_secrets_value` | no `MA` stage |
| failure-6 (F6; I4, I7) | `test_w2_88_practice.py::test_s14_f6_guard_a_planted_used_marker_makes_the_runner_refuse`, `test_w2_88_practice.py::test_s14_f6_guard_a_measured_role_is_refused_a_read_of_the_set_and_the_orchestrator_is_not`, `test_w2_88_practice.py::test_s14_guard_the_declaration_is_written_before_the_used_marker` | none red: all **GUARD (green)**. "The tuning set's fixes cite no verdict question" has no seam (no checker, no record form): package P-8 |
| failure-7 (F7; I3) | `test_w2_88_s5_s6_s11_a9_blocks.py::test_s11_f7_a_departure_is_named_and_the_stage_is_not_ok_without_a_decision`, `test_w2_88_s5_s6_s11_a9_blocks.py::test_s11_f7_a_departure_with_the_owners_decision_is_ok_and_cites_it` | no `gov.adopt.fabric`; no A9 |
| failure-8 (F8) | `test_w2_88_practice.py::test_f8_a_variant_brief_keeps_the_products_own_search_forbidden`, `test_w2_88_practice.py::test_f8_guard_the_gov_os_briefs_forbid_the_products_own_search` | the variant case: no A9. **GUARD (green):** the Gov OS briefs' section 4 forbids `gov retrieve`. "A planted question whose record names a search call is refused by the checker": the checker is an Independent session with no mechanical check (package P-9) |
| failure-9 (F9; I3, I4) | `test_w2_88_s18_s23_memory_sets.py::test_s18_f9_adoption_starts_no_audit_installs_no_schedule_and_changes_no_sets_root`, `test_w2_88_s18_s23_memory_sets.py::test_s19_a_launch_under_a_variant_not_on_the_approved_list_exits_10`, `test_w2_88_s18_s23_memory_sets.py::test_s20_f9_no_file_of_src_gov_adopt_defines_a_pre_flight_a_use_once_marker_or_figures` | no A9; the AST scan is **GUARD (green)** |

The rows of success-11 and failure-7 above name the run-3 departure cases; run 4 changes them as the next section says (the "red for package
P-W2-88-B-1" reasons of the row and of P-10 below are removed: the loader's refusal of `rerank`/`bundle` is now the decided behaviour).

## Run 4 revisions (base `b1fe858ac`; every case below is named by its full node id; red reasons are as run on the base)

Every case of this section is in the KPI line named in its first column and was changed or added for the item named; each commit body names its item.
Cases the base already passes are named **GUARD** with the reason.

| KPI id / item | tests | red reason on the base `b1fe858ac` |
|---|---|---|
| success-16 (S16) / B-1.1 + B-1.3 | `test_w2_88_s16_search_again.py::test_s16_a_planted_adoption_holds_the_kernels_file_byte_for_byte_and_lists_it_installed` (one case per file: the retrieval and discovery skills' SKILL.md, T-0's brief.md, T-8's role-cto.md), `test_w2_88_s16_search_again.py::test_s16_the_copies_are_committed_in_a9s_own_record_commit_and_the_tree_is_clean`, `test_w2_88_s16_search_again.py::test_s16_the_copies_are_in_place_before_the_build_runs`, `test_w2_88_s16_search_again.py::test_s16_a_planted_adoption_holds_the_four_phrases_in_the_copy` (retrieval skill, T-0, T-8) | no file is copied by A9 (no `.claude/skills/...`, no `governance/kernel/templates/...`; `installed` is not in the record; nothing in the A9 commit; none present when the build begins) |
| success-16 / B-1.1 (W2-142) | `test_w2_88_s16_search_again.py::test_s16_a_planted_adoption_holds_the_discovery_skills_search_again_line` | **green on the head**: the copy step is built and W2-142's line (S2, merged: "searches once more in its own words before treating the question as unanswered") is in Gov OS's skill; revised in run 4 from the literal "search again once", which W2-142 did not decide for the discovery skill (the KPI asks the line copied unchanged). Red if the copy is absent or differs from Gov OS's skill, or the line leaves the skill |
| success-16 / B-1.3 | `test_w2_88_s16_search_again.py::test_s16_a_repository_with_no_retrieval_yaml_gets_gov_oss_s_and_a9_is_ok_with_no_decision`, `test_w2_88_s16_search_again.py::test_s16_a_repositorys_own_tracked_retrieval_yaml_is_kept_unchanged_and_listed`, `test_w2_88_s16_search_again.py::test_s16_the_default_planted_adoption_keeps_its_tracked_retrieval_yaml` | a repository with no `retrieval.yaml` is refused `STANDARD_DEPARTURE` (pool) and nothing is installed; no `kept` list in the record |
| success-16 / B-1.1 (a refusal) | `test_w2_88_s16_search_again.py::test_s16_a_refused_a9_leaves_no_copy_in_the_tree` | red for B-1.4 first: the pool-depth plant is not refused on the base (see below); once it is, the case judges that a refused A9 leaves no copy, no `.claude/`, a clean tree and an unmoved HEAD |
| success-16 | `test_w2_88_s16_search_again.py::test_s16_the_copy_plan_names_every_file_of_the_two_skills_and_both_templates` | **GUARD (green by design):** the suite's reading of Gov OS's own files (what the plan names exists) |
| success-11, failure-7 / B-1.2 | `test_w2_88_s5_s6_s11_a9_blocks.py::test_s11_f7_a_rerank_or_bundle_key_is_config_invalid_naming_it_and_no_decision_makes_it_ok` (key x with/without `--decision`: 4 cases) | **GUARD (green on the base):** `gov.config.loader` already refuses a top-level `rerank`/`bundle` key (`CONFIG_INVALID`, the key named, details `{file, key}`): the decided behaviour; the cases replace the run-3 `second-reranker`/`bundle-budget` variants of the two departure cases (a decided-behaviour revision, DEC-1157 (12)) |
| success-11, failure-7 / B-1.2 (in-process) | `test_w2_88_s5_s6_s11_a9_blocks.py::test_s11_f7_a_pin_constant_that_departs_is_named_by_departures_with_its_value`, `test_w2_88_s5_s6_s11_a9_blocks.py::test_s11_f7_read_standard_refuses_a_pin_constant_that_departs_without_a_decision`, `test_w2_88_s5_s6_s11_a9_blocks.py::test_s11_f7_read_standard_with_a_decision_returns_the_block_citing_it` (each over rerank.MODEL, rerank.SOCKET, retrieve.BUNDLE_BUDGET) | **red for the socket only** (`reranker_service` is still `shared` when `rerank.SOCKET` departs: `settings_of` does not read it); **GUARD (green on the base)** for the model and the bundle budget (the engineer's code already reads those two constants) |
| success-11 / B-1.2 | `test_w2_88_s5_s6_s11_a9_blocks.py::test_s11_the_pins_constants_as_they_stand_are_the_standard_and_no_departure` | **GUARD (green by design):** untouched constants: the four settings are the standard's, no departure |
| success-11, failure-7 / B-1.4 (RV1-1) | `test_w2_88_s5_s6_s11_a9_blocks.py::test_s11_f7_a_departure_is_named_and_the_stage_is_not_ok_without_a_decision[pool-depth]`, `test_w2_88_s5_s6_s11_a9_blocks.py::test_s11_f7_a_departure_with_the_owners_decision_is_ok_and_cites_it[pool-depth]`, `test_w2_88_s5_s6_s11_a9_blocks.py::test_s11_f7_a_pool_differing_from_the_shipped_block_in_any_key_is_a_departure_with_its_value[a-value-changed]`, `test_w2_88_s5_s6_s11_a9_blocks.py::test_s11_f7_a_pool_differing_from_the_shipped_block_in_any_key_is_a_departure_with_its_value[a-key-missing]`, `test_w2_88_s5_s6_s11_a9_blocks.py::test_s11_f7_a_pool_differing_from_the_shipped_block_in_any_key_is_a_departure_with_its_value[a-key-added]` | a pool block differing from the shipped one in a key (`route_depth: 5`, a key missing or added) is no departure on the base (A9 ok, `departures: []`, `fabric.departures` names nothing) |
| success-11, failure-7 / B-1.4 | `test_w2_88_s5_s6_s11_a9_blocks.py::test_s11_f7_a_pool_differing_from_the_shipped_block_in_any_key_is_a_departure_with_its_value[no-block]`, `test_w2_88_s5_s6_s11_a9_blocks.py::test_s11_f7_a_pool_differing_from_the_shipped_block_in_any_key_is_a_departure_with_its_value[meaning-off]`, `test_w2_88_s5_s6_s11_a9_blocks.py::test_s11_f7_a_pool_block_equal_to_the_shipped_one_is_no_departure`, `test_w2_88_s5_s6_s11_a9_blocks.py::test_s11_f7_a_departure_with_the_owners_decision_is_ok_and_cites_it[pool-off]` (now also value false) | **GUARD (green on the base):** pool off, no block and an equal block are judged as the interface states |
| success-5 (S5) / RV1-2 | `test_w2_88_s5_s6_s11_a9_blocks.py::test_s5_a_scan_that_did_not_run_is_null_with_its_reason_and_is_never_compared_with_the_budget[route-unavailable]`, `test_w2_88_s5_s6_s11_a9_blocks.py::test_s5_a_scan_that_did_not_run_is_null_with_its_reason_and_is_never_compared_with_the_budget[route-raises]` | the base records a figure for the vector scan whatever the semantic route answered (here 15 ms; `vector_scan_reason` absent) and does not take the scan through `fabric.vector_scan` |
| success-5 / RV1-2 | `test_w2_88_s5_s6_s11_a9_blocks.py::test_s5_a_measured_scan_over_a_budget_of_one_millisecond_is_recorded_proposed_and_no_store_file_changes` (the P-1 over-budget case, the scan planted through the seam: `available: True` after 0.05 s), `test_w2_88_s5_s6_s11_a9_blocks.py::test_s5_the_record_holds_a_query_time_per_route_and_the_vector_scan_against_the_budget` and `test_w2_88_s5_s6_s11_a9_blocks.py::test_s5_a_proposal_exists_exactly_when_a_figure_is_over_the_budget` (a null scan with its reason is read as a result; never compared with the budget) | **GUARD (green on the base):** the base's real route answers in the planted world (a figure over 1 ms), so the proposal and the byte-identical store hold; the seam is not used by the base. The case stays: it is the planted measured scan once the seam is used |
| success-3 (S3) / RV1-4 | `test_w2_88_s3_a9_stores.py::test_s3_a_tracked_binary_the_lexical_index_chunked_is_indexed_and_named_held_never_refused`, `test_w2_88_s3_a9_stores.py::test_s3_no_store_names_a_file_in_refused_while_the_store_holds_it` | the lexical store holds chunks of `assets/logo.bin` and the base lists it in `lexical.refused` as `binary`, not in `indexed`, with no `binary_held` |
| success-3 / RV1-4 | `test_w2_88_s3_a9_stores.py::test_s3_the_planted_refusals_carry_their_reasons` (revised: the binary is held or refused as binary, never both; the run-2 "refused as binary by some store" is gone) | **GUARD (green on the base, loosened by design):** the new cases above carry the rule |
| failure-2 (F2) / RV1-5 | `test_w2_88_s3_a9_stores.py::test_s3_f2_check_coverage_raises_for_a_code_graph_that_could_not_be_read_naming_codegraph` | **GUARD (green on the base):** the engineer's `check_coverage` already raises `FABRIC_INCOMPLETE` with `codegraph` in `not_built` for `{"built": false, "error": "x"}` |
| success-2 (S2), failure-1, failure-5 / B-1.5 (RV1-3) | `test_w2_88_s2_plan.py::test_s2_ma_with_no_gitleaks_writes_what_it_found_names_the_scan_not_run_and_is_not_ok`, `test_w2_88_s2_plan.py::test_s2_a_clean_repository_is_not_called_clean_when_the_secrets_scan_did_not_run`, `test_w2_88_s2_plan.py::test_s2_a_blob_over_the_scan_limit_is_named_unscanned_and_the_run_is_not_ok` | MA with no `gitleaks` on `PATH`, or with a blob over `assess.SCAN_LIMIT_BYTES`, ends ok (`SECRETS_UNSCANNED` is not raised), and a clean repository without the scan gets `NOTHING-TO-REFACTOR.md` |
| success-1 (S1) / RV1-8 | `test_w2_88_s1_assessment.py::test_s1_the_no_route_rule_names_the_code_languages_the_graph_does_not_read`, `test_w2_88_s1_assessment.py::test_s1_a_vue_a_ps1_and_a_proto_file_are_no_route_as_unsupported_language` | no `assess.OTHER_CODE_SUFFIXES` on the base; a `.vue`, a `.ps1` and a `.proto` file are in no list of `no_route` |
| success-10 (S10), failure-3 / RV1-6 | `test_w2_88_s10_layout.py::test_s10_f3_a_load_does_not_make_a_stale_store_current[unstamped-lexical-no-parent-0]`, `test_w2_88_s10_layout.py::test_s10_f3_a_load_does_not_make_a_stale_store_current[stamped-1-1]` | after `loader.load` the stale store (unstamped with `lexical_chunk` lacking `parent_id`; stamped 1) opens as current: the load stamps it |
| success-7 (S7) / RV1-7 | none | no proof case reads the evidence's scale figures (the fields it checks are commit, size, assessment, proposals, per-store figures, measure): no case revised or added |

**Existing MA cases and the B-1.5 rule.** None of the existing MA cases plants a blob over 16 MiB (the largest planted blob is 1 MiB + 4,096 B; W2-81's builders
are run with `SELF_TEST_LARGE` = 300,000 B; F4's trees are 16 KiB files) and none runs without gitleaks (every environment links the real scanner, the
suite skips without it): none expects the old behaviour, none is revised for it.

**Existing cases that expected `binary` in `refused`.** One: `test_s3_the_planted_refusals_carry_their_reasons` (revised above).

**Not testable here, a named residual (P-3's reason: the real code-graph tool is never run).** RV1-5's first half, "with the code graph called for, a
code file whose suffix is not in the graph's languages (`.cob`) is refused `unsupported-language` by the code graph and never indexed by it", is a
property of the record a built graph produces. It needs the code graph built, which this suite never does (and an unbuilt graph is `FABRIC_INCOMPLETE`: no
record). What is held: the unit seam above, and RV1-8's constants (`OTHER_CODE_SUFFIXES` disjoint from `CODE_GRAPH_SUFFIXES`). Where it goes: W2-27's first
full run (the real tool on `PATH`), or a package for a stand-in tool speaking the daemon's protocol (not built here).

**Run-4 bite checks** (`standin_b1/sitecustomize.py`, loaded in the parent when its folder is first on `PYTHONPATH` and in the children when `W2_88_STANDIN` names
it; it replaces on the product's own modules only `fabric.settings_of|departures|read_standard`, the stage A9 (the departure check, the scan seam, a record) and
`loader.load`): `env PYTHONPATH=$PWD/tests/acceptance/W2-88/standin_b1:$PWD/src W2_88_STANDIN=$PWD/tests/acceptance/W2-88/standin_b1 W2_88_STANDIN_MODE=<mode> ...
pytest tests/acceptance/W2-88/test_w2_88_s5_s6_s11_a9_blocks.py tests/acceptance/W2-88/test_w2_88_s10_layout.py -k "pool or pin_constant or read_standard or
scan_that_did_not_run or load_does_not or pins_constants"` (27 cases). `good` (as the interface states): **27 of 27 pass**. `pool-meaning-only` (the pool departs only
when `meaning_uncut` is not true): **5 fail** (the two `pool-depth` CLI cases, `a-value-changed`, `a-key-missing`, `a-key-added`). `scan-always-a-figure` (the scan's
time is a figure whatever the route answered): **2 fail** (`route-unavailable`, `route-raises`). `stamps-always` (the load stamps every store current): **2 fail**
(`unstamped-lexical-no-parent`, `stamped-1`). `constants-ignored` (reranker and bundle read from `retrieval.yaml`, not the pin's constants; run on the 13 constant
cases): **12 fail**, the untouched-constants guard passes. The measured-scan case needs a real build (`gov.rebuild.command.run`), which the stand-in A9 does not
run: it is not shown to bite on its own.

## Run 4b addition (L-1, DEC-1052, the lead's stated interface; base `89576e801a02`; five cases, one narrow addition)

What the stores will take is what the assessment and the plan say: the keyword index chunks a tracked binary's bytes as text, so (L-1a) a tracked
file over `assess.FILE_LIMIT_BYTES` is in `no_route` as `over-limit` whether text or binary (a binary over the limit is in `binary` and in `no_route`;
the plan proposes its `over-limit` ticket; a binary at or under the limit stays only in `binary`), and (L-1b) `estimate.chunks` is the chunks the
keyword index will make, binaries included. Planted by `w2_88_plan_support.plant_with_binary` (the clean repository plus `assets/big.bin`, a NUL byte
first); MA runs as every MA case runs it (gitleaks on `PATH`). No existing case plants a binary over the limit and asserts `no_route`, the plan or
`NOTHING-TO-REFACTOR.md` (the proving-ground builders run at 300,000 B and the case asserts the peak RSS only): no existing case is revised.

| KPI id / item | tests | red reason on the base `89576e801a02` |
|---|---|---|
| success-1 (S1) / L-1a | `test_w2_88_s1_assessment.py::test_s1_l1a_a_tracked_binary_over_the_limit_is_in_binary_and_in_no_route_as_over_limit` | a 2 MiB binary is under `binary` but `no_route` is empty: the base leaves a binary out of `no_route` |
| success-1 (S1) / L-1a (the edge) | `test_w2_88_s1_assessment.py::test_s1_l1a_a_binary_at_or_under_the_limit_stays_only_in_binary_and_one_byte_over_is_over_limit` | the binaries of 4 KiB and of exactly the limit pass (only in `binary`: kept, as today); the one of limit + 1 byte is in no `no_route` entry |
| success-1 (S1) / L-1b | `test_w2_88_s1_assessment.py::test_s1_l1b_the_estimate_counts_the_keyword_indexs_chunks_binaries_included` | no `estimate.chunks` on the base (`estimate` holds `index_seconds`, `estimated_nodes`, `estimated_edges`, ... only) |
| success-2 (S2) / L-1a | `test_w2_88_s2_plan.py::test_s2_l1a_a_tracked_binary_over_the_limit_gets_the_over_limit_proposal_and_no_nothing_to_refactor` | a repository whose only finding is a 2 MiB binary gets `NOTHING-TO-REFACTOR.md` and no `over-limit` proposal |
| success-2 (S2) / L-1a (the edge) | `test_w2_88_s2_plan.py::test_s2_l1a_a_binary_at_or_under_the_limit_gets_no_proposal_and_one_byte_over_gets_one` | the binaries of 4 KiB and of exactly the limit get no proposal and `NOTHING-TO-REFACTOR.md` (kept, as today); the one of limit + 1 byte gets no proposal |

The two edge cases hold their at-or-under-the-limit halves as part of the same case (green on the base by design) beside the over-the-limit half that is red;
no other new case is green on the base. Each binary size is planted in its own repository (alike but for that file's size), so the repositories of
`estimate.chunks` differ in that file only (2 MiB against 4 KiB: the interface's lower bound on the difference is `2 * 1048576 / 1200`). The suite's S1 and S2
modules with the bite checks (`test_w2_88_bites.py`): **58 cases, 5 failed (the five above), 53 passed**.

## Run 4 on the base (`b1fe858ac`)

Full run (`heavy_slot.sh`, `-rfE --tb=no`, 2026-11-13, HOME an empty folder, the sandbox's own TMPDIR): **199 cases, 34 failed, 163 passed, 2 skipped**
(the 152 of run 3, less the 5 that failed on this base for a reason now decided (the old P-6 case and the four `rerank`/`bundle` departure cases),
plus the run 4 cases of the table above). The 34 red are the run 4 cases the table marks red, each for its stated reason (the copy step, the pool, the
socket constant, the scan seam, the held binary, `SECRETS_UNSCANNED`, `OTHER_CODE_SUFFIXES`, the load that stamps); none by a collection, import or fixture
error. The cases the table marks **GUARD** pass on the base by design or because the engineer's code already holds that part. The 2 skipped are the branch
cases. `gov accept W2-88 --json` reads the map (no `ACCEPT_MAP_UNREADABLE`).

**Not a KPI line (not in the map above):** the path case (DEC-1155) `test_w2_88_f5_paths.py` (4 cases: the branch `w2/W2-88` changes only the
ticket's `allowed_paths`, judged with the close's own glob matcher; skipped, naming the branch found, on any other checkout, including this
tests branch; the planted cases judge a repository in `tmp_path`) and the bite checks `test_w2_88_bites.py` (24 cases, green by
design: they test the suite's own judges, see below).

## Bite checks (each check shown to bite)

- **Function-level, in the suite (`test_w2_88_bites.py`, green on the base):** S2's ticket form (one good ticket passes; seven mutants each
  fail on the defect: no `Verify:`, a wrong sha256, no failure KPIs, an unknown profile, no allowed paths, no title, no frontmatter); S19's diff
  (a variant that changes only the blind list and the domain table passes for the three briefs; one extra sentence in section 1 fails); S20's
  AST check (a `def run_preflight`, `USED =`, `compute_figures` and a class `Preflight` are flagged; imports from `gov.memaudit` are not);
  S7/S8's record sections; the byte-identical comparison (an edited file, an untracked file and an empty commit are each seen); the category lookup.
- **End to end, against stand-ins (`standin_ma/sitecustomize.py`, `standin/sitecustomize.py`; loaded in the children only when `W2_88_STANDIN` names the
  folder and `W2_88_STANDIN_MODE` the mode; never imported by a case, never part of the ticket's paths).**
  S1: the stand-in `MA` in mode `good` passes 10 of the 10 S1 cases it can serve (the I2 and module cases are deselected: `-k "not i2 and not
  assess_module"`); `leaky` (the secret's value in the record) fails the secret-by-rule and the no-value-in-any-output cases; `writes-repo`
  fails the byte-identical case; `no-out-check` fails the `OUT_INSIDE_PROJECT` case; `loads-tree` fails F4's memory case. S10: the stand-in layout in
  `good` passes the 10 cases that run in children (`-k "not layout_py and not every_table"`); `never-stale` fails 3 (older, newer, pre-span: the
  open path reads another layout as current); `wrong-found` fails 2 (the refusal's versions are not both named).
  Run: `env W2_88_STANDIN=$PWD/tests/acceptance/W2-88/standin_ma W2_88_STANDIN_MODE=<mode> ... python3 -m pytest ...`.
- **Run 3: `check_coverage` and the P-10 departure cases, against `standin_fabric/sitecustomize.py`** (a stand-in of the two seams as the engineer
  states them: a module `gov.adopt.fabric` holding only `check_coverage(record, tracked)`, and a stage `A9` doing the standard's departure check only,
  with the engineer's keys; modes by `W2_88_STANDIN_MODE`). It is loaded in the parent (for the in-process cases) when its folder is first on
  `PYTHONPATH`, and in the children when `W2_88_STANDIN` names it:
  `env PYTHONPATH=$PWD/tests/acceptance/W2-88/standin_fabric:$PWD/src W2_88_STANDIN=$PWD/tests/acceptance/W2-88/standin_fabric W2_88_STANDIN_MODE=<mode>
  ... python3 -m pytest tests/acceptance/W2-88/test_w2_88_s3_a9_stores.py -k test_s3_f2` (and `.../test_w2_88_s5_s6_s11_a9_blocks.py -k test_s11_f7`).
  `check_coverage` (6 cases): `good` passes 6 of 6; `coverage-never-raises` fails 4 (the two paths, the sorted list, the unbuilt store);
  `coverage-wrong-code` fails the same 4; `coverage-no-details` (the right code, no `missing`) fails the same 4; `coverage-refused-is-missing` (a path named only
  in a refused list is reported) fails 5 (the complete record, the two paths, the sorted list, the refused-alone case); `coverage-absent-store-ok` (a record with no
  lexical store passes) fails 1 (the unbuilt store). The departure cases (6: two tests by three variants), with the stand-in's A9 and the keys the engineer
  named: `good` (the loader taking `rerank` and `bundle`, package P-W2-88-B-1 applied) **passes 6 of 6**; with the loader as it is on the base (the same stand-in
  before the loader was relaxed; the mode `loader-as-is`) **4 fail and the 2 `pool-off` cases pass**: all four are `CONFIG_INVALID: key 'rerank'/'bundle': unknown key
  (the keys are routing, pool)`, the red for package P-W2-88-B-1 seen on the CLI path; `blind` (an A9 that reads run 2's keys and so does not see the planted
  departures) **fails 6 of 6**; `never-refuses` (names the departure, never refuses) **fails 3 of 6** (the three "not ok without a decision" cases; the decided ones pass). The check that the departure's
  `value` carries `private` / `4000` passed against `good`; it is not shown to bite on its own.
  Not built as a stand-in: the S5 and S6 planted cases (a stand-in A9 would have to be the whole stage: the scale probe, the proposal, the record); they
  are red on the base for the stage's absence, and their asserts (figures, form, byte-identity, no question text) are read against the seams as stated.

## Red run on the base (run 2: 32d10098b0b7; run 3: b482fc5bf)

Run 3's full run on `b482fc5bf` (`heavy_slot.sh`, `-rfE --tb=line`, 2026-11-13): **152 cases, 98 failed, 52 passed, 2 skipped** (the 144 of run 2, less
the one F2 case that deleted store rows, plus the 6 `check_coverage` cases, the bare-A3 case and the two planted cases S5 and S6). The 52 green are the
**GUARD** cases and bite checks the table and "Bite checks" name (the core exists; `test_w2_88_bites.py`); the 2 skipped are the branch cases (`w2/W2-88`
is not the checked-out branch). Every red is red by a
stated reason in the table (the stage is not offered, the module or the file does not exist, the record is not written, the line is not in the record);
none by a collection, import or fixture error: the stage-not-offered assertion is in the case body (`assert_offered`), the fixtures (`worlds`, `box`)
never assert. **Base-red rule:** every case changed or added in run 3 is red on the base (the table's last column says why); none is green.

## Packages (questions the Interface leaves open; the suite tests what is stated, never a guess)

- **P-1 (S5, S6: the planted over-budget and low figures): decided and built in run 3.** The engineer's seams: `gov adopt --lite --stage A9
  --budget-ms <N>` (default `fabric.RETRIEVE_BUDGET_MS`, 2000 proposed) and `--questions <file>` (`w2-88-questions/1`). The two planted cases:
  `test_s5_a_budget_of_one_millisecond_is_recorded_over_and_proposed_and_no_store_file_changes` and
  `test_s6_a_question_set_whose_gold_is_never_retrieved_is_a_named_residual_and_no_failure`. Two things they assume, named: (a) an
  adoption of 150+ embedded notes makes the vector scan take more than 1 ms (the smallest budget `--budget-ms` takes); if the engineer's
  `vector_scan_ms` excludes the scan proper and can fall under 1 ms on that adoption, the case says so by its message and the plant
  grows; (b) the S5 byte-identity check wraps `gov.rebuild.command.run` in the child (`a9_hash_stores.py`), as I3 says A9 calls it in
  full: an A9 that builds in another process makes the case say the plant did not take. No question is run through the reader here (the
  standing residual says so).
- **P-2 (S15, the result record).** `docs/research/W2-88-any-repository.md` is W2-88b's (DEC-1150 (1)); no file is stated here for the verdict line
  and the side table. The cases judge `gov.memaudit.figures.verdict_lines`'s text. Option: W2-88b's record is judged in W2-88b's suite (recommended).
- **P-3 (the code graph): a named residual (DEC-1157 (3)).** The cases never run the real tool (no `_CBM_SUITES` entry): the code graph's nodes and
  edges are asserted present only (`stores.codegraph.nodes`/`edges` are numbers, `codegraph_bytes` is reported, none compared), and the planted
  adoptions have code intelligence off. **Where it goes:** W2-27's first full run on EXAMIN's copy (the real tool there); no case here.
- **P-4 (F2 and S3's lock): decided in run 3 (P-4 (a), DEC-1157 (3)).** S3's lock reads "never two at once": the case holds the wait (a second
  rebuild is serialised, not refused; `gov.rebuild.watch.take` blocks). F2's "a file in neither list" is the unit seam `fabric.check_coverage(record,
  tracked)` (six cases, `test_s3_f2_*`); the run-2 case that deleted store rows is gone, and no stage-level "file in neither list" case is kept (none
  can be planted without deleting rows). One reading the seam leaves open and the cases do not decide: a store other than the lexical one (the vectors
  judging "a file of an embedded namespace", the code graph "a file of a language it reads") needs the path map or a language list that `check_coverage(record,
  tracked)` does not take; the cases use the lexical store (it judges every tracked file), and the stage-level unbuilt-store case stands for the rest.
- **P-5 (S21).** The KPI says `due` prints `not due: no verdict set used`; the Interface says `due` is unchanged (W2-172 prints `MODE`, `DUE`, `REASON`
  and `memaudit/` is not in this ticket's paths). The case reads the string from the A9 files (the audit record or ACT package), the only place this ticket can
  write it. Options: (a) as written here (recommended); (b) W2-172's `due` is changed by its own ticket.
- **P-6 (S16): decided in run 4 (P-W2-88-B-1, B-1.1 (a), B-1.3 (a)).** The copy step is A9's; the cases read the copies where the interface puts them
  (see "Run 4 revisions"). The run-2 case `test_s16_a_planted_adoption_holds_the_retrieval_skill_unchanged` is replaced; no reason red for package P-6 remains.
- **P-7 (F4): decided (DEC-1157 (3)), the upper bound only.** The KPI says the memory grows with the largest file; a chunked reader would not grow at all.
  The case asserts only the upper bound.

**Named residuals (no case; each with where it goes; DEC-1157 (3), (12)):**

- **P-3, the real code-graph tool:** the cases never run it; nodes and edges are asserted present only. Goes to **W2-27's first full run** (EXAMIN's copy,
  the real tool on `PATH`).
- **P-8, F6's "the tuning set's fixes cite no verdict question":** no checker or record form exists for a fix's citations; it is a practice-run check.
  Goes to **W2-27's first full run** (the tuning set's fix log read against the verdict set's gold sources). No case here.
- **P-9, F8's "a planted question whose record names a search call or a retrieval-work session is refused by the checker":** the checker is an
  independent session with no mechanical check in `gov.memaudit`. Goes to **W2-170** (the audit's checks, for the checker's refusal) and **W2-27's
  first full run** (the writer's session log read for a call of the product's search). No case here; the Gov OS briefs' ban on `gov retrieve` is the
  one **GUARD** case (`test_f8_guard_the_gov_os_briefs_forbid_the_products_own_search`).
- **P-10 (S11, F7): decided in run 3 and by P-W2-88-B-1 in run 4.** Only the pool departs through `retrieval.yaml`; the reranker and the bundle are the pin's
  constants, and a `rerank:` or `bundle:` key is `CONFIG_INVALID` naming the key (the loader refuses it first today, which is the decided behaviour). The
  run-3 `second-reranker`/`bundle-budget` CLI variants now assert that (decided-behaviour revision, DEC-1157 (12)); the constants are judged in-process
  (see "Run 4 revisions"). No reason red for package P-W2-88-B-1 remains.
- **Risk R1** (above): decided (b) in run 3: bare A3 runs and says `assessment: none`; the five suites that call it bare stay green.
