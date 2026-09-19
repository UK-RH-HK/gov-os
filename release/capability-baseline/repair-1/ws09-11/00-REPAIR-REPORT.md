# Repair 1, WS-9 (part) + WS-11: builder report (run P2-AR-0021)

| Field | Value |
|---|---|
| Handoff | `P2-HO-0018` (with `P2-HO-0010`) |
| Branch / base | `phase2/repair-1-ws09-11` from `c6b60bc760a0bb42907f74210fd9e644a420851a` |
| Classes | BC-P2-33, BC-P2-52, BC-P2-21 (catalogue and plan identity side), BC-P2-50 |
| Claims | BC-P2-33 `REPAIRED_CLAIMED`, BC-P2-52 `REPAIRED_CLAIMED`, BC-P2-50 `REPAIRED_CLAIMED`, BC-P2-21 (catalogue/plan side) `PARTIAL` (the governance-suite audit-finding ids need the one-line WS-2 integration below) |
| Round 2, not started | BC-P2-34 (adoption independence), the adopt call sites for BC-P2-08, the G5 tier hook at adopt |
| Evidence | `evidence/` (see `evidence/README.md`). Everything in it is regression evidence only (Contract v3 O3). Nothing here claims acceptance. |

All four classes are implemented as general mechanisms. None of them special-cases a probe fixture. The builder probes in `evidence/B-ws0911-regression-probes.py` deliberately use different wording, file names and layouts from the audit probes.

---

## BC-P2-33: legacy identification, extraction and retirement

**Requirement** (repair-delta; Contract v3:872-885, :191, :928-929; framework §69-§70; adoption protocol §8, §13)

- Extraction must cover decisions, lessons, skills, evidence, research and any other unique durable knowledge, or surface whatever it does not extract for review, before a store is retired.
- Every retirement must be preceded by a dependency proof over code, configuration and docs. It is refused or gated while active references exist.
- Migration never rewrites an active reference so that it points into archived legacy material.
- The plan and the independently scaffolded tests must agree on every artefact's disposition. This includes secret-bearing legacy stores.
- Classification never treats the Governance OS's own installed or generated state as legacy.

**What changed**

- **Governance OS ownership.** New module `runtime/src/migrations/ownership.rs` (`OsState`, `Ownership`).
  - An installed OS layout is recognised from the lock plus the kernel manifest: `governance/{kernel,project,generated,tests}/**` and `governance/framework.lock`.
  - Generated outputs are recognised only when the *installed kernel's* `adapters/*/adapter.yaml` declares them and `adapter-manifest.json` also records them. The root `framework.json` projection counts too. A planted manifest entry therefore cannot exempt a legacy file.
  - The adoption evidence tree (`spec/audits/GOVERNANCE-ADOPTION/**`) is always recognised.
  - An OS layout that has no lock is treated as an interrupted install. It is classified `GENERATED` / `UNKNOWN_OR_CONFLICTING` and kept in place, never archived.
  - These paths are consumed by `classify::classify_all` (they short-circuit to current state and are marked `os_owned`), by `classify::legacy_mechanisms` (used by A5, A7, A11 and doctor D013), and by `planner::plan` (`KEEP_IN_PLACE`).
- **Reference scanning and the dependency proof.** New module `runtime/src/migrations/references.rs`.
  - What it indexes:
    - code imports, using the existing analyser (now indexed by stem in `classify::import_edges`);
    - markdown, reference-style, HTML and reStructuredText links;
    - path mentions: exact, relative, and bare file names;
    - globs and multi-segment directory references in live code and configuration.
  - The index can be built fresh (`build_fresh`). It can also resolve "ghost" paths (`build_fresh_with_ghosts`), so a dangling reference to a retired path is found by its full path.
  - What does not count as a dependency:
    - declarations of provenance (`legacy_source`, `extracted_from`);
    - OS-written event records (checkpoints, audits, reports, CITs, handoffs, gates, legacy registrations, and decisions minted from a gate answer);
    - ignore and ownership files (`.gitignore` and similar, `CODEOWNERS`);
    - the archive;
    - OS state.
  - `dependency_proof()` records the active references with their role (code/config/docs), kind, resolution and line, and a dependants digest.
- **Plan (A3).** `planner::apply_dependency_proofs` attaches a proof to every retirement: archive moves, EXTRACT, RETIRE and DELETE.
  - An artefact with active references becomes a *gated retirement*. It gets `gate_reasons: [active_references]`, runs in batch 7, and needs an answered Human Decision Gate whose question lists the dependants.
  - For an EXTRACT of a legacy document, the knowledge is still extracted in its own batch (`extract_batch`). Only the retirement of the original waits for the gate.
  - The proofs are iterated to a fixed point: a gated artefact stays in the tree, so its own references become active.
  - Secret-bearing legacy stores are planned as legacy stores (EXTRACT in A8, provider-rules MOVE), gated with `secret_material_move`. Their archive destination is classified secret in the repository contract (`adopt::brownfield_contract`).
- **Execution (A6).** `executor::apply_batch`:
  - Each batch takes one fresh scan. Every retirement re-proves its dependencies.
  - If active references exist, the retirement proceeds only when an A-answered gate raised for exactly those dependants covers them (`proof_covered_by`). Otherwise it is `blocked` and recorded in the ledger.
  - References are re-pointed only for moves whose target stays active. For a retirement, only links inside the archived file and in other archived material are touched (`refs::update_references_in` with a scope).
  - Records extracted from legacy documents have content-derived ids. Sections that carry secrets are withheld.
  - Ledger rows carry the stable artefact id, `entry_hash`, catalogue and plan versions, the proof summary, and `skipped` or `blocked` status.
- **Verification (A7).** `verify::verify_catalogue` now re-derives, from a fresh scan and from the ledger across all passes:
  - live code or configuration referring to retired material that no gate accepted: a problem;
  - live code or configuration referring into the archive: a problem;
  - dependants that a gate accepted: reported;
  - legacy mechanisms pending a gate or kept by decision: reported, not treated as unregistered.
- **Extraction (A8).** New module `runtime/src/migrations/extraction.rs`, called by `adopt::a8_extract_legacy`.
  - It reads SQLite stores, JSON/JSONL (all string fields), SQL text dumps and text/markdown (paragraphs and bullets).
  - Every unit becomes one of: a decision, a lesson, a skill candidate (a PROJECT lesson carrying `proposed_skill`), a research note (NARRATIVE, with completeness gaps listed), or an evidence claim (a NARRATIVE report).
  - Any other unit is listed verbatim in a per-store review register (`RPT-LK…`, `review_required`).
  - Secret units are withheld and counted.
  - Each store is retired only after a fresh proof passes, or under a gate that covers its dependants. Retirements are written to the ledger.
  - LEG-0001 registers every legacy mechanism still in the tree, with the gate or proof that holds it there.
- **Plan/test agreement (A5/A6).**
  - `verify::scaffold_tests` derives every expectation from the catalogue's disposition: gated entries carry `gate_artifact`, A8 stores get no A6 absence test, and a new test kind `retirement_references` exists.
  - `verify::plan_test_agreement` finds contradictions. `a5_review` refuses an APPROVED verdict with `PLAN_TEST_DISAGREEMENT`. `a6_migrate` refuses to start on a disagreement.
- **Audit (A11).** Adoption findings are re-derived with stable ids:
  - a live dependant of retired material: high;
  - a dependant in docs: medium;
  - a legacy mechanism kept by decision: medium;
  - a pending gate: high;
  - a review register: low.

  A legacy mechanism kept by an answered gate gives `ADOPTED_WITH_ACCEPTED_EXCEPTIONS` instead of `ADOPTED_HEALTHY`.

**Product checks that own it, and their tier**

These run in the adoption stages themselves:

- A3 `planner::apply_dependency_proofs`
- A5 `a5_review` agreement
- A6 `executor::apply_batch`, which runs the proof and the `retirement_references` tests after each batch
- A7 `verify::verify_catalogue`
- A8 store proof
- A11 adoption findings
- `gov doctor` D013, which now excludes OS state

The G5 hook at adopt is round 2.

**Probes re-run** (the before runs use the base binary, the after runs the final binary; both unedited)

| Probe line | Before | After |
|---|---|---|
| beta-r `R1-R2` R1-b4-skills-research-evidence | FAIL | PASS |
| beta-r `R1-R2` R2-b2 (uncued facts) | FAIL | PASS |
| beta-r `R1-R2` R1-b7 (dependency on retired material detected) | FAIL | PASS (A11 names `src/app/rules_loader.py:4` and `:5`) |
| beta-r `R1-R2` R1-b2, R1-b3, R1-b4-decisions-lessons, R1-b5, R1-b1, R1-b6, R2-b1, R2-b4-index-regression | PASS | PASS |
| beta-r `R1-R2` R2-b3 | FAIL | FAIL (see limits) |
| beta-r `R1-R2` R2-b4-cit (CIT-E retirement; finding A0-R2 non-blocking, not in this class) | FAIL | FAIL |
| alpha-r `S4-adopt-end-to-end` with `RAW_SQL_STORE=1` | A6 fails at batch 1 (MT-029 contradicts KEEP_IN_PLACE); A7-A11 unreachable | A0-A11 all `done`; A7 accepted 40/40 |
| alpha-r `S4-adopt-end-to-end` (prepared fixture) | A0-A11 done | A0-A11 done (A7 40/40) |
| LEAD `X5-S4xB2-os-generated-adapter-not-legacy` | FAIL (adapter archived) | PASS |
| Builder S1 to S5 (proof over code/config/docs, no re-pointing, A7 re-point detection, new-dependant block, OS state, secret store, extraction without cues) | 16 FAIL, 2 controls PASS | all 18 PASS |

**Tests added or changed**

- Added `migration::adoption_dependency_proof_citations_and_rerun_identity`.
- Added unit tests in `references.rs`, `extraction.rs` and `identity.rs`.
- Changed `brownfield::brownfield_adoption_end_to_end`. README.md cites `AGENT_RULES_v2.md`, so that file now stays in place until its gate is answered A, and is retired at batch 7. The test now asserts:
  - the dependency proof names README.md;
  - the retirement happens only after the gate;
  - README.md is byte-identical, meaning it was never re-pointed into the archive.

  The old test asserted immediate retirement, which is exactly the behaviour BC-P2-33 forbids while an active reference exists.
- Changed `migration::path_migration_with_rollback_and_memory_rebuild`. Two reasons:
  1. The extracted records now have content-derived ids (`D-L<hex>` instead of the positional `D-L0001`/`D-L0002`, per BC-P2-21 stable identity), so the test finds them by prefix and status.
  2. `docs/old/legacy_decisions.md` is cited by the architecture document, so its knowledge is extracted but the original is kept, and the citation still resolves to the original rather than the archive. The test asserts exactly that.

  Neither test was weakened. Each one now asserts the stronger property.

**Limits, and what was not done**

- *R2-b3 cannot pass on this fixture for any product that conforms.* The probe's live loader reads `.cursorrules` and `memory/chat_history.sqlite`. The check passes only if no line of that product file names them after A8, which would require the product to rewrite customer code. The requirement forbids that ("migration never rewrites active references into archived legacy material").
  - What the product now does: it gates both retirements with a proof naming `src/app/rules_loader.py`.
  - The probe's own gate step answers A. The references are left untouched.
  - A7 records them as gate-accepted. A11 raises them as high findings.
- A `CIT-E` transaction for store retirement (R2-b4-cit) is not implemented. It is finding A0-R2 (non-blocking, not in BC-P2-33). It would change WS-4's CIT API usage in A8.
- Dependency proofs are syntactic. They find:
  - full paths, relative paths and bare file names (≥5 characters, with an extension or a leading dot);
  - links;
  - imports (loose, by stem);
  - globs;
  - multi-segment directory paths in code and configuration.

  They cannot see a path assembled at run time (`"chat_" + "history.db"`) or a lone single-segment directory string (`"memory/"`). The conservative choices (bare names count, stem-matched imports count) may raise more gates than strictly needed. Files larger than 1 MiB are not scanned and are listed in the proof as `skipped_large_files`.
- Extraction kinds are heuristic and labelled as such (`extraction.kind_basis`). Every unit is kept either in a typed record or in the review register.

---

## BC-P2-52: the path map represents citations

**Requirement.** Document citations and links appear in the path map alongside imports and consumers (Contract v3:194).

**What changed.** `classify::classify_all` builds the reference index over the inventory in one pass (`ReferenceIndex::path_map_all`). Each classification entry, and each catalogue entry built from it by `planner::plan`, carries these fields:

- `imports`: outgoing code imports;
- `citations`: outgoing document links and mentions;
- `path_references`: outgoing path references from code and configuration;
- `consumers`: everything incoming;
- `cited_by`: incoming citations;
- `references`: both directions;
- `reference_edges`: kind, resolution, line and direction.

`consumers` also marks code as live for dead-code detection. A path reference from code or configuration counts for this; a documentation citation does not.

**Product check.** A2 classification and the A3 catalogue. The schema `migration-catalogue-entry` documents the fields.

**Probes re-run**

| Probe line | Before | After |
|---|---|---|
| alpha-r `S4-T2-B2-negative [N5]` README.md | `references=[]` | `references=['docs/spec-login.md']` |
| `[N5]` docs/spec-login.md | `references=[] consumers=[]` | `references=['README.md'] consumers=['README.md']` |
| Builder S6 (reference-style, HTML, rst, relative, both ends) | FAIL | PASS |

The rest of `S4-T2-B2-negative` is unchanged except for one line: in [N2], the executor had edited the catalogue after approval to delete a module that is still imported. The fresh proof now refuses that deletion, and A7 rejects.

---

## BC-P2-21 (catalogue and plan identity side): stable identity

**Requirement.** Every W1-named output carries a stable id, type, version or hash, producer, and supersession lineage that survive re-generation and re-runs. This includes migration plans, adoption catalogue entries and audit findings. The migration ledger's artefact ids must match the catalogue (Contract v3:1069-1080, :972, :945).

**What changed**

- New module `runtime/src/migrations/identity.rs`:
  - `artefact_id(path)`: `ART-<12 hex>` over the path. It is identical on every pass and independent of ordering.
  - `finding_id` and `assign_finding_ids`: `GF-<10 hex>` over family, message and path, deduplicated with `-2`, `-3` and so on.
  - `extracted_record_id` and `extracted_doc_record_id`: content-derived ids for records extracted from legacy material.
  - `Actor` and `producer`.
- Catalogue entries (`planner::finalise_identity`) carry:
  - `type: migration-catalogue-entry`, `entry_hash`, `entry_version`, `catalogue_version`, `producer`;
  - `supersedes`, holding the previous entry hash and version;
  - `lineage.migrated_from`, which ties an artefact a migration moved back to the ledger row and the id recorded there;
  - a Human Decision Gate carried over only within the same adoption pass, and only when its subject is unchanged.
- Catalogue versions are kept in `04-TARGET-PATH-MAP.versions/vNNNN.jsonl`, with the identity `PMAP-GOVERNANCE-ADOPTION` in `04-TARGET-PATH-MAP.meta.json`.
- The migration plan `05-plan.yaml` is the governed record `MPLAN-GOVERNANCE-ADOPTION`:
  - it has `type: migration-plan`, `status`/`state_class`, `version`, `content_hash`, `producer` and declared `consumers` (A5, A6, A7 artefacts);
  - `supersedes: ["MPLAN-GOVERNANCE-ADOPTION@vN"]` plus `supersedes_detail`, and `history`;
  - every version is kept as JSON in `05-plan.versions/`, and superseded versions are marked `SUPERSEDED` / `superseded_by`;
  - an identical re-plan keeps its version.
- Ledger rows name the stable id of the path at the time of the action. A8 store retirements are now in the ledger too.
- Adoption findings in A11, the `12-ADOPTION-FINAL-REPORT.md` report and `finding_messages` carry stable ids.

**Product check.** Stages A3/A4/A6/A8/A11. The schema `migration-catalogue-entry` 1.1.0 now requires `type`, `entry_hash`, `entry_version` and `producer`, and A3 validates every entry against it (`schema_problems: []` on the fixtures).

**Probes re-run**

| Probe line | Before | After |
|---|---|---|
| LEAD `X5-W1-catalogue-ids-stable-across-passes` | FAIL (21 paths changed id) | PASS (0) |
| LEAD `X5-T3-ledger-ids-match-catalogue` | FAIL (13 mismatches) | PASS (0) |
| zeta-r `W01b`: W1-b1/b2/b4/b6/b7/b8/b9 on the migration plan, and replan-keeps-history | 8 FAIL | all PASS |
| zeta-r `W01` W1-b1-audit-finding-id-stable (governance suite `gov audit`) | FAIL | FAIL, pending WS-2 integration point 1 |
| zeta-r `W01` W1-b7-* (authored-record provenance), W1-b3 (misplaced record), W1-b6-benchmark-hash | FAIL | FAIL (WS-4 records side / WS-6; not this workstream) |
| Builder S7 (ids survive an inserted artefact; plan v1 to v2 supersession; v1 retrievable) | FAIL | PASS |

**Why PARTIAL.** The governance suite mints `GF-{n:04}` positionally in `runtime/src/verification/mod.rs`. That file is owned by WS-2, so the repair there is a one-line integration (point 1). Everything on the catalogue and plan side is claimed.

---

## BC-P2-50: the export gate fails closed on content

**Requirement.** The upstream export gate fails closed on raw project content and index data, whatever the names or synthetic declaration (Contract v3:861-866; release protocol §17; framework §75E, §75G).

**What changed.** In `runtime/src/upstream.rs`, `content_gate` is applied in `prepare` to every fixture file (strict) and to every lesson text field (prose rules; fenced code is strict). It is applied again in `submit` to exactly what would leave. It blocks on:

- a whole-file copy of a project file (normalised for whitespace and case, so CRLF or re-indentation does not help);
- more than one reproduced significant line (≥16 non-whitespace characters);
- one reproduced line of ≥48 characters;
- any line from a secret or never-export (DATA_SENSITIVITY restricted/confidential) file;
- in prose, a verbatim excerpt of three or more consecutive project lines;
- a chunk id of the project's derived index;
- a run of the stored embedding vectors (three consecutive non-zero components at stored precision, with their spacing; this works for sparse and dense vectors and ignores `0` versus `0.0` formatting);
- any run of more than 64 numbers;
- any opaque hex or base64 run of 200 or more characters.

Supporting controls:

- The corpus excludes only the framework's own kernel, derived adapter output, and the lesson records being exported.
- The bounds are fixed in code (`ContentControls`) so that no policy or overlay can switch them off. This also avoids new policy keys in WS-3's `ENFORCEMENT_MAP`. `LEARNING_POLICY.upstream.forbidden_content` gains a comment naming the controls.
- At submit, a packet whose content no longer matches its payload hash is refused before anything leaves.
- The export-approval hook is `upstream::resolve_export_approval(p, &ExportApprovalRequest{packet_id, lesson_id, payload_hash, destination}, approved_by)`. Today it records the CLI string as `channel: cli-argument, authenticated: false`, bound to the packet id, the payload hash and the destination. That binding lands in the packet and the ledger.
- The `upstream-packet` schema (1.1.0) documents `approval` and `scans.content`.

**Product check.** `gov upstream prepare` and `gov upstream submit` (command-level; export is refused with `UPSTREAM_BLOCKED`).

**Probes re-run**

| Probe line | Before | After |
|---|---|---|
| epsilon-r `Q4.5 (a)`: verbatim `src/lib.rs` declared synthetic | prepared PKT-0012; the inbox received a byte-identical copy | BLOCKED: "copy of project file src/lib.rs", "reproduces 23 line(s) of raw project content" |
| epsilon-r `Q4.5 (b)`: vector rows as `embeddings.json` | prepared PKT-0013 | `UPSTREAM_BLOCKED` |
| epsilon-r `Q4.5 (c)`, `Q4.1-Q4.4` | as before | as before (a synthetic reproducer still passes) |
| Builder S8: one-line-changed copy, one restricted customer line, 40 vector components with integer zeros, raw code in a fenced block with a trivial fixture, submit-time tamper, synthetic control | 5 FAIL, control PASS | all PASS |

**Limits.**

- Content that has been paraphrased, re-typed, or compressed, or a short vector excerpt rounded below the stored precision, is not recognised. Numbers or blobs longer than the bounds still block.
- Prose rules do not block a single sentence that also appears in a project report. That is deliberate: lessons are distilled from reports.
- Approval authenticity is BC-P2-10 (WS-3). See integration point 2.

---

## Integration points (for later rounds and other workstreams)

1. **WS-2, audit finding ids (BC-P2-21).** In `runtime/src/verification/mod.rs::audit`, drop the positional `y["id"] = json!(format!("GF-{n:04}"))` and the positional id of the reproducibility finding. After `findings` is complete, call `crate::migrations::identity::assign_finding_ids(&mut findings);`. This closes zeta-r `W1-b1-audit-finding-id-stable`. Adoption findings already use it.
2. **WS-3, BC-P2-10 export approval.** Replace the body of `runtime/src/upstream.rs::resolve_export_approval` with the authenticated human channel. For example: a gate raised for `(packet_id, payload_hash, destination)` and answered through the channel, returning `authenticated: true`. Then refuse CLI-string approval when `LEARNING_POLICY.upstream.approval = human`. `submit` needs no other change.
3. **Round 2, BC-P2-08 adopt call sites (WS-3 API, then WS-9).** The `cli/src/main.rs` adopt arms should call `adopt::a3_map_by` and `adopt::a4_plan_by` with `identity::Actor::declared(session, role)`. Today the producer's session comes from `GOV_SESSION`, or falls back to the A0 planner session, and `session_source` says which. The other stages get their declared role when WS-3's resolution API lands.
4. **Round 2, G5 at adopt (WS-2 tier contract).** The adoption checks above are the natural G5 payload at A11 and at re-runs. The hook is not wired.
5. **WS-4, records `TYPE_DIR`.** The migration plan is now a governed record of type `migration-plan` at `spec/audits/GOVERNANCE-ADOPTION/05-plan.yaml`. If WS-4 reports records outside a canonical directory or of an unknown type, add `("migration-plan", "spec/audits/GOVERNANCE-ADOPTION")`, with prefix `MPLAN`. The plan's `supersedes` values (`…@vN`) deliberately do not match the id pattern, so they create no dangling edges.
6. **WS-1, evidence map (BC-P2-02).** These checks are evidence owners that should appear in `tests/governance/capability-evidence-map.yaml`:
   - R1/R2/S4/B2/T3: the adoption stage checks, and `migration::adoption_dependency_proof_citations_and_rerun_identity`;
   - W1 (plan and catalogue): the same test;
   - Q4: `upstream::export_gate_fails_closed_on_content_whatever_the_name`.
7. **Shared test files.** New tests were appended to `tests/certification/migration.rs` and `tests/certification/upstream.rs`. There are no new modules, so `tests/certification/main.rs` is untouched. The changed assertions are in `brownfield.rs` and `migration.rs`, as explained above.

## R1 preservation and regression

- None of the files listed in P2-HO-0010's R1 clause was edited: `srr/**`, `kernel_trust.rs`, `kernel.rs`, `lock.rs`, `init.rs`, `update.rs`, `release.rs`, `recovery.rs`, `records.rs`, `tools.rs`, `capabilities/**`, and the §6 sinks.
  - The new code writes records only through `records::save_record`.
  - The batch-0 install path in `a6_migrate` is unchanged apart from the repository-contract secret patterns.
  - The prior R1 held-out suites were therefore not re-run.
  - `tests/certification/section6.rs`, the §6 derivation, passes.
- `cargo test --lib`: 51 passed, 0 failed (the base had 42).
- `cargo test --test certification`: 81 passed, 0 failed (the base had 79).
- Outputs are in `evidence/after/REG-*.out`. The base outputs are in `evidence/before/`.
- `rustfmt` was run on every touched Rust file.

## Owner decisions

None required. No class needed a change to an accepted architecture or trust boundary, a new external dependency class, or owner-controlled material. OD-P2-01 and OD-P2-02 are not touched.
