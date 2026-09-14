# 01 — Findings (review r3 B, trust and security)

Revision under review: RoT-1 revision 3, `ca77a431418bd6b349f465aa2521ca43bccfd5a6`.

## Evidence classes

| Class | Meaning |
|---|---|
| **executed** | real 4.1.5 binary or the pack's own checker |
| **computed** | independent reference model `evidence/RV3-B-M-reference-model.py` |
| **code** | 4.1.5 runtime, unchanged where cited |
| **design** | pack text |

Correction directions are architectural only. Nothing in this directory edits the pack.

## Summary

| ID | Severity | Blocking | Title |
|---|---|---|---|
| **RV3-B-H1** | HIGH | yes | The precedence order treats `immutable` as strongest, so a surface-eligible kernel silently discards project-owned strengthening |
| **RV3-B-H2** | HIGH | yes | Freshness anchors do not stop attacker-selected stale state becoming anchored-current on CI and first-install machines |
| **RV3-B-H3** | HIGH | yes | Binary acceptance never binds the compiled source to verified source; the TCB's source is chosen by threshold-1 `release-final` |
| RV3-B-M1 | MEDIUM | no (CR-01) | Lifting WITHDRAWN/REJECTED needs two keys, not three: the pre-withdrawal attestation is reusable |
| RV3-B-M2 | MEDIUM | no (CR-03) | Pins, decision pins and confirmations are files writable by the governed account; `gov` itself runs repository-supplied commands in that account |
| RV3-B-M3 | MEDIUM | no (CR-06) | Any verified `issued_at` raises a monotonic clock high-water; one far-future value permanently disables clock-based freshness |
| RV3-B-M4 | MEDIUM | no (CR-04) | The compromise playbook "TSS stops referencing them" contradicts artefact admissibility and freezes every verifier |
| RV3-B-M5 | MEDIUM | no (CR-02) | Computed weakening covers four overlay categories; `release-final`-signed migrations write any other overlay key without the weakening gate |
| RV3-B-L1 | LOW | no (CR-05) | Decision-table conflicts: OP-7 (d) with INCOMPLETE; OP-7 (c) with a non-witness anchor |
| RV3-B-L2 | LOW | no (CR-07) | The draft inventory marks keys read by `23` §6.5 security decision points as `project_tunable`; the `release-final` blast-radius sentence is inexact |
| RV3-B-L3 | LOW | no (CR-08) | No single YAML profile: the checker (YAML 1.1) and the runtime (serde_yaml) parse boolean tokens differently |
| RV3-B-L4 | LOW | no (CR-09) | Reinstall identity is checked against the A2-writable lock, not the VTS per-project record |
| RV3-B-L5 | LOW | no (CR-10) | TPS fields outside the surface (eligibility, gating, bootstrap, historical set) are outside the computed-reduction set |
| RV3-B-I1 | INFO | no | The acting role is still caller-declared (V-L5), so role-level ceilings bind only honest role declarations |

---

## RV3-B-H1 — HIGH — The precedence order treats `immutable` as strongest; a surface-eligible kernel silently discards project-owned strengthening

### Statement

1. **The order.** `23` §4 defines the project-layer order: `a ≥ b` if `a.mode = immutable` or `b.mode = overridable` or the modes match, subject to `exception_relaxable` implication. The join of incomparable rules is `immutable`. The effective precedence of each concrete key is that join (`19` §5.2), and the overlay is applied under it (`19` §5.3).

2. **Why the order is unsound.** A project-layer rule does two things. It refuses weakening overrides, and it *admits strengthening* overrides: a floor raise, an additive entry, a lower ceiling, a shrink-only removal, a strict boolean. `immutable` refuses every override, strengthening included (`runtime/src/policy_precedence.rs` `evaluate`; refusals leave the effective value at the kernel value, `runtime/src/policy.rs:162-190`). The `23` §4 order measures only the refusal direction. So `immutable ≥ floor | ceiling | additive | shrink_only | strengthen_only_bool` does not hold in effect: moving a rule to `immutable`, or joining to it, discards project strengthening already in the overlay.

3. **What the rest of the surface does with such a kernel.**
   - E7 and the checker report `precedence_weakened` only when the kernel rule is below the registered one. A move to `immutable` passes.
   - Precedence has no "stronger than registered" check, so the change also needs no TPS registration. `23` §6.2 claims "strengthening is mechanical" for values, but precedence rules are not covered.
   - `19` §9 (computed weakening) and `26` §6 (project-strength vector) compare overlay content. The overlay does not change, so both are silent.

### Evidence

- **executed** — `evidence/RV3-B-A01-precedence-immutable.json`. The kernel changes only `AUTHORITY_POLICY.authority_levels_required.*` (floor), `SECURITY_POLICY.never_index_classes` (additive) and `HUMAN_GATE_POLICY.agent_resolvable_when.max_radius` (ceiling) to `immutable`. Checker exit 0, surface-eligible, per-key join `immutable`; floor effective values equal genuine. The project overlay raises `resume_control` to L5, adds `confidential` to never-index for `product/customers/**`, and narrows `max_radius` to R0.

  | Test (both policy roots `verified: true`) | Genuine 4.1.5 kernel | Precedence-only kernel |
  |---|---|---|
  | L4 orchestrator `resume` under the project L5 raise | `AUTHORITY_DENIED` | succeeds; effective `resume_control: L4` |
  | Project-confidential customer file after `rebuild-memory` | excluded (`sensitivity:confidential`) | indexed and retrievable; effective `never_index_classes: [secret, restricted]` |
  | L3 agent answers an R1, 0.85, reversible gate under project R0 | `AUTHORITY_DENIED` | succeeds; effective `max_radius: R1` |
  | Overlay bytes | identical | identical |

- **design** — `23` §4, §6.2, §7; `19` §5.2–§5.3, §9; `26` §6; `12` RT-75 and RT-99 cover neither direction.

### Failure scenarios

1. **Honest owner, no attacker.**
   1. A future release "tightens" `SECURITY_POLICY.never_index_classes` to `immutable`, so that projects cannot remove `restricted`.
   2. Every project that had added `confidential` for customer data loses that protection on update.
   3. The `framework_update` trust gate shows an empty computed-weakening list.
   4. `rebuild-memory` indexes the customer files and context packets retrieve them.
   5. Every verdict is verified and eligible; no `PROJECT_STRENGTH_WEAKENED` is raised.

2. **Attacker.**
   1. A `release-final` thief signs a final with a high sequence (passes E10). Its authority required-levels, `max_radius`, `MEMORY_POLICY.namespaces.*.roles` (shrink_only) and `LEARNING_POLICY.upstream.allowed_payload` (shrink_only) are all set to `immutable`.
   2. A2 commits it. On anchored machines it becomes the policy root at use without any gate.
   3. Project L5 raises, agent-gate narrowing, namespace-role narrowing and upstream-payload narrowing all vanish.

### Why HIGH

An authentic, eligible kernel below root threshold confers weaker effective authority, indexing and gate policy while every check passes. This is the R2-H1 class. It also silently removes project-owned security controls, which is the R2-H4 harm that rule (20) exists to prevent. Both are shown on a real consumer.

### Correction direction

- Define the project-layer order in both directions: the refusal set must not shrink **and** the admitted-strengthening set must not shrink. `immutable` is then incomparable with modes that admit strengthening.
- Choose a join that keeps project strengthening, for example `floor` with the kernel minimum, never `immutable`.
- Register precedence rules like pinned values: any change needs a TPS registration.
- Compute project strength over the *effective* policy, meaning the applied project strengthening before and after any kernel, TPS or overlay change. Then `19` §9 and `26` §6 see losses from every source.

---

## RV3-B-H2 — HIGH — Freshness anchors do not stop attacker-selected stale state becoming anchored-current on CI and first-install machines

### Statement

HO-0001 §3.2 requires that an attacker controlling transport or the repository cannot select an old signed trust state and thereby create a current trusted fact. Revision 3 anchors freshness. Three mechanisms still leave the clean-CI-runner and first-install classes open.

**(a) Pins have no currency bound under the proposed OP-7 (a), and none under (c) or (d).**
- `24` §9 proposes (a) and says it "makes the review's B5 class impossible on every machine"; `21` OP-7 (a) says "impossible everywhere".
- A state pin is a static file: the schema has `provisioned_at` and no validity.
- A runner image pinned at epoch *e* accepts any genuine state ≥ *e* that A2 supplies, including releases revoked after *e*. It shows `ANCHORED(e, pin, age)` and may show `current` (`24` §4.1, R-ANCH-4).
- Every new TSS (each release, each emergency revocation) makes every existing pin stale. Nothing requires, detects or bounds re-provisioning: `13` §10 and `14` RK-25 only require that a pin exists.
- This is the review r2 P4-B5 / R2-H2 scenario, with "binary older than the TPS" replaced by "pin older than the TSS".

**(b) An anchor is satisfied by sequence number.**
- `24` §4.1 defines `BELOW_ANCHOR(have n < e)`. `17` S4(b) orphans forks only when the anchored TSS is held. The architect's `P4r3` `freshness()` implements `if seq < anchor["sequence"]`.
- A2 or A5 withholds the anchored TSS. A trust-state key (threshold 1) presents a TSS *n > e* that chains only through held lower states and omits later revocations.
- Current pins and first-install human anchors are then satisfied. The revoked release is a C2 policy root and passes C3 freshness and eligibility, under every OP-7 option.
- `17` §15 and `05` §1 state that trust-state theft is only a freeze.
- One sentence in `24` §3.2 ("When the confirmed epoch is not held … `BELOW_ANCHOR`") points the other way. It is not reflected in the axis definition, in pins, in S4 or in the reference model.

**(c) The OP-7 (c) witness is a threshold-1 trust-state signature under scheduled custody.**
- On a stateless runner, a thief's one-day witness that chains the compiled T0 and omits revocations yields `WITNESSED`, C2 and C3.
- `21` OP-7 (c) says "staleness bounded by the expiry window"; `17` §15 says "freeze".

**Contributing.** Pins can be rewritten by same-account processes, including repository-controlled code run on CI and by `gov` itself (RV3-B-M2). With a rewritten pin, every stateless runner is anchored at the attacker's epoch under every OP-7 option.

### Evidence

- **computed** — model scenarios `B5_r3…` (the claim holds without a pin and with a current held pin; it fails with a stale pin), `RV3-B-A02`, `RV3-B-A06`, `RV3-B-A12`.
- **computed** — the matrix in `evidence/RV3-B-M-reference-model.json`: 11 machine variants × OP-7 (a)–(d) × 3 adversaries, 132 rows. Revoked R7 is a C2 policy root in 90 rows and passes C3 freshness and eligibility in 86.

  | Machine | Rows where R7 is a C2 policy root | Unavoidable core? |
  |---|---|---|
  | M1 first install, anchor t10 | trust-state key, all options | no (A12) |
  | M2 runner, no pin | (d) only for A2/A5; all options with pin rewrite; (c) with the trust-state key | the (d) rows are the stated residual |
  | M2 runner, current pin t10 | pin rewrite and trust-state key, all options | no |
  | M2 runner, pin t5 aged 400 or 100 days | A2/A5 under (a), (c), (d); (b) only within the age limit | no (A02) |
  | M3 restored at t5 (400 days); M7 offline at t5 (1095 days) | (a), (c), (d) | anchored before the revocation (stated) |
  | M4 and M6B, anchored at t5 recently | all | yes (never received t9) |
  | M5 no epoch | as M2 without a pin | — |
  | M6A holding t10 | none | — |

- **design** — `24` §3.2, §4.1, §4.3, §5.2, §9; `21` OP-7; `17` S4(b), §15; `05` §1; `schemas/trust-state-pin.schema.json`; `evidence/P4r3-trust-state-model.py` `freshness()`.
- **executed** — `evidence/RV3-B-A03-A14-A16-probes.json` A03 (pin files written by a `gov`-executed repository command).

### Failure scenario

1. The owner publishes TSS 9, which revokes 4.1.7 after a security defect. The revocation fast path is used; the TPS raise follows later.
2. The organisation's CI image was pinned at TSS 5 three months earlier, and its `gov` was compiled at TSS 5.
3. A malicious collaborator reinstates the 4.1.7 kernel set and removes TSS 9 and the revocation from `governance/trust/state/`.
4. Every CI job reports `ANCHORED(5, pin, 90d)` and `KNOWN(5)`. 4.1.7 is eligible, and governance checks and agent mutations run with 4.1.7 as the verified policy root, with `current` permitted.
5. With a stolen trust-state key, the same works on runners whose pin was refreshed to TSS 9 (A12).

### Why HIGH

This is the recurring rejection class — attacker-selected stale signed state becoming a current trusted fact — on the machine class that enforces governance automatically. The stated bound of the proposed owner option is false, and a single threshold-1 key suffices for the anchor bypass.

### Correction direction

1. Define anchor satisfaction as: the anchored `(sequence, digest)` is held **and** is the effective TSS or in its `prior_states`; otherwise `BELOW_ANCHOR`. Apply it to pins, human confirmations and witnesses.
2. Give anchors a currency bound that the repository cannot defeat, or state the residual exactly. Either make currency a property the pin carries and C2/C3 checks, or state that under (a) a pinned runner is bounded only by pin maintenance and never show it as `current`. Restate `24` §9 and `21` OP-7 accordingly.
3. Under OP-7 (c), a witness must come from a purpose and threshold whose compromise is stated separately (≥ 2 keys, or a distinct purpose), or C3 must never rest on a witness alone. Correct the `17` §15 and `05` §1 blast-radius statements.
4. Apply pin integrity as in RV3-B-M2.

---

## RV3-B-H3 — HIGH — Binary acceptance never binds the compiled source to verified source; the TCB's source is chosen by threshold-1 `release-final`

### Statement

1. **The stated rule.** `25` §1: binary authentication must be at least as strong as the authority the binary carries. Compiled code (purpose table, schemas, operators, command register, bootstrap enforcement) is "protected by the build attestation. A reproduction of `source_commit` yields identical bytes only if the code is the tagged code" (`25` §4).

2. **Who chooses the source.** The "tagged code" is set by `release_commit` in the final release statement, and `release-final` (threshold 1) signs that statement.
   - V8 ("as revision 2"; `d37b05c` `04` V8) binds a final to its `promoted_from_candidate` by identical `kernel.tree_digest`, not by `release_commit`.
   - `verify-artifact` A4 requires `source_commit` = the final's `release_commit`. A1–A10 require no verification attestation, no certification and no candidate-commit match. The certification binding is informational (`25` §2).

3. **What each other signer checks.**
   - The rebuilder attests reproduction of `source_commit` (`05` §7 rule 6).
   - The `release-artifact` custodians "sign only binaries that carry at least one build attestation" (`05` §7 rule 6).
   - The trust-state publisher references the artefact statement (`07` §7 step 14).

   No rule checks that the built source is the source an independent verifier attested.

4. **Consequence.** A `release-final` key plus control of the pipeline input (A5 release or Git host, or A6) gets a malicious binary accepted.
   - The attacker signs a final promoted from a genuine attested candidate, with an identical kernel tree (so V8 and E7 pass) and `release_commit` = C′.
   - The three other purposes sign as their rules direct.
   - The malicious binary's TBM names genuine root, TPS and TSS digests, so A6 passes; its code ignores them.

5. **Overstated bound.** `25` §7 ("one `release-final` key: no"; "4 keys over 3 purposes") and TB-3 overstate it. Review r2 CD2-3 required "an ACCEPTED verification attestation of that artifact digest"; that requirement was dropped with no equivalent.

### Evidence

- **computed** — model `RV3-B-A08`: `verify-artifact` returns `ACCEPTED`; with the attested-source requirement it returns `ARTIFACT_SOURCE_UNVERIFIED`.
- **design** — `25` §1–§7; `05` §7 rules 2 and 6; `07` §3 and §7; `d37b05c` `04` V8. `09` R-REL-6 requires an ACCEPTED attestation for `release promote`, a producer tool that a key holder does not need to use; acceptance never re-checks it.

### Failure scenario

1. A7 steals the `release-final` token, and A5 controls the Git host.
2. The attacker pushes commit C′. Its kernel is identical to the verified 4.1.8 candidate, but its runtime skips E7, anchors and trust gates.
3. The attacker signs final 4.1.8 naming C′, promoted from the genuine candidate.
4. The rebuild job reproduces C′ and the rebuilder attests. The two artefact custodians see a build attestation and sign. The owner's routine TSS publication references the artefact.
5. `gov trust verify-artifact` accepts it on every machine. The installed `gov` reports verified everywhere while enforcing nothing.

### Why HIGH

TCB compromise below the declared threshold, with the same adversary and outcome as R2-H3.

### Correction direction

- The verification attestation, or a certification that references it, must name the candidate's `release_commit` and build inputs.
- V8 must require final `release_commit` = candidate `release_commit`.
- `verify-artifact` must require an ACCEPTED attestation whose commit equals the TBM `source_commit`, and may additionally require `CERTIFIED_AS_OF` for the final.
- The custodial rules for `build-attestation`, `release-artifact` and `trust-state` must include this check.

---

## RV3-B-M1 — MEDIUM — Lifting WITHDRAWN or REJECTED needs two keys, not three

**Statement.**
- **The rule.** MS-2 and S5 lift a negative only with a higher CERTIFIED that the effective TSS references. That CERTIFIED must reference an ACCEPTED attestation that the TSS also references.
- **The gap.** A verification attestation binds a candidate digest, with no sequence and no relation to the negative. The attestation that preceded the withdrawal therefore remains valid input.
- **Result.** A lift needs new signatures only from `certification-status` and `trust-state`. The `05` §3 statement ("lift of WITHDRAWN/REJECTED: 3 distinct keys") and `17` §3 are false. The architect's own P4r3 B2 scenario lifts with the pre-withdrawal attestation `a1`, and RT-97 would accept it.

**Evidence.** computed — model `RV3-B-A05`; `evidence/arch-rerun-P4r3-trust-state-model.json` B2.

**Failure scenario.**
1. A release is WITHDRAWN for a security defect.
2. Thieves of the certification and trust-state keys (threshold 1 each) re-certify it, reusing the old attestation.
3. The release becomes `CERTIFIED_AS_OF` again and is no longer refused by `refuse_known_withdrawn`.

**Why MEDIUM.** It needs two purposes' keys, and it affects certification visibility and withdrawal refusal, not authenticity or floors. The fix is bounded (CR-01).

---

## RV3-B-M2 — MEDIUM — Pins, decision pins and confirmations are files writable by the governed account

**Statement.**
- **Where the authority files live.** State pins (`24` §3.2), operator decision pins (`27` §3.2) and VTS confirmations are files in the account's home.
- **Who can write them.** Any process of that account, including:
  - agent tool calls, the actors Governance OS governs;
  - plugins;
  - tool install commands and product test commands run by `gov` (`02` §5 rows 12–13; `runtime/src/verification/mod.rs:956-1001`, `tools.rs:458-464`, `capabilities/host.rs:175-190`);
  - on CI, any repository-controlled build step.
- **Why the stated assumptions do not cover it.** TA-9 addresses who provisions a pin, not who can rewrite it afterwards. `27` §3.3 ("MUST NOT be answerable by `gov decide` or by any agent path") holds only for the `gov decide` path.
- **Declared residuals versus reliance.** RS-3, RS-4 and TG-2 name A3. Yet the architecture relies on pins as its CI solution and on decision pins as its automation path, and presents agent-unanswerability as a compiled rule.

**Evidence.**
- **executed** — A03. The real 4.1.5 `gov verify product` ran an A2-committed `PROJECT_POLICY.tests.product_test_command` as uid 1000, and it wrote `trust-state-pins` and `approved-trust-decisions` (owner 1000, mode 0644). The account-database home is writable by that uid.
- **computed** — model `RV3-B-A03`: a forged or rewritten pin anchors every stateless runner, and a runner whose current pin is rewritten, under every OP-7 option.
- **computed** — model `RV3-B-A04`: a same-account decision pin authorises `framework_update`, `weakening` and `project_strength`.

**Why MEDIUM.** The same-account boundary is declared. A bounded, testable check (file and ancestor writability, or a read-only mount), with TA-9 and `27` §3.3 restated, contains it (CR-03). Relative to R2-M1, this is the part not closed.

---

## RV3-B-M3 — MEDIUM — Any verified `issued_at` raises a monotonic clock high-water

**Statement.**
- **The high-water.** `24` §8 keeps a monotonic "highest verified `issued_at`", used for clock-rollback detection (`17` §13 (c), RS-2), and a "highest witness `issued_at`" (`24` §3.2).
- **The gap.** Any verified statement raises it; release, candidate, certification and build-attestation statements all carry `issued_at`. Nothing bounds the value by the local clock, and no reset exists.
- **Result.**
  - A `release-candidate` key (lowest custody) signing `issued_at` 100 years ahead permanently disables OP-3 mode B and OP-7 (b) and (c) on every VTS that ingests it, even after re-anchoring.
  - A trust-state key doing the same with a witness permanently rejects honest witnesses.
  - This contradicts `05` §1 ("candidates only") and `17` §15 ("until the next honest TSS or a root rotation").

**Evidence.** computed — model `RV3-B-A07`.

**Why MEDIUM.** The harm is persistent loss of availability, not trust. The fix is bounded (CR-06).

---

## RV3-B-M4 — MEDIUM — The compromise playbook contradicts artefact admissibility

**Statement.**
- `05` §9 (release-artifact compromise) says the "TSS stops referencing them".
- `17` S4(d) requires `T.artifacts ⊇ L.artifacts`. An honest TSS that drops the references is therefore non-admissible, giving `REGRESSION` and C0 on every verifier holding the earlier TSS.
- Only a root-signed chain reset recovers.

**Evidence.** computed — model `RV3-B-A09`.

**Why MEDIUM.** It turns the compromise remedy into a global freeze. Fix: CR-04.

---

## RV3-B-M5 — MEDIUM — Computed weakening covers four overlay categories; release-signed migrations write any other overlay key without the weakening gate

**Statement.**
- **How migrations are bound.** Migrations are `transaction_input` (`23` §3.1), bound only by the release statement's `migrations[]`. That statement is `release-final`-signed; V10 checks listing, digest and chain; R-MIG-6 says only "declarative".
- **What is checked.** `19` §9 computes weakening in four categories: classifications, overlay floor raises, contract exclusions, and deleted non-overridable overlay keys.
- **What migrations can write.** The operations `set_overlay_key`, `rename_overlay_key`, `delete_overlay_key`, `add_overlay_file_from_template`, `rename_overlay_file` and `set_overlay_rule` (`runtime/src/migrations/framework.rs:82-230`) write any key of any overlay file, and `overlay.join(&file)` accepts any relative path.
- **Security-relevant content outside the four categories:**
  - `TOOL_PERMISSIONS.yaml` role permission classes, which plugin authorisation checks (`capabilities/governance.rs:287`);
  - `TOOL_PERMISSIONS.yaml` `install_authority_roles` (`capabilities/governance.rs:420-433`; `tools.rs:52,147,324`);
  - `PROJECT_EXCEPTIONS.yaml` entries;
  - `DATA_SENSITIVITY.identifiers_to_strip`, used for upstream redaction (`security/secrets.rs:81`);
  - `REPOSITORY_CONTRACT` includes.
- **Result.** A `release-final`-signed migration can widen all of these with only the `framework_update` trust gate, whose computed-weakening list is empty. The checker passes a new migration file (injection I08, exit 0).

**Evidence.**
- **design** — `19` §9, `23` §3.1, `04` V10, `09` R-MIG.
- **code** — as cited above.
- **executed** — `evidence/RV3-B-CSI-injections.json` I08.

**Why MEDIUM.** It needs ingress with a local trust gate. The fix is bounded (CR-02: total weakening computation and an operation × target whitelist). It shares a root with H1: project strength must be computed over effective configuration.

---

## LOW

| ID | Statement | Evidence | Carried |
|---|---|---|---|
| RV3-B-L1 | Two conflicts in the decision rules. (i) Under OP-7 (d), `24` §4.3 allows C2 on an unanchored `INCOMPLETE` machine, while `17` §7 requires `KNOWN`. (ii) Under OP-7 (c), §4.3 and §9 let non-witness anchors of any age allow C2/C3, while §5.7 says (c) refuses for lack of a fresh witness. | computed A10, A11 | CR-05 |
| RV3-B-L2 | The draft inventory classifies `MEMORY_POLICY.embedding.provider`, `ARCHIVE_POLICY.default_retrieval_for_archive` and `LEARNING_POLICY.upstream.aggregate_metrics_enabled` as `project_tunable`, yet their runtime consumers are `23` §6.5 security decision points. A kernel changing them passes the checker. `05` §1 and `21` OP-2 say only root-registered content becomes a policy root, which is inexact for 57 `project_tunable` and 32 `release_bound` leaves. A2 can already set overridable keys, so A7's marginal harm is limited. | executed A16; code `memory/embedder.rs:27,125`, `project.rs:170`, `paths.rs:288`, `upstream.rs:140` | CR-07 |
| RV3-B-L3 | The checker parses with PyYAML (YAML 1.1). All 10 strict-true `bool_toward` floors written as `on` pass (exit 0), while the 4.1.5 runtime reads the string `"on"`. 4.1.5 defaults for these keys are `true`, so there is no weakening in 4.1.5, but producer, CI and binary can disagree. | executed A14; code `get_bool` defaults | CR-08 |
| RV3-B-L4 | `20` §8 remedies authenticate the source "to the lock-recorded identity", and the lock is A2-writable. `17` §7 gives reinstall no freshness and no gate. | design A15 | CR-09 |
| RV3-B-L5 | `19` §10.6 computes reductions over surface leaves, precedence, classes and registrations only. It does not cover `eligibility.min_release_sequence`, `historical_releases[]`, `install_authority`, `gating.mode`, `local_terminal_only[]` or `bootstrap.op7_mode`, whose lowering needs root threshold but bypasses `lowering_history` and the per-project gate (G11). | design A17 | CR-10 |

## INFO

**RV3-B-I1 — caller-declared role.**
- The acting role remains caller-declared (V-L5, `19` §8, RK-14).
- ROLES `level_at_most` ceilings therefore bound callers who declare their role truthfully; trust gates do not depend on role.
- This review requests no change and notes it only because the P1 and A01 authority harms are measured under that model.
