# Repair report — agentic-engineering-os 4.1.5 (third repair iteration, after the rejection of 4.1.4)

Written for: the independent verifier re-verifying the candidate, and the product owner.

| | |
|---|---|
| Rejected candidate | 4.1.4 at commit `47d8394b945bcfd9f35a5fee80836e424a4570dc` (tag `v4.1.4-rc1`) — verdict OS_RELEASE_CANDIDATE_REJECTED (`release/verification/4.1.4/INDEPENDENT_REVERIFICATION_REPORT.md`, `VERDICT.md`) |
| Repair branch | `release/4.1.5-rc1` (branched from the verifier's commit `f4b3429`; nothing rewritten, nothing merged to `main`) |
| Repair code commit | `25dac6e` |
| Candidate commit | the commit tagged **`v4.1.5-rc1`** on `release/4.1.5-rc1` (`git rev-parse v4.1.5-rc1^{commit}`; exact hash also given in the handoff message). It carries the payload `release/releases/4.1.5/` built at `2e53657`, the clean-clone harness reruns, the regenerated evidence and this report. |
| Release version | 4.1.5 — kernel payload changed (TOOL_POLICY.plugins registry, authority classes, precedence rules, four schemas) → new immutable PATCH release; 4.1.4 untouched and REJECTED |
| Migration chain | `M-4.1.1-4.1.2` → `M-4.1.2-4.1.3` → `M-4.1.3-4.1.4` → `M-4.1.4-4.1.5`; `supported_from_versions` 4.1.1 / 4.1.2 / 4.1.3 / 4.1.4; exercised from a consumer created by the genuine 4.1.2 binary through to 4.1.5 with ledgered rollbacks |
| Certification | **pending** — READY_FOR_INDEPENDENT_REVERIFICATION; the implementer has not certified anything |

No verifier artefact was modified: `release/verification/4.1.2/**`, `4.1.3/**` and `4.1.4/**` (reports, verdicts, all
three harnesses, results, evidence) are byte-identical to the verifier commits, and all three harnesses were rerun
unchanged. No verifier-authored test was weakened, rewritten, bypassed or special-cased. The only released-artefact
edit is the 4.1.4 manifest certification block, transcribed verbatim from that verifier's `VERDICT.md` at their
explicit request; the kernel payload and `file_hashes` are untouched and `gov release verify release/releases/4.1.4`
remains ok.

## 1. Totals

| Suite | Result |
|---|---|
| `cargo build --release` (clean clone of the tag) | PASS (exit 0; reproduced from a fresh clone of the tag — see the handoff message) |
| Rust unit tests (gov-runtime) | PASS — 19 passed, 0 failed |
| Certification suite (7 fixtures + architecture + regressions for the 4.1.2, 4.1.3 and 4.1.4 findings) | PASS — 49 passed, 0 failed (7 fixtures, architecture, 17 + 9 + 5 repair regressions) |
| Python plugin tests | PASS — 4 passed |
| First verifier harness, unchanged (`release/verification/4.1.2/heldout/harness.py`) | 36 PASS / 1 FAIL (HV-08b) / 1 INFO (HV-08) / 0 ERROR — verifier run 12 / 25 / 1 / 0 |
| Second verifier harness, unchanged (`release/verification/4.1.3/heldout-new/harness_v2.py`) | 13 PASS / 2 FAIL (NV-09, NV-19 — both frozen to the immutable 4.1.3 payload) / 0 ERROR — verifier run 6 / 9 / 0 / 0. In the working tree during development NV-16 also reports FAIL while the new payload directory is untracked; from the committed tag it passes. |
| Third verifier harness, unchanged (`release/verification/4.1.4/heldout-v3/harness_v3.py`) | 14 PASS / 2 FAIL (VV-05, VV-07 pinned to the 4.1.4 candidate identity, §5) / 0 ERROR — verifier run 13 / 3 / 0 / 0. **VV-03, VV-04 and VV-14 — the three findings — all PASS.** |
| rustfmt (`cargo fmt --all -- --check`) | PASS — `cargo fmt --all -- --check` clean |
| Clippy (`cargo clippy --workspace --all-targets`) | PASS — exit 0, 0 warnings, 0 errors |
| `gov release verify release/releases/4.1.5` | ok — 4.1.5 payload verified, release_hash matches the kernel, certification READY_FOR_INDEPENDENT_REVERIFICATION |
| Working tree at the candidate commit | clean at the candidate commit (`git status --porcelain` empty) |

Evidence: `docs/EVIDENCE.md`, `release/evidence/`, and the three rerun directories
`release/verification/4.1.2/heldout-rerun-4.1.5/`, `release/verification/4.1.3/heldout-new-rerun-4.1.5/`,
`release/verification/4.1.4/heldout-v3-rerun-4.1.5/`.

## 2. Preserved repairs

Confirmed by the third verifier and not regressed: CIT/Human-Decision-Gate integrity (C-N1), constitutional policy
precedence (H-N1), sensitivity controls (H5), replaceable embedding/reranking (C1/H7), benchmark and selection
(H7/M-B1), plugin-host large-output safety (C2), L0–L5 authority enforcement (H3), observed mutation scope (H4/M-N4),
persistent claims (H2), destructive-migration gates (H6), the 4.1.2 → 4.1.3 → 4.1.4 chain and rollback ledger
(M-N3/L-N2), `framework.lock` provenance (M-N1/M-N2), relocation-aware indexing (M-N5), Rust-first deterministic core,
polyglot capability architecture and model/provider independence. Their builder tests (`repair.rs`, `repair2.rs`) and
the first two harnesses continue to pass; §3 notes where a repair was *strengthened*.

## 3. Findings — root cause, invariant, trust sources, change, tests, residual risk

### V-H1 (HIGH) — a plugin descriptor authorised itself

| | |
|---|---|
| Root cause | `capabilities::governance::authorize` computed `role_ok` as *(a)* `approved_roles` contains the acting role or `"all"`, else *(b)* `provenance.registered_at` is non-empty, else *(c)* `level >= TOOL_POLICY.plugins.min_authority`. (a) and (b) are fields **inside the descriptor being authorised**, so a three-line YAML file granted itself the authority it was being checked against. An L0 `independent-auditor` obtained arbitrary command execution during `gov rebuild-memory`, and D028 stayed green because the descriptor was *usable*, not denied. |
| Violated invariant | Framework §28–32 capability governance and TOOL_PERMISSIONS least authority; API-0001 §governance ("a descriptor is not an authorisation"); the protocol's independence model (all four independence roles are L0). |
| Trust source before | The descriptor file itself (`approved_roles`, `provenance`) — project-controlled configuration, class T4 in D-0007. |
| Trust source after | The authority floor and permission classes come from **verified kernel policy** (T1, via `kernel_trust`); registration, authoritative `approved_roles`, required permission classes and the approving gate come from the **OS-written plugin registry** `governance/generated/plugin-registry.json` (T2), written only by `gov plugins register` after its authority, health, permission and gate checks. The descriptor supplies only the command, capability and a declared pin — and the pin is checked against observed bytes. |
| Implementation change | New `runtime/src/capabilities/registry.rs` (registry read/write, `Standing::{Unregistered,Registered,Mismatched}`, descriptor-content binding, orphan detection). `governance.rs::authorize` rewritten: the floor applies to **every** execution, registered or not; `approved_roles` may only narrow (registry-authoritative when registered); permission classes are the union of registry and descriptor (a descriptor may only add needs); the elevated-permission gate is read from the registry only; the registered implementation hash is checked alongside the declared pin and observed drift. `register` writes the registry record (descriptor sha256, implementation sha256, files, approved roles, permission classes, permissions, gate, session, role, time) and `unregister` removes it. `self_authorising_claims` records ignored claims in the grant and in every denial. `findings`/D028 report a descriptor that declares its own authorisation **whatever the acting role**, a registry mismatch, and stale registrations. Kernel data: `TOOL_POLICY.plugins.registry_path`/`registration_binds` and a corrected `min_authority` comment, `plugin-descriptor` schema 1.2.0 (approved_roles/provenance documented as advisory), new `plugin-registry` schema, POLICY_PRECEDENCE rules, ENFORCEMENT_MAP entries. CLI: `gov plugins register|unregister|registry|list|health`. |
| Files / components | `runtime/src/capabilities/{registry.rs,governance.rs,mod.rs}`, `runtime/src/doctor.rs`, `runtime/src/tools.rs`, `cli/src/main.rs`, `framework/policies/{TOOL_POLICY,POLICY_PRECEDENCE,ENFORCEMENT_MAP}.yaml`, `framework/schemas/{plugin-descriptor,plugin-registry}.schema.json`. |
| Builder regression test | `repair3::plugin_descriptors_can_never_authorise_themselves` |
| Original verifier test after repair | **VV-04 → PASS** (all thirteen items, including `3_D028`) |
| Adjacent attack tests | self-declared `approved_roles: ["all"]`; forged `provenance.registered_at`; both plus `status: active` and a self-declared `pin`; identity spoofing (a different descriptor reusing a registered id); descriptor edited after registration; version drift against the registration; orphan registration; elevated permissions unregistered, registered without a gate, and registered with an answered gate; registration attempted by an unauthorised role; execution attempted by L0, L1 and L4; actual command execution observed via a marker file during `rebuild-memory` and `capabilities invoke`; a hand-written registry entry (in `repair3::lower_trust_inputs_cannot_manufacture_higher_trust_facts`). |
| Residual risk | The registry is a repository file, so an actor with write access can forge an entry — but it cannot lower the authority floor (read from the verified kernel), cannot approve elevated permissions (the gate record is checked), and is reported by D028 when it does not match a descriptor. There is no cryptographic signature chain in this release. Interpreter-only commands (`python3 -m pkg`) have no local file to hash and are pinned by version alone; this is reported in the grant. |

### V-H2 (HIGH) — constitutional floors were read from an unverified installed kernel

| | |
|---|---|
| Root cause | `policy_precedence::load` and `PolicySet::load` read `governance/kernel/policies/*.yaml` from disk and trusted whatever was there. Editing the installed `POLICY_PRECEDENCE.yaml` re-enabled every weakening override and let an L0 role create tasks; editing the installed `SECURITY_POLICY.never_index_classes` removed a restricted-class exclusion at index time. The condition *was* detected (D003, `gov kernel verify`, audit) but no enforcement path consulted it — while the absent-file path already failed closed to the embedded payload. |
| Violated invariant | Framework §21 precedence and INV-006/INV-007: constitutional enforcement may not consume kernel state that has not been authenticated against the installed release identity. |
| Trust source before | Whatever bytes were at `governance/kernel/**` — project-controlled files, class T4. |
| Trust source after | `kernel_trust::trust(root)`: the installed release is identified from `framework.lock`; the payload is verified against its own `KERNEL_MANIFEST.json`; that manifest is verified against `framework.lock.kernel_manifest_hash` (so neither file nor manifest can be rewritten alone). Verified → the installed payload is the policy root (T1). Not verified → the immutable payload embedded in this binary is substituted **explicitly** (T1), never mixed, and recorded. |
| Implementation change | New `runtime/src/kernel_trust.rs` (verdict, per-process cache invalidated by `install_kernel`, `write_lock` and `Project::invalidate`, `trusted_root`, `guard`, `request_override`). `PolicySet::load` takes the repository root, resolves the trusted policy root, records `kernel_trust` and pushes the substitution into `problems`; `policy_precedence::load` reads the same root. Every other direct kernel read now goes through `trusted_root`: `authority::roles_doc`, `routing`, `handoffs`, `adapters`, `verification`, `policy_coverage`, and the migration secret scanner. `control::guard_write` (the single mutating choke point, 27 call sites) and `memory::indexer::rebuild` call `kernel_trust::guard`, which returns `KERNEL_TAMPERED` unless the operation is a remedy (`kernel reinstall`, `kernel verify`, `recover`, `update --rollback`, controls) or the human-decision channel (`gate present`, `gate answer`) — kept open because that is how the remedy is recorded, while everything a gate could unblock stays refused. `gov kernel trust` reports the verdict; `gov kernel override --reason` raises an L4+ gate bound to a fingerprint of that exact kernel state. Doctor D029, the `policy_precedence` suite family, `gov policy overrides` and context-packet layer 2 all carry the verdict. |
| Files / components | `runtime/src/kernel_trust.rs`, `runtime/src/policy.rs`, `runtime/src/{authority,routing,adapters,policy_coverage,doctor,lock,kernel}.rs`, `runtime/src/orchestration/{control,handoffs}.rs`, `runtime/src/memory/indexer.rs`, `runtime/src/migrations/verify.rs`, `runtime/src/verification/mod.rs`, `runtime/src/context/mod.rs`, `runtime/src/project.rs`, `cli/src/main.rs`, `framework/policies/AUTHORITY_POLICY.yaml`. |
| Builder regression test | `repair3::constitutional_floors_require_a_verified_kernel` |
| Original verifier tests after repair | **VV-03 → PASS** and **VV-14 → PASS** |
| Adjacent attack tests | precedence file tampered, deleted, and restored; `SECURITY_POLICY` floor tampered (never-index class removed) with the restricted document still excluded from retrieval; `KERNEL_MANIFEST.json` rewritten to match the tampered payload (caught by the lock comparison, D004); `task create` (L0 and L4), `rebuild-memory`, `cit propose` and `gate create` all refused; D003/D004/D029 and `gov kernel verify` name the exact file; the override refused for L3, raised for L4, inert until the gate is answered, and invalidated by a *different* subsequent tampering; full restoration returns the system to HEALTHY. |
| Residual risk | `framework.lock` is itself a repository file; an actor who rewrites the payload, the manifest **and** the lock coherently presents a self-consistent kernel. Detecting that requires comparing against the release registry or a signature chain, which this release does not have — the mitigation is that such a change is a visible, reviewable diff of tracked governance files, and that `release_commit`/`release_hash` in the lock are checkable against the published release. Substituting the embedded baseline can mean *newer* floors than the installed version declared; deliberate, since floors only strengthen, and every mutating operation is refused while it applies. |

### V-M1 (MEDIUM) — `PROJECT_EXCEPTIONS` decisions were self-attested

| | |
|---|---|
| Root cause | `policy.rs` tested only that the `decision` field was a non-empty string, so `decision: D-DOES-NOT-EXIST` applied. Reachable for `exception_relaxable` keys, which include `BUDGET_POLICY.defaults.*`, `CHECKPOINT_POLICY.watchdog.*` and the `MEMORY_POLICY.regression.*` quality floors — a repository could silently disable its own retrieval-regression gates, checkpoint watchdogs and spend caps with a fabricated governance reference. |
| Violated invariant | An exception is a governed decision with an expiry, not a waiver a project writes for itself (framework §21; AUTHORITY_POLICY precedence). |
| Trust source before | The `decision` string inside the overlay (T4). |
| Trust source after | The governed record it names (T2), resolved from `spec/` and checked for existence, type, ACTIVE status, supersession, revocation, expiry, approver authority (`AUTHORITY_POLICY.authority_levels_required.grant_policy_exception`, or human approval), explicit scope over this exception id or policy key, and project scope. |
| Implementation change | New `runtime/src/exceptions.rs` (`resolve_record` — a recursion-free lookup that does not load the record store, and `validate`). `PolicySet::load` calls it before the precedence evaluation; refusals land in `refused_overrides` with the reason and are reported by doctor D027. Decision schema 1.1.0 gains `authorises_exceptions`, `permits_policy_keys`, `applies_to_project`, `expires`, `revoked`. |
| Files / components | `runtime/src/exceptions.rs`, `runtime/src/policy.rs`, `framework/schemas/decision.schema.json`, `framework/policies/{AUTHORITY_POLICY,ENFORCEMENT_MAP}.yaml`. |
| Builder regression test | `repair3::policy_exceptions_require_a_real_governing_decision` (plus unit tests in `exceptions.rs`) |
| Original verifier test after repair | **VV-03 → PASS** (`exception_with_fabricated_decision_applied: false`) |
| Adjacent attack tests | nonexistent decision; no decision at all; a record of another type; a real decision that does not name the exception or key; superseded; REJECTED; revoked; expired; approved by an insufficient authority; scoped to another project; and an exception aimed at a constitutional floor, which no decision can authorise. |
| Residual risk | The decision record is a repository file: an actor who can write the overlay can usually also write `spec/`. The exception is then a visible, reviewable governed record with an approver, a scope and an expiry — which is the point — and it still cannot reach any non-`exception_relaxable` key. |

## 4. Trust-boundary audit (directive §5)

Recorded as decision **D-0007**: trust classes (immutable release state > OS-written project state > verified derived
state > project configuration > caller input > plugin/model output) and the rule that a fact named `approved`,
`registered`, `verified`, `human_approved`, `authority`, `role`, `trusted`, `provenance`, `exception` or `override`
may be established only by the two highest classes.

| Input | Class | Fact it was allowed to establish | Verdict |
|---|---|---|---|
| Plugin descriptor `approved_roles` / `provenance` / `status` | T4 | authorisation, registration | **Repaired (V-H1)** — inert, recorded, reported |
| Installed kernel policy files | T4 unless authenticated | every constitutional floor | **Repaired (V-H2)** — verified or substituted, mutations refused |
| `PROJECT_EXCEPTIONS.decision` | T4 | a governing decision | **Repaired (V-M1)** — resolved against T2 |
| Tool descriptor `security_review: passed`, `license`, `reversible` | T4/T5 | skipping the installation gate | **Repaired (new finding)** — `security_review_record` must resolve to a governed record, else the condition fails and a gate is raised (`tool` schema 1.2.0) |
| CIT `approval` / decision `human_approved` | T2, but caller-writable | human approval | Already derived from the gate answer at approve **and re-derived at execute** (C-N1); re-tested here |
| Task report `files_changed` | T5 | mutation compliance | Already cross-checked against the observed working tree (M-N4); re-tested here |
| `--by` on `gov decide` | T5 | human vs agent answer kind | Derived from the acting role's authority and `agent_resolvable_when`; the acting role itself is caller-declared (see below) |
| `memory select --by` | T5 | `human_approved` on the selection decision | Derived from the acting role's level (L-N3) |
| Plugin stdout | T6 | index content, symbols | Validated shape; never a permission; secret/restricted content never reaches a plugin (VV-17/NV-17) |
| `--role` / `--session` | T5 | which authority level acts | **Documented boundary** (V-L5, `docs/ARCHITECTURE.md` §4.8): the OS enforces what a role may do; binding a session to an identity is the adapter's responsibility. Unchanged in this release and stated as such. |

`repair3::lower_trust_inputs_cannot_manufacture_higher_trust_facts` asserts four of these end to end (self-certified
tool review, forged approval decision, self-attested mutation report, hand-written plugin registry entry).

## 5. Verifier tests that cannot change verdict on this candidate (documented, not modified)

- **NV-09, NV-19** (second harness) read the immutable, rejected **4.1.3** payload. Both underlying defects are
  repaired in 4.1.4/4.1.5; the third verifier independently confirmed this (VV-05, VV-06).
- **VV-05, VV-07** (third harness) are pinned to the **4.1.4** candidate identity: VV-05 requires
  `release/releases/4.1.4/kernel/KERNEL.yaml` to equal `framework/KERNEL.yaml` in the working tree, and VV-07 requires
  HEAD to carry the `v4.1.4-rc1` tag. Both are necessarily false for a 4.1.5 candidate and could only be made true by
  not repairing. Everything else they measure passes: 193 kernel YAML files scanned with the sole duplicate key in the
  frozen 4.1.3 payload, manifest agreement, payload verification, reproduction from the recorded commit, immutability
  and provenance. The 4.1.5 equivalents are asserted by
  `repair3::current_release_payload_identity_and_hygiene`.
- **HV-08b** (first harness) remains a non-blocker by construction (D-0006), as both later verifiers confirmed.
- **NV-16** asserts that a release build leaves `release/releases` untouched in git. It reports dirty in the working
  tree while a new payload directory is still untracked, and PASSES from the committed tag — the clean-clone
  reproduction is the authoritative evidence, and it passes there.

## 6. Escalation boundary (directive §9)

No Human Decision Gate was required. Both HIGH findings were repairable within the existing architecture: they were
one mistake — reading an assertion from the artefact whose privileges that assertion controls — and the repair adds a
verification boundary and an authoritative record rather than changing any subsystem's shape. No architectural
redesign is implied, and no finding was worked around.

## 7. Records

D-0007 (trust classes), TASK-0012, RPT-0012, migration `migrations/M-4.1.4-4.1.5.yaml`, release notes
`release/notes/4.1.5.md`, and the updated `docs/ARCHITECTURE.md` §4.4a/§4.7/§4.8, `docs/COMMANDS.md`,
`docs/FIXTURES.md`, `docs/DECISIONS.md` and `README.md`.
