# Output 3 — Privileged-Ingress Coverage Matrix

For every route by which bytes can enter, replace, select or be executed as privileged framework material, or by which
a fact about such material can be established:

- **Auth before stage/mutate**: does RoT-1 authenticate before any staging or write to a trust location?
- **Currency / post-install**: after admission, is the material checked for integrity and acceptability at use?

Verdicts: **COVERED**, **PARTIAL**, **NOT COVERED**, **UNMAPPED** (an ingress the pack's map does not list).

## 1. Flows named in the review brief

| Flow | Pack rows | Auth before stage/mutate | Currency / post-install | Verdict | Findings |
|---|---|---|---|---|---|
| `gov init` | I-01, I-02 | yes (R-INIT-1; nothing under `governance/` before V14) | integrity yes. Authority for the first install is read from the **target** (`09` §1 step 2). REJECTED gating is bypassable by omitting the REJECTED certification. | **PARTIAL** | RV-M3, RV-H2 |
| `gov adopt` (batch 0 and pre-install stages) | I-03, I-30 | yes (R-ADOPT-1..3) | yes for batch 0; **batch rollback unmapped** (I-34) | **PARTIAL** | RV-M1 |
| `gov update` (check / apply / auto-rollback) | I-04, I-05, I-06 | yes (R-UPD-1..4) | gate skipping relies on certification without freshness; signed migrations may weaken project strengthening without a gate | **PARTIAL** | RV-H2, RV-M8 |
| Kernel reinstall | I-08 | yes; statement digest must equal the installed one; `lock.source` is never a path (R-RI-1..2) | yes | **COVERED** | — |
| Repair / recovery | I-10 | journal-bound restore only (R-REC-3) | forged journal + `.kernel.prev` is caught only by the lock cross-check (A3 alone); **adoption batch restore** bypasses the journal entirely | **PARTIAL** | RV-M1, RV-H1 |
| Rollback (explicit) | I-07 | yes (R-RB-1) | downgrade bound to the ledger, which A2 can write; no use-time floor | **PARTIAL** | RV-H1 |
| Migration | I-18 | yes (V10 id/path/digest; lock allowlist) | chain uniqueness unspecified; strengthening removal ungated | **PARTIAL** | RV-M8 |
| Embedded / bundled source | I-11, I-12, I-22, I-24 | yes (in-memory digests; marker never evidence; archive rules) | yes | **COVERED** | RV-L2 (build profile) |
| Local source (`--source`, `GOV_CANONICAL_ROOT`) | I-01, I-13 | yes; unsigned → refused or explicit `DEVELOPMENT_UNSIGNED` | yes | **COVERED** | — |
| Private GitHub / release source | I-23 | transport only; offline authentication (R-NET-1..3) | same as bundles | **COVERED** (deferred) | — |
| Future release package | I-24 | extraction rules then authentication (R-BUN-1) | same | **COVERED** | — |
| Git delivery to a consumer repository | I-15 | n/a (no `gov`) | forged or regenerated sets refused; **older genuine or legacy set accepted as policy root** | **PARTIAL** | RV-H1 |

## 2. Full register

| ID | Route | Code today | Review verdict | Note |
|---|---|---|---|---|
| I-01 | `init [--source]` | `init.rs:217-248` | PARTIAL | RV-M3 (authority from target), RV-H2 |
| I-02 | `init --force` | `init.rs:219-226` | PARTIAL | treated as reinstall/update (R-INIT-6). Authority when the installed kernel is UNAUTHENTICATED must come from T0 (RV-M3). |
| I-03 | `adopt migrate --batch 0` | `adopt.rs:628-646` (reads an existing manifest unverified at `:631-632`) | COVERED | R-ADOPT-2 replaces the unverified read |
| I-04 | `update --check` | `update.rs:46-102` | PARTIAL | RV-H2 |
| I-05 | `update --apply` | `update.rs:118-342` | PARTIAL | RV-H2, RV-M8 |
| I-06 | automatic rollback | `update.rs:330-340` | COVERED | journal |
| I-07 | `update --rollback` | `update.rs:348-420` | PARTIAL | RV-H1 |
| I-08 | `kernel reinstall` | `cli/src/main.rs:853` (follows `lock.source` if it exists as a path; compares with `lock.release_hash`; runs as an EXEMPT operation while tampered) | COVERED | R-RI-1..2 and RT-12 close the lock-as-path vector |
| I-09 | `kernel override` | `kernel_trust.rs:320-347` | COVERED | floors stay on the baseline (R-OV-1). Gate records are A2-writable, but override only unlocks mutations, never floors. |
| I-10 | `recover` | `recovery.rs:9-147` (CIT rollback; **adoption batch rollback** `:30-57`) | PARTIAL | the pack describes it as “project state only today”; incorrect, see I-34 |
| I-11 | embedded materialisation | `kernel.rs:31-80` | COVERED | — |
| I-12 | V-H2 baseline | `kernel_trust.rs:191-238` | COVERED | — |
| I-13 | `GOV_CANONICAL_ROOT` | `kernel.rs:83-112`, `project.rs:127-139`, `adopt.rs:79` | COVERED | — |
| I-14 | `GOV_KERNEL_SOURCE` | `adopt.rs:80` | COVERED | removed |
| I-15 | Git delivery | none | PARTIAL | RV-H1 |
| I-16 | in-place edit | `kernel_trust.rs:134-148` | PARTIAL | static edits covered; racing edits not (RV-H3, **E** R2b) |
| I-17 | use-time readers | `context/mod.rs:93-97`, `tools.rs`, `skills.rs`, `adapters.rs`, `orchestration/{intents,readiness}.rs`, `verification/mod.rs` | PARTIAL | the `TrustedKernel` design is right; enforcement must be path-based (RV-M1) and byte-bound (RV-H3) |
| I-18 | migration loading and execution | `update.rs:19-27, 201-233`; `kernel.rs:226-232`; `migrations/framework.rs:236-242` | PARTIAL | RV-M8 |
| I-19 | `release build` | `release.rs:62-228` | COVERED | determinism (RV-L3) |
| I-20 | `release verify` | `release.rs:230-256` | COVERED | — |
| I-21 | certification transcription | manual | PARTIAL | RV-H2, RV-M5 |
| I-22 | binary build | `build.rs:40-117` | PARTIAL | RV-L2, RV-M6 |
| I-23 | remote fetch | none | COVERED | deferred |
| I-24 | bundles | none | COVERED | — |
| I-25 | plugin descriptors | `capabilities/{host,registry,governance}.rs` | COVERED | floor via `TrustedKernel` |
| I-26 | `tools install` | `tools.rs` | COVERED | — |
| I-27 | memory select pins | `memory/benchmark.rs` | COVERED | — |
| I-28 | reference profile install | none | PARTIAL | RV-M7 |
| I-29 | upstream lessons | `upstream.rs` | COVERED | procedural boundary |
| I-30 | pre-install adoption policy | `adopt.rs:74-95, 280-292` | COVERED | — |
| I-31 | generated views | `adapters.rs`, `tools.rs` | PARTIAL | `adapters.rs:168` compares `kernel_hash` with `lock.kernel_manifest_hash`; see I-37 |
| I-32 | statement schemas | none | COVERED | compiled |
| I-33 | manual lock edits | `project.rs:113-119`, doctor D004/D005 | COVERED | — |

## 3. Ingress routes absent from the pack's map

| ID | Route | Code | What it can do | Adversary | Verdict | Finding |
|---|---|---|---|---|---|---|
| **I-34** | Adoption batch rollback: `gov adopt rollback --batch N`, and `gov recover` for an interrupted batch | `migrations/executor.rs:9-13` (snapshot under `.governance-runtime/migration/batch-N/`), `:304-350` (restores **every** file under `files/` to the same relative path; `git rm` of `created`) | restores `governance/kernel/**`, `governance/framework.lock` and, once it exists, `governance/trust/**` from a user-writable snapshot; with an older genuine set this is an **A3-only downgrade** (RV-H1) | A3 | **UNMAPPED** | RV-M1 |
| **I-35** | CIT file operations | `cit/mod.rs:700-708` (`write_file` refuses only `governance/kernel/**`); `:713` `move_file` and `:731` `delete_file` carry **no** governance path guard; CIT snapshot restore `:1124-1185` | writes, moves or deletes `governance/framework.lock` and `governance/trust/**`; moves or deletes kernel files | A2 through an approved CIT; A3 through the CIT snapshot | **UNMAPPED** | RV-M1 |
| **I-36** | Adoption A7 migration verification and A11 audit | `adopt.rs:816`, `adopt.rs:1363` (`verify_kernel` against its own manifest) | D-0007 predicate decides `MIGRATION_ACCEPTED_FOR_MEMORY_REBUILD` and an audit result | A2 | **UNMAPPED** | RV-M1 |
| **I-37** | Adapter freshness check | `adapters.rs:168` | lock-derived hash decides adapter validity | A2 | **UNMAPPED** | RV-M1, RV-M4 |
| **I-38** | Partial install states | `kernel_trust.rs:128-130` (missing manifest or lock ⇒ `uninstalled`, `policy_root = governance/kernel`); `:289-291` (`guard` passes when not installed); `cli/src/main.rs:743` (`doctor`), `:865` (`capabilities`) open without requiring installation | policy root silently becomes an unverified directory | A2, A3 | **UNMAPPED** | RV-M2 |
| **I-39** | Trust metadata refresh and user trust store | proposed `gov trust refresh --from <file\|url>`; `$XDG_CONFIG_HOME/gov/trust-state.json` (`05` §5) | selects the revocation and root high-water marks; location is env-selectable | A3, A4 | **UNMAPPED** as an ingress | RV-H2 |
| **I-40** | Pre-RoT-1 binaries opening RoT-1 projects | `kernel_trust.rs:156-169` with lock 2.0.0 keeping `kernel_manifest_hash`/`release_hash` (`08` §3) | circular D-0007 trust continues for any collaborator on ≤4.1.5 | A2 | **UNMAPPED** | RV-M4 |
| **I-41** | Install journal and `.kernel.prev-<TX>` / `.trust.prev-<TX>` | proposed `09` §3 | forged phase + planted previous set drives swap-back | A3 (bounded by lock cross-check); A2+A3 | **UNMAPPED** as an adversarial input | RV-H1 |

## 4. Completeness-rule assessment (`02` §3)

The pack enforces completeness by type signatures (`&AuthenticatedRelease`) and by source inspection for
`kernel_dir()`, `install`, `write_lock`. That is necessary but not sufficient. I-34 and I-35 write trust locations
through generic file APIs with computed relative paths, which no symbol grep will flag. **Required:** a single governed
filesystem layer that refuses writes, renames and deletes under `governance/kernel/**`, `governance/trust/**` and
`governance/framework.lock` unless the caller holds an install-transaction token. It must be proven by write
interception across every CLI command in the conformance suite (AC-G1..G3).
