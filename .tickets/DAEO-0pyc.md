---
id: DAEO-0pyc
status: in_progress
deps: [DAEO-g0ip, DAEO-rd0g]
links: []
created: 2026-10-16T16:35:11Z
type: task
priority: 1
assignee: engineer
external-ref: W2-32
tags: [wave-2, implementation, standard]
wbs_id: W2-32
title: 'Retrieval components and bounded improvements: model pin, swap by configuration, learning loop; ranked-lexical tuning, chunking, the hit@5 85 row'
class: implementation
state_class: AUTHORITATIVE
role: engineer
depends_on:
- DAEO-g0ip
- DAEO-rd0g
allowed_paths:
- docs/changes/W2-32-evidence.md
- src/gov/retrieval/**
- src/gov/config/models*
- tests/unit/retrieval/**
- tests/unit/semantic/**
kpis:
  success:
  - Changing the embedder pin in configuration triggers a full re-embed, and the dev-tier retrieval regression passes [CAP-10.b].
  - An unpinned or mismatched model fails closed with a named error [CAP-19.a, W2-M073, W2-M191, W2-L065].
  - A retrieval miss is recorded as a memory-quality event with its root cause, its repair and a held-out regression case [CAP-19.c].
  - A reranker that dies after loading is reported, not raised [W2-M104].
  - The fusion limit is honoured [W2-M103].
  - 'At most the three gaps that W2-15a named, from these: ranked-lexical tuning: field weights, tokenizer, and the exact-identifier boost'
  - 'At most the three gaps that W2-15a named, from these: chunking: span size, overlap and parent expansion, with a re-embed'
  - 'At most the three gaps that W2-15a named, from these: the hit@5 85 row on the dev queryset [W2-M341]: Each gets one round plus its probe; its effect is measured by W2-15b. What remains is a named residual.'
  - 'If memory is below 85 % after two improvement rounds, the orchestrator escalates to the owner with the reasons; at the third the owner decides: a discovery and research ticket benchmarking market tools in a separate worktree, accepting the level reached, or another course. At 85 % or above but under the owner''s target of 95 %, with room for improvement found, memory is not closed: an escalation to the owner [DEC-954 Q9e, DEC-957]'
  failure:
  - An improvement that lowers any baseline figure of W2-15a beyond its noise band is reverted.
profile: STANDARD
sources:
- CAP-10.b
- CAP-19.a
- CAP-19.c
- DEC-725
- DEC-954
- DEC-957
est_loc: 320
acceptance_tests:
  path: tests/acceptance/W2-32/
  author: independent-test-designer (MR-3); written before implementation
track: C
closes:
- CAP-10.b
- CAP-19.a
- CAP-19.c
- DEC-725
list_rows:
- W2-L029
- W2-L065
- W2-L066
- W2-L068
- W2-L239
- W2-M001
- W2-M073
- W2-M103
- W2-M104
- W2-M191
- W2-M341
---
# W2-32 Retrieval components and bounded improvements: model pin, swap by configuration, learning loop; ranked-lexical tuning, chunking, the hit@5 85 row

Card: `docs/plan/WAVE_2_WBS.md` §2 (W2-32), as approved (DEC-729). The list rows it takes in are in `list_rows` and in `docs/plan/WAVE_2_TRIAGE.md`; a row's state is re-checked against the code when the ticket picks it up (DEC-718).

- **Allowed paths:** `src/gov/retrieval/**`, `src/gov/config/models*`, `tests/unit/retrieval/**`, `tests/unit/semantic/**`.
- **KPIs, components:**
  - Changing the embedder pin in configuration triggers a full re-embed, and the dev-tier retrieval regression passes [CAP-10.b].
  - An unpinned or mismatched model fails closed with a named error [CAP-19.a, W2-M073, W2-M191, W2-L065].
  - A retrieval miss is recorded as a memory-quality event with its root cause, its repair and a held-out regression case [CAP-19.c].
  - A reranker that dies after loading is reported, not raised [W2-M104].
  - The fusion limit is honoured [W2-M103].
- **KPIs, bounded improvements (DEC-725):** at most the three gaps that W2-15a named, from these:
  - ranked-lexical tuning: field weights, tokenizer, and the exact-identifier boost;
  - chunking: span size, overlap and parent expansion, with a re-embed;
  - the hit@5 85 row on the dev queryset [W2-M341].
  Each gets one round plus its probe; its effect is measured by W2-15b. What remains is a named residual.
- **Failure:** an improvement that lowers any baseline figure of W2-15a beyond its noise band is reverted.

**Claimed (CTO, 2026-11-03 ~21:20, D-4b, DEC-1055; the owner's order of 21:10):** W2-32's test designer and engineer run as `gov launch` workers under this ticket's own id (no lead: the CTO acts as its lead from its session), so the guard's G-14 enforces their separation (DEC-1056, DEC-1063). Its dependency on W2-15a is W2-15a's baseline record, D-4b measure 1 (DEC-1055 (6)). S1-S5, S9, F1 now; S6-S8 after the owner approves the gaps.

## The interface (the engineer's spec; CTO, 2026-11-03, P2 under DEC-957: P-W2-32-1, from the test designer's spec-gap note, DEC-136; "the noise band" of F1 is the spread of D-4b measure 1's three runs with the merged code, 0 today, the pinned run excluded: P-W2-32-2)

- **S1, S2: the embedder pin in configuration.** A project's `governance/project/models.yaml`:

      embedder:
        model: <the Ollama model name>
        revision: <the digest Ollama's model list reports, or a prefix of it of at least 12 hex digits>

  Absent, ADR-0002 §2's pin holds: `qwen3-embedding:0.6b` at `ac6da0dfba84…` (the tool registry's manifest sha256,
  which is the digest `/api/tags` reports). The file is read as it stands in the working tree, tracked or not
  (W2-M073). The pin is checked at every rebuild and every search: against the store's manifest and against the
  revision the endpoint reports.
- **Named errors.** A fail-closed answer carries an upper-case error code: one holding `UNPINNED` for a configured
  model without a revision (proposed: `MODEL_UNPINNED`), one holding `MISMATCH` for a revision or a model that does
  not match (proposed: `MODEL_MISMATCH`), and any upper-case code (two parts or more) that names the model for a
  pinned model the endpoint does not list. The code is looked for anywhere in the answer's text: in `gov rebuild`'s
  `result.stores.semantic` (its `reason`, or a field of its own), in `semantic.search`'s answer, and in the reason of
  `retrieve`'s `facets.semantic` (which has only `available` and `reason`, so the code goes in the reason).
- **W2-L065: the cut.** `semantic.manifest(root)` holds the embedding cut, `512`, as one of its values (the key is
  not judged). A store whose `semantic_*` tables are only the vectors and the four-column manifest (two models and
  their revisions), as every store built before W2-32 is, is stale.
- **S3: the memory-quality event.** `gov.retrieval.learning`:
  - `record(root, miss) -> dict`. `miss` holds `question`, `expected` (the sources the answer needed:
    `[{"path": …}]`), `observed` (the paths retrieval gave first), `root_cause`, `repair`, and `regression`: a case
    in the standing measure's question form (`question`, `gold_answer`, `sources`; W2-61, `gov.retrieval.measure`).
    It writes the event as a YAML (or JSON) file in the project, outside `.gov-runtime/`, and the regression case
    as a file of its own, and returns the event: `id`, `type: memory-quality`, `question`, `root_cause`, `repair`,
    `path` (the event file, relative to the root) and `regression_case` (the case file, relative to the root).
  - A miss without its `question`, `expected`, `root_cause`, `repair` or `regression` (absent or empty), or a case
    without its `question`, `gold_answer` or `sources`, raises a `ValueError` (or a `GovError`) whose message names
    the missing part, and writes nothing.
  - `events(root) -> list[dict]`: every recorded event, with the same fields.
  - "Held out": the case file is not embedded (no vector after a rebuild), as tests and probe records stay out of
    memory (DEC-1052).
- **S4: reported.** `last_outcome()` after the rerank, and `rerank` in a bundle, say `by: unavailable` with a reason
  that names the failure; the order given is kept, with no `rerank_score`. `fusion.search`'s answer says
  `reranked: false`.
- **S5: honoured or refused.** `fusion.search` with a limit returns exactly that many distinct hits (all that match,
  if fewer), or refuses a limit above its cap with a `ValueError` or a `GovError` naming the limit or the cap.

