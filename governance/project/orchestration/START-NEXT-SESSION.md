# Start here — the next CTO session (written 2026-11-04 ~18:00 by session 33b3628c)

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
1. `governance/project/prompts/w2-orchestrator.md` §0 (the standing decisions in short) and §1 (session start).
2. **This file.**
3. `.gov-runtime/scratch/orchestrator/CHECKPOINT.md`, its **RESUME HERE** (2026-11-04): the session state, what is open.
4. `governance/project/orchestration/packages/LIFT-1/P1-PLAN.md`, its section **"DECIDED BY DEC-1052"** with the status
   table (D-4b's row holds the measures m1 to m6, re-pin window 3 and the trial).
5. `governance/project/orchestration/DECISIONS-IN-FORCE.md` (DEC-1068, DEC-1069 and today's standing practice:
   the stand-by file while waiting, the sentinel check, bisect only in a throwaway clone, a stop only by named pids).
6. `docs/DECISION_REGISTER.md`: DEC-1054 to DEC-1071 (**next free id DEC-1072**).
7. **D-4b's record:** `.gov-runtime/scratch/orchestrator/drafts/d4b/DAY.md` (today: m6, the trial's rule and state,
   the methods' rule, rows) and `NIGHT.md` (2026-11-04's night: m2 to m5, the GPU trips, the slips); the packages
   `packages/LIFT-1/D4B-NIGHT.md`, `D4B-RESEARCH.md`, `D4B-AUDIT.md`; the measure's audit
   `docs/research/memory-measure-audit/` (RUBRIC.md version 2, VISIBLE.md, HIDDEN.md, NEW-VISIBLE.md) and
   `docs/audit/memory-measure-new-*.md`.
8. The ACTs in flight or done today: `packages/ACT-REPIN-W3.md` (done), `ACT-RERANK-TRIAL-1.md` (section 4 is the
   CTO's: running), `ACT-HLABEL-1`, `-2`, `-3`, `ACT-HNEW-1` (done by the operator).
9. `INTENT-DEC-1052.md`, `OWNER-GLOSSARY.md`; the agents' common rules `.gov-runtime/scratch/orchestrator/briefs/EMG-common.md`;
   reviewers `governance/project/briefs/JUDGEMENT.md`.

## 3. Done (2026-11-03 and 2026-11-04, session 33b3628c)
- **G-14, D-3, D-4** (DEC-1054 to DEC-1063), **D-8** (ACT-D8), **re-pin window 2** (`pin-9894b0cf`).
- **D-4b, the memory stage** (DEC-1055, DEC-1064 to DEC-1069): W2-61h, W2-91, W2-92, W2-13 (S5, S6), D-7 + G4
  (`27a80411`), W2-32 (S1-S5, S7 G1, S8 routing by question type and the phrasings, S9, S10 no CPU fallback, F1; the
  padded reranker bound; contextual headers), the five index-time methods M1-M5 (each off by default, `d9e9f9ea`); the
  adopted methods switched on (`dc8a2829`: `governance/project/rebuild.yaml`, `retrieval.yaml`).
- **The measures** (hit@5): m1 28/48, m2 29, m2g1 35, m3 37, m4 38, m5 38/48 (the product), and on the grown set
  **m6 65/80 (81.2 %): visible 36/40, hidden 29/40** (`24f06026`, the new baseline).
- **Re-pin window 3** (DEC-1068 (e)): `pin-8284fb408bd4` live (the owner's registry commit `b05f62b8`); the
  integration store at `8284fb40` with headers; the main tree's store rebuilt with it.
- **The measure's audit** (DEC-1068, DEC-1069): the rubric, both halves judged blind; every label fix applied (visible
  by an independent session; hidden by the owner's operator); the set grown to **40 + 40**, cross-checked.
- **Found and fixed:** `core.bare` turning true at 00:31 (cause: `git bisect run` from a linked worktree exports
  `GIT_DIR`, and W2-122's test helper ran `git init` with it; the fix for the tests waits for the proposal flow;
  the CTO's rule is in force); the GPU backstop's two trips (a request bound by count, not size: the padded bound now).

## 4. Live and running now
- **gov:** `~/.local/bin/gov` -> `pin-8284fb408bd4` (rollback `pin-9894b0cf`, one line in `ACT-REPIN-W3.md`).
- **The servers:** the shared embedder 127.0.0.1:11434 and the query server :11435, both on the GPU (29/29 layers).
- **The shared reranker:** **stopped for the trial's quiet window** (since 17:54 on 2026-11-04); the trial copy serves on
  `~/.local/share/gov-os/rerank-trial/run/rerank.sock`. The window ends with T6's restore: the live service restarted
  under class 3 (it then starts from the new pin). If you find the window open and no trial step running: run T6
  (`ACT-RERANK-TRIAL-1.md` section 5) first.
- **The hold file** `log/act-in-progress.txt`: the CTO's own, for the trial window; it ends with T6.
- **Watchers:** the dispatcher (cron); the inbox waiter; `tools/sentinel_check.sh` (the sentinel's login, Remote
  Control, tmux and watch log); `tools/bare_watch.sh` (`core.bare`); `tools/gpu_backstop.sh` twice during the trial
  (`MARK=research-retrieval`, `MARK=rerank-trial`); the samplers; the slot watcher (pid 8416).
- **The sentinel:** tmux `cto-sentinel`, restarted by the operator at 15:17 (its login had expired at 11:43).
- **Must not start:** §1's list.

## 5. Next, in order
1. **The reranker trial** (DEC-1069 (11)-(13); `DAY.md`'s rule, written before any candidate ran): T2 (the 0.6B on
   the trial copy, the faithfulness check against m6), T3 (mxbai-rerank-large-v2), T4 (Qwen3-Reranker-4B 8-bit), each
   with `drafts/rerank-trial/trial_model.sh`; T6, the restore; the result to the owner (all three, both halves, the
   GPU peak, the load time, the speed alone and at 10 and 20 at once). The standing model bench recorded.
2. **The methods' measures** (`DAY.md`'s rule, re-based on m6): each of M1-M5 alone, one run on the 80; m7 with the
   kept ones, three runs.
3. **The embedder trial** (Qwen3-Embedding-4B), after the reranker's decision, measured the same way.
4. **Re-pin window 4:** W2-112's memory release (built on `w2/W2-112`, 52 of 52, not merged) and what the trial and the
   methods adopt.
5. D-5 (with the row: the generated MR-1..MR-6 records take the Contract's status), D-6, D-9, D-10 (the owner's word),
   the lift; D-11 after it.

## 6. Waiting on the owner
- The trial's result and the adoption it implies (the rule decides; the owner sees all three).
- Q07 and Q14 (R11: their answers grow with ordinary work): computed gold (a measure change) or re-worded.
- The visible 40's category shortfalls (2 exact-string, callers, history): filled by the next additions or left.
- The tests' half of the `core.bare` fix (the root conftest clears `GIT_*`; W2-122's helper): a proposal (CIT-P).

## 7. The checks at start (after the prompt's §1)
1. `echo "$GOV_ROLE $GOV_TICKET"` = `orchestrator DAEO-sdxk`; `git status --porcelain` in the main tree empty.
2. Register: your session id into `log/cto-session.txt`; arm `tools/inbox_wait_quiet.sh` and `tools/sentinel_check.sh`
   (the Bash tool's background runs); one test push; the sentinel's last line in `log/deadman.log` under 10 minutes old.
3. **Holds:** if `log/act-in-progress.txt` exists, read it: an owner's ACT means no main-tree commit; the CTO's trial
   window means finish or restore it (T6). While you wait on the owner or the operator, write `log/cto-standby.txt`.
4. **The pin:** `readlink -f ~/.local/bin/gov` = `/home/usain/.local/share/gov-os/pin-8284fb408bd4/bin/gov`; the guard:
   `python3 .gov-runtime/scratch/orchestrator/tools/guard4_check.py --settings /home/usain/Dynamic-Agentic-Engineering-OS` = `PASS`.
5. **The servers on the GPU:** both embedders 29/29 layers; the reranker (after T6): `tail -2 ~/.cache/gov-os/rerank.log`
   `READY ... cuda:0`, and `gov retrieve` from `~/gov-os-worktrees/W2-00-store` gives `rerank.by` = `service`.
6. **`core.bare`:** `git --git-dir=.git config --get core.bare` = `false`; `tools/bare_watch.sh` running.
7. **The inbox:** read and file each item; a `*-sentinel-down.txt` is pushed to the owner at once.
8. After every record commit: `python3 .gov-runtime/scratch/orchestrator/tools/structural_pass.py /home/usain/Dynamic-Agentic-Engineering-OS HEAD~1`.
