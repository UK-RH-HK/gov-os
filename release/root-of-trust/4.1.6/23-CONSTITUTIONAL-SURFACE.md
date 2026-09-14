# Output 23 — Constitutional Surface and total floor semantics

> **RoT-1 revision 3 — PROPOSED, pending a fresh independent review; not approved, not implemented.**
> New in revision 3. Closes R2-H1 as a class (`../4.1.6-review-r2/10-BLOCKING-FINDINGS.md`) and satisfies HO-0001 §3.1
> and §4. Normative keywords: MUST, MUST NOT, SHOULD.

## 1. The class, and why no key list can close it

Revision 2 registered 145 floor keys. The review executed the gap: every one of those floors held on a kernel that made an
L1 role act at L4, got an AWS credential indexed and retrievable, and let an agent answer an R5 irreversible gate
(review `evidence/P1`). The mistaken equivalence was *registered floor keys ⇒ constitutional policy*.

Any design whose coverage is a list that someone chooses fails open for whatever the list forgets. That includes a list
chosen by the producer, by the release statement's `security_critical` field, or by the Trust Policy author picking keys
one by one. Revision 3 inverts the direction:

- the **Constitutional Surface** is *everything* the kernel payload contains, plus every key of the policy universe that
  POLICY_PRECEDENCE governs;
- every file and every leaf of that surface MUST carry exactly one **floor semantics** from a closed, compiled vocabulary;
- anything that carries none is **denied** (`UNCLASSIFIED`). It never takes effect as policy.

**Different mechanism from CD2-1.** The review proposed defining the surface as the release statement's `security_critical`
list. Revision 3 does not, because that list is signed under the threshold-1 `release-final` purpose. A lower-trust input
would then decide which content counts as constitutional, which is the rejection class itself. In revision 3 the surface
is the whole payload, and its classification is root-signed.

## 2. Definitions

| Term | Definition |
|---|---|
| Constitutional Surface | Every file of a release kernel payload admitted by the tree rules (`07` §5.1; `KERNEL_MANIFEST.json` is excluded), every leaf of every structured file, and every concrete key of the policy universe used for precedence (§4). |
| Constitutional Surface Inventory (CSI) | The machine-readable classification of the surface. It is the **surface section of the Trust Policy Statement** (`19` §3) and is signed with the TPS under the `trust-policy` purpose, which means root keys at root threshold (`05` KS-2). Schema: `schemas/constitutional-surface-inventory.schema.json`. The draft for TPS v1, derived from the current kernel (4.1.5 content standing in for 4.1.6): `constitutional-surface/CONSTITUTIONAL_SURFACE_INVENTORY.yaml`. |
| Floor semantics | For a file, one mode (§3.1). For a leaf, one class (§3.2) with its operator, registered values or registered digests. |
| Default deny | A file matching no file rule, or a leaf matching no leaf rule, is `UNCLASSIFIED`. This yields `RELEASE_INELIGIBLE(surface_unclassified)` at ingress, `KERNEL_INELIGIBLE(surface_unclassified)` at use, and `SURFACE_UNCLASSIFIED` at the producer. |
| Named TPS | The Trust Policy a release statement names in `trust_references.trust_policy_version`, meaning the policy the producer registered the release under. |
| Effective TPS | The highest admissible TPS the verifier holds (`17` S3). |

The binary never derives a classification from a kernel. It evaluates kernels against the CSI of a verified TPS. The
derivation script (`constitutional-surface/csi_derive.py`) is producer tooling: it drafts the next CSI for the root
ceremony to review.

## 3. Closed vocabulary (`floor_schema_version: 2`, compiled)

### 3.1 File modes

| Mode | Meaning | Registration | Violation |
|---|---|---|---|
| `structured` | YAML or JSON whose every leaf is enumerated (§3.4) and classified | per leaf | per leaf |
| `pinned_file` | non-orderable content (schemas, skills, adapters, overlay templates, taxonomies, command contract, constitution text, enforcement map, MCP registry) | SHA-256 of the file bytes, per path | `surface_unregistered` |
| `transaction_input` | migrations. They are consumed only inside the install transaction, from authenticated buffers (`04` V10). Their overlay effects are computed, and every weakening needs a trust gate (`19` §9, `27`). They can change no floor, pin or registration. | bound by the release statement's `migrations[]` | V10 codes |
| `informational_file` | documentation with no runtime reader | rationale required | — |

### 3.2 Leaf classes

| Class | Meaning | Kernel value used? | Violation (E7) |
|---|---|---|---|
| `floor` | orderable value with an operator and a registered floor value (§3.3) | joined with the effective TPS floor | weaker than the named TPS → `floor_violation`; stronger than the named TPS → `floor_not_registered` |
| `pinned` | non-orderable value; the TPS registers the permitted value digests | only when its digest is registered in the effective TPS | `surface_unregistered` |
| `members` | the member-id set of a declared keyed collection (`roles[id]`, `invariants[id]`, `tools[tool_id]`, `secret_content_patterns[id]`), with `ids_equal`, `ids_subset` or `ids_superset` | registered members only (additive collections keep additions) | `surface_membership` |
| `precedence` | the POLICY_PRECEDENCE rule list, compared per concrete key (§4) | joined per key | `precedence_weakened` |
| `release_bound` | must equal a field of the signed release statement (`KERNEL.yaml` version, compatibility, schema versions). It decides compatibility only, never eligibility, floors or gates. | yes | V8/V11 codes |
| `project_tunable` | a key POLICY_PRECEDENCE marks `overridable`. The project layer may set it freely, so no kernel-lineage floor can be stronger. | yes | — (lint: the registered precedence MUST be `overridable`) |
| `informational` | no runtime reader. A rationale is required, and the compiled consumer register (§6.5) MUST NOT read it. | yes | — (lint) |
| `collection_id` | the identity field of a collection member | yes | — |
| `covered_by_collection` | a member subtree governed by its collection rule: precedence rules, or fields of additional members of an additive collection | per collection | per collection |

### 3.3 Floor operators

| Operator | Value | Holds when | Join (effective value) |
|---|---|---|---|
| `level_at_least` / `level_at_most` | `L0`…`L5` | kernel ≥ / ≤ floor | max / min |
| `ordered_at_least` / `ordered_at_most` | member of an explicit `order` (radius `R0`…`R5`; tier `none`,`T0`…`T3`; reasoning; sensitivity; export) | later / earlier or equal | max / min in the order |
| `decimal_at_least` / `decimal_at_most` | fixed-point decimal string (e.g. `"0.8"`), compared exactly | ≥ / ≤ | max / min |
| `set_superset` | list | contains every floor member | union (kernel order, missing floor members appended) |
| `set_subset` | list | contains no member outside the floor | intersection |
| `bool_toward` | boolean with `strict` | kernel = strict, or floor ≠ strict | strict if either is strict |
| `equals` | scalar | equal | the floor value |

A leaf missing from the kernel takes the floor value. An unknown operator, class or `floor_schema_version` makes the
binary `BINARY_BELOW_TRUST_POLICY`, which is read-only. There is no partial evaluation (`19` §4).

**Value canonical form (for pinned digests):**
- GOV-JCS-1 applies (`07` §2).
- A YAML float is represented as `{"$decimal": "<shortest round-trip text>"}`.
- A YAML date is represented as its string.

The TPS itself carries decimal strings, so it stays within GOV-JCS-1's integer-only numbers.

### 3.4 Leaf enumeration (inventory-driven)

Enumeration follows only the CSI's declarations. It never infers structure from the tree under judgement:
- **Mappings** descend key by key into dotted leaves, for example `SECURITY_POLICY.never_index_classes`.
- **Declared collections** (`path`, `id_field`) produce one membership leaf, `NAME.path[id_field]#members`, plus member
  leaves, `NAME.path[id_field=<id>].<field>`. A declared collection that is not a list of objects with unique string ids
  is a structure violation.
- **Undeclared lists** are a single leaf whose value is the whole list.
- **Declared subtrees** (`subtree: true`) are one leaf whose value is the whole node.

A leaf rule key MAY use `*` for one plain segment, but only below at least two literal segments, and never for
`project_tunable`. A `[id=*]` segment matches any member. Catch-all rules are refused by the inventory lint (§6.1).

## 4. Precedence floor, per concrete key

POLICY_PRECEDENCE rules are resolved as the runtime resolves them: the first rule whose `key` pattern matches wins
(`runtime/src/policy_precedence.rs` `rule_for`, `key_matches`), with `default_mode` otherwise. Adding, reordering or
re-scoping rules can therefore weaken a key without touching any single rule. Revision 3 floors the **effective rule of
every concrete key** instead of individual rule entries.

**Strength lattice for the project layer.**
- A rule tuple is `(mode, kind, order, strict_value, exception_relaxable)`.
- `a ≥ b` iff all of the following hold:
  - `a.exception_relaxable` implies `b.exception_relaxable`;
  - one of:
    - `a.mode = immutable`;
    - `b.mode = overridable`;
    - the modes are equal and, for `floor`/`ceiling`, kinds and orders are equal, and for `strengthen_only_bool`,
      strict values are equal.
- All other pairs are incomparable. The **join** of incomparable rules is `immutable` with `exception_relaxable: false`.
  That is a flat lattice with safe tops.

**Universe.** Every leaf key of every policy file, plus every rule key pattern (instantiated) from the registered and the
installed rule lists.

**Check.**
- For every key in the universe: `effective_rule(installed, key) ≥ effective_rule(registered, key)`; otherwise
  `precedence_weakened`.
- At policy loading, the rule applied to the project layer is the join.

**Exceptions** (`PROJECT_EXCEPTIONS`) are applied after the join, subject to two conditions:
- effective `exception_relaxable` = registered ∧ installed;
- regardless of any attribute, no exception relaxes a key whose class is `floor`, `pinned`, `members` or `precedence`,
  or any key under `SECURITY_POLICY.`, `AUTHORITY_POLICY.`, `HUMAN_GATE_POLICY.`, `TOOL_POLICY.`, `POLICY_PRECEDENCE.`
  or `ROLES.` (compiled prefix list).

## 5. Classification principle and the TPS v1 draft

### 5.1 Policy files: never weaker than POLICY_PRECEDENCE

For every policy leaf, the CSI class MUST be at least as strong as what the registered precedence already grants the
project layer. The derivation proposes these classes, and the lint enforces them:

| Registered effective mode for the key | Permitted classes |
|---|---|
| `overridable` | any, including `project_tunable` |
| `immutable` | `pinned`, or `floor` with `equals` |
| `floor` (kind level, radius, tier, ordered, number) | `floor` with the matching `*_at_least`, or `pinned` |
| `ceiling` | `floor` with the matching `*_at_most`, or `pinned` |
| `additive` | `floor` `set_superset`, `members` `ids_superset`, or `pinned` |
| `shrink_only` | `floor` `set_subset`, or `pinned` |
| `strengthen_only_bool` | `floor` `bool_toward` with the same strict value, or `pinned` |

### 5.2 Non-policy files (explicit)

| Area | Class | Why |
|---|---|---|
| `roles/ROLES.yaml` `roles[id]` | `members` `ids_equal` | Removing an id reclassifies `gov decide --by <id>` answers as human (`gates.rs` `answer`). Adding one creates an authority level. |
| `ROLES.roles[id=*].level` | `floor` `level_at_most`, per id | the actor level for every authority check (`authority.rs` `level_of`); raising it is a weakening |
| `ROLES.roles[id=*].minimum_tier`, `.default_reasoning` | `floor` `ordered_at_least` | routing quality floors (`routing.rs`) |
| `ROLES.roles[id=*].name` | `pinned` | rendered into adapters |
| `ROLES.groups.<g>` | `floor` `set_subset` | group membership grants memory-namespace access (`authority.rs` `role_in`) |
| `ROLES.authority_levels.*.*` | `informational` | display vocabulary; no runtime reader in 4.1.5 (only `authority_levels_required` is read) |
| `constitution/HARD_INVARIANTS.yaml` `invariants[id]` | `members` `ids_equal` plus each member `pinned` | statements are copied verbatim into adapters (review RV2-A06) |
| `tools/registry/TOOLS.yaml` `tools[tool_id]` | `members` `ids_subset` plus each member `pinned` | descriptors carry executed install and health commands (RV2-A08); removal is a narrowing |
| `SECURITY_POLICY.secret_content_patterns[id]` | `members` `ids_superset`; registered members' `regex` `pinned`; additional members `covered_by_collection` | an added pattern only classifies more material as secret; a registered pattern cannot be removed or edited |
| `POLICY_PRECEDENCE.rules[key]` | `precedence` (§4); `layers` `pinned`; `default_mode` `equals immutable` | per-key lattice |
| `KERNEL.yaml` version, contract, CLI/runtime and schema versions, `supported_from_versions` | `release_bound` | equal to the signed statement |
| `KERNEL.yaml` `payload_dirs`, `framework_revision`, `adapter_versions` | `pinned` | |
| `schemas/*.schema.json`, `skills/SKL-*.yaml`, `adapters/*`, `overlay-templates/*.yaml`, `taxonomy/*.yaml`, `commands/COMMAND_CONTRACT.yaml`, `constitution/CONSTITUTION.md`, `policies/ENFORCEMENT_MAP.yaml`, `tools/mcp/registry.yaml` | `pinned_file` | non-orderable constitutional content |
| `migrations/M-*.yaml` | `transaction_input` | §3.1 |
| `migrations/README.md`, `tools/installers/README.md` | `informational_file` | documentation |

### 5.3 Counts (executed, `evidence/CSI-check-*.json`)

| Kernel | Files | Leaves by class | Coverage result |
|---|---|---|---|
| `framework/` | 113 | floor 234, pinned 160 (plus 96 pinned files), project_tunable 57, release_bound 32, members 3, precedence 1, collection_id 37, covered_by_collection 85, informational 14 | exit 0: no unclassified file or leaf; all floors, pins and memberships hold |
| `release/releases/4.1.5/kernel` (121 files including migrations and tools) | 121 | floor 234, pinned 177 (plus 97 pinned files), members 4, transaction_input 4, informational_file 2, others as above | exit 0 |
| `release/releases/4.1.2/kernel` | 113 | — | exit 2: `AUTHORITY_POLICY.authority_levels_required.approve_cit` unclassified; 64 registration violations |
| `release/releases/4.1.3/kernel`, `4.1.4/kernel` | 117, 119 | — | exit 3: 64 and 62 registration violations |

Every one of the 308 leaves the review reported unfloored or partially floored now has a class. The mapping is listed per
leaf in `evidence/P1r3-floor-coverage.json` part 1.

## 6. Enforcement points

### 6.1 Coverage checker (release gate)

`constitutional-surface/csi_check.py check <kernel> [--inventory <csi>]` is the architectural reference for the check the
producer, the canonical CI and `gov trust draft-policy` MUST run.

**Exit codes:**
- 0 — pass;
- 2 — coverage failure: unclassified, ambiguous or structural;
- 3 — a floor, pin, membership or precedence violation, or a value stronger than registered;
- 4 — inventory consistency failure: a class weaker than precedence, a catch-all rule, or a `project_tunable` key that is
  not overridable;
- 5 — inventory malformed: default other than deny, unknown vocabulary, or missing registrations.

**Self-test:** `csi_check.py selftest --scratch <dir>` injects 25 mutations and verifies the genuine and
forward-compatible cases pass. Result: 26 of 26 cases as expected (`evidence/CSI-selftest.json`).

### 6.2 Producer and publisher

- `gov release build` MUST run the check against the named TPS. It refuses a release unless the check exits 0, with codes
  `SURFACE_UNCLASSIFIED`, `SURFACE_UNREGISTERED`, `FLOOR_VIOLATION`, `FLOOR_NOT_REGISTERED` or `PRECEDENCE_WEAKENED`.
- The canonical repository's CI MUST run the same check on every release commit and fail the release on non-zero.
- `gov trust draft-policy` MUST derive the next CSI draft and list three things:
  - every classification change;
  - every registration change: new, removed or replaced digests and member ids;
  - every computed reduction (§7).

  The root ceremony signs only after reviewing that list.
- **Strengthening is mechanical.** Any change of a kernel value that the named TPS does not already register is
  `FLOOR_NOT_REGISTERED` (floors) or `SURFACE_UNREGISTERED` (pins). The release therefore cannot ship until a TPS
  registers the new value. No one has to remember to raise anything.

### 6.3 Eligibility and use

- E7 (`19` §6) is the surface check at ingress and at use.
- The effective policy (`19` §5) is:
  - the eligible installed kernel or, failing that, the EmbeddedSnapshot;
  - every `floor` leaf joined with the effective TPS;
  - `pinned` leaves only when registered in the effective TPS;
  - otherwise the consumer's compiled fail-closed default.

### 6.4 Floors raised without a new kernel

Because joins use the effective TPS, a newer TPS can raise a floor over an older eligible kernel that is registered under
an older TPS. P1r3 demonstrates this with `migration-executor` capped at L2 and `min_confidence` at 0.9 over the genuine
4.1.5 kernel. On the real 4.1.5 binary, the raised floors refuse `task release --force` by `migration-executor` and an
agent answer at confidence 0.85 (`evidence/P1r3` part 3 d, e).

### 6.5 Compiled consumer and decision-point registers

- Every policy key the binary reads MUST appear in a compiled **consumer register** naming its decision point.
- Decision points flagged security-relevant MUST read only keys of class `floor`, `pinned`, `members` or `precedence`.
  These are authority, secret and sensitivity classification, indexing and export, gate answering, plugin and tool
  authorisation and installation, precedence and exceptions, install authority, and upstream export.
- The build MUST fail (`SURFACE_CONSUMER_UNCLASSIFIED`) when a consumed key has no classification in the compiled TPS,
  or when a security-relevant decision point reads a `project_tunable` or `informational` key.
- This connects D-0003 (`ENFORCEMENT_MAP`: every key is enforced or informational) to the surface. A key D-0003 lists as
  `enforced_by` a security decision point cannot be classified away.

## 7. Schema evolution cannot introduce an unfloored setting

| Change | Result |
|---|---|
| New key in an existing constitutional file | `UNCLASSIFIED` until a root-signed TPS classifies it (checker S01, S03; P1r3 T9) |
| New constitutional file | `UNCLASSIFIED` (S02). Under a pinned glob it is `surface_unregistered` (S19). |
| New member of a keyed collection | `surface_membership` (S05, S17), except in additive collections |
| New runtime consumer of a key | the build fails unless the key is classified (§6.5) |
| New floor semantics (class or operator) | `floor_schema_version` bump; older binaries become `BINARY_BELOW_TRUST_POLICY`, read-only |
| Reclassification toward a weaker class (`floor` → `project_tunable`, `pinned` → `informational`, removal of a floor value, a weaker precedence registration) | a **computed reduction**: it MUST appear in the arriving TPS's cumulative `lowering_history`, or that TPS is invalid, and it needs the per-project trust gate (`19` §10, `27`) |
| Classification toward a stronger class, or removal of a registered digest | strengthening; no gate |

### 7.1 Forward compatibility (HO-0001 §4)

The Capability Acceptance Contract, the Gate W artifact-flow and consumption-integrity policy, and the G0–G6 governance
health scheduler are classified with the existing vocabulary. They need no new class:

| Future artefact | Classification |
|---|---|
| Owner-supplied normative Markdown (hash-bound) | `pinned_file` |
| Compiled executable YAML | `structured`: acceptance requirements as `floor` (`bool_toward`, `set_superset`, `decimal_at_least`); non-orderable content as `pinned` |
| Its schema and evidence map | `pinned_file`, or `structured` with `pinned` leaves |
| Gate W task input manifests, consumption receipts, lineage requirements | `floor` `bool_toward` (required), `set_superset` (required receipt fields), `pinned` (receipt schema) |
| G0–G6 scheduler | `floor` `decimal_at_most` (maximum intervals), `ordered_at_least` (severity), `project_tunable` only where POLICY_PRECEDENCE makes the key overridable |

Checker case S22 adds `policies/CAPABILITY_ACCEPTANCE_POLICY.yaml` and `constitution/CAPABILITY_ACCEPTANCE_CONTRACT.md`
to a kernel. It extends only the inventory data and passes (exit 0).

**Constitutional files outside the release kernel** (for example an owner-supplied contract under `spec/`) use the same
vocabulary in a CSI `domain` other than `kernel`. Their registration source MUST be one of:
- a verified TPS, for release-shipped content;
- a local trust-gate confirmation of the file digest (`27`), for owner-supplied project content.

It is never a repository record alone (rule 18).

## 8. HO-0001 §3.1 test list — evidence

| Required test | Mutation | Checker (`evidence/CSI-selftest.json`) | Reference evaluation (`evidence/P1r3` part 2) | Consumption on the real 4.1.5 binary (`evidence/P1r3` part 3) |
|---|---|---|---|---|
| Role → authority map | backend-engineer L1→L4; change-controller L3→L5; new role `superuser` L5; role removed | S04 exit 3, S05 exit 2, S06 exit 3 | T1 and the review tamper: ineligible; effective levels equal genuine | L1 `resume`: harm (review tamper consumed directly) → `AUTHORITY_DENIED` (revision-3 effective kernel) |
| Sensitivity and indexing exclusions | `never_index_classes` → [secret]; secret patterns emptied; `sensitivity_classes` reordered | S07, S08 exit 3 | T2: effective equal genuine | AWS credential indexed and retrievable → excluded, not retrievable |
| Irreversible Human Gate authority | `agent_resolvable_when` R5 / 0.0 / irreversible; `must_be_presented_in_chat` false; `answer_gate` L1 | S09 exit 3 | T3: effective equal genuine | agent answers R5 irreversible gate → `AUTHORITY_DENIED` |
| Plugin and tool permission floor | `plugins.min_authority` L0; elevated classes reduced; `auto_install_conditions` reduced; licence added; new tool with install command | S10, S17 exit 3 | T4: effective equal genuine | — |
| Outbound and export controls | `never_export_classes` → [secret]; `on_secret_in_export_payload` warn; upstream approval policy; `forbidden_paths` reduced; product namespace export allowed | S11 exit 3 | T5: effective equal genuine | — |
| Project override controls | rule weakened; earlier overridable rule inserted; `SECURITY_POLICY.*` made overridable; `default_mode` and `layers` changed; `exception_relaxable` set on gate rules | S12, S13, S14 exit 3 | T6: effective equal genuine; exception relaxation of `SECURITY_POLICY.never_index_classes` refused | — |
| Install and update authority | `install_kernel` L0, `update_apply` L0/L1 | S15 exit 3 | T7: effective equal genuine | — |
| Exception authority | `grant_policy_exception` L1; `exception_relaxable` on authority and security rules | S16 exit 3 | T8: effective equal genuine; exception relaxation false for compiled prefixes, and for registered-false ∧ kernel-true | — |
| A future unknown constitutional field | `SECURITY_POLICY.outbound_hosts_allowlist: ["*"]`; new policy file | S01, S02, S03 exit 2 | T9: ineligible (unclassified); effective equal genuine | — |
| Value stronger than registered | `resume_control` L4→L5 without a TPS raise | S21 exit 3 (`FLOOR_NOT_REGISTERED`) | — | — |
| Agent-facing content | invariant statement rewritten; adapter template edited | S18, S20 exit 3 | — | — |

## 9. Outside the surface (stated)

- **The binary's code.** It is the TCB. Its authentication is `25`.
- **Project overlay values within precedence.** The project governs itself as T4. Weakening of recorded project strength
  is reported by `26` §6 (rule 20).
- **Agent behaviour within granted permissions.** Enforcement is by `gov`. Agent-facing kernel content is pinned, and
  its consumption is `18` §12.

## 10. Residuals

| ID | Residual | Bound |
|---|---|---|
| CS-1 | The correctness of each classification is a root-ceremony review responsibility. | Classifying too strictly fails closed. Classifying too weakly is limited by the lint (never weaker than precedence; no catch-alls; `informational` never read by a security decision point, §6.5), and any remaining weakness needs a root-threshold signature. |
| CS-2 | Every final release that changes pinned or unregistered content needs a TPS at root threshold. | Ceremony frequency (`14` RK-17; `21` OP-1). |
