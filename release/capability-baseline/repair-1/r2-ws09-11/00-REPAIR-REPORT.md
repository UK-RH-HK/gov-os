# Repair 1, round 2, WS-9 + WS-11: builder report (run P2-AR-0030)

| Field | Value |
|---|---|
| Run | P2-AR-0030, role `capability-repair`, model Claude Opus 5 (1M context), `claude-opus-5[1m]` |
| Handoffs | P2-HO-0028, with P2-HO-0020 and P2-HO-0010 |
| Branch / base | `phase2/repair-1-r2-ws09-11` from `843d79c33e8a8db8b223611abc23d317edbc82a1` (the integrated round-1 tree; `product_code_digest b1ab1c8c…fbb1`) |
| Work commits | `8893829` (main repair), `609a8f7` (reviewer attribution across test-design re-runs), `23a76d2` (unit tests). Evidence and reports follow in separate commits. |
| Product identity at `23a76d2` | `product_code_digest 4a7b82608eb603526888c69bced01640b45f448b5e82f833c716c6f1d26d9b14`, `governed_state_digest 4981437f…227d` (unchanged) |
| Classes | BC-P2-34 (adoption side); the adopt host call sites (BC-P2-08: IP-10 / own IP-3; BC-P2-07: IP-WS02-18 / own IP-4); BC-P2-10 (export-approval use: IP-9 / own IP-2); ws06 IP-7 (migration) |
| Claims | See §0. Every claim is a builder claim. The evidence is regression evidence only (Contract v3 O3). |
| Owner decisions | None raised. OWNER-DECISION-P2-0001 (roles are adapter-declared) is applied as written. |

---

## 0. Claims

| Class / IP | Status | Product check that owns it |
|---|---|---|
| BC-P2-34, adoption side | `REPAIRED_CLAIMED` | These run in the adoption stages themselves: `adopt::check_actor` (A0–A11); `adopt::require_approved_artefacts` (A6, A8); the A7 computed verdict; A10 held-out authorship; A11. The adoption record is T2-bound (`adopt::load_baseline`). |
| BC-P2-08, adopt call sites (IP-10, own IP-3) | `REPAIRED_CLAIMED` (runtime side) | `identity::resolve_actor` and `adopt::stage_authority` run in every stage. `*_by(…, &Actor)` APIs are exposed for all stages. The CLI change is optional and is WS-3's (IP-R2-1). |
| BC-P2-07, host side at adopt (IP-WS02-18, own IP-4) | `REPAIRED_CLAIMED` (adopt host side) | G0 `scheduler::guard("adopt.migrate")` in A6 and A8. G4 `scheduler::tier_run` after a completed migration (A6) and after the memory build (A9). G5 (`RunOptions::new(G5)`, deep, recorded) is the A11 audit. |
| BC-P2-10, export-approval use (IP-9, own IP-2) | `REPAIRED_CLAIMED` (export use) | `upstream::resolve_export_approval` → `gates::human_approval_for(p, gate, subject_sha256)`. The export gate is raised at `upstream prepare`; `upstream submit` enforces the approval. |
| ws06 IP-7 (migration overlay operation) | done (migration side) | `migrations/M-4.1.5-4.1.6.yaml` (`set_overlay_rule`), with a unit test. The template rule itself is WS-6's file (IP-R2-2). |

---

## 1. BC-P2-34 (adoption side): independence from recorded authorship, bound to what was approved

### Requirement

Sources: repair-delta BC-P2-34; Contract v3 T1/T2/T3 :957-972 and O3 :783-785; adoption protocol §3, §10, §11 and §15; findings A0-T2-01 and A0-O3-01 (adoption part).

- Independence is established from recorded authorship: the role and session of the author, compared with the planner, executor and builder.
- Each independent stage (A5, A7, A10, A11) is performed by the kernel role designated for it.
- Execution and every independent verdict are bound to the exact artefacts approved. Changing the plan, map or tests after approval invalidates the approval or is refused.
- An A7 accept with 0 tests must be refused.
- A10's held-out tests come from the independent verifier. Builder tests are regression evidence only.
- A11 has an independence check.
- OWNER-DECISION-P2-0001 applies: roles are adapter-declared. They are bound to the *declared* role, consistently, and to T2-sealed approvals rather than free strings. No agent credentials are built.

### What changed

Files: `runtime/src/adopt.rs`, `runtime/src/migrations/{identity,planner,verify}.rs` and `framework/schemas/adoption-baseline.schema.json`. The module documentation of `adopt.rs` states the design.

**1. Actor = declared role + declared session**

Every stage resolves its actor through `identity::resolve_actor`:

- **Role.** The role is the process's acting role (`authority::installed_acting_role`, else `GOV_ROLE`): the one authority is evaluated against. A different role supplied by a caller is refused (`ROLE_CONFLICT`).
- **Session.** The session is the one declared to the process: the global `--session`, else `GOV_SESSION`, or `adopt review --reviewer-session` as the stage's own declaration. Two different declarations are refused (`SESSION_CONFLICT`).
- **Generated ids.** The CLI's generated fallback id is recognised as undeclared: the runtime checks the declaration itself (args, env, or an optional installed declaration).
- **No declared session.** A stage refuses with `ADOPTION_SESSION_UNDECLARED`. Authorship that is not recorded cannot establish independence. This closes alpha-r [N1], where one agent with no session flags got a fresh random id per stage.
- **Authority.** Authority for the stage's class is evaluated inside the runtime for the declared role (`stage_authority`: installed policy, or the embedded kernel before the first install). This is the same decision G0 makes, now held for every caller.

**2. Authorship log**

- Every stage records its author in the adoption record `authors`: group (planner / executor / memory builder / independent), role, session, where each came from, and the stages performed.
- Within one adoption, a session keeps the role it first acted under (`ADOPTION_ROLE_INCONSISTENT`): one agent session, one adapter-declared role.

**3. Designated independent roles**

- `adopt::DESIGNATED_ROLES` binds each independent stage to its kernel role:
  - A5 → `migration-reviewer`
  - A7 → `migration-verifier`
  - A10 → `memory-verifier`
  - A11 → `independent-auditor`
- The declared role must be exactly that role. The session and role must not be ones that authored any planner, executor or memory-builder stage of this adoption.
- Refusals use `INDEPENDENCE` with `details.cause` ∈ {`ROLE_UNDECLARED`, `ROLE_NOT_DESIGNATED`, `SAME_SESSION_AS_BUILDER`, `SAME_ROLE_AS_BUILDER`} and remediation text.
- The `--reviewer-role` / `--verifier-role` free strings no longer reach a verdict. The verdict records the declared acting role and where it came from.

**4. A5 approval: reviewer-authored tests, bound digests**

- **Identifying the planner's tests.** `test-design` records the identity (`verify::test_identity`: the test without its id or description) of every test the planner's scaffold generates. It also records every test the file holds when the planner runs `test-design`, except tests an earlier approval recorded as the reviewer's.
- **Refusals.** An approval requires at least one reviewer-authored test. Without one: `INDEPENDENT_TESTS_REQUIRED`. A relabelled scaffold test does not count. A reviewer test of a kind the executor cannot run, or with no id, is refused (`INDEPENDENT_TESTS_INVALID`). The plan/test agreement check (round 1) stays first.
- **What the approval records:**
  - `catalogue_sha256`: `planner::catalogue_digest`, recomputed from each entry's material content, never from a stored hash. It excludes the OS's own bookkeeping, including the gate id the OS assigns during A6.
  - `plan_sha256`: excludes only the regeneration stamps.
  - `tests_sha256`.
  - The reviewer's test ids and identities, and the scaffold tests the reviewer removed.
  - The independence evidence (designated role, and the builders it was judged against).

**5. A6 bound to the approval**

- Before anything executes, `require_approved_artefacts` recomputes the three digests. It refuses `APPROVAL_STALE` when the catalogue, plan or tests differ from what A5 bound, and names which ones.
- This covers the executor who empties the tests, turns a KEEP into an ungated DELETE, or drops a plan batch after approval.
- The A6 result reports the approval it executed.

**6. A7**

- Performed by `migration-verifier` only.
- The computed verdict is `MIGRATION_ACCEPTED_FOR_MEMORY_REBUILD` only if all of these hold:
  - the catalogue checks pass;
  - no test fails and **at least one test executed**;
  - the tests, plan and catalogue are exactly the approved ones;
  - the approval records reviewer-authored tests;
  - secrets are isolated and the kernel is intact.
- A claimed accept against a rejecting computation is refused (`VERDICT_CONFLICT`, with `approval_problems`).
- The verdict records the digests it verified (`approval_bound`).

**7. A8**

- Refuses a catalogue changed since A7 accepted (`APPROVAL_STALE`).

**8. A9 and A10: held-out queries from the verifier**

- **A9** records the identity (`heldout_query_identity`: query, expected and forbidden refs, route; not id, k or category) of every held-out query present after the build. That is the builder's starter set plus anything that pre-existed.
- **Builder queries at A10.** A10 treats as the builder's those recorded queries, plus every query the product's own starter generator produces from the current index.
- **Refusal.** With no verifier-authored query, A10 refuses (`INDEPENDENT_HELDOUT_REQUIRED`). Relabelled starter queries do not count.
- **Accept.** Acceptance requires both of these, as well as reproducibility and no secret leak:
  - the verifier's own set passes as a measured set (`MEMORY_POLICY.regression.min_queries`);
  - the whole set passes.
- **Record.** The verdict records the verifier's query ids and identities and the held-out digest.

**9. A11**

- Performed by `independent-auditor` only, in a session and role that authored no builder stage.
- Its acceptance criteria now include:
  - "migration executed and verified against the approved plan and tests";
  - "comprehensive audit by a fresh independent auditor";
  - independent verdicts given by the designated roles.

**10. T2: the adoption record**

- `00-BASELINE.yaml` holds the stage order, authorship and every verdict. It is sealed (`t2::seal_value`) whenever a stage writes it.
- It is honoured only when the seal verifies. Otherwise: `T2_UNBOUND`, with remediation "restore from version control or restart at A0".
- A hand-edited verdict, digest or author entry decides nothing.
- `adopt status` reports the binding (`honoured`), the authors, and each verdict's role against its designated role.

**11. Adoption gates bound to their subject** (BC-P2-11 for adoption; found while binding execution)

- Destructive-migration gates now carry `subject: {kind: adoption-catalogue-entry, id, sha256}` over the entry's path, action, target, gate reasons and dependants (`planner::gate_subject_sha256`).
- `adopt::entry_gate_answer` honours an answer only for the entry the gate was raised for, and only while that entry still asks the same question. It is used by A6, A8 and the migration-test runner.
- Pointing an entry's `human_gate` at another entry's answered gate therefore authorises nothing. Before this change, an executor could do that without changing the approval digest, because the gate id is OS bookkeeping.

### Probes re-run

Before = base 843d79c; after = candidate. Outputs are in `evidence/probes/`.

| Line | Before | After |
|---|---|---|
| alpha-r `S4-T2-B2-negative` [N1] (unedited, adapter declares orchestrator) | A0→A11 all ok, final verdict `ADOPTED_WITH_ACCEPTED_EXCEPTIONS` | A0 refused `ADOPTION_SESSION_UNDECLARED`; no stage completes. The probe then crashes reading a baseline that was never written, so its N2–N7 lines are not reached unedited. Named checks N2/N7 cover them. |
| [N2] tests emptied after approval (named check `N2-tests-emptied`) | A6 executes | `APPROVAL_STALE ["tests"]`; nothing executed (no `framework.lock`) |
| [N2] KEEP → ungated DELETE after approval (`N2-keep-to-delete`) | A6 runs | `APPROVAL_STALE ["catalogue"]`; `util.py` present |
| plan batch dropped after approval (`N2-plan-changed`) | A6 runs | `APPROVAL_STALE ["plan"]` |
| [N7] A5 `--reviewer-role migration-executor`; A5 as orchestrator | approved | `INDEPENDENCE` / `ROLE_NOT_DESIGNATED` |
| [N7] A7 `--verifier-role migration-executor`; A7 acting `backend-engineer` | accepted | `INDEPENDENCE` / `ROLE_NOT_DESIGNATED` |
| T1-roles [T1c] A11 by the executor's session (`T1c-A11-executor`, `A11-builder-session`) | accepted | refused (`ROLE_NOT_DESIGNATED`; even under the auditor role, `SAME_SESSION_AS_BUILDER`) |
| epsilon-r O3 §C: planner reviews its own plan (unedited) | refused `INDEPENDENCE` | refused `INDEPENDENCE` ([control]) |
| epsilon-r O3 §D: `SESS=S-planner` + `--reviewer-session S-anything` (unedited) | **approved** with zero reviewer tests | **`SESSION_CONFLICT`** |
| zero reviewer tests / relabelled scaffold (`O3-D-zero-tests`, `O3-D-relabel`) | approved | `INDEPENDENT_TESTS_REQUIRED` |
| A5 with no declared session (`A5-session-undeclared`) | approved (random id) | `ADOPTION_SESSION_UNDECLARED` |
| hand-edited verdict digest (`T2-record`) | honoured | `T2_UNBOUND` |
| another entry's answered gate (`gate-subject`) | both files deleted | only the entry its own gate answered is deleted |
| reviewer session returns as verifier (`role-consistency`) | accepted | `ADOPTION_ROLE_INCONSISTENT` |
| A7 over emptied tests (`A7-zero-tests`) | `MIGRATION_ACCEPTED…` with 0/0 tests | claim refused `VERDICT_CONFLICT`; computed `MIGRATION_REJECTED_NEEDS_REPAIR` |
| A7 over tests changed after approval (`A7-bound-tests`) | accepted | rejected ("tests differs from what the independent reviewer approved") |
| A8 over a catalogue changed after A7 (`A8-bound`) | runs | `APPROVAL_STALE` |
| A10 on the builder's starter set / relabelled copies / role `migration-verifier` | accepted | `INDEPENDENT_HELDOUT_REQUIRED` ×2 / `INDEPENDENCE` |
| A10 on 6 verifier-authored queries (`A10-verifier-set`) | – | accepted; independent set measured and passing |
| alpha-r `S4-adopt-end-to-end` (unedited, adapter) | A0–A11 done; "does the verdict bind … by digest? **False**" | stops at A5: the undeclared reviewer role becomes the adapter's orchestrator, which is not designated |
| same, **derived copy** (5 lines: designated roles, one reviewer test, verifier queries), prepared and `RAW_SQL_STORE=1` | – | **A0–A11 done**; "bind by digest? **True**"; A7 accepted 41 executed / 41 pass; every A11 criterion OK, including the new ones |

Named checks: base **4 PASS ([control]) / 33 FAIL** of 37 reachable lines; candidate **41/41 PASS**.

### Tests added and changed

- **Added** `migration::adoption_independence_is_bound_to_declared_roles_and_approved_artefacts`. It is certification-level: roles, sessions, reviewer tests, the three post-approval tampers, the T2 record, gate subject, A7 zero tests, A10 authorship, A11 G5, and status.
- **Added** unit tests in `adopt.rs`: approval digest, verdict staleness, plan digest, held-out identity, designated roles are L0 kernel roles.
- **Added** a unit test in `identity.rs`: session declaration (flag, environment, stage flag, conflict, installed).
- **Changed** `brownfield.rs`, `migration.rs`, `common.rs::run_brownfield_to_a6` and `repair.rs::freeze_writes_is_honoured_by_adopt_and_upstream`: see §6.

### Limits

- **Identity is declared, not credentialed.** Roles and sessions are declared by the adapter (OWNER-DECISION-P2-0001, Option A). A misbehaving agent that declares the designated role in a fresh session is the owner's recorded residual risk. This repair makes the declared role and session the ones bound, recorded and checked consistently. It builds no agent credential.
- **Where declarations come from.** The runtime reads the session declaration from the process arguments and environment, or from `identity::install_declared_session` if the CLI installs one (IP-R2-1). A library embedder declares through `GOV_SESSION`.
- **Test authorship.** The file `06-migration-tests.yaml` is shared. A test added by someone other than the reviewer after the last `test-design` counts as reviewer-authored once the reviewer approves it: the approval records exactly which tests it adopted as its own. The same holds for the verifier's held-out queries.
- **T2 strength and scope.** The seal is detection-grade against a process with the operator's OS privileges (WS-3, t2.rs). An adoption record sealed on one machine is `FOREIGN` on another, so an adoption runs on one machine or restarts at A0.

---

## 2. Adopt host call sites

### BC-P2-08 (IP-10 from WS-3; own IP-3)

- Every stage now evaluates authority for its class against the declared role inside the runtime, and binds the stage to that role (§1.1). There is no longer a planner-session fallback: `Actor::from_env_or_baseline` is kept only for API compatibility.
- Every stage has an explicit-actor entry point:
  - `a0_baseline_by`, `a1_inventory_by`, `a2_classify_by`, `a3_map_by`, `a4_plan_by`, `a5_test_design_by`, `a5_review_by`, `a6_migrate_by`, `rollback_batch_by`, `a7_verify_migration_by`, `a8_extract_legacy_by`, `a9_build_memory_by`, `a10_verify_memory_by`, `a11_audit_by`;
  - `identity::Actor::{declared, supplied, process}`.
- The existing CLI arms keep working unchanged: they already pass the declared acting role, and the runtime resolves the session declaration itself. Switching the arms to the `*_by` APIs is optional (IP-R2-1).

### BC-P2-07, host side at adopt (IP-WS02-18 from WS-2; own IP-4)

- **G0.** `scheduler::guard(p, ops::ADOPT_MIGRATE, touched)` runs before any A6 batch of an installed project (the paths each selected batch touches) and before A8's retirements. An active hard-block refuses with `HEALTH_HARD_BLOCK`.
- **G4.** `scheduler::tier_run(G4, Trigger("adopt.migrate").with_paths(moved))` runs when a migration completes. `tier_run(G4, "adopt.build-memory")` runs after A9. The health result is reported in the stage output; a run that cannot complete is reported, not hidden.
- **G5 at A11.** A11 no longer calls `verification::audit(deep)`. It runs WS-2's tier contract: `RunOptions::new(Tier::G5, Trigger("adopt.audit"))` (all checks, `Refresh`), `deep`, `RecordPolicy::Always` (the adoption's audit gets its own record), `surface "adopt"`, through `verification::audit_with`. The verdict records `tier`, `health_result` and `inputs_hash`. IP-WS02-18 named `tier_run`; its recording policy (`WhenCompleteAndStale`) would not always produce the audit record A11 needs, so the same tier contract is used with `record = Always`.
- **Evidence.** Named checks show the difference:
  - `G0-A6`: base proceeds; candidate returns `HEALTH_HARD_BLOCK` on a planted critical secret, then releases after the repair.
  - `G4-after-migration`: base has no health; candidate runs tier G4 and returns a `health_result`.
  - `A11-G5`: base has no tier; candidate records G5 and an audit record.

---

## 3. BC-P2-10, export-approval use (IP-9 from WS-3; own IP-2)

### Requirement

A record asserting human approval of an upstream export derives from the authenticated human channel, bound to the packet. Sources: repair-delta BC-P2-10; finding A0-Q1-02; Contract v3 :851, :864.

### What changed

Files: `runtime/src/upstream.rs`, `framework/schemas/upstream-packet.schema.json` (1.2.0), `LEARNING_POLICY.yaml` (comment only).

**At `prepare`**

- `upstream prepare` raises the packet's export-approval Human Decision Gate through `gates::create_system`: trigger `upstream_export`, with a complete package that shows what would leave.
- The gate's `subject` is `upstream::export_subject`. It binds the packet id, the lesson and the payload hash, with a `sha256`.
- The gate is `R3` and irreversible, so it is not agent-resolvable.

**At `submit`**

- `resolve_export_approval` honours only `gates::human_approval_for(p, gate, subject_sha256)`: a T2-bound gate, an owner-signed human answer re-verified against the anchor, an authorising option, and exactly this subject.
- `--approved-by` is recorded as `approved_by_claim` and ignored.
- A packet without an export gate gets one raised, with a typed refusal naming it.
- Typed refusals:
  - `HUMAN_GATE_REQUIRED`: pending, with next actions;
  - `GATE_DECLINED`;
  - `APPROVAL_STALE`: the content was changed and re-hashed after the answer;
  - `HUMAN_APPROVAL_REQUIRED`: agent-resolved;
  - `T2_UNBOUND`: a hand-edited gate.
- Destination checks now run before approval, so the same typed destination errors appear with or without an approval.

**Records**

- The ledger's `approved_by` is the signed document's `answered_by`.
- The approval evidence (gate, decision, key ids, envelope digest, subject) is stored in the delivered packet, the ledger and the lesson.
- With `LEARNING_POLICY.upstream.approval: policy`, no human approval is asserted (channel `policy`).

### Probes re-run

| Line | Before | After |
|---|---|---|
| epsilon-r `Q-learning-upstream` Q1.6-8 (unedited, direct and adapter) | `--approved-by i-approve-myself` exported; lesson promoted; `gate list` `[]` | `HUMAN_GATE_REQUIRED`; lesson not promoted; the export gates exist (`HDG-0001..3`) |
| Q4.5 (a)/(b)/(c) (round-1 BC-P2-50) | blocked | blocked (unchanged) |
| Q4.3 "submit (approved)" | exported with `--approved-by owner` | refused `HUMAN_GATE_REQUIRED`: the probe's approval is a CLI string. The positive path with an owner-signed answer is named check `Q-human`. |
| named checks `Q-gate-raised`, `Q1.6-8`, `Q-agent`, `Q-declined`, `Q-stale`, `Q-human` | FAIL (base raises no gate; the string exports) | PASS |

### Tests

- Added `upstream::export_approval_comes_only_from_an_owner_signed_answer_bound_to_the_packet`. It covers the claim, an agent answer, a forged record, a decline, another packet's approval, stale content, and the positive path.
- Changed `upstream::upstream_export_gate_fails_closed_and_sanitises` and `export_gate_fails_closed_on_content_whatever_the_name` (§6).

---

## 4. ws06 IP-7: the memory-quality repository-contract rule

- **New migration.** `migrations/M-4.1.5-4.1.6.yaml` delivers the rule to installed projects:
  - `set_overlay_rule` on `REPOSITORY_CONTRACT.yaml`: `spec/reports/memory-quality/**`, class `evidence`, all four index flags `false`, namespace `spec`, `add_if_missing`. Contract rules are last-match, so the appended rule decides those paths after `spec/**`.
  - The template change is declared under `overlay_template_changes` (`op:set_overlay_rule`).
  - Index rebuild and adapter regeneration.
- **Unit test.** `migrations::framework::tests::the_next_migration_delivers_the_memory_quality_contract_rule` checks that the record is schema-valid, that it chains 4.1.4 → 4.1.6, that the rule decides the path (evidence, never indexed), and that it is idempotent.
- **Not done here.**
  - The overlay template itself is WS-6's file, and WS-6's round-2 handoff routes IP-7 to WS-9. The template rule is therefore recorded as IP-R2-2.
  - The release owner completes this record when 4.1.6 is cut (IP-R2-3). `gov release build` refuses a release whose migration misses a template delta.

---

## 5. Integration points for round 3

| IP | Owner / file | Exact change | Why |
|---|---|---|---|
| IP-R2-1 | WS-3, `cli/src/main.rs` (optional) | In `run()`, after `install_acting_role`: `gov_runtime::migrations::identity::install_declared_session(cli.session.clone().or(std::env::var("GOV_SESSION").ok()))?;`. If the adopt arms are switched to the `*_by` APIs, pass `identity::Actor::process()` or `Actor::supplied(&session, Some(&acting))`; do not present the generated fallback id as declared (it is refused either way). No other adopt-arm change is needed. | The runtime gets the session declaration directly instead of reading the process arguments. This completes own IP-3 / WS-3 IP-10 on the CLI side. |
| IP-R2-2 | WS-6, `framework/overlay-templates/REPOSITORY_CONTRACT.yaml` | After the `spec/**` rule, add `- {pattern: "spec/reports/memory-quality/**", class: evidence, semantic_index: false, lexical_index: false, graph_index: false, code_index: false, namespace: spec}` | New installations get the rule that `M-4.1.5-4.1.6` delivers to installed ones (ws06 IP-7). |
| IP-R2-3 | Release owner, `framework/KERNEL.yaml` + `migrations/M-4.1.5-4.1.6.yaml` at release | Set `schema_versions.upstream-packet: 1.2.0` (it already said 1.0.0 while the file was 1.1.0) and add `adoption-baseline: 1.1.0`. When 4.1.6 is cut, extend `M-4.1.5-4.1.6` with an operation or `overlay_template_changes` entry for every other template delta. | Release metadata consistency; `release build` substance check. |
| IP-R2-4 | WS-2, `doctor.rs` / governance families | Report `spec/audits/GOVERNANCE-ADOPTION/00-BASELINE.yaml` whose `t2::verify_value` is not `Verified` as an adoption-integrity finding. Optionally list the adopt tier events (`adopt.migrate`, `adopt.build-memory`, `adopt.audit`) in the scheduler documentation. | Makes a tampered adoption record visible outside the adopt commands, which already refuse it. |
| IP-R2-5 | WS-3, `framework/policies/HUMAN_GATE_POLICY.yaml` (optional) | Add `upstream_export` to `human_only_triggers`. | Defence in depth: the export gate is already not agent-resolvable (irreversible), and `human_approval_for` requires an owner-signed answer. |
| IP-R2-6 | WS-1, `tests/governance/capability-evidence-map.yaml` | Evidence owners: T1/T2/T3/S4/O3 (adoption) → `adopt::check_actor` (A5/A7/A10/A11 independence), `adopt::require_approved_artefacts` (A6/A8), the A7 computed verdict, A10 held-out authorship, and the certification test `migration::adoption_independence_is_bound_to_declared_roles_and_approved_artefacts`. Q1 (human approval) → `upstream::resolve_export_approval` and `upstream::export_approval_comes_only_from_an_owner_signed_answer_bound_to_the_packet`. O5 G5 at adopt → `adopt::a11_audit_by`. | AC-10 |
| IP-R2-7 | WS-3 (docs), `docs/COMMANDS.md` | Document the adoption stage requirements (designated roles, declared sessions, reviewer-authored tests, verifier-authored held-out queries, `APPROVAL_STALE`, T2 record) and the export approval flow (`upstream prepare` raises the gate; owner-signed answer; `submit`). | Documentation |
| carried | WS-2 IP-1 (round 1), WS-4 IP-5 (round 1) | Unchanged, routed in round 2 to their owners. | – |

---

## 6. Existing tests changed, and why

No assertion about a property was weakened. Each change moves the test onto the path the requirement now demands.

| Test | Change | Reason |
|---|---|---|
| `brownfield::brownfield_adoption_end_to_end` | Before approving, the reviewer authors tests (`migration::reviewer_authors_tests`). The memory verifier authors held-out queries before A10 (`verifier_authors_heldout`). A11 (first audit and re-audit) runs as `independent-auditor` in session `S-auditor` instead of the executor. | BC-P2-34: approval with reviewer-authored tests; held-out tests from the verifier; A11 by the designated auditor in a fresh session. Every property assertion is unchanged. |
| `migration::path_migration_with_rollback_and_memory_rebuild` | Asserts `INDEPENDENT_TESTS_REQUIRED` before the reviewer authors tests. A10 runs as `memory-verifier` (it was `migration-verifier`) after first asserting `INDEPENDENT_HELDOUT_REQUIRED`. A11 is refused for the executor (`INDEPENDENCE`) and run by `independent-auditor`. | As above. The test now asserts more. |
| `migration::adoption_dependency_proof_citations_and_rerun_identity` | The reviewer authors tests after restoring the original file. | Same reason. |
| `common::run_brownfield_to_a6`, `repair::freeze_writes_is_honoured_by_adopt_and_upstream` | One added line: the reviewer authors tests before approval. | Same reason. |
| `upstream::upstream_export_gate_fails_closed_and_sanitises` | `--approved-by owner` is now asserted **refused** (`HUMAN_GATE_REQUIRED`). The export follows an owner-signed answer on the packet's gate (`ws03::human_decide`). `approved_by` is the signed document's, and `approved_by_claim` is the CLI string. | BC-P2-10 |
| `upstream::export_gate_fails_closed_on_content_whatever_the_name` | The final export uses the owner-signed answer and asserts `approval.authenticated == true` (it was `false` in round 1). | BC-P2-10 |

---

## 7. Regression and R1 preservation (at `23a76d2`)

| Suite | Result |
|---|---|
| `cargo test --lib` | **153 passed, 0 failed** (base 146; +5 `adopt`, +1 `identity`, +1 `migrations::framework`) |
| `cargo test --test certification` | **102 passed, 0 failed** (base 100; +2), including `section6::*` |
| R1 held-out, unedited, built against this worktree through a private per-run path | AR-0027 **26/3**, AR-0029 **26/2** (`ho_f` does not compile), AR-0031 **27/7**, AR-0033 **30/1**: all at their recorded baselines, with the same failing tests. The AR-0033 failure is `hv_a::a1` (pins 84 / 740); **census of this tree: 105 files / 1515 functions**. The unpinned copy and AR-0033's `derive.py` report **0 violations** in every §6 activity. |
| Round-1 builder probe, derived owner-channel copy with reviewer tests | 27/27 (base 27/27): BC-P2-33/52/21/50 hold |
| `rustfmt --check` (edition 2021) | clean on every touched Rust file |
| `cargo build` | no warnings |

No file under `runtime/src/srr/**`, `kernel_trust.rs`, `kernel.rs`, `lock.rs`, `init.rs`, `update.rs`, `release.rs`, `recovery.rs`, `records.rs`, `tools.rs` or `capabilities/**` changed.

Two new callers reach a §6 activity:

- **Human-gate creation:** `upstream::raise_export_gate` → `gates::create_system`. It passes through `srr::breakglass::guard_effect(HumanGateCreate)` and conforms to the §6 derivation; `section6.rs` stays green.
- **Adoption kernel install (`srr::admit`):** unchanged.

The Contract v3 source is byte-identical (`4c2df291…5ed3`).

---

## 8. What this run did not do, and observations

**Not done**

- No agent credentials (OWNER-DECISION-P2-0001). No change to `cli/src/main.rs`, `lib.rs` or any other workstream's file.
- The gamma-r `E1.b4.b` (task designated roles) and `H4.b2` (test-data authorship) acceptance lines of BC-P2-34 belong to WS-5 and WS-10. They were not repaired or claimed here.
- epsilon-r O3 §A/§B (the DAG's independence boolean) and §E (the governed memory held-out set generated at `gov init`) are outside adoption. They belong to WS-5/WS-2 and WS-6/WS-2.

**Observations for routing**

| # | Observation | Recommendation |
|---|---|---|
| 1 | Unedited audit-of-record probes stop early by design: alpha-r `S4-T2-B2-negative`, `S4-adopt-end-to-end`, `T1-roles`. They declare no designated roles and no session, and author no reviewer tests or held-out queries. | Fresh verifiers must use the designated roles and declared sessions. The derived copy shows exactly the five lines that must change. |
| 2 | A reviewer-authored `command` test executes an arbitrary command at A6/A7 with the executor's privileges. This is existing behaviour, not introduced here. | Worth a verifier's look under tool/command governance. |
| 3 | My named-check script and derived probes provision a standalone human-channel anchor. After WS-3 applies P2-ADJ-0001 (default `false`), they need a provisioned throw-away root, as the certification helpers will. | The product tests use `ws03::human_decide` and follow WS-3's helper. |

---

## 9. Owner-decision questions

None.
