# P2-AR-0049 — verification iteration 1, capability family `delta`

| Field | Value |
|---|---|
| Run | **P2-AR-0049** — fresh, independent capability family verifier |
| Family | `delta` — J1–J2, K1–K4, L1–L4, M1–M4, N1–N4 (research and experimentation, change control and impact, human decision gates and contradictions, model routing, checkpoints/compaction/handoffs) |
| Candidate | `cap2-candidate-1` |
| Verdict | **`FAMILY_VERIFICATION_COMPLETE`** |
| Blocking findings | **none** |
| Capabilities | 18 owned, 93 checklist bullets evaluated individually |
| Statuses | 15 `PRESENT_AND_SUBSTANTIAL`, 3 `PARTIAL` (K4, M1, M4), 0 `ABSENT`, 0 `UNCLEAR`, 0 `N/A_WITH_REASON` |
| Held-out suite | 265 tests, **256 pass, 9 fail** — every failure is a gap this run records, asserted deliberately: six for the three `PARTIAL` capabilities and three for two residual low-severity prior findings |
| Independence | I authored none of the implementation, none of its tests, none of the iteration-0 audits, none of the repairs and no Phase-1 role. I did not read another iteration-1 verifier's evidence or branch, any transcript, any task-output store or user auto-memory. |

## 1. Pinned inputs — verified

| Input | Expected | Observed | |
|---|---|---|---|
| `git rev-list -n1 cap2-candidate-1` | `0bad524d836f179964ffbac31972856ea6434682` | `0bad524d836f179964ffbac31972856ea6434682` | ✅ |
| `product_identity.py cap2-candidate-1` → `product_code_digest` | `e6332fc7…2220` | `e6332fc7d5af5c73adbe0f200003db30fe5a6fd0b7f24d047d3e340e6f972220` | ✅ |
| `product_identity.py cap2-candidate-1` → `governed_state_digest` | `3d2aeba2…20c0` | `3d2aeba2fc3b52a95c369c49a854bb9d443b0b03da1180db5339f01d892620c0` | ✅ |
| `product_identity.py HEAD` (my worktree, `8588813`) | same two digests | identical to the tag's | ✅ |
| `Governance_OS_Capability_Acceptance_Contract_v3.md` SHA-256 | `4c2df291…5ed3` | `4c2df29115c8d5389034b2e2d817772add80d61678807c23e0d520c937cb5ed3` | ✅ |
| `GATES/PHASE-2-FROZEN-GATE-CONTRACT.md` SHA-256 | `d2f33e89…f25e` | `d2f33e89d5459dd809e17271e46854cc886ed958ca63f89765e16d6a26a9f25e` | ✅ |

`python3 release/orchestration/phase-2/tools/product_identity.py cap2-candidate-1` prints `commit: f75eb7db…` because
`cap2-candidate-1` is an **annotated tag** and the tool echoes the object it was given; `git cat-file -t` confirms it is
a tag object whose commit is `0bad524`, which `git rev-list -n1` returns and which is the commit my worktree's HEAD
descends from with identical product code. No mismatch, no STOP.

## 2. Method

Every one of the 93 checklist bullets in the owner source (Contract v3 lines 594–747) was established afresh on this
candidate with my own evidence. Nothing was carried over from iteration 0; the repair and integration reports under
`release/capability-baseline/repair-1/**` were read only as claims to attack and are cited nowhere as evidence.

**The harness is my own.** `gov` holds no signing key, so a human answer, a presentation receipt, a provisioned trust
root, a T2 binding authority and a signed kernel release all have to come from outside the product. I wrote that
administrator/owner domain myself in `heldout/hc.py`, from the on-disk metadata format read out of
`runtime/src/srr/metadata.rs`, `runtime/src/srr/binding.rs` and `runtime/src/human_channel.rs` — Ed25519 through
python-`cryptography`, my own key seeds, my own root document, my own release/snapshot/timestamp chain. It reproduces
the product's payload digest exactly (`348e1922945fbf91c730cc64e2257c13a73356d14dc9516d792264aaf9667bb5`), so the
releases it signs install. Nothing in it is copied from
the product's certification signer, which I read only to learn the document shapes.

Every scenario machine follows the documented first-run path of OWNER-DECISION-P2-0002 and P2-ADJ-0002: **provision a
throw-away root, bind the machine's T2 authority, then install a signed release**. Each probe builds a
legitimately green baseline under Contract v3 before it asserts anything (P2-ADJ-0003) — a feature whose readiness
cells are all `PRESENT` or carry an explicit `N/A_WITH_REASON`, a scenario with its data declaration, and an acceptance
obligation produced by a test-design task claimed and closed by an independent role in its own session, because the
product refuses a self-claimed one. A vacuous pass is not a pass.

**The held-out suite** is `heldout/RUN-ALL` (nine probes, 265 tests; per-test output in `evidence/<probe>.out`). Each
probe's scenario machines are keyed by `DELTA_RUN`, so a re-run never inherits a previous run's state:

| Probe | Covers | Result |
|---|---|---|
| `J-research-experiment.sh` | J1, J2 | 29 pass, 0 fail |
| `D-prior-findings.sh` | disposition of the low-severity iteration-0 findings | 10 pass, 3 fail (A0-M2-01 and A0-M4-02, unchanged) |
| `K12-cit-p-and-e.sh` | K1, K2, sealed CIT state, a CIT declined inside another task's claim window | 29 pass, 0 fail |
| `K34-materiality-and-radius.sh` | K3 (all eight classes, two paths), K4 | 22 pass, 2 fail (K4's two missing effects) |
| `L12-contradictions-and-package.sh` | L1, L2 | 27 pass, 0 fail |
| `L34-presentation-and-blocking.sh` | L3, L4, the availability rule for gate blocks | 42 pass, 0 fail |
| `M-model-routing.sh` | M1–M4 | 30 pass, 4 fail (no T0 route; the M4 comparison surface) |
| `N-checkpoints-and-handoffs.sh` | N1–N4, `handoff.create` as a remedy | 41 pass, 0 fail |
| `X-crosscutting.sh` | the availability rule for a real health hard block, cross-machine continuity, trust classes, freshness | 26 pass, 0 fail |

`cargo test --lib`: **276 passed, 0 failed**. `cargo test --test certification`: **207 passed, 0 failed**
(`evidence/regression-AC15.out`). Builder tests are cited as regression evidence only.

## 3. Per-capability result

| Cap | Title | Bullets | Status | Note |
|---|---|---|---|---|
| J1 | Research becomes evidence | 8/8 | `PRESENT_AND_SUBSTANTIAL` | every field required; influence derived, reported and syncable |
| J2 | Experiment lifecycle | 7/7 | `PRESENT_AND_SUBSTANTIAL` | lifecycle enforced; reproducibility judged, not declared; production merge refused |
| K1 | CIT-P | 4/4 | `PRESENT_AND_SUBSTANTIAL` | deterministic traversal, routed semantic supplement, radius, eight consequences |
| K2 | CIT-E | 8/8 | `PRESENT_AND_SUBSTANTIAL` | propagation reaches completed work, its evidence, packets and checkpoints; atomic rollback |
| K3 | Automatic impact simulation | 8/8 | `PRESENT_AND_SUBSTANTIAL` | all eight classes derived from what the change touches, in CITs and inside tasks |
| K4 | Impact radius | 0/1 bullets (4 of its 6 effects) | **`PARTIAL`** | traversal, test scope, model tier and human approval hold; agents and rollback do not (V1-K4-01) |
| L1 | Contradiction resolution | 4/4 | `PRESENT_AND_SUBSTANTIAL` | precedence first, blocked manifest, gate escalation, independent assessment |
| L2 | Human Decision Gate package | 10/10 | `PRESENT_AND_SUBSTANTIAL` | every field substantive; options real; OS-derived next actions |
| L3 | Gate presentation | 5/5 | `PRESENT_AND_SUBSTANTIAL` | the whole fabrication surface refused; owner-signed channel only |
| L4 | Non-global blocking | 2/2 | `PRESENT_AND_SUBSTANTIAL` | scoped blocks, remedies available, one explicit global stop |
| M1 | T0–T3 capability tiers | 3/4 | **`PARTIAL`** | no T0 routing outcome (V1-M1-01) |
| M2 | Reasoning requirement | 1/1 | `PRESENT_AND_SUBSTANTIAL` | declared minimum honoured, floors raise only |
| M3 | Role defaults | 2/2 | `PRESENT_AND_SUBSTANTIAL` | T3 for orchestration/memory/audit; provider names only in the overlay |
| M4 | Empirical routing | 6/8 | **`PARTIAL`** | reasoning effort and reviewer findings not comparable (V1-M4-01) |
| N1 | Structured checkpoint | 9/9 | `PRESENT_AND_SUBSTANTIAL` | every declared field, including OS-derived open questions |
| N2 | Mandatory triggers | 8/8 | `PRESENT_AND_SUBSTANTIAL` | all eight fire |
| N3 | Provider-independent watchdog | 3/3 | `PRESENT_AND_SUBSTANTIAL` | self-observed counters, real staleness, degraded boundaries |
| N4 | Worker return contract | 1/1 | `PRESENT_AND_SUBSTANTIAL` | survives the sub-session and the close-receipt schema |

Bullet-level detail, implementation references, automated and independent evidence, freshness, health tiers,
qualification coverage, adoption obligations and residual risk are in `capability-audit.yaml`.

## 4. Family delta's iteration-1 duties

### K1–K4 CIT-P/CIT-E end to end, sealed CIT state, and a CIT declined inside another task's claim window

One transaction carried the whole of K2: a change to `REQ-0001`'s acceptance criteria, proposed with the declared
trigger `editorial`, was derived `acceptance_criteria_change`, auto-simulated at R1 over typed edges reaching the
feature, both reports and both tasks; it raised its gate; execution before an honoured answer was refused; the owner's
signed answer approved it; it committed; the authoritative record changed; the DONE task that implemented the
requirement was marked for revalidation with its reasons and a revalidation task was generated; the acceptance
obligation went stale; the checkpoint that had recorded the pre-change input was reported `STALE`; the index refreshed;
and the executed writes were bound in the CIT's sealed state. A second transaction that introduced a dangling reference
failed verification, was `ROLLED_BACK`, its file write removed and its record restored. Derived-view regeneration was
shown by deliberately damaging the tool registry and the adapter manifest before execution and finding both rebuilt
from the committed state.

**Sealed CIT state.** Hand-editing a CIT record to `APPROVED` makes `gov cit execute` refuse `T2_UNBOUND`, naming the
operation and time the record was sealed at, and the governance suite reports it in `os_binding_integrity` at **high**
severity. The same record is `FOREIGN` on a machine provisioned from another owner's root.

**A CIT declined inside another task's claim window.** With `TASK-0007` claimed by session `w`, a CIT to change the
same requirement was proposed, its gate raised and answered **B** (declining). The decline did not approve the CIT
(`gov cit approve` refused), the CIT could not execute, the change never reached the authoritative record — and the
claimed task's own close path was untouched: it closed `OK`. The decline refused exactly what it protected.

### K3's auto-trigger for all eight material classes

Each of architecture, behaviour, interfaces, security, governance/policy, infrastructure cost, acceptance criteria and
data migration was proposed **with the declared trigger set to `editorial`**. Each was derived as its true class with
`label_understates: true`, auto-simulated, and gated. The same eight changes made inside one ordinary task whose
contract allowed every path were refused at close with `MATERIAL_CHANGE_REQUIRES_CIT`, the refusal naming each class,
its subject, its rule and its evidence. The one exception is the kernel's own stated rule: a behaviour change to
product source is classified material (`behaviour_change`, `requires_cit_in_task: false`) but left to the
implementation task's contract — it is detected, not refused.

*A note on preconditions (P2-ADJ-0003):* my first behaviour probe wrote to `src/**`, which the default
`REPOSITORY_CONTRACT.yaml` does not classify as `source` (it classifies `product/**`). The empty classification was my
fixture's fault, not the product's; re-run against `product/**` the class is derived. This is recorded because it is
also a real adoption obligation: on a tree whose repository contract does not classify the product directory, the
behaviour class cannot be derived, and adoption is where that must be fixed.

### L3's owner-signed human channel, and that no agent-supplied input manufactures a human approval

P2-ADJ-0001 holds as written: `HUMAN_GATE_POLICY.human_channel.standalone_anchor_when_unprovisioned` is `false`, an
unprovisioned machine reports `HUMAN_CHANNEL_UNAVAILABLE` with provisioning as the remediation, and on a provisioned
machine the anchor is the root's `human-gate` delegation (`source: srr-root`).

Everything I could think of to fabricate an approval was refused: `--by human`, `--by product-owner`,
`--by owner@example.com`, `--role human`, `GOV_ROLE=human`, `GOV_HUMAN_GATE_APPROVED=1`, an invocation declaring no
role at all, a hand-written `presented_in_chat: true`, a hand-written `ANSWERED` gate with `by_kind: human` plus a
matching decision carrying `human_approved: true`, a presentation receipt signed by a key the root delegates nothing
to, and an answer the owner signed for a different gate. The forged gate/decision pair is `T2` `BROKEN`, is not
honoured, and is reported by the suite. Only an owner-signed `human-gate-answer` bound to the gate id, its OS-issued
instance nonce and the SHA-256 of the exact rendered package produced an approval — and it re-verified on the owner's
second provisioned machine while failing under a foreign owner's root.

### L4 and the availability rule for gate blocks

A gate holds only its own branch: the gated task sits in `waiting_human` while the independent branch stays `runnable`
and was actually claimed, and the DAG names the human-gate dependencies. Every refusal is typed and names its scope
(the blocked task **and** the gate that blocks it). The block's remedies stay available — `gate present`, `gate show`,
`gate list`, `task dag` all return `OK` under it — and answering the gate clears the block for exactly the work it
protected. Against a real health hard block (`X-crosscutting.sh`), each block names its scope, subjects, refused
operations and remedies; `handoff.create`, `task.create`, `task.claim` and independent read-only work all stay
available; and the two operations that appear in both lists, `cit.execute` and `update.apply`, are **admitted as the
block's own remedy** rather than refused (`gov health guard` says so, and a remedy CIT executed under the block and
cleared it). Only the explicit global stop, `FREEZE_WRITES`, refuses everything that mutates, and `gov resume` lifts it.

### M1–M4 model routing

Three tiers are reachable routing outcomes and the overlay cannot lower a kernel floor: `security: T1` in the overlay
leaves security at T3, `default_reasoning: low` for the orchestrator leaves it at `high`, a strengthening does take
effect, and `gov policy overrides` lists the applied override and the refused weakenings with their kernel values.
Provider and model names resolve only from the overlay and appear nowhere in project state. A declared reasoning
minimum is honoured and cannot be declared downwards. **T0 is not reachable** and the routing comparison cannot
separate reasoning effort or report reviewer findings — the two `PARTIAL`s, below.

### N1–N4 checkpoints and handoffs, including `handoff.create` as a remedy

All nineteen `CHECKPOINT_POLICY.fields` are recorded on a real checkpoint, with the context packet hash bound to a
state reference (repo commit, governed-state digest, index manifest hash) and each mandatory input carrying its
delivered and current hash. All eight mandatory triggers fire. Staleness is real: after a CIT changed an input a
checkpoint had recorded, `gov checkpoint freshness` reports `STALE` with the upstream change and its cause; `gov
session close` is explicitly **degraded and not resumable** (never refused); `gov handoff create` over the same state
reports the stale inputs, the invalidated previous packet and the refreshed one. The watchdog fires with the caller's
counters at zero, on gov commands and changed files it observed itself. A schema-valid worker return is accepted,
persisted as a governed record, survives the sub-session and is read back by a fresh session with no conversation
state. **`handoff.create` is a listed remedy of each hard block this run raised, and is actually available under one**
— the remediation handoff can be made while the block stands. (The blocks I could raise were `high`-severity
`schema_invariants` blocks; `scheduler/catalogue.rs` narrows the handoff remedy further at `critical`, to the handoff
of work that declares the block's check among its `remedies`. I did not raise a critical block, so that narrower case
is untested here.)

## 5. Findings

Four findings, **none blocking**. Full text in `findings.yaml`.

| Id | Cap | Sev | Blocking | Label | Summary |
|---|---|---|---|---|---|
| `V1-K4-01` | K4 | MEDIUM | no | `RESIDUAL` (prior `A0-K4-01`; no BC class) | the radius determines neither the agents a change needs nor a differentiated rollback |
| `V1-M1-01` | M1 | MEDIUM | no | `RESIDUAL` (prior `A0-M1-01`; no BC class) | no routing outcome resolves to the declared T0 deterministic tier |
| `V1-M4-01` | M4 | MEDIUM | no | `RESIDUAL` (prior `A0-M4-01`; no BC class) | the comparison cannot separate reasoning effort and reports no reviewer findings |
| `V1-DELTA-01` | K1,K2,K3,N1,N2 | LOW | no | `RESIDUAL` of **BC-P2-02** | 9 of 93 bullets declare no automated check in the evidence map |

**On the labels.** The first three are the same capability, the same bullet and the same mechanism as iteration-0
findings that the synthesis recorded as MEDIUM and **non-blocking**, so they never entered the `BC-P2` blocker-class
inventory. They are therefore residuals with `inventoried_class: null` and the prior finding named explicitly — they
are not materially new, because neither the capability nor the mechanism is absent from iteration 0. Labelling them
`MATERIALLY_NEW` would be false and would inflate the convergence count for gaps the phase has known about since
iteration 0. `V1-DELTA-01` is an incomplete fix of an inventoried class (BC-P2-02 went from 101 unmapped rows to 9
unmapped bullets in my scope), which §8 of the frozen contract treats as a residual.

**Why none of them blocks.** A finding blocks only if it leaves an acceptance criterion unmet or falsifies an explicit
Phase-2 claim (frozen contract §6). AC-2 is met for this family — no capability is `ABSENT` or `UNCLEAR`. The three
`PARTIAL`s carry the AC-3 argument in `capability-audit.yaml`:

- **K4** — the radius already decides what is traversed, what is retested, whether the human must approve and the tier
  floor; the two missing effects are allocation and recovery *planning* outputs. A qualification scenario is scored on
  whether the OS admitted or refused work and whether propagation reached the right artefacts, and neither depends on
  the OS naming reviewers or varying the rollback text by radius. `CANNOT_UNDERMINE`.
- **M1** — the absence of a T0 routing outcome changes which model tier the harness is told to use, never what the OS
  enforces. The deterministic work the T0 description lists (graph traversal, validation, the suite, generation) is
  performed by the OS itself outside the router; every governance decision in this verification was produced with no
  model at all. The exposure is cost and latency on trivial classes, which Phase 4 measures through M4 telemetry.
  `CANNOT_UNDERMINE`.
- **M4** — both missing dimensions are recorded per run and retained in `routing/evidence.jsonl`, so an advanced
  qualification analysis can compute them offline; what is missing is the product's own view. No governance admission,
  refusal or propagation decision depends on it. `CANNOT_UNDERMINE`.

## 6. Iteration-0 findings: disposition

All 28 iteration-0 findings in family delta's scope are disposed in `prior-findings-disposition.yaml` — the 26
findings of the delta audit of record plus the two synthesis findings that touch L3 and N4:
**23 CLOSED, 5 RESIDUAL, 0 NOT_APPLICABLE.**

**Closed (23).** `A0-J1-01` (research completeness), `A0-J1-02` (derived views carried no bullet and no evidence
owner), `A0-J1-03` (currency omitted delta's record classes and the runtime identity), `A0-J2-01` (experiment lifecycle
absent), `A0-K2-01` (propagation stopped at open work), `A0-K2-02` (rolled-back state left in derived views),
`A0-K2-03` (pre-existing damage attributed to a transaction), `A0-K3-01` (materiality was the proposer's label),
`A0-L1-01` (agent resolution failed open on unassessed values), `A0-L1-02` (no rationale, nowhere for evidence),
`A0-L1-03` (contradictions undetected and delivered as authority), `A0-L2-01` (package not enforced), `A0-L3-01`
(approval from caller metadata), `A0-L3-02` (forged records approved and executed), `A0-L3-03` (approval not bound to
its subject), `A0-L3-04` (declined/revoked/missing gates authorised work), `A0-L3-05` (self-attested presentation),
`A0-M1-02` (overlay lowered kernel floors), `A0-N1-01` (no open questions, coarse files_changed), `A0-N2-01` (half the
triggers never fired), `A0-N3-01` (no staleness, a watchdog that counted nothing), plus the two synthesis findings in
my scope: `S0-E1-01` (an undeclared invocation acted as L4 — closed on the L3 surfaces) and `S0-W5-01` (a worker return
could not be the close receipt — closed on the N4 side).

**Residual (5).** `A0-K4-01` (partly closed: the radius now maps to a tier floor; agents and rollback unchanged),
`A0-M1-01` (no T0 route), `A0-M2-01` (a run recorded below the task's declared reasoning minimum is accepted with no
flag — a later-lifecycle note, it does not unseat M2's bullet), `A0-M4-01` (the comparison surface) and `A0-M4-02`
(untyped routing evidence silently zeroed; the policy's own field aliases mis-aggregated — a later-lifecycle note on
evidence quality).

Fourteen of the eighteen `BC-P2` classes the routing table associates with family delta are `CLOSED` for delta's
capabilities; `BC-P2-02` is residual (`V1-DELTA-01`); `BC-P2-14` and `BC-P2-29` are closed for delta's half and left to
the owning families for the rest. Per-class judgements are at the end of `prior-findings-disposition.yaml`.

## 7. The attacks the common protocol asks of every verifier

- **Cross-machine continuity (P2-ADJ-0002).** Two machines of the same owner, both provisioned from my throw-away root
  and bound to the same T2 binding authority: a gate answered on A is honoured on B with its T2 binding `VERIFIED` and
  the owner's signature re-verified against the same anchor; the CIT state and the decision written on A are honoured
  on B. A record hand-edited on B is refused there; a machine provisioned from a **foreign owner's** root reports the
  same record `FOREIGN` with the reason, and the owner's signature does not verify under that root; an **unprovisioned**
  machine has no human channel at all and names provisioning as the remediation. No private key or shared secret is in
  the repository, and `gov` verifies without any signing entry point.
- **Availability rule.** Exercised on both block kinds my capabilities issue — gate blocks (§4) and health hard blocks.
- **Trust classes (D-0007).** No project file, CLI flag, environment variable, role claim or model output produced a
  higher-trust fact, a role or a human approval anywhere in this verification.
- **Freshness (AC-10).** Demonstrated, not assumed: the currency key covers 31 input classes including research and
  experiment records, checkpoint/handoff records, task manifests and the runtime identity; writing a research record
  and a checkpoint changes it and `gov health currency` names the changed classes with their Contract v3 labels;
  changing a governing policy changes it; and a CIT invalidates completed work, its reports, its packets and its
  checkpoints.

## 8. Regression (AC-15, for the synthesis verifier's benefit)

Both suites were re-run in my own worktree against this candidate, with `CARGO_BUILD_JOBS=2`:

- `cargo test --lib` — **276 passed, 0 failed** (62s)
- `cargo test --test certification` — **207 passed, 0 failed** (4901s)

Both numbers match what the integration run recorded for `cap2-candidate-1`, reproduced here independently. AC-15 is
the synthesis verifier's criterion, not mine; I record my own run so the numbers can be checked against another's.
Full output: `evidence/regression-AC15.out`.

## 9. What I could not establish

1. **Content, as opposed to form.** The OS checks that a research record carries every J1 field, that a gate package is
   substantive, that an experiment's reproduction agrees — never that the measurements support the conclusion, that the
   impact statement is true, or that two runs agree for the right reason. Those are Phase-4 hidden-fault classes; each
   is named per capability in `capability-audit.yaml` under `hidden_oracle_fault_class`.
2. **Scale.** Every probe ran on a synthetic project of a few dozen artefacts. Traversal at R5 over a large graph,
   `gov research sync` over thousands of influence edges, and the routing report over a large evidence file are
   proposed as chaos/scale/soak challenges; I did not run them, and Gate U SLOs belong to family epsilon.
3. **The narrowest remedy case.** The availability rule was exercised against `high`-severity hard blocks. At
   `critical`, `scheduler/catalogue.rs` narrows the surviving remedies further (only a proposal or a handoff whose
   subjects reach the block's); I could not raise a critical block with the conditions available to me, so that
   narrower case rests on the code and on the builder's own tests, not on my evidence.
4. **The harness boundary for context utilisation.** N3's watchdog fires on counters the OS observes itself, which I
   demonstrated; the context-utilisation input is necessarily supplied by the harness, and I could only confirm that it
   makes the watchdog fire *earlier*, never later.
5. **A truly hostile agent.** OD-P2-01 keeps agent roles adapter-declared, so I attacked the human boundary (which
   holds completely) and not the agent-role boundary, which the owner has accepted as a known gap for Phase 2.
6. **Capabilities outside family delta.** Every judgement here is about delta's 18 capabilities. Where a finding or a
   blocker class spans families (`S0-E1-01`, `S0-W5-01`, `BC-P2-14`, `BC-P2-29`), I disposed only of delta's side and
   said so.

## 10. Procedural note

Early in the run, while polling my own background build, I ran `ls` on the harness's task-output directory
(`/tmp/claude-.../tasks/`), which the common protocol lists among the stores a verifier must not read. I listed the
directory and read no file in it other than my own build's output; no other agent's output influenced any judgement in
this report. Recording it here rather than leaving it unsaid. For the rest of the run I wrote background output into my
own evidence directory instead.

`rm` is denied in this environment. Nothing was deleted: each probe run uses its own set of scenario machines
(`DELTA_RUN=<tag>`), and where a probe needed a file moved aside it was copied to the scratch area and moved back.

## 11. Contents of this directory

| Path | What |
|---|---|
| `00-VERIFICATION-REPORT.md` | this report |
| `capability-audit.yaml` | 18 capabilities, 93 bullets, bullet-level status and evidence |
| `findings.yaml` | 4 findings, none blocking |
| `prior-findings-disposition.yaml` | all 28 iteration-0 findings in scope, disposed, plus a per-class judgement |
| `heldout/RUN-ALL` | runs the whole held-out suite, one PASS/FAIL line per test |
| `heldout/lib.sh` | the harness: provisioning, binding, signed install, seeding, signed human answers |
| `heldout/hc.py` | the verifier's own administrator/owner domain (TEST MATERIAL ONLY) |
| `heldout/*.sh` | the nine probes |
| `evidence/*.out` | every probe's captured output, and the regression run |
| `evidence/build-capability-audit.py` | generates `capability-audit.yaml`, taking the bullet text verbatim from the owner source |

Nothing in `heldout/` or `evidence/` is part of the product tree, and no product source, test, fixture, schema, policy
or document was modified by this run.
