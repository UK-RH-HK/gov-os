# The emergency's stops (DEC-1033), 2026-11-02 13:01, each at a safe point
- **The landing of six** (W2-11 c9f99b28b88b, W2-105 fa653609cc93, W2-90b 73c18fea1e1f, W2-81 e78e6af7530d,
  W2-91 55b47e075b3b, W2-92 448a835a9dca): `land.py` and its queue run stopped (17 processes) while testing in the
  queue's warm clone (merged 2f669de8842e onto 01f5d8be36ae at 11:19); w2/integrate unmoved, no merge in the main tree;
  the six stay approved in `merge-queue/approved/` and listed in `dispatch/land.pending.txt` (with W2-61h). Resume:
  relist them after the emergency (one queue run).
- **The re-close of W2-05 and W2-96** (DEC-1027 B): `close_build.py` stopped (4 processes) in its scoped run on its
  clone (selection made 12:59); no close record, no commit. Resume: run it again after the emergency, against the
  nightly baseline of 11-02.
- **W2-04's repair round** (DEC-1025): its lead stopped (14 processes) after the repair commit `de81824b` and the
  test designer's merge `a0c79a6c`; its tree clean. Next: `gov accept`, the scoped run, review 2 (the brief's steps 3
  and on). Resume: a fresh lead in its worktree from its `.gov-runtime/scratch/lead/CHECKPOINT.md`.
- **Left running (the fixes):** W2-122 (seeded rebuilds), W2-123 (the bounded retry; returning run 2 as DONE),
  W2-112 (the shared reranker, started 13:01 past the gate). Parked: the ready list in `dispatch/ready.parked-by-freeze.txt`.
