# Output 11 — Migration plan from 4.1.5

> **RoT-1 revision 5 — PROPOSED, pending fresh independent reviews; not approved, not implemented.**
> Revision 5: every phase below applies to revision 5 (read "revision 4" as "revision 5"). **Phase 0** adds the
> registration authority (OP-2), the reproducer set and quorum (OP-9), the verification processes (OP-8), the admitter
> registration and the publication of its digest in the channels. **Phase 2** adds WP-22 reproducible production builds
> (IR-REP-1…4: no `git rev-parse HEAD` provenance fallback in the production profile; normative path remapping; per-target
> cross-OS reproduction), WP-23 `gov-admit` and the shared admission vectors (`31`), WP-24 the compiled decision register and
> the Fact Threshold Check (`29`), WP-25 registration, reproduction and publication statements and `gov trust
> draft-registration` (`30`), WP-26 installation-state closed entry sets and root discovery (`18` §9.1–§9.2), WP-27
> allow-list confinement and the TCB-location rule (CR4-B-01). **Phase 3 step 5 and Phase 4** are replaced below.
> 4.1.5 stays immutable and REJECTED. Nothing in `release/releases/4.1.2…4.1.5`, or in any verifier or review directory,
> is edited. No phase below starts before fresh independent reviews accept revision 4 and the owner answers the D-0008
> gate.
>
> Revision 4 changes the plan:
> - **new work packages:** WP-20 (confined execution) and WP-21 (system pin directory and CI provisioning);
> - **changed work packages:** WP-3, WP-4, WP-9, WP-11, WP-12 and WP-14; WP-18 re-issues the migration chain without lock
>   operations;
> - **root ceremony additions:** exact precedence, the Overlay Surface, owner-domain slots, pin-currency parameters and,
>   optionally, production sources.

## Phase 0 — Review, approval, key ceremony (before any code)

1. **Fresh independent reviews of revision 4.** Trust and security (B); compatibility and transactions (C); synthesis.
   The architect session AR-0005 authored revision 4 and cannot review it.
2. **Owner decision.** Present D-0008 as a Human Decision Gate. The owner answers OP-1…OP-7 (`21`).
3. **Root ceremony** (offline), per OP-1 and OP-2:
   - root keys with threshold;
   - keys for `release-final` (+ standby), `release-candidate`, **`release-artifact` (≥ 2 custodians)**,
     **`build-attestation` (independent rebuilder)**, `verification-attestation`, `certification-status` (+ standby),
     `revocation`, `trust-state`, `retrieval-profile` and, only under OP-7 (c), `freshness-witness` (≥ 2 keys, KS-11), with grants satisfying the compiled whitelist (`05` §3);
   - root v1 signed; trust-root id computed;
   - the root fingerprint published in at least two independent channels (`06` §2).
4. **TPS v1.** `gov trust draft-policy` output for the 4.1.6 kernel. It contains:
   - the **Constitutional Surface Inventory**. The draft for review is `constitutional-surface/CONSTITUTIONAL_SURFACE_INVENTORY.yaml`,
     derived from the current `framework/`. It is re-derived after the WP-10 kernel path changes, and the change list is
     reviewed;
   - eligibility, with `min_release_sequence` = the first 4.1.6 candidate's sequence, `min_binary_version: 4.1.6`, and
     **`historical_releases[]`** for 4.1.2–4.1.5;
   - gating per OP-3;
   - the **`bootstrap`** block per OP-6 and OP-7, with `pin_max_validity_days`, `c3_currency_window_hours` and, where chosen, `max_anchor_age_days`, `witness_max_validity_hours` and `freshness_witness_threshold`;
   - the exact precedence registration, the Overlay Surface and the owner-domain slots (`23` §4.1, §7.2, §11);
   - under OP-2 (S1), `eligibility.production_sources[]`;
   - an empty `lowering_history`.

   It is reviewed and signed at root threshold.
5. **TSS 1** references root v1 and TPS v1; its state fingerprint is published.
6. **Test lineage** covering all twelve purposes, compiled only into `gov-test-profile`.

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
| **WP-3 anchors, freshness and currency** | inclusion satisfaction; pins with validity and the integrity predicate; `confirm-state` and in-gate state confirmation; currency proofs; `freshness-witness` (OP-7 c); freshness and currency axes; the single C0–C3 decision rule; monotonic VTS records with the accepted-TBM high-water and a witness-only clock high-water; SV-11 | `24` |
| **WP-4 Constitutional Surface** | evaluator of `floor_schema_version: 3`: presence; the YAML profile; exact precedence registration; the two-directional order; the directed project join; `SURFACE_VALUE_UNAVAILABLE` fallbacks; the Overlay Surface and migration whitelist; owner-domain slots; E7; consumer and decision-point registers, including the CR-07 reclassifications. The `csi_check.py selftest` cases are a conformance oracle (R-SURF-7). | `23`, `19` |
| WP-5 eligibility and floor | E1–E10, install authority with joined actor levels, computed weakenings, computed policy lowering | `19` |
| WP-6 secure filesystem and snapshot | `SecureDir`, link counts, KernelSnapshot generation (VU-11), EmbeddedSnapshot, installation state machine including `LEGACY` and occupation | `18` §1–§3, §6–§9 |
| WP-7 governed filesystem | every mutation site rewired; PPS including occupation entries and the transaction area | `18` §8 |
| WP-8 install transaction and recovery | `.governance-runtime/trust-tx`, VTS open-transaction registry, union trust record, exchange, recovery, `overlay.prev` weakening gate | `18` §5, `20` |
| **WP-9 layout and legacy containment** | FORMAT with layout; lock 3.0.0; occupation entries, typed by `st_mode`; the ignore rule `/.governance-runtime/*` + `!/.governance-runtime/migration`; layout migration of legacy projects; quarantine of legacy residue; project-strength vector over effective policy; doctor D033 naming mixed layouts | `26`, `08` |
| **WP-10 kernel path changes** | kernel values naming legacy paths move to the RoT-1 layout: `TOOL_POLICY.plugins.registry_path`, `mcp.registry_path`, `LEARNING_POLICY.upstream.forbidden_paths`, overlay templates (`PROJECT_POLICY.governance.*`, `REPOSITORY_CONTRACT` patterns), adapters (pointers, not canonical-source text), schemas naming paths. Re-derive and review the CSI draft. | `23` §6.2 |
| **WP-11 trust gates** | compiled kinds; `gov trust confirm` terminal challenge with a typed digest and, for C3 kinds, a typed state fingerprint; decision pins with `expires_at`, `approved_under_state` and the integrity predicate; `gov decide` refusal for trust gates; `by_kind` for non-trust gates | `27` |
| **WP-12 binaries** | Trust Base Manifest v2 with `binary.source` in `build.rs`; `gov version --trust`; `verify-artifact` A1–A10 with A4a/A4b attested source, A7 accepted-TBM high-water and A9 currency; `--stage rebuilder|custodian|publisher`; first-run self-check against the accepted-TBM high-water; reproducible build pipeline from `release.source` | `25` |
| WP-13 ingress rewiring | init, adopt batch 0, update, rollback, reinstall, recover, profile install, trust refresh | `09` §2 |
| WP-14 producer and publisher | `release build` with the surface checker and `release.source`; `attach-signature`; `promote` with source equality; `verify`; `trust draft-policy` (reductions in both directions, Overlay Surface, bootstrap); `publish --stage publisher` (never drops `artifacts[]`); `export` | `07` §7, `23` §6 |
| WP-15 agent consumption | `gov kernel show`, `skills show`, adapter pointers, VTS rendering record, D036 | `18` §12 |
| WP-16 conformance | `release_ingress` family; command register with operation classes; interception; private-key scan; floor-regression and TBM-profile pipeline checks; separate `gov-test-profile` | `02` §6, `05` §10 |
| WP-17 documentation | `docs/ARCHITECTURE.md` §4.4a; release and distribution protocol (fingerprints, surface registration, binary acceptance, OP-6/OP-7 ceremony, legacy binary retirement) | `06`, `25`, `26` |
| WP-18 migration | **Re-issue the 4.1.6 migration chain without the historical `set_lock_field` operations**, which the revision-4 checker refuses (`evidence/CSI-check-release-4.1.5.json`, exit 3; `28` A-R4-04). `migrations/M-4.1.5-4.1.6.yaml` holds notes, `regenerate_adapters`, an index rebuild, and only whitelisted Overlay Surface operations. The install transaction performs the layout migration, including the ignore rule; a migration operation never does. | `08` §4, `23` §11.3, `26` §7 |
| WP-19 profiles (may slip) | `gov profile install`, CAS, host verification | `10` |
| **WP-20 confined execution** | `confine::spawn` for product and test commands, tool commands, plugin processes and hooks: Landlock ABI ≥ 1 or a mount namespace; a macOS sandbox profile; a Windows restricted token or AppContainer. Refusal where unavailable; trust decisions before children. | `24` §3.5, `09` R-CONF |
| **WP-21 system pin directory and CI provisioning** | OS-resolved system pin directory; integrity predicate; runner-image documentation (root-owned `/etc/gov`, job run as another user, re-provisioning before `valid_until`) | `24` §3.2, §3.5; `06` §3 |

## Phase 3 — Candidate, verification, promotion, certification, binaries, publication

1. `gov release build --version 4.1.6 --trust-policy <TPS v1>`; surface checker exit 0.
2. Sign the candidate; `attach-signature`; tag `v4.1.6-rc1`.
3. Independent verification per `12` (on the production binary and `gov-test-profile`), including RT-50 and RT-50b (real
   4.1.2–4.1.5 binaries), RT-80 [OP7], RT-101…RT-127 and the distinguishing scenarios of `12` §8.
4. Verification attestation.
5. If ACCEPTED:
   1. promote and sign the final;
   2. (revision 5) the **registration ceremony** checks first-hand verification records, upstream toolchain checksums, its own
      `content_digest` (and, under OP-9 (d), its own reproduction) and signs the release registration (`30` §5);
   3. (revision 5) n independent reproducers build every registered target and the admitter from the registered source with
      inputs by digest, sign one-signature reproductions and confirm first-hand to the publisher (`30` §7);
   4. certification (optional);
   5. TSS 2 referencing the registration and exactly one quorum-reproduced digest per target (`30` §8);
   6. publish the state fingerprint and the admitter digest in the independent channels.
6. If REJECTED: the attestation and any revocation are referenced in TSS 2, and a new candidate follows.

## Phase 4 — Consumer transition

| Consumer state | With a 4.1.6 binary | Path |
|---|---|---|
| Legacy layout, lock 1.1.0, historical kernel | `LEGACY` + `HISTORICAL_IDENTIFIED`, read-only | (revision 5) **`gov-admit` admits the 4.1.6 binary with the typed state fingerprint (the legacy binary never verifies it; `31` §7)** → `confirm-state` on the admitted binary (or protected pins) → `gov update --apply --source <signed final 4.1.6>` → local `framework_update` trust gate with the typed state fingerprint (currency proof) → layout migration (`26` §7, including the ignore rule) and lock 3.0.0 |
| Legacy layout, unknown kernel | `LEGACY`, read-only | same |
| RoT-1 layout, eligible | normal, per freshness | — |
| Clean CI runner | `UNANCHORED` | (revision 5) image build runs `gov-admit`, writes a root-owned admission record with `valid_until`, and provisions a protected state pin naming the TSS used for C3 (OP-7 a), or witnesses at threshold (OP-7 c) |
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
