# HO-0027 — Handoff for the fresh independent R1 candidate verification

| Field | Value |
|---|---|
| Handoff | HO-0027 |
| From | orchestrator (routing only) |
| To | NEW fresh independent R1 verifier / test author |
| Candidate | `949c4d343a6d5f203534afa6e3363992fee12488` on `phase1/srr1-r1-build` (builder report `cedb3e6f`) |
| Builder run | AR-0026, `READY_FOR_INDEPENDENT_OS_VERIFICATION` |
| Active gate | `GATE-R1-CANDIDATE-ACCEPT` |
| Required verdict | `ROT_PHASE1_CANDIDATE_ACCEPTED_R1` or `BLOCKING_FINDINGS_PRESENT` |

## Independence

You did not author this implementation, the architecture, the correction or either R0 review. You author your own
held-out tests; the builder has not seen them and must not. You never modify product source — if a test needs a fixture,
put it in your own evidence tree or a test-only path, and say so.

## What R1 is graded against

The **R1 section** of the frozen boundary:
`release/root-of-trust/signed-release-root-v1/01-FROZEN-R0-R1-R2-R3-ACCEPTANCE-BOUNDARY.md`,
SHA-256 `70977d11b778c4a8391a65cb3e0f53103bcc1e565de595c1e83150797f1699c1`.

Plus the R0-accepted architecture that R1 implements: `spec/architecture/ARCH-0003.yaml` (accepted body scalar SHA-256
`093cb78ef097413665bd34f468b2e7e0f5d9f20b0e9b532dcef517fd8f71536a`; the file digest at the acceptance commit `2b36b44`
was `42681978…`) and `release/root-of-trust/signed-release-root-v1/00-ARCHITECTURE.md` (SHA-256 `695aa185…`).

Plus, as normative owner input: `OWNER-DECISION-0006` (SHA-256 `903407729327d67c198c9bf97885a936c5601993e16ad76137a3106c5728d1db`),
`OWNER-DECISION-0005`, `OWNER-DIRECTIVE-0004`, `D-0009`, and `D-0007` which remains ACTIVE.

Plus the owner Capability Acceptance Contract v3 at the repo root, SHA-256
`4c2df29115c8d5389034b2e2d817772add80d61678807c23e0d520c937cb5ed3` — every capability whose evidence this change
invalidates. Verify the digest; never reconstruct contract text from memory.

Verify each digest before relying on it. A mismatch is a STOP condition to report, not work around.

## Toolchain

`export PATH="$HOME/.cargo/bin:$PATH"` (cargo 1.98.1; not on PATH by default). Set `CARGO_TARGET_DIR` into your scratch
directory. crates.io is reachable.

## Scope — prove or falsify these

From the frozen R1 section, on this exact candidate:

1. A mature reviewed cryptographic/TUF implementation is used **correctly** — not merely present. The builder chose
   `ed25519-dalek` 2.2.0 with `verify_strict`, signing over the exact bytes of the `signed` member via
   `serde_json::value::RawValue`. Attack the adapter: signature-over-different-document, key-id confusion, role
   confusion, threshold bypass, unparsed-trailing-bytes, duplicate keys, malleability.
2. Candidate/source files cannot create their own trusted identity — repository content, `KERNEL_MANIFEST.json`,
   `framework.lock`, env vars, caller fields, plugins and model output must never establish release authority or Human
   Gate approval.
3. Wrong key, wrong product, wrong channel, modified metadata/payload/migration, replay, downgrade and expiry all fail
   closed.
4. **All** privileged ingress paths call the common verifier. The builder's claim is that `kernel::install_kernel`
   takes an `AuthenticatedRelease` constructible only by `srr::verifier::admit`. Test that claim, and specifically
   probe the one declared exception — the update **transaction abort** path — for a usable bypass.
5. Verified bytes are staged, installed and used without substitution.
6. Staging/install/rollback/recovery are atomic and crash-safe on supported filesystems. Interrupt them.
7. Metadata/release high-water is durable and monotonic, stored outside every repository, and enforced at **every**
   backward-capable ingress — not only `rollback`.
8. All ten `OWNER-DECISION-0006` requirements hold **in running code**, including the byte-exact
   `DEGRADED — RECOVERY ONLY` token (U+2014) and the requirement that break-glass recovery works with **no network**.
9. Everything else the frozen R1 section requires.

## Five disclosed residuals you must independently judge

The builder disclosed these rather than concealing them. Judge each on its merits — a disclosed limitation is not
automatically acceptable, and not automatically a blocker:

- **Unprovisioned posture.** Floors advance only from `Authenticity::Authentic`, so a machine that has never verified a
  signed release enforces no release floor and claims no authenticity. The builder calls this an IMPLEMENTATION-CHOICE
  preserving the pre-RoT product. Test whether an adversary can *keep* or *return* a machine to that posture to evade a
  floor, and whether the honesty claim holds everywhere it must.
- **Protected-state relocation.** A process running as the owner can relocate `HOME`/`XDG_STATE_HOME`. The builder
  relies on ARCH-0003 §1 placing such a process inside the trusted boundary. Check that the override is genuinely
  refused on a provisioned machine and that the reliance is sound, not circular.
- **Expiry comparison** is a lexicographic RFC-3339 UTC comparison at second precision. Attack it with inputs that are
  valid RFC-3339 but not in the emitted format.
- **Delegated targets have no issuing tooling.** Verification and enforcement exist, but nothing can *issue* a
  delegation, so a privileged remotely-acquired capability currently has no admission path. Judge whether the owner's
  R1 obligation from `OWNER-DECISION-0005` — distinguishing built-in/local capabilities from remotely acquired
  privileged plugins/tools/profiles — is actually met by enforcement alone.
- **Certification harness change.** `tests/certification/common.rs` now gives each scenario its own `XDG_STATE_HOME`.
  Confirm no assertion was weakened and no pre-existing test was edited to make it pass. All 49 pre-existing scenarios
  are claimed to pass unmodified — verify that against history.

## Also verify

- `SRR2-R1-C1` is implemented at exactly one named point (`breakglass::exit_satisfied`, flag `EXIT_POLICY`) at the
  stricter both-floors reading, and nothing else in the codebase compares a release against an exit floor. The owner's
  question on it is open and non-blocking; **do not** treat the interim choice as a defect.
- `SRR2-R1-C2`, `SRR2-R1-C3`, `SRR-R0-L1`, `L2`, `L3`, `L4` (must remain vacuous — no dev/test trust mode, no flag, env
  or feature that relaxes verification), `L5`, `L6`.
- `SRR-R0-L7` is owner-closed: offline/air-gapped **first install** must NOT exist. Its absence is correct. Break-glass
  *recovery* must still work offline.
- D-0007 semantics preserved: installed-kernel integrity remains a separate control establishing **intact**, never
  **authentic** or **admissible**.
- No private key material in the repository, logs or fixtures usable as a production root; `gov` verifies and never
  signs outside `#[cfg(test)]`.
- The Contract v3 canonical import is byte-identical to the owner source and fails closed on divergence.
- Full regression: `cargo test --lib` and `cargo test --test certification`. The builder reports 26 and 64 passing with
  no pre-existing failures. Reproduce and report exact figures.

## Classification rule

Every finding states: exact normative source; provenance class (ORIGINAL_NORMATIVE / OWNER_ADDED_NORMATIVE /
NECESSARY_DERIVED / IMPLEMENTATION_CHOICE / VERIFIER_HARDENING / LATER_QUALIFICATION / NEW_OWNER_DECISION_REQUIRED /
OUT_OF_SCOPE); lifecycle/gate; whether it falsifies an existing claim or proposes stronger assurance; consequence; and
evidence or a bounded counterexample.

A finding blocks R1 only if its normative source and lifecycle are R1 under the frozen boundary, or it falsifies an R1
claim. Do NOT promote R2 production evidence or R3 high-assurance criteria into R1 blockers.

**Critical routing distinction.** If a finding would require changing the **accepted R0 architecture boundary** — the
trust chain, metadata model, ingress set, transaction invariant, bootstrap assumption, or an owner-decided
security/availability/cost/usability trade-off — mark it `REQUIRES_R0_OR_OWNER_ADJUDICATION`. Such a finding stops for
the owner instead of being silently repaired. Implementation defects **within** the accepted boundary are ordinary R1
blockers and route to a bounded repair.

## Prohibitions

Do not modify product source, the frozen boundary, owner records, prior review evidence, `release/verification/**`,
`release/releases/**` or any historical record. Do not implement fixes — you verify. Do not read, list or search
session/agent transcripts or task-output stores. Do not open or write user auto-memory. Do not contact the product
owner; record `NEW_OWNER_DECISION_REQUIRED` items in your report. Disclose any delegation.

## Deliverables

Evidence under `release/verification/4.1.6-r1/`: `00-VERIFICATION-REPORT.md`, `10-BLOCKING-FINDINGS.md` (present and
explicitly empty if none), `20-LATER-LIFECYCLE-CONDITIONS.md`, and `evidence/` with your held-out test sources, their
output, `REVIEWED-CONTENT-DIGESTS.txt` and reproduction instructions.

Commit that, then write `release/orchestration/phase-1/AGENT_RUNS/AR-0027.report.yaml` per the `AGENT_RUNS/README.md`
schema with `output.commit` naming the work commit, and commit it separately. A run without a durable committed report
is INCOMPLETE and advances no gate.
