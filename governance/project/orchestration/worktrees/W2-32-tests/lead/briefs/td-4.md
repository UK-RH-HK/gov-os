# W2-32 test designer, round 4: the stand-ins S10 breaks (the CTO; P-W2-32-4)

The engineer's S10 is in (`3a27107d`; the CTO merged your round 3 into `w2/W2-32` outside the sandbox). Same rules as
before (stand-ins only, no `gov retrieve`, the `ps` check; do not merge yourself: the CTO merges `w2/W2-32` into your
branch first; run on that head). S10: `gov` never starts an embedder (a health check only, `EMBEDDER_UNAVAILABLE`); the
GPU is the only device (a stand-in's `/api/ps` must report the model on the GPU, `size_vram` > 0, or its vector is refused
as `EMBEDDER_ON_CPU`; a rebuild on the CPU stores nothing). Revise, as you did for the digests, the cases this breaks, each
keeping what it guards, each still red on the change it guards (planted in a scratch copy):
- `tests/unit/rebuild/test_w2_122_seed.py`: 18 cases (its stand-in reports no model on the GPU);
- W1-18's `test_w1_18_on_demand_start.py`: it asserts `gov` starts Ollama on demand, the rule DEC-1065 (1) replaces: revise
  it to the new rule (the server not answering: the semantic part unavailable, named `EMBEDDER_UNAVAILABLE`, a keyword
  answer, no `ollama serve` started), with `Rewrite-Reason: DEC-1065 (1) replaces the on-demand start`;
- the acceptance stand-ins whose `/api/ps` reports `size_vram: 0` (W2-123's, W2-122's, W2-54's, and any others a scan of
  `tests/` finds).
Commit with `Task: DAEO-0pyc`, `Implements: DEC-1064, DEC-1065`, `Role: independent-test-designer`, a `Rewrite-Reason:` naming
S10 (or DEC-1065 (1)), Co-Authored-By. Return the twelve fields with the cases' before/after on the engineer's head.
