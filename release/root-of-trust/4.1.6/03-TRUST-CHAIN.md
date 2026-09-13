# Output 3 — Trust-chain diagram

> **RoT-1 revision 2 — PROPOSED, pending a fresh independent review; not approved, not implemented.**
> Revision 2 adds currency (eligibility and floors), monotonic trust state, purpose separation, byte binding, the
> protected-path writer rule and the trust-format boundary.

## 1. The chain

```text
 ═══════════════════════ OFFLINE / OUTSIDE EVERY REPOSITORY (private keys) ═══════════════════════
  root (k-of-n) ── trust-policy (root keys) ── trust-state ── release-final ── release-candidate
  verification-attestation ── certification-status ── revocation ── retrieval-profile          (05 §1)
        │ sign: each purpose signs only its own statement types (05 §2), key sets constrained (05 KS-1…KS-7)
        ▼
  trust-root vN · Trust Policy (floors, eligibility, install authority, gating) · Trust State (published set)
  release (final|candidate) · attestation · certification · revocation · profile       — public, signed
 ═══════╪═════════════════════════════════════════════════════════════════════════════════════════
        │ carried by: binaries (compiled) · bundles · governance/trust/ (PTR) · Verifier Trust Store · refresh
        ▼
  T0  gov binary — compiled: root chain, newest TPS, newest TSS + referenced statements, historical-identity
      registry, purpose table + separation constraints, statement schemas, floor operators,
      EmbeddedSnapshot + its statement, trust-format reader versions
        │
        │  knowledge set K = T0 ∪ VTS ∪ PTR ∪ bundle ∪ refresh     (verified statements only; availability untrusted)
        │  effective root · effective TPS · admissible TSS · negative set N · required minimums      (17 §5)
        ▼
  authenticate(SourceRef)        ← the only constructor of T1 release material                        (04)
     secure reader: read once → VerifiedBlobs (18 §1)
     SV-1…SV-10 purpose-bound signature checks (05 §4)
     V8 identity + lineage + stage · V9 every blob digest = RCS(D) · V10 migration chain · V11 compatibility
        ▼
  T1  AuthenticatedRelease (memory only; CI = (D, tree_digest))
        │
        │  currency   (19 §6)  E1 release purpose · E2 stage · E3 min sequence · E4 not revoked · E5 binary
        │                      E6 lineage · E7 floors registered · E8 trust state not STALE · E9 downgrade authorised
        │  authorise  (19 §8, 17 §7, 21 OP-3) authority floor from T0/TPS ⊔ current eligible kernel (never the target)
        │                      gate bound to D (mode A: always) · computed weakenings gated (19 §9)
        ▼
  install transaction (18 §5): exclusive lock · stage from blobs · read-back re-digest · atomic exchange
        │                      · migrations from blobs · lock last (commit point) · post-commit snapshot CI equality
        ▼
  PPS  governance/kernel/** · governance/trust/** · governance/framework.lock · governance/.tx/**
       writable only with InstallTxToken (GovernedFs, 18 §8); lock = record; KERNEL_MANIFEST.json = tombstone
        │
        │  every process: installation state machine (18 §9) → KernelSnapshot (18 §6)
        │    read once through secure reader · files ≡ statement (integrity) · statement under T0 (authenticity)
        │    eligibility E1–E7, E10 (currency) · trust-state view (17 §6) · lock ≡ statement (record)
        ▼
  POLICY ROOT = KernelSnapshot            if verified ∧ eligible
              = EmbeddedSnapshot           otherwise (read-only except remedies)
  EFFECTIVE FLOOR = TPS_effective ⊔ policy root ⊔ overlay-strengthening                         (19 §5)
        ▼
  USE  consumers read snapshot bytes only; derived artefacts bound to CI (18 VU-7, VU-8)
```

## 2. Where each attack class is stopped

```text
 ─────────────────────────────── before any trusted write ───────────────────────────────
 tampered source, stale or regenerated manifests (V-H3, E1)    V9 blob digests ≠ RCS              RELEASE_DIGEST_MISMATCH
 self-labelled CERTIFIED manifest (E2)                         manifests never read; gate mode A  (no effect)
 forged statement / unknown key                                SV-6                               SIGNER_UNKNOWN
 wrong-purpose key (cert key signs a release)                  SV-6                               PURPOSE_NOT_GRANTED
 historical identity supplied by a bundle or repository        SV-2                               STATEMENT_SOURCE_NOT_PERMITTED
 statement of another lineage / test profile                   SV-10                              STATEMENT_LINEAGE_MISMATCH / TRUST_PROFILE_MISMATCH
 replay under another version / mixed releases                 V8, V9                             RELEASE_IDENTITY_MISMATCH / RELEASE_DIGEST_MISMATCH
 genuine older release below policy                            E3                                 RELEASE_INELIGIBLE(below_min_release_sequence)
 revoked genuine release                                       E4 (sticky N)                      RELEASE_INELIGIBLE(revoked)
 stale CERTIFIED without WITHDRAWN / omitted REJECTED          17 §6–§7: no view relaxes (mode A)  HUMAN_GATE_REQUIRED
 stripped TSS/TPS/root link referenced by signed statements    17 S7–S9                           TRUST_STATE_STALE / TRUST_ROOT_STALE
 signed trust-state regression                                 17 S4                              TRUST_STATE_REGRESSION
 incoming release lowers install authority                     19 §8                              AUTHORITY_DENIED (from floor)
 signed migration removes project strengthening                19 §9                              OVERLAY_WEAKENING_GATE_REQUIRED
 source swapped after verification / symlinks / races          18 VU-1…VU-4, §3                   STAGED_CONTENT_CHANGED / RELEASE_TREE_INVALID
 poisoned or substituted cache (E3)                            no cache on any trust path          (nothing read)
 tampered or ineligible snapshot (E5)                          20 §2–§4                           SNAPSHOT_UNAUTHENTICATED / SNAPSHOT_INELIGIBLE
 forged journal planting an older genuine release              20 §5                              RELEASE_INELIGIBLE / HUMAN_GATE_REQUIRED
 CIT / adoption / recovery write to protected paths            18 §8 GovernedFs                   PROTECTED_PATH_WRITE_REFUSED / CIT_PROTECTED_PATH
 ─────────────────────────────── trusted write boundary ───────────────────────────────
 post-install static edit (V-H2)                               18 §6 step 5                       KERNEL_TAMPERED
 post-verification byte swap (review R2b)                      snapshot bytes only (VU-7)          (swap has no effect on this process)
 Git-delivered forged or regenerated set (E4)                  18 §6 step 3                       KERNEL_UNAUTHENTICATED
 Git-delivered genuine legacy kernel (review R1)               E1 / installation state             KERNEL_INELIGIBLE(historical) / INSTALL_STATE_PARTIAL
 Git-delivered genuine older eligible release                  floors from TPS; E10 on known machines  KERNEL_INELIGIBLE(downgrade_without_transaction)
 partial deletion of protected paths                           18 §9                              INSTALL_STATE_PARTIAL
 edited framework.lock                                         record cross-check                  LOCK_IDENTITY_MISMATCH
 pre-RoT binary opens a RoT-1 project                          13 §3 format boundary               4.1.5: KERNEL_TAMPERED (sentinel text)
```

## 3. What each artefact may and may not establish

| Artefact | May establish | May never establish |
|---|---|---|
| Trust root (compiled or chained) | keys, purpose grants, thresholds, key revocation | anything about a release; freshness |
| Trust Policy Statement | floors, eligibility, install-authority floor, gating mode, lowering, unrevocation | authenticity; certification |
| Trust State Statement | which separately signed statements form the published state at sequence n | a certification or revocation not separately signed; freshness beyond its own sequence (except mode B expiry) |
| Release statement (final/candidate) | content identity, compatibility, migrations, signed references to root/policy/state current at signing | eligibility; certification; authority to install itself |
| Verification attestation | an independent verdict for one candidate digest | certification; authenticity |
| Certification status | CERTIFIED / REJECTED / WITHDRAWN for one final digest (visible as CERTIFIED only with attestation + TSS reference) | authenticity; freshness |
| Revocation | refusal of named digests | new trust |
| Historical-identity registry (compiled only) | that a tree digest is a known legacy release | eligibility; policy-root status |
| `governance/trust/**` in a repository | nothing by presence; its statements once verified | freshness; eligibility on its own |
| Verifier Trust Store | verified knowledge; lineage confirmation; per-project high-water | anything unverifiable; trust against A3 |
| `framework.lock` | a record of the installed identity; hints about required metadata | authenticity, integrity reference, eligibility, freshness |
| `KERNEL_MANIFEST.json` | nothing (compatibility tombstone for pre-RoT binaries) | any decision |
| `manifest.json`, `manifest.yaml`, release notes | human-readable description | any decision |
| Update ledger, gate records (Git-tracked T2) | evidence; authorisation against A1/A3/A5 | currency, freshness or downgrade decisions against a repository writer (D-0008 rule 18) |
| Journal, `.tx/*.prev`, snapshots | hints about which candidate states to evaluate | any trust without re-authentication and eligibility |
| Environment variables, CLI flags | source selection; opting into a lower labelled state; narrowing (lineage pin) | anchors, keys, identity, certification, freshness |
