# P2-HO-0007 — Iteration-0 capability baseline synthesis and verdict

| Field | Value |
|---|---|
| Handoff | P2-HO-0007 |
| From | Phase-2 orchestrator (routing only) |
| To | fresh independent `capability-baseline-synthesis`, run **P2-AR-0007** — not any of P2-AR-0001…0006, 0008…0013 |
| Candidate | `cap2-candidate-0` = `57177a37ea296ece16b185874831462b6a76db18`, `product_code_digest` `bd4d65d9d5ffd6aedbd9435e2091a664dfc3e62f80614a76197cfaf87efd0547` |
| Base commit (family audits merged) | `{{MERGE_COMMIT}}` |
| Active gate | `GATE-P2-BASELINE-AUDIT-0` → verdict for `GATE-P2-CAPABILITY-BASELINE-ACCEPT` |
| Frozen gate contract | `release/orchestration/phase-2/GATES/PHASE-2-FROZEN-GATE-CONTRACT.md`, SHA-256 `d2f33e89d5459dd809e17271e46854cc886ed958ca63f89765e16d6a26a9f25e` |
| Contract v3 | `Governance_OS_Capability_Acceptance_Contract_v3.md`, SHA-256 `4c2df29115c8d5389034b2e2d817772add80d61678807c23e0d520c937cb5ed3` |
| Evidence directory | `release/capability-baseline/audit-0/synthesis/` |
| Run report | `release/orchestration/phase-2/AGENT_RUNS/P2-AR-0007.report.yaml` |
| Required verdict | `GOVERNANCE_CAPABILITY_BASELINE_ACCEPTED` or `GOVERNANCE_CAPABILITY_BASELINE_REJECTED` |

## Who you are

A fresh, independent **capability baseline synthesis auditor**. You authored none of the implementation, none of the
family audits or re-audits, and no Phase-1 role. You are the sole issuer of the iteration-0 Phase-2 verdict; the orchestrator will not
overrule it. You never modify product source.

Read `release/orchestration/phase-2/HANDOFFS/P2-HO-0000-audit-0-common-protocol.md` in full — its evidence standard,
schemas and prohibitions apply to you unchanged — and the frozen gate contract in full.

## Inputs — the audits of record

Six family re-audits on the pinned model, merged at the base commit, each under `release/capability-baseline/audit-0/<family>-r/`
with `00-AUDIT-REPORT.md`, `capability-audit.yaml`, `findings.yaml`, `evidence/` (with a `RUN-ALL`/`run-all` script),
and a run report in `release/orchestration/phase-2/AGENT_RUNS/`:

| Run | Family | Capabilities | Family-specific determinations |
|---|---|---|---|
| P2-AR-0013 | alpha-r | A1–A5, B1–B3, S1–S6, T1–T3 | AC-4 (A2) |
| P2-AR-0009 | beta-r | C1–C10, D1–D6, R1–R3 | AC-7 |
| P2-AR-0010 | gamma-r | E1–E4, F1–F5, G1–G2, H1–H4, I1–I4 | AC-4 (F4) |
| P2-AR-0011 | delta-r | J1–J2, K1–K4, L1–L4, M1–M4, N1–N4 | — |
| P2-AR-0008 | epsilon-r | O1–O5, P1–P2, Q1–Q4, U, V1–V4 | AC-5, AC-6 |
| P2-AR-0012 | zeta-r | W1–W12 | AC-8 (`artifact-flow-coverage-matrix.yaml`) |

The first-pass audits P2-AR-0001…0006 (`audit-0/<family>/`, no `-r`) were ruled nonconforming or model-deviating by the
orchestrator (see their `.run.yaml` outcome blocks and ledger P2-L-0004). They are **not** audits of record. You may consult
them only as unverified leads; nothing in them counts as evidence unless you reproduce it.

The family audits are **evidence, not verdicts**. Verify, don't adopt: re-run each family's `RUN-ALL`/`run-all` script (or
a documented subset if one is prohibitively slow — say which), and re-run every probe behind a status you intend to rely
on for acceptance, a `PRESENT_AND_SUBSTANTIAL` that looks thin, or a blocking finding you intend to classify. Where a
family's status or finding is wrong, say so and correct it with your own evidence.

### Cross-family leads the families passed on (not findings until you establish them)

- delta-r → I4: a task set BLOCKED is still handed out as runnable; E3/E1: any role can return any handoff; C7/D2: nested
  worker return not indexed; C9: impact-simulation candidates contain duplicates.
- beta-r → F4: plugins registered as `python3 -m <module>` carry no implementation pin; S4/B2: adoption archives the OS's
  own generated IDE adapter as a legacy rules file, and the migration-ledger artefact ID mismatches the catalogue; N4/E3:
  a valid worker return is rejected at task close because its `status` collides with the report lifecycle status;
  W6/O5 as the owning families reported.
- zeta-r → how R1 assessed "the original product controls, Gate W and G0–G6 implementation mappings remain valid"
  (frozen SRR boundary, R1 list) is for you under AC-14/AC-4.

### Owner-decision flags you must adjudicate

The families raised these as owner decisions. Decide for each whether the accepted sources **already determine** the
answer (then it is an ordinary repair requirement, and you state the requirement and its source) or whether a genuine
owner choice remains (then write it in `owner-decisions-required.md` with the minimum decision, options, consequences and
a recommendation). Read the sources yourself: Contract v3 L3 (*"Human approval cannot be fabricated by agent/CLI
metadata"*) and E1; framework §§23, 50–54; ARCH-0003 §8 (*"Interactive trust changes use local administrator/Human Gate
authority. Repository gate records remain requests"*) and §9 (*"Descriptors cannot self-authorise"*); D-0007 (trust
classes: a lower-trust input may never manufacture a higher-trust fact); OWNER-DECISION-0006 (break-glass authority from
an owner-controlled local or out-of-band mechanism, not manufacturable by repository content, environment, caller
fields, plugins or model output) and its R1 implementation; ARCH-0001.

- **Human-presence / role authentication channel** — delta-r A0-L3-01, A0-L3-05; gamma-r A0-E1-04: the acting role and
  "human" approval are whatever the caller declares (`--role`, `GOV_ROLE`, CLI defaults, record edits).
- **Plugin self-declaration** — gamma-r A0-F4-03: a plugin's own declarations decide whether a gate is needed.
- Any further `owner_decision_required: true` flag in alpha-r.

## What you do

1. **Universe (AC-1).** Establish the full capability set from the owner source yourself and reconcile it against the union
   of the six families and against the compiled YAML/evidence map. Any capability without a status is an AC-1 failure.
2. **Assemble the matrices** into your evidence directory:
   - `capability-status-matrix.yaml` — one row per capability: final status (yours), family status, bullet counts by
     status, evidence location, blocking finding IDs.
   - `suite-to-contract-matrix.yaml` — AC-10: evidence owners per capability, whether each owner actually runs, and the
     invalidation behaviour. Flag every required capability with zero evidence owners.
   - `qualification-coverage-matrix.yaml` — AC-11: Repo A / Repo B / hidden-oracle fault class / chaos-scale-soak /
     retrieval per applicable capability, with the not-challengeable routes.
   - carry `artifact-flow-coverage-matrix.yaml` from zeta-r forward, verified, for AC-8.
3. **Cross-cutting criteria you own directly:** AC-9 (verify the candidate identity yourself with
   `release/orchestration/phase-2/tools/product_identity.py`), AC-12 (freshness and independence of every relied-on piece
   of evidence), AC-13 (contract-binding chain and semantic fidelity of the derived views to the owner source),
   AC-14 (not required for this candidate — confirm the digest equality that makes it so), AC-15 (run the regression
   yourself: `cargo test --lib` and `cargo test --test certification`), AC-16 (exercise the cross-capability interactions
   the frozen contract lists end-to-end, across family boundaries — this is the one place no single family could do it).
4. **Adjudicate AC-2…AC-8** against the assembled evidence, including each family's AC-4/AC-5/AC-6/AC-7/AC-8 determination.
5. **Blocker-class inventory.** Group every blocking finding into blocker classes `BC-P2-NN`, each defined by capability
   ID(s) plus defect mechanism (frozen contract §8). This inventory is what later iterations are measured against for
   convergence, so make each class precise and non-overlapping, and list the finding IDs in each.
6. **Repair delta.** If rejecting, write `repair-delta.md`: for every blocker class, the exact requirement that must become
   true (with normative source), the acceptance evidence a later verifier will demand, dependencies between classes, and
   a suggested work partition into independent repair workstreams with **non-overlapping file scopes** where possible.
   State requirements, not designs.
7. **Owner decisions.** For every item where closing it would need a choice the accepted sources do not make, write it in
   `owner-decisions-required.md` with the minimum decision needed, the options, their consequences and your recommendation.
   Do not manufacture such items: a missing capability that the contract already requires is **not** an owner decision.

## Output

`release/capability-baseline/audit-0/synthesis/`: `00-SYNTHESIS-REPORT.md` (verdict first, then AC-1…AC-16 each with
HOLDS / FAILS and evidence), the four matrices, `blocker-classes.yaml`, `findings.yaml` (your own findings plus your
disposition of every family finding: CONFIRMED / CORRECTED / REFUTED, with evidence), `repair-delta.md` (if rejecting),
`owner-decisions-required.md` (write "none" explicitly if none), `later-lifecycle-notes.md`, `evidence/`.

Commit the evidence directory first, then your run report with that commit's hash, on branch
`phase2/cap-audit-0-synthesis`. Do not merge, rebase, tag or push.

## Prohibitions

As in P2-HO-0000. In addition: do not edit any family's evidence directory — disagree in your own files.
