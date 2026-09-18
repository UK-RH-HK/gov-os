# P2-HO-0001 — Iteration-0 capability family audit: `alpha`

| Field | Value |
|---|---|
| Handoff | P2-HO-0001 |
| From | Phase-2 orchestrator (routing only) |
| To | fresh independent `capability-family-auditor`, run **P2-AR-0001** |
| Candidate | `cap2-candidate-0` (see common protocol for the pinned identities) |
| Active gate | `GATE-P2-BASELINE-AUDIT-0` under `GATE-P2-CAPABILITY-BASELINE-ACCEPT` |
| Family | `alpha` |
| Capabilities owned | A (A1–A5), B (B1–B3), S (S1–S6), T (T1–T3) — constitutional/trust foundations, repository contract, release/distribution/init/adopt/update, adoption roles |
| Owner-source location | Contract v3 lines 130–203 (Gates A, B) and 894–973 (Gates S, T) |
| Evidence directory | `release/capability-baseline/audit-0/alpha/` |
| Run report | `release/orchestration/phase-2/AGENT_RUNS/P2-AR-0001.report.yaml` |
| Required verdict | `FAMILY_AUDIT_COMPLETE` or `INCOMPLETE` |

**First read `release/orchestration/phase-2/HANDOFFS/P2-HO-0000-audit-0-common-protocol.md` in full.** It defines who you
are, the standard you apply, the output schemas and the prohibitions. This handoff only scopes your family.

## Your capabilities

A (A1–A5), B (B1–B3), S (S1–S6), T (T1–T3) — constitutional/trust foundations, repository contract, release/distribution/init/adopt/update, adoption roles. Establish the exact capability and bullet set yourself from the owner source at the lines above — not from the
compiled YAML or the evidence map, which are derived views (frozen contract §1). If you find that a derived view omits
or distorts anything in your scope, that is itself a finding.

## Governing-document trace

framework §§2–3, 8–9, 20–21, 72–74 (Part III, V, XXII) and Part XXIV; the Release/Distribution protocol v1.2 in full (§§1–18, including init §9, adopt §10 stages A0–A11, update §12, cross-machine §16); the Adoption/Migration/Audit protocol v3.0 in full (role separation §3, evidence tree §5, A1–A4 §§6–9, independent migration review/verification §§10–12, memory §§13–15, audit §16).

## Where the implementation starts (orientation only — find the rest yourself)

`runtime/src/policy.rs`, `policy_precedence.rs`, `policy_coverage.rs`, `authority.rs`, `exceptions.rs`, `security/`, `kernel.rs`, `kernel_trust.rs`, `lock.rs`, `srr/` (Signed Release Root), `init.rs`, `adopt.rs`, `migrations/`, `update.rs`, `release.rs`, `recovery.rs`, `orchestration/control.rs` (emergency controls), `paths.rs`, `project.rs`; `framework/constitution/`, `framework/policies/`, `framework/roles/`; `fixtures/` (greenfield, brownfield, migration, update, multi-machine); `tests/certification/`.

These are starting points, not conclusions. A module's existence says nothing about whether a bullet is met.

## Family-specific duties

- **A2 and AC-4.** A2 is `POST_VERIFICATION_HARDENING` and rests on the Phase-1 acceptance `ROT_PHASE1_CANDIDATE_ACCEPTED_R1`
  (AR-0033, `release/verification/4.1.6-r1-4/`). Map every A2 bullet to the R1 evidence that establishes it **and** re-run
  enough yourself to confirm it on this candidate. R1 acceptance is evidence, not a substitute for your per-bullet judgement.
  Note which A2 bullets R1 did not examine (e.g. offline verification after an authentic envelope; rotation/revocation
  semantics) and establish them yourself.
- **S4 (`gov adopt`)** has twelve stages A0–A11; each is a bullet. Drive them end-to-end on a brownfield tree, not only via
  the certification test.
- **T1–T2** concern role separation and fresh-session independence **as product capabilities** (what the OS enforces for
  consumer adoption), not how this Phase-2 orchestration is run.
- Cross-capability interactions you own (frozen contract AC-16): S3/S4/S5 ↔ A2 (every lifecycle ingress through the
  common verifier).

## Five other families are auditing in parallel

Other fresh auditors own the other gates. Do not audit their capabilities, and do not read their evidence directories
(they are on other branches and are not merged). A separate fresh synthesis auditor assembles all six families, checks the
cross-cutting criteria (AC-9, AC-10, AC-11, AC-13, AC-14, AC-15, AC-16) and issues the Phase-2 verdict.
