# 11 — Architectural correction delta (revision 5 → revision 6)

This delta is architectural only. It is not a patch list and implements nothing. For each blocking **class** it states:
- the invariant that is not yet established;
- whether closing it needs an engineering correction inside the architecture, or a genuine owner product or security
  trade-off (HO-0014 §2a);
- what would close it.

The mechanisms are the next architect's choice. The next reviewers will attack each class with new held-out attacks; they
will not tick these items. The next architect receives the completed findings (`10-BLOCKING-FINDINGS.md`) and this file.

D-0008 and ARCH-0002 remain PROPOSED. Nothing here approves them.

## Routing

| Class | Findings | Remainder of | Unestablished root invariant (short) | Kind of fix | Route |
|---|---|---|---|---|---|
| **BC5-1** First-contact root of trust | RV5-H1 | BC4-2 (R2-H2/BC-2 ∩ R2-H3/BC-3) at its intersection with BC4-4; the instance is new | first-admission selectors (lineage, quorum, evaluator) not selectable by the values they govern; the first-contact root stated exactly | **ENGINEERING_CORRECTION** for enforcement and statements, **plus OWNER_TRADE_OFF** for the composition of the first-contact root | architect, then owner |
| **BC5-2** Byte-determining build environment | RV5-H2 | BC4-1 (R2-H3/BC-3); the instance is new | every byte-determining input established first-hand or a stated residual; the pipeline selects none | **ENGINEERING_CORRECTION** to assign the selector, **plus OWNER_TRADE_OFF** for the common-mode environment that remains | architect, then owner |
| **BC5-3** First-hand constitutional content | RV5-H3 | BC4-3 (R2-H1/BC-1) at its intersection with BC4-1's first-hand principle; the instance is new | registered content derived first-hand and bound to verification of exactly the registered candidate; E7 applies AP-5's restrictors | **ENGINEERING_CORRECTION** | architect |
| **BC5-4** Complete register and derived statements | option statements (`D-synthesis/04` §2); RV5-M5; D-A07 | BC4-4 | every consequence statement derived from a complete decision register whose selector substitutions are calculator strategies | **ENGINEERING_CORRECTION** | architect |

Each blocking class is the recurring rejection class: **a lower-trust input yielding a current, higher-trust fact**.

| Class | Lower-trust input | Higher-trust fact obtained |
|---|---|---|
| BC5-1 | one channel page (rank 2), no key | the root of trust, the evaluator and the first TCB on a machine |
| BC5-2 | the build image record (no assigned authority) | the bytes of every accepted production binary |
| BC5-3 | the release pipeline plus threshold-1 `release-candidate` and `release-final` keys | the effective constitutional content of a registered release |

## CD5-0 — Retain (confirmed by reproduction)

- **Everything review r4 CD4-0 retained** that this review did not contradict.
- **BC4-1 closures as stated.**
  - `release-artifact` and `build-attestation` withdrawn.
  - Release registration selects source identity and input manifest.
  - Quorum of at least two first-person reproductions, confirmed first-hand; conflict refuses.
  - Fact Threshold Check.
  - One key of any purpose, with or without pipeline input, never mints a binary.
  - Evidence: CS5 (408 configurations, 21/21 self-checks, 0 invariant failures) and P4r5 VA5 rows reproduced
    byte-identical.
- **BC4-2 closures as stated.**
  - `gov-admit` never executes the candidate; installation from the measured buffer.
  - GB-1 … GB-3 bind genuine binaries.
  - No ceremony before admission; Phase 4 without self-verification.
  - Revoked, remediated and moved-tag binaries refused.
  - Evidence: FA5 (45/45 scenarios, 17/17 vectors, 26/27 mutants) reproduced byte-identical.
- **BC4-3 closures as stated.**
  - Exact per-release registration; single-valued, append-only.
  - Release-scoped presence; ranges excluded.
  - `release-final` mixes refused; the `ASIA…` file excluded on 4.1.5.
  - Evidence: REG5 and self-test 71/71 reproduced.
- **Carried closures.**
  - CR4-B-06 … CR4-B-10 rows; the stateful clock high-water; CR4-B-07 option 1.
  - Evidence: P4r5 (65/65, 42/42) and DA03r5 (20/20, 17/17) reproduced.
- **Legacy containment.**
  - Closed trust entry sets and RoT-1 root discovery.
  - Evidence: reviewer C's `matrix5` reproduced (R2-H4 property, 0 violations over 30,165 rows).

## CD5-1 — First-contact root of trust stated and enforced at its true authority (closes BC5-1: RV5-H1)

**Class.** The mistaken equivalence is: *"the typed fingerprint is a good selector of state, therefore of everything it
commits to"*. The value from one channel also selects:
- the lineage;
- the rule on how many channels must agree (read from the Trust Policy it selects);
- through the admitter digest compared with one channel, the evaluator.

**Invariant not yet established.**
- On first admission, every selector (lineage, state, the required number of agreeing channels, the evaluator) is either:
  - an authenticated value that the values it governs cannot select; or
  - the set of consulted channels, stated exactly as the first-contact root with its computed minimum.
- The required number of independent channels is enforced by the evaluator, independently of anything those channels
  select, for every first-contact value (root id or lineage, state fingerprint, admitter digest).

**What closes the enforcement part (engineering).**
1. **Compiled first-contact quorum.** The admitter enforces the owner's OP-13 answer as a compiled minimum. It applies to
   every first-contact value, and is never read from a statement those values select.
2. **Evaluator binding.** The admitter refuses when its own digest is absent from the selected state's admitter list or is
   revoked there. This is defence in depth, not a replacement for 1.
3. **Lineage from the typed value.** Never from bundle order (RV5-L1).
4. **Exact residual.**
   - AD-1 restated as "the channels the operator consults".
   - First-admission minimal sets computed with lineage substitution and evaluator substitution as calculator strategies.
   - `30` §10, `25` §7, `05` §3 and `21` OP-9, OP-12, OP-13 restated from that output.
5. **Register rows** for first-admission lineage selection, channel quorum and evaluator selection (RV5-M5).

**What no mechanism removes: an owner trade-off.** A machine with no prior trust accepts whatever its designated
first-contact sources jointly present. The owner decides which sources those are. The architecture must present these
options with computed consequences and must not choose.

| Option | Trust added | Who selects the first TCB (residual) | Operational consequence |
|---|---|---|---|
| **T1-a** one owner channel | TA-5 | compromise of that channel, zero keys | highest availability |
| **T1-b** two owner channels under distinct custody; compiled quorum over every first-contact value | TA-5 for both channels; the operator reads both | compromise of both channels. One compromised channel gives `CHANNEL_DISAGREEMENT` when the operator reads both. An operator who types one page's value twice remains TA-5/A10. | first install unavailable while either channel is unreachable; custody of two channels |
| **T1-c** a second authentication path independent of the owner's channels (for example an admitter with compiled lineage, delivered and authenticated by a platform or distribution signing service, or pre-provisioned OS images) | the third party's signing infrastructure joins the first-contact TCB | if path and channels must agree: compromise of both; if either suffices: compromise of either | dependence on the third party's availability and policy; per-platform packaging |
| **T1-d** physical provisioning (offline media or a hardware token carrying lineage and admitter digest) for designated machines | custody of the media | compromise of that custody | a ceremony per machine or batch; for CI only through images built with the media |

**Evidence required.**
- RV5-B-A01 (A01a/b/c, A02, ORD) and RV5-D-A02 on the corrected admitter: refused, or accepted only inside the restated
  residual.
- RV5-B-A04 part L extended with evaluator substitution: the calculator's first-admission minima equal the executed
  results for each option.

## CD5-2 — Every byte-determining build input established first-hand (closes BC5-2: RV5-H2)

**Class.** The mistaken equivalence is: *"every input named by digest ⇒ every input legitimately selected"*. A reproduction
quorum shows that independent parties obtained the same bytes. It cannot distinguish a common-mode input that all of them
are required to use (R-REP-2).

**Invariant not yet established.**
- Every input that determines a binary's bytes (toolchain, image or base environment, linker, C runtime objects, system
  libraries) has a registered selector whose content is established first-hand, or is a stated residual with computed
  minima.
- The pipeline selects none of them.
- A reproduction counts toward the faithful-build fact only across environments that do not share an unestablished input.

**What closes the selector part (engineering).**
1. **The environment as a first-hand-established input.** Every component is digest-pinned to upstream signed artefacts
   that the ceremony and the verifiers check, as for toolchain archives. The image is reproduced bit for bit from those
   components by parties independent of the pipeline. Or an owner option below applies.
2. **Authority named.** The decision register names the producer and authority of the image record; the pipeline never
   produces or selects it.
3. **Calculator.** Environment atoms (pipeline-produced record, upstream environment supplier, diverse environment
   compromised) and an environment goal; OP-10 and TB-S2 restated from its output.
4. **Test.** An acceptance test substitutes one environment component and asserts refusal before registration, or a
   conflict.

**What no mechanism removes: an owner trade-off** (common-mode build environment; extends OP-10).

| Option | Residual | Cost |
|---|---|---|
| **E-a** accept the registered upstream environment components as a trust assumption (TA-12 extended) | a compromised upstream component that passes the checksum checks yields identical malicious bytes from every reproducer | pinning and checks only |
| **E-b** environment diversity: the quorum includes matching reproductions from at least two independently sourced environments (`30` IR-REP-3 already requires cross-distribution reproducibility before registration) | compromise of every environment supplier used | self-contained or static linking, per-target engineering, longer builds; some targets may not reproduce across environments |
| **E-c** an owner-built environment from source, itself registered and reproduced | compromise of the owner's environment build or its upstream sources | highest engineering and maintenance cost |

**Evidence required.**
- RV5-B-A08 against the corrected ceremony and reproducer rules: a substituted component is refused or conflicts.
- RV5-B-A04 part I on the corrected calculator: every minimal set contains the registration threshold and OP-8
  verification, or the residual atom of the owner's option.

## CD5-3 — Registered constitutional content established first-hand (closes BC5-3: RV5-H3)

**Class.** The mistaken equivalence is: *"the registration authority signed the unit map ⇒ the registration authority
established it"*.
- CI derives the unit map from a final that the release keys signed (`23` §12.5).
- Verification records are bound to source and inputs, not to the registered candidate or its kernel (R-REG-3 (d), R-VER-2,
  AP-5 as written).
- E7 applies no verification restrictor.

**Invariant not yet established.**
- The effective constitutional content of a release (unit map, kernel tree digest, migrations) is established first-hand
  at the registration's authority: derived from the verified source, or reproduced by an independent quorum.
- It is bound to verification records for exactly the registered candidate, whose kernel equals the registered kernel.
- E7 applies the same restrictors as AP-5.
- No threshold-1 release key plus pipeline input selects content.

**What closes the class (engineering).** The architect chooses a mechanism and shows D-A01 refused. Part A of D-A01
demonstrates two that refuse.
1. **First-hand content.** Each registration custodian derives the unit map, kernel tree digest and migration digests from
   the source it fetched, with the registered input manifest, and refuses to sign on any difference from the proposed
   final. Alternatively, an independent reproduction quorum of the kernel payload establishes them.
2. **Verification bound to what is registered.**
   - R-REG-3 (d), R-VER-2 and AP-5 count only ACCEPTED attestations for exactly the registered candidate.
   - The attestation names the kernel tree digest the verifier reproduced.
   - The registered final's `promoted_from` equals the registered candidate.
   - AP-5 is clarified accordingly (RV5-M9).
3. **E7.** The same restrictors as AP-5 at ingress and at use: verification records for the registered candidate, no
   REJECTED attestation, final/candidate/registration consistency.
4. **Reductions and calculator.** Registration reductions are computed at the verifier (RV5-M2). A policy-root goal is
   added to the calculator, with `rc`, `rf`, `pipeline`, custodians and registration keys as atoms, per victim class.
5. **Statements restated from the corrected rules.** `05` §1 (`release-final`, `release-registration`); `21` OP-2, OP-4,
   OP-8; `23` CS-2; D-0008 rules (6), (17), (24). Under OP-2 (b), the delegated quorum, restricted by OP-8 verification,
   remains the selector of content: a stated consequence of OP-2, not a new trade-off.

**Not an owner trade-off.** D-A01 part A shows that a candidate-bound restrictor with consistency refuses, and part B shows
that a first-hand registration refuses. Neither leaves a residual beyond the registration authority and OP-8 verification.

**Evidence required.**
- D-A01 parts A and B against the corrected rules: the attacker's kernel is refused, including the OP-4 "no" row; the
  genuine release stays eligible.
- D-A05 N3 refused.
- RV5-B-A06 on the corrected E7: every OP-2 (b) minimal set contains OP-8 verification compromises.
- RV5-B-A09 variant regex and tool command reported and gated on recorded machines (RV5-M2).

## CD5-4 — Complete decision register and derived consequence statements (closes BC5-4)

**Class.**
- FD-1's closure argument rests on the decision register (R-SEL-1…4) and the derivation calculator (FD-3).
- The register lists only the rows revision 5 changed, and the calculator's model omits selectors: lineage, evaluator,
  build environment, content derivation and restrictor revocation.
- Every false consequence statement found by this review lies in an omitted row, and no RT can detect those defects
  (D-A07).

**Invariant not yet established.**
- Every consequence statement of D-0008, `05`, `21`, `25`, `30` and `31` is derived from a complete decision register whose
  every selector substitution is a calculator strategy.
- Every register row has an acceptance test that fails when its restrictor is removed.

**What closes the class.**
1. **Full register in the pack** (RV5-M5):
   - first-admission lineage, quorum and evaluator;
   - the image record;
   - registered-content derivation;
   - verification binding;
   - restrictor revocation (RV5-M1);
   - release selection among eligible releases under OP-11 (a).
2. **Calculator.**
   - It enumerates those strategies over victim classes P1, P2, FA1, FA2, witness-reliant runners and CI-record runners
     (RV5-L5).
   - RT-127 and RT-131 compare option text and minimal sets with its output.
3. **Options restated.** Nothing is decided; proposals are either absent everywhere or labelled consistently (`24` §9,
   RV5-L4).

   | Option or statement | Required restatement |
   |---|---|
   | OP-1 | minimum root threshold (RV5-L6) |
   | OP-2, OP-4, OP-8 | from CD5-3 |
   | OP-3 mode B | the per-update currency proof it needs (RV5-L9) |
   | OP-7, OP-12, OP-14 | the installation-location consequence (RV5-M8) |
   | OP-9, OP-12, OP-13 | from CD5-1 |
   | OP-10 | from CD5-2 |
   | OP-14 (b), OP-15 (a) | re-admission (RV5-M3) |
   | new trade-offs | CD5-1 options T1-a … T1-d; CD5-2 options E-a … E-c |

4. **Plan detection.** RV5-D-A07 re-run against the next plan finds a failing RT for each defect of this review.

## 5. Rule text affected (D-0008 and ARCH-0002; to stay PROPOSED)

| Rule | Class | Change required |
|---|---|---|
| (6) | CD5-3 | non-join units are fixed per release by a first-hand-established registration; registration reductions are computed at the verifier |
| (9) | CD5-2, CD5-3 | the faithful-build fact includes the build environment; counted verification records are bound to the registered candidate |
| (16), (19), (23) | CD5-1 | first-admission selectors (lineage, quorum, evaluator) are not selectable by the values they govern; the first-contact residual is stated |
| (17) | CD5-3 | "release-final selects none of them" is made true for constitutional content |
| (22) | CD5-4 | the decision register in the architecture is complete |
| (24) | CD5-3 | a registration's content is established first-hand |
| (10), (12) | RV5-L8, RV5-L7 (carried) | scope consistent with `18` §9.1–§9.2 and with executed LP-1s |

## 6. Non-blocking items the next revision must carry or close

These do not change the verdict. Each is a bound, testable requirement. "CR5-B-nn" refers to reviewer B's
`04-CARRIED-REQUIREMENTS.md`; "RV5-C-xx" to reviewer C's `04-CARRIED-REQUIREMENTS.md`.

| Item | Requirement | Acceptance test |
|---|---|---|
| RV5-M1 | CR5-B-01: a revocation of a reproduction or verification attestation clears neither `REPRODUCTION_CONFLICT` nor `ARTIFACT_SOURCE_REJECTED` unless issued under the registration authority or root; the calculator models it | CR5-B-01 (i)–(iii) |
| RV5-M2 | CR5-B-04: the verifier computes registration reductions over every referenced registration (`INCOMPLETE` if one is not held) and refuses undeclared ones; changes of security-classified non-orderable units are listed in the per-project gate; rule (6) states what "down" means for them | CR5-B-04 (i)–(iii) |
| RV5-M3 | CR5-B-03 and RV5-C-L3: first admission defined (no store, or no admission record ever written); re-admission keeps the store and checks its prior record; each admitted binary keeps its own record, so rollback keeps it | CR5-B-03 (i)–(iii); RT-139 extended: a re-run preserves high-waters and anchors; admitting N+1 keeps N's record |
| RV5-M4 | an unambiguous source-identity encoding (length-prefixed or NUL-separated, control characters refused) or the Git tree object id under SHA-256; SRC5 replaced by a test of the specified function | RV5-B-A05 two-tree construction gives different identities; the replacement test is identical across two runs and two clones |
| RV5-M5 | CR5-B-05 (also a CD5-4 closure criterion) | RT-128 asserts every row; a mutation removing each row's restrictor fails a scenario |
| RV5-M6 | RV5-C-M1: the install transaction writes a `.gitattributes` marking `governance/trust/**` and the occupation sentinels `-text` | RT-50/RT-122 clones with `core.autocrlf=true` and with `* text=auto` + `core.eol=crlf`: `COMPLETE`, kernel byte-equal to the release content set |
| RV5-M7 | RV5-C-M2: the occupation's survival of the untracking idiom is stated to require that no active ignore source matches `.governance-runtime/` | RT-122/RT-145 under a user `core.excludesFile` and under `.git/info/exclude`: the idiom lists nothing, or D033 names the resulting `PARTIAL(occupation)` |
| RV5-M8 | Either (a) `31` GB-4, `24` §4.2, `21` OP-7, OP-12, OP-14 and RT-138 state that a user-writable installation is C0 only under OP-7 (a), (b), and (c) without witnesses, and name the burden (an administrator-protected install or system pin for governed use); or (b) anchoring ceremonies for C1–C2 are permitted on user-writable installations, with C3 still refused and RS-3 restated | RV5-D-A03 on the implementation: the classes reached equal the restated table for each OP-7 answer; the Phase 4 path of a legacy consumer on a user-writable workstation gives the stated outcome |
| RV5-M9 | The shared conformance vectors of `gov` and `gov-admit` include: registered final revoked; registered candidate revoked; ACCEPTED attestation for another candidate with the same source; binary version below `min_binary_version`. AP-5 binds counted attestations to the registered candidate. | RV5-D-A04 re-run against the next reference executor and oracle: both refuse R1–R4 with the same codes; the vectors contain the four rows |
| RV5-L1 | CR5-B-06 | CR5-B-06 |
| RV5-L2 | CR5-B-07 | CR5-B-07 |
| RV5-L3 | CR5-B-08 | CR5-B-08 (RT-148 extended) |
| RV5-L4 | CR5-B-09; `07` §3 and `04` V8 aligned with `30` §4.1 (`content_digest`, `inputs_manifest_digest`, no statements under a withdrawn purpose) | text review; RT-127 |
| RV5-L5 | CR5-B-10 | CR5-B-10 |
| RV5-L6 | CR5-B-11 | RT-132 with root threshold 1 → `ROOT_VERSION_INVALID` in `gov`, `gov-admit` and `draft-policy` |
| RV5-L7 | RV5-C-L1; D-0008 rule (12) restated to what holds | RV5-C-L1 test |
| RV5-L8 | RV5-C-L2; D-0008 rule (10) consistent with `18` §9.2 | RV5-C-L2 test |
| RV5-L9 | `21` OP-3 states that mode B still needs, per update, a currency proof naming the publishing Trust State (a fresh confirmation or pin, or OP-7 (c) witnesses) | RT-127 text; an oracle row: a mode-B machine anchored at t10 refuses an update published in t11 without a new proof |
| RV5-I2 | For the capability-contract phase: derived members of an owner binding group are recomputed by `gov` or confirmed with the derivation shown | a group whose compiled YAML does not compile from its Markdown is refused |
| CR5-B-02, CR5-B-12 | as reviewer B `04` | as reviewer B `04` |
| CR4-B-01, CR4-B-02, CR4-B-04, CR4-B-05; C-2 … C-6 | still specification only; carried with their review r4 tests | as review r4 |

## 7. Re-review entry criteria

1. **Classes closed.** CD5-1 … CD5-4 are closed as classes in the pack, schemas, D-0008 and ARCH-0002, which stay PROPOSED
   and not active.
2. **Evidence re-run against the revision-6 rules.**
   - (a) RV5-B-A01 (A01a/b/c, A02, ORD) and RV5-D-A02 against the corrected admitter; RV5-B-A04 part L with lineage and
     evaluator substitution.
   - (b) RV5-B-A08 and RV5-B-A04 part I with environment atoms.
   - (c) RV5-D-A01 parts A and B, RV5-D-A05 N3, RV5-B-A06 and RV5-B-A09 against the corrected registration and E7.
   - (d) RV5-D-A04 against the next reference executor and oracle; RV5-D-A07 against the next plan.
   - (e) Unchanged in what they refuse:
     - CS5 self-checks;
     - P4r5 (65/65 and 42/42 or their successors);
     - DA03r5 (20/20, 17/17);
     - FA5 (45/45);
     - REG5;
     - CSI self-test (71/71);
     - P1r4 on real 4.1.5;
     - reviewer C's `matrix5` (property R2-H4, 0 violations).
3. **Response matrix.** It covers RV5-H1 … RV5-I2, CR5-B-01 … CR5-B-12, reviewer C's items and CD5-0 … CD5-4, with no
   "resolved" claim resting on untested evidence.
4. **Owner options.** The trade-offs of CD5-1 (T1-a … T1-d) and CD5-2 (E-a … E-c) are presented with computed
   consequences, and no choice is made.
