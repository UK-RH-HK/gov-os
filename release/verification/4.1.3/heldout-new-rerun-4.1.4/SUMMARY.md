# Second verifier harness (4.1.3) — implementer rerun for candidate 4.1.4

Harness `release/verification/4.1.3/heldout-new/harness_v2.py` executed **unchanged** (byte-identical to the verifier's commit) with `GOV_VERIFIER_OUT` pointing here and `GOV412_WORKTREE` set to a 4.1.2 binary built from commit `8ad06be` in a detached worktree; the verifier's original results are untouched.

| Verdict | Verifier run | Rerun (4.1.4) |
|---|---|---|
| PASS | 6 | 13 |
| FAIL | 9 | 2 |
| INFO | 0 | 0 |
| ERROR | 0 | 0 |

| ID | Original | Rerun | Severity (rerun) | Title |
|---|---|---|---|---|
| NV-01 | FAIL | PASS |  | CIT approval/execution require a presented AND answered gate; a human decline (option B) stops the t |
| NV-02 | FAIL | PASS |  | project overlay policy_overrides cannot silently lower AUTHORITY_POLICY levels or empty SECURITY_POL |
| NV-03 | FAIL | PASS |  | genuine 4.1.2 consumer (created by the 4.1.2 binary) updated to release 4.1.3 by the 4.1.3 binary, v |
| NV-04 | FAIL | PASS |  | plugin descriptors (arbitrary commands) are governed like tools: registration/approval, version pin, |
| NV-05 | FAIL | PASS |  | task close cross-checks the self-reported files_changed against the actual working-tree changes (git |
| NV-13 | PASS | PASS |  | control: a framework-update gate answered B (decline) stops `update --apply --approve` and the lock  |
| NV-19 | FAIL | FAIL | MEDIUM | migration M-4.1.2-4.1.3 operations perform what its description and the release notes claim (overlay |
| NV-06 | PASS | PASS |  | paraphrase retrieval obtained end-to-end through the governed mechanism (benchmark >= 3 candidates o |
| NV-07 | FAIL | PASS |  | a governed record survives an incremental rebuild after being moved (git mv) within spec/ |
| NV-08 | FAIL | PASS |  | framework.lock.release_commit identifies the framework release commit (manifest.release_commit), and |
| NV-09 | FAIL | FAIL | LOW | KERNEL.yaml is strict-YAML valid (no duplicate mapping keys) and schema_versions agree across KERNEL |
| NV-10 | PASS | PASS |  | a pinned reranker's scores govern the final ranking (not just invoked) and are exposed per hit |
| NV-12 | PASS | PASS |  | after an embedder pin change without rebuild, gov continue / context compile fail closed (EMBEDDER_M |
| NV-16 | PASS | PASS |  | release 4.1.3 identity: verify ok, payload == kernel data at manifest.release_commit (ancestor of th |
| NV-17 | PASS | PASS |  | an external embed plugin never receives secret-class, secret-content or restricted-class text (API-0 |

Verdict assignment remains the independent verifier's; this rerun is implementer evidence only.

Residuals: NV-09 and NV-19 evaluate the immutable 4.1.3 payload (`release/releases/4.1.3/kernel/...`) and cannot change verdict without mutating a released payload; the repaired state for 4.1.4 is covered by `tests/certification/repair2.rs::interface_contract_kernel_yaml_and_migration_substance_are_consistent`.
