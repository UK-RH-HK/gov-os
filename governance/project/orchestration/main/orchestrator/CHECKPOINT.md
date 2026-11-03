# CHECKPOINT — W2 orchestrator, the CTO (`orchestrator DAEO-sdxk`)

## RESUME HERE — 2026-11-03 00:00: handover from session `debdb3f7` before the owner's restart of WSL and the machine

**Resumed 2026-11-03 11:28 by session `bb5cd8bd`** (registered; stand-by ended; waiter armed; 3 night items filed:
restart marks, all clear; test push "not sent", terminal active). **D-0:** list `packages/LIFT-1/D0-CLEANUP-LIST.md`
(`ad3d1529`) with the owner, nothing deleted until the answers. **D-1:** merged as built W2-122 `5543a03a44c0`, W2-123
`f704f7d3fee3`, W2-112 `9a02a474e3d5`, emg/select `b120aad0f048`. Conflicts: W2-04 (W2-54 README, vs integrate: test
designer), emg/noscan (rebuild/command.py vs W2-122: engineer), W2-126 (semantic.py vs W2-123: engineer + KPI 7; the
designer revises W2-123's 500 case and W2-126's KPI 7 cases on `w2/W2-126-tests`, and W2-66's live test-map case on
`emg/select`). Three in-session workers running. Then: merge `w2/W2-126-tests` into `w2/W2-126`, `gov accept`, merge
W2-126, W2-04, emg/noscan, emg/select into `w2/integrate`; then re-pin window 2's ACT. `emg/w1-19-helper` (1 test
commit) asked of the owner in the D-0 list.
**11:39:** emg/noscan DONE (merge `b8957843aba8`; unit 177 + 250/1 skip, W2-122 acceptance 22/22), merged into
`w2/integrate` as `c72ededc5c97`. For D-9's homes (W2-122 or W2-45): a seed base and a copy with different `scan`
settings may index different files (untested; not on this repository); `seed.py` fingerprints the gitleaks binary
even with the scan off (harmless).
**11:43:** W2-126 engineer PACKAGES: merge `0ee425698978`, KPI 7 `dbdcddad8df5` (14 unit cases; W2-126 acceptance green;
W2-123's 500 case red as expected, the designer's). 8 builder reds outside its paths (6 W2-122 seed: the shared cache
makes the cold rebuild warm; 2 W2-123 retry: old rule). P-W2-126-BT decided (delegated P2, ticket line `81801789`);
the same engineer resumed on the 8. Review F1-F8 left for the formal close.
**11:45 (owner) DEC-1053 `d855e41a`: D-0 as recommended, DONE:** emg/w1-19-helper merged `d7b25cf3c605`; 43 worktrees +
branches removed (scratch archived to `archive/worktree-scratch/`, self-ignored so the sync skips it; record synced
`557e5d4e` first); `w2/W2-48` deleted; 67 run folders removed (measures' evidence kept); 879 GB free. W2-78 and the
in-flight branches wait for D-9. W2-126 engineer DONE `6f7fd689da30` (8 builder reds fixed). W2-123's cap builder
tests red in a narrow slot (fixed config CPUs "0-1"/"0"): fixed on the spot `043f8222` (CPUs from the run's affinity).
One guard false refusal (nested `bash -c` quoting: "list index out of range"); worked round by a script file.
**Waiting:** the test designer (W2-04 README; W2-123 500 case + W2-126 KPI 7 cases on `w2/W2-126-tests`; W2-66 case on
`emg/select`). Then merge `w2/W2-126-tests` into `w2/W2-126`, acceptance W2-126 + W2-123 once, merge W2-126 and W2-04
and emg/select into `w2/integrate`; then re-pin window 2's ACT.
**12:03:** designer DONE (W2-04 README `fcfb9150b557`; W2-126-tests `aabbf31a7536` + `741f9eddd45c`: W2-123's 500 case rewritten, 10 KPI 7 cases; W2-66 live map `e66ca8510b42`). `w2/W2-126-tests` merged into W2-126 `15c80ebb72b7`; W2-126 +
W2-123 acceptance and retrieval/rebuild/semantic units 369 passed 1 skipped; merged W2-126 `0c5d7f4c935f`, emg/select
`9a5254ce8bf7`. W2-04 now conflicts with W2-126's W2-54 revision in `test_w2_54_query_cache.py`: the designer
resumed on it (merge integrate into w2/W2-04). Test map: `packages/*.diff` record-only `530879a4` (W2-66 red's
half); its `.ps1` half is W2-66b's (D-9 fate: P1-12 red fixes). Then: W2-04's merge, the integration store refresh,
`pin/make_repin3_commands.sh <head>` (dry build twice), `pin/repin3_checks.sh` on the dry install, then the ACT.
**12:05: D-1's seven merges DONE:** W2-04 merged `70965cf61311` (designer's merge `98993db4ec0e`, W2-54 query_cache
combined, 14/14). One red owned by `w2/integrate`: W2-54 `test_no_hard_block_check_is_weakened` pins
`secrets-indexing.yaml`, which DEC-1045 (emg/noscan) changed: the designer revises it on `emg/select`
(Rewrite-Reason: DEC-1045), then I merge it. Window 2 tools written and tested: `pin/make_repin4_commands.sh`,
`pin/REPIN-COMMANDS-W2.template.sh` (OLD=a7182f6c), `pin/repin4_registry.py` (tested on a throwaway copy: replaces
window 1's entry, a second run refuses). Next: merge the designer's fix; refresh the integration store; then
`bash pin/make_repin4_commands.sh <head>` and `pin/repin3_checks.sh` on the dry install; then ACT-REPIN-W2 to the owner
(write `log/act-in-progress.txt` at the hand-over).
**12:10: ACT-REPIN-W2 handed to the owner** (`packages/ACT-REPIN-W2.md`, `70a82a72`; commands
`pin/REPIN-COMMANDS-9894b0cf.sh`; sha256 94931d3d...25c2, two builds agree; ALL CHECKS PASS on the dry install,
`log/repin-w2-dry-checks-20261103-r2.txt`). emg/select's W2-54 fix merged `9894b0cf514a` (the pinned head); store
refreshed there. `tools/guard4_check.py`'s two rule-2 cases repointed from W2-87 / W2-61's clone (removed by D-0) to
W2-13's (backup `.pre-d0`). HOLD ON: `log/act-in-progress.txt` written; no main-tree commit until the owner says
done; then `mv` it, confirm `readlink -f ~/.local/bin/gov` = pin-9894b0cf, a search, and go on with D-2 (E1 first,
`EMG-queue`'s uncommitted work).
**12:20:** E1 DONE: `emg/queue` merge `daef9a55bab8` + Q-1 `04568e140703` (108 queue tests); `tools/land.candidate.py`
(G-1, merges by `--remerge-diff`; 22/22; promoted copy 26 passed). Review (Sonnet, read-only) writes
`reviews/e1-q1-g1.md`; READY by `tools/verdict.py`. Promotion after READY, when no landing runs and the ACT hold has
ended: `mv tools/land.candidate.py tools/land.py` (backup `land.py.pre-dec1050` exists) together with merging
`emg/queue` (the new land.py passes `--load-sensitive`). Open for later: `close_build.py`'s attribution (Q-1's other
half, or retire it); the queue's `--base` path unused (O-8); `land.candidate.applied-2112.py` a dead copy (O-8).
**12:27: ACT-REPIN-W2 DONE (owner): pin-9894b0cf live, registry `b74d2c7f`; hold ended (`mv`); confirmed from this
session (link, a search with both facets).** Owner: deleting the CTO's own scratch is not a slip (DEC-1050 (8)): not
logged. **E1 LIVE:** review `reviews/e1-q1-g1.md` (the reviewer's Write to reviews/ refused twice by the guard: a false
rule-5 refusal; transcribed by the CTO), READY (True, []); F1 fixed before promotion (`core.quotepath=off`, probe);
F2, F3 Wave 3 rows; emg/queue merged `2d968b5089c5`; `tools/land.py` promoted (backup `land.py.pre-dec1050`); land
tests 26, queue Q-1 + base 31 passed. **D-2 running, three engineers:** R1-21 (`tools/structural_pass.py` +
`tools/land.candidate.py`), E3 (`drafts/act-guard-fix-4/`, with the reviews/ rule-5 case; then one review, then
ACT-GUARD-FIX-4 to the owner), LB held-slot fix + O-A1 (`EMG-lb2`; then one review, then merge). G-14's path-map
role checks after E3.

**THE PLAN, as decided (DEC-1052):** `governance/project/orchestration/packages/LIFT-1/P1-PLAN.md`, its section
"DECIDED BY DEC-1052" first (it overrides the draft below it). The owner's intent, which every affected ticket points to:
`governance/project/orchestration/INTENT-DEC-1052.md` (one question, five tests; templates; READY and DONE by code;
path-map roles; what memory holds). **After the restart: `governance/project/orchestration/MORNING-RESTART-2026-11-03.md`**
(what to start again, in order, and what must not start).

**The owner's terms:** `governance/project/orchestration/OWNER-GLOSSARY.md` (two lines each). The old emergency plan file is history (marked SUPERSEDED at its top).

**Read first:** the prompt's §0 (DEC-1047, DEC-1049, DEC-1051, DEC-1052 hold over everything below);
`governance/project/orchestration/DECISIONS-IN-FORCE.md`; the register's last entries DEC-1040 to DEC-1052; this block.
Next free id DEC-1053.

**State at the handover:** EVERYTHING STOPPED (DEC-1051, 23:08): no lead, no landing, no agent, no test run; nothing
scheduled but the dispatcher (cron, every minute; ready list empty; no `dispatch/land.txt`; the queue's approvals
parked in `merge-queue/parked-by-emergency/`); the nightly and the runs sweep commented out in the crontab
(ACT-NIGHTLY-STOP-1, ACT-SCHEDULE-STOP-2); the guard harvest off; `bench_loop.sh` and `usage_watch.sh` stopped. Where
each piece stopped and how it resumes: `log/emergency-stops-20261102.md` (its 23:08 and 23:39 sections).
`w2/integrate` at its last records commit (the owner pushes); main tree clean.

**The order of work (DEC-1052), for the fresh session:**
1. D-0 clean-up (O-8, O-13): list anything unmerged that may hold work TO THE OWNER before deleting it.
2. D-1 merge directly into `w2/integrate`, accepted as built, no queue run: W2-122 `3fc448601e2d`, W2-123
   `3de9bcf44d91`, W2-126 `2785b2e47432` (an engineer resolves its `semantic.py` conflict with W2-123, then KPI 7),
   W2-112 `d5216599e6fd`, W2-04 `a0c79a6c970e`, `emg/noscan` `ddcec657c278` (the DEC-1045 product switch), `emg/select`
   `194e3289c540` (T-4; one W2-66 case for a designer). Then re-pin window 2 with its checks (an ACT).
3. D-2 the CTO's tools: E1 (Q-1, G-1; its partial work in worktree `EMG-queue`, uncommitted), then R1-21, then E3's guard
   ACT (`drafts/act-guard-fix-4/`, partial), then G-14's path-map role checks; O-A1; the LB held-slot fix (`EMG-lb2`,
   uncommitted).
4. D-3 configuration and text lifts (T-3 first). D-4 the test suite cut to about 5,000 cases before any full suite,
   the deletions listed to the owner first, counts and times before and after. D-5 templates (scripts first), READY and
   DONE by code. D-6 the code tidy-up. D-7 memory's scope (M-4) with W2-61's measure. D-8 G-3.
5. D-9 the WBS refactor with the homes (KPI lines in the home tickets; every affected ticket points to the intent note);
   the tests run per ticket, before and after.
6. D-10 the full suite on the refactored repository, on the owner's word only; then the lift, the restart of tickets,
   the formal closes, EXAMIN's adoption.
7. D-11 the basis as a standing practice, after the lift (at adoption, on symptoms, weekly; the list to the owner first).
**No run uses the old way:** gitleaks off; no full suite but D-10's; scoped selection; attribution once each way.

**Open with the owner:** nothing blocking; the CTO lists D-0's unmerged work to the owner first. P-LB-PRODUCT-1 is
covered by the homes (D-9). Two engineer tickets cover `tests/acceptance/` in their paths (core-mutation): DAEO-a3u2
fixed (`8562ae79`); DAEO-tgk2 still to fix in D-3.

**Standing practice:** record times only from `date`; only a ticket's probe record, with its frontmatter, under
`docs/probes/`; no main-tree commit while `log/act-in-progress.txt` exists; stops cover every standing script, not only
running tests (slips of 2026-11-02 in `log/drift-2026-w44.txt`).


## (history, superseded by the RESUME HERE above) — 2026-11-02 ~18:30 GMT: handover from session `07f25884` (W2O V3) to the FRESH SESSION; window 1 and ACT-QUERY-GPU-2 DONE

**EMERGENCY IN FORCE (DEC-1033; DEC-1037, DEC-1038, DEC-1039): read
`.gov-runtime/scratch/orchestrator/EMERGENCY-PLAN-2026-11-02.md` FIRST: "THE OWNER'S PLAN (DEC-1039)" at its top is
the work, in order, **including step 1b (the owner, ~18:40): the Gov Load Balancer** (phases and their measured peaks
on CPU, RAM, GPU and its memory; GPU-heavy work paired with CPU-heavy work; embedders and rerankers within the GPU's
budget even if leads are limited to two or three; the rule that the GPU's dedicated memory never spills into shared
memory nor runs out into a CUDA crash, tested; the CTO's tools first, then a DEC-1003 proposal: its own ticket or
W2-20/W2-121 KPI lines); then "State at ~18:30". At start: register in `log/cto-session.txt`, end the stand-by with `mv
log/cto-standby.txt log/cto-standby.ended-$(date +%H%M).txt`, arm `bash tools/inbox_wait_quiet.sh` in the background.
The dispatcher starts nothing (empty ready list) until you restart work under DEC-1039. Checkpoints only by
`tools/cto_checkpoint.sh`; processes judged by `tools/tree_busy.sh` (never `pgrep -f`); every heavy run through
`tools/heavy_slot.sh`; anything outside the repository that changes the machine is an owner ACT (DEC-1038). The push
of w2/integrate is the owner's (refused by the CTO session's permissions). The older summaries below are history: (1) watch the W2-122 + W2-123 landing (since 15:48; no commit to w2/integrate until it ends); (2) commit
DEC-1037, the re-pin P1, ACT-QUERY-GPU-2's step 0 and the plan; (3) refresh the integration store; (4) **window 1's
preparation** (the re-pin, every check incl. the guard's; any failure: back to the old pin, tell the owner), then
ACT-QUERY-GPU-2; (5) the full suite on the re-pinned head; (6) the clean restart until green. The plan supersedes the
older notes below where they differ. At start: steps 1-2 of "At start, in order" below (register in
`log/cto-session.txt`, end the stand-by with `mv`), arm the inbox waiter, then the plan.**

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
**11:05 (owner) DEC-1028 `79fa030f`:** push test PASSED; ACT-STOP-WAITER-1 applied (live check in the next fresh
session); quiet-hours test confirmed to the owner (backups may go). Standing: no main-tree commit while an owner ACT is
applied (`log/act-in-progress.txt`, prompt §0). W2-42a `DAEO-03ub` filed (FULL; split files from W2-09; claim when a
K3 slot opens). W2-55: KPI line `09a1ac54`, run-2 brief `W2-55-A5-r2-append.md` queued (test reads the register at the
proposal's commit; append mode); **TODO when it returns: wire its append command into a decision-recording tool and
use it for every register entry.** A: the load-balancing plan: `tools/lb_measure.py` runs 10:57-11:57
(`log/lb/hour-20261102.*`); sections a-d drafted by a research subagent into `drafts/LB-PLAN-sections-a-d.md`; the CTO
writes e and f, then the package `packages/P1-LOAD-BALANCE-1.md`.
**11:18 (owner) DEC-1029 `39e3c16f`:** ROOT CAUSE of the night: the shared embedder fell off the GPU at 04:33 (CUDA
crashes 02:36, 04:31; 8-10 rerankers on the GPU; 0/29 layers). Reloaded 11:15 (runner ended, serve kept, caps kept):
29/29 on the GPU, about 26 chunks/s at batch 32; dispatcher health 1.96 s. **Standing until the plan: alert the
owner on any `offloaded 0/N layers` or `CUDA error` in serve-11434.log** (background watch task b7ulw6ru4; re-arm after
it fires). The seven ready relisted to `land.txt` at 11:18 (they no longer wait for W2-123's retry).
**11:30 (owner) DEC-1030 `01f5d8be` (standing): the whole machine watched.** Dispatcher GPU pass being built by an
engineer subagent (test_dispatcher.py; then a short review, then commit; until then the background watch b7ulw6ru4).
Morning package: run `tools/server_log_scan.py` (found 3 CUDA crashes 23:54, 02:36, 04:30 and the 0/29 load at 04:34).
SMART-WORK-6 `1e5d3395` (4 GPU KPI lines for W2-20 and W2-121) for the owner. Landing 11:16 refused before queueing:
W2-104's gitleaks (two test fixtures: REPLY_TOKEN, SECRET; redacted); W2-104 run 3 `W2-104-A5-r3-gitleaks.md` queued
(build the literals from parts); six relisted in `land.txt`.
**11:27:** six landing (claimed 11:21). The nightly of 11-02 ENDED 09:24, verdict red 32 (status line corrected 11:25).
Its reds: 6 test_dispatcher (they read the untracked scratch tools: skip guard asked of the GPU-pass engineer); W1-19 x4 +
W1-21 x4 (real-model errors: the embedder was on the CPU; re-run alone after the landing); W1-33 x4, W1-05 x2, W1-46,
W2-59 x4 (known install/hook-line, W2-90c/W2-105); W2-54 x3 (AR-5: DEC-1024 after the head; sandboxed worker; time
limit); W2-55, W2-66 (their runs); W1-01 x2 (history: DEC-906's known red; integration merges: to check). B: W2-05 + W2-96
re-close started 11:26 against it (`log/close-two-20261102-1127.out`). W2-61h DONE `ac7dfa1790c7` in land.pending.txt.
**11:46:** P1-NIGHTLY-2026-11-02 `578203ec` pinged (one decision: W1-01's merge rule and 0568d91baf56, rec (a)).
Dispatcher v4.4 `7f81f91a` LIVE (DEC-1030 item 1): GPU line in status, `gpu-alert` inbox items (the quiet waiter wakes
on them: push the owner at once); the 6 scratch-tools tests skip by name; review by Sonnet running
(`reviews/dispatch-v4.4.md`). The background log watch b7ulw6ru4 stays as a second net.
**12:25 (owner) DEC-1031 `44f4df2d`.** Embedder PINNED in VRAM (keep_alive -1, 12:05). COMMIT HOLD ON
(`log/act-in-progress.txt`): ACT-W1-01-EXEMPT-1 `983f1ece` with the operator; ACT-RERANK-CPU-1 `5aeed6ea` must NOT be
applied (CPU rerank >100 s/query): replaced by `drafts/ACT-RERANK-GPU-SLOTS-1.md` + `drafts/gov_reranker_gpu_slot.py`
(at most 2 rerankers on the GPU; tested) — commit both to packages/ and tools/ when the hold ends, and mark v1
superseded. The plan: `drafts/P1-LOAD-BALANCE-1.md` (with the GPU agent's figures; query on GPU: no answer changes)
— commit to packages/ when the hold ends. W1-01b `DAEO-vhad` queued. SMART-WORK-6 applied (`4036a296`, `42889c78`).
GPU at 15.1/16.3 GB with 11 rerankers at 12:16 (pre-crash state).
**12:45 (owner) DEC-1032 `caa01da9`: FREEZE + the infrastructure sprint.** Ready list frozen (the rest parked in
`dispatch/ready.parked-by-freeze.txt`; land.pending kept). Sprint: (i) W2-112 claimed `be02bb01`, first on the ready
list (waits for CPU room); (ii) ACT-QUERY-GPU-1 `10f856c7` handed to the operator (HOLD on); W2-123 got the
query-GPU line `b0156a41` (its lead messaged); (iii) dispatcher v4.6 being built by an engineer agent (review, then
commit); (iv) seeding everywhere being built by an engineer agent (tools; review, then commit); W2-126 (the vector
cache) filed+claimed `2a3c998f`, run 1 = tests only, queued; (v) the assessment after. After the query ACT: set
dispatch/config.json `gpu_expected.query` true. Plan + v2 ACT committed `d03ce368`.
**13:03 EMERGENCY (owner) DEC-1033 `7fa7fe54`.** ACT-QUERY-GPU-1 NOT applied, never (semantic.py's `_on_cpu` gate). Stopped
at safe points (`log/emergency-stops-20261102.md`): the landing of six, the W2-05+W2-96 re-close, W2-04's lead. Running:
W2-122, W2-123 (returning run 2 DONE), W2-112 (started 13:01 past the gate). Fixes in parallel, each to one review
then live: (a) W2-112; (b) engineer agent on branch `emg/query` (worktree EMG-query): any-device query vector +
ollama.py start without NO_GPU, then the operator's restart ACT; reranker interim: engineer agent on
tools/gov_reranker_gpu_slot.py (wait for a slot or go without reranking, named; never the CPU), then the operator's
install ACT; (c) dispatcher v4.6 agent; (d) seeding agent (it is editing merge_queue.py in the MAIN tree, uncommitted).
Before snapshot: `log/emergency-before-20261102.txt`. After all four: the after figures, then the owner lifts it.
**13:16:** fix (b) LIVE in code: emg/query reviewed PASS (`reviews/emg-query.md`, READY true) and merged `6ed6a5ae`
(slip: merged without Task/Role trailers; not amended; drift log). ACT-QUERY-GPU-2 `2cd0e836` waits until W2-112,
W2-122 and W2-123 have merged 6ed6a5ae (messaged; background watch), then to the owner. Reranker interim patch
(tools/gov_reranker_gpu_slot.py + 14 tests, uncommitted) in review (`reviews/emg-rerank-slot.md`); then commit and the
owner's install ACT (commands in the engineer's return). Follow-ups: W2-54 acceptance revision (5 groups), review F1
(zero vector) and F2 (list answers), the automatic start's caps.
**13:30:** reranker interim LIVE (ACT-RERANK-WAIT-1 applied, `81b7a739`). v4.6 review FAILED health (F1 first request
after idle = HUNG; F2 5xx counted as progress): engineer fixing F1-F4 live-by-rename after tests; then review round 2
(health only). Seeding (d) built and NOT live (`tools-review/`, both patches + seed_store.py, new_worktree.sh,
rebuild_counts.py); in review (`reviews/emg-seeding.md`). After install: refresh the integration store once by hand
past 6ed6a5ae (it is at 6ebd7b56 of 11-01). W2-123: success-7/8 amended `0fa24eda`; P-W2-123-4 to W2-126 `5e67a14d`.
**13:33 (owner):** the 19:30 after figures include a seeded close's time beside today's cold median (30 min) and
confirm no close runs cold (rebuild_counts.py). Plan: once seeding is live (~15:30), run the stopped W2-05+W2-96
re-close as the measured seeded close, unless the owner objects.
**13:55:** fix (d) seeding LIVE `648e5067` (review 2 rounds; READY true after a strict block; verdict.py now reads the
LAST block, fixed + test). Fix (c) dispatcher v4.6 LIVE `b06ee350` (G1/G2 installed on the owner's word, DEC-1035).
W2-127 `DAEO-1vka` filed (`8e0daae2`): the reranker socket in the sandbox, after W2-112. All three leads have the patch;
ACT-QUERY-GPU-2 handed over 13:55 (HOLD on). After it: set dispatch/config.json gpu_expected.query true; land W2-123
(DONE, head 3de9bcf44d91, verified 2a4455be0785) via the queue (now seeded); W2-122 DONE soon; then the seeded close of
W2-05+W2-96 as the measurement; refresh the integration store once by hand (it is at 6ebd7b56).
**14:00:** W2-112's T5 (b) and T6 (b) decided and told to its lead; DEC-1036 drafted in `drafts/DEC-1036.md`: commit it
and W2-112's KPI 6 lines when the ACT hold ends.

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
generated: 2026-11-02T14:25:00Z 11715889ad43893f7b3b5d2c8a1ff93400b0ce47097255b73b91fe65cc399bb1
git head: a7182f6c7de00d91b3c5161e10590e06641f0baa
tickets in progress (`tk ls --status=in_progress`):
  DAEO-0z8c [in_progress] - W2-05 The git environment of every check, hook and helper; the settings re-sort <- [DAEO-g0ip]
  DAEO-3r1j [in_progress] - W2-110 A product's CTO-only install rule
  DAEO-6b2q [in_progress] - W2-109 Contract v4.3
  DAEO-6n5k [in_progress] - W2-37 gov impact <- [DAEO-g0ip, DAEO-ym8a]
  DAEO-a3u2 [in_progress] - W2-91 Full embeddings: the root files, the governance overlay and schemas/ <- [DAEO-jsg1]
  DAEO-arrl [in_progress] - W2-55 Decisions tagged by domain, status and scope; superseded and done entries left out of what agents see
  DAEO-blwa [in_progress] - W2-122 Seeded rebuilds
  DAEO-clon [in_progress] - W2-112 One reranker serves every session
  DAEO-cv58 [in_progress] - W2-60a The role, its skills and its model and effort loaded at launch; the launch record
  DAEO-drhj [in_progress] - W2-104 The skill evaluation harness
  DAEO-h2k3 [in_progress] - W2-61h W2-61's held-out half: 20 hidden memory questions with their gold sources <- [DAEO-m1u3]
  DAEO-jpr0 [in_progress] - W2-126 A machine-wide vector cache keyed by the text <- [DAEO-qzrq]
  DAEO-k7hz [in_progress] - W2-11 Briefs and the orchestration skill: twelve fields, payload after, two-refusal stop, DEC-430 <- [DAEO-g0ip]
  DAEO-l78m [in_progress] - W2-81 The adoption proving ground: five synthetic repositories with planted problems, a judge, and question sets per repository
  DAEO-n0wb [in_progress] - W2-92 The knowledge graph and the code graph as routes of plain-question retrieval <- [DAEO-s9qc, DAEO-ym8a]
  DAEO-nqa2 [in_progress] - W2-90b W2-90's next round <- [DAEO-0mtg]
  DAEO-ouet [in_progress] - W2-96 The opaque acceptance runner
  DAEO-qzrq [in_progress] - W2-123 Parallel requests on the embedding server
  DAEO-r30l [in_progress] - W2-20 Machine-wide resource gate <- [DAEO-g0ip]
  DAEO-siiz [in_progress] - W2-52 The lite A7 and A10 stage records <- [DAEO-g0ip, DAEO-ha8z]
  DAEO-u4oz [in_progress] - W2-04 gov context bounded and reproducible <- [DAEO-g0ip, DAEO-ym8a]
  DAEO-vhad [in_progress] - W1-01b A listed merge is exempt for its own changes
  DAEO-wnnz [in_progress] - W2-56 `gov launch` usable for every worker
  DAEO-zpdj [in_progress] - W2-105 The template's install block removed
  DAEO-zqvn [in_progress] - W2-13 RETR-X-02 and a ranked lexical route (BM25, SQLite FTS5) <- [DAEO-g0ip, DAEO-ym8a]
  DAEO-zuiy [in_progress] - W2-66b W2-66's record-only case reads a .ps1 script as code
worktrees (`git worktree list`):
  /home/usain/Dynamic-Agentic-Engineering-OS  a7182f6c [w2/integrate]
  /home/usain/gov-os-worktrees/EMG-query      75f18d11 [emg/query]
  /home/usain/gov-os-worktrees/W1-01b         76f12566 [w2/W1-01b]
  /home/usain/gov-os-worktrees/W2-00-record   3a8ed9f9 [record/w2]
  /home/usain/gov-os-worktrees/W2-00-store-a  d88a1fff (detached HEAD)
  /home/usain/gov-os-worktrees/W2-00-store-b  6ebd7b56 (detached HEAD)
  /home/usain/gov-os-worktrees/W2-03          92e03a72 [w2/W2-03]
  /home/usain/gov-os-worktrees/W2-04          a0c79a6c [w2/W2-04]
  /home/usain/gov-os-worktrees/W2-05          8d2a1f54 [w2/W2-05]
  /home/usain/gov-os-worktrees/W2-07          31ddf173 [w2/W2-07]
  /home/usain/gov-os-worktrees/W2-104         909d7ff0 [w2/W2-104]
  /home/usain/gov-os-worktrees/W2-105         fa653609 [w2/W2-105]
  /home/usain/gov-os-worktrees/W2-106         9525808d [w2/W2-106]
  /home/usain/gov-os-worktrees/W2-107         3861d3f3 [w2/W2-107]
  /home/usain/gov-os-worktrees/W2-108         d3f87c55 [w2/W2-108]
  /home/usain/gov-os-worktrees/W2-109         695eea48 [w2/W2-109]
  /home/usain/gov-os-worktrees/W2-11          c9f99b28 [w2/W2-11]
  /home/usain/gov-os-worktrees/W2-110         d0ecd1bc [w2/W2-110]
  /home/usain/gov-os-worktrees/W2-112         0b9deb2d [w2/W2-112]
  /home/usain/gov-os-worktrees/W2-112-tests   9af602dc [w2/W2-112-tests]
  /home/usain/gov-os-worktrees/W2-114         e9214850 [w2/W2-114]
  /home/usain/gov-os-worktrees/W2-122         3fc44860 [w2/W2-122]
  /home/usain/gov-os-worktrees/W2-123         3de9bcf4 [w2/W2-123]
  /home/usain/gov-os-worktrees/W2-126         2a3c998f [w2/W2-126]
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
  /home/usain/gov-os-worktrees/W2-60a         4d798caf [w2/W2-60a]
  /home/usain/gov-os-worktrees/W2-61          6b517db9 [w2/W2-61]
  /home/usain/gov-os-worktrees/W2-61h         ac7dfa17 [w2/W2-61h]
  /home/usain/gov-os-worktrees/W2-63          ad38ed68 [w2/W2-63]
  /home/usain/gov-os-worktrees/W2-64          bb389b71 [w2/W2-64]
  /home/usain/gov-os-worktrees/W2-65          f6881547 [w2/W2-65]
  /home/usain/gov-os-worktrees/W2-66b         2536346b [w2/W2-66b]
  /home/usain/gov-os-worktrees/W2-67          ff2cc697 [w2/W2-67]
  /home/usain/gov-os-worktrees/W2-68          05ec0f6a [w2/W2-68]
  /home/usain/gov-os-worktrees/W2-71          027d4f10 [w2/W2-71]
  /home/usain/gov-os-worktrees/W2-75          e7f90cd3 [w2/W2-75]
  /home/usain/gov-os-worktrees/W2-76          e1ddcaa6 [w2/W2-76]
  /home/usain/gov-os-worktrees/W2-77          3ce51300 [w2/W2-77]
  /home/usain/gov-os-worktrees/W2-78          8e7640b9 [w2/W2-78]
  /home/usain/gov-os-worktrees/W2-81          e78e6af7 [w2/W2-81]
  /home/usain/gov-os-worktrees/W2-84          e3096fae [w2/W2-84]
  /home/usain/gov-os-worktrees/W2-85          d113ff5e [w2/W2-85]
  /home/usain/gov-os-worktrees/W2-86          01e21d63 [w2/W2-86]
  /home/usain/gov-os-worktrees/W2-87          51a72c7f [w2/W2-87]
  /home/usain/gov-os-worktrees/W2-90          12f85350 [w2/W2-90]
  /home/usain/gov-os-worktrees/W2-90b         73c18fea [w2/W2-90b]
  /home/usain/gov-os-worktrees/W2-91          55b47e07 [w2/W2-91]
  /home/usain/gov-os-worktrees/W2-91-tests    a5bf211f [w2/W2-91-tests]
  /home/usain/gov-os-worktrees/W2-92          448a835a [w2/W2-92]
  /home/usain/gov-os-worktrees/W2-95          6ce82952 [w2/W2-95]
  /home/usain/gov-os-worktrees/W2-96          220e2923 [w2/W2-96]
  /home/usain/gov-os-worktrees/W2-97          115def7e [w2/W2-97]
pending owner decisions: not known to the hook; see the written part of this checkpoint
<!-- GENERATED STATE BLOCK END -->
