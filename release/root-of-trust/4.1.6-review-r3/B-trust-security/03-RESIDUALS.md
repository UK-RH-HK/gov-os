# 03 — Residual determination (review r3 B, trust and security)

Revision under review: RoT-1 revision 3 at `ca77a431418bd6b349f465aa2521ca43bccfd5a6`.

## 1. Acceptance criteria

A declared residual is accepted only when **one** of the following holds. Documentation alone is never a bound.

| Criterion | Test |
|---|---|
| **RC-1 Excluded trigger** | The trigger needs a capability that the production trust model explicitly excludes, and the exclusion holds in the deployment the architecture itself prescribes for that machine class. |
| **RC-2 Unavoidable and correctly bounded** | All five of these hold: (a) no design reasonable under the chosen assumptions removes or bounds it; (b) the bound is stated exactly; (c) the verdict surface never presents the residual state as a stronger one; (d) an acceptance test fails when the bound is exceeded; (e) the bound does not rest on an assumption the architecture violates elsewhere. |

Determinations use **ACCEPTED**, **ACCEPTED WITH CONDITION** (a named carried requirement in `04` must hold), or **NOT ACCEPTED** (a finding in `01`).

## 2. Freshness residuals (`24` §10, `20` §10)

| ID | Residual as declared | Tested by | Determination |
|---|---|---|---|
| RS-1 | A machine that never receives newer metadata cannot know it exists. The declared bound is the compiled T0, raised by a retained anchor or pin and by any witness. The pack also claims no governed mutation on an unanchored machine under OP-7 (a)–(c), and that "(a) … makes the review's B5 class impossible on every machine". | RV3-B-M model: B5, A02, A06, A12 and the 132-row machine matrix | **NOT ACCEPTED as stated.** The unavoidable core is agreed. RC-2 fails on (b), (c) and (a). (b): the "impossible on every machine" claim is false for pinned CI runners whose pin predates the newest trust state (A02). (c): `ANCHORED` permits the `current` label at any anchor age. (a): OP-7 (b) or a pin currency rule bounds it. In addition, under the `24` §4.1 definition `BELOW_ANCHOR(have n < e)`, a trust-state key presenting a higher TSS that omits the anchored one satisfies a current anchor it does not hold (A12). → **RV3-B-H2** |
| RS-2 | OP-3 mode B and OP-7 (b)/(c) trust the local clock. | A07 | **ACCEPTED WITH CONDITION CR-06.** Clock trust is an owner option with TA-7 stated. The clock-rollback high-water, however, is raised by any verified statement's `issued_at`. One far-future value from a low-custody key permanently disables mode B and OP-7 (b)/(c) on every VTS that ingests it (RV3-B-M3). |
| RS-3 | A3 deletes or rewrites its own VTS; A3 can forge a local anchor or confirmation. | A03 (executed), A04 | Deletion: **ACCEPTED** under RC-1, because the machine becomes `UNANCHORED` and fails closed. Forging: **ACCEPTED WITH CONDITION CR-03** for interactive developer machines only. On CI runners, which `24` §5.2 prescribes as pin consumers, repository-controlled code runs in the pin-reading account. The real 4.1.5 `gov verify product` ran an A2-committed command that wrote both pin files (A03), so RC-1 does not hold there. → **RV3-B-M2** |
| RS-4 | A pin provisioned by a party the repository writer controls. | A03 | **ACCEPTED as a scoping statement only.** It covers who provisions the pin, not who can rewrite it afterwards. The rewrite case is RS-3 above. |
| RR-2 | On a machine without a per-project record, an A2-delivered older eligible release is accepted as installed content. An anchored machine "judges the release at its anchor epoch". | A02, A12, matrix | **NOT ACCEPTED as stated.** "At its anchor epoch" holds only if an anchor is satisfied by the anchored statement being held and chained. A12 shows it is not under the literal definition. Under (a) the anchor epoch has no currency bound. → **RV3-B-H2** |
| RR-1 | Automatic rollback may leave an ineligible installation. | reading | **ACCEPTED** (RC-2: fails closed; remedy stated). |
| RR-3 | A3 deletes the per-project record or VTS. | reading | **ACCEPTED** (RC-1; the machine becomes `UNANCHORED`). |
| OP-7 (d) residual | Under (d), a repository writer selects older genuine state for governed use on unanchored machines. | matrix (d) rows | **ACCEPTED as an owner-selectable residual.** It is stated, labelled `FRESHNESS_UNPROVEN`, the `current` label is not permitted, and C3 is refused. In the matrix, every unanchored (d) row refuses C3 ingestion of the revoked release. |

## 3. Constitutional-surface residuals (`23` §10)

| ID | Residual as declared | Tested by | Determination |
|---|---|---|---|
| CS-1 | Each classification's correctness is a root-ceremony review responsibility. Classifying too weakly is limited by the lint ("never weaker than precedence"; no catch-alls; `informational` never read by a security decision point). | A01 (executed), A16 | **NOT ACCEPTED as the sole bound.** The lint's anchor, the `23` §4 precedence order, is unsound for the project layer: `immutable` is treated as strongest although it refuses project strengthening. A kernel that only moves rules to `immutable` passes the checker and discards project strengthening on the real 4.1.5 binary (A01) → **RV3-B-H1**. In addition, the inventory classifies keys read by `23` §6.5 decision points as `project_tunable`, and the lint accepts them (A16) → **RV3-B-L2**. |
| CS-2 | Every final release that changes pinned content needs a root-threshold TPS. | reading | **ACCEPTED** (operational cost; `14` RK-17). |

## 4. Binary and TCB residuals (`25` §9)

| ID | Residual as declared | Tested by | Determination |
|---|---|---|---|
| TB-1 | The binary remains the TCB; running an unverified binary is outside the chain. | reading | **ACCEPTED** (RC-1, TA-1). |
| TB-2 | The reproducible-build attestation trusts the rebuilder's environment. | A08 | **ACCEPTED only for what it bounds**: binary bytes equal a build of `source_commit`. It does not bound *which* source is built. That choice rests on `release-final` (threshold 1) through `release_commit`, which V8 does not tie to the verified candidate's commit (A08) → **RV3-B-H3**. |
| TB-3 | Compromise of `release-artifact` ×2 + `build-attestation` + `trust-state` is required for a malicious binary. | A08 | **NOT ACCEPTED as stated.** Under the rules as written, one `release-final` key plus control of the release-pipeline input (the review r2 H3 adversary) reaches an accepted malicious binary. The other three purposes sign after checks that never test source legitimacy. → **RV3-B-H3** |

## 5. Verify-and-use, legacy and gate residuals

| ID | Residual as declared | Determination |
|---|---|---|
| VR-1 | A3 modifies installed files between units of work | **ACCEPTED** for this review's scope (VU-11, RT-86). Not attacked in depth: compatibility and transactions are reviewer C's scope. |
| VR-2 | A3 ignores advisory locks | **ACCEPTED** (refusals only). |
| VR-3 | Non-`gov` subprocesses write PPS, overlay, records or the VTS | PPS detection by the next unit of work: **ACCEPTED**. Repository records never authorising trust decisions: **ACCEPTED** (P2 flips in the RV3-B model). Overlay detection by the strength vector: **NOT ACCEPTED as complete**. The vector is computed from the overlay, so a kernel-side precedence change removes applied project strengthening with the overlay unchanged (A01, RV3-B-H1). Migration operations can also write overlay content outside the four computed-weakening categories (RV3-B-M5). VTS and pins: see RS-3 (RV3-B-M2). |
| VR-4 | Plugin runtimes and model files consumed by path | **ACCEPTED** (unchanged from revision 2; not attacked). |
| LR-1…LR-4 | Legacy-binary residuals | **Not judged beyond trust aspects.** The P3r3 matrix is reviewer C's scope and was not re-executed by B. LR-4 (fresh clones accept the repository overlay): **ACCEPTED** as T4 authority of A2. |
| TG-1 | A trust decision on one machine does not authorise another | **ACCEPTED** (by design). |
| TG-2 | A3 can write the VTS or drive a pseudo-terminal | **ACCEPTED WITH CONDITION CR-03** for developer machines. Operator decision pins are the architecture's automation path. They are plain account files, and an agent tool call, plugin or `gov`-run repository command can write them (A03, A04). `27` §3.3 ("MUST NOT be answerable … by any agent path") therefore holds only for the `gov decide` path. → **RV3-B-M2** |
| TG-3 | Non-trust gates stay forgeable by A2 | **ACCEPTED** (RC-1 for trust facts). Plugin registration and tool installation, both governed by non-trust gates, give same-account code execution; that is the RS-3/TG-2 surface (RV3-B-M2). |

## 6. Summary

| Determination | Residuals |
|---|---|
| NOT ACCEPTED (finding) | RS-1, RR-2 (H2); CS-1 (H1, L2); TB-3 and the TB-2 scope (H3); VR-3 overlay completeness (H1, M5) |
| ACCEPTED WITH CONDITION | RS-2 (CR-06), RS-3 forging on developer machines (CR-03), TG-2 (CR-03) |
| ACCEPTED | RS-3 deletion, RS-4 (scoping), RR-1, RR-3, OP-7 (d), CS-2, TB-1, VR-1, VR-2, VR-4, TG-1, TG-3, LR-4 |
| Not judged by B | LR-1…LR-3 (reviewer C scope) |
