# Held-out attack register (RV2-A01 … RV2-A36)

These attacks were authored by this review and are not in `12`. "Revision 2 as written" states what the specification
produces. **E** marks attacks executed or computed in `evidence/`.

## A — Floors and eligibility

| ID | Attack | Adversary | Expected secure outcome | Revision 2 as written | Finding |
|---|---|---|---|---|---|
| RV2-A01 | Authentic eligible release whose ROLES raises an L1 role to L4; all TPS floors hold | A7+A2, or a future or older release | actor levels bounded by T0/TPS; `AUTHORITY_DENIED` | unspecified. **E** P1a: L1 passes an L4 operation | H1 |
| RV2-A02 | Authentic eligible release with empty or never-matching secret patterns | same | secret classification from TPS/embedded; file excluded | unspecified. **E** P1b: secret indexed and retrievable | H1 |
| RV2-A03 | Authentic eligible release widening `agent_resolvable_when`; an agent answers a trust gate | same | trust gates never agent-resolvable (compiled rule) | unspecified. **E** P1c: agent answers an R5 irreversible gate | H1, M1 |
| RV2-A04 | Release sets `exception_relaxable: true` on a SECURITY rule; A2 commits an approving decision record and an exception | A7+A2 | exceptions never relax floor or security/authority keys | unspecified | H1, M1 |
| RV2-A05 | Release reorders `POLICY_PRECEDENCE.layers` so the overlay outranks the kernel for unfloored keys | A7+A2 | layer order registered | unspecified | H1 |
| RV2-A06 | Release rewrites HARD_INVARIANTS statements keeping the ids; adapters copy the new text | A7+A2 | invariant content registered | ids only | H1 |
| RV2-A07 | Release sets `CHANGE_POLICY.auto_approve_max_radius: R5` and empties `human_gate_triggers` | A7+A2 | CIT gating from TPS | unspecified | H1 |
| RV2-A08 | Release adds a tool descriptor with an `install_command` and widens `auto_install_conditions` | A7+A2 | tool commands content-registered | unspecified | H1 |

## B — Freshness and authorisation

| ID | Attack | Adversary | Expected secure outcome | Revision 2 as written | Finding |
|---|---|---|---|---|---|
| RV2-A09 | Ephemeral CI runner, binary compiled at TPS v1; A2 commits an older authentic eligible release and strips the PTR (TPS v3) | A2 | governed mutations refused, or `FRESHNESS_UNPROVEN` with read-only | **E** P4-B5: verified, `CURRENT_KNOWN(1)`, floor lowered | H2 |
| RV2-A10 | As A09 with a release revoked in the stripped TSS | A2 | refused | **E** P4-B5: eligible | H2 |
| RV2-A11 | As A09 with a release signed only by a key removed in the stripped root N+1 | A2+A7 | refused | verifies | H2 |
| RV2-A12 | `min_binary_version` bypass by stripping the PTR | A2 | old binary read-only | not enforced | H2 |
| RV2-A13 | A2 commits an answered `framework_update` gate record bound to the target digest | A2 | a repository record is a request | **E** P2: update applied without `gate present` or `decide` | M1 |
| RV2-A14 | Plugin (A3) writes an answered downgrade gate and runs `gov update --rollback` | A3 | local human confirmation required | accepted | M1 |
| RV2-A15 | Release-candidate statement with `trust_state_sequence = 2^53−1` | A7 | reference ignored or a hint | **E** P4-B1: STALE for all ingress, no override, not cleared by revocation | M2 |
| RV2-A16 | Trust-state key publishes a TSS with `root_version: 999` | A7 | reference rejected as unresolvable; successors admissible | **E** P4-B4: every honest successor is a REGRESSION | M2 |
| RV2-A17 | Certification key publishes CERTIFIED seq 3 after WITHDRAWN seq 2, unreferenced, no attestation | A7 | WITHDRAWN stays effective | **E** P4-B2: lifted | M3 |
| RV2-A18 | Two TSS with the same sequence and different content | A7 or publisher error | `TRUST_STATE_EQUIVOCATION` | **E** P4-B3: both admissible, silent | M4 |
| RV2-A19 | TSS n+1 whose `previous_state_digest` names an unknown TSS while a different TSS n is known | A7 | chain break detected | admissible | M4 |
| RV2-A20 | TPS v4 keeps a lowering that v3 declared; the verifier holds v2 | owner error | gate required | **E** P4-B6: silent lowering | M5 |

## C — Byte binding

| ID | Attack | Adversary | Expected secure outcome | Revision 2 as written | Finding |
|---|---|---|---|---|---|
| RV2-A21 | Long-lived process across an update that raises floors, and across a `refuse_operation` revocation | honest, A7 | re-check at each unit of work; reload or refuse | the snapshot is kept for the process lifetime | M7 |
| RV2-A22 | A2 edits a rendered adapter body and the hash in `adapter-manifest.json`; the agent follows it | A2 | detected; agents obtain kernel content from `gov` | CI-only binding | M8 |
| RV2-A23 | Hard link to a staged file, written after read-back | A3 | refused before the exchange (`st_nlink`) or rolled back | rolled back after commit | L2 |
| RV2-A24 | `governance/.tx/<TX>/journal.json` committed to Git | A2 | a tracked `.tx/` is ignored or refused; clones not `IN_TRANSACTION` | every clone `IN_TRANSACTION` | M9 |
| RV2-A25 | Forged `migrated` journal with a weakened `overlay.prev` (identity unchanged), then `gov recover` | A3, A2 | computed-weakening gate | restored silently | M9 |
| RV2-A26 | Automatic rollback after an update that delivered TPS v3; then clone the repository elsewhere | honest | `governance/trust/` still holds v3 | v3 removed with the exchanged directory | M9 |

## D — Purposes and the TCB

| ID | Attack | Adversary | Expected secure outcome | Revision 2 as written | Finding |
|---|---|---|---|---|---|
| RV2-A27 | `release-final` key signs an artifact statement for a malicious `gov`; the operator runs `gov trust verify-artifact` | A7+A5 | refused without attestation, certification and threshold | accepted | H3 |
| RV2-A28 | Genuine but older binary (compiled root, TPS or TSS below the VTS high-water) presented as an upgrade | A5 | `BINARY_T0_ROLLBACK` | cannot be checked (schema) | H3 |
| RV2-A29 | OP-4 "no": the candidate-signing key signs `artifact-final` | A7 | refused | accepted | H3 |
| RV2-A30 | Root version grants one key both `certification-status` and `trust-state` | owner misconfiguration | `PURPOSE_SEPARATION_VIOLATION` | accepted | M6 |

## F — Pre-RoT binaries

| ID | Attack | Adversary | Expected secure outcome | Revision 2 as written | Finding |
|---|---|---|---|---|---|
| RV2-A31 | 4.1.5 `update --rollback` on a RoT-1 project that has a legacy update snapshot | A14, A10 | no byte written | **E** P3: kernel, lock and overlay overwritten; `verified: true`; restricted file served | H4 |
| RV2-A32 | 4.1.5 `init --force` on a RoT-1 project | A14 | no byte written | **E** P3: same | H4 |
| RV2-A33 | 4.1.2 `task create` and `rebuild-memory` on a RoT-1 project | A14 | refused before any write | **E** P3/P3b: runs; restricted file exposed | H4 |
| RV2-A34 | RoT-1 remedy (`kernel reinstall`) after RV2-A31 | — | project strengthening restored, or weakening reported | not restored, not reported (specification reading) | H4 |
| RV2-A35 | 4.1.5 `adopt rollback --batch N`, `cit execute`, `tools install`, `plugins register` on a RoT-1 project | A14 | no byte written | untested by the pack | H4 |
| RV2-A36 | 4.1.3 and 4.1.4 binaries, full command matrix | A14 | no byte written | untested | H4 |
