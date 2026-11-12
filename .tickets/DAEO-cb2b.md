---
id: DAEO-cb2b
status: in_progress
deps: [DAEO-r30l]
links: [DAEO-zkr9, DAEO-r30l, DAEO-ts4y]
created: 2026-11-01T20:10:00Z
type: task
priority: 1
assignee: engineer
external-ref: W2-121
tags: [wave-2, implementation, dispatch, full]
wbs_id: W2-121
title: 'gov dispatch: one pass a minute keeps the machine full and the work moving without depending on any agent session: the ready list started when there is room for each job''s peak, returns into an inbox, approved landings as one batch, the true status (DEC-1007, DEC-1008)'
class: implementation
state_class: AUTHORITATIVE
role: engineer
waits_on: []
depends_on:
- DAEO-r30l
allowed_paths:
- src/gov/dispatch/**
- tests/unit/dispatch/**
kpis:
  success:
  - '`gov dispatch tick` does one pass and exits; passes never overlap (a lock); an OFF file stops them; the host runs it every minute (cron or a service) and after a restart, outside any agent session; `gov dispatch status` prints the status Verify: a planted project: two `tick` calls started together run one pass (the second exits at the lock, writing nothing); a planted OFF file makes `tick` exit without starting anything; the host''s cron or service entry runs it every minute and after a restart (read from the installed entry, no agent session in its chain); `gov dispatch status` prints the status. [DEC-1007]'
  - 'It starts at most one session per pass, staggered, and only an entry of the orchestrator''s ready list (the WBS order is the orchestrator''s, never the dispatcher''s), and only when the ticket''s claim is committed on the integration branch and in its worktree, the worktree clean, the brief complete, the ticket not running and with no unread return, and the gate (W2-20) and disk open; each skipped entry is named with its reason Verify: planted ready lists with several entries: one session starts per pass, staggered; an entry not on the orchestrator''s list is never started; entries with an uncommitted claim, an unclean worktree, an incomplete brief, a running ticket, an unread return, a shut gate or a full disk are each skipped and named with their reason. [DEC-1007, DEC-995, DEC-944 item 2]'
  - 'Peaks, not the moment: from the history of each kind of job (a lead''s heavy steps, a rebuild, a close''s or the queue''s run, a full check) it keeps each kind''s measured peak (CPU and memory) and starts new work only when the machine has room for the new job''s peak plus the peaks still ahead for the work already running; the figures and their dates are in its status and refreshed from the history at least daily; its memory floor and working size are the gate''s (W2-20 S8 and S9), and memory admission stays W2-20''s S6 Verify: planted job histories for each kind of job: the status prints each kind''s peak (CPU and memory) with its date, refreshed from the history within a day; a start is refused when the room is under the new peak plus the peaks ahead and made when it is over; the memory floor and working size read are the gate''s. [DEC-1008] [re-worded, DEC-1084]'
  - 'Every finished session''s return becomes one inbox item, once; a start that never ran becomes one inbox item; an item unread past a configured time raises an escalation the host''s notifier pushes to the orchestrator''s owner Verify: a planted finished session: one inbox item, and none more on the next pass; a planted start that never ran: one inbox item; a planted item unread past the configured time: one escalation pushed by the notifier stub to the orchestrator''s owner. [DEC-1007, DEC-998]'
  - 'A status file every pass: the sessions running counted from the processes (the launcher''s identity marker), the load, memory, the gate, the slots held, the peaks ahead, the queue, the inbox; a pass that fails says so at the top of the status, never a stale file that looks current Verify: after a planted pass the status file holds the running sessions (counted from processes by the launcher''s identity marker), load, memory, gate, slots held, peaks ahead, queue and inbox; after a planted failing pass the top line says the pass failed and the file is not a stale one that looks current. [DEC-1007]'
  - 'Nothing project-specific in the code; planted tests for every refusal (an uncommitted claim, a shut gate, no room for a peak, a running ticket, an unread return, a malformed list line, a hung command, a crash after a launch); an independent review before it is switched on; this repository''s dispatcher (the CTO''s tool) moves onto it Verify: grep of the dispatcher code for this repository''s branches, paths and ticket ids finds 0 lines; planted tests exist and fail for each named refusal (uncommitted claim, shut gate, no room for a peak, running ticket, unread return, malformed list line, hung command, crash after a launch); the independent review''s record exists before the dispatcher is switched on; this repository''s tool is no longer the one running. [DEC-1007, DEC-982, DEC-1003]'
  - 'The dispatcher never starts a third review round for a ticket (its review rounds counted from its probe records); such a ticket goes to the inbox as an owner item Verify: a planted ticket with two probe records: its next review launch is not started and the ticket becomes one owner item in the inbox; a planted ticket with one probe record is started. [DEC-1010 item 1, SMART-WORK-3]'
  - 'No watcher needs re-arming; every wake is an inbox item a pass writes Verify: a planted run across a restart: every wake the caller gets is an inbox item written by a pass, and no watcher process or re-arm step is present or needed. [DEC-1014 item 2, SMART-WORK-4 line 12] (folds W2-118 S5)'
  - 'Every commit id and path a return names is resolved against git; one that does not resolve is named in the inbox item Verify: planted returns naming a real commit and path and a nonexistent one: the inbox item for the second names the one that does not resolve; the first names none. [DEC-1014 item 2, SMART-WORK-4 line 2] [moved from W2-118 S4, DEC-1083]'
  - 'The ready list the dispatcher reads may come from gov plan --ready (W2-136), reviewed and committed by the orchestrator; the dispatcher starts only what is on it, and its own order is never its choice Verify: a planted list from `gov plan --ready` committed by the orchestrator: the dispatcher starts only entries on it and in no order of its own; an entry not on it is not started. [DEC-1007 (2), DEC-1088 (1)] [added, DEC-1088]'
  failure:
  - 'A session started for an entry not on the ready list, not ready, already running, or without room for its peak; a ticket landed that was not approved, or twice; a return never put in the inbox; a lead count not from the processes Verify: planted passes with an off-list entry, a not-ready one, a running one and one with no room for its peak: no session starts for any; an unapproved ticket and an approved one a second time are not landed; a finished return missing from the inbox, and a lead count taken from anything but processes, are each absent. [DEC-1007, DEC-1008]'
  lifted:
  moved:
profile: FULL
sources:
- DEC-1007
- DAEO-ts4y
- DEC-1008
- DEC-1003
- DEC-979
- DEC-998
- DEC-1009
- DEC-1010
- DEC-1014
- DEC-1015
- DEC-1018
- DEC-1030
- DEC-1031
- DEC-1083
- DEC-1084
- DEC-1088
- DEC-715
- DEC-944
- DEC-952
- DEC-982
- DEC-983
- DEC-989
- DEC-995
- DAEO-ts4y
- DAEO-1ahb
est_loc: 500
acceptance_tests:
  path: tests/acceptance/W2-121/
  author: independent-test-designer (MR-3)
track: A
list_rows:
- W2-H046
---
# W2-121 gov dispatch

The owner's DEC-1007 (the dispatcher, built first as this repository's CTO tool on 2026-11-01) and DEC-1008 (P1-DISPATCH-1 (a); it lands before EXAMIN's copy and is one of K9's entry criteria: the Gov OS is not adopted on EXAMIN without a dispatcher; its starts are judged by each job's peak, every heavy step in a slot). Its model is `.gov-runtime/scratch/orchestrator/dispatch/` (reviewed PASS on the second round). Its landing step uses `gov queue` where W2-117 has landed it, a configured landing command otherwise (W2-117 is planned after EXAMIN's copy; the owner decides whether it moves before).

## Part a, the core (the CTO's delegated decision, DEC-1112 (3), 2026-11-12: run 1's P-W2-121-1 (a) to P-W2-121-4 (a))

This ticket is now part a: `gov dispatch tick` and `gov dispatch status` (the former S1, S2, S3, S5, S7, S8, S11, S12,
S18, S20 and F1's start half). The other lines moved word for word: landing to W2-121b (DAEO-ifgf), health to W2-121c
(DAEO-5rgj, with `src/gov/resources/slots.py`), watch and launch lead to W2-121d (DAEO-6w5n, with `src/gov/watch/**` and
`src/gov/launch/**`). Each part is one FULL loop. Whether parts a and b together meet K9's "a dispatcher" entry criterion
for EXAMIN's copy is the owner's to say (09:30 digest of 11-12).

## Interface (DEC-1052; P-W2-121-2 (a): the reference dispatcher's state folder, its names made generic)

- State folder `.gov-runtime/dispatch/`: `ready.txt` (`<W2> <ticket id> <brief> <log name>` per line; `#` comments; one
  start per log name), `land.txt` (`<W2>=<12-hex head>`), `started.txt`, `land-done.txt`, `never-ran.txt`, `inbox/` and
  `inbox/read/` (one text item per event, first lines `log:`, `W2:`, `status:`), `status.json` and `status.txt` (every
  pass), `peaks.json`, an `OFF` file (no pass runs), `tick.lock`.
- Configuration: a `dispatch:` section of the project's configuration (`max_leads`, the stagger, the CPU band, the nightly
  hold window, the landing command, the notifier command); the memory floor and working size from W2-20's `gate.json`.
- The launcher's identity marker: the lead's `GOV_TICKET` in its `--settings`, as `gov launch` sets it.
- Exit codes: 0 a pass done or nothing to do; 3 the gate or the forecast refused a start (named in the status); 4 a lock
  held; 2 a usage or configuration error.
- S1's installed host entry and S8's switch-over (P-W2-121-4 (a)): checked at the close of the last part through the
  CTO's ACT after the probe record exists, not inside a build run.

## P-W2-121-5 (the CTO's ruling, delegated P2, 2026-11-12 03:20)

The six W2-96 reds in `tests/unit/accept/test_w2_96_{run2,review3,review4}.py` (signals and timeouts in `gov accept`'s
clean-up; red in 13 of 14 recent verifies across eight trees, and in the nightly of 11-12) are shared base reds: each return
names them; they do not block this ticket's verify, review or land (the queue traces an unowned red against the head
without the batch). They are not added to `skip_known.json` (that list is for skips). Their fix is its own ticket.

## P-W2-121-6 and P-W2-121-7 (the CTO, delegated P2, 2026-11-12 05:50)

- **P-W2-121-6 (a):** the `type: bug` of DAEO-1k7y and DAEO-c9n8 corrected to `task` on w2/integrate (da6ba9c53); W2-02's
  core-schema case is green again (4 passed). **The base-red rule from now on:** a red in a lead's verify that is not the
  ticket's and also fails on w2/integrate's head is a shared base red: named in the return with its evidence, not blocking.
- **P-W2-121-7 (a):** the fix run now, before review round 2 (the last, DEC-1010): a test-design batch for F-1 to F-5 as
  behaviours, an engineer for F-1 to F-4 and F-6, rebuild, verify, round 2. F-1: an inbox item, once written, is never written
  again as unread (a returns-seen record; `never-ran.txt` read). F-2: an escalation is recorded only after the notifier exits 0,
  retried at a bounded cadence, its failure shown in every pass while it lasts.
