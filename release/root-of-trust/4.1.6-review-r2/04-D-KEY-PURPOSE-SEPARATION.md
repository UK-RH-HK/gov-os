# D — Key-purpose separation

## 1. Required attempts

| # | Attempt | Revision 2 control | Result |
|---|---|---|---|
| D-1 | Certification key signs release authenticity | SV-5/SV-6 `PURPOSE_NOT_GRANTED`; KS-3 forbids the grant | **closed** |
| D-2 | Candidate key signs a final or certified release | the `release-final` payloadType needs a `release-final` grant; a stage mismatch fails SV-9; KS-6 | **closed** (owner-visible exception: OP-4 "no" puts both purposes on one key) |
| D-3 | Retrieval-profile key signs a Trust Policy | `trust-policy` needs root keys at root threshold (KS-2) | **closed** |
| D-4 | Historical-identity statement supplied outside the binary | SV-2 `STATEMENT_SOURCE_NOT_PERMITTED`; it confers only `HISTORICAL_IDENTIFIED`, never eligible | **closed**. RV-H4 is resolved. |
| D-5 | Key-id substitution | key id recomputed from `public_key` (SV-4); duplicate public keys refused (KS-7); threshold counts distinct valid keys (SV-7) | **closed** |
| D-6 | Algorithm or type confusion | algorithm taken from the key record; Ed25519 only; payloadType ↔ purpose ↔ `_type` compiled; PAE binds the payloadType | **closed** |
| D-7 | Root key used below or above its scope | KS-1: root keys may additionally hold only `trust-policy`; dual-threshold chain | **closed** |
| D-8 | Replay of a revoked or rotated key | `SIGNER_REVOKED` wherever root N+1 is known | Closed with retained state or a surviving reference. On a stateless verifier: R2-H2. |

## 2. New purpose failures found

### 2.1 R2-H3 — the TCB is authenticated by the release-final purpose alone

- `05` §2 maps `artifact-final.v1` to the `release-final` purpose, with 1 active key, threshold 1, by default (OP-2).
- `06` §2 step 6: "Subsequent binaries are authenticated by the previous one (5a)". R-BOOT-4 checks lineage and the root
  high-water only.
- `schemas/artifact-statement.schema.json` has no field for the binary's compiled T0:
  - root version;
  - TPS version or digest;
  - TSS sequence;
  - historical-registry digest;
  - embedded release statement digest.

  The claim in `06` §2 step 6 that a new binary "must carry a root chain … whose version is ≥ the VTS high-water"
  therefore cannot be checked without running the candidate binary.
- A certification binds `release_statement_digest` (`07` §4), never an artifact digest. "Certification follows
  verification of the built binary" (`06` §2 step 4) has no mechanical counterpart. No attestation, certification,
  trust-state reference or gate is required to accept a binary.
- `05` §1 lists the impact of a stolen `release-final` key as "authentic finals can be forged. Eligibility floors, the
  install gate (OP-3 mode A) and certification … still apply". It omits binary forgery.
- A forged binary *is* the trusted computing base. It bypasses every floor, gate, eligibility rule and trust-state rule
  for every consumer who follows the documented upgrade path.
- Under OP-4 "no", the key used several times a day for candidates also signs binaries.

### 2.2 R2-M2 — non-trust-state purposes assert trust-state minimums

- `17` S7 builds `RM_state`, `RM_policy` and `RM_root` from `trust_references` in release statements (final **and**
  candidate) and from `issued_under` in certification statements.
- A key of those purposes therefore asserts "trust state n exists and you must hold it", which is a trust-state fact.
- Values are unbounded and the result has no override. Executed: P4-B1 and P4-B4 (see `02`).

### 2.3 R2-M3 — certification-status alone lifts negative facts

S5 uses the highest `certification_sequence` regardless of attestation or TSS reference (P4-B2). A single certification
key can therefore reverse WITHDRAWN or REJECTED refusals. This contradicts MS-2 and the "three independent signatures"
design of `17` §3.

### 2.4 R2-M6 — separation constraints are incomplete

- KS-1…KS-7 never mention `trust-state`. A single key may hold `trust-state` together with `certification-status` or
  `verification-attestation`.
- The "Permitted only by explicit grant" list (`05` §3) is not stated as a compiled whitelist. The binary checks only
  KS-1…KS-7.
- The OP-2 recommended matrix (`21`) allows `certification-status`+`revocation` and `revocation`+`trust-state`. One
  owner token may therefore hold certification, revocation and trust-state together, which collapses the "three
  independent signatures" of a visible CERTIFIED into two keys.
- Impact in mode A is limited (certification relaxes nothing). In mode B it is direct.

## 3. What one stolen key can do (revision 2 as written)

| Purpose stolen alone | Pack's impact claim (`05` §1) | Worst case found by this review |
|---|---|---|
| `release-final` | forge authentic finals; floors, gate and certification still apply | **forge binaries for upgraders (H3)**; A2 Git delivery makes a forged final the policy root with no gate, carrying chosen unfloored content (H1); inflated references freeze ingress (M2) |
| `release-candidate` | candidates only | global no-override ingress freeze, not cleared by revoking the statement (M2); binaries too under OP-4 "no" (H3) |
| `verification-attestation` | a verdict alone certifies nothing | confirmed |
| `certification-status` | CERTIFIED needs two more signatures | lifts WITHDRAWN/REJECTED refusals (M3); inflated `issued_under` freezes ingress (M2) |
| `revocation` | denial of service only | confirmed |
| `trust-state` | withholding only; regressions rejected | inflated references make every honest successor a REGRESSION, refusing governed mutations at use (M2) |
| `retrieval-profile` | profile integrity only | confirmed |
| one `root` key | nothing below threshold | confirmed |
