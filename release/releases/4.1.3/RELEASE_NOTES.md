# agentic-engineering-os 4.1.3 — release notes (repair candidate)

Repair iteration after the independent rejection of 4.1.2 (`release/verification/4.1.2/INDEPENDENT_VERIFICATION_REPORT.md`,
verdict OS_RELEASE_CANDIDATE_REJECTED). The kernel payload changed (policies, roles, overlay template, schemas, tool
registry, enforcement map), so the version is bumped per release immutability; 4.1.2 stays immutable and rejected.
Repair mapping: `release/repair/4.1.3/REPAIR_REPORT.md`.

## Repaired (CRITICAL / HIGH)
- **C1** Retrieval, context compilation, held-out regression and CIT simulation embed queries with the embedder pinned
  in the index manifest (`meta.embedder` = id/version/dimensions/source); a missing plugin is `EMBEDDER_UNAVAILABLE`,
  a policy/index pin mismatch is `EMBEDDER_MISMATCH`. No silent fallback to the built-in embedder.
- **C2** Capability plugin host: stdin writer thread, concurrent stdout/stderr drains, timeout watchdog with
  process-group kill; unit tests cover a 1.2 MB response, a 600 KB request with stderr flood, timeout termination,
  malformed and protocol-mismatched responses.
- **H1** Pin-aware indexing: embedder/chunking/lexical/index-version pins are compared before an incremental build and
  escalate to a full staged rebuild (`state.db.building` → atomic swap); freshness reports `pin_mismatch`;
  doctor D025 flags mixed-dimension vectors as CRITICAL; `task close` refuses on `INDEX_PIN_MISMATCH`.
- **H2** Session claims live in `.governance-runtime/claims.db`, outside the rebuilt derived store; doctor D026
  checks its integrity; claims survive `gov rebuild-memory` (builder + HV-05).
- **H3** Authority levels L0–L5 (ROLES.yaml × AUTHORITY_POLICY.authority_levels_required) are enforced mechanically
  on tasks, CIT, gates, controls, checkpoints, handoffs, kernel install/reinstall, update apply/rollback, tool install,
  adoption batches, upstream prepare/submit, benchmark/select; unknown roles are `UNKNOWN_ROLE`.
- **H4** `task close` validates the report's `files_changed` against the task's allowed/forbidden paths, kernel paths
  and contract prohibitions (`MUTATION_SCOPE_VIOLATION`) unless the paths were touched by a committed CIT.
- **H5** `SECURITY_POLICY.never_index_classes` / `never_export_classes` and `DATA_SENSITIVITY.classifications` are
  applied by the repository contract: restricted/confidential/secret material is never indexed or retrievable;
  namespace roles filter retrieval; suite finding is CRITICAL when such artefacts appear in the index.
- **H6** Destructive migration entries get Human Decision Gate records at A4; A6 executes only entries whose gate was
  presented and answered A; `--gate-answer` is ignored (noted in the batch result). A gate answered B withdraws the
  removal and defers its scaffolded independent tests with the recorded reason.
- **H7** Reranker capability wired between fusion and filtering (pinned `MEMORY_POLICY.reranker`, `RERANKER_UNAVAILABLE`
  / `RERANKER_MISMATCH`); `gov memory benchmark --candidate …` measures candidates on the held-out set into a research
  record; `gov memory select <candidate>` pins the winner via a decision record, overlay override and full rebuild;
  `regression.min_queries` makes a too-small held-out set UNMEASURED (never green); starter held-out sets are richer.

## Repaired (MEDIUM / LOW)
Language-tagged tool registry (M1); automatic CIT-P for `auto_simulate_triggers` (M2); `update --apply` requires a
presented and answered gate (M3); context packet authority layers + conflicting-decision flag + deterministic
truncation (M4, L9); FREEZE_WRITES honoured by adoption batches and upstream submit (M5); kernel embedded in the
binary with logical lock source (M6); every upstream packet field sanitised incl. hyphen/underscore identifier
variants (M7); bare-identifier symbol route (M8); CIT propose redacts secrets and flags the record (M9);
implementation-task prerequisites and independent-author rules in the DAG (M10); FTS5 porter tokenizer option +
benchmark (M11); ENFORCEMENT_MAP + `policy_enforcement_coverage` family (M12, D-0003); catalogue
imports/references/consumers from the import graph (M13); `gov lessons cluster` → FCP records, MCP deferral recorded
(M14, D-0004); evidence script reports tool availability and never counts a missing tool (M15); stored synthetic 4.1.1
payload fixture (M16); checkpoint before handoff (L1); namespace filter (L2); CALLS edges + Go module resolution (L3);
audit keeps the index fresh (L4); held-out file not lexically indexed (L5); worker lessons promoted to PROVISIONAL
lesson records (L6); rollback marks the approval decision REJECTED (L7); timestamps quoted in YAML (L8).

## Supported migration paths
- 4.1.1 → 4.1.2 → 4.1.3 and 4.1.2 → 4.1.3 via `M-4.1.2-4.1.3` (non-breaking; overlay gains the sensitivity /
  reranker / lexical keys, lock schema unchanged, full index rebuild required because the index version changed).

## Known limits (honest scope)
- HV-08b: semantic paraphrase retrieval with the baseline hashed n-gram embedder fails by construction; the remedy
  is a per-repository benchmark and governed selection of a stronger embedder plugin, not a kernel default.
- MCP transport deferred (D-0004); remote upstream transports still refused.
- Dead-code classification remains heuristic; removal always requires an answered, presented gate.
- rustfmt divergence is advisory in this release; five clippy style warnings remain (zero errors).

## Certification
Implementer tests and evidence only. Status: READY_FOR_INDEPENDENT_REVERIFICATION (not certified).
