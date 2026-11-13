---
type: probe
task: DAEO-jpr0
reviewer_session: agent-a84fd077e9f150872 (subagent of CTO session debdb3f7-879f-4f53-8ef5-ba7d562eaef2)
implementer_session: agent-ae4c0d11fdfeee5c5 (subagent of CTO session debdb3f7-879f-4f53-8ef5-ba7d562eaef2)
reviewer_wrote_nothing: true
commissioned_by: orchestrator
judged_by: orchestrator
judgement: pass
probed_commit: 4b3721a8f055c76c84cf3b44a244067843058ab9
---

# PR-DAEO-jpr0: independent review of W2-126, the machine-wide vector cache

- **Ticket:** DAEO-jpr0 (W2-126, STANDARD). **Branch:** `w2/W2-126` at `4b3721a8f055`, in `/home/usain/gov-os-worktrees/W2-126`.
- **Reviewer:** a fresh read-only session (independent reviewer, the emergency's rules, `EMG-common.md`; judgement by
  `governance/project/briefs/JUDGEMENT.md`). It wrote none of the files it reviews. No gitleaks scan (DEC-1045).
- **Read:** `git diff w2/integrate...w2/W2-126 -- src tests/conftest.py tests/unit docs/changes`; the ticket's KPIs;
  DEC-1032, DEC-1033, DEC-1042; the engineer's brief; the wide-scoped fixtures of the suites that embed (W1-17,
  W1-21, W2-54, W2-108) for the conftest question.
- **Probes (this session, its scratch folder, never the real cache):** a cache of 10,000 entries of 1,024 float32
  numbers built through `vector_cache.Cache`; then planted rows. The user's real cache was only read, opened with
  SQLite's `immutable=1` (no lock, no write).
- **Tests (once, through the gate, this tree's `src`):** `test_w2_126_vector_cache.py`,
  `test_semantic_query_vector.py`, `test_w2_108_freshness_once.py` and `tests/acceptance/W2-126`: **63 passed** in
  140 s, exit 0.

## Answers to the brief's questions

1. **A wrong vector in ordinary work?** No. The key is (model, the `/api/tags` digest of the host that embeds,
   sha256 of the exact text sent: a chunk's first `EMBED_CHARS` characters, a question's `INSTRUCTION + query`); a
   lookup names all three; a row is used only if its bytes hash to the stored sha256 and are whole float32 numbers;
   another model or revision is another key space. Chunk and question texts cannot collide (the instruction prefix).
   Every write is one SQLite transaction, so a torn row cannot be read; a garbage or corrupt file raises
   `sqlite3.DatabaseError`, caught, a miss. A wrong vector needs another program writing the file or page-level
   corruption (F4). The real cache holds 1,172 rows, all `qwen3-embedding:0.6b` at the real digest `ac6da0dfba84…621d`,
   all 4,096 bytes, WAL mode, auto_vacuum incremental: no test's stand-in vector has reached it.
2. **Concurrent writers?** No corruption and no lost write read as a vector: WAL, `BEGIN IMMEDIATE`, `INSERT OR
   IGNORE` on the unique key (the first of two equal-key vectors kept), no connection held across `_embed`. A rebuild
   is never blocked for long: the longest wait is the 2 s busy timeout, once per run. But one such timeout turns the
   cache off for the rest of that run (F1); the eviction that every store does at the bound scans the whole table
   inside the write lock (F2), measured small (a store at the bound: 20-36 ms at 30,000 entries). Nothing a rebuild did is lost: vectors are stored before
   the store's insert, so a rebuild that stops later leaves them for the next.
3. **An unusable cache?** A miss, named in `skipped`, never an error: `OSError` and `sqlite3.Error` are caught around
   every open, read and write (unreadable, a folder in its place, not a database, locked past the timeout, a full
   disk: `SQLITE_FULL` is a `sqlite3.Error`). The one escape needs a foreign row (a text value in `embedding`:
   `TypeError`, F4).
4. **The bound?** Kept: the eviction runs in the store's own transaction until the file's pages fit, least recently
   used first, and incremental vacuum returns the pages (the probe: auto_vacuum 2, WAL; 4,738 B per entry). The WAL
   (up to about 4 MiB) is outside the bound, as the evidence says.
5. **The root conftest fixture?** It isolates every test function and every subprocess that inherits the
   environment, under the run's base folder, and hides no defect: sharing across tests would only serve one
   stand-in's vectors to another stand-in. Its limit: it is function-scoped, so a module- or session-scoped fixture
   runs before it (F5); today's wide-scoped embedding fixtures all give their own `HOME` or folder.
6. **The revised builder tests?** Faithful. The three tree-cache cases in `test_semantic_query_vector.py` make the
   machine-wide cache unusable because their subject is the tree's own cache or no cache at all; their assertions are
   unchanged; a new case asserts the behaviour in force (a tree whose own cache is gone, and another tree, get the
   same bytes with one request). `test_w2_108_freshness_once.py` drops only the `vector_cache` counts from the
   compared answer, which legitimately change from a miss to a hit; the answer itself is still compared.

## Findings

### F1: one busy timeout turns the cache off for the rest of the run (KPI success-3)
`Cache._skip` sets `usable = False` on any failed open, read or store; every later batch of that run is a miss and is
embedded. A rebuild of 54,000 chunks whose third store waits more than 2 s behind other writers (a rebuild storing,
a full cache evicting, many searches touching their hits in their own write transactions) embeds the remaining
~53,900 texts cold although the cache holds them. Correct (named, no failure, no wrong vector), but it defeats the
ticket's purpose under exactly the load it exists for. Recommendation (rides along with KPI 7's follow-up, DEC-802):
skip only the failing call; keep `get` usable after a failed `put`; or retry the next batch.
- Ordinary work: no, because a store holds the writer lock about 20-40 ms (measured, F2), so a wait past 2 s needs
  dozens of writers queued at one moment or a stalled disk; plausible only under extreme load.
- Consequence: other (more texts sent to the shared embedder; nothing fails, nothing wrong is served).

### F2: the eviction scans and sorts the whole table inside the write lock (KPI success-4)
`_evict` orders `vector LEFT JOIN vector_use ... ORDER BY coalesce(u.used, 0), v.id`, which cannot use the
`vector_use_used` index, so every store at the bound (the steady state) reads every row while holding the writer lock.
Measured here: a store of 32 at the bound took 24-46 ms at 10,000 entries and 20-36 ms at 30,000; the order query
alone 11 ms at 30,000 (0.1 ms in the indexed form below), so about 40 ms at the default bound's ~110,000, small next to
the commit. Every new row gets its `vector_use` row, so `SELECT id FROM vector_use ORDER BY used LIMIT ?` would use
the index. Orphan `vector_use` rows also stay behind when a bad row is replaced (`INSERT OR REPLACE` gives a new id),
a small leak.
- Ordinary work: yes, because a cache at its bound evicts on every store.
- Consequence: other (a few tens of ms more lock per store; no wrong vector, no failure).

### F3: a malformed chunk vector from the embedder is cached for the whole machine (failure-1, success-2)
`_build` never checked the shared runner's chunk vectors (finite numbers, one length); the query path does
(`_well_formed`). Now one bad answer is stored machine-wide and served to every tree until evicted, where before a
fresh tree embedded the chunk again. The read check rejects only empty or non-multiple-of-4 blobs. Recommendation: put
only well-formed vectors (one length across the batch, every number finite).
- Ordinary work: no, because the shared runner has not been seen to return malformed chunk vectors; it is a
  hardening row.
- Consequence: other (a bad vector reproduced, as the store itself would hold it; not another text's vector).

### F4: a lookup trusts the index and any whole-float blob (failure-1, failure-3)
`get` selects only `id, checksum, embedding`, so a corrupt unique index could hand back another key's row; a row of
4 bytes with a matching checksum is served as a 1-number vector (probe: returned, length 4); a text value in
`embedding` raises `TypeError`, which is not caught and stops the rebuild (probe: `TypeError: string argument without
an encoding`). Recommendation: select the three key columns and compare them; reject a length unlike the batch's or
the store's; catch `TypeError`/`ValueError` as a miss.
- Ordinary work: no, because each needs another program writing the file or page-level corruption.
- Consequence: other (Wave 3 hardening row).

### F5: the isolating fixture is function-scoped (conftest question)
`_own_vector_cache` is an autouse function fixture; pytest instantiates module- and session-scoped fixtures first, so
a wide-scoped fixture that embeds in-process, or spawns with `os.environ`, uses the default folder, the user's real
cache. None does today (W1-21 and W1-17 build from a scratch environment with their own `HOME`; W2-54 and W2-126 set
their own folder; the real cache holds no stand-in digest). Such vectors would carry the stand-in's digest and never be
served for the real revision, but take bound space. Recommendation: also set `GOV_VECTOR_CACHE_DIR` per process in
`pytest_configure`, as `GOV_REBUILD_LOCK` is.
- Ordinary work: no, because no such fixture exists now; it needs a new wide-scoped fixture that embeds.
- Consequence: other (bound space used in the real cache; no wrong vector served).

### F6: KPI 7 (the bounded retry on 5xx and a reset or refused connection) is not in this tree
W2-123's retry is not on `w2/integrate` (no `RETRY_WAITS_S` there or here); DEC-1042 (4) places KPI 7 after W2-123
lands. The KPI is not met at this head, by decision.
- Ordinary work: yes, because a transient 5xx happens (W2-123's 10:39 rebuild), but the gap is W2-123's, not this
  change's.
- Consequence: other (a deferred line, as DEC-1042 (4) decided).

### F7: the per-day "after" figure is projected, not measured (KPI success-6)
The planted measurement gives before/after for the first fill, a lead's first rebuild, a close's clone and a nightly
(49,600 to 12,412 texts), and the size (4,839 B per entry); the machine's own texts per day after is "by construction",
to be read from the shared embedder's log after the merge (the freeze forbids touching the servers).
- Ordinary work: no, because it is a gap in a measurement, not a behaviour.
- Consequence: other (a follow-up measure row after the merge).

### F8: launched sessions may not be able to write the cache (out of scope: `src/gov/launch/launcher.py`)
The launcher's sandbox `allowWrite` is the session's TMPDIR and its own folder; if sandboxed commands cannot write
`~/.cache/gov-os/vector-cache`, their rebuilds read the cache but never store into it or record last use (a named
`skipped`), and the cache is filled only by unsandboxed runs (the CTO's gate, the nightly). Not verified: this session
can write the folder, but it is not a `gov launch` session.
- Ordinary work: yes, because every launched session's rebuild would hit it, if the sandbox denies the write.
- Consequence: other (fewer hits; named, never a failure or a wrong vector).

### F9: W2-54's `test_one_ticket_gets_one_packet_hash_whatever_the_cache_s_state` stays red (out of scope: MR-3)
The evidence names it red because of this change: its premise expects `gov context` to leave the tree's query-vector
file, which a machine-wide hit no longer writes. The packet's answer is unchanged; the case's premise is stale. It is a
test designer's revision under DEC-1042 (2) ("any other W2-54 case red for this reason").
- Ordinary work: yes, because the scoped set runs it.
- Consequence: other (a red acceptance case on a stale premise; no product defect).

## Verdict

READY by the rule: no finding that is in scope, reachable in ordinary work and fails open or loses work. KPI 7 is
not met at this head, deferred by DEC-1042 (4); F1 and F2 are recommended to ride along with that follow-up.

```verdict
{"kpis": [
 {"kpi": "success-1", "verdict": "pass", "findings": [{"id": "F8", "scope": "out", "ordinary_work": "yes", "consequence": "other"}]},
 {"kpi": "success-2", "verdict": "pass", "findings": [{"id": "F3", "scope": "in", "ordinary_work": "no", "consequence": "other"}]},
 {"kpi": "success-3", "verdict": "pass", "findings": [{"id": "F1", "scope": "in", "ordinary_work": "no", "consequence": "other"}, {"id": "F5", "scope": "in", "ordinary_work": "no", "consequence": "other"}, {"id": "F9", "scope": "out", "ordinary_work": "yes", "consequence": "other"}]},
 {"kpi": "success-4", "verdict": "pass", "findings": [{"id": "F2", "scope": "in", "ordinary_work": "yes", "consequence": "other"}]},
 {"kpi": "success-5", "verdict": "pass", "findings": []},
 {"kpi": "success-6", "verdict": "pass", "findings": [{"id": "F7", "scope": "in", "ordinary_work": "no", "consequence": "other"}]},
 {"kpi": "success-7", "verdict": "fail", "findings": [{"id": "F6", "scope": "in", "ordinary_work": "yes", "consequence": "other"}]},
 {"kpi": "failure-1", "verdict": "pass", "findings": [{"id": "F3", "scope": "in", "ordinary_work": "no", "consequence": "other"}, {"id": "F4", "scope": "in", "ordinary_work": "no", "consequence": "other"}]},
 {"kpi": "failure-2", "verdict": "pass", "findings": []},
 {"kpi": "failure-3", "verdict": "pass", "findings": [{"id": "F4", "scope": "in", "ordinary_work": "no", "consequence": "other"}]}
]}
```
