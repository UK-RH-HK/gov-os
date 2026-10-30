---
id: DAEO-0mab
status: open
deps: [DAEO-g0ip, DAEO-zflj, DAEO-ym8a, DAEO-u4oz, DAEO-0z8c, DAEO-kia7, DAEO-r9ss, DAEO-7r5e, DAEO-a3m2, DAEO-cuao, DAEO-k7hz, DAEO-j8gn, DAEO-zqvn, DAEO-7y6v, DAEO-rd0g, DAEO-49o5, DAEO-sdhj, DAEO-057v, DAEO-jzvg, DAEO-r30l, DAEO-1ahb, DAEO-xm6l, DAEO-kmcr, DAEO-xxgp, DAEO-ha8z, DAEO-kl5e, DAEO-7rr2]
links: []
created: 2026-10-16T16:35:11Z
type: task
priority: 1
assignee: orchestrator
external-ref: W2-24
tags: [wave-2, integration, full]
wbs_id: W2-24
title: Track A gate run
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
- DAEO-xxgp
- DAEO-ha8z
- DAEO-kl5e
- DAEO-7rr2
allowed_paths:
- docs/plan/wave-2/track-a-gate/**
kpis:
  success:
  - From a fresh orchestrator session in accept-edits mode, one lead starts with gov launch lead, with no classifier denial and no permission given by hand; the launch is recorded [AR-10, DEC-716].
  - 'A release is cut and hash-verified, then installed pinned into a fresh copy of a non-Python dev fixture (the W2-19 TypeScript fixture) [AR-10, CAP-43.b lite]: the fixture is adopted (A0 to A6, A8);
    gov doctor and gov check are green there; one ticket closes with gov close at exit 0, using the fixture''s own test command'
  - gov update moves the fixture to a second release and back [CAP-45.a].
  - The full, uncached regression runs once and is green (DEC-726).
  - AR-1 to AR-10 are each shown to pass, in order, with the evidence path of each (DEC-721). EXP-003's line is shown by W2-15a.
  failure:
  - Any AR line not shown; the fixture importing this repository's src/.
profile: FULL
sources:
- DEC-716
- CAP-43.b
- CAP-45.a
- DEC-726
- DEC-721
est_loc: 0
acceptance_tests:
  judged_by: 'its class (WBS §0 rule 1, W2-07): its named evidence files'
track: A
closes:
- AR-1 … AR-10
list_rows:
- W2-I035
---
# W2-24 Track A gate run

Card: `docs/plan/WAVE_2_WBS.md` §2 (W2-24), as approved (DEC-729). The list rows it takes in are in `list_rows` and in `docs/plan/WAVE_2_TRIAGE.md`; a row's state is re-checked against the code when the ticket picks it up (DEC-718).

- **Allowed paths:** `docs/plan/wave-2/track-a-gate/**` (evidence); fixture clones under `~/gov-os-runs/W2-24/`.
- **KPIs:**
  - From a fresh orchestrator session in accept-edits mode, one lead starts with `gov launch lead`, with no classifier denial and no permission given by hand; the launch is recorded [AR-10, DEC-716].
  - A release is cut and hash-verified, then installed pinned into a fresh copy of a non-Python dev fixture (the W2-19 TypeScript fixture) [AR-10, CAP-43.b lite]:
    - the fixture is adopted (A0 to A6, A8);
    - `gov doctor` and `gov check` are green there;
    - one ticket closes with `gov close` at exit 0, using the fixture's own test command.
  - `gov update` moves the fixture to a second release and back [CAP-45.a].
  - The full, uncached regression runs once and is green (DEC-726).
  - AR-1 to AR-10 are each shown to pass, in order, with the evidence path of each (DEC-721). EXP-003's line is shown by W2-15a.
- **Failure:** any AR line not shown; the fixture importing this repository's `src/`.
