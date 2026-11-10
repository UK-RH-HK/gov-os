# W2-141's staged hook rebuilt on ACT-SETS-GLOBS-1's hook: the rehearsal record (DECIDED-NOT-DONE row 78)

`rehearsal.log` beside this file is the run of `rehearse.sh`, 2026-11-10 00:08–00:45 GMT, from a fresh `env -i` shell,
**0 failures**. Nothing live changed (`out/live-before.txt` = `out/live-after.txt`); 63,160 hook lines went to the
rehearsal's own call log, 0 to the live one. The real sets root was never opened, listed or stat'ed.

## The rebuild (commit `beec1f2f8`)
- The first staged `pretooluse.py` (`7c8a6e8d9dbf`) was made from `bd545af83198` (`15952bbfa`, ACT-GUARD-SETS-1),
  not from `97a84e770058` as row 78 first said. Its only change was `"Glob"` in G-14's tool list (diff: 2 lines).
  Applied as it stood, it would have taken out ACT-INDEP-WALLS-1, ACT-GUARD-CALLLOG-1, ACT-OPERATOR-1 and
  ACT-SETS-GLOBS-1.
- Rebuilt: the live hook `74f8dbea4761` (`9cce7430d`) with the same one word: `e7e1c4ce66d6`. `role_reads.py`'s copy
  (`b1bc1745f80c`) stands, its live file unchanged (`5407aade9417`).
- The D-10 restage engineer did the same in parallel (`9536ea954` on `w2/W2-141-d10`). Both files are byte for byte
  the same there and in `beec1f2f8`, so merging it is clean.

## Results
| Step | Before (live hook) | After (staged pair) |
|---|---|---|
| `tests/unit/guard/test_w2_141_search.py` (main tree) | the pin case, run alone: 1 failed (the base moved); the D-10 helper's whole run at `adb4f6b4c`: 203 passed, 1 failed | **204 passed** (no test changed) |
| `gov accept W2-141` (pin `bcea09060ebc`) | — | **184 passed, 0 failed, 0 skipped** |
| `sets_globs_check.py` (planted HOME, SG_EXPECT=after) | 573 run, 0 failed, PASS | **573 run, 0 failed, PASS** |
| `walls_check.py repo` | 331, 0 failed | **331, 0 failed** |
| `guard4_check.py --settings` | 501, 0 failed | **501, 0 failed** |
| `test_guard_fix_4` | 467 passed | 467 passed |
| `test_g14` (drafts/g14) | 150 passed, 1 skipped, 1 failed (`test_w2_91_tests_today`, red at this head) | 146 passed, 1 skipped, 5 failed: that one plus 4 engineer near-miss cases, searches from above (`grep -rn x tests/acceptance`, Glob `tests/acceptance/**`, Grep of the root, `grep -r foo tests/`): S1/S2's intended refusals |
| `test_live_hook` + `test_reads` | 85 passed | 85 passed |
| Replay 48 h (00:08:21 11-08 .. 11-10), 14,569 unique calls, under DAEO-sdxk | 14,483 allow, 86 deny | **0 changed** |
| The same, under DAEO-xwro (W2-141's ticket) | 14,482 allow, 87 deny | **29 allow→deny, 0 deny→allow**: engineer Grep 23, Bash `grep -r` 6, each "the search can reach tests/acceptance/W2-141/" (W2-141's S1/S2) |
| Latency, median per call (20 rounds × 7 calls × 2 roles) | 147.3 ms | 168.0 ms (load 13–16 on 20 CPUs; per-call rows move together) |

## For the lift's re-pin ACT
- `drafts/g14/test_g14.py`'s four `ENGINEER_PASSED` cases "a search of the whole acceptance folder (from above)",
  "Glob lists names", "Grep from above" and "grep -r from above" encode the rule W2-141 changes. They are revised with
  the ACT (as `test_live_hook.py`'s `G14_PASSED` case was in W2-141), or the ACT's g14 step expects them red.
- `guard4_check.py`: 501/0 with the staged pair, so its case `sets G5` did not trip here (its engineer's ticket has no
  acceptance folder with files in the clone).
