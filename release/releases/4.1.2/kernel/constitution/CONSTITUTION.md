# Governance OS Constitution

**Kernel:** agentic-engineering-os 4.1.2
**Source framework:** Dynamic Agentic Software Engineering Operating Framework v4.1 (revision 4.1.2)

This constitution is the highest-precedence governance artefact installed in a consumer repository.
It is model-agnostic: no clause depends on a vendor, model, IDE or harness name.
Machine-readable hard invariants live in `HARD_INVARIANTS.yaml` next to this file; each invariant carries an
`INV-*` identifier that adapters must reproduce verbatim.

## Core principle

The agent session is not the source of truth. The governed project system is the source of truth.

## Article 1 — Continuity belongs to the organisation

Agent conversations are disposable. No essential project knowledge may exist only inside a conversation.
Material knowledge is committed into structured project state (decision, requirement, research finding,
experiment, task, report, lesson, skill, test, scenario, interface contract or change transaction).

## Article 2 — Authority precedence

When information conflicts, apply, in order: (1) explicit current human-approved decision; (2) current
constitutional hard invariant; (3) active structured project state; (4) active specification and interface
contract; (5) active architecture/workflow decision; (6) approved task contract and mutation manifest;
(7) active scenario and acceptance criteria; (8) current verified implementation behaviour; (9) current
research evidence and execution reports; (10) historical/superseded records; (11) semantic memory retrieval;
(12) agent inference. Retrieval can locate evidence; it cannot make something authoritative.

## Article 3 — State classes and lifecycle

Every material artefact is classified as AUTHORITATIVE, DERIVED, NARRATIVE, EVIDENCE, HISTORICAL or
UNKNOWN_OR_CONFLICTING and carries a lifecycle status (ACTIVE, PROVISIONAL, SUPERSEDED, LEGACY, HISTORICAL,
REJECTED, DEPRECATED, RETIRED). LEGACY material has no default authority.

## Article 4 — Model agnosticism

The constitution and policies are canonical. Provider, IDE, CLI and API instruction files are generated
adapters. No canonical policy, skill, task or decision may permanently depend on a model or vendor name.

## Article 5 — Controlled self-improvement

An executing agent must not rewrite the rules governing its own execution. Framework, policy and skill
changes pass evidence → corroboration → proposal → independent review/test → human approval where material →
versioned promotion.

## Article 6 — Kernel and overlay

`governance/kernel/` is the immutable installed release payload pinned by `governance/framework.lock`.
`governance/project/` is the project-owned overlay. Agents never edit the kernel inside a product repository;
improvements travel upstream as sanitised framework lessons and return through `gov update`.

## Article 7 — Human decision gates

A Human Decision Gate that exists only in a file is not considered presented. It must be surfaced in the
active human interface, and independent runnable work continues while it is pending.

## Article 8 — Security boundaries

Secrets, credentials, unapproved customer material, production personal data and restricted legal or security
material are never indexed into generic semantic memory and never leave the repository through the upstream
export gate.

## Article 9 — Rebuildable memory

The Git repository is the authoritative physical record. SQLite, vector, graph, lexical and code indexes are
derived and must be rebuildable from Git plus authoritative records without loss of project truth.

## Article 10 — Change control

Every accepted material state change is a Change-Impact Transaction: simulated (CIT-P) before approval and
executed atomically (CIT-E) with rollback after approval.
