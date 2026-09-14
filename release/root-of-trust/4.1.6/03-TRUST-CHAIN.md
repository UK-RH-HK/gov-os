# Output 3 — Trust-chain diagram

> **RoT-1 revision 3 — PROPOSED, pending a fresh independent review; not approved, not implemented.**
> Revision 3 adds:
> - the Constitutional Surface (`23`);
> - freshness anchoring (`24`);
> - binary and trust-base authentication (`25`);
> - legacy-path occupation (`26`);
> - local trust-gate authorisation (`27`).

## 1. The chain

```text
 ═══════════════════════ OFFLINE / OUTSIDE EVERY REPOSITORY (private keys) ════════════════════════════════════════════
  root (k-of-n) ── trust-policy (root keys) ── trust-state ── release-final ── release-candidate ── release-artifact (≥2)
  build-attestation ── verification-attestation ── certification-status ── revocation ── retrieval-profile      (05 §1)
        │ each purpose signs only its own types; compiled pairwise whitelist (05 §3)
        ▼
  trust-root vN · Trust Policy v2 (Constitutional Surface, eligibility + historical releases, bootstrap, lowering history)
  Trust State v2 (prior_states, artifacts) · release (final|candidate) · artefact · build attestation · attestation ·
  certification · revocation · profile                                                          — public, signed
  independent channels: trust_root_id + state fingerprint of every TSS                          — public, unsigned (06 §2)
 ═══════╪══════════════════════════════════════════════════════════════════════════════════════════════════════════════
        │ binaries: reproducible build → build-attestation → artifact-final (release-artifact ×2) → TSS reference (25)
        ▼
  T0  gov binary — compiled Trust Base Manifest names: root chain, TPS (surface, floors, bootstrap), TSS, embedded release;
      compiled code: purpose table, schemas, floor-ops/2, precedence lattice, command register, layout reader
        │   accepted only by verify-artifact A1–A10 or built from source at a verified tag; first run: TBM ≥ VTS high-water
        │
        │  knowledge K = T0 ∪ VTS ∪ PTR ∪ bundle ∪ refresh   (verified only; union; availability untrusted)
        │  anchors  = pin (TA-9) · human confirm-state (TA-5) · witness (OP-7 c, TA-7) · retained        (24 §3)
        │  effective root · TPS (prior_policies, computed lowering) · TSS (resolution → orphans → equivocation → admissibility)
        │  negative set (MS-2) · trust_state axis · freshness axis                                     (17 §5, 24 §4)
        ▼
  authenticate(SourceRef): read once → SV-1…SV-10 → V8 identity → V9 content → V10 migrations → V11 compatibility
        ▼
  T1  AuthenticatedRelease (memory only; CI)
        │  E7 surface: every file/leaf classified · pinned registered · floors vs named TPS · precedence per key   (23, 19 §6)
        │  E1–E6, E8 trust state KNOWN + freshness ANCHORED/WITNESSED + release-local references, E9 downgrade
        │  authorise: install-authority and actor levels from joined policy (never the target) · trust gate confirmed LOCALLY
        │             (terminal challenge or operator decision pin; never a repository record) · computed weakenings gated (27)
        ▼
  install transaction (.governance-runtime/trust-tx, VTS-registered): stage from blobs → read-back + nlink → exchange
        governance/trust (union state/root) → migrations → lock last (inside trust) → layout occupation → snapshot CI
        equality → strength vector recorded
        ▼
  PPS  governance/trust/** · occupation entries (governance/kernel, project, generated = files; framework.lock = dir;
       spec/audits/GOVERNANCE-ADOPTION; .governance-runtime/migration) · trust-tx
        │  every unit of work: installation state (incl. occupation) → KernelSnapshot generation check (VU-11)
        ▼
  POLICY ROOT = KernelSnapshot if verified ∧ eligible (incl. E7), else EmbeddedSnapshot
  EFFECTIVE POLICY = root kernel with every floor leaf ⊔ effective TPS · pinned only if registered · precedence joined per
                     key · overlay after join · exceptions never relax floor/pinned/members/precedence or compiled prefixes
        ▼
  USE  operation class C0–C3 permitted by trust_state × freshness × OP-7 (24 §4.3); consumers read snapshot bytes;
       agents get content from gov (18 §12); derived artefacts bound to CI + policy digest
```

## 2. Where each attack class is stopped

```text
 ─────────────────────────────── before any trusted write ─────────────────────────────────────────────────────────
 tampered or regenerated source (V-H3, E1)                  V9                                    RELEASE_DIGEST_MISMATCH
 forged / wrong-purpose / historical-type statement           SV-2, SV-6                            STATEMENT_TYPE_UNKNOWN / PURPOSE_NOT_GRANTED
 authentic release with weakened unfloored content (R2-H1)    E7 surface                            RELEASE_INELIGIBLE(floor_violation | surface_*)
 unknown constitutional key or file                           E7 default deny                       RELEASE_INELIGIBLE(surface_unclassified)
 precedence reorder / exception_relaxable on security keys    E7 precedence lattice                 RELEASE_INELIGIBLE(precedence_weakened)
 genuine older release below policy / revoked                 E3 / E4                               RELEASE_INELIGIBLE(...)
 stateless verifier fed older genuine state (R2-H2)           E8 freshness                          TRUST_STATE_UNANCHORED / BELOW_ANCHOR
 candidate-key reference inflation (R2-M2)                    S7 release-local                      RELEASE_REFERENCES_UNKNOWN_STATE (that release only)
 unresolvable / forked / equivocating trust state             S4                                    TRUST_STATE_INCOMPLETE / EQUIVOCATION / REGRESSION
 certification-key-only un-withdraw (R2-M3)                   S5 MS-2                               (negative remains)
 skipped-version lowering (R2-M5)                             S3 computed reductions                TRUST_POLICY_UNDECLARED_LOWERING / policy_lowering gate
 A2-committed or plugin-written gate record (R2-M1)           27 local confirmation                 TRUST_GATE_LOCAL_CONFIRMATION_REQUIRED
 malicious or older binary (R2-H3)                            25 A2–A7                              PURPOSE_NOT_GRANTED / ARTIFACT_BUILD_UNATTESTED /
                                                                                                    ARTIFACT_UNREFERENCED / BINARY_T0_UNVERIFIED / BINARY_T0_ROLLBACK
 source swap, symlink, hard link, race                        18 §3, VU-1…VU-4, VU-12               STAGED_CONTENT_CHANGED / PATH_SUBSTITUTION_DETECTED
 incoming release lowers install authority or actor levels    19 §8 (joined ROLES)                  AUTHORITY_DENIED
 signed migration or overlay.prev removes strengthening       19 §9, 20 §5                          weakening trust gate
 ─────────────────────────────── trusted write boundary ────────────────────────────────────────────────────────────
 post-install edit / race                                     snapshot per unit of work             KERNEL_TAMPERED / SNAPSHOT_GENERATION_STALE
 Git-delivered forged set                                     use-time authentication               KERNEL_UNAUTHENTICATED
 Git-delivered legacy kernel or layout                        installation state LEGACY; E1         KERNEL_INELIGIBLE(historical)
 Git-delivered older eligible release                         E7 + joins; E10; freshness (OP-7)     KERNEL_INELIGIBLE(downgrade_without_transaction) / TRUST_STATE_UNANCHORED
 occupation entry removed                                     installation state                    INSTALL_STATE_PARTIAL(occupation)
 committed install journal                                    VTS registry                          FOREIGN_TRANSACTION_ARTEFACT (ignored)
 pre-RoT binary on a RoT-1 project (R2-H4)                    legacy-path occupation                (legacy) NOT_INSTALLED / IO_ERROR / ADOPTION_NOT_STARTED; no byte written
 overlay weakened outside a transaction                       strength vector                       PROJECT_STRENGTH_WEAKENED
 long-lived process after an update or revocation (R2-M7)     VU-11                                 SNAPSHOT_GENERATION_STALE → reload / refuse
 agent follows rewritten adapter (R2-M8)                      18 §12                                ADAPTER_BODY_MODIFIED
```

## 3. What each artefact may and may not establish

| Artefact | May establish | May never establish |
|---|---|---|
| Trust root | keys, grants, thresholds, key revocation | anything about a release; freshness |
| Trust Policy Statement | Constitutional Surface, floors, eligibility including historical releases, install authority, gating, bootstrap, lowering, unrevocation, chain reset | authenticity; certification; currency on a machine |
| Trust State Statement | the published set at its sequence, including artefact references | a fact not separately signed; currency on a machine (except as an OP-7 (c) witness) |
| Release statement | content identity, compatibility, migrations, release-local references | eligibility; surface registration; certification; binaries; global minimums |
| Artefact statement (`release-artifact` ×2) | binary digests bound to TBM digests | acceptance without build attestation and TSS reference |
| Build attestation | independent reproduction of a binary and its TBM | authenticity |
| Verification attestation | a verdict for one candidate | certification |
| Certification status | CERTIFIED / REJECTED / WITHDRAWN (visible only with attestation and TSS) | authenticity; freshness; lifting a negative alone |
| Revocation | refusal | new trust |
| Anchor (pin, human confirmation, witness) in the VTS | "the published state was at least epoch e at time t" on this machine | anything on another machine; authenticity |
| Trust-gate confirmation in the VTS | authorisation of one trust transition for one project on this machine | anything else |
| `governance/trust/**` in a repository | nothing by presence; its statements once verified | freshness; anchors; authorisation |
| Lock 3.0.0 | a record of the installed identity; hints | authenticity, eligibility, freshness, authorisation |
| Occupation entries | nothing (a barrier for legacy binaries) | any decision |
| Gate records under `spec/decisions/` | T2 evidence; a request for trust gates | any trust decision |
| Journals, `.prev` directories, snapshots | hints, only when VTS-registered | any trust without re-authentication |
| Environment variables, CLI flags | source selection; narrowing | anchors, keys, identity, certification, freshness, authorisation |
