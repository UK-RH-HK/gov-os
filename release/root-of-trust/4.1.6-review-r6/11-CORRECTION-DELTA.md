# 11 — Architectural correction delta (revision 6 → revision 7)

This delta is architectural only. It is not a patch list and implements nothing. For each blocking **class** it states:
- the invariant not yet established;
- whether closing it needs an engineering correction inside the architecture, a genuine owner product or security trade-off,
  or both (HO-0018 §2a);
- what would close it;
- the evidence the next review will require.

The mechanisms are the next architect's choice. The next reviewers will attack each class with new held-out attacks; they will
not tick these items. The next architect receives `10-BLOCKING-FINDINGS.md` and this file.

D-0008 and ARCH-0002 remain PROPOSED. Nothing here approves them.

## Routing

| Class | Findings | Remainder of | Unestablished root invariant (short) | Kind of fix | Route |
|---|---|---|---|---|---|
| **BC6-1** First-contact selector authority | RV6-H1 | BC5-1 (R2-H2/BC-2 ∩ R2-H3/BC-3); new instances | every value that selects lineage, state or evaluator at first contact is established first-hand by a party the stated root counts, or that party is itself a stated root atom | **ENGINEERING_CORRECTION**, **plus OWNER_TRADE_OFF** (who establishes first-contact values) | architect, then owner |
| **BC6-2** First-contact currency | RV6-H2 | BC5-1 ∩ R2-H2/BC-2 (currency); new instances | a first-contact selector of state is current now or within a mandatory, compiled maximum age, and never below monotonic state the machine holds | **ENGINEERING_CORRECTION**, **plus OWNER_TRADE_OFF** (maximum age of stored first-contact values) | architect, then owner |
| **BC6-3** First-hand environment manifest | RV6-H3 | BC5-2 (BC4-1/R2-H3); new instance | every byte-determining selection, placement, recipe, tool, upstream key and supplier-class fact is established at the registration's authority; diversity counts established identity | **ENGINEERING_CORRECTION** | architect |
| **BC6-4** Register over inputs; derived statements; plan detection | RV6-M2, RV6-M1; the false consequence statements of RV6-H1…H3 | BC5-4 | register completeness is defined and checked over every input value with its establishing party; statements derive from it; tests detect a missing selector independently of it | **ENGINEERING_CORRECTION** | architect |

Each blocking class is the recurring rejection class: **a lower-trust input yielding a current, higher-trust fact**.

| Class | Lower-trust input | Higher-trust fact obtained |
|---|---|---|
| BC6-1 | the trust-state publisher process (rank 3); the carrier-delivered, unadmitted candidate or documentation that names the sources and steps (rank 5); the platform package submitter (rank 5) | the lineage, the evaluator and the first TCB of a machine; the anchor of P1, P2, CIR and WR machines |
| BC6-2 | a replayed package, stored media or CI codes, or a stale or designated page (rank 5) | a revoked, including malicious, binary as the current TCB, also on a machine that holds its revocation |
| BC6-3 | the author of an environment manifest, the pipeline in a conforming process (rank 5) | the bytes of every production binary |
| BC6-4 | the scope of the architect's rule tables | the owner's view of consequences, and what the plan can detect |

## CD6-0 — Retain (confirmed by reproduction)

- **Everything review r5 CD5-0 retained** that this review did not contradict.
- **BC5-1 closures as stated.**
  - Compiled first-contact quorum; lineage from the typed value, never bundle order; compiled lineage under (c)/(d).
  - Evaluator binding FC-8; one code over a manifest.
  - Evidence: FA6 byte-identical over two runs (S2 refusals, S3 equality within its model, S4 5/5, S7 14/14).
- **BC5-2 closures as stated.**
  - No pipeline image record.
  - Components against upstream checksums; environment reproduction quorum; re-assembly; diversity check.
  - Evidence: ENV6 byte-identical (21/21); CS6 G_ENV within its model.
- **BC5-3 closed at the registration.**
  - First-hand derivation; candidate and kernel binding; E7 with AP-5's restrictors; verifier-side reductions.
  - Evidence: CON6 byte-identical (17/17); P4r6 G; CSI 78/78; B-A10 and D-A03 (`verify-registration` exit 3 on every
    non-first-hand proposal). Content on first-admission machines inherits BC6-1 and BC6-2.
- **Carried closures.**
  - Restrictor revocation only under the registration authority (P4r6 `R6-AP5r_*`, FA6 S5).
  - Source identity v2 (SRC6); KS-14; the OP-3 mode-B currency proof; user-writable installation classes (UW6).
  - Serialised admissions (ADM6 A11); records only inside the store (FA6 S6, ADM6 A15).
  - Evidence: all byte-identical, or identical except the unlocked mutant's race counts.
- **Running-machine currency.** B-A11 (352 rows, 0 `current`, 0 C3 on the thief descendant) and B-A12 (0 accepts with ≤ 1 key)
  were reproduced byte-identical.
- **Legacy containment.** R2-H4 is closed as a class (C `matrix6` reproduced; `01-REPRODUCTION.md`).

## CD6-1 — First-contact values established by the parties the root counts (closes BC6-1: RV6-H1)

**Class.** The mistaken equivalence is: *"a value agreed across independent sources is established by those sources"*.
Agreement shows that the sources carry the same value. It does not show who composed it. Revision 6 also never states:
- where the operator learns which sources to read and which steps to perform;
- who submits the package a signing service signs.

**Invariant not yet established.**
- Every value that selects the lineage, the state or the evaluator at first contact is established first-hand by a party the
  stated first-contact root counts. Such values are the first-contact manifest and code, the list of sources and procedure steps,
  and under OP-13 (c) the platform package. Alternatively, the party that establishes the value is itself an atom of the stated
  root, with computed sets.
- No such value is supplied by the candidate, by a carrier, or by a party the register does not name.
- Anchors, pins and witness inputs of running machines taken "from the channel" satisfy the same condition.

**What closes it (engineering).**
1. **Establishment of the manifest.** Either:
   - each designated source (and media) custodian publishes only a code over a manifest it derived itself: lineage from the root
     ceremony record, admitter set from the root-signed Trust Policy, state from a Trust State it verified with its own admitted,
     anchored binary; or
   - lineage and admitter set are fixed in a record produced at root threshold that the sources carry and the procedure checks,
     and only the state epoch is composed per Trust State (bounded by CD6-2).

   The owner trade-off below chooses between these and a stated composer atom.
2. **Lineage compiled into every admitter build**, under every OP-13 answer, so a genuine admitter never accepts another lineage
   (B-A01 part P row "attacker lineage, genuine admitter").
3. **Designation.**
   - The list of sources and the procedure steps are part of the root ceremony record and are delivered to operators outside any
     carrier of the release.
   - No unadmitted binary prints anything an operator uses to select; `gov trust fc-procedure` is not a first-install
     instruction.
   - `32` §10 FC-R2's bound, `06` §3 step 0 and `31` §9 TB-1′ are restated consistently.
   - The operator's prior knowledge of at least one source identity is stated as the core (TA-5′), as a root atom.
4. **Submission under (c).** The package is submitted by, or on authorisation of, the registration authority, and its digest is
   checked against the root-signed admitter list before signing. The submitter is a register row. The compiled-manifest
   construction is resolved (an admitter cannot list its own digest in a manifest compiled into itself).
5. **Running-machine inputs.** Human confirmations, pins and the witness service take the state fingerprint from a value
   established as in 1, never from the publisher alone (`24` §3.2, §3.3).
6. **Register, calculator, statements.**
   - Register rows name composition, designation and submission.
   - Calculator atoms for the composer, the designation and the submitter, over FA (seven answers), P1, P2k1, P2k2, CIR and WR.
   - Statements regenerated from the calculator: FC-ROOT, FC-KEY-THEFT, FC-CONTENT, OP-9-BYTES, `25` §6–§7, `21` OP-6, OP-7 (c),
     OP-13 and §17; D-0008 rules (16), (19), (25).
   - FA6 S3's platform branch uses the package's own manifest and a submitter-signed package.

**What no mechanism removes: an owner trade-off.** Who may establish first-contact values is a choice between operational burden
and a stated residual. The architecture must present these options with computed consequences and must not choose.

| Option | Who establishes lineage / admitter set / state | Residual that remains | Operational consequence |
|---|---|---|---|
| **F1-a** each designated source custodian derives the manifest first-hand before publishing its code | each source custodian, for all three | the stated root: compromise of every required source custodian | every source custodian operates an admitted, anchored `gov` and derives per Trust State; first contact is unavailable while any custodian lags; custodians become anchored machines to protect |
| **F1-b** lineage and admitter set fixed in a root-threshold record carried and checked by the sources; state epoch composed per Trust State | root threshold for lineage and evaluator; the trust-state purpose for the state epoch, as DR-18 already has it for publication and negatives | at first contact, the trust-state publisher selects the state epoch (never lineage or evaluator), within the CD6-2 maximum age | a root ceremony at every admitter-list change (already needed for `bootstrap.admitter_digests`); two published values, or a two-part code |
| **F1-c** the composer is accepted as a first-contact root atom for all three values | the trust-state publisher process | one rank-3 process selects the first TCB of every first-install machine; OP-13 (b)'s distinct custody adds nothing against it; P1, P2, CIR and WR anchors made after its compromise follow it | none added. A weaker residual an owner may choose only when it is stated with computed sets (FD-1 §2 (5)); a design removes it (F1-a, F1-b) |

**Evidence required for re-review.**
- B-A01 parts P and S, and D-A01 parts P and C (all seven answers, WR included), against the corrected procedure, executor and
  calculator. Each case is refused before an evaluator runs, or accepted only inside a restated root whose atoms include every
  party that composes, designates or submits.

## CD6-2 — First-contact currency bounded and monotonic (closes BC6-2: RV6-H2)

**Class.** The mistaken equivalence is: *"the value the operator uses at first contact is current"*. Revision 6 bounds currency
with an optional field and gives bootstrap mode no access to the monotonic state a re-admitted machine holds.

**Invariant not yet established.**
- A first-contact selector of state has currency "now" (a code read now from the sources) or within a mandatory maximum age that
  the admitter enforces against a compiled ceiling.
- On a machine with a verifier trust store, no admission selects a state below the store's anchor, admits a binary or admitter
  the store holds as revoked, or admits a binary below the store's accepted-TBM high-water.

**What closes it (engineering).**
1. **Mandatory age.**
   - Every first-contact manifest carries `valid_until`; `gov-admit` refuses a manifest without it or beyond the compiled ceiling.
   - This applies to codes read from sources, platform packages, provisioning media and codes provisioned into CI images.
   - Schema, `32` §3 and §7, and DR-04 are restated.
2. **Re-admission applies the store.**
   - Bootstrap mode reads the store's anchors, held negatives and accepted-TBM high-water.
   - It refuses a first-contact epoch below the highest anchor, a candidate or admitter revoked in held state (AP-4), and a
     candidate below the high-water (AP-8; RV6-L5). `31` R-ADM-3′ and R-ADM-8′ and `25` §5 are restated.
3. **Stored values under (c) and (d)** select no state older than the maximum age (see the owner trade-off).
4. **Residuals restated with the bound:** RS-B1 (including a malicious binary, which never "anchors next"), FC-R4 (media age),
   `32` §8 (CI images).
5. **Calculator.** A goal "revoked binary admitted at first admission or re-admission", with atoms for a replayed package, stored
   media or image codes, and a stale or designated page, over FA and re-admitted victims.
6. **Tests.** B-A01 part R; D-A02; D-A08; D-A01 S2.

**What no mechanism removes: an owner trade-off.** A stored value can be up to its maximum age behind the newest revocation, and
a stricter bound costs availability. The architecture must present these options with computed consequences and must not choose.

| Option | Residual | Operational consequence |
|---|---|---|
| **C-a** mandatory `valid_until` on every first-contact manifest; the owner sets a maximum per path (sources, packages, media, CI images) within a compiled ceiling | on first-install machines, admission of a binary revoked within the maximum age; none on re-admitted machines (store applied) | codes re-published, packages re-signed, media re-prepared and images rebuilt within the window; offline media expire |
| **C-b** stored values (packages, media, CI codes) select lineage and evaluator only; the state always comes from a code read now from the OP-13 sources | the stated root's own currency | first contact under (c), (d) and in CI needs online access to the sources; offline provisioning is lost |
| **C-c** C-a for sources and CI images, C-b for packages and media | as each part | as each part |

**Evidence required for re-review.** B-A01 part R, D-A02, D-A08 and D-A01 S2 against the corrected executor: refused
(`FIRST_CONTACT_MANIFEST_EXPIRED`, a missing-validity refusal, below-anchor or revoked-in-held-state codes), or accepted only
within the stated maximum age on a machine without a store.

## CD6-3 — The environment manifest established first-hand (closes BC6-3: RV6-H3)

**Class.** The mistaken equivalence is: *"reproduced from the manifest by independent parties ⇒ the manifest was legitimately
selected"*. Revision 6 moved revision 5's unestablished image record into the manifest content.

**Invariant not yet established.**
- Every byte-determining fact of an environment is established first-hand at the registration's authority, with a stated
  establishing party: component selection, placement, recipe content, assembly tool, the upstream key each checksum is verified
  under, and supplier-class identity.
- The pipeline selects none of them.
- OP-16 (b) diversity counts established identities, never labels.

**What closes it (engineering).**
1. **Manifest provenance.** Component selection, placement, recipe and assembly tool are registered source content, reviewed under
   OP-8 verification. Alternatively, they are derived from a source lockfile by a normative assembly function with no free
   content, which verifiers and custodians recompute.
2. **Upstream keys** are pinned per supplier in the root-signed Trust Policy. A manifest reference to a key is never a selector.
3. **Supplier class** is established from pinned key identity and disjoint component digests.
4. **Verification order** (RV6-L3): the verifier's environment before registration comes from the established manifest, and
   verification attestations name the `environment_id`.
5. **Register, calculator, statements.**
   - Register rows name manifest authoring and supplier-class establishment.
   - Calculator strategies for recipe, selection, label and upstream key, across OP-9 (d), OP-8, OP-2 and victims FA and CIR (D-A05 E1).
   - OP-16-ENV, `25` §7 and D-0008 rules (9) and (26) regenerated or restated.

**Not an owner trade-off.** The common-mode residual of trusted upstream suppliers is already OP-16 (a)…(c). Pinning keys adds a
root ceremony per supplier key change, which is an operational cost, not a new trusted party.

**Evidence required for re-review.** B-A02 A07a, A07b, A07c, A08 and A09 (executed with the real toolchain) against the corrected
ceremony and tooling: each refused before registration, or a conflict. Computed: INV-ENV, INV-ENV-PIPELINE and INV-ENV-B hold with
the added strategies under every answer of D-A05 E1.

## CD6-4 — Register over inputs, derived statements, independent detection (closes BC6-4: RV6-M2, RV6-M1)

**Class.** Revision 6 made the register complete **over its own rule ids**. Every selector review r6 found (composer,
designation, submitter, stored-value age, manifest author) lies outside those ids. The calculator and the plan derive from the
register, so none of them could see it. Three tests compare the model with itself (RT-159, RT-162, RT-183).

**Invariant not yet established.**
- The register's completeness is defined and checked over every **input value** of every decision, each with its role and
  establishing party. Inputs are every field of every statement, manifest and local-record schema, and every procedure input
  (sources, steps, stored codes).
- Every selector has a calculator strategy.
- Every consequence statement is generated, with a renderer that never merges atom classes.
- Every selector has at least one acceptance test whose input does not come from the register.

**What closes it (engineering).**
1. **Completeness over inputs.**
   - C2 is extended to schema fields and procedure inputs, and fails on a field or input without a role and establishing party.
   - D-A09 (251 fields; 193 unnamed, 28 without an establishing party, lexically) and B-A16 are re-run as checks.
2. **Calculator and statements** gain the strategies of CD6-1…CD6-3. `compact` is injective over atom classes, and
   `statements_check.py` S1 compares atom sets (RV6-M1; D-A06).
3. **Independent detection.**
   - Every review-r6 defect (D-A04's 15 rows) has a plan row, a register row and a failing instrument.
   - RT-159, RT-162 and RT-183 are each paired with held-out vectors that do not come from the register.
4. **Options restated** from the regenerated blocks; nothing decided; no proposal labelled anywhere.

**Evidence required for re-review.** D-A09 and D-A04 against revision 7: 0 unregistered selector inputs, and 15/15 defects
detected. B-A03 and D-A06: the renderer is injective, and the S1 atom-level check fails a merged rendering.

## 5. Rule text affected (D-0008 and ARCH-0002; both stay PROPOSED)

| Rule | Class | Change required |
|---|---|---|
| (7) | CD6-2 | held negative facts and anchors apply at every admission, re-admission included |
| (9) | CD6-3 | "build environments established first-hand" includes manifest selection, recipe, tool, upstream keys and supplier class |
| (16) | CD6-1 | the evaluator of a first admission is selected through values established by the parties the root counts; no unadmitted binary or carrier supplies the source list or steps |
| (19) | CD6-1, CD6-2 | first-admission selectors established first-hand; mandatory maximum age; no admission below held state |
| (22) | CD6-4 | the register is complete over input values with establishing parties |
| (23) | CD6-2, RV6-M6 | re-admission applies the store; the first-admission determination does not rest on a file the governed account can write |
| (25) | CD6-1, CD6-2 | first-contact root restated with composer, designation, submitter and age atoms, from the calculator |
| (26) | CD6-3 | the pipeline selects no manifest content; diversity by established identity |

## 6. Non-blocking items the next revision must carry or close

These do not change the verdict. Each is a bound, testable requirement. "CR6-B-nn" refers to reviewer B's
`04-CARRIED-REQUIREMENTS.md`; "CR6-C-n" to reviewer C's `04-CARRIED-REQUIREMENTS.md`.

| Item | Requirement | Acceptance test |
|---|---|---|
| RV6-M1 | CR6-B-03 (a) (also a closure criterion of CD6-4) | CR6-B-03 (i); D-A06 re-run |
| RV6-M3 | CR6-C-7 (a)–(e), plus: RoT-1 `init` on a tree holding `governance/overlay` or `governance/views` refuses, or evaluates `19` §9 item 5 over the pre-transaction overlay before commit; `init` is added to `19` §9's coverage | RT-16 as CR6-C-7 (f); an `init` over the executed C-A15 order-A prefix loses no classification and is not `COMPLETE` without the `weakening` gate; D-A10 re-run finds the rule |
| RV6-M4 | CR6-C-8 | CR6-C-8 (RT-99, RT-118 extended) |
| RV6-M5 | CR6-C-9 | CR6-C-9 (RT-81, RT-167 extended) |
| RV6-M6 | CR6-C-10, plus: the first-admission determination and move-aside read only the protected admission store (or an authenticated record) and never an unsigned file in a store the governed account can write; a first admission also moves aside the account verifier trust store for the lineage | CR6-C-10 tests; D-A07 re-run: a planted record in the account store does not suppress the move-aside, and planted anchors, project records and confirmations do not survive |
| RV6-L1 | CR6-B-04, strengthened for HO-0001 §4: every non-orderable unit's inventory row carries `security_classified` explicitly; the checker refuses a row without it | B-A10 K1–K3 exit 8; D-A03: an unflagged new file row is refused, a flagged one is listed (exit 8) |
| RV6-L2 | CR6-B-05 | text review; RT-127 |
| RV6-L3 | CR6-B-06 (inside CD6-3) | as CR6-B-06 |
| RV6-L4 | CR6-B-07 | as CR6-B-07 |
| RV6-L5 | CR6-B-02 (i), (ii) and CR6-C-12; the reference executor's `gov_run` and the shared vectors implement `09` R-ART-2 | B-A04 on the implementation: `BINARY_T0_ROLLBACK` at admission or at first trusted operation; RT-170 extended to a lower-TBM rollback |
| RV6-L6 | CR6-C-2 | RT-174; `kernel reinstall` on `PARTIAL(occupation)` leaves the occupation tracked |
| RV6-L7 | CR6-C-1 | RT-50, RT-122, RT-173 |
| RV6-L8 | CR6-C-6 | as CR6-C-6 |
| RV6-L9 | RV6-C-L3 clarifications: a store without a record; records bound to the binary's lineage; fixed store-name length | C `admtx6` T3a, T8 on the implementation |
| RV6-L10 | CR6-C-3 | RT-176 extended to `governance/overlay/` |
| RV6-L11 | CR6-C-11 | text review |
| RV6-L12 | `21` §17 states OP-16 (b) + OP-10 (a) (and every OP-10 × OP-16 pair) from the calculator | RT-127; D-A05 E2 re-run |
| RV6-I2 | RT-182 (capability-contract phase) | RT-182 |
| CR4-B-01, CR4-B-02, CR4-B-04, CR4-B-05; C-2 … C-6 | still specification only; carried with their earlier tests | as review r4 and reviewer C `04` |

## 7. Re-review entry criteria

1. **Classes closed.** CD6-1 … CD6-4 are closed as classes in the pack, the schemas, the register, D-0008 and ARCH-0002, which stay
   PROPOSED and not active.
2. **Evidence re-run against the revision-7 rules.**
   - (a) B-A01 parts P, S and C, and D-A01 parts P and C, under all seven OP-13 answers (WR included).
   - (b) B-A01 part R, D-A02, D-A08 and D-A01 S2.
   - (c) B-A02 (A07a/b/c, A08, A09; executed and computed) and D-A05 E1.
   - (d) D-A09 and D-A04 against the revision-7 register and plan.
   - (e) B-A03 and D-A06.
   - (f) Unchanged in what they refuse:
     - CS6 self-checks and invariants, P4r6, DA03r6, FA6, CON6, ENV6, SRC6, ADM6, UW6, ATTR6;
     - CSI self-test (78/78, or its successor);
     - the register and statement checks as extended;
     - the retained revision-5 instruments;
     - B-A11 and B-A12;
     - reviewer C's `matrix6` (property R2-H4, 0 violations) and `crashmig6` (with CR6-C-7: no post-recovery prefix `ABSENT` or
       served restricted material through an RoT-1 path).
3. **Response matrix.** It covers RV6-H1 … RV6-I2, CR6-B-01 … CR6-B-07, CR6-C-1 … CR6-C-12 and CD6-0 … CD6-4, with no "resolved"
   claim resting on untested evidence.
4. **Owner options.**
   - F1-a … F1-c and C-a … C-c are presented with computed consequences.
   - OP-6, OP-7 (c), OP-9, OP-13, OP-14, OP-15, OP-16 and §17 are restated from regenerated blocks.
   - No choice is made.
