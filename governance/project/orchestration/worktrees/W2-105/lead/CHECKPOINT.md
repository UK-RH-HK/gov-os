# Lead checkpoint, DAEO-zpdj (W2-105), run 2 (resume), at return (~17:58Z, 2026-11-01)

## State
- Branch w2/W2-105, head fa653609cc93 (clean). Verified head = fa653609cc93. Nothing committed in run 2 (no gov
  checkpoint record committed, to keep the verified head the head returned).
- KPI 2 re-baselined (DEC-971 item 4); P-W2-105-1 closed by it.
- Status returned: DONE, with residual R-W2-105-1 (the README map is unreadable to gov accept for 3 lines).

## Results (run 2)
- ps-3 (product-spec, sandboxed via gov launch, session cf9826ec): sandbox check passed; `gov accept DAEO-zpdj
  --json` exit 3, outcome fail, totals 28 passed / 0 failed / 0 skipped; success-3 and failure-3 pass (6 each);
  success-1, success-2, failure-1 fail with 0/0/0 (map items with placeholders such as `test_x[<install>-deny]` and
  `[<role>-<install>]` do not match in src/gov/accept/runner.py matches(); names_a_test then fails the line);
  22 cases unmapped. No case asserts the CTO-only rule. Tripwire 4: nothing changed in this worktree; other trees
  W2-13 (untracked dotfiles) and W2-13-tests (3 modified files): other tickets' work.
- W1-38: 201 passed (exit 0, 94 s). W1-39: 71 passed (exit 0, 75 s). No conflict after the merge-back.
- select_tests.py: scoped, core_changed [], unplaced [], 32 targets, 282 options, 0 serial-only entries.
- Scoped parallel run (close's form): exit 0, 4196 passed, 1 skipped, 591 s (W2-105 28/28, W1-38 201/201 inside it).
- Collection: exit 0, "19074/19076 tests collected (2 deselected) in 24.75s".
- Rebuild-2: exit 0 (lock wait 15:34 to ~16:21; semantic 3,700 s on the shared Ollama); ended 17:28:36Z.
- gov check: exit 3. RED context reproducibility: "DAEO-i89t: mandatory input 'AR-5' not found in the store"
  (W2-120's ticket, CTO commit 7224a564 on w2/integrate; not this change). YELLOW core-decision-citations
  (DEC-999, DEC-994, DEC-998, DEC-991, DEC-9003, DEC-9004, DEC-968 ... cited by commits but not recorded in this
  tree). YELLOW openspec-validate (openspec not on PATH). All others GREEN.
- trailer_gate: "DAEO-zpdj: 10 commits, 10 judged, 0 lacking, 0 Implements item(s) not a decision or Contract id
  that resolves". keyword_warn: 0 files.

## What a resume must do
- Nothing for verification. If the CTO takes R-W2-105-1 as a test-designer revision: a README-only map revision in
  tests/acceptance/W2-105/ (Rewrite-Reason naming DEC-959 item 6), then one gov accept run.

## Brief gaps (run 2)
- The README map form gov accept (W2-96) reads came later than this ticket's tests; nothing said to re-check the map
  against it | this ticket's part | ~15 min
- The order "rebuild first, then the scoped run" holds the run for an hour behind the machine's rebuild queue,
  though no selected case reads this worktree's store | common brief | ~0 (worked in parallel), est.
- gov check takes over 10 min (gitleaks) and outlives a foreground call | common brief | ~10 min
- The final gov checkpoint record (step 7) changes the head after verification, against "DONE with the exact head
  you verified" | common brief | ~3 min

## Guard refusals (run 2)
- none

## Left files
- .gov-runtime/scratch/lead/briefs/ps-2-head.md (rm refused, run 1)
- /tmp/gov-os-lead-W2-105: 4.5M, 726 files and folders
- blob 1ae28402a109 ("sandbox-trial") in the shared object store from ps-3's step 0 (b)
