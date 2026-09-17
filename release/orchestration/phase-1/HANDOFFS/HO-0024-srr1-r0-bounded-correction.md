# HO-0024 — Handoff for the single bounded R0 architecture correction (SRR-1)

| Field | Value |
|---|---|
| Handoff | HO-0024 |
| From | orchestrator (routing only) |
| To | fresh isolated architecture-correction role |
| Candidate under correction | D-0009 + ARCH-0003 + `release/root-of-trust/signed-release-root-v1/` at `5fd8358` |
| Rejection being corrected | AR-0023, `ROT_ARCHITECTURE_REJECTED_R0`, work commit `2dc08c2` |
| Active gate | `GATE-R0-ARCH-ACCEPT` |
| Cycle | bounded R0 correction cycle **1 of 1** |
| Required verdict | `ARCHITECTURE_CORRECTION_READY_FOR_REVIEW` or `INCOMPLETE` |

## Scope — exactly two blockers

Correct only the two findings in the active R0 repair queue, using the bounded delta at
`release/root-of-trust/signed-release-root-v1-review-r0/11-CORRECTION-DELTA.md`:

- **`SRR-R0-H1`** (HIGH) via **CD-R0-1** — make the signed security-floor / minimum-version rule govern `recovery`,
  `rollback` and every other backward-capable privileged lifecycle ingress consistently; qualify the `recovery`
  ingress's "installed valid recovery path" object so local D-0007 integrity records establish only that the local copy
  is *intact*, never that it is *admissible*; reconcile the revoked-binary recovery allowance at `ARCH-0003.yaml:91`;
  and state the below-floor outcome per the owner decision below.
- **`SRR-R0-M1`** (MEDIUM) via **CD-R0-2** — declare the time/clock assumption and its non-guarantee, and make the
  currency-honesty claim conditional in the same register the document already uses.

## Owner decision that CD-R0-1 was blocked on

`OWNER-DECISION-0006` selects **(b) BREAK-GLASS, authorised and recorded**. Read the record in full at
`release/orchestration/phase-1/GATES/OWNER-DECISION-0006-BELOW-FLOOR-RECOVERY.md`. Its ten binding requirements are
normative for this correction. Designing the break-glass authority in *architectural* terms is in scope; its
implementation, storage format, CLI surface and tests are R1 and are not.

## Hard scope limits

- Do **not** redesign unrelated Governance OS capabilities. The trust chain, metadata model, metadata role table,
  domain-separation table, lifecycle ingress set, transaction invariant, bootstrap assumption, CI/headless model,
  D-0007 transition rule and non-goals are unchanged and uncontested — the candidate got them right.
- Do **not** route any of `SRR-R0-L1`…`L9` into this correction. They are non-blocking later-lifecycle conditions.
  `SRR-R0-L6` is deferred to R1 and `SRR-R0-L7` is closed as out of scope, both by `OWNER-DECISION-0005`.
- Do **not** broaden `SRR-R0-M1` into another trust-state protocol, and do not introduce a trusted-time service,
  monotonic-time source, time attestation, signed-time floor or roughtime. Expiry *durations* stay R1/R2 parameters.
- Do **not** modify `01-FROZEN-R0-R1-R2-R3-ACCEPTANCE-BOUNDARY.md`. It is the frozen contract, pinned at SHA-256
  `70977d11b778c4a8391a65cb3e0f53103bcc1e565de595c1e83150797f1699c1`, and must stay byte-identical.
- Do **not** modify `D-0009`, `D-0007`, `D-0008`, `ARCH-0002`, any review evidence, `release/verification/**`,
  `release/releases/**`, product source, runtime, kernel, CLI, capabilities, migrations or tests.
- Do **not** implement anything. Do **not** grade your own correction — a new fresh independent R0 reviewer does that.
- Do **not** create a RoT-1 Revision 8 or resume CP-1.

## Files you may change

1. `spec/architecture/ARCH-0003.yaml` — the two corrections, plus lineage bookkeeping (`updated`, and a correction
   marker consistent with the record's existing field conventions). Keep `status: PROVISIONAL`, `in_effect: false`,
   `human_approved: false`.
2. `release/root-of-trust/signed-release-root-v1/00-ARCHITECTURE.md` — the two corrections.
3. `release/root-of-trust/signed-release-root-v1/04-R0-CORRECTION-1.md` — **new**: the correction record. State, per
   blocker, what text changed, where, why, which frozen R0 item it closes, and which owner requirement it satisfies.
   Include a requirement-by-requirement map of the ten `OWNER-DECISION-0006` requirements to architecture text.

If closing a blocker honestly requires touching anything outside this list, do not do it silently: stop, and say so in
your report with the exact reason.

## Method

For each correction state: the blocker id; the exact prior text and its location; the corrected text; the frozen R0
item(s) it closes; the normative source; and what an R1 verifier could test as a result. Acceptance is not yours to
assert — your deliverable is a corrected candidate plus an honest account of what changed.

## Deliverables

Commit the corrected candidate on your branch, then write
`release/orchestration/phase-1/AGENT_RUNS/AR-0024.report.yaml` per the schema in `AGENT_RUNS/README.md`
(`run_id: AR-0024`, `role: r0-architecture-correction`, `output.commit` naming the correction commit) and commit it
separately. A run without a durable committed report is INCOMPLETE and advances no gate.
