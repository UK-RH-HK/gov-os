# W2-108: retrieval checks the stores' freshness once per run

Ticket `DAEO-zoex` (W2-108), a follow-up of W2-54 (`DAEO-0rfi`, closed). Basis: P-W2-54-LOAD-1 (a), DEC-969. The
time limits of W2-54 are not raised and its tests are not changed.

## 1. The problem (P-W2-54-LOAD-1, measured 2026-10-31, load 40 to 70)

`python3 -m gov.context.context_check` made 328 retrieval calls in 1,252 s. About 460 s of that was two checks
repeated on every call, though neither answer can change within the run:

- `semantic._status`: 315 s over 328 calls; inside it `_wanted` judged every chunk against the path map (about 17
  million calls to `embedded()`, 228 s).
- `lexical.freshness`: 148 s over 656 calls, each hashing every tracked file (`git hash-object --stdin-paths`; about
  0.28 s on this repository's 2,601 files at low load).

## 2. The design

Both answers are remembered for the life of the process, one entry per project root (its resolved path), with the
key it was worked out under. A call works out the key first; it reuses the remembered answer only when the key is
equal to the one remembered, and otherwise works the answer out again and remembers it under the new key. The key
is taken **before** the answer is worked out, so a change made while the answer is computed gives a different key
at the next call.

**A stamp** (`lexical._stamps`) is a file's device, inode, size, modification time and change time, in nanoseconds.
Any write changes the times; a replacement (a store rebuilt by a rename) changes the inode. An absent file has the
stamp `None`, so its appearance is a change too.

| Answer | Key | Where |
|---|---|---|
| Lexical freshness (`freshness`, through `_checked`) | the store's fingerprint (the stamps of `store.db`, `store.db-wal`, `store.db-journal`) and the tree's: `HEAD` and the git index's stamp (one `git rev-parse HEAD --git-path index`), the tracked paths and the stamp of each tracked file in the working tree | `lexical._FRESHNESS` |
| The tracked paths (`git ls-files -z`, raw) | `HEAD` and the git index's stamp: listed again only when either changed | `lexical._LISTED` |
| Vectors' status (`semantic._status`) | the lexical key above (store and tree, taken in the same call) and the stamps of the configuration `_wanted` reads (`governance/project/path-map.yaml`, every file of `KNOWN_FILES`) | `semantic._STATUS` |

`semantic._status` asks `lexical._checked` first on every call, which gives the lexical answer and its key together,
so one call takes one stat sweep, not two. So a later call on an unchanged store and tree runs one `git rev-parse`
and no listing or hashing git command. The first call lists the tracked files twice (once for the key, once in
`_tracked` for the hashes; `_tracked` is left as it is, since the refresh uses it too) and hashes them once. The rest
of the two modules (the searches, the embedder's client, the query-vector cache, fusion) is unchanged.

### Why each change is seen (KPI 3)

- **A store rebuilt or written** (a refresh, a rebuild, a deletion): its file's times, size or inode change, or the
  write-ahead log or journal appears: a new store fingerprint, a fresh check of both answers. The query-vector cache
  is a file of its own beside the store (DEC-782), so a search's write to it changes no key.
- **A tracked file changed, committed or not** (DEC-344: the index reads the working tree): its stamp changes, so
  the tree's key changes without hashing any file. A file added to or removed from the index rewrites the index,
  so its stamp changes, the paths are listed again and the new list is in the key. This costs one short git call
  and one `stat` per tracked file on each call: on this worktree's 2,601 files, at load 40 to 53, the earlier form
  (two git calls and the stats) took 24 to 80 ms per call against 222 to 556 ms for hashing them (the paths are
  joined as bytes, since a `Path` per file cost three times its `stat`). Over the check's 328 calls that is at most
  about 8 to 26 s left, a residual the measure will show (§4).
- **The head moved**: `HEAD`'s commit is in the tree's key, and so in the vectors' key: both are checked afresh.
- **The path map changed**, even where it is not tracked: its stamp is in the status key.

### When a key cannot be read: check every time (never fail open)

The key is `None`, and the answer is worked out afresh on that call and never reused, when:

- `git rev-parse HEAD --git-path index` or `git ls-files` fails (no head, an unborn branch, not a repository), or
  the first does not give the two lines;
- a file's stamp cannot be read for any reason other than its absence (for example permission refused);
- a stamp is **too recent to trust**: a file changed less than `RACY_NS` (10 ms) ago, or later than the clock's now.
  On a filesystem with coarse times, a second write within one tick could leave the same stamp; a file that recent
  is therefore checked again at each call until the window has passed. On this machine (kernel 6.18, ext4) two
  same-size writes in a row, with a `stat` between them, gave distinct times in 2,000 of 2,000 tries (the smallest
  gap 54 µs), so the window is a margin, not the main guard.

An error raised by the check itself (a git failure inside `_tracked`, a store that cannot be opened) is raised as
before and nothing is remembered.

### Residuals (DEC-135: recorded, no code)

- Settings outside the tracked tree that change `git hash-object`'s result for an unchanged file (`.git/config`
  filters, `.git/info/attributes`) are not in the key. A tracked `.gitattributes` is.
- A write that keeps a file's inode, size and both nanosecond times is not seen; the window above covers the
  coarse-clock case.
- A process that changes `lexical.indexable`'s or the path map's code (not their files) while it runs, as a test's
  stand-in can, is not seen; within the context check, nothing does.

## 3. Evidence: the builder tests

`tests/unit/retrieval/test_w2_108_freshness_once.py` (regression evidence, DEC-136), on planted repositories in
`tmp_path`, with a stand-in endpoint and a Python `vec_distance_cosine` (no network, no `sqlite_vec`). A check is
counted by the calls to `lexical._tracked` and `semantic._wanted`.

- Six rounds of the semantic search, the lexical search and both statuses: one check of each (the tracked files
  listed twice and hashed once, all in the first round), and every answer equal to the first and to the answer
  worked out with nothing remembered.
- A store deleted and rebuilt, a tracked file edited to the same size and not committed (seen at once and after the
  window, then not checked again while it stands), a new file added to the index and not committed, a head moved
  by an empty commit (both checks afresh), an untracked path map changed: each seen, with a fresh check.
- An unborn branch (no head) and an unreadable store fingerprint: a check on every call.
- A stamp written inside the window gives no key; an absent file's stamp is `None`.

## 4. Measure

*To be filled in from the lead's measure:* `python3 -m gov.context.context_check` on one rebuilt store, before and
after, at two measured loads (one of them 40 or more), with cProfile's time in the freshness checks
(`semantic._status`, `lexical.freshness`) and in query embedding.

| Load | Before (s) | After (s) | Freshness checks, before / after (s) | Query embedding (s) |
|---|---|---|---|---|
| | | | | |
| | | | | |

**Verdict on the query-embedding batching:** to be written from the figures (target: under W2-54's 600 s limit at
ordinary load; DEC-969, DEC-968 item 3).
