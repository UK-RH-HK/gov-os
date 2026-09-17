# HO-0028 — Handoff for bounded R1 repair 1

| Field | Value |
|---|---|
| Handoff | HO-0028 |
| From | orchestrator (routing only) |
| To | fresh isolated R1 repair role |
| Base commit | `d10c2a552f71462209f53977d272eaf38a35f93f` |
| Rejected candidate | `srr1-r1-candidate-1` (`229d1543`, builder work `949c4d3`) |
| Verification | AR-0027, `BLOCKING_FINDINGS_PRESENT` (work commit `26c2dc5`) |
| Active gate | `GATE-R1-CANDIDATE-ACCEPT` |
| R1 repair iteration | 1 |
| Required verdict | `READY_FOR_INDEPENDENT_OS_VERIFICATION` or `INCOMPLETE` |

## Independence

You did not author the implementation under repair and you do not grade your own repair. A NEW fresh independent
verifier will re-verify the repaired candidate with its own held-out tests. You have not seen and must not seek the
next verifier's tests. AR-0027's held-out tests are committed at
`release/verification/4.1.6-r1/evidence/heldout-tests/` and you may read them — that verdict is already issued.

## Mandatory — the blocking finding

**`AR27-B1`** (MEDIUM, `OWNER-ADDED-NORMATIVE`, lifecycle R1). Read it in full at
`release/verification/4.1.6-r1/10-BLOCKING-FINDINGS.md`.

`runtime/src/srr/breakglass.rs` enforces `OWNER-DECISION-0006` §6 bullet 1 through `guard` / `guard_light` as a
**substring deny-list** over 26 strings, so any operation not matching one proceeds while the machine is marked
`DEGRADED — RECOVERY ONLY`. Measured across all 35 `guard_write` labels after a genuine break-glass entry: 23 refused,
12 permitted. Four of those twelve are legitimate §5 activities. **Seven are normal privileged governed operation
covered by no §5 activity:** `cit approve`, `cit reject`, `gate revoke`, `handoff return`, `plugins unregister`,
`adopt extract-legacy`, `adopt build-memory`. Nothing else gates them — `authority::require` is orthogonal to the
marking.

This also falsifies a claim the candidate makes about itself: `breakglass.rs:163` documents `guard` as "The default is
**refuse**", and the module requirement map asserts §6 row 6 satisfied. Both are false as written.

**What must become true.** A machine marked `DEGRADED — RECOVERY ONLY` must refuse normal privileged governed
operation **as a class**, not as an enumerated list of strings. The owner already fixed the policy in
`OWNER-DECISION-0006` §5 (permitted activities) and §6 (forbidden operations) — you are implementing the decided
policy, not choosing one. Invert to an allow-list derived from §5, or otherwise make refusal the structural default;
a longer deny-list that still fails open for an unlisted operation does not close this finding. Correct the doc comment
and the requirement map so they state what the code actually does.

## Authorised in the same cycle — three non-blocking R1-lifecycle findings

These are same-gate findings the verifier recommended fixing in this cycle because they are local to the same files.
Fix them; they are in scope.

- **`AR27-N1`** (MEDIUM) — expiry is compared lexicographically with no canonical-form gate: a `+14:00` expiry
  thirteen hours in the past evaluates as not expired, lowercase `z` likewise, and an absent `expires` never expires.
  Gate the canonical form, or compare properly. Note the verifier's reasoning that this is publisher-side deviation
  rather than an adversary path, because `expires` sits inside the signed byte-string — that is why it is not blocking,
  not a reason to leave it.
- **`AR27-N2`** (MEDIUM) — an expired trust anchor still authorises trust-changing operations: the branch at
  `verifier.rs:312-314` has two identical arms, so its comment describes a control that is not implemented. Implement
  the control the comment claims, or remove the claim. Do not leave code asserting a property it does not have.
- **`AR27-N4`** (LOW) — `crypto::verify` carries a permissive `or_else(verify)` fallback that defeats
  `verify_strict`. It has zero product call sites today, but it is live on the public API. Remove it or make it
  strict.

## Explicitly OUT OF SCOPE — do not touch

- **`AR27-OD1`** — anchoring protected machine state to a fixed machine-domain path independent of `HOME`/
  `XDG_STATE_HOME`. It is flagged `REQUIRES_R0_OR_OWNER_ADJUDICATION` and routed to the product owner. It would change
  the accepted R0 bootstrap/trusted-boundary assumption and collides with the certification harness's own isolation
  mechanism. **Do not implement it, do not partially implement it, and do not change how machine-state paths are
  resolved.**
- **R2-lifecycle findings** `AR27-N3`, `AR27-N5`, `AR27-N6`, `AR27-N7` — recorded and carried; not this cycle.
- **`SRR2-R1-C1`** — the stricter both-floors interim stands while the owner's question is open. Leave
  `breakglass::exit_satisfied` and `EXIT_POLICY` at the interim reading, and keep it the single point where a release
  is compared against an exit floor. Do not widen it.
- **`SRR-R0-L7`** — offline/air-gapped first install stays absent (owner-closed). Break-glass recovery must continue
  to work with no network.

Do not repair beyond this list. Scope creep in a repair cycle invalidates evidence and burns a verification cycle.

## Preservation obligations

Everything AR-0027 found satisfied must stay satisfied. In particular: the compiler-enforced no-bypass property
(`install_kernel` taking an `AuthenticatedRelease` constructible only by `admit`); exactly five `admit` sites and five
`install_kernel` sites; floors enforced at all six ingresses; durability ordering with floors advancing last; D-0007
remaining a separate control establishing **intact**, never **authentic** or **admissible**; `SRR-R0-L4` vacuous (no
`SigningKey` or secret-key construction in product source, no flag/env/feature relaxing verification); `gov` verifying
and never signing; the Contract v3 canonical import byte-identical and failing closed.

The regression must still pass in full: `cargo test --lib` (26) and `cargo test --test certification` (64), zero
failures, no pre-existing test edited to make anything pass, no assertion weakened. Report exact figures.

Re-run AR-0027's held-out tests too, and report their results — they are your best check that you closed `AR27-B1`
rather than moved it.

## Hard prohibitions

No RoT-1 Revision 8; no CP-1 resumption; no D-0008/ARCH-0002 activation. Do not amend D-0007, D-0009, the accepted
ARCH-0003 body, the frozen boundary or any owner record. Do not modify `release/verification/**` (including AR-0027's
evidence), `release/root-of-trust/*-review*/**`, `release/releases/**` or any historical record. No private keys. No R2
ceremony, no R3 criteria. Do not read session/agent transcripts or task-output stores. Do not open or write user
auto-memory. Do not contact the product owner — record any `NEW_OWNER_DECISION_REQUIRED` item in your report.

## Toolchain

`export PATH="$HOME/.cargo/bin:$PATH"` (cargo 1.98.1, not on PATH by default). Set `CARGO_TARGET_DIR` into scratch.

## Deliverables

- The repair, committed on branch `phase1/srr1-r1-repair-1`.
- Repair evidence under `release/root-of-trust/signed-release-root-v1-r1-repair-1/`: what changed and why, per finding;
  how `AR27-B1` is now structural rather than enumerated; the full regression output; the AR-0027 held-out test results;
  and `REVIEWED-CONTENT-DIGESTS.txt`.
- `release/orchestration/phase-1/AGENT_RUNS/AR-0028.report.yaml` per the `AGENT_RUNS/README.md` schema, committed after
  the work commit and naming it in `output.commit`.

An honest `INCOMPLETE` is better than a false readiness claim. You declare readiness only; never acceptance.
