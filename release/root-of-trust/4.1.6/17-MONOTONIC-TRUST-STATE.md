# Output 17 — Monotonic trust-state model (certification, withdrawal, revocation, root rotation)

> **RoT-1 revision 4 — PROPOSED, pending fresh independent reviews; not approved, not implemented.**
> Revision 4 changes, with the review r3 finding each closes:
> - S4 uses **inclusion anchors** (BC-2, RV3-H2; normative definition in `24` §3.4).
> - Currency comes only from currency proofs (MS-9).
> - A lift needs an attestation that names the negative it lifts (CR-01, RV3-M1).
> - Only witnesses raise the clock high-water, and statements from the future are refused (CR-06, RV3-M3).
> - The artefact-compromise playbook revokes and never un-references (CR-04, RV3-M4).
> - Rotation re-signs retained statements (RV3-L8).
> - The blast radius is restated from the corrected rules (CD3-2 (5)).
>
> CD3-0 retains the rest of revision 3: release-local references, resolution, equivocation, cumulative `prior_states` and
> `prior_policies`, computed lowering and sticky negatives. Normative keywords: MUST, MUST NOT, SHOULD.

## 1. The problem

A signature proves who said something. It does not prove that it is the latest thing they said, nor that the verifier
has seen it.

| Revision | What it closed |
|---|---|
| 2 | omission and replay useless for **relaxation** |
| 3 | purpose leakage (B1, B4), certification-key lifts (B2) and equivocation (B3); currency moved to anchors |
| 4 | anchors identify statements rather than numbers; currency needs a separate proof (`24`) |

## 2. Principles (normative)

| ID | Principle |
|---|---|
| MS-1 | **Absence is never positive.** |
| MS-2 | **Negative facts are sticky.** A verified revocation stays effective until a root-signed TPS `unrevokes` it. A verified REJECTED or WITHDRAWN certification is lifted only when all of these hold: a higher-sequence CERTIFIED exists; the effective admissible TSS references it; it references a verified ACCEPTED verification attestation that the same TSS references; and **that attestation names the latest negative statement in `lifts_negative_statement_digest`** (CR-01). An attestation issued before the negative therefore never lifts it. A lift needs three distinct keys: verification-attestation, certification-status and trust-state. |
| MS-3 | **Relaxation requires proven currency.** A positive lifecycle fact relaxes a control only with a currency proof (`24` §4.4). Under OP-3 mode A nothing is relaxable by certification. |
| MS-4 | **Monotonic acceptance.** Signed regressions and equivocations are security events. |
| MS-5 | **Availability is untrusted; content is signed.** |
| MS-6 | **Offline use is always possible** for an installed eligible release. The permitted classes follow `24` §4.3. |
| MS-7 | **The latest file in a repository is never freshness.** |
| MS-8 | **Minimums come only from the trust-state lineage.** References elsewhere are release-local (S7). |
| MS-9 | **Anchors give a safety floor; currency needs a proof.** An anchor is satisfied only by inclusion (`24` §3.4). A state is presented as the published state as of a time only with a currency proof (`24` §4.4). No surface says `current`. |

## 3. Statement types and their counters

| Statement | Purpose (`05`) | Counter and chain | Asserts | Can never assert |
|---|---|---|---|---|
| Trust root vN | `root` | `version`, dual-threshold chain | keys, grants, thresholds, revoked keys | anything about a release |
| Trust Policy Statement (TPS) | `trust-policy` | `policy_version`; cumulative `prior_policies[]` and `lowering_history[]` | Constitutional Surface (with exact precedence registration, presence, Overlay Surface and owner-domain slots, `23`); eligibility (historical releases; OP-2 production sources); install authority; gating; bootstrap (OP-6, OP-7 parameters, `clock_reset`); `unrevokes[]`; optional `state_chain_reset` | authenticity, certification |
| Trust State Statement (TSS) | `trust-state` | `sequence`; `previous_state_digest`; cumulative `prior_states[]` | the published set at `sequence`: `references`, `revocations[]`, `certifications[]`, `attestations[]`, `artifacts[]` | currency (revision 4: `expires_at` is no longer a witness) |
| **Freshness witness** | **`freshness-witness`** (new) | `issued_at`, `expires_at` | that `(sequence, digest)` was the latest TSS as of `issued_at` | any state |
| Certification status | `certification-status` | `certification_sequence` per final | CERTIFIED / REJECTED / WITHDRAWN | CERTIFIED without an ACCEPTED attestation |
| Verification attestation v2 | `verification-attestation` | bound by candidate digest | ACCEPTED / REJECTED for one candidate; **the verified `source`**; optional `lifts_negative_statement_digest` | certification |
| Build attestation v2 | `build-attestation` | bound by artefact, TBM and source | independent reproduction of attested source | authenticity; source legitimacy |
| Revocation | `revocation` | `revocation_sequence` | `refuse_install` / `refuse_operation` | new trust |

**Why a visible CERTIFIED and any lift need three distinct keys.**
1. The attestation, certification and trust-state purposes are pairwise non-shareable (KS-8).
2. A lift needs an attestation that names the negative (MS-2), so it cannot reuse an earlier one.

Evidence: `P4r4` `RV3-B-A05_lift_requires_post_dating_attestation`. The attestation issued before the withdrawal leaves
the negative in place; a new one naming the withdrawal lifts it.

## 4. Knowledge sources

| Source | Location | Writer | Role |
|---|---|---|---|
| T0 | compiled (TBM, `25` §4) | nobody at run time | knowledge; safety floor |
| Verifier Trust Store (VTS) | `<account-home>/.local/state/gov/trust/<trust_root_id>/`, resolved from the account database | the same OS user (A3); `gov`-run children are confined away from it (`24` §3.5) | knowledge; human, in-gate and retained anchors; high-water; per-project records; confirmations |
| **Pins** | system pin directory, or the account location when the integrity predicate holds (`24` §3.5) | the operator (TA-9 restated) | anchors (with validity); decision pins (`27` §3.2) |
| Project Trust Record (PTR) | `governance/trust/state/`, `root/` | repository writers (A2) | knowledge only |
| Lock references | `governance/trust/framework.lock` | A2 | hints |
| Bundle | `trust/` in a release bundle | A1 | knowledge |
| Refresh | `gov trust refresh --from <file>` | A1/A5 | knowledge |

Every statement is verified (SV-1…SV-10) before it enters knowledge **K**. A source can add, delete or withhold genuine
statements. It cannot forge statements, and it cannot anchor.

## 5. Effective state algorithm (normative)

| Step | Rule |
|---|---|
| S1 | **Collect.** K = verified statements from T0 ∪ VTS ∪ PTR ∪ bundle ∪ refresh. A statement whose `issued_at` exceeds the local clock by more than the compiled skew (300 s) is refused at ingest and never recorded (`STATEMENT_ISSUED_IN_FUTURE`, CR-06). |
| S2 | **Root.** Effective root = the highest version reachable from the compiled chain by dual-threshold links. |
| S3 | **Trust policy.** (a) Equal versions with different digests → `TRUST_POLICY_EQUIVOCATION`. (b) The highest TPS MUST list every held lower TPS in `prior_policies[]`. (c) Computed reductions against the strongest held values (`19` §10.6 revision 4: floor values, classes, memberships, presence, precedence in both directions, migration-writable overlay targets, owner-domain slots, and the non-surface fields listed there) MUST each appear in `lowering_history[]` with `in_policy_version` above the held version, otherwise `TRUST_POLICY_UNDECLARED_LOWERING`. Explained reductions need the per-project `policy_lowering` gate before they apply to a project that holds the stronger registration. (d) Unknown `floor_schema_version`, class or operator → `BINARY_BELOW_TRUST_POLICY`. |
| S4 | **Trust state.** (a) *Resolution:* a TSS is resolved iff its referenced root version is ≤ the effective root and its referenced TPS is held. Unresolved TSSs never constrain. (b) ***Anchors (revision 4).*** With anchors *A* (honoured pins, human, in-gate and retained anchors), candidates are the resolved TSSs whose chain contains every anchored `(sequence, digest)`, each of which must be held (`24` §3.4). Resolved TSSs outside the anchored chain are **orphans** (at or below the top anchor) or **unchained above the anchor**. Neither is ever effective or a constraint; both are reported (`TRUST_STATE_FORK_ORPHANS`, `TRUST_STATE_UNCHAINED_ABOVE_ANCHOR`, doctor CRITICAL). No candidate → freshness `BELOW_ANCHOR`. Anchors on different chains → `ANCHOR_CONFLICT`. (c) *Equivocation* among candidates (or among resolved TSSs, without anchors) → `TRUST_STATE_EQUIVOCATION`. (d) *Admissibility:* in sequence order over the candidates and the ancestors in the anchored chain, T is admissible iff for every admissible lower L: `T.revocations ⊇ L.revocations`, `T.attestations ⊇ L.attestations`, `T.artifacts ⊇ L.artifacts`, certification sequences do not decrease, references do not decrease, and `(L.sequence, digest(L)) ∈ T.prior_states`. (e) Effective TSS = the highest admissible. A higher non-admissible resolved TSS, or any unchained TSS above the anchor → `TRUST_STATE_REGRESSION`. An unresolved TSS above the effective one → `TRUST_STATE_INCOMPLETE`. |
| S5 | **Negative set N** = every verified revocation target − TPS `unrevokes` ∪ every release with a REJECTED or WITHDRAWN certification not lifted per MS-2. |
| S6 | **Certification view** per final release (§6). |
| S7 | **Release-local requirements** (unchanged). |
| S8 | **Hints** (unchanged): warnings only. |
| S9 | **Trust-state axis** = `EQUIVOCATION` \| `REGRESSION` \| `INCOMPLETE(n′)` \| `KNOWN(n)`. |
| S10 | **Freshness and currency axes** (`24` §4.1, §4.4). |
| S11 | **Persist.** Newly verified statements go into the VTS (union). High-water components rise monotonically. Only witnesses raise `clock_high_water`. Human and in-gate anchors are recorded; pin anchors are recomputed per process. The PTR is written only inside an install transaction or `gov trust refresh`, as a union (`18` §5.2). |
| S12 | **Chain reset.** Only a root-signed TPS `state_chain_reset {after_sequence, genesis_digest}`. |

Evidence: `evidence/P4r4-trust-state-model.json`, 54 scenarios, all hold. The conformance oracle kills each of 9
single-rule mutants. `M-sequence-anchor`, which replaces S4 (b) with a sequence comparison, fails RV3-B-A12, RV3-D-A12,
RV3-D-A15 and the machine matrix.

## 6. Certification view

| View | Condition | May it relax a control? |
|---|---|---|
| `REVOKED` | X ∈ N | no |
| `WITHDRAWN` / `REJECTED` | a negative not lifted per MS-2 | no; refused when TPS `gating.refuse_known_*` |
| `CERTIFICATION_UNREFERENCED` | CERTIFIED exists, no admissible TSS references it | no |
| `CERTIFIED_AS_OF(n)` | effective TSS n references CERTIFIED C for X; C references an ACCEPTED attestation of X's candidate that TSS n also references; no negative | **no** |
| `CERTIFIED_AS_OF(n) WITH CURRENCY(proof)` | the above ∧ trust state `KNOWN` ∧ a currency proof (`24` §4.4) | only under OP-3 mode B, and only to skip the update gate |
| `NOT_CERTIFIED` | none of the above | no |

Revision 3's `CERTIFIED_CURRENT` is renamed. No view says `current`.

## 7. Trust-state and freshness requirement by operation

| Operation | Trust state | Freshness and currency (`24` §4.3–§4.4) | Gate |
|---|---|---|---|
| C0 | none | none | — |
| C1 | not `EQUIVOCATION`/`REGRESSION` | per OP-7 | — |
| C2 | `KNOWN` | per OP-7; `INCOMPLETE` refuses under every option | non-trust gates as policy |
| C3 `init`, `adopt migrate --batch 0` | `KNOWN`; release-local requirement met | `ANCHORED` or `WITNESSED` **and a currency proof** | `init_ack` |
| C3 `update --apply` | as above | as above | mode A: `framework_update` always |
| C3 rollback, restore, downgrading recovery | as above | as above | `downgrade` |
| C3 `trust verify-artifact` acceptance | as above | as above | — (`25` A9) |
| `kernel reinstall` (same statement digest) | not `EQUIVOCATION`/`REGRESSION` | none (integrity remedy; identity from the VTS per-project record, CR-09) | — |
| C3 evaluation-candidate install | as above | as above | `evaluation_candidate` |

There is no override for `INCOMPLETE`, `REGRESSION`, `EQUIVOCATION`, `BELOW_ANCHOR`, `UNANCHORED` or
`CURRENCY_UNPROVEN` at ingress.

## 8. Revocation state

- Revocations accumulate (S5). A revocation delivered alone is effective immediately. Unrevocation exists only as a TPS
  `unrevokes`.
- `refuse_install` applies at ingress, rollback and restore. `refuse_operation` also applies at use.
- **A security-relevant revocation SHOULD come with a TPS raising `eligibility.min_release_sequence`.** Machines that
  receive neither the revocation nor the TPS are the stated core (RS-1).
- **Revocation-only TSS (RV3-L6).** When no TPS raise accompanies a revocation, the OP-7 (d) exposure covers every
  binary whose compiled TSS predates the revoking TSS, not only binaries older than the newest TPS (`24` §9).

## 9. Root rotation and re-signing (RV3-L8)

- Root N+1 is known once its dual-threshold link is held.
- A key removed in N+1 is `SIGNER_REVOKED` on every verifier holding N+1.
- **Playbook rule.** Before publishing a root N+1 that removes a key of any purpose, the owner MUST re-sign, with the
  successor key, every retained honest statement signed by the removed key. That covers:
  - trust-state history, including every TSS an anchor may name;
  - attestations, certifications and build attestations;
  - artefact statements and witnesses.

  The re-signed statements go in the same bundle or refresh as N+1. Payload digests do not depend on signatures, so
  every anchor stays satisfied.
- Without re-signing, anchored machines drop to `BELOW_ANCHOR` (C0) until the re-signed statements arrive. That is
  availability only, and it fails closed.
- Evidence: `P4r4` `RV3-D-A16_rotation_resigns_retained_statements`.
- **RS-1 case.** A thief of a later-removed key can sign statements referencing old roots. A machine that never receives
  N+1 cannot tell. On an anchored machine, such statements are effective only if they descend from its anchor (`24` RS-1).

## 10. Replay protection

| Replay | Binding that defeats it |
|---|---|
| cross-lineage or cross-profile | `trust_root_id`, `trust_profile` (SV-10) |
| cross-type | payloadType ↔ purpose ↔ `_type`; PAE |
| certification or attestation for another release | full digests and `release_id`; source equality |
| older TSS or TPS presented as current | knowledge union; admissibility; inclusion anchors |
| a higher TSS that does not chain through the anchor | S4 (b): never a candidate |
| forked history across missing intermediates | cumulative `prior_states[]` |
| older witness | highest witness `issued_at`; validity bound; separate purpose |
| future-dated statement poisoning the clock | S1 ingest refusal; only witnesses raise the high-water |
| gate answer reused for another digest or project | confirmation bound to kind, project, digests and, for C3, the typed state fingerprint; consumed once |
| CERTIFIED after WITHDRAWN | MS-2 with `lifts_negative_statement_digest` |
| older binary as upgrade | accepted-TBM high-water (`25` A7) |

## 11. Rollback of trust metadata

| Attack | Result |
|---|---|
| A1 serves an older TSS, TPS or root | knowledge only; below an anchor it is never effective |
| A2 deletes `governance/trust/state/` | no effect on VTS-holding machines; fresh machines are `UNANCHORED` (`24` §4.3) |
| A2 swaps in an older eligible release | judged at the machine's effective state; ingress refused without a gate and currency proof; per-project record downgrade detection (`20` §9) |
| A2 edits lock references | warning |
| A3 deletes or rewrites the VTS | `UNANCHORED` (RS-3); pins outside A3's write reach under the predicate |
| A4 redirects `HOME`, `XDG_*`, `GOV_*` | no effect |
| Trust-state key thief publishes a TSS that omits revocations or forks | anchored machines: never effective unless it descends from the anchor and is admissible; a machine holding the omitted revocation freezes (`REGRESSION`) |

## 12. Offline operation

- Using an installed eligible release needs no network. The classes follow `24` §4.3.
- Installing from a local bundle works offline on an anchored machine when:
  - the bundle carries the anchored chain; and
  - the operator supplies a currency proof: typing the published fingerprint into the gate is clockless (`24` §4.4 P2).
- Air-gapped propagation: `gov trust export` and `gov trust refresh --from`.

## 13. Clock (TA-7 only where an option or a window uses it)

- The local clock is trusted only for:
  - pin validity;
  - the C3 currency window;
  - OP-3 mode B;
  - OP-7 (b) and (c).
- `clock_ok` iff the local clock is ≥ `clock_high_water`. When it is not, clock-based proofs and pins are unusable (fail
  closed).
- `clock_high_water` rises only with verified `freshness-witness` statements.
- A root-signed TPS `bootstrap.clock_reset {reset_to}` lowers it.

Evidence: `P4r4` `RV3-B-A07_issued_at_high_water`. A candidate issued 100 years ahead is refused at ingest; OP-7 (b)
still allows C2; a future-dated witness is refused while an honest witness still verifies.

## 14. Recovery semantics

| Situation | Recovery |
|---|---|
| VTS missing or corrupt | rebuilt from T0 ∪ PTR ∪ bundles; `UNANCHORED` until re-anchored |
| PTR deleted | the next transaction or refresh rewrites it as a union |
| `INCOMPLETE` / `BELOW_ANCHOR` | supply the statements (`gov trust refresh --from`) |
| `REGRESSION` / `EQUIVOCATION` | refused; rotate the `trust-state` purpose (root N+1, with re-signing per §9) and, if histories forked, issue `state_chain_reset` |
| Erroneous TSS publication | publish a correct n+1 including every lower revocation and the full `prior_states[]` |
| Certification key stolen | root removes the key; a forged CERTIFIED is visible only with an attestation and a trust-state reference; a forged lift also needs a fresh attestation (MS-2) |
| **Release-artifact keys stolen (CR-04, RV3-M4)** | root N+1 removes the keys (with re-signing); **revoke the forged artefact digests; the next TSS keeps every `artifacts[]` reference and adds the revocations.** Verifiers holding the earlier TSS reach `KNOWN(n+1)`, and the artefact is refused `ARTIFACT_REVOKED`. A TSS never drops artefact references. Evidence: `P4r4` `RV3-B-A09_playbook_revokes_never_unreferences`. |
| Build-attestation or verification-attestation keys stolen | `25` §7 |

## 15. Purpose blast radius (restated from the revision-4 rules; CD3-2 (5))

| Stolen alone | Worst case |
|---|---|
| `trust-state` | **Anchored machine:** a statement that does not descend from the anchor is never effective (`BELOW_ANCHOR`, or `REGRESSION` where the anchored statement is held); a descendant that drops a held revocation is non-admissible (freeze). A descendant presented to a machine that never held a later revocation admits no more than withholding already admits (RS-1 core). **Stateless machine:** a freeze under OP-7 (a)–(c); under (d), a descendant of the compiled T0, which equals the (d) residual and never C3. **Never:** lift a negative, create certification, witness currency, or accept a binary alone. |
| `freshness-witness` (one key, threshold 2) | nothing |
| `freshness-witness` (keys at threshold) | stale selection of genuine existing TSSs for witness-reliant machines until rotation (`24` §3.3); no state creation |
| `certification-status` | negatives take effect (denial of service); CERTIFIED stays unreferenced |
| `release-candidate` | candidate statements; their references constrain only their own ingress |
| `release-final` | `25` §7 and `05` §1: authentic finals; no binary source choice |

Evidence: `P4r4` `TS_KEY_BLAST_RADIUS`, `RV3-B-A06_witness_authority`, `RV3-B-A12_RV3-D-A12_higher_unchained_tss`, and the
matrix (no unstated row).

## 16. Residuals

RS-1…RS-5 are stated exactly in `24` §10.
