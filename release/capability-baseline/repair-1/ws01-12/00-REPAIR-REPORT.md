# P2-AR-0014 — Repair iteration 1, round 1: WS-1 (part) + WS-12

| Field | Value |
|---|---|
| Run | P2-AR-0014, role `capability-repair`, model Claude Opus 5 (1M context), fresh context |
| Handoffs | `P2-HO-0010` (common protocol), `P2-HO-0011` (WS-1 part + WS-12) |
| Branch / base | `phase2/repair-1-ws01-12` / `c6b60bc760a0bb42907f74210fd9e644a420851a` |
| Product work commit | `473c3fba12a64cc36144c192c02b07f5db63fa04` (`product_code_digest` `d6005a51…f03c`; base `bd4d65d9…0547`) |
| Classes | **BC-P2-01** — `REPAIRED_CLAIMED`; **BC-P2-51** — `REPAIRED_CLAIMED` (the format; its acceptance is the AC-6 fresh review) |
| Owner-decision questions | none |
| Owner source | `Governance_OS_Capability_Acceptance_Contract_v3.md` and its canonical import are byte-for-byte unchanged (`4c2df291…5ed3`) |

This is a builder's claim with regression evidence (Contract v3 O3). Nothing here is acceptance: the probes below are the
audits' own probes re-run unedited, plus builder evidence. Fresh verifiers decide.

---

## 1. BC-P2-01 — compiled contract views carry the owner source; `gov contract verify` is no longer self-referential

### 1.1 Requirement (repair-delta §1, sources)

The compiled form, the generated view and the evidence map carry, for every capability section of the owner source
**including Gate U**, every checklist item (713 checkbox bullets plus the qualifiers at lines 385 and 515), the W10
hard-invariant text, each gate's advanced-qualification challenge, the per-capability fields of Contract v3:53-73 and the
requirement-class label exactly as the source states it (O5 "NEW EXECUTION REFINEMENT"; Gate V "NEW TESTING REFINEMENT",
carried verbatim, not mapped). `gov contract verify` fails, typed, on any semantic difference between the owner source and
any derived view (Contract v3:37-49 "Any semantic difference between source and compiled representation is a hard
failure"; frozen gate contract AC-13, §9.4).

### 1.2 What changed

`runtime/src/contracts.rs` (rewritten; public entry points `verify`, `generate`, `compile`, the path constants and
`OWNER_SOURCE_SHA256` kept):

- **`parse` — a line-accounting compiler.** Every line of the owner source other than a blank line or a `---` thematic
  break is placed, verbatim with its line number, exactly once: document title; preamble sections; gates; capability
  sections; checklist items (`- [ ] …` and `N. [ ] …`, stable ids `<capability>.<n>`, the lead-in each belongs to);
  every other line of a section as a statement with a mechanical kind (`lead_in`, `qualifier`, `hard_invariant`, `quote`,
  `prose`); advanced-qualification challenges (ids `AQC-<section>` minted from position); closing sections. A construct
  the compiler cannot place is refused (`CONTRACT_SOURCE_UNRECOGNISED`), never dropped.
- **Gate U.** A gate that states its checklist without numbered capability headings is a capability section whose id
  is the gate letter (frozen gate contract §9.4). Result: 101 capabilities, 23 gates, 713 checklist items, 37
  statements (incl. line 385 "persist beyond conversation lifetime.", line 515 "and silent N/A is invalid.", the W10
  hard invariant at line 1164, Gate V's custody sentence at 1014), 8 challenges, 1026 of 1255 lines carried (229 blank
  or `---`).
- **Labels.** `requirement_class_label` carries the label exactly as written (capability heading, else gate heading),
  with its line. `requirement_class` is the Contract v3:60 class the label denotes (unlabelled → `ORIGINAL`;
  `POST-VERIFICATION HARDENING` → `POST_VERIFICATION_HARDENING`; `NEW EXECUTION REFINEMENT` → `EXECUTION_REFINEMENT`), or —
  when the label denotes none of the three (Gate V) — the label itself, verbatim, with `requirement_class_enumerated:
  false`. Titles no longer carry markup (O5 was `…**[NEW EXECUTION REFINEMENT]**`).
- **Contract v3:53-73 fields.** The 17 fields are read from the source (`CONTRACT_FIELDS`; the compiler refuses a
  source whose list differs) and every capability carries every field in all three views. Where the owner source states
  a value (id, title, source reference, requirement class, challenge ids) it is carried; where it states none
  (severity, applicability, evidence class, automated checks, independent verification, freshness triggers, tiers,
  adoption / operational-audit obligations, allowed status, N/A requirements, remediation rule) the compiled form
  carries the field as `null` — it may not invent a value — and the evidence map carries it as a **governed** field
  (`evidence_class: NOT_YET_MAPPED`, `automated_checks: []`, others `null`), plus `automated_checks: []` per checklist
  item. Contract-level vocabularies are compiled from the preamble: requirement classes (:60), evidence classes
  (:83-91), freshness inputs (:99-109), lifecycle points (:117-127), health-scheduler tiers G0-G6 (O5 "Tiered checks:").
- **`source_accounting` — the independent check.** It uses none of the compiler's parsing. From the raw source text
  and a compiled value it requires: every non-blank line carried verbatim exactly once; every checklist-shaped line
  carried *as a checklist item* inside the capability section that textually contains it; every `## X<n>.` heading and
  every `# GATE` heading carried; every heading-less gate carried as a capability; every label carried as written; every
  challenge carried. `verify` applies it to the committed compiled form **and** to a fresh compilation (so a lossy
  compiler is itself refused: `CONTRACT_COMPILER_LOSSY`).
- **`verify`** now checks, in order: import digest + byte identity with the owner source; the lock binds the digest;
  compiler losslessness; the compiled-form schema admits the fresh compilation (`CONTRACT_SCHEMA_DIVERGED`); the
  compiled YAML — line accounting, field-by-field keyed comparison with the owner-source model, schema validation,
  equality (`CONTRACT_COMPILED_DIVERGED`); the evidence map — every source-derived field compared with the model, every
  governed field present and drawn from the contract's vocabularies, schema (`CONTRACT_EVIDENCE_MAP_DIVERGED`); the
  generated view — every rendered element present, then byte equality with a fresh rendering
  (`CONTRACT_GENERATED_VIEW_DIVERGED`); every field of the lock (`CONTRACT_LOCK_DIVERGED`). Each error carries the full
  difference list (`at`, `problem`, expected/found) and remediation text.
- **`generate`** (`gov contract compile`) preserves governed evidence-map values by capability/item id, refuses to
  overwrite a map it cannot read or whose data it would discard, and ends by running `verify`.
- **Lock** (`contract-source.lock`, schema v2) binds the compiled form, the compiled-form schema, the source-derived
  part of the evidence map, the generated view and the universe counts.

Derived files regenerated by `gov contract compile` (never hand-edited): `framework/contracts/governance-capability-acceptance.yaml`,
`framework/contracts/contract-source.lock`, `tests/governance/capability-evidence-map.yaml`,
`docs/generated/GOVERNANCE_CAPABILITY_ACCEPTANCE.md`. `framework/schemas/governance-capability-acceptance.schema.json`
rewritten: id pattern `^[A-Z]+[0-9]*$` (admits `U`), the full compiled structure, `additionalProperties: false`, governed
fields constrained to `null` in the compiled form, and `$defs/evidence_map` for the map. The capability item schema is
inline at `properties.capabilities.items` (the shape the previous schema had and the synthesis probe reads).

### 1.3 Product check and tier

`gov contract verify` (`contracts::verify`) is the check; `cargo test --lib` owns 14 unit tests of it. It does **not yet
run at a G-tier**: wiring it into the G5 full suite / doctor and into release build belongs to files this workstream does
not own — see integration points IP-1 and IP-2. `the_committed_binding_chain_verifies` and
`regeneration_is_idempotent_over_the_committed_views` make `cargo test --lib` fail whenever a committed derived view
drifts from the source or from `gov contract compile`'s output.

### 1.4 Probes re-run (audit-of-record probes, unedited; runner `evidence/probes-runner/run-probes.sh`)

Before = base `c6b60bc`, gov `3271ce0e…`; after = `473c3fb`, gov `bd1106a5…`.

| Probe | Before | After |
|---|---|---|
| synthesis `AC01-09-13-14` — `gov contract verify` | `exit=0 CONTRACT_SOURCE_BOUND capability_count=100` | `exit=0 CONTRACT_SOURCE_BOUND capability_count=101` |
| — compiled universe | `capability_count=100 … missing from compiled: ['U']` | `capability_count=101 ids=101; owner universe=101; missing from compiled: []` |
| — Contract v3:53-73 fields in compiled form | `none` | `severity, applicability, evidence_class, automated_checks, independent_verification, freshness_triggers, health_scheduler_tiers, adoption_obligation, operational_audit_obligation, allowed_status, na_requirements, remediation_rule, checklist` (+ `qualification_challenge_ids`, listed under compiled fields) |
| — bullets ≥25 chars in compiled form | `0/344` | `344/344` |
| — class O5 | `compiled='ORIGINAL' … DIVERGES`; title retains markup | `compiled='EXECUTION_REFINEMENT' … OK`; no markup line |
| — class U | `compiled=None … DIVERGES` | no line (OK) |
| — class V1-V4 | `compiled='ORIGINAL' … DIVERGES` | `owner_label='NEW TESTING REFINEMENT' compiled='NEW TESTING REFINEMENT' … DIVERGES` — see note (a) |
| — schema admits `U` | `False` | `True` |
| — evidence map rows | `rows=100 missing=['U']` | `rows=101 missing=[]` |
| — generated view | `rows=100 missing=['U']; bullets 0/344` | `rows=101 missing=[]; bullets 344/344` |
| — verify reads map / view / self-referential | `False / False / True` | `True / True / False` |
| — `[AC-10]` zero evidence owners | `101/101` | `101/101` — BC-P2-02 (later round), not this class |
| alpha-r `C0-contract-derived-views` | compiled keys: 6 identity keys; fields present `[]` | compiled keys include `checklist`, `statements`, all 12 unstated fields; fields present: 7 of the probe's 9 names — see note (b) |
| beta-r `DERIVED-views-reconciliation` | `DERIVED-compiled FAIL` (0 carried); view bullets 0 | `DERIVED-compiled FAIL` 121/123 — see note (c); generated view carries 123/123; `DERIVED-evidence-map FAIL` (BC-P2-02) |
| gamma-r `DV-derived-views` | `no-bullets`, 100 rows | compiled carries `checklist` + all fields for E-I; titles/classes `same`; evidence map `NOT_YET_MAPPED/0chk` (BC-P2-02) |
| delta-r `DERIVED-VIEWS-JKLMN` | `DV.compiled.bullets FAIL`, `DV.compiled.fields FAIL`, `DV.map.1 FAIL` (20/23) | `DV.compiled.bullets PASS`, `DV.compiled.fields PASS`, `DV.map.1 FAIL` (BC-P2-02) (22/23) |
| epsilon-r `V-oracle-format-and-contract-views` §D | `gate U present … False`; O5/V1-V4 `ORIGINAL`; 100 caps | `gate U present in compiled form: True \| in evidence map: True`; O5 `EXECUTION_REFINEMENT`; V1-V4 `NEW TESTING REFINEMENT`; 101 caps — note (d) |
| zeta-r `DV-derived-view-reconciliation` | 4/9: W bullets, W10 invariant, W challenge, fields, evidence owner FAIL | 7/9: W10 invariant PASS, W challenge PASS, required fields PASS; `W bullets FAIL 83/86` — note (c); evidence owner FAIL (BC-P2-02) |

Notes. (a) The synthesis probe's expected value for Gate V is the sentinel string `'(no enumerated class; Contract
v3:60 lists …)'`, which no data value can equal; the repair delta requires the label carried verbatim rather than
mapped, which the compiled form does (`requirement_class_label` and `requirement_class` both `NEW TESTING REFINEMENT`,
`requirement_class_enumerated: false`). (b) alpha-r searches for `evidence_classes` and `qualification_challenges`; the
product names these `evidence_class` and `qualification_challenge_ids` (the latter is Contract v3:68's wording). alpha-r's
summary line "bullets represented in the compiled form: 0" is a literal string in the probe, not a count (the compiled
form carries 100/100 alpha bullets — `evidence/bc-p2-01/probe-encoding-check.out`). (c) beta-r tests `bullet in
json.dumps(entry)` and zeta-r `bullet[:40] in json.dumps(entry)`; `json.dumps` escapes non-ASCII by default, so the two
D3 bullets and three W bullets containing `→` (L324, L325, L1148, L1180, L1181) can never match. With
`ensure_ascii=False` the same comparisons give 123/123 and 86/86, and all 722 checklist lines of the source are carried
verbatim (`evidence/bc-p2-01/probe-encoding-check.out`). (d) epsilon-r §D's last line ("fields absent …") and "bullets
carried: 0" are literal strings in the probe, printed unconditionally.

### 1.5 Mutation controls (Accept: "deleting one bullet, one capability (U), or changing one label in any derived view each make `gov contract verify` fail with a typed error")

`evidence/bc-p2-01/mutation-controls.py` → `.out`: 20/20 against `target/release/gov` on disposable copies — unmodified
chain `CONTRACT_SOURCE_BOUND`; in the compiled form, evidence map and generated view each: delete one bullet, delete U,
change one label → `CONTRACT_COMPILED_DIVERGED` / `CONTRACT_EVIDENCE_MAP_DIVERGED` / `CONTRACT_GENERATED_VIEW_DIVERGED`
(first difference names the element, e.g. `source line 133 not carried`, `capabilities[U] missing`,
`capabilities[O5].requirement_class_label label differs`); also dropped W10 invariant, dropped line-515 qualifier,
dropped Gate W challenge, invented severity, map mapping V1 to ORIGINAL, dropped per-capability field, evidence class
outside :81-91, altered lock digest (`CONTRACT_LOCK_DIVERGED`), a schema that cannot express U
(`CONTRACT_SCHEMA_DIVERGED`), an edited import (`CONTRACT_SOURCE_DIVERGED`).

### 1.6 Tests added / changed

`runtime/src/contracts.rs` unit tests (14): universe read in full (101/23/713/8, U 28 items, 9 closing items, 17
fields, vocabularies, tiers); labels verbatim; qualifiers/invariant/challenges verbatim; compiler line accounting;
accounting independent of the compiler (dropped item, dropped U, changed label, misattributed item); byte change
changes binding + determinism; committed chain verifies; regeneration idempotent; typed failure per mutation in compiled
form (7 mutations), evidence map (7), generated view (4); lock and schema bound; governed values survive regeneration
and undiscardable data is refused; edited import refused first.

Changed builder test: `contracts::tests::the_compiler_invents_nothing_and_is_deterministic` was **replaced** — it
exercised `parse_capabilities`, the headings-only reader that no longer exists. Its two properties are now asserted more
strongly: determinism in `a_single_changed_byte_in_the_source_changes_the_binding` (kept, adapted to `compile(&str) ->
Result` and the real source), and "invents nothing" in `the_line_accounting_is_independent_of_the_compiler` and the
"invent a per-capability value" case of `a_semantic_difference_in_the_compiled_form_is_a_typed_failure`.
`tests/certification/srr.rs::the_capability_contract_source_chain_is_hash_bound_and_fails_closed` passes **unchanged**
(edited import → `CONTRACT_SOURCE_DIVERGED`; edited `requirement_class` → `CONTRACT_COMPILED_DIVERGED`).

### 1.7 Limits — what this does not do

- The evidence map names **no** evidence owner (101/101 zero owners, AC-10): that is BC-P2-02 (WS-1, later round). This
  repair gives it the structure: every Contract v3:53-73 field per capability, per-item `automated_checks`, vocabulary
  enforcement, and preservation across regeneration.
- The per-capability values the owner source does not state (severity, applicability, adoption obligation, …) are not
  invented; assigning them is governed work (BC-P2-02 populates evidence class and check ids).
- The v1 evidence map's builder placeholder `independent_verification_obligation: "R1/R2 per the frozen acceptance
  boundary"` (not owner text) is not carried; the governed field `independent_verification` is `null` until mapped.
- Attribution of statements and challenges is positional (e.g. the D6-positioned challenge is recorded in section `D6`,
  gate `D`, and listed in the gate's `qualification_challenge_ids`; line 1062 is a qualifier in `V4`). Nothing is
  re-scoped by interpretation.
- `gov contract verify` runs where the canonical OS tree is (as before); it is not a consumer-project check.

---

## 2. BC-P2-51 — Qualification Oracle format

### 2.1 Requirement (repair-delta §1, sources)

A machine-checkable Qualification Oracle format covering every V1-V4 element exists, is kept separate from the public
qualification suite, and is accepted by a fresh independent reviewer against V1-V4 before any hidden fault is generated
(Contract v3:1012-1062, :1206; frozen gate contract AC-6, §9.2). Accept: the format validates a well-formed sample and
rejects samples missing each V1-V4 field; a fresh `oracle-format-reviewer` issues `QUALIFICATION_ORACLE_FORMAT_ACCEPTED`.
No hidden fault is generated in Phase 2.

### 2.2 What was built

- **Definition** `framework/qualification-oracle/qualification-oracle.schema.json` (JSON Schema 2020-12, format
  `governance-os.qualification-oracle` v1, **`format_sha256` `f89a3e2ff882e116f4593d0f7b8fd9725c7ba491090aedadc3a942c66f4316fd`**).
  Location: outside `tests/`, `fixtures/` and any public qualification suite, and outside the kernel `payload_dirs` that
  are installed into consumer projects (it is compiled into `gov` so validation needs no checkout). It contains no
  fault, no oracle content and no repository.
- **Validator** `runtime/src/qualification_oracle.rs` and additive CLI `gov oracle format` / `gov oracle validate <file>
  [--oracle <sealed oracle>] [--public-suite <dir>]… [--repository <dir>]…` (read-only).

Two document kinds:

| Kind | Carries | Key fields |
|---|---|---|
| `qualification-oracle` (one repository, one commit) | V1 fault manifest; V2 hidden path-map oracle (required for `BROWNFIELD`); V3 hidden memory oracle; custody; separation | header `format`, `format_version`, `format_sha256`, `kind`, `purpose` (`QUALIFICATION` \| `FORMAT_SAMPLE`); `oracle_id` (≥8 chars); `custody` {`owner_role: FRESH_INDEPENDENT_VERIFIER`, `owner_run_id`, `authored_independently_of_implementation: true`, `created_at`}; `visibility: HIDDEN`; `repository` {`id`, `adoption_mode`, `commit`}; `separation` {`public_qualification_suite`, `qualification_repository`, `oracle_storage`} |
| `qualification-score-report` (one candidate run) | V4 | `binding` {`oracle_id`, `oracle_sha256` (canonical digest of the sealed oracle), `repository`, `candidate` {`commit`, `product_code_digest`}, `run_id`, `scored_at`}; `metrics` (12 required); `per_fault_outcomes` |

V1-V4 crosswalk (`x-contract-crosswalk`, 44 entries). `gov oracle format` and `crosswalk()` **check it against the
approved source bytes**: each element's text must equal the owner source at that element, and every V1-V4 checklist item
and every Gate V statement must be mapped, else `ORACLE_FORMAT_INCOMPLETE`.

| Contract v3 | Field (oracle unless noted) |
|---|---|
| 1014 verifier-owned hidden oracle | `/custody`, `/visibility`, `/repository` |
| 1017 "Each injected defect records:" | `/fault_manifest/faults` (minItems 1) |
| V1.1-V1.9 (1018-1026) | per fault: `fault_id`; `class` {`id`, `capabilities` (owner-source ids), `challenge_ids`}; `hidden_authoritative_truth` {`statement`, `authoritative_refs`}; `injected_repository_state` {`description`, `changes[]` {path, change, from_path for MOVED/RENAMED, content_sha256}}; `expected_detection` {`tiers` (O5 G-tiers), `signals`, `must_detect_before`}; `expected_severity`; `expected_impacted[]` {ref, ref_kind, relation}; `expected_governed_action[]` {action, target, description}; `forbidden_outcomes[]` {outcome, observable} |
| 1029 "For brownfield Repo B:" | `/repository/adoption_mode`; `/path_map_oracle` required when `BROWNFIELD` |
| V2.1-V2.7 (1030-1036) | per entry: `current_artefact` {path, content_sha256}; `correct_classification`; `authority`; `expected_target_paths`; `action` (KEEP/MOVE/RENAME/SPLIT/MERGE/EXTRACT/RETIRE + B2's DELETE_FROM_ACTIVE_TREE); `expected_references`, `expected_consumers`; `sensitivity`, `indexing_expectation` |
| V3.1-V3.7 (1039-1045) | `must_be_indexed`, `must_never_be_indexed`, `expected_authority_namespaces`, `expected_status` (CURRENT/SUPERSEDED/HISTORICAL + `superseded_by`), `expected_graph_relationships`, `expected_code_symbols`, `expected_retrieval_results` {query_id, query, route, top_k, must_include, must_not_include} |
| 1048 "Report:", V4.1-V4.12 (1049-1060) — score report | `/metrics`: `injected_defect_detection_recall`, `false_positives`, `severity_accuracy`, `impact_map_accuracy`, `path_map_accuracy`, `missed_authoritative_artefacts`, `wrong_indexing_count`, `stale_index_count`, `retrieval_metrics` {k, queries, recall_at_k, mrr, precision_at_k, stale_hit_rate, …}, `recovery_chaos_pass_rate`, `human_gate_correctness`, `task_readiness_correctness` (ratios {numerator, denominator, value}, counts {count, refs}, or explicit N/A {applicable:false, reason}) |
| 1062 separation | `/separation` + filesystem separation check |
| W12.7 (1192) G6 injects hidden artifact-flow failures; AQC-W12 (1194) "The hidden oracle defines the correct required input/version and expected downstream propagation." | per fault `artifact_flow` {`required_inputs[]` (artefact_id + version or content_sha256), `expected_propagation[]` (ref, expected_state)} — **required whenever the fault's class challenges a Gate W capability** |
| 1206 "Qualification Oracle format is accepted before generating hidden faults." | `/format_sha256` on both kinds: a document is valid only against the exact format version it names, so acceptance can be pinned to a digest |

Semantic rules beyond the schema: unique fault ids; `class.capabilities`, `class.challenge_ids` and detection tiers
drawn from the owner source (parsed from the approved bytes); path-map action/target consistency (KEEP = [current];
MOVE/RENAME = one other path; SPLIT ≥2; MERGE 1; EXTRACT ≥1; RETIRE ≤1; DELETE 0); no material both indexed and never
indexed; no required retrieval result that is never-indexed; SUPERSEDED needs a successor ≠ itself; V2 indexing
expectation consistent with V3; oracle storage not inside (or containing) the public suite or the repository. Score
reports: ratio value = numerator/denominator; recall, severity accuracy and impact-map accuracy recomputed from
`per_fault_outcomes`; undetected faults carry no detection record or credit; counts equal the listed refs. With
`--oracle`: identity, canonical digest, repository, purpose, every injected fault scored exactly once, impacted counts,
severity correctness, path-map denominator / N/A, retrieval query count (`ORACLE_SCORE_BINDING_MISMATCH`). For an
oracle, `validate` scans the given (and declared, if present) public-suite and repository directories: the oracle stored
inside, a copy, its id, its digest, or a hidden truth statement (≥32 chars) quoted verbatim → `ORACLE_SEPARATION_VIOLATED`.
Violations are tagged with the Contract v3 element and line (e.g. `V1.6 … Contract v3:1023 “expected severity”`).

### 2.3 Product check and tier

`gov oracle validate` / `qualification_oracle::{validate_file, validate_value, cross_check}`, owned by 9 unit tests in
`cargo test --lib`. It is the natural G6 check; the G6 entry point is WS-2's (IP-4). It is not in the public suite.

### 2.4 Probes re-run

| Probe | Before | After |
|---|---|---|
| synthesis `AC06-oracle-format-search` — V1-V4 identifiers | `<none>` for all 12 patterns | all 12 found in `framework/qualification-oracle/qualification-oracle.schema.json` and `runtime/src/qualification_oracle.rs` |
| — CLI surface | `gov oracle unrecognised` | `gov oracle exists` |
| epsilon-r `V-oracle-format-and-contract-views` §A | all V1-V4 patterns `<none>` (except incidental) | all found in the format and validator |
| — §B `gov oracle` | `error: unrecognized subcommand 'oracle'` | `gov oracle: Qualification Oracle format (Contract v3 Gate V, V1-V4): …` |
| — §B a `fault-manifest` record as a *governed project record*, `gov audit --family schema_invariants` | `HEALTHY` | `HEALTHY` — unchanged: the governance suite is WS-2's (IP-5). The same record given to the format's validator is refused: `ORACLE_RECORD_INVALID` (evidence F) |

### 2.5 Builder evidence (`evidence/bc-p2-51/oracle-format-checks.py` → `.out`, 78/78, CLI only)

A: the FORMAT_SAMPLE oracle and score report (`evidence/bc-p2-51/samples/`, placeholders, bound to no repository)
conform; the report binds to its oracle file. B: for **every** field of the format's own crosswalk (50 fields over 44
elements), the sample without that field is rejected `ORACLE_RECORD_INVALID` with a violation at that field tagged with
that element. C: 16 semantic cases. D: an oracle changed after sealing, and a report leaving a fault unscored →
`ORACLE_SCORE_BINDING_MISMATCH`. E: oracle in the repository, a copy in the public suite, a hidden truth quoted in the
repository → `ORACLE_SEPARATION_VIOLATED`; the same oracle in verifier custody passes. F: epsilon-r's own records
(`FM-0001` with no V1 field, `FM-0002` nonsense) → `ORACLE_RECORD_INVALID`, explaining the format's kinds and the nine
V1 fields. `evidence/bc-p2-51/gov-oracle-format.json` is the full `gov oracle format` output for the reviewer.

### 2.6 Design choices a reviewer should judge (not settled by the sources)

`DELETE_FROM_ACTIVE_TREE` admitted as a V2 action (V2 lists seven; B2, which the oracle scores, has eight); governed
actions, ref kinds, propagation states, severity (`CRITICAL…INFO`) and indexing expectations are closed enums with
`OTHER`/free text only where noted; V3 lists and the fault manifest require ≥1 entry; `must_detect_before` required;
`oracle_id` ≥8 characters (leakage scan); V4 ratios may be an explicit, reasoned N/A except detection recall; separation
leakage detection is heuristic beyond the structural checks (id, digest, verbatim truth ≥32 chars); `adoption_mode`
GREENFIELD/BROWNFIELD is the format's reading of "For brownfield Repo B".

### 2.7 Limits

No hidden fault, oracle or qualification repository was generated; `purpose: FORMAT_SAMPLE` documents exist only as
format fixtures (unit tests and `evidence/bc-p2-51/samples/`). `GATE-P2-ORACLE-FORMAT` stays `NOT_SATISFIED` until the
fresh review. The format is `PROPOSED` (`x-format-status`).

---

## 3. Regression and preservation

| Check | Result | Evidence |
|---|---|---|
| `cargo test --lib` at `473c3fb` | **63 passed, 0 failed** (base 42; −2 old contract tests, +14 contract, +9 oracle) | `evidence/regression/cargo-test-lib.out` |
| `cargo test --test certification` at `473c3fb` | **79 passed, 0 failed** (incl. `srr::the_capability_contract_source_chain_is_hash_bound_and_fails_closed` unchanged, all `section6::*`) | `evidence/regression/cargo-test-certification.out` |
| rustfmt | `contracts.rs`, `qualification_oracle.rs` clean; `cli/src/main.rs` 4 pre-existing hunks at base and here (additions fmt-clean) | `evidence/regression/rustfmt-and-hotspots.out` |
| Shared hot spots | `cli/src/main.rs` +42/−0, `runtime/src/lib.rs` +1/−0 | same |
| R1 held-out suites (AC-14) | **not triggered**: no change to `srr/**`, `kernel_trust.rs`, `kernel.rs`, `lock.rs`, `init.rs`, `update.rs`, `release.rs`, `recovery.rs`, `records.rs`, `tools.rs`/`capabilities/**` or any §6 sink. The only kernel-payload file changed is `framework/schemas/governance-capability-acceptance.schema.json` (data no SRR code reads); `framework/contracts/**` and `framework/qualification-oracle/**` are embedded but not in `payload_dirs`. The certification suite's SRR and §6 tests pass. The AC-14 verifier re-runs them on the integrated candidate. | — |

`*.interim.out` files are earlier runs on uncommitted changes, before the last guard (`generate` refusing to discard
evidence-map data) was added; the final runs above supersede them.

## 4. Integration points (for other workstreams; nothing here was edited in their files)

- **IP-1 — WS-2, G5 full suite / doctor** (`runtime/src/verification/mod.rs` or `runtime/src/doctor.rs`): add a check that
  calls `gov_runtime::contracts::verify(&root)` when the canonical OS tree is present (`kernel::canonical_root()` or the
  audited root holds `framework/contracts/source/…`), reporting any `CONTRACT_*` error as a HIGH finding with its
  `details.differences`. Why: BC-P2-01's check must run at a tier (repair-delta §0.2c); today it runs only on demand.
- **IP-2 — WS-8, release build** (`runtime/src/release.rs`, `release::build`): refuse to build a release unless
  `contracts::verify(canonical_root)` returns `CONTRACT_SOURCE_BOUND`. Why: a release must not ship derived contract views
  that diverge from the owner source.
- **IP-3 — WS-1 later round, BC-P2-02**: populate the governed fields of `tests/governance/capability-evidence-map.yaml`
  (row `evidence_class` from Contract v3:83-91, `automated_checks` per capability and per checklist item,
  `health_scheduler_tiers` ⊆ G0-G6, `freshness_triggers` ⊆ :99-109, others), then run `gov contract compile` (preserves
  them, refreshes view and lock); `gov contract verify` enforces the vocabularies.
- **IP-4 — WS-2, G6 entry point (BC-P2-07)**: when a qualification run is recorded, call
  `qualification_oracle::validate_file(oracle, &ValidateOptions{public_suites, repositories, ..})` and
  `validate_file(report, &ValidateOptions{oracle: Some(oracle), ..})` (or `validate_value` / `cross_check` in-process), and
  refuse to record health for a run whose oracle or report does not conform, is unbound, or is not separate.
- **IP-5 — WS-2, governance suite (`schema_invariants` or a new family)**: report HIGH for hidden-oracle material inside a
  governed repository — `qualification_oracle::is_hidden_oracle_material(&record.data)` per record, or
  `scan_for_hidden_oracle_material(&p.root)` (Contract v3:1014, :1062). This turns epsilon-r V §B from `HEALTHY` into a
  finding.
- **IP-6 — orchestrator / oracle-format reviewer**: the AC-6 review should name `format_sha256`
  `f89a3e2ff882e116f4593d0f7b8fd9725c7ba491090aedadc3a942c66f4316fd`; documents written against any other digest are refused.
- **IP-7 — WS-3 (`cli/src/main.rs`)**: additive `Cmd::Oracle` / `OracleCmd` block and `command_name` arm `"oracle"`
  (read-only; no role semantics). For a BC-P2-08 authority-class census: `oracle *` and `contract verify` are read-only;
  `contract compile` (unchanged surface) writes `framework/contracts/**`, `tests/governance/**`, `docs/generated/**` of
  the OS source tree.

## 5. Owner-decision questions

None. The Gate V label question is answered by the repair delta (carry verbatim); nothing required a new trust boundary,
external dependency or owner-controlled material.

## 6. Evidence index (`evidence/`)

`probes-runner/run-probes.sh` (how the probes were run); `probes-before/*.out`, `probes-after/*.out` (8 audit-of-record
probes each); `bc-p2-01/mutation-controls.{py,out}`, `bc-p2-01/probe-encoding-check.{py,out}`;
`bc-p2-51/oracle-format-checks.{py,out}`, `bc-p2-51/gov-oracle-format.json`, `bc-p2-51/samples/`;
`regression/cargo-test-lib.out`, `regression/cargo-test-certification.out`, `regression/rustfmt-and-hotspots.out`.
