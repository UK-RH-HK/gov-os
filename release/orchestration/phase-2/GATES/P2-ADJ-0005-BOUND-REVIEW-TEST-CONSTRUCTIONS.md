# P2-ADJ-0005 — Orchestrator adjudication: the remaining review constructions are updated, and one moot test is re-pointed

| Field | Value |
|---|---|
| Record | Orchestrator adjudication (**not** an owner decision; the owner may override) |
| Date | 2026-09-21 |
| Raised by | P2-AR-0071, which retired the subjectless-review fallback under P2-ADJ-0004 and then correctly **reported** six failing tests instead of adjusting files outside its mandate |
| Extends | P2-ADJ-0004 |

## What P2-AR-0071 found

Retiring the fallback left the tree at 225 passed / 6 failed of 231. Every failure is a test whose **construction** wrote a
subjectless review and relied on it authorising an installation:

- `tests/certification/r2_toolbind.rs` — `a_pinned_script_installs_ungated_and_a_hash_drift_afterwards_is_refused_not_executed`,
  `negative_controls_still_install_ungated_with_zero_gate_records`, and
  `moving_the_installed_descriptor_aside_does_not_rearm_a_subjectless_review`.
- `tests/certification/r4_residual.rs` — `a_tool_installation_is_gated_for_each_way_it_expands_authority`,
  `ordinary_allowlisted_network_use_does_not_gate_but_a_new_boundary_does`, and
  `an_installation_whose_envelope_changed_after_simulation_is_refused_at_the_write`.

None is a defect in the repair. Each asserts something still true — a pinned script installs ungated, allowlisted network
use alone does not gate, an envelope change is refused at the write — but each builds its precondition with a review that
no longer authorises anything.

## Ruling

1. **Update the constructions, preserve the assertions.** Those six tests may have their review construction changed to
   name `subject_sha256`, exactly as P2-AR-0071 did for the flagship `ws07` test: split the descriptor build from the
   write if needed, compute the digest with `gov_runtime::tools::review_subject`, and leave **every assertion byte-for-byte
   unchanged**. If any of them cannot pass with a bound review, that is a finding about the repair — stop that item and
   report it rather than relaxing the test.
2. **`moving_the_installed_descriptor_aside_does_not_rearm_a_subjectless_review` is re-pointed, not deleted.** Its premise
   (the single-use fallback could be re-armed) no longer exists, but the property underneath it still matters and is now
   *stronger*: moving an installed descriptor aside must not let an unbound review authorise anything. Keep the test name,
   rewrite its body to assert that stronger fact, and note the change with these records named. Deleting a test remains
   prohibited.
3. **Names stay as they are.** P2-AR-0071 discovered the hard way that renaming even one mapped test breaks the evidence
   map (`CONTRACT_EVIDENCE_OWNER_UNRESOLVED` for F3/F4, and a puzzling second failure in an unrelated update/rollback
   test, both downstream of the one rename). `r2_wsa::an_unbound_review_is_still_held_to_a_single_installation` therefore
   keeps a name that now understates what it proves — it asserts outright refusal. Recorded as cosmetic debt: a future
   round may rename it **together with** an evidence-map regeneration, which is integration work, not repair work.

## Scope limit

This authorises construction changes in those two files and the one re-pointed body, and nothing else. Any further test
that turns out to depend on the retired fallback is again a finding to report.
