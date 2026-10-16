---
id: DAEO-h4rh
status: open
deps: [DAEO-g0ip, DAEO-ym8a, DAEO-u4oz, DAEO-0z8c, DAEO-kia7, DAEO-7r5e, DAEO-a3m2, DAEO-cuao, DAEO-49o5, DAEO-057v, DAEO-r30l, DAEO-1ahb, DAEO-kmcr, DAEO-2ds6, DAEO-ha8z, DAEO-kl5e]
links: []
created: 2026-10-16T16:35:11Z
type: task
priority: 1
assignee: orchestrator
external-ref: W2-27
tags: [wave-2, integration, full]
wbs_id: W2-27
title: EXAMIN adoption on a copy
class: integration
state_class: AUTHORITATIVE
role: orchestrator
depends_on:
- DAEO-g0ip
- DAEO-ym8a
- DAEO-u4oz
- DAEO-0z8c
- DAEO-kia7
- DAEO-7r5e
- DAEO-a3m2
- DAEO-cuao
- DAEO-49o5
- DAEO-057v
- DAEO-r30l
- DAEO-1ahb
- DAEO-kmcr
- DAEO-2ds6
- DAEO-ha8z
- DAEO-kl5e
allowed_paths:
- docs/plan/wave-2/examin-copy/**
kpis:
  success:
  - The pinned, hash-verified release is installed (W2-16, W2-18).
  - gov adopt runs A0 to A6 and A8 with the A5 independent review, and the lite A7 and A10 gates of Contract v4.2.
  - EXAMIN's own CLAUDE.md, settings and untracked files are preserved (W2-23).
  - gov doctor and gov check are green.
  - 'One LITE ticket goes through the full cycle: test designer, red, implement, green, then gov close at exit 0 with EXAMIN''s own test command.'
  - Its governance share is measured and ≤ 15 %.
  failure: []
profile: FULL
sources:
- DEC-727
- DEC-728
est_loc: 0
acceptance_tests:
  judged_by: 'its class (WBS §0 rule 1, W2-07): its named evidence files'
track: B
closes:
- Track B
list_rows: []
---
# W2-27 EXAMIN adoption on a copy

Card: `docs/plan/WAVE_2_WBS.md` §2 (W2-27), as approved (DEC-729). The list rows it takes in are in `list_rows` and in `docs/plan/WAVE_2_TRIAGE.md`; a row's state is re-checked against the code when the ticket picks it up (DEC-718).

- **Depends on (DEC-727):** W2-01, W2-03, W2-04, W2-05, W2-06, W2-08, W2-09, W2-10, W2-16, W2-18, W2-20, W2-21 and W2-23; W2-26; W2-49 (the lite gates); W2-50 (the clone's folder, DEC-728); and W2-19 and W2-45 if W2-26 says so. W2-07 lands before it by rule 1.
- **Allowed paths:** `docs/plan/wave-2/examin-copy/**` (evidence); the clone at `~/gov-os-runs/W2-27/examin/` only.
- **KPIs:**
  - The pinned, hash-verified release is installed (W2-16, W2-18).
  - `gov adopt` runs A0 to A6 and A8 with the A5 independent review, and the lite A7 and A10 gates of Contract v4.2.
  - EXAMIN's own `CLAUDE.md`, settings and untracked files are preserved (W2-23).
  - `gov doctor` and `gov check` are green.
  - One LITE ticket goes through the full cycle: test designer, red, implement, green, then `gov close` at exit 0 with EXAMIN's own test command.
  - Its governance share is measured and ≤ 15 %.
