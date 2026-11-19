# Lead brief: a fix under a closed ticket lands and relaunches (a fix under W2-201, `DAEO-k1us`; DEC-1219 (5); release 0.1.4)

Read `docs/emergency-2/briefs/LEAD-COMMON.md` first and follow it. Name: `rubric-tickets-2`; worktree
`/home/usain/gov-os-worktrees/E2-rubric-tickets-2`, branch `e2/rubric-tickets-2` from `w2/integrate` (it now holds the
first part: `gov launch --fix` / `--chore` and the landing's `NEW_TICKET_NOT_FEATURE`, merged `2031f758d`; read
`.tickets/DAEO-k1us.md`'s section "Fix: what becomes a ticket (DEC-1219 (5))" and `tests/acceptance/W2-201/README.md`
rows S10 to S14).

**Kind:** a fix under W2-201, recorded in `DAEO-k1us.md` (append X6 to X8 to that section, the README maps them as the
next S numbers, `gov accept` reads only S/F/K names). No new ticket. Every commit `Task: DAEO-k1us`.

**The gaps the first part found (its lead's return), which break the owner's model:** a fix is recorded in its owning
ticket, open or closed (EMERGENCY-2 4.2), but:
- **X6 A fix branch under a closed ticket lands through `gov queue`.** Today `gov queue` refuses a ticket that is closed at
  the integration head (`TICKET_CLOSED`). A branch whose commits say they are a fix (the launch kind `fix`, or the
  branch's commits carrying the owning ticket's `Task:` while the ticket is closed: use the signal the first part
  already records; say which) lands, runs its impact-selected tests and the owning ticket's acceptance folder, and
  appends a fix line to the owning ticket's record (or its close record: the form the landing already writes) instead
  of closing it again. A branch for a closed ticket that is not a fix is still refused as today. Verify: planted
  branches through `gov queue` (or its dry-run seam): a fix branch on a closed ticket lands and the record gains the
  line; a plain branch on a closed ticket is refused.
- **X7 `gov relaunch` keeps the kind.** A dead fix or chore session relaunches as the same kind with its line (today it
  restarts as a plain launch and is refused). Verify: a planted dead fix launch and a dead chore launch relaunch with
  `kind` and line kept.
- **X8 A worker fix gets a run folder.** A worker launched with `--fix` on a closed ticket gets the run folder an
  `in_progress` ticket's worker gets (or the launcher states plainly where its runs go). Verify: the planted launch
  shows the folder.

**Order:** your spec lines in the ticket → independent test designer (C3, Opus, prompt carrying `Task: DAEO-k1us`):
new cases under `tests/acceptance/W2-201/`, red on the base → engineer (Opus, `Task: DAEO-k1us`) until
`gov accept W2-201` is green → green: `gov accept W2-201`, `tests/unit/launch`, `tests/unit/queue`, W2-202, W2-206,
`tests/unit/optin`. **Do not merge.** Return: branch and head, each X line with its tests, the summary lines, reds not
yours.

Not here: `gov update` and the kit template (lead kit-e2); test retirements (lead ti-cuts).
