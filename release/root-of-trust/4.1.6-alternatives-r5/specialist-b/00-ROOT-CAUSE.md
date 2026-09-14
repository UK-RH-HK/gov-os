# 00 — Root cause of the persistent root-of-trust classes (specialist B, AR-0010)

> **Proposal input only.** Written for the revision-5 synthesis architect. It edits nothing, approves nothing, and does
> not change the status of D-0008 or ARCH-0002 (PROPOSED, `PROVISIONAL`, `in_effect: false`).

| | |
|---|---|
| Run | AR-0010, role `rot-specialist-architect` (specialist B), handoff `HO-0010` |
| Base | `6ea45a5` on `phase1/rot1-r5-specialist-b` |
| Latest rejected revision | RoT-1 revision 4, `bca05a7`; review r4 `97a5545` (synthesis governs) |
| Starting lens | release, build and custody supply chain: who establishes each fact, at what threshold, how facts compose, and what a verifier can check without trusting the thing accepted |
| Evidence | `evidence/` (F0–F5); classes in `02-FALSIFICATION.md` |

## 1. The three persistent classes

| Class | Consolidated finding | Lower-trust input | Higher-trust fact obtained |
|---|---|---|---|
| **BC4-1** independent TCB decisions | RV4-H1 | one threshold-1 `build-attestation` key (or `verification-attestation` key) plus release-pipeline input | an accepted production binary |
| **BC4-2** anchored, non-circular first TCB acceptance | RV4-H2 | a transport- or source-host-selected revoked, remediated or self-reporting binary | the first trusted binary on a machine |
| **BC4-3** release-scoped registration of constitutional content | RV4-H3 | a threshold-1 final choosing among registered non-orderable digests | the effective constitutional content of a later release |
| BC4-4 owner-option statements | review r4 §7 | follows from BC4-1…BC4-3 | — |

## 2. Chains across revisions

Sources: the four reviews' `10` and `11` files, revision 4's `28`, `25`, `23`, `24`, `05`, `06`. "Why it remained" is this
analysis.

### 2.1 BC4-1 — who establishes that a binary is the TCB

| Rev. | Finding | Correction made | Remainder | Why it remained |
|---|---|---|---|---|
| 1 (`676dfce`) | **RV-H4**: the legacy-identity statement, signed by the threshold-1 certification role, made an installed kernel authentic | CD-3: only the release role or the root threshold confers kernel authenticity; legacy identities compiled | binaries still authenticated by the release purpose | the fix named *which purpose* may sign, not *which fact* the signature establishes |
| 2 (`d37b05c`) | **R2-H3**: the TCB authenticated by one threshold-1 `release-final` artefact statement with no T0 binding | revision 3: `release-artifact` threshold 2, an independent build attestation, a TSS reference, the Trust Base Manifest | **RV3-H3**: every signer checked the bytes against the `release_commit` a threshold-1 final chose | signers were multiplied, but all of them answered one question (bytes = build of the named commit); nobody established the other fact (the named commit is verified source) |
| 3 (`ca77a43`) | **RV3-H3** | revision 4: V8 source equality; source taken from an ACCEPTED verification attestation; custodial pre-check stages | **RV4-H1**: the faithful-build fact rests on one `build-attestation` key, source legitimacy on one `verification-attestation` key; custodians pass the pipeline's bytes through | see below |

**Why it remained through revision 4.**
1. **Statements were counted, not establishments.** `verify-artifact` is a conjunction of statement checks, each with
   its purpose threshold. The two `release-artifact` custodians sign a threshold-2 statement whose only first-hand content
   is "an attestation exists" (`25` §9, `05` §7 rule 6). An honest pass-through signer converts a threshold-1 fact into a
   threshold-2 statement. That is D-0007's forbidden derivation, performed by honest parties.
2. **The analysis was manual and omitted an input.** `25` §7 enumerated "routes" by hand. Route S counted pipeline
   input; route B did not ("no pipeline control needed"). Reviewer B's enumeration over every capability subset found
   `{ba, pipeline}`. This run re-executes it (F1, `revision_4_reviewer_B_model`): `{ba, pipeline}` under OP-2 (S0) and
   (S1); `{ba, ba2, pipeline}` with two rebuilders; `{va, pipeline}` under (S0) when the REJECTED verdict does not reach
   the signers.
3. **The oracle encoded the defect.** VA4's "route B" row expects the attack as `ACCEPTED` (review r4 RV4-H1 (5)), so no
   test could fail.

**Invariant never established.** *The strength of a fact a decision consumes is the minimum, over every input that can
change or select that fact, of that input's establishment strength. A signature adds strength only for a fact its
signer established first-hand, and the resulting minimum must be computed mechanically, not by route enumeration.*

### 2.2 BC4-2 — the base case of TCB acceptance

| Rev. | Finding | Correction made | Remainder | Why it remained |
|---|---|---|---|---|
| 1 | **RV-H2**: lifecycle facts not replay- or omission-safe; the supplier chose which authentic statements were seen | monotonic retained state; compiled T0 | **R2-H2**: on a stateless verifier the repository writer chose currency | knowledge was made monotonic *on a machine that already has state* |
| 2 | **R2-H2** | revision 3: anchors, a freshness axis, C3 needs an anchor | **RV3-H2**: anchors satisfied by sequence number; pins without currency; threshold-1 witness; RV3-D-A15 re-accepted a revoked **binary** on pinned CI | anchors were evaluated over a supplier-chosen value |
| 3 | **RV3-H2** | revision 4: inclusion anchors, pin validity, currency proofs, a separate witness purpose | **RV4-H2**: the first binary on a machine is accepted outside anchors, negatives and currency (independent tooling checks A2–A6; build-from-source compares values the candidate prints; Phase 4 verifies a binary with itself; first-install ceremonies run on the unaccepted binary) | see below |

**Why it remained through revision 4.**
1. **The acceptance predicate lived inside the TCB.** Anchors, the negative set and currency are implemented only in
   `gov`. Any evaluator other than `gov` was specified ad hoc (`06` §2 step 6 (b), (c)) and as a subset.
2. **The chain was defined inductively with a weaker base case.** Binary N verifies binary N+1 under A1–A10 (`25` §6).
   The base case was a different predicate: "tooling verifying A2–A6" or "compare `gov version --trust`". An inductive
   argument whose base case does not satisfy the inductive predicate proves nothing about the machine.
3. **The base case was out of scope for three reviews.** Review r3 accepted TB-1 ("a user who runs an unverified binary
   is outside the chain"); revisions 3 and 4 put all currency work into machines that already run `gov`.

**Invariant never established.** *Every TCB acceptance, the first on a machine included, is the same predicate,
evaluated by code other than the candidate over bytes that code measured, and the bytes it installs are the bytes it
measured. Nothing evaluated by an unaccepted binary establishes a trust fact.*

### 2.3 BC4-3 — registration of non-orderable constitutional content

| Rev. | Finding | Correction made | Remainder | Why it remained |
|---|---|---|---|---|
| 1 | **RV-H1**: an older authenticated kernel became the policy root; floors read from the kernel | a currency floor; strengthen-only floors from the embedded kernel | the release chose which keys counted (`28` §2.1) | floors attached to selected keys |
| 2 | **R2-H1**: 145 floor keys registered; 64 of 125 AS-1 leaves unfloored; the rest came from the installed kernel | revision 3: whole payload classified, default deny, per-key precedence join | **RV3-H1**: the precedence order ranked refusal only; a kernel precedence change, a deleted file or a TPS tightening removed project strengthening | the join was evaluated over the kernel's own precedence choice |
| 3 | **RV3-H1** | revision 4: registration-only precedence, required presence, directed join, strength over effective policy | **RV4-H3**: `pinned` leaves, members and `pinned_file` paths register a **list** of digests with no release relation; a threshold-1 final selects a superseded one in a higher sequence | see below |

**Why it remained through revision 4.**
1. **Registration was modelled as a permitted set.** `23` §3.2 registers "permitted digests" per key, and §7 calls
   removing one a strengthening. A set is a selection space; the selector is whoever signs the release.
2. **The ordering machinery cannot see non-orderable content.** Revision 4's detectors (computed reductions, the
   strength vector) work on strength directions; a pinned value has direction `none` (review r4 part P). Precedence was
   fixed by making the kernel's input irrelevant; pinned content kept the kernel's choice.
3. **The defect was latent.** The draft TPS v1 inventory holds 179 pinned digest keys and 97 `pinned_file` paths, each
   with exactly **one** digest (0 multi-digest registrations, counted in this run). The selection space appears only
   with the first fix, when an owner keeps the old digest so installed releases stay eligible (`19` §5.2
   `SURFACE_VALUE_UNAVAILABLE`). CS-2 treated the per-release TPS as ceremony cost only.

**Invariant never established.** *Every registration of non-orderable constitutional content is a function of release
identity: exactly one value per release sequence. No lower threshold selects among registered values, and making
earlier content effective again, or rewriting what a registered sequence means, is a computed reduction.*

## 3. The common root cause

D-0007's rule is: authorisation, registration, verification, approval and provenance facts derive only from a strictly
higher-trust source. Every revision applied that rule **to inputs**: each statement is verified at its purpose and
threshold, each file is classified. No revision applied it **to facts**: the value a decision consumes, whose strength
is the weakest input that can change or select it. Three structural forms recur.

| Form | Where it recurs | What the high-trust artefact does | What the lower party does |
|---|---|---|---|
| **Pass-through** | RV4-H1 (custodians); RV3-H3 (artefact custodians over `release_commit`); D-A07 (root co-signature) | signs at a high threshold | supplies the fact the signature relies on |
| **Selection from an authorised set** | RV4-H3 (registered digests); RV3-H2 (TSS satisfying an anchor); R2-H2 (statements a stateless machine sees); RV4-M3 (the TSS a witness service is fed); RV4-L10 (several valid decision pins for one contract) | authorises every member | chooses which member is in force |
| **Evaluator inside the object** | RV4-H2 (first binary, Phase 4, ceremonies); RV-H3 (verified bytes are not the bytes used) | defines the predicate | runs it, or supplies the bytes after it ran |

**Root cause.** *Trust strength is attached to artefacts rather than derived for facts. No rule states that a fact's
strength is the minimum over its derivation, selections and pass-through signers included, and no mechanism computes
that minimum.* Each revision therefore raised the threshold of the artefact a review had attacked, and the next review
found the weaker input one step away: a new pass-through signer, a new selector or a new evaluator.

Revision 4's own diagnosis (`28` §2: "each revision added conditions downstream of a choice that a lower-trust party
still made") is correct for each instance. It did not generalise into a rule or a computation, so revision 4 re-created
the pattern in the three places above.

## 4. Testing the review's stated invariants

Review r4 (`00` §9, `11` CD4-1…CD4-3) names one unestablished invariant per class. Each was tested against this
analysis and the evidence.

### 4.1 BC4-1: "each TCB fact is established by independent parties at a verifier-checked threshold at least as strong as the binary's authority; downstream signatures count only for facts their signers established"

| Test | Result |
|---|---|
| Necessary? | **Yes.** F1: removing pass-through and counting a quorum of first-hand reproducers takes the minimum from `{ba, pipeline}` to `{ba1, ba2, pipeline}` or `{ba1, ba2, ts}`. |
| Operational? | **No, as stated.** "At least as strong as the authority the binary carries" names no number, and a verifier cannot check who "established" a fact. It becomes checkable only as: (a) compiled per-fact minimum thresholds that a root version must meet (01 M1 FTC), (b) no purpose in the predicate whose definition allows asserting an unestablished fact, and (c) a mechanical minimum-cut computation over the release process for every owner answer (F1). |
| Complete? | **No, in three respects.** (i) **Build inputs.** Two honest rebuilders using the same compromised admitted toolchain produce the same malicious bytes; "faithful build of legitimate source" holds and the binary is malicious. The toolchain must be part of the admitted source identity, and the residual must be stated (01 TB-2′). (ii) **Legitimacy is a process fact.** With verification keys removed from the predicate (root admission), F1 still accepts `{vp1, vp2, pipeline}`: two compromised verification processes. Key thresholds bound key theft, not the verification process. (iii) **Source identity.** F4 shows that `source_tree_digest` as defined (`25` §4: SHA-256 of `git archive` of the commit) binds the commit id through the pax header, is not recomputable by a party holding the same tree under another commit, and that `git archive` of a tree is stamped with the current time. An externally checkable source fact needs a canonical content digest. |

### 4.2 BC4-2: "every TCB acceptance on a machine, first binary included, is anchored, negative-set-checked and currency-proven over externally measured digests; no TA-5 ceremony runs before it"

| Test | Result |
|---|---|
| Necessary? | **Yes.** F2: the admitter refuses the revoked binary (`TRUST_STATE_BELOW_ANCHOR` when stripped, `ARTIFACT_REVOKED` when served), the remediated compromise (three variants), the moved tag and Phase 4 self-evaluation. |
| Internally consistent? | **Not quite.** First acceptance *must* use the channel's state fingerprint, which is the TA-5 input. The invariant has to separate the channel as an **input** (required) from ceremonies **evaluated by the candidate** (forbidden). |
| Complete? | **No, in four respects.** (i) **Measured bytes vs installed bytes.** F4 part T: an evaluator that measures the file and then installs by re-reading the path installs swapped bytes; installing from the measured buffer does not. (ii) **Genuine-but-revoked binaries can enforce admission themselves.** A procedure-only invariant does nothing when the user skips the procedure; a genuine binary that refuses trusted operations without a protected admission record naming its own digest closes the genuine-revoked selection even then (F2). (iii) **Same-user code run before admission** can write the Verifier Trust Store (A3). Ordering alone cannot remove that; a fresh VTS at first admission bounds it. (iv) **CI images** age after acceptance; an image-scoped admission record needs a validity, as pins do. |

### 4.3 BC4-3: "a registration fixes, for each release sequence, the effective value of every constitutional leaf, member and file; content registered only for an earlier sequence is never effective in a later one except through a computed, cumulatively declared, per-project-gated reduction"

| Test | Result |
|---|---|
| Necessary? | **Yes.** F3 (unmodified revision-4 checker on sequence projections): the forged 4.1.8 carrying the superseded `aws-access-key` regex exits 3 at sequence 8 in both range forms. So do D-A02 T1–T4. The installed 4.1.6 stays eligible at sequence 6 (exit 0). On real 4.1.5 the selected content keeps the `ASIA…` key file out of the index. |
| Precise? | **No, as stated.** "For each release sequence" does not say whether a registration may cover sequences not yet released. F3: with an open-ended last range, a machine holding only the older TPS accepts a forged later-sequence final carrying the content that TPS registered (exit 0); with closed ranges it refuses (exit 3), and a genuine later release is also refused until registered (exit 3, then 0 after TPS v3). That is an owner trade-off (`03` OC-3). |
| Complete? | **No, in two respects.** (i) **Two reduction kinds are needed:** reversion to superseded content and retroactive rewrite of an already-registered sequence. F3: the unmodified revision-4 `reductions` tool reports neither (exit 0 on the reversion in open form); the added rule reports both (exit 6, or 0 with `lowering_history`). (ii) **Scope.** The same selection exists for member-id sets and for owner-domain slot sets (RV4-L10: several valid decision pins for one contract). The invariant should cover every registration of non-orderable content, not only kernel leaves and files. |

## 5. Consequence for the next revision

Adding one more condition to each class would repeat the pattern. What removes the classes is:
- a **derivation rule** that governs facts rather than artefacts;
- three structural consequences:
  - no pass-through purposes in the TCB predicate;
  - no set-valued registrations;
  - no evaluator inside the object evaluated;
- **mechanical checks** that compute and enforce the rule.

`01-ALTERNATIVE.md` specifies them. `02-FALSIFICATION.md` attacks them, including where they fail.
