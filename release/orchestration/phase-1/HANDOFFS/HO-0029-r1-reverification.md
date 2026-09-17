# HO-0029 — Handoff for the fresh independent R1 re-verification (candidate 2)

| Field | Value |
|---|---|
| Handoff | HO-0029 |
| From | orchestrator (routing only) |
| To | NEW fresh independent R1 verifier / test author (not AR-0027) |
| Candidate | `srr1-r1-candidate-2` (repair work commit `4c7c40c`) |
| Prior verdict | AR-0027 `BLOCKING_FINDINGS_PRESENT` on candidate 1 |
| Repair run | AR-0028 `READY_FOR_INDEPENDENT_OS_VERIFICATION`, repair cycle 1 |
| Active gate | `GATE-R1-CANDIDATE-ACCEPT` |
| R1 verification iteration | 2 |
| Required verdict | `ROT_PHASE1_CANDIDATE_ACCEPTED_R1` or `BLOCKING_FINDINGS_PRESENT` |

## Independence

You are NOT AR-0027 and did not author the implementation or the repair. You author your own held-out tests. The repair
role has not seen them. You are the sole issuer of this verdict.

## What R1 is graded against

The **R1 section** of the frozen boundary, SHA-256
`70977d11b778c4a8391a65cb3e0f53103bcc1e565de595c1e83150797f1699c1`. Plus the R0-accepted architecture (`ARCH-0003`
accepted body scalar `093cb78ef097413665bd34f468b2e7e0f5d9f20b0e9b532dcef517fd8f71536a`), `00-ARCHITECTURE.md`
(`695aa185…`), the owner Capability Acceptance Contract v3 at the repo root (`4c2df291…`), and the binding owner
records `OWNER-DECISION-0006` (`90340772…`), `OWNER-DECISION-0005`, **`OWNER-DECISION-0007`** (`4a0f61c0…`),
`OWNER-DIRECTIVE-0004`, `D-0009` and `D-0007`.

Verify each digest before relying on it. A mismatch is a STOP condition to report, not work around.

## Two owner decisions that close prior questions — do not reopen them

`OWNER-DECISION-0007` answers both questions that were open during AR-0027:

- **`AR27-OD1` is CLOSED.** The owner keeps the current derivation of protected machine state from
  `XDG_STATE_HOME`/`HOME`. The residual relocation asymmetry is an owner-adjudicated position, **not** a defect. It must
  **not** be raised as an R1 blocker, and the machine-state path resolution is correct as it stands.
- **`SRR2-R1-C1` is CLOSED.** The stricter both-floors exit is now owner-decided policy, not an interim. Verify it is
  still implemented at the single point `breakglass::exit_satisfied` with `EXIT_POLICY = "b_stricter_both_floors"` and
  that nothing else compares a release against an exit floor. Do not grade the policy itself.

## Primary focus — what the repair changed

`AR27-B1` was the blocker: `OWNER-DECISION-0006` §6 bullet 1 was enforced as a 26-string substring deny-list, so seven
normal privileged governed operations proceeded below floor. The repair claims it is now **structural**:

- `guard` and `guard_light` decide through `permitted_activity(operation) -> Option<&'static str>`, an **exact-match
  allow-list** derived from §5. `None` means refuse. Nothing is consulted in order to refuse.
- `REFUSED_OPERATIONS` is renamed `REFUSAL_CLASSES` and **decides nothing** — it only selects which §6 bullet a refusal
  is reported under, defaulting to bullet 1.
- `REFUSAL_POLICY = "allow_list_default_refuse"` names the shape.
- The complete below-floor permitted set is **four** operations: `checkpoint` (§5 backup/export), `kernel reinstall`
  (§5 uninstall/reinstall), `update --apply` and `update --rollback` (§5 restoration of an authenticated release).
- A marking record that exists but cannot be read now **refuses** (`Marking::Unreadable`) instead of returning `Ok`.

**Attack all of it.** Specifically: is refusal genuinely the default for an operation that exists nowhere in either
list? Do exact-match semantics hold against case variation, whitespace, prefixes, suffixes, and argument-bearing forms
like `kernel reinstall --force` or `update --apply-unverified`? Can any privileged governed mutation still reach
`guard_write` (or bypass it) below floor? Are all four permitted operations genuinely §5 activities, and do all three
installation paths remain authenticity- and floor-checked inside `admit`?

**Two specific things to check hard:**

1. **Deadlock risk from `Marking::Unreadable`.** Refusing on an unreadable marking is safer, but a machine must still
   be able to reach its exit. The repair claims the allow-list is consulted *before* any state read, so the exit path
   stays open. Test that a machine with a corrupt or unreadable marking can still restore an authenticated release and
   clear the marking. A recovery mode you cannot exit is a defect.
2. **The repair chose to be NARROWER than AR-0027 suggested.** `task status` and `cit simulate` are now **refused**,
   because in code both mutate (`tasks::set_status` behind `mutate_task_status`; `cit simulate` writes
   `cit_status = SIMULATED`). The repair's reasoning is that §5 is permissive ("may include") while §6 is a MUST NOT,
   so erring narrow cannot breach the owner decision, and read-only inspection/diagnosis never calls `guard_write`.
   **Verify that reasoning holds** — confirm §5 inspection and diagnosis genuinely still work below floor, and that
   nothing an operator needs for diagnosis is now unreachable.

Also note `update --rollback` is permitted but was **not** in AR-0027's 35-label set; it reaches `breakglass::guard`
from `update.rs:410` rather than via a `guard_write` label. Confirm it is correctly permitted and still floor-checked.

## The three same-cycle findings

- **`AR27-N1`** — `Envelope::is_expired` now delegates to `expiry_fault`, fail-closed on absent `expires`,
  non-canonical `expires`, non-canonical clock reading, or canonical `expires <= now`. Attack the canonical-form gate,
  and check fail-closed does not brick legitimate operation (for example an unusual but valid clock reading).
- **`AR27-N2`** — the repair **removed the false claim rather than implementing the control**, and named the decision
  `verifier::ROOT_EXPIRY_PROFILE = "reported_not_admission_blocking_r1"`. Its stated evidence: `provision` refuses to
  re-anchor a provisioned machine (`SRR_ALREADY_PROVISIONED`), so barring an expired root from signing its successor
  would make root rotation permanently impossible; TUF applies the expiry check to the final root of the chain for this
  reason. **Independently verify that reasoning** — is root rotation genuinely impossible under the alternative, is the
  profile honest about what expiry does and does not bar, and is the state still reported honestly? If the reasoning is
  wrong, this is a finding.
- **`AR27-N4`** — `crypto::verify` is now `verify_strict` only, with the `ed25519_dalek::Verifier` trait import
  removed. Confirm the permissive verifier is out of scope crate-wide.

## Rerun the prior evidence

AR-0027's held-out tests are committed byte-identical at `release/verification/4.1.6-r1/evidence/heldout-tests/`
(orchestrator-verified unchanged). Rerun them. Expect **26 passed / 3 failed** — the three failures should be exactly
its own `OBSERVED:` weakness assertions flipping (`heldout_srr3::d3` for `AR27-B1`, `heldout_srr2::b1` and `b2` for
`AR27-N1`). **Confirm those three are the intended flips and not regressions**, and that every test pinning a satisfied
property still passes. Then author your own fresh held-out tests — do not merely rerun AR-0027's.

## Carried, not this cycle

R2-lifecycle `AR27-N3`, `AR27-N5`, `AR27-N6`, `AR27-N7` are recorded and carried; do not raise them as R1 blockers.
`SRR-R0-L7` stays absent by owner decision; break-glass recovery must still work with no network. Three INFO items from
the repair (`AR28-R1` the narrower allow-list, `AR28-R2` a now-stale sentence in the candidate-1 build report left
unedited as historical record, `AR28-R3` a wording slip in AR-0027) are recorded for your awareness.

## Preservation — must still hold

Compiler-enforced no-bypass (`install_kernel` taking an `AuthenticatedRelease` constructible only by `admit`); exactly
five `admit` sites and five `install_kernel` sites; floors enforced at all six ingresses; durability ordering with
floors advancing last; D-0007 a separate control establishing **intact**, never **authentic** or **admissible**;
`SRR-R0-L4` vacuous; `gov` verifies and never signs; Contract v3 canonical import byte-identical and failing closed.

Regression: the repair reports `cargo test --lib` 31 passed (26 pre-existing + 5 new) and `cargo test --test
certification` 65 passed (64 + 1 new), zero failures, `tests/certification/srr.rs` purely additive at +177/−0. The
orchestrator independently reproduced these figures. Reproduce and report them yourself.

## Classification and routing

Every finding states: exact normative source; provenance class; lifecycle/gate; whether it falsifies a claim or
proposes stronger assurance; consequence; and evidence or a bounded counterexample. A finding blocks R1 only if its
normative source and lifecycle are R1, or it falsifies an R1 claim. Do not promote R2/R3 material into R1 blockers.

Mark `REQUIRES_R0_OR_OWNER_ADJUDICATION` on anything that would change the accepted R0 boundary or an owner-decided
trade-off — that stops for the owner rather than being repaired. **Note for convergence tracking:** state explicitly,
for each blocking finding, whether it is a **residual of `AR27-B1`/`N1`/`N2`/`N4`** or a **materially new blocker
class**. The orchestrator uses that to decide whether the convergence-escalation threshold is reached.

## Prohibitions

Do not modify product source, the frozen boundary, owner records, prior review or verification evidence,
`release/releases/**`, or any historical record — your own new evidence directory is the sole exception. Do not
implement fixes. Do not read session/agent transcripts or task-output stores. Do not open or write user auto-memory. Do
not contact the product owner. Disclose any delegation.

Judge honestly. An accurate acceptance and an accurate rejection are equally good; only an inaccurate verdict fails.

## Toolchain

`export PATH="$HOME/.cargo/bin:$PATH"` (cargo 1.98.1, not on PATH by default). Set `CARGO_TARGET_DIR` into scratch.

## Deliverables

Evidence under `release/verification/4.1.6-r1-2/`: `00-VERIFICATION-REPORT.md`, `10-BLOCKING-FINDINGS.md` (present and
explicitly empty if none), `20-LATER-LIFECYCLE-CONDITIONS.md`, `evidence/` with your held-out test sources and output,
the AR-0027 rerun output, `REVIEWED-CONTENT-DIGESTS.txt` and reproduction instructions.

Commit that, then write `release/orchestration/phase-1/AGENT_RUNS/AR-0029.report.yaml` per the `AGENT_RUNS/README.md`
schema with `output.commit` naming the work commit, and commit it separately. A run without a durable committed report
is INCOMPLETE and advances no gate.
