# 11 — Architectural correction delta (revision 3 → revision 4)

This delta is architectural only. It states each blocking **class** and what closes it. It is not a patch list and it
implements nothing. The next architect receives the completed findings (`10-BLOCKING-FINDINGS.md`). The mechanisms are
the architect's choice. A re-review will attack each class with new held-out attacks, not tick these items.

D-0008 and ARCH-0002 remain PROPOSED. Nothing here approves them.

## CD3-0 — Retain (confirmed sound under reproduction)

- **Authentication core.**
  - compiled root chain;
  - purpose-bound DSSE statements;
  - the compiled purpose whitelist and KS-1…KS-10;
  - the single `authenticate` constructor;
  - VerifiedBlobs, KernelSnapshot and EmbeddedSnapshot;
  - GovernedFs and the Protected Path Set.
- **Constitutional Surface.**
  - the Constitutional Surface Inventory as a root-signed TPS section;
  - default deny for added files and keys;
  - the closed floor vocabulary and value joins.
- **Trust state.**
  - release-local references;
  - resolution, equivocation and cumulative `prior_states`/`prior_policies`;
  - computed lowering with cumulative history;
  - sticky negatives.
- **Freshness and authorisation.**
  - no trust ingress without an anchor;
  - unanchored machines read-only under OP-7 (a)–(c);
  - local trust-gate confirmations, with repository records treated as requests.
- **Binaries.**
  - `release-artifact` at threshold ≥ 2;
  - the independent build attestation;
  - the Trust Base Manifest and its resolution (A6).
- **Legacy layout.** The legacy-path-occupation layout and property LP-1 on the intact layout.
- **Transactions.**
  - the transaction area outside Git with a VTS registry;
  - union trust records;
  - VU-11 and VU-12.

## CD3-1 — Constitutional-surface soundness for project-owned strength and for absence (closes BC-1: RV3-H1; absorbs the root of RV3-M5 and the precedence case of RV3-M7)

**Class.** Two mistaken equivalences:
- a rule that refuses more project overrides is at least as strong;
- every leaf present being classified means the registered constitution is in force.

**What closes the class:**

1. **An order sound in both directions.** One order is used by E7, by the effective-policy join and by TPS computed reductions. For the project layer it must preserve two things:
   - the refused weakenings;
   - the admitted strengthenings.

   A change that removes admitted project strengthening is a **reduction**, whoever makes it (kernel, TPS, file deletion). A join must not discard strengthening that the registered rule admits.
2. **Exact precedence registration.** A kernel precedence rule, `default_mode` or `layers` differing from its named TPS registration is refused, as unregistered values already are. A TPS change to a registered rule that removes admitted strengthening is a computed reduction. It carries `lowering_history` and the per-project `policy_lowering` gate.
3. **Project-owned strength over effective policy.**
   - It is computed over the applied project strengthening, before and after every kernel, TPS, migration, recovery, remedy or overlay change.
   - Rule (20), the `weakening` gate and `PROJECT_STRENGTH_WEAKENED` consume that computation, not an enumerated list of overlay categories.
   - Migration writes are default-deny over overlay targets.
4. **Absence is not neutral.**
   - A registered constitutional file or leaf missing from a release is refused, or it resolves to a defined value at least as strong as the registered one, never to an unspecified consumer default.
   - The absence of POLICY_PRECEDENCE, or of any rule, changes no key's effective project-layer semantics.

**Evidence required:**

| ID | Kind | Content |
|---|---|---|
| P1r4 | executed on real consumption | RV3-B-A01 for each strengthening mode; D-A10 R07 (POLICY_PRECEDENCE deleted); the honest-owner tightening. Each is refused, or project strengthening remains effective. Harm assertions: authority, indexing, gate. |
| Reference | computed | D-A01 and D-A02 on the corrected order: no unsound pair; a TPS tightening that removes strengthening is a computed reduction. |
| Checker self-test | executed | adds `immutable` moves, precedence deletion and the D-A10 R01–R09 removals |
| Migration cases | reference | RV3-B-A18 migration cases need the `weakening` gate |

## CD3-2 — Anchor satisfaction and anchor currency (closes BC-2: RV3-H2)

**Class.** Two mistaken equivalences:
- an anchor number is met, so the anchored state is in force;
- a machine anchored once is current.

**What closes the class:**

1. **Inclusion semantics for every anchor kind.** This covers pins, human confirmations, witnesses and retained anchors.
   - An anchor is satisfied only when the anchored `(sequence, digest)` is held **and** is the effective TSS or lies in its cumulative chain. Otherwise the machine is `BELOW_ANCHOR`.
   - The freshness axis, `17` S4 orphan handling, the pin schema and the reference model use one definition.
2. **Currency bounded or disclaimed exactly.** Either an anchor carries a currency bound that neither the repository writer nor the transport can defeat, or the architecture states exactly the operation classes and binary acceptance it permits when the anchor is not current. In the second case:
   - it is never labelled `current` beyond a stated bound;
   - the owner is told, per OP-7 option, who can select which state and for how long.
3. **No single threshold-1 currency authority.** Under any witness option, one of three must hold:
   - the witness authority's purpose and threshold are stated separately;
   - its compromise consequence is stated;
   - C3 and binary acceptance never rest on a witness alone.
4. **Anchor and decision-pin integrity is part of the anchor definition.** It covers who can write a pin after provisioning, and it rules out `gov` executing repository-supplied commands in the pin-reading account before a trust decision (RV3-M2, CR-03).
5. **Restated blast radius.** `17` §15, `05` §1, TB-3 and `21` OP-7 are restated from the corrected rules.

**Evidence required:**
- **Reference model P4r4**, independent of P4r3, meeting all of these:
  - RV3-B-A02, A06, A12 and RV3-D-A12, A15 refuse, except the stated core (anchored before the revocation and never contacted again), labelled with its bound;
  - in the full machine × OP-7 × adversary matrix (RV3-B-A13), only stated-core rows admit revoked state, and none is labelled `current`;
  - at least one scenario **fails** when inclusion is replaced by sequence comparison, and one uses a realisable artefact construction (RV3-M8, RV3-M9).

## CD3-3 — Built-source legitimacy of production binaries (closes BC-3: RV3-H3)

**Class.** The mistaken equivalence is "reproduced from the named commit, therefore built from verified source".

**What closes the class:**

1. **Bind the source to independent verification.** The source and build inputs compiled into a production binary must be bound to source that an independent verification accepted.
   - The verification attestation, or a statement referencing it, names the candidate's `release_commit` and build inputs.
   - Promotion to final requires the final's `release_commit` to equal the attested candidate's.
   - This is checked by every verifier (V8), not only by the producer tool.
2. **Apply the binding everywhere it is consumed.** `verify-artifact` requires it, and so does every custodial signing rule: build attestation, release artefact, any root co-signature, and TSS publication.
3. **Re-derive the true minimum capability set for an accepted malicious binary** from the corrected rules. State it in `25` §7, `05` §3, TB-3, OP-2 and OP-4.

**Evidence required.** Each of these is refused:
- RV3-B-A08;
- a variant whose candidate is REJECTED;
- D-A03 (OP-4 "no").

RT-92 is extended accordingly.

## CD3-4 — Owner options restated from the corrected rules (closes BC-4)

| Option | Required restatement |
|---|---|
| OP-7 | (a)–(d) consequences under the CD3-2 semantics. Add a pin-currency parameter. Offer (c) with a witness authority above a single threshold-1 key, with custody consequences. Scope the (d) residual to binaries whose compiled TSS predates the newest TSS (RV3-L6). |
| OP-2 | Binary blast radius from CD3-3. Present the `release-final` threshold and root co-signature relative to CD3-3. Correct the `release-final` sentence (RV3-L2). |
| OP-4 | Consequences of "no" after CD3-3. |
| OP-3 | Decision-pin integrity (RV3-M2). |
| All | Nothing decided; proposals labelled. |

## 5. Rule text affected (D-0008 and ARCH-0002; to stay PROPOSED)

| Rule | Class | Change required |
|---|---|---|
| (3) and (6) | CD3-1 | An order sound in both directions; exact precedence registration; absence semantics |
| (7) and (19) | CD3-2 | Inclusion anchors; currency bound or exact disclaimer; witness authority |
| (9) | CD3-3 | Built source bound to independently verified source |
| (20) | CD3-1 | Project strength computed over effective policy |

## 6. Non-blocking items the next revision must carry or close

These do not change the verdict. Each is a bound, testable requirement.

| Item | Requirement | Acceptance test |
|---|---|---|
| RV3-M1 | CR-01: a lifting CERTIFIED references an attestation post-dating the negative | RV3-B-A05: the negative remains; with a new attestation, a lift needs ≥ 3 distinct keys |
| RV3-M2 | CR-03: pins and decision pins ignored when writable by the effective uid; TA-9 covers integrity after provisioning | RV3-B-A03 replayed: pins written by `gov verify product`'s child are ignored; the (a)–(e) cases of CR-03 |
| RV3-M3 | CR-06: only trust-state witnesses raise the clock high-water; far-future `issued_at` refused at ingest; root-signed reset | RV3-B-A07 |
| RV3-M4 | CR-04: reconcile the artefact playbook with S4(d) | RV3-B-A09: holders of TSS 11 reach `KNOWN(12)`, artefact `ARTIFACT_REVOKED` |
| RV3-M5 | CR-02 (operation × target whitelist inside `governance/overlay/`); totality via CD3-1 (3) | RV3-B-A18 targets need the `weakening` gate; an out-of-overlay target is refused before any write |
| RV3-M6 | C-1 broadened: LR-2 states the reachable outcome of occupation removal **or** a Git restore of pre-migration paths (legacy verified install; retrieval without RoT-1-era classifications; legacy writes to `governance/trust/**` and the overlay). Only these bounds hold: RoT-1 fails closed, strength weakening is detected where recorded, and LR-4 applies. Doctor names mixed layouts. | Replay C A04–A06 and D-A05/A06: assert the legacy outcome as documented, RoT-1 `PARTIAL`/`KERNEL_TAMPERED` refusal, and `PROJECT_STRENGTH_WEAKENED` on a recorded machine |
| RV3-M7 | Defined fallback for missing or unregistered pinned and members content: the registered EmbeddedSnapshot value, or a typed refusal of the dependent decision point. For non-kernel owner constitutional files: required presence recorded; absence fail-closed; included in the strength vector. | D-A10 R01–R09 replayed on the binary with harm assertions; an owner contract removed on a confirmed machine and on an unconfirmed machine |
| RV3-M8 | A7, the first-run self-check and R-ART-2 compare with the accepted-TBM high-water only | D-A13: a realisable TBM → TSS → artefact order is accepted; a genuine older binary is still `BINARY_T0_ROLLBACK` |
| RV3-M9 | Plan uses property assertions, not model reproduction. The oracle includes distinguishing scenarios. An RT exists for every RV3-B, RV3-C and RV3-D attack with binary-observable harm assertions (CR-11, CR-12). | Oracle fails under sequence-only anchors; `12` rows exist for RV3-B-A01…A18, RV3-C-A01…A10, RV3-D-A01…A18 |
| RV3-L1…L5 | CR-05, CR-07, CR-08, CR-09, CR-10 | as stated in B `04` |
| RV3-L6 | OP-7 (d) residual scoped to the newest TSS | option text review |
| RV3-L7 | the migration occupation not dropped by untracking ignored files (ignore-rule negation or non-ignored path); doctor names its absence | D-A07: a fresh clone after the idiom keeps the occupation, or doctor reports it |
| RV3-L8 | rotation playbooks re-sign retained honest statements of the removed key before publishing root N+1 | trust-state key rotation: anchored machines stay `ANCHORED` after the remedy |
| C-2…C-5 | cross-device transaction refusal; stray merge and partial-removal artefacts named by doctor; type by `st_mode`; full-register RT-50 with type-aware digests | as stated in C `04` |

## 7. Re-review entry criteria

1. **Classes closed.** CD3-1…CD3-4 are closed as classes in the pack, schemas, D-0008 and ARCH-0002, with D-0008 and ARCH-0002 still PROPOSED and not active.
2. **Evidence re-run.** The architect re-runs:
   - P1r4 (executed) and P4r4 (reference), per CD3-1 and CD3-2;
   - the `verify-artifact` source scenarios of CD3-3;
   - P3r3, unchanged;
   - every RV3-B, RV3-C and RV3-D probe, against the revision-4 rules and models.

   Each blocking attack is refused or removed by a design change, and each carried item's test is named.
3. **Response matrix.** It covers RV3-H1…RV3-I1, CR-01…CR-12 and C-1…C-5, with no "resolved" claim resting on untested evidence.
4. **Oracle and plan.** The conformance oracle distinguishes the corrected anchor semantics from sequence comparison, and uses only realisable constructions. The acceptance plan meets RV3-M9.
