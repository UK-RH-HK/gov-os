# agentic-engineering-os 4.1.2 — release notes (release candidate)

First software release of the Governance OS implementing the Dynamic Agentic Software Engineering Operating
Framework v4.1 (revision 4.1.2), the Release/Distribution/Adoption/Upstream-Learning Protocol v1.2 and the
Adoption/Migration/Independent-Audit Protocol v3.0.

## Contents
- Kernel payload: constitution + 15 machine-readable hard invariants, 13 policies, 59 JSON Schemas, 12 skills,
  5 adapters (generic, ide, cli, api, mcp), roles/authority levels, capability taxonomy, 26 readiness dimensions,
  command contract with intent patterns, 7 overlay templates, tool + MCP registries, declarative migration
  M-4.1.1-4.1.2.
- Rust deterministic core (`gov-runtime`) and `gov` CLI (D-0002): kernel/lock/overlay/policy enforcement,
  repository contract, Development Knowledge Fabric (SQLite/FTS5, built-in embedder, graph, code intelligence,
  retrieval router, context compiler, manifests, held-out regression), tasks/DAG/claims/gates/control, checkpoints,
  CIT-P/CIT-E with snapshots, doctor (24 checks), governance suite (17 families) + audit records, init, adopt A0–A11,
  update/rollback, release build/verify, upstream export gate, recovery, tool/MCP registry, model routing, telemetry.
- Capability plugin protocol `gov-capability/1` with Python (python-ast code intelligence, reference embedder) and
  shell plugins.
- Seven synthetic certification fixtures and an implementer certification harness.

## Supported migration paths
- 4.1.1 → 4.1.2 via `M-4.1.1-4.1.2` (non-breaking; overlay key rename `human_gates`→`gates`, new
  `PROJECT_EXCEPTIONS.yaml`, lock schema version, full index rebuild).

## Known limits (honest scope)
- The repository-intelligence MCP server (MCP-REPO-001) is registered as planned; the same operations are exposed
  through the CLI JSON contract.
- Upstream submission supports local destinations (a clone of the canonical repository); remote transports are
  refused with `REMOTE_TRANSPORT_NOT_CONFIGURED`.
- The built-in embedder is a deterministic lexical baseline; stronger embedders/rerankers are plugged in via
  API-0001 and pinned per repository after a measured benchmark.
- Dead-code classification is heuristic (import graph); removal always requires an answered human gate.

## Certification
Implementer tests and evidence only. Status: READY_FOR_INDEPENDENT_OS_VERIFICATION (not certified).
