# CONTROL-A: why this subject was chosen (R1-CTRL, orchestrator)

The subject is the governed evidence map and `gov contract verify`: why renaming a certification test breaks
verification, which requirement demands an evidence owner, where that is enforced, and which tests prove it.
BR-ARCH-RULING-2 records the choice.

The subject meets the REPAIR-1 §9 criteria. The evidence is `baseline/selection-greps.out`, from `git grep` at
`3c880d8` and `6e7a2a3`:

* **It spans at least 3 top-level directories.** It touches `cli/` (main.rs), `runtime/` (contracts.rs, release.rs,
  scheduler/catalogue.rs), `framework/` (contracts/, schemas/), `tests/` (governance/capability-evidence-map.yaml,
  certification/r2_wsa.rs, ws01r4.rs) and `release/` (Phase-2 GATES).
* **At least one decision record is involved.** `release/orchestration/phase-2/GATES/PHASE-2-FROZEN-GATE-CONTRACT.md`
  (AC-10, AC-13), and `P2-ADJ-0005-BOUND-REVIEW-TEST-CONSTRUCTIONS.md`.
* **At least one test file is involved.** `tests/certification/r2_wsa.rs`, `tests/certification/ws01r4.rs`, and
  `tests/governance/capability-evidence-map.yaml`.
* **It is not a Review-8 subject**, since it has no connection to floor composition, path rules or the sandbox
  exemption. **It is not CTRL-1..3**, which cover the signed release root, plugin registration and
  control-panel/Phase-1/stop-condition lineage.

This control is **visible** to builders. The held-out control, CONTROL-B, is chosen only when R1-MB is dispatched.
