# Architecture correction delta (revision 2 → revision 3)

This delta **amends** revision 2; it does not replace it. It is architectural only. This reviewer does not edit the pack,
D-0008 or ARCH-0002, and implements nothing. After applying it, the architect re-issues the pack for a **fresh**
independent review.

## CD2-0 — Retain unchanged

- compiled root chain;
- nine purposes, the compiled payloadType table and SV-1…SV-10;
- compiled-only historical identities, never eligible;
- DSSE, Ed25519 strict verification and GOV-JCS-1;
- the full file map and `gov-tree-v2`;
- the single `authenticate` constructor;
- VerifiedBlobs, the install transaction and VU-1…VU-10;
- KernelSnapshot and EmbeddedSnapshot;
- the installation state machine;
- GovernedFs and the Protected Path Set as the internal writer rule;
- the install-authority *required level* from T0/TPS;
- computed migration weakenings;
- sticky revocations and admissibility (a)(e);
- the account-database VTS location;
- mode A as the default;
- OP-6 lineage confirmation;
- the separate test-profile binary;
- the E1–E5, R1 and R2b closures;
- RT-01…RT-72, amended per CD2-14.

## CD2-1 — Total constitutional registration (closes R2-H1)

| Pack file | Change |
|---|---|
| `19` §2–§4 | Define the **Constitutional Surface**: every file listed in the release statement's `security_critical`. It must include at least AS-1 in full, `CHANGE_POLICY`, `MEMORY_POLICY.namespaces` and retrieval filters, `CONTEXT_POLICY.deterministic_authority_fields`, `ARCHIVE_POLICY.archive_mutation`, `TEST_POLICY` verification requirements, `ENFORCEMENT_MAP`, the schemas that validate records, exceptions, gates and registries, and the kernel tool registry. Every leaf of the surface must be covered by exactly one of three: **(a) floor** — an operator (add a per-entry ceiling for map values, e.g. `map_level_at_most` for `ROLES.roles[id=*].level`; `set_superset` by id for pattern lists; `ordered_at_most` for `agent_resolvable_when.max_radius`; `number_at_least` for `min_confidence`; `sequence_equals` for `POLICY_PRECEDENCE.layers`; `bool_required` for `exception_relaxable: false` on security and authority rules); **(b) content registration** — the TPS lists permitted content digests for non-orderable content (schemas, invariant statements, tool descriptors, skills); **(c) explicit non-security classification** — a TPS `unregistered_keys[]` entry signed at root threshold. |
| `19` §5 | At policy loading, a surface leaf covered by none of (a)–(c) takes its value from EmbeddedSnapshot ⊔ TPS, never from the installed kernel (`KERNEL_SURFACE_UNREGISTERED`, doctor CRITICAL). `PROJECT_EXCEPTIONS` are applied **after** the join and may never relax a floor key, a content-registered key or any SECURITY/AUTHORITY/HUMAN_GATE key, regardless of kernel `exception_relaxable`. |
| `19` §6 E7, §10.3, `07` §7 | E7 and the producer check totality over the surface. **Any change of a `security_critical` file digest between consecutive finals requires a TPS registration of the new content.** Where the change strengthens policy, the same TPS must raise `min_release_sequence` mechanically (a producer rule), not by owner memory. |
| `19` §8 | State that the actor level used against the install-authority floor comes from the joined, registered ROLES. The incoming release never defines actor levels. |
| `01`, `15` rule (6), D-0008 | Amend rule (6): "floors and registrations are total over the Constitutional Surface". Add assets AS-2, AS-4 and AS-5 to the surface statement. |
| `12` | Add RV2-A01…A08 with harm assertions for authority, secrets and gates (P1 must flip). |

## CD2-2 — Bounded currency for stateless verifiers (closes R2-H2, R2-L1)

| Pack file | Change |
|---|---|
| `17` §5, `19` §6 | New trust-state axis value **`FRESHNESS_UNPROVEN`**. It applies when this machine has no retained record for the project (VTS per-project record) and no state pin. It replaces `CURRENT_KNOWN` on the verdict surface. |
| `17` §7 (new row), `19` §6 (new E11) | Production **governed mutations** under `FRESHNESS_UNPROVEN` require one of the following. None may come from the repository. **(a) Retained state:** a VTS per-project record, then E10. **(b) State pin:** an account-database file, like the OP-6 pin, giving minimum root version, TPS version and TSS sequence (optionally minimum release sequence) per lineage, provisioned by the operator or CI image. **(c) `gov trust confirm-state <state fingerprint>`:** a human compares the fingerprint with a channel independent of the release host; recorded in the VTS. Without one of these: read-only diagnostics only (`TRUST_STATE_UNPROVEN`). Owner option **OP-7** selects (a)/(b)/(c), or **(d)** expiring TSS for stateless mutating use with TA-7 stated. OP-7 is security-material. |
| `17` §15, `20` §10, `19` §10, `22` §8, `01` §5 | Restate RS-1 and RR-2 exactly: "bounded by the running binary's compiled T0 and by retained or pinned state; gates do not bound a repository writer; Git-delivered use is never gated". Delete "floors and install authority are unaffected" unless retained or pinned state exists. |
| `17` §4 (optional) | Verified trust statements reachable in local Git history of `governance/trust/**` may enter K (defence in depth only; shallow clones stay `FRESHNESS_UNPROVEN`). |
| `21` OP-5 | The age warning counts from the newest statement's signed sequence position known to the verifier, and is always shown when the state is `FRESHNESS_UNPROVEN`. |
| `12` | Add RV2-A09…A12, including a CI-runner variant with a pinned older binary. |

## CD2-3 — Binary authenticity as a constitutional purpose (closes R2-H3)

| Pack file | Change |
|---|---|
| `05` §1–§3 | New purpose `release-artifact`, carrying `artifact-final` and `artifact-candidate`. Default threshold ≥ 2, or a root-threshold co-signature for production binaries. Disjoint from `release-candidate`, `certification-status`, `verification-attestation` and `trust-state` (new KS). Update the `05` §1 impact table, TH-22, RK-11 and OP-2. |
| `07` §4, `schemas/artifact-statement.schema.json` | The artifact statement binds each binary's compiled-T0 identity: lineage, root version and digest, TPS version and digest, TSS sequence and digest, historical registry digest, embedded release statement digest, floor schema version, trust profile, target and reproducible-build inputs. |
| `06` §2, `09` R-BOOT-4 | `verify-artifact` requires all of: the statement verified under `release-artifact`; compiled-T0 versions ≥ the VTS high-water (`BINARY_T0_ROLLBACK`); the artifact digest referenced by an admissible TSS; an ACCEPTED verification attestation of that artifact digest; not in the negative set. Certification of a release covers the artifact statement digest. |
| `12` | Add RV2-A27…A29. |

## CD2-4 — Fail-before-write format boundary and protected project strengthening (closes R2-H4, R2-L3)

| Pack file | Change |
|---|---|
| `13` §3, `08` §2, `18` §8 | Relocate the RoT-1 Protected Path Set so no pre-RoT binary reads or writes RoT-1 authority content. Occupy the legacy paths with inert entries of a type every pre-RoT binary fails on **before its first write**. P3 V3 shows a regular file at `governance/kernel` plus a directory at `governance/framework.lock` is sufficient for the tested commands of 4.1.5 and 4.1.2. Path names are the architect's choice. |
| `13` §3.3 | Replace LC-1 and LC-2 with a tested property: **for every pre-RoT binary 4.1.2–4.1.5 and every command in its register, no byte of `governance/` or `spec/` changes on a RoT-1 project.** |
| `11` Phase 4, `20` §3 | The first RoT-1 install transaction quarantines legacy `.governance-runtime/update/<v>/` snapshots (renamed so no pre-RoT binary finds them). The release protocol tells teams to retire legacy binaries. |
| `18` §5, `20` §8, `19` §9 | Record a **project-strength vector** at each install transaction, and let RoT-1 remedies (`kernel reinstall`, update, recover) report a weakening not made through a gated RoT-1 transaction. The vector is the computed-weakening input: overlay classifications, overlay floor raises, contract exclusions and non-overridable overlay keys. It is stored in the VTS record and the trust record. A remedy that restores Protected Paths must report `OVERLAY_WEAKENED_OUTSIDE_TRANSACTION` and require a gate before re-enabling mutations. |
| `12` RT-50 | Replace with the no-write property across full command registers, real 4.1.2–4.1.5 binaries and a legacy update snapshot present (RV2-A31…A36). Regenerate F1 with the exact `08` §2 FORMAT and lock. |

## CD2-5 — Authorisation for trust decisions is not a repository record (closes R2-M1)

| Pack file | Change |
|---|---|
| `17` §7, `19` §9–§10, `20` §4–§5, `09` R-UPD-5 | Gates for `framework_update`, `init_ack`, `downgrade`, `weakening`, `hint_mismatch`, `lowering`, `override` and evaluation candidates are **trust gates**. Their answer is valid only when bound to a local human confirmation recorded outside the repository: VTS entry, interactive confirmation or equivalent. The binding covers the gate id and the statement digest(s). The repository record stays evidence (T2) and, when it appears without the local binding, is a request. Trust gates are never agent-resolvable (a compiled rule, independent of `HUMAN_GATE_POLICY`) and consumers must require `by_kind: human`. |
| `03` §3, `15` rule (18), TA-8 | Correct `03` §3 ("authorisation against A3" is false). Extend rule (18) to cover authorisation for trust decisions. State TA-8's limit for other gates. |
| `02` §4 | Add plugins and tool subprocesses as writers of authorisation records and the overlay (VR-3 extended). |

## CD2-6 — Trust-state facts only from the trust-state purpose (closes R2-M2)

- `17` S7: `RM_state`, `RM_policy` and `RM_root` are taken only from verified TSS, TPS and root statements, and from the
  **installed release when an admissible TSS references it**.
- References in other release, candidate or certification statements are hints: HINT_MISMATCH, never STALE.
- S4 (c) and (d) constrain successors only by references that resolve to verified statements in K. A TSS whose
  references do not resolve is itself `STALE`, not a constraint on later TSSs.
- A reference beyond any resolvable statement is `REFERENCE_UNRESOLVED` (warning).
- Update the `05` §1 impact table.

## CD2-7 — Lifting a negative certification needs two purposes (closes R2-M3)

S5: a REJECTED/WITHDRAWN fact is lifted only by a higher-sequence CERTIFIED that satisfies both of:
- referenced by an admissible TSS;
- referencing an ACCEPTED attestation.

Otherwise the negative fact remains. Amend MS-2.

## CD2-8 — Equivocation and chain continuity (closes R2-M4)

- Two verified TSS with equal sequence and different digests → `TRUST_STATE_EQUIVOCATION`, handled as REGRESSION.
- The effective TSS must chain by `previous_state_digest` to the highest known lower TSS, or carry a root-signed chain
  reset.
- Apply the same to TPS `supersedes_policy_digest`.

## CD2-9 — Computed floor lowering and a defined mode order (closes R2-M5)

- `19` §10 step 6: compare the arriving TPS with the strongest previously accepted values. Any computed reduction needs
  the per-project trust gate (CD2-5), whatever `lowers[]` says.
- A reduction not listed in the lowering TPS's own `lowers[]` makes that TPS invalid.
- Define a total order or lattice for `rule_mode_at_least`, including the `exception_relaxable` attribute (CD2-1).

## CD2-10 — Complete separation constraints (closes R2-M6)

- Add compiled KS-8: `trust-state` ∩ (`certification-status` ∪ `verification-attestation`) = ∅.
- Add KS-9 for `release-artifact` (CD2-3).
- Make the permitted-sharing list a compiled whitelist: every unlisted pair is forbidden.
- Re-derive the OP-2 matrix so a visible CERTIFIED always needs three keys.

## CD2-11 — Snapshot generation discipline (closes R2-M7, R2-L2)

- `18` §5.3, §6: every unit of work that reads policy, and every governed mutation, takes the shared lock and compares
  its snapshot CI with the installed statement digest and lock. It also re-evaluates the negative set and TPS/TSS
  knowledge. On mismatch it reloads or refuses.
- Long-lived processes have a bounded snapshot lifetime.
- Require `st_nlink == 1` for staged and installed kernel and trust files (refuse `PATH_SUBSTITUTION_DETECTED`).
- The MCP server design must adopt this before it ships.

## CD2-12 — Agent consumption of kernel content (closes R2-M8)

- Adapters direct agents to kernel content served by `gov` from snapshot bytes (context packets, `gov skills show`).
- Direct disk reads of kernel paths by agents are declared T4.
- Rendered adapter bodies are verified by content digest against a record held outside A2's reach (VTS) or re-rendered
  per context packet.
- Add AS-4 to the use-time closure table of `18` §10.

## CD2-13 — Monotonic trust record and recovery state (closes R2-M9)

- `18` §4–§5: `trust.next` = union of the current PTR, the target's statements and the VTS knowledge.
- Exchange-back never removes a verified statement from `governance/trust/`.
- The installer excludes `governance/.tx/` from version control. A tracked `.tx/` is classified `PARTIAL` (foreign), not
  `IN_TRANSACTION`.
- `20` §5: restoring `overlay.prev` passes the computed-weakening check (CD2-5 gate).

## CD2-14 — Acceptance plan (closes R2-M10)

- Add RV2-A01…A36 with expected codes.
- Give RT-35(d), 37(c) and 38(c) pass/fail criteria (after CD2-2).
- Replace RT-50 and RT-72 expectations with property assertions.
- [FS] evidence by OS-level tracing, run by the verifier.
- Every scenario states the binary's compiled root, TPS and TSS versions.
- Add harm assertions for unfloored inputs.

## D-0008 rule changes (for the architect to draft; not approved by this review)

| Rule | Change |
|---|---|
| (6) | floors and content registrations are total over the Constitutional Surface |
| (7) | freshness is bounded for stateless verifiers per OP-7; trust-state minimums come only from the trust-state lineage |
| (9) | binary authenticity is its own purpose, bound to compiled-T0 identity |
| (12) | pre-RoT binaries fail before any write on RoT-1 projects |
| (18) | authorisation for trust decisions is never a repository record |
| new (19) | no governed mutation on unproven freshness without retained or pinned state (or the OP-7 alternative) |
| new (20) | project-owned strengthening is recorded by every install transaction, and a weakening outside a gated transaction is reported before mutations resume |

## Owner options to restate

- New **OP-7** (stateless verifier currency).
- **OP-2** extended to `release-artifact`.
- **OP-4:** state that "no" also exposes binaries unless CD2-3 separates them.
- The owner answers only after a fresh review accepts revision 3.

## Re-review entry criteria

1. CD2-1…CD2-14 reflected in the pack, schemas, D-0008 (rules above) and ARCH-0002.
2. `evidence/P1`, `P3` and `P4` re-run by the architect against the revised specification, with each `agrees` flipped
   or the scenario explicitly removed by a design change.
3. The full pre-RoT command-register matrix executed for 4.1.2–4.1.5 (4.1.3 and 4.1.4 binaries built from `26ab5b6` and
   `47d8394`).
4. `22` response matrix updated to R2-H1…R2-L3 with no "resolved" claim that rests on untested evidence.
