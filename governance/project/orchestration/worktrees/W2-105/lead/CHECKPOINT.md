# Lead checkpoint, DAEO-zpdj (W2-105), run r4 tests (hand-built brief, DEC-1130 (1)), 2026-11-11, at return

STATE: verified, returning DONE | HEAD: 19ac51dd9793 | BASE: 19ac51dd9793 | NEXT: the CTO writes land.txt W2-105=19ac51dd9793, lands and closes (tk close + record) | WAITING ON: none

Workers: none · Rounds: converged (no build this run) · Decisions taken: no merge of integrate (step 2: integrate 38 ahead, no trigger path in its diff) · Open packages: none (readme_map_gap is a recommendation, not a block) · Paths: log/ (cases-r4, accept-r4, verify/, alone-r4, alone-home-r4, w1-39-r4, w1-38-optin-r4)
task: DAEO-zpdj · decisions_applied: DEC-966, DEC-1130, DEC-959, DEC-968, DEC-952

## Results
- Step 1: head, the designer's fix (19ac51dd9793 over f95b82431ec5), diff of 3 files, BASE_COMMIT dca333e7a55d, template file: all as the brief says.
- Step 3: tests/acceptance/W2-105: 28 passed, 0 failed (log/cases-r4.xml). TESTS-READY written.
- Step 5: gov accept --json exit 3: totals 28/0/0, unmapped 22; success-1, success-2, failure-1, failure-2 fail 0/0/0; success-3, failure-3 pass 6/0/0 (as expected; README map gap).
- Step 6: lead_verify: scoped, core_changed [], unplaced [], 121 targets; parallel 3965 tests, 9 failed, 10 skipped (846 s); serial 0 entries. W2-105 28/28, W1-38 42/42 inside it; W1-39 NOT selected.
  - 8 reds: SIGINT variants of W2-56 test_s12 (2) and W2-96 signal cases (6): lead_verify starts with `setsid bash ... &` from a non-interactive shell, so SIGINT is ignored in the run; alone (SigIgn 0): W2-56 2 passed; W2-96 6 passed with the session's HOME (with an empty HOME they fail: gov accept's child drops PYTHONUSERBASE).
  - 1 red: W1-01 test_the_integration_merges_of_this_repository_pass: merge f95b82431ec5 brings owner commit 6fbe73b1adde (ACT-OPERATOR-ROUNDS-1); integrate's path-map exempts it (DEC-1136) after the branch's merge; red alone too; green on the candidate merge.
- W1-39 run separately: 39 passed, 32 deselected (the common -k form).
- W1-38 file with GOV_TESTS_OPTIN=lifted,breadth: 19 passed.
- links: 0 new since 19ac51dd9793; keyword_warn 0; context 4804 of 6000, ok.

## Brief gaps
- integrate 38 ahead (not 11) and touching tests/acceptance/W2-81 | this ticket's part | ~2 min
- select_tests.py does not select W1-39 (brief expected it) | this ticket's part / tool | ~5 min
- lead_verify.sh's detached launch ignores SIGINT: 8 signal cases red for the launch form | tool | ~15 min
- the empty-HOME form breaks gov accept's own child (PYTHONUSERBASE dropped) | common brief | ~5 min
- the branch lacks integrate's DEC-1136 exemption, so W1-01 is red on the branch | this ticket's part | ~5 min

## Guard refusals
- none

## Left files
- /tmp/gov-os-lead-W2-105: 37M, 8411 files and folders (not removed: rm of own temp folder not allowed headless)
- .gov-runtime/scratch/lead/briefs/ps-2-head.md (run 1)
