# Output 2 — Privileged-ingress map

> **RoT-1 revision 7 — PROPOSED, pending fresh independent reviews; not approved, not implemented.**
> Revision 7: the certified production profile CP-1 (`35`) governs this file. Where the text below names an owner option
> other than the CP-1 selection, the freshness-witness purpose, a platform signing path, OP-3 mode B or the revision-6
> first-contact manifest, that text is non-production history: the mode is excluded and absent or refused (`35` §4). Parameters
> are the CP-1 values (`35` §2); consequence statements are the CS7 blocks of `21`, `30`, `32`–`34`.
> (Revision 6 banner follows.)
> Revision 6 amendments: new ingress I-75 (first-contact code and manifest, `32`), I-76 (environment manifests and
> reproductions, `33`), I-77 (registration revocations, `30` R-REG-11), I-78 (CI-proposed registration content, `34`), I-79
> (Git attribute and ignore sources, `26`); I-68 restated (clock high-water from every ingested non-future statement,
> CR5-B-09); admission records (I-72) are honoured only inside the verifier trust store (`31` GB-1′).
> Revision 5 amendments: new ingress **I-69** release registration statements, **I-70** reproduction statements, **I-71**
> input manifests (all carriers until selected, `30`), **I-72** admission records (local, `31` R-ADM-7), **I-73** the
> independent executor `gov-admit`, **I-74** the working directory of a RoT-1 command (root discovery, `18` §9.2). Withdrawn:
> artefact statements and build attestations (`05` §2). `governance/trust/registration.dsse.json` is in the Protected Path Set.
> Revision 4 revises I-18, I-22, I-46, I-47, I-48…I-54 and I-56, and adds I-61…I-68:
> - the system pin directory and the pin integrity predicate;
> - in-gate state confirmation;
> - `gov`-executed repository and plugin commands under confinement;
> - Overlay Surface migrations;
> - owner constitutional files;
> - the attested source of a binary;
> - the bootstrap parameters, `clock_reset` and production sources;
> - the local clock.
>
> Completeness is proven by OS-level tracing over the full command register.

An **ingress** is any route by which bytes can enter, replace, select or be executed as privileged framework material, or
by which a fact about such material can be established: identity, eligibility, surface registration, certification,
revocation, floors, gate requirements or authorisation, currency, binary acceptance.

## 1. Kernel and release ingress

| ID | Route | 4.1.5 code | Class | Revision 3 control | Req |
|---|---|---|---|---|---|
| I-01 | `gov init [--source P]` | `init.rs:217-248` | T5 | secure read → `authenticate` → E7 surface → eligibility → freshness `ANCHORED` → install-authority floor → `init_ack` trust gate (local) → install transaction creating the layout | R-INIT |
| I-02 | `gov init --force` on an installed project | `init.rs:219-226` | T5 | reinstall (same digest) or update/downgrade (different digest) with those rules | R-INIT |
| I-03 | `gov adopt migrate --batch 0` | `adopt.rs:628-646` | T5 | the `init` pipeline (`adopt_install`); layout creation (`26` §2) | R-ADOPT |
| I-04 | `gov update --check` | `update.rs:46-102` | T5 | `authenticate` in report mode; E7, eligibility, trust state, freshness, certification view, computed weakenings, gate requirement | R-UPD |
| I-05 | `gov update --apply` | `update.rs:118-342` | T5 | re-authenticate; E7; eligibility; freshness; `framework_update` trust gate (mode A); migrations from ARO; `weakening` trust gate; transaction; legacy layout migration on first RoT-1 install | R-UPD |
| I-06 | Automatic rollback inside a failed update | `update.rs:330-340` | T4 | exchange-back with union trust state (`20` RB-1) | R-RB |
| I-07 | `gov update --rollback` | `update.rs:348-420` | T4 | restore pipeline, `downgrade` trust gate (`20` §2, §4) | R-RB |
| I-08 | `gov kernel reinstall [--source P]` | `cli/src/main.rs:853` | T5 | authenticate to the installed statement digest; restores PPS and occupation | R-RI |
| I-09 | `gov kernel override --reason` | `kernel_trust.rs:320-347` | T2 | `override_kernel_integrity` trust gate (local terminal only); never changes authenticity, eligibility or policy root | R-OV |
| I-10 | `gov recover` | `recovery.rs:9-147` | T2/T4 | CIT and adoption recovery through GovernedFs; install-journal recovery only for VTS-registered transactions (`20` §5) | R-REC |
| I-11 | Embedded payload | `kernel.rs:31-80` | T0 | in-memory EmbeddedSnapshot named by the TBM | R-EMB |
| I-12 | Fail-closed baseline | `kernel_trust.rs:191-238` | T0 | EmbeddedSnapshot ⊔ floors | R-EMB |
| I-13 | `GOV_CANONICAL_ROOT` | `kernel.rs:83-112` | T5 | source selection only | R-ENV |
| I-14 | `GOV_KERNEL_SOURCE` | `adopt.rs:80` | T5 | removed | R-ENV |
| I-15 | Git delivery (pull, merge, checkout, clone) | none | T4 | evaluated at use: authenticity, integrity, E7, eligibility, floors, trust state, freshness (`24` §4.3), installation state including occupation | R-USE |
| I-16 | In-place edit or race on installed files | none | T4 | per-unit-of-work snapshot generation (VU-11) | R-USE |
| I-17 | Use-time readers of kernel content | `context/mod.rs:93-97`, `tools.rs`, `skills.rs`, `adapters.rs`, `orchestration/*`, `verification/mod.rs`, `project.rs:120-139` | T4 | KernelSnapshot API only; GovernedFs read guard | R-USE |
| I-18 | Migration loading and execution | `update.rs`, `kernel.rs:226-232`, `migrations/framework.rs` | T5 | ARO blobs only; unique chain; operations only on migration-writable Overlay Surface targets (`23` §11.3), otherwise `MIGRATION_OPERATION_NOT_PERMITTED` before any write; computed weakening over the recorded vector → `weakening` trust gate | R-MIG |
| I-19 | `gov release build` (producer) | `release.rs:62-228` | T4 | unsigned candidate naming a TPS; the surface checker must exit 0 (`23` §6.1); private-key scan | R-REL, R-SURF |
| I-20 | `gov release verify DIR` | `release.rs:230-256` | T5 | `authenticate` in report mode | R-REL |
| I-21 | Certification publication | manual | T5 | attestation → certification → TSS reference | R-CERT |
| I-22 | Binary build and distribution | `build.rs:40-117` | TCB | TBM v2 with `binary.source`; reproducible build from the attested source; custodial stages; build attestation; `release-artifact` ×2; TSS reference (`25`) | R-EMB, R-ART |
| I-23 | Remote release fetch (future) | none | T5 | transport only | R-NET |
| I-24 | Release bundle archives (future) | none | T5 | streamed into buffers | R-BUN |

## 2. Adjacent ingress

| ID | Route | 4.1.5 code | Revision 3 control | Req |
|---|---|---|---|---|
| I-25 | Plugin descriptors and registration | `capabilities/{host,registry,governance}.rs` | authority floor and permission classes from the effective policy (floor-joined); descriptors under `governance/overlay/plugins` | R-PLG |
| I-26 | `gov tools install` | `tools.rs` | kernel tool descriptors are content-registered (`TOOLS_REGISTRY` members pinned); project descriptors under TOOL_POLICY floors; subprocess installs are I-46 | R-TOOL |
| I-27 | `gov memory select` pins | `memory/benchmark.rs` | binds profile statement digest | R-PRF |
| I-28 | Reference retrieval profile install | none | signed profile; host verification; transaction (`10`) | R-PRF |
| I-29 | Upstream lessons | `upstream.rs` | development input; GovernedFs | — |
| I-30 | Pre-install adoption policy | `adopt.rs:74-95, 280-292` | EmbeddedSnapshot ⊔ floor | R-ADOPT |
| I-31 | Generated views | `adapters.rs`, `tools.rs`, `memory/indexer.rs` | from the snapshot; CI and policy digest (VU-8) | R-USE |
| I-32 | Schemas validating trust statements and locks | none | compiled | R-AUTH |
| I-33 | Manual lock edits | `project.rs:113-119` | record cross-check; hints are warnings | R-LOCK |

## 3. Ingress added in revision 2 (controls as in revision 3)

| ID | Route | Revision 3 control | Req |
|---|---|---|---|
| I-34 | Adoption batch rollback and recovery | batch 0 = uninstall; batches ≥ 1 from `.governance-runtime/adoption/`; GovernedFs refuses PPS and occupation | R-ADOPT, R-FS |
| I-35 | CIT file operations and CIT snapshot restore | planning refuses PPS (including occupation); GovernedFs | R-FS |
| I-36 | Adoption A7/A11 kernel checks | snapshot verdict | R-ADOPT |
| I-37 | Adapter freshness | CI and policy digest; VTS rendering record (`18` §12) | R-USE, R-AGENT |
| I-38 | Partial install states | installation state machine including `LEGACY` and `PARTIAL(occupation)` | R-PART |
| I-39 | Trust metadata refresh and VTS | account database; union; monotonic | R-TS |
| I-40 | Pre-RoT binaries opening RoT-1 projects | legacy-path occupation (`26`); LP-1 | R-FMT |
| I-41 | Install journal and `trust-tx/<TX>/*.prev` | VTS open-transaction registry; foreign artefacts ignored | R-REC |
| I-42 | Trust Policy acceptance | `trust-policy` at root threshold; `prior_policies`; computed lowering; `policy_lowering` trust gate | R-TS, R-SURF |
| I-43 | Trust State, certification, attestation, revocation acceptance | resolution, equivocation, admissibility, MS-2 | R-TS, R-CERT |
| I-44 | Lineage confirmation and root pins | human command or pin (account database) | R-BOOT |
| I-45 | `gov`-run git subprocess mutations | GovernedFs argument pre-validation | R-FS |
| I-46 | Subprocesses `gov` starts (plugins, tool commands, product and test commands, hooks) | run under write confinement (`24` §3.5 (3)); cannot write pins, the VTS, `governance/trust/**`, occupation entries or the transaction area; refused where confinement is unavailable; other writes detected by the next unit of work (PPS) and the strength vector; records never authorise (`27`) | R-USE, R-CONF |
| I-47 | Candidate → final promotion | `gov release promote`; V8 tree and source equality at every verifier | R-REL |

## 4. Ingress added in revision 3

| ID | Route | What it could do without a control | Revision 3 control | Req |
|---|---|---|---|---|
| **I-48** | `gov trust confirm-state <fingerprint>` | anchor an attacker-chosen epoch | typed from an independent channel; satisfied only by inclusion; an unheld statement gives `BELOW_ANCHOR`; a currency proof only within `c3_currency_window_hours` (`24` §3.2, §3.4) | R-ANCH |
| **I-49** | State pins (`trust-state-pins`) | anchor from a repository-controlled or stale file | system pin directory, or the account location under the integrity predicate; mandatory `valid_until` ≤ `pin_max_validity_days`; recomputed per process; inclusion satisfaction; TA-9 restated (`24` §3.2, §3.5) | R-ANCH |
| **I-50** | Freshness witness (OP-7 c) | replay old state as current; mint currency with one key | separate `freshness-witness` purpose (KS-11); names the effective TSS; C3 needs ≥ 2 keys; validity bound; highest `issued_at`; witness-only clock high-water (`24` §3.3, §8) | R-ANCH |
| **I-51** | Trust-gate confirmation (`gov trust confirm <gate>`) | authorise a trust decision from an agent or repository | local terminal challenge with typed digest prefix and, for C3 kinds, typed state fingerprint; VTS record bound to kind, project and digests; never `gov decide` (`27`) | R-GATE |
| **I-52** | Operator decision pins (`approved-trust-decisions`) | pre-authorise arbitrary transitions | system pin directory or the account location under the integrity predicate; digest-bound; mandatory `expires_at`; `approved_under_state` in the effective chain; currency proof for C3 kinds; `local_terminal_only[]` kinds excluded (`27` §3.2) | R-GATE |
| **I-53** | Constitutional Surface registration (`gov trust draft-policy` → TPS) | register weaker constitutional content | root threshold; change list reviewed; lint; exact precedence registration, presence, Overlay Surface, owner-domain slots; computed reductions in both directions declared and trust-gated (`23` §6–§7, `19` §10.6) | R-SURF |
| **I-54** | `gov trust verify-artifact` and binary replacement | accept a malicious or older binary | A1–A10 with attested source (A4a, A4b), accepted-TBM high-water (A7) and currency proof (A9) (`25` §5) | R-ART |
| **I-55** | Build attestations | self-attested reproduction | `build-attestation` purpose, KS-10, independent custody | R-ART |
| **I-56** | Legacy runtime residue (`.governance-runtime/update/*`, `migration/*`) | legacy rollback source | quarantine; occupation of `.governance-runtime/migration` (tracked, and re-included by the ignore rule so untracking idioms keep it) | R-FMT |
| **I-57** | Occupation entries delivered or removed via Git | remove the legacy barrier | PPS; `PARTIAL(occupation)` | R-PART, R-FMT |
| **I-58** | Long-lived processes (MCP server, scheduler) | enforce a superseded snapshot | VU-11 per request or job step | R-USE |
| **I-59** | Agent reads of adapter bodies and kernel files | follow A2-rewritten instructions | pointers; `gov kernel show`; VTS rendering record | R-AGENT |
| **I-60** | Lock and VTS-record hints | refuse or relax | warnings only (`17` S8) | R-LOCK |

## 4b. Ingress added in revision 4

| ID | Route | What it could do without a control | Revision 4 control | Req |
|---|---|---|---|---|
| **I-61** | System pin directory (`/etc/gov/`, `/Library/Application Support/gov/`, `%ProgramData%\gov\`) and account pin files | anchor or approve from a location the governed account can write | OS-resolved location; integrity predicate; recomputed per process (`24` §3.5) | R-ANCH-6 |
| **I-62** | In-gate state confirmation (typed fingerprint in `gov trust confirm`) | fabricate currency | typed from an independent channel; must name the effective TSS; recorded as a human anchor (`24` §3.2, `27` §3.1) | R-GATE-3 |
| **I-63** | Repository- and plugin-supplied commands executed by `gov` | write pins, the VTS or trust paths before a trust decision (RV3-B-A03) | `confine::spawn`; trust decisions precede children; refusal without confinement (`24` §3.5) | R-CONF-1…3 |
| **I-64** | Overlay migration operations (`set_overlay_key`, `set_overlay_rule`, `rename_overlay_key`, `add_from_template`) | widen tool permissions, exceptions, identifiers or contract; write any overlay file (RV3-B-A18) | Overlay Surface whitelist per operation and target; computed weakening over the recorded vector (`23` §11.3, `19` §9) | R-MIG-5, R-MIG-7 |
| **I-65** | Owner constitutional files outside the kernel (`23` §7.2) | an absent or replaced constitution treated as present | owner-domain slots; `owner_constitutional_file` confirmation; fail-closed absence; strength vector | R-SURF-12 |
| **I-66** | Verification attestation v2 (`source`, `lifts_negative_statement_digest`) | choose a binary's source; lift a negative with an old attestation | V8, A4b; custodial stages; MS-2 (`25` §5.1, `17` §2) | R-ART-5, R-CERT-4 |
| **I-67** | Trust Policy `bootstrap` parameters and `clock_reset`; `eligibility.production_sources` | widen currency windows, reset the clock, register a source | root threshold; computed reductions (CR-10) with a per-project gate | R-TS-6 |
| **I-68** | Local clock | make pins or windows valid again; poison the high-water | (restated in revision 6) every ingested non-future statement raises `clock_high_water`; SV-11 refuses future statements at ingest, and a refused future statement makes clock-based proofs unusable for that unit of work; a clock below the high-water makes clock-based proofs unusable (`24` §8) | R-TS-10, R-TS-11 |

## 4c. Ingress added in revision 6

| ID | Route | What it could do without a control | Revision 6 control | Req |
|---|---|---|---|---|
| **I-75** | First-contact code and first-contact manifest (typed codes; manifest from any carrier) | select the lineage, the Trust State, the source quorum or the evaluator at first admission (RV5-H1) | FC-1…FC-3 before any evaluator; FC-4…FC-8 in `gov-admit`; the stated first-contact root (`32`) | R-ADM-2′, R-ADM-3′ |
| **I-76** | Environment manifests and `environment-reproduction` statements | select the build environment of every reproducer (RV5-H2) | R-BENV-1…R-BENV-6 (`33`) | IR-REP-5 |
| **I-77** | `registration-revocation` statements | remove a restrictor | registration threshold only; AP-5r (`30` R-REG-11) | R-REG-11 |
| **I-78** | Registration content proposed by CI | select constitutional content (RV5-H3) | a proposal only; custodians derive it first-hand (`34` R-CON-1); `verify-registration` | R-CON-1 |
| **I-79** | `.git/info/attributes`, user `core.excludesFile`, `.git/info/exclude` | convert kernel line endings; untrack the migration occupation (RV5-M6, RV5-M7) | `governance/trust/.gitattributes` member; stated conditions fail closed with doctor naming the source (`26` §2, §8) | R-ST5-1 |

## 5. Protected Path Set and file-mutation inventory

**Protected Path Set** (`18` §8):
- `governance/trust/**`;
- occupation entries: `governance/kernel`, `governance/project`, `governance/generated`, `governance/framework.lock` (and
  its sentinel), `spec/audits/GOVERNANCE-ADOPTION`, `.governance-runtime/migration`;
- the directory entries `governance`, `governance/trust`;
- the transaction area `.governance-runtime/trust-tx/**` (install_tx only; journals are hints).

| # | Mechanism | 4.1.5 location | May touch PPS? | Treatment |
|---|---|---|---|---|
| 1 | Install transaction (init, adopt batch 0, update, rollback, reinstall, recovery, uninstall, trust refresh, profile install, layout migration) | `kernel.rs`, `lock.rs`, `update.rs`, `init.rs`, `adopt.rs` | **yes, only with `InstallTxToken`** | `18` §5 (union trust record) |
| 2 | CIT `write_file`/`move_file`/`delete_file`/`append_record` and snapshot restore | `cit/mod.rs:586-660, 700-745, 1124-1185` | no | planning refusal + GovernedFs |
| 3 | Adoption executor moves, deletions, `git mv`/`git rm`, batch rollback | `migrations/executor.rs` | no | planner classification + GovernedFs |
| 4 | Migration overlay operations; template reconciliation | `migrations/framework.rs` | no | GovernedFs; weakening trust gate |
| 5 | `init` roots, `.gitignore`, overlay | `init.rs:43-215` | no (overlay at `governance/overlay`) | GovernedFs |
| 6 | Gate, decision, report records | `records.rs`, `orchestration/gates.rs` | no | GovernedFs; never authorise trust decisions (`27`) |
| 7 | Ledger, checkpoints, claims, telemetry | `update.rs`, `checkpoints.rs`, `claims.rs`, `observability.rs` | no | GovernedFs |
| 8 | Indexer DB and manifests | `memory/indexer.rs` | no | GovernedFs; CI and policy digest |
| 9 | Adapter and registry generation | `adapters.rs`, `tools.rs`, `capabilities/registry.rs` | no | GovernedFs; VTS rendering record |
| 10 | Tool installer file writes | `tools.rs` | no | GovernedFs |
| 11 | Upstream packaging, lesson clustering | `upstream.rs`, `lessons.rs` | no | GovernedFs |
| 12 | **Plugins** (subprocess, cwd = project root) | `capabilities/host.rs:175-190` | outside GovernedFs, **confined** | Confined children (`24` §3.5): no writes to pins, the VTS, PPS or the transaction area. Other writes are A3-equivalent. Records: never authorise trust. Overlay: strength vector. |
| 13 | **Tool install and uninstall commands**; product test commands | `tools.rs:458-464, 503`; `verification/` | outside GovernedFs, **confined** | as row 12; kernel tool commands are content-registered |
| 14 | Git operations by users and agents | none | outside | evaluated at use; journals in Git are foreign |
| 15 | External editors and processes | — | outside | A2/A3 model |
| 16 | **Pre-RoT binaries 4.1.2–4.1.5** | legacy binaries | cannot (P3r3: 0 of 695 invocations, 0 of 40 chains) | `26` |
| 17 | VTS, pins, confirmations | `gov`, operator, A3 | n/a | pins: system pin directory, or the account location under the integrity predicate; VTS: account database; confined children cannot write either; RS-3 |
| 18 | Release build output | `release.rs` | canonical repository only | producer rules; LR-3 |

## 6. Completeness rules (enforced by tests)

1. Only `install_tx` holds `InstallTxToken`. Its entry points accept an `AuthenticatedRelease` (or an authenticated
   restore target) and an `Authorisation` that carries a consumed trust-gate confirmation. They never accept a path.
2. Only `kernel_trust` and `install_tx` open `governance/trust/**`.
3. No code path reads a release `manifest.*`, a source `KERNEL_MANIFEST.json`, an occupation entry's content, a repository
   gate record's `answer`, or lock hints to make a decision.
4. Every CLI subcommand is in a compiled command register with its operation class (C0–C3, `24` §4.2). The conformance
   suite runs every command:
   - the builder uses an interception layer;
   - the independent verifier uses OS-level tracing (`strace`, fanotify or eBPF).

   Both assert no PPS mutation outside `install_tx` and no open of trust paths outside the two modules. The inputs include
   protected-path CIT manifests, adoption plans, `../` spellings, case variants and symlinked parents.
5. Every consumed policy key is in the consumer register; security decision points read only `floor`, `pinned`,
   `members` or `precedence` leaves (`23` §6.5).
6. A new `GOV_*` variable selecting kernel material, trust metadata, a trust-store location, an anchor or a decision fails
   the architecture test.
7. Every ingress in this map names at least one scenario in `12`; `22` checks this.
8. Every spawn of a repository- or plugin-supplied command goes through `confine::spawn` (R-CONF-1). The architecture test
   fails on any other spawn of such a command.
