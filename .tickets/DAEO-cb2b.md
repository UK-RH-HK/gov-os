---
id: DAEO-cb2b
status: open
deps: [DAEO-r30l, DAEO-ts4y]
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
depends_on:
- DAEO-r30l
- DAEO-ts4y
allowed_paths:
- src/gov/dispatch/**
- tests/unit/dispatch/**
kpis:
  success:
  - '`gov dispatch tick` does one pass and exits; passes never overlap (a lock); an OFF file stops them; the host runs it every minute (cron or a service) and after a restart, outside any agent session; `gov dispatch status` prints the status [DEC-1007]'
  - 'It starts at most one session per pass, staggered, and only an entry of the orchestrator''s ready list (the WBS order is the orchestrator''s, never the dispatcher''s), and only when the ticket''s claim is committed on the integration branch and in its worktree, the worktree clean, the brief complete, the ticket not running and with no unread return, and the gate (W2-20) and disk open; each skipped entry is named with its reason [DEC-1007, DEC-995, DEC-944 item 2]'
  - 'Peaks, not the moment: for each kind of job (a lead''s heavy steps, a rebuild, a close''s or the queue''s run, a full check) it reads the measured peak (CPU and memory) from the gate''s figures (W2-20: its configuration file and its re-measure, S8 and S9 there; the memory admission stays W2-20''s S6) and starts new work only when the machine has room for the new job''s peak plus the peaks still ahead for the work already running; the figures and their dates are in its status, read from the gate at least daily [DEC-1008] [re-worded, DEC-1084]'
  - 'Every heavy step takes a heavy-job slot (W2-20: test runs, rebuilds, full checks, retrieval measures), so peaks stay capped whenever they come; a heavy step found running outside a slot is named in the status as a finding [DEC-1008, DEC-979 D1]'
  - 'Every finished session''s return becomes one inbox item, once; a start that never ran becomes one inbox item; an item unread past a configured time raises an escalation the host''s notifier pushes to the orchestrator''s owner [DEC-1007, DEC-998]'
  - 'Every ticket the orchestrator approved to land goes to the project''s landing command (`gov queue`, W2-117, where it exists; a configured command otherwise) as one batch whenever it is free, the tree clean and on the integration branch, and no close running; never one not approved, never twice (the approvals claimed before the launch); each outcome becomes an inbox item [DEC-1007, DEC-989]'
  - 'A status file every pass: the sessions running counted from the processes (the launcher''s identity marker), the load, memory, the gate, the slots held, the peaks ahead, the queue, the inbox; a pass that fails says so at the top of the status, never a stale file that looks current [DEC-1007]'
  - 'Nothing project-specific in the code; planted tests for every refusal (an uncommitted claim, a shut gate, no room for a peak, a running ticket, an unread return, a malformed list line, a hung command, a crash after a launch); an independent review before it is switched on; this repository''s dispatcher (the CTO''s tool) moves onto it [DEC-1007, DEC-982, DEC-1003]'
  - 'A landing never waits for a close it does not conflict with: a running close blocks a landing only when a ticket it closes is among the landing''s, or while it is committing its records; otherwise the landing goes ahead, and two record commits never collide (retried) [DEC-1014 item 5]'
  - 'Nothing holds the machine unseen: each pass checks the shared embedding server''s health (a fixed test request answered within a configured time) and every heavy-job slot holder''s progress (its process tree''s CPU time growing within a configured time); a hung server or an idle holder becomes one inbox item and one alert through the host''s notifier, once per incident, cleared on recovery; the server is restarted only through the project''s configured safe restart (W2-123), rate-limited and recorded; a holder is never killed automatically [DEC-1015 item 2]'
  - 'The dispatcher never starts a third review round for a ticket (its review rounds counted from its probe records); such a ticket goes to the inbox as an owner item [DEC-1010 item 1, SMART-WORK-3]'
  - 'The dispatcher alerts when the orchestrator''s session or its sentinel has no heartbeat for a configured time [DEC-1014 item 2, SMART-WORK-4 line 11] (to Wave 3, W3-P16, W-10) [re-scoped, DEC-1083]'
  - 'No watcher needs re-arming; every wake is an inbox item a pass writes [DEC-1014 item 2, SMART-WORK-4 line 12] (folds W2-118 S5)'
  - 'While ready work waits, busy cores stay within a configured band for at least 80 % of the hours; time below or above the band is reported daily with its cause [DEC-1014 item 2, SMART-WORK-4 line 13]'
  - 'The project''s nightly is never kept from starting by a landing: from a configured time before its start until it has started (its running marker), or a configured latest time, the dispatcher claims no landing; one already running is finalised; the status names the hold [DEC-1018 item 1]'
  - 'Each pass reads the GPU state and, for each embedding server, its model''s layers on the GPU (from the server''s own log or API); a crash in a server''s log, or a model loaded with 0 layers on a GPU it is expected to use, writes one inbox item at once and one line for the sentinel, once per incident; the status shows the GPU, its holders and each model''s layers [DEC-1030 items 1 and 4, DEC-1031 item 4]'
  - '`gov watch` wakes its caller when a lead''s worktree gains a commit whose subject marks a key result (a probe record, a measure, a package, a baseline) and when a lead returns, each once, named [DEC-952 item 3, DEC-983, DEC-982]; where a dispatcher runs, gov watch only reads its inbox and never marks a return seen [DEC-1009, SMART-WORK-3] [moved from W2-118 S1, DEC-1083]'
  - 'A commit brought into a lead''s branch by a merge from the integration branch never wakes the caller [DEC-1003, SMART-WORK-3] [moved from W2-118 S3, DEC-1083]'
  - 'Every commit id and path a return names is resolved against git; one that does not resolve is named in the inbox item [DEC-1014 item 2, SMART-WORK-4 line 2] [moved from W2-118 S4, DEC-1083]'
  - 'gov launch lead <ticket> builds the whole lead invocation (absolute paths, the identity in --settings, the model, background mode, the log and PID files) and passes the resource gate [DEC-715, W2-H046]. [moved from W2-21 S1, DEC-1083]'
  failure:
  - 'A session started for an entry not on the ready list, not ready, already running, or without room for its peak; a ticket landed that was not approved, or twice; a return never put in the inbox; a lead count not from the processes [DEC-1007, DEC-1008]'
  - 'A key result or a return reported twice, or not at all. [moved from W2-118 F1, DEC-1083]'
  lifted:
  - 'The morning report lists every crash or error in the servers'' logs overnight (CUDA errors, runner exits, model loads and their layers, failed and timed-out requests with their counts), beside the nightly''s tests [DEC-1030 item 3, DEC-1031 item 4] [lifted (was S17), DEC-1083: re-scoped by D9-FATES (INVESTIGATION-1 §5)]'
profile: FULL
sources:
- DEC-1007
- DEC-1008
- DEC-1003
- DEC-979
- DEC-998
est_loc: 500
acceptance_tests:
  path: tests/acceptance/W2-121/
  author: independent-test-designer (MR-3)
track: A
list_rows: []
---
# W2-121 gov dispatch

The owner's DEC-1007 (the dispatcher, built first as this repository's CTO tool on 2026-11-01) and DEC-1008 (P1-DISPATCH-1 (a); it lands before EXAMIN's copy and is one of K9's entry criteria: the Gov OS is not adopted on EXAMIN without a dispatcher; its starts are judged by each job's peak, every heavy step in a slot). Its model is `.gov-runtime/scratch/orchestrator/dispatch/` (reviewed PASS on the second round). Its landing step uses `gov queue` where W2-117 has landed it, a configured landing command otherwise (W2-117 is planned after EXAMIN's copy; the owner decides whether it moves before).
