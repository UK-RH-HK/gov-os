# P2-AR-0029 — Repair iteration 1, round 2, WS-8: root of trust and lifecycle ingress

| Field | Value |
|---|---|
| Run | P2-AR-0029, fresh `capability-repair` builder, model Claude Opus 5 (1M context), `claude-opus-5[1m]` |
| Handoffs | P2-HO-0027 (WS-8 round 2), P2-HO-0020 (round-2 common), P2-HO-0010 (common protocol); OWNER-DECISION-P2-0002 |
| Items | BC-P2-36 **admission** (OWNER-DECISION-P2-0002, Option A) with harness/fixture/docs provisioning; the unprovisioned sub-case of BC-P2-35; IP-WS02-12..16 (WS-2); IP-2 (WS-1/12); IP-7 (WS-3); IP-16 (WS-4) |
| Base | `843d79c33e8a8db8b223611abc23d317edbc82a1` (integrated round-1 tree), `product_code_digest b1ab1c8c…fbb1` |
| Branch | `phase2/repair-1-r2-ws08` |
| Work commits | `eca268e` product + harness + tests + fixture READMEs · `cf13dee` cache unit test (**final product state**) · evidence/report commit (named in the run report) |
| Final `product_code_digest` | `37087f1308754f86a20d505da9474d11b2ff7d27d36eb09ce148a316ab4c4966` at `cf13dee`; `governed_state_digest 4981437f…227d` **unchanged** (no spec/, docs/, D-0007 or Contract v3 change) |
| Release binary | `target/release/gov` at `cf13dee`: sha256 `8d94a48a9beb8cc3…3e9c` (base export: `7095d188…0332`) |
| Verdict | `READY_FOR_INDEPENDENT_CAPABILITY_VERIFICATION` — builder claims only (Contract v3 O3). Two routed IPs are not implemented, each with its reason (§7); the documentation part of requirement 3 is an integration point because no doc file is owned by WS-8 (§3.3). |

Every number below is from a run recorded under `evidence/`. Builder tests and probes are regression evidence; acceptance
belongs to fresh independent verifiers.

## 0. Design in one paragraph

The one verification policy (`srr::verifier::admit`) now decides OWNER-DECISION-P2-0002 in its unprovisioned branch,
after the candidate is privately staged and measured and before anything else: a machine with no trust anchor admits
exactly one payload, the one embedded in the running `gov` binary, **decided by the digest of the staged bytes**
(never by path), and only as a marked `BOOTSTRAP_EMBEDDED_PAYLOAD` admission carrying the binary's identity; every
other candidate is refused `SRR_UNPROVISIONED_EXTERNAL_SOURCE_REFUSED` (typed, remediation "provision") and its staging
is abandoned. Because the check sits in the verifier, it covers every ingress (`init --source`, `update`, `adopt`,
`kernel reinstall`, rollback, recovery) without touching any call site. The marking travels into the protected
per-project installation record, `framework.lock` (`admission`), `gov trust status` and every presentation disclosure.
Post-install integrity on an unprovisioned machine now holds the installed kernel to the bootstrap record (or the
running binary's payload), which closes the unprovisioned sub-case of BC-P2-35. The certification suite follows the
documented first-run path: every scenario machine is provisioned with the suite's throw-away test root and installs
releases signed under it. The provisioned path of `admit` — metadata chain, identity/verified-byte/migration binding,
floor check, break-glass — is byte-identical to the base.

## 1. BC-P2-36 admission — OWNER-DECISION-P2-0002 requirements 1 and 2

**Requirement** (OWNER-DECISION-P2-0002 §"Requirements" 1-2, applying Contract v3 A2:143 as written; A2:150;
OWNER-DIRECTIVE-0004; ARCH-0003 §5): on a machine with no administrator-provisioned trust anchor, privileged kernel
material from an external source (`init --source`, `update`, `adopt`, `kernel reinstall`, any ingress staging material
not embedded in the running verifier binary) is refused, typed and observable, with remediation pointing to
provisioning; the binary's own embedded payload may be installed only as an explicitly marked bootstrap mode tied to
the binary's identity, never presented as current, verified or certified, and disclosed by doctor and audit.

**What changed**
- `runtime/src/srr/verifier.rs`
  - `admit_inner`, unprovisioned branch: `staged.payload_hash != kernel::embedded_payload_hash()` →
    `SRR_UNPROVISIONED_EXTERNAL_SOURCE_REFUSED` (details: ingress, posture, `UNPROVISIONED_ADMISSION_POLICY`, decision,
    candidate, measured digests, embedded digest, `staged_for_installation: false`, remediation list); otherwise the
    admission carries `bootstrap = {mode, decision, binary: kernel::binary_identity(), authenticity: UNKNOWN, …}` and a
    `BOOTSTRAP_EMBEDDED_PAYLOAD` note. The pre-existing "no provisioned Signed Release Root trust anchor" note is kept
    verbatim (AR-0027 `c4` reads it).
  - `AuthenticatedRelease` gains `pub bootstrap: Option<Value>` and `admission()` (`SIGNED_RELEASE_METADATA`,
    `PROTECTED_RECORD_OF_AN_EARLIER_VERIFICATION`, `BOOTSTRAP_EMBEDDED_PAYLOAD`); `to_value` reports both. The seal
    (`sealed::Admitted`, one `by_admit` call) is unchanged.
  - `refuse_external_source_if_unprovisioned(ingress, candidate)`: the same decision taken early and read-only (the
    candidate is measured with the product's staging selection into a temporary directory outside every project), so
    `update --apply` refuses before it raises a Human Decision Gate for a candidate admission will refuse, and
    `update --check` states it (`admission.refused_before_staging`). An unresolvable state root is a refusal, not a
    clearance (AR-0033 `hv_c::c6`). One error constructor serves both points.
- `runtime/src/kernel.rs`: `binary_identity()` (gov/cli version, embedded kernel version and commit, embedded payload
  digest, executable sha256).
- `runtime/src/srr/installation.rs`: `BoundPayload` records `admission` and the `bootstrap` marking (older records
  read as empty); `posture_of` reports `admission`, the `bootstrap` marking and a BOOTSTRAP disclosure;
  `presentation_disclosures` carries one generic BOOTSTRAP sentence (no path or identity, so context packets stay
  reproducible) and one "NOT ADMITTED" sentence.
- `runtime/src/lock.rs` + `framework/schemas/framework-lock.schema.json`: `framework.lock.admission` and a BOOTSTRAP
  `identity_basis.established_by`.
- `runtime/src/srr/mod.rs`: `gov trust status` reports `admission_policy` for the posture and each installation's
  `admission`.
- `runtime/src/update.rs`: the early refusal before the gate (above); `check` reports `admission`.

**Presentation** is the round-1 mechanism: a bootstrap installation's authenticity is `UNKNOWN`, so every command
envelope says `presented_as: UNAUTHENTICATED` with the BOOTSTRAP disclosure, `gov status` makes no `verified_release`
claim, `gov update --check` never says "nothing to do", and `gov doctor`'s own payload carries the disclosure. Doctor's
*verdict* and audit *findings* need checks in WS-2's files — round-1 IP-1/IP-2, re-routed with the admission field
(§9, IP-R2-WS08-2/3).

**Product checks that own it**: `srr::verifier::admit` (every privileged ingress; 5 call sites unchanged),
`srr::verifier::refuse_external_source_if_unprovisioned` (update before its gate; update --check),
`srr::present::presentation` via `installation::presentation_disclosures` (every CLI envelope, doctor payload, update
--check, context packet), `srr::status` (`admission_policy`).

**Probes re-run** (audit of record, unedited, through the integration builder's evidence adapter — §8.2)

| Probe line | Before (base `843d79c`) | After (`cf13dee`) |
|---|---|---|
| AC16-X3 `X3a-S3xA2-unprovisioned-refuses-unauthenticated` | **FAIL** — `init_ok: true`, authenticity UNKNOWN | **PASS** — refused `SRR_UNPROVISIONED_EXTERNAL_SOURCE_REFUSED` |
| AC16-X3 `X3a-A2xA3xC4-*`, `X3a-A2:150xU-no-masquerade` | PASS, PASS | not evaluated by the probe: its tampered release is refused at ingress, so no installation exists to present (the probe only grades them `if o.ok()`); the bootstrap installation's presentation is graded by A2-01 [U3] and `ws08_r2` below |
| alpha-r A2-01 [U2] tampered release, unprovisioned | admitted, UNKNOWN; installed SECURITY_POLICY tampered; effective `never_index_classes = []` | refused typed before staging; nothing installed |
| alpha-r A2-01 [U3] embedded payload, unprovisioned | ok, UNKNOWN, `embedded:` | ok, UNKNOWN, `embedded:` (bootstrap admission) |
| alpha-r A2-04 [L3] unknown-install row | `established_by: not established: installed on a machine with no … anchor` | `admission: BOOTSTRAP_EMBEDDED_PAYLOAD`, `established_by: not established: a BOOTSTRAP installation …` (authentic row: `SIGNED_RELEASE_METADATA`) |
| round-1 `WS08-P2` P1a-P1f (presentation on an unprovisioned machine) | 8/8 | 8/8 (the probe's "unsigned release" is `git archive HEAD` of this tree, byte-identical to the embedded payload, so it is — correctly — a bootstrap installation, disclosed as such) |

Full comparison: `evidence/COMPARE-probes-before-base-843d79c-vs-after-cf13dee.out`.

**Builder tests added** (`tests/certification/ws08_r2.rs`):
- `an_unprovisioned_machine_refuses_external_source_kernel_ingress_at_every_ingress` — `init --source` (another
  release; a doctored copy of the current framework; a release signed under some root), `update --check`/`--apply`
  (refused before any gate is raised), `kernel reinstall`, `update --rollback` (a snapshot is repository content) and
  `adopt migrate` batch 0: each refused typed, remediation "provision", nothing staged left behind, installation
  unchanged.
- `the_bootstrap_installation_is_marked_tied_to_the_binary_and_never_presented_as_current` — via the embedded cache and
  via a byte-identical checkout: admission, binary identity, lock marking, UNAUTHENTICATED + BOOTSTRAP disclosure on
  status/doctor/gate list/version, no `verified_release`, no floor raised, trust status policy and installation
  marking; governed work proceeds on the bootstrap baseline.
- `a_provisioned_machine_never_installs_in_bootstrap_mode` — the embedded payload without signed metadata is refused
  `SRR_RELEASE_UNVERIFIED` on a provisioned machine (R1 behaviour unchanged); a signed install is
  `SIGNED_RELEASE_METADATA`, CURRENT.

**Limits.** Content-based: a source directory that is byte-identical to the embedded payload *is* the embedded payload
and is admitted as bootstrap whatever its path (this is the decision's own criterion, "material not embedded in the
running verifier binary"). A refused `init` envelope on an unprovisioned machine still says `presented_as: CURRENT`,
because the command acts on no installation (round-1 design, R1 `hv_b` b2/b4).

## 2. BC-P2-35 — the unprovisioned sub-case

**Requirement** (repair-delta BC-P2-35 "the unprovisioned case follows OD-P2-02"; owner-decisions-required row 3
"under A there is no unprovisioned install to verify"; handoff: "none remains under Option A — confirm").

**Confirmed, with one refinement.** Under Option A no *external-source* install can happen on an unprovisioned machine.
But a bootstrap installation can still be rewritten consistently after install (payload + manifest + lock), and a
clone can carry another machine's kernel onto an unprovisioned machine; round 1 reported those and did not enforce
them (`DIVERGED_NOT_ENFORCED`, `UNRECORDED`). Left so, Option A could be bypassed without an ingress. Now, on a machine
with no trust anchor (`srr::installation::anchor_posture` / `divergence_posture`):
- the payload byte-identical to the running binary's embedded payload is `MATCHED` (the bootstrap baseline D-0007
  rule 1 would substitute anyway);
- a record that binds the payload **and** records a bootstrap admission is `MATCHED`;
- a divergence from the record is `DIVERGED`, **enforced** (`KERNEL_TAMPERED`, embedded baseline substituted);
- anything else — no record, or a pre-decision external-source install — is the new `UNADMITTED` state:
  `KERNEL_UNANCHORED` with remediation "provision, then verify the pinned signed release"
  (`kernel_trust::guard`, message and details name OWNER-DECISION-P2-0002).

Provisioned-machine decisions are unchanged (the provisioned arms of `anchor_posture` are the base's, reordered only
behind the posture test). `kernel_trust.rs` still contains none of `srr::admit`, `AuthenticatedRelease`,
`Authenticity`, `breakglass`, `below_floor`, `Floors` (evidence `r1-invariants-after-cf13dee.out`).

**Tests**: `ws08_r2::a_consistent_rewrite_of_a_bootstrap_installation_fails_closed` (rewrite → `kernel verify` not ok,
`protected_record: DIVERGED`, mutation `KERNEL_TAMPERED`, security floor from the embedded baseline, "NOT ADMITTED"
disclosure; restore → trusted) and `…_does_not_trust_kernel_material_it_never_admitted` (a provisioned machine's signed
4.1.1 copied to an unprovisioned machine → `KERNEL_UNANCHORED`/`UNADMITTED`; remedy provision + reinstall → CURRENT;
control: a bootstrap install copied to another unprovisioned machine stays trusted). Unit tests in
`srr/installation.rs` replaced (§5.2).

**Probes**: AC16-X3 `X3c-*` (provisioned consistent rewrite) PASS before and after; round-1 `WS08-P1` R2a now FAILS by
design — it asserted round 1's report-only behaviour on an unprovisioned machine (`"the rewrite is REPORTED"`), which
this item reverses (after: `protected_record.state = DIVERGED`, enforced).

## 3. Harness, fixtures and documentation — requirement 3 ("provision, then install")

### 3.1 Harness (`tests/certification/common.rs`)

Additive helpers, documented in the file: `provision(&Gov)` (anchors one simulated machine on the suite's THROW-AWAY
TEST ROOT — `srr_material::Publisher`'s published-seed keys, 2-of-3 root, release/snapshot/timestamp/recovery roles,
plus the `human-gate` role delegated to the test owner key `ws03::owner`, because on a provisioned machine the
authenticated human channel is that delegation), `suite_root_file()`, `is_provisioned`, `signed_source()` (the current
framework signed at `CURRENT_SEQUENCE = 100`), `signed_copy(src, tag, seq)` / `sign_release(dir, seq)` (historical and
synthetic releases at `sequence_of(version)` = 11..14), `break_glass(&Gov, recovery_kernel, nonce)` (owner-signed
`recovery` token in the machine's inbox), and `setup_fixture_unprovisioned` for scenarios that are about the
unprovisioned posture. `setup_fixture` now provisions the scenario machine; `run_brownfield_to_a6` installs from the
signed release.

### 3.2 Every certification test's setup — what changed and why no assertion was weakened

| File | Change | Why / property kept |
|---|---|---|
| arch, greenfield, failure_injection, repair (18), repair2 (5), repair3 (4), upstream (2), ws03 (8) | `init` gets `--source signed_source()`; `setup_fixture` provisions; upstream provisions explicitly; failure_injection's `kernel reinstall` gets the signed source | provision then install; the asserted properties are about the installed product, not the install path |
| brownfield, migration (2), repair (freeze test), common | `adopt migrate` batch 0 gets `--source signed_source()`; migration's hand-built project provisions | A6 batch 0 is the adopt ingress |
| multi_machine | machine B is provisioned and verifies the pinned release (`kernel reinstall --source …`) before relying on the clone; asserts the verification leaves the working tree clean | ARCH-0003 §8 "additional machines … verify their pinned release"; the manifest/status/context-hash identity assertions are unchanged |
| update | provision; signed synthetic 4.1.1 (seq 11) and current (seq 100); `update --rollback` first asserted refused `SRR_BELOW_FLOOR`, then run with `--break-glass` under the owner token | on a provisioned machine 4.1.1 is below the release high-water (ARCH-0003 §7, OWNER-DECISION-0006); the byte-for-byte restoration assertions are unchanged (one assertion added) |
| repair (update approval) | provision; signed 4.1.1 / current | unchanged assertions |
| repair (`embedded_kernel_installs_without_canonical_root`) | stays **unprovisioned** (its subject is the embedded payload); asserts the admission is `BOOTSTRAP_EMBEDDED_PAYLOAD`, authenticity UNKNOWN | assertions added only |
| repair2 lock test | adds an unprovisioned machine refusing the shipped 4.1.3 (`SRR_UNPROVISIONED_…`, nothing written); installs the signed 4.1.3 on a provisioned machine: `release_commit` still `unverified` and ≠ the unsigned manifest commit, basis still "not recorded as identity"; `source`/`authenticity` now `release:…@4.1.3` / `AUTHENTIC` (+ sequence); the two embedded-identity installs stay unprovisioned (bootstrap) with their assertions unchanged; the clone is another machine: provisioned, verifies, then the D003 assertion | the property (an unsigned claim is never identity; identity is decided by verification and content, never by path) is kept; the two value changes state what a verified install now establishes |
| repair2 chain test | signed 4.1.2/4.1.3/current; 4.1.3 lock `source` `release:`, `AUTHENTIC`; current lock `release:` with the embedded commit (content); both rollbacks first refused `SRR_BELOW_FLOOR`, then run under break-glass | same reasons; ledger, snapshot, INV-013 and final-state assertions unchanged |
| ws03 | `fresh_unprovisioned` for `human_answers_come_only_from_the_owner_signed_channel` | that test is about the standalone human-channel anchor, which exists only on a machine with no release root |

Suite size: 100 → 110 (10 new tests in `ws08_r2.rs`). `tests/certification/main.rs`: one additive `mod ws08_r2;` line.

### 3.3 Fixtures and documentation

- Every fixture README (`fixtures/*/README.md`) now states the first-run path (provision with the suite's throw-away
  root, install a release signed under it; unprovisioned machines admit only the binary's embedded payload as a marked
  bootstrap), plus the multi-machine verification step, the update fixture's signed sequences and break-glass
  rollback, and the adopt ingress. No fixture `project/` file changed.
- **Documentation outside `fixtures/` is not owned by WS-8** (`README.md` quickstart line 59-60 `bin/gov init …`,
  `docs/COMMANDS.md`, `docs/FIXTURES.md`, `docs/ARCHITECTURE.md`). The exact change is integration point
  **IP-R2-WS08-1** (§9).

## 4. Requirement 4 — Phase-4 and release evidence on provisioned machines

Product support within WS-8's files: `gov release build` records the building machine's posture in
`PRE_RELEASE_CHECKS.json` (`machine_posture`, `release_evidence_eligible = PROVISIONED ∧ contract bound`), so release
evidence produced on a machine with no trust anchor cannot pass for provisioned evidence. The qualification (G6) entry
point is WS-2's: **IP-R2-WS08-8**.

## 5. Requirement 5 / R1 (AC-14) — provisioned behaviour unchanged

### 5.1 Prior R1 held-out suites, unedited, measuring this worktree

Run by `evidence/r1-heldout/run-r1-heldout.sh` from a **private scratch root named with this run id**
(`…/scratchpad/p2-ar-0029-r1-heldout`, symlinks `wt/srr1-r1-verify{,-2,-3,-4}` → this worktree only; each header
records the worktree path, HEAD, dirty count and census). Every copied suite file is `cmp`-identical; each test binary
runs single-threaded with the nine refused-authority variables and `GOV_MACHINE_STATE_DIR` stripped.

| Suite | Recorded baseline | Before (base `843d79c`) | After (`cf13dee`) |
|---|---|---|---|
| AR-0027 (`4.1.6-r1`) | 26 / 3 (`b1`, `b2`, `d3`) | 26 / 3 (same) | **26 / 3** (same) |
| AR-0029 (`4.1.6-r1-2`) | 26 / 2 (`b3`, `b6`); `ho_f` does not compile | 26 / 2 (same); `ho_f` n/c | **26 / 2** (same); `ho_f` n/c |
| AR-0031 (`4.1.6-r1-3`) | 27 / 7 (`a1`, `a5`, `a8`, `b6`, `c2`, `c3`, `d2`) | 27 / 7 (same) | **27 / 7** (same) |
| AR-0033 (`4.1.6-r1-4`) | 31 / 0 | 30 / 1 (`hv_a::a1` size pin) | **30 / 1** (`hv_a::a1` size pin only) |
| **Census** (AR-0033 `hv_a::a1` independent walk) | 84 files / 740 functions | **105 / 1457** | **105 / 1468** |

- Every failure/observation message is identical before and after once paths, thread ids and 3+-digit integers are
  normalised (58 lines each, empty diff: `evidence/r1-heldout/failure-messages-before-vs-after.txt`).
- **`hv_a::a1`, handled as P2-HO-0020 item 7 says**: the labelled derived copy
  `evidence/r1-heldout/hv_a_derivation.a1-unpinned.P2-AR-0029.rs.txt` differs from the held-out file only in the two
  size assertions (the `diff` is printed in each output) and runs from a separate scratch crate: 105 files / 1468
  functions, **0 violations in every §6 activity** (human_gate_create 43 derived / 38 writers / 1 exempt;
  human_gate_approve 1/1; release_certification 1/1; trust_policy_mutation 8/1; privileged_plugin_acquisition 10/2;
  floor_lower_or_reset 3/1; present_below_floor_release_as_current 1/1 — identical to the base). AR-0033's own
  `derive.py` (ROOT line only substituted) agrees under all three splitter configurations, 0 violations.
- One regression was found and fixed during development: the first version of the early refusal used
  `let Ok(root) = resolve_state_root() else { return Ok(()) }`, which AR-0033 `hv_c::c6` rejects as the AR31-B2
  fail-open shape (`r1-heldout-dev-dirty.out`, 29/2). It now propagates the error (fail closed); the final run is at
  baseline.

### 5.2 The four ingress/floor properties and the §5 allow-list (`evidence/r1-invariants-after-cf13dee.out`)

1. **One verifier at every privileged ingress; only it constructs the typed value** — `srr::admit(` 5 sites (cli
   reinstall, adopt, init, update ×2), `install_kernel(` 5 sites, one `by_admit` call, no `AuthenticatedRelease`
   literal outside `verifier.rs`. The new admission rule lives inside `admit`, so it is uniform by construction.
2. **The floor binds every ingress** — `admit_inner`'s floor-check and break-glass block (steps 9-10),
   `Ingress::is_backward_capable` and `may_use_protected_installed_record` are byte-identical to the base;
   `effective_floor_sequence()` occurrences 3 (≤ 4).
3. **Break-glass relaxes the floor only, never authenticity** — `SRR_BREAK_GLASS_REQUIRES_AUTHENTIC_RELEASE` unchanged;
   an unprovisioned machine has no floors and no `recovery` role, as before.
4. **Floors are monotonic and rise only from authenticated observations** — `breakglass.rs`, `state.rs`, `metadata.rs`,
   `crypto.rs`, `provision.rs` unchanged; no floors writer outside `state.rs`; a bootstrap (UNKNOWN) admission raises no
   floor (`ws08_r2` asserts `release_high_water.sequence == 0`).

**§5 allow-list**: `breakglass.rs` is byte-identical to the base; `PERMITTED_OPERATIONS` is exactly
`checkpoint`, `kernel reinstall`, `update --apply`, `update --rollback`. Because IP-WS02-12 changes what runs inside
`update --apply`, the reachable behaviour behind its entry was measured: `ws08_r2::below_floor_restoration_by_update_
still_completes_with_the_g5_post_install_suite` — a machine in owner-authorised break-glass restores an authenticated,
certified at-floor release through `update --apply` with the G5 post-install suite, and the marking clears.

`tests/certification/section6.rs` (9) and `srr.rs` (21) are green in both regression modes. Provisioned audit-of-record
probes A2-02, A2-03, A2-05, A2-08 and S6 are identical before/after modulo payload digests (the COMPARE file).
OWNER-DECISION-0007 §1 functions (`resolve_state_root`, `default_state_root`) are byte-identical.

### 5.3 Other behaviour changes inside WS-8's files, stated

- `srr/staging.rs::commit_tree`: the installed `KERNEL_MANIFEST.json` no longer carries an install timestamp
  (`built_at`), so a second machine verifying a clone's pinned release (ARCH-0003 §8) re-commits byte-identical files.
  The manifest's lock binding (`manifest_hash`) never included it; `framework.lock.installed_at` records when. The
  transaction order (§ SRR-R0-L5) is untouched.
- `init`: authority is checked at the ingress itself (`authority::require_with_embedded_kernel` for an uninstalled
  repository — the decision the CLI G0 already takes first), and the floors advance before the conformance run
  (IP-WS02-14).

## 6. IP-WS02-15 — the embedded-kernel cache race, root cause

`kernel::embedded_kernel_dir` staged into `kernels/.staging-<pid>` (shared by every thread of a process) and re-used any
directory holding `KERNEL.yaml` and `.complete`. Now: a cache is re-used only when `cache_matches_listing` holds (every
embedded file present with its digest, no other file, marker naming this listing); each call stages privately
(`.staging-<pid>-<uuid>`), verifies the staged copy, publishes it with one `rename`, keeps a concurrent winner that
verifies, and moves an unverified directory aside rather than deleting it under a reader. A verified path is remembered
per process.

Evidence: unit test `kernel::tests::a_kernel_cache_is_reused_only_when_it_is_exactly_the_embedded_listing` (missing,
extra, altered file, wrong marker → rejected); `ws08_r2::a_corrupt_or_racing_embedded_kernel_cache_is_never_installed`
(a cache in the old defect's exact shape — one file missing, marker present — is replaced, and 6 concurrent `init`
processes on one cold cache all install exactly the embedded payload with no staging leftovers); the integration
builder's `cold_cache_scheduler.py`, unedited, on the repaired binary: **17/17**
(`evidence/concurrency/cold_cache_scheduler.after-cf13dee.out`). The cache check also matters for Option A: a corrupt
cache is no longer the embedded payload, and would otherwise be refused as external material.

## 7. Integration points routed to WS-8

| IP | Status | What was done / why not |
|---|---|---|
| **IP-WS02-12** (G5 at update apply; guard at entry) | done, one deviation | The four-family post-install audit is replaced by a G5 run (`RunOptions::new(G5, "update.apply")`, all checks fresh, recorded in the health ledger, no governed audit record — the update writes its lock/ledger/checkpoint afterwards); UNHEALTHY, RED or any critical refuses and the transaction rolls back. **The G0 entry guard is not taken**: the blocks that govern `update.apply` include findings the update is the remedy for (D006 "overlay file missing: PROJECT_EXCEPTIONS.yaml" on a 4.1.1 installation, whose migration adds it — the entry guard refused the certification update fixture with `HEALTH_HARD_BLOCK`); the IP's purpose (no update applies over a defect the full suite detects) is met after install. Test: `ws08_r2::an_update_over_a_defect_the_full_suite_detects_is_refused_and_rolled_back` (epsilon-r O5-G5-update's DAG cycle: refused `VERIFICATION_FAILED`, lock/kernel/trust as before). Found with it: the abort path restored the protected record *after* rebuilding against the restored bytes, so an aborted update failed its own abort with `KERNEL_TAMPERED`; the record is now restored first. Entry-guard question routed: IP-R2-WS08-5. |
| **IP-WS02-13** (guard + G5 at release build) | done | `release::build` (signature unchanged) runs `scheduler::guard("release.build")` and a G5 run when the canonical root is a governed installation (refusing `RELEASE_HEALTH_REFUSED` on UNHEALTHY/RED); otherwise it records `health: {tier: G5, ran: false, reason}` — stated, never claimed. |
| **IP-WS02-14** (conformance after `record_installed`) | done | `init` advances the floors after commit, byte verification and the authority check, before the conformance run and doctor. WS-2 may now add the installed records to `machine_trust` (IP-R2-WS08-4). |
| **IP-WS02-15** | done | §6. |
| **IP-WS02-16** (`health` in `KERNEL.yaml` payload_dirs) | **not implemented** | Tried and reverted: (a) `framework/health/SKILL_SCENARIO_CHECKS.yaml` contains a planted secret literal (`AWS_SECRET_ACCESS_KEY=AKIAIOSFODNN7EXAMPLE`, SKL-MEMORY-RECONSTRUCTION V1); installed into `governance/kernel/health/` it is flagged by the kernel's own secret scanner, so every fresh install was UNHEALTHY and adoption A7 reported `secrets_isolated: false` (7 certification tests failed: greenfield, failure_injection, brownfield, both migration tests, `repair::cit_auto_simulation_and_secret_redaction`, `repair::smaller_findings_regressions`); (b) `KERNEL.yaml` of 4.1.5 is pinned byte-for-byte by the shipped `release/releases/4.1.5` (`repair3::current_release_payload_identity_and_hygiene`), so a payload-dir change needs a new release version. The runtime's compiled copy keeps serving the checks (integration §4.4). Routed: IP-R2-WS08-6. |
| **IP-2** (release build only when `contracts::verify` is `CONTRACT_SOURCE_BOUND`) | done, one deviation | A present chain that does not verify (any `*_DIVERGED`, `UNREADABLE`, `INVALID`, `LOSSY`, `UNRECOGNISED`) refuses `RELEASE_CONTRACT_NOT_BOUND` before anything is written. A tree that does not carry the whole chain (`*_MISSING`: the payload-only canonical trees release tooling and every root-of-trust probe build from) is recorded as `INCOMPLETE_IN_THIS_TREE` — never as bound — and makes the build release-evidence ineligible. Reason: the kernel payload carries no contract view (`framework/contracts` is not a payload dir), so the IP's stated purpose ("must not ship derived contract views that diverge") is met by refusing divergence; refusing absence broke every probe that builds a release (alpha-r A2-02, AC16-X3 in the first after-run). The built release is also verified as written (`release::verify`) and removed if it does not verify; `PRE_RELEASE_CHECKS.json` is kept beside the immutable manifest. Test: `ws08_r2::a_release_is_built_only_from_a_contract_bound_tree_and_verified_as_written`. |
| **IP-7** (update reads answers through `gates::verified_answer`; init role handling) | done | `apply_update_opts` honours its gate only through `verified_answer` (T2 seal, owner-signed answer re-verified against the human channel, presentation receipt, human-only trigger, revoked decision); a verified declining answer now declines (`"human declined the update"`, unreachable before); verification errors propagate. `init` checks authority at the ingress with WS-3's embedded-kernel resolution. Test: `ws08_r2::update_applies_only_on_a_verified_authorising_answer`. |
| **IP-16** (release artefacts as governed records with `derived_from`/`validated_by`) | **not implemented** | zeta-r `W8-l1-forward-reaches:release` asks for a *product* release record in a governed project's lineage. `release.rs` builds Governance OS kernel releases, which are records of no governed project. A product-release record needs a record type and relation fields (`framework/schemas/record.schema.json`, `records.rs` relation region: WS-4), a creation command and its G0 classification (`cli/src/main.rs`, `control::COMMAND_GUARDS`: WS-3), none of which WS-8 owns. Routed with a concrete split: IP-R2-WS08-7. |

## 8. Regression and probes

### 8.1 Regression (`evidence/regression.sh`; certification split in two parts per invocation only to fit the host)

| Suite | Before (base, default) | After `cf13dee` default | After `cf13dee` xdgcache |
|---|---|---|---|
| `cargo test --lib` | 146 / 0 | **147 / 0** | **147 / 0** |
| `cargo test --test certification` | 100 / 0 | **110 / 0** (34 + 76; `--list` = 110) | **110 / 0** (34 + 76) |

Lib: +1 (`kernel` cache test); two `srr::installation` unit tests replaced because their asserted behaviour is the one
OWNER-DECISION-P2-0002 reverses: `an_unprovisioned_divergence_is_reported_not_enforced` →
`an_unprovisioned_divergence_is_enforced_since_owner_decision_p2_0002`, and
`an_unprovisioned_machine_without_a_record_is_not_blocked` →
`an_unprovisioned_machine_admits_only_a_bootstrap_installation_or_the_embedded_payload`. rustfmt: every touched Rust
file is clean (checked per file via stdin; all were clean at base). No `cargo build` warnings. `CARGO_BUILD_JOBS=2`.

### 8.2 Audit-of-record probes (`evidence/probes-rerun.sh`)

The alpha-r/synthesis probes predate WS-3 and stop at `AUTHORITY_DENIED` unedited, so they are reached exactly as the
integration builder reached them: through a scratch mirror of the tree whose `target/release/gov` runs the integration
builder's adapter `gov-owner-channel-shim.py` (role declaration, owner-signed relay of a rendered gate, absent package
fields — every lifecycle ingress passes through byte-for-byte; logs kept as `*.shimlog`). "Before" runs the identical
probe files from a `git archive` export of the base with its own release build. Results are in §1, §2, §5.2 and the
COMPARE file. Probe preconditions that Option A removes, all re-established on provisioned machines in the
certification suite: S5-update [U0] (installs shipped 4.1.4 unprovisioned), A2-01 [U2] consequences, AC16-X3 X3a
consequences; X3d (TypeError) and A2-01 [U4] (KeyError) break as on the base.

### 8.3 Round-1 WS-8 builder probes (`evidence/ws08-round1-probes.sh`, unedited / integration's derived copies, role shim)

| Probe | Before (base) | After (`cf13dee`) |
|---|---|---|
| WS08-P1 post-install integrity | 15/15 | 14/15 — R2a asserts round 1's report-only unprovisioned divergence, now enforced (§2) |
| WS08-P2 presentation | 8/8 | 8/8 |
| WS08-P3 certification and lock identity | 11/11 | 11/11 |
| WS08-P4 rollback and atomicity | 11/11 | K1-K4 9/9, then K5's precondition (shipped 4.1.4 on an unprovisioned machine) is refused → traceback; the K5 property (abort restores the protected record with the bytes) is measured provisioned by `ws08_r2`'s G5 abort test |

## 9. Integration points for round 3

| ID | Owner / file | Exact change | Why |
|---|---|---|---|
| IP-R2-WS08-1 | docs (unowned: `README.md` §"Quick start" lines 59-60, `docs/COMMANDS.md` `gov init` row, `docs/FIXTURES.md` intro, `docs/ARCHITECTURE.md` §4.8) | Replace the first-run line with "provision, then install": `bin/gov trust provision --anchor <root metadata from the administrator domain>` then `bin/gov init --source <release signed under it> --name …`; state that a machine with no trust anchor refuses external-source kernel ingress (`SRR_UNPROVISIONED_EXTERNAL_SOURCE_REFUSED`) and installs only the binary's embedded payload as a marked bootstrap installation, never presented as current/verified/certified; `docs/COMMANDS.md`: `gov init [--source]` "(on an unprovisioned machine: embedded payload only, BOOTSTRAP)"; `docs/FIXTURES.md`: "every scenario machine is provisioned with the suite's throw-away test root (`tests/certification/common.rs::provision`)". | OWNER-DECISION-P2-0002 requirement 3 (documentation part) |
| IP-R2-WS08-2 | WS-2 `runtime/src/doctor.rs` | `add(crate::srr::installation::doctor_check(&p.root, "<D0xx>"))` (round-1 IP-1, still open) — its `posture` now carries `admission` and the `bootstrap` marking | requirement 2 "doctor/audit disclose it": doctor's payload discloses already; its verdict must not be HEALTHY for a bootstrap or not-admitted installation |
| IP-R2-WS08-3 | WS-2 `runtime/src/verification/` | finding from `crate::srr::installation::posture_of(&p.root)` when `authenticity_established` is false, message = `disclosure`, include `admission` (round-1 IP-2) | audit discloses it |
| IP-R2-WS08-4 | WS-2 `verification/currency.rs::machine_trust_state` | IP-WS02-14 is done: `installed/<product>.json`, `installed/<product>/verified/*` and `floors/<product>.json` are now written before init's conformance run; they may join the `machine_trust` class | currency of kernel trust (BC-P2-35) |
| IP-R2-WS08-5 | WS-2 `scheduler/catalogue.rs` (+ WS-8 `update.rs` once decided) | Decide how `update.apply` meets blocks it is the remedy for: exclude `update.apply` from `RELY_ON_STATE` for kernel/overlay-derived checks (D006/D007 on an older kernel) or make D006 kernel-version-aware; then add `crate::scheduler::guard(p, ops::UPDATE_APPLY, &[])?` after `authority::require` in `apply_update_opts` | IP-WS02-12's entry guard without deadlocking the upgrade path |
| IP-R2-WS08-6 | WS-2 `framework/health/SKILL_SCENARIO_CHECKS.yaml` + release owner (`framework/KERNEL.yaml`) | Remove the planted literal from SKL-MEMORY-RECONSTRUCTION V1 (e.g. `text_parts: ["AWS_SECRET_ACCESS_KEY=AKIA", "IOSFODNN7EXAMPLE\n"]` joined by the check runner), then add `health` to `payload_dirs` in the next release version | IP-WS02-16 |
| IP-R2-WS08-7 | WS-4 (record type/relations) + WS-3 (CLI, G0) + WS-8 (writer) | WS-4: `release` record type (`spec/releases/REL-*.yaml`) with relation fields `derived_from` (tasks/reports) and `validated_by` (audit/evidence); WS-3: a `release record` subcommand classified Write in `COMMAND_GUARDS`; WS-8 then adds `release::record(p, …)` through `control::guard_write` + `records::save_record` | IP-16 / zeta-r `W8-l1-forward-reaches:release` |
| IP-R2-WS08-8 | WS-2 G6 / qualification entry | Record the machine posture with every qualification run and refuse (or mark non-qualifying) a run on a machine where `srr::state::MachineState::read_only(&resolve_state_root()?).is_provisioned()` is false | OWNER-DECISION-P2-0002 requirement 4 |
| IP-R2-WS08-9 | WS-3 `cli/src/main.rs` `KernelCmd::Reinstall` | round-1 IP-3, still open: `.with_pinned_payload(lock["release_hash"].as_str().map(String::from))` on the `AdmissionRequest` | the pin refusal before break-glass entry (BC-P2-38 residual) |
| IP-R2-WS08-10 | WS-5 `runtime/src/status.rs` | round-1 IP-4, still open: `release_trust` from `crate::srr::installation::posture_of(&p.root)` (now with `admission`) | per-project truth on a multi-project machine |
| IP-R2-WS08-11 | WS-1 `tests/governance/capability-evidence-map.yaml` | A2:143 → `srr::verifier::admit` (unprovisioned branch) + `refuse_external_source_if_unprovisioned` + `ws08_r2` refusal/bootstrap tests; A2:146 (unprovisioned) → `installation::anchor_posture` + `ws08_r2` rewrite/unadmitted tests; O5 G5 update → `update::apply_update_opts` + `ws08_r2` G5 test; release build → `release::build` + `ws08_r2` release test | AC-10 evidence owners |
| IP-R2-WS08-12 | every builder writing certification tests (WS-3 in particular) | New scenarios provision (`common::provision` / `setup_fixture`) and install `--source common::signed_source()`; scenarios about the unprovisioned posture use `setup_fixture_unprovisioned` and say so. `ws03::human_answers_come_only_from_the_owner_signed_channel` now runs unprovisioned on the standalone anchor: if P2-ADJ-0001 turns the standalone default off, that test is WS-3's to adapt | harness convention |
| IP-R2-WS08-13 | verifiers / probe authors | Probes that install external material on unprovisioned machines (alpha-r S5-update, A2-01 [U2] consequences, A2-04 unprovisioned rows, AC16-X3 X3a consequences, WS08-P4 K5) no longer reach their consequences under Option A; run them provisioned. Probes that `git archive HEAD` produce the embedded payload when HEAD is the binary's commit, which is admitted as bootstrap by content | probe maintenance |

## 10. Owner-decision questions

None. Every choice above is determined by OWNER-DECISION-P2-0002, D-0007 rule 1, ARCH-0003 §5/§7/§8 and the IPs'
stated purposes. One consequence is recorded for the verifier's attention rather than asked: enforcing the
unprovisioned sub-case means an external-source kernel installed on an unprovisioned machine *before* this change is
`UNADMITTED` after it (mutations refused until the machine is provisioned and verifies the pinned release, or the
project is re-bootstrapped from the binary's payload). That follows from Option A and D-0007 rule 1 ("when T1 cannot
be authenticated, the embedded baseline is substituted and mutating operations fail closed").

## 11. What this run did not do

- It did not edit any file outside WS-8's assignment except the declared additive ones: builder tests calling the new
  harness helpers (P2-HO-0027 "other test files may call them"), one `mod` line in `tests/certification/main.rs`, and
  the fixture READMEs ("the fixtures' provisioning setup"). No `cli/src/main.rs`, `doctor.rs`, `verification/**`,
  `scheduler/**`, `adopt.rs`, docs, `release/verification/`, `release/root-of-trust/`, `release/releases/`,
  `release/orchestration/phase-1/`, `release/capability-baseline/audit-0/` or other `repair-1/<ws>/` change.
  `Governance_OS_Capability_Acceptance_Contract_v3.md` is byte-identical (`4c2df291…5ed3`).
- IP-WS02-16 and IP-16 are not implemented (§7). The update entry guard is not taken (§7, IP-R2-WS08-5).
- No production key material exists or was used: the suite root is the published-seed test material.

## 12. Evidence index (`evidence/`)

| Path | Content |
|---|---|
| `regression.sh`, `regression-before-base-843d79c.out`, `regression-after-cf13dee-{default,xdgcache}-{lib,cert-a,cert-b}.out` | before/after regression; `regression-after-eca268e-*-lib.out` are the same lib suite at the first work commit |
| `r1-heldout/run-r1-heldout.sh`, `r1-heldout-before-base-843d79c.out`, `r1-heldout-after-cf13dee.out`, `r1-heldout-dev-dirty.out` (the `hv_c::c6` catch, superseded), `hv_a_derivation.a1-unpinned.P2-AR-0029.rs.txt`, `failure-messages-before-vs-after.txt` | all four R1 suites unedited, private paths, census, S1/S2 supplementary |
| `r1-invariants.sh`, `r1-invariants-after-cf13dee.out` | the four ingress/floor properties and the §5 allow-list, structurally |
| `probes-rerun.sh`, `probes-before-base-843d79c/`, `probes-after-cf13dee/`, `compare-probes.sh`, `COMPARE-probes-before-base-843d79c-vs-after-cf13dee.out` | audit-of-record probes. `probes-after-dev/` is **superseded**: those probes `git archive HEAD`, and at that time HEAD was still the base while the binary embedded the working tree |
| `ws08-round1-probes.sh`, `ws08-round1-probes-{before-base-843d79c,after-cf13dee}/` | round-1 WS-8 probes (`-after-dev/` superseded, same reason) |
| `concurrency/cold_cache_scheduler.after-cf13dee.out` | integration builder's cold-cache concurrency probe, unedited, 17/17 |

Outputs contain absolute scratch paths of this run. Scripts default their scratch roots to directories named
`p2-ar-0029-*` beside the worktrees.

## 13. Process disclosures

- Model Claude Opus 5 (1M context), `claude-opus-5[1m]`. No sub-agents; the product owner was not contacted; no session
  or agent transcripts, task-output stores or user auto-memory were read. All long commands ran in the foreground.
- One shell command that included `rm -f` of two superseded evidence files was denied by the permission system; it was
  not retried, and those files remain (labelled in §12).
- Development runs that did not reach the final state are kept and labelled (`dev-dirty`, `after-dev`); the claims rest
  on the `cf13dee` runs.
