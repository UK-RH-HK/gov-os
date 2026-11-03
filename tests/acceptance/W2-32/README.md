# W2-32 acceptance tests: retrieval components (S1–S5) and the rules on the record (S9, F1)

Ticket `DAEO-0pyc` (W2-32), profile STANDARD, round 1 (D-4b, DEC-1055). The independent test designer (MR-3) wrote
these cases from the ticket's KPI lines, its card (`docs/plan/WAVE_2_WBS.md`, W2-32), its list rows
(`docs/plan/WAVE_2_LIST.md`: W2-M073, W2-M191, W2-L065, W2-M103, W2-M104) and its sources (CAP-10.b, CAP-19.a,
CAP-19.c, DEC-954 Q9e, DEC-957). They were written before the implementation, without reading W2-32's new code; the
integrated code at `9c468dbd` was read for today's interfaces (DEC-963).

**Round 1:** S1 to S5, S9 and F1. **Round 2:** S3's hidden miss (the CTO's ruling), S10 (DEC-1065), S5's premise,
the map in the runner's form, and the stand-in reporting the GPU (below, "Round 2's rewrites"). S6 to S8 (at most
three of W2-15a's gaps, one round each) come in a later round, once the owner has approved the gaps. **88 cases from
42 test functions in seven files** (round 3: the hidden miss made strict, P-W2-32-5), with a support module, a driver, the S9/F1 rule module and a conftest. They run in
about 2 minutes (S10's cases wait for the health checks on code that still starts an embedder; once it does not,
they are quick).

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
- **W2-L065: the cut.** `semantic.manifest(root)` holds the embedding cut, `512`, as one of its values (the key is
  not judged). A store whose `semantic_*` tables are only the vectors and the four-column manifest (two models and
  their revisions), as every store built before W2-32 is, is stale.
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
| S3 | A retrieval miss is recorded as a memory-quality event with its root cause, its repair and a held-out regression case [CAP-19.c]; a hidden miss by its id only (the CTO's ruling) | `test_w2_32_s3_memory_quality.py::test_a_miss_is_recorded_as_a_memory_quality_event_with_its_root_cause_and_repair`; `test_w2_32_s3_memory_quality.py::test_an_event_without_one_of_its_parts_is_refused_and_nothing_is_written` (10 cases); `test_w2_32_s3_memory_quality.py::test_a_regression_case_not_in_the_measures_form_is_refused` (3 cases); `test_w2_32_s3_memory_quality.py::test_the_regression_case_is_a_question_in_the_measures_form_in_a_file_of_its_own`; `test_w2_32_s3_memory_quality.py::test_the_regression_case_is_held_out_of_what_memory_embeds`; `test_w2_32_s3_memory_quality.py::test_a_hidden_miss_is_refused_unless_it_carries_its_id_only` (12 cases, the ruling, strict); `test_w2_32_s3_memory_quality.py::test_a_hidden_miss_with_its_id_only_is_recorded_without_its_text` (2 cases, the ruling); `test_w2_32_s3_memory_quality.py::test_recorded_events_are_read_back` |
| S4 | A reranker that dies after loading is reported, not raised [W2-M104] | `test_w2_32_s4_reranker_dies.py::test_rerank_with_a_reranker_that_dies_after_loading_keeps_the_order_and_reports_it` (6 cases, each searched twice); `test_w2_32_s4_reranker_dies.py::test_the_default_reranker_that_dies_after_loading_is_reported_not_raised`; `test_w2_32_s4_reranker_dies.py::test_the_fusion_with_a_dying_reranker_answers_unreranked_and_reports_it` (2 cases); `test_w2_32_s4_reranker_dies.py::test_retrieve_with_a_dying_reranker_cites_its_evidence_and_reports_the_rerank_unavailable` (3 cases) |
| S5 | The fusion limit is honoured [W2-M103] | `test_w2_32_s5_fusion_limit.py::test_a_limit_above_thirty_is_honoured_or_refused` (31, 40, 50 against all that match); `test_w2_32_s5_fusion_limit.py::test_a_limit_up_to_thirty_returns_exactly_that_many` (1, 5, 30); `test_w2_32_s5_fusion_limit.py::test_a_honoured_limit_keeps_the_order_of_a_smaller_one` (skips if the build refuses) |
| S9 | Below 85 % after two improvement rounds: escalated to the owner, who decides at the third; at 85 % or above but under 95 % with room, not closed: escalated [DEC-954 Q9e, DEC-957] | `test_w2_32_record.py::test_the_baseline_record_holds_both_figures_against_their_bars`; `test_w2_32_record.py::test_s9_escalates_below_85_after_two_rounds_and_under_95_with_room` (6 cases, the rule); `test_w2_32_record.py::test_the_evidence_file_states_s9s_and_f1s_outcome` (the verdict is judged by the record, below) |
| F1 | An improvement that lowers any baseline figure of W2-15a beyond its noise band is reverted | `test_w2_32_record.py::test_the_baseline_was_run_more_than_once_on_one_commit_so_it_has_a_noise_band`; `test_w2_32_record.py::test_f1_reverts_a_round_below_the_baselines_noise_band` (5 cases, the rule); `test_w2_32_record.py::test_the_evidence_file_states_s9s_and_f1s_outcome` (the verdict is judged by the record, below) |
| S10 | No CPU fallback for embeddings: the GPU embedders unreachable, the semantic part named unavailable and a keyword answer; no private embedder started; a vector computed on the CPU refused, never cached or stored; a rebuild refuses to embed on the CPU [DEC-1065, DEC-1031, ACT-RERANK-WAIT-1] | `test_w2_32_s10_no_cpu_fallback.py::test_ensure_available_with_the_embedders_unreachable_checks_health_only`; `test_w2_32_s10_no_cpu_fallback.py::test_a_search_with_the_embedders_unreachable_reports_the_semantic_part_unavailable_with_a_named_code`; `test_w2_32_s10_no_cpu_fallback.py::test_retrieve_with_the_embedders_unreachable_answers_by_keywords`; `test_w2_32_s10_no_cpu_fallback.py::test_a_rebuild_with_the_embedder_unreachable_refuses_the_vectors_and_starts_nothing`; `test_w2_32_s10_no_cpu_fallback.py::test_a_question_vector_computed_on_the_cpu_is_refused_and_nothing_cached`; `test_w2_32_s10_no_cpu_fallback.py::test_retrieve_with_the_query_embedder_on_the_cpu_answers_by_keywords`; `test_w2_32_s10_no_cpu_fallback.py::test_a_rebuild_with_the_embedder_on_the_cpu_refuses_to_embed` |

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
