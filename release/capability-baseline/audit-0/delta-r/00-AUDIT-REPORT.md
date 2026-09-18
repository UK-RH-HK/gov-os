# P2-AR-0011 — Iteration-0 capability family RE-AUDIT: `delta`

| Field | Value |
|---|---|
| Run | P2-AR-0011 (re-audit under P2-HO-0009; scope P2-HO-0004) |
| Role | capability-family-auditor (fresh, independent) |
| Agent model | claude-opus-5 (1M context) |
| Family | delta — J1–J2, K1–K4, L1–L4, M1–M4, N1–N4 (Contract v3 lines 594–747) |
| Candidate | `cap2-candidate-0`, commit `57177a37ea296ece16b185874831462b6a76db18`, `product_code_digest` `bd4d65d9d5ffd6aedbd9435e2091a664dfc3e62f80614a76197cfaf87efd0547` |
| Worktree / branch | `phase2/cap-audit-0-delta-r` at `7eddf91` (candidate + one orchestration-only commit carrying P2-HO-0009) |
| Date | 2026-09-18 |
| Verdict | `FAMILY_AUDIT_COMPLETE` |

## 1. Scope and independence

The universe was established from the owner source itself (18 capabilities, 93 checklist bullets; `evidence/DERIVED-VIEWS-JKLMN.out`
prints every bullet with its line), not from the compiled YAML or the evidence map. I authored none of the Governance OS
implementation, tests or Phase-1 work. Per P2-HO-0009 I did **not** read `release/capability-baseline/audit-0/delta/`,
`AGENT_RUNS/P2-AR-0004.*`, any other family's evidence, session/agent transcripts, task-output stores or user auto-memory
(the one background build/test command's output was captured by redirecting it into this evidence directory, never read from
the task store). No sub-agents were used. No product source was modified; everything I wrote is under this directory and the
run report.

## 2. Pinned inputs (all verified — `evidence/PINNED-INPUTS.out`)

- `product_identity.py HEAD` → `product_code_digest bd4d65d9…0547` (matches); the only diff from `57177a3` is P2-HO-0009.
- Contract v3 SHA-256 `4c2df291…5ed3` (root file and canonical import byte-identical); `gov contract verify` → `CONTRACT_SOURCE_BOUND`.
- Frozen gate contract SHA-256 `d2f33e89…f25e` = `ORCHESTRATOR_STATE.yaml frozen_gate_contract.sha256`.
- Build: `~/.cargo/bin/cargo build --release` (rustc 1.98.1) → `target/release/gov` sha256 `3271ce0e…e81d`, `gov version` 4.1.5.
- Regression (builder tests = regression evidence only, O3): `cargo test --lib` 42/42, `cargo test --test certification` 79/79
  (`evidence/REG-cargo-test-lib.out`, `evidence/REG-cargo-test-certification.out`).

## 3. Method

Every bullet has its own executable demonstration. Seventeen probe programs (`evidence/*.py`, common harness
`evidence/harness.py`) each create disposable projects with `gov init` (or copy `fixtures/brownfield/project`), drive the
release binary through its JSON CLI, and print the exact command (`$ gov …`), one `CHECK <id> PASS|FAIL <statement>` line per
observation with a `detail:` line, `OBSERVE` lines for neutral facts, and a `SUMMARY`. Each capability record in
`capability-audit.yaml` cites the CHECK ids that establish each bullet. Machine state is isolated per project through
`XDG_STATE_HOME` (the builder suite's own mechanism), so the operator's protected machine state was never touched.
Attacks included direct record edits (a real vector: any worker with repository write access can do them), a process kill
mid-transaction (a `git` shim that hangs on `git mv`, then `SIGKILL`), a modified binary copy (implementation-change
freshness), and policy/overlay weakening. `evidence/RUN-ALL.sh` re-runs everything.

Probe outputs and their totals: L3 attacks 46 checks (28 pass / 18 fail), L3 supplement 2 (0/2), L2 20 (13/7), L1 19 (15/4),
L4 10 (10/0), K1 12 (12/0), K2 27 (20/7), K3 19 (9/10), K4 9 (6/3), J1–J2 20 (12/8), M1–M3 21 (15/6), M4 15 (9/6),
N1–N2 24 (16/8), N2-adopt 1 (1/0), N3–N4–W9 18 (12/6), freshness 13 (6/7), derived views 23 (20/3).

## 4. Result per capability

| Cap | Title | Status | Bullets (P&S / PARTIAL / ABSENT) | AC-3 argument | Findings |
|---|---|---|---|---|---|
| J1 | Research becomes evidence | PARTIAL | 0 / 8 / 0 | COULD_UNDERMINE | A0-J1-01 |
| J2 | Experiment lifecycle | **ABSENT** | 0 / 1 / 6 | — (AC-2) | A0-J2-01 |
| K1 | CIT-P | PRESENT_AND_SUBSTANTIAL | 4 / 0 / 0 | — | — |
| K2 | CIT-E | PARTIAL | 5 / 3 / 0 | COULD_UNDERMINE | A0-K2-01, -02, -03 |
| K3 | Automatic impact simulation | PARTIAL | 0 / 8 / 0 | COULD_UNDERMINE | A0-K3-01 |
| K4 | Impact radius (framework R0–R5, not SRR R0–R3) | PARTIAL | 0 / 1 / 0 | CANNOT_UNDERMINE | A0-K4-01 |
| L1 | Contradiction resolution | PARTIAL | 1 / 3 / 0 | COULD_UNDERMINE | A0-L1-01, -02, -03 |
| L2 | Human Decision Gate package | PARTIAL | 1 / 9 / 0 | COULD_UNDERMINE | A0-L2-01, A0-L1-01 |
| L3 | Gate presentation | PARTIAL | 1 / 3 / 1 | COULD_UNDERMINE | A0-L3-01 … -05 |
| L4 | Non-global blocking | PRESENT_AND_SUBSTANTIAL | 2 / 0 / 0 | — | — |
| M1 | T0–T3 tiers | PARTIAL | 2 / 1 / 1 | COULD_UNDERMINE | A0-M1-01, -02 |
| M2 | Reasoning requirement | PARTIAL | 0 / 1 / 0 | COULD_UNDERMINE | A0-M1-02, A0-M2-01 |
| M3 | Role defaults | PARTIAL | 1 / 1 / 0 | COULD_UNDERMINE | A0-M1-02 |
| M4 | Empirical routing | PARTIAL | 2 / 6 / 0 | CANNOT_UNDERMINE | A0-M4-01, -02 |
| N1 | Structured checkpoint | PARTIAL | 7 / 2 / 0 | CANNOT_UNDERMINE | A0-N1-01 |
| N2 | Mandatory triggers | PARTIAL | 2 / 2 / 4 | COULD_UNDERMINE | A0-N2-01 |
| N3 | Provider-independent checkpoint watchdog | PARTIAL | 0 / 1 / 2 | COULD_UNDERMINE | A0-N3-01 |
| N4 | Worker return contract | PRESENT_AND_SUBSTANTIAL | 1 / 0 / 0 | — | — |

Totals: 3 PRESENT_AND_SUBSTANTIAL, 14 PARTIAL, 1 ABSENT, 0 UNCLEAR, 0 N/A_WITH_REASON. Bullets: 29 / 50 / 14 (93).
Family-wide findings A0-J1-02 (derived views) and A0-J1-03 (evidence currency) apply to all 18 and do not change bullet statuses.

## 5. Family-specific duties

### L3 attacks (evidence/L3-gate-presentation-attacks.out, evidence/L3-supplement.out)

| Attack | CIT execution | Task-blocking gate |
|---|---|---|
| Declined gate | refused (REJECTED; GATE_DECLINED even after hand-reset) — L3.b4.d1–d4 | **task becomes READY/runnable** — L3.b4.t2 |
| Revoked gate | refused (GATE_REVOKED at approve and execute; decision REJECTED → refused) — L3.b4.r0–r5 | **task stays runnable** after approval revoked — L3.b4.t3; withdrawn-unanswered → replan READY → claimed — L3.b4.t4 |
| Stale gate | re-answered → APPROVAL_STALE (L3.b4.s1); **manifest edited after approval → COMMITTED** (s2); **answered at R2, re-simulated R5 → COMMITTED** (s3); gates never expire | pending gate: **task closed DONE** — L3s.1 |
| Other-CIT gate | pointer swap → GATE_MISMATCH (o1); **gate.cit edited → CIT-1's answer executes CIT-2** (o2) | missing gate reference → **runnable** — L3.b4.t5 |
| Fabrication: CLI flags / defaults | **`gov decide G --option A` with no role and no --by records human_approved true; CIT COMMITTED** (L3.b5.1, 1x); `--method human` cannot upgrade an agent answer (b5.6 PASS); L1 role refused (b5.4 PASS) | — |
| Fabrication: environment | `GOV_HUMAN_GATE_APPROVED=1` ignored (b5.7 PASS); **`GOV_ROLE=human` records a human answer** (b5.3) | — |
| Fabrication: role claims | **`--role human`** (b5.2); **`gov memory select --role human` → human_approved** (b5.11) | — |
| Fabrication: record edits | **forged gate+decision files → APPROVED human_approved → COMMITTED** (b5.8); **presented flag edited → answerable** (b1.6); **worker's forged records invisible to task close** (b5.9); **suite silent** (b5.10) | — |

Presented ≠ answered holds (b3). Presentation itself is self-attested: `gov --json gate present` and `gov --json continue`
mark `presented_in_chat` with no human-facing output (b2.2, b2.3). The product documents that it "does not authenticate who
holds the session" (docs/ARCHITECTURE.md §4.8); the contract requires the property regardless (Contract v3 line 679; D-0007
rule 2; ARCH-0003 §8). L3 ↔ E1: the E1 role checks work (L1 cannot answer, L1 cannot revoke, L0 cannot present), but the role
checked is the caller's own claim.

### N3 watchdog (evidence/N3-N4-W9-watchdog-handoff.out)

`gov checkpoint watchdog` is provider-independent and its thresholds cannot be relaxed, but it fires only on the counters
the caller passes (after 40 mutating commands with no counters it does not fire). **What marks a checkpoint stale: nothing**
(no field, no check in status/doctor, not after a committed CIT changed the requirement the checkpoint relied on). **What
blocks/degrades a handoff: nothing**; the handoff's own `before_handoff` checkpoint copies the stale context-packet hash;
there is no session-close operation.

### M4 eight-dimension comparison (evidence/M4-empirical-routing.out)

From recorded data the product compares model/provider, task class, cost, latency, pass/fail and repair count. Reasoning
effort and reviewer findings are required at record time but cannot be compared (runs merged; no aggregate). Values are
untyped, and the policy's own names `latency`/`pass_fail` are accepted but reported as 0 ms / failed. Task reports never feed
the data.

### K4

Evaluated strictly as framework §49's impact radius R0–R5 (editorial … governance-wide), unrelated to the Signed Release
Root R0–R3 gates.

### Cross-capability interactions (AC-16, K/N/L side)

- **K2 ↔ W6** — fails: completed tasks, their reports, compiled context packets and checkpoints are not invalidated by a
  committed upstream change; no revalidation work is generated (A0-K2-01).
- **N ↔ W9** — fails: checkpoints record a context-packet hash and memory snapshot, but a handoff after a mandatory input
  changed proceeds with the stale hash; nothing blocks or degrades it (A0-N3-01, A0-N2-01).
- **L3 ↔ E1** — fails: role authority is checked on every gate path but is caller-declared, so the highest-trust fact
  (human approval) is manufactured by a lower-trust input (A0-L3-01, A0-L3-02).

## 6. Blocking findings (17 of 26)

| ID | Sev | Capability | Blocks | Owner decision |
|---|---|---|---|---|
| A0-L3-01 | HIGH | L3 | AC-3, AC-16 | **yes** — choice of human-authentication channel |
| A0-L3-02 | HIGH | L3 | AC-3, AC-16 | no |
| A0-L3-03 | HIGH | L3 | AC-3 | no |
| A0-L3-04 | HIGH | L3 | AC-3 | no |
| A0-L3-05 | MEDIUM | L3 | AC-3 | **yes** — same channel as A0-L3-01 |
| A0-J2-01 | HIGH | J2 | AC-2 | no |
| A0-K2-01 | HIGH | K2 | AC-3, AC-8, AC-16 | no |
| A0-K3-01 | HIGH | K3 | AC-3 | no |
| A0-N2-01 | HIGH | N2 | AC-3, AC-16 | no |
| A0-N3-01 | HIGH | N3 | AC-3, AC-16 | no |
| A0-J1-01 | MEDIUM | J1 | AC-3 | no |
| A0-L1-01 | MEDIUM | L1, L2 | AC-3 | no |
| A0-L1-03 | MEDIUM | L1 | AC-3 | no |
| A0-L2-01 | MEDIUM | L2 | AC-3 | no |
| A0-M1-02 | MEDIUM | M1, M2, M3 | AC-3 | no |
| A0-J1-02 | MEDIUM | all 18 (derived views) | AC-10, AC-13 | no |
| A0-J1-03 | MEDIUM | all 18 (evidence currency) | AC-10, AC-12 | no |

Non-blocking (AC-3 argued CANNOT_UNDERMINE or no Phase-2 AC left unmet): A0-K2-02, A0-K2-03, A0-K4-01, A0-L1-02, A0-M1-01,
A0-M2-01, A0-M4-01, A0-M4-02, A0-N1-01. All findings are `new_vs_residual: BASELINE` (iteration-0 inventory), provenance
`ORIGINAL-NORMATIVE`, lifecycle `P2`. Full statements, normative sources, reproduction and repair directions: `findings.yaml`.

## 7. Freshness, evidence owners, health-scheduler tiers

- The product has no G0–G6 scheduler for these capabilities; the equivalents that exist are G0-style guards in gate/CIT
  commands, CIT-E's own G4-style verification, the task-close checks (G2) and `gov audit` families (G5). None of the
  TEST_POLICY governance families exercises gates, CITs, checkpoints, handoffs, routing, research or experiments
  (FRESH F.families.1), and the evidence map assigns no automated check to any of the 18 capabilities (DV.map.1).
- Invalidation **demonstrated**: overlay policy, provider map and gate/decision record changes make the green audit stale and
  block governance-touching task close until re-audit (F.PROJECT_POLICY, F.MODEL_ROUTING_OVERRIDES, F.HDG-0500, F.close.1/2;
  K3.outside.2a).
- Invalidation **absent**: research, experiment, task, checkpoint and handoff records, and the runtime/CLI implementation
  (a modified binary reproduces the same inputs_hash) — A0-J1-03.
- My evidence is fresh for the exact candidate; each capability record lists its invalidation inputs.

## 8. Derived views (P2-HO-0004 requirement)

Headings, titles, requirement classes and source lines of all 18 capabilities are faithful in the compiled YAML and the
generated view. The compiled "machine-executable" form carries none of the 93 bullets and none of the lines 53–73 fields;
the evidence map marks all 18 `NOT_YET_MAPPED` with no checks (A0-J1-02).

## 9. Cross-family observations for the synthesis auditor (not family-delta findings)

- I4: a task whose `task_status` is set BLOCKED is still handed out as runnable (`L4-non-global-blocking.out` OBSERVE L4.b2.3a).
- E3/E1: any L1 role/session may return any handoff regardless of `to_role` (`N3-N4-W9-watchdog-handoff.out` OBSERVE N4.b1.9).
- C7/D2: the nested worker return (discoveries/risks) is not in the indexed text; a lexical query does not retrieve it (OBSERVE N4.b1.6).
- C9/D2: CIT-P semantic candidates contain duplicates and, for uninformative proposal text, kernel/.gitkeep noise (OBSERVE K1.b2.0, K1.b2.3).
- A1/O4: `gov audit` records carry no implementation identity (FRESH F.impl.1) — reported here as A0-J1-03 for my capabilities.

## 10. What I could not establish, and why

- Whether a gate reaches a human cannot be demonstrated in a synthetic repository without a human and a real adapter; the
  product offers no receipt to test. Alternative route recorded in L3 `not_challengeable`.
- Model execution, session close and provider compaction happen outside the product; I tested the product's routing
  decisions, recorded evidence and trigger surfaces, not a live model/provider.
- The significant-mutation trigger was exercised only through the adoption fixture's migration batches (the only wired path),
  using the same fixture preparation as the builder suite.
- Nothing was left UNCLEAR: every bullet has a direct PASS/FAIL demonstration cited in `capability-audit.yaml`.

## 11. Files

`capability-audit.yaml` (18 capabilities, 93 bullets), `findings.yaml` (26 findings), `evidence/` (17 probe sources and
outputs, `harness.py`, `RUN-ALL.sh`, `PINNED-INPUTS.out`, `REG-*.out`).
