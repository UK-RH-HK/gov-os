# First verifier harness (4.1.2) — implementer rerun for candidate 4.1.4

Harness `release/verification/4.1.2/heldout/harness.py` executed **unchanged** (byte-identical to the verifier's commit) with `GOV_VERIFIER_OUT` pointing here; the verifier's original results are untouched.

| Verdict | Verifier run | Rerun (4.1.4) |
|---|---|---|
| PASS | 12 | 36 |
| FAIL | 25 | 1 |
| INFO | 1 | 1 |
| ERROR | 0 | 0 |

| ID | Original | Rerun | Severity (rerun) | Title |
|---|---|---|---|---|
| HV-01 | FAIL | PASS |  | embedding model replaceable at query time: index built by the pinned plugin, query embedded with the |
| HV-02 | FAIL | PASS |  | reranker plugin is invoked when pinned (API-0001 rerank capability wired into retrieval?) |
| HV-03 | FAIL | PASS |  | authority levels L0-L5 (AUTHORITY_POLICY.authority_levels_required) enforced on mutating operations |
| HV-04 | FAIL | PASS |  | task close rejects files_changed outside the task's allowed_paths (mutation manifest scope) |
| HV-05 | FAIL | PASS |  | session claims (deterministic state) survive a full derived-memory rebuild |
| HV-06 | FAIL | PASS | MEDIUM | Tool Capability Registry resolves native run_tests tooling for a Rust governed project (not Python) |
| HV-07 | FAIL | PASS |  | an embedder pin change (version/dimensions) forces a full re-index; incremental rebuild must not lea |
| HV-08 | INFO | INFO |  | verifier-authored golden retrieval set on the adopted brownfield (recall@k, MRR, stale/superseded hi |
| HV-08b | FAIL | FAIL | MEDIUM | semantic paraphrase retrieval with the pinned baseline embedder |
| HV-09 | FAIL | PASS |  | SECURITY_POLICY.never_index_classes [secret, restricted]: restricted-class material (DATA_SENSITIVIT |
| HV-10 | FAIL | PASS |  | CIT-P is automatic for CHANGE_POLICY.auto_simulate_triggers (framework 48: the human should not need |
| HV-11 | FAIL | PASS | MEDIUM | gov update --apply --approve bypasses INV-008 (gate presented+answered) while CIT approval enforces  |
| HV-12 | PASS | PASS |  | delete vector/SQLite/graph + ALL generated views + framework.json, then rebuild from Git: identical  |
| HV-13 | PASS | PASS |  | a Go governed project (language different from the OS core and from every shipped fixture) is invent |
| HV-14 | PASS | PASS |  | cit rollback reverts propagation side-effects (retest flags) in addition to file snapshots |
| HV-15 | FAIL | PASS | MEDIUM | context compiler: superseded-but-ACTIVE decision is flagged/excluded from the deterministic authorit |
| HV-16 | FAIL | PASS |  | FREEZE_WRITES is honoured by migration batches and upstream submission (framework 74: every mutating |
| HV-17 | PASS | PASS |  | CIT-E verification blocks committing a governed record that contains a secret pattern (write-side ga |
| HV-18 | PASS | PASS | LOW | natural-language intent routing (T0 deterministic patterns) compiles to governance operations |
| HV-19 | FAIL | PASS | LOW | CHECKPOINT_POLICY mandatory trigger before_handoff is honoured automatically by handoff create |
| HV-20 | FAIL | PASS | MEDIUM | governance suite is green while memory recall is unmeasured (0 held-out queries) - framework 17 says |
| HV-21 | FAIL | PASS | LOW | retrieval applies MEMORY_POLICY.namespaces roles (product namespace roles=[engineering]) as an autho |
| HV-22 | PASS | PASS | LOW | one dependency-aware DAG expresses research -> experiment -> decision -> scenario -> dataset -> crit |
| HV-23 | FAIL | PASS | LOW | code-intelligence plugin (python-ast) is used and CALLS relationships reach the graph (framework 11. |
| HV-24 | FAIL | PASS | MEDIUM | portable gov executable: kernel payload obtainable without the build machine's source checkout (D-00 |
| HV-25 | PASS | PASS |  | deterministic core runs status/continue/audit/doctor with only git on PATH (no Python, no cargo) |
| HV-26 | FAIL | PASS |  | upstream packet sanitises every emitted field (category/title/tags carry identifiers?) |
| HV-27 | PASS | PASS |  | every generated artefact/record of a fresh project validates against the installed kernel schemas (d |
| HV-28 | FAIL | PASS | LOW | running gov audit (which writes an audit record) leaves the index fresh |
| HV-29 | FAIL | PASS |  | destructive migration batch requires an answered, presented Human Decision Gate record (not a CLI fl |
| HV-30 | PASS | PASS |  | multi-machine rebuild after a full brownfield adoption (mixed Python/TypeScript, archived stores, ex |
| HV-31 | PASS | PASS |  | TypeScript relative import is rewritten when the imported file is relocated by the migration executo |
| HV-32 | PASS | PASS | LOW | typed worker return is durably promoted into project state (handoff record carries the return; disco |
| HV-33 | FAIL | PASS |  | symbol route resolves a bare identifier query (the common form of a code-symbol question) |
| HV-34 | FAIL | PASS |  | cit propose scans the proposal/mutation manifest before persisting it as a governed record (secret l |
| HV-35 | PASS | PASS | LOW | the held-out regression file is not itself indexed (test-set leakage into the retrieval index) |
| HV-39 | FAIL | PASS |  | TEST_POLICY.implementation_task_requires [scenarios_present, acceptance_tests_declared] gates implem |
| HV-36 | FAIL | PASS |  | capability plugin host (API-0001) handles responses larger than the OS pipe buffer (a 512-dim embedd |

Verdict assignment remains the independent verifier's; this rerun is implementer evidence only.

Residual: HV-08b (baseline embedder paraphrase) by construction; assessed non-blocking by the second verifier (D-0006).
