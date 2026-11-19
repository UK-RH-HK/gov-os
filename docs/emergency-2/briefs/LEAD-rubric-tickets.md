# Lead brief: what becomes a ticket, in code (a fix under W2-201, `DAEO-k1us`; the owner, DEC-1219 (5); release 0.1.4)

Read `docs/emergency-2/briefs/LEAD-COMMON.md` first and follow it (worktree, the machine rule, memory first, the flow,
trailers, models). This page names your work. Name: `rubric-tickets`; worktree
`/home/usain/gov-os-worktrees/E2-rubric-tickets`, branch `e2/rubric-tickets` from `w2/integrate`.

**The owner's words (DEC-1219 (5), `docs/DECISION_REGISTER.md`):** "Only half the rubric is in code: the model and
effort part is (W2-201), but what becomes a ticket is not, and a lead can only be launched against a ticket. Fix that in
code, in release 0.1.4: the launcher accepts a fix under its owning ticket and a chore with no ticket; a new ticket must
be a feature with its spec and KPIs, flagged at the landing if not, never refused." And (6): "From now on, open a new
ticket only for a new feature."

**What kind of work this is:** a **fix** in W2-201's feature (the rubric in code), not a new ticket (EMERGENCY-2 4.2).
No new ticket file. Record it in `.tickets/DAEO-k1us.md`: append a section `## Fix: what becomes a ticket (DEC-1219 (5))`
with the fix lines below (each observable, each with its verify), and leave the ticket `closed`. Every commit says
`Task: DAEO-k1us`.

**The rubric to encode** (EMERGENCY-2 4.1, 4.2, 4.6; audit 4's Table 3 in `docs/emergency-2/audits/`, read it):
- *feature*: a ticket with a spec and KPIs;
- *fix*: a known bug in a feature, recorded in its owning ticket (open or closed), failing test first when no test caught it;
- *chore*: records, docs, configuration, kernel text, a tidy-up with the tests unchanged and green; a direct commit, no ticket.

## The fix lines (the CTO's; refine the wording, keep the behaviour)
- **X1 A fix launches under its owning ticket, closed or not.** `gov launch <role> <ticket> --fix "<one line>"` (or the
  form that fits the launcher's CLI best; say which) starts the role on the owning ticket even when that ticket is
  `closed`; the launch record states `kind: fix`, the owning ticket and the line; the model and effort come from the
  rubric for that ticket's class as today. Verify: a planted closed ticket launches with `--fix` (dry run / the
  launcher's test seam), the record carries the three fields; without `--fix` a closed ticket is refused as today.
- **X2 A chore launches with no ticket.** `gov launch <role> --chore "<one line>"` starts the role with no ticket;
  `GOV_TICKET` is unset or empty, the record states `kind: chore` and the line; model and effort from the role file's
  default in the rubric. Verify: a planted launch with `--chore` and no ticket id succeeds, its record says so.
- **X3 A lead launches the same way.** The lead roles (`orchestrator`, `lead`) accept `--fix` and `--chore` exactly as
  workers do. Verify: as X1 and X2 for the lead role.
- **X4 A new ticket that is not a feature is flagged at the landing, never refused.** When a branch landed by
  `gov queue` adds a ticket file under `.tickets/` that lacks a spec or KPI lines (no `kpis.success` line with its
  verify, or no spec: use the field the ticket schema already has for it; say which), the landing prints and records one
  notice `NEW_TICKET_NOT_FEATURE <id>: <what is missing>` and lands anyway. A new ticket that is a feature gives no
  notice; an edited existing ticket gives none. Verify: three planted branches through `gov queue` (or its `--dry-run`
  seam): a bad new ticket (notice, landed), a good one (no notice), an edit (no notice).
- **X5 Words match code.** The kernel lines that tell a CTO or lead how to launch work (the orchestration skill, the
  orchestrator, senior-engineer and ticket-lead role files and their generated copies) say: a new ticket only for a new
  feature; a fix launches under its owning ticket with `--fix`; a chore with `--chore`. The CTO approves this kernel text
  by naming it here (EMERGENCY-2 3.5): change only those lines, regenerate the copies with the project's generator.

## Order
1. Spec: write the fix lines into `DAEO-k1us.md` (your commit, `Role: orchestrator`).
2. Independent test designer (C3 work: `src/gov/launch/**` is in the criticality list; run it on Opus as LEAD-COMMON
   says, the prompt carrying the line `Task: DAEO-k1us`): new files under `tests/acceptance/W2-201/`, red on the base,
   mapped in that folder's README to X1 to X5; `Role: independent-test-designer`.
3. Engineer (Opus, `Task: DAEO-k1us`): builds until `gov accept W2-201 --root <worktree>` is green, all cases.
4. Green: `gov accept W2-201`, `tests/unit/launch`, `tests/unit/queue` (or wherever `gov queue`'s unit tests are),
   `tests/acceptance/W2-202`, `W2-206` (the queue's), `tests/unit/optin`.
5. Return: branch and head; each X line with its tests; the summary lines; reds not yours; anything for the owner as one line.

Not here: `gov pause` (G5-2, a separate fix); anything in `gov update` (a lead is working there).
