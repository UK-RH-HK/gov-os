# Output 24 — Freshness anchoring, currency and new-machine trust bootstrap

> **RoT-1 revision 5 — PROPOSED, pending fresh independent reviews; not approved, not implemented.**
> Revision 5: currency proofs name the Trust State they cover (CR4-B-07 option 1, CR4-B-06); the witness service's input
> and custody are fixed (CR4-B-02); every ingested non-future statement raises a stateful clock high-water and RS-2 is
> restated (CR4-B-03, RV4-M4); binary acceptance and first admission follow `25` and `31`.
> Revision 3 added this file for R2-H2. Revision 4 closes blocking class **BC-2** (review r3 RV3-H2: anchor satisfaction
> and anchor currency), carried RV3-M2 (CR-03), RV3-M3 (CR-06), RV3-L1 (CR-05) and RV3-L6, and HO-0001 §3.2. OP-7 is
> presented in `21` and is not decided here. Normative keywords: MUST, MUST NOT, SHOULD.

## 1. The class

**Revision 2.** The mistaken equivalence was *compiled or repository knowledge ⇒ current state*.

**Revision 3.** It added anchors. The review of revision 3 found two narrower equivalences (RV3-H2):

| Mistaken equivalence | How it failed |
|---|---|
| *an anchor number is met ⇒ the anchored state is in force* | The anchor was compared with the effective TSS's **sequence number**. A trust-state key presented TSS 100, chaining only t1 and t5, to a machine anchored at t10 whose t9 and t10 were withheld. The machine was `ANCHORED` without the revocation t9 carries (RV3-B-A12, RV3-D-A12). |
| *anchored once ⇒ current* | A pin had no time bound. A CI image pinned at t5 accepted any genuine state ≥ t5 for ever, including a release and a binary revoked later (RV3-B-A02, RV3-D-A15). A one-day witness minted with the threshold-1 trust-state key made a stateless runner `WITNESSED` (RV3-B-A06). |

`28` §2.2 explains why these survived: the anchor was evaluated over a value the supplier chooses.

**Revision 4 removes those inputs from the decision.**
1. **Inclusion.** An anchor is the identity `(sequence, digest)` of a statement. It is satisfied only when that
   statement is held and lies in the effective chain. A statement that does not descend from the anchor is never
   effective, whatever its number (§3.4).
2. **Bounded pins.** A pin carries a mandatory validity. Outside it, the pin is not an anchor (§3.2).
3. **Currency is separate from anchoring.** Trust ingress (C3) and binary acceptance need a **currency proof**
   established within a stated window, or typed into the trust gate itself (§4.4). An aged anchor keeps the safety floor
   and nothing more.
4. **A separate witness purpose.** The `freshness-witness` purpose cannot create state. C3 needs at least two witness
   keys (§3.3).
5. **No surface says `current`.** Every surface shows the anchor, how it was made, its as-of time and age, and a currency
   proof or `CURRENCY_UNPROVEN` (§4.1).
6. **Integrity.** Pins and decision pins that the governed account can write are ignored. `gov` runs repository-supplied
   commands under write confinement (§3.5).

The architecture still does not pretend that a machine can know metadata it never received (§10 RS-1).

## 2. Safety, anchoring and currency

| Property | Holds without an anchor? | Holds with a satisfied anchor? | Needs a currency proof? | Mechanism |
|---|---|---|---|---|
| Authenticity of every statement and release | yes | yes | no | compiled root chain, purposes (`05`) |
| Integrity of installed and enforced bytes | yes | yes | no | `18` |
| Eligibility against the knowledge held | yes | yes | no | `19` §6 |
| Effective floors ≥ max(compiled TPS, held TPS), joined over the Constitutional Surface | yes | yes | no | `19` §5, `23` |
| Held negative facts stay effective; absence is never positive | yes | yes | no | `17` MS-1, MS-2 |
| Equivocation and fork detection among held statements | yes | yes | no | `17` S3, S4 |
| Trust decisions never authorised by repository records | yes | yes | no | `27` |
| **The effective state descends from the published state as of the anchor time** | no | **yes** (inclusion, §3.4) | no | §3 |
| **No revocation, floor raise or root rotation published after the anchor applies** | no | **no** | **yes**, and only as of the proof time | §4.4 |

An attacker who controls the transport or the repository can choose which genuine statements a machine sees, down to:
- the machine's anchored chain, when it has a satisfied anchor;
- otherwise, the compiled T0.

The attacker can never make the machine present a state as current, and can never make a statement that does not
descend from the anchor effective.

## 3. Anchors

An **anchor** is a local record that at time *t* the published trust state of lineage *L* included the Trust State
Statement `(e, d_e)`. The record is established by a source independent of the repository writer (A2), the source
controller (A1) and the transport (A5).

### 3.1 Epoch and state fingerprint (unchanged)

- **Epoch:** `(root_version, root_digest, policy_version, policy_digest, state_sequence, state_digest)`.
- **State fingerprint:** `gov-state:<first 8 hex of lineage id>:<state_sequence>:<first 32 hex of SHA-256(GOV-JCS-1(epoch
  object with lineage))>`.
- The owner publishes the fingerprint of every new TSS in the independent channels (`06` §2 step 2).

### 3.2 Anchoring events

| Event | How | Currency it carries | Trust assumption |
|---|---|---|---|
| **Pin** | `trust-state-pins` (schema `trust-state-pin.schema.json`) in the system pin directory (§3.5), or in the account configuration when the integrity predicate holds. **`provisioned_at` and `valid_until` are mandatory**, and `valid_until − provisioned_at ≤` TPS `bootstrap.pin_max_validity_days`. A pin outside `[provisioned_at, valid_until]` by the local clock is **not an anchor** (`PIN_OUTSIDE_VALIDITY`). | a currency proof for C3 only within `c3_currency_window_hours` of `provisioned_at` | TA-9 restated (§3.5); **TA-7** (clock) |
| **Human confirmation** | `gov trust confirm-state <fingerprint>`, typed from an independent channel; `gov` never supplies the value. If the confirmed statement is not held, the anchor is recorded and the machine is `BELOW_ANCHOR` until it is supplied. | a currency proof for C3 within `c3_currency_window_hours` of `confirmed_at` | TA-5; TA-7 for the window |
| **In-gate state confirmation** (new) | The trust-gate confirmation of a C3 transition (`27` §3.1) also requires the operator to type the state fingerprint currently published in the channel. It must name the effective TSS. It is recorded as a human anchor. | a currency proof **for that transition only**, with no clock | TA-5 |
| **Witness** (OP-7 (c) only) | a `freshness-witness` statement (§3.3) naming the effective TSS | a currency proof while unexpired, at the C3 witness threshold | TA-7; witness custody |
| **Retained** | an anchor recorded earlier in this VTS; later verified statements raise the held state monotonically | none (safety floor only) | the VTS survives (RS-3) |

**Pin anchors are recomputed from the pin file in every process.** They are never persisted as retained anchors. A pin
therefore cannot outlive its validity through the VTS.

### 3.3 Witness authority (OP-7 (c); CD3-2 (3))

**Revision 5 (CR4-B-02, RV4-M3).** **Input:** the witness service takes the `(sequence, digest)` to witness only from the
owner's signing ceremony or the independent channel, never from the repository, a Git host, a bundle or an unauthenticated
transport. **Custody:** the C3 witness threshold is met by keys under at least two independent custodians; a ceremony record
with both keys in one service is flagged by `gov trust draft-policy`, and `21` OP-7 states the one-custody consequence.
Tests: RT-104 (i) a service whose Git host serves TSS 5 while TSS 9 is published refuses to witness TSS 5; (ii) the flag.

- **Purpose.** `freshness-witness` is a separate signing purpose (`05` §1). KS-11 forbids sharing its keys with any other
  purpose.
- **Statement.** `freshness-witness.v1+json` (schema `freshness-witness.schema.json`) names `witnessed_state {sequence,
  statement_digest}`, `issued_at` and `expires_at`. It asserts only that this TSS was the latest as of `issued_at`. It
  cannot add, remove or reorder state, because the named TSS must itself verify under `trust-state`.
- **Acceptance.** A witness is honoured only when:
  - it names the machine's effective TSS;
  - `expires_at − issued_at ≤ bootstrap.witness_max_validity_hours`;
  - `issued_at` is not later than the local clock plus the compiled skew;
  - it is not older than the newest witness this VTS has accepted.
- **Threshold.** C3 and binary acceptance require at least **two** distinct valid witness keys. This is a compiled
  minimum. The owner may register threshold 1 for the purpose; such a witness then admits C1–C2 only.
- **Compromise consequence (stated).**
  - With witness keys at the C3 threshold and control of the transport or repository, an attacker can present any
    genuine older TSS as the latest to machines that rely on witnesses. That exposes C1–C3 on stateless runners until
    the next root rotation removes the keys.
  - The attacker cannot create state or lift a negative, and machines with a satisfied pin or human anchor are
    unaffected below that anchor.
  - Below the C3 threshold, the exposure is C1–C2 only, and only where the owner registered threshold 1.
  - The trust-state key alone cannot witness (RV3-B-A06 flips: `P4r4` RV3-B-A06).

### 3.4 Anchor satisfaction (normative; CD3-2 (1))

For a set of anchors *A* (valid pins, human confirmations, retained anchors), let *H* be the resolved Trust State
Statements the machine holds. Each rule below applies to pins, human confirmations, witnesses and retained anchors
alike:

1. *A* is **satisfied** by TSS *T* ∈ *H* iff, for every `(e, d) ∈ A`:
   - `(e, d)` is held in *H*; and
   - `(e, d) = (T.sequence, digest(T))` or `(e, d) ∈ T.prior_states`.
2. **Candidates** are the TSSs in *H* that satisfy *A*. Admissibility (`17` S4 (d)) runs over the candidates together
   with the ancestors in the top anchor's chain. The effective TSS is the highest admissible candidate.
3. If there is no candidate, freshness is `BELOW_ANCHOR`. This includes the case where the anchored statement is not
   held, and the case where every higher statement fails to chain through it. No operation above C0 runs.
4. Resolved TSSs outside the anchored chain are:
   - **orphans**, when their sequence is at or below the top anchor (reported, never effective);
   - **unchained above the anchor**, otherwise.

   Unchained statements are never effective. When a candidate exists they make the trust state `REGRESSION` (C0),
   because they indicate a trust-state key compromise or equivocation.
5. Two anchors neither of whose statements chains the other → `ANCHOR_CONFLICT` (C0).

One definition serves the freshness axis, `17` S4, the pin schema and the reference model. The model's oracle
(`evidence/P4r4-trust-state-model.json`) fails when rule 1 is replaced by a sequence comparison: mutant `M-sequence-anchor` fails RV3-B-A12,
RV3-D-A12, RV3-D-A15 and the matrix.

### 3.5 Anchor and decision-pin integrity (CD3-2 (4); CR-03, RV3-M2)

1. **Pin locations** are resolved from the OS, never from `HOME`, `XDG_*`, `GOV_*` or the repository.
   - **System pin directory**: `/etc/gov/` on Linux, `/Library/Application Support/gov/` on macOS, `%ProgramData%\gov\`
     on Windows.
   - **Account location**: `<account-home>/.config/gov/`, resolved from the account database.
2. **Integrity predicate.** A pin file or decision pin file is honoured only if either:
   - neither it nor any ancestor directory is writable by the effective uid (for the account location: every ancestor up
     to and including the account home; on Windows, the equivalent ACL check); or
   - it is on a read-only mount.

   Otherwise the pin yields `PIN_WRITABLE_IGNORED` (the machine is `UNANCHORED` for that pin), and a decision pin
   authorises nothing (`TRUST_GATE_LOCAL_CONFIRMATION_REQUIRED`).
3. **Confined execution.** Every repository-supplied or plugin-supplied command that `gov` executes MUST run under OS
   write confinement. This covers product and test commands, tool install, uninstall and health commands, plugin
   processes and adapter hooks. The confinement denies writes to:
   - the system and account pin locations;
   - the Verifier Trust Store;
   - `governance/trust/**`;
   - the occupation entries;
   - the transaction area.

   Mechanisms: Linux Landlock (ABI ≥ 1) or an equivalent mount namespace; a macOS sandbox profile; a Windows restricted
   token or AppContainer. Where confinement is unavailable, `gov` refuses to run the command
   (`REPOSITORY_COMMAND_CONFINEMENT_UNAVAILABLE`). Every trust decision of a unit of work is made before any such child
   is started, and the next unit of work re-reads pins with the predicate.
4. **TA-9 restated.** Two things hold. Pins and decision pins are provisioned by an operator whom the repository writer
   does not control. No process that the repository writer controls runs, before `gov`'s trust decision, with an
   identity that can write the pin location. On CI this means a root-owned `/etc/gov` in the runner image and a job that
   runs as another user. A CI job whose repository-controlled steps run as root before `gov` is not a governance boundary
   against that writer, whatever the design (RS-4).
5. **The rule of `27` §3.3** covers the `gov decide` path and every `gov`-executed child. An agent with an unconfined shell
   in the same account is A3 (RS-3, TG-2).

Evidence:
- RV3-B-A03 re-run on the real 4.1.5 binary (`evidence/rerun-RV3-B-A03-A14-A16-probes.json`): the pin written by the
  `gov verify product` child is owned by the effective uid with mode 0644, so under the predicate it is ignored.
- `P4r4` RV3-B-A03 and RV3-B-A04: a writable pin yields `UNANCHORED`; a writable decision pin authorises no kind; a
  protected pin never approves `local_terminal_only` kinds.

### 3.6 Not anchors

The following are never anchors:
- the repository (PTR, lock hints, gate records);
- bundles;
- `gov trust refresh` input;
- environment variables and CLI flags;
- CI configuration committed to the repository;
- the compiled T0;
- a VTS record of a pin.

The compiled T0 is a safety floor. Only OP-7 (d) accepts it for governed use, and never for trust ingress.

## 4. Verdict axes, operation classes and the decision rule

### 4.1 Axes

| Axis | Values |
|---|---|
| `trust_state` (`17` S9) | `KNOWN(n)` · `INCOMPLETE(n′)` · `REGRESSION` (including unchained statements above an anchor) · `EQUIVOCATION` |
| `freshness` | `ANCHORED(e, method, as-of t, age)` · `BELOW_ANCHOR(anchored (e, d) not in the effective chain)` · `UNANCHORED(held n)` · `UNANCHORED(FRESHNESS_UNPROVEN)` (OP-7 (d)) · `WITNESSED(n, k signers, expires)` (OP-7 (c)) · `ANCHOR_CONFLICT` |
| `currency` (new) | `CURRENCY(proof, established t)` · `CURRENCY_UNPROVEN(age of the last proof)` |

- Every surface (`gov status`, `gov kernel trust`, context packets, doctor D032/D035, gate text) MUST show all three
  axes.
- **The word `current` MUST NOT appear on any surface.** A proof is shown as "state published as of *t*", never as
  "current".
- The OP-5 age is measured from the anchor time. The age warning is always shown when the machine is `UNANCHORED` or
  `CURRENCY_UNPROVEN`.

### 4.2 Operation classes (compiled command register)

| Class | Commands (examples) |
|---|---|
| **C0** diagnostics and knowledge intake | `version`, `doctor`, `status` (without policy-dependent sections), `kernel verify`/`trust`, `trust show`, `trust refresh --from`, `trust confirm-root`/`confirm-state`, trust-gate confirmation (`27`) |
| **C1** governed read | `context compile`, `memory query`, `continue`, readiness views |
| **C2** governed mutation | tasks, CIT, non-trust gates, `rebuild-memory`, `plugins register`, `tools install`, adoption batches ≥ 1, `upstream`, checkpoints |
| **C3** trust ingress | `init`, `adopt migrate --batch 0`, `update --apply`, rollback and restore, `kernel reinstall` with another envelope, recovery exchange, **`trust verify-artifact` acceptance**, profile install, lineage adoption |

### 4.3 Decision rule (one rule; the most restrictive applicable row wins; CR-05, RV3-L1)

| Condition | C0 | C1 | C2 | C3 |
|---|---|---|---|---|
| `EQUIVOCATION`, `REGRESSION`, `BELOW_ANCHOR`, `ANCHOR_CONFLICT` | yes | no | no | no |
| `INCOMPLETE` (any option, any anchor) | yes | yes | **no** | no |
| `UNANCHORED` under OP-7 (a) or (b) | yes | no | no | no |
| `UNANCHORED` under OP-7 (c), no witness honoured | yes | no | no | no |
| `WITNESSED` under OP-7 (c), below the C3 witness threshold | yes | yes | yes | no |
| `WITNESSED` under OP-7 (c), at the C3 witness threshold | yes | yes | yes | yes |
| `UNANCHORED` under OP-7 (d) | yes | yes, labelled `FRESHNESS_UNPROVEN` | yes, labelled | no (architecture minimum) |
| `ANCHORED`, `KNOWN`, OP-7 (b), latest anchoring event older than `max_anchor_age_days` | yes | yes | **no** | no |
| `ANCHORED`, `KNOWN`, otherwise | yes | yes | yes | **only with a currency proof** (§4.4) |

**Under OP-7 (c), a non-witness anchor follows the (a) rows.** C2 is allowed at any anchor age, and C3 needs a currency
proof. `§5.7` states the same rule.

**Refusal codes:**

| Code | Condition |
|---|---|
| `TRUST_STATE_UNANCHORED` | the machine has no honoured anchor |
| `TRUST_STATE_BELOW_ANCHOR` | the anchored statement is not in the effective chain |
| `TRUST_STATE_CURRENCY_UNPROVEN` (new) | C3 or binary acceptance without a currency proof |
| `TRUST_STATE_EQUIVOCATION` | as `17` S4 |
| `TRUST_STATE_REGRESSION` | as `17` S4 |
| `TRUST_STATE_INCOMPLETE` | as `17` S4 |
| `TRUST_ANCHOR_EXPIRED` | an anchor past its age limit |
| `PIN_OUTSIDE_VALIDITY` (new) | a pin outside `[provisioned_at, valid_until]` |
| `PIN_WRITABLE_IGNORED` (new) | a pin that fails the integrity predicate |
| `ANCHOR_CONFLICT` (new) | two anchors on different chains |

Each code carries `required`, `held` and `remedy` (refresh, confirm-state, re-provision the pin, supply a witness, or
upgrade).

### 4.4 Currency proof (normative; CD3-2 (2))

A **currency proof** for effective TSS *n* exists iff the machine is `KNOWN`, is `ANCHORED` or (OP-7 (c)) `WITNESSED` at the
C3 witness threshold (CR4-B-06: the §4.3 row and this definition now agree), the local clock passes the rollback check (§8),
and one of these holds:

| Proof | Condition | Clock |
|---|---|---|
| (P1) recent anchoring event **naming *n*** (revision 5) | a pin provisioning or human confirmation **whose anchored statement is *n* itself** is no older than `bootstrap.c3_currency_window_hours`; an anchoring event naming an ancestor of *n* is not a proof for *n* (CR4-B-07 option 1) | TA-7 |
| (P2) in-gate confirmation | the trust-gate confirmation for this transition carries a typed fingerprint equal to `(n, digest(n))` | none |
| (P3) witnesses | witnesses on *n* at the C3 threshold (§3.3) | TA-7 |

A proof establishes that *n* was the published state **as of** the proof time. It is used for exactly one C3 decision,
or for the window. It is never displayed as `current`.

**Evidence.** `evidence/P4r4-trust-state-model.json` has 54 scenarios (all hold) and a conformance oracle that kills each
of 9 single-rule mutants. The mutants re-introduce the review r3 defects: sequence anchors, unbounded pins, a threshold-1
trust-state witness, C3 without a currency proof, writable pins, A7 against the TSS high-water, source taken from
`release_commit`, lift with a pre-negative attestation, and any `issued_at` raising the clock.

## 5. The machine list (HO-0001 §3.2)

"Local state" means the VTS (§8). Scenario ids refer to `evidence/P4r4-trust-state-model.json`. The assumed parameters
are proposals only:
- `pin_max_validity_days` 30;
- `c3_currency_window_hours` 168;
- `max_anchor_age_days` 180;
- `witness_max_validity_hours` 168;
- witness C3 threshold 2.

### 5.1 First install (M1)

- **Starting state.** An empty VTS.
- **Safe without freshness.** C0: verify the bundle, show both fingerprints, `trust refresh`.
- **Gated or read-only.** C1–C3 refuse (`TRUST_STATE_UNANCHORED`).
- **Anchor and currency.**
  - The human confirms the root (OP-6), then the state fingerprint. When the bundle holds that TSS, the machine is
    `ANCHORED` with a currency proof (P1), and `init` proceeds through its trust gate.
  - If the source withholds the confirmed TSS, or supplies only statements that do not chain through it, the machine is
    `BELOW_ANCHOR` (inclusion). One stolen trust-state key presenting a higher unchained TSS changes nothing
    (RV3-B-A12 flips).
- **Persisted.** Lineage confirmation, the human anchor, verified statements, the per-project record.
- **OP-7 effect.** None on C3. Under (c), witnesses at the C3 threshold can serve instead of a human.
- **Evidence.** `M1_first_install`; `RV3-B-A12_RV3-D-A12_higher_unchained_tss`.

### 5.2 Clean CI runner (M2)

- **Starting state.** An empty VTS on every run.
- **Safe without freshness.** C0.
- **Anchor.** A pin in the root-owned system pin directory of the runner image (§3.5), valid for at most
  `pin_max_validity_days`. The image must be re-provisioned within that period.
- **Behaviour.**

  | Condition | Result |
  |---|---|
  | valid pin, intact repository | `ANCHORED`; C2. C3 (including `verify-artifact`) only while the pin is younger than the C3 window |
  | valid pin, stripped repository | `BELOW_ANCHOR` |
  | pin outside its validity (for example an image pinned 100 or 400 days earlier) | not an anchor: `UNANCHORED` (RV3-B-A02 flips under (a)–(c)) |
  | pin writable by the job's uid | ignored (RV3-B-A03 flips) |
  | OP-7 (c), no pin | witnesses at threshold admit C1–C3; one of two witness keys admits nothing |
  | OP-7 (d), no pin | C1–C2 labelled `FRESHNESS_UNPROVEN`; C3 never |

- **Persisted.** Nothing beyond the run.
- **OP-7 effect.** As the table. The (d) residual exposes binaries whose compiled TSS predates the newest TSS (RV3-L6;
  §9).
- **Evidence.** `M2_clean_ci_runner`, `RV3-B-A02_stale_ci_pin`, `RV3-B-A03_pin_written_by_governed_account`,
  `PIN_WINDOW_bound`, `RV3-D-A15_revoked_binary_pinned_ci`.

### 5.3 Machine restored from backup (M3)

- **Starting state.** A VTS rolled back to a human anchor at t5, 400 days old; the published state is t10.
- **Safe.** Never below t5.
- **Gated.**
  - C3 refuses without a fresh proof.
  - Under (b), C2 refuses past `max_anchor_age_days`.
  - Under (a), (c) and (d), C2 runs at the anchored chain, labelled `ANCHORED(5, human, as-of …, age 400d)
    CURRENCY_UNPROVEN`.
- **Remedy.** `confirm-state` of the current fingerprint (P1), or an in-gate confirmation (P2).
- **Evidence.** `M3_restored_from_backup`.

### 5.4 Machine with an old trust epoch (M4)

- **Behaviour.** Anchored at t5, 20 days ago.
- **Result.**
  - The effective state is never below t5.
  - C2 runs at the anchored chain.
  - C3 refuses without a proof in the window: 20 days exceeds the proposed 7-day window.
- **Evidence.** `M4_old_epoch`.

### 5.5 Machine with no trust epoch (M5)

- **Behaviour.** `UNANCHORED`. C3 never. C1–C2 only under (d), labelled, or under (c) with witnesses.
- **Evidence.** `M5_no_epoch`.

### 5.6 Two machines at different epochs (M6)

- **Behaviour.**
  - Each machine enforces its own anchor by inclusion.
  - B learns t10 when the PTR carries it, because t10 chains through B's anchor t5.
  - A never accepts a statement that does not descend from t10.
  - Lock hints are warnings.
- **Evidence.** `M6_two_machines`.

### 5.7 Offline machine after a long absence (M7)

- **Behaviour.** Anchored at t5, 1095 days ago.
  - Under (a), (c) and (d): C2 at the anchored chain, with the age shown. This is the honest limit (RS-1).
  - Under (b): C2 refuses.
  - Under every option: C3 refuses without a proof. Under (c), a non-witness anchor follows (a), as §4.3 states.
- **In-gate confirmation.** Typing the currently published fingerprint into the gate is a clockless proof, but only if
  the machine holds that TSS.
- **Evidence.** `M7_offline_long_absence`, `INGATE_state_fingerprint_currency`.

## 6. Replay, equivocation, forks and incomplete state

| Case | Rule | Evidence |
|---|---|---|
| Replay of genuine older TSS or TPS | Knowledge is a union; replay lowers nothing | `R1_signed_state_replay` |
| Replay of an older witness | accepted only by a verifier that never saw a newer one, and only within its validity | `R2_witness_replay` |
| Same-sequence fork | `EQUIVOCATION`, C0 only | `B3_same_sequence_fork` |
| Fork across a gap | cumulative `prior_states[]`; `REGRESSION` | `E1_fork_across_a_gap` |
| Fork with an anchor | outside the anchored chain: orphans, reported, never effective | `E3_fork_without_and_with_anchor` |
| Higher TSS that does not chain through the anchor | not a candidate: `BELOW_ANCHOR` when the anchored statement is not held; `REGRESSION` (freeze) when it is | `RV3-B-A12_RV3-D-A12_higher_unchained_tss` |
| Pin names a digest the effective chain does not contain | `BELOW_ANCHOR` (C0) | `R5_pin_digest_mismatch` |
| TSS referencing an unknown root or policy | unresolved; `INCOMPLETE` above the effective sequence (C0–C1 only) | `B4_unresolvable_references` |
| References in release, candidate or certification statements | release-local (`17` S7) | `B1_candidate_reference_inflation` |

**Trust-state key blast radius** (corrects revision 3 `17` §15 and `05` §1; CD3-2 (5)):
- **On a machine with a satisfied anchor.** A thief's statement either descends from the anchor or is never effective.
  - A descendant that omits a revocation the machine holds is non-admissible, so `REGRESSION` (freeze)
    (`TS_KEY_BLAST_RADIUS`).
  - A descendant on a machine that never held the revocation admits what withholding already admits: the stated core
    (RS-1).
- **On a stateless machine.**
  - Under (a)–(c), the thief can do nothing beyond a freeze. It cannot witness (§3.3).
  - Under (d), it can publish a descendant of the compiled T0. That equals the (d) residual and is never C3.
- **What it can never do.** Lift a negative, create certification, accept a binary (`25` §7 routes), or make a
  statement effective that does not descend from an anchor.

## 7. Gate records supplied from repository state

Unchanged. A repository gate record never authorises a trust decision (`27`). Review r2 evidence `P2` and `P4r4`
`R3_gate_record_from_repository` flip.

## 8. Monotonic local state (Verifier Trust Store)

**Revision 5 clock rule (RV4-M4, CR4-B-03).** SV-11 refuses statements issued in the future at ingest, so on a machine with a
verifier trust store **every ingested verified non-future statement raises `clock_high_water`** (not only witnesses). A local
clock below the high-water fails closed: pins and the C3 window are not honoured (`CLOCK_BELOW_HIGH_WATER`). A root-signed
`bootstrap.clock_reset` lowers it. On a machine without a verifier trust store there is no high-water (RS-2). Evidence: P4r5
`CLOCK-RV4-B-A13_stateful_machine_clock_set_back` (refused); DA03r5 mutant `R5-clock-high-water` (witness-only) detected.

**Revision 5 accepted-TBM rule (CR4-B-08).** Only a `build: release` binary whose TBM resolves records into `accepted_tbm`;
`bootstrap.accepted_tbm_reset` resets it (`25` §5).

**Location:** `<account-home>/.local/state/gov/trust/<trust_root_id>/`, resolved from the account database.

| Record | Content | Rule |
|---|---|---|
| `statements/` | every verified statement | union; A3 can delete (RS-3) |
| `high-water.json` | root version and digest; TPS version and digest; TSS sequence and digest; **`accepted_tbm {root, policy, state}`** (the highest Trust Base Manifest accepted by `verify-artifact` or by the first run of a verified binary; `25` A7); **`clock_high_water`**; `highest_witness_issued_at` | components never decrease, except by a root-signed clock reset |
| `anchors.json` | human, in-gate and retained anchors: `(sequence, digest)`, method, `anchored_at`, operator, fingerprint | never decreases; **pin anchors are not stored here** |
| `lineage.json` | OP-6 confirmation | — |
| `projects/<project_trust_id>.json` | repository paths, highest installed sequence and CI, project-strength vector (`26` §6), **held Trust Policy registration** (`19` §10.6), open transactions, adapter rendering digests | raised only by install transactions or gated confirmation |
| `confirmations/` | trust-gate confirmations (`27`) | append-only |

**Clock high-water (CR-06, RV3-M3).**
- Only verified `freshness-witness` statements raise `clock_high_water`.
- A statement of any purpose whose `issued_at` exceeds the local clock by more than the compiled skew (300 seconds) is
  refused at ingest (`STATEMENT_ISSUED_IN_FUTURE`) and never recorded.
- A root-signed TPS field `bootstrap.clock_reset {reset_to, reason}` lowers the high-water after a witness-key
  compromise.
- Evidence: `P4r4` `RV3-B-A07_issued_at_high_water`.

## 9. OP-7 (presented in `21`; not decided here)

Architecture minima, not owner-selectable:
- inclusion anchors (§3.4);
- no C3 or binary acceptance without a currency proof (§4.4);
- mandatory pin validity (§3.2);
- the separate witness purpose, with a compiled C3 threshold of at least 2 (§3.3);
- pin and decision-pin integrity with confined execution (§3.5);
- no `current` label (§4.1).

| Option | Unanchored machine | Anchored machine | Clock | Who can select which state, and for how long |
|---|---|---|---|---|
| **(a) anchored only** | C0 | C1–C2 at any age of a human or retained anchor; pins only within validity; C3 only with a currency proof | TA-7 for pins and the C3 window; none for human anchors and in-gate proofs | **A2/A5**: any genuine descendant of the anchor, for C1–C2, on a machine whose anchor predates a revocation. That lasts as long as the machine holds no later statement (human anchors), or at most `pin_max_validity_days` (pins). For C3: at most `c3_currency_window_hours` of staleness, or none with an in-gate proof. |
| **(b) anchored with maximum age** | C0 | as (a), but C2 refused once the latest anchoring event is older than `max_anchor_age_days` | TA-7 | as (a), with the C1–C2 exposure bounded by `max_anchor_age_days` on every machine |
| **(c) expiring witnesses** | C1–C2 with a witness at the purpose threshold; C3 with witnesses at the C3 threshold (≥ 2) | as (a), plus witnesses | TA-7; scheduled witness custody | as (a) on anchored machines. On stateless machines: A2/A5 within `witness_max_validity_hours` of the newest honest witness. A thief of witness keys at the C3 threshold selects any genuine older TSS for C1–C3 until root rotation; at threshold 1 (if registered), for C1–C2. |
| **(d) compiled epoch accepted for use** | C1–C2 labelled `FRESHNESS_UNPROVEN`; C3 never | as (a) | none added | **A2/A5**: any genuine state at or above the running binary's **compiled TSS**, for C1–C2 on unanchored machines, indefinitely. The exposure covers every binary whose compiled TSS predates the newest TSS, not only binaries older than the newest TPS (RV3-L6; `P4r4` `RV3-D-A04_op7_d_scope`). |

**Parameters** (all in the root-signed TPS `bootstrap` block, all raised or lowered only through computed reductions,
`19` §10.6):
- `op7_mode`;
- `pin_max_validity_days`;
- `c3_currency_window_hours`;
- `max_anchor_age_days`;
- `witness_max_validity_hours`;
- `freshness_witness_threshold`;
- `clock_reset`.

**Proposal (labelled, not a decision): (a), with `pin_max_validity_days` 30, `c3_currency_window_hours` 168 and a
witness threshold of 2 if (c) is ever chosen.** (a) adds a clock only for pinned machines and C3 windows. It removes the
stale-pin, unchained-TSS and minted-witness classes on every machine. The cost is operational: CI pins must be
re-provisioned at least every 30 days, and C3 on long-idle machines needs a fresh confirmation.

## 10. Residuals, restated exactly

**Revision 5 restatements.**
- **RS-2 (CR4-B-03).** Under OP-7 (a), (b) and (d), and on any machine without a verifier trust store, a clock set back is not
  detected: pin validity and the C3 window rest entirely on TA-7, so an expired pin becomes valid and yields a P1 proof for the
  TSS it names (P4r5 residual demonstration on a stateless runner). On machines with a verifier trust store, a clock set back
  below the high-water fails closed (§8). Test: RT-56 with RV4-B-A13 on a clean runner and on a stateful machine.
- **RS-1b (CR4-B-07).** A P1 proof covers only the anchored statement; C3 on a later descendant needs P2 or P3, so the label
  "published as of *t*" is exact. Test: RT-101 with RV4-B-A12 (i).
- **RS-5 (CR4-B-02).** The key-compromise bound holds with the witness input and custody rules of §3.3.

| ID | Residual | Bound | Test that fails if exceeded |
|---|---|---|---|
| RS-1 | **Core.** A machine anchored before a revocation that never receives later metadata cannot know about the revocation. | C1–C2 at any genuine descendant of its anchor. Shown as `ANCHORED(e, method, as-of t, age) CURRENCY_UNPROVEN`, never `current`. Never C3 without a proof. Under (b), bounded by `max_anchor_age_days`. | `12` RT-80, RT-101; `P4r4` matrix: rows admitting revoked R7 are only the stated core and the (d) residual |
| RS-1b | A C3 decision whose proof is a recent anchoring event (P1) or a witness (P3) can be stale by up to the window. | `c3_currency_window_hours` (P1) or `witness_max_validity_hours` (P3); zero for an in-gate proof (P2) | RT-101 (c), RT-102 |
| RS-1c | A valid pin provisioned before a revocation admits the stale descendant for C1–C2. | `pin_max_validity_days` | `P4r4` `PIN_WINDOW_bound`; RT-102 |
| RS-2 | Pin validity, the C3 window and OP-7 (b)/(c) trust the local clock (TA-7). | Clock rollback below `clock_high_water` makes clock-based proofs and pins unusable (fail closed). Only witnesses raise the high-water. Far-future statements are refused. A root-signed reset exists. | RT-56, RT-98 |
| RS-3 | A3 deletes or rewrites its own VTS. | Deletion leaves the machine `UNANCHORED` (fail closed). A3 can forge a human anchor or confirmation in its own VTS (same-user boundary). Pins and decision pins are outside A3's reach under the predicate, and `gov`-run children are confined. | RT-91, RT-103 |
| RS-4 | A pin provisioned by a party the repository writer controls, or a CI job that runs repository-controlled steps as a user who can write the pin location before `gov`. | Outside TA-9 as restated (§3.5). | procedural; RT-103 (d) |
| RS-5 | Compromise of freshness-witness keys (OP-7 (c) only). | §3.3: stale selection on witness-reliant machines until root rotation; no state creation | RT-98, RT-104 |
