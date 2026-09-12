# agentic-engineering-os 4.1.4 — release notes (repair candidate)

Second repair iteration, after the independent re-verification rejected 4.1.3
(`release/verification/4.1.3/INDEPENDENT_REVERIFICATION_REPORT.md`, verdict OS_RELEASE_CANDIDATE_REJECTED). The nine
CRITICAL/HIGH findings of the first verification were independently confirmed repaired and are preserved. The kernel
payload changed (policies, schemas, migration), so the version is bumped; 4.1.3 stays immutable and rejected.
Repair mapping: `release/repair/4.1.4/REPAIR_REPORT.md`.

## Repaired (CRITICAL / HIGH)
- **C-N1** Human Decision Gate integrity for CIT: approval is derived from the authoritative gate answer (presented,
  ANSWERED with A, ACTIVE decision, gate bound to the transaction); presentation is not approval, a decline REJECTS
  the CIT, a revoked or re-answered gate cannot approve, execution revalidates, approval records carry presenter /
  answerer / kind / time / decision; `human_approved` is never caller-supplied. `gov gate revoke` added.
- **H-N1** Constitutional policy precedence: `POLICY_PRECEDENCE.yaml` (kernel) classifies every policy key as
  immutable / floor / ceiling / additive / shrink-only / strengthen-only / overridable (deny by default); overrides
  and exceptions that would weaken authority, sensitivity, human-gate, change-control or export floors are refused,
  recorded, reported (doctor D027 CRITICAL, family `policy_precedence`, context packet) and leave the effective
  policy unchanged. `gov policy overrides|effective` added.
- **H-N2** Governed capability plugins: schema-validated descriptors (identity + version pin required),
  registration through `gov plugins register` (gate for elevated permissions), authority floor
  (`TOOL_POLICY.plugins.min_authority`), `approved_roles`, permission classes, health, content pin with drift
  refusal; L0/L1 roles cannot trigger execution; plugins appear in the Tool/Capability Registry; doctor D028 and
  family `plugin_governance`. API-0001 amended to v1.1 (D-0005).

## Repaired (MEDIUM / LOW)
Lock provenance (`release_commit` = framework release commit, `installed_at_commit` = consumer HEAD, logical
`source` on init/adopt/update; lock schema 1.1.0) — M-N1/M-N2/NV-08/NV-03; migration substance (`set_overlay_rule`
op, template-default reconciliation in `gov update`, `overlay_template_changes` declarations, `MIGRATION_INCOMPLETE`
at release build, M-4.1.2-4.1.3 description corrected with amendment history) — M-N3/NV-19; observed mutation scope
at task close (claim-time tree snapshot vs close-time tree) — M-N4/NV-05; relocation-aware incremental indexing —
M-N5/NV-07; interface truth (API-0001 v1.1, PROTOCOL.md, fixture README) — M-N6; branch/tag provenance
(`release/4.1.4-rc1`, `v4.1.3-rc1`, `v4.1.4-rc1`, manifest `provenance`) — M-N7; genuine 4.1.2 → 4.1.3 → 4.1.4
builder test — M-N8; paraphrase-capable candidate policy (D-0006, optional sentence-transformers plugin template,
benchmark record) — M-B1; KERNEL.yaml duplicate key removed + strict-YAML test — L-N1; rollback ledger + consumed
snapshots — L-N2; `memory select` approval derived from the acting authority — L-N3; trust boundary documented —
L-N4; docs refreshed — L-N5; rustfmt applied and clippy clean — L-N6; five-state evidence vocabulary; single
literal-like tokens are exact lookups in retrieval.

## Supported migration paths
- 4.1.1 → 4.1.2 → 4.1.3 → 4.1.4, 4.1.2 → 4.1.3 → 4.1.4 and 4.1.3 → 4.1.4 via `M-4.1.3-4.1.4` (non-breaking; sets
  `governance/tests/**` lexical_index=false, lock schema 1.1.0, full index rebuild, adapters regenerated).

## Known limits (honest scope)
- HV-08b stays FAIL with the baseline embedder by construction (accepted as non-blocking by the verifier); NV-16 and
  NV-19 are bound to the immutable 4.1.3 payload and are re-evaluated for 4.1.4 by equivalent builder tests.
- MCP transport deferred (D-0004); remote upstream transports refused; roles are caller-declared (documented boundary).

## Certification
Implementer tests and evidence only. Status: READY_FOR_INDEPENDENT_REVERIFICATION (not certified).
