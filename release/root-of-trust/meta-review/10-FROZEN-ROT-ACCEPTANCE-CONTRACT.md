# Frozen Root-of-Trust acceptance contract

## Status

`PROPOSED_FOR_OWNER_ADOPTION_BY_META_REVIEW`

This document freezes the recommended Phase-1 boundary so another reviewer cannot silently expand it. It is not active until the product owner explicitly adopts it. It does not activate D-0008 or supersede D-0007.

## Gate definitions

### Gate R0 — Architecture acceptance

Architecture is acceptable when all of the following are explicit and internally coherent:

1. **Bootstrap assumption:** the authentic root public key/fingerprint reaches a machine through a named pre-existing trusted act/channel.
2. **Signed metadata:** canonical release metadata binds product/version, payload digests, supported platform, expiry/version/sequence, key IDs and required migration identity.
3. **Delegation/rotation:** offline root authority can delegate, rotate and revoke release-signing keys without trusting the repository being judged.
4. **Ingress coverage:** init, adopt, update, reinstall, recovery and rollback call the same verification policy before privileged staging.
5. **Verify/use binding:** installed and executed/enforced bytes are the bytes verified; staging is atomic and fails closed.
6. **Rollback protection:** local monotonic state prevents silent downgrade below a signed security minimum; recovery behavior is defined.
7. **Local authorization:** human/admin gates are local authority; repository gate records cannot authorize trust operations.
8. **State honesty:** authentic-but-stale/unknown is distinct from current; offline operation never implies knowledge of unseen revocation.
9. **Trust-domain separation:** release authenticity, build provenance, certification, project policy and retrieval/plugin trust are distinct.
10. **Threat/support envelope:** OS/admin/time/network assumptions and unsupported platforms/modes are stated.

Architecture acceptance does not require production keys, production signatures, a certified platform, DDC evidence, two supplier classes, or final operational ceremonies.

### Gate R1 — Phase-1 implementation candidate

The exact candidate must demonstrate:

- use of an established, reviewed cryptographic library and canonical format;
- no private signing key in repository, payload, logs or fixtures;
- wrong key, modified payload/metadata, stale/expired metadata, replay/downgrade and forged version fail closed;
- each privileged ingress is covered by a table-driven test;
- source cannot regenerate its own identity;
- post-install tampering is detected separately from source authenticity;
- crash-safe staging/commit/rollback on supported filesystems;
- deterministic errors and audit evidence;
- D-0007 policy precedence, plugin governance and sensitivity controls preserved;
- builder tests plus fresh independent held-out tests;
- exact candidate commit and evidence hashes pinned.

### Gate R2 — Release certification

Certification additionally requires:

- production/ceremony keys and custody evidence appropriate to the adopted profile;
- two independent verifier records if OP-8 remains active;
- supported-platform clean-install/update/rollback/recovery evidence;
- key rotation/revocation drill;
- remote publication/clean-clone smoke;
- SBOM, provenance, licenses and support statement;
- no unresolved critical/high finding for this gate;
- current Contract v3 evidence for A2 and affected capabilities.

### Gate R3 — High-assurance platform qualification

Only this gate requires OP-9/10/13/16-style evidence:

- independent reproduction quorum;
- evidenced toolchain bootstrap/DDC-equivalent criterion;
- supplier-class independence evidence;
- multi-source first-contact ceremony if retained;
- chaos/soak/hidden-oracle attacks;
- organizational independence audit;
- explicit platform label.

Failure at R3 yields `NOT CERTIFIED — TOOLCHAIN ASSURANCE INCOMPLETE`; it does not retroactively falsify R0 architecture acceptance.

## Explicit non-requirements for R0/R1

- no proof of absolute absence of compiler compromise;
- no proof of current global revocation while offline and unrefreshed;
- no inference of organizational independence from key IDs;
- no mandatory custom admitter, C0–C3 calculus, full selector register or supplier×toolchain cross-product;
- no platform certification claim without evidence;
- no requirement that every later Contract V/G6 qualification challenge already pass at architecture review.

## Change control

A reviewer may propose stronger security. It becomes blocking only after provenance classification shows it is original normative, owner-added normative or necessary-derived for an already accepted guarantee, and its lifecycle matches the active gate. Material security/availability/cost/usability changes require owner adoption.

## Acceptance tokens

- `ROT_ARCHITECTURE_ACCEPTED_R0`
- `ROT_PHASE1_CANDIDATE_ACCEPTED_R1`
- `ROT_RELEASE_CERTIFIED_R2`
- `ROT_PLATFORM_HIGH_ASSURANCE_CERTIFIED_R3`

Tokens are exact-candidate/profile scoped and become stale under the evidence-freshness rules of Contract v3.
