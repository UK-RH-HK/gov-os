---
id: DAEO-7y6v
status: open
deps: [DAEO-g0ip, DAEO-u4oz, DAEO-r9ss, DAEO-zqvn, DAEO-kl5e]
links: []
created: 2026-10-16T16:35:11Z
type: task
priority: 1
assignee: orchestrator
external-ref: W2-14
tags: [wave-2, integration, full]
wbs_id: W2-14
title: ARGUS's full cycle, a-dev green, the governance share per programme
class: integration
state_class: AUTHORITATIVE
role: orchestrator
depends_on:
- DAEO-g0ip
- DAEO-u4oz
- DAEO-r9ss
- DAEO-zqvn
- DAEO-kl5e
allowed_paths:
- docs/plan/wave-2/argus-cycle/**
kpis:
  success:
  - B-dev is adopted far enough that its store holds the ticket's sources. ARGUS's implementation ticket closes with gov close at exit 0, then gov ci and the owner's merge after green CI; each is kept as
    evidence [AR-9, W2-L018].
  - B-dev's canaries run and hit [AR-9].
  - On a store freshly rebuilt with embeddings, a-dev's gov check is green on context reproducibility, claims and schema [AR-9].
  - Governance-share.json holds a measured share for ORION and for ARGUS, each ≤ 15 %, from the counter after clean closes, with every part measured; this evidence holds the requirement, W1-42's share case being retired (DEC-900) [F-M1, W2-H053, W2-L324, DEC-900].
  - ORION's test_exact_agreement is green, or named with its owner [W2-L341].
  failure:
  - Any clone held under /tmp or the workbench; a programme merge made by a lead.
profile: FULL
sources:
- DEC-723
- DEC-900
est_loc: 0
acceptance_tests:
  judged_by: 'its class (WBS §0 rule 1, W2-07): its named evidence files'
track: A
closes:
- AR-9
- F-M1
list_rows:
- W2-H053
- W2-L018
- W2-L266
- W2-L324
- W2-L337
- W2-L341
- W2-M180
- W2-M182
---
# W2-14 ARGUS's full cycle, a-dev green, the governance share per programme

Card: `docs/plan/WAVE_2_WBS.md` §2 (W2-14), as approved (DEC-729). The list rows it takes in are in `list_rows` and in `docs/plan/WAVE_2_TRIAGE.md`; a row's state is re-checked against the code when the ticket picks it up (DEC-718).

- **Allowed paths:** `docs/plan/wave-2/argus-cycle/**` (evidence); the dev-tier clones under `~/gov-os-runs/W2-14/`, made from the dev tiers by exact path (never `/tmp`, W2-M355; never the workbench, DEC-723).
- **KPIs:**
  - b-dev is adopted far enough that its store holds the ticket's sources. ARGUS's implementation ticket closes with `gov close` at exit 0, then `gov ci` and the owner's merge after green CI; each is kept as evidence [AR-9, W2-L018].
  - b-dev's canaries run and hit [AR-9].
  - On a store freshly rebuilt with embeddings, a-dev's `gov check` is green on context reproducibility, claims and schema [AR-9].
  - `governance-share.json` holds a measured share for ORION and for ARGUS, each ≤ 15 %, from the counter after clean closes, with every part measured; this evidence holds the requirement, W1-42's share case being retired (DEC-900) [F-M1, W2-H053, W2-L324, DEC-900].
  - ORION's `test_exact_agreement` is green, or named with its owner [W2-L341].
- **Failure:** any clone held under `/tmp` or the workbench; a programme merge made by a lead.
