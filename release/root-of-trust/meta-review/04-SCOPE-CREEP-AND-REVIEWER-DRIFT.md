# Scope creep and reviewer drift

## Findings

### 1. Historical scope expansion is proven

The original baseline required hashes and immutable release records, not cryptographic source authenticity. The stage-control panel later added a dedicated non-circular root-of-trust architecture stage, release envelopes/signatures, bootstrap/key management and attack requirements. Contract v3 explicitly marks A2 as post-verification hardening. This is a documented scope addition.

### 2. Owner adoption prevents a blanket “reviewer scope creep” conclusion

The owner subsequently adopted:

- Contract A2/F4, G0–G6, V and W;
- OP-1…OP-16;
- OT-1/OT-2 clarifications.

After those acts, a reviewer was entitled to test the new guarantees. A requirement absent from the original baseline is not scope creep when the owner has deliberately made it normative.

### 3. Revision 7 was judged against an owner clarification written after it

OWNER-DESIGN-REQUIREMENTS-0002 post-dates the Revision 7 architecture commit. Applying it was correct for the current acceptance target, but it is temporal goalpost movement. It should be recorded as “Revision 7 became stale against a later owner clarification,” not as proof that its author ignored the then-existing brief.

### 4. Reviewer lifecycle drift is also proven

The review process repeatedly treated all discovered concerns as inputs to the next architecture revision. Examples:

- crash-window behavior, atomic high-water files and evidence-runner reproducibility belong to implementation acceptance;
- mutation-killing coverage and full hidden-oracle scoring belong to qualification;
- DDC/toolchain lineage and supplier-class proof belong to platform certification;
- organizational independence of verifier executions needs operational audit, not just architecture text;
- clean headless CI first-use is a product/availability choice.

These concerns are valid, but validity does not determine phase.

### 5. Claim inflation invited legitimate rejection

Revision 7 claimed strong bounds over revocation, freshness, first contact, supplier/toolchain independence and compromise sets. Once those claims were made, reviewers properly tested their counterexamples. Several “new goalposts” were therefore consequences of the architecture's own language, not arbitrary demands.

### 6. The custom protocol multiplied proof obligations

CP-1 introduced custom statement types, thresholds, trust stores, state codes, first-contact codes, operation classes, registers, calculators, admission records, source custodians and environment identities. Every new selector created another authority, freshness, replay, crash and recovery question. The loop's non-convergence is partly structural: the design surface grew faster than the reviews could close it.

## Finding-origin policy for future reviews

Every new finding must include:

1. exact normative source;
2. original-baseline yes/no;
3. current-owner-approved yes/no;
4. provenance class;
5. lifecycle: architecture, implementation, candidate acceptance, qualification, certification or operations;
6. security/availability/usability/cost impact;
7. whether the finding falsifies an explicit claim or merely proposes stronger assurance;
8. owner decision needed, if any.

A finding may block the current gate only when its normative source and lifecycle match that gate.

## Prompt/control-panel assessment

The control panel has strong properties: fresh independence, evidence freshness, no self-certification, exact candidate pinning and explicit repair-loop invalidation. Its problem is scope aggregation.

The root-review and Prompt 2 instructions ask one verifier to judge:

- full Governance OS capability completeness;
- non-circular cryptographic bootstrap;
- every privileged ingress;
- key rotation/revocation/recovery;
- compiler and build provenance;
- retrieval architecture/model selection;
- advanced fixture readiness;
- current and future supply-chain integration.

The phrase “repair until accepted” plus no fixed requirement-provenance gate allowed later findings to become automatic next-revision inputs. The revised workflow should require a provenance/lifecycle adjudication before any repair loop is authorized.

### Prompt and step findings

| Control-panel element | Intended function | Forensic effect | Recommended treatment |
|---|---|---|---|
| Prompt 1 and Rust/polyglot amendment | Build the broad canonical OS | Ambitious but substantially traceable to the original baseline; building many pillars together increased defect density | Historical only, as V5 already says |
| Root-of-Trust architecture escalation/review | Close 4.1.5 V-H3 before implementation | Correctly added independent authenticity, but one prompt aggregated bootstrap, every ingress, offline behavior, rotation/recovery, adversarial cases and future retrieval-profile trust | Replace with the fixed R0 contract; review only architecture guarantees at this step |
| Root implementation step | Implement only an accepted design | Sound gate ordering | Retain after a new owner-approved architecture; do not use for CP-1 Revision 8 |
| Owner contract upload and compiled-contract integration | Prevent an IDE agent inventing owner requirements; bind source to executable evidence, G0–G6 and Gate W | Strong authority control and explicit owner addition | Retain; keep the owner source distinct from generated views |
| Prompt 2 | Fresh comprehensive candidate verification and held-out test authorship | Combined architecture completeness, security, memory, retrieval selection, capability evidence, G0–G6 and Gate W in one release-candidate gate | Split R1 candidate checks from later capability baseline/qualification; require provenance and lifecycle on every blocker |
| “Repair until OS_RELEASE_CANDIDATE_ACCEPTED” | Iterate until the exact candidate passes | With no change-budget or scope-adjudication gate, every valid concern could become automatic Phase-1 work | Permit one bounded correction cycle; then require owner re-adjudication |
| Phase 2 CAP-1 | Audit the full capability baseline before sophisticated tests | Correct later capability gate; it should not retroactively redefine the release-authentication architecture | Retain as a separate gate after R1 |
| Phases 3–5 PR/AQ/retrieval prompts | Bootstrap retrieval, run hidden two-repository qualification, then select the reference profile | Good lifecycle separation in principle; source-change escape rules correctly invalidate stale evidence, but qualification discoveries must not automatically become new architecture requirements | Retain with defect routing by provenance/lifecycle |
| Phase 6 Prompt 3 and remote smoke | Certify and publish the exact accepted bundle | Correct release-certification stage | Retain as R2, after candidate and qualification gates applicable to the release |
| Phases 7–9 Prompts 4–14 | Freeze legacy repositories and independently plan, execute, verify and audit adoption | Closely follows the original adoption protocol and belongs after release certification | Retain; do not use adoption readiness to block R0 |
| Phase 10 ongoing health | Periodic/post-change capability health and upstream learning | Owner-added lifecycle control in Contract v3, not an original Phase-1 architecture criterion | Retain as operations/G0–G5 health, with G6 at qualification |

The browser checkboxes and locally saved notes are orchestration aids, not normative approvals or cryptographic evidence. Authority comes from the referenced records, exact candidate identities and signed/committed evidence—not the UI's local completion state.

## Bottom line

- **Architectural drift:** yes, substantial.
- **Unapproved reviewer-created product scope:** yes, but limited mainly to phase/lifecycle elevation and some implementation choices.
- **Owner-approved new scope:** yes, and it accounts for most of CP-1's breadth.
- **Revision 7 rejection valid against CP-1:** yes.
- **Revision 7 rejection proof that the original Governance OS failed its original architecture:** no.
- **Next action:** owner rebase, not Revision 8.
