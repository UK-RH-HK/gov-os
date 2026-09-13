# Output 19 — Current-policy eligibility and the non-downgradable security floor

> **RoT-1 revision 2 — PROPOSED, pending a fresh independent review; not approved, not implemented.**
> New in revision 2. Addresses RV-H1 (CD-1), RV-M3 (CD-7) and the floor half of RV-M8 (CD-12). Normative keywords:
> MUST, MUST NOT, SHOULD.

## 1. Three questions, three answers

| Question | Answered by | Never answered by |
|---|---|---|
| **Authenticity** — did an authorised release key sign this exact content? | a release statement verified under the T0-rooted root chain for `release-final` or `release-candidate` (`04`, `05`) | anything else |
| **Eligibility** — may this authentic release be the *current* policy root of this project, on this binary, now? | the eligibility predicate (§6), evaluated over T0, the effective Trust Policy and trust state (`17`), and the machine's Verifier Trust Store | the release being judged; Git-tracked records; `framework.lock`; the update ledger |
| **Floor** — which minimum constitutional values does enforcement use, whatever kernel is installed? | the effective floor (§5): effective Trust Policy floors joined with the installed eligible kernel and project strengthening | the candidate kernel alone |

An old release can be authentic, recognised, listed, and installed in an evaluation project while being `INELIGIBLE` as
current production governance. Rollback, recovery and Git delivery can restore bytes. They cannot restore weaker
floors.

## 2. Where the non-downgradable floor lives

The floor lives in the **Trust Policy Statement (TPS) lineage**: statements signed under the `trust-policy` purpose
(root keys, root threshold; `05` KS-2), ordered by a strictly increasing `policy_version`.

1. **Compiled TPS.** The newest TPS at build time is compiled into every binary (T0). It is the hard minimum for that
   binary; nothing at run time can go below it.
2. **Accepted newer TPS.** A TPS with a higher `policy_version` delivered by a bundle, `gov trust refresh`, the VTS or
   the PTR, and verified under the effective root, is accepted monotonically (`17` S3) and persisted to the VTS and PTR.
3. **Project strengthening.** The project overlay may raise floor values under POLICY_PRECEDENCE. It can never lower
   them.

The floor does **not** live in:
- the installed or incoming kernel (its values are joined in, never used alone);
- `framework.lock`, `spec/reports/framework-updates.jsonl` or gate records (A2-writable, D-0008 rule 18);
- any cache, snapshot or journal.

## 3. Trust Policy content

Schema: `schemas/trust-policy-statement.schema.json`.

| Field | Meaning |
|---|---|
| `policy_version`, `supersedes_policy_digest` | monotonic order; hash link to the previous TPS |
| `floor_schema_version` | version of the compiled floor-operator vocabulary needed to evaluate `floors` |
| `floors[] {key, op, value}` | constitutional minimums (§4) |
| `eligibility.min_release_sequence` | releases with a lower `release.sequence` are never eligible |
| `eligibility.min_binary_version` | binaries below this version are read-only for projects under this policy |
| `eligibility.production_stage` | const `final` |
| `eligibility.historical_releases` | const `never_eligible` |
| `eligibility.evaluation_candidates` | `refuse` or `flag_and_gate` |
| `install_authority {operation: level}` | minimum authority for install-class operations (§8) |
| `gating.mode` | the OP-3 answer: `always_gate` (mode A) or `fresh_certified_may_skip_update_gate` (mode B) (`21`) |
| `gating.refuse_known_rejected`, `gating.refuse_known_withdrawn` | whether a known REJECTED/WITHDRAWN final is refused outright instead of gated |
| `sensitivity_order` | the ordered sensitivity classes used to detect weakening (§9); v1 equals `SECURITY_POLICY.sensitivity_classes` |
| `lowers[]` | explicit floor reductions in this version (§10 step 6) |
| `unrevokes[]` | root-authorised lifting of named revocations (`17` §8) |

## 4. Floor operators (compiled, T0)

The operators reuse the vocabulary POLICY_PRECEDENCE already applies to overlays (`framework/policies/POLICY_PRECEDENCE.yaml`
modes `immutable`, `floor`, `ceiling`, `additive`, `shrink_only`, `strengthen_only_bool`, `overridable`; kinds `level`,
`radius`, `tier`, `number`, `ordered`). The TPS applies them to the **kernel layer itself**.

| `op` | Value | “At least as strong” means | Corresponding precedence mode |
|---|---|---|---|
| `level_at_least` | `L0`…`L5` | higher or equal level | `floor` / kind `level` |
| `ordered_at_least` | member of an order: `R0`…`R5`, `T0`…`T3`, or an explicit `order` list | later or equal in the order | `floor` / kinds `radius`, `tier`, `ordered` |
| `ordered_at_most` | as above | earlier or equal | `ceiling` |
| `number_at_least` / `number_at_most` | integer | larger or equal / smaller or equal | `floor` / `ceiling`, kind `number` |
| `set_superset` | list of strings | contains every floor member | `additive` |
| `set_subset` | list of strings | contains no member outside the floor list | `shrink_only` |
| `bool_required` | boolean | equals the floor value | `strengthen_only_bool` |
| `equals` | string | equals the floor value (enumerations with one safe value, e.g. `fail_closed`) | `immutable` value |
| `rule_mode_at_least` | a POLICY_PRECEDENCE mode | the effective precedence rule for the named key has the floor mode, or is `immutable` | meta-floor over precedence rules |

Key addressing:
- `<POLICY>.<dotted.path>`, e.g. `AUTHORITY_POLICY.authority_levels_required.update_apply`;
- precedence rules: `POLICY_PRECEDENCE.rules[key=<rule key>]`;
- hard invariants: `HARD_INVARIANTS.invariants[*].id` with `set_superset`.

**Unknown operator or `floor_schema_version`.** A TPS using either cannot be evaluated by the running binary. The binary
becomes `BINARY_BELOW_TRUST_POLICY`: read-only, remedy “upgrade gov”. There is no partial evaluation.

**TPS v1 floors (for 4.1.6)** are generated from the 4.1.6 kernel's constitutional files and reviewed in the ceremony:
- every `AUTHORITY_POLICY.authority_levels_required.*` value → `level_at_least`;
- `SECURITY_POLICY.never_index_classes` and `never_export_classes` → `set_superset`;
- `SECURITY_POLICY.on_secret_in_export_payload`, `agent_read_default_for_secret_class` → `equals`;
- `HUMAN_GATE_POLICY.raise_for` → `set_superset`; `must_be_presented_in_chat` → `bool_required`;
- `TOOL_POLICY.plugins.min_authority` → `level_at_least`; `elevated_permission_classes` and `registration_binds` →
  `set_superset`; `refuse_on_pin_drift` and `require_valid_descriptor` → `bool_required`;
- every POLICY_PRECEDENCE rule → `rule_mode_at_least`; `POLICY_PRECEDENCE.default_mode` → `equals immutable`;
- `HARD_INVARIANTS.invariants[*].id` → `set_superset`.

`examples/make_example.py` shows the derivation.

## 5. Effective floor

For each floor key k, with join operator ⊔ given by the op:

```
effective(k) = TPS_effective.floor(k)  ⊔  root_kernel(k)
root_kernel  = KernelSnapshot   if the installed release is verified ∧ eligible (§6)
             = EmbeddedSnapshot otherwise
```

| op | a ⊔ b |
|---|---|
| `level_at_least`, `number_at_least`, `ordered_at_least` | the stronger (max in order) |
| `number_at_most`, `ordered_at_most` | the stronger (min in order) |
| `set_superset` | union |
| `set_subset` | intersection |
| `bool_required`, `equals` | the floor value |
| `rule_mode_at_least` | the floor mode, unless the kernel rule is `immutable` |

- A key the kernel lacks takes the floor value. Example: the 4.1.2 kernel lacks `update_apply` → L4 from the floor, not
  the runtime's L3 default for missing classes.
- The project overlay is applied **after** the join, under the joined precedence rules, so it can only strengthen.
- The effective floor is applied in one place — policy loading from the snapshot (`18` VU-7) — and reaches every
  consumer: authority checks, precedence evaluation, sensitivity and indexing, plugin authorisation, gate policy and
  install authority.

## 6. Eligibility predicate (production profile, normative)

A verified release R with statement digest D is **eligible as current policy root** iff every applicable condition
holds.

| ID | Condition | Applies at | Failure reason (`RELEASE_INELIGIBLE` at ingress, `KERNEL_INELIGIBLE` at use) |
|---|---|---|---|
| E1 | R authenticates as a **release** statement (`release-final` or `release-candidate` purpose). A historical identity never satisfies E1. | both | `historical` |
| E2 | `R.stage = final`, or `R.stage = candidate` in an evaluation project created through a gate under `eligibility.evaluation_candidates = flag_and_gate` | both | `candidate` |
| E3 | `R.sequence ≥ TPS_effective.eligibility.min_release_sequence` (and ≥ any project strengthening of it) | both | `below_min_release_sequence` |
| E4 | D and R's `release_id` are not in the effective negative set N (`17` S5) with `refuse_operation` (use) or either effect (ingress) | both | `revoked` |
| E5 | binary version ≥ `min_binary_version`; binary supports R's `kernel_contract_version` and `floor_schema_version`; CLI version within `compatibility.cli` | both | `binary_below_policy` / `incompatible` |
| E6 | `R.trust_root_id` = binary lineage = the lineage pinned for this project and machine (`06` §4) | both | `lineage_mismatch` |
| E7 | R's kernel values for every floor key are no stronger than the TPS named by `R.trust_references.trust_policy_version` (the producer registered every floor; §10.3) | both | `floor_not_registered` |
| E8 | trust state is not `STALE` (`17` §7) | ingress | `trust_state_stale` |
| E9 | if `R.sequence` is lower than the installed eligible release's sequence, a downgrade authorisation exists (`20` §4) | ingress | `downgrade_not_authorised` |
| E10 | R's sequence is not lower than the VTS per-project record, and the project's `project_trust_id` has not changed at a known path (`20` §9) | use | `downgrade_without_transaction` / `project_trust_id_changed` |

Trust state `STALE` never makes an installed release ineligible for **use** (`17` MS-6).

### Verdict axes

| Axis | Values |
|---|---|
| `authenticity` | `AUTHENTICATED`, `HISTORICAL_IDENTIFIED`, `DEVELOPMENT_UNSIGNED`, `TEST`, `UNAUTHENTICATED` |
| `integrity` | `INTACT`, `TAMPERED`, `NOT_APPLICABLE` |
| `stage` | `final`, `candidate`, `historical`, `development` |
| `eligibility` | `ELIGIBLE`, `ELIGIBLE_EVALUATION`, `INELIGIBLE(reason)` |
| `certification` | views of `17` §6 |
| `trust_state` | `CURRENT_KNOWN(n)`, `HINT_MISMATCH`, `STALE`, `REGRESSION` |
| `verified` | production: `authenticity = AUTHENTICATED ∧ integrity = INTACT ∧ eligibility ∈ {ELIGIBLE, ELIGIBLE_EVALUATION}`. Test profile additionally admits `TEST`, `DEVELOPMENT_UNSIGNED` and historical identities, always labelled. |

`verified` keeps its consumer meaning: *the KernelSnapshot may be the policy root, joined with the floor.* When it is
false, the root is the EmbeddedSnapshot joined with the floor. Mutations are refused, except remedies, with
`KERNEL_TAMPERED` (integrity), `KERNEL_UNAUTHENTICATED` (authenticity) or `KERNEL_INELIGIBLE` (eligibility).

## 7. Historical, rejected, candidate and development material

| Material | Recognised as | Production policy root? | Installable in production? | Floors when installed |
|---|---|---|---|---|
| Legacy 4.1.2–4.1.5 kernels (identities compiled into T0, `05` §5) | `HISTORICAL_IDENTIFIED` | **never** | no (test profile only, labelled) | EmbeddedSnapshot ⊔ floor |
| Genuine final below `min_release_sequence` | `AUTHENTICATED` | no | no | EmbeddedSnapshot ⊔ floor |
| Genuine final, revoked | `AUTHENTICATED` | no | no | EmbeddedSnapshot ⊔ floor |
| Genuine final with REJECTED or WITHDRAWN certification | `AUTHENTICATED` | yes, unless revoked or refused by TPS `gating.refuse_known_*`. Certification is a gate input, not eligibility (`17` §7). | through a gate | installed ⊔ floor |
| Candidate | `AUTHENTICATED` (`release-candidate`) | only `ELIGIBLE_EVALUATION` in an evaluation project | only with flag + gate | installed ⊔ floor |
| Development, unsigned | `DEVELOPMENT_UNSIGNED` | no | only with `--allow-unsigned-development` (recorded in `development.json`) | EmbeddedSnapshot ⊔ floor |
| Test-signed | `TEST` | no (yes in the test-profile binary) | test profile only | — |

**Withdrawal of a rev 1 claim.** Revision 1 (`11` Phase 1.3) said the defects of 4.1.2–4.1.5 “lie in the binaries' install
and use logic, not in kernel content”. That is withdrawn. The independent review showed security-relevant kernel
differences (`../4.1.6-review/evidence/legacy-kernel-security-diffs.txt`) and executed an authority-floor lowering on the
genuine 4.1.2 kernel (`../4.1.6-review/evidence/R1-legacy-kernel-floors.json`).

## 8. Install-authority floor (RV-M3)

For every install-class operation o — `install_kernel` (init, adopt batch 0, reinstall), `update_apply`, `rollback_apply`,
`recover`, `override_kernel_integrity`, `trust_refresh`, `trust_confirm_root`, `allow_unsigned_development`,
`install_evaluation_candidate`:

```
required_level(o) = max( TPS_effective.install_authority[o],
                         EmbeddedSnapshot AUTHORITY_POLICY.authority_levels_required[o],
                         KernelSnapshot   AUTHORITY_POLICY.authority_levels_required[o]   if verified ∧ eligible,
                         project overlay strengthening )
```

- **The incoming release is never consulted.** An incoming kernel declaring `install_kernel: L0` changes nothing.
- A first install (`ABSENT`) uses the TPS and EmbeddedSnapshot values only.
- The acting role remains caller-declared, the documented V-L5 boundary: the floor defines what a role may do; Human
  Decision Gates remain the human authorisation boundary.

## 9. Strength-reducing changes introduced by migrations (RV-M8)

During `update`, the transaction interprets migration operations over the current overlay (`18` §4, `migrated` phase).
It computes every change that weakens a project-owned value compared with its pre-update value:

- deletion of a DATA_SENSITIVITY classification, or a class change to an earlier class in `sensitivity_order`;
- deletion or lowering of an overlay value that strengthened a floor key (judged by the op of §4);
- relaxation of a REPOSITORY_CONTRACT rule that excluded a path from indexing, retrieval or export;
- deletion of any overlay key whose effective precedence rule is not `overridable`.

A non-empty `computed_weakenings[]` requires a Human Decision Gate bound to the statement digest and to the digest of
the list. This applies whatever the signer declared in `breaking`/`human_gates` and whatever the OP-3 mode.
Signer-declared information can add gates; it can never remove computed ones (`OVERLAY_WEAKENING_GATE_REQUIRED`).

## 10. How the floor evolves safely

1. **Raising.** When a release strengthens any floor-key value, the release owner issues a TPS with a higher
   `policy_version` containing the stronger value, before or together with the final release statement. The release
   statement's `trust_references.trust_policy_version` names that TPS.
2. **Compiling.** Every binary compiles the newest TPS. The release pipeline refuses a binary whose compiled
   `policy_version` is lower than the previously published binary's (`FLOOR_REGRESSION_IN_BUILD`); the verifier
   re-checks.
3. **Producer consistency.** `gov release build` refuses a final release whose kernel floor-key values are stronger than
   the referenced TPS (`FLOOR_NOT_REGISTERED`) or weaker than it (`FLOOR_VIOLATION`). Verifiers re-check (E7).
4. **Distribution.** Bundles carry the newest TPS; `gov trust refresh` imports; install transactions write it into the
   PTR; the VTS persists it.
5. **Minimum eligible sequence.** Raised when older releases must never again be current (security-relevant kernel
   defect, key compromise). Per-digest revocation is the complementary tool.
6. **Lowering.** Only through a higher-version TPS listing each reduction in `lowers[]`, signed by the root threshold. A
   project whose PTR or VTS holds the previous stronger policy keeps the stronger values until a Human Decision Gate bound
   to the lowering TPS digest accepts the reduction. Projects with no record of the stronger policy (fresh clones) apply
   the reduction, which the owner deliberately published.
7. **Binary floor.** `min_binary_version` retires binaries whose enforcement is inadequate; they become read-only for
   projects under that policy.

**Why current floors survive rollback, recovery and Git delivery:**
- the effective floor never takes a value from a kernel alone (§5);
- every floor value of every final release is registered in a TPS (step 3);
- TPS versions only increase (step 2, `17` S3).

Restoring any older eligible kernel therefore yields that kernel's content, joined with floors at least as strong as
the newest registered ones.

## 11. Worked examples

| Case | Result |
|---|---|
| A2 commits the genuine 4.1.2 kernel and a 1.1.0 lock, and deletes `governance/trust/` — the review's R1 shape | Installation state `PARTIAL` (no trust record) → EmbeddedSnapshot ⊔ floor. If a historical identity is recognised from the tree digest it is reported as `HISTORICAL_IDENTIFIED`, `INELIGIBLE(historical)`. Floors `authority_levels_required.update_apply` L4 and `resume_control` L4 hold, so L3 `update --apply` and `resume` are refused. **R1 must flip** (`12` RT-32). |
| A2 commits a genuine signed 4.1.6 set into a project on 4.1.7, whose kernel raised a floor | 4.1.6 is authentic and eligible if ≥ `min_release_sequence`. Floors are joined with the TPS, which holds 4.1.7's registered values, so the floor is preserved. On a machine whose VTS recorded 4.1.7 for this project: `INELIGIBLE(downgrade_without_transaction)` until an authorised rollback or update. |
| `gov update --rollback` to a revoked release | `RELEASE_INELIGIBLE(revoked)`, refused with no override |
| Incoming release declares `install_kernel: L0` | ignored (§8) |
| A newer binary opens a project installed from an older eligible release | content from the installed release; floors from the newer binary's compiled TPS ⊔ installed values |
| A TPS arrives with a floor operator unknown to the running binary | `BINARY_BELOW_TRUST_POLICY`: read-only until upgraded |
