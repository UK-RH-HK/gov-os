# 10 — Consolidated findings (review r5 synthesis D), CRITICAL to LOW

- **Revision reviewed:** RoT-1 revision 5, `cdb4e14009bba60bea9b805563c1b60e84f30b4b`.
- **Panel:** reviewer B `248f12a`, reviewer C `840d583`.
- **Synthesis run:** AR-0014.
- D-0008 and ARCH-0002 remain PROPOSED; nothing here approves them.

| Severity | Count | IDs |
|---|---|---|
| CRITICAL | 0 | — |
| HIGH | 3 | RV5-H1, RV5-H2, RV5-H3 |
| MEDIUM | 9 | RV5-M1 … RV5-M9 |
| LOW | 9 | RV5-L1 … RV5-L9 |
| INFO | 2 | RV5-I1, RV5-I2 |

## Evidence classes

| Class | Meaning |
|---|---|
| **executed** | the real legacy 4.1.5 binary as consumer, real Git, the real Rust toolchain, the pack checker (unmodified), or the reference executor `gov_admit_reference.py` (unmodified; real Ed25519 through OpenSSL) |
| **computed** | the architect's P4r5, P4r4 or CS5 functions loaded unmodified; reviewer B's calculator extensions (reproduced byte-identical) |
| **design** | pack text at `cdb4e14` |
| **code** | a reference instrument's source |

Every panel probe cited was re-run by this review (`D-synthesis/01-REPRODUCTION.md`). "B-Axx", "C-Axx" and "D-Axx" mean
RV5-B-Axx, RV5-C-Axx and RV5-D-Axx.

**No CRITICAL.**
- **Running machines with a compiled lineage.** Registration, reproduction quorum, publication, negatives and
  currency-naming hold under every key-theft and pipeline shape of review r4. CS5, P4r5 and FA5 were reproduced
  byte-identical.
- **Each HIGH needs one of:**
  - a first-contact channel;
  - an infrastructure input the pack names but does not govern;
  - two threshold-1 release keys (one under OP-4 "no") plus pipeline input.

  None fails the chain for every machine without such a condition.

---

## RV5-H1 — HIGH — The first TCB on a machine is selected by the independent channels alone

**Summary.**
- The typed fingerprint selects the lineage, the Trust Policy and therefore the channel quorum.
- The admitter digest is compared with one channel.
- A channel attacker with no key admits a malicious TCB under OP-13 (a) and (b).
- The declared first-admission minima, AD-1 and the OP-9, OP-12 and OP-13 consequences are false.

**Origin:** RV5-B-H1, extended by D-A02. **Adjudication:** CONFIRMED HIGH.

### Statement

1. **Lineage and state.**
   - `31` R-ADM-3: the typed fingerprint is "the only selector of root chain, Trust Policy, Trust State".
   - `25` AP-2: "Lineage: bootstrap from the typed fingerprint's epoch".
   - A channel page that shows the fingerprint of a lineage the attacker generated selects that lineage's root, Trust
     Policy, Trust State, registration, attestations, reproductions and publication, all valid within it.
2. **Quorum.**
   - `25` AP-3 compares the number of typed values with `bootstrap.channel_quorum` of the Trust Policy that the typed
     fingerprint selects. The admitter has no compiled minimum.
   - Under OP-13 (b), an operator who types the one value a compromised channel shows is admitted.
3. **Evaluator (D-A02).**
   - `31` R-ADM-2 compares the admitter digest with "the channels" and sets no quorum. `21` OP-13 scopes agreement to
     "typed state fingerprints".
   - FA5 `operator_compare_admitter(measured, tps_admitter_list, channel_digest)` takes one channel digest.
   - The reference executor never reads `bootstrap.admitter_digests` and has no negative check on itself.
   - Under any OP-13 answer, one channel substitutes the evaluator. A substituted evaluator admits anything.
4. **Pack statements contradicted.**
   - `30` §10 FA1/FA2 key-theft rows;
   - `25` §7 row "q reproducer keys + trust-state key + the channel(s) the victim types";
   - `05` §3 minimum-sets table;
   - `21` OP-9, OP-12, OP-13, and the combinations "OP-9 (a) + OP-13 (a)" and "OP-9 (c) or (d) + OP-13 (b)";
   - `31` §9 AD-1;
   - CS5 H-CH ("`ch_k` shows t_x's", a descendant inside the genuine lineage);
   - FD-1 §2 (5): a shortfall must be a residual with an exact bound.

### Evidence

- **executed** `RV5-B-A01` (reproduced byte-identical):

  | Case | Result |
  |---|---|
  | A01a, OP-13 (a) | `ACCEPTED` |
  | A01b, OP-13 (b), both channels | `ACCEPTED` |
  | A01c, genuine OP-13 (b), one value typed | `ACCEPTED` |
  | controls: genuine lineage | `ACCEPTED` |
  | controls: one genuine fingerprint under quorum 2 | `CHANNEL_QUORUM_NOT_MET` |
  | controls: FA5 CH2 shape | refused |
  | controls: disagreeing values | `CHANNEL_DISAGREEMENT` |
  | A02: a negative-skipping evaluator on a revoked binary | `ACCEPTED` |

- **computed** `RV5-B-A04` part L (reproduced byte-identical):

  | Victim | Minimum | Configurations |
  |---|---|---|
  | FA1 | {ch1} | 96/96 |
  | FA2 | {ch1, ch2} | 96/96 |
  | FA2, quorum read from the selected state | {ch1} | 96/96 |

- **computed** D-A07: `29` §4 has no row naming lineage selection or channel quorum. FA5 CH2 types the genuine
  fingerprint, so no conformance vector or RT types an attacker lineage's fingerprint.
- **design and code:**
  - `31` R-ADM-1…3, R-CER-2, §9;
  - `25` AP-2, AP-3, §7;
  - `06` §1–§3;
  - `21` OP-9, OP-12, OP-13;
  - `01` TA-5, A20;
  - `29` §3, §4;
  - `gov_admit_reference.accept()`;
  - `FA5-first-admission.py` `operator_compare_admitter`.

### Failure scenario

1. The owner chooses OP-13 (b) and OP-9 (c), because `21` says first admission then needs both channels and all three
   reproducer keys.
2. One channel, an owner-run download page, is compromised.
3. The attacker leaves the fingerprints genuine and replaces the admitter digest and download.
4. A new engineer follows `06` §3: compares the admitter digest with that page, then types the fingerprints from both
   channels.
5. The substituted admitter installs the attacker's binary and writes an admission record. Every later trust decision on
   that machine is the attacker's.

### Unavoidable core versus this finding

| Situation | Determination |
|---|---|
| A machine with no prior trust must accept some out-of-band source for its first root | core; acceptable when stated exactly, with its computed minimum |
| The declared minima name reproducer, trust-state or registration keys the channel attacker does not need | **not core**: computing with lineage and evaluator substitution gives the exact statement |
| The channel quorum is read from the Trust Policy that the channel's value selects | **not core**: a compiled minimum of the admitter removes it |
| The admitter digest is compared with one channel under OP-13 (b) | **not core**: the same compiled quorum over every first-contact value (root id, state fingerprint, admitter digest) removes it |
| How many, and which, independent sources form the first-contact root | **owner trade-off** (`11` CD5-1): no mechanism removes it; options differ in trusted parties and availability |

### Why HIGH

- TCB compromise on the first-install machine class below the declared threshold, with zero keys. This includes the owner
  answer (OP-13 (b)) that the pack presents as closing it.
- The consequence statements of security-material options are false: the BC4-4 class, blocking in review r4.

### Class and novelty

**Narrowed remainder of BC4-2** (R2-H2/BC-2 ∩ R2-H3/BC-3) at its intersection with BC4-4. The instance (lineage, quorum and
evaluator selection at first admission) is new. **Unestablished invariant:**
- On first admission, every selector (lineage, state, the rule on how many channels must agree, and the evaluator) is
  either an authenticated value that the values it governs cannot select, or is the set of consulted channels, stated
  exactly as the first-contact root with its computed minimum.
- The required number of independent channels is enforced by the evaluator, independently of anything those channels
  select, for every first-contact value.

---

## RV5-H2 — HIGH — The build environment selects the bytes of every production binary

**Summary.**
- The image record that legitimises `build_image_digest` has no assigned producer, authority or content check.
- Every honest reproducer, including an OP-10 (b) diverse one, obtains the same malicious bytes.
- No option or residual covers it.

**Origin:** RV5-B-H2. **Adjudication:** CONFIRMED HIGH.

### Statement

1. **The input.** `30` §4.2 and `schemas/input-manifest.schema.json` require `build_image_digest`.
2. **Its only check.** R-REG-3 (c): "the build image digest against the owner's image record".
   - No section names who produces that record, from what, or under which authority.
   - `29` §4 has no row for it.
3. **Nobody establishes its content.**
   - Verifiers check "the manifest against upstream signed checksums" (R-VER-1). An image has no such checksum.
   - CS5 H-VER and H-REG check toolchain archives only.
4. **Reproducers cannot detect it.** R-REP-2 has every reproducer fetch the one registered image by digest.
   - OP-9 (a)–(d) change nothing.
   - OP-10 (b)'s diverse reproducer must match bit for bit, so it uses the same image.
   - OP-10 (c) replaces the toolchain archive, not the image.
5. **Minima.**
   - {pipeline} when release CI produces the record: a reading the text permits.
   - {image supplier} when the owner builds the image from upstream images, with no residual stated.
6. **Pack statements contradicted.**
   - CS5 G_INPUTS "The pipeline alone never succeeds", and INV-INPUTS;
   - `30` §10 and `05` §3 "accepted malicious named build inputs: registration custodians at threshold + OP-8 verification
     keys";
   - `25` §8 "Its source and build inputs: the registration ..., first-hand verification records, upstream checksum checks";
   - `21` OP-10;
   - TB-S2/TA-12, which cover only the toolchain archive.
7. **Diversity is achievable but not required.** `30` IR-REP-3 already requires "cross-OS and cross-distribution
   reproducibility for each registered target ... before that target is registered". Per release, the quorum is not
   required to span independently sourced environments.

### Evidence

- **executed** `RV5-B-A08` (reproduced; every verdict identical, digests compiler-dependent):

  | Case | Result |
  |---|---|
  | two reproducers, clean image | bit-identical |
  | two reproducers, malicious image | bit-identical to each other; different from clean |
  | malicious-image binary run | injected code runs |
  | toolchain | unchanged |
  | build or image path embedded | none |

- **computed** `RV5-B-A04` part I (reproduced byte-identical): G_IMAGE is {pipeline} or {image_up} for P1, P2 and FA1
  under every OP-2, OP-8, OP-9 and OP-10 answer.
- **computed** D-A07: the calculator's goals and atoms contain no image atom, and no RT substitutes the image.
- **design** `30` §2, §4.2, R-REG-3 (c), R-VER-1, R-REP-2, IR-REP-3, §10, §12; `05` §3; `25` §8; `21` OP-10; `29` §4.

### Failure scenario

1. Release CI builds the Rust build image (base OS, linker, C runtime objects) and records its digest. The ceremony
   compares the manifest against that record.
2. An attacker in the CI job replaces a C runtime object.
3. R-REG-3 (a)–(c) pass, and the verifiers accept clean source.
4. Every reproducer fetches the image by digest and obtains the same malicious binary. The quorum is met; the publisher
   publishes.
5. Every machine accepts the binary, pinned CI runners included.

### Why HIGH and not CRITICAL

- **Why HIGH.** TCB compromise from one infrastructure input below the declared minimum, with no option and no stated
  residual.
- **Why not CRITICAL.**
  - The pack names an "owner's image record", so a conforming process can keep its production outside the pipeline.
  - The defect is that no rule requires this and no residual states the supplier that remains.

### Class and novelty

**Narrowed remainder of BC4-1** (R2-H3/BC-3). The faithful-build fact is established first-hand for source, lockfile and
toolchain archive, but not for the build environment. The instance is new: CS5's G_TOOLCHAIN models the toolchain archive
only. **Unestablished invariant:**
- Every input that determines the bytes of a binary (toolchain, image or base environment, linker, system objects) has a
  registered selector whose content is established first-hand, or is a stated residual with computed minima.
- No such input is selected by the pipeline.
- A reproduction quorum counts toward the faithful-build fact only across environments that do not share an unestablished
  input.

---

## RV5-H3 — HIGH — Registered constitutional content is not established first-hand

**Summary.**
- The registration ceremony signs a unit map and kernel tree digest that CI derives from the final handed to it.
- Verification records are bound to source and inputs, not to the registered candidate.
- E7 applies no verification restrictor.
- {pipeline, `release-candidate`, `release-final`} (OP-4 "no": {pipeline, one everyday key}) makes malicious non-orderable
  constitutional content effective on every machine. Under OP-2 (b), {two delegated custodians, `release-final`} does too.

**Origin:** D-A01 (new) and RV5-B-H3, extended by D-A05. **Adjudication:** CONFIRMED HIGH. B's route alone would be MEDIUM
(`D-synthesis/02-ADJUDICATION.md` §1.1).

### Statement

1. **Who selects the content.** `29` §4: policy-root eligibility is selected by "the registration of R ... (exact per-release
   unit map and kernel tree digest)". R-REG-6: the `constitution` block fixes every non-join unit.
2. **Who establishes it.**
   - `23` §12.5: "`gov release build`, canonical CI: `csi_check.py derive-registration` produces the unit map". The
     ceremony "lists every unit that differs from the previous registration".
   - R-REG-3 (e) recomputes only the source `content_digest`. No rule derives the unit map, kernel tree digest or
     migrations from the fetched source.
3. **What the verification records bind.**
   - R-REG-3 (d): "each ACCEPTED for exactly this `source` and `inputs_manifest_digest`".
   - R-VER-2 and AP-5 count ACCEPTED attestations "with the registered source and inputs". The reference executor does
     exactly that. P4r5's `accept_binary` alone binds them to the registered candidate.
4. **What E7 checks.** `19` §6 and `23` §12.3: the registration is referenced by the effective TSS, names R's final, and
   units and kernel tree digest are equal. There is no verification condition and no candidate condition. V8 requires only
   that final and candidate have equal kernel and source.
5. **The attack (D-A01).**
   - The honest verifiers accept candidate C (kernel K_fix, source S).
   - With the pipeline and the `release-candidate` and `release-final` keys, the attacker signs C′ and F′ with kernel
     K_weak and source S, and hands them to the ceremony.
   - Honest custodians: R-REG-3 (a)–(e) pass. The diff list is identical to the genuine release's. No reduction is
     reported (a non-identical weakening; RV5-M2).
   - The honest publisher references the first-hand registration.
   - E7, V8 and the checker all pass. Under OP-4 "no" the Fact Threshold Check accepts the root, and one everyday key
     suffices.
6. **Breadth.**
   - Every non-join unit: secret patterns, tool descriptors including the commands `gov` executes, hard invariants,
     schemas, skills, migrations.
   - New constitutional files shipped in the kernel, including the forward-compatibility Capability Acceptance Contract
     (D-A05 N3: attacker YAML exit 0, no reduction).
7. **OP-2 (b) route (RV5-B-H3).** Two delegated custodians plus `release-final`, or two delegated keys plus the trust-state
   and `release-final` keys for C1–C2, register content with no OP-8 verification compromise.
8. **Pack statements contradicted.**
   - `05` §1 `release-final` "nothing becomes effective ... `release-final` appears in no minimal set";
   - `05` §1 `release-registration` "accepted only with OP-8 verification statements";
   - `21` OP-2 (b), OP-4 ("neither `release-candidate` nor `release-final` selects ... a policy root"), OP-8;
   - `23` CS-2 ("one registration ceremony per release fixes source, inputs, content and final together");
   - `00` §1 BC4-3 row;
   - D-0008 rule (17) ("release-final selects none of them").

### Evidence

- **computed** D-A01 part A (P4r5 functions, unmodified):

  | Check | Result |
  |---|---|
  | ceremony as written | signs |
  | V8 | holds |
  | E7 as written | eligible |
  | E7 + source-bound restrictor (reviewer B's correction as worded) | eligible |
  | E7 + candidate-bound restrictor and consistency | refused |
  | OP-4 "no" | root valid under the Fact Threshold Check; eligible |
  | control: registration derived first-hand | `surface_unregistered_for_release` |

- **executed** D-A01 part B (pack checker; real 4.1.5):

  | Check | Result |
  |---|---|
  | ceremony diff lists, genuine and attacker | identical (one unit) |
  | `registration-reductions` | exit 0 |
  | attacker kernel, CI-derived registration | exit 0 |
  | attacker kernel, first-hand registration | exit 3 |
  | genuine kernel, first-hand registration | exit 0 |
  | 4.1.5, attacker kernel | `ASIA…` key file indexed and returned by `memory query` |
  | 4.1.5, genuine kernel | excluded |

- **executed** D-A05: new kernel-shipped contract files. N1 unclassified exit 2; N2 exit 0; N3 attacker YAML exit 0 under
  the CI-derived registration; N4 exit 3 under a first-hand registration; N5 no reduction.
- **computed** `RV5-B-A04` part P and `RV5-B-A09` (reproduced byte-identical): the OP-2 (b) route; the variant regex E7
  exit 0; the `ASIA…` file served on 4.1.5.
- **computed** D-A07: the calculator has no constitutional-content goal; no RT varies the kernel under an identical source.
- **design** `30` R-REG-3, R-REG-6, R-VER-2; `23` §12.3, §12.5; `19` §6; `04` V8; `25` AP-5; `29` §4; `05` §1; `21` OP-2,
  OP-4, OP-8.

### Failure scenario

1. 4.1.8 extends the `aws-access-key` regex to `(AKIA|ASIA|ABIA)`, and the verifiers accept that candidate.
2. The attacker controls the release job and has stolen the owner's everyday release key (OP-4 "no").
3. It signs a candidate and final whose regex is `(?:AKIA|ABIA)` and delivers them to the registration ceremony.
4. The custodians see one changed unit, the regex this release is known to change, and no reduction. They sign.
5. The publisher publishes the registration. A2 commits the kernel, or machines update with a currency proof.
6. Temporary AWS keys are indexed and served to agents on every machine.
7. If the release ships binaries, AP-8 stalls their publication. That is a signal no rule acts on, and the registration is
   already append-only and effective.

### Why HIGH

- Authentic, eligible content confers weaker secret handling, tool execution or agent instruction while every check
  passes. The selectors are two threshold-1 release keys (one key under OP-4 "no") plus pipeline input.
- This is the RV4-H3 shape. HO-0001 §3.1 lists sensitivity and indexing exclusions and the tool permission floor among
  the required cases.
- **Not CRITICAL:** the TCB, the trust state and orderable floors are unaffected (floors stay joined with the root-signed
  Trust Policy).

### Class and novelty

**Narrowed remainder of BC4-3** (R2-H1/BC-1) at its intersection with BC4-1's first-hand principle. Revision 5 moved the
selector of content from `release-final` to the registration (RV4-H3 as stated is closed: REG5 reproduced), but the
registration passes through a unit map it did not establish. **Unestablished invariant:**
- The effective constitutional content of a release (unit map, kernel tree digest, migrations) is established first-hand
  at the registration's authority: derived from the verified source, or reproduced by an independent quorum.
- It is bound to verification records for exactly the registered candidate, whose kernel equals the registered kernel.
- E7 applies the same restrictors as AP-5.
- No threshold-1 release key plus pipeline input selects content.

---

## MEDIUM

Every MEDIUM is carried with a bound acceptance test (`11-CORRECTION-DELTA.md` §6). None needs an architecture change, for
the reason given.

| ID | Statement | Evidence | Origin → adjudication | Why carriable |
|---|---|---|---|---|
| **RV5-M1** | Revocation removes restrictors. A trust-state (or `revocation`) key lists honest conflicting reproductions, or a REJECTED attestation, in `revocations`, and AP-4 then ignores them. `05` §1 calls `revocation` "denial of service only". CS5 lets restrictors disappear only through `transport`. | executed B-A03 (`ACCEPTED` without transport); computed B-A04 part R (36/216 configurations lose `transport`). Reproduced. | RV5-B-M1 → CONFIRMED MEDIUM | the key sets still need q reproducer keys, the trust-state key and the channel; a bound rule plus recomputation |
| **RV5-M2** | Registration reductions are exact-match and ceremony-side only. E7 accepts an undeclared exact reversion; a withheld intermediate registration hides it; a non-identical weakening (variant regex, tool command) is reported by nothing. `23` §12.4's per-project gate is not enforced at the verifier. | executed B-A09, A10 (reproduced) | RV5-B-M2 → CONFIRMED MEDIUM | the actor is the registration authority; a verifier rule and a restated rule (6) close it |
| **RV5-M3** | Re-admission discards the monotonic verifier trust store: anchors, clock and accepted-TBM high-waters, per-project records (E10, strength vectors). "First admission" is undefined, and the reference moves the store aside on every run. OP-14 (b) and OP-15 (a) make re-admission routine. R-ADM-7 "record beside the binary" contradicts the in-store record, so an earlier binary's record is lost. | computed B-A12 M8; code `write_admission_record`; C `admit_tx` A09, A10 (reproduced) | RV5-B-M3 + RV5-C-L3 (DUPLICATE) → CONFIRMED MEDIUM | the trigger is an operator procedure and the effect is loss of detection; a bound definition and tests close it |
| **RV5-M4** | The source identity is ambiguous for newline-bearing paths, and SRC5 tests `git archive` of a tree id (time-dependent), not the specified canonical digest. | executed B-A05 (verdicts reproduced); SRC5 re-run: 16 digest leaves differ from the committed output, verdicts equal | RV5-B-M4 → CONFIRMED MEDIUM | `release_commit` is also registered; an encoding and a test close it |
| **RV5-M5** | The decision register in `29` §4 is partial and misclassifies selectors. It has no rows for lineage selection, evaluator selection, channel quorum, the image record, registered-content derivation, restrictor revocation; Git delivery under OP-11 (a) is labelled a carrier. RT-128 asserts only the listed rows. | design; computed D-A07 | RV5-B-M5 → CONFIRMED MEDIUM | a complete register is a bound deliverable (RT-128). Its completion is also a closure criterion of CD5-4. |
| **RV5-M6** | No `.gitattributes` protects the kernel bytes: `core.autocrlf=true` (the Git for Windows default) or `* text=auto` with `core.eol=crlf` leaves every clone `PARTIAL(kernel_content_mismatch)` / `KERNEL_TAMPERED`. | executed C `gitops` AUTOCRLF, TEXTAUTO_EOLCRLF (reproduced) | RV5-C-M1 → CONFIRMED MEDIUM | fails closed; a transaction step and a clone test |
| **RV5-M7** | The `.gitignore` surgery reaches only the project file: a user `core.excludesFile` or `.git/info/exclude` carrying `.governance-runtime/` re-drops the migration occupation under the untracking idiom. | executed C `gitops` GLOBALEXCL, INFOEXCL (reproduced) | RV5-C-M2 → CONFIRMED MEDIUM | fails closed (`PARTIAL(occupation)`); a stated condition and tests |
| **RV5-M8** | **A user-writable installation can never anchor, so it is C0 only under OP-7 (a), (b), and (c) without witnesses, not "C0–C2 only".** GB-4 refuses `confirm-state`, `confirm-root` and trust-gate confirmation on such installs. Account-location pins fail the integrity predicate. R-ADM-8 removes retained anchors. On a workstation without administrator rights: no governed use under (a)/(b); upgrades only through `gov-admit` (RV5-M3); a legacy consumer cannot run Phase 4 `update --apply`. `24` §4.2 lists `confirm-state` in C0; `31` GB-4 and RT-138 state C0–C2. No option text states the burden (an administrator-protected install or pin on every developer machine). | computed D-A03 (`gov_run` and P4r4 decision rule, unmodified) | NEW (D) → MEDIUM | fails closed. Either the consequence is restated (operational burden in OP-7, OP-12, OP-14; RT-138 corrected), or anchoring ceremonies for C1–C2 are permitted on user-writable installs (A3 already can forge its own store, RS-3). Both are bound rule choices that change no trust relationship. |
| **RV5-M9** | **The two executors of admission-predicate/1 disagree, and neither oracle carries the cases.** The bootstrap reference accepts a binary whose registered final or candidate is revoked (AP-4), and one whose ACCEPTED attestation was issued for another candidate with the same source (AP-5 as P4r5 reads it). The running-mode oracle refuses all three. No instrument models `min_binary_version` at admission. FA5 has no final or candidate revocation, no candidate-binding case and no binary-floor vector; P4r5 has only `AP-A8_candidate_revoked`. RT-134/RT-135 inherit the gaps. AP-5's text ("with the registered source and inputs") is ambiguous about candidate binding. | executed D-A04 (reference executor, 44 Ed25519 verifications); computed D-A04 (P4r5); computed D-A07 | NEW (D) → MEDIUM (remainder of RV4-M7: oracle regression sensitivity) | vectors, a normative clarification of AP-5 and a binary-version field in the admission vectors close it; no trust relationship changes |

## LOW

| ID | Statement | Evidence | Origin → adjudication |
|---|---|---|---|
| RV5-L1 | The reference executor takes the lineage from the first self-verifying root v1 in bundle order, not from the typed fingerprint (`25` AP-2); an attacker root served first makes a genuine admission fail. | executed B-A01 ORD rows (reproduced) | RV5-B-L1 → CONFIRMED LOW |
| RV5-L2 | The admission record is unsigned and honoured by digest anywhere in the record directory; a package shipping a genuine revoked binary with a record passes GB-1; TB-1′ holds only for installs that did not ship a record. | code `gov_run`, `load_admission_records`; design `31` GB-1…5 | RV5-B-L2 → CONFIRMED LOW |
| RV5-L3 | On a restored or long-offline machine with an old clock high-water, a clock set back within the C3 window of an old anchor yields a P1 proof for stale state; `24` §5.3 and §5.7 hold only under TA-7. | computed B-A12 CLOCK-back rows (reproduced) | RV5-B-L3 → CONFIRMED LOW |
| RV5-L4 | Stale text contradicts revision-5 rules: the witness-only clock high-water (`24` §8, §10 RS-2; `17`; `01` TA-7, G23; `02` I-68); the deny-list confinement in `24` §3.5 (3); the labelled OP-7 proposal in `24` §9. **D extension:** `07` §3 still defines `release.source {release_commit, source_tree_digest, build_inputs_digest}` and "Artefact v3" statements under `release-artifact`; `04` V8 names `source_tree_digest`. | design | RV5-B-L4 → CONFIRMED LOW, extended |
| RV5-L5 | CS5 enumerates only P1, P2, FA1 and FA2; witness-reliant and CI-record runners are not enumerated although `25` §7 claims "under any owner answer". | computed B-A04 part C (reproduced) | RV5-B-L5 → CONFIRMED LOW |
| RV5-L6 | No normative minimum root threshold: at threshold 1 one root key signs every Trust Policy. The reference instruments compile 2. | design; code | RV5-B-L6 → CONFIRMED LOW |
| RV5-L7 | `26` §4 LP-1s and D-0008 rule (12) claim every write under `governance/**` other than overlay content leaves a state that is not `COMPLETE`; subtree `adopt baseline`/`migrate baseline` litter under `governance/spec` and `governance/views/spec` stays `COMPLETE` (inert). | executed C `matrix5` (16 counterexamples, reproduced) | RV5-C-L1 → CONFIRMED LOW, extended to rule (12) |
| RV5-L8 | `18` §9.1 and §9.2 omit the transaction area that `18` §8 places in the Protected Path Set, and D-0008 rule (10) says RoT-1 commands refuse a working directory inside it; a legacy `init` there leaves `COMPLETE` with a reported nested install (inert through the VTS registration gate). | executed C `matrix5` (96 rows, reproduced) | RV5-C-L2 → CONFIRMED LOW, extended to rule (10) |
| RV5-L9 | OP-3 mode B's consequence is incomplete under CR4-B-07 option 1: without a trust gate there is no P2 proof, and a P1 proof names only the anchored TSS, so each certified update needs a fresh confirmation or pin naming the publishing TSS, or witnesses. "Certified updates skip the gate" removes the human step only under OP-7 (c). | design `24` §4.4, `27` §3.1, `21` OP-3 (D-A06) | NEW (D) → LOW (option statement; fails closed) |

## INFO

| ID | Statement | Origin → adjudication |
|---|---|---|
| RV5-I1 | The acting role remains caller-declared (V-L5); no trust gate depends on it (`27` §5). | RV4-I1 → unchanged |
| RV5-I2 | Owner-domain binding groups (`23` §7.2) bind the digests of a set, not a derivation between its members. For the Capability Acceptance Contract, "compiled executable YAML" is a function of the normative Markdown. A group whose YAML does not compile from its Markdown is consumable once confirmed or pinned. The capability-contract phase should make derived members recomputed by `gov`, or confirmed with the derivation shown. | D-A05 (design); for the later phase, not a finding against this revision's classification |
