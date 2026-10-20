# W1-13 (DAEO-w616) lead checkpoint — 2026-10-05

## State
- Branch `w1/W1-13`, head `9eca416f` (designer's commit; base `d94f1cf6`, up to date with `w1/integrate` at start).
- Step 1 (merge) done: already up to date.
- Step 2 (test design) done: 92 cases in `tests/acceptance/W1-13/`, plus the planned W1-07 revision
  (`readiness` joins `BUILT_LATER`; "planned: command implemented", DEC-190).
- Step 3 (check red) done by the lead: `3 failed, 89 errors` — 89 stop at the `built` fixture
  (`NOT_IMPLEMENTED`), 3 in `test_w1_13_command.py`. W1-07 + `tests/unit/launch/test_command_modules.py`: 242 passed.
- Returned PACKAGES: DP-1 to DP-4 (designer's, each tested at its option (a)). 90 of 92 cases depend on them.

## Nothing runs. No engineer was started.

## Next, once the packages are answered
- If all four are answered at option (a): the suite stands. Start the engineer (brief A2, est. 170 lines), with the
  `main.py` docstring word for word, `src/gov/checkpoint/command.py` as the example, and the interface in the first
  block of `tests/acceptance/W1-13/w1_13_support.py`. Then verify all suites, then reviewer (A3) with the probes in
  the lead's task.
- If any is answered otherwise: a fresh designer revises the suite first (the answer as described behaviour).
- `.gov-runtime/scratch/w1-13-standin/` is the designer's throwaway copy with a working stand-in implementation.
  The lead's `rm -r` was not permitted. It must be gone before the engineer starts, or the engineer brief must
  forbid reading it.
- The designer's full return is in `.gov-runtime/scratch/lead/log/a1-designer.json` (`result`).

## Loop count
0 (no engineer iteration yet). Tell nobody.
