# W2-67 round 1, batch 2 (td-2): the planted faults

Throwaway, never in the tracked tree. `src/` is never written; nothing is copied but these single named files
(written in the session scratch folder, copied here with `cp <file> <folder>/`).

- `w2_67c_plant.py`: pytest plugin (`-p w2_67c_plant`, this folder on `PYTHONPATH`). Wraps
  `w1_07_support.write_launcher` in the test process: each launcher a case writes first imports `w2_67c_child` and
  calls `apply(<W2_67_PLANT, comma-separated>)` in that `gov` process. For a fault of `gov.check.schema`'s text it
  also redirects W2-02's `sh -c "python3 -m gov.check.schema"` to `w2_67c_run_patched.py <fault>`.
- `w2_67c_child.py`: the faults (each named and described in its comments). In the `gov` process: function
  wrappers of `gov.check.runner` (PF20, P67C-2, the MUTE-* faults), one exact text change of one function
  recompiled in memory (PF21, PF22, PF23). For a declared check: the command the runner runs replaced, in that run,
  by `true` (MUTE-schema/-graph/-authority/-mutation/-claims, PF3) or by `python3 w2_67c_run_patched.py <fault>`
  (PF7, PF8, PF17, PF24, P67C-1, P67C-3, P67C-4).
- `w2_67c_run_patched.py`: runs a check's module as `python3 -m` would, with one exact text change of its source
  made in memory (it refuses to run when the old text is not there exactly once).

A command (from the worktree root):

    W2_67_PLANT=<fault> PYTHONPATH=/home/usain/gov-os-worktrees/W2-67/src:/home/usain/gov-os-worktrees/W2-67/.gov-runtime/scratch/td-2/plant \
      python3 -m pytest -p no:cacheprovider -p w2_67c_plant -q -n 4 --tb=no -rf \
      --junitxml=/home/usain/gov-os-worktrees/W2-67/.gov-runtime/scratch/td-2/plant/<group>-<set>-<fault>.xml <node ids>

The runs and their XML (the case lists and results are in `tests/acceptance/W1-26/README-W2-67.md` and
`tests/acceptance/W2-02/README-W2-67.md`):

| XML | Cases | Result |
|---|---|---|
| `g0-PF21.xml` | `test_w1_26_green_base.py` (3) | 2 failed (both base cases), 1 passed |
| `g1-planted-defects-{PF20,PF7,PF17,PF8,MUTE-authority,MUTE-mutation,MUTE-claims}.xml` | the 10 revised planted-defect cases | 10, 1, 2, 3, 1, 2, 2 failed |
| `g1-overall-red-{PF20,MUTE-authority,MUTE-claims,MUTE-policy,MUTE-skill-version}.xml` | the other 14 overall-red cases | 14, 5, 6, 1, 2 failed |
| `g2-derived-{PF20,PF7,PF17,PF8,P67C-3,P67C-4}.xml` | the 7 derived-scope cases | 7, 3, 5, 2, 1, 1 failed |
| `g3-rest-{PF20,PF21,PF22,PF23,PF24,PF8,P67C-2,MUTE-authority,MUTE-readiness,MUTE-openspec}.xml` | the 5 always-true, the duplicate pair, the warning case, the unmeasured family, W2-L379's three (12) | 12, 1, 1, 2, 1, 1, 1, 2, 3, 3 failed |
| `g4-w2-02-P67C-1.xml`, `g4-w2-02-before-P67C-1.xml`, `g4-w2-02-head.xml` | W2-02's unmeasured file (4) | 2 failed; 0 failed (the case as it was); 0 failed |
| `final-head-w1-26.xml` | every touched W1-26 file, W1-28's copy check, W2-02's unmeasured file | 112 passed |
