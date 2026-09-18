# P2-HO-0011 — Repair iteration 1, round 1: WS-1 (part) + WS-12

| Field | Value |
|---|---|
| Handoff | P2-HO-0011 |
| From | Phase-2 orchestrator (routing only) |
| To | fresh `capability-repair` builder, run **P2-AR-0014** |
| Workstream | WS-1 (part) + WS-12 |
| Classes | BC-P2-01, BC-P2-51 |
| Base | the commit your worktree is checked out at (integration branch after the iteration-0 synthesis merge) |
| Output directory | `release/capability-baseline/repair-1/ws01-12/` |
| Run report | `release/orchestration/phase-2/AGENT_RUNS/P2-AR-0014.report.yaml` |
| Required verdict | `READY_FOR_INDEPENDENT_CAPABILITY_VERIFICATION`, `OWNER_DECISION_REQUIRED` or `INCOMPLETE` |

**First read `release/orchestration/phase-2/HANDOFFS/P2-HO-0010-repair-1-common-protocol.md` in full.** Then read
`release/capability-baseline/audit-0/synthesis/repair-delta.md` §0, §2, §3 and **every class listed above** in full,
with the findings each class cites (`blocker-classes.yaml`, `findings.yaml`, and the family audit evidence).

## Files you own

`runtime/src/contracts.rs`; `framework/contracts/**` (never the canonical import's bytes); `framework/schemas/governance-capability-acceptance.schema.json`; `tests/governance/capability-evidence-map.yaml` (structure/bullets only — evidence owners are BC-P2-02, a later round); `docs/generated/**`; a **new, separate** Qualification Oracle format definition and validator (location your choice, outside the public qualification suite, e.g. `framework/qualification-oracle/` + a runtime module).

Shared hot spots and additive exceptions are in the common protocol.

## Your classes

- **BC-P2-01** — compiled contract, generated view and evidence map carry every capability section of the owner source
  (including Gate U), every checklist item, the W10 hard-invariant text, each gate's advanced-qualification challenge, the
  per-capability fields of Contract v3:53-73, and the requirement-class label **verbatim**; `gov contract verify` fails,
  typed, on any semantic difference in any derived view. The owner source's bytes are untouched.
- **BC-P2-51** — a machine-checkable Qualification Oracle **format** covering V1 (fault manifest), V2 (hidden path-map
  oracle), V3 (hidden memory oracle) and V4 (quantitative scoring), with a validator that rejects a record missing any
  required field. It is a *format*; generate **no** hidden fault and no oracle content. A fresh independent reviewer will
  judge it against Contract v3 V1-V4 (AC-6). Keep it separate from the permanent public qualification suite
  (Contract v3:1062).

## Seven other builders run in parallel

WS-1/12, WS-2, WS-3, WS-4, WS-5, WS-6, WS-8 and WS-9/11 each own disjoint files. You will not see their work until
integration. Where you need something they own, expose your side and record the integration point.
