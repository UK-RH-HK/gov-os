# Output 19 — Current-policy eligibility and the non-downgradable security floor

> **RoT-1 revision 3 — PROPOSED, pending a fresh independent review; not approved, not implemented.**
> Revision 3 makes floors total over the Constitutional Surface (`23`, R2-H1), bounds currency by anchors (`24`, R2-H2),
> and computes lowering against the strongest held values (R2-M5). Normative keywords: MUST, MUST NOT, SHOULD.

## 1. Four questions, four answers

| Question | Answered by | Never answered by |
|---|---|---|
| **Authenticity:** did an authorised release key sign this exact content? | a release statement verified under the T0-rooted root chain for `release-final` or `release-candidate` (`04`, `05`) | anything else |
| **Eligibility:** may this authentic release be the policy root of this project, on this binary, given what this machine holds? | the predicate of §6, evaluated over T0, the effective Trust Policy and its Constitutional Surface, trust state (`17`) and the VTS | the release being judged; Git-tracked records; the lock; the ledger |
| **Floor:** which constitutional values does enforcement use, whatever kernel is installed? | the effective policy (§5): the root kernel with every floor leaf joined with the effective TPS, pinned leaves only when registered, precedence joined per key | the candidate kernel alone |
| **Currency:** is what this machine holds the currently published state? | an anchor (`24`) | knowledge, the compiled T0, the repository |

An old release can be authentic, recognised and installed for evaluation, yet `INELIGIBLE` as production governance.
Rollback, recovery and Git delivery can restore bytes. They cannot restore values weaker than the floors the machine
holds, and they cannot restore content the effective Trust Policy does not register.

## 2. Where the floor lives

The floor lives in the **Trust Policy lineage**: statements signed under `trust-policy` (root keys, root threshold,
`05` KS-2), ordered by `policy_version` and chained by `prior_policies[]`.

1. **Compiled TPS.** The newest TPS at build time, named in the Trust Base Manifest (`25` §4), is the hard minimum for
   that binary.
2. **Accepted newer TPS.** Verified and accepted monotonically (`17` S3), persisted to the VTS and PTR.
3. **Project strengthening.** The overlay may only strengthen, under the joined precedence (§5.3).

The floor does **not** live in the installed or incoming kernel (joined in, never used alone), the lock, the ledger, gate
records (`27`), caches, snapshots or journals.

## 3. Trust Policy content (revision 3)

Schema: `schemas/trust-policy-statement.schema.json`.

| Field | Meaning |
|---|---|
| `policy_version`, `supersedes_policy_digest`, `prior_policies[]` | monotonic order; cumulative chain (`17` S3) |
| `floor_schema_version` | `2`: the compiled class and operator vocabulary (`23` §3) |
| **`surface`** | the Constitutional Surface Inventory: file rules, leaf rules with floors, registered digests and member ids, registered precedence rules (`23`). Draft v1: `constitutional-surface/CONSTITUTIONAL_SURFACE_INVENTORY.yaml`. It replaces revision 2's `floors[]` list. |
| `eligibility.min_release_sequence`, `.min_binary_version`, `.production_stage` (`final`), `.evaluation_candidates` | as revision 2 |
| **`eligibility.historical_releases[]`** | `{version, release_id, release_commit, tree_digest, manifest_digest, status: REJECTED, verifier_report_digest}`: never eligible. It replaces the withdrawn threshold-1 historical-identity statement (`05` §2). |
| `install_authority {operation: level}` | minimum authority for install-class operations (§8) |
| `gating.mode`, `.refuse_known_rejected`, `.refuse_known_withdrawn`, **`.local_terminal_only[]`** | OP-3; trust-gate kinds that an operator pin cannot approve (`27` §3.2) |
| **`bootstrap`** | `{op6_mode, op7_mode, max_anchor_age_days, witness_max_validity_days}` (OP-6, OP-7; `24` §9) |
| `sensitivity_order` | used for computed weakening (§9) |
| **`lowering_history[]`** | cumulative `{key or rule, previous, new, in_policy_version, reason}` for every reduction ever published (§10) |
| `unrevokes[]` | root-authorised lifting of named revocations |
| `state_chain_reset` | optional (`17` S12) |

## 4. Floor operators

These are the compiled vocabulary of `23` §3, `floor_schema_version: 2`:
- **Classes:** `floor`, `pinned`, `members`, `precedence`, `release_bound`, `project_tunable`, `informational`,
  `collection_id`, `covered_by_collection`.
- **Operators:** `level_at_least`/`at_most`, `ordered_at_least`/`at_most`, `decimal_at_least`/`at_most`, `set_superset`,
  `set_subset`, `bool_toward`, `equals`; member operators `ids_equal`, `ids_subset`, `ids_superset`.
- **Precedence:** a per-key strength lattice (`23` §4) that replaces revision 2's `rule_mode_at_least`, which had no order
  over non-comparable modes (R2-M5).

**Unknown vocabulary.** A TPS using an unknown class, operator or `floor_schema_version` makes the binary
`BINARY_BELOW_TRUST_POLICY` (read-only). There is no partial evaluation.

## 5. Effective policy

### 5.1 Root kernel

```
root_kernel = KernelSnapshot    if the installed release is verified ∧ eligible (§6, including E7 surface)
            = EmbeddedSnapshot  otherwise
```

### 5.2 Per-leaf value

| Leaf class | Effective value |
|---|---|
| `floor` | `op_join(effective TPS floor, root_kernel value)`; a missing leaf takes the floor value |
| `pinned` | the root-kernel value if its digest is registered in the effective TPS; otherwise the consumer's compiled fail-closed default (`23` §6.5) |
| `members` | registered members only (additive collections keep additions) |
| `precedence` | per concrete key: `join(root_kernel rule, registered rule)` (`23` §4) |
| `release_bound`, `project_tunable`, `informational`, `collection_id` | the root-kernel value |

### 5.3 Project layer and exceptions

- **Overlay.** Applied after the join, under the joined precedence, so it can only strengthen.
- **Exceptions.** Applied after the overlay. Effective `exception_relaxable` = registered ∧ root kernel. They never relax
  a `floor`, `pinned`, `members` or `precedence` leaf, or a key under the compiled prefixes `SECURITY_POLICY.`,
  `AUTHORITY_POLICY.`, `HUMAN_GATE_POLICY.`, `TOOL_POLICY.`, `POLICY_PRECEDENCE.`, `ROLES.` (`23` §4).
- **Single enforcement point.** The effective policy is applied in one place, policy loading from the snapshot
  (`18` VU-7). It reaches every consumer, including actor levels (ROLES), secret patterns, gate answering, plugin and tool
  authorisation, export, precedence, exceptions and install authority.

## 6. Eligibility predicate (production profile, normative)

A verified release R with statement digest D, named TPS P_named (`trust_references.trust_policy_version`, or the effective
TPS when unknown) and effective TPS P_eff, is **eligible as policy root** iff every applicable condition holds:

| ID | Condition | Applies at | Failure reason (`RELEASE_INELIGIBLE` at ingress, `KERNEL_INELIGIBLE` at use) |
|---|---|---|---|
| E1 | R is a release statement (`release-final` or `release-candidate`), not listed in `P_eff.eligibility.historical_releases` | both | `historical` |
| E2 | `stage = final`, or a candidate in a gated evaluation project | both | `candidate` |
| E3 | `R.sequence ≥ P_eff.eligibility.min_release_sequence` | both | `below_min_release_sequence` |
| E4 | D and R's `release_id` ∉ N (`17` S5) with `refuse_operation` (use) or either effect (ingress) | both | `revoked` |
| E5 | binary version ≥ `min_binary_version`; contract, `floor_schema_version` and CLI compatible | both | `binary_below_policy` / `incompatible` |
| E6 | `R.trust_root_id` = binary lineage = the pinned lineage | both | `lineage_mismatch` |
| **E7** | **Surface check** of R's kernel against P_eff's CSI, with floor violations judged against P_named (`23` §6.3): every file and leaf classified; pinned digests and members registered; floors not weaker than P_named and not stronger than P_named; precedence not weaker | both | `surface_unclassified` / `surface_unregistered` / `surface_membership` / `floor_violation` / `floor_not_registered` / `precedence_weakened` |
| E8 | trust state `KNOWN`, freshness `ANCHORED` or `WITNESSED`, and R's release-local requirements met (`17` S7, `24` §4.3) | ingress | `trust_state_unanchored` / `below_anchor` / `incomplete` / `equivocation` / `regression` / `references_unknown_state` |
| E9 | if R.sequence < the installed eligible release's sequence: a consumed `downgrade` trust-gate confirmation bound to both digests (`27`) | ingress | `downgrade_not_authorised` |
| E10 | R.sequence ≥ the VTS per-project record; `project_trust_id` unchanged at a known path | use | `downgrade_without_transaction` / `project_trust_id_changed` |

The freshness axis never makes an installed release ineligible for **use**. It restricts operation classes (`24` §4.3).

### Verdict axes

| Axis | Values |
|---|---|
| `authenticity` | `AUTHENTICATED`, `HISTORICAL_IDENTIFIED`, `DEVELOPMENT_UNSIGNED`, `TEST`, `UNAUTHENTICATED` |
| `integrity` | `INTACT`, `TAMPERED`, `NOT_APPLICABLE` |
| `stage` | `final`, `candidate`, `historical`, `development` |
| `eligibility` | `ELIGIBLE`, `ELIGIBLE_EVALUATION`, `INELIGIBLE(reason)` |
| `surface` | `REGISTERED`, `UNCLASSIFIED(n)`, `UNREGISTERED(n)`, `FLOOR_VIOLATION(n)` |
| `certification` | `17` §6 |
| `trust_state` | `KNOWN(n)`, `INCOMPLETE(n′)`, `REGRESSION`, `EQUIVOCATION` |
| `freshness` | `ANCHORED(e, method, age)`, `WITNESSED(e, expires)`, `BELOW_ANCHOR`, `UNANCHORED` |
| `verified` | production: `authenticity = AUTHENTICATED ∧ integrity = INTACT ∧ eligibility ∈ {ELIGIBLE, ELIGIBLE_EVALUATION}`. It means "may be the policy root, joined with floors". It never means "current": that is `freshness`. |

## 7. Historical, rejected, candidate and development material

| Material | Recognised as | Production policy root? |
|---|---|---|
| Legacy 4.1.2–4.1.5 kernels (tree digests in `P_eff.eligibility.historical_releases`) | `HISTORICAL_IDENTIFIED` | **never** (E1); independently, their surfaces fail E7 (`evidence/CSI-check-legacy-*`) |
| Genuine final below `min_release_sequence` | `AUTHENTICATED` | no |
| Genuine final, revoked | `AUTHENTICATED` | no |
| Genuine final with REJECTED/WITHDRAWN not lifted | `AUTHENTICATED` | only if not refused by `gating.refuse_known_*`, through a trust gate |
| Candidate | `AUTHENTICATED` | only `ELIGIBLE_EVALUATION` in a gated evaluation project; unregistered surface content is labelled `SURFACE_UNREGISTERED(evaluation)` and never produces a production verdict |
| Development, unsigned | `DEVELOPMENT_UNSIGNED` | no |
| Test-signed | `TEST` | test profile only |

## 8. Install-authority floor

For every install-class operation o (`install_kernel`, `update_apply`, `rollback_apply`, `recover`,
`override_kernel_integrity`, `trust_refresh`, `trust_confirm_root`, `trust_confirm_state`, `allow_unsigned_development`,
`install_evaluation_candidate`):

```
required_level(o) = max( P_eff.install_authority[o],
                         effective AUTHORITY_POLICY.authority_levels_required[o]  (floor-joined, §5),
                         project overlay strengthening )
actor_level       = effective ROLES.roles[id=<acting role>].level  (floor-joined level_at_most, §5; never from the incoming release)
```

- The incoming release is never consulted for either value.
- Install-class trust transitions also need their trust gate (`27`), whatever the actor level.
- The acting role remains caller-declared (V-L5).

## 9. Strength-reducing changes introduced by migrations or recovery

During `update`, or when restoring `overlay.prev` in recovery (`20` §5), the transaction computes every weakening of
project-owned values:
- a deleted classification, or a class change to an earlier class in `sensitivity_order`;
- a deleted or lowered overlay floor raise;
- a relaxed repository-contract exclusion;
- a deleted overlay key whose joined precedence is not `overridable`.

A non-empty list needs the `weakening` trust gate, bound to the statement digest and the list digest (`27`). This
applies in every OP-3 mode. Signer declarations can add gates, never remove them. After commit, the project-strength
vector is re-recorded (`26` §6).

## 10. How the floor evolves safely

1. **Raising is mechanical.** A kernel value stronger than its named TPS is `FLOOR_NOT_REGISTERED`; an unregistered
   pinned value is `SURFACE_UNREGISTERED`. The producer and E7 refuse. The release therefore ships only with a TPS that
   registers the new value.
2. **Raising without a kernel.** A TPS may raise a floor over existing releases. Joins apply it to older eligible kernels
   (`evidence/P1r3` part 2 join path; part 3 d, e on the real 4.1.5 binary).
3. **Compiling.** Every binary names its compiled TPS in its TBM. The pipeline refuses `FLOOR_REGRESSION_IN_BUILD`, and
   binaries below the VTS high-water refuse trusted operations (`25` §5 A7).
4. **Distribution.** Bundles carry the newest TPS; transactions write the PTR as a union; the VTS persists.
5. **Minimum eligible sequence.** Raised when older releases must never again be current.
6. **Lowering is computed, not declared (R2-M5).**
   - When accepting TPS v_new, the verifier computes every reduction of v_new against the **strongest** value it holds
     for each leaf, precedence key, class and registration. The sources are the VTS, the PTR and T0.
   - Each reduction MUST appear in `v_new.lowering_history[]` with `in_policy_version` greater than the version of the
     strongest held value. Otherwise v_new is invalid: `TRUST_POLICY_UNDECLARED_LOWERING`, not used.
   - Explained reductions apply to a project whose record holds the stronger value only after the per-project
     `policy_lowering` trust gate (`27`).
   - A skipped intermediate version does not hide a lowering: the history is cumulative (`evidence/P4r3` `B6`).
7. **Binary floor.** `min_binary_version` retires binaries.

**Restated claim.** Restoring an older eligible kernel yields that kernel's registered content, joined with floors at
least as strong as the effective TPS on that machine. On an anchored machine that is at least the anchored epoch's TPS
(`24`). On an unanchored machine it is at least the compiled TPS, and under OP-7 (a)–(c) such a machine performs no
governed mutation.

## 11. Worked examples

| Case | Result |
|---|---|
| The review's unfloored-only tamper (backend-engineer L4, secret patterns emptied, `agent_resolvable_when` R5/0.0/irreversible), authentic and sequence-eligible | E7 fails (`floor_violation`, `surface_membership`), so the root is the EmbeddedSnapshot ⊔ floors. Every harm flips on the real 4.1.5 binary consuming the effective kernel (`evidence/P1r3` part 3 a–c). |
| A2 commits the genuine 4.1.2 kernel and a 1.1.0 lock and deletes `governance/trust/` (review R1) | occupation missing and no trust record, so `PARTIAL`; historical and surface failure; EmbeddedSnapshot ⊔ floor; L3 `update --apply` and `resume` refused |
| 4.1.8 caps `migration-executor` at L2 (a TPS raise); A2 commits the eligible 4.1.7 set | effective level L2 from the join (review scenario 1 flips) |
| A `release-final` thief signs a final whose ROLES maps every role to L5 | E7 `floor_violation` (level_at_most) and `surface_membership`; not a policy root (review scenario 2 flips) |
| A TPS arrives with an operator unknown to the binary | `BINARY_BELOW_TRUST_POLICY`, read-only |
| TPS v4 keeps a v3 lowering; the verifier holds v2 | explained by the cumulative history, so the `policy_lowering` trust gate is required; a v4 hiding it is invalid |
