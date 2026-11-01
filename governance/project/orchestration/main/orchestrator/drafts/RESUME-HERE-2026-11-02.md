## RESUME HERE — handover of 2026-11-01 22:45 GMT, for the fresh session after the reload (DEC-994, DEC-1018)

**Read first:** `governance/project/prompts/w2-orchestrator.md` §0; `governance/project/orchestration/DECISIONS-IN-FORCE.md`;
this block. Older history: `drafts/CHECKPOINT-ARCHIVE-to-2026-11-01.md` (read only for a named question). Register: DEC-1009
to DEC-1018 are today's; next free id DEC-1019.

**At start, in order:**
1. `echo "$GOV_ROLE $GOV_TICKET"` = `orchestrator DAEO-sdxk`; `git status --porcelain` in the main tree empty.
2. Write your session id to `log/cto-session.txt` (the sentinel watches it), then end the stand-by with
   `mv log/cto-standby.txt log/cto-standby.ended-$(date +%H%M).txt` (no `rm`: it needs the owner's approval, DEC-991).
   Check the sentinel: `tmux ls` shows `cto-sentinel`.
3. Confirm your Remote Control link is live and send one test push (DEC-998 item 2).
4. **If before 02:00:** the live "push when actions required" test (ACT-PUSH-INPUT-1): ping the owner first, then run one
   command that needs approval (e.g. `ls .claude/`); the owner should get a push. From 02:00 the quiet-hours hook refuses
   prompts: the test moves to 07:30.
5. **At 03:00:** the throwaway hook test (ACT-QUIET-DENY-1): a throwaway session started with `GOV_QUIET_NOW=03:00` and
   `GOV_QUIET_QUEUE=<a scratch file>` (the hook's test clock and queue) tries one command that needs approval; it must be
   denied with the hook's message, never shown, and appear in that queue file. Report both results in the morning package.

**The night's rules:**
- Quiet hours 02:00-07:30: never run a command that could need approval (rm in any form, owner-ping, any `.claude/` path);
  queue it to `log/approval-queue.jsonl` for the 09:00 package (DEC-991).
- **The nightly runs at 04:00** (DEC-973). From 03:15 until it has started (`NIGHTLY-RUNNING` written, or today's line in
  `log/nightly/status.txt`): no commit, no file written in the main tree; the dispatcher holds landings (v4.3,
  `66b08891`; check the 03:15 pass's status shows `held for the nightly`, cleared after it starts). Last two nights it
  never started (a dirty tree). A `land.py` or `close_build.py` run by hand must not be started after 03:00.
- Leads start only through `dispatch/ready.txt` (or `tools/start_owner_order.sh` on an owner's explicit order); landings
  through `dispatch/land.txt` or `tools/land.py`. Never `&`; check a tree with `tools/tree_busy.sh <W2>` (never
  `pgrep -f` on a path: matched my own shell twice).
- A rule broken twice becomes a mechanism (DEC-1012); slips go to `log/drift-2026-w44.txt`.
- Status counts come from files: `dispatch/status.txt`, `git log`, `tk`.
- `tools/applied_check.py` at every handover and in the morning package: every decision draft in the register, every
  package KPI line in a ticket (ignores with reasons in `tools/applied_check.ignore`).

**The machinery (all live):**
- Dispatcher v4.2 (`d216e61f`, cron every minute): ready list by peaks, inbox, landings, sentinel heartbeat, interim
  results, guard refusals (harvest detached), nightly lines, embedding-server health (starts held while it is down) and
  slot-holder progress; v4.3 (`66b08891`) holds landings 03:15 until the nightly starts. Status `dispatch/status.txt`.
  Open v4 follow-ups (non-blocking): reviews `reviews/dispatch-v4.2-round2.md` F2/F3 (server flapping hysteresis;
  reaped children's CPU) and `reviews/dispatch-v4.3.md` F2/F3.
- `tools/rebuild_slot.sh` exits 75 when a rebuild answers ok without its semantic store (DEC-1015 item 4): a lead,
  close or queue run sees it as failed.
- Sentinel (ACT-SENTINEL-1, two-day trial from tonight): tmux `cto-sentinel`, Haiku, Remote Control "CTO sentinel";
  `dispatch/sentinel-expected` present. Report its cost after day one (morning of 11-03).
- Embedding servers: 11434 (shared) and 11435 (query, CPU-only), both capped 12-19, nice 10 (ACT-OLLAMA-CAP-1/2). The
  caps are lost on a restart until W2-20 and W2-123 land (DEC-1017).

**State at the handover (w2/integrate `9a74ef2a91b3`, main tree clean):**
- Closed 45. Leads running 4 (from the processes): W2-104, W2-92, W2-122, W2-123 (the last two started 22:24 and 22:26 on
  the owner's order, DEC-1018 item 2). Load about 22; embedding server healthy.
- **Detached from the old session (parent: init), each writing its own log; check them first:**
  - The landing batch W2-11, W2-105, W2-81: `land.py` pid 514085, `log/land-batch3-20261101-2205.out` (rebuilding its
    warm clone, then tests, merge, close records, commit). Its last line "exit N" will be missing (its wrapper was
    ended to detach it): judge it by the queue's records and `git log`.
  - The close W2-05, W2-55, W2-96: `close_build.py` pid 514602, `log/close-three-20261101-2205.out` (same note).
  - W2-04's store rebuild: pid 515103, `log/rebuild-W2-04-20261101-2205.out`. W2-04's verify run is on the ready list;
    its brief waits on this tree's rebuild lock, then refreshes the rest.
  - If any of them dies, re-run it with `setsid -f` and a log redirect, never in a session-bound background shell.
- `dispatch/land.txt`: `W2-90b=73c18fea1e1f` (DEC-1016). The dispatcher lands it once the queue is free, outside the
  nightly hold.
- **Starts held at the handover:** W2-92's lead runs one acceptance suite with 4 workers outside a slot (pid 761575,
  `timeout 3000`), against the common brief. Raise it with W2-92's return.
- The guard-fix subagent stopped with the old session: relaunch it from `drafts/GUARD-FIX-3-brief.md` (by day).

**Open for the owner (the 09:00 package):**
- ACT-GUARD-FIX-3 (DEC-1018 item 3): the acceptance-folder rule's fix, 57 of 61 refusals false; its design subagent to be relaunched from `drafts/GUARD-FIX-3-brief.md`.
- P-W2-90b-1 (DEC-1016): how W1-46's live sessions and W1-50's launcher judge the worktree's code; lead's rec (b).
- W2-11's seven unplaced lines (SW3 reviewer template; SW4 4, 6, 9, 10; SW5 B, C): a ticket covering the orchestration
  skill once W2-11 closes (P1, DEC-1015 item 3).
- SW4 line 3 (reviewer recall per model): no home (W2-81 lands without a round; W2-93 has no scorer). SW4 line 1
  (W2-82 ROLE_SCOPE): at W2-82's claim with its split.
- The sentinel's cost after day one; the two tests' results; the approval queue.

**Next, in order:** land and close what returns (one merge per ticket); W2-04's verification once its store is
complete (store `semantic_vector` near 50,000; `log/rebuild-W2-04-20261101-2205.out`); then the ready list as written
(W2-92 run 2, W2-61h verify, W2-91); the memory chain W2-92 -> W2-13 -> W2-15a -> W2-32; W2-115 after W2-55 closes;
W2-20's next run starts by merging w2/integrate (1,510 behind; acceptance conflicts: its test designer).
