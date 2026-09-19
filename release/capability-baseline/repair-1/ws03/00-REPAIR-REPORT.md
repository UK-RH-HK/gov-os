# WS-3 repair report: repair iteration 1, round 1 (P2-AR-0016)

| | |
|---|---|
| Run | P2-AR-0016, role `capability-repair`, model Claude Opus 5 (1M context), `claude-opus-5[1m]` |
| Handoffs | P2-HO-0010 (common protocol), P2-HO-0013 (WS-3) |
| Branch / base | `phase2/repair-1-ws03` from `c6b60bc760a0bb42907f74210fd9e644a420851a` |
| Work commits | `76a3ad7` (main repair), `34aa810` (consumer prechecks, receipt kind, plugin ping G0, contradiction package), `a8c1dfb` (human-only triggers, repository-sourced anchor refusal, role doc notes), then the commit that adds this report and `evidence/` |
| Classes | BC-P2-08, BC-P2-09, BC-P2-10, BC-P2-12 (answer side), BC-P2-18 (resolution rules), BC-P2-45, BC-P2-49 |
| Claims | All seven: `REPAIRED_CLAIMED` for the WS-3 share. BC-P2-09, -12 and -18 also have acceptance lines that other workstreams complete; those are listed in §9 as integration points. |

**Status of these claims.** They come from the builder, and the evidence is regression evidence only (Contract v3 O3). Nothing here says a class is accepted, verified or closed. That decision belongs to the independent verifiers.

---

## 0. Evidence index and regression

| What | Where | Result at the final code (`a8c1dfb`) |
|---|---|---|
| `cargo test --lib` | `evidence/REGRESSION-lib.out` | **53 passed, 0 failed** |
| `cargo test --test certification` (includes `section6.rs`, the §6 derivation) | `evidence/REGRESSION-certification.out` | **91 passed, 0 failed**: the 79 base tests plus 12 new tests in `ws03.rs` |
| R1 held-out suites, all four rounds, run **unedited** (a `cmp` line proves each copied file is byte-identical) | `evidence/R1-HELDOUT-RERUN-candidate-final.out`, baseline `evidence/R1-HELDOUT-RERUN-base-c6b60bc.out`, runner `evidence/r1_heldout_rerun.sh` | base: **110 passed / 12 failed**; candidate: **109 passed / 13 failed**. The only change is `hv_a_derivation::a1` (see §0.1). The other 12 failures are identical at base and candidate. |
| hv_a::a1 detail (unedited, plus a derived copy with the scale pins printed instead of asserted) | `evidence/R1-HELDOUT-hv_a-a1-detail-final.out`, copy `evidence/hv_a_derivation_unpinned_ws03.rs.txt` | The unedited test fails only on its pinned tree size, 84 files / 740 fns, against a measured 86 / 846. The census itself reports **0 violations in every §6 activity**. |
| Named checks (a discriminating reimplementation of every audit line these classes name) | `evidence/ws03_named_checks.py`; base run `probes/ws03-named-checks.base-c6b60bc.out`; candidate run `probes/ws03-named-checks.candidate-final.out` | base (negative control): **35 of 36 FAIL**; candidate: **37 of 37 PASS** |
| Audit-of-record probes, run unedited against the final binary | `probes/final-unedited/*.out` (runner `evidence/rerun_named_probes.sh`) | see each class. Most stop at setup, for reasons §0.2 explains. |
| The same probes with a role-declaring adapter | `probes/final-roleshim/*.out` (adapter `evidence/gov-role-shim.sh`) | see each class |
| Derived G0 guard matrix (O5): the same matrix with roles declared | `evidence/derived-probes/O5-G0-guard-matrix.derived.py`, `probes/final-derived.O5-G0-guard-matrix.out` | Under FREEZE_WRITES only `pause` and `freeze-writes` mutate. Under PAUSE only allow-listed commands mutate. |
| Owner-side reference signer. **Test material only**, with a published seed. | `evidence/hc_owner.py` | used by the named checks |

The `probes/after-*` directories and `R1-HELDOUT-RERUN-candidate.out` are the same runs at `34aa810`. They are kept because their results match the final runs. The final and earlier probe outputs differ only in session IDs, paths, and one timing-dependent `[MUTATED]` marker on `gate present` under PAUSE, which is an allow-listed command.

### 0.1 Why `hv_a::a1` changes, and why it is not an R1 regression

`hv_a_derivation::a1` walks the product tree independently and then asserts two scale pins: 84 source files and 740 functions, the size of the tree AR-0033 certified. This repair adds two modules (`t2.rs`, `human_channel.rs`) and functions elsewhere, so the pin cannot hold for any repair that adds code. The same census with only the two pins printed (`evidence/R1-HELDOUT-hv_a-a1-detail-final.out`) derives every §6 activity and finds **0 violations**:

- human_gate_create: 37 derived, 34 writers, 1 exempt
- human_gate_approve: 1 derived, 1 writer
- release_certification: 2 derived, 1 writer
- trust_policy_mutation: 7 derived, 1 writer
- privileged_plugin_acquisition: 9 derived, 2 writers
- floor_lower_or_reset: 3 derived, 1 writer
- present_below_floor_release_as_current: 1 derived, 1 writer

The other nine hv_a tests, and every hv_b, hv_c and hv_d test, pass unchanged. No file under `runtime/src/srr/**` differs from base (`git diff c6b60bc -- runtime/src/srr` is empty).

### 0.2 Why most audit probes cannot run to completion unedited

The audit-of-record harnesses assume three behaviours that these classes remove:

- `gov init` and later setup steps ran with no role, relying on the old default `orchestrator` role. BC-P2-08 refuses this now: `AUTHORITY_DENIED`, cause `ROLE_UNDECLARED`.
- Fixture gates were created with only a question. BC-P2-49 refuses this now: `GATE_PACKAGE_INCOMPLETE`.
- Human answers were relayed with `gov decide --by owner`. BC-P2-10 refuses this now: `HUMAN_ANSWER_UNAUTHENTICATED` or `HUMAN_CHANNEL_UNAVAILABLE`.

Run unedited, most of them stop at those steps (see `probes/final-unedited/`). The refusal lines are themselves after-evidence, for example `S0-E1-01`, `E1.b3.a` and `X2-L3-*`.

Two further evidence sets fill the gap:

- `probes/final-roleshim/` uses an adapter that only declares `--role orchestrator` where the probe declared no role.
- `ws03_named_checks.py` reproduces each named check's scenario and PASS criterion. It adapts only the legitimate paths the repair changed: roles are declared, gates carry a complete package, and a real human answer is an owner-signed document. The base binary is its negative control, and every named line FAILs there.

---

## 1. BC-P2-08: role resolution and G0 guard coverage

**Requirement** (repair-delta §BC-P2-08; Contract v3:364, :173-174, :793; framework §23, §74):

- Every command evaluates authority against the role the caller declared. This includes `init` and every adopt or migrate stage.
- An undeclared invocation has no privileged authority.
- Every command that writes has a declared authority class.
- Nothing mutates under FREEZE_WRITES or PAUSE except commands on an explicit recovery allow-list.

**Changes**

- `runtime/src/authority.rs` (rewritten): role resolution is one process-wide decision.
  - `resolve_acting_role(flag)` resolves in this order: `--role` flag, then `GOV_ROLE`, then *undeclared*. `ActingRole` records the `RoleSource`.
  - `install_acting_role` stores the role in a `OnceLock`. A conflicting re-install is refused with `ROLE_CONFLICT`.
  - Every `Project::open` then uses `default_role_id()`. This covers the Projects that `init`, `adopt` and `migrate` open internally, which is how the first install batch is covered without editing `init.rs` or `adopt.rs`.
  - `UNDECLARED_ROLE = "undeclared"` carries L0.
  - `level_of` maps a declared L5 role (`human`) to L0, because a role claim is not the human.
  - `require` refuses with `AUTHORITY_DENIED`. `details.cause` is one of `ROLE_UNDECLARED`, `HUMAN_ROLE_CLAIM` or `LEVEL_TOO_LOW`, each with remediation text.
  - `require_with_embedded_kernel` evaluates authority for repositories with no installed kernel (first `init`, pre-install adopt stages) against the kernel embedded in the binary.
  - `required_level` checks three sources in order: installed policy, the embedded AUTHORITY_POLICY, then L3 as a fail-safe.
- `runtime/src/project.rs`: `Project::open` takes its role from `authority::default_role_id()`. The old default `orchestrator` is gone.
- `runtime/src/orchestration/control.rs`, **G0**:
  - `COMMAND_GUARDS` classifies all **111** CLI labels by effect (`Read` / `Write`), authority class and scope. 14 labels are `Outside`: machine-trust and canonical-repository tooling, each with a stated reason.
  - `g0(p, label)` refuses an unclassified label (`G0_UNCLASSIFIED`).
  - It refuses a write under FREEZE_WRITES or PAUSE unless the label is on `FROZEN_ALLOW_LIST` or `PAUSED_ALLOW_LIST`. Each entry states its reason. The lists hold `pause`, `freeze writes`, `cancel agents`, `resume`, `cit rollback` and `telemetry emit`, and PAUSE also allows `gate present`.
  - It evaluates the authority class for the declared role.
  - When the kernel is untrusted, the more fundamental `KERNEL_TAMPERED` refusal is reported. `kernel override` is exempt, because it exists to remediate that state.
  - `guard_write` now also calls `guard_emergency_state`. Refusals are typed and carry the allow-list in their details.
- `framework/policies/AUTHORITY_POLICY.yaml` adds the missing classes: `record_audit` L0, `replan_tasks` L2, `compile_context` L0, `regenerate_heldout_set` L3, `generate_adapters` L2, `generate_tool_registry` L2, `emit_telemetry` L0, `adoption_plan` L3, `adoption_review` L0.
- `framework/roles/ROLES.yaml` gains documentation comments only: undeclared = L0, and L5 is never conferred by declaration.
- `cli/src/main.rs` (semantic owner):
  - `declared_role(cli)` resolves the role and refuses `ROLE_CONFLICT` when `--role` and `GOV_ROLE` disagree.
  - `run()` starts with `install_acting_role(declared_role(cli)?)?; g0(cli)?;`.
  - `g0_label(&Cmd)` gives every subcommand its label.
  - `open_project` no longer passes a role.
  - `--by` on `decide`, `update`, `cit approve|reject` and `memory select` defaults to the acting role, not `human`.
  - The adopt review and verify role flags are now `Option`.

**Product checks and tier.** `control::g0` runs on every invocation, before dispatch (G0). `authority::require` runs at each operation. Unit tests `labels_are_unique_and_allow_lists_name_classified_writes` and `every_authority_class_exists_in_the_kernel_authority_policy` enforce the classification. The certification test `every_cli_command_label_is_classified_by_g0` scans every CLI literal.

**Probes before and after**

| Line (source) | Base | Final |
|---|---|---|
| AC16-X2 `X2-E1-undeclared-role-is-not-orchestrator` | FAIL | PASS (`AUTHORITY_DENIED`), named check |
| AC16-X2 `X2-E1-init-honours-declared-role` | FAIL | PASS: `--role` and `GOV_ROLE` evaluate identically |
| alpha-r `S0-E1-01` init with an undeclared role | FAIL | PASS: nothing installed. The unedited `alpha-r.S3-S4` run also shows it refused. |
| alpha-r `S3-S4` R2 adopt stage as L0 | FAIL | PASS (`AUTHORITY_DENIED`) |
| gamma-r `E1.b2` census: replan / heldout-starter / adapters / tool registry with no class | FAIL | PASS: classified and refused for L0 with no mutation |
| epsilon-r `O5-G0` freeze-writes / pause | FAIL: mutations | PASS: `{"mutated": []}` outside the allow-list. The derived matrix agrees. |
| epsilon-r `O5-G0` L0 `init --force` | FAIL | PASS (`AUTHORITY_DENIED`) |
| epsilon-r `O5-G0-focus` (unedited) | commands mutated under FREEZE | every command `FROZEN` (`probes/final-unedited/epsilon-r.O5-G0-focus.out`) |

**Tests.**

- `ws03::an_undeclared_invocation_carries_no_privileged_authority_anywhere`
- `ws03::g0_freeze_and_pause_refuse_every_write_outside_the_listed_recovery_operations`
- `ws03::every_cli_command_label_is_classified_by_g0`
- Unit tests in `authority.rs` and `control.rs`

**Limits.**

- The declared role is still a claim (D-0007 T5). Whether the OS binds *agent* L0–L4 identity is **OD-P2-01** and out of scope. This repair makes the declared role the one that is consistently evaluated, gives an undeclared invocation L0, and gives a declared `human` role L0 as well.
- `init.rs` and `adopt.rs` were not edited. They are covered through the process-wide role. See §9 for their follow-up.

---

## 2. BC-P2-09: the T2 binding primitive

**Requirement** (Contract v3:365, :427, :675; D-0007 T2 and rule 2; ARCH-0003 §8):

- A T2 fact is honoured only when it provably results from the OS operation. T2 facts are: gate presentation and answer, decision, CIT state, plugin registration.
- Lower-trust writes to OS-written state are detected and refused.

**Mechanism** (`runtime/src/t2.rs`, new module; its module documentation is the API contract):

- A seal is HMAC-SHA256, algorithm id `hmac-sha256/t2-v1`. It is computed over the record's canonical content, the operation name and the time.
- The key is a **machine binding key** held in protected machine state outside every repository: `<state_root>/t2-binding/key.json`, 32 random bytes, created race-free with mode 0600.
- The seal is stored in the record itself, in field `os_binding`, so no sidecar store is needed.
- `verify_record` returns one of:
  - `Verified`: the only honoured state
  - `Unsealed`: hand-written, legacy, or written by code that has not adopted the primitive
  - `Broken`: modified after sealing
  - `Foreign`: sealed by another machine's key
  - `KeyUnavailable`
- `require_verified` refuses with `T2_UNBOUND`. The details carry the binding, record and path.

**What WS-3 seals and consumes**

- **Gate records**: sealed by `create`, `create_system`, `present`, `acknowledge`, `answer` and `revoke` in `gates.rs`.
- **Decision records** derived from an answer: sealed by `answer`, and re-sealed when a revoke sets them to REJECTED.
- **Consumers**:
  - `gates::verified_answer(_in)`, which re-verifies a human answer against the owner signature at use time
  - `task_gate_authorisation`, `human_approval_for`, `verified_decision` and `require_honoured_answers`
  - the policy-exception path (`policy.rs`: the governing decision must be `Verified`)
  - `gate list` and `gate show`, which report unverified records separately
- `answer()` refuses an unbound gate with `GATE_NOT_PRESENTED`, cause `T2_UNBOUND`. A forged presentation flag is therefore not a presentation.
- **CIT answer consumption at the product surface**: `cit approve` and `cit execute` call `gates::require_honoured_answers` for the CIT's gate (`main.rs::cit_gate_precheck`), and `update --apply` does the same for its `framework_update` gates.

**What the seal proves, and what it does not**

- A process that can write the repository but cannot read machine state cannot produce a `Verified` record. This is the lower-role and record-forgery attack in A0-E1-02, A0-L3-02 and A0-F4-02.
- A process with the operator's full OS privileges can read the key. Against that attacker the seal is detection-grade, not proof. For that reason the facts that must hold against it are bound to an owner signature (§3):
  - human answers
  - human-approval assertions
  - presentation evidence
- Agent resolutions have no owner signature. For them, the most consequential gates are protected by a use-time rule that does not depend on the seal: human-only triggers, §6.

**Probes before and after**

| Line | Base | Final |
|---|---|---|
| delta-r `L3.b1.6` presentation flag set by file edit | FAIL | PASS (`GATE_NOT_PRESENTED`) |
| delta-r `L3.b5.8`, AC16-X2 `X2-L3xE1` and `X2-L3xK2`: forged gate/decision files carry a CIT to COMMITTED | FAIL | PASS (`T2_UNBOUND` at approve and execute; the CIT is not committed). Shown in the named check and in the **unedited** `synthesis.AC16-X2` run. |
| delta-r `L3.b4.o2` re-binding an answered gate to another CIT by editing records | FAIL | PASS (`T2_UNBOUND`) |
| AC16-X2 `X2-E1xG2` worker writes invisible at task close | FAIL | **still FAIL**: close side, WS-5 (§9, IP-1) |
| AC16-X2 `X2-L3xU` and delta-r `L3.b5.10`: suite reports forged approvals | FAIL | **still FAIL**: suite and doctor side, WS-2 (§9, IP-5). The API `t2::audit` exists. |
| delta-r `L3.b5.9` mutation scope sees forged records | FAIL | **still FAIL**: WS-5 (IP-1) |
| gamma-r `F4.b2.x` and `FRESH.4` registry forgery | FAIL | **still FAIL**: registry side, WS-7 (IP-6) |

**Tests.**

- `ws03::hand_written_gate_and_decision_records_are_not_honoured`
- `ws03::cit_approval_consumes_only_honoured_gate_answers`
- `repair2::cit_approval_derives_only_from_an_answered_gate`, updated per §10
- `t2.rs` unit tests: RFC 4231 HMAC vectors, a seal survives save and load, a seal breaks on any edit, a foreign key yields `Foreign`

**Limits.**

- The key is readable by the operator's account (stated above).
- Records sealed on one machine are `Foreign` on a clone; this is deliberate.
- CIT state records, the plugin registry, and the task-close and suite consumers belong to other workstreams (§9).

---

## 3. BC-P2-10: human answers and presentation from an authenticated human channel

**Requirement** (Contract v3:676, :679, :851; D-0007 rule 2; ARCH-0003 §8; OWNER-DIRECTIVE-0004; the authority class is fixed by OWNER-DECISION-0006 req. 2):

- Human answers, human-approval assertions, and the evidence that a gate reached the human must come from a channel the acting agent cannot operate through any of these:
  - CLI arguments
  - the environment
  - role claims
  - defaults
  - repository files
  - plugins
  - model output

### 3.1 Mechanism HC-1: owner-signed documents against the administrator-provisioned anchor

The module is `runtime/src/human_channel.rs`. Its module documentation states the design; this is a summary.

1. **Authority.** Ed25519 keys of a `human-gate` role, held by the product owner **off the agents' machine**. `gov` has no signing code and no key. The threshold is taken from the delegation.
2. **Anchor** (`human_channel::anchor`).
   - On a machine with a Signed Release Root, the anchor is the trusted root's delegation of the `human-gate` role, obtained through `srr::verifier::trusted_root` and verified with `Root::verify_role`. This is the same administrator-provisioned anchor that governs releases and break-glass.
   - On a machine with no release root, the anchor is a standalone self-signed `human-channel-anchor` document. It is installed in protected machine state by `gov trust human-channel --provision <file>`, and only while `HUMAN_GATE_POLICY.human_channel.standalone_anchor_when_unprovisioned` is true. That policy key is strengthen-only: a project may set it false, never true.
   - Provisioning is refused in each of these cases:
     - below floor (`guard_effect(TrustPolicyMutation)`)
     - for an anchor that is repository content (`HUMAN_CHANNEL_ANCHOR_FROM_REPOSITORY_REFUSED`, the same rule `gov trust provision` applies)
     - for an anchor that is not self-signed at threshold (`HUMAN_CHANNEL_ANCHOR_INVALID`)
     - on a machine with a release root (`HUMAN_CHANNEL_SRR_GOVERNS`)
     - on a machine that already has an anchor (`HUMAN_CHANNEL_ALREADY_PROVISIONED`); the product never re-anchors
   - Once a release root exists, a standalone anchor is ignored.
3. **Rendering.**
   - `gov gate present <id>` renders the decision package, records `presented_at`, `presented_by` and `presentation.package_sha256`, seals the record, and writes the package to the channel outbox.
   - This **does not** set `presented_in_chat`. Output that an agent can capture is not evidence that a human saw it.
4. **Answer.**
   - The owner signs a `human-gate-answer` document. It binds: product, gate id, the gate's OS-issued `gate_instance` (a new UUID for every raise), the SHA-256 of the exact package the OS rendered, the option, `answered_by`, a nonce, `issued` and `expires`.
   - The document is placed in the inbox `<state_root>/human-channel/inbox/`, or passed with `--answer-file`. The path carries no authority; only the signature does.
   - `gov decide <id> --option X` runs as the L3 `answer_gate` relay. It verifies the document and refuses anything that is not a valid answer to this package. The document must not be:
     - missing (`HUMAN_ANSWER_UNAUTHENTICATED`, listing what was rejected)
     - unsigned, signed by the wrong key, or below threshold
     - expired
     - replayed (each nonce is single-use)
     - bound to another gate, instance or package
     - for an option the package does not offer
     - inconsistent with the option given on the command line (`HUMAN_ANSWER_MISMATCH`)
5. **Presentation evidence.**
   - `presented_in_chat` becomes true only on an owner-signed answer, or on an owner-signed `human-gate-receipt` over the same digest (`gov gate present <id> --receipt-file|--receipt-inbox`).
   - The record's `presentation_receipt.kind` is `answer`, `receipt` or `agent_resolution`. The last one is never a human receipt.
6. **Use-time re-verification.**
   - The exact signed envelope is stored, hex-encoded, in the gate and decision records (`human_approval_evidence`).
   - Every consumer that honours a human answer re-verifies it against the *current* anchor (`human_channel::reverify`, called from `gates::verified_answer_in`). The error is `HUMAN_ANSWER_UNVERIFIED`.
   - If the anchor is later rotated away from the signing key, the old answer is no longer honoured.
7. **Status.** `gov trust human-channel` reports:
   - the anchor
   - the inbox and outbox
   - exactly what a document must bind
   - the list of things that cannot produce an answer
   - the premise check `anchor_writable_by_invoking_account`

### 3.2 Trust argument against an agent process with the operator's OS privileges

| The attacker tries to | Result | Why |
|---|---|---|
| pass `--by human` or `--by owner`, `--option`, or rely on a default | `HUMAN_ANSWER_UNAUTHENTICATED` | an answer needs an owner signature; `--by` has no `human` default |
| declare `--role human` or `GOV_ROLE=human` | `AUTHORITY_DENIED` (`HUMAN_ROLE_CLAIM`) | a declared L5 role carries L0 |
| set `GOV_HUMAN_GATE_APPROVED=1` or similar | refused or ignored | env vars never create approval (existing SRR env refusal, unchanged) |
| hand-edit gate or decision records to ANSWERED or `human_approved: true`, or set `presented_in_chat` | not honoured (`T2_UNBOUND`, `GATE_NOT_PRESENTED`) | T2 seal (§2) |
| forge a T2 seal with the machine key it can read | a human answer is still not honoured | the stored human evidence is re-verified against the owner-key anchor at use, and the agent has no owner key |
| forge an agent resolution, sealed with the stolen key, on a human-only gate | not honoured (`GATE_STATE_INVALID`) | use-time human-only-trigger rule (§6), independent of the seal |
| sign its own answer with its own key | `HUMAN_ANSWER_UNAUTHENTICATED` | the key is not in the anchor |
| replay an owner-signed answer onto another gate, a re-raised gate, an edited package or another option | refused | the document binds gate, `gate_instance`, package digest and option |
| replay the same answer twice | refused | the nonce is consumed, and the answer expires |
| install its own anchor through the product: from the repository, not self-signed, over an existing anchor, or while a release root governs | refused | see §3.1 item 2 |
| install its own anchor on a **fresh machine with no release root and no anchor** (TOFU) | **possible** | out of envelope, exactly as for `gov trust provision` (ARCH-0003 §5: bootstrap authenticity comes from the admin installation boundary). See §3.3. |
| overwrite the anchor or root files in machine state directly | **possible if the account can write them** | out of envelope (ARCH-0003 §1: the administrator boundary is uncompromised). The same holds for the release root and break-glass. `status` reports `anchor_writable_by_invoking_account`. |
| use plugins or model output | cannot sign | no owner key |

### 3.3 Premise, and a note on OD-P2-02

HC-1 is exactly as strong as the owner-accepted R1 break-glass mechanism. It uses the same authority class, the same primitives, and the same premise. The residual exposure is the same one R1 has at bootstrap: an unprovisioned machine is anchored by whoever provisions it first.

Whether an unprovisioned machine may admit privileged material is the owner's pending **OD-P2-02**, which is out of this run's scope. HC-1 is built so either answer is a one-key change:

- If the owner rules that unprovisioned machines may not admit such material, set `HUMAN_GATE_POLICY.human_channel.standalone_anchor_when_unprovisioned: false` in the kernel. Human answers then come only from a Signed Release Root's `human-gate` delegation.
- A project can already make that choice for itself.

**This does not block the class.** The owner's answer only changes that one kernel key.

**Probes before and after**

| Line | Base | Final |
|---|---|---|
| AC16-X2 `X2-L3-fabrication-default`, `-role-human` and `-env-GOV_ROLE` (which cover delta-r `L3.b5.2` and `L3.b5.3`) | FAIL | PASS (`answer.by_kind: null`) |
| delta-r `L3.b5.1` default relay | FAIL | PASS (`HUMAN_CHANNEL_UNAVAILABLE` or `HUMAN_ANSWER_UNAUTHENTICATED`) |
| delta-r `L3.b2.2` and `L3.b2.3` rendering into JSON or `continue` counted as presented | FAIL | PASS (`presented_in_chat: false`) |
| delta-r `L3.b2.5` receipt required (adapted: the literal check only looks for a field) | FAIL | PASS: only an owner-signed receipt marks presentation |
| delta-r `L3.b5.11` `memory select --role human` records human approval | FAIL | PASS (`AUTHORITY_DENIED`). The API for the memory-select writer is in IP-8. |
| HC-1 positive: an owner-signed answer is recorded as the human's, with presentation evidence | n/a | PASS |
| delta-r `L3s.2` intent router proposes `--by human` | FAIL | **not in WS-3 files** (`intents.rs`, IP-3) |
| epsilon-r `Q1.6-8` upstream export approval | FAIL | **not in WS-3 files** (WS-11: `gates::human_approval_for`, IP-9) |

**Tests.**

- `ws03::human_answers_come_only_from_the_owner_signed_channel`, which covers:
  - CLI, env and role claims
  - an impostor key
  - another package, instance or gate
  - a replayed nonce
  - expiry
  - an option not offered
  - an unsigned document
  - an in-repository anchor, a non-self-signed anchor, and a re-anchor attempt
- `ws03::presentation_is_recorded_only_from_an_owner_signed_receipt`

**Limits.** The premises of §3.3. An owner-side tool that produces signed documents is outside the product. `hc_owner.py` is only a test reference for the document format.

---

## 4. BC-P2-12 (answer side): task-blocking gate semantics

**Requirement** (Contract v3:678; framework §53):

- Blocked work becomes runnable only on an answer that authorises it.
- It returns to blocked on revoke or withdraw.
- It cannot complete while the gate is unanswered.
- A reference to a missing gate blocks.

**Changes** (`gates.rs`):

- Every option records `authorises_blocked_work`. The default is true for id `A` only, and the gate package states it.
- `answer()` moves the tasks the gate blocks as follows:
  - an authorising answer: WAITING_HUMAN → READY
  - a non-authorising answer: WAITING_HUMAN or READY → BLOCKED
- `revoke()` withdraws the gate:
  - derived decisions become REJECTED and are re-sealed
  - a linked CIT returns to SIMULATED
  - tasks in WAITING_HUMAN, READY, IN_PROGRESS or CLAIMED become BLOCKED
- **API for the DAG and close side:** `task_gate_authorisation(_in)` returns `Authorised`, `Pending`, `Declined`, `Withdrawn`, `Missing` or `Unverified`. It is the one question the DAG and task close should ask.

**Probes.** delta-r `L3.b4.t2` (declining answer) and `L3.b4.t3` (revoke) change from **FAIL at base to PASS**. `L3.b4.t4` passes at both. `L3.b4.t5` (missing gate) and `L3s.1` (close while pending) are the DAG and close side, WS-5 (IP-1, IP-2).

**Tests.** `ws03::blocked_work_is_released_only_by_an_authorising_answer`.

---

## 5. BC-P2-49: the decision package is enforced

**Requirement** (Contract v3:662-672):

- Every package field has substantive content.
- There is at least one option.
- The answer is one of the offered options.
- The gate states the exact permitted next actions.

**Changes**

- `gates.rs`:
  - `validate_package` refuses with `GATE_PACKAGE_INCOMPLETE`. The error lists every field that is missing or not substantive, judged against `HUMAN_GATE_POLICY.package_non_substantive_values` (for example `not assessed`, `tbd` or `?`).
  - It requires at least one option with a unique id.
  - `next_actions` derives the exact commands for this gate and its options; there are no placeholders.
  - System-raised gates get framework-authored content per trigger (`complete_system_package`, from `HUMAN_GATE_POLICY.system_gate_package`) only for fields the raising code did not supply.
  - An answer outside the offered options is refused with `GATE_OPTION_INVALID`. This applies to both agent and human answers, and a signed answer is checked the same way.
- `routing.rs`: the budget gate carries a complete package.
- `human-gate.schema.json` 1.1.0.

**Probes.** delta-r `L2.min.1`, `L2.b4.min`, `L2.b10.min`, `L2.b4.answer2`, `L2.cit.b10` and the budget gate (`L2.budget.complete`) all change from **FAIL at base to PASS**.

**Tests.** `ws03::the_decision_package_is_enforced`.

---

## 6. BC-P2-18 (resolution rules): agent resolution only within policy

**Requirement** (Contract v3:657-660, :1103; framework §50): agent resolution only on assessed impact, reversibility and confidence that do not rest solely on the resolver's own declaration.

**Changes** (`gates.rs::answer`, `HUMAN_GATE_POLICY.agent_resolvable_when`). An agent answer requires all of the following:

- an **L3+ acting role resolving as itself** (`--by` must equal the acting role)
- a **complete assessment**: an unassessed radius, reversibility or confidence counts against resolution (`require_assessed`)
- radius ≤ R1 (for a CIT-linked gate, the larger of the declared and simulated radius), confidence ≥ 0.8, and reversible
- an assessment made **by another session or by the OS** (`independent_assessment`; the gate records `assessment.source` and `declared_by`)
- a recorded **rationale**

Two further rules:

- **Human-only triggers** (framework §51) are never agent-resolvable: `framework_update`, `destructive_migration`, `privilege_elevation`, `kernel_integrity_override`, `tool_install`, `budget_threshold`. This list is the kernel floor `gates::HUMAN_ONLY_TRIGGERS`. `HUMAN_GATE_POLICY.human_only_triggers` may add triggers but never remove them.
  - At answer time the answer is refused.
  - At use time `verified_answer_in` refuses an agent-resolved record of such a gate, even when its seal verifies.
- An agent resolution records `presentation_receipt.kind: agent_resolution` and `by_kind: agent`. It is never a human approval.

The precedence rules make every `agent_resolvable_when` key strengthen-only.

Contradiction detection belongs to WS-4. WS-3 provides the `contradiction` system package, so `create_system` with trigger `contradiction` yields a complete package.

**Probes.** delta-r `L1.b2.self`, `L1.b2.neg.no-reversibility`, `L1.b4.1` and `L1.b2.1.independent` change from **FAIL at base to PASS**. The detection side does not change: `L1.b1.6` and zeta-r `W3-r3-conflict-triggers-handling` and `W3-r3-duplicate-id-conflict-handled` still FAIL in `probes/final-*`. They belong to WS-4 and WS-5 (IP-4).

**Tests.** `ws03::agent_resolution_needs_an_assessed_and_independent_assessment`, including the human-only trigger case, and the updated `repair.rs` and `repair3.rs` (§10).

---

## 7. BC-P2-45: project overlays bound by policy precedence

**Requirement** (Contract v3:134-138, :693-699, :522; D-0007 rule 3): every project-level policy input goes through POLICY_PRECEDENCE. Floors may be raised, never lowered, and every refused weakening is reported.

**Changes**

- `policy_precedence.rs`: `evaluate_overlay` returns `OverlayVerdict {effective, applied, refused}`.
  - Empty maps are skipped.
  - A value equal to the kernel value is accepted.
  - A refused key is replaced by its kernel value, or deleted.
- `policy.rs`:
  - `PROJECT_POLICY.yaml` is evaluated against the kernel overlay template.
  - `MODEL_ROUTING_OVERRIDES.yaml` is evaluated against the kernel values: task-class minimum tier, role minimum tier and default reasoning.
  - Results are recorded in `applied_overrides`, `refused_overrides` and `PolicySet.effective_overlays`.
- `project.rs::project_policy()` returns the *enforced* PROJECT_POLICY. Every reader therefore sees the enforced value, including the `dag.rs` readiness read.
- `routing.rs`:
  - `effective_overrides` is the entry point.
  - `tier_for_class` is raise-only.
  - The reasoning of a role override is raise-only.
  - `DEFAULT_CLASS_TIER` is T2.
- `POLICY_PRECEDENCE.yaml`:
  - rules for `PROJECT_POLICY.*`: readiness gating strengthen-only, staleness floor ordered, the listed descriptive keys overridable, the catch-all immutable
  - rules for `MODEL_ROUTING_OVERRIDES.*`: tier floors, reasoning floor ordered, providers and preferences overridable, the catch-all immutable
  - rules for the new HUMAN_GATE keys
- `model-routing-overrides.schema.json` 1.1.0 (enums). `ENFORCEMENT_MAP.yaml` entries for the new keys.

**Probes.** delta-r `M1.floor.1` (security stays T3), `M2.b1.4` (reasoning stays extra_high) and `M3.b1.floor` (orchestrator stays T3/high), and gamma-r `H3.b5` (the readiness switch is refused and reported, and the task is not runnable), all change from **FAIL at base to PASS**.

**Tests.** `ws03::project_overlays_may_raise_floors_but_never_lower_them`, and a unit test in `policy_precedence.rs`.

---

## 8. APIs that other workstreams must call

All of these are public, and each has doc comments in its module.

| Need | API |
|---|---|
| Acting role (BC-P2-08) | `authority::resolve_acting_role`, `install_acting_role`, `installed_acting_role`, `default_role_id`, `is_declared`, `require(p, class)`, `require_with_embedded_kernel(role, class)` for repositories with no installed kernel, `level_of`, `required_level` |
| G0 classification | `orchestration::control::{COMMAND_GUARDS, command_guard, g0, FROZEN_ALLOW_LIST, PAUSED_ALLOW_LIST}`. **Every new CLI label must be added to `COMMAND_GUARDS`,** or it is refused as `G0_UNCLASSIFIED`. |
| T2 writers | `t2::seal_record(&mut rec, op)` or `t2::seal_value(&mut v, body, op)`, called immediately before persisting |
| T2 consumers | `t2::verify_record`, `verify_value`, `verify_file`, `require_verified` (→ `T2_UNBOUND`) |
| Task close (G2) | `t2::classify_path(root, rel)`: a changed path under an OS-managed prefix is an OS write only when `Verified` |
| Suite / doctor | `t2::audit(p)` (open T2 records no OS operation produced) and `gates::unverified(p)` |
| Gate answers | `gates::verified_answer(p, id)` → `VerifiedAnswer {option, authorises_blocked_work, by_kind, answered_by, decision, human_evidence}`; `require_honoured_answers(p, ids)`; `answered_gates_for_trigger(p, trigger)` |
| Blocking semantics | `gates::task_gate_authorisation(p, gate)` or `task_gate_authorisation_in(p, store, gate)` |
| Human approval of a subject | `gates::human_approval_for(p, gate, subject_sha256)` |
| Decisions | `gates::verified_decision(p, id)` (T2-verified, ACTIVE) |
| System gates | `gates::create_system(p, fields)` with a `trigger`. Package content comes from `HUMAN_GATE_POLICY.system_gate_package`. `gates::human_only_trigger(p, trigger)` |
| Human channel | `human_channel::{anchor, status, find, verify_document, reverify, provision_standalone}` |
| Overlays | `policy_precedence::evaluate_overlay`, `PolicySet.effective_overlays`, `Project::project_policy()`, `routing::effective_overrides` |

## 9. Integration points (not implemented here: owned by other workstreams)

| IP | File / function (owner) | Exact change | Why / lines it completes |
|---|---|---|---|
| IP-1 | `orchestration/tasks.rs` close (WS-5) | Replace the `OS_MANAGED_PREFIXES` exemption with `t2::classify_path(&p.root, rel)`: a non-`Verified` change is a worker mutation (`MUTATION_SCOPE_VIOLATION`). Refuse close while `gates::task_gate_authorisation(p, task.human_gate)` is not `Authorised`. | BC-P2-09 `X2-E1xG2`, `L3.b5.9`, `E1.b3.d`; BC-P2-12 `L3s.1` |
| IP-2 | `orchestration/dag.rs` compute / replan (WS-5) | Readiness through `gates::task_gate_authorisation_in` (`Missing` and `Unverified` block). Keep reading readiness through `p.project_policy()`. | BC-P2-12 `L3.b4.t5`; BC-P2-45 `H3.b5` (already PASS through `project_policy`) |
| IP-3 | `intents.rs`, `status.rs` next_action (WS-5) | Stop proposing `--by human`. Propose `gov gate present` and the channel inbox instead (see `gov trust human-channel`). | BC-P2-10 `L3s.2` |
| IP-4 | `cit/mod.rs` authoritative gate and execute (WS-4) | Read answers only through `gates::verified_answer`. Create CIT gates with `create_system` so the OS assessment is recorded. Seal CIT state with `t2::seal_record`. Route undecidable contradictions to `create_system(.., {"trigger": "contradiction", ..})`. | BC-P2-09 (CIT state); BC-P2-18 `L1.b1.6`, `W3-r3-*` (the CLI precheck in `main.rs::cit_gate_precheck` covers the answer side today) |
| IP-5 | `verification/*` suite family and `doctor.rs` check (WS-2) | Report `t2::audit(p)` and `gates::unverified(p)` as findings. Include them in `inputs_hash` so a forged record invalidates green evidence. | BC-P2-09 `X2-L3xU`, `L3.b5.10` |
| IP-6 | plugin registry writer and reader (WS-7) | Seal registry entries with `t2::seal_value` and honour only `Verified` entries | BC-P2-09 `F4.b2.x`, `FRESH.4` |
| IP-7 | `update.rs`, `init.rs` (WS-8) | `update.rs`: replace the `answered_yes` field read with `gates::verified_answer`. The CLI calls `require_honoured_answers` before `--apply` today. `init.rs`: the process role is already honoured through `default_role_id()`, so no change is needed unless init opens a Project with a hard-coded role. | BC-P2-08/09 |
| IP-8 | `memory` select writer (WS-6) | Derive `human_approved` only from `gates::human_approval_for`, never from the role. The CLI already refuses `--role human` (L0). | BC-P2-10 `L3.b5.11` |
| IP-9 | `upstream` submit (WS-11) | Require `gates::human_approval_for(p, gate, packet_sha256)` | BC-P2-10 `Q1.6-8` |
| IP-10 | `adopt.rs` (WS-9) | Same as IP-7: use the resolution API. Stage roles are evaluated through G0 today. | BC-P2-08 |
| IP-11 | `docs/ARCHITECTURE.md` §4.8, `docs/COMMANDS.md` (unowned) | Document the new behaviour: role resolution and G0, `gov trust human-channel`, `gate present --receipt-*`, `gate show`, `decide --answer-file`, human-only triggers | documentation |
| IP-12 | `tests/certification/main.rs` | `mod ws03;` (additive, one line) | test registration |

**Additions to `cli/src/main.rs`, listed for integrators** (WS-3 is the semantic owner):

- `declared_role`, `g0_label`, `g0`, `cit_gate_precheck`
- the first lines of `run()`
- `Decide {option, by, rationale, answer_file, evidence}`
- `GateCmd::Present {receipt_file, receipt_inbox}`, `GateCmd::Show`
- `TrustCmd::HumanChannel {provision}`
- `--by` is `Option` on `update`, `cit approve|reject` and `memory select`
- the adopt role flags are `Option`
- the `update --apply` precheck
- `gate list` = `pending` + `unverified`

Any workstream that adds a subcommand must also add its label to `g0_label` and to `control::COMMAND_GUARDS`.

## 10. Existing builder tests changed, and why

The behaviour changes are intended, and no assertion was weakened.

| File | Change | Reason |
|---|---|---|
| `brownfield.rs`, `greenfield.rs`, `migration.rs`, `update.rs`, `failure_injection.rs`, `repair.rs` (several), `repair2.rs`, `repair3.rs` | `gov decide … --by owner` replaced by `ws03::human_decide` (an owner-signed answer through the channel) | BC-P2-10: `--by owner` is CLI metadata and no longer records a human answer. The tests keep their assertions about what the answer causes. |
| `failure_injection.rs`, `srr.rs` (positive gate create), `repair.rs` | gate creation supplies a complete package (`ws03::package`) | BC-P2-49: a question-only gate is refused |
| `repair.rs::authority_levels_are_enforced_on_executable_paths` | `--role human` is now asserted **refused** (`AUTHORITY_DENIED`). The agent-resolution case is raised by another session (`S-cc`) and carries a rationale. | BC-P2-08 / BC-P2-10: a role claim is not the human. BC-P2-18: independent assessment and rationale. |
| `repair2.rs::cit_approval_derives_only_from_an_answered_gate` | presentation by owner receipt. The edited-answer cases now expect `T2_UNBOUND` instead of `APPROVAL_STALE` / `GATE_DECLINED`, plus a new assertion that the CIT did not execute. | BC-P2-09: an edited record is refused before any answer field is read. This is stricter than before. |
| `repair2.rs::project_policy_cannot_weaken_constitutional_floors`, `repair3.rs::policy_exceptions_require_a_real_governing_decision` | the governing decision is produced by a gov-answered gate whose `decision_scope` names the exceptions. A hand-written decision is now asserted refused ("T2 binding"). The L4-approver case uses a real agent resolution. | BC-P2-09: "approved" is a T2 fact |
| `repair3.rs::lower_trust_inputs_cannot_manufacture_higher_trust_facts` | presentation by owner receipt | BC-P2-10 |

## 11. What this run did not do

- It did not implement agent L0–L4 credentials (OD-P2-01).
- It did not decide OD-P2-02 (§3.3).
- It did not edit `runtime/src/srr/**`, `init.rs`, `adopt.rs`, `tasks.rs`, `dag.rs`, `cit/**`, `doctor.rs`, `verification/**`, `intents.rs`, `status.rs`, `memory/**`, `upstream`, the registry, or docs. §9 records every point where these must call WS-3's API.
- It did not edit any file under `release/verification/`, `release/root-of-trust/`, `release/releases/`, `release/orchestration/phase-1/`, `release/capability-baseline/audit-0/`, another workstream's `repair-1/` directory, or the Contract v3 source.
- Audit probes were run unedited from `audit-0`. The adapters and derived copies are separate files in `evidence/` and are labelled as such.

## 12. Owner-decision questions

None block these classes. One question relates to OD-P2-02, which is already with the owner: *on a machine with no Signed Release Root, may the administrator-provisioned standalone human-channel anchor authenticate human answers (availability), or must human answers always come from a release root's `human-gate` delegation?* The current default is `standalone_anchor_when_unprovisioned: true`. Either answer is a change to one kernel key (§3.3).
