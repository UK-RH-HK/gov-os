# W1-17 acceptance tests — lexical index and shared store

Ticket `DAEO-rxln` (`W1-17`), profile STANDARD (DEC-221). Written by the Independent Test Designer before
implementation (MR-3, DEC-069), from the ticket's KPI lines, Contract v4 (CAP-18, CAP-17, CAP-11, CAP-03, CAP-07,
CAP-38) and the decisions named below. The sources G-17, G-20 and G-21 were not read.

**53 test functions, 65 cases** in eight files. Run:

```
PATH=$HOME/.nvm/versions/node/v22.23.3/bin:$PATH python3 -m pytest tests/acceptance/W1-17 -q -p no:cacheprovider
```

## Red before implementation

Observed on `w1/W1-17` at `1ddfa3c1` plus this suite: **64 errors, 1 passed**. Every one of the 64 stops in the
`api` fixture with one line:

```
the lexical index does not exist: ModuleNotFoundError: No module named 'gov.retrieval.lexical'
```

The seven family-check cases stop at the same line today; once the module exists and the declaration does not,
they stop at `the index-freshness check is not registered: nothing matches
template/governance/kernel/checks/index-freshness*.yaml`.

The one case that passes is a premise, not a test of the ticket:
`test_the_secret_filter_lets_the_fixture_corpus_through_and_nothing_else` asks W1-15's `gov.secrets.indexable` about
the fixture and expects the eleven corpus files through and the product-data file and the two planted secrets out.
It shows the fixture is what the other tests take it to be.

**The tests were also run against a throwaway reference implementation**, kept in the session's scratch directory outside the repository and never committed
(a naive substring index over SQLite, about 190 lines): 65 of 65 passed, the three dev-tier cases included. So the
suite is satisfiable, and its expectations do not contradict each other. The reference is not the design: it has no
FTS5 and nothing carried.

## The interface the tests assume

A Python interface, as `gov.store` and `gov.tasks` are (DEC-275): no KPI names a `gov` command and `src/gov/cli/**`
is outside the ticket's paths. All six functions are reached as attributes of **`gov.retrieval.lexical`**
(`src/gov/retrieval/lexical*`); where the code lives among `lexical*`, `chunking*` and `store*` is the engineer's.
`root` is the project root, a `Path`. Every value is plain JSON data. Each call is made in a new Python process
whose working directory is not the project.

| Function | Returns |
|---|---|
| `refresh(root)` | Brings the index up to date with the tracked files and returns `{"digest": <sha256 hex>, "indexed": [<path>, …]}`. `indexed` is the paths whose content was chunked in this call, each once; the tests compare it sorted. More keys are allowed. |
| `search(root, query, refresh=True)` | `{"available": bool, "facet": "lexical", "state": str, "reason": str or None, "hits": [...]}`. `query` is an exact string. With `refresh=True` the index is brought up to date first. With `refresh=False` nothing is written. Unavailable: `available` false, `state` `"FACET_UNAVAILABLE"`, `reason` one of `"missing"`, `"empty"`, `"stale"`, `hits` `[]`. Available: `state` anything else, `reason` empty or `None`. |
| a hit | `{"path", "line", "text", "chunk_id", "parent_id"}`: one per line that holds the query string; `line` is 1-based; `text` holds the query string. An occurrence is reported once. |
| `freshness(root)` | `{"status": "fresh" | "stale" | "empty" | "missing", "stale": [<path>, …]}`. Writes nothing. `stale` names tracked paths whose content the index does not hold as it stands, and indexed paths that are gone. |
| `digest(root)` | The sha256 hex digest of the index as it stands. Writes nothing. |
| `chunks(root, path=None)` | The chunk records, all or one file's: `[{"chunk_id", "path", "start_line", "end_line", "parent_id"}, …]`, the same list in the same order for the same content. |
| `parent(root, parent_id)` | `{"parent_id", "path", "kind", "start_line", "end_line"}`; `kind` is `"section"` for a document, `"function"` or `"module"` for code. |

The family check is a declaration matching `template/governance/kernel/checks/index-freshness*.yaml`, listed by
`gov check --list --json` with a family that reads "index freshness" and the five fields `id`, `family`, `tier`,
`severity`, `command`. The tests run `command` by `sh -c` in the project root with this worktree's `src/` on
`PYTHONPATH`; exit 0 is green (DEC-285).

## The six points: what the sources settle, and what is a package

| Point | Settled by | In the tests |
|---|---|---|
| **1. Interface** | DEC-275 (a Python interface for the store); DEC-260 and DEC-257 (a facet's result in `gov.retrieval` is a mapping with `available`, `facet`, `state`, never a raise, with `state` `FACET_UNAVAILABLE`); the ticket's `allowed_paths`. The function names and the `refresh=False` mode are not in any source: **package DP-1**. | All files |
| **2. Corpus** | `governance/project/path-map.yaml` has no exclude key. What the map excludes is a namespace whose `memory_class` is not `governance`, and `gov.secrets.indexable` already drops it, with files holding a secret, unreadable files and paths with no namespace (DEC-285, DEC-225). So the corpus is `git ls-files` passed through `indexable`. No package. | `test_w1_17_corpus.py` |
| **3. Freshness and scale** | Incrementality is read from `refresh`'s `indexed`. What "2.8 s" measured is in G-20, which was not read: **package DP-3**. Whether the corpus is the working tree or `HEAD`: **package DP-7**. | `test_w1_17_incremental.py`, `test_w1_17_freshness.py`, `test_w1_17_dev_tier.py` |
| **4. Empty or stale** | CAP-17 acceptance (`FACET_UNAVAILABLE`, "never returns the old text as current"); DEC-257 for the shape; DEC-322 for why a retrieval that may not write must exist (worker sessions read the live store and may not write it). The three reasons and "the whole facet is unavailable when one file is stale": **package DP-4**. | `test_w1_17_freshness.py` |
| **5. Digest and the check** | DEC-276 by analogy (logical content, not file bytes); DEC-285 (`sh -c`, exit 0 is green). What the check does with no index, and that it prints the stale paths: **package DP-5**. | `test_w1_17_digest.py`, `test_w1_17_family_check.py` |
| **6. Parent ids** | DEC-091; CAP-18.b (document→section→chunk, code file→module→function). Function level for Python through the standard library, module level elsewhere: **package DP-6**. | `test_w1_17_parents.py` |

## KPI lines and their tests

| KPI line | File | Tests | Red reason today |
|---|---|---|---|
| **Success 1.** Carried FTS5 and chunking ported into `src/gov`; blob-hash incremental index in the shared store; every chunk record carries `parent_id` [CAP-18.b] | `test_w1_17_incremental.py` · `test_w1_17_parents.py` | `test_a_second_refresh_indexes_nothing` · `test_only_the_file_whose_blob_changed_is_indexed_again` · `test_a_file_rewritten_with_the_same_content_is_not_indexed_again` · `test_a_new_tracked_file_is_the_only_one_indexed` · `test_an_index_brought_up_to_date_equals_one_built_from_nothing` · `test_the_index_is_in_the_shared_store_beside_the_record_graph` · `test_building_the_index_changes_no_tracked_file` · `test_every_chunk_record_carries_a_parent_that_contains_it` · `test_the_chunks_of_one_file_are_listed_by_its_path` · `test_a_chunk_of_a_document_has_its_section_as_parent` · `test_two_sections_of_one_document_are_two_parents` · `test_a_chunk_of_code_has_a_function_or_a_module_as_parent` · `test_a_chunk_inside_a_python_function_has_that_function_as_parent` · `test_python_code_outside_any_function_has_the_module_as_parent` · `test_chunk_and_parent_ids_are_the_same_in_a_second_build` · `test_a_hit_names_the_chunk_record_it_comes_from` | The module does not exist |
| **Success 2.** Changed blobs re-index before the next retrieval (2.8 s scale on a-dev); an empty or stale index is reported, never returned as absent [CAP-17.a] | `test_w1_17_freshness.py` · `test_w1_17_dev_tier.py` | `test_an_edited_file_is_re_indexed_before_the_next_retrieval` · `test_an_uncommitted_edit_to_a_tracked_file_is_re_indexed_too` · `test_a_removed_file_is_no_longer_returned` · `test_a_renamed_file_is_returned_under_its_new_path_only` · `test_zero_hits_from_an_up_to_date_index_is_an_available_answer` · `test_a_stale_index_is_reported_by_a_retrieval_that_may_not_write` · `test_a_missing_index_is_reported_by_a_retrieval_that_may_not_write` · `test_the_first_retrieval_builds_a_missing_index` · `test_an_empty_index_is_reported_not_answered_as_zero_hits` · `test_freshness_names_the_paths_that_are_stale` · `test_a_file_the_corpus_excludes_does_not_make_the_index_stale[2]` · `test_one_changed_file_is_re_indexed_by_the_next_retrieval_within_the_bound` | The module does not exist |
| **Success 3.** Registers the index-freshness family check: the index digest matches the tracked blobs, and a stale index is reported [CAP-38.b] | `test_w1_17_family_check.py` · `test_w1_17_digest.py` | `test_the_check_is_registered_in_the_kernel_template` · `test_the_check_is_green_on_an_index_that_matches_the_tracked_blobs` · `test_the_check_is_not_green_on_a_stale_index_and_names_the_file[3]` · `test_the_check_is_green_again_once_the_index_is_refreshed` · `test_the_check_is_not_green_when_there_is_no_index` · `test_the_digest_of_the_index_is_the_one_the_refresh_reported` · `test_the_digest_changes_when_the_tracked_content_changes[4]` | The module does not exist; then, the check is not registered |
| **Success 4.** The corpus is the whole tracked repository minus what the secret filter and the path map exclude; no hand-kept include list [CAP-03.d] | `test_w1_17_corpus.py` · `test_w1_17_dev_tier.py` | `test_every_tracked_governance_file_is_indexed_whatever_its_folder_or_extension` · `test_a_new_tracked_file_under_a_new_folder_is_indexed_with_no_configuration_change` · `test_an_untracked_or_ignored_file_is_not_indexed` · `test_a_file_in_a_product_namespace_is_not_indexed` · `test_the_path_map_decides_what_is_product_data` · `test_a_file_with_a_secret_is_not_indexed_and_the_secret_is_in_no_store[2]` · `test_a_file_that_gains_a_secret_leaves_the_index` · `test_the_whole_tier_is_indexed_and_no_canary_reaches_the_store` · premise: `test_the_secret_filter_lets_the_fixture_corpus_through_and_nothing_else` | The module does not exist |
| **Success 5.** An exact string, identifier or error-message query returns every occurrence with file path and line [CAP-11.a] | `test_w1_17_exact_query.py` | `test_an_error_message_query_returns_every_occurrence_with_path_and_line` · `test_an_identifier_query_returns_every_occurrence_with_path_and_line[3]` · `test_occurrences_far_into_a_long_file_are_each_reported_once_with_their_line` · `test_a_string_with_query_syntax_characters_is_read_as_the_string_it_is[4]` · `test_the_same_content_at_two_paths_is_reported_at_both` | The module does not exist |
| **Failure 1.** A retrieval returns pre-edit text as current | `test_w1_17_freshness.py` · `test_w1_17_corpus.py` | `test_the_text_from_before_an_edit_is_not_returned_as_current` · `test_a_stale_index_is_reported_by_a_retrieval_that_may_not_write` · `test_an_uncommitted_edit_to_a_tracked_file_is_re_indexed_too` · `test_a_removed_file_is_no_longer_returned` · `test_a_file_that_gains_a_secret_leaves_the_index` · `test_the_path_map_decides_what_is_product_data` | The module does not exist |
| **Failure 2.** Rebuild digest differs between two runs | `test_w1_17_digest.py` · `test_w1_17_incremental.py` · `test_w1_17_dev_tier.py` | `test_a_rebuild_after_the_derived_state_is_deleted_gives_the_same_digest` · `test_a_build_elsewhere_gives_the_same_digest` · `test_an_index_brought_up_to_date_equals_one_built_from_nothing` · `test_a_rebuild_of_the_tier_gives_the_same_digest` · guard: `test_the_digest_changes_when_the_tracked_content_changes[4]` | The module does not exist |

**Count.** KPI lines with tests: 7 of 7 (5 success, 2 failure).

| Covers id | Tests |
|---|---|
| **CAP-18.b** hierarchical retrieval: document→section→chunk, code file→module→function | all of `test_w1_17_parents.py`; `test_a_hit_names_the_chunk_record_it_comes_from`. Expanding a hit to its parent and naming the expansion in the bundle is W1-20. |
| **CAP-17.a** changed content re-indexed before the next retrieval, or the facet reported unavailable | all of `test_w1_17_freshness.py`; the timed dev-tier case |
| **CAP-38.b** governance test family "index freshness" | all of `test_w1_17_family_check.py` |
| **CAP-03.d** whole-repository corpus minus secrets | all of `test_w1_17_corpus.py`; `test_the_whole_tier_is_indexed_and_no_canary_reaches_the_store` |
| **CAP-11.a** exact strings, identifiers and error messages with file and line | all of `test_w1_17_exact_query.py` |

## How the tests decide

- **Every project is a temporary git repository** (DEC-322): a clone of one fixture repository, with its own path
  map, a copy of `template/.gitleaks.toml` at its root, a `.gitignore` naming `.gov-runtime/`, and its own
  `.gov-runtime/store.db`. No test builds an index in this worktree or writes its `.gov-runtime/`.
- **The fixture corpus** is eleven tracked files: Markdown, Python, TypeScript, JSON, a Makefile, a file with no
  extension, a 3000-line file, and two files with the same content. One more tracked file stands in a namespace
  the fixture's map classes as product data (`tenant-exports/**`, a name this repository's own map does not use).
- **Every occurrence** is computed from the fixture's own text: each line of a corpus file that holds the query
  string, as `(path, line)`. The answer must be exactly that set, each place once. A line holding the same words in
  another order is in the fixture and is not an occurrence.
- **Incremental** means `refresh` reports as `indexed` only the paths whose blob changed. A file written again with
  the same content a day later is not indexed again.
- **The path map decides.** One test commits a changed map and expects both directions to follow: the product file
  is now returned, and a file of a namespace that became product data is no longer returned. So a change of the map
  (or of the rules) re-judges files whose own blob did not change.
- **Secrets.** The planted strings are the canary as W1-15's KPI writes it, found by the canary rule, and a private
  key the gitleaks defaults find. Neither depends on the `gov-token` rule DEC-325 changes. They are built at run
  time from parts; none stands whole in a committed file. "In no store" means no file under `.gov-runtime/` holds
  the bytes.
- **Never as absent.** With `refresh=False`, a stale index answers three queries (the old sentence, the new one,
  a string that occurs nowhere) with `FACET_UNAVAILABLE` and no hit, and the index's digest is unchanged afterwards.
  The same string that occurs nowhere, asked of an up-to-date index, is an available answer with zero hits.
- **Empty** is a repository whose map classes every file as product data: the index is built and holds no chunk.
- **The digest** is compared after deleting `.gov-runtime/` and waiting more than a second; across a clone in
  another path with files aged 400 days, another time zone and another hash seed; and between an index refreshed
  step by step and one built once from the final commit. Four content changes must each give another digest.
- **Shared store.** After a refresh, every file under `.gov-runtime/` is named `store.db…`; `gov.store.load` before
  and after leaves the index's digest and answers alone, and the refresh leaves `gov.store.digest` alone.
- **The check** is green on an up-to-date index in a tree that also holds a product file and a canary file; not
  green after a committed edit, a new file or a removed file, with the path in its output and no traceback; it
  changes nothing in the index; green again after a refresh; not green with no index, writing nothing.

## `local_only` (3 cases) and gitleaks

- `test_w1_17_dev_tier.py` clones `$GOV_DEV_TIERS/a-dev` (default `~/gov-os-workbench/synthetic/a-dev`, by exact
  path) into a temporary directory, adopts the clone with a one-namespace governance map, and indexes it once for
  the file. Skipped when the tier is absent. Deselect with `-m "not local_only"` (62 cases remain). The three cases
  run in the order written; one indexing job at a time.
- **The scale figure.** One call is timed: the `search` that follows one edited, committed file. The bound is 10 s,
  generous against "2.8 s scale" (package DP-3). The full build is not timed.
- **gitleaks.** Every build of an index calls `gov.secrets.indexable`, which runs the gitleaks binary (DEC-287).
  The tests pass `PATH` on to the child. Nothing is installed: once the interface exists, a machine without
  `gitleaks` on `PATH` skips the whole suite; until then every case fails with the red reason above. The W1-15
  suite marks only the cases that run the binary directly; here every case depends on it through the filter, so the
  skip is in the `api` fixture and the cases are not marked.

## Not tested, on purpose

- That the implementation uses SQLite FTS5 or the carried code: the tests see behaviour only. The unit tests under
  `tests/unit/retrieval/**` and the review are where "carried, ported" is shown.
- A query that is part of a token (`floor_rules` inside `partition_floor_rules`), a query in another letter case,
  word stems, a query spanning two lines, an empty query, ranking and any result limit. The sources do not say.
- The parent of text before a document's first heading, of a document with no heading, of nested headings, of a
  class body, of a nested function, and of a file that is neither a document nor code: the tests ask only that the
  parent is in the same file and contains the chunk.
- Chunk size and overlap; the form of `chunk_id` and `parent_id` beyond being stable across builds.
- Binary files, files that are not UTF-8, symbolic links, submodules.
- The namespace fields `export_policy`, `embedding_policy` and `permitted_roles` (the W1-08 residuals DEC-289 moved
  to "W1-17 or W1-24"): no KPI of this ticket reads them; the lexical corpus follows `memory_class` only.
- `gov rebuild` and `gov retrieve` (W1-27, W1-20), the commit-time hook (CAP-17.b, Wave 2), zero-result canaries
  (CAP-17.c, W1-22).
- A file replaced between the filter's answer and the indexer's read (W1-15 residual; reasoned, not testable
  deterministically).
- Concurrent refreshes of one store.

## Decision packages

Returned in full in the designer's final message. Every one is encoded in the tests as its recommended option.

| Package | Question | Tests that hold the recommended option |
|---|---|---|
| **DP-1** | The public interface: six functions of `gov.retrieval.lexical`, with a `refresh=False` retrieval | every test |
| **DP-3** | What "2.8 s scale on a-dev" bounds, and the bound | `test_one_changed_file_is_re_indexed_by_the_next_retrieval_within_the_bound` |
| **DP-4** | What a missing, empty or stale index returns | the three `…is_reported…` tests, `test_the_first_retrieval_builds_a_missing_index` |
| **DP-5** | The check with no index, and what it prints | `test_the_check_is_not_green_when_there_is_no_index`; the `…names_the_file[3]` cases |
| **DP-6** | Function-level parents for Python through the standard library | `test_a_chunk_inside_a_python_function_has_that_function_as_parent`, `test_python_code_outside_any_function_has_the_module_as_parent` |
| **DP-7** | The corpus is the tracked files as they stand in the working tree, not `HEAD` | `test_an_uncommitted_edit_to_a_tracked_file_is_re_indexed_too` |
