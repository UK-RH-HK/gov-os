# CHECKPOINT — W2 orchestrator, the CTO (`orchestrator DAEO-sdxk`)

## RESUME HERE — handover of 2026-11-01 22:45 GMT, for the fresh session after the reload (DEC-994, DEC-1018)

**Read first:** `governance/project/prompts/w2-orchestrator.md` §0; `governance/project/orchestration/DECISIONS-IN-FORCE.md`;
this block. Older history: `drafts/CHECKPOINT-ARCHIVE-to-2026-11-01.md` (read only for a named question). Register: DEC-1009
to DEC-1018 are today's; next free id DEC-1019.

**Resumed 2026-11-01 23:49 by session `07f25884` (registered; stand-by ended; `dispatch/sentinel-expected` on).**
Done: inbox read (5 filed; guard 61-63 false positives, ACT-GUARD-FIX-3's pattern, 60 of 64 false); pre-reload jobs
all alive (land.py 514085, close_build.py 514602, leads W2-104/W2-122/W2-123; W2-92's lead returned PACKAGES);
P-W2-92-5 decided (a), DEC-1019 `f9d0685f`, run 3 brief `briefs/W2-92-A5-run3-dec1019.md` on the ready list; the
quiet-hours hook test at 03:00 PASSED and the push-on-prompt test ran 23:50:50 (prompt approved in ~10 s; owner to
confirm the phone push): `log/safety-net-tests-20261101.txt`. Test push: first "not sent" (owner at the PC), the two
APPROVE pings "Mobile push requested". ACT-GUARD-FIX-3 copied to `drafts/act-guard-fix-3/`; its independent review
(Sonnet subagent) writes `reviews/act-guard-fix-3.md`; then `packages/` and the ping (before midnight, else 09:00).
**00:08:** review round 1 FAILED (F2 regression fails open; F3, F4 as today; F1 flaky test). Moderator's triage at the
record's end: F1-F3 fixed, F4 only if false refusals stay under 10 %, F5-F7 rows. Round 2 (Opus subagent) works in
`drafts/act-guard-fix-3/` (round 1 kept in `drafts/act-guard-fix-3-round1/`); then the second and last review
(Sonnet, same probes); then the package to `packages/`, pinged if before 02:00 (DEC-1021), else the 09:00 package.
**00:25 (owner):** both 23:50 pushes arrived; DEC-1021 `a332b2aa`: pings until 02:00, quiet 02:00-07:30. Push-on-prompt
re-run 00:12:48 (pinged first, approved in ~25 s; owner to confirm Claude Code's own push). Owner asked for the three
open items in short form (P-W2-90b-1, W2-11's seven lines, SW4 line 3) to decide now.
**00:35 (owner) DEC-1022** `94df6e93`: P-W2-90b-1 (b), W2-90c's S4 line re-worded `3a4203e5`; W2-11b `DAEO-9bc0` filed
`c361b095` (product-spec, STANDARD; starts once W2-11 closes; withdrawn if W2-11 takes the lines in another round);
SW4 line 3 -> W3-P21. applied_check 0 gaps. **TODO by day (after 07:30, 2026-11-02):** the push-on-prompt test again:
ping first, the owner steps away, the prompt waits a few minutes (DEC-1022 item 1).
**00:45:** guard-fix round 2 done (F1-F4 fixed; corpus 2/61; 0 of 167 planted writes missed; 270 tests stable; one
residual regression -> Wave 3 row). Review round 2 (Sonnet, the last) writes `reviews/act-guard-fix-3-round2.md`.
PASS -> copy to `packages/ACT-GUARD-FIX-3.md` (+ diff, files), commit, ping (before 02:00) or 09:00 package. FAIL ->
the owner once, with options (DEC-1010). Refusals 63 of 67 false (a classify can race the harvester: re-check
unclassified after classifying).
**00:58:** review round 2 PASS, READY true (`tools/verdict.py`); package in `packages/` (`49158e13`: .md with the review
summary, .diff, test file); ACT pinged (sent). Waiting on the owner's operator to apply it. Round 2's low findings and
F5-F7 are Wave 3 rows to add to WAVE_3_PARKING.md with the morning records.
**01:02 (owner) DEC-1023:** ACT-GUARD-FIX-3 (a) approved; the owner's operator applies it THIS MORNING with the owner
present (not overnight). Morning list: remind the owner at 09:00; after it is applied, confirm guard4 PASS and the
test file's result, and watch the next refusals harvested.
**00:15:** W2-104 returned DONE at `ac2d92af8c0e` with P-W2-104-CMDLIST: decided (a) + CLAUDEPATH (c), DEC-1020
`235c4d5d`, ticket paths `d942524f`; run 2 brief `briefs/W2-104-A5-run2-dec1020.md` on the ready list after W2-92.
Guard 64 (the reviewer's heredoc probe) false; 61 of 65 false. Leftover scratch for removal (rm: by day only, pinged):
`/tmp/gov-os-lead-W2-92`, `/tmp/gov-os-lead-W2-104` once its run 2 ends. Morning package: W2-104 run 1's inherited
reds (W2-54 AR-5 input, W1-46/W2-59 hook-file reds, W2-66 win_toast.ps1) to trace.

**01:26 slip (drift log):** the inbox sat 30+ min unread (guard 67-69, W2-123 interim) because this session never armed
`tools/inbox_wait.sh` after the reload; the sentinel's stale-inbox push caught it. **Every session start and after every
wake: arm `bash tools/inbox_wait_quiet.sh` (09:28: repeat server-hung items wake at most hourly; else as inbox_wait.sh) with the Bash tool's background run (it exits on an item; re-arm after handling).**
Mechanism proposed to the owner (DEC-1012): a Stop hook that names an unarmed waiter (a `.claude/` change: the owner's).

**02:52:** the close W2-05+W2-55+W2-96 REFUSED at 01:48 (W2-55's backfill 31 rows behind the register: W2-55's;
W2-66's record-only red on `win_toast.ps1` from `42104b11`: the CTO's, misattributed because the baseline predates it).
The landing batch found an owned W1-08 probe-schema red at 02:01 (W2-11's or W2-81's probe record) and is still
re-running cases alone; no hold of its own; left running. All in `drafts/P1-MORNING-2026-11-02.md` (scratch until the
nightly starts; then copy to `packages/`). **After the nightly's verdict:** re-close W2-05 + W2-96 against it (rec (a));
W2-55 back for its table + P-W2-55-HOOK. Inbox waiter re-armed 02:52.
**03:17:** W2-123 DONE (verified `17d88232b287`, head `9bb92097c811`): added to `dispatch/land.txt` (held for the
nightly); its three P1s (Ollama `-np 1`; embedder not bit-reproducible; the query server starved: an ACT for its own
CPUs, first) in the morning draft §5. Leads now 1 (W2-122). Waiter re-armed 03:17.
**04:45:** nightly started 04:00 on `9d605eba20a2`. First landing batch STOPPED 04:32 (baseline prepare failed),
nothing landed. Culprit of its owned reds: **W2-81** (both probe records fail `probe.schema.json`; reproduced, edit
undone): back to its lead. Dispatcher batch of five started 04:33 (`land-dispatch-20261102-043305.out`). Embedding
servers hung/overloaded since 04:31 (11434 reloading its model; 11435's runner 490 % CPU for ~5 h); a background
probe (task bydgl3oz2) watches; no restart (caps would be lost; the owner's). Waiter re-armed 04:45. Draft §6.
**05:20:** batch of five STOPPED 04:37 (prepare failed: the server). Shared server flapping (HUNG 05:14). W2-81
ejected by hand (`merge-queue/ejected/W2-81.json`); its records-only repair `briefs/W2-81-A5-r4-records.md` on the ready
list. The four others stay approved; the dispatcher retries.
**06:07:** W2-122 PACKAGES (26/26 at `bd50a9581893`); P-W2-122-K5 (K5 reds 100 earlier cases; adoption would need an
embedder) is the owner's P1: morning draft §7, rec (b) then (a). W2-122 waits. W2-81's records repair running.
**06:20:** W2-81 repair DONE `e78e6af7530d` (records only, checked). All five relisted in `dispatch/land.txt` (the
dispatcher does not retry kept entries by itself: a gap, morning draft).
**07:56:** landing of five STOPPED 07:54 (semantic not recreated: the embedder); relisted. Nightly: parallel 21 F + 2 E,
serial 3 F + 8 E; re-running alone. W2-04 verify run 4 running (scoped). Morning package at 09:00 from the draft,
with the push-on-prompt re-test (DEC-1022 item 1).
**08:01:** retry STOPPED 07:59 (semantic not recreated in 121 s, server healthy): W2-123 (its new embedding client) is
the suspect; its approval moved to `merge-queue/held/` (not ejected); W2-11, W2-105, W2-90b, W2-81 relisted.
**08:06:** the four failed the same way: W2-123 NOT the cause, restored to approved/. Cause: the one-at-a-time shared
embedder busy with W2-04's retrieve_check and the nightly's W1-19 re-run. `land.txt` left empty: relist all five once
those end.
**09:00:** morning package `packages/P1-MORNING-2026-11-02.md` (`0d0e8e41`) pinged (sent). Waiting on the owner's A-F. The
nightly still re-running its reds alone; investigate when it ends. Leads W2-04, W2-92, W2-104. Handover to a fresh
session after the package (DEC-952 item 6).
**09:15:** W2-04 verify DONE `b37b5c8f1741` (FULL: review not yet run); its review run `briefs/W2-04-A5-review.md`
first on the ready list. P-W2-04-5 decided: DEC-1024 `446897f7`, W2-120's sources DEC-718 `a4c92d4e` (W2-10 and W2-11 keep
AR-5/6 under closes:). Nightly marked FAILED at 09:00 (no verdict yet, still re-running): package item G `24375c96`.
**09:20:** sixth landing attempt failed (09:16). Mechanism: `semantic.py` TIMEOUT_S 120, no retry. Package A updated with
option (d), a bounded retry (`be9e2812`), pinged. `land.txt` left empty: relist only when the embedder is free.
**09:36:** W2-91 DONE `55b47e075b3b` (STANDARD, gov accept 8/8; VERIFY-1: the queue verifies). Six to land kept in
`dispatch/land.pending.txt` (copy to `land.txt` when the embedder is free or (d) lands). Leftovers to remove by day
(rm: ping first): W2-91-tests worktree + branch, gov-os-runs/W2-91/{base,head}, /tmp/gov-os-lead-W2-{91,92,104,122,123,04}.
**09:38:** W2-92 run 3 DONE `448a835a9dca` (STANDARD; DEC-1019 built; 30/30; gov check's retrieval-regression red is
environmental: 0 % at the pre-ticket base too, the shared embedder). Seven pending to land. W2-13 waits on W2-92's landing.
**09:46:** W2-04 review 1 FAILED (F1 fails open: an emptied mandatory file shown as read). DEC-1025 `3861c3fb`: one repair
round (F1; F2, F3 ride along), review 2 the last (a different model); brief `briefs/W2-04-A5-r5-repair.md` first on
the ready list. P-W2-04-7 -> package item H `60a9b4a1`, pinged.
**10:19:** W2-104 run 2 DONE `909d7ff0a926` (STANDARD; the one skilleval line checked). Eight pending to land.
**10:25:** DEC-1026 `5f3d143b` (delegated, package A (d)): W2-123 run 2 builds the bounded embed retry in semantic.py
(ticket `4c3f3ecd`); brief `briefs/W2-123-A5-r2-retry.md` first on the ready list; W2-123's old approval moved to
`merge-queue/held/W2-123-at-9bb92097c811.json`. Seven pending in `dispatch/land.pending.txt`; land them WITH W2-123's new head.
**10:50 (owner) DEC-1027 `feb80819`, B-H; A to follow.** Applied: F ACT-GUARD-FIX-3 applied by the operator `e662684a`
(guard4 PASS); the push test by day 10:37:42, approved in 8 s (owner to confirm the phone push). H: common brief 6a
`4fdee1e6`, W2-61h's lead messaged; W2-125 `DAEO-jfm3` filed. C: W2-124 `DAEO-mb2t` filed (K5), W2-122's KPI 5 moved
`42dad22d`, W2-122 run 2 brief `W2-122-A5-r2-nok5.md` queued. B: W2-66b `DAEO-zuiy` filed+claimed, worktree, brief
queued; **W2-05 + W2-96 re-close against tonight's nightly once it has a verdict** (watch bnsm55ns4); **W2-55's run
held: asked the owner how its table stays current** (my package mis-described P-W2-55-HOOK). E: ACT-STOP-WAITER-1
`36970e6f` (script + 6 tests) for the operator. P1-GUARD-PARSER-W2 `f614ec78` pinged. Guard 71 = first false positive
under the new hook (F4 rule).

**At start, in order (the earlier session's list; items 1-5 done above):**
1. `echo "$GOV_ROLE $GOV_TICKET"` = `orchestrator DAEO-sdxk`; `git status --porcelain` in the main tree empty.
2. Write your session id to `log/cto-session.txt` (the sentinel watches it), then end the stand-by with
   `mv log/cto-standby.txt log/cto-standby.ended-$(date +%H%M).txt` (no `rm`: it needs the owner's approval, DEC-991).
   **The sentinel:** started 22:44 in tmux `cto-sentinel`, but it waits at Claude Code's folder-trust prompt (the owner's
   choice; never press it for them). Once the owner has accepted it (`tmux attach -t cto-sentinel`) and its watch writes
   `log/deadman.log`, `mv dispatch/sentinel-expected.pending dispatch/sentinel-expected` (parked so the dispatcher does
   not flag it silent meanwhile: the log's last line is a 13:01 test).
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
  - W2-04's store rebuild: DONE 22:43 (semantic recreated, 54,514 vectors). W2-04's verify run is on the ready list
    and starts when the dispatcher admits it.
  - If any of them dies, re-run it with `setsid -f` and a log redirect, never in a session-bound background shell.
- `dispatch/land.txt`: `W2-90b=73c18fea1e1f` (DEC-1016). The dispatcher lands it once the queue is free, outside the
  nightly hold.
- **Starts held at the handover:** W2-92's lead runs one acceptance suite with 4 workers outside a slot (pid 761575,
  `timeout 3000`), against the common brief. Raise it with W2-92's return.
- ACT-GUARD-FIX-3 is designed and staged (finished 23:3x, before the reload): `/tmp/claude-1000/-home-usain-Dynamic-Agentic-Engineering-OS/20804c5c-af51-4450-934e-42f650effce2/scratchpad/guard-fix/`
  (`ACT-GUARD-FIX-3.md`, `.diff`, `bash_writes.py`, 198 tests). Logged refusals 31 of 61 refused by today's hook ->
  2 of 61 (3.3 %) with the fix; planted writes 40 of 87 missed today -> 0; the final history differential (4,873
  commands) done: 67 newly passed (none writes into the tests), 9 newly refused (6 real test writes today's hook
  misses, 3 fail-closed). To do: an independent review of
  `bash_writes.py` (about 1,200 lines, a different model); copy the package into `packages/`; send it to the owner
  (rec (a)). Product half: W2-42's six proposed lines (package §7). Do NOT relaunch the brief in `drafts/`.

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

## Archive
Everything older: `drafts/CHECKPOINT-ARCHIVE-to-2026-11-01.md` (to 2026-11-01 night) and `CHECKPOINT-ARCHIVE.md` (to 2026-10-18).

<!-- GENERATED STATE BLOCK BEGIN -->
generated: 2026-11-01T21:48:55Z e07513828259a7b2e3a543ae9dc3c0dd9ea8ba9422457f39bc27c80f0df4ac19
git head: e639b83908c87b83f8ddcb922a6d6f0f3d23dc5a
tickets in progress (`tk ls --status=in_progress`):
  DAEO-0z8c [in_progress] - W2-05 The git environment of every check, hook and helper; the settings re-sort <- [DAEO-g0ip]
  DAEO-3r1j [in_progress] - W2-110 A product's CTO-only install rule
  DAEO-6b2q [in_progress] - W2-109 Contract v4.3
  DAEO-6n5k [in_progress] - W2-37 gov impact <- [DAEO-g0ip, DAEO-ym8a]
  DAEO-a3u2 [in_progress] - W2-91 Full embeddings: the root files, the governance overlay and schemas/ <- [DAEO-jsg1]
  DAEO-arrl [in_progress] - W2-55 Decisions tagged by domain, status and scope; superseded and done entries left out of what agents see
  DAEO-blwa [in_progress] - W2-122 Seeded rebuilds
  DAEO-cv58 [in_progress] - W2-60a The role, its skills and its model and effort loaded at launch; the launch record
  DAEO-drhj [in_progress] - W2-104 The skill evaluation harness
  DAEO-h2k3 [in_progress] - W2-61h W2-61's held-out half: 20 hidden memory questions with their gold sources <- [DAEO-m1u3]
  DAEO-k7hz [in_progress] - W2-11 Briefs and the orchestration skill: twelve fields, payload after, two-refusal stop, DEC-430 <- [DAEO-g0ip]
  DAEO-l78m [in_progress] - W2-81 The adoption proving ground: five synthetic repositories with planted problems, a judge, and question sets per repository
  DAEO-n0wb [in_progress] - W2-92 The knowledge graph and the code graph as routes of plain-question retrieval <- [DAEO-s9qc, DAEO-ym8a]
  DAEO-nqa2 [in_progress] - W2-90b W2-90's next round <- [DAEO-0mtg]
  DAEO-ouet [in_progress] - W2-96 The opaque acceptance runner
  DAEO-qzrq [in_progress] - W2-123 Parallel requests on the embedding server
  DAEO-r30l [in_progress] - W2-20 Machine-wide resource gate <- [DAEO-g0ip]
  DAEO-siiz [in_progress] - W2-52 The lite A7 and A10 stage records <- [DAEO-g0ip, DAEO-ha8z]
  DAEO-u4oz [in_progress] - W2-04 gov context bounded and reproducible <- [DAEO-g0ip, DAEO-ym8a]
  DAEO-wnnz [in_progress] - W2-56 `gov launch` usable for every worker
  DAEO-zpdj [in_progress] - W2-105 The template's install block removed
  DAEO-zqvn [in_progress] - W2-13 RETR-X-02 and a ranked lexical route (BM25, SQLite FTS5) <- [DAEO-g0ip, DAEO-ym8a]
worktrees (`git worktree list`):
  /home/usain/Dynamic-Agentic-Engineering-OS  e639b839 [w2/integrate]
  /home/usain/gov-os-worktrees/W2-00-record   54f122fe [record/w2]
  /home/usain/gov-os-worktrees/W2-00-store-a  d88a1fff (detached HEAD)
  /home/usain/gov-os-worktrees/W2-00-store-b  6ebd7b56 (detached HEAD)
  /home/usain/gov-os-worktrees/W2-03          92e03a72 [w2/W2-03]
  /home/usain/gov-os-worktrees/W2-04          e0d06a04 [w2/W2-04]
  /home/usain/gov-os-worktrees/W2-05          8d2a1f54 [w2/W2-05]
  /home/usain/gov-os-worktrees/W2-07          31ddf173 [w2/W2-07]
  /home/usain/gov-os-worktrees/W2-104         738cec98 [w2/W2-104]
  /home/usain/gov-os-worktrees/W2-105         fa653609 [w2/W2-105]
  /home/usain/gov-os-worktrees/W2-106         9525808d [w2/W2-106]
  /home/usain/gov-os-worktrees/W2-107         3861d3f3 [w2/W2-107]
  /home/usain/gov-os-worktrees/W2-108         d3f87c55 [w2/W2-108]
  /home/usain/gov-os-worktrees/W2-109         695eea48 [w2/W2-109]
  /home/usain/gov-os-worktrees/W2-11          c9f99b28 [w2/W2-11]
  /home/usain/gov-os-worktrees/W2-110         d0ecd1bc [w2/W2-110]
  /home/usain/gov-os-worktrees/W2-114         e9214850 [w2/W2-114]
  /home/usain/gov-os-worktrees/W2-122         c2e4d0f2 [w2/W2-122]
  /home/usain/gov-os-worktrees/W2-123         1045f565 [w2/W2-123]
  /home/usain/gov-os-worktrees/W2-13          bdc4b795 [w2/W2-13]
  /home/usain/gov-os-worktrees/W2-16          05952376 [w2/W2-16]
  /home/usain/gov-os-worktrees/W2-20          1a54976c [w2/W2-20]
  /home/usain/gov-os-worktrees/W2-26          5cee4e6b [w2/W2-26]
  /home/usain/gov-os-worktrees/W2-37          38e74a5d [w2/W2-37]
  /home/usain/gov-os-worktrees/W2-49          9fc4dcd9 [w2/W2-49]
  /home/usain/gov-os-worktrees/W2-51          61b6600b [w2/W2-51]
  /home/usain/gov-os-worktrees/W2-52          2b922bf7 [w2/W2-52]
  /home/usain/gov-os-worktrees/W2-55          aca86233 [w2/W2-55]
  /home/usain/gov-os-worktrees/W2-55-tests    1f7a4dd9 [w2/W2-55-tests]
  /home/usain/gov-os-worktrees/W2-56          23079f92 [w2/W2-56]
  /home/usain/gov-os-worktrees/W2-57          70ee48e2 [w2/W2-57]
  /home/usain/gov-os-worktrees/W2-58          09f5ebfa [w2/W2-58]
  /home/usain/gov-os-worktrees/W2-60a         e1a3e221 [w2/W2-60a]
  /home/usain/gov-os-worktrees/W2-61          6b517db9 [w2/W2-61]
  /home/usain/gov-os-worktrees/W2-61h         ac7dfa17 [w2/W2-61h]
  /home/usain/gov-os-worktrees/W2-63          ad38ed68 [w2/W2-63]
  /home/usain/gov-os-worktrees/W2-64          bb389b71 [w2/W2-64]
  /home/usain/gov-os-worktrees/W2-65          f6881547 [w2/W2-65]
  /home/usain/gov-os-worktrees/W2-67          ff2cc697 [w2/W2-67]
  /home/usain/gov-os-worktrees/W2-68          05ec0f6a [w2/W2-68]
  /home/usain/gov-os-worktrees/W2-71          027d4f10 [w2/W2-71]
  /home/usain/gov-os-worktrees/W2-75          e7f90cd3 [w2/W2-75]
  /home/usain/gov-os-worktrees/W2-76          e1ddcaa6 [w2/W2-76]
  /home/usain/gov-os-worktrees/W2-77          3ce51300 [w2/W2-77]
  /home/usain/gov-os-worktrees/W2-78          8e7640b9 [w2/W2-78]
  /home/usain/gov-os-worktrees/W2-81          166f459f [w2/W2-81]
  /home/usain/gov-os-worktrees/W2-84          e3096fae [w2/W2-84]
  /home/usain/gov-os-worktrees/W2-85          d113ff5e [w2/W2-85]
  /home/usain/gov-os-worktrees/W2-86          01e21d63 [w2/W2-86]
  /home/usain/gov-os-worktrees/W2-87          51a72c7f [w2/W2-87]
  /home/usain/gov-os-worktrees/W2-90          12f85350 [w2/W2-90]
  /home/usain/gov-os-worktrees/W2-90b         d2408361 [w2/W2-90b]
  /home/usain/gov-os-worktrees/W2-91          e7935f2d [w2/W2-91]
  /home/usain/gov-os-worktrees/W2-92          fd03541c [w2/W2-92]
  /home/usain/gov-os-worktrees/W2-95          6ce82952 [w2/W2-95]
  /home/usain/gov-os-worktrees/W2-96          220e2923 [w2/W2-96]
  /home/usain/gov-os-worktrees/W2-97          115def7e [w2/W2-97]
pending owner decisions: not known to the hook; see the written part of this checkpoint
<!-- GENERATED STATE BLOCK END -->
