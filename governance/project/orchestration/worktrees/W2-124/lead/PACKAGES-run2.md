task: DAEO-mb2t (W2-124) · run 2 (build) · lead return PACKAGES (P3 list) with fix round 1 LAUNCH-refused twice

## P4: earlier suites red under S1's rule (P3: to the owner by name; widening is the owner's, DEC-1142 (8))
All 20 fail for one cause: the planted project has an embedded namespace and no embedder, and its rebuild now fails
REBUILD_FAILED (store: semantic). That is S1 (DEC-1015 item 4, DEC-1027 C) working, not a fault in the code.
Evidence: lead_verify at c3e57a2c87f6, .gov-runtime/scratch/lead/log/verify/{parallel,serial}.xml.
- tests/acceptance/W2-32/test_w2_32_s2_fail_closed.py (5): reads stores.semantic from a result that is now {}
- tests/acceptance/W2-32/test_w2_32_s10_no_cpu_fallback.py (2): same
- tests/acceptance/W2-13/test_w2_13_secrets.py (1), test_w2_13_unavailable.py (2), test_w2_13_latency.py (1, serial)
- tests/acceptance/W2-76/test_w2_76_timings.py (1), test_w2_76_unchanged.py (1)
- tests/acceptance/W2-116/test_w2_116_reindex.py (1)
- tests/acceptance/W1-41/test_w1_41_embedding_policy.py (1): its not-embedded project's exit code no longer matches the embedded one's
- tests/unit/rebuild/test_w2_116_integration.py (2): one ok expectation, plus [endpoint fails] where the error's stores are now under details.details (integration.py wraps command.run's GovError)
- tests/unit/rebuild/test_no_embeddings.py (1): the not-embedded project now says requested: false (S2 / the Interface)
- tests/unit/rebuild/test_w2_122_seed.py (1)
- tests/unit/retrieval/test_w2_32_rebuild_cut.py (1)
Options:
- (a) Widen: the test designer gets these 13 files under Rewrite-Reason: DEC-1027 C. Each case gets --no-embeddings,
  a healthy stand-in, or reads error.details.stores where it checks a refusal. One designer batch (~USD 3) plus a
  lead_verify. Recommended. Confidence: high.
- (b) Narrow S1 to the CLI: check() runs only in gov rebuild's CLI entry, not in command.run. Most unit reds clear,
  but the close (close/batch.py -> command.run) would no longer fail. That breaks S4 and F1 and the accepted Interface.
  Not recommended.
- (c) Leave them as reds in the queue for each owner ticket. Landing stays blocked.
Blocks: DONE (DOD green). Does not block the fix round below.

## Fix round 1 (not converged yet: one iteration of three)
Own-suite reds at c3e57a2c8, given to eng-2 (brief .gov-runtime/scratch/lead/briefs/eng-2.md, failing output eng-2-failing.txt):
- S5 no .gitleaks.toml: exit 1 REBUILD_FAILED (lexical). P2 (b) requires exit 0 with complete: false and not_built naming it.
- S5 whole and S5 --no-embeddings: codeintel goes into not_built when the path map does not ask for code intelligence (tool absent).
- S1 hung and S1 part-way-500 (in-process): 76 to 81 s against a 60 s bound. They fail alone too (127 s), so this is real, not load.
eng-2's launch: LAUNCH_REFUSED, the resource gate shut on memory (DEC-1088 (5)), refused twice (16:2x and 16:3x). Stopped
per DEC-1142 (9). NEXT: relaunch eng-2 unchanged once the gate is open.
