# AR-0026 — R1 implementation of the Signed Release Root (`ARCH-0003`)

| Field | Value |
|---|---|
| Run | `AR-0026`, role `builder` |
| Handoff | `release/orchestration/phase-1/HANDOFFS/HO-0026-r1-signed-release-root-builder.md` |
| Base commit | `1e31f6b5cb4e112d4ec86b45839e093c7b50d687` |
| Branch | `phase1/srr1-r1-build` |
| Active gate | `GATE-BUILDER-READY` |
| Verdict | `READY_FOR_INDEPENDENT_OS_VERIFICATION` |
| Not claimed | any acceptance token. R1 acceptance is issued only by the designated fresh independent verifier. |

## 0. Digest verification

Every normative source named in the handoff was digest-verified before use; all matched. See
`REVIEWED-CONTENT-DIGESTS.txt`. The handoff quotes `ARCH-0003`'s **accepted body** digest
`42681978…`; that is the digest of the whole `spec/architecture/ARCH-0003.yaml` file at the acceptance
candidate commit `2b36b44`. At `HEAD` the file differs only by the post-verdict `r0_acceptance:` governance
annotation; the `body:` scalar is byte-identical at both commits (`093cb78e…`). No mismatch, no STOP condition.

The handoff records base commit `7858b6d`; the orchestrator dispatched this run at its descendant
`1e31f6b` (which added the `AR-0025` acceptance record). Work started from `1e31f6b`, as instructed.

## 1. The cryptographic dependency, and why

**`ed25519-dalek` 2.2.0** (pinned in `Cargo.toml` and `Cargo.lock`), with `curve25519-dalek` 4.1.3 and `hex` 0.4.3.

* It is the mature, widely reviewed Rust Ed25519 implementation (dalek-cryptography / RustCrypto ecosystem) and is
  the crate `HO-0026` itself names as an example.
* `runtime/src/srr/crypto.rs` is a thin adapter: no curve arithmetic, point decompression, cofactor handling or
  malleability check is written here. All of it is delegated.
* Verification uses `verify_strict`, which rejects small-order keys and non-canonical encodings, so a signature
  cannot be made to verify under more than one identity — the right choice where signatures are also identities.
* A TUF **client** crate (e.g. `tough`) was considered and not used: the release role must bind product/repository
  identity, channel, monotonic sequence, kernel/CLI payload digests, schema and migration identities and the
  minimum secure release. Expressing that through a fixed client's custom-metadata escape hatch would have hidden
  the bindings this gate is about. The TUF **role model** is implemented directly and explicitly instead
  (`runtime/src/srr/metadata.rs`), which is what `ARCH-0003` §4 asks for ("a mature TUF-style metadata model and
  reviewed cryptographic library").

### Metadata parsing is not hand-rolled, and there is no canonicalisation step

Signatures cover **the exact bytes of the `signed` member as they appear in the file**, extracted with
`serde_json::value::RawValue` (a first-class serde_json facility; `raw_value` feature enabled). There is therefore
no canonical-JSON encoder for a producer and a consumer to disagree about, and no way to verify one byte-string
and then act on a different parse: the policy is parsed from the same `RawValue` that was verified. A test
(`modified_metadata_payload_and_migration_all_fail_closed`, case b) presents a signature made over a *different*
document and confirms it is refused.

### `gov` verifies; `gov` never signs

There is no signing entry point and no key material anywhere in `runtime/` or `cli/` outside `#[cfg(test)]`.
Fixture metadata is produced by `tests/certification/srr_material.rs`, which is compiled only into the test binary.
Its keys derive from published constant seeds, so their private halves are public by construction and unusable as
a production root. **No private key exists in this repository**, and no production signing or key-custody ceremony
was performed — those are R2 (`GATE-OWNER-KEY-CEREMONY`).

## 2. No-bypass, enforced by the type system

`kernel::install_kernel` no longer accepts a path. Its signature is:

```rust
pub fn install_kernel(auth: &crate::srr::AuthenticatedRelease, governance_dir: &Path) -> Result<Value>
```

`AuthenticatedRelease` is constructible **only** by `srr::verifier::admit`, and `auth.verified_payload()` is the
private staging copy that was measured. An ingress therefore cannot install from a raw source directory even by
mistake: "every privileged ingress calls the common verifier" is a compile-time property, not a convention.

Every privileged ingress and where it calls the verifier:

| Ingress | Call site | `Ingress` value |
|---|---|---|
| `init` | `runtime/src/init.rs` (`init`) | `Ingress::Init` |
| `adopt` | `runtime/src/adopt.rs` (`a6_migrate`, batch 0) | `Ingress::Adopt` |
| `update` | `runtime/src/update.rs` (`apply_update_opts`) | `Ingress::Update` |
| `reinstall` | `cli/src/main.rs` (`KernelCmd::Reinstall`) | `Ingress::Reinstall` |
| `rollback` | `runtime/src/update.rs` (`rollback_internal`, operator path) | `Ingress::Rollback` |
| `recovery` | `runtime/src/recovery.rs` (`recover`) + the reinstall/rollback restore paths | `Ingress::Recovery` |

The one path that does **not** cross the ingress boundary is the *transaction abort* inside `apply_update_opts`:
when an update fails after installing, the previous tree is restored. That is not a backward ingress, because the
floors were never advanced (step 9 of the ordering below is unreached), so the restored state is exactly the state
the floors already describe. It is marked `transaction_abort` in the code and cannot be reached from the CLI.

## 3. What was built

`runtime/src/srr/`:

| Module | Responsibility |
|---|---|
| `crypto.rs` | thin adapter over `ed25519-dalek`; verification only |
| `metadata.rs` | root / release / snapshot / timestamp / break-glass roles, threshold verification, root succession |
| `state.rs` | protected machine state: floors, installed record, journal, staging, break-glass inbox; durable writes |
| `staging.rs` | private staging, verified-byte binding, atomic crash-safe commit, journal replay |
| `verifier.rs` | **the one verification policy**; the typed `AuthenticatedRelease`; the floor check |
| `breakglass.rs` | `OWNER-DECISION-0006` in full, including the single `SRR2-R1-C1` exit policy point |
| `plugins.rs` | `SRR-R0-L6` acquisition classes and delegated signed targets |
| `provision.rs` | administrator trust-anchor provisioning and root succession |

Plus `runtime/src/contracts.rs` (Contract v3 hash-bound scaffolding) and a new `gov trust` / `gov contract`
command surface.

## 4. Protected state, floors and durability ordering

Protected machine state lives **outside every repository**, under `$XDG_STATE_HOME/governance-os/machine` (or
`$HOME/.local/state/…`). Nothing governed by a project can write it.

Three separately durable floors:

* `metadata_high_water` — highest accepted version per metadata role. Replay protection.
* `release_high_water` — highest release this machine **verified and installed**, in both a signed-sequence basis
  and a semantic-version basis.
* `minimum_secure` — the signed minimum secure release, monotonic, never lowered.

The effective release floor is the higher of the last two, and it is checked inside the one verifier, so it binds
**every** ingress rather than only `rollback` (`ARCH-0003` §7, `OWNER-DECISION-0006` §9).

### `SRR-R0-L5` — durability ordering relative to atomic commit

```text
 (1) journal intent                 fsync BEFORE anything moves
 (2) build <dest>.srr-new from the staged, measured bytes
 (3) journal phase=swap             fsync BEFORE the first rename
 (4) rename dest -> dest.srr-old    atomic
 (5) rename dest.srr-new -> dest    atomic; fsync(parent)
 (6) journal phase=committed        fsync
 (7) verify the committed bytes against the verified measurement
 (8) remove dest.srr-old
 (9) ADVANCE THE FLOORS             fsync — only now
(10) journal phase=done
```

(9) is deliberately after (5)–(7). Advancing first and then crashing would leave the machine on the *old* release
with its own protected floor naming the new one — a machine below its own floor, i.e. self-inflicted bricking that
only break-glass could clear. Advancing afterwards fails the safe way. Journal replay never advances a floor,
because a crashed transaction never proved its post-commit verification.

### A deliberate scoping decision, stated plainly

The floors enforced are the ones established from **verified** facts. `ARCH-0003` §7 says clients persist "the
**highest valid** root/metadata versions and minimum secure release they have observed"; a machine with no trust
anchor has validated nothing. So `Floors::raise_release` advances **only** for `Authenticity::Authentic`, and a
machine that has never verified a signed release has no release floor to enforce. Recording an unauthenticated
observation as a protected floor would manufacture a security claim out of nothing *and* would brick rollback on a
machine that has no break-glass authority to unbrick it (break-glass is anchored in the root's `recovery` role).
`gov trust status`, `gov status` and the verifier notes all say plainly when no floor is in force.

This is an `IMPLEMENTATION-CHOICE`, and the residual is stated in §8 below.

## 5. `OWNER-DECISION-0006` — all ten requirements

| # | Requirement | Implementation | Test |
|---|---|---|---|
| 1 | recovery release must still be authentic | `verifier.rs` refuses break-glass for any non-authenticated candidate (`SRR_BREAK_GLASS_REQUIRES_AUTHENTIC_RELEASE`); the floor check is the only thing relaxed | `break_glass_never_admits_an_inauthentic_release_and_needs_no_network` |
| 2 | owner-controlled, non-manufacturable authority | `breakglass::authorise` — an owner-signed `recovery`-role token, machine-bound, nonce-bound, in protected state outside every repository; `state::refuse_authority_env` refuses authority-bearing env vars; `--break-glass` only *requests* | `the_floor_binds_every_ingress_…` (flag alone refused), `break_glass_never_admits_…` (impostor key, wrong machine), `environment_repository_and_caller_inputs_cannot_create_trust_or_approval` |
| 3 | durable entry record | `breakglass::enter` writes machine identity, both floors at entry, the recovery release identity and digests, the reason and timestamps, fsync'd before the nonce is spent | `the_floor_binds_every_ingress_…` |
| 4 | exact marking `DEGRADED — RECOVERY ONLY` | `breakglass::DEGRADED_TOKEN`, pinned byte-for-byte against U+2014 in a unit test | `degraded_marking_is_byte_exact_with_an_em_dash`; the certification test compares the emitted bytes |
| 5 | permitted activities | `PERMITTED_ACTIVITIES`; `guard_light` refuses only what §6 lists, so inspection, backup/export, diagnosis, repair, uninstall/reinstall and restoration keep working | `the_floor_binds_every_ingress_…` (status, doctor, recover, reinstall all succeed while marked) |
| 6 | refused activities | `REFUSED_ACTIVITIES` + `guard_light`, wired into `orchestration::control::guard_write` — the same chokepoint `FREEZE_WRITES` uses, with 29 call sites | `the_floor_binds_every_ingress_…` (`task create`, `gate create` refused) |
| 7 | exit condition | `breakglass::exit_satisfied` — the single `SRR2-R1-C1` policy point; called from exactly one place | `the_floor_binds_every_ingress_…` (marking cleared on restore) |
| 8 | the floor is never lowered | `enter` writes no floor file at all; `Floors::raise_*` are monotonic-only | `the_floor_binds_every_ingress_…` asserts both floors unchanged after entry |
| 9 | ingress consistency | the floor check lives in the one verifier every ingress calls | `the_floor_binds_every_ingress_…` (refusal at `reinstall`, not only `rollback`), `protected_floors_survive_uninstall_and_project_removal` (refusal at `init`) |
| 10 | works with no network | every check reads local files only: the protected inbox, the trusted root, the local clock. No network or code-hosting call exists on the path | `break_glass_never_admits_an_inauthentic_release_and_needs_no_network`; `gov trust break-glass` reports `network_required: false` |

## 6. R1 conditions

| Condition | Status | Where |
|---|---|---|
| `SRR2-R1-C1` | **CLOSED** — stricter reading (b) implemented as ONE isolated policy point, `breakglass::exit_satisfied`, commented with `SRR2-R1-C1` and `GATE-OWNER-R1-BREAK-GLASS-EXIT`, with the exact two-line change the owner needs to adopt (a). `EXIT_POLICY = "b_stricter_both_floors"` is the single flag. Nothing else in the codebase compares a release against an exit floor. | `runtime/src/srr/breakglass.rs` |
| `SRR2-R1-C2` | **CLOSED** — the protected offline-recovery record and the break-glass token both bind `payload_hash` / `kernel_manifest_hash`, not the release version. A token that binds only a version is rejected at parse time. | `state::InstalledRecord::vouches_for`, `metadata::BreakGlassToken::parse`, `breakglass::enter` |
| `SRR2-R1-C3` | **CLOSED** — floors live outside every repository and are proven to survive `governance/` deletion and whole-project deletion, and to still be enforced afterwards. | `protected_floors_survive_uninstall_and_project_removal` |
| `SRR-R0-L1` | **CLOSED** — root succession stated concretely, not by reference: same product; version exactly *n+1* (no gaps, no replay); threshold of the **outgoing** root's `root` role; threshold of the **incoming** root's own `root` role; not expired; keys absent from the successor revoked by omission. | `metadata::accept_root_succession`, `root_succession_requires_both_quorums_no_gaps_and_revokes_by_omission` |
| `SRR-R0-L2` | **CLOSED** — `channel` is a bound field of release metadata and a mismatch fails closed; delegations may additionally bind a channel. | `metadata::Release`, `wrong_key_wrong_product_and_wrong_channel_all_fail_closed` |
| `SRR-R0-L3` | **CLOSED** — `verifier::is_trust_changing` scopes "repository gate records are requests" to trust-changing operations only. Ordinary Human Gates keep the authority D-0007 T2 and Contract v3 L2 give them; no existing gate behaviour changed (the whole pre-existing suite still passes, including `update_approval_requires_presented_answered_gate` and `cit_approval_derives_only_from_an_answered_gate`). | `runtime/src/srr/verifier.rs` |
| `SRR-R0-L4` | **CLOSED (kept vacuous)** — no dev/test trust mode exists. There is no flag, env var or build feature that relaxes verification; `gov` has no signing path at all; the only postures are *provisioned* (full verification) and *unprovisioned* (authenticity reported as `UNKNOWN`, asserting nothing). Provisioning is a durable latch that is never cleared, so a provisioned machine cannot be walked back to the unprovisioned posture. | `verifier::Posture`, `state::MachineState::is_provisioned` |
| `SRR-R0-L5` | **CLOSED** — ordering fixed and documented above; replay never advances a floor. | `runtime/src/srr/staging.rs`, `an_interrupted_install_leaves_one_complete_version_and_never_advances_a_floor` |
| `SRR-R0-L6` | **CLOSED** — three acquisition classes derived from **where the bytes are**, never from what the descriptor claims. Built-in bytes are covered by the release payload digests; local-project bytes keep the existing kernel-owned controls; a **privileged remotely acquired** capability requires a delegated signed target in verified release metadata and is refused without one. | `runtime/src/srr/plugins.rs`, wired into `capabilities::governance::register`; `a_privileged_capability_acquired_from_outside_needs_a_delegated_signed_target` |
| `SRR-R0-L7` | **OUT OF SCOPE, not built** — owner-closed. No offline/air-gapped first-install ceremony exists. Break-glass *recovery* is fully offline regardless. | — |

## 7. D-0007 preservation — three predicates, three sources

| Predicate | Means | Established by | Lives in |
|---|---|---|---|
| **intact** | the local copy is unmodified | payload ↔ `KERNEL_MANIFEST.json` ↔ `framework.lock.kernel_manifest_hash` | `runtime/src/kernel_trust.rs` — D-0007, ACTIVE, **unchanged** |
| **authentic** | the bytes are an authorised release | signed metadata chaining to the machine's root anchor, or this machine's own protected record | `srr::verifier::Authenticity` |
| **admissible** | it may be installed now | at or above both protected floors | `AuthenticatedRelease::below_floor` |

`kernel_trust.rs` reads no signed metadata and the `srr` modules read no D-0007 record. The offline-recovery path
explicitly derives authenticity from **this machine's own protected record**, never from the manifest, the lock,
the repository or files delivered with the copy — preserving `OWNER-DIRECTIVE-0004`'s rule that the manifest and
lock are not a first-install authenticity root.
`installed_integrity_authenticity_and_admissibility_stay_three_separate_predicates` tampers the installed payload
and confirms D-0007 still refuses mutating work with `KERNEL_TAMPERED` while the authenticity record is untouched
and does not excuse it.

## 8. Honest limitations and residual risk

1. **Unprovisioned posture.** A machine with no trust anchor makes no authenticity claim and enforces no release
   floor. This preserves the pre-RoT product (every one of the 49 pre-existing certification scenarios still runs
   unmodified) and grants nothing, but a verifier should confirm they agree it is not a disguised trust mode. It
   is reported honestly by `gov trust status`, `gov status` and the verifier's own notes.
2. **State-root relocation.** `GOV_MACHINE_STATE_DIR` is refused once the default root is provisioned. But a
   process running as the owner can still relocate `HOME` / `XDG_STATE_HOME` and so move the *default*. `ARCH-0003`
   §1 places the local OS/administrator boundary inside the trusted domain, so such a process is inside the
   boundary — but this is a real residual and is stated rather than concealed.
3. **Expiry comparison.** Expiry is a lexicographic comparison of RFC-3339 UTC strings at second precision against
   the declared local clock. Correct for the emitted format; a metadata producer using a different offset or
   precision would need a real date parse. Recorded as a hardening item, not a claimed guarantee.
4. **Delegated targets are checked but none are published.** `SRR-R0-L6` refuses undelegated privileged remote
   capabilities. The publisher-side tooling to *issue* a delegated target is not built; today the only ways to ship
   such a capability are inside the release payload or in the governed project. That is a deliberate scope limit,
   not a gap being papered over.
5. **`fsync` on directories is best-effort.** A failure tightens nothing and loosens nothing about the committed
   bytes; it only widens the crash window on filesystems that do not support it.
6. **Nothing is stubbed.** There is no placeholder, no `todo!()`, and no code path that appears to verify but does
   not.

## 9. Regression

`TEST-OUTPUT.txt` holds the full output.

| Suite | Result |
|---|---|
| `cargo test --lib` (runtime unit) | **26 passed, 0 failed** (24 pre-existing + 2 new modules' tests) |
| `cargo test --test certification` | **64 passed, 0 failed** (49 pre-existing, unmodified, all passing + 15 new) |

**No pre-existing test was modified to make it pass.** One change was made to the shared harness
(`tests/certification/common.rs`): each scenario now runs with its own `XDG_STATE_HOME`, so each simulated machine
has its own protected state instead of sharing one — and so the suite does not write to the developer's own machine
state. That is test isolation for a machine-scoped control, not a weakened assertion.

There are **no pre-existing failures** and none were introduced.

## 10. `NEW_OWNER_DECISION_REQUIRED`

None newly raised. The one open owner question, `SRR2-R1-C1` / `GATE-OWNER-R1-BREAK-GLASS-EXIT`, is implemented at
the orchestrator's interim stricter reading (b) and is flippable to (a) at one named policy point.
