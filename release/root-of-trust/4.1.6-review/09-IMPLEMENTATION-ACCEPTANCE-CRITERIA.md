# Output 10 — Implementation Acceptance Criteria for the 4.1.6 Builder

These criteria apply **after** the architect applies `11-CORRECTION-DELTA.md`, the owner answers the D-0008 gate, and
the key ceremony is held. They add to RT-01…RT-30 (`12-ACCEPTANCE-TEST-PLAN.md`), which remain required. The independent
verifier proves each criterion black-box; builder tests are necessary but not sufficient.

## A. Records and approval preconditions

| ID | Criterion |
|---|---|
| AC-A1 | D-0008 is ACTIVE with `human_approved: true`, `chosen_option`, owner answers to OP-1…OP-6, and rules (11)–(14) of `06-D0007-D0008-REVIEW.md` §2. D-0007 is SUPERSEDED. ARCH-0002 is ACTIVE. The public ceremony record lists the trust-root id and key ids and contains no secret material. |
| AC-A2 | The record schema has a `PROPOSED` status, or `RecordStore::active()` and the context compiler exclude `in_effect: false` records (RV-L4). |
| AC-A3 | The trust-root fingerprint is published in at least two channels not hosted with the releases (RV-M6). |

## B. Authentication boundary

| ID | Criterion |
|---|---|
| AC-B1 | `AuthenticatedRelease` has one constructor; install APIs accept no `Path`; proven by source inspection **and** by write interception (AC-G). |
| AC-B2 | V0–V14 as specified, with: key id recomputed from `public_key`; duplicate public keys refused; migration chain unique (one migration per `from_version` on the path); certification `release_id`/`version` equal to the release statement; revocation matched on full statement digest; a corrupt compiled root makes every authenticated operation fail closed (RV-A08, A04, A36, A40). |
| AC-B3 | No decision reads `manifest.json`, `manifest.yaml` or a source `KERNEL_MANIFEST.json` (RT-02 manifest-only edits leave identity, certification and gate decision byte-identical). |
| AC-B4 | Cross-implementation vectors: PAE bytes, Ed25519 strict verification, GOV-JCS-1 canonical bytes agree with an independent implementation; paths outside ASCII are refused by the producer, or the canonical profile is amended consistently (RV-L1). |

## C. Currency and anti-rollback (RV-H1)

| ID | Criterion |
|---|---|
| AC-C1 | The binary compiles a T0 **operational floor** (minimum release sequence and version). `kernel_trust` v2 refuses an installed release below it as a policy root (`KERNEL_BELOW_OPERATIONAL_FLOOR`, D030 CRITICAL), substituting the embedded baseline and refusing mutations except `update --apply` to a release at or above the floor. |
| AC-C2 | Constitutional floors are **strengthen-only** against the binary's embedded authenticated kernel for every key the embedded `POLICY_PRECEDENCE` marks immutable or strengthen-only. With the genuine 4.1.2 kernel installed (RV-A19), an L3 role is refused `update --apply` and `resume` exactly as on the embedded kernel (R1 must flip). |
| AC-C3 | `minimum_trust_level` is a T0 constant; installed kernel and overlay may only raise it. |
| AC-C4 | Legacy 4.1.2–4.1.5 kernels are **identified** (`LEGACY_IDENTIFIED`) but never the policy root. Floors come from the embedded baseline; only update, rollback-forward and read-only diagnostics are allowed; D030 CRITICAL. Rollback to a legacy snapshot yields the same restricted state and requires a gate. |
| AC-C5 | Recovery, explicit rollback, adoption restore and any journal-driven swap-back apply AC-C1…C4 and the downgrade gate. None depends on the ledger alone (RV-A15, A18, A27). |
| AC-C6 | RV-A18, A19, A15 (A2+A3 variant) and A27 are refused with harm assertions. |

## D. Lifecycle freshness (RV-H2, RV-M5)

| ID | Criterion |
|---|---|
| AC-D1 | REJECTED, WITHDRAWN and release revocation are carried by the monotonic revocation statement (compiled floor + high-water). A certification statement cannot by itself carry a negative status that gating depends on. |
| AC-D2 | Each certification statement records `issued_under_revocation_sequence`. CERTIFIED relaxes a gate only when the effective revocation sequence is at least that value; otherwise the gate is required (RV-A17, A21). |
| AC-D3 | A genuine rejected candidate without its REJECTED certification is still gated or refused for `init` and `update` (RV-A22). Either a signed `release.stage` field or mandatory candidate revocation implements OP-4's answer. |
| AC-D4 | The high-water store location is not selectable by `XDG_CONFIG_HOME`/`HOME` alone, or an env-selected store counts as absent. D032 reports a repository whose statements reference a revocation or root version the binary cannot see as CRITICAL (RV-A10, A23, A24). |
| AC-D5 | D-0008 and the threat model state the A2/A4 metadata-rollback residual explicitly, distinct from offline freeze, and state that compromise recovery is durable only through binary upgrade. |

## E. Use-time integrity (RV-H3)

| ID | Criterion |
|---|---|
| AC-E1 | `TrustedKernel` is an immutable in-memory snapshot whose parsed content comes from the digested buffers; no component re-opens kernel paths after verification. Proven by RV-A25: the R2b racer script (`evidence/R2b-use-time-toctou.py`), pointed at the 4.1.6 binary, must show the restricted records excluded and not retrievable in **20/20** trials. |
| AC-E2 | Use-time tree rules equal quarantine rules, including ancestor symlink refusal for `governance/`, `governance/kernel/`, `governance/trust/` (RV-A37, A38). |
| AC-E3 | `installed` for trust purposes = any of lock, kernel directory, trust directory or journal present. A partial state is UNAUTHENTICATED with the embedded baseline, including for commands that do not require installation (RV-A26). |

## F. Transactions and recovery

| ID | Criterion |
|---|---|
| AC-F1 | RT-16 kill-9 matrix passes; at no point is a mixed identity `verified`. |
| AC-F2 | Readers take a shared lock or check the journal before reading kernel content; CIT execution, adoption executor and `rebuild-memory` honour the transaction lock (RV-A16). |
| AC-F3 | Directory entries are fsynced after renames; staging directories are created exclusively with unpredictable names and no-follow semantics (RV-A14). |
| AC-F4 | Migrations and templates are read from the `AuthenticatedRelease` memory during the transaction. |
| AC-F5 | A crash between lock commit and ledger append recovers to a consistent, verifiable state; the ledger entry is written idempotently from the journal. |

## G. Writers (RV-M1)

| ID | Criterion |
|---|---|
| AC-G1 | One governed filesystem layer refuses write, rename and delete under `governance/kernel/**`, `governance/trust/**`, `governance/framework.lock` without an install-transaction token. |
| AC-G2 | CIT operations (`write_file`, `move_file`, `delete_file`, snapshot restore) and adoption batch rollback refuse those paths at planning and execution (RV-A27, A28). |
| AC-G3 | The conformance suite runs **every** CLI command with a filesystem write interceptor and asserts no trust-location write outside the transaction. Symbol inspection alone does not satisfy this. |
| AC-G4 | `adopt.rs` A7/A11 kernel checks and `adapters.rs` freshness use `kernel_trust` v2 and statement identity, never lock hashes (I-36, I-37). |

## H. Authority, keys, profiles, build

| ID | Criterion |
|---|---|
| AC-H1 | Authority for init, adopt batch 0, update, reinstall, rollback, recover and override is read from T0, strengthened by the installed authenticated kernel, never from the target (RV-A29, A30). |
| AC-H2 | Lock 2.0.0 contains no `kernel_manifest_hash`/`release_hash` under their 1.1.0 names. A 4.1.5 binary opening a 4.1.6 project reports `verified:false` and refuses mutations (RV-A31). |
| AC-H3 | The test profile is a separate binary target or crate; the release pipeline fails if the shipped binary reports anything other than `trust_profile: production`; production deny-lists test key ids (RV-A33). |
| AC-H4 | Only release-role statements (or root threshold) confer kernel authenticity. A certification-signed identity statement fails `RELEASE_SIGNER_NOT_AUTHORISED`. Legacy identity digests are compiled constants (RV-A20). |
| AC-H5 | Lineage mismatch on an existing project fails closed (RV-A35); OP-6's answer is implemented as specified. |
| AC-H6 | When profiles ship: host-side digest verification of plugin, runtime and model files; plugin-reported digests informational only (RV-A32). |
| AC-H7 | Strength-reducing overlay changes by migrations are computed by the runtime and gated (RV-A05). |
| AC-H8 | Private-key scan of repository history at the tag, every payload, fixtures and CI artefacts is clean; the planted-key test fails `release build`. |

## I. Regression and evidence

| ID | Criterion |
|---|---|
| AC-I1 | The four prior harnesses run unchanged with the classifications of `12` §4, **plus** `harness_wv.py` 6/6. Any additional change must be classified by the verifier as an intended trust refusal and re-proven with a signed equivalent. |
| AC-I2 | V-H1 (plugin self-authorisation), V-H2 (installed-kernel verification), V-M1 (exception decision resolution), Human Decision Gate integrity (INV-008, gate bound to statement digest), constitutional precedence, sensitivity and indexing exclusion, authority L0–L5, the rollback ledger and release immutability all re-proven on the production-profile binary. |
| AC-I3 | E1–E5 re-executed with `evidence/E1-E5-reproduction-probe.sh` against 4.1.6: every probe refused or not verified, and the restricted floor intact. |
| AC-I4 | Evidence per scenario: transcript, error envelope, before/after tree hashes, harm assertion, `kernel trust` verdict, D030–D033. |
| AC-I5 | Release immutability: files that may be added to `release/releases/<v>/` after build (`release.dsse.json`, `certification/*.dsse.json`) are enumerated. Everything else is byte-identical to the build output (RV-L3). |
