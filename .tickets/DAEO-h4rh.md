---
id: DAEO-h4rh
status: open
deps: [DAEO-g0ip, DAEO-ym8a, DAEO-u4oz, DAEO-0z8c, DAEO-kia7, DAEO-7r5e, DAEO-a3m2, DAEO-cuao, DAEO-49o5, DAEO-057v, DAEO-r30l, DAEO-1ahb, DAEO-kmcr, DAEO-2ds6, DAEO-ha8z, DAEO-kl5e, DAEO-jzvg]
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
- DAEO-jzvg
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
  - At the first full gov rebuild after adoption, each index's time, peak RSS and node and edge counts on EXAMIN are measured with W2-26's method and RSS sampler, against DEC-078's envelope; a figure over the envelope stops the ticket, and W2-45 joins its dependencies [DEC-735].
  - Before any known-red list, a diagnosis hour sorts EXAMIN's red tests into environment reds and real ones, using the owner's answer on whether its governance suite passes in the owner's environment.
    Then the reds go into W2-19's ratchet baseline (exact id, owner, cause class, how it shrinks), which the owner accepts [DEC-736].
  - One pinned install package goes to the owner. It holds EXAMIN's 10 product-suite packages from EXAMIN's own lock file, installed into the clone's own virtual environment only. With the owner's approval,
    the product suite is measured before W2-30's verdict. Until then it is "needs environment", reported UNMEASURED by name and never as passed [DEC-736].
  - EXAMIN's governance kit stays in a legacy namespace, and its tests stay in the declared test command. The A5 review maps each of its checks to a Gov OS check family or to "no equivalent" [DEC-736].
  - The path map marks the tool-configuration folders (.claude/commands/ and the kit's .claude/ templates) as not records. The files in spec/5-REPORTS/attempts/ get a mechanical quoting fix of their front
    matter with no change of content, as an adoption commit. If the store cannot leave paths unread, all 18 files get the fix [DEC-736].
  - EXAMIN's own CLAUDE.md, AGENTS.md and .claude/commands/ are never silently overwritten. Their content is migrated into EXAMIN's rulesync sources or kept in place, and the A5 review checks that nothing
    of the owner's was lost [DEC-736].
  failure: []
profile: FULL
sources:
- DEC-727
- DEC-728
- DEC-735
- DEC-736
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

- **Depends on (DEC-727):** W2-01, W2-03, W2-04, W2-05, W2-06, W2-08, W2-09, W2-10, W2-16, W2-18, W2-20, W2-21 and W2-23; W2-26; W2-49 (the lite gates); W2-50 (the clone's folder, DEC-728); W2-19 (DEC-736: `gov close` runs its regression only over `tests/`, and EXAMIN's suites are elsewhere); and W2-45 if the index measures say so (DEC-735). W2-07 lands before it by rule 1.
- **Allowed paths:** `docs/plan/wave-2/examin-copy/**` (evidence); the clone at `~/gov-os-runs/W2-27/examin/` only.
- **KPIs:**
  - The pinned, hash-verified release is installed (W2-16, W2-18).
  - `gov adopt` runs A0 to A6 and A8 with the A5 independent review, and the lite A7 and A10 gates of Contract v4.2.
  - EXAMIN's own `CLAUDE.md`, settings and untracked files are preserved (W2-23).
  - `gov doctor` and `gov check` are green.
  - One LITE ticket goes through the full cycle: test designer, red, implement, green, then `gov close` at exit 0 with EXAMIN's own test command.
  - Its governance share is measured and ≤ 15 %.
  - At the first full `gov rebuild` after adoption, each index's time, peak RSS and node and edge counts on EXAMIN are measured with W2-26's method and RSS sampler (`docs/research/EXP-003/examin/`), against DEC-078's envelope. A figure over the envelope stops the ticket, and W2-45 joins its dependencies [DEC-735].
  - Before any known-red list, a diagnosis hour sorts EXAMIN's red tests into environment reds and real ones, using the owner's answer on whether its governance suite passes in the owner's environment. Then the reds go into W2-19's ratchet baseline (exact id, owner, cause class, how it shrinks), which the owner accepts [DEC-736].
  - One pinned install package goes to the owner. It holds EXAMIN's 10 product-suite packages from EXAMIN's own lock file, installed into the clone's own virtual environment only. With the owner's approval, the product suite is measured before W2-30's verdict. Until then it is "needs environment", reported UNMEASURED by name and never as passed [DEC-736].
  - EXAMIN's governance kit stays in a legacy namespace, and its tests stay in the declared test command. The A5 review maps each of its checks to a Gov OS check family or to "no equivalent". Retirement is the owner's decision later, judged on function, never to clear reds [DEC-736].
  - The path map marks the tool-configuration folders (`.claude/commands/` and the kit's `.claude/` templates) as not records. The files in `spec/5-REPORTS/attempts/` get a mechanical quoting fix of their front matter with no change of content, as an adoption commit. If the store cannot leave paths unread, all 18 files get the fix [DEC-736].
  - EXAMIN's own `CLAUDE.md`, `AGENTS.md` and `.claude/commands/` are never silently overwritten. Their content is migrated into EXAMIN's rulesync sources or kept in place, and the A5 review checks that nothing of the owner's was lost [DEC-736].
- **Correction (DEC-736):** DEC-735 item 2 said W2-19 does not join this ticket, because EXAMIN's tests are pytest. That was wrong. `gov close` runs its regression only over `tests/`, whatever the language, so W2-19 is now in `deps`.
