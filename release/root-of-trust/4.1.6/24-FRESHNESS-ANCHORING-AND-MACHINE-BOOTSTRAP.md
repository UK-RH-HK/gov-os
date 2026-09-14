# Output 24 — Freshness anchoring and new-machine trust bootstrap

> **RoT-1 revision 3 — PROPOSED, pending a fresh independent review; not approved, not implemented.**
> New in revision 3. It closes R2-H2 and R2-L1 as a class and satisfies HO-0001 §3.2. OP-7 is presented in `21` and
> is not decided here. Normative keywords: MUST, MUST NOT, SHOULD.

## 1. The class

On a verifier with no retained state, revision 2 took currency from whatever genuine statements the repository writer
left in place, above the running binary's compiled T0. It still reported `CURRENT_KNOWN(n)` and `verified: true`.
In review evidence `P4-B5`, an older revoked release became the verified policy root, with a lowered floor and no gate
at use.

The mistaken equivalence was *compiled or repository knowledge ⇒ current state*.

Revision 3 does not pretend that a machine can know metadata it has never received. Instead:

1. It **separates safety from freshness**. Safety properties hold on every machine. Freshness is claimed only when an
   **anchor** that the repository writer and the transport do not control establishes it (§3).
2. It **never presents unanchored knowledge as current**. The verdict gains a `freshness` axis, and `CURRENT_KNOWN`
   is withdrawn.
3. It **refuses trust ingress without an anchor**. This architecture minimum is not owner-selectable.
4. It **lets the owner decide (OP-7)** what an unanchored or aged machine may do for governed use. The consequences are
   stated per option.
5. It **persists monotonic local state**, so no replay, stripping or swap can lower a machine below what it has
   verified or been anchored to.

## 2. Safety versus freshness

| Property | Holds without a freshness proof? | Mechanism |
|---|---|---|
| Authenticity of every statement and release | yes | compiled root chain, purposes (`05`) |
| Integrity of installed and enforced bytes | yes | `18` |
| Eligibility against the knowledge held (historical never, below minimum, revoked, lineage) | yes | `19` §6 |
| Effective floors ≥ max(compiled TPS, every held TPS), joined over the whole Constitutional Surface | yes | `19` §5, `23` |
| No relaxation from absence; held negative facts stay effective | yes | `17` MS-1, MS-2 |
| Equivocation and fork detection among held statements | yes | `17` S3, S4 |
| Never below this machine's anchor | yes, once anchored | §3, §8 |
| Trust decisions never authorised by repository records | yes | `27` |
| Pre-RoT binaries cannot write a RoT-1 project | yes | `26` |
| **The held state is the currently published state** | **no — needs an anchor** | §3 |
| **No newer revocation, floor raise, minimum-sequence raise or root rotation applies** | **no — needs an anchor** | §3 |

An attacker who controls the transport or the repository can choose which genuine statements a machine sees, down to
that machine's safety floor: the compiled T0, raised by anything the machine has retained or been anchored to. The
attacker can never create a **current** trusted fact: an unanchored verdict is labelled `UNANCHORED` and is not used for
trust ingress. Under OP-7 (a)–(c), it is not used for governed mutations either.

## 3. Anchors

An **anchor** is a local, monotonic record, stored in the Verifier Trust Store, stating that at time *t* the published
trust state of lineage *L* was at least epoch *e*. The record is established by a source independent of the repository
writer (A2), the source controller (A1) and the transport (A5).

### 3.1 Epoch and state fingerprint

- **Epoch:** `(root_version, root_digest, policy_version, policy_digest, state_sequence, state_digest)` of an admissible
  Trust State Statement and the statements it references.
- **State fingerprint:** `gov-state:<first 8 hex of lineage id>:<state_sequence>:<first 32 hex of SHA-256(GOV-JCS-1(epoch
  object with lineage))>`.
- The owner publishes the fingerprint of every new TSS in the same independent channels as the root fingerprint
  (`06` §2 step 2).

### 3.2 Anchoring events

| Event | How | Independent of | Trust assumption |
|---|---|---|---|
| **Pin** | `<account-home>/.config/gov/trust-state-pins` (schema `schemas/trust-state-pin.schema.json`), resolved from the account database, never from `HOME`, `XDG_*`, `GOV_*` or the repository | A1, A2, A4, A5 | **TA-9:** the pin is provisioned by an operator whom the repository writer does not control (CI runner image, configuration management, organisation-level protected job) |
| **Human confirmation** | `gov trust confirm-state <fingerprint>`. The human types the fingerprint read from an independent channel. `gov` never supplies the value. When the confirmed epoch is not held, the anchor still records it and the machine is `BELOW_ANCHOR` until the statements are supplied. | A1, A2, A4, A5 | TA-5 (as for OP-6) |
| **Witness** (OP-7 (c) only) | a verified, admissible TSS whose `expires_at` is later than the local clock, and whose `issued_at` is not older than the newest witness this VTS has seen | A1, A2, A5, within the expiry window | **TA-7:** local clock honest; coarse rollback detection |
| **Retained** | an earlier anchor in this VTS; statements verified later raise the held epoch monotonically | — | the VTS survives (RS-3) |

These are **not** anchors: the repository (PTR, lock hints, gate records), bundles, `gov trust refresh` input,
environment variables, CLI flags, CI configuration committed to the repository, and the compiled T0. The compiled T0 is
a safety floor. Only OP-7 (d) accepts it for governed use, and never for trust ingress.

The first anchor on a machine is normally set in the same ceremony as lineage confirmation (OP-6):
`gov trust confirm-root <id>` followed by `gov trust confirm-state <fingerprint>`, or one pin file containing both.

## 4. Verdict axes and operation classes

### 4.1 Axes

| Axis | Values | Replaces |
|---|---|---|
| `trust_state` (`17` S9) | `KNOWN(n)` · `INCOMPLETE(n′)` (a higher TSS whose references do not resolve) · `REGRESSION` · `EQUIVOCATION` | `CURRENT_KNOWN(n)`, `STALE`, `HINT_MISMATCH` |
| `freshness` (this file) | `ANCHORED(e, method, age)` · `WITNESSED(e, expires)` (OP-7 c) · `BELOW_ANCHOR(have n < e)` · `UNANCHORED(held n)`; OP-7 (b) and (c) add `ANCHOR_EXPIRED` and `WITNESS_EXPIRED` | — |

Every surface (`gov status`, `gov kernel trust`, context packets, doctor D032/D035, gate text) MUST show both axes. The
label `current` MUST NOT appear without `ANCHORED` or `WITNESSED`. The OP-5 age is measured from the anchor time, and the
age warning is always shown when `UNANCHORED` (R2-L1).

### 4.2 Operation classes (compiled command register)

| Class | Commands (examples) |
|---|---|
| **C0** diagnostics and knowledge intake | `version`, `doctor`, `status` (without policy-dependent sections), `kernel verify`/`trust`, `trust show`, `trust refresh --from` (adds verified knowledge; PTR written only in a transaction), `trust confirm-root`/`confirm-state`, trust-gate confirmation (`27`) |
| **C1** governed read | `context compile`, `memory query`, `continue`, readiness views: anything whose output applies policy filters |
| **C2** governed mutation | tasks, CIT, gates for non-trust decisions, `rebuild-memory`, `plugins register`, `tools install`, adoption batches ≥ 1, `upstream`, checkpoints |
| **C3** trust ingress | `init`, `adopt migrate --batch 0`, `update --apply`, rollback and restore, `kernel reinstall` with another envelope, recovery exchange, `trust verify-artifact` acceptance, profile install, lineage adoption |

### 4.3 Decision table

| Freshness / trust state | C0 | C1 | C2 | C3 |
|---|---|---|---|---|
| `EQUIVOCATION`, `REGRESSION`, `BELOW_ANCHOR` | yes | no | no | no |
| `INCOMPLETE` (with any anchor) | yes | yes | no | no |
| `ANCHORED` / `WITNESSED`, `KNOWN` | yes | yes | yes | yes (with the other `04` §4 conditions) |
| `ANCHORED` under OP-7 (b) with the anchor older than `bootstrap.max_anchor_age_days` | yes | yes | **no** | **no** |
| `WITNESSED` expired under OP-7 (c), no other anchor | yes | yes | **no** | **no** |
| `UNANCHORED` under OP-7 (a), (b), (c) | yes | **no** | **no** | **no** |
| `UNANCHORED` under OP-7 (d) | yes | yes, labelled `FRESHNESS_UNPROVEN` | yes, labelled `FRESHNESS_UNPROVEN` | **no** (architecture minimum) |

**Refusal codes:**
- `TRUST_STATE_UNANCHORED`;
- `TRUST_STATE_BELOW_ANCHOR`;
- `TRUST_STATE_EQUIVOCATION`;
- `TRUST_STATE_REGRESSION`;
- `TRUST_STATE_INCOMPLETE`;
- `TRUST_ANCHOR_EXPIRED`.

Each carries `required`, `held` and `remedy`: refresh, confirm-state, pin, or upgrade.

## 5. The machine list (HO-0001 §3.2)

"Local state" means the VTS (`17` §4; §8 below). Scenario ids refer to `evidence/P4r3-trust-state-model.json`. Each
subsection states what the machine may safely do without a freshness proof, what is gated or read-only, what needs an
anchor or witness, what is persisted locally, and how OP-7 affects the result.

### 5.1 First install on a machine (M1)

- **Starting state.** An empty VTS. The machine holds only T0 plus the bundle or repository it was given.
- **Safe without freshness.** C0: verify the bundle, show both fingerprints, run `trust refresh`.
- **Gated or read-only.** C3 (`init`, update) refuses with `TRUST_STATE_UNANCHORED`. C1 and C2 have nothing to act on
  yet.
- **Anchor needed.** The human confirms the root (OP-6), then the state fingerprint read from the channel.
  - If the bundle holds that epoch, the machine becomes `ANCHORED` and init proceeds through its trust gate (`27`).
  - If the source withholds the confirmed epoch, the machine is `BELOW_ANCHOR` until the statements are supplied.
- **Persisted.** Lineage confirmation, anchor, verified statements, the per-project record after init.
- **OP-7 effect.** None on C3. Under (c), a valid witness in the bundle can anchor instead of a human.
- **Evidence.** `M1_first_install`: all three branches.

### 5.2 Clean CI runner (M2)

- **Starting state.** The VTS is empty on every run.
- **Safe without freshness.** C0.
- **Gated or read-only.** Without a pin, under OP-7 (a), (b) and (c), C1–C3 refuse.
- **Anchor needed.**
  - **Pin.** A pin provisioned in the runner image or by protected organisation configuration. This relies on TA-9: if
    the repository writer controls the job definition, the job is not a governance boundary against that writer at all,
    whatever the trust design.
  - **Witness.** Under OP-7 (c), an unexpired witness TSS in the repository or bundle.
- **Behaviour.**
  - With a pin at `t9` and an intact repository, the runner is `ANCHORED`.
  - With the pin and a stripped repository plus an older binary, it is `BELOW_ANCHOR` and refuses. This flips review
    P4-B5.
  - With an expired witness swapped in by A2, it refuses.
- **Persisted.** Nothing beyond the run. The anchor is the pin.
- **OP-7 effect.** Under (d), C1 and C2 run labelled `FRESHNESS_UNPROVEN`; the review's B5 residual remains for binaries
  older than the newest TPS. C3 never runs unanchored.
- **Evidence.** `M2_clean_ci_runner`, `B5_fresh_old_binary_after_A2_swap`.

### 5.3 Machine restored from backup (M3)

- **Starting state.** The VTS rolls back to an older anchor (epoch 5, anchored 400 days ago), while the real published
  state is 9.
- **Safe without freshness.** Everything at or above epoch 5. The effective state is never below 5, because VTS
  statements persist.
- **Gated or read-only.** Under (b), C2 and C3 refuse once the anchor is older than the limit.
- **Anchor needed.** Re-anchoring (confirm-state or pin) restores C2 and C3 under (b).
- **Persisted.** The restored VTS. When the repository PTR still carries TSS 9, knowledge rises to 9 monotonically.
- **OP-7 effect.**
  - Under (a) and (d), C2 is allowed at the restored anchor, labelled with its age.
  - Under (c), the machine needs a current witness.
- **Evidence.** `M3_restored_from_backup`.

### 5.4 Machine with an old trust epoch (M4)

- **Starting state.** The machine is anchored at 5. A2 offers only TSS 1 and an older release.
- **Safe without freshness.** The effective state stays at 5, the retained anchor; the offered older state is ignored as
  knowledge.
- **Gated or read-only.** Eligibility of the offered older release is judged at epoch 5 (revocations, minimum sequence and
  floors known at 5), plus the per-project downgrade record (`20` §9).
- **Anchor needed.** Freshness beyond 5 needs a newer anchor or a witness.
- **Persisted.** Anchor 5 and its statements.
- **OP-7 effect.** As in §5.3.
- **Evidence.** `M4_old_epoch`.

### 5.5 Machine with no trust epoch (M5)

- **Starting state.** Identical to §5.1 or §5.2 until anchored.
- **Behaviour.** `UNANCHORED`. C3 never runs. C1 and C2 run only under OP-7 (d), labelled.
- **Evidence.** `M5_no_epoch`.

### 5.6 Two machines at different epochs (M6)

- **Starting state.** Machine A is anchored at 9 and machine B at 5, sharing one repository.
- **Behaviour.**
  - Each enforces its own anchor.
  - A never accepts a lower state.
  - B learns 9 when the PTR carries it: the install transaction on A writes the union of its knowledge (`18` §5).
  - If A2 strips the PTR, B stays at 5, never lower.
  - A's lock hint `trust_state_sequence_min: 9` on B is a warning only (`TRUST_STATE_HINT_MISMATCH`). The lock is
    A2-writable, so it can neither refuse nor relax.
- **Divergence.** Allowed and safe. B's remedy is refresh or confirm-state.
- **Evidence.** `M6_two_machines_different_epochs`, `R4_lock_hint_inflation`.

### 5.7 Offline machine returning after a long absence (M7)

- **Starting state.** Anchored at 5 three years ago. No newer metadata reaches it while offline.
- **Safe without freshness.** Everything at epoch 5. Offline use of the installed eligible release continues (MS-6).
- **Gated or read-only.** Under (b), C2 and C3 refuse by age; under (c), for lack of a fresh witness.
- **Anchor needed.** On reconnection, verified statements are ingested monotonically and a new confirmation or witness
  re-anchors.
- **OP-7 effect.** Under (a) and (d), the machine operates at its anchor with the age shown (`ANCHORED(5, human, 1095d)`),
  which is the honest limit.
- **Evidence.** `M7_offline_long_absence`.

## 6. Replay, equivocation, forks and incomplete state

| Case | Rule | Evidence |
|---|---|---|
| Replay of genuine older TSS or TPS | Knowledge is a union and effective state is the highest admissible. Replay can neither lower knowledge nor an anchor. | `R1_signed_state_replay` |
| Replay of an older witness (OP-7 c) | Accepted only by a verifier that never saw a newer witness. Staleness is bounded by the expiry window (TA-7). | `R2_witness_replay` |
| Same-sequence, different-digest TSS (resolved) | `TRUST_STATE_EQUIVOCATION`: C0 only | `B3_same_sequence_fork` |
| Fork across a gap (the verifier lacks intermediates) | Every TSS carries a cumulative `prior_states[]`. A higher TSS omitting a held lower one is not admissible. | `E1_fork_across_a_gap` |
| Fork with an independent anchor | Statements at or below the anchor that are outside the anchored chain are orphans: reported (doctor CRITICAL), never effective, never a constraint | `E3_old_sequence_fork_without_and_with_anchor` |
| TSS referencing an unknown root or policy | Unresolved, so never effective and never a constraint. If it is above the effective sequence, the state is `INCOMPLETE`: C2 and C3 refuse until it is resolved or rotated out. | `B4_*`, `B4b_*` |
| Pin digest differs from the held TSS at that sequence | `EQUIVOCATION` | `R5_pin_digest_mismatch` |
| References in release, candidate or certification statements | Release-local requirements. They constrain only the ingress of that release, or the visibility of that certification, never global state. | `B1_*` |

**Trust-state key blast radius** (corrects revision 2, R2-M2):
- A thief can freeze trust ingress and governed mutation, but only on verifiers that receive an unresolvable or
  equivocating statement above their effective state, and only until the next honest TSS or a root rotation removes the
  key.
- A thief cannot make honest successors regress, lift a negative fact, or create certification.
- A pin or human anchor resolves forks in favour of the anchored chain.

## 7. Gate records supplied from repository state

A repository gate record never authorises a trust decision. Trust gates are answered only by local confirmations bound to
the statement digests (`27`). A repository record without a local binding is a **request**. Review evidence `P2` (an
update applied from an A2-edited gate file) and `R3_gate_record_from_repository` flip.

## 8. Monotonic local state (Verifier Trust Store, per OS account and lineage)

**Location:** `<account-home>/.local/state/gov/trust/<trust_root_id>/`, resolved from the account database.

| Record | Content | Monotonic rule |
|---|---|---|
| `statements/` | every verified statement ever accepted | union; never removed except by explicit `gov trust reset` (A3 can delete: RS-3) |
| `high-water.json` | root version and digest, TPS version and digest, TSS sequence and digest, highest witness `issued_at`, highest verified `issued_at` (clock rollback detection), compiled TBM high-water (`25`) | components never decrease |
| `anchor.json` | epoch, method (pin / human / witness / retained), `anchored_at`, operator, fingerprint | epoch never decreases; `anchored_at` updates only on an anchoring event |
| `lineage.json` | OP-6 confirmation | — |
| `projects/<project_trust_id>.json` | repository paths, highest installed release sequence and CI, project-strength vector (`26` §6), open install transactions (`18` §5.1), adapter rendering digests (`18` §12) | sequence and strength vector raised only by install transactions or gated confirmation |
| `confirmations/` | trust-gate confirmations (`27`) | append-only |

## 9. OP-7 (presented in `21`; not decided here)

| Option | Unanchored machine | Anchored machine | Trust assumptions | Consequences |
|---|---|---|---|---|
| **(a) Anchored only** | C0 only | all; age shown, never limited | TA-5 / TA-9 | Every CI runner needs a pin outside the repository writer's control; long-absent machines operate at their anchor. |
| **(b) Anchored with maximum age** | C0 only | C2 and C3 refused after `max_anchor_age_days` | + TA-7 | Bounds staleness by time; needs honest clocks and periodic re-confirmation. |
| **(c) Expiring witness** | C0–C3 while an unexpired witness verifies; C0 and C1 after expiry | as (a), plus witness renewal | + TA-7; the trust-state key signs heartbeats on a schedule (custody) | Stateless CI without pins; staleness bounded by the expiry window; offline use beyond expiry refuses governed mutation. |
| **(d) Compiled epoch accepted for use** | C0–C2 labelled `FRESHNESS_UNPROVEN`; C3 never | as (a) | none added | The review's P4-B5 residual remains for binaries older than the newest TPS: the owner accepts that a repository writer can select older genuine state for governed use on unanchored machines. |

**Proposal (labelled, not a decision): (a).** It adds no clock assumption and makes the review's B5 class impossible on
every machine. The cost is operational: pins for CI.

## 10. Residuals, restated exactly

| ID | Residual | Bound |
|---|---|---|
| RS-1 | A machine that never receives newer metadata cannot know it exists. | Bounded below by the running binary's compiled T0, raised by the retained anchor or pin and by any verified witness (OP-7 c). Gates do not bound a repository writer's selection of Git-delivered state. Under OP-7 (a)–(c), no governed mutation happens on an unanchored machine. Under (d), unanchored governed use is bounded only by the compiled T0 and is labelled. |
| RS-2 | OP-3 mode B and OP-7 (b)/(c) trust the local clock. | Owner-optional; clock rollback detection against the highest verified `issued_at`. |
| RS-3 | A3 deletes or rewrites its own VTS. | The machine becomes `UNANCHORED` (fails closed under (a)–(c)); rewritten statements that do not verify are ignored. A3 can forge a local anchor or confirmation on its own machine (same-user boundary). |
| RS-4 | A pin provisioned by a party the repository writer controls. | Outside TA-9. Such a job is not a governance boundary against that writer, whatever the design (§5.2). |
