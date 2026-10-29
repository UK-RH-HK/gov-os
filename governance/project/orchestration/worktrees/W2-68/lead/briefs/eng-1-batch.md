batch 1 of 3: the fingerprints, the store and its check

Build, as the design note states them (sections 1, 2, 5, and the settled points B and C):

1. **The two fingerprints of a commit** (new `src/gov/close/fingerprint.py`): the code fingerprint and the records fingerprint, read from git objects of that commit only; the test map's `record_only` list read from the commit, judged by the schema in the order of point B; the path map, the test map and the test-map schema always counted as code; "cannot be computed" as its own answer, never an empty list.
2. **The fingerprints a rebuild records** (`src/gov/store/**`): every load records one row (the head, its code fingerprint, its records fingerprint, the kind `rebuild`), kept out of the store's digest and out of the graph's tables (point C).
3. **The incremental record load** (`src/gov/store/**`): only when the store's row holds a code fingerprint equal to HEAD's (else `STORE_CODE_CHANGED`, exit 1); reloads the record graph from HEAD (every graph table, `commit_paths` included), refreshes the lexical index and the semantic vectors incrementally through their existing refresh functions, leaves the code index alone, and writes the row (kind `records`). It must leave the same store digest as a full load of that commit.
4. **The store-freshness check** (`src/gov/close/repo.py`, that check only): today's rule and, where the store has a row, its head is HEAD and both fingerprints equal HEAD's; where HEAD's fingerprints cannot be computed, the row must be a `rebuild` of HEAD; a store without a row is judged by today's rule alone.
5. **The `refresh` entry** of the batch's command line (new `src/gov/close/batch.py`, only its command-line frame and `refresh` in this batch): `python3 -m gov.close.batch refresh --root <project> --json`, the API-0002 envelope (as `gov.close.nightly`'s `main` gives it), exit 0 when the store is fresh at HEAD after the load, exit 1 with the `GovError`'s code otherwise.

Builder tests for each in `tests/unit/close/test_fingerprint*`, `tests/unit/store/test_fingerprint*` and `tests/unit/close/test_batch*`. The batch's `run`, reuse and the close's record lines are the next batch's: leave them out.
