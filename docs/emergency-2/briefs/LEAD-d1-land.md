# Lead brief: bring W2-210 (D1, the lite verdict stage) up to the 0.1.5 base for its landing

You are a ticket lead (Sonnet, medium), started by the Gov OS CTO on 2026-11-24. **Read `docs/emergency-2/briefs/LEAD-COMMON.md` first: every rule there applies.** Decide, never ask (I-10).

## Why
W2-210 (`.tickets/DAEO-d3d4.md`; branch `e2/d1-verdict`, worktree `/home/usain/gov-os-worktrees/E2-d1-verdict`, head `3f2050653`) is built and green but about 207 commits behind `w2/integrate`. It lands in 0.1.6 (DEC-1231). The CTO tried the merge and undid it: the merge conflicts in `tests/acceptance/W2-81/README.md` (the `VERDICT` capability row: the branch says built, `w2/integrate` says not built), and after the merge `tests/acceptance/W2-81/test_w2_81_judge.py::test_the_capability_table_is_dated_2026_11_20_and_the_readme_says_what_the_verdict_stage_is` (added on `w2/integrate` after the branch began) asserts the "not built" text. Resolving it inside the merge commit broke DEC-253 (`tests/acceptance/W1-01/test_w1_01_integration_merges.py`: a merge commit may not itself change a file under `tests/acceptance/`).

## What
1. Bring `e2/d1-verdict` up to `w2/integrate` so that **no merge commit changes anything under `tests/acceptance/`** and every acceptance change is a commit by the independent test designer (`Role: independent-test-designer`). Choose the order that achieves it (for example: the test designer first commits, on the branch, the W2-81 README and test as they must read once W2-210 is built, taking `w2/integrate`'s other changes to those two files; then the merge resolves with no acceptance content of its own). Read `tests/acceptance/W1-01/test_w1_01_integration_merges.py` for the exact rule before you choose.
2. The test designer owns every edit under `tests/acceptance/` (W2-81 and W2-210); the engineer touches none (DEC-1243 (2)).
3. Check `tests/acceptance/W1-35/` alone on the merged branch: in the CTO's one-process run of the selection it failed to import (`cannot import name 'CHECKS_DIR' from 'conftest'` resolving to `tests/unit/dispatch/conftest.py`). Say whether it is red on `w2/integrate` too when run alone and when run with `tests/unit/dispatch/`, and if it is a clash of two `conftest` modules in one run, name it as a finding (do not fix it here).

## Green
`gov accept W2-210 --root <worktree>` green; then exactly the impact-selected suites: `PYTHONPATH=<worktree>/src python3 -m gov.cli.main queue DAEO-d3d4=e2/d1-verdict --onto w2/integrate --select` (the ticket file is already on `w2/integrate`), run through the heavy slot (DEC-1244 X-1). `tests/acceptance/W1-01/test_w1_01_integration_merges.py` must pass. Check the trailers (LEAD-COMMON) and that no merge commit on the branch touches `tests/acceptance/` (`git diff --name-only <merge>^1 <merge> -- tests/acceptance` empty for each merge, per the W1-01 rule).

## Return
Branch and head; the order you chose and why; the selected suites' summary lines; the W1-35 answer; reds not yours.
