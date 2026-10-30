---
id: DAEO-swdu
status: open
deps: [DAEO-g0ip, DAEO-rd0g, DAEO-0pyc, DAEO-2ds6]
links: []
created: 2026-10-16T16:35:11Z
type: task
priority: 1
assignee: research
external-ref: W2-15b
tags: [wave-2, research, full]
title: 'EXP-003, pass 2: the final measurement against 99 %'
class: research
state_class: AUTHORITATIVE
role: research
depends_on:
- DAEO-g0ip
- DAEO-rd0g
- DAEO-0pyc
- DAEO-2ds6
allowed_paths:
- docs/research/EXP-003/**
- experiments/EXP-003/**
kpis:
  success:
  - The same metric, corpora and modes as W2-15a, re-run after W2-32's bounded improvements. Each figure is shown beside its baseline [AR-10].
  - The corpus mean per corpus and mode against the owner's 99 % goal, with every miss classified (labelling, chunking, ranking, coverage).
  - 'The stacking test, final: complete and no duplicates, or each gap named [AR-10].'
  - 'The scale probe: EXAMIN''s clone and ~/workspace against DEC-078''s envelope (≈ 80k nodes, 270k edges, ≈ 2.2 GB peak RSS), including the brute-force vector scan and the graph cache [W2-M351, W2-L317,
    W2-L320, W2-M089].'
  - CAP-10's hit@5 against 85, per class beside the single-class figure, for the owner's CAP-10 package (Q-10) [W2-M017, F-m2].
  - 'Batched, ranked, stacked retrieval: a question whose evidence exceeds one batch is answered in batches, ranked and stacked within the agent''s budget, never by one giant query or context; the
    measure is the share of questions whose stacked context holds all their needed evidence, in order of relevance, across batches, against the owner''s target of 99 % [DEC-860]'
  - 'Both figures in every report: hit@5 against CAP-10''s floor of 85, and the complete-stacked-evidence share against 99 % [DEC-833]'
  failure: []
profile: FULL
sources:
- DEC-078
- CAP-10
- DEC-725
- DEC-727
- DEC-833
- DEC-860
est_loc: 60
acceptance_tests:
  judged_by: 'its class (WBS §0 rule 1, W2-07): its evidence record'
track: B
closes:
- AR-10
- exit criterion 4
list_rows:
- W2-L317
- W2-L320
- W2-M017
- W2-M089
- W2-M351
---
# W2-15b EXP-003, pass 2: the final measurement against 99 %

Card: `docs/plan/WAVE_2_WBS.md` §2 (W2-15b), as approved (DEC-729). The list rows it takes in are in `list_rows` and in `docs/plan/WAVE_2_TRIAGE.md`; a row's state is re-checked against the code when the ticket picks it up (DEC-718).

- **Allowed paths:** as W2-15a, with working copies under `~/gov-os-runs/W2-15b/`.
- **KPIs:**
  - The same metric, corpora and modes as W2-15a, re-run after W2-32's bounded improvements. Each figure is shown beside its baseline [AR-10].
  - The corpus mean per corpus and mode against the owner's 99 % goal, with every miss classified (labelling, chunking, ranking, coverage).
  - **The stacking test**, final: complete and no duplicates, or each gap named [AR-10].
  - **The scale probe:** EXAMIN's clone and `~/workspace` against DEC-078's envelope (≈ 80k nodes, 270k edges, ≈ 2.2 GB peak RSS), including the brute-force vector scan and the graph cache [W2-M351, W2-L317, W2-L320, W2-M089].
  - CAP-10's hit@5 against 85, per class beside the single-class figure, for the owner's CAP-10 package (Q-10) [W2-M017, F-m2].
  - **Batched, ranked, stacked retrieval (DEC-860, owner, 2026-10-20):** a question whose evidence exceeds one batch is answered in batches, ranked and stacked within the agent's budget, never by one giant query or context; the measure is the share of questions whose stacked context holds all their needed evidence, in order of relevance, across batches, against the owner's target of 99 %.
  - **Both figures in every report (DEC-833):** hit@5 against CAP-10's floor of 85, and the complete-stacked-evidence share against 99 %.
- **Under the finish line (DEC-725):** one run plus its probe; what is short of 99 % becomes a named residual with its cause, and goes to the owner.
- **Gates:** W2-29 (DEC-727).

## The wbs_id

This ticket has no `wbs_id`: the kernel's grammar (`common.schema.json`, `^W[0-9]+-[0-9]{2,}$`) refuses the letter suffix. Its W2 id is its `external-ref`, which `gov close` reads when `wbs_id` is absent (`src/gov/close/command.py`).
