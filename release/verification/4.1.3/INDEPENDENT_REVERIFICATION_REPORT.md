# Independent OS Re-Verification Report — agentic-engineering-os repair candidate 4.1.3

| | |
|---|---|
| **Verdict** | **OS_RELEASE_CANDIDATE_REJECTED** (repairable; precise builder repair delta in §12) |
| Verifier | Independent Governance OS Verifier and Test Author — fresh re-verification session, no builder context, no continuation of the first verifier's session (Claude Fable 5.1) |
| Date | 2026-09-12 |
| Candidate | branch `release/4.1.2-rc1`, commit `26ab5b6eb111d573f8686bc4f4b1dfc20539f45e`; payload `release/releases/4.1.3` (release_commit `78f6853…`, release_hash `6bebfdbb…3627d1`) |
| Toolchain | rustc/cargo 1.98.1, clippy 0.1.98, rustfmt 1.9.0, Python 3.12.3 (harnesses only), git 2.43.0, Linux x86_64 (`evidence/toolchain-and-binaries.txt`) |
| Independence | Builder and first-verifier conclusions were not trusted. `cargo clean` + release rebuild; builder suites re-executed; the first verifier's harness re-run **byte-identical** (sha256 `a01155de…b1f9c` = commit 9563192); 17 new scenarios authored here (`heldout-new/harness_v2.py`) that neither the builder nor the first verifier knew, driven only through the `gov --json` contract; a second binary built from the rejected 4.1.2 commit `8ad06be` was used solely to create genuine 4.1.2 consumer state |
| Artefacts | `heldout-prev-rerun/` (unchanged harness rerun), `heldout-new/` (new harness, results, log), `builder-suite-rerun/` (unit, certification, plugin, clippy, rustfmt logs), `evidence/` (toolchain, build logs), `VERDICT.md` |
| Not modified | No implementation source, kernel data, fixture, builder test, first-verifier artefact or release payload was modified. `git status` shows only `release/verification/4.1.3/` as new. The 4.1.3 manifest certification block was **not** changed by this session (permission to edit shared release files was withheld); the verdict is recorded here and in `VERDICT.md` for the release owner to transcribe |

## 0. Summary

The repair is real. Every CRITICAL and HIGH finding of the 4.1.2 rejection (C1, C2, H1–H7) was independently inspected at the source and re-exercised: the first verifier's 37-scenario harness now passes 36/37 unchanged (the residual HV-08b is assessed in §5), and the repairs are implemented at the root cause rather than special-cased (§3). The builder's suites reproduce on a clean rebuild (35/35 certification, 14/14 unit, 4/4 plugin; clippy 5 style warnings, rustfmt divergent). The 4.1.3 release payload is internally coherent: it equals the kernel data at `manifest.release_commit`, rebuilds to the same `release_hash`, and is immutable (NV-16).

The candidate is nevertheless rejected because 17 freshly authored held-out scenarios expose one CRITICAL, two HIGH and several MEDIUM defects that the repair did not touch and that the previous held-out set did not cover:

1. **CRITICAL — Human Decision Gates do not actually gate CIT approval.** `cit approve --method human` succeeds on a gate that was presented but never answered, and on a gate the human answered **B (decline)**; the declined CIT is then executed and its mutation manifest is written to disk. An L3 agent role (`change-controller`) can do this, and a decision record with `human_approved: true` is fabricated in the process (NV-01). The framework-update path implements the rule correctly (NV-13), so this is a CIT-specific gap in the very mechanism INV-008 and INV-011 protect.
2. **HIGH — Project overlay silently overrides SECURITY and AUTHORITY policy.** `PROJECT_POLICY.policy_overrides` lowered `authority_levels_required.create_task` to L0 (an L0 auditor then created tasks) and emptied `SECURITY_POLICY.never_index_classes` (restricted customer content was indexed and retrievable) with no doctor/audit finding, no decision and no exception record — inverting the framework §21 hierarchy (NV-02).
3. **HIGH — Plugin descriptors are ungoverned executables.** A three-line YAML under `governance/project/plugins/` with an arbitrary command is discovered, never validated against the shipped `plugin-descriptor` schema, never registered, pinned, health-checked or permission-scoped, and is executed by an L0 role via `gov capabilities invoke` and via `gov rebuild-memory` once pinned (NV-04).
4. **MEDIUM — Version-transition provenance and migration completeness.** With a project genuinely created by the 4.1.2 binary, `gov update` to 4.1.3 and rollback work mechanically (overlay preserved, `spec/` untouched, machine-B rebuild identical, rollback byte-for-byte), but `framework.lock.release_commit` records the *consumer's* HEAD instead of the release commit on every install path, `source` becomes an absolute machine path after update, the held-out regression file is lexically indexed on upgraded projects because `M-4.1.2-4.1.3` performs none of the overlay tightening its description claims, and rollback leaves no ledger entry (NV-03, NV-08, NV-19).
5. **MEDIUM — Mutation scope at close is self-attested** (NV-05), **a moved governed record disappears from the index for one incremental rebuild** (NV-07), **the authoritative interface record API-0001 contradicts the implementation** (it still promises a silent built-in fallback for a failing embed plugin that C1 deliberately removed), and **KERNEL.yaml carries a duplicate mapping key** (LOW, NV-09).

HV-08b is **not** a release blocker (§5): the governed benchmark/selection mechanism was proven end-to-end here with a genuinely paraphrase-capable candidate that neither party shipped (NV-06), and framework §14.3 forbids hard-coding a model in the kernel.

None of the new defects needs an architectural rewrite; the repair delta (§12) is bounded and each item has an acceptance test in `harness_v2.py`.

## 1. Reproduction of builder evidence (independent rerun, clean build)

| Suite | Builder claim (`docs/EVIDENCE.md`) | This session |
|---|---|---|
| `cargo clean && cargo build --release` | exit 0 | exit 0, 0 warnings, 36.8 s (`evidence/clean-release-build.log`); binary links libc/libm/libgcc only |
| Unit tests (gov-runtime) | 14 passed | 14 passed (`builder-suite-rerun/unit-tests.log`) |
| Certification harness | 35 passed | 35 passed, 49.6 s (`builder-suite-rerun/certification-tests.log`) |
| Python plugin tests | 4 passed | 4 passed |
| Clippy | RAN, 5 style warnings, 0 errors | RAN, exit 0, 5 warnings (`sort_by_key` ×2, `&mut Vec` param, complex type, large enum variant), 0 errors |
| rustfmt --check | divergent (advisory) | 756 `Diff in` lines, exit 1 — the repair was not formatted |
| `gov release verify release/releases/4.1.3` | — | ok: 117 files, none modified/missing/added, release_hash matches kernel |
| Payload vs `framework/`+`migrations/`+`tools/` at HEAD | — | identical; also identical to the tree at `manifest.release_commit` 78f6853, which is an ancestor of 26ab5b6 (NV-16) |
| First verifier's artefacts untouched by the builder | claimed | confirmed: `git diff 9563192..78f6853 -- release/verification/4.1.2/heldout release/releases/4.1.2` is empty; only `heldout-rerun/` was added |

## 2. Previous held-out harness — unchanged regression rerun

Harness `release/verification/4.1.2/heldout/harness.py` executed unchanged (hash identical to commit 9563192) against the rebuilt candidate: **36 PASS / 1 FAIL / 1 INFO / 0 ERROR** (`heldout-prev-rerun/SUMMARY.md`, `results.json`, `run-full.log`), matching the builder's rerun. Original verifier run: 12 / 25 / 1. The only FAIL is HV-08b; HV-08 metrics: recall@k 0.833, MRR 0.715, stale 0.0, superseded 0.0, forbidden 0. No prior test was changed, weakened or bypassed.

## 3. Previous-Finding Repair Matrix (CRITICAL/HIGH of the 4.1.2 rejection)

| ID | Previous root cause | Claimed repair | Independently observed (source + behaviour) | Original held-out | New independent test | Regression risk | Verdict |
|---|---|---|---|---|---|---|---|
| C1 query embedder hard-coded | semantic route called the builtin hasher | `memory/embedder.rs` `EmbedSpec`/`Embedder::resolve`/`for_query`; `EMBEDDER_UNAVAILABLE`/`MISMATCH`/`BAD_OUTPUT`; live spec in `meta.embedder` | `retrieval/mod.rs` semantic route calls `for_query(p, db)` which requires live == policy pin and resolves builtin/plugin with no fallback; heterogeneous vector dimension is refused; `context::compile`, `run_heldout_with`, benchmark inherit | HV-01 PASS, HV-07 PASS | NV-06 PASS (plugin-built index queried with the plugin; plugin removed → `EMBEDDER_UNAVAILABLE`); NV-12 PASS (`gov continue`/`context compile` fail closed on pin change) | low | **REPAIRED** |
| C2 plugin host deadlock | `try_wait` loop before reading stdout | stdin writer thread, stdout/stderr drain threads, watchdog + process-group kill, typed errors | `capabilities/host.rs` as described; 4 unit tests (1.2 MB response, 600 KB request + stderr flood, timeout kill < 5 s, bad JSON/protocol) pass here | HV-36 PASS (< 1 s both sizes) | NV-06 (512-d plugin over 489 chunks in batches of 256, 241 ms index) and NV-17 (plugin logging 307 texts) exercised the host at scale | low (timing-sensitive unit test noted by builder; did not flake in this session) | **REPAIRED** |
| H1 mixed-embedder index after pin change | incremental builds never compared pins | `expected_pins`/`live_pins`/`pin_differences`, escalation to staged full rebuild, `Freshness.pin_mismatch`, doctor D025, `INDEX_PIN_MISMATCH` at close | confirmed in `indexer.rs`, `manifest.rs`, `doctor.rs`, `tasks.rs`; note `pin_differences` excludes the reranker (reranking is query-time; `RERANKER_MISMATCH` covers it, NV-10) | HV-07 PASS | NV-12 PASS; NV-03 (4.1.2 index opened by 4.1.3: D010/D025 report pin mismatch, update performs a full rebuild) | low | **REPAIRED** |
| H2 claims lost on rebuild | claims rows in `state.db` | `memory/claims.rs` `ClaimsStore` at `.governance-runtime/claims.db`, D026 | confirmed; `rebuild` never touches `claims.db`; `control.json` separate | HV-05 PASS | — (covered by HV-05; store inspected) | low; claims remain per-machine (acceptable) | **REPAIRED** |
| H3 authority levels unenforced | policy data only | `authority.rs` `require()` on every mutating path; `AUTHORITY_POLICY.authority_levels_required` completed | confirmed on tasks, CIT, gates, controls, checkpoints, handoffs, kernel, update, tools, adoption, upstream, benchmark/select | HV-03 PASS | NV-01(c): L3 `change-controller` passes the level check but bypasses the *gate answer* (separate defect); NV-02: the required levels can be lowered by the project overlay (new HIGH); NV-04: L0 can still execute arbitrary plugin commands (new HIGH) | medium: enforcement exists but is undermined by overlay override and by role self-declaration (`--role human` is unauthenticated by design) | **REPAIRED as specified; new adjacent gaps** |
| H4 mutation scope at close | `files_changed` unchecked | `scope_violations()` → `MUTATION_SCOPE_VIOLATION` | confirmed (forbidden, kernel, contract-prohibited, outside allowed unless CIT-governed) | HV-04 PASS | NV-05 FAIL (MEDIUM): the check trusts the worker's list; `git status` showed an omitted out-of-scope modification and close succeeded; the checkpoint copies the self-reported list | medium | **REPAIRED as specified; self-attestation gap** |
| H5 restricted classes indexed | only `secret` honoured | `SensitivityRules` in `paths.rs`, namespace/role filter, suite CRITICAL finding, export gate | confirmed; restricted paths excluded with reason `sensitivity:<class>`; dangling imports recorded as `excluded:` | HV-09 PASS, HV-21 PASS | NV-17 PASS (no secret/restricted text reaches a plugin); NV-02 FAIL: the rule set is read from the *effective* policy, which the project overlay can empty | high if overlay override is not closed | **REPAIRED; nullified by NV-02** |
| H6 destructive migration by flag | `--gate-answer` counted as answer | A4 creates HDG records; A6 executes only presented+answered-A; `--gate-answer` ignored | confirmed in `adopt.rs` (`ensure_destructive_gates`, `answered_destructive` → `is_answered_yes`) | HV-29 PASS, HV-31 PASS | control NV-13 PASS for the update gate; CIT gate (NV-01) is the path that remained wrong | low for adoption | **REPAIRED** |
| H7 no reranker hook / no benchmark | reranker pin unread; embedder hard-coded | `Reranker::resolve/rerank` between fusion and filtering; `gov memory benchmark`/`select`; `regression.min_queries`; richer starter set | confirmed in `retrieval/mod.rs`, `memory/benchmark.rs`, `heldout.rs` | HV-02 PASS, HV-20 PASS | NV-10 PASS (scores govern order and are exposed per hit; `RERANKER_MISMATCH` before rebuild); NV-06 PASS (3-candidate benchmark → research record → decision with alternatives → pin → rebuild → paraphrase recall 1.0) | low; `select` derives `human_approved` from `--by != "agent"` (LOW) | **REPAIRED** |

MEDIUM/LOW repairs (M1–M16, L1–L9) were spot-checked through the unchanged harness (all corresponding HV scenarios PASS) and by source inspection; exceptions found: M6 (logical lock `source`) is implemented for `init` only — `update --apply` writes an absolute path (NV-03); L5 (held-out file not lexically indexed) is delivered by the overlay *template* only and therefore not for upgraded projects (NV-03/NV-19).

## 4. New Held-Out Test Register (authored in this session; unknown to builder and first verifier)

Harness: `release/verification/4.1.3/heldout-new/harness_v2.py`; results `results.json`; log `run-full.log`. Totals: **6 PASS / 9 FAIL / 0 ERROR**.

| ID | Requirement challenged | Attack / failure scenario | Expected | Actual | Evidence | Severity on failure |
|---|---|---|---|---|---|---|
| NV-01 | INV-008, INV-011, framework §47.2/§52: CIT approval rests on a presented **and answered** gate; a decline stops the CIT | (a) present the CIT's gate, never answer, `cit approve --method human`; (b) answer **B**, then approve + execute; (c) repeat (a) as `change-controller` (L3 agent) | all refused | (a) approved, decision record written with `human_approved: true`, gate still PRESENTED; (b) CIT stays SIMULATED after decline, approve ok, **execute ok, manifest file written**; (c) L3 agent approved | `results.json` NV-01 | **CRITICAL** |
| NV-02 | framework §21 hierarchy (SECURITY+AUTHORITY above PROJECT POLICY), INV-006 | overlay `policy_overrides` sets `create_task`/`execute_cit`/`install_kernel` to L0 and `never_index_classes: []`; L0 auditor creates a task; restricted-classified file indexed? | overrides of security/authority refused or flagged; L0 denied; restricted excluded | D007 "13 policies loaded, 5 overrides", audit DEGRADED with **no** finding about the overrides; L0 created the task; restricted file indexed with `sensitivity=restricted` and retrievable | NV-02 | **HIGH** |
| NV-03 | protocol §7.4/§12, framework §82/§83, INV-013: genuine 4.1.2 → 4.1.3 update, multi-machine, rollback, lock/provenance | project created and populated by the **4.1.2 binary**; 4.1.3 binary: doctor, `update --check/--apply` (gate flow), clone+rebuild on machine B, 4.1.2 binary view of the upgraded project, `--rollback`, second rollback | coherent lock/provenance; overlay + spec preserved; leak-free index; ledger complete | applied 4.1.2→4.1.3 via `M-4.1.2-4.1.3` after presented+answered gate; `--approve` alone refused; overlay override preserved; `spec/` unchanged; kernel verify ok; index `4.1.3-idx2` porter tokenizer; machine-B manifest hash equal; rollback restores lock and overlay byte-for-byte, kernel ok, second rollback re-applies silently. **Defects:** `lock.release_commit` = consumer HEAD (≠ `78f6853`); `lock.source` = absolute path after update; `governance/tests/memory/heldout.yaml` lexically indexed after update (overlay rule unchanged, template tightened); no rollback ledger entry | NV-03 | MEDIUM (four findings) |
| NV-04 | framework §28–30, §32, TOOL_PERMISSIONS least authority: executable capabilities are registered, pinned, health-checked, permission-scoped | minimal descriptor `{plugin_id, capability, command}` → `capabilities invoke` as L0 auditor; pin it and `rebuild-memory` as L0 | refused / gated | schema accepts the minimal descriptor; core discovers it; **L0 executed it** (marker written) both via invoke and via rebuild; not in tool registry; `tools resolve` reports a gap; no doctor/audit finding; `plugin-descriptor.schema.json` is unreferenced in `runtime/src` | NV-04 | **HIGH** |
| NV-05 | framework §25/§42 mutation manifests; H4 | worker modifies `src/lib.rs` outside `allowed_paths: docs/**`, reports only `docs/notes.md`, closes | close refuses (working tree contradicts report) | close succeeded; checkpoint copied the self-reported list | NV-05 | MEDIUM |
| NV-06 | framework §14.3 / directive §3: governed benchmark-and-selection is sufficient to obtain paraphrase retrieval | adopted brownfield, 10-query verifier set with two token-overlap-free paraphrases; a synonym-aware embed plugin authored here; `memory benchmark` (3 candidates, `--record`), `memory select`, `memory verify`, plugin removal | paraphrase recall 1.0 after selection, decision with alternatives, no fallback | baseline semantic recall 0.5 → candidate 1.0 (recall@k 0.9→1.0, MRR 0.75→0.84); `RES-0001` with 3 rows (recall, MRR, precision, stale/superseded, symbol recall, latency, index cost); decision `D-0003` chosen `plugin:syn-embed:512`, 3 alternatives; live index `syn-embed`; `memory verify` PASS; plugin removed → `EMBEDDER_UNAVAILABLE` | NV-06 | (PASS) |
| NV-07 | framework §13 incremental indexing; deterministic memory | `git mv spec/decisions/D-0001.yaml spec/decisions/2026/`, `rebuild-memory --incremental` | record present at new path | first incremental: "duplicate record id … first occurrence kept", `removed: 1, indexed: 0` → record absent, structured query misses; freshness not fresh; second incremental restores | NV-07 | MEDIUM |
| NV-08 | protocol §4/§8, framework §80: `framework.lock` identifies the installed release | init from release dir, from canonical root, from embedded payload; compare `release_commit` | equals `manifest.release_commit` | equals the **project's** HEAD on all three paths; `source` labels correct at init (`release:`/`source:`/`embedded:`); `release_hash` correct | NV-08 | MEDIUM |
| NV-09 | kernel data hygiene | strict YAML load of `KERNEL.yaml` | valid | duplicate key `schema_versions.release-manifest` (lines 26 and 32; 1.0.0 then 1.1.0); strict loaders reject; manifests agree with last-wins | NV-09 | LOW |
| NV-10 | H7 follow-through: reranker scores govern order | rerank plugin scoring one artefact 10.0 | top-1 changes, score exposed | PASS; `RERANKER_MISMATCH` when pinned before rebuild | NV-10 | — |
| NV-12 | C1/H1 follow-through on all consumers | pin change without rebuild → `gov continue`, `context compile`, `status` | fail closed; status works | PASS (`EMBEDDER_MISMATCH` ×2, status ok, freshness pin_mismatch) | NV-12 | — |
| NV-13 | control for NV-01 on the update path | update gate answered B → `--apply --approve` | not applied | PASS (`applied: false`, lock stays 4.1.2) | NV-13 | — |
| NV-16 | protocol §8, framework §75D: release identity, reproducibility, immutability | verify; compare payload with tree at `release_commit`; rebuild 4.1.3 into a temp dir; rebuild into `release/` | all consistent; second build refused | PASS: identical files, same `release_hash` and `file_hashes`, `RELEASE_IMMUTABLE`, repo untouched | NV-16 | — |
| NV-17 | API-0001 invariant, framework §16/§72: plugins never receive secret/restricted content | logging embed plugin; secret path, secret content in product source, restricted-classified file | none of the markers reach the plugin | PASS (0 leaks; 3 exclusions recorded) | NV-17 | — |
| NV-19 | migration record integrity (protocol §8 "supported migration paths", framework §75D) | compare `M-4.1.2-4.1.3` description/release notes with its `operations` | consistent | description claims the contract rule is tightened; operations: note, set_lock_field, require_index_rebuild, regenerate_adapters — **no overlay operation**; template changed between releases | NV-19 | MEDIUM |

## 5. HV-08b — independent assessment

**Question.** Is the failure of token-overlap-free paraphrase retrieval with the pinned baseline embedder a release blocker, or is the governed benchmark/selection mechanism sufficient?

**Architecture and governing text.** Framework §14.3: "Do not permanently hard-code a particular embedding or reranking model into the constitutional standard. For each repository/environment, benchmark candidate … models against repository-specific held-out retrieval queries … The chosen embedding and reranker versions are pinned in the memory/index manifest and may be changed only through a measured migration." §11.3 requires semantic memory as a class; §17 requires the memory to be tested with Recall@K, MRR, precision, stale/superseded rates, symbol recall, latency. D-0002 §4 makes embedding model, runtime, index store and reranker replaceable concerns. Nothing in the governing documents requires the kernel to ship a paraphrase-capable model; they require the *mechanism* and the *pins*.

**Evidence.** (1) The mechanism exists and is executable: `gov memory benchmark` re-indexes each candidate into an isolated database and computes recall@k, MRR, precision@k, stale/superseded hit rates, forbidden violations, symbol recall, query latency, index cost and vector count per candidate; `--record` writes a research record; `gov memory select` writes a decision record listing the benchmarked alternatives, pins the choice in the overlay and performs a full rebuild; `regression.min_queries` prevents an unmeasured set from being green. (2) It is sufficient in practice: NV-06 authored a paraphrase-capable candidate that neither party shipped, benchmarked it against `current` and `builtin:128`, selected it through the decision path and obtained paraphrase recall 1.0 (both V-SEM queries), overall recall@k 1.0 and MRR 0.84 on the adopted brownfield, with no silent fallback when the plugin is removed. (3) The failure is by construction: the hashed n-gram baseline has no paraphrase capability, and the release notes say so. (4) What is still missing is *evidence in the canonical repository itself*: no benchmark research record or selection decision exists for the Governance OS's own governance memory, and no credible paraphrase-capable candidate (local or remote, behind API-0001) is shipped or referenced, so an adopter's first `gov memory benchmark` has only `current`/`builtin` variants to compare unless they write a plugin.

**Decision.** HV-08b is **not** a release blocker. The selection mechanism satisfies §14.3 and was proven end-to-end here. The gap is recorded as **MEDIUM (M-B1)**: before certification the canonical repository should either ship at least one credible paraphrase-capable embed plugin (a small local model behind API-0001) or record, as a decision with a benchmark research record, why none is shipped and which candidate classes adopters are expected to evaluate; the first verifier's harness note "no comparative benchmark mechanism exists" is now factually stale and should not be read as a current finding.

## 6. Version / Provenance Matrix

| Item | Observed | Verdict |
|---|---|---|
| Branch | `release/4.1.2-rc1` (only branch besides `main`; `main` = initial commit `5118d40`; **no tags**) carrying the 4.1.2 release, its rejection, the repair and the 4.1.3 payload | naming misleading for a 4.1.3 payload; not functionally incoherent (see Q27) |
| Candidate commit | `26ab5b6` = repair code `78f6853` + `release/releases/4.1.3/` + a 2-line repair-report edit | consistent |
| Framework version | `Cargo.toml` 4.1.3; `lib.rs` VERSION/CLI/RUNTIME 4.1.3, INDEX 4.1.3-idx2; `gov version` matches | consistent |
| Kernel version | `framework/KERNEL.yaml` 4.1.3, `framework_revision: "4.1.2"` (the governing document revision), `supported_from_versions: [4.1.1, 4.1.2]`; duplicate `release-manifest` key (NV-09) | consistent apart from LOW hygiene defect |
| Release payload | `release/releases/4.1.3`: 117 files; `release_hash` = kernel `payload_hash`; equals kernel data at `release_commit 78f6853` and at HEAD; rebuild reproduces hash and file hashes; second build refused (NV-16) | **sound** |
| Release manifest | schema `release-manifest` 1.1.0 (adds READY_FOR_INDEPENDENT_REVERIFICATION); yaml == json; certification `READY_FOR_INDEPENDENT_REVERIFICATION`, verifier empty | consistent; **must be set to REJECTED by the release owner** (this session was not permitted to edit it) |
| Migration `M-4.1.2-4.1.3` | schema-valid; `from 4.1.2 → to 4.1.3`, non-breaking, no human gate, all indexes rebuilt; operations: note, set_lock_field (1.0.0, unchanged), require_index_rebuild, regenerate_adapters; **no overlay operation although the description and the changed overlay template imply one** (NV-19); chain 4.1.1→4.1.2→4.1.3 resolved by the builder test; 4.1.2→4.1.3 resolved and applied here (NV-03) | valid and reversible; **incomplete** (MEDIUM) |
| `framework.lock` | `version`, `release_hash`, `kernel_manifest_hash`, `cli_version`, `schema_versions`, `lock_schema_version` correct after init, update and rollback; `release_commit` = consumer HEAD on all paths (NV-08); `source` logical at init, absolute path after update (NV-03) | **two provenance defects** (MEDIUM) |
| Update semantics | CIT-P check (radius R3, index rebuild, uncertified → gate); `--approve` alone refused; presented+answered gate → kernel replaced, migration applied, overlay preserved (`OVERLAY_CLOBBERED` guard), adapters regenerated, full rebuild, doctor + suite, ledger "committed"; failure → automatic rollback | sound |
| Rollback semantics | restores kernel, overlay, generated, lock from `.governance-runtime/update/<target>/` byte-for-byte; full rebuild; **no ledger entry; second rollback silently re-applies the same snapshot; snapshot never invalidated** | sound mechanically; provenance gap (LOW) |
| Release provenance | `release_commit` ancestor of HEAD; commit messages record verifier → repair → payload; builder did not modify verifier artefacts | sound |
| Repaired RC → 4.1.3 | kernel payload changed (policies, roles, template, schemas, registry, enforcement map, migration) ⇒ PATCH bump per §75D and `docs/RELEASE.md`; 4.1.2 stays immutable and REJECTED | **coherent and correctly represented** |

## 7. Answers to the mandatory questions

1. **Substantially complete relative to the governing documents?** Closer than 4.1.2 but not yet: control plane, repository intelligence, adoption, rebuildable multi-layer memory, release mechanics, model routing, readiness and DAG are PRESENT_AND_SUBSTANTIAL; human-gate integrity for CIT (CRITICAL), policy-hierarchy enforcement (HIGH) and capability governance for plugins (HIGH) are PARTIAL; MCP transport, lesson clustering evidence and a shipped paraphrase-capable candidate remain deferred/absent with records.
2. **PARTIAL/ABSENT/UNCLEAR pillars:** §8. PARTIAL: authority/policy engine (overlay override), Human Decision Gate handling (CIT path), tool/capability registry (plugins), mutation manifests (self-attested), framework.lock provenance, migration completeness, incremental indexing after relocation, temporal memory (no git lineage), code intelligence (regex baseline + plugins), token metrics. ABSENT: MCP transport (D-0004, documented), shipped paraphrase-capable embedder, benchmark evidence for the canonical repository's own memory.
3. **Deterministic core language:** Rust (`runtime/` lib 7.5k dense lines ≈ 590 KB, `cli/` binary; rusqlite bundled SQLite+FTS5, serde, jsonschema, regex, walkdir, sha2, chrono, uuid, clap, libc). Kernel payload embedded at build time.
4. **Rust-first exceptions:** none in the deterministic core. Python plugins (python-ast code intelligence, reference embedder) and a bash embedder sit behind API-0001 with the D-0002 rationale. Justified.
5. **Core without Python?** Yes (HV-25 PASS; `ldd` libc-only; builder arch test reproduced). Python is used only by optional plugins and by the verifier harnesses.
6. **Non-Rust / mixed projects?** Yes: Python+TypeScript brownfield and migration fixtures, Go project (HV-13), language-tagged registry resolves cargo/pytest/npm/go/ctest/make/mvn per detected ecosystem (HV-06). No architectural change needed.
7. **Structured-state DB:** SQLite (rusqlite, bundled, WAL, FTS5) at `.governance-runtime/state.db`; claims in a separate `claims.db`; control in `control.json`. Chosen for zero dependency, single file, offline determinism (TOOL-SQLITE-001, ARCH-0001). Adequate for a derived store.
8. **Lexical search:** FTS5 bm25 with `porter unicode61` (pinned in MEMORY_POLICY.lexical.tokenizer, part of the index pin). Morphological paraphrase now succeeds (V-SEM-2).
9. **Vector/index:** SQLite `vectors` (JSON text), brute-force cosine, no ANN; acceptable at fixture scale; not abstracted behind a trait.
10. **Graph:** SQLite `edges` with 20 relation types; record-field relations, IMPORTS, TESTS, CALLS (now materialised), SUPERSEDES; BFS neighbours/impact.
11. **Code intelligence:** built-in regex extractor (9 language families) + `code_intel` plugins (python-ast) with recorded degradation; bare identifiers route to symbols; no LSP/SCIP (rust-analyzer registered as `proposed`).
12. **Embedding model:** built-in `hashed-ngram` v1 512-d baseline; selection per repository via `gov memory benchmark/select` (proven NV-06); no paraphrase-capable candidate shipped (M-B1).
13. **Reranker:** none pinned by default; `rerank` plugins wired between fusion and filtering (NV-10).
14. **Alternatives benchmarked:** by the builder, only builtin variants (`current`, `builtin:64`, `plugin:gov-builtin-embed:32`); by this session, `current`, `builtin:128` and a synonym-aware plugin (NV-06). No benchmark recorded for the canonical repository's own memory.
15. **Retrieval metrics:** first verifier's set: recall@k 0.833, MRR 0.715, stale 0, superseded 0. This session's set: baseline 0.9 / 0.75 / precision 0.42 / symbol recall 1.0 / 2.8 ms; selected candidate 1.0 / 0.84 / 0.43 / 1.0 / 15 ms (index 241 ms).
16. **Generative/orchestrator routing:** tier (T0–T3) and reasoning floors from task class, task fields, role defaults, impact radius, overlay overrides; candidates only from `MODEL_ROUTING_OVERRIDES.yaml`; cheapest-meeting-tier; evidence ledger with budget gates. Kernel is vendor-free. Adequate.
17. **Pinned and replaceable?** Embedder/reranker: pinned in overlay + index manifest, replaceable, fail-closed — yes (C1/H7 repaired). Tools: registry descriptors with `version_pin`. Plugins: **not pinned/approved** (NV-04). Model routing: overlay, replaceable.
18. **Delete and rebuild?** Yes: HV-12, HV-30, NV-03 machine B (manifest hash identical after update). Claims/control survive rebuild (H2).
19. **Fresh agent reconstruction?** Yes: `status` (≤25 reads), `continue` (hash-stable packet with authority layers, conflicting-decision flag, deterministic truncation); fails closed on pin mismatch (NV-12).
20. **Top gaps preventing release:** (1) CIT approval/execution without an answered gate, and despite a decline (NV-01); (2) project overlay overriding SECURITY/AUTHORITY policy (NV-02); (3) ungoverned plugin execution (NV-04); (4) lock/migration provenance defects (NV-03/08/19); (5) self-attested mutation scope (NV-05); (6) record loss on incremental rebuild after relocation (NV-07); (7) API-0001 contradicting the no-fallback implementation.
21. **Previous CRITICAL/HIGH genuinely repaired?** Yes, all nine (§3), at the root cause; H3/H5 are nullified in effect by the new overlay-override defect and H4 remains self-attested.
22. **New regressions or contradictions introduced?** Yes: (a) API-0001 (AUTHORITATIVE interface), `capabilities/PROTOCOL.md` and `fixtures/failure-injection/README.md` still state that a failing embed plugin degrades to the built-in fallback, contradicting the deliberate no-fallback design — a code/spec disagreement inside the canonical repository; (b) `update --apply` regressed M6 by writing an absolute `source`; (c) `KERNEL.yaml` gained a duplicate key; (d) `docs/FIXTURES.md`/update README still describe 4.1.1→4.1.2.
23. **Original held-out tests pass unchanged?** 36/37 (HV-08b residual) — yes.
24. **New tests added:** NV-01…NV-19 (17 scenarios, §4/§13).
25. **HV-08b blocker?** No (§5); MEDIUM M-B1.
26. **4.1.2 → 4.1.3 transition internally correct?** The payload, manifests, version constants, migration chain and update/rollback mechanics are coherent and were exercised with genuine 4.1.2 state (NV-03). Incorrect details: `framework.lock.release_commit`, `source` after update, migration operations not matching the migration's own description, no rollback ledger entry.
27. **Branch `release/4.1.2-rc1` for a 4.1.3 payload?** Provenance is traceable through commit messages and `manifest.release_commit`, so identity is not compromised, but the name is misleading and there are no tags anywhere. Before certification: tag the candidate (`v4.1.3-rc1` or equivalent at `26ab5b6`/its repair) and either rename or branch to `release/4.1.3-rc1`; record the branch/tag in the manifest or release notes. MEDIUM, must be corrected before Prompt 3, not by itself a rejection cause.
28. **`M-4.1.2-4.1.3` valid, reversible, exercised?** Schema-valid and reversible (rollback verified byte-for-byte); exercised via the builder's 4.1.1→4.1.3 chain and here with real 4.1.2 state; **incomplete**: it does not perform the contract tightening its description claims, so upgraded projects keep indexing the held-out file (NV-19, NV-03).
29. **`framework.lock` across 4.1.2 → 4.1.3?** Version, hashes, schema versions and lock schema version are right through update and rollback; `release_commit` is wrong (consumer HEAD) and `source` is inconsistent between init and update (NV-03/NV-08).
30. **Commit `26ab5b6` suitable for Prompt 3?** **No.**

## 8. Architecture Completeness Matrix (delta from the 4.1.2 report; unchanged rows are summarised)

Legend: P&S = PRESENT_AND_SUBSTANTIAL.

### A. Governance / deterministic control plane
| Requirement | Status | Implementation | Evidence | Notes | Sev |
|---|---|---|---|---|---|
| Deterministic core; Rust-first; justified exceptions | P&S | `runtime/`, `cli/`, D-0002, ARCH-0001 | clean build, `ldd`, HV-25 | — | — |
| Portable `gov` CLI | P&S | embedded kernel (`build.rs`), `GOV_KERNEL_CACHE`, logical `source` at init | HV-24, NV-08 | `update` writes absolute `source` (NV-03) | LOW |
| Authority / policy engine | PARTIAL | `authority.rs`, `policy.rs`, ENFORCEMENT_MAP, `policy_coverage.rs` | HV-03; NV-02 FAIL | levels enforced but overridable from the project overlay; role is self-declared (`--role`) | HIGH |
| Constitution / policy precedence | PARTIAL | context `authority_layers`, retrieval filters | HV-15; NV-02 | §21 hierarchy not enforced at policy-load time | HIGH |
| Kernel vs overlay separation; `framework.lock` | P&S / PARTIAL | `kernel.rs`, `lock.rs`, D003/D004 | NV-16; NV-08 | lock `release_commit` provenance wrong | MEDIUM |
| Checkpoint / recovery | P&S | `checkpoints.rs`, `recovery.rs`, `before_handoff` automatic | HV-19; failure-injection | — | — |
| CIT-P / CIT-E | PARTIAL | `cit/mod.rs` (auto-simulation, secret redaction, snapshots, rollback) | HV-10/14/17/34 PASS; **NV-01 FAIL** | approval ignores the gate's answer; execute ignores option B | CRITICAL |
| Dynamic task DAG; readiness gating; TEST_POLICY prerequisites | P&S | `dag.rs`, `readiness.rs` | HV-22, HV-39 | — | — |
| Human Decision Gate handling | PARTIAL | `gates.rs` (present/answer, agent_resolvable_when), update/adoption/tool/budget gates | HV-11/29 PASS, NV-13 PASS; NV-01 FAIL | correct everywhere except CIT approve/execute | CRITICAL |
| Model routing / reasoning tiers | P&S | `routing.rs`, MODEL_ROUTING_POLICY, budget gates | greenfield fixture | — | — |
| Tool / capability / permission registry | PARTIAL | `tools.rs`, language-tagged TOOLS.yaml, install conditions → gate | HV-06 PASS; **NV-04 FAIL** | plugins bypass registry, approval, pin, health, permissions, schema | HIGH |
| Release / install / update / rollback | P&S | `release.rs`, `update.rs`, `kernel.rs` | NV-03, NV-16 | rollback ledger/idempotence (LOW); migration completeness (MEDIUM) | MEDIUM |
| Immutable release manifest / hashes / provenance | P&S | `release/releases/4.1.3` | NV-16 | — | — |
| Observability / execution evidence | PARTIAL | `observability.rs` (spans, retrieval, rework, cost, network budget, routing report) | greenfield | no token measurement | LOW |

### B. Repository intelligence and adoption / migration
All P&S as in the 4.1.2 report (inventory, classification, authority classification, path map with populated imports/references/consumers, contract, migration engine with TS/Python import rewrite, independent test hooks, byte-identical batch rollback, legacy retirement and extraction, `gov init`, `gov adopt` with destructive gate records, `gov update`, native-layout preservation). Dependency-aware batching remains by protocol batch order (PARTIAL, MEDIUM, unchanged).

### C. Development Knowledge Fabric / memory
| Requirement | Status | Notes | Sev |
|---|---|---|---|
| Git records as truth; SQLite derived state; claims/control outside the rebuilt store | P&S | H2 verified | — |
| Lexical FTS/BM25 (porter) | P&S | pinned tokenizer | — |
| Semantic / vector retrieval | P&S (mechanism) / PARTIAL (shipped candidate) | C1/H1/H7 repaired; NV-06/10/12 PASS; baseline cannot paraphrase; no shipped stronger candidate | MEDIUM (M-B1) |
| Graph relationships incl. CALLS | P&S | HV-23 | — |
| Temporal / supersession | PARTIAL | `superseded_by`, conflict flagging; no git lineage per record | MEDIUM (unchanged) |
| Episodic / failure / working / capability memory | P&S | telemetry, reports, lessons, packets, `meta.capability.*` | — |
| Code intelligence | PARTIAL | regex baseline + AST plugin; no LSP/references | MEDIUM (unchanged) |
| Retrieval router; exact/lexical/semantic/graph/symbol routes; fusion; parent-child; graph expansion; reranking; authority + namespace filtering; provenance; stale/superseded filtering | P&S | HV-08, HV-21, HV-33, NV-10 | — |
| Incremental indexing and freshness | PARTIAL | pin-aware escalation works (H1); relocated record lost for one build (NV-07) | MEDIUM |
| Context compiler; bounded context; duplicate suppression; contradictions flagged | P&S | HV-15, NV-12 | — |
| Rebuildability; deletion-and-rebuild tests | P&S | HV-12, HV-30, NV-03 | — |
| Retrieval regression / golden queries; Recall@K, MRR, precision, stale-hit | P&S | starter set at init, `min_queries` UNMEASURED, benchmark metrics | — |
| Latency / context-size / token metrics | PARTIAL | latency and chars; no tokens | LOW |

### D. Memory component separation
Embedding model, inference runtime, vector store, lexical engine, graph, code intelligence, reranker, router, generative LLM, context compiler: all separated and individually pinned; embedder/reranker replaceable and fail-closed (C1/C2/H7 verified; NV-06/10/12/17). Vector/lexical/graph stores are fixed to SQLite by code (acceptable, unchanged). **No constitutional provider dependency.** P&S.

### E. Rust-first core / polyglot independence
P&S across the board (core without Python, language-tagged registry, Rust/Python/TypeScript/Go governed fixtures, mixed repositories, language-native tooling table). rust-analyzer/LSP resolution remains `proposed` (MEDIUM, unchanged).

### F. Agent organisation / orchestration
| Requirement | Status | Notes | Sev |
|---|---|---|---|
| Role separation; authority levels | PARTIAL | levels enforced (H3) but overlay-overridable (NV-02) and role self-declared | HIGH |
| Task contracts; typed results; handoffs; INV-014 | P&S | — | — |
| Mutation manifests | PARTIAL | declared-list check only (NV-05) | MEDIUM |
| Worktree / claim collision controls | P&S | claims store survives rebuild; per machine | — |
| Checkpoint before handoff / close; fresh-session independence; continue while gates pending; durable promotion | P&S | HV-19/32, adoption independence gates | — |

### G. Tools / interfaces / extensibility
| Requirement | Status | Notes | Sev |
|---|---|---|---|
| Stable interfaces (API-0001/0002) | PARTIAL | API-0001 invariant text contradicts the no-fallback implementation | MEDIUM |
| MCP | ABSENT (deferred by D-0004, registry `planned`) | acceptable with record | — |
| A2A separation; CLI JSON contract; capability discovery | P&S | — | — |
| Tool registration / health / acquisition gate / version pinning | PARTIAL | tools yes; plugins no (NV-04) | HIGH |
| Secrets handling; plugin boundary | P&S | NV-17, HV-17/34 | — |
| Privilege / destructive-action gates | PARTIAL | NV-01, NV-04 | CRITICAL/HIGH |

### H. Model routing / reasoning policy — P&S (unchanged).

### I. Synthetic certification fixtures
Greenfield, dirty brownfield (all listed hazards present), migration, upstream, multi-machine, failure-injection: P&S. Framework-update fixture: P&S for 4.1.1→4.1.3 (stored synthetic payload, M16) but the real 4.1.2→4.1.3 path was exercised only by this session (NV-03) — add it (MEDIUM). Adapter conformance: PARTIAL (verbatim invariants + hashes; unchanged). Secrets/outbound negative controls: P&S.

### J. Security / safety / outbound
| Requirement | Status | Notes | Sev |
|---|---|---|---|
| Secret detection/exclusion; sensitive-path handling (restricted/confidential) | P&S / PARTIAL | H5 implemented; nullifiable by overlay override (NV-02) | HIGH |
| Outbound allowlist / default deny; upstream sanitisation; synthetic reproducer preference | P&S | HV-26, upstream fixture | — |
| Project/customer data separation from governance memory | P&S (mechanism) | namespaces × role groups; NV-17 | — |
| Destructive-action controls; privilege boundaries | PARTIAL | NV-01, NV-04 | CRITICAL/HIGH |
| Auditable security decisions | PARTIAL | override of security policy leaves no audit trail (NV-02) | HIGH |

### K. Learning / upstream — P&S except clustering/FCP evidence (implemented `gov lessons cluster` + schema; exercised by builder test only) and central release path lacking tags (MEDIUM).

### L. Observability / governance health — as 4.1.2 report plus policy-enforcement coverage family; token usage still ABSENT (LOW).

## 9. Model / Retrieval Selection Matrix

| Component | Selected | Version | Alternatives considered | Benchmark / evidence | Rationale recorded | Pinned | Replaceable | Privacy / locality | Verdict |
|---|---|---|---|---|---|---|---|---|---|
| Generative / orchestrator model | none in kernel (tier T3 floors) | n/a | overlay decides | routing evidence ledger + budget gates | MODEL_ROUTING_POLICY, ROLES.yaml | overlay | yes | provider-agnostic | ACCEPT |
| Specialist / worker tiers | T1/T2 by class | n/a | n/a | same | same | overlay | yes | same | ACCEPT |
| Embedding model | `hashed-ngram` v1 512-d builtin | 1 | builder: builtin variants; this session: synonym-aware plugin (NV-06) | `gov memory benchmark` rows (recall/MRR/precision/stale/superseded/symbol/latency/index cost); research record | MEMORY_POLICY, release notes, D-0002 §4 | index manifest + overlay | **yes, verified** | local | ACCEPT mechanism; MEDIUM: no shipped paraphrase-capable candidate, no benchmark for the canonical repo |
| Embedding inference runtime | in-process builtin / subprocess plugin (any language) | gov-capability/1 | — | host unit tests; NV-06/17 | API-0001 | plugin version in manifest | yes | local | ACCEPT (host repaired) |
| Vector store / index | SQLite `vectors`, brute-force cosine | 4.1.3-idx2 | none | — | ARCH-0001 | index_version pin | code change | local | ACCEPT with note (no ANN, no trait) |
| Lexical engine | FTS5 bm25 `porter unicode61` | bundled | unicode61 (previous) | V-SEM-2 morphological now passes | MEMORY_POLICY.lexical | yes (pin) | code change | local | ACCEPT |
| Graph implementation | SQLite `edges` + BFS | — | none | dangling/orphan checks; CALLS | ARCH-0001 | n/a | code change | local | ACCEPT |
| Reranker | none by default; `rerank` plugins | 0 | — | NV-10 (scores govern order) | MEMORY_POLICY.reranker | yes | yes | — | ACCEPT |
| Code-intelligence tooling | regex baseline + python-ast plugin; rust-analyzer `proposed` | 1.0.0 | LSP/SCIP not evaluated | HV-13/23/33 | ARCH-0001, RPT-0001 | plugin version | yes | local | PARTIAL (acceptable baseline) |
| Query-planning / rewrite LLM | none (T0 intent patterns) | — | — | HV-18 | COMMAND_CONTRACT | — | adapters may add | — | ACCEPT |

## 10. Structured state, context compiler, readiness, DAG (verified again)

- **SQLite:** schema idempotent (`init_schema_with(tokenizer)`), `PRAGMA integrity_check`, WAL, batched transactions (500), staged full rebuild with atomic swap, `excluded`/`meta`/`retrieval_log`/`capability` tables; claims and control outside the derived store; no DB-level migration system (acceptable: fully derived, `index_version` pinned). Vectors remain derived; authority resolved from record status/`superseded_by`. Defect: incremental path handling of relocated records (NV-07).
- **Context compiler:** ordered `authority_layers` (invariants → security/authority → project policy → decisions/spec → task/manifest → role/skill → retrieved → inference), `conflicting_decisions` flagged `UNKNOWN_OR_CONFLICTING`, deterministic truncation, hash-stable deterministic block, fails closed on pin mismatch. Sound.
- **Readiness:** 26 dimensions (all listed ones), cell states PRESENT/MISSING/PROVISIONAL/BLOCKED/N/A_WITH_REASON (schema-enforced, silent N/A rejected), gap tasks generated with declared classes and implementation tasks blocked until pre-implementation cells are PRESENT; implementation tasks without a feature gated by TEST_POLICY. Executable and enforceable.
- **DAG:** 23 task classes, dependencies, gates, cycles, longest chain, missing dependencies, replan; the 11-step research→validation chain (HV-22) reproduced. Sound.

## 11. Critical Gap Register

### CRITICAL
| ID | Gap | Evidence | Affected architecture | Risk | Required repair | Acceptance test |
|---|---|---|---|---|---|---|
| C-N1 | CIT approval with a presented-but-unanswered gate; approval and execution after the human answered B; fabricated `human_approved: true` decision; L3 agent can do it | NV-01 (a/b/c); `cit/mod.rs::approve` checks only "not ANSWERED and not presented"; `execute` checks only `gate_status == ANSWERED` | Human Decision Gates (INV-008), CIT (INV-011), authority precedence §2 (human decision first) | any L3+ agent can push human-gated changes through; a human "no" does not stop execution | `approve --method human` requires `gates::answered_option(gate) == Some("A")`; option B → CIT `REJECTED` (also from `gates::answer` when the gate carries a `cit`); `execute` re-checks option A; decision record created by `answer`, not by `approve`; `human_approved` only when the gate answer `by_kind == human` | `harness_v2.py NV01` → PASS (a, b, c all refused; CIT REJECTED after B) |

### HIGH
| ID | Gap | Evidence | Affected | Risk | Required repair | Acceptance test |
|---|---|---|---|---|---|---|
| H-N1 | Project overlay `policy_overrides` (and `PROJECT_EXCEPTIONS`) can override AUTHORITY_POLICY and SECURITY_POLICY silently | NV-02; `policy.rs::PolicySet::load` applies any `<POLICY>.<key>` | framework §21 hierarchy, INV-006, H3/H5 effectiveness | a repository (or an agent with overlay write access) disables authority levels and never-index classes with no record | refuse overrides/exceptions targeting AUTHORITY_POLICY, SECURITY_POLICY, `authority_levels_required.*`, `never_index_classes`, `never_export_classes` (constitutional layer); allow only via a kernel-declared allowlist of overridable keys; doctor D007 and `schema_invariants` report CRITICAL on any such override; every applied override recorded with its source | NV02 → PASS (override refused/flagged; L0 denied; restricted excluded) |
| H-N2 | Plugin descriptors are ungoverned executables | NV-04; `host.rs::discover` accepts any YAML with `plugin_id/capability/command`; `plugin-descriptor.schema.json` unreferenced; no `tools install` path; `invoke` unauthorised | framework §28–32, TOOL_PERMISSIONS, privilege boundaries | arbitrary command execution by any role through a tracked overlay file | validate descriptors against the schema (require `version`, `health`, `required_permission_classes`, `approved_roles`, `version_pin`/hash); register plugins through `tools install` conditions (or a `plugins install` equivalent with the same gate); `capabilities invoke` and pinned use require role permission (e.g. `EXEC_PLUGIN`) and the plugin's `approved_roles`; doctor check for unregistered/unpinned plugins; suite family finding | NV04 → PASS (minimal descriptor rejected; L0 invoke `AUTHORITY_DENIED`/permission error; registered plugin runs for approved roles) |

### MEDIUM
| ID | Gap | Evidence | Required repair | Acceptance |
|---|---|---|---|---|
| M-N1 | `framework.lock.release_commit` = consumer HEAD on every install path | NV-08, NV-03 (`init.rs`, `update.rs` pass `Project::git_commit()`) | write the release's commit: from `manifest.json` when installing from a release dir, from `KERNEL.yaml`/embedded metadata (add `release_commit` to KERNEL_MANIFEST at release build) otherwise; record the consumer commit in a separate field (`installed_at_commit`) | NV08 → PASS |
| M-N2 | `update --apply` writes an absolute `source` (M6 regression on the update path) | NV-03 | use `kernel::source_label(src)` in `update.rs` | NV03 defect list empty for `source` |
| M-N3 | `M-4.1.2-4.1.3` does not perform the overlay tightening it describes; upgraded projects lexically index the held-out file | NV-19, NV-03 | add `set_overlay_key`-style operation for the `governance/tests/**` rule (or an `update_contract_rule` op) and make migration descriptions machine-checked against operations; fix release notes | NV19 → PASS; NV03 `heldout_file_in_index_after_update` empty |
| M-N4 | Mutation scope at close is self-attested | NV-05 | compare `files_changed` with `git status`/diff since the claim checkpoint; unreported out-of-scope changes → `MUTATION_SCOPE_VIOLATION`; record actual dirty set in the checkpoint | NV05 → PASS |
| M-N5 | Relocated governed record dropped by the first incremental rebuild | NV-07 (`indexer.rs` duplicate-id branch) | treat "same id, different path, old path gone" as a move: delete the old artefact before deciding duplication, or run the removal sweep before the duplicate check | NV07 → PASS |
| M-N6 | API-0001 (AUTHORITATIVE), `capabilities/PROTOCOL.md`, failure-injection README promise a silent built-in fallback for failing embed plugins; code fails closed | source vs records | amend API-0001 through a CIT/decision (embed: fail closed; code_intel: degrade), update docs | records consistent; `schema_invariants` clean |
| M-N7 | Release branch/tag provenance for 4.1.3 | §6, Q27 | tag the candidate; rename or branch `release/4.1.3-rc1`; record in manifest/notes | `git tag` shows the release; manifest references it |
| M-B1 | No shipped/referenced paraphrase-capable embedder and no benchmark record for the canonical repository | §5, NV-06 | ship or reference one credible local candidate behind API-0001 with a recorded benchmark on this repository's held-out set, or a decision recording why not | research + decision records in `spec/` |
| M-N8 | Real 4.1.2 → 4.1.3 update path not in the builder suite | NV-03 only | add a certification test that initialises with the stored immutable 4.1.2 payload and updates to the current release (chain both from 4.1.1 and 4.1.2) | test present and green |

### LOW
| ID | Gap | Evidence | Repair |
|---|---|---|---|
| L-N1 | `KERNEL.yaml` duplicate `schema_versions.release-manifest` key | NV-09 | remove the 1.0.0 line; add a strict-YAML check to the arch test |
| L-N2 | Rollback leaves no ledger entry; second `--rollback` silently re-applies the snapshot | NV-03 | append `rolled_back` ledger entry; mark snapshot consumed |
| L-N3 | `memory select` sets `human_approved = (--by != "agent")` | `benchmark.rs` | derive from an answered gate or the acting role level |
| L-N4 | Role is self-declared (`--role human` from any session) | design | document as a trust boundary; optionally bind human answers to a channel token |
| L-N5 | Docs stale: `fixtures/update/README.md`, `docs/FIXTURES.md` row 4 ("4.1.1 → 4.1.2"), update fixture title | docs | update |
| L-N6 | rustfmt divergent (756 diffs); 5 clippy warnings | builder-suite-rerun | format and fix before certification |
| L-N7 | Update ledger `by`/`session` only; no verifier identity field in `framework.lock` for certified installs | `update.rs` | optional |

## 12. Builder repair delta (ordered)

1. **C-N1** CIT gate integrity: approval requires answer option A; option B rejects the CIT (from `gates::answer` when `cit` is set, and in `approve`/`execute`); no decision record is fabricated by `approve`; `human_approved` only from a human answer. Builder regression test + `harness_v2.py NV01`.
2. **H-N1** Policy hierarchy at load time: allowlist of overridable keys; refuse/flag overrides and exceptions of AUTHORITY/SECURITY keys; D007 + suite CRITICAL; record applied overrides in the context packet layer 3. `NV02`.
3. **H-N2** Plugin governance: schema validation, registration through the install gate, `approved_roles`/permission class checks on invoke and on pinned use, hash/version pin, doctor + suite checks. `NV04`.
4. **M-N1/M-N2** Lock provenance: `release_commit` from the release; logical `source` on update. `NV08`, `NV03`.
5. **M-N3** Complete `M-4.1.2-4.1.3` (contract rule op) and make migration descriptions machine-checked; fix release notes. `NV19`, `NV03`.
6. **M-N4** Working-tree cross-check at task close. `NV05`.
7. **M-N5** Relocation handling in incremental indexing. `NV07`.
8. **M-N6** Amend API-0001/PROTOCOL.md/fixture README to the fail-closed embed semantics via a governed change.
9. **M-N7** Tag and rename/branch for 4.1.3; **M-N8** add the real 4.1.2→4.1.3 update test; **M-B1** ship/reference a paraphrase-capable candidate with a recorded benchmark or a decision.
10. **L-N1…L-N7**.
11. Because the fix set touches kernel data (AUTHORITY/SECURITY override rules, plugin schema, migration file, KERNEL.yaml), the repaired candidate must be a new immutable PATCH release (4.1.4) with migration `M-4.1.3-4.1.4`; rerun the builder suite, both held-out harnesses unchanged (`heldout/harness.py`, `heldout-new/harness_v2.py` — the latter needs a 4.1.2 binary at `GOV412_WORKTREE`, buildable with `git worktree add --detach <dir> 8ad06be && cargo build --release`), clippy, rustfmt; regenerate evidence; leave certification pending.

## 13. Independent test additions (this session; not part of builder tests or the first verifier's harness)

NV-01 CIT gate answer integrity (three sub-cases) · NV-02 overlay override of security/authority policy · NV-03 genuine 4.1.2 → 4.1.3 update, machine-B rebuild, downgrade view, rollback and second rollback · NV-04 plugin descriptor governance · NV-05 self-attested mutation scope · NV-06 paraphrase retrieval through benchmark/select with an independently authored embed plugin · NV-07 incremental rebuild after record relocation · NV-08 lock provenance on three install paths · NV-09 kernel YAML strictness · NV-10 reranker ordering and mismatch · NV-12 fail-closed pin change on continue/context · NV-13 update-gate decline control · NV-16 release identity, reproducibility, immutability · NV-17 plugin boundary for secret/restricted content · NV-19 migration record integrity. (NV-11/14/15/18 were folded into NV-01/NV-03 or documented as design limitations.)

Test-author and executor separation: the harness was authored and executed in this single fresh session; results were reviewed against the first-run log and a second full run (identical verdicts) before writing this report.

## 14. Verified sound (do not regress)

Rust-only core with embedded kernel and no Python/Node dependency; language-neutral kernel data and language-tagged tool registry; init/adopt (A0–A11 with destructive gate records)/update/rollback mechanics including genuine 4.1.2 → 4.1.3 with overlay preservation, `spec/` immutability and byte-identical rollback; release payload identity, reproducibility and immutability; embedder/reranker replaceability with fail-closed pins on every query path; plugin host at scale; plugin boundary for secrets and restricted content; index-side and write-side secret controls; claims/control outside the rebuilt store; deterministic context hash across machines and rebuilds; authority layers and conflicting-decision flags in the packet; readiness-driven task generation; DAG semantics incl. TEST_POLICY prerequisites; intent routing; failure-injection recoveries; upstream export gate; policy-enforcement coverage map; benchmark/selection mechanism.

## 15. Verdict

**OS_RELEASE_CANDIDATE_REJECTED** for commit `26ab5b6eb111d573f8686bc4f4b1dfc20539f45e` (repair candidate 4.1.3). Rejection triggers met (directive §10): fresh independently authored tests expose unresolved CRITICAL/HIGH defects (C-N1, H-N1, H-N2); security/privilege boundaries are materially incomplete (H-N1, H-N2); version/provenance state has internal inconsistencies affecting update provenance (M-N1…M-N3), though not release identity. The previous CRITICAL/HIGH findings are genuinely repaired and the previous held-out tests pass unchanged; HV-08b is not a blocker. The release manifest certification block must be set to REJECTED by the release owner (this session was not permitted to modify shared release files); `VERDICT.md` contains the exact block.
