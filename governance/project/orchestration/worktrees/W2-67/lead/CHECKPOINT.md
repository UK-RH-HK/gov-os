# Lead checkpoint — DAEO-9nys (W2-67), run 5 (merge-back, re-verification, fresh probe; DEC-941 item 2, DEC-895): RETURNED PACKAGES (P-W2-67-HOLD5)

## RESUME HERE
- State (2026-10-30 11:42): branch w2/W2-67, head 060955b53618 = the lead's merge of w2/integrate 05009374427a (no conflict; trailers Task: DAEO-9nys, Implements: DEC-941, DEC-895, Role: orchestrator, Co-Authored-By, in the message's last paragraph since git merge has no --trailer). Pre-merge head d0140d4d222e. git status: only `?? tests/acceptance/W1-27/w2_67_td4_plant.py` (keep; never commit or delete).
- Not done: the full verification run, TD1C-A's run outside the sandbox, the KPI 4 count, the gov checkpoint commit, the fresh probe, the probe record, the _check_probe dry run. No repair batch spent; no worker started; loop count 0.
- Why returned: the verification run was held past 90 minutes (DEC-943). 10:10 load gate (another lead's run, load 40-80); verify lock held by W2-84's full run, then W2-61's alone run, then W2-51's full run; from 10:31:17 CLOSE-RUNNING is set by close_queue.sh for five closes (DAEO-ym8a, DAEO-e8f0, DAEO-b6hm, DAEO-cy5o, DAEO-2ds6), and the queue holds the verify lock for its whole run. At 11:41 nothing of mine had started. Both queued jobs (verify5.sh r5 parallel, td1ca5.sh) were stopped before any test ran.
- Done in run 5 and valid on head 060955b53618:
  - W1-30 README at HEAD holds all 27 of integrate's added lines and differs from integrate only by this ticket's 3 lines and a blank; `grep -c '^### DEC-941'` = 1.
  - DEC-895 check: the merge changed five files this ticket's commits changed: tests/acceptance/W1-07/w1_07_support.py, W1-26/README.md, W1-26/test_w1_26_planted_defects.py, W1-27/test_w1_27_doctor.py, W1-30/README.md. Probe must be redone.
  - rebuild-6 (flock /tmp/gov-os-rebuild.lock, this worktree's code): exit 0, store.invalid [], lexical/semantic/codeintel recreated.
  - gov check: exit 0; YELLOW core-decision-citations (warning; other tickets' commits cite DEC-942 not in their trees) and openspec-validate (openspec absent); rest GREEN.
  - collect-only (DEC-868): "17099/17101 tests collected (2 deselected) in 22.37s", exit 0.
  - trailer_gate: "DAEO-9nys: 60 commits, 56 judged, 0 lacking, 0 Implements item(s) not a decision or Contract id that resolves".
  - gov.__file__ = /home/usain/gov-os-worktrees/W2-67/src/gov/__init__.py.
- Integrate moved after the merge: now d52da393492b; W2-03 merged (a8eaf26e), W2-26 merged (816f764f); commit db002376 (W2-03) touches tests/acceptance/W1-26/README.md, a file this ticket changed.
- Containment hook at the merge flagged six Role: owner commits brought from integrate (82f2d4538a53, 8ba8b231a990, 048f5758e1cd, e95d3520db9a, 6367e96597e4, bc37c419359c): the owner's own; nothing of this ticket.
- Next run (recommended): after the close queue ends and before 01:00 (or after the nightly): merge w2/integrate again (one more merge: the closes of W2-03, W2-57, W2-26 etc. change integrate, incl. W1-26/README.md), check W1-30 README and DEC-941 again, rebuild, then verify5.sh with a NEW label (r5 is dirty: verify-r5.summary has stale start lines) parallel, then serial, each as its own bg job launched when the lock is free (the bg job's 2-hour clock starts at launch; the parallel phase took ~55 min, serial ~60 min); td1ca5.sh; KPI 4 count; gov checkpoint commit; reviewer with briefs/rev-4.md (fill __HEAD__, __VERIFY__, __TD1CA__; update the merge lines if merged again).
- Scratch: .gov-runtime 3,325 inodes / 430 MB; /tmp/gov-os-lead-W2-67 2 inodes / 8 KB (verify-r5/ empty).

## Brief gaps (running)
- git merge has no --trailer option; trailers go in a -m paragraph | common brief | 2 min
- w2/integrate had moved (280 behind, not 233) and brought W2-77's test_nightly_cleanup.py and W2-72's two guard unit files into tests/unit | this ticket's part | 2 min
- the close queue (close_queue.sh, five closes) set CLOSE-RUNNING and holds the verify lock for its whole run, starting 3 minutes after this run's verification was ready; the brief did not say a five-ticket close queue was due this morning | this ticket's part | ~90 min (measured: 10:10 to 11:41)
- a background job's 2-hour limit counts from launch, so a full run queued behind another run's lock is killed mid-run; relaunch when the lock frees | common brief | 15 min
- `pgrep -f`/`pkill -f` on a pattern also match the waiting shell's own command line (a wait loop never ended; a pkill killed its own shell) | common brief | 10 min
