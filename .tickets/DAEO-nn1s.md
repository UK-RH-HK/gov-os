---
id: DAEO-nn1s
status: open
deps: [DAEO-g0ip, DAEO-zflj, DAEO-ym8a, DAEO-u4oz, DAEO-0z8c, DAEO-kia7, DAEO-r9ss, DAEO-7r5e, DAEO-a3m2, DAEO-cuao, DAEO-k7hz, DAEO-j8gn, DAEO-zqvn, DAEO-7y6v, DAEO-rd0g, DAEO-49o5, DAEO-sdhj, DAEO-057v, DAEO-jzvg, DAEO-r30l, DAEO-1ahb, DAEO-xm6l, DAEO-kmcr, DAEO-0mab, DAEO-btt7, DAEO-xxgp, DAEO-ha8z, DAEO-kl5e, DAEO-2ds6, DAEO-h4rh, DAEO-csj8, DAEO-swdu, DAEO-b926, DAEO-60rw, DAEO-wbdh, DAEO-0pyc, DAEO-lrre, DAEO-yadm, DAEO-2keg, DAEO-w19l, DAEO-6n5k, DAEO-g23i, DAEO-wudw, DAEO-6ox0, DAEO-s694, DAEO-fau3, DAEO-u5g6, DAEO-zndm, DAEO-neam, DAEO-7rr2]
links: []
created: 2026-10-16T16:35:12Z
type: task
priority: 1
assignee: orchestrator
external-ref: W2-46
tags: [wave-2, integration, full]
wbs_id: W2-46
title: Wave 2 exit run
class: integration
state_class: AUTHORITATIVE
role: orchestrator
depends_on:
- DAEO-g0ip
- DAEO-zflj
- DAEO-ym8a
- DAEO-u4oz
- DAEO-0z8c
- DAEO-kia7
- DAEO-r9ss
- DAEO-7r5e
- DAEO-a3m2
- DAEO-cuao
- DAEO-k7hz
- DAEO-j8gn
- DAEO-zqvn
- DAEO-7y6v
- DAEO-rd0g
- DAEO-49o5
- DAEO-sdhj
- DAEO-057v
- DAEO-jzvg
- DAEO-r30l
- DAEO-1ahb
- DAEO-xm6l
- DAEO-kmcr
- DAEO-0mab
- DAEO-btt7
- DAEO-xxgp
- DAEO-ha8z
- DAEO-kl5e
- DAEO-2ds6
- DAEO-h4rh
- DAEO-csj8
- DAEO-swdu
- DAEO-b926
- DAEO-60rw
- DAEO-wbdh
- DAEO-0pyc
- DAEO-lrre
- DAEO-yadm
- DAEO-2keg
- DAEO-w19l
- DAEO-6n5k
- DAEO-g23i
- DAEO-wudw
- DAEO-6ox0
- DAEO-s694
- DAEO-fau3
- DAEO-u5g6
- DAEO-zndm
- DAEO-neam
- DAEO-7rr2
allowed_paths:
- docs/plan/wave-2-exit/**
kpis:
  success:
  - 'Every exit criterion of §5 is run and evidenced, including: the full, uncached regression and the dev-tier regression, both green'
  - 'Every exit criterion of §5 is run and evidenced, including: a mid-programme specification change on a-dev that propagates through CIT-P → CIT-E with the correct impact set (WBS §6 exit)'
  - 'Every exit criterion of §5 is run and evidenced, including: every Wave 2 close record listed with its exit code'
  - 'Every exit criterion of §5 is run and evidenced, including: the governance share per programme, the EXAMIN pilot included'
  - 'Every exit criterion of §5 is run and evidenced, including: gov doctor green here and in EXAMIN.'
  failure: []
profile: FULL
sources:
- DEC-729
est_loc: 0
acceptance_tests:
  judged_by: 'its class (WBS §0 rule 1, W2-07): its named evidence files'
track: C
closes:
- Exit criteria
list_rows:
- W2-L340
- W2-M010
- W2-M343
---
# W2-46 Wave 2 exit run

Card: `docs/plan/WAVE_2_WBS.md` §2 (W2-46), as approved (DEC-729). The list rows it takes in are in `list_rows` and in `docs/plan/WAVE_2_TRIAGE.md`; a row's state is re-checked against the code when the ticket picks it up (DEC-718).

- **Allowed paths:** `docs/plan/wave-2-exit/**`.
- **KPIs:** every exit criterion of §5 is run and evidenced, including:
  - the full, uncached regression and the dev-tier regression, both green;
  - a mid-programme specification change on a-dev that propagates through CIT-P → CIT-E with the correct impact set (WBS §6 exit);
  - every Wave 2 close record listed with its exit code;
  - the governance share per programme, the EXAMIN pilot included;
  - `gov doctor` green here and in EXAMIN.
