# P2-AR-0020 — Repair iteration 1, round 1, WS-8 (part): root of trust and lifecycle ingress

| Field | Value |
|---|---|
| Run | P2-AR-0020, fresh `capability-repair` builder (model `claude-opus-5[1m]`, Opus 5, 1M context) |
| Handoffs | P2-HO-0010 (common protocol), P2-HO-0017 (WS-8 part) |
| Classes | BC-P2-35, BC-P2-36 (presentation and disclosure part only), BC-P2-37, BC-P2-38 |
| Base | `c6b60bc760a0bb42907f74210fd9e644a420851a`, `product_code_digest bd4d65d9…0547` (= `cap2-candidate-0` = `srr1-r1-accepted`) |
| Branch | `phase2/repair-1-ws08` |
| Work commits | `d2f0977` product repair · `39667f8` builder regression tests · `63f82ba` API unit test (final product state) |
| Final `product_code_digest` | `d34fbec033612eb497ee8b4052c6b9b41410433d0715b0f6c4ec02be7aa548e8` (`governed_state_digest` unchanged: `3dabf06a…ad91` — no spec/ or docs/ change, D-0007 text untouched) |
| Release binary | `target/release/gov` sha256 `b3218094…d12f` (base `3271ce0e…be81d`, identical to the alpha-r audit binary) |
| Claims | BC-P2-35 `REPAIRED_CLAIMED` · BC-P2-36 (presentation) `REPAIRED_CLAIMED` (doctor/audit check = integration point IP-1/IP-2, WS-2) · BC-P2-37 `REPAIRED_CLAIMED` · BC-P2-38 `REPAIRED_CLAIMED` (one residual side effect closes with IP-3, WS-3) |
| Verdict | `READY_FOR_INDEPENDENT_CAPABILITY_VERIFICATION` — builder claims only; nothing here is acceptance (Contract v3 O3) |

Every number below is from a run recorded under `evidence/`. Builder tests and builder probes are regression evidence;
acceptance is decided later by fresh independent verifiers with their own held-out tests.

## 0. Design in one paragraph

A new module, `runtime/src/srr/installation.rs`, keeps two records in the machine's protected state (outside every
project, beside the single `installed/<product>.json` the R1 verifier keeps): **per project**, the exact payload this
machine committed into it (per-file digests, written `pending` immediately before the atomic swap and `current`
immediately after its verification, so any tree an interrupted install recovers to is bound), and **per payload
digest**, a *verified-release ledger* of every release this machine authenticated (never written for authenticity
`UNKNOWN`). D-0007 post-install integrity (`kernel_trust`, `kernel::verify_kernel`) consults these records **by digest
only** (ARCH-0003 §2 "Evidence may connect domains by digest"); `kernel_trust.rs` still contains none of `srr::admit`,
`AuthenticatedRelease`, `Authenticity`, `breakglass`, `below_floor`, `Floors`, `AUTHENTIC`, `admissible`. Authenticity
questions — may this installation be presented as current, may the rollback ingress admit these bytes offline — are
answered in the SRR domain from the same records.

## 1. BC-P2-35 — post-install integrity against this machine's protected record

**Requirement** (repair-delta; Contract v3:146; D-0007 rule 1; ARCH-0003 §7, §8; OWNER-DIRECTIVE-0004): installed-kernel
verification detects a mutually consistent payload/`KERNEL_MANIFEST.json`/`framework.lock` rewrite wherever the machine
holds a protected record of what it verified and installed, and treats the kernel as unauthenticated T1 (embedded
baseline substituted, mutations fail closed) until it matches; a machine that holds no protected record for the project
verifies the installed kernel against the pinned authenticated release before privileged work; no change to D-0007's
text; the unprovisioned sub-case follows OD-P2-02.

**What changed**
- `runtime/src/srr/installation.rs` (new): `bind_pending`/`bind_committed`/`clear_pending` (per-project record),
  `record_verified`/`verified_release` (ledger), `anchor_for`/`anchor_posture` (digest-level verdict:
  `MATCHED` / `DIVERGED` / `DIVERGED_NOT_ENFORCED` / `UNRECORDED` / `UNRECORDED_REQUIRED` / `UNDETERMINED`),
  `divergence` (which files differ from what this machine committed).
- `runtime/src/kernel.rs`: `install_kernel_inner` writes the pending/current record around `staging::commit_tree`;
  `verify_kernel` measures the payload digest from the files on disk (`measured_payload_hash`), and folds an
  **enforced** divergence from the protected record into `modified`/`missing`/`added` and `ok` — so the existing
  consumers (doctor D003, audit `mutation_scope`, `update --rollback` `kernel_ok`, adopt checks) see it without edits.
- `runtime/src/kernel_trust.rs`: `compute` requires the anchor to hold; `KERNEL_TAMPERED` names the files; a new typed
  refusal `KERNEL_UNANCHORED` (remediation: `gov kernel reinstall --source <the signed release framework.lock pins>`)
  for a kernel no record of a verification binds on a machine with a trust anchor; the anchor state enters the
  override-gate fingerprint only when it is why the kernel is untrusted; `to_value` carries the protected-record state
  only when it bears on the verdict (agent context packets hash this value; see §5 multi_machine).
- `runtime/src/kernel.rs` `pinned_release_check`: on a provisioned machine, a reinstall of exactly the recorded payload
  while `framework.lock` pins something else is refused `KERNEL_PIN_REWRITTEN` before anything moves, naming the pin
  this machine recorded — the remedy path for a rewrite that also rewrote the lock.
- `runtime/src/srr/state.rs`: `MachineState::read_only` (no state is created by a reader) and `installed_dir`;
  `InstalledRecord::vouches_for` now also requires the record to record a verification.

**Enforcement by posture.** Provisioned machine: `DIVERGED` and `UNRECORDED_REQUIRED` make the kernel untrusted
(embedded baseline, mutations refused). Unprovisioned machine: the per-project record is still written (it records
what was *installed*, authenticity `UNKNOWN`), a divergence is **reported** (`DIVERGED_NOT_ENFORCED` in `gov kernel
trust`, and in the presentation disclosure) and **not enforced** — that sub-case is OD-P2-02, with the owner
(owner-decisions-required.md row 3: "On an unprovisioned machine there is no authenticated record to compare with, so
that sub-case follows OD-P2-02"). Enforcing it there is one condition (`enforced: provisioned`) once the owner decides.

**Product check that owns it.** `kernel_trust::guard` on every governed mutation (via `control::guard_write`), the
policy root on every policy read, doctor D003/D029, audit `mutation_scope` — all now fed by the protected record.
Builder regression: `tests/certification/ws08.rs::a_consistent_post_install_rewrite_is_detected_against_the_protected_record`,
`…::a_machine_that_did_not_install_the_project_verifies_the_pinned_release_first`; lib tests
`srr::installation::tests::{a_consistent_rewrite_diverges…, an_unprovisioned_divergence_is_reported_not_enforced,
pending_and_current_are_both_bound…, a_provisioned_machine_requires_a_verification_record}`. Tier mapping in
`tests/governance/capability-evidence-map.yaml` is WS-1's (IP-5).

**Probes re-run** (audit of record, unedited; `evidence/probes-{before-base-c6b60bc,after-63f82ba}/`)

| Probe line | Before (base) | After |
|---|---|---|
| alpha-r A2-03 [T2] `kernel verify` | `ok=True modified=[] trust.verified=True substituted=False` | `ok=False modified=['policies/SECURITY_POLICY.yaml'] trust.verified=False substituted=True` |
| A2-03 [T2] effective never_index_classes / `task create` | `[]` / `ok` | `['secret','restricted']` / `REFUSED KERNEL_TAMPERED` |
| A2-03 [T2] doctor / audit mutation_scope | `DEGRADED`, D003 intact / `HEALTHY` | `UNHEALTHY`, D003 names the file / `UNHEALTHY` |
| AC16-X3 `X3c-A2:146-consistent-rewrite-detected` | FAIL | **PASS** |
| AC16-X3 `X3d-A2xE1xL3-rewrite-cannot-lower-gate-authority` | FAIL | probe raises `TypeError` before grading (see below) |

X3d creates its gate *after* the rewrite; on the repaired product `gate create` is itself refused `KERNEL_TAMPERED`
(D-0007 rule 1: mutations fail closed), so the probe passes `gid=None` to the next command and crashes. The property it
tests is measured by `evidence/WS08-P1-post-install-integrity.py` [R1c], which raises the gate *before* the rewrite: an
L1 `decide` after the rewrite is refused `AUTHORITY_DENIED` (PASS; base: accepted with `by_kind human`).

Supplementary probe `WS08-P1` (15 lines): repaired 15/15 PASS; base binary 1/15 (R1a–R1h, R2a, R3a–R3c, R4a, R5a fail
on base; R5b is a control). Some base failures cascade from R1 (the base cannot restore the rewritten project).

**Not done / limits.** Unprovisioned enforcement (OD-P2-02). A project copied to a new path on the same provisioned
machine is anchored by the ledger (the machine verified those bytes); a ledger-anchored payload is not additionally
floor-checked at use time (admissibility stays with the ingresses and the break-glass marking, as in R1). A consistent
rewrite that also rewrote the lock needs the pin restored (from VCS or the refusal's details) before reinstalling;
`gov kernel reinstall` cannot rewrite the lock because `cli/src/main.rs` compares against a lock it read before the
install (IP-3 covers a cleaner path).

## 2. BC-P2-36 — presentation and disclosure (admission part is OD-P2-02, untouched)

**Requirement** (repair-delta "determined now"; Contract v3:150; OWNER-DIRECTIVE-0004): an installation whose authenticity
is not established is never presented as current, verified or certified by any surface (CLI envelope, `gov status`,
init/update results), is reported by doctor and audit, and cannot yield a HEALTHY verdict without disclosing it.
**Admission behaviour on unprovisioned machines is unchanged** (verified: `admit`'s unprovisioned branch is untouched;
A2-01 [U2]/[U3] still install with authenticity `UNKNOWN`).

**What changed**
- `runtime/src/srr/present.rs`: `presentation()` speaks about the installations in context
  (`srr::installation::installations_in_context`: roots whose integrity this process evaluated, plus the one the
  working directory is in). If any has no established authenticity, `presented_as` is the new
  `PRESENTED_UNAUTHENTICATED` with a `disclosure` list; the break-glass marking keeps precedence. The disclosure is
  generic per posture (no path, timestamp or machine identity) so context packets stay reproducible across clones.
  `attach` rewrites a "nothing to do" recommendation for an unauthenticated installation (it leaves `up_to_date`, a
  decision input of `update --apply`, as computed). `may_present_as_current` is true only for `CURRENT`.
- `runtime/src/srr/verifier.rs` `record_installed`: the single machine record "what this machine VERIFIED and installed"
  is written only for an authenticated install, so `gov status` (WS-5's file, unchanged) no longer shows an `UNKNOWN`
  install as `verified_release`; `runtime/src/srr/mod.rs` `status()` lists `installations` with their authenticity.
- `runtime/src/srr/installation.rs` `posture_of`, `presentation_disclosures`, `doctor_check` — the API doctor needs.

**Surfaces covered:** every command-result envelope (single `attach` in `cli/src/main.rs`), `gov doctor`'s own payload,
`gov update --check`, the agent context packet, `gov trust status`, `gov status` (no false `verified_release`).
Doctor's **verdict** and audit **findings** need a check in WS-2's files: IP-1 / IP-2.

**Probes re-run**

| Probe line | Before | After |
|---|---|---|
| A2-01 [U2] envelope `presented_as` | `CURRENT` | `UNAUTHENTICATED` |
| A2-01 [U2] `gov status.release_trust.verified_release` | `"4.1.5"` (+ payload hash) | `null` |
| A2-01 [U2] doctor `release_trust` | `presented_as CURRENT`, no disclosure | `UNAUTHENTICATED` + disclosure |
| A2-01 [U2] `trust status.installed_release` | UNKNOWN record shown | `null` (installations listed separately) |
| A2-01 [U2] `gov kernel trust` summary | "verified against KERNEL_MANIFEST.json and framework.lock" | "intact: matches … protected installation record" |
| A2-01 [U4] | self-identified source built `--certification CERTIFIED`, installs UNKNOWN | probe raises `KeyError`: the build is now refused (BC-P2-37) |
| AC16-X3 `X3a-A2:150xU-no-masquerade` | FAIL (`CURRENT`, doctor HEALTHY) | FAIL on its doctor half only: `presented_as UNAUTHENTICATED`, doctor `HEALTHY` → PASS once IP-1 lands |
| AC16-X3 `X3a-S3xA2-unprovisioned-refuses-unauthenticated` | FAIL | FAIL — admission is OD-P2-02, deliberately unchanged |

Supplementary `WS08-P2` (8 lines): repaired 8/8; base 2/8 (P2a/P3a are controls: an authentic provisioned install is
CURRENT, and a command acting on no installation says nothing about one — R1 `hv_b` b2/b4 preserved).

## 3. BC-P2-37 — no trust decision from unsigned release fields; lock records verified identity and its basis

**Requirement** (Contract v3:149-150, :161, :937, :950; D-0007 rule 2): no gate- or trust-relaxing decision rests on a
certification claim the trust root has not authenticated; an unauthenticated certification is uncertified everywhere;
minting a certification claim is authority-gated; every identity field of framework.lock comes from what verification
established (or is marked unverified), records its basis, and does not vary with machine paths.

**What changed**
- `runtime/src/srr/verifier.rs` `certification_of` (read-only): the only authenticated carrier is the signed release
  metadata's `evidence.certification.status` verified under the trusted root's `release` role (ARCH-0003 §4); the
  unsigned `manifest.json` claim is reported and ignored. `AuthenticatedRelease` carries the signed `evidence`.
- `runtime/src/update.rs`: `check` takes the target's identity and compatibility from the candidate payload's
  `KERNEL.yaml` (not `manifest.json`) and certification from `certification_of`; `apply_update_opts` re-binds the
  decision to the admitted release (`bind_decision_to_admitted`: same version; a gate waived for certification only if
  admission authenticated the very `release.json` digest the certification came from; the admitted payload's own
  migrations still need no gate) — typed `UPDATE_TARGET_CHANGED` / `UPDATE_CERTIFICATION_NOT_BOUND` /
  `UPDATE_GATE_CHANGED`. `CERTIFIED`, `UNCERTIFIED`, `claims_certification` live here.
- `runtime/src/release.rs` `build`: `--certification <anything claiming CERTIFIED>` is refused
  `RELEASE_CERTIFICATION_REQUIRES_SIGNED_METADATA` after the §6 guard and before any write (gov never signs, so it cannot
  mint an authenticated claim; the authority is the owner's `release` key). `verify` reports
  `certification.effective_status` (authenticated or `UNCERTIFIED`) with the unsigned claim beside it.
- `runtime/src/lock.rs` `write_lock` / `release_identity` (signature unchanged, so WS-9's adopt call site benefits
  without edits): identity from the protected installation record of these exact digests; top-level `authenticity`,
  `sequence`, `channel`, `release_metadata_sha256` and an `identity_basis` block; `release_commit` = signed
  (`evidence.provenance.release_commit`) › binary constant when the payload is byte-identical to the embedded payload ›
  `unverified`; `source` = `release:` only when verified, `embedded:` decided by **content**
  (`kernel::embedded_payload_hash`), else `source:`. `kernel::source_label` / `release_commit_for_source` /
  `is_embedded_dir` no longer use path patterns or unsigned manifests. `framework-lock.schema.json`: optional fields
  documented (no `additionalProperties:false`, so older installed schemas still validate).

**Probes re-run**

| Probe line | Before | After |
|---|---|---|
| A2-04 [L1] `framework.lock.release_commit` (forged `f00dface…` in unsigned manifest) | `f00dface…` | not recorded (`25dac6ef…` binary constant here: the canonical copy equals the embedded payload; `unverified` otherwise) |
| A2-04 [L2] edited unsigned manifest CERTIFIED | `certification CERTIFIED`, gate waived, update applied with no gate | `UNCERTIFIED`, gate required, `HUMAN_GATE_REQUIRED`, gate `HDG-0001` pending |
| A2-04 [L2] `release build --certification CERTIFIED` as L1 | `ok = True`, CERTIFIED | refused |
| A2-04 [L3] lock carries authenticity/sequence/channel/metadata digest | `False` | `True` (AUTHENTIC vs UNKNOWN distinguishable) |
| A2-04 [L4a/b/c] embedded identity vs XDG_CACHE_HOME | `embedded…25dac6ef` / `source… unknown` / `source…` = consumer HEAD | identical `embedded:…@4.1.5`, `25dac6ef…` in all three |
| S6 [X3] XDG_CACHE_HOME without `.cache` | identity ≠ A | identity = A |
| `00-regression-variant-xdg-cache` (certification suite, XDG_CACHE_HOME without `.cache`) | 78/79 (`repair2::framework_lock_is_release_identifying_and_portable` fails) | 86/86 |

Supplementary `WS08-P3` (11 lines incl. C7 R1 control): repaired 11/11; base 2/11.

## 4. BC-P2-38 — provisioned-machine rollback and failure atomicity

**Requirement** (Contract v3:944, :151; OWNER-DIRECTIVE-0004; ARCH-0003 §6-§7; OWNER-DECISION-0006/0007): on a
provisioned machine the rollback ingress can restore a release this machine previously verified, subject to the
owner's floor/break-glass rule; a refused privileged lifecycle command leaves the installation as it found it.

**What changed**
- `runtime/src/srr/verifier.rs` offline path (Recovery/Rollback/Reinstall with no reachable metadata): authenticity from
  the verified-release **ledger** (any release this machine authenticated, by digest), then the single record; both
  must record a verification. Identity (version, sequence) comes from the ledger, so the floor check and break-glass run
  on machine-verified values. No floor, break-glass or exit-policy code changed.
- `runtime/src/kernel.rs` `pinned_release_check`: a reinstall of a payload other than the pinned one is refused
  `KERNEL_MISMATCH` **before the swap** (staging abandoned; `installation_changed: false`). `AdmissionRequest::
  with_pinned_payload` lets the caller move that refusal ahead of break-glass entry (IP-3).
- `runtime/src/update.rs`: a refused admission removes the pre-admission snapshot (A0-S5-01: no false rollback); the
  transaction abort restores the protected installation record with the bytes; `rollback_internal` commits the
  verified kernel first, then overlay/generated/lock.

**Probes re-run**

| Probe line | Before | After |
|---|---|---|
| A2-02 [P9] `update --rollback` after an authentic update | `SRR_RELEASE_UNVERIFIED` (previous release not authenticatable) | `SRR_BELOW_FLOOR` (authenticated from the ledger; the owner's floor refuses) |
| A2-08 [V1] reinstall authentic 4.1.6 onto 4.1.5 | `KERNEL_MISMATCH` after commit | `KERNEL_MISMATCH` before the swap |
| A2-08 [V2] state after | kernel 4.1.6 under lock 4.1.5, `trust.verified=False`, mutations `KERNEL_TAMPERED` | kernel 4.1.5 = lock, verified, mutations ok |
| A2-05 [K6a] break-glass reinstall of an older release | kernel = older, lock = newer, `trust.verified=False`, `KERNEL_TAMPERED` | kernel = lock = newer, verified; machine marked DEGRADED (residual, IP-3) so mutations `SRR_BELOW_FLOOR_REFUSED`; exit reinstall clears it |
| A2-05 [K6b] | update applied only because an unsigned CERTIFIED manifest waived the gate; rollback `SRR_RELEASE_UNVERIFIED` | the probe's update now stops at the gate (BC-P2-37), so there is nothing to roll back (`SNAPSHOT_MISSING`) — re-established with the gate walked in `WS08-P4` [K1] |
| S5 [U7]/[U8] | built with `--certification CERTIFIED` | builds refused (BC-P2-37); re-established in `WS08-P4` [K4]/[K5] |

Supplementary `WS08-P4` (11 lines): repaired 11/11; base 4/11. [K1]: gated update 4.1.5 (seq 10) → 4.1.6 (seq 20);
`update --rollback` → `SRR_BELOW_FLOOR`, installation unchanged; owner token → `update --rollback --break-glass` restores
4.1.5 with authenticity `PREVIOUSLY_VERIFIED_BY_THIS_MACHINE`, machine marked `DEGRADED — RECOVERY ONLY`, high-water
unchanged (seq 20). [K4]: refused unsigned update leaves no snapshot; rollback `SNAPSHOT_MISSING`, no ledger event.
[K5]: transaction abort restores kernel, lock and protected record; governed work continues.

**Residual (closes with IP-3).** On the reinstall path the verifier enters break-glass (writes the marking, consumes the
owner's nonce) before it learns the project's pin, because `cli/src/main.rs` does not pass it. The installation is
unchanged (kernel, lock, records verified above), but the machine is left marked until an at-floor reinstall clears it.

## 5. R1 preservation (AC-14) and regression

**Every prior R1 held-out suite, unedited** (`evidence/r1-heldout-rerun.sh`; byte-identity of every copied file is
`cmp`-verified in each output; single-threaded, authority env stripped):

| Suite | Recorded baseline (AR-0033 `REPRODUCTION.md` §5-§6) | Before (base `c6b60bc`) | After (`63f82ba`) |
|---|---|---|---|
| AR-0027 (`4.1.6-r1`) | 26 pass / 3 fail (b1, b2, d3) | 26 / 3 (b1, b2, d3) | 26 / 3 (b1, b2, d3) |
| AR-0029 (`4.1.6-r1-2`) | 26 / 2 (b3, b6); `ho_f_preservation` does not compile | 26 / 2 (b3, b6); ho_f n/c | 26 / 2 (b3, b6); ho_f n/c |
| AR-0031 (`4.1.6-r1-3`) | 27 / 7 (a1, a5, a8, b6, c2, c3, d2) | 27 / 7 (same) | 27 / 7 (same) |
| AR-0033 (`4.1.6-r1-4`) | 31 / 0 | 31 / 0 | **30 / 1** (`hv_a::a1`) |

The failure message of every pre-existing failure is identical before and after (diffed). The one new failure is
`hv_a_derivation::a1`, whose first assertions pin the product tree's size (`84` files, `740` functions); this repair adds
one file and functions, so any candidate that adds a function fails it (after: 85 files / 801 functions). Its
substantive assertion — zero independently derived §6 violations — is measured by AR-0033's own independent Python
derivation (`release/verification/4.1.6-r1-4/evidence/derive.py`, copied with only its ROOT line changed, appended to
`r1-heldout-after-63f82ba.out`): **0 violations** in all three splitter configurations. `hv_a::a9` (the `#[cfg(test)]`
cut hides no primitive) passes; an intermediate version of the new unit tests wrote a provisioning latch and tripped it,
so the tests now pass the posture to `anchor_posture`/`divergence_posture` instead of writing one.

R1 invariants held by construction and re-measured by the suites: `srr::admit(` call sites 5, `install_kernel(` call
sites 5, `by_admit` 1, one `AuthenticatedRelease` construction; `resolve_state_root`, `default_state_root`,
`exit_satisfied` byte-identical to base; no `resolve_state_root() else`; `effective_floor_sequence()` sites ≤ 4;
`"CERTIFIED"` literal only in `update.rs`, `"certification": {"status": certification_status` only in `release.rs`;
`root_metadata_path()` reached from the same 2 files; `kernel_trust.rs` free of SRR verdict vocabulary; no `Floors`
mutator added; no signing capability.

**Product regression** (`evidence/regression.sh`, HOME redirected; mode `xdgcache` also points XDG_* at paths without
`.cache`):

| | Before | After |
|---|---|---|
| `cargo test --lib` | 42/42 (both modes) | 52/52 (both modes) |
| `cargo test --test certification` | 79/79 default; **78/79** xdgcache | **86/86** default; **86/86** xdgcache |

`tests/certification/section6.rs` and `srr.rs` green (inside the 86). Tests changed: `repair2.rs` —
`framework_lock_is_release_identifying_and_portable` and `genuine_412_consumer_updates_through_413_to_414_and_rolls_back_with_ledger`
asserted the old BC-P2-37 defect (lock `release_commit` = the unsigned `manifest.json` value; `release:` label from a
`/release/releases/` path; the checkout's Git HEAD as identity). They now assert `unverified` / `source:` for an unsigned
release on an unprovisioned machine, and content-decided `embedded:` identity (equal to the embedded install) for the
canonical checkout. Tests added: `tests/certification/ws08.rs` (7), lib tests in `srr/installation.rs` (8),
`kernel.rs` (1: embedded payload digest = what staging measures), `update.rs` (1). `cargo fmt`: every touched Rust file
is rustfmt-clean (formatted per file via stdin so untouched modules, e.g. `breakglass.rs`, were not reformatted).

## 6. Integration points

| ID | Owner / file | Exact call | Why |
|---|---|---|---|
| IP-1 | WS-2 `runtime/src/doctor.rs` `run` | `add(crate::srr::installation::doctor_check(&p.root, "<D0xx>"));` (id is doctor's to assign) | BC-P2-36: doctor must report an unestablished authenticity and not be HEALTHY without it; `doctor_check` returns doctor's own `chk()` shape, severity `medium` when not established. Makes AC16-X3 `X3a-A2:150xU-no-masquerade` pass. |
| IP-2 | WS-2 `runtime/src/verification/mod.rs` (a posture/trust family) | `let pst = crate::srr::installation::posture_of(&p.root); if pst["installed"] == true && pst["authenticity_established"] != true { f.findings.push(finding("medium", &fam, pst["disclosure"]…)) }` | BC-P2-36: audit discloses it. (Consistent rewrites already reach audit via `verify_kernel`.) |
| IP-3 | WS-3 `cli/src/main.rs` `KernelCmd::Reinstall` | chain `.with_pinned_payload(lock["release_hash"].as_str().map(String::from))` on the `AdmissionRequest`; optionally re-read the lock after `install_kernel` instead of the pre-read copy | BC-P2-38: the pin refusal then precedes break-glass entry and nonce consumption (closes the [K6a] marking residual). |
| IP-4 | WS-5 `runtime/src/status.rs` `status` | build `release_trust` from `crate::srr::installation::posture_of(&p.root)` (this project) instead of the machine-wide `InstalledRecord` | BC-P2-36: on a provisioned machine with several projects, `verified_release` should describe this project's installation. |
| IP-5 | WS-1 `tests/governance/capability-evidence-map.yaml` | map A2:146 → `kernel_trust::guard`/`srr::installation::anchor_for` + `ws08.rs` rewrite/clone tests; A2:149-150 → `lock::release_identity`, `update::check`/`verifier::certification_of`, `release::build` + `ws08.rs` cert/lock tests; A2:150 presentation → `present::presentation` + `ws08.rs` presentation test; S5:944 → verifier offline ledger path + `ws08.rs` rollback/atomicity tests | AC-10 evidence owner rows. |
| IP-6 | WS-9 `runtime/src/adopt.rs` | none required: `write_lock` and `install_kernel` decide identity and records themselves; adopt's hints are ignored | noted so WS-9 does not duplicate. |

Round 2 (per handoff): the `init.rs` role plumbing for BC-P2-08 waits for WS-3's resolution API.

## 7. Owner decisions

No new owner-decision question. Two interactions with **OD-P2-02** (already with the owner) are recorded so the answer
can be applied mechanically: (a) admission on unprovisioned machines is unchanged; (b) the unprovisioned sub-case of
BC-P2-35 is report-only (`DIVERGED_NOT_ENFORCED`); under option A or C it disappears, under option B the record already
marks integrity as unanchored, and enforcing it is the single condition `enforced: provisioned` in
`srr::installation::anchor_posture`/`divergence_posture`.

## 8. Limits and observations

- Operator impact on provisioned machines: a clone from another machine, a `git pull` of another machine's update, or a
  checkout of an older kernel is refused (`KERNEL_UNANCHORED` / `KERNEL_TAMPERED`) until `gov kernel reinstall --source
  <the signed release framework.lock pins>` verifies it — ARCH-0003 §8, and the floor check applies at that ingress.
- `gov` cannot mint `CERTIFIED` at all now; certified releases exist only through owner-signed release metadata (R2).
- Probe precondition breakages caused by the repairs themselves (not regressions): AC16-X3 X3d (`TypeError`), A2-01 [U4]
  (`KeyError`), A2-02 [P6]/[P8] (sources now absent: `KERNEL_SOURCE_NOT_FOUND`), A2-05 [K6b] and S5 [U7]/[U8] (updates
  now need their gate). Each property is re-established in `WS08-P1..P4` (R1c, C7, K1, K4, K5).
- Observation outside my files: `runtime/build.rs` derives `EMBEDDED_COMMIT` from `release/releases/<version>/manifest.json`
  whenever the tree carries that release, even when the working tree's framework differs from it; the lock basis calls
  it "constant of the running gov binary", which is exactly what it is, but for a development build it is not the
  commit the embedded bytes came from.

## 9. Evidence index (`evidence/`)

| File | What |
|---|---|
| `regression.sh`, `regression-{before-base-c6b60bc,after-63f82ba}.out` | lib + certification, default and xdgcache modes |
| `r1-heldout-rerun.sh`, `r1-heldout-{before-base-c6b60bc,after-63f82ba}.out` | all four R1 held-out suites unedited + supplementary `derive.py` |
| `probes-rerun.sh`, `probes-{before-base-c6b60bc,after-63f82ba}/` | audit-of-record probes A2-01/02/03/04/05/08, S5, S6, AC16-X3 (probe sources sha256-listed, unmodified) |
| `ws08_common.py`, `WS08-P1…P4-*.py`, `ws08-probes.sh` | supplementary builder probes |
| `ws08-probes-after-63f82ba.out` / `ws08-probes-negative-control-base-c6b60bc.out` | 45/45 PASS repaired; 9/45 PASS on the base binary (the probes discriminate) |
