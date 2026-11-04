---
id: CP-DAEO-sdxk-0777
type: checkpoint
status: ACTIVE
state_class: NARRATIVE
title: DAEO-sdxk at stop
task: DAEO-sdxk
task_status: open
trigger: stop
next_action: 'D-4: parts A (w2/D4-cut-a, green) and B (w2/D4-cut-b, 83 commits) done;
  an engineer makes the CTO''s config changes on D4-cut-b (T-6, T-11, Q-8/Q-10, win_toast,
  T-7 helper_exceptions, T-10 lifted in select_tests.py + nothing_to_run, nightly_only
  emptied), then merges D4-cut-a into it and re-counts; next one review of the regenerated
  KPI maps, then merge into w2/integrate and re-check selection. D-4b: W2-13 re-pin
  designer on w2/W2-13-tests (13 cases; P-W2-13-R3 (a) keep DP-3, (c) to W2-32 S5);
  then W2-13 reviewer delta, merge, measure 1 (drafts/d4b/measure.sh m1 <head> --pinned-too)
  and the W2-15a modes harness by research. DEC-1061, DEC-1062 recorded.'
created: '2026-11-03T19:22:06Z'
inputs:
- id: DAEO-sdxk
  version: b8571d9d
  hash: sha256:e3bc3c636cac0a66e0ff7f46e3c4e9115735ce5f4a4c49f9393635fafb4f9b3e
- id: governance/project/orchestration/packages/LIFT-1/D4-LIST.md
  version: 2978152a
  hash: sha256:f0ba962a5582a1c465b5143166faf40a3caf4afa3dfe2d16ba9ff07eebb31c43
- id: .gov-runtime/scratch/orchestrator/drafts/d4b/measure.sh
  version: untracked
  hash: sha256:b65e0112940d8946b3a0ece874eed04b01240484a25955f5a3e57372abcf3eba
head_commit: 7524fa042713b8b5d4de8daf7ca7b2fb23b20c52
---

# CP-DAEO-sdxk-0777 — DAEO-sdxk at stop

## Next action

D-4: parts A (w2/D4-cut-a, green) and B (w2/D4-cut-b, 83 commits) done; an engineer makes the CTO's config changes on D4-cut-b (T-6, T-11, Q-8/Q-10, win_toast, T-7 helper_exceptions, T-10 lifted in select_tests.py + nothing_to_run, nightly_only emptied), then merges D4-cut-a into it and re-counts; next one review of the regenerated KPI maps, then merge into w2/integrate and re-check selection. D-4b: W2-13 re-pin designer on w2/W2-13-tests (13 cases; P-W2-13-R3 (a) keep DP-3, (c) to W2-32 S5); then W2-13 reviewer delta, merge, measure 1 (drafts/d4b/measure.sh m1 <head> --pinned-too) and the W2-15a modes harness by research. DEC-1061, DEC-1062 recorded.
