# Independent held-out harness — implementer rerun (unchanged harness)

Rerun at 2026-09-12T03:45:45Z by the implementer against the repaired candidate (branch `release/4.1.2-rc1`, kernel 4.1.3).
Harness: `release/verification/4.1.2/heldout/harness.py` — **not modified**; invoked with `GOV_VERIFIER_OUT` pointing
at this directory so the verifier's original `heldout/results.json` and `run-full.log` stay untouched.
Command: `cargo build --release && GOV_VERIFIER_OUT=$PWD/release/verification/4.1.2/heldout-rerun python3 release/verification/4.1.2/heldout/harness.py`

`gov version` output: `framework: agentic-engineering-os
version: 4.1.3
cli_version: 4.1.3
runtime_version: 4.1.3
index_version: 4.1.3-idx2`

| Verdict | Original run (verifier) | Rerun (repaired candidate) |
|---|---|---|
| PASS | 12 | 36 |
| FAIL | 25 | 1 |
| INFO | 1 | 1 |
| ERROR | 0 | 0 |

## Per-scenario

| ID | Original | Rerun | Severity (rerun) | Title |
|---|---|---|---|---|
| HV-01 | FAIL | PASS |  | embedding model replaceable at query time: index built by the pinned plugin, query embedded with the same mode |
| HV-02 | FAIL | PASS |  | reranker plugin is invoked when pinned (API-0001 rerank capability wired into retrieval?) |
| HV-03 | FAIL | PASS |  | authority levels L0-L5 (AUTHORITY_POLICY.authority_levels_required) enforced on mutating operations |
| HV-04 | FAIL | PASS |  | task close rejects files_changed outside the task's allowed_paths (mutation manifest scope) |
| HV-05 | FAIL | PASS |  | session claims (deterministic state) survive a full derived-memory rebuild |
| HV-06 | FAIL | PASS | MEDIUM | Tool Capability Registry resolves native run_tests tooling for a Rust governed project (not Python) |
| HV-07 | FAIL | PASS |  | an embedder pin change (version/dimensions) forces a full re-index; incremental rebuild must not leave a mixed |
| HV-08 | INFO | INFO |  | verifier-authored golden retrieval set on the adopted brownfield (recall@k, MRR, stale/superseded hits, by cat |
| HV-08b | FAIL | FAIL | MEDIUM | semantic paraphrase retrieval with the pinned baseline embedder |
| HV-09 | FAIL | PASS |  | SECURITY_POLICY.never_index_classes [secret, restricted]: restricted-class material (DATA_SENSITIVITY classifi |
| HV-10 | FAIL | PASS |  | CIT-P is automatic for CHANGE_POLICY.auto_simulate_triggers (framework 48: the human should not need to type / |
| HV-11 | FAIL | PASS | MEDIUM | gov update --apply --approve bypasses INV-008 (gate presented+answered) while CIT approval enforces it |
| HV-12 | PASS | PASS |  | delete vector/SQLite/graph + ALL generated views + framework.json, then rebuild from Git: identical derived st |
| HV-13 | PASS | PASS |  | a Go governed project (language different from the OS core and from every shipped fixture) is inventoried, map |
| HV-14 | PASS | PASS |  | cit rollback reverts propagation side-effects (retest flags) in addition to file snapshots |
| HV-15 | FAIL | PASS | MEDIUM | context compiler: superseded-but-ACTIVE decision is flagged/excluded from the deterministic authority block; h |
| HV-16 | FAIL | PASS |  | FREEZE_WRITES is honoured by migration batches and upstream submission (framework 74: every mutating operation |
| HV-17 | PASS | PASS |  | CIT-E verification blocks committing a governed record that contains a secret pattern (write-side gate, not on |
| HV-18 | PASS | PASS | LOW | natural-language intent routing (T0 deterministic patterns) compiles to governance operations |
| HV-19 | FAIL | PASS | LOW | CHECKPOINT_POLICY mandatory trigger before_handoff is honoured automatically by handoff create |
| HV-20 | FAIL | PASS | MEDIUM | governance suite is green while memory recall is unmeasured (0 held-out queries) - framework 17 says that is n |
| HV-21 | FAIL | PASS | LOW | retrieval applies MEMORY_POLICY.namespaces roles (product namespace roles=[engineering]) as an authority+names |
| HV-22 | PASS | PASS | LOW | one dependency-aware DAG expresses research -> experiment -> decision -> scenario -> dataset -> criteria -> te |
| HV-23 | FAIL | PASS | LOW | code-intelligence plugin (python-ast) is used and CALLS relationships reach the graph (framework 11.2 CALLS ed |
| HV-24 | FAIL | PASS | MEDIUM | portable gov executable: kernel payload obtainable without the build machine's source checkout (D-0002: self-c |
| HV-25 | PASS | PASS |  | deterministic core runs status/continue/audit/doctor with only git on PATH (no Python, no cargo) |
| HV-26 | FAIL | PASS |  | upstream packet sanitises every emitted field (category/title/tags carry identifiers?) |
| HV-27 | PASS | PASS |  | every generated artefact/record of a fresh project validates against the installed kernel schemas (draft 2020- |
| HV-28 | FAIL | PASS | LOW | running gov audit (which writes an audit record) leaves the index fresh |
| HV-29 | FAIL | PASS |  | destructive migration batch requires an answered, presented Human Decision Gate record (not a CLI flag naming  |
| HV-30 | PASS | PASS |  | multi-machine rebuild after a full brownfield adoption (mixed Python/TypeScript, archived stores, extracted re |
| HV-31 | PASS | PASS |  | TypeScript relative import is rewritten when the imported file is relocated by the migration executor |
| HV-32 | PASS | PASS | LOW | typed worker return is durably promoted into project state (handoff record carries the return; discoveries/les |
| HV-33 | FAIL | PASS |  | symbol route resolves a bare identifier query (the common form of a code-symbol question) |
| HV-34 | FAIL | PASS |  | cit propose scans the proposal/mutation manifest before persisting it as a governed record (secret lands in sp |
| HV-35 | PASS | PASS | LOW | the held-out regression file is not itself indexed (test-set leakage into the retrieval index) |
| HV-39 | FAIL | PASS |  | TEST_POLICY.implementation_task_requires [scenarios_present, acceptance_tests_declared] gates implementation t |
| HV-36 | FAIL | PASS |  | capability plugin host (API-0001) handles responses larger than the OS pipe buffer (a 512-dim embedder answeri |

## Residuals

- **HV-08b (MEDIUM, FAIL, unchanged verdict)** — semantic paraphrase retrieval with the pinned *baseline* embedder. The built-in hashed n-gram embedder has no paraphrase capability by construction (it is the deterministic zero-dependency baseline); V-SEM-1 (no token overlap) still misses. The harness note "no comparative benchmark mechanism exists to select a stronger one" no longer holds: `gov memory benchmark --candidate current --candidate plugin:<id>[:dim] --record` measures candidates on the held-out set and records a research record, and `gov memory select <candidate>` pins the winner through a decision record + overlay override + full rebuild (builder test `repair::benchmark_records_evidence_and_selection_pins_through_decision`). Selecting a stronger embedder for a given repository is a governed, evidence-driven decision, not a kernel default — the kernel must run with no model dependency (INV: Git truth, rebuildability, no Python to operate the core).
- **HV-08 (INFO)** — verifier golden set on the adopted brownfield: recall@k 0.833 (was 0.833), MRR 0.715 (was 0.683), stale/superseded hit rate 0.0, forbidden violations 0, pass under policy thresholds: True.
- HV-36 detail text still names the pre-repair cause (the harness embeds that string); the measured result is PASS with both response sizes returning in < 1 s.

Verdict assignment remains the independent verifier's; this rerun is implementer evidence only.
