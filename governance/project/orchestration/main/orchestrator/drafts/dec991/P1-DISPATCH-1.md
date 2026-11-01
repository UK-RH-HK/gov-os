# P1-DISPATCH-1 — the dispatcher as a Gov OS feature (DEC-1007 item 5, DEC-1003)

## 1. Context
DEC-1007: a plain program keeps the machine full and the work moving without depending on any session's memory. This
repository's version is the CTO's tool (`.gov-runtime/scratch/orchestrator/dispatch/`, built tonight, 18 tests,
independent review running). DEC-1003: every practice of the CTO's tools goes into the product the same day as a
KPI proposal.

## 2. What it touches in the product
- W2-20 (the resource gate: load, memory, disk, the heavy-job slots): the dispatcher reads it, adds nothing to it.
- W2-117 (`gov queue`, after EXAMIN's copy): the dispatcher puts an approved batch into it.
- W2-118 (`gov watch`: wakes its caller on a lead's key result and return): the dispatcher's inbox replaces "wake the
  caller" with a file that needs no watcher to be re-armed.
- Nothing in the product starts leads on its own today; `gov launch` starts one session when asked.

## 3. Why it matters
An adopted product's orchestrator has the same failure modes: a session that forgets to watch, compacts, or freezes
leaves the machine idle and returns unread. The product must keep its own work moving.

## 4. Options
- **(a) A new ticket, W2-121 `gov dispatch` (engineer, FULL: it acts on its own), recommended,** after W2-20 and
  W2-118, its landing step after W2-117 (so after EXAMIN's copy, as W2-117 is); about 400 lines. KPI lines:
  - `'gov dispatch tick does one pass and exits; passes never overlap (a lock); an OFF file stops them; the host runs it every minute (cron or a service) and after a restart, outside any agent session [DEC-1007]'`
  - `'It starts at most one session per pass, staggered, and only an entry of the orchestrator''s ready list (the WBS order is the orchestrator''s, never the dispatcher''s), and only when the ticket''s claim is committed on the integration branch and in its worktree, the worktree clean, the brief complete, the ticket not running and with no unread return, and the gate (W2-20) and disk open; each skipped entry is named with its reason [DEC-1007, DEC-995, DEC-944 item 2]'`
  - `'Every finished session''s return becomes one inbox item, once; an item unread past a configured time raises an escalation the host''s notifier pushes (the orchestrator''s phone) [DEC-1007, DEC-998]'`
  - `'Every ticket the orchestrator approved to land goes into gov queue (W2-117) as one batch whenever the queue is free, the tree clean and no close running; never one not approved; each outcome becomes an inbox item [DEC-1007, DEC-989]'`
  - `'A status file every pass: the sessions running counted from the processes, the load, memory, the gate, the slots held, the queue, the inbox; the orchestrator''s status reads it [DEC-1007]'`
  - `'Nothing project-specific in the code; planted tests for every refusal; an independent review before it is switched on [DEC-1007, DEC-982]'`
  - and W2-118's S1 amended: `"...wakes its caller ... ; or, where a dispatcher runs, writes the inbox item it reads (no watcher to re-arm) [DEC-1007]"`.
- **(b) KPI changes spread over W2-20, W2-117 and W2-118:** no new ticket, but the starting of sessions belongs to none
  of them (the gate reads, the queue lands, the watch wakes), so the core would be split across three owners.
- **(c) Keep it as this repository's tool only:** fails DEC-1003.

## 5. Recommendation
(a), confidence medium-high: one owner for the loop, the three tickets' boundaries kept. The ticket count grows by one
(126 to 127). Its order: with W2-117, after EXAMIN's copy (it may land later, as the owner allowed); this repository
runs the CTO's tool meanwhile.

## 6. What it blocks
Nothing tonight; the CTO's tool runs meanwhile.
