# P2-AR-0039 — Repair iteration 1, round 3, WS-8: provisioning for T2 continuity, kernel payload/version, update availability

| Field | Value |
|---|---|
| Run | P2-AR-0039, fresh `capability-repair` builder, model Claude Opus 5 (1M context), `claude-opus-5[1m]` |
| Handoffs | P2-HO-0038 (WS-8 round 3), P2-HO-0031 (round-3 common, incl. the availability rule), P2-HO-0020, P2-HO-0010; P2-ADJ-0002; OWNER-DECISION-P2-0002 |
| Items | P2-ADJ-0002 provisioning side + two-machine harness helper; kernel payload/version consistency (WS-8 r2 IP-R2-WS08-6, WS-9 r2 IP-R2-3, WS-7 r2 IP-W7-5); IP-R2-WS08-5 (update entry guard vs its own remedy); IP-R2-WS08-7 (product-release records, WS-8 side); IP-R2-WS08-12/13 (harness convention; external-install probes on provisioned machines); WS-6 r2 IP-R2-10 (update snapshots to the BC-P2-31 store) |
| Base | `53897c1a44157e5af81b176017bc7ded6a63b9cd` (integrated round-2 tree), `product_code_digest 797da37c…1fe1` |
| Branch | `phase2/repair-1-r3-ws08` |
| Product commit | `f9daec1` — **final product state**, `product_code_digest 7a3da864a51b94cae96c914a55b6c10bc2c756b8edd5750a2f1c104d77fbf757`; `governed_state_digest 8f191e39…948f` **unchanged** (no spec/, docs/, D-0007 or Contract v3 change) |
| Work commit | the commit that adds this report, `claims.yaml` and `evidence/` (named in the run report); it changes no product file |
| Release binary | `target/release/gov` at `f9daec1`: sha256 `9788aa80…51e2` |
| Verdict | `READY_FOR_INDEPENDENT_CAPABILITY_VERIFICATION` — builder claims only (Contract v3 O3). Two items are PARTIAL because their other half is another workstream's file this round (the product-release record type and command, WS-4/WS-3; the `M-4.1.5-4.1.6` migration record, WS-9), and the `framework/health` payload step waits on WS-2's literal removal; each is stated with its integration point (§8). |

Every number below is from a run recorded under `evidence/`. Builder tests and probes are regression evidence; acceptance
belongs to fresh independent verifiers.

## 0. Summary

- **P2-ADJ-0002 (provisioning side).** The owner's T2 binding authority is delegated through the provisioned root: the
  root delegates a `t2-binding` role; the owner signs a `t2-binding-authority` document that authorises binding keys by id
  and commitment only; `gov trust bind` installs the authority and one authorised key from the administrator domain into
  protected machine state, **at the location `crate::t2` already seals with**. Every owner machine then seals with the
  same key, so their T2 facts verify on each other after a clone/pull. Unprovisioned, unbound, foreign and hand-edited
  records stay refused. No key or secret is in any repository, and `gov` still never signs. The certification harness
  binds every provisioned scenario machine and has a two-machine helper. The full two-machine scenario passes end to end
  in this tree: gates, owner answers and decisions, CIT state, a plugin registration and governed audit evidence.
- **Kernel payload/version.** The working tree is now the recorded next version, **4.1.6** (`VERSION`, Cargo,
  `KERNEL.yaml`). The immutable `release/releases/4.1.5` is untouched, and its payload differs from this one.
  `KERNEL.yaml` `schema_versions` now lists every versioned schema file at that file's version. `release build` refuses a
  new release when the declared schema versions and the schema files it ships disagree in either direction, or when the
  kernel's own secret scanner flags a payload file. `repair3::current_release_payload_identity_and_hygiene` now asserts
  both the shipped 4.1.5 and the 4.1.6 payload, so it can no longer pass vacuously.
- **Update availability.** `update --apply` takes the G0 entry guard. A block whose check reads what an update replaces
  may be remedied by it: the update proceeds and commits only if the block is gone afterwards
  (`UPDATE_REMEDY_NOT_CLEARED` otherwise). Any other block refuses at entry, typed, before a gate is raised.
- **BC-P2-31.** Update rollback snapshots now live in `.governance-state/update/` and survive deleting everything
  classified as derived. Legacy snapshots are relocated through the store API.
- **R1.** Every prior R1 held-out suite is at its recorded baseline before and after. Census 118/1991 → **119/2022**, with
  0 violations in every §6 activity. The four ingress/floor properties and the §5 allow-list hold exactly, and every
  pre-existing `srr/*.rs` file is byte-identical to the base.

## 1. P2-ADJ-0002 — T2 facts honoured across the owner's provisioned machines (provisioning side)

**Requirement** (P2-ADJ-0002; Contract v3 S6:947-950, E4; D-0007 rule 2; ARCH-0003 §8 "additional machines are
provisioned outside the project repository with the verifier, public root metadata and protected machine/workload
policy"; OWNER-DECISION-P2-0002):
- A T2 fact written by an OS operation on any machine provisioned for the owner is honoured on every other such machine
  after a clone or pull.
- Anything else is refused, typed and observable: a hand edit, an unprovisioned machine, a machine the provisioning did
  not authorise, a forged or modified seal.
- No private key or shared secret is stored in any repository, and no new external dependency class is added.
- The handoff adds WS-8's part: provisioning, plus a two-machine harness helper.

**Why this design.** The adjudication names two conforming designs.
- *Per-machine keys verified by other machines* needs each machine to sign its seals. `gov` verifies and never signs:
  `SRR-R0-L4`, and three R1 held-out suites fail on any signing primitive in product source (AR-0029 `f2`, AR-0031 `d7`,
  AR-0033 `d6`).
- The other design, *a per-owner binding authority delegated through the provisioned root*, is therefore the conforming
  one. The T2 seal is an HMAC (`crate::t2`), so every owner machine must hold the owner's binding key.
- ARCH-0003 §8 puts that key where the root metadata already comes from: the administrator domain, outside every
  repository. This choice keeps the accepted threat model.
  - `crate::t2` already states that a process with the operator's full privileges can read the machine key.
  - Revocation granularity is per authority version, stated in the module documentation.

No trade-off here is left open by the sources, so no owner question is raised.

**What changed**
- `runtime/src/srr/binding.rs` (new, WS-8's `srr/**`):
  - `ROLE = "t2-binding"` and `AUTHORITY_TYPE = "t2-binding-authority"`.
  - `verify_authority(root, env, now)` checks:
    - the type, spec version and product;
    - the `t2-binding` role's signatures at its threshold (`Root::verify_role`);
    - expiry against the declared local clock;
    - exactly one `active` key, well-formed ids and commitments, and no duplicates;
    - an optional `machines` list.
  - `bind(authority, key, project_root)` (`gov trust bind`) checks, in order:
    - the environment carries no authority (`refuse_authority_env`);
    - the break-glass operation guard;
    - neither file is repository content (`T2_BINDING_FROM_REPOSITORY_REFUSED`);
    - the machine is provisioned (`T2_BINDING_UNPROVISIONED`);
    - the root delegates `t2-binding` (`T2_BINDING_NOT_DELEGATED`);
    - the machine is listed, when the authority lists machines (`T2_BINDING_MACHINE_NOT_AUTHORISED`);
    - the key is authorised (`T2_BINDING_KEY_NOT_AUTHORISED`) and matches its commitment (`T2_BINDING_KEY_MISMATCH`);
    - the version is monotonic (`T2_BINDING_AUTHORITY_ROLLBACK`, `…_CONFLICT`).
  - `install_binding` is the one writer:
    - It asks `breakglass::guard_effect_on(…, Effect::TrustPolicyMutation, …)` at the instant of the write
      (OWNER-DECISION-0006 §6 bullet 4).
    - It writes the keyring entry, the exact authority bytes and the binding record, and installs an `active` key as
      `<state_root>/t2-binding/key.json`. That is the file `crate::t2` seals and verifies with.
    - A different key already there (a machine that sealed before it was bound) is kept in the keyring, never
      destroyed.
    - Key files are mode 0600 and durable.
  - `keyring()` is the API for WS-3. It re-verifies the installed authority against the **current** trusted root on
    every call, returns every held key with its standing (`ACTIVE` / `RETIRED` / not authorised), and returns an error
    rather than a stale authority. It is read-only.
  - `status()` reports whether the machine is bound, the authority, whether the sealing key is the authority's active
    key, and held keys with their standing. It never prints key material.
- `runtime/src/srr/mod.rs`: `pub mod binding;`, and `gov trust status` reports `t2_binding`.
- `cli/src/main.rs` (additive): `TrustCmd::Bind { authority, key }`, `g0_label` "trust bind", and the dispatch.
  `runtime/src/orchestration/control.rs` (additive): `outside("trust bind", …)` in `COMMAND_GUARDS`.
- Harness (`tests/certification/common.rs`, WS-8's):
  - The suite root delegates `t2-binding` to a key drawn at run time.
  - `suite_binding()` holds an authority (v1, one active key drawn at run time) and its key file in the administrator
    domain.
  - `bind(g)`.
  - `provision(g)` now means an owner machine: anchor plus binding, for fresh machines only. `provision_anchor_only(g)`
    gives an unauthorised machine.
  - `foreign_owner()` and `provision_foreign(g)` give another owner: another root, another authority, and the current
    payload signed under that root.
  - **Two-machine helper:** `clone_to_machine(src, tag, session, MachineKind::{Owner, AnchorOnly, Unprovisioned,
    ForeignOwner})` gives a Git clone on a new simulated machine with its own `XDG_STATE_HOME` and its own `HOME`.
    `verify_pinned_release(g, source)` implements ARCH-0003 §8. `pull_from(dst, src)` pulls.
  - `srr_material::ephemeral_key/ephemeral_secret`: the new test material is drawn at run time and stored nowhere, so
    not even a published secret is added to this repository.

**Product checks that own it:**
- `srr::binding::bind` at the provisioning ingress.
- `srr::binding::keyring` and `status` at use time.
- `crate::t2` (unchanged) verifies every T2 record against the installed key at every consumer.

**Tests** (`tests/certification/ws08_r3.rs`):
- `t2_facts_written_on_one_owner_machine_are_honoured_on_the_others_and_refused_elsewhere`:
  - **Setup on A (owner).**
    - A gate is created and answered by the owner (owner-signed), recording a sealed decision.
    - A governance CIT is proposed, its gate answered and approved.
    - A plugin registration is approved through its gate.
    - `gov audit` writes sealed governance-suite evidence.
    - The work is committed.
    - The binding key appears in neither the tree nor the history (`git grep`, `git log -S`).
  - **B (owner clone, own state and `HOME`).**
    - Pulls a commit from C.
    - The gate is `VERIFIED` and its owner answer verifies.
    - The CIT approved on A executes on B (`COMMITTED`).
    - The plugin registered on A runs.
    - D033 reports exactly 1 record not honoured: C's gate.
  - **C (same root, not bound).**
    - The gate is not `VERIFIED` and its answer does not verify.
    - `cit execute` is refused `T2_UNBOUND`.
    - The plugin does not run.
    - D033 discloses the owner's records.
    - C then writes a gate of its own.
  - **D (unprovisioned).** `trust bind` is refused `T2_BINDING_UNPROVISIONED`, with remediation "provision". The gate is
    not honoured.
  - **E (another owner).** The gate is `FOREIGN`, `cit execute` is refused `T2_UNBOUND`, and the owner's authority is
    refused against E's root (`SRR_THRESHOLD_NOT_MET`).
  - **On B again.** C's pulled gate is `FOREIGN` and listed `honoured: false`. A hand edit of the owner-sealed gate is
    `BROKEN` and its answer no longer verifies.
- `a_t2_binding_authority_installs_only_from_the_owners_provisioned_root` covers every refusal above, one by one:
  - unprovisioned;
  - no delegation;
  - an intruder signer;
  - a tampered document;
  - expired;
  - an unauthorised key;
  - an id/commitment mismatch;
  - an unlisted machine;
  - an authority or key file inside the repository;
  - an environment variable.

  It also covers:
  - the machine-local key kept on binding;
  - no key material printed by `bind` or `trust status`;
  - idempotent re-bind;
  - rollback and same-version conflict;
  - rotation (v3: the sealing key becomes k2, and k1 is `RETIRED`), then v2 refused as a rollback.
- `a_binding_authority_is_not_installed_below_floor`: on a machine marked `DEGRADED — RECOVERY ONLY`, `trust bind` is
  refused `SRR_BELOW_FLOOR_REFUSED` and the sealing key is unchanged.
- Lib: `srr::binding::tests::key_ids_match_the_t2_primitive_and_commitments_are_domain_separated`.

**Limits (stated):**
- `crate::t2` (WS-3's) still verifies against the single installed key, so two things are left to the consumer:
  - Seals made under a `RETIRED` key are not yet honoured after a rotation.
  - A machine whose authority stops verifying (for example after a root succession that drops the delegation) keeps
    honouring the installed key until the consumer consults `keyring()`.

  This is WS-3's side, routed as IP-R3-WS08-1. `trust status` already reports both states.
- Records a machine sealed before it was bound become not-honoured on that machine. By P2-ADJ-0002 they were written by
  a machine the provisioning had not authorised. An administrator who wants them kept can issue the authority for that
  machine's existing key; `bind` accepts a `key.json`-format key file.

## 2. Kernel payload/version consistency (IP-R2-WS08-6 release part, WS-9 IP-R2-3, WS-7 IP-W7-5)

**Requirement** (handoff):
- `KERNEL.yaml` `schema_versions` must match the actual schema files.
- Decide how the `framework/health` payload and the schema changes are carried, given that `release/releases/4.1.5` is
  immutable. The branch is `release/4.1.6-rc1`, and the recorded next version is 4.1.6.
- Keep `repair3::current_release_payload_identity_and_hygiene` meaningful, and never edit `release/releases/**`.
- Coordinate `M-4.1.5-4.1.6` with WS-9.

**Decision: the working tree is 4.1.6.**
- Phase-2 repairs changed 18 schema files and several policies. The working tree's payload is therefore no longer the
  shipped 4.1.5 payload, yet it still carried the version 4.1.5.
- Two payloads with one version is an identity collision. For example, `update --check` from an installed shipped 4.1.5
  to this binary compared versions and said "nothing to do", so no path led to the repaired payload.
- `release/releases/4.1.5` pins 4.1.5's `KERNEL.yaml`, so the fix cannot be made under 4.1.5.
- The recorded next version, 4.1.6, is the consistent choice. `M-4.1.5-4.1.6` becomes the operative update path.

**What changed**
- `framework/KERNEL.yaml`:
  - `version`, `cli_version` and `runtime_version` are `4.1.6`.
  - `supported_from_versions` gains `4.1.5`.
  - `schema_versions` lists **all 62 schema files that declare `x-schema-version`**, each at its file's version: the 27
    previously listed, 9 of them corrected, plus 35 added. `governance-capability-acceptance` declares none.
- `runtime/src/lib.rs`: `VERSION`, `CLI_VERSION` and `RUNTIME_VERSION` are `4.1.6`. `INDEX_VERSION` is untouched.
  `Cargo.toml` `[workspace.package] version` is `4.1.6`, and `Cargo.lock` follows (§9: declared exceptions).
- `runtime/src/kernel.rs`:
  - `schema_version_problems(kernel_dir)` finds every declared entry without its file or with another version, and every
    versioned file that is not declared.
  - `payload_secret_hits(kernel_dir)` runs the payload's own `SECURITY_POLICY` scanner over every payload file and
    reports path, line and pattern, never the matched text.
- `runtime/src/release.rs`, `build`:
  - Before writing a **new** release, it refuses `RELEASE_KERNEL_INCONSISTENT` or `RELEASE_PAYLOAD_SECRET` and removes
    the partial output.
  - Reproducing a shipped version reports and refuses nothing.
  - Both results are recorded in `PRE_RELEASE_CHECKS.json` (`kernel_payload`).
- **`framework/health`: decided to ship in the 4.1.6 payload once it is clean under the kernel's own scanner.**
  - Today it carries WS-2's planted `AKIA…EXAMPLE` literal. Shipped, every installation would carry and flag it (D011
    critical; round 2 measured 7 certification failures). So `health` stays out of `payload_dirs`, and the runtime's
    compiled copy serves the checks.
  - WS-2 removes the literal in round 3.
  - The decision is **enforced, not remembered**:
    `ws08_r3::the_health_checks_ship_in_the_payload_exactly_when_the_kernel_scanner_finds_them_clean` fails as soon as
    `framework/health` is clean and `health` is not in `payload_dirs`, and fails as long as it is flagged and shipped.
    `release build` refuses a flagged payload in either case.
  - Integration step: IP-R3-WS08-5.
- `M-4.1.5-4.1.6` (WS-9's file) is **not edited**. It is schema-valid, chains 4.1.5 → 4.1.6 and passes its substance
  check: the overlay templates are unchanged since 4.1.5, apart from the one delta WS-6 and WS-9 declared. What WS-9
  completes is in IP-R3-WS08-6.

**`repair3::current_release_payload_identity_and_hygiene`, rewritten to stay meaningful.**
- The old body looked for `release/releases/<VERSION>`. With 4.1.6 it would have skipped every identity assertion.
- It now asserts the **last shipped release**, which is the highest under `release/releases/`, today 4.1.5:
  - both manifests agree;
  - `KERNEL.yaml` = `KERNEL_MANIFEST` = manifest `schema_versions`;
  - provenance;
  - no migration substance problems;
  - its `KERNEL.yaml` is byte-identical to `framework/KERNEL.yaml` at its recorded release commit, which is an ancestor
    of HEAD;
  - `release verify` passes;
  - it reproduces byte-identically;
  - building over it is `RELEASE_IMMUTABLE`, and `release/releases` is unchanged.
- It asserts the **working tree's payload**:
  - its versions equal the binary's;
  - no schema problems;
  - it is newer than the shipped release, supports updating from it, and has a migration from it;
  - a release built from it into scratch verifies, carries exactly this `KERNEL.yaml`, and has consistent
    `schema_versions` everywhere;
  - its identity differs from 4.1.5;
  - migration substance is clean;
  - the kernel scan is clean;
  - `release/releases` is untouched.
- When the current version is itself cut, the old equality assertion applies again.
- The duplicate-key hygiene loop is unchanged.

**Tests:**
- `ws08_r3::the_next_kernel_payload_is_version_consistent_and_release_build_refuses_drift`:
  - version, CLI, runtime and embedded agree;
  - the payload is distinct from shipped 4.1.5;
  - a control build is ok;
  - each of these is refused `RELEASE_KERNEL_INCONSISTENT`, with nothing left behind: a bumped schema file, a declared
    version the file lacks, an undeclared versioned schema;
  - a planted secret (assembled at run time) is refused `RELEASE_PAYLOAD_SECRET` without echoing it.
- `ws08_r3::the_health_checks_ship_…` (above).
- Lib: `kernel::tests::the_payload_declares_the_schema_versions_it_ships_and_carries_no_secret`.
- `srr.rs:724`: the literal `"4.1.5"` becomes `gov_runtime::VERSION` (the release the machine verified is the current
  payload). This is a value change forced by the version, and the property is unchanged.
- `common::sequence_of("4.1.5") = 15`.

**Consequence for audit-of-record probes.** Several of them build "the current release" from a `git archive HEAD` copy
with `--version 4.1.5`, and now stop at `VERSION_MISMATCH`. §6 gives the labelled derived copies that restore their
premise, and their before/after results.

## 3. IP-R2-WS08-5 — the `update --apply` entry guard and its own remedy (availability rule)

**Requirement:**
- IP-WS02-12 asked for G0 at the entry of `update.apply`.
- Round 2 found the guard refusing the very update that adds the missing file (D006 on a 4.1.1 installation).
- P2-HO-0031's availability rule:
  - a hard-block refuses the operations whose reliance it protects, scoped to what the failing check governs;
  - work that remedies a block stays available;
  - a remedy that does not clear its block does not commit;
  - every refusal is typed and names the block and its scope.
- The handoff: implement this against WS-2's availability API.

**What changed** (`runtime/src/update.rs`):
- `update_can_remedy(check)`, from the catalogue's own declared inputs (`scheduler::catalogue::get(check).deps`): a
  check reading anything an update substantively replaces may be remedied by it. That covers `@kernel`, `@overlay`,
  `@files` (which contains those), the lock, the kernel and overlay classes, and `machine_trust`. Derived outputs the
  update only regenerates, such as the index and adapters, cannot repair what they derive from.
- `entry_guard(p)` calls the one G0 API (`scheduler::guard(p, ops::UPDATE_APPLY, &[])`, which re-evaluates stale
  blocks). It partitions `HEALTH_HARD_BLOCK` details:
  - blocks the update may remedy are carried;
  - any other block refuses **at entry**, after `update --check` and before a Human Decision Gate is raised or anything
    is staged. The refusal is `HEALTH_HARD_BLOCK`, and its details carry `blocks` (check, severity, scope, operations),
    `remediable_by_this_update`, the rule and a remediation.
- After install, doctor and G5 re-run, and any carried block still active refuses `UPDATE_REMEDY_NOT_CLEARED`. The
  transaction then rolls back through the existing abort path.
- The result records `remedied_blocks`. The old comment explaining why no entry guard was taken is removed.

**Measured on the 4.1.1 update fixture:**
- The blocks that governed `update.apply` were `schema_invariants` ("overlay file missing: PROJECT_EXCEPTIONS.yaml",
  "kernel policy missing: LEARNING_POLICY/ARCHIVE_POLICY") plus D006 and D007. All are remediable.
- The update passes, clears them, and records them as `remedied_blocks`.
- A records-only block (D023, a record that does not parse) refuses at entry, and no gate is raised.

**Tests:**
- `ws08_r3::update_entry_guard_is_scoped_and_snapshots_survive_derived_state_deletion`: the D023 refusal with scope and
  rule, no gate raised, lock unchanged; the remedy path cleared and recorded.
- Unchanged and passing: `update::…` (4.1.1 → current), `ws08_r2::an_update_over_a_defect…` (G5 refusal and rollback),
  `ws08_r2::below_floor_restoration_by_update…` (§5 allow-list path), `ws08::…`.

**Integration.**
- WS-2 is designing the catalogue's remedy and block-scope semantics in parallel. When the catalogue declares remedies,
  `update_can_remedy` is replaced by that declaration (IP-R3-WS08-4).
- The host contract stays as is: entry refusal of non-remediable blocks, carry-and-verify of remediable ones.

## 4. BC-P2-31 — update snapshots in the state store (WS-6 r2 IP-R2-10)

**Requirement:**
- Rollback material survives the deletion of everything classified as derived (Contract v3 B1:188, B3:202; A0-D6-01).
- The writer resolves its location through `paths::store_path` and relocates the legacy directory once.

**What changed** (`update.rs`):
- `snapshot_base` runs `paths::relocate_legacy(root, "update-snapshots")` (a legacy directory moves once, and
  `STATE_LOCATION_CONFLICT` refuses rather than overwrites), then `paths::store_path(root, "update-snapshots")`, which is
  `.governance-state/update`.
- `snapshot_dir` also ensures the self-ignoring state directory exists.
- Both the apply and rollback paths use them, and the `SNAPSHOT_MISSING` message names the new location.
- `release.rs` `rollback_procedure` text names the new location. This affects new manifests only; reproduction compares
  hashes, not this text.

**Tests:**
- `ws08_r3::update_entry_guard_is_scoped_and_snapshots_survive_derived_state_deletion`:
  - the snapshot is at `.governance-state/update/4.1.6` and not at the legacy location, and `git status` is clean;
  - **the whole `.governance-runtime/` is deleted**, then the rollback (refused below floor, then break-glass) restores
    4.1.1 and consumes the snapshot;
  - a snapshot moved to the legacy location is relocated by the next rollback.
- `ws08.rs`: the "no snapshot after a refused update" assertion checks both locations.
- `ws08_r2`: its planted legacy snapshot now also exercises relocation, unchanged.

**Probe:** the S5 provisioned derivation `[U2]` shows the snapshot at `.governance-state/update/4.1.5` after and at the
legacy location before. That is its only difference before/after (§6).

## 5. IP-R2-WS08-7 — product-release records (WS-8 side)

**Requirement:** zeta-r `W8-l1-forward-reaches:release` needs a product release record in a governed project's lineage.
- WS-4: record type and relation fields.
- WS-3: the command and its G0 class.
- WS-8: the writer.

**What changed** (`runtime/src/release.rs`):
- `compose_product_release(store, spec)` composes a `release` record, `REL-<version>`, with `derived_from` (tasks,
  reports, features, requirements, decisions) and `validated_by` (audit, report, test-obligation, scenario). It refuses:
  - `RELEASE_LINEAGE_INCOMPLETE`: no lineage;
  - `RELEASE_LINEAGE_UNKNOWN_RECORD`: unknown references;
  - `RELEASE_LINEAGE_WRONG_TYPE`: wrong types;
  - `T2_UNBOUND`: health evidence not honoured;
  - `RELEASE_RECORD_EXISTS`: an existing version, because records are immutable.
- `record_product_release(p, spec)`:
  - takes G0 (`guard_write(p, "release record")`) and authority (`mutate_spec_other`, WS-3 may choose another class);
  - resolves the canonical path **only** through `records::record_path_for("release", id)`, which is typed
    `RECORD_TYPE_UNKNOWN` until WS-4 registers the type, and nothing is written;
  - T2-seals the record (`release record`) and saves it through `records::save_record`.

**Test:** lib `release::tests::a_product_release_is_composed_only_inside_its_lineage`.

**Limit, and why PARTIAL:**
- The type (WS-4 `TYPE_DIR`/`TYPE_PREFIX`) and the command (WS-3) are other workstreams' files this round, so the
  writer is not exercisable end to end in this tree.
- W8 forward reachability also depends on the direction WS-4's graph gives `DERIVED_FROM`/`VALIDATED_BY`.
- IP-R3-WS08-8 gives the exact wiring.

## 6. IP-R2-WS08-12/13 — harness convention and external-install probes on provisioned machines

**IP-R2-WS08-12:**
- The convention is written at `common::setup_fixture`: provision (now including the owner's binding authority), install
  `--source signed_source()`, use `setup_fixture_unprovisioned` for scenarios about the unprovisioned posture, and use
  `clone_to_machine` for other machines.
- Every scenario test of the 142 follows it. The root-of-trust tests in `srr.rs` and `section6.rs` provision their own
  test roots by design, because their subject is the root itself.

**IP-R2-WS08-13** (`evidence/derived-probes/`, **labelled derived copies**; the audit of record is never edited):

- `S5-update.provisioned.P2-AR-0039.py` is a hand-written derivation. S5 stops at `[U0]` in every tree since Option A,
  because it installs the shipped 4.1.4 unprovisioned. This copy runs all nine update bullets on provisioned machines
  (every change is marked `# DERIVED:`):
  - the throw-away `hc_root` root;
  - the shipped 4.1.4/4.1.5 signed at sequences 14/15;
  - `[U5]` refused below the high-water, then run under break-glass;
  - `[U6]` built on a separate build machine, because a release build is refused below floor;
  - `[U7]` on a second provisioned machine, signed at 17, with its gate answered;
  - `[U8]` provisioned with a human-gate root, the unsigned 4.1.6 built without `CERTIFIED`, and snapshots looked for at
    both locations.

  Results: base and after both run all bullets (exit 0). They are **identical except the snapshot location** (§4).
  After:
  - `[U2]`: 4.1.4 → 4.1.5 applied, overlay preserved, spec untouched, ledger written.
  - `[U5]`: `SRR_BELOW_FLOOR`, then a break-glass rollback to 4.1.4, the overlay byte-identical, the machine marked
    `DEGRADED — RECOVERY ONLY`.
  - `[U6]`: `UPDATE_UNSUPPORTED`, and the downgrade reported.
  - `[U7]`: `OVERLAY_INVALID`, rolled back automatically, kernel and lock restored.
  - `[U8]`: an unsigned target refused `SRR_RELEASE_UNVERIFIED`, no snapshot left at either location, and the rollback
    `SNAPSHOT_MISSING`.
- `derive_probes.py` and `run-derived.sh` handle the probes whose premise the 4.1.6 decision changes: A2-01, A2-03, A2-04,
  A2-05, S5 and AC16-X3.
  - They pass `version="4.1.5"` to the canonical copies that feed a `--version 4.1.5` build, and import the probe
    library from the tree under test.
  - In A2-04 `[L3]`, the unprovisioned row installs the embedded payload itself, as its premise was ("a HEAD copy is the
    embedded payload").
  - The diff against the originals is `00-derivation-diff.out`.
  - Derived, before vs after, normalised (`COMPARE-probes-…out`):

  | Probe | Before vs after |
  |---|---|
  | A2-03 | 0 lines differ |
  | A2-05 | only the `SNAPSHOT_MISSING` location and a truncated init line differ |
  | A2-01 | `[U3]` embedded 4.1.5 → 4.1.6 |
  | AC16-X3 | `X3c` PASS lines identical except the embedded baseline version (4.1.6) and one extra D005 note in an already-UNHEALTHY line; `X3a`/`X3d` still end in the TypeError they end in at the base |
  | A2-04 | version labels. `[L1]`/`[L3]` `release_commit` is `unverified` for the relabelled authentic payload: it is no longer byte-identical to the binary's embedded payload, so no commit is established for it (BC-P2-37, "recorded, not invented"). The bootstrap row is present |

- The other probes' consequences under Option A cannot exist in either posture. A tampered release is refused at
  ingress, unprovisioned (A2-01 `[U2]`, AC16-X3 X3a) and provisioned (A2-02 `[P2]`, which runs in both trees). Where they
  are measured provisioned:

  | Consequence | Where it is measured provisioned |
  |---|---|
  | WS08-P4 K5 | `ws08_r2::an_update_over_a_defect_the_full_suite_detects_is_refused_and_rolled_back` |
  | Unprovisioned lock rows | `ws08_r2` bootstrap tests |

- Unedited probes, before vs after:
  - A2-08: identical.
  - S6: version labels only.
  - A2-02: identical apart from two truncated lines. It ends at `[P9]` in **both** trees; at the base, `[P8]` adopt
    already needs WS-9's review verdict.
  - A2-03, A2-04, A2-05, AC16-X3: stop at `VERSION_MISMATCH`, which is what the derived copies address.
  - S5: stops at `[U0]` in both.

## 7. R1 preservation (AC-14): every prior R1 held-out suite, unedited, measuring this worktree

- The runner is `evidence/r1-heldout/run-r1-heldout.sh`, WS-8's round-2 runner split into phases.
- The private scratch root is `…/scratchpad/p2-ar-0039-r1-heldout`. Its links `wt/srr1-r1-verify{,-2,-3,-4}` point at
  this worktree only.
- Each header records HEAD and 0 product files differing.
- Every copied suite file is `cmp`-identical: 26 lines `identical`.

| Suite | Recorded baseline | Before (base `53897c1`) | After (`f9daec1`) |
|---|---|---|---|
| AR-0027 (`4.1.6-r1`) | 26 / 3 (`b1`, `b2`, `d3`) | 26 / 3 (same) | **26 / 3** (same) |
| AR-0029 (`4.1.6-r1-2`) | 26 / 2 (`b3`, `b6`); `ho_f` does not compile | 26 / 2 (same); `ho_f` n/c | **26 / 2** (same); `ho_f` n/c |
| AR-0031 (`4.1.6-r1-3`) | 27 / 7 (`a1`, `a5`, `a8`, `b6`, `c2`, `c3`, `d2`) | 27 / 7 (same) | **27 / 7** (same) |
| AR-0033 (`4.1.6-r1-4`) | 31 / 0 (30 / 1 on any larger tree) | 30 / 1 (`hv_a::a1` size pin) | **30 / 1** (`hv_a::a1` size pin only) |
| **Census** (AR-0033 `hv_a::a1` walk) | 84 files / 740 functions | **118 / 1991** | **119 / 2022** |

- The census grew by one file, `srr/binding.rs`, and 31 functions.
- **`hv_a::a1`** is run as P2-HO-0020 item 7 prescribes. The labelled copy `hv_a_derivation.a1-unpinned.P2-AR-0039.rs.txt`
  differs from the held-out file only in the two size assertions, and the diff is printed in each output. It finds
  **0 violations in every §6 activity**:

  | Activity | Derived | Writers | Exempt |
  |---|---|---|---|
  | human_gate_create | 48 | 43 | 1 |
  | human_gate_approve | 1 | 1 | — |
  | release_certification | 1 | 1 | — |
  | trust_policy_mutation | 8 | 1 | — |
  | privileged_plugin_acquisition | 9 | 2 | — |
  | floor_lower_or_reset | 3 | 1 | — |
  | present_below_floor_release_as_current | 1 | 1 | — |

  `human_gate_create` rose by one against base, from 47/42: the new record writer, accepted through `save_record`.
- AR-0033's own `derive.py`, with only its ROOT line changed, agrees under all three splitter configurations, with 0
  violations.
- **Failure messages** of the unedited suites, normalised, are 42 lines before, 42 after and 42 in the round-2
  integration run. Both diffs are empty (`failure-messages-before-vs-after.txt`).
- **The four ingress/floor properties and the §5 allow-list** (`r1-invariants-after-f9daec1.out`, WS-8's round-2
  script, unchanged):
  - `srr::admit(` has 5 sites, `install_kernel(` 5, `by_admit(` one call, and there is no `AuthenticatedRelease` literal
    outside `verifier.rs`.
  - `is_backward_capable`, `may_use_protected_installed_record` and the step 9-10 floor/break-glass block are
    byte-identical to base.
  - `effective_floor_sequence()` occurs 3 times.
  - `SRR_BREAK_GLASS_REQUIRES_AUTHENTIC_RELEASE` is present.
  - No floors writer exists outside `state.rs`.
  - `breakglass.rs` is byte-identical, and `PERMITTED_OPERATIONS` is exactly checkpoint, kernel reinstall,
    update --apply and update --rollback.
  - `kernel_trust.rs` is free of SRR verdict vocabulary.
  - There is no signing capability.
  - `resolve_state_root` and `default_state_root` are byte-identical.
- **Every pre-existing `srr/*.rs` file is byte-identical to the base**, as are `kernel_trust.rs`, `lock.rs`, `init.rs`,
  `recovery.rs`, `records.rs`, `tools.rs` and `capabilities/` (`identity-and-scope.out`).
- **The new code avoids the held-out suites' needles.** Product source, tests included, carries none of the signing
  needles (`SigningKey`, `ed25519_dalek::Signer`, `PRIVATE KEY`, `.sign(`, `SecretKey`, `from_keypair_bytes`), no
  relaxation switch, and no `resolve_state_root() else` shape.
- `tests/certification/section6.rs` (9) and `srr.rs` (21) are green in both regression modes.

## 8. Integration points (round 3 → integration)

| ID | Owner / file | Exact change | Why |
|---|---|---|---|
| IP-R3-WS08-1 | WS-3 `runtime/src/t2.rs` | Keep sealing with `<state_root>/t2-binding/key.json`, which binding installs as the authority's active key. In `verify_value`, when a seal's `key_id` is not the installed key, consult `crate::srr::binding::keyring()`: `Some(k)` with `k.standing(id) == Some(Retired)` and `k.verification_key(id)` present means verify under that key, and on success `Verified` (note the authority). Otherwise keep `Foreign`. When `keyring()` returns `Err` (installed authority no longer verifies against the trusted root), do not honour seals made under the installed key either (`KeyUnavailable` with that reason). If WS-3 moved the key location this round, change `srr::binding`'s `DIR`/`CURRENT_KEY_FILE` to match (one place). `ws08_r3::t2_facts_…` guards the result. | P2-ADJ-0002 consumer side: retired keys honoured after rotation; a revoked or unverifiable authority refused |
| IP-R3-WS08-2 | WS-3 docs | `docs/COMMANDS.md`: `gov trust bind --authority <doc> --key <file>` (administrator; P2-ADJ-0002); `gov trust status` → `t2_binding`. `docs/ARCHITECTURE.md`: the owner's T2 binding authority (§1 of this report, "Why this design"). `docs/RELEASE.md:53`: snapshots are in `.governance-state/update/<version>/`. The working tree is 4.1.6. IP-R2-WS08-1 (provision then install) now also says "bind". | documentation truthful |
| IP-R3-WS08-3 | WS-2 `doctor.rs` D033 / `os_binding_integrity` | Report `crate::srr::binding::status()`. On a bound machine a `FOREIGN` record was written by a machine the owner did not authorise (disclose as such). `sealing_key_is_authority_active_key == false` or an `authority_error` is a finding (medium). | observable T2 continuity state |
| IP-R3-WS08-4 | WS-2 `scheduler/catalogue.rs` (then WS-8 `update.rs`) | When the catalogue declares which operations remedy a check's block, replace `update::update_can_remedy` with that declaration. `entry_guard`'s contract (refuse others at entry, carry remediable ones, `UPDATE_REMEDY_NOT_CLEARED` after install) stays. | one availability API |
| IP-R3-WS08-5 | integration builder, after WS-2's literal removal | Add `  - health` to `framework/KERNEL.yaml` `payload_dirs`. `ws08_r3::the_health_checks_ship_…` fails until done once `framework/health` is clean. Also: `EMBEDDED` payload hash and `signed_source` follow automatically. | the 4.1.6 payload carries the scenario checks with the skills they verify (IP-WS02-16) |
| IP-R3-WS08-6 | WS-9 `migrations/M-4.1.5-4.1.6.yaml` | Update `description`: 4.1.6 is now the working-tree version and this is the operative 4.1.5 → 4.1.6 migration, no longer "prepared". Keep `to_version: 4.1.6`. Declare or deliver any further overlay-template delta (today only WS-6's REPOSITORY_CONTRACT rule, already declared). Review the 18 schema-version changes since 4.1.5 (§2 evidence: model-routing-overrides, task, decision, upstream-packet, context-packet, index-manifest, tool, plugin-descriptor, plugin-registry, adoption-baseline, audit, experiment, human-gate, migration-catalogue-entry, report, research, scenario, worker-return) for record-level migration operations installed 4.1.5 projects need. | version/migration coordination |
| IP-R3-WS08-7 | every workstream that bumps a schema's `x-schema-version` this round | Mirror it in `framework/KERNEL.yaml` `schema_versions` (the release build, the kernel unit test, `repair3::…` and `ws08_r3::the_next_kernel_payload_…` refuse drift). A new versioned schema file is added there too. | payload/version consistency |
| IP-R3-WS08-8 | WS-4 `records.rs` + schema; WS-3 `cli/src/main.rs` + `COMMAND_GUARDS` | WS-4: `("release", "spec/releases")` in `TYPE_DIR`, `("release", "REL")` in `TYPE_PREFIX`, a `release` record schema; `DERIVED_FROM`/`VALIDATED_BY` traversal so W8 forward lineage reaches `REL-*`. WS-3: `gov release record --version V --title T --derived-from IDS --validated-by IDS [--notes N]`, label `release record`, class Write/`mutate_spec_other` (or WS-3's choice: then change the one `authority::require` line in `release::record_product_release`), dispatching to `gov_runtime::release::record_product_release(&p, &ProductRelease{…})`. | IP-R2-WS08-7 / zeta-r W8 |
| IP-R3-WS08-9 | verifiers / probe authors | Audit-of-record probes that build "the current release" as `--version 4.1.5` from a HEAD copy (A2-01, A2-03, A2-04, A2-05, S5 `[U8]`, AC16-X3) need the derived premise (`evidence/derived-probes/derive_probes.py`). S5's update lifecycle runs provisioned in `S5-update.provisioned.P2-AR-0039.py`. Probes looking for leftover update snapshots must look in `.governance-state/update/`. | probe maintenance |
| IP-R3-WS08-10 | WS-1 `tests/governance/capability-evidence-map.yaml` | S6/E4 cross-machine T2 continuity: `srr::binding::{bind, keyring}` + `ws08_r3::t2_facts_…`, `…installs_only_from_the_owners_provisioned_root`, `…not_installed_below_floor`. Release payload consistency: `kernel::{schema_version_problems, payload_secret_hits}`, `release::build` + `ws08_r3::the_next_kernel_payload_…`, `repair3::current_release_…`. L4/O5 update availability: `update::entry_guard` + `ws08_r3::update_entry_guard_…`. B1/B3 update snapshots: `update::snapshot_base` + same test. | AC-10 evidence owners |

## 9. Files changed, and the declared exceptions

**WS-8's own files:**
- `runtime/src/srr/binding.rs` (new) and `srr/mod.rs`.
- `runtime/src/kernel.rs`, `runtime/src/release.rs` and `runtime/src/update.rs`.
- `framework/KERNEL.yaml`.
- Harness: `tests/certification/common.rs` and `srr_material.rs`.
- Tests: `tests/certification/ws08_r3.rs` (new), `ws08.rs`, and `main.rs` (one `mod` line).

**Declared exceptions:**
- `runtime/src/lib.rs`: the three version constants (plus a comment). This is not a `pub mod` line. It is the release
  identity the version decision routed to WS-8 requires, and it changes no other line.
- `Cargo.toml` `[workspace.package] version`, and `Cargo.lock` (the two package versions).
- `cli/src/main.rs`: additive `TrustCmd::Bind`, its `g0_label` arm and its dispatch.
- `runtime/src/orchestration/control.rs`: one additive `COMMAND_GUARDS` entry.

**Builder tests changed, and why:**
- `tests/certification/repair3.rs`: §2. The test is rewritten so it cannot pass vacuously, and it asserts strictly more.
- `srr.rs`: one literal becomes `VERSION`.
- `update.rs`: the diagnostic message only.
- `ws08.rs`: both snapshot locations.

**Not touched:** `release/releases/**`, `release/verification/`, `release/root-of-trust/`, `release/orchestration/phase-1/`,
`audit-0/`, any other `repair-1/` directory, and the Contract v3 source (`4c2df291…5ed3`). rustfmt is clean on every file
this run authored. The files `rustfmt` still reports (`srr/breakglass.rs`, `srr/metadata.rs`, `section6.rs`, the rest of
`srr.rs`) were already unformatted at the base and are deliberately left byte-identical.

## 10. Regression (`evidence/regression/`, `evidence/regression.sh`)

| Suite | Before (base, default) | After `f9daec1` default | After `f9daec1` xdgcache |
|---|---|---|---|
| `cargo test --lib` | 207 / 0 | **210 / 0** | **210 / 0** |
| `cargo test --test certification` | 136 / 0 (35 + 48 + 53) | **142 / 0** (35 + 48 + 59; `--list` = 142) | **142 / 0** (35 + 48 + 59) |

- Lib +3: `srr::binding`, `kernel` and `release` unit tests.
- Certification +6: all in `ws08_r3`.
- `CARGO_BUILD_JOBS=2` throughout, and no `cargo build` warnings.
- `regression-dev1-*` are superseded development runs on the uncommitted tree.

## 11. Owner-decision questions

None.
- P2-ADJ-0002 names the delegated binding authority as a conforming design, and R1 (`gov` never signs) excludes the other
  one, so no open trade-off remains.
- The version is the recorded next version.
- The `health` payload decision follows IP-WS02-16's stated purpose and the kernel's own scanner.

## 12. Evidence index (`evidence/`)

| Path | Content |
|---|---|
| `regression.sh`, `regression/` | before (base) and after (`f9daec1`, default and xdgcache) lib + certification (3 parts, `--list`); `dev1` superseded |
| `r1-heldout/` | runner, labelled `hv_a` copy, `r1-heldout-before-base-53897c1.out`, `r1-heldout-after-f9daec1.out` (suites, census, S1, S2), `failure-messages-before-vs-after.txt` (+ `fm-*.txt`, `failure_messages.py`) |
| `r1-invariants.sh`, `r1-invariants-after-f9daec1.out` | the four ingress/floor properties and the §5 allow-list |
| `identity-and-scope.out` | digests, binary sha256, change list, protected-path and byte-identity checks |
| `probes-rerun.sh`, `probes-{before-base-53897c1,after-f9daec1}/` | WS-8's audit-of-record probe set, unedited, via the integration adapter (base = `git archive` export of `53897c1` with its own release build) |
| `derived-probes/` | `derive_probes.py`, `run-derived.sh`, `S5-update.provisioned.P2-AR-0039.py`, `derived-{before-base-53897c1,after-f9daec1}/`. The `*.superseded*` directories are development runs of the derivations, before the A2-04 `[L3]` and S5 `[U6]/[U8]` fixes. |
| `normdiff.py`, `COMPARE-probes-before-base-53897c1-vs-after-f9daec1.out` | normalised before/after comparison of every probe output |

Outputs contain this run's absolute scratch paths. The scratch roots are named `p2-ar-0039-*` beside the worktrees.

## 13. Process disclosures

- Model Claude Opus 5 (1M context), `claude-opus-5[1m]`.
- No sub-agents were spawned and the product owner was not contacted.
- No session or agent transcripts, task-output stores or user auto-memory were read.
- One `cargo build --release` exceeded the foreground limit and the harness moved it to the background. I waited for its
  completion notice and checked the binary directly, and did not read the output store. The base export's release build
  then ran in the foreground.
- The permission system denied one exploratory command that contained `rm -rf` of a scratch directory. It was not
  retried, and fresh directories were used instead.
- Development iterations are kept and labelled (`dev1`, `*.superseded*`). The claims rest on the `f9daec1` runs.
