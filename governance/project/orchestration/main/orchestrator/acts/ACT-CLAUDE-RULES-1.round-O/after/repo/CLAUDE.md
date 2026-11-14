# Governance

This project uses the Gov OS governance framework. All changes follow the Contract and the decision register.

## Contract and decisions

The Contract (`docs/contract/`) defines the mandatory requirements and milestone reviews. The decision register (`docs/DECISION_REGISTER.md`) records every owner decision with its rationale and governing sources. No change to the kernel, policy or skills is made without evidence, independent review and owner approval (CAP-33).

## Roles

Seven kinds of session operate under the guard: six roles and the ticket lead.

- **engineer** — implements one ticket until its acceptance tests pass.
- **independent-test-designer** — writes acceptance tests from KPIs before implementation.
- **independent-auditor** — audits finished work as a fresh, read-only session.
- **orchestrator** — coordinates the wave, starts workers and makes delegated decisions.
- **product-spec** — writes schemas, templates, skills, role files and documentation.
- **research** — runs experiments and leaves an evidence record.
- **ticket lead** — an orchestrator session in one ticket's worktree: runs that ticket's loop, starts its workers, verifies, and returns to the orchestrator; it never merges.

Each role's permissions, tools and allowed paths are stated in its role file under `template/governance/kernel/roles/` (generated as `.claude/agents/`). Wave 2's working rules are in `governance/project/prompts/w2-orchestrator.md` and `governance/project/briefs/`; the orchestration record is in `governance/project/orchestration/` (DEC-819).

## Guard

Here, since DEC-953 item 2, the live hook (`.claude/hooks/pretooluse.py`) keeps five rules: only the independent test designer writes acceptance tests; the held-out material and the hidden half of an evaluation set are not read; independent reviewers and auditors write only their own outcomes; secrets and keys are not read; and an install asks the owner in the CTO's own session and is refused in every other. It also refuses the catastrophic deletes and applies the path map's role separation. It has no rule that keeps a worker's writes inside its ticket's paths: a launched worker's writes outside its worktree are walled by the OS sandbox of `gov launch` (SANDBOX-1, DEC-1128 (4)), not by the hook. In an adopted product the kernel guard enforces allowed paths, tool restrictions and permission classes at runtime. Reads are open; only secrets, the held-out material's contents, the counterpart's work on the same ticket and the hidden half of an evaluation set are refused (DEC-820). The guard decides; role files state.

## Skills and methods

Kernel method skills (`template/governance/kernel/skills/`, generated as `.claude/skills/`) define how work is done: planning, discovery, retrieval, checkpoint, change, audit, test design and adoption. Skills follow the Contract and the decision register; they grant no permissions on their own authority (CAP-24.b).

## Proposing changes

Changes follow the CIT-P/CIT-E workflow: evidence, corroboration, proposal, independent review, owner approval and versioned promotion (CAP-33). A contradiction against a closed specification presents three costed options: apply now, defer or re-baseline (DEC-105).
