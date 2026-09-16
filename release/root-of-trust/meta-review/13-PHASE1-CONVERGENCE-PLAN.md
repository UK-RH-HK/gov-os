# Phase-1 convergence plan

## Constraint

No Revision 8, implementation change, D-0008 activation or D-0007 supersession is authorized by this plan.

## Step 0 — Accept this forensic boundary

Owner reviews:

- executive conclusion;
- finding-origin matrix;
- frozen acceptance contract;
- OP dispositions;
- recommended target architecture.

Outcome: accept, amend or reject the rebase proposal.

## Step 1 — Owner decision on scope

Record a new owner decision that explicitly states:

- Phase-1 R0/R1 requirements;
- later R2/R3 requirements;
- bootstrap profile;
- key thresholds/custody;
- metadata freshness/offline behavior;
- CI authorization;
- fate of OP-9/10/12/13/16;
- D-0007/D-0008 transition rule.

Until then, current state remains frozen.

## Step 2 — Standards/design selection

Perform a bounded architecture selection comparing mature signed-update/attestation patterns. Selection criteria:

- supported Rust implementation/library quality;
- canonical metadata and threshold/delegation support;
- rollback/version/expiry semantics;
- offline behavior;
- key rotation/recovery;
- platform support;
- auditability and dependency cost;
- compatibility with existing release bundles and Contract A2.

This is a design choice, not a web-era model/vendor commitment.

## Step 3 — One architecture record, one threat model

After owner approval, create a new architecture decision lineage rather than Revision 8 of CP-1. It must contain:

- fixed R0 contract;
- named bootstrap assumption;
- trust-domain boundaries;
- ingress map;
- metadata/key lifecycle;
- failure/degraded states;
- explicit non-guarantees;
- migration from 4.1.5;
- acceptance test map.

Keep the document set small. Derived schemas/examples must not become independent normative sources.

## Step 4 — Architecture review with provenance gate

Fresh reviewers may block only on R0 requirements. Every finding must state provenance and lifecycle. Hardening proposals are recorded but do not redefine R0 without owner adoption.

Target token: `ROT_ARCHITECTURE_ACCEPTED_R0`.

## Step 5 — Implement bounded R1

Implement the uniform verifier and atomic installer across all ingresses while preserving earlier valid controls. No build-system/high-assurance expansion during this step.

Run builder tests, prior relevant trust-boundary probes and new R1 held-out tests.

## Step 6 — Independent candidate acceptance

Fresh verifier evaluates the exact candidate against Contract v3 plus R1. Capability-contract evidence must distinguish original, post-verification hardening and execution refinements.

Target token: `ROT_PHASE1_CANDIDATE_ACCEPTED_R1`.

## Step 7 — Resume the wider control panel

Only after R1:

- capability baseline/Gate W;
- provisional retrieval profile;
- advanced qualification/G6;
- high-assurance platform certification if owner retained it;
- final release certification;
- remote publication and adoption.

## Convergence controls

- fixed gate contract hash;
- maximum one architecture correction cycle before owner re-adjudication;
- no medium/low architecture blocker without lifecycle justification;
- no claim stronger than tested threat/support envelope;
- no bespoke crypto/protocol primitive when a mature one suffices;
- architecture acceptance and platform certification are separate tokens;
- unresolved later-certification work produces an explicit not-certified status, not endless architecture revision.
