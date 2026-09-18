# Phase 1 — residual later-lifecycle risks carried past `ROT_PHASE1_CANDIDATE_ACCEPTED_R1`

| Field | Value |
|---|---|
| Accepted candidate | `srr1-r1-candidate-4` |
| Accepting run | AR-0033 (`verifier-d`), verdict `ROT_PHASE1_CANDIDATE_ACCEPTED_R1`, 0 blocking findings |
| Purpose | Every condition that did **not** block R1 but must not be silently lost. Recorded separately from the acceptance so a later gate inherits them explicitly. |
| Status of all items below | **non-blocking at R1**; none was a materially new blocker class; none requires an owner decision |

## 1. The assurance gap the accepted candidate knowingly carries

R1 accepts a §6 enforcement mechanism whose coverage is **derived from the product** rather than hand-enumerated — a
genuine class control, proven non-vacuous: graded against the **pre-repair** source with the candidate's own
signatures, it flags exactly three violations (the latent bullet-6 primitive, `AR31-B1` and `AR31-N1`), i.e. it would
have failed the suite on candidate 3 and independently rediscovered a HIGH finding that cost a human verifier a full
iteration.

It is nonetheless **a narrow syntactic detector, not a decision procedure**, and the accepted candidate says so. The
three items below are the honest statement of that gap. They are the highest-value assurance work for R2.

| id | lifecycle | severity | condition |
|---|---|---|---|
| `AR33-N1` | R2 | MEDIUM | The derived census is a narrow detector: **nine of nine** plausible future primitives the verifier wrote evade it — a gate approval spelled as a literal or named constant, a hand-built path, a differently-spelled status field, a computed role-file name, a computed registry directory, the repair's own worked bullet-6 example, a new in-process reporting surface, and a new serve mode. Three of seven positive controls are cosmetic (written around the literal, or a verbatim copy of the existing implementation with enforcement removed), so the controls establish **non-vacuity, not coverage**. |
| `AR33-N2` | R2 | MEDIUM | **Highest-value hardening.** Acceptance markers accept unenforced implementations: for bullet 2, `save_record(` is both signature and acceptance marker, so a function derived through it is accepted by the same string. The product **held that exact shape one commit ago** — `cit::apply_op` was accepted purely by the marker while a sibling branch wrote a governed record path with `write_text`. The instance is closed, but by reading, not by the mechanism firing. Recommended fix, from the verifier: a **negative control per acceptance set** — an implementation carrying the marker but not the enforcement, which the suite must still flag. |
| `AR33-N3` | R2 | LOW | Bullet 7's universality is a property of the **CLI envelope**, not the library. `gov capabilities serve-embed` prints and calls `std::process::exit(0)` from inside `run()`, so its output carries no `release_trust`. Not a §6 breach — it reports a provider protocol version, not the installed release, and makes no currency claim — but a future in-process reporting surface would not inherit the marking. |

## 2. Accuracy corrections to the accepted candidate's own self-description

| id | lifecycle | severity | condition |
|---|---|---|---|
| `AR33-N4` | R1 | LOW | Two claims about the bullet-7 mechanism's reach are **false as written**: that `run()`'s value reaches stdout *only* through the match, and `DERIVATION.md` limit 10's "the derivation finds them". Both non-result print sites live in `cli/src/main.rs::run`, which matches neither bullet-7 signature marker. No §6 consequence; the substance is disclosed in limit 10. |
| `AR33-N5` | R1 | LOW | `cargo fmt --check` **fails** (57 hunks, 8 files), so `DERIVATION.md` limit 5's stated mitigation — that the tree is rustfmt-canonical — is absent. Measured consequence: the verifier's brace-counting splitter and the candidate's disagree on **one** function body tree-wide (`util.rs::glob_to_regex`), and **no §6 verdict changes**. |

## 3. Test-assurance placement

| id | lifecycle | severity | condition |
|---|---|---|---|
| `AR33-N6` | R2 | LOW | A **second** held-out check has migrated into the implementer's own suite (`AR31-N4` restored in `tests/certification/section6.rs`). The verifier reproduced both properties independently and confirmed the migration did not weaken them, but the pattern — verifier-authored evidence becoming implementer-maintained — is worth a policy at R2. |
| `AR33-N7` | R2 | LOW | `gov continue` is affected by the reported `gov gate present` behaviour change and was not reported alongside it. |

## 4. Carried from earlier iterations, not re-examined at R1

| id | lifecycle | condition |
|---|---|---|
| `AR31-N6` | R2 | `status::continue_work` drops the `release_trust` block its own callee computes. *(Operator-facing half now closed via the envelope; noted ungraded by AR-0033.)* |
| `AR29-N2` | R2 | The canonical expiry gate is syntactic, not calendrical. |
| `AR27-N3` | R2 | `timestamp.json` and `snapshot.json` are optional, so TUF freeze-attack controls can be dropped by omission. Release expiry and metadata high-water still bind. |
| `AR27-N5` | R2 | A `minimum_secure_release` published without `minimum_secure_sequence` never raises the floor. |
| `AR27-N6` | R2 | `guard_acquisition` receives a hard-coded empty delegation slice, so verified-metadata delegations are never consulted (fail-closed). |
| `AR27-N7` | R2 | Capability evidence-map rows are all `NOT_YET_MAPPED` — honestly declared, an R2 obligation. |
| `SRR-R0-L9` | R2 | `release/targets` threshold value and custody unspecified — correctly deferred at R0. |
| `SRR-R0-L8` | INFO | The R0 traceability table maps 11 of 14 frozen R0 items. |

## 5. Owner-closed — recorded so they are not silently reopened

| id | record | disposition |
|---|---|---|
| `SRR-R0-L6` | `OWNER-DECISION-0005` | Plugin/tool acquisition authenticity deferred to R1 and **closed there**; the built-in vs remotely-acquired distinction is implemented and enforced. |
| `SRR-R0-L7` | `OWNER-DECISION-0005` | Offline/air-gapped **first install** is out of scope for the private/local profile. Break-glass *recovery* works with no network, verified at every iteration. |
| `AR27-OD1` | `OWNER-DECISION-0007` §1 | Protected machine state keeps its `XDG_STATE_HOME`/`HOME` derivation. The relocation asymmetry is an owner-adjudicated position, not a defect. |
| `SRR2-R1-C1` | `OWNER-DECISION-0007` §2 | Break-glass exit requires a release at or above **both** the signed minimum secure release and the protected local high-water. Owner policy, not an interim. |

## 6. Not carried

Nothing from R0 is carried: `GATE-R0-ARCH-ACCEPT` is satisfied and no R1 finding required reopening it. No item in this
register is an R2 *certification* claim, an R3 high-assurance criterion, or a Phase-2 obligation; those gates define
their own requirements and inherit this register as input, not as a substitute.
