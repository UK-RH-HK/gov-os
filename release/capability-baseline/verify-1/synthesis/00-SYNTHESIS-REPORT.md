# P2-AR-0052 — Governance OS Phase 2, verification iteration 1: synthesis and verdict

## Verdict

# `GOVERNANCE_CAPABILITY_BASELINE_REJECTED`

for candidate **`cap2-candidate-1`**, commit `0bad524d836f179964ffbac31972856ea6434682`,
`product_code_digest` `e6332fc7d5af5c73adbe0f200003db30fe5a6fd0b7f24d047d3e340e6f972220`,
`governed_state_digest` `3d2aeba2fc3b52a95c369c49a854bb9d443b0b03da1180db5339f01d892620c0`.

**Three acceptance criteria are not met: AC-3, AC-4 and AC-5.** The other thirteen hold. The verdict is issued on
the whole of AC-1…AC-16 for this exact candidate.

This is a rejection on a much better candidate than iteration 0. Thirty-seven of the fifty-two iteration-0 blocker
classes are closed outright; of the 193 iteration-0 findings the families disposed, 142 are closed. Eight blocking
findings remain, concentrated in three places: the tool-installation trust surface that OWNER-DECISION-P2-0003
created (four of the eight), adoption on a secret-bearing brownfield tree, failure memory, the update ingress's
version short circuit, and one tier of the health scheduler.

| Field | Value |
|---|---|
| Run | **P2-AR-0052**, fresh independent capability-baseline synthesis verifier, sole issuer of this verdict |
| Gate | `GATE-P2-CAPABILITY-BASELINE-ACCEPT` |
| Branch / worktree | `phase2/verify-1-synthesis`, at `311eafaf6f123f5c9c4dfe146c4ce8e38f31f154` |
| Blocking findings | **8** — 7 confirmed from the family verifications, 1 of my own (`S1-A1-01`) |
| Blocker classes still blocking | BC-P2-07, BC-P2-32, BC-P2-33, BC-P2-37, BC-P2-41, BC-P2-45 |
| New blocker classes | **BC-P2-53** (one) |
| `introduces_materially_new_blocker_classes` | **true** |
| Owner decisions required | **none** |

I authored none of the implementation, none of its tests, none of the iteration-0 audits, none of the repairs and
none of the iteration-1 verifications. I am not the orchestrator. I modified no product source. I read no agent
transcript, no task-output store and no user auto-memory, spawned no sub-agent and contacted no owner.

---

## 1. Pinned inputs — all verified; no STOP

| Input | Expected | Observed | |
|---|---|---|---|
| `git rev-list -n1 cap2-candidate-1` | `0bad524d…4682` | `0bad524d836f179964ffbac31972856ea6434682` | ✔ |
| `product_identity.py cap2-candidate-1` | both digests | `e6332fc7…2220` / `3d2aeba2…20c0` | ✔ |
| `product_identity.py HEAD` (`311eafa`) | identical to the tag's | `e6332fc7…2220` / `3d2aeba2…20c0` | ✔ |
| Contract v3 SHA-256 | `4c2df291…5ed3` | `4c2df29115c8d5389034b2e2d817772add80d61678807c23e0d520c937cb5ed3` | ✔ |
| Frozen Phase-2 gate contract SHA-256 | `d2f33e89…f25e` | `d2f33e89d5459dd809e17271e46854cc886ed958ca63f89765e16d6a26a9f25e` | ✔ |
| Frozen SRR R0–R3 boundary SHA-256 | `70977d11…99c1` | `70977d11b778c4a8391a65cb3e0f53103bcc1e565de595c1e83150797f1699c1` | ✔ |

`evidence/AC-9-AC-13-pinned-inputs-and-contract-verify.out`. The product code and governed state at my worktree's
`HEAD` are byte-identical to the tag's, so everything below grades the frozen candidate.

## 2. Method — verify, don't adopt

The eight iteration-1 verifications are **evidence, not verdicts**. I re-ran all of it.

| What I re-ran | Result |
|---|---|
| `alpha` `heldout/RUN-ALL` (suites t01–t06, its default set) | **387 PASS / 10 FAIL** — P2-AR-0046's per-suite figures reproduced exactly (54/1, 74/0, 53/5, 67/1, 59/2, 80/1) |
| `beta` `heldout/RUN-ALL` | **185 PASS / 10 FAIL** — its nine recorded failures exactly; the tenth is a load artefact, §2.1 |
| `gamma` `heldout/RUN-ALL` | **184 PASS / 17 FAIL** — P2-AR-0048's totals and every failing check exactly, including the executed proof |
| `delta` (every probe, run individually so nothing was written into delta's evidence directory) | **256 PASS / 9 FAIL** — its nine recorded failures exactly |
| `epsilon` `heldout/RUN-ALL` | **163 PASS / 4 FAIL** — exactly its recorded figures |
| `zeta` `heldout/RUN-ALL` | **135 PASS / 2 FAIL** — exactly its recorded figures |
| `r1-preservation` `heldout/RUN-ALL`, including the four unedited prior R1 suites | **40/1** for its own suite (p1 13/0, p2 9/0, p3 10/1, p6 8/0) and AR-0027 26/3, AR-0029 26/2, AR-0031 27/7, AR-0033 30/1 — every per-binary figure exactly |
| `oracle-format` crosswalk and attack matrix | 35 bullets + 5 statements → existing, required, typed fields, 0 problems; 93 samples, 93 as expected, 0 unexpected |

Beyond re-running, I established from scratch, in my own probe projects and without relying on any verifier's harness:
the candidate identity (AC-9); the contract-binding chain by my own line accounting **without using the product**
(AC-13); the suite-to-contract matrix from the product, fed with my own run logs (AC-10); the G1/G5 tier coverage
(AC-5); `cargo test --lib` and `cargo test --test certification` (AC-15); and an end-to-end cross-family chain
K3/K4 → W8 → D1 → W6 → W4/W10 → O4 → G0/W12 → L4 (AC-16).

**Independence caveats I weighed.** Two verifiers (P2-AR-0044, P2-AR-0049) each listed the harness task-output
directory once, reading no other agent's output, and P2-AR-0048 provisioned a trust anchor in the real machine's
shared state before isolating `XDG_STATE_HOME` and moved both files aside (`rm` being denied), returning that
directory to its prior empty `UNPROVISIONED` posture; the orchestrator verified it cleared. None of the three
touches the evidence I rely on, and I re-ran all of it on a clean machine state of my own, so each is disclosed
rather than load-bearing. P2-AR-0048 did not run the certification suite; AC-15 is mine and I ran it.

### 2.1 The one discrepancy I found in re-running, and its resolution

In my first beta run, `C1-transactions` failed (`transaction CIT-0001 not listed`) — a failure P2-AR-0047 did not
record. I re-ran `t-C1-deterministic-memory.sh` alone: **17 passed, 0 failed**, including that check, and I
reproduced `cit propose` → `cit list` by hand in a fresh project, where CIT-0001 is listed. The first run had six
held-out suites and a certification build in flight at once. It is a load artefact, not product behaviour, and
beta's C1 status stands. I record it because it was in my logs.

## 3. AC-1 … AC-16

| AC | Verdict | Basis |
|---|---|---|
| **AC-1** | **HOLDS** | I parsed the owner source myself: **101 capabilities** (A1–A5, B1–B3, C1–C10, D1–D6, E1–E4, F1–F5, G1–G2, H1–H4, I1–I4, J1–J2, K1–K4, L1–L4, M1–M4, N1–N4, O1–O5, P1–P2, Q1–Q4, R1–R3, S1–S6, T1–T3, **U**, V1–V4, W1–W12) carrying **687** capability checklist bullets. Gate U has no numbered heading and is in the universe (frozen §9.4). The union of the six families is exactly those 101, with no capability twice and none missing; every one has a status and an evidence location in `capability-status-matrix.yaml`. The compiled view and evidence map independently carry 101. |
| **AC-2** | **HOLDS** | No capability is `ABSENT` or `UNCLEAR`: 73 `PRESENT_AND_SUBSTANTIAL`, 28 `PARTIAL`, 0 `ABSENT`, 0 `UNCLEAR`, 0 `N/A_WITH_REASON`. Eleven bullets inside PARTIAL capabilities are `ABSENT` (C8×4, C10×2, E2, F1, M1, M4×2), which §4's granularity rule makes those capabilities `PARTIAL`, not `ABSENT`. Because no capability is recorded `N/A_WITH_REASON`, every one is "required" and every one is graded. |
| **AC-3** | **FAILS** | Eight of the 28 `PARTIAL` capabilities are argued `COULD_UNDERMINE` the advanced-qualification scenario: **A1** (my correction), **S4**, **S5**, **C8**, **F3**, **F4**, **O5**, **U**. Frozen §3: "A `PARTIAL` whose gap could invalidate qualification fails AC-3." Each argument is anchored in the owner source's own challenge text or V4's own metrics — §4 below. The remaining 20 PARTIALs each carry an explicit justification and an argued `CANNOT_UNDERMINE`, which I checked against V4:1049–1060 and the stated per-gate challenges and accept. |
| **AC-4** | **FAILS** | A2 (the first `POST_VERIFICATION_HARDENING` capability) is `PRESENT_AND_SUBSTANTIAL`, all ten bullets established, and the R1 acceptance it rests on is still valid (AC-14). **F4 (the second) is `PARTIAL` and argued `COULD_UNDERMINE`**, on three confirmed blocking findings: V1-F4-01 (BC-P2-53), V1-F3-01 (BC-P2-41), V1-F4-02 (BC-P2-45). F4's plugin half is in good order; the tool-installation half OD-P2-03 brought inside it is not. AC-4 asks whether those capabilities are *incorporated*; one of the two is not. |
| **AC-5** | **FAILS** | Established by exercising the scheduler, not reading it. Ten of the twelve AC-5 behaviours are **met** and I saw them: impacted-test selection (18 of 39 for a one-line comment; a different 28 for a decision change), parallel execution (4 workers, 2338 ms wall against 5772 ms of executed check time), safe isolation, cache reuse (32 of 39), cache invalidation, stale evidence, RED/YELLOW/GREEN, hard-block vs warning over all 74 catalogue entries, remediation generation, and it does **not** serially re-run the whole suite for a trivial mutation. Two are **not met**, from one cause: **health-result provenance** and the **G5 tier duty**. In my own probe project `gov health run --tier G5` evaluated **39 of the 74** checks the catalogue declares at G5 and wrote a health result reading `complete: true, executed: 39, not_evaluated: 0`; `--tier G1` evaluated 18 of 49 with the same claim; D001–D035 appear in neither and run only under `gov doctor`. A tier that claims completeness over a third of its declared membership it never evaluated does not meet AC-5. (`E-O5-01`, BC-P2-07.) |
| **AC-6** | **HOLDS** | A machine-checkable format covering V1–V4 exists (`framework/qualification-oracle/qualification-oracle.schema.json`, `format_sha256` `f89a3e2ff882e116f4593d0f7b8fd9725c7ba491090aedadc3a942c66f4316fd`, which I recomputed and which `gov oracle format` reports), and it **is accepted by a fresh independent reviewer in this phase** — P2-AR-0045, verdict `ORACLE_FORMAT_ACCEPTED`. I re-ran the two checks the acceptance rests on: the crosswalk against the **owner-source bytes** resolves all 35 Gate V bullets and 5 prose statements to existing, *required*, *typed* fields (0 problems), and the 93-sample attack matrix is 93 as expected, 0 unexpected. No hidden fault was generated in Phase 2; the format's own status field still reads `PROPOSED`, which frozen §9.2 places outside the file, in P2-AR-0045's report. |
| **AC-7** | **HOLDS** | Frozen §9.1's reconciliation: an executable, evidenced path to a provisional retrieval profile. P2-AR-0047 established D4's ten components separately identifiable with an out-of-band swap reported `UNGOVERNED`/high, and D5's full governed chain — benchmark → Human Decision Gate → owner-signed answer → pin → complete re-index → recorded regression, with automatic rollback. Reproduced in my beta re-run (`t-D4-D5-AC7-retrieval-profile.sh`, one failure, and it is V1-BETA-03, not the path). Phase 3 can earn `PROVISIONAL_RETRIEVAL_PROFILE_READY` on this candidate. V1-BETA-03 — the generated held-out set leaves its semantic queries pending, so the evidence cannot discriminate the embedder — is non-blocking here and is a Phase-3 input I flag in `later-lifecycle-notes.md`. |
| **AC-8** | **HOLDS** | `artifact-flow-coverage-matrix.yaml`, rebuilt by P2-AR-0051 on this candidate: 15 rows, all eleven columns. I carried it forward **verified**: its whole suite reproduced at 135/2, and I re-checked each of AC-8's three rejection conditions myself. Semantic retrieval is not relied on to rediscover mandatory inputs (`W3-09`: resolution byte-identical with the index removed; W10 01–05b). Stale versions cannot silently satisfy downstream work (W6-01…W6-09c, and my own chain: after a direct change the dependent task reads `stale: true, retest_required: true` with both hashes and the delivered packet stops verifying). Completion traces to upstream evidence (W5-09, W5-09b). |
| **AC-9** | **HOLDS** | §1. Commit, tag, both digests verified at the tag and at `HEAD`. One INFO note carried from two verifiers: `product_identity.py <annotated tag>` prints the tag-object id on its `commit:` line; both digests are correct, so it is not a STOP, and it is orchestration tooling, not product source. |
| **AC-10** | **HOLDS** | Regenerated **with the product** after `gov contract verify` → `CONTRACT_SOURCE_BOUND`, and fed with my own run logs. **101 capabilities, 798 evidence owners, 0 capabilities with zero owners, 0 owners that fail to resolve against the product.** Sampling owners per gate: every one of the 101 has at least one owner I observed running — 127 executed at G5, 34 under `gov doctor`, 477 cargo tests I ran, 110 independent-verification obligations discharged by this verification. Invalidation is **shown**, not assumed: the currency key carries 31–32 input classes, and changing one at a time invalidates prior green evidence naming that class — nine classes by epsilon, four by alpha, four by beta, three by gamma, and five in my own chain. *Recorded, not fatal:* the doctor-kind owners declare tiers G1/G5 but are never evaluated by a tier run; they do run, so AC-10 is met, and the wrong tier declaration is E-O5-01 under AC-5. 126 of 713 checklist items name no automated check and `severity` is null for all 101 — `S1-AC13-01`, non-blocking, because AC-10 is capability-level and every capability has a running owner. |
| **AC-11** | **HOLDS** | `qualification-coverage-matrix.yaml`: all 101 capabilities carry a Repo A challenge, a Repo B challenge, a hidden-oracle fault class, and a chaos/scale/soak and a retrieval entry (or a stated "not relevant: reason"). No row is incomplete and no capability needed the not-challengeable route. |
| **AC-12** | **HOLDS** | Every capability status rests on a held-out probe an independent verifier wrote and that I re-ran on this exact candidate; all pinned identities verify at the tag and at `HEAD`; freshness is demonstrated per family and by me. Builder evidence is used as regression evidence only: the 276 lib and 207 certification tests are cited as O3 regression, and no capability status here rests on them. The three protocol deviations are disclosed in §2 and none is load-bearing. |
| **AC-13** | **HOLDS** | The canonical import is **byte-identical** to the owner source (`cmp`) and both hash to `4c2df291…5ed3`. The compiled form is a line-accounting compiler's output, and I checked its coverage rule **without using the product**: of the owner source's 1255 lines, 1026 are non-blank and not `---`, and **all 1026 are carried verbatim, exactly once — 0 missing, 0 extra, 0 without a verbatim carrier**; `capability_count` is 101 including Gate U with its 28 items; 713 capability checklist items + 9 acceptance-gate items = the source's own 722 checklist lines; O5 is correctly `EXECUTION_REFINEMENT` and A2/F4 `POST_VERIFICATION_HARDENING`. `gov contract verify` returns `CONTRACT_SOURCE_BOUND`, and its declared checks now include an **independent** line accounting against the source text rather than equality with a fresh run of the same compiler — which was BC-P2-01's self-referential half. S0-AC13-01, A0-O1-03, A0-O5-14 and A0-U-03 are closed by my own evidence. |
| **AC-14** | **HOLDS** | The candidate's `product_code_digest` differs from `srr1-r1-accepted` (`bd4d65d9…0547`), so AC-14 is required. P2-AR-0044 re-ran all four prior R1 held-out suites **unedited** (byte identity asserted by `cmp`) and adjudicated the twelve frozen R1 items over a 204-file, +116 505-line delta, verdict `R1_PRESERVED`. **I re-ran its whole suite** and reproduced every per-binary figure exactly, and the OWNER-DECISION-0006 §6 census re-derived at 123 files / 2392 functions with **zero violations in all three splitter configurations**. The single new failure, `hv_a::a1`, pins file and function counts on a tree 3.2× larger and its property holds. `ROT_PHASE1_CANDIDATE_ACCEPTED_R1` remains valid for this candidate; it is not re-issued here. |
| **AC-15** | **HOLDS** | Run by me in this worktree on this candidate: `cargo test --lib` **276 passed, 0 failed**; `cargo test --test certification` **207 passed, 0 failed** (1274.6 s). `evidence/AC-15-regression.out`. |
| **AC-16** | **HOLDS** | Every listed interaction exercised end to end, across family boundaries. **W12 ↔ G0–G6**: 13 of 14 checks pass (the one failure is a preview surface, A1-W12-01; the enforcing gate is correct). **O4/W6**: nine input classes one at a time. **K2 ↔ D1 ↔ W6**: my own chain — a CIT-E impact simulation reaching the dependent task at hop 1 `via CONSUMES → REQ-0001` at radius R2, then an index rebuild propagating staleness with `propagated: true`, the delivered packet failing to verify, and the green record going obsolete naming five classes. **N ↔ W9**: W9-01…W9-06c and delta's checkpoint probes. **L3 ↔ E1**: OD-P2-01 attacked nine ways, every one refused typed. **S3/S4/S5 ↔ A2**: every lifecycle ingress through the one verifier (the seam is V1-S5-01, counted under AC-3). **U ↔ O5**: 14 of 15 SLOs crossed, each moving the health state. **Cross-machine (P2-ADJ-0002)**: 74/74 across five machine postures, plus delta's X2.1–X2.10 and the R1 suite's two-machine positive control. **Availability rule across scheduler, task, CIT, gate and update hosts**: 15/15 and delta's X1.1–X1.7, and in my own chain `task dag`, `health status`, `status`, `doctor`, an independent `task create` and the remedy `rebuild-memory` all stayed available under a block. |

**Not met: AC-3, AC-4, AC-5.** Met: AC-1, AC-2, AC-6, AC-7, AC-8, AC-9, AC-10, AC-11, AC-12, AC-13, AC-14, AC-15, AC-16.

## 4. The eight blocking findings

All seven raised by the family verifiers are **CONFIRMED**, each reproduced by me; none is refuted. One is mine.

| Id | Cap | Sev | AC | Class | What it is |
|---|---|---|---|---|---|
| **V1-F4-01** | F4, F3 | HIGH | AC-4, AC-3 | **BC-P2-53** (new) | An interpreter-wrapped install command evades every authority-expansion trigger, and a command the OS cannot read is recorded as fully evaluated |
| **V1-F3-01** | F3, F4 | HIGH | AC-4, AC-3 | BC-P2-41 | The governed security review is bound to a tool id and version, not to the installation it authorises |
| **V1-F4-02** | F4, F3, E1 | HIGH | AC-4, AC-3 | BC-P2-45 | The authorised side of the envelope is an unprotected project overlay file |
| **S1-A1-01** *(mine)* | A1, F4, F3 | MEDIUM | AC-3 | BC-P2-45 | Authority- and sensitivity-bearing overlay documents are never visited by POLICY_PRECEDENCE, so its deny-by-default never reaches them |
| **V1-S4-01** | S4 | HIGH | AC-3 | BC-P2-33 | A6 is hard-blocked on a brownfield tree whose secret-bearing files A2 itself classified SECRET |
| **V1-S5-01** | S5, A2 | MEDIUM | AC-3 | BC-P2-37 | `gov update` answers "already up to date", `ok: true`, from the source's own unauthenticated declared version |
| **V1-BETA-01** | C8 | MEDIUM | AC-3 | BC-P2-32 | Four of the seven failure classes have a record shape and no writer |
| **E-O5-01** | O5, U | MEDIUM | AC-5 | BC-P2-07 | A tier run never executes the 35 doctor checks its own catalogue declares at G1 and G5, yet reports the run complete with nothing unevaluated |

### 4.1 The two judgements a synthesis verifier had to make

**V1-S5-01, which P2-AR-0046 explicitly flagged as weighable differently.** The exposure is narrow: nothing is
installed, `framework.lock` is unchanged, and the defect is the affirmative report. What settles it is
**Contract v3:154** — A2's own advanced-qualification challenge is *"tampered source payload, stale/forged manifest,
wrong key, altered security policy, modified migration, downgrade/replay attempt, interrupted install"*. The probe
tampers a payload and alters a security policy while keeping the declared version; the product answers `ok: true`
with no refusal. A hidden fault of exactly the class the contract names for this capability would score as
undetected. AC-3 unmet for S5. Confirmed blocking.

**Delta's M1 label, which I corrected.** P2-AR-0049 recorded M1's `partial_qualification_impact` opening
`COULD_UNDERMINE only for a qualification design that scores cost or determinism of routing` while recording its
finding `blocking: false` — a contradiction, since a PARTIAL argued COULD_UNDERMINE fails AC-3. I corrected the
**label**, not the verdict: none of V4's twelve scored metrics (Contract v3:1049–1060) is cost or routing
determinism, and M1 carries no advanced-qualification challenge in the owner source, so the gap cannot invalidate
the scenario as Contract v3 scopes it. **CANNOT_UNDERMINE.** delta's `blocking: false` was right.

### 4.2 My own finding, and the status I corrected

`S1-A1-01`. P2-AR-0046 graded **A1 `PRESENT_AND_SUBSTANTIAL` 6/6**, with bullet-2 and bullet-6 evidence drawn from
MODEL_ROUTING_OVERRIDES and SECURITY_POLICY. P2-AR-0048, in another family, demonstrated that a hand edit of
`governance/project/TOOL_PERMISSIONS.yaml` — no `gov` command, no transaction, no gate — turns a gated installation
into an ungated one, with `gov audit` silent. Both are right about what they ran; neither could see that they
contradict. Reading the code: `policy_precedence::evaluate_overlay` is reached for exactly two documents
(`runtime/src/policy.rs:295, :340`) under a comment claiming *"every project overlay input is subject to
POLICY_PRECEDENCE"* (`:285`), while `tools::role_permissions` reads TOOL_PERMISSIONS.yaml straight from the overlay
(`runtime/src/tools.rs:66-78`), and POLICY_PRECEDENCE declares rules for sixteen documents and none of the three
OD-P2-03 envelope sources. Its own deny-by-default cannot deny what the evaluator never visits.

So **I correct A1 to `PARTIAL`, `COULD_UNDERMINE`** — Contract v3:140 makes *"attempted authority/sensitivity
weakening"* A1's own advanced-qualification challenge. I claim the coverage gap for all three documents and the
**exploit for one**: my attempt to show an effective weakening through DATA_SENSITIVITY.yaml was inconclusive
(D011 read `none` both before and after), and I say so rather than assert the stronger claim.

## 5. Convergence (frozen §8)

| | |
|---|---|
| Iteration-0 classes | **52** |
| `CLOSED` | **37** |
| `PARTIALLY_CLOSED` | **14** |
| `RESIDUAL` | **1** (BC-P2-32, failure memory — the only class with nothing closed) |
| Still leaving an acceptance criterion unmet | BC-P2-07, BC-P2-32, BC-P2-33, BC-P2-37, BC-P2-41, BC-P2-45 |
| New blocker classes | **BC-P2-53** |
| `introduces_materially_new_blocker_classes` | **true** |

Per-class evidence is in `convergence.yaml`. Of the 193 iteration-0 findings the verifiers disposed, 142 are
`CLOSED`, 43 `RESIDUAL`, 8 `NOT_APPLICABLE`; one — `S0-AC13-01` — no family owned, and I closed it myself under
AC-13.

**BC-P2-53** is the one materially-new blocker class: `installation_authority` derives what an installation would
hold by scanning each argv **element** literally, so one interpreter argument hides sudo, host authority, an
absolute path and a policy write, and `undetermined` is pushed only when the descriptor carries no command at all.
I verified the label in the direction that would have avoided escalation, and it holds: `installation_authority`,
`authority_expansion_triggers`, `installation_envelope` and `CHANGE_POLICY.change_classes.tool_installation` have
**zero occurrences at `cap2-candidate-0`**. The whole surface was built during this repair iteration under
OD-P2-03. Its adjacency to BC-P2-39 is real and P2-AR-0048 recorded it rather than claiming distance; BC-P2-39's
own inventoried mechanism — the **plugin** authorize/register path trusting the descriptor's declared fields — is
closed on this candidate. Shading a mechanism that did not exist into a closed class to keep the count at zero
would be the relabelling §8 forbids.

Ten further findings are labelled `MATERIALLY_NEW` and **none of them blocks**, so none forms a class: the six
oracle-format findings (all `PROPOSES_STRONGER_LATER_ASSURANCE`, five at lifecycle P4), `V1-BETA-08`,
`A1-W12-01`, `V1-R1P-01` and `V1-R1P-02`. I confirmed each label.

**On the convergence rule.** Iteration 0 *established* the inventory rather than introducing classes into it, so
this is the first iteration that can count toward §8's three-consecutive-iterations rule. **One of three.** No
escalation follows from this verification; the count is the orchestrator's to keep.

**A note on labelling practice.** P2-AR-0050 flagged an ambiguity honestly: the inventory contains blocking classes
only, so a non-blocking finding cannot name one, and it chose `RESIDUAL` with `inventoried_class: null` plus the
iteration-0 finding each restates, rather than labelling three non-blocking findings `MATERIALLY_NEW` on a
technicality. That is the right call — the alternative would misstate convergence — and several other verifiers did
the same. I confirm it.

## 6. What I could not establish

Stated plainly, because a verification is worth only as much as its boundaries.

1. **The G2 close gate refusing on a stale input, in my own chain.** My AC-16 chain established staleness
   propagation, packet invalidation, currency loss and the G0 re-evaluation, but its implementation task stayed
   `BLOCKED` on readiness (correct H3/I1 behaviour) so I could not claim and close it. The property itself is
   established by two independent probes I re-ran — beta's `D1-b6-stale-close` and zeta's `W6-09c` and `W12-G2` —
   not by my own end-to-end close.
2. **An effective weakening through REPOSITORY_CONTRACT.yaml or DATA_SENSITIVITY.yaml.** I established that both are
   outside `evaluate_overlay` (code and `gov policy overrides`), not that a weakening of either takes effect.
   `S1-A1-01` claims the coverage gap for three documents and the exploit for one.
3. **A full signed-release install of my own.** Like P2-AR-0044, I did not mint a signed release payload and install
   it; the lifecycle-ingress half of AC-16 rests on alpha's suite (which I re-ran) and the prior R1 suites, not on
   an end-to-end signed install I performed.
4. **The 50 evidence owners my supplied logs did not cover** (13 held-out, 19 G0, 13 human-gate, 5 release). They
   resolve against the product and the families exercised them; I did not feed every family's log into the matrix,
   only alpha's. Every capability still has at least one owner I observed running.
5. **R2, R3, public-cloud and Phase-3/4 material** — outside this gate by frozen §7; see `later-lifecycle-notes.md`.

## 7. Outputs

| File | Contents |
|---|---|
| `00-SYNTHESIS-REPORT.md` | this report |
| `capability-status-matrix.yaml` | 101 capabilities: my final status, the family's, bullet counts, evidence location, blocking finding ids, and my corrections |
| `suite-to-contract-matrix.yaml` | AC-10: 798 evidence owners, their tiers, whether each resolves and whether I observed it run |
| `qualification-coverage-matrix.yaml` | AC-11: Repo A / Repo B / hidden-oracle fault class / chaos-scale-soak / retrieval per capability |
| `artifact-flow-coverage-matrix.yaml` | AC-8: carried forward from P2-AR-0051, verified, with my re-check of all three rejection conditions |
| `blocker-classes.yaml` | the 52 iteration-0 classes with their iteration-1 state and evidence, plus BC-P2-53 |
| `convergence.yaml` | per-class `CLOSED`/`RESIDUAL`/`PARTIALLY_CLOSED`, the new class, and `introduces_materially_new_blocker_classes: true` |
| `findings.yaml` | my three findings, and my disposition of all 55 verifier findings |
| `repair-delta.md` | what must become true, per blocker class, with its normative source and the acceptance evidence a later verifier will demand |
| `owner-decisions-required.md` | **none** — with the reasoning for the one candidate that was flagged |
| `later-lifecycle-notes.md` | what is real but belongs to Phase 3, Phase 4, R2, R3, adoption or operations |
| `evidence/` | every re-run log, the AC-13 independent checker and its output, the AC-10 matrix with my runs, the AC-5 tier evidence, the AC-16 chain, the AC-15 regression |
