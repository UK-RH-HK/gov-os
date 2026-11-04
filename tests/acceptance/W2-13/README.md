# W2-13 acceptance tests: RETR-X-02 and a ranked lexical route (BM25, SQLite FTS5)

Ticket `DAEO-zqvn` (W2-13), profile FULL. Written by the independent test designer (MR-3) from the ticket's KPI lines,
its card (`docs/plan/WAVE_2_WBS.md`, W2-13), its list rows and its sources (DEC-725, DEC-900), in parallel with the
engineer and without reading the implementation (DEC-462, DEC-963). Other decisions used: DEC-260, DEC-342, DEC-343,
DEC-396, DEC-414, DEC-372, DEC-732, DEC-911, DEC-956 item 2; AR-9; CAP-11.

**99 cases from 50 test functions in nine files** (counted by collection), with three support modules
(`w2_13_support.py`, `w2_13_roles_support.py`, `w2_13_lexical_policy_support.py`) and a conftest. Seven of S1's and
S2's cases were rewritten after implementation to read the lexical route's ranking from `ranked` (DEC-1000,
P-W2-13-3 (b)): see "Rewrite after implementation". S5 (search respects role separation, DEC-1065 (2)) was added in
the DEC-1065 round by a fresh test designer, from the KPI line and the guard's matcher, without reading W2-13's
implementation of it: see "S5: search respects role separation". S6 (the keyword index honours the path map,
DEC-1066 (3)) was added in the DEC-1066 round, from the KPI line and the integrated code only: see "S6: the keyword
index honours the path map".

## How the tests reach the code under test

- The support module imports `gov` from whatever `PYTHONPATH` the run gives (DEC-732). Nothing is hard-coded.
- Every child process gets, first on its `PYTHONPATH`, the folder that this run's `gov` was imported from, then the
  run's own `PYTHONPATH`. Each driver process reports the `gov` it imported, and `Box.run` fails a case whose child
  ran another `gov`. The `gov` commands run as `python -m gov.cli.main` with the same `PYTHONPATH`.
- Run from the ticket worktree with `PYTHONPATH=<ticket worktree>/src` and they exercise its code:

      cd <worktree> && PYTHONPATH=<worktree>/src \
        python3 -m pytest tests/acceptance/W2-13 -q -p no:cacheprovider -o tmp_path_retention_policy=failed -rs

  `gov accept DAEO-zqvn` runs the folder with the root's `src/` on `PYTHONPATH` and reads the map below.

Only public interfaces are used:

- the commands `gov rebuild --json` and `gov retrieve "<question>" --json` (`--root`, `--id`, `--radius`,
  `--bundle-budget`), read through the API-0002 envelope;
- `gov.retrieval.lexical.search(root, query, refresh=...)`, `chunks(root, path=...)` and `parent(root, parent_id)`
  (W1-17's interface; the answer's `available`, `facet`, `state`, `reason`, `hits`, each hit's `path`, `line`, `text`,
  `chunk_id`, `parent_id`), and, beside `hits`, the answer's `ranked` list (DEC-1000): chunk records, best first,
  each with at least `chunk_id`, `path`, `start_line`, `end_line`, `parent_id`, `bm25` (absent or null for a chunk
  only the exact route found) and `exact`;
- `gov.retrieval.fusion.search(root, query, limit, refresh=..., reranker=...)` (W1-19's interface: `hits` with
  `routes`, `facets`, `reranked`);
- the store `.gov-runtime/store.db`, read as an SQLite file only: which tables are FTS5 tables, what the rows of its
  ordinary tables hold, and each FTS5 table's terms through `fts5vocab` on a copy (the project's store is never
  written).

**The ranking is read from the order of `ranked`** (DEC-1000): each file at the place of its first chunk. `hits` stays
W1-17's exact list (every line that holds the string, case and all, by path and line, not ranked); the exact-string
case, W2-M100's case and the secrets cases read it, and two rewritten cases check that it is still that list. No case
names a column, a weight or a private function of the index.

## The fixture and the environment

- **One fixture repository** (`build_fixture`), built from scratch in a temporary folder: a path map that classes
  every path as embedded governance memory, the kernel's `.gitleaks.toml`, and a corpus of small files, each built
  for one line of the KPIs (`w2_13_support.py` names them). The session's store (`built`) is a clone rebuilt by
  `gov rebuild --json`; every case that only reads shares it. A case that changes a project takes its own clone.
- **The scratch environment** of every child is built from nothing: an empty `HOME` (the default reranker is absent,
  DEC-374), a `PATH` holding only `git`, `gitleaks` and `python3` (the code tool is absent, so no code graph is
  built: the cases run the same in a sandbox, where the code graph's temp folder is read-only), the run's own
  rebuild lock (`GOV_REBUILD_LOCK`, DEC-956 item 2; the tests root conftest sets it), and a secrets cache of the
  session's own (`GOV_SECRETS_CACHE`): W2-107's cache stays on, in front of the filter, as `gov rebuild` uses it.
- **The semantic route** is W1-21's stand-in Ollama endpoint on a loopback port (`OLLAMA_HOST` and
  `GOV_QUERY_OLLAMA_HOST`): vectors made of words, so no model runs. Where a case needs the semantic route down, it
  points both at a dead port. **The reranker** is a stand-in loader in the child (it scores by a favoured word), or
  an absent one.
- **The planted secret** is a string of the kernel's canary rule, joined at run time from parts: no file of this
  suite holds it whole (DEC-911), and none is printed.
- **Markers.** `needs(...)` skips a case, with its reason, where this machine lacks `git`, `gitleaks`, `sqlite_vec`,
  the Ollama model or the reranker environment; nothing is installed. `local_only` marks the cases that clone the
  dev tiers (`GOV_DEV_TIERS`, default `~/gov-os-workbench/synthetic`, read by name and cloned into a temporary
  folder); each skips where a tier or the query set is absent. `latency` marks the timed cases.
- **Latency cases (DEC-372).** `test_w2_13_latency.py` holds the two timed cases: run that file alone, never beside
  another suite; a case that fails under parallel load is re-run alone. The real-model one shares the session's
  `real_tiers` (both dev tiers rebuilt once with the real embedder) with RETR-A-04's case.

## KPI lines and their tests

The test files are all `test_w2_13_<name>.py`.

| KPI | Line (short) | Tests |
|---|---|---|
| S1 | The ranked lexical route: an FTS5 table over today's parents and spans, built by `gov rebuild`; a plain-word question ranked by BM25 with field weights for id, title and body; an exact identifier still first, the exact-match route kept as a boost [DEC-725, W2-M102, W2-L233, W2-M292, W2-M072, W2-M100] | `test_w2_13_ranked_route.py::test_the_lexical_index_is_an_fts5_table_that_gov_rebuild_builds`, `test_w2_13_ranked_route.py::test_the_index_keeps_the_parents_and_spans_of_today`, `test_w2_13_ranked_route.py::test_a_plain_word_question_returns_ranked_lexical_chunks`, `test_w2_13_ranked_route.py::test_ranked_chunks_are_best_first_by_how_well_they_match_the_words`, `test_w2_13_ranked_route.py::test_a_word_in_the_id_or_the_title_ranks_above_the_same_word_in_the_body`, `test_w2_13_ranked_route.py::test_an_exact_identifier_ranks_first`, `test_w2_13_ranked_route.py::test_every_line_that_holds_an_exact_string_is_found_with_its_file_and_line`, `test_w2_13_ranked_route.py::test_letter_case_does_not_change_what_a_plain_word_question_finds`, `test_w2_13_ranked_route.py::test_a_word_matches_whole_tokens_only` |
| S2 | The fusion receives a ranked lexical list beside the semantic one; lexical, semantic and the reranker each contribute [DEC-725] | `test_w2_13_fusion.py::test_lexical_semantic_and_the_reranker_each_contribute`, `test_w2_13_fusion.py::test_the_lexical_route_hands_the_fusion_its_ranking_best_first`, `test_w2_13_fusion.py::test_gov_retrieve_cites_what_the_lexical_route_ranks_for_a_plain_word_question` |
| S3 | Lexical search returns "unavailable" instead of raising [W2-M071]; retrieval latency within the retrieve budget on the dev tiers | `test_w2_13_unavailable.py::test_a_search_of_an_unusable_index_answers_unavailable_and_never_raises`, `test_w2_13_unavailable.py::test_a_default_search_that_may_refresh_never_raises_on_an_unreadable_store`, `test_w2_13_unavailable.py::test_gov_retrieve_on_an_unusable_index_answers_without_a_traceback`, `test_w2_13_unavailable.py::test_no_question_makes_a_search_raise`, `test_w2_13_unavailable.py::test_gov_retrieve_answers_any_question_without_a_traceback`, `test_w2_13_latency.py::test_the_ranked_lexical_route_answers_a_warm_question_within_the_budget`, `test_w2_13_latency.py::test_a_warm_retrieval_with_the_real_models_answers_within_the_budget` |
| S4 | A question about an id that exists nowhere stops with a named reason and no unrelated items: the stated gap (RETR-X-02) [AR-9, W2-M296, DEC-900] | `test_w2_13_stated_gap.py::test_premise_no_file_of_the_fixture_holds_the_missing_id`, `test_w2_13_stated_gap.py::test_an_id_that_exists_nowhere_asked_alone_is_a_stated_gap`, `test_w2_13_stated_gap.py::test_an_id_that_exists_nowhere_given_with_its_id_is_a_stated_gap`, `test_w2_13_stated_gap.py::test_a_question_naming_an_id_that_exists_is_answered_with_no_gap_for_it`, `test_w2_13_stated_gap.py::test_retr_x_02_on_a_dev_tier_asked_with_no_id_is_a_stated_gap` |
| S5 | Search respects role separation: `gov retrieve`'s results (every route) and `gov context`'s supplementary block filtered by the caller's role_paths (GOV_ROLE or --role, and GOV_TICKET; the guard's path checks); an engineer never its own ticket's acceptance tests, a test designer never the ticket's new code; what is filtered named (how many, by which rule); no role_paths section, no filter [DEC-1065, DEC-1056, DEC-1063] | `test_w2_13_role_separation.py::test_engineer_retrieve_returns_none_of_its_own_tickets_acceptance_tests`, `test_w2_13_role_separation.py::test_engineer_context_supplementary_holds_none_of_its_own_tickets_acceptance_tests`, `test_w2_13_role_separation.py::test_engineer_retrieve_holds_back_its_tickets_cases_revised_in_another_folder`, `test_w2_13_role_separation.py::test_coordination_ticket_holds_back_its_own_folder_only`, `test_w2_13_role_separation.py::test_designer_retrieve_returns_none_of_the_tickets_new_code`, `test_w2_13_role_separation.py::test_designer_retrieve_keeps_the_shared_test_files`, `test_w2_13_role_separation.py::test_no_role_paths_section_means_no_filter` |
| S6 | The keyword index honours the path map: a namespace whose `lexical_policy` is `not indexed` keeps its files out of the keyword index (absent: indexed, as today); the validator accepts the field with its two values; a file kept out is named in the rebuild's report; the evaluation set's own documents (lens B's report, `fixtures/evaluation/**`) are what D-7 marks so [DEC-1066, DEC-1052 M-4] | `test_w2_13_lexical_policy.py::test_a_namespace_not_indexed_keeps_its_files_out_of_the_keyword_index`, `test_w2_13_lexical_policy.py::test_no_term_of_the_keyword_index_spells_a_word_of_a_file_kept_out`, `test_w2_13_lexical_policy.py::test_gov_retrieve_cites_nothing_of_a_file_kept_out`, `test_w2_13_lexical_policy.py::test_the_rebuild_names_each_file_it_kept_out`, `test_w2_13_lexical_policy.py::test_a_namespace_with_no_lexical_policy_or_indexed_is_indexed_as_today`, `test_w2_13_lexical_policy.py::test_with_no_lexical_policy_anywhere_every_file_is_indexed_and_none_named`, `test_w2_13_lexical_policy.py::test_the_path_map_validator_accepts_both_values`, `test_w2_13_lexical_policy.py::test_the_path_map_validator_refuses_an_invalid_value`, `test_w2_13_lexical_policy.py::test_the_vectors_keep_their_embedding_policy`, `test_w2_13_lexical_policy.py::test_a_namespace_not_indexed_and_embedded_is_refused_naming_it`, `test_w2_13_lexical_policy.py::test_a_store_built_before_the_policy_is_put_right_by_the_next_refresh`, `test_w2_13_lexical_policy.py::test_the_repository_marks_the_evaluation_sets_own_documents_not_indexed` |
| F1 | RETR-A-04's bundle is unchanged (citations, three parent expansions, stopping reason) | `test_w2_13_bundle_unchanged.py::test_the_bundle_keeps_its_form`, `test_w2_13_bundle_unchanged.py::test_a_child_hit_is_still_cited_as_its_parent_and_named_as_an_expansion`, `test_w2_13_bundle_unchanged.py::test_retr_a_04_cites_both_files_with_three_named_expansions_and_its_stopping_reason` |
| F2 | The secrets filter applies to the FTS5 table as to the old index: a planted canary is never indexed | `test_w2_13_secrets.py::test_no_row_or_term_of_the_store_holds_the_canary`, `test_w2_13_secrets.py::test_no_lexical_search_for_the_canary_or_its_words_finds_its_file`, `test_w2_13_secrets.py::test_gov_retrieve_cites_nothing_from_the_file_that_holds_the_canary`, `test_w2_13_secrets.py::test_a_second_rebuild_answered_from_the_secrets_cache_indexes_the_canary_no_more` |

### The list rows and their tests

| Row | What the tests hold | Cases |
|---|---|---|
| W2-L233 | An exact identifier ranks first | `ranked_route::test_an_exact_identifier_ranks_first` (both forms) |
| W2-M102 | A ranked lexical route contributes hits to the fusion (on identifier and plain-word questions) | `fusion` (all three); `ranked_route::test_an_exact_identifier_ranks_first` |
| W2-M292 | A plain-word question returns lexical hits; its words are matched, not the phrase | `ranked_route::test_a_plain_word_question_returns_ranked_lexical_chunks`, `::test_ranked_chunks_are_best_first_by_how_well_they_match_the_words`; `fusion::test_gov_retrieve_cites_what_the_lexical_route_ranks_for_a_plain_word_question` |
| W2-M072 | Cases for letter case and for ranking (the decision on mid-token matches and stems is the engineer's to record; no case fixes it beyond W2-M100's whole tokens) | `ranked_route::test_letter_case_does_not_change_what_a_plain_word_question_finds`; the ranking cases of `ranked_route` |
| W2-M100 | Search never raises; whole-token matching; a case for each | `unavailable::test_no_question_makes_a_search_raise`, `::test_a_search_of_an_unusable_index_answers_unavailable_and_never_raises`; `ranked_route::test_a_word_matches_whole_tokens_only` |
| W2-M071 | The DEC-260 unavailable mapping instead of raising | `unavailable` (all five functions) |
| W2-M296 | The question alone about an id that exists nowhere: the stated gap, no unrelated items | `stated_gap` (all five functions) |
| W2-M098 | The stopping reason for a non-record id is the same on every machine | **Not held exactly: package P-W2-13-TD-1.** The cases accept `UNRESOLVED_IDS` or `FACET_UNAVAILABLE` (as W1-21 does), and `FACET_UNAVAILABLE` only where a facet the bundle reports says it could not answer (`check_bundle`) |

## How each line is read

- **S1, the parents and spans of today.** `SPANS_TODAY` is what the base (`w2/integrate` at `c38a5b49bc86`) gives
  through `chunks` and `parent` for a document of three sections and a Python file of two functions: three section
  chunks, two function chunks and two module chunks (DEC-343). The case asserts the same list after the change.
- **S1, BM25.** Three files of the same length hold three, two and one of the question's words; their paths sort the
  other way round. A document that holds some of the words is a hit (BM25 ranks partial matches); the one that holds
  more ranks higher.
- **S1, the fields (the lead's reading).** *id* is the identifier a document is known by (a record's frontmatter
  `id`); *title* is the heading of the document or of the section the chunk lies in; *body* is the text. Each pair
  of files holds **the same words the same number of times**, the question's word in the id (or the heading) of one
  and in the body of the other: a ranking without field weights ties them exactly. Both files hold the word in the
  same letter case, so an exact-string boost lifts both alike. Each pair has a mirror whose paths sort the other
  way, so a tie broken by path, row or insertion order passes at most one of the two.
- **S1, the exact identifier.** `QX-4471` stands verbatim in one file; two other files hold `QX`, `4471` and the
  question's other words far more often. Asked alone and with words, the holder is first in `ranked`, no chunk
  marked `exact` is ranked below one that is not (the exact route's chunks come first), the holder's chunk is marked
  `exact` when the identifier is asked alone, and `hits` is W1-17's exact list (the holder's line asked alone, none
  with words: no line holds "QX-4471 gauge reading"). Every line that
  holds the exact string `KV-208` is a hit of its own, with its file, line and text (CAP-11, W1-17); the case looks
  only at the hits whose text holds the string, so plain-word hits beside them do not disturb it.
- **S2.** The question is S1's plain-word question. With both routes and a reranker, the fused hits hold lexical and
  semantic ones and are reranked. With the semantic route down and no reranker, the fused order is the order of the
  lexical route's `ranked` list (DEC-1000), best first.
- **S3.** The stores: missing; an empty file; bytes that are not a database; a database without the lexical table;
  the form before this change (the base's W1-17 tables, its DDL copied as the frozen "before" form, one file's rows);
  stale (a commit after the rebuild). A read-only search answers each as unavailable, with `FACET_UNAVAILABLE` and a
  reason. A default search (which may rebuild) and `gov retrieve` never raise or print a traceback; a governance
  error with its code is accepted. The questions: thirteen with no token, thirty-six that FTS5 would read as syntax.
  The empty question is not given to `gov retrieve` (it may be a usage error, exit 2).
- **S3, latency.** W1-19's warm-query budget, p95 at most 0.5 s, over the dev query set's questions on both tiers,
  after three warm-up questions, in one process: once through the lexical route alone (no model), once through the
  fusion with the real models.
- **S4.** `DEC-9999` is in no file and no record. The semantic route is up (the stand-in), so a gap is never
  explained by a route that is down. Asked as `DEC-9999` alone and as "What does DEC-9999 decide?" with no `--id`,
  and with `--id`: the id is a gap; the reason is `UNRESOLVED_IDS` or `FACET_UNAVAILABLE`, never `CLOSURE_COMPLETE`,
  `SATURATED` or `BUDGET_EXHAUSTED_WITH_GAPS`; no continuation; **no evidence at all** (nothing is about the id, so
  any item is unrelated; the fixture holds a line with the question's other words on purpose, as the dev tiers do).
  A question naming `DEC-0042`, which exists, cites its record and names no gap for it.
- **F1.** On the fixture: the bundle keeps W1-21's keys, an evidence item's and an expansion's keys, the fixed list of
  reasons, and every citation checks against the bytes; a child hit in a long section is still cited as its parent
  and named as an expansion. On a-dev with the real models: RETR-A-04 as the exit run asked it (`--radius 1`) cites
  both implementation files, names at least the three recorded parent expansions, and stops with
  `BUDGET_EXHAUSTED_WITH_GAPS`, its gaps named and a continuation, as recorded (EXIT-REPORT, "Retrieval"). The exact
  count of expansions depends on the cited chunks, so three is held as a floor, not as an equality.
- **F2.** After `gov rebuild`: no row of any ordinary table of the store (FTS5 tables read through their shadow
  tables) and no byte of its files holds the canary or the leaky file's own word; no term of any FTS5 table holds the
  canary's own word (`fts5vocab`, on a copy); no lexical search for the canary, its words or the file's words returns
  a line of that file; `gov retrieve` cites nothing from it. The terms', the searches' and `gov retrieve`'s checks
  each have a positive control on the clean file beside it (the rows' has none: an index may keep its text outside
  the store's rows). The vocabulary check works for word, stem and trigram terms. A second and third rebuild,
  answered from the secrets cache, change nothing.

## Expected red on the base

Run by the designer on the base (`w2/integrate` at `c38a5b49bc86`, this branch's parent), in a sandboxed session,
with `PYTHONPATH=<tests worktree>/src`, the two real-model cases deselected (see "What was not run"):

    54 run: 17 failed, 37 passed, 2 deselected (88 s)

That run was of the first batch. After DEC-1000's rewrite the expected count on the base is **54 run: 20 failed, 34
passed, 2 deselected**: the three rewritten cases that passed on the base by path order or through the exact route
(the two mirror field cases and `[the identifier alone]`) now read `ranked`, which the base does not have. Not re-run
by the designer (no checkout of the base in the rewrite batch); the lead runs the red check. The seven rewritten
functions (eleven cases) are marked † below.

| Case | Red reason on the base |
|---|---|
| † `ranked_route::test_a_plain_word_question_returns_ranked_lexical_chunks` | "search's answer for 'pilot tide harbour' has no `ranked` list (DEC-1000)"; behind it, the base matches the question as one phrase and finds no line (W2-M292) |
| † `ranked_route::test_ranked_chunks_are_best_first_by_how_well_they_match_the_words` | no `ranked` list (DEC-1000); behind it, the three files are not found (no phrase match) |
| † `ranked_route::test_a_word_in_the_id_or_the_title_ranks_above_the_same_word_in_the_body[title, the body first by path]` | no `ranked` list (DEC-1000); behind it, the base orders by path, so the body file comes first |
| † `ranked_route::test_a_word_in_the_id_or_the_title_ranks_above_the_same_word_in_the_body[id, the body first by path]` | the same, for the id |
| † `ranked_route::test_a_word_in_the_id_or_the_title_ranks_above_the_same_word_in_the_body[title, the title first by path]`, `[id, the id first by path]` | no `ranked` list (DEC-1000) (they passed on the base by path order before the rewrite) |
| † `ranked_route::test_an_exact_identifier_ranks_first[the identifier and words]` | no `ranked` list (DEC-1000); behind it, "QX-4471 gauge reading" stands on no line |
| † `ranked_route::test_an_exact_identifier_ranks_first[the identifier alone]` | no `ranked` list (DEC-1000) (it passed on the base through the exact route before the rewrite) |
| † `ranked_route::test_letter_case_does_not_change_what_a_plain_word_question_finds` | no `ranked` list (DEC-1000) for 'pilot tide harbour'; behind it, nothing is found for either case |
| `fusion::test_lexical_semantic_and_the_reranker_each_contribute` | no fused hit came from the lexical route (only semantic ones) |
| † `fusion::test_the_lexical_route_hands_the_fusion_its_ranking_best_first` | no `ranked` list (DEC-1000) in the lexical answer; behind it, the fusion holds no hit without the semantic route |
| `fusion::test_gov_retrieve_cites_what_the_lexical_route_ranks_for_a_plain_word_question` | `rank/z-best.md` is not cited by the lexical route |
| `stated_gap::test_an_id_that_exists_nowhere_asked_alone_is_a_stated_gap[the id alone]`, `[a question naming the id]` | "DEC-9999 is not named among the gaps": the base stops with `BUDGET_EXHAUSTED_WITH_GAPS`, 20 unrelated items and `NOT_GATHERED` gaps (W2-M296) |
| `stated_gap::test_an_id_that_exists_nowhere_given_with_its_id_is_a_stated_gap` | "the bundle does not stop: it carries a continuation" (and it cites unrelated items); the id is a gap with `FACET_UNAVAILABLE` |
| `stated_gap::test_retr_x_02_on_a_dev_tier_asked_with_no_id_is_a_stated_gap[A]`, `[B]` | "DEC-9999 is not named among the gaps" on a-dev and b-dev (`local_only`) |
| `unavailable::test_a_search_of_an_unusable_index_answers_unavailable_and_never_raises[not a database]` | "lexical search raised DatabaseError" (W2-M071) |
| `unavailable::test_a_default_search_that_may_refresh_never_raises_on_an_unreadable_store[not a database]` | the same, with `refresh=True` |
| `unavailable::test_gov_retrieve_on_an_unusable_index_answers_without_a_traceback[not a database]` | a traceback: `sqlite3.DatabaseError` from the record queries under `gov retrieve` |

**Passing on the base, as guards against regression (34 after the rewrite; 37 before it):** the FTS5 table and the
spans of today; `test_every_line_that_holds_an_exact_string_is_found_with_its_file_and_line` (the exact-match route);
`test_a_word_matches_whole_tokens_only`; S3's other store states (missing, an empty file, a database without the
lexical table, the form before this change, stale: the base answers each as unavailable or rebuilds) and every
question case (the base quotes the question as a phrase); the lexical latency case on the dev tiers; S4's premise
and the existing-id cases; F1's two fixture cases; F2's four cases (the filter holds today).

## S5: search respects role separation (DEC-1065 (2))

Written in the DEC-1065 round (D-4b, launched by the CTO, no lead) from the S5 line, DEC-1065, DEC-1056, DEC-1063
and the guard's matcher `.claude/hooks/role_reads.py` (DEC-1052 G-14), which the KPI names as the checks to share.
**12 cases from 7 functions** in `test_w2_13_role_separation.py`; the projects, the calls and the checks are in
`w2_13_roles_support.py` (its docstring states the guard's checks as the cases take them).

**The projects.** Each is planted from nothing and indexed by `gov rebuild --no-embeddings`: the record store and the
lexical index, no embedder asked. The child's environment is the W2-13 scratch one (an empty `HOME` but for what a
case plants there, a `PATH` of git, gitleaks and python3, both Ollama hosts at a dead port, no reranker), so no model
starts: the semantic route reports itself unavailable (DEC-1065 (1)) and the keyword route answers. Every planted
file holds the words of the questions, `barnacle lighthouse gauge`, and the exact id `QZ-7731`, and its own marker
word that no other file holds. The path map's `role_paths` block is this project's own (`engineer: ["{ticket_tests}"]`,
`independent-test-designer: ["{ticket_impl}"]`).

- **A** (a plain repository, outside any engineer's tree): `.tickets/` with `DAEO-s5own` (W9-01, implementation),
  `DAEO-s5other` (W9-02) and `DAEO-s5coord` (W9-00, `class: coordination`), the record `DEC-0101` they cite; the
  acceptance tests of W9-01 (two files), W9-02 and W9-00; one file in W9-02's folder revised for W9-01 and one for
  W9-00, each by a commit with `Task:` the ticket and `Role: independent-test-designer` (the guard's linked tests);
  integrated code and a unit test (`src/harbour/`, `src/quay/`, `tests/unit/harbour/`).
- **B** (the engineer's tree as the guard places it: `~/gov-os-worktrees/W9-01`, `~` the case's own planted
  `HOME`): `w2/integrate` holds the integrated code, the ticket's paths included; the branch `w2/W9-01`, checked out,
  adds the ticket's new work under its `allowed_paths` (`src/harbour/calibrate.py`, its unit test, its evidence
  document), a new shared test file (`harbour_support.py`) and a new file outside the ticket's paths.
- **C**: A with no `role_paths` section.

**How the line is read.** The caller's role comes as `GOV_ROLE` or as `--role` (both forms, parametrized `env` and
`flag`); the ticket as `GOV_TICKET`, its file's name. "Returns none" is: no evidence item, expansion or `NOT_GATHERED`
gap of `gov retrieve` (no supplementary item, further-batch item or batch item of `gov context`) from a held-back
path, and the held-back files' marker words nowhere in the result. A held-back path may be named in the filter's
record: naming it returns nothing. "Named (how many, by which rule)" is held by `filter_records`: somewhere in the
result, outside the cited items and the fields that carry the project's own words, a mapping that names the rule
(`role_paths`, `reads_denied`, the entry such as `{ticket_tests}`, or the glob it expands to, such as
`tests/acceptance/W9-01`) beside a positive count, or a mapping from such a rule to a positive count, or a non-empty
list of entries that each name it. The field names and the form are the engineer's. "Still come back" is: another
ticket's tests, the integrated code and unit tests (and, for the designer, the integrated code under the same paths,
the shared test file and the branch's work outside the ticket's paths) are cited. Each case first makes the same call
with no role and checks that the files to be held back do come back then (a premise), so a red is never a project
that does not hold them.

| Case | What it holds |
|---|---|
| `test_engineer_retrieve_returns_none_of_its_own_tickets_acceptance_tests[env\|flag-plain words\|an exact identifier]` | project A, the engineer of W9-01: none of `tests/acceptance/W9-01/**` through the ranked words or the exact route; named; W9-02's tests and the integrated code still cited |
| `test_engineer_context_supplementary_holds_none_of_its_own_tickets_acceptance_tests[env\|flag]` | the same for `gov context DAEO-s5own`'s supplementary block |
| `test_engineer_retrieve_holds_back_its_tickets_cases_revised_in_another_folder` | `{ticket_tests}`'s linked tests: the file revised for W9-01 in W9-02's folder is held back; W9-02's own file is not |
| `test_coordination_ticket_holds_back_its_own_folder_only` | for the coordination ticket, its own folder only: W9-00's tests held back, the file revised for it in W9-02's folder cited |
| `test_designer_retrieve_returns_none_of_the_tickets_new_code[env\|flag]` | project B, the test designer of W9-01: none of the branch's new files under the ticket's paths (code, unit test, document); named; the integrated code under the same paths and the branch's file outside them still cited |
| `test_designer_retrieve_keeps_the_shared_test_files` | the guard's (c3): the new `*support*.py` under the ticket's paths stays readable |
| `test_no_role_paths_section_means_no_filter` | projects A and C, the same engineer's call: held back with the section; cited, and no filter named, without it |

**Expected red on today's integrated code** (`w2/integrate` at `eb28c40866af`, merged into this branch as
`295a20f7ec7f`; run by the designer in the launch sandbox, `PYTHONPATH=<tests worktree>/src`, through the heavy slot):

    12 run: 12 failed (15 s)

Every case is red on its first role assertion, after its premise held: no product code reads `role_paths` today and
`--role` is parsed and never used. The engineer's cases: "the engineer of W9-01 got its own acceptance tests:
['tests/acceptance/W9-01/README.md', 'tests/acceptance/W9-01/test_w9_01_gauge.py']" (`gov context`: "the engineer's
supplementary block holds its own acceptance tests: [the same two]"); the linked case: "got a case revised for its
ticket in another folder: ['tests/acceptance/W9-02/test_w9_02_revised_for_w9_01.py']"; the coordination case: "got its
own folder's tests: ['tests/acceptance/W9-00/test_w9_00_gauge.py']"; the designer's cases: "the test designer got the
ticket's new work: ['docs/changes/W9-01-evidence.md', 'src/harbour/calibrate.py',
'tests/unit/harbour/test_calibrate.py']" and "the designer's filter is not in force"; the no-section case: "with the
section, the engineer's own tests came back". Their other assertions (still cited, nothing named without the section)
pass today and guard against a filter that holds back too much. The checks were tried on today's results and on the
same results with the held-back items removed and a filter record added: `filter_records` finds nothing in today's
results (a first draft counted the context packet's `ticket_text`, which names the ticket's acceptance folder; content
fields are now passed over) and finds the record in the filtered ones, and every other assertion then passes.

**Not covered here:** the test designer's own tests tree (`~/gov-os-worktrees/<WBS>-tests`, where the guard names the
files the engineer's commits carried in) and the linked tests found on `w2/<WBS>-tests`'s first-parent line; the
closure and code routes by name (the filter sits at the chunk list, which every route's hits pass through; project
A has no code index, and its acceptance files are no records).

**P-W2-13-TD-5 (allowed paths for S5).** `gov context`'s supplementary block is built in
`src/gov/retrieval/supplementary.py` and called from `src/gov/context/__init__.py`; neither is in the ticket's
`allowed_paths`, which name `src/gov/context/supplementary.py` (no such file today). Options: (a) add
`src/gov/retrieval/supplementary.py` (where the block's chunks are listed) to the paths; (b) the engineer creates
`src/gov/context/supplementary.py` and `src/gov/context/__init__.py` calls it, which needs `__init__.py` in the paths
too; (c) leave `gov context` to another ticket and re-scope the two `gov context` cases. Recommendation (a);
confidence medium-high. No case depends on which file changes.

## S6: the keyword index honours the path map (DEC-1066 (3), G4)

Written in the DEC-1066 round (launched by the CTO, no lead) from the S6 line, DEC-1066 (3) and DEC-1052 M-4, and the
integrated code's interfaces only (DEC-963: the path map's validator `gov.config.loader.load_config`, which every
command runs first, and `gov.check.pathmap.check`); nothing of W2-13's S6 work was read. **31 cases from 12 functions**
in `test_w2_13_lexical_policy.py`; the projects, the calls and the checks are in `w2_13_lexical_policy_support.py`.

**The projects.** Planted from nothing and indexed by `gov rebuild --no-embeddings` (the record store and the keyword
index, no embedder asked), in the W2-13 scratch environment (an empty `HOME`, a `PATH` of git, gitleaks and python3,
both Ollama hosts at a dead port, no reranker). Four disjoint namespaces, every tracked path in exactly one:

| Namespace | `lexical_policy` | `embedding_policy` | Files |
|---|---|---|---|
| `evaluation` (`evaluation/**`) | `not indexed` | `not embedded` | `evaluation/lens-report.md`, `evaluation/cases/q01.yaml` (D-7's shape: out of both indexes) |
| `kept-out` (`kept-out/**`) | `not indexed` | `not embedded` | `kept-out/notes.md` (a second namespace kept out; its `embedded` form is planted only in the refusal's scratch copy) |
| `indexed` (`indexed/**`) | `indexed` | `not embedded` | `indexed/log.md` |
| `governance` (`*`, `docs/**`, `governance/**`) | absent | `embedded` | `docs/plain.md`, the README, the path map |

Each planted file holds two made-up words (so no word, stem or trigram of another text spells them) and an id held by
no other file. The **control** project is the same files with no `lexical_policy` anywhere. Every "kept out" case
first asks the control the same question and checks the file comes back (the premise), so a red is never a question
that could not find it.

**How the line is read.**

- "Kept out of the keyword index": `lexical.search(root, q, refresh=False)` returns the file neither in `hits` nor in
  `ranked`, asked by its words and by its id; no FTS5 term spells its words (word, stem or every trigram, through
  `fts5vocab` on a copy; the indexed files' words are spelt, as a positive control); and `gov retrieve` (the keyword
  route, the semantic endpoint dead) returns it as no evidence, expansion or gap. The record store and the vectors'
  rows are not read: "out of the keyword index" is held on the index and the search, not on every table of the store.
- "Named in the rebuild's report": each kept-out file's path stands in `gov rebuild --json`'s result (or in the record
  file the result names), and no indexed file's path does (a report that lists every file does not name what was kept
  out). The field names and the form are the engineer's.
- "Absent: indexed, as today": the absent namespace's and the `indexed` namespace's files are found by words and id;
  on the control every file is found and the report names none.
- "The validator accepts the field with its two values": `load_config` keeps `indexed` and `not indexed` as given,
  `gov.check.pathmap.check` finds nothing, `gov rebuild` succeeds. "Refused": `skip`, `not-indexed`, `Not Indexed`,
  `not embedded`, the empty string, `true` and a list are each refused by `load_config` with `CONFIG_INVALID` naming
  `lexical_policy`, and `gov rebuild --json` fails with that code and builds no store. The values are the two the KPI
  line names, exactly as written (as `embedding_policy`'s are).
- "The vectors' `embedding_policy` is unaffected" (the brief's case): the planted project rebuilt with its vectors
  through W1-21's stand-in endpoint (vectors made of words, no model runs, DEC-1064); `fusion.search` with no
  reranker returns `indexed/log.md` by the keyword route only and `evaluation/lens-report.md` by neither. This is the
  one S6 case that builds vectors (`needs("sqlite_vec")`).
- **`not indexed` with `embedded` is refused** (the CTO, P2, revising the row "not indexed, embedded: in the vectors
  only"): the vectors are built from the keyword index's chunks, so a file the keyword index keeps out has no vectors.
  A scratch copy of the planted project whose `kept-out` namespace says `not indexed` and `embedded` is refused by
  `load_config` with `CONFIG_INVALID` naming the namespace, and `gov rebuild --json` fails with that code, names it,
  and builds no store (`test_a_namespace_not_indexed_and_embedded_is_refused_naming_it`).
- "What D-7 marks so": this repository's own path map (the run's root): lens B's report and every tracked file under
  `fixtures/evaluation/` lie in exactly one namespace, which says `lexical_policy: not indexed`. Only file names are
  listed (`git ls-files`); no evaluation file is read.

**Expected red on today's integrated code** (`w2/integrate` merged into this branch as `fd22f3d0`; run by the designer
in the launch sandbox, `PYTHONPATH=<tests worktree>/src`, through the heavy slot):

    30 run: 22 failed, 8 passed (11 s)

| Case | Red reason today |
|---|---|
| `test_a_namespace_not_indexed_keeps_its_files_out_of_the_keyword_index` (6: three files × words, id) | "… lies in namespace 'evaluation' (lexical_policy: not indexed) and the keyword route found it for 'zorquix vexlumbra'" |
| `test_no_term_of_the_keyword_index_spells_a_word_of_a_file_kept_out` | the index holds all six words of the three kept-out files |
| `test_gov_retrieve_cites_nothing_of_a_file_kept_out` (3) | "gov retrieve returned evaluation/lens-report.md (lexical_policy: not indexed)" |
| `test_the_rebuild_names_each_file_it_kept_out` | the report names none of the three files |
| `test_the_path_map_validator_refuses_an_invalid_value` (7) | "the path map's validator accepted lexical_policy: 'skip'" (the field is not read today) |
| `test_the_vectors_keep_their_embedding_policy[not indexed, not embedded…]` | the file came back by the keyword route |
| `test_a_namespace_not_indexed_and_embedded_is_refused_naming_it` | "the path map's validator accepted namespace 'kept-out' with lexical_policy: not indexed and embedding_policy: embedded" |
| `test_the_repository_marks_the_evaluation_sets_own_documents_not_indexed` (2) | lens B's report: "namespace 'docs' says lexical_policy: None"; 26 of 26 evaluation fixtures: "namespace 'fixtures' says lexical_policy: None" |

**Passing today, as guards (8):** the absent and `indexed` namespaces found by words and id (4); the control project
finds every file and its report names none; the validator accepts both values (2, since it ignores the field today);
the `indexed, not embedded` vectors case. They hold that S6 keeps out only what it should.

**For the CTO: the repository case is D-7's, not the engineer's.** `governance/project/path-map.yaml` is outside the
ticket's `allowed_paths`, so the two cases of `test_the_repository_marks_the_evaluation_sets_own_documents_not_indexed`
turn green only when D-7 marks the repository's path map. Lens B's report lies under `docs/**` today: a namespace of
its own cannot be added beside `docs/**` without the file matching two namespaces (`core-pathmap` refuses that), so
D-7 must either list `docs/`'s sub-folders in `docs` or mark the whole of `docs/assessment/2026-10/` (the case asks
exactly one namespace per file). `fixtures/**` likewise needs `fixtures/evaluation/**` split out, or the whole
`fixtures` namespace marked `not indexed`. Since the refusal rule, a namespace D-7 marks `not indexed` must also say
`not embedded` (`docs` is `embedded` today; `fixtures` is already `not embedded`).

**Revised (the CTO, P2, after `gov accept` on the engineer's head: S6 27 of 30).** The row
`test_the_vectors_keep_their_embedding_policy[not indexed, embedded: in the vectors only]` asked for a combination the
design cannot hold (the vectors come from the keyword chunks). It is replaced by
`test_a_namespace_not_indexed_and_embedded_is_refused_naming_it` (the refusal, planted in a scratch copy), and the
planted project's `vectors-only` namespace (`not indexed`, `embedded`) became `kept-out` (`not indexed`,
`not embedded`), so that the planted project stays valid under the rule; its file is still one of the three kept out,
by the same words. The other rows and cases are unchanged; nothing else is lowered.

**Revised again (the CTO, after `gov accept` on `d4285bad`: S6 27 of 30).** The premise of
`test_the_path_map_validator_accepts_both_values[not indexed]` planted its one namespace `embedded`, which P2 now
refuses. For `not indexed` the one-namespace project is now `not embedded` (the only combination P2 allows); the case
still asserts the value is accepted and kept and that the rebuild runs. `[indexed]` and the invalid-value cases
(none of whose values is `not indexed`) keep the namespace `embedded`. Expected on the engineer's head: 28 of 30, the
two repository cases red (D-7).

**Added from the review (S6-F1, the CTO): a store built before the policy existed is put right by the next refresh.**
`test_a_store_built_before_the_policy_is_put_right_by_the_next_refresh`, from S6's line ("a namespace whose
`lexical_policy` is `not indexed` keeps its files out of the keyword index"), without reading the engineer's code.
The keyword index is incremental by blob: the integrated code judges every file again only when the path map's (or
the rules') blob changes. The hard case is a store that has already recorded the *marked* path map's blob while still
holding the files as indexed:

1. The pre-S6 code is taken from this repository's history: `src/` of `68ce354a74c7` (`w2/integrate` at DEC-1066's
   placing; its `src/gov` names no `lexical_policy`), extracted with `git archive` into the case's temporary folder.
   The case fails, naming the commit, where the history does not hold it.
2. The planted project with no `lexical_policy` anywhere is rebuilt by that code (`gov rebuild --json
   --no-embeddings`): every file indexed.
3. The two namespaces are marked `not indexed`, `not embedded` and committed; the pre-S6 code rebuilds again. Premise,
   read from the store's `lexical_file(path, blob, indexed)` table (the pre-S6 code's documented schema, read-only):
   the store holds the marked path map's blob, and each of the three kept-out files with its blob and `indexed = 1`.
4. The path map's text is not changed again. One ordinary refresh by the code under test (`gov rebuild --json
   --no-embeddings`): no keyword search for a kept-out file's words finds it, the indexed files are still found, and
   the refresh's report names each kept-out file.

**Red on the W2-13 head** (`0f448c06`, its `src/` extracted into a scratch folder and put on `PYTHONPATH`; run in the
launch sandbox through the heavy slot): the premises hold, then "after the refresh, the keyword route still finds files
whose namespace says not indexed …: {'evaluation/lens-report.md', 'evaluation/cases/q01.yaml', 'kept-out/notes.md'}"
(the refresh sees the path map's blob unchanged and judges nothing again). The whole file on that head: **31 run, 3
failed, 28 passed** — this case and the two repository cases; S6's fresh-store cases pass there, so what this case
asks after the refresh is what the head already does on a store built from nothing. On today's integrated code
(`fd22f3d0`): 31 run, 23 failed, 8 passed, this case red the same way. Expected on the engineer's fix: 29 of 31, the
two repository cases red (D-7).

## Rewrite after implementation (DEC-1000, P-W2-13-3 (b))

The CTO decided (DEC-1000, delegated) where the lexical route's ranking is read: `lexical.search` answers `hits`
unchanged from W1-17 (the exact list: every line that holds the string, case and all, by path and line, not ranked)
and, beside it, `ranked`: chunk records best first, the exact route's chunks first (the boost), then up to about 30
chunks that match the question's words, by BM25 with the field weights id, title and body; an unavailable answer
carries `hits: []` and `ranked: []`. The fusion fuses `ranked`, not `hits`. A fresh designer rewrote seven cases to
read the ranking from `ranked` instead of the hits' order, without reading the implementation (policy 2 (c)):

1. `ranked_route::test_a_plain_word_question_returns_lexical_hits`, renamed
   `test_a_plain_word_question_returns_ranked_lexical_chunks` (the old name now names the exact list, which is empty
   for this question): `ranked` is not empty and holds `rank/z-best.md`; added: `hits` is W1-17's exact list (empty:
   no line holds the question).
2. `ranked_route::test_hits_are_ranked_best_first_by_how_well_they_match_the_words`, renamed
   `test_ranked_chunks_are_best_first_by_how_well_they_match_the_words` (`hits` is no longer ranked): best, second,
   third in that order in `ranked`, best first.
3. and 4. `ranked_route::test_a_word_in_the_id_or_the_title_ranks_above_the_same_word_in_the_body` (all four
   parameters, the title and the id pairs with their mirrors): the weighted file above the body file in `ranked`.
5. `ranked_route::test_an_exact_identifier_ranks_first` (both parameters): the holder first in `ranked`; added: no
   chunk marked `exact` below one that is not, the holder's chunk marked `exact` when the identifier is asked alone,
   and `hits` is W1-17's exact list.
6. `ranked_route::test_letter_case_does_not_change_what_a_plain_word_question_finds`: the same files in `ranked` for
   the words in lower case and in capitals, `rank/z-best.md` among them.
7. `fusion::test_the_lexical_route_hands_the_fusion_its_ranking_best_first`: the fused order is the order of the
   files of `ranked`, best first.

Each case asserts what it asserted before, on `ranked` instead of `hits`: no expectation lowered, no fixture changed,
no tolerance widened, no case dropped or skipped. Every `ranked` it reads has its form checked
(`w2_13_support.ranked_list`: the keys above, a line span, `bm25` a score or null, `exact` true or false); nothing
else about `ranked` is assumed. Every other case is unchanged: `test_a_word_matches_whole_tokens_only` and the secrets
cases still read `hits` (through `ranked_paths`), and
`fusion::test_gov_retrieve_cites_what_the_lexical_route_ranks_for_a_plain_word_question` waits for `gov retrieve`'s
bundle to fuse `ranked` (a one-line change in a file another ticket holds, outside this batch).

Run by the designer against the ticket's code (`w2/W2-13-tests` at `12bca6c58610`, this worktree's `src/`), the
two files `test_w2_13_ranked_route.py` and `test_w2_13_fusion.py`: **16 cases, 14 passed, 2 failed**:

- `ranked_route::test_an_exact_identifier_ranks_first[the identifier and words]`: "ids/z-holder.md holds QX-4471
  verbatim and is not first in the ranked list for 'QX-4471 gauge reading': ['ids/a-noise.md', 'ids/b-noise.md',
  'ids/z-holder.md', …]". No chunk of `ranked` is marked `exact` for this question: the exact route boosts only a
  question that stands verbatim on a line, not an identifier inside a worded question. Package P-W2-13-TD-4.
- `fusion::test_gov_retrieve_cites_what_the_lexical_route_ranks_for_a_plain_word_question` (not rewritten): "cited by
  it: []": `gov retrieve`'s bundle does not yet fuse `ranked` (outside this batch, above).

## What was not run by the designer

- `test_w2_13_latency.py::test_a_warm_retrieval_with_the_real_models_answers_within_the_budget` and
  `test_w2_13_bundle_unchanged.py::test_retr_a_04_cites_both_files_with_three_named_expansions_and_its_stopping_reason`
  (`needs("ollama", "reranker")`, `local_only`): they rebuild both dev tiers with the real embedder, longer than one
  of the designer's foreground commands may run. Collected, not run; the lead runs them, alone (DEC-372). Both are
  expected to pass on the base (RETR-A-04 passed at the Wave 1 exit run; W1-19's warm p95 case holds the fused
  budget today).

## Earlier tests the KPIs may require revising (named, not revised)

- **W1-17, the cases that hold a query's hits to exactly the lines that hold the string, or to none.** (No longer at
  risk from this ticket since DEC-1000: `hits` stays W1-17's exact list and the ranking goes to `ranked`.) Once a
  plain-word question returns hits (success 1, W2-M292), a multi-word query also finds the lines that hold some of its
  words, unless the hits that hold the exact string are listed apart. W1-17's fixture holds, on purpose, a runbook line
  with the error message's words in another order. At risk, by their exact-list or no-hit assertions:
  `test_w1_17_exact_query.py::test_an_error_message_query_returns_every_occurrence_with_path_and_line`,
  `::test_an_identifier_query_returns_every_occurrence_with_path_and_line` (`pool.full()`),
  `::test_a_string_with_query_syntax_characters_is_read_as_the_string_it_is`;
  `test_w1_17_freshness.py::test_an_edited_file_is_re_indexed_before_the_next_retrieval`,
  `::test_the_text_from_before_an_edit_is_not_returned_as_current`, `::test_an_uncommitted_edit_to_a_tracked_file_is_re_indexed_too`,
  `::test_a_removed_file_is_no_longer_returned`, `::test_zero_hits_from_an_up_to_date_index_is_an_available_answer`,
  `::test_a_stale_index_is_reported_by_a_retrieval_that_may_not_write`, `::test_the_first_retrieval_builds_a_missing_index`.
  The revision, if the lead's regression run shows them red: hold the hits **whose text holds the string** to the
  occurrences (as `test_every_line_that_holds_an_exact_string_is_found_with_its_file_and_line` here does), and "no
  hit" to "no hit holds the string". Nothing they protect is lowered.
- **W1-21's paging and merge cases** count candidates gathered for exact phrases; more lexical candidates may change
  their counts. Named as at risk only; the lead's regression run decides.
- **W2-M098, only under package P-W2-13-TD-1 (a):** `tests/acceptance/W1-20/test_w1_20_gaps.py::test_a_start_id_that_names_nothing_is_in_the_gap_list`,
  `::test_only_unresolved_start_ids_give_an_answer_with_gaps`, `::test_an_unresolved_id_is_told_from_one_beyond_the_depth`
  (they hold only "not `CLOSURE_COMPLETE`"), and W1-21's `test_w1_21_closure_and_gaps.py::test_an_id_that_exists_nowhere_is_named_as_a_gap_and_nothing_is_made_up`
  and `test_w1_21_dev_tier.py::test_retr_x_02_a_record_that_does_not_exist_is_a_stated_gap` (they accept two
  reasons): each would assert the one reason exactly.

## Packages

**P-W2-13-TD-4 (an identifier inside a worded question; from the DEC-1000 rewrite).** S1 and W2-L233 say "an exact
identifier still ranks first", and the case holds it in two forms: `QX-4471` alone and "QX-4471 gauge reading".
DEC-1000 says the exact route's chunks come first (the boost) and `exact` marks a chunk that holds the exact string;
it does not say whether the exact string of a worded question is the whole question or the identifier in it. The
ticket's code takes the whole question: for "QX-4471 gauge reading" no chunk is marked `exact`, and BM25 ranks the two
noise files (which hold `QX`, `4471`, `gauge` and `reading` many times) above the holder. Options: (a) the exact route
also runs on each identifier-shaped token of a question (the form S4's stated gap already recognises in "What does
DEC-9999 decide?"), its chunks first and marked `exact`; the case stands; (b) the boost only for a question that stands
verbatim on a line, the case's `[the identifier and words]` form re-scoped by a decision (an expectation lowered,
which needs the owner); (c) a heavy BM25 weight on identifier tokens instead of the boost; the case stands, with no
guarantee for an identifier that is rare in the corpus. Recommendation (a); confidence medium-high.

**P-W2-13-TD-2 (W2-M100 against lens G's R8).** W2-M100 closes on "matches whole tokens"; lens G's R8
(`docs/assessment/2026-10/G-tools-glue.md`) proposes a trigram FTS5 table for exact identifiers, which finds a string
inside a longer token (W1-17's residual: `floor_rules` in `partition_floor_rules`). The case
`test_a_word_matches_whole_tokens_only` holds the row as written ("tern" does not find "lanternfish"). Options:
(a) whole tokens, as the row and the lead's brief say (the case stands); (b) substrings through a trigram table,
the row restated by a decision and the case revised to its opposite; (c) whole tokens for the ranked route and
substrings only for a question that is one identifier, the case narrowed to plain words. Recommendation (a), the
engineer recording the decision W2-M072 asks for; confidence medium. The secrets case does not depend on the answer:
its vocabulary check works for word, stem and trigram terms.

**P-W2-13-TD-3 (allowed paths).** The bundle is assembled in `src/gov/retrieval/retrieve.py`, and the record
queries that raise under `gov retrieve` on a store that is not a database are in `src/gov/records/`; neither is in
the ticket's `allowed_paths` (`src/gov/retrieve/**` is the command only). Success 4 (the stated gap for the question
alone, and with `--id` with no unrelated items) and `test_gov_retrieve_on_an_unusable_index_answers_without_a_traceback[not a database]`
can then be met only in `src/gov/retrieve/command.py`. Options: (a) widen the paths by
`src/gov/retrieval/retrieve.py` (the stated gap where the bundle is made); (b) keep the paths and meet both in the
command; (c) re-scope the two cases. Recommendation (a); confidence medium. No case depends on which file changes.

**P-W2-13-TD-1 (W2-M098).** The stopping reason for an id no record has depends on the machine: `FACET_UNAVAILABLE`
without the code tool (the closure facet: "the code index did not answer for an id that is no record"),
`UNRESOLVED_IDS` with it. Row W2-M098 closes when it is the same everywhere and the cases assert it exactly. The
cases here accept either (as W1-21 does), and `FACET_UNAVAILABLE` only with a facet reported unavailable.
Options: (a) `UNRESOLVED_IDS` on every machine for an id that no record has and that the exact lexical search finds
in no tracked file (the code tool cannot change that answer), then the cases here, W1-21's two RETR-X-02 cases and
W1-20's three cases assert it exactly; (b) keep both reasons and re-scope the row; (c) move the row to the ticket that
owns `src/gov/closure/**`, which is outside W2-13's paths. Recommendation (a), the closure's part through (c);
confidence medium.
