# W2-126 acceptance tests: a machine-wide vector cache keyed by the text (DAEO-jpr0)

Written by the independent test designer (MR-3) from the ticket's KPI lines and sources (DEC-1032;
P1-LOAD-BALANCE-1 section a, levers b.1 and b.6; DEC-1031, DEC-1015, DEC-374), before the implementation, without
reading it. Behaviour through public interfaces only (DEC-462), in proportion to a STANDARD ticket (DEC-221).

## Run

    PYTHONPATH=<this worktree>/src python3 -m pytest tests/acceptance/W2-126 -q -p no:cacheprovider \
        -o tmp_path_retention_policy=failed -rs

17 cases (one of them `local_only`); about 40 s without the `local_only` case, about 2 minutes with it (measured on
the base).
Each needs `gitleaks` on `PATH` and an importable `sqlite_vec` (the lexical index and the vectors need them); a case
is skipped, named, where either is missing.

## How the suite finds the code under test

- `w2_126_support.SRC` is the `src/` of the repository the test file sits in (`Path(__file__).parents[3] / "src"`),
  never a fixed path and never an installed copy. Merged into the ticket's worktree, the suite exercises that
  worktree's code.
- Every call runs in a child process (a small driver written to the test's temporary folder) whose `PYTHONPATH` is
  that `src/` (plus a folder that links this machine's `sqlite_vec`). A session fixture asserts that `gov` imported
  with that `PYTHONPATH` comes from that `src/` (DEC-732).
- The public interfaces used: `gov.retrieval.semantic.refresh(root)`, `search(root, question, refresh=False)` and
  `query_vector(root, question)`; the store's plain `semantic_vector` and `semantic_manifest` tables
  (`.gov-runtime/store.db`, read read-only); the retrieval check as its declaration runs it,
  `python3 -m gov.retrieval.retrieve_check` in a project root with `GOV_DEV_TIERS` set.

## Never the real embedders, never the user's real cache

- **A stand-in embedder** (`StandIn`) on a free loopback port answers Ollama's protocol: `/api/version` (so the
  base's `ensure_available`/`ensure_query_available` find it healthy and start nothing), `/api/tags` (the model
  with a revision the case chooses, as its `digest`, DEC-374), `/api/ps` (the model wholly on the CPU, so the
  device rule decides no case) and `/api/embed`. It records every text it is sent with the vector it returned.
  Its vectors are float32-exact and a function of (revision, text), or, with `varying`, of the request too (so a
  vector served from the cache shows it was not computed again). It can hold one request open (`hold`).
- `OLLAMA_HOST` and `GOV_QUERY_OLLAMA_HOST` both name it; `PATH` holds no folder with an `ollama` in it (gitleaks is
  linked into a folder of its own); `HOME`, `XDG_CACHE_HOME` and `TMPDIR` are temporary folders of the test;
  `GOV_VECTOR_CACHE_DIR` names a temporary folder (one case leaves it out on purpose, with `HOME` and
  `XDG_CACHE_HOME` still temporary). No network beyond the loopback stand-in. Each server is stopped by its fixture.
- Every project is a temporary git repository planted from scratch under `tmp_path` (this repository's path map
  with the namespaces replaced, and the template's gitleaks rules: single named files), cloned with `git clone`
  where a case needs a clone.

## Interface the cases need

What the cases rely on, and nothing more (no module, function or table of the code to be written is named):

1. **Location setting: `GOV_VECTOR_CACHE_DIR`**: the folder that holds the machine-wide cache, created if absent.
   Default: a folder in the user's own folder (for example under `$XDG_CACHE_HOME`, else `~/.cache`: the cases
   only check that it is under `HOME` or `XDG_CACHE_HOME`). Once every process using it has ended, the folder
   holds **one file, the cache, of mode 0600**. Every tree and clone on the machine shares it. No switch to turn
   the cache off is needed: the "built without the cache" store is built with an empty cache folder of its own.
2. **Size-limit setting: `GOV_VECTOR_CACHE_MAX_BYTES`**: a whole number of bytes, the bound on the cache, measured
   as the size on disk of what the cache folder holds once a write has ended. Default: about two corpora, from the
   measured corpus (not tested). Past it, the least recently used entries (by lookup or store) go first.
3. **The result names the cache**: the dicts `semantic.refresh(root)` and `semantic.search(root, question, ...)`
   return carry a key `vector_cache` with
   - `hits`: the number of texts whose vector came from the cache in that call;
   - `misses`: the number of texts sent to the embedder in that call (and stored);
   - `skipped`: `None` when the cache was used; otherwise a non-empty string saying why it was skipped (unreadable,
     locked); the texts are then embedded and the call succeeds.
   `query_vector` keeps its `(vector, reason)` return; the cases only count what it sends.
4. The key is the model, the revision `/api/tags` reports (its `digest`) and the sha256 of the exact text sent
   (a chunk's first characters as sent; a question's text as sent). The cases see it only through what is sent.

## KPI lines and their tests, with the red reason on the base

The base has no machine-wide cache: a second tree re-sends its texts, there is no cache file, no setting is
honoured and the results do not name a cache. Seen on the base (`2a3c998fe786`), every case fails, each as below.

The map `gov accept DAEO-jpr0` reads (DEC-1042 item 3): the KPI column names each line as `gov accept` reads it,
`S<n>` for the ticket's success line n and `F<n>` for its failure line n; the test column holds only test names in
backticks, a parameterised case once per parameter (`name[id]`); notes on a case are in the third column.

| KPI | test | notes, and the red reason on the base |
|---|---|---|
| S1 | `test_w2_126_hits.py::test_a_second_tree_and_a_clone_send_nothing` | "a tree whose texts are all cached sent texts to the embedder" |
| S1, F1 | `test_w2_126_hits.py::test_a_changed_text_is_a_miss` | one letter's case changed; "texts already cached were sent again" |
| S1 | `test_w2_126_hits.py::test_a_question_from_two_trees_is_embedded_once` | "the question was embedded once per tree" (2 == 1) |
| S1 | `test_w2_126_hits.py::test_the_cache_is_one_file_of_mode_0600` | "the cache folder must hold one file, not []" |
| S1 | `test_w2_126_hits.py::test_by_default_the_cache_sits_in_the_users_own_folder` | "without the location setting, a second tree sent its texts again" |
| S2 | `test_w2_126_same_vector.py::test_a_cached_vector_is_the_one_the_embedder_returned` | varying stand-in; also the result's hits, misses and skipped; "a tree whose texts are all cached sent texts to the embedder" |
| S2, F2 | `test_w2_126_same_vector.py::test_an_all_cached_rebuild_gives_the_store_built_without_the_cache` | "the rebuild of an all-cached tree embedded texts" |
| S3, F1, F3 | `test_w2_126_writers.py::test_concurrent_rebuilds_and_searches_serve_only_right_vectors` | 4 processes; "texts every writer stored were sent again: a write was lost" |
| S3 | `test_w2_126_writers.py::test_no_lock_is_held_across_an_embedding_request` | one request held open; "the result does not name the vector cache ('vector_cache')" |
| S3, F3 | `test_w2_126_writers.py::test_an_unusable_cache_is_skipped_and_named[unreadable]`, `test_w2_126_writers.py::test_an_unusable_cache_is_skipped_and_named[locked]`, `test_w2_126_writers.py::test_an_unusable_cache_is_skipped_and_named[garbage]` | "the cache folder must hold one file, not []" (each) |
| S4 | `test_w2_126_bound.py::test_least_recently_used_entries_go_first` | 96 KiB bound, 1 KiB vectors; "the most recently used entry was evicted" (the base caches no question for a tree without a `.gov-runtime/` folder, so every ask is sent) |
| S4, F1 | `test_w2_126_bound.py::test_a_revision_change_is_a_new_key_space` | "the first revision's entries were lost when the revision changed" |
| S5 | `test_w2_126_dev_tiers.py::test_a_later_check_embeds_nothing` | a planted GOV_DEV_TIERS folder: two small tiers, four questions; "a later check embedded 60 texts cold" |
| S5 | `test_w2_126_dev_tiers.py::test_a_later_check_on_this_machines_dev_tiers_embeds_nothing` | marked local_only: this machine's dev tiers by GOV_DEV_TIERS's name, skipped where absent; "a later check embedded … texts cold" |
| S6 | `test_w2_126_evidence.py::test_the_evidence_file_states_the_named_figures` | light: the file exists and names the figures, never their values; "docs/changes/W2-126-evidence.md does not exist" |

Success line 7 (the bounded retry's cover of a transient server error, W2-123's case revised under
`Rewrite-Reason: P-W2-123-4`) is not in this map: DEC-1042 item 4 does it after W2-123 lands.

Failure lines: **F1** (a vector for a different text, model or revision): the changed-text, concurrent-writers and
revision cases. **F2** (a store built with the cache differs): the all-cached rebuild, the cached-vector case and
the unusable-cache cases (the store equals the one built from the embedder). **F3** (a rebuild or search fails
because of the cache): the concurrent-writers, held-request and unusable-cache cases (every call must succeed).

## Notes

- **A model change** cannot be made through a public interface (the model is pinned in the code); the revision
  change stands for "a new key space" (KPI 4). The key's other parts are seen only through what is sent.
- **The bound's default** (about two corpora) and KPI 6's figures are values for the evidence and the audit, not
  tested.
- **"Locked"** is made by holding both a `flock` and a POSIX record lock over the whole cache file from the test
  process, so whatever whole-file lock the cache takes is taken already; a cache that waits on it must still end
  the call within the driver's limit (300 s).
- **"Garbage"** (the file overwritten with other bytes) must not fail a rebuild or a search, and must not give
  wrong vectors; whether it is skipped (named) or replaced is the engineer's choice and is not tested.
- **The root conftest's per-test cache folder** (W2-126's own fixture, DEC-1042 item 1) sets `GOV_VECTOR_CACHE_DIR`
  in the pytest process only. No case here reads it: every child process gets an environment built from scratch
  (`Box.env`: only `PATH` is taken from the pytest process), naming the case's own folder, or, in the
  default-location case (`use_setting=False`), no `GOV_VECTOR_CACHE_DIR` at all, so that case sees the default
  under its temporary `HOME` and `XDG_CACHE_HOME` whatever the pytest process holds.
- **The user's own folder** already holds what the base writes there besides the cache (its secrets scan, under
  `~/.cache/gov-os/`): the default-location case counts only what appears once the location setting is left out.
- **Lever b.6 through public interfaces**: the retrieval check clones the tiers into a new temporary folder on
  every run, so a later run that sends nothing shows that the tiers' chunks and questions came from the machine-wide
  cache. The `local_only` case uses this machine's tiers only by `GOV_DEV_TIERS`'s name (default
  `~/gov-os-workbench/synthetic`) and checks only that a named file exists there; the check itself clones them into
  the test's temporary folder.
