# W2-86 (DAEO-jsg1) lead checkpoint

## State (2026-11-01 ~03:00 UTC)
- Branch w2/W2-86, head 01e21d630c44. Base 9dc5288161c4. Tests worktree and branch w2/W2-86-tests removed (merged).
- Commits (all trailers checked; trailer_gate: 9 commits, 0 lacking):
  - dc53772c6c8e test designer (Task, Role: independent-test-designer, Implements DEC-952, DEC-388)
  - eb198a6ff517 lead merge of tests (Task, Role: orchestrator)
  - 3bc60ad31987 engineer: namespaces (Implements DEC-952, DEC-388)
  - 338c14fa6475 engineer resume: kernel-template provenance restored (spec: only paths and embedding_policy change)
  - 362bb64f6983 engineer batch 2: docs/research/W2-86-memory-measure.md (Implements DEC-952, DEC-941, DEC-833)
  - 01e21d630c44 lead: gov checkpoint record CP-DAEO-jsg1-0004 (Implements DEC-952, DEC-388, Role: orchestrator)
- Tests: red at eb198a6ff517 (2 failed, 1 passed); green from 3bc60ad31987 (3/3 + unit 3/3). W1-41 embedding_policy 36 passed.
- Re-measure DONE: pinned pair control 7/11/13, head 7/11/13 (no figure moved; digest moved 11 Qs); supplementary head with tree code 11/11/15 (= W2-87). Q18, Q19 0 in all. Vectors: 93 template files / 410 chunks gained; vendored + .rulesync 0; outside template only the 3 new test files. Record committed.
- gov check (check-1, at 338c14fa6475 after wt-2 rebuild): ok; yellow core-decision-citations (195 older commits, DECISION_UNRECORDED) and openspec-validate (openspec absent): pre-existing. Doctor: path_map pass; no "no namespace is embedded"; unhealthy pre-existing.
- collect-only: 18550/18552 collected (2 deselected), no error. keyword_warn 0.
- Selection v2 (final head): scoped; core_changed [governance/project/path-map.yaml]; unplaced []; 43 targets; same as v1.
- RUNNING: verify.sh v2 (background) waiting on the load gate since ~02:26 (load 36-64 on 20 CPUs); v1 waited ~01:15-02:20 before being stopped for eng-2.

- 03:56: verify v2 stopped before it started any test: the load gate stayed shut 02:26 to 03:56 (min of 1- and 15-min load 29 to 108, never under 20). Returned PACKAGES (DEC-943).

## What a resume must do
- If verify v2 has not started by ~03:55, stop it and return PACKAGES (DEC-943: held past 90 min by the load gate); the scoped run then falls to the orchestrator or a later lead: `bash .gov-runtime/scratch/lead/verify.sh v3`.
- If it runs: read log/parallel-v2.{out,exit,xml}, log/serial-v2.*; re-run any load-sensitive or W2-54 green-here red alone; name every red.
- Return DONE/PACKAGES with the twelve fields, guard_refusals, brief_gaps.

## Brief gaps
- workers' .gov-runtime/scratch/<name>/ writes refused in the sandbox (td-1, eng-1) | common brief | ~3 min
- pinned gov 5c40122014da predates W2-87's authority order, so the brief's "control includes W2-87" does not hold under the named procedure | this ticket's part | ~15 min
- 2 h background limit vs the shared rebuild lock queue: waiters had to be restarted | common brief | ~15 min
- the tree's code cannot read pinned stores (W2-87 §7) so a tree-code pair needs tree-built stores | this ticket's part | ~5 min
- loop count: converged.
