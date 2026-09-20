#!/usr/bin/env python3
"""P2-AR-0049 — generate `capability-audit.yaml` for family delta from this file's bullet table.

The bullet text is taken verbatim from the owner source (`Governance_OS_Capability_Acceptance_Contract_v3.md`
lines 594-747) by reading the file, so the checklist universe cannot drift from the owner source; the per-bullet
judgement, implementation reference and independent-evidence reference are this verifier's.

    python3 evidence/build-capability-audit.py <path to Governance_OS_Capability_Acceptance_Contract_v3.md> > capability-audit.yaml
"""
import sys

RUN = "P2-AR-0049"
CANDIDATE_COMMIT = "0bad524d836f179964ffbac31972856ea6434682"
DIGEST = "e6332fc7d5af5c73adbe0f200003db30fe5a6fd0b7f24d047d3e340e6f972220"

# capability -> (title, first bullet source line, governing doc refs, health tiers, adoption obligation, residual risk)
CAPS = {
 "J1": ("Research becomes evidence", 598, ["DYNAMIC_AGENTIC_SOFTWARE_ENGINEERING_OPERATING_FRAMEWORK_v4.1.2.md Part XII §45"],
        ["G2", "G5"],
        "gov init/adopt must place spec/research/ under the repository contract and index it; post-adoption, `gov research check` must report every legacy research record that is not concluded, so a brownfield tree's narrative notes are not silently promoted to evidence.",
        "A concluded record's *content* is not judged: the OS checks that every J1 field is present and that influences are recorded, not that the measurements support the conclusion. An unsupported research conclusion is a Phase-4 hidden-fault class."),
 "J2": ("Experiment lifecycle", 608, ["DYNAMIC_AGENTIC_SOFTWARE_ENGINEERING_OPERATING_FRAMEWORK_v4.1.2.md Part XII §46"],
        ["G2", "G5"],
        "adopt/post-adoption must classify any pre-existing experiment directory and refuse to treat its outputs as production until promoted; `gov experiment check` must run in the adoption baseline.",
        "Reproducibility is judged by comparing recorded results under an acceptance mode; a reproduction that agrees because both runs share a hidden defect is not detected. Phase-4 fault class."),
 "K1": ("CIT-P", 623, ["DYNAMIC_AGENTIC_SOFTWARE_ENGINEERING_OPERATING_FRAMEWORK_v4.1.2.md Part XIII §47-48", "CIT-0001"],
        ["G1", "G2", "G4"],
        "adopt must build the graph and index before any CIT is proposed, or traversal is vacuous; post-adoption must re-run CIT-P over a sample of legacy records.",
        "Semantic candidates depend on the provisional retrieval profile (Phase 3); on an inadequate profile the supplementary set is weak, although the deterministic set is not."),
 "K2": ("CIT-E", 629, ["DYNAMIC_AGENTIC_SOFTWARE_ENGINEERING_OPERATING_FRAMEWORK_v4.1.2.md Part XIII §47-49", "CIT-0001"],
        ["G1", "G2", "G4", "G5"],
        "adopt/update must leave the CIT snapshot store (.governance-state/cit/) writable and outside the derived runtime directory, and must not carry a half-executed transaction across a migration (`gov trust recover-transactions`).",
        "Rollback restores the files the transaction touched from its snapshot; work committed to git between execute and rollback by another process is outside the transaction's control."),
 "K3": ("Automatic impact simulation", 640, ["DYNAMIC_AGENTIC_SOFTWARE_ENGINEERING_OPERATING_FRAMEWORK_v4.1.2.md Part XIII §47-48"],
        ["G1", "G2"],
        "adopt must classify the brownfield tree against the repository contract before materiality can be derived from paths; an unclassified product tree yields no behaviour_change class.",
        "Materiality is derived from record type, repository-contract class, path patterns and content heuristics. A material change in a path class the repository contract does not classify (a tree adopted with an incomplete contract) is not derived; the contract's own classification is the adoption obligation."),
 "K4": ("Impact radius", 650, ["DYNAMIC_AGENTIC_SOFTWARE_ENGINEERING_OPERATING_FRAMEWORK_v4.1.2.md Part XIII §49"],
        ["G1", "G2"],
        "the radius rules are kernel policy; adopt must not let a project overlay lower them (POLICY_PRECEDENCE floors).",
        "Agent allocation and a radius-differentiated rollback strategy are not produced. Orchestration compensates today by routing all change control at T3."),
 "L1": ("Contradiction resolution", 657, ["DYNAMIC_AGENTIC_SOFTWARE_ENGINEERING_OPERATING_FRAMEWORK_v4.1.2.md Part XIV §50"],
        ["G2", "G5"],
        "adopt must detect contradictions among legacy decisions before work is dispatched; the adoption baseline records them.",
        "Detection covers declared conflicts, supersession forks and decision conflicts keyed on decision_key/question/subject. Two decisions that contradict only in prose, with no shared key, are not detected."),
 "L2": ("Human Decision Gate package", 663, ["DYNAMIC_AGENTIC_SOFTWARE_ENGINEERING_OPERATING_FRAMEWORK_v4.1.2.md Part XIV §51-52"],
        ["G2", "G3", "human-gate"],
        "adopt must not import legacy 'approvals' as answered gates; they have no package and no signed answer.",
        "The package's fields are checked for substance, not for accuracy: a gate can carry a plausible but wrong impact statement. Phase-4 fault class."),
 "L3": ("Gate presentation", 675, ["DYNAMIC_AGENTIC_SOFTWARE_ENGINEERING_OPERATING_FRAMEWORK_v4.1.2.md Part XIV §51-53", "ARCH-0003 §3, §8", "OWNER-DIRECTIVE-0004"],
        ["G0", "G2", "G3", "human-gate"],
        "adopt/init must leave the machine provisioned with a root delegating `human-gate` before any governed answer is possible (OWNER-DECISION-P2-0002); an unprovisioned machine has no human channel at all.",
        "The support envelope is ARCH-0003 §1: a process that can write the administrator's machine state is outside it. `gov trust human-channel` reports whether the anchor is writable by the invoking account."),
 "L4": ("Non-global blocking", 682, ["DYNAMIC_AGENTIC_SOFTWARE_ENGINEERING_OPERATING_FRAMEWORK_v4.1.2.md Part XIV §54"],
        ["G0", "G2", "G5"],
        "adopt must generate the DAG before dispatch, or 'independent branch' has no meaning; FREEZE_WRITES/PAUSE state must survive adoption.",
        "Independence is judged from the declared graph. Two branches that share an undeclared file dependency are treated as independent."),
 "M1": ("T0-T3 or equivalent capability tiers", 690, ["DYNAMIC_AGENTIC_SOFTWARE_ENGINEERING_OPERATING_FRAMEWORK_v4.1.2.md Part XV §55-56"],
        ["G2", "G5"],
        "adopt writes MODEL_ROUTING_OVERRIDES.yaml from the overlay template; it must not be able to lower a kernel tier floor.",
        "No routing outcome resolves to T0, so the deterministic tier is declared but not selectable; deterministic work is instead performed by the OS itself outside the router."),
 "M2": ("Reasoning requirement", 696, ["DYNAMIC_AGENTIC_SOFTWARE_ENGINEERING_OPERATING_FRAMEWORK_v4.1.2.md Part XV §56"],
        ["G2"],
        "a task's declared minimum survives adoption/migration of the task schema.",
        "The router states the minimum; whether the harness actually runs the model at that reasoning level is recorded, not enforced, at run time (`gov route --record` accepts a lower-effort run)."),
 "M3": ("Role defaults", 699, ["DYNAMIC_AGENTIC_SOFTWARE_ENGINEERING_OPERATING_FRAMEWORK_v4.1.2.md Part XV §57"],
        ["G2"],
        "adopt must keep provider/model names out of project state; only the overlay carries them.",
        "Role minimum tiers come from the kernel ROLES.yaml; a project that declares its own roles outside the kernel taxonomy has no floor."),
 "M4": ("Empirical routing", 704, ["DYNAMIC_AGENTIC_SOFTWARE_ENGINEERING_OPERATING_FRAMEWORK_v4.1.2.md Part XV §58"],
        ["G2", "G5"],
        "the routing evidence file lives in the derived runtime directory; adopt/update must not discard it, or the comparison loses its history.",
        "The comparison surface cannot separate reasoning effort or show reviewer findings, so a routing decision taken from `gov route --report` cannot see two of the eight dimensions; the raw evidence retains them."),
 "N1": ("Structured checkpoint", 719, ["DYNAMIC_AGENTIC_SOFTWARE_ENGINEERING_OPERATING_FRAMEWORK_v4.1.2.md Part XVI §59"],
        ["G3"],
        "adopt must create spec/reports/checkpoints and classify it as evidence; a brownfield tree's prose 'session summaries' are not checkpoints (CHECKPOINT_POLICY.prose_summary_as_checkpoint: prohibited).",
        "files_changed comes from the working tree, so a change already committed and pushed before the checkpoint is not listed as changed."),
 "N2": ("Mandatory triggers", 730, ["DYNAMIC_AGENTIC_SOFTWARE_ENGINEERING_OPERATING_FRAMEWORK_v4.1.2.md Part XVI §59-60"],
        ["G3"],
        "adopt/update must preserve the previous checkpoint so the first boundary after an upgrade has a baseline to compare against.",
        "Boundaries are observed when a gov command runs; a session that performs work and then dies without any further gov invocation checkpoints nothing at that moment (the next session's first command observes it)."),
 "N3": ("Provider-independent checkpoint watchdog", 740, ["DYNAMIC_AGENTIC_SOFTWARE_ENGINEERING_OPERATING_FRAMEWORK_v4.1.2.md Part XVI §60"],
        ["G3", "G5"],
        "the command log and the git history are the watchdog's inputs; adopt into a tree with no git history degrades the file-change counter (the command counter still works).",
        "Context utilisation is necessarily caller-supplied (only the harness knows it); it can only make the watchdog fire earlier, never later."),
 "N4": ("Worker return contract", 745, ["DYNAMIC_AGENTIC_SOFTWARE_ENGINEERING_OPERATING_FRAMEWORK_v4.1.2.md Part XVI §61"],
        ["G3", "G5"],
        "the handoff records live in spec/; adopt must classify them and keep them indexed.",
        "The return's *content* is the worker's claim; the OS validates it against the task's manifest (receipt_validation) and records the result, but a plausible false claim is caught only by the close-time checks."),
}

# capability -> list of (bullet_index, status, implementation, automated, independent, gap)
B = {}
def b(cap, idx, status, impl, auto, indep, gap=None):
    B.setdefault(cap, {})[idx] = (status, impl, auto, indep, gap)

P = "PRESENT_AND_SUBSTANTIAL"
GOV = "heldout/RUN-ALL (DELTA_RUN=final2)"

# ---------------------------------------------------------------- J1 (8 bullets)
J1_IMPL = ["runtime/src/lifecycle/research.rs:52-70 (missing_fields)", "runtime/src/lifecycle/research.rs:240-343 (record)",
           "runtime/src/lifecycle/research.rs:389-433 (conclude)", "runtime/src/lifecycle/mod.rs:332-381 (cited_evidence / influenced_by)"]
for i, fld in enumerate(["question/reason", "method", "sources/data", "measurements", "uncertainty", "conclusion", "confidence"]):
    b("J1", i, P, J1_IMPL, ["cargo test --lib lifecycle::research::tests", "gov research check"],
      [f"evidence/J-research-experiment.out J1.1-J1.5: a record without '{fld}' is refused RESEARCH_INCOMPLETE and the refusal names the field; a record carrying all seven is CONCLUDED with state_class EVIDENCE"])
b("J1", 7, P, J1_IMPL + ["runtime/src/lifecycle/mod.rs:383-430 (record_influence/sync_influences)"],
  ["gov research check (INFLUENCE_NOT_RECORDED)", "gov research sync"],
  ["evidence/J-research-experiment.out J1.7-J1.9: a task that relies on the research is derived as an influence, the unrecorded backlink is a governance finding, and `gov research sync` records it"])

# ---------------------------------------------------------------- J2 (7 bullets)
J2_IMPL = ["runtime/src/lifecycle/experiment.rs:919-1114 (design)", "runtime/src/lifecycle/experiment.rs:1115-1180 (run)",
           "runtime/src/lifecycle/experiment.rs:1181-1239 (reproduce)", "runtime/src/lifecycle/experiment.rs:1240-1345 (conclude)",
           "runtime/src/orchestration/tasks.rs:2129 (PRODUCTION_MERGE_NOT_ALLOWED)"]
j2ev = {
 0: "J2.1/J2.3: a design with no hypothesis/method/data is refused EXPERIMENT_DESIGN_INCOMPLETE; a complete one is DESIGNED",
 1: "J2.1/J2.6: method and data/inputs are required at design, and the run binds every input by SHA-256",
 2: "J2.7-J2.9: an agreeing reproduction is judged to agree, a disagreeing one is not, and reproducibility falls to NOT_REPRODUCED",
 3: "J2.5/J2.6: the run records its results and their digest and moves the experiment to RUNNING",
 4: "J2.10: conclusion records the interpretation and moves the experiment to CONCLUDED",
 5: "J2.10: conclusion records decision_influence; J2.4 shows the lifecycle order is enforced",
 6: "J2.2/J2.11-J2.15: a design whose output is in the production tree is refused; an experiment task records production_merge_allowed false and its close is refused PRODUCTION_MERGE_NOT_ALLOWED when its mutations land in production, and the refusal disappears when they do not",
}
for i in range(7):
    b("J2", i, P, J2_IMPL, ["cargo test --lib lifecycle::experiment::tests", "gov experiment check"],
      [f"evidence/J-research-experiment.out {j2ev[i]}"])

# ---------------------------------------------------------------- K1 (4)
K1_IMPL = ["runtime/src/cit/mod.rs:124-432 (propose)", "runtime/src/cit/mod.rs:433-855 (simulate)",
           "runtime/src/cit/materiality.rs:1159 (classify_paths)", "runtime/src/graph/mod.rs (traversal)"]
k1ev = {
 0: "K1.1/K3.*: a change proposed as `editorial` to a governed record is derived material and auto-simulated; the traversal seeds on the manifest's targets and reaches F-0001, the reports and both tasks over typed edges",
 1: "K1.3: the impact carries semantic_candidates, each with its `routes` (lexical + semantic), alongside the deterministic set",
 2: "K1.4/K4.1: an impact radius is produced (R1 for the requirement change, R0 and R5 for the two K4 cases)",
 3: "K1.5: eight human-readable consequences are produced, naming retest, revalidation, stale tests, readiness, material classes, approval and rollback",
}
for i in range(4):
    b("K1", i, P, K1_IMPL, ["cargo test --test certification ws04*", "gov cit simulate"],
      [f"evidence/K12-cit-p-and-e.out {k1ev[i]}", "evidence/K34-materiality-and-radius.out"])

# ---------------------------------------------------------------- K2 (8)
K2_IMPL = ["runtime/src/cit/mod.rs:856-1000 (approve)", "runtime/src/cit/mod.rs:1548-1900 (execute)",
           "runtime/src/cit/propagation.rs:271-1140 (plan/apply)", "runtime/src/cit/binding.rs (writes binding)",
           "runtime/src/t2.rs (seal)"]
k2ev = {
 0: "K2.3-K2.6: the CIT's own human gate decides; execution before an honoured answer is refused, and the approved CIT commits",
 1: "K2.7/K2.13: the manifest's declared operation is what lands, and the executed writes are bound in the CIT's sealed state",
 2: "K2.7: the authoritative record carries exactly the manifest's change",
 3: "K2.8-K2.11: the DONE task is marked for revalidation, a revalidation task is generated, the acceptance obligation goes stale and the checkpoint that captured the pre-change state is reported stale",
 4: "K2.13b: the tool registry and the adapter manifest, deliberately damaged before execution, are rebuilt from the committed state",
 5: "K2.12: the index manifest hash changes across CIT-E (index_refresh.refreshed true in the execution record)",
 6: "K2.14: a transaction that introduces a dangling reference fails verification (VERIFICATION_FAILED)",
 7: "K2.14-K2.16: the failed transaction is ROLLED_BACK, its file write is removed and the authoritative record is restored; K2.6 shows the commit path",
}
for i in range(8):
    b("K2", i, P, K2_IMPL, ["cargo test --test certification ws04*/ws06*", "gov cit execute"],
      [f"evidence/K12-cit-p-and-e.out {k2ev[i]}"])

# ---------------------------------------------------------------- K3 (8)
K3_IMPL = ["runtime/src/cit/materiality.rs:1-1158 (the eight classes; kernel floor)",
           "runtime/src/cit/mod.rs:124-432 (effective triggers = declared + derived)",
           "runtime/src/orchestration/tasks.rs:2160 (MATERIAL_CHANGE_REQUIRES_CIT)",
           "framework/policies/CHANGE_POLICY.yaml auto_simulate_triggers/human_gate_triggers"]
k3names = ["architecture", "behaviour", "interfaces", "security", "governance/policy", "infrastructure cost",
           "acceptance criteria", "data migration"]
k3probe = ["K3.architecture", "K3.behaviour", "K3.interfaces", "K3.security", "K3.governance",
           "K3.infrastructure", "K3.acceptance", "K3.migration"]
k3task = ["K3.intask.architecture_change", "K3.intask.behaviour_change", "K3.intask.interface_change",
          "K3.intask.security_change", "K3.intask.governance_change", "K3.intask.infrastructure_cost",
          "K3.intask.acceptance_criteria_change", "K3.intask.data_migration"]
for i in range(8):
    b("K3", i, P, K3_IMPL, ["cargo test --test certification repair2/ws04r3", "gov cit classify"],
      [f"evidence/K34-materiality-and-radius.out {k3probe[i]}: a {k3names[i]} change proposed with the declared trigger 'editorial' is derived material, auto-simulated and gated",
       f"evidence/K34-materiality-and-radius.out {k3task[i]}: the same change made inside an ordinary task is refused at close (for product-source behaviour, classified and left to the task contract, as the kernel rule states)"])

# ---------------------------------------------------------------- K4 (1)
b("K4", 0, "PARTIAL",
  ["runtime/src/cit/mod.rs:433-855 (radius -> depth, semantic breadth, gate)",
   "framework/policies/CHANGE_POLICY.yaml graph_traversal_depth_by_radius / semantic_candidates_by_radius / human_gate_triggers",
   "framework/policies/MODEL_ROUTING_POLICY.yaml radius_minimum_tier", "runtime/src/routing.rs:64-180 (route)"],
  ["cargo test --test certification ws04*", "gov cit simulate", "gov route --radius"],
  ["evidence/K34-materiality-and-radius.out K4.1-K4.5: the radius is produced and sets the traversal depth (0 at R0, 5 at R5), the semantic breadth (0 vs 24 candidates), whether human approval is required (false vs true) and, through MODEL_ROUTING_POLICY.radius_minimum_tier, the model tier (T1 T1 T2 T2 T3 T3 across R0..R5); the test set is the tests inside the traversed radius (evidence/K12-cit-p-and-e.out K2.10)",
   "evidence/K34-materiality-and-radius.out K4.6/K4.7 (both FAIL): the rollback consequence the OS states is byte-identical at R0 and R5, and no output of the impact names the agents or reviewers the change needs"],
  "Two of the six effects the bullet lists are absent: the radius does not determine the agents/reviewers, and it does not differentiate the rollback consequence or plan.")

# ---------------------------------------------------------------- L1 (4)
L1_IMPL = ["runtime/src/context/contradictions.rs:1-600 (precedence, detect_among, route, resolution)",
           "runtime/src/context/manifest.rs:1029 (contradictions block the manifest)",
           "runtime/src/orchestration/gates.rs:1357-1700 (answer: agent_resolvable_when, independent assessment, rationale)",
           "framework/policies/HUMAN_GATE_POLICY.yaml agent_resolvable_when/human_only_triggers"]
l1ev = {
 0: "L1.1: a superseded input is resolved by precedence and is not raised as a contradiction",
 1: "L1.6-L1.8: the session that declared the assessment may not resolve on it; another session's L3+ agent may, within agent_resolvable_when, and the rationale is recorded",
 2: "L1.2-L1.5/L1.9: an undecidable contradiction blocks the task's manifest, the task cannot be claimed, a contradiction gate is raised at dispatch, and an irreversible R4 human-only gate is refused to an agent",
 3: "L1.8: the resolution's rationale is stored on the decision; `gov decide --evidence` refuses an evidence id that is not a governed record (runtime/src/orchestration/gates.rs:1414-1424)",
}
for i in range(4):
    b("L1", i, P, L1_IMPL, ["cargo test --test certification ws03*", "gov context manifest", "gov decide"],
      [f"evidence/L12-contradictions-and-package.out {l1ev[i]}"])

# ---------------------------------------------------------------- L2 (10)
L2_IMPL = ["runtime/src/orchestration/gates.rs:78-297 (package_fields, non_substantive, validate_package)",
           "runtime/src/orchestration/gates.rs:298-378 (option_authorises, next_actions)",
           "framework/policies/HUMAN_GATE_POLICY.yaml decision_package_fields/package_non_substantive_values/system_gate_package"]
l2fields = ["plain-language question", "why now", "current state", "options", "impact", "reversibility",
            "cost/rework", "recommendation", "confidence", "exact permitted next actions"]
for i, f in enumerate(l2fields):
    if f == "options":
        ev = "L2.2/L2.4/L2.6/L2.7: a package with no options is refused, and an option the package does not offer is refused even when the owner signed it"
    elif f == "exact permitted next actions":
        ev = "L2.5: the permitted next actions name this gate id and carry no `<gate>` placeholder; L2.8: a system-raised (contradiction) gate carries a complete, substantive package with four real options"
    else:
        ev = f"L2.1-L2.3: a gate with only a question is refused GATE_PACKAGE_INCOMPLETE; a package missing '{f}' is refused; a placeholder value ('', 'not assessed', 'tbd') is not substantive content"
    b("L2", i, P, L2_IMPL, ["cargo test --test certification ws03*", "gov gate create"],
      [f"evidence/L12-contradictions-and-package.out {ev}"])

# ---------------------------------------------------------------- L3 (5)
L3_IMPL = ["runtime/src/human_channel.rs:1-806 (anchor, signed answer, receipt, use-time re-verification)",
           "runtime/src/orchestration/gates.rs:787-874 (present, acknowledge)",
           "runtime/src/orchestration/gates.rs:970-1270 (verified_answer_in, task_gate_authorisation, human_approval_for)",
           "runtime/src/t2.rs (records are OS-sealed state)",
           "framework/policies/HUMAN_GATE_POLICY.yaml human_channel.standalone_anchor_when_unprovisioned: false (P2-ADJ-0001)"]
l3ev = {
 0: "L3.1-L3.3: a newly raised gate is PENDING and not presented; hand-writing presented_in_chat in the record does not make it answerable (GATE_NOT_PRESENTED)",
 1: "L3.4-L3.10: rendering to an agent's stdout, in --json, or by an L1 worker never marks it presented to the human; only an owner-signed receipt (or the signed answer) does, and a receipt signed by an undelegated key is refused HUMAN_RECEIPT_UNAUTHENTICATED",
 2: "L3.11-L3.13: an acknowledged gate is still only PRESENTED, carries no answer, and the work it blocks stays blocked",
 3: "L3.20-L3.25: a declining answer leaves the task blocked; a revoked gate withdraws the authorisation it had given; an answer signed for one gate cannot authorise another; and a CIT approval does not survive a widened manifest (APPROVAL_STALE)",
 4: "L3.14-L3.19: --by human, --by <any string>, --role human, GOV_ROLE=human and GOV_HUMAN_GATE_APPROVED all fail to produce a human approval; a hand-written ANSWERED gate plus a matching decision record is T2 BROKEN, is not honoured, and is reported by the governance suite",
}
for i in range(5):
    b("L3", i, P, L3_IMPL, ["cargo test --test certification ws03*/ws03_r3", "gov gate present/decide", "gov audit os_binding_integrity"],
      [f"evidence/L34-presentation-and-blocking.out {l3ev[i]}",
       "evidence/X-crosscutting.out X2.1-X2.8: the answer re-verifies on the owner's second provisioned machine, is FOREIGN under another owner's root, and an unprovisioned machine has no human channel at all"])

# ---------------------------------------------------------------- L4 (2)
L4_IMPL = ["runtime/src/orchestration/dag.rs (runnable/blocked/waiting_human, human_gate_dependencies)",
           "runtime/src/orchestration/gates.rs:582-603 (block_tasks), 1227-1270 (task_gate_authorisation)",
           "runtime/src/orchestration/control.rs (FREEZE_WRITES/PAUSE and gov resume)",
           "runtime/src/scheduler/catalogue.rs:83-170 (scoped hard blocks and their remedies)"]
b("L4", 0, P, L4_IMPL, ["cargo test --test certification ws05*", "gov task dag", "gov health status"],
  ["evidence/L34-presentation-and-blocking.out L4.1-L4.3: the gate holds its own branch in waiting_human while the independent branch stays runnable and is actually claimed, and the DAG names the human-gate dependencies",
   "evidence/L34-presentation-and-blocking.out AV.1-AV.6 and evidence/X-crosscutting.out X1.1-X1.7: every refusal is typed and names its subject, the block's remedies stay available (including handoff.create), and no block refuses its own remedy (cit.execute and update.apply are admitted as remedies)"])
b("L4", 1, P, L4_IMPL, ["cargo test --test certification failure_injection", "gov freeze-writes / gov resume"],
  ["evidence/L34-presentation-and-blocking.out L4.4-L4.6: only the explicit global stop (FREEZE_WRITES, a policy state an L4 sets) refuses everything that mutates; read-only planning stays available under it and `gov resume` lifts it"])

# ---------------------------------------------------------------- M1 (4)
M1_IMPL = ["runtime/src/routing.rs:24-180 (tier_for_class, route)", "framework/policies/MODEL_ROUTING_POLICY.yaml tiers/task_class_minimum_tier",
           "framework/roles/ROLES.yaml minimum_tier", "runtime/src/policy_precedence.rs (overlay floors)"]
b("M1", 0, "ABSENT", M1_IMPL, ["gov route --class <every declared class>"],
  ["evidence/M-model-routing.out M1.2 (FAIL): routing every task class the kernel declares, at the lowest-floor role, yields only T1, T2 and T3; no class, role or radius resolves to T0, and the overlay can only raise"],
  "No routing outcome resolves to the declared T0 (deterministic / no-LLM) tier: the kernel's lowest task-class minimum is T1 and every kernel role's minimum_tier is >= T1.")
for i, name in enumerate(["lightweight", "strong engineering", "frontier/high-reasoning"], start=1):
    b("M1", i, P, M1_IMPL, ["cargo test --test certification ws03*", "gov route"],
      [f"evidence/M-model-routing.out M1.1/M1.3-M1.5: the {name} route is reached (documentation -> T1, implementation -> T2, architecture/security -> T3), an overlay that lowers a kernel floor does not take effect and the refused weakening is reported by `gov policy overrides`"])

# ---------------------------------------------------------------- M2 (1)
b("M2", 0, P, ["runtime/src/routing.rs:64-180 (task minimum_reasoning/minimum_model_tier raise the requirement)",
               "framework/policies/MODEL_ROUTING_POLICY.yaml reasoning_levels", "framework/roles/ROLES.yaml default_reasoning"],
  ["cargo test --test certification ws03*", "gov route --task"],
  ["evidence/M-model-routing.out M2.1/M2.2: a task declaring extra_high/T3 routes at T3 extra_high, and a task declaring 'low' cannot route below its role's floor (high)"])

# ---------------------------------------------------------------- M3 (2)
M3_IMPL = ["framework/roles/ROLES.yaml (orchestrator/memory-engineer/independent-auditor minimum_tier T3)",
           "runtime/src/routing.rs:24-180 (providers/models read only from MODEL_ROUTING_OVERRIDES.yaml)"]
b("M3", 0, P, M3_IMPL, ["gov route --role"],
  ["evidence/M-model-routing.out M3.1/M3.4: orchestration, memory and audit roles route at T3, and an overlay that lowers the orchestrator's reasoning default is refused"])
b("M3", 1, P, M3_IMPL, ["gov route", "grep over spec/**"],
  ["evidence/M-model-routing.out M3.2/M3.3: mapping providers in the overlay makes the router choose provider-alpha/alpha-large, and no provider or model name appears anywhere in project state (spec/**)"])

# ---------------------------------------------------------------- M4 (8)
M4_IMPL = ["runtime/src/routing.rs:186-272 (record: every MODEL_ROUTING_POLICY.record_evidence field required)",
           "runtime/src/routing.rs:273-301 (report: groups by provider|model|task_class)",
           "runtime/src/observability.rs (telemetry mirror)",
           "framework/policies/MODEL_ROUTING_POLICY.yaml record_evidence"]
m4 = [("model/provider", P, "M4.1/M4.3: every run records model and provider, and the report groups by both", None),
      ("task class", P, "M4.1/M4.3: every run records task_class and the report groups by it", None),
      ("reasoning effort", "ABSENT",
       "M4.5 (FAIL): reasoning_effort is required at record time and kept in the raw evidence, but `gov route --report` and the model_routing block of `gov telemetry summary` group by provider|model|task_class only, so two runs of one model at extra_high and at low are merged into a single row (pass_rate 0.5)",
       "The comparison surface cannot separate runs by reasoning effort; the dimension exists only in the raw JSONL."),
      ("cost", P, "M4.1/M4.4: cost is required and reported as avg_cost", None),
      ("latency", P, "M4.1/M4.4: latency_ms is required and reported as avg_latency_ms", None),
      ("pass/fail", P, "M4.1/M4.4: pass is required and reported as pass_rate", None),
      ("repair count", P, "M4.1/M4.4: repair_count is required and reported as avg_repairs", None),
      ("reviewer findings", "ABSENT",
       "M4.6/M4.7 (FAIL): reviewer_findings is required at record time (M4.2 shows a run missing a declared field is refused) but appears in no column of `gov route --report` or `gov telemetry summary`",
       "The comparison surface reports no reviewer-findings figure; the dimension exists only in the raw JSONL.")]
for i, (name, st, ev, gap) in enumerate(m4):
    b("M4", i, st, M4_IMPL, ["gov route --record", "gov route --report", "gov telemetry summary"],
      [f"evidence/M-model-routing.out {ev}"], gap)

# ---------------------------------------------------------------- N1 (9)
N1_IMPL = ["runtime/src/checkpoints.rs:363-586 (create: every CHECKPOINT_POLICY.fields entry)",
           "runtime/src/checkpoints.rs:301-362 (task_inputs: inputs/input_state)",
           "runtime/src/checkpoints.rs:146-235 (routing_digest, governed_state_digest, observe_state)",
           "framework/policies/CHECKPOINT_POLICY.yaml fields"]
n1ev = {
 0: "N1.1: session, role, task, mode and claim are all recorded (the claim carries task_id, session_id, role and expiry)",
 1: "N1.1: last_completed_step is recorded",
 2: "N1.1: next_action is recorded",
 3: "N1.1: pending_decisions and open_questions are recorded; open_questions is derived by the OS from pending gates and blocking contradictions (runtime/src/checkpoints.rs:453-489), so it is empty only when there are none",
 4: "N1.1: open_transactions is recorded",
 5: "N1.1: files_changed is recorded (from the working tree, with untracked directories expanded)",
 6: "N1.1: tests_status is recorded",
 7: "N1.1/N1.2: context_packet_hash is recorded and bound together with a state reference (repo commit, governed-state digest and the index manifest hash)",
 8: "N1.1/N1.3: memory_snapshot is recorded, and every mandatory input is recorded with its delivered and current hash",
}
for i in range(9):
    b("N1", i, P, N1_IMPL, ["cargo test --test certification ws04r2/ws04r3", "gov checkpoint create"],
      [f"evidence/N-checkpoints-and-handoffs.out {n1ev[i]}"])

# ---------------------------------------------------------------- N2 (8)
N2_IMPL = ["runtime/src/checkpoints.rs:236-300 (triggers_between, state_triggers)",
           "runtime/src/checkpoints.rs:721-745 (observe_boundaries)", "runtime/src/checkpoints.rs:746-802 (watchdog)",
           "runtime/src/checkpoints.rs:803-900 (session_close)", "runtime/src/cit/mod.rs:1548+ (accepted CIT)",
           "runtime/src/orchestration/handoffs.rs:168-337 (before_handoff)",
           "framework/policies/CHECKPOINT_POLICY.yaml mandatory_triggers"]
n2ev = {
 0: "N2.1: releasing and re-claiming a task is observed as a task_transition boundary and checkpointed",
 1: "N2.2: an owner-signed answer to an R3 gate is observed as a material_decision boundary and checkpointed",
 2: "N2.3: executing an approved CIT writes its own checkpoint with trigger accepted_cit",
 3: "N2.4: 30 changed repository files cross CHECKPOINT_POLICY.watchdog.max_operations_between_checkpoints and are checkpointed as significant_mutation",
 4: "N2.5: `gov handoff create` writes the before_handoff checkpoint automatically",
 5: "N2.6: changing the provider map is observed as a before_model_switch boundary (the routing digest changed)",
 6: "N2.7: `gov session close` writes the before_session_close checkpoint",
 7: "N2.8: context utilisation over CHECKPOINT_POLICY.watchdog.context_utilisation_threshold fires a checkpoint with reason context_utilisation (the known-compaction boundary)",
}
for i in range(8):
    b("N2", i, P, N2_IMPL, ["cargo test --test certification ws04r2", "gov checkpoint watchdog", "gov session close"],
      [f"evidence/N-checkpoints-and-handoffs.out {n2ev[i]}"])

# ---------------------------------------------------------------- N3 (3)
N3_IMPL = ["runtime/src/checkpoints.rs:746-802 (watchdog: commands_since + files_changed_since, observed by the OS)",
           "runtime/src/checkpoints.rs:619-720 (freshness_of/freshness)",
           "runtime/src/checkpoints.rs:803-900 (session_close: degraded, never refused)",
           "runtime/src/orchestration/handoffs.rs:33-152 (handoff_freshness)"]
b("N3", 0, P, N3_IMPL, ["gov checkpoint watchdog"],
  ["evidence/N-checkpoints-and-handoffs.out N3.1/N3.6: with the caller's counters at zero the watchdog still fires on gov commands and changed files it observed itself; its inputs are the command log and git, with no proprietary hook"])
b("N3", 1, P, N3_IMPL, ["gov checkpoint freshness"],
  ["evidence/N-checkpoints-and-handoffs.out N3.2/N3.3: a checkpoint over current state is CURRENT, and after a CIT changed an input it recorded it is STALE, with the upstream change and the changed input named"])
b("N3", 2, P, N3_IMPL, ["gov session close", "gov handoff create"],
  ["evidence/N-checkpoints-and-handoffs.out N3.4/N3.5: session close over stale state is explicitly degraded and not resumable (never refused), and a handoff over stale state reports the stale inputs, the invalidated previous packet and the refreshed one"])

# ---------------------------------------------------------------- N4 (1)
b("N4", 0, P, ["runtime/src/orchestration/handoffs.rs:338-444 (return_result)",
               "framework/schemas/worker-return.schema.json", "runtime/src/context/receipt.rs (receipt_validation)"],
  ["cargo test --test certification ws05*", "gov handoff return"],
  ["evidence/N-checkpoints-and-handoffs.out N4.1-N4.4: a schema-valid worker return is accepted, persisted as a governed record on disk, survives the sub-session, and is read back by a fresh session with no conversation state",
   "evidence/X-crosscutting.out X3.1/X3.2: the same schema-valid worker return is accepted by `gov task close --report` without a schema failure (the iteration-0 collision on `status` no longer occurs)"])


def esc(s):
    return '"' + str(s).replace("\\", "\\\\").replace('"', '\\"') + '"'


def main():
    src = open(sys.argv[1]).read().split("\n")
    out = []
    out.append("schema: governance-os.phase-2.capability-audit")
    out.append("schema_version: 1")
    out.append(f"run_id: {RUN}")
    out.append("family: delta")
    out.append("candidate: cap2-candidate-1")
    out.append(f"candidate_commit: {CANDIDATE_COMMIT}")
    out.append(f"product_code_digest: {DIGEST}")
    out.append("capabilities:")
    for cap, (title, first, docs, tiers, adopt, risk) in CAPS.items():
        bullets = B[cap]
        n = len(bullets)
        lines = [src[first - 1 + i] for i in range(n)]
        sts = [bullets[i][0] for i in range(n)]
        status = P if all(s == P for s in sts) else ("PARTIAL" if any(s == P for s in sts) else "ABSENT")
        if cap == "K4":
            status = "PARTIAL"
        out.append(f"  - capability: {cap}")
        out.append(f"    title: {esc(title)}")
        out.append(f"    source_ref: Governance_OS_Capability_Acceptance_Contract_v3.md:{first}-{first + n - 1}")
        out.append("    governing_document_refs: [" + ", ".join(esc(d) for d in docs) + "]")
        out.append("    requirement_class: ORIGINAL")
        out.append(f"    status: {status}")
        out.append(f"    status_justification: {esc(JUSTIFY[cap])}")
        out.append("    na_reason_normative_text: null")
        out.append(f"    partial_qualification_impact: {esc(PARTIAL_IMPACT[cap]) if cap in PARTIAL_IMPACT else 'null'}")
        out.append("    bullets:")
        for i in range(n):
            st, impl, auto, indep, gap = bullets[i]
            text = lines[i].strip()
            if text.startswith("- [ ] "):
                text = text[6:]
            out.append(f"      - bullet: {esc(text)}")
            out.append(f"        source_line: {first + i}")
            out.append(f"        status: {st}")
            out.append("        implementation_evidence: [" + ", ".join(esc(x) for x in impl) + "]")
            out.append("        automated_evidence: [" + ", ".join(esc(x) for x in auto) + "]")
            out.append("        independent_evidence:")
            for e in indep:
                out.append(f"          - {esc(e)}")
            out.append(f"        gap: {esc(gap) if gap else 'null'}")
        out.append("    health_scheduler_tiers: [" + ", ".join(tiers) + "]")
        out.append("    evidence_owners: [" + ", ".join(EVIDENCE_OWNERS[cap]) + "]")
        out.append(f"    evidence_owner_actually_runs: {esc(OWNER_RUNS[cap])}")
        out.append("    freshness:")
        out.append(f"      state: {FRESHNESS[cap][0]}")
        out.append("      invalidation_inputs: [" + ", ".join(esc(x) for x in FRESHNESS[cap][1]) + "]")
        out.append(f"      invalidation_demonstrated: {FRESHNESS[cap][2]}")
        out.append(f"      invalidation_evidence: {esc(FRESHNESS[cap][3]) if FRESHNESS[cap][3] else 'null'}")
        out.append("    qualification_coverage:")
        qc = QUAL[cap]
        for k in ("repo_a_challenge", "repo_b_challenge", "hidden_oracle_fault_class", "chaos_scale_soak", "retrieval_challenge"):
            out.append(f"      {k}: {esc(qc[k])}")
        out.append(f"      not_challengeable: {esc(qc['not_challengeable']) if qc.get('not_challengeable') else 'null'}")
        out.append(f"    adoption_obligation: {esc(adopt)}")
        out.append(f"    residual_risk: {esc(risk)}")
        out.append("    findings: [" + ", ".join(FINDINGS.get(cap, [])) + "]")
    print("\n".join(out))


JUSTIFY = {
 "J1": "All eight bullets are executably evidenced on this candidate: each J1 field is individually required before a research output becomes governed evidence, and the influence backlink is derived, reported when unrecorded and back-filled.",
 "J2": "All seven bullets are executably evidenced: the lifecycle states are enforced in order, reproducibility is judged by the OS from the recorded runs rather than declared, and an experiment task whose mutations land in the production tree cannot close.",
 "K1": "All four bullets are executably evidenced: a change proposed as editorial is derived material and traversed deterministically from the manifest's targets, semantic/lexical candidates supplement it with their routes, a radius is produced and eight human-readable consequences are surfaced.",
 "K2": "All eight bullets are executably evidenced end to end on one transaction: gate-decided approval, the manifest's operations, the authoritative update, propagation into completed work, its evidence, packets and checkpoints, derived-view regeneration, index refresh, verification, and atomic commit or rollback.",
 "K3": "All eight material classes are executably evidenced twice: proposed through a CIT with the declared trigger set to 'editorial' (derived material, auto-simulated, gated) and made inside an ordinary task (refused at close, except product-source behaviour, which the kernel rule leaves to the task contract and which is still classified material).",
 "K4": "The radius is produced and drives traversal depth, semantic breadth, test scope and human approval, and MODEL_ROUTING_POLICY.radius_minimum_tier maps it to a model tier. Two of the six effects the bullet names are not produced at all: the agents/reviewers a change needs, and a radius-differentiated rollback.",
 "L1": "All four bullets are executably evidenced: precedence resolves supersession before any contradiction is raised, an undecidable contradiction blocks the manifest and is routed to a gate, agent resolution is confined to an assessed, independent, in-policy case, and the rationale is recorded with evidence references checked against governed records.",
 "L2": "All ten package fields are enforced as substantive content on agent-raised and system-raised gates alike, options must be real, answers must name an offered option even when owner-signed, and the permitted next actions are derived by the OS for the exact gate.",
 "L3": "All five bullets are executably evidenced, including the full fabrication attack surface: CLI flags, environment variables, role claims and hand-written gate/decision records all fail to produce a human approval, and only an owner-signed document verified against the provisioned root's human-gate delegation does.",
 "L4": "Both bullets are executably evidenced, together with the availability rule: a gate holds only its own branch, independent work stays runnable and claimable, every refusal is typed and names its scope, listed remedies stay available (including handoff.create), and only the explicit global stop refuses everything that mutates.",
 "M1": "Three of the four tiers are reachable routing outcomes and the overlay cannot lower a kernel floor, but no class, role or radius resolves to the declared T0 deterministic/no-LLM tier.",
 "M2": "The single bullet is executably evidenced: a task declares a minimum reasoning level, the router honours it, and a task cannot declare its way below its role's floor.",
 "M3": "Both bullets are executably evidenced: orchestration, memory and audit roles route at T3, and provider/model names resolve only from the overlay, leaving project state free of them.",
 "M4": "Six of the eight dimensions are comparable on the product's comparison surface. Reasoning effort and reviewer findings are required at record time and kept in the raw evidence, but neither `gov route --report` nor `gov telemetry summary` can group by or report them, so the comparison merges runs that differ only in reasoning effort and shows no reviewer-findings figure.",
 "N1": "All nine recorded items are executably evidenced on a real checkpoint, including the OS-derived open questions, the context packet hash bound to a state reference, and every mandatory input with its delivered and current hash.",
 "N2": "All eight mandatory triggers fire: four are checkpointed automatically by the operation itself and four are observed as boundaries and checkpointed at the next gov invocation.",
 "N3": "All three bullets are executably evidenced: the watchdog fires on state the OS observes itself with the caller's counters at zero, a checkpoint goes STALE when the state it captured changes, and both session close and handoff are explicitly degraded (never silently) over stale state.",
 "N4": "The single bullet is executably evidenced: a schema-valid structured return is accepted, persisted as a governed record, survives the sub-session and is read back by a fresh session with no conversation state.",
}

PARTIAL_IMPACT = {
 "K4": "CANNOT_UNDERMINE. The two missing effects are allocation and recovery *planning* outputs, not governance decisions: the radius already decides what is traversed, what is retested, whether the human must approve, and (through radius_minimum_tier) the tier floor, and rollback itself is implemented and demonstrated atomically (K2.14-K2.16). A qualification scenario is scored on whether the OS admitted or refused work and whether propagation reached the right artefacts; neither depends on the OS naming reviewers or varying the rollback text by radius. The risk it leaves is under-resourcing a wide change, which qualification measures as a rework/repair count, not as a governance failure.",
 "M1": "COULD_UNDERMINE only for a qualification design that scores cost or determinism of routing; it CANNOT_UNDERMINE the governance properties under test. No T0 route means deterministic work cannot be *routed* to a no-LLM tier, but the deterministic work the contract lists (SQL, graph, AST, parsing, validation, tests, generation) is performed by the OS itself outside the router, and every governance decision in this baseline was produced deterministically with no model at all. The concrete exposure is cost and latency on trivial classes, which Phase-4 measures through M4 telemetry rather than as a governance fault.",
 "M4": "CANNOT_UNDERMINE. Both missing dimensions are recorded per run and retained in routing/evidence.jsonl, so an advanced-qualification analysis can compute them offline; what is missing is the product's own comparison view. No governance admission, refusal or propagation decision depends on it. It does weaken the empirical-routing feedback loop the framework intends (a wrong reasoning level or a reviewer-finding regression will not surface in the product's report), which is a Phase-4 measurement-quality risk rather than a Phase-2 capability gap in what the OS enforces.",
}

EVIDENCE_OWNERS = {
 "J1": ["G2", "G5", "independent-heldout"], "J2": ["G2", "G5", "independent-heldout"],
 "K1": ["G1", "G2", "G4", "independent-heldout"], "K2": ["G1", "G2", "G4", "G5", "independent-heldout"],
 "K3": ["G1", "G2", "independent-heldout"], "K4": ["G1", "G2", "independent-heldout"],
 "L1": ["G2", "G5", "independent-heldout"], "L2": ["G2", "G3", "human-gate", "independent-heldout"],
 "L3": ["G0", "G2", "G3", "human-gate", "independent-heldout"], "L4": ["G0", "G2", "G5", "independent-heldout"],
 "M1": ["G2", "G5", "independent-heldout"], "M2": ["G2", "independent-heldout"],
 "M3": ["G2", "independent-heldout"], "M4": ["G2", "G5", "independent-heldout"],
 "N1": ["G3", "independent-heldout"], "N2": ["G3", "independent-heldout"],
 "N3": ["G3", "G5", "independent-heldout"], "N4": ["G3", "G5", "independent-heldout"],
}

OWNER_RUNS = {
 "J1": "true — the governance suite family research_experiment_data_lifecycle runs at G2/G5 and produced the INFLUENCE_NOT_RECORDED finding on this candidate (evidence/J-research-experiment.out J1.8).",
 "J2": "true — the same family reports production-merge detection on this candidate (evidence/J-research-experiment.out J2.13).",
 "K1": "partial — G1/G2 run the change-control families and the CIT itself simulates on every proposal; there is no scheduler check that re-derives an impact set independently of cit::simulate, so the automated owner observes the transaction rather than the traversal.",
 "K2": "true — CIT-E runs its own verification (schema, graph integrity, index freshness) inside the transaction and the suite's graph_integrity/os_binding_integrity families observe the result (evidence/K12-cit-p-and-e.out K2.2b, K2.14).",
 "K3": "true — task close calls the same classifier at G2 (evidence/K34-materiality-and-radius.out K3.intask.*), and `gov cit classify` exposes it read-only.",
 "K4": "partial — the radius and its traversal/approval effects are observed at G1/G2; nothing observes the two effects that are absent, because there is nothing to observe.",
 "L1": "true — contradictions are detected by the suite (verification/reporting.rs:843-847 uses contradictions::detect_all) and block the manifest at dispatch.",
 "L2": "true — package validation runs on every gate creation, and the human-gate evidence class is the signed answer itself.",
 "L3": "true — os_binding_integrity reports a forged gate at high severity on this candidate (evidence/L34-presentation-and-blocking.out L3.19), and every consumer re-verifies the signed answer at use time.",
 "L4": "true — G0 is the hard-block guard exercised in evidence/X-crosscutting.out X1.*, and the DAG is recomputed on every dispatch.",
 "M1": "partial — `gov policy overrides` and doctor D027 observe a refused weakening (evidence/M-model-routing.out M1.5); no check asserts that a T0 route exists, which is why the absence is silent.",
 "M2": "true — the router applies the minimum on every route; `gov route --record` accepts a run below it without flagging (recorded as a later-lifecycle note).",
 "M3": "true — role floors are applied on every route and the overlay is evaluated through POLICY_PRECEDENCE.",
 "M4": "partial — `gov route --record` enforces the declared evidence fields at G2 (evidence/M-model-routing.out M4.2); no check asserts that the comparison surface can separate them.",
 "N1": "true — every checkpoint is written through checkpoints::create, which fills each declared field, and G3 is the checkpoint/handoff tier.",
 "N2": "true — four triggers checkpoint inside the operation and four are observed by checkpoints::observe_boundaries on the next gov invocation (evidence/N-checkpoints-and-handoffs.out N2.1-N2.8).",
 "N3": "true — `gov checkpoint freshness`, `gov session close` and `gov handoff create` each compute freshness on this candidate.",
 "N4": "true — `gov handoff return` validates against the worker-return schema and records receipt_validation against the task's manifest.",
}

FRESHNESS = {c: ("FRESH_FOR_CANDIDATE",
                 ["runtime/kernel implementation", "governing contract/policy", "schema", "authoritative spec/decision",
                  "relevant source files", "relevant index manifest"],
                 "true",
                 "evidence/X-crosscutting.out X4.1/X4.2: changing a governing policy changes the evidence currency key and the currency report names the changed classes; evidence/K12-cit-p-and-e.out K2.8-K2.11 and evidence/N-checkpoints-and-handoffs.out N3.3 show a CIT invalidating completed work, its evidence, its packet and its checkpoint")
             for c in CAPS}
FRESHNESS["M4"] = ("FRESH_FOR_CANDIDATE",
                   ["runtime/kernel implementation", "governing contract/policy", "model/retrieval profile"],
                   "true",
                   "evidence/N-checkpoints-and-handoffs.out N2.6: changing the provider map changes the routing digest and is observed as a before_model_switch boundary, so evidence taken under the old map is superseded")

QUAL = {
 "J1": {"repo_a_challenge": "A greenfield repository where a decision cites a research record that was never concluded: the OS must hold it NARRATIVE and refuse it as citable evidence.",
        "repo_b_challenge": "A brownfield tree with a docs/research directory of prose notes carrying ids: adoption must not promote them to EVIDENCE, and `gov research check` must list each as REFERENCE_ONLY with its missing fields.",
        "hidden_oracle_fault_class": "A research record whose measurements do not support its conclusion, cited by a decision — detected only if the oracle scores content, not fields.",
        "chaos_scale_soak": "10k research records with dense influence graphs: `gov research sync` must stay linear and must not lose a backlink.",
        "retrieval_challenge": "A question whose answer is in a concluded research record that is not linked to the asking task: retrieval must surface it as supplementary, never as authority."},
 "J2": {"repo_a_challenge": "An experiment whose declared outputs are under spec/experiments/**, promoted through a gate: the promotion must require an owner-signed answer.",
        "repo_b_challenge": "A brownfield tree with an experiments/ directory already merged into production: adoption must flag it and refuse to treat its output as governed.",
        "hidden_oracle_fault_class": "An experiment concluded from a single run with reproducibility declared rather than judged.",
        "chaos_scale_soak": "Interleaved reproduce calls from several sessions on one experiment: the judged verdict must be a deterministic function of the recorded runs.",
        "retrieval_challenge": "not relevant: experiment standing is read from the record, never retrieved semantically."},
 "K1": {"repo_a_challenge": "A dense requirement/feature/scenario graph: the deterministic traversal must reach every dependent at the stated depth and no further.",
        "repo_b_challenge": "A legacy tree whose links are implicit in prose: the deterministic set is small and the semantic supplement carries the load — the OS must label which is which.",
        "hidden_oracle_fault_class": "A dependency declared only in a path the repository contract does not classify, so it is invisible to traversal.",
        "chaos_scale_soak": "A 50k-artefact graph at R5: traversal must complete inside the Gate U SLO.",
        "retrieval_challenge": "Semantic candidates on an intentionally inadequate profile must not be presented as deterministic impact."},
 "K2": {"repo_a_challenge": "A CIT that invalidates a DONE task, its report, its packet and its checkpoint: every one must be marked and a revalidation task generated.",
        "repo_b_challenge": "A CIT over a legacy tree where the index is stale: execution must refresh it and the verification must not attribute pre-existing damage to the transaction.",
        "hidden_oracle_fault_class": "A transaction that commits the manifest but silently skips one propagation target.",
        "chaos_scale_soak": "Kill the process mid-execute: `gov trust recover-transactions` must leave the tree either fully committed or fully rolled back.",
        "retrieval_challenge": "not relevant: CIT-E's authoritative updates never depend on retrieval."},
 "K3": {"repo_a_challenge": "Each of the eight classes proposed with the declared trigger set to 'editorial': each must be derived, simulated and gated per CHANGE_POLICY.",
        "repo_b_challenge": "A brownfield tree whose repository contract does not yet classify the product directory: the behaviour class must be absent and adoption must say so, rather than silently reporting 'not material'.",
        "hidden_oracle_fault_class": "A security check removed by a rename rather than an edit, so the content heuristic does not see a weakened line.",
        "chaos_scale_soak": "A manifest of 500 operations spanning all eight classes: classification must stay complete and bounded.",
        "retrieval_challenge": "not relevant: materiality is derived from records, paths and content, never from retrieval."},
 "K4": {"repo_a_challenge": "One change proposed at each radius: traversal depth, semantic breadth, test set and approval must differ as the policy states.",
        "repo_b_challenge": "A legacy tree where a single edit reaches three modules: the radius must rise to R3+ from the cross-module threshold, not from the proposer's label.",
        "hidden_oracle_fault_class": "A change whose true blast radius exceeds its computed one because a dependency is undeclared.",
        "chaos_scale_soak": "not relevant: the radius computation is bounded by the traversal it configures.",
        "retrieval_challenge": "Semantic breadth at R4/R5 on a weak profile must not inflate the impact set with noise presented as impact."},
 "L1": {"repo_a_challenge": "Two current decisions on one decision_key: the task must be blocked, the gate raised and the resolution must set one aside.",
        "repo_b_challenge": "A legacy tree with a decision superseded only in prose: precedence must not resolve it, so it must surface as a contradiction.",
        "hidden_oracle_fault_class": "Two decisions that contradict only in prose with no shared key, delivered together as authority.",
        "chaos_scale_soak": "1k decisions with a dense supersession forest: detection must stay bounded and deterministic.",
        "retrieval_challenge": "A contradiction between an authoritative decision and a retrieved supplementary note must never be treated as a contradiction between authorities."},
 "L2": {"repo_a_challenge": "Every gate trigger raised in turn: each package must be complete and substantive with real options and OS-derived next actions.",
        "repo_b_challenge": "A legacy 'approvals' file imported at adoption: it must not become an answered gate.",
        "hidden_oracle_fault_class": "A package whose impact and reversibility statements are plausible but wrong.",
        "chaos_scale_soak": "not relevant: package validation is per-gate.",
        "retrieval_challenge": "not relevant: package content is authored, not retrieved."},
 "L3": {"repo_a_challenge": "The full fabrication battery (flags, environment, role claims, forged records, another gate's signed answer, a widened manifest) against a provisioned machine.",
        "repo_b_challenge": "A cloned repository on the owner's second machine and on a foreign owner's machine: the first honours the answer, the second does not.",
        "hidden_oracle_fault_class": "A gate answered, then re-bound to a different subject by an edit the seal does not cover.",
        "chaos_scale_soak": "Concurrent `gov decide` calls with the same signed answer: replay must be refused after the first.",
        "retrieval_challenge": "not relevant: gate authority never comes from retrieval."},
 "L4": {"repo_a_challenge": "A plan with one gated branch and three independent ones: the three must run to completion while the gate waits.",
        "repo_b_challenge": "A legacy tree where two branches share an undeclared file: the OS treats them as independent — the qualification must measure the resulting conflict.",
        "hidden_oracle_fault_class": "A block whose declared scope is narrower than what it actually refuses.",
        "chaos_scale_soak": "Many concurrent claims under an active block: the refusal set must stay exactly the protected one.",
        "retrieval_challenge": "not relevant: blocking is graph- and policy-driven."},
 "M1": {"repo_a_challenge": "Route every task class and role and assert the tier floor; then attempt to lower each through the overlay.",
        "repo_b_challenge": "A legacy overlay that already lowers a floor: adoption must refuse the weakening and report it.",
        "hidden_oracle_fault_class": "A task routed below its class floor through a path the precedence evaluator does not cover.",
        "chaos_scale_soak": "not relevant: routing is a pure function of policy and the task.",
        "retrieval_challenge": "not relevant."},
 "M2": {"repo_a_challenge": "Tasks declaring each reasoning level: the router must honour the maximum of task, role and radius.",
        "repo_b_challenge": "A legacy task schema without minimum_reasoning: migration must supply the role default rather than 'low'.",
        "hidden_oracle_fault_class": "A run recorded at a lower effort than the task declared, accepted without a flag.",
        "chaos_scale_soak": "not relevant.", "retrieval_challenge": "not relevant."},
 "M3": {"repo_a_challenge": "Map two providers in the overlay and assert the chosen model and that no provider name enters project state.",
        "repo_b_challenge": "A legacy project that hard-codes model names in spec records: adoption must flag them as project state that should live in the overlay.",
        "hidden_oracle_fault_class": "A role whose floor is bypassed because the project declared a same-named role outside the kernel taxonomy.",
        "chaos_scale_soak": "not relevant.", "retrieval_challenge": "not relevant."},
 "M4": {"repo_a_challenge": "Record runs that differ only in reasoning effort and only in reviewer findings, then ask the product to compare them.",
        "repo_b_challenge": "A legacy routing evidence file from an earlier schema: the report must not silently mis-aggregate it.",
        "hidden_oracle_fault_class": "A routing recommendation drawn from a report that merged two materially different populations.",
        "chaos_scale_soak": "100k recorded runs: the report must stay bounded and must not mis-sum.",
        "retrieval_challenge": "not relevant."},
 "N1": {"repo_a_challenge": "A checkpoint taken mid-task: every declared field must be populated from OS state, not from the caller.",
        "repo_b_challenge": "A brownfield tree with prose session summaries: they must not be accepted as checkpoints.",
        "hidden_oracle_fault_class": "A checkpoint that records an index reference taken before the change it claims to capture.",
        "chaos_scale_soak": "A very large working tree: files_changed must stay bounded and must not omit untracked work.",
        "retrieval_challenge": "not relevant: the checkpoint records the index identity, it does not retrieve."},
 "N2": {"repo_a_challenge": "Drive all eight triggers in one session and assert a checkpoint for each.",
        "repo_b_challenge": "An adopted tree with no previous checkpoint: the first boundary must establish the baseline rather than fire spuriously.",
        "hidden_oracle_fault_class": "A trigger that occurs and is then masked by a later checkpoint before any gov command observes it.",
        "chaos_scale_soak": "A session that runs thousands of commands: the watchdog must fire on schedule, not once.",
        "retrieval_challenge": "not relevant."},
 "N3": {"repo_a_challenge": "Change an input a checkpoint recorded and assert STALE, then assert session close and handoff are degraded and say why.",
        "repo_b_challenge": "A tree with no git history: the file counter degrades, so the command counter must carry the watchdog.",
        "hidden_oracle_fault_class": "A checkpoint that stays CURRENT although an input it recorded changed through a path the freshness computation does not cover.",
        "chaos_scale_soak": "Long sessions with no checkpoint: the watchdog must fire from the OS's own counters.",
        "retrieval_challenge": "not relevant."},
 "N4": {"repo_a_challenge": "A subagent returns a schema-valid result and its session ends: a fresh session must reconstruct the work from the record alone.",
        "repo_b_challenge": "A legacy handoff record from an earlier schema: migration must keep the returned result readable.",
        "hidden_oracle_fault_class": "A return whose claims are plausible but false, accepted because the receipt validation was not consulted at close.",
        "chaos_scale_soak": "Concurrent returns on one handoff: exactly one must be recorded as the return.",
        "retrieval_challenge": "not relevant: the return is read by id."},
}

FINDINGS = {
 "K4": ["V1-K4-01"],
 "M1": ["V1-M1-01"],
 "M4": ["V1-M4-01"],
}

if __name__ == "__main__":
    main()
