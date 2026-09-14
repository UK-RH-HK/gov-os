# Output 11 — Migration plan from 4.1.5

> **RoT-1 revision 3 — PROPOSED, pending a fresh independent review; not approved, not implemented.**
> 4.1.5 stays immutable and REJECTED. Nothing in `release/releases/4.1.2…4.1.5`, or in any verifier or review directory,
> is edited. No phase below starts before fresh independent reviews accept revision 3 and the owner answers the D-0008
> gate.

## Phase 0 — Review, approval, key ceremony (before any code)

1. **Fresh independent reviews of revision 3.** Trust and security (B); compatibility and transactions (C); synthesis.
   The architect session AR-0001 authored revision 3 and cannot review it.
2. **Owner decision.** Present D-0008 as a Human Decision Gate. The owner answers OP-1…OP-7 (`21`).
3. **Root ceremony** (offline), per OP-1 and OP-2:
   - root keys with threshold;
   - keys for `release-final` (+ standby), `release-candidate`, **`release-artifact` (≥ 2 custodians)**,
     **`build-attestation` (independent rebuilder)**, `verification-attestation`, `certification-status` (+ standby),
     `revocation`, `trust-state` and `retrieval-profile`, with grants satisfying the compiled whitelist (`05` §3);
   - root v1 signed; trust-root id computed;
   - the root fingerprint published in at least two independent channels (`06` §2).
4. **TPS v1.** `gov trust draft-policy` output for the 4.1.6 kernel. It contains:
   - the **Constitutional Surface Inventory**. The draft for review is `constitutional-surface/CONSTITUTIONAL_SURFACE_INVENTORY.yaml`,
     derived from the current `framework/`. It is re-derived after the WP-10 kernel path changes, and the change list is
     reviewed;
   - eligibility, with `min_release_sequence` = the first 4.1.6 candidate's sequence, `min_binary_version: 4.1.6`, and
     **`historical_releases[]`** for 4.1.2–4.1.5;
   - gating per OP-3;
   - the **`bootstrap`** block per OP-6 and OP-7;
   - an empty `lowering_history`.

   It is reviewed and signed at root threshold.
5. **TSS 1** references root v1 and TPS v1; its state fingerprint is published.
6. **Test lineage** covering all eleven purposes, compiled only into `gov-test-profile`.

**Exit:**
- D-0008 ACTIVE (human-approved) with rules (1)–(20);
- D-0007 SUPERSEDED;
- ARCH-0002 ACTIVE;
- public trust data under `trust/production/`;
- the record schema gains a `PROPOSED` status.

## Phase 1 — Historical releases

1. Independently reproduce the 4.1.2–4.1.5 payloads and confirm the tree digests `9964830b…`, `6bebfdbb…`, `e5e2f2c7…`,
   `962f9848…`.
2. Record them in TPS v1 `eligibility.historical_releases[]` with status `REJECTED` and verifier report digests. There is
   no separate threshold-1 statement (`05` §2).

## Phase 2 — Implementation on `release/4.1.6-rc1` (builder)

| Work package | Content | Governing sections |
|---|---|---|
| WP-1 trust core | JCS, DSSE, statements v3, purpose table, compiled whitelist, Ed25519 | `05`, `07` |
| WP-2 trust state | knowledge union, S1–S12, equivocation, `prior_states`, release-local references, MS-2 | `17` |
| **WP-3 anchors and freshness** | pins, `confirm-state`, witnesses, freshness axis, C0–C3 gating, VTS monotonic records | `24` |
| **WP-4 Constitutional Surface** | evaluator of `floor_schema_version: 2`, precedence lattice, E7, effective policy, exceptions after join, consumer and decision-point registers. The implementation must pass `csi_check.py selftest` equivalents (R-SURF-7). | `23`, `19` |
| WP-5 eligibility and floor | E1–E10, install authority with joined actor levels, computed weakenings, computed policy lowering | `19` |
| WP-6 secure filesystem and snapshot | `SecureDir`, link counts, KernelSnapshot generation (VU-11), EmbeddedSnapshot, installation state machine including `LEGACY` and occupation | `18` §1–§3, §6–§9 |
| WP-7 governed filesystem | every mutation site rewired; PPS including occupation entries and the transaction area | `18` §8 |
| WP-8 install transaction and recovery | `.governance-runtime/trust-tx`, VTS open-transaction registry, union trust record, exchange, recovery, `overlay.prev` weakening gate | `18` §5, `20` |
| **WP-9 layout and legacy containment** | FORMAT with layout; lock 3.0.0; occupation entries; layout migration of legacy projects; quarantine of legacy residue; project-strength vector | `26`, `08` |
| **WP-10 kernel path changes** | kernel values naming legacy paths move to the RoT-1 layout: `TOOL_POLICY.plugins.registry_path`, `mcp.registry_path`, `LEARNING_POLICY.upstream.forbidden_paths`, overlay templates (`PROJECT_POLICY.governance.*`, `REPOSITORY_CONTRACT` patterns), adapters (pointers, not canonical-source text), schemas naming paths. Re-derive and review the CSI draft. | `23` §6.2 |
| **WP-11 trust gates** | compiled kinds, `gov trust confirm` terminal challenge, decision pins, `gov decide` refusal for trust gates, `by_kind` for non-trust gates | `27` |
| **WP-12 binaries** | Trust Base Manifest in `build.rs`; `gov version --trust`; `verify-artifact` A1–A10; first-run high-water self-check; reproducible build pipeline with published build inputs | `25` |
| WP-13 ingress rewiring | init, adopt batch 0, update, rollback, reinstall, recover, profile install, trust refresh | `09` §2 |
| WP-14 producer and publisher | `release build` with surface checker; `attach-signature`, `promote`, `verify`; `trust draft-policy`, `publish`, `export` | `07` §7, `23` §6 |
| WP-15 agent consumption | `gov kernel show`, `skills show`, adapter pointers, VTS rendering record, D036 | `18` §12 |
| WP-16 conformance | `release_ingress` family; command register with operation classes; interception; private-key scan; floor-regression and TBM-profile pipeline checks; separate `gov-test-profile` | `02` §6, `05` §10 |
| WP-17 documentation | `docs/ARCHITECTURE.md` §4.4a; release and distribution protocol (fingerprints, surface registration, binary acceptance, OP-6/OP-7 ceremony, legacy binary retirement) | `06`, `25`, `26` |
| WP-18 migration | `migrations/M-4.1.5-4.1.6.yaml`: notes, `regenerate_adapters`, index rebuild. Layout migration is performed by the install transaction, never a migration operation. | `08` §4, `26` §7 |
| WP-19 profiles (may slip) | `gov profile install`, CAS, host verification | `10` |

## Phase 3 — Candidate, verification, promotion, certification, binaries, publication

1. `gov release build --version 4.1.6 --trust-policy <TPS v1>`; surface checker exit 0.
2. Sign the candidate; `attach-signature`; tag `v4.1.6-rc1`.
3. Independent verification per `12` (on the production binary and `gov-test-profile`), including RT-50 (LP-1 with real
   4.1.2–4.1.5 binaries) and RT-80 [OP7].
4. Verification attestation.
5. If ACCEPTED:
   1. promote and sign the final;
   2. build binaries reproducibly;
   3. independent build attestation;
   4. `artifact-final.v2` signed by two `release-artifact` custodians;
   5. certification;
   6. TSS 2 referencing certification, attestation and artefacts;
   7. publish the state fingerprint.
6. If REJECTED: the attestation and any revocation are referenced in TSS 2, and a new candidate follows.

## Phase 4 — Consumer transition

| Consumer state | With a 4.1.6 binary | Path |
|---|---|---|
| Legacy layout, lock 1.1.0, historical kernel | `LEGACY` + `HISTORICAL_IDENTIFIED`, read-only | `gov trust verify-artifact` for the binary → `confirm-root` + `confirm-state` (or pins) → `gov update --apply --source <signed final 4.1.6>` → local `framework_update` trust gate → layout migration (`26` §7) and lock 3.0.0 |
| Legacy layout, unknown kernel | `LEGACY`, read-only | same |
| RoT-1 layout, eligible | normal, per freshness | — |
| Clean CI runner | `UNANCHORED` | state pin in the runner image (OP-7 a), or witness (OP-7 c) |
| Rollback 4.1.6 → 4.1.5 | **refused** (`SNAPSHOT_INELIGIBLE(historical)`) | newer eligible release, or `kernel reinstall` of 4.1.6 |
| 4.1.2–4.1.5 binary on a 4.1.6 project | fails before any write (LP-1) | retire legacy binaries |

## Phase 5 — Deprecations and follow-ups

- **Removed:**
  - `GOV_KERNEL_SOURCE` and `GOV_KERNEL_CACHE`;
  - path-string source labelling;
  - the `stage_payload` parent fallback;
  - decisions read from `manifest.json`;
  - the migration lock operation;
  - `load_migrations(&Path)`;
  - the tombstone `KERNEL_MANIFEST.json` and lock sentinel fields;
  - `gov decide` for trust gates.
- **Retained:** `GOV_CANONICAL_ROOT` (source selection only).
- **Later MINOR releases:**
  - `gov release fetch`;
  - profile statements (if WP-19 slips);
  - the MCP server (must adopt VU-11 before shipping);
  - optional supplementary transparency attestation.
