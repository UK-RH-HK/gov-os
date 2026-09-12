# Second verifier harness (4.1.3) — implementer rerun for candidate 4.1.5

Harness `release/verification/4.1.3/heldout-new/harness_v2.py` executed **unchanged** (byte-identical to the verifier's commit) from a fresh `git clone` of tag `v4.1.5-rc1`, with `GOV_CANONICAL_ROOT` set to that clone and `GOV_VERIFIER_OUT` pointing here; `GOV412_WORKTREE` provided a 4.1.2 binary built from commit `8ad06be`. The verifier's own results are untouched.

| Verdict | Verifier run | Rerun (4.1.5) |
|---|---|---|
| PASS | 6 | 13 |
| FAIL | 9 | 2 |
| INFO | 0 | 0 |
| ERROR | 0 | 0 |

| ID | Original | Rerun | Note |
|---|---|---|---|
| NV-01 | FAIL | PASS |  |
| NV-02 | FAIL | PASS |  |
| NV-03 | FAIL | PASS |  |
| NV-04 | FAIL | PASS |  |
| NV-05 | FAIL | PASS |  |
| NV-13 | PASS | PASS |  |
| NV-19 | FAIL | FAIL | reads the immutable 4.1.3 payload; repaired in 4.1.4/4.1.5 (confirmed by the third verifier, VV-06) |
| NV-06 | PASS | PASS |  |
| NV-07 | FAIL | PASS |  |
| NV-08 | FAIL | PASS |  |
| NV-09 | FAIL | FAIL | reads the immutable 4.1.3 payload; repaired in 4.1.4/4.1.5 (confirmed by the third verifier, VV-05) |
| NV-10 | PASS | PASS |  |
| NV-12 | PASS | PASS |  |
| NV-16 | PASS | PASS |  |
| NV-17 | PASS | PASS |  |

Verdict assignment remains the independent verifier's; this rerun is implementer evidence only.
