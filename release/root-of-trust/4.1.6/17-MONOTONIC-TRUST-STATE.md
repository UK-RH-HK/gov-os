# Output 17 — Monotonic trust-state model (certification, withdrawal, revocation, root rotation)

> **RoT-1 revision 3 — PROPOSED, pending a fresh independent review; not approved, not implemented.**
> Revision 3 addresses:
> - R2-M2: minimums come only from the trust-state lineage; references elsewhere are release-local;
> - R2-M3: lifting a negative certification needs two purposes plus a trust-state reference;
> - R2-M4: equivocation, cumulative chains, anchored fork resolution;
> - R2-M5 with `19` §10: cumulative lowering history;
> - R2-H2 and R2-L1 together with `24`: the freshness axis, anchors and `CURRENT_KNOWN` withdrawn.
>
> Normative keywords: MUST, MUST NOT, SHOULD.

## 1. The problem

A signature proves who said something. It does not prove that it is the latest thing they said, nor that the verifier has
seen the latest thing they said. Revision 2 made omission and replay useless for **relaxation**. The review showed three
remaining defects:
- non-trust-state purposes and unresolvable references could force global minimums (B1, B4);
- a certification key alone could lift a negative fact (B2);
- equivocation was undefined (B3).

Revision 3 closes those. It also moves every claim of **currency** to anchors (`24`), because a stateless verifier's
knowledge is chosen by whoever supplies it.

## 2. Principles (normative)

| ID | Principle |
|---|---|
| MS-1 | **Absence is never positive.** Missing certification, revocation, attestation or trust state never yields a less restrictive state than the corresponding negative fact would. |
| MS-2 | **Negative facts are sticky.** A verified revocation stays effective until a root-signed TPS `unrevokes` it. A verified REJECTED or WITHDRAWN certification stays effective until a higher-sequence CERTIFIED that the effective admissible TSS references, and that references a verified ACCEPTED attestation which the same TSS references (S5). A certification key alone lifts nothing. |
| MS-3 | **Relaxation requires proven freshness.** A positive lifecycle fact relaxes a control only with a freshness proof (§13). Under OP-3 mode A nothing is relaxable by certification. |
| MS-4 | **Monotonic acceptance.** Root versions, TPS versions, TSS sequences and per-release certification sequences are accepted only if they regress nothing already known. Signed regressions and equivocations are security events, not fresher truths. |
| MS-5 | **Availability is untrusted; content is signed.** |
| MS-6 | **Offline use is always possible** for an installed eligible release. The permitted operation classes depend on freshness (`24` §4.3). |
| MS-7 | **The latest file in a repository is never freshness.** |
| MS-8 | **Minimums come only from the trust-state lineage.** Required minimums (state sequence, policy version, root version) are taken only from TSS, TPS and root statements. References inside release, candidate, certification or artefact statements are **release-local requirements**: they constrain only that statement's own ingress or visibility (S7). |
| MS-9 | **Currency comes only from anchors.** A trust state is presented or used as current only when a pin, a human confirmation or a verified witness (OP-7 c) establishes it (`24`). |

## 3. Statement types and their counters

| Statement | Purpose (`05`) | Monotonic counter and chain | Asserts | Can never assert |
|---|---|---|---|---|
| Trust root vN | `root` | `version`, dual-threshold chain | keys, purpose grants, thresholds, revoked keys | anything about a release |
| **Trust Policy Statement (TPS)** | `trust-policy` | `policy_version`; `prior_policies[]` cumulative `{policy_version, statement_digest}`; `lowering_history[]` cumulative | Constitutional Surface (`23`), eligibility (including `historical_releases[]`), install authority, gating (OP-3), bootstrap (OP-6, OP-7), `unrevokes[]`, optional `state_chain_reset` | authenticity, certification |
| **Trust State Statement (TSS)** | `trust-state` | `sequence`; `previous_state_digest`; **`prior_states[]`** cumulative `{sequence, statement_digest}` | the published set at `sequence`: `references{root_version, root_digest, trust_policy{policy_version, statement_digest}}`, `revocations[]`, `certifications[]`, `attestations[]`, **`artifacts[]`** (binary artefact statements, `25`); optional `expires_at` (OP-3 mode B or OP-7 c witness) | any fact not itself separately signed |
| Certification status | `certification-status` | `certification_sequence` per final statement digest | CERTIFIED / REJECTED / WITHDRAWN; optional `artifact_statement_digests[]` | authenticity; CERTIFIED without an ACCEPTED attestation |
| Verification attestation | `verification-attestation` | bound by candidate digest | ACCEPTED / REJECTED for one candidate | certification |
| Build attestation | `build-attestation` (`25`) | bound by artefact digest and TBM digest | independent reproduction | authenticity |
| Revocation | `revocation` | `revocation_sequence` | `refuse_install` / `refuse_operation` for digests | new trust |

**Why a visible CERTIFIED needs three distinct keys:**
- the attestation, certification and trust-state purposes are pairwise non-shareable (compiled whitelist, `05` §3, KS-8);
- so a visible CERTIFIED, and any lift of a negative fact, needs three keys.

## 4. Knowledge sources

| Source | Location | Writer | Role |
|---|---|---|---|
| **T0** | compiled into the binary (TBM, `25` §4) | nobody at run time | knowledge; safety floor |
| **Verifier Trust Store (VTS)** | `<account-home>/.local/state/gov/trust/<trust_root_id>/`, resolved from the account database, never from `HOME`, `XDG_*` or `GOV_*` | same OS user (A3) | knowledge; anchors; high-water; per-project records; trust-gate confirmations (`24` §8) |
| **Pins** | `<account-home>/.config/gov/trust-state-pins`, `trust-root-pins`, `approved-trust-decisions` | the operator (TA-9) | anchors (`24` §3); operator decisions (`27` §3.2) |
| **Project Trust Record (PTR)** | `governance/trust/state/`, `root/` (Git-tracked, PPS) | repository writers (A2) | cross-machine knowledge only |
| **Lock references** | `governance/trust/framework.lock` `trust_references` | A2 | hints (warnings only) |
| **Bundle** | `trust/` in a release bundle | A1 | knowledge |
| **Refresh** | `gov trust refresh --from <file>` | A1/A5 | knowledge |

Every statement from every source is verified (`05` SV-1…SV-10) before it enters knowledge **K**. A source's writer can
add genuine statements, delete them or withhold them. It cannot forge statements, and it cannot anchor.

## 5. Effective state algorithm (normative)

Runs in every process that makes a trust decision, and in every unit of work of a long-lived process (`18` §6.3).

| Step | Rule |
|---|---|
| S1 | **Collect** K = verified statements from T0 ∪ VTS ∪ PTR ∪ bundle ∪ refresh. |
| S2 | **Root.** Effective root = the highest version reachable from the compiled chain by dual-threshold links. |
| S3 | **Trust policy.** (a) Two verified TPS with the same `policy_version` and different digests → `TRUST_POLICY_EQUIVOCATION`. (b) The highest TPS MUST list every held lower TPS in `prior_policies[]`, otherwise `TRUST_POLICY_EQUIVOCATION` (fork). (c) Computed reductions against the strongest values held (VTS, PTR, T0) MUST each appear in the arriving TPS's `lowering_history[]` with `in_policy_version` above the held version, otherwise the arriving TPS is invalid (`TRUST_POLICY_UNDECLARED_LOWERING`) and not used. Explained reductions need the per-project trust gate before they apply to a project that held the stronger value (`19` §10, `27`). (d) An unknown `floor_schema_version`, class or operator → `BINARY_BELOW_TRUST_POLICY` (read-only). |
| S4 | **Trust state.** (a) *Resolution:* a TSS is resolved iff its referenced root version is ≤ the effective root and its referenced TPS (version and digest) is held. Unresolved TSSs are never effective and never constrain. (b) *Anchored forks:* if an anchor (`24` §3) names a held resolved TSS A, resolved TSSs with sequence ≤ A.sequence outside A's `prior_states[]` ∪ {A} are **orphans**: reported (`TRUST_STATE_FORK_ORPHANS`, doctor CRITICAL), never effective, never constraints. (c) *Equivocation:* two resolved, non-orphan TSSs with equal sequence and different digests → `TRUST_STATE_EQUIVOCATION`. (d) *Admissibility:* in sequence order, T is admissible iff for every admissible lower L: `T.revocations ⊇ L.revocations`, `T.attestations ⊇ L.attestations`, `T.artifacts ⊇ L.artifacts`, certification sequences per release do not decrease, `T.references.root_version ≥ L's`, `T.references.trust_policy.policy_version ≥ L's`, and `(L.sequence, digest(L)) ∈ T.prior_states`. (e) Effective TSS = the highest admissible. A higher non-admissible resolved TSS → `TRUST_STATE_REGRESSION`. An unresolved TSS with sequence above the effective one → `TRUST_STATE_INCOMPLETE`. |
| S5 | **Negative set N** = every verified revocation target in K − TPS `unrevokes` ∪ every release with a verified REJECTED or WITHDRAWN certification **not lifted** per MS-2. |
| S6 | **Certification view** per final release (§6). |
| S7 | **Release-local requirements.** A release, candidate or artefact statement's `trust_references` (state sequence, policy version, root version) and a certification's `issued_under` are requirements for that statement only. Its ingress (or visibility) needs the effective state to meet them; otherwise that ingress refuses with `RELEASE_REFERENCES_UNKNOWN_STATE` (remedy: refresh). They never change global status. |
| S8 | **Hints.** The lock's `trust_references` and the VTS per-project record's last state → `TRUST_STATE_HINT_MISMATCH` when above the effective state. Warning only. |
| S9 | **Trust-state axis** = `EQUIVOCATION` \| `REGRESSION` \| `INCOMPLETE(n′)` \| `KNOWN(n)`. |
| S10 | **Freshness axis** (`24` §4.1): `ANCHORED` \| `WITNESSED` \| `BELOW_ANCHOR` \| `UNANCHORED`, from anchors and OP-7. |
| S11 | **Persist.** Newly verified statements are copied into the VTS (union). High-water components rise monotonically. The PTR is written only inside an install transaction or `gov trust refresh`, as the **union** of the current PTR, the target's statements and VTS knowledge (`18` §5.2). A verified statement is never removed from `governance/trust/`. |
| S12 | **Chain reset.** A TSS chain can be restarted only by a root-signed TPS `state_chain_reset {after_sequence, genesis_digest}`. It is used after a trust-state key compromise with a forked history. |

Evidence: `evidence/P4r3-trust-state-model.json`, 34 scenarios, all agree.

## 6. Certification view

For a final release statement digest X:

| View | Condition | May it relax a control? |
|---|---|---|
| `REVOKED` | X ∈ N | no; refuse per effect |
| `WITHDRAWN` / `REJECTED` | a verified negative certification for X not lifted per MS-2 | no; refused outright when TPS `gating.refuse_known_*` |
| `CERTIFICATION_UNREFERENCED` | a verified CERTIFIED for X exists, but no admissible TSS references it | no |
| `CERTIFIED_AS_OF(n)` | effective TSS n references CERTIFIED C for X; C references an ACCEPTED attestation for X's `promoted_from_candidate`, itself referenced by TSS n; no negative fact | **no** |
| `CERTIFIED_CURRENT(n)` | `CERTIFIED_AS_OF(n)` ∧ freshness proof (§13) ∧ trust state `KNOWN` ∧ freshness `ANCHORED` or `WITNESSED` | only under OP-3 mode B, and only to skip the update gate |
| `NOT_CERTIFIED` | none of the above | no |

## 7. Trust-state and freshness requirement by operation

The operation classes and the decision table are in `24` §4. In summary:

| Operation | Trust state required | Freshness required | Gate |
|---|---|---|---|
| C0 diagnostics, refresh, confirmations | none | none | — |
| C1 governed read | not `EQUIVOCATION`/`REGRESSION` | per OP-7 | — |
| C2 governed mutation (including project-state mutation under the installed release) | `KNOWN` | per OP-7 (`24` §4.3) | non-trust gates as policy |
| C3 `init`, `adopt migrate --batch 0` | `KNOWN`; release-local requirement met | `ANCHORED` or `WITNESSED` | `init_ack` trust gate (`27`) |
| C3 `update --apply` | as above | as above | mode A: `framework_update` trust gate always |
| C3 rollback, restore, downgrading recovery | as above | as above | `downgrade` trust gate |
| C3 `kernel reinstall` (same statement digest) | not `EQUIVOCATION`/`REGRESSION` | none (integrity remedy; identity unchanged) | — |
| C3 evaluation-candidate install | as above | as above | `evaluation_candidate` trust gate plus flag |

There is no override for `INCOMPLETE`, `REGRESSION`, `EQUIVOCATION`, `BELOW_ANCHOR` or `UNANCHORED` at ingress. The
remedies are supplying the missing signed metadata, re-anchoring, or a root rotation.

## 8. Revocation state

- Revocations accumulate (S5); an admissible TSS must contain every revocation of every admissible lower TSS.
- A revocation delivered alone is effective immediately (MS-2).
- Unrevocation exists only as a root-signed TPS `unrevokes`.
- `refuse_install` applies at ingress, rollback and restore. `refuse_operation` also applies at use: the release becomes
  `INELIGIBLE` and the policy root falls back to the EmbeddedSnapshot ⊔ floor.
- A security-relevant revocation SHOULD come with a TPS raising `eligibility.min_release_sequence`. Binaries compiled
  afterwards refuse the release even where the revocation never arrives, and anchored machines refuse it once they hold
  that TPS.

## 9. Root-rotation state

- A root version N+1 is known once its dual-threshold link is held.
- A TSS referencing an unheld root version is unresolved (S4 a). Above the effective sequence it makes the state
  `INCOMPLETE`: C2 and C3 refuse until the link is supplied.
- A key removed in N+1 is `SIGNER_REVOKED` on every verifier holding N+1.
- **RS-1:** a thief of a later-removed key can sign statements referencing only old roots, and a machine that never
  receives N+1 cannot tell. Such a machine is bounded as in `24` §10. Under OP-7 (a)–(c) it performs no governed mutation
  unless anchored at or above a state that includes N+1; a pin or human anchor naming a TSS that references N+1 makes it
  `BELOW_ANCHOR` or `INCOMPLETE`.

## 10. Replay protection

| Replay | Binding that defeats it |
|---|---|
| cross-lineage or cross-profile | `trust_root_id`, `trust_profile` (`05` SV-10) |
| cross-type | payloadType ↔ purpose ↔ `_type` compiled; PAE |
| certification or attestation for another release | full digests plus `release_id` equality |
| older TSS or TPS presented as current | knowledge union; admissibility; `prior_states[]`/`prior_policies[]`; anchors (never below) |
| forked TSS history across missing intermediates | cumulative `prior_states[]` (S4 d) |
| older witness (OP-7 c) | highest witness `issued_at` in the VTS; expiry window (`24` §6) |
| gate answer reused for another digest or project | trust-gate confirmation bound to kind, `project_trust_id` and digests; consumed once (`27` §3) |
| CERTIFIED after WITHDRAWN | MS-2 lifting rule |
| older binary as upgrade | TBM high-water (`25` §5 A7) |

## 11. Rollback of trust metadata

| Attack | Result |
|---|---|
| A1 serves an older TSS, TPS or root | knowledge only; effective state unchanged on machines holding more; below-anchor on anchored machines |
| A2 deletes `governance/trust/state/` | no effect on VTS-holding or anchored machines. Fresh machines are `UNANCHORED`: read-only under OP-7 (a)–(c); labelled under (d). |
| A2 swaps in an older eligible release | judged at the machine's effective state (floors joined, revocations and minimum sequence held); refused at ingress without a trust gate; per-project record downgrade detection (`20` §9) |
| A2 edits lock references | warning (S8) |
| A3 deletes or rewrites the VTS | the machine becomes `UNANCHORED` (RS-3) |
| A4 redirects `HOME`, `XDG_*`, `GOV_*` | no effect; account database |
| Trust-state key thief publishes a TSS that omits revocations, or forks | `REGRESSION` or `EQUIVOCATION` on verifiers holding the lower TSS; anchored verifiers orphan the fork (S4 b) |

## 12. Offline operation

- **Using an installed eligible release:** no network. The permitted classes depend on the anchor (`24` §4.3).
- **Installing from a local bundle:** works offline when the machine is anchored (a pin or confirmation needs no network)
  and the bundle carries the anchored epoch's statements.
- **Air-gapped propagation:** `gov trust export` and `gov trust refresh --from`.
- **Under OP-7 (c):** stateless use beyond witness expiry refuses governed mutation.

## 13. Freshness proof (OP-3 mode B; OP-7 (c) witness)

A freshness proof exists for effective TSS n iff all of these hold:
- (a) `expires_at` is non-null;
- (b) the local clock is earlier than `expires_at`;
- (c) the local clock is later than the highest verified `issued_at` recorded in the VTS high-water;
- (d) TSS n's `issued_at` is not older than the newest witness this VTS has accepted;
- (e) the trust state is `KNOWN`.

The clock is trusted (TA-7) only for this decision. Time never removes trust: expiry never invalidates an installed
release, authenticity or a revocation.

## 14. Recovery semantics

| Situation | Recovery |
|---|---|
| VTS missing or corrupt | Rebuilt from T0 ∪ PTR ∪ bundles; the machine is `UNANCHORED` until re-anchored (OP-6 and OP-7 ceremony). |
| PTR deleted | The next install transaction or refresh rewrites it as a union. |
| `INCOMPLETE` / `BELOW_ANCHOR` | Supply the statements (`gov trust refresh --from`). |
| `REGRESSION` / `EQUIVOCATION` | Governed mutation and ingress refused. The owner rotates the `trust-state` purpose (root N+1) and, if histories forked, issues a TPS `state_chain_reset`. Anchored machines already orphan the fork. |
| Erroneous TSS publication | Publish a correct n+1 that includes every lower revocation and the full `prior_states[]`. |
| Certification key stolen | Root removes the key. A forged CERTIFIED is visible only with an attestation and a trust-state reference, and a forged lift needs both (MS-2). |
| Build-attestation or release-artifact keys stolen | `25` §7. |

## 15. Purpose blast radius (trust-state and certification; corrects revision 2)

| Stolen alone | Worst case |
|---|---|
| `trust-state` | Freeze of C2 and C3 on verifiers that receive an unresolvable, forked or regressive statement above their effective state. It lasts until the next honest TSS supersedes it or a root rotation removes the key. It cannot lift negatives, create certification, or regress honest successors. |
| `certification-status` | Publishes CERTIFIED or negatives. Negatives take effect (denial of service). CERTIFIED stays unreferenced; it can neither lift a negative nor become visible. |
| `release-candidate` | Candidate statements with inflated references constrain only their own ingress (S7). |

## 16. Residuals

RS-1…RS-4 are stated exactly in `24` §10.
