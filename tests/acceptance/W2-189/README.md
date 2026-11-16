# W2-189 acceptance tests: gov retrieve answering from the last good store when HEAD has moved, naming it

Ticket DAEO-kfn1 (W2-189), profile FULL, class C2. Written by the independent test designer (MR-3) from the ticket's
KPI lines S1 to S3 and F1 to F3 as described behaviour (DEC-136), before any implementation, reading only the
integrated code as it stands at the ticket's base (`b183a850d`, DEC-963): `gov.retrieval.retrieve` (`store_of`,
`retrieve`, the stopping choice), `gov.retrieval.lexical` (`search`, `freshness`, `_freshness`, the recipe check of
DEC-1068), `gov.retrieval.semantic` (`search`, `_status`, `_vectors`), `gov.retrieve.command`, `gov.cli.main` (the text
form), `gov.util.role_paths` (the wall) and `tests/acceptance/W2-138/`, `tests/unit/retrieval/test_w2_32_pin.py` for
method. DEC-1197 (2)(i): `gov retrieve` serves the last good store and names its commit.

## How they run

    env HOME=<an empty folder> PYTHONUSERBASE=$HOME_REAL/.local PYTHONPATH=<worktree>/src TMPDIR=<scratch> \
      python3 -m pytest tests/acceptance/W2-189 -q -p no:cacheprovider -o tmp_path_retention_policy=failed

3 s for the 43 cases, in process, no network, no model. The tests use the tree `PYTHONPATH` names; without one, the
worktree's own `src`. No case is marked `skip`, `xfail` or `flaky`, none is `local_only`, and no case name holds `real`,
`green_here` or `time_limit`, so the whole-folder run (with `-m "not local_only" -k "not real and not green_here and not
time_limit"`) selects all 43.

## The planted repository (`w2_189_support.plant`)

One git repository per case, as an adopted repository is after A9 and before anything else happens to it: tracked
notes and source files each holding one planted unique word, a project path map (one namespace `open` whose
`embedding_policy` is `embedded`, `decision_register`, and a `role_paths` wall: the `engineer` may not read `walled/**`),
a gitignored file and an untracked one that exist at X but in no commit, and **the store built in place at X**
(`lexical.refresh` and `store.load`: A9's lexical and record stages, as W2-138 builds its stores, because A9's own
`gov rebuild` also runs the semantic stage, which needs a model; with `semantic=True` also `semantic.refresh`, its model
calls the stand-ins below). The secret filter is replaced (`lexical.indexable`), as the unit tests do. Nothing rebuilds
the store after X: the cases then commit, one commit at a time, with the repository's own `git` (every call pinned: no
system or user configuration, no hook), adding exactly the paths a case names.

| word | file | what happens to it after X |
|---|---|---|
| marmalade | `notes/steady.md` | nothing (the unchanged note of S1, S3, F3) |
| tamarind | `src/steady.py` | nothing (the unchanged source file) |
| zeppelin | `notes/changing.md` | the word is removed (F1) |
| gryphon | `notes/shifted.md` | two lines are put before it, so the file still holds the word, at other lines (F1) |
| kestrel | `notes/doomed.md` | the file is deleted (F1, key edge) |
| ocelot | `src/engine.py` | a function with a new word (wyvern) is added; the old word stays in the file (S3, F1) |
| kraken | `notes/newcomer.md` | the file is added (S3, F1) |
| sandpiper | `governance/adoption/A10-record.md` | the file is added, alone in its commit (S1, S2) |
| cormorant | `walled/ledger.md` | nothing; walled from `engineer` by the path map (F3) |

The command line is `gov.cli.main.main(["retrieve", "--json", "--root", <repo>, ...])` in this process, stdout read as
the envelope (`result`, `error`). `gov.retrieval.retrieve.retrieve` and `gov.retrieval.retrieve.store_of` are called
as functions on the same repositories. No question names an id except F3's stated gap (`DEC-4242`).

## The semantic facet

By default the conftest replaces `semantic.search` by a stand-in with no hit (available, so the stopping reason is the
lexical store's own), turns the file route off and makes the reranker the identity (`retrieve.rerank`,
`retrieve.last_outcome`). The cases that ask for the `semantic_endpoint` fixture (S1, S3, F1, F2) run
**`gov.retrieval.semantic` itself, unpatched** with `refresh=False`: its status gate (`_status` over the lexical
facet's `_checked`), `_vectors`, `query_vector`, over vectors built at X by the real `semantic.refresh`. Only the model
calls are replaced, as `tests/unit/retrieval/test_w2_32_pin.py` does: `semantic._ask` (the model list at the pinned
digest, the device listing on the GPU, the embedding request: a two-number vector, "holds *pelican*", "holds
*marmalade*") and `semantic._ready` (`sqlite_vec`'s distance replaced by a Python function); the machine cache is a
temporary folder. The semantic route could be driven without a model; nothing is left to a stand-in that hides the
fault.

## What the cases read, where the ticket states no form

- **Function and command line.** The ticket's "result's `store` entry" is `store_of(root)` (the function, W2-138's) and
  `result.store` of `gov retrieve --json`. S2's "the CLI's JSON carries the same three values" compares the two. The
  bundle `gov.retrieval.retrieve.retrieve` returns has no `store` key today and is not asked for one; its cases hold
  the evidence and the stopping reason (S1, S3), the walls and the left-out paths.
- **`stale`** is a sorted list of repository-relative paths, `[]` when the commit equals HEAD; a path changed by two
  commits is named once. A deleted file is a changed tracked path (one case, see "Open").
- **The text form** (S2): the line that names the commit (12 digits, as W2-138's case reads it) holds the count of stale
  paths as a number (two, in the case), read with the commit and the folder taken out of the line. The exact wording is
  open.
- **"Left out and named"** (F1): left out of the evidence (no item, no hit, no ranked chunk, no semantic hit) and named
  in `store.stale`; no other place is asserted.
- **The walls** (F3): the role's search at a moved head is walled as at a fresh store, and the file the wall closes is
  served with no role (a premise, so a wall that hides nothing cannot pass). "The existing retrieval wall cases pass
  unchanged" is the lead's run of `tests/unit/retrieval` and `tests/acceptance/W2-138`; it is not repeated here.

## KPI lines, cases and the outcome at the base (`b183a850d`)

43 cases: **28 red, 15 green (guards)**. Every red fails on its own line's behaviour: the lexical facet reports `stale`
and the search stops `FACET_UNAVAILABLE` with no evidence, or `store` has no `head` or `stale`; none fails on a premise
about the fixture itself (the guard `test_s1_guard_a_store_built_at_head...` proves the fixture answers at X). The 15
guards are green on the base and must stay green: F2's, each run on the base to find the reason it gives today, and S3's
hook check.

| KPI line | Test (node id) | At the base | Why |
|---|---|---|---|
| success-1 | `test_w2_189_moved_head.py::test_s1_gov_retrieve_after_a_stage_record_commit_returns_the_unchanged_file` | red | lexical facet `stale`, `FACET_UNAVAILABLE`, no evidence |
| success-1 | `test_w2_189_moved_head.py::test_s1_gov_retrieve_returns_a_source_file_the_commit_did_not_touch_too` | red | as above (a source file) |
| success-1 | `test_w2_189_moved_head.py::test_s1_gov_retrieval_retrieve_after_a_stage_record_commit_returns_the_unchanged_file` | red | the function's bundle: lexical `stale`, `FACET_UNAVAILABLE` |
| success-1 | `test_w2_189_moved_head.py::test_s1_the_semantic_facet_s_own_gate_is_available_at_the_moved_head` | red | `semantic.search(refresh=False)` reason `stale` (its gate takes the lexical answer); the search stops |
| success-1 | `test_w2_189_moved_head.py::test_s1_guard_a_store_built_at_head_answers_from_its_unchanged_file` | green (guard) | the fixture's store answers at HEAD; it must stay so |
| success-2 | `test_w2_189_store_named.py::test_s2_store_of_names_the_commit_the_head_and_exactly_the_added_record` | red | `store_of` has no `head`, no `stale` |
| success-2 | `test_w2_189_store_named.py::test_s2_the_json_output_carries_the_same_three_values_as_the_function` | red | `result.store` has no `head`, no `stale` |
| success-2 | `test_w2_189_store_named.py::test_s2_a_store_built_at_head_gives_empty_stale_and_a_commit_equal_to_head` | red | no `head`, no `stale` (the commit holds) |
| success-2 | `test_w2_189_store_named.py::test_s2_stale_is_sorted_and_names_a_path_once_however_many_commits_changed_it` | red | no `stale` |
| success-2 | `test_w2_189_store_named.py::test_s2_an_empty_commit_moves_the_head_and_leaves_stale_empty` | red | no `head`, no `stale` |
| success-2 | `test_w2_189_store_named.py::test_s2_the_text_form_names_the_store_s_commit_and_the_count_of_stale_paths` | red | the line names the commit (it does today) and no count of stale paths |
| success-3 | `test_w2_189_moved_head.py::test_s3_gov_retrieve_after_two_ordinary_commits_answers_queries_on_unchanged_files` | red | lexical `stale`, `FACET_UNAVAILABLE`, no evidence |
| success-3 | `test_w2_189_moved_head.py::test_s3_gov_retrieval_retrieve_after_two_ordinary_commits_answers_from_the_store` | red | as above, through the function |
| success-3 | `test_w2_189_moved_head.py::test_s3_the_answer_after_both_kinds_of_commit_is_still_named_by_its_commit` | red | `FACET_UNAVAILABLE`; and no `head`, no `stale` |
| success-3 | `test_w2_189_moved_head.py::test_s3_the_semantic_facet_s_own_gate_is_available_after_ordinary_commits` | red | semantic reason `stale`; the search stops |
| success-3 | `test_w2_189_moved_head.py::test_s3_no_refresh_hook_is_installed_in_the_planted_repository` | green (guard) | the planted repository has no hook and no `core.hooksPath` (so no case can pass by a hook) |
| failure-1 | `test_w2_189_stale_left_out.py::test_f1_a_phrase_removed_from_a_file_after_x_is_not_returned_from_it_and_the_file_is_named` | red | the store does not answer at the moved head (premise); no `stale` |
| failure-1 | `test_w2_189_stale_left_out.py::test_f1_the_lexical_facet_gives_no_hit_and_no_ranked_chunk_of_a_stale_path` | red | `lexical.search(refresh=False)` unavailable (`stale`) at the moved head |
| failure-1 | `test_w2_189_stale_left_out.py::test_f1_a_changed_file_is_left_out_whole_even_where_the_phrase_still_stands_in_it` | red | as above |
| failure-1 | `test_w2_189_stale_left_out.py::test_f1_a_phrase_planted_only_after_x_is_returned_from_no_file` | red | as above |
| failure-1 | `test_w2_189_stale_left_out.py::test_f1_a_file_changed_after_x_is_not_quoted_by_its_old_text_either` | red | as above |
| failure-1 | `test_w2_189_stale_left_out.py::test_f1_a_file_deleted_after_x_is_left_out_and_named_and_the_search_does_not_fail` | red | as above |
| failure-1 | `test_w2_189_stale_left_out.py::test_f1_the_semantic_facet_leaves_out_the_chunks_of_stale_paths` | red | `semantic.search(refresh=False)` reason `stale` |
| failure-2 | `test_w2_189_unusable.py::test_f2_guard_no_store_is_missing_for_both_facets_and_gov_retrieve_says_so` | green (guard) | both facets `missing`; the command line `STORE_MISSING` (params: `unmoved`, `record`) |
| failure-2 | `test_w2_189_unusable.py::test_f2_guard_an_empty_store_stays_empty_and_stops_facet_unavailable` | green (guard) | reason `empty`, `FACET_UNAVAILABLE`, no evidence (params: `unmoved`, `empty-commit`) |
| failure-2 | `test_w2_189_unusable.py::test_f2_guard_an_empty_store_at_a_moved_head_with_a_changed_path_stays_unavailable` | green (guard) | reason `stale` today (the changed path is checked first), `empty` or `stale` accepted |
| failure-2 | `test_w2_189_unusable.py::test_f2_guard_a_corrupt_store_file_is_unreadable_and_stops_facet_unavailable` | green (guard) | reason `unreadable`, `FACET_UNAVAILABLE` (params: `unmoved`, `record`) |
| failure-2 | `test_w2_189_unusable.py::test_f2_guard_a_changed_keyword_index_recipe_is_stale_and_stops_facet_unavailable` | green (guard) | `lexical_split_identifiers: true`, reason `stale` (params: `uncommitted`, `committed`, `committed-and-moved`) |
| failure-2 | `test_w2_189_unusable.py::test_f2_guard_a_changed_embed_recipe_is_stale_for_the_semantic_facet_and_stops_facet_unavailable` | green (guard) | `embed_headers: true`, semantic reason `stale`, nothing embedded (params as above) |
| failure-3 | `test_w2_189_store_named.py::test_f3_the_moved_head_result_always_carries_commit_head_and_stale` | red | `result.store` carries `commit`, `root` only (params: `bundle`, `stated-gap`, `recipe-changed`; `stated-gap` is red first on its premise: the stated gap is not reached at a moved head, the search stops `FACET_UNAVAILABLE`) |
| failure-3 | `test_w2_189_store_named.py::test_f3_stale_holds_tracked_paths_only_untracked_and_ignored_files_never_appear` | red | no `stale` |
| failure-3 | `test_w2_189_store_named.py::test_f3_untracked_and_ignored_changes_alone_leave_stale_empty` | red | no `head`, no `stale` |
| failure-3 | `test_w2_189_store_named.py::test_f3_a_walled_path_is_withheld_from_the_role_through_a_moved_head_search` | red | the walled file is not served even with no role (premise: lexical `stale`) |
| failure-3 | `test_w2_189_store_named.py::test_f3_the_role_s_search_through_the_function_is_walled_at_a_moved_head_too` | red | as above, through the function |

"The existing retrieval wall cases (tests/unit/retrieval, tests/acceptance/W2-138) pass unchanged" (failure-3) is mapped
in prose: it is the lead's run of those two folders, not a case here.

## Why each guard is a guard, and what F2 holds

F2 is about stores that cannot be answered from. Each is combined with a moved HEAD (a commit after X: an empty one, or
a stage record), so a path that answers from the last good store cannot answer them. The base's reason was found by
running each on it: no store `missing` (and `STORE_MISSING` from the command line), an empty store `empty`, a corrupt
file `unreadable`, a changed recipe `stale`. An empty store with a *changed path* gives `stale` today (the path check
comes first); the case accepts `empty` or `stale`. The recipes: the keyword index's `lexical_split_identifiers` (DEC-1068
M4, an `INDEX_FLAGS` switch) and the vectors' `embed_headers` (DEC-1067 order (5), driven through the real semantic gate
with the stand-in embedder); each as a working-tree change, as a commit, and as a commit followed by another, so a
design that treats `rebuild.yaml` as one more stale path cannot pass. The ticket's "a changed embed recipe" is read as
both.

## A check of the tests themselves

A scratch copy of `src` (never committed) with about 35 lines of sketch (`store_of` gaining `head` and `stale` from
`git rev-parse HEAD` and `git diff --name-only <commit> HEAD`; `lexical.serving`: a store stale only by changed files,
with the recipe as built, is served with those paths left out of the keyword hits, the ranked chunks, the semantic hits
and every route; the text line given the count) passes all 43 cases. On the base: 28 red, 15 green.

## Open (also returned to the lead as `unresolved`)

- **Uncommitted working-tree changes** to a tracked file (not in the commit range) are not in the ticket's lines: no
  case. The keyword index today compares blobs with the working tree, so such a path is stale in that sense.
- **Whether `stale` lists a tracked path the asking role is walled from**: not stated; no case (the walled path is
  never changed after X here).
- **A deleted tracked file** is read as a changed path (named in `stale`, left out, no crash): one case (F1); a rename
  is not asserted (`git diff --name-only` names the new path only).
- **The text form's wording**: the count only; and only for a moved head (two paths), not for a store at HEAD.
- **The stated gap at a moved head** (`UNRESOLVED_IDS`, F3's second parameter) assumes the id check may run against the
  last good store: an id in no record and no line of the index is a stated gap, not `FACET_UNAVAILABLE`.

## Files

- `w2_189_support.py`: the planted repository, its commits, the command line in process, the readers.
- `conftest.py`: the stand-ins (autouse) and the `semantic_endpoint` fixture.
- `test_w2_189_moved_head.py` (S1, S3), `test_w2_189_store_named.py` (S2, F3), `test_w2_189_stale_left_out.py` (F1),
  `test_w2_189_unusable.py` (F2).
