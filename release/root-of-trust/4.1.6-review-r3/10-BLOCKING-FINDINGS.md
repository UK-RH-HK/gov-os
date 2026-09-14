# 10 — Consolidated findings (review r3 synthesis D), CRITICAL to LOW

Revision reviewed: RoT-1 revision 3, `ca77a431418bd6b349f465aa2521ca43bccfd5a6`. Panel: B `7d8c73a`, C `9e013c1`.

| Severity | Count | IDs |
|---|---|---|
| CRITICAL | 0 | — |
| HIGH | 3 | RV3-H1, RV3-H2, RV3-H3 |
| MEDIUM | 9 | RV3-M1 … RV3-M9 |
| LOW | 8 | RV3-L1 … RV3-L8 |
| INFO | 1 | RV3-I1 |

## Evidence classes

| Class | Meaning |
|---|---|
| **executed** | real legacy binary (4.1.5 unless stated), real Git, or the pack's own checker `constitutional-surface/csi_check.py` |
| **computed** | the pack's own lattice (`csi_lib.py`), the architect's own model (`evidence/P4r3-trust-state-model.py`, loaded unmodified), or reviewer B's model (reproduced byte-identical) |
| **design** | pack text at `ca77a43` |
| **code** | 4.1.5 runtime, unchanged since `da9c851` |

Every panel probe cited below was re-run by this review (`D-synthesis/01-REPRODUCTION.md`). "D-Axx" means RV3-D-Axx (`D-synthesis/03-HELDOUT-ATTACKS-RV3-D.md`).

No CRITICAL finding. The review r2 "no CRITICAL" basis still holds: the compiled root chain, purpose-bound statements and the single authentication boundary are non-circular.

---

## RV3-H1 — HIGH — The precedence order is refusal-only: a kernel precedence change, a deleted POLICY_PRECEDENCE file or a root-signed TPS tightening silently discards project-owned strengthening

**Origin.** RV3-B-H1, extended by D-A01, D-A02 and D-A10. **Adjudication:** CONFIRMED HIGH.

### Statement

1. **The order.**
   - `23` §4 defines `a ≥ b` for the project layer as follows: `a.exception_relaxable` implies `b.exception_relaxable`, and either `a.mode = immutable`, or `b.mode = overridable`, or the modes are equal.
   - The join of incomparable rules is `immutable`.
   - The same order is used in three places:
     - E7 (`precedence_weakened`);
     - the effective-policy join (`19` §5.2);
     - computed reductions of a TPS (`19` §10.6).
   - Code: `csi_lib.py` `rule_ge` and `rule_join`.
2. **What the consumer does.**
   - Under `immutable` the runtime refuses every project override, strengthening included (`runtime/src/policy_precedence.rs` `evaluate`).
   - Each other mode admits exactly one direction of project strengthening:
     - `floor` admits a raise;
     - `ceiling` admits a lower value;
     - `additive` admits adding entries;
     - `shrink_only` admits removing entries;
     - `strengthen_only_bool` admits setting the strict value.
3. **Class defect.** The order measures only the refusal direction. For all five strengthening modes `immutable ≥ mode` holds, yet `immutable` admits strictly less project strengthening. That is 5 unsound pairs out of 36 evaluated (D-A01, computed on the pack's lattice). Three routes reach the same loss.
   - **(a) Kernel precedence change.**
     - A kernel that only moves rules to `immutable` passes the checker with exit 0.
     - No registration is needed, because precedence has no "stronger than registered" check.
     - The per-key join is `immutable`.
     - (RV3-B-A01, reproduced with 0 differences.)
   - **(b) Deleted `policies/POLICY_PRECEDENCE.yaml`.**
     - The checker exits 0 (D-A10 R07).
     - With no kernel rules, every key's kernel rule is the default `immutable`.
     - The join makes **66 of 85 registered rules** `immutable` for the project layer: additive 19, ceiling 10, floor 13, overridable 13, shrink_only 4, strengthen_only_bool 7.
   - **(c) Root-signed TPS tightening.**
     - TPS v2 registers `immutable` where v1 registered a strengthening-admitting mode.
     - This is not a computed reduction, so it needs no `lowering_history` entry and no per-project `policy_lowering` gate.
     - Older kernels registered under v1 become `precedence_weakened` (ineligible).
     - The effective project-layer mode is `immutable` for all five modes (D-A02).
4. **Detectors are blind.**
   - `19` §9 (computed weakening) and `26` §6 (project-strength vector) take overlay content as input. The overlay is unchanged in all three routes.
   - D-0008 rule (3) ("a project layer may strengthen") and rule (20) ("project-owned strengthening is recorded … a weakening is reported") therefore do not hold.

### Evidence

- **executed** RV3-B-A01 on the real 4.1.5 binary. Both policy roots report `verified: true`; the overlay bytes are identical.

  | Test | Genuine kernel | Precedence-only kernel |
  |---|---|---|
  | L4 orchestrator `resume` under the project L5 raise | `AUTHORITY_DENIED` | succeeds |
  | Project-confidential customer file after `rebuild-memory` | excluded | indexed and retrievable |
  | L3 agent answers an R1 gate under project R0 | `AUTHORITY_DENIED` | succeeds |

- **computed** D-A01: 5 unsound pairs. D-A02: all five modes lose project strengthening through a TPS, with no gate.
- **executed** D-A10 R07: checker exit 0 on deletion; 66 of 85 rules join to `immutable`.
- **design** `23` §4, §6.2 (strengthening mechanical for values, not precedence), §7; `19` §5.2, §9, §10.6; `26` §6; `12` RT-75 and RT-99 cover neither direction.
- **code** `runtime/src/policy_precedence.rs` `evaluate` (`"immutable" => refuse`).

### Failure scenarios

1. **Honest owner.**
   1. A release "tightens" `SECURITY_POLICY.never_index_classes` to `immutable`.
   2. The `framework_update` gate shows an empty weakening list.
   3. Every project's `confidential` additions stop applying, and customer files are indexed.
2. **Root ceremony.**
   1. A TPS registers `immutable` for `AUTHORITY_POLICY.authority_levels_required.*`.
   2. Projects that raised required levels lose the raises with no `policy_lowering` gate.
   3. Every kernel registered under the previous TPS becomes ineligible, and machines fall back to EmbeddedSnapshot ⊔ floors.
3. **Attacker.**
   1. A `release-final` thief signs a final whose only change is a deleted POLICY_PRECEDENCE file. E7 passes and the sequence is eligible.
   2. A2 commits it.
   3. On anchored machines it is the policy root at use, with no gate. Every project strengthening and every project tunable disappears.

### Why HIGH

- Authentic, eligible content confers weaker effective authority, indexing and gate policy while every check passes. That is the R2-H1 class.
- It silently removes project-owned security controls. That is R2-H4's harm, executed on a real consumer.
- The trigger is one threshold-1 key plus the repository writer, or a routine owner release or TPS ceremony.

---

## RV3-H2 — HIGH — Stale state becomes anchored-current: anchors satisfied by sequence number, pins without currency, and a threshold-1 witness make revoked state a policy root, a C3 target and an accepted binary

**Origin.** RV3-B-H2, extended by D-A11, D-A12 and D-A15. **Adjudication:** CONFIRMED HIGH.

### Statement

HO-0001 §3.2 requires that a transport or repository attacker cannot select an old signed trust state and create a current trusted fact. Revision 3's anchors do not meet this requirement on the machine class that enforces governance automatically. Three rules cause the failure.

1. **Anchor satisfaction by sequence number.**
   - The rules:
     - `24` §4.1 defines `BELOW_ANCHOR(have n < e)`.
     - `17` S4(b) orphans forks only when the anchored TSS is held.
     - The architect's model implements `if seq < anchor["sequence"]`.
   - The contrary text: `24` §3.2 and §5.1 say an unheld confirmed epoch gives `BELOW_ANCHOR`. That sentence is not reflected in the axis definition, in pins, in S4 or in the model.
   - The attack:
     - A2 or A5 withholds the anchored TSS and later revocations.
     - One trust-state key (threshold 1) presents TSS *n* > *e* that chains only held lower states.
     - The machine is then `ANCHORED` and `KNOWN(n)` without the revocation.
2. **No currency bound on pins.**
   - The pin schema has `provisioned_at` and no validity.
   - Under the proposed OP-7 (a), a runner pinned at *e* accepts any genuine state ≥ *e* that A2 supplies, including releases revoked after *e*.
   - The runner shows `ANCHORED(e, pin, age)`, and `current` is permitted (R-ANCH-4). The pack says (a) makes the B5 class "impossible everywhere".
3. **Witness authority is a single threshold-1 key.**
   - Under OP-7 (c) a thief-minted, one-day witness yields `WITNESSED` and C0–C3 on stateless runners.
   - `21` OP-7 (c) says "staleness bounded by the expiry window"; `17` §15 and `05` §1 say trust-state theft is a "freeze".

### Evidence

- **computed** (architect's own functions, D-A12). Setup: pin (10, t10); the repository carries t1, t5, t100 (t100 chains t1 and t5 only) and R7; t9, t10 and the revocation `rv7` are withheld.

  | Anchor semantics | Result |
  |---|---|
  | Sequence (pack `24` §4.1, P4r3) | `ANCHORED(anchor 10, held 100)`, R7 not in the negative set, C2 and C3 allowed |
  | Chain inclusion | `BELOW_ANCHOR`, C0 only |
  | Machine holding t10 | `REGRESSION` (a freeze, as claimed) |

- **computed** (architect's functions, D-A15): a genuine production binary revoked in t9 is re-accepted by `verify-artifact` (A9 freshness plus A1–A8) on a pinned CI runner in two cases.
  - With a stale pin at t5: under both anchor semantics.
  - With a current pin at t10 plus t100 from the trust-state key: under sequence semantics.

  The same attack path reaches the TCB.
- **computed** (reviewer B's model, reproduced byte-identical): 11 machine variants × OP-7 (a)–(d) × 3 adversaries = 132 rows. Revoked R7 is a C2 policy root in 90 rows and passes C3 freshness and eligibility in 86. Named cases: RV3-B-A02 (stale pin), A06 (witness minting), A12 (higher unchained TSS).
- **computed** D-A11: the architect's model passes 34 of 34 scenarios under both sequence and chain-inclusion semantics, so the acceptance plan's mandated oracle cannot detect this defect.
- **design** `24` §3.2, §4.1, §4.3, §5.1–§5.2, §9; `17` S4(b), §15; `05` §1; `21` OP-7; `schemas/trust-state-pin.schema.json`; `09` R-ANCH-1…4.

### Unavoidable core versus this finding

| Situation | Determination |
|---|---|
| A machine anchored before a revocation that never receives later metadata (M3, M4, M6B, M7) | **Unavoidable core, accepted**, provided it is never labelled `current` beyond a stated bound |
| An anchor satisfied by a higher sequence while the anchored statement is not held | **Not core.** Removed by inclusion semantics (D-A12 flips). |
| A pin with no currency bound, labelled `ANCHORED` and `current` indefinitely, and permitting C3 and binary acceptance | **Not core.** Boundable by a validity or age limit, or by exact non-current labelling with stated operation classes. |
| A witness whose authority is one threshold-1 key declared a "freeze" | **Not core.** Boundable by threshold, a distinct purpose, or by C3 never resting on a witness alone. |

### Failure scenario

1. The owner publishes TSS 9 revoking a release and its binary after a security defect. There is no TPS raise; `17` §8 says only "SHOULD".
2. CI images were pinned at TSS 5.
3. A malicious collaborator reinstates the revoked kernel set and strips TSS 9.
4. Every CI job reports `ANCHORED(5, pin, age)` and `KNOWN(5)`. The revoked release is the verified policy root, and the revoked binary passes `verify-artifact`.
5. On runners whose pin was refreshed to TSS 10, the same outcome follows with one stolen trust-state key.

### Why HIGH

- The recurring rejection class — attacker-selected stale signed state becoming a current trusted fact — appears on automated enforcement machines, including TCB acceptance.
- The bound of the proposed default option is false.
- A single threshold-1 key whose declared blast radius is a freeze suffices.

---

## RV3-H3 — HIGH — Binary acceptance never binds the built source to verified source; threshold-1 `release-final` chooses the TCB's source

**Origin.** RV3-B-H3, extended by D-A03. **Adjudication:** CONFIRMED HIGH.

### Statement

1. **Who chooses the source.**
   - `25` A4 requires the build attestation's `source_commit` to equal the final release's `release_commit`.
   - The final release statement is signed by `release-final` (threshold 1).
2. **V8 binds only the kernel tree.**
   - Revision 3's `04` V8 is "as revision 2". Revision 2 (`d37b05c` `04` V8) binds a final to its `promoted_from_candidate` by identical `kernel.tree_digest`.
   - It does not bind `release_commit`.
   - A final can reuse a verified candidate's kernel tree while naming a different commit whose runtime differs.
3. **Nobody checks legitimacy.**
   - `verify-artifact` A1–A10 require no verification attestation and no candidate-commit match.
   - The custodial rules check other things:
     - the rebuilder attests reproduction of `source_commit` (`05` §7 rule 6);
     - the `release-artifact` custodians sign binaries that "carry at least one build attestation";
     - the TSS publisher references the artefact.
   - `09` R-REL-6 binds only the `promote` producer tool, which a key holder need not use.
4. **Consequence.**
   - `release-final` plus control of the pipeline input (A5, or A6) gives an accepted malicious binary. It carries genuine root, TPS and TSS digests in its TBM, so A6 passes, and its code ignores them.
   - The bound "4 keys over 3 purposes" (`25` §7, `05` §3, TB-3, OP-2) is false.
   - Review r2 CD2-3's "ACCEPTED verification attestation" requirement was dropped with no equivalent.
5. **Owner-option combination (D-A03).** Under OP-4 "no", the everyday candidate-signing key is this key. `21` OP-4's "no longer exposes binaries" is false.

### Evidence

- **computed** RV3-B-A08 (reproduced): `verify-artifact` gives `ACCEPTED`. With an attested-source requirement it gives `ARTIFACT_SOURCE_UNVERIFIED`.
- **design** `25` §1–§7; `05` §3, §7 rules 2 and 6; `07` §3, §7; `04` V8 (revision 3 "as revision 2") with `d37b05c` `04` V8; `09` R-REL-6; `21` OP-2, OP-4.

### Failure scenario

1. A7 steals the `release-final` token; A5 controls the Git host.
2. The attacker pushes commit C′: kernel identical to the verified candidate, runtime skipping E7, anchors and trust gates.
3. The attacker signs final F′ promoted from the genuine candidate, naming C′.
4. The rebuilder reproduces C′; the artefact custodians see an attestation and sign; the TSS references the artefact.
5. `gov trust verify-artifact` accepts the binary everywhere, and the binary enforces nothing.

### Why HIGH

It is TCB compromise with the same adversary and outcome as R2-H3, below the declared threshold.

---

## MEDIUM

Each is carried in `11-CORRECTION-DELTA.md` §6 with its acceptance test, except RV3-M5, whose class closes inside CD3-1.

| ID | Statement | Evidence | Origin → adjudication | Carried as |
|---|---|---|---|---|
| **RV3-M1** | A lift of WITHDRAWN or REJECTED needs a higher CERTIFIED referenced by the effective TSS, with an ACCEPTED attestation the TSS also references. The pre-withdrawal attestation satisfies that, so a lift needs two new signatures (certification-status and trust-state), not three. `05` §3 and `17` §3 are false. The architect's P4r3 B2 lift reuses the pre-withdrawal `a1`. | computed RV3-B-A05 (reproduced); P4r3 B2 read | RV3-B-M1 → CONFIRMED MEDIUM (two purposes' keys; affects withdrawal refusal, not authenticity or floors) | CR-01 |
| **RV3-M2** | State pins, decision pins and VTS confirmations are files the governed account can write. That account includes agent tool calls, plugins and commands `gov` itself runs, such as `gov verify product` executing an A2-committed `product_test_command`. `27` §3.3 ("never answerable by any agent path") holds only for `gov decide`. | executed RV3-B-A03 (reproduced: both pin files written by uid 1000, mode 0644); computed A04 | RV3-B-M2 → CONFIRMED MEDIUM. Not raised: repository code running in a CI job before `gov`'s decision is outside TA-9 whatever the design; the `gov`-executed vector and file integrity are bounded by CR-03. Also required by CD3-2 (4). | CR-03 |
| **RV3-M3** | Any verified `issued_at` raises a monotonic clock high-water, with no local-clock bound and no reset. One far-future candidate or witness permanently disables OP-3 mode B and OP-7 (b)/(c) on each VTS that ingests it. | computed RV3-B-A07 (reproduced) | RV3-B-M3 → CONFIRMED MEDIUM (availability) | CR-06 |
| **RV3-M4** | `05` §9 ("TSS stops referencing them") contradicts `17` S4(d) (`artifacts ⊇`). The honest remedy makes every verifier holding the earlier TSS `REGRESSION`. | computed RV3-B-A09 (reproduced) | RV3-B-M4 → CONFIRMED MEDIUM | CR-04 |
| **RV3-M5** | `19` §9 computes weakening over four overlay categories. `release-final`-signed migrations (`set_overlay_key` and similar, any overlay file) can widen `TOOL_PERMISSIONS`, `PROJECT_EXCEPTIONS`, `identifiers_to_strip` or contract includes under a `framework_update` gate whose weakening list is empty. The checker passes a new migration (I08). | design `19` §9, `23` §3.1; code `migrations/framework.rs`; executed I08 (reproduced) | RV3-B-M5 → CONFIRMED MEDIUM. Its root (strength not computed over effective policy) is RV3-H1's class. | class closes in CD3-1 (3); op × target whitelist CR-02 |
| **RV3-M6** | The occupation defence holds only while the occupation entries are present. Four observations follow. **(i)** After removal of all entries, real 4.1.5 `init --force` completes a `verified: true` legacy install that retrieves restricted material (C). **(ii)** One ordinary `git checkout <pre-migration> -- governance` retypes every legacy authority path. The legacy binary then goes from `NOT_INSTALLED` to `verified: true` and retrieves a file that only the RoT-1 overlay classifies (D-A05); `git restore --source` also removes `governance/trust` and the overlay (LR-1 class). **(iii)** In both states, a legacy CIT (propose, simulate, `gate present`, caller-declared `decide`, approve, execute) rewrites `governance/trust/kernel/policies/SECURITY_POLICY.yaml`, deletes `governance/trust/framework.lock` and removes the overlay classification. The intact-layout control refuses every step with `NOT_INSTALLED` (D-A06). **(iv)** LR-2 and RT-81 state and test none of this. | executed C A04–A06 (reproduced); executed D-A05, D-A06 | C-1 → CONFIRMED MEDIUM, broadened. C's statement that `governance/trust/**` is outside every legacy write set is refuted except for the intact layout. Not HIGH: RoT-1 binaries report `PARTIAL`/`KERNEL_TAMPERED` and fail closed; overlay changes are A2-equivalent (LR-4) and detected where recorded; no design stops Git restoring pre-migration history. | C-1 (restated), D-A05/A06 tests |
| **RV3-M7** | Surface totality covers content present in a kernel, not content registered. **(a)** Removing a registered constitutional file passes the producer checker and E7. With the pack's checker, exit 0 for each of: `SECURITY_POLICY.yaml`, `HARD_INVARIANTS.yaml`, `ENFORCEMENT_MAP.yaml`, a schema, `ROLES.yaml`, the generic adapter template, `HUMAN_GATE_POLICY.yaml`, `AUTHORITY_POLICY.yaml`. **(b)** Floor leaves are then joined, which is safe. **(c)** Pinned and members content falls to "the consumer's compiled fail-closed default" (`19` §5.2), which no rule defines per consumer and no RT exercises (for example, the registered `secret_content_patterns` regexes). **(d)** For owner-supplied constitutional files outside the kernel (`23` §7.1), the reference checker has no domain support, absence on an unconfirmed machine is not specified as fail-closed, and such files are outside the strength vector. The POLICY_PRECEDENCE deletion case belongs to RV3-H1. | executed D-A10 R01–R09; design D-A18 | NEW (D) → MEDIUM: an underspecified fallback, not a demonstrated harm beyond RV3-H1 | defined fallback + removal tests |
| **RV3-M8** | `25` A7, the first-run self-check and R-ART-2 compare the TBM with "the VTS high-water", and `24` §8's high-water includes the TSS sequence. The TSS that references a binary's artefact must be later than the TSS the binary compiles (otherwise the digests would form a cycle), and A5 requires that TSS to be held. Under the TSS reading every realisable genuine binary is `BINARY_T0_ROLLBACK`, and every installed binary refuses trusted operations after the next TSS. P4r3's `A_valid` passes only through a circular, non-realisable construction (its TBM names t9 and t9 references the artefact). | computed D-A13 (TSS high-water `BINARY_T0_ROLLBACK`; accepted-TBM high-water `ACCEPTED`) | NEW (D) → MEDIUM (fails closed; a clarifying rule closes it) | define against the accepted-TBM high-water |
| **RV3-M9** | The acceptance plan cannot detect the blocking classes, and its mandated oracle encodes defects. **(a)** `12` RT-72(vi) and `13` §8 require the implementation to reproduce P4r3 34/34, but P4r3 passes 34/34 under both anchor semantics (D-A11) and contains the non-realisable `A_valid` (RV3-M8). **(b)** `12` §1 rule 11 forbids expectations defined as the architect's evidence, while §8 and `13` §8 mandate exactly that. **(c)** RT-75, RT-80, RT-81 and RT-92 lack the RV3-B-A01/A02/A08/A12, D-A01/A02/A05/A06/A10/A15 and C-1 cases. | computed D-A11; design `12`, `13` §8 | NEW (D, with B CR-11 and CR-12) → MEDIUM (review r2 R2-M10 remainder) | property assertions; distinguishing scenarios; RT per attack |

## LOW

| ID | Statement | Evidence | Origin → adjudication | Carried as |
|---|---|---|---|---|
| RV3-L1 | Decision-table conflicts: under OP-7 (d), `24` §4.3 allows C2 on an unanchored `INCOMPLETE` machine while `17` §7 requires `KNOWN`; under OP-7 (c), non-witness anchors of any age allow C2/C3 while `24` §5.7 says (c) refuses without a fresh witness. | computed RV3-B-A10, A11 (reproduced) | RV3-B-L1 → CONFIRMED LOW | CR-05 |
| RV3-L2 | Draft inventory keys read by `23` §6.5 security decision points are `project_tunable` (`MEMORY_POLICY.embedding.provider`, `ARCHIVE_POLICY.default_retrieval_for_archive`, `LEARNING_POLICY.upstream.aggregate_metrics_enabled`). The `release-final` blast-radius sentence is inexact. | executed RV3-B-A16 (reproduced) | RV3-B-L2 → CONFIRMED LOW (A2 can already set overridable keys) | CR-07 |
| RV3-L3 | The checker uses PyYAML (YAML 1.1) and the runtime serde_yaml: `on` is `true` to the checker and the string `"on"` to 4.1.5. | executed RV3-B-A14 (reproduced) | RV3-B-L3 → CONFIRMED LOW | CR-08 |
| RV3-L4 | `20` §8 remedies authenticate to the A2-writable lock-recorded identity; `17` §7 gives same-digest reinstall no freshness and no gate. | design RV3-B-A15 | RV3-B-L4 → CONFIRMED LOW (no marginal harm over Git delivery) | CR-09 |
| RV3-L5 | TPS fields outside the surface (`min_release_sequence`, `historical_releases[]`, `install_authority`, `gating.mode`, `local_terminal_only[]`, `bootstrap.*`) are outside the computed reduction and per-project gate. | design RV3-B-A17 | RV3-B-L5 → CONFIRMED LOW (root threshold required) | CR-10 |
| RV3-L6 | The OP-7 (d) consequence limits the residual to "binaries older than the newest TPS". A revocation-only TSS (`17` §8 only SHOULD raise the TPS) also exposes binaries at the newest TPS: the unpinned-runner (d) row admits revoked R7 as a C2 policy root. | computed D-A04 (from reviewer B's reproduced matrix) | NEW (D) → LOW (wording of an owner option) | restate as "compiled TSS older than the newest TSS" |
| RV3-L7 | `.governance-runtime/migration` is a tracked file under an ignored directory. `git ls-files -ci --exclude-standard` lists it, and the common "untrack ignored files" idiom removes it from every later clone. The result is `PARTIAL(occupation)` for every RoT-1 clone (availability), and one of the two adoption occupations is lost; P3r3 ablation L3A shows it is needed when residue exists. | executed D-A07 | NEW (D) → LOW | ignore-rule negation or non-ignored path; doctor; test |
| RV3-L8 | SV-6 accepts a signature only from a key not revoked in the effective root. Root N+1 removing a trust-state, `release-final` or other threshold-1 key therefore invalidates every honest statement that key signed, including the TSS an anchor names, and anchored machines drop to `BELOW_ANCHOR` (C0). `05` §9 lists re-attestation only for `release-final` finals, not for trust-state history or other purposes. | design D-A16 | NEW (D) → LOW (availability; `05` §8 permits re-signing) | playbooks re-sign retained statements before root N+1; test |

## INFO

| ID | Statement | Origin → adjudication |
|---|---|---|
| RV3-I1 | The acting role remains caller-declared (V-L5). ROLES `level_at_most` ceilings bind honest declarations only; trust gates do not depend on role. D-A06 shows the legacy binary likewise accepts a caller-declared `decide --by owner`. | RV3-B-I1 → CONFIRMED INFO |
