# Output 2 — Privileged-ingress map

> **RoT-1 revision 3 — PROPOSED, pending a fresh independent review; not approved, not implemented.**
> Revision 3 updates paths for the legacy-path-occupation layout (`26`) and adds ingress I-48…I-60. The new routes are
> anchors, pins, trust-gate confirmations, surface registration, binary acceptance, build attestations, legacy residue,
> occupation entries, long-lived requests and adapter consumption. The mutation inventory gains plugins and tool
> subprocesses as writers of records and the overlay (R2-M1). Completeness is proven by OS-level tracing over the full
> command register.

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
| I-18 | Migration loading and execution | `update.rs`, `kernel.rs:226-232`, `migrations/framework.rs` | T5 | ARO blobs only; unique chain; no lock operation; `weakening` trust gate | R-MIG |
| I-19 | `gov release build` (producer) | `release.rs:62-228` | T4 | unsigned candidate naming a TPS; the surface checker must exit 0 (`23` §6.1); private-key scan | R-REL, R-SURF |
| I-20 | `gov release verify DIR` | `release.rs:230-256` | T5 | `authenticate` in report mode | R-REL |
| I-21 | Certification publication | manual | T5 | attestation → certification → TSS reference | R-CERT |
| I-22 | Binary build and distribution | `build.rs:40-117` | TCB | TBM compiled; reproducible build; build attestation; `release-artifact` ×2; TSS reference (`25`) | R-EMB, R-ART |
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
| I-46 | Non-`gov` subprocesses (plugins, tools, test commands) | A3-equivalent; detected by the next unit of work (PPS), strength vector (overlay); records never authorise (`27`) | R-USE |
| I-47 | Candidate → final promotion | `gov release promote` | R-REL |

## 4. Ingress added in revision 3

| ID | Route | What it could do without a control | Revision 3 control | Req |
|---|---|---|---|---|
| **I-48** | `gov trust confirm-state <fingerprint>` | anchor an attacker-chosen epoch | the fingerprint is typed from an independent channel; unheld epochs make the machine `BELOW_ANCHOR`; monotonic (`24` §3) | R-ANCH |
| **I-49** | State pins (`trust-state-pins`) | anchor from a repository-controlled file | account-database location only; TA-9; digest-bound (`EQUIVOCATION` on mismatch) | R-ANCH |
| **I-50** | Witness TSS (OP-7 c) | replay old state as fresh | expiry, highest witness `issued_at`, clock rollback detection | R-ANCH |
| **I-51** | Trust-gate confirmation (`gov trust confirm <gate>`) | authorise a trust decision from an agent or repository | local terminal challenge; VTS record bound to kind, project and digests; never `gov decide` (`27`) | R-GATE |
| **I-52** | Operator decision pins (`approved-trust-decisions`) | pre-authorise arbitrary transitions | account database; digest-bound; `local_terminal_only[]` kinds excluded | R-GATE |
| **I-53** | Constitutional Surface registration (`gov trust draft-policy` → TPS) | register weaker constitutional content | root threshold; change list reviewed; lint; computed reductions declared and trust-gated (`23` §6–§7) | R-SURF |
| **I-54** | `gov trust verify-artifact` and binary replacement | accept a malicious or older binary | A1–A10 (`25` §5) | R-ART |
| **I-55** | Build attestations | self-attested reproduction | `build-attestation` purpose, KS-10, independent custody | R-ART |
| **I-56** | Legacy runtime residue (`.governance-runtime/update/*`, `migration/*`) | legacy rollback source | quarantine; occupation of `.governance-runtime/migration` (tracked) | R-FMT |
| **I-57** | Occupation entries delivered or removed via Git | remove the legacy barrier | PPS; `PARTIAL(occupation)` | R-PART, R-FMT |
| **I-58** | Long-lived processes (MCP server, scheduler) | enforce a superseded snapshot | VU-11 per request or job step | R-USE |
| **I-59** | Agent reads of adapter bodies and kernel files | follow A2-rewritten instructions | pointers; `gov kernel show`; VTS rendering record | R-AGENT |
| **I-60** | Lock and VTS-record hints | refuse or relax | warnings only (`17` S8) | R-LOCK |

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
| 12 | **Plugins** (subprocess, cwd = project root, no sandbox) | `capabilities/host.rs:175-190` | outside GovernedFs | A3-equivalent. PPS changes: detected by the next unit of work. Records: never authorise trust. Overlay: strength vector. VTS: RS-3. |
| 13 | **Tool install and uninstall commands**; product test commands | `tools.rs:458-464, 503`; `verification/` | outside GovernedFs | as row 12; kernel tool commands are content-registered |
| 14 | Git operations by users and agents | none | outside | evaluated at use; journals in Git are foreign |
| 15 | External editors and processes | — | outside | A2/A3 model |
| 16 | **Pre-RoT binaries 4.1.2–4.1.5** | legacy binaries | cannot (P3r3: 0 of 695 invocations, 0 of 40 chains) | `26` |
| 17 | VTS, pins, confirmations | `gov`, operator, A3 | n/a | account database; RS-3 |
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
