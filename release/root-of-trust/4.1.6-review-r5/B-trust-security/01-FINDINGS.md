# 01 — Findings (review r5 B, trust and security)

Revision reviewed: RoT-1 revision 5, `cdb4e14009bba60bea9b805563c1b60e84f30b4b` (`release/root-of-trust/4.1.6/`,
`spec/decisions/D-0008.yaml`, `spec/architecture/ARCH-0002.yaml`). Reviewer: AR-0012, role `rot-reviewer-trust-security`.
This reviewer does not issue the architecture verdict.

| Severity | Count | IDs |
|---|---|---|
| CRITICAL | 0 | — |
| HIGH | 3 | RV5-B-H1, RV5-B-H2, RV5-B-H3 |
| MEDIUM | 5 | RV5-B-M1 … RV5-B-M5 |
| LOW | 6 | RV5-B-L1 … RV5-B-L6 |
| INFO | 0 new (RV4-I1 unchanged) | — |

## Evidence classes

| Class | Meaning |
|---|---|
| **executed** | the architect's reference executor `evidence/r5/gov_admit_reference.py` (unmodified; real Ed25519 through OpenSSL), the pack checker `constitutional-surface/csi_check.py` (unmodified), the real legacy 4.1.5 binary as stand-in consumer, real Git, or the real Rust toolchain on this machine |
| **computed** | the architect's instruments loaded unmodified (`CS5-tcb-capability-sets.py` with its `accepted` wrapped and still called; `P4r5-conformance-oracle.py` and, through it, `P4r4-trust-state-model.py`), or this review's enumeration of the revision-5 rules |
| **design** | pack text at `cdb4e14` |
| **code** | a reference instrument's source, or 4.1.5 runtime (unchanged since `da9c851`) |

"A-nn" means held-out attack RV5-B-A-nn (`02-HELDOUT-ATTACKS.md`). Files are under `evidence/outputs/` and
`evidence/probes/`.

**No CRITICAL.** For running binaries with a compiled lineage the registration, reproduction quorum, publication, negative
set and currency-naming rules hold under every key-theft and pipeline shape of review r4 (CS5, P4r5 and FA5 reproduced
byte-identical). Each HIGH below needs either one infrastructure input the pack names but does not govern, or a named owner
option.

---

## RV5-B-H1 — HIGH — First admission is selected by the independent channel alone: the typed fingerprint selects the lineage and the channel's digest selects the evaluator, so a channel attacker with no key admits a malicious TCB under OP-13 (a) and (b); the declared first-admission minima are false in every configuration

### Statement

1. **What selects on first admission.**
   - `31` R-ADM-3: "The fingerprint is the only selector of root chain, Trust Policy, Trust State and therefore the negative
     set. No compiled value, clock, repository file or environment variable is an input." `25` AP-2: "Lineage: bootstrap
     from the typed fingerprint's epoch." `31` R-CER-2: the fingerprint "commits to the lineage id".
   - `06` §1–§2: the trust-root id, every state fingerprint and the admitter digest are published in the same independent
     channels. `31` R-ADM-2: the operator selects the evaluator by comparing its digest with those channels.
   - `01` A20 names the "independent-channel attacker (stale or forged channel page)". `29` §3 ranks "a human typing a value
     read now from an independent channel" at rank 2.
2. **What one forged page therefore selects.** A page showing the fingerprint of a lineage the attacker generated selects
   the attacker's root v1, its Trust Policy (with `channel_quorum` 1), Trust State, registration, verification
   attestation, two one-signature reproductions and publication. Each is valid within that lineage. No genuine key is
   used, and no withholding is needed: the attacker's bundle is the download.
3. **OP-13 (b) is enforced by the value it is meant to check.** `25` AP-3 compares the typed count with
   `bootstrap.channel_quorum` of the Trust Policy that the typed fingerprint selects. The admitter has no compiled minimum.
   An operator who types the one value a compromised channel shows is admitted. `CHANNEL_DISAGREEMENT` arises only for an
   operator who independently knows to type two values.
4. **The evaluator is selected by the same channel.**
   - The reference executor never reads the selected state's `bootstrap.admitter_digests` and has no rule for a revoked or
     superseded admitter; `evaluator_digest` is used only for the self-evaluation check.
   - R-ADM-1's "registered, quorum-reproduced artefact" is checked by nobody on the machine.
   - An evaluator that skips negatives admits a revoked binary: a substituted admitter, or a genuine defective version whose
     digest the channel still lists.
5. **Pack statements contradicted.**
   - `30` §10 G_BYTES key-theft rows for FA1 ({ch1, rep×q, ts, transport} or {ch1, regk1, regk2, rep×q, ts}; FA2 adds `ch2`)
     and the G_SRC key-theft rows.
   - `25` §7: "q reproducer keys + trust-state key + the channel(s) the victim types (+ transport, or + registration keys)".
   - `05` §3 minimum-sets table.
   - `21` OP-13 (a) and (b), and the combinations "OP-9 (a) + OP-13 (a) | first admission: {ch1, 2 reproducer keys,
     trust-state key, transport}" and "OP-9 (c) or (d) + OP-13 (b) | first admission key-theft sets need both channels and
     all three reproducer keys, or the registration keys".
   - `31` §9 AD-1: "All channels the operator uses are compromised together with the trust-state key and reproducer quorum
     keys".
   - CS5's H-CH rule: "`ch_k` shows t_x's" (a descendant of the genuine lineage, which needs `ts`).
   - FD-1 §2 (5): a shortfall must be a stated residual with an exact bound. AD-1's bound is wrong, and RS-B1 covers only a
     stale page.

### Evidence

- **executed** `RV5-B-A01-first-admission-channel.json` (reference executor unmodified; 48 OpenSSL verifications; attacker
  key labels disjoint from genuine ones):

  | Row | Result |
  |---|---|
  | control: genuine lineage, two genuine fingerprints | `ACCEPTED` |
  | control: genuine OP-13 (b), one genuine fingerprint | `CHANNEL_QUORUM_NOT_MET` |
  | control: the architect's CH2 shape (attacker bundle, genuine fingerprint) | `STATE_NOT_HELD_OR_FINGERPRINT_MISMATCH` |
  | control: one compromised channel, operator types both values | `CHANNEL_DISAGREEMENT` |
  | A01a OP-13 (a): the channel shows the attacker lineage's fingerprint | **`ACCEPTED`** |
  | A01b OP-13 (b): both channels show it | **`ACCEPTED`** |
  | A01c genuine owner under OP-13 (b); one compromised channel; one value typed | **`ACCEPTED`** |
  | A02 evaluator that skips negatives, genuine fingerprints, binary revoked in the selected state | **`ACCEPTED`** (genuine admitter: `BINARY_REVOKED`) |
  | executor source: `admitter_digests` referenced / compiled or typed root id input / quorum read from the selected Trust Policy | false / false / true |

- **computed** `RV5-B-A04-calculator-extensions.json` part L. CS5 is unmodified; its `accepted` is wrapped with the
  strategy "the channel shows a lineage the attacker generated", and the original function is still called for every other
  strategy. Results over every configuration:
  - FA1 minimum {ch1} in 96 of 96 configurations;
  - FA2 minimum {ch1, ch2} in 96 of 96;
  - FA2 with the quorum read from the selected state: {ch1} in 96 of 96;
  - 480 committed FA minimal sets are superseded;
  - 0 monotonicity violations.
- **design** `31` R-ADM-1…3, R-CER-2, §9 AD-1; `25` AP-2, AP-3, §7; `06` §1–§3; `30` §10; `21` OP-9, OP-12, OP-13 and
  combinations; `01` TA-5, A20; `29` §3, §4 (no row for lineage selection or evaluator selection at first admission).

### Failure scenario

1. The owner publishes the root id, state fingerprints and admitter digest on an owner-run download page that is not the
   Git host (a qualifying channel, `06` §2).
2. The page is compromised. It now shows the attacker's root id and fingerprint and links the attacker's bundle; the admitter
   digest is left genuine.
3. A new team member follows `06` §3: compares the admitter digest, types the fingerprint, runs `gov-admit`.
4. The attacker's binary, whose compiled lineage is the attacker's root, is admitted, installed from the buffer and
   recorded. It is now the machine's TCB, and every later trust decision on that machine is the attacker's.
5. The owner had chosen OP-9 (c) and OP-13 (b) because `21` said first admission would then need both channels and all
   three reproducer keys, or the registration keys.

### Why HIGH

- **TCB compromise below the declared threshold.** The declared minimum names reproducer keys, the trust-state key and
  transport, or registration keys; the actual minimum is the channel or channels alone.
- **Owner options.** The OP-9 and OP-13 consequence statements are false: the BC4-4 class, which was blocking in review r4.
- **FD-1 §2 (5).** The shortfall is neither refused nor stated with an exact bound.

### Unavoidable core versus this finding

| Situation | Determination |
|---|---|
| A first-install machine must take some value from an out-of-band channel | core, acceptable when stated exactly |
| The declared first-admission minima include keys the channel attacker does not need | **not core**: computing the minima with lineage and evaluator substitution gives the exact statement |
| The two-channel rule is read from the state the channels select | **not core**: a compiled minimum in the admitter removes it |
| The evaluator is chosen by the same page, with no binding to the selected state's admitter list or negatives | **not core**: the admitter can check its own digest against the selected state |

### Class and novelty

This is the remainder of BC4-2 (the selector of the first TCB), at its intersection with BC4-4. It is also the recurring
class: a rank-2 input, one channel page, selects rank-1 facts, the root of trust and the evaluator. The instance was not
attacked before: the architect's CH2 and K2 constructions change only the state inside the genuine lineage.

### Correction direction (architectural)

1. Compute first-admission minima with lineage substitution and evaluator substitution as strategies. State AD-1 as "the
   channels the operator reads". State that OP-2, OP-8 and OP-9 do not change it.
2. Make OP-13's quorum a compiled minimum of the admitter that applies to the root id, the state fingerprint and the
   admitter digest alike. It must never be a field of the selected Trust Policy.
3. Bind the lineage to a value the same page does not carry, or state exactly that it cannot be. For example: a root id
   compiled into a separately authenticated admitter, or delivered through a second authentication path.
4. The admitter refuses when its own digest is absent from the selected state's admitter list or is in its negative set.
5. Conformance vectors: an attacker-lineage fingerprint typed; one value typed under a genuine quorum of 2; a
   negative-skipping evaluator.

---

## RV5-B-H2 — HIGH — The build image selects the bytes of every production binary: its digest is legitimised only by an "owner's image record" that no rule assigns to anyone, no check establishes its content, and every honest reproducer (including an OP-10 (b) diverse one) reproduces the same malicious bytes

### Statement

1. **The fact and its unassigned selector.**
   - F-INPUTS (`30` §2): "the build inputs are the admitted inputs". The input manifest names `build_image_digest` (`30`
     §4.2; required by `schemas/input-manifest.schema.json`).
   - R-REG-3 (c): the ceremony checks "the build image digest against the owner's image record". No section of the pack
     names who produces that record, from what, or under which authority; "image record" occurs only there.
   - `29` §4 has no row for it.
2. **Nobody establishes the image's content.**
   - Verifiers check "the manifest against upstream signed checksums" (R-VER-1). An image has no such checksum.
   - CS5's honest parties (H-VER, H-REG) check toolchain archive digests only.
   - Reproducers obtain the image by digest (R-REP-2), so they are carriers of a value someone else chose.
3. **The image determines the bytes.** Executed: two reproducers in different directories build the same source with the
   same rustc 1.98.1 and flags (path remapping, fixed options), each using the build image. When the image's linker driver
   adds one object, both produce bit-identical binaries that differ from the clean-image binaries and run injected code.
   The toolchain is unchanged and no build or image path is embedded.
4. **Consequence.** Whoever selects the image record's content selects the bytes every honest reproducer obtains.
   - The quorum is met, no reproduction conflicts, the publisher publishes, and P1, P2 and FA victims accept.
   - OP-9 (a)–(d) change nothing: under (d) the custodians' own reproduction uses the same registered image.
   - OP-10 (b) changes nothing: the diverse reproducer "must match" bit for bit, so it must use the same image.
   - OP-10 (c) replaces the toolchain archive, not the image.
   - If the release pipeline produces the record (an A5/A6/A16 capability), the minimum is {pipeline}. If the owner builds
     it from upstream base images or packages, the minimum is {image supplier}, with no checksum rule, option or residual.
5. **Pack statements contradicted.**
   - CS5 G_INPUTS: "The pipeline alone never succeeds (the ceremony and verifiers check upstream checksums)", and INV-INPUTS.
   - `30` §10 and `05` §3: "accepted malicious named build inputs: registration custodians at threshold + OP-8 verification
     keys".
   - `25` §8: "Its source and build inputs: the registration (rank 1 or 2), first-hand verification records, upstream
     checksum checks".
   - `21` OP-10 consequences.
   - TB-S2 / TA-12, which cover only "the upstream toolchain release that passes the checksum check".

### Evidence

- **executed** `RV5-B-A08-build-image-selects-bytes.json`. Clean image: two reproducers, both
  `sha256:2954f7131880a1ddb9a30667c272f910c4a0ad81d33d71ff1027e22d084845bc`, output `gov: genuine behaviour`. Evil image:
  two reproducers, both `sha256:d8426b8921f41c45ea3e8cc2de700b5e89066311e0aebcdeb1b699b66fe02e75`, output
  `INJECTED-BY-BUILD-IMAGE` then the genuine line. `toolchain_unchanged: true`; `no_build_or_image_path_embedded: true`.
- **computed** `RV5-B-A04-calculator-extensions.json` part I. G_IMAGE minimal sets for P1, P2 and FA1 under every OP-2, OP-8,
  OP-9 and OP-10 answer: {pipeline} when the record is pipeline-produced; {image_up} when it is owner-built from upstream
  images; none when the image is itself a digest-pinned, independently reproduced input. CS5's goal atoms contain no image
  atom.
- **design** `30` §2, §4.2, R-REG-3 (c), R-VER-1, R-REP-2, §10, §12; `05` §3; `25` §8; `21` OP-10; `29` §4.

### Failure scenario

1. Release CI builds the Rust build image (base OS, linker, C runtime objects) and records its digest. That record is what
   the registration ceremony compares the manifest against.
2. An attacker with the CI job replaces a C runtime object in the image.
3. R-REG-3 (a) passes (toolchain archives equal upstream checksums), (b) passes (lockfile in source), and (c) passes (digest
   equals the record). Verifiers accept clean source.
4. Every reproducer fetches the image by digest and obtains the same malicious binary. The quorum is met and the publisher
   publishes it.
5. Every machine accepts it, including pinned CI runners.

### Why HIGH

- **TCB compromise below the declared threshold.** One infrastructure input suffices; the declared minimum is the
  registration threshold plus OP-8 verification.
- **No owner option raises it.**
- **FD-1.** The image is a selector of bytes with no authority, and no residual is stated.

### Class and novelty

This is the remainder of BC4-1, whose invariant requires each fact that makes a binary the TCB to be established by
independent parties. The faithful-build fact is established first-hand for the source, lockfile and toolchain archive, but
not for the build environment. A reproduction quorum cannot detect a common-mode input that all reproducers must share.
The instance is new: CS5's G_TOOLCHAIN models the toolchain archive only.

### Correction direction (architectural)

1. Make the build environment a registered input whose content is established first-hand: digest-pinned upstream components
   with signed checksums that the ceremony and verifiers check, and the image itself reproduced bit for bit from them by
   independent parties. Alternatively, build it from source under an OP-10 (c)-style owner option.
2. Name the producer and authority of the image record in the decision register.
3. Add image-provenance atoms and goals to the derivation calculator. State the remaining upstream residual with options.
4. Add an acceptance test that substitutes the image.

---

## RV5-B-H3 — HIGH — Policy-root content under OP-2 (b): E7 has no verification-record restrictor and the calculator derives no policy-root goal, so two delegated registration custodians plus one `release-final` key (or, by key theft, two delegated registration keys plus the trust-state and `release-final` keys) make malicious non-orderable constitutional content effective; OP-8 changes nothing, `release-final` is in the minimal sets, and the declared consequences are false

### Statement

1. **What E7 requires of a policy root** (`19` §6 E7, `23` §12.3; the `29` §4 register row "Policy root eligibility …
   restrictors: floors; registered precedence; E3/E4/E9/E10"):
   - the registration of *R* is referenced by the effective Trust State;
   - *R*'s final verifies under `release-final`;
   - the kernel tree digest and non-join units equal the registration.

   There is no verification-record condition. The binary predicate has one: `25` AP-5 requires OP-8 ACCEPTED attestations
   listed by the registration.
2. **Who references a registration.**
   - The honest publisher references a registration "only when received first-hand from the ceremony" (`30` R-PUB-1). The
     verification conditions of R-PUB-1 apply to binary digests.
   - A stolen trust-state key's descendant can reference any registration. For C1–C2, such a descendant is effective on
     anchored and pinned machines; revision 5 removes only C3 (`24` §4.4).
3. **Minimal sets under OP-2 (b)**, for any OP-8 value:
   - {cust1, cust2, rf} with A2: the registration is first-hand, the honest publisher publishes it, and every machine uses
     it, for use and ingress.
   - {regk1, regk2, ts, rf} with A2: effective for C1–C2 on anchored and pinned machines and on OP-7 (d) runners.

   Neither set contains a verification compromise; both contain `release-final`. Under OP-2 (a) the same sets are the root
   threshold (A8), which is not a finding.
4. **What the content can be.** Any non-orderable unit: secret patterns, tool descriptors including their health commands,
   hard invariants, schemas, skills. The registration-reduction mechanism reports only exact reversions, and only in the
   ceremony tool (RV5-B-M2). A non-identical weakening therefore reports nothing.
5. **Pack statements contradicted.**
   - `05` §1 `release-registration` row: "At the threshold: registers malicious source, inputs or non-orderable content for a
     new release; accepted only with OP-8 verification statements and publication".
   - `05` §1 `release-final` row: "`release-final` appears in no minimal set (CS5 INV-RF)".
   - `21` OP-2 (b): "two delegated custodians plus OP-8 verification keys register malicious source, inputs or non-orderable
     content".
   - `21` combination "OP-2 (b) + OP-8 = 1 | {two delegated custodians, one verification key}".
   - `21` OP-4: "neither `release-candidate` nor `release-final` selects a production binary or a policy root; they appear in
     no minimal set".
   - `21` OP-8 (content protection implied).
   - `00` §1: `release-final` "selects nothing".
   - CS5 computes goals for binaries only (G_SRC, G_INPUTS, G_BYTES, G_MIRROR, G_TOOLCHAIN).

### Evidence

- **computed** `RV5-B-A04-calculator-extensions.json` part P: this review's enumeration of the revision-5 rules, over
  OP-2 × OP-8 × three victims × two E7 variants. For OP-2 (b), both OP-8 values, and E7 as written:

  | Victim | Minimal sets that violate the declared minimum |
  |---|---|
  | use on an anchored or pinned machine (C1–C2) | {cust1, cust2, repo, rf}; {regk1, regk2, repo, rf, ts} (and mixed custodian/key forms) |
  | ingress with a P1 proof (C3) | {cust1, cust2, repo, rf} |
  | ingress with a P2 typed fingerprint | the above, plus {ch1, regk1, regk2, repo, rf, ts} |

  With E7 extended by the verification-record condition (the correction), every non-insider set contains OP-8 verification
  compromises.
- **computed** with the architect's P4r5 functions, unmodified, on world W11 plus a registration `g12` with no verification
  record, a `release-final` `F12`, and a trust-state thief's descendant `t12x` of the anchored `t11`:

  | Machine | `eligible_release_r5(F12)` | Allowed classes | C3 covers `t12x` |
  |---|---|---|---|
  | human anchor today | eligible | C0–C3 | false |
  | human anchor, 40 days old | eligible | C0–C2 | — |
  | pin, 1 day old | eligible | C0–C3 | false |
  | OP-7 (d) runner | eligible | C0–C2 | — |

  Control: a binary of the same registration gives `accept_binary` = `VERIFICATION_RECORDS_BELOW_MINIMUM`.
- **executed** `RV5-B-A09-floor-class-kernels.json` (pack checker; real 4.1.5 consumer):
  - a 4.1.8 registration whose `aws-access-key` regex is `(?:AKIA)[0-9A-Z]{16}` (as weak as 4.1.6's, not byte-identical):
    E7 exit 0; `registration-reductions` exit 0 with no reduction;
  - on 4.1.5, the `ASIA…` key file is excluded under 4.1.7 and indexed and served under 4.1.8;
  - a `TOOL-GIT-001` `health_check` command changed from `['git', '--version']` to a shell command: E7 exit 0; no
    reduction.
- **design** `19` §6; `23` §12.3–§12.5; `29` §4; `30` R-PUB-1, §10; `25` AP-5; `24` §4.4; `05` §1; `21` OP-2, OP-4,
  OP-8; `00` §1.

### Failure scenario

1. The owner chooses OP-2 (b), to keep root keys offline, and OP-8 = 2, for two independent verifiers.
2. An attacker steals the `release-final` key, an online everyday key, and compromises the two delegated registration
   custodians' ceremony host.
3. They register 4.1.8, identical to 4.1.7 except the `aws-access-key` regex variant and the `TOOL-GIT-001` health command.
   `draft-registration` lists no reduction; the registration names any two verification record digests.
4. The honest publisher references it, because it was received first-hand. A2 commits 4.1.8.
5. Every machine uses it as the policy root: temporary AWS keys are indexed and served to agents, and the tool health check
   runs the attacker's command. No verifier ever checks the two verification records the owner chose.

### Why HIGH

- **Security control loss below the declared threshold.** The declared minimum requires OP-8 verification statements; the
  actual one does not.
- **Owner options.** The OP-2 (b), OP-4 and OP-8 consequence statements are false (BC4-4).

### Class and novelty

This is the remainder of BC4-3 at its intersection with BC4-4. Revision 5 moved the selector of non-orderable content from
`release-final` to the registration (RV4-H3 as stated is closed: REG5 reproduced). At the verifier, that selector's
authority is lower than declared, because the verification restrictor exists for binaries only, and the calculator derives
no policy-root minima. The instance is new.

### Correction direction (architectural)

1. E7 applies AP-5's verification-record restrictor: at least OP-8 ACCEPTED attestations, listed by the registration, for
   its source, unrevoked, with no REJECTED verdict. Alternatively, state the weaker minimum and its option.
2. Derive policy-root goals (use and ingress, per victim class) in the calculator. Restate `05` §1, `21` OP-2, OP-4 and OP-8
   from its output.
3. Apply RV5-B-M2's corrections to registration reductions.

---

## MEDIUM

Every MEDIUM is carried with a bound acceptance test (`04-CARRIED-REQUIREMENTS.md`). None needs an architecture change, for
the reason given.

| ID | Statement | Evidence | Failure scenario | Why MEDIUM, not blocking | Correction direction |
|---|---|---|---|---|---|
| **RV5-B-M1** | **Revocation removes restrictors, and the calculator models that removal only through transport.** `25` AP-4 says revoked reproductions, attestations and keys "count for nothing below", and `30` R-REP-5 clears a conflict when "a revocation removes one side". A stolen trust-state key's descendant can therefore list the honest conflicting reproductions, or a REJECTED verification attestation, in `revocations`, and the predicate ignores them. The same holds for a `revocation` key (threshold 1; shareable with `trust-state` under the whitelist), since a revocation delivered alone is effective immediately (`17` §8). `05` §1 describes `revocation` as "denial of service only" and says the trust-state key can "never … lift a negative"; removing the REJECTED or conflict restrictor has the effect of lifting one. CS5 lets these restrictors disappear only when `transport` withholds them. | **executed** A03 (reference executor): stolen p1, p2 and ts; the channel shows t11x; honest reproductions held. Without revocations: `REPRODUCTION_CONFLICT`. With the honest reproductions listed in `revocations`: **`ACCEPTED`**, no transport. **computed** A04 part R: in 36 of 216 P2/FA configurations, committed minimal sets lose `transport`; for example G_BYTES, OP-2 (a), OP-8 = 1, OP-9 (a), P2: {ch1, rep1, rep2, transport, ts} becomes {ch1, rep1, rep2, ts}. The P4r5 oracle has two conflict rows, neither with a revoking Trust State. | A channel page, two reproducer keys and the trust-state key reach a P2 or FA victim that holds every honest reproduction, with no transport. | The key sets still need q reproducer keys, the trust-state key and the victim's channel. The correction is a bound rule plus recomputation, with no new trust relationship. | A revocation of a reproduction or verification attestation clears neither the conflict nor the REJECTED verdict it caused unless issued under the registration authority (or root) through the `05` §9 playbook. Recompute the minima; add oracle rows. |
| **RV5-B-M2** | **Registration reductions are exact-match and ceremony-side only.** `23` §12.4 computes `registration_reversion` as equality with a value an intermediate registration superseded. `23` §12.5 places the computation in the ceremony tool; the verifier runs "E7 as §12.3", which computes none. RT-141 nevertheless expects a verifier refusal "without history" that no rule defines. Consequences: (i) E7 accepts an undeclared exact reversion; (ii) withholding the intermediate registration hides the reversion; (iii) a non-identical but equally weak value, or a changed tool command, is reported by no mechanism. Rule (6) and HO-0001 §3.1 ("values move down only through a computed, cumulatively declared, per-project-gated reduction") therefore hold for non-orderable units only against exact reversion reported by an honest ceremony. | **executed** A09 and A10 (checker; 4.1.5): E7 exit 0 on the undeclared exact reversion, while `registration-reductions` exits 6; with 4.1.7's registration withheld, `registration-reductions` exits 0; variant regex and tool command: exit 0 with no reduction; on 4.1.5 the variant indexes and serves the `ASIA…` file. | A registration authority, or under OP-2 (b) the RV5-B-H3 sets, weakens secret handling with a non-identical value; no project gate is raised, even on recorded machines. | Under OP-2 (a) the actor is the root threshold (review r4 did not rate root-registered pinned content as a finding). The lower-authority case is counted in RV5-B-H3. The correction is a verifier rule and restated claims. | The verifier computes reductions over every registration the effective Trust State references (`INCOMPLETE` if one is not held) and refuses undeclared ones, as `TRUST_POLICY_UNDECLARED_LOWERING` does for policies. Every change of a security-classified non-orderable unit between consecutive registrations is listed in the per-project gate on recorded machines. Rule (6) states what "down" means for non-orderable units. |
| **RV5-B-M3** | **Re-admission discards the machine's monotonic trust state.** `31` R-ADM-8 moves aside "any verifier trust store present for the lineage before the first admission"; "first admission" is not defined, and the reference executor (`write_admission_record`) moves the store aside on every run. Re-admission through `gov-admit` is the documented path in two cases, because an expired-record or self-revoked binary runs C0 and `verify-artifact` is C3: GB-2 with OP-14 (b) ("periodic re-admission"), and GB-3 with OP-15 (a) ("incident response needs a new binary admitted first"). The store holds anchors, the clock and accepted-TBM high-waters, and per-project records: the highest installed sequence (E10), strength vectors (`26` §6) and held registrations (`policy_lowering` gates). Moving it aside contradicts `24` §8 ("components never decrease"). | **code** `gov_admit_reference.write_admission_record`. **computed** A12 row M8: E10 reasons for an older release before re-admission `['revoked', 'downgrade_without_transaction']`, after `['revoked']`. **design** `31` R-ADM-8, GB-2, GB-3; `21` OP-14 (b), OP-15 (a); `24` §8. | Under OP-14 (b), a workstation re-runs `gov-admit` after its record expires. A2 has committed an older eligible release (OP-11 (a)). The downgrade and the loss of recorded project strength are no longer detected; an older genuine binary is no longer below an accepted-TBM high-water. | The trigger is an operator procedure, and the effect is loss of detection, not forgery. The fix is a bound rule. | First admission means that no store exists for the lineage, or that no admission record was ever written in it. Re-admission keeps the store and checks its prior admission record. AD-2's move-aside applies only to first admission. Tests for both cases. |
| **RV5-B-M4** | **The source identity is ambiguous, and its evidence tests a different, time-dependent function.** (i) `30` §4.1 hashes the sorted lines `<mode> <path> <SHA-256>`. A Git path may contain a newline, so two trees with different file sets can have identical line sequences; the canonical digest is equal under both delimiter readings while a build-relevant file (`.cargo/config.toml`) is absent from one tree. R-REG-3 (e) and R-REP-2 recompute the digest from a fetched tree. (ii) SRC5, cited for the canonical digest (`30` §4.1, `05` §11, `22` §1 "equal across repositories … 10/10"), hashes `git archive` of a tree id, which the pack itself calls time-stamped. | **executed** A05: equal canonical digests (`sha256:9d9e9e47…` joined; `sha256:ba529e73…` terminated) for Git trees `2055cf0f…` and `bd97776e…`; tree archive digests at t and t + 2 s differ. **executed** re-run of SRC5: every digest differs from the committed output, and all verdicts stay true because each run compares values computed within one run. | A carrier serves a tree whose merged path swallows `.cargo/config.toml`; reproducers that check only `content_digest` build different code than the verifier reviewed. | `release_commit` is also registered, and a harmful exploit needs a file whose absence does not break the build. The correction is an encoding and a test. | An unambiguous encoding (length-prefixed or NUL-separated; refuse control characters in paths) or the Git tree object id under SHA-256. Fetch and check by commit and content. Replace SRC5 with a test of the specified function. |
| **RV5-B-M5** | **The decision register is incomplete in the architecture, and misclassifies selectors.** `29` §4 lists only "the decisions whose selectors revision 5 changes or states for the first time"; R-SEL-1 leaves the full register to the binary. The rows this review found load-bearing are absent or wrong: first-admission lineage selection (the channel); evaluator selection (the channel digest); the channel quorum (read from the selected Trust Policy); the build image record (no authority); the policy-root verification restrictor (absent); revocation acting as selector of a conflict outcome; and Git delivery choosing among eligible releases under OP-11 (a), listed as a carrier. | **design** `29` §4, R-SEL-1…4; A01, A03, A06, A08. | FD-1 claims closure through the register; a reviewer or implementer who checks the listed rows finds none of the HIGH findings. | The HIGH findings are separate. A complete register is a bound deliverable with RT-128. | List every trust decision's selectors, restrictors and carriers in the pack, including those above; RT-128 asserts each row, and FD-3 derives each consequence from it. |

## LOW

| ID | Statement | Evidence | Carried as |
|---|---|---|---|
| RV5-B-L1 | The reference executor takes the lineage from the first self-verifying root v1 in bundle order, whereas `25` AP-2 takes it "from the typed fingerprint's epoch". A self-signed root served first makes a genuine admission fail (availability). No FA5 conformance vector holds two root v1 statements. | **executed** A01 ORD: attacker root first, genuine fingerprint: `STATE_NOT_HELD_OR_FINGERPRINT_MISMATCH`; genuine first: `ACCEPTED` | CR5-B-06 |
| RV5-B-L2 | The admission record is unsigned (`schemas/admission-record.schema.json`: "never signed"), and GB-1 honours any record naming the binary's digest. A package or archive that ships a genuine revoked binary with a record passes GB-1. A root-owned package location also satisfies GB-4, and GB-3 binds only where the revocation is held. TB-1′ ("GB rules bind genuine binaries, including revoked ones") holds only for installs that did not ship a record. | **code** `gov_admit_reference.gov_run`, `load_admission_records`; **design** `31` GB-1…GB-5, TB-1′ | CR5-B-07 |
| RV5-B-L3 | On a machine whose clock high-water is old (restored from backup, long offline), a clock set back to within the C3 window of an old human anchor yields a P1 currency proof for the stale state. Newer genuine statements are refused at ingest as "future", so C3 runs on a state that precedes a revocation. The restated RS-2 is exact ("below the high-water"), but `24` §5.3 ("C3 refuses without a fresh proof") and §5.7 hold only under TA-7. | **computed** A12, M3 CLOCK-back rows under OP-7 (a)–(d): human anchor aged 5 days, effective t5, C3 with a currency proof naming it, revoked R7 eligible | CR5-B-08 |
| RV5-B-L4 | Stale text contradicts revision-5 rules. "Only witnesses raise the clock high-water" remains in `24` §8 (second clock paragraph) and the §10 RS-2 row, `17` header and S11, `01` TA-7 and G23, and `02` I-68. `24` §3.5 (3) still enumerates a deny list, against the allow list of `27` §3.3 and rule (21). `24` §9 keeps revision 4's labelled OP-7 proposal, although `21` says every proposal is withdrawn. | **design** | CR5-B-09 |
| RV5-B-L5 | CS5's victim classes are P1, P2, FA1 and FA2. Witness-reliant runners under OP-7 (c) and CI runners with an admission record and pin are not enumerated, yet `25` §7 states "under any owner answer (CS5: 0 invariant failures over 408 configurations)". | **computed** A04 part C | CR5-B-10 |
| RV5-B-L6 | No minimum root threshold appears in the normative text: KS-1′…KS-13 and the Fact Threshold Check set none, and OP-1 leaves the threshold open. At root threshold 1, one root key signs every Trust Policy (floors, `bootstrap` including `channel_quorum`, `clock_reset`, `accepted_tbm_reset`). The reference instruments compile 2 (`gov_admit_reference.COMPILED_MIN`, P4r4 `COMPILED_MIN_THRESHOLD`). | **design** `05` §3; **code** reference instruments | CR5-B-11 |
