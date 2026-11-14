# W2-94 fix flow — acceptance cases for the launch script's one-question fix flow, the independent test designer's brief (DAEO-g87r)

You are a fresh independent test designer (class C2) under **W2-94** (`DAEO-g87r`; the ticket, read-only:
`/home/usain/Dynamic-Agentic-Engineering-OS/.tickets/DAEO-g87r.md`; read its "Reopened 2026-11-14" paragraph and KPI
lines S6 to S12 and F4 to F6). The owner decided **DEC-1180 (2)** (P-Q02-RUN-1 (a), "run today, as soon as it is built
and reviewed"): the walled launch script `governance/project/orchestration/tools/indep_launch.py` gains a one-question
fix flow on the writer's round 2, so the owner's approved writer variant for hidden question q02 (DEC-1178 (5)) runs
byte for byte unchanged. You write the acceptance cases **from the KPI lines and the interface below, as described
behaviour (DEC-136)**. An engineer changes the script in parallel; you do not read its branch or its work.

**Speed matters:** the owner's operator runs q02 today once this lands. Write a tight suite that checks each line once,
well; no case beyond S6 to S12 and F4 to F6.

## Where you work
- Worktree `/home/usain/gov-os-worktrees/W2-94-fix-tests`, branch `w2/W2-94-fix-tests` (at `340cd0efb`). Write only
  **new** files under `tests/acceptance/W2-94/`: `test_w2_94_fix_flow.py`, and a support file
  (`w2_94_fix_support.py`) if you need one, plus a byte copy of the approved variant as a fixture
  (`tests/acceptance/W2-94/fixtures/EXAMIN-writer-q02-fix.md`; copy it from
  `/home/usain/gov-os-worktrees/W2-94-fix-tests/.gov-runtime/scratch/variant/EXAMIN-writer-q02-fix.md` and have a case
  assert its sha256 is `0703aebf69522cbb853d77f4e134e03843f1d961307b46c77ceaa575fa469173`). Leave every existing W2-94
  test file unchanged, except `tests/acceptance/W2-94/README.md`, where you add one map row per KPI id you cover
  (S6, S7, S8, S9, S10, S11, S12, F4, F5, F6) in the existing table's form: a row's KPI cell names only this ticket's
  line, its tests cell names `<file>::<test>` ids, and the red reason against the unchanged script.
- Read first: the script's docstring (top of `indep_launch.py`) and only as much of its code as you need to know its
  command-line interface, exit codes and file layout (`check_args`, `plan_inputs`, `build_and_run`'s order, `deliver`'s
  writer branch, `pack`, `choose_run`); then the existing **fake-session test seam**: `tests/unit/orchestration/test_w2_149_indep_launch.py`
  (`World`: a planted sets root, HOME, repository with the walls' template and an APPROVED list, and a stub `claude`
  driven by a JSON config; `w.launch(...)`, `w.args(...)`, `w.plant_set`, `nothing_built`, `writer_out`), and how
  `tests/unit/orchestration/test_w2_173_indep_launch.py` and `test_w2_178_indep_launch.py` reuse it (import from
  `test_w2_149_indep_launch`; you may import it the same way, putting `tests/unit/orchestration` on `sys.path` in your
  support file). Do not change those unit files.
- A delivered round-1 run for the sample: plant it as the interface's item 3 says (a `counts.json` under
  `<runs>/indep/writer/<rid>/` and the archive `<walls>/writer/<rid>.tar` holding `<rid>/input/selection.json`), either
  by writing those planted files directly or by running a planted round-1 writer launch through the stub; plant two
  delivered round-1 runs with different samples and one non-delivered later one, so "the latest delivered" is tested.
