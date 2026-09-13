# Output 2 — Complete privileged-ingress map

An **ingress** is any route by which bytes can enter, replace, select or be executed as privileged framework material,
or by which a fact about such material (identity, certification, compatibility, gate requirement) can be established.
The map was produced by enumerating every caller of `install_kernel`, `write_lock`, `stage_payload`,
`resolve_kernel_source`, `embedded_kernel_dir`, `load_migrations`, every direct reader of `Project::kernel_dir()`,
every `GOV_*` environment variable, every CLI subcommand in `cli/src/main.rs`, and every Git-tracked or runtime
location that holds kernel state.

Trust locations (the destinations RoT-1 protects): `governance/kernel/**`, `governance/trust/**` (new),
`governance/framework.lock`, the embedded-kernel materialisation directory, migration execution, and the in-process
policy root returned by `kernel_trust`.

Legend — *Now*: current authentication. *Class*: provenance class of the incoming material under the D-0008 table
(`15-D-0007-SUPERSESSION.md`). *Req*: integration requirement ID in `09-INTEGRATION-REQUIREMENTS.md`.

## 1. Kernel and release ingress

| ID | Route | Code path | Material / destination | Now | Defect (evidence) | Class | RoT-1 control | Req |
|---|---|---|---|---|---|---|---|---|
| I-01 | `gov init [--source P]` | `init::init` → `resolve_kernel_source` → `install_kernel` → `write_lock` | any kernel dir → `governance/kernel`, lock | none: manifest regenerated from source | V-H3 | T5 | `authenticate(SourceRef)` → install transaction consuming `AuthenticatedRelease` | R-INIT-* |
| I-02 | `gov init --force` on an installed project | same as I-01; authority read from the currently installed kernel | replaces an installed kernel | none | V-H3 + no downgrade rule | T5 | treated as reinstall/update: identity, downgrade and gate rules apply; authority read from the authenticated trust root | R-INIT-6 |
| I-03 | `gov adopt migrate --batch 0 [--source P]` | `adopt::a6_migrate` batch 0 | install; when a lock exists, reads the existing manifest unverified | none | V-H3 class | T5 | same as I-01; existing installation authenticated first | R-ADOPT-* |
| I-04 | `gov update --check --source P` | `update::check` → `source_manifest` (reads `P/../manifest.json`) → dry-run `apply` over migrations from the source and its parent | identity, compatibility, certification, gate requirement | none; **certification self-declared** | E2 | T5 | check = `authenticate` in read-only mode; all decision inputs from statements | R-UPD-1..3 |
| I-05 | `gov update --apply [--approve]` | `update::apply_update` → `install_kernel` → `load_migrations(kernel_dir)` → `apply` → `write_lock` → `set_lock_field` | kernel, migrations executed, lock | none | V-H3, E2 | T5 | install transaction; migrations from the authenticated object only; lock-field allowlist; gate bound to statement digest | R-UPD-4..12 |
| I-06 | automatic rollback inside `apply_update` on any failure | `update::rollback` | snapshot → kernel, overlay, generated, lock | none | E5 class | T4 (runtime dir) | transaction rollback restores the previous *authenticated* state recorded in the journal | R-TX-* |
| I-07 | `gov update --rollback [--reason]` | `update::rollback` | `.governance-runtime/update/<v>/` (gitignored, user-writable) | `verify_kernel` against the snapshot's own manifest | E5 | T4 | snapshot carries statement bytes; restore = authenticate + ledger-bound downgrade rule + gate | R-RB-* |
| I-08 | `gov kernel reinstall [--source P]` | `cli/src/main.rs` `KernelCmd::Reinstall` | any source; accepted when `payload_hash == lock.release_hash` | compared to a repository-writable lock value | E4 + I-01 | T5 | must authenticate **and** equal the installed statement digest; the lock is never the reference | R-RI-* |
| I-09 | `gov kernel override --reason` | `kernel_trust::request_override` | permission to operate on an untrusted kernel (not material) | L4+ gate bound to fingerprint | sound | T2 | retained; never marks a kernel authenticated; floors stay on the authenticated baseline | R-OV-1 |
| I-10 | `gov recover` | `recovery::recover` (CIT rollback, adoption batch rollback, runtime DB rebuild, claims) | project state only today | n/a | none, but no install-transaction recovery exists | T2/T4 | adds interrupted-install recovery; must never restore kernel/lock/trust except through the transaction journal | R-REC-* |
| I-11 | Embedded payload materialisation | `kernel::embedded_kernel_dir` (`$GOV_KERNEL_CACHE`, `$XDG_CACHE_HOME/gov`, `~/.cache/gov`, temp) | install source for I-01/I-03/I-08 when no `--source` | reused when `KERNEL.yaml` and `.complete` exist | E3 | T4 | embedded bytes served from memory or re-verified against compiled-in digests on every use | R-EMB-* |
| I-12 | V-H2 fail-closed baseline | `kernel_trust::compute` → `embedded_kernel_dir` | policy root for all enforcement when installed kernel is untrusted | same as I-11 | E3 | T4 | same as I-11 | R-EMB-3 |
| I-13 | `GOV_CANONICAL_ROOT` | `kernel::canonical_root` in `resolve_kernel_source`; `Project::schemas` fallback; `adopt::scanner_for` | developer checkout as install source; schemas; adoption secret-scanner policy | none | TH-11 | T5 | source selection only; authenticated if its staged tree matches a signed statement, else the unsigned development path; never used for schemas or scanner policy | R-ENV-1 |
| I-14 | `GOV_KERNEL_SOURCE` | `adopt::scanner_for` | `SECURITY_POLICY` for the pre-install adoption scanner | none | TH-11 | T5 | removed; pre-install scanner uses the authenticated embedded baseline | R-ENV-2 |
| I-15 | **Git delivery**: pull, merge, checkout, rebase, cherry-pick, PR merge, clone on a second machine | none (no `gov` involvement) | `governance/kernel/**`, `framework.lock`, future `governance/trust/**` | integrity only (self-consistent set passes) | E4 | T4 | use-time authentication against the installed statement under T0 | R-USE-* |
| I-16 | In-place edit of the installed kernel | none | `governance/kernel/**` | V-H2 integrity check | closed | T4 | preserved | R-USE-4 |
| I-17 | Use-time readers outside `kernel_trust` | `Project::schemas` (+ `GOV_CANONICAL_ROOT` fallback), `Project::kernel_manifest`, `tools::kernel_tools`, `tools::mcp_servers`, `skills`, `adapters::invariants`/templates, `context` HARD_INVARIANTS, `orchestration::intents`, `orchestration::readiness`, `verification` HARD_INVARIANTS/COMMAND_CONTRACT, doctor D003 | schemas, tool registry, skills, invariants, command contract | none at read time | TH-14 | T4 | one `TrustedKernel` read handle; architecture test forbids `kernel_dir()` outside the trust module | R-USE-5 |
| I-18 | Migration loading and execution | `update::migrations_for_source` (source and **its parent** dir), `kernel::stage_payload` sibling fallback for `migrations`/`tools`, `migrations::framework::apply`, `set_lock_field` (any key) | overlay, lock, generated | none | TH-12 | T5 | statement lists every migration id/from/to/digest; only migrations inside the authenticated tree run; `set_lock_field` restricted to non-identity keys | R-MIG-* |
| I-19 | `gov release build` (producer) | `release::build` | payload + unsigned `manifest.{json,yaml}`; certification default `READY_FOR_INDEPENDENT_OS_VERIFICATION` | n/a | no separation of build from signing | T4 | emits an **unsigned statement payload**; signing is an external offline step; build refuses private key material | R-REL-1..4 |
| I-20 | `gov release verify DIR` | `release::verify` | a verdict used as evidence by operators and verifiers | self-referential | E1 | T5 | becomes `authenticate` in report-only mode | R-REL-5 |
| I-21 | Certification block transcription into `manifest.{json,yaml}` | manual (release owner, per `VERDICT.md`) | certification status consumed by I-04 | unsigned | E2 | T5 | signed certification statement by the certification role; manifest block becomes descriptive only | R-CERT-* |
| I-22 | Binary build and distribution (`cargo build`, `runtime/build.rs`) | `build.rs` embeds `framework/`, `migrations/`, `tools/`, and `release_commit` from `release/releases/<v>/manifest.json` or `git rev-parse HEAD` | T0 carrier | none | provenance string from an unsigned file | TCB | build embeds statement bytes if present; runtime authenticates them; artifact statement for binaries; bootstrap fingerprint | R-EMB-4, `06-BOOTSTRAP.md` |
| I-23 | Future private-GitHub (or any remote) release fetch | none yet (`REMOTE_TRANSPORT_NOT_CONFIGURED` for upstream) | bundle download | n/a | would inherit A1/A5 | T5 | transport-only `gov release fetch` into quarantine; identical authentication | R-NET-* |
| I-24 | Packaged release bundle (tar/zip) | none yet | archive extraction | n/a | archive path traversal, symlinks | T5 | safe extraction rules, then authentication | R-BUN-* |

## 2. Adjacent ingress where framework trust is relevant

| ID | Route | Code path | Now | Relevance | RoT-1 treatment | Req |
|---|---|---|---|---|---|---|
| I-25 | Plugin descriptors `governance/project/plugins/*.yaml`, `$GOV_PLUGINS_DIR`, `gov plugins register` | `capabilities::host::discover_all`, `registry::record`, `governance::authorize` | D-0007 registry binding (T2) + authority floor from verified kernel | the floor must come from an *authenticated* kernel; profile-shipped plugins need provenance | floor read via `TrustedKernel`; registry entries of profile plugins bind `profile_statement_digest`; descriptors from `$GOV_PLUGINS_DIR` can never carry profile trust | R-PLG-* |
| I-26 | `gov tools install` executing `install_command` | `tools::install` | TOOL_POLICY conditions + governed `security_review_record` | kernel-shipped tool descriptors are framework material | kernel descriptors authenticated as part of the release; project descriptors stay governed by TOOL_POLICY; package hash pins recommended (non-blocking) | R-TOOL-1 |
| I-27 | `gov memory benchmark` / `select` writing `MEMORY_POLICY.embedding.*` pins into `PROJECT_POLICY.yaml` | `memory::benchmark::select` | gated decision + overlay (T4) | choice of retrieval implementation | unchanged for arbitrary plugins; a reference-profile pin additionally binds the profile statement digest | R-PRF-6 |
| I-28 | Reference retrieval profile installation | none today; plugin template pins `--model sentence-transformers/all-MiniLM-L6-v2` by name only | none | model and runtime supply chain | signed profile statement (`10-RETRIEVAL-PROFILE-TRUST.md`) | R-PRF-* |
| I-29 | Upstream lessons into canonical `lessons/inbox/` → change proposals → release | `upstream::submit` (local path only) | export gate | input to framework development, not trusted state | trust boundary is the signing ceremony: sign-what-you-reproduced, independent verification, separate certification key | `05-KEY-MANAGEMENT.md` §3 |
| I-30 | Pre-install adoption planning policy | `adopt::a3_map` reads `ARCHIVE_POLICY` via `resolve_kernel_source(None)` | none (env-redirectable) | policy decides destructive actions | authenticated embedded baseline | R-ADOPT-3 |
| I-31 | Generated views `governance/generated/**` (adapters, tool registry, plugin registry, index manifest) | `adapters::generate`, `tools::generate_registry` | derived (T3) | regenerated after install | generated only from `TrustedKernel` + overlay after authentication | R-UPD-9 |
| I-32 | Schemas used to validate trust statements and the lock | none yet; today `release-manifest` is validated with the schema of the payload being built | validating with the material under test is circular | statement schemas compiled into the binary, never loaded from a kernel | R-AUTH-7 |
| I-33 | Manual `framework.lock` edits | read by `kernel reinstall`, D004, D005, `Project::framework_version` | believed | lock-derived decisions | lock cross-checked against the installed statement; mismatch `LOCK_IDENTITY_MISMATCH` | R-LOCK-* |

## 3. Completeness rule (enforced by tests)

1. Only the install-transaction module may write `governance/kernel/**`, `governance/trust/**` or `governance/framework.lock`;
   its entry points accept `&AuthenticatedRelease` (or a journal-bound restore of a previously authenticated state) and
   no `Path`.
2. Only `kernel_trust` may resolve a filesystem path to kernel content; everything else receives a `TrustedKernel`.
3. No code path reads a release `manifest.json`/`manifest.yaml` or a source `KERNEL_MANIFEST.json` to make a decision.
4. Every CLI subcommand that reaches (1) is listed in an ingress register asserted by the `release_ingress` test family,
   and each is exercised with a tampered source (RT-27).
5. A new `GOV_*` environment variable that selects kernel material fails the architecture test unless registered as
   *source selection only*.
