# W2-122 (DAEO-blwa) lead checkpoint

## State (2026-11-01 ~22:35)
- Branch w2/W2-122, head 2de1cb194a0f (start). Tests worktree /home/usain/gov-os-worktrees/W2-122-tests on w2/W2-122-tests from the same head.
- Running: rebuild-0 of this worktree (log/rebuild-0.log, .exit); test designer td-1 (old launch form, code graph needed; log/td-1.json; tripwire-before-1.json).
- Next: when rebuild-0 exits 0, tripwire snapshot 2 and launch engineer eng-1 (old form; briefs/eng-1.md).
- Then: merge w2/W2-122-tests when td-1 commits (no worker running here), write TESTS-READY, red check on a scratch at the base, engineer gov accept batch, KPI 3 measurement in this session (shared GPU), engineer batch 2 writes docs/changes/W2-122-evidence.md, scoped verification, checkpoint record, return.
- Loop count: 0 iterations of repair.

## Update 22:55
- rebuild-0 cancelled while still queued (all 3 slots held by ~45-min cold rebuilds, W2-104 queued ahead); the engineer's retrieval pointed at W2-00-store (same code). Full rebuild runs before verification.
- td-1 DONE-with-PACKAGES: commit 4244ef4fe2fc on w2/W2-122-tests (26 tests, 9 files, trailers ok). Tripwire 1: tests tree only W2-122 folder; other trees' changes are other tickets' sessions. Session cc7b5891.
- Packages: P-W2-122-TD-1 (K5 reds earlier W2-76 / W1-27 cases: W2-76 test_w2_76_unchanged::test_two_full_rebuilds_of_the_same_tree_give_the_same_digest, test_w2_76_timings::test_every_stage_timed_in_output_and_record[full], W1-27 test_w1_27_rebuild_r8_no_embeddings::test_a_rebuild_without_the_argument_asks_the_endpoint_as_today and ::test_a_retrieval_on_a_store_whose_vectors_could_not_be_built_says_so; rec (a) a TD rewrite round, Rewrite-Reason DEC-1015 item 4; P2, CTO). P-W2-122-TD-2 (secrets record machine-wide: rec (a) nothing copied on one machine).
- td left probe folders in /tmp/gov-os-lead-W2-122 (w2122-probe-*, w2122-batch-*, w2122-key-*).
- Running: eng-1 (log/eng-1.json, tripwire-before-2.json); red check in the tests worktree (log/red.log, red.exit).
- Next: when eng-1 returns, merge w2/W2-122-tests here (message file), TESTS-READY, eng-2 gov accept.

## Update 23:15
- eng-1 commit dda239e827fc (seed.py 226, command.py +47-12, unit test 207; trailers ok). Session adc7e620. Packages: P-1 K5 reds earlier tests (W2-107 unit test_w2_107_record x2, W2-76 x2, W1-41 full cases; adopt stages.py:364 INDEX_REFRESH_FAILED without an endpoint; DEC-694 projects now need an endpoint); P-2 code-graph copy discarded (codeintel.index rebuilds from scratch); P-3 fingerprint = whole gov package + gitleaks binary + python/sqlite versions (any src/gov ticket seeds refused).
- Tests merged: 7b2ac64c197b (message file merge-tests.msg). TESTS-READY written (first written with a wrong suffix, corrected).
- eng-2 (resume): gov accept refused ACCEPT_MAP_UNREADABLE (README rows "The answer and the base's record" and "Failure line" name no numbered line). No code change.
- td-2 (resume cc7b5891) running: fix the README map only, Rewrite-Reason. tripwire-before-4.
- KPI 3 measurement: worktrees /home/usain/gov-os-runs/W2-122/base (dda239e827fc) and /fresh (7b2ac64c197b), same src. Proxy :11501 (bt26t16yz) counting into /tmp/gov-os-lead-W2-122/m/cold-base.counts.json; measure.sh cold-base running (bskqb4zs6), waiting for a slot.
- After td-2: merge tests again, eng-3 gov accept; then seeded measurement (fresh from base, proxy :11502), three seeded at once (fresh2..4 or reuse), eng batch writes evidence file; full rebuild here; scoped verification.

## Update 23:27
- td-2 commit 57ea4be62a1d (README map, Rewrite-Reason). Merged afb8fed57fbb. TESTS-READY updated.
- eng-3 (resume): gov accept 24 passed / 2 failed: success-3 (evidence, expected) and success-4 1 failed (reason did not name the configured path; I ran the file myself to get the message).
- eng-4 (fresh, session e14ad1c4, repair iteration 1): commit 800cca6fba83, seed.py +4-3, unit +13-1; gov accept success-4 8/8; only success-3 red. Converged.
- Head now 800cca6fba83. Still to do: K3 measurement (cold-base queued since ~23:12 behind priority waiters), eng batch for the evidence file, full rebuild here, scoped verification, gov check, collect-only, keyword_warn, trailer_gate, checkpoint record, remove tests worktree + measurement worktrees.

## Update 00:08 (2026-11-02)
- K3 cold-base (dda239e8) FAILED after 3013 s: REBUILD_FAILED semantic "Ollama did not embed" after 1023 of ~1560 requests; the shared runner was reloaded mid-run (outside our code; K5 behaved as designed). Files kept in /tmp/gov-os-lead-W2-122/m/old/. Old measurement worktrees removed.
- New plan: base2 = /home/usain/gov-os-runs/W2-122/base2 at 800cca6fba83 (current head code), cold, proxy :11511 (bfycti8yx), measure.sh cold-base2 (b9pjbh6ji) waiting for a slot since 23:57. Sampler bupq41xru -> m/concurrency.log.
- Then: this worktree's verification rebuild = `rebuild_slot.sh W2-122 --seed /home/usain/gov-os-runs/W2-122/base2` (seeded alone, proxy); then one seeded + one cold side by side (new worktrees at head) for "with two others"; eng-5 writes evidence; incremental seeded rebuild of W2-122 after eng-5's commit; scoped run via /tmp/gov-os-lead-W2-122/verify.py parallel|serial (select.json: scoped, core_changed [], unplaced []).

## Update 01:57 (2026-11-02)
- K3 measured (m/ files under /tmp/gov-os-lead-W2-122/m): cold base2 at 800cca6fba83 semantic 4709.2 s / total 4761.6, 1701 req / 54,425 chunks, two others 74 % / one 25 %; seeded W2-122 (same commit) semantic 0.7 / total 30.8, 0 req, two others; seeded s1 (WBS edited) semantic 20.3 / total 57.7, 10 req / 320 chunks (exactly that file), one other. KPI 1 here: digest b5408db1250c7b8a equal, 54,425 vectors equal. Cold strictly alone not measured.
- eng-5 (resume e14ad1c4): commit 98d46fbc180f, docs/changes/W2-122-evidence.md (84 lines), trailers ok; gov accept 26/26 pass, all six lines.
- Final rebuild of W2-122 at 98d46fbc: exit 0, all recreated, semantic 1.3 s, digest 76bdaeac8117.
- select_tests at 98d46fbc: scoped, core_changed [], unplaced [], 39 targets, 181 options. keyword_warn 0. collect-only 19168/19170 (2 deselected).
- Removed: tests worktree + branch w2/W2-122-tests (merged), all measurement worktrees and /home/usain/gov-os-runs/W2-122.
- Running: scoped parallel run (log/parallel.log, .exit, parallel.xml) via /tmp/gov-os-lead-W2-122/verify.py; then serial (3 cases), gov check --json via heavy_slot, trailer_gate, gov checkpoint record, commit it, return DONE.

## Lead readings (P3, logged for the CTO)
- Interface fixed for both workers: `--seed [folder]` (folder = base tree root, link followed); `--json` result `seed: {status: seeded|refused|none, base, reason}`; every full rebuild writes `.gov-runtime/rebuild/stores.json` {code, embedder{model,revision}, schema}; configured base = `integration_store` (absolute path) in `governance/project/rebuild.yaml`; K5 = GovError REBUILD_FAILED with store "semantic".
- "Code fingerprint" in KPI 2 read as the Gov OS builder code's fingerprint, not the repository content's (W2-68's of_commit would refuse every seed whose tree differs, contradicting KPI 1).
- Both workers in the old launch form: the rebuild's code-graph stage needs /tmp/gov-cbm-<uid>, read-only inside the sandbox.
- The engineer runs no real-tree rebuild; KPI 3 measured in the lead's session; evidence file written by a later engineer batch.

## Brief gaps (running)
- W2-116's configuration key for the integration store does not exist yet (W2-116 open); the lead had to fix one | ticket file | ~10 min est.
- KPI 2's "code fingerprint" has two readings in the code base (W2-68's repository fingerprint vs the builder's) | ticket file | ~10 min est.
- KPI 3's measurement must run on the shared GPU (lead's session) but its file is in the engineer's paths; the split of who measures and who writes is not stated | this ticket's part | ~5 min est.

## Guard refusals
- none so far.
