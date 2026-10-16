---
id: DAEO-rd0g
status: open
deps: [DAEO-g0ip, DAEO-ym8a, DAEO-u4oz, DAEO-r9ss, DAEO-zqvn, DAEO-kl5e]
links: []
created: 2026-10-16T16:35:11Z
type: task
priority: 1
assignee: research
external-ref: W2-15a
tags: [wave-2, research, full]
title: 'EXP-003, pass 1: the baseline'
class: research
state_class: AUTHORITATIVE
role: research
depends_on:
- DAEO-g0ip
- DAEO-ym8a
- DAEO-u4oz
- DAEO-r9ss
- DAEO-zqvn
- DAEO-kl5e
allowed_paths:
- docs/research/EXP-003/**
- experiments/EXP-003/**
kpis:
  success:
  - 'The metric is defined and recorded before the first run [AR-10]: what counts as a hit; how the needed evidence for each question is labelled (by whom, blind to the system''s answers); per-question
    recall of needed evidence in the stacked context; the corpus mean, against the owner''s goal of 99 %'
  - 'Corpora: the dev tiers; ~/workspace read-only; EXAMIN through this ticket''s own clone of the owner''s copy. W2-26''s clone sits under /tmp and may be gone.'
  - 'Five modes compared: lexical only (now ranked), semantic only, fused, fused plus reranker, and the lighter-reranker spike (DEC-074 Q3) [W2-L329].'
  - Indexing time, peak RSS and incremental update per corpus, against DEC-078's envelope [W2-L102, W2-L321].
  - The stacking test (a question needing about 24k tokens, retrieved in 8k batches, assembled complete, no duplicates by span hash), run once as a baseline [AR-10].
  - Decision-level retrieval after W2-03 [AR-10]. The thin-margin cases and the two dev queries without gold paths are fixed or named [W2-M342, W2-L322, W2-M340].
  - Closes when the evidence record holds every measure per corpus and mode, with commands, versions and raw answers kept, and names the gaps that W2-32 will work on (at most three, chosen with the owner's
    approval of the metric).
  failure: []
profile: FULL
sources:
- DEC-074
- DEC-078
est_loc: 100
acceptance_tests:
  judged_by: 'its class (WBS §0 rule 1, W2-07): its evidence record'
track: A
closes:
- AR-10 (EXP-003)
list_rows:
- W2-L102
- W2-L321
- W2-L322
- W2-L329
- W2-M340
- W2-M342
---
# W2-15a EXP-003, pass 1: the baseline

Card: `docs/plan/WAVE_2_WBS.md` §2 (W2-15a), as approved (DEC-729). The list rows it takes in are in `list_rows` and in `docs/plan/WAVE_2_TRIAGE.md`; a row's state is re-checked against the code when the ticket picks it up (DEC-718).

- **Needs first:** the owner's approval of the metric (queued Q-2), recorded before the first run. The same metric serves both passes.
- **Allowed paths:** `docs/research/EXP-003/**`, `experiments/EXP-003/**`; working copies under `~/gov-os-runs/W2-15a/`, cloned by exact path.
- **KPIs:**
  - **The metric is defined and recorded before the first run** [AR-10]:
    - what counts as a hit;
    - how the needed evidence for each question is labelled (by whom, blind to the system's answers);
    - per-question recall of needed evidence in the stacked context;
    - the corpus mean, against the owner's goal of 99 %.
  - **Corpora:** the dev tiers; `~/workspace` read-only; EXAMIN through this ticket's own clone of the owner's copy. W2-26's clone sits under `/tmp` and may be gone.
  - **Five modes compared:** lexical only (now ranked), semantic only, fused, fused plus reranker, and the lighter-reranker spike (DEC-074 Q3) [W2-L329].
  - **Indexing** time, peak RSS and incremental update per corpus, against DEC-078's envelope [W2-L102, W2-L321].
  - **The stacking test** (a question needing about 24k tokens, retrieved in 8k batches, assembled complete, no duplicates by span hash), run once as a baseline [AR-10].
  - Decision-level retrieval after W2-03 [AR-10]. The thin-margin cases and the two dev queries without gold paths are fixed or named [W2-M342, W2-L322, W2-M340].
- **Closes when:** the evidence record holds every measure per corpus and mode, with commands, versions and raw answers kept, and names the gaps that W2-32 will work on (at most three, chosen with the owner's approval of the metric).

## The wbs_id

This ticket has no `wbs_id`: the kernel's grammar (`common.schema.json`, `^W[0-9]+-[0-9]{2,}$`) refuses the letter suffix. Its W2 id is its `external-ref`, which `gov close` reads when `wbs_id` is absent (`src/gov/close/command.py`).
