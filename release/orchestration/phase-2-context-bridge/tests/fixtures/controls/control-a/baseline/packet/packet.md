# Context packet

manifest_sha256: 09a7cd1fa2f9e4ee6f3ceca077ea335d72750d81d109218dd5124406710ac08e
status: OK

## A. MANDATORY AUTHORITATIVE INPUTS

- unit: record:state:bridge#contract_v3  (delivery=MANDATORY, route=resolver, class=CONTRACT, lifecycle=UNKNOWN)
  source: Governance_OS_Capability_Acceptance_Contract_v3.md@9ba8367372cdffef35098abb9078570068f96eea
  [UNKNOWN: lifecycle could not be determined; never treated as ACTIVE.]
  reason: the owner source contract (the evidence-owner requirement)
# Governance OS Capability Acceptance Contract — v3

**Role:** First-class, versioned Governance OS capability contract and second-layer health/audit baseline.

This contract is derived from the original three Governance OS governing documents. Later independent-verification hardening requirements remain explicitly labelled as such rather than silently rewriting the original requirements.

## Canonical implementation in the Governance OS repository

The human/product owner controls the normative checklist source. The IDE agent must **not invent or rewrite its semantics from memory**.

Use this structure:

```text
framework/
  contracts/
    source/
      GOVERNANCE_CAPABILITY_ACCEPTANCE_CONTRACT_v3.md
        # HUMAN-APPROVED NORMATIVE SOURCE; uploaded by the product owner
    governance-capability-acceptance.yaml
        # executable compiled representation consumed by Governance OS
    contract-source.lock
        # binds the compiled representation to the exact uploaded source hash
  schemas/
    governance-capability-acceptance.schema.json

tests/
  governance/
    capability-evidence-map.yaml
        # capability → test/check/evidence mapping

docs/
  generated/
    GOVERNANCE_CAPABILITY_ACCEPTANCE.md
        # generated readable runtime view
```

### Contract authority model

`framework/contracts/source/GOVERNANCE_CAPABILITY_ACCEPTANCE_CONTRACT_v3.md` is the **human-approved normative source**.

`framework/contracts/governance-capability-acceptance.yaml` is the **machine-executable compiled form**.

The runtime consumes the YAML, but it is valid only when `contract-source.lock` proves that it was compiled/validated from the exact approved source hash.

The builder may create the destination path and compiler/schema machinery, but MUST stop and ask the product owner to upload the approved contract file. It must not fabricate the contract from remembered conversation context or silently change its semantics.

Any semantic difference between source and compiled representation is a hard failure.

The generated docs view is derived and non-authoritative.

Consumer projects do **not** receive giant synthetic qualification repositories. They receive the contract, the governance health scheduler, and the executable evidence/check families needed to evaluate the real project.

## Required contract fields per capability

Every capability item should carry, where applicable:

- stable capability ID;
- title/description;
- source governing-document reference;
- requirement class: `ORIGINAL`, `POST_VERIFICATION_HARDENING`, or `EXECUTION_REFINEMENT`;
- severity if violated;
- applicability rule;
- evidence class(es);
- automated check/test IDs;
- independent-verification obligation;
- evidence-freshness triggers;
- health-scheduler tier(s) G0–G6;
- advanced-qualification challenge IDs;
- adoption verification obligation;
- periodic operational-audit obligation;
- allowed status values;
- N/A requirements;
- remediation/task-generation rule.

## Relationship between the contract and the governance suite

The contract is the umbrella acceptance definition.

The governance suite is the continuous executable evidence layer beneath it.

Not every capability can be proven by a unit test. Each item must therefore map to one or more evidence classes:

- automated invariant/guard;
- unit/integration/system test;
- governance health check;
- independent held-out test;
- migration/rollback evidence;
- synthetic-repository evidence;
- human-gate evidence;
- clean-clone/release evidence;
- independent audit evidence.

A capability may not be reported `PRESENT_AND_SUBSTANTIAL` solely because a file/schema/policy exists.

## Evidence freshness

A previously green capability becomes `STALE` when any relevant evidence input changes, including where applicable:

- governing contract/policy;
- runtime/kernel implementation;
- schema;
- migration;
- tool/plugin;
- model/retrieval profile;
- project path map;
- authoritative spec/decision;
- relevant sour
read_token: 13bc31a40336

## B. SYSTEM PURPOSE / WHY

(none)
read_token: 789225112cf7

## C. DIRECT DEPENDENCY / IMPACT CONTEXT

(none)
read_token: f840389be91c

## D. RELEVANT ACTIVE DECISIONS

### D.1 -- RELEVANT ACTIVE DECISIONS

(none)

### D.2 -- OWNER DIRECTION TO TEST (not yet authority)

(none)

### D.3 -- HYPOTHESIS TO TEST (no classificatory force)

(none)
read_token: 613018e96a13

## E. RELEVANT HISTORICAL / SUPERSEDED DECISIONS

(none)
read_token: bc8bba2850e3

## F. FAILED APPROACHES / LESSONS

(none)
read_token: 78e75d3e21be

## G. CODE / TEST / ENFORCEMENT SURFACES

queries: [{"id":"CA-WHY","k":8,"routes":["lexical","semantic"],"text":"Why does renaming or removing a certification test break gov contract verify? What is the governed evidence map for?"},{"id":"CA-ENF","k":8,"routes":["lexical","semantic"],"text":"Where in code does gov contract verify resolve evidence owners against the product and fail on a capability with no running owner?"},{"id":"CA-TESTS","k":8,"routes":["lexical","semantic"],"text":"Which tests prove that the contract-binding chain and the evidence map are verified and that a missing owner fails?"},{"id":"CA-DEPS","k":8,"routes":["lexical","semantic"],"text":"What depends on the evidence map and what becomes stale if the evidence map or the contract source changes?"}]
- unit: chunk:fe242c342bf9262a1a4ef01c  (delivery=RETRIEVED, route=semantic, class=EVIDENCE, lifecycle=UNKNOWN)
  source: tests/governance/capability-evidence-map.yaml@58219d5628683d6f462aa67bf25dbc2641933bce:5-8
  [UNKNOWN: lifecycle could not be determined; never treated as ACTIVE.]

- unit: chunk:ba587648d8cbba4530a17871  (delivery=RETRIEVED, route=semantic, class=EVIDENCE, lifecycle=UNKNOWN)
  source: runtime/src/contracts.rs@94d02116e770e0c4e99fe62367f89cd915692592:2635-2672
  [UNKNOWN: lifecycle could not be determined; never treated as ACTIVE.]

- unit: chunk:a612b2085ce8e55c954a51ee  (delivery=RETRIEVED, route=semantic, class=EVIDENCE, lifecycle=UNKNOWN)
  source: tests/governance/capability-evidence-map.yaml@94d02116e770e0c4e99fe62367f89cd915692592:12611-12626
  [UNKNOWN: lifecycle could not be determined; never treated as ACTIVE.]

- unit: chunk:c9652a10dc5b16c7f57df718  (delivery=RETRIEVED, route=semantic, class=EVIDENCE, lifecycle=UNKNOWN)
  source: runtime/src/contracts.rs@94d02116e770e0c4e99fe62367f89cd915692592:1374-1375
  [UNKNOWN: lifecycle could not be determined; never treated as ACTIVE.]

- unit: chunk:0b0472ab17232830f63cadca  (delivery=RETRIEVED, route=semantic, class=EVIDENCE, lifecycle=UNKNOWN)
  source: tests/governance/capability-evidence-map.yaml@58219d5628683d6f462aa67bf25dbc2641933bce:12701-12716
  [UNKNOWN: lifecycle could not be determined; never treated as ACTIVE.]

- unit: chunk:b9b7d26e7a82c052bd401b31  (delivery=RETRIEVED, route=lexical, class=EVIDENCE, lifecycle=UNKNOWN)
  source: runtime/src/release.rs@d34184e5e4b3166f0330ee149a70169c09f4c77c:286-304
  [UNKNOWN: lifecycle could not be determined; never treated as ACTIVE.]
            && contract["verdict"] == "CONTRACT_SOURCE_BOUND",
        "capability_contract": contract,
        "health": health,
        "built_release_verified": {"ok": true, "release_hash_matches_kernel": built["release_hash_matches_kernel"]},
        "checked_at": now_iso(),
    });
    write_json(&dir.join("PRE_RELEASE_CHECKS.json"), &checks)?;
    let mut out = manifest;
    out["pre_release_checks"] = checks;
    Ok(out)
}

/// IP-2 — the canonical tree's capability-contract binding, as `release::build` requires it.
///
/// The IP's purpose is that "a release must not ship derived contract views that diverge from the owner source".
/// A chain that is present and does not verify — the import, compiled form, evidence map, generated view, schema or
/// lock diverging from the approved source, or unreadable — refuses the build (`RELEASE_CONTRACT_NOT_BOUND`). A tree
/// that does not carry the whole chain (a payload-only canonical tree — framework/, migrations/, tools/ — which is how
/// release tooling and every root-of-trust probe builds releases) cannot ship a divergent view it does not have: that

- unit: chunk:6066b02d31c071bd8cf76337  (delivery=RETRIEVED, route=semantic, class=EVIDENCE, lifecycle=UNKNOWN)
  source: runtime/src/contracts.rs@94d02116e770e0c4e99fe62367f89cd915692592:5894-5920
  [UNKNOWN: lifecycle could not be determined; never treated as ACTIVE.]

- unit: chunk:e8b0ae805ec0f5f0554ec7ce  (delivery=RETRIEVED, route=semantic, class=EVIDENCE, lifecycle=UNKNOWN)
  source: runtime/src/contracts.rs@94d02116e770e0c4e99fe62367f89cd915692592:5982-6007
  [UNKNOWN: lifecycle could not be determined; never treated as ACTIVE.]

- unit: chunk:ac15d5eb7eb98e9925f5c298  (delivery=RETRIEVED, route=lexical, class=EVIDENCE, lifecycle=UNKNOWN)
  source: release/capability-baseline/audit-0/synthesis/evidence/tools/build_synthesis.py@58219d5628683d6f462aa67bf25dbc2641933bce:394-399
  [UNKNOWN: lifecycle could not be determined; never treated as ACTIVE.]
     "normative_source": "Governance_OS_Capability_Acceptance_Contract_v3.md:43 'valid only when contract-source.lock proves that it was compiled/validated from the exact approved source'; :47 'Any semantic difference between source and compiled representation is a hard failure.'; frozen gate contract AC-13.",
     "provenance_class": "ORIGINAL-NORMATIVE", "blocks": ["AC-13"], "blocking": True,
     "evidence": ["evidence/AC01-09-13-14-universe-identity-binding.py", "evidence/AC01-09-13-14-universe-identity-binding.out ([AC-13] lines)"],
     "reproduction": "python3 release/capability-baseline/audit-0/synthesis/evidence/AC01-09-13-14-universe-identity-binding.py",
     "repair_direction": "Verification of the binding chain must fail whenever the compiled form, the evidence map or the generated view differs semantically from the owner source (every capability section including Gate U, every checklist bullet, every Contract v3:53-73 field, every requirement-class label), not only when it differs from the compiler's own output (Contract v3:43, :47)."},
    {"id": "S0-B1B3-01", "capability": ["B1", "B3", "D6", "C1"], "severity": "MEDIUM", "blocker_class": ["BC-P2-31"],

- unit: chunk:fb410ac1592e410edbdc4d27  (delivery=RETRIEVED, route=semantic, class=EVIDENCE, lifecycle=UNKNOWN)
  source: release/capability-baseline/verify-1/delta/evidence/build-capability-audit.py@94d02116e770e0c4e99fe62367f89cd915692592:477-488
  [UNKNOWN: lifecycle could not be determined; never treated as ACTIVE.]

- unit: chunk:40ed3277968438d38e407e97  (delivery=RETRIEVED, route=lexical, class=EVIDENCE, lifecycle=UNKNOWN)
  source: runtime/src/release.rs@58219d5628683d6f462aa67bf25dbc2641933bce:328-337
  [UNKNOWN: lifecycle could not be determined; never treated as ACTIVE.]
/// The IP's purpose is that "a release must not ship derived contract views that diverge from the owner source".
/// A chain that is present and does not verify — the import, compiled form, evidence map, generated view, schema or
/// lock diverging from the approved source, or unreadable — refuses the build (`RELEASE_CONTRACT_NOT_BOUND`). A tree
/// that does not carry the whole chain (a payload-only canonical tree — framework/, migrations/, tools/ — which is how
/// release tooling and every root-of-trust probe builds releases) cannot ship a divergent view it does not have: that
/// is recorded as `INCOMPLETE_IN_THIS_TREE`, never as bound, and such a build is not release-evidence eligible. The
/// kernel payload itself carries no contract view (`framework/contracts` is not a payload directory).
fn pre_release_contract(canonical_root: &Path, version: &str) -> Result<Value> {
    match crate::contracts::verify(canonical_root) {
        Ok(v) if v["verdict"] == "CONTRACT_SOURCE_BOUND" => Ok(json!({"verdict": v["verdict"], "owner_source_sha256": v["owner_source_sha256"], "capability_count": v["capability_count"], "checklist_item_count": v["checklist_item_count"]})),

- unit: chunk:c886ca01677a1e71875fef8e  (delivery=RETRIEVED, route=semantic, class=EVIDENCE, lifecycle=UNKNOWN)
  source: runtime/src/contracts.rs@94d02116e770e0c4e99fe62367f89cd915692592:2610-2638
  [UNKNOWN: lifecycle could not be determined; never treated as ACTIVE.]
read_token: d9d60767952a

## H. SUPPLEMENTARY RETRIEVED CONTEXT

queries: [{"id":"CA-WHY","k":8,"routes":["lexical","semantic"],"text":"Why does renaming or removing a certification test break gov contract verify? What is the governed evidence map for?"},{"id":"CA-REQ","k":8,"routes":["lexical","semantic"],"text":"Which Contract v3 capability and which frozen Phase-2 acceptance criterion require every capability to have a running evidence owner?"},{"id":"CA-ENF","k":8,"routes":["lexical","semantic"],"text":"Where in code does gov contract verify resolve evidence owners against the product and fail on a capability with no running owner?"},{"id":"CA-TESTS","k":8,"routes":["lexical","semantic"],"text":"Which tests prove that the contract-binding chain and the evidence map are verified and that a missing owner fails?"},{"id":"CA-DEPS","k":8,"routes":["lexical","semantic"],"text":"What depends on the evidence map and what becomes stale if the evidence map or the contract source changes?"}]
- unit: chunk:35c85c07366257e130521baa  (delivery=RETRIEVED, route=lexical, class=OWNER_DECISION, lifecycle=UNKNOWN)
  source: release/orchestration/phase-2-context-bridge/GATES/OWNER-LAUNCHER-BR-0001-P2X-FAIL-1.md@94d02116e770e0c4e99fe62367f89cd915692592:197-224
  [UNKNOWN: lifecycle could not be determined; never treated as ACTIVE.]
      → concrete effective permission/behaviour
      → tests
      → prior findings/failed repairs
      → current Review-8 finding/status

For any claimed property, require the context to reach the ACTUAL decision/enforcement point. Do not accept evidence that proves only an upstream representation while downstream semantics decide the real effect.

Also demonstrate at least these query classes:
- Why does this mechanism exist?
- Which Contract-v3 capability requires it?
- Which owner/architecture decisions constrain it?
- What does it depend on?
- What depends on it?
- Which prior approaches failed and why?
- Which tests prove or challenge it?
- Which evidence becomes stale if it changes?
- What is current versus superseded?
- What can potentially be deleted without violating the actual requirement?

DO NOT
- build unrelated V8.3 features;
- run Phase 3A ecosystem research;
- perform the final retrieval-model bake-off;
- repair F1/F2/F3 during bridge construction;
- mutate the frozen Phase-2 product;
- silently promote bridge-derived state to authority;
- ask the owner to supervise routine internal dispatches that the orchestration state can determine.

- unit: chunk:1339aef918366b1241b2faae  (delivery=RETRIEVED, route=semantic, class=ORCHESTRATION_RECORD, lifecycle=UNKNOWN)
  source: release/orchestration/phase-2/HANDOFFS/P2-HO-0049-integration-4.md@94d02116e770e0c4e99fe62367f89cd915692592:27-36
  [UNKNOWN: lifecycle could not be determined; never treated as ACTIVE.]

- unit: chunk:82f0cd3082b2b2c8b2e7aed4  (delivery=RETRIEVED, route=semantic, class=ORCHESTRATION_RECORD, lifecycle=UNKNOWN)
  source: release/orchestration/phase-2/AGENT_RUNS/P2-AR-0042.report.yaml@94d02116e770e0c4e99fe62367f89cd915692592:48-49
  [UNKNOWN: lifecycle could not be determined; never treated as ACTIVE.]

- unit: chunk:af1bf11e21317883c8154c15  (delivery=RETRIEVED, route=semantic, class=ORCHESTRATION_RECORD, lifecycle=UNKNOWN)
  source: release/orchestration/phase-2/AGENT_RUNS/P2-AR-0054.report.yaml@94d02116e770e0c4e99fe62367f89cd915692592:69-70
  [UNKNOWN: lifecycle could not be determined; never treated as ACTIVE.]

- unit: chunk:73e601733df0390108d1a96a  (delivery=RETRIEVED, route=lexical, class=ORCHESTRATION_RECORD, lifecycle=UNKNOWN)
  source: release/orchestration/phase-2/HANDOFFS/P2-HO-0050-repair-1-r4-tool-install-gate.md@58219d5628683d6f462aa67bf25dbc2641933bce:42-55
  [UNKNOWN: lifecycle could not be determined; never treated as ACTIVE.]
serves Contract v3 K3 — the OS-proposed change transaction, the CIT-E writer that re-derives and re-verifies the request,
the installation-authority checks, and the §6 acquisition sink asked at the instant of the write — and remove its
unconditional gating and its edit to that test. Do not weaken `TOOL_POLICY` or the policy-precedence rules to achieve this.

## Constraints

- Do not edit the round-4 evidence-map files owned by P2-AR-0042: `runtime/src/contracts.rs`, `framework/contracts/**`,
  `framework/schemas/governance-capability-acceptance.schema.json`, `tests/governance/capability-evidence-map.yaml`,
  `docs/generated/**`.
- **Do not rename, remove or `#[ignore]` any existing test** (the evidence map names 441 tests by path). New tests are
  expected — list each with what it proves, for the integrator and the evidence map.
- Tests must cover both branches: a non-elevated install closing with no gate; an install gated for **each**
  authority-expansion trigger; and one showing that ordinary allowlisted network use alone does not gate.
- Availability rule (P2-HO-0031) on what you touch; classify any new or changed subcommand in `COMMAND_GUARDS` / `g0_label`;

- unit: chunk:a2a7b2044b6b13463459aa3c  (delivery=RETRIEVED, route=lexical, class=ORCHESTRATION_RECORD, lifecycle=UNKNOWN)
  source: release/orchestration/phase-2/HANDOFFS/P2-HO-0048-repair-1-r4-residual-continuation.md@58219d5628683d6f462aa67bf25dbc2641933bce:44-56
  [UNKNOWN: lifecycle could not be determined; never treated as ACTIVE.]
   AR-0033 30/1 (the `hv_a::a1` size pin — run its census with only the size assertions removed, in a labelled copy).
   P2-AR-0043 measured lib 265/0, certification 198/0/0, census 123 files / 2329 functions, 0 §6 violations.
4. **A short continuation section** appended to the output directory as `01-CONTINUATION-REPORT.md`: what you verified of the
   recovered work (state plainly that you re-ran the suites yourself), item 1's outcome, your files changed, tests added or
   changed with reasons, your regression and R1 numbers with census, and the remaining integration points for the round-4
   integrator — including anything P2-AR-0043's report lists as not done.

## Constraints

- The parallel round-4 builder **P2-AR-0042** (evidence map, branch `phase2/repair-1-r4-ws01`, completed) owns
  `runtime/src/contracts.rs`, `framework/contracts/**`, `framework/schemas/governance-capability-acceptance.schema.json`,
  `tests/governance/capability-evidence-map.yaml`, `docs/generated/**`. Do not edit those files.
- **Do not rename, remove or `#[ignore]` any existing test**: P2-AR-0042's evidence map names 441 tests by path, and

- unit: chunk:c9cb7a00c44c332dbcf33ee1  (delivery=RETRIEVED, route=lexical, class=ORCHESTRATION_RECORD, lifecycle=UNKNOWN)
  source: release/orchestration/phase-2/HANDOFFS/P2-HO-0041-repair-1-r4-ws01-evidence-map.md@58219d5628683d6f462aa67bf25dbc2641933bce:40-53
  [UNKNOWN: lifecycle could not be determined; never treated as ACTIVE.]
list, and do not rename or remove any existing test (the map names them). If resolving an owner id needs a registry of check/test ids that does not
exist, build it inside your files (e.g. `contracts.rs` resolving `cargo test` names, scheduler check ids from
`scheduler::catalogue`, doctor ids, held-out suite paths) rather than editing other modules.

## What "actually runs" means

- A **tier owner** names a check id the scheduler catalogue declares at that tier (`scheduler::catalogue`), or a doctor id
  run by a tier; the map's tier must match the catalogue's.
- A **test owner** names a `cargo test` path that exists in `--lib` or `--test certification` (resolved, not string-matched
  by prefix only) and is not `#[ignore]`d.
- An **independent held-out owner** names a suite under `release/verification/**/heldout-tests/` or an obligation the
  frozen gate contract assigns to an independent verifier (AC-14 R1, AC-6 oracle review) — label it as independent, never
  as builder evidence.
- **Human-gate** and **release/clean-clone** owners name the command/record type that produces that evidence.

- unit: chunk:1f605b7857fcbd5d709346ad  (delivery=RETRIEVED, route=lexical, class=ORCHESTRATION_RECORD, lifecycle=UNKNOWN)
  source: release/orchestration/phase-2/HANDOFFS/P2-HO-0051-repair-2-common-protocol.md@58219d5628683d6f462aa67bf25dbc2641933bce:31-44
  [UNKNOWN: lifecycle could not be determined; never treated as ACTIVE.]
  manufactures a higher-trust fact, a role or a human approval.
- **Fail closed**: what cannot be evaluated is refused or gated, never waved through.
- **No test renames.** The evidence map names **477** tests by path; renaming, removing or ignoring one fails
  `gov contract verify`, the binding-chain test and `release build`. New tests are expected — name each in your result.
- **New or changed subcommands** are classified in `COMMAND_GUARDS` / `g0_label`; schema version bumps are mirrored in
  `framework/KERNEL.yaml`.
- **Scope**: write only inside your packet's `allow_write` list. The adapter refuses anything else. If closing your class
  needs a file outside it, stop that item and say so in your result rather than reaching for the file.
- **Regression**: the checks in your packet are the ones you may run; run the relevant ones before finishing. The
  orchestrator reproduces the full suites independently afterwards, so do not claim a figure you did not observe.

## What "done" means for a workstream

Your `finish` call carries: a verdict (`REPAIRED_CLAIMED`, `PARTIAL`, `OWNER_DECISION_REQUIRED` or `INCOMPLETE`), a summary

- unit: chunk:4001af7692243e98de4e848d  (delivery=RETRIEVED, route=semantic, class=ORCHESTRATION_RECORD, lifecycle=UNKNOWN)
  source: release/orchestration/phase-2/HANDOFFS/P2-HO-0041-repair-1-r4-ws01-evidence-map.md@94d02116e770e0c4e99fe62367f89cd915692592:16-28
  [UNKNOWN: lifecycle could not be determined; never treated as ACTIVE.]

- unit: chunk:07a4d559a4464d3b0ec224f2  (delivery=RETRIEVED, route=lexical, class=ORCHESTRATION_RECORD, lifecycle=UNKNOWN)
  source: release/orchestration/phase-2/HANDOFFS/P2-HO-0052-repair-3-bounded-final.md@94d02116e770e0c4e99fe62367f89cd915692592:188-203
  [UNKNOWN: lifecycle could not be determined; never treated as ACTIVE.]
certification suite and report its exact figures. Do not claim a figure you did not observe. Every check must run through
the `pipefail` wrapper — a suite piped through anything else can report exit 0 while red, which is a defect this
orchestration already had once and fixed.

## Scope boundaries

`allow_write`: `runtime/src/tools.rs`, `runtime/src/policy_precedence.rs`, `framework/policies/TOOL_POLICY.yaml`,
`tests/certification/r2_failclosed.rs`, and **one** new certification test file for the property tests, declared in
`tests/certification/main.rs` and added to `tests/governance/capability-evidence-map.yaml`.

Everything else is out of scope. In particular: **no test renames** (the evidence map names tests by exact path, and a
rename fails `gov contract verify`, the binding-chain test and `release build`); no weakening of any existing assertion;
no reach into `runtime/src/orchestration/tasks.rs` to change what `contract_generated` means — the defect is that the
*comparison* ignores it, not that the exemption is wrong.

If closing either finding requires a file outside that list, **stop that item and say so** rather than reaching for the

- unit: chunk:4b26df2fe9ecff16a3a0d7b9  (delivery=RETRIEVED, route=semantic, class=EVIDENCE, lifecycle=UNKNOWN)
  source: framework/schemas/governance-capability-acceptance.schema.json@94d02116e770e0c4e99fe62367f89cd915692592:1065-1091
  [UNKNOWN: lifecycle could not be determined; never treated as ACTIVE.]

- unit: chunk:5aee68a10a4450a87d4c9b87  (delivery=RETRIEVED, route=semantic, class=EVIDENCE, lifecycle=UNKNOWN)
  source: release/capability-baseline/repair-1/r4-ws01/evidence/mapping/owner-spec.yaml@58219d5628683d6f462aa67bf25dbc2641933bce:1258-1266
  [UNKNOWN: lifecycle could not be determined; never treated as ACTIVE.]

- unit: chunk:a09a214031aab1ba68054f76  (delivery=RETRIEVED, route=semantic, class=EVIDENCE, lifecycle=UNKNOWN)
  source: release/capability-baseline/verify-1/synthesis/evidence/AC-10-gov-contract-matrix-with-my-runs.yaml@94d02116e770e0c4e99fe62367f89cd915692592:1-19
  [UNKNOWN: lifecycle could not be determined; never treated as ACTIVE.]

[42 items / 39656 bytes omitted: see manifest]
read_token: 41dc9434b8da

## I. TASK CONTRACT / MUTATION SCOPE

- unit: section:I  (delivery=PINNED, route=task_spec, class=None, lifecycle=ACTIVE)
  reason: task_spec, verbatim
{
 "mutation_scope": [],
 "objective": "Explain why renaming or removing a certification test breaks gov contract verify, which requirement the governed evidence map serves, where the check is enforced in code, and which tests prove it.",
 "prohibitions": []
}
read_token: 463399a7270b

## J. COMPLETION / EVIDENCE OBLIGATIONS

- unit: section:J  (delivery=PINNED, route=task_spec, class=None, lifecycle=ACTIVE)
  reason: task_spec, verbatim
{
 "completion_vocabulary": [
  "ANSWERED",
  "PARTIAL",
  "BLOCKED"
 ],
 "notices": [
  {
   "class": "CONTRACT",
   "id": "state:bridge#contract_v3",
   "lifecycle": "UNKNOWN",
   "type": "MANDATORY_LIFECYCLE_NOT_ACTIVE"
  }
 ],
 "receipt_schema": "govbridge-receipt/1",
 "required_checks": []
}
read_token: 8b9c87898d87
