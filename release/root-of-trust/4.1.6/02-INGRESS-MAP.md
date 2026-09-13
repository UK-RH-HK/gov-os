# Output 2 — Privileged-ingress map

> **RoT-1 revision 2 — PROPOSED, pending a fresh independent review; not approved, not implemented.**
> Revision 2 adds the eight ingress routes the independent review found missing (I-34…I-41), six more found while
> amending (I-42…I-47), and a complete inventory of file-mutation mechanisms against the Protected Path Set (§4).
> Addresses RV-M1 (CD-5).

An **ingress** is any route by which bytes can enter, replace, select or be executed as privileged framework material, or
by which a fact about such material (identity, eligibility, certification, revocation, floors, gate requirement) can be
established.

Legend. *4.1.5 code*: where the route exists today. *Class*: provenance class under D-0008 (`15` §4). *Control*: the
revision 2 mechanism. *Req*: requirement group in `09`.

## 1. Kernel and release ingress

| ID | Route | 4.1.5 code | Class | Revision 2 control | Req |
|---|---|---|---|---|---|
| I-01 | `gov init [--source P]` | `init.rs:217-248` | T5 | secure read → `authenticate` → eligibility → authority floor from TPS ⊔ embedded (never the target) → init acknowledgement gate → install transaction | R-INIT |
| I-02 | `gov init --force` on an installed project | `init.rs:219-226` | T5 | treated as reinstall (same statement digest) or update/downgrade (different digest); authority from the floor | R-INIT |
| I-03 | `gov adopt migrate --batch 0 [--source P]` | `adopt.rs:628-646` | T5 | same pipeline as `init` (operation `adopt_install`); an existing installation is evaluated through the installation state machine, never read unverified | R-ADOPT |
| I-04 | `gov update --check` | `update.rs:46-102` | T5 | `authenticate` in report mode; eligibility, trust state, certification view, computed weakenings and gate requirement from signed data only | R-UPD |
| I-05 | `gov update --apply` | `update.rs:118-342` | T5 | re-authenticate; eligibility; gate (mode A always); migrations from ARO blobs; weakening gate; install transaction | R-UPD |
| I-06 | Automatic rollback inside a failed update | `update.rs:330-340` | T4 | journal exchange-back, then normal evaluation (`20` RB-1) | R-RB |
| I-07 | `gov update --rollback` | `update.rs:348-420` | T4 | restore pipeline + downgrade policy (`20` §2, §4) | R-RB |
| I-08 | `gov kernel reinstall [--source P]` | `cli/src/main.rs:853` | T5 | must authenticate to the installed statement digest; never follows `lock.source`; re-attestation allowed | R-RI |
| I-09 | `gov kernel override --reason` | `kernel_trust.rs:320-347` | T2 | fingerprint-bound L4+ gate permitting governed mutations on an untrusted kernel; never changes authenticity, eligibility or the policy root; unavailable for revoked releases | R-OV |
| I-10 | `gov recover` | `recovery.rs:9-147` | T2/T4 | CIT and adoption recovery through GovernedFs (never protected paths); install-journal recovery per `20` §5 | R-REC |
| I-11 | Embedded payload | `kernel.rs:31-80` | T0 | in-memory EmbeddedSnapshot; never materialised for trust | R-EMB |
| I-12 | Fail-closed baseline | `kernel_trust.rs:191-238` | T0 | EmbeddedSnapshot ⊔ effective floor | R-EMB |
| I-13 | `GOV_CANONICAL_ROOT` | `kernel.rs:83-112`, `project.rs:127-139`, `adopt.rs:79` | T5 | source selection only; never schemas or scanner policy | R-ENV |
| I-14 | `GOV_KERNEL_SOURCE` | `adopt.rs:80` | T5 | removed | R-ENV |
| I-15 | Git delivery (pull, merge, checkout, clone, PR merge) | none | T4 | evaluated at use: authenticity, integrity, eligibility (E10), floors (`19`), installation state (`18` §9) | R-USE |
| I-16 | In-place edit or race on installed files | none | T4 | per-process KernelSnapshot from the secure reader; enforcement from snapshot bytes | R-USE |
| I-17 | Use-time readers of kernel content | `context/mod.rs:93-97`, `tools.rs`, `skills.rs`, `adapters.rs`, `orchestration/{intents,readiness}.rs`, `verification/mod.rs`, `project.rs:120-139` | T4 | KernelSnapshot API only; GovernedFs read guard | R-USE |
| I-18 | Migration loading and execution | `update.rs:19-27, 201-233`; `kernel.rs:226-232`; `migrations/framework.rs:7-58, 236-242` | T5 | only from ARO blobs; unique chain; statement/file equality; no lock operation; weakening gate | R-MIG |
| I-19 | `gov release build` (producer) | `release.rs:62-228` | T4 | unsigned candidate payload; deterministic inputs; floor-registration check; private-key scan | R-REL |
| I-20 | `gov release verify DIR` | `release.rs:230-256` | T5 | `authenticate` in report mode | R-REL |
| I-21 | Certification publication | manual transcription into `manifest.*` | T5 | verification attestation → certification statement → trust-state reference; manifests descriptive only | R-CERT |
| I-22 | Binary build and distribution | `build.rs:40-117` | TCB | compiles T0 including TPS, TSS and historical registry; separate test-profile binary; artifact statements | R-EMB, R-BOOT |
| I-23 | Remote release fetch (future) | none | T5 | transport only, into memory or scratch; then `authenticate` | R-NET |
| I-24 | Release bundle archives (future) | none | T5 | streamed into buffers under tree rules; then `authenticate` | R-BUN |

## 2. Adjacent ingress where framework trust is relevant

| ID | Route | 4.1.5 code | Revision 2 control | Req |
|---|---|---|---|---|
| I-25 | Plugin descriptors and registration | `capabilities/{host,registry,governance}.rs` | authority floor and permission classes from the effective floor; profile-bound entries record the profile statement digest | R-PLG |
| I-26 | `gov tools install` | `tools.rs` | kernel tool descriptors via KernelSnapshot; project descriptors under TOOL_POLICY; file writes through GovernedFs | R-TOOL |
| I-27 | `gov memory select` pins | `memory/benchmark.rs` | unchanged; a reference-profile pin binds the profile statement digest | R-PRF |
| I-28 | Reference retrieval profile install | none | signed profile statement; host-side verification (`10`) | R-PRF |
| I-29 | Upstream lessons | `upstream.rs` | input to development, never trusted state; writes through GovernedFs | — |
| I-30 | Pre-install adoption policy (scanner, `ARCHIVE_POLICY`) | `adopt.rs:74-95, 280-292` | EmbeddedSnapshot ⊔ floor | R-ADOPT |
| I-31 | Generated views (adapters, registries, index manifest) | `adapters.rs`, `tools.rs`, `memory/indexer.rs` | generated from the snapshot; each records the content identity (`18` VU-8) | R-USE |
| I-32 | Schemas validating trust statements and locks | none | compiled into the binary | R-AUTH |
| I-33 | Manual `framework.lock` edits | `project.rs:113-119`; doctor D004/D005 | record cross-check → `LOCK_IDENTITY_MISMATCH`; reference fields are hints | R-LOCK |

## 3. Ingress added in revision 2

| ID | Route | 4.1.5 code | What it can do without a control | Revision 2 control | Req |
|---|---|---|---|---|---|
| **I-34** | Adoption batch rollback (`gov adopt rollback --batch N`) and `gov recover` for an interrupted batch | `migrations/executor.rs:9-13, 304-350` | restore any path, including `governance/kernel/**` and `framework.lock`, from `.governance-runtime/migration/batch-N/` | batch 0 rollback is `install_tx::uninstall`; batches ≥ 1 restore through GovernedFs, which refuses PPS targets; planner never snapshots PPS paths (`20` §6) | R-ADOPT, R-FS |
| **I-35** | CIT `write_file`, `move_file`, `delete_file`, `append_record`, and CIT snapshot restore | `cit/mod.rs:700-745, 1124-1185` | `write_file` guards only `governance/kernel/**`; `move_file` and `delete_file` have no guard | planning refuses PPS (`CIT_PROTECTED_PATH`); execution and restore via GovernedFs (`20` §7) | R-FS |
| **I-36** | Adoption A7 migration verification and A11 audit kernel checks | `adopt.rs:816`, `adopt.rs:1363` | a self-manifest check decides `MIGRATION_ACCEPTED_FOR_MEMORY_REBUILD` | use the snapshot verdict (`verified` per `19` §6) | R-ADOPT |
| **I-37** | Adapter freshness check | `adapters.rs:168` | lock-hash comparison decides freshness | compare the adapter manifest's CI with the snapshot CI | R-USE |
| **I-38** | Partial install states | `kernel_trust.rs:128-130, 289-291`; `cli/src/main.rs:743, 865` | policy root silently becomes an unverified directory | installation state machine (`18` §9) | R-PART |
| **I-39** | Trust metadata refresh and the Verifier Trust Store | none (rev 1 proposed an env-selectable store) | select or reset high-water state | VTS path from the account database; only verified statements enter K; monotonic acceptance (`17` §4–§5) | R-TS |
| **I-40** | Pre-RoT binaries opening RoT-1 projects | `kernel_trust.rs:156-169` (4.1.5) | circular verification continues on RoT-1 data | trust-format boundary (`13` §3); executed F1 | R-FMT |
| **I-41** | Install journal and `.tx/<TX>/*.prev` | none | forged phase plus planted previous state | recovery re-authenticates and applies eligibility and downgrade policy (`20` §5) | R-REC |
| **I-42** | Trust Policy acceptance (bundle, refresh, PTR, VTS, compiled) | none | lower floors; remove eligibility constraints | `trust-policy` purpose (root threshold); monotonic `policy_version`; explicit `lowers[]` with a per-project gate (`19` §10) | R-TS |
| **I-43** | Trust State, certification, attestation and revocation acceptance | rev 1: V13 highest-present | stale replay; omission | admissibility; sticky negative set; views without relaxation (`17`) | R-TS, R-CERT |
| **I-44** | Lineage confirmation and pin files | none | confirm an unverified root | human command, explicit flag or pin file resolved from the account database; never environment (`06` §3) | R-BOOT |
| **I-45** | `gov`-run git subprocess mutations (adoption `git mv`, `git rm`) | `migrations/executor.rs` | move or remove protected paths | arguments pre-validated by GovernedFs (`18` §8) | R-FS |
| **I-46** | Non-`gov` subprocesses (plugins, tools, test commands) writing files | n/a | modify installed files | outside GovernedFs by nature (A3-equivalent); detected by the next snapshot; never enforced (VR-3) | R-USE |
| **I-47** | Candidate → final promotion and artifact statements | none | promote different content; mislabel candidates | `gov release promote`: same tree digest, `promoted_from_candidate`, new sequence, `release-final` purpose; V8 promotion check (`07` §7) | R-REL |

## 4. Protected Path Set and file-mutation inventory

**Protected Path Set** (`18` §8): `governance/kernel/**`, `governance/trust/**`, `governance/framework.lock`,
`governance/.tx/**`, and the directory entries `governance`, `governance/kernel`, `governance/trust`, `governance/.tx`.

Every mechanism in the runtime that mutates files, and its revision 2 treatment:

| Mechanism | 4.1.5 location | May touch PPS? | Treatment |
|---|---|---|---|
| Install transaction (init, adopt batch 0, update, rollback, reinstall, recovery, uninstall, trust refresh) | `kernel.rs`, `lock.rs`, `update.rs`, `init.rs`, `adopt.rs` | **yes, only with `InstallTxToken`** | `18` §5 |
| CIT `write_file` / `move_file` / `delete_file` / `append_record` | `cit/mod.rs:700-745` | no | planning refusal + GovernedFs |
| CIT snapshot take and restore | `cit/mod.rs:586-660, 1124-1185` | no | GovernedFs |
| Adoption executor moves, deletes, extractions | `migrations/executor.rs` | no | planner classification + GovernedFs |
| Adoption `git mv` / `git rm` | `migrations/executor.rs` | no | argument pre-validation |
| Adoption batch rollback | `migrations/executor.rs:304-350` | no (batch 0 → `install_tx::uninstall`) | `20` §6 |
| Migration overlay operations | `migrations/framework.rs:69-259` | no; the lock operation is removed | GovernedFs; weakening gate |
| Overlay template reconciliation | `migrations/framework.rs:339-382` | no | templates from ARO blobs |
| `init` roots, `.gitignore`, overlay, NOW.md | `init.rs:43-215` | no | GovernedFs |
| Gate, decision, report and other records | `records.rs`, `orchestration/gates.rs` | no | GovernedFs |
| Update ledger, checkpoints, claims, telemetry | `update.rs`, `checkpoints.rs`, `orchestration/claims.rs`, `observability.rs` | no | GovernedFs |
| Memory indexer DB and manifests | `memory/indexer.rs` | no | GovernedFs; manifest records CI |
| Adapter and registry generation | `adapters.rs`, `tools.rs`, `capabilities/registry.rs` | no | GovernedFs; outputs record CI |
| Tool installer file writes | `tools.rs` | no | GovernedFs (subprocess installs are I-46) |
| Upstream packaging, lesson clustering | `upstream.rs`, `lessons.rs` | no | GovernedFs |
| Release build output (canonical repository) | `release.rs` | n/a (writes `release/releases/<v>/`, not a consumer PPS) | producer rules (`07` §7) |

## 5. Completeness rules (enforced by tests)

1. Only `install_tx` holds `InstallTxToken`. Its entry points accept an `AuthenticatedRelease`, or an authenticated,
   eligibility-checked restore target, and an `Authorisation`. They never accept a `Path`.
2. Only `kernel_trust` and `install_tx` can open `governance/kernel/**` or `governance/trust/**`. Everything else
   receives a KernelSnapshot.
3. No code path reads a release `manifest.json`/`manifest.yaml`, a source `KERNEL_MANIFEST.json` or the installed
   tombstone to make a decision.
4. Every CLI subcommand is in a command register. The conformance suite runs each with a filesystem interception layer
   and asserts: no PPS mutation outside `install_tx`, and no open of a kernel or trust path outside the two modules.
   Inputs include protected-path CIT manifests, adoption plans, `../` spellings, case variants and symlinked parents
   (`12` RT-27, RT-48).
5. A new `GOV_*` environment variable that selects kernel material, trust metadata or a trust-store location fails the
   architecture test unless registered as *source selection only*.
6. Every ingress in this map names at least one `RT-*` scenario in `12`; the response matrix (`22`) checks this.
