# Additional Conventions Beyond the Built-in Functions

As this project's AI coding tool, you must follow the additional conventions below, in addition to the built-in functions.

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

Here the live hook (`.claude/hooks/pretooluse.py`) keeps five rules (DEC-953 item 2, and DEC-954 for the fifth): only the independent test designer writes acceptance tests; the held-out material is not read, nor the hidden half of an evaluation set by the sessions it measures, and the sets root's hidden folders are neither read nor written by the roles the path map refuses them; independent reviewers and auditors write only their own outcomes; secrets and keys are not read; and an install asks the owner in the CTO's own session and is refused in every other, while sudo is refused to every session. It also refuses the catastrophic deletes; refuses every session's writes into the operator agent's folder (but its queue/) and into the guard's call log; refuses named sessions reads and writes of the folders the path map walls off for them (the engineer on W2-56: the raw transcripts); and applies the path map's role separation to reads. Its write rules judge a Bash line by the writes the guard resolves from it (`.claude/hooks/bash_writes.py`): a write whose target it cannot work out is let through, and for the acceptance-test and reviewer rules the backstops are the landing's check of acceptance-test commits and the reviewed tree's git status. It has no rule that keeps a worker's writes inside its ticket's paths: a launched worker's writes outside its worktree are walled by the OS sandbox of `gov launch` (SANDBOX-1, DEC-1128 (4)), not by the hook. In an adopted product the kernel guard enforces allowed paths, tool restrictions and permission classes at runtime. Reads are open; only secrets, the held-out material's contents, the counterpart's work on the same ticket and the hidden half of an evaluation set are refused (DEC-820). The guard decides; role files state.

## Skills and methods

Kernel method skills (`template/governance/kernel/skills/`, generated as `.claude/skills/`) define how work is done: planning, discovery, retrieval, checkpoint, change, audit, test design and adoption. Skills follow the Contract and the decision register; they grant no permissions on their own authority (CAP-24.b).

## Golden rule: how work is judged (DEC-1204)

Every review, audit, probe, QA check and moderation judges work by one standing rule (DEC-1204; it merges ADR-0001 / DEC-039, DEC-801 and DEC-1010 item 1):

- **Threat model:** honest agent mistakes, plausible accidents and drift in ordinary work, not a same-privilege adversary; the hard boundary is git history, protected-branch CI and the owner's signed approvals.
- **What may block:** only a finding within the change's scope that an honest agent can hit in ordinary work and that fails open or loses work. A finding that needs a deliberate construction (decoys, booby-traps, planted links, hand-set git environment or replace refs, chained escapes) is a Wave 3 row, never a new round.
- **How reviews converge:** a moderator triages every finding against the change's scope; at most two rounds, then the owner once with options; no extra round on its own; READY is computed by code from each reviewer's structured verdict.
- **Scope:** every review, the ACTs, the job runner and the box included.
- **Every brief carries it:** each reviewer, auditor, probe, QA and moderator brief states this rule: by the kernel skill `judging-work`, put in by `gov brief`, once it lands; by hand until then.

## Proposing changes

Changes follow the CIT-P/CIT-E workflow: evidence, corroboration, proposal, independent review, owner approval and versioned promotion (CAP-33). A contradiction against a closed specification presents three costed options: apply now, defer or re-baseline (DEC-105).
