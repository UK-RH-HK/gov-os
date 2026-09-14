# Synthesis of the root-cause specialist alternatives before RoT-1 revision 5

| | |
|---|---|
| Run | AR-0011, role `rot-synthesis-architect`, handoff HO-0011 |
| Inputs judged | specialist A (`afda663`, AR-0009, "Selection-Authority Model"); specialist B (`ed07926`, AR-0010, "fact-derivation architecture"); revision 4 (`bca05a7`); review r4 (`97a5545`, with B `152e68e`, C `c6b8ba9`); reviews r3, r2, r1 |
| Output | RoT-1 revision 5 in `release/root-of-trust/4.1.6/`; D-0008 and ARCH-0002 PROPOSED revision 5 (not active, not approved) |
| Date | 2026-09-14 |

## 0. Independence and method

- **Authored before by this session:** nothing (no revision, review or specialist proposal).
- **Read under `release/orchestration/`:** HO-0011, HO-0001 and `AGENT_RUNS/README.md` only. The host-supplied auto-memory
  index (one-line summaries of earlier runs) was present in context; no memory file was opened and nothing here rests on it.
- **Specialist claims were treated as claims.** §5 lists what AR-0011 re-ran, what it confirmed, and what it did not re-run.
- **Two scoped helper sessions** ran under AR-0011's instructions and wrote only `evidence/r5/ST5-*` (legacy containment)
  and `evidence/r5/FA5-*`, `SRC5-*`, `gov_admit_reference.py` (first admission). AR-0011 specified the predicates they
  encoded, verified their outputs, and corrected one harness gap (the FA5 install mutant) before recording results.

## 1. The common root cause

| | Specialist A | Specialist B | Accepted |
|---|---|---|---|
| Lens | the verifier's minimal trusted inputs | release, build and custody supply chain | both |
| Diagnosis | set membership was checked where **identity selection** was required: a lower-trust party chose the member (SEL-1) | trust strength was attached to **artefacts, not facts**: pass-through signatures, selection from authorised sets and evaluators inside the object added strength they did not have (derivation floor) | the same property stated at two granularities |
| Mechanical form | compiled selector register; mutant per selector | Fact Threshold Check on root versions; derivation calculator over the release process; single-valued lint | all four |

**Accepted root cause.** No rule classified, per trust decision, which inputs may select the effective fact and at what
authority and currency, and no mechanism computed the minimum strength of that fact. Revision 4's own diagnosis was correct
per instance but never became a rule, so each correction moved the lower-trust selector one input away.

**Rule adopted:** FD-1 (`29` §2) — roles (selector, restrictor, carrier); selector authority and currency at least those
the decision confers; signatures count only for facts their signers established first-hand; the artefact judged never
selects or evaluates itself; shortfall fails closed or is a stated, labelled, tested residual; minima computed (FD-2, FD-3).
From A: the role vocabulary, authority and currency ranks, compiled decision register (R-SEL-1…4). From B: the
first-hand/pass-through distinction, the Fact Threshold Check, the derivation calculator as the source of every minimum-set
statement.

## 2. BC4-1 — independent decisions for the TCB (RV4-H1)

**Root cause accepted.** Every fact that makes a binary the TCB had a selector below the authority the TCB carries: bytes by
one `build-attestation` key plus pipeline (custodians re-checked that an attestation existed), source by one
`verification-attestation` key, and build inputs by the release process. Revision 4 counted statements per purpose.

**Positions.**

| Question | Specialist A | Specialist B | Revision 5 | Why |
|---|---|---|---|---|
| Who selects source? | registration authority (root threshold or delegated quorum ≥ 2) | L1: root-threshold admission statement over two first-hand verification records; L2: two verification attestations counted by machines | **registration authority**, over OP-8 first-hand verification records (A's selector, B's first-hand records) | L2 leaves inputs and constitutional content selected by the pipeline and needs open registration to avoid per-release ceremonies; OP-2 (b) gives the same ceremony relief without a lower selector |
| Who selects build inputs? | registration, after the ceremony verifies toolchain checksums, lockfile and image (R-REG-3) | part of source identity (build profile digest); residual TB-2′ | **input manifest registered after upstream checksum checks by ceremony and verifiers**; normative remapping profile (B) | A found the named-inputs selector; B found the reproducibility precondition |
| Source identity | commit + source digest | commit + **canonical content digest** + build profile | **canonical content digest** (B) + input manifest (A) | SRC5: `git archive` digest binds the commit id and is time-stamped for trees |
| Who establishes bytes? | ≥ 2 first-person reproductions, submitted outside the pipeline, conflict refuses | ≥ 2 build attestations by distinct keys; publisher refuses two quorum digests | **≥ 2 one-signature reproductions confirmed first-hand to the publisher; conflict refuses; one published digest per release and target** | CS5 control: through the pipeline the minimum falls to {pipeline, 2 keys}; A's "outside the pipeline" is made precise as first-hand confirmation |
| Pass-through signers | withdrawn (`release-artifact`, `build-attestation`) | `release-artifact` retired; `build-attestation` becomes the quorum | `release-artifact` and `build-attestation` withdrawn; new `reproducer` purpose | a clean purpose avoids re-using a name whose revision-4 meaning was single-key |
| `release-final` | withdrawn as authority | kept for authenticity; not a TCB input | **restrictor**: the registered final must verify; selects nothing | defence in depth without selection; CS5 INV-RF |
| Rotation | — | re-attestation requires re-reproduction (N19) | reproductions never re-signed (`05` §8) | re-signing launders a stolen key's statements |
| Verification count | one record (TA-11) | two independent verifications as minimum | **OP-8** with calculator consequences | under registration, stolen verification keys yield nothing (INV-SRC-KEYS); the count bounds process compromise (TB-4′), a genuine trade-off |
| Root co-signers reproduce | — | OC-2 (d) | **OP-9 (d)**, with the custodians' own reproduction required | CS5 control: a pass-through co-signature lowers the minimum (the D-A07 shape) |

**Rejected alternatives.** CD4-1's literal "build-attestation threshold 2 with verification threshold 2" (both specialists
showed it leaves named inputs and mirrors as selectors); B's L2; revision 4's OP-2 (S0)–(S3) and `release-artifact`
(i)–(iii) (each keeps a selector below authority).

**Evidence relied on (re-run by AR-0011).** CS5 (408 configurations, 21/21 self-checks, 1,752 invariant checks with 0
failures, 138,042 monotonicity checks with 0 violations; controls); P4r5 VA5 rows; DA03r5; SRC5; revision-4 controls at base.

**Owner trade-offs (not decided):** OP-2 registration authority; OP-8 verification records; OP-9 reproducer set and
registered digests; OP-10 common-mode toolchain; OP-4 remaining custody.

## 3. BC4-2 — anchored, non-circular first TCB acceptance (RV4-H2)

**Root cause accepted.** Anchors, negatives and currency existed only inside `gov`; the base case of the binary chain was a
weaker, documentation-level predicate, evaluated partly by the candidate, and ceremonies ran on the unaccepted binary.

**Positions.**

| Question | Specialist A | Specialist B | Revision 5 | Why |
|---|---|---|---|---|
| Evaluator | `gov-accept`, different language and code base | `gov-admit`, root-registered digest; shared AP spec | **`gov-admit`**, registered and reproduced like any release artefact; form is **OP-12** | the evaluator's authenticity comes from registration, reproduction and digest comparison; code-base independence is a conformance cost trade-off |
| Selector of state | fingerprint typed from the channel (P2) | fingerprints from both channels | **typed fingerprint; one or two agreeing channels is OP-13** | availability versus RS-B1 |
| Bytes | read once, never executed; install and re-read | install from the measured buffer (F4 T) | **install from the buffer, re-read and compare** | FA5 INS1: re-reading the path installs swapped bytes |
| Evaluator-inside-object for ceremonies | R-CER-1; record is guard only | genuine-binary rule: refuse C1–C3 and ceremonies without a protected record | **GB-1…GB-5**: C0 only without a record; C3 and ceremonies need the TCB-location predicate (CR4-B-01 (b)) | binds genuine-but-revoked binaries run outside the procedure (B); A's install-location option is not an option because CR4-B-01 (b) is carried |
| Pre-admission account state | — | fresh verifier trust store | **adopted** (R-ADM-8) | AD-2 |
| Self-restriction of a revoked genuine binary | OC-6 (C0 or C0–C2) | refuse C1–C3 when own digest is revoked | **OP-15** | incident continuity versus defect exposure |
| CI images | image build = first acceptance; rebuild at pin cadence | image record with validity | **both**: root-owned record with `valid_until` ≤ pin validity | bounded exposure |
| Workstation record validity | — | OC-5 | **OP-14** | availability versus RS-1 core |
| Currency on pinned machines | retained | retained | **CR4-B-07 option 1**: a P1 proof covers only the TSS it names | FD-1: the trust-state key must not select C3 state; CS5 control shows option 2 admits {reproducer keys, trust-state key, transport} |

**Rejected alternatives.** Revision 4's paths (b) and (c) (FA5 controls pass on revoked, remediated and planted binaries);
"TOFU for production" (incompatible with fingerprint selection); A's OC-4 (b)/(c) (C3 from user-writable installs;
contradicts CR4-B-01 (b)); B's OC-5 (c) (no validity on image records).

**Evidence relied on (re-run or verified by AR-0011).** FA5 (45/45, 17/17, 26/27; deterministic), P4r5 running-mode rows,
revision-4 controls at base.

**Owner trade-offs (not decided):** OP-6, OP-12, OP-13, OP-14, OP-15, OP-7.

## 4. BC4-3 — release-scoped registration of constitutional content (RV4-H3)

**Root cause accepted.** Registration defined a **domain** of permitted digests per key; for non-orderable units no join
neutralised the choice; retention of superseded digests (forced by fallback and release-global presence) let a threshold-1
final select superseded content.

**Positions.**

| Question | Specialist A | Specialist B | Revision 5 | Why |
|---|---|---|---|---|
| Form | exact per-release registration ("closed"), in the release registration | E1 admission by final digest; E2-closed; E2-open (owner choice) | **exact per-release registration by final digest and kernel tree digest** (= A closed = B E1) | E2-closed per sequence is equivalent; E2-open lets `release-final` select sequence position (gap, inflation, stale policy) |
| Presence | release-scoped (N24) | — | **release-scoped** | REG5 first run: release-global presence made the legitimate older release exit 2 |
| Rewrite | invalid (append-only) | computed reduction | **invalid** | a registered release's meaning never changes; mistakes are revoked and re-registered |
| Reversion | computed reduction | computed reduction | **computed reduction**, plus **unit removal** and **member-set narrowing** | found while scoping presence (a later registration may otherwise drop a control) |
| Owner-domain sets | binding groups | binding groups; refuse on conflicting pins | **binding groups; exact set match only** | RV4-L10 |
| Additive collections | admitted only where the consumer is monotone | — | additions registered per release; project-layer additions follow the directed join | the registration fixes kernel additions |

**Rejected alternatives.** Sequence ranges and "latest registered" (CD4-3 (1) permitted them; REG5 `ranges_excluded`);
B's E2-open.

**Evidence relied on (re-run by AR-0011).** REG5 (executed on real 4.1.5, all 10 verdicts true); CSI5 self-test 71/71 with
the 56 revision-4 cases unchanged; P1r4 byte-identical; review-r3 probe copies identical.

**Owner trade-offs (not decided):** OP-11 retention; OP-2 (who registers).

## 5. Specialist claims: what AR-0011 re-ran

| Claim | Source | Re-run | Result |
|---|---|---|---|
| Revision 4 admits {one build-attestation key, pipeline} and {verification key, pipeline} | A E2, B F1 (= reviewer B) | reviewer B's model at base | confirmed (byte-identical) |
| Path (b) accepts revoked and remediated binaries; path (c) accepts a planted binary and executes it | A E3, B F2/F4 | FA5 controls | confirmed |
| Part P and D-A02 retention attacks exist; exact registration refuses them and the secret stays excluded | A E4, B F3 | REG5 (own checker implementation, real 4.1.5) | confirmed |
| Release-global presence breaks a legitimate older release | A N24 | REG5 first run, selftest S69 | confirmed |
| Reproductions through the pipeline lower the minimum | A N04 | CS5 control | confirmed |
| Inputs from a CI-named mirror are a zero-key selector | A N01 | CS5 control | confirmed (under the mirror-fetch reading) |
| `runtime/build.rs` falls back to `git rev-parse HEAD` | A N25 | read line 73 | confirmed; IR-REP-1 |
| `git archive` digests bind the commit and time-stamp trees | B F4, N09 | SRC5 | confirmed |
| Measure-then-swap installs swapped bytes when re-reading the path | B N10 | FA5 INS1 | confirmed |
| Two verification processes plus pipeline under L1 | B F1 N03 | CS5 G_SRC (OP-8 = 2) | confirmed |
| Path-remapped builds are bit-identical | B F5 | **not re-run** | carried as IR-REP-2 with RT-133 |
| Open ranges admit gap, inflation, stale policy | A E4 | **not re-run** (exact lookup refusal re-run) | not relied on beyond rejecting E2-open |
| Rotation re-signing launders forged attestations | B N19 | design reading | adopted as R-REP-7 |
| SEL-1 flags every HIGH row and no sound mechanism | A E1 | **not re-run** (design-encoded) | not relied on |
| B's F2 18/18 mutants | B F2 | **not re-run** | superseded by FA5 |

## 6. BC4-4 and the owner-option set

Revision 4's OP-1…OP-7, A's OC-1…OC-8 and B's OC-1…OC-5 are reconciled into **OP-1…OP-15** (`21` §0 gives the mapping and
the items that are architecture minima, each with its reason). Consequences are taken from CS5 (capability sets), REG5,
FA5 and P4r5. No option is decided, and revision 5 withdraws revision 4's labelled proposals, so no default exists.

| ID | Question |
|---|---|
| OP-1 | How many root keys, what threshold, which custodians? |
| OP-2 | Does the root threshold or a delegated quorum register each release? |
| OP-3 | Must every adoption, update and rollback pass a local trust gate (mode A), or may certified updates skip it (mode B)? |
| OP-4 | Separate candidate key, and how are the remaining purposes held and shared? |
| OP-5 | At what age does the metadata warning appear? |
| OP-6 | Is lineage confirmed once per verifier trust store or on every `init`? |
| OP-7 | What may a machine without a current proof do (anchored only, maximum age, witnesses, compiled epoch), with which parameters? |
| OP-8 | How many independent verification records must a registration list? |
| OP-9 | How many reproducers and what quorum, and does the registration also name binary digests after the custodians' own reproduction? |
| OP-10 | Accept the upstream toolchain as common mode, add a diverse reproducer, or build the toolchain? |
| OP-11 | Do releases whose non-orderable content was superseded stay eligible, get retired on security-relevant change, or get a grace period? |
| OP-12 | Is the admitter a separate program, an auditable script, or a helper machine? |
| OP-13 | Does first admission need one channel or two agreeing channels? |
| OP-14 | Do workstation admission records expire? |
| OP-15 | May a genuine binary that holds its own revocation run C0 only, or C0–C2? |
