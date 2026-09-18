# P2-HO-0003 — Iteration-0 capability family audit: `gamma`

| Field | Value |
|---|---|
| Handoff | P2-HO-0003 |
| From | Phase-2 orchestrator (routing only) |
| To | fresh independent `capability-family-auditor`, run **P2-AR-0003** |
| Candidate | `cap2-candidate-0` (see common protocol for the pinned identities) |
| Active gate | `GATE-P2-BASELINE-AUDIT-0` under `GATE-P2-CAPABILITY-BASELINE-ACCEPT` |
| Family | `gamma` |
| Capabilities owned | E (E1–E4), F (F1–F5), G (G1–G2), H (H1–H4), I (I1–I4) — agent organisation, skills/tools/MCP/capabilities, human command surface, specification and readiness, dynamic work system |
| Owner-source location | Contract v3 lines 360–456 (Gates E, F, G) and 458–590 (Gates H, I) |
| Evidence directory | `release/capability-baseline/audit-0/gamma/` |
| Run report | `release/orchestration/phase-2/AGENT_RUNS/P2-AR-0003.report.yaml` |
| Required verdict | `FAMILY_AUDIT_COMPLETE` or `INCOMPLETE` |

**First read `release/orchestration/phase-2/HANDOFFS/P2-HO-0000-audit-0-common-protocol.md` in full.** It defines who you
are, the standard you apply, the output schemas and the prohibitions. This handoff only scopes your family.

## Your capabilities

E (E1–E4), F (F1–F5), G (G1–G2), H (H1–H4), I (I1–I4) — agent organisation, skills/tools/MCP/capabilities, human command surface, specification and readiness, dynamic work system. Establish the exact capability and bullet set yourself from the owner source at the lines above — not from the
compiled YAML or the evidence map, which are derived views (frozen contract §1). If you find that a derived view omits
or distorts anything in your scope, that is itself a finding.

## Governing-document trace

framework Part VI §§23–25, Part VII §§26–27, Part VIII §§28–32, Part IX §§33–35, Part X §§36–40, Part XI §§41–44; decisions D-0003, D-0004, D-0005, D-0007; API-0001, API-0002.

## Where the implementation starts (orientation only — find the rest yourself)

`runtime/src/authority.rs`, `orchestration/` (claims, dag, tasks, readiness, handoffs, intents, gates, control), `skills.rs`, `tools.rs`, `capabilities/` (registry, protocol, host, ecosystems, governance), `srr/plugins.rs`, `adapters.rs`, `status.rs`, `records.rs`; `framework/roles/`, `framework/skills/`, `framework/commands/`, `framework/taxonomy/`, `tools/` (tool + MCP registries); `spec/`; `tests/certification/`.

These are starting points, not conclusions. A module's existence says nothing about whether a bullet is met.

## Family-specific duties

- **F4 and AC-4.** F4 is `POST_VERIFICATION_HARDENING`; its plugin trust boundary was re-examined in Phase 1 R1 (see
  `release/verification/4.1.6-r1*/`). Map each F4 bullet to that evidence and confirm it yourself on this candidate.
- **H2** is a 26-dimension readiness contract plus a status vocabulary with *silent N/A invalid*: every dimension and
  every status is a bullet.
- **I1** lists twenty-two task classes and **I3** eleven generation sources: each is a bullet.
- **G1** natural-language intent: establish what *deterministic* mapping exists and whether consequential intents invoke
  impact/gate logic automatically; do not assume an LLM is required or forbidden — cite the governing text.
- Cross-capability interactions you own (AC-16): L3 ↔ E1 (gate presentation respects authority) — exercise the E1 side.

## Five other families are auditing in parallel

Other fresh auditors own the other gates. Do not audit their capabilities, and do not read their evidence directories
(they are on other branches and are not merged). A separate fresh synthesis auditor assembles all six families, checks the
cross-cutting criteria (AC-9, AC-10, AC-11, AC-13, AC-14, AC-15, AC-16) and issues the Phase-2 verdict.
