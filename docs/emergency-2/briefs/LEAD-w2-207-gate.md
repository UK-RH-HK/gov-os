# Lead brief: W2-207, one machine-wide gate (DEC-1246 (3)(a), DEC-1247)

You are a ticket lead (Sonnet, medium), started by the Gov OS CTO on 2026-11-24. **Read `docs/emergency-2/briefs/LEAD-COMMON.md` first: every rule there applies.** Decide, never ask (I-10). Where this brief leaves a choice, make it inside W2-207 and say what you chose in your return.

## Why
W2-207 (`.tickets/DAEO-rt4s.md`, open) is built and green on two held branches: `e2/w2-207-runtime` (worktree `/home/usain/gov-os-worktrees/E2-w2-207-runtime`) and `e2/w2-207-pre-retire`, each about 207 commits behind `w2/integrate`. Its brief, with KPI lines MA-1 to MA-6, is `docs/emergency-2/briefs/LEAD-w2-207-runtime.md` (read it whole; MA-6 is new, DEC-1247). Since it was built, the owner decided (DEC-1246 (3)(a), read it in `docs/DECISION_REGISTER.md`): three repositories now run at once on this machine (Gov OS, EXAMIN at `/home/usain/gov-os-runs/W2-27/examin`, ASMO OS at `/home/usain/ASMO-OS-V1`), so the dispatcher and load balancer become **one machine-wide gate over every repository's sessions, leads, test slots and GPU work**: work waits for a slot instead of starting; capacity read, never assumed. It ships in 0.1.6; the CTO does the live cut-over by the runbook after you return.

## What
1. **Bring both branches up to date:** `git merge w2/integrate` into each (in the existing worktree for `e2/w2-207-runtime`; a new worktree `/home/usain/gov-os-worktrees/E2-w2-207-pre-retire` for the other). Resolve conflicts keeping `w2/integrate`'s behaviour plus W2-207's. Their own tests green after the merge.
2. **MA-6** on `e2/w2-207-runtime`, as its brief states it.
3. **The machine-wide gate**, KPI lines written into the ticket on your branch (the CTO approves them by this brief):
   - **MG-1 One gate per machine.** Its state lives under `~/.gov-os/` (machine state, in no repository). Every repository's `gov launch`, lead start, product test slot and GPU job takes its slot from it, so the counts of all repositories add up against one limit (the MA-1/MA-2 rules over the machine reading). A repository is named in each slot's record.
   - **MG-2 Wait, never start over the limit.** Work beyond the limit waits for a slot, in request order, the wait logged with repository, kind and the resource that is short; it starts when a slot frees. Only MA-3 (a machine too small) refuses.
   - **MG-3 Sessions it did not start count too.** Interactive sessions (each repository's CTO, on Opus) and any `claude` process found in the process table are counted against memory and sessions by their resident memory, so a new lead waits when the CTOs take the room.
   - **MG-4 A dead holder frees its slot** within one pass (its process gone), so a crashed session never keeps a slot.
   - **MG-5 Proved on planted repositories:** three planted repositories each asking for more than the planted machine holds: the total in use never exceeds the limit, each repository's waiting work starts in request order, a killed holder's slot is reused within one pass; with MA-4's profiles.
4. **The runbook** (`docs/emergency-2/W2-207-CUTOVER-RUNBOOK.md` on the branch): update its steps for the gate, MA-6 and the merged base, each step with its exact command, its check and its rollback. Name the cron and hook lines in EXAMIN and ASMO OS the cut-over must touch, if any (read only; never write outside your worktrees).

Code area: `src/gov/dispatch/`, `src/gov/resources/`, the slot code, `governance/project/orchestration/`. Stay out of `src/gov/rebuild*`, `src/gov/status*`, `src/gov/launch/` beyond the call that takes a slot, and `src/gov/decisions/` (other leads work there).

## Green
LEAD-COMMON's flow; the test designer writes MA-6 and MG-1 to MG-5's acceptance tests in the ticket's acceptance folder (red on the base), the engineer builds. Then the impact-selected suites for each branch: `PYTHONPATH=<worktree>/src python3 -m gov.cli.main queue w2-207=e2/w2-207-runtime --onto w2/integrate --select` (and the same for `e2/w2-207-pre-retire`); run exactly those lists through the heavy slot (DEC-1244 X-1). Check the acceptance trailers on both branches (LEAD-COMMON; only `independent-test-designer`).

## Return
Both branches and heads; each KPI line (MA-1 to MA-6, MG-1 to MG-5) with its tests and result; the selected suites' summary lines; reds not yours; the runbook's path and its step list in one line each; the capacity reading on this machine (limits it computes for leads, test slots and memory with the CTOs running); the C3-trial counts.
