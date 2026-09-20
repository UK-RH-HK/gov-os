# P2-AR-0045 — AC-6 Qualification Oracle **format** review (verification iteration 1)

## Verdict

**`ORACLE_FORMAT_ACCEPTED`**

Accepted format identity — **`format_sha256` = `f89a3e2ff882e116f4593d0f7b8fd9725c7ba491090aedadc3a942c66f4316fd`**
(`framework/qualification-oracle/qualification-oracle.schema.json`, format
`governance-os.qualification-oracle`, `format_version` 1), on candidate `cap2-candidate-1`, commit
`0bad524d836f179964ffbac31972856ea6434682`.

A Qualification Oracle format covering Contract v3 Gate V V1–V4 exists on this candidate as a
machine-checkable definition. Every one of the 35 Gate V checklist bullets and all 5 Gate V prose
statements maps to an existing, **required**, **typed** field of the format; 93 of 93 labelled samples
behaved exactly as the definition requires (3 valid accepted, 90 invalid refused with typed errors, each
tagged with the Contract v3 element it concerns); the G6 entry point records a qualification run only
against a conforming, separate, bound oracle, and a `FORMAT_SAMPLE` never counts as qualification.

Six findings are recorded (2 MEDIUM, 1 LOW, 3 INFO). **None blocks AC-6**: each concerns assurance beyond
what AC-6 and Gate V state, or a neighbouring surface. They are the work a Phase-4 qualification author
must still do, and they are listed in §7 and in `findings.yaml`.

No hidden fault was generated. Every document under `samples/` carries `purpose: FORMAT_SAMPLE`, describes
no qualification repository (every path is a placeholder under `sample/` or `example/`), and is a labelled
sample, never an oracle.

---

## 1. Pinned inputs (verified)

| Input | Expected | Observed | Result |
|---|---|---|---|
| `cap2-candidate-1` commit | `0bad524d836f179964ffbac31972856ea6434682` | `git rev-list -n1 cap2-candidate-1` → same | OK |
| `product_code_digest` | `e6332fc7d5af5c73adbe0f200003db30fe5a6fd0b7f24d047d3e340e6f972220` | `product_identity.py 0bad524` and `… HEAD` → same | OK |
| `governed_state_digest` | `3d2aeba2fc3b52a95c369c49a854bb9d443b0b03da1180db5339f01d892620c0` | same at the tag and at `HEAD` | OK |
| Worktree `HEAD` | later orchestration commit | `8588813`; `git diff --stat 0bad524 HEAD` touches only `release/orchestration/phase-2/**` | OK |
| Contract v3 | `4c2df291…5ed3` | `sha256sum` → same | OK |
| Frozen gate contract | `d2f33e89…f25e` | `sha256sum` → same | OK |
| Contract-binding chain | — | `gov contract verify` → `ok`, `owner_source_sha256 = 4c2df291…5ed3`, canonical import byte-identical (`evidence/10-contract-verify.out`) | OK |

No STOP condition.

## 2. The format, and its digest

| | |
|---|---|
| Definition | `framework/qualification-oracle/qualification-oracle.schema.json` (538 lines; JSON Schema 2020-12 plus `x-contract-crosswalk`) |
| Validator | `runtime/src/qualification_oracle.rs` (1 710 lines); CLI `gov oracle format`, `gov oracle validate` |
| G6 entry point | `runtime/src/scheduler/mod.rs::qualification_run`; CLI `gov health qualify` |
| `format_sha256` | `f89a3e2ff882e116f4593d0f7b8fd9725c7ba491090aedadc3a942c66f4316fd` |
| Digest definition | `sha256_text(include_str!(DEFINITION_PATH))` — the raw bytes of the definition file, not a canonicalised parse |
| `x-format-status` | `PROPOSED — no hidden fault may be generated against this format until a fresh independent oracle-format reviewer issues QUALIFICATION_ORACLE_FORMAT_ACCEPTED for this format_sha256` |

The digest the product reports (`gov oracle format`, `evidence/01-gov-oracle-format.json`) equals
`sha256sum` of the definition file, and equals the value round-1 WS-1/12 reported (`f89a3e2f…16fd`). It has
not changed: `git log -- framework/qualification-oracle/ runtime/src/qualification_oracle.rs` shows a single
commit, `473c3fb` (P2-AR-0014, BC-P2-51), and nothing in repair rounds 2–4 or the four integrations touched
either path. The format is **not** installed into consumer projects (`find` over a freshly `gov init`-ed
project finds no `qualification-oracle` path), so it is not kernel payload.

Because the acceptance status is a string inside the definition, editing it to "ACCEPTED" would change
`format_sha256` and invalidate every document naming the accepted digest. The acceptance therefore lives
outside the file — in this report and in `AGENT_RUNS/P2-AR-0045.report.yaml` — which is exactly what frozen
contract §9.2 prescribes. Recorded as finding `V1-OF-05` (INFO).

## 3. Coverage of V1–V4, bullet by bullet

`evidence/02-coverage-crosswalk-check.py` reads the **owner-source bytes** (`Governance_OS_Capability_Acceptance_Contract_v3.md`,
digest verified inline), extracts Gate V lines 1012–1062 itself — it does not use the product's parse — and
resolves each crosswalk pointer through the schema (`$ref`, `allOf`, `if`/`then`) to check the field exists,
is required on every path to it, and is typed. Result: **35 bullets, 5 statements, 0 problems**
(`evidence/02-coverage-crosswalk-check.out`).

Refusal columns are from `evidence/05-RUN-ALL-samples.out`; every refusal is tagged with the Contract v3
element in square brackets by the validator itself.

### V1 — Fault manifest (Contract v3:1016–1026)

| Bullet | Line | Field (required, typed) | Attack → refusal |
|---|---|---|---|
| fault ID | 1018 | `/fault_manifest/faults/*/fault_id` (`id` pattern) | missing → `ORACLE_RECORD_INVALID … [V1.1]`; duplicate → `fault_id "SMP-F-001" is not unique [V1.1]` |
| class | 1019 | `/…/class` = `{id: token, capabilities[≥1], challenge_ids[]}` | missing → `[V1.2]`; `"ZZ9"` → `is not a capability of the owner source [V1.2]`; `"AQC-NOPE"` → `is not an advanced-qualification challenge of the owner source [V1.2]` |
| hidden authoritative truth | 1020 | `/…/hidden_authoritative_truth` = `{statement, authoritative_refs}` | missing → `[V1.3]` |
| injected repository state | 1021 | `/…/injected_repository_state` = `{description, changes[≥1]}`, each change a typed `state_change` (`MOVED`/`RENAMED` force `from_path`) | missing → `[V1.4]` |
| expected detection | 1022 | `/…/expected_detection` = `{tiers[≥1] ^G[0-9]+$, signals[≥1], must_detect_before}` | missing → `[V1.5]`; `"whenever"` → pattern refusal `[V1.5]`; `"G9"` → `is not a Governance Health Scheduler tier of O5 (G0…G6) [V1.5]` |
| expected severity | 1023 | `/…/expected_severity` enum CRITICAL/HIGH/MEDIUM/LOW/INFO | missing → `[V1.6]`; `"quite bad"` → `is not one of […] [V1.6]` |
| expected impacted artefacts/nodes | 1024 | `/…/expected_impacted[≥1]` = `{ref, ref_kind enum, relation DIRECT|TRANSITIVE}` | missing → `[V1.7]`; free text → `is not of type "array" [V1.7]` |
| expected governed action | 1025 | `/…/expected_governed_action[≥1]` = `{action enum(13), target?, description}` | missing → `[V1.8]` |
| forbidden outcomes | 1026 | `/…/forbidden_outcomes[≥1]` = `{outcome, observable}` | missing → `[V1.9]` |

Gate V's lead-ins are covered too: line 1014 (`verifier-owned hidden oracle`) → `/custody` (owner role
`const FRESH_INDEPENDENT_VERIFIER`, `authored_independently_of_implementation` `const true`), `/visibility`
(`const HIDDEN`), `/repository`; line 1017 → `/fault_manifest/faults` (`minItems: 1`). Attacks
`type-06/07/08` (visibility `PUBLIC`, custody not independent, custody role `BUILDER`) and `sem-11` (empty
fault manifest) are all refused, tagged `[L1014]` / `[L1017]`.

W12.7 and the Gate W challenge are carried as `/…/artifact_flow` = `{required_inputs[≥1] (each needing a
version or a content digest), expected_propagation[≥1] (typed expected states)}`, **required** whenever a
fault's `class.capabilities` names a Gate W capability: `sem-09` → `required field 'artifact_flow' is
missing [W12.7]`.

### V2 — Hidden path-map oracle (Contract v3:1028–1036)

`/path_map_oracle` is required exactly when `repository.adoption_mode` is `BROWNFIELD` (line 1029):
`sem-10` → `required field 'path_map_oracle' is missing [L1029]`; the greenfield oracle without one is
accepted (`valid/oracle-greenfield.json`).

| Bullet | Line | Field | Attack → refusal |
|---|---|---|---|
| current artefact | 1030 | `/…/current_artefact` = `{path, content_sha256?}` | missing → `[V2.1]`; duplicate current path → `appears in more than one path-map entry` |
| correct classification | 1031 | `/…/correct_classification` (text) | missing → `[V2.2]` |
| authority | 1032 | `/…/authority` (text) | missing → `[V2.3]` |
| expected target path | 1033 | `/…/expected_target_paths[]` | missing → `[V2.4]`; and the action/target rules below |
| KEEP/MOVE/RENAME/SPLIT/MERGE/EXTRACT/RETIRE | 1034 | `/…/action` enum (plus B2's `DELETE_FROM_ACTIVE_TREE`, Contract v3:192) | missing → `[V2.5]`; `"leave it where it is"` → `is not one of […] [V2.5]` |
| expected references/consumers | 1035 | `/…/expected_references[]`, `/…/expected_consumers[]` | either missing → `[V2.6]` |
| sensitivity/indexing expectation | 1036 | `/…/sensitivity` (text), `/…/indexing_expectation` enum `INDEX_CURRENT|INDEX_HISTORICAL|NEVER_INDEX` | either missing → `[V2.7]`; `"probably index it"` → `is not one of […] [V2.7]` |

The action/target arithmetic is machine-checked, not described: `KEEP` with another target → `KEEP:
expected_target_paths must be exactly [the current path] [V2.4]`; `SPLIT` with one target → `SPLIT: two or
more target paths [V2.4]`; `DELETE_FROM_ACTIVE_TREE` with a target → refused `[V2.4]`.

### V3 — Hidden memory oracle (Contract v3:1038–1045)

All seven bullets are required arrays with `minItems: 1` and typed items; each missing one is refused with
its own element tag (`v3-01`…`v3-07` → `[V3.1]`…`[V3.7]`). Beyond presence, the format is contradiction-checked:

- the same ref in `must_be_indexed` and `must_never_be_indexed` → refused `[V3.1]`;
- a query whose `must_include` names never-indexed material, or names the same ref in `must_include` and
  `must_not_include` → refused `[V3.7]`;
- `status: SUPERSEDED` forces `superseded_by` (schema), and self-supersession is refused `[V3.4]`;
- V2 ↔ V3: `NEVER_INDEX` on an artefact `must_be_indexed` lists, or `INDEX_*` on one `must_never_be_indexed`
  lists → refused `[V2.7]`.

### V4 — Quantitative qualification scoring (Contract v3:1047–1060)

All twelve metrics are required fields of `/metrics` with types; each omission is refused with its element
tag (`v4-01`…`v4-12` → `[V4.1]`…`[V4.12]`). Ratios are `{numerator, denominator, value}` with the quotient
checked, or an explicit reasoned `{applicable: false, reason}` — never a silent omission:

- `value` ≠ `numerator/denominator` → `value 0.95 is not 1/2 [V4.1]`;
- numerator > denominator → refused `[V4.1]`;
- recall not equal to the detected/total the report's own per-fault outcomes give → `is 2/2; the per-fault
  outcomes give 1/2 [V4.1]`; likewise severity accuracy `[V4.3]` and impact-map accuracy `[V4.4]`;
- `false_positives.count` ≠ number of findings listed → refused `[V4.2]`; the three count metrics likewise
  (`count differs from the number of artefacts listed [V4.7]`);
- N/A discipline: `severity_accuracy` N/A while detections exist → `cannot be N/A: the report has outcomes
  to measure [V4.3]`; a greenfield report inventing a path-map ratio → `the oracle has no path-map oracle,
  so path-map accuracy is an explicit N/A [V4.5]`; a brownfield report claiming N/A → `the oracle has a
  path-map oracle, so path-map accuracy is measured [V4.5]`; N/A without a reason → schema refusal
  (`evidence/09-greenfield-and-na.out`).

Per-fault outcomes are internally consistent by rule: an undetected fault cannot claim a correct severity,
cannot claim impact-map credit, and must carry no detection record; a detected fault must record tier,
signal and severity.

## 4. Separation and custody (Contract v3:1062)

The sentence *"The permanent public qualification suite and fresh verifier hidden oracle must remain
separate"* is carried as a required `/separation` object with three locations, and is checked both as a
declaration and physically (`evidence/06-separation-attacks.out`):

| Attack | Result |
|---|---|
| A0 oracle in verifier custody, both trees clean | ACCEPTED, `scanned=2 findings=0` |
| declared `oracle_storage` nested in the public suite / in the qualification repository | `ORACLE_RECORD_INVALID … [L1062]` (samples `sep-01`, `sep-02`) |
| A1 oracle file stored inside the public suite | `ORACLE_SEPARATION_VIOLATED` — *the hidden oracle is stored inside the public qualification suite* |
| A2 oracle file stored inside the qualification repository | `ORACLE_SEPARATION_VIOLATED` |
| A3 a copy of the oracle document left in the public suite | `ORACLE_SEPARATION_VIOLATED` — *a hidden-oracle document lies inside …* |
| A10 the same copy re-serialised as YAML | `ORACLE_SEPARATION_VIOLATED` |
| A4 only the oracle **id** leaked into the repository | `ORACLE_SEPARATION_VIOLATED` |
| A5 only the oracle **digest** leaked into the public suite | `ORACLE_SEPARATION_VIOLATED` |
| A6 a hidden authoritative truth leaked **verbatim** into the repository | `ORACLE_SEPARATION_VIOLATED` |
| **A7/A8 the same manifest re-expressed as a governed record (`type: fault-manifest` / `hidden-memory-oracle`)** | **ACCEPTED — not detected** (finding `V1-OF-01`) |
| **A9 the hidden truth reflowed over two lines** | **ACCEPTED — not detected** (finding `V1-OF-01`) |
| **A11 fault ids and class ids leaked as plain text** | **ACCEPTED — not detected** (finding `V1-OF-01`) |

Inside a **governed** repository the picture is different and correct: a bare `type: fault-manifest` record
planted in a `gov init`-ed project is refused by the governance suite as `high | FM-0001 (fault-manifest) is
hidden Qualification Oracle material inside the governed repository` and disappears when the record is
moved aside (`evidence/12-governed-repo-record.out`). This is precisely the mechanism iteration-0 A0-V1-01
said was accepted; it is closed.

## 5. The G6 entry point

`gov health qualify` in a disposable `gov init` project (`evidence/07-g6-entry-point.out`; machine posture
`UNPROVISIONED`):

| Scenario | Result |
|---|---|
| conforming `FORMAT_SAMPLE` oracle + bound report | `RECORDED | counts_as_qualification=false purpose=FORMAT_SAMPLE posture=UNPROVISIONED health=YELLOW` |
| oracle missing a V1 field | `ORACLE_RECORD_INVALID` |
| report bound to the wrong oracle digest | `ORACLE_SCORE_BINDING_MISMATCH` |
| an injected fault left unscored | `ORACLE_SCORE_BINDING_MISMATCH` — *the oracle's fault "SMP-F-002" has no outcome — every injected defect is scored* |
| a score report supplied as the oracle | `USAGE` (typed) |
| unknown run kind | `USAGE` naming the four kinds of Contract v3:799 |
| oracle stored inside the **governed** repository (always a forbidden location) | `ORACLE_SEPARATION_VIOLATED` |
| only the oracle id leaked into the governed repository | `ORACLE_SEPARATION_VIOLATED` |
| `purpose: QUALIFICATION` on this unprovisioned machine | `QUALIFICATION_MACHINE_UNPROVISIONED` (OD-P2-02 requirement 4) |
| `QUALIFICATION` oracle + `FORMAT_SAMPLE` report, and the reverse | `ORACLE_SCORE_BINDING_MISMATCH` — *a report and its oracle must have the same purpose (a FORMAT_SAMPLE is never scored as QUALIFICATION)* (`evidence/13-purpose-laundering.out`) |

A `FORMAT_SAMPLE` therefore never counts as qualification: `counts_as_qualification` is
`purpose == "QUALIFICATION" && provisioned`, and both halves were attacked.

What the recorded G6 result carries was checked for leakage: the persisted health record
(`gov health show`) holds a one-way `commitment_sha256`, the `format_sha256`, the purpose, the scanned
separation roots, the report's canonical digest, `binding_verified: true` and the twelve V4 numbers — and a
`grep` of the whole governed repository for the oracle id, the oracle's canonical digest, a fault id and a
hidden truth returns **0 occurrences each**.

## 6. Method and limits

- Built in this worktree (`CARGO_BUILD_JOBS=2 cargo build --release`), `target/release/gov`.
- Independent evidence is everything under `evidence/` and `samples/`; `evidence/RUN-ALL.sh` re-runs it.
- Builder claims under `release/capability-baseline/repair-1/**` were treated as claims; the builder's own
  samples were not reused. The sample corpus here was authored from Contract v3 Gate V and the schema
  (`evidence/03-make-samples.py`, `evidence/04-make-report-samples.py`). The nine `qualification_oracle`
  unit tests pass (`cargo test --release --lib qualification_oracle` → 9 passed, 0 failed) and are cited as
  **regression** evidence only (O3).
- The definition is compiled into the binary with `include_str!`, so the product's own
  `ORACLE_FORMAT_INCOMPLETE` guard (which refuses a format that fails to map a Gate V element) cannot be
  exercised without rebuilding from a mutated definition — that would mean modifying product source, which
  this role never does. Coverage was therefore established directly and independently against the
  owner-source bytes (§3), which is what AC-6 asks; the guard's behaviour rests on a builder test.
- `rm` is denied in this environment. Two artefacts were **moved aside** rather than deleted: an
  `evidence/__pycache__` directory and the planted `FM-0001-fault-manifest.md` record, both moved into the
  session scratchpad. No product source was modified.

## 7. What a Phase-4 qualification author still has to invent

The format lets an author write a real hidden oracle and score report without inventing any field the
contract requires — every V1–V4 element has a home. What it does **not** supply:

1. **Vocabularies for three V2 bullets.** `correct_classification`, `authority` and `sensitivity` are free
   text with no binding to the product's own path-map classifications, authority states or
   `DATA_SENSITIVITY` levels; `expected_detection.signals` and `must_detect_before` are free text too.
   A scorer must map strings by hand. (Finding `V1-OF-03`.)
2. **Nothing to measure V4.10–V4.12 against.** The oracle format has no place to declare chaos/soak
   scenarios, expected human-gate decisions, or expected task/readiness outcomes, yet
   `recovery_chaos_pass_rate`, `human_gate_correctness` and `task_readiness_correctness` must be reported.
   The author must define those expectations outside the format. (Finding `V1-OF-02`.)
3. **No per-path-map-entry outcome structure.** V4.5's numerator has no analogue of `per_fault_outcomes`,
   so per-entry correctness is the scorer's assertion. (Finding `V1-OF-02`.)
4. **`retrieval_metrics.k` is not reconciled** with the oracle queries' own `top_k`; with queries of
   differing `top_k` the author must choose what `k` means. `k = 99` and `k = 1` against a `top_k = 5` oracle
   are both accepted (`evidence/14-retrieval-k-and-tiers.out`). (Finding `V1-OF-02`.)
5. **Per-run conventions:** the four `QUALIFICATION_KINDS` (`synthetic-repository`, `chaos`, `soak`,
   `hidden-test`) all consume the same oracle shape; how a chaos or soak run maps onto a fault manifest is
   the author's convention.
6. **Two documents, deliberately.** One oracle per repository at one commit, so Repo A and Repo B need two
   oracle documents and two score reports; the format supports this and the greenfield shape was exercised.

None of these is a field the contract names, so none blocks AC-6; all are recorded so that the Phase-4
handoff does not rediscover them.

## 8. Findings

| id | severity | blocking | label | title |
|---|---|---|---|---|
| `V1-OF-01` | MEDIUM | no | MATERIALLY_NEW | the hidden-oracle leak scan misses governed-record types and any reformatting of a hidden truth |
| `V1-OF-02` | MEDIUM | no | MATERIALLY_NEW | four V4 metrics, three count-metric ref lists and two per-fault judgements are not bound to the oracle |
| `V1-OF-03` | LOW | no | MATERIALLY_NEW | three V2 bullets and two V1 detection sub-fields are free text with no vocabulary |
| `V1-OF-04` | INFO | no | MATERIALLY_NEW | `gov health history` rows report `qualification: null` for G6 results |
| `V1-OF-05` | INFO | no | MATERIALLY_NEW | the acceptance status lives inside the digested definition |
| `V1-OF-06` | INFO | no | MATERIALLY_NEW | V1–V3 carry no health-scheduler tier in the evidence map |

Full statements, evidence and reproduction in `findings.yaml`.

## 9. Iteration-0 disposition

`BC-P2-51 — Qualification Oracle format absent` (finding `A0-V1-01`, HIGH; blocked AC-2, AC-6, AC-10):
**CLOSED**. Each limb of its mechanism was re-established on this candidate, with my own evidence:

- *"No machine-checkable definition … exists"* → §3: the definition exists and covers all 35 bullets and 5
  statements with required typed fields; 93/93 samples behaved.
- *"a fault-manifest record lacking every V1 field is accepted"* → §4: exactly that record is now refused
  `high` by the governance suite inside a governed repository (`evidence/12-governed-repo-record.out`).
- *"GATE-P2-ORACLE-FORMAT is NOT_SATISFIED"* → this review is the fresh independent acceptance frozen
  contract §9.2 requires, before any hidden fault exists.
- *"V1–V4 have zero evidence owners"* (AC-10 limb) → every one of the 35 bullets now carries at least one
  evidence owner in `tests/governance/capability-evidence-map.yaml`
  (`evidence/11-evidence-owners-v1-v4.out`; 0 bullets with zero owners). V1–V3 carry an empty
  `health_scheduler_tiers` list — noted as `V1-OF-06` (INFO), not a violation, since AC-10 counts independent
  audit and held-out evidence as owners.

See `prior-findings-disposition.yaml`.

---

*Run P2-AR-0045, fresh independent oracle-format reviewer. Evidence directory:
`release/capability-baseline/verify-1/oracle-format/`. No product source modified; no hidden fault generated.*
