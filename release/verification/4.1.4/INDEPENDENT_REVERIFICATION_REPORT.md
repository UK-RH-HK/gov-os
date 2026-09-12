# Independent OS Re-Verification Report — agentic-engineering-os repair candidate 4.1.4

| | |
|---|---|
| **Verdict** | **OS_RELEASE_CANDIDATE_REJECTED** (repairable; builder repair delta in §13) |
| Verifier | Independent Governance OS Verifier and Test Author — fresh session, no builder context, no continuation of either previous verifier session (Claude Opus 5) |
| Date | 2026-09-12 |
| Candidate | branch `release/4.1.4-rc1`, tag `v4.1.4-rc1`, commit `47d8394b945bcfd9f35a5fee80836e424a4570dc`; payload `release/releases/4.1.4/` (release_commit `c6b594ba…d8ab`, release_hash `e5e2f2c7…37d2b`) |
| Toolchain | rustc/cargo 1.98.1, clippy 0.1.98, rustfmt 1.9.0, Python 3.12.3 (harnesses only), git 2.43.0, Linux x86_64 WSL2 (`evidence/toolchain-and-binaries.txt`) |
| Independence | Nothing in the builder's or previous verifiers' reports was taken on trust. Verification ran against a **fresh `git clone` of the candidate tag** into a scratch directory; `cargo build --release` and the full `cargo test` suite were executed there. Both previous harnesses were re-run **byte-identical** (sha256 confirmed against the verifier commits `9563192` / `9cb05d8`). Sixteen new scenarios (`heldout-v3/harness_v3.py`) were authored in this session, driven only through the `gov --json` contract, before reading the builder's certification tests. |
| Artefacts | `heldout-v3/` (new harness, results, log), `prev-harness-reruns/` (both unchanged harnesses), `evidence/` (clean build, full test run, clippy, rustfmt, pytest, 4.1.2 worktree build, toolchain + `ldd`), `VERDICT.md` |
| Not modified | No implementation source, kernel data, fixture, builder test, released payload or previous-verifier artefact was modified. The only additions are under `release/verification/4.1.4/`. The 4.1.4 manifest certification block was **not** edited by this session (same convention as the 4.1.3 verification); `VERDICT.md` carries the exact block for the release owner. |

## 0. Summary

The second repair iteration is substantially successful. Every CRITICAL/HIGH finding of the 4.1.3 re-verification —
**C-N1** (CIT approval without an answered gate), **H-N1** (project overlay weakening security/authority policy) and
**H-N2** (ungoverned plugin execution) — was repaired at the root cause, and each survived adversarial attack
sets that the builder did not have. All nine CRITICAL/HIGH findings of the original 4.1.2 verification remain repaired.
Both previous harnesses reproduce exactly the results the builder claims (36/1/1/0 and 13/2/0/0), the two remaining
failures are genuinely artefacts of reading the immutable, rejected 4.1.3 payload, and the equivalent 4.1.4 behaviour is
independently confirmed repaired. The complete 4.1.2 → 4.1.3 → 4.1.4 upgrade and the 4.1.4 → 4.1.3 → 4.1.2 rollback
chain work, with byte-identical overlay and lock restoration, ledger entries and snapshot consumption.

The candidate is nevertheless **rejected** because three freshly authored held-out scenarios expose defects the repair
did not touch, one of which re-opens the exact invariant H-N2 was raised to protect:

1. **HIGH — a plugin descriptor still authorises itself.** `TOOL_POLICY.plugins.min_authority: L2` is documented in the
   kernel as "hand-declared (unregistered) descriptors execute only for roles at/above this level", and API-0001 §governance
   states that "a descriptor is not an authorisation". In fact two attacker-controlled fields *inside the descriptor* —
   `approved_roles: ["all"]` and `provenance.registered_at: "<any string>"` — both bypass that floor. An **L0
   `independent-auditor`** dropped a three-line YAML into `governance/project/plugins/` and obtained **arbitrary command
   execution** during `gov rebuild-memory` (an L0 operation). `gov doctor` D028 reported "no plugin problems" throughout
   (VV-04). The L0 roles are precisely the independence roles (`independent-auditor`, `migration-reviewer`,
   `migration-verifier`, `memory-verifier`), so the defect lands on the independence model the protocol depends on.
2. **HIGH — constitutional floors are read from unverified installed-kernel files.** `policy_precedence::load` reads
   `governance/kernel/policies/POLICY_PRECEDENCE.yaml` from disk and trusts it. Editing that file in an installed project
   made every weakening override apply again and let an **L0 role create tasks** (VV-03c). Editing the kernel
   `SECURITY_POLICY.never_index_classes` removed a restricted-class exclusion at index time (VV-14). The tampering *is*
   detected — D003 CRITICAL and the audit finding "kernel payload modified in place (INV-007)" — but no enforcement path
   consults that result, and `load()` already fails closed when the file is **absent** (embedded fallback), so the
   intended posture is clear and the present-but-tampered case is an omission rather than a design choice.
3. **MEDIUM — `PROJECT_EXCEPTIONS` decisions are self-attested.** `policy.rs` only checks that the `decision` field is a
   non-empty string. An exception naming `D-DOES-NOT-EXIST` was applied (VV-03a). The blast radius is the
   `exception_relaxable` key set, which includes `BUDGET_POLICY.defaults.*`, `CHECKPOINT_POLICY.watchdog.*` and the
   `MEMORY_POLICY.regression.*` quality floors — so a repository can silently disable its own retrieval-regression gates,
   checkpoint watchdogs and spend caps with a fabricated governance reference. Security and authority keys are never
   relaxable, so this cannot reach the constitutional floors.

None of the three needs an architectural rewrite; each is a bounded change with an acceptance test already written
(§13). HV-08b remains not a blocker (§6). The architecture is materially complete (§9): the deterministic core is
Rust-only with no Python/Node dependency, memory is a genuine multi-layer fabric rather than a vector index, all derived
state deletes and rebuilds deterministically across machines, and model/component choices are pinned and replaceable.

## 1. Reproduction of builder evidence (fresh clone, clean build)

Executed in `/tmp/.../scratchpad/clone414`, a `git clone` of the candidate repository checked out at tag `v4.1.4-rc1`
(`git rev-parse HEAD` = `47d8394b945bcfd9f35a5fee80836e424a4570dc`, `git status --porcelain` empty).

| Suite | Builder claim (`docs/EVIDENCE.md`) | This session | Evidence |
|---|---|---|---|
| `cargo build --release` from a fresh clone | PASS (exit 0) | **PASS**, exit 0, 38.0 s, 0 warnings | `evidence/clean-build.log` |
| Rust unit tests (gov-runtime) | 16 passed / 0 failed | **16 passed / 0 failed** | `evidence/clean-test.log` |
| Certification harness | 44 passed / 0 failed | **44 passed / 0 failed**, 5.63 s | `evidence/clean-test.log` |
| Python capability plugin tests | 4 passed | **4 passed**, 0.13 s | `evidence/pytest.log` |
| Clippy `--workspace --all-targets` | exit 0, 0 warnings, 0 errors | **exit 0, 0 warning/error lines** | `evidence/clippy.log` |
| `cargo fmt --all -- --check` | PASS | **exit 0, no diff** | `evidence/fmt.log` |
| `gov release verify release/releases/4.1.4` | ok | **ok**: 0 modified, 0 missing, 0 added; certification `READY_FOR_INDEPENDENT_REVERIFICATION` | VV-07 |
| Payload vs `framework/` + `migrations/` + `tools/` at the release commit | — | **identical**; `git diff c6b594b..HEAD -- framework migrations tools` empty; `c6b594b` is an ancestor of HEAD | VV-07 |
| `gov release build --version 4.1.4` into a temp dir | — | **reproduces** the same `release_hash` and every `file_hash`; rebuilding in place is refused (`RELEASE_IMMUTABLE`) | VV-07 |
| Verifier artefacts untouched by the builder | claimed | **confirmed**: `release/verification/4.1.2/heldout/harness.py` sha256 `a01155de…b1f9c` and `release/verification/4.1.3/heldout-new/harness_v2.py` sha256 `4ad69a8d…52bb` are byte-identical to the versions at commits `9563192` and `9cb05d8` | `evidence/toolchain-and-binaries.txt` |
| Binary dependencies | "no Python to operate the core" | **confirmed**: `ldd` shows only `libgcc_s`, `libm`, `libc`, `ld-linux` | `evidence/toolchain-and-binaries.txt` |

Every implementer claim in `docs/EVIDENCE.md` that this session could check reproduced exactly. The evidence vocabulary
requested at 4.1.3 §11 (PASS / FAIL / NOT_AVAILABLE / NOT_RUN / NOT_APPLICABLE) is present and used honestly.

## 2. Previous held-out harnesses — unchanged reruns

Both harnesses were executed unmodified against the freshly built candidate, with `GOV_VERIFIER_OUT` redirected so that
no previous-verifier artefact was written. Harness v2 was given a 4.1.2 binary built in a detached worktree at `8ad06be`
(`evidence/build-412.log`), exactly as its own reproduction instructions require.

| Harness | Original verifier run | Builder's rerun (claimed) | **This session** |
|---|---|---|---|
| First (`release/verification/4.1.2/heldout/harness.py`, 38 scenarios) | 12 PASS / 25 FAIL / 1 INFO / 0 ERROR | 36 / 1 / 1 / 0 | **36 PASS / 1 FAIL / 1 INFO / 0 ERROR** |
| Second (`release/verification/4.1.3/heldout-new/harness_v2.py`, 15 scenarios) | 6 PASS / 9 FAIL / 0 INFO / 0 ERROR | 13 / 2 / 0 / 0 | **13 PASS / 2 FAIL / 0 INFO / 0 ERROR** |

First harness: the only FAIL is **HV-08b** (§6). HV-08 remains INFO with recall@k 0.833, MRR 0.715, stale 0.0,
superseded 0.0, forbidden violations 0 — unchanged from the original run. No previously passing scenario regressed.

Second harness: the only FAILs are **NV-09** and **NV-19** (§7). NV-01, NV-02, NV-03, NV-04, NV-05, NV-07 and NV-08 —
the seven scenarios that carried the 4.1.3 rejection — all now PASS, and the four controls (NV-06, NV-10, NV-12, NV-13,
NV-16, NV-17) still PASS.

## 3. Previous-finding repair matrix (independently re-derived)

Each row was verified by reading the implementation, then attacking it with scenarios the builder did not have.

| ID | Claimed repair | Independently observed (source + behaviour) | Independent attack result | Verdict |
|---|---|---|---|---|
| **C-N1** CIT approval without an answered gate | `cit/mod.rs::authoritative_gate()` used by both `approve` and `execute`; approval derived from the gate answer; `gates::answer` rejects the CIT on any non-A option; `gates::revoke` added | `authoritative_gate` (`runtime/src/cit/mod.rs:372-450`) requires: gate exists, is a `human-gate`, `cit` field equals this CIT, `presented_in_chat`, status `ANSWERED`, option `A`, and an **ACTIVE decision record deriving from the gate**. `approve` (`:459`) derives `human_approved` from `answer.by_kind`, refuses `APPROVAL_METHOD_MISMATCH` when a caller claims `--method human` over an agent answer, and marks the CIT `REJECTED` on `GATE_DECLINED`. `execute` (`:790`) re-runs `authoritative_gate` and cross-checks gate id, decision id, `answered_at` and `answered_by` against the stored approval | **VV-01, all nine sub-cases refused**: unpresented → `GATE_NOT_PRESENTED`; presented-unanswered → `GATE_NOT_ANSWERED`; decline B → CIT `REJECTED`, approve and execute refused, no file written; gate revoked after approval → CIT back to `SIMULATED`, execute refused; gate answer hand-edited after approval → `APPROVAL_STALE`; approval object forged directly into the CIT record → refused, no file written; a gate raised for another CIT → `GATE_MISMATCH`; an agent answering an R4 gate → `AUTHORITY_DENIED`; L1 role approving → `AUTHORITY_DENIED`; L1 role recording a human answer → `AUTHORITY_DENIED` | **REPAIRED** (robust under attack) |
| **H-N1** overlay weakens security/authority policy | kernel `POLICY_PRECEDENCE.yaml` + `policy_precedence.rs` evaluated at policy-load time; refusals recorded, effective policy unchanged; doctor D027 CRITICAL | 82 rules, `default_mode: immutable` (deny by default), modes immutable/floor/ceiling/additive/shrink_only/strengthen_only_bool/overridable; `policy.rs::PolicySet::load` evaluates every override and exception and records `applied_overrides` / `refused_overrides` | **VV-02: all 15 weakening overrides refused** (authority levels ×3, `never_index_classes`, `never_export_classes`, `secret_path_patterns`, `auto_approve_max_radius`, `snapshot_before_execute`, `must_be_presented_in_chat`, agent radius, `plugins.min_authority`, `require_valid_descriptor`, test-status widening, `archive_mutation`, and `POLICY_PRECEDENCE.default_mode` itself). Effective `create_task` stayed L2, effective `never_index_classes` stayed `[secret, restricted]`, an L0 role was denied, a restricted-class file was excluded with reason `sensitivity:restricted` and was not retrievable, D027 CRITICAL listed all 15 with reasons. VV-13: a tier floor could be raised but not lowered | **REPAIRED** — but see V-H2/V-M1: the rule file itself is trusted unverified, and exception decisions are unverified |
| **H-N2** plugin descriptors are ungoverned executables | `plugin-descriptor` schema 1.1.0, `capabilities/governance.rs::authorize` (authority floor, approved_roles, permission classes, registration gate for elevated permissions, health, pin, drift), `gov plugins register/list/health`, doctor D028 | `authorize` (`runtime/src/capabilities/governance.rs:181`) performs the checks as described and every execution path (indexer, retrieval, benchmark, code intelligence, `capabilities invoke`) goes through `plugin_set` | **VV-04: 10 of 13 attacks refused** — malformed descriptor rejected; plain unregistered descriptor not usable by L1 and not executed during an L0 rebuild; wrong declared pin → `PLUGIN_PIN_MISMATCH`; implementation drift after first governed use → `PLUGIN_PIN_MISMATCH`; elevated permissions without a registration gate → `PLUGIN_NOT_APPROVED` (**even with `approved_roles: ["all"]`**); registration by L1 → `AUTHORITY_DENIED`; `capabilities invoke` by L0 → `AUTHORITY_DENIED`. **Three failed**: `approved_roles: ["all"]` and `provenance.registered_at` both bypass `min_authority`, giving an L0 role arbitrary command execution during `rebuild-memory`, and D028 reports "no plugin problems" | **PARTIALLY REPAIRED — the authority floor is still self-attested (V-H1, §11)** |
| **M-N1/M-N2** lock provenance | `kernel::release_commit_for_source`, `source_label`, lock schema 1.1.0 with `installed_at_commit` | NV-08 PASS across three install paths; verified again in the chain run: after update the lock carries `release_commit: 78f6853…` / `c6b594b…` (the release commits, not the consumer HEAD), `source: release:agentic-engineering-os@4.1.3` / `@4.1.4` (logical), and `installed_at_commit` separately | Chain run §5 | **REPAIRED** |
| **M-N3 / NV-19** migration substance | new op `set_overlay_rule`; `M-4.1.3-4.1.4` performs the tightening and declares `overlay_template_changes`; `check_substance` refuses a new release whose migration neither performs nor declares a template change | **VV-06**: `M-4.1.3-4.1.4` operations are `note, set_overlay_rule, set_lock_field, require_index_rebuild, regenerate_adapters`; the `set_overlay_rule` op sets `REPOSITORY_CONTRACT.yaml` `governance/tests/**` `lexical_index: false` with `add_if_missing`, and `overlay_template_changes` declares it with a reason. No overlay template changed between 4.1.3 and 4.1.4 without being declared. The released `M-4.1.2-4.1.3` operations are **unchanged** (4 ops, identical to the 4.1.3 payload); only its description changed, with an `amendments` history | VV-06 PASS; chain run step 3 observed the op applied (`skipped: already_set` when reconciliation had already delivered it) | **REPAIRED** |
| **M-N4 / NV-05** self-attested mutation scope | `tasks::snapshot_tree` at claim, `observed_mutations` at close | **VV-08**: an undeclared out-of-scope edit to `src/lib.rs` under `allowed_paths: docs/**` → `MUTATION_SCOPE_VIOLATION` with `undeclared`, `out_of_scope`, `reported`, `observed` and the claim baseline commit in the details; declaring it does not make it in scope → still refused | VV-08 PASS | **REPAIRED** |
| **M-N5 / NV-07** record lost after `git mv` | relocation handling in `indexer.rs` | NV-07 PASS in the unchanged rerun | | **REPAIRED** |
| **M-N6** API-0001 promised a silent fallback | D-0005; API-0001 v1.1 with history | `spec/interfaces/API-0001.yaml:9-14,39-41` — v1.1, `amended_by: [D-0005]`, invariant now reads "embed and rerank fail closed … the core never substitutes the built-in embedder for a pinned plugin (D-0005 supersedes the v1 fallback statement)"; `code_intel` degrades with a recorded degradation | source inspection | **REPAIRED** |
| **M-N7** branch/tag provenance | tags + manifest provenance | `git tag --points-at HEAD` = `v4.1.4-rc1`; branch `release/4.1.4-rc1`; `v4.1.3-rc1` at `26ab5b6`; manifest `provenance.release_branch` / `release_tag` populated | VV-07 PASS | **REPAIRED** |
| **M-N8** real 4.1.2 → 4.1.3 path untested | `repair2::genuine_412_consumer_updates_through_413_to_414_and_rolls_back_with_ledger` | present and green in the clean-clone run; independently re-executed end-to-end in §5 | | **REPAIRED** |
| **M-B1** no paraphrase-capable candidate, no benchmark record | D-0006, optional `embed_sentence_transformers.py` template, `RES-0001` | `spec/decisions/D-0006.yaml` records option B with rationale, the candidate classes adopters should evaluate and why nothing is bundled; `spec/research/RES-0001.yaml` carries measured rows (recall, MRR, precision, stale/superseded, symbol recall, latency, index cost) from `gov memory benchmark --record` | source inspection; NV-06 PASS | **ADDRESSED** (§6) |
| **L-N1 / NV-09** duplicate kernel YAML key | duplicate removed; strict scan in the builder suite | **VV-05**: 192 kernel YAML files across `framework/`, `migrations/` and all three released payloads loaded with a duplicate-key-rejecting loader. **The only duplicate in the repository is in the immutable 4.1.3 payload.** 4.1.4 and `framework/` are clean; `schema_versions` agree across `KERNEL.yaml`, `KERNEL_MANIFEST.json` and `manifest.json`; `manifest.yaml` == `manifest.json`; released `KERNEL.yaml` == `framework/KERNEL.yaml` | VV-05 PASS | **REPAIRED** |
| **L-N2** no rollback ledger; second rollback re-applies | ledger entry, `consumed.json`, `SNAPSHOT_CONSUMED`/`SNAPSHOT_MISSING` | §5: each rollback appends a full entry to `spec/reports/framework-updates.jsonl` (source/target, identity, authority level, reason, migrations reverted, resulting lock, verification, snapshot); a third rollback is refused with `SNAPSHOT_MISSING` | §5 | **REPAIRED** |
| **L-N3** `memory select` derived `human_approved` from `--by` | derived from the acting role's authority level | source inspection (`memory/benchmark.rs`) | | **REPAIRED** |
| **L-N4** self-declared role | documented as a trust boundary | `docs/ARCHITECTURE.md` §4.8 | | **DOCUMENTED** (§12) |
| **L-N5** stale docs | updated | spot-checked | | **REPAIRED** |
| **L-N6** rustfmt/clippy | formatted, warnings fixed | reproduced clean in §1 | | **REPAIRED** |

## 4. HV-08b, NV-09 and NV-19 — independent determination

### 4.1 HV-08b — not a release blocker (confirmed)

**Question.** Is token-overlap-free paraphrase retrieval failing with the pinned baseline embedder a blocker?

**Independent finding: no.** Framework §14.3 forbids hard-coding an embedding/reranking model into the constitutional
standard and requires per-repository benchmark-and-pin instead; the deliverable is therefore the *mechanism*, not a
bundled model. The mechanism exists and is executable (`gov memory benchmark` → research record → `gov memory select` →
decision with alternatives → overlay pin → full rebuild, with `regression.min_queries` preventing an unmeasured green),
and it was proven end-to-end by NV-06, which reached paraphrase recall 1.0 with a candidate neither the builder nor the
first verifier shipped. The residual gap the 4.1.3 report raised as M-B1 — no recorded rationale and no benchmark
evidence in the canonical repository — is now closed by `D-0006` and `RES-0001`, plus the fail-closed
`embed_sentence_transformers.py` template. The first harness's note attached to HV-08b ("no comparative benchmark
mechanism exists") is factually stale and should not be read as a current finding. **HV-08b remains FAIL by
construction of the baseline embedder and is accepted as non-blocking.**

### 4.2 NV-09 — fails only because it reads the immutable 4.1.3 payload; repaired in 4.1.4

`harness_v2.py:535-554` opens `release/releases/4.1.3/kernel/KERNEL.yaml` by a hard-coded path (`REL413`). The duplicate
key `schema_versions.release-manifest` lives in that released payload, which the release protocol forbids changing.
Independently re-derived with my own strict loader over **every** kernel YAML in the repository (VV-05, 192 files):
the 4.1.4 payload, the 4.1.2 payload, `framework/` and `migrations/` are all free of duplicate mapping keys; the sole
occurrence is the 4.1.3 payload. Manifest agreement holds for 4.1.4. **The defect is genuinely repaired; the FAIL cannot
change without mutating a released payload.**

### 4.3 NV-19 — fails only because it reads the immutable 4.1.3 payload; repaired in 4.1.4

`harness_v2.py:397-411` reads `REL413/kernel/migrations/M-4.1.2-4.1.3.yaml` and `REL413/RELEASE_NOTES.md`, and compares
the 4.1.2 and 4.1.3 overlay templates. All three inputs are frozen released artefacts. Independently re-derived for the
current release (VV-06): `M-4.1.3-4.1.4` **performs** the contract tightening through a real `set_overlay_rule`
operation and **declares** it in `overlay_template_changes`; no overlay template changed between 4.1.3 and 4.1.4
without an operation or a declaration; the released `M-4.1.2-4.1.3` keeps its four operations byte-for-byte and gained
only a truthful description plus an `amendments` history. Behaviourally: in the chain run (§5) a genuine 4.1.2 consumer
upgraded to 4.1.3 by the 4.1.4 binary had the rule reconciled
(`overlay_keys_changed: ["reconciled:REPOSITORY_CONTRACT.yaml.paths[pattern=governance/tests/**].lexical_index"]`), and
at 4.1.4 the held-out file is not indexed. **The defect is genuinely repaired; the FAIL cannot change without mutating a
released payload.**

**Recommendation for the release owner:** record both scenarios as *frozen-input failures* in the 4.1.4 evidence with a
pointer to VV-05/VV-06, rather than leaving two bare FAILs in the totals.

## 5. Complete 4.1.2 → 4.1.3 → 4.1.4 upgrade and rollback chain (independently executed)

A governed project was created **by the 4.1.2 binary** (built from `8ad06be`) from the greenfield fixture, populated
(`rebuild-memory`, a project-specific overlay customisation, a specification record), and then driven by the 4.1.4
candidate binary.

| Step | Observed | Verdict |
|---|---|---|
| 4.1.2 install | lock `version: 4.1.2`, `release_commit e8ca71d…`, `release_hash 9964830b…`; 151 artefacts indexed | baseline |
| 4.1.4 binary opens a 4.1.2 project | `doctor` UNHEALTHY with the correct reasons (D005 CLI/kernel mismatch, D010/D025 index pin mismatch, D020 adapters stale, D021 suite obsolete) | correct |
| `update --check` → 4.1.3 | `compatible: true`, `certification: REJECTED`, `migration_path: [M-4.1.2-4.1.3]`, `human_gate_required: true` | correct — the consumer is told the target release is rejected |
| `update --apply` without approval | refused, gate `HDG-0001` raised | correct |
| `update --apply --approve --by owner --role human` **before** any gate is presented/answered | **refused**: `applied: false`, `"human gate not presented/answered (INV-008): --approve is not a substitute for an answered gate record"`, lock unchanged. Re-verified by me on a pristine project after a subagent reported the opposite; the subagent's project already carried an answered gate | correct (claim of a bypass **refuted**) |
| gate present → `decide --option A` → apply | applied; `overlay_keys_changed` records the contract reconciliation; lock `version 4.1.3`, `release_commit 78f6853…`, `source release:agentic-engineering-os@4.1.3`, `installed_at_commit` separate; **project overlay byte-identical**, **`spec/` records byte-identical** | correct |
| 4.1.3 → 4.1.4 with the 4.1.2→4.1.3 gate still answered | **refused**; a *new* gate `HDG-0002` is raised for the new transition. An answered gate authorises exactly its own transition | correct |
| 4.1.3 → 4.1.4 after its own gate | applied; `M-4.1.3-4.1.4` operations executed; lock `version 4.1.4`, `lock_schema_version 1.1.0`, `release_commit c6b594b…`; overlay and `spec/` byte-identical | correct |
| gate answered **B** (decline) then `--apply --approve` | `applied: false`, lock stays 4.1.2 | correct |
| held-out file at 4.1.4 | `governance/tests/**` carries `lexical_index: false` (and semantic/graph/code false); the file is not indexed and does not appear in retrieval | correct |
| rollback 4.1.4 → 4.1.3 | `rolled_back_to: 4.1.3`, `snapshot_consumed: true`, `kernel_ok: true`; full ledger entry in `spec/reports/framework-updates.jsonl` (from/to, the rolled-back update, actor, role, **authority level L5**, reason, `migrations_reverted`, `resulting_lock` incl. lock hash, verification block); lock and all seven overlay files **byte-identical** to the saved 4.1.3 state | correct |
| rollback 4.1.3 → 4.1.2 | same; lock and overlay **byte-identical** to the original 4.1.2 state | correct |
| third rollback | refused: `SNAPSHOT_MISSING` — "every rollback consumes its snapshot" | correct |
| multi-machine after the chain | machine A and machine B `manifest_hash` identical (`aac8f5b5…`), 162 artefacts / 326 chunks / 318 vectors / 12 symbols on both | correct |
| re-apply the same release | `applied: false`, `reason: "already up to date"`, `up_to_date: true` | correct |
| apply an **older** release (4.1.2 kernel onto 4.1.4) | `applied: false`, `downgrade: true`, `compatible: false`, `migration_path_complete: false`; nothing changed | correct |

Two cosmetic observations, recorded as LOW (§11): the refusal envelopes for decline / up-to-date / downgrade return
`ok: true` with `applied: false` (a caller must read `applied`, not `ok`); and `framework.lock.source` is a logical
release label after any `update`, but the **4.1.2-era `init`** wrote an absolute host path — that historical value is
faithfully restored on rollback to 4.1.2, which is correct behaviour for a rollback but means a 4.1.2-origin lock keeps
a host-specific string until the next update. The 4.1.4 `init` writes `source: source:agentic-engineering-os@4.1.4`.

## 6. New held-out test register (authored in this session)

Harness `heldout-v3/harness_v3.py`; results `heldout-v3/results.json`; log `run-full.log`. **13 PASS / 3 FAIL / 0 ERROR.**
Every scenario is black-box through `gov --json`; none was known to the builder or to either previous verifier.

| ID | Requirement challenged | Attack | Result |
|---|---|---|---|
| VV-01 | INV-008/INV-011, framework §47.2/§52 | nine attacks on CIT gate integrity: unpresented, presented-unanswered, declined, revoked-after-approval, answer tampered after approval, approval object forged into the CIT record, a gate raised for another CIT, agent answer laundered as human, L1 approving and L1 relaying a human answer | **PASS** (all refused with specific codes; nothing written) |
| VV-02 | framework §21, INV-006 | 15 simultaneous weakening overrides in `PROJECT_POLICY.policy_overrides`, incl. `POLICY_PRECEDENCE.default_mode` itself; behavioural probes for L0 task creation and restricted-class indexing | **PASS** (all 15 refused, effective policy unchanged, L0 denied, restricted excluded, D027 CRITICAL) |
| VV-03 | exceptions are governed decisions; the precedence rules themselves | (a) exception naming a non-existent decision on a relaxable key; (b) exception on an authority key; (c) kernel `POLICY_PRECEDENCE.yaml` deleted; (d) kernel `POLICY_PRECEDENCE.yaml` tampered to `overridable` | **FAIL** — (a) applied; (b) refused ✔; (c) embedded fallback, still refused ✔; (d) weakening applied and an **L0 role created a task** |
| VV-04 | framework §28–32, TOOL_POLICY.plugins, API-0001 §governance | 13 descriptor attacks: malformed, unregistered ×2 roles, self-declared `approved_roles`, forged `provenance.registered_at`, wrong declared pin, content drift, elevated-without-gate, elevated + self-declared roles, registration by L4/L1, `capabilities invoke` by L0 | **FAIL** — 10 refused; `approved_roles` and forged `provenance` bypass the authority floor and **execute an arbitrary command as L0**; D028 silent |
| VV-05 | kernel data hygiene | strict duplicate-key load of all 192 kernel YAML files in the repository + manifest agreement for 4.1.4 | **PASS** (only the immutable 4.1.3 payload is affected) |
| VV-06 | migration record integrity | does `M-4.1.3-4.1.4` perform what it claims; were released migration operations altered | **PASS** |
| VV-07 | protocol §8, framework §75D | verify, payload vs release commit, reproduction into a temp dir, in-place rebuild refusal, tag/branch provenance | **PASS** |
| VV-08 | framework §25/§42 | undeclared out-of-scope edit; declared out-of-contract edit; a `.gitignore`d out-of-scope write | **PASS** (both scored cases → `MUTATION_SCOPE_VIOLATION`; the gitignored case is recorded as a boundary, not scored) |
| VV-09 | rebuildability | delete the derived store; delete the entire `.governance-runtime`; rebuild on a second machine | **PASS** (identical `manifest_hash` in all four states; claims survive a partial wipe) |
| VV-10 | framework §75E, LEARNING_POLICY | PROJECT-scope lesson export; identifier stripping; a secret-bearing lesson; L1 submission | **PASS** (`UPSTREAM_SCOPE`; export gate failed closed; no secret, customer marker or identifier in any artefact; secret file not retrievable) |
| VV-11 | fresh-agent reconstruction | `status` / `context compile` / `continue` on a fresh clone with a new session id | **PASS** (identical `deterministic_hash` `9bbd07fa…`, identical `next_action`) |
| VV-12 | dynamic task DAG | all 23 task classes, a 23-node dependency chain from discovery to governance | **PASS** (no class rejected, no cycles, `longest_chain` = 23) |
| VV-13 | model routing | lower a task-class tier floor from the overlay; raise one; check the effective route | **PASS** (lowering refused and ineffective; raising applied and effective T1 → T3) |
| VV-14 | kernel integrity at use time | tamper kernel `SECURITY_POLICY.never_index_classes`; re-index | **FAIL** — with an intact kernel the restricted file is excluded (`sensitivity:restricted`); after tampering the exclusion is gone and `rebuild-memory` proceeds. D003 CRITICAL and audit "kernel payload modified in place (INV-007)" detect it, but nothing consults them |
| VV-15 | dirty brownfield adoption | A0→A6 on the brownfield fixture; migrate before the independent review; executor supplying its own verdict; destructive batches; the deprecated `--gate-answer` flag | **PASS** (`VERDICT_REQUIRED`; `INDEPENDENCE` — "reviewer session must differ from the planner session"; `DELETE_FROM_ACTIVE_TREE` entries raise `HDG` gates that stay PENDING and nothing is deleted; `--gate-answer` authorises nothing; `pyproject.toml` and `web/package.json` preserved) |
| VV-16 | failure injection | CIT left EXECUTING; `state.db` overwritten with garbage; missing tool | **PASS** (D016 detects the interrupted transaction; `recover` freezes writes and classifies it UNKNOWN; a query on the corrupt store fails closed with `DB_ERROR`; rebuild restores it; `tools resolve` reports the capability gap) |

## 7. Version / provenance matrix

| Item | Observed | Verdict |
|---|---|---|
| Branch / tag | `release/4.1.4-rc1`; `v4.1.4-rc1` points at HEAD; `v4.1.3-rc1` at `26ab5b6`; `main` untouched at `5118d40` | **sound** (M-N7 closed) |
| Candidate commit | `47d8394` = repair code `c6b594b` + `release/releases/4.1.4/` + both harness reruns + regenerated evidence | consistent |
| Framework version | `Cargo.toml` 4.1.4; `gov version` → version/cli/runtime 4.1.4, index `4.1.3-idx2` | consistent (the index version is deliberately unchanged: the index format did not change) |
| Kernel version | `framework/KERNEL.yaml` 4.1.4; released `KERNEL.yaml` byte-identical to it | consistent |
| Release payload | 4.1.4: `release verify` ok, 0 modified/missing/added; `release_hash` = kernel `payload_hash`; identical to `framework/`+`migrations/`+`tools/` at `c6b594b` and at HEAD; reproduces byte-for-byte from a clean rebuild; in-place rebuild refused | **sound** |
| Release manifest | yaml == json; `certification.status: READY_FOR_INDEPENDENT_REVERIFICATION`, verifier empty; `provenance.release_branch/release_tag/kernel_source/migration_substance_problems` populated | consistent; **must be set by the release owner** (§14) |
| 4.1.3 payload | untouched; `certification.status: REJECTED` with the verifier's verbatim text; `release verify` still ok | correct |
| 4.1.2 payload | untouched, REJECTED | correct |
| `CERTIFICATION_STATUS.md` | records 4.1.2 REJECTED, 4.1.3 REJECTED (verbatim), 4.1.4 READY_FOR_INDEPENDENT_REVERIFICATION with an explicit "the implementer has not issued OS_RELEASE_CANDIDATE_ACCEPTED and must not" | correct — no self-certification |
| Migration chain | `M-4.1.1-4.1.2` → `M-4.1.2-4.1.3` → `M-4.1.3-4.1.4`; `supported_from_versions` covers 4.1.1/4.1.2/4.1.3; exercised genuinely end-to-end (§5) | **sound** |

## 8. Answers to the mandatory questions

1. **Is the architecture substantially complete relative to the governing documents?** Yes, materially. Every pillar in
   §9 is PRESENT_AND_SUBSTANTIAL except the rows marked PARTIAL/ABSENT there, and no PARTIAL row is load-bearing for the
   release except the two security gaps in §11.
2. **Which pillars are PARTIAL / ABSENT / UNCLEAR?** PARTIAL: capability/plugin registry authority (V-H1), kernel-integrity
   enforcement (V-H2), exception governance (V-M1), AST/LSP code intelligence (regex baseline + plugins), vector store and
   graph store swappability (both fixed to SQLite by code), token-level observability, temporal memory (no per-record git
   lineage). ABSENT with a recorded decision: MCP transport (D-0004), a bundled paraphrase-capable embedder (D-0006),
   JSON-RPC/HTTP transports. Nothing is UNCLEAR.
3. **What is the deterministic core implemented in?** Rust — `runtime/` (library, ~26.8k lines across 71 source files)
   and `cli/` (the `gov` binary), with the kernel payload embedded at build time by `runtime/build.rs`. Dependencies:
   rusqlite (bundled SQLite + FTS5), serde/serde_json/serde_yaml, jsonschema, regex, walkdir, sha2, chrono, uuid, clap.
4. **Rust-first exceptions, and are they justified?** None in the deterministic core. The only non-Rust code is optional
   capability plugins (`capabilities/python/`, `capabilities/shell/`) behind API-0001, and the verifier harnesses.
   Justified by D-0002 §4 (replaceable specialised capabilities behind stable interfaces).
5. **Can the core operate without Python?** Yes. `ldd target/release/gov` → `libgcc_s`, `libm`, `libc`, `ld-linux` only.
   `arch::core_runs_without_any_governed_toolchain_on_path` and HV-25 both pass; VV-01…VV-16 ran without any plugin.
6. **Can the OS govern non-Rust and mixed-language projects without architectural change?** Yes. 11 ecosystems are
   detected (`capabilities/ecosystems.rs`: rust-cargo, python, node-npm, go, cmake, make, maven, gradle, dotnet,
   ruby-bundler, elixir-mix), `language_for_ext` covers 20+ extensions, the tool registry is language-tagged and
   resolved against the *governed project's* detected languages, and the brownfield fixture is a mixed Python + TypeScript
   repository whose native layouts (`pyproject.toml`, `web/package.json`) survive adoption (VV-15).
7. **Structured-state database and why?** SQLite via rusqlite (bundled), WAL, `PRAGMA integrity_check`, FTS5, at
   `.governance-runtime/state.db`; claims in a separate `claims.db` and control in `control.json` so they survive a
   rebuild. Chosen for zero external dependency, single-file portability and offline determinism (ARCH-0001,
   TOOL-SQLITE-001). Appropriate for a purely derived store.
8. **Lexical search and why?** SQLite FTS5 with BM25 ranking and the `porter unicode61` tokenizer, pinned in
   `MEMORY_POLICY.lexical.tokenizer` and part of the index pin (changing it forces a full rebuild). Chosen because it
   ships inside the same bundled engine — no second service, no second index format.
9. **Vector/index implementation and why?** A SQLite `vectors` table with brute-force cosine similarity; no ANN. Adequate
   and exactly reproducible at governed-repository scale; the cost is O(n) per semantic query. Not behind a trait —
   replacing it is a code change, not a configuration change (MEDIUM, unchanged from 4.1.3).
10. **Graph implementation and why?** A SQLite `edges` table with 20 typed edge kinds and BFS neighbour/impact traversal
    (`runtime/src/graph/mod.rs`), plus dangling-edge and orphan-node checks. Same rationale as (7); likewise not behind a
    trait (LOW).
11. **Code-intelligence mechanisms and why?** A built-in regex extractor covering ~13 language families (symbols,
    qualnames, kinds, line spans, parents, signatures, references, imports, calls) with `code_intel` plugins overriding
    it per language and degradations recorded in capability memory. Chosen so that the core has no language-server
    dependency; true AST/LSP fidelity requires a plugin (none bundled). PARTIAL, acceptable.
12. **Embedding model, and why?** Built-in `hashed-ngram` v1, 512 dimensions — a deterministic, dependency-free lexical
    approximation, explicitly *not* a neural model. Chosen (D-0006, option B) so the kernel stays buildable and operable
    offline with no model or vendor dependency, while every repository pins its own choice through the governed
    benchmark. Pinned in `MEMORY_POLICY.embedding` and in the index manifest; fail-closed on mismatch.
13. **Reranker, and why?** None by default (`MEMORY_POLICY.reranker.provider: none`); `rerank` plugins are wired between
    fusion and authority filtering and their scores govern the final order (NV-10). Same rationale as (12).
14. **What alternatives were benchmarked?** By the builder: baseline variants (`current`, `builtin:64`,
    `plugin:gov-builtin-embed:32`), recorded in `RES-0001` with full metric rows. By the first two verifiers:
    `builtin:128` and an independently authored synonym-aware plugin (NV-06). D-0006 names the candidate classes
    adopters are expected to evaluate (local sentence-embedding models via the shipped template; a local inference
    server behind a thin plugin; a remote API behind API-0001 subject to the outbound allowlist).
15. **What retrieval metrics support those choices?** `RES-0001` rows (recall@K, MRR, precision@K, stale and superseded
    hit rates, symbol recall, query latency, index cost, vector count per candidate); HV-08 on the adopted brownfield
    (recall@k 0.833, MRR 0.715, stale 0.0, superseded 0.0); NV-06 (baseline 0.9/0.75 → selected candidate 1.0/0.84,
    paraphrase recall 0.5 → 1.0); this session's machine-B `memory verify` (recall@k 1.0, MRR 1.0, precision 0.97,
    stale 0.0, superseded 0.0 over 17 measured queries).
16. **Generative/orchestrator routing mechanism?** `runtime/src/routing.rs`: a capability tier (T0–T3) and reasoning
    floor derived from task class, task fields, acting-role default, impact radius and overlay overrides, combined
    monotonically (a floor can only be raised), with candidates drawn solely from `MODEL_ROUTING_OVERRIDES.yaml` and the
    cheapest candidate meeting the tier chosen. The kernel contains no provider or model name. An evidence ledger records
    provider, model, task class, pass/fail, cost, latency and repair count, and `--report` aggregates them; budget
    thresholds raise Human Decision Gates. The core never contacts a model.
17. **Are model/tool choices pinned and replaceable?** Yes. Embedder and reranker: pinned in the overlay and the index
    manifest, replaceable through `benchmark`/`select`, fail-closed on every query path. Tools: registry descriptors with
    `version_pin`. Plugins: content-hash pinned (declared `sha256` or first-observed-per-version), with drift refused —
    **but the authority decision is not pinned (V-H1)**. Routing: overlay-driven and replaceable.
18. **Can all derived memory/index state be deleted and rebuilt?** Yes — verified four ways in VV-09: delete `state.db`,
    delete the entire `.governance-runtime`, rebuild on a clone, and rebuild after overwriting the database with
    garbage (VV-16). All produce the identical `manifest_hash`; claims and control state live outside the rebuilt store.
19. **Can a fresh independent agent reconstruct authoritative project context?** Yes — VV-11: a clone with a new session
    id produced the identical `next_action` and the identical context-packet `deterministic_hash`, with the authority
    layers, conflicting-decision flags and bounded truncation intact; `continue` explained exactly why no work was
    runnable. It fails closed on an embedder pin change (NV-12).
20. **Top critical architectural gaps preventing release?** (1) descriptor self-authorisation giving L0 roles arbitrary
    command execution (V-H1); (2) constitutional floors read from unverified installed-kernel files (V-H2);
    (3) self-attested exception decisions (V-M1). Nothing else blocks.

Additional questions carried forward from the 4.1.3 report:

21. **Are the previous CRITICAL/HIGH findings genuinely repaired?** C-N1 yes, at the root cause and robust under nine
    fresh attacks. H-N1 yes, for every override and exception route that the precedence file governs. H-N2 partially —
    the schema, pin, drift, health, elevated-permission and `capabilities invoke` paths are genuinely closed; the
    authority floor is not.
22. **New regressions or contradictions?** One contradiction inside the candidate: `TOOL_POLICY.plugins.min_authority`
    and API-0001 §governance both state a rule that `capabilities/governance.rs::authorize` does not enforce (V-H1). No
    behavioural regression was found against either previous harness.
23. **Do the original held-out tests pass unchanged?** Yes — 36/37 on the first harness (HV-08b residual) and 13/15 on
    the second (NV-09/NV-19, frozen inputs).
24. **Which tests were added?** VV-01…VV-16 (§6, §12).
25. **Is HV-08b a blocker?** No (§4.1); M-B1 is now closed by D-0006 and RES-0001.
26. **Is the 4.1.3 → 4.1.4 transition internally correct?** Yes — payload, manifests, version constants, migration
    substance, update/rollback mechanics, tags and branch are all coherent and were exercised with genuine 4.1.2 state.
27. **Is the branch/tag provenance correct now?** Yes.
28. **Is `M-4.1.3-4.1.4` valid, reversible and exercised?** Yes — schema-valid, performs and declares its overlay change,
    reversible byte-for-byte, exercised from genuine 4.1.2 state through 4.1.3 with two ledgered rollbacks.
29. **Is `framework.lock` correct across the chain?** Yes — version, hashes, schema versions, `release_commit`,
    `installed_at_commit` and a logical `source` on every 4.1.3+ path; restored byte-identically by rollback.
30. **Is commit `47d8394` suitable for Prompt 3 (release certification)?** **No** — not until V-H1 and V-H2 are repaired.

## 9. Architecture Completeness Matrix

Legend: **P&S** = PRESENT_AND_SUBSTANTIAL · PARTIAL · ABSENT · UNCLEAR. Rows unchanged from the 4.1.3 report and
re-confirmed here are marked "(re-confirmed)".

### A. Governance / deterministic control plane

| Requirement | Status | Implementation | Evidence | Verifier note | Sev |
|---|---|---|---|---|---|
| Deterministic Governance OS core | P&S | `runtime/`, `cli/` | clean build, 44+16 tests, VV-01…VV-16 | — | — |
| Rust-first control plane | P&S | 71 Rust source files, ~26.8k lines; `ldd` libc-only | `evidence/toolchain-and-binaries.txt` | — | — |
| Justified non-Rust exceptions | P&S | D-0002 §4, API-0001 | source | only optional plugins | — |
| Portable `gov` CLI | P&S | embedded kernel via `build.rs`; logical `source` label on every 4.1.3+ path | VV-07, §5 | — | — |
| Authority / policy engine | **PARTIAL** | `authority.rs`, `policy.rs`, ENFORCEMENT_MAP, `policy_coverage.rs` | VV-02 PASS; **VV-03c, VV-04 FAIL** | levels enforced and un-weakenable from the overlay, but the rule file is trusted unverified and a descriptor can self-authorise | **HIGH** |
| Canonical constitution / policy precedence | **PARTIAL** | `POLICY_PRECEDENCE.yaml` (82 rules, deny by default), `policy_precedence.rs`, D027 | VV-02 PASS; **VV-03c FAIL** | correct when the kernel file is authentic | **HIGH** |
| Kernel vs project-overlay separation | P&S | `kernel.rs`, overlay templates, migration reconciliation | §5 (overlay byte-identical through 4 transitions) | — | — |
| `framework.lock` release pinning | P&S | `lock.rs`, schema 1.1.0 with `installed_at_commit` | §5, NV-08 | — | — |
| Checkpoint / recovery | P&S | `checkpoints.rs`, `recovery.rs` | VV-16, HV-19 | — | — |
| CIT-P / CIT-E | P&S | `cit/mod.rs` incl. `authoritative_gate` | **VV-01 PASS (9 attacks)** | previously CRITICAL, now the strongest area | — |
| Dynamic task DAG / orchestration | P&S | `orchestration/dag.rs`, 23 task classes | VV-12 | — | — |
| Human Decision Gate handling | P&S | `gates.rs` incl. `revoke`, `answered_option`, `is_answered_yes` | VV-01, §5, VV-15 | previously CRITICAL, now sound on every path tested | — |
| Model-routing policy | P&S | `routing.rs`, MODEL_ROUTING_POLICY | VV-13 | floors monotonic | — |
| Reasoning-tier support | P&S | `routing.rs` reason ranks; role/task/radius floors | VV-13 | — | — |
| Tool / capability / permission registry | **PARTIAL** | `tools.rs`, `capabilities/governance.rs`, TOOL_PERMISSIONS | **VV-04 FAIL** | schema/pin/health/elevated paths correct; authority floor self-attested | **HIGH** |
| Release / install / update / rollback | P&S | `release.rs`, `update.rs`, `kernel.rs` | §5, VV-07 | ledger, snapshot consumption and downgrade refusal all correct | — |
| Immutable release manifest / hashes / provenance | P&S | `release/releases/4.1.4/` | VV-07 | — | — |
| Observability / execution evidence | PARTIAL | `observability.rs` (JSONL spans, retrieval log, rework, cost, routing report) | greenfield fixture | no token-level measurement (char proxy) | LOW |

### B. Repository intelligence and adoption / migration

All P&S and re-confirmed: cold deterministic inventory, material-artefact and authority classification, target path map,
repository contract, governed migration engine with dependency-ordered batches and byte-identical batch rollback,
**independent migration-test hooks with an enforced session-independence check** (`INDEPENDENCE`: "reviewer session must
differ from the planner session"), legacy retirement and pre-retirement extraction, `gov init`, `gov adopt` A0–A11 with
destructive-gate records, `gov update`, and preservation of healthy native layouts (VV-15). Dependency-aware batching is
still by protocol batch order rather than a computed dependency graph — PARTIAL, MEDIUM, unchanged.

### C. Development Knowledge Fabric / memory

| Requirement | Status | Notes | Sev |
|---|---|---|---|
| Git records as source of truth; SQLite as derived state; claims/control outside the rebuilt store | P&S | `memory/db.rs:1` declares the store "never authoritative"; VV-09 proves it four ways | — |
| Lexical FTS5/BM25 (`porter unicode61`, pinned) | P&S | part of the index pin | — |
| Semantic / vector retrieval | P&S (mechanism) | brute-force cosine over a SQLite table; no ANN | MEDIUM (scale only) |
| Graph relationships / dependency memory | P&S | 20 edge types, BFS neighbours and impact set, dangling/orphan checks | — |
| Temporal / supersession awareness | PARTIAL | `superseded_by`, status filters, conflicting-decision flagging; no per-record git lineage | MEDIUM (unchanged) |
| Episodic / execution evidence | P&S | telemetry JSONL, reports, checkpoints, routing evidence, capability memory | — |
| Code intelligence; AST/LSP/symbol/reference/import/call | PARTIAL | regex extractor for ~13 language families + `code_intel` plugins; no LSP/SCIP | MEDIUM (unchanged) |
| Retrieval router (exact / path / symbol / lexical / semantic / graph) | P&S | `retrieval/mod.rs::classify` + six route implementations | — |
| Candidate fusion | P&S | reciprocal-rank fusion, `rrf_k` 60 | — |
| Hierarchical / parent-child retrieval | P&S | document→section→child chunking, parent expansion of the top 3 | — |
| Graph-neighbour expansion | P&S | `graph_neighbour_depth` | — |
| Reranking | P&S | plugin hook between fusion and authority filtering; scores govern order (NV-10) | — |
| Authority filtering; provenance; stale/superseded filtering | P&S | status excludes, namespace × role filtering, `content_hash`/`repo_commit` per artefact | — |
| Context compiler; bounded authoritative context | P&S | eight ordered authority layers, deterministic hash, `max_packet_chars` with tail truncation | — |
| Rebuildability; deletion-and-rebuild tests | P&S | VV-09, VV-16, `repair.rs:619` | — |
| Retrieval regression / golden queries; Recall@K; MRR; precision; stale-hit | P&S | `heldout.rs` 8 categories, `run_heldout_with`, `regression.min_queries` guard against unmeasured greens | — |
| Latency / context-size / token metrics | PARTIAL | latency and characters measured; tokens not | LOW |

### D. Memory component separation

Embedding model, embedding runtime, lexical engine, code intelligence, reranker and the generative LLM are each
separately pinned and replaceable (`EmbedSpec`/`Embedder`, plugin host, `MEMORY_POLICY.lexical`, `code_intel` plugins,
`RerankSpec`/`Reranker`, `MODEL_ROUTING_OVERRIDES`), with fail-closed pins on every query path. The retrieval router and
context compiler are single implementations parameterised by policy. The **vector store and graph store are fixed to
SQLite in code** — no trait, no configuration point. No provider, model or runtime is a constitutional dependency.
**P&S with two acceptable, documented couplings** (MEDIUM / LOW, unchanged).

### E. Rust-first core / polyglot project independence

P&S across the board: no Python or Node needed to operate the core; specialised capabilities behind `gov-capability/1`;
governed-project language detected, never assumed; language-tagged tool registry resolved against the governed project;
Rust, Python, TypeScript and Go governed fixtures; mixed repositories supported. `rust-analyzer` remains registered as
`proposed` (MEDIUM, unchanged).

### F. Agent organisation / orchestration

| Requirement | Status | Notes | Sev |
|---|---|---|---|
| Role separation; authority levels | **PARTIAL** | 27 kernel roles L0–L5, enforced on every mutating path and not overlay-weakenable — but V-H1 lets an L0 role execute arbitrary commands, and the acting role remains caller-declared (L-N4) | **HIGH** |
| Task contracts; typed results; handoffs | P&S | bounded `allowed_paths`/`prohibited_paths`, schema-validated worker returns | — |
| Mutation manifests | P&S | observed vs declared, baseline snapshot at claim | — (M-N4 closed) |
| Worktree / task-claim collision controls | P&S | `claims.db` outside the rebuilt store | — |
| Checkpointing before handoff / close / model switch | P&S | `CHECKPOINT_POLICY.mandatory_triggers`, watchdog | — |
| Fresh-session independence for verification roles | P&S | enforced for migration review (`INDEPENDENCE`) | — |
| Continue independent DAG branches while gates pend | P&S | `blocks_tasks` scoping; `continue` reports blocked branches separately | — |
| Durable promotion of agent results | P&S | HV-32 | — |

### G. Tools / interfaces / extensibility

| Requirement | Status | Notes | Sev |
|---|---|---|---|
| Stable interfaces (API-0001 v1.1, API-0002) | P&S | API-0001 now matches the fail-closed implementation and states the governance contract | — (M-N6 closed) |
| MCP | ABSENT with a decision (D-0004); `MCP_NOT_IMPLEMENTED` returned explicitly; registry entry `planned` | acceptable | — |
| A2A separation from memory and tool execution | P&S | `handoffs.rs` | — |
| CLI / structured-stdio governed interfaces | P&S | API-0002 JSON envelope with typed codes; plugin stdin/stdout | JSON-RPC and HTTP absent by design | LOW |
| Capability discovery; tool registration; health checks; acquisition gate; version pinning | P&S | `tools.rs`, `capabilities/host.rs`, `governance.rs` | — |
| Secrets handling | P&S | `security/secrets.rs`, path + content patterns, redaction, index-side and write-side blocks | — |
| Privilege / destructive-action gates | **PARTIAL** | destructive migration, tool install, elevated plugin permissions and budget thresholds all gate correctly; **plugin execution authority does not** | **HIGH** |
| Loose coupling to external services | P&S | subprocess plugin host; the core never links a model or calls one | — |

### H. Model routing / reasoning policy — P&S (re-confirmed; VV-13)

Capability-tier selection with no provider name in the kernel; per-task minimum tier and reasoning; floors combine
monotonically so a critical task can never be downgraded; deterministic no-LLM paths throughout; routing evidence
records provider/model/task class/pass/cost/latency/repairs; policy replaceable through the overlay.

### I. Synthetic certification fixtures

Greenfield, dirty brownfield (legacy provider rules `.cursorrules`/`copilot-instructions.md`/`AGENT_RULES_v2.md`, stale
`.index/`, duplicate and superseded decisions, code/spec disagreement, misplaced `docs/*.py`, missing tests, broken
links, `.env` and `config/secrets.yaml`), migration, framework update, upstream learning, multi-machine, failure
injection, secrets/outbound negative controls: **P&S**. The real 4.1.2 → 4.1.3 → 4.1.4 path is now in the builder suite
(`repair2::genuine_412_…`), closing M-N8. Adapter conformance remains PARTIAL (verbatim invariants + hashes, unchanged).

### J. Security / safety / outbound

| Requirement | Status | Notes | Sev |
|---|---|---|---|
| Secret detection/exclusion | P&S | VV-10, VV-15, HV-21 | — |
| Sensitive-path handling | **PARTIAL** | correct with an authentic kernel (VV-02); nullified by kernel tampering (VV-14) | **HIGH** |
| Outbound allowlist / default deny; upstream sanitisation; synthetic reproducer preference | P&S | VV-10 (`UPSTREAM_SCOPE`, fail-closed export gate, identifier stripping) | — |
| Project/customer data separation | P&S | namespaces × role groups; NV-17 | — |
| Destructive-action controls; privilege boundaries | **PARTIAL** | V-H1 | **HIGH** |
| Auditable security decisions | P&S | D027 CRITICAL on refusals, audit INV-007 on kernel drift, plugin findings surface in `plugins list` | — (but D028 is silent about the V-H1 class) |

### K. Learning / upstream — P&S (re-confirmed)

PROJECT/PRODUCT/FRAMEWORK scoping enforced (`UPSTREAM_SCOPE`), local capture, sanitised candidates, a fail-closed
Upstream Export Gate, no whole-project export, clustering into Framework Change Proposals (`gov lessons cluster` +
schema), a central release path with tags, and a downstream `gov update` mechanism.

### L. Observability / governance health — P&S except token usage (LOW, unchanged)

Task traceability (trace/span JSONL), readiness, contradictions, graph orphans, retrieval quality, stale/superseded
rates, context size, latency, cost, handoff violations, retries/repairs, tests, decisions, human interventions and
rebuild/fresh-agent reconstruction are all measurable. Token counts are proxied by cost and characters.

## 10. Model / Retrieval Selection Matrix

| Component | Selected | Version | Alternatives considered | Benchmark / evidence | Rationale recorded | Pinned | Replaceable | Privacy / locality | Verdict |
|---|---|---|---|---|---|---|---|---|---|
| Generative / orchestrator model | none in the kernel; tier floors T0–T3 | n/a | overlay decides per project | routing evidence ledger + `route --report` + budget gates | MODEL_ROUTING_POLICY, ROLES.yaml | overlay | yes | provider-agnostic; the core never calls a model | **ACCEPT** |
| Specialist / worker tiers | T1/T2 by task class and role | n/a | n/a | same | same | overlay | yes | same | **ACCEPT** |
| Embedding model | builtin `hashed-ngram`, 512-d | 1 | builder: `current`, `builtin:64`, `plugin:gov-builtin-embed:32` (RES-0001); verifiers: `builtin:128`, synonym-aware plugin (NV-06) | RES-0001 rows + NV-06 (paraphrase recall 0.5 → 1.0) | **D-0006** (why nothing is bundled; candidate classes for adopters) | overlay + index manifest | **yes, verified** | fully local, offline, deterministic | **ACCEPT** — M-B1 closed |
| Embedding inference runtime | in-process builtin, or any language subprocess | `gov-capability/1` v1.1 | — | host unit tests (1.2 MB response, 600 KB request, timeout kill, bad protocol); NV-06/17; HV-36 | API-0001 | plugin version + content hash | yes | local by default | **ACCEPT** |
| Vector store / index engine | SQLite `vectors`, brute-force cosine | index `4.1.3-idx2` | none recorded | — | ARCH-0001 | `index_version` | code change only | local | **ACCEPT with note** (no ANN, no trait) |
| Lexical engine | FTS5 BM25, `porter unicode61` | bundled SQLite | `unicode61` (superseded) | V-SEM-2 morphological query now passes | MEMORY_POLICY.lexical | yes (part of the index pin) | code change | local | **ACCEPT** |
| Graph implementation | SQLite `edges` + BFS, 20 edge types | — | none recorded | dangling/orphan checks; HV-23 | ARCH-0001 | n/a | code change | local | **ACCEPT** |
| Reranker | none by default; `rerank` plugins | 0 | — | NV-10 (scores govern order; `RERANKER_MISMATCH` before rebuild) | MEMORY_POLICY.reranker, D-0006 | yes | yes | local or plugin-defined | **ACCEPT** |
| Code-intelligence tooling | builtin regex extractor + `code_intel` plugins; rust-analyzer `proposed` | 1.0.0 | LSP/SCIP not evaluated | HV-13/23/33, VV-12 | ARCH-0001, RPT-0001 | plugin version + hash | yes | local | **PARTIAL** (acceptable baseline) |
| Query planning / rewrite model | none (deterministic T0 intent patterns) | — | — | HV-18 | COMMAND_CONTRACT | — | adapters may add | — | **ACCEPT** |

Selection-quality assessment (directive §3): the benchmark evaluates realistic Governance OS retrieval tasks — exact
decision retrieval, exact path, symbol and symbol-reference, lexical literal, graph impact, superseded-vs-current
authority, semantic paraphrase and historical evidence — with Recall@K, MRR, precision@K, stale and superseded hit
rates, symbol recall, latency, index cost and vector count. It re-indexes each candidate into an isolated database, so
comparisons are like-for-like, and `--record`/`select` bind the outcome to a research record and a decision listing the
alternatives. Multiple credible candidates were compared by three independent parties. **This satisfies §2 and §3; no
model family is required and none is demanded here.**

## 11. Critical Gap Register

### CRITICAL
None.

### HIGH

| ID | Gap | Evidence | Affected architecture | Risk | Required repair | Acceptance test |
|---|---|---|---|---|---|---|
| **V-H1** | A plugin descriptor authorises itself. `capabilities/governance.rs::authorize` computes `role_ok` as *(a)* `approved_roles` contains the acting role or `"all"`, else *(b)* `provenance.registered_at` is a non-empty string, else *(c)* `level >= TOOL_POLICY.plugins.min_authority`. (a) and (b) are attacker-controlled fields **in the descriptor being authorised**, and the schema permits both on a hand-written file. An L0 `independent-auditor` therefore executes an arbitrary command during `gov rebuild-memory` (an L0 operation) via the `code_intel` path. `doctor` D028 reports "no plugin problems" because the descriptor is *usable*, not denied | VV-04 items 3, 4 and 3_D028: marker file written by `plugins list` + `rebuild-memory` as `independent-auditor`; reproduced for both fields independently. Contradicts the kernel's own `TOOL_POLICY.plugins.min_authority` comment and API-0001 §governance ("a descriptor is not an authorisation") | framework §28–32 capability governance; TOOL_PERMISSIONS least authority; J privilege boundaries; F role separation; the protocol's independent-verification model (all four independence roles are L0) | any actor able to write one tracked YAML file under `governance/project/plugins/` obtains arbitrary command execution at the next rebuild, under an identity the governance model treats as read-only | (1) `approved_roles` may only **narrow**, never widen: require `level >= min_authority` **and** membership of `approved_roles` when that list is present. (2) Treat `provenance` as untrusted descriptor content: registration must be proven by an OS-side record the descriptor cannot fabricate — e.g. a `governance/generated/plugin-registry.json` entry written by `plugins register`, keyed by `plugin_id` + `version` + observed content hash, and required before `registered` is believed. (3) Require a declared `pin.sha256` on any descriptor claiming registration. (4) Make D028 report every descriptor that is usable below `min_authority` without an OS-side registration record, at HIGH. (5) Add a suite family finding in `plugin_governance` | `harness_v3.py VV-04` → PASS (items 3, 4, 8 and `3_D028` all clean) |
| **V-H2** | Constitutional floors are read from unverified installed-kernel files. `policy_precedence::load` reads `governance/kernel/policies/POLICY_PRECEDENCE.yaml` and trusts whatever is there; `PolicySet::load` reads the kernel policies the same way. Tampering with the precedence file re-enables every weakening override and lets an L0 role create tasks; tampering with `SECURITY_POLICY.never_index_classes` removes a restricted-class exclusion at index time. The condition **is** detected (D003 CRITICAL, `gov kernel verify` `ok: false`, audit "kernel payload modified in place (INV-007)") but no enforcement path consults it — and `load()` already fails closed when the file is **absent**, so the fail-closed posture exists and simply is not applied to the present-but-modified case | VV-03 (c): `c_applied_after_kernel_tamper` lists three weakening overrides applied, `c_L0_create_task.ok == true`, `c_kernel_integrity_checks` D003 `ok: false` severity critical. VV-14: `exclusions_with_intact_kernel = [{customer/secretdoc.md, sensitivity:restricted}]` → `excluded: []` after tampering, rebuild proceeds | A authority/policy engine and policy precedence; J sensitive-path handling; INV-006, INV-007 | an agent or process with write access to the installed kernel silently removes the authority floor and the never-index floor; every H-N1 guarantee is conditional on a file nobody verifies at load time | Verify the installed kernel against `framework.lock.kernel_manifest_hash` / `KERNEL_MANIFEST.json` **inside `PolicySet::load`** (cache the result per process). On mismatch: use the embedded kernel payload for the precedence rules and the security/authority policies exactly as the absent-file path already does, record the substitution in `problems` and in the context packet, and refuse mutating operations with a typed `KERNEL_TAMPERED` error until `gov kernel reinstall` or an explicit override by an L4+ role with a gate | `harness_v3.py VV-03` → PASS (`c_L0_create_task.ok == false`, weakening not applied) and `VV-14` → PASS (exclusion preserved or the operation refused) |

### MEDIUM

| ID | Gap | Evidence | Required repair | Acceptance |
|---|---|---|---|---|
| **V-M1** | `PROJECT_EXCEPTIONS` entries are accepted on a self-attested decision reference. `policy.rs` only tests `decision` for non-emptiness, so `decision: D-DOES-NOT-EXIST` is applied. Reachable only for `exception_relaxable` keys, but that set includes `BUDGET_POLICY.defaults.*`, `CHECKPOINT_POLICY.watchdog.*` and the `MEMORY_POLICY.regression.*` quality floors (`min_recall_at_k`, `min_mrr`, `max_stale_hit_rate`, `max_superseded_hit_rate`) | VV-03 (a): `exception_with_fabricated_decision_applied: true`; no doctor or audit finding names the dangling reference | Resolve the referenced record: it must exist, be of type `decision`, be `ACTIVE`, and reference this exception or policy key. Otherwise refuse the exception and record it in `refused_overrides`. Add a doctor finding for dangling exception references | `harness_v3.py VV-03` → PASS (`exception_with_fabricated_decision_applied: false`) |
| **V-M2** | Vector and graph stores are fixed to SQLite in code with no trait or configuration point; brute-force cosine is O(n) per semantic query | §9 D; `retrieval/mod.rs` semantic route | Unchanged from the 4.1.3 report: acceptable at governed-repository scale. Before a scale-sensitive release, introduce a narrow trait for the vector store or record a decision bounding the supported corpus size | decision record or trait + benchmark |
| **V-M3** | Temporal memory has no per-record git lineage; code intelligence is regex-based with no bundled LSP/AST plugin; dependency-aware migration batching is by protocol batch order | §9 C, B | Unchanged from the 4.1.3 report | — |

### LOW

| ID | Gap | Evidence | Repair |
|---|---|---|---|
| V-L1 | A schema-invalid `DATA_SENSITIVITY.classifications` entry does not classify and does not block indexing; the file is indexed at the default class while D006 reports the schema error at HIGH | VV-02 (`malformed_rule_content_retrievable: true`, `D006` HIGH) | Fail closed on an invalid sensitivity rule: refuse to index paths the malformed rule was meant to cover, or refuse the rebuild |
| V-L2 | `update` refusals return `ok: true` with `applied: false` (decline, up-to-date, downgrade), so a caller checking only the envelope `ok` cannot distinguish success from refusal | §5 | Return a typed error envelope for a declined gate, or document the contract explicitly in API-0002 |
| V-L3 | The rollback ledger's `snapshot` field is an absolute host path; the snapshot directory survives after `snapshot_consumed: true` | §5 | Record a repository-relative path; state that "consumed" means invalidated, not deleted |
| V-L4 | `framework.lock.source` written by the 4.1.2-era `init` is an absolute host path; it is faithfully restored by a rollback to 4.1.2 | §5 | None required (historical value); optionally normalise on the next update |
| V-L5 | The acting role is caller-declared (`--role human`); documented in `docs/ARCHITECTURE.md` §4.8 as the adapter's authentication boundary | L-N4, VV-01 | Unchanged: acceptable as a documented boundary. Optionally bind human answers to a channel token |
| V-L6 | `.gitignore`d paths are invisible to the observed-mutation check (`git ls-files -co --exclude-standard`) | VV-08 | Document as a boundary in the task-close contract, or hash-compare ignored paths under `allowed_paths` |
| V-L7 | Token-level usage is not measured (cost and characters are proxies) | §9 A, L | Optional |

## 12. Independent test additions (this session)

Sixteen scenarios, authored before reading the builder's certification tests and unknown to both previous verifiers:

VV-01 CIT gate integrity under nine attacks · VV-02 fifteen simultaneous constitutional-floor weakening attempts ·
VV-03 exception governance and kernel-precedence tampering/absence · VV-04 thirteen plugin-descriptor attacks ·
VV-05 strict-YAML hygiene across all 192 kernel YAML files and manifest agreement · VV-06 migration substance for 4.1.4
and immutability of released migration operations · VV-07 4.1.4 release identity, reproduction and immutability ·
VV-08 observed-vs-declared mutation scope with an evasion attempt · VV-09 four-way derived-state deletion and rebuild
including a second machine · VV-10 upstream export scope, sanitisation, secrets and authority · VV-11 fresh-agent
reconstruction on a clone with a new session · VV-12 DAG expressiveness over all 23 task classes ·
VV-13 model-routing floor monotonicity · VV-14 kernel-integrity enforcement at use time · VV-15 dirty-brownfield
adoption gating and native-layout preservation · VV-16 failure injection and recovery.

Plus, outside the harness: a full independent execution of the 4.1.2 → 4.1.3 → 4.1.4 upgrade and the two-step rollback
chain with a genuine 4.1.2-binary-created consumer (§5), and a targeted re-test that **refuted** a reported
`update --apply --approve --role human` gate bypass.

**Test-author / executor separation.** Scenario authorship, execution and result review were separated across contexts:
the upgrade/rollback chain (§5) and the architecture-completeness survey (§9) were each executed by a separate agent
context that did not author the other's tests, and every material claim they returned was re-executed or re-read by this
verifier before being recorded — which is how the reported gate bypass was caught and refuted. The `harness_v3.py`
scenarios were authored and executed here and reviewed against a second full run with identical verdicts.

## 13. Builder repair delta (ordered)

1. **V-H1 — plugin authority must not be self-attested.** `approved_roles` narrows, never widens; `provenance` in a
   descriptor is untrusted; registration is proven by an OS-written registry record keyed by `plugin_id` + `version` +
   observed content hash; a descriptor claiming registration must carry a matching `pin.sha256`; D028 reports any
   descriptor usable below `min_authority` without an OS-side record at HIGH; add a `plugin_governance` suite finding.
   Acceptance: `harness_v3.py VV-04` → PASS.
2. **V-H2 — verify the installed kernel before trusting its floors.** Check the kernel manifest hash inside
   `PolicySet::load`; on mismatch fall back to the embedded payload (as the absent-file path already does), record the
   substitution, and refuse mutating operations with `KERNEL_TAMPERED` until reinstall or an L4+ gated override.
   Acceptance: `harness_v3.py VV-03` and `VV-14` → PASS.
3. **V-M1 — resolve exception decisions.** The referenced record must exist, be a `decision`, and be `ACTIVE`; otherwise
   refuse and record in `refused_overrides`; add a doctor finding for dangling references.
   Acceptance: `harness_v3.py VV-03` → PASS.
4. **V-L1** fail closed on a schema-invalid sensitivity classification. **V-L2** typed refusal envelope (or an explicit
   API-0002 contract note). **V-L3** repository-relative snapshot path and clearer "consumed" wording. **V-L6** document
   the gitignore boundary in the task-close contract.
5. **Evidence hygiene:** record NV-09 and NV-19 as frozen-input failures with a pointer to VV-05/VV-06, so the totals
   are not read as open defects.
6. Because the fix set touches kernel data (`TOOL_POLICY.plugins`, the plugin-descriptor schema, ENFORCEMENT_MAP and the
   generated plugin registry), the repaired candidate must be a **new immutable PATCH release 4.1.5** with migration
   `M-4.1.4-4.1.5`, on branch `release/4.1.5-rc1` tagged `v4.1.5-rc1`; 4.1.4 stays immutable and REJECTED. Re-run the
   builder suite, **all three** held-out harnesses unchanged (`release/verification/4.1.2/heldout/harness.py`,
   `release/verification/4.1.3/heldout-new/harness_v2.py` — which needs a 4.1.2 binary at `GOV412_WORKTREE` — and
   `release/verification/4.1.4/heldout-v3/harness_v3.py`), clippy and rustfmt; regenerate evidence; leave certification
   pending.

## 14. Certification block for the release owner

This session did not edit `release/releases/4.1.4/manifest.{yaml,json}` or `release/CERTIFICATION_STATUS.md`, following
the convention established at 4.1.3. `VERDICT.md` contains the exact block to transcribe verbatim (the kernel payload
and `file_hashes` must stay untouched; `gov release verify release/releases/4.1.4` remains ok because only `kernel/` is
hashed).

## 15. Verified sound — do not regress

Rust-only deterministic core with an embedded kernel and no Python/Node dependency; CIT gate integrity under nine
independent attacks; constitutional precedence refusing fifteen simultaneous weakening overrides while leaving the
effective policy unchanged; the plugin schema, content pin, drift detection, health check, elevated-permission gate,
registration authority and `capabilities invoke` authority; observed-versus-declared mutation scope; four-way derived
state deletion and deterministic rebuild including a second machine; the complete 4.1.2 → 4.1.3 → 4.1.4 upgrade with
byte-identical overlay and `spec/` preservation, per-transition gates, ledgered rollbacks, snapshot consumption and
downgrade refusal; release identity, reproduction and immutability; fresh-agent reconstruction with an identical
deterministic context hash across machines; upstream export scope, sanitisation and fail-closed gate; brownfield
adoption with an enforced reviewer-session independence check and destructive-deletion gates; failure injection and
recovery; model-routing floor monotonicity; DAG expressiveness across all 23 task classes; the benchmark-and-selection
mechanism with recorded evidence (RES-0001) and a recorded model-policy decision (D-0006).

## 16. Verdict

**OS_RELEASE_CANDIDATE_REJECTED** for commit `47d8394b945bcfd9f35a5fee80836e424a4570dc` (repair candidate 4.1.4).

Rejection triggers met (directive §10): independently authored held-out tests expose unresolved HIGH defects (V-H1,
V-H2), and security/privilege boundaries are materially incomplete in consequence. No critical architectural pillar is
absent; memory is a genuine multi-layer fabric, not a vector index; authoritative truth does not depend on derived
indexes; component choices are recorded, pinned and replaceable; a credible benchmark/selection mechanism exists with
evidence; derived indexes rebuild deterministically; the OS is not tied to one governed-project language; and the
deterministic core does not contradict the Rust-first architecture. The three previous CRITICAL/HIGH findings are
genuinely repaired, both previous harnesses pass unchanged apart from two frozen-input scenarios and one accepted
non-blocker, and the repair delta in §13 is bounded — the candidate is close, and 4.1.5 should be a small iteration.
