# Output 23 — Constitutional Surface, total floor semantics and the Overlay Surface

> **RoT-1 revision 7 — PROPOSED, pending fresh independent reviews; not approved, not implemented.**
> Revision 7: the certified production profile CP-1 (`35`) governs this file. Where the text below names an owner option
> other than the CP-1 selection, the freshness-witness purpose, a platform signing path, OP-3 mode B or the revision-6
> first-contact manifest, that text is non-production history: the mode is excluded and absent or refused (`35` §4). Parameters
> are the CP-1 values (`35` §2); consequence statements are the CS7 blocks of `21`, `30`, `32`–`34`.
> (Revision 6 banner follows.)
> **Revision 6** closes blocking class **BC5-3** (review r5 RV5-H3) with `34`: registered content is derived first-hand by
> the registration authority, verification is bound to exactly the registered candidate and kernel, E7 applies AP-5's
> restrictors, and registration reductions are computed at the verifier with security-classified changes listed per
> project (§6.1, §10 CS-2, §12.4, §12.5 amended; checker S71–S77).
> **Revision 5** closes blocking class **BC4-3** (review r4 RV4-H3: release-scoped registration of non-orderable content)
> under rule FD-1 (`29`): the registration of each release fixes every non-join unit and the kernel tree (new §12). §3.1,
> §3.2, §6.3, §7, §7.2 and §10 are amended accordingly. Everything review r4 CD4-0 retained (default deny, closed
> vocabulary, exact precedence registration, required presence, one YAML profile, the directed join, the Overlay Surface,
> strength over effective policy) is unchanged.
> Revision 3 added this file for R2-H1. Revision 4 closes blocking class **BC-1** (review r3 RV3-H1: constitutional-surface
> soundness for project-owned strength and for absence). It absorbs the root of RV3-M5 and the precedence case of RV3-M7,
> and meets HO-0001 §3.1 and §4. Carried items: RV3-M5 (CR-02), RV3-M7, RV3-L2 (CR-07), RV3-L3 (CR-08), RV3-L5 (CR-10).
> Normative keywords: MUST, MUST NOT, SHOULD.

## 1. The class

**Revision 2.** It registered 145 floor keys. The mistaken equivalence was *registered floor keys ⇒ constitutional
policy*.

**Revision 3 kept** (review r3 CD3-0 confirms these sound):
- the whole kernel payload is the surface;
- its classification is root-signed inside the Trust Policy;
- unknown content is denied;
- the floor vocabulary is closed, and floor leaves are joined.

**The review of revision 3 found two narrower equivalences (RV3-H1):**

| Mistaken equivalence | How it failed |
|---|---|
| *a rule that refuses more project overrides is at least as strong* | The revision-3 order ranked `immutable` above every mode, and joined incomparable rules to `immutable`. `immutable` also refuses every project **strengthening**. Three routes removed project-owned controls while every check passed: a kernel that moved precedence rules to `immutable` (RV3-B-A01, executed on 4.1.5: authority, indexing and gate harms); a kernel with POLICY_PRECEDENCE deleted (RV3-D-A10 R07, 66 of 85 rules `immutable`); and a root-signed TPS tightening applied without a per-project gate (RV3-D-A02). |
| *every leaf present is classified ⇒ the registered constitution is in force* | Removing a registered file or leaf passed the checker and E7 (RV3-D-A10 R01–R09). The fallback for missing pinned content was undefined (RV3-M7). |

A third issue shared the root: the project-strength detector (`26` §6) and computed weakening (`19` §9) read the overlay,
not the effective policy. They were blind to all three routes (RV3-M5 root). `28` §2.1 explains why these survived
revision 3.

**Revision 4 changes the kernel's role instead of adding conditions to it:**
1. **Precedence is read from the Trust Policy only.** The kernel's POLICY_PRECEDENCE never enters effective policy. It
   must equal its registration exactly, or the release is ineligible (§4.1).
2. **The order is sound in both directions.** It is used only where two root-signed registrations meet (§4.2).
3. **The project layer is a directed join.** No refusal discards admitted strengthening (§4.5, `19` §5.3).
4. **Absence is not neutral.** Every registered file and leaf is required (§3.5).
5. **Project-owned strength is evaluated over the effective policy** and over every classified overlay input. Migrations
   are default-deny over a root-registered **Overlay Surface** (§11, `26` §6, `19` §9).

## 2. Definitions

| Term | Definition |
|---|---|
| Constitutional Surface | Every file of a release kernel payload admitted by the tree rules (`07` §5.1; `KERNEL_MANIFEST.json` excluded), every leaf of every structured file, and every concrete key of the policy universe. |
| Constitutional Surface Inventory (CSI) | The machine-readable classification of the surface. It is the **surface section of the Trust Policy Statement** (`19` §3), signed under `trust-policy` at root threshold (KS-2). Schema: `schemas/constitutional-surface-inventory.schema.json` (schema version 2). The draft for TPS v1 is `constitutional-surface/CONSTITUTIONAL_SURFACE_INVENTORY.yaml`, derived by `csi_derive.py` from the current kernel. |
| Floor semantics | For a file, one mode and one presence (§3.1, §3.5). For a leaf, one class (§3.2) with its operator, registered values or registered digests, and one presence. |
| Default deny | A file matching no file rule, or a leaf matching no leaf rule, is `UNCLASSIFIED`. |
| **Required presence** | Every registered file and leaf is required unless the inventory declares it `optional` under the presence lint (§3.5). |
| **Registered precedence** | The ordered POLICY_PRECEDENCE rule list, `default_mode` and `layers` registered in a Trust Policy. |
| **Strength direction** | The direction in which a change to a leaf is a strengthening, read from the leaf's registered classification (§4.2). It is never read from a rule. |
| **Held registration** | The Trust Policy registration under which a project's strength was last recorded (`24` §8 per-project record). |
| **Overlay Surface** | The Trust Policy section that gives every overlay input a strength direction and lists the only migration-writable targets (§11). |
| **Owner constitutional domain** | The Trust Policy slots for owner-supplied constitutional files outside the kernel (§7.2). |
| Named TPS / Effective TPS | As revision 3: the TPS the release names; the highest admissible TPS the verifier holds (`17` S3). |

The binary never derives a classification from a kernel.

## 3. Closed vocabulary (`floor_schema_version: 3`, compiled)

Version 3 changes the semantics of the `precedence` class and adds presence and the YAML profile. A binary implementing
version 2 is `BINARY_BELOW_TRUST_POLICY` (read-only) against a version-3 Trust Policy.

### 3.1 File modes

| Mode | Meaning | Registration | Violation |
|---|---|---|---|
| `structured` | YAML or JSON whose every leaf is enumerated (§3.4) and classified | per leaf | per leaf |
| `pinned_file` | non-orderable content (schemas, skills, adapters, overlay templates, taxonomies, command contract, constitution text, enforcement map, MCP registry) | **the one SHA-256 registered for this path by the registration of the release (§12)** | `surface_unregistered_for_release` |
| `transaction_input` | migrations, consumed only inside the install transaction from authenticated buffers (`04` V10) | the digest registered for this release (§12) and the release statement's `migrations[]`, **and every operation targets a migration-writable Overlay Surface key (§11.3)** | V10 codes; `migration_operation_not_permitted`; `surface_unregistered_for_release` |
| `informational_file` | documentation with no runtime reader | rationale | — |

### 3.2 Leaf classes

| Class | Meaning | Kernel value used? | Violation (E7) |
|---|---|---|---|
| `floor` | orderable value with an operator and a registered floor | joined with the effective TPS floor | `floor_violation` (weaker than named); `floor_not_registered` (stronger than named) |
| `pinned` | non-orderable value (a leaf or a whole keyed-collection member); **the registration of the release fixes exactly one digest (§12)** | only the value registered for the policy-root release; otherwise the fallback of §6.3 | `surface_unregistered_for_release` |
| `members` | the member-id set of a declared keyed collection | **the set registered for the release (§12), additions included**; a project-layer addition follows the directed join | `surface_membership` |
| **`precedence`** | the POLICY_PRECEDENCE rule list | **never** (§4.1) | **`precedence_unregistered`** (any difference from the named registration) |
| `release_bound` | equals a field of the signed release statement | yes | V8/V11 codes |
| `project_tunable` | a key the registered precedence marks `overridable`, read by no security decision point | yes | — (lint) |
| `informational` | no runtime reader | yes | — (lint) |
| `collection_id`, `covered_by_collection` | collection plumbing | per collection | per collection |

### 3.3 Floor operators

Unchanged from revision 3. The operators are `level_at_least`/`at_most`, `ordered_at_least`/`at_most`,
`decimal_at_least`/`at_most`, `set_superset`, `set_subset`, `bool_toward` and `equals`. Each has the join given there.

**Revision 4 change.** A registered floor leaf missing from a kernel **no longer takes the floor value**. It is refused
(§3.5).

### 3.4 Leaf enumeration

Unchanged. Enumeration is inventory-driven, and it never infers structure from the tree under judgement.

### 3.5 Presence: absence is not neutral (CD3-1 (4); RV3-M7)

1. **Files.**
   - Every path rule is `required` unless declared `optional`.
   - Every path named by a glob rule's registered digests is required under the same rule.
   - A required file missing from a kernel is `surface_required_missing`: coverage failure, checker exit 2, E7
     ineligible.
2. **Leaves.** Every concrete leaf rule of a present structured file is required, including collection memberships and
   registered member content. Wildcard rules, `informational`, `collection_id` and `covered_by_collection` are not. A
   missing required leaf is `surface_required_missing`.
3. **Presence lint.**
   - **Who may be `optional`.** An `optional` file must carry `absent_rationale`, and is permitted only where absence
     removes a capability and never a control. That means one of:
     - a `pinned_file`, `informational_file` or `transaction_input` rule; or
     - a structured file whose leaves are all `pinned`, `informational`, collection plumbing or an `ids_subset`
       membership.
   - **Who may not.** A `policy_file` is never optional, and a `floor`, `pinned`, `members` or `precedence` leaf is never
     optional.
   - **The draft TPS v1 declares optional** only `tools/registry/TOOLS.yaml` (absence offers no kernel tools),
     `tools/mcp/registry.yaml`, `migrations/M-*.yaml` (bound by `migrations[]`) and the two README files.
4. **Changing presence.** `required` → `optional` is a computed reduction (`19` §10.6).
5. **Consequence for POLICY_PRECEDENCE.**
   - Deleting the file makes the release ineligible.
   - Even where a policy root lacks it, the project-layer rule of every key is the registered one (§4.1).
   - **The absence of POLICY_PRECEDENCE, or of any rule, changes no key's effective project-layer semantics.**

Evidence:
- `csi_check.py selftest` S31–S40: every RV3-D-A10 removal, and the deleted floor leaf of RV3-B I09, exit 2.
- `evidence/P1r4-project-strength-and-absence.json` part A3: R01–R09 all exit 2.
- `evidence/rerun-RV3-D-surface-forward-compat-and-removal.json`: R01–R09 exit 2 with the reviewer's unmodified script.

### 3.6 One YAML and JSON profile (CR-08; RV3-L3)

The producer checker, the canonical CI, and the binary's surface evaluator and consumers parse constitutional documents
with one profile:
- YAML 1.2 core booleans only (`true`/`false`). A YAML-1.1-only token (`on`, `off`, `yes`, `no`, `y`, `n`) is refused.
- No anchors, aliases, merge keys or explicit tags.
- No duplicate or non-string mapping keys.
- For JSON, no duplicate members.

A violation is `SURFACE_STRUCTURE(yaml_profile)`: checker exit 2, E7 ineligible.

Evidence:
- selftest S41–S43;
- `evidence/rerun-RV3-B-A03-A14-A16-probes.json`: RV3-B-A14 exits 2 for all 10 `bool_toward` leaves written as `on`.

## 4. Precedence

### 4.1 Exact registration; effective precedence only from registrations (CD3-1 (1), (2))

1. **E7.** A kernel's POLICY_PRECEDENCE MUST equal the named TPS registration: the ordered list of `(key, mode, kind,
   order, strict_value, exception_relaxable)`, the `default_mode`, and `layers` (a pinned leaf). Any difference, whether
   a rule moved to `immutable`, a reordering with identical per-key effect, or a changed `exception_relaxable`, is
   `precedence_unregistered`. Checker exit 3; selftest S12–S14, S16, S26–S30, S45, S55.
2. **Effective project-layer rule.** For every concrete key *k* of project *p*:
   ```
   rule_eff(k) = registered(effective TPS, k)                         if p holds no registration with a pending reduction for k
               = join( registered(effective TPS, k), registered(held, k) )   otherwise (§4.3)
   ```
   The kernel's POLICY_PRECEDENCE, and the EmbeddedSnapshot's, are never inputs.
3. **Consequences.**
   - A kernel precedence change is refused, and even an accepted kernel cannot change project-layer semantics.
   - A deleted file is refused and changes nothing.
   - A TPS change applies to a project that held a stronger registration only through the per-project gate.

Evidence (`evidence/P1r4-project-strength-and-absence.json`, part B, executed on the real 4.1.5 binary):
- Each RV3-B-A01 variant (floor, ceiling, additive, shrink_only, strengthen_only_bool, and the review's three-rule
  example) exits 3.
- The revision-3 effective kernel loses the project strengthening. The revision-4 effective kernel keeps it: authority
  (`AUTHORITY_DENIED`), indexing (customer file excluded) and gate (`AUTHORITY_DENIED`) harms flip.
- RV3-D-A10 R07 exits 2, with all harms flipped.

### 4.2 Strength order, sound in both directions (CD3-1 (1))

**Strength direction of a key.** It comes from its registered classification.

| Classification | Direction |
|---|---|
| `floor` `*_at_least` | up |
| `floor` `*_at_most` | down |
| `set_superset`, `ids_superset` | add |
| `set_subset`, `ids_subset` | remove |
| `bool_toward` strict *v* | toward *v* |
| every other class | none (no change is a strengthening) |

A pattern key without a concrete leaf takes the direction of its registered mode. The lint keeps modes and
classifications consistent.

**What a rule admits.** For a key of direction *d*, a rule admits a set *A(rule, d)* ⊆ {**s** (a project strengthening),
**w** (a project weakening)}:

| Mode | *d* ≠ none | *d* = none |
|---|---|---|
| `overridable` | {s, w} | {w} |
| `immutable` | {} | {} |
| `floor` / `ceiling` / `additive` / `shrink_only` / `strengthen_only_bool(v)` | {s} if the mode's direction is *d*; otherwise {w} | {w} |
| unknown mode | {w} | {w} |

**Order.** `a ≥ b` iff all of these hold:
- w ∈ A(a) ⇒ w ∈ A(b): *a* admits no weakening *b* refuses;
- s ∈ A(b) ⇒ s ∈ A(a): *a* admits every strengthening *b* admits;
- `a.exception_relaxable` ⇒ `b.exception_relaxable`;
- for `floor`/`ceiling` in both, equal kind and order.

**Join.** `A(join) = (A(a) ∩ A(b) ∩ {w}) ∪ ((A(a) ∪ A(b)) ∩ {s})`, and `exception_relaxable` only if both. The join never
discards admitted strengthening and never admits a weakening either rule refuses.

A change of registration from *b* to *a* is a **computed reduction** iff `a ≱ b`. That includes removing an admitted
strengthening (for example `additive` → `immutable`), whoever made the change.

Evidence:
- `evidence/P1r4-project-strength-and-absence.json` part A1: 343 mode × mode × direction combinations; 0 unsound pairs; 0 joins dropping strengthening.
- The five RV3-D-A01 pairs: the revision-3 order holds `immutable ≥ mode`, and the revision-4 order does not.
- `evidence/rerun-RV3-D-precedence-lattice.json`, the synthesis reviewer's script unmodified: 0 unsound pairs, and all
  five RV3-D-A02 tightenings are computed reductions whose join keeps project strengthening.

### 4.3 Where the order is used

It is used only where two **root-signed** registrations meet:
1. **TPS acceptance** (`17` S3 (c), `19` §10.6). A precedence reduction must appear in the cumulative `lowering_history`.
   Otherwise the TPS is invalid (`TRUST_POLICY_UNDECLARED_LOWERING`).
2. **Per project.** Until the per-project `policy_lowering` trust gate accepts the reduction, the project's effective
   rule is the join with its held registration (§4.1 (2)).
3. **Lint** (§5.1).

Evidence:
- `evidence/P1r4-project-strength-and-absence.json` scenarios RV3-D-A02 (honest-owner `never_index_classes` and root-ceremony authority levels):
  - the reduction is reported (`reductions` exit 6 without history, 0 with);
  - the project-layer mode is `additive` / `floor` before the gate and `immutable` only after it;
  - on 4.1.5 the customer file stays excluded and `resume` stays denied until the gate.
- selftest S53, S54.

### 4.4 Exceptions

Applied after the project layer.
- Effective `exception_relaxable` is the **registered** value only.
- No exception relaxes a key of class `floor`, `pinned`, `members` or `precedence`.
- No exception relaxes a key under the compiled prefixes `SECURITY_POLICY.`, `AUTHORITY_POLICY.`, `HUMAN_GATE_POLICY.`,
  `TOOL_POLICY.`, `POLICY_PRECEDENCE.` or `ROLES.`.

### 4.5 Project layer

The project layer is a directed join under `rule_eff` (`19` §5.3). A project override is decomposed into its
strengthening and weakening components in the key's direction:
- a component the rule admits is applied;
- a component it refuses is refused;
- no refusal discards an admitted component.

Evidence: `evidence/P1r4-project-strength-and-absence.json` part D. A TPS raise of the never-index floor refuses the whole project override under the 4.1.5
semantics that revision 3 kept, so the customer file is indexed. Under the directed join it stays excluded.

## 5. Classification principle and the TPS v1 draft

### 5.1 Policy files: never weaker than the registered precedence

Unchanged from revision 3:

| Registered effective mode | Permitted classes |
|---|---|
| `overridable` | any, including `project_tunable` |
| `immutable` | `pinned`, or `floor` with `equals` |
| `floor` | `floor` `*_at_least`, or `pinned` |
| `ceiling` | `floor` `*_at_most`, or `pinned` |
| `additive` | `floor` `set_superset`, `members` `ids_superset`, or `pinned` |
| `shrink_only` | `floor` `set_subset`, or `pinned` |
| `strengthen_only_bool` | `floor` `bool_toward` with the same strict value, or `pinned` |

**A consequence revision 4 relies on.** A TPS that registers `immutable` for a key must also reclassify the leaf to
`pinned` or `equals`, and the lint refuses one that does not (exit 4). A tightening is therefore always visible as both a
precedence reduction and a direction change (`28` A-R4-03).

### 5.2 Non-policy files and security decision points

Revision 3's explicit table stands (ROLES, HARD_INVARIANTS, TOOLS registry, secret content patterns, POLICY_PRECEDENCE,
KERNEL.yaml, pinned files, migrations, documentation).

**Revision 4 reclassifies keys read by security decision points (CR-07; RV3-L2).** Their registered precedence stays
`overridable`, so the project layer keeps A2's existing authority. A kernel can no longer change them without a
root-signed registration.

| Key | Revision 3 | Revision 4 | Consumer |
|---|---|---|---|
| `MEMORY_POLICY.embedding.provider` | `project_tunable` | `pinned` | embedder: which plugin receives indexed text |
| `MEMORY_POLICY.reranker.provider` | `project_tunable` | `pinned` | reranker: which plugin receives retrieved text |
| `ARCHIVE_POLICY.default_retrieval_for_archive` | `project_tunable` | `floor` `bool_toward` strict `false` | retrieval scope of historical paths |
| `LEARNING_POLICY.upstream.aggregate_metrics_enabled` | `project_tunable` | `floor` `bool_toward` strict `false` | upstream packet content |
| `HUMAN_GATE_POLICY.continue_independent_work` | `project_tunable` | `floor` `bool_toward` strict `false` | work continuation while a gate is pending |

Evidence:
- selftest S44;
- `evidence/rerun-RV3-B-A03-A14-A16-probes.json`: RV3-B-A16 exits 3.

The compiled consumer register (§6.5) remains the build gate for any further key.

### 5.3 Counts (executed, `evidence/CSI-check-*.json`, draft TPS v1 inventory schema version 2)

| Kernel | Files | Leaves by class | Result |
|---|---|---|---|
| `framework/` | 113 | floor 237, pinned 162 (+96 pinned files), project_tunable 52, release_bound 32, members 3, precedence 1, collection_id 37, covered_by_collection 85, informational 14 | **exit 0** |
| `release/releases/4.1.5/kernel` | 121 | floor 237, pinned 179 (+97 pinned files), members 4, transaction_input 4, informational_file 2, others as above | **exit 3**: its four historical migrations carry `set_lock_field`, which RoT-1 refuses (R-MIG-3). 4.1.6 re-issues the chain without lock operations (`11` WP-18). |
| the same payload with lock operations removed (stand-in for re-issued migrations) | 121 | as above | **exit 0** |
| `release/releases/4.1.2/kernel` | 113 | — | exit 2: 1 unclassified leaf, 62 required files or leaves missing (including POLICY_PRECEDENCE), 65 violations |
| `release/releases/4.1.3/kernel` | 116 | — | exit 2: 15 required missing, 65 violations |
| `release/releases/4.1.4/kernel` | 119 | — | exit 2: 6 required missing, 64 violations, 44 precedence registration differences |

## 6. Enforcement points

### 6.1 Coverage checker (release gate)

`constitutional-surface/csi_check.py` is the architectural reference for the check the producer, the canonical CI and
`gov trust draft-policy` MUST run.

| Command | Exit codes |
|---|---|
| `check <kernel>` | 0 pass; 2 coverage failure (unclassified, ambiguous, structure, YAML profile, **required missing**); 3 floor, pin, membership, **precedence registration** or **migration-operation** violation, or a value stronger than registered; 4 inventory consistency (class weaker than precedence, catch-all, `project_tunable` not overridable, **presence lint**); 5 inventory malformed (including a missing Overlay Surface) |
| `check-owner <repo> --registrations F` | 0; 2 a required owner constitutional file absent; 3 unconfirmed or changed (§7.2) |
| `reductions --old A --new B [--lowering-history H]` | 0; 6 a computed reduction not declared (§7) |
| `selftest` | 0 iff all cases behave as expected (revision 4: 56 cases; revision 5: 71; **revision 6: 78**, `evidence/r6/CSI6-selftest.json`, 78 passed, the 71 revision-5 cases identical) |
| `verify-registration --registration R --source-kernel K` (revision 6) | 0 the proposal equals the content derived from the custodian's own kernel build; 3 `REGISTRATION_CONTENT_NOT_ESTABLISHED` (`34` R-CON-1) |
| `registration-reductions --verifier F --referenced IDS` (revision 6) | 0; 6 `REGISTRATION_UNDECLARED_REDUCTION`; 7 `INCOMPLETE`, a referenced registration not held (`34` R-CON-4) |
| `registration-changes --held A --new B` (revision 6) | 0 no security-classified change; 8 security-classified changes listed for the per-project gate (`34` R-CON-5) |

### 6.2 Producer and publisher

- `gov release build` MUST run `check` against the named TPS, and refuse unless it exits 0.
- The canonical CI MUST run the same check on every release commit.
- `gov trust draft-policy` MUST list:
  - every classification change;
  - every registration change;
  - every **computed reduction** (`reductions`): floor values, classes, memberships, presence, **precedence in both
    directions**, **newly migration-writable overlay targets**, removed owner-domain slots, and the non-surface TPS
    fields of `19` §10.6.

  The root ceremony signs only after reviewing that list.
- **Strengthening is mechanical.** A kernel value stronger than registered is `FLOOR_NOT_REGISTERED`; a pinned value not
  registered is `SURFACE_UNREGISTERED`. **A precedence rule different from registration is `PRECEDENCE_UNREGISTERED`.**

### 6.3 Eligibility and use (`19` §5–§6)

- E7 is the surface check at ingress and at use: coverage, presence, profile, floors, pins, memberships, exact precedence
  and migration operations.
- **Effective values.**

  | Leaf class | Value |
  |---|---|
  | `floor` | root kernel joined with the effective TPS |
  | `pinned`, `members`, `pinned_file` | the value registered **for the policy-root release** (§12.3); the kernel of an eligible release carries exactly that value |
  | `precedence` | registered only (§4.1) |

- **Fallback for unregistered or missing pinned and members content (RV3-M7 (c); revision 5).** The value used is the
  EmbeddedSnapshot value, if the registration of **the running binary's embedded release** is held and registers it.
  Otherwise the dependent decision point refuses with `SURFACE_VALUE_UNAVAILABLE(key, decision_point)`. The consumer register names each decision point's fail-closed
  meaning, for example:
  - no secret patterns: indexing and export of the affected scope refuse;
  - no gate policy: agent answers refuse;
  - no plugin descriptor set: plugin execution refuses.

  There is no unspecified consumer default.

### 6.4 Floors raised without a new kernel

Unchanged. Joins use the effective TPS. Evidence: `evidence/P1r3-floor-coverage.json` part 3 (d, e), re-run against the revision-4 library,
still enforced (`evidence/rerun-P1r3-against-r4-lib.json`).

### 6.5 Compiled consumer and decision-point registers

As revision 3, with two additions:
1. every **overlay** key the binary reads MUST appear with its Overlay Surface direction (§11). The build fails on an
   unclassified consumed overlay key (`OVERLAY_CONSUMER_UNCLASSIFIED`);
2. each security decision point records its fail-closed behaviour for `SURFACE_VALUE_UNAVAILABLE` (§6.3).

## 7. Schema evolution cannot silently introduce an unfloored setting

| Change | Result |
|---|---|
| New key in an existing constitutional file | `UNCLASSIFIED` until a root-signed TPS classifies it |
| New constitutional file | `UNCLASSIFIED`; under a pinned glob, `surface_unregistered` |
| New member of a keyed collection | registered with the release that introduces it (§12); otherwise `surface_membership` |
| New runtime consumer of a key or overlay key | the build fails unless it is classified (§6.5) |
| New floor semantics (class, operator, presence rule) | `floor_schema_version` bump; older binaries become `BINARY_BELOW_TRUST_POLICY` |
| Reclassification toward a weaker class; removal of a floor value | computed reduction: cumulative `lowering_history` plus the per-project `policy_lowering` gate |
| **A precedence registration that admits a new weakening or removes an admitted strengthening** | **computed reduction** (§4.2) |
| **A registered file or leaf removed from a release** | refused (`surface_required_missing`) unless a TPS unregisters it, which is a computed reduction |
| **`required` → `optional`** | computed reduction |
| **A new migration-writable overlay target** | computed reduction |
| A kernel POLICY_PRECEDENCE differing from registration | refused (`precedence_unregistered`) |
| Classification toward a stronger class | strengthening; no gate |
| **A later registration whose unit value equals a value an intermediate registration superseded** (revision 5) | **computed reduction** `registration_reversion` (§12.4) |
| **A later registration omitting a unit the previous registration had, or narrowing a member-id set against its direction** (revision 5) | **computed reduction** `registration_unit_removed` / `registration_members_reduced` (§12.4) |
| **A registration that changes an already registered release, or two releases at one sequence** (revision 5) | malformed and refused (`REGISTRATION_REWRITE`, `REGISTRATION_SEQUENCE_EQUIVOCATION`) |
| **A set-valued registration** (several permitted digests for one unit) (revision 5) | malformed (`REGISTRATION_NOT_SINGLE_VALUED`) |

### 7.1 Forward compatibility (HO-0001 §4)

The Capability Acceptance Contract, the Gate W artifact-flow and consumption-integrity policy and the G0–G6 scheduler are
classified with existing vocabulary, as revision 3 showed. Revision 4 adds one release-consistency rule: a release adding
a constitutional policy carries the same precedence rules in its kernel as the TPS registers.

Evidence:
- selftest S22, updated to that rule: exit 0.
- `evidence/RV3-D-A09-A10-rerun-r4-release-consistent.json`, the synthesis reviewer's F01–F12 with release-consistent
  fixtures: F01, F05, F06, F07 and F09 exit 0; the weakening cases F03, F04, F08, F10 and F11 exit 3; F02 (a registered
  requirement removed) and F12 (an unknown key) exit 2.
- The unmodified script (`rerun-RV3-D-surface-forward-compat-and-removal.json`) reports exit 3 for its positive cases.
  Its fixtures add rules to the inventory only, so exact registration refuses them, as designed.

### 7.2 Owner constitutional domain (RV3-M7 (d); RV3-D-A18)

1. The TPS `surface.owner_domain[]` declares **slots** for owner-supplied constitutional files outside the kernel, for
   example `spec/contracts/CAPABILITY_ACCEPTANCE_CONTRACT.md`. Each slot carries `path`, mode, presence and the consumers
   that read it.
2. A slot's digest is registered **per machine** by the `owner_constitutional_file` trust gate (`27`), never by a
   repository record (rule 18).
3. **Absence** of a required slot file is fail-closed for its consumers on every machine, confirmed or not
   (`OWNER_CONSTITUTIONAL_FILE_MISSING`).
4. **A present file whose digest this machine has not confirmed, or whose digest changed,** is fail-closed for its
   consumers (`OWNER_CONSTITUTIONAL_FILE_UNCONFIRMED` / `…_CHANGED`). A fresh CI runner therefore refuses the dependent
   decisions until an operator decision pin or confirmation registers the digest.
5. The confirmed digest is part of the project-strength vector (`26` §6).
6. **Binding groups (revision 5; RV4-L10).** A slot may declare `binding_group`. The group (for example the Capability
   Acceptance Contract Markdown, compiled YAML, schema and evidence map) is confirmed, pinned and consumed only as a set:
   the confirmation or decision pin names the **group digest**, SHA-256 over the sorted `(path, file digest)` pairs of every
   member. Any member absent is `OWNER_CONSTITUTIONAL_FILE_MISSING`; a computed group digest that equals no confirmed or
   valid pinned group digest is `OWNER_CONSTITUTIONAL_GROUP_UNCONFIRMED`. Several valid decision pins resolve by exact set
   match only; per-path registrations of grouped slots are ignored. Evidence: selftest S66 (Markdown v2 with YAML v1 while
   both sets are pinned: exit 3) and S67 (matching v2 set: exit 0).

Evidence: `csi_check.py check-owner` is the reference; selftest S50–S52 give absent 2, unconfirmed 3 and confirmed 0.

## 8. HO-0001 §3.1 test list — evidence

| Required test | Checker (`CSI-selftest.json`) | Reference (`P1r3`/`P1r4` part A) | Consumption on the real 4.1.5 binary |
|---|---|---|---|
| Role → authority map | S04–S06 | P1r3 T1 (re-run against the revision-4 library) | P1r3 (a): L1 `resume` `AUTHORITY_DENIED` |
| Sensitivity and indexing exclusions | S07, S08, S28 | P1r3 T2; P1r4 additive | P1r3 (b); **P1r4 additive, three-rule and R07: project `confidential` stays excluded** |
| Irreversible Human Gate authority | S09, S27 | P1r3 T3; P1r4 ceiling | P1r3 (c); **P1r4 ceiling: agent answer under project R0 `AUTHORITY_DENIED`** |
| Plugin and tool permission floor | S10, S17, S29, S30 | P1r3 T4; P1r4 shrink_only (`approved_licences`) | P1r4: project narrowing stays applied |
| Outbound and export controls | S11 | P1r3 T5; P1r4 shrink_only (`upstream.allowed_payload`) | P1r4: project narrowing stays applied |
| **Project override controls** | S12–S14, S16, **S26–S30, S45, S53–S55** | **P1r4 A1 (0 unsound), A4, all nine scenarios** | **P1r4: every RV3-B-A01 mode, R07 and both RV3-D-A02 tightenings keep project strengthening** |
| Install and update authority | S15 | P1r3 T7; P1r4 floor (`resume_control`) | P1r4 floor: `resume` `AUTHORITY_DENIED` under the project L5 raise |
| Exception authority | S16, S55 | P1r3 T8 | — |
| A future unknown constitutional field | S01–S03, S22 | P1r3 T9; RV3-D-A09 re-run | — |
| **Absence of registered content** | **S31–S40** | **P1r4 A3** | P1r4 R07 |
| **YAML profile** | **S41–S43** | RV3-B-A14 re-run | RV3-B-A14 runtime reads `"on"` as a string; the checker now refuses it |
| Agent-facing content | S18, S20 | — | — |

## 9. Outside the surface (stated)

- **The binary's code.** It is the TCB; its authentication, including its source, is `25`.
- **Project overlay values.** The project governs itself as T4 within registered precedence. The Overlay Surface (§11)
  and the strength vector (`26` §6) report every weakening against a recorded vector.
- **Agent behaviour within granted permissions.** Enforcement is by `gov`.

## 10. Residuals

| ID | Residual | Bound | Test |
|---|---|---|---|
| CS-1 | The correctness of each classification, direction and Overlay Surface entry is a root-ceremony review responsibility. | Too strict fails closed. Too weak is limited by: the lint (never weaker than precedence; no catch-alls; no optional control; `immutable` only with `pinned`/`equals`); the consumer register; exact precedence registration; directed joins; and computed reductions in both directions. Any remaining weakness needs a root-threshold signature and appears in the `draft-policy` change list. | selftest S23–S25, S53; RT-73…RT-79, RT-100 |
| CS-2 | **Restated in revision 6.** One registration ceremony per release (OP-2) fixes source, inputs, environments, content and final together, and each custodian derives the content first-hand (`30` R-REG-3 (g), `34` R-CON-1); verification is bound to the registered candidate and kernel (`34` R-CON-2). Retention no longer widens what later releases may carry (§12.3 rule 5); whether older releases stay eligible is OP-11. | ceremony frequency (`14` RK-17; `21` OP-2) | REG5; selftest S57–S70 |

## 11. The Overlay Surface (new; CD3-1 (3); CR-02, RV3-M5)

### 11.1 Purpose

The project overlay (`governance/overlay/`) is T4 project configuration. Security decision points consume parts of it.
Revision 3 computed weakenings over four enumerated categories (RV3-M5). Revision 4 classifies **every overlay input the
binary consumes** in a root-signed TPS section, with default deny.

### 11.2 Directions (draft TPS v1: `CONSTITUTIONAL_SURFACE_INVENTORY.yaml` `overlay_surface`)

| Overlay input | Direction (a strengthening is…) |
|---|---|
| `DATA_SENSITIVITY.classifications` | a pattern added or its class raised (sensitivity order) |
| `DATA_SENSITIVITY.identifiers_to_strip` | an identifier added |
| `DATA_SENSITIVITY.default_class` | a higher class |
| `REPOSITORY_CONTRACT.paths` | for every recorded pattern, the effective contract (later rules override; `secret` wins) keeps index flags off, `agent_read: prohibited`, `export: denied`, `default_retrieval: false`, `mutation` at least as restrictive, and `secret` class |
| `REPOSITORY_CONTRACT.roots` | none: any change counts |
| `TOOL_PERMISSIONS.roles`, `tool_allowlist`, `mcp_servers` | a subset: no new role, no new permission, tool or server |
| `TOOL_PERMISSIONS.install_authority_roles` | a subset |
| `PROJECT_EXCEPTIONS.exceptions` | a subset of recorded entries, each unchanged |
| `PROJECT_POLICY.policy_overrides` | evaluated over the **effective policy** in each key's registered direction |
| `PROJECT_POLICY.readiness.enforce_pre_implementation_cells` | toward `true` |
| `PROJECT_POLICY.staleness.on_stale_close` | toward `fail` |
| `CAPABILITY_PROFILE.categories` | no applicable category becomes inapplicable |
| `plugins/*.yaml` | the descriptor set with digests is a subset |
| name, alias, tests, gates, routing preferences, governance paths | none (not in the strength vector) |
| any other overlay file | **default deny**: recorded by digest; any change or addition is a weakening candidate |

### 11.3 Migration targets (default deny)

A `transaction_input` migration operation is permitted only if all of these hold:
- it is `note`, `require_index_rebuild` or `regenerate_adapters`, or it targets a file directly inside
  `governance/overlay/` (a plain file name, never a path);
- it writes a key the Overlay Surface registers as `migration_writable`; and
- it is not a lock operation (R-MIG-3).

Draft TPS v1 marks writable only schema versions, `PROJECT_POLICY.governance` and `PROJECT_POLICY.gates` (path moves and
template reconciliation), `PROJECT_POLICY.human_gates` (historical rename), `REPOSITORY_CONTRACT.paths` (template
tightening) and `PROJECT_EXCEPTIONS.yaml` creation from its template.
- **Refusal.** A violation is `migration_operation_not_permitted`: checker exit 3, and at the transaction
  `MIGRATION_OPERATION_NOT_PERMITTED` before any write.
- **Gate.** Every permitted operation is still evaluated by the strength vector over the effective result, and a
  non-empty weakening needs the `weakening` trust gate (`19` §9).

Evidence (`evidence/P1r4-project-strength-and-absence.json` part C, migrations):

| Migration case (RV3-B-A18 shapes) | Before any write | Computed weakening, `weakening` gate |
|---|---|---|
| `install_authority_roles` widened | refused | reported |
| a role granted `SECRET_READ` | refused | reported |
| a `PROJECT_EXCEPTIONS` entry added | refused | reported |
| `identifiers_to_strip` emptied | refused | reported |
| `policy_overrides` dropping the project never-index class | refused | reported |
| a registered target that weakens (`**/.env*` indexed) | passes the whitelist | reported |
| target `../../spec/decisions/HDG-0001.yaml` | refused | — |
| a registered strengthening (control) | passes | none |

Selftest: S46–S48 refused; S49 permitted.

## 12. Release-scoped registration of non-join units (revision 5; BC4-3)

### 12.1 Root cause accepted

Revision 4 registered **permitted digests** per pinned key, member and file: a domain, not a function of the release.
For orderable leaves the floor join made any member of the domain safe; for non-orderable units nothing did. Retention of a
superseded digest for installed releases (forced by `SURFACE_VALUE_UNAVAILABLE` and by release-global presence) let a
threshold-1 `release-final` restore superseded content in a higher-sequence release with no reduction, gate or detector
(RV4-B-A08 on real 4.1.5; D-A02 T1–T4). Under FD-1 the lower-trust final was the selector of effective content.

### 12.2 Units and single-valued registration

1. **Non-join units** are: every `pinned` leaf and whole pinned member (`leaf:<key>`); every member-id set
   (`members:<key>`); every `pinned_file` and `transaction_input` file (`file:<path>`); every owner-domain binding group
   (§7.2). **Join units** (floors, registered precedence) stay in the Trust Policy and are joined as §4 and §6.4 state.
2. The **registration of release *R*** (`30` §5: `constitution {kernel_tree_digest, units}`) maps every non-join unit
   present in *R* to **exactly one value** and fixes *R*'s kernel tree digest. A set-valued registration is malformed
   (`REGISTRATION_NOT_SINGLE_VALUED`); revision 4's retention form is that shape (REG5, selftest S56: exit 5).
3. Registrations are **append-only** (`30` R-REG-4): rewriting a registered release, or registering two releases at one
   sequence, is malformed (selftest S61, S62; REG5 rewrite row: exit 5).
4. The classification of units (which rule, which class, which presence) stays in the root-signed Constitutional Surface.
   The draft inventory's per-key `digests` maps are the projection of one registration (the draft release) and carry one
   value each (179 pinned keys, 97 pinned files, 0 multi-valued).

### 12.3 Eligibility and effective values (E7 at ingress and at use)

1. **Exact lookup.** *R* is eligible only if a registration for *R*'s release id is effective on the machine (referenced by
   the effective Trust State, `30` R-REG-2), names *R*'s final statement, and every non-join unit of *R*'s kernel and its tree
   digest equal that registration. Otherwise `release_unregistered` or `surface_unregistered_for_release`. **Ranges,
   unions and "latest registered" are never used.**
2. A registration of a release is never evidence for another release: content registered for 4.1.6 is ineligible when
   presented as 4.1.8, as a gap sequence or at an inflated sequence (REG5 `ranges_excluded`: exit 3 each).
3. **Presence is release-scoped.** Required presence (§3.5) of a non-join unit is evaluated against *R*'s registration: a
   member introduced for 4.1.7 is not required of 4.1.6 (selftest S69: exit 0; REG5 legitimate 4.1.6 under the set that
   registers 4.1.7: exit 0).
4. **Knowledge follows state.** A machine that holds no effective registration for *R* treats *R* as unregistered and never
   falls back to an earlier release's content (REG5: a machine holding only 4.1.6's registration refuses genuine 4.1.7 with
   exit 3, and accepts it with exit 0 once it holds the 4.1.7 registration).
5. **Legitimate retention does not widen.** An installed release remains eligible at its own registration while later
   releases carry their own; no later registration makes superseded content eligible under another release. Whether older
   releases stay eligible at all is OP-11.
6. `release_bound`, `project_tunable` and `informational` leaves are fixed too, because the kernel tree digest is registered:
   `release-final` selects nothing (selftest S60: one tunable leaf changed, exit 3).

### 12.4 Computed reductions over registrations

`csi_check.py registration-reductions` computes, over the ordered registration set:
- `registration_reversion`: a unit value equal to a value an intermediate registration superseded (selftest S63 exit 6,
  S64 with `lowering_history` exit 0; REG5: the owner registering the superseded `aws-access-key` regex for 4.1.8 exits 6
  without history, 0 with);
- `registration_unit_removed`: a unit the previous registration had and the new one omits (selftest S70 exit 6);
- `registration_members_reduced`: a member-id set narrowed against its collection direction.

Each needs a cumulative `lowering_history` entry and, for every project whose record holds the stronger registration, the
per-project `policy_lowering` trust gate (`19` §10.6).

**Revision 6 (CR5-B-04; `34` R-CON-4, R-CON-5).** (a) The **verifier** computes these reductions at ingress and at use over every
registration the effective Trust State references; if one is not held the result is `INCOMPLETE` and E7 refuses the release
(`registration_history_incomplete`); an undeclared reduction refuses it. (b) For non-orderable units only exact reversion,
removal and member narrowing are computed. Every other change of a security-classified unit is selected by the registration
authority and is listed in the per-project `registration_change` gate package before security-relevant use (`registration-changes`,
exit 8). Evidence: `evidence/r6/CON6-*` (RV5-B-A09 variant regex and tool command listed; RV5-B-A10 reversion refused, withheld
intermediate `INCOMPLETE`); selftest S73–S77.

### 12.5 Enforcement points

| Point | Rule |
|---|---|
| `gov release build`, canonical CI | `csi_check.py derive-registration` produces a **proposal** of the unit map (revision 6: never an input to a signature); `check --registrations --release-id` exits 0 on the release's own kernel |
| Registration ceremony | each custodian builds the kernel from the source it fetched and runs `verify-registration` against the proposal (`34` R-CON-1); `gov trust draft-registration` lists every unit that differs from the previous registration and every computed reduction (§12.4) |
| Verifier at ingress and at use | E7 as §12.3 with AP-5's restrictors (`34` R-CON-3); reductions over every referenced registration (`34` R-CON-4); `19` §6 |
| Recorded projects | `registration-changes` lists security-classified changes for the `registration_change` gate (`34` R-CON-5) |
| Consumers | effective values as §6.3 |

### 12.6 Evidence (executed; pack checker as amended, real legacy 4.1.5 as the consumer)

`evidence/r5/REG5-release-scoped-registration.json`: part P and D-A02 T1–T4 — each mixed release refused under every
claimed identity (5 targets × 3 identities, exit 3); legitimate 4.1.6 and 4.1.7 eligible (exit 0); revision-4 retention
form malformed (exit 5); gap, inflation and stale-policy releases refused; rewrite malformed; reversion reported; a
different migration under the same release refused (exit 3). On real 4.1.5, the content revision 5 makes effective keeps
the `ASIA…` key file out of the index and out of query results, while the revision-4 effective content indexes and serves
it (control). Checker self-test: `evidence/r5/CSI5-selftest.json`, 71 of 71, the 56 revision-4 cases unchanged.

