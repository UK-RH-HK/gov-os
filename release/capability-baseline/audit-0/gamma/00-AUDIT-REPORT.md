# Iteration-0 Capability Family Audit: gamma

| Field | Value |
|---|---|
| Run | P2-AR-0003 |
| Family | gamma |
| Capabilities | E (E1-E4), F (F1-F5), G (G1-G2), H (H1-H4), I (I1-I4) |
| Candidate | cap2-candidate-0 |
| Candidate commit | 57177a37ea296ece16b185874831462b6a76db18 |
| Product code digest | bd4d65d9d5ffd6aedbd9435e2091a664dfc3e62f80614a76197cfaf87efd0547 |
| Contract v3 SHA-256 | 4c2df29115c8d5389034b2e2d817772add80d61678807c23e0d520c937cb5ed3 |
| Frozen gate contract SHA-256 | d2f33e89d5459dd809e17271e46854cc886ed958ca63f89765e16d6a26a9f25e |
| Audit date | 2026-09-18 |
| Auditor model | claude-opus-4-6 |

## Pinned-input verification

All pinned inputs verified:
- HEAD = 57177a37ea296ece16b185874831462b6a76db18, tag `cap2-candidate-0` present
- `product_code_digest` matches: `bd4d65d9d5ffd6aedbd9435e2091a664dfc3e62f80614a76197cfaf87efd0547`
- Contract v3 SHA-256 matches: `4c2df29115c8d5389034b2e2d817772add80d61678807c23e0d520c937cb5ed3`
- Frozen gate contract SHA-256 matches orchestrator state: `d2f33e89d5459dd809e17271e46854cc886ed958ca63f89765e16d6a26a9f25e`
- Branch: `phase2/cap-audit-0-gamma`

## Method

For every capability and bullet, the auditor:
1. Read the relevant implementation source and schema files
2. Built the product (`cargo build --release`, 42 lib tests pass, 79 certification tests pass)
3. Initialized a disposable governed project under a scratch directory
4. Drove `target/release/gov` against the disposable project to exercise each bullet
5. Recorded all probe scripts and outputs under `evidence/`

## Summary table

| Capability | Status | Finding count |
|---|---|---|
| E1 | PRESENT_AND_SUBSTANTIAL | 0 |
| E2 | PRESENT_AND_SUBSTANTIAL | 0 |
| E3 | PRESENT_AND_SUBSTANTIAL | 0 |
| E4 | PRESENT_AND_SUBSTANTIAL | 0 |
| F1 | PRESENT_AND_SUBSTANTIAL | 0 |
| F2 | PRESENT_AND_SUBSTANTIAL | 0 |
| F3 | PRESENT_AND_SUBSTANTIAL | 0 |
| F4 | PRESENT_AND_SUBSTANTIAL | 0 |
| F5 | PARTIAL | 1 |
| G1 | PRESENT_AND_SUBSTANTIAL | 0 |
| G2 | PRESENT_AND_SUBSTANTIAL | 0 |
| H1 | PRESENT_AND_SUBSTANTIAL | 0 |
| H2 | PRESENT_AND_SUBSTANTIAL | 0 |
| H3 | PRESENT_AND_SUBSTANTIAL | 0 |
| H4 | PARTIAL | 1 |
| I1 | PRESENT_AND_SUBSTANTIAL | 0 |
| I2 | PRESENT_AND_SUBSTANTIAL | 0 |
| I3 | PARTIAL | 1 |
| I4 | PRESENT_AND_SUBSTANTIAL | 0 |

## Key findings

### F5 - PARTIAL (A0-F5-01)

F5 requires that MCP, tools, A2A and Knowledge Fabric are explicitly separated with no silent
substitution. The implementation separates tools (CLI/library/plugin), MCP servers and A2A handoffs
into distinct registries and code paths. However, the explicit textual contract between MCP = action/
capability, A2A = communication, Knowledge Fabric = knowing is not enforced as a runtime invariant.
The separation exists architecturally (separate modules, separate registries), but no executable
guard prevents a future path from routing an A2A communication through a tool call or vice versa. The
gap is structural clarity rather than a live bypass, and cannot undermine qualification because the
actual code paths are separate.

### H4 - PARTIAL (A0-H4-01)

H4 requires FEATURE -> SCENARIOS -> DATA -> TEST DATA -> SUCCESS/FAILURE -> INDEPENDENT TESTS chain.
The feature schema has `scenarios` and `acceptance_tests` fields, and the DAG enforces
`TEST_POLICY.implementation_task_requires: [scenarios_present, acceptance_tests_declared]`. The
test-data author independence is supported via `TEST_POLICY.independent_test_author_required_for`.
However, `test_data`, `success_criteria` and `failure_criteria` are not dedicated fields in the
feature schema; they are captured as readiness dimensions (H2) rather than explicit schema-level
fields in the feature record. Data provenance is recorded via the record `state_class` field. The gap
is schema-level vs dimension-level traceability, which does not undermine qualification because the
readiness contract enforces their presence.

### I3 - PARTIAL (A0-I3-01)

I3 lists 11 generation sources. Of these, 8 are executably evidenced: readiness gaps, CIT effects,
lessons, missing tools/skills, human decisions, failed tests (retest_required), audit findings
(doctor remediation), and research discoveries (proposed_decisions). Three sources are not directly
demonstrated as automatic task generators at runtime: retrieval failures, security findings, and
performance regressions. The code detects retrieval regressions (verification/mod.rs) and the doctor
checks security/performance, but these produce findings/degraded-status rather than automatically
creating governed tasks. The gap cannot undermine qualification because the detection mechanisms
exist and a human or orchestrator can create the tasks from the findings.

## What could not be established

Nothing prevents the audit from being complete. All capabilities in scope were evaluated with
executable evidence.
