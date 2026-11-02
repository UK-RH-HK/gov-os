# W2-126 evidence: the machine-wide vector cache (DAEO-jpr0; DEC-1032, DEC-1039)

Each text is embedded once on the machine, whatever tree, clone or code asks. A chunk's or a question's vector depends
only on the model, its revision and the exact text sent, not on the `gov` code, so one cache keyed by those three,
shared by every tree and clone, replaces the cold embedding of every new worktree, clone, close and `gov check`.

## The design

- **Where:** `src/gov/retrieval/vector_cache.py` (new), used by `src/gov/retrieval/semantic.py`. One SQLite file,
  `vectors.db`, in `GOV_VECTOR_CACHE_DIR`; by default `$XDG_CACHE_HOME/gov-os/vector-cache/vectors.db`, else
  `~/.cache/gov-os/vector-cache/vectors.db` (this machine: `/home/usain/.cache/gov-os/vector-cache/vectors.db`). The
  file is created with mode 0600 (`os.open(..., O_CREAT | O_EXCL, 0o600)`) in a folder of mode 0700; SQLite gives its
  WAL and shared-memory files the same mode and removes them when the last connection closes, so at rest it is one
  file.
- **The key:** the model's name, the digest the model list (`/api/tags`) reports for it (its revision, DEC-374) and
  the sha256 of the exact text sent (UTF-8): a chunk's first `EMBED_CHARS` characters; a question's text with its
  instruction (`INSTRUCTION + query`). Another model or revision is another key space: a lookup names all three, so no
  other model's or revision's vector is ever served. Without a revision there is no key and the cache is skipped.
- **The value:** the vector's bytes exactly as `_embed` packed what the embedder returned (float32), with their
  sha256. A row whose bytes do not hash to it, or are not whole float32 numbers (empty, a length not a multiple of 4),
  is a miss, never a vector; the next store replaces it.
- **The flow (no lock across a request):** per batch of `BATCH` chunks, the stage opens the cache, looks every text
  up, records the hits' last use, and closes it; it then sends only the misses to the embedder, with no cache
  connection open; then it opens the cache again and stores the new vectors in one short `BEGIN IMMEDIATE`
  transaction. `query_vector` looks up the machine-wide cache first, then the tree's own device-keyed cache
  (DEC-782, unchanged), then embeds; a vector it embeds goes to both, and one from the tree's cache is copied to the
  machine-wide one.
- **Many writers:** WAL mode, so readers never wait for a writer and a writer never waits for readers; a 2 s busy
  timeout (`BUSY_S`) on every connection; `INSERT OR IGNORE` on the unique key, so two writers storing the same text
  keep the first vector (each is one the embedder returned for that model, revision and text) and a lost race is
  never read as a vector; every write is one transaction, so a crash leaves none half-written.
- **Skipped, never a failure:** a cache that cannot be opened, read or written (unreadable, not a database, a folder,
  locked past the busy timeout) is skipped for the rest of that run: its texts are embedded, `skipped` names why, and
  nothing raises. A failed last-use update keeps the hits (the run stops updating last use). So a locked cache costs at
  most one busy timeout per run, not one per batch.
- **Bounded:** `GOV_VECTOR_CACHE_MAX_BYTES` (default 512 MiB, `BOUND`) bounds the file's pages. A store that goes past
  it deletes the least recently used entries (last use kept in a small table of its own, `vector_use`, so a hit
  rewrites no vector) in the same transaction, then returns the freed pages to the file system
  (`auto_vacuum = INCREMENTAL`, `PRAGMA incremental_vacuum`). The default: a real entry (1,024 float32 numbers, the
  key, the hash) measured at 4,841 bytes on disk (5,000 entries) and 4,839 bytes (12,412 entries); two corpora of
  about 54,000 texts are about 523 MB, so 512 MiB (536,870,912 bytes) holds about 110,900 entries, about 2.05 corpora.
- **Named in the results:** `semantic.refresh` and `semantic.search` carry `vector_cache`:
  `{"hits": <texts served from the cache>, "misses": <texts sent to the embedder>, "skipped": null | "<why>"}`; a
  search with `refresh` counts its rebuild's chunks and its question together. As the CTO decided on the lead's T2
  (P3, (a)), the naming is in the semantic results only, not in `gov rebuild --json`.

## The KPI lines and how each is met

| KPI | How it is met | Tests |
|---|---|---|
| success-1: the lookup before every embedding, keyed by model, revision and sha256 of the text; a hit sends nothing; one file, 0600, in the user's folder, shared by every tree | `_build` and `query_vector` call `Cache.get` before `_embed`; only misses are sent; `vector_cache.location()` | acceptance `test_w2_126_hits.py` (5); unit `test_a_second_tree_sends_nothing_and_its_store_is_the_same`, `test_a_question_is_embedded_once_across_trees_and_named_in_the_search`, `test_the_cache_is_one_file_of_mode_0600`, `test_the_default_place_is_the_users_cache_folder`, `test_the_key_is_the_model_the_revision_and_the_exact_text` |
| success-2: the same vector, byte for byte; an all-cached rebuild embeds nothing and gives the same store | the bytes stored are those `_embed` returned, checked by their sha256 on every read | acceptance `test_w2_126_same_vector.py` (2); unit `test_an_all_cached_store_equals_one_built_without_the_cache`, `test_an_entry_whose_bytes_do_not_match_is_a_miss_and_is_replaced` |
| success-3: many writers, no corrupt entry, no lost write read as a vector, no lock across a request; an unusable cache skipped and named | WAL, busy timeout, one transaction per store, connections closed before `_embed`; `skipped` names the reason | acceptance `test_w2_126_writers.py` (5); unit `test_concurrent_writers_never_corrupt_or_serve_a_wrong_vector` (6 processes), `test_an_unusable_cache_is_skipped_and_named_never_a_failure` (3), `test_a_locked_cache_is_skipped_quickly_for_the_rest_of_the_run` |
| success-4: bounded, least recently used first; a model or revision change a new key space | `_evict` in the store's transaction; the key names model and revision | acceptance `test_w2_126_bound.py` (2); unit `test_the_bound_evicts_the_least_recently_used_first`, `test_a_revision_change_is_a_new_key_space` |
| success-5: the retrieval check's dev tiers and their 52 questions embedded once on the machine | `retrieve_check` builds each dev tier through `semantic.refresh` and asks each question through `semantic.search`, so both go through the cache with no change of their own; a later `gov check` finds every chunk and question cached | acceptance `test_w2_126_dev_tiers.py` (2) |
| success-6: measured, in this file | the figures below | acceptance `test_w2_126_evidence.py` |
| success-7: the bounded retry (W2-123, DEC-1026) also on HTTP 5xx and a reset or refused connection | **not in this tree:** W2-123's retry has not landed on `w2/integrate` (this branch has no `RETRY_WAITS_S`); extending it here would fork W2-123's change to `semantic.py`. Left for after W2-123 lands (see the return) | none here |

## The measured figures

Measured on a small planted tree with a stand-in embedder (in-process `_ask`, 1,024 float32 numbers per text; never
the real servers), by a script outside the tree that calls `semantic.refresh` on each planted tree: 400 Python files, 12,400 chunks, a code-changing ticket editing 12
files (12 chunks). "Before" gives every rebuild a fresh empty cache folder (the old behaviour: nothing shared);
"after" one shared cache folder.

| Rebuild | Texts sent before | Texts sent after | Cache counts after (hits / misses / skipped) |
|---|---|---|---|
| the integration tree (the cache's first fill) | 12,400 | 12,400 | 0 / 12,400 / none |
| a lead's first rebuild of a code-changing ticket (a fresh worktree) | 12,400 | 12 | 12,388 / 12 / none |
| a close's clone of that ticket | 12,400 | 0 | 12,400 / 0 / none |
| the nightly (the base again) | 12,400 | 0 | 12,400 / 0 / none |
| **all four** | **49,600** | **12,412** (the distinct texts, each once) | |

- **The cache's size:** 60,063,744 bytes for those 12,412 entries (4,839 bytes each). On the real corpus of about
  54,000 texts, one corpus is about 261 MB; the default bound (512 MiB) holds about two.
- **Texts sent to the embedder per day, before and after:** before, about 503,000 texts in 13 hours on 2026-11-01/02
  (nine full copies of the corpus of about 54,000, from cold worktrees, clones, closes and checks). After, every copy
  after the first is answered from the cache, as the table shows: a day sends the corpus once at most (about 54,000,
  only when the model or its revision changes or the cache was emptied) plus the texts the day's tickets changed
  (12 of 12,400 in the planted ticket). So the target, under one corpus (about 54,000) a day against about 503,000 in
  13 hours, is met by construction once the cache is warm; the machine's own figure per day comes from the shared
  embedder's log after this lands (a measure, not made here: the freeze forbids touching the shared servers).
- **The retrieval check:** each later `gov check` sends none of the dev tiers' chunks and none of the 52 questions
  (acceptance `test_w2_126_dev_tiers.py`); before, every check embedded both tiers cold.

## Test results (head `b32fdb80f5fc`, through the confined gate)

- `gov accept DAEO-jpr0`: **pass, 17/17**; every mapped line passes (success-1 to success-6, failure-1 to failure-3).
- Builder tests: `tests/unit/retrieval/test_w2_126_vector_cache.py` 14/14. Each test now has its own
  `GOV_VECTOR_CACHE_DIR` (`tests/conftest.py`, DEC-1042), so no test is served another's stand-in vectors and none
  writes the user's own cache; the five builder files that embed in-process pass (76 cases), two of them revised to the
  behaviour in force (`test_semantic_query_vector.py`, `test_w2_108_freshness_once.py`).
- The scoped set at `fa137d75b86f`: 4,647 passed, 42 failed, 26 errors, 9 skipped; none in `tests/unit`. The reds:
  - **Not caused by this change:**
    - W1-19 (22) and W2-108 (20 errors): their fixtures need gitleaks (`FileNotFoundError: 'gitleaks'` in the
      lexical refresh). They run only in the nightly under DEC-1045.
    - W2-59 (4): the test project's `.claude/hooks/pretooluse.py` is missing. These four are red on the 2026-11-02
      nightly's baseline (known).
  - **W2-54 (22):** rerun after the test designer's revision (DEC-1042), below.
- `tests/acceptance/W2-54/` with `-m "not local_only and not shared_gpu"`, after the merge: 99 passed, 3 failed.
  - `test_w2_54_green_here.py::test_gov_check_gives_context_reproducibility_green_here` and
    `test_w2_54_time_limit.py::test_the_check_run_as_declared_on_this_repository_ends_green_within_its_limit`:
    `gov check` on this worktree reads its store, which predates the merge ("DAEO-1vka: … the store holds no record
    of … the store was loaded before it"). The worktree's store is stale; this change does not cause it.
  - `test_w2_54_query_cache.py::test_one_ticket_gets_one_packet_hash_whatever_the_cache_s_state`: **caused by this
    change.** Its premise ("the context left no cache file to make read-only") expects `gov context` to leave the
    tree's query-vector file. With the machine-wide cache, a question it already holds is served from there, and
    nothing is written in the tree.

## Limits

- The WAL file can hold up to about 4 MiB (`journal_size_limit`) beyond the bound while connections are open.
- A file that is not a database stays skipped until removed (the cache never deletes a file it cannot read); its
  reason names the file.
- On the GPU, a vector can depend on the prompt computed just before it (DEC-773); the cache keeps the first vector
  stored for a text, so later rebuilds reproduce it exactly (P-W2-123-2) instead of drifting.
