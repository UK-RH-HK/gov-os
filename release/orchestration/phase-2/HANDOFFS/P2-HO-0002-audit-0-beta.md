# P2-HO-0002 — Iteration-0 capability family audit: `beta`

| Field | Value |
|---|---|
| Handoff | P2-HO-0002 |
| From | Phase-2 orchestrator (routing only) |
| To | fresh independent `capability-family-auditor`, run **P2-AR-0002** |
| Candidate | `cap2-candidate-0` (see common protocol for the pinned identities) |
| Active gate | `GATE-P2-BASELINE-AUDIT-0` under `GATE-P2-CAPABILITY-BASELINE-ACCEPT` |
| Family | `beta` |
| Capabilities owned | C (C1–C10), D (D1–D6), R (R1–R3) — Development Knowledge Fabric, indexing/retrieval/context, legacy/archive/history |
| Owner-source location | Contract v3 lines 207–357 (Gates C, D) and 870–891 (Gate R) |
| Evidence directory | `release/capability-baseline/audit-0/beta/` |
| Run report | `release/orchestration/phase-2/AGENT_RUNS/P2-AR-0002.report.yaml` |
| Required verdict | `FAMILY_AUDIT_COMPLETE` or `INCOMPLETE` |

**First read `release/orchestration/phase-2/HANDOFFS/P2-HO-0000-audit-0-common-protocol.md` in full.** It defines who you
are, the standard you apply, the output schemas and the prohibitions. This handoff only scopes your family.

## Your capabilities

C (C1–C10), D (D1–D6), R (R1–R3) — Development Knowledge Fabric, indexing/retrieval/context, legacy/archive/history. Establish the exact capability and bullet set yourself from the owner source at the lines above — not from the
compiled YAML or the evidence map, which are derived views (frozen contract §1). If you find that a derived view omits
or distorts anything in your scope, that is itself a finding.

## Governing-document trace

framework Part IV §§10–19 (memory architecture, the ten memory classes, databases, incremental indexing, retrieval routing, hierarchical retrieval, embeddings vs runtimes vs LLMs, evidence-driven model selection, context packet, memory security, memory regression tests, retrieval learning loop, rebuild guarantee), Part XX §§69–70 and Part XXI §71; decisions D-0005, D-0006 and research RES-0001.

## Where the implementation starts (orientation only — find the rest yourself)

`runtime/src/memory/` (db, indexer, chunking, embedder, embeddings, benchmark, heldout, claims, manifest), `retrieval/`, `graph/`, `code_intelligence/`, `context/`, `lessons.rs`, `capabilities/` (embed/rerank plugins), `adopt.rs` (legacy extraction), `framework/policies/` (MEMORY/CONTEXT/ARCHIVE policies); `capabilities/python`, `capabilities/shell`; `fixtures/multi-machine`, `fixtures/brownfield`; `tests/certification/`.

These are starting points, not conclusions. A module's existence says nothing about whether a bullet is met.

## Family-specific duties

- **AC-7 (frozen contract §9.1).** Establish, with executable evidence, whether the candidate provides a path to a
  non-intentionally-inadequate provisional retrieval profile: separately identifiable/replaceable embedder, runtime,
  reranker, stores and router (D4); benchmark/compare/select/pin with golden or held-out queries and Recall@K/MRR/precision/
  stale-hit/latency/resource metrics (D5); governed reindex/regression on profile change. Record your AC-7 determination
  explicitly in `00-AUDIT-REPORT.md`. You do **not** select a profile — that is Phase 3.
- **C1** lists seventeen record kinds and **C3/C4/C5/C6/C7/C8** each list their own facets: every facet is a bullet.
- **D6 rebuild guarantee**: actually delete derived state and rebuild; compare authoritative state and claims before/after;
  run a fresh-agent reconstruction (`gov status`) after rebuild; if you can, rebuild at a different absolute path and compare.
- Cross-capability interactions you own (AC-16): K2 ↔ D1 (CIT-E triggers index refresh), D1 ↔ W6 (index staleness).
  Coordinate nothing with other auditors; just exercise what touches your capabilities.

## Five other families are auditing in parallel

Other fresh auditors own the other gates. Do not audit their capabilities, and do not read their evidence directories
(they are on other branches and are not merged). A separate fresh synthesis auditor assembles all six families, checks the
cross-cutting criteria (AC-9, AC-10, AC-11, AC-13, AC-14, AC-15, AC-16) and issues the Phase-2 verdict.
