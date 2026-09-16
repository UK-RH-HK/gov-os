# Recommended target architecture

## Outcome

Adopt a small, standards-shaped release-authentication core and layer build provenance/certification above it. Do not continue the bespoke CP-1 Revision 7 lineage.

## Trust chain

```text
pre-installed / independently verified offline root public keys
                          |
                          v
              signed root/delegation metadata
                          |
                          v
             delegated release metadata/signature
       (version, sequence/expiry, payload and migration digests)
                          |
                          v
             one verifier used by every ingress
                          |
                          v
             measured bytes in private staging area
                          |
                          v
              atomic install + local high-water
                          |
                          v
            installed-byte integrity at use time
```

Build provenance, independent verifier attestations, SBOMs and reproducibility reports are signed evidence referenced by release/certification records. They do not replace the root → release authorization chain.

## Components

### 1. Offline root/delegation metadata

- Root public keys are installed through a named trusted bootstrap act.
- Root metadata defines thresholds, release roles, key rotation and metadata versions.
- A 2-of-3 offline root is reasonable if the owner retains OP-1.
- Prefer a mature update-framework metadata model and library rather than custom signature/state semantics.

### 2. Release metadata

The delegated release role signs canonical metadata binding:

- product/repository identity;
- release version and monotonically increasing sequence;
- supported platform/architecture;
- exact payload/tree and binary digests;
- schema/migration identities;
- minimum allowed release/security version;
- metadata expiry or refresh policy;
- optional references/digests for provenance, SBOM, verification and certification evidence.

### 3. Uniform verifier

One library/API evaluates every privileged ingress. The caller receives typed values such as `AuthenticatedRelease` and never a raw source directory. Source path, repository files, locks and CLI claims are not authority.

### 4. Atomic installer

- opens/reads bytes safely into private staging;
- verifies exact bytes and metadata before any protected write;
- installs from verified handles/buffers;
- records release identity and local monotonic high-water;
- verifies committed bytes;
- supports journaled rollback/recovery;
- keeps post-install integrity checking separate.

### 5. Currency and revocation

- Signed metadata versions, expiry and revocations are monotonic.
- Online/connected operations refresh metadata according to policy.
- Offline operation may continue only within the accepted cached-metadata policy and never claims knowledge of unseen state.
- Stale metadata yields explicit degraded/read-only/refused behavior by operation class.
- Avoid inventing a second mutable “currentness” protocol unless the product truly needs near-real-time revocation.

### 6. Local trust gates

- Trust decisions bind to exact release/root/security-minimum digests.
- Repository files may request but never answer gates.
- Headless CI uses a separately approved provisioned policy/token or is excluded from privileged lifecycle work. This needs owner selection.

### 7. Build/certification evidence

- Use established provenance/attestation formats where practical.
- Two independent verifier records remain certification evidence.
- Reproducible build, supplier diversity and DDC evidence are evaluated by a high-assurance certification policy.
- A release can be authentic but uncertified; the UI/state must show both axes.

### 8. Existing Governance OS controls

The new verifier/installer must preserve policy precedence, plugin registry/byte binding, governed exceptions, sensitivity classes, CIT gates, overlay preservation, immutable releases, memory rebuildability and evidence freshness.

## Bootstrap profiles

The owner should approve at least one concrete profile:

| Profile | Bootstrap | Trade-off |
|---|---|---|
| Managed workstation | administrator/MDM installs root and verifier | best enterprise control; external admin trust assumed |
| Manual fingerprint | operator verifies root fingerprint through independent channel | portable; human ceremony and usability cost |
| OS/package trust | platform package signature installs root/verifier | simpler; platform vendor becomes accepted root dependency |
| High assurance | two separately custodied sources plus root ceremony | strongest operational separation; expensive and later-certification oriented |

The architecture can support several profiles, but the initial certified profile must select one and state assumptions. Unlike Revision 1–6, optional modes must not all be reasoned about at once.

## Why this converges

- It satisfies Contract A2 without making build provenance the distribution root.
- It states the first-trust assumption instead of trying to derive it.
- It uses signed metadata version/expiry semantics instead of a custom universal trust-state calculus.
- It moves DDC/supplier independence to the gate where evidence exists.
- It sharply reduces custom statement types, selectors and crash-recovery states.
- It gives reviewers a fixed, provenance-scoped acceptance contract.

## Owner decisions before implementation

1. approve this smaller phase boundary or retain CP-1;
2. select bootstrap profile;
3. choose root/release thresholds and custody model;
4. decide headless CI authorization;
5. choose freshness/expiry versus offline availability;
6. decide whether OP-9/10/13/16 remain a later high-assurance profile.

No implementation should start before those decisions are recorded.
