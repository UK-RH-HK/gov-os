# P2-AR-0051 — Phase 2 verification iteration 1, capability family `zeta` (Gate W, W1–W12)

| Field | Value |
|---|---|
| Run | **P2-AR-0051** — fresh independent capability family verifier |
| Family | `zeta` — W1–W12, Artifact Flow, Dependency Consumption and End-to-End Traceability |
| Candidate | `cap2-candidate-1` |
| Verdict | **FAMILY_VERIFICATION_COMPLETE** |
| Blocking findings | **0** |
| AC-8 determination | **MET** against all three rejection conditions |
| Branch / worktree | `phase2/verify-1-zeta`, `scratchpad/wt/p2-verify1-zeta` |

I authored none of the implementation, none of its tests, none of the iteration-0 audits, none of the
repairs, and no Phase-1 role. I verified; I did not repair. I do not issue the Phase-2 verdict.

---

## 1. Pinned inputs — all verified, no STOP

| Input | Expected | Observed | |
|---|---|---|---|
| `cap2-candidate-1` | `0bad524d836f179964ffbac31972856ea6434682` | `git rev-list -n1 cap2-candidate-1` → `0bad524d836f179964ffbac31972856ea6434682` | ✔ |
| `product_code_digest` at `HEAD` | `e6332fc7…2220` | `product_identity.py HEAD` → `e6332fc7d5af5c73adbe0f200003db30fe5a6fd0b7f24d047d3e340e6f972220` | ✔ |
| `governed_state_digest` at `HEAD` | `3d2aeba2…20c0` | `product_identity.py HEAD` → `3d2aeba2fc3b52a95c369c49a854bb9d443b0b03da1180db5339f01d892620c0` | ✔ |
| worktree `HEAD` | later orchestration commit | `8588813ec1ef9c832879e258ca5acfb573ae996f`, with `0bad524` an ancestor and both digests identical to the tag's | ✔ |
| Contract v3 | `4c2df291…5ed3` | `sha256sum Governance_OS_Capability_Acceptance_Contract_v3.md` → `4c2df29115c8d5389034b2e2d817772add80d61678807c23e0d520c937cb5ed3` | ✔ |
| Frozen gate contract | `d2f33e89…f25e` | `sha256sum …/PHASE-2-FROZEN-GATE-CONTRACT.md` → `d2f33e89d5459dd809e17271e46854cc886ed958ca63f89765e16d6a26a9f25e` | ✔ |
| Governing documents | three at the repository root | present; SHAs recorded in `evidence/00-pinned-inputs.out` | ✔ |
| Decisions in force | OD-P2-01, OD-P2-02, OD-P2-03, P2-ADJ-0001/0002/0003 | read and applied as sources | ✔ |

One thing worth recording so a reader is not misled: `cap2-candidate-1` is an **annotated** tag, so
`product_identity.py cap2-candidate-1` echoes the tag object id `f75eb7db…`. The tag dereferences to
`0bad524d836f179964ffbac31972856ea6434682` (`git rev-parse cap2-candidate-1^{commit}`) and both
digests are identical to the dispatch's. No mismatch; no STOP.

The audit universe was established from the **owner source** (Contract v3:1066–1194), not from the
compiled YAML or the evidence map. Gate W has **86 checklist bullets** across W1–W12 (confirmed by
counting `- [ ]` lines in the owner source, and matched by the evidence map's 86 Gate-W rows); each
was evaluated individually.

## 2. Method

A **full re-audit**. No iteration-0 status was adopted; the iteration-0 statements were read only to
know what to attack, and every disposition in `prior-findings-disposition.yaml` rests on evidence
produced here, on this candidate.

* **Held-out probes I wrote**: `heldout/` — `lib.py` plus thirteen probe files and `RUN-ALL`, which
  re-runs them all and prints one PASS/FAIL line per check. They were written from the contract text
  and the product's observable CLI behaviour; no builder test, builder probe or audit-of-record probe
  was copied. They never enter the product tree. Each probe builds its own disposable governed
  repository (`gov init` of the binary's embedded payload, admitted on an unprovisioned machine by
  OWNER-DECISION-P2-0002) on its own simulated machine (`XDG_STATE_HOME`).
* **Green baselines are legitimately green** (P2-ADJ-0003 §2). `lib.seed_green` builds the whole
  Contract v3 H4 chain — feature with all 26 readiness cells, scenario, data requirement and test
  dataset registered through `gov data register` so the OS records their authorship, and an
  acceptance test obligation and its test file authored by an **independent session** through a
  governed test-design task that closes with a valid consumption receipt. The product refuses the
  shortcut: a test obligation that merely *asserts* `independent_of_implementer: true` is rejected
  as its own claim rather than evidence, and `tests.status: passed` is refused unless a product test
  actually ran. Both refusals are recorded as observations in favour of the product.
* **Builder evidence is regression evidence only** (O3). `cargo test --lib`: **276 passed, 0 failed**.
  `cargo test --test certification`: **207 passed, 0 failed** (`evidence/cargo-lib.out`,
  `evidence/cargo-certification.out`). The certification run completed after the evidence commit and
  was recorded in a follow-up commit; the note in that file gives the full history.
* **Counts.** 137 held-out checks across the thirteen probes; 135 PASS, 2 FAIL. Each FAIL is a
  recorded finding (W3-04 → A1-W3-01; W12-G2b → A1-W12-01). The W8.5 gap is recorded as
  A1-W8-01 from the passing W8-05/W8-05b pair, whose recorded detail shows what is and is not covered.

## 3. Per-capability result

| Capability | Status | Bullets | Held-out checks | Findings |
|---|---|---|---|---|
| W1 Stable artefact identity | `PRESENT_AND_SUBSTANTIAL` | 9/9 | W1-01…W1-10, W1b-01…W1b-05 (16) | A1-W-01 |
| W2 Typed output → input contracts | `PRESENT_AND_SUBSTANTIAL` | 8/8 | W2-01…W2-08 (10) | A1-W-01 |
| W3 Mandatory task-input manifest | **`PARTIAL`** | 8/9 | W3-01…W3-09 (12) | **A1-W3-01**, A1-W-01 |
| W4 Context compiler delivery proof | `PRESENT_AND_SUBSTANTIAL` | 6/6 | W4-01…W4-06b (11) | A1-W4-01, A1-W-01 |
| W5 Consumption receipt & traceability | `PRESENT_AND_SUBSTANTIAL` | 9/9 | W5-00…W5-10 (11) | A1-W-01 |
| W6 Upstream-change staleness propagation | `PRESENT_AND_SUBSTANTIAL` | 7/7 | W6-01…W6-10b (15) | A1-W-01 |
| W7 Orphan / dead-output detection | `PRESENT_AND_SUBSTANTIAL` | 6/6 | W7-01…W7-09 (10) | A1-W-01 |
| W8 Forward and reverse lineage | **`PARTIAL`** | 4/5 | W8-01…W8-05b (8) | **A1-W8-01**, A1-W-01 |
| W9 Session/handoff continuity | `PRESENT_AND_SUBSTANTIAL` | 6/6 | W9-01…W9-06c (10) | A1-W5-01, A1-W-01 |
| W10 Deterministic inputs outrank retrieval | `PRESENT_AND_SUBSTANTIAL` | 5/5 | W10-01…W10-05b (8) | A1-W-01 |
| W11 Artifact-flow quantitative health | `PRESENT_AND_SUBSTANTIAL` | 9/9 | W11-01…W11-11 (12) | A1-W-01 |
| W12 Health-scheduler integration | `PRESENT_AND_SUBSTANTIAL` | 7/7 | W12-G0…W12-01 (14) | A1-W12-01, A1-W-01 |

**10 of 12 `PRESENT_AND_SUBSTANTIAL`; 2 `PARTIAL`; 0 `ABSENT`; 0 `UNCLEAR`; 0 `N/A_WITH_REASON`.**
Both `PARTIAL`s carry an argued AC-3 `CANNOT_UNDERMINE` statement in `capability-audit.yaml`.

### The two PARTIALs

**W3.4 (Contract v3:1097, "reason for each dependency") — finding A1-W3-01, MEDIUM, RESIDUAL of
BC-P2-17, non-blocking.** A task that declares its mandatory inputs through the typed list fields
(`requirements`, `decisions`, `scenarios`, `acceptance_tests`, `interfaces`, `architecture`,
`required_data`, `derived_from`, `dependencies`) records `reason: null` for every one of them; the
manifest is `COMPLETE`, the task is READY, claimable and dispatchable, and no surface at any health
tier reports the omission. The object declaration forms (`required_inputs`, `optional_inputs`,
`relations[].note`) do carry a reason, and `gov task create` — the product's own authoring command —
writes the typed list form. The automated check the evidence map maps to W3.4 asserts a reason on
exactly one entry, the one declared in object form, while the same fixture's other inputs carry none,
so it does not establish the bullet it is mapped to. AC-3 argument: the missing element is the prose
beside a dependency, not the dependency, its version or its delivery; every fault the Gate-W
advanced-qualification challenge names is detected and refused without it.

**W8.5 (Contract v3:1152, cross-language / cross-repository relationships "where in scope") —
finding A1-W8-01, LOW, RESIDUAL of BC-P2-20, non-blocking, owner decision flagged.** Relationships
in more than one language within one repository *are* captured (Python and Rust `CALLS`/`IMPORTS`
edges from the built-in extractor). A relationship spanning two languages (an FFI boundary) or two
repositories is not, and the repository contract declares no convention for either. The bullet is
conditioned on "where in scope" and nothing in the accepted sources places such a relationship in
scope at Phase 2, so this is recorded as not-established rather than unmet; placing it in scope
would be an owner decision.

## 4. AC-8 — the Artifact Flow Coverage Matrix

`artifact-flow-coverage-matrix.yaml` was **rebuilt from scratch on this candidate**. It has **15
rows** — one per governed artefact type Contract v3 W1:1080 names (specifications as requirement and
as feature, scenarios, decisions, datasets, experiments, research outputs, architecture records,
interfaces, test designs, migration plans, audit findings, benchmark results) plus the equivalent
governed outputs the same line admits (the task close report as implementation evidence, and the
release record that terminates the W8 chain) — and **all eleven columns the frozen gate contract
lists**: producer artefact → stable ID/version → relationship type → downstream consumer/task →
mandatory/optional → task input manifest → context-packet evidence → consumption receipt → output
traceability → invalidation trigger → qualification challenge. Every cell names the held-out check
that proved it.

**AC-8 determination: MET.** Against its three rejection conditions:

1. **"semantic retrieval is relied on to rediscover mandatory inputs" — does not hold.** The
   required-input resolution is byte-identical with the index database removed (W3-09). A current
   spec whose rows are deleted from the semantic index is still delivered as a mandatory input with
   its content (W10-01). With the index removed, and again with it replaced by non-SQLite bytes, the
   packet stays `COMPLETE` with identical input hashes and only the supplementary block is `DEGRADED`
   — with its failing stage, error code, effect and remediation (W10-04-remove, W10-04-corrupt). The
   retrieved block is separately hashed and never enters the deterministic authority block (W4-02).
2. **"stale versions can silently satisfy downstream work" — does not hold.** A superseded input
   blocks the manifest, is delivered flagged with its successor, and the task is not claimable
   (W3-07, W10-02b). A HISTORICAL record cannot fill an authoritative slot (W2-06). A violated
   version or content-hash pin blocks (W3-03, W3-03b). A receipt acknowledging an input at a stale
   hash is refused with `STALE_CONSUMPTION` (W5-07c). After a direct upstream change, the work cannot
   be re-claimed or closed on the stale evidence (W6-09, W6-09c). A superseded, deliberately more
   semantically similar spec never replaces the current required one (W10-02).
3. **"completion cannot be traced to upstream evidence" — does not hold.** Task close refuses a
   completion with no consumption receipt and names every missing field (W5-07); refuses a fabricated
   requirement id (W5-07b) and a declared acceptance test with no evidence (W5-05); refuses
   implementation present in the tree but absent from the receipt, by path (W5-08). The persisted
   receipt records inputs consumed, outputs, what was implemented, what was applied, test evidence,
   deviations and unknowns (W5-02), and the chain walks feature → scenario → requirement → decision →
   architecture → task → code → test → evidence → release in both directions (W8-01, W8-01b, W8-02).

Gaps recorded against the matrix, none of which touches a rejection condition: the `task input
manifest` column carries A1-W3-01 for every row; the migration plan's `consumption receipt` cell is
PARTIAL because adoption stages A5–A11 are alpha's scope and were not driven here; G6 hidden-fault
injection is Phase 4 and only its Phase-2-verifiable surface was exercised.

## 5. The other iteration-1 duties

**W6 staleness after an upstream change — at rebuild and at claim.** Both halves hold, for the
harder case of a change made entirely **outside** change control. When the index rebuild observes it:
the DONE task is marked `retest_required` with `staleness.inputs_changed` naming the input and both
hashes; its closing report is marked stale; its delivered packet is marked `invalidated`; a linked
revalidation task is generated (and re-observing generates no duplicate); the task stays DONE but
`revalidation.required` is true; and the recorded green evidence is reported obsolete naming the
changed input classes (W6-01…W6-07b). At claim: claiming *other* work propagates the change, so the
completed work's staleness is recorded at claim time (W6-08); the stale work cannot then be
re-claimed — the refusal names the retest requirement and its remedy — and its own remedy stays
available (W6-09, W6-09b, W6-09c). Through CIT: CIT-P computes the impacted downstream nodes by name
(the completed task, its close report, its scenario, its test obligation) and states the revalidation
consequence (W6-10). The CIT-E *execution* half could not be driven to completion: at R3 an
unanswered Human Decision Gate correctly blocks approval, which is right behaviour, and the
propagation engine is the one the direct route exercised end to end (W6-10b).

**W12 across G0–G6.** Each tier's Gate-W duty was exercised at the tier, not read from a catalogue —
see §3 and `heldout/w12_tiers.py`. Thirteen of fourteen checks pass; the one failure is the G2
*preview* surface (A1-W12-01), not the gate.

**W7 orphan and dead-output detection.** All five W7 classes injected and each detected by name with
its contract line; one linked governed investigation per orphan, idempotent, nothing deleted; the
generated remediation does not count as a consumer, so an orphan stays reported until it is really
linked; genuinely consumed outputs are not reported (W7-01…W7-09).

**W11 quantitative metrics.** All nine computed with numerator, denominator and contract line, each
with a declared target, and each *moved* by injecting the fault it measures; a metric below target is
disclosed as a finding naming the metric, its value and its target; orphan-detection recall is
explicitly stated as not measurable in the governed repository, with the reason and the tier that
measures it, rather than reported as a silent null (W11-01…W11-11).

**W10 hard invariant, by construction.** All five bullets: current spec absent from the semantic
index (W10-01); superseded, more similar spec cannot replace the current one (W10-02, W10-02b); token
pressure drops supplementary before mandatory (W10-03); index outage and index corruption do not
erase the deterministic dependencies (W10-04-remove, W10-04-corrupt); delivery is independently
testable and the verification fails by name when a delivered input has changed (W10-05, W10-05b).

**Cross-cutting attacks the common protocol asks of every verifier, where zeta's scope reaches them.**
*Availability rule*: every Gate-W block I raised refuses only what it protects and leaves its remedy
available — a task blocked for a missing input can still be inspected and repaired (W3-06b); work
blocked for retest can still recompile its context and show its staleness (W6-09b); each refusal is
typed and names its scope. *Trust classes (D-0007)*: a test obligation's own
`independent_of_implementer` claim is refused as evidence; a `tests.status: passed` claim the product
cannot run is refused; research and lessons cannot occupy a decision slot (W2-04b, W2-05).
*Freshness*: demonstrated for every capability through the W6 chain, and recorded per capability in
`capability-audit.yaml`. *Cross-machine continuity* is alpha's lead and was not exercised here.

## 6. Findings I raise

| id | Capability | Severity | Blocking | Label | Class |
|---|---|---|---|---|---|
| A1-W3-01 | W3 | MEDIUM | no | RESIDUAL | BC-P2-17 |
| A1-W-01 | W2 W4 W8 W9 W10 W12 | LOW | no | RESIDUAL | BC-P2-02 |
| A1-W12-01 | W12, W5 | LOW | no | **MATERIALLY_NEW** | — |
| A1-W5-01 | W9, W5 | LOW | no | RESIDUAL | — (continuation of the non-blocking A0-W5-03) |
| A1-W8-01 | W8 | LOW | no | RESIDUAL | BC-P2-20 |
| A1-W4-01 | W4 | INFO | no | RESIDUAL | — (continuation of the non-blocking A0-W4-05) |

**Nothing here blocks `GATE-P2-CAPABILITY-BASELINE-ACCEPT` for Gate W.** The single
`MATERIALLY_NEW` label is A1-W12-01, and it is **non-blocking**, so this family contributes **no
materially new blocker class** to the frozen contract §8 convergence count. The two RESIDUAL findings
with `inventoried_class: null` (A1-W5-01, A1-W4-01) are continuations of iteration-0 findings that
were recorded non-blocking and therefore are not named by any `BC-P2-NN` class; they are labelled
RESIDUAL because their capability and mechanism are identical to an iteration-0 finding, and they are
flagged here so the orchestrator can see the label is not a downgrade.

One finding carries `owner_decision_required: true` — A1-W8-01, because placing cross-repository
relationships in scope would add a product requirement (a second governed repository, its trust and
path-map boundary, and how identity and impact cross it) that the accepted sources do not make.

## 7. Iteration-0 findings: what I closed and what is still residual

29 prior findings are in scope (27 from the zeta audit of record, 2 from the synthesis auditor).
**24 CLOSED, 5 RESIDUAL, 0 NOT_APPLICABLE.** Of the 25 that were recorded blocking, **23 are closed**
and the remaining two are residual only in a narrow element and are no longer blocking.

**Closed (24)** — A0-W1-01, A0-W2-01, A0-W2-02, A0-W3-01, A0-W3-02, A0-W3-04, A0-W4-01, A0-W4-02,
A0-W4-03, A0-W4-04, A0-W5-01, A0-W5-02, A0-W6-01, A0-W6-02, A0-W6-03, A0-W6-04, A0-W6-05, A0-W7-01,
A0-W9-01, A0-W10-01, A0-W11-01, A0-W12-01, S0-W1-01, S0-W5-01. Per-finding evidence is in
`prior-findings-disposition.yaml`. Four are worth naming because they were the deepest:

* **A0-W10-01** (the W10 hard invariant, HIGH) — the compiler no longer aborts on a retrieval error;
  with the index removed *or corrupted*, the mandatory inputs are delivered whole and only the
  supplementary block is DEGRADED, with reason and remedy.
* **A0-W6-02** (ungoverned upstream change propagates nothing, HIGH) — change detection is now
  content-based against what each consumer recorded it consumed, so an index rebuild *causes* the
  propagation instead of licensing stale consumption.
* **A0-W7-01** (orphans undetected, HIGH) — all five classes detected by name, each with linked,
  idempotent governed investigation work, nothing deleted.
* **A0-W11-01** (no artifact-flow metrics, HIGH) — all nine computed, each moved by its own injected
  fault, each below-target value disclosed as a finding.

**Residual (5)**

| prior id | element still open | now blocking? | new finding |
|---|---|---|---|
| A0-W3-03 | the *reason* element only; state, version/hash and supplementary context are closed | no | A1-W3-01 |
| A0-W8-01 | the *cross-language / cross-repository* element only; code, evidence, release, stale and missing links are closed | no | A1-W8-01 |
| A0-W-01 | nine Gate-W bullets with no automated check; `severity` unpopulated. The compiled form and evidence map now carry all 86 bullets, the hard invariant and the challenge | no | A1-W-01 |
| A0-W5-03 | the string handling is unchanged; its consequence moved from worker attribution to `gov recover`'s uncommitted list | no (was non-blocking) | A1-W5-01 |
| A0-W4-05 | unchanged; still not a breach of W4:1109 | no (was non-blocking) | A1-W4-01 |

## 8. What I could not establish

* **A relationship spanning two languages or two repositories** (W8.5). Multi-language relationships
  within one repository are captured; an FFI-style edge and any cross-repository edge are not, and
  the repository contract declares no convention for either. Recorded as A1-W8-01 with an owner
  decision flagged, not as an unmet requirement — W8:1152 conditions the bullet on "where in scope".
* **The CIT-E execution half of W6 propagation.** At the R3 radius my change produced, approval
  correctly requires an answered Human Decision Gate, and I am not the owner and may not manufacture
  a human answer. I established the CIT-P half (the impact set by name, the revalidation consequence)
  and the whole propagation through the direct-change route, which uses the same engine. A smaller,
  auto-approvable radius was not reachable in a repository that has both source and tests, because
  the two-module rule lifts the radius to R3.
* **Adoption stages A5–A11**, and therefore the migration plan's consumption-receipt cell and the
  adoption audit's own findings. A11 correctly refuses out of protocol order. That path is alpha's
  scope; I verified the migration plan's identity, versioning and supersession through A0–A4 and the
  finding-id scheme through the governance suite.
* **Cross-machine continuity** (P2-ADJ-0002) — alpha leads it; nothing in W1–W12 required it, and I
  did not exercise it.
* ~~The certification regression suite.~~ **Resolved after the first evidence commit**: it completed
  **207 passed, 0 failed**, independently reproducing the regression state. Recorded in
  `evidence/cargo-certification.out` and in the run report.
* **Whether a `PARTIAL` metric set can hide a real defect.** Several W11 metrics report
  `applicable: false` in a repository with no live work, so a project could carry a green
  artifact-flow family with almost nothing measured. I demonstrated that each metric becomes
  applicable and moves under its own fault, but I could not establish a lower bound on what must be
  measured before the family may be green. Recorded as W11's residual risk, not as a finding.
* **A plugin-provided embedder that hangs rather than failing.** The W10 outage attacks covered a
  missing index, a corrupt index and a failing retrieval stage; a hanging capability plugin was not
  exercised. Recorded as W10's residual risk.

## 9. Files

```
release/capability-baseline/verify-1/zeta/
  00-VERIFICATION-REPORT.md          this file
  capability-audit.yaml              12 capabilities, 86 bullets, each with its own evidence
  findings.yaml                      6 findings, 0 blocking
  prior-findings-disposition.yaml    29 prior findings: 24 CLOSED, 5 RESIDUAL
  artifact-flow-coverage-matrix.yaml AC-8: 15 rows x 11 columns, determination MET
  heldout/                           the probes I wrote, and RUN-ALL
    RUN-ALL, lib.py,
    w01_identity.py  w01b_plan_bench.py  w02_contracts.py  w03_manifest.py
    w04_delivery.py  w05_receipt.py      w06_staleness.py  w07_orphans.py
    w08_lineage.py   w09_continuity.py   w10_hard_invariant.py
    w11_metrics.py   w12_tiers.py
  evidence/
    00-pinned-inputs.out               identity and digest verification
    RUN-ALL.out                        the full held-out run, one PASS/FAIL line per check
    cargo-lib.out, cargo-certification.out   regression evidence (O3)
    A1-W3-01-no-reason.out             the missing-reason transcript
    A1-W-01-evidence-map-coverage.out  Gate-W rows of the evidence map
    A1-W-01-contract-verify.out        `gov contract verify` in the product repository
    A1-W5-01-dirty-path-truncation.out the dropped uncommitted path
    A1-W12-01-close-check.out          preview vs gate, same task, same report
```

To re-run everything: `ZETA_WORK=<fresh scratch dir> release/capability-baseline/verify-1/zeta/heldout/RUN-ALL`
from a worktree at this candidate with `target/release/gov` built. Run it **once at a time** against a
given `ZETA_WORK`; two concurrent runs sharing one scratch root will move each other's disposable
repositories aside.
