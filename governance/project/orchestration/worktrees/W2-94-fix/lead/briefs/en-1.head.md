# W2-94 fix flow — the launch script's one-question fix flow, the engineer's brief (DAEO-g87r)

You are a fresh engineer (class C2) under **W2-94** (`DAEO-g87r`; the ticket, read-only:
`/home/usain/Dynamic-Agentic-Engineering-OS/.tickets/DAEO-g87r.md`; read its "Reopened 2026-11-14" paragraph and KPI
lines S6 to S12 and F4 to F6). The owner decided **DEC-1180 (2)** (P-Q02-RUN-1 (a), "run today, as soon as it is built
and reviewed"): the walled launch script gains a one-question fix flow on the writer's round 2, so that the owner's
approved writer variant for hidden question q02 (DEC-1178 (5)) runs byte for byte unchanged. Its text is at
`/home/usain/gov-os-worktrees/W2-94-fix/.gov-runtime/scratch/variant/EXAMIN-writer-q02-fix.md` (sha256
`0703aebf69522cbb853d77f4e134e03843f1d961307b46c77ceaa575fa469173`; read its front matter and sections 2, 3 and 5: they
name the inputs and the output the flow gives it). Never change it.

**Speed matters; keep the change small:** one flag pair on the existing writer round 2, read and checked before
anything is written, its own staging and delivery branch; no refactor, no change to any other flow.

## Where you work
- Worktree `/home/usain/gov-os-worktrees/W2-94-fix`, branch `w2/W2-94-fix`. Write only
  `governance/project/orchestration/tools/indep_launch.py` and a new `tests/unit/orchestration/test_w2_94_fix_flow_unit.py`.
  Never change `governance/project/indep-walls/**`, `governance/project/indep-briefs/**` (the owner's class O),
  `governance/project/orchestration/tools/indep-schemas/**`, or any other test file. Do not edit `tests/acceptance/W2-94/**`
  (the independent test designer's; its suite is written in parallel and the lead merges it into your branch when
  ready; then you make it pass).
- Read: the script's docstring and `check_args`, `resolve_brief`, `plan_inputs`, `build_and_run`, `check_result`,
  `copy_numbers`, `deliver` (the writer branch), `pack`, `choose_run`, `finish`. The fake-session test seam for your
  unit tests: `tests/unit/orchestration/test_w2_149_indep_launch.py` (`World`, `w.launch`, `w.args`, `w.plant_set`,
  `nothing_built`, `writer_out`), reused by `test_w2_173_indep_launch.py` and `test_w2_178_indep_launch.py` (import from
  `test_w2_149_indep_launch`).
