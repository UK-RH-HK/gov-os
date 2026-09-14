# 00 — Root cause of the persistent RoT-1 blocking classes (specialist A)

| | |
|---|---|
| Run | AR-0009, role `rot-specialist-architect`, handoff `HO-0009` |
| Status | **Proposal input for the revision-5 synthesis architect. Not an architecture revision, not a review verdict, not an owner decision.** D-0008 and ARCH-0002 are untouched and remain PROPOSED. |
| Base | branch `phase1/rot1-r5-specialist-a` from `6ea45a57cb17820c02366f2e75e37cee8f38099d`; revision 4 (`bca05a7`) and its review (`97a5545`) identical at base (`evidence/outputs/E0-baseline-LOG.txt`) |
| Starting lens | A — the verifier's minimal trusted inputs |
| Date | 2026-09-14 |

## Independence and disclosures

- **Authored before by this session:** nothing. No RoT-1 revision, no review, not specialist B's proposal.
- **Read under `release/orchestration/`:** `HANDOFFS/HO-0009-rot-specialist-r5-a.md`, `HANDOFFS/HO-0001-rot-architect-r3.md`,
  `AGENT_RUNS/README.md`.
- **Disclosed incidental exposure (nothing opened):**
  - a directory listing of `HANDOFFS/` showed the file names of other handoffs, including HO-0010;
  - one listing of the session scratchpad root showed the names of sibling scratch directories, including `ar-0010`;
  - the host supplied the user's auto-memory index (one-line summaries of earlier reviews), which was not opened and on which nothing here rests.
- **Hygiene slip, disclosed:** one command wrote a temporary copy of pack file `24` to the scratchpad root instead of `ar-0009/`.
  It was moved into `ar-0009/notes/` by the next command. No other location was written.
- **Read in full or in the parts cited:** reviews r1–r4 (consolidated reports, findings, correction deltas; r4 B, C and D files;
  r3 D files), the revision-4 pack (`00`, `01`, `05`, `06`, `07`, `17`, `19`, `21`, `23`, `24`, `25`, `27`, `28`; `11` Phase 4),
  D-0007, D-0008, ARCH-0002, and the runtime paths cited (`runtime/build.rs`, `runtime/src/security/secrets.rs`,
  `cli/src/main.rs` root discovery).

## 1. Summary

**One root cause explains all three persistent classes, and it is testable per decision.**

Every revision checked that the value a lower-trust party supplied was a **member of a set** that a higher authority had
approved. The lower-trust party still chose **which member** became the effective fact.

That substitution is harmless where the value has a lattice join: the join makes every member yield an effective value at
least as strong as the floor, so the join itself acts as the selector. It is not harmless where no join exists. That covers:
- which binary is the TCB;
- which source and which build inputs it came from;
- which Trust State is current;
- which pinned constitutional content is in force.

In each of those cases a set with more than one member is a choice left to the lower-trust party.

| Class | Set checked (authority) | Member chosen by (lower trust) | Invariant never established |
|---|---|---|---|
| **BC4-1** independent TCB decisions | binaries with a build attestation, custodian signatures and an attested source | one `build-attestation` key plus the pipeline (bytes); one `verification-attestation` key (source); the release process (build inputs) | the TCB's source **and build inputs** are selected by the registration authority; its bytes are selected by a quorum of first-person reproductions from those inputs |
| **BC4-2** anchored first TCB | genuine signed binaries and states ever published | the transport (which statements exist on the machine), and the candidate itself (what it prints, what it confirms) | the first acceptance consumes a **current selector of state** at local-machine authority, runs the same acceptance function on externally measured bytes, and binds the bytes that run to the bytes accepted |
| **BC4-3** release-scoped registration | digests registered as permitted for a key | threshold-1 `release-final` | the registration is a **function of the release** (exactly one digest per unit per registered release), not a domain of permitted values |

The invariant, stated once for every decision, is **SEL-1 (selection authority)** (§5). An encoding of 43 decisions across
revisions 1–4 flags every row behind the 14 HIGH findings of the four reviews (18 rows) and all 10 encoded MEDIUM and LOW rows.
It flags none of the 12 mechanisms the reviews confirmed sound (`evidence/E1-selector-audit.py`; design-encoded, see §6).

## 2. Why each class survived: the chains

### 2.1 BC4-1 — independent decisions for the TCB (R2-H3 → RV3-H3 → RV4-H1)

| Revision | Finding against it | Correction applied | Remainder | Why it remained |
|---|---|---|---|---|
| 1 (`676dfce`) | RV-H4: the certification role signs the legacy identity that makes a kernel authentic | CD-1/CD-3: only compiled historical identities; artefact statements under the release purpose | R2-H3: the TCB is authenticated by one threshold-1 `release-final` signature | binary authenticity was modelled like release authenticity, so one purpose key selected the TCB |
| 2 (`d37b05c`) | R2-H3 | CD2-3: `release-artifact` purpose at threshold ≥ 2; compiled T0 identity in the artefact statement; attestation | RV3-H3: every signer checks the bytes against the `release_commit` that threshold-1 `release-final` names | the threshold was added to **who signs the bytes**; the **source** selector stayed with `release-final` |
| 3 (`ca77a43`) | RV3-H3 | CD3-3: V8 source equality; source taken from an ACCEPTED verification attestation; custodial stages | RV4-H1: the faithful-build fact rests on one `build-attestation` key plus pipeline input; the source fact on one `verification-attestation` key | signatures were counted **per purpose**, not per independent observation or selection. Custodians and the publisher re-check that an upstream signature exists; that adds signatures but not selectors. |
| 4 (`bca05a7`) | RV4-H1, extended by D-A07 | (none yet) | this specialist's E2: **the build inputs** (toolchain, lockfiles) in `release.source.build_inputs_digest` are named by the release process and are not evaluated by the independent verifier, which reproduces the kernel payload (`05` §7 rule 3, `07` §3). Under that reading the pipeline alone yields an accepted malicious binary under OP-2 S0, S1 and S2, with zero keys. | the same substitution one component down: every check confirms that the binary equals `build(source, inputs)`; nothing selects `inputs` at the authority the binary carries |

**Invariant never established.** Each component that determines the TCB must have its own selector at or above the
authority the binary carries:
- **source tree and build inputs:** the registration authority;
- **bytes:** a quorum of first-person reproductions whose inputs are fixed by digest;
- **current acceptability:** the machine's current selector of state.

A signature counts only for the component its signer selected or observed.

### 2.2 BC4-2 — anchored, non-circular first TCB acceptance (R2-H2 ∩ R2-H3 → RV3-H2 → RV4-H2)

| Revision | Finding against it | Correction applied | Remainder | Why it remained |
|---|---|---|---|---|
| 1 | RV-H2: lifecycle facts replay- and omission-unsafe; RV-M6: bootstrap channels co-hosted; OP-6 TOFU | CD-2: monotonic lifecycle; CD-10: independent channels | R2-H2: on a machine without retained state the repository selects the effective trust state; the compiled T0 is shown as current | the only selector available on a fresh machine was what the repository supplied |
| 2 | R2-H2 | CD2-2: `FRESHNESS_UNPROVEN`; state pins; `confirm-state`; OP-7 | RV3-H2: anchors satisfied by the supplier's sequence number; pins with no currency; threshold-1 witness; RV3-D-A15 a revoked binary accepted on pinned CI | the anchor was compared with a number the supplier chooses, and a past anchor stood for "now" |
| 3 | RV3-H2 | CD3-2: inclusion anchors; pin validity; currency proofs P1/P2/P3; separate witness purpose | RV4-H2: the **first** binary is accepted outside those rules, by tooling that checks A2–A6 only, or by values the candidate prints, and all TA-5 ceremonies run on it | anchors and currency proofs are implemented **inside the binary**. Non-circularity was proven for "binary N accepts binary N+1" and extended to "the machine" by assumption (TA-1, TB-1). The first acceptance is a documentation procedure with weaker checks. |

**Invariant never established.** Every TCB acceptance, including the first on a machine, must meet all of these:
- it consumes a selector of the **current** published state at local-machine authority (a fingerprint typed now from an
  independent channel, or a protected pin within its window);
- it applies the same acceptance function as `verify-artifact`;
- it runs on bytes measured by code other than the candidate;
- the bytes that later run as `gov` are bound to the bytes accepted.

**Lens A result.** A first machine has no compiled trust, no state and no trustworthy clock. It can still reach a current,
negative-set-checked acceptance from **one typed value**. The r4 state fingerprint (`24` §3.1) is a 128-bit commitment to the
epoch object, which contains the lineage id, the root version and digest, the Trust Policy version and digest, and the Trust
State sequence and digest. Typing it:
- selects the Trust State, and therefore its cumulative revocations;
- selects the root chain;
- carries currency (P2) with no clock.

Executed: `evidence/E3-first-binary-acceptance.py`, reference executor `evidence/gov_accept_reference.py`.

### 2.3 BC4-3 — release-scoped registration of constitutional content (R2-H1 → RV3-H1 → RV4-H3)

| Revision | Finding against it | Correction applied | Remainder | Why it remained |
|---|---|---|---|---|
| 1 | RV-H1: an older or legacy authenticated kernel becomes the policy root; `minimum_trust_level` read from the kernel judged | CD-1: currency floor; strengthen-only floors for selected keys | R2-H1: 145 floored keys; the kernel supplies every other constitutional leaf | registration covered a selected set; for everything else the kernel was the selector |
| 2 | R2-H1 | CD2-1: total classification; floors, content registration or explicit non-security class for every leaf | RV3-H1: kernel precedence is an input to a join under a refusal-only order; deleting the file joins rules to `immutable`; TPS tightening without a gate | the kernel stayed a selector of precedence, and the order that should have neutralised it was unsound |
| 3 | RV3-H1 | CD3-1: precedence only from registrations; required presence; directed join; strength over effective policy | RV4-H3: `pinned`, member and `pinned_file` registrations are **lists** of permitted digests with no release binding; a higher-sequence final restores superseded content | registration defines a **domain**. For orderable leaves the join neutralises the choice; for non-orderable units nothing does. `19` §5.2's `SURFACE_VALUE_UNAVAILABLE` forces owners to keep superseded digests for installed releases, so the domain grows. |

**Invariant never established.** For every constitutional unit without a join, the registration authority must fix exactly
one digest **as a function of the release** that carries it. A release that is not registered, or whose unit differs from
the digest registered for it, is ineligible. The kernel only carries bytes.

## 3. The common pattern, stated as a mechanism

1. **Set membership was used where identity selection was required.** Each correction added a check that the lower-trust
   input belonged to an authority-approved set:
   - floors registered;
   - digests registered;
   - an anchor exists;
   - an attestation exists;
   - the source is attested.

   Each correction was correct. None removed the lower-trust party's choice **within** the set.
2. **Chains were verified from their second link.** The trust-state machine protects every binary after the first; the
   binary chain protects every binary accepted by a trusted `gov`. The first link was delegated to procedure and assumption,
   and procedures are not attacked by the architecture's own oracle.
3. **Components were bound by equality, not selected.** `release.source` bound `build_inputs_digest` by equality across
   statements. Equality checks do not say who chose the value.
4. **No per-decision register of selectors existed.** The reviews state an invariant per class. The architecture has no
   table that lists, for each decision, which inputs may choose and which may only refuse. So neither an architect nor a
   conformance oracle could find the next input in the same position. The next revision therefore closed the demonstrated
   instance, and a review found the remainder one input over.

The MEDIUM findings show the same pattern (E1 rows `r4-07`…`r4-11`, `r3-06`, `r3-07`, `r2-06`, `r2-07`):
- RV4-M3: the witness service's input is selected by the Git host.
- RV4-M5: migration content is selected by `release-final` on machines without a record.
- RV4-L10: owner-contract set members are selected by per-path pins.
- RV4-M2: later-executed code is selected by a `gov`-run repository command.
- RV4-M1: `COMPLETE` is decided by the presence of named entries while foreign entries are ignored.

## 4. Testing the review's diagnosis (not assumed)

The r4 synthesis states one unestablished invariant per class (`00-REVIEW-REPORT.md` §9, `11-CORRECTION-DELTA.md`). Each was
tested for necessity and sufficiency.

### 4.1 BC4-1: "each TCB fact is established by independent parties at a verifier-checked threshold at least as strong as the binary's authority"

- **Necessary.** Yes. E2 reproduces reviewer B's minimal sets for revision 4 with an independent encoding: `{ba, pipeline}`
  for malicious bytes under S0, S1, S2; `{pipeline, va}` for malicious source under S0 with the REJECTED verdict not held.
- **Not sufficient as stated.** The literal closure CD4-1 offers ("RID": build-attestation threshold 2 with two rebuilders,
  and verification threshold 2 or root-registered sources) still accepts malicious binaries:
  - **Named malicious build inputs.** `{pipeline}` alone, zero keys, under S1 and S2, when the verifier does not establish
    the legitimacy of the inputs digest. The r4 text gives no check that does (`05` §7 rule 3 reproduces the kernel payload,
    which a toolchain does not change). With the verifier checking inputs: S1 refuses; S2 needs `{pipeline, rf, va, va2}`.
  - **Poisoned input mirror.** `{input_mirror}` alone, zero keys, when rebuilders fetch the toolchain from the source the
    release CI names; refused when inputs are fetched by digest.
  - **Custody.** "Independent parties" is not verifier-checkable. What a verifier can check is the number of distinct keys of
    a purpose that shares no key with any other purpose. Custody independence is an assumption under every design.
- **Correction to the diagnosis.** The selector of the build inputs must be the registration authority. Reproducers must
  obtain every input by digest. Reproductions must reach the publisher outside the pipeline: E2 shows that if they travel
  through it, the minimum falls to `{pipeline, rep×2}`.

### 4.2 BC4-2: "every TCB acceptance applies the same anchored, negative-set-checked, currency-proven decision over externally measured digests; no TA-5 ceremony before acceptance"

- **Necessary.** Yes. E3 executes revision 4's path (b) on the revoked binary (FB1) and on the remediated binary with root v1
  metadata (FB2): both `PASS (A2-A6)`. Path (c) passes the planted binary built from a moved tag.
- **Not sufficient as stated.** It has three gaps:
  - **Execution binding.** It speaks of the digest accepted, not the bytes that run. E3 N-FB8: after a correct acceptance
    and install into a location the account owns, a same-uid replacement succeeds and nothing in the acceptance detects it.
    The acceptance invariant must bind the install location (or state that residual as an owner choice, `03` OC-4).
  - **Executor authenticity.** The independent executor is itself obtained over the transport; its authenticity is a
    TA-5-class assumption that must be stated (E3 N-FB7).
  - **Channel currency.** A fingerprint typed from a stale channel page selects stale state (E3 N-FB1: a binary revoked later
    is accepted). This is TA-5's residual and needs a label and a bound.

### 4.3 BC4-3: "a registration fixes, for each release sequence, the effective value of every unit; superseded content is effective later only through a gated reduction"

- **Necessary.** Yes. E0 re-executes B's part P and D-A02 byte-identically: revision 4 exits 0 for every mixed release, and on
  the real 4.1.5 consumer the `ASIA…` key file is indexed and retrievable.
- **The permitted "sequence range" reading is not sufficient.** CD4-3 (1) allows binding "to release identity or a sequence
  range". With open-ended ranges (E4, the pack checker unmodified):
  - **Superseded content in a gap.** 4.1.6 content under a forged sequence between 4.1.6 and 4.1.7 is eligible.
  - **Sequence inflation.** Current content under sequence 10^9 is eligible; installed once, it poisons E10's per-project
    high-water.
  - **Stale Trust Policy.** A machine holding only the older Trust Policy accepts 4.1.6 content at 4.1.8-x's sequence.

  Only exact per-release registration ("closed") matches all six expectations (`lookup_mutants`: closed 6/6; open, union and
  latest each fail at least one).
- **Presence is registration too.** Under the global registration of revision 4 (the "union" rule), registering a new
  required member for 4.1.7 makes the legitimate installed 4.1.6 kernel `surface_required_missing` (exit 2). That is part of
  why retention was forced. Release-scoped registration scopes presence as well.

### 4.4 Conclusion on the diagnosis

The three stated invariants are necessary, and each names the right fact. Each is scoped to its instance and misses one
input in the same position:
- **BC4-1:** build inputs;
- **BC4-2:** the bytes that run;
- **BC4-3:** sequences between and beyond registrations.

SEL-1 (§5) states the property across decisions, so a missed input shows up as an unclassified or under-authorised selector,
not as the next review's finding.

## 5. The invariant never established: SEL-1 (selection authority)

For every trust decision *D* that confers authority α(*D*) and currency κ(*D*), every input to *D* is exactly one of:

| Role | Definition | May be supplied by |
|---|---|---|
| **selector** | its value determines which of several authentic candidates becomes the effective fact: binary, source, build inputs, state, constitutional content, anchor, installation state | only an input whose authority ≥ α(*D*) and whose currency ≥ κ(*D*) |
| **restrictor** | it can only refuse, or strengthen through a monotone join | any authenticated input |
| **carrier** | it transports bytes whose identity a selector already fixed | anything |

A decision whose selector cannot be supplied at the required authority and currency **fails closed**, unless the
architecture states the shortfall as a residual with an exact bound, a label on every surface and a test. RS-1 core and
OP-7 (d) are residuals of that kind.

**Authority** (highest first):
1. the root threshold;
2. a quorum of at least two distinct keys of one purpose that shares no key with any other purpose; or local machine
   authority (a human typing from an independent channel, a protected operator pin, a local confirmation);
3. one key of one purpose;
4. the repository writer, project configuration or governed account;
5. transport, unauthenticated input, or the artefact under judgement.

**Currency:** established now (typed in the gate) > within a stated window (P1 pin, P3 witnesses) > as of a past anchor or
compiled state > none.

**Consequences for what a verifier must hold (lens A):**

| Question | Answer under SEL-1 |
|---|---|
| What must be compiled in | the algorithms (decision rules, schemas, selector register, purpose table), the lineage id, and the root chain and embedded kernel as a **safety floor**. Nothing compiled is ever a selector of a current fact. |
| What may be fetched | every statement, binary and bundle, as carriers |
| Which facts can be current at all | only those selected by (i) a value typed now from an independent channel (P2), (ii) a protected pin within its window (P1, TA-7), or (iii) witnesses at the C3 threshold within their window (P3, TA-7) |
| What a first machine can prove | a current, negative-set-checked TCB acceptance from one typed fingerprint and a self-measured digest; nothing current without the typed value |
| What a clean CI runner can prove | what its image's protected pin selects, stale by at most the pin's window; its binary is the one accepted when the image was built, re-accepted at least every `pin_max_validity_days` |
| What a long-offline machine can prove | its anchored prefix only (RS-1); C3 and binary upgrades need a new typed fingerprint and the statements it names |
| Which inputs can be removed from each decision | `release-final` from constitutional content and from source; custodial re-check signatures from binary acceptance; the verification key from source selection; the pipeline from build-input selection; the candidate from its own acceptance and from TA-5 ceremonies; the compiled T0 and the clock from first acceptance |

## 6. Limits of this analysis

- **E1 is design-encoded.** The row classification is this specialist's. Its value is completeness and specificity against
  the reviews' own adjudications, not an independent execution. Each row cites the file holding the decision and the finding.
- **E2 is symbolic.** Honest actors act only on the checks their design states; readings of r4 that the text leaves open are
  named in the output and evaluated both ways.
- **E3 uses a toy lineage with real Ed25519.** No RoT-1 binary exists.
- **E4 uses the pack's checker unmodified**, with only the registration function projected into its inventory, and the real
  4.1.5 binary as the consumer, as reviewer B and the architect did.
