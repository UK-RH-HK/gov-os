# OWNER-DIRECTIVE-0004 — Adopt the Signed Release Root rebase

| Field | Value |
|---|---|
| Record | OWNER-DIRECTIVE-0004 |
| Source | product owner, Phase 1 orchestration chat, 2026-09-17 |
| Classification | **binding owner architecture and assurance-boundary decision** |
| Decision | Adopt the compact TUF-style Signed Release Root direction and retire CP-1 as the Phase-1 target |
| Direction token | `ADOPT_A_TUF_STYLE_SIGNED_RELEASE_ROOT_WITH_PLATFORM_TRUSTED_BOOTSTRAP__KEEP_D0007_TRUST_DIRECTION__SEPARATE_PHASE1_RELEASE_CERTIFICATION_AND_OPTIONAL_HIGH_ASSURANCE_QUALIFICATION__RETIRE_CP1_AS_THE_PHASE1_TARGET` |
| New records | D-0009; ARCH-0003 |
| Next gate | R0 — fresh independent architecture review |

## Owner decision

Governance OS is initially a privately operated, locally hosted engineering/governance system used by the product owner on controlled machines and private repositories. Phase 1 is not a public multi-tenant cloud/SaaS or general-purpose high-assurance supply-chain product.

Security protects the Governance OS mission: governed repository truth, deterministic authority, Human Gates, CIT-P/CIT-E, task DAG/readiness/checkpoints, the Development Knowledge Fabric, governed skills/tools/plugins, independent verification, safe lifecycle operations, Gate W, G0–G6, recovery, observability, learning and adoption across multiple private repositories. This rebase must not redesign unrelated working capabilities.

The Phase-1 root-of-trust target is:

```text
trusted platform/admin bootstrap
  -> embedded or pre-installed offline root public keys
  -> signed root/delegation metadata
  -> signed release/targets metadata
  -> one verifier used by every privileged ingress
  -> private verified-byte staging
  -> atomic installation plus local monotonic high-water
  -> post-install integrity verification
```

Use a mature TUF-style metadata/update model and reviewed cryptographic implementation. The architecture must cover init, adopt, update, reinstall, rollback and recovery. A project repository may pin an authenticated release identity but cannot establish its trust root.

## Support envelope

R0/R1 may assume an uncompromised local OS, administrator and bootstrap boundary on the owner's controlled machines. Public, commercial, enterprise and high-assurance threat profiles are later profiles. The assumption is explicit and testable; it is not recursively eliminated by material delivered through the repository being judged.

## Decision and evidence disposition

- D-0007 remains ACTIVE during transition. Its trust-direction, precedence, Human Gate, plugin, exception, integrity and typed-refusal rules remain normative.
- D-0007's manifest and `framework.lock` remain post-install integrity and release-pin records; they are not the first-install authenticity root.
- D-0007 is not superseded or amended unless ARCH-0003 passes R0 and a later transition record explicitly authorises that change.
- CP-1 is retired as the Phase-1 target. No RoT-1 Revision 8 is permitted and the CP-1 repair loop is not resumed.
- D-0008 and ARCH-0002 remain non-active proposed/historical evidence. They are not activated or silently mutated.
- RoT-1 revisions 1–7, their independent reviews, attacks and threat research remain immutable high-assurance research evidence.
- D-0009 records this active owner direction. ARCH-0003 is the new, separate R0 review candidate; it is not active implementation architecture until fresh R0 acceptance.

## Assurance lifecycle

- **R0 — architecture:** signed-release/authentication architecture and declared private/local support envelope only.
- **R1 — implementation candidate:** mature library, fail-closed verifier at every ingress, byte binding, atomic/crash-safe lifecycle, high-water, post-install integrity and fresh independent candidate evidence.
- **R2 — standard release certification:** production signatures/custody, two independent verification records, supported-platform lifecycle tests, private publication smoke, rotation/revocation drill, SBOM/licences/provenance, capability evidence, Gate W and G6/release qualification as applicable.
- **R3 — optional high assurance:** reproducibility quorum, DDC/diverse compiler bootstrap, multi-source first contact, supplier independence, cross-axis compromise tests, enhanced independence audits and extensive ceremonies.

An unmet R3 condition produces exactly:

`STANDARD RELEASE — HIGH-ASSURANCE TOOLCHAIN PROFILE NOT CERTIFIED`

It does not invalidate R0, R1 or the standard Governance OS product.

## Freshness, CI and authority

- Standard signed root, targets/release, snapshot and timestamp metadata provide versions and expiry; operational durations are profile parameters, not constitutional constants here.
- Clients retain the highest valid metadata/minimum secure release observed and refuse rollback below local high-water.
- Stale/expired metadata blocks trust-changing lifecycle operations according to policy; it does not automatically brick an already authenticated installation.
- Offline clients report currency as stale/unknown and never claim knowledge of unseen revocations.
- CI and additional machines are pre-provisioned with the verifier, public root metadata and protected machine policy outside the governed project repository.
- Repository files, environment variables, caller fields, plugins and models cannot manufacture trust or Human Gate approval.

## Review governance

The frozen acceptance boundary at `release/root-of-trust/signed-release-root-v1/01-FROZEN-R0-R1-R2-R3-ACCEPTANCE-BOUNDARY.md` governs future reviews. Every finding must state its normative source, provenance, lifecycle/gate, claim effect and material trade-offs. A finding blocks only when its normative source and lifecycle match the active gate. Stronger security proposals require owner adoption before becoming requirements.

## Immediate effect

This directive authorises governance/architecture records and a fresh independent R0 review only. It authorises no runtime, kernel, CLI, capability or migration implementation, no production key ceremony, no D-0008 activation and no D-0007 supersession.
