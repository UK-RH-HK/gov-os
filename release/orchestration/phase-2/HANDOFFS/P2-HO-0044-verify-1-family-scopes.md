# P2-HO-0044 — Verification iteration 1: family scopes

| Field | Value |
|---|---|
| Handoff | P2-HO-0044 |
| From | Phase-2 orchestrator (routing only) |
| To | six fresh independent family verifiers, runs **P2-AR-0046 … P2-AR-0051** (one family each; your dispatch message names yours) |
| Candidate | `cap2-candidate-1` (identities in your dispatch message and `ORCHESTRATOR_STATE.yaml`) |
| Active gate | `GATE-P2-CAPABILITY-BASELINE-ACCEPT`, verification iteration 1 |
| Required verdict | `FAMILY_VERIFICATION_COMPLETE` or `INCOMPLETE` |

**Read first, in full:** `P2-HO-0043-verify-1-common-protocol.md` (and through it P2-HO-0000 and P2-HO-0009). Then your
family's **original** audit handoff for its capability set, owner-source lines, governing-document trace and
family-specific duties — those duties apply again. Its "where the implementation starts" list is iteration-0 orientation
only: four repair rounds added modules (e.g. `srr/binding.rs`, `t2.rs`, `orchestration/generation.rs`,
`verification/{slo,flow}.rs`, `cit/*`, `lifecycle/*`); find the current code yourself.

## Families

| Run | Family | Capabilities | Original handoff | Evidence directory | Iteration-0 classes touching your capabilities (`BC-P2-NN`) |
|---|---|---|---|---|---|
| P2-AR-0046 | alpha | A1–A5, B1–B3, S1–S6, T1–T3 | `P2-HO-0001-audit-0-alpha.md` | `verify-1/alpha/` | 01 02 03 08 21 31 33 34 35 36 37 38 45 52 |
| P2-AR-0047 | beta | C1–C10, D1–D6, R1–R3 | `P2-HO-0002-audit-0-beta.md` | `verify-1/beta/` | 01 02 03 19 25 26 27 28 29 30 31 32 33 |
| P2-AR-0048 | gamma | E1–E4, F1–F5, G1–G2, H1–H4, I1–I4 | `P2-HO-0003-audit-0-gamma.md` | `verify-1/gamma/` | 01 02 03 08 09 10 11 13 14 15 16 20 24 34 39 40 41 42 45 46 |
| P2-AR-0049 | delta | J1–J2, K1–K4, L1–L4, M1–M4, N1–N4 | `P2-HO-0004-audit-0-delta.md` | `verify-1/delta/` | 01 02 03 04 05 09 10 11 12 13 14 18 20 29 45 47 48 49 |
| P2-AR-0050 | epsilon | O1–O5, P1–P2, Q1–Q4, U, V1–V4 | `P2-HO-0005-audit-0-epsilon.md` | `verify-1/epsilon/` | 01 02 03 04 06 07 08 10 24 34 42 43 44 50 51 |
| P2-AR-0051 | zeta | W1–W12 | `P2-HO-0006-audit-0-zeta.md` | `verify-1/zeta/` | 01 02 03 04 05 07 16 17 18 19 20 21 22 23 |

The class list is routing help (computed from each class's capability IDs); it is not a claim about any class's state. A
class spanning several families is judged by each family for its own capabilities; the synthesis verifier reconciles.

## Iteration-1 duties by family (in addition to the original family duties)

- **alpha.** A2 per bullet on this candidate (the separate AC-14 verifier re-runs the R1 suites; you still judge A2
  yourself). Lead the **cross-machine attack** of the common protocol end to end (S6; P2-ADJ-0002; OD-P2-02 unprovisioned
  refusal; the embedded-payload bootstrap marking). S4 `gov adopt` A0–A11 on a brownfield tree; S5 `gov update` including
  its health admission and rollback; relocated OS stores (BC-P2-31) through adopt/update/migrate on a legacy tree.
- **beta.** Item 7 as interpreted in the frozen contract §9.1 (AC-7): an executable, evidenced path to establish a
  provisional retrieval profile — you do **not** select a profile. Memory integrity and the relocated claims store;
  rebuild coverage; retrieval regression in the health sandbox.
- **gamma.** F4 and AC-4: plugin trust boundary, D-0010 (hand-declared descriptors), registration inside a claimed task
  (round-4 INT3-O1: K3 impact simulation and F4 gate both hold). OD-P2-01: agent roles stay adapter-declared — attack that
  no agent-supplied input manufactures a human approval. H2–H4 readiness and the scenario chain (P2-ADJ-0003). I1–I4 and
  generated work (BC-P2-24): every source generates linked, idempotent work.
- **delta.** K1–K4 CIT-P/CIT-E end to end, including sealed CIT state and a CIT declined inside another task's claim
  window. L3 owner-signed human channel (P2-ADJ-0001: the standalone anchor is off by default). L4 and the **availability
  rule** for gate blocks. N1–N4 checkpoints/handoffs, including `handoff.create` as a remedy.
- **epsilon.** AC-5 by exercising the scheduler (every item AC-5 lists), the **availability rule** for health blocks
  (scoped refusals, remedies, re-evaluation before refusal, `HEALTH_REMEDY_INCOMPLETE`), Gate U SLOs and the HEALTHY
  conjunction, O4 currency. V1–V4 capability statuses are yours; the AC-6 format acceptance is a separate reviewer's
  (P2-AR-0045) — do not wait for it.
- **zeta.** AC-8: rebuild the Artifact Flow Coverage Matrix yourself on this candidate (every column AC-8 lists). W6
  staleness after an upstream change, both at rebuild and at claim; W12 across G0–G6; W7 orphans; W11 metrics.

Your worktree, branch and commit procedure are given in your dispatch message. Five other family verifiers, an AC-14
R1-preservation verifier and an AC-6 oracle-format reviewer run in parallel; a fresh synthesis verifier follows.
