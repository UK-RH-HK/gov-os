# 00 — Independent trust and security review (B) of RoT-1 revision 7, certified profile CP-1

| Field | Value |
|---|---|
| Run | AR-0020, role `rot-reviewer-trust-security` (reviewer B) |
| Handoff | `release/orchestration/phase-1/HANDOFFS/HO-0020-rot-review-r7-b-trust-security.md` |
| Revision reviewed | `d07d200ac08a52c45071d33074e20cc62fbcc26e` (the pack, `spec/`, `docs/` unchanged at base `7e50c6e`) |
| Rejected predecessor | revision 6 `4106885`; consolidated review r6 `ab6b1f8` (synthesis adjudication governs) |
| Branch | `phase1/rot1-r7-review-b` |
| **Verdict** | **`BLOCKING_FINDINGS_PRESENT`** |

This review does not issue the architecture verdict and does not approve D-0008.

## 1. Scope, independence and reads

- **Independence.** This run authored no RoT-1 revision, specialist proposal, prior review, panel review or owner requirement. It
  did not read reviewer C's output, other branches, other worktrees, other scratch directories, transcripts or task-output files.
- **Orchestration files read:** HO-0020, HO-0001, `AGENT_RUNS/README.md` and `GATES/OWNER-DESIGN-REQUIREMENTS-0001.md`
  (verbatim). The `.yaml` index was not opened; only its sha256 was computed. No other orchestration file was opened.
- **Architecture read:**
  - `00`, `05`, `06`, `21`, `22` (§1–§3, §8–§12), `24`, `25`, `27`, `30`, `31`, `32`, `33`, `35` in full or in the sections cited;
  - `01` TA rows, `17` §2–§3, `19` E3, `28` A-R7 list, `12` RT-184…RT-202;
  - `profile/CP-1.yaml`, `DECISION_REGISTER.yaml` (DR-04, DR-13, DR-18, DR-25, DR-36, DR-38…DR-45, PI-01…PI-23), the schemas;
  - D-0007, D-0008, ARCH-0002, `docs/DECISIONS.md` rows;
  - the instruments `gov_admit_reference_r7.py`, `w7world.py`, CS7, CUR7, BA11r7 and PROF7.
- **Prior review read:** review r6 `10-BLOCKING-FINDINGS.md`, `11-CORRECTION-DELTA.md`, `D-synthesis/02-ADJUDICATION.md` and
  `05-RESIDUALS.md`, and `B-trust-security/02-HELDOUT-ATTACKS.md` and `04-CARRIED-REQUIREMENTS.md`.
- Digests of every reviewed file are in `evidence/REVIEWED-CONTENT-DIGESTS.txt`.

## 2. Method

1. **Re-run.** The architect's evidence runner was re-run from a scratch export: 15 revision-7 instruments, 23 retained
   instruments, and the unmodified review r6 (B, D) and r5 probes. The outputs were compared with the committed files
   (`evidence/rerun/`).
2. **Instruments run and read.** The reference executor, CS7, CUR7, BA11r7 and PROF7 were read as claims. PROF7 was re-run on a
   mutated copy.
3. **Held-out attacks.** RV7-B-A01…A13 were authored and executed or computed with the architect's unmodified executor and
   calculator (`02-HELDOUT-ATTACKS.md`).
4. **Conformance.** CP-1 was checked against every owner selection, and every declared residual was judged against the review r6
   criteria (`03-RESIDUALS.md`).

## 3. Findings

| ID | Severity | Title |
|---|---|---|
| **RV7-B-H1** | **HIGH** | A revocation issued by the revocation authority is effective at first contact only if a Trust State lists it; no party establishes that listing, so a revoked binary is admitted without limit in time |
| **RV7-B-H2** | **HIGH** | The C3 currency proof bounds the age of the confirmation or pin, not the age of the Trust State it names: stored or re-stamped state codes make a stale state "published as of now" |
| **RV7-B-M1** | MEDIUM (blocking under §4: not carriable without an architecture text change) | Both source identities reach the operator in one onboarding record; the stated first-contact root models them as two independent atoms and omits the one-input set |
| RV7-B-L1 | LOW | Supplier-class and toolchain-lineage independence is inequality of root-signed free-text provenance strings |
| RV7-B-L2 | LOW | The certified trust-root schema accepts `trust-policy` and `first-contact-authority` at threshold 1 on non-root keys; only the compiled check refuses |
| RV7-B-L3 | LOW | R-FCS-2 (d) is relative to a custodian's own history; a custodian without history publishes a revocation-dropping descendant |
| RV7-B-L4 | LOW | No rule states the Trust State issuance cadence that the 24-hour admission age requires |
| RV7-B-L5 | LOW | Two committed re-run outputs are stale against the committed pack; the committed runner is not self-contained |
| RV7-B-L6 | LOW | No genesis procedure for the source custodians' "own admitted binary" (R-FCS-1) |
| RV7-B-I1 | INFO | OP-8 independence is mechanically distinct key ids, execution ids and report digests only |
| RV7-B-I2 | INFO | ARCH-0002 carries no `human_approved` field |

- **Why CRITICAL is absent.** Machines whose store holds the negative refuse. Running machines that are delivered the revocation
  statement refuse. H2 needs withheld newer states and a stored code.
- **Evidence.** H1 is executed (11 daily states, revocation up to 342 h old, `ACCEPTED`) and computed (`{fcpub}` as written;
  `{2 trust-state keys, fcpub}` under the stricter reading). H2 is executed (C3 `ALLOWED` on a 4-month-old state; CI C3 on a
  6-day-old state) and computed (`{transport, stored_old}` at P2).

## 4. Prior findings and classes

| Item | Status | Evidence |
|---|---|---|
| **BC6-1** first-contact selector authority | **NARROWED** | **Closed instances:** composer (FA7 S2 P, re-run byte-identical ×2: custodians refuse composed or below-threshold FCAs and states; a genuine admitter refuses composed codes); submitter and platform path excluded (PROF7 EX-04, EX-05; FA7 S2 X); printer excluded (EX-24); attacker lineage refused (S2 D); executed minima equal CS7 (S3). **Remainder:** designation as one input (RV7-B-M1); custodian verifier genesis (RV7-B-L6). |
| **BC6-2** first-contact currency | **NARROWED** | **Closed instances:** replayed, stored, media, CI and designated old codes refused by the compiled 24 h age; re-admission applies the stores (CUR7 re-run byte-identical). **New HIGH remainder:** negatives by listing (RV7-B-H1); the running-machine C3 state age (RV7-B-H2). |
| **BC6-3** first-hand environment manifest | **CLOSED** as a class within this review's attacks | ENV7 re-run byte-identical with the real `rustc 1.98.1` (A07a/b/c, A08, A09, T1–T3); CS7 pipeline never minimal. LOW remainder at root threshold: RV7-B-L1. |
| **BC6-4** register over inputs; statements; plan detection | **NARROWED** | C9–C11, DA09r7 (578 fields), DA04r7 15/15, DA06r7 and STATEMENTS-CHECK re-run byte-identical. **Remainder:** listing completeness has no establishing party and no calculator strategy (H1); designation atoms do not match the one-record register row (M1); BA11r7's `sources_latest` assumption (H2); false statements CUR-R1, CP-REVOKED, CP-FC-ROOT, RS-1b, `24` §6, A-R7-08. |
| RV6-H1 | **CLOSED as stated** (composer, designation printer, submitter) | as BC6-1; the designation remainder is RV7-B-M1 |
| RV6-H2 | **CLOSED as stated** (replayed package, media, CI codes, designated old pages, re-admission over a newer store) | CUR7 R, A02, A08, S2; RV6-D-A02 re-run. New instances are H1 and H2. |
| RV6-H3 | **CLOSED** | ENV7; PROF7 EX-21; register PI-07 (no author) |
| RV6-M1 | **CLOSED** | DA06r7; RV6-B-A03 unmodified re-run (S2 now rejects the misrendered set); S1a and S3 |
| RV6-M2 | **NARROWED** | as BC6-4 |
| RV6-M6 (trust parts) | **CLOSED** | ADM7 A07 re-run byte-identical: a planted account record does not suppress the move-aside; R-STORE-2 |
| RV6-L1 | **OPEN** (carried, RT-198) | RV6-B-A10 and RV6-D-A03 re-run byte-identical: an unflagged security-relevant change is still not listed |
| RV6-L2 | **CLOSED** | `05` §1–§2 list the revision-7 payload types and the first-contact codes |
| RV6-L3 | **CLOSED** in specification | R-BENV-8; `accept` counts attestations only when they name the registered environments; RT-200 |
| RV6-L4 | **CLOSED** in specification | R-BENV-9, R-REG-3 (g); RT-186. The analogous custodian-verifier genesis gap is RV7-B-L6. |
| RV6-L5 | **CLOSED** | CUR7 A04 re-run: `BINARY_T0_ROLLBACK` at re-admission (AP-R6) and at use (`gov_run` R-ART-2) |
| RV6-L12 | **CLOSED** by exclusion | one OP-10 × OP-16 combination; DA05r7; PROF7 EX-15, EX-21 |
| RV6-I1 | **OPEN** (INFO, unchanged) | `27` §5: no trust gate depends on the declared role |
| RV6-I2 | **OPEN** (carried, RT-182) | capability-contract phase |
| OT-1 | **real, bounded, genuine owner trade-off; understated** | §7 |
| OT-2 | **real, bounded; not a new owner trade-off** | §7 |

## 5. Conformance with OWNER-DESIGN-REQUIREMENTS-0001

| Owner selection | Result |
|---|---|
| Option C; A, B, D, E, F not supported | conforms (EX-22; D-0008 option texts; no `chosen_option`) |
| OP-1 root 3 keys, 2-of-3, custodial roles | conforms in the compiled check; the schema accepts sub-threshold root-held purposes (RV7-B-L2) |
| OP-2 (b) delegated registration 2-of-3 | conforms (EX-09; `PURPOSE_SHAPE` 3/2; whitelist) |
| OP-3 Mode A | conforms (gating const; decision-pin enum excludes every C3 kind; confirmations required). The currency carried by a C3 confirmation is RV7-B-H2. |
| OP-4 purposes | shapes conform (candidate separate, final ≥ 2, trust state 2-of-3, certification ≥ 2, revocation 2-of-3, retrieval separate, no witness). **Deviation:** the dedicated revocation authority's effect at first contact is subordinate to trust-state listing, which no rule establishes (RV7-B-H1). |
| OP-5 30-day warning, informational | conforms (PROF7 EX-07 compiled check re-run) |
| OP-6 (a) once per verifier trust store | conforms |
| OP-7 (a) 90 d / 7 d / 24 h / expiry C0 / high-water | Anchor validity, expiry to C0 and R-CLK-1 conform (ADM7, BA11r7 re-run); the admission path conforms (FC-9). **Deviation:** production installation, update and rollback on running machines accept a currency proof naming a state of unbounded age, and present it as published as of now (RV7-B-H2). |
| OP-8 = 2 | conforms mechanically; independence rests on custody (RV7-B-I1) |
| OP-9 (b) + (d) | conforms (EX-14; AP-6; BA12r7) |
| OP-10 (b) | conforms as a rule with no fallback (EX-15); not evidenced (OT-2); independence by root-signed strings (RV7-B-L1) |
| OP-11 (b) | conforms (AP-SEC; E3). The minimum advances when a Trust State references the registration, the same listing dependence as H1. |
| OP-12 (a) | conforms (compiled admitter; EX-02, EX-03); custodian verifier genesis unspecified (RV7-B-L6) |
| OP-13 (b) | The mechanism conforms (compiled quorum 2, byte-identical codes, both required; (c), platform root and (d)-only excluded and refused). **Deviation in stated consequence:** one onboarding record designates both sources (RV7-B-M1). Media: OT-1. |
| OP-14 (b) | conforms (records expire; AP-R1…AP-R6; CUR7 A02) |
| OP-15 (a) | conforms (C0-R; ADM7 X15) |
| OP-16 (b) | conforms (derived manifests, pinned keys, two classes); label canonicalisation RV7-B-L1 |
| First-contact composer/signer at root threshold | conforms (R-FCA-1…4, R-FCS-1…3; FA7 S2 P) |
| Build-environment manifest authority | conforms (no author; ≥ 2 environment reproductions and the 2-of-3 registration over the exact `environment_id`; ENV7) |
| Initial certified scope and exclusions (witness, helper machine, script, (c) either, platform root, mode B, clock or grace trust, unanchored mutation) | conforms. PROF7 holds 113/113 checks and 24/24 exclusions (re-run byte-identical); it detects injected witness and channel-quorum schema fields (RV7-B-A08); the schema sweep finds no reachable excluded field (RV7-B-A09). No target is labelled CERTIFIED. |
| D-0008 state | conforms: `status: PROVISIONAL`, `proposal_state: PROPOSED`, `human_approved: false`, `in_effect: false`; D-0007 `ACTIVE`. ARCH-0002 is PROVISIONAL/PROPOSED, `in_effect: false`, with no `human_approved` field (RV7-B-I2). |

## 6. HO-0020 §3 required work

### 6.1 Constitutional surface

- **Checker unchanged.** `constitutional-surface/` did not change between `4106885` and `d07d200`.
- **Self-test and checks re-run:** CSI self-test 78/78; checks exit 0 (framework), 3 (4.1.5) and 2 (4.1.2, 4.1.3, 4.1.4). All
  byte-identical apart from `kernel_dir`.
- **Kernels changing only non-security or registered leaves, unmodified re-runs, byte-identical:**
  - RV5-B-A09: variant and tool-command kernels, unknown key, new file;
  - RV6-B-A10: command contract, tool-permission template granting `SECRET_READ`, taxonomy, unknown key, new file (exit 2);
  - RV5-D-A05 and RV6-D-A03: new constitutional files for Gate W and G0–G6.
- **Result.** Default deny holds. A non-first-hand proposal is refused at registration (exit 3; CON6 byte-identical), so a weaker
  authority, secret, gate, plugin or tool, export, override, install or exception policy is not made effective through a
  registration. RV6-L1 remains carried: an unflagged security-relevant change is not listed per project.
- **Limit.** This review authored no new kernel construction beyond these re-runs.

### 6.2 Freshness bootstrap: machine classes (HO-0001 §3.2) under a repository and transport adversary

CP-1 has one OP-7 answer. Answers (b), (c) and (d) are excluded and refused (PROF7 EX-01, EX-07, EX-08 and EX-12 re-run).

| Machine | What the adversary can make it accept as current (as written) | Evidence |
|---|---|---|
| M1 first install | A state both sources name, at most 24 h old; never an older state (FC-9) and never another lineage or evaluator. **But** a binary revoked by the revocation authority and omitted from those states, for any length of time (H1). Stated residuals: `{win}` ≤ 24 h; `{stored_old, clockback}` without a store. | CUR7, FA7 (re-run); RV7-B-A01 |
| M2 clean CI runner | Image build as M1, including H1. Jobs run C1–C2 at the pin state for ≤ 7 days. **C3 on a state up to 7 days old** through a re-stamped pin (H2). A pin writable by the job's uid is ignored. | BA11r7, ADM7 (re-run); RV7-B-A02 |
| M3 restored from backup (anchor 400 days) | C0 until re-anchored. Re-anchoring with stored codes gives C3 on the stale effective state (H2). Clock set back with every later statement withheld: RS-2b. | BA11r7; RV7-B-A02 |
| M4 old epoch (20 days) | C1–C2 at the anchored chain (RS-1). C3 only with codes naming the effective state: stored codes suffice (H2). | BA11r7; RV7-B-A02 part C |
| M5 no epoch | C0 only | BA11r7 |
| M6 two machines at different epochs | each its own anchor; a lock hint is a warning; no cross-authorisation (TG-1) | BA11r7 |
| M7 offline 1095 days | C0; re-anchoring as M3 | BA11r7 |
| Re-admission | never below held state, negatives, security minimum or accepted TBM (AP-R1…AP-R6). Over a store that predates an omitted revocation: H1. | CUR7 A02, A04; RV7-B-A01 |
| Air-gapped | media at most 24 h old (OT-1), plus H1 | CUR7 A08 |

A machine that never received newer metadata is not claimed to know it, and no surface prints `current` (BA11r7 re-run: 0 rows).
The claim that a stale state is never presented as the state published as of now fails for C3 (H2).

### 6.3 Binary and TCB

- **Key subsets below threshold.** BA12r7 re-run byte-identical: 0 accepts with ≤ 1 key; 0 with release keys, trust-state keys
  and infrastructure only. RV6-B-A12 re-run byte-identical.
- **First-contact authority below root threshold.** An FCA signed by one root key or by two trust-state keys is refused
  (`FIRST_CONTACT_AUTHORITY_UNVERIFIED`; FA7 S2 P, PROF7 EX-23).
- **OP-4 variants refused:** release-final threshold 1, a candidate key shared with final, registration on root keys (PROF7 EX-09,
  EX-10).
- **Older binary.** `BINARY_T0_ROLLBACK` at re-admission and at use; the release security minimum applies (FA7 R11; CUR7 A04).
- **Malicious bytes.** No accept below CP-BYTES (`{2 registration custodians, 3 reproducer processes}`, or key theft at every
  threshold with publication).
- **Revoked binary.** Accepted below the declared authority when the revocation is omitted from states (H1).
- **Chain.** Non-circular for machines (`25` §6): the evaluator is selected by the FCA digest the sources show; it never evaluates
  itself; the FCA requires the admitter's registration, reproduction and two records. The genesis of the source custodians' own
  verifier is unspecified (L6).

## 7. Owner trade-offs OT-1 and OT-2

**OT-1 (offline media versus the 24-hour bound).**
- **Real.** Media older than 24 h are refused (CUR7 A08 `media_prepared_at_T7_used_now` → `FIRST_CONTACT_STATE_TOO_OLD`; the
  within-ceiling control is accepted; re-run byte-identical).
- **Correctly bounded.** The refusal is compiled and fails closed, and the stricter reading is applied pending a decision.
- **A genuine owner trade-off.** OP-13 (b) names an offline media channel and OP-7 (a) names 24 h; every resolution changes an
  owner parameter's effect for a path (OT-1b) or gives up air-gapped C1–C3 (OT-1c).
- **Understated in two ways:**
  1. The same bound makes daily Trust State issuance (2-of-3 hardware-backed trust-state custody) and daily first-hand publication
     by both source custodians a precondition of *every* first admission, CI image build and re-admission, not only media. No rule
     states that cadence (RV7-B-L4).
  2. OT-1's consequences are computed as "only the bound of `win`" changes. RV7-B-H1 shows `win` is not bounded by the owner
     parameter while listing delay is unbounded, so OT-1b's window would be added to an unbounded delay.

**OT-2 (OP-10 (b) not evidenced for the current compiler).**
- **Real.** No independently bootstrapped lineage of `rustc 1.98.1` is evidenced; ENV7 §9 states that its lineages are distinct
  provenance records over one `rustc 1.98.1`.
- **Correctly bounded.** CC-3 is unmet, so both initial targets are NOT CERTIFIED, first contact refuses an uncertified target,
  and there is no fallback (EX-15; PROF7 re-run).
- **Not a genuinely new owner trade-off.** The owner text already decides the consequence ("that target is not certified rather
  than silently falling back to OP-10(a)").
  - OT-2a restates that decision.
  - OT-2b (a compiler version constraint) is an engineering choice within OP-10 (b).
  - OT-2c reopens an owner parameter without a new trade-off.
- **Consequence to state.** CP-1 certifies no target today, so CC-1…CC-5 and the OP-10 (b) mechanism are exercised only in
  models.

## 8. Probe reproduction

| Set | Result |
|---|---|
| Revision-7 instruments (CS7 and results, FA7 ×2, CUR7, ADM7, ENV7, BA11r7, BA12r7, PPR7, DA05r7, DA06r7, PROF7, STATEMENTS-CHECK, REGISTER-CHECK, DA09r7, DA04r7, EXAMPLES) | all byte-identical to the committed outputs and logged digests. REGISTER-CHECK, DA09r7 and DA04r7 reproduce only after the committed `crashmig7.json` is supplied; EXAMPLES reproduces only in place (RV7-B-L5). |
| Retained instruments (23) | 16 byte-identical; 5 CSI checks and ADM6 differ in run-dependent leaves; DA07r6 on the revision-7 plan is stale (2 leaves, no verdict) |
| Review r6 B and D probes, unmodified (17) | 11 byte-identical: B-A04, A10, A11, A12; D-A01, A02, A03, A04, A06, A07, A10. B-A03: 2 stale leaves. Cannot run (confirmed, withdrawn artefacts): B-A01, B-A02, D-A05, D-A08, D-A09; their CP-1 re-expressions were re-run byte-identical. |
| Review r5 probes, unmodified | 9 byte-identical; RV5-B-A05, RV5-B-A08 run-dependent leaves only |
| Total comparisons | 68: 53 byte-identical, 8 run-dependent, 2 stale, 5 not runnable |

## 9. Held-out attacks

| Attacks | Count |
|---|---|
| Authored | 13 (RV7-B-A01…A13) |
| Executed | 9 |
| Computed (parts) | 3 |
| Design | 2, plus A12 as design and code |
| HIGH | A01 (with A06), A02 |
| MEDIUM | A03 |
| LOW | A04, A05, A07, A10, A11, A13 |
| INFO | A12 |
| Holding | A08, A09 |

## 10. Scope deviations and disclosures

- The architect's runner was adapted (placeholders filled). Reviewer C's chain (`matrix6`, `gitops6`, `attrprec6`, `crashmig7`)
  was not run: it is compatibility scope, and `crashmig7` needs C's built trees. The committed `crashmig7.json` was used only as
  REGISTER-CHECK's input.
- Review r6 reviewer C probe files were copied to scratch as the helper-library path the runner names. They were not used as
  review input.
- The harness saved two long tool outputs to files under `~/.claude/projects/`; those files were not read, and the source files
  were read directly. The background runner's task-output file was not read; the scratch logs were used.
- No helper sessions were used. There are no out-of-scope orchestration reads.

## 11. Unresolved

- The corrections for RV7-B-H1, RV7-B-H2 and RV7-B-M1 (architecture), with the re-review entry cases in `04`.
- CR7-B-01…CR7-B-07; RV6-L1 (RT-198); CR4-B-01, CR4-B-04, CR4-B-05.
- OT-1: owner decision. OT-2: no evidenced lineage, no certified target.
- No implementation exists. RT-184…RT-202 and CC-1…CC-9 are unexercised.
- Reviewer C scope (legacy containment, crash migration) is not assessed here.
