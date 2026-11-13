# W2-124 acceptance tests (DAEO-mb2t): the semantic store fails named, adoption records it

Author: independent test designer (MR-3), STANDARD profile. Written from the ticket's KPI lines S1-S5, F1, F2, its
`## Interface` and run 1's P2 (b) and P3, never from the implementation. Run with the worktree's own code:
`PYTHONPATH=<worktree>/src python3 -m pytest tests/acceptance/W2-124 -m "not local_only" -k "not real and not green_here and not time_limit"`.

## The interface the cases hold

- Asked for = no `--no-embeddings` AND the path map has a namespace with `embedding_policy: embedded`; otherwise
  `result.stores.semantic = {status: not_recreated, requested: false, reason}` and no embedder is called (S2).
- Asked for and not recreated (unavailable, hung, failing part way): `GovError REBUILD_FAILED`, exit 1, details
  `{store: "semantic", reason, stores}`; human form `gov rebuild: REBUILD_FAILED: <message>` on stderr, the message holding the literal
  `store: semantic`; no warm-base record (`.gov-runtime/rebuild/stores.json`).
- `gov.close.rebuild_gate.semantic_failure(result)` and `check(result)`; the rule of the CTO's `rebuild_semantic_check.py`
  (a semantic store that is not `recreated` and not `requested: false`, or absent, is a failure).
- Adoption: A6 finishes; the committed A6 record and `gov adopt --lite --stage A6 --json` each hold
  `findings: [{code: SEMANTIC_NOT_RECREATED, store: semantic, reason, command: "gov rebuild"}]`.
- P2 (b): `gov rebuild` keeps exit 0 and `"ok": true`; its result carries `complete` and `not_built: [{store, reason}]`
  (`complete` is true exactly when `not_built` is empty; a store with `requested: false` is never in it).

## KPI map

| KPI id | tests | expected red reason (today's integrated code) |
|---|---|---|
| S1 | `test_w2_124_s1_semantic_fails_named.py::test_s1_unavailable_embedder_json_exits_1_named_semantic`<br>`test_w2_124_s1_semantic_fails_named.py::test_s1_unavailable_embedder_human_output_names_the_failure`<br>`test_w2_124_s1_semantic_fails_named.py::test_s1_embedder_failing_part_way_json_exits_1_named_semantic`<br>`test_w2_124_s1_semantic_fails_named.py::test_s1_hung_or_transient_failing_embedder_raises_rebuild_failed_semantic[hung]`<br>`test_w2_124_s1_semantic_fails_named.py::test_s1_hung_or_transient_failing_embedder_raises_rebuild_failed_semantic[part-way-500]`<br>`test_w2_124_s1_semantic_fails_named.py::test_s1_no_embeddings_exits_0_with_the_embedder_unavailable`<br>`test_w2_124_s1_semantic_fails_named.py::test_s1_a_healthy_embedder_recreates_the_semantic_store_and_prints_ok` | today `gov rebuild` exits 0 and prints ok with the semantic store `not_recreated` (unavailable, hung, part way); the `--no-embeddings` and healthy cases are controls and are green today |
| S2 | `test_w2_124_s2_nothing_to_embed.py::test_s2_nothing_to_embed_with_the_embedder_unavailable_prints_ok_and_is_not_asked[no-path-map]`<br>`test_w2_124_s2_nothing_to_embed.py::test_s2_nothing_to_embed_with_the_embedder_unavailable_prints_ok_and_is_not_asked[path-map-without-an-embedded-namespace]`<br>`test_w2_124_s2_nothing_to_embed.py::test_s2_nothing_to_embed_with_the_embedder_unavailable_prints_ok_and_is_not_asked[template-path-map-no-policy]`<br>`test_w2_124_s2_nothing_to_embed.py::test_s2_no_embedder_is_called_when_nothing_is_to_be_embedded[no-path-map]`<br>`test_w2_124_s2_nothing_to_embed.py::test_s2_no_embedder_is_called_when_nothing_is_to_be_embedded[path-map-without-an-embedded-namespace]` | no `not_built` list and no `requested: false` in `stores.semantic` today (ok and no embedder call are already true) |
| S3 | `test_w2_124_s3_adoption_records_the_finding.py::test_s3_stage_a6_finishes_without_an_error_with_the_embedder_unavailable`<br>`test_w2_124_s3_adoption_records_the_finding.py::test_s3_the_adoption_report_holds_the_named_finding`<br>`test_w2_124_s3_adoption_records_the_finding.py::test_s3_the_committed_a6_record_holds_the_named_finding`<br>`test_w2_124_s3_adoption_records_the_finding.py::test_s3_record_and_report_give_the_same_finding`<br>`test_w2_124_s3_adoption_records_the_finding.py::test_s3_a_healthy_embedder_adoption_holds_no_such_finding` | A6 finishes today but neither the report nor the committed record holds a `findings` list; the first case (A6 finishes) and the healthy control are green today |
| S4 | `test_w2_124_s4_close_and_prepare_gate.py::test_s4_the_close_check_reports_a_partial_store_failed` (6 cases: 3 planted results x result/envelope)<br>`test_w2_124_s4_close_and_prepare_gate.py::test_s4_check_raises_rebuild_failed_naming_the_semantic_store` (6 cases)<br>`test_w2_124_s4_close_and_prepare_gate.py::test_s4_a_store_recreated_or_not_asked_for_passes_the_check` (2 cases)<br>`test_w2_124_s4_close_and_prepare_gate.py::test_s4_rebuild_slot_exits_75_on_the_planted_partial_result`<br>`test_w2_124_s4_close_and_prepare_gate.py::test_s4_rebuild_slot_exits_75_on_the_planted_result_with_no_semantic_store`<br>`test_w2_124_s4_close_and_prepare_gate.py::test_s4_rebuild_slot_passes_a_planted_whole_result` | `gov.close.rebuild_gate` does not exist (the gate cases fail on import); the `rebuild_slot.sh` cases are green today (the CTO's tool enforces the rule already) or skipped where the tool or the heavy slot is absent; the prepare half of S4 is S1's CLI cases (`gov rebuild --json` fails through `check()`) |
| S5 | `test_w2_124_s5_stores_not_built.py::test_s5_no_path_map_is_ok_incomplete_and_named`<br>`test_w2_124_s5_stores_not_built.py::test_s5_no_gitleaks_toml_is_ok_incomplete_and_named`<br>`test_w2_124_s5_stores_not_built.py::test_s5_a_store_the_path_map_calls_for_and_not_built_is_named`<br>`test_w2_124_s5_stores_not_built.py::test_s5_a_store_the_path_map_does_not_call_for_is_not_in_not_built`<br>`test_w2_124_s5_stores_not_built.py::test_s5_no_embeddings_is_ok_and_says_it_skipped_the_vectors`<br>`test_w2_124_s5_stores_not_built.py::test_s5_w2_26_finding_2_an_unadopted_clone_stays_ok_and_is_named_incomplete` | no `complete` and no `not_built` in the result today; with a path map and no `.gitleaks.toml` today's rebuild exits 1 (`REBUILD_FAILED` on the lexical index) where P2 (b) says exit 0 |
| F1 | `test_w2_124_f1_no_ok_over_a_partial_store.py::test_f1_no_gov_rebuild_run_prints_ok_over_a_partial_store[unavailable-json]`<br>`test_w2_124_f1_no_ok_over_a_partial_store.py::test_f1_no_gov_rebuild_run_prints_ok_over_a_partial_store[unavailable-human]`<br>`test_w2_124_f1_no_ok_over_a_partial_store.py::test_f1_no_gov_rebuild_run_prints_ok_over_a_partial_store[part-way-json]`<br>`test_w2_124_f1_no_ok_over_a_partial_store.py::test_f1_no_gov_rebuild_run_prints_ok_over_a_partial_store[part-way-human]`<br>`test_w2_124_s4_close_and_prepare_gate.py::test_f1_no_close_or_prepare_check_passes_a_partial_store` | today those runs exit 0 and print ok over a partial store; the close's check does not exist |
| F2 | `test_w2_124_s3_adoption_records_the_finding.py::test_f2_an_unavailable_embedder_never_fails_the_adoption_nor_hides_the_finding` | the adoption finishes today (no error exit) but its report and its A6 record hold no finding |

## What the cases do not do

- No real embedder or model: stand-ins on loopback ports only (unavailable = a closed port; part way = HTTP 400 from the second embed
  request on; hung = accepts and never answers; a healthy one for the controls). The hung and the HTTP 500 cases call
  `gov.rebuild.command.run` in-process with `gov.retrieval.semantic.TIMEOUT_S` set to 1 s and `RETRY_WAITS_S` to `(0.0, 0.0)`
  (the real values: 120 s and waits of 10 s and 30 s a failed request); nothing else is patched.
- The `rebuild_slot.sh` cases (S4) run the CTO's tool in `/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/`;
  they skip with their reason where the tool is absent or the heavy slot refuses.
- "Any other `REBUILD_FAILED` stays `INDEX_REFRESH_FAILED`" (Interface, adoption) is not a KPI line and has no case.
