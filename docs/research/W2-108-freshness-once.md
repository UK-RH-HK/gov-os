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

Measured by the lead, outside the sandbox, on 2026-10-31: pairs 1 to 3 from 10:04 to 12:01 GMT, and pair 4 from
12:41 to 13:39 GMT.

**How.** One store: a scratch clone of this branch at the ticket's base `f6af39c1665b`, rebuilt once in full
(`gov rebuild --json`, exit 0) and used unchanged by every run. Only the code under test changed: "before" is the
base's `src/` (`f6af39c1665b`), "after" is this branch's `src/` at `ee5056be590a`. Each run was
`python3 -m cProfile -o <file> -m gov.context.context_check` in the clone's root. The query-vector cache was
deleted before each run, so every run embedded the same questions cold (97 embedder calls a run). The runs went in
four back-to-back pairs, in this order: before then after; after then before; before then after; before then after.
That was meant to give the two runs of a pair about the same load. The 1-minute load was sampled every 15 s. The
machine has 20 processors, and the load is whatever the other sessions made: it was not controlled.

- *Freshness and status* is cProfile's cumulative time in `semantic._status`, plus the time in `lexical.freshness`
  when it was not called from `_status`.
- *Query embedding* is the cumulative time in `semantic.query_vector`.
- *Wall* includes cProfile's own overhead, which this measure does not separate out.

**Figures.** Every run's verdict was `context-reproducibility: green`, exit 0, with 336 retrieval calls and 97
embedder calls. The 5-minute load mean was given for pair 4 only.

| Pair | Run | Code | Wall (s) | 1-min load, mean (min–max) | Samples at load ≥ 40 | 5-min load mean | Freshness and status (s) | Query embedding (s) |
|---|---|---|---|---|---|---|---|---|
| 1 | before-1 | base | 1,141 | 34.0 (16.1–45.8) | 19 of 69 | — | 360.0 | 259.3 |
| 1 | after-1 | W2-108 | 940 | 36.2 (17.0–46.8) | 23 of 57 | — | 17.0 | 372.9 |
| 2 | after-2 | W2-108 | 406 | 19.6 (12.5–26.5) | 0 of 25 | — | 10.9 | 33.7 |
| 2 | before-2 | base | 876 | 22.6 (9.8–40.3) | 2 of 53 | — | 291.6 | 161.0 |
| 3 | before-3 | base | 625 | 12.6 (0.1–38.7) | 0 of 38 | — | 230.6 | 67.5 |
| 3 | after-3 | W2-108 | 300 | 10.1 (8.0–20.3) | 0 of 19 | — | 8.7 | 6.9 |
| 4 | before-4 | base | 2,414 | 63.4 (18.6–106.0) | 133 of 145 | 64.6 | 611.4 | 894.4 |
| 4 | after-4 | W2-108 | 1,063 | 48.0 (18.2–77.7) | 38 of 64 | 48.4 | 18.2 | 451.4 |

The call counts from the profiles of pairs 1 to 3, the same in every run of each code (pair 4's were not given):

| | `lexical._tracked` | `semantic._wanted` | `semantic.embedded` | `lexical._checked` |
|---|---|---|---|---|
| Before | 672 | 336 | 17,615,472 | (not in the base) |
| After | 1 | 1 | 52,427 | 672, 10.4 to 16.3 s in all, mostly the stat sweep `_stamps` |

**The load.** KPI 4 asks for a before and an after run at the same measured load, at two loads, one of them 40 or
more.

- **Pairs 1 to 3 never reached it.** None of their six runs had a mean of 40. The highest was pair 1: means of 34.0
  and 36.2, peaks of 45.8 and 46.8, about a third of its samples at 40 or more. The load then fell. A wait for a load of 40 or
  more, from 11:00 to 11:46, saw it fall to 0.2 instead.
- **Pair 4 did.** Once the load rose again, both of its runs had a mean above 40: 63.4 and 48.0 (5-minute means of
  64.6 and 48.4), with 133 of 145 and 38 of 64 samples at 40 or more.
- **But pair 4's two runs did not see the same load.** The load fell during it, from 82 at 12:40 to about 30 at
  13:21. The "after" run had a mean about 15 lower than the "before" run.

So the eight runs cover four mean loads: about 10 and 20 (pairs 3 and 2), about 35 (pair 1), and 48 to 63 (pair 4).
The load of 40 or more is now measured, but the before and after runs at that load are further apart in load than
in the other pairs.

The package's profile (1,252 s at load 40 to 70, P-W2-54-LOAD-1) was taken on another store, under cProfile and at
another load. It is not one of these runs and is not compared with them here.

**What the figures show.**

- **The checks are now worked out once, as KPI 1 asks.** In pairs 1 to 3, `_tracked` and `_wanted` fell from 672
  and 336 calls a run to 1 each, and `embedded` fell from 17.6 million calls to 52,427.
- **The time in the freshness checks fell from 231–611 s to 9–18 s a run.** That is a 21- to 34-fold cut within each
  pair, and the cut was largest at the highest load (611.4 s to 18.2 s in pair 4). In pair 4 the "after" run had
  the lighter load, but the base's lightest run of all (230.6 s at a mean of 12.6) still spent almost 13 times as
  long in these checks as after-4 did at 48, so the load does not account for the cut. What is left is about the
  cost of the per-call stat sweep. `_checked` runs twice per retrieval call (once from the lexical search, once from
  `semantic._status`), 672 times in all, for 10.4 to 16.3 s in pairs 1 to 3.
- **The wall time fell in every pair:** by 201 s in pair 1 (1,141 to 940), 470 s in pair 2 (876 to 406), 325 s in
  pair 3 (625 to 300) and 1,351 s in pair 4 (2,414 to 1,063). Not all of each difference is this change, for two
  reasons:
  - The two runs of a pair did not see the same load. The "after" run was the lighter one in pairs 2, 3 and 4 (by
    about 15 in pair 4), and the heavier one in pair 1.
  - Query embedding swings widely with load: 6.9 to 894.4 s across the eight runs, for the same 97 calls. Within a
    pair it differs by 114 s in pair 1, 127 s in pair 2 and 443 s in pair 4.

  Only the freshness-and-status figures compare cleanly across a pair. The rest of each wall-time saving, pair 4's
  above all, mixes the change with the load.
- **Against W2-54's 600 s limit:** "after" was under it at mean loads of about 10 and 20 (300 s and 406 s). It was
  over it at a mean of 36 (940 s) and at a mean of 48 (1,063 s). "Before" was over it in all four pairs, including
  the lightest (625 s at a mean of 12.6). These wall times include cProfile's overhead, and W2-54's tests time the
  check without cProfile, so the same runs unprofiled would likely be somewhat shorter. This measure does not say by
  how much.

**Verdict on the query-embedding batching (the package's option (b)), reviewed against all eight runs.** Batching
is not needed at the lighter loads. At the two heavier loads it is not enough: alone it cannot bring the profiled
check under 600 s.

- **At the lighter loads (means of about 10 and 20) it is not needed.** The check already finishes under 600 s
  without it, at 300 s and 406 s. There, query embedding takes 6.9 s and 33.7 s, 2 % and 8 % of the run.
- **At a mean of 36 (after-1) it would not be enough on its own.** Query embedding is the largest single part of
  after-1, at 372.9 of 940 s (40 %). But the run without any of its embedding time would still last 567 s
  (940 − 372.9). To bring after-1 under 600 s, batching would have to cut the embedding from 373 s to under 33 s at
  that load. The questions still have to be embedded, and these figures do not show batching doing that.
- **At a mean of 48 (after-4) it could not be enough even in the limit.** Query embedding is again the largest
  single part, at 451.4 of 1,063 s (42 %). But the run without any of its embedding time would still last 612 s
  (1,063 − 451.4), which is over 600 s. Even a batching that removed every second of query embedding would leave
  this run over W2-54's limit, under cProfile.
- **The larger cost at both heavier loads is the rest of the run,** outside the freshness checks and query
  embedding: 550 s in after-1 and 593 s in after-4. This measure does not break that rest down, so it does not show
  where the next saving lies.

So the figures say two things about option (b):

- Batching could still shorten the check at a heavy load, since query embedding is 40 to 42 % of the "after" runs
  there. The figures do not show how much it would save.
- It is not what would bring the check under 600 s at a mean load of 36 or more. At 48, nothing taken out of query
  embedding alone can do that.

Whether W2-54's limit is met at a heavy load therefore rests on the rest of the run, which this measure does not
attribute, and possibly on cProfile's overhead, which it does not separate out.

The decision on option (b) is the owner's (DEC-969). The orchestrator brings it from this record.
