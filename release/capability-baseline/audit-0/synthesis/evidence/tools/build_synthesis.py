#!/usr/bin/env python3
"""P2-AR-0007: generate the synthesis matrices, the finding dispositions and the blocker-class inventory from
(a) the six family audits of record (read-only) and (b) the synthesis adjudication tables in this file.

Outputs (written into release/capability-baseline/audit-0/synthesis/):
  capability-status-matrix.yaml, suite-to-contract-matrix.yaml, qualification-coverage-matrix.yaml,
  findings.yaml, blocker-classes.yaml
Every adjudication below cites the synthesis evidence that supports it. Run from the worktree root:
  python3 release/capability-baseline/audit-0/synthesis/evidence/tools/build_synthesis.py
"""
import collections
import os
import re
import sys

import yaml

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "..", ".."))
A0 = os.path.join(ROOT, "release/capability-baseline/audit-0")
OUT = os.path.join(A0, "synthesis")
FAM = {"alpha-r": "P2-AR-0013", "beta-r": "P2-AR-0009", "gamma-r": "P2-AR-0010", "delta-r": "P2-AR-0011",
       "epsilon-r": "P2-AR-0008", "zeta-r": "P2-AR-0012"}
RERUN = "evidence/rerun/{fam}.log; evidence/COMPARE-family-outputs.out (re-run in a disposable clone of 11d051e: PASS/FAIL outcomes identical)"

# --------------------------------------------------------------------------------------------- blocker classes
# id: (title, capabilities, mechanism, acs)
BC = collections.OrderedDict([
    ("BC-P2-01", ("Compiled contract views lose owner-source semantics and verification is self-referential",
                  ["all 101 (derived views)", "U", "O5", "V1", "V2", "V3", "V4"],
                  "The compiler reads `## <ID>.` headings only (runtime/src/contracts.rs:73-165): no checklist bullet, none of the Contract v3:53-73 fields, no Gate U (the schema id pattern ^[A-Z]+[0-9]+$ cannot even express it), O5 and V1-V4 compiled ORIGINAL; `gov contract verify` compares the compiled file only with a fresh run of the same lossy compiler and never reads the evidence map or the generated view, so it reports CONTRACT_SOURCE_BOUND over a semantically different contract.",
                  ["AC-13"])),
    ("BC-P2-02", ("Evidence map declares no evidence owner for any capability",
                  ["all 101"],
                  "tests/governance/capability-evidence-map.yaml has 100 rows (U missing), every row evidence_class NOT_YET_MAPPED with automated_checks: []; the suite-to-contract mapping the contract requires does not exist in the product.",
                  ["AC-10"])),
    ("BC-P2-03", ("Green governance evidence currency: key omits relevant input classes and enforcement is path-keyed",
                  ["O4", "U", "B3", "D1", "W6", "all capabilities relying on green evidence"],
                  "verification::inputs_hash (runtime/src/verification/mod.rs:54-72) covers governance/kernel, governance/project, governance/tests, spec/decisions, framework.lock only: requirements/architecture/interfaces, source, index manifest, tool/plugin registry, research/experiment/task/checkpoint/handoff records, adoption evidence, machine trust state and the runtime binary leave a green record current; audit records carry no implementation identity; task-close currency applies only to governance/** and spec/decisions/** paths.",
                  ["AC-10", "AC-3", "AC-5"])),
    ("BC-P2-04", ("Upstream change does not invalidate completed work, its evidence or compiled packets",
                  ["W6", "K2", "O4"],
                  "CIT-E marks only non-DONE tasks retest_required and test/scenario records within the radius depth (cit/mod.rs:922-967); DONE tasks, closing reports, stored context packets and release evidence are never invalidated, no revalidation/rework is generated, task close clears retest without retest evidence (tasks.rs:543-545), and a non-CIT change propagates nothing (an index rebuild then licenses closing on the pre-change packet).",
                  ["AC-8", "AC-3", "AC-16"])),
    ("BC-P2-05", ("Checkpoint and handoff continuity: triggers, staleness and handoff blocking",
                  ["N2", "N3", "W9"],
                  "Half the mandatory checkpoint triggers never fire; nothing marks a checkpoint stale; the watchdog trusts caller-supplied counters; checkpoints record no input ids/versions and can record an index reference taken before the change; handoff/session close are never blocked or degraded for stale or missing required-input state (no session-close operation exists).",
                  ["AC-3", "AC-8", "AC-16"])),
    ("BC-P2-06", ("Health scheduler mechanics absent",
                  ["O5"],
                  "No scheduler: no dependency-aware impacted-check selection, strictly serial execution, no isolation for mutating checks, no per-check cache, no declared hard-block/warning semantics and no health state that blocks work, incomplete result provenance (doctor results unpersisted; audit records lack runtime identity/commit).",
                  ["AC-5"])),
    ("BC-P2-07", ("Health tiers G1-G6 do not perform their duties at their trigger events (incl. Gate-W duties)",
                  ["O5", "W12"],
                  "G1 exists only on the CIT path; G2 task close skips readiness, references, test results, secrets and schema; G3 checks nothing about claims/gates/decision currency; G4 runs only the 3-check CIT verification; G5 update runs a 4-family subset and release build none; G6 does not exist; W12's G0-G5 Gate-W duties are absent or fragmentary.",
                  ["AC-5", "AC-8", "AC-16"])),
    ("BC-P2-08", ("Acting-role resolution and G0 guard coverage on privileged/mutating paths",
                  ["E1", "O5", "A5", "S3", "S4", "T1"],
                  "init and every adopt/migrate stage evaluate authority against GOV_ROLE or the default 'orchestrator', ignoring --role (cli/src/main.rs:782-813; init.rs:228,257; adopt.rs:592ff); an invocation declaring no role acts as L4 orchestrator; task replan and memory heldout-starter --force carry no authority class; 15 mutating commands change governed state under FREEZE_WRITES (gate present has no guard_write; adopt baseline has neither guard nor authority check).",
                  ["AC-3", "AC-5"])),
    ("BC-P2-09", ("OS-written (T2) records honoured without binding to an OS operation; lower-role writes exempt at task close",
                  ["E1", "L3", "F4", "I2"],
                  "Gate/decision/CIT records under spec/decisions/ and the plugin registry under governance/generated/ are plain repository files the product trusts as OS-written; task close excludes OS_MANAGED_PREFIXES from observed mutations (tasks.rs:201-218, 308-316); a worker-forged gate answer + human_approved decision approves and commits a CIT, a forged registry entry runs an unapproved elevated plugin; suite and doctor are silent.",
                  ["AC-3", "AC-4", "AC-16"])),
    ("BC-P2-10", ("Human approval and presentation derived from caller-declared metadata",
                  ["L3", "E1", "Q1"],
                  "gates::answer records answered_by_kind human whenever --by is not a kernel agent id and the declared role is L3+; `gov decide` defaults --by to 'human' and the role to orchestrator, so the default invocation, --role human and GOV_ROLE=human all record human approval; presentation is recorded whenever any L1+ caller renders the package to its own stdout; upstream export 'human approval' is any --approved-by string.",
                  ["AC-3", "AC-16"])),
    ("BC-P2-11", ("Gate approval not bound to the subject and content it authorises",
                  ["L3", "F4"],
                  "A CIT approval survives manifest edits and re-simulation to a larger radius, and an answered gate can be re-bound to another CIT by editing its cit field; plugin registration accepts any presented, answered-A gate on any subject (governance.rs:290-318, 493-513; no GATE_MISMATCH equivalent).",
                  ["AC-3", "AC-4"])),
    ("BC-P2-12", ("Task-blocking gate semantics", ["L3"],
                  "gates::answer moves every WAITING_HUMAN task to READY whatever the option; the DAG blocks only on PENDING/PRESENTED gates, so declined, revoked, withdrawn or missing gates leave work runnable and an IN_PROGRESS task closes while its gate is pending.",
                  ["AC-3"])),
    ("BC-P2-13", ("Material changes escape change control (materiality self-declared, in-task edits bypass CIT)",
                  ["K3", "G1"],
                  "Auto-simulation and human gating key on the proposer's trigger label (a material change labelled 'editorial' auto-approves at R0) and on the CIT path only; material spec/interface/security/governance edits made inside ordinary tasks close with no impact simulation or gate.",
                  ["AC-3"])),
    ("BC-P2-14", ("Task-contract fields and path scope not enforced", ["I2", "J2"],
                  "blocks, required_data, required_tools and production_merge_allowed have no enforcing consumer; any path once touched by any committed CIT is permanently in scope for every later task (tasks.rs:327-337).",
                  ["AC-3"])),
    ("BC-P2-15", ("Claim atomicity and claim scope", ["E4"],
                  "ClaimsStore::claim is check-then-insert without a transaction (memory/claims.rs:56-72): concurrent claims all succeed; claims record no worktree identity and parallel claims ignore mutation-scope overlap.",
                  ["AC-3"])),
    ("BC-P2-16", ("Runnable / claimable / READY state not derived from the DAG", ["E4", "H3", "I4", "W3"],
                  "task claim checks only the stored task_status, which callers can set READY; dependency-, readiness- and input-blocked tasks are claimed and closed; a task whose status is BLOCKED is in the runnable set and offered by `gov continue`; absent mandatory inputs never block READY.",
                  ["AC-3", "AC-8"])),
    ("BC-P2-17", ("Mandatory task-input manifest semantics", ["W2", "W3"],
                  "No required/optional distinction; authority class dropped on entry to the authority block; no consumption rules in output schemas; superseded/historical inputs satisfy current work silently; the manifest cannot declare required state, version/hash constraints, reasons or supplementary context.",
                  ["AC-8", "AC-3"])),
    ("BC-P2-18", ("Contradiction detection and resolution", ["L1", "W3"],
                  "Contradictions deterministic precedence cannot resolve (two ACTIVE contradictory decisions; conflicting mandatory inputs) are delivered together as authority with no gate or block; agent resolution fails open on unassessed reversibility and is judged on the gate creator's own declared values.",
                  ["AC-3"])),
    ("BC-P2-19", ("Context-packet delivery, provenance and outage behaviour", ["W4", "W10", "C9"],
                  "The deterministic block carries a field whitelist (no normative statements/bodies/versions, hash insensitive to them); datasets, derived_from experiments/research and task-level interfaces reach the worker only via retrieval or not at all; missing inputs vanish silently; any retrieval/index error aborts the whole compile (context/mod.rs:190-209), withholding the deterministic inputs (W10 hard invariant).",
                  ["AC-8", "AC-3"])),
    ("BC-P2-20", ("Consumption receipt and implementation traceability", ["W5", "W8", "N4", "E3"],
                  "Task close records no consumed inputs, implemented requirements or applied decisions and accepts fabricated trace; lineage stops before code/tests/evidence/release; the worker-return schema and the task-close report schema collide on `status`, so a schema-valid worker return cannot be the close receipt.",
                  ["AC-8", "AC-3"])),
    ("BC-P2-21", ("Artefact identity and relation-edge semantics", ["W1", "W2", "S4"],
                  "Migration plans and audit findings lack stable identity (positional GF-/ART- ids that change on re-run, re-plan overwrites); authored records carry no provenance; consumers/producers/report.task produce inverted edges and required_data/influences none, so impact never reaches declared consumers.",
                  ["AC-8", "AC-3"])),
    ("BC-P2-22", ("Orphan / unexplained output detection", ["W7"],
                  "No product surface names an unconsumed output, a requirement without implementation/test path, unconsumed research, an unjustified test or code; only dangling edges and an anonymous orphan count; no remediation.",
                  ["AC-8", "AC-3"])),
    ("BC-P2-23", ("Artifact-flow quantitative health absent", ["W11"], "None of the nine W11 metrics is computed or reported.", ["AC-2"])),
    ("BC-P2-24", ("Governed work not generated from events", ["I3", "O5"],
                  "Only readiness gaps generate tasks; failed tests, audit/security findings, research discoveries, human decisions, lessons, capability gaps, retrieval failures, performance regressions and health failures generate none; CIT effects only flag existing tasks.",
                  ["AC-3", "AC-5"])),
    ("BC-P2-25", ("Index content coverage and chunk granularity", ["C3", "C4", "C7", "D3"],
                  "List-valued and nested record fields (acceptance criteria, scenario steps, decision options, worker-return discoveries) are never chunked; code outside recognised units after the 15-line head is in no chunk; methods are not chunk units so symbol lookups return the file header.",
                  ["AC-3", "AC-7"])),
    ("BC-P2-26", ("Retrieval pipeline ordering, routing and de-duplication", ["C3", "C4", "C9", "D2"],
                  "Authority/namespace filters run after candidate truncation and after a reranker plugin receives the text; bare filenames route to the symbol route only; graph answers are buried by equal-weight fusion; duplicate suppression is a per-artefact cap only.",
                  ["AC-3"])),
    ("BC-P2-27", ("Code-structural extraction", ["C5"],
                  "No route registrations, DB models or inheritance/implementation relations; AST-equivalent fidelity only for Python; TESTS edges only when an import resolves.",
                  ["AC-3"])),
    ("BC-P2-28", ("Graph integrity detection", ["C2"], "Orphans only counted; edges to superseded targets and reversed/ill-typed relationships not detected.", ["AC-3"])),
    ("BC-P2-29", ("Incremental index invalidation", ["D1", "R3", "K2"],
                  "Incremental builds leave stale edges owned by unchanged files; a path-map reclassification never reaches unchanged files while freshness reports fresh; CIT-E refreshes and verifies with the pre-mutation cached policy/path map.",
                  ["AC-3", "AC-16"])),
    ("BC-P2-30", ("Retrieval-profile component identity and change governance", ["D4", "D5", "D1"],
                  "The embedding runtime/model artefact is neither identified nor bound; pinned revisions are strings not bound to what executes; profile changes are not bound to benchmark evidence, post-reindex regression or the radius gate, and direct pin edits pass unflagged.",
                  ["AC-7", "AC-3"])),
    ("BC-P2-31", ("Non-rebuildable authoritative state stored in, or classified as, derived/generated state", ["B1", "B3", "D6"],
                  "claims.db (C1 'claims' current truth) and control.json (emergency control) live in .governance-runtime/**, which the product's REPOSITORY_CONTRACT classifies `derived` and its docs call 'derived and rebuildable'; the OS plugin registry (D-0007 T2) lives under governance/generated/** (`generated`); deleting what the product declares derived loses the claim and lifts FREEZE_WRITES.",
                  ["AC-3"])),
    ("BC-P2-32", ("Failure memory not durable", ["C8"], "Ad-hoc retrieval misses and tool failures leave no durable, structured, rebuild-surviving record.", ["AC-3"])),
    ("BC-P2-33", ("Legacy identification, extraction and retirement", ["R1", "R2", "S4"],
                  "Extraction is cue-word gated (skills, research, evidence, cue-less facts lost); no dependency proof before retirement and A6 rewrites live code to read archived legacy rules; the planner and the test scaffold disagree on a secret-bearing legacy store and adoption stalls; on a re-run the OS's own generated IDE adapter is classified legacy provider rules and archived.",
                  ["AC-3"])),
    ("BC-P2-34", ("Independence of test, review and verification authorship is self-attested", ["O3", "T1", "T2", "T3", "S4", "E1", "H4"],
                  "Independence is a self-declared boolean or a caller-chosen session-string inequality; task designated roles are not enforced; adoption verdicts bind no digest of the reviewed plan/map/tests (executor changed both after approval and A6/A7 accepted); A10 evaluates the builder's own held-out set; test-data authorship unrecorded.",
                  ["AC-3"])),
    ("BC-P2-35", ("Post-install kernel integrity anchored only in repository-controlled records", ["A2"],
                  "kernel_trust decides 'intact' from the payload, KERNEL_MANIFEST.json and framework.lock, all writable in the project; a mutually consistent rewrite passes kernel verify, guards, doctor and audit; the machine's protected installed record is never consulted after install.",
                  ["AC-4", "AC-3", "AC-16"])),
    ("BC-P2-36", ("Unauthenticated installation presented as current/verified (default posture)", ["A2", "S3", "S5"],
                  "On the default unprovisioned machine every ingress admits kernel material with authenticity UNKNOWN; the CLI envelope says presented_as CURRENT, gov status reports verified_release/verified_payload_hash, doctor and audit report HEALTHY with no authenticity/posture check.",
                  ["AC-4", "AC-3", "AC-16"])),
    ("BC-P2-37", ("Trust decisions and identity records taken from unauthenticated release fields", ["A2", "A3", "S2", "S5", "S6"],
                  "update gating reads certification.status from the unsigned manifest.json (an edit to CERTIFIED removes the Human Decision Gate); any role can mint a CERTIFIED release; framework.lock records release_commit/source from unverified inputs, records no authenticity basis, and varies with XDG_CACHE_HOME.",
                  ["AC-4", "AC-3"])),
    ("BC-P2-38", ("Provisioned-machine rollback/reinstall", ["S5", "A2"],
                  "On a provisioned machine `gov update --rollback` cannot authenticate the previous release (the protected record vouches only for the current one); a refused reinstall commits the new payload before refusing (KERNEL_MISMATCH), leaving a mixed installation.",
                  ["AC-3"])),
    ("BC-P2-39", ("Plugin elevation decided by descriptor self-declaration", ["F4"],
                  "authorize/register derive whether a gate is needed from the descriptor's own required_permission_classes/permissions; plugins are unsandboxed, so an under-declaring hand-declared plugin performs undeclared effects with no gate.",
                  ["AC-4"])),
    ("BC-P2-40", ("Plugin implementation bytes not bound", ["F4"],
                  "The implementation pin covers only command arguments that resolve to local files (capabilities/governance.rs:79-122): interpreter/module-form commands (`python3 -m <module>`, the form the shipped templates use) have implementation_sha256 null even when REGISTERED and gate-approved, so post-approval code swaps run undetected; unregistered plugins are bound only by resettable machine-local TOFU.",
                  ["AC-4", "AC-3"])),
    ("BC-P2-41", ("Tool acquisition: review evidence and approval not bound to the tool installation", ["F3", "F4"],
                  "A tool's security review is satisfied by naming any existing record; an install gate answered A is never consumed (a new gate is raised every time), so approved installation is a dead end.",
                  ["AC-4", "AC-3"])),
    ("BC-P2-42", ("Skill regression never executed", ["F1", "O2"],
                  "skills::validate_all and the skill_regression family check schema and non-empty validation_scenarios only; no scenario is executed and project skill versions are not bound to content, so a green skill_regression result asserts a property never tested.",
                  ["AC-3"])),
    ("BC-P2-43", ("Product-test results not governed", ["O1", "U"],
                  "`gov verify product` runs one family-blind command and exits 0 on failure; a failing suite leaves doctor/audit HEALTHY; task close accepts a self-attested tests.status passed.",
                  ["AC-3"])),
    ("BC-P2-44", ("Health SLO thresholds and the HEALTHY conjunction", ["U"],
                  "9 of 15 SLOs have no effective threshold or are absent; neither doctor nor audit implements 'HEALTHY only when' (HEALTHY with failing retrieval regression, DAG cycle, legacy provider rules, unresolved critical findings, empty readiness).",
                  ["AC-3", "AC-16"])),
    ("BC-P2-45", ("Project overlay files bypass POLICY_PRECEDENCE", ["A1", "M1", "M2", "M3", "H3"],
                  "MODEL_ROUTING_OVERRIDES lowers kernel tier floors and reasoning minimums verbatim (routing.rs tier_for_class) although POLICY_PRECEDENCE marks them floors; PROJECT_POLICY.readiness.enforce_pre_implementation_cells is read directly by dag.rs and switches off readiness gating; neither is refused or reported.",
                  ["AC-3"])),
    ("BC-P2-46", ("Scenario -> data -> test-data lineage and provenance", ["H4"],
                  "scenario.data_requirements and test-obligation.data_provenance are not relation fields, success/failure criteria are not required, and data provenance is optional and never read.",
                  ["AC-3"])),
    ("BC-P2-47", ("Research output completeness", ["J1"], "Only the benchmark producer records the J1 fields; any other research record with only a question is governed evidence; influences never recorded.", ["AC-3"])),
    ("BC-P2-48", ("Experiment lifecycle absent", ["J2"], "No experiment command, lifecycle state or required fields (hypothesis, method/data, reproducibility, results, interpretation, decision influence).", ["AC-2"])),
    ("BC-P2-49", ("Human Decision Gate package not enforced", ["L2"],
                  "Package fields default to 'not assessed', options may be empty, answers outside the offered options are recorded, system-raised gates carry placeholder next actions.",
                  ["AC-3"])),
    ("BC-P2-50", ("Upstream export gate fails open on content", ["Q4"],
                  "Reproducer controls are path/filename based and trust a self-declared synthetic flag: verbatim project source and dumped vector rows leave as 'synthetic' fixtures.",
                  ["AC-3"])),
    ("BC-P2-51", ("Qualification Oracle format absent", ["V1", "V2", "V3", "V4"],
                  "No machine-checkable definition of the fault manifest, hidden path-map oracle, hidden memory oracle or quantitative scoring exists; a fault-manifest record lacking every V1 field is accepted.",
                  ["AC-2", "AC-6", "AC-10"])),
    ("BC-P2-52", ("Path map does not represent documentation citations", ["B2"],
                  "Code imports and consumers are catalogued, markdown/document links are not (references: [] on both ends), so the path map cannot answer Repo B's 'hidden cross-references' or V2 'expected references/consumers'.",
                  ["AC-3"])),
])

# ------------------------------------------------------------------------------------------ dispositions of family findings
# id: (disposition, final_blocking, [classes], note)
C, R_, X_ = "CONFIRMED", "CORRECTED", "REFUTED"
D = {
    # ---------------- alpha-r
    "A0-A2-01": (R_, True, ["BC-P2-35"], "Reproduced (A2-03 re-run identical) and extended by AC16-X3 [X3c]/[X3d]: after an authentic install on a provisioned machine the consistent rewrite passes `kernel verify` (trust.verified true). Refinement: the demonstrated consequence is not secret exposure (a path-classified .env stays excluded by a second layer, X3c) but authority-floor rewriting: with AUTHORITY_POLICY answer_gate L3->L1 rewritten consistently, an L1 backend-engineer records a human answer (by_kind human) that the untampered control refuses (X3d). owner_decision_required CORRECTED to false: Contract v3:146 (owner source) requires detection, D-0007 rule 1 already provides for 'T1 cannot be authenticated', ARCH-0003 §7 names this machine's protected installed record as the authority for an installed copy, and ARCH-0003 §8 requires additional machines to verify their pinned release before privileged work; strengthening detection amends no D-0007 text. The unprovisioned-machine sub-case is part of OD-P2-02."),
    "A0-A2-02": (R_, True, ["BC-P2-36"], "Reproduced (A2-01 re-run identical; AC16-X3 [X3a]: tampered release admitted UNKNOWN/UNPROVISIONED, presented_as CURRENT, doctor HEALTHY, audit HEALTHY). Split: the non-masquerade/visibility requirement is determined by Contract v3:150 and OWNER-DIRECTIVE-0004 and is blocking now (BC-P2-36); whether external-source ingress must be refused on an unprovisioned machine is a genuine owner choice (OD-P2-02)."),
    "A0-A2-03": (C, True, ["BC-P2-37"], "Reproduced (A2-04, S6 re-runs identical)."),
    "A0-A2-04": (C, True, ["BC-P2-37"], "Reproduced (A2-04 [L2] re-run identical)."),
    "A0-T2-01": (C, True, ["BC-P2-34"], "Reproduced (S4-T2-B2-negative, T1-roles, S4-adopt-end-to-end re-runs identical)."),
    "A0-A1-02": (C, True, ["BC-P2-01", "BC-P2-02"], "Reproduced and generalised to all 101 capabilities by synthesis evidence AC01-09-13-14 (0 of 344 substantive bullets in the compiled form; U absent from all three derived views; 101/101 capabilities with zero evidence owners)."),
    "A0-B3-01": (C, True, ["BC-P2-03"], "Reproduced (FRESH-invalidation re-run identical) and by AC16-X1 [X1-O4-green-stale-after-direct-spec-change FAIL]."),
    "A0-A1-01": (C, False, [], "Reproduced. Non-blocking accepted: A1's qualification challenge (line 140) exercises precedence, not the constitution display of a tampered kernel; enforcement uses the embedded baseline when kernel trust fails."),
    "A0-A4-01": (C, False, [], "Reproduced. Non-blocking accepted: no Contract v3 challenge line or V1-V4 element targets budgets."),
    "A0-A5-01": (R_, True, ["BC-P2-08"], "Reproduced (A5 re-run identical; epsilon O5-G0 matrix). Blocking status CORRECTED: this is the same mechanism as blocking A0-O5-05 (G0 guard coverage: mutating commands not passing guard_write under FREEZE_WRITES), which AC-5 requires; one mechanism cannot be both blocking and non-blocking."),
    "A0-A5-02": (C, False, [], "Reproduced. Non-blocking accepted (no challenge or oracle element; CANCEL_AGENTS pauses)."),
    "A0-A5-03": (C, False, [], "Reproduced. Non-blocking accepted."),
    "A0-B2-01": (C, False, [], "Reproduced. Non-blocking accepted: SPLIT/MERGE can be recorded in the path map and are routed explicitly to a governed CIT, which carries verification and rollback."),
    "A0-B2-02": (R_, True, ["BC-P2-52"], "Reproduced. Blocking status CORRECTED (AC-3): the Repo B challenge (Contract v3:197 'hidden cross-references') and the V2 oracle element 'expected references/consumers' (Contract v3:1035) score exactly this; under the synthesis AC-3 criterion (a gap on a path a named challenge or oracle element exercises predetermines that element's outcome) B2 is COULD_UNDERMINE."),
    "A0-S2-01": (C, False, [], "Reproduced. Non-blocking accepted (qualification pins by product digest)."),
    "A0-S3-01": (C, False, [], "Reproduced. Non-blocking accepted: certification is R2 and qualification runs on an uncertified candidate by design; authenticity presentation is carried by BC-P2-36."),
    "A0-S4-01": (C, False, [], "Reproduced. Non-blocking accepted (batch snapshots and rollback exist; interrupted-work handling is advisory)."),
    "A0-S4-02": (R_, True, ["BC-P2-33"], "Reproduced (S4-adopt-raw-sql-chat-store re-run identical). Blocking status CORRECTED (AC-3): a Repo B carrying a secret-bearing legacy chat store (Contract v3:197 challenge; the brownfield fixture as shipped) stalls adoption at A6 with no product resolution, so the Repo B scenario cannot complete."),
    "A0-S4-03": (R_, True, ["BC-P2-08"], "Reproduced; same defect as gamma-r A0-E1-01 (blocking HIGH) and epsilon-r A0-O5-05; blocking status CORRECTED for consistency. AC16-X2 [X2-E1-init-honours-declared-role FAIL]."),
    "A0-S5-01": (C, False, [], "Reproduced. Non-blocking accepted (ledger provenance defect on a refused update; no qualification element)."),
    "A0-S5-02": (R_, True, ["BC-P2-38"], "Reproduced (A2-05, A2-08 re-runs identical). Blocking status CORRECTED (AC-3): S5:944 'rollback' fails on the supported (provisioned) posture, OWNER-DIRECTIVE-0004 requires the architecture to cover rollback, and ARCH-0003 §7 derives an installed recovery path's authenticity from the machine's protected record of what it previously verified; an update scenario with rollback on a provisioned machine fails for a known reason."),
    "A0-A2-05": (C, False, [], "Reproduced. Hygiene (INFO); non-blocking accepted."),
    "A0-A3-01": (C, False, [], "Reproduced. INFO/verifier-hardening; non-blocking accepted."),
    "A0-A3-02": (C, False, [], "Reproduced. INFO; related to BC-P2-45 (overlay widening) but no execution effect was observed; non-blocking accepted."),
    "A0-B1-01": (C, False, [], "Reproduced. INFO; non-blocking accepted."),
    # ---------------- beta-r
    "A0-C1-01": (C, True, ["BC-P2-01", "BC-P2-02"], "Reproduced (DERIVED-views re-run identical; synthesis AC01-09-13-14)."),
    "A0-C2-01": (C, True, ["BC-P2-28"], "Reproduced (C2 re-run identical)."),
    "A0-C3-01": (C, True, ["BC-P2-26"], "Reproduced (C3 re-run: 14/14 markers identical)."),
    "A0-C3-02": (C, True, ["BC-P2-25"], "Reproduced (C3/C4/C7 re-runs identical); also covers delta-r's C7/D2 lead (nested worker return not indexed, N3-N4-W9 OBSERVE N4.b1.6 re-run identical)."),
    "A0-C4-01": (C, True, ["BC-P2-25"], "Reproduced."),
    "A0-C4-02": (C, False, [], "Reproduced. Non-blocking accepted (recall for existing codes preserved)."),
    "A0-C5-01": (C, True, ["BC-P2-27"], "Reproduced."),
    "A0-C5-02": (C, True, ["BC-P2-27"], "Reproduced."),
    "A0-C6-01": (C, False, [], "Reproduced. INFO recommendation."),
    "A0-C8-01": (C, True, ["BC-P2-32"], "Reproduced."),
    "A0-C9-01": (C, True, ["BC-P2-26"], "Reproduced. Additional instance in the CIT-P candidate list (AC16-X1 [X1-C9-cit-p-candidates-deduplicated]: RPT-0001 twice), consistent with the documented per-artefact cap; delta-r's C9 lead is covered by this finding."),
    "A0-C9-02": (C, False, [], "Reproduced. INFO."),
    "A0-C10-01": (C, False, [], "Reproduced. Non-blocking accepted (no challenge or oracle element)."),
    "A0-D1-01": (C, True, ["BC-P2-29"], "Reproduced."),
    "A0-D1-02": (C, True, ["BC-P2-29"], "Reproduced."),
    "A0-D1-03": (C, True, ["BC-P2-29"], "Reproduced (X-K2-D1-W6 re-run identical)."),
    "A0-D1-04": (C, True, ["BC-P2-03"], "Reproduced."),
    "A0-D2-01": (C, False, [], "Reproduced. Non-blocking accepted (record still returned at rank 2)."),
    "A0-D2-02": (C, True, ["BC-P2-26"], "Reproduced."),
    "A0-D2-03": (C, True, ["BC-P2-26"], "Reproduced."),
    "A0-D3-01": (C, True, ["BC-P2-25"], "Reproduced."),
    "A0-D4-01": (C, True, ["BC-P2-30"], "Reproduced (D4 re-run identical)."),
    "A0-D5-01": (C, True, ["BC-P2-30"], "Reproduced; its `python3 -m` observation is extended to registered, gate-approved elevated plugins by synthesis finding S0-F4-01 (BC-P2-40)."),
    "A0-D5-02": (C, True, ["BC-P2-30"], "Reproduced."),
    "A0-D6-01": (C, True, ["BC-P2-31"], "Reproduced (D6 re-run identical); root cause generalised by S0-B1B3-01 (the product classifies the location derived)."),
    "A0-D6-02": (C, False, [], "Reproduced. Non-blocking accepted (tampered plugin still fails closed via the descriptor pin); location defect recorded in BC-P2-31's statement for context."),
    "A0-R1-01": (C, True, ["BC-P2-33"], "Reproduced."),
    "A0-R1-02": (C, True, ["BC-P2-33"], "Reproduced."),
    "A0-R2-01": (C, False, [], "Reproduced. Non-blocking accepted (index refresh and regression do follow at A9/A10)."),
    "A0-R3-01": (C, False, [], "Reproduced. Non-blocking accepted."),
    # ---------------- gamma-r
    "A0-E1-01": (C, True, ["BC-P2-08"], "Reproduced (E1 re-run identical; AC16-X2 [X2-E1-init-honours-declared-role FAIL])."),
    "A0-E1-02": (C, True, ["BC-P2-09"], "Reproduced and carried end-to-end across E4/G2/L3/K2/U by AC16-X2 (forged answer invisible at close, approves, commits, audit HEALTHY)."),
    "A0-E1-03": (C, True, ["BC-P2-08"], "Reproduced."),
    "A0-E1-04": (R_, True, ["BC-P2-10"], "Reproduced (AC16-X2 [X2-L3-fabrication-role-human], [X2-L3-fabrication-env-GOV_ROLE]). CORRECTED: the human-approval part is not an owner decision - Contract v3:679 and :365, D-0007 rule 2 ('human_approved' is a T1/T2 fact; a T5 field carrying it is a request), ARCH-0003 §8 and OWNER-DIRECTIVE-0004 ('caller fields ... and models cannot manufacture trust or Human Gate approval') determine it; it is blocking (BC-P2-10). The residual question - whether the OS itself must authenticate which agent holds an L0-L4 role (D-0007 consequence 5 vs Contract v3 E1:365 / framework §23) - is genuinely open and is OD-P2-01 (non-blocking until decided)."),
    "A0-E1-05": (C, True, ["BC-P2-34"], "Reproduced."),
    "A0-E1-06": (R_, True, ["BC-P2-01", "BC-P2-02"], "Reproduced. Blocking status CORRECTED: gamma-r left AC-13 weighing to synthesis; AC-13 fails (headings-only compiled form is a semantic difference, Contract v3:47) and AC-10 fails (zero evidence owners)."),
    "A0-E2-01": (C, False, [], "Reproduced. Non-blocking accepted."),
    "A0-E3-01": (C, False, [], "Reproduced; also confirms delta-r's E3/E1 lead (AC16-X2 [X2-E3-return-bound-to-recipient FAIL]). Non-blocking accepted (a deliberate wrong-role or second return is required; faults are injected into repository state)."),
    "A0-E4-01": (C, True, ["BC-P2-15"], "Reproduced (E4 re-run: 3/3 sessions granted in every trial)."),
    "A0-E4-02": (C, True, ["BC-P2-16"], "Reproduced."),
    "A0-E4-03": (C, True, ["BC-P2-15"], "Reproduced."),
    "A0-E4-04": (C, False, [], "Reproduced. Non-blocking accepted (parallel_runnable + task claim reach independent work)."),
    "A0-F1-01": (R_, True, ["BC-P2-42"], "Reproduced. Blocking status CORRECTED for consistency with epsilon-r A0-O2-01 (same mechanism, rated blocking): a skill_regression family that reports green without executing any scenario is untrustworthy G5 evidence."),
    "A0-F1-02": (C, False, [], "Reproduced. Non-blocking accepted."),
    "A0-F1-03": (C, False, [], "Reproduced. Non-blocking accepted; its upstream human-approval note is carried by A0-Q1-02 (BC-P2-10)."),
    "A0-F2-01": (C, False, [], "Reproduced. Non-blocking accepted."),
    "A0-F2-02": (C, False, [], "Reproduced. Non-blocking accepted (execution refuses the unregistered plugin)."),
    "A0-F3-01": (C, True, ["BC-P2-41"], "Reproduced."),
    "A0-F3-02": (C, False, [], "Reproduced. Non-blocking accepted."),
    "A0-F4-01": (C, True, ["BC-P2-11"], "Reproduced."),
    "A0-F4-02": (C, True, ["BC-P2-09"], "Reproduced."),
    "A0-F4-03": (R_, True, ["BC-P2-39"], "Reproduced. owner_decision_required CORRECTED to false: Contract v3 F4:426 and :430 (owner source, precedence row 2) and ARCH-0003 §9 (owner-adopted: 'Descriptors cannot self-authorise') determine the requirement; D-0005 consequence 3 (agent-approved, 'product owner may supersede', precedence row 4) is subordinate and remains satisfiable (hand-declared descriptors may keep working for effects that are enforced or non-elevated). The choice among conforming designs is an implementation choice; only a design that adds a new external dependency class would need owner adoption."),
    "A0-F4-04": (R_, True, ["BC-P2-40"], "Reproduced. Blocking status CORRECTED: gamma-r recorded it non-blocking because 'only registered plugins may hold declared elevated permissions', but LEAD-X4 shows a REGISTERED, gate-approved, network-elevated plugin in module form has implementation_sha256 null and runs swapped code undetected (synthesis finding S0-F4-01), so the unpinned-implementation mechanism reaches elevated plugins (AC-4)."),
    "A0-F4-05": (C, True, ["BC-P2-41"], "Reproduced."),
    "A0-F5-01": (C, False, [], "Reproduced. Non-blocking accepted."),
    "A0-G1-01": (C, False, [], "Reproduced. Non-blocking accepted (qualification drives governed operations directly)."),
    "A0-G1-02": (C, True, ["BC-P2-13"], "Reproduced."),
    "A0-H3-01": (R_, True, ["BC-P2-45"], "Reproduced. Blocking status CORRECTED: an overlay switching off a kernel readiness rule outside POLICY_PRECEDENCE is 'attempted authority weakening' via project policy, which the A1 qualification challenge (Contract v3:140) injects; same mechanism as blocking A0-M1-02."),
    "A0-H4-01": (C, True, ["BC-P2-46"], "Reproduced."),
    "A0-H4-02": (C, True, ["BC-P2-34"], "Reproduced."),
    "A0-H4-03": (C, True, ["BC-P2-46"], "Reproduced."),
    "A0-I2-01": (C, True, ["BC-P2-14"], "Reproduced."),
    "A0-I2-02": (C, True, ["BC-P2-14"], "Reproduced."),
    "A0-I2-03": (C, False, [], "Reproduced. Non-blocking accepted (same porcelain-parse defect as zeta-r A0-W5-03)."),
    "A0-I3-01": (C, True, ["BC-P2-24"], "Reproduced."),
    "A0-I4-01": (C, False, [], "Reproduced. Non-blocking accepted; I4's status is changed for another reason (S0-I4-01)."),
    # ---------------- delta-r
    "A0-J1-01": (C, True, ["BC-P2-47"], "Reproduced."),
    "A0-J1-02": (C, True, ["BC-P2-01", "BC-P2-02"], "Reproduced."),
    "A0-J1-03": (C, True, ["BC-P2-03"], "Reproduced."),
    "A0-J2-01": (C, True, ["BC-P2-48"], "Reproduced. Its production-merge part is the same mechanism as A0-I2-01 and is repaired under BC-P2-14; the capability-absent part is BC-P2-48."),
    "A0-K2-01": (C, True, ["BC-P2-04"], "Reproduced and carried across K2/D1/W6/O4 by AC16-X1 (DONE task, its report and the stored packet untouched; no rework)."),
    "A0-K2-02": (C, False, [], "Reproduced. Non-blocking accepted."),
    "A0-K2-03": (C, False, [], "Reproduced. Non-blocking accepted (fails closed)."),
    "A0-K3-01": (C, True, ["BC-P2-13"], "Reproduced."),
    "A0-K4-01": (C, False, [], "Reproduced. Non-blocking accepted."),
    "A0-L1-01": (C, True, ["BC-P2-18"], "Reproduced."),
    "A0-L1-02": (C, False, [], "Reproduced. Non-blocking accepted."),
    "A0-L1-03": (C, True, ["BC-P2-18"], "Reproduced."),
    "A0-L2-01": (C, True, ["BC-P2-49"], "Reproduced."),
    "A0-L3-01": (R_, True, ["BC-P2-10"], "Reproduced (AC16-X2 [X2-L3-fabrication-default|role-human|env-GOV_ROLE] all FAIL: by_kind human). owner_decision_required CORRECTED to false: the requirement is determined (Contract v3:679; D-0007 rule 2; ARCH-0003 §8; OWNER-DIRECTIVE-0004 'caller fields, plugins and models cannot manufacture ... Human Gate approval'), and the class of acceptable authority is already defined by OWNER-DECISION-0006 requirement 2 (owner-controlled local/out-of-band mechanism not manufacturable by repository content, environment, caller fields, plugins or model output) and implemented for break-glass as an owner-signed token verified against a role delegated by the administrator-provisioned root. Choosing the concrete mechanism is an implementation matter, as ARCH-0003 §7.1 treats the break-glass mechanism."),
    "A0-L3-02": (C, True, ["BC-P2-09"], "Reproduced (AC16-X2)."),
    "A0-L3-03": (C, True, ["BC-P2-11"], "Reproduced."),
    "A0-L3-04": (C, True, ["BC-P2-12"], "Reproduced."),
    "A0-L3-05": (R_, True, ["BC-P2-10"], "Reproduced. owner_decision_required CORRECTED to false for the same reason as A0-L3-01; presentation evidence travels over the same determined channel."),
    "A0-M1-01": (C, False, [], "Reproduced. Non-blocking accepted (cost/efficiency only)."),
    "A0-M1-02": (C, True, ["BC-P2-45"], "Reproduced; also falsifies A1:134-135 (synthesis correction of A1)."),
    "A0-M2-01": (C, False, [], "Reproduced. Non-blocking accepted."),
    "A0-M4-01": (C, False, [], "Reproduced. Non-blocking accepted."),
    "A0-M4-02": (C, False, [], "Reproduced. Non-blocking accepted."),
    "A0-N1-01": (C, False, [], "Reproduced. Non-blocking accepted."),
    "A0-N2-01": (C, True, ["BC-P2-05"], "Reproduced."),
    "A0-N3-01": (C, True, ["BC-P2-05"], "Reproduced and by AC16-X1 [X1-NxW9-checkpoint-stale-marked FAIL, X1-NxW9-handoff-blocked-or-degraded FAIL]."),
    # ---------------- epsilon-r
    "A0-O1-01": (C, True, ["BC-P2-43"], "Reproduced (O1 re-run byte-identical)."),
    "A0-O1-02": (C, False, [], "Reproduced. Non-blocking accepted (verifier hardening)."),
    "A0-O1-03": (C, True, ["BC-P2-01", "BC-P2-02"], "Reproduced."),
    "A0-O2-01": (C, True, ["BC-P2-42"], "Reproduced."),
    "A0-O2-02": (C, False, [], "Reproduced. Non-blocking accepted."),
    "A0-O2-03": (C, False, [], "Reproduced. INFO."),
    "A0-O3-01": (C, True, ["BC-P2-34"], "Reproduced. Its AC-12 tag is not adopted: AC-12 concerns the evidence this gate relies on (fresh, independent - it is); the product-side independence defect blocks through AC-3."),
    "A0-O4-01": (C, True, ["BC-P2-03"], "Reproduced (O4 re-run byte-identical). AC-12 tag not adopted (see A0-O3-01); blocks AC-10/AC-3/AC-5/AC-16."),
    "A0-O4-02": (C, True, ["BC-P2-03"], "Reproduced."),
    "A0-O4-03": (C, True, ["BC-P2-04"], "Reproduced and by AC16-X1."),
    "A0-O5-01": (C, True, ["BC-P2-06"], "Reproduced."),
    "A0-O5-02": (C, True, ["BC-P2-06"], "Reproduced (single thread sampled again)."),
    "A0-O5-03": (C, True, ["BC-P2-06"], "Reproduced."),
    "A0-O5-04": (C, True, ["BC-P2-06"], "Reproduced."),
    "A0-O5-05": (C, True, ["BC-P2-08"], "Reproduced (G0 matrix re-run: same mutating-while-frozen set; 'gate present' mutates in whichever control state it runs first)."),
    "A0-O5-06": (C, True, ["BC-P2-07"], "Reproduced."),
    "A0-O5-07": (C, True, ["BC-P2-07"], "Reproduced."),
    "A0-O5-08": (C, True, ["BC-P2-07"], "Reproduced and by AC16-X1 [X1-W12-G4-wider-check-recorded FAIL]."),
    "A0-O5-09": (C, True, ["BC-P2-07"], "Reproduced (O5-G5-update re-run byte-identical)."),
    "A0-O5-10": (C, True, ["BC-P2-07"], "Reproduced (no qualify/oracle/score/qualification subcommand: AC06-oracle-format-search)."),
    "A0-O5-11": (C, True, ["BC-P2-06"], "Reproduced."),
    "A0-O5-12": (C, True, ["BC-P2-06"], "Reproduced."),
    "A0-O5-13": (C, True, ["BC-P2-24"], "Reproduced."),
    "A0-O5-14": (C, True, ["BC-P2-01"], "Reproduced (AC01-09-13-14: O5, V1-V4 compiled ORIGINAL; O5 title retains the marker)."),
    "A0-O5-15": (C, False, [], "Reproduced. R2 later-lifecycle note (release certification)."),
    "A0-P1-01": (C, False, [], "Reproduced. Non-blocking accepted."),
    "A0-P2-01": (C, False, [], "Reproduced. Non-blocking accepted."),
    "A0-Q1-01": (C, False, [], "Reproduced. Non-blocking accepted."),
    "A0-Q1-02": (C, True, ["BC-P2-10"], "Reproduced."),
    "A0-Q1-03": (C, False, [], "Reproduced. INFO."),
    "A0-Q2-01": (C, False, [], "Reproduced. Non-blocking accepted (the deterministic authority block excludes lessons; zeta-r W2:1087 P&S agrees)."),
    "A0-Q4-01": (C, True, ["BC-P2-50"], "Reproduced."),
    "A0-U-01": (C, True, ["BC-P2-44"], "Reproduced."),
    "A0-U-02": (C, True, ["BC-P2-44"], "Reproduced and by AC16-X1 [X1-UxO5-health-reflects-invalid-completed-work FAIL: audit and doctor HEALTHY]."),
    "A0-U-03": (C, True, ["BC-P2-01", "BC-P2-02"], "Reproduced (AC01-09-13-14: U missing from compiled form, evidence map and generated view; the compiled-form schema cannot express it)."),
    "A0-V1-01": (C, True, ["BC-P2-51"], "Reproduced and independently re-established by AC06-oracle-format-search (no V1-V4 identifier, schema or command anywhere in the tree)."),
    # ---------------- zeta-r
    "A0-W1-01": (C, True, ["BC-P2-21"], "Reproduced; extended by S0-W1-01 (adoption catalogue ids positional)."),
    "A0-W2-01": (C, True, ["BC-P2-21"], "Reproduced."),
    "A0-W2-02": (C, True, ["BC-P2-17"], "Reproduced."),
    "A0-W3-01": (C, True, ["BC-P2-16"], "Reproduced."),
    "A0-W3-02": (C, True, ["BC-P2-17"], "Reproduced."),
    "A0-W3-03": (C, True, ["BC-P2-17"], "Reproduced."),
    "A0-W3-04": (C, True, ["BC-P2-18"], "Reproduced."),
    "A0-W4-01": (C, True, ["BC-P2-19"], "Reproduced."),
    "A0-W4-02": (C, True, ["BC-P2-19"], "Reproduced."),
    "A0-W4-03": (C, True, ["BC-P2-19"], "Reproduced."),
    "A0-W4-04": (C, False, [], "Reproduced. Non-blocking accepted."),
    "A0-W4-05": (C, False, [], "Reproduced. INFO."),
    "A0-W5-01": (C, True, ["BC-P2-20"], "Reproduced."),
    "A0-W5-02": (C, True, ["BC-P2-20"], "Reproduced."),
    "A0-W5-03": (C, False, [], "Reproduced. Non-blocking accepted."),
    "A0-W6-01": (C, True, ["BC-P2-04"], "Reproduced and by AC16-X1 (close cleared the CIT retest flag without retest evidence)."),
    "A0-W6-02": (C, True, ["BC-P2-04"], "Reproduced and by AC16-X1 [X1-G1xW6-direct-change-cannot-be-licensed-by-rebuild FAIL]."),
    "A0-W6-03": (C, True, ["BC-P2-04"], "Reproduced and by AC16-X1 [X1-K2xW6-packet-invalidated FAIL]."),
    "A0-W6-04": (C, True, ["BC-P2-04"], "Reproduced."),
    "A0-W6-05": (C, True, ["BC-P2-03"], "Reproduced. AC-12 tag not adopted (see A0-O3-01)."),
    "A0-W7-01": (C, True, ["BC-P2-22"], "Reproduced."),
    "A0-W8-01": (C, True, ["BC-P2-20"], "Reproduced."),
    "A0-W9-01": (C, True, ["BC-P2-05"], "Reproduced and by AC16-X1."),
    "A0-W10-01": (C, True, ["BC-P2-19"], "Reproduced."),
    "A0-W11-01": (C, True, ["BC-P2-23"], "Reproduced."),
    "A0-W12-01": (C, True, ["BC-P2-07"], "Reproduced."),
    "A0-W-01": (C, True, ["BC-P2-01", "BC-P2-02"], "Reproduced."),
}

SEVCORR = {"A0-B2-02": "MEDIUM"}
CORR_KIND = {"A0-A5-01": "blocking_status", "A0-B2-02": "blocking_status+severity", "A0-S4-02": "blocking_status", "A0-S4-03": "blocking_status",
             "A0-S5-02": "blocking_status", "A0-E1-04": "blocking_status+owner_decision_split", "A0-E1-06": "blocking_status", "A0-F1-01": "blocking_status",
             "A0-F4-04": "blocking_status (new evidence S0-F4-01)", "A0-H3-01": "blocking_status", "A0-A2-01": "owner_decision_classification (blocking confirmed)",
             "A0-A2-02": "owner_decision_split (blocking confirmed)", "A0-L3-01": "owner_decision_classification (blocking confirmed)",
             "A0-L3-05": "owner_decision_classification (blocking confirmed)", "A0-F4-03": "owner_decision_classification (blocking confirmed)"}
# cross-family attribution: findings that also falsify a bullet of another capability (synthesis correction of A1)
EXTRA_CAPS = {"A0-M1-02": ["A1"], "A0-H3-01": ["A1"]}  # blocking after correction; LOW understated a gap on a named Repo B / V2 path

# ------------------------------------------------------------------------------------------------ synthesis findings
S = [
    {"id": "S0-AC13-01", "capability": ["all 101 (contract binding chain)"], "severity": "MEDIUM", "blocker_class": ["BC-P2-01"],
     "title": "`gov contract verify` cannot detect semantic divergence; the compiled-form schema cannot represent Gate U",
     "statement": "contracts::verify (runtime/src/contracts.rs:167-245) checks the canonical import's digest and byte identity, the lock's source digests, and that the compiled YAML equals a fresh run of the same headings-only compiler; it never reads the evidence map or the generated view, and it has no reference to the owner source's checklist, fields or labels, so a compiled form with 0 of 344 substantive bullets, no Gate U and misclassified O5/V1-V4 verifies CONTRACT_SOURCE_BOUND. The compiled-form schema's id pattern ^[A-Z]+[0-9]+$ rejects 'U', so the present schema cannot carry the full owner universe.",
     "normative_source": "Governance_OS_Capability_Acceptance_Contract_v3.md:43 'valid only when contract-source.lock proves that it was compiled/validated from the exact approved source'; :47 'Any semantic difference between source and compiled representation is a hard failure.'; frozen gate contract AC-13.",
     "provenance_class": "ORIGINAL-NORMATIVE", "blocks": ["AC-13"], "blocking": True,
     "evidence": ["evidence/AC01-09-13-14-universe-identity-binding.py", "evidence/AC01-09-13-14-universe-identity-binding.out ([AC-13] lines)"],
     "reproduction": "python3 release/capability-baseline/audit-0/synthesis/evidence/AC01-09-13-14-universe-identity-binding.py",
     "repair_direction": "Verification of the binding chain must fail whenever the compiled form, the evidence map or the generated view differs semantically from the owner source (every capability section including Gate U, every checklist bullet, every Contract v3:53-73 field, every requirement-class label), not only when it differs from the compiler's own output (Contract v3:43, :47)."},
    {"id": "S0-B1B3-01", "capability": ["B1", "B3", "D6", "C1"], "severity": "MEDIUM", "blocker_class": ["BC-P2-31"],
     "title": "The product classifies the stores of claims, emergency-control state and the OS plugin registry as derived/generated",
     "statement": "REPOSITORY_CONTRACT (framework/overlay-templates/REPOSITORY_CONTRACT.yaml:140) classifies `.governance-runtime/**` as `derived`, which holds claims.db (C1 lists 'claims' as current truth) and control.json (FREEZE_WRITES/PAUSE); `governance/generated/**` (`generated`) holds plugin-registry.json, which D-0007 names T2 authoritative OS-written state. docs/ARCHITECTURE.md:76 says everything in .governance-runtime/ is derived and rebuildable while :119-120 says claims and control state are not touched by rebuild. beta-r's D6 probe (re-run identical) shows deleting what the product declares derived loses the claim and lifts FREEZE_WRITES. B1:188 and B3:202 were recorded PRESENT_AND_SUBSTANTIAL by alpha-r; both are corrected to PARTIAL.",
     "normative_source": "Contract v3:188 'Generated/runtime state is distinguished from authoritative tracked state.'; :202 'Deleting derived state cannot delete project truth.'; :213-227 (C1 claims); :352 'Fresh rebuild preserves authoritative structured state and claims where required.'; spec/decisions/D-0007.yaml T2.",
     "provenance_class": "ORIGINAL-NORMATIVE", "blocks": ["AC-3"], "blocking": True,
     "evidence": ["evidence/AC16-X2-authority-gate-chain.out [X2-B1B3-nonrebuildable-state-not-classified-derived]", "release/capability-baseline/audit-0/beta-r/evidence/D6-rebuild-guarantee.out (re-run identical)"],
     "reproduction": "SYNTH_SCRATCH=$(mktemp -d) python3 release/capability-baseline/audit-0/synthesis/evidence/AC16-X2-authority-gate-chain.py",
     "repair_direction": "Non-rebuildable authoritative state (claims, emergency-control state, OS plugin registration) must be stored and classified as authoritative (or protected) state that survives deletion of every path the product classifies derived or generated, and the product's own documentation and repository contract must agree (Contract v3:188, :202, :352)."},
    {"id": "S0-I4-01", "capability": ["I4", "U"], "severity": "MEDIUM", "blocker_class": ["BC-P2-16"],
     "title": "A task whose status is BLOCKED is in the runnable set and is offered by `gov continue`",
     "statement": "After `gov task status TASK-B BLOCKED`, `gov task dag` lists TASK-B in runnable and `gov continue` returns NEXT_WORK TASK-B (task_status BLOCKED). delta-r observed this (L4-non-global-blocking OBSERVE L4.b2.3a, re-run identical) and passed it on; gamma-r recorded I4 bullet 587 'runnable/blocked sets' PRESENT_AND_SUBSTANTIAL. I4 is corrected: bullet 587 PARTIAL, qualification impact COULD_UNDERMINE (V4 'task/readiness correctness' and the U HEALTHY condition 'task runnable/blocked state correct' score it).",
     "normative_source": "Contract v3:587 'runnable/blocked sets'; :1003 'task runnable/blocked state correct'; :1060 'task/readiness correctness'.",
     "provenance_class": "ORIGINAL-NORMATIVE", "blocks": ["AC-3"], "blocking": True,
     "evidence": ["evidence/AC16-X2-authority-gate-chain.out [X2-I4-blocked-not-runnable], [X2-I4-continue-does-not-offer-blocked]"],
     "reproduction": "SYNTH_SCRATCH=$(mktemp -d) python3 release/capability-baseline/audit-0/synthesis/evidence/AC16-X2-authority-gate-chain.py",
     "repair_direction": "A task in a blocked state must be excluded from the runnable set and from next-work selection until the state that blocks it is resolved (Contract v3:587)."},
    {"id": "S0-E1-01", "capability": ["E1", "L3"], "severity": "HIGH", "blocker_class": ["BC-P2-08"],
     "title": "An invocation that declares no role acts as the L4 orchestrator",
     "statement": "Every command's --role defaults to $GOV_ROLE or 'orchestrator' (project.rs:40-49; CLI help 'Acting role (default: $GOV_ROLE or orchestrator)'); a process that declares nothing performs L4-only operations (gate revoke succeeded with no role) and, combined with `gov decide`'s --by default 'human', records human approval.",
     "normative_source": "DYNAMIC_AGENTIC_SOFTWARE_ENGINEERING_OPERATING_FRAMEWORK_v4.1.2.md §23 'No spawned worker behaves as an orchestrator unless explicitly assigned that role.'; Contract v3:364 'Role authority is checked on every privileged/mutating path.'",
     "provenance_class": "ORIGINAL-NORMATIVE", "blocks": ["AC-3"], "blocking": True,
     "evidence": ["evidence/AC16-X2-authority-gate-chain.out [X2-E1-undeclared-role-is-not-orchestrator], [X2-L3-fabrication-default]"],
     "reproduction": "SYNTH_SCRATCH=$(mktemp -d) python3 release/capability-baseline/audit-0/synthesis/evidence/AC16-X2-authority-gate-chain.py",
     "repair_direction": "An invocation without an explicitly assigned role must not receive orchestrator (or any privileged) authority, and no default may yield a human answer (framework §23; Contract v3:364, :679)."},
    {"id": "S0-F4-01", "capability": ["F4", "D5"], "severity": "HIGH", "blocker_class": ["BC-P2-40"],
     "title": "A registered, gate-approved, elevated plugin in module form has no implementation pin; post-approval code swaps run undetected",
     "statement": "An embed plugin with command [python3, -m, synthplug], permissions network true and required_permission_classes [NETWORK_READ] was registered through a presented, human-answered registration gate; its registry entry has implementation_files [] and implementation_sha256 null. After its module source was replaced, `gov capabilities invoke` ran the new code (it wrote SWAPPED_IMPLEMENTATION_RAN.txt) with no PLUGIN_PIN_MISMATCH, and doctor D028 reported 'no plugin problems'. Cause: capabilities/governance.rs:79-122 hashes only command arguments that resolve to local files, and the registered-implementation check is skipped when the registered hash is null. The `python3 -m` form is the one the shipped capability templates document (beta-r OBS-1).",
     "normative_source": "Contract v3:428 'Descriptor/implementation bytes are hash-bound.'; :429 'Drift/tampering fails closed.'; ARCH-0003 §9 'their bytes and descriptor identity are bound through kernel-owned registration/policy'.",
     "provenance_class": "OWNER-ADDED-NORMATIVE", "blocks": ["AC-4", "AC-3"], "blocking": True,
     "evidence": ["evidence/LEAD-X4-registered-module-plugin-unpinned.py", "evidence/LEAD-X4-registered-module-plugin-unpinned.out"],
     "reproduction": "SYNTH_SCRATCH=$(mktemp -d) python3 release/capability-baseline/audit-0/synthesis/evidence/LEAD-X4-registered-module-plugin-unpinned.py",
     "repair_direction": "Every executable plugin's implementation bytes (including module-form and interpreter-only commands) must be bound in the registration, and any change must fail closed at execution and be reported by health checks (Contract v3:428-429)."},
    {"id": "S0-S4-01", "capability": ["S4", "B2", "R1"], "severity": "MEDIUM", "blocker_class": ["BC-P2-33"],
     "title": "Re-running adoption classifies the Governance OS's own generated IDE adapter as legacy provider rules and archives it",
     "statement": "After one A0-A7 adoption of the brownfield fixture, a second A0-A7 pass classified governance/generated/adapters/ide/RULES.md as class GOVERNANCE_LEGACY, authority LEGACY, kinds [provider_rules, doc], mapped it MOVE to archive/governance/legacy-rules/, and executed the move (A7 accepted). The OS's own agent-facing adapter left the active tree (beta-r OBS-2, reproduced independently).",
     "normative_source": "Contract v3:874 'mark old governance LEGACY' (current governance is not old governance); :191 'Every material artefact can be classified by current path, class, authority and intended target.'; :923-925 (A0/A1/A2 stages); adoption protocol A0 'detect interrupted prior governance work'.",
     "provenance_class": "ORIGINAL-NORMATIVE", "blocks": ["AC-3"], "blocking": True,
     "evidence": ["evidence/LEAD-X5-adoption-rerun-archives-os-adapter.py", "evidence/LEAD-X5-adoption-rerun-archives-os-adapter.out [X5-S4xB2-os-generated-adapter-not-legacy]"],
     "reproduction": "SYNTH_SCRATCH=$(mktemp -d) python3 release/capability-baseline/audit-0/synthesis/evidence/LEAD-X5-adoption-rerun-archives-os-adapter.py",
     "repair_direction": "Adoption classification must recognise the Governance OS's own installed and generated state and never classify or retire it as legacy governance (Contract v3:874, :191)."},
    {"id": "S0-W1-01", "capability": ["W1", "T3", "S4"], "severity": "MEDIUM", "blocker_class": ["BC-P2-21"],
     "title": "Adoption catalogue artefact ids are positional: they change on re-run and the migration ledger then names other artefacts",
     "statement": "Between two adoption passes 21 paths changed artifact_id (e.g. .env ART-00003 -> ART-00002); migration-ledger.jsonl accumulates entries from both passes, so 13 ledger entries name ids that the current catalogue assigns to different paths (e.g. ledger ART-00002 = .cursorrules, catalogue ART-00002 = .env). This is the mechanism behind beta-r OBS-2's 'ledger/catalogue id mismatch'.",
     "normative_source": "Contract v3:1070 'stable artefact ID'; :1080 'Applies to ... migration plans ...'; :972 (traceable adoption evidence tree); :945 'ledger/provenance'.",
     "provenance_class": "ORIGINAL-NORMATIVE", "blocks": ["AC-3", "AC-8"], "blocking": True,
     "evidence": ["evidence/LEAD-X5-adoption-rerun-archives-os-adapter.out [X5-W1-catalogue-ids-stable-across-passes], [X5-T3-ledger-ids-match-catalogue]"],
     "reproduction": "SYNTH_SCRATCH=$(mktemp -d) python3 release/capability-baseline/audit-0/synthesis/evidence/LEAD-X5-adoption-rerun-archives-os-adapter.py",
     "repair_direction": "Every catalogued artefact must keep a stable identity across re-runs of adoption stages, and ledger entries must remain resolvable to the artefact they recorded (Contract v3:1070, :1080, :972)."},
    {"id": "S0-W5-01", "capability": ["W5", "N4", "E3"], "severity": "MEDIUM", "blocker_class": ["BC-P2-20"],
     "title": "A worker return that satisfies the worker-return schema cannot be used as the task-close receipt",
     "statement": "worker-return.schema.json requires status in {success, partial, failed, blocked}; task close persists the report as a record whose status must be a lifecycle status. Passing a schema-valid worker return (accepted by `gov handoff return`) to `gov task close --report` fails SCHEMA_INVALID ('/status: \"success\" is not one of [\"ACTIVE\", ...]'). The structured result survives (N4 holds), but the worker's return cannot be the consumption receipt, so discoveries/unresolved/deviations recorded in it never reach close (beta-r OBS-3, reproduced).",
     "normative_source": "Contract v3:1115-1126 (W5 'Worker/task return records ... Task close refuses missing mandatory traceability'); :385 (E3 typed handoffs persist); :745 (N4).",
     "provenance_class": "NECESSARY-DERIVED", "blocks": ["AC-8", "AC-3"], "blocking": True,
     "evidence": ["evidence/AC16-X2-authority-gate-chain.out [X2-N4xW5-worker-return-usable-at-close]"],
     "reproduction": "SYNTH_SCRATCH=$(mktemp -d) python3 release/capability-baseline/audit-0/synthesis/evidence/AC16-X2-authority-gate-chain.py",
     "repair_direction": "The worker return and the task-close receipt must be one consumable contract (or a lossless, validated mapping), so the receipt W5 requires is the worker's own structured return (Contract v3:1115-1126)."},
    {"id": "S0-R1-01", "capability": ["W1-W12", "O5"], "severity": "INFO", "blocker_class": [],
     "title": "R1 item 11 ('Gate W and G0-G6 implementation mappings remain valid') was assessed as non-regression only",
     "statement": "AR-0027, AR-0029/31 and AR-0033 (release/verification/4.1.6-r1*/00-VERIFICATION-REPORT.md: R1-11 / item 11) dispositioned the item on builder suites passing unmodified and an unchanged contract import; none examined whether Gate W or a G0-G6 scheduler exists, and AR-0027 records capability evidence population as R2 (AR27-N7). R1's acceptance is therefore still valid for this byte-identical candidate (AC-14, AC-4) for what it examined, but it is not evidence that Gate W or G0-G6 capabilities are present; the Phase-2 statuses of W1-W12 and O5 stand on Phase-2 evidence alone.",
     "normative_source": "release/root-of-trust/signed-release-root-v1/01-FROZEN-R0-R1-R2-R3-ACCEPTANCE-BOUNDARY.md R1 list; Contract v3 O3:784 (builder tests are regression evidence).",
     "provenance_class": "LATER-QUALIFICATION/CERTIFICATION", "blocks": [], "blocking": False,
     "evidence": ["release/verification/4.1.6-r1/00-VERIFICATION-REPORT.md:234-240", "release/verification/4.1.6-r1-4/00-VERIFICATION-REPORT.md:415"],
     "reproduction": "grep -n 'Gate W' release/verification/4.1.6-r1*/00-VERIFICATION-REPORT.md",
     "repair_direction": "None for Phase 2. At R2 ('Gate W dependency/consumption evidence'; 'G6 and release qualification') R1-11 must not be cited as capability evidence."},
    {"id": "S0-AC09-01", "capability": ["(phase-2 tooling)"], "severity": "INFO", "blocker_class": [],
     "title": "product_identity.py prints the annotated-tag object id as 'commit' when given a tag name",
     "statement": "`product_identity.py cap2-candidate-0` prints 'commit: 9ee8dff…' (the tag object) instead of 57177a3…; the digests are unaffected because tree lookups dereference the tag. Non-product orchestration tooling.",
     "normative_source": "frozen gate contract AC-9 (commit, tag, product_code_digest, governed_state_digest).",
     "provenance_class": "VERIFIER-HARDENING", "blocks": [], "blocking": False,
     "evidence": ["evidence/AC01-09-13-14-universe-identity-binding.out [AC-9] quirk line"],
     "reproduction": "python3 release/orchestration/phase-2/tools/product_identity.py cap2-candidate-0",
     "repair_direction": "Resolve the argument with `^{commit}` before printing it."},
]

# ------------------------------------------------------------------------------------------- capability corrections
# cap: dict(final_status, impact_override, bullet_overrides {line: status}, reason)
CAPCORR = {
    "A1": {"impact": "COULD_UNDERMINE — the A1 challenge (Contract v3:140) injects 'attempted authority/sensitivity weakening' through project policy; MODEL_ROUTING_OVERRIDES lowers kernel tier floors and reasoning minimums (A0-M1-02) and PROJECT_POLICY switches off readiness gating (A0-H3-01) outside POLICY_PRECEDENCE, unrefused and unreported.",
           "bullets": {134: "PARTIAL", 135: "PARTIAL"}, "reason": "Cross-family correction: A1:134/135 falsified by delta-r A0-M1-02 and gamma-r A0-H3-01 (both re-run identical); alpha-r evaluated PROJECT_POLICY overrides only."},
    "A5": {"impact": "COULD_UNDERMINE — the FREEZE_WRITES leak (A0-A5-01) is the G0 guard gap AC-5 requires closed (A0-O5-05); the CANCEL_AGENTS and resume-audit gaps alone cannot undermine qualification.",
           "bullets": {}, "reason": "Impact aligned with the blocking G0 class BC-P2-08."},
    "B1": {"status": "PARTIAL", "impact": "COULD_UNDERMINE — Gate D's 'deleted indexes' challenge (Contract v3:356) deletes what the product declares derived, losing claims and lifting FREEZE_WRITES; the OS plugin registry sits in generated state.",
           "bullets": {188: "PARTIAL"}, "reason": "S0-B1B3-01 (synthesis) with beta-r D6 evidence."},
    "B2": {"impact": "COULD_UNDERMINE — the Repo B challenge ('hidden cross-references', Contract v3:197) and V2 'expected references/consumers' (:1035) score citations the path map does not represent (A0-B2-02).",
           "bullets": {}, "reason": "AC-3 criterion applied uniformly (see report §3)."},
    "B3": {"status": "PARTIAL", "impact": "COULD_UNDERMINE — as B1: deleting derived-classified state deletes claims (C1 current truth) and emergency-control state.",
           "bullets": {202: "PARTIAL"}, "reason": "S0-B1B3-01 (synthesis) with beta-r D6 evidence."},
    "F1": {"impact": "COULD_UNDERMINE — a skill_regression result that is green without executing any scenario is untrustworthy G5 evidence (same mechanism epsilon-r rated blocking in O2).",
           "bullets": {}, "reason": "Consistency with epsilon-r A0-O2-01."},
    "I4": {"impact": "COULD_UNDERMINE — V4 'task/readiness correctness' (Contract v3:1060) and the U condition 'task runnable/blocked state correct' (:1003) score a BLOCKED task that the product offers as runnable (S0-I4-01).",
           "bullets": {587: "PARTIAL"}, "reason": "S0-I4-01 (delta-r lead L4.b2.3a, reproduced)."},
    "F4": {"impact": None, "bullets": {}, "reason": "Status unchanged (PARTIAL); bullets 428/429 gaps extended to registered module-form plugins (S0-F4-01)."},
    "S4": {"impact": None, "bullets": {}, "reason": "Status unchanged (PARTIAL); additional gaps S0-S4-01 and S0-W1-01 (adoption re-run)."},
    "W5": {"impact": None, "bullets": {}, "reason": "Status unchanged (PARTIAL); additional gap S0-W5-01."},
}


def load(f, name):
    return yaml.safe_load(open(os.path.join(A0, f, name)))


def gate_of(c):
    return re.match(r"[A-Z]+", c).group(0)


def main():
    caps, finds = collections.OrderedDict(), {}
    for fam in FAM:
        for c in load(fam, "capability-audit.yaml")["capabilities"]:
            c["_family"] = fam
            caps[str(c["capability"])] = c
        for f in load(fam, "findings.yaml")["findings"] or []:
            f["_family"] = fam
            finds[f["id"]] = f
    missing = [i for i in finds if i not in D]
    extra = [i for i in D if i not in finds]
    assert not missing and not extra, (missing, extra)

    # ---------------------------------------------------------------- findings.yaml
    disp = []
    for fid, f in finds.items():
        d, blk, cls, note = D[fid]
        disp.append({"id": fid, "family": f["_family"], "family_run": FAM[f["_family"]], "capability": f.get("capability"),
                     "family_severity": f.get("severity"), "final_severity": SEVCORR.get(fid, f.get("severity")), "family_blocking": f.get("blocking"),
                     "family_owner_decision_required": f.get("owner_decision_required"),
                     "disposition": d, "correction_kind": CORR_KIND.get(fid) if d == R_ else None, "final_blocking": blk, "blocker_class": cls,
                     "owner_decision_required": False if fid in ("A0-A2-01", "A0-L3-01", "A0-L3-05", "A0-F4-03") else (
                         "split: human-approval part false (BC-P2-10); agent-role identity part -> OD-P2-01" if fid == "A0-E1-04" else (
                             "split: presentation/visibility part false (BC-P2-36); unprovisioned ingress scope -> OD-P2-02" if fid == "A0-A2-02" else f.get("owner_decision_required"))),
                     "new_vs_residual": "BASELINE",
                     "synthesis_evidence": RERUN.format(fam=f["_family"]),
                     "note": note, "title": f.get("title")})
    syn = []
    for s in S:
        s2 = dict(s)
        s2.update({"lifecycle": "P2" if s["blocking"] else ("R2" if s["id"] == "S0-R1-01" else "P2"),
                   "falsifies_or_proposes": "FALSIFIES_PHASE2_REQUIREMENT" if s["blocking"] else "PROPOSES_STRONGER_LATER_ASSURANCE",
                   "blocks_acceptance_criteria": s["blocks"], "owner_decision_required": False, "owner_decision_reason": None,
                   "new_vs_residual": "BASELINE"})
        s2.pop("blocks")
        syn.append(s2)
    counts = collections.Counter(x["disposition"] for x in disp)
    fblock = sum(1 for x in disp if x["final_blocking"]) + sum(1 for s in S if s["blocking"])
    out = {"schema": "governance-os.phase-2.findings", "schema_version": 1, "run_id": "P2-AR-0007",
           "summary": {"family_findings": len(disp), "dispositions": dict(counts),
                       "family_findings_blocking_after_synthesis": sum(1 for x in disp if x["final_blocking"]),
                       "synthesis_findings": len(S), "synthesis_findings_blocking": sum(1 for s in S if s["blocking"]),
                       "total_blocking": fblock},
           "findings": syn, "family_finding_dispositions": disp}
    yaml.safe_dump(out, open(os.path.join(OUT, "findings.yaml"), "w"), sort_keys=False, width=180, allow_unicode=True)

    # ---------------------------------------------------------------- blocker-classes.yaml
    members = collections.defaultdict(list)
    for x in disp:
        for c in x["blocker_class"]:
            members[c].append(x["id"])
    for s in S:
        for c in s["blocker_class"]:
            members[c].append(s["id"])
    sev_rank = {"CRITICAL": 5, "HIGH": 4, "MEDIUM": 3, "LOW": 2, "INFO": 1}
    sev = {**{x["id"]: x["final_severity"] for x in disp}, **{s["id"]: s["severity"] for s in S}}
    classes = []
    for cid, (title, cp, mech, acs) in BC.items():
        m = members.get(cid, [])
        assert m, cid
        classes.append({"id": cid, "title": title, "capabilities": cp, "mechanism": mech, "acceptance_criteria_blocked": acs,
                        "max_severity": max((sev[i] for i in m), key=lambda s: sev_rank[s]), "finding_count": len(m), "findings": m})
    for c in members:
        assert c in BC, c
    yaml.safe_dump({"schema": "governance-os.phase-2.blocker-classes", "schema_version": 1, "run_id": "P2-AR-0007",
                    "candidate": "cap2-candidate-0", "product_code_digest": "bd4d65d9d5ffd6aedbd9435e2091a664dfc3e62f80614a76197cfaf87efd0547",
                    "convergence_rule": "frozen gate contract §8: a later finding in an inventoried class (same capability AND same mechanism, including an incomplete fix) is RESIDUAL; a capability or mechanism absent from this inventory, or a regression a repair introduced into a previously held capability, is MATERIALLY_NEW. A finding listed under two classes (derived-view findings A0-A1-02/C1-01/E1-06/J1-02/O1-03/U-03/W-01) carries two distinct mechanisms (compiled-form fidelity; evidence-map owners).",
                    "class_count": len(classes), "blocking_findings_inventoried": len({i for c in classes for i in c["findings"]}),
                    "classes": classes}, open(os.path.join(OUT, "blocker-classes.yaml"), "w"), sort_keys=False, width=180, allow_unicode=True)

    # ---------------------------------------------------------------- capability-status-matrix.yaml
    blocking_by_cap = collections.defaultdict(set)
    classes_by_cap = collections.defaultdict(set)
    for x in disp:
        if x["final_blocking"]:
            for cp in list(x["capability"] or []) + EXTRA_CAPS.get(x["id"], []):
                blocking_by_cap[str(cp)].add(x["id"])
                for c in x["blocker_class"]:
                    classes_by_cap[str(cp)].add(c)
    for s in S:
        if s["blocking"]:
            for cp in s["capability"]:
                blocking_by_cap[cp].add(s["id"])
                for c in s["blocker_class"]:
                    classes_by_cap[cp].add(c)
    rows, final_count = [], collections.Counter()
    for cid, c in caps.items():
        corr = CAPCORR.get(cid, {})
        bcount = collections.Counter(b["status"] for b in c.get("bullets") or [])
        final_b = collections.Counter()
        for b in c.get("bullets") or []:
            st = corr.get("bullets", {}).get(int(b["source_line"]), b["status"])
            final_b[st] += 1
        fstat = corr.get("status", c["status"])
        final_count[fstat] += 1
        rows.append({"capability": cid, "gate": gate_of(cid), "title": c.get("title"), "requirement_class": c.get("requirement_class"),
                     "owning_family": c["_family"], "family_run": FAM[c["_family"]], "family_status": c["status"],
                     "final_status": fstat, "status_corrected": fstat != c["status"],
                     "family_bullet_counts": dict(bcount), "final_bullet_counts": dict(final_b),
                     "bullet_corrections": {int(k): v for k, v in corr.get("bullets", {}).items()} or None,
                     "family_qualification_impact": (str(c.get("partial_qualification_impact")).split(" ")[0].rstrip(".:;,") if c.get("partial_qualification_impact") else None),
                     "final_qualification_impact": (corr.get("impact") or c.get("partial_qualification_impact")) if fstat == "PARTIAL" else None,
                     "correction_reason": corr.get("reason"),
                     "evidence_location": [f"release/capability-baseline/audit-0/{c['_family']}/capability-audit.yaml#{cid}",
                                           f"release/capability-baseline/audit-0/{c['_family']}/evidence/"] +
                                          (["release/capability-baseline/audit-0/synthesis/evidence/"] if cid in CAPCORR or cid in blocking_by_cap and any(i.startswith("S0-") for i in blocking_by_cap[cid]) else []),
                     "blocking_findings": sorted(blocking_by_cap.get(cid, [])),
                     "blocker_classes": sorted(classes_by_cap.get(cid, []))})
    yaml.safe_dump({"schema": "governance-os.phase-2.capability-status-matrix", "schema_version": 1, "run_id": "P2-AR-0007",
                    "candidate": "cap2-candidate-0", "candidate_commit": "57177a37ea296ece16b185874831462b6a76db18",
                    "product_code_digest": "bd4d65d9d5ffd6aedbd9435e2091a664dfc3e62f80614a76197cfaf87efd0547",
                    "universe": {"capabilities": len(rows), "source": "Governance_OS_Capability_Acceptance_Contract_v3.md (evidence/AC01-09-13-14-universe-identity-binding.out [UNIV])"},
                    "final_status_counts": dict(final_count),
                    "family_status_counts": dict(collections.Counter(r["family_status"] for r in rows)),
                    "capabilities": rows}, open(os.path.join(OUT, "capability-status-matrix.yaml"), "w"), sort_keys=False, width=180, allow_unicode=True)

    # ---------------------------------------------------------------- suite-to-contract-matrix.yaml
    emap = {r["capability"]: r for r in yaml.safe_load(open(os.path.join(ROOT, "tests/governance/capability-evidence-map.yaml")))["capabilities"]}
    srows = []
    for cid, c in caps.items():
        fr = c.get("freshness") or {}
        owners = c.get("evidence_owners") or []
        runs = str(c.get("evidence_owner_actually_runs"))
        product_owners = [o for o in owners if o.startswith("G")]
        srows.append({"capability": cid, "evidence_owners_identified_by_audit": owners,
                      "product_declared_owners_in_evidence_map": (emap.get(cid) or {}).get("automated_checks", "ROW ABSENT"),
                      "product_declared_evidence_class": (emap.get(cid) or {}).get("evidence_class", "ROW ABSENT"),
                      "owner_actually_runs": runs[:400],
                      "zero_evidence_owners": (not owners) or runs.startswith("false"),
                      "scheduled_tier_owner_runs": False,
                      "health_scheduler_tiers": c.get("health_scheduler_tiers"),
                      "freshness_state": fr.get("state"), "invalidation_inputs": fr.get("invalidation_inputs"),
                      "invalidation_demonstrated": fr.get("invalidation_demonstrated"), "invalidation_evidence": fr.get("invalidation_evidence")})
    zero = [r["capability"] for r in srows if r["zero_evidence_owners"]]
    not_demo = [r["capability"] for r in srows if r["invalidation_demonstrated"] is not True]
    yaml.safe_dump({"schema": "governance-os.phase-2.suite-to-contract-matrix", "schema_version": 1, "run_id": "P2-AR-0007",
                    "determination": {
                        "product_declared_owners": "0 of 101 capabilities have any automated check in tests/governance/capability-evidence-map.yaml (100 rows, all NOT_YET_MAPPED; U has no row).",
                        "audit_identified_owner_that_actually_runs": f"{len(zero)} capabilities have no evidence owner that runs: {zero}. For every other capability the owners are G-tier-EQUIVALENT host-command checks (no G0-G6 scheduler exists: scheduled_tier_owner_runs false for all 101).",
                        "invalidation": f"Invalidation of prior green evidence was demonstrated to WORK for policy, kernel, schema, migration, repository contract, sensitivity, plugin descriptor, retrieval profile, held-out set and decision inputs, and demonstrated to FAIL (evidence stays green) for requirements, architecture, interfaces, source files, index manifest, tool/plugin registry, research/experiment/task/checkpoint/handoff records, adoption evidence, trust state and the runtime implementation (BC-P2-03). {len(not_demo)} capabilities do not have product-side invalidation of their evidence shown working: {not_demo}.",
                        "AC-10": "FAILS"},
                    "capabilities": srows}, open(os.path.join(OUT, "suite-to-contract-matrix.yaml"), "w"), sort_keys=False, width=180, allow_unicode=True)

    # ---------------------------------------------------------------- qualification-coverage-matrix.yaml
    qrows, incomplete = [], []
    for cid, c in caps.items():
        q = c.get("qualification_coverage") or {}
        row = {"capability": cid, **{k: q.get(k) for k in ("repo_a_challenge", "repo_b_challenge", "hidden_oracle_fault_class", "chaos_scale_soak", "retrieval_challenge", "not_challengeable")},
               "proposed_by": FAM[c["_family"]]}
        need = ["repo_a_challenge", "repo_b_challenge", "hidden_oracle_fault_class", "chaos_scale_soak", "retrieval_challenge"]
        empty = [k for k in need if not (row.get(k) and str(row[k]).strip())]
        if empty and not row.get("not_challengeable"):
            incomplete.append((cid, empty))
        row["complete"] = not empty or bool(row.get("not_challengeable"))
        qrows.append(row)
    yaml.safe_dump({"schema": "governance-os.phase-2.qualification-coverage-matrix", "schema_version": 1, "run_id": "P2-AR-0007",
                    "note": "Pre-qualification coverage plan (frozen contract AC-11). Challenges were proposed by the owning family audits of record and checked here for completeness and for a not-challengeable route where a synthetic repository cannot exercise the capability. No hidden fault is generated in Phase 2.",
                    "determination": {"capabilities": len(qrows), "incomplete": incomplete, "AC-11": "HOLDS" if not incomplete else "FAILS"},
                    "capabilities": qrows}, open(os.path.join(OUT, "qualification-coverage-matrix.yaml"), "w"), sort_keys=False, width=180, allow_unicode=True)

    print("final status counts:", dict(final_count))
    print("family status counts:", dict(collections.Counter(c["status"] for c in caps.values())))
    print("dispositions:", dict(counts), "| family blocking after synthesis:", sum(1 for x in disp if x["final_blocking"]),
          "| synthesis findings:", len(S), "blocking:", sum(1 for s in S if s["blocking"]), "| total blocking:", fblock)
    print("classes:", len(classes), "| inventoried blocking findings:", len({i for c in classes for i in c["findings"]}))
    print("zero-owner capabilities:", zero)
    print("qualification coverage incomplete:", incomplete)
    for c in classes:
        print(f"  {c['id']} n={c['finding_count']:2d} {c['max_severity']:6s} {c['title'][:90]}")


if __name__ == "__main__":
    main()
