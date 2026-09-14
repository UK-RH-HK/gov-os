# 02 — Adjudication of reviewer B and reviewer C (AR-0004)

**Vocabulary** (HO-0004 §2.2):
- `CONFIRMED`: severity kept or changed, with reason;
- `REFUTED`: with evidence;
- `DUPLICATE`.

Reproduction is recorded in `01-REPRODUCTION.md`, and D-Axx refers to `03-HELDOUT-ATTACKS-RV3-D.md`.

## Reviewer B (AR-0002, `7d8c73a`, role verdict `BLOCKING_FINDINGS_PRESENT`)

| B item | B severity | Reproduced | Adjudication | Reason |
|---|---|---|---|---|
| RV3-B-H1 precedence order treats `immutable` as strongest | HIGH | yes: A01 executed on 4.1.5 plus the checker, 0 differences | **CONFIRMED HIGH** → RV3-H1 | See the RV3-B-H1 detail below. |
| RV3-B-H2 anchors do not stop stale state becoming anchored-current | HIGH | yes: model byte-identical | **CONFIRMED HIGH** → RV3-H2 | See the RV3-B-H2 detail below. |
| RV3-B-H3 binary source not bound to verified source | HIGH | yes: model A08 byte-identical | **CONFIRMED HIGH** → RV3-H3 | See the RV3-B-H3 detail below. |
| RV3-B-M1 lift with two keys | MEDIUM | yes (model A05) | **CONFIRMED MEDIUM** → RV3-M1 | The architect's P4r3 B2 `K_lift` adds `c4` referencing `a1`, with TSS `t2` attestations `["a1"]`: the pre-withdrawal attestation. Two purposes' keys; affects withdrawal refusal, not authenticity or floors. |
| RV3-B-M2 same-account writers of pins and decision pins | MEDIUM | yes (A03 executed: both files, uid 1000, 0644) | **CONFIRMED MEDIUM** → RV3-M2 | See the RV3-B-M2 detail below. |
| RV3-B-M3 `issued_at` high-water poisoning | MEDIUM | yes (model A07) | **CONFIRMED MEDIUM** → RV3-M3 | Persistent availability loss; bounded fix. |
| RV3-B-M4 playbook contradicts admissibility | MEDIUM | yes (model A09) | **CONFIRMED MEDIUM** → RV3-M4 | `05` §9 against `17` S4(d) read directly. |
| RV3-B-M5 migrations outside the four computed categories | MEDIUM | yes (I08 checker exit 0) | **CONFIRMED MEDIUM** → RV3-M5 | Root shared with RV3-H1: project strength is not computed over effective policy. The totality part closes in CD3-1 (3); the operation × target whitelist is carried (CR-02). B asked whether CR-02 needs an architecture change: its totality part does, and it is placed in CD3-1. |
| RV3-B-L1 decision-table conflicts | LOW | yes (model A10, A11) | **CONFIRMED LOW** → RV3-L1 | — |
| RV3-B-L2 `project_tunable` keys read by security decision points | LOW | yes (A16 executed) | **CONFIRMED LOW** → RV3-L2 | A2 can already set overridable keys. |
| RV3-B-L3 YAML 1.1 versus serde_yaml | LOW | yes (A14 executed) | **CONFIRMED LOW** → RV3-L3 | No weakening in 4.1.5 defaults. |
| RV3-B-L4 reinstall identity from the lock | LOW | design | **CONFIRMED LOW** → RV3-L4 | No marginal harm over direct Git delivery of the same files. |
| RV3-B-L5 TPS fields outside computed reduction | LOW | design | **CONFIRMED LOW** → RV3-L5 | Root threshold needed. |
| RV3-B-I1 caller-declared role | INFO | — | **CONFIRMED INFO** → RV3-I1 | — |
| B prior-status table: R2-M4 `CLOSED` | — | P4r3 B3, E1, E2, E3 byte-identical | **CONFIRMED** | — |
| B prior-status table: R2-M6 `CLOSED` | — | P4r3 K1–K3 byte-identical; whitelist read | **CONFIRMED** | — |
| B prior-status table: other rows `NARROWED` | — | — | **CONFIRMED** | See `00-REVIEW-REPORT.md` §8. |
| B residual determinations | — | — | **CONFIRMED**, with RR-2 and RS-1 made exact in `05` | — |
| B residual determinations: OP-7 (d) accepted as stated | — | D-A04 | **CHANGED** to accepted with condition RV3-L6 | B's own matrix shows the (d) residual is not limited to binaries older than the newest TPS. |

### RV3-B-H1 detail

- **Mechanism.** Independently confirmed: the pack lattice yields 5 unsound pairs (D-A01).
- **Beyond B's example.** The class extends to a TPS tightening that needs no gate (D-A02) and to deletion of POLICY_PRECEDENCE, which passes the checker with 66 of 85 rules joined to `immutable` (D-A10).
- **Severity kept HIGH.**
  - It is the R2-H1 class with R2-H4's harm, executed on a real consumer.
  - The trigger is one threshold-1 key plus A2, or a routine owner release.

### RV3-B-H2 detail

- **Independent re-derivation.** Re-derived with the architect's unmodified functions (D-A12): sequence anchors bypassed by a single trust-state key; chain inclusion flips the result.
- **Reach beyond policy roots.** It reaches binary acceptance of a revoked genuine binary on pinned CI (D-A15).
- **Undetectable by the mandated oracle.** P4r3 cannot detect it (D-A11).
- **Unavoidable core.** Separated exactly in `10` RV3-H2; B's core rows are agreed.
- **Severity kept HIGH.**
  - Attacker-selected stale state becomes an anchored-current policy root, a C3 target and an accepted binary on automated machines.
  - The stated bound of the proposed option is false.

### RV3-B-H3 detail

- **Design verification.**
  - Revision 3 `04` V8 reads "as revision 2", and `d37b05c` `04` V8 binds by identical `kernel.tree_digest` only.
  - `25` A4 binds to the final's `release_commit`.
  - A1–A10 require no attestation.
  - `05` §7 rule 6 checks only attestation presence.
  - `09` R-REL-6 binds only the promote tool.
- **Owner-option combination.** D-A03 adds OP-4 "no".
- **Severity kept HIGH.** TCB compromise with review r2's H3 adversary.

### RV3-B-M2 detail

- **Why not HIGH.**
  - TA-9 and RS-4 scope out CI jobs whose repository-controlled steps run before `gov`'s trust decision. Such a job is not a boundary against A2 whatever the design: A2 could skip `gov`.
  - The design-controllable vector is `gov` itself executing repository commands, together with file integrity. CR-03 bounds both.
- **Placement.** It is also a required element of CD3-2 (4).

## Reviewer C (AR-0003, `9e013c1`, role verdict `NO_BLOCKING_FINDINGS`)

| C item | C severity | Reproduced | Adjudication | Reason |
|---|---|---|---|---|
| C-1 occupation defence not robust to removal of the entries | MEDIUM (carried) | yes (A04, A05, A06: 0 differences) | **CONFIRMED MEDIUM, broadened** → RV3-M6 | See the C-1 detail below. |
| C statement "`governance/trust/**` is structurally outside every legacy binary's write vocabulary, so the new trust state cannot be mutated by a pre-RoT binary" | claim | — | **REFUTED as a general statement** | It holds for the intact layout only. Once the legacy paths are vacated or restored, a legacy CIT writes `governance/trust/**` (D-A06). The bound that holds is that a **RoT-1** binary never treats the result as valid. |
| C-2 cross-device transaction area | carried constraint | design | **CONFIRMED** (carried) | — |
| C-3 stray artefacts named by doctor | carried constraint | yes (A03, A04) | **CONFIRMED** (carried) | — |
| C-4 type by `st_mode` | carried constraint | enumeration | **CONFIRMED** (carried) | — |
| C-5 full-register RT-50 with type-aware digests | carried constraint | P3r3 and C destructive reproduced | **CONFIRMED** (carried) | — |
| C prior status: R2-H4 `NARROWED` | — | LP-1 reproduced (P3r3 695 + 40; C 84) | **CONFIRMED**; consolidated as **CLOSED as a class**, residual RV3-M6 | The class requirement (no pre-RoT write on a RoT-1 layout; RoT-1 never treats legacy-mutated state as valid) holds. The residual is the explicit-restoration boundary. |
| C prior status: R2-M7, R2-M8, R2-M9 and R2-L2 `CLOSED (design)` | — | spec-only | **CONFIRMED** as closed in design, open for execution (RT-86, RT-88, RT-83…85, RT-87) | — |
| C prior status: R2-L3 `CLOSED` | — | P3r3 reproduced | **CONFIRMED** | — |
| C prior status: R2-M1 transaction part `CLOSED (design)` | — | — | **CONFIRMED** for repository records; consolidated R2-M1 is `NARROWED` (RV3-M2) | — |
| C residuals: LR-1, LR-3, LR-4, VR-1, VR-2, VR-3 (transaction part), RR-1, RR-3 | — | — | **CONFIRMED** | — |
| C residuals: LR-2 not accepted as stated | — | — | **CONFIRMED** | Accepted with condition RV3-M6 once restated. |
| C verdict `NO_BLOCKING_FINDINGS` | — | — | Agreed **within C's scope** | C's scope contains no HIGH. The architecture verdict rests on B's confirmed HIGHs and this review's attacks. |

### C-1 detail

The precondition is wider than C stated.

1. **One ordinary Git command is enough.** `git checkout <pre-migration> -- governance` restores a legacy-operable layout beside `governance/trust`. The real 4.1.5 binary moves from `NOT_INSTALLED` to `verified: true` and retrieves a file that only the RoT-1 overlay classifies (D-A05).
2. **The legacy binary then writes RoT-1 paths.** In that state, and in C's removal state, the legacy binary executes a CIT that rewrites `governance/trust` and the overlay (D-A06).

**Why MEDIUM stands.**
- RoT-1 binaries report `PARTIAL` or `KERNEL_TAMPERED` and fail closed.
- Overlay changes are within A2's authority (LR-4) and are detected on machines with a record.
- Git can always restore pre-migration history (the LR-1 class).
