# OWNER-DECISION-P2-0003 — A tool installation needs the human gate only when it expands authority

| Field | Value |
|---|---|
| Record | Owner decision (product owner, 2026-09-20), answering owner gate **HG-P2-0002** |
| Raised by | P2-AR-0053 (round-4 residual continuation), item R4-O1, verdict `OWNER_DECISION_REQUIRED` |
| Decision id | **OD-P2-03**, option **"gate only elevated installs"** |
| Status | IN FORCE for Phase 2 and later phases until the owner changes it |

## The question put to the owner

A tool descriptor write (`governance/project/tools/<id>.yaml`, written only by `tools::install`) is a material governance
and security change, so Contract v3 K3 auto-triggers impact simulation for it. Three accepted things could not all hold:

- **K3 + the product's materiality classification** ⇒ an installation is change-controlled;
- the shipped **`framework/policies/CHANGE_POLICY.yaml`** lists `governance_change` in `human_gate_triggers` ⇒ that change
  transaction needs a human gate;
- **IP-W7-1 / BC-P2-41**, built by WS-7 in round 3, lets an installation evidenced by a governed security review from an
  independent role proceed **without the owner's gate** (`ws07::a_governed_security_review_by_another_role_lets_the_installation_proceed`
  asserts no gate is raised), and **`framework/policies/TOOL_POLICY.yaml`** declares `auto_install_conditions` for that case.

Contract v3 F3 requires a "security/licence/maintenance/cost review" and "approval **when required**", leaving *when* to
policy; the owner owns that policy. So this was a genuine owner decision, not an orchestrator adjudication.

## The decision, in the owner's terms

**Gate only elevated installs.** Normal tool acquisition may proceed **without** a Human Gate when the tool is:

- **authenticated and pinned**;
- **independently governed-reviewed**;
- **registered**;
- **reversible**;
- and **operates entirely within the project's already-authorised permission and trust envelope**.

A **Human Gate is required** when the installation **expands authority**, including:

- privilege escalation;
- broader filesystem or project access;
- new secret or credential access;
- host-level authority;
- governance or security-policy mutation;
- a new or unrestricted network trust boundary.

**Ordinary network use already authorised by project or tool policy** — approved registries, allowlisted services — **does
not by itself count as elevated permission**.

**Every installation is recorded** with its security and CIT evidence, whether or not a Human Gate was required.

## What this requires of the implementation (requirements, not a design)

1. **An explicit, governed rule** in policy (`CHANGE_POLICY`, with `TOOL_POLICY` supplying the authorised envelope) naming
   the tool-installation change class, the non-gated conditions and the authority-expansion triggers above, plus a governed
   decision record referencing this one. It must be visible to `gov` policy inspection and to an auditor, never implicit in
   code.
2. **The authorised envelope is computed from trusted OS state, never from the descriptor's own declarations** (Contract v3
   F4 "descriptor cannot authorise itself"; BC-P2-39's defect). The comparison is: the permissions, filesystem/project
   scope, secret access, host authority, policy-mutation capability and network trust boundary the tool would hold, against
   what the project has already authorised (`TOOL_PERMISSIONS`, `AUTHORITY_POLICY`, `DATA_SENSITIVITY`, the path map and the
   tool policy's allowlists). Anything outside that envelope is an expansion and gates.
3. **Fail closed and fail gated.** If the envelope cannot be determined, a condition cannot be evaluated, the review is
   missing, self-attested or not bound to this exact installation (BC-P2-41), or the pin/hash cannot be verified, the Human
   Gate is required and the installation does not proceed.
4. **Contract v3 F4's "elevated permissions reference authoritative gate/decision" still binds** — and under this decision
   elevated permissions are exactly the gated class, so they reference an actual gate. Non-elevated installations reference
   this decision, the governed rule and the bound independent review in their recorded change transaction, so an auditor can
   trace any installed tool to what allowed it.
5. **Recording is unconditional**: the change transaction (impact simulation, radius, propagation) and the security review
   evidence are recorded for every installation, gated or not, and the recorded transaction states which branch applied and
   why.
6. **Round-3 behaviour is restored for the non-elevated case**:
   `ws07::a_governed_security_review_by_another_role_lets_the_installation_proceed` goes back to asserting that no gate is
   raised, with its tool inside the authorised envelope. P2-AR-0053's commit `ab0a075`, which implemented "always gate", is
   superseded: keep its change-control machinery where it serves K3 (the OS-proposed transaction, the CIT-E writer, the §6
   acquisition sink at the instant of the write, the installation-authority checks), drop its unconditional gating and its
   edit to that test.
7. **Tests must cover both branches**: a non-elevated install closing with no gate, and an install gated for each
   authority-expansion trigger above — including one showing that ordinary allowlisted network use alone does not gate.

## Consequences the owner accepted

- A tool that stays inside the project's existing authority can enter the trusted surface without the owner seeing it,
  on the strength of an independent review, pinning, registration and reversibility.
- Authority expansion always stops for the owner.
- A verifier may still find the implementation of this decision insufficient against a Contract v3 requirement; that is a
  finding against the implementation, not a re-opening of the decision. The owner may override at any time.
