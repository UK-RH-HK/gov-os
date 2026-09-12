# Repair report — agentic-engineering-os 4.1.3 (repair candidate after the rejection of 4.1.2)

Written for: the independent verifier re-verifying the candidate, and the product owner.

| | |
|---|---|
| Rejected candidate | 4.1.2 at commit `8ad06be` — verdict OS_RELEASE_CANDIDATE_REJECTED (`release/verification/4.1.2/INDEPENDENT_VERIFICATION_REPORT.md`) |
| Repair code commit | `REPAIR_CODE_COMMIT` (branch `release/4.1.2-rc1`; not merged to `main`) |
| Repair candidate commit | the commit that adds `release/releases/4.1.3/` on top of the repair code commit (hash reported in the handoff message and in `release/CERTIFICATION_STATUS.md`) |
| Kernel version | 4.1.3 (payload changed → new immutable release; 4.1.2 untouched, still REJECTED) |
| Certification | **pending** — READY_FOR_INDEPENDENT_REVERIFICATION; the implementer has not certified anything |

Verifier artefacts (`INDEPENDENT_VERIFICATION_REPORT.md`, `heldout/harness.py`, `heldout/results.json`,
`heldout/run-full.log`, the REJECTED text in `CERTIFICATION_STATUS.md`, `release/releases/4.1.2/`) were **not modified**.
The harness was rerun unchanged with `GOV_VERIFIER_OUT=release/verification/4.1.2/heldout-rerun` (summary in
`heldout-rerun/SUMMARY.md`). No verifier-authored test was weakened, rewritten, bypassed or special-cased; no
independent test was judged invalid.

## 1. Held-out harness — unchanged rerun

| Verdict | Verifier run (4.1.2) | Implementer rerun (4.1.3) |
|---|---|---|
| PASS | 12 | 36 |
| FAIL | 25 | 1 (HV-08b, MEDIUM) |
| INFO | 1 | 1 (HV-08) |
| ERROR | 0 | 0 |

## 2. CRITICAL / HIGH findings — root cause, change, regression test, held-out result

| ID | Root cause (as reproduced) | Implementation change | Builder regression test | Held-out (unchanged) |
|---|---|---|---|---|
| **C1** query embedding hard-coded to built-in | `retrieval/mod.rs` semantic route called the built-in hasher directly; the pinned plugin was used only at index time, so query and index vectors lived in different spaces and results equalled the built-in prediction | `memory/embedder.rs`: `EmbedSpec` + `Embedder::resolve` (builtin or plugin, `EMBEDDER_UNAVAILABLE` when the pinned plugin is missing — no fallback), `Embedder::for_query` uses the live `meta.embedder`, `EMBEDDER_MISMATCH` on policy≠index or dimension mismatch, `EMBEDDER_BAD_OUTPUT` on wrong count/dims; retrieval, context compiler, held-out regression, CIT simulation and benchmark all go through it; identity/dimensions recorded in `meta.embedder` and `index-manifest.json` | `repair::embedder_replaceable_end_to_end_and_no_silent_fallback` (index with a reversed-vector plugin served by `gov capabilities serve-embed --reverse`; query ranking follows the plugin; plugin removed → `EMBEDDER_UNAVAILABLE`, no fallback); `arch::builtin_embedder_matches_python_reference_plugin` | HV-01 PASS, HV-07 PASS |
| **C2** plugin host deadlock on large responses | `capabilities/host.rs` wrote stdin, then polled `try_wait()` until exit before reading stdout; a child producing more than the pipe buffer blocked forever → `PLUGIN_TIMEOUT` | Host rewritten: stdin writer thread, concurrent stdout/stderr drain threads (stderr tail retained), watchdog loop with `try_wait` + timeout that kills the child's process group (`libc::kill(-pid, SIGKILL)`, child spawned with `process_group(0)`), typed errors `PLUGIN_TIMEOUT`/`PLUGIN_BAD_RESPONSE`/`PLUGIN_PROTOCOL_MISMATCH`/`PLUGIN_ERROR`, `PluginOutcome` carries `stdout_bytes`/`elapsed_ms` | Unit: `host::tests::large_response_well_above_pipe_buffer_does_not_deadlock` (1.2 MB), `large_stdin_request_and_stderr_flood_are_drained` (600 KB in + 60 000 stderr lines), `timeout_kills_child_promptly` (< 5 s incl. grandchild), `bad_json_and_protocol_mismatch_are_reported`; CLI: `repair::plugin_host_large_response_through_cli` | HV-36 PASS (both sizes < 1 s) |
| **H1** pin change leaves a mixed index reported healthy | Incremental builds never compared pins; new vectors used the new dimension next to old ones; freshness/doctor only looked at content hashes | `indexer.rs`: `expected_pins`/`live_pins`/`pin_differences`; incremental → full escalation (`escalated_to_full`); full builds staged in `state.db.building` and swapped atomically; `manifest.rs` `Freshness.pin_mismatch` (fresh=false); doctor D025 (mixed dimension groups CRITICAL, pin diff HIGH, reranker pin); `task close` refuses `INDEX_PIN_MISMATCH` | `repair::embedder_pin_change_escalates_to_full_rebuild_without_mixed_index` (asserts one dimension group after an incremental build following a pin change, freshness `pin_mismatch`, D025) ; `failure_injection` (bad plugin → error, index intact) | HV-07 PASS |
| **H2** claims lost on full rebuild | Claims were rows in `state.db`, which a full rebuild deletes | `memory/claims.rs` `ClaimsStore` at `.governance-runtime/claims.db` (never touched by rebuild; `control.json` already separate); `orchestration/claims.rs` delegates; doctor D017 uses the store, D026 checks integrity | `repair::claims_survive_full_memory_rebuild`; `failure_injection` (raw insert survives) | HV-05 PASS |
| **H3** authority levels not enforced | `AUTHORITY_POLICY.authority_levels_required` and `ROLES.yaml` levels were data only | `authority.rs` (`level_of`, `required_level` default L3, `require` → `AUTHORITY_DENIED` with details, `UNKNOWN_ROLE`); enforced on task create/status/claim/release/close, CIT propose/simulate/approve/execute/rollback, gate create/present/answer (human relay needs L3+, `human` role L5, agent answers only within `agent_resolvable_when`), emergency/resume controls, checkpoint, handoff, kernel install/reinstall, update apply/rollback, tool install, adoption batches A6/A8/A9, upstream prepare/submit, benchmark/select, claims sweep; `AUTHORITY_POLICY.yaml` operation map completed | `repair::authority_levels_are_enforced_on_executable_paths` (L0 auditor / L1 denied on each path, L3+ allowed, unknown role) | HV-03 PASS |
| **H4** mutation scope not checked at close | `task close` accepted any `files_changed` | `orchestration/tasks.rs` `scope_violations` (forbidden paths, kernel paths, contract-prohibited mutations, outside `allowed_paths` unless the path was touched by a COMMITTED CIT's propagation) → `MUTATION_SCOPE_VIOLATION`; close also checks index pin/staleness and governance currency | `repair::task_close_enforces_mutation_scope` | HV-04 PASS |
| **H5** restricted/confidential material indexed and retrievable | `paths.rs` knew only the secret class; `never_index_classes`/`never_export_classes`/`DATA_SENSITIVITY.classifications` were unread; no namespace filter | `paths.rs` `SensitivityRules` (classifications, never_index, never_export, archive default retrieval) applied in `decide()`; `project.rs` `contract()` builds them from SECURITY_POLICY/DATA_SENSITIVITY/ARCHIVE_POLICY; indexer excludes with reason `sensitivity:<class>` and records dangling imports as `excluded:<path>`; retrieval namespace/role filter via `ROLES.yaml` groups; suite finding CRITICAL when never-index artefacts are indexed; export gate honours `never_export_classes` | `repair::sensitivity_classes_and_namespaces_are_enforced` (confidential path never indexed/retrieved by any route; namespace role exclusion) ; `paths::tests::secret_classification_can_never_be_downgraded` | HV-09 PASS, HV-21 PASS |
| **H6** destructive batches gated by a CLI flag | `adopt migrate --gate-answer <ART>` counted as an answer; no gate record existed | `adopt.rs` `ensure_destructive_gates` creates one HDG record per destructive entry at A4 (and batch 0); `answered_destructive` accepts only presented gates answered **A**; `--gate-answer` ignored with a note; a gate answered B withdraws the removal (`verify.rs` defers the scaffolded test with the recorded reason; batch result names the gate); `gates::answered_option` | `repair::destructive_migration_requires_answered_gate_record` (flag-only → nothing deleted, gate PENDING, `GATE_NOT_PRESENTED`, present+decide A → executed); `brownfield`/`migration` fixtures answer gates through records (option A / option B paths) | HV-29 PASS, HV-31 PASS |
| **H7** no reranker hook, no benchmark/selection | Reranker pin unread; embedder choice hard-coded; a 0-query held-out set was green | `Reranker::resolve`/`rerank` between fusion and filtering (`RERANKER_UNAVAILABLE`/`RERANKER_MISMATCH`); `memory/benchmark.rs` (`gov memory benchmark` → isolated index per candidate, held-out metrics, research record; `gov memory select` → decision record + overlay override + full rebuild); `regression.min_queries` → `UNMEASURED` never green; `memory/heldout.rs` richer starter set (ids, paths, symbols incl. methods, literals, graph, superseded, pending paraphrase placeholders); FTS5 tokenizer configurable (`porter unicode61`) | `repair::reranker_hook_invoked_and_never_silently_skipped`, `repair::benchmark_records_evidence_and_selection_pins_through_decision`, `repair::unmeasured_memory_recall_is_not_green` | HV-02 PASS, HV-20 PASS, HV-08 INFO (recall 0.833, MRR 0.715, pass under policy thresholds), HV-08b FAIL (residual, §5) |

## 3. MEDIUM / LOW findings

| ID | Change | Test / evidence |
|---|---|---|
| M1 | `tools/registry/TOOLS.yaml` language-tagged descriptors (cargo test/clippy/rustfmt/rust-analyzer, npm, go, ctest/make, maven); `tools resolve` filters by detected ecosystems; `health_check_required`, `auto_install_conditions`, `mcp.registry_path` read | `arch::ecosystem_resolution_follows_the_governed_project_not_the_os`; HV-06 PASS |
| M2 | `cit propose` simulates automatically for `CHANGE_POLICY.auto_simulate_triggers` | `repair::cit_auto_simulation_and_secret_redaction`; HV-10 PASS |
| M3 | `update --apply` requires the framework-update gate presented+answered; `--approve` alone → `applied:false` | `repair::update_approval_requires_presented_answered_gate`, `update` fixture; HV-11 PASS |
| M4 / L9 | Context packet `authority_layers` (invariants → security/authority → project policy → decisions …), `conflicting_decisions` flagged `UNKNOWN_OR_CONFLICTING`, deterministic truncation to `max_packet_chars` (`truncated_slices`) | `repair::context_packet_layers_and_contradiction_flags`; HV-15 PASS |
| M5 | `guard_write` (FREEZE_WRITES) in adopt A6/A8/A9 and `upstream submit` | `repair::freeze_writes_is_honoured_by_adopt_and_upstream`; HV-16 PASS |
| M6 | Kernel payload embedded in the binary (`runtime/build.rs`), cache under `$GOV_KERNEL_CACHE`/XDG; lock `source` is a logical label; `--source` / `GOV_CANONICAL_ROOT` overrides | `repair::embedded_kernel_installs_without_canonical_root`; HV-24 PASS |
| M7 | Upstream packet sanitises category/title/tags/every field; identifier redaction matches hyphen/underscore/space variants | `upstream` fixture; HV-26 PASS |
| M8 | Bare identifier queries take the symbol route | `repair::implementation_prerequisites_and_symbol_route`; HV-33 PASS |
| M9 | `cit propose` redacts secrets in proposal/manifest, marks `secret_flagged`; execute refuses `SECRET_IN_MANIFEST` | `repair::cit_auto_simulation_and_secret_redaction`; HV-34 PASS, HV-17 PASS |
| M10 | `TEST_POLICY.implementation_task_requires` + `independent_test_author_required_for` block implementation tasks in the DAG | `repair::implementation_prerequisites_and_symbol_route`; HV-39 PASS |
| M11 | FTS5 `porter unicode61` tokenizer option + benchmark mechanism (residual HV-08b, §5) | benchmark test; HV-08 INFO |
| M12 | `framework/policies/ENFORCEMENT_MAP.yaml` + `policy_coverage::report` + suite family `policy_enforcement_coverage`; every previously unread key is now consumed (budget thresholds → gates, `auto_simulate_triggers`, `corroboration_min_sources`, `agent_resolvable_when`, `implementation_task_requires`, `prose_summary_as_checkpoint`, `unused_code_action`, `record_evidence`, …) — decision D-0003 | `repair::policy_enforcement_coverage_is_complete_and_honest`; suite family |
| M13 | Catalogue `imports`/`references`/`consumers` populated from the classifier's import graph | `migration` fixture assertion |
| M14 | `gov lessons cluster` → Framework Change Proposal records (`framework-change-proposal` schema); MCP transport deferred by decision D-0004 | `repair::smaller_findings_regressions` |
| M15 | `scripts/collect_evidence.sh` reports tool availability (`tool-status.txt`), clippy/rustfmt RAN/NOT_RUN, never counts a missing tool; clippy and rustfmt installed and run for this candidate | `docs/EVIDENCE.md`, `release/evidence/` |
| M16 | Stored synthetic 4.1.1 payload `fixtures/update/previous-release/4.1.1/` | `update` fixture |
| L1 | Checkpoint `before_handoff` written automatically | `repair::smaller_findings_regressions`; HV-19 PASS |
| L2 | Namespace/role retrieval filter | see H5; HV-21 PASS |
| L3 | CALLS edges from symbol references; Go module import resolution | HV-23 PASS, HV-13 PASS |
| L4 | `gov audit` persists the record then rebuilds incrementally | HV-28 PASS |
| L5 | `governance/tests/**` `lexical_index: false` in the contract template | HV-35 PASS, HV-08 top-k no longer contains the held-out file |
| L6 | Worker-return lessons promoted to PROVISIONAL lesson records | HV-32 PASS |
| L7 | CIT rollback marks the approval decision REJECTED (`rollback_of`) | HV-14 PASS |
| L8 | Date/timestamp scalars quoted in YAML | HV-27 PASS |

## 4. Builder evidence (this candidate)

Suites on the final code state (`docs/EVIDENCE.md`, raw outputs in `release/evidence/`):
- `cargo test -p gov-runtime` — 14 unit tests (incl. the four host tests) pass.
- `cargo test -p gov-cli --test certification` — 35 scenarios pass (7 fixtures + architecture tests + 17 repair regressions + update/upstream/failure-injection).
- `pytest capabilities/tests` — 4 pass.
- `cargo clippy --workspace --all-targets` — ran; 0 errors; 5 style diagnostics remain (sort_by_key ×2, `&mut Vec` parameter, complex type, large enum variant; `release/evidence/clippy-summary.txt` counts 7 `warning:` lines because it includes the two per-crate summary lines).
- `cargo fmt --all -- --check` — ran; formatting divergent (advisory; deliberately not applied so the repair diff stays reviewable).
- Held-out harness rerun unchanged: 36 PASS / 1 FAIL / 1 INFO / 0 ERROR.

One intermittent unit-test failure was observed once (1 of 14 failed in a background run whose captured output only kept the summary line); it did not reproduce in nine subsequent runs, four of them concurrent with the full certification suite. It is recorded here rather than hidden; the timing-sensitive tests are the host tests (`timeout_kills_child_promptly` asserts termination within 5 s of a 400 ms timeout).

## 5. Residuals and honest limits
- **HV-08b (MEDIUM) remains FAIL**: semantic paraphrase retrieval with the pinned *baseline* embedder. The built-in hashed n-gram embedder cannot represent paraphrase by construction; it exists so the core runs with zero model dependencies. The remedy the verifier asked for is delivered as a mechanism, not a kernel default: `gov memory benchmark` + `gov memory select` pin a stronger embedder per repository through a measured, recorded decision. The harness note "no comparative benchmark mechanism exists" is therefore no longer accurate, but the verdict of that scenario is the verifier's to reassess.
- MCP transport deferred (D-0004); remote upstream transports still refused.
- rustfmt not applied (advisory); five clippy style warnings.
- `HV-36` detail text in the rerun still contains the pre-repair cause string because the harness embeds it; the measured result is PASS.

## 6. Architecture constraints preserved
Rust-first deterministic core, no Python to operate the core (`arch::core_runs_without_any_governed_toolchain_on_path`, HV-25 PASS); polyglot capabilities behind `gov-capability/1`; model independence (embedder/reranker are pinned, replaceable specs — the binary itself can serve as an embed plugin); Git as truth, SQLite as derived state, claims/control outside the derived store; all memory classes rebuildable (`multi_machine`, HV-12 PASS, HV-30 PASS); kernel/overlay separation (migration `M-4.1.2-4.1.3` touches overlay/lock/generated only); independent verification boundaries (verifier artefacts untouched, no self-certification).

## 7. Records
D-0003 (policy enforcement coverage), D-0004 (MCP deferral, lesson clustering/FCP), TASK-0010 (repair task), RPT-0010
(closing report), release notes `release/notes/4.1.3.md`, migration `migrations/M-4.1.2-4.1.3.yaml`.
