---
id: DAEO-rd0g
status: closed
deps: [DAEO-g0ip, DAEO-ym8a, DAEO-u4oz, DAEO-r9ss, DAEO-zqvn, DAEO-kl5e, DAEO-h2k3]
links: []
created: 2026-10-16T16:35:11Z
type: task
priority: 1
assignee: research
external-ref: W2-15a
wbs_id: W2-15a
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
- DAEO-h2k3
allowed_paths:
- docs/research/EXP-003/**
- experiments/EXP-003/**
kpis:
  success:
  - 'The metric is defined and recorded before the first run [AR-10]: what counts as a hit; how the needed evidence for each question is labelled (by whom, blind to the system''s answers); per-question recall of needed evidence in the stacked context; the corpus mean, against the owner''s goal of 99 % Answered by DEC-954 Q9 and DEC-957: the metric is W2-61''s measure, both figures, on the enlarged set of 48 questions (24 visible, 24 hidden), the hidden half used only once the five-rule hook and W2-84 refuse it from every worktree; hit@5 is judged against the owner''s target of 95 % with CAP-10''s 85 the floor, memory proven on the hidden half at least 21 of 24, judged on the combined memory spec (Q9c) [DEC-954 Q9, DEC-957] [changed, DEC-1171 (3)] Verify: the evidence record under docs/research/EXP-003/ has a metric section committed before the pass''s first run (its commit an ancestor of the first commit holding the pass''s raw outputs, and every raw output dated after it) that states what counts as a hit; who labelled each question''s needed evidence, blind to the system''s answers; per-question recall of needed evidence in the stacked context; and the corpus mean; and, as DEC-1171 (3) decides Q-2 (a): W2-61''s measure, both figures, on the current set (40 visible; 39 hidden until the half is back at 40): hit@5 against the owner''s 95 % with CAP-10''s 85 % the floor, the share of questions whose stacked context holds all their needed evidence against 99 %, and memory proven at a hidden hit@5 of at least 34 of 39 (35 of 40 once the half is 40); every hidden-half figure in the record is copied from the record of the owner''s operator''s walled run (counts, ids, ranks and pass or fail only, never a question or an answer), whose run follows a recorded refused probe read of the sets root''s hidden folder from a worktree; no launched session reads hidden content'
  - 'Five modes compared: lexical only (now ranked), semantic only, fused, fused plus reranker, and the lighter-reranker spike (DEC-074 Q3) [W2-L329]. Verify: the evidence record''s mode table holds, for the corpus this pass measures (this repository; the other corpora moved to W2-15b, DEC-1083), one row for each of the five modes: lexical only (ranked), semantic only, fused, fused plus reranker, and the lighter-reranker spike (DEC-074 Q3); each row gives both W2-61 figures on the visible half and the hidden counts from the operator''s walled-run record, with its command, versions and raw output under docs/research/EXP-003/w2-15a/raw/; a mode with no row (pass 1''s lighter reranker, not installed) leaves the line unmet'
  - 'The stacking test (a question needing about 24k tokens, retrieved in 8k batches, assembled complete, no duplicates by span hash), run once as a baseline [AR-10]. Verify: the evidence record holds one stacking-test run: a question whose needed evidence is about 24k tokens, retrieved in batches of at most 8k tokens and stacked, with its command, its raw output under docs/research/EXP-003/w2-15a/raw/ and the result of each check, assembled complete (each stacked item''s sha256 equal to its span''s bytes in the measured clone, no item cut) and duplicates by span hash (their count), as pass 1''s section 6 and raw/stack-q14.json record them; a check that fails is recorded as failing, it is a baseline'
  - 'Closes when the evidence record holds every measure per corpus and mode, with commands, versions and raw answers kept, and names the gaps that W2-32 will work on (at most three, chosen with the owner''s approval of the metric). [changed, DEC-1171 (3)] Verify: the evidence record holds, for each of the five modes on the corpus this pass measures, every measure of S1 to S3 with its command, the gov, model and reranker versions, the clone''s commit and the store''s digest, and the raw answers kept under docs/research/EXP-003/w2-15a/raw/ (each figure re-derived from them by the record''s table script, the same figures); and it names at most three gaps, chosen with the owner''s approval of the metric, which DEC-1171 (3) sends to W2-15b (W2-32 is closed), each with the misses it is meant to reach'
  failure: []
  moved:
  - 'Corpora: the dev tiers; ~/workspace read-only; EXAMIN through this ticket''s own clone of the owner''s copy. W2-26''s clone sits under /tmp and may be gone. [moved to W2-15b, DEC-1083] (was S2)'
  - 'Indexing time, peak RSS and incremental update per corpus, against DEC-078''s envelope [W2-L102, W2-L321]. [moved to W2-15b, DEC-1083] (was S4)'
  - 'Decision-level retrieval after W2-03 [AR-10]. The thin-margin cases and the two dev queries without gold paths are fixed or named [W2-M342, W2-L322, W2-M340]. [moved to W2-15b, DEC-1083] (was S6)'
profile: FULL
sources:
- DEC-074
- DEC-078
- DEC-954
- DEC-957
- DEC-1055
- DEC-1072
- DEC-1083
- DAEO-swdu
- DEC-1171
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

**D9-FATES (DEC-1083):** Close formally at the lift (DEC-1083), lines met: S1, S5 and S7 (`ff691ec2`, `docs/research/EXP-003/w2-15a-baseline.md`); met in part: S3 (its lighter reranker was not run, not installed); S2, S4 and S6 moved to W2-15b (the cold-rebuild peak RSS moves with S4). The CTO closes it at the lift (P1-13). The numbers above are D9-FATES': S2, S4 and S6 are now under `kpis.moved`, so S3, S5 and S7 are now S2, S3 and S4.

**Claimed 2026-11-15 by the CTO (DEC-1186 (3), DEC-1171 (3); package P-W2-15A-CLOSE):** the close run. A research session (1) rewrites section 2 of `docs/research/EXP-003/w2-15a-baseline.md` as the metric for the current set (40 visible, 39 hidden; W2-61's measure, both figures; pass at 34 of 39 or 35 of 40) and commits it before any new run; (2) records one refused probe of the sets root's hidden folder from its own worktree (a Read of a file that does not exist, the guard's refusal recorded, no content); (3) prepares the record's table from the visible run and the operator's counts. The CTO's visible run and the owner's operator's walled hidden run (counts only, `drafts/w2-15a-close/walled_hidden_counts.sh`) follow at one named head after the re-pin's done, never beside a store rebuild. On a miss: the record as measured, at most three gaps to W2-15b, S1's memory clause re-worded to "recorded against 34 of 39" (DEC-1186 (3)).
