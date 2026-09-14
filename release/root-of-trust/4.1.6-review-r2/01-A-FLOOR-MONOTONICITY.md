# A — Security-floor monotonicity

Question: can an authentic older release, rollback, snapshot restore, recovery, root-policy downgrade, project-specific
gate, partial or stale Trust Policy, or mixed policy state make weaker constitutional policy current? Does authenticity
ever confer eligibility?

Evidence classes: **E** executed in this review (`evidence/`), **C** code reading of the 4.1.5 runtime, **D** design
reading of the revision 2 pack.

## 1. What revision 2 gets right (confirmed)

| Property | Mechanism | Verdict | Basis |
|---|---|---|---|
| Historical 4.1.2–4.1.5 kernels are never eligible | compiled registry only (`05` SV-2); E1 (`19` §6) | holds | D |
| A key the kernel lacks takes the floor value | `19` §5 join | holds; closes the review's R1 shape (4.1.2 lacks `update_apply`) | D; `evidence/P1` part 2 evaluator |
| Trust Policy versions only increase; floors need root threshold | `17` S3; KS-2 | holds for the registered key set | D |
| Required install authority never comes from the target | `19` §8 | holds for *required* levels (but see R2-H1 on *actor* levels) | D |
| Snapshot restore is authenticated and judged under current policy | `20` §3 | holds | D |
| Revoked, below-minimum and historical targets refused without override | `20` §4 | holds wherever the verifier knows the fact | D |

## 2. Falsification attempts

| # | Attack | Adversary | Revision 2 claim | Result | Evidence | Finding |
|---|---|---|---|---|---|---|
| A1 | Authentic older **eligible** release delivered through Git | A2 | floors from the TPS; E10 on known machines | Floored keys hold where the newest TPS is known. **Unfloored constitutional content** (role levels, secret patterns, gate resolution rules, precedence attributes, invariant statements, tool install rules) comes from the older kernel on every machine. On a verifier without retained state running an older binary, floored keys and `min_release_sequence` also fall back to the compiled TPS. | E P1, E P4-B5 | R2-H1, R2-H2 |
| A2 | Rollback (`update --rollback`) to an older eligible release | operator, A2 | gate bound to both digests; floors from TPS | The gate is a repository record that A2 can write (P2). Floored keys hold; unfloored content reverts. | E P2, E P1 | R2-M1, R2-H1 |
| A3 | Snapshot restore | A3 | authenticate + current eligibility | Tampered or ineligible snapshots are refused. An authentic eligible snapshot behaves as A2. | D `20` §3 | — / R2-H1 |
| A4 | Recovery from a planted journal | A3; A2+A3 | `20` §5: downgrade policy against the lock and the VTS record | Holds on machines with a VTS record. On a fresh clone, A2 commits a `swapped` journal with a lock naming the `.prev` identity, and exchange-back needs no gate (equal to RR-2). The `overlay.prev` restore has no computed-weakening check. | D | R2-H2, R2-M9 |
| A5 | Root-policy downgrade | owner error; TPS lineage | monotonic `policy_version`; explicit `lowers[]` plus a per-project gate | A lowering declared in v3 is not detected by a verifier that jumps from v2 to v4 (the gate is keyed on the arriving TPS's own `lowers[]`). `rule_mode_at_least` has no defined order for non-comparable modes. | E P4-B6 | R2-M5 |
| A6 | Project-specific gate, overlay or exception | A2 | overlay applied after the join and strengthen-only | The overlay is sound for floored keys. **`PROJECT_EXCEPTIONS` relax any key whose precedence rule has `exception_relaxable: true`** (`policy.rs:192-255`, `policy_precedence.rs:160-192`). That attribute is not a floor (`rule_mode_at_least` covers only `mode`). The decision record that authorises an exception lives under `spec/`, which A2 can write. `19` §5 never places exceptions relative to the join. | C, D | R2-H1, R2-M1 |
| A7 | Partial or stale Trust Policy | A2 strips `governance/trust/state/` | STALE refuses ingress; use continues with the highest known TPS | A binary compiled at TPS v1, after A2 strips the v3 PTR, enforces v1 floors and v1 `min_release_sequence`. `min_binary_version: 4.1.8` is not enforced. Verdict shows `CURRENT_KNOWN(1)`. | E P4-B5 | R2-H2 |
| A8 | Mixed old/new policy state (PTR v3, VTS v2, compiled v1, kernel registered under v2) | — | highest verified TPS wins; unknown operators make the binary read-only | holds | D | — |

## 3. Floor coverage (executed, `evidence/P1-floor-coverage.json`)

TPS v1 floors were regenerated **exactly** as `examples/make_example.py` derives them (`19` §4 lists the same categories):
145 floors, namely POLICY_PRECEDENCE 86, AUTHORITY_POLICY 47, TOOL_POLICY 5, SECURITY_POLICY 4, HUMAN_GATE_POLICY 2 and
HARD_INVARIANTS 1.

Across the seven files the pack names as constitutional floors (`01` AS-1):
- 125 leaves;
- 59 floored;
- 2 partially floored (precedence rules by `mode` only, invariants by `id` only);
- **64 unfloored**.

The table lists the unfloored leaves that decide security at use time.

| File | Asset | Unfloored leaves (selection) | What they decide in the runtime |
|---|---|---|---|
| `roles/ROLES.yaml` | AS-1 | `roles[*].level`, `groups` | **the actor's authority level for every authority check** (`authority.rs:25-35`) and memory-namespace access (`authority.rs:59-76`). All 47 AUTHORITY_POLICY floors bound *required* levels only. |
| `SECURITY_POLICY` | AS-1 | `secret_path_patterns`, `secret_content_patterns`, `sensitivity_classes`, `on_secret_outside_secret_class` | what is classified secret (`security/secrets.rs:51-79`); `never_index_classes` is useless if nothing is classified |
| `HUMAN_GATE_POLICY` | AS-1 | `agent_resolvable_when.{max_radius,min_confidence,reversible}` | whether an agent may answer a gate (`gates.rs` `answer`). Consumers accept agent answers: `is_answered_yes` and the update gate check ignore `by_kind` (`gates.rs:226-240`, `update.rs:109-176`). |
| `TOOL_POLICY` | AS-1 | `permission_classes`, `auto_install_conditions`, `approved_licences`, `tool_types`, `plugins.descriptor_schema`, `plugins.registry_path` | which tools auto-install and which commands run (`tools.rs:321, 458-464`) |
| `AUTHORITY_POLICY` | AS-1 | `state_classes`, `default_state_class_by_type`, `lifecycle_statuses`, `precedence`, `retrieval_default_excludes_statuses` | which records are authoritative, including `human-gate` records |
| `POLICY_PRECEDENCE` | AS-1 | `layers` (order); per rule `exception_relaxable`, `kind` | which layer wins for unfloored keys; which keys exceptions may relax |
| `HARD_INVARIANTS` | AS-1 | invariant `statement` and enforcement fields (only `id` floored) | the invariant text copied verbatim into agent adapters |
| `CHANGE_POLICY` | not AS-1 | `auto_approve_max_radius`, `human_gate_triggers`, `radius_rules.governance_paths_radius` | whether a CIT needs a human gate |
| `MEMORY_POLICY` | not AS-1 | `namespaces.*.roles`, retrieval filters | who may retrieve what |
| `ENFORCEMENT_MAP` (134 leaves), schemas (AS-2), skills, adapters, command contract (AS-4), tool registry (AS-5) | — | everything | no floor and no content registration |

## 4. Consumption on the 4.1.5 binary (executed, `evidence/P1` part 3)

Both consumers report `kernel trust` `verified: true`. **All 145 TPS v1 floors hold on both kernels** (P1 part 2). The
second kernel changes only unfloored leaves.

| Test | Genuine 4.1.5 kernel | Kernel changing only unfloored leaves |
|---|---|---|
| (a) L1 `backend-engineer` runs `resume` (floor `resume_control: L4` unchanged) | `AUTHORITY_DENIED` | **ok** |
| (b) `product/aws-credentials.md` containing an AWS access key id, after `rebuild-memory` | excluded (`secret_class`); not retrievable | **indexed; returned by `memory query`** |
| (c) L3 `change-controller` answers an R5, confidence 0.1, irreversible gate as an agent | `AUTHORITY_DENIED` | **ok** (`answered_by_kind: agent`) |

The 4.1.5 V-H3 install path was used only to obtain a verified policy root carrying this content. The conclusion does not
depend on V-H3.

Under revision 2, such a kernel is the policy root whenever it is authentic and eligible. That covers:
- any future release that loosens an unfloored value;
- any older eligible release restored by Git, rollback or recovery after a later release tightened one;
- any final that a `release-final` key thief signs and A2 commits (Git-delivered use has no gate).

`min_release_sequence` is the only other barrier. Its raise is an owner action (`19` §10 step 5) that is not tied to any
content change, and E7 and the producer check registered floor keys only.

## 5. Proof obligation: "authenticity cannot confer eligibility"

**Proven** (given retained or compiled knowledge of the relevant fact):
- historical identities (E1);
- candidates in production (E2);
- releases below the known `min_release_sequence` (E3);
- known revocations (E4);
- lineage mismatch (E6).

**Not proven:**
1. An authentic release whose unfloored constitutional content is weaker is eligible by construction. E7 examines only
   registered floor keys, so eligibility makes that content the policy root for about half of the AS-1 leaves and all of
   AS-2, AS-4 and AS-5. (R2-H1)
2. On a verifier without retained state, the inputs to E3, E4 and E5 are chosen by the repository writer above the
   compiled T0. (R2-H2)

**Conclusion.** Revision 2 narrows the RV-H1 class from "any authentic kernel" to "any authentic release at or above the
verifier's known minimum sequence". It does not close the class. The pack's statements need that qualification:
- G11;
- D-0008 rule (6);
- `19` §1: "they cannot restore weaker floors";
- `19` §10: "floors at least as strong as the newest registered ones".

Each holds only for 145 keys, and only on verifiers that hold the newest TPS.
