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
| [API-0001](../spec/interfaces/API-0001.yaml) | ACTIVE | Capability Plugin Protocol v1 (`gov-capability/1`) |
| [API-0002](../spec/interfaces/API-0002.yaml) | ACTIVE | `gov` CLI machine contract (JSON envelope, exit codes) |
| [D-0003](../spec/decisions/D-0003.yaml) | ACTIVE | Every kernel policy key is executable or explicitly informational (ENFORCEMENT_MAP, `policy_enforcement_coverage`) |
| [D-0004](../spec/decisions/D-0004.yaml) | ACTIVE | MCP transport deferred with a record; lesson clustering → Framework Change Proposal records |
| [D-0005](../spec/decisions/D-0005.yaml) | ACTIVE | Embed/rerank plugins fail closed, code_intel degrades; plugins are governed executables (API-0001 v1.1) |
| [D-0006](../spec/decisions/D-0006.yaml) | ACTIVE | No paraphrase model in the kernel; per-repository benchmark/selection, optional plugin template, candidate classes |
| [D-0007](../spec/decisions/D-0007.yaml) | ACTIVE | Trust classes: a lower-trust input may never manufacture a higher-trust fact (kernel trust root, plugin registry, governed exceptions) |
| [D-0008](../spec/decisions/D-0008.yaml) | **PROPOSED (revision 7) — pending fresh independent reviews and the owner approval gate; not active, not approved** (record status field PROVISIONAL, the nearest schema value; human_approved false; in_effect false) | Proposed root of trust RoT-1 revision 7: one certified production profile CP-1 applying the product owner's binding design requirements OWNER-DESIGN-REQUIREMENTS-0001 (OP-1…OP-16, first-contact composer/signer at root threshold, derived build-environment manifests, initial certified scope) with every unselected mode excluded; rule FD-1 over a register complete over every input value; would supersede D-0007 only after independent acceptance and owner ratification (D-0007 stays ACTIVE) |
| [ARCH-0002](../spec/architecture/ARCH-0002.yaml) | **PROPOSED (revision 7) — pending D-0008 review and approval; not active** (record status field PROVISIONAL) | Proposed root-of-trust architecture companion to D-0008 (revision 7, certified profile CP-1) |
| [TASK-0001 … TASK-0012](../spec/tasks/) | see records | Implementation workstreams (DAG); TASK-0010/0011/0012 = repair iterations for candidates 4.1.3/4.1.4/4.1.5 |
| [RPT-0010](../spec/reports/RPT-0010.yaml) | EVIDENCE | Closing report of the first repair iteration |
| [RPT-0011](../spec/reports/RPT-0011.yaml) | EVIDENCE | Closing report of the second repair iteration (4.1.4) |
| [RPT-0012](../spec/reports/RPT-0012.yaml) | EVIDENCE | Closing report of the third repair iteration (4.1.5) |
| [RPT-0001](../spec/reports/RPT-0001.yaml) | EVIDENCE | Assessment of the implementation against D-0002 |
