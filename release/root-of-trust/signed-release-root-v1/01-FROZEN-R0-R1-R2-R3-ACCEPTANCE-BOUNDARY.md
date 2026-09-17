# Frozen Signed Release Root acceptance boundary

## Status and authority

`OWNER-FROZEN BY OWNER-DIRECTIVE-0004`

This is the gate contract for ARCH-0003. It derives from the original three Governance OS documents, Capability Acceptance Contract v3, D-0009, OWNER-DIRECTIVE-0004 and the forensic meta-review. It replaces the meta-review's proposed frozen contract as the owner-adopted boundary for this new lineage. It does not alter historical RoT-1 evidence.

## Normative hierarchy

1. Product-owner decisions and the authoritative Capability Acceptance Contract v3.
2. Original Governance OS governing documents for original mission and invariants.
3. D-0009 and this frozen lifecycle boundary.
4. D-0007 while active during transition.
5. ARCH-0003 as the R0 candidate architecture.
6. Review evidence, which tests requirements but does not create them.

When sources differ, the later explicit owner decision governs the changed point while preserving unaffected original requirements.

## Finding provenance

Every finding must use exactly one primary provenance class:

- `ORIGINAL-NORMATIVE`
- `OWNER-ADDED-NORMATIVE`
- `NECESSARY-DERIVED`
- `IMPLEMENTATION-CHOICE`
- `VERIFIER-HARDENING`
- `NEW-OWNER-DECISION-REQUIRED`
- `LATER-QUALIFICATION/CERTIFICATION`
- `OUT-OF-SCOPE / UNSATISFIABLE-AS-STATED`

## R0 — Root/Release Architecture Acceptance

R0 proves only that the architecture, within its private/local support envelope, coherently specifies:

1. the pre-existing platform/admin bootstrap assumption;
2. signed root, delegation and release/targets metadata;
3. binding of release identity, exact payloads and migrations;
4. key delegation, rotation and revocation semantics;
5. one verification policy across init, adopt, update, reinstall, rollback and recovery;
6. verified-byte/use binding;
7. private staging, atomic commit and crash-safe architectural outcome;
8. signed rollback floors and protected local high-water;
9. local authority/Human Gate and headless-policy boundaries;
10. explicit stale, expired and offline states without false revocation knowledge;
11. separation of authenticity, installed integrity, build provenance, certification, project policy and plugin/retrieval trust;
12. local OS/admin/time/network assumptions and explicit non-guarantees;
13. preservation of the original Governance OS mission and Contract v3 capabilities;
14. D-0007 remaining active and non-circular first-install authenticity being supplied outside its manifest/lock.

### R0 acceptance

`ROT_ARCHITECTURE_ACCEPTED_R0` requires:

- every R0 item above is explicit, internally consistent and testable at later gates;
- no unresolved CRITICAL/HIGH defect that falsifies an R0 normative guarantee;
- no unresolved MEDIUM that requires architecture change to meet an R0 guarantee;
- every carried R1/R2/R3 concern is labelled with its correct lifecycle;
- no private key, production ceremony or implementation is required as evidence;
- the verdict identifies the exact reviewed Git commit and document hashes.

### Not required at R0

Production signatures or custody ceremonies; final library/algorithm selection; runtime code; DDC; supplier diversity; reproduction quorum; multi-source first contact; public/cloud/hostile-admin assurance; completed Gate W/G6 qualification evidence.

## R1 — Phase-1 Implementation Candidate

R1 later proves on one exact candidate:

- a mature reviewed TUF/cryptographic implementation is used correctly;
- candidate/source files cannot create their own trusted identity;
- wrong keys, modified metadata/payload/migration, replay, downgrade and expiry fail closed;
- all privileged ingress paths call the common verifier;
- verified bytes are staged, installed and used without substitution;
- staging/install/rollback/recovery are atomic and crash-safe on supported filesystems;
- metadata/release high-water is durable and monotonic;
- post-install integrity remains distinct and D-0007 controls remain effective;
- project, CLI, environment, model and plugin inputs cannot create trust or approval;
- CI/multi-machine provisioning follows ARCH-0003;
- the original product controls, Gate W and G0–G6 implementation mappings remain valid;
- builder evidence and fresh independently authored held-out evidence pin the exact candidate.

`ROT_PHASE1_CANDIDATE_ACCEPTED_R1` is issued only by the designated fresh independent candidate-verification process after R0.

## R2 — Standard Release Certification

R2 later requires, as applicable to the exact standard release:

- production signatures and key-custody evidence;
- two genuinely independent verification records;
- supported-platform clean install/update/rollback/recovery evidence;
- private-remote publication and clean-clone/install smoke;
- key rotation/revocation drill;
- SBOM, licences and build provenance bound to artifact digest;
- current capability evidence;
- Gate W dependency/consumption evidence;
- G6 and release qualification required by Contract v3;
- adoption/support envelope and residual-risk statement.

`ROT_STANDARD_RELEASE_CERTIFIED_R2` certifies only the named candidate, target and profile.

## R3 — Optional High-Assurance Platform Qualification

R3 alone contains:

- OP-9 independent reproducibility quorum;
- OP-10 DDC/diverse compiler/bootstrap assurance;
- OP-13 multi-source first-contact ceremony;
- OP-16 independent supplier/environment classes;
- cross-axis supplier/toolchain compromise tests;
- enhanced organizational-independence audit;
- extensive root, recovery and air-gap ceremonies.

Until satisfied, the platform state is:

`STANDARD RELEASE — HIGH-ASSURANCE TOOLCHAIN PROFILE NOT CERTIFIED`

R3 failure does not invalidate R0/R1/R2 or ordinary Governance OS capability operation.

## Finding intake contract

Every future finding must state:

1. exact normative source and clause;
2. original-baseline yes/no and current-owner-approved yes/no;
3. provenance class;
4. lifecycle/gate: R0, R1, R2, R3, implementation, qualification or operations;
5. explicit claim falsified, or that it merely proposes stronger assurance;
6. security, availability, usability and cost impact;
7. reproducible evidence or bounded design counterexample;
8. owner decision needed, if any.

A finding blocks the active gate only when its normative source and lifecycle match that gate. A reviewer may recommend stronger security but cannot promote it into a requirement. Any material new security, availability, cost, usability or product-scope requirement needs explicit owner adoption.

## Change control

Changing this boundary requires a new product-owner decision. Reviewer reports, implementation convenience, library limitations or inherited CP-1 language cannot silently amend it. No rejection of ARCH-0003 may be routed into RoT-1 Revision 8.
