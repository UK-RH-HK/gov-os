# First verifier harness (4.1.2) — implementer rerun for candidate 4.1.5

Harness `release/verification/4.1.2/heldout/harness.py` executed **unchanged** (byte-identical to the verifier's commit) with `GOV_CANONICAL_ROOT` set to this repository and `GOV_VERIFIER_OUT` pointing here. The verifier's own results are untouched.

| Verdict | Verifier run | Rerun (4.1.5) |
|---|---|---|
| PASS | 12 | 36 |
| FAIL | 25 | 1 |
| INFO | 1 | 1 |
| ERROR | 0 | 0 |

| ID | Original | Rerun | Note |
|---|---|---|---|
| HV-01 | FAIL | PASS |  |
| HV-02 | FAIL | PASS |  |
| HV-03 | FAIL | PASS |  |
| HV-04 | FAIL | PASS |  |
| HV-05 | FAIL | PASS |  |
| HV-06 | FAIL | PASS |  |
| HV-07 | FAIL | PASS |  |
| HV-08 | INFO | INFO |  |
| HV-08b | FAIL | FAIL | non-blocker by construction (baseline embedder has no paraphrase capability; D-0006) |
| HV-09 | FAIL | PASS |  |
| HV-10 | FAIL | PASS |  |
| HV-11 | FAIL | PASS |  |
| HV-12 | PASS | PASS |  |
| HV-13 | PASS | PASS |  |
| HV-14 | PASS | PASS |  |
| HV-15 | FAIL | PASS |  |
| HV-16 | FAIL | PASS |  |
| HV-17 | PASS | PASS |  |
| HV-18 | PASS | PASS |  |
| HV-19 | FAIL | PASS |  |
| HV-20 | FAIL | PASS |  |
| HV-21 | FAIL | PASS |  |
| HV-22 | PASS | PASS |  |
| HV-23 | FAIL | PASS |  |
| HV-24 | FAIL | PASS |  |
| HV-25 | PASS | PASS |  |
| HV-26 | FAIL | PASS |  |
| HV-27 | PASS | PASS |  |
| HV-28 | FAIL | PASS |  |
| HV-29 | FAIL | PASS |  |
| HV-30 | PASS | PASS |  |
| HV-31 | PASS | PASS |  |
| HV-32 | PASS | PASS |  |
| HV-33 | FAIL | PASS |  |
| HV-34 | FAIL | PASS |  |
| HV-35 | PASS | PASS |  |
| HV-39 | FAIL | PASS |  |
| HV-36 | FAIL | PASS |  |

Verdict assignment remains the independent verifier's; this rerun is implementer evidence only.
