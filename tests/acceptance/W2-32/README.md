# W2-32 acceptance tests: retrieval components (S1–S5) and the rules on the record (S9, F1)

Ticket `DAEO-0pyc` (W2-32), profile STANDARD, round 1 (D-4b, DEC-1055). The independent test designer (MR-3) wrote
these cases from the ticket's KPI lines, its card (`docs/plan/WAVE_2_WBS.md`, W2-32), its list rows
(`docs/plan/WAVE_2_LIST.md`: W2-M073, W2-M191, W2-L065, W2-M103, W2-M104) and its sources (CAP-10.b, CAP-19.a,
CAP-19.c, DEC-954 Q9e, DEC-957). They were written before the implementation, without reading W2-32's new code; the
integrated code at `9c468dbd` was read for today's interfaces (DEC-963).

**Round 1:** S1 to S5, S9 and F1. **Round 2:** S3's hidden miss (the CTO's ruling), S10 (DEC-1065), S5's premise,
the map in the runner's form, and the stand-in reporting the GPU (below, "Round 2's rewrites"). Round 3: the hidden
miss made strict (P-W2-32-5). Round 4: S7, the owner's first gap (G1, DEC-1066); S8 (G3) and S6 (G2) come in later
rounds; round 10 adds DEC-1067 order (5)'s contextual headers. **167 cases from 77 test functions in thirteen files**, with a support module, a driver, the S9/F1 rule module
and a conftest. They run in under a minute on the engineer's head.

## How the tests reach the code under test

- `gov` is imported from whatever `PYTHONPATH` the run gives (DEC-732); a case fails unless it is this repository's
  `src/`. Every child process gets that folder first on its `PYTHONPATH`, and each driver call reports the `gov` it
  imported. Run from the ticket worktree:

      cd <worktree> && PYTHONPATH=<worktree>/src \
        python3 -m pytest tests/acceptance/W2-32 -q -p no:cacheprovider -o tmp_path_retention_policy=failed -rs

- **Public interfaces only:** `gov rebuild --json` (`python -m gov.cli.main`), `--no-embeddings`;
  `gov.retrieval.semantic.search(root, query, refresh=...)`, `semantic.refresh(root)` and `semantic.manifest(root)`;
  `gov.retrieval.fusion.search(root, query, limit, refresh=..., reranker=...)`;
  `gov.retrieval.rerank.rerank(query, candidates, reranker)` and `last_outcome()`;
  `gov.retrieval.retrieve.retrieve(root, query, reranker=...)`; the store `.gov-runtime/store.db` read as SQLite
  (`semantic_vector` joined to `lexical_chunk`, as W2-91's tests read it). One case rewrites a copy's
  `semantic_*` tables to the form a store built before W2-32 has (W2-L065, below). The S3 cases call the new
  interface stated below. No private function is called or patched.

## The interface these cases assume (to be stated in the ticket for the engineer)

The KPI lines do not name these. The cases assume the smallest forms below; the test designer's return proposes them
to the CTO so that the engineer builds to the same ones (spec gaps, DEC-136).

- **S1, S2: the embedder pin in configuration.** A project's `governance/project/models.yaml`:

      embedder:
        model: <the Ollama model name>
        revision: <the digest Ollama's model list reports, or a prefix of it of at least 12 hex digits>

  Absent, ADR-0002 §2's pin holds: `qwen3-embedding:0.6b` at `ac6da0dfba84…` (the tool registry's manifest sha256,
  which is the digest `/api/tags` reports). The file is read as it stands in the working tree, tracked or not
  (W2-M073). The pin is checked at every rebuild and every search: against the store's manifest and against the
  revision the endpoint reports.
- **Named errors.** A fail-closed answer carries an upper-case error code: one holding `UNPINNED` for a configured
  model without a revision (proposed: `MODEL_UNPINNED`), one holding `MISMATCH` for a revision or a model that does
  not match (proposed: `MODEL_MISMATCH`), and any upper-case code (two parts or more) that names the model for a
  pinned model the endpoint does not list. The code is looked for anywhere in the answer's text: in `gov rebuild`'s
  `result.stores.semantic` (its `reason`, or a field of its own), in `semantic.search`'s answer, and in the reason of
  `retrieve`'s `facets.semantic` (which has only `available` and `reason`, so the code goes in the reason).
- **W2-L065: the cut.** `semantic.manifest(root)` records the embedding cut under a key of its own besides
  `embedder` and `reranker` (the key and, since S7, the value are not judged here). A store whose `semantic_*` tables
  are only the vectors and the four-column manifest (two models and their revisions), as every store built before
  W2-32 is, is stale.
- **S7: the whole chunk** (G1, DEC-1066). The embedder is sent each chunk whole, and the reranker given it whole (its
  path line may come first): a chunk whose question words lie past character 600 is embedded with them, found by
  the semantic route nearer the question than when embedded from its first 512 characters (round 5: not "first",
  which the stand-in's bag of words decides at any cut), and given to a reranker with them. The manifest's cut is neither 512 nor 500. A store that
  records the cut as 512 (each store column named as a cut key of the manifest, or else holding its value, set back
  to 512), with the chunk's vector made from its first 512 characters, is stale (no answer) and the next rebuild
  embeds the chunk whole. `retrieve(root, question, batch_size=1, radius=0)` followed through its continuations
  sends no item whose sha256 an earlier bundle sent, and none within a span an earlier bundle sent. Its premise
  (round 6): a later bundle either holds another chunk of the expanded section, or names one as left out (a span
  record, with `path`, `start_line` and `end_line`, anywhere in the bundle but its evidence, its expansions and its
  not-gathered gaps, inside the section an earlier bundle sent).
- **S3: the memory-quality event.** `gov.retrieval.learning`:
  - `record(root, miss) -> dict`. `miss` holds `question`, `expected` (the sources the answer needed:
    `[{"path": …}]`), `observed` (the paths retrieval gave first), `root_cause`, `repair`, and `regression`: a case
    in the standing measure's question form (`question`, `gold_answer`, `sources`; W2-61, `gov.retrieval.measure`).
    It writes the event as a YAML (or JSON) file in the project, outside `.gov-runtime/`, and the regression case
    as a file of its own, and returns the event: `id`, `type: memory-quality`, `question`, `root_cause`, `repair`,
    `path` (the event file, relative to the root) and `regression_case` (the case file, relative to the root).
  - A miss without its `question`, `expected`, `root_cause`, `repair` or `regression` (absent or empty), or a case
    without its `question`, `gold_answer` or `sources`, raises a `ValueError` (or a `GovError`) whose message names
    the missing part, and writes nothing.
  - `events(root) -> list[dict]`: every recorded event, with the same fields.
  - "Held out": the case file is not embedded (no vector after a rebuild), as tests and probe records stay out of
    memory (DEC-1052).
  - **A miss on the hidden half** (the CTO's ruling, round 2) is recorded by its id only: no question text, gold
    answer, sources or regression case in the repository. A miss is hidden when its `id` is `H` and digits or it
    says `part: hidden`. Strict (P-W2-32-5, round 3): it carries its id (or `part: hidden`) and nothing else.
    Carrying its `question`, `expected`, `regression`, `root_cause` or `repair`, it is refused (a `ValueError` or a
    `GovError` whose message says it is hidden) and nothing is written; with its id only, it is recorded with no
    regression case and no text field (`question`, `expected`, `observed`, `root_cause`, `repair`, `regression`),
    and no file written holds its text, answer, source path, root cause or repair.
- **S10: no CPU fallback** (DEC-1065). With both embedders unreachable, `ollama.ensure_available()` and
  `ensure_query_available()` answer unavailable and start nothing; `semantic.search` answers unavailable with no hit
  and a named code; `retrieve` names the semantic part unavailable (a code in its reason) and still cites by keywords;
  `gov rebuild` refuses the vectors with a named code and still builds the keyword index. A model reported loaded on
  the CPU (`size_vram` 0 at `/api/ps`): a question's vector is refused, with a code, and neither vector cache gains a
  row; a rebuild refuses to embed (a code; no vector stored or cached).
- **S4: reported.** `last_outcome()` after the rerank, and `rerank` in a bundle, say `by: unavailable` with a reason
  that names the failure; the order given is kept, with no `rerank_score`. `fusion.search`'s answer says
  `reranked: false`.
- **S5: honoured or refused.** `fusion.search` with a limit returns exactly that many distinct hits (all that match,
  if fewer), or refuses a limit above its cap with a `ValueError` or a `GovError` naming the limit or the cap.

## The fixtures and the environment

- **Planted projects**, built from scratch in pytest's `tmp_path`: six short notes and a README (each about one
  thing, in words no other note uses), or 50 council notes for S5; this repository's path map with planted
  namespaces (only `docs/**` and `README.md` embedded), no register, no code index, no evaluation sets; the secrets
  scan off (DEC-1045), so no `gitleaks` is needed.
- **No model runs and no embedder is started** (the CTO's binding rule of 2026-11-03). The embedders are a stand-in
  for Ollama's HTTP interface on the loopback interface (`OLLAMA_HOST` and `GOV_QUERY_OLLAMA_HOST`), serving the
  pinned `qwen3-embedding:0.6b` (1,024 numbers) and a second model, `w2-32-stand-in-embed:1` (384), with vectors made
  of words; it can report another revision of the pinned model. It reports each model loaded on the GPU
  (`size_vram` equal to `size`), and on the CPU only in S10's cases. Every child gets an empty scratch `HOME`, a `PATH`
  with no folder holding `ollama` or `llama-server`, and `GOV_OLLAMA_BIN` pointing at a trap script that only leaves
  a marker and exits: **every case fails if a child tried to start an embedder.** The machine-wide vector cache and
  the rebuild lock are the test's own (the tests root conftest).
- **The rerankers** are stand-in loaders in the driver: a child process that prints its "loaded" line and exits,
  and the same failure raised directly (`BrokenPipeError`, `ConnectionResetError`, `EOFError`, a JSON decode error,
  `RuntimeError`). The default reranker is reached through a fake reranker environment in the scratch `HOME`
  (DEC-397's path), whose service ends at once and whose private worker prints "loaded" and exits. No model loads.
- `sqlite_vec` absent: the cases that build vectors skip, with the reason. Nothing is installed.

## KPI lines and their tests

Each item names its file and its test function in full, as `gov accept` matches them.

| KPI | Line (short) | Tests |
|---|---|---|
| S1 | Changing the embedder pin in configuration triggers a full re-embed, and the dev-tier retrieval regression passes [CAP-10.b] | `test_w2_32_s1_pin_swap.py::test_a_changed_embedder_pin_re_embeds_every_chunk_at_the_next_rebuild` (the pin changed in an untracked models.yaml, W2-M073: every vector the new model's, every chunk sent to it, the manifest names it and its revision); `test_w2_32_s1_pin_swap.py::test_removing_the_pin_change_re_embeds_every_chunk_with_the_default_pin_again`; `test_w2_32_s1_pin_swap.py::test_a_search_that_may_refresh_re_embeds_after_a_pin_change`; `test_w2_32_s1_pin_swap.py::test_after_the_swap_questions_are_embedded_by_the_new_model_and_the_planted_regression_passes` (each planted question embedded by the new model only, its note in the semantic route's first five and cited in retrieve's first five) |
| S2 | An unpinned or mismatched model fails closed with a named error [CAP-19.a, W2-M073, W2-M191, W2-L065] | `test_w2_32_s2_fail_closed.py::test_without_configuration_adr_0002s_pin_builds_and_the_planted_questions_are_answered` (the default pin); `test_w2_32_s2_fail_closed.py::test_an_endpoint_reporting_another_revision_of_the_pinned_model_fails_closed_at_rebuild` (a MISMATCH code, nothing embedded); `test_w2_32_s2_fail_closed.py::test_a_configured_model_without_a_revision_fails_closed_at_rebuild` (3 cases, an UNPINNED code); `test_w2_32_s2_fail_closed.py::test_a_pinned_model_the_endpoint_does_not_list_fails_closed_at_rebuild`; `test_w2_32_s2_fail_closed.py::test_a_search_after_the_endpoints_revision_changed_fails_closed`; `test_w2_32_s2_fail_closed.py::test_a_search_after_the_configured_pin_changed_without_a_rebuild_fails_closed`; `test_w2_32_s2_fail_closed.py::test_retrieve_reports_the_mismatch_as_an_unavailable_semantic_route`; `test_w2_32_s2_fail_closed.py::test_rebuild_without_embeddings_after_a_pin_change_leaves_no_vector_answering` (W2-M191); `test_w2_32_s2_fail_closed.py::test_rebuild_without_embeddings_after_a_file_changed_leaves_no_stale_vector_answering` (W2-M191); `test_w2_32_s2_fail_closed.py::test_the_manifest_records_the_embedding_cut` (W2-L065); `test_w2_32_s2_fail_closed.py::test_a_store_that_records_no_cut_is_stale_and_the_next_rebuild_renews_it` (W2-L065) |
| S3 | A retrieval miss is recorded as a memory-quality event with its root cause, its repair and a held-out regression case [CAP-19.c]; a hidden miss by its id only (the CTO's ruling) | `test_w2_32_s3_memory_quality.py::test_a_miss_is_recorded_as_a_memory_quality_event_with_its_root_cause_and_repair`; `test_w2_32_s3_memory_quality.py::test_an_event_without_one_of_its_parts_is_refused_and_nothing_is_written` (10 cases); `test_w2_32_s3_memory_quality.py::test_a_regression_case_not_in_the_measures_form_is_refused` (3 cases); `test_w2_32_s3_memory_quality.py::test_the_regression_case_is_a_question_in_the_measures_form_in_a_file_of_its_own`; `test_w2_32_s3_memory_quality.py::test_the_regression_case_is_held_out_of_what_memory_embeds`; `test_w2_32_s3_memory_quality.py::test_a_hidden_miss_is_refused_unless_it_carries_its_id_only` (18 cases, the ruling, strict: H07, h07, part hidden); `test_w2_32_s3_memory_quality.py::test_a_hidden_miss_with_its_id_only_is_recorded_without_its_text` (3 cases, the ruling); `test_w2_32_s3_memory_quality.py::test_recorded_events_are_read_back` |
| S4 | A reranker that dies after loading is reported, not raised [W2-M104] | `test_w2_32_s4_reranker_dies.py::test_rerank_with_a_reranker_that_dies_after_loading_keeps_the_order_and_reports_it` (6 cases, each searched twice); `test_w2_32_s4_reranker_dies.py::test_the_default_reranker_that_dies_after_loading_is_reported_not_raised`; `test_w2_32_s4_reranker_dies.py::test_the_fusion_with_a_dying_reranker_answers_unreranked_and_reports_it` (2 cases); `test_w2_32_s4_reranker_dies.py::test_retrieve_with_a_dying_reranker_cites_its_evidence_and_reports_the_rerank_unavailable` (3 cases) |
| S5 | The fusion limit is honoured [W2-M103] | `test_w2_32_s5_fusion_limit.py::test_a_limit_above_thirty_is_honoured_or_refused` (31, 40, 50 against all that match); `test_w2_32_s5_fusion_limit.py::test_a_limit_up_to_thirty_returns_exactly_that_many` (1, 5, 30); `test_w2_32_s5_fusion_limit.py::test_a_honoured_limit_keeps_the_order_of_a_smaller_one` (skips if the build refuses) |
| S9 | Below 85 % after two improvement rounds: escalated to the owner, who decides at the third; at 85 % or above but under 95 % with room, not closed: escalated [DEC-954 Q9e, DEC-957] | `test_w2_32_record.py::test_the_baseline_record_holds_both_figures_against_their_bars`; `test_w2_32_record.py::test_s9_escalates_below_85_after_two_rounds_and_under_95_with_room` (6 cases, the rule); `test_w2_32_record.py::test_the_evidence_file_states_s9s_and_f1s_outcome` (the verdict is judged by the record, below) |
| F1 | An improvement that lowers any baseline figure of W2-15a beyond its noise band is reverted | `test_w2_32_record.py::test_the_baseline_was_run_more_than_once_on_one_commit_so_it_has_a_noise_band`; `test_w2_32_record.py::test_f1_reverts_a_round_below_the_baselines_noise_band` (5 cases, the rule); `test_w2_32_record.py::test_the_evidence_file_states_s9s_and_f1s_outcome` (the verdict is judged by the record, below) |
| S10 | No CPU fallback for embeddings: the GPU embedders unreachable, the semantic part named unavailable and a keyword answer; no private embedder started; a vector computed on the CPU refused, never cached or stored; a rebuild refuses to embed on the CPU [DEC-1065, DEC-1031, ACT-RERANK-WAIT-1] | `test_w2_32_s10_no_cpu_fallback.py::test_ensure_available_with_the_embedders_unreachable_checks_health_only`; `test_w2_32_s10_no_cpu_fallback.py::test_a_search_with_the_embedders_unreachable_reports_the_semantic_part_unavailable_with_a_named_code`; `test_w2_32_s10_no_cpu_fallback.py::test_retrieve_with_the_embedders_unreachable_answers_by_keywords`; `test_w2_32_s10_no_cpu_fallback.py::test_a_rebuild_with_the_embedder_unreachable_refuses_the_vectors_and_starts_nothing`; `test_w2_32_s10_no_cpu_fallback.py::test_a_question_vector_computed_on_the_cpu_is_refused_and_nothing_cached`; `test_w2_32_s10_no_cpu_fallback.py::test_retrieve_with_the_query_embedder_on_the_cpu_answers_by_keywords`; `test_w2_32_s10_no_cpu_fallback.py::test_a_rebuild_with_the_embedder_on_the_cpu_refuses_to_embed` |
| S7 | The models read the whole chunk: the embedder and the reranker read each chunk in full (no 512/500-character cut below the chunk's size; the manifest's cut changes, so a full re-embed by S1), and parent expansion keeps its expanded parents across continuations (no span sent twice) [G1, DEC-1066] | `test_w2_32_s7_whole_chunk.py::test_the_embedder_reads_the_whole_chunk_and_the_semantic_route_finds_words_past_the_old_cut`; `test_w2_32_s7_whole_chunk.py::test_the_reranker_reads_the_whole_chunk` (2 cases: retrieve, the fusion); `test_w2_32_s7_whole_chunk.py::test_the_manifest_records_a_cut_that_is_not_the_old_one`; `test_w2_32_s7_whole_chunk.py::test_a_store_embedded_at_the_old_cut_is_stale_and_the_next_rebuild_embeds_the_chunk_whole`; `test_w2_32_s7_whole_chunk.py::test_across_continuations_no_span_is_sent_twice`; `test_w2_32_s7_dec1067.py::test_no_reranker_request_carries_more_than_16_texts_and_the_order_is_the_unbatched_one` (2 cases: the fusion, retrieve; DEC-1067 (f)); `test_w2_32_s7_dec1067.py::test_a_parent_expanded_later_leaves_out_the_children_sent_alone_earlier_and_names_them` (the converse, the review's F-5); `test_w2_32_s7_dec1067.py::test_a_chunk_above_the_embedders_limit_is_embedded_from_its_first_part_and_named`; `test_w2_32_s7_dec1067.py::test_nested_parents_send_no_line_twice_and_name_every_span_left_out` (a Python module and its functions, the round-2 review's R2-F1; a known failure, xfail strict: R2-F1 deferred to D-9 by the CTO, 2026-11-04, DEC-802, work parked at tag park/W2-32-R2-F1; it turns red when the behaviour is fixed and the mark is not removed); `test_w2_32_s7_size_bound.py::test_a_pool_of_long_chunks_goes_in_the_fewest_requests_within_16_texts_and_24000_characters` (2 cases: the fusion, retrieve; the review's S7-F4); `test_w2_32_s7_size_bound.py::test_a_chunk_above_the_budget_is_read_up_to_it` (2 cases); `test_w2_32_s7_headers.py::test_with_the_setting_on_each_chunk_is_embedded_after_a_header_of_its_path_and_the_headings_above_it` (DEC-1067 order (5): a title and nested sections); `test_w2_32_s7_headers.py::test_a_file_with_no_headings_is_embedded_after_a_header_of_its_path_alone`; `test_w2_32_s7_headers.py::test_the_header_is_deterministic`; `test_w2_32_s7_headers.py::test_a_headed_chunk_stays_within_the_embedders_limit`; `test_w2_32_s7_headers.py::test_the_keyword_chunk_and_the_evidence_are_unchanged_with_the_setting_on`; `test_w2_32_s7_headers.py::test_the_rerankers_input_is_unchanged_with_the_setting_on`; `test_w2_32_s7_headers.py::test_with_the_setting_absent_or_false_the_embedder_receives_the_chunk_as_today` (3 cases: no file, no key, false); `test_w2_32_s7_headers.py::test_an_invalid_setting_is_refused_with_config_invalid_naming_the_key` (4 cases: yes, 1, a quoted "true", a word); `test_w2_32_s7_headers.py::test_switching_the_setting_makes_the_store_stale_and_the_next_rebuild_re_embeds_every_chunk` |
| S8 | Routing by question type: a question that names a symbol puts the code route's first 2 hits ahead after the rerank; a question that names a record puts that record's 2 best chunks ahead; each half kept only if it holds at its measure (each half behind its own setting, both off by default) [DEC-1067 (a)] | `test_w2_32_s8_routing.py::test_with_both_halves_off_the_order_is_the_rerankers` (12 cases: no setting, both 0 or an empty block, four questions); `test_w2_32_s8_routing.py::test_off_by_setting_gives_the_same_bundle_as_no_setting`; `test_w2_32_s8_routing.py::test_route_by_symbol_puts_the_code_routes_first_two_hits_ahead_after_the_rerank` (S8's measured form: the code route's hits by stored-vector cosine to the question); `test_w2_32_s8_routing.py::test_route_by_symbol_without_stored_vectors_falls_back_to_the_routes_own_order`; `test_w2_32_s8_routing.py::test_route_by_symbol_leaves_a_question_naming_no_symbol_in_the_rerankers_order` (2 cases); `test_w2_32_s8_routing.py::test_route_by_record_puts_the_records_two_best_chunks_ahead_after_the_rerank`; `test_w2_32_s8_routing.py::test_route_by_record_leaves_a_question_naming_no_record_in_the_rerankers_order` (2 cases); `test_w2_32_s8_routing.py::test_both_halves_on_a_question_naming_a_symbol_and_a_record_puts_both_ahead`; `test_w2_32_s8_routing.py::test_the_16_text_cap_holds_with_routing_on`; `test_w2_32_s8_routing.py::test_an_invalid_setting_is_config_invalid_naming_the_key` (6 cases: a negative number, a word, a list, each key); the phrasings (DEC-1067 order (4), a note within S8): `test_w2_32_s8_phrasings.py::test_the_content_word_phrasing_brings_a_chunk_only_it_reaches` (on, off); `test_w2_32_s8_phrasings.py::test_the_id_appended_phrasing_reaches_a_chunk_naming_the_resolved_record` (on, off); `test_w2_32_s8_phrasings.py::test_the_merged_pool_is_reranked_once_within_16_texts_and_24000_characters` (2 cases); `test_w2_32_s8_phrasings.py::test_off_is_todays_bundle_byte_for_byte` (2 cases); `test_w2_32_s8_phrasings.py::test_an_invalid_phrasings_value_is_config_invalid_naming_the_key` (3 cases) |

## What the record judges instead of a test

- **S1's regression with a real second model.** The cases swap to a stand-in second embedder and ask the planted
  questions; no real model runs here. A swap to a real model, and the dev-tier regression (`retrieve_check`, the
  dev tiers) on it, is a measured run on the CTO's record, not a case of this suite.
- **S9 and F1** are about the rounds' measured figures, not W2-32's code. The CTO's measure records
  (`~/gov-os-runs/D4B/`, measure 1 under `m1/records`, read through `W2_32_RUNS`) and the ticket's evidence file
  (`docs/changes/W2-32-evidence.md`) are the record. `w2_32_record.py` states the two rules as code, and the
  reviewer runs it on the records:

      python3 tests/acceptance/W2-32/w2_32_record.py ~/gov-os-runs/D4B/m1/records <round record.json> ...

  It prints each figure's noise band over the baseline's runs, then per round F1's verdict (`revert` when a count is
  below the band's lowest) and S9's state. **The band is the spread of D-4b measure 1's three runs with the merged
  code (the CTO, P-W2-32-2; 0 when they agree)**: the records in `m1/records` itself, never its `pinned/` folder (the
  pinned run's record), which the non-recursive read leaves out. Only the records' totals and top-level fields are
  read, never a question's text.

## Round 2's rewrites

- **The map in the runner's form** (`Rewrite-Reason: the README map in the runner's form`): every item is
  `test_w2_32_<name>.py::<function>`, and no prose in the Tests column is backticked, so `gov accept` matches each.
- **S5's premise** (`Rewrite-Reason`, in the file): the routes give the fusion 42 distinct chunks of the 50 notes, so
  each limit is judged against `min(limit, all that match)`, measured in the same project; the bar is unchanged.
- **The stand-in reports the GPU** (`Rewrite-Reason: W2-32's S10`, DEC-1065): it used to report the CPU, which S10
  refuses; the S1 to S5 cases are about the pin, not the device.
- **S3's hidden miss** (`Rewrite-Reason: the CTO's ruling on S3`): two functions added; no round-1 case recorded a
  hidden-shaped miss.
- **Other tickets' cases that W2-32's S2 makes fail closed** are revised to pin their stand-in's digest in their
  planted project's `models.yaml` (each with its own `Rewrite-Reason`; the return lists them).

## Round 18 (the padded request bound; `Rewrite-Reason: the padded bound groups requests by length (ties in the pool's order)`)

The engineer's bound (`b7085897`) is the padded size: a request's texts times its longest at most 24,000 characters,
at most 16 texts, the fewest requests grouped longest first, each score put back at its candidate's place (the order
the unbatched one: scores descending, ties in the merged pool's order). The requests no longer come in pool order, so:

- **S8's stand-in reranker gives no ties** (`w2_32_driver.rank_score`: the `rankNN` plus half a hash fraction under
  1, so the ranks still decide), and "the reranker's order" is the order of those scores alone, whatever the order
  of the requests. The guards are unchanged.
- **The size bound** (`test_w2_32_s7_size_bound.py`, and the phrasings' "reranked once"): every request within 16
  texts and 24,000 characters in total and padded; the fewest requests grouped longest first.
- **On `w2/W2-32`'s head `5c6dd724`:** the whole folder 151 passed, 1 skipped (S5's order case), 1 xfailed (R2-F1).

## Round 17 (the phrasings: DEC-1067 order (4), measure 3; a note within S8)

`test_w2_32_s8_phrasings.py` (11 cases): with `routing.phrasings: true` in `governance/project/retrieval.yaml`, each
question is searched in three phrasings (the question; its content words without stopwords or the question mark; the
question with the record ids the record route resolves appended), fused, and reranked once.

- **The content-word phrasing:** `records/ledger-room.md` holds `tide ledger quorum kept` in a row once, in a long
  chunk out of the vectors; forty short notes hold those words more often, never in that row, so the lexical route's
  30 words-ranked chunks for the question as asked leave it out (a probe of the integrated lexical route: the
  question reaches it not, its content words as a phrase put it first). On: in the rerank pool; off: not.
- **The id-appended phrasing:** "What are the quayside lamp hours?" names `CAP-88` by its title; the record route
  resolves it; `records/board-minutes.md` names `CAP-88` and shares no word with the question (out of the vectors):
  the question with `CAP-88` appended reaches it (probed: the question alone does not). On: in the pool; off: not.
- **Reranked once** (on): each text once, requests within 16 texts and 24,000 characters, the fewest meeting both.
  **Off:** no setting and `phrasings: false` give the same bundle and the same rerank pool, byte for byte.
  **Invalid:** a word, a number, a list: `CONFIG_INVALID` naming `routing.phrasings`.
- `retrieve` at radius 4 gathers the whole fused list, so the pool is every fused chunk.
- **On `16e0287a`:** 6 red (both "on" rows, both "reranked once", both "off": today's loader refuses
  `routing.phrasings` as an unknown key), 5 green (both "off" rows' premises, and the three invalid values, refused
  today as an unknown key naming it).

## Round 15 (the review's S7-F4 and S8-F4)

- **S7-F4, the size bound** (DEC-1067 (f); the CTO's bound after the GPU trip of 2026-11-04 03:53):
  `test_w2_32_s7_size_bound.py`. Every reranker request carries at most 16 texts and at most 24,000 characters in all
  (every text counted whole, its path line too). Ten notes of one 6,000-character line each go in the fewest requests
  meeting both bounds in the order the pool is sent (cut only where the next text would break one), with the order
  the unbatched one; a single chunk of 40,000 characters is given to the reranker as its first part, at most 24,000
  and at least half of it. On `45f24f09`: 4 green. On integrate's code: 4 red (one request of 60,668 characters).
- **S8-F4, an empty block:** the off case gains a bare `routing:` (YAML null) beside `routing: {}`: off, today's order,
  never a refusal; an invalid present key stays `CONFIG_INVALID` naming it. On `45f24f09`: the 4 bare-block rows red
  ("key 'routing': must be a map"), the rest of S8 green (the cap case too).

## Round 14 (S8's measured form; `Rewrite-Reason: S8's measured form (cosine order of the code route)`)

- **The symbol half's "first 2 hits"** are the code route's hits ranked by their stored vectors' cosine to the
  question (the research's r01, the form the owner adopted; the code graph returns a set), the route's own order only
  where a hit has no vector. The case works the cosine order out from the stand-in's own vectors (the question's,
  from the text it was sent; each code chunk's, from the store): gamma and alpha go ahead, where the route's own
  order would put alpha and beta. A new case, `test_route_by_symbol_without_stored_vectors_falls_back_to_the_routes_own_order`,
  plants the code out of the vectors: alpha and beta go ahead.
- **The reranker's order** is now each chunk once, at its first place: the code may score a chunk again in a later
  request, and the cases counted it twice. The `routing` record may name what it moved by chunk id or by path.
- **On the engineer's branch `808f7c90`:** 27 passed, 1 failed. The record half and the "both" case pass once the
  order is read right. `test_the_16_text_cap_holds_with_routing_on` is red for its own reason: with the record half
  on the reranker gets requests of 16, 4 and 5, the last re-scoring the named record's 5 chunks the first request
  scored already, so the pool is not cut into full requests of 16 (each request is at most 16, so DEC-1067 (f)'s
  cap holds; the guard asks the merged set be reranked once, as R2-F3 asked of W1-19 and W1-21).
- **On `296a4639`:** 10 red (the three routing cases, the fallback, the six invalid settings), 18 green.

## Round 12 (S8: routing by question type; DEC-1067 (a))

`test_w2_32_s8_routing.py` (28 cases) and `w2_32_routing.py` (the planted project and the helpers).

- **The settings, as the engineer stated them** (round 13; `Rewrite-Reason: the engineer's stated setting names`,
  where round 12 had `route_by_symbol`/`route_by_record`, true or false): `governance/project/retrieval.yaml`, a
  `routing` block with `code_first` (how many of the code route's first hits go ahead) and `named_first` (how many
  of the named record's best chunks go ahead); absent or 0 is off, the measured form is 2 (`w2_32_routing.KEYS`,
  `ON`, `OFF`). The CTO's ruling: each half behind its own setting, both off by default, off gives today's order
  exactly, an invalid value (a negative number, a word, a list) is `CONFIG_INVALID` naming the key
  (`routing.code_first`). With either half on, the bundle carries a `routing` record naming what it moved.
- **The corpus:** three code files of one function each (one chunk each); a record `CAP-88` of three sections (one
  chunk each); 23 notes, so the rerank pool exceeds 16. Every ordered chunk holds a `rankNN`: the stand-in reranker's
  score (none: 0), so the routed chunks score below the notes and only routing puts them ahead.
- **The stand-ins:** the reranker scores by `rankNN` and keeps each request; **the code route is a stand-in** (the
  driver's `code_route` option replaces `gov.retrieval.code_route.route`): the real code-graph tool needs a local
  coordination endpoint the launch sandbox refuses ("secure CLI coordination could not be created"), and its index
  folder (`/tmp/gov-cbm-<uid>`) is read-only there. It answers a question naming `w32_alpha` with the three code
  files' chunks in a set order, any other question with no route; the fusion, the rerank and the routing are the
  code's own. The record route is the code's own (the record store and the closure).
- **What is judged:** "the reranker's order" is the order the same scores give the pool as the reranker received it
  (stable for ties); with a half on and a question it names, the evidence starts with exactly the routed chunks
  (the code route's first 2; the record's 2 best by score; both for a question naming both) and the rest keeps the
  reranker's order; off, or a question it does not name, the order is the reranker's; the requests stay those of
  DEC-1067 (f).
- **On `296a4639` (round 13):** 9 red (the three routing cases and the six invalid settings, taken today), 18
  green (off in three forms and the unnamed questions: today's order, guards; the cap).

## Round 11 (the round-2 review: R2-F1, R2-F3)

- **R2-F1:** `test_w2_32_s7_dec1067.py::test_nested_parents_send_no_line_twice_and_name_every_span_left_out`. A
  planted Python file (a module of 59 lines and five functions; each function and each run of module lines one
  chunk, so no two chunks overlap) asked with one item a batch through its continuations: no line is sent twice,
  across calls or within one; in each call every gathered chunk is sent or named as a span record outside the
  evidence and the expansions (`merge.candidates` = the evidence plus the named spans); a named span lies within
  lines already sent. Red on `b32e8504`: call 1 sends lines 18-26, then the module 1-59 that holds them, and calls
  2 and 3 send three more functions inside it, unnamed. With the twice check off (a scratch copy), the naming and
  the count pass there.
- **R2-F3 (W1-19's and W1-21's one-rerank cases):** every rerank request but the last carries exactly 16 texts,
  the last at most 16, so two passes of their own (one per route) no longer pass. Green on `b32e8504`.

## Round 10 (DEC-1067 order (5), index-time method 1: contextual headers when embedded)

`test_w2_32_s7_headers.py`, 14 cases from the ticket's note "DEC-1067 order (5), index-time method 1" (the CTO,
2026-11-04), mapped under S7 as round 9's were (the note has no KPI line of its own). The interface they assume:

- **The setting:** `embed_headers: true|false` in the project's `governance/project/rebuild.yaml`, read as it stands in
  the working tree; absent (no file or no key) is off. Only the YAML booleans `true` and `false` are values: `yes`,
  `1`, a quoted `"true"` or a word refuse `gov rebuild` with `CONFIG_INVALID` naming `embed_headers` (anywhere in the
  envelope), and no chunk is sent to the embedder. (PyYAML's `safe_load` reads `yes` as true: the check reads the
  scalar as written, as `read_yaml(..., plain=True)` does.)
- **On:** the text the embedder is sent for a chunk is a header followed by the chunk's own text (its file's lines, as
  the keyword index holds them). The header names the file's path (relative) and, in order, the headings the chunk
  lies under (title, section, subsection; its own first heading may be named too); no heading it does not lie under,
  no word of the file's body. A file with no headings (Markdown or text): its path alone. The same in two projects with
  the same files. A chunk above the embedder's limit is sent, header and all, within the length it is sent at with the
  setting off (at most 16,384 characters), and the rebuild still names it.
- **Unchanged with it on:** the keyword index of the embedded files (chunk and parent rows, the full-text rows), the
  evidence text `retrieve` returns (each item its file's lines) and the text the reranker is given for each chunk.
- **Off:** each chunk's own text exactly, as today.
- **Switched:** with the settings file outside the index (a namespace with `lexical_policy: not indexed`, so no indexed
  file changes) and left uncommitted, turning the setting on after a rebuild makes `semantic.search` (no refresh)
  answer unavailable with no hit, `semantic.manifest` changes, and the next rebuild re-embeds every chunk with its
  header; turning it off again does the same back.

Red on W2-32's reviewed head `612cd009` (a scratch tree, not merged): 11 of 14. The header cases: no header is sent;
the unchanged cases and the determinism case: their premise (the setting took effect) fails; the invalid values:
the rebuild succeeds (`ok: true`, the key ignored); the switch: the store is answered from after the switch. Green:
the three "off" cases (today's behaviour, kept as guards).

## Round 9 (S7's note under DEC-1067)

`test_w2_32_s7_dec1067.py`, four cases, all red on W2-32's head `2ea1a524`:

- **The cap (DEC-1067 (f)):** a rerank pool above 16 (the fusion's 30, `retrieve`'s 20 at radius 0) is sent to the
  reranker in requests of at most 16 texts, and the final order is the one the same scores give unbatched. The
  stand-in reranker keeps each request and scores each text by a hash of it (no ties). Red: one request of 30 (20);
  the order check alone passes there.
- **No span twice, the converse (the review's F-5):** with one item a batch and a bundle budget of 1,000 tokens, the
  first call sends two chunks of a 44-line section alone (no room for the section), and the second expands the
  section. No later item may hold a span an earlier call sent, and an expansion names what it left out (a span
  record outside the evidence and the expansions). Red: call 2 sends lines 1-46, holding 16-31 sent in call 1.
- **The embedder's limit, named:** a one-line chunk of over 40,000 characters is embedded from its first part, at
  most 16,384 characters (4,096 tokens at four characters each, above any limit of the shared embedder's context),
  and the rebuild's report names its path (and not every file). Red: 32,768 characters sent, the chunk not named.

## Round 7 (the review of W2-32, F-1)

A hidden miss whose id is lower case (`h07`, as the measure writes its hidden ids) with no `part` is hidden too: the
two hidden-miss functions gain a `lower-id` row each (7 cases), with planted text only. Red on the review's head
`85c16e9b` (an `h07` miss is taken for a visible one and, carried in full, recorded with its text) until the
engineer's F-1 fix.

## Round 4 (S7, G1; DEC-1066)

Six S7 cases, red on the engineer's head (`8a190197`) and on the integrated code (`9c468dbd`): the embedder and the
reranker are given the chunk cut short, the manifest records 512, a store at the old cut is answered from, and a
continuation sends the expanded section again. Two S2 cases (W2-L065) no longer ask for 512 but for a recorded cut
(`Rewrite-Reason: W2-32's S7`). The stand-in now keeps which text each vector it returned was made from, and the
driver gains a recording reranker and `retrieve`'s paging options.

## Round 3 (P-W2-32-5, strict)

The hidden-miss cases no longer pass a root cause or repair: an id-only miss is recorded with no text, and a root
cause or a repair alone is refused (4 cases added). On the engineer's `2bc918f1` (run in a scratch tree, not merged)
all 31 S3 cases pass; on `dcb30ab1` (before the ruling) the 14 hidden-miss cases are red.

## Round 2's state (the engineer's head `dcb30ab1`, merged)

66 green, 18 red (`gov accept W2-32 --json`: every map item matched; S1, S2, S4, S5 pass). S3's 17 round-1 cases
green; red: S3's 10 hidden-miss cases (the ruling is not built yet), S10's 7 (none built: the trap catches
`ollama serve`, so 4 of them also error at teardown; no named code; the CPU vector is used, cached and stored), and
the evidence file case (no S9 or F1 row until the rounds run). On the integrated code (`9c468dbd`), S10's 7 and all 27
of S3 are red.

## Round 1's state (the integrated code at `9c468dbd`)

46 red, 21 green. Each red case fails for the reason its line states:

- S1: 3 of 4 red (the configuration is not read; `MODEL` is fixed in `semantic.py`). Green: returning to the default
  pin (true today because nothing ever leaves it; kept as a guard).
- S2: 11 of 13 red (no pin check; mismatched revisions rebuild and answer; no cut in the manifest). Green: the
  default pin builds; `--no-embeddings` after a file change is already refused as stale (kept as guards).
- S3: 16 of 16 red (no `gov.retrieval.learning`).
- S4: 10 of 12 red (`rerank` and `fusion.search` raise). Green: `retrieve` with a process that dies, or with the
  default reranker, because it already catches `OSError`. With `EOFError` it raises.
- S5: 4 of 7 red (30 hits for any limit above 30). Green: limits up to 30.
- S9, F1: the baseline record and the rules are green; the evidence file case is red until the file is written.

## Not in this round

- S6 to S8, the gap rounds, once the owner approves the gaps.
- DEC-833 item 1 and DEC-866: the card has W2-32's test designer raise W1-19's, W1-21's and W2-54's pass lines of 80
  to 85 (`Rewrite-Reason: DEC-833`). Those files are outside `tests/acceptance/W2-32/**`, the only path this round
  may write; it is named in the return.
- A reranker swap by configuration (CAP-19.a's "components separable" for the reranker) is not asked by a KPI line
  and is not tested.
