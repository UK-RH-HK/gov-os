# Start here — the next CTO session (written 2026-11-03 14:05 by session bb5cd8bd)

You are the Wave 2 orchestrator (the CTO), `orchestrator DAEO-sdxk`, in the main tree on `w2/integrate`, in
**emergency mode**. This file maps everything you need, in order. Where it and an older note differ, this file holds;
the register and the owner's word hold over both.

## 1. The emergency: in force
- **What holds it:** DEC-1047 (the emergency raised; the refactoring and the basis), DEC-1049 (no nightly full suite
  until the owner's word), DEC-1050 (the twelve decide-first rows), DEC-1051 (everything stopped until the
  refactoring and the re-pins; nothing scheduled but the dispatcher), DEC-1052 (the basis, the rows, the plan D-0 to
  D-11; and **the basis as a standing practice**: every rule, gate, check or KPI line is assessed against the five
  questions at adoption, on symptoms and weekly, the lift-or-remove list to the owner first), DEC-1053 (D-0 done).
  DEC-1045 (no gitleaks scan here) stands.
- **Allowed:** the plan's steps in order (§5), with engineers, test designers, reviewers and research as in-session
  agents of their role; scoped test runs through `tools/heavy_slot.sh`; record commits (`Task:`, `Role:` trailers);
  restarts of the repository's own servers from committed configs; the shared reranker (W2-112) running.
- **Not allowed (must not start):** any lead (the dispatcher's ready list stays empty) and any landing or queue run
  until the plan's restart (after D-10 and the lift); the nightly and its checks (crontab lines stay commented,
  `# DEC-1049 stopped:`), the runs sweep (`# DEC-1050 stopped:`); `tools/bench_loop.sh`, `tools/usage_watch.sh`; the
  guard-refusal harvest (`dispatch/config.json` `guard_harvest_s` 10^9); any full suite (D-10 only, on the owner's
  word), any `gov close`, any gitleaks scan; any change to `.wslconfig` before the RAM upgrade; any machine change
  outside the repository except by an owner ACT (DEC-1038).

## 2. The reading list, in order
1. `governance/project/prompts/w2-orchestrator.md` §0 (the standing decisions in short) and §1 (session start). The
   rest for reference.
2. **This file.**
3. `.gov-runtime/scratch/orchestrator/CHECKPOINT.md`, its **RESUME HERE** (2026-11-03 14:03): the session state, the
   commits, what is open. The rest of the file is history.
4. `governance/project/orchestration/packages/LIFT-1/P1-PLAN.md`, its section **"DECIDED BY DEC-1052"** with the
   status table (it overrides the draft below it): the plan, step by step.
5. `governance/project/orchestration/INTENT-DEC-1052.md`: the owner's one question and five tests; templates; READY and
   DONE by code; the path-map roles; what memory holds. Every step is judged by it.
6. `governance/project/orchestration/OWNER-GLOSSARY.md`: the owner's terms, two lines each (two added today).
7. `governance/project/orchestration/DECISIONS-IN-FORCE.md`: the short list of what holds (DEC-1053's line today).
8. `docs/DECISION_REGISTER.md`: DEC-1047 to DEC-1053 (the last entries; **next free id DEC-1054**).
9. For G-14 (your first task): `.gov-runtime/scratch/orchestrator/drafts/g14/NEXT.md`; for D-3:
   `governance/project/orchestration/packages/LIFT-1/D3-WORKLIST.md`.
10. The common rules for the CTO's agents: `.gov-runtime/scratch/orchestrator/briefs/EMG-common.md`; reviewers:
    `governance/project/briefs/JUDGEMENT.md`.

## 3. Done on 2026-11-03 (session bb5cd8bd)
- **D-0** (DEC-1053 `d855e41a`; the list `packages/LIFT-1/D0-CLEANUP-LIST.md` `ad3d1529`): 43 worktrees and branches
  with nothing unmerged removed (their scratch in `.gov-runtime/scratch/orchestrator/archive/worktree-scratch/` and on
  `record/w2`); `w2/W2-48` deleted; 67 run folders removed (the measures' evidence kept). 32 worktrees left.
- **D-1**, merged as built into `w2/integrate`: W2-122 `5543a03a44c0`, W2-123 `f704f7d3fee3`, W2-112 `9a02a474e3d5`,
  emg/select `b120aad0f048`, emg/noscan `c72ededc5c97`, emg/w1-19-helper `d7b25cf3c605`, W2-126 `0c5d7f4c935f`, W2-04
  `70965cf61311`, W2-54's hard-block case `9894b0cf514a`. **Re-pin window 2:** `pin-9894b0cf` live
  (`packages/ACT-REPIN-W2.md` `70a82a72`; the owner's registry commit `b74d2c7f`).
- **D-2:** E1 (Q-1 attribution once each way, G-1 the landing check; `emg/queue` `2d968b5089c5`, `tools/land.py`
  promoted); R1-21 (`tools/structural_pass.py`, called by `land.py`); the Load Balancer's held-slot fix and O-A1
  (`emg/lb2` `bad90a750fb7`); **the guard**, ACT-GUARD-FIX-4 (`packages/ACT-GUARD-FIX-4.md`, applied: the owner's
  hooks commit `3bc25241`; the `rm` asks removed from `~/.claude/settings.json`; §8 records the stop and the fix,
  `a698ebfe`). Each with one independent review, READY by `tools/verdict.py` (`.gov-runtime/scratch/orchestrator/reviews/`).
- **Reds fixed on the spot:** `043f8222` (W2-123's cap tests), `530879a4` (the test map), `0e6de735` (the path map).
- **W2-112's trial** (`.gov-runtime/scratch/orchestrator/drafts/W2-112-trial/REPORT.md`): it holds; kept running.
- The handover: `06f2078a`, `468475e1`, and this file's commit; `record/w2` synced.

## 4. Live and running now
- **gov:** `~/.local/bin/gov` -> `pin-9894b0cf` (rollback `pin-a7182f6c`, one command in `ACT-REPIN-W2.md`).
- **The guard:** the five rules, with rules 1 and 5 judged only on targets that resolve; `rm` free but the
  catastrophic (refused with a reason); reviewers' records allowed in `.gov-runtime/scratch/orchestrator/reviews/`.
- **The landing tool** (`tools/land.py`, nothing to land): G-1, Q-1, the structural pass.
- **The servers:** the shared embedder 127.0.0.1:11434 (CPUs 12-19, nice 10) and the query server 127.0.0.1:11435
  (CPUs 8-11), both on the GPU (`dispatch/status.txt`: layers 29/29 each).
- **The shared reranker** (W2-112): pid 356621 since 13:45:09, `cuda:0`, ends after 12 h with no search; its slot
  watcher pid 8416 (`tools/rerank_service_slot_hold.py --watch`) holds the other GPU slot.
- **The dispatcher:** cron every minute (`run_tick.sh`, the only active crontab line); ready list empty; admission by
  the Load Balancer's forecast.
- **The sentinel:** tmux `cto-sentinel` (Haiku, Remote Control), its watch writing `log/deadman.log`; the stand-by file
  `log/cto-standby.txt` written at this handover.
- **The samplers:** `mem_sampler.sh`, `kind_sampler.py`, `oom_watch.sh` (and the slot watcher above).
- **Must not start:** §1's list.

## 5. Next, in the plan's order
1. **G-14, role separation from the path map** (D-2's last item). An engineer resumes from `drafts/g14/NEXT.md`
   steps 1-5 (the candidate hook in `drafts/g14/`, the path-map patch, the replay of real reads for false refusals,
   the planted cases, `ACT-G14.md`); one independent review (READY by `tools/verdict.py`); then the owner's ACT.
   Verified by the replay's counts (honest refusals named), the planted cases and the five rules' tests
   (`drafts/act-guard-fix-4/test_guard_fix_4.py`).
2. **D-3, the configuration and text lifts:** the CTO, from `D3-WORKLIST.md` (items 5, 8, 9, 10; item 11, the
   prompt, as one patch to the owner; item 12 with it). Verified by each row's check line and the structural pass.
3. **D-4, the test suite cut** to about 5,000 cases (with T-6, T-7, T-10, Q-8, Q-10 moved there): test designers, one
   independent reviewer; **the deletions and merges listed to the owner first**; the count and the full suite's
   expected time before and after.
4. **D-5 the templates** (product-spec; scripts first; READY and DONE by code), **D-6 the code tidy-up** (engineer +
   review), **D-7 memory's embedding scope** (M-4, with W2-61's measure before and after), **D-8 G-3** (the hidden half
   outside every worktree).
5. **D-9 the WBS refactor** with the homes: the ticket fates and K9 to the owner first, as a list.
6. **D-10 the full suite** on the refactored repository, on the owner's word; then the lift, the restart, the formal
   closes; EXAMIN's adoption.
7. **D-11 the basis as a standing practice**, after the lift.

## 6. Waiting on the owner (now or coming)
- **With G-14:** answered by DEC-1054 (the ticket's own new unit-test files on the designer's no-read list, shared
  test files readable; back to the owner only if the replay shows a problem); then ACT-G14.
- **D-4b, the memory stage** (the owner's re-plan of 2026-11-03 ~14:40): the package to the owner first; nothing
  starts until it is approved.
- **D-3's prompt patch** (R-9, R-11, R-12, O-6, O-11), and the class list of approved server restarts (O-6).
- **D-4's list** of deletions and merges, and whether the lifted features' suites count in D-10's full run (T-10).
- **D-9's list** of ticket fates and K9.
- **D-10's word** for the full suite.
- Nothing is blocking the fresh session's first step.

## 7. The checks at start (after the prompt's §1)
1. `echo "$GOV_ROLE $GOV_TICKET"` = `orchestrator DAEO-sdxk`; `git status --porcelain` in the main tree empty.
2. Register: your session id into `.gov-runtime/scratch/orchestrator/log/cto-session.txt`; `mv log/cto-standby.txt
   log/cto-standby.ended-$(date +%H%M).txt`; arm `bash .gov-runtime/scratch/orchestrator/tools/inbox_wait_quiet.sh`
   (the Bash tool's background run); one test push (`tools/ping_log.sh`, `PushNotification`, `--result`); the
   sentinel's last heartbeat in `log/deadman.log` under 2 hours old.
3. **No hold file:** `.gov-runtime/scratch/orchestrator/log/act-in-progress.txt` must not exist.
4. **The pin:** `readlink -f ~/.local/bin/gov` = `/home/usain/.local/share/gov-os/pin-9894b0cf/bin/gov`; **the guard:**
   `python3 .gov-runtime/scratch/orchestrator/tools/guard4_check.py --settings /home/usain/Dynamic-Agentic-Engineering-OS` = `PASS`.
5. **The settings' first live test:** an `rm` of your own scratch runs with no prompt (the user settings load at
   session start); a catastrophic one would be refused by the hook with a reason (do not try one on real paths).
6. **The servers on the GPU:** `dispatch/status.txt` shows `layers: query 29/29, shared 29/29`; both ports listen.
7. **The shared reranker:** `tail -2 ~/.cache/gov-os/rerank.log` shows `READY pid 356621` and no `END` after it; one
   `gov retrieve "<question>" --json` from `~/gov-os-worktrees/W2-00-store` gives `rerank.by` = `service`. The GPU's
   memory (`nvidia-smi --query-gpu=memory.used --format=csv`): 9,714 MiB at 14:02; about 900 MiB stayed after the
   trial: if it keeps growing, find the holder.
8. **The inbox:** `.gov-runtime/scratch/orchestrator/dispatch/inbox/*.txt`: read and file each.
9. After every record commit: `python3 .gov-runtime/scratch/orchestrator/tools/structural_pass.py /home/usain/Dynamic-Agentic-Engineering-OS HEAD~1`.
