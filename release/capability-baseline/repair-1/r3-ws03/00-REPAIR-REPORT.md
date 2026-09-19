# WS-3 (+ docs, spec amendments, adapters) repair report: repair iteration 1, round 3 (P2-AR-0034)

| | |
|---|---|
| Run | P2-AR-0034, role `capability-repair`, model Claude Opus 5 (1M context), `claude-opus-5[1m]` |
| Handoffs | P2-HO-0033 (WS-3 round 3), P2-HO-0031 (round-3 common, incl. the availability rule), P2-HO-0020, P2-HO-0010 |
| Branch / base | `phase2/repair-1-r3-ws03` from `53897c1a44157e5af81b176017bc7ded6a63b9cd` (integrated round-2 tree, `product_code_digest 797da37c…1fe1`) |
| Work commits | `dd80e62` (product, tests, kernel adapters/policies), `f50e37c` (D-0010, API-0001 1.2, ENFORCEMENT_MAP, docs), `a0cb4e3` (R1 census fix, §7), then the commit that adds this report, `claims.yaml` and `evidence/` (no product file) |
| Product identity | `a0cb4e3`: `product_code_digest c653a0cb16388a8a7d5f5f81df9fb3007bbbe824a7e05c6789b830588dbbf458`, `governed_state_digest 51b122a7…887a` (`evidence/identity.out`); release binary sha256 `4d30cd77…c9cb` |
| Items | P2-ADJ-0002; T2 completeness (IP-R3-2 `cit`, IP-R3-1 gates side, WS-2 R3-11); BC-P2-31 control-state move; WS-10 IP-WS10-01/02/15; WS-9 IP-R2-1/-5; WS-7 IP-W7-3/-4/-6; WS-4 R2-12/-13; WS-8 IP-R2-WS08-7; docs |
| Claims | `REPAIRED_CLAIMED`: P2-ADJ-0002 (WS-3 side), IP-R3-1 (gates side), R3-11, BC-P2-31 control state, IP-WS10-02, IP-WS10-15, IP-R2-1, IP-R2-5, IP-W7-3, IP-W7-4, IP-W7-6, R2-12, R2-13 (reviewed), docs. `PARTIAL`: IP-R3-2 (`cit` joins `SEALED_RECORD_TYPES` once WS-4 seals every CIT write), BC-P2-31 registry-as-OS-managed (API; the task-close list is WS-5's), IP-R2-WS08-7 (G0 class; the arm needs WS-8's writer). `NOT_REPAIRED`: IP-WS10-01 (needs `runtime/src/lifecycle/mod.rs`, WS-10's file, not in this round) |
| Verdict | `READY_FOR_INDEPENDENT_CAPABILITY_VERIFICATION` — builder claims only; nothing here is acceptance (Contract v3 O3). No owner-decision question (§10) |

---

## 0. Evidence index and regression (at `a0cb4e3`)

| What | Where | Result |
|---|---|---|
| `cargo test --lib` | `evidence/regression/cargo-test-lib.out` | **210 passed, 0 failed** (207 at base + 3 new `t2` unit tests) |
| `cargo test --test certification`, five chunks of exact names (`cert-list.txt`, `cert-chunk.sh`) | `evidence/regression/cert-chunk-{000,016,046,081,114}.out` | **146 passed, 0 failed** (16+30+35+33+32; 136 at base + 10 new `ws03_r3`), incl. `section6::*` 9, `srr::*` 21, `ws03::*` 15 |
| rustfmt, warnings, diffstat, scope checks | `evidence/regression/hygiene.out` | 0 hunks in every changed file (the 36 hunks reported through `tests/certification/main.rs` are the pre-existing `section6.rs`/`srr.rs` ones); 0 build / 0 test-build warnings; 23 files; no signing needle in product source; no protected path, other `repair-1/` directory or R1-listed file touched; Contract v3 `4c2df291…5ed3` |
| R1 held-out suites, all four, unedited, private path | `evidence/r1-heldout/r1-heldout-final-a0cb4e3.out` (runner `run-r1-heldout.P2-AR-0034.sh`) | every suite at its recorded baseline; census 118 files / 2025 functions, 0 violations (§7) |
| R1 run that found this run's own defect | `evidence/r1-heldout/r1-heldout-warmup.out` (at `f50e37c`) | AR-0031 26/8: `hx_a::a4` newly failed; fixed in `a0cb4e3` (§7) |
| Supplementary black-box probe | `evidence/R3-WS03-probes.py` (+ `r3_machine.py`); `probes/R3-WS03-probes.final-a0cb4e3.out`; negative control `probes/R3-WS03-probes.base-53897c1.out` | **26/26** after; base **1/26** (only the set-up control passes) |
| Audit-of-record probes, base vs this tree | `evidence/probes/COMPARE-audit-probes.out` (runner `run-audit-probe.P2-AR-0034.sh`, `audit-*/`, labelled copies in `derived/`) | no verdict line changes; the control-state difference is shown in D6/A5 (§3) |
| Test material | `r3_machine.py` (owner roots, the `t2-binding` role, bundles; published seeds only) | — |

---

## 1. P2-ADJ-0002 — T2 facts portable across the owner's provisioned machines

**Requirement** (P2-ADJ-0002; Contract v3 S6 :947-950 "tracked truth syncs through Git/private remote"; D-0007 rule 2;
ARCH-0003 §8 "additional machines are provisioned outside the project repository with the verifier, public root metadata
and protected machine/workload policy"; OWNER-DECISION-P2-0002). A T2 fact written by an OS operation on any machine
provisioned for the owner/project is honoured on every other such machine after a clone/pull; a record written by
anything else (hand edit, unprovisioned machine, a machine the provisioning did not authorise, a forged or modified
seal) is still refused, typed and observable. No private key or shared secret in any repository; no new external
dependency class.

### 1.1 Which conforming designs exist, and why this one

P2-ADJ-0002 names two: a per-owner/per-project binding authority delegated through the provisioned root, or per-machine
keys authorised by such a delegation.

* **Per-machine signing keys are excluded.** A record written on A and checked on B with A's *public* key needs `gov` on
  A to sign. `SRR-R0-L4` requires `gov` to verify and never sign. The R1 held-out suites enforce it over the whole
  product source (`ho_f::f2`, `hx_d::d7`, `hv_d::d6`: no `SigningKey`, `.sign(`, `SecretKey`, …, including unit tests).
  Such a design would break R1.
* **Per-machine symmetric keys give no gain.** B can check A's HMAC only by holding A's key. That is a keyring shared by
  the owner's machines, the same exposure as one shared authority key. The mechanism below still supports it: the owner
  may issue one authority per machine, and every machine holds all of them.
* **Chosen: an owner-authorised symmetric binding authority, delegated through the provisioned root.** It uses the
  existing primitives only: HMAC-SHA256 (`sha2`) and Ed25519 verification (`ed25519-dalek`, verify-only), the same
  root-role verification HC-1 uses for `human-gate`. The key is protected machine material installed from the
  administrator domain.

### 1.2 Mechanism (`runtime/src/t2.rs`; module documentation is the contract)

1. **Delegation.** The owner's Signed Release Root delegates the role `t2-binding` (`t2::AUTHORITY_ROLE`) to the owner's
   key(s). Root roles are open-ended, so the root format and `srr/**` do not change.
2. **Authorisation.** Off the agents' machines, the owner generates a 32-byte binding key and signs a
   `t2-binding-authority` document. The `t2-binding` key(s) sign it at threshold, and it binds:
   * `product`;
   * `authority_id`: `t2a-` plus 16 hex of SHA-256(`"t2-binding-authority-id:"` ‖ key), derived from the key, never
     taken from the document;
   * `key_commitment`: SHA-256(`"t2-binding-key-commitment:"` ‖ key);
   * `issued`, `expires`, `owner`.
3. **Provisioning** (`t2::provision_authority`; `gov trust t2-binding --provision <bundle>`). The administrator installs
   a `t2-binding-provisioning` bundle (`{_type, key_hex, authority: <envelope verbatim>}`) from the administrator domain,
   on each of the owner's machines. The command refuses, typed, and writes nothing:
   * below floor (`guard_effect(TrustPolicyMutation)`, first);
   * a bundle inside a repository or under `.git`/`governance` (`T2_AUTHORITY_FROM_REPOSITORY_REFUSED`);
   * an unprovisioned machine (`T2_AUTHORITY_UNPROVISIONED`, remediation: provision);
   * a root with no `t2-binding` role (`T2_AUTHORITY_ROLE_NOT_DELEGATED`);
   * a signature below threshold or from keys this root does not delegate (`T2_AUTHORITY_UNAUTHORISED`), which covers
     another owner's root and an agent's own key;
   * an expired authorisation (`T2_AUTHORITY_EXPIRED`);
   * a key the owner did not authorise (`T2_AUTHORITY_KEY_MISMATCH`);
   * a malformed bundle (`T2_AUTHORITY_INVALID`).

   The key is stored in `<state_root>/t2-binding/authorities/<id>/key.json` with mode 0600 (the directory is 0700) and is
   never printed. The owner's envelope is stored verbatim beside it. Installing the same bundle again is `unchanged`. A
   newly signed authorisation of the same key, e.g. after the role's key rotated, replaces the stored authorisation.
4. **Sealing** (`t2::seal_value`, unchanged signature). When this machine holds an authority that its trusted root
   authorises now and that is unexpired, the seal is `hmac-sha256/t2-v2`, scope `provisioned`. Its MAC binds:
   * the authority id;
   * the sealing machine's id;
   * the operation and the time;
   * the canonical content.

   If several authorities qualify, the latest issued is used. Otherwise the seal is the round-1 machine scope
   (`hmac-sha256/t2-v1`, the machine's own key). An unprovisioned machine, or a provisioned one without an authority,
   keeps working locally, as before.
5. **Verifying** (`t2::verify_value` and everything built on it). Every T2 consumer is unchanged and gets the new
   behaviour, because the `Binding` API is unchanged apart from one added variant. A portable seal is:
   * `Verified` (scope `provisioned`) only when this machine holds the authority's key (the MAC verifies) **and** its own
     trusted root authorises the authority now. The owner's signature is re-verified against the current root, so a
     root successor that drops the `t2-binding` key revokes it.
   * `Foreign` when this machine does not hold the authority: another owner's machine, or a machine whose administrator
     has not installed it.
   * `Unauthorised`, a new code, when the machine holds the authority but its root no longer authorises it.
   * `Broken` for any edited byte: a field, the sealing machine, the operation, the time, the authority name.

   A machine-scope seal from another machine is `Foreign`. That includes a machine with no local key of its own, which
   the base binary called `KEY_UNAVAILABLE`. Expiry limits when an authority may *seal*. Records sealed while it was
   valid stay honoured, as owner-signed human answers do.
6. **Status** (`t2::binding_status`, `gov trust t2-binding`) reports:
   * the sealing scope, and why it is the machine scope (unprovisioned, no delegation, none installed, revoked,
     expired);
   * each installed authority: authorised or not, expiry, signers;
   * the bundle format and the premise.
7. **Continuity** (`t2::reseal`, `gov trust t2-binding --reseal [--dry-run]`, L4 `reseal_t2_bindings`). It re-seals
   under the authority exactly those machine-scope seals that verify here **and** were made while this machine was
   provisioned (seal `at` ≥ the provisioning record's `provisioned_at`), keeping the recorded operation and time. It
   works bottom-up through nested seals (registry entries, CIT `os_state`); an enclosing seal is kept valid in the scope
   it had. A record sealed while the machine was unprovisioned, and a record whose seal does not verify, is never
   re-sealed.

### 1.3 Trust argument

| Attacker / case | Result | Why |
|---|---|---|
| repository write only (hand-written or edited gate, decision, CIT state, registry entry, evidence) | `UNSEALED` / `BROKEN` on every machine, `T2_UNBOUND` | the MAC needs a key that lives only in protected machine state |
| copy a sealed record into another place of the same project | refused where content changed (`BROKEN`) | the MAC covers the whole canonical content, including the id |
| a machine provisioned for the owner but not given the authority | its seals are machine-scope: `FOREIGN` on the owner's machines; it honours none of theirs (`FOREIGN`) | possession of the authority key is the provisioning's authorisation |
| an unprovisioned machine | cannot install an authority (`T2_AUTHORITY_UNPROVISIONED`); its records are `FOREIGN` elsewhere | the authority is only honoured under a trusted root |
| another owner's machine (another root and authority) | its records are `FOREIGN` (scope provisioned); the owner's bundle is refused there (`T2_AUTHORITY_UNAUTHORISED`) | its root does not delegate the owner's `t2-binding` key |
| an agent installs its own key or bundle through `gov` | `T2_AUTHORITY_UNAUTHORISED` | only a signature by the root's `t2-binding` role at threshold authorises a key; `gov` holds no signing key |
| environment variables, CLI flags, plugins, model output | cannot provide an authority | none of them is an owner signature or protected machine state |
| owner revokes (root succession without the `t2-binding` key) | records become `UNAUTHORISED`; sealing falls back to the machine scope | use-time re-verification against the current root |
| a process with the **operator's OS privileges** on one of the owner's machines | can read the key: **detection-grade**, as in round 1. What it forges there is honoured on the owner's other machines holding that authority | This is inherent in the requirement: any mechanism that honours A's facts on B honours what a compromised A forges. Human answers and human-approval assertions stay bound to the owner's signature, which no machine holds. |

**Premise (ARCH-0003 §1, §8).** The administrator boundary is uncompromised. The binding key is protected machine
material. The administrator carries it to the owner's machines the way they carry the root: from the administrator
domain, outside every repository. The channel must be confidential; that is administrator practice, not product code.
**Residual stated:** the key is shared by the machines that hold it (symmetric; `gov` never signs). One machine's
compromise therefore also lets records be forged *as* the owner's other machines. Revocation is per authority (a new
authority plus `--reseal` before revoking, or root succession), unless the owner issues one authority per machine.

### 1.4 What WS-8 (provisioning) needs to provide: the API, not an edit of `srr/**` (IP-R3-WS03-1)

* **Product: nothing is required.** The root format already carries arbitrary roles, and `srr::verifier::trusted_root`
  and `Root::verify_role` are the only calls used. Optional usability improvements:
  * `gov trust provision --anchor <root> [--t2-binding <bundle>]` as one administrator step. After provisioning
    succeeds it calls `gov_runtime::t2::provision_authority(bundle, project_root)`.
  * `gov trust status` includes `gov_runtime::t2::binding_status()["sealing"]`.
* **Harness (`tests/certification/common.rs`).** The reference implementation is in `tests/certification/ws03_r3.rs`
  (`owner_root`, `foreign_root`, `bundle`, `install_binding`, `clone_of`):
  * the suite root may delegate `t2-binding` to a published test key (`ws03_r3::t2_role_key`, seed 0x6b);
  * `common::provision_with_t2(&Gov)` = `provision` + `trust t2-binding --provision <suite bundle>`;
  * a two-machine helper: clone to a new path, `provision_with_t2`, `kernel reinstall --source signed_source()`;
  * plus an unprovisioned clone and a foreign-root machine.

  If the suite's `provision` starts installing the bundle, every scenario machine seals in the provisioned scope. No
  certification test depends on the machine scope.

### 1.5 Tests, probes, observability

* **Certification** (`tests/certification/ws03_r3.rs`):
  * `os_written_facts_are_honoured_on_the_owners_other_provisioned_machines_and_nowhere_else` covers machines A, B, D
    (provisioned without the authority), U and U2 (unprovisioned) and F (another owner). It covers gates, decisions, a
    CIT simulated on A and approved+executed on B, a plugin registered on A that runs on B, governed evidence, a pull
    back to A and a hand edit. Every seal is re-derived in the test from the documented format, independently of the
    product.
  * `a_t2_binding_authority_is_admitted_only_from_the_administrator_domain_under_this_machines_root`: every refusal of
    §1.2 item 3, the 0600 key file and the re-signed authority.
  * `root_succession_that_drops_the_binding_role_revokes_its_records_and_sealing_falls_back`.
  * `reseal_makes_what_this_machine_sealed_while_provisioned_portable_and_nothing_else`.
* **Unit tests** (`t2::tests`): a portable seal is honoured only where the authority is held and authorised; every edit
  breaks it; sealing-authority selection (authorised, unexpired, latest); reseal rules.
* **Supplementary probe** (`R3-WS03-probes.py`, black-box, published seeds, two binaries):

  | Line | Base `53897c1` | This tree |
  |---|---|---|
  | ADJ2.a authority installs; seals take the provisioned scope | FAIL (no command) | PASS |
  | ADJ2.b gate answered on A honoured on B (answer verified) | FAIL (`KEY_UNAVAILABLE`) | PASS |
  | ADJ2.c nothing written on A unverified on B | FAIL (7 records + 2 health outputs) | PASS |
  | ADJ2.d gate raised on A answered by the owner on B | FAIL (`T2_UNBOUND`) | PASS |
  | ADJ2.e CIT from A approved + executed on B | FAIL (`T2_UNBOUND` ×2) | PASS |
  | ADJ2.f plugin registered on A runs on B | FAIL (`PLUGIN_REGISTRATION_UNBOUND`) | PASS |
  | ADJ2.g A's governance-suite records honoured on B | FAIL | PASS |
  | ADJ2.h B's writes honoured on A after a pull | FAIL | PASS |
  | ADJ2.i/j machine without the authority: refuses A's gate/CIT/registration; its gate `FOREIGN` on B | FAIL (untyped: `KEY_UNAVAILABLE`) | PASS |
  | ADJ2.k/l unprovisioned: cannot install; its gate `FOREIGN` on B | FAIL | PASS |
  | ADJ2.m another owner: bundle refused; its gate `FOREIGN` on B | FAIL | PASS |
  | ADJ2.n hand edit `BROKEN` on B | FAIL | PASS |
  | ADJ2.o key in no tracked file; 0600 | FAIL (no key) | PASS |
  | ADJ2.p root succession revokes (`UNAUTHORISED`), fallback | FAIL | PASS |
  | RESEAL.a / G0.a | FAIL / FAIL | PASS / PASS |

  On the base binary the records of D, U and F are not honoured either; the difference there is the typing.

**Observed consequence, by design.** `init` run on a machine *before* it was provisioned seals its conformance record in
the machine scope. That record is `FOREIGN` on the owner's other machines and is not re-sealed (it was written while
unprovisioned). The documented first run, provision then install, never produces one (probe dev run 3 vs 4,
`probes/R3-WS03-probes.dev-after.out`).

---

## 2. T2 completeness

* **IP-R3-2 (`cit` in `t2::SEALED_RECORD_TYPES`), PARTIAL.** In this tree no writer whole-record-seals a CIT (only the
  `os_state` sub-object is sealed). Adding `cit` now would make every CIT window change a T2 violation at task close
  (`tasks::sealed_kind`, `cit_record_honoured`) and fail `greenfield_end_to_end`. The WS-3 side is ready: the constant's
  documentation states the condition, and `gates.rs` already re-seals the CIT records it rewrites (below). The one-line
  change is IP-R3-WS03-2, for the integrator after WS-4's sealing merges.
* **IP-R3-1, gates side: REPAIRED_CLAIMED.** `gates::block_tasks`, `move_tasks` (answer: release/block; revoke: block)
  and the CIT writes in `answer` (decline → REJECTED, decision link) and `revoke` (→ SIMULATED) capture whether the
  record's seal verified *before* the write and re-seal it after only then (`t2::seal_if_verified`), under their own
  operation name. A record whose seal did not verify is written and left unsealed: the OS never blesses content it did
  not write. Test: `gate_operations_keep_os_sealed_task_records_verifiable_and_never_bless_others` (the sealed task is
  re-verified independently at each of the three writes; an unsealed task stays unsealed; a broken seal stays broken).
* **WS-2 R3-11: REPAIRED_CLAIMED.** `t2::audit` also lists every plugin-registry entry and the registry document whose
  seal does not verify (`capabilities::registry::{path, unbound_entries, document_binding}`). So `os_binding_integrity`,
  doctor D033 and the `t2_bindings` currency class cover the registry. Test: `the_t2_audit_covers_the_plugin_registry`;
  probe T2C.a (base: FAIL).

## 3. BC-P2-31 — the emergency-control state moves to the operational store

**Requirement** (repair-delta BC-P2-31; WS-6 r2 IP-R2-8; Contract v3 B1:188, B3:202, D6:352). Emergency-control state
survives deletion of every path the product classifies derived.

**Change** (`runtime/src/orchestration/control.rs`).
* `control::path` is `paths::store_path(root, "emergency-control")` (`.governance-state/control.json`).
* `control::state` reads without writing. When a legacy `<runtime dir>/control.json` also exists, the stricter state is
  in force: frozen if either is, paused if either is, agents cancelled if either is. The legacy copy is shown as
  `legacy_state`.
* `control::set` calls `paths::ensure_state_dir`, then `paths::relocate_legacy(root, "emergency-control")`. It applies
  the command to the effective state, writes the store and removes any legacy copy.
* **Deviation from the letter of WS-6 r2 IP-R2-8** ("`relocate_legacy` before read/write"): the relocation runs on the
  write path only. `control::state` is called by every G0 guard, including read commands and commands run under
  FREEZE_WRITES, so a relocating read would be a write where none may happen. Honouring the stricter of the two
  copies on read gives the same enforcement without writing. The first control command moves the state.
* **`governance/registry/` as OS-managed: PARTIAL.** `t2::OS_MANAGED_PREFIXES` and `t2::os_managed_location` name it.
  The task-close list (`tasks::OS_MANAGED_PREFIXES`) is WS-5's file (IP-R3-WS03-3).

**Evidence.**
* Test `emergency_control_state_lives_in_the_operational_store` covers: the freeze is in the store and not in git
  status; deleting `.governance-runtime/` leaves it frozen; a legacy freeze is honoured, then resolved; a legacy pause
  plus a new freeze yields both.
* Probe CS.a-c: base FAIL ×3, after PASS ×3.
* beta-r D6 labelled copy (the fixture's claimed task made claimable, and the unregistered reranker override dropped;
  the header lists the three changes). After deleting the whole runtime directory the base loses `{claims, control}`
  and this tree loses `{claims}` only. D6-b2-B stays FAIL until WS-5 moves the claims store (WS-6 r2 IP-R2-7). Verdict lines are
  otherwise identical.
* alpha-r A5, unedited, now stops where it reads the old path (`TypeError` on `None`). The labelled copy reading the store path
  prints output identical to the base's unedited run after normalisation (`COMPARE-audit-probes.out`).
* Test changed: `ws06::deleting_everything_classified_derived_keeps_claims_control_and_registration`. It asserted
  `emergency-control` is reported misplaced, which held while its writer used the legacy path. It now asserts the store
  is in place, and that every store is reported misplaced exactly when its legacy location exists. That is stronger,
  and it holds whichever writers have moved.

## 4. Integration points routed to WS-3

| IP | Status | What changed |
|---|---|---|
| WS-10 IP-WS10-02 | REPAIRED_CLAIMED | `gates::create` refuses a gate whose `derived_from`/`evidence_refs` cite research/experiment evidence that is not governed (`lifecycle::require_citable` → `EVIDENCE_NOT_CITABLE`), before writing, and records the backlink after (`lifecycle::record_influence`, re-sealing only verified records). `gates::answer` does the same for `--evidence` ∪ the gate's citations, and backlinks the decision. A backlink failure after the write is reported in `evidence_influence`, never undoing the persisted gate/decision. Test `gates_cite_only_governed_research_and_record_its_influence`; probe EV.a |
| WS-10 IP-WS10-15, WS-9/11 IP-R2-5 | REPAIRED_CLAIMED | `experiment_promotion` and `upstream_export` join `gates::HUMAN_ONLY_TRIGGERS` (the kernel floor) and `HUMAN_GATE_POLICY.human_only_triggers` (additive). Test `upstream_export_and_experiment_promotion_gates_are_human_only` (with an agent-resolvable control); probe HO.a |
| WS-10 IP-WS10-01 | NOT_REPAIRED | Needs `lifecycle::RECORD_AUTHORITY` (in `runtime/src/lifecycle/mod.rs`, WS-10's file; WS-10 is not in round 3, and P2-HO-0010 forbids editing it) changed together with its twelve `COMMAND_GUARDS` entries (the lifecycle unit test keeps them equal). No policy class was declared, because it would do nothing until then. Exact recipe: IP-R3-WS03-4 |
| WS-9/11 IP-R2-1 | REPAIRED_CLAIMED | `run()` installs the declared session (`--session`, else `GOV_SESSION`) right after the acting role (`identity::install_declared_session`). Adoption authorship records the source `installed`. `ws03::round_two_call_sites…` now expects `"session: installed; role: flag"` |
| WS-7 IP-W7-3 | REPAIRED_CLAIMED | `ENFORCEMENT_MAP` rewords `elevated_permission_classes`, `refuse_on_pin_drift` and `registration_binds` (keys and `enforced_by` unchanged; `repair::policy_enforcement_coverage_is_complete_and_honest` passes) |
| WS-7 IP-W7-4 | REPAIRED_CLAIMED | `gov plugins registry` → `registry::report` (each entry's T2 binding and `honoured`, and the document binding) |
| WS-7 IP-W7-6 | REPAIRED_CLAIMED | New governed record `spec/decisions/D-0010.yaml`: amends D-0005 consequence 3 to conform with Contract v3 F4 / ARCH-0003 §9, authored within delegated authority as D-0005/D-0007 were; the owner may supersede. D-0005's text is unchanged. `spec/interfaces/API-0001.yaml` 1.2: governance clause rewritten, the 1.1 clause kept verbatim in its history (append-only, as D-0005 did for 1.1), `amended_by: [D-0005, D-0010]`. `docs/DECISIONS.md` indexes both. `arch::schemas_policies_and_registries_validate…` and `repair2::interface_contract…` pass |
| WS-4 R2-12 | REPAIRED_CLAIMED | New kernel adapter `framework/adapters/hooks/` → `governance/generated/adapters/hooks/provider-hooks.json`: `pre_compaction` → `gov checkpoint create --trigger before_compaction …`, `session_end` → `gov session close …`, `model_switch` → `gov checkpoint create --trigger before_model_switch …`, with the invariants (adapter conformance). The generic/IDE adapters point to it. Test `generated_provider_hooks_call_gov_checkpoint_and_session_close` (each hook's argv run as written records its trigger); probe HOOKS.a. `greenfield` now expects six adapters. The delta-r N2.b8 criterion (a file under `adapters/` named `hook`) holds; the unedited N1-N2 probe stops earlier on both binaries (§6) |
| WS-4 R2-13 | REPAIRED_CLAIMED (reviewed) | `cit classify`, `cit propagate --dry-run`, `context staleness`, `checkpoint freshness`: Read. `cit propagate` → Write/`simulate_cit` (L2): it writes markers and revalidation tasks, the same level as creating tasks. `session close` → Write/`checkpoint` (L1). Refused under FREEZE_WRITES/PAUSE like every checkpoint, consistent with round-2 O-4 (only derived-state rebuild and the controls are recovery operations). No change |
| WS-8 IP-R2-WS08-7 | PARTIAL | `COMMAND_GUARDS`: `release record` → Write / `record_release` (L2, declared in `AUTHORITY_POLICY`), so the command cannot run unguarded once it lands. The CLI arm needs WS-8's writer `release::record` and WS-4's record type; neither is in this tree (IP-R3-WS03-5) |

## 5. Documentation

* **`docs/ARCHITECTURE.md`:**
  * §3: the operational store, the plugin-registry location and the kernel classification of OS stores;
  * §4.3: the control state and the other writers;
  * §4.4a: admission and bootstrap on unprovisioned machines, "provision, then install" (WS-3 IP-R2-5, WS-8
    IP-R2-WS08-1);
  * §4.7: rewritten for executable-plugin registration and byte binding, and tool approval (WS-7, D-0010);
  * §4.8: the T2 binding rewritten, a new "T2 facts across the owner's machines" section, human-only triggers, and
    evidence a gate rests on;
  * §4.9: T2-honoured evidence, the new families, D032-D034, `health qualify` (WS-2 R3-10), change propagation,
    checkpoint/handoff/session continuity, provider hooks, contradictions (WS-4), fabric integrity and
    retrieval-profile governance (WS-6), research/experiment/data lifecycles (WS-10);
  * §5: materiality, CIT binding;
  * §6: adoption independence, sessions, designated roles, bound approvals (WS-9 IP-R2-7);
  * §6.1: runnable derivation, the close order, recorded authorship, the producer rule (WS-5 IP-R3-9);
  * §7: the export approval flow.
* **`docs/COMMANDS.md`:**
  * `trust t2-binding`, provision-then-install, `init` BOOTSTRAP;
  * the adopt requirements and the export flow;
  * the new work, health, CIT, lifecycle and memory commands, and the hooks;
  * refusal codes by area: T2 and machines, admission, work and close, change control, evidence and lifecycles,
    adoption, plugins, tools and profile.
* **`README.md`:** the quick start is now provision, then install, plus the optional T2 authority (WS-8 IP-R2-WS08-1,
  exact text).
* **`docs/FIXTURES.md`:** the provisioned harness convention, the multi-machine row and the round builder scenarios.
* **`docs/DECISIONS.md`:** D-0010 and API-0001 1.2.
* `docs/generated/**` is untouched.

## 6. Tests added or changed

| File | Change | Reason |
|---|---|---|
| `tests/certification/ws03_r3.rs` (new, `mod` line in `main.rs`) | 10 tests (§1, §2, §3, §4) | this round's items |
| `runtime/src/t2.rs` unit tests | 3 new; the round-1 test uses `seal_local_at` | §1 |
| `tests/certification/ws06.rs` | misplaced-store assertion generalised | §3: the control writer moved, as intended |
| `tests/certification/ws03.rs` | `session_source` expects `installed` | IP-R2-1 |
| `tests/certification/greenfield.rs` | adapter count derived from the kernel (6) and the hooks file asserted | R2-12 |

No test was deleted and no assertion weakened.

## 7. R1 preservation (AC-14)

**Scope.** Changed §6 sinks:
* `gates.rs`: human-gate create/approve (new writes all pass `save_record` and existing guards);
* `control.rs`: the control-state writer (`guard_write` unchanged);
* a new trust-policy-mutation writer, `t2::provision_authority`, which calls `guard_effect(TrustPolicyMutation)` first.

No file under `srr/**`, `kernel*.rs`, `lock.rs`, `init.rs`, `update.rs`, `release.rs`, `recovery.rs`, `records.rs`,
`tools.rs` or `capabilities/**` changed.

**Run.** All four prior R1 held-out suites ran unedited: 28 `identical` cmp lines, a private scratch root whose
`srr1-r1-verify*` links point at this worktree only, HEAD `a0cb4e3`, 0 product files differing.

| Suite | Recorded baseline | This tree |
|---|---|---|
| AR-0027 | 26 / 3 (`b1`, `b2`, `d3`) | **26 / 3**, same tests |
| AR-0029 | 26 / 2 (`b3`, `b6`); `ho_f` does not compile | **26 / 2**, same; `ho_f` does not compile |
| AR-0031 | 27 / 7 (`a1`, `a5`, `a8`, `b6`, `c2`, `c3`, `d2`) | **27 / 7**, same tests |
| AR-0033 | 31 / 0 (30 / 1 on any larger tree) | **30 / 1**: `hv_a::a1` size pin only |

**Census.** AR-0033's walk counts **118 files / 2025 functions**. The labelled unpinned copy (byte-identical to
P2-AR-0032's) finds **0 violations in every §6 activity**:

| §6 activity | Derived | Writers | Exempt |
|---|---|---|---|
| human_gate_create | 48 | 43 | 1 |
| human_gate_approve | 1 | 1 | — |
| release_certification | 1 | 1 | — |
| trust_policy_mutation | 8 | 1 | — |
| privileged_plugin_acquisition | 9 | 2 | — |
| floor_lower_or_reset | 3 | 1 | — |
| present_below_floor_release_as_current | 1 | 1 | — |

AR-0033's own `derive.py` agrees under all three splitter configurations. `section6::*` is green (9/9).

**A defect this run introduced and fixed.** The first R1 run (`r1-heldout-warmup.out`, at `f50e37c`) showed AR-0031
**26/8**: `hx_a::a4_the_trust_anchor_sink_refuses_and_is_the_only_writer` failed with "the trust anchor path is composed
by hand outside `state.rs`: runtime/src/t2.rs". The authority cache's fingerprint had composed `trust/root.json`.
`a0cb4e3` keys it by the provisioning record instead: `MachineState::set_root_metadata` rewrites that record with the
anchor's digest on every provisioning and succession. `t2.rs` no longer names the anchor path, and `a4` passes. The
final run is at baseline.

## 8. Integration points for round 4 / integration

| IP | Owner / file | Change | Why |
|---|---|---|---|
| IP-R3-WS03-1 | WS-8 `tests/certification/common.rs` (+ optional `trust provision --t2-binding`) | §1.4: `t2-binding` role in the suite root, `provision_with_t2`, the two-machine / unprovisioned / foreign helpers (reference: `ws03_r3.rs`) | P2-ADJ-0002 harness; one convention for the suite |
| IP-R3-WS03-2 | integrator after WS-4's CIT sealing merges; `runtime/src/t2.rs` | `SEALED_RECORD_TYPES = &["human-gate", "cit"]`, then run the suite | WS-5 IP-R3-2 |
| IP-R3-WS03-3 | WS-5 `orchestration/tasks.rs` | add `"governance/registry/"` to `OS_MANAGED_PREFIXES` (or consult `t2::os_managed_location`) | BC-P2-31: the registry's new home (WS-7 IP-R2-9) is observed at close by its seal |
| IP-R3-WS03-4 | integrator (WS-10's file unowned in round 3) | declare `record_research_evidence: L1` in `AUTHORITY_POLICY`; set `lifecycle::RECORD_AUTHORITY` to it and the twelve research/experiment/data write labels in `COMMAND_GUARDS` | WS-10 IP-WS10-01 |
| IP-R3-WS03-5 | WS-8 writer + WS-4 record type, then CLI | `ReleaseCmd::Record {…}` → `gov_runtime::release::record(&p, …)`; `g0_label` `"release record"` (already classified) | WS-8 IP-R2-WS08-7 |
| IP-R3-WS03-6 | WS-2 `doctor.rs`, `verification/reporting.rs` | disclose (low) a provisioned machine whose seals are machine-scope (`t2::binding_status()["portable"] == false`); report `binding_status()["sealing"]` beside `binding_key` in `os_binding_integrity` | observability of P2-ADJ-0002 posture |
| IP-R3-WS03-7 | WS-7 `capabilities/PROTOCOL.md` | the last bullet ("a fresh clone re-registers"): with the owner's T2 binding authority, registrations are honoured on the owner's provisioned machines (P2-ADJ-0002) | documentation truth |
| IP-R3-WS03-8 | WS-5 `status.rs` (optional) | `gov status` shows `t2::binding_status()["sealing"]["scope"]` | fresh-agent view of portability |
| IP-R3-WS03-9 | probe authors / verifiers | alpha-r A5 reads `.governance-runtime/control.json`; the state is now `.governance-state/control.json` (labelled copy in `evidence/probes/derived/`) | BC-P2-31 |

## 9. What this run did not do

* No agent L0–L4 credentials (OWNER-DECISION-P2-0001).
* No change to root metadata, `srr/**`, the verifier, the floors or the harness `common.rs`.
* No new external dependency class.
* No edit of `runtime/src/lifecycle/**`, `tasks.rs`, `status.rs`, `cit/**`, `capabilities/**`, `doctor.rs` or
  `verification/**`.
* No edit of D-0005's text or of any accepted record's history.
* Nothing under `release/verification/`, `release/root-of-trust/`, `release/releases/`,
  `release/orchestration/phase-1/`, `release/capability-baseline/audit-0/` or another workstream's `repair-1/`
  directory.
* Audit-of-record probes ran unedited. The two labelled copies (`derived/`) list every change in their headers.
* The standalone human-gate anchor stays off, and no default role or unauthenticated answer path was introduced.
* No new hard-block (availability rule, P2-HO-0031):
  * The new refusals are typed and scoped to the one operation whose reliance they protect: `T2_AUTHORITY_*`,
    `EVIDENCE_NOT_CITABLE` on the citing gate or answer, and the two human-only triggers on their own gates.
  * `trust t2-binding --reseal` is not a governed-work operation, so `control::guard_health` never refuses it.
  * The control-state move keeps FREEZE_WRITES/PAUSE as the policy-required global stop (Contract v3 L4), with the
    round-2 recovery allow-lists unchanged.

## 10. Owner-decision questions

None. I considered whether P2-ADJ-0002 forces a trade-off the sources leave open and concluded it does not, for three
reasons:

* The design class used here, a per-owner binding authority delegated through the provisioned root, is one P2-ADJ-0002
  itself names as conforming.
* The alternative class (per-machine signatures) is excluded by an R1-accepted property (`SRR-R0-L4`), not by a
  preference.
* The one security consequence is inherent in the requirement, not in this mechanism: a compromised machine's forgeries
  are honoured on the owner's other machines. The seal's detection-grade standing against an operator-privileged
  process is the round-1 posture ARCH-0003 §1 already places outside the envelope. The human-answer facts stay bound to
  the owner's signature.

**For the owner's information:** the administrator now carries one secret file (the binding bundle) to each of the
owner's machines, besides the public root. If the owner prefers per-machine revocation, the mechanism already supports
one authority per machine.

## 11. Process disclosures

* Model Claude Opus 5 (1M context), `claude-opus-5[1m]`. No sub-agents. The product owner was not contacted. No
  session or agent transcripts, task-output stores or user auto-memory were read. Every command ran in the foreground,
  with output redirected into scratch or `evidence/`.
* The permission system denied one command that began with `rm -f` of an earlier base N1-N2 output. I did not retry it
  as written. That output was later overwritten by the recorded run under the same name.
* Found and fixed before the recorded runs:
  * the AR-0031 `a4` census regression (§7; the warmup output is kept);
  * the probe's owner key object lacked the method name the alpha-r minter calls;
  * the probe's first A machine was bootstrap-installed before provisioning, which made its init-time conformance
    record, correctly, `FOREIGN` on B;
  * a falsy-empty check in ADJ2.g;
  * two certification-test fixture errors (a registry edit that changed nothing; a decide before render). Recorded
    runs are the final versions.
* This run built the base binary from a `git archive` of `53897c1` in scratch, reusing this worktree's target
  directory, and restored this tree's binary afterwards. Its sha256 equals the round-2 integration's recorded release
  binary (`5ff6ce9c…`).
* Outputs contain the absolute scratch paths of this run.
