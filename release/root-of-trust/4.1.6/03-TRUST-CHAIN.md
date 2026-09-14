# Output 3 — Trust-chain diagram

> **RoT-1 revision 7 — PROPOSED, pending fresh independent reviews; not approved, not implemented.**
> Revision 7: the certified production profile CP-1 (`35`) governs this file. Where the text below names an owner option
> other than the CP-1 selection, the freshness-witness purpose, a platform signing path, OP-3 mode B or the revision-6
> first-contact manifest, that text is non-production history: the mode is excluded and absent or refused (`35` §4). Parameters
> are the CP-1 values (`35` §2); consequence statements are the CS7 blocks of `21`, `30`, `32`–`34`.
> (Revision 6 banner follows.)
> Revision 6 amendment: the chain of record is `25` §6 as amended in revision 6. First contact is selected by the agreed
> first-contact code over the OP-13 sources (`32`); build environments are registered and reproduced first-hand (`33`);
> registered content is derived first-hand and verification is bound to the registered candidate and kernel (`34`).
> Revision 5 amendment: the chain of record is `25` §6 (registration selects source, inputs, content and final; a first-hand
> reproduction quorum establishes bytes; the selected Trust State selects publication and negatives; `gov-admit` or an
> admitted `gov` evaluates over measured bytes). Rows below that name `release-artifact`, build attestations or first-binary
> tooling paths are superseded by `25`, `30` and `31`.
> Revision 4 changes the chain in five places:
> - anchors are satisfied by inclusion, and trust ingress needs a currency proof (`24`);
> - a binary's source is the source an independent verification attested (`25` §5.1);
> - precedence comes only from registrations, registered content must be present, and the project layer is a directed
>   join (`23`, `19` §5);
> - repository- and plugin-supplied commands run confined (`24` §3.5);
> - project strength is evaluated over effective policy (`26` §6).

## 1. The chain

```text
 ═══════════════════════ OFFLINE / OUTSIDE EVERY REPOSITORY (private keys) ════════════════════════════════════════════
  root (k-of-n) ── trust-policy (root keys) ── trust-state ── release-final ── release-candidate ── release-artifact (≥2)
  build-attestation ── verification-attestation ── certification-status ── revocation ── retrieval-profile ── freshness-witness (05 §1)
        │ each purpose signs only its own types; compiled pairwise whitelist (05 §3)
        ▼
  trust-root vN · Trust Policy v2 (surface: exact precedence, presence, Overlay Surface; eligibility + historical + production sources; bootstrap)
  Trust State v2 (prior_states, artifacts) · release (final|candidate, source) · artefact · build attestation (source) · attestation (source) ·
  certification · revocation · profile · freshness witness                                     — public, signed
  independent channels: trust_root_id + state fingerprint of every TSS                          — public, unsigned (06 §2)
 ═══════╪══════════════════════════════════════════════════════════════════════════════════════════════════════════════
        │ binaries: ACCEPTED attestation names source S → final (V8: same S) → build from S → build-attestation → artifact-final (×2) → TSS ref (25)
        ▼
  T0  gov binary — compiled Trust Base Manifest names: root chain, TPS (surface, floors, bootstrap), TSS, embedded release;
      compiled code: purpose table (12), schemas, floor-ops/3, two-directional order, YAML profile, command register, layout reader; TBM binary.source
        │   accepted only by verify-artifact A1–A10 (A4b attested source, A7 accepted-TBM high-water, A9 currency) or built from attested source
        │
        │  knowledge K = T0 ∪ VTS ∪ PTR ∪ bundle ∪ refresh   (verified only; union; availability untrusted)
        │  anchors  = protected pin with valid_until (TA-9) · human or in-gate confirmation (TA-5) · retained           (24 §3)
        │  satisfied only by INCLUSION of the anchored (sequence, digest) in the effective chain                        (24 §3.4)
        │  currency proof = anchoring event within window · in-gate typed fingerprint · witnesses ≥ 2 (OP-7 c)          (24 §4.4)
        │  effective root · TPS (prior_policies, computed lowering) · TSS (resolution → orphans → equivocation → admissibility)
        │  negative set (MS-2, lift attestation names the negative) · trust_state · freshness · currency axes (17 §5, 24 §4)
        ▼
  authenticate(SourceRef): read once → SV-1…SV-11 → V8 identity + source equality → V9 content → V10 migrations → V11 compatibility
        ▼
  T1  AuthenticatedRelease (memory only; CI)
        │  E7 surface: classified · present · YAML profile · pinned registered · floors vs named TPS · precedence = registration · migrations whitelisted
        │  E1–E6, E8 trust state KNOWN + anchors by inclusion + currency proof + release-local references, E9 downgrade
        │  authorise: install-authority and actor levels from joined policy (never the target) · trust gate confirmed LOCALLY
        │             (terminal challenge + typed fingerprint, or protected expiring decision pin; never a repository record) · weakenings over effective policy gated (27)
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
  EFFECTIVE POLICY = root kernel with every floor leaf ⊔ effective TPS · pinned only if registered (else registered embedded value or SURFACE_VALUE_UNAVAILABLE)
                     · project layer = REGISTERED precedence (⊔ held registration) as a directed join · exceptions registered-relaxable only
        ▼
  USE  operation class C0–C3 permitted by trust_state × freshness × currency × OP-7 (24 §4.3); consumers read snapshot bytes;
       agents get content from gov (18 §12); derived artefacts bound to CI + policy digest; repository commands run confined (24 §3.5)
```

## 2. Where each attack class is stopped

```text
 ─────────────────────────────── before any trusted write ─────────────────────────────────────────────────────────
 tampered or regenerated source (V-H3, E1)                  V9                                    RELEASE_DIGEST_MISMATCH
 forged / wrong-purpose / historical-type statement           SV-2, SV-6                            STATEMENT_TYPE_UNKNOWN / PURPOSE_NOT_GRANTED
 authentic release with weakened unfloored content (R2-H1)    E7 surface                            RELEASE_INELIGIBLE(floor_violation | surface_*)
 unknown constitutional key or file                           E7 default deny                       RELEASE_INELIGIBLE(surface_unclassified)
 any precedence change / deleted registered file              E7 exact registration + presence      RELEASE_INELIGIBLE(precedence_unregistered | surface_required_missing)
 genuine older release below policy / revoked                 E3 / E4                               RELEASE_INELIGIBLE(...)
 stateless verifier fed older genuine state (R2-H2)           E8 freshness + currency               TRUST_STATE_UNANCHORED / BELOW_ANCHOR / CURRENCY_UNPROVEN
 higher unchained TSS; stale pin; minted witness (RV3-H2)      24 §3.2–§3.4                          BELOW_ANCHOR / PIN_OUTSIDE_VALIDITY / PURPOSE_NOT_GRANTED
 candidate-key reference inflation (R2-M2)                    S7 release-local                      RELEASE_REFERENCES_UNKNOWN_STATE (that release only)
 unresolvable / forked / equivocating trust state             S4                                    TRUST_STATE_INCOMPLETE / EQUIVOCATION / REGRESSION
 certification-key-only un-withdraw (R2-M3, RV3-M1)           S5 MS-2 lift attestation              (negative remains)
 skipped-version lowering (R2-M5)                             S3 computed reductions                TRUST_POLICY_UNDECLARED_LOWERING / policy_lowering gate
 A2-committed or plugin-written gate record (R2-M1)           27 local confirmation                 TRUST_GATE_LOCAL_CONFIRMATION_REQUIRED
 malicious or older binary (R2-H3, RV3-H3)                    25 A2–A7, V8 source                   PURPOSE_NOT_GRANTED / ARTIFACT_BUILD_UNATTESTED / ARTIFACT_SOURCE_* /
                                                                                                    RELEASE_IDENTITY_MISMATCH(source) / ARTIFACT_UNREFERENCED / BINARY_T0_UNVERIFIED / BINARY_T0_ROLLBACK
 source swap, symlink, hard link, race                        18 §3, VU-1…VU-4, VU-12               STAGED_CONTENT_CHANGED / PATH_SUBSTITUTION_DETECTED
 incoming release lowers install authority or actor levels    19 §8 (joined ROLES)                  AUTHORITY_DENIED
 signed migration or overlay.prev removes strengthening       Overlay Surface whitelist; 19 §9      MIGRATION_OPERATION_NOT_PERMITTED / weakening trust gate
 pin or decision pin written by a gov-run repository command  24 §3.5 integrity + confinement       PIN_WRITABLE_IGNORED / REPOSITORY_COMMAND_CONFINEMENT_UNAVAILABLE
 ─────────────────────────────── trusted write boundary ────────────────────────────────────────────────────────────
 post-install edit / race                                     snapshot per unit of work             KERNEL_TAMPERED / SNAPSHOT_GENERATION_STALE
 Git-delivered forged set                                     use-time authentication               KERNEL_UNAUTHENTICATED
 Git-delivered legacy kernel or layout                        installation state LEGACY; E1         KERNEL_INELIGIBLE(historical)
 Git-delivered older eligible release                         E7 + joins; E10; freshness (OP-7)     KERNEL_INELIGIBLE(downgrade_without_transaction) / TRUST_STATE_UNANCHORED
 occupation entry removed                                     installation state                    INSTALL_STATE_PARTIAL(occupation)
 committed install journal                                    VTS registry                          FOREIGN_TRANSACTION_ARTEFACT (ignored)
 pre-RoT binary on a RoT-1 project (R2-H4)                    legacy-path occupation                (legacy) NOT_INSTALLED / IO_ERROR / ADOPTION_NOT_STARTED; no byte written
 project strength lost by any change outside a transaction    strength vector over effective policy PROJECT_STRENGTH_WEAKENED
 long-lived process after an update or revocation (R2-M7)     VU-11                                 SNAPSHOT_GENERATION_STALE → reload / refuse
 agent follows rewritten adapter (R2-M8)                      18 §12                                ADAPTER_BODY_MODIFIED
```

## 3. What each artefact may and may not establish

| Artefact | May establish | May never establish |
|---|---|---|
| Trust root | keys, grants, thresholds, key revocation | anything about a release; freshness |
| Trust Policy Statement | Constitutional Surface (exact precedence, presence, Overlay Surface, owner-domain slots), floors, eligibility including historical releases and production sources, install authority, gating, bootstrap parameters and clock reset, lowering, unrevocation, chain reset | authenticity; certification; currency on a machine |
| Trust State Statement | the published set at its sequence, including artefact references | a fact not separately signed; currency on any machine |
| Release statement | content identity, compatibility, migrations, release-local references | eligibility; surface registration; certification; binaries; global minimums |
| Artefact statement (`release-artifact` ×2) | binary digests bound to TBM digests | acceptance without build attestation and TSS reference |
| Build attestation | independent reproduction of a binary and its TBM from a named source | authenticity; that the source was verified |
| Verification attestation | a verdict for one candidate, the source it reproduced, and the negative a new verdict lifts | certification |
| Freshness witness (OP-7 c) | that a named existing TSS was the latest as of a time | any state; C3 currency below two keys |
| Certification status | CERTIFIED / REJECTED / WITHDRAWN (visible only with attestation and TSS) | authenticity; freshness; lifting a negative alone |
| Revocation | refusal | new trust |
| Anchor (protected valid pin; human or in-gate confirmation) | "the published state included (e, d) at time t" on this machine, satisfied only by inclusion | anything on another machine; authenticity; currency after its window |
| Currency proof | the published state as of time t, for trust ingress on this machine | anything beyond its bound; the word `current` |
| Trust-gate confirmation in the VTS | authorisation of one trust transition for one project on this machine | anything else |
| `governance/trust/**` in a repository | nothing by presence; its statements once verified | freshness; anchors; authorisation |
| Lock 3.0.0 | a record of the installed identity; hints | authenticity, eligibility, freshness, authorisation |
| Occupation entries | nothing (a barrier for legacy binaries) | any decision |
| Gate records under `spec/decisions/` | T2 evidence; a request for trust gates | any trust decision |
| Journals, `.prev` directories, snapshots | hints, only when VTS-registered | any trust without re-authentication |
| Environment variables, CLI flags | source selection; narrowing | anchors, keys, identity, certification, freshness, authorisation |
