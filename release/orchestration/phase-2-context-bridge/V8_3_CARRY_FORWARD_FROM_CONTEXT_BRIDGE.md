# V8.3 carry-forward from the Phase-2 Context/Retrieval Bridge (P2X-FAIL-1)

> **Status: NON-NORMATIVE evidence and handoff input** for the future full V8.3 architecture session (OD-P2-10 §9) and
> for Phase-3 retrieval qualification (OD-P2-10 §10). **It is not Contract v3 authority, not an owner decision and
> not V8.3.** It becomes normative only through a later CIT or an owner-approved contract evolution (OD-BR-06
> preamble; OD-BR-06 §9: "Do not silently transform this evidence package into normative Contract authority").
>
> **Companion to** `release/orchestration/phase-2/V8_3_EVIDENCE_PACKAGE.md`. The bridge's mutation boundary forbids
> it to write anything under `release/orchestration/phase-2/`, so the carry-forward lives here. **A V8.3
> architecture session must read both.**

## The requirements a full V8.3 must receive, each with its source and its bridge implementation status

Implementation status is as of the date of this file. The independent bridge verifier must re-check each one; see
`HANDOFFS/BR-HO-VERIFY-*` §4.

| # | Requirement for V8.3 | Owner source | Bridge implementation status |
|---|---|---|---|
| 1 | **Whole-repository retrieval, not retrieval shaped around Review 8.** The corpus is the whole canonical repository, with principled, cited exclusions. Benchmarks such as Review 8 F1/F2/F3 are oracle cases, not corpus boundaries. | OC-BR-02; OD-BR-06 §1 | **Implemented and measured.** All 98 view refs are covered and equal `git ls-tree --full-tree`, with 0 unclassified (D1). No code special-cases Review 8; the controls are D-0006 and CTRL-1..3. |
| 2 | **Multi-batch / multi-hop retrieval.** A top-k or per-query budget is a configurable **batch size**, never an evidence-completeness limit (for example 8k + 8k + …). This needs pagination/continuation, facets, adaptive follow-up, a merge that preserves provenance, and deduplication. | OD-BR-05; OD-BR-06 §2 | **NOT yet implemented at `94d0211`.** Routes and compiler use a fixed top-k (8) in one round, with no paging. Planned as B7 `govbridge gather` before BUILT. |
| 3 | **Parallel + sequential retrieval.** Independent facets (WHY, decisions, code, graph, tests, history) run in parallel where it is safe. Evidence they discover then triggers sequential follow-up, repeating until a stopping criterion is met, and only then is the bounded context compiled. | OD-BR-05 §2–3; OD-BR-06 §3 | **NOT yet implemented.** In run-1, the demonstration **worker** performed 103 adaptive queries by hand. Planned in B7. |
| 4 | **Explicit retrieval stopping criteria, recorded per task:** authoritative inputs resolved, edges traversed, facets covered, no unresolved identifiers left, only duplicates remaining, or the budget reached with the unresolved coverage disclosed. | OD-BR-05 §5; OD-BR-06 §2 | **NOT yet implemented.** Planned in B7, with telemetry. |
| 5 | **Hierarchical evidence synthesis** when the evidence exceeds one final packet. The intermediate notes are **derived, not authoritative**, keep source ids/hashes/citations and claim-to-source lineage, disclose unresolved evidence, and can be rebuilt. Critical evidence is never silently dropped. | OD-BR-05 §7; OD-BR-06 §4 | **Partial.** Truncation is recorded, never silent (budgets, manifest drops, J notices). There is no intermediate-note schema or validator yet. Planned in B7. |
| 6 | **Checkpoint enforcement.** A typed worker checkpoint on completion. An outer checkpoint on every material transition, gate or decision, handoff, model switch or session switch, and before compaction and before close. A git commit or narrative ledger entry alone does not count. Retrospective reconstructions carry a label. | OD-BR-04; OD-BR-06 §7–8 | **Enforcement implemented on the side branch:** `check_state.py checkpoint`, `verify` refuses a state without a matching checkpoint, `integrate-check` enforces the schema-2 worker checkpoint, and PreCompact/SessionEnd hooks exist. The hooks are **not confirmed active in the originating session**, so checkpoints are also written manually. |
| 7 | **The BGE model is provisional and replaceable.** `BAAI/bge-small-en-v1.5` is a bridge embedder, not the final model. Keep provider/model replaceability, a pinned model/revision/licence/dimensions, deterministic reindexing, and index/provider interfaces that are independent of the model. Phase 3A/3B/3C may replace or augment it. | OD-BR-06 §5; launcher semantic bootstrap rule | **Implemented.** It sits behind the `gov-capability/1` adapter, pinned in `config/model-pin.yaml` (MIT, 384-d, ONNX Runtime 1.30 CPU). Vectors were bitwise-deterministic across processes, thread counts and batch sizes. Replaceability is argued in ARCHITECTURE.md §9–§10 and is to be challenged by the verifier. |
| 8 | **Mandatory authoritative inputs stay separate from supplementary retrieval.** Section A is resolver-only and identifiable. Retrieval never substitutes for it. A lifecycle label never removes a mandatory input. | launcher hard invariant; OD-P2-10 §6; OD-BR-06 §6; BR-ARCH-RULING-1 | **Implemented and verified on real data.** A is typed resolver-only, with an import boundary. An independent validator re-derives it. A is byte-identical when the index is unavailable. Contract v3 and the launcher sit in A with `UNKNOWN` lifecycle banners. |

## Lessons carried forward (empirical, from this bridge's own record: PHASE_LEDGER BR-L-0001 onward)

* **The recurring defect shape recurred inside the bridge.** Several times an upstream representation looked right
  while the effect downstream was wrong:
  * mandatory inputs placed as "supplementary";
  * a code layer that was empty in the reproducibility digest;
  * secret-excluded files leaking into code literals;
  * a section-G budget that was bypassed by rendering overhead, which buried the seed-cited enforcement points.

  **Each was caught only by compiling or measuring the real output end to end.** The builders' own checks passed
  every time.
* Budgets must be measured on **what the worker actually reads**, meaning rendered bytes.
* Any derived or eagerly built layer must go through **the same corpus/security exclusions** as the content layers.
* A view that follows a moving branch tip needs **freezes** during view-sensitive runs, or pinned views.
* A mandatory list and a lifecycle filter can combine to **silently remove required inputs**. Mandatory membership
  and lifecycle labelling must stay orthogonal.
* Every change to bridge code currently forces a FULL rebuild of about 40 minutes, dominated by CPU embedding.
  Layer-scoped invalidation is a V8.3 cost question.
* The demonstration agent's peak context was about 504k tokens. Cost against the 10–20% overhead objective
  (OD-P2-09 §16) needs a V8.3 answer, and multi-batch retrieval with hierarchical synthesis (items 2–5) is the
  intended remedy.
