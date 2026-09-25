# Review-8 demonstration: query set, held-out oracle schema and grading rules (BR-AR-0001)

| Field | Value |
|---|---|
| Class | `ORCHESTRATION_RECORD` (design). **Review 8 is the first mandatory benchmark case, not a design driver** (OC-BR-02). Every mechanism below is generic: the query classes, the chain stages, the oracle schema and the grading rules apply unchanged to any other case. Only the query *instances* and the oracle *content* are Review-8-specific. |
| Required by | the launcher's REVIEW-8 CONTEXT DEMONSTRATION; BR-HO-0001 §2.3; `GATE-BR-R8-DEMONSTRATION` |
| Machine-readable | `demonstration-queries.yaml` (the public query set); `demonstration-task.yaml` (the public task spec); `schemas/oracle.yaml`, `schemas/answers.yaml`, `schemas/grading-report.yaml` |

## 1. Who does what, and who never sees what

| Role | Routing | Sees | Never sees |
|---|---|---|---|
| Builders (B1–B6, I1) | sonnet | this file, `demonstration-queries.yaml`, `demonstration-task.yaml` | the oracle |
| **Test-author** (node `TA`) | **fresh opus**, not a builder | primary sources, meaning records at `6e7a2a3`, code at `3c880d8`, evidence at `58219d5`; this file; the schema | builder branches; demonstration answers until grading |
| **Demonstration agent** (node `DEMO`) | **fresh opus**; not a builder, not the test-author, and no prior chat | the `govbridge bootstrap` output for `demonstration-task.yaml`, the compiled packet(s), and the `govbridge` query commands | the oracle; `ARCHITECTURE/**`, `AGENT_RUNS/**`, `DEMONSTRATION/**`, `HANDOFFS/BR-HO-0*` (the task spec's `retrieval_exclusions`); Phase-2 session transcripts |
| **Grader** (node `GRADE`) | deterministic script, then **fresh opus** for the rubric items | everything, after the demonstration run has committed its answers | — |

**How the oracle is kept held out.** The test-author writes `oracle.yaml` **outside every worktree**, in a directory
the orchestrator creates with mode `0700` (for example `$HOME/.cache/gov-bridge/oracle-sealed/<run>/`). The path is
never placed in a builder or demonstration brief. The only thing committed at that point is
`DEMONSTRATION/oracle-commitment.yaml`, which holds `{oracle_sha256, author_run, author_model, written_at, schema:
govbridge-oracle/1}`, and it is committed **before** the demonstration runs. At grading, the oracle is copied into
`DEMONSTRATION/oracle/`, and the grader refuses it unless its sha256 equals the commitment.

## 2. Demonstration protocol

1. **Preconditions**, each a deterministic check:
   * I1 merged;
   * D1 coverage reports `unclassified = 0`;
   * `govbridge freshness` returns `NOOP` against the committed build manifest;
   * the oracle commitment is merged.
2. The orchestrator runs `govbridge bootstrap ARCHITECTURE/demonstration-task.yaml > DEMONSTRATION/<run>/bootstrap.md`
   and `govbridge compile …`. Both outputs and the manifest are committed.
3. The demonstration agent receives **only** `bootstrap.md` and the packet as its prompt. It may run `govbridge
   search/why/impact/history/exact/state`. **Every such command writes a supplementary packet with its own manifest.**
   The agent may read files directly, but it must declare each read in the receipt's `external_reads`. Reads are
   counted (§4, G7).
4. It returns:
   * `answers.yaml` (`schemas/answers.yaml`), with one entry per query id, each claim citing a packet `item_id` or an
     exact `(path, commit, lines)`;
   * `receipt.yaml`, covering the main packet and every supplementary packet.
5. The orchestrator extracts the agent's tool calls from its transcript. It ADAPTs `telemetry_context_extract.py`'s
   categorisation logic, copied into the domain. The extraction goes to `DEMONSTRATION/<run>/reads.json`, for G7.
6. Grading runs (§4).

## 3. The public query set

The query set is the benchmark instance of the **ten generic query classes** that the launcher requires, plus the
**chain reconstruction** and the **authority-preservation** checks. Wording is neutral: no query presupposes a
classification, a remedy or an answer.

### 3.1 Chain reconstruction: `R8-CHAIN-F2`, `R8-CHAIN-F3`

> *Starting from the finding as reported in the Review-8 return (P2-AR-0097, F2 or F3), reconstruct its full
> decision/effect chain at the frozen product `3c880d8`, stage by stage:*
>
> requirement / intended property → source/construction → composition / union → partition / filtering → precedence /
> ordering → matcher / evaluator → final enforcement decision → concrete effective permission/behaviour → tests →
> prior findings / failed repairs → current Review-8 finding / status.
>
> *For each stage, cite the code or record anchor, and state what it does, **verified at `3c880d8`** rather than
> quoted from the review. Identify the **actual decision/enforcement point**, meaning the code whose evaluated result
> decides the concrete behaviour. If you believe a stage does not exist for this finding, say so and cite why.*

### 3.2 Side by side: `R8-SIDE-BY-SIDE`

> *Place the F2 path and the F3 path side by side, each down to its real enforcement point. List the code locations
> they share and the ones where they differ. Record the evidence that bears on whether they are one deeper class and
> the evidence that bears against it. **Do not classify them.** End with `classification: NOT_DETERMINED_BY_BRIDGE`.*

This makes the owner's F2/F3 hypothesis (`HYPOTHESIS_TO_TEST`) **testable without answering it**.

### 3.3 Evidence both ways: `R8-F1-BOTHWAYS`

> *For the health-sandbox exemption that F1 concerns: reconstruct why it was created (its purpose, its origin record
> and the requirement or owner decision it served), every consumer (production and test, and whether each consumer
> is in-process or cross-process), what it depends on, and what depends on it. Record the evidence relevant to the
> owner's direction (DELETE / SIMPLIFY / REPAIR / NARROW / RETAIN), both for and against. **State no decision.***

### 3.4 The ten query classes × three subjects (`S1..S3 × QC1..QC10` = 30 queries)

The subjects are described by function, so no query hands over an answer:

* **S1**: the composition that decides a path's effective attributes (from the pattern-producing layout derivation,
  through policy loading and the overlay evaluation, to the path decision);
* **S2**: the re-onboarding union of last-known floor rules across the machine store;
* **S3**: the health-sandbox exemption and its creator-liveness predicate.

| Class | Query template (instantiated per subject in `demonstration-queries.yaml`) |
|---|---|
| QC1 | Why does this mechanism exist? |
| QC2 | Which Contract-v3 capability requires it? |
| QC3 | Which owner or architecture decisions constrain it? |
| QC4 | What does it depend on? |
| QC5 | What depends on it? |
| QC6 | Which prior approaches failed, and why? |
| QC7 | Which tests prove it or challenge it? |
| QC8 | Which evidence becomes stale if it changes? |
| QC9 | What is current and what is superseded, for its governing decisions and for the code itself (which ref is canonical)? |
| QC10 | What could potentially be deleted without violating the actual requirement? *(Answer with the evidence only: consumers, requirements served, test-only consumers. **No recommendation.**)* |

### 3.5 Authority preservation: `AUTH-1..AUTH-4`

These are checked on the **packet** by the deterministic grader, and on the **answers** by the rubric:

* `AUTH-1`: list every mandatory input with its authority class, as the packet presents it;
* `AUTH-2`: which items are owner decisions in force, and which are owner directions or hypotheses to test;
* `AUTH-3`: which Phase-2 findings were withdrawn, and by whom;
* `AUTH-4`: which Phase-2 stop conditions are current, and which are superseded.

### 3.6 Controls: `CTRL-1..CTRL-3`

These are unrelated subsystems. They show that the bridge is not Review-8-shaped (OC-BR-02).

* `CTRL-1`: *Which decision adopted the signed release root, what requirement does rollback/high-water protection
  serve, where is the high-water check enforced in code, and which tests prove it?*
* `CTRL-2`: *Why does an executable capability plugin need a registration, which decisions constrain that, and where
  does the product refuse an unregistered plugin?*
* `CTRL-3`: *What is current and what is superseded for: the operator control panel version; the Phase-1 target
  architecture; the Phase-2 stop conditions?*

## 4. Grading rules

The deterministic grader (`govbridge demo grade`, built in node I1) computes everything marked **[D]**. A fresh opus
grader applies the rubric items marked **[R]**. Each rubric item is binary, and the grader must quote the answer text
it judged. The grading report follows `schemas/grading-report.yaml`.

### G1 Packet validity: hard
**[D]** `govbridge packet verify` passes for the main packet and every supplementary packet (`ARCHITECTURE.md`
§5.3, point 4).

### G2 Receipt: hard
**[D]** `govbridge receipt check` passes:
* hashes and read tokens match;
* every A item is acknowledged with its exact `content_sha256`;
* every cited `item_id` exists;
* every external read resolves to a real blob.

### G3 Authority classes preserved: hard, as BR-HO-0001 §2.3 requires
The run **fails** if any of the following holds:
* **[D]** a `mandatory_bridge_inputs` item appears in any section other than its expected one, or without its exact
  class and banner (`ARCHITECTURE.md` §5.1);
* **[D]** section A or D.1 contains a non-ladder class or a non-`ACTIVE` lifecycle;
* **[D + R]** the F1 direction is **presented as a decision**. On the packet side [D], that means it appears in A or
  D.1. On the answer side [R], it means a statement that deletion, or any other disposition, *has been decided* or
  *is authorised*;
* **[D + R]** the F2/F3 hypothesis is **presented as a classification**. On the packet side, placement outside D.3.
  On the answer side, any statement that F2 and F3 *are* or *are not* one class, other than
  `classification: NOT_DETERMINED_BY_BRIDGE`;
* **[D + R]** the **withdrawn positive-control finding is cited as a finding**. That means a citation to
  `P2-AR0096-POSITIVE-CONTROL-GAP.md`, or to its item, that is not marked `WITHDRAWN`, or that is used as support for
  a defect claim;
* **[R]** the **orchestrator's reasoning errors are presented as evidence for the hypothesis**. That means a citation
  to `orchestrator_error_f3`, `P2-L-0046` or `P2-L-0047`'s reasoning-error passage offered in support of a
  single-class conclusion or placed in the side-by-side "for" evidence.

### G4 Chain reconstruction: hard, per chain (`R8-CHAIN-F2`, `R8-CHAIN-F3`)

Each of the 11 stages is graded against the oracle's stage entry:

| Grade | Rule |
|---|---|
| `REACHED` | **[D]** the answer cites at least one of the stage's `anchors.any_of`, or every anchor in `anchors.all_of`. A code anchor matches on the same path at the same commit, or at a commit where the file's blob is identical, **and** a line within `line_tolerance` (default 3) or the same `symbol`. A record anchor matches by record id or section. **[R]** Each `must_state` fact is present in the stage's claim. |
| `UPSTREAM_ONLY` | the stage is the oracle's `is_enforcement_point: true` stage, and the answer cites **only** anchors listed in `traps`: upstream representations, such as a report/refused list, a doctor finding, a unit test's assertion, or a value computed but not consumed |
| `MISSING` | no citation, or `does not exist` stated for a `required: true` stage |
| `WRONG` | it cites an anchor the oracle lists under `wrong`, or a must_state fact is contradicted |

**A chain passes** only if every `required` stage is `REACHED`, and the enforcement stage is `REACHED` at an oracle
enforcement anchor or at a listed `acceptable_alternative_enforcement_points` entry. **An `UPSTREAM_ONLY` enforcement
stage fails the chain regardless of every other stage.** That is the launcher's rule, applied mechanically: *"Do not
accept evidence that proves only an upstream representation while downstream semantics decide the real effect."*
Both F2 and F3 must pass. `R8-SIDE-BY-SIDE` passes when both enforcement points are reached, the shared and differing
code locations match the oracle's `shared_points` / `differing_points` at recall ≥ 0.8, and **[R]** no classification
is asserted.

### G5 Query classes: hard

For each query:
* **[D]** recall of the oracle's `required` items (records by id, anchors by §G4 matching) is at least **0.8**
  (`MEMORY_POLICY.regression.min_recall_at_k`);
* **[D + R]** it cites none of the oracle's `forbidden` items;
* **[R]** every `must_state` fact is present.

A class passes when at least 2 of its 3 subjects pass. **QC9 (current vs superseded) must pass for all three
subjects**, because it is the class that most directly tests the authority filtering. The overall threshold is 10/10
classes.

### G6 F1 evidence both ways: hard
* **[D]** the answer cites at least one oracle `purpose_anchors` entry **and** every oracle `consumer_anchors` entry;
* **[R]** it states no decision.

### G7 No whole-repository dumping: hard

Let *corpus* be the included text bytes of the view at the demonstration build (the build manifest's coverage). The
measured value is about 77.3 MB for the three named refs, per SO-04. The run fails if any of the following holds:

* **[D]** total packet bytes (the main packet plus every supplementary packet) exceed **1% of corpus**, or the sum of
  the budget profiles used;
* **[D]** there are more than **25** distinct externally-read files (`CONTEXT_POLICY.fresh_agent_read_budget_files:
  25`), or external read bytes exceed **0.5% of corpus**;
* **[D]** the transcript extraction shows a read that the receipt does not declare (**undeclared reads fail**);
* **[D]** the transcript shows whole-tree enumeration or content sweeps with no path restriction: `grep -r`/`rg` at the
  repository root, `find .` or `ls -R` at the root, `git ls-tree -r` over a whole commit, `git grep` without a pathspec
  outside `govbridge`, or `cat`/`sed` of more than 25 files.

The grader reports `(packet_bytes + external_read_bytes) / corpus` as the headline context-efficiency figure.

### G8 Controls: hard (OC-BR-02)
`CTRL-1..3` must each meet the G5 query rule. A bridge that passes Review 8 and fails the controls is Review-8-shaped,
and it fails.

### Verdict

`DEMONSTRATION_PASS` requires every one of G1–G8. Anything else is `DEMONSTRATION_FAIL`, with a per-gate reason list.
The grade is **builder-level evidence** that feeds `P2_CONTEXT_RETRIEVAL_BRIDGE_BUILT`. It is **not** the acceptance
token. `P2_CONTEXT_RETRIEVAL_BRIDGE_READY` belongs to the independent verifier dispatched by the next control-panel
stage.

## 5. The held-out oracle: structure (content is the test-author's alone)

The oracle's schema is `schemas/oracle.yaml`. Its shape is:

```yaml
schema: govbridge-oracle/1
oracle_id: R8-ORACLE-1
author: {run_id: BR-AR-NNNN, role: test-author, model_observed: …}
commits: {product: 3c880d80f81475f5306bdd5f680f2e004df49391, records: 6e7a2a3495a8d3619759a95b7ed055da9c848618,
          evidence: 58219d5628683d6f462aa67bf25dbc2641933bce}
written_from: [{path, commit, lines?}]          # the primary sources the author actually read
line_tolerance: 3
chains:
  - query_id: R8-CHAIN-F2
    stages:
      - stage: requirement | source_construction | composition_union | partition_filtering | precedence_ordering |
               matcher_evaluator | final_enforcement_decision | effective_behaviour | tests | prior_findings |
               current_status
        required: true|false
        is_enforcement_point: false|true         # exactly one stage per chain is true
        anchors: {any_of: [ANCHOR…]} | {all_of: [ANCHOR…]}
        must_state: [short factual statements the claim must contain]
        traps: [ANCHOR + why]                    # upstream representations; citing only these = UPSTREAM_ONLY
        wrong: [ANCHOR + why]
    acceptable_alternative_enforcement_points: [ANCHOR + justification]
    effective_behaviour: {subject, attribute, before, after, evidence: ANCHOR}
side_by_side: {shared_points: [ANCHOR…], differing_points: [ANCHOR…]}
f1_both_ways: {purpose_anchors: [ANCHOR…], consumer_anchors: [ANCHOR + {process: in|cross, production: true|false}]}
queries:
  - query_id: S1-QC4
    required: [ID | ANCHOR…]
    forbidden: [ID | ANCHOR + why]
    must_state: [...]
authority_expectations:
  - {item: OD-P2-10A, sections: [A, D.1], class: OWNER_DECISION}
  - {item: F1-DIRECTION, sections: [D.2], class: OWNER_DIRECTION_TO_TEST}
  - …                                            # one per mandatory_bridge_inputs item
controls: [{query_id: CTRL-1, required: [...], must_state: [...]}, …]
ANCHOR := {kind: code|test|record|contract|evidence, commit, path, lines: [start, end]?, symbol?, record_id?, section?}
```

**Rules the test-author must follow** (the test-author's own acceptance, node `TA`):

* every anchor is verified at its commit (`git show <commit>:<path>`), with the command logged in its checkpoint;
* every stage cites the primary source, never the Review-8 return alone. The return may be listed in `written_from`,
  and it is the finding's source of truth for *what was reported*;
* the author **identifies the enforcement point by reading to the decision**, not by inheriting the review's
  location. Where the author finds more than one genuine consumer, they are listed as
  `acceptable_alternative_enforcement_points` with a justification;
* the oracle must not assert any classification of F2/F3 or any disposition of F1. It records facts and anchors only;
* before the commitment is written, the oracle passes a structural check against `schemas/oracle.yaml`: required
  keys, exactly one enforcement stage per chain, well-formed anchors, and one `authority_expectations` row per
  `mandatory_bridge_inputs` item. The test-author writes that small checker inside its own scope, because it runs in
  parallel with the builders. At grading, I1's `govbridge demo validate-oracle` re-runs the same check, and it must
  agree.
