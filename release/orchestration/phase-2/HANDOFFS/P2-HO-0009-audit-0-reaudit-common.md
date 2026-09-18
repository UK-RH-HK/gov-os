# P2-HO-0009 — Iteration-0 family RE-AUDIT: common instructions

| Field | Value |
|---|---|
| Handoff | P2-HO-0009 |
| From | Phase-2 orchestrator (routing only) |
| Applies to | re-audit runs P2-AR-0009 (beta), P2-AR-0010 (gamma), P2-AR-0011 (delta), P2-AR-0012 (zeta), P2-AR-0013 (alpha), and any later family re-audit that cites it |
| Candidate | `cap2-candidate-0`, `product_code_digest` `bd4d65d9d5ffd6aedbd9435e2091a664dfc3e62f80614a76197cfaf87efd0547` |
| Evidence directory | `release/capability-baseline/audit-0/<family>-r/` |
| Scope | exactly the original family handoff `P2-HO-000N-audit-0-<family>.md` — same capabilities, same family-specific duties |

**Read in full, in this order:** this file; `P2-HO-0000-audit-0-common-protocol.md` (standard, schemas, prohibitions —
all apply unchanged); your family's original handoff; the frozen gate contract; `AGENT_RUNS/README.md`.

## Why the families are being re-audited

The iteration-0 family audits P2-AR-0001…0006 were recorded against `agent_model: claude-opus-5` but each run
self-reported `claude-opus-4-6`, a deviation from the phase's recorded protocol. Several also fell short of the common
protocol's evidence standard: capability statuses of `PRESENT_AND_SUBSTANTIAL` alongside the same run's own findings of
unmet bullets, and many bullets resting on a single aggregate output. For a uniform exhaustive baseline, every family is
re-audited from scratch on the pinned model. The earlier audits are retained unchanged as historical records.

**Do not read your family's earlier evidence (`release/capability-baseline/audit-0/<family>/`) or its run report**, nor
any other family's evidence. Your judgement must not be anchored on them.

## The evidence standard, restated (the common protocol's own — nothing new)

- **Exhaustive and bullet-level.** Every checklist bullet has its own demonstration: construct the input, run the product
  (`target/release/gov`, the library through a small harness in your evidence directory, or the product tests), capture
  the observable result. A single aggregate output may support several bullets only if the record for each bullet names
  the exact lines of that output that demonstrate it.
- **Not evidence:** a printed `echo` of expected behaviour; a help string; a flag's existence; a schema field; a policy
  key; a doc comment; a test *name*. (Contract v3 line 93.)
- **No contradiction between a status and a finding.** A bullet with a recorded gap is not `PRESENT_AND_SUBSTANTIAL`; a
  capability with any such bullet is not either (frozen contract §4).
- **Blocking follows the frozen acceptance criteria**, not severity labels (frozen contract §6). A gap that leaves AC-1…AC-16
  unmet blocks.
- **Lifecycle labels mean what the frozen contract says.** `P3` is the provisional-retrieval-profile phase, `P4` advanced
  qualification. A gap in a Phase-2 capability is `P2` unless a normative text places it later — quote it.
- **A failing observation is recorded as failing**, with an explanation.
- **Owner decisions** only where closing a gap needs a choice the accepted sources do not make; a capability the contract
  requires but the product lacks is not an owner decision.
- **Depth over speed.** There is no time pressure. Record your actual model identity in `agent_model`.

Worktree, branch and commit procedure are given in your dispatch message.
