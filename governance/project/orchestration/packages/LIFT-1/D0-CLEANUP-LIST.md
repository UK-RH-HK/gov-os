# D-0 — the clean-up list, for the owner before anything is deleted (DEC-1052, O-8, O-13)

Written 2026-11-03 11:45 by the CTO (session bb5cd8bd), read-only so far: nothing has been deleted or moved.
Source: `git worktree list`, `git rev-list --count w2/integrate..<branch>` (commits not in `w2/integrate`),
`git status --porcelain [--ignored]` in each worktree, `tk ls`, `du`. 75 worktrees (27 GB), 77 local branches,
64 run folders under `~/gov-os-runs/` (about 19 GB). Disk: 854 GB free.

**Decided: DEC-1053 (owner, 2026-11-03), every ASK line as recommended.**

## 1. Unmerged work: KEPT (nothing deleted)

**1a. Merged now in D-1** (the plan's list): `w2/W2-122` 17 commits, `w2/W2-123` 20, `w2/W2-126` 15 (its tests branch
is inside it), `w2/W2-112` 24, `w2/W2-04` 19, `emg/noscan` 1, `emg/select` 2.

**1b. Uncommitted work for D-2** (kept as is until its engineer commits it):
- `EMG-queue` (E1, Q-1 attribution once each way): `merge_queue.py` +105/−22 lines, its README, a new test file
  `tests/unit/orchestration/test_merge_queue_q1.py`.
- `EMG-lb2` (the Load Balancer's held-slot fix): `dispatcher.py`, its README, `test_dispatcher.py` (+73 lines).

**1c. In-flight tickets with built, unmerged work** (kept until D-9's fate list, which comes to you first):
W2-11 26 commits · W2-60a 25 · W2-81 19 · W2-92 18 · W2-52 16 · W2-37 13 · W2-91 13 (tests branch inside it) ·
W2-104 11 · W2-110 11 · W2-13 11 · W2-20 10 (from 10-17, 1,648 behind) · W2-61h 7 · W2-105 7 · W2-90b 6 ·
W2-42a 5 (tests branch inside it).

## 2. Unmerged work with no live use — ASK

| item | what it holds | recommendation |
|---|---|---|
| `emg/w1-19-helper` (1 commit `a0d1d3a0`, `Role: independent-test-designer`, DEC-1046 item 3) | the W1-19 test helper hides only ollama, not all of `~/.local/bin` (gitleaks and the rest stay on PATH) | **ASK: merge it in D-1** with the others (it is a test fix the full suite needs), then delete |
| `w2/W2-48` (21 commits, ticket closed, no worktree) | the result cache withdrawn by DEC-880 | **ASK: delete** (its 21 commits become unreachable; recommended: withdrawn, never in the product) |
| `w2/W2-78` (5 commits, ticket open) | the ratchet work; fate proposed "retire" (follows T-4) | keep until D-9's fate list; delete with that answer |
| `W2-67` worktree, untracked `tests/acceptance/W1-27/w2_67_td4_plant.py` | a test designer's planted case left behind; W2-67 closed | **ASK: delete** |

## 3. Nothing unmerged: REMOVED (worktree and branch), after your yes

**ASK: remove these 42** (0 commits not in `w2/integrate`, nothing uncommitted; the only untracked files are
`pytest-of-usain/` leftovers):
- emergency branches already merged: `emg/gitleaks`, `emg/lb`, `emg/noscan-tools`, `emg/query`, `emg/w2-54-dec1033`;
- closed tickets: W2-03, W2-07, W2-16, W2-26, W2-49, W2-51, W2-57, W2-58, W2-61, W2-63, W2-64, W2-65, W2-67, W2-68,
  W2-71, W2-75, W2-76, W2-77, W2-84, W2-85, W2-86, W2-87, W2-90, W2-95, W2-97, W2-106, W2-107, W2-108, W2-114;
- in-progress tickets whose work is all merged (a fresh worktree from the refactored head at the restart):
  W1-01b, W2-05, W2-55 (and W2-55-tests), W2-56, W2-66b, W2-96, W2-109.

Before removal, each worktree's ignored `.gov-runtime/scratch/` (the leads' checkpoints and logs, under 0.7 GB in
all) is copied to `.gov-runtime/scratch/orchestrator/archive/worktree-scratch/<W2>/`, so no lead record is lost.
The worktrees' memory stores are not kept (rebuilt on demand). Frees about 20 GB.

## 4. Kept by rule
`main`, `w1/integrate`, `w1/W1-42` (DEC-711), `record/w2` and its worktree `W2-00-record`, the designers' store
(`W2-00-store-a`, `W2-00-store-b` and the link `W2-00-store`).

## 5. Run folders (`~/gov-os-runs/`) — ASK
- remove the 56 empty or near-empty folders (8 KB or less each);
- remove the base and head clones of finished measures (W2-55, W2-86, W2-87: `base/`, `head/`; W2-61: `repo/`),
  **keeping** their `measure/`, `records/`, `register/` and `logs/` (cited by `docs/research/W2-86-memory-measure.md`
  and `W2-87-memory-measure.md`); W2-13, W2-91, W2-92 kept until their tickets' fates;
- `W2-00/`: remove `close/` (10 old close clones, 5.2 GB), `precheck-w254-20261030-2146/`, `w103-before-w272/`,
  `tooltrials/`; keep `merge-queue/` (the warm clones), `nightly/`, `bench/`, `act-runs/`.

## 6. Not in D-0
The dead copies in the CTO's scratch (`dispatcher.pre-*.py`, `*.reviewed.py`, backups) are O-8, which the plan puts
after E1's promotion (D-2); they go then, from a list like this one.
