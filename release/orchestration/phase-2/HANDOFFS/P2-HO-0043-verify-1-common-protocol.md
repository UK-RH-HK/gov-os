# P2-HO-0043 — Verification iteration 1: common protocol

Every iteration-1 verifier reads this file. Family verifiers also read `P2-HO-0044-verify-1-family-scopes.md`; the R1-preservation,
oracle-format and synthesis verifiers read their own handoffs (P2-HO-0045, -0046, -0047), which build on this one.

## Who you are

A **fresh, independent capability verifier** for Governance OS Phase 2, verification iteration 1. You authored none of the
Governance OS implementation, none of its tests, none of the iteration-0 audits, none of the repairs (P2-AR-0014…0043) and
no Phase-1 role. You are not the orchestrator. You do not repair anything. You **never modify product source**. You do not
issue the Phase-2 verdict unless you are the synthesis verifier.

## Pinned inputs (verify each before relying on it; a mismatch is a STOP)

| Input | Identity |
|---|---|
| Candidate | **`cap2-candidate-1`** — tag, commit, `product_code_digest` and `governed_state_digest` as given in your dispatch message and in `ORCHESTRATOR_STATE.yaml` `candidates`. Verify with `python3 release/orchestration/phase-2/tools/product_identity.py cap2-candidate-1` and `git rev-list -n1 cap2-candidate-1`. Your worktree is at a later orchestration commit whose product code and governed state are identical to the tag's — check both digests at `HEAD` too. |
| Contract v3 (owner source) | `Governance_OS_Capability_Acceptance_Contract_v3.md`, SHA-256 `4c2df29115c8d5389034b2e2d817772add80d61678807c23e0d520c937cb5ed3` |
| Frozen Phase-2 gate contract | `release/orchestration/phase-2/GATES/PHASE-2-FROZEN-GATE-CONTRACT.md`, SHA-256 `d2f33e89d5459dd809e17271e46854cc886ed958ca63f89765e16d6a26a9f25e` |
| Governing documents | the three `*.md` governing documents at the repository root |
| Decisions in force | `spec/decisions/`, `spec/architecture/` (ARCH-0003 owner-adopted), `spec/interfaces/`; Phase-1 owner records in `release/orchestration/phase-1/GATES/`; Phase-2 owner decisions `GATES/OWNER-DECISION-P2-0001-AGENT-ROLE-IDENTITY.md` (OD-P2-01 A: agent roles stay adapter-declared) and `GATES/OWNER-DECISION-P2-0002-UNPROVISIONED-MACHINES.md` (OD-P2-02 A: refuse external-source kernel ingress until provisioned); orchestrator adjudications `GATES/P2-ADJ-0001-*`, `P2-ADJ-0002-*`, `P2-ADJ-0003-*` (the owner may override them; you apply them as sources, and you may record a finding that one is wrong, with evidence) |

## The standard you apply

Everything in `P2-HO-0000-audit-0-common-protocol.md` ("The standard you apply", the schemas, "Commit and report",
"Prohibitions") and in `P2-HO-0009-audit-0-reaudit-common.md` ("The evidence standard, restated") applies unchanged. Read
both in full. Wherever they say `cap2-candidate-0`, `bd4d65d9…`, `audit-0` or "iteration-0", read `cap2-candidate-1`, its
digest, `verify-1` and "iteration 1". In addition:

1. **Full re-audit.** The product changed broadly across four repair rounds and three integrations, so every iteration-0
   status is stale. Establish every bullet of every capability you own afresh, on this candidate, with your own evidence.
2. **Held-out tests you author.** For each capability, write held-out tests of its behaviour — probes that drive
   `target/release/gov` (or the library through a small harness) against disposable projects — under
   `release/capability-baseline/verify-1/<scope>/heldout/`, with a `RUN-ALL` script that re-runs them all and prints one
   PASS/FAIL line per test. They are independent evidence: write them from the contract and the product's observable
   behaviour, not by copying builder tests or builder probes. They never enter the product tree.
3. **Builder claims are claims.** You may read the repair and integration reports under
   `release/capability-baseline/repair-1/**` to learn what is claimed, so that you can attack it. Nothing in them is
   evidence for you. Builder tests (`cargo test`) are regression evidence (O3).
4. **Iteration-0 inventory and convergence labels (frozen contract §8).** Inputs:
   `release/capability-baseline/audit-0/synthesis/{blocker-classes.yaml,findings.yaml,repair-delta.md}`. You may re-run the
   audits-of-record probes (`release/capability-baseline/audit-0/<family>-r/evidence/`) to check whether a prior finding is
   closed; do not adopt their statuses. Produce `prior-findings-disposition.yaml`: every iteration-0 finding in your scope
   → `CLOSED` (your evidence), `RESIDUAL` (still open or incompletely fixed; your evidence) or `NOT_APPLICABLE` (reason).
   Label every finding **you** raise `RESIDUAL` (same capability and same mechanism as an inventoried class — name the
   class) or `MATERIALLY_NEW` (a capability or mechanism absent from the inventory, including a regression a repair
   introduced into a previously held capability), with your reason. Label honestly; the orchestrator checks labels and
   never relabels.
5. **Probe preconditions** (P2-ADJ-0003): a probe that needs a green baseline builds one that is legitimately green under
   Contract v3. A vacuous pass is not a pass. A precondition the contract itself makes false is not a product defect.

## Attacks every verifier makes where their scope reaches them

- **Cross-machine continuity (P2-ADJ-0002).** Two machines of the same owner, both provisioned under ARCH-0003 §8
  (the product's test harness provisions a throw-away root; use the product's own provisioning commands): OS-written
  facts written on one must be honoured on the other; a record forged or edited by hand, a record from a foreign owner, an
  unprovisioned machine, a wrong signer, an expired or rolled-back authority must each be refused with a typed result;
  nothing secret is in any repository; `gov` verifies and never signs (SRR-R0-L4).
- **Availability rule** (Contract v3 L4 and O5; `P2-HO-0031-repair-1-round-3-common.md`): a block refuses only what it
  protects; its listed remedy stays available; independent work stays available; no block refuses its own remedy; every
  refusal is typed and names its scope. Attack each block your capabilities issue.
- **Trust classes** (D-0007; Contract v3 A2/F4/L3): no project, CLI, environment, model or plugin input manufactures a
  higher-trust fact, a role, or a human approval.
- **Freshness** (Contract v3 lines 95–111; AC-10): for each capability, change a relevant input and show whether prior green
  evidence goes stale.

## What you produce

Under `release/capability-baseline/verify-1/<scope>/` (your handoff names `<scope>`): `00-VERIFICATION-REPORT.md`,
`capability-audit.yaml` and `findings.yaml` (schemas of P2-HO-0000, with `candidate: cap2-candidate-1`; each finding adds
`new_vs_residual: RESIDUAL | MATERIALLY_NEW`, `inventoried_class: BC-P2-NN | null`, `label_reason`),
`prior-findings-disposition.yaml`, `heldout/` (with `RUN-ALL`), `evidence/`. Your run report
`release/orchestration/phase-2/AGENT_RUNS/<run-id>.report.yaml` records your actual model in `agent_model`; verdict
`FAMILY_VERIFICATION_COMPLETE` or `INCOMPLETE` (special roles: see their handoffs).

Commit your evidence directory first, then your run report with that commit's hash in `output.commit`, on the branch you
are given. Do not merge, rebase, tag or push.

## Prohibitions (in addition to P2-HO-0000's)

- Do not read another iteration-1 verifier's evidence directory or branch.
- Do not read, list or search session or agent transcripts, task-output stores (`/tmp/claude-*/**/tasks/`) or user
  auto-memory. Do not spawn sub-agents. Do not contact the product owner.
- `rm` is denied in this environment; do not retry it — move files aside and say so.
- `export CARGO_BUILD_JOBS=2`. Build in your own worktree's `target/`.
