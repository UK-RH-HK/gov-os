# Output 19 — Current-policy eligibility, effective policy and the non-downgradable security floor

> **RoT-1 revision 4 — PROPOSED, pending fresh independent reviews; not approved, not implemented.**
> Revision 4 changes, with the review r3 findings each closes:
> - effective precedence comes from registrations only, and the project layer is a directed join (§5; BC-1, RV3-H1);
> - absence resolves to a defined value or a typed refusal (§5.2; RV3-M7);
> - project-owned strength and computed weakening are evaluated over the effective policy (§9; root of RV3-M5);
> - computed reductions cover precedence in both directions and the non-surface Trust Policy fields (§10.6; RV3-L5, CR-10);
> - E8 requires a currency proof for ingress (`24`; BC-2).
>
> Normative keywords: MUST, MUST NOT, SHOULD.

## 1. Four questions, four answers

| Question | Answered by | Never answered by |
|---|---|---|
| **Authenticity:** did an authorised release key sign this exact content, with the same source as its candidate? | the release statement verified for its purpose (`04` V5–V8) | anything else |
| **Eligibility:** may this authentic release be the policy root here? | §6 over T0, the effective TPS and its surface, trust state (`17`) and the VTS | the release judged; Git-tracked records; the lock; the ledger |
| **Floor:** which constitutional values, and which project-layer rules, does enforcement use? | the effective policy (§5): registered floors joined, registered pins, **registered precedence**, the project layer as a directed join | the candidate kernel alone; the kernel's POLICY_PRECEDENCE |
| **Currency:** is what this machine holds the published state as of now? | a currency proof (`24` §4.4) | knowledge, the compiled T0, the repository, an aged anchor |

## 2. Where the floor lives

1. **Compiled TPS**, named in the Trust Base Manifest. It is the hard minimum for that binary.
2. **Accepted newer TPS**, accepted monotonically (`17` S3) and persisted.
3. **The project's held registration** (`24` §8 per-project record). While a computed reduction has not been accepted by
   that project's `policy_lowering` trust gate, the project keeps the stronger registration through joins (§5.2, §10.6).
4. **Project strengthening**, applied as a directed join (§5.3).

The floor does **not** live in:
- the installed or incoming kernel (joined in, never used alone; its POLICY_PRECEDENCE is never used);
- the lock, the ledger or gate records;
- caches, snapshots or journals.

## 3. Trust Policy content (revision 4)

Schema: `schemas/trust-policy-statement.schema.json` (`x-schema-version` 2.0.0).

| Field | Meaning |
|---|---|
| `policy_version`, `supersedes_policy_digest`, `prior_policies[]` | monotonic order; cumulative chain |
| `floor_schema_version` | **3** (`23` §3) |
| `surface` | Constitutional Surface Inventory: file and leaf rules with presence; floors; registered digests and member ids; **exact precedence registration**; **Overlay Surface** (`23` §11); **owner-domain slots** (`23` §7.2) |
| `eligibility.min_release_sequence`, `.min_binary_version`, `.production_stage`, `.evaluation_candidates`, `.historical_releases[]` | as revision 3 |
| **`eligibility.production_sources[]`** | `{release_commit, source_tree_digest, build_inputs_digest}`; present and enforced only if OP-2 selects root-registered production sources (`25` A4b) |
| `install_authority {operation: level}` | minimum authority for install-class operations (§8) |
| `gating.mode`, `.refuse_known_rejected`, `.refuse_known_withdrawn`, `.local_terminal_only[]` | OP-3; trust-gate kinds a decision pin cannot approve |
| **`bootstrap`** | `{op6_mode, op7_mode, pin_max_validity_days, c3_currency_window_hours, max_anchor_age_days, witness_max_validity_hours, freshness_witness_threshold, clock_reset}` (`24` §9) |
| `sensitivity_order` | used by the Overlay Surface directions |
| `lowering_history[]` | cumulative `{subject, previous, new, in_policy_version, reason}` for every computed reduction ever published (§10.6) |
| `unrevokes[]`, `state_chain_reset` | as revision 3 |

## 4. Vocabulary

The compiled vocabulary is `floor_schema_version: 3` (`23` §3): classes, operators, member operators, presence, the
precedence order in both directions (`23` §4.2) and Overlay Surface directions. An unknown class, operator,
presence value, direction or `floor_schema_version` makes the binary `BINARY_BELOW_TRUST_POLICY` (read-only). There is no
partial evaluation.

## 5. Effective policy

### 5.1 Root kernel

```
root_kernel = KernelSnapshot    if the installed release is verified ∧ eligible (§6, including E7)
            = EmbeddedSnapshot  otherwise
```

### 5.2 Per-leaf value

| Leaf class | Effective value |
|---|---|
| `floor` | `op_join(effective TPS floor, root_kernel value)`. A registered floor leaf missing from a kernel makes the kernel ineligible (E7), so the EmbeddedSnapshot value is joined instead. |
| `pinned` | the root-kernel value if its digest is registered in the effective TPS; else the EmbeddedSnapshot value if registered; else **`SURFACE_VALUE_UNAVAILABLE(key, decision point)`**, and the dependent decision point refuses per the consumer register (`23` §6.3) |
| `members` | registered members only (additive collections keep additions); the missing-content fallback is as for `pinned` |
| `precedence` | **per concrete key: the registered rule of the effective TPS, joined (`23` §4.2) with the project's held registration while a reduction for that key awaits the project's `policy_lowering` gate. Never the kernel's rule.** |
| `release_bound`, `project_tunable`, `informational`, `collection_id` | the root-kernel value |

### 5.3 Project layer: directed join (normative; CD3-1 (1), (3))

A project override (`PROJECT_POLICY.policy_overrides`) is flattened to concrete leaves. For leaf *k* with registered
strength direction *d* (`23` §4.2; while a reduction is pending, the held registration's direction) and effective rule
*r = rule_eff(k)*, let *A = admitted(r, d)*. Let *b* be the effective value before the project layer and *o* the
override.

| Direction | Components of *o* relative to *b* | Effective value |
|---|---|---|
| up / down (levels, orders, decimals) | *o* stronger: **s**; *o* weaker: **w** | *o* if its component ∈ *A*, else *b* |
| add (supersets) | entries of *o* not in *b*: **s**; entries of *b* not in *o*: **w** | *b*, plus the added entries if s ∈ *A*, minus the removed entries if w ∈ *A* |
| remove (subsets) | entries of *b* not in *o*: **s**; entries of *o* not in *b*: **w** | as above, with the roles exchanged |
| toward *v* (booleans) | *o* = *v*: **s**; otherwise **w** | *o* if its component ∈ *A*, else *b* |
| none | any change: **w** | *o* if w ∈ *A*, else *b* |

- **The rule of refusal.** A refused component is refused alone and recorded (`OVERRIDE_COMPONENT_REFUSED`). No refusal
  discards an admitted component.
- **Consequence.** A later floor raise that adds an entry the project did not list keeps the project's own additions.
  Revision 3's replacement semantics lost them (`evidence/P1r4-project-strength-and-absence.json` part D, executed).
- **Exceptions** are applied after the project layer: registered `exception_relaxable` only, never for
  `floor`/`pinned`/`members`/`precedence` classes or the compiled prefixes (`23` §4.4).
- **Single enforcement point.** Policy loading from the snapshot (`18` VU-7) reaches every consumer.

## 6. Eligibility predicate (production profile, normative)

A verified release R, with statement digest D, named TPS P_named and effective TPS P_eff, is **eligible as policy root**
iff every applicable condition holds:

| ID | Condition | Applies at | Failure reason |
|---|---|---|---|
| E1 | R is a release statement, not in `P_eff.eligibility.historical_releases` | both | `historical` |
| E2 | `stage = final`, or a candidate in a gated evaluation project | both | `candidate` |
| E3 | `R.sequence ≥ P_eff.eligibility.min_release_sequence` | both | `below_min_release_sequence` |
| E4 | D and R's `release_id` ∉ N | both | `revoked` |
| E5 | binary version ≥ `min_binary_version`; contract, `floor_schema_version` and CLI compatible | both | `binary_below_policy` / `incompatible` |
| E6 | `R.trust_root_id` = binary lineage = pinned lineage | both | `lineage_mismatch` |
| **E7** | **Surface check** of R's kernel against P_eff's surface, with floors, pins and precedence registration judged against P_named: every file and leaf classified; **every registered file and leaf present**; **single YAML profile**; pinned digests and members registered; floors neither weaker nor stronger than P_named; **POLICY_PRECEDENCE equal to P_named's registration**; **every migration operation on a migration-writable Overlay Surface target** | both | `surface_unclassified` / **`surface_required_missing`** / **`surface_structure`** / `surface_unregistered` / `surface_membership` / `floor_violation` / `floor_not_registered` / **`precedence_unregistered`** / **`migration_operation_not_permitted`** |
| E8 | trust state `KNOWN`; freshness `ANCHORED` or `WITNESSED`; **a currency proof** (`24` §4.4); R's release-local requirements met | ingress | `trust_state_unanchored` / `below_anchor` / **`currency_unproven`** / `incomplete` / `equivocation` / `regression` / `references_unknown_state` |
| E9 | if R.sequence < the installed eligible release's sequence: a consumed `downgrade` trust-gate confirmation | ingress | `downgrade_not_authorised` |
| E10 | R.sequence ≥ the VTS per-project record; `project_trust_id` unchanged | use | `downgrade_without_transaction` / `project_trust_id_changed` |

The freshness and currency axes never make an installed release ineligible for **use**. They restrict operation classes
(`24` §4.3).

### Verdict axes

| Axis | Values |
|---|---|
| `authenticity` | `AUTHENTICATED`, `HISTORICAL_IDENTIFIED`, `DEVELOPMENT_UNSIGNED`, `TEST`, `UNAUTHENTICATED` |
| `integrity` | `INTACT`, `TAMPERED`, `NOT_APPLICABLE` |
| `stage` | `final`, `candidate`, `historical`, `development` |
| `eligibility` | `ELIGIBLE`, `ELIGIBLE_EVALUATION`, `INELIGIBLE(reason)` |
| `surface` | `REGISTERED`, `UNCLASSIFIED(n)`, `REQUIRED_MISSING(n)`, `UNREGISTERED(n)`, `FLOOR_VIOLATION(n)`, `PRECEDENCE_UNREGISTERED` |
| `certification` | `17` §6 |
| `trust_state` | `KNOWN(n)`, `INCOMPLETE(n′)`, `REGRESSION`, `EQUIVOCATION` |
| `freshness`, `currency` | `24` §4.1 |
| `project_strength` | `RECORDED`, `WEAKENED(n)` (`26` §6) |
| `verified` | `authenticity = AUTHENTICATED ∧ integrity = INTACT ∧ eligibility ∈ {ELIGIBLE, ELIGIBLE_EVALUATION}`. It never means "current". |

## 7. Historical, rejected, candidate and development material

Unchanged from revision 3. Legacy kernels are never eligible (E1). Independently, their surfaces fail E7: 4.1.2, 4.1.3
and 4.1.4 exit 2 against the revision-4 inventory (`evidence/CSI-check-legacy-*.json`).

## 8. Install-authority floor

Unchanged:

```
required_level(o) = max( P_eff.install_authority[o], effective AUTHORITY_POLICY.authority_levels_required[o], project strengthening )
actor_level       = effective ROLES.roles[id=<acting role>].level
```

The incoming release is never consulted. The acting role remains caller-declared (V-L5; RV3-I1).

## 9. Computed weakening over effective policy (replaces revision 3's four categories)

Every install transaction evaluates the project's recorded strength vector (`26` §6) against the **post-transaction
effective inputs**, before commit:
- the new root kernel, effective TPS and registered precedence;
- the migrated overlay;
- the result of any `overlay.prev` restore or remedy.

This covers update, rollback, restore, recovery exchange-back and adoption batch 0.

1. **Migration operations** are first checked against the Overlay Surface whitelist (`23` §11.3). A violation refuses the
   transaction before any write: `MIGRATION_OPERATION_NOT_PERMITTED`.
2. **Every requirement of the recorded vector** is evaluated over the effective policy and overlay the transaction would
   commit. This is not an enumerated list of categories. It covers:
   - constitutional-key strength contributions;
   - classifications, contract exclusions, tool permissions, install-authority roles, exceptions and identifiers to
     strip;
   - plugin descriptors and owner constitutional files;
   - unclassified overlay files by digest.
3. A non-empty failure list needs the `weakening` trust gate, bound to the statement digest and the failure-list digest
   (`27`). This applies in every OP-3 mode. Signer declarations can add gates, never remove them.
4. After commit, the vector is re-recorded from the committed effective inputs.

Evidence: `evidence/P1r4-project-strength-and-absence.json` part C.
- **Release-signed migrations.**
  - Refused before any write: widening install-authority roles, granting `SECRET_READ`, adding an exception, emptying
    `identifiers_to_strip`, and dropping the project never-index class.
  - Passed the whitelist but reported as a weakening: a registered target that indexes `**/.env*`.
  - Passed with no weakening: a registered strengthening.
- **Constitutional strength.** The vector reports the loss of every revision-3 effective kernel, and is quiet for every
  revision-4 one.

## 10. How the floor evolves safely

1. **Raising is mechanical.** A kernel value stronger than its named TPS is `FLOOR_NOT_REGISTERED`; an unregistered pinned
   value is `SURFACE_UNREGISTERED`; a precedence rule different from registration is `PRECEDENCE_UNREGISTERED`.
2. **Raising without a kernel.** A TPS may raise a floor over existing releases. Joins apply it, and directed joins keep
   project strengthening (§5.3).
3. **Compiling.** Every binary names its compiled TPS in its TBM. Binaries below the **accepted-TBM** high-water refuse
   trusted operations (`25` A7).
4. **Distribution.** Bundles carry the newest TPS; transactions write the PTR as a union.
5. **Minimum eligible sequence.** Raised when older releases must never again be current.
6. **Lowering is computed, not declared** (revision 4 scope). When accepting TPS v_new, the verifier computes every
   reduction against the **strongest** value it holds (VTS, PTR, T0) for:
   - floor values, classes, memberships and presence (`required` → `optional`);
   - **precedence registrations in both directions** (`23` §4.2): a newly admitted weakening, a removed admitted
     strengthening, or an added `exception_relaxable`;
   - newly migration-writable Overlay Surface targets, and removed or weakened Overlay Surface directions;
   - removed owner-domain slots;
   - **non-surface fields (CR-10, RV3-L5):**
     - `eligibility.min_release_sequence` lowered;
     - `eligibility.historical_releases[]` removals;
     - `eligibility.production_sources[]` additions;
     - `install_authority` levels lowered;
     - `gating.mode` from `always_gate`;
     - `gating.local_terminal_only[]` removals;
     - `bootstrap.op7_mode` toward (d) in the order (b) > (a) > (c) > (d);
     - increases of `pin_max_validity_days`, `c3_currency_window_hours`, `max_anchor_age_days` or
       `witness_max_validity_hours`;
     - `freshness_witness_threshold` lowered.

   **Rules that apply to every reduction:**
   - Each reduction MUST appear in `v_new.lowering_history[]` with `in_policy_version` greater than the version of the
     strongest held value. Otherwise v_new is invalid (`TRUST_POLICY_UNDECLARED_LOWERING`) and not used.
   - Explained reductions apply to a project whose record holds the stronger registration only after that project's
     `policy_lowering` trust gate. The gate package lists the project strengthening that will stop applying. Until then
     the joins of §5.2 keep it.
   - A skipped intermediate version hides nothing, because the history is cumulative.
7. **Binary floor.** `min_binary_version` retires binaries.

Evidence:
- `evidence/P1r4-project-strength-and-absence.json` RV3-D-A02 (honest owner and root ceremony): reduction reported; before the gate the project-layer mode
  is `additive` / `floor` and the harms stay absent on 4.1.5; after the gate, accepted.
- `P4r4` `CR-10_non_surface_tps_reductions`: all seven fields refuse without history.
- `P4r4` `B6_lowering_across_skipped_version`.

**Restated claim.** Restoring an older eligible kernel yields that kernel's registered content, joined with floors at
least as strong as the effective TPS on that machine. It is governed by registered precedence joined with the project's
held registration, and the project layer is applied as a directed join. On an anchored machine that is at least the
anchored chain's TPS. On an unanchored machine it is at least the compiled TPS.

## 11. Worked examples

| Case | Result |
|---|---|
| Review r2 unfloored-only tamper (authentic, sequence-eligible) | E7 fails; policy root is EmbeddedSnapshot ⊔ floors; every harm flips on 4.1.5 (`P1r3`, re-run against the revision-4 library) |
| **RV3-B-A01:** a kernel whose only change moves precedence to `immutable` (floor, ceiling, additive, shrink_only or strengthen_only_bool rules) | E7 `precedence_unregistered` (exit 3). Even if accepted, the project layer uses registered precedence. On 4.1.5 the project L5 raise denies `resume`, `confidential` stays excluded, and an agent answer under R0 is denied (`P1r4`) |
| **RV3-D-A10 R07:** POLICY_PRECEDENCE deleted | E7 `surface_required_missing` (exit 2); effective precedence unchanged (`P1r4`) |
| **RV3-D-A02:** TPS v2 registers `never_index_classes` `immutable` and reclassifies the leaf `equals` | computed reduction; `lowering_history` required; per-project gate; until then the project keeps `additive` (`P1r4`) |
| TPS raises the never-index floor by `internal` while the project added `confidential` | directed join keeps both; revision 3 lost `confidential` (`P1r4` part D) |
| A `release-final` thief signs a final whose ROLES maps every role to L5 | E7 `floor_violation`, `surface_membership`; not a policy root |
| A `release-final`-signed migration widens `install_authority_roles` | E7 `migration_operation_not_permitted`; at the transaction, refused before any write |
| A TPS arrives with an operator unknown to the binary | `BINARY_BELOW_TRUST_POLICY`, read-only |
