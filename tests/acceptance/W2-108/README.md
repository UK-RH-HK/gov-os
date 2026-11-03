# W2-108 acceptance tests: retrieval checks the stores' freshness once per run

Ticket `DAEO-zoex` (W2-108), profile STANDARD. Written by the independent test designer (MR-3, DEC-963) from the
ticket's KPI lines and its sources (DEC-969, DEC-968, DEC-966 item 4, DEC-860, DEC-424; P-W2-54-LOAD-1; DEC-342,
DEC-344, DEC-322, DEC-221), without reading the implementation. Proportion (DEC-221, STANDARD): every KPI line's
success and failure, and the key edge cases.

## How the suite chooses the code under test (DEC-732)

- The suite tests **the `gov` package that `PYTHONPATH` gives the pytest process**. `w2_108_support.GOV_SRC` is the
  folder holding that package (found with `importlib.util.find_spec("gov")`, never a hard-coded path); every
  child process gets that folder on its `PYTHONPATH`. Set it per command:

      PYTHONPATH=<worktree>/src python3 -m pytest tests/acceptance/W2-108 -q -p no:cacheprovider -o tmp_path_retention_policy=failed

  In the ticket's worktree: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-108/src`. Check first:
  `PYTHONPATH=<worktree>/src python3 -c "import gov; print(gov.__file__)"`.
- The single named files the planted repositories copy (the path map `governance/project/path-map.yaml` and the
  template's gitleaks rules `template/.gitleaks.toml`) are read from the worktree the tests run in.
- `TMPDIR` must name a writable folder: where it does not, pytest falls back to the current directory and leaves
  `pytest-of-<user>/` in the worktree.

## How the tests observe the behaviour

- **Public interfaces only:** `gov.retrieval.lexical.freshness`, `lexical.search(root, query, refresh=False)`,
  `lexical.refresh`, `gov.retrieval.semantic.search(root, query, refresh=False)`, `semantic.refresh`,
  `gov.retrieval.retrieve.retrieve` (with a stand-in reranker that does not rerank: the rerank is not under test),
  `gov.context.context`, and `gov.store.load` to build the record graph.
- **One process per scenario.** A driver written to a temporary folder runs a list of steps in one Python process:
  calls, and between them edits, removals, git commands, or another process that rebuilds the store.
- **What is counted (KPI 1).** The driver installs a Python audit hook (`sys.addaudithook`) and records, per call:
  - every `git` command the process starts. Counted as freshness work: `git ls-files` listing every tracked file,
    and `git hash-object` hashing their content. **Not counted:** a command that only asks whether anything
    changed (`git status`, `git diff-files`, `git rev-parse`, `ls-files` with `-m`, `-d`, `-o`, `-u` or `-k`),
    so an implementation may probe the tree on every call;
  - every `open` of the path map (`path-map.yaml`), from which the files that should be embedded are worked out.
    This is counted only on `semantic.search` calls: `retrieve` also reads the path map for its authority order
    (W2-87), which this ticket does not change.
- **No network.** The embedder is a stand-in for Ollama's HTTP interface on a loopback port (vectors made from
  words, the model reported wholly on the CPU). `HOME` is empty and `PATH` holds no `ollama`. `sqlite_vec` is
  linked into a folder of its own, as W1-19 does.
- **Planted repositories** are built from scratch in pytest's `tmp_path`: seven files in four namespaces (two
  embedded), the path map and the gitleaks rules. They are committed, or only staged for the "no commit yet" cases.

## KPI lines and their tests

| KPI line | Tests | Today, against `w2/integrate`'s code |
|---|---|---|
| 1. Once per store and tree; failure: a check repeated on every call | `test_w2_108_once.py`: `test_lexical_freshness_is_worked_out_once`, `test_lexical_search_checks_freshness_once`, `test_semantic_status_is_worked_out_once`, `test_retrieve_checks_both_stores_once`, `test_every_kind_of_call_shares_one_check`, `test_an_unchanged_tree_with_an_uncommitted_edit_is_checked_once`, `test_this_repositorys_store_is_checked_once` | **red** (all 7) |
| 2. Every answer unchanged; failure: any bundle, facet or stopping reason different | `test_w2_108_unchanged.py`: `test_planted_answers_are_unchanged`, `test_planted_continuation_is_unchanged`, `test_planted_unavailable_answers_are_unchanged`, `test_no_commit_answers_are_unchanged`, `test_this_repositorys_answers_are_unchanged`, `test_this_repositorys_semantic_answers_are_unchanged`, `test_this_repositorys_context_packet_is_unchanged` | green: guards, expected to stay green |
| 3. A change is still seen; failure: a stale answer reused | `test_w2_108_change_seen.py`: `test_a_file_changed_in_the_working_tree_is_seen[edited, deleted]`, `test_a_committed_change_is_seen`, `test_a_second_edit_of_an_edited_file_is_seen`, `test_a_store_rebuilt_by_another_process_is_seen[full-rebuild, index-and-vectors-only]`, `test_a_store_rebuilt_in_the_same_process_is_seen`, `test_a_moved_head_is_checked_afresh`, `test_a_removed_store_is_seen`, `test_without_a_head_every_call_checks` | green: guards, expected to stay green |
| 4. Measured; not done: W2-54's limits raised or its tests changed | `test_w2_108_scope.py`: `test_w2_54_is_not_changed_by_this_ticket`, `test_the_context_checks_limit_is_not_raised` (green guards); `test_the_research_record_names_the_measure` | the record check is **red** |

### The red reason of each red test, today

- `test_lexical_freshness_is_worked_out_once`, `test_lexical_search_checks_freshness_once`,
  `test_an_unchanged_tree_with_an_uncommitted_edit_is_checked_once`: every call after the first still runs
  `git ls-files -z` and `git hash-object --stdin-paths`: `[(2, 2), (3, 2), …]` (call number, commands).
- `test_semantic_status_is_worked_out_once`: every call after the first lists and hashes the tracked files again
  (2 commands) and reads the path map again (1 read).
- `test_retrieve_checks_both_stores_once`, `test_this_repositorys_store_is_checked_once`: every `retrieve` after the
  first runs the freshness check twice (once for the lexical facet, once inside the semantic status), so 4 commands.
- `test_every_kind_of_call_shares_one_check`: 8 mixed calls list the tracked files 10 times and hash them 10 times,
  against at most twice each (once for the lexical index, once for the vectors).
- `test_the_research_record_names_the_measure`: `docs/research/W2-108-freshness-once.md` does not exist yet.

### What the guards hold (KPI 2 and 3)

- **Unchanged answers:** each call made alone in a fresh process, where nothing can have been remembered, against
  the same call made after a warm-up, twice over, in one process. The comparison is the whole return value, item for
  item: the bundle, its evidence, facets, gaps, merge and stopping reason; a facet's hits; the freshness answer.
  It is made on a fresh store, on a store made stale by an uncommitted edit (unavailable facets), on a repository with
  no commit, for a paged question's continuation, and on this repository's store.
- **A change still seen** (each case first warms the process with several calls of every kind):
  - a tracked file edited or deleted in the working tree, uncommitted (DEC-344); a committed change; both facets
    report `stale`, and the bundle stops on `FACET_UNAVAILABLE`;
  - a **second edit of a file already edited** when the store was built: the set of changed paths is the same
    before and after, but the content is not;
  - the store **rebuilt by another process** with the tree and the head unchanged: in full (`gov.store.load`, then
    the index and the vectors), or with **only the index and the vectors refreshed**, which leaves the store's
    fingerprints row as it was; also the store refreshed **within the same process**;
  - the **head moved** with nothing else changed (an empty commit): the next calls check again (some listing,
    hashing or path-map read) and answer as before;
  - the **store removed**: `missing`, never the old answer;
  - **no commit yet** (the head cannot be read): every call checks, and an edit between two calls is seen.

## This repository's store

`test_this_repositorys_store_is_checked_once`, `test_this_repositorys_answers_are_unchanged`,
`test_this_repositorys_semantic_answers_are_unchanged` and `test_this_repositorys_context_packet_is_unchanged` read
the store of **the worktree the tests run in** (`<worktree>/.gov-runtime/store.db`). The lead rebuilds that store
(`gov rebuild`) before running them. `W2108_STORE_ROOT` may name another worktree whose store to read. These cases
only read the store; the one file a read writes is the query-vector cache beside it (DEC-782).

- **No store:** the four cases are skipped with the reason `no store at …`.
- **No embedder:** they run in the scratch environment (an empty `HOME`, nothing on `PATH` that could start an
  embedder), using the embedders this environment names in `OLLAMA_HOST` and `GOV_QUERY_OLLAMA_HOST`, else the
  defaults. Where none answers, the semantic facet is unavailable. The bundle, lexical and context cases still compare
  their answers, with that facet unavailable. `test_this_repositorys_semantic_answers_are_unchanged` is skipped with
  the facet's reason.

## Not done here

- W2-54's tests (`tests/acceptance/W2-54/`) are not touched, and its time limits are not raised (DEC-969).
- KPI 4's measure (the context check timed before and after, at two loads) is the engineer's research record. The
  suite checks only that the record exists and names the loads (two, one of them 40 or more), the freshness and
  embedding times in seconds, and the batching.

## Requirements

`gitleaks` on `PATH` (the lexical index judges every file with it) and `sqlite_vec` (the vectors). Without them,
the planted cases are skipped with the reason. Nothing is installed or downloaded.

## KPI map after D-4's cut (DEC-1061)

Regenerated at the cut (tier 2: each KPI line's own case kept first, then at most 6 functions per line;
a parametrised function keeps its first row in the full run unless it is a line's own case). The rest stay
built in the opt-in suite `lifted` (`tests/optin-lifted*.txt`), run report-only with `--optin=lifted`.

| KPI line | case(s) in the full run | placed by |
|---|---|---|
| S1: Within one process, the semantic store's status (which files should be embedded and whether the store holds them) and the lexical ind... | `test_w2_108_change_seen.py::test_a_store_rebuilt_by_another_process_is_seen`, `test_w2_108_once.py::test_lexical_freshness_is_worked_out_once` | by its words (every function of the suite kept) |
| S2: Every answer is unchanged: for the same store and tree, each retrieval call returns the same bundle, facets and stopping reason as be... | `test_w2_108_unchanged.py::test_planted_unavailable_answers_are_unchanged`, `test_w2_108_once.py::test_an_unchanged_tree_with_an_uncommitted_edit_is_checked_once` | by its words (every function of the suite kept) |
| S3: A change is still seen: a store rebuilt, a file changed or a head moved between two calls is seen as such (a new key, a fresh check);... | `test_w2_108_change_seen.py::test_without_a_head_every_call_checks`, `test_w2_108_change_seen.py::test_a_store_rebuilt_by_another_process_is_seen` | by its words (every function of the suite kept) |
| S4: Measured: `python3 -m gov.context.context_check` on one store, before and after, at the same measured load (two loads, one of them 40... | `test_w2_108_change_seen.py::test_a_second_edit_of_an_edited_file_is_seen`, `test_w2_108_once.py::test_lexical_search_checks_freshness_once` | by its words (every function of the suite kept) |
| F1: A freshness or status check repeated on every call within one process. | `test_w2_108_once.py::test_every_kind_of_call_shares_one_check`, `test_w2_108_once.py::test_an_unchanged_tree_with_an_uncommitted_edit_is_checked_once` | by its words (every function of the suite kept) |
| F2: Any bundle, facet or stopping reason different from before for the same store and tree. | `test_w2_108_unchanged.py::test_this_repositorys_semantic_answers_are_unchanged`, `test_w2_108_change_seen.py::test_a_second_edit_of_an_edited_file_is_seen` | by its words (every function of the suite kept) |
| F3: A stale answer reused after the store, a file or the head changed. | `test_w2_108_change_seen.py::test_a_second_edit_of_an_edited_file_is_seen`, `test_w2_108_change_seen.py::test_a_removed_store_is_seen` | by its words (every function of the suite kept) |
| F4: W2-54's time limits raised, or its tests changed. | `test_w2_108_change_seen.py::test_a_file_changed_in_the_working_tree_is_seen`, `test_w2_108_change_seen.py::test_a_second_edit_of_an_edited_file_is_seen` | by its words (every function of the suite kept) |
