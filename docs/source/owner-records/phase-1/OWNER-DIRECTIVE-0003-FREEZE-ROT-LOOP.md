# OWNER-DIRECTIVE-0003 — Freeze the Root-of-Trust revision loop after Revision 7

| Field | Value |
|---|---|
| Record | OWNER-DIRECTIVE-0003 |
| Source | the product owner, in the Phase 1 orchestration chat, 2026-09-14, during the revision-7 review panel (reviewer B completed, reviewer C running) |
| Classification | **binding orchestration directive**: stop the RoT architecture loop after the revision-7 verdict |
| Not | an architecture verdict, D-0008 approval or activation, or an owner option |
| Terminal next action | `PHASE_1_ROOT_OF_TRUST_LOOP_FROZEN_PENDING_META_ARCHITECTURE_REVIEW` |
| Recorded by | the Phase 1 orchestrator. The text below is the owner's message **verbatim** and is authoritative. |

## Verbatim owner text

```text
Stop the Root-of-Trust revision loop after Revision 7.

Do NOT create Revision 8.

Do NOT spawn another architecture author after the Revision-7 verdict.

Complete only the work already in flight for Revision 7:

1. allow Reviewer B evidence to be finalised and preserved;
2. allow Reviewer C to finish;
3. run the already-planned fresh synthesis reviewer;
4. record the final Revision-7 verdict regardless of whether it is ACCEPTED or REJECTED.

If Revision 7 is rejected, record all findings but DO NOT route them into another repair/revision loop.

If Revision 7 is accepted, record the acceptance but DO NOT proceed to implementation or formal D-0008 activation yet.

Before stopping, persist a complete durable checkpoint containing:

- exact Revision-7 architecture commit;
- Reviewer B commit/report/evidence;
- Reviewer C commit/report/evidence;
- synthesis review commit/report/evidence;
- final Revision-7 verdict;
- all CRITICAL/HIGH/MEDIUM/LOW findings;
- status of OT-1 and OT-2;
- current D-0008 state;
- confirmation D-0007 remains unchanged/active unless already lawfully superseded;
- OP-1 through OP-16 owner requirements;
- every Root-of-Trust revision 1–7 commit and verdict;
- all corresponding review report locations;
- unresolved findings;
- exact current branch/HEAD;
- working-tree status;
- orchestration state;
- next action explicitly set to:

"PHASE_1_ROOT_OF_TRUST_LOOP_FROZEN_PENDING_META_ARCHITECTURE_REVIEW"

Do not modify runtime/kernel implementation.

Do not open new owner options.

Do not attempt to solve new findings.

Stop after the Revision-7 evidence package is complete.
```
