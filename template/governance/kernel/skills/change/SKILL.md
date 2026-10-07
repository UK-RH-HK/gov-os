---
name: change
description: Method for taking a Gov OS change through evidence, proposal, independent review and owner approval to a new version.
version: "1.0.0"
---
# Change

This skill describes how to propose and promote changes to the Gov OS kernel, policy and skills. It follows the Contract and the decision register; it does not grant permissions or set rules on its own authority.

## Skill change lifecycle

Per CAP-24.c, a change to a skill follows these steps in order:

1. **Evidence**: gather evidence that the change is needed — experiment results, incident records or specification analysis (CAP-24.c).
2. **Proposal**: draft a change proposal describing what changes, why and the expected impact (CAP-24.c).
3. **Independent review**: an independent reviewer examines the proposal for correctness and side-effects (CAP-24.c).
4. **Owner approval**: the owner accepts, requests changes or rejects the proposal (CAP-24.c).
5. **Version**: on approval, the skill's frontmatter version is incremented and the change is committed (CAP-24.c).

## CIT-P and CIT-E

Per CAP-33.a (CAP-33.d), a change to the Gov OS kernel, policy or skills follows the full change-integration workflow:

1. **Evidence**: the practitioner collects evidence (experiment results, findings, incident data) (CAP-33.a).
2. **Corroboration**: a second source or method confirms the evidence (CAP-33.a, CAP-33.d).
3. **Proposal (CIT-P)**: an OpenSpec proposal is drafted via `gov closure`, listing what changes, the evidence and the corroboration (CAP-33.a).
4. **Independent review**: a reviewer who did not author the proposal examines it (CAP-33.d).
5. **Owner approval**: the owner decides whether to accept the proposal (CAP-33.d).
6. **Versioned promotion**: on acceptance, the changed artefact receives a new version and is committed (CAP-33.d).

A CIT-E records what was done after the owner's decision. Per CAP-33.d, a CIT-E that attempts to archive a kernel change without the required evidence, corroboration, independent review and owner approval records is refused.

## Three costed options on contradiction

Per DEC-105 (CAP-33.e), when an experiment or finding contradicts a closed specification, the change skill opens a CIT-P whose impact assessment lists the affected specifications, decisions, tickets, tests and code. The CIT-P presents three costed options:

1. **Apply now**: adopt the change immediately; CIT-E records the update (DEC-105, CAP-33.e).
2. **Defer**: schedule the change for a later wave; CIT-E records the deferral and the reason (DEC-105).
3. **Re-baseline**: revise the specification to match current reality; CIT-E records the new baseline (DEC-105, CAP-33.e).

The owner chooses among these options. CIT-E records what was done. Every version of the specification is kept (DEC-105, CAP-33.e).

## Impact assessment

Per DEC-167 (CAP-33.f), a question of the form "what is the impact of X?" triggers the impact assessment. In Wave 1, the method is:

1. Draft an OpenSpec proposal describing the change (DEC-167, CAP-33.f).
2. Run `gov closure` over the affected records to identify downstream specifications, decisions, tickets, tests and code (DEC-167).
3. Present the impact summary to the requester (CAP-33.f).

## Audit ticket

Per DEC-088 (CAP-47.d), an accepted CIT-E that changes a closed spine creates an audit ticket. The audit ticket assigns a fresh independent auditor to verify that the change followed the full CIT-P/CIT-E workflow and that every version of the affected artefact is kept (DEC-088, CAP-47.d).

## Tools

CIT-P and CIT-E use OpenSpec (installed, v1.13.2) for drafting proposals and recording outcomes (CAP-33.a). Run `gov closure` to compute the downstream impact of a proposed change (DEC-167, CAP-33.f). Run `gov status` to check the current state of a CIT-P or CIT-E (CAP-33.d).
