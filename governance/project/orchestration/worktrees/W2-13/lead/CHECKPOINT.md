# W2-13 lead checkpoint (DAEO-zqvn), end of resume 1 under DEC-1000: PACKAGES (waiting for W2-92's landing)

- Updated: 2026-11-01 17:35 UTC. Branch w2/W2-13, head bdc4b7956a48 (lead checkpoint record CP-DAEO-zqvn-0008) over febe5f6403d5 (last code).
- Commits this resume (trailer_gate before the record: 13 judged, 0 lacking, 0 bad Implements):
  - 9f96baf04a06 engineer (eng-2): builder test test_w2_13_rerank_work.py; no src change (Implements DEC-725, DEC-802)
  - 15e235d637bc independent-test-designer (td-2): the seven S1/S2 cases read `ranked` (Rewrite-Reason: DEC-1000 (P-W2-13-3 (b)); Implements DEC-725, DEC-900)
  - 962fc43467f7 orchestrator: merge --no-ff w2/W2-13-tests (DEC-725, DEC-900, DEC-963)
  - febe5f6403d5 engineer (eng-3): id boost for a question holding an id among words (TD-4); lexical.whole_id shared with command.py (DEC-725)
  - bdc4b7956a48 orchestrator: docs/checkpoints/DAEO-zqvn/CP-DAEO-zqvn-0008.md
- Tests worktree W2-13-tests and branch w2/W2-13-tests: removed (merged).
- Results:
  - red at the base (rewritten tests, base clone's code): 20 failed, 34 passed (latency file left out), as the README states.
  - gov accept (lead, febe5f6403d5): 54 passed, 2 failed: S1 13/0, S2 2/1, S3 24/1, S4 8/0, F1 3/0, F2 4/0. The S2 red is test_gov_retrieve_cites_what_the_lexical_route_ranks_for_a_plain_word_question (waits for W2-92 / the retrieve.py line); the S3 red is the real-model latency case under load (30-37) (all unavailable cases pass: lead's run of the unavailable and fusion files, 25 passed, 1 failed = the bundle case).
  - Interleaved latency (lead, fusion.search warm, both dev tiers, 52 questions, head-built real-embedder stores, load 22-30): base-1 p95 1.334 (cold), head-1 0.407, base-2 0.479, head-2 0.423. The head is not slower than the base; P-1 settled with no code change.
  - collect-only: 19119/19121 tests collected (2 deselected), no error. keyword_warn: 0 files.
- Packages left: only "waiting for W2-92's landing" (P-W2-13-1 (a) as decided in DEC-1000). Residuals: TD-1 (src/gov/closure/** owner), TD-2 trigram table (W2-32 / Wave 3).
- A resume must: after the CTO adds src/gov/retrieval/retrieve.py to the paths and merges w2/integrate: an engineer makes the one line (routes fuse `answer.get("ranked", answer["hits"])`), gov accept once, the memory re-measure (base clone kept at /home/usain/gov-os-runs/W2-13/base with its store; head clone: check out the new head and rebuild), the dev queryset lexical-only hit@5 again, the full worktree rebuild, select_tests.py and its scoped run in the close's form (verify_lock.sh), gov check, collect-only, trailer_gate, keyword_warn, the review (independent-auditor, max, JUDGEMENT.md) and the probe record under docs/probes/DAEO-zqvn/. Re-run the real-model latency case alone (load-sensitive) if it is red.
- Left in place: /home/usain/gov-os-runs/W2-13/{base,head} (1.3 G, 24,171 inodes); /tmp/gov-os-lead-W2-13 (90 M, 9,024 inodes; holds lat-tiers); untracked pytest-of-usain/ in this worktree (428 K, 79 inodes; the engineer's pytest temp from run 1, planted test secret); the worktree store .gov-runtime (470 M, base code).
- Loop count: held by the lead.
