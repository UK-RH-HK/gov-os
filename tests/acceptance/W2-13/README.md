# W2-13 acceptance tests: RETR-X-02 and a ranked lexical route (BM25, SQLite FTS5)

Ticket `DAEO-zqvn` (W2-13), profile FULL. Written by the independent test designer (MR-3) from the ticket's KPI lines,
its card (`docs/plan/WAVE_2_WBS.md`, W2-13), its list rows and its sources (DEC-725, DEC-900), in parallel with the
engineer and without reading the implementation (DEC-462, DEC-963). Other decisions used: DEC-260, DEC-342, DEC-343,
DEC-396, DEC-414, DEC-372, DEC-732, DEC-911, DEC-956 item 2; AR-9; CAP-11.

**56 cases from 32 test functions in seven files**, with a support module (`w2_13_support.py`) and a conftest.
Seven of S1's and S2's cases were rewritten after implementation to read the lexical route's ranking from `ranked`
(DEC-1000, P-W2-13-3 (b)): see "Rewrite after implementation".

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
