# Decision and architecture records (canonical repository)

The canonical repository governs itself with the same record types it ships. Authoritative records live under
`spec/`; this page is a narrative index only.

| Record | Status | Summary |
|---|---|---|
| [PRJ-0001](../spec/product/PRJ-0001.yaml) | ACTIVE | Governance OS canonical source product: mission, outcomes, actors |
| [D-0001](../spec/decisions/D-0001.yaml) | SUPERSEDED | Python reference implementation (superseded the same day) |
| [D-0002](../spec/decisions/D-0002.yaml) | ACTIVE (human-approved) | Rust-first deterministic core, polyglot capability ecosystem |
| [CIT-0001](../spec/decisions/CIT-0001.yaml) | COMMITTED | Transaction applying D-0002 (pivot, plugin protocol, DAG update) |
| [ARCH-0001](../spec/architecture/ARCH-0001.yaml) | ACTIVE | Layered implementation architecture and coupling rules |
| [API-0001](../spec/interfaces/API-0001.yaml) | ACTIVE (1.2) | Capability Plugin Protocol v1 (`gov-capability/1`); 1.2 (D-0010): every executable plugin needs a registration approved for exactly it |
| [API-0002](../spec/interfaces/API-0002.yaml) | ACTIVE | `gov` CLI machine contract (JSON envelope, exit codes) |
| [D-0003](../spec/decisions/D-0003.yaml) | ACTIVE | Every kernel policy key is executable or explicitly informational (ENFORCEMENT_MAP, `policy_enforcement_coverage`) |
| [D-0004](../spec/decisions/D-0004.yaml) | ACTIVE | MCP transport deferred with a record; lesson clustering → Framework Change Proposal records |
| [D-0005](../spec/decisions/D-0005.yaml) | ACTIVE | Embed/rerank plugins fail closed, code_intel degrades; plugins are governed executables (API-0001 v1.1) |
| [D-0006](../spec/decisions/D-0006.yaml) | ACTIVE | No paraphrase model in the kernel; per-repository benchmark/selection, optional plugin template, candidate classes |
| [D-0007](../spec/decisions/D-0007.yaml) | ACTIVE | Trust classes: a lower-trust input may never manufacture a higher-trust fact (kernel trust root, plugin registry, governed exceptions) |
| [D-0008](../spec/decisions/D-0008.yaml) | **PROVISIONAL / not active; CP-1 retired as the Phase-1 target by D-0009** | Historical proposed RoT-1 revision-7/CP-1 decision, preserved unchanged as high-assurance research evidence; never owner-activated and not routed to Revision 8 |
| [ARCH-0002](../spec/architecture/ARCH-0002.yaml) | **PROVISIONAL / not active; historical CP-1 proposal** | Historical RoT-1 revision-7 architecture companion to D-0008, retained unchanged as research evidence |
| [D-0009](../spec/decisions/D-0009.yaml) | **ACTIVE (human-approved)** | Adopt a separate compact TUF-style Signed Release Root with trusted platform/admin bootstrap and frozen R0/R1/R2/R3 assurance separation; keep D-0007 active during transition |
| [ARCH-0003](../spec/architecture/ARCH-0003.yaml) | **ACTIVE (human-approved, owner-adopted by OWNER-DECISION-0009); R0 and R1 independently accepted** | Signed Release Root v1: standard signed metadata, uniform lifecycle verifier, verified-byte atomic install, local high-water and separate installed-kernel integrity. Implemented by `srr1-r1-candidate-4` (tag `srr1-r1-accepted`). Not R2-certified or released. Does not supersede ARCH-0001 or amend D-0007. |
| [D-0010](../spec/decisions/D-0010.yaml) | ACTIVE (orchestrator, delegated; owner may supersede) | Amends D-0005 consequence 3 to conform with Contract v3 F4 / ARCH-0003 §9: only the OS's own capability server runs hand-declared; every executable plugin runs only with a registration approved by a gate raised for exactly it (D-0005's text unchanged) |
| [TASK-0001 … TASK-0012](../spec/tasks/) | see records | Implementation workstreams (DAG); TASK-0010/0011/0012 = repair iterations for candidates 4.1.3/4.1.4/4.1.5 |
| [RPT-0010](../spec/reports/RPT-0010.yaml) | EVIDENCE | Closing report of the first repair iteration |
| [RPT-0011](../spec/reports/RPT-0011.yaml) | EVIDENCE | Closing report of the second repair iteration (4.1.4) |
| [RPT-0012](../spec/reports/RPT-0012.yaml) | EVIDENCE | Closing report of the third repair iteration (4.1.5) |
| [RPT-0001](../spec/reports/RPT-0001.yaml) | EVIDENCE | Assessment of the implementation against D-0002 |
