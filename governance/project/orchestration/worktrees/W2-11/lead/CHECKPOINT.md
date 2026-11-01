# W2-11 (DAEO-k7hz) lead checkpoint — round 1 of 2 (DEC-916), resume under DEC-992 (run 2)

## State at return (2026-11-01, PACKAGES)
- Branch w2/W2-11, head c5a9b43a0e79 (start d7a9e4af0df1). Tracked tree clean; untracked: sandbox placeholder
  dotfiles, `pytest-of-usain/` (185M, 21,038 inodes) and `gov-rebuild-4-xtmxc8yp.lock` (left from run 1; the CTO
  was to remove them before this run; still there).
- Commits this run: bdae4e45, 668b0ad5, 38887d51, 647f2f44 (test designer, Rewrite-Reason each); 7a2baf50 (lead
  merge of w2/W2-11-tests); 233f7cfc (product-spec: W2-96 KPI 6, F1-F6); c5a9b43a (lead: CP-DAEO-k7hz-0011).
- Tests worktree W2-11-tests removed; branch w2/W2-11-tests deleted. TESTS-READY names 7a2baf50b4a6.
- trailer_gate: "DAEO-k7hz: 29 commits, 29 judged, 0 lacking, 0 Implements item(s) not a decision or Contract id
  that resolves". keyword_warn: 0 files. gov.__file__ = /home/usain/gov-os-worktrees/W2-11/src/gov/__init__.py.
- gov accept (ps-5, at 233f7cfc): 127 passed, 17 failed, 1 skipped; fails = success-7 (2), success-12 (5),
  unmapped G13 (9): the .claude copies (P-5); failure-1 (1): the validator (P-2 / P-W2-11-9).
- W1-35 (lead, at 233f7cfc): 166 passed in 294.93 s, exit 0.
- Scenarios: all six PASS (scenarios/RESULTS.md).
- NOT RUN (held by DEC-992 until the copies land): rebuild, select_tests, collect-only, scoped run, gov check.

## Open (blocks DONE)
1. P-W2-11-5 (b): the 16 .claude/ copies — the CTO's commit. None landed in d7a9e4af0df1..HEAD.
2. P-W2-11-9 (new): gov launch refuses an engineer on this ticket:
   `gov launch: LAUNCH_REFUSED: ticket 'DAEO-k7hz' is a ticket of another role ('product-spec'), not of 'engineer'`
   so P-W2-11-2 (validator failure KPI, row W2-L097) is not done.

## What a resume must do
1. If the copies have landed (a commit touching .claude/skills/ with Task: DAEO-k7hz): check `git log -2`,
   `git status`; then if P-W2-11-9 is decided with an engineer, run it (brief briefs/en-1.md stands), else skip.
2. Run `python3 .gov-runtime/scratch/lead/verify_c.py` in the background (rebuild-3, select-2, collect-2,
   parallel-2, serial-2 if any, govcheck-2 with node PATH, validator-2, trailers-2, keywords-2; vc.done at end).
3. Known reds: W1-33 guard_and_launcher x4 (red on w2/integrate, nightly's); DEC-906's W1-01 case if selected.
4. Return DONE with the verified head.

## Brief gaps (this run)
- gov launch refuses an engineer on a product-spec ticket though DEC-992 orders one | ticket file / DEC-992 / tool | 5 (meas.)
- the stray worktree-root files were not removed before the resume | common brief | 1 (meas.)
- no unit-test path in the ticket's paths for an engineer's builder tests | ticket file | 3 (est.)
- the W2-11 README map was fenced YAML, which gov accept refuses (ACCEPT_NO_MAP) | skill test-design / this ticket's part | 15 (meas.)
- "run the scenarios on a fresh session" needs writes a read-only subagent cannot make; run as dry runs | skill change / templates/skill.md | 10 (est.)
- /tmp/gov-os-lead-W2-11 is read-only inside the launcher's sandbox (the brief says to use it) | common brief / tool | 2 (est.)
- the brief says the scoped run waits on the copies, and also "verify before you return"; DONE needs both | this ticket's part | 3 (est.)

## Loop
No repair iteration this run.
