# Fixture 7 — Failure injection

Starting from a healthy `gov init` project, the harness injects faults one at a time and asserts detection by
`gov doctor` / the governance suite and repair by the recovery primitives:

| Injection | Detection | Repair |
|---|---|---|
| Corrupt `state.db` | D009 (high) | `gov recover` rebuilds the runtime |
| Interrupted CIT (status EXECUTING with snapshot, file half-changed) | D016 (high) | `gov recover` rolls back; file restored |
| Stale index (record edited after build) | D010 | `gov rebuild-memory --incremental`; `task close` refuses (`INDEX_STALE`) |
| Expired claim | D017 | `gov claims sweep` |
| Freeze left on | D018; mutations refused (`FROZEN`) | `gov resume` |
| Kernel tampered in place | D003 critical; suite `mutation_scope` critical | `gov kernel reinstall` |
| Invalid policy override | D007 | fix overlay |
| Secret planted in product source | D011 critical; file excluded from index; no chunk contains it | move to secret-class path |
| Task depending on a missing task | `graph_integrity` finding; DAG blocked with reason | fix dependency |
| Missing overlay file | D006 | restore file |
| Failing embed plugin | rebuild degrades to builtin, degradation recorded, no crash | — |
| Gate answered without presentation | `GATE_NOT_PRESENTED` (INV-008) | `gov gate present` |
