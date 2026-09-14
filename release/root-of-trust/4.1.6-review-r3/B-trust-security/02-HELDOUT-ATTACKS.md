# 02 — Held-out attack register RV3-B-A01…A18 (review r3 B)

These attacks were authored by this review (AR-0002). None is an acceptance case of `12-ACCEPTANCE-TEST-PLAN.md`; the
nearest existing case is named, with the reason it does not cover the attack.

## Evidence classes

| Class | Meaning |
|---|---|
| **E** | Executed against the real 4.1.5 binary or the pack's own checker (`constitutional-surface/csi_check.py`). |
| **C** | Computed in `evidence/RV3-B-M-reference-model.py`. This is an independent encoding of revision 3's rules, written from the pack text. |
| **K** | Code reading of the 4.1.5 runtime, which revision 3 does not change where cited. |
| **D** | Design reading of the pack at `ca77a43`. |

## Shared scenario world

Used by A02–A13 unless stated otherwise:
- **Published state.** TSS t1 → t5 → t9 → t10. t9 is an emergency revocation of release R7 (revocation `rv7`), with no TPS raise; `17` §8 only says SHOULD raise. t10 is its heartbeat.
- **Adversary's view.** A2 or A5 strips t9, t10 and `rv7`, and commits R7 as the installed release.
- **Runner binary.** Compiled at t5.

## Register

| ID | Attack | Adversary | Expected secure outcome | Revision 3 as written | Class, evidence | Nearest RT (why not covered) | Finding |
|---|---|---|---|---|---|---|---|
| **RV3-B-A01** | A kernel that changes **only** POLICY_PRECEDENCE modes to `immutable`: `authority_levels_required.*` (floor), `never_index_classes` (additive), `agent_resolvable_when.max_radius` (ceiling). The project overlay raises `resume_control` to L5, adds `confidential` to never-index with `product/customers/**` classified confidential, and narrows `max_radius` to R0. | A7 (`release-final`) + A2 (Git delivery; no gate at use); or a future release, or an honest owner "tightening", through `framework_update` | Precedence changes that refuse accepted project strengthening are weakenings: E7 flags them, or the join keeps project strengthening. Project-strength detection sees the effective loss. | **Checker exit 0**; surface-eligible; join `immutable` on all three keys. On the 4.1.5 binary, both roots `verified: true`: L4 `resume` succeeds (genuine: `AUTHORITY_DENIED`); the confidential file is indexed and retrievable (genuine: excluded); an L3 agent answers an R1 gate (genuine: `AUTHORITY_DENIED`). The overlay is byte-identical, so `19` §9 and `26` §6 compute nothing. | E: `evidence/RV3-B-A01-precedence-immutable.{py,json}` | RT-75 (only overridable insertion, floor↔ceiling, `default_mode`, layers); RT-99 (overlay deletion only) | **H1** |
| **RV3-B-A02** | Clean CI runner whose state pin was baked into the image at t5, 400 days old (and 100 days old). | A2/A5 | Refuse C2/C3, or never present as current. The pack claims "(a) … makes the review's B5 class impossible on every machine" (`24` §9, `21` OP-7). | (a), (c), (d): `ANCHORED(5, pin, 400d)`; R7 usable as C2 policy root; C3 freshness and eligibility pass; `current` label permitted. (b): refused at 400 days, allowed at 100 days. | C: model `RV3-B-A02`, `B5_r3_…`, matrix | RT-80 M2 (pin present vs absent only); RT-37(c) (unanchored only) | **H2** |
| **RV3-B-A03** | A2 commits `PROJECT_POLICY.tests.product_test_command`. The real 4.1.5 `gov verify product` executes it as the invoking account, and it writes `.config/gov/trust-state-pins` and `.config/gov/approved-trust-decisions`. The model then gives the runner a rewritten pin at t5. | A2 whose code runs in the pin-reading account (`gov`-run product or test command, tool install command, plugin, CI build step, agent tool call) | A pin or decision pin writable by the invoking account is not an anchor or approval (TA-9). | **Executed:** `ran: true`, `uid=1000`; both files written (owner uid 1000, mode 0644); the account-database home is writable by that uid. **Model:** every stateless runner, and a runner with a current pin whose file is rewritten, becomes `ANCHORED(5, pin, 0d)` with R7 usable, under every OP-7 option. | E: `evidence/RV3-B-A03-A14-A16-probes.{py,json}`; C: model `RV3-B-A03` | RT-91 (digest binding only); RT-80 (no writer identity) | **M2**, feeds H2 |
| **RV3-B-A04** | An operator decision pin written by a same-account process for `framework_update`, `weakening`, `project_strength` and `downgrade`. | Agent tool call, plugin, repository build step | `27` §3.3: a trust gate is never answerable by any agent path | `framework_update`, `weakening` and `project_strength` authorised; `downgrade` refused (`local_terminal_only`) | C: model `RV3-B-A04` | RT-91 (writer not tested) | **M2** |
| **RV3-B-A05** | Lift a WITHDRAWN certification with a new CERTIFIED (certification key) and a new TSS (trust-state key), both referencing the ACCEPTED attestation issued **before** the withdrawal | A7 ×2: `certification-status` + `trust-state` | `05` §3 and `17` §3: a lift needs three distinct keys | Lifted with two new signatures; no attestation key used. The architect's P4r3 B2 scenario lifts with the same reused attestation `a1`. | C: model `RV3-B-A05` | RT-97 ("referenced with attestation → lifted"; reuse not distinguished) | **M1** |
| **RV3-B-A06** | Under OP-7 (c), a trust-state key signs a 1-day witness TSS 100 that chains t1 and t5 and omits `rv7`. It is delivered to a stateless runner. | A2 + A7 (`trust-state`, threshold 1; scheduled-signing custody under (c)) | `17` §15, `05` §1: trust-state theft is a freeze only | `WITNESSED(100)`; C0–C3 allowed; R7 is a C2 policy root and passes C3 freshness and eligibility. A machine holding t10 sees `REGRESSION` (freeze). | C: model `RV3-B-A06` | RT-98 (witness replay, expiry and clock only) | **H2** |
| **RV3-B-A07** | A statement with `issued_at` 100 years ahead: a release candidate (lowest-custody key) and, separately, a witness TSS | A7 `release-candidate`; A7 `trust-state` | At most a time-bounded availability loss, cleared by key rotation or re-anchoring | OP-7 (b): `ANCHOR_EXPIRED` persists after the statement is gone and a human re-anchors. OP-7 (c): honest witnesses stay rejected. Both are permanent under the monotonic high-water. | C: model `RV3-B-A07` | RT-98 (clock rolled back only) | **M3** |
| **RV3-B-A08** | A `release-final` thief signs F-evil. It is promoted from the genuine, attested candidate C11 with an identical kernel tree, so V8 passes, but its `release_commit` is `commit-evil`. The rebuilder reproduces `commit-evil`. Two `release-artifact` custodians sign, as their stated check is "carries at least one build attestation". The TSS references the artefact. | A7 `release-final` + release-pipeline input (A5/A6): the review r2 H3 adversary | `25` §7: one `release-final` key cannot mint an accepted malicious binary | `verify-artifact` **ACCEPTED**. With review r2 CD2-3's attested-source requirement: `ARTIFACT_SOURCE_UNVERIFIED`. | C: model `RV3-B-A08`; D: review r2 V8 text (`d37b05c` `04` V8: identical `kernel.tree_digest` only), `25` §3–§5, `05` §7 rule 6 | RT-92 (no source case) | **H3** |
| **RV3-B-A09** | `05` §9 playbook after a `release-artifact` compromise: revoke, then "TSS stops referencing them" | Honest owner | Durable remedy | TSS 12 without the artefact is non-admissible (`artifacts ⊇` rule, `17` S4(d)). Every verifier holding TSS 11 is at `REGRESSION` (C0). | C: model `RV3-B-A09` | none | **M4** |
| **RV3-B-A10** | Unanchored machine under OP-7 (d) with an unresolved higher TSS (`INCOMPLETE`) | A1/A2 | One rule | `24` §4.3 literal rows allow C2; `17` §7 requires `KNOWN` for C2 | C: model `RV3-B-A10` | none | **L1** |
| **RV3-B-A11** | OP-7 (c) with a 1095-day human anchor | A12 | One rule | `24` §4.3 and §9 allow C2/C3; `24` §5.7 says (c) refuses for lack of a fresh witness | C: model `RV3-B-A11` | RT-80 follows the table | **L1** |
| **RV3-B-A12** | A runner with a **current** pin, or a first-install machine whose human anchor names t10. A2/A5 withhold t9, t10 and `rv7`. A trust-state key presents TSS 100 chaining only t1 and t5. | A2/A5 + A7 `trust-state` | `BELOW_ANCHOR` (`24` §5.1–§5.2); trust-state theft is a freeze only | Literal `24` §4.1 `BELOW_ANCHOR(have n < e)` and a componentwise epoch comparison both give not below; R7 is a C2 policy root and passes C3 freshness and eligibility. Only a chain-inclusion reading refuses. The architect's P4r3 `freshness()` uses `if seq < anchor["sequence"]`. | C: model `RV3-B-A12` | RT-80, RT-95 (no higher unchained TSS) | **H2** |
| **RV3-B-A13** | HO-0002 §3.4 matrix: 11 machine variants (M1–M7 of HO-0001 §3.2) × OP-7 (a)–(d) × 3 adversaries: A2/A5; A2 with same-account code execution; A2/A5 + trust-state key | as listed | No attacker-selected stale state becomes a current policy root or C3 target, except the stated unavoidable core (a machine anchored before the revocation) and the stated OP-7 (d) residual | 132 rows. R7 is a C2 policy root in 90 rows and passes C3 freshness and eligibility in 86. Beyond the unavoidable core (M3, M4, M6B, M7 anchored at t5): M1 with the trust-state key (A12); M2 with a current pin under the trust-state key or pin rewrite; M2 with stale pins under (a), (c), (d); M2/M5 without a pin under pin forging (all options) and trust-state key (c). M6A (holds t10) never. | C: model `MATRIX_machine_x_op7_x_adversary` | RT-80 (one adversary, no key compromise, no stale or forged pin) | **H2**, **M2** |
| **RV3-B-A14** | Kernel writes `on` for each of the 10 `bool_toward` floors with strict `true` | A7 `release-final` | Producer checker and binary parse identically | Checker exit 0 for all 10 (PyYAML reads `true`). The 4.1.5 runtime reads the string `"on"` (`TOOL_POLICY.plugins.refuse_on_pin_drift`, kernel `verified: true`). Every 4.1.5 `get_bool` default for these keys is `true`, so 4.1.5 does not weaken. | E: `evidence/RV3-B-A03-A14-A16-probes.{py,json}`; K: `grep get_bool` defaults | RT-73…79 (values, not YAML profile) | **L3** |
| **RV3-B-A15** | A2 edits the lock identity and removes an occupation entry, so the state is `PARTIAL`. An operator runs the documented `gov kernel reinstall --source <older release>`. | A2, A10 | Reinstall identity taken from the VTS per-project record; otherwise downgrade policy | `20` §8 step 3: "S authenticates to the **lock-recorded** identity"; `17` §7: reinstall needs no freshness and no gate. On a machine without a record, the older release installs through a transaction. | D | RT-43 (partial install) | **L4** |
| **RV3-B-A16** | Kernel changes only `project_tunable` leaves with runtime consumers: `MEMORY_POLICY.embedding.provider` (selects an `embed` plugin), `ARCHIVE_POLICY.default_retrieval_for_archive` (historical paths retrievable by default), `LEARNING_POLICY.upstream.aggregate_metrics_enabled` (upstream packet content) | A7 `release-final` | `05` §1: only root-registered content becomes a policy root; `23` §6.5: security decision points never read `project_tunable` | Checker exit 0; the kernel values are used by `19` §5.2 | E: probes JSON; K: `memory/embedder.rs:27,125`, `project.rs:170`, `paths.rs:288`, `upstream.rs:140` | RT-100 (build-time register, not the draft inventory) | **L2** |
| **RV3-B-A17** | TPS v(n+1) lowers non-surface fields: `eligibility.min_release_sequence`, `historical_releases[]`, `gating.mode` A→B, `local_terminal_only[]`, `bootstrap.op7_mode` a→d, `max_anchor_age_days` | A8-class (root threshold) or owner error | G11: values move down only by a computed, declared, per-project-gated lowering | `19` §10.6 computes reductions "for each leaf, precedence key, class and registration" of the surface; these fields are outside it | D | RT-78 (surface floors) | **L5** |
| **RV3-B-A18** | A `release-final`-signed migration `M-4.1.6-4.1.7.yaml` (a `transaction_input` file, checker exit 0, injection I08) uses `set_overlay_key` on `TOOL_PERMISSIONS.yaml` (`install_authority_roles`, role permission classes such as `SECRET_READ`) and on `PROJECT_EXCEPTIONS.yaml` | A7 `release-final`, installed through `framework_update` | `19` §9 / rule (20): every weakening of project-owned values needs the `weakening` trust gate | Not a weakening under `19` §9, whose four categories are classifications, overlay floor raises, contract exclusions and deleted non-overridable overlay keys. V10 checks only listing, digest and chain. R-MIG-6 says only "declarative". `set_overlay_key` writes any key of any overlay file (`runtime/src/migrations/framework.rs:91-230`). | D, K | RT-85 (`overlay.prev` only); RT-99 (classification deletion only) | **M5** |

## Constitutional-surface injections (HO-0002 §3.3)

Independent of the architect's self-test names. Evidence: `evidence/RV3-B-CSI-injections.{py,json}`.

| Case | Checker result |
|---|---|
| I01 unknown key `TOOL_POLICY.plugins.allow_unsigned_descriptors` | exit 2 (unclassified leaf) |
| I02 new policy file `policies/GATE_W_POLICY.yaml` | exit 2 (unclassified file) |
| I03 new top-level directory `hooks/pre-index.sh` | exit 2 |
| I04 stray `migrations/notes.yaml` | exit 2 |
| I05 `agent_resolvable_when: {}` | exit 2 |
| I06 new JSON policy `policies/EXPORT_POLICY.json` | exit 2 |
| I07 new skill under the pinned glob | exit 3 (digest not registered) |
| I08 new `migrations/M-999.yaml` under the `transaction_input` glob | **exit 0** (bound only by the `release-final`-signed `migrations[]`; see M5) |
| I09 floor leaf `max_radius` deleted | exit 0 (missing leaf takes the floor value, as specified) |

## Counts

| Item | Count |
|---|---|
| Held-out attacks authored | **18** (A01–A18) |
| Executed on the real 4.1.5 binary | 3 (A01, A03, A14) |
| Executed with the pack's checker | 4 (A01, A14, A16, injections I01–I09 as one set) |
| Computed in the independent model | 12 (A02, A04–A13, plus B1–B6 re-execution) |
| Design or code reading only | 3 (A15, A17, A18; A08 is also design-backed) |
| Claim of the pack contradicted | 18 of 18 |
| Blocking (HIGH) | 5 attacks across 3 findings (A01 → H1; A02, A06, A12, A13 → H2; A08 → H3) |
