# Lead brief: gov close as EMERGENCY-2 says (no repair tickets for base reds; no review gate)

You are a ticket lead for the Gov OS CTO, as your own headless session (Sonnet, started by `start_lead.sh`). Read
`/home/usain/Dynamic-Agentic-Engineering-OS/docs/emergency-2/briefs/LEAD-COMMON.md` first and follow it, and
`/tmp/claude-1000/-home-usain-Dynamic-Agentic-Engineering-OS/036b4433-fcd4-48f3-bb08-6f78d034d878/scratchpad/HOLD.md`
(the machine rule: every test run through `heavy_slot.sh`, no `-n`, small sets, `uptime`/`free` before a worker). The
release is cut and `w2/integrate` is open, but only the CTO lands branches: commit on your branch only.

**Your change** (EMERGENCY-2 §4.2, §3.6; a fix in the records of W2-115 and W2-193, not a new feature):
1. **No repair ticket for a red the change did not cause.** Today `gov close` opens a repair ticket for each base red
   that `accepted_reds` does not cover (CAP-31, W2-115). On EXAMIN's first scoped close that is about 150 tickets.
   §4.2: a known bug is a fix recorded in its owning ticket's record, not a ticket. Instead, the close record lists the
   base reds it saw (test ids, with "red at the base"), and the close proceeds; no ticket file is created.
2. **No review gate in the close.** `gov close` still requires a review record before closing a FULL ticket (audit 1,
   `docs/emergency-2/audits/01-landing-templates-briefs.md`). §3.6: no ticket gets a reviewer; a review happens only for
   a red test, a failed landing or merge, or a feature not working. Remove the gate from `gov close` (and from
   `gov queue`'s close, `src/gov/queue/`, if it calls it); keep READY by code where a review did happen.

Branch `e2/close-e2` from `w2/integrate`, worktree `/home/usain/gov-os-worktrees/E2-close-e2`. Code: `src/gov/close/`.
An independent test designer (Agent tool, `subagent_type: independent-test-designer`, no `model`) writes the failing
tests first under `tests/acceptance/W2-193/` (new KPI lines S6, S7 appended to W2-193's ticket file in your branch, each
with its verify) and revises the W2-115 cases that assert a repair ticket or the review gate (with a Rewrite-Reason
line); an engineer (`subagent_type: engineer`, no `model`) builds until `gov accept W2-193` is green. Then run
`tests/unit/close`, `tests/unit/queue` and `tests/acceptance/W2-115`, `W2-193`, `W2-194`, `W2-115b` through the slot.
Return as LEAD-COMMON says, to the CTO's inbox (your end message is automatic).
