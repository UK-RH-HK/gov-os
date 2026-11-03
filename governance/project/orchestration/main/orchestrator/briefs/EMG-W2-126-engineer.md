# Emergency task: W2-126, the machine-wide vector cache (engineer)

Read `briefs/EMG-common.md` beside this file first; its rules hold.

**Role:** engineer. **Worktree:** `/home/usain/gov-os-worktrees/W2-126`, branch `w2/W2-126`, head `e267dd3a1daa`
(`w2/integrate` merged in by the CTO at 19:28; tree clean). **Ticket:** `DAEO-jpr0` (W2-126, STANDARD). TMPDIR
`/tmp/gov-os-emg-w2126`. Note: the live query server (pid 3877550) has this tree as its working folder; never stop it
or anything of the shared servers.

## Why
DEC-1032/DEC-1033 item 2 (d), DEC-1039 item 1: about 503,000 texts went through the shared embedder in 13 hours, nine
full copies of the corpus. A chunk's vector depends only on the model, its revision and the text; one cache, shared on
the machine, makes every text embedded once. No cold rebuild anywhere.

## The spec
Read `.tickets/DAEO-jpr0.md` (its KPIs are your spec) and the decisions it cites. **Never read
`tests/acceptance/W2-126/**`** by any tool (the counterpart's work, DEC-820 (c)); run them only, results only. The
interface the test designer stated (handed to you by the CTO):
- `GOV_VECTOR_CACHE_DIR`: the cache's folder (default under `$XDG_CACHE_HOME`, else `~/.cache`); one file, mode 0600.
- `GOV_VECTOR_CACHE_MAX_BYTES`: the bound in bytes on disk; least-recently-used eviction past it.
- `vector_cache` `{hits, misses, skipped}` in the results of `semantic.refresh` and of search.
- The key: the model, its `/api/tags` digest (the revision) and the sha256 of the exact text sent.
- The CTO's decision on the lead's T2 (P3, delegated): (a), the naming in the semantic results only, not in
  `gov rebuild --json`.
Allowed paths: `src/gov/retrieval/semantic.py`, `src/gov/retrieval/vector_cache.py`, `tests/unit/retrieval/test_w2_126*`,
`docs/changes/W2-126-evidence.md`. Nothing else.

## Musts
- Never a wrong vector: a hit only for the same model, revision and exact text; a corrupt or unreadable cache is a miss
  (named `skipped` or a miss, never an error that stops a rebuild, never a vector of the wrong length).
- Concurrent writers (many sessions and rebuilds at once) never corrupt the cache or block a rebuild for long
  (SQLite in WAL mode with a busy timeout is the expected shape; your design, stated in the evidence file).
- A rebuild of an all-cached tree sends nothing to the embedder and gives the same store, byte for byte.
- Your own unit tests first (test-driven), then `gov accept DAEO-jpr0` (the opaque runner: results only; through the
  gate, with this tree's `src`), then the scoped set. Evidence in `docs/changes/W2-126-evidence.md`: the design, the
  KPI lines and how each is met, the measured numbers (a rebuild's texts sent before and after, on a small planted
  tree with a stand-in embedder; never the real servers).
- Commits: `Task: DAEO-jpr0`, `Implements: DEC-1032,DEC-1039`, `Role: engineer`.

Return DONE with the head, `gov accept`'s result (n/17), the scoped results with every red explained, and the cache's
default location and size. Estimate: about 150 lines of product code, 2 hours. One independent review follows (the
CTO starts it).
