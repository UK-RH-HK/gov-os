# HO-0025 — Handoff for the fresh independent R0 re-review of the corrected SRR-1 candidate

| Field | Value |
|---|---|
| Handoff | HO-0025 |
| From | orchestrator (routing only) |
| To | NEW fresh independent R0 architecture reviewer |
| Corrected candidate | `d34478aa945617a93b1c962fcc363b1c3f835ab3` (correction commit `29516f8`, merged) |
| Prior verdict corrected | AR-0023 `ROT_ARCHITECTURE_REJECTED_R0` (work commit `2dc08c2`) |
| Correction run | AR-0024 `ARCHITECTURE_CORRECTION_READY_FOR_REVIEW` |
| Active gate | `GATE-R0-ARCH-ACCEPT` |
| Required verdict | `ROT_ARCHITECTURE_ACCEPTED_R0` or `ROT_ARCHITECTURE_REJECTED_R0` |

## Independence

You did not author the architecture, the correction, or the AR-0023 review. You are the sole issuer of this verdict.
The orchestrator routes evidence and will not overrule you.

## Pinned inputs and digests — verify each before relying on it

| Input | SHA-256 |
|---|---|
| `release/root-of-trust/signed-release-root-v1/01-FROZEN-R0-R1-R2-R3-ACCEPTANCE-BOUNDARY.md` (FROZEN R0 CONTRACT) | `70977d11b778c4a8391a65cb3e0f53103bcc1e565de595c1e83150797f1699c1` |
| `spec/architecture/ARCH-0003.yaml` (corrected) | `42681978d3a7603da857029e68bd120453bd9ff373b8dea2c4247343a857cfda` |
| `release/root-of-trust/signed-release-root-v1/00-ARCHITECTURE.md` (corrected) | `695aa185ab32a813cd596b12f80d235afb92d56f147f395b15f16e37d0bcd983` |
| `release/root-of-trust/signed-release-root-v1/04-R0-CORRECTION-1.md` (correction record) | `6922fd352219b36acb75395bc03b2a15888d3f801824acf0f878f6a7931a9044` |
| `Governance_OS_Capability_Acceptance_Contract_v3.md` (owner source) | `4c2df29115c8d5389034b2e2d817772add80d61678807c23e0d520c937cb5ed3` |
| `GATES/OWNER-DECISION-0006-BELOW-FLOOR-RECOVERY.md` | `903407729327d67c198c9bf97885a936c5601993e16ad76137a3106c5728d1db` |
| `GATES/OWNER-DECISION-0005-R0-REVIEW-ANSWERS.md` | `3831cbf51d6f663299a3a338d85bd07bed662fd33e5392502d4f270ce87e36fa` |

A hash mismatch is a STOP condition. Report it; do not work around it.

## Scope

1. **Rerun the prior blockers.** `SRR-R0-H1` and `SRR-R0-M1` in
   `release/root-of-trust/signed-release-root-v1-review-r0/10-BLOCKING-FINDINGS.md`, plus the AR-0023 probe set in
   `.../evidence/PROBES.md`. Re-run them against the corrected text and state, per blocker, whether it is CLOSED or
   still OPEN, with evidence.
2. **Author fresh held-out R0 attacks** of your own, within the frozen R0 boundary. Do not merely re-execute AR-0023.
   Attack the *new* text hardest: the ingress-wide floor rule, the intact-versus-admissible distinction, the break-glass
   authority and its non-manufacturability, the revoked-binary reconciliation, the offline authenticity basis, and the
   declared time assumption and its two-directional non-guarantee.
3. **Verify the owner requirements are actually met.** All ten `OWNER-DECISION-0006` requirements must be stated in
   architecture text, not merely in the correction record. The correction record is a map, not the architecture.
4. **Check the correction did not smuggle scope.** Confirm it stayed within CD-R0-1 and CD-R0-2, did not weaken any
   previously satisfied R0 item, and did not route later-lifecycle conditions into R0.
5. **Disclosed judgement call to check:** AR-0024 did not fix `SRR-R0-L8` (traceability table maps 11 of 14 R0 items)
   but re-pointed two existing rows whose target sections moved. Verify those re-points are accurate.

Everything uncontested at AR-0023 — trust chain, metadata model, role table, domain-separation table, ingress set,
transaction invariant, bootstrap assumption, CI/headless model, D-0007 transition rule, non-goals — should not be
reopened without cause. If you find cause, say so explicitly with evidence.

## Classification rule — mandatory for every finding

State: exact normative source; provenance class (ORIGINAL_NORMATIVE / OWNER_ADDED_NORMATIVE / NECESSARY_DERIVED /
IMPLEMENTATION_CHOICE / VERIFIER_HARDENING / LATER_QUALIFICATION / NEW_OWNER_DECISION_REQUIRED / OUT_OF_SCOPE);
lifecycle/gate; whether it **falsifies an existing claim** or merely **proposes stronger assurance**; and the
security/availability/usability/cost consequence.

A finding blocks R0 only if its normative source and lifecycle are R0, or it proves an R0 claim internally
inconsistent. Do NOT promote R1/R2/R3 hardening into R0 blockers. `SRR-R0-L6` is owner-deferred to R1 and must not be
raised as an R0 blocker; `SRR-R0-L7` is owner-closed as out of scope.

Not required at R0: production ceremonies, DDC/diverse compilers, supplier independence, reproduction quorum,
multi-source first contact, public/cloud/hostile-admin assurance, Gate W/G6 completion, platform certification.

## Loop limit — read this carefully

The single permitted bounded R0 correction cycle has been used. No further correction cycle is authorised.

- If the corrected architecture satisfies the frozen R0 acceptance rule, return `ROT_ARCHITECTURE_ACCEPTED_R0`.
- If it does not, return `ROT_ARCHITECTURE_REJECTED_R0` with findings classified as above. Mark clearly, for each
  blocker, whether it is (i) a **residual** of `SRR-R0-H1`/`SRR-R0-M1` the correction failed to close, or (ii) a
  **genuinely new** architecture/security requirement or owner trade-off. The orchestrator uses that distinction to
  decide owner escalation. Do not soften a real defect to avoid escalation, and do not invent one to force it.

## Prohibitions

No implementation. No authoring of a replacement architecture or a further correction delta beyond a bounded statement
of what remains unclosed. No RoT-1 Revision 8, no CP-1 resumption, no D-0007/D-0008/ARCH-0002 change. Do not modify
product source, the frozen boundary, prior review evidence or any historical record. Do not read session/agent
transcripts or task-output stores. Do not contact the product owner.

## Deliverables

Evidence under `release/root-of-trust/signed-release-root-v1-review-r0-2/`:
`00-REVIEW-REPORT.md`, `10-BLOCKING-FINDINGS.md` (empty or absent if none), `20-LATER-LIFECYCLE-CONDITIONS.md`,
`evidence/` with `REVIEWED-CONTENT-DIGESTS.txt` and your probes. Commit that, then write
`release/orchestration/phase-1/AGENT_RUNS/AR-0025.report.yaml` per the `AGENT_RUNS/README.md` schema with
`output.commit` naming the work commit, and commit it separately. A run without a durable committed report is
INCOMPLETE and advances no gate.
