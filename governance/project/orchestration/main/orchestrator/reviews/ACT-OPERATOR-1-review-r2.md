# ACT-OPERATOR-1: independent review, round 2 (narrow re-check of F1-F5, F8 and F9)

- **Reviewer:** the same independent session as round 1, which wrote none of the drafts. Read-only except this record.
- **Date:** 2026-11-09, on `w2/integrate` at `010e1f0c0`. ACT-GUARD-CALLLOG-1 was applied live at `b7a373cf9`, so
  the live hook is now `a7981319f877`.
- **Scope:** only the fixes for round 1's F1, F2, F3, F4, F5, F8 and F9 (`ACT-OPERATOR-1-review-r1.md`), and anything
  new those fixes bring in.

## Files as read

| File | sha256 |
|---|---|
| `apply.sh` | `7e9398ad91ca8fe091b23784ae4eacfcccf01623b8a8e5798bfa88389d374fe9` |
| `code/freeze_gate.py` | `00e8ce13249e427626765b1c53b54811815276d6fbed4c8dd55c238c29c4122a` |
| `code/merge_queue.py` | `1f3b1d44f507459337361c20308c36d2e6f7cbfcad3d767b027feef8b734d3da` |
| `code/test_act_operator_1.py` | `5ced364cdf0687f5dd8f0a6aec18aebb8faaa17e0dba1d5795efbbf269c426df` |
| `crontab.line` | `77dcf466177792b5cf02e3afa86b251a1084c9d359b5db6123935fc0bd1c6c07` |
| `rehearse.sh` | `d93709e1e8f5…` |
| `rehearsal-pre.log` | `64ec40532444…` |
| `rehearsal-post.log` | `f19c36a00466…` |

All of these are pinned in `apply.sh`, and `drafts_ok` passes.

## What I ran
All runs were in scratch copies, and nothing live was changed. `apply.sh check` only reads, and it left no `backup/`.
- **The unit tests** (`code/test_act_operator_1.py`), in a scratch layout with the merged operator code and the
  drafts overlaid: **18 passed**.
- **Round 1's gate probes** re-run against the new `freeze_gate.py`, in a scratch repository with a main tree, a
  worktree and a planted freeze. I added two cases: a loose ref packed with `--prune`, and a worktree
  `update-ref -d` of the live branch.
- **`apply.sh check` on the live main tree:**
  - the state is `before` (merge_queue.py at `36c8e1573285`, as `MQ_BEFORE` pins);
  - every draft and every install source is as built;
  - the verdict: "ready to apply (the hook is post-calllog)".
- **Both rehearsal logs, read to the end:** `rehearsal done (pre): … failures: 0` and
  `rehearsal done (post): … failures: 0`.

## The fixes

| r1 | Fix | Evidence | Closed |
|---|---|---|---|
| F1 | `queue_part` gives `absent`, `empty`, `record` or `other`. A record counts as before and as applied; undo keeps a record and removes an empty queue. | Pre: before-undo `queue: record`, after-undo `state before`, "ready to apply again". Post: `queue: empty` removed. Undo exits 0 in both. | yes |
| F2 | The planted sets root is full; the units are run per folder. | guard4 runs `501 ok, last line PASS` before and after, in both kinds. Both logs end `failures: 0`. test_g14's one failure (`test_w2_91_tests_today`) is the same before and after, outside this ACT. | yes |
| F3 | When `old` is zeros it is replaced by the ref's present value. An update where `old` equals `new`, or a deletion, goes on. | My probes: `pack-refs` and `gc` return 0 while frozen. An `update-ref` with no old value is judged on its change: a control change is refused, an unrelated one passes (the new test). | yes (see R2-F1) |
| F4 | `live_branch()` falls back to `refs/heads/w2/integrate`. | My probe: with the main tree detached and frozen, a worktree commit on another branch passes. The new test also shows the live branch is still judged by name. | yes |
| F5 | `merge_queue.py advance()` raises `Stop` while the freeze exists, before its fetch and before any ref or tree moves. `Stop` exits 4 with "entries kept". | The new test, plus the merge queue's five unit files in the rehearsal clone (97 passed, before and after). The gate keeps refusing an ff in the main tree as a backstop; my probe still shows the half-landed tree when it does, so the tool's own check is what prevents it. | yes (see R2-F2) |
| F8 | `sources_ok` runs before the first write, in check and apply. Undo checks every part (applied or before), the crontab table, `install_removable` (a whole or partial install whose files are all the ACT's own) and the queue before it writes anything. Only then does it restore, the crontab first. | Code read. A partial apply that died in step 2 now undoes cleanly: no `APPROVED.sha256` is accepted, the files are checked against `install.sums`, and then removed. Both rehearsal undos end `state before`. | yes |
| F9 | Hours `0,8-23`. | `crontab.line`: the last launch is at 00:50, so a 45-minute session ends before 02:00. | yes |

## New findings (none blocking)

| id | Finding | Blocking | One-line fix |
|---|---|---|---|
| R2-F1 | To let `pack-refs --prune` through, the gate now lets any deletion of the live branch go on. In my probe, pack-refs sends `0 → X` and `X → 0` for a loose live ref. A real `update-ref -d refs/heads/w2/integrate` while frozen now passes, where round 1 refused it, and HEAD is left unborn. That is no ordinary work, and it still fails closed: the operator's next commit onto the unborn HEAD is refused as "created while it holds", so the run undoes, holds the lock and sends a P1. | no (not ordinary; fails closed) | Let a deletion through only when the same input also carries pack-refs' `0 → <that old>` line for the same ref |
| R2-F2 | The merge queue reads the live freeze path by default (`/home/usain/gov-os-operator/install/act-in-progress.txt`). Its own tests (the unit files, W2-97, W2-136) would stop with exit 4 if they ran during a live apply. That is a spurious red, not a hole. | no (other) | The merge queue's tests set `MERGE_QUEUE_OPERATOR_FREEZE` to a temporary path (conftest), as the new test does |

A note: a freeze written in the instant between `advance()`'s check and its `merge --ff-only` would still half-land
the tree. The window is milliseconds, the gate backs it up, and the operator fails closed. No action needed.

Round 1's F6, F7 and F10-F12 were outside this round. F7 is now moot, since CALLLOG-1 was applied first. The others
stand as round 1 left them: notes for the package message.

## Verdict
**READY.** Every fix in scope works: by code, by the 18 unit tests and by my probes. Both rehearsals end
`failures: 0` with the live files unchanged, and the live `apply.sh check` says ready (post-calllog). The two new
findings fail closed and are not ordinary work.

```verdict
{"manifest": "ACT-OPERATOR-1 drafts as read in round 2: apply.sh sha256 7e9398ad91ca8fe091b23784ae4eacfcccf01623b8a8e5798bfa88389d374fe9 (freeze_gate.py 00e8ce13249e, merge_queue.py 1f3b1d44f507, test_act_operator_1.py 5ced364cdf06, crontab.line 77dcf4661777; rehearsals pre 64ec40532444 and post f19c36a00466, failures 0)",
 "kpis": [
  {"kpi": "F1 apply.sh undo with queue/'s record", "verdict": "pass", "findings": []},
  {"kpi": "F2 rehearsal ends failures: 0", "verdict": "pass", "findings": []},
  {"kpi": "F3 freeze gate: old zeros, pack-refs, gc, update-ref without an old value", "verdict": "pass", "findings": [
    {"id": "R2-F1", "scope": "in", "ordinary_work": "no", "consequence": "other"}]},
  {"kpi": "F4 freeze gate on a detached main tree", "verdict": "pass", "findings": []},
  {"kpi": "F5 the merge queue waits on the freeze", "verdict": "pass", "findings": [
    {"id": "R2-F2", "scope": "in", "ordinary_work": "no", "consequence": "other"}]},
  {"kpi": "F8 apply.sh checks sources and every part before writing; partial install removable", "verdict": "pass", "findings": []},
  {"kpi": "F9 crontab hours", "verdict": "pass", "findings": []}
 ]}
```
