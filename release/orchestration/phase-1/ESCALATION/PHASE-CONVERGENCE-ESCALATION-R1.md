# `PHASE_CONVERGENCE_ESCALATION_REQUIRED` — R1 root-cause / meta-review package

| Field | Value |
|---|---|
| Raised by | orchestrator, after R1 verification iteration 3 |
| Date | 2026-09-18 |
| Phase | 1, gate `GATE-R1-CANDIDATE-ACCEPT` (**not** satisfied) |
| Current candidate | `srr1-r1-candidate-3` — **not accepted, not certified, not released** |
| R0 status | `ROT_ARCHITECTURE_ACCEPTED_R0` stands. **Nothing here reopens R0.** |
| Owner decision required | **Yes** — which of the options in §6 to take |
| Owner decisions still in force | `OWNER-DIRECTIVE-0004`, `OWNER-DECISION-0005`, `-0006`, `-0007` — all unchanged |

## 1. Why you are being interrupted

Three R1 verification iterations have each produced at least one blocking finding, and each has surfaced a blocker
class the previous iteration did not see. The orchestrator committed, before this iteration ran, to stopping and
producing this package if a third materially new class appeared rather than spending another repair cycle. AR-0031
labelled one of its two blockers a materially new class. That commitment is therefore honoured here.

**This is a decision point, not a failure report.** The convergence evidence is genuinely mixed and the orchestrator
will not resolve it on your behalf. §5 states the case for continuing and the case for concern, in that order.

## 2. What each iteration found

| # | Verifier | Candidate | Blocker class | Essence |
|---|---|---|---|---|
| 1 | AR-0027 | 1 | **BC-R1-1 — guard decision** | `OWNER-DECISION-0006` §6 bullet 1 was enforced as a 26-string substring **deny-list**, so any unlisted operation proceeded below floor. Seven privileged governed operations did. |
| 2 | AR-0029 | 2 | **BC-R1-2 — guard coverage** | The decision procedure was then correct and unbreakable (63 near-miss forms, zero permitted) — but two privileged operations **reached no guard at all**. `provision::root_update` mutated trust policy below floor; `gates::create_system` created Human Gates unguarded. |
| 3 | AR-0031 | 3 | **BC-R1-3 — undetermined-subject fail-open** (materially new) + **residual of BC-R1-2** | The sink census closed bullets 2, 3, 4 and 6. Two gaps remain: `AR31-B1` (HIGH, **residual**) — §6 bullet 7 is enforced **nowhere**, its effect has no call site outside `breakglass.rs`, and the excusing claim that every reporting surface carries the marking is false (`gov doctor` holds zero references to it; `gov update --check` reports a below-floor release as up to date). `AR31-B2` (MEDIUM, **materially new**) — both enforcement points convert a state-root resolution error into a clearance, so one environment variable makes all eight §6 effects return `Ok` on a genuinely marked machine. |

Each repair closed what it was given. BC-R1-1 was closed completely and has never regressed. BC-R1-2 is closed for
four of six bullets, with the strongest sink (bullet 4, the only writer of `trust/root.json`) verified as complete.

## 3. The shared root cause

**`OWNER-DECISION-0006` §6 is a universal negative — "below-floor recovery MUST NOT permit X" — and it has been
implemented three times as a positive enumeration, at successively deeper levels.**

| level | the enumeration | how it failed |
|---|---|---|
| 1 | the list of **forbidden operations** | anything unlisted was permitted |
| 2 | the set of **guarded call sites** | anything reaching no call site was unenforced |
| 3 | the census of **effect primitives** (`SECTION_6_SINKS`) | a bullet whose primitive was asserted not to exist is enforced nowhere |

Every one of those enumerations was complete and correct on the day it was written. Each became silently incomplete the
moment the product grew a path its author had not enumerated. That is the defining property of an enumeration standing
in for a universal.

**The second half of the root cause is why the tests did not catch it.** At each level the test checked the
enumeration against itself rather than against the property. AR-0027's sweep pushed operation *labels* through the
guard — eight of those labels have no call site in the product, so refusing a label proved nothing about an operation.
AR-0031 found the same shape one level down (`AR31-N5`): the census test's loop **skips the bullets whose entry says
"no primitive"**, so bullets 6 and 7 are unfalsifiable by the candidate's own suite. A test derived from the same
enumeration as the code cannot detect that the enumeration is short.

This is a design-pattern defect, not carelessness. Each repair was a correct and well-argued response to the finding it
was handed, and each was independently confirmed to have closed it.

## 4. What is actually left

Both remaining blockers are **local, bounded, and need no owner decision and no boundary change**:

- **`AR31-B2`** — two `let … else { return Ok(…) }` blocks in `breakglass.rs` failing closed instead of open. The
  verifier enumerated every input to that branch: the unprovisioned case the code's own comment names **never reaches
  it**, and the only input that does is `GOV_MACHINE_STATE_DIR` pointing elsewhere on a provisioned machine — which the
  product already refuses. Failing closed therefore costs nothing. The repair had characterised this as requiring the
  owner-closed machine-state change; the verifier showed both limbs of that reasoning are wrong, and the orchestrator
  confirmed the branches are in `breakglass.rs` alone, with `resolve_state_root` byte-identical throughout.
- **`AR31-B1`** — bullet 7 needs either a primitive, or the "every reporting surface carries the marking" claim made
  true **and testable**. The existing census test cannot fail on it, which is how the gap survived.

## 5. The evidence, both ways

**For continuing (convergence is real):**

- Each iteration closed its assigned class; none regressed. BC-R1-1 has held through two further repairs.
- Scope is shrinking sharply: iteration 1 needed the control's shape rethought, iteration 2 needed a new enforcement
  layer, iteration 3 needs two lines and one claim made testable.
- `AR31-B2` was **disclosed by repair 2 itself** and deliberately routed for adjudication. It is inherited from repair
  1, was present and visible in candidates 1 and 2, and was simply not raised by AR-0029. It is a **known defect
  reaching first adjudication, not a new depth this repair's work uncovered.**
- Neither blocker needs an owner decision, a boundary change, or any R0 rework.
- Everything else is holding: all twelve frozen R1 items (item 9 qualified by `AR31-B2` alone), the four-operation
  allow-list, 5 `admit` / 5 `install_kernel`, floors at six ingresses, D-0007 separation, Contract v3 byte-identical,
  36 lib + 70 certification tests passing, independently reproduced by the orchestrator at every candidate.

**For concern (why this was escalated anyway):**

- Three iterations, three classes. The pattern the escalation rule exists to catch is precisely "each fix is correct
  and a new class appears underneath it".
- The root cause in §3 is **not** addressed by fixing the two remaining blockers. A fourth enumeration could go short
  the same way. Bullet 5 already has a second primitive (`tools::install`) that the census does not name — non-blocking
  today only because the operation-level allow-list happens to refuse it.
- Two prior verifiers independently asserted properties stronger than the code held: "no public constructor"
  (`AR29-N1`, since fixed by sealing) and "every reporting surface carries the marking" (`AR31-B1`, false). The
  orchestrator repeated the first of those to the product owner before it was corrected. Confident claims about
  universal properties have been wrong more than once in this lineage.

## 6. Your options

**A — One more bounded repair, instances only.** Fix `AR31-B1` and `AR31-B2` plus `AR31-N1`/`N3`/`N4`, then a fresh
verifier. Smallest change, fastest path. Leaves the §3 root cause in place.

**B — One more bounded repair, with a structural mandate (orchestrator's recommendation).** The same two blockers,
*plus* an explicit requirement that the §6 property stop depending on an enumeration being complete: make the
enumeration **derived from the product rather than asserted alongside it**, and make the census test able to fail on a
bullet that claims no primitive. Slightly larger, addresses the pattern that produced all three classes. Still no owner
decision and no boundary change.

**C — Re-scope R1.** Accept the candidate with §6 bullets 1, 2, 3, 4 and 6 enforced, and bullets 5 and 7 recorded as
R2 obligations. **This needs your decision**, because it changes what `OWNER-DECISION-0006` §6 requires at R1. The
orchestrator does not recommend it while bullet 7 is unenforced: a below-floor machine currently reports itself as up
to date, which is the one thing §6 bullet 7 names.

**D — Pause R1 and re-examine the architecture.** Not indicated on the evidence. R0 is sound and independently
accepted, the trust chain and metadata model are uncontested, and every finding has been an implementation defect
inside the accepted boundary.

**Orchestrator's recommendation: B.** The two blockers are genuinely small, and the structural mandate is the only
option that makes a fourth iteration of the same shape unlikely. If you choose B, the loop continues automatically as
before and you will next hear from the orchestrator at R1 acceptance or at the next genuine decision point.

## 7. State at the point of stopping

Nothing is accepted. `GATE-R1-CANDIDATE-ACCEPT` remains OPEN, `GATE-PHASE1-COMPLETE` NOT_OPEN, and no release,
certification or merge to `main` has occurred. All evidence for all three iterations is committed and immutable.
`ROT_ARCHITECTURE_ACCEPTED_R0` is unaffected. The orchestrator has issued no verdict of its own at any point.
