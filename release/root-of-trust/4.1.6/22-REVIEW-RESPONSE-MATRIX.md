# Output 22 — Response matrix to the independent review of revision 3

> **RoT-1 revision 4 — PROPOSED, pending fresh independent reviews; not approved, not implemented.**
> - **Review answered:** `release/root-of-trust/4.1.6-review-r3/` (synthesis `79a09a1`; panel B `7d8c73a`, C `9e013c1`).
>   It reviewed revision 3 (`ca77a43`) and returned `ROOT_OF_TRUST_ARCHITECTURE_REJECTED`.
> - **Task:** HO-0005.
> - **Scope:** every consolidated finding of review r3: RV3-H1…RV3-I1, CR-01…CR-12 and C-1…C-5. Also the correction
>   delta CD3-0…CD3-4, the §7 re-review entry criteria, and the owner requirements of HO-0001 §3–§4.
>
> This matrix claims **no finding as accepted or closed**; acceptance is the next reviewers' decision. Status vocabulary:
> - **ADDRESSED — executed**: real legacy binaries, real Git or the pack's checker were run against the revision-4 rules;
> - **ADDRESSED — reference**: a model or checker that encodes the revision-4 rules was run (with conformance-oracle
>   mutants where named);
> - **ADDRESSED — specification only**: not executable before implementation; the acceptance scenario is named;
> - **CARRIED — named test**: a bounded residual or engineering constraint, stated with its test;
> - **RESTATED**: owner-option text, corrected from the revision-4 rules; nothing decided.
>
> No row is marked addressed on untested evidence. Where revision 4 uses a mechanism other than the one the correction
> delta suggests, the row says so. `28` explains why each blocking class survived earlier corrections.

## 1. Evidence produced by revision 4 (`evidence/`, `constitutional-surface/`, `examples/rev4/`)

All runs were scratch-only: `GOV_*` stripped, `HOME` and `GOV_KERNEL_CACHE` in scratch. Commands, times and exit codes are
in `evidence/EVIDENCE-RUN-LOG.json`.

| ID | Evidence | Result |
|---|---|---|
| **CSI** | `CSI-check-*.json` (`csi_check.py check`, revision-4 inventory) | `framework/`: 113 files, exit 0. 4.1.5 payload: 121 files, exit 3 (4 migration problems: historical `set_lock_field`). 4.1.5 with lock operations removed: exit 0. 4.1.2: exit 2 (1 unclassified leaf, 62 required missing, 65 violations). 4.1.3: exit 2 (15 missing, 65 violations). 4.1.4: exit 2 (6 missing, 64 violations, 44 precedence registration differences). |
| **CSI-ST** | `CSI-selftest.json` | **56 of 56** cases as expected (S00–S55) |
| **P1r4** | `P1r4-project-strength-and-absence.{py,json}`; executed on the real **4.1.5** binary | **Part A:** 343 order combinations, 0 unsound pairs, 0 joins dropping strengthening; removals R01–R09 all exit 2. **Part B:** 9 attack cases (5 strengthening modes to `immutable`, the review's three-rule example, POLICY_PRECEDENCE deleted, 2 TPS tightenings). In 9/9 the revision-3 effective kernel loses project strengthening and the revision-4 one keeps it; the revision-4 reference equals the binary's `policy effective` in 9/9. Harm assertions flip where observable: (a) authority, (b) indexing and retrieval, (c) gate. Checker: precedence-only kernels exit 3, deletion exit 2; TPS v2 reductions exit 6 without history and 0 with. **Part C:** the strength vector reports every revision-3 loss (9/9) and is quiet for every revision-4 kernel (9/9). Release-signed migrations: M1–M4, M6 and M7 refused before any write; M5 passes the whitelist and needs the weakening gate; M8 control neither. **Part D:** composition; revision-3 replacement semantics lose the project class, the directed join keeps it. 12 consumers initialised. |
| **P4r4** | `P4r4-trust-state-model.{py,json}` (independent of P4r3) | **54 of 54** scenarios hold. **9 of 9** conformance-oracle mutants detected. Machine × OP-7 × adversary matrix: 132 rows, of which 77 refused, 42 stated core, 13 OP-7 (d) residual; 0 unstated; 0 labelled `current`. No hash-cyclic construction. |
| **VA4** | `VA4-verify-artifact-source-scenarios.{py,json}` | **16 of 16** as expected. 12 attacks refused. 3 minimum capability sets accepted and documented: route S; route S under OP-4 "no"; route B. |
| **P3r3** | `P3r3-rerun-r4-summary.json`; the harness unchanged since `ca77a43`; real 4.1.2–4.1.5 | 2085 jobs. `summary`, `property_L3`, `chain_summary` and `job_count` **equal** to the committed revision-3 output. |
| **LR2** | `LR2-installation-state-and-strength-reference.{py,json}`, `LR2-spec.json` | The installation state machine and the revision-4 strength vector applied to 24 real trees left by reviewer C's and synthesis D's legacy probes. Every tree with legacy entries is `PARTIAL(occupation)` or `LEGACY`; intact trees and clean clones are `COMPLETE`. RV3-D-A07 fresh clone: `PARTIAL(occupation)` on the revision-3 layout, `COMPLETE` on revision 4. `PROJECT_STRENGTH_WEAKENED` on A05a (3 failures) and A05c (9) on both layouts; none on A05b and the controls. |
| **SCH** | `examples/rev4/validation.json` | every schema valid JSON Schema 2020-12; 9 revision-4 instances validate; the inventory validates against the revision-4 inventory schema; 4 revision-3 instance shapes are refused by the revision-4 schemas |

### 1.1 Review r3 probes re-run against revision 4

| Probe (origin) | Output | Result |
|---|---|---|
| RV3-B-A01 precedence to `immutable` (B), real 4.1.5 + revision-4 checker and library | `rerun-RV3-B-A01-precedence-immutable.json` | `passes_E7_reference_checker: false` (exit 3). The 4.1.5 binary still consumes whatever kernel it is given, so B's consumption part still shows the loss. Consumption of the revision-4 effective kernel is P1r4 part B. |
| RV3-B-A03/A14/A16 (B), real 4.1.5 + revision-4 checker | `rerun-RV3-B-A03-A14-A16-probes.json` | **A03:** the `gov verify product` child still writes both pin files as the invoking account, mode 0644 (legacy behaviour; revision 4 ignores such files and confines the child). **A14:** checker exit 2 for all 10 `bool_toward` leaves written `on`; the runtime reads the string `"on"`. **A16:** checker exit 3. |
| RV3-B CSI injections I01–I09 (B) | `rerun-RV3-B-CSI-injections.json` | I01–I06 exit 2; I07 exit 3; I08 exit 3; I09 exit 2. I08's exit comes from the base 4.1.5 payload's historical `set_lock_field` operations; the injected migration carries no operation, so it adds no finding. Overlay-writing migration shapes are P1r4 part C. |
| RV3-D-A01/A02 lattice (D), revision-4 library | `rerun-RV3-D-precedence-lattice.json` | A01: 36 pairs, no unsound pair. A02, each of the 5 modes: a TPS registering `immutable` is a computed reduction needing history and the gate; the effective project-layer mode is unchanged; no strengthening removed. |
| RV3-D-A09/A10 (D), unmodified | `rerun-RV3-D-surface-forward-compat-and-removal.json` | R01–R09 exit 2. F01/F05/F06/F07/F09 exit 3: the unmodified fixture adds policies without copying their precedence rules into the kernel, which exact registration refuses. The R07 effect uses the revision-3 join formula, which revision 4 no longer uses. |
| RV3-D-A09/A10 (D), release-consistent copy | `RV3-D-A09-A10-rerun-r4-release-consistent.{py,json}` | F01, F05, F06, F07, F09 exit 0 (forward compatibility by inventory data); F02, F12 exit 2; F03, F04, F08, F10, F11 exit 3; R01–R09 exit 2 |
| P1r3 (architect r3), real 4.1.5 + revision-4 library | `rerun-P1r3-against-r4-lib.json` | coverage 0 unclassified; every §3.1 case has effective values equal to genuine; harm verdicts (a)–(e) true |
| C `build_base`, `run_destructive`, `occ_removal`, `full_removal_and_merge`, `durability` (C), real binaries and Git | `rerun-RV3-C-*.json` | **destructive:** 84 runs of 4 binaries, 0 writes, property holds. **Partial removal:** legacy `init --force` fails `IO_ERROR` after creating a legacy kernel manifest; `governance/trust` unchanged; RoT-1 emulation `PARTIAL(occupation)`. **Full removal:** a legacy verified install; `product/restricted-plan.md` retrievable by the legacy binary; `governance/trust` unchanged; RoT-1 `PARTIAL(occupation)`. **Merge:** `CONFLICT`, then `governance/framework.lock~legacy`. **Durability:** clone, archive and `clean -fdx` keep the types; sparse checkout omits the occupation; revert restores the legacy layout. |
| RV3-D-A05/A06/A07 (D), revision-3 layout | `rerun-RV3-D-legacy-git-restore.json` | A05a/A05c: legacy verified; the post-migration classified file is retrievable. A06: the legacy CIT writes `governance/trust/**` on restored trees; the intact control refuses with `NOT_INSTALLED`. A07: the idiom lists the occupation; a fresh clone lacks it. |
| RV3-D-A05/A06/A07 (D), revision-4 layout (ignore-rule delta) | `RV3-D-A05-A07-rerun-r4-layout.{py,json}` | A05, A06: the same legacy outcome (documented LR-2). A07: the idiom lists nothing; a fresh clone has the occupation; `COMPLETE`. |

**Not re-run unmodified (stated):**
- **Reviewer B's `RV3-B-M-reference-model.py`** encodes the revision-3 rules. Its constructions (RV3-B-A02, A05…A13 and the
  132-row matrix) are re-encoded against the revision-4 rules as named P4r4 scenarios.
- **Synthesis D's `RV3-D-oracle-anchor-artifact.py`** loads `P4r3`. Its constructions (RV3-D-A11, A12, A13, A15) are P4r4
  scenarios. Its sensitivity claim (A11) is answered by P4r4's mutant `M-sequence-anchor`, which fails three scenarios.
- **Review r2 `P2-gate-record-forgery.py`** is unchanged by revision 4 (repository records remain requests). Reviewer B
  re-ran it on 4.1.5; the reference is P4r4 `R3_gate_record_from_repository`.

## 2. Blocking classes (BC-1 … BC-4)

| Class | Findings | Revision 4 mechanism (removes the input, or adds a condition) | Specified in | D-0008 rules | Evidence | Status |
|---|---|---|---|---|---|---|
| **BC-1** constitutional-surface soundness for project-owned strength and absence | RV3-H1; root of RV3-M5; precedence case of RV3-M7 | **Removes the kernel from effective precedence:** POLICY_PRECEDENCE must equal its registration (`precedence_unregistered`); project-layer precedence comes from registrations only, joined with the project's held registration until a per-project gate. **Removes absence as an input:** required presence (`surface_required_missing`); pinned fallback or `SURFACE_VALUE_UNAVAILABLE`. **Sound order** for comparing registrations: two-directional admitted sets; a TPS removing admitted strengthening is a computed reduction. **Directed join:** no refusal discards an admitted component. **Output-based detection:** the project-strength vector over effective policy and every Overlay Surface input. **Migrations** default-deny over root-registered targets. One YAML profile. **Different from CD3-1 (2) in kind:** the delta suggested refusing a differing kernel rule "as unregistered values already are" and otherwise joining; revision 4 also removes the kernel rule from the join entirely. | `23` §3.5, §3.6, §4, §11; `19` §5, §9, §10.6; `26` §6; `09` R-SURF-8…12, R-MIG-5, R-MIG-7 | (3), (6), (20) | P1r4 parts A–D; CSI-ST S22, S26–S40, S45–S49, S53–S55; re-runs of RV3-B-A01, D lattice, D-A09/A10; LR2 strength vector | **ADDRESSED — executed** (harm assertions on real 4.1.5 consuming revision-3 and revision-4 effective kernels; checker) **and reference** (order, reductions). Implementation evaluator and in-binary vector: specification only, RT-106…RT-109, RT-99. |
| **BC-2** anchor satisfaction and anchor currency | RV3-H2 | **Removes the supplier's sequence number:** anchors are satisfied only by inclusion; statements outside the anchored chain are never effective. **Removes "anchored once" as currency:** mandatory pin validity; a currency proof (P1 anchoring event within the window, P2 in-gate typed fingerprint, P3 witnesses ≥ 2) for C3 and binary acceptance; no `current` label. **Removes the trust-state key from currency:** separate `freshness-witness` purpose (KS-11), C3 threshold ≥ 2. **Removes the governed account from pin writers:** integrity predicate, system pin directory, confined execution, TA-9 restated. One decision rule; witness-only clock high-water; accepted-TBM high-water. **CD3-2 (2):** both a bound and an exact disclaimer. **CD3-2 (3):** a separate purpose plus a threshold, and C3 never on a witness alone below threshold. | `24` §3–§4, §8–§10; `17` S4, §7, §15; `05` §1, §3; `27` §3; `25` A7, A9; `09` R-ANCH-1…9, R-CONF-1…3 | (7), (18), (19), (21) | P4r4 54/54, 9/9 mutants, 132-row matrix; re-run RV3-B-A03 (the writer is real) | **ADDRESSED — reference.** Implementation: specification only, RT-80, RT-101…RT-105, RT-113, RT-116, RT-119. |
| **BC-3** built-source legitimacy of production binaries | RV3-H3 | **Removes `release-final` from the choice of source:** `release.source` in candidate and final with V8 source equality at every verifier; verification attestation v2 names the source; `verify-artifact` A4a (build attestation source = TBM source) and A4b (ACCEPTED attestation of the candidate, referenced by the effective TSS, same source, no REJECTED attestation or negative); custodial stages at rebuilder, custodians and publisher. Minimum capability sets re-derived (route S: 3 keys + pipeline input, 2 under OP-4 "no"; route B: 4 keys over 3 purposes). Owner option (S1) root-registered production sources. **Extends CD3-3 (1):** source identity includes `source_tree_digest` (SHA-256 of `git archive`), not only the commit id. | `25` §4–§7, §9; `04` V8; `05` §1, §3, §7; `07` §3, §7; `09` R-ART-5…7, R-REL-6, R-REL-9 | (9), (17) | VA4 16/16; P4r4 RV3-B-A08 and mutant `M-source-from-release-commit`; schemas v2 | **ADDRESSED — reference.** Implementation: specification only, RT-115, RT-92. |
| **BC-4** OP-2, OP-4, OP-7 consequence statements | follows BC-2, BC-3; RV3-D-A08; RV3-L2, RV3-L6 | Restated from the revision-4 rules with evidence per consequence. **OP-7:** (a)–(d) with who selects which state and for how long; pin-currency parameters; witness authority above a single threshold-1 key with custody consequences; (d) scoped to the newest TSS. **OP-2:** binary blast radius per source-authority choice S0–S3; `release-final` threshold and root co-signature relative to CD3-3; `release-final` sentence corrected. **OP-4:** consequences of "no" after CD3-3. **OP-3:** decision-pin integrity. | `21` | — | VA4 routes; P4r4 matrix and `RV3-D-A04_op7_d_scope` | **RESTATED** — proposals labelled; nothing decided; verification RT-127 |

## 3. Findings RV3-H1 … RV3-I1

| Finding | Revision 4 change | Specified in | Evidence | Status |
|---|---|---|---|---|
| **RV3-H1** | BC-1 (§2) | §2 | §2 | ADDRESSED — executed and reference; RT-106…RT-109 |
| **RV3-H2** | BC-2 (§2) | §2 | §2 | ADDRESSED — reference; RT-80, RT-101…RT-105 |
| **RV3-H3** | BC-3 (§2) | §2 | §2 | ADDRESSED — reference; RT-115 |
| **RV3-M1** lift reuses the pre-withdrawal attestation | MS-2: a lift needs an ACCEPTED attestation naming the negative (`lifts_negative_statement_digest`); ≥ 3 distinct keys | `17` §2, §3; `05` §3; `schemas/verification-attestation.schema.json` 2.0.0 | P4r4 `RV3-B-A05_lift_requires_post_dating_attestation`; mutant `M-lift-reuses-pre-negative-attestation` | ADDRESSED — reference; RT-112, RT-97 |
| **RV3-M2** pins and decision pins writable by the governed account | integrity predicate; system pin directory; decision pins with `expires_at` and `approved_under_state`; write confinement of `gov`-run repository and plugin commands; TA-9 and `27` §3.3 restated | `24` §3.5; `27` §3.2–§3.3; `01` TA-9; `09` R-ANCH-6, R-GATE-7, R-CONF-1…3; `schemas/trust-decision-pin.schema.json` | re-run RV3-B-A03 (the real child writes both files as the invoking uid, mode 0644, which the predicate ignores); P4r4 RV3-B-A03, A04; mutant `M-pins-writable-by-governed-account` | ADDRESSED — reference (predicate, model) with the writer observed by execution; confinement and predicate implementation: specification only, RT-103 (a)–(f) |
| **RV3-M3** `issued_at` poisons the clock high-water | SV-11 refuses statements from the future; only witnesses raise the high-water; root-signed `bootstrap.clock_reset`. **Different from CR-06's wording:** witnesses are `freshness-witness` statements, not TSSs. | `24` §8; `17` §13; `05` SV-11; `19` §3 | P4r4 `RV3-B-A07_issued_at_high_water`; mutant `M-any-issued-at-raises-clock` | ADDRESSED — reference; RT-113 |
| **RV3-M4** playbook contradicts admissibility | revoke, never un-reference; the next TSS keeps `artifacts[]` and adds revocations | `05` §9; `17` §14 | P4r4 `RV3-B-A09_playbook_revokes_never_unreferences` | ADDRESSED — reference; RT-114 |
| **RV3-M5** weakening over four overlay categories; ungated migrations | class closed in BC-1 (the vector over effective policy and every Overlay Surface input). CR-02 whitelist: migration-writable targets per Overlay Surface key, default deny, nothing outside `governance/overlay/`. **Different in location from CR-02:** the operation × target registration is root-signed TPS data (compiled default deny), not a compiled list, so it evolves with the kernel templates at root threshold. | `23` §11; `19` §9; `26` §6; `09` R-MIG-5, R-MIG-7 | P1r4 part C (M1–M8; vector over real 4.1.5 effective kernels); CSI-ST S46–S49 | ADDRESSED — executed (vector) and reference (whitelist); RT-109 |
| **RV3-M6** occupation not robust to removal or Git restore | LR-2 restated with the reachable legacy outcome and the only bounds that hold (RoT-1 fails closed; strength loss reported where recorded; LR-4); doctor names mixed layouts; the ignore rule keeps the occupation through untracking | `26` §2, §8; `18` §9; `09` R-FMT-6 | re-runs of C `occ_removal`, `full_removal_and_merge`; D legacy restore on both layouts; LR2 (24 trees) | **CARRIED — named test.** The legacy outcome is executed; the RoT-1 bounds are reference-evaluated on the resulting trees. RT-81, RT-50b. |
| **RV3-M7** presence not checked; pinned/members fallback undefined; owner files outside the vector | required presence at E7; `SURFACE_VALUE_UNAVAILABLE` or the registered embedded value; owner-domain slots with `check-owner`, fail-closed absence on confirmed and unconfirmed machines, in the strength vector | `23` §3.5, §7.2; `19` §5.2; `09` R-SURF-9, R-SURF-12 | P1r4 A3 (R01–R09 exit 2) and R07 on real 4.1.5 (harms absent); D-A09/A10 release-consistent R01–R09 exit 2; CSI-ST S31–S40, S50–S52 | ADDRESSED — executed (R07 consumption; checker) and reference; per-decision-point fallback and owner files at run time: specification only, RT-107, RT-120 |
| **RV3-M8** A7 against an ambiguous high-water | A7 and the first-run self-check compare with the accepted-TBM high-water only | `25` §5 A7; `24` §8; `09` R-ART-2 | P4r4 `A_valid_realisable_TBM_t9_reference_t11`, `RV3-D-A13_realisable_tbm_order`; mutant `M-a7-against-tss-high-water` | ADDRESSED — reference; RT-116, RT-93 |
| **RV3-M9** plan cannot detect the classes | no expected result from architect evidence; RT-72(vi) withdrawn; a conformance oracle with 9 mutants and named distinguishing scenarios; realisable constructions; RT rows for RV3-B-A01…A18, RV3-C-A01…A10, RV3-D-A01…A18 with binary-observable harm assertions | `12` §1 rules 11, 13–15, §4b, §7b, §8; `13` §8 | P4r4 conformance oracle (executed: 9/9 mutants detected); `12` §7b tables | ADDRESSED — reference (oracle) and specification (plan) |
| **RV3-L1** decision-table conflicts | one decision rule, most restrictive row wins; `INCOMPLETE` refuses C2 under every option; (c) non-witness anchors follow (a) | `24` §4.3; `17` §7 | P4r4 `RV3-B-A10_incomplete_refuses_c2_under_d`, `RV3-B-A11_op7_c_non_witness_anchor` | ADDRESSED — reference; RT-119 |
| **RV3-L2** tunable keys at security decision points; `release-final` sentence | `MEMORY_POLICY.embedding.provider`, `reranker.provider` → pinned; `ARCHIVE_POLICY.default_retrieval_for_archive`, `LEARNING_POLICY.upstream.aggregate_metrics_enabled`, `HUMAN_GATE_POLICY.continue_independent_work` → floor; sentence names 52 `project_tunable` and 32 `release_bound` leaves | `23` §5.2; `05` §1; `21` OP-2 | re-run RV3-B-A16 (checker exit 3); CSI-ST S44 | ADDRESSED — executed (checker); consumer-register build: specification only, RT-111 |
| **RV3-L3** YAML 1.1 versus serde_yaml | one YAML profile: core booleans only; no anchors, aliases, tags, merge keys, duplicate or non-string keys | `23` §3.6; `09` R-SURF-10 | re-run RV3-B-A14 (exit 2 ×10); CSI-ST S41–S43 | ADDRESSED — executed (checker); binary: specification only, RT-110 |
| **RV3-L4** reinstall identity from the lock | identity from the VTS per-project record; the lock is a hint; downgrade policy relative to the record | `20` §1, §4, §5, §8; `09` R-RI-1 | none executable before implementation | ADDRESSED — specification only; RT-118 |
| **RV3-L5** non-surface TPS fields outside computed reductions | `min_release_sequence`, `historical_releases[]` removals, `production_sources[]` additions, `install_authority`, `gating.mode`, `local_terminal_only[]` removals, `op7_mode` toward (d), window increases, witness threshold decreases | `19` §10.6; `17` S3 | P4r4 `CR-10_non_surface_tps_reductions` | ADDRESSED — reference; RT-108 |
| **RV3-L6** OP-7 (d) scope | residual = binaries whose compiled TSS predates the newest TSS, including a revocation-only TSS | `21` OP-7; `24` §9; `17` §8 | P4r4 `RV3-D-A04_op7_d_scope`; matrix (13 (d) rows) | RESTATED — option text with reference evidence; RT-80, RT-127 |
| **RV3-L7** untracking idiom drops the occupation | ignore rule `/.governance-runtime/*` + `!/.governance-runtime/migration`; doctor names an absent occupation | `26` §2; `08` §2; `09` R-FMT-1 | `RV3-D-A05-A07-rerun-r4-layout.json` (real Git: idiom lists nothing; occupation in fresh clone); LR2 (`COMPLETE`) | ADDRESSED — executed; RT-122 |
| **RV3-L8** rotation invalidates anchored history | re-sign retained honest statements of the removed key before root N+1 | `05` §8–§9; `17` §9 | P4r4 `RV3-D-A16_rotation_resigns_retained_statements` | ADDRESSED — reference; RT-117 |
| **RV3-I1** caller-declared role | unchanged and stated: no trust gate depends on the declared role | `27` §5; `19` §8 | — | INFO — stated; RT-89 |

## 4. Carried requirements CR-01 … CR-12 (review r3 B `04`)

| CR | From | Where revision 4 specifies it | B's acceptance test → revision-4 test and evidence | Status |
|---|---|---|---|---|
| CR-01 | RV3-M1 | `17` MS-2; `05` §3 | RV3-B-A05 → RT-112; P4r4 `RV3-B-A05` (negative remains with the old attestation; lifted with a new one naming the negative; 3 distinct keys) | ADDRESSED — reference |
| CR-02 | RV3-M5 | `23` §11.3; `19` §9 | the five migrations and the `../../spec` target → RT-109; P1r4 part C M1–M7 | ADDRESSED — executed and reference |
| CR-03 | RV3-M2 | `24` §3.5; `27` §3.2–§3.3; `01` TA-9 | (a)–(e) → RT-103 (a)–(f); re-run RV3-B-A03; P4r4 RV3-B-A03, A04 | ADDRESSED — reference; implementation specification only |
| CR-04 | RV3-M4 | `05` §9; `17` §14 | RV3-B-A09 → RT-114; P4r4 | ADDRESSED — reference |
| CR-05 | RV3-L1 | `24` §4.3; `17` §7 | RV3-B-A10, A11 → RT-119; P4r4 | ADDRESSED — reference |
| CR-06 | RV3-M3 | `24` §8; `05` SV-11 | RV3-B-A07 and reset → RT-113; P4r4 | ADDRESSED — reference |
| CR-07 | RV3-L2 | `23` §5.2; `05` §1; `21` OP-2 | build fails on the draft classification; RV3-B-A16 exit 3 → RT-111; re-run A16 exit 3; CSI-ST S44 | ADDRESSED — executed (checker) |
| CR-08 | RV3-L3 | `23` §3.6 | RV3-B-A14; duplicate and merge keys → RT-110; re-run A14; CSI-ST S41–S43 | ADDRESSED — executed (checker) |
| CR-09 | RV3-L4 | `20`; `09` R-RI-1 | RV3-B-A15 → RT-118 | ADDRESSED — specification only |
| CR-10 | RV3-L5 | `19` §10.6 | RV3-B-A17 → RT-108; P4r4 `CR-10_non_surface_tps_reductions` (`witness_max_validity_days` is `witness_max_validity_hours` in revision 4) | ADDRESSED — reference |
| CR-11 | R2-M10 / RV3-M9 | `12` §7b | rows for RV3-B-A01…A18 with codes and harm assertions → present | ADDRESSED — specification (plan) |
| CR-12 | RV3-H2 reference | P4r4 (not P4r3) | the oracle returns `BELOW_ANCHOR` for RV3-B-A12 → P4r4 `RV3-B-A12_RV3-D-A12_higher_unchained_tss` holds; `M-sequence-anchor` fails it | ADDRESSED — reference |

**B's acceptance cases for the corrected blocking findings:**

| Case | Pass criterion (B) | Revision-4 evidence |
|---|---|---|
| H1: RV3-B-A01 for each mode, plus an honest owner tightening | E7 refuses, or project strengthening remains effective; harms absent on the binary; computed strength over effective policy reports any loss | P1r4: each of the 5 modes plus the three-rule example exits 3; the revision-4 effective kernel keeps strengthening on 4.1.5 with harms (a)–(c) absent where observable; TPS tightenings are computed reductions; the vector reports revision-3 losses and is quiet for revision 4 |
| H2: RV3-B-A02, A06, A12 and the A13 matrix | no stale state as a C2 root or C3 target labelled `ANCHORED`/`WITNESSED`, except the stated core and the (d) residual | P4r4: A02, A06, A12 hold; matrix 77 refused, 42 core, 13 (d), 0 unstated, 0 `current` |
| H3: RV3-B-A08 and a REJECTED-candidate variant | refused unless an ACCEPTED attestation covers the exact source and the final's commit equals the candidate's | VA4: `RELEASE_IDENTITY_MISMATCH(source)` and `ARTIFACT_SOURCE_REJECTED` |

## 5. Carried constraints C-1 … C-5 (review r3 C `04`)

| C | Requirement | Where | Test | Evidence | Status |
|---|---|---|---|---|---|
| C-1 | LR-2 restated with harm assertions (broadened as RV3-M6) | `26` §8 | RT-81, RT-50b | re-runs of C `occ_removal`, `full_removal_and_merge`; D legacy restore; LR2 | CARRIED — named test |
| C-2 | cross-device transaction area refused, typed and before any write; unanchored `PARTIAL` repairable | `18` §3; `20` §8; `09` R-FS-7 | RT-123 | — | CARRIED — specification only |
| C-3 | doctor names stray merge and partial-removal artefacts | `18` §9; `09` R-FMT-6, D033 | RT-124 | LR2 names `governance/kernel/KERNEL_MANIFEST.json` and `governance/project/DATA_SENSITIVITY.yaml` on the removal trees (reference) | CARRIED — named test |
| C-4 | occupation type by `st_mode` / `GetFileInformationByHandle` | `18` §3; `26` §2; `09` R-FMT-7 | RT-125 | — | CARRIED — specification only |
| C-5 | full-register RT-50 on a genuine 4.1.6 install with type-aware digests and a `governance/trust` digest | `12` RT-50; `09` R-FMT-5 | RT-50 | P3r3 re-run unchanged (on the hand-built layout; the genuine-install run needs the implementation) | CARRIED — specification only |

## 6. Correction delta CD3-0 … CD3-4 and rule text (review r3 `11`)

| Item | Applied as | Different mechanism? |
|---|---|---|
| CD3-0 retain | Retained: authentication core, whitelist and KS-1…KS-10, the constructor, the snapshots, GovernedFs and PPS; CSI as a root-signed TPS section, default deny, closed vocabulary and joins; release-local references, resolution, equivocation, cumulative chains, computed lowering, sticky negatives; no trust ingress without an anchor, unanchored machines read-only under (a)–(c), local confirmations; `release-artifact` ≥ 2, build attestation, TBM and A6; the occupation layout and LP-1; the transaction area, union records, VU-11, VU-12. | Deltas inside retained items: floor vocabulary v2 → v3 (presence, profile, directions); the ignore rule for the migration occupation; the historical 4.1.5 migrations (`set_lock_field`) now fail the checker (`28` A-R4-04); a TSS `expires_at` is no longer a currency witness. |
| CD3-1 (1) order sound in both directions | the two-directional admitted-set order, used for TPS computed reductions and the held registration | **Yes for the kernel:** kernel rules are compared by equality and never joined |
| CD3-1 (2) exact precedence registration | `precedence_unregistered`; TPS reductions with `lowering_history` and per-project gate | as proposed, and the kernel rule is removed from effective policy |
| CD3-1 (3) strength over effective policy; migrations default deny | the vector over effective policy and Overlay Surface inputs; migration-writable targets | the whitelist is root-registered data (see RV3-M5) |
| CD3-1 (4) absence not neutral | presence required at E7; pinned fallback or typed refusal; POLICY_PRECEDENCE deletion changes nothing | as proposed |
| CD3-2 (1) inclusion semantics for every anchor kind | `24` §3.4; `17` S4 (b); pin schema; P4r4 | as proposed |
| CD3-2 (2) currency bounded or disclaimed exactly | **both:** pin validity and C3 windows bound currency, and `CURRENCY_UNPROVEN` with no `current` label disclaims it | combined |
| CD3-2 (3) no single threshold-1 currency authority | separate purpose (KS-11), C3 threshold ≥ 2, compromise consequence stated | combined the first and third alternatives |
| CD3-2 (4) anchor and decision-pin integrity | integrity predicate, system pin directory, confined execution, TA-9 | **Adds** the system pin directory and confinement of every `gov`-run repository command |
| CD3-2 (5) restated blast radius | `17` §15, `05` §1, `25` TB-3, `21` OP-7 | as proposed |
| CD3-3 (1) bind source to independent verification | `release.source`, attestation v2, V8 at every verifier | **Extends** the source identity with `source_tree_digest` |
| CD3-3 (2) binding everywhere consumed | A4a, A4b; custodial stages rebuilder, custodian, root co-signer, publisher | as proposed |
| CD3-3 (3) true minimum capability set | route S, route B, route I in `25` §7, `05` §3, TB-3, `21` OP-2/OP-4 | as proposed; adds the OP-2 source-authority options |
| CD3-4 owner options | `21` OP-2, OP-3, OP-4, OP-7 restated | as proposed |
| §5 rule text (3), (6), (7), (9), (19), (20) | revised in `15` §3, §5 and D-0008; also (12), (17), (18) revised and **(21)** added | (21) is new: confined execution |

## 7. HO-0001 owner requirements

| Requirement | Where | Evidence |
|---|---|---|
| §3.1 constitutional-floor closure (review r3: NOT SATISFIED on project override controls and schema evolution through removal) | `23`, `19`, `26` §6 | CSI (113/121 files), CSI-ST 56/56, P1r4 A–D on real 4.1.5, re-runs of RV3-B-A01, D-A01/A02, D-A09/A10 |
| §3.2 new-machine trust bootstrap (NOT SATISFIED on stale-state currency) | `24`, `17`, `27` | P4r4 M1–M7, B5, RV3-B-A02…A13, RV3-D-A04, A12, A13, A15, INGATE, PIN_WINDOW; 132-row matrix |
| §3.3 binary and root authenticity (NOT SATISFIED on single lower-threshold key and source) | `25`, `05`, `04` V8 | VA4 16/16; P4r4 A27…A29, A_valid, RV3-B-A08 |
| §3.4 legacy-binary damage containment (SATISFIED; must not regress) | `26` | P3r3 re-run unchanged (equal); re-run of C destructive (84 runs, 0 writes); LR-2 restated with LR2 |
| §4 forward compatibility | `23` §7.1 | D-A09 release-consistent F01/F05/F06/F07/F09 exit 0 |

## 8. Re-review entry criteria (review r3 `11` §7)

| Criterion | State |
|---|---|
| 1. CD3-1…CD3-4 closed as classes in pack, schemas, D-0008 and ARCH-0002; both still PROPOSED | §2, §6; `schemas/` (x-schema-versions in `examples/rev4/validation.json`); D-0008 and ARCH-0002 revision 4, PROVISIONAL, `in_effect: false` |
| 2. P1r4 (executed), P4r4 (reference), `verify-artifact` source scenarios, P3r3 unchanged, every RV3-B/C/D probe against revision 4 | P1r4, P4r4, VA4, P3r3 (§1). Probes: §1.1. B's and D's model probes are re-encoded as P4r4 scenarios, not re-run unmodified, because they model revision-3 functions (stated in §1.1). |
| 3. Response matrix over RV3-H1…RV3-I1, CR-01…CR-12, C-1…C-5, no untested "resolved" | §3, §4, §5 |
| 4. Oracle distinguishes anchor semantics with realisable constructions; plan meets RV3-M9 | P4r4 mutant `M-sequence-anchor` fails 3 scenarios; no hash-cyclic construction (`A_valid_realisable_TBM_t9_reference_t11`); `12` §1 rules 11, 13–15, §4b, §7b, §8 |

## 9. Residuals (explicit; none presented as stronger than it is)

| ID | Residual | Defined in |
|---|---|---|
| RS-1, RS-1b, RS-1c, RS-2…RS-5 | core unseen metadata; C3 window; pin validity window; clock; A3 and the VTS; pins controlled by the repository writer; witness-key compromise | `24` §10 |
| VR-1…VR-4 | same-user modification between units of work; advisory locks; processes outside `gov`; profile runtimes | `18` §11 |
| RR-1…RR-3 | ineligible state after automatic rollback; machines without a record; A3 deletes records | `20` §10 |
| CS-1, CS-2 | classification review; ceremony frequency | `23` §10 |
| TB-1…TB-4 | binary TCB; rebuilder environment; minimum capability sets (route S, route B); insider source accepted by an honest verifier | `25` §10 |
| LR-1…LR-4 | unconverted working copies; occupation removal or Git restore (restated); explicit output paths; fresh clones accept the overlay | `26` §8 |
| TG-1…TG-3 | per-machine decisions; A3 with an unconfined shell; non-trust gates forgeable by A2 | `27` §7 |

## 10. Unresolved or not yet executable

- **Specification only (no implementation exists):**
  - write confinement and the pin integrity predicate on real platforms;
  - the currency axis and gate fingerprint UI;
  - the in-binary surface evaluator, directed join, strength vector and consumer-register build;
  - `verify-artifact` and its custodial stages on real binaries;
  - reinstall identity from the VTS record;
  - cross-device refusal, doctor naming of stray artefacts, and `st_mode` typing;
  - RT-50 on a genuine 4.1.6 install.

  Each has a named RT in `12`.
- **Examples.** `examples/rev4/` validates the new record shapes and fragments of the release statement and Trust Policy.
  No full signed release statement, TPS or TSS example is produced.
- **Owner decisions pending (not answered here):** OP-1…OP-7, including the OP-2 source authority (S0–S3) and the OP-7
  parameters.
- **Independence.** Revision 4 was written by a fresh architect session (AR-0005). That session did not author revisions
  1–3 or any review. It must be reviewed by fresh reviewers.
