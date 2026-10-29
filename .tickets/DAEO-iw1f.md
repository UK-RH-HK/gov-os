---
id: DAEO-iw1f
status: open
deps: []
links: []
created: 2026-10-29T15:55:50Z
type: task
priority: 1
assignee: engineer
external-ref: W2-61
tags: [wave-2, implementation, standard, keystone-4]
wbs_id: W2-61
title: 'The standing 20-question measure, split under Policy 2 (d)'
class: implementation
state_class: AUTHORITATIVE
role: engineer
depends_on: []
allowed_paths:
- src/gov/retrieval/measure.py
- tests/unit/retrieval/test_measure*
- fixtures/evaluation/memory-retrieval/visible/**
- docs/research/W2-61-baseline.md
kpis:
  success:
  - 'Lens B''s 20 questions and their gold answers (docs/assessment/2026-10/B-memory-retrieval.md section 2) are the visible development half [DEC-828 item 4, DEC-820 (d)]'
  - 'A hidden measurement half of 20 more questions, with their gold answers, is written by a session independent of the retrieval tickets and stored under fixtures/evaluation/memory-retrieval/hidden/, where the path map''s evaluation_sets block (memory-retrieval) refuses it to the measured roles [DEC-828 item 3, DEC-820 (d), DEC-845 item 2]'
  - 'A measurement script reports, per question and in total, whether the governing source is in the first five and in the bundle, and repeatability on an unchanged index and after a rebuild; it prints scores, never the hidden answers [DEC-828 item 4, DEC-820 (d)]'
  - 'Both figures, always together: hit@5 against CAP-10''s floor of 85, and the share of questions whose stacked context holds all their needed evidence, across batches, against the owner''s target of 99 % [DEC-833 items 1 to 3]'
  - 'Stacked, never giant: each question is answered by retrieval in batches, ranked and stacked within the budget, never one giant query or context; the script measures the stacked answer [DEC-860 items 1 to 3]'
  - 'The same split for EXAMIN''s set, written by a session independent of the adopting team before W2-27; EXP-003''s gold answers (W2-15a, W2-15b) split the same way [DEC-828 item 3]'
  - 'The baseline: the first measure runs today on the pinned stores, both halves, and is recorded in docs/research/W2-61-baseline.md with the pinned gov''s version and commit and the stores'' fingerprint; the same measure is repeated after each ticket of the memory chain, beside the baseline [DEC-941, DEC-833 item 3]'
  failure:
  - A measured role can read the hidden half by a route an honest agent takes in ordinary work.
  - The script prints, logs or writes a hidden question's gold answer.
  - A figure reported without the other.
  - A hit counted from lens B's own report or from the evaluation files rather than from the governing source.
profile: STANDARD
sources:
- DEC-828
- DEC-833
- DEC-860
- DEC-820
- DEC-845
- DEC-825
- DEC-941
est_loc: 180
acceptance_tests:
  path: tests/acceptance/W2-61/
  author: independent-test-designer (MR-3); written before implementation; the planted evaluation set built at test time, never the real hidden half
track: A
list_rows: []
---
# W2-61 The standing 20-question measure, split under Policy 2 (d)

Card: `docs/plan/WAVE_2_WBS.md` §2 (W2-61), from the accepted plan's §4.4, order 6 (DEC-828 item 4, DEC-831); ticket file at its start (DEC-825 item 7). Starts first in the memory chain, today, as its baseline (the re-plan the owner accepted on 2026-10-29, DEC-941).

- **Why:** lens B's 20 questions become the standing measure at each release and on EXAMIN's copy (DEC-828). Memory (keystone 4) is now on the critical path for EXAMIN's copy, and lens B's 65 % hit@5 is the last figure; the re-plan's date moves on this baseline.
- **Place:** first in block B; W2-03, W2-55, W2-64, W2-04, W2-05, W2-06, W2-13 and W2-15a follow, and the measure is repeated after each. W2-58's refusal (d) is merged (`4845b9b8`) and in the second pin (`5c401220`); W2-58's close is still pending, so it is not a `depends_on`.
- **The split (card):** the questions by an independent auditor session, the script by an engineer. This ticket's role and paths are the engineer's. The engineer is a measured role (`measures: roles: [engineer, research]`), so it never reads the hidden half; its tests use a planted set.
- **The auditor session's files** (named here, not in the engineer's paths): `fixtures/evaluation/memory-retrieval/hidden/**`, the 20 hidden questions and their gold answers.
