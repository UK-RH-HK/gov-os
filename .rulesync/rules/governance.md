---
root: true
targets: ["claudecode", "agentsmd"]
description: "Gov OS governance rules"
---

# Governance

This project uses the Gov OS governance framework. All changes follow the Contract and the decision register.

## Contract and decisions

The Contract (`governance/contract/`) defines the mandatory requirements and milestone reviews. The decision register (`governance/decisions/`) records every owner decision with its rationale and governing sources. No change to the kernel, policy or skills is made without evidence, independent review and owner approval (CAP-33).

## Roles

Six roles operate under the guard:

- **engineer** — implements one ticket until its acceptance tests pass.
- **independent-test-designer** — writes acceptance tests from KPIs before implementation.
- **independent-auditor** — audits finished work as a fresh, read-only session.
- **orchestrator** — coordinates the wave, starts workers and makes delegated decisions.
- **product-spec** — writes schemas, templates, skills, role files and documentation.
- **research** — runs experiments and leaves an evidence record.

Each role's permissions, tools and allowed paths are stated in its role file under `governance/kernel/roles/`.

## Guard

The guard enforces allowed paths, tool restrictions and permission classes at runtime. It refuses writes outside a ticket's scope, denies installs for non-orchestrator roles, and blocks access to held-out paths. The guard decides; role files state.

## Skills and methods

Kernel method skills (`governance/kernel/skills/`) define how work is done: planning, discovery, retrieval, checkpoint, change, audit, test design and adoption. Skills follow the Contract and the decision register; they grant no permissions on their own authority (CAP-24.b).

## Proposing changes

Changes follow the CIT-P/CIT-E workflow: evidence, corroboration, proposal, independent review, owner approval and versioned promotion (CAP-33). A contradiction against a closed specification presents three costed options: apply now, defer or re-baseline (DEC-105).
