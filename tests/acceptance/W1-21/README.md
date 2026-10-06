# W1-21 acceptance tests: `gov retrieve` with completeness

Written before the implementation by the independent test designer (MR-3) from the ticket's KPI lines, its
`covers` ids and its sources. 119 cases in ten files. Behaviour is reached through public interfaces only: the
function `gov.retrieval.retrieve.retrieve`, the command `gov retrieve`, and the check declaration that
`gov check --list --json` lists. Every case builds its own project in a temporary directory; nothing reads or
writes this repository's `.gov-runtime/`.

Run: `python3 -m pytest tests/acceptance/W1-21 -q -p no:cacheprovider`

## The interface the tests fix

Several points of it are not in the sources. They are written against the recommended option of a decision
package (DP-1 to DP-9, in the designer's return) and marked below; a different decision changes the named
constant in `w1_21_support.py` or the named cases, not the rest.

### Python

    gov.retrieval.retrieve.retrieve(root, query, *, ids=(), ticket=None, radius=0, batch_size=None,
                                    bundle_budget=None, continuation=None, reranker=None) -> dict

* `root`: the project. The call only reads: it refreshes no index, loads no store, makes no `.gov-runtime/`.
* `query`: the question, a string. `ids`: record or symbol ids to close over. `ticket`: a ticket id; it is closed
  over like an id, and failure and lesson records in its scope come ahead.
* `radius`: the impact radius, 0 to 4. It sets the follow-up rounds (1, 1, 3, 8, 8) and the closure depth
  (`gov.closure.depth_of_radius`).
* `batch_size`: candidates per batch; `None` is the default, which the tests do not fix (it is below 30).
* `bundle_budget`: tokens (four characters each) the bundle may hold after parent expansion; `0` expands nothing.
* `continuation`: the token of an earlier bundle of the same question and arguments. Any other value raises
  `gov.cli.errors.GovError` with a code.
* `reranker`: a loader, as `gov.retrieval.fusion.search` takes it; `None` is the pinned default.

### The bundle

| key | value |
|---|---|
| `stopping_reason` | one string of `CLOSURE_COMPLETE`, `SATURATED`, `DEPTH_LIMIT_REACHED`, `BUDGET_EXHAUSTED_WITH_GAPS`, `FACET_UNAVAILABLE`, `UNRESOLVED_IDS` |
| `evidence` | list, best first, failure and lesson records of the ticket's scope ahead. Each: `id`, `sha256` (of the cited file's bytes or of the cited lines), `path`, `start_line`, `end_line`, `text` (found in those lines), `chunk_id` (a chunk of the lexical index, cited once), `routes` (of `lexical`, `semantic`, `closure`), `batch` (1-based) |
| `batches` | list, at least one entry, each with `size` (at most the batch size) |
| `merge` | `candidates` (int), `duplicates` (int), `dropped` (list of `{path, id, reason}`; `reason` is `SUPERSEDED` for a superseded record), `reranked` (bool) |
| `expansions` | list of `{chunk_id, parent_id, path, start_line, end_line}`: one for each evidence item cited at its parent's span |
| `gaps` | list of maps with a `reason` and an `id` and/or a `path`: ids the closure did not resolve or reach, and candidates not gathered |
| `facets` | `lexical` and `semantic`, each `{available, reason}`; `closure` with `available` when a ticket or an id was given |
| `budget` | `rounds: {limit, used}` (the retrieval spend) and `bundle: {limit, used}` (the bundle budget) |
| `continuation` | `null`, or a token; a bundle with a token never says `CLOSURE_COMPLETE` or `SATURATED` |

### Command (`src/gov/retrieve/command.py`, DEC-317)

    gov retrieve [--json] [--root <dir>] [--ticket <id>] [--id <id>]... [--radius <R>] [--batch-size <N>]
                 [--bundle-budget <N>] [--continue <token>] <query>

The API-0002 envelope with the bundle as `result`. Exit 0 with a bundle (also one that says
`BUDGET_EXHAUSTED_WITH_GAPS` or `FACET_UNAVAILABLE`); exit 1 with `ok: false` and `error.code` for a governance
error (a token that is none); exit 2 for a usage error (no question, an option that is no number).

## KPI lines and covers ids

| KPI line | covers | cases |
|---|---|---|
| S1 paging with continuation | CAP-16.a | `test_w1_21_paging.py`: batches, batch size does not change what is gathered, continuation neither skips nor repeats, tokens refused; `test_w1_21_command.py::test_a_bundle_cut_by_the_budget_is_continued_by_its_token` |
| S1 facets | CAP-16.a | `test_w1_21_merge.py::test_the_bundle_names_the_routes_and_their_state`; `test_w1_21_closure_and_gaps.py` (closure facet, unavailable routes) (DP-8) |
| S1 dedup by chunk hash | CAP-18.a | `test_w1_21_merge.py::test_a_chunk_both_routes_return_is_cited_once_and_names_both`, `::test_small_batches_cite_no_chunk_twice`; `check_bundle` on every bundle |
| S1 authority/current filter | CAP-51.b | `test_w1_21_authority.py` (all) |
| S1 one rerank over the merged set | CAP-18.a | `test_w1_21_merge.py::test_several_batches_are_reranked_in_one_pass_over_the_merged_set`, `::test_a_continued_bundle_is_reranked_once_too`, the absent and the dying reranker (DP-9) |
| S2 id, sha256, one stopping reason | CAP-55.a | `test_w1_21_bundle.py` (all); `check_bundle` in every other file |
| S3 RETR-A-04 and RETR-X-02 multi-batch | CAP-16.b | `test_w1_21_dev_tier.py::test_retr_*`; on the fixture `test_w1_21_closure_and_gaps.py::test_a_tickets_closure_is_gathered_over_several_hops`, `::test_an_id_that_exists_nowhere_*` |
| S4 parent expansion within the bundle budget, named | CAP-18.b | `test_w1_21_expansion.py` (all) (DP-3) |
| S5 the retrieval-regression family check | CAP-38.b | `test_w1_21_family_check.py`; the baselines in `test_w1_21_dev_tier.py::test_the_dev_query_set_meets_*` (DP-7) |
| S6 radius-scaled spend budget, apart from the packet ceiling | CAP-04.c, CAP-16.c | `test_w1_21_paging.py::test_the_follow_up_rounds_scale_with_the_radius`, `::test_reaching_the_spend_budget_*`, `::test_a_larger_radius_gathers_more`, `::test_the_spend_budget_is_separate_from_the_bundle_budget` (DP-2) |
| S7 failure or lesson record ahead | CAP-14.a (and CAP-41's line) | `test_w1_21_failure_memory.py` (all) (DP-5) |
| F1 a batch-size limit reported as completeness | CAP-16.a | `test_w1_21_paging.py::test_a_batch_size_limit_is_never_reported_as_completeness[1,2,4]`, `::test_the_gap_list_names_what_was_not_gathered`; `check_bundle` (a token never with a reason that says nothing is left) |
| F2 a superseded record cited as current | CAP-51.b | `test_w1_21_authority.py`: by the exact string (three markings), the vectors, the closure, a lesson ahead, a continuation, a later commit, no record graph; `test_w1_21_dev_tier.py::test_no_file_whose_frontmatter_says_superseded_*` |

Also asked for: a sha256 that does not match the bytes (`test_w1_21_bundle.py::test_a_file_changed_after_the_index_*`,
and `check_citation` on every bundle); two stopping reasons or none (`::test_the_stopping_reason_is_one_value_*`,
`check_bundle`); a token that skips or repeats (`test_w1_21_paging.py::test_the_continuation_neither_skips_nor_repeats`);
non-deterministic output (`test_w1_21_bundle.py::test_two_runs_*`, `test_w1_21_command.py::test_repeated_runs_print_the_same_bytes`);
absent models, endpoint, index, store and code tool (`test_w1_21_closure_and_gaps.py`, `test_w1_21_bundle.py`
`::test_a_bundle_without_the_embedding_endpoint_has_the_same_form`, `test_w1_21_merge.py` reranker cases).

## Expected red before the implementation

All 119 cases fail at set-up, for one of three reasons, each from a fixture of `conftest.py`:

| reason | cases |
|---|---|
| `gov.retrieval.retrieve.retrieve does not exist: ModuleNotFoundError` (fixture `api`) | 103: every case of the authority, bundle, closure_and_gaps, dev_tier, expansion, failure_memory, merge and paging files |
| `gov retrieve is not built: there is no src/gov/retrieve/command.py (DEC-317)` (fixture `cli`) | 14: every case of `test_w1_21_command.py` |
| `the retrieval-regression check is not registered: nothing matches template/governance/kernel/checks/retrieval-regression*` (fixture `family_check`) | 2: `test_w1_21_family_check.py` |

No case fails on a behaviour assertion before the module exists; none passes.

## What each case needs

* Every file but `test_w1_21_family_check.py::test_the_check_is_registered_*` needs `gitleaks` on PATH and
  `sqlite_vec` importable (`needs` marker; a case skips with the reason when one is absent).
* **No model, no Ollama, no reranker, no code tool**: all 108 cases outside `test_w1_21_dev_tier.py`, and seven of
  its eleven. The embedding endpoint is a stand-in on a loopback port (`OllamaStandIn`), the reranker a stand-in
  loader that counts its loads and passes, the code tool is absent from the scratch PATH on purpose.
* **Real Ollama with `qwen3-embedding:0.6b` and the reranker environment** (`needs("ollama", "reranker")`), four
  cases of `test_w1_21_dev_tier.py`: `test_retr_a_04_finds_and_cites_both_implementations`,
  `test_the_dev_query_set_meets_the_hit_at_5_pass_line`, `test_the_dev_query_set_meets_the_forbidden_citation_baseline`,
  `test_every_measured_bundle_was_reranked_from_both_routes`.
* **The dev tiers** (`GOV_DEV_TIERS`, default `~/gov-os-workbench/synthetic`): all of `test_w1_21_dev_tier.py`
  (`local_only`); a case skips when a tier or the query set is not on the machine.
* **The real code tool**: no case. The symbol side of the closure is W1-20's; here the tool is always absent.

## Cases that depend on `src/gov/retrieve/command.py`

The file is outside the ticket's `allowed_paths` (the lead raised that package). All 14 cases of
`test_w1_21_command.py` depend on it, and so does the revision of W1-07's lists below. No other case does.

## Written against a recommended option

| package | what the cases assume | cases |
|---|---|---|
| DP-1 interface | names of the module, function, arguments, bundle keys, options | all; the names are constants at the top of `w1_21_support.py` |
| DP-2 paging and spend | a follow-up round is one more batch; rounds 1/1/3/8/8 by radius; the token is refused for another question | `test_w1_21_paging.py`; `ROUNDS_BY_RADIUS` |
| DP-3 bundle budget | tokens of four characters; it bounds expansion, a child hit is never dropped for it; `0` expands nothing | `test_w1_21_expansion.py`; the paging and merge cases pass `bundle_budget=0` |
| DP-4 authority | `SUPERSEDED` status or a `SUPERSEDES` edge (sourced); `DEPRECATED` is must-not-cite; a file with `status: SUPERSEDED` the store could not load is dropped | `test_a_must_not_cite_record_is_not_cited`, `test_a_superseded_file_the_store_could_not_load_is_not_cited`, `test_no_file_whose_frontmatter_says_superseded_*`; `merge.dropped` in `test_the_bundle_names_what_the_filter_dropped_and_why` |
| DP-5 scope match | types `failure` and `lesson`; in scope = joined to the ticket by a typed edge (`constrains`) | `test_w1_21_failure_memory.py`, `test_a_superseded_lesson_is_not_put_ahead` |
| DP-6 which reason wins | `FACET_UNAVAILABLE` over the budget over the depth over unresolved ids; a dying reranker ends nothing | `test_w1_21_closure_and_gaps.py`, the stale-index case, the dying-reranker case |
| DP-7 baselines | forbidden citations at most 2; the pass line of 80 is DEC-414 | `test_the_dev_query_set_meets_the_forbidden_citation_baseline`; `FORBIDDEN_BASELINE` |
| DP-8 facets | facets are the routes, reported with their state | `test_the_bundle_names_the_routes_and_their_state` |
| DP-9 one rerank | one `score` call over all candidates gathered for the bundle | the rerank cases of `test_w1_21_merge.py` |

## Not written, waiting on a package

* DP-7: the declared check command run over the dev query set, green at the baselines and red below them. How
  the command finds the query set and where the baselines are recorded is not settled.
* DP-2: the default batch size; a merged set of more than 30 candidates from the semantic route (its `TOP_K` is
  30 and cannot be continued); "escalate" at R3 and above when the rounds run out.
* DP-8: content facets (decisions, code, tests, history, why) and a `--facet` option.
* DP-4: a supersession stated in prose only (b-dev `docs/adr/adr-003.md`), and a must-not-cite code file.

Also untested: `S0a-G-06`. It is among the ticket's sources and its text is in none of the places a worker may
read; no case is derived from it. The symbol side of the closure with the real code tool is W1-20's. The packet
ceiling itself is W1-24's; here only that the retrieval budget is not it.

## Earlier tests revised

`tests/acceptance/W1-07/w1_07_support.py`, on lines of its own after `READ_COMMANDS` ("planned: command
implemented", DEC-190): `retrieve` joins `BUILT_LATER` and leaves `NOT_BUILT`, and the cases that run every
command give it the question it requires. The W1-07 suite passes before the implementation (224 passed) because
a command that is not built ignores the argument.

## How the cases were checked without an implementation

A throwaway `retrieve` kept outside the worktree (removed with the session) met the 92 function cases and the 7
model-free dev-tier cases, and four faults put into it were each caught: no authority filter (11 cases red), the
budget reported as `SATURATED`, nothing put ahead, and expansion ignoring the budget. The command and check cases
could not be checked this way: both need a file inside the worktree.
