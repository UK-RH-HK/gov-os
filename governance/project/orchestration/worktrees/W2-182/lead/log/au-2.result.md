task: DAEO-5y8d (W2-182), the narrow independent check (run 4): the revert f299a5eb6 and the README change (0564b50a8, b826e2007, merged by 5110578c8), at head 5110578c830aeea23c1bfdfbd2fdfd5594764e0b
status: PASS
work_completed: Step 0 passed. Point 1: the template is back to how it was before E's line, the ticket's own change touches only its allowed paths, and the four tests E's line had turned red pass on a copy of HEAD. Point 2: the map names exactly the ticket's current lines, nothing was lowered, the skip plant goes red and the unplanted run is green, the redirect behaves, and the README's words agree with the ticket and the map.
files_changed: none
evidence: (1) `git diff w2/integrate...HEAD -- template/` gives 0 lines. `git diff f0cb5284d^ HEAD -- template/.rulesync/hooks.jsonc` gives 0 lines. The whole `git diff f0cb5284d^ HEAD -- template/` is not empty, but every file in it is one of the 8 spec-writing skill files that came in from `w2/integrate` (W2-98, 380860ef1), and that diff is byte-identical to `git diff f0cb5284d^ 95a55bfca -- template/` (cmp: IDENTICAL). f299a5eb6 removes exactly the 6 lines f0cb5284d added. The ticket's own change (`--stat`) is 14 files, all in `allowed_paths`, with no `template/` and no `src/gov/**`. (2) The README's table rows are Success 1 (B) to Success 5 (F) and Failure 1, 8 node ids, and every one is collected. This agrees with `gov accept` on 5110578c8 (success-1 to success-5 and failure-1, 8 passed, 0 failed, 0 unmapped). The rows for B, C, R, D and F are unchanged from run 3 except one label: "Success 6 (F)" became "Success 5 (F)". The revert touches only `template/` and the README change touches only `tests/acceptance/W2-182/`, so no case file of S1 to S5 changed. That is why S1 to S5 keep run 3's pass without being re-judged.
tests: 4 formerly-red tests: 4 passed. W2-182 folder alone: 8 passed. Failure 1 with a skip planted on W2-23 S6: 1 failed, 7 passed. Failure 1 with the W2-23 S6 row deleted from the README: 1 failed (6 >= 7). Collect-only: 8 alone, 53 = 52 + 1 mixed. W2-23 S6 alone: red, as the README says (base red).
discoveries: (a) The redirect also fires when you run one node of this folder: running Failure 1's node alone runs all 8 mapped cases. This is documented in `conftest.py` as "every argument is this folder (or a node in it)" and is harmless. (b) `heavy_slot.sh` could not append to `.gov-runtime/scratch/orchestrator/log/heavy-slot-waits.jsonl` from the sandbox ("Read-only file system"). It still ran every case. (c) Step 0 (b) wrote one blob, 1ae28402a, into the shared `.git`, as that step requires.
risks: none in this check's scope. W2-23 S6 stays a base red until W2-185 lands.
lessons: Copying a tree with `cp -a` brings stale `__pycache__` folders along, so tracebacks name the wrong path. Clear them before a planted run. The verdict did not change once they were cleared.
proposed_decisions: none
unresolved: none
recommended_next_action: Land W2-182 on this PASS. W2-185 (DAEO-qyt2) carries line E, and W2-23 S6 goes green there.

**Sandbox check (Step 0, `launch_worker.sh`, GOV_TICKET=DAEO-5y8d):** (a) `python3 -c "open('/home/usain/gov-os-worktrees/.sandbox-trial-W2-182','w').write('x')"` failed with `OSError: [Errno 30] Read-only file system` and no file was made. (b) `git hash-object -w --stdin` printed 1ae28402a109c3397a44b19239a00adfa9472eb0 with exit 0, and `git update-index --refresh` exited 0. `ps` check: `ps -eo pid,args | grep -iE "[o]llama|[l]lama-server"` showed nothing (exit 1), both before and after.

## Point 1: the revert f299a5eb6 — PASS
- `git diff w2/integrate...HEAD -- template/ | wc -l` → 0 (merge base 95a55bfca).
- `git diff f0cb5284d^ HEAD -- template/.rulesync/hooks.jsonc | wc -l` → 0.
- `git diff f0cb5284d^ HEAD -- template/` differs from before E's line only by the 8 spec-writing skill files from integrate, and it is identical to `git diff f0cb5284d^ 95a55bfca -- template/`.
- `git diff w2/integrate...HEAD --stat` → 14 files:
  - `docs/probes/DAEO-5y8d/PR-DAEO-5y8d.md`
  - the 7 revised test files (W1-18, W1-32, W2-121, W2-123, W2-128, W2-136, W2-23)
  - the READMEs of W2-128 and W2-136
  - 4 files in `tests/acceptance/W2-182/`
  
  All are in `allowed_paths`.
- I ran the four cases on a copy of HEAD through `heavy_slot.sh`:
  - `tests/unit/gitenv/test_program_env.py::test_this_repository_s_two_hooks_sources_agree`
  - `tests/acceptance/W2-05/test_w2_05_hooks_source.py::test_adapter_portability_is_green_over_this_repository_s_two_hooks_sources`
  - `tests/acceptance/W1-38/test_w1_38_rulesync.py::TestHookStubs::test_hook_stubs_exist`
  - `tests/acceptance/W1-38/test_w1_38_hooks_any_folder.py::TestABashCallAfterAChangeOfDirectory::test_an_ordinary_allowed_call_is_not_blocked`
  
  Result: `4 passed in 5.94s`.

## Point 2: the README change — PASS
- **(a) The map:** `pytest tests/acceptance/W2-182 --collect-only -q` → `8 tests collected`. That is B (1), C (2), R (1), D (1), F (2: role-lead and role-cto) and Failure 1 (1), every node existing and collected. There is no E row. W2-23 S6 sits only in the "Revised, not run here" table and in the "Known reds" bullet, and the bullet is not a table row, so it is not collected.
- **(b) Nothing lowered:** The failure-line case now scans the mapped cases plus the unrun ones. Listing what it scans gives 7 functions, the 7th being W2-23 S6. The assertion is unchanged (`len(functions) >= 7`, then `assert not problems`), and so are `LOWERING`, `BASELINE` and the module-level `pytestmark` scan.
  - Unplanted: `8 passed`.
  - Planted (`@pytest.mark.skip(reason='plant')` above the W2-23 S6 function in a copy, `__pycache__` cleared): `1 failed, 7 passed`, with `AssertionError: tests/acceptance/W2-23/test_w2_23_space.py::test_s6_every_kernel_hook_exits_alike_with_a_space_in_the_project_dir carries ['skip']` at `test_w2_182_no_lowering.py:72`.
  - Extra plant (the W2-23 S6 row deleted from the README): `assert 6 >= 7`, so the row cannot drop out unseen.
- **(c) The redirect:** The folder alone collects 8. `pytest tests/acceptance/W1-32 tests/acceptance/W2-182 --collect-only -q` collects `53/82 (29 deselected)`, and W1-32 alone collects `52/81 (29 deselected)`. So the mixed run is W1-32's own cases plus this folder's one.
- **(d) The words:**
  - "B is Success 1 ... F is Success 5" and "(8 cases)" match the ticket's lines B, C, R, D, F and Failure 1, and the map.
  - "Known reds" names W2-23 S6 a base red owned by W2-185 (DEC-1167 (4)), as the ticket's last note says. I ran it on HEAD and it is red (`do not reach the seven kernel hooks: ['context_watch.py']`).
  - "Nothing else of the map is known red" agrees with the 8 passing.

## Findings
None. What I probed and found sound: the revert is exact; integrate's merges add nothing of the ticket's own to `template/`; the ticket stays inside its paths; the four former reds pass; the map is exact; Failure 1's scan includes W2-23 S6 and goes red on a planted skip and on a dropped row; the redirect fires only when the folder runs alone; and the README agrees with the ticket. (Discovery (a), the single-node redirect, is documented behaviour and not a defect, so it is not a finding.)

```verdict
{"kpis": [{"kpi": "S1", "verdict": "pass", "findings": []}, {"kpi": "S2", "verdict": "pass", "findings": []}, {"kpi": "S3", "verdict": "pass", "findings": []}, {"kpi": "S4", "verdict": "pass", "findings": []}, {"kpi": "S5", "verdict": "pass", "findings": []}, {"kpi": "F1", "verdict": "pass", "findings": []}]}
```

guard_refusals: none. One sandbox write was refused inside `heavy_slot.sh`'s own logging (`heavy-slot-waits.jsonl: Read-only file system`); it did not stop any run. The tree is clean at the end (`git status --porcelain` is empty, HEAD is still 5110578c8).