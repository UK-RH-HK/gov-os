# Output 3 — Trust-chain diagram

## 1. The chain

```text
 ════════════════════════ OFFLINE / OUTSIDE EVERY REPOSITORY ════════════════════════
  root keys (k-of-n, offline)          release key(s)        certification key(s)     profile key(s)
        │ sign                               │ sign                  │ sign                  │ sign
        ▼                                    ▼                       ▼                       ▼
  trust-root metadata vN          release statement         certification statement   profile statement
  (roles, key ids, thresholds)    (identity + all digests)  (statement digest→status) (plugin/runtime/model digests)
        │                                    │                       │                       │
        │ public data only                   └──── shipped inside release bundles, embedded in binaries,
        │                                          copied into consumer governance/trust/ (all signed)
 ═══════╪═══════════════════════════════════════════════════════════════════════════════════
        ▼
  T0  gov binary — compiled-in: trust-root chain v1..vN, revocation floor, statement schemas,
      embedded kernel bytes + embedded release statement (+ legacy-identity statement)
        │
        │  authenticate(SourceRef)   ← the ONLY way to create T1
        │   V1 quarantine read (single read, tree rules)
        │   V2–V7 statement parse, canonical check, signature, role, threshold, revocation, schema
        │   V8–V12 identity, full digest recomputation, migrations, compatibility, downgrade/replay
        │   V13 certification statements
        ▼
  T1  AuthenticatedRelease (in-memory capability; quarantine bytes; zero trusted writes so far)
        │
        │  authorise(ARO, project policy)   ← gates bound to statement digest, authority, OP-3 policy
        ▼
      install transaction  (journal: prepared → staged → swapped → migrated → committed)
        │   stage from quarantine → re-digest → atomic swap → governance/trust/release.dsse.json
        │   → migrations from ARO only → framework.lock (commit point, records identity)
        ▼
  T1-installed   governance/kernel/**  +  governance/trust/{release,certification}.dsse.json
  T2-record      governance/framework.lock  (never read as a trust source)
        │
        │  every process: kernel_trust v2
        │   installed files ≡ statement file map        (integrity  — post-install tampering)
        │   statement signature verifies under T0       (authenticity — Git/snapshot/manual replacement)
        │   not revoked; lock identity ≡ statement      (freshness floor, record consistency)
        ▼
  USE  TrustedKernel → policies, precedence, schemas, roles, adapters, skills, tools, migrations
        │ any failure
        ▼
       authenticated embedded baseline (T0 bytes) + KERNEL_TAMPERED / KERNEL_UNAUTHENTICATED refusals
```

## 2. Where each attack class is stopped

```text
 pre-install tampering  (V-H3, E1, E2)     source ──► authenticate ✗ RELEASE_DIGEST_MISMATCH / RELEASE_STATEMENT_MISSING
 forged statement                          source ──► authenticate ✗ RELEASE_SIGNER_UNKNOWN / SIGNATURE_INVALID
 replay / downgrade                        source ──► authenticate ✗ RELEASE_REPLAY_DETECTED / RELEASE_DOWNGRADE_REFUSED
 poisoned embedded cache (E3)              cache  ──► compiled-in digests ✗ EMBEDDED_BASELINE_CORRUPT (or never read)
 tampered snapshot (E5)                    snapshot ─► authenticate ✗ SNAPSHOT_UNAUTHENTICATED
 interrupted install                       journal ─► recover → previous authenticated state (INSTALL_INTERRUPTED until then)
 ─────────────────────────────── trusted write boundary ───────────────────────────────
 post-install edit (V-H2)                  kernel_trust v2 ✗ KERNEL_TAMPERED (integrity)
 Git-delivered coherent replacement (E4)   kernel_trust v2 ✗ KERNEL_UNAUTHENTICATED (authenticity)
 edited framework.lock                     kernel_trust v2 ✗ LOCK_IDENTITY_MISMATCH (record)
 revoked release / key                     kernel_trust v2 ✗ RELEASE_REVOKED / RELEASE_SIGNER_REVOKED
```

## 3. What each artefact may and may not establish

| Artefact | May establish | May never establish |
|---|---|---|
| Trust-root metadata compiled into the binary | which keys hold which roles; thresholds; revocation floor | anything about a specific release |
| Release statement (verified) | release identity, content digests, compatibility, migrations, update impact | certification; project authorisation |
| Certification statement (verified) | certification status of one statement digest | authenticity of content (it references a digest) |
| Revocation statement (verified) | that keys or releases must not be adopted/used | new trust |
| `governance/trust/*.dsse.json` in a repository | nothing by presence; everything above once verified under T0 | trust when verification fails |
| `framework.lock` | a record of what was adopted, when, from which logical source | authenticity, integrity reference, certification |
| `manifest.json`, `manifest.yaml`, `RELEASE_NOTES.md` | human-readable description | any decision |
| Source `KERNEL_MANIFEST.json` | nothing (ignored; regenerated deterministically from the statement) | any decision |
| Gate records | project authorisation for one statement digest | authenticity |
| Environment variables, CLI flags | source selection; opting into a *lower, labelled* trust state | anchors, identity, certification |
