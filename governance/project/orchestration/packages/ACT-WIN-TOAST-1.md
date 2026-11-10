# ACT-WIN-TOAST-1: tools/win_toast.ps1 out of the test map's record_only list (DEC-1112 (3), D-10's red-fix list)

- **For:** the owner's operator. It is a test-map change; the test map is a control path (`src/gov/close/select.py`
  reads it), so it is applied as an ACT, as ACT-SELECT-FIXES-1 was.
- **By:** the CTO's D-10 helper, 2026-11-10, for orchestrator DAEO-sdxk. Built and rehearsed in a scratch clone.
  Nothing live changes until the operator runs §3.
- **Under:** DEC-1112 (3). The CTO's delegated item 4 of 2026-11-10: "tools/win_toast.ps1: not record-only
  (deadman.py runs it)". The finding is W2-66's D-10 review F2 (`reviews/D10-W2-66-review.md`).
- **Class:** (b) by the operator agent's rule table (any test-map removal), though by effect it only tightens (DEC-1104 (2)'s
  test for (a)): a change to `win_toast.ps1` is no longer record-only, and as an unplaced path it runs the full
  selection.
- **Route: by hand (review round 2's F1, route (i)).** The owner tells their operator to run §3, and that instruction
  is the owner's yes (DEC-1104 (4)), as ACT-CLAUDE-COPIES-2 offered. It is not bundled for the operator agent's queue:
  no manifest, and the scripts run in the main tree they sit in (round 2's F2 concerns the agent's frozen-copy path only).

## 1. What changes (one file)
`governance/project/test-map.yaml` (`drafts/win-toast/test-map.patch`):
- the `record_only` line `"governance/project/orchestration/tools/win_toast.ps1"` becomes a comment that names the
  decision and the reason, and keeps the old line;
- nothing else changes;
- the map has 16 `record_only` entries (was 17).

Map sha256 before `42e22dd70a05546e99fd7f2503c109a417ee6d1c11ebfddc42dfee5ff8f1a665` (as of `8038e0ee6`, the last
commit that changed it); after `45e785d12b14ff0f7e4c52507f4c529f2fff3e488c15864ec20bc53f17c2d348`.

## 2. Rehearsal (`drafts/win-toast/rehearsal.log`)
In a scratch clone of `w2/integrate` (`c906619646da`) with a planted HOME, only the root substituted:
- `check`: "state before / check: ready to apply";
- `apply`: "state applied", with `test-map.yaml` 3 lines added and 1 removed;
- `check`: "already applied";
- `win_toast.ps1` is no longer listed record-only;
- W2-66's live test-map suite with both opt-ins: 89 passed;
- `undo`: "state before", with an empty diff.

## 3. The operator's steps
In the main tree, about one minute:
```
cd /home/usain/Dynamic-Agentic-Engineering-OS
D=.gov-runtime/scratch/orchestrator/drafts/win-toast
bash $D/apply.sh check     # "state before", then "check: ready to apply" (exit 0)
bash $D/apply.sh apply     # backup with its sha256, the map replaced, "state applied"
git commit -m "ACT-WIN-TOAST-1: tools/win_toast.ps1 out of the test map's record_only list (DEC-1112 (3); deadman.py runs it)" --trailer "Task: decision-record" --trailer "Role: owner" -- governance/project/test-map.yaml
```
- **Check:** `bash $D/apply.sh check` prints "state applied".
- **Undo:** `bash $D/apply.sh undo` (byte for byte from the backup), or `git revert` of the operator's commit.

## 4. Review
`reviews/ACT-WIN-TOAST-1-review.md`, two rounds, READY by verdict.py.
- **Round 1:** READY. F1 (the class) is answered above.
- **F2 and F3, fixed after round 1 and re-rehearsed** (`rehearsal.log`):
  - `apply` now refuses a candidate that is not the reviewed one, and restores the backup if the result is not the
    applied state;
  - `undo` now refuses unless the map is as this ACT left it, so a later change is not lost.
- **Round 2:** READY. F2 and F3 are closed. Its F1 (route) is answered above: by hand. Its F2 (the tree rule) applies only to
  the agent's route.
