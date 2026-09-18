# P2-HO-0000 — Common protocol for the iteration-0 capability family audits

Every iteration-0 family auditor (P2-AR-0001 … P2-AR-0006) reads this file **and** its own family handoff. The family
handoff names the capabilities you own; this file says how to audit them and what to produce.

## Who you are

You are a **fresh, independent Governance Capability Baseline Auditor** for Governance OS Phase 2. You authored none of the
Governance OS implementation, none of its tests, and none of the Phase-1 reviews, repairs or verifications. You are not
the orchestrator. You do not repair anything. You **never modify product source** (anything outside your own evidence
directory and your own run report). You do not issue the Phase-2 verdict — a separate synthesis auditor does, from your
evidence and five other families'.

## Pinned inputs (verify each before relying on it; record mismatches as a STOP)

| Input | Identity |
|---|---|
| Candidate | `cap2-candidate-0` — the commit your worktree is checked out at (tag `cap2-candidate-0`) |
| Candidate product code | `product_code_digest` `bd4d65d9d5ffd6aedbd9435e2091a664dfc3e62f80614a76197cfaf87efd0547` — verify with `python3 release/orchestration/phase-2/tools/product_identity.py HEAD`. Byte-identical to the R1-accepted `srr1-r1-candidate-4` (`c7d3fef`, tag `srr1-r1-accepted`). |
| Capability Acceptance Contract v3 (owner source) | `Governance_OS_Capability_Acceptance_Contract_v3.md`, SHA-256 `4c2df29115c8d5389034b2e2d817772add80d61678807c23e0d520c937cb5ed3` |
| Frozen Phase-2 gate contract | `release/orchestration/phase-2/GATES/PHASE-2-FROZEN-GATE-CONTRACT.md` — SHA-256 in `ORCHESTRATOR_STATE.yaml` `frozen_gate_contract.sha256`; verify it |
| Governing documents | the three `*.md` governing documents at the repository root |
| Active decisions / architecture | `spec/decisions/`, `spec/architecture/`, `spec/interfaces/`; owner records in `release/orchestration/phase-1/GATES/` |

**Read in full before auditing:** the frozen Phase-2 gate contract; Contract v3; the sections of the three governing
documents that your capabilities trace to (the framework's table of contents maps directly onto the contract gates).
Read the implementation, tests, fixtures, schemas, policies and docs relevant to your capabilities as deeply as needed.

## The standard you apply

- **Exhaustive.** Every checklist bullet of every capability you own is evaluated individually. No sampling.
- **Executable evidence.** *"A capability may not be reported `PRESENT_AND_SUBSTANTIAL` solely because a file/schema/policy
  exists"* (Contract v3 line 93). Documentation, a schema, a policy key, a doc comment, a CLI help string or a test
  *name* is not evidence of behaviour. For each bullet, find the code path **and** run something that exercises it.
- **Builder tests are regression evidence, not independent evidence** (O3). You may cite them as automated evidence and
  you should run them, but the independent evidence column is what **you** ran.
- **Run it.** Build in your worktree (`~/.cargo/bin/cargo build --release`; your worktree has its own `target/`). Drive
  `target/release/gov` against disposable projects you create under your scratch area — `gov init` into a temp dir,
  copies of `fixtures/*`, or synthetic trees you build. Write small probe scripts. Keep every probe's source and its
  output under your evidence directory so the synthesis auditor and later verifiers can re-run it. Probes are your
  independent evidence; they are **not** product tests and must not be added to the product tree.
- **Freshness.** For each capability, state which inputs invalidate its evidence (Contract v3 lines 95–111) and whether the
  product actually marks prior green evidence stale when such an input changes. Where cheap, **demonstrate it** (change an
  input, observe the status change) — the frozen contract's AC-10 requires invalidation to be shown, not assumed.
- **Health-scheduler tiers.** For each capability, name the G0–G6 tier(s) that would observe it (Contract v3 O5) and
  whether the product actually runs that check at that tier.
- **Qualification coverage.** For each capability, propose the Repo A (greenfield-style) and Repo B (brownfield-style)
  challenge, the hidden-oracle fault class, and chaos/scale/soak and retrieval challenges where relevant. If a capability
  cannot be meaningfully challenged in synthetic repositories, say why and name another independent evidence route
  (frozen contract AC-11). You are **not** generating hidden faults or qualification repositories — that is Phase 4.
- **Status vocabulary** exactly as frozen contract §4: `PRESENT_AND_SUBSTANTIAL`, `PARTIAL`, `ABSENT`, `UNCLEAR`,
  `N/A_WITH_REASON`. A capability is `PRESENT_AND_SUBSTANTIAL` only if all its applicable bullets are. `N/A_WITH_REASON`
  must quote the normative text that places the obligation outside Phase 2; silent N/A is invalid.
- **`PARTIAL` needs an argument.** For every `PARTIAL`, state explicitly whether the gap could undermine advanced
  qualification, and why (AC-3).
- **Lifecycle discipline.** Do not promote R2 certification, R3 high-assurance, public-cloud, Phase-3 profile selection
  or Phase-4 execution into Phase-2 blockers (frozen contract §7). Record them as later-lifecycle notes.
- **Cross-capability interactions** the contract states (frozen contract AC-16) that touch your capabilities: exercise them.

## What you produce

Everything goes under **`release/capability-baseline/audit-0/<family>/`** (your family handoff names `<family>`):

1. `00-AUDIT-REPORT.md` — human-readable: scope, method, pinned-input verification, per-capability summary table, the most
   important findings, what you could not establish and why.
2. `capability-audit.yaml` — machine-readable, one entry per capability you own, schema below.
3. `findings.yaml` — every finding, schema below. Write `findings: []` explicitly if none.
4. `evidence/` — every probe source and its captured output, named by capability (e.g. `evidence/C3-b2-semantic-filter.sh`,
   `evidence/C3-b2-semantic-filter.out`). Record the exact command lines.
5. Your run report `release/orchestration/phase-2/AGENT_RUNS/<run-id>.report.yaml` (schema in
   `release/orchestration/phase-2/AGENT_RUNS/README.md`), verdict `FAMILY_AUDIT_COMPLETE` or `INCOMPLETE`.

### `capability-audit.yaml` schema

```yaml
schema: governance-os.phase-2.capability-audit
schema_version: 1
run_id: <P2-AR-NNNN>
family: <family>
candidate: cap2-candidate-0
candidate_commit: <full sha>
product_code_digest: bd4d65d9d5ffd6aedbd9435e2091a664dfc3e62f80614a76197cfaf87efd0547
capabilities:
  - capability: <ID, e.g. C3>
    title: <owner-source title>
    source_ref: Governance_OS_Capability_Acceptance_Contract_v3.md:<line>
    governing_document_refs: [<file §section>]
    requirement_class: <ORIGINAL | POST_VERIFICATION_HARDENING | EXECUTION_REFINEMENT>
    status: <PRESENT_AND_SUBSTANTIAL | PARTIAL | ABSENT | UNCLEAR | N/A_WITH_REASON>
    status_justification: <why>
    na_reason_normative_text: <quoted text or null>
    partial_qualification_impact: <for PARTIAL: CANNOT_UNDERMINE | COULD_UNDERMINE, with argument; else null>
    bullets:
      - bullet: <verbatim checklist text>
        source_line: <n>
        status: <status>
        implementation_evidence: [<path:line-range>]
        automated_evidence: [<test id / command / doctor or audit check id>]
        independent_evidence: [<evidence/file — what you ran and what it showed>]
        gap: <null or precise statement>
    health_scheduler_tiers: [<G0..G6>]
    evidence_owners: [<G0 | G1 | G2 | G3 | G4 | G5 | G6 | independent-heldout | human-gate | release-clean-clone>]
    evidence_owner_actually_runs: <true | false | partial — with explanation>
    freshness:
      state: <FRESH_FOR_CANDIDATE | STALE | NO_EVIDENCE>
      invalidation_inputs: [<input classes from Contract v3 lines 97-109>]
      invalidation_demonstrated: <true | false | not_attempted>
      invalidation_evidence: <path or null>
    qualification_coverage:
      repo_a_challenge: <text>
      repo_b_challenge: <text>
      hidden_oracle_fault_class: <text>
      chaos_scale_soak: <text or "not relevant: reason">
      retrieval_challenge: <text or "not relevant: reason">
      not_challengeable: <null, or reason + alternative independent evidence route>
    adoption_obligation: <what gov init/adopt/update/post-adoption must verify>
    residual_risk: <text>
    findings: [<finding ids>]
```

### `findings.yaml` schema

```yaml
schema: governance-os.phase-2.findings
schema_version: 1
run_id: <P2-AR-NNNN>
findings:
  - id: A0-<CAP>-<nn>            # e.g. A0-C3-01; unique because capability IDs are partitioned across families
    capability: [<ID>]
    bullet_source_lines: [<n>]
    severity: <CRITICAL | HIGH | MEDIUM | LOW | INFO>
    title: <one line>
    statement: <precise defect statement>
    normative_source: <file:line and quoted clause>
    provenance_class: <ORIGINAL-NORMATIVE | OWNER-ADDED-NORMATIVE | NECESSARY-DERIVED | IMPLEMENTATION-CHOICE | VERIFIER-HARDENING | NEW-OWNER-DECISION-REQUIRED | LATER-QUALIFICATION/CERTIFICATION | OUT-OF-SCOPE / UNSATISFIABLE-AS-STATED>
    lifecycle: <P2 | P3 | P4 | R2 | R3 | adoption | operations>
    falsifies_or_proposes: <FALSIFIES_PHASE2_REQUIREMENT | PROPOSES_STRONGER_LATER_ASSURANCE>
    blocks_acceptance_criteria: [<AC-n>]      # empty if non-blocking
    blocking: <true | false>
    evidence: [<evidence/ paths>]
    reproduction: <exact commands>
    repair_direction: <what closing it would require, stated as a requirement, not a design>
    owner_decision_required: <true | false>
    owner_decision_reason: <null, or why an agent cannot legitimately decide it: new product requirement, security/availability/usability/cost trade-off, architecture-boundary change, normative conflict, owner-controlled material>
```

`repair_direction` states **what** must become true, citing the source, not how to build it. If closing a gap would
require a choice the accepted sources do not make (for example selecting a network-downloaded model, adding a new
external dependency class, changing a trust boundary, or trading availability/cost/usability), set
`owner_decision_required: true` and say exactly which choice.

## Commit and report

Work in the worktree you are given, on the branch you are given. Commit your evidence directory first (message
`P2-AR-NNNN iteration-0 audit <family>: …`). Then write your run report with that commit's hash in `output.commit` and
commit the report separately. Do not merge, rebase, tag or push. Do not touch any other branch or worktree.

## Prohibitions

- No product-source modification of any kind, including tests, fixtures, schemas, policies, docs and `Cargo.*`.
- No edit to anything under `release/verification/`, `release/root-of-trust/`, `release/releases/`,
  `release/orchestration/phase-1/`, or another family's evidence directory.
- Do not read, list or search session or agent transcripts, task-output stores (`/tmp/claude-*/**/tasks/`) or user
  auto-memory (`~/.claude/projects/**/memory/`). Do not write anything to user auto-memory.
- Do not contact the product owner. If you hit a genuine STOP (a pinned identity does not verify), write that in your
  report with verdict `INCOMPLETE` and stop.
- Do not spawn sub-agents. Every command you rely on, you run yourself.
