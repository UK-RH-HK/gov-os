# Third verifier harness (4.1.4) — implementer rerun for candidate 4.1.5

Harness `release/verification/4.1.4/heldout-v3/harness_v3.py` executed **unchanged** (byte-identical to the verifier's commit) from a fresh `git clone` of tag `v4.1.5-rc1`, with `GOV_CANONICAL_ROOT` set to that clone and `GOV_VERIFIER_OUT` pointing here. The verifier's own results are untouched.

| Verdict | Verifier run | Rerun (4.1.5) |
|---|---|---|
| PASS | 13 | 14 |
| FAIL | 3 | 2 |
| INFO | 0 | 0 |
| ERROR | 0 | 0 |

| ID | Original | Rerun | Note |
|---|---|---|---|
| VV-01 | PASS | PASS |  |
| VV-02 | PASS | PASS |  |
| VV-03 | FAIL | PASS |  |
| VV-04 | FAIL | PASS |  |
| VV-05 | PASS | FAIL | pinned to the 4.1.4 candidate identity (released KERNEL.yaml must equal the working tree's); 193 files scanned, the only duplicate key is in the frozen 4.1.3 payload; 4.1.5 equivalent: repair3::current_release_payload_identity_and_hygiene |
| VV-06 | PASS | PASS |  |
| VV-07 | PASS | FAIL | pinned to the 4.1.4 candidate identity (HEAD must carry the v4.1.4-rc1 tag); verification, reproduction from the recorded commit, immutability and provenance all pass; 4.1.5 equivalent: repair3::current_release_payload_identity_and_hygiene |
| VV-08 | PASS | PASS |  |
| VV-09 | PASS | PASS |  |
| VV-10 | PASS | PASS |  |
| VV-11 | PASS | PASS |  |
| VV-12 | PASS | PASS |  |
| VV-13 | PASS | PASS |  |
| VV-14 | FAIL | PASS |  |
| VV-15 | PASS | PASS |  |
| VV-16 | PASS | PASS |  |

Verdict assignment remains the independent verifier's; this rerun is implementer evidence only.
