# W2-81 (DAEO-l78m) lead checkpoint — run 1, end state

## State (2026-11-01 ~01:45)
- Branch w2/W2-81, head 3004f33024f9 (clean tree). Base 26b387a0ad3d.
- Commits this run (all trailers ok; trailer_gate: 11 commits, 0 lacking, 0 bad Implements):
  - e1d40b68d3b2 batch 1 (independent-test-designer): builders, planted problems, controls, seed, manifest, self-tests.
  - 2dd40a4e530b, 3cc35cd5cca1 batch 2 (independent-test-designer): judge, stand-ins, 21 mutants.
  - 18d082983e02 batch 3 (independent-test-designer): scorer, 61 visible questions, hidden-half form + variants hook, runner, README.
  - 19ec510ad263 lead: checkpoint record CP-DAEO-l78m-0004 (before review 1).
  - 0a2608e40388 batch 4 (independent-test-designer): review 1's F1-F10 fixed (183 cases).
  - 3004f33024f9 lead: checkpoint record CP-DAEO-l78m-0007 (before review 2).
- Designer session 9c2f47ad-6ef7-4454-ac3e-6408fad47084 (gov launch, sandboxed, effort high), four batches.
- Review 1 (47dd5343-86a7-437e-8ef4-0518bc474261) on 19ec510ad263: FAIL (F1-F5 yes/fails open). Draft: .gov-runtime/scratch/lead/probes/PR-DAEO-l78m-review1-draft.md.
- Review 2, the last (ab3355c0-c85f-4da1-be70-c38d92840362) on 3004f33024f9: FAIL on F1 only (a large file moved by a reviewed A3 move into an embedded namespace is judged at its old path -> FOUND_AND_HANDLED; yes / fails open). Draft: probes/PR-DAEO-l78m-review2-draft.md. No probe record committed (DEC-733).
- Both reviews of the declared round are used (DEC-916, DEC-413). Fixing F1 needs a new declared round (orchestrator) or the owner's exception for a third review -> PACKAGE P-W2-81-F1.
- Scoped selection (select_tests.py) at 3004f33024f9: scope scoped, core_changed [], unplaced []; selects tests/acceptance/W2-81/, tests/unit and ~30 other acceptance targets. NOT run: the head is not final (F1 package); the store rebuild has not run (queued lock, stopped once).
- suite_now.sh (W2-81 suite plain + -n auto + collect-only) was held ~25 min by the load gate (load ~80 on 20 cpus) and stopped by the lead before any test ran (head not final). Returned PACKAGES.

## What a resume must do
1. If the orchestrator declares round 2: resume designer session 9c2f47ad... with F1 (+ ride-alongs F2, F5, F11, F12; F9 and F13 optional) as behaviours; check commit/trailers/tripwire; commit a gov checkpoint record; review (up to two in round 2) on the new head; commit the passing probe record (full probed_commit) under docs/probes/DAEO-l78m/.
2. Then: full rebuild (flock), import check, select_tests.py, scoped parallel + serial runs in the close's form, gov check, collect-only, keyword_warn, trailer_gate; return.

## Loop count
- 2 (review 1 failed -> batch 4; review 2 failed on F1).

## Brief gaps
- Effort for FULL designer: run part says high, DEC-839 says xhigh | this ticket's part | 2 min (est.)
- Rebuild lock queue (5 rebuilds ahead); designer did not need this store | common brief | 25 min (measured)
- gov retrieve from W2-00-store fails inside the sandbox (network to ollama.com) | tool | ~5 min across workers (measured)
- Reviewer in this worktree: gov retrieve STORE_MISSING (no store here; rebuild never ran) | this ticket's part | ~2 min (est.)
- The run declared one round with two reviews but no rule for a fail-open left after the last review except the owner's exception | this ticket's part | 10 min (est.)
- Workers cannot remove their own sandbox temp folders (rm -rf needs approval) | tool | ~2 min (est.)

## Guard refusals
- designer batch 1: chained mkdir && python3 ...; rm -rf ... refused (permission) | true-ish (rm -rf needs approval) | 2 min, moved to a script
- reviewer 1: shell variable as write target (true); inline python3 -c naming the suite path read as a write (false positive?); rm -rf of own probe folders (permission prompt)
- reviewer 2: shell arithmetic on a variable (true, form rule); combined rm -rf needing approval (permission)
- lead: none
