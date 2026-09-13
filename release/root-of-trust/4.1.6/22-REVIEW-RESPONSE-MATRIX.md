# Output 22 — Response matrix to the independent review

> **RoT-1 revision 2 — PROPOSED, pending a fresh independent review; not approved, not implemented.**
> Review: `release/root-of-trust/4.1.6-review/` (commit `1c6027c`), verdict `ROOT_OF_TRUST_ARCHITECTURE_REJECTED`.
> Every finding, correction-delta item and held-out attack is mapped below to the revision 2 correction, where it is
> specified, the governing D-0008 rule, and the acceptance scenarios.

## 1. Status summary

| Severity | Findings | Resolved in architecture | Resolved with an explicitly bounded residual | Unresolved |
|---|---|---|---|---|
| HIGH | RV-H1…RV-H4 | 4 | RV-H1 (RR-2), RV-H2 (RS-1, RS-2), RV-H3 (VR-1…VR-4) | **0** |
| MEDIUM | RV-M1…RV-M8 | 8 | RV-M4 (LC-1…LC-3), RV-M6 (OP-6 mode b is owner-selectable), RV-M7 (VR-4) | **0** |
| LOW | RV-L1…RV-L4 | 4 | RV-L3 and RV-L4 need owner or implementation action at approval time (§4) | **0** |

## 2. HIGH findings

| Finding | Underlying trust class fixed | Revision 2 correction | Specified in | D-0008 rule | Tests (`12`) |
|---|---|---|---|---|---|
| **RV-H1** No currency floor: authentic older or legacy kernels become the current policy root; floors read from the kernel being judged | **authenticity mistaken for currency** | Eligibility predicate E1–E10 evaluated from T0, the Trust Policy lineage, trust state and the VTS — never from the candidate. The non-downgradable floor lives in the root-signed Trust Policy lineage (compiled hard minimum, monotonic versions). Effective floor = TPS ⊔ eligible kernel ⊔ overlay strengthening. Every final's floor values must be registered in a TPS. Explicit, gated lowering only. Historical 4.1.2–4.1.5 identities are never eligible. Every restoring path (rollback, snapshot, journal recovery, adoption uninstall, Git delivery) applies eligibility and the downgrade policy. Install authority comes from the floor. Rev 1's “legacy defects are binary-only” claim is withdrawn. | `19` (all), `20` §2–§5, §9, `13` §2, §6, `05` §5 | (1), (6), (11), (18) | RT-11, RT-29, RT-31, RT-32 (R1 flip), RT-33, RT-34, RT-52, RT-57, RT-58, RT-70 |
| **RV-H2** Lifecycle facts replay- and omission-unsafe | **availability mistaken for freshness** | Separate trust-state purpose publishing an admissible, hash-chained Trust State. Negative facts sticky and unioned across all knowledge sources. Absence never positive. CERTIFIED visible only with attestation + certification + TSS reference, and relaxes nothing under OP-3 mode A. Signed required minimums (`trust_references`, `issued_under`) detect staleness. `STALE` refuses ingress without override. Signed regressions refused. VTS location from the account database. Root rotation references. Recovery semantics for every store and key. Offline use unaffected. | `17` (all), `05` §3, §9, `21` OP-3, OP-4, OP-5 | (7), (17) | RT-20, RT-35, RT-36, RT-37, RT-38, RT-39, RT-56, RT-60, RT-61, RT-62, RT-64 |
| **RV-H3** Verified bytes are not the enforced bytes | **verification separated from use** | Exact objects defined: statement bytes, CI, VerifiedBlob, ARO, StagedTree, KernelSnapshot, EmbeddedSnapshot. Invariants VU-1…VU-10: read once, install from buffers, read-back before commit, atomic exchange, lock commit point, post-commit snapshot equality, enforcement only from snapshot bytes, derived artefacts bound to CI. Secure no-follow primitives per platform, including ancestors. Exclusive staging. Locks. Installation state machine. No cache on any trust path. | `18` (all), `04` §3 V1, §6 | (8), (10) | RT-16, RT-17, RT-22, RT-40, RT-41, RT-42 (R2b flip), RT-43, RT-45, RT-51, RT-59, RT-71 |
| **RV-H4** Legacy identity conferred by the certification role | **purpose confusion** | Nine purposes with a compiled payloadType → purpose → `_type` table. Root grants with mandatory separation constraints KS-1…KS-7 (release-final ∩ certification = ∅, …). Verification rules SV-1…SV-10 (purpose, lineage, profile, source context). Historical identity signed by `release-final`, accepted only from the compiled copy, and never eligible. Kernel authenticity only from release purposes. | `05` §1–§5, `19` §7, `13` §2 | (9), (16), (17) | RT-04, RT-21, RT-46, RT-47, RT-55 |

## 3. MEDIUM findings

| Finding | Revision 2 correction | Specified in | D-0008 rule | Tests |
|---|---|---|---|---|
| **RV-M1** Unguarded writers; ingress map omitted adoption batch rollback, CIT `move_file`/`delete_file`, A7/A11 checks, adapter freshness; completeness by symbol grep | Protected Path Set; GovernedFs as the only mutation API with `InstallTxToken`; CIT planning refusal; adoption batch 0 rollback = `install_tx::uninstall`; batch ≥ 1 restores through GovernedFs; `gov`-run git arguments pre-validated; A7/A11 and adapter freshness use the snapshot and CI. Ingress map adds I-34…I-47 and a full mutation inventory. Conformance by filesystem interception across all commands. | `18` §8, `02` §3–§5, `20` §6–§7, `09` R-FS | (10) | RT-27, RT-48, RT-59 |
| **RV-M2** Partial-install fail-open | Installation state machine evaluated first in every process, including commands not requiring installation. Non-complete states use EmbeddedSnapshot ⊔ floor, refuse mutations, and offer only remedies; D033. | `18` §9, `20` §8, `09` R-PART | (1), (14) | RT-43 |
| **RV-M3** Install authority from the target | Install-authority floor = max(TPS, EmbeddedSnapshot, current eligible kernel, overlay); the target is never consulted; new install-class operations defined | `19` §8, `09` R-INIT-2 | (11) | RT-49 |
| **RV-M4** Pre-RoT binaries keep circular trust | Explicit trust-format boundary: `governance/trust/FORMAT`; lock 2.0.0 sentinel values in the 1.1.0 hash fields; tombstone `KERNEL_MANIFEST.json`; identity moved to `kernel.*`; unknown formats fail closed. **Executed** against the real 4.1.5 binary (`evidence/F1-*`): `verified: false`, sentinel text in problems, `KERNEL_TAMPERED` refusals, doctor UNHEALTHY. Source check shows 4.1.2–4.1.4 `verify_kernel`/D003 fail on the tombstone. | `13` §3–§4, `08` §3, `09` R-FMT | (12) | RT-50, RT-72 |
| **RV-M5** Verification acceptance and candidate status not distinct | Signed `release.stage` with separate payloadTypes; `release-candidate` purpose (OP-4 reversed to “yes”); `verification-attestation` purpose and statement; promotion requires an ACCEPTED attestation and identical tree digest; CERTIFIED requires the attestation. The five facts are distinct (authenticity, candidate identity, verification result, certification state, eligibility). | `05` §1, §5, `07` §3–§4, §7, `17` §6, `19` §6 E2, `21` OP-4 | (17) | RT-39, RT-62, RT-63 |
| **RV-M6** Bootstrap channels co-hosted; OP-6 TOFU; lineage mismatch unspecified; fork binaries | At least two fingerprint channels not sharing an attacker with the release host (repository copies do not count). OP-6 restated as first-install user verification with mode (a) recommended, pin files from the account database, no env confirmation. Fail-closed `TRUST_ROOT_LINEAGE_MISMATCH` with no re-pin; explicit `adopt-lineage` for re-rooting. | `06` §2–§4, `21` OP-6, `09` R-BOOT | (15) | RT-65, RT-66 |
| **RV-M7** Profile integrity via plugin-reported digests and size/mtime | Host-side verification; plugin digests informational (T6); CAS store with fs-verity where available; full host verification bracketing every persistent index write; residual VR-4 explicit | `10` §4–§5, §7 | (2), (8) | RT-15, RT-67 |
| **RV-M8** Signed migration removes project strengthening; forked chain | Runtime-computed weakenings gated in every OP-3 mode; signer declarations add but never remove gates; unique migration chain (`MIGRATION_CHAIN_AMBIGUOUS`); statement/file equality for all duplicated fields; migration lock operation removed | `19` §9, `04` §3 V10, `07` §3, `08` §4 | (13) | RT-08, RT-53, RT-54 |

## 4. LOW findings

| Finding | Correction | Where |
|---|---|---|
| **RV-L1** Specification inconsistencies | V15 removed (steps now V0–V12); RT-05(c) expects `STATEMENT_MALFORMED`, consistent with `minItems: 1`; tree paths restricted to ASCII (matches GOV-JCS-1; all existing payload paths comply); `release_id` wording fixed; migration fields equality; key-id recomputation and duplicate-key refusal (SV-4, KS-7); `require_algorithms` added to the schema; OP-5 informational only; revocation matching on full digest; corrupt compiled trust material fails closed | `04` §3, `05` §3–§4, §11, `07` §2–§5, `12` RT-05, RT-55, RT-69, `21` OP-5, `schemas/` |
| **RV-L2** Test profile exposed to feature unification | Separate `gov-test-profile` binary target and crate; `compile_error!` guard; pipeline assertion; artifact statement records profile | `05` §10, `09` R-REL-8, `12` RT-68 |
| **RV-L3** Determinism, append-only release directory, design commit branch | Deterministic statement inputs (`released_at` from commit time, fixed builder string); the producer table defines exactly which files are added after build (`release-candidate.dsse.json`, attestation, `lineage/`, `release-final.dsse.json`, certification, trust statements). **Branch placement is an owner decision**, recorded in `11` Phase 0: revision 1 sits on `release/4.1.5-rc1`; `v4.1.5-rc1` still points at `da9c851`. | `05` §7, `07` §6–§7, `11` Phase 0 |
| **RV-L4** `PROVISIONAL` treated as active by the runtime | Architecture requires a `PROPOSED` record status, or exclusion of `in_effect: false` from `RecordStore::active()` and the context compiler, **in the same implementation change that approves D-0008**. Until then the canonical repository is not an installed consumer, so there is no effect (verified by the review). | `15` §6, `11` Phase 0 |

## 5. Correction delta (`../4.1.6-review/11-CORRECTION-DELTA.md`)

| Item | Applied in revision 2 |
|---|---|
| CD-1 currency floor and strengthen-only floors | `19` §2–§10; `20` §2–§5, §9; `13` §2, §6; `11` Phase 1, Phase 4; `01` TH-24; `15` rules (1), (6), (18); `12` RT-31…RT-34, RT-58. The CD-1 proposal of strengthen-only against the *embedded* kernel is generalised into the signed Trust Policy lineage, so floors can evolve after ship without a binary. |
| CD-2 monotonic lifecycle facts and freshness linkage | `17`. The CD-2 proposal to carry `decertify` in revocation statements is replaced by a dedicated trust-state purpose with admissibility, which also covers certification ordering and root/policy references; `issued_under` implements the freshness linkage. |
| CD-3 only release purposes confer authenticity | `05` §2, §5; `13` §2; `15` rule (9) |
| CD-4 byte binding at use time | `18` §1–§3, §6, §10; `04` §3 V1 |
| CD-5 path-based writer guard and completed ingress map | `18` §8; `02` §3–§5; `20` §6–§7 |
| CD-6 installed-state determination | `18` §9; `20` §8 |
| CD-7 authority from T0 | `19` §8; `15` rule (11) |
| CD-8 older binaries fail closed | `13` §3 (with executed F1); `08` §3 |
| CD-9 candidate stage and verification attestation | `05` §1; `07` §3, §4, §7; `17` §6; `21` OP-4 |
| CD-10 bootstrap anchoring | `06` §2–§4; `21` OP-6 |
| CD-11 host-verified profile integrity | `10` §4–§5 |
| CD-12 migration authorisation and chain shape | `19` §9; `04` V10 |
| CD-13 low-severity fixes | §4 above |
| Re-review entry criteria 1–4 | (1) CD-1…CD-12 reflected, D-0008 rules (1)–(18), ARCH-0002 revised; (2) `12` includes all review attacks (§6); (3) legacy claim corrected (`19` §7, `13` §2, `11` Phase 1); (4) OP-3, OP-4, OP-6 restated (`21`) |

## 6. Held-out attack register (`../4.1.6-review/08-HELDOUT-ATTACK-REGISTER.md`)

All 40 attacks are mapped to acceptance scenarios in `12` §5. The 30 attacks the review marked *not covered* or *not
specified* are now specified with expected outcomes:
- RV-A04, A05, A10, A14–A38, A40.

Three variants are defined as documented-residual checks, where the scenario records behaviour against a stated bound:
- RT-35(d) — RS-1/RS-2;
- RT-37(c) and RT-38(c) — RS-1.

## 7. Owner-required amendments checklist

| Requirement from the amendment prompt | Where |
|---|---|
| Authenticity does not imply eligibility; floors outside the candidate; older release cannot lower invariants; downgrade governed by external policy; historical releases constrained; floors survive rollback; old release recognised yet refused | `19` §1–§2, §6–§7, §10; `20` §4 |
| Exactly where the floor lives and how it evolves | `19` §2, §10 |
| Certification freshness, withdrawal/rejection, revocation, rotation, monotonic versioning, replay protection, metadata rollback, offline operation | `17` §5–§12 |
| Trusted monotonic state mechanism and recovery semantics | `17` §3–§5, §14 |
| OP-3 and OP-4 revisited | `21` |
| Exact authenticated object and consumed bytes | `18` §1 |
| Source swap, symlink substitution, concurrent mutation, partial install, crash recovery, same-user races, cache replacement closed | `18` §10 |
| Purpose authorities: release, certification, revocation, retrieval profile, historical identity, root | `05` §1, §5 |
| Domain-separated statement types and verification rules | `05` §2, §4 |
| Additional write paths constrained (adoption batch rollback, CIT move/delete, recovery, snapshot, cache, migration) | `02` §3–§4, `18` §8, `20` |
| Partial-install fail-closed recovery | `18` §9, `20` §8 |
| Install authority floor | `19` §8 |
| Legacy-binary trust-format boundary | `13` §3–§4 |
| Distinct authenticity, candidate identity, verification result, certification, eligibility | `15` rule (17), `05` §5, `17` §6, `19` §6 |
| OP-1…OP-6 re-analysed; material choices flagged | `21` |
| D-0008 rules 1–8 | `15` §5 rules (5)–(12) marked [O1]…[O8]; `spec/decisions/D-0008.yaml` |
| D-0007 superseded explicitly, not silently modified | `15` §1, §6; D-0007 file untouched |
| 20 required adversarial cases | `12` §4 |
| Revised threat model, trust chain, ingress map, monotonic model, verify-and-use, key purposes, rollback/recovery, legacy compatibility, OP analysis, D-0008, ARCH-0002, acceptance plan, response matrix | `01`, `03`, `02`, `17`, `18`, `05`, `20`, `13`, `21`, `spec/decisions/D-0008.yaml`, `spec/architecture/ARCH-0002.yaml`, `12`, this file |

## 8. Unresolved findings

**No independent-review finding remains unresolved at the architecture level.**

**Accepted residuals.** These are explicit, bounded, and none can produce a certification view, an eligibility the
policy forbids, a floor below the compiled Trust Policy, or a relaxation under OP-3 mode A:

| ID | Residual | Defined in |
|---|---|---|
| RS-1 | a verifier that never receives newer metadata cannot know it exists | `17` §15 |
| RS-2 | OP-3 mode B trusts the local clock (owner-optional; not the default) | `17` §13 |
| RS-3 | A3 can delete its own VTS | `17` §15 |
| VR-1…VR-4 | same-user post-snapshot modification; advisory locks; non-`gov` subprocess writes; profile runtimes by path | `18` §11, `10` §7 |
| RR-1…RR-3 | ineligible state after an automatic rollback; older eligible release on a machine without a VTS record; A3 deleting the record | `20` §10 |
| LC-1…LC-3 | pre-RoT binaries' own behaviour (4.1.5 remedies overwriting; 4.1.2–4.1.4 no trust boundary; 4.1.5 cache baseline for read-only commands) | `13` §3.3 |

**Actions for others, not unresolved architecture.**
- RV-L3 branch placement of design commits: owner decision.
- RV-L4 record-schema change: part of the approval implementation.

**Independence.** This revision was written in the same session that authored the independent review of revision 1.
The next review must be performed by a different, fresh reviewer.

## 9. Portions confirmed sound by the review, preserved

| Confirmed sound | Preserved in revision 2 |
|---|---|
| Compiled external public trust anchors | `05` §6, `06` §1–§2, T0 (`15` §4) |
| Offline/private release signing | `05` §7 |
| Signed release identity covering kernel material | `07` §3, §5 |
| Authentication before install | `04` §3 (no Protected Path write before V12 and authorisation) |
| Transactional/journaled install | `18` §5 (strengthened with read-back and exchange) |
| `framework.lock` as evidence only | `08` §1 |
| Post-install kernel verification | `18` §6 (strengthened: byte-bound snapshot) |
| In-memory embedded baseline | `18` §7 |
| Transport/GitHub independence | `09` R-NET, `03` §3 |
| Dev/test/unsigned states distinct from production-authenticated | `04` §8, `05` §10, `06` §8 |
