# Output 28 — Why three classes survived three revisions, and what revision 4 changes in kind

> **RoT-1 revision 4 — PROPOSED, pending fresh independent reviews; not approved, not implemented.**
> New in revision 4. HO-0005 §2a requires the pack to state, for each blocking class, why earlier corrections left a
> remainder, and to prefer mechanisms that remove the lower-trust input from a decision over mechanisms that add
> conditions to it. This file does that, and lists the attacks the architect ran against revision 4 before handing it on.

## 1. The recurring class

Every rejection since 4.1.3 is one class: **a lower-trust input yielding a current, higher-trust fact.** The review of
revision 3 found it three more times:

| Class | Lower-trust input | Higher-trust fact it produced | Findings |
|---|---|---|---|
| BC-1 | a threshold-1 kernel's POLICY_PRECEDENCE, its absence, or a root-signed TPS applied without a per-project gate | the project's effective security configuration | RV3-H1 (root of RV3-M5; precedence case of RV3-M7) |
| BC-2 | whichever Trust State Statements the repository or transport supplies, plus at most one threshold-1 key | a current, anchored trust state | RV3-H2 |
| BC-3 | the `release_commit` a threshold-1 final release statement names | the source of the trusted computing base | RV3-H3 |

## 2. Why each correction left a remainder

The same pattern explains all three: **each revision added conditions downstream of a choice that a lower-trust
party still made.** The conditions were correct, but they were evaluated over the lower-trust party's choice, so the
attacker could satisfy them by choosing differently.

### 2.1 BC-1 — constitutional surface

| Revision | What it added | Lower-trust input left in the decision | How the review exploited it |
|---|---|---|---|
| 1 | release-statement floors for selected keys | the release chose which keys counted | review r1 |
| 2 | 145 floor keys registered in the Trust Policy | the kernel supplied every unregistered leaf | R2-H1 (P1: authority, secret, R5 gate) |
| 3 | the whole payload classified; default deny for additions; per-key precedence **join** of kernel and registered rules; strength detection over the overlay | (a) the kernel's precedence rules were an input to the join, and the order used for the join measured only refusals; (b) absence of registered content was not a check; (c) the strength detector read the overlay (an input) rather than the effective policy (the output) | RV3-B-A01 (precedence moved to `immutable`, executed); RV3-D-A10 R07 (file deleted, 66 of 85 rules `immutable`); RV3-D-A02 (TPS tightening without a gate) |

**Why a remainder survived.** Revision 3 tried to make the kernel's contribution safe: register it, classify it, join
it. Each safeguard was a condition on content the kernel still chose. The join is where it failed. A join over an order
that ranks `immutable` above every other mode lets the kernel remove project strengthening by making its own rule
"stronger". Deleting the file then makes every rule the default, which is `immutable`. The detector was also blind:
it compared overlay bytes, and the overlay had not changed.

**What revision 4 changes in kind** (`23`, `19` §5, `26` §6):

| Mechanism | Removes the input, or adds a condition? |
|---|---|
| The project-layer precedence of every key comes from Trust Policy registrations only. The kernel's POLICY_PRECEDENCE is never an input to effective policy. It must equal its registration exactly, or the release is ineligible (`precedence_unregistered`). | **removes** the kernel from the decision |
| Every registered file and leaf is required. Absence is refused (`surface_required_missing`). An unregistered or missing pinned value resolves to the registered EmbeddedSnapshot value or a typed refusal of the dependent decision point. | **removes** absence as an input that changes semantics |
| The project layer is a directed join. Admitted strengthening is applied, unadmitted weakening is refused, and no refusal discards an admitted component. | **removes** the kernel value's ability to veto a project strengthening (see §4, A-R4-01) |
| Project-owned strength is a set of requirements evaluated over the effective policy and every classified overlay input, whatever changed it. | **replaces** an input-based detector with an output-based one |
| Migrations are default-deny over a root-registered Overlay Surface. | **removes** `release-final`'s power to name an arbitrary overlay target |
| The precedence order is sound in both directions. It is used only where two root-signed registrations are compared: TPS computed reductions, and a project's held registration. | a condition, applied only to root-threshold inputs |

### 2.2 BC-2 — anchor satisfaction and currency

| Revision | What it added | Lower-trust input left in the decision | How the review exploited it |
|---|---|---|---|
| 1 | authenticated statements | whichever authentic statements a supplier chose were treated as current | review r1 |
| 2 | monotonic retained state; compiled T0 | on a fresh machine, the repository's selection was current knowledge | R2-H2 (P4-B5) |
| 3 | anchors (pin, human, witness); freshness axis; C3 needs an anchor | (a) an anchor was satisfied by the **sequence number** of the effective TSS, and the supplier picks which TSS is held; (b) a pin carried no time bound, so "anchored once" meant "anchored for ever"; (c) the witness was a TSS signed by the threshold-1 trust-state key | RV3-B-A12 and RV3-D-A12 (higher unchained TSS); RV3-B-A02 (stale pin); RV3-B-A06 (minted witness); RV3-D-A15 (revoked binary accepted on pinned CI) |

**Why a remainder survived.** The anchor was a correct idea evaluated over the wrong value. The anchored epoch was
compared with a number that the supplier's statements determine, so a statement numbered above the anchor, which never
chained through it, satisfied the check. Currency then rested on the anchor having existed at some past moment.
Nothing independent of the supplier said how old that moment was allowed to be.

**What revision 4 changes in kind** (`24`, `17` S4):

| Mechanism | Removes the input, or adds a condition? |
|---|---|
| **Inclusion anchors.** The anchored `(sequence, digest)` must be held and must be the effective TSS or in its cumulative chain. Statements that do not descend from the anchor are never effective, whatever their number. | **removes** the supplier's sequence number from the decision |
| **Mandatory pin validity.** A pin carries `valid_until`, capped by the Trust Policy. Outside validity it is not an anchor. | **removes** the unbounded "anchored once" input; adds TA-7 for pinned machines (stated) |
| **Currency proof for C3 and binary acceptance.** A proof is an anchoring event within the C3 window, an in-gate typed state fingerprint (no clock), or witnesses at a compiled threshold of at least 2. | **removes** aged anchors from trust ingress |
| **Witnesses are a separate purpose** (`freshness-witness`, KS-11). A witness names an existing TSS digest and cannot create state. | **removes** the trust-state key from currency decisions |
| **No surface says `current`.** Surfaces show the anchor, method, as-of time, age, and a currency proof or `CURRENCY_UNPROVEN`. | removes a label that overstated a fact |
| **Pins and decision pins are honoured only if the governed account cannot write them.** `gov` runs repository-supplied commands under write confinement. | **removes** the governed account from the anchor's writers |

### 2.3 BC-3 — built-source legitimacy

| Revision | What it added | Lower-trust input left in the decision | How the review exploited it |
|---|---|---|---|
| 1–2 | binaries authenticated under `release-final` | one threshold-1 key chose the binary | R2-H3 |
| 3 | `release-artifact` ×2, independent build attestation, TSS reference, Trust Base Manifest | every one of those signers checked the bytes against `release_commit`, chosen by the threshold-1 final | RV3-B-A08 (computed); RV3-D-A03 (OP-4 "no") |

**Why a remainder survived.** Revision 3 multiplied the signers and made them independent. Every one of them, however,
answered "are these bytes a build of the named commit?" None answered "is the named commit the one that was
independently verified?" The name itself stayed a threshold-1 choice.

**What revision 4 changes in kind** (`25`, `04` V8, `05` §7):

| Mechanism | Removes the input, or adds a condition? |
|---|---|
| The binary's source identity `(release_commit, source_tree_digest, build_inputs_digest)` is taken from an ACCEPTED verification attestation of the candidate, referenced by the effective TSS. V8 requires the final to carry the same source as its candidate. `verify-artifact` A4b and every custodian check it. | **removes** `release-final` from the choice of source |
| A REJECTED attestation, or a negative for the final or the candidate, refuses the binary (`ARTIFACT_SOURCE_REJECTED`). | a condition over root- and trust-state-published facts |
| Owner option: register production sources at root threshold in the Trust Policy. | would **remove** the verification-attestation key from the choice too (`21` OP-2) |

## 3. What remains a lower-trust input in revision 4, and why it is bounded

Every trust design must start somewhere. Revision 4 lists what still enters a decision from outside the root threshold
and states each bound. None of these produces a current fact that a higher class did not issue.

| Input | Decision it enters | Bound | Where |
|---|---|---|---|
| Human typing a fingerprint from an independent channel | anchor; in-gate currency proof | TA-5 | `24` §3, `06` §3 |
| Operator provisioning a pin or decision pin | anchor; automation approval | TA-9 restated; integrity predicate; `valid_until` / `expires_at` | `24` §3.2, `27` §3.2 |
| Local clock | pin validity; C3 currency window; OP-7 (b)/(c) | TA-7; the clock high-water is raised only by witnesses; far-future statements refused; root-signed reset | `24` §8, CR-06 |
| Verification-attestation key | the source of a production binary | route S needs it together with the release keys and pipeline input; OP-2 may raise it to threshold 2 or add root-registered sources | `25` §7, `21` OP-2 |
| Freshness-witness keys (OP-7 (c) only) | currency on stateless machines | a separate purpose that cannot create state; compiled threshold ≥ 2 for C3; the owner may allow 1 for C1–C2 only | `24` §3.3, `21` OP-7 |
| Repository-delivered state below or at a valid anchor | C1/C2 on machines anchored before a revocation | the unavoidable core (RS-1), shown with age, never labelled current, never C3 without a fresh proof | `24` §10 |
| Project overlay (T4) | project configuration | A2's authority (LR-4); every weakening against a recorded vector is reported and gated | `26` §6 |

## 4. Attacks the architect ran against revision 4 before hand-off

Each of these is a candidate instance of the recurring class, tested against the revision-4 rules. None is a review
attack. The evidence files are named.

| ID | Attack | Result on revision 4 | Evidence |
|---|---|---|---|
| A-R4-01 | **Composition.** A Trust Policy raises the never-index floor by a class the project did not list, while the project had added `confidential`. The 4.1.5 replacement semantics (which revision 3 kept) refuse the whole project override. | Revision-3 effective policy: `confidential` is lost, and the customer file is indexed and retrievable on the real 4.1.5 binary. Revision 4's directed join keeps it, and the file is excluded. This led to the directed-join rule (`19` §5.3). | `P1r4` part D |
| A-R4-02 | **Route S.** Steal the verification-attestation, release-candidate and release-final keys, control the build input, and leave downstream custodians honest. | ACCEPTED. The true minimum under the architecture minimum is stated in `25` §7 and `21` OP-2, with owner options that refuse it (root-registered source; verification threshold 2). | `VA4` |
| A-R4-03 | **TPS tightening without reclassification.** A Trust Policy registers `immutable` for a key still classified `set_superset`. | Inventory lint refuses it (exit 4). A consistent tightening is a computed reduction (exit 6 without `lowering_history`; per-project gate). | `P1r4` part B checker rows; `CSI-selftest` S53, S54 |
| A-R4-04 | **Historical migrations.** The 4.1.5 payload's migrations carry `set_lock_field`. | The checker refuses them (exit 3). 4.1.6 must re-issue the migration chain without lock operations (`11` WP-18). | `CSI-check-release-4.1.5.json` |
| A-R4-05 | **Pattern precedence keys.** A precedence rule whose key is a pattern has no concrete leaf, so no direction can be read from the inventory. | The direction is inferred from the registered modes, which the lint keeps consistent with the leaf classes. Without that fallback, a join would have fallen to `immutable`. | `csi_lib.effective_project_rule` |
| A-R4-06 | **Pin rewritten by a `gov`-run repository command** (RV3-B-A03 replayed on the real 4.1.5 binary). | The written pin is owned by the effective uid with mode 0644, so it is ignored (`UNANCHORED`). Under confinement, the child cannot write the pin location. | `rerun-RV3-B-A03-A14-A16-probes.json`; `P4r4` RV3-B-A03 |
| A-R4-07 | **Trust-state key on a machine anchored before a revocation.** Present a descendant of the anchor that omits the later revocation. | Admitted, as the stated core. Withholding the revocation already had that effect; the key adds no reach. On a machine holding the revocation, the descendant is non-admissible (REGRESSION, freeze). | `P4r4` matrix rows M4/M6B; TS_KEY_BLAST_RADIUS |
| A-R4-08 | **Untracking ignored files** under the revision-4 ignore rules. | The idiom lists nothing, and a fresh clone keeps the occupation (`COMPLETE`). | `RV3-D-A05-A07-rerun-r4-layout.json`; `LR2` |
