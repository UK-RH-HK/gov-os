# Lead checkpoint, DAEO-jpr0 (W2-126), run 1 (tests only) — STOPPED by the owner's order (via the CTO, 18:2x)

- **Stage:** STOPPED at a safe point on the owner's order (run 1 was started after the owner's 17:00 stop; W2-126
  becomes an emergency patch under DEC-1039, not a lead run). Nothing running; nothing half-written; tree clean.
- **Head (w2/W2-126):** `75c4db0e08f7`. Commits since `2a3c998fe786`:
  - `8c3ea9964218` test designer's suite, tests/acceptance/W2-126/ (9 files, 971 lines, 17 cases); Task DAEO-jpr0,
    Role independent-test-designer, Implements DEC-1032, Co-Authored-By;
  - `f90b34c47fdd` merge --no-ff of w2/W2-126-tests (clean; tree equals git's own merge); Task, Implements DEC-1032,
    Role independent-test-designer (as the ticket part directed, DEC-1031 item 3), Co-Authored-By;
  - `75c4db0e08f7` checkpoint record CP-DAEO-jpr0-0001; Task, Implements DEC-1032, Role orchestrator.
- **Workers:** td-1 (independent test designer) DONE and exited (session f06ad839-5bc5-4703-8954-18c0a91688a8);
  twelve fields complete; tripwire clean. Tests worktree and branch removed. TESTS-READY written. No engineer.
- **Results:**
  - red check 17/17 failed, each for the README's reason (`log/red.xml`);
  - rebuild-1 exit 0, 2,357 s (semantic 2,314 s: the whole corpus for a fresh tree);
  - rebuild-2 exit 0, 28 s;
  - select_tests: scoped, core_changed [], unplaced [];
  - scoped parallel run: 4119 passed, 17 failed (exactly the 17 W2-126 reds), 7 skipped, 1,445 s (`log/parallel.xml`);
  - serial phase (1 case: W2-54 test_gov_check_gives_context_reproducibility_green_here): NOT RUN, stopped (verify.exit 143);
  - collect-only "19221/19223 tests collected (2 deselected)"; trailer_gate 4 judged, 0 lacking; keyword_warn 0;
  - gov context ok (tokens 1,619,286 vs limit 6,000: every DEC source resolves to the whole register; for W2-04);
  - gov check exit 3. RED: retrieval-regression (hit@5 10 vs 80: the semantic facet is off because this base
    refuses a query vector not computed on the CPU, and the query embedder is now on the GPU; DEC-1033's fix is on
    w2/integrate), context-reproducibility (timed out at 600 s under load), core-mutation (DAEO-a3u2's
    allowed_paths cover tests/acceptance/W2-86, already on the base). YELLOW: decision citations, openspec.
- **Interface (README, for the engineer):** GOV_VECTOR_CACHE_DIR (default under XDG_CACHE_HOME, else ~/.cache;
  one file, 0600); GOV_VECTOR_CACHE_MAX_BYTES (bytes on disk, LRU eviction); `vector_cache` {hits, misses,
  skipped} in the results of semantic.refresh/search; the key is the model, the /api/tags digest and the sha256 of
  the exact text.
- **Packages:** T1 (the sandbox's TMPDIR: my brief gap); T2 (naming in the semantic results only, not in
  `gov rebuild --json`): recommend (a).
- **Exact next step:** none until the CTO or the owner says so (DEC-1039 emergency patch). If resumed: run the serial
  case alone under verify_lock.sh only when no embedding server is needed and the owner allows; merge w2/integrate
  before any engineer (DEC-1033's device rule).
- **Leftovers for the orchestrator:** /tmp/gov-os-lead-W2-126 (pytest folders); the designer's sandbox TMPDIR
  /tmp/gov-launch-independent-test-designer-* (about 136 MB, 11,832 inodes).
- **Brief gaps:** the gov launch line for a separate tests worktree; td-1's TMPDIR, read-only inside the sandbox;
  the merge's role for a clean merge (W1-01); no helper for a scoped run's serial phase (I wrote run_verify.py).
- **Guard refusals:** none.
